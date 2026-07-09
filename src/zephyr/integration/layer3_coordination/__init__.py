# [A_module] module_id=MOD-ORC_layer3_coordination | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export from authoritative shared location
# DM-384: shared layer3_coordination now exports Protocol interfaces and data contracts only.
# Concrete implementations are in zephyr.infrastructure.a2a_protocol.layer3_coordination.
# 5.93.6 修复：import * → 显式导入
from zephyr.shared.protocols.a2a.layer3_coordination import (
    A2AGovernanceRecord,
    AgentRole,
    DispatchedTask,
    GovernanceAdapterProtocol,
    MergeStrategy,
    Phase4HoldProtocol,
    ResultMerge,
    TaskDispatchProtocol,
    TaskStatus,
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
