# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.exchange_partition_detector

# [INVARIANTS] 交易所网络分区检测不可跳过;heartbeat必须验证

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Exchange Partition Detector — v0.12.0 交易所网络分区检测器。
"""
from __future__ import annotations

class ExchangePartitionDetector:
    def __init__(self):
        self._known_exchanges:set[str]=set()

    def register(self, exchange:str):
        self._known_exchanges.add(exchange)

    def detect_partition(self, reachable:set[str])->list[str]:
        return list(self._known_exchanges-reachable)

    def is_partitioned(self, reachable:set[str])->bool:
        return len(self._known_exchanges)>0 and len(reachable)<len(self._known_exchanges)
