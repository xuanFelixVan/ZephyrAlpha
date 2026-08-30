# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.cold_start_booster
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
cold_start_booster.py — 冷启动 (DD107, TASK-019)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: cold_start_booster.py
# 层: 算法
# - id: A1
#   name_zh: ① ColdStartBooster
#   name_en: ColdStartBooster
#   intro: build 发现 KE count < min_count -> 自动种子 KE (DD107).
#   desc: build 发现 KE count < min_count -> 自动种子 KE (DD107).；公共方法（定义序）: detect_cold_start；源码 L59-L67
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ColdStartBooster
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class ColdStartProfile:
    ke_count: int
    strategy: str  # "auto_seed" | "manual_tune"
    estimated_commit_count: int


class ColdStartBooster:
    """build 发现 KE count < min_count -> 自动种子 KE (DD107)."""

    def detect_cold_start(self, ke_count: int, min_count: int = 5) -> ColdStartProfile:
        if ke_count < min_count:
            return ColdStartProfile(
                ke_count=ke_count, strategy="auto_seed", estimated_commit_count=100 * (min_count - ke_count)
            )
        return ColdStartProfile(ke_count=ke_count, strategy="manual_tune", estimated_commit_count=0)
