# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.context_governance.context_package
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_schemas
# [CONSUMERS] tests/context/test_context_package.py; tests/e/test_e_context_package.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ContextPackage API: task_id/source_agent/blueprints/decisions/session_state/locks_held
# [MODIFY-GUARD] ContextPackage SSoT is zephyr.shared.protocols.a2a.a2a_schemas — re-export only
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/context/test_context_package.py; tests/e/test_e_context_package.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

Context Package — D-022-08 委托上下文包: 升级原因+证据链+历史try_trace。

This module exposes two distinct context-package types:
  1. `ContextPackage` (re-exported from zephyr.shared.protocols.a2a.a2a_schemas):
     the A2A-protocol context package with task_id/source_agent/blueprints/
     decisions/session_state/locks_held. SSoT is a2a_schemas — re-export only.
  2. `EscalationContext` + `ContextPackageBuilder`: escalation-specific context
     with evidence_chain/try_trace/escalation_level. Locally defined.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 升级上下文构建请求
#   fields: task_id / reason / level / evidence / trace
#   code: ContextPackageBuilder.build (L58)
# 层: 算法
# - id: A1
#   name_zh: SSoT 再导出
#   name_en: ssot_reexport
#   intro: ContextPackage 从 a2a_schemas 真源原样再导出，本地禁止重定义
#   code: L37 from-import
# - id: A2
#   name_zh: 升级上下文构建
#   name_en: escalation_context_build
#   intro: 组装 EscalationContext（context_id=CTX-{task_id}，证据链+try_trace）
#   code: ContextPackageBuilder.build (L58)
# 层: 输出
# - id: O1
#   name_zh: 上下文包/升级上下文
#   name_en: context_packages
#   intro: ContextPackage / EscalationContext
#   downstream: tests/context/test_context_package.py; tests/e/test_e_context_package.py
# [/ALGO_FLOW]
# 边: I1 --> A1 ; I1 --> A2 ; A1 --> O1 ; A2 --> O1
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

# Re-export the canonical ContextPackage from a2a_schemas (SSoT).
# Local aliasing/redefinition is prohibited — a2a_schemas is the single source.
from zephyr.shared.protocols.a2a.a2a_schemas import ContextPackage  # noqa: F401

__all__ = [
    "ContextPackage",
    "ContextPackageBuilder",
    "EscalationContext",
]


class EscalationContext(BaseModel):
    context_id: str
    task_id: str = ""
    reason: str = ""
    evidence_chain: list[str] = Field(default_factory=list)
    try_trace: list[dict] = Field(default_factory=list)
    escalated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    escalation_level: str = ""
    suggested_action: str = ""


class ContextPackageBuilder:
    def build(
        self, task_id: str, reason: str, level: str, evidence: list[str] = None, trace: list[dict] = None
    ) -> EscalationContext:
        return EscalationContext(
            context_id=f"CTX-{task_id}",
            task_id=task_id,
            reason=reason,
            escalation_level=level,
            evidence_chain=evidence or [],
            try_trace=trace or [],
        )
