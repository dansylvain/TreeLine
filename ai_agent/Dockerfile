FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data
RUN mkdir -p /app/data/knowledge_base /app/data/vector_db

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (if running as standalone service)
EXPOSE 8001

# Run the AI agent (can be imported or run standalone)
CMD ["python", "-m", "agent.core"]
