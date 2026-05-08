"""Escalation Metrics — D-022-07 指标收集器: 升级率/误升级率/响应延迟。"""
from __future__ import annotations
import time

class EscalationMetrics:
    def __init__(self):
        self._total_evals=0
        self._blocks=0
        self._auto_guards=0
        self._autonomous=0
        self._false_positives=0
        self._latencies:list[float]=[]

    def record(self, level:str, latency_s:float, was_false_positive:bool=False):
        self._total_evals+=1
        if level=="blocked":self._blocks+=1
        elif level=="auto_guard":self._auto_guards+=1
        else:self._autonomous+=1
        self._latencies.append(latency_s)
        if was_false_positive:self._false_positives+=1

    def escalation_rate(self)->float:
        return self._blocks/max(1,self._total_evals)

    def avg_latency(self)->float:
        return sum(self._latencies)/max(1,len(self._latencies))

    def false_positive_rate(self)->float:
        return self._false_positives/max(1,self._blocks)
