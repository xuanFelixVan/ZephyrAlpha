# [A_module] module_id=MOD-EXE_signal_degradation_warning | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md

# [MODULE] zephyr.execution.trading.trading_contracts.market.signal_degradation_warning

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] signal; risk; pf_core

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# ==== BEGIN CODGEN:CTR-ERR-003 ====
from dataclasses import dataclass, field

from typing import List
from typing import Optional

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

__all__ = ["SignalDegradationWarning"]
