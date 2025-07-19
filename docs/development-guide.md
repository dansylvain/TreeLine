# TreeLine Development Guide

This guide provides development best practices, code standards, and workflow recommendations for the TreeLine AI Customer Support Agent project.

## 🏗️ Project Architecture

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  FastAPI Backend │────│   AI Agent      │
│   (Port 8501)   │    │   (Port 8000)    │    │   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │    ChromaDB     │
                       │   (Port 5432)   │    │  Vector Store   │
                       └─────────────────┘    └─────────────────┘
```

### Directory Structure
```
TreeLine/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Configuration and database
│   │   ├── models/         # SQLAlchemy database models
│   │   └── schemas/        # Pydantic request/response schemas
│   └── tests/              # Backend unit tests
├── ai_agent/               # AI agent service
│   ├── agent/              # Core agent logic
│   ├── data/               # Knowledge base and vector storage
│   └── tests/              # Agent unit tests
├── ui/                     # Streamlit user interface
│   ├── components/         # Reusable UI components
│   └── tests/              # UI tests
├── config/                 # Configuration files
├── docs/                   # Documentation
└── dev.sh                  # Development script
```

## 🛠️ Development Workflow

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/TreeLine.git
cd TreeLine

# Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Start development environment
./dev.sh start
```

### 2. Development Commands

```bash
# Start all services
./dev.sh start

# Check service status
./dev.sh status

# View logs
./dev.sh logs [service_name]

# Run tests
./dev.sh test

# Format code
./dev.sh format

# Open services in browser
./dev.sh open

# Clean up
./dev.sh clean
```

### 3. Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   ./dev.sh test
   ./dev.sh format
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### Python Code Style

- **Formatter**: Black (line length: 88 characters)
- **Linter**: Ruff for fast linting and import sorting
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings

#### Example Function
```python
from typing import Optional, Dict, Any

async def process_user_message(
    message: str,
    session_id: Optional[str] = None,
    include_sources: bool = False
) -> Dict[str, Any]:
    """Process a user message and generate an AI response.
    
    Args:
        message: The user's input message
        session_id: Optional session identifier for conversation continuity
        include_sources: Whether to include source information in response
        
    Returns:
        Dictionary containing the AI response and metadata
        
    Raises:
        ValueError: If message is empty or invalid
        HTTPException: If AI service is unavailable
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")
    
    # Implementation here
    return {"response": "...", "session_id": session_id}
```

### FastAPI Best Practices

#### Route Organization
```python
# backend/app/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def create_chat_message(
    request: ChatRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ChatResponse:
    """Create a new chat message and get AI response."""
    # Implementation
```

#### Error Handling
```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

try:
    # Operation that might fail
    result = await some_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(
        status_code=400,
        detail=f"Operation failed: {str(e)}"
    )
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(
        status_code=500,
        detail="Internal server error"
    )
```

### Database Best Practices

#### Model Definition
```python
# backend/app/models/conversation.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class Conversation(Base):
    """Conversation model for storing chat history."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### Database Queries
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_conversation_history(
    db: AsyncSession,
    session_id: str,
    limit: int = 50
) -> List[Conversation]:
    """Get conversation history for a session."""
    stmt = (
        select(Conversation)
        .where(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
```

### AI Agent Best Practices

#### Configuration Management
```python
# ai_agent/agent/core.py
import os
from typing import Optional
from pydantic_settings import BaseSettings

class AgentSettings(BaseSettings):
    """AI Agent configuration settings."""
    
    openai_api_key: str
    llm_model: str = "gpt-4-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    embedding_model: str = "text-embedding-ada-002"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

#### Error Handling in AI Operations
```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def generate_response(self, message: str) -> Dict[str, Any]:
    """Generate AI response with proper error handling."""
    try:
        # AI generation logic
        response = self.llm.generate(message)
        return {
            "response": response,
            "error": None,
            "fallback_used": False
        }
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return {
            "response": "I'm experiencing technical difficulties. Please try again.",
            "error": str(e),
            "fallback_used": True
        }
    except Exception as e:
        logger.error(f"Unexpected error in AI generation: {e}")
        return {
            "response": "I'm sorry, I couldn't process your request.",
            "error": str(e),
            "fallback_used": True
        }
```

### Streamlit UI Best Practices

#### Component Organization
```python
# ui/components/chat_interface.py
import streamlit as st
from typing import List, Dict, Any

def render_chat_message(message: Dict[str, Any], is_user: bool = False) -> None:
    """Render a single chat message."""
    css_class = "user-message" if is_user else "ai-message"
    sender = "You" if is_user else "TreeLine AI"
    
    st.markdown(f"""
    <div class="chat-message {css_class}">
        <strong>{sender}:</strong><br>
        {message['content']}
        <div class="timestamp">{message['timestamp']}</div>
    </div>
    """, unsafe_allow_html=True)

def render_chat_history(messages: List[Dict[str, Any]]) -> None:
    """Render the complete chat history."""
    for message in messages:
        render_chat_message(message, message.get("is_user", False))
```

## 🧪 Testing Standards

### Unit Test Structure
```python
# tests/test_chat_api.py
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

class TestChatAPI:
    """Test cases for chat API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_chat_message_success(self, async_client: AsyncClient):
        """Test successful chat message creation."""
        response = await async_client.post(
            "/api/chat",
            json={
                "message": "Hello, how can you help me?",
                "session_id": "test-session"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_message"] == "Hello, how can you help me?"
        assert data["session_id"] == "test-session"
        assert "ai_response" in data
        assert data["response_time_ms"] > 0
    
    @pytest.mark.asyncio
    async def test_create_chat_message_empty_message(self, async_client: AsyncClient):
        """Test chat message creation with empty message."""
        response = await async_client.post(
            "/api/chat",
            json={"message": ""}
        )
        
        assert response.status_code == 422
```

### Test Configuration
```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@pytest.fixture
async def async_client():
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db_session():
    """Create test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        yield session
```

## 📊 Logging Standards

### Logging Configuration
```python
# backend/app/core/logging.py
import logging
import sys
from typing import Optional

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Set up application logging."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
```

### Logging Usage
```python
import logging

logger = logging.getLogger(__name__)

# Info level for normal operations
logger.info(f"Processing chat message for session {session_id}")

# Warning for recoverable issues
logger.warning(f"AI service timeout, using fallback response")

# Error for serious issues
logger.error(f"Database connection failed: {error}")

# Debug for detailed troubleshooting
logger.debug(f"Generated response: {response[:100]}...")
```

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique passwords for database connections
- Rotate API keys regularly
- Use environment-specific configurations

### API Security
```python
# Future: Rate limiting example
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, ...):
    """Rate-limited chat endpoint."""
    pass
```

### Input Validation
```python
from pydantic import BaseModel, validator

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    
    @validator('message')
    def message_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
```

## 🚀 Performance Optimization

### Database Optimization
- Use database indexes on frequently queried columns
- Implement connection pooling
- Use async database operations
- Consider read replicas for high-traffic scenarios

### Caching Strategies
```python
# Future: Redis caching example
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(expiration: int = 300):
    """Cache decorator for expensive operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### AI Agent Optimization
- Implement response caching for common queries
- Use streaming responses for long generations
- Optimize vector search parameters
- Consider model fine-tuning for domain-specific responses

## 📈 Monitoring and Observability

### Health Checks
```python
# backend/app/api/routes/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "treeline-backend"}

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check including dependencies."""
    checks = {
        "database": await check_database_health(db),
        "ai_agent": await check_ai_agent_health(),
        "openai_api": await check_openai_health()
    }
    
    overall_status = "healthy" if all(
        check["status"] == "healthy" for check in checks.values()
    ) else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Metrics Collection
```python
# Future: Prometheus metrics example
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
AI_RESPONSE_TIME = Histogram('ai_response_duration_seconds', 'AI response generation time')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect request metrics."""
    start_time = time.time()
    
    response = await call_next(request)
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response
```

## 🔄 Deployment Best Practices

### Environment Configuration
```bash
# Production environment variables
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/treeline
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# AI Configuration
OPENAI_API_KEY=your-production-api-key
LLM_MODEL=gpt-4-turbo
TEMPERATURE=0.5
MAX_TOKENS=800

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_FILE=/var/log/treeline/app.log
```

### Docker Production Configuration
```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### CI/CD Pipeline Example
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt
        pip install -r ai_agent/requirements.txt
    
    - name: Run tests
      run: |
        pytest backend/tests/
        pytest ai_agent/tests/
    
    - name: Run linting
      run: |
        ruff check backend/ ai_agent/ ui/
        black --check backend/ ai_agent/ ui/
```

## 🐛 Debugging and Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Issues
```bash
# Check database connectivity
./dev.sh logs postgres

# Reset database
./dev.sh stop
docker volume rm treeline_postgres_data
./dev.sh start
```

#### 2. AI Agent Not Responding
```bash
# Check AI agent logs
./dev.sh logs ai-agent

# Verify OpenAI API key
grep OPENAI_API_KEY .env

# Test AI agent directly
curl http://localhost:8001/health
```

#### 3. Streamlit UI Issues
```bash
# Check UI logs
./dev.sh logs streamlit-ui

# Verify backend connectivity
curl http://localhost:8000/health
```

### Debug Mode Configuration
```python
# backend/main.py - Development debugging
if settings.debug:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Enable SQL query logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## 📚 Additional Resources

### Documentation Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)

### Development Tools
- **IDE**: VS Code with Python extension
- **Database Client**: pgAdmin or DBeaver
- **API Testing**: Postman or Insomnia
- **Container Management**: Docker Desktop
- **Version Control**: Git with conventional commits

---

*This guide is a living document. Please update it as the project evolves and new best practices are established.*
