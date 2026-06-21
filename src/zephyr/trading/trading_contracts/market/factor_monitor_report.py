# [A_module] module_id=MOD-UNK_factor_monitor_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md

# [MODULE] zephyr.execution.trading.trading_contracts.market.factor_monitor_report

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] factor; pf_core

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# ==== BEGIN CODGEN:CTR-P1-001 ====

from dataclasses import dataclass

@dataclass(frozen=True)
class FactorMonitorReport:
    factor_id: str
    evaluation_date: str
    ic_mean: float
    ic_std: float
    ic_ir: float
    rank_ic: float
    is_effective: bool
    decay_alert: bool
    idempotency_key: str
    evaluation_window: int = 63
    schema_version: str = "1.0"
    half_life_days: int | None = None


# ==== END CODGEN:CTR-P1-001 ====
