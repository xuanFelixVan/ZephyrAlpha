# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.network_partition
# [DOMAIN] D-GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_orchestration.__init__
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
# [A_module] module_id=MOD-GOV_network_partition | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""网络分区容忍（CT-NETWORK-PARTITION）——CAP定理CP优先+脑裂检测+quorum write。"""

from __future__ import annotations


class NetworkPartitionGuard:
    def __init__(self):
        self._partitioned = False

    def detect_partition(self, can_reach_peers: bool) -> bool:
        self._partitioned = not can_reach_peers
        return self._partitioned

    def should_quorum_write(self, peer_count: int, reachable: int) -> bool:
        return reachable > peer_count // 2

    @property
    def partitioned(self) -> bool:
        return self._partitioned
