from __future__ import annotations

import json
from typing import ClassVar, Protocol, cast

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from mcp.types import ToolAnnotations
from pydantic import BaseModel, ConfigDict, Field

from . import __version__
from .config import Mem0Config
from .server import mcp


McpContext = Context[ServerSession, dict[str, object], object]


class _Mem0ClientProtocol(Protocol):
    def add(self, data: str, **kwargs: object) -> object: ...

    def search(self, query: str, **kwargs: object) -> object: ...

    def get_all(self, **kwargs: object) -> object: ...

    def get(self, memory_id: str) -> object: ...

    def update(self, memory_id: str, data: str) -> object: ...

    def delete(self, memory_id: str) -> object: ...

    def delete_all(self, **kwargs: object) -> object: ...

    def history(self, memory_id: str) -> object: ...


class _ScopedInput(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", str_strip_whitespace=True)

    user_id: str | None = Field(default=None, min_length=1)
    agent_id: str | None = Field(default=None, min_length=1)
    run_id: str | None = Field(default=None, min_length=1)


class _Mem0AddInput(_ScopedInput):
    data: str = Field(..., min_length=1, description="Text content to persist as memory.")
    metadata: dict[str, object] | None = Field(
        default=None,
        description="Optional metadata attached to the memory object.",
    )


class _Mem0SearchInput(_ScopedInput):
    query: str = Field(..., min_length=1, description="Semantic search query.")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results to return.")


class _Mem0ListInput(_ScopedInput):
    pass


class _MemoryIdInput(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", str_strip_whitespace=True)

    memory_id: str = Field(..., min_length=1, description="Unique memory identifier.")


class _Mem0UpdateInput(_MemoryIdInput):
    data: str = Field(..., min_length=1, description="Updated memory content.")


class _Mem0DeleteAllInput(_ScopedInput):
    confirm: bool = Field(default=False, description="Safety flag required to execute bulk delete.")


def _json_response(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, default=str)


def _error_response(tool_name: str, exc: Exception, hint: str | None = None) -> str:
    return _json_response(
        {
            "error": str(exc),
            "tool": tool_name,
            "hint": hint
            or "Check tool inputs and MEM0_* environment configuration, then retry.",
        }
    )


def _extract_results(payload: object) -> list[object]:
    if isinstance(payload, dict):
        payload_dict = cast(dict[str, object], payload)
        results = payload_dict.get("results")
        if isinstance(results, list):
            return cast(list[object], results)
    if isinstance(payload, list):
        return cast(list[object], payload)
    if payload is None:
        return []
    return [payload]


def _get_runtime_dependencies(ctx: McpContext) -> tuple[_Mem0ClientProtocol, Mem0Config]:
    lifespan_context = ctx.request_context.lifespan_context

    try:
        client = lifespan_context["mem0_client"]
        config = lifespan_context["config"]
    except KeyError as exc:
        raise RuntimeError(
            "mem0 client is not initialized in lifespan context. Check startup logs and MEM0_* environment variables."
        ) from exc

    if not isinstance(config, Mem0Config):
        raise RuntimeError(
            "Invalid runtime configuration object in lifespan context. Restart the server to rebuild runtime state."
        )

    required_methods = (
        "add",
        "search",
        "get_all",
        "get",
        "update",
        "delete",
        "delete_all",
        "history",
    )
    for method_name in required_methods:
        if not callable(getattr(client, method_name, None)):
            raise RuntimeError(
                f"mem0 client does not implement required method '{method_name}'. Verify the installed mem0ai package version."
            )

    return cast(_Mem0ClientProtocol, client), config


def _resolve_scope(
    user_id: str | None,
    agent_id: str | None,
    run_id: str | None,
    config: Mem0Config,
) -> dict[str, str]:
    """Build scope kwargs, falling back to config defaults. Raises if no scope provided."""

    scope: dict[str, str] = {}
    uid = user_id or config.default_user_id
    if uid:
        scope["user_id"] = uid
    if agent_id:
        scope["agent_id"] = agent_id
    if run_id:
        scope["run_id"] = run_id
    if not scope:
        raise ValueError(
            "At least one scope identifier required: user_id, agent_id, or run_id. Set MEM0_DEFAULT_USER_ID env var or pass explicitly."
        )
    return scope


resolve_scope = _resolve_scope


@mcp.tool(
    name="mem0_add",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ),
)
async def mem0_add(
    data: str,
    ctx: McpContext,
    user_id: str | None = None,
    agent_id: str | None = None,
    run_id: str | None = None,
    metadata: dict[str, object] | None = None,
) -> str:
    """Add a new memory entry to mem0 for the provided scope.

    This tool stores text content in mem0 using either explicit scope identifiers
    or `MEM0_DEFAULT_USER_ID` as a fallback when `user_id` is omitted.

    Args:
        data (str): The memory content to store.
        ctx (Context): FastMCP request context carrying lifespan state.
        user_id (str | None): Optional user scope identifier.
        agent_id (str | None): Optional agent scope identifier.
        run_id (str | None): Optional run scope identifier.
        metadata (dict[str, object] | None): Optional metadata to attach.

    Returns:
        str: JSON payload with created memory IDs, normalized results, scope, and count.
    """

    try:
        params = _Mem0AddInput(
            data=data,
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            metadata=metadata,
        )
        client, config = _get_runtime_dependencies(ctx)
        scope = _resolve_scope(params.user_id, params.agent_id, params.run_id, config)

        result = client.add(params.data, **scope, metadata=params.metadata)
        entries = _extract_results(result)
        memory_ids: list[str] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            entry_dict = cast(dict[str, object], entry)
            memory_id = entry_dict.get("id")
            if isinstance(memory_id, str):
                memory_ids.append(memory_id)

        return _json_response(
            {
                "tool": "mem0_add",
                "scope": scope,
                "memory_ids": memory_ids,
                "results": entries,
                "count": len(entries),
            }
        )
    except Exception as exc:
        return _error_response(
            "mem0_add",
            exc,
            hint="Pass user_id, agent_id, or run_id (or set MEM0_DEFAULT_USER_ID) before calling mem0_add.",
        )


@mcp.tool(
    name="mem0_search",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def mem0_search(
    query: str,
    ctx: McpContext,
    user_id: str | None = None,
    agent_id: str | None = None,
    run_id: str | None = None,
    limit: int = 10,
) -> str:
    """Search mem0 memories for a scoped identity using semantic similarity.

    Args:
        query (str): Semantic query string used for memory retrieval.
        ctx (Context): FastMCP request context carrying lifespan state.
        user_id (str | None): Optional user scope identifier.
        agent_id (str | None): Optional agent scope identifier.
        run_id (str | None): Optional run scope identifier.
        limit (int): Maximum number of matches to return (1-100).

    Returns:
        str: JSON payload with matching memories, scope, and result count.
    """

    try:
        params = _Mem0SearchInput(
            query=query,
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            limit=limit,
        )
        client, config = _get_runtime_dependencies(ctx)
        scope = _resolve_scope(params.user_id, params.agent_id, params.run_id, config)

        result = client.search(params.query, **scope, limit=params.limit)
        matches = _extract_results(result)

        return _json_response(
            {
                "tool": "mem0_search",
                "query": params.query,
                "scope": scope,
                "results": matches,
                "count": len(matches),
            }
        )
    except Exception as exc:
        return _error_response(
            "mem0_search",
            exc,
            hint="Ensure query is non-empty and provide scope identifiers explicitly or via MEM0_DEFAULT_USER_ID.",
        )


@mcp.tool(
    name="mem0_list",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def mem0_list(
    ctx: McpContext,
    user_id: str | None = None,
    agent_id: str | None = None,
    run_id: str | None = None,
) -> str:
    """List all memories for a scoped identity.

    Args:
        ctx (Context): FastMCP request context carrying lifespan state.
        user_id (str | None): Optional user scope identifier.
        agent_id (str | None): Optional agent scope identifier.
        run_id (str | None): Optional run scope identifier.

    Returns:
        str: JSON payload containing all memories for the resolved scope.
    """

    try:
        params = _Mem0ListInput(user_id=user_id, agent_id=agent_id, run_id=run_id)
        client, config = _get_runtime_dependencies(ctx)
        scope = _resolve_scope(params.user_id, params.agent_id, params.run_id, config)

        result = client.get_all(**scope)
        memories = _extract_results(result)

        return _json_response(
            {
                "tool": "mem0_list",
                "scope": scope,
                "results": memories,
                "count": len(memories),
            }
        )
    except Exception as exc:
        return _error_response(
            "mem0_list",
            exc,
            hint="Provide scope identifiers explicitly or set MEM0_DEFAULT_USER_ID for default scope.",
        )


@mcp.tool(
    name="mem0_get",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def mem0_get(memory_id: str, ctx: McpContext) -> str:
    """Fetch a single memory by ID.

    Args:
        memory_id (str): Target memory identifier.
        ctx (Context): FastMCP request context carrying lifespan state.

    Returns:
        str: JSON payload with the fetched memory object.
    """

    try:
        params = _MemoryIdInput(memory_id=memory_id)
        client, _ = _get_runtime_dependencies(ctx)
        result = client.get(params.memory_id)

        return _json_response(
            {
                "tool": "mem0_get",
                "memory_id": params.memory_id,
                "memory": result,
            }
        )
    except Exception as exc:
        return _error_response(
            "mem0_get",
            exc,
            hint="Verify the memory_id exists in mem0 and that your backend credentials are valid.",
        )


@mcp.tool(
    name="mem0_update",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def mem0_update(memory_id: str, data: str, ctx: McpContext) -> str:
    """Update a specific memory's content by ID.

    Args:
        memory_id (str): Target memory identifier.
        data (str): Replacement memory text.
        ctx (Context): FastMCP request context carrying lifespan state.

    Returns:
        str: JSON confirmation payload with backend response details.
    """

    try:
        params = _Mem0UpdateInput(memory_id=memory_id, data=data)
        client, _ = _get_runtime_dependencies(ctx)
        result = client.update(params.memory_id, params.data)

        return _json_response(
            {
                "tool": "mem0_update",
                "memory_id": params.memory_id,
                "status": "updated",
                "result": result,
            }
        )
    except Exception as exc:
        return _error_response(
            "mem0_update",
            exc,
            hint="Ensure memory_id exists and data is non-empty before updating.",
        )


@mcp.tool(
    name="mem0_delete",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def mem0_delete(memory_id: str, ctx: McpContext) -> str:
    """Delete a specific memory by ID.

    Args:
        memory_id (str): Target memory identifier.
        ctx (Context): FastMCP request context carrying lifespan state.

    Returns:
        str: JSON confirmation payload for the delete operation.
    """

    try:
        params = _MemoryIdInput(memory_id=memory_id)
        client, _ = _get_runtime_dependencies(ctx)
        result = client.delete(params.memory_id)

        return _json_response(
            {
                "tool": "mem0_delete",
                "memory_id": params.memory_id,
                "status": "deleted",
                "result": result,
            }
        )
    except Exception as exc:
        return _error_response(
            "mem0_delete",
            exc,
            hint="Confirm memory_id is correct and that the configured backend permits deletion.",
        )


@mcp.tool(
    name="mem0_delete_all",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def mem0_delete_all(
    ctx: McpContext,
    user_id: str | None = None,
    agent_id: str | None = None,
    run_id: str | None = None,
    confirm: bool = False,
) -> str:
    """Delete all memories for a scope after explicit confirmation.

    Args:
        ctx (Context): FastMCP request context carrying lifespan state.
        user_id (str | None): Optional user scope identifier.
        agent_id (str | None): Optional agent scope identifier.
        run_id (str | None): Optional run scope identifier.
        confirm (bool): Must be True to perform destructive delete-all.

    Returns:
        str: JSON warning when confirmation is missing, otherwise delete confirmation.
    """

    try:
        params = _Mem0DeleteAllInput(
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            confirm=confirm,
        )
        client, config = _get_runtime_dependencies(ctx)

        if not params.confirm:
            return _json_response(
                {
                    "tool": "mem0_delete_all",
                    "status": "confirmation_required",
                    "warning": "Set confirm=true to delete all memories for the resolved scope.",
                }
            )

        scope = _resolve_scope(params.user_id, params.agent_id, params.run_id, config)
        result = client.delete_all(**scope)

        return _json_response(
            {
                "tool": "mem0_delete_all",
                "scope": scope,
                "status": "deleted",
                "result": result,
            }
        )
    except Exception as exc:
        return _error_response(
            "mem0_delete_all",
            exc,
            hint="For safety, pass confirm=true and provide scope identifiers explicitly or via MEM0_DEFAULT_USER_ID.",
        )


@mcp.tool(
    name="mem0_history",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def mem0_history(memory_id: str, ctx: McpContext) -> str:
    """Return change history for a memory ID.

    Args:
        memory_id (str): Target memory identifier.
        ctx (Context): FastMCP request context carrying lifespan state.

    Returns:
        str: JSON payload containing historical updates for the specified memory.
    """

    try:
        params = _MemoryIdInput(memory_id=memory_id)
        client, _ = _get_runtime_dependencies(ctx)
        result = client.history(params.memory_id)
        entries = _extract_results(result)

        return _json_response(
            {
                "tool": "mem0_history",
                "memory_id": params.memory_id,
                "results": entries,
                "count": len(entries),
            }
        )
    except Exception as exc:
        return _error_response(
            "mem0_history",
            exc,
            hint="Verify memory_id and ensure your mem0 backend allows history retrieval.",
        )


@mcp.tool(
    name="mem0_health",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def mem0_health(ctx: McpContext) -> str:
    """Check server runtime state and mem0 backend wiring.

    Args:
        ctx (Context): FastMCP request context carrying lifespan state.

    Returns:
        str: JSON status payload including profile, server version, and backend readiness.
    """

    try:
        client, config = _get_runtime_dependencies(ctx)
        required_methods = (
            "add",
            "search",
            "get_all",
            "get",
            "update",
            "delete",
            "delete_all",
            "history",
        )
        method_support = {
            method_name: callable(getattr(client, method_name, None))
            for method_name in required_methods
        }
        backend_status = "ok" if all(method_support.values()) else "degraded"

        return _json_response(
            {
                "tool": "mem0_health",
                "profile": config.profile,
                "version": __version__,
                "backend_status": backend_status,
                "client_type": type(client).__name__,
                "default_user_id": config.default_user_id,
                "method_support": method_support,
            }
        )
    except Exception as exc:
        return _error_response(
            "mem0_health",
            exc,
            hint="Validate MEM0_PROFILE, MEM0_API_KEY/MEM0_CONFIG_PATH, and dependency installation before retrying.",
        )
