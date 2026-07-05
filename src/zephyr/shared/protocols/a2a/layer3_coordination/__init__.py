# [A_module] module_id=MOD-SHR_layer3_coordination | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

"""A2A Layer3 Coordination — shared Protocol interfaces and data contracts.

DM-384: Removed facade delegation to zephyr.infrastructure.a2a_protocol.
This package now contains only Protocol interfaces and data contracts, consistent
with the shared layer invariant of no cross-domain imports.

Concrete implementations live in zephyr.infrastructure.a2a_protocol.layer3_coordination.
Consumers that need concrete implementations should import from infrastructure directly.
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
