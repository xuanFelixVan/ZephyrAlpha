"""
Alert Precision Tracker — 告警精度退化检测 (盲点 #45)
特性：
  - Precision / Recall 计算
  - Precision < 30% → 自动抑制高误报规则
"""
import time
from collections import defaultdict
from typing import Any, Optional


class AlertPrecisionTracker:
    """
    告警精度追踪器 (盲点 #45)
    """

    PRECISION_MINIMUM = 0.30

    def __init__(self):
        self._true_positives: dict[str, int] = defaultdict(int)
        self._false_positives: dict[str, int] = defaultdict(int)
        self._false_negatives: dict[str, int] = defaultdict(int)

    def record_true_positive(self, rule_id: str):
        self._true_positives[rule_id] += 1

    def record_false_positive(self, rule_id: str):
        self._false_positives[rule_id] += 1

    def record_false_negative(self, rule_id: str):
        self._false_negatives[rule_id] += 1

    def get_metrics(self, rule_id: str) -> dict:
        tp = self._true_positives[rule_id]
        fp = self._false_positives[rule_id]
        fn = self._false_negatives[rule_id]

        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        suppressed = precision < self.PRECISION_MINIMUM

        return {
            "rule_id": rule_id,
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "suppressed": suppressed,
        }
