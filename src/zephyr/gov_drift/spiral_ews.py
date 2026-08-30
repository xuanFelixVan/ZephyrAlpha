# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.gov_drift.spiral_ews
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] src/zephyr/governance/ops_governance/budget_engine.py; tests/budget/test_budget_shutdown.py; tests/governance/budget/test_budget_enforcer_submodules.py; tests/governance/resilience/test_spiral_ews.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: window 参数
#   fields: 参数 window（无注解）
#   code: spiral_ews.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: threshold 参数
#   fields: 参数 threshold（无注解）
#   code: spiral_ews.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SpiralEarlyWarningSystem
#   name_en: SpiralEarlyWarningSystem
#   intro: class SpiralEarlyWarningSystem 源码 L68-L132
#   desc: 公共方法（定义序）: feed, check, recent_signals, is_spiraling, reset；源码 L68-L132
#   inputs: window threshold
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SpiralEarlyWarningSystem
#   downstream: src/zephyr/governance/ops_governance/budget_engine.py; tests/budget/test_budget…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class SpiralSignal:
    token_growth_rate: float
    cost_growth_rate: float
    depth_increase_rate: float
    composite_score: float
    level: str
    timestamp: float = field(default_factory=time.time)


class SpiralEarlyWarningSystem:
    def __init__(self, window: int = 10, threshold: float = 1.5):
        self._window = window
        self._threshold = threshold
        self._token_history: deque[int] = deque(maxlen=window)
        self._cost_history: deque[float] = deque(maxlen=window)
        self._depth_history: deque[int] = deque(maxlen=window)
        self._signals: list[SpiralSignal] = []

    def feed(self, tokens_this_step: int, cost_this_step: float, depth: int = 1) -> None:
        self._token_history.append(tokens_this_step)
        self._cost_history.append(cost_this_step)
        self._depth_history.append(depth)

    def check(self) -> SpiralSignal:
        tok_rate = self._growth_rate(self._token_history)
        cost_rate = self._growth_rate(self._cost_history)
        depth_rate = self._growth_rate(self._depth_history)

        composite = tok_rate * 0.4 + cost_rate * 0.4 + depth_rate * 0.2

        if composite > self._threshold * 3:
            level = "CRITICAL"
        elif composite > self._threshold:
            level = "WARNING"
        else:
            level = "NORMAL"

        signal = SpiralSignal(
            token_growth_rate=tok_rate,
            cost_growth_rate=cost_rate,
            depth_increase_rate=depth_rate,
            composite_score=composite,
            level=level,
        )
        self._signals.append(signal)
        return signal

    def _growth_rate(self, history: deque) -> float:
        if len(history) < 2:
            return 0.0
        values = list(history)
        if all(v == 0 for v in values):
            return 0.0
        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2 :]
        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0
        if avg_first == 0:
            return 1.0 if avg_second > 0 else 0.0
        return avg_second / avg_first

    def recent_signals(self, n: int = 10) -> list[SpiralSignal]:
        return self._signals[-n:]

    def is_spiraling(self) -> bool:
        if not self._signals:
            return False
        return self._signals[-1].level == "CRITICAL"

    def reset(self) -> None:
        self._token_history.clear()
        self._cost_history.clear()
        self._depth_history.clear()
        self._signals.clear()
