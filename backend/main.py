"""TreeLine Backend Main Application

FastAPI application entry point for the TreeLine AI customer support agent.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.core.database import engine, Base
from app.api.routes import chat

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="TreeLine API",
    description="AI-powered customer support agent backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://streamlit-ui:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "treeline-backend",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TreeLine AI Customer Support Agent API",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
