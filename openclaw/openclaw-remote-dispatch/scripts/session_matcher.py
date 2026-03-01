from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Callable

from session_registry import SessionNode, SessionRegistry

log = logging.getLogger(__name__)

try:
    from rapidfuzz import fuzz  # type: ignore
except ImportError:
    fuzz = None


class MatchDecision:
    NEW_ROOT = "new_root"
    FORK = "fork"
    CONTINUE = "continue"


@dataclass
class MatchResult:
    decision: str
    matched_session_id: str
    score: float
    reason: str


class SessionMatcher:
    def __init__(
        self,
        registry: SessionRegistry,
        llm_classify: Callable[..., Any] | None = None,
        fork_threshold: float = 0.78,
        new_threshold: float = 0.35,
    ) -> None:
        self.registry = registry
        self.llm_classify = llm_classify
        self.fork_threshold = max(0.0, min(1.0, fork_threshold))
        self.new_threshold = max(0.0, min(1.0, new_threshold))
        if self.new_threshold > self.fork_threshold:
            self.new_threshold, self.fork_threshold = self.fork_threshold, self.new_threshold

    def match(self, host: str, folder: str, title: str) -> MatchResult:
        normalized_title = title.strip()
        candidates = self.registry.list_by_host_folder(host, folder)
        if not candidates:
            return MatchResult(
                decision=MatchDecision.NEW_ROOT,
                matched_session_id="",
                score=0.0,
                reason="No sessions found for host/folder",
            )

        fuzzy_scores: list[tuple[float, SessionNode]] = []
        if fuzz is not None:
            fuzzy_scores = self._compute_fuzzy_scores(normalized_title, candidates)
            best_score, best_node = fuzzy_scores[0]
            if best_score < self.new_threshold:
                return MatchResult(
                    decision=MatchDecision.NEW_ROOT,
                    matched_session_id="",
                    score=best_score,
                    reason=f"Best fuzzy score {best_score:.2f} below new_threshold",
                )
            if best_score >= self.fork_threshold:
                return MatchResult(
                    decision=MatchDecision.FORK,
                    matched_session_id=best_node.session_id,
                    score=best_score,
                    reason=f"Best fuzzy score {best_score:.2f} above fork_threshold",
                )
        else:
            log.debug("rapidfuzz unavailable, skipping stage-2 fuzzy scoring")

        llm_result = self._run_llm_tie_breaker(host, folder, normalized_title, candidates, fuzzy_scores)
        if llm_result is not None:
            return llm_result

        return self._deterministic_fallback(normalized_title, candidates, fuzzy_scores)

    def _compute_fuzzy_scores(
        self,
        title: str,
        candidates: list[SessionNode],
    ) -> list[tuple[float, SessionNode]]:
        scores = [
            (float(fuzz.token_sort_ratio(title, node.title)) / 100.0, node)
            for node in candidates
        ]
        scores.sort(key=lambda item: item[0], reverse=True)
        return scores

    def _run_llm_tie_breaker(
        self,
        host: str,
        folder: str,
        title: str,
        candidates: list[SessionNode],
        fuzzy_scores: list[tuple[float, SessionNode]],
    ) -> MatchResult | None:
        if self.llm_classify is None:
            return None

        system_prompt = (
            "You route tasks to existing coding sessions. "
            "Return strict JSON only with keys: decision, matched_session_id, score, reason. "
            "Allowed decision values: new_root, fork, continue."
        )
        candidates_text = self._format_candidates(candidates, fuzzy_scores)
        user_prompt = (
            f"Host: {host}\n"
            f"Folder: {folder}\n"
            f"Incoming title: {title}\n\n"
            f"Candidates:\n{candidates_text}\n\n"
            "Rules:\n"
            "- new_root: unrelated work\n"
            "- fork: related but should branch from an existing session\n"
            "- continue: directly continue one existing session\n"
            "Return JSON only."
        )

        try:
            raw = self.llm_classify(system_prompt, user_prompt)
        except TypeError:
            raw = self.llm_classify(system_prompt=system_prompt, user_prompt=user_prompt)
        except Exception as exc:  # noqa: BLE001
            log.warning("Session matcher LLM callback failed: %s", exc)
            return None

        parsed = self._coerce_response_to_dict(raw)
        if parsed is None:
            return None

        return self._validate_llm_result(parsed, candidates)

    def _format_candidates(
        self,
        candidates: list[SessionNode],
        fuzzy_scores: list[tuple[float, SessionNode]],
    ) -> str:
        score_map = {node.session_id: score for score, node in fuzzy_scores}
        lines: list[str] = []
        for idx, node in enumerate(candidates, start=1):
            summary = node.summary_text.replace("\n", " ").strip()
            if len(summary) > 180:
                summary = summary[:179].rstrip() + "…"
            score = score_map.get(node.session_id)
            if score is None:
                score_text = "n/a"
            else:
                score_text = f"{score:.2f}"
            lines.append(
                f"{idx}. session_id={node.session_id} fuzzy={score_text} title={node.title!r} "
                f"summary={summary!r}",
            )
        return "\n".join(lines)

    def _coerce_response_to_dict(self, raw: Any) -> dict[str, Any] | None:
        if isinstance(raw, dict):
            return raw

        if isinstance(raw, str):
            candidates = [raw.strip()]
            fenced = re.findall(r"```(?:json)?\s*(.*?)\s*```", raw, flags=re.IGNORECASE | re.DOTALL)
            candidates.extend(chunk.strip() for chunk in fenced if chunk.strip())
            for candidate in candidates:
                try:
                    parsed = json.loads(candidate)
                except json.JSONDecodeError:
                    continue
                if isinstance(parsed, dict):
                    return parsed

        return None

    def _validate_llm_result(
        self,
        payload: dict[str, Any],
        candidates: list[SessionNode],
    ) -> MatchResult | None:
        decision = str(payload.get("decision", "")).strip().lower()
        if decision not in {
            MatchDecision.NEW_ROOT,
            MatchDecision.FORK,
            MatchDecision.CONTINUE,
        }:
            return None

        candidate_ids = {node.session_id for node in candidates}
        matched_session_id = str(
            payload.get("matched_session_id") or payload.get("session_id") or "",
        ).strip()

        if decision == MatchDecision.NEW_ROOT:
            matched_session_id = ""
        elif matched_session_id not in candidate_ids:
            return None

        score_raw = payload.get("score", 0.0)
        try:
            score = float(score_raw)
        except (TypeError, ValueError):
            score = 0.0
        score = max(0.0, min(1.0, score))

        reason = str(payload.get("reason", "LLM tie-breaker result")).strip() or "LLM tie-breaker result"
        return MatchResult(
            decision=decision,
            matched_session_id=matched_session_id,
            score=score,
            reason=reason,
        )

    def _deterministic_fallback(
        self,
        title: str,
        candidates: list[SessionNode],
        fuzzy_scores: list[tuple[float, SessionNode]],
    ) -> MatchResult:
        if fuzzy_scores:
            best_score, best_node = fuzzy_scores[0]
        else:
            scored = [
                (
                    SequenceMatcher(None, title.lower(), node.title.lower()).ratio(),
                    node,
                )
                for node in candidates
            ]
            scored.sort(key=lambda item: item[0], reverse=True)
            best_score, best_node = scored[0]

        if best_score >= 0.5:
            return MatchResult(
                decision=MatchDecision.FORK,
                matched_session_id=best_node.session_id,
                score=best_score,
                reason="Deterministic fallback selected best candidate >= 0.5",
            )

        return MatchResult(
            decision=MatchDecision.NEW_ROOT,
            matched_session_id="",
            score=best_score,
            reason="Deterministic fallback selected new_root (< 0.5)",
        )


if __name__ == "__main__":
    import tempfile
    import time
    from pathlib import Path

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    demo_path = Path(tempfile.gettempdir()) / f"session-matcher-demo-{int(time.time())}.json"
    registry = SessionRegistry(str(demo_path))
    registry.add(
        SessionNode(
            session_id="ses_alpha",
            task_id="task_alpha",
            host="devbox",
            folder="/srv/app",
            title="Fix websocket reconnect race",
            agent="build",
            summary_text="Implemented locking around reconnect path",
            completed_at=time.time() - 300,
        ),
    )
    registry.add(
        SessionNode(
            session_id="ses_beta",
            task_id="task_beta",
            host="devbox",
            folder="/srv/app",
            title="Refactor notifier chunking logic",
            agent="build",
            summary_text="Split long messages with channel limits",
            completed_at=time.time() - 100,
        ),
    )

    matcher = SessionMatcher(registry)
    print("match 1 ->", matcher.match("devbox", "/srv/app", "Fix reconnect websocket race condition"))
    print("match 2 ->", matcher.match("devbox", "/srv/app", "Design PostgreSQL schema migration"))

    def _fake_llm(system_prompt: str, user_prompt: str) -> dict[str, Any]:
        _ = system_prompt
        _ = user_prompt
        return {
            "decision": "continue",
            "matched_session_id": "ses_alpha",
            "score": 0.9,
            "reason": "Same reconnect thread, continue existing conversation",
        }

    llm_matcher = SessionMatcher(registry, llm_classify=_fake_llm, fork_threshold=0.95, new_threshold=0.2)
    print(
        "match 3 (LLM tie-break) ->",
        llm_matcher.match("devbox", "/srv/app", "Continue reconnect race investigation"),
    )

    try:
        demo_path.unlink(missing_ok=True)
    except OSError:
        pass
