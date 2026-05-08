"""盲点追踪——定期检测未覆盖权限场景+主动发现+报告Owner."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BlindSpot(BaseModel):
    spot_id: str
    description: str
    severity: str = "MEDIUM"
    detected_at: str
    acknowledged: bool = False
    coverage_gap: str = ""


class BlindSpotTracker:
    def __init__(self) -> None:
        self._spots: dict[str, BlindSpot] = {}
        self._scan_count: int = 0

    def detect(self, description: str, severity: str = "MEDIUM", coverage_gap: str = "") -> BlindSpot:
        from datetime import datetime, timezone

        sid = f"BS-{self._scan_count}-{hash(description) % 10000}"
        spot = BlindSpot(
            spot_id=sid,
            description=description,
            severity=severity,
            detected_at=datetime.now(timezone.utc).isoformat(),
            coverage_gap=coverage_gap,
        )
        self._spots[sid] = spot
        self._scan_count += 1
        return spot

    def acknowledge(self, spot_id: str) -> dict[str, Any]:
        if spot_id in self._spots:
            self._spots[spot_id].acknowledged = True
            return {"acknowledged": True, "spot_id": spot_id}
        return {"acknowledged": False, "reason": "not_found"}

    def summary(self) -> dict[str, Any]:
        total = len(self._spots)
        unack = sum(1 for s in self._spots.values() if not s.acknowledged)
        critical_unack = sum(1 for s in self._spots.values() if not s.acknowledged and s.severity == "CRITICAL")
        return {"total_blind_spots": total, "unacknowledged": unack, "critical_unacknowledged": critical_unack}
