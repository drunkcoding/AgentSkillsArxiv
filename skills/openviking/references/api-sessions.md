# Sessions API

Sessions manage conversation state, track context usage, and extract long-term memories.

## client.session()

```python
def session(self, session_id: Optional[str] = None) -> Session
```

Creates new or loads existing session. Auto-generates ID if None.

```python
session = client.session()                          # new
session = client.session(session_id="abc123")       # existing
session.load()                                      # load data
```

## Session.add_message()

```python
def add_message(self, role: str, parts: List[Part]) -> Message
```

### Part Types

```python
from openviking.message import TextPart, ContextPart, ToolPart

TextPart(text="Hello, how can I help?")

ContextPart(
    uri="viking://resources/docs/auth/",
    context_type="resource",    # "resource", "memory", or "skill"
    abstract="Authentication guide..."
)

ToolPart(
    tool_id="call_123",
    tool_name="search_web",
    skill_uri="viking://skills/search-web/",
    tool_input={"query": "OAuth best practices"},
    tool_output="",
    tool_status="pending"  # "pending", "running", "completed", "error"
)
```

### Examples

```python
# Text message
session.add_message("user", [TextPart(text="How do I authenticate users?")])
session.add_message("assistant", [TextPart(text="You can use OAuth 2.0...")])

# With context reference
session.add_message("assistant", [
    TextPart(text="Based on the documentation..."),
    ContextPart(uri="viking://resources/docs/auth/", context_type="resource", abstract="Auth guide...")
])

# With tool call
msg = session.add_message("assistant", [
    TextPart(text="Let me search for that..."),
    ToolPart(tool_id="call_123", tool_name="search_web", skill_uri="viking://skills/search-web/",
             tool_input={"query": "OAuth best practices"}, tool_status="pending")
])
```

## Session.used()

Track which contexts/skills were actually used.

```python
def used(self, contexts: Optional[List[str]] = None, skill: Optional[Dict[str, Any]] = None) -> None
```

```python
session.used(contexts=["viking://resources/auth-docs/"])
session.used(skill={
    "uri": "viking://skills/code-search/",
    "input": "search for auth examples",
    "output": "Found 3 example files",
    "success": True
})
```

## Session.update_tool_part()

```python
def update_tool_part(self, message_id: str, tool_id: str, output: str, status: str = "completed") -> None
```

## Session.commit()

Archive messages and extract long-term memories.

```python
def commit(self) -> Dict[str, Any]
```

Returns:
```python
{
    "session_id": "abc123",
    "status": "committed",
    "memories_extracted": 3,
    "active_count_updated": 5,
    "archived": True,
    "stats": {"total_turns": 10, "contexts_used": 4, "skills_used": 2, "memories_extracted": 3}
}
```

**What happens on commit**: Archive messages to `history/archive_N/`, extract memories via LLM, deduplicate against existing, create relations, update statistics.

### Memory Categories

| Category | Location | Description |
|----------|----------|-------------|
| profile | `user/memories/.overview.md` | User profile |
| preferences | `user/memories/preferences/` | User preferences by topic |
| entities | `user/memories/entities/` | Entity memories (people, projects) |
| events | `user/memories/events/` | Event records |
| cases | `agent/memories/cases/` | Problem-solution cases |
| patterns | `agent/memories/patterns/` | Interaction patterns |

## Session.load()

```python
def load(self) -> None
```

## Session.get_context_for_search()

```python
def get_context_for_search(self, query: str, max_archives: int = 3, max_messages: int = 20) -> Dict[str, Any]
# Returns: {"summaries": [...], "recent_messages": [...]}
```

## Session Properties

| Property | Type | Description |
|----------|------|-------------|
| uri | str | `viking://session/{session_id}/` |
| messages | List[Message] | Current messages |
| stats | SessionStats | Session statistics |
| summary | str | Compression summary |
| usage_records | List[Usage] | Context/skill usage records |

## Session Storage Structure

```
viking://session/{session_id}/
├── .abstract.md
├── .overview.md
├── messages.jsonl
├── tools/{tool_id}/tool.json
├── .meta.json
├── .relations.json
└── history/
    ├── archive_001/
    │   ├── messages.jsonl
    │   ├── .abstract.md
    │   └── .overview.md
    └── archive_002/
```

## Full Example

```python
import openviking as ov
from openviking.message import TextPart, ContextPart, ToolPart

client = ov.OpenViking(path="./my_data")
client.initialize()

session = client.session()
session.add_message("user", [TextPart(text="How do I configure embedding?")])
results = client.search("embedding configuration", session=session)
session.add_message("assistant", [
    TextPart(text="Based on the documentation..."),
    ContextPart(uri=results.resources[0].uri, context_type="resource", abstract=results.resources[0].abstract)
])
session.used(contexts=[results.resources[0].uri])
result = session.commit()
client.close()
```
