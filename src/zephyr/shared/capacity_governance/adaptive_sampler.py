# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.adaptive_sampler
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.feedback_loop.__init___from_obs
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
#   name: base_rate 参数
#   fields: 参数 base_rate（无注解）
#   code: adaptive_sampler.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: error_boost 参数
#   fields: 参数 error_boost（无注解）
#   code: adaptive_sampler.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_rate 参数
#   fields: 参数 max_rate（无注解）
#   code: adaptive_sampler.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AdaptiveSampler
#   name_en: AdaptiveSampler
#   intro: class AdaptiveSampler 源码 L71-L102
#   desc: 公共方法（定义序）: base_rate, decide, update_base_rate；源码 L71-L102
#   inputs: base_rate error_boost max_rate
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AdaptiveSampler
#   downstream: zephyr.feedback_loop.__init___from_obs
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class SamplingDecision:
    should_sample: bool
    sample_rate: float
    reason: str


class AdaptiveSampler:
    def __init__(self, base_rate: float = 0.1, error_boost: float = 0.9, max_rate: float = 1.0):
        self._base_rate = base_rate
        self._error_boost = error_boost
        self._max_rate = max_rate
        self._error_count = 0
        self._total_count = 0

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def base_rate(self):
        """只读：base_rate（Stage 4 公共化）。"""
        return self._base_rate

    @base_rate.setter
    def base_rate(self, value):
        """写入：base_rate（Stage 4 公共化）。"""
        self._base_rate = value

    def decide(self, is_error: bool = False) -> SamplingDecision:
        self._total_count += 1
        if is_error:
            self._error_count += 1
            rate = min(self._error_boost, self._max_rate)
            return SamplingDecision(True, rate, "error_boosted")
        error_ratio = self._error_count / max(self._total_count, 1)
        rate = min(self._base_rate + error_ratio * 0.5, self._max_rate)
        should = random.random() < rate
        return SamplingDecision(should, rate, f"adaptive_rate={rate:.3f}")

    def update_base_rate(self, new_rate: float) -> None:
        self._base_rate = max(0.0, min(new_rate, self._max_rate))
