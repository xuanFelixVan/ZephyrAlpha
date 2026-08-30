# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.fault_tolerance.network_partition
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
网络分区容忍（CT-NETWORK-PARTITION）——CAP定理CP优先+脑裂检测+quorum write。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: network_partition.py
# 层: 算法
# - id: A1
#   name_zh: ① NetworkPartitionGuard
#   name_en: NetworkPartitionGuard
#   intro: class NetworkPartitionGuard 源码 L49-L62
#   desc: 公共方法（定义序）: detect_partition, should_quorum_write, partitioned；源码 L49-L62
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: NetworkPartitionGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


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
