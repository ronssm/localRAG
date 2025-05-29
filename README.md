# Local RAG System

A locally hosted Retrieval-Augmented Generation (RAG) system with chat capabilities and knowledge base management.

## Overview

This project implements a local RAG system with the following components:

- **Frontend**: Next.js web interface for chat and document embedding
- **Proxy**: FastAPI service handling API requests and routing
- **RAG API**: Backend service for embeddings and vector search
- **ChromaDB**: Vector database for document storage
- **Ollama**: Local LLM service

## Architecture

```
Frontend (Next.js)
       │
       ▼
    Proxy (FastAPI)
       │
       ├─────────────┐
       ▼             ▼
RAG API (FastAPI)  Ollama (LLM)
       │
       ▼
   ChromaDB
```

The system consists of:

1. A Next.js frontend for user interactions
2. A FastAPI proxy that routes requests to appropriate services
3. A RAG API service that handles embeddings and vector search
4. An Ollama instance for local LLM inference
5. A ChromaDB instance for vector storage

## Features

- Chat interface with context-aware responses
- Document embedding for knowledge base expansion
- Local LLM integration via Ollama
- Vector search using ChromaDB
- Modern web interface with responsive design

## Prerequisites

- Docker and Docker Compose
- Git
- 8GB RAM minimum
- 20GB disk space

## Quick Start

1. Clone the repository:

```bash
git clone <repository-url>
cd localRAG
```

2. Start the services:

```bash
docker compose up -d
```

3. Download required models:

```bash
# Access the Ollama container
docker compose exec ollama bash

# Download the default model (e.g., llama2)
ollama pull llama2

# Exit the container
exit
```

4. Access the web interface:

```
http://localhost:3000
```

## Project Structure

```
localRAG/
├── frontend/         # Next.js web application
├── proxy/           # FastAPI proxy service
├── api-rag/         # RAG backend service
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Proxy Service (port 5050)

- `POST /api/chat` - Chat with context
- `POST /api/embeddings` - Add documents to knowledge base

### RAG API (port 8080)

- `POST /query` - Vector search
- `POST /embeddings` - Document embedding

## Development

### Local Setup

1. Install dependencies:

```bash
# Frontend
cd frontend && npm install

# Proxy
cd proxy && pip install -r requirements.txt
```

2. Run in development mode:

```bash
docker compose up -d chromadb ollama
npm run dev   # Frontend
uvicorn main:app --reload  # Proxy
```

### Environment Variables

- `PROXY_URL`: Proxy service URL (default: http://proxy:5050)
- `RAG_API_URL`: RAG API URL (default: http://api-rag:8080)
- `OLLAMA_URL`: Ollama service URL (default: http://ollama:11434)

## Model Management

### Required Models

The system requires the following Ollama models:

- `gemma:2b`: Used as the default LLM for chat interactions (lightweight model optimized for CPU)
- `nomic-embed-text`: Used for generating text embeddings in the RAG system

### Installing Models

Install the required models:

```bash
# Download the chat model
docker compose exec ollama ollama pull gemma:2b

# Download the embeddings model
docker compose exec ollama ollama pull nomic-embed-text
```

List installed models:

```bash
docker compose exec ollama ollama list
```

### Managing Models

Remove a model if needed:

```bash
docker compose exec ollama ollama rm <model-name>
```

Note: Models are downloaded and stored within the Ollama container. The total storage required is approximately:

- gemma:2b: ~2.5GB
- nomic-embed-text: ~1.5GB

Make sure you have at least 4GB of free disk space for the models.
