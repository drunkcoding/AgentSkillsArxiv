# File System API

Unix-like file system operations for managing context.

## abstract()

Read L0 abstract (~100 tokens summary). Applies to directories.

```python
def abstract(self, uri: str) -> str
```

```python
abstract = client.abstract("viking://resources/docs/")
```

## overview()

Read L1 overview (~2k tokens). Applies to directories.

```python
def overview(self, uri: str) -> str
```

## read()

Read L2 full content.

```python
def read(self, uri: str) -> str
```

```python
content = client.read("viking://resources/docs/api.md")
```

## ls()

List directory contents.

```python
def ls(self, uri: str, **kwargs) -> List[Any]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| simple | bool | False | Return only relative paths |
| recursive | bool | False | List all subdirectories recursively |

Entry structure:
```python
{"name": "docs", "size": 4096, "mode": 16877, "modTime": "2024-01-01T00:00:00Z", "isDir": True, "uri": "viking://resources/docs/", "meta": {}}
```

## tree()

Get directory tree structure. Returns flat list with `rel_path`.

```python
def tree(self, uri: str) -> List[Dict]
```

## rm()

Remove file or directory.

```python
def rm(self, uri: str, recursive: bool = False) -> None
```

## mv()

Move file or directory.

```python
def mv(self, from_uri: str, to_uri: str) -> None
```

## grep()

Search content by regex pattern.

```python
def grep(self, uri: str, pattern: str, case_insensitive: bool = False) -> Dict
```

Returns:
```python
{"matches": [{"uri": "viking://...", "line": 15, "content": "..."}], "count": 1}
```

## glob()

Match files by glob pattern.

```python
def glob(self, pattern: str, uri: str = "viking://") -> Dict
```

Returns:
```python
{"matches": ["viking://resources/docs/api.md", ...], "count": 2}
```

```python
results = client.glob("**/*.md", "viking://resources/")
results = client.glob("**/*.py", "viking://resources/")
```

## link()

Create relations between resources.

```python
def link(self, from_uri: str, uris: Any, reason: str = "") -> None
```

```python
client.link("viking://resources/docs/auth/", "viking://resources/docs/security/", reason="Security best practices")
client.link("viking://resources/docs/api/", ["viking://resources/docs/auth/", "viking://resources/docs/errors/"], reason="Related docs")
```

## relations()

```python
def relations(self, uri: str) -> List[Dict[str, Any]]
# Returns: [{"uri": "viking://...", "reason": "..."}]
```

## unlink()

```python
def unlink(self, from_uri: str, uri: str) -> None
```
