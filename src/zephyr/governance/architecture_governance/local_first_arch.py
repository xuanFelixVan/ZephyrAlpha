# [BLUEPRINT] SRC-015 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.architecture_governance.local_first_arch
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.architecture_governance.__init__
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
# [A_module] module_id=MOD-GOV_local_first_arch | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ComputeLocation(str, Enum):
    LOCAL = "LOCAL"
    CLOUD_BACKFILL = "CLOUD_BACKFILL"


class LocalFirstPolicy(BaseModel):
    all_compute: ComputeLocation = ComputeLocation.LOCAL
    websocket_dep: str = "唯一远程依赖——仅WebSocket行情"
    cloud_role: str = "backfill only — 灾备恢复用"
    zero_cloud_dep: bool = True

    def is_local_first(self) -> bool:
        return self.all_compute is ComputeLocation.LOCAL and self.zero_cloud_dep


LOCAL_FIRST = LocalFirstPolicy()
