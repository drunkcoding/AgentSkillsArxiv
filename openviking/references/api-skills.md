# Skills API

Skills are callable capabilities that agents can invoke.

## add_skill()

```python
def add_skill(self, data: Any, wait: bool = False, timeout: float = None) -> Dict[str, Any]
```

### Supported Data Formats

**Dict (Skill format)**:
```python
{
    "name": "skill-name",
    "description": "Skill description",
    "content": "Full markdown content",
    "allowed_tools": ["Tool1", "Tool2"],  # optional
    "tags": ["tag1", "tag2"]              # optional
}
```

**Dict (MCP Tool format)** - auto-detected by `inputSchema` field:
```python
{
    "name": "tool_name",
    "description": "Tool description",
    "inputSchema": {
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}
```

**String (SKILL.md content)** or **Path** (file/directory).

Returns:
```python
{"status": "success", "uri": "viking://agent/skills/skill-name/", "name": "skill-name", "auxiliary_files": 0}
```

### Examples

```python
# From dict
result = client.add_skill({
    "name": "search-web",
    "description": "Search the web for current information",
    "content": "# search-web\n\nSearch the web for current information.\n\n## Parameters\n- **query** (string, required): Search query\n- **limit** (integer, optional): Max results, default 10"
})

# From MCP tool (auto-detected)
result = client.add_skill({
    "name": "calculator",
    "description": "Perform mathematical calculations",
    "inputSchema": {"type": "object", "properties": {"expression": {"type": "string", "description": "Math expression"}}, "required": ["expression"]}
})

# From file or directory
result = client.add_skill("./skills/search-web/SKILL.md")
result = client.add_skill("./skills/code-runner/")
```

## SKILL.md Format

```markdown
---
name: skill-name
description: Brief description of the skill
allowed-tools:
  - Tool1
tags:
  - tag1
---
# Skill Name
Full skill documentation in Markdown format.
```

## Managing Skills

```python
# List
skills = client.ls("viking://agent/skills/")
names = client.ls("viking://agent/skills/", simple=True)

# Read content
abstract = client.abstract("viking://agent/skills/search-web/")   # L0
overview = client.overview("viking://agent/skills/search-web/")    # L1
content = client.read("viking://agent/skills/search-web/")         # L2

# Search
results = client.find("search the internet", target_uri="viking://agent/skills/", limit=5)
for ctx in results.skills:
    print(f"Skill: {ctx.uri}, Score: {ctx.score:.3f}")

# Remove
client.rm("viking://agent/skills/old-skill/", recursive=True)
```

## Skill Storage Structure

```
viking://agent/skills/
├── search-web/
│   ├── .abstract.md       # L0
│   ├── .overview.md       # L1
│   ├── SKILL.md           # L2
│   └── [auxiliary files]
└── calculator/
    ├── .abstract.md
    ├── .overview.md
    └── SKILL.md
```

## MCP Conversion

Auto-detected when dict contains `inputSchema`. Converts name to kebab-case, extracts parameters from `inputSchema.properties`, marks required fields.
