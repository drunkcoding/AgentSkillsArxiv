# Resources API

Resources are external knowledge agents can reference.

## Supported Formats

| Format | Extensions | Processing |
|--------|------------|------------|
| PDF | `.pdf` | Text and image extraction |
| Markdown | `.md` | Native support |
| HTML | `.html`, `.htm` | Cleaned text extraction |
| Plain Text | `.txt` | Direct import |
| JSON/YAML | `.json`, `.yaml`, `.yml` | Structured parsing |
| Code | `.py`, `.js`, `.ts`, `.go`, `.java`, etc. | Syntax-aware parsing |
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp` | VLM description |
| Video | `.mp4`, `.mov`, `.avi` | Frame extraction + VLM |
| Audio | `.mp3`, `.wav`, `.m4a` | Transcription |
| Documents | `.docx` | Text extraction |

## Processing Pipeline

```
Input → Parser → TreeBuilder → AGFS → SemanticQueue → Vector Index
```

## add_resource()

```python
def add_resource(
    self,
    path: str,
    target: Optional[str] = None,
    reason: str = "",
    instruction: str = "",
    wait: bool = False,
    timeout: float = None,
) -> Dict[str, Any]
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| path | str | Yes | - | Local file path, directory path, or URL |
| target | str | No | None | Target Viking URI (must be in `resources` scope) |
| reason | str | No | "" | Why this resource is being added (improves search relevance) |
| instruction | str | No | "" | Special processing instructions |
| wait | bool | No | False | Wait for semantic processing to complete |

Returns:
```python
{
    "status": "success",
    "root_uri": "viking://resources/docs/",
    "source_path": "./docs/",
    "errors": [],
    "queue_status": {...}  # only when wait=True
}
```

### Examples

```python
# Single file
result = client.add_resource("./documents/guide.md", reason="User guide documentation")

# From URL
result = client.add_resource(
    "https://example.com/api-docs.md",
    target="viking://resources/external/",
    reason="External API documentation"
)

# Wait inline
result = client.add_resource("./documents/guide.md", wait=True)

# Batch then wait
client.add_resource("./file1.md")
client.add_resource("./file2.md")
status = client.wait_processed()
```

## export_ovpack()

Export a resource tree as `.ovpack` file.

```python
def export_ovpack(self, uri: str, to: str) -> str
```

## import_ovpack()

Import a `.ovpack` file.

```python
def import_ovpack(self, file_path: str, parent: str, force: bool = False, vectorize: bool = True) -> str
```

## Managing Resources

### List

```python
entries = client.ls("viking://resources/")
paths = client.ls("viking://resources/", simple=True)  # names only
all_entries = client.ls("viking://resources/", recursive=True)
```

### Read Content (Progressive)

```python
abstract = client.abstract("viking://resources/docs/")   # L0
overview = client.overview("viking://resources/docs/")    # L1
content = client.read("viking://resources/docs/api.md")   # L2
```

### Move / Delete

```python
client.mv("viking://resources/old/", "viking://resources/new/")
client.rm("viking://resources/docs/old.md")
client.rm("viking://resources/old-project/", recursive=True)
```

### Links & Relations

```python
client.link("viking://resources/docs/auth/", "viking://resources/docs/security/", reason="Security best practices")
client.link("viking://resources/docs/api/", ["viking://resources/docs/auth/", "viking://resources/docs/errors/"], reason="Related docs")
relations = client.relations("viking://resources/docs/auth/")
client.unlink("viking://resources/docs/auth/", "viking://resources/docs/security/")
```

## Best Practices

Organize by project:
```
viking://resources/
├── project-a/
│   ├── docs/
│   ├── specs/
│   └── references/
├── project-b/
└── shared/
    └── common-docs/
```
