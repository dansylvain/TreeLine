"""Core AI agent implementation."""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .rag_pipeline import RAGPipeline
from .vector_store import VectorStoreManager

from agent.logger import TreeLineLogger

logger = TreeLineLogger().logger

# Load environment variables
load_dotenv()


class TreeLineAgent:
    """Main TreeLine AI customer support agent."""
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
        llm_model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        # Get configuration from environment or use defaults
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "./data/vector_db"
        )
        self.collection_name = collection_name or os.getenv(
            "COLLECTION_NAME", "treeline_knowledge_base"
        )
        self.llm_model = llm_model or os.getenv("LLM_MODEL", "gpt-4-turbo")
        self.temperature = temperature or float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens = max_tokens or int(os.getenv("MAX_TOKENS", "1000"))
        
        # Initialize components
        self.vector_store_manager = VectorStoreManager(
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        )
        
        self.rag_pipeline = RAGPipeline(
            vector_store_manager=self.vector_store_manager,
            llm_model=self.llm_model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Initialize knowledge base if directory exists
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize knowledge base from documents directory."""
        knowledge_dir = "./data/knowledge_base"
        if os.path.exists(knowledge_dir):
            docs_loaded = self.rag_pipeline.load_knowledge_from_directory(knowledge_dir)
            if docs_loaded > 0:
                print(f"Loaded {docs_loaded} documents into knowledge base")
        else:
            print("No knowledge base directory found. Agent will use fallback responses.")
    
    def generate_response(
        self,
        message: str,
        session_id: Optional[str] = None,
        include_sources: bool = False
    ) -> Dict[str, Any]:
        """Generate a response to a customer message."""
        if not message or not message.strip():
            return {
                "response": "I'd be happy to help! Could you please tell me what you need assistance with?",
                "session_id": session_id,
                "sources_used": 0,
                "knowledge_base_size": 0,
                "fallback_used": True
            }
        
        return self.rag_pipeline.generate_response(
            query=message.strip(),
            session_id=session_id,
            include_sources=include_sources
        )
    
    def add_knowledge(
        self,
        texts: list = None,
        documents: list = None,
        metadatas: list = None
    ) -> int:
        """Add knowledge to the agent's knowledge base."""
        return self.rag_pipeline.add_knowledge(
            documents=documents,
            texts=texts,
            metadatas=metadatas
        )
    
    def search_knowledge(
        self,
        query: str,
        k: int = 4,
        include_scores: bool = False
    ) -> list:
        """Search the knowledge base."""
        return self.rag_pipeline.search_knowledge(
            query=query,
            k=k,
            include_scores=include_scores
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and configuration."""
        kb_info = self.rag_pipeline.get_knowledge_base_info()
        
        return {
            "agent_name": "TreeLine AI Customer Support Agent",
            "version": "0.1.0",
            "llm_model": self.llm_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "knowledge_base": {
                "collection_name": kb_info["name"],
                "document_count": kb_info["count"],
                "persist_directory": self.persist_directory
            },
            "openai_api_configured": bool(os.getenv("OPENAI_API_KEY"))
        }


# Global agent instance
_agent_instance = None


def get_agent() -> TreeLineAgent:
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TreeLineAgent()
    return _agent_instance


# For standalone execution
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    from pydantic import BaseModel
    
    # Create FastAPI app for standalone mode
    app = FastAPI(
        title="TreeLine AI Agent",
        description="Standalone AI agent service",
        version="0.1.0"
    )
    
    class GenerateRequest(BaseModel):
        message: str
        session_id: Optional[str] = None
        include_sources: bool = False
    
    class GenerateResponse(BaseModel):
        response: str
        session_id: Optional[str]
        sources_used: int
        knowledge_base_size: int
        fallback_used: Optional[bool] = None
        error: Optional[str] = None
    
    @app.post("/generate", response_model=GenerateResponse)
    async def generate_response(request: GenerateRequest):
        """Generate a response using the AI agent."""
        agent = get_agent()
        result = agent.generate_response(
            message=request.message,
            session_id=request.session_id,
            include_sources=request.include_sources
        )
        return GenerateResponse(**result)
    
    @app.get("/status")
    async def get_status():
        """Get agent status."""
        agent = get_agent()
        return agent.get_status()
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "treeline-ai-agent"}
    
    agent = get_agent()

    # Run the standalone service
    uvicorn.run(app, host="0.0.0.0", port=8001)
