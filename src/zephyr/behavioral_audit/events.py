# [A_module] module_id=MOD-SEC_events | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md

# [MODULE] zephyr.behavioral_audit.events

# [INVARIANTS] 事件定义不可修改

# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__

# [CONSUMERS] behavioral_auditor包内所有模块

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] immutable_core

# [ERROR_CONTRACT] 定义所有漂移事件类型

# [TESTS] tests/behavioral-auditor/

"""
G-CT-005 — DriftEvent Pydantic V2 BaseModel 漂移事件定义."""

from datetime import UTC, datetime
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

    detected_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

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
