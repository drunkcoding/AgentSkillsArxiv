# OpenViking Quickstart

## Prerequisites

- Python 3.9+
- Stable network connection

## Installation

```bash
pip install openviking
```

## Model Requirements

- **VLM Model**: For image/content understanding (e.g., `doubao-seed-1-8-251228` or `gpt-4-vision-preview`)
- **Embedding Model**: For vectorization and semantic retrieval (e.g., `doubao-embedding-vision-250615` or `text-embedding-3-large`)

## Configuration

Create `ov.conf`:

```json
{
  "embedding": {
    "dense": {
      "api_base": "<api-endpoint>",
      "api_key": "<your-api-key>",
      "backend": "<backend-type>",
      "dimension": 1024,
      "model": "<model-name>"
    }
  },
  "vlm": {
    "api_base": "<api-endpoint>",
    "api_key": "<your-api-key>",
    "backend": "<backend-type>",
    "model": "<model-name>"
  }
}
```

### Volcengine Example

```json
{
  "embedding": {
    "dense": {
      "api_base": "https://ark.cn-beijing.volces.com/api/v3",
      "api_key": "your-volcengine-api-key",
      "backend": "volcengine",
      "dimension": 1024,
      "model": "doubao-embedding-vision-250615"
    }
  },
  "vlm": {
    "api_base": "https://ark.cn-beijing.volces.com/api/v3",
    "api_key": "your-volcengine-api-key",
    "backend": "volcengine",
    "model": "doubao-seed-1-8-251228"
  }
}
```

### OpenAI Example

```json
{
  "embedding": {
    "dense": {
      "api_base": "https://api.openai.com/v1",
      "api_key": "your-openai-api-key",
      "backend": "openai",
      "dimension": 3072,
      "model": "text-embedding-3-large"
    }
  },
  "vlm": {
    "api_base": "https://api.openai.com/v1",
    "api_key": "your-openai-api-key",
    "backend": "openai",
    "model": "gpt-4-vision-preview"
  }
}
```

Set environment variable:

```bash
export OPENVIKING_CONFIG_FILE=ov.conf
```

## First Example

```python
import openviking as ov

client = ov.OpenViking(path="./data")
try:
    client.initialize()

    # Add resource (URL, file, or directory)
    add_result = client.add_resource(
        path="https://raw.githubusercontent.com/volcengine/OpenViking/refs/heads/main/README.md"
    )
    root_uri = add_result['root_uri']

    # Explore tree structure
    ls_result = client.ls(root_uri)
    print(f"Directory structure:\n{ls_result}\n")

    # Find markdown files
    glob_result = client.glob(pattern="**/*.md", uri=root_uri)
    if glob_result['matches']:
        content = client.read(glob_result['matches'][0])
        print(f"Content preview: {content[:200]}...\n")

    # Wait for semantic processing
    print("Wait for semantic processing...")
    client.wait_processed()

    # Get abstract and overview
    abstract = client.abstract(root_uri)
    overview = client.overview(root_uri)
    print(f"Abstract:\n{abstract}\n\nOverview:\n{overview}\n")

    # Semantic search
    results = client.find("what is openviking", target_uri=root_uri)
    print("Search results:")
    for r in results.resources:
        print(f"  {r.uri} (score: {r.score:.4f})")

    client.close()
except Exception as e:
    print(f"Error: {e}")
```
