# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.market.signal_degradation_warning
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] signal; risk; pf_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_signal_degradation_warning | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ==== BEGIN CODGEN:CTR-ERR-003 ====
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SignalDegradationWarning:
    degradation_level: str
    idempotency_key: str
    reason: str
    suggested_action: str
    warning_id: str
    affected_factor_ids: list[str] = field(default_factory=list)
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-ERR-003 ====
