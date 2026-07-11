# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.drift_detection.spiral_ews
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] src/zephyr/governance/ops_governance/budget_engine.py; tests/budget/test_budget_shutdown.py; tests/governance/budget/test_budget_enforcer_submodules.py; tests/governance/resilience/test_spiral_ews.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_spiral_ews | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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
