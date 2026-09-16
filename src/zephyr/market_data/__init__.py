# [BLUEPRINT] MOD-MKT_DATA | (pending)
# [MODULE] zephyr.market_data
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.shared.contracts.market_data
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
# [A_module] module_id=MOD-MKT_DATA | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW] external: docs/03_modules/_domain_mkt_data/algo_flow/market_data__init__.yaml
"""

from zephyr.shared.contracts.market_data import NormalizedMarketData

__all__ = ["NormalizedMarketData"]

# NOTE(P1W16 2026-08-25): scaffold 注册器写入 eager import + 类名 append
# （#ARCH-228/235/238/241/245 同款 bug 复发），按各域包"纯模块名导出、
# 无导入无初始化逻辑"约定归一为模块名条目；NormalizedMarketData 既有导出行未动。
__all__.append("auction_data_manager")
