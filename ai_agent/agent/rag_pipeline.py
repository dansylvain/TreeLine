"""RAG (Retrieval-Augmented Generation) pipeline implementation."""

import os
from typing import List, Optional, Dict, Any

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import Document

from .vector_store import VectorStoreManager


class RAGPipeline:
    """RAG pipeline for customer support using ChromaDB and OpenAI."""
    
    def __init__(
        self,
        vector_store_manager: Optional[VectorStoreManager] = None,
        llm_model: str = "gpt-4-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        self.vector_store_manager = vector_store_manager or VectorStoreManager()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Customer support prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are TreeLine, a helpful AI customer support agent. Use the following context information to answer the customer's question. If the context doesn't contain relevant information, provide a helpful general response and suggest they contact human support for specific issues.

Context:
{context}

Customer Question: {question}

Response Guidelines:
- Be friendly, professional, and empathetic
- Provide clear, actionable answers when possible
- If you don't have specific information, be honest about it
- Offer to escalate to human support when appropriate
- Keep responses concise but comprehensive

Answer:"""
        )
        
        # Initialize retrieval chain
        self.retrieval_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store_manager.as_retriever(
                search_kwargs={"k": 4}
            ),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
    
    def generate_response(
        self,
        query: str,
        session_id: Optional[str] = None,
        include_sources: bool = False
    ) -> Dict[str, Any]:
        """Generate a response using RAG pipeline."""
        
        try:
            # Check if vector store has any documents
            collection_info = self.vector_store_manager.get_collection_info()
            
            if collection_info["count"] == 0:
                # No knowledge base available, use general response
                return self._generate_fallback_response(query, session_id)
            
            # Use RAG pipeline
            result = self.retrieval_chain.invoke({"query": query})
            
            response_data = {
                "response": result["result"],
                "session_id": session_id,
                "sources_used": len(result.get("source_documents", [])),
                "knowledge_base_size": collection_info["count"]
            }
            
            if include_sources:
                response_data["source_documents"] = [
                    {
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result.get("source_documents", [])
                ]
            
            return response_data
            
        except Exception as e:
            print(f"Error in RAG pipeline: {e}")
            return self._generate_fallback_response(query, session_id, error=str(e))
    
    def _generate_fallback_response(
        self,
        query: str,
        session_id: Optional[str] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a fallback response when RAG pipeline fails or no knowledge base exists."""
        
        fallback_prompt = PromptTemplate(
            input_variables=["question"],
            template="""You are TreeLine, a helpful AI customer support agent. The customer has asked: {question}

Since I don't have access to specific company information right now, I'll provide a helpful general response and guide them to appropriate next steps.

Provide a friendly, professional response that:
- Acknowledges their question
- Offers general helpful guidance if possible
- Suggests contacting human support for specific account or technical issues
- Maintains a positive, supportive tone

Answer:"""
        )
        
        try:
            # Use LLM directly for fallback response
            chain = fallback_prompt | self.llm
            response = chain.invoke({"question": query})
            
            return {
                "response": response.content,
                "session_id": session_id,
                "sources_used": 0,
                "knowledge_base_size": 0,
                "fallback_used": True,
                "error": error
            }
            
        except Exception as e:
            # Ultimate fallback
            return {
                "response": "I apologize, but I'm experiencing technical difficulties right now. Please contact our human support team for assistance with your question.",
                "session_id": session_id,
                "sources_used": 0,
                "knowledge_base_size": 0,
                "fallback_used": True,
                "error": str(e)
            }
    
    def add_knowledge(
        self,
        documents: List[Document] = None,
        texts: List[str] = None,
        metadatas: List[Dict] = None
    ) -> int:
        """Add knowledge to the vector store."""
        if documents:
            ids = self.vector_store_manager.add_documents(documents)
            return len(ids)
        elif texts:
            ids = self.vector_store_manager.add_texts(texts, metadatas)
            return len(ids)
        return 0
    
    def search_knowledge(
        self,
        query: str,
        k: int = 4,
        include_scores: bool = False
    ) -> List[Dict[str, Any]]:
        """Search the knowledge base."""
        if include_scores:
            results = self.vector_store_manager.similarity_search_with_score(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                }
                for doc, score in results
            ]
        else:
            results = self.vector_store_manager.similarity_search(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in results
            ]
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get information about the knowledge base."""
        return self.vector_store_manager.get_collection_info()
    
    def load_knowledge_from_directory(self, directory_path: str) -> int:
        """Load knowledge from a directory of documents."""
        return self.vector_store_manager.load_documents_from_directory(directory_path)
