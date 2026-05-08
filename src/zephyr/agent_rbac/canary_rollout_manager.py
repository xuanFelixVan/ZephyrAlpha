"""D-018-33 Canary权限灰度发布——1%采样/24h观察/自动全量/异常回滚."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CanaryState(str, Enum):
    PENDING = "PENDING"
    SAMPLING = "SAMPLING"
    OBSERVING = "OBSERVING"
    FULL_ROLLOUT = "FULL_ROLLOUT"
    ROLLED_BACK = "ROLLED_BACK"


class CanaryPermission(BaseModel):
    permission_id: str
    rule_ids: list[str] = Field(default_factory=list)
    state: CanaryState = CanaryState.PENDING
    sample_rate: float = 0.01
    rollout_at: str = ""
    observe_until: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    stats: dict[str, int] = Field(default_factory=lambda: {"total_checks": 0, "allowed": 0, "blocked": 0, "anomalies": 0})


class CanaryRolloutManager:
    _OBSERVE_HOURS: int = 24
    _ANOMALY_THRESHOLD: float = 0.05

    def __init__(self) -> None:
        self._canaries: dict[str, CanaryPermission] = {}
        self._history: list[dict[str, Any]] = []

    def register(self, permission_id: str, rule_ids: list[str]) -> CanaryPermission:
        cp = CanaryPermission(permission_id=permission_id, rule_ids=rule_ids)
        self._canaries[permission_id] = cp
        self._history.append({"action": "REGISTERED", "permission_id": permission_id})
        return cp

    def start_sampling(self, permission_id: str) -> dict[str, Any]:
        cp = self._canaries.get(permission_id)
        if not cp:
            return {"error": "not_found", "permission_id": permission_id}
        cp.state = CanaryState.SAMPLING
        cp.rollout_at = datetime.now(timezone.utc).isoformat()
        return {"permission_id": permission_id, "state": "SAMPLING", "sample_rate": cp.sample_rate}

    def promote_to_full(self, permission_id: str) -> dict[str, Any]:
        cp = self._canaries.get(permission_id)
        if not cp:
            return {"error": "not_found", "permission_id": permission_id}
        anomaly_rate = cp.stats["anomalies"] / max(cp.stats["total_checks"], 1)
        if anomaly_rate > self._ANOMALY_THRESHOLD:
            return {"promoted": False, "permission_id": permission_id, "reason": f"anomaly_rate={anomaly_rate:.3f} > {self._ANOMALY_THRESHOLD}"}
        cp.state = CanaryState.FULL_ROLLOUT
        return {"promoted": True, "permission_id": permission_id}

    def rollback(self, permission_id: str) -> dict[str, Any]:
        cp = self._canaries.get(permission_id)
        if not cp:
            return {"error": "not_found", "permission_id": permission_id}
        cp.state = CanaryState.ROLLED_BACK
        self._history.append({"action": "ROLLED_BACK", "permission_id": permission_id, "stats": cp.stats})
        return {"rolled_back": True, "permission_id": permission_id}
