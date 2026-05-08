"""金丝雀发布管理器（CT-CANARY）——权重分流+指标对比+自动回滚。"""

from __future__ import annotations

class CanaryManager:
    def __init__(self):
        self._canary_weight: float = 0.1

    def set_weight(self, weight: float) -> None:
        self._canary_weight = min(1.0, max(0.0, weight))

    def should_rollback(self, error_rate: float, baseline: float) -> bool:
        return error_rate > baseline * 2.0

    def promote(self) -> None:
        self._canary_weight = 1.0
