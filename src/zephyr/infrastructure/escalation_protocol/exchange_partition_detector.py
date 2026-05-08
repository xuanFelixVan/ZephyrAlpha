"""Exchange Partition Detector — v0.12.0 交易所网络分区检测器。"""
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
