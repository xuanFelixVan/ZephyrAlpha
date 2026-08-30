# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.staleness_manager
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
staleness_manager.py — 全局过期检测 (DD112, TASK-019)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: staleness_manager.py
# 层: 算法
# - id: A1
#   name_zh: ① StalenessManager
#   name_en: StalenessManager
#   intro: per-KE TTL 定时任务 + 批量标记 legacy (DD112).
#   desc: per-KE TTL 定时任务 + 批量标记 legacy (DD112).；公共方法（定义序）: check；源码 L61-L69
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: StalenessManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class StalenessReport:
    ke_id: str
    age_days: float
    ttl_days: float
    exceeded: bool
    proposed_action: str  # "mark_legacy" | "rebuild_embedding" | "delete"


class StalenessManager:
    """per-KE TTL 定时任务 + 批量标记 legacy (DD112)."""

    def check(self, ke_id: str, age_days: float, ttl_days: float = 90) -> StalenessReport:
        exceeded = age_days > ttl_days
        action = "mark_legacy" if exceeded else "active"
        return StalenessReport(
            ke_id=ke_id, age_days=age_days, ttl_days=ttl_days, exceeded=exceeded, proposed_action=action
        )
