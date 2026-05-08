"""
Drift Detector 数据模型 — drift_models.py

module_id: MOD-INF-023
定义漂移检测系统的所有核心数据类、枚举和类型别名。
对标 blueprint.md §2.3（漂移状态机数据表）、§7（文件组成）。
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Optional


class DriftState(Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVING = "RESOLVING"
    RESOLVED = "RESOLVED"
    VERIFIED = "VERIFIED"
    FIX_FAILED = "FIX_FAILED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    DEAD_LETTER = "DEAD_LETTER"
    SUPPRESSED = "SUPPRESSED"


class ScanLevel(Enum):
    LIGHT = auto()
    STANDARD = auto()
    DEEP = auto()


class Severity(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class OrphanClassification(Enum):
    TRUE_ORPHAN = "true_orphan"
    UNDOCUMENTED_ASSET = "undocumented_asset"
    STALE_ARTIFACT = "stale_artifact"


@dataclass
class DriftEvent:
    event_id: uuid.UUID
    module_id: str
    detector_id: str
    drift_dimension: str
    baseline_version: str
    state: DriftState
    created_at: datetime
    updated_at: datetime
    resolved_by: Optional[str] = None
    resolution_detail: Optional[str] = None
    auto_fixed: bool = False
    rollback_verified: bool = False


@dataclass
class BaselineSnapshot:
    version: str
    tree_hash: dict[str, str] = field(default_factory=dict)
    interface_snapshot: dict[str, str] = field(default_factory=dict)
    import_graph: dict[str, list[str]] = field(default_factory=dict)
    config_snapshot: dict[str, object] = field(default_factory=dict)


@dataclass
class ScanResult:
    scan_id: uuid.UUID
    detectors_run: int
    total_drift_events: int
    new_events: list[uuid.UUID] = field(default_factory=list)
    resolved_events: list[uuid.UUID] = field(default_factory=list)
    storm_mode_triggered: bool = False
    events: list[DriftEvent] = field(default_factory=list)


@dataclass
class DriftReport:
    module_health_index: dict[str, float] = field(default_factory=dict)
    top_drift_dimensions: list[tuple[str, int]] = field(default_factory=list)
    active_drift_count: int = 0
    scan_summary: str = ""


@dataclass
class DriftBudget:
    module_id: str
    tier: str
    monthly_budget: int
    consumed: int = 0
    remaining: int = 0
    hard_limit_reached: bool = False
    reset_date: str = ""

    @staticmethod
    def tier_budget(tier: str) -> int:
        return {"P0": 5, "P1": 20, "P2": 50, "P3": 100}.get(tier, 20)

    def consume(self, n: int = 1) -> None:
        self.consumed += n
        self.remaining = max(0, self.monthly_budget - self.consumed)
        if self.remaining <= 0:
            self.hard_limit_reached = True

    def is_exhausted(self) -> bool:
        return self.hard_limit_reached or self.remaining <= 0


@dataclass
class Runbook:
    event_id: uuid.UUID
    metadata: dict[str, str] = field(default_factory=dict)
    diagnosis: str = ""
    remediation: str = ""
    rollback: str = ""
    references: list[str] = field(default_factory=list)


@dataclass
class CascadeEvent:
    module_id: str
    trigger_count: int = 0
    repair_loop_events: list[uuid.UUID] = field(default_factory=list)
    cascade_lock_until: Optional[datetime] = None


@dataclass
class BulkDriftEvent:
    event_id: uuid.UUID
    scan_id: uuid.UUID
    affected_modules: list[str] = field(default_factory=list)
    dimension_groups: dict[str, int] = field(default_factory=dict)
    is_expected: bool = False
    is_unexpected: bool = False
    child_event_ids: list[uuid.UUID] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())


@dataclass
class ForensicsReport:
    event_id: uuid.UUID
    timeline: list[dict[str, object]] = field(default_factory=list)
    state_diffs: list[dict[str, object]] = field(default_factory=list)
    actor_trace: list[str] = field(default_factory=list)
    dependency_impact: list[str] = field(default_factory=list)


@dataclass
class ConfigConflict:
    key_name: str
    env_source_value: Optional[str] = None
    yaml_source_value: Optional[object] = None
    hardcoded_default_value: Optional[object] = None


@dataclass
class BreakingChange:
    api_signature: str
    field_path: str
    old_definition: str
    new_definition: str
    impacted_modules: list[str] = field(default_factory=list)


@dataclass
class OrphanFile:
    file_path: str
    classification: OrphanClassification
    last_modified: Optional[datetime] = None
    suggestion: str = ""


@dataclass
class Detector:
    id: str
    drift_dimension: str
    severity: Severity
    category: str
    script: Optional[str] = None
    method: Optional[str] = None
    status: str = "active"
    auto_fixable: bool = False
    check_dims: list[str] = field(default_factory=list)
