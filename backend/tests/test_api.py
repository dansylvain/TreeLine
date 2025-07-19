"""API endpoint tests."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint returns correct response."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "treeline-backend"
        assert data["version"] == "0.1.0"


class TestRootEndpoint:
    """Test root endpoint."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns correct response."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "TreeLine AI Customer Support Agent API" in data["message"]
        assert data["version"] == "0.1.0"
        assert data["docs"] == "/docs"


class TestChatEndpoint:
    """Test chat API endpoints."""
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_with_session_id(self, client: AsyncClient, sample_chat_request):
        """Test chat endpoint with provided session ID."""
        response = await client.post("/api/chat", json=sample_chat_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert data["session_id"] == sample_chat_request["session_id"]
        assert data["user_message"] == sample_chat_request["message"]
        assert "ai_response" in data
        assert "response_time_ms" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_without_session_id(self, client: AsyncClient):
        """Test chat endpoint without session ID (should generate one)."""
        request_data = {"message": "Hello, how can you help me?"}
        response = await client.post("/api/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that session_id was generated
        assert "session_id" in data
        assert data["session_id"] is not None
        assert len(data["session_id"]) > 0
        assert data["user_message"] == request_data["message"]
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_empty_message(self, client: AsyncClient):
        """Test chat endpoint with empty message."""
        request_data = {"message": ""}
        response = await client.post("/api/chat", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_long_message(self, client: AsyncClient):
        """Test chat endpoint with message exceeding max length."""
        long_message = "x" * 2001  # Exceeds 2000 character limit
        request_data = {"message": long_message}
        response = await client.post("/api/chat", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_chat_history_endpoint(self, client: AsyncClient, sample_chat_request):
        """Test chat history endpoint."""
        # First, create a conversation
        chat_response = await client.post("/api/chat", json=sample_chat_request)
        assert chat_response.status_code == 200
        
        session_id = sample_chat_request["session_id"]
        
        # Then, get the history
        history_response = await client.get(f"/api/chat/history/{session_id}")
        assert history_response.status_code == 200
        
        history_data = history_response.json()
        assert isinstance(history_data, list)
        assert len(history_data) == 1
        assert history_data[0]["session_id"] == session_id
        assert history_data[0]["user_message"] == sample_chat_request["message"]
    
    @pytest.mark.asyncio
    async def test_chat_history_empty(self, client: AsyncClient):
        """Test chat history for non-existent session."""
        response = await client.get("/api/chat/history/non-existent-session")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
