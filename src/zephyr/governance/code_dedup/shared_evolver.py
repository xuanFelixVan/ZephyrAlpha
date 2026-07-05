# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.shared_evolver
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/shared/test_shared_evolver.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_shared_evolver | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""共享函数自我进化引擎 — 自动升降级 + 行为漂移锁定.

职责：
  - shared函数被频繁使用(>50次) → 自动晋升为[*A]autonomous
  - 连续2月Health下降 → 自动降级
  - 时态漂移3个月 → 自动锁定为[*R]劣化限制
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class EvolutionTier(str, Enum):
    A_AUTONOMOUS = "[*A]autonomous"
    S_STANDARD = "[*S]standard"
    R_RESTRICTED = "[*R]restricted"


@dataclass
class EvolutionEntry:
    function_name: str
    tier: str = EvolutionTier.S_STANDARD.value
    call_count: int = 0
    health_history: list[int] = field(default_factory=list)
    temporal_drift_count: int = 0
    last_promoted: str = ""
    last_demoted: str = ""
    locked: bool = False
    lock_reason: str = ""


class SharedEvolver:
    """共享函数自我进化引擎."""

    _PROMOTION_CALL_THRESHOLD: int = 50
    _DEGRADE_MONTHS: int = 2
    _DRIFT_LOCK_MONTHS: int = 3
    _DRIFT_LOCK_THRESHOLD: int = 10

    def __init__(self) -> None:
        self._entries: dict[str, EvolutionEntry] = {}

    # ── 公共 API ──────────────────────────────────────────────

    def evaluate(
        self,
        function_name: str,
        call_count: int,
        health_score: int,
        drift_events_this_month: int = 0,
    ) -> EvolutionEntry:
        """评估函数进化方向."""
        entry = self._entries.get(function_name)
        if entry is None:
            entry = EvolutionEntry(function_name=function_name)
            self._entries[function_name] = entry

        entry.call_count = call_count
        entry.health_history.append(health_score)
        entry.temporal_drift_count += drift_events_this_month

        if len(entry.health_history) > 6:
            entry.health_history = entry.health_history[-6:]

        if (
            call_count > self._PROMOTION_CALL_THRESHOLD
            and entry.tier != EvolutionTier.A_AUTONOMOUS.value
            and not entry.locked
        ):
            entry.tier = EvolutionTier.A_AUTONOMOUS.value
            entry.last_promoted = datetime.now(UTC).isoformat()

        if self._should_downgrade(entry):
            entry.tier = EvolutionTier.R_RESTRICTED.value
            entry.last_demoted = datetime.now(UTC).isoformat()

        if self._should_lock(entry):
            entry.locked = True
            entry.lock_reason = f"时态漂移过多: {entry.temporal_drift_count}次/{self._DRIFT_LOCK_MONTHS}月"
            entry.tier = EvolutionTier.R_RESTRICTED.value

        return entry

    def get_autonomous_functions(self) -> list[EvolutionEntry]:
        return [e for e in self._entries.values() if e.tier == EvolutionTier.A_AUTONOMOUS.value]

    def get_restricted_functions(self) -> list[EvolutionEntry]:
        return [e for e in self._entries.values() if e.tier == EvolutionTier.R_RESTRICTED.value]

    # ── 内部 ──────────────────────────────────────────────────

    def _should_downgrade(self, entry: EvolutionEntry) -> bool:
        if len(entry.health_history) < self._DEGRADE_MONTHS:
            return False
        recent = entry.health_history[-self._DEGRADE_MONTHS :]
        return all(s < 50 for s in recent)

    def _should_lock(self, entry: EvolutionEntry) -> bool:
        return entry.temporal_drift_count >= self._DRIFT_LOCK_THRESHOLD
