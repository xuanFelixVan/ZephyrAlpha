# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination._security_and_economics
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_economics; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_forgetting; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_delegation_chain; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_idempotency; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_temporal_admission; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_idle_guard; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_red_team; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_security; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_anomaly_detector; zephyr.infrastructure.a2a_protocol.layer3_coordination.session_smuggling_defense
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
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Re-export bridge for layer3_coordination security and economics symbols.

Aggregates 22 symbols from 10 source modules to preserve backward compatibility
for ``from layer3_coordination._security_and_economics import ...`` consumers.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: _security_and_economics.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 A2AAnomalyDetector, A2ADelegationChain, A2AEconomics, A2AForgetting, A2AIde…
#   desc: __init__ import L0；__all__ 22 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（22 符号）
#   name_en: __all__
#   intro: A2AAnomalyDetector, A2ADelegationChain, A2AEconomics, A2AForgetting, A2AIdempot…
#   downstream: zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
