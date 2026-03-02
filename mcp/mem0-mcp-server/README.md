# mem0-mcp-server

Production-grade Model Context Protocol (MCP) server for persistent AI memory using [`mem0ai`](https://pypi.org/project/mem0ai/) and Python FastMCP.

## Features

- FastMCP-based tool server (no raw JSON-RPC implementation)
- Profile-based mem0 backend initialization via environment variables
- Lifespan-managed mem0 client initialization
- Scope-safe memory operations (`user_id`, `agent_id`, `run_id`)
- Structured JSON responses and actionable error payloads

## Installation

```bash
pip install -e .
```

## Configuration

Set behavior using environment variables:

- `MEM0_PROFILE`: `local` (default) | `hosted` | `custom`
- `MEM0_API_KEY`: required for `hosted`
- `MEM0_CONFIG_PATH`: required for `custom` (JSON config for `Memory.from_config`)
- `MEM0_DEFAULT_USER_ID`: optional fallback scope when `user_id` is omitted

### Profile examples

Local:

```bash
MEM0_PROFILE=local python -m mem0_mcp
```

Hosted:

```bash
MEM0_PROFILE=hosted MEM0_API_KEY=your-mem0-api-key python -m mem0_mcp
```

Custom:

```bash
MEM0_PROFILE=custom MEM0_CONFIG_PATH=/path/to/mem0-config.json python -m mem0_mcp
```

## Run

```bash
python -m mem0_mcp
```

The server runs over stdio transport.

## Available Tools

- `mem0_add`
- `mem0_search`
- `mem0_list`
- `mem0_get`
- `mem0_update`
- `mem0_delete`
- `mem0_delete_all`
- `mem0_history`
- `mem0_health`

## Tests

```bash
pytest
```
