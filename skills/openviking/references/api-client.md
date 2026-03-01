# Client API

The OpenViking client is the main entry point for all operations.

## Deployment Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Embedded** | Local storage, singleton instance | Development, small apps |
| **Service** | Remote storage, multiple instances | Production, multi-process |

## OpenViking()

```python
def __init__(
    self,
    path: Optional[str] = None,
    vectordb_url: Optional[str] = None,
    agfs_url: Optional[str] = None,
    user: Optional[str] = None,
    config: Optional[OpenVikingConfig] = None,
    **kwargs,
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| path | str | No* | None | Local storage path (embedded mode) |
| vectordb_url | str | No* | None | Remote VectorDB URL (service mode) |
| agfs_url | str | No* | None | Remote AGFS URL (service mode) |
| user | str | No | None | Username for session management |
| config | OpenVikingConfig | No | None | Advanced configuration object |

*Either `path` (embedded) or both `vectordb_url` and `agfs_url` (service) required.

### Embedded Mode

```python
import openviking as ov
client = ov.OpenViking(path="./my_data")
client.initialize()
results = client.find("test query")
client.close()
```

### Service Mode

```python
import openviking as ov
client = ov.OpenViking(
    vectordb_url="http://vectordb.example.com:8000",
    agfs_url="http://agfs.example.com:8001",
)
client.initialize()
client.close()
```

### Config Object

```python
from openviking.utils.config import (
    OpenVikingConfig, StorageConfig, AGFSConfig, VectorDBBackendConfig
)
config = OpenVikingConfig(
    storage=StorageConfig(
        agfs=AGFSConfig(backend="local", path="./custom_data"),
        vectordb=VectorDBBackendConfig(backend="local", path="./custom_data")
    )
)
client = ov.OpenViking(config=config)
client.initialize()
client.close()
```

## initialize()

Initialize storage and indexes. Must be called before using other methods.

```python
def initialize(self) -> None
```

## close()

Close the client and release resources.

```python
def close(self) -> None
```

## wait_processed()

Wait for all pending resource processing to complete.

```python
def wait_processed(self, timeout: float = None) -> Dict[str, Any]
```

Returns:
```python
{
    "queue_name": {
        "processed": 10,
        "error_count": 0,
        "errors": []
    }
}
```

## reset()

Reset the singleton instance (primarily for testing).

```python
@classmethod
def reset(cls) -> None
```

## observers

```python
@property
def observers(self) -> Dict[str, Any]
# Returns: {"queue": QueueObserver, "vikingdb": VikingDBObserver}
```

## Singleton Behavior

Embedded mode uses singleton; service mode creates new instances each time.

## Error Handling

```python
try:
    client.initialize()
except RuntimeError as e:
    print(f"Initialization failed: {e}")
try:
    content = client.read("viking://invalid/path/")
except FileNotFoundError:
    print("Resource not found")
```
