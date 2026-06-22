# [A_module] module_id=MOD-GOV_realtime_streaming | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-062 | docs/03_modules/_domain-governance/blueprint.md | §

# [MODULE] zephyr.governance.realtime_streaming

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations

from enum import Enum


class PipelineMode(str, Enum):
    BATCH = "Batch"
    STREAM = "Stream"


CONNECTION_POOL_MIN: int = 10
FIFO_MAX_DEPTH: int = 1000
DISCONNECT_ALERT_SECONDS: int = 120
BACKPRESSURE_THRESHOLD: int = 1000
