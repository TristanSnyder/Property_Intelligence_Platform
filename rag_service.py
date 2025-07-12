import chromadb
import asyncio
import json
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.schema import Document
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyRAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = "property_intelligence"
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.vectorstore = None
        self.initialize_vectorstore()
        
    def initialize_vectorstore(self):
        """Initialize the vector store with sample property data"""
        try:
            # Try to load existing collection
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory="./chroma_db"
            )
            logger.info("Loaded existing vector store")
        except Exception as e:
            logger.info(f"Creating new vector store: {e}")
            self.seed_initial_data()
    
    def seed_initial_data(self):
        """Seed the vector database with initial property market data"""
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
            },
            {
                "content": "Rising interest rates create both challenges and opportunities. While buyer demand softens, cash buyers gain negotiating power in competitive markets.",
                "source": "Interest Rate Impact Analysis",
                "type": "market_condition"
            },
            {
                "content": "Property risk assessment should include flood zones, earthquake probability, and climate change impacts. FEMA flood maps updated quarterly.",
                "source": "Risk Assessment Guidelines",
                "type": "risk_factor"
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
        logger.info("Seeded vector store with initial data")
    
    async def add_property_data(self, property_data: Dict[str, Any]):
        """Add new property data to the vector database"""
        try:
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
            logger.info(f"Added property data for {property_data.get('address')}")
            
        except Exception as e:
            logger.error(f"Error adding property data: {e}")
    
    async def search_similar_properties(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar properties using vector similarity"""
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar properties: {e}")
            return []
    
    async def generate_property_insights(self, property_address: str, context: str = "") -> Dict[str, Any]:
        """Generate AI-powered property insights using RAG"""
        try:
            # Search for relevant context
            search_query = f"property analysis market trends {property_address}"
            relevant_docs = await self.search_similar_properties(search_query, k=3)
            
            # Build context from retrieved documents
            context_text = "\n".join([doc["content"] for doc in relevant_docs])
            
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
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating property insights: {e}")
            return {
                "insights": "Unable to generate insights at this time.",
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
                "trends": results,
                "summary": "Market analysis based on available data",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market trends: {e}")
            return {"trends": [], "error": str(e)}

# Global RAG service instance
rag_service = PropertyRAGService()