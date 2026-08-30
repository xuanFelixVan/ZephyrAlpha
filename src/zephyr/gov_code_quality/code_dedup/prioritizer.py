# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.prioritizer
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/orchestrator/test_prioritizer.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
修复优先级排序器 — 置信度×Impact×适配性 三因子排序.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: prioritizer.py
# 层: 算法
# - id: A1
#   name_zh: ① Prioritizer
#   name_en: Prioritizer
#   intro: 三因子修复优先级排序.
#   desc: 三因子修复优先级排序.；公共方法（定义序）: rank；源码 L63-L85
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: Prioritizer
#   downstream: tests/governance/orchestrator/test_prioritizer.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class PrioritizedFix:
    dup_group_id: str = ""
    confidence: float = 0.0
    impact_scope: int = 0
    suitability: int = 0
    priority_score: float = 0.0
    rank: int = 0
    action: str = ""


class Prioritizer:
    """三因子修复优先级排序."""

    def rank(self, candidates: list[tuple[str, float, int, int]]) -> list[PrioritizedFix]:
        """排序: score = confidence * 0.4 × impact * 0.3 × suitability * 0.3."""
        results: list[PrioritizedFix] = []
        for dup_id, conf, impact, suit in candidates:
            score = (conf * 0.4) + (min(impact, 100) / 100 * 0.3) + (suit / 100 * 0.3)
            action = "AUTO_FIX" if score >= 0.8 else "SUGGEST" if score >= 0.5 else "INFORM"
            results.append(
                PrioritizedFix(
                    dup_group_id=dup_id,
                    confidence=conf,
                    impact_scope=impact,
                    suitability=suit,
                    priority_score=round(score, 3),
                    action=action,
                )
            )
        results.sort(key=lambda x: x.priority_score, reverse=True)
        for i, r in enumerate(results):
            r.rank = i + 1
        return results
