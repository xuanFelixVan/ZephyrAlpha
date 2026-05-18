# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.market.signal_degradation_warning

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l03_signal_generation; l04_risk_management; l05_portfolio_construction

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# ==== BEGIN CODGEN:CTR-ERR-003 ====
from dataclasses import dataclass, field

from typing import List
from typing import Optional

from zephyr.shared.contracts.core.trace_context import TraceContext

@dataclass(frozen=True)
class SignalDegradationWarning:
    degradation_level: str
    idempotency_key: str
    reason: str
    suggested_action: str
    warning_id: str
    affected_factor_ids: List[str] = field(default_factory=list)
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-ERR-003 ====
