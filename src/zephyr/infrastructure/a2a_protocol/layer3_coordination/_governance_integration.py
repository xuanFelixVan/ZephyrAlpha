# [A_module] module_id=MOD-INF__governance_integration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination._governance_integration
# [INVARIANTS] backward_compat: all exports must remain available from layer3_coordination
# [MODIFY-GUARD] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [CONSUMERS] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.infrastructure.a2a_protocol.layer3_coordination"

from .a2a_dashboard import A2ADashboard, DashboardPanel
from .a2a_governance_adapter import A2AGovernanceAdapter, GovernanceCheckResult
from .a2a_tracing import A2ATracing, Span
from .a2a_protocol_gateway import A2AProtocolGateway, GatewayResult
from .a2a_frame_negotiation import A2AFrameNegotiation, FrameOffer, NegotiatedFrame
from .spec_sync import SpecSync, SpecSyncEntry
from .a2a_formal_verification import A2AFormalVerification, VerificationStatus, PropertyCheck, VerificationReport
