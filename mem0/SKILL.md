---
name: mem0
description: >
  Persistent memory layer for AI agents using mem0 (mem0ai/mem0). Use this skill when
  users want to: (1) add persistent memory to AI applications or chatbots, (2) store,
  search, update, or delete memories from conversations, (3) set up mem0 with various
  LLM/embedding/vector store backends, (4) build memory-augmented agents that remember
  user preferences and context across sessions. Triggers on mentions of "mem0", "memory
  layer", "persistent memory for AI", "remember user preferences", or building chatbots
  that need long-term memory.
---

# mem0 - Memory Layer for AI

mem0 extracts facts from conversations via LLM, stores them as vector embeddings, and retrieves semantically relevant memories on subsequent queries.

## Installation

```bash
pip install mem0ai
```

Default setup requires `OPENAI_API_KEY` (uses OpenAI for LLM + embeddings, Qdrant local for vector store).

For alternative provider setups, see [references/configuration.md](references/configuration.md).

## Quick Start

```python
from mem0 import Memory

memory = Memory()

# Store memories from conversation
memory.add(
    [{"role": "user", "content": "I'm a backend engineer who prefers Python and uses vim"}],
    user_id="alice"
)

# Search memories
results = memory.search("what editor does she use", user_id="alice")
for r in results["results"]:
    print(f"{r['memory']} (score: {r['score']:.2f})")

# Store raw text (no LLM extraction)
memory.add("Prefers dark mode in all editors", user_id="alice", infer=False)
```

## Core Operations

All operations require at least one of: `user_id`, `agent_id`, or `run_id`.

### Add Memories

```python
# From conversation messages
memory.add(messages, user_id="u1")

# From plain string
memory.add("Fact to remember", user_id="u1")

# Skip LLM fact extraction, store verbatim
memory.add("Raw data", user_id="u1", infer=False)

# With custom metadata
memory.add(messages, user_id="u1", metadata={"source": "onboarding"})

# Procedural memory (requires agent_id)
memory.add(messages, agent_id="deploy-bot", memory_type="procedural_memory")
```

`add()` returns `{"results": [{"id": "...", "memory": "...", "event": "ADD|UPDATE|NONE"}]}`.

### Search Memories

```python
results = memory.search("query", user_id="u1", limit=5)
# Optional: threshold=0.7 to filter low-relevance results

for r in results["results"]:
    print(r["id"], r["memory"], r["score"])
```

### Get, Update, Delete

```python
# Get all memories for a user
all_mems = memory.get_all(user_id="u1")

# Get specific memory
mem = memory.get("memory-uuid")

# Update
memory.update("memory-uuid", "Updated fact text")

# Delete one
memory.delete("memory-uuid")

# Delete all for user
memory.delete_all(user_id="u1")

# View change history
memory.history("memory-uuid")

# Full reset
memory.reset()
```

## Integration Pattern: Chat with Memory

```python
from openai import OpenAI
from mem0 import Memory

client = OpenAI()
memory = Memory()

def chat(message: str, user_id: str) -> str:
    # Retrieve relevant memories
    mems = memory.search(message, user_id=user_id, limit=3)
    context = "\n".join(f"- {m['memory']}" for m in mems["results"])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are helpful. User context:\n{context}"},
            {"role": "user", "content": message},
        ],
    )
    reply = response.choices[0].message.content

    # Store the conversation as new memories
    memory.add(
        [{"role": "user", "content": message}, {"role": "assistant", "content": reply}],
        user_id=user_id,
    )
    return reply
```

## Custom Configuration

Pass a config dict or `MemoryConfig` object:

```python
from mem0 import Memory

config = {
    "llm": {
        "provider": "openai",
        "config": {"model": "gpt-4o-mini", "temperature": 0.1},
    },
    "embedder": {
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {"collection_name": "my_memories", "path": "/tmp/qdrant"},
    },
}
memory = Memory.from_config(config)
```

For all provider options (17 LLMs, 11 embedders, 24 vector stores, graph stores, rerankers), see [references/configuration.md](references/configuration.md).

## Custom Prompts

Override fact extraction or memory update logic:

```python
config = {
    "custom_fact_extraction_prompt": "Extract technical decisions from: {messages}",
    "custom_update_memory_prompt": "Your custom update rules...",
}
memory = Memory.from_config(config)
```

## Async Usage

```python
from mem0 import AsyncMemory

memory = AsyncMemory()
result = await memory.add(messages, user_id="u1")
results = await memory.search("query", user_id="u1")
```

## Hosted Platform (MemoryClient)

For the managed API at `api.mem0.ai` (requires API key from `app.mem0.ai`):

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-key")  # or set MEM0_API_KEY env var
client.add(messages, user_id="u1")
results = client.search("query", user_id="u1")
```

Same methods as `Memory`, but runs on mem0's hosted infrastructure.

## Memory Scoping Guide

| Scope | Use Case |
|-------|----------|
| `user_id` | Per-user preferences and facts |
| `agent_id` | Agent-specific knowledge and procedures |
| `run_id` | Session-scoped temporary context |
| Combined | Multi-dimensional (e.g., user + agent) |

## Response Format

All operations return `{"results": [...]}`. Each memory item:

```python
{
    "id": "uuid",
    "memory": "The extracted fact",
    "score": 0.85,          # search only
    "metadata": {},
    "created_at": "ISO-ts",
    "updated_at": "ISO-ts",
    "user_id": "...",
}
```
