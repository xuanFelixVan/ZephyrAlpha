"""自适应阈值——从历史 FAIL/PASS 数据学习门禁参数调整（experimental）"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ThresholdState:
    gate_id: str
    current_threshold: float
    history: deque[float] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.history is None:
            self.history = deque(maxlen=100)


class AdaptiveThreshold:
    DEFAULT_WINDOW = 50
    DEFAULT_SMOOTHING = 0.2

    def __init__(self, window: int = DEFAULT_WINDOW, smoothing: float = DEFAULT_SMOOTHING) -> None:
        self._window = window
        self._smoothing = smoothing
        self._states: dict[str, ThresholdState] = {}

    def get_state(self, gate_id: str, initial: float = 0.8) -> ThresholdState:
        if gate_id not in self._states:
            self._states[gate_id] = ThresholdState(gate_id=gate_id, current_threshold=initial)
        return self._states[gate_id]

    def observe(self, gate_id: str, value: float, outcome: str) -> float:
        state = self.get_state(gate_id)
        state.history.append(value)

        if outcome == "PASS":
            direction = -self._smoothing
        elif outcome == "FAIL":
            direction = self._smoothing
        else:
            return state.current_threshold

        state.current_threshold = max(0.1, min(0.99, state.current_threshold + direction * (1.0 - state.current_threshold)))
        logger.debug("threshold %s adjusted: %.4f (outcome=%s)", gate_id, state.current_threshold, outcome)
        return state.current_threshold

    def ewma(self, gate_id: str) -> float:
        state = self.get_state(gate_id)
        if not state.history:
            return state.current_threshold
        alpha = 2.0 / (min(len(state.history), self._window) + 1)
        ewma_val = state.history[0]
        for v in list(state.history)[1:]:
            ewma_val = alpha * v + (1 - alpha) * ewma_val
        return ewma_val


__all__ = ["AdaptiveThreshold", "ThresholdState"]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
