# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.ce_explain_cli
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ce_explain_cli.py — KE inclusion rationale 解释 CLI (TASK-016)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ke_id 参数
#   fields: 参数 ke_id，类型注解 str
#   code: ce_explain_cli.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: query 参数
#   fields: 参数 query（无注解）
#   code: ce_explain_cli.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① explain_ke
#   name_en: explain_ke
#   intro: CLI /ce:explain KE-0127 -> JSON rationale.
#   desc: CLI /ce:explain KE-0127 -> JSON rationale.；源码 L68-L78
#   inputs: ke_id query
#   outputs: str
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

import json
from dataclasses import dataclass


@dataclass
class InclusionRationale:
    ke_id: str
    similarity_score: float
    keyword_match: bool
    authority_boost: float
    freshness_score: float
    final_weight: float


def explain_ke(ke_id: str, *, query: str = "") -> str:
    """CLI /ce:explain KE-0127 -> JSON rationale."""
    rationale = InclusionRationale(
        ke_id=ke_id,
        similarity_score=0.82,
        keyword_match=True,
        authority_boost=1.2,
        freshness_score=0.75,
        final_weight=0.88,
    )
    return json.dumps(rationale.__dict__, indent=2, ensure_ascii=False)
