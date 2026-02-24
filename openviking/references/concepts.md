# OpenViking Concepts

## Table of Contents
- [Architecture](#architecture)
- [Context Types](#context-types)
- [Viking URI](#viking-uri)
- [Context Layers (L0/L1/L2)](#context-layers)
- [Storage Architecture](#storage-architecture)
- [Retrieval Mechanism](#retrieval-mechanism)
- [Context Extraction](#context-extraction)
- [Session Management](#session-management)

## Architecture

OpenViking unifies all context types (Memory, Resource, Skill) into a directory structure with semantic retrieval and progressive content loading.

### Core Modules

| Module | Responsibility |
|--------|---------------|
| **Client** | Unified entry, coordinates modules |
| **Retrieve** | Intent analysis, hierarchical retrieval, rerank |
| **Session** | Message recording, usage tracking, memory commit |
| **Parse** | Document parsing, tree building, async semantic generation |
| **Compressor** | 6-category memory extraction, LLM deduplication |
| **Storage** | VikingFS virtual filesystem, vector index, AGFS |

### Dual-Layer Storage

| Layer | Content |
|-------|---------|
| **AGFS** | L0/L1/L2 full content, multimedia, relations |
| **Vector Index** | URIs, vectors, metadata (no file content) |

### Data Flows

**Adding Context**: `Input → Parser → TreeBuilder → AGFS → SemanticQueue → Vector Index`
**Retrieving Context**: `Query → Intent Analysis → Hierarchical Retrieval → Rerank → Results`
**Session Commit**: `Messages → Compress → Archive → Memory Extraction → Storage`

## Context Types

| Type | Purpose | Lifecycle | Initiative |
|------|---------|-----------|------------|
| **Resource** | Knowledge and rules | Long-term, static | User adds |
| **Memory** | Agent's cognition | Long-term, dynamic | Agent records |
| **Skill** | Callable capabilities | Long-term, static | Agent invokes |

### Memory: 6 Categories

| Category | Location | Description | Update Strategy |
|----------|----------|-------------|-----------------|
| profile | `user/memories/.overview.md` | User basic info | Appendable |
| preferences | `user/memories/preferences/` | User preferences by topic | Appendable |
| entities | `user/memories/entities/` | Entity memories (people, projects) | Appendable |
| events | `user/memories/events/` | Event records | No update |
| cases | `agent/memories/cases/` | Learned cases | No update |
| patterns | `agent/memories/patterns/` | Learned patterns | No update |

## Viking URI

Format: `viking://{scope}/{path}`

### Scopes

| Scope | Description | Lifecycle |
|-------|-------------|-----------|
| **resources** | Independent resources | Long-term |
| **user** | User-level data | Long-term |
| **agent** | Agent-level data | Long-term |
| **session** | Session-level data | Session lifetime |
| **queue** | Processing queue | Temporary |
| **temp** | Temporary files | During parsing |

### Directory Structure

```
viking://
├── resources/{project}/     # docs, code, web pages
├── user/
│   ├── .overview.md         # user profile
│   └── memories/
│       ├── preferences/
│       ├── entities/
│       └── events/
├── agent/
│   ├── skills/
│   ├── memories/
│   │   ├── cases/
│   │   └── patterns/
│   └── instructions/
└── session/{session_id}/
    ├── messages.jsonl
    ├── tools/
    └── history/
```

### Special Files

| File | Purpose |
|------|---------|
| `.abstract.md` | L0 abstract (~100 tokens) |
| `.overview.md` | L1 overview (~2k tokens) |
| `.relations.json` | Related resources |
| `.meta.json` | Metadata |

### URI Utilities

```python
from openviking.utils.uri import VikingURI
uri = VikingURI("viking://resources/docs/api")
uri.scope       # "resources"
uri.full_path   # "resources/docs/api"
uri.join("file.md").uri    # "viking://resources/docs/api/file.md"
uri.parent.uri             # "viking://resources/docs"
```

Use trailing slash for directories: `viking://resources/docs/`

## Context Layers

| Layer | File | Token Limit | Purpose |
|-------|------|-------------|---------|
| **L0** Abstract | `.abstract.md` | ~100 | Vector search, quick filtering |
| **L1** Overview | `.overview.md` | ~2k | Rerank, content navigation |
| **L2** Detail | Original files | Unlimited | Full content, on-demand |

Generation: bottom-up (leaf nodes → parent → root). Child abstracts aggregate into parent overview.

Multimodal: L0/L1 always text; L2 can be any format. Binary content described in text for L0/L1.

### Token Budget

```python
overview = client.overview(uri)
if needs_more_detail(overview):
    content = client.read(uri)
```

## Storage Architecture

```
VikingFS (URI Abstraction)
├── Vector Index (Semantic Search)
└── AGFS (Content Storage)
```

### VikingFS

URI mapping layer: `viking://resources/docs/auth → /local/resources/docs/auth`
Auto-syncs vector index on delete/move operations.

### AGFS Backends

| Backend | Config |
|---------|--------|
| `localfs` | `path` |
| `s3fs` | `bucket`, `endpoint` |
| `memory` | (testing) |

### Vector Index Schema

| Field | Type | Description |
|-------|------|-------------|
| uri | string | Resource URI |
| parent_uri | string | Parent directory URI |
| context_type | string | resource/memory/skill |
| is_leaf | bool | Whether leaf node |
| vector | vector | Dense vector |
| abstract | string | L0 abstract text |
| active_count | int64 | Usage count |

Index: `flat_hybrid`, cosine distance, int8 quantization.
Backends: `local`, `http`, `volcengine`.

## Retrieval Mechanism

### find() vs search()

| Feature | find() | search() |
|---------|--------|----------|
| Session | Not needed | Required |
| Intent analysis | Not used | LLM analysis |
| Query count | Single | 0-5 TypedQueries |
| Latency | Low | Higher |

### Intent Analysis (search only)

TypedQuery: `{query, context_type, intent, priority}`

0 queries = chitchat. Multiple queries = complex task needing skill + resource + memory.

### Hierarchical Retrieval

Priority queue recursive search:
1. Root directories by context_type (MEMORY→user/agent memories, RESOURCE→resources, SKILL→agent/skills)
2. Global vector search → starting directories
3. Recursive: `score = 0.5 * embedding + 0.5 * parent_score`
4. Convergence: stop after top-k unchanged 3 rounds

### Rerank

Trigger: rerank configured + THINKING mode. Uses `doubao-seed-rerank` (Volcengine).

## Context Extraction

```
Input File → Parser → TreeBuilder → SemanticQueue → Vector Index
```

Parser handles format conversion (no LLM). Semantic generation is async.

### Smart Splitting

- ≤1024 tokens → single file
- >1024 → split by headers
- Section <512 tokens → merge
- Section >1024 tokens → subdirectory

### SemanticQueue (Bottom-up)

Per directory: concurrent file summaries → collect child abstracts → generate L1 overview → extract L0 → write to AGFS → vectorize.

Config: `max_concurrent_llm=10`, `max_images_per_call=10`, `max_sections_per_call=20`.

## Session Management

Lifecycle: Create → Interact → Commit

### Compression

Auto-archive on commit: increment index, copy messages, generate structured summary, clear current.

### Memory Extraction Flow

```
Messages → LLM Extract → Candidate Memories → Vector Pre-filter → LLM Dedup → CREATE/UPDATE/MERGE/SKIP → AGFS → Vectorize
```
