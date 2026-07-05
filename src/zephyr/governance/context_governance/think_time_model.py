# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.context_governance.think_time_model
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_think_time_model | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class ThinkTimeSnapshot:
    elapsed: float
    tokens_generated: int
    tokens_per_second: float
    tier: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ThinkTimeModel:
    _history: deque[ThinkTimeSnapshot] = field(default_factory=lambda: deque(maxlen=100))
    _total_thinking_time: float = 0.0
    _total_tokens_reasoned: int = 0
    _chunk_times: list[float] = field(default_factory=list)

    def record_think_segment(self, elapsed: float, tokens: int, tier: str) -> ThinkTimeSnapshot:
        tps = tokens / elapsed if elapsed > 0 else 0.0
        snap = ThinkTimeSnapshot(elapsed=elapsed, tokens_generated=tokens, tokens_per_second=tps, tier=tier)
        self._history.append(snap)
        self._total_thinking_time += elapsed
        self._total_tokens_reasoned += tokens
        return snap

    def record_chunk_latency(self, chunk_time: float) -> None:
        self._chunk_times.append(chunk_time)

    def estimate_next_duration(self, expected_tokens: int = 500) -> float:
        if not self._history:
            return expected_tokens / 10.0
        avg_tps = sum(s.tokens_per_second for s in self._history) / len(self._history)
        if avg_tps == 0:
            return expected_tokens / 10.0
        return expected_tokens / avg_tps

    def average_tps(self) -> float:
        if not self._history:
            return 0.0
        return sum(s.tokens_per_second for s in self._history) / len(self._history)

    def average_chunk_latency(self) -> float:
        if not self._chunk_times:
            return 0.0
        return sum(self._chunk_times) / len(self._chunk_times)

    def total_thinking_cost(self, cost_per_second: float = 0.0) -> float:
        return self._total_thinking_time * cost_per_second

    def thinking_ratio(self, total_wall_time: float) -> float:
        if total_wall_time == 0:
            return 0.0
        return min(self._total_thinking_time / total_wall_time, 1.0)

    def recent_snapshots(self, n: int = 10) -> list[ThinkTimeSnapshot]:
        return list(self._history)[-n:]

    def reset(self) -> None:
        self._history.clear()
        self._chunk_times.clear()
        self._total_thinking_time = 0.0
        self._total_tokens_reasoned = 0
