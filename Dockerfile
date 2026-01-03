FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install MCP SDK
RUN pip install --no-cache-dir mcp

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose MCP server port (stdio via stdin/stdout)
# MCP typically uses stdio, but we can expose a port for monitoring
EXPOSE 8000

# Default command runs MCP server
CMD ["python", "-m", "mcp_server.server"]
