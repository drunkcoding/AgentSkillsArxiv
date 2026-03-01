from __future__ import annotations

import logging
import time
import uuid
from dataclasses import asdict
from graphlib import CycleError, TopologicalSorter

from session_registry import SessionNode, SessionRegistry

log = logging.getLogger(__name__)


class SessionGraph:
    def __init__(self, registry: SessionRegistry) -> None:
        self.registry = registry

    def add_edge(self, parent_id: str, child_id: str) -> None:
        data = self.registry._load()
        parent = data.get(parent_id)
        child = data.get(child_id)
        if parent is None or child is None:
            log.warning("Cannot add edge %s -> %s, missing node", parent_id, child_id)
            return

        if child_id not in parent.children:
            parent.children.append(child_id)
        child.parent_session_id = parent_id

        data[parent_id] = parent
        data[child_id] = child
        self.registry._save(data)

    def get_roots(self) -> list[str]:
        data = self.registry._load()
        roots = [
            session_id
            for session_id, node in data.items()
            if not node.parent_session_id or node.parent_session_id not in data
        ]
        roots.sort()
        return roots

    def get_subtree(self, session_id: str) -> list[str]:
        data = self.registry._load()
        if session_id not in data:
            return []

        children_map = self._build_children_map(data)
        queue = [session_id]
        visited = {session_id}
        descendants: list[str] = []

        while queue:
            current = queue.pop(0)
            for child_id in sorted(children_map.get(current, set())):
                if child_id in visited:
                    continue
                visited.add(child_id)
                descendants.append(child_id)
                queue.append(child_id)

        return descendants

    def get_ancestors(self, session_id: str) -> list[str]:
        data = self.registry._load()
        if session_id not in data:
            return []

        ancestors: list[str] = []
        seen: set[str] = set()
        current_id = session_id

        while True:
            current = data.get(current_id)
            if current is None:
                break
            parent_id = current.parent_session_id
            if not parent_id or parent_id not in data or parent_id in seen:
                break
            ancestors.append(parent_id)
            seen.add(parent_id)
            current_id = parent_id

        return ancestors

    def get_related(self, session_id: str) -> list[str]:
        data = self.registry._load()
        node = data.get(session_id)
        if node is None:
            return []

        children_map = self._build_children_map(data)
        related: set[str] = {
            related_id
            for related_id in node.related_sessions
            if related_id in data and related_id != session_id
        }

        parent_id = node.parent_session_id
        if parent_id and parent_id in data:
            siblings = {
                sibling_id
                for sibling_id in children_map.get(parent_id, set())
                if sibling_id != session_id and sibling_id in data
            }
            related.update(siblings)

            parent = data[parent_id]
            grandparent_id = parent.parent_session_id
            if grandparent_id and grandparent_id in data:
                for aunt_uncle_id in children_map.get(grandparent_id, set()):
                    if aunt_uncle_id == parent_id:
                        continue
                    for cousin_id in children_map.get(aunt_uncle_id, set()):
                        if cousin_id != session_id and cousin_id in data:
                            related.add(cousin_id)

        return sorted(related)

    def merge_sessions(self, session_ids: list[str], new_title: str) -> str:
        data = self.registry._load()
        selected_ids = [session_id for session_id in session_ids if session_id in data]
        if not selected_ids:
            raise ValueError("No valid session IDs provided for merge")

        selected_nodes = [data[session_id] for session_id in selected_ids]
        hosts = {node.host for node in selected_nodes}
        folders = {node.folder for node in selected_nodes}
        agents = {node.agent for node in selected_nodes}

        merge_id = f"merge_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        merged_summary = "Merged sessions: " + ", ".join(selected_ids)
        merge_node = SessionNode(
            session_id=merge_id,
            task_id=f"task_{merge_id}",
            host=hosts.pop() if len(hosts) == 1 else "mixed",
            folder=folders.pop() if len(folders) == 1 else "mixed",
            title=new_title,
            agent=agents.pop() if len(agents) == 1 else "merge",
            summary_text=merged_summary,
            completed_at=time.time(),
            children=selected_ids,
            metadata={
                "synthetic_merge": True,
                "merged_from": selected_ids,
                "created_at": time.time(),
            },
        )
        data[merge_id] = merge_node

        for session_id in selected_ids:
            node = data[session_id]
            if merge_id not in node.related_sessions:
                node.related_sessions.append(merge_id)
            data[session_id] = node

        self.registry._save(data)
        return merge_id

    def to_dict(self) -> dict:
        data = self.registry._load()
        return {
            "roots": self.get_roots(),
            "nodes": {
                session_id: asdict(node)
                for session_id, node in data.items()
            },
        }

    def detect_cycles(self) -> list[list[str]]:
        data = self.registry._load()
        children_map = self._build_children_map(data)

        predecessors: dict[str, set[str]] = {session_id: set() for session_id in data}
        for parent_id, children in children_map.items():
            for child_id in children:
                if child_id in predecessors and parent_id in data:
                    predecessors[child_id].add(parent_id)

        sorter = TopologicalSorter(predecessors)
        try:
            list(sorter.static_order())
            return []
        except CycleError as exc:
            if len(exc.args) >= 2 and isinstance(exc.args[1], list):
                cycle = [str(item) for item in exc.args[1]]
                return [cycle]
            return [["unknown_cycle"]]

    def format_tree(self, root_id: str | None = None) -> str:
        data = self.registry._load()
        if not data:
            return ""

        children_map = self._build_children_map(data)
        if root_id is not None and root_id not in data:
            return ""

        roots = [root_id] if root_id else self.get_roots()
        if not roots:
            roots = sorted(data.keys())

        lines: list[str] = []

        def format_label(session_id: str) -> str:
            node = data[session_id]
            return f"{session_id} [{node.title}]"

        def walk(current_id: str, prefix: str, seen: set[str]) -> None:
            children = [child_id for child_id in sorted(children_map.get(current_id, set())) if child_id in data]
            for index, child_id in enumerate(children):
                is_last = index == len(children) - 1
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{format_label(child_id)}")

                next_prefix = prefix + ("    " if is_last else "│   ")
                if child_id in seen:
                    lines.append(f"{next_prefix}↺ {child_id}")
                    continue
                next_seen = set(seen)
                next_seen.add(child_id)
                walk(child_id, next_prefix, next_seen)

        for root in roots:
            if root not in data:
                continue
            lines.append(format_label(root))
            walk(root, "", {root})

        return "\n".join(lines)

    def _build_children_map(self, data: dict[str, SessionNode]) -> dict[str, set[str]]:
        children_map: dict[str, set[str]] = {session_id: set() for session_id in data}
        for session_id, node in data.items():
            parent_id = node.parent_session_id
            if parent_id and parent_id in data:
                children_map[parent_id].add(session_id)
            for child_id in node.children:
                if child_id in data:
                    children_map[session_id].add(child_id)
        return children_map


if __name__ == "__main__":
    import tempfile
    from pathlib import Path

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    demo_path = Path(tempfile.gettempdir()) / f"session-graph-demo-{int(time.time())}.json"
    registry = SessionRegistry(str(demo_path))

    registry.add(
        SessionNode(
            session_id="ses_root",
            task_id="task_root",
            host="devbox",
            folder="/srv/app",
            title="Root investigation",
            agent="plan",
            completed_at=time.time() - 500,
        ),
    )
    registry.add(
        SessionNode(
            session_id="ses_child_a",
            task_id="task_child_a",
            host="devbox",
            folder="/srv/app",
            title="Reconnect fixes",
            agent="build",
            completed_at=time.time() - 300,
        ),
    )
    registry.add(
        SessionNode(
            session_id="ses_child_b",
            task_id="task_child_b",
            host="devbox",
            folder="/srv/app",
            title="Notifier cleanup",
            agent="build",
            completed_at=time.time() - 200,
        ),
    )
    registry.add(
        SessionNode(
            session_id="ses_grandchild",
            task_id="task_grandchild",
            host="devbox",
            folder="/srv/app",
            title="Retry policy refinement",
            agent="build",
            completed_at=time.time() - 100,
        ),
    )

    graph = SessionGraph(registry)
    graph.add_edge("ses_root", "ses_child_a")
    graph.add_edge("ses_root", "ses_child_b")
    graph.add_edge("ses_child_a", "ses_grandchild")

    print("roots ->", graph.get_roots())
    print("subtree(ses_root) ->", graph.get_subtree("ses_root"))
    print("ancestors(ses_grandchild) ->", graph.get_ancestors("ses_grandchild"))
    print("related(ses_child_a) ->", graph.get_related("ses_child_a"))

    merge_id = graph.merge_sessions(["ses_child_a", "ses_child_b"], "Merged implementation thread")
    print("merge_id ->", merge_id)
    print("cycles ->", graph.detect_cycles())
    print("tree:\n" + graph.format_tree())
    print("to_dict keys ->", sorted(graph.to_dict().keys()))

    try:
        demo_path.unlink(missing_ok=True)
    except OSError:
        pass
