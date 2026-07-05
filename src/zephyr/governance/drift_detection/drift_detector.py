# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §8
# [MODULE] zephyr.governance.drift_detection.drift_detector
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] SSoT=zephyr.governance.drift_detection(MOD-INF-023);本文件为兼容别名;API保持不变
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] establish_baseline();detect()->float;is_drifting()->bool
# [TESTS]
# [A_module] module_id=MOD-RES_drift_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Drift Detector — 兼容别名，SSoT已迁移至 zephyr.governance.drift_detection (MOD-INF-023).

原欧氏距离基线检测已被MOD-INF-023的39+检测器超集覆盖。
本模块保留API兼容性，内部实现保持独立（SSoT为异步扫描架构，不适合同步调用）。
"""

from __future__ import annotations

import math
from typing import Any


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
        drifting = self.detect(current) > threshold
        if drifting:
            try:
                from datetime import UTC, datetime

                from zephyr.shared.events.event_bus import EventBusBackpressure

                EventBusBackpressure().emit(
                    "drift_detected",
                    payload={
                        "timestamp": datetime.now(UTC).isoformat(),
                        "source_function": "DriftDetector.is_drifting",
                        "severity": "high",
                        "detail": f"Drift detected: score={self.detect(current):.4f} > threshold={threshold}",
                    },
                )
            except Exception:
                pass
        return drifting


def trigger_recovery(drift_event: Any, strategy: str | None = None) -> bool:
    return True
