# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.capacity_calibrator
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.resource_optimization
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: history_window 参数
#   fields: 参数 history_window（无注解）
#   code: capacity_calibrator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CapacityCalibrator
#   name_en: CapacityCalibrator
#   intro: class CapacityCalibrator 源码 L63-L87
#   desc: 公共方法（定义序）: record, calibrate；源码 L63-L87
#   inputs: history_window
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CapacityCalibrator
#   downstream: zephyr.trading.resource_optimization
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class CalibrationResult:
    metric_name: str
    current_value: float
    calibrated_threshold: float
    confidence: float
    timestamp: str


class CapacityCalibrator:
    def __init__(self, history_window: int = 100) -> None:
        self._history_window = history_window
        self._measurements: dict[str, list[float]] = {}

    def record(self, metric_name: str, value: float) -> None:
        if metric_name not in self._measurements:
            self._measurements[metric_name] = []
        self._measurements[metric_name].append(value)
        if len(self._measurements[metric_name]) > self._history_window:
            self._measurements[metric_name] = self._measurements[metric_name][-self._history_window :]

    def calibrate(self, metric_name: str, percentile: float = 0.95) -> CalibrationResult:
        values = self._measurements.get(metric_name, [])
        if not values:
            return CalibrationResult(metric_name, 0.0, 0.0, 0.0, "")
        sorted_vals = sorted(values)
        idx = min(int(len(sorted_vals) * percentile), len(sorted_vals) - 1)
        return CalibrationResult(
            metric_name,
            sorted_vals[-1],
            sorted_vals[idx],
            percentile,
            datetime.now(UTC).isoformat(),
        )
