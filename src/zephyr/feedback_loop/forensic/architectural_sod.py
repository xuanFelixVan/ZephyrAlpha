# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.architectural_sod
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Architectural SoD — v0.15.0 R205

Blindspot: Single FLE role can diagnose AND execute repair; no separation of duties.
Risk: R205 — Same entity that diagnoses also fixes; no internal challenge to diagnosis correctness.

Mitigation: Separation of Duties—diagnoser cannot also be executor without external approval gate.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: architectural_sod.py
# 层: 算法
# - id: A1
#   name_zh: ① ArchitecturalSoD
#   name_en: ArchitecturalSoD
#   intro: class ArchitecturalSoD 源码 L76-L93
#   desc: 公共方法（定义序）: register, check_conflict, require_dual_approval；源码 L76-L93
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ArchitecturalSoD
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SoDRole(str, Enum):
    DIAGNOSER = "DIAGNOSER"
    EXECUTOR = "EXECUTOR"
    VERIFIER = "VERIFIER"
    AUDITOR = "AUDITOR"


@dataclass
class SoDConflict:
    action_id: str
    requested_by: SoDRole
    attempted_role: SoDRole
    blocked: bool = True


@dataclass
class ArchitecturalSoD:
    role_assignments: dict[str, SoDRole] = field(default_factory=dict)
    conflicts: list[SoDConflict] = field(default_factory=list)
    forbidden_transitions: set[tuple[str, str]] = field(
        default_factory=lambda: {("DIAGNOSER", "EXECUTOR"), ("EXECUTOR", "VERIFIER")}
    )

    def register(self, instance_id: str, role: SoDRole) -> None:
        self.role_assignments[instance_id] = role

    def check_conflict(self, instance_id: str, requested_role: SoDRole) -> bool:
        current_role = self.role_assignments.get(instance_id)
        if current_role is None:
            return False
        return (current_role.value, requested_role.value) in self.forbidden_transitions

    def require_dual_approval(self, action_id: str) -> list[SoDRole]:
        return [SoDRole.DIAGNOSER, SoDRole.AUDITOR]
