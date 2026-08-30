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
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Re-export bridge for layer3_coordination consensus symbols.

Aggregates 17 symbols from 5 source modules to preserve backward compatibility
for ``from layer3_coordination._consensus import ...`` consumers.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: _consensus.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 A2ADebate, A2ANegotiation, A2ASaga, A2AVoting, A2AWorkSteal, DebatePhase, D…
#   desc: __init__ import L0；__all__ 17 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（17 符号）
#   name_en: __all__
#   intro: A2ADebate, A2ANegotiation, A2ASaga, A2AVoting, A2AWorkSteal, DebatePhase, Debat…
#   downstream: zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
