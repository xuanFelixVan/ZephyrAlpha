# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.fault_tolerance.network_partition
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_network_partition | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""网络分区容忍（CT-NETWORK-PARTITION）——CAP定理CP优先+脑裂检测+quorum write。"""


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
