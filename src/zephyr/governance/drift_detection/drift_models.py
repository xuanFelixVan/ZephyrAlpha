# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.drift_models
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] drift_engine;detector_dispatcher;correlation_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 数据模型不可破坏兼容性
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_drift_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drift Detector 数据模型 — drift_models.py





module_id: MOD-INF-023


定义漂移检测系统的所有核心数据类、枚举和类型别名。


对标 blueprint.md §2.3（漂移状态机数据表）、§7（文件组成）。"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto


class DriftState(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

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
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    LIGHT = auto()

    STANDARD = auto()

    DEEP = auto()


class Severity(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    HIGH = "HIGH"

    MEDIUM = "MEDIUM"

    LOW = "LOW"


class OrphanClassification(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

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

    resolved_by: str | None = None

    resolution_detail: str | None = None

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

    cascade_lock_until: datetime | None = None


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

    last_modified: datetime | None = None

    suggestion: str = ""


@dataclass
class Detector:
    id: str

    drift_dimension: str

    severity: Severity

    category: str

    script: str | None = None

    method: str | None = None

    status: str = "active"

    auto_fixable: bool = False

    check_dims: list[str] = field(default_factory=list)

    timeout_seconds: int = 30

    script_args: list[str] = field(default_factory=list)
