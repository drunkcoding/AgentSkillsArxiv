from __future__ import annotations

import logging

log = logging.getLogger(__name__)

_DEEP_KEYWORDS = (
    "investigate",
    "explore",
    "find out",
    "how does",
    "what is",
    "search for",
    "look into",
    "understand",
    "discover",
    "dig into",
)
_PLAN_KEYWORDS = (
    "analyze",
    "review",
    "propose",
    "plan",
    "audit",
    "assess",
    "evaluate",
    "design",
    "architect",
    "outline",
)
_BUILD_KEYWORDS = (
    "implement",
    "fix",
    "add",
    "create",
    "update",
    "refactor",
    "test",
    "build",
    "write",
    "delete",
    "remove",
    "migrate",
)
_VALID_AGENTS = ("build", "plan", "deep")
_FALLBACKS = {"deep": ("deep", "plan", "build"), "plan": ("plan", "build"), "build": ("build",)}


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _pick_agent(title: str) -> str:
    text = title.lower().strip()
    if _contains_any(text, _DEEP_KEYWORDS):
        return "deep"
    if _contains_any(text, _PLAN_KEYWORDS):
        return "plan"
    if _contains_any(text, _BUILD_KEYWORDS):
        return "build"
    return "build"


def classify_intent(title: str) -> str:
    selected = _pick_agent(title)
    if selected == "deep":
        return "exploration"
    if selected == "plan":
        return "analysis"
    return "implementation"


def route_agent(title: str, explicit_agent: str | None = None, available_agents: list[str] | None = None) -> str:
    if explicit_agent:
        explicit = explicit_agent.strip().lower()
        if explicit in _VALID_AGENTS:
            return explicit
        log.debug("Ignoring invalid explicit agent: %r", explicit_agent)

    selected = _pick_agent(title)
    if not available_agents:
        return selected

    available = {agent.strip().lower() for agent in available_agents if isinstance(agent, str) and agent.strip()}
    for candidate in _FALLBACKS[selected]:
        if candidate in available:
            return candidate
    return "build"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    examples = [
        "Investigate why retries never stop",
        "Explore OpenCode SSE ordering",
        "Find out what causes duplicate prompts",
        "How does resume logic work",
        "Analyze current dispatch flow",
        "Review tunnel reconnect behavior",
        "Propose safer retry policy",
        "Design event batching",
        "Implement backpressure handling",
        "Fix notifier truncation",
        "Add task status footer",
        "Refactor parser regexes",
    ]
    for title in examples:
        print(f"{title} -> agent={route_agent(title)} intent={classify_intent(title)}")
    print("explicit override ->", route_agent("investigate retries", explicit_agent="build"))
    print("fallback demo ->", route_agent("investigate retries", available_agents=["plan", "build"]))
