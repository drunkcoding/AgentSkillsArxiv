# pyright: reportMissingImports=false

import asyncio
import copy
import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from mem0_mcp.config import Mem0Config, Mem0Profile
from mem0_mcp.tools import resolve_scope
from mem0_mcp.tools import mem0_list, mem0_search


def _clear_mem0_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MEM0_PROFILE", raising=False)
    monkeypatch.delenv("MEM0_API_KEY", raising=False)
    monkeypatch.delenv("MEM0_CONFIG_PATH", raising=False)
    monkeypatch.delenv("MEM0_DEFAULT_USER_ID", raising=False)


def test_resolve_scope_uses_explicit_user_id() -> None:
    config = Mem0Config(profile=Mem0Profile.LOCAL, default_user_id="fallback-user")
    scope = resolve_scope("alice", None, None, config)
    assert scope == {"user_id": "alice"}


def test_resolve_scope_falls_back_to_default_user_id() -> None:
    config = Mem0Config(profile=Mem0Profile.LOCAL, default_user_id="fallback-user")
    scope = resolve_scope(None, None, None, config)
    assert scope == {"user_id": "fallback-user"}


def test_resolve_scope_includes_agent_and_run() -> None:
    config = Mem0Config(profile=Mem0Profile.LOCAL)
    scope = resolve_scope(None, "agent-1", "run-1", config)
    assert scope == {"agent_id": "agent-1", "run_id": "run-1"}


def test_resolve_scope_raises_when_no_scope_available() -> None:
    config = Mem0Config(profile=Mem0Profile.LOCAL)
    with pytest.raises(ValueError, match="At least one scope identifier required"):
        _ = resolve_scope(None, None, None, config)


def test_config_from_env_defaults_to_local(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_mem0_env(monkeypatch)
    config = Mem0Config.from_env()
    assert config.profile == Mem0Profile.LOCAL
    assert config.api_key is None
    assert config.config_path is None
    assert config.default_user_id is None


def test_config_from_env_loads_hosted_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_mem0_env(monkeypatch)
    monkeypatch.setenv("MEM0_PROFILE", "hosted")
    monkeypatch.setenv("MEM0_API_KEY", "test-api-key")
    config = Mem0Config.from_env()
    assert config.profile == Mem0Profile.HOSTED
    assert config.api_key == "test-api-key"


def test_config_from_env_requires_api_key_for_hosted(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_mem0_env(monkeypatch)
    monkeypatch.setenv("MEM0_PROFILE", "hosted")
    with pytest.raises(ValidationError, match="MEM0_API_KEY is required"):
        _ = Mem0Config.from_env()


def test_config_from_env_requires_config_path_for_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_mem0_env(monkeypatch)
    monkeypatch.setenv("MEM0_PROFILE", "custom")
    with pytest.raises(ValidationError, match="MEM0_CONFIG_PATH is required"):
        _ = Mem0Config.from_env()


def test_config_profile_validation_rejects_unknown_profile() -> None:
    with pytest.raises(ValidationError):
        _ = Mem0Config.model_validate({"profile": "invalid-profile"})


def _build_test_ctx(client: MagicMock, *, default_user_id: str | None = None) -> SimpleNamespace:
    config = Mem0Config(profile=Mem0Profile.LOCAL, default_user_id=default_user_id)
    return SimpleNamespace(
        request_context=SimpleNamespace(
            lifespan_context={"mem0_client": client, "config": config}
        )
    )


def test_mem0_search_passes_filters_to_client() -> None:
    client = MagicMock()
    client.search.return_value = []
    ctx = _build_test_ctx(client)
    filters: dict[str, object] = {"project": "alpha"}

    _ = asyncio.run(
        mem0_search(query="find alpha", ctx=ctx, user_id="alice", limit=7, filters=filters)
    )

    client.search.assert_called_once_with(
        "find alpha",
        user_id="alice",
        limit=7,
        filters=filters,
    )


def test_mem0_search_without_filters_keeps_backward_compatible_call_shape() -> None:
    client = MagicMock()
    client.search.return_value = []
    ctx = _build_test_ctx(client)

    _ = asyncio.run(mem0_search(query="find all", ctx=ctx, user_id="alice"))

    client.search.assert_called_once_with(
        "find all",
        user_id="alice",
        limit=10,
    )


def test_mem0_list_passes_filters_to_client() -> None:
    client = MagicMock()
    client.get_all.return_value = []
    ctx = _build_test_ctx(client)
    filters: dict[str, object] = {"app_id": "beta"}

    _ = asyncio.run(mem0_list(ctx=ctx, user_id="alice", filters=filters))

    client.get_all.assert_called_once_with(user_id="alice", filters=filters)


def test_mem0_list_passes_limit_to_client() -> None:
    client = MagicMock()
    client.get_all.return_value = []
    ctx = _build_test_ctx(client)

    _ = asyncio.run(mem0_list(ctx=ctx, user_id="alice", limit=3))

    client.get_all.assert_called_once_with(user_id="alice", limit=3)


def test_mem0_list_without_filters_or_limit_keeps_backward_compatible_call_shape() -> None:
    client = MagicMock()
    client.get_all.return_value = []
    ctx = _build_test_ctx(client)

    _ = asyncio.run(mem0_list(ctx=ctx, user_id="alice"))

    client.get_all.assert_called_once_with(user_id="alice")


def test_mem0_search_passes_complex_filter_dict_unchanged() -> None:
    client = MagicMock()
    client.search.return_value = []
    ctx = _build_test_ctx(client)
    filters: dict[str, object] = {
        "AND": [
            {"project": {"in": ["alpha", "beta"]}},
            {"created_at": {"gte": "2026-01-01"}},
        ],
        "topic": "memory",
    }
    original_filters = copy.deepcopy(filters)

    response = asyncio.run(
        mem0_search(query="complex", ctx=ctx, user_id="alice", limit=4, filters=filters)
    )

    client.search.assert_called_once_with(
        "complex",
        user_id="alice",
        limit=4,
        filters=original_filters,
    )
    assert filters == original_filters
    parsed = json.loads(response)
    assert parsed["tool"] == "mem0_search"
