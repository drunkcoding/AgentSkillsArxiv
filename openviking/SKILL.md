---
name: openviking
description: >
  Context database reference for OpenViking — an open-source context database for AI Agents
  that unifies memory, resources, and skills through a filesystem paradigm with hierarchical
  context delivery (L0/L1/L2) and semantic retrieval. Use this skill when the user asks about
  OpenViking, needs help writing code that uses the openviking Python package, wants to
  configure or troubleshoot OpenViking, or needs to understand its architecture, APIs, or
  concepts (Viking URI, context types, retrieval mechanisms, session management, etc.).
  Trigger on mentions of: "openviking", "viking://", "OpenViking", "context database",
  "AGFS", "VikingFS", "ovpack", or related API methods like find/search/add_resource/add_skill/session.
---

# OpenViking Context Database

OpenViking is an open-source context database for AI Agents. It unifies memory, resources,
and skills via a virtual filesystem (`viking://` URIs), provides 3-layer progressive content
loading (L0 Abstract / L1 Overview / L2 Detail), and supports directory-recursive semantic
retrieval with intent analysis.

## Quick Reference

```python
import openviking as ov

client = ov.OpenViking(path="./data")   # embedded mode
client.initialize()

# Add resources
client.add_resource("./docs/", reason="Project docs")
client.wait_processed()

# Search
results = client.find("authentication", target_uri="viking://resources/")
results = client.search("help with auth", session=session)  # with intent analysis

# Filesystem ops
client.ls("viking://resources/")
client.abstract("viking://resources/docs/")   # L0 ~100 tokens
client.overview("viking://resources/docs/")   # L1 ~2k tokens
client.read("viking://resources/docs/api.md") # L2 full content

# Sessions & memory
session = client.session()
session.add_message("user", [TextPart(text="...")])
session.commit()  # archives + extracts memories

client.close()
```

## Reference Files

Load the appropriate reference file based on what the user needs:

- **Getting started**: Read [references/quickstart.md](references/quickstart.md) — installation, configuration examples, first script
- **Client API**: Read [references/api-client.md](references/api-client.md) — OpenViking(), initialize, close, modes
- **Resources API**: Read [references/api-resources.md](references/api-resources.md) — add_resource, formats, ovpack, managing resources
- **Skills API**: Read [references/api-skills.md](references/api-skills.md) — add_skill, SKILL.md format, MCP conversion
- **Sessions API**: Read [references/api-sessions.md](references/api-sessions.md) — session lifecycle, messages, commit, memory extraction
- **Retrieval API**: Read [references/api-retrieval.md](references/api-retrieval.md) — find vs search, FindResult, hierarchical retrieval
- **Filesystem API**: Read [references/api-filesystem.md](references/api-filesystem.md) — abstract, overview, read, ls, tree, rm, mv, grep, glob, link
- **Concepts**: Read [references/concepts.md](references/concepts.md) — architecture, context types, Viking URI, L0/L1/L2, storage, retrieval mechanism, extraction, session management
- **Configuration**: Read [references/configuration.md](references/configuration.md) — ov.conf schema, model providers, env vars, troubleshooting

## Key Concepts Summary

| Concept | Description |
|---------|-------------|
| **Viking URI** | `viking://{scope}/{path}` — scopes: resources, user, agent, session |
| **Context Types** | Resource (knowledge), Memory (cognition), Skill (capabilities) |
| **L0/L1/L2** | Abstract (~100 tok) / Overview (~2k tok) / Full content (unlimited) |
| **find()** | Simple vector search, low latency |
| **search()** | Intent analysis + session context, higher quality |
| **Session commit** | Archives messages, extracts 6 memory categories |
| **Memory categories** | profile, preferences, entities, events (user); cases, patterns (agent) |

## Docs Source

Full documentation: https://openviking.ai/docs
