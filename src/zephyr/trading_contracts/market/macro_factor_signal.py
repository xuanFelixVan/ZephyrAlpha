# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.market.macro_factor_signal

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l02_factor_computation

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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
