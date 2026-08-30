# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.numerical_stability_guard
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Numerical Stability Guard — v0.38.0 R475

Blindspot: Floating-point anomalies — NaN, Inf, -Inf, subnormal numbers,
catastrophic cancellation, integer overflow — propagate silently through
the FLE pipeline. EWMA accumulates NaN, thresholds compare Inf, z-scores
become undefined.

Risk: R475 — FLE makes decisions on corrupted numerical values; phantom
anomalies triggered by NaN; real anomalies hidden by Inf saturation.

Mitigation: Intercept all numeric metrics entering the pipeline. Classify:
NaN -> quarantine, Inf -> cap at sentinel, overflow -> flag for type upgrade.
Track numerical health score per metric stream.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: numerical_stability_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① NumericalStabilityGuard
#   name_en: NumericalStabilityGuard
#   intro: class NumericalStabilityGuard 源码 L79-L155
#   desc: 公共方法（定义序）: validate, is_stream_healthy, get_quarantine_summary, reset_metric；源码 L79-L155
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: NumericalStabilityGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum


class NumAnomaly(str, Enum):
    CLEAN = "CLEAN"
    NAN = "NAN"
    POS_INF = "POS_INF"
    NEG_INF = "NEG_INF"
    SUBNORMAL = "SUBNORMAL"
    OVERFLOW_SUSPECT = "OVERFLOW_SUSPECT"
    ZERO_DIVISION = "ZERO_DIVISION"


@dataclass
class NumericalStabilityGuard:
    nan_threshold_ratio: float = 0.01
    inf_sentinel: float = 1e308
    max_safe_float: float = 1e154

    quarantine: dict[str, list[dict]] = field(default_factory=dict)
    health_scores: dict[str, float] = field(default_factory=dict)
    total_checks: dict[str, int] = field(default_factory=dict)
    anomaly_counts: dict[str, dict[str, int]] = field(default_factory=dict)

    def validate(self, metric_name: str, value: float) -> dict:
        self.total_checks[metric_name] = self.total_checks.get(metric_name, 0) + 1

        classification = NumAnomaly.CLEAN
        sanitized = value

        if value != value:
            classification = NumAnomaly.NAN
            sanitized = 0.0
        elif value == float("inf"):
            classification = NumAnomaly.POS_INF
            sanitized = self.inf_sentinel
        elif value == float("-inf"):
            classification = NumAnomaly.NEG_INF
            sanitized = -self.inf_sentinel
        elif abs(value) > self.max_safe_float:
            classification = NumAnomaly.OVERFLOW_SUSPECT
            sanitized = math.copysign(self.max_safe_float, value)
        elif value != 0.0 and abs(value) < 1e-308:
            classification = NumAnomaly.SUBNORMAL
            sanitized = 0.0

        if classification is not NumAnomaly.CLEAN:
            if metric_name not in self.quarantine:
                self.quarantine[metric_name] = []
            self.quarantine[metric_name].append(
                {
                    "original": value,
                    "sanitized": sanitized,
                    "anomaly": classification.value,
                }
            )
            if metric_name not in self.anomaly_counts:
                self.anomaly_counts[metric_name] = {}
            self.anomaly_counts[metric_name][classification.value] = (
                self.anomaly_counts[metric_name].get(classification.value, 0) + 1
            )

        total = self.total_checks[metric_name]
        anomaly_total = sum(self.anomaly_counts.get(metric_name, {}).values())
        self.health_scores[metric_name] = max(0.0, 1.0 - anomaly_total / max(total, 1))

        return {
            "metric": metric_name,
            "classification": classification.value,
            "sanitized": sanitized,
            "health_score": round(self.health_scores[metric_name], 4),
        }

    def is_stream_healthy(self, metric_name: str) -> bool:
        return self.health_scores.get(metric_name, 1.0) >= 0.99

    def get_quarantine_summary(self) -> dict:
        return {
            name: {
                "total_checks": self.total_checks.get(name, 0),
                "anomaly_counts": dict(self.anomaly_counts.get(name, {})),
                "health_score": round(self.health_scores.get(name, 1.0), 4),
            }
            for name in self.total_checks
        }

    def reset_metric(self, metric_name: str) -> None:
        self.quarantine.pop(metric_name, None)
        self.total_checks.pop(metric_name, None)
        self.anomaly_counts.pop(metric_name, None)
        self.health_scores.pop(metric_name, None)
