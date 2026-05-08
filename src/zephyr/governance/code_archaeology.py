from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class BlameRecord(BaseModel):
    file: str
    line: int
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    provenance: Optional[dict[str, object]] = None


class CommitNode(BaseModel):
    commit_hash: str
    message: str
    author: str
    date: str
    parents: list[str] = Field(default_factory=list)
    files_changed: list[str] = Field(default_factory=list)


class EvolutionGraph(BaseModel):
    nodes: dict[str, CommitNode] = Field(default_factory=dict)
    edges: list[tuple[str, str]] = Field(default_factory=list)

    def add_commit(self, node: CommitNode) -> None:
        self.nodes[node.commit_hash] = node
        for parent in node.parents:
            self.edges.append((parent, node.commit_hash))

    def timeline(self) -> list[CommitNode]:
        return sorted(self.nodes.values(), key=lambda n: n.date)


def blame(file: str, line: int) -> BlameRecord:
    return BlameRecord(file=file, line=line)


def auto_doc(module_id: str, functions: list[str]) -> str:
    header = f"# Module: {module_id}\n\n"
    header += f"Auto-generated {datetime.now(timezone.utc).isoformat()[:19]}\n\n"
    header += "## Key Functions\n\n"
    for fn in functions:
        header += f"* `{fn}()`\n"
    return header
