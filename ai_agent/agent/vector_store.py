"""Vector store management using ChromaDB."""

import os
from typing import List, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from agent.logger import TreeLineLogger

logger = TreeLineLogger().logger


class VectorStoreManager:
    """Manages ChromaDB vector store for RAG pipeline."""
    
    def __init__(
        self,
        persist_directory: str = "./data/vector_db",
        collection_name: str = "treeline_knowledge_base",
        embedding_model: str = "text-embedding-ada-002"
    ):
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Ensure directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize vector store
        self.vector_store = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory)
        )
        
        # Text splitter for document processing
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        if not documents:
            return []
        
        # Split documents into chunks
        split_docs = self.text_splitter.split_documents(documents)
        
        # ************** LOGS **************
        # ************** LOGS **************
        # ************** LOGS **************
        logger.info(f"[SPLIT] Split into {len(split_docs)} chunks")
        if split_docs:
            logger.info(f"[SPLIT] First chunk preview:\n{split_docs[0].page_content[:300]}")
        # ************** LOGS **************
        # ************** LOGS **************
        # ************** LOGS **************

        # Add to vector store
        ids = self.vector_store.add_documents(split_docs)

        # ************** LOGS **************
        # ************** LOGS **************
        # ************** LOGS **************
        logger.info(f"[VECTOR_DB] Added {len(ids)} embedded chunks to collection '{self.collection_name}'")
        
        # Inspecte les embeddings générés (attention, ça peut être long)
        sample_text = split_docs[0].page_content if split_docs else None
        if sample_text:
            sample_embedding = self.embeddings.embed_query(sample_text)
            logger.info(f"[EMBED] Sample embedding (first 10 floats): {sample_embedding[:10]}")
            logger.info(f"[EMBED] Length of embedding: {len(sample_embedding)} dimensions")

        # ************** LOGS **************
        # ************** LOGS **************
        # ************** LOGS **************
        return ids
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> List[str]:
        """Add raw texts to the vector store."""
        if not texts:
            return []
        
        # Create documents from texts
        documents = [
            Document(page_content=text, metadata=metadata or {})
            for text, metadata in zip(texts, metadatas or [{}] * len(texts))
        ]
        
        return self.add_documents(documents)
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """Search for similar documents."""
        return self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter
        )
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[tuple[Document, float]]:
        """Search for similar documents with similarity scores."""
        return self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter
        )
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass  # Collection might not exist
    
    def get_collection_info(self) -> dict:
        """Get information about the collection."""
        try:
            collection = self.client.get_collection(self.collection_name)
            return {
                "name": collection.name,
                "count": collection.count(),
                "metadata": collection.metadata
            }
        except Exception:
            return {
                "name": self.collection_name,
                "count": 0,
                "metadata": {}
            }
    
    def load_documents_from_directory(self, directory_path: str) -> int:
        """Load documents from a directory."""
        directory = Path(directory_path)
        if not directory.exists():
            return 0
        
        documents = []
        supported_extensions = {'.txt', '.md', '.json'}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(file_path),
                            "filename": file_path.name,
                            "file_type": file_path.suffix
                        }
                    )
                    documents.append(doc)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        # ************** LOGS **************
        # ************** LOGS **************
        # ************** LOGS **************
        logger.info(f"[LOAD] Loaded {len(documents)} documents from {directory_path}")
        if documents:
            logger.info(f"[LOAD] First document preview:\n{documents[0].page_content[:300]}")
        # ************** LOGS **************
        # ************** LOGS **************
        # ************** LOGS **************


        if documents:
            self.add_documents(documents)
        
        return len(documents)
    
    def as_retriever(self, **kwargs):
        """Return the vector store as a retriever."""
        return self.vector_store.as_retriever(**kwargs)
