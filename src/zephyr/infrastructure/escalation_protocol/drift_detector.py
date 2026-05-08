"""Drift Detector — v0.6.0 Agent行为漂移检测: 基线建立+偏离度量+auto_guard触发。"""
from __future__ import annotations
import math

class DriftDetector:
    def __init__(self):
        self._baseline:dict[str,float]={}
        self._history:list[dict] = []

    def establish_baseline(self, metrics:dict[str,float]):
        self._baseline=dict(metrics)

    def detect(self, current:dict[str,float])->float:
        if not self._baseline:return 0.0
        diffs=[abs(current.get(k,0.0)-v) for k,v in self._baseline.items()]
        return math.sqrt(sum(d*d for d in diffs))/max(1,len(diffs))

    def is_drifting(self, current:dict[str,float], threshold:float=0.3)->bool:
        return self.detect(current)>threshold
