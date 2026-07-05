# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.data_governance.exchange_partition_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 交易所网络分区检测不可跳过;heartbeat必须验证
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_exchange_partition_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Exchange Partition Detector — v0.12.0 交易所网络分区检测器。
"""

from __future__ import annotations


class ExchangePartitionDetector:
    def __init__(self):
        self._known_exchanges: set[str] = set()

    def register(self, exchange: str):
        self._known_exchanges.add(exchange)

    def detect_partition(self, reachable: set[str]) -> list[str]:
        return list(self._known_exchanges - reachable)

    def is_partitioned(self, reachable: set[str]) -> bool:
        return len(self._known_exchanges) > 0 and len(reachable) < len(self._known_exchanges)
