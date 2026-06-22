# [A_module] module_id=MOD-INF__security_and_economics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination._security_and_economics
# [INVARIANTS] backward_compat: all exports must remain available from layer3_coordination
# [MODIFY-GUARD] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [CONSUMERS] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.infrastructure.a2a_protocol.layer3_coordination"
"""Re-export bridge for layer3_coordination security and economics symbols.

Aggregates 22 symbols from 10 source modules to preserve backward compatibility
for ``from layer3_coordination._security_and_economics import ...`` consumers.
"""

from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_anomaly_detector import (
    A2AAnomalyDetector,
    AnomalyLevel,
    AnomalyRecord,
    MetricBaseline,
    MetricKey,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_delegation_chain import (
    A2ADelegationChain,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_economics import (
    A2AEconomics,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_forgetting import (
    A2AForgetting,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_idempotency import (
    A2AIdempotency,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_idle_guard import (
    A2AIdleGuard,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_red_team import (
    A2ARedTeam,
    AttackCategory,
    AttackSeverity,
    AttackVector,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_security import (
    A2ASecurityReport,
    A2ASecurityScanner,
    SecurityFinding,
    SecurityVerdict,
    ThreatCategory,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_temporal_admission import (
    A2ATemporalAdmission,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.session_smuggling_defense import (
    SessionSmugglingDefense,
    SmugglingAttempt,
)

__all__ = [
    "A2AAnomalyDetector",
    "A2ADelegationChain",
    "A2AEconomics",
    "A2AForgetting",
    "A2AIdempotency",
    "A2AIdleGuard",
    "A2ARedTeam",
    "A2ASecurityReport",
    "A2ASecurityScanner",
    "A2ATemporalAdmission",
    "AnomalyLevel",
    "AnomalyRecord",
    "AttackCategory",
    "AttackSeverity",
    "AttackVector",
    "MetricBaseline",
    "MetricKey",
    "SecurityFinding",
    "SecurityVerdict",
    "SessionSmugglingDefense",
    "SmugglingAttempt",
    "ThreatCategory",
]
