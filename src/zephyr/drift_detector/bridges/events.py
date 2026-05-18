# [BLUEPRINT] MOD-INF-023 | 03_modules/l01_infrastructure/drift-detector/blueprint.md | §

# [MODULE] zephyr.drift_detector.bridges.events

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""G-CT-005 — DriftEvent Pydantic V2 BaseModel 漂移事件定义."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class DriftType(str, Enum):
    CODE_DIVERGENCE = "CODE_DIVERGENCE"
    CONFIG_DRIFT = "CONFIG_DRIFT"
    SCHEMA_DRIFT = "SCHEMA_DRIFT"
    DEPENDENCY_DRIFT = "DEPENDENCY_DRIFT"
    INTERFACE_DRIFT = "INTERFACE_DRIFT"


class DriftState(str, Enum):
    DETECTED = "DETECTED"
    FIXED = "FIXED"
    MANUAL_REQUIRED = "MANUAL_REQUIRED"
    IGNORED = "IGNORED"


class DriftEvent(BaseModel):
    drift_id: str
    detected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    target: str
    drift_type: DriftType = DriftType.CODE_DIVERGENCE
    fix_suggestion: str = ""
    auto_fixable: bool = False
    state: DriftState = DriftState.DETECTED
    agent_id: str = ""
    severity: str = "MEDIUM"

    def mark_fixed(self) -> None:
        self.state = DriftState.FIXED

    def mark_manual_required(self) -> None:
        self.state = DriftState.MANUAL_REQUIRED
