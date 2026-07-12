# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination._consensus
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_debate; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_voting; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_negotiation; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_saga; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_work_steal
# [CONSUMERS] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] backward_compat: all exports must remain available from layer3_coordination
# [MODIFY-GUARD] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.infrastructure.a2a_protocol.layer3_coordination"
# [A_module] module_id=MOD-INF__consensus | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export bridge for layer3_coordination consensus symbols.

Aggregates 17 symbols from 5 source modules to preserve backward compatibility
for ``from layer3_coordination._consensus import ...`` consumers.
"""

from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_debate import (
    A2ADebate,
    DebatePhase,
    DebateResult,
    DebateRound,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_negotiation import (
    A2ANegotiation,
    NegotiationOffer,
    NegotiationResult,
    NegotiationStatus,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_saga import (
    A2ASaga,
    SagaResult,
    SagaStatus,
    SagaStep,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_voting import (
    A2AVoting,
    VoteAction,
    VotingResult,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_work_steal import (
    A2AWorkSteal,
    TaskQueue,
)

__all__ = [
    "A2ADebate",
    "A2ANegotiation",
    "A2ASaga",
    "A2AVoting",
    "A2AWorkSteal",
    "DebatePhase",
    "DebateResult",
    "DebateRound",
    "NegotiationOffer",
    "NegotiationResult",
    "NegotiationStatus",
    "SagaResult",
    "SagaStatus",
    "SagaStep",
    "TaskQueue",
    "VoteAction",
    "VotingResult",
]
