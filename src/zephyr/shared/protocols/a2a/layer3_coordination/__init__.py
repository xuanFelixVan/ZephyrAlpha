# [A_module] module_id=MOD-GOV-init | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols.a2a.layer3_coordination
# [INVARIANTS] Protocol interfaces and data contracts only; no imports from zephyr.infrastructure or zephyr.integration
# [MODIFY-GUARD] no concrete implementations; no cross-domain imports
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] zephyr.integration.agent_communication.layer3_coordination
# [ERROR_CONTRACT] import errors only
# [TESTS] tests/test_shared_protocols.py
# [TTL] permanent

"""
A2A Layer3 Coordination — shared Protocol interfaces and data contracts.

DM-384: Removed facade delegation to zephyr.infrastructure.a2a_protocol.
This package now contains only Protocol interfaces and data contracts, consistent
with the shared layer invariant of no cross-domain imports.

Concrete implementations live in zephyr.infrastructure.a2a_protocol.layer3_coordination.
Consumers that need concrete implementations should import from infrastructure directly.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: AgentRole, DispatchedTask, MergeStrategy, ResultMerge, TaskDispatchPr…
#   code: __init__.py import L51
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 A2AGovernanceRecord, AgentRole, DispatchedTask, GovernanceAdapterProtocol,…
#   desc: __init__ import L51；__all__ 9 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（9 符号）
#   name_en: __all__
#   intro: A2AGovernanceRecord, AgentRole, DispatchedTask, GovernanceAdapterProtocol, Merg…
#   downstream: zephyr.integration.agent_communication.layer3_coordination
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.protocols.a2a.a2a_coordination import (
    AgentRole,
    DispatchedTask,
    MergeStrategy,
    ResultMerge,
    TaskDispatchProtocol,
    TaskStatus,
)
from zephyr.shared.protocols.a2a.a2a_governance import (
    A2AGovernanceRecord,
    GovernanceAdapterProtocol,
    Phase4HoldProtocol,
)

__all__ = [
    "A2AGovernanceRecord",
    "AgentRole",
    "DispatchedTask",
    "GovernanceAdapterProtocol",
    "MergeStrategy",
    "Phase4HoldProtocol",
    "ResultMerge",
    "TaskDispatchProtocol",
    "TaskStatus",
]

__version__ = "0.10.0"
