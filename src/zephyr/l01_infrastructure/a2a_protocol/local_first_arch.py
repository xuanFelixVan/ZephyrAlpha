# [BLUEPRINT] MOD-INF-025 | docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md
# [MODULE] zephyr.l01_infrastructure.a2a_protocol
# [INVARIANTS] Agent间通信;冲突解决;四级委托约束
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md;src/zephyr/l01_infrastructure/a2a_protocol/__init__.py
# [CONSUMERS] MOD-INF-027;MOD-INF-018;MOD-INF-022
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CommunicationError;ConflictError;DelegationError
# [TESTS] tests/test_a2a_protocol/

from __future__ import annotations

from enum import Enum
from typing import Optional

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
        return self.all_compute == ComputeLocation.LOCAL and self.zero_cloud_dep


LOCAL_FIRST = LocalFirstPolicy()
