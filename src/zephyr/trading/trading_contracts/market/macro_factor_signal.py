# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.market.macro_factor_signal
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] factor
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_macro_factor_signal | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:CTR-P1-002 ====

from dataclasses import dataclass


@dataclass(frozen=True)
class MacroFactorSignal:
    factor_id: str
    as_of_date: str
    macro_regime: str
    signal_value: float
    data_source: str
    release_lag_days: int
    idempotency_key: str
    confidence: float = 1.0
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-002 ====
