# TreeLine AI Customer Support Agent

TreeLine is an AI-powered customer support agent built with modern technologies including FastAPI, LangChain, ChromaDB, and Streamlit. It provides intelligent customer support through a retrieval-augmented generation (RAG) pipeline that can answer questions based on your knowledge base.

## 🌲 Features

- **AI-Powered Responses**: Uses OpenAI GPT-4 Turbo for natural language understanding and generation
- **RAG Pipeline**: Retrieval-augmented generation with ChromaDB vector store for knowledge retrieval
- **FastAPI Backend**: High-performance async API with automatic documentation
- **PostgreSQL Database**: Reliable conversation storage and history
- **Streamlit UI**: Clean, intuitive web interface for customer interactions
- **Docker Compose**: Easy deployment and development setup
- **Comprehensive Testing**: Unit tests for all components with pytest
- **Code Quality**: Linting and formatting with ruff and black

## 🏗️ Architecture

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

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/TreeLine.git
cd TreeLine
```

### 2. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the Application

Use the development script to start all services:

```bash
chmod +x dev.sh
./dev.sh start
```

This will:
- Start PostgreSQL database
- Start the FastAPI backend
- Start the AI agent service
- Start the Streamlit UI
- Load sample knowledge base documents

### 4. Access the Application

- **Streamlit UI**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **AI Agent Service**: http://localhost:8001

## 📁 Project Structure

```
TreeLine/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration and database
│   │   ├── models/         # SQLAlchemy models
│   │   └── schemas/        # Pydantic schemas
│   ├── tests/              # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── ai_agent/               # AI agent service
│   ├── agent/              # Core agent logic
│   │   ├── core.py         # Main agent class
│   │   ├── rag_pipeline.py # RAG implementation
│   │   └── vector_store.py # ChromaDB management
│   ├── data/
│   │   ├── knowledge_base/ # Knowledge documents
│   │   └── vector_db/      # ChromaDB storage
│   ├── tests/              # Agent tests
│   ├── Dockerfile
│   └── requirements.txt
├── ui/                     # Streamlit user interface
│   ├── components/         # UI components
│   ├── tests/              # UI tests
│   ├── .streamlit/         # Streamlit configuration
│   ├── streamlit_app.py    # Main UI application
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml      # Docker services configuration
├── dev.sh                  # Development script
├── pyproject.toml          # Python project configuration
├── .env.example            # Environment variables template
└── README.md
```

## 🛠️ Development

### Development Commands

The `dev.sh` script provides convenient commands for development:

```bash
# Start all services
./dev.sh start

# Stop all services
./dev.sh stop

# Restart all services
./dev.sh restart

# Check service status and health
./dev.sh status

# View logs
./dev.sh logs [service_name]

# Open services in browser
./dev.sh open

# Run tests
./dev.sh test

# Format code
./dev.sh format

# Clean up (remove containers and volumes)
./dev.sh clean

# Show help
./dev.sh help
```

### Adding Knowledge Base Documents

1. Add your documents (`.txt`, `.md`, or `.json` files) to `ai_agent/data/knowledge_base/`
2. Restart the AI agent service:
   ```bash
   ./dev.sh restart ai-agent
   ```

The agent will automatically load and index the new documents.

### Running Tests

Run all tests:
```bash
./dev.sh test
```

Run specific component tests:
```bash
# Backend tests
cd backend && python -m pytest

# AI agent tests
cd ai_agent && python -m pytest

# UI tests
cd ui && python -m pytest
```

### Code Quality

Format code:
```bash
./dev.sh format
```

Lint code:
```bash
./dev.sh lint
```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=gpt-4-turbo
EMBEDDING_MODEL=text-embedding-ada-002
TEMPERATURE=0.7
MAX_TOKENS=1000

# Database Configuration
POSTGRES_USER=treeline
POSTGRES_PASSWORD=treeline_password
POSTGRES_DB=treeline
DATABASE_URL=postgresql+asyncpg://treeline:treeline_password@db:5432/treeline

# Service URLs
BACKEND_URL=http://backend:8000
AI_AGENT_URL=http://ai-agent:8001

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./data/vector_db
COLLECTION_NAME=treeline_knowledge_base
```

### Customizing the AI Agent

Edit `ai_agent/agent/rag_pipeline.py` to customize:
- Prompt templates
- Response generation logic
- Knowledge retrieval parameters

### Customizing the UI

Edit `ui/streamlit_app.py` and `ui/components/` to customize:
- UI layout and styling
- Chat interface behavior
- Additional features

## 📊 API Documentation

The FastAPI backend provides automatic API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/chat` - Send a message to the AI agent
- `GET /api/chat/history/{session_id}` - Get chat history
- `GET /health` - Health check
- `GET /` - API information

## 🧪 Testing

The project includes comprehensive tests:

- **Backend Tests**: API endpoints, database models, business logic
- **AI Agent Tests**: RAG pipeline, vector store, agent responses
- **UI Tests**: Component rendering, user interactions

Run tests with coverage:
```bash
./dev.sh test --coverage
```

## 🚢 Deployment

### Production Deployment

1. Set production environment variables
2. Use production-ready database (not the development PostgreSQL)
3. Configure proper secrets management
4. Set up reverse proxy (nginx) for the UI
5. Enable HTTPS
6. Configure monitoring and logging

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `./dev.sh test`
5. Format code: `./dev.sh format`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

- **[API Endpoints](docs/api-endpoints.md)**: Comprehensive API documentation with examples
- **[Development Guide](docs/development-guide.md)**: Best practices, coding standards, and workflow
- **[Code Review Observations](docs/code-review-observations.md)**: Code quality analysis and future improvements
- **[Database Initialization](docs/database-initialization.md)**: Database setup and schema information

## 🆘 Support

- **Documentation**: Check this README and the docs/ directory
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 and embedding models
- **LangChain** for LLM orchestration framework
- **ChromaDB** for vector database
- **FastAPI** for the high-performance backend
- **Streamlit** for the intuitive UI framework
- **PostgreSQL** for reliable data storage

---

Built with ❤️ for better customer support experiences.
