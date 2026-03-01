# mem0 Configuration Reference

## Table of Contents

- [LLM Providers](#llm-providers)
- [Embedding Providers](#embedding-providers)
- [Vector Store Providers](#vector-store-providers)
- [Graph Store Providers](#graph-store-providers)
- [Reranker Providers](#reranker-providers)
- [Fully Local Setup](#fully-local-setup)
- [Docker Self-Hosted Server](#docker-self-hosted-server)

## LLM Providers

17 supported providers. Set via `config["llm"]`.

### OpenAI (default)

```python
"llm": {"provider": "openai", "config": {"model": "gpt-4o-mini", "temperature": 0.1, "api_key": "..."}}
```

### Anthropic

```python
"llm": {"provider": "anthropic", "config": {"model": "claude-sonnet-4-20250514", "api_key": "..."}}
```

### Ollama (local)

```python
"llm": {"provider": "ollama", "config": {"model": "llama3.1:8b", "ollama_base_url": "http://localhost:11434"}}
```

### Other providers

| Provider | Key | Required config |
|----------|-----|-----------------|
| `gemini` | `api_key` | `model` |
| `groq` | `api_key` | `model` |
| `together` | `api_key` | `model` |
| `deepseek` | `api_key` | `model` |
| `xai` | `api_key` | `model` |
| `aws_bedrock` | AWS credentials | `model`, `region` |
| `azure_openai` | `api_key` | `model`, `azure_endpoint`, `api_version` |
| `litellm` | varies | `model` |
| `sarvam` | `api_key` | `model` |
| `lmstudio` | none | `model`, `base_url` |
| `vllm` | none | `model`, `base_url` |
| `langchain` | varies | LangChain LLM object |
| `openai_structured` | `api_key` | `model` |
| `azure_openai_structured` | `api_key` | `model`, `azure_endpoint` |

## Embedding Providers

11 supported providers. Set via `config["embedder"]`.

### OpenAI (default)

```python
"embedder": {"provider": "openai", "config": {"model": "text-embedding-3-small"}}
```

Dimension: 1536

### Ollama (local)

```python
"embedder": {"provider": "ollama", "config": {"model": "nomic-embed-text"}}
```

### Other providers

| Provider | Key | Required config |
|----------|-----|-----------------|
| `huggingface` | none | `model` (e.g., `sentence-transformers/all-MiniLM-L6-v2`) |
| `azure_openai` | `api_key` | `model`, `azure_endpoint` |
| `gemini` | `api_key` | `model` |
| `vertexai` | GCP credentials | `model` |
| `together` | `api_key` | `model` |
| `lmstudio` | none | `model`, `base_url` |
| `langchain` | varies | LangChain Embeddings object |
| `aws_bedrock` | AWS credentials | `model`, `region` |
| `fastembed` | none | `model` |

**Important:** When using a non-OpenAI embedder, set `embedding_model_dims` in the vector store config to match the model's output dimension. Default is 1536 (OpenAI). Common dimensions: fastembed `BAAI/bge-small-en-v1.5` = 384, `nomic-embed-text` = 768, `all-MiniLM-L6-v2` = 384.

## Vector Store Providers

24 supported providers. Set via `config["vector_store"]`.

### Qdrant (default)

```python
"vector_store": {"provider": "qdrant", "config": {"collection_name": "mem0", "path": "/tmp/qdrant"}}
```

Runs locally, no external service needed.

### ChromaDB

```python
"vector_store": {"provider": "chroma", "config": {"collection_name": "mem0", "path": "./chroma_db"}}
```

### pgvector (PostgreSQL)

```python
"vector_store": {"provider": "pgvector", "config": {
    "dbname": "mem0", "user": "postgres", "password": "...",
    "host": "localhost", "port": 5432
}}
```

### Other providers

| Provider | Key config fields |
|----------|-------------------|
| `pinecone` | `api_key`, `index_name`, `dimension` |
| `mongodb` | `connection_string`, `db_name`, `collection_name` |
| `milvus` | `collection_name`, `uri` |
| `weaviate` | `url`, `api_key`, `collection_name` |
| `faiss` | `dimension`, `path` |
| `redis` | `redis_url`, `collection_name` |
| `elasticsearch` | `url`, `index_name` |
| `opensearch` | `host`, `port`, `index_name` |
| `azure_ai_search` | `api_key`, `service_name`, `index_name` |
| `azure_mysql` | connection params |
| `vertex_ai_vector_search` | GCP config |
| `upstash_vector` | `url`, `token` |
| `supabase` | `url`, `api_key`, `table_name` |
| `cassandra` | `keyspace`, `table_name` |
| `neptune` | `endpoint` |
| `langchain` | LangChain VectorStore object |
| `s3_vectors` | AWS config, `bucket_name` |
| `databricks` | `endpoint`, `index_name` |
| `valkey` | `url`, `collection_name` |
| `baidu` | `api_key`, `account` |

## Graph Store Providers

Optional. Extracts entity relationships alongside vector memories. Set via `config["graph_store"]`.

### Neo4j

```python
"graph_store": {"provider": "neo4j", "config": {
    "url": "bolt://localhost:7687", "username": "neo4j", "password": "password"
}}
```

### Other providers

| Provider | Key config |
|----------|-----------|
| `memgraph` | `url`, `username`, `password` |
| `neptune` | `endpoint` |
| `kuzu` | `db_path` |

Install graph support: `pip install mem0ai[graph]`

## Reranker Providers

Optional. Improves search relevance. Set via `config["reranker"]`.

| Provider | Key config |
|----------|-----------|
| `cohere` | `api_key`, `model` (e.g., `rerank-english-v3.0`) |
| `sentence_transformer` | `model` |
| `zero_entropy` | `api_key`, `model` |
| `llm` | Uses configured LLM |
| `huggingface` | `model` |

## Fully Local Setup

Zero API keys required. Uses Ollama for LLM + embeddings, ChromaDB for storage:

```bash
# Prerequisites
pip install mem0ai chromadb
# Ollama must be running: https://ollama.ai
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

```python
from mem0 import Memory

config = {
    "llm": {
        "provider": "ollama",
        "config": {"model": "llama3.1:8b", "ollama_base_url": "http://localhost:11434"},
    },
    "embedder": {
        "provider": "ollama",
        "config": {"model": "nomic-embed-text"},
    },
    "vector_store": {
        "provider": "chroma",
        "config": {"collection_name": "mem0", "path": "./chroma_db"},
    },
}
memory = Memory.from_config(config)
```

### Alternative: fastembed + Qdrant (no Ollama needed for embeddings)

```bash
pip install mem0ai fastembed
```

```python
config = {
    "embedder": {
        "provider": "fastembed",
        "config": {"model": "BAAI/bge-small-en-v1.5"},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "mem0",
            "path": "/tmp/qdrant",
            "embedding_model_dims": 384,
        },
    },
}
```

## Docker Self-Hosted Server

REST API server with PostgreSQL/pgvector + Neo4j:

```bash
git clone https://github.com/mem0ai/mem0.git
cd mem0/server
cp .env.example .env
# Edit .env: set OPENAI_API_KEY
docker-compose up
```

Services started:
- **mem0 API**: `http://localhost:8888`
- **PostgreSQL (pgvector)**: port 8432
- **Neo4j**: port 8474 (HTTP), 8687 (Bolt)

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/memories` | Add memories |
| `GET` | `/memories?user_id=...` | Get all memories |
| `GET` | `/memories/{id}` | Get one memory |
| `POST` | `/search` | Search memories |
| `PUT` | `/memories/{id}` | Update memory |
| `DELETE` | `/memories/{id}` | Delete memory |
| `DELETE` | `/memories?user_id=...` | Delete all |
| `POST` | `/reset` | Full reset |

### Example requests

```bash
# Add
curl -X POST http://localhost:8888/memories \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "I love Python"}], "user_id": "u1"}'

# Search
curl -X POST http://localhost:8888/search \
  -H "Content-Type: application/json" \
  -d '{"query": "programming", "user_id": "u1"}'
```
