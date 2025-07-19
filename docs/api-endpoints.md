# TreeLine API Endpoints Documentation

This document provides comprehensive documentation for all API endpoints in the TreeLine AI Customer Support Agent.

## Base URLs

- **Backend API**: `http://localhost:8000`
- **AI Agent Service**: `http://localhost:8001`
- **Streamlit UI**: `http://localhost:8501`

## Backend API Endpoints

### Health Check

#### `GET /health`

Check if the backend service is healthy and operational.

**Response:**
```json
{
  "status": "healthy",
  "service": "treeline-backend",
  "version": "0.1.0"
}
```

**Status Codes:**
- `200 OK`: Service is healthy

---

### Root Information

#### `GET /`

Get basic information about the API.

**Response:**
```json
{
  "message": "TreeLine AI Customer Support Agent API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

**Status Codes:**
- `200 OK`: Success

---

### Chat Endpoints

#### `POST /api/chat`

Send a message to the AI agent and receive a response.

**Request Body:**
```json
{
  "message": "string",
  "session_id": "string (optional)"
}
```

**Parameters:**
- `message` (required): The user's message/question
- `session_id` (optional): Session identifier for conversation continuity. If not provided, a new UUID will be generated.

**Response:**
```json
{
  "id": "integer",
  "session_id": "string",
  "user_message": "string",
  "ai_response": "string",
  "response_time_ms": "integer",
  "created_at": "datetime",
  "sources_used": "integer (optional)",
  "knowledge_base_size": "integer (optional)"
}
```

**Status Codes:**
- `200 OK`: Successful response
- `422 Unprocessable Entity`: Invalid request format
- `500 Internal Server Error`: Server error

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How can I reset my password?",
    "session_id": "user-123-session"
  }'
```

**Example Response:**
```json
{
  "id": 1,
  "session_id": "user-123-session",
  "user_message": "How can I reset my password?",
  "ai_response": "To reset your password, please follow these steps: 1. Go to the login page...",
  "response_time_ms": 1250,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### `GET /api/chat/history/{session_id}`

Retrieve chat history for a specific session.

**Path Parameters:**
- `session_id` (required): The session identifier

**Query Parameters:**
- `limit` (optional): Maximum number of messages to return (default: 50)

**Response:**
```json
[
  {
    "id": "integer",
    "session_id": "string",
    "user_message": "string",
    "ai_response": "string",
    "response_time_ms": "integer",
    "created_at": "datetime"
  }
]
```

**Status Codes:**
- `200 OK`: Successful response
- `404 Not Found`: Session not found

**Example Request:**
```bash
curl "http://localhost:8000/api/chat/history/user-123-session?limit=10"
```

---

## AI Agent Service Endpoints

### Health Check

#### `GET /health`

Check if the AI agent service is healthy.

**Response:**
```json
{
  "status": "healthy",
  "service": "treeline-ai-agent"
}
```

**Status Codes:**
- `200 OK`: Service is healthy

---

### Agent Status

#### `GET /status`

Get detailed information about the AI agent configuration and knowledge base.

**Response:**
```json
{
  "agent_name": "TreeLine AI Customer Support Agent",
  "version": "0.1.0",
  "llm_model": "gpt-4-turbo",
  "temperature": 0.7,
  "max_tokens": 1000,
  "knowledge_base": {
    "collection_name": "treeline_knowledge_base",
    "document_count": 25,
    "persist_directory": "./data/vector_db"
  },
  "openai_api_configured": true
}
```

**Status Codes:**
- `200 OK`: Success

---

### Generate Response

#### `POST /generate`

Generate an AI response to a user message (used internally by the backend).

**Request Body:**
```json
{
  "message": "string",
  "session_id": "string (optional)",
  "include_sources": "boolean (optional, default: false)"
}
```

**Response:**
```json
{
  "response": "string",
  "session_id": "string",
  "sources_used": "integer",
  "knowledge_base_size": "integer",
  "fallback_used": "boolean (optional)",
  "error": "string (optional)"
}
```

**Status Codes:**
- `200 OK`: Successful response
- `422 Unprocessable Entity`: Invalid request format
- `500 Internal Server Error`: Server error

---

## Interactive API Documentation

### Swagger UI
Access interactive API documentation at: `http://localhost:8000/docs`

### ReDoc
Alternative API documentation at: `http://localhost:8000/redoc`

## Error Handling

All endpoints follow consistent error response patterns:

### Client Errors (4xx)
```json
{
  "detail": "Error description"
}
```

### Server Errors (5xx)
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. For production deployment, consider implementing rate limiting based on:
- IP address
- Session ID
- API key (if implemented)

## Authentication

Currently, no authentication is required. For production deployment, consider implementing:
- API key authentication
- JWT tokens
- OAuth 2.0

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:8501` (Streamlit UI)
- `http://streamlit-ui:8501` (Docker internal)

Additional origins can be configured via the `ALLOWED_ORIGINS` environment variable.

## Database Schema

### Conversation Table

The backend stores all conversations in a PostgreSQL database:

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Variables

Key environment variables affecting API behavior:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for AI responses
- `AI_AGENT_URL`: URL of the AI agent service
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Send a chat message
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how can you help me?"}'

# Get chat history
curl "http://localhost:8000/api/chat/history/your-session-id"
```

### Using Python requests

```python
import requests

# Send a message
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "What are your business hours?",
        "session_id": "test-session"
    }
)
print(response.json())

# Get history
history = requests.get(
    "http://localhost:8000/api/chat/history/test-session"
)
print(history.json())
```

## Performance Considerations

- **Response Times**: Typical response times range from 1-5 seconds depending on:
  - OpenAI API response time
  - Knowledge base search complexity
  - Database write operations

- **Concurrent Requests**: The FastAPI backend supports concurrent requests using async/await patterns

- **Database Connections**: Connection pooling is handled by SQLAlchemy with async support

## Monitoring and Logging

- All requests are logged with response times
- Health check endpoints for service monitoring
- Database connection health is monitored
- AI agent service availability is checked before requests

---

*Last updated: January 2024*
*API Version: 0.1.0*
