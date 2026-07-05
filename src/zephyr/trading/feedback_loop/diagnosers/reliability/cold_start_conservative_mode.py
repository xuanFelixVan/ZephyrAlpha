# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.cold_start_conservative_mode
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_cold_start_conservative_mode | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R509: ColdStartConservativeMode
冷启动渐进激活 — collect→detect→diagnose→full，阈值×3衰减到×1
对标: Control Theory — Settling Time + progressive activation
"""

import time
from dataclasses import dataclass, field
from enum import Enum


class ColdStartPhase(str, Enum):
    COLLECT_ONLY = "collect_only"
    WITH_DETECT = "with_detect"
    WITH_DIAGNOSE = "with_diagnose"
    FULL_ENABLED = "full_enabled"


@dataclass
class ColdStartConservativeMode:
    started_at: float = 0.0
    current_cycle: int = 0
    phase: ColdStartPhase = ColdStartPhase.COLLECT_ONLY

    phase_thresholds: dict[ColdStartPhase, int] = field(
        default_factory=lambda: {
            ColdStartPhase.COLLECT_ONLY: 100,
            ColdStartPhase.WITH_DETECT: 300,
            ColdStartPhase.WITH_DIAGNOSE: 500,
            ColdStartPhase.FULL_ENABLED: 500,
        }
    )
    threshold_multiplier: float = 3.0
    blocked_actions: set[str] = field(default_factory=lambda: {"SELF_UPGRADE", "PROMPT_EVOLVE", "KNOWLEDGE_INJECT"})

    def start(self) -> None:
        self.started_at = time.time()
        self.current_cycle = 0
        self.phase = ColdStartPhase.COLLECT_ONLY

    def tick(self) -> ColdStartPhase:
        self.current_cycle += 1
        prev = self.phase

        if self.current_cycle >= self.phase_thresholds[ColdStartPhase.WITH_DIAGNOSE]:
            self.phase = ColdStartPhase.FULL_ENABLED
        elif self.current_cycle >= self.phase_thresholds[ColdStartPhase.WITH_DETECT]:
            self.phase = ColdStartPhase.WITH_DIAGNOSE
        elif self.current_cycle >= self.phase_thresholds[ColdStartPhase.COLLECT_ONLY]:
            self.phase = ColdStartPhase.WITH_DETECT

        if self.phase != prev:
            self._on_phase_transition(prev, self.phase)

        return self.phase

    def current_threshold_multiplier(self) -> float:
        if self.phase is ColdStartPhase.FULL_ENABLED:
            return 1.0
        phases = [
            ColdStartPhase.COLLECT_ONLY,
            ColdStartPhase.WITH_DETECT,
            ColdStartPhase.WITH_DIAGNOSE,
            ColdStartPhase.FULL_ENABLED,
        ]
        idx = phases.index(self.phase)
        decay = 1.0 - idx / 3.0
        return max(1.0, self.threshold_multiplier * decay)

    def is_action_allowed(self, action_type: str) -> bool:
        if self.phase is ColdStartPhase.FULL_ENABLED:
            return True
        if action_type.startswith("COLLECT_"):
            return True
        if self.phase in (ColdStartPhase.WITH_DETECT, ColdStartPhase.WITH_DIAGNOSE):
            if action_type.startswith("DETECT_") or action_type.startswith("DIAGNOSE_"):
                return True
        return action_type not in self.blocked_actions

    def _on_phase_transition(self, from_phase: ColdStartPhase, to_phase: ColdStartPhase) -> None:
        pass

    def is_warm(self) -> bool:
        return self.phase is ColdStartPhase.FULL_ENABLED

    def elapsed_cycles(self) -> int:
        return self.current_cycle

    def status_report(self) -> dict:
        return {
            "phase": self.phase.value,
            "cycle": self.current_cycle,
            "is_warm": self.is_warm(),
            "threshold_multiplier": round(self.current_threshold_multiplier(), 2),
            "elapsed_seconds": round(time.time() - self.started_at, 1) if self.started_at > 0 else 0,
        }
