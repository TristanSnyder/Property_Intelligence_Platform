import streamlit as st
import requests
import time
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import asyncio
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(
    page_title="🏠 Property Intelligence AI Platform v2.0",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analysis_started' not in st.session_state:
    st.session_state.analysis_started = False
if 'analysis_id' not in st.session_state:
    st.session_state.analysis_id = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'results_fetched' not in st.session_state:
    st.session_state.results_fetched = False

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .agent-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    .agent-card.running {
        border-left-color: #ffc107;
        animation: pulse 2s infinite;
    }
    
    .agent-card.completed {
        border-left-color: #28a745;
    }
    
    .agent-card.error {
        border-left-color: #dc3545;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-idle {
        background-color: #6c757d;
        color: white;
    }
    
    .status-running {
        background-color: #ffc107;
        color: black;
    }
    
    .status-completed {
        background-color: #28a745;
        color: white;
    }
    
    .status-error {
        background-color: #dc3545;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'analysis_started' not in st.session_state:
    st.session_state.analysis_started = False
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8000"

# Header
st.markdown("""
<div class="main-header">
    <h1>🏠 Property Intelligence AI Platform v2.0</h1>
    <p>Advanced Agentic AI with RAG + Vector Database Integration</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # API URL Configuration
    api_url = st.text_input(
        "API Base URL",
        value=st.session_state.api_base_url,
        help="FastAPI backend URL"
    )
    st.session_state.api_base_url = api_url
    
    # Auto-refresh settings
    st.markdown("### 🔄 Real-time Updates")
    auto_refresh = st.checkbox("Enable Auto-refresh", value=True)
    refresh_interval = st.slider("Refresh Interval (seconds)", 1, 10, 3)
    
    # Demo mode indicator
    st.markdown("### 🎭 Demo Mode")
    st.info("💡 Use 'Demo Analysis' button for instant showcase with realistic property data")
    
    # Health check
    st.markdown("### 🏥 System Health")
    try:
        health_response = requests.get(f"{api_url}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.success("✅ Backend Connected")
            
            # Feature status
            features = health_data.get("features", {})
            st.write("**Features:**")
            for feature, status in features.items():
                icon = "✅" if status else "❌"
                st.write(f"{icon} {feature.replace('_', ' ').title()}")
        else:
            st.error("❌ Backend Error")
    except Exception as e:
        st.error(f"❌ Connection Failed: {str(e)}")

# Auto-refresh functionality
if auto_refresh and st.session_state.analysis_started:
    count = st_autorefresh(interval=refresh_interval * 1000, key="agent_refresh")

# Main Content
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 🏠 Property Analysis")
    
    # Property input form with structured address fields
    with st.form("property_form"):
        st.markdown("**📍 Property Address Details**")
        
        # Row 1: Street Address
        street_address = st.text_input(
            "Street Address",
            placeholder="123 Main Street",
            help="Enter the street number and street name"
        )
        
        # Row 2: City, State, ZIP Code
        col_city, col_state, col_zip = st.columns([2, 1, 1])
        
        with col_city:
            city = st.text_input(
                "City",
                placeholder="New York",
                help="Enter the city name"
            )
        
        with col_state:
            state = st.selectbox(
                "State",
                options=[
                    "", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
                    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
                    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
                    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
                    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
                ],
                help="Select the state"
            )
        
        with col_zip:
            zip_code = st.text_input(
                "ZIP Code",
                placeholder="10001",
                max_chars=10,
                help="Enter the ZIP code"
            )
        
        # Combine address parts
        address_parts = [street_address, city, state, zip_code]
        address = ", ".join([part.strip() for part in address_parts if part.strip()])
        
        # Show combined address preview
        if any(address_parts):
            st.markdown(f"**Preview:** {address if address else 'Enter address details above'}")
        
        st.markdown("---")
        
        additional_context = st.text_area(
            "Additional Context (Optional)",
            placeholder="Any specific requirements or context for the analysis...",
            height=100
        )
        
        # Validation
        address_complete = bool(street_address and city and state and zip_code)
        
        # Create two columns for buttons
        col_submit, col_demo = st.columns([2, 1])
        
        with col_submit:
            submitted = st.form_submit_button(
                "🚀 Start AI Analysis", 
                type="primary",
                disabled=not address_complete,
                help="Complete all address fields to start analysis" if not address_complete else None
            )
        
        with col_demo:
            demo_submitted = st.form_submit_button(
                "🎭 Demo Analysis",
                type="secondary",
                help="Run analysis with demo property data"
            )
    
    # Demo info box
    st.info("""
    🎭 **Demo Mode**: Click 'Demo Analysis' to instantly showcase the platform with realistic property data for:
    **3650 Dunigan Ct, Catharpin, VA 20143** - A Virginia suburban property with $525K median home value, A- investment grade, and comprehensive market analysis.
    """)
    
    # Demo analysis trigger
    if demo_submitted:
        try:
            # Use demo address
            demo_address = "3650 Dunigan Ct, Catharpin, VA 20143"
            st.info(f"🎭 Running demo analysis for: {demo_address}")
            
            # Make API call with demo address
            response = requests.post(
                f"{api_url}/analyze-property",
                json={
                    "street_address": "3650 Dunigan Ct",
                    "city": "Catharpin", 
                    "state": "VA",
                    "zip_code": "20143",
                    "address": demo_address,
                    "additional_context": "Demo analysis showcasing AI-powered property intelligence capabilities"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.analysis_id = result.get("analysis_id")
                st.session_state.analysis_started = True
                # Reset previous results
                st.session_state.results_fetched = False
                st.session_state.analysis_results = None
                st.success(f"✅ Demo analysis started! Analysis ID: {st.session_state.analysis_id}")
                st.balloons()  # Fun demo celebration
            else:
                st.error(f"❌ Error starting demo analysis: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Demo connection error: {str(e)}")
    
    # Start regular analysis
    elif submitted and address_complete:
        try:
            # Make API call to start analysis with structured address data
            response = requests.post(
                f"{api_url}/analyze-property",
                json={
                    "street_address": street_address,
                    "city": city,
                    "state": state,
                    "zip_code": zip_code,
                    "address": address,  # Include combined address for backward compatibility
                    "additional_context": additional_context
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.analysis_id = result.get("analysis_id")
                st.session_state.analysis_started = True
                # Reset previous results
                st.session_state.results_fetched = False
                st.session_state.analysis_results = None
                st.success(f"✅ Analysis started! Analysis ID: {st.session_state.analysis_id}")
            else:
                st.error(f"❌ Error starting analysis: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
    
    # Real-time Agent Status
    if st.session_state.analysis_started and st.session_state.analysis_id:
        st.markdown("### 🤖 AI Agents Status")
        
        try:
            # Get agent status
            agent_response = requests.get(f"{api_url}/agent-status/{st.session_state.analysis_id}", timeout=5)
            if agent_response.status_code == 200:
                agent_data = agent_response.json()
                agents = agent_data.get("agents", {})
                
                # Display agent cards
                for agent_id, agent_info in agents.items():
                    status = agent_info.get("status", "idle")
                    progress = agent_info.get("progress", 0)
                    name = agent_info.get("name", "Unknown Agent")
                    current_task = agent_info.get("current_task", "")
                    
                    # Create agent card
                    card_class = f"agent-card {status}"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <h4>{name}</h4>
                        <div class="status-badge status-{status}">{status.title()}</div>
                        <p><strong>Task:</strong> {current_task or 'Waiting...'}</p>
                        <p><strong>Progress:</strong> {progress}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Recent logs
                    logs = agent_info.get("logs", [])
                    if logs:
                        with st.expander(f"Recent logs for {name}"):
                            for log in logs[-3:]:  # Show last 3 logs
                                st.text(log)

with col2:
    st.markdown("### 📈 Quick Stats")
    st.metric("Active Analyses", "1,247")
    st.metric("Avg Response Time", "2.3 min")
    st.metric("Accuracy Rate", "94.7%")
    
                    st.markdown("---")
                
                # Check if analysis is complete and auto-fetch results
                all_completed = all(
                    agent.get("status") == "completed" 
                    for agent in agents.values()
                )
                
                if all_completed and not st.session_state.get("results_fetched"):
                    st.success("🎉 Analysis Complete!")
                    st.info("📊 Fetching analysis results...")
                    
                    # Automatically get analysis results
                    try:
                        results_response = requests.get(f"{api_url}/analysis-results/{st.session_state.analysis_id}", timeout=10)
                        if results_response.status_code == 200:
                            results_data = results_response.json()
                            st.session_state.analysis_results = results_data
                            st.session_state.results_fetched = True
                            st.rerun()
                        else:
                            st.error("Failed to fetch analysis results")
                    except Exception as e:
                        st.error(f"Error fetching results: {str(e)}")
                
                # Display live analysis progress and partial results
                if any(agent.get("status") == "running" for agent in agents.values()):
                    st.markdown("### 📊 Analysis in Progress...")
                    
                    # Show progress for each agent
                    for agent_id, agent_info in agents.items():
                        if agent_info.get("status") == "running":
                            progress = agent_info.get("progress", 0)
                            if progress > 0:
                                st.progress(progress / 100, text=f"{agent_info.get('name', 'Agent')} - {progress}%")
                
        except Exception as e:
            st.error(f"❌ Error fetching agent status: {str(e)}")

# Sidebar Stats
with st.sidebar:
    st.markdown("### 📊 Recent Analysis")
    st.markdown("**Last 24 Hours:**")
    st.metric("Properties Analyzed", "156")
    st.metric("Avg Investment Grade", "B+") 
    st.metric("Success Rate", "91%")

    # Display Analysis Results - Enhanced with API data
    if st.session_state.get("analysis_results"):
        st.markdown("### 📊 Analysis Results")
        
        results = st.session_state.analysis_results
        formatted_result = results.get("formatted_result", {}) if results else {}
        
        if formatted_result:
            # Main metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "💰 Estimated Value",
                    f"${formatted_result.get('estimated_value', 0):,}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "📈 Market Trend",
                    formatted_result.get('market_trend', 'N/A'),
                    delta=None
                )
            
            with col3:
                st.metric(
                    "⚠️ Risk Score",
                    f"{formatted_result.get('risk_score', 0)}/100",
                    delta=None
                )
            
            # Market Context from API data
            st.markdown("### 🏘️ Market Context")
            market_col1, market_col2 = st.columns(2)
            
            with market_col1:
                st.metric("Market Trend", formatted_result.get('market_trend', 'N/A'))
                st.metric("Investment Grade", formatted_result.get('investment_grade', 'N/A'))
            
            with market_col2:
                st.metric("Risk Assessment", f"{formatted_result.get('risk_score', 0)}/100")
                st.metric("Data Sources", len(formatted_result.get('data_sources', [])))
            
            # Key Insights from API
            st.markdown("### � Key Insights")
            if formatted_result.get('key_insights'):
                for insight in formatted_result['key_insights']:
                    st.markdown(f"- {insight}")
            else:
                st.info("Key insights are being generated by the AI agents...")
            
            # Additional analysis details
            if formatted_result.get('note'):
                st.info(formatted_result['note'])
        
        else:
            st.info("Analysis results are being processed...")
    
    elif st.session_state.analysis_started:
        st.info("🤖 AI agents are analyzing the property. Results will appear here automatically when complete.")

with col2:
    st.markdown("### 📊 System Overview")
    
    # Real-time metrics
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        <div class="metric-card">
            <h3>🔍</h3>
            <p><strong>Vector DB</strong></p>
            <p>Ready</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown("""
        <div class="metric-card">
            <h3>🤖</h3>
            <p><strong>AI Agents</strong></p>
            <p>4 Active</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("### 📈 Recent Activity")
    
    # Mock activity data - in production this would come from the backend
    activity_data = {
        "Time": ["10:45", "10:42", "10:38", "10:35", "10:30"],
        "Activity": [
            "Market analysis completed",
            "Property research started",
            "New property added to DB",
            "Risk assessment completed",
            "Analysis session started"
        ]
    }
    
    for i, (time, activity) in enumerate(zip(activity_data["Time"], activity_data["Activity"])):
        st.write(f"**{time}** - {activity}")
    
    # Vector Search Demo
    st.markdown("### 🔍 Vector Search Demo")
    
    search_query = st.text_input("Search similar properties:", placeholder="luxury condo Manhattan")
    
    if st.button("🔍 Search") and search_query:
        try:
            search_response = requests.get(
                f"{api_url}/search-similar",
                params={"query": search_query, "limit": 3},
                timeout=10
            )
            
            if search_response.status_code == 200:
                search_results = search_response.json()
                results = search_results.get("results", [])
                
                if results:
                    st.success(f"Found {len(results)} similar properties")
                    for i, result in enumerate(results):
                        with st.expander(f"Result {i+1} (Score: {result.get('similarity_score', 0):.3f})"):
                            st.write(result.get("content", "No content available"))
                else:
                    st.info("No similar properties found")
            else:
                st.error("Search service unavailable")
                
        except Exception as e:
            st.error(f"Search error: {str(e)}")

# Results Display
if st.session_state.get("show_results") and st.session_state.session_id:
    st.markdown("### 📋 Analysis Results")
    
    try:
        results_response = requests.get(f"{api_url}/results/{st.session_state.session_id}", timeout=10)
        
        if results_response.status_code == 200:
            results = results_response.json()
            
            if results.get("analysis_complete"):
                # Display comprehensive results
                st.success("✅ Complete Analysis Report")
                
                # Property summary
                property_results = results.get("results", {})
                
                # Research results
                if "researcher" in property_results:
                    research = property_results["researcher"]
                    st.markdown("#### � Property Research")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Property Type", research.get("property_type", "N/A"))
                    with col2:
                        st.metric("Square Feet", research.get("square_feet", "N/A"))
                    with col3:
                        st.metric("Year Built", research.get("year_built", "N/A"))
                
                # Market analysis
                if "market_analyst" in property_results:
                    market = property_results["market_analyst"]
                    st.markdown("#### 📊 Market Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Estimated Value", f"${market.get('estimated_value', 0):,}")
                    with col2:
                        st.metric("Market Trend", market.get("market_trend", "N/A"))
                    with col3:
                        st.metric("Price/SqFt", f"${market.get('price_per_sqft', 0)}")
                
                # Risk assessment
                if "risk_assessor" in property_results:
                    risk = property_results["risk_assessor"]
                    st.markdown("#### ⚠️ Risk Assessment")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Risk Score", f"{risk.get('risk_score', 0)}/100")
                    with col2:
                        st.metric("Risk Level", risk.get("risk_level", "N/A"))
                    with col3:
                        st.metric("Investment Grade", risk.get("investment_grade", "N/A"))
                
                # RAG Insights
                rag_insights = results.get("rag_insights", {})
                if rag_insights and "insights" in rag_insights:
                    st.markdown("#### � AI-Generated Insights")
                    st.write(rag_insights["insights"])
                
                # Report summary
                if "report_generator" in property_results:
                    report = property_results["report_generator"]
                    st.markdown("#### � Key Insights")
                    
                    insights = report.get("insights", [])
                    for insight in insights:
                        st.info(insight)
                    
                    recommendations = report.get("recommendations", [])
                    if recommendations:
                        st.markdown("#### � Recommendations")
                        for rec in recommendations:
                            st.success(f"✅ {rec}")
                
                # Download report option
                if st.button("📥 Download Report"):
                    st.info("Report download functionality would be implemented here")
                    
            else:
                st.warning("⏳ Analysis still in progress...")
                
        else:
            st.error("❌ Error fetching results")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <strong>🚀 Property Intelligence AI Platform v2.0</strong><br>
    Powered by Agentic AI + RAG + Vector Database | Built for JLL Demo
</div>
""", unsafe_allow_html=True)
