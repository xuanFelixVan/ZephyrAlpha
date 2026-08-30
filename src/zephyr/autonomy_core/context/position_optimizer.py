# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.position_optimizer
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
position_optimizer.py — 位置优化 (DD104, TASK-019)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: position_optimizer.py
# 层: 算法
# - id: A1
#   name_zh: ① PositionOptimizer
#   name_en: PositionOptimizer
#   intro: Order KE 优先注入前 20%, avoid truncation tail (DD104).
#   desc: Order KE 优先注入前 20%, avoid truncation tail (DD104).；公共方法（定义序）: optimize_order；源码 L60-L69
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: PositionOptimizer
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class PositionScore:
    section_name: str
    page: int
    priority: float
    is_optimal: bool


class PositionOptimizer:
    """Order KE 优先注入前 20%, avoid truncation tail (DD104)."""

    def optimize_order(self, ke_items: list[tuple[str, float]]) -> list[PositionScore]:
        ranked = sorted(ke_items, key=lambda x: x[1], reverse=True)
        total = len(ranked)
        return [
            PositionScore(section_name=k, page=i, priority=s, is_optimal=i < total * 0.2)
            for i, (k, s) in enumerate(ranked)
        ]
