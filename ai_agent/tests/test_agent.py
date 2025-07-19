"""AI Agent tests."""

import pytest
import os
from unittest.mock import Mock, patch
from langchain.schema import Document

from agent.core import TreeLineAgent
from agent.vector_store import VectorStoreManager
from agent.rag_pipeline import RAGPipeline


class TestVectorStoreManager:
    """Test VectorStoreManager functionality."""
    
    @pytest.fixture
    def temp_vector_store(self, tmp_path):
        """Create a temporary vector store for testing."""
        return VectorStoreManager(
            persist_directory=str(tmp_path / "test_vector_db"),
            collection_name="test_collection"
        )
    
    def test_vector_store_initialization(self, temp_vector_store):
        """Test vector store initializes correctly."""
        assert temp_vector_store.collection_name == "test_collection"
        assert temp_vector_store.embedding_model == "text-embedding-ada-002"
        assert temp_vector_store.persist_directory.exists()
    
    def test_add_texts(self, temp_vector_store):
        """Test adding texts to vector store."""
        texts = ["This is a test document", "Another test document"]
        metadatas = [{"source": "test1"}, {"source": "test2"}]
        
        with patch.object(temp_vector_store.vector_store, 'add_documents') as mock_add:
            mock_add.return_value = ["id1", "id2"]
            ids = temp_vector_store.add_texts(texts, metadatas)
            
            assert len(ids) == 2
            mock_add.assert_called_once()
    
    def test_get_collection_info(self, temp_vector_store):
        """Test getting collection information."""
        info = temp_vector_store.get_collection_info()
        
        assert "name" in info
        assert "count" in info
        assert "metadata" in info
        assert info["name"] == "test_collection"


class TestRAGPipeline:
    """Test RAG pipeline functionality."""
    
    @pytest.fixture
    def mock_vector_store(self):
        """Create a mock vector store."""
        mock_store = Mock(spec=VectorStoreManager)
        mock_store.get_collection_info.return_value = {
            "name": "test_collection",
            "count": 5,
            "metadata": {}
        }
        return mock_store
    
    @pytest.fixture
    def rag_pipeline(self, mock_vector_store):
        """Create RAG pipeline with mock vector store."""
        with patch('agent.rag_pipeline.ChatOpenAI') as mock_llm:
            mock_llm.return_value = Mock()
            pipeline = RAGPipeline(vector_store_manager=mock_vector_store)
            return pipeline
    
    def test_rag_pipeline_initialization(self, rag_pipeline):
        """Test RAG pipeline initializes correctly."""
        assert rag_pipeline.vector_store_manager is not None
        assert rag_pipeline.llm is not None
        assert rag_pipeline.prompt_template is not None
    
    def test_generate_fallback_response(self, rag_pipeline):
        """Test fallback response generation."""
        with patch.object(rag_pipeline.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = "I'm here to help! Please contact support."
            mock_invoke.return_value = mock_response
            
            result = rag_pipeline._generate_fallback_response("Help me", "session123")
            
            assert result["response"] == "I'm here to help! Please contact support."
            assert result["session_id"] == "session123"
            assert result["fallback_used"] is True
            assert result["sources_used"] == 0
    
    def test_generate_response_no_knowledge_base(self, rag_pipeline):
        """Test response generation when no knowledge base exists."""
        rag_pipeline.vector_store_manager.get_collection_info.return_value = {
            "name": "test_collection",
            "count": 0,
            "metadata": {}
        }
        
        with patch.object(rag_pipeline, '_generate_fallback_response') as mock_fallback:
            mock_fallback.return_value = {"response": "Fallback response", "fallback_used": True}
            
            result = rag_pipeline.generate_response("Test query")
            
            assert result["fallback_used"] is True
            mock_fallback.assert_called_once()


class TestTreeLineAgent:
    """Test TreeLine agent functionality."""
    
    @pytest.fixture
    def mock_agent(self, tmp_path):
        """Create agent with mocked dependencies."""
        with patch('agent.core.VectorStoreManager') as mock_vsm, \
             patch('agent.core.RAGPipeline') as mock_rag:
            
            # Mock vector store manager
            mock_vsm_instance = Mock()
            mock_vsm.return_value = mock_vsm_instance
            
            # Mock RAG pipeline
            mock_rag_instance = Mock()
            mock_rag.return_value = mock_rag_instance
            
            agent = TreeLineAgent(persist_directory=str(tmp_path / "test_db"))
            return agent
    
    def test_agent_initialization(self, mock_agent):
        """Test agent initializes correctly."""
        assert mock_agent.llm_model == "gpt-4-turbo"
        assert mock_agent.temperature == 0.7
        assert mock_agent.max_tokens == 1000
        assert mock_agent.vector_store_manager is not None
        assert mock_agent.rag_pipeline is not None
    
    def test_generate_response_empty_message(self, mock_agent):
        """Test response to empty message."""
        result = mock_agent.generate_response("")
        
        assert "I'd be happy to help!" in result["response"]
        assert result["fallback_used"] is True
        assert result["sources_used"] == 0
    
    def test_generate_response_valid_message(self, mock_agent):
        """Test response to valid message."""
        mock_agent.rag_pipeline.generate_response.return_value = {
            "response": "Here's how I can help you",
            "session_id": "test123",
            "sources_used": 2,
            "knowledge_base_size": 10
        }
        
        result = mock_agent.generate_response("How can you help me?", "test123")
        
        assert result["response"] == "Here's how I can help you"
        assert result["session_id"] == "test123"
        assert result["sources_used"] == 2
        mock_agent.rag_pipeline.generate_response.assert_called_once()
    
    def test_get_status(self, mock_agent):
        """Test getting agent status."""
        mock_agent.rag_pipeline.get_knowledge_base_info.return_value = {
            "name": "test_collection",
            "count": 5,
            "metadata": {}
        }
        
        status = mock_agent.get_status()
        
        assert status["agent_name"] == "TreeLine AI Customer Support Agent"
        assert status["version"] == "0.1.0"
        assert status["llm_model"] == "gpt-4-turbo"
        assert status["knowledge_base"]["document_count"] == 5
        assert "openai_api_configured" in status
    
    def test_add_knowledge(self, mock_agent):
        """Test adding knowledge to agent."""
        mock_agent.rag_pipeline.add_knowledge.return_value = 3
        
        result = mock_agent.add_knowledge(texts=["doc1", "doc2", "doc3"])
        
        assert result == 3
        mock_agent.rag_pipeline.add_knowledge.assert_called_once_with(
            documents=None,
            texts=["doc1", "doc2", "doc3"],
            metadatas=None
        )
    
    def test_search_knowledge(self, mock_agent):
        """Test searching knowledge base."""
        mock_results = [
            {"content": "Test content", "metadata": {"source": "test.txt"}}
        ]
        mock_agent.rag_pipeline.search_knowledge.return_value = mock_results
        
        results = mock_agent.search_knowledge("test query")
        
        assert len(results) == 1
        assert results[0]["content"] == "Test content"
        mock_agent.rag_pipeline.search_knowledge.assert_called_once_with(
            query="test query",
            k=4,
            include_scores=False
        )


class TestAgentIntegration:
    """Integration tests for the agent."""
    
    @pytest.mark.integration
    def test_agent_with_real_components(self, tmp_path):
        """Test agent with real components (requires OpenAI API key)."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OpenAI API key not available")
        
        agent = TreeLineAgent(persist_directory=str(tmp_path / "integration_test"))
        
        # Test basic functionality
        status = agent.get_status()
        assert status["openai_api_configured"] is True
        
        # Test response generation (will use fallback since no knowledge base)
        result = agent.generate_response("Hello, can you help me?")
        assert "response" in result
        assert len(result["response"]) > 0
