# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination._governance_integration
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_dashboard; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_governance_adapter; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_tracing; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_gateway; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_frame_negotiation; zephyr.infrastructure.a2a_protocol.layer3_coordination.spec_sync; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_formal_verification
# [CONSUMERS] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] backward_compat: all exports must remain available from layer3_coordination
# [MODIFY-GUARD] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.infrastructure.a2a_protocol.layer3_coordination"
# [A_module] module_id=MOD-INF__governance_integration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export bridge for layer3_coordination governance integration symbols.

Aggregates 17 symbols from 7 source modules to preserve backward compatibility
for ``from layer3_coordination._governance_integration import ...`` consumers.
"""

from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_dashboard import (
    A2ADashboard,
    DashboardPanel,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_formal_verification import (
    A2AFormalVerification,
    PropertyCheck,
    VerificationReport,
    VerificationStatus,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_frame_negotiation import (
    A2AFrameNegotiation,
    FrameOffer,
    NegotiatedFrame,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_governance_adapter import (
    A2AGovernanceAdapter,
    GovernanceCheckResult,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_gateway import (
    A2AProtocolGateway,
    GatewayResult,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_tracing import (
    A2ATracing,
    Span,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.spec_sync import (
    SpecSync,
    SpecSyncEntry,
)

__all__ = [
    "A2ADashboard",
    "A2AFormalVerification",
    "A2AFrameNegotiation",
    "A2AGovernanceAdapter",
    "A2AProtocolGateway",
    "A2ATracing",
    "DashboardPanel",
    "FrameOffer",
    "GatewayResult",
    "GovernanceCheckResult",
    "NegotiatedFrame",
    "PropertyCheck",
    "Span",
    "SpecSync",
    "SpecSyncEntry",
    "VerificationReport",
    "VerificationStatus",
]
