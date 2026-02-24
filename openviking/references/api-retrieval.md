# Retrieval API

Two search methods: `find` (simple) and `search` (complex with session context).

## find vs search

| Aspect | find | search |
|--------|------|--------|
| Intent Analysis | No | Yes (LLM) |
| Session Context | No | Yes |
| Query Expansion | No | Yes |
| Query Count | Single | 0-5 TypedQueries |
| Default Limit | 10 | 3 |
| Latency | Low | Higher |
| Use Case | Simple queries | Conversational search |

## find()

Basic vector similarity search.

```python
def find(
    self,
    query: str,
    target_uri: str = "",
    limit: int = 10,
    score_threshold: Optional[float] = None,
    filter: Optional[Dict] = None,
) -> FindResult
```

### FindResult Structure

```python
class FindResult:
    memories: List[MatchedContext]
    resources: List[MatchedContext]
    skills: List[MatchedContext]
    query_plan: Optional[QueryPlan]           # search only
    query_results: Optional[List[QueryResult]]
    total: int                                # auto-calculated
```

### MatchedContext Structure

```python
class MatchedContext:
    uri: str
    context_type: ContextType    # "resource", "memory", "skill"
    is_leaf: bool
    abstract: str                # L0 content
    category: str
    score: float                 # 0-1
    match_reason: str
    relations: List[RelatedContext]
```

### Examples

```python
# Basic search
results = client.find("how to authenticate users")
for ctx in results.resources:
    print(f"URI: {ctx.uri}, Score: {ctx.score:.3f}")

# Scoped to resources
results = client.find("authentication", target_uri="viking://resources/")

# Scoped to user memories
results = client.find("preferences", target_uri="viking://user/memories/")

# Scoped to skills
results = client.find("web search", target_uri="viking://agent/skills/")

# Scoped to specific project
results = client.find("API endpoints", target_uri="viking://resources/my-project/")
```

## search()

Search with session context and intent analysis.

```python
def search(
    self,
    query: str,
    target_uri: str = "",
    session: Optional[Session] = None,
    limit: int = 3,
    score_threshold: Optional[float] = None,
    filter: Optional[Dict] = None,
) -> FindResult
```

### Examples

```python
# Session-aware search
session = client.session()
session.add_message("user", [TextPart(text="I'm building a login page with OAuth")])
results = client.search("best practices", session=session)

# Without session (still does intent analysis)
results = client.search("how to implement OAuth 2.0 authorization code flow")
```

## Retrieval Pipeline

```
Query → Intent Analysis → Vector Search (L0) → Rerank (L1) → Results
```

### Intent Analysis (search only)

Generates 0-5 TypedQueries:
```python
@dataclass
class TypedQuery:
    query: str                  # Rewritten query
    context_type: ContextType   # MEMORY/RESOURCE/SKILL
    intent: str                 # Query purpose
    priority: int               # 1-5
```

Query styles by type:
- **skill**: Verb-first ("Create RFC document")
- **resource**: Noun phrase ("RFC document template")
- **memory**: "User's XX" ("User's code style preferences")

### Hierarchical Retrieval

Directory recursive search using priority queue:
1. Determine root directories by context_type
2. Global vector search to locate starting directories
3. Merge starting points + Rerank scoring
4. Recursive search with score propagation: `final_score = 0.5 * embedding_score + 0.5 * parent_score`
5. Convergence detection (stops after top-k unchanged for 3 rounds)

Key parameters:
- `SCORE_PROPAGATION_ALPHA`: 0.5
- `MAX_CONVERGENCE_ROUNDS`: 3
- `GLOBAL_SEARCH_TOPK`: 3

## Working with Results

### Progressive Content Loading

```python
results = client.find("authentication")
for ctx in results.resources:
    print(f"Abstract: {ctx.abstract}")       # L0 already in result
    if not ctx.is_leaf:
        overview = client.overview(ctx.uri)   # L1
    else:
        content = client.read(ctx.uri)        # L2

# Get related resources
relations = client.relations(ctx.uri)
```

## Best Practices

- Use specific queries ("OAuth 2.0 authorization code flow" > "auth")
- Scope searches with `target_uri`
- Use session context for conversational search
- Know what you want → `find()`, complex task → `search()`
