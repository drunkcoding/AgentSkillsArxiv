from __future__ import annotations

import importlib
import json
import os
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import ClassVar, cast

from pydantic import BaseModel, ConfigDict, model_validator


class Mem0Profile(str, Enum):
    LOCAL = "local"
    HOSTED = "hosted"
    CUSTOM = "custom"


def _normalize_env_value(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized if normalized else None

TECHNICAL_FACT_EXTRACTION_PROMPT = """You are a Technical Knowledge Extractor for a software engineering AI agent system.
Your task is to extract actionable technical facts from conversations between engineers and AI agents.

Extract ONLY facts that are worth remembering across sessions. Focus on:
- Architecture decisions and their rationale
- Library/API patterns, version-specific gotchas, and migration notes
- Debugging root causes that weren't immediately obvious
- Codebase conventions and structural patterns
- Performance characteristics and thresholds
- Configuration requirements and environment setup
- Security considerations and best practices applied
- User preferences for code style, PR conventions, or workflow

DO NOT extract:
- Trivial file paths or variable names (easily found via grep)
- Generic programming knowledge (common to any engineer)
- Temporary debugging state (stack traces, log lines)
- Raw code snippets without context about WHY they matter

Return facts as concise, actionable statements. Each fact should be self-contained and
useful to an engineer encountering the same codebase/library/problem in the future.

Input:
{user_input}

Extracted facts (return as JSON list of strings):"""


class Mem0Config(BaseModel):
    """Configuration loaded from environment variables."""

    model_config: ClassVar[ConfigDict] = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    profile: Mem0Profile = Mem0Profile.LOCAL
    api_key: str | None = None
    config_path: str | None = None
    default_user_id: str | None = None
    local_store_path: str | None = None

    @model_validator(mode="after")
    def _validate_profile_requirements(self) -> "Mem0Config":
        if self.profile == Mem0Profile.HOSTED and not self.api_key:
            raise ValueError("MEM0_API_KEY is required when MEM0_PROFILE=hosted.")
        if self.profile == Mem0Profile.CUSTOM and not self.config_path:
            raise ValueError("MEM0_CONFIG_PATH is required when MEM0_PROFILE=custom.")
        return self

    @classmethod
    def from_env(cls) -> "Mem0Config":
        """Load configuration from environment variables."""

        profile = (_normalize_env_value(os.getenv("MEM0_PROFILE")) or Mem0Profile.LOCAL.value).lower()

        return cls.model_validate(
            {
                "profile": profile,
                "api_key": _normalize_env_value(os.getenv("MEM0_API_KEY")),
                "config_path": _normalize_env_value(os.getenv("MEM0_CONFIG_PATH")),
                "default_user_id": _normalize_env_value(os.getenv("MEM0_DEFAULT_USER_ID")),
                "local_store_path": _normalize_env_value(os.getenv("MEM0_LOCAL_STORE_PATH")),
            }
        )

    def _resolve_local_store_path(self) -> Path:
        """Resolve the local store path, creating directories if needed."""
        raw = self.local_store_path or os.getenv("MEM0_LOCAL_STORE_PATH")
        if raw:
            store_path = Path(raw).expanduser().resolve()
        else:
            store_path = Path.home() / ".local" / "share" / "opencode" / "mem0"
        store_path.mkdir(parents=True, exist_ok=True)
        return store_path

    def create_memory_client(self) -> object:
        """Create the appropriate mem0 client based on profile."""

        try:
            mem0_module = importlib.import_module("mem0")
        except ImportError as exc:
            raise RuntimeError(
                "mem0ai is not installed. Install dependencies with `pip install -e .` or `pip install mem0ai`."
            ) from exc

        memory_cls: object | None = getattr(mem0_module, "Memory", None)
        memory_client_cls: object | None = getattr(mem0_module, "MemoryClient", None)
        if memory_cls is None or memory_client_cls is None:
            raise RuntimeError(
                "mem0 module does not expose Memory/MemoryClient. Upgrade to a compatible mem0ai version."
            )

        memory_client_ctor = cast(Callable[..., object], memory_client_cls)

        if self.profile == Mem0Profile.LOCAL:
            store_path = self._resolve_local_store_path()
            qdrant_path = str(store_path / "qdrant")
            local_config: dict[str, object] = {
                "custom_prompt": TECHNICAL_FACT_EXTRACTION_PROMPT,
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "collection_name": "opencode_mem0",
                        "path": qdrant_path,
                    },
                },
            }
            from_config = cast(
                Callable[..., object] | None,
                getattr(memory_cls, "from_config", None),
            )
            if not callable(from_config):
                raise RuntimeError(
                    "mem0 Memory.from_config is unavailable. Upgrade to a compatible mem0ai version."
                )
            if not os.getenv("OPENAI_API_KEY"):
                raise RuntimeError(
                    "mem0 LOCAL profile uses OpenAI for embeddings by default. "
                    "Set the OPENAI_API_KEY environment variable, or use "
                    "MEM0_PROFILE=custom with a config that specifies an "
                    "alternative embedder (e.g. huggingface)."
                )

            return from_config(local_config)  # type: ignore[arg-type]

        if self.profile == Mem0Profile.HOSTED:
            return memory_client_ctor(api_key=self.api_key)

        if self.profile == Mem0Profile.CUSTOM:
            config_path = Path(str(self.config_path)).expanduser()
            if not config_path.exists():
                raise FileNotFoundError(
                    f"MEM0_CONFIG_PATH does not exist: {config_path}. Provide a valid JSON config file."
                )

            try:
                parsed_config = cast(object, json.loads(config_path.read_text(encoding="utf-8")))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"MEM0_CONFIG_PATH must contain valid JSON: {config_path}."
                ) from exc

            if not isinstance(parsed_config, dict):
                raise ValueError(
                    "MEM0_CONFIG_PATH must point to a JSON object compatible with Memory.from_config."
                )

            config_data = cast(dict[str, object], parsed_config)
            memory_class = memory_cls

            from_config = cast(
                Callable[[dict[str, object]], object] | None,
                getattr(memory_class, "from_config", None),
            )
            if not callable(from_config):
                raise RuntimeError(
                    "mem0 Memory.from_config is unavailable. Upgrade to a compatible mem0ai version."
                )
            return from_config(config_data)

        raise ValueError(
            "Unsupported MEM0_PROFILE value. Expected one of: local, hosted, custom."
        )
