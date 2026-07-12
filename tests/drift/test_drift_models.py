# [A_test] module_id: SRC-TST-0779 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_drift_models
# [INVARIANTS] 数据模型不可破坏兼容性
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/drift_models.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip
# [TESTS] python -m pytest tests/test_drift_models.py -q
# [TTL] task_bound

from __future__ import annotations

import uuid
from datetime import datetime

from zephyr.gov_drift.drift_models import (
    BaselineSnapshot,
    BreakingChange,
    BulkDriftEvent,
    CascadeEvent,
    Detector,
    DriftBudget,
    DriftEvent,
    DriftReport,
    DriftState,
    OrphanClassification,
    OrphanFile,
    Runbook,
    ScanLevel,
    ScanResult,
    Severity,
)


class TestDriftState:
    def test_all_states_exist(self):
        expected = {
            "DETECTED",
            "TRIAGED",
            "ACKNOWLEDGED",
            "RESOLVING",
            "RESOLVED",
            "VERIFIED",
            "FIX_FAILED",
            "FALSE_POSITIVE",
            "DEAD_LETTER",
            "SUPPRESSED",
        }
        actual = {s.value for s in DriftState}
        assert actual == expected

    def test_enum_count(self):
        assert len(DriftState) == 10


class TestScanLevel:
    def test_levels_exist(self):
        assert ScanLevel.LIGHT is not None
        assert ScanLevel.STANDARD is not None
        assert ScanLevel.DEEP is not None

    def test_enum_count(self):
        assert len(ScanLevel) == 3


class TestSeverity:
    def test_values(self):
        assert Severity.HIGH.value == "HIGH"
        assert Severity.MEDIUM.value == "MEDIUM"
        assert Severity.LOW.value == "LOW"


class TestOrphanClassification:
    def test_values(self):
        assert OrphanClassification.TRUE_ORPHAN.value == "true_orphan"
        assert OrphanClassification.UNDOCUMENTED_ASSET.value == "undocumented_asset"
        assert OrphanClassification.STALE_ARTIFACT.value == "stale_artifact"


class TestDriftEvent:
    def test_creation(self):
        now = datetime.utcnow()
        event = DriftEvent(
            event_id=uuid.uuid4(),
            module_id="mod_a",
            detector_id="det_1",
            drift_dimension="interface",
            baseline_version="v1",
            state=DriftState.DETECTED,
            created_at=now,
            updated_at=now,
        )
        assert event.module_id == "mod_a"
        assert event.state == DriftState.DETECTED
        assert event.resolved_by is None
        assert event.auto_fixed is False

    def test_optional_fields(self):
        event = DriftEvent(
            event_id=uuid.uuid4(),
            module_id="mod_b",
            detector_id="det_2",
            drift_dimension="config",
            baseline_version="v2",
            state=DriftState.RESOLVED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            resolved_by="agent",
            resolution_detail="fixed",
            auto_fixed=True,
            rollback_verified=True,
        )
        assert event.resolved_by == "agent"
        assert event.auto_fixed is True


class TestBaselineSnapshot:
    def test_default_values(self):
        snap = BaselineSnapshot(version="v1")
        assert snap.version == "v1"
        assert snap.tree_hash == {}
        assert snap.interface_snapshot == {}
        assert snap.import_graph == {}
        assert snap.config_snapshot == {}

    def test_custom_values(self):
        snap = BaselineSnapshot(
            version="v2",
            tree_hash={"a.py": "hash1"},
            interface_snapshot={"a.py": "iface1"},
        )
        assert snap.tree_hash["a.py"] == "hash1"


class TestScanResult:
    def test_creation(self):
        sr = ScanResult(scan_id=uuid.uuid4(), detectors_run=5, total_drift_events=3)
        assert sr.detectors_run == 5
        assert sr.total_drift_events == 3
        assert sr.new_events == []
        assert sr.storm_mode_triggered is False

    def test_with_events(self):
        event = DriftEvent(
            event_id=uuid.uuid4(),
            module_id="m",
            detector_id="d",
            drift_dimension="x",
            baseline_version="v1",
            state=DriftState.DETECTED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        sr = ScanResult(scan_id=uuid.uuid4(), detectors_run=1, total_drift_events=1, events=[event])
        assert len(sr.events) == 1


class TestDriftReport:
    def test_defaults(self):
        report = DriftReport()
        assert report.module_health_index == {}
        assert report.top_drift_dimensions == []
        assert report.active_drift_count == 0
        assert report.scan_summary == ""


class TestDriftBudget:
    def test_tier_budget_known_tiers(self):
        assert DriftBudget.tier_budget("P0") == 5
        assert DriftBudget.tier_budget("P1") == 20
        assert DriftBudget.tier_budget("P2") == 50
        assert DriftBudget.tier_budget("P3") == 100

    def test_tier_budget_unknown(self):
        assert DriftBudget.tier_budget("PX") == 20

    def test_consume(self):
        budget = DriftBudget(module_id="m1", tier="P1", monthly_budget=20)
        budget.consume(5)
        assert budget.consumed == 5
        assert budget.remaining == 15
        assert not budget.hard_limit_reached

    def test_consume_to_exhaustion(self):
        budget = DriftBudget(module_id="m1", tier="P0", monthly_budget=5)
        budget.consume(5)
        assert budget.remaining == 0
        assert budget.hard_limit_reached

    def test_consume_over_budget(self):
        budget = DriftBudget(module_id="m1", tier="P0", monthly_budget=5)
        budget.consume(10)
        assert budget.remaining == 0
        assert budget.hard_limit_reached

    def test_is_exhausted(self):
        budget = DriftBudget(module_id="m1", tier="P0", monthly_budget=5)
        budget.consume(5)
        assert budget.is_exhausted()

    def test_not_exhausted(self):
        budget = DriftBudget(module_id="m1", tier="P1", monthly_budget=20)
        budget.consume(5)
        assert not budget.is_exhausted()


class TestRunbook:
    def test_defaults(self):
        rb = Runbook(event_id=uuid.uuid4())
        assert rb.metadata == {}
        assert rb.diagnosis == ""
        assert rb.remediation == ""
        assert rb.rollback == ""
        assert rb.references == []


class TestCascadeEvent:
    def test_defaults(self):
        ce = CascadeEvent(module_id="m1")
        assert ce.trigger_count == 0
        assert ce.repair_loop_events == []
        assert ce.cascade_lock_until is None


class TestBulkDriftEvent:
    def test_defaults(self):
        bde = BulkDriftEvent(event_id=uuid.uuid4(), scan_id=uuid.uuid4())
        assert bde.affected_modules == []
        assert bde.is_expected is False
        assert bde.is_unexpected is False


class TestBreakingChange:
    def test_creation(self):
        bc = BreakingChange(
            api_signature="func(a, b)",
            field_path="module.func",
            old_definition="old",
            new_definition="new",
        )
        assert bc.impacted_modules == []


class TestOrphanFile:
    def test_creation(self):
        of = OrphanFile(file_path="/tmp/x.py", classification=OrphanClassification.TRUE_ORPHAN)
        assert of.last_modified is None
        assert of.suggestion == ""


class TestDetector:
    def test_defaults(self):
        det = Detector(id="d1", drift_dimension="interface", severity=Severity.HIGH, category="code")
        assert det.script is None
        assert det.method is None
        assert det.status == "active"
        assert det.auto_fixable is False
        assert det.check_dims == []

    def test_custom_values(self):
        det = Detector(
            id="d2",
            drift_dimension="config",
            severity=Severity.LOW,
            category="infra",
            script="check.py",
            method="run",
            status="disabled",
            auto_fixable=True,
            check_dims=["a", "b"],
        )
        assert det.script == "check.py"
        assert det.auto_fixable is True
