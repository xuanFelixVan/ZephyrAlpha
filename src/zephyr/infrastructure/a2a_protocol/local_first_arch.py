# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.local_first_arch
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-018;MOD-INF-022
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Agent间通信;冲突解决;四级委托约束
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md;src/zephyr/infrastructure/runtime_integration/a2a_protocol/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CommunicationError;ConflictError;DelegationError
# [TESTS] tests/test_a2a_protocol/
# [A_module] module_id=MOD-INF_local_first_arch | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
