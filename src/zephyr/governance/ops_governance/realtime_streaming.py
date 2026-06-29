# [BLUEPRINT] SRC-062 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.realtime_streaming
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.ops_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_realtime_streaming | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from enum import Enum


class PipelineMode(str, Enum):
    BATCH = "Batch"
    STREAM = "Stream"


CONNECTION_POOL_MIN: int = 10
FIFO_MAX_DEPTH: int = 1000
DISCONNECT_ALERT_SECONDS: int = 120
BACKPRESSURE_THRESHOLD: int = 1000
