from __future__ import annotations

import importlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from .config import Mem0Config


@asynccontextmanager
async def mem0_lifespan(server: FastMCP) -> AsyncIterator[dict[str, object]]:
    """Initialize mem0 client on startup, cleanup on shutdown."""

    del server
    config = Mem0Config.from_env()
    client = config.create_memory_client()
    yield {"mem0_client": client, "config": config}


mcp = FastMCP(
    "mem0_mcp",
    lifespan=mem0_lifespan,
)


def _register_tools() -> None:
    _ = importlib.import_module(".tools", package=__package__)


def main() -> int:
    _register_tools()
    mcp.run(transport="stdio")
    return 0
