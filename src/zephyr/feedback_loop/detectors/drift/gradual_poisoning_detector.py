# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.drift.gradual_poisoning_detector
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
Gradual Poisoning Detector — v0.15.0 R210

Blindspot: Attacker slowly poisons training data; drift too gradual for single-window detection.
Risk: R210 — 30-day slow poisoning corrupts FLE behavior; detector sees "normal" in short windows.

Mitigation: Long-term trend analysis with cumulative deviation tracking across multiple time scales.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: gradual_poisoning_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① GradualPoisoningDetector
#   name_en: GradualPoisoningDetector
#   intro: class GradualPoisoningDetector 源码 L68-L86
#   desc: 公共方法（定义序）: observe, is_poisoned；源码 L68-L86
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: GradualPoisoningDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class PoisoningSignal:
    short_term_mean: float = 0.0
    long_term_mean: float = 0.0
    cumulative_deviation: float = 0.0


@dataclass
class GradualPoisoningDetector:
    short_window: deque[float] = field(default_factory=lambda: deque(maxlen=100))
    long_window: deque[float] = field(default_factory=lambda: deque(maxlen=1000))
    threshold: float = 3.0

    def observe(self, value: float) -> PoisoningSignal:
        self.short_window.append(value)
        self.long_window.append(value)
        st_mean = sum(self.short_window) / len(self.short_window) if self.short_window else value
        lt_mean = sum(self.long_window) / len(self.long_window) if self.long_window else value
        return PoisoningSignal(
            short_term_mean=st_mean, long_term_mean=lt_mean, cumulative_deviation=abs(st_mean - lt_mean)
        )

    def is_poisoned(self) -> bool:
        if len(self.long_window) < 100:
            return False
        signal = self.observe(0.0)
        return signal.cumulative_deviation > self.threshold
