# [BLUEPRINT] MOD-MKT_DATA | (pending)
# [MODULE] zephyr.market_data
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.shared.contracts.market_data
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-MKT_DATA | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from zephyr.shared.contracts.market_data import NormalizedMarketData

__all__ = ["NormalizedMarketData"]
