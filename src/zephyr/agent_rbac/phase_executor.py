# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.phase_executor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""相位执行器——Phase 1-4分段部署+gate检查+rollback-if-fail."""
from __future__ import annotations

from enum import Enum
from typing import Any


class Phase(str, Enum):
    P1_BOOTSTRAP = "P1_BOOTSTRAP"
    P2_CORE_GUARDS = "P2_CORE_GUARDS"
    P3_INTEGRATION = "P3_INTEGRATION"
    P4_FULL_ROLLOUT = "P4_FULL_ROLLOUT"


class PhaseExecutor:
    _PHASE_ORDER = [Phase.P1_BOOTSTRAP, Phase.P2_CORE_GUARDS, Phase.P3_INTEGRATION, Phase.P4_FULL_ROLLOUT]

    def __init__(self) -> None:
        self._current_phase: Phase = Phase.P1_BOOTSTRAP
        self._completed: set[Phase] = set()
        self._history: list[dict[str, Any]] = []

    def execute(self, phase: Phase) -> dict[str, Any]:
        if phase not in self._PHASE_ORDER:
            return {"success": False, "reason": "unknown_phase", "phase": phase.value}

        phase_idx = self._PHASE_ORDER.index(phase)
        for prev in self._PHASE_ORDER[:phase_idx]:
            if prev not in self._completed:
                return {"success": False, "reason": f"prerequisite_phase_not_completed: {prev.value}", "phase": phase.value}

        self._completed.add(phase)
        self._current_phase = phase
        self._history.append({"phase": phase.value, "status": "COMPLETED"})
        return {"success": True, "phase": phase.value, "completed_phases": [p.value for p in self._completed]}

    def rollback(self, phase: Phase) -> dict[str, Any]:
        if phase in self._completed:
            self._completed.discard(phase)
            self._history.append({"phase": phase.value, "status": "ROLLED_BACK"})
            return {"rolled_back": True, "phase": phase.value}
        return {"rolled_back": False, "reason": "phase_not_completed", "phase": phase.value}
