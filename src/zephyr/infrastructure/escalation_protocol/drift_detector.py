"""Drift Detector — v0.6.0 Agent行为漂移检测: 基线建立+偏离度量+auto_guard触发。

SRC-0038: 副本文件 — 保持独立实现，待后续审核。
  此文件是一个完全独立的 DriftDetector 实现（欧氏距离基线检测），
  与真源 drift_detector/ 中的 DriftEngine 没有任何共享代码。
  两者语义相关但实现不同：此处侧重 Agent 行为基线 vs 真源侧重模块文件漂移。
  待后续确定是否统一到真源的 detector 注册机制中。
"""

from __future__ import annotations

import math


class DriftDetector:
    def __init__(self):
        self._baseline: dict[str, float] = {}
        self._history: list[dict] = []

    def establish_baseline(self, metrics: dict[str, float]):
        self._baseline = dict(metrics)

    def detect(self, current: dict[str, float]) -> float:
        if not self._baseline:
            return 0.0
        diffs = [abs(current.get(k, 0.0) - v) for k, v in self._baseline.items()]
        return math.sqrt(sum(d * d for d in diffs)) / max(1, len(diffs))

    def is_drifting(self, current: dict[str, float], threshold: float = 0.3) -> bool:
        return self.detect(current) > threshold
