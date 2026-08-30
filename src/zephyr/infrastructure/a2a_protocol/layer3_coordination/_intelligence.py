# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination._intelligence
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_collusion_detector; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_blame_attribution; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_causal_trace; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_behavior_fingerprint; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_knowledge_distill; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_latent_comm; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_cross_agent_semantic_flow
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
Re-export bridge for layer3_coordination intelligence symbols.

Aggregates 19 symbols from 7 source modules to preserve backward compatibility
for ``from layer3_coordination._intelligence import ...`` consumers.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: _intelligence.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 A2ABehaviorFingerprint, A2ABlameAttribution, A2ACausalTrace, A2ACollusionDe…
#   desc: __init__ import L0；__all__ 19 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（19 符号）
#   name_en: __all__
#   intro: A2ABehaviorFingerprint, A2ABlameAttribution, A2ACausalTrace, A2ACollusionDetect…
#   downstream: zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_behavior_fingerprint import (
    A2ABehaviorFingerprint,
    BehaviorFingerprint,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_blame_attribution import (
    A2ABlameAttribution,
    BlameItem,
    BlameReport,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_causal_trace import (
    A2ACausalTrace,
    CausalEdge,
    CausalGraph,
    CausalNode,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_collusion_detector import (
    A2ACollusionDetector,
    CollusionFinding,
    CollusionReport,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_cross_agent_semantic_flow import (
    CrossAgentSemanticFlow,
    SemanticFlow,
    SemanticFlowNode,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_knowledge_distill import (
    A2AKnowledgeDistill,
    DistilledKnowledge,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_latent_comm import (
    A2ALatentComm,
    LatentCommSignal,
)

__all__ = [
    "A2ABehaviorFingerprint",
    "A2ABlameAttribution",
    "A2ACausalTrace",
    "A2ACollusionDetector",
    "A2AKnowledgeDistill",
    "A2ALatentComm",
    "BehaviorFingerprint",
    "BlameItem",
    "BlameReport",
    "CausalEdge",
    "CausalGraph",
    "CausalNode",
    "CollusionFinding",
    "CollusionReport",
    "CrossAgentSemanticFlow",
    "DistilledKnowledge",
    "LatentCommSignal",
    "SemanticFlow",
    "SemanticFlowNode",
]
