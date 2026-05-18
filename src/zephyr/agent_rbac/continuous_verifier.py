# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.continuous_verifier

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""持续验证器——权限判定后持续监控+定期recheck 防静默漂移."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class VerificationRecord(BaseModel):
    session_id: str
    check_time: str
    status: str
    drift_detected: bool = False


class ContinuousVerifier:
    _CHECK_INTERVAL_SECONDS: int = 60

    def __init__(self) -> None:
        self._records: dict[str, list[VerificationRecord]] = {}
        self._drifts: list[dict[str, Any]] = []

    def record(self, session_id: str, status: str, drift: bool = False) -> VerificationRecord:
        vr = VerificationRecord(
            session_id=session_id,
            check_time=datetime.now(timezone.utc).isoformat(),
            status=status,
            drift_detected=drift,
        )
        if session_id not in self._records:
            self._records[session_id] = []
        self._records[session_id].append(vr)

        if drift:
            self._drifts.append({"session_id": session_id, "time": vr.check_time})

        return vr

    def should_reverify(self, session_id: str) -> bool:
        records = self._records.get(session_id, [])
        if not records:
            return True
        last = datetime.fromisoformat(records[-1].check_time)
        elapsed = (datetime.now(timezone.utc) - last).total_seconds()
        return elapsed > self._CHECK_INTERVAL_SECONDS

    def get_drifts(self) -> list[dict[str, Any]]:
        return self._drifts
