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
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: file_path 参数
#   fields: 参数 file_path，类型注解 str
#   code: code_archaeology.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: line 参数
#   fields: 参数 line，类型注解 int
#   code: code_archaeology.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: module_id 参数
#   fields: 参数 module_id，类型注解 str
#   code: code_archaeology.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: functions 参数
#   fields: 参数 functions，类型注解 list[str]
#   code: code_archaeology.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① blame
#   name_en: blame
#   intro: blame(file_path, line) 源码 L115-L116
#   desc: 源码 L115-L116
#   inputs: file_path line
#   outputs: BlameRecord
# - id: A2
#   name_zh: ② auto_doc
#   name_en: auto_doc
#   intro: auto_doc(module_id, functions) 源码 L119-L125
#   desc: 源码 L119-L125
#   inputs: module_id functions
#   outputs: str
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: BlameRecord
#   name_en: BlameRecord
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

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
