# KAMCO MCP Server Setup Guide

## Overview

This guide explains how to set up and use the KAMCO MCP (Model Context Protocol) server to connect with ChatGPT locally.

## What is MCP?

MCP (Model Context Protocol) is a protocol that allows AI assistants like ChatGPT to interact with external tools and data sources. The KAMCO MCP server provides ChatGPT with access to KAMCO (Korea Asset Management Corporation) public auction data through RAG (Retrieval-Augmented Generation).

## Architecture

```
ChatGPT (Local)
    ↓ (MCP Protocol)
KAMCO MCP Server
    ├─ MongoDB (raw + metadata)
    ├─ Qdrant (vector store)
    └─ Ollama (LLM & Embedding)
```

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available
- NVIDIA GPU (optional, for better performance with Ollama)
- KAMCO OpenAPI service key

## Setup Steps

### 1. Clone and Configure

```bash
# Navigate to project directory
cd kamco_gradio_collector

# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

Update the following in `.env`:
```env
KAMCO_SERVICE_KEY=your_actual_service_key_here
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=your_secure_password
```

### 2. Start Services with Docker

```bash
# Start all services (MongoDB, Qdrant, Ollama, MCP Server)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f mcp-server
```

### 3. Pull Ollama Model

```bash
# Enter Ollama container
docker exec -it kamco-ollama ollama pull qwen2.5:latest

# Verify model is downloaded
docker exec -it kamco-ollama ollama list
```

### 4. Collect and Process Data

```bash
# Enter MCP server container
docker exec -it kamco-mcp-server bash

# Run data collection and RAG processing
python -m rag.manager

# Or manually:
python -m services.kamco_collector_service  # Collect data
python -m normalize.kamco_normalizer        # Normalize data
python -m rag.embed                         # Embed into vector DB
```

### 5. Configure ChatGPT Desktop for MCP

#### For macOS/Linux

Create or edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kamco": {
      "command": "docker",
      "args": [
        "compose",
        "-f",
        "/full/path/to/kamco_gradio_collector/docker-compose.yml",
        "run",
        "--rm",
        "mcp-server"
      ]
    }
  }
}
```

#### For ChatGPT Desktop (if supporting MCP)

The configuration file location may vary. Typically:
- Windows: `%APPDATA%\OpenAI\ChatGPT\config.json`
- macOS: `~/Library/Application Support/OpenAI/ChatGPT/config.json`

Use the same `mcp_config.json` format:

```json
{
  "mcpServers": {
    "kamco": {
      "command": "docker",
      "args": [
        "compose",
        "-f",
        "/Users/hyun/workspace/kamco_gradio_collector/docker-compose.yml",
        "run",
        "--rm",
        "mcp-server"
      ]
    }
  }
}
```

### 6. Alternative: Run MCP Server Directly (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Start MongoDB and Qdrant separately
docker-compose up -d mongodb qdrant ollama

# Run MCP server
python -m mcp_server.server
```

## Available MCP Tools

Once connected, ChatGPT can use these tools:

1. **search_kamco** - Search auction data by natural language query
   - Example: "서울 아파트"
   
2. **get_kamco_by_id** - Get details of specific auction item
   - Example: item_id "2024-12345"
   
3. **get_recent_kamco** - Get recently collected listings
   
4. **ask_kamco** - Ask questions with RAG-generated answers
   - Example: "서울에 있는 저렴한 아파트를 추천해줘"
   
5. **collect_kamco_data** - Trigger new data collection
   
6. **embed_kamco_data** - Process and embed data for RAG

## Testing the MCP Server

### Test with stdio (manual testing)

```bash
# Run the server and test manually
python -m mcp_server.server

# The server will wait for JSON-RPC messages on stdin
# You can send test messages like:
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | python -m mcp_server.server
```

### Test with Docker

```bash
# Check if server starts correctly
docker-compose up mcp-server

# View server logs
docker-compose logs -f mcp-server
```

## Troubleshooting

### MongoDB Connection Issues

```bash
# Check MongoDB is running
docker-compose ps mongodb

# Test connection
docker exec -it kamco-mongodb mongosh -u admin -p password
```

### Qdrant Connection Issues

```bash
# Check Qdrant is running
docker-compose ps qdrant

# Access Qdrant dashboard
open http://localhost:6333/dashboard
```

### Ollama Model Issues

```bash
# Check Ollama is running
docker exec -it kamco-ollama ollama list

# Pull model again if needed
docker exec -it kamco-ollama ollama pull qwen2.5:latest
```

### MCP Server Not Starting

```bash
# Check logs
docker-compose logs mcp-server

# Restart the server
docker-compose restart mcp-server

# Rebuild if code changed
docker-compose build mcp-server
docker-compose up -d mcp-server
```

## Updating

```bash
# Pull latest code
git pull

# Rebuild and restart services
docker-compose build
docker-compose down
docker-compose up -d
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## Performance Tips

1. **GPU Acceleration**: Ensure Ollama can access GPU for faster embedding
2. **Memory**: Allocate at least 8GB RAM to Docker
3. **Storage**: Vector database can grow large; ensure sufficient disk space
4. **Batch Processing**: Collect data in batches to avoid API rate limits

## Security Notes

- Never commit `.env` file with real credentials
- Use strong passwords for MongoDB
- Limit network exposure in production
- Use environment-specific configurations

## Next Steps

1. Collect initial data: `docker exec -it kamco-mcp-server python -m rag.manager`
2. Verify data in MongoDB: `docker exec -it kamco-mongodb mongosh`
3. Test RAG search: Use the `search_kamco` tool through ChatGPT
4. Set up scheduled data collection with cron or systemd

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Verify service health: `docker-compose ps`
3. Review this documentation
4. Check KAMCO API status

## References

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [KAMCO OpenAPI](https://www.onbid.co.kr/)
