"""Rule Canary Manager — v0.10.0 规则金丝雀: 1%用户先上新规则→A/B对比→rollback。"""
from __future__ import annotations

class RuleCanaryManager:
    def __init__(self):
        self._canary_weight=0.01
        self._baseline_metrics:dict={}
        self._canary_metrics:dict={}

    def set_baseline(self, metrics:dict):
        self._baseline_metrics=metrics

    def set_canary_metrics(self, metrics:dict):
        self._canary_metrics=metrics

    def should_rollback(self)->bool:
        baseline_err=self._baseline_metrics.get("false_positive_rate",0)
        canary_err=self._canary_metrics.get("false_positive_rate",0)
        return canary_err>baseline_err*2.0

    def promote(self)->None:
        self._canary_weight=1.0
