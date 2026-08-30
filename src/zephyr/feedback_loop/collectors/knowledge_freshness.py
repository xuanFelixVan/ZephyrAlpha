# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.collectors.knowledge_freshness
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Knowledge Freshness — v0.5.0 R47

Blindspot: Stale KB entries have same weight as fresh ones.
Risk: R47 — Outdated knowledge misguides current diagnosis.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: knowledge_freshness.py
# 层: 算法
# - id: A1
#   name_zh: ① KnowledgeFreshness
#   name_en: KnowledgeFreshness
#   intro: class KnowledgeFreshness 源码 L56-L61
#   desc: 公共方法（定义序）: score；源码 L56-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: KnowledgeFreshness
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import time
from dataclasses import dataclass, field


@dataclass
class KnowledgeFreshness:
    entries: dict[str, float] = field(default_factory=dict)

    def score(self, entry_id: str, created_at: float) -> float:
        age_days = (time.time() - created_at) / 86400.0
        return max(0.0, 1.0 - age_days / 90.0)
