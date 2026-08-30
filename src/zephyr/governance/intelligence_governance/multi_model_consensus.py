# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.intelligence_governance.multi_model_consensus
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.intelligence_governance.__init__
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
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: reason 参数
#   fields: 参数 reason，类型注解 str
#   code: multi_model_consensus.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① escalate_to_owner
#   name_en: escalate_to_owner
#   intro: escalate_to_owner(reason) 源码 L66-L67
#   desc: 源码 L66-L67
#   inputs: reason
#   outputs: str
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
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
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum


class ConsensusProtocol(str, Enum):
    MAJORITY = "Majority"
    WEIGHTED = "Weighted"
    UNANIMOUS = "Unanimous"


class DebateRound(str, Enum):
    R1_PROPOSAL = "R1_模型A解答"
    R2_CHALLENGE = "R2_模型B挑战"
    R3_REBUTTAL = "R3_模型A反驳"


def escalate_to_owner(reason: str) -> str:
    return f"ESCALATED: {reason} -> Owner"
