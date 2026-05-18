# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §8

# [MODULE] zephyr.escalation_engine.drift_detector

# [INVARIANTS] SSoT=zephyr.drift_detector(MOD-INF-023);本文件为兼容别名;API保持不变

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine.__init__

# [STABILITY] frozen

# [SAFETY] L

# [AI_AUTONOMY] immutable_core

# [ERROR_CONTRACT] establish_baseline();detect()->float;is_drifting()->bool

# [TESTS]

"""Drift Detector — 兼容别名，SSoT已迁移至 zephyr.drift_detector (MOD-INF-023).

原欧氏距离基线检测已被MOD-INF-023的39+检测器超集覆盖。
本模块保留API兼容性，内部实现保持独立（SSoT为异步扫描架构，不适合同步调用）。
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
