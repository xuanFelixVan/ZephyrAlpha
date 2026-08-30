# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols.a2a.a2a_governance
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.shared.protocols.a2a; zephyr.infrastructure.a2a_protocol
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] no imports from zephyr.infrastructure or zephyr.trading; Protocol interfaces and data contracts only
# [MODIFY-GUARD] interface changes require consumer audit
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Protocol violations caught at type-check time
# [TESTS] tests/test_shared_protocols.py
# [A_module] module_id=MOD-SHARED-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
A2A Governance — shared interface definitions for governance layer.

Data contracts and Protocol interfaces for A2A governance:
  - A2AGovernanceRecord: audit record for agent-pair governance decisions
  - GovernanceAdapterProtocol: interface for governance verification
  - Phase4HoldProtocol: interface for phase hold checks

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: a2a_governance.py
# 层: 算法
# - id: A1
#   name_zh: ① GovernanceAdapterProtocol
#   name_en: GovernanceAdapterProtocol
#   intro: Protocol interface for A2A governance verification.
#   desc: Protocol interface for A2A governance verification. Any class that provides verify_pair,…；公共方法（定义序）: verify_p…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② Phase4HoldProtocol
#   name_en: Phase4HoldProtocol
#   intro: Protocol interface for A2A Phase 4 hold checks.
#   desc: Protocol interface for A2A Phase 4 hold checks.；公共方法（定义序）: check, can_proceed, is_hold_active；源码 L96-L103
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: GovernanceAdapterProtocol, Phase4HoldProtocol
#   downstream: zephyr.shared.protocols.a2a; zephyr.infrastructure.a2a_protocol
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class A2AGovernanceRecord:
    """Audit record for A2A agent-pair governance decisions."""

    agent_pair: tuple[str, str]
    action: str
    granted: bool = False
    escalation_level: str = ""
    audit_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class GovernanceAdapterProtocol(Protocol):
    """Protocol interface for A2A governance verification.

    Any class that provides verify_pair, escalate_if_needed, and
    audit_communication satisfies this protocol.
    """

    def verify_pair(self, agent_a: str, agent_b: str, content: str = "") -> A2AGovernanceRecord: ...

    def escalate_if_needed(self, record: A2AGovernanceRecord, severity: str = "WARN") -> A2AGovernanceRecord: ...

    def audit_communication(self, record: A2AGovernanceRecord, session_id: str = "") -> A2AGovernanceRecord: ...


@runtime_checkable
class Phase4HoldProtocol(Protocol):
    """Protocol interface for A2A Phase 4 hold checks."""

    def check(self) -> dict[str, Any]: ...

    def can_proceed(self, current_phase: str) -> bool: ...

    def is_hold_active(self) -> bool: ...


__all__ = [
    "A2AGovernanceRecord",
    "GovernanceAdapterProtocol",
    "Phase4HoldProtocol",
]
