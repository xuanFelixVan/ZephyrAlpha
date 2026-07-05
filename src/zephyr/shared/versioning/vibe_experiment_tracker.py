# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.versioning.vibe_experiment_tracker
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class ExperimentRecord:
    experiment_id: str
    session_id: str
    parameters: dict[str, str] = field(default_factory=dict)
    outcome: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: float = 0.0


class VibeExperimentTracker:
    def __init__(self):
        self._experiments: list[ExperimentRecord] = []

    def start(self, session_id: str, **parameters: str) -> ExperimentRecord:
        record = ExperimentRecord(str(uuid.uuid4())[:8], session_id, parameters, created_at=time.time())
        self._experiments.append(record)
        return record

    def record_outcome(self, experiment_id: str, outcome: str, **metrics: float) -> bool:
        for e in self._experiments:
            if e.experiment_id == experiment_id:
                e.outcome = outcome
                e.metrics.update(metrics)
                return True
        return False

    def get_by_session(self, session_id: str) -> list[ExperimentRecord]:
        return [e for e in self._experiments if e.session_id == session_id]
