# Configuration Reference

## Configuration File

Create `ov.conf` in project directory:

```json
{
  "embedding": {
    "dense": {
      "backend": "volcengine",
      "api_key": "your-api-key",
      "model": "doubao-embedding-vision-250615",
      "dimension": 1024,
      "input": "multimodal"
    }
  },
  "vlm": {
    "api_key": "your-api-key",
    "model": "doubao-seed-1-8-251228",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3"
  },
  "rerank": {
    "backend": "volcengine",
    "api_key": "your-api-key",
    "model": "doubao-rerank-250615"
  },
  "storage": {
    "agfs": {
      "backend": "local",
      "path": "./data",
      "timeout": 30.0
    },
    "vectordb": {
      "backend": "local",
      "path": "./data"
    }
  },
  "user": "string"
}
```

## Configuration Sections

### embedding

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| backend | string | Yes | `"volcengine"`, `"openai"`, or `"vikingdb"` |
| api_key | string | Yes | API key |
| model | string | Yes | Model ID |
| api_base | string | No | API endpoint |
| dimension | int | Yes | Vector dimension (usually 1024 or 768) |
| input | string | No | `"multimodal"` (default) or `"text"` |

Supports Dense, Sparse, and Hybrid embedding modes.

### vlm

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| backend | string | Yes | `"volcengine"` or `"openai"` |
| api_key | string | Yes | API key |
| model | string | Yes | Model ID |
| api_base | string | No | API endpoint |
| temperature | float | No | Generation temperature (0-1), recommended 0.1 |
| max_retries | int | No | Retries on failure, recommended 3 |

### rerank (optional)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| backend | string | Yes | `"volcengine"` |
| api_key | string | Yes | API key |
| model | string | Yes | `"doubao-rerank-250615"` |

### storage

AGFS backends: `local` (path), `remote` (url).
VectorDB backends: `local` (path), `remote` (url).

## Environment Variables

```bash
export VOLCENGINE_API_KEY="your-api-key"
export OPENVIKING_DATA_PATH="./data"
export OPENVIKING_CONFIG_FILE=ov.conf
```

## Configuration Priority

1. Constructor parameters (highest)
2. Config object
3. Configuration file (`ov.conf`)
4. Environment variables
5. Default values (lowest)

## Programmatic Configuration

```python
from openviking.utils.config import (
    OpenVikingConfig, StorageConfig, AGFSConfig,
    VectorDBBackendConfig, EmbeddingConfig, DenseEmbeddingConfig
)
config = OpenVikingConfig(
    storage=StorageConfig(
        agfs=AGFSConfig(backend="local", path="./custom_data"),
        vectordb=VectorDBBackendConfig(backend="local", path="./custom_data")
    ),
    embedding=EmbeddingConfig(
        dense=DenseEmbeddingConfig(
            backend="volcengine", api_key="your-api-key",
            model="doubao-embedding-vision-250615", dimension=1024
        )
    )
)
client = ov.OpenViking(config=config)
```

## Model Providers

### Volcengine (Recommended)

| Model | ID | Purpose |
|-------|----|---------|
| Doubao-Seed-1.8 | `doubao-seed-1-8-251228` | VLM |
| Doubao-Embedding-Vision | `doubao-embedding-vision-250615` | Embedding |
| Doubao-Rerank | `doubao-rerank-250615` | Rerank |

Regional endpoints:
- Beijing: `https://ark.cn-beijing.volces.com/api/v3`
- Shanghai: `https://ark.cn-shanghai.volces.com/api/v3`

### OpenAI

| Model | Purpose |
|-------|---------|
| `gpt-4-vision-preview` | VLM |
| `text-embedding-3-large` (dim 3072) | Embedding |

## Troubleshooting

- **Invalid API Key**: Check complete string starting with `sk-`, not deleted/expired
- **Model Not Activated**: Check model status in console, ensure "Running"
- **Connection Timeout**: Check network, verify `api_base`, increase timeout
- **Resources not indexed**: Call `wait_processed()`, check embedding config, verify file format
- **Search no results**: Confirm resources processed via `ls()`, check `target_uri`, try different queries
- **Memory extraction failing**: Ensure `commit()` called, check VLM config, conversation must have extractable info
