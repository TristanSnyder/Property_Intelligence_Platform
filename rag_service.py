# Quick fix for your rag_service.py to work without OpenAI API key initially

# Add this to the top of your rag_service.py __init__ method:

def __init__(self):
    self.client = chromadb.PersistentClient(path="./chroma_db")
    self.collection_name = "property_intelligence"
    
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if openai_api_key:
        # Use OpenAI embeddings and LLM
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        self.use_openai = True
        logger.info("✅ Using OpenAI for embeddings and LLM")
    else:
        # Use local sentence transformers as fallback
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings = None  # We'll handle embeddings manually
            self.llm = None
            self.use_openai = False
            logger.warning("⚠️ OpenAI API key not found. Using local embeddings (limited functionality)")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
            raise
    
    self.text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    self.vectorstore = None
    self.initialize_vectorstore()

# Also update your generate_property_insights method to handle missing OpenAI:

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
                
                Based on available data and market patterns:
                • Market conditions appear favorable for this location
                • Consider local amenities and transportation access
                • Property valuation should account for comparable sales
                • Investment potential depends on local economic indicators
                
                Note: Limited analysis available without OpenAI API. 
                Add OPENAI_API_KEY for comprehensive AI insights.
                """,
                "sources": [doc.get("metadata", {}) for doc in relevant_docs],
                "relevant_properties": relevant_docs,
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_type": "basic"
            }
        
        # Build context from retrieved documents
        context_text = "\n".join([doc["content"] for doc in relevant_docs])
        
        # Create RAG chain (only if OpenAI is available)
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
            "insights": "Unable to generate insights at this time.",
            "sources": [],
            "relevant_properties": [],
            "error": str(e)
        }
