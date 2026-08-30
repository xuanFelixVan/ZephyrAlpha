# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.cognitive.adaptive_param_tuning
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Adaptive Parameter Tuning — v0.37.0 R452

Blindspot: FLE detection/diagnosis thresholds are static; drift in
data distribution causes false positives or missed anomalies.

Risk: R452 — Parameter staleness degrades FLE accuracy over time.

Mitigation: EWMA-based adaptive threshold tuning. Monitor false-positive and
false-negative rates; auto-adjust sensitivity when rates breach tolerance.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: adaptive_param_tuning.py
# 层: 算法
# - id: A1
#   name_zh: ① AdaptiveParamTuning
#   name_en: AdaptiveParamTuning
#   intro: class AdaptiveParamTuning 源码 L70-L111
#   desc: 公共方法（定义序）: observe, lock, unlock；源码 L70-L111
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AdaptiveParamTuning
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TuningMode(str, Enum):
    LOCKED = "LOCKED"
    ADAPTIVE = "ADAPTIVE"
    AGGRESSIVE = "AGGRESSIVE"


@dataclass
class AdaptiveParamTuning:
    alpha: float = 0.3
    false_positive_tolerance: float = 0.05
    false_negative_tolerance: float = 0.02
    step_size: float = 0.1
    min_threshold: float = 0.01
    max_threshold: float = 10.0

    mode: TuningMode = TuningMode.ADAPTIVE
    current_threshold: float = 1.0
    ewma_fp: float = 0.0
    ewma_fn: float = 0.0
    adjustment_history: list[dict] = field(default_factory=list)

    def observe(self, was_anomaly: bool, was_true_positive: bool) -> float:
        fp = 1.0 if (not was_anomaly and not was_true_positive) else 0.0
        fn = 1.0 if (was_anomaly and not was_true_positive) else 0.0

        self.ewma_fp = self.alpha * fp + (1 - self.alpha) * self.ewma_fp
        self.ewma_fn = self.alpha * fn + (1 - self.alpha) * self.ewma_fn

        if self.mode is TuningMode.LOCKED:
            return self.current_threshold

        if self.ewma_fp > self.false_positive_tolerance:
            self.current_threshold += self.step_size
        elif self.ewma_fn > self.false_negative_tolerance:
            self.current_threshold -= self.step_size

        self.current_threshold = max(self.min_threshold, min(self.max_threshold, self.current_threshold))

        self.adjustment_history.append({"fp": self.ewma_fp, "fn": self.ewma_fn, "threshold": self.current_threshold})
        if len(self.adjustment_history) > 100:
            self.adjustment_history = self.adjustment_history[-100:]

        return self.current_threshold

    def lock(self) -> None:
        self.mode = TuningMode.LOCKED

    def unlock(self) -> None:
        self.mode = TuningMode.ADAPTIVE
