# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.gov_audit.code_archaeology
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-GOV_code_archaeology | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class BlameRecord(BaseModel):
    file: str
    line: int
    agent_id: str | None = None
    session_id: str | None = None
    task_id: str | None = None
    provenance: dict[str, object] | None = None


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


def blame(file_path: str, line: int) -> BlameRecord:
    return BlameRecord(file=file_path, line=line)


def auto_doc(module_id: str, functions: list[str]) -> str:
    header = f"# Module: {module_id}\n\n"
    header += f"Auto-generated {datetime.now(UTC).isoformat()[:19]}\n\n"
    header += "## Key Functions\n\n"
    for fn in functions:
        header += f"* `{fn}()`\n"
    return header
