# Add this to your rag_service.py to fix the container issues

import chromadb
import asyncio
import json
import logging
from typing import List, Dict, Any
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyRAGService:
    def __init__(self):
        self.use_chromadb = False
        self.use_openai = False
        self.mock_data = []
        
        try:
            # Try to initialize ChromaDB
            self.client = chromadb.PersistentClient(path="./chroma_db")
            self.collection_name = "property_intelligence"
            self.use_chromadb = True
            logger.info("✅ ChromaDB initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ ChromaDB initialization failed: {e}")
            logger.info("🔄 Falling back to in-memory storage")
        
        # Check for OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                from langchain_openai import OpenAIEmbeddings, ChatOpenAI
                from langchain_chroma import Chroma
                from langchain.chains import RetrievalQA
                
                self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.7,
                    openai_api_key=openai_api_key
                )
                self.use_openai = True
                logger.info("✅ OpenAI services initialized")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI initialization failed: {e}")
        
        if not self.use_openai:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Local embeddings model loaded")
            except Exception as e:
                logger.warning(f"⚠️ Local embeddings failed: {e}")
        
        # Initialize with mock data for immediate functionality
        self.initialize_mock_data()
        
        if self.use_chromadb:
            try:
                self.initialize_vectorstore()
            except Exception as e:
                logger.error(f"Vectorstore initialization failed: {e}")
    
    def initialize_mock_data(self):
        """Initialize with realistic mock property data"""
        self.mock_data = [
            {
                "content": "Luxury 3BR/2BA condo in Manhattan with city views, doorman, gym, and rooftop terrace. Prime location near Central Park.",
                "metadata": {
                    "address": "123 Park Avenue, Manhattan, NY",
                    "price": 1250000,
                    "bedrooms": 3,
                    "bathrooms": 2,
                    "sqft": 1800,
                    "type": "condo"
                },
                "similarity_score": 0.95
            },
            {
                "content": "Modern 2BR/2BA apartment in Upper East Side with updated kitchen, hardwood floors, and excellent school district.",
                "metadata": {
                    "address": "456 Madison Avenue, Manhattan, NY", 
                    "price": 950000,
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "sqft": 1200,
                    "type": "apartment"
                },
                "similarity_score": 0.88
            },
            {
                "content": "Penthouse suite with panoramic Manhattan skyline views, private elevator, chef's kitchen, and 1000 sqft terrace.",
                "metadata": {
                    "address": "789 Fifth Avenue, Manhattan, NY",
                    "price": 2800000,
                    "bedrooms": 4,
                    "bathrooms": 3,
                    "sqft": 2500,
                    "type": "penthouse"
                },
                "similarity_score": 0.92
            },
            {
                "content": "Historic brownstone converted to luxury condos, featuring original architectural details and modern amenities.",
                "metadata": {
                    "address": "321 West 78th Street, Manhattan, NY",
                    "price": 1650000,
                    "bedrooms": 3,
                    "bathrooms": 2.5,
                    "sqft": 2000,
                    "type": "townhouse"
                },
                "similarity_score": 0.85
            },
            {
                "content": "Studio apartment in trendy SoHo district with high ceilings, exposed brick, and close to shopping and dining.",
                "metadata": {
                    "address": "555 Broadway, Manhattan, NY",
                    "price": 750000,
                    "bedrooms": 1,
                    "bathrooms": 1,
                    "sqft": 800,
                    "type": "studio"
                },
                "similarity_score": 0.78
            }
        ]
        logger.info("✅ Mock property data initialized")
    
    def initialize_vectorstore(self):
        """Initialize the vector store with sample property data"""
        if not self.use_chromadb or not self.use_openai:
            logger.info("Skipping vectorstore initialization - dependencies not available")
            return
            
        try:
            from langchain.schema import Document
            from langchain_chroma import Chroma
            
            # Try to load existing collection
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory="./chroma_db"
            )
            logger.info("✅ Vector store loaded successfully")
        except Exception as e:
            logger.info(f"Creating new vector store: {e}")
            self.seed_initial_data()
    
    def seed_initial_data(self):
        """Seed the vector database with initial property market data"""
        if not self.use_openai:
            return
            
        try:
            from langchain.schema import Document
            from langchain_chroma import Chroma
            
            sample_data = [
                {
                    "content": "New York residential market shows strong growth with average home prices increasing 8.2% year-over-year. Manhattan luxury condos leading the surge with median price of $1.2M.",
                    "source": "NYC Market Report 2024",
                    "type": "market_analysis"
                },
                {
                    "content": "School district ratings significantly impact property values. Properties in top-rated school districts command 15-20% premium over similar homes in average districts.",
                    "source": "Education Impact Study",
                    "type": "market_factor"
                },
                {
                    "content": "Transportation accessibility is crucial for property valuation. Properties within 0.5 miles of major transit hubs show 25% higher appreciation rates.",
                    "source": "Transit Accessibility Report",
                    "type": "location_factor"
                }
            ]
            
            documents = []
            for item in sample_data:
                doc = Document(
                    page_content=item["content"],
                    metadata={
                        "source": item["source"],
                        "type": item["type"],
                        "timestamp": datetime.now().isoformat()
                    }
                )
                documents.append(doc)
            
            # Create vector store from documents
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                persist_directory="./chroma_db"
            )
            logger.info("✅ Vector store seeded with initial data")
        except Exception as e:
            logger.error(f"Failed to seed vector store: {e}")
    
    async def search_similar_properties(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar properties using vector similarity or mock data"""
        try:
            if self.use_chromadb and self.use_openai and hasattr(self, 'vectorstore'):
                # Use real vector search
                results = self.vectorstore.similarity_search_with_score(query, k=k)
                
                formatted_results = []
                for doc, score in results:
                    formatted_results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity_score": float(score)
                    })
                
                return formatted_results
            else:
                # Use mock data with query-based filtering
                logger.info("Using mock property search")
                
                # Filter and rank mock data based on query
                query_lower = query.lower()
                scored_results = []
                
                for prop in self.mock_data:
                    score = 0.5  # Base score
                    
                    # Boost score based on query terms
                    if 'luxury' in query_lower and 'luxury' in prop['content'].lower():
                        score += 0.3
                    if 'condo' in query_lower and 'condo' in prop['content'].lower():
                        score += 0.2
                    if 'manhattan' in query_lower and 'manhattan' in prop['content'].lower():
                        score += 0.2
                    if 'penthouse' in query_lower and 'penthouse' in prop['content'].lower():
                        score += 0.4
                    
                    scored_results.append({
                        "content": prop["content"],
                        "metadata": prop["metadata"],
                        "similarity_score": min(0.98, score)
                    })
                
                # Sort by score and return top k
                scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
                return scored_results[:k]
                
        except Exception as e:
            logger.error(f"Error in property search: {e}")
            return []
    
    async def add_property_data(self, property_data: Dict[str, Any]):
        """Add new property data to the vector database"""
        try:
            if self.use_chromadb and self.use_openai and hasattr(self, 'vectorstore'):
                from langchain.schema import Document
                
                content = f"""
                Property: {property_data.get('address', 'Unknown')}
                Value: ${property_data.get('value', 'Unknown')}
                Type: {property_data.get('type', 'Unknown')}
                Features: {property_data.get('features', 'Unknown')}
                Market Analysis: {property_data.get('market_analysis', 'Unknown')}
                """
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": "property_analysis",
                        "type": "property_data",
                        "address": property_data.get('address'),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                # Add to vector store
                self.vectorstore.add_documents([doc])
                logger.info(f"✅ Added property data for {property_data.get('address')}")
            else:
                # Add to mock data
                mock_entry = {
                    "content": f"Property at {property_data.get('address', 'Unknown')} - {property_data.get('description', 'No description')}",
                    "metadata": property_data,
                    "similarity_score": 0.90
                }
                self.mock_data.append(mock_entry)
                logger.info(f"✅ Added to mock data: {property_data.get('address')}")
                
        except Exception as e:
            logger.error(f"Error adding property data: {e}")
    
    async def generate_property_insights(self, property_address: str, context: str = "") -> Dict[str, Any]:
        """Generate AI-powered property insights using RAG"""
        try:
            # Search for relevant context
            search_query = f"property analysis market trends {property_address}"
            relevant_docs = await self.search_similar_properties(search_query, k=3)
            
            if not self.use_openai:
                # Fallback analysis without OpenAI
                return {
                    "insights": f"""
                    Property Analysis for {property_address}:
                    
                    Based on available market data:
                    • Strong potential in this market segment
                    • Consider location factors like schools and transportation
                    • Market conditions are generally favorable
                    • Property type and amenities are key value drivers
                    
                    Relevant comparable properties found: {len(relevant_docs)}
                    
                    Note: Enhanced AI analysis available with OpenAI API key.
                    """,
                    "sources": [doc.get("metadata", {}) for doc in relevant_docs],
                    "relevant_properties": relevant_docs,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "analysis_type": "basic"
                }
            
            # If OpenAI is available, use full RAG analysis
            from langchain.chains import RetrievalQA
            
            # Create RAG chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            # Generate insights
            query = f"""
            Analyze the property at {property_address}. Consider:
            1. Market trends and comparable properties
            2. Location factors (schools, transportation, amenities)
            3. Investment potential and risk factors
            4. Current market conditions
            
            Additional context: {context}
            
            Provide a comprehensive analysis with specific insights and recommendations.
            """
            
            result = qa_chain({"query": query})
            
            return {
                "insights": result["result"],
                "sources": [doc.metadata for doc in result["source_documents"]],
                "relevant_properties": relevant_docs,
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_type": "comprehensive"
            }
            
        except Exception as e:
            logger.error(f"Error generating property insights: {e}")
            return {
                "insights": "Unable to generate detailed insights at this time. Basic analysis suggests considering location factors, market trends, and comparable properties.",
                "sources": [],
                "relevant_properties": [],
                "error": str(e)
            }
    
    async def get_market_trends(self, location: str = "") -> Dict[str, Any]:
        """Get market trends for a specific location"""
        try:
            search_query = f"market trends analysis {location}"
            results = await self.search_similar_properties(search_query, k=5)
            
            return {
                "location": location,
                "trends": results,
                "summary": "Market analysis based on available data and comparable properties",
                "timestamp": datetime.now().isoformat(),
                "data_source": "Vector Database" if self.use_chromadb else "Mock Data"
            }
            
        except Exception as e:
            logger.error(f"Error getting market trends: {e}")
            return {"trends": [], "error": str(e)}

# Global RAG service instance
rag_service = PropertyRAGService()
