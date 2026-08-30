# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §8
# [MODULE] zephyr.gov_drift.drift_detector
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SSoT=zephyr.gov_drift(MOD-INF-023);本文件为兼容别名;API保持不变
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] establish_baseline();detect()->float;is_drifting()->bool
# [TESTS]
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drift Detector — 兼容别名，SSoT已迁移至 zephyr.gov_drift (MOD-INF-023).

原欧氏距离基线检测已被MOD-INF-023的39+检测器超集覆盖。
本模块保留API兼容性，内部实现保持独立（SSoT为异步扫描架构，不适合同步调用）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: drift_event 参数
#   fields: 参数 drift_event，类型注解 object
#   code: drift_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: strategy 参数
#   fields: 参数 strategy，类型注解 str | None
#   code: drift_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DriftDetector
#   name_en: DriftDetector
#   intro: class DriftDetector 源码 L73-L117
#   desc: 公共方法（定义序）: baseline, establish_baseline, detect, is_drifting；源码 L73-L117
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② trigger_recovery
#   name_en: trigger_recovery
#   intro: trigger_recovery(drift_event, strategy) 源码 L120-L121
#   desc: 源码 L120-L121
#   inputs: drift_event strategy
#   outputs: bool
# 层: 输出
# - id: O1
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.governance.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import math


class DriftDetector:
    def __init__(self):
        self._baseline: dict[str, float] = {}
        self._history: list[dict] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def baseline(self) -> dict[str, float]:
        """只读：baseline（Stage 4 公共化）。"""
        return self._baseline

    @baseline.setter
    def baseline(self, value):
        """写入：baseline（Stage 4 公共化）。"""
        self._baseline = value

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

                from zephyr.shared.event_bus import EventBusBackpressure

                EventBusBackpressure().emit(
                    "drift_detected",
                    payload={
                        "timestamp": datetime.now(UTC).isoformat(),
                        "source_function": "DriftDetector.is_drifting",
                        "severity": "high",
                        "detail": f"Drift detected: score={self.detect(current):.4f} > threshold={threshold}",
                    },
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in drift_detector", exc_info=True)
        return drifting


def trigger_recovery(drift_event: object, strategy: str | None = None) -> bool:
    return True


__version__ = "1.0.0"
