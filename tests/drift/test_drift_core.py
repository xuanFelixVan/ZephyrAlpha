# [A_test] module_id: SRC-TST-1865 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-491 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.drift_detector.test_drift_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: drift-detector core — drift_engine + baseline_manager + drift_models"""

import os
import uuid
from datetime import UTC, datetime

import pytest

from zephyr.gov_drift.baseline_manager import BaselineManager, DiffReport
from zephyr.gov_drift.drift_engine import (
    STORM_THRESHOLD,
    _create_bulk_event,
    _detect_expected_storm,
    _event_to_dict,
    _filter_detectors_by_level,
    _max_parallel,
    _parse_event,
    build_report,
    load_detector_registry,
)
from zephyr.gov_drift.drift_models import (
    BulkDriftEvent,
    Detector,
    DriftBudget,
    DriftEvent,
    DriftReport,
    DriftState,
    ScanLevel,
    ScanResult,
    Severity,
)


@pytest.fixture
def sample_detector():
    return Detector(
        id="DET-001",
        drift_dimension="architecture",
        severity=Severity.HIGH,
        category="structural",
        script=None,
        method="static",
        status="active",
        auto_fixable=False,
        check_dims=["tree_hash", "interface"],
    )


@pytest.fixture
def sample_detector_medium():
    return Detector(
        id="DET-002",
        drift_dimension="interface",
        severity=Severity.MEDIUM,
        category="contract",
        script=None,
        method="static",
        status="active",
        auto_fixable=True,
        check_dims=["interface_snapshot"],
    )


@pytest.fixture
def sample_detector_low():
    return Detector(
        id="DET-003",
        drift_dimension="config",
        severity=Severity.LOW,
        category="configuration",
        script=None,
        method="static",
        status="active",
        auto_fixable=False,
        check_dims=["config_snapshot"],
    )


@pytest.fixture
def sample_event(sample_detector):
    return DriftEvent(
        event_id=uuid.uuid4(),
        module_id="MOD-INF-023",
        detector_id=sample_detector.id,
        drift_dimension=sample_detector.drift_dimension,
        baseline_version="0.1.0",
        state=DriftState.DETECTED,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def tmp_project(tmp_path):
    module_dir = tmp_path / "src" / "zephyr" / "sample_mod"
    module_dir.mkdir(parents=True)
    (module_dir / "__init__.py").write_text("", encoding="utf-8")
    (module_dir / "core.py").write_text(
        "def hello():\n    return 'world'\n\nclass Foo:\n    pass\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def baseline_mgr(tmp_project):
    return BaselineManager(project_root=str(tmp_project))


class TestDriftModels:
    def test_drift_state_values(self):
        assert DriftState.DETECTED.value == "DETECTED"
        assert DriftState.FALSE_POSITIVE.value == "FALSE_POSITIVE"
        assert DriftState.RESOLVED.value == "RESOLVED"

    def test_severity_values(self):
        assert Severity.HIGH.value == "HIGH"
        assert Severity.MEDIUM.value == "MEDIUM"
        assert Severity.LOW.value == "LOW"

    def test_scan_level_members(self):
        assert ScanLevel.LIGHT is not None
        assert ScanLevel.STANDARD is not None
        assert ScanLevel.DEEP is not None

    def test_detector_creation(self, sample_detector):
        assert sample_detector.id == "DET-001"
        assert sample_detector.severity == Severity.HIGH
        assert sample_detector.auto_fixable is False
        assert sample_detector.check_dims == ["tree_hash", "interface"]

    def test_drift_event_creation(self, sample_event):
        assert sample_event.module_id == "MOD-INF-023"
        assert sample_event.state == DriftState.DETECTED
        assert isinstance(sample_event.event_id, uuid.UUID)

    def test_drift_budget_tier_budget(self):
        assert DriftBudget.tier_budget("P0") == 5
        assert DriftBudget.tier_budget("P1") == 20
        assert DriftBudget.tier_budget("P2") == 50
        assert DriftBudget.tier_budget("P3") == 100
        assert DriftBudget.tier_budget("UNKNOWN") == 20

    def test_drift_budget_consume(self):
        b = DriftBudget(module_id="MOD-X", tier="P0", monthly_budget=5, remaining=5)
        b.consume(1)
        assert b.consumed == 1
        assert b.remaining == 4
        assert not b.is_exhausted()

    def test_drift_budget_exhaustion(self):
        b = DriftBudget(module_id="MOD-X", tier="P0", monthly_budget=2, remaining=2)
        b.consume(1)
        b.consume(1)
        assert b.remaining == 0
        assert b.hard_limit_reached is True
        assert b.is_exhausted()

    def test_scan_result_defaults(self):
        sr = ScanResult(scan_id=uuid.uuid4(), detectors_run=0, total_drift_events=0)
        assert sr.storm_mode_triggered is False
        assert sr.events == []

    def test_drift_report_defaults(self):
        dr = DriftReport()
        assert dr.active_drift_count == 0
        assert dr.scan_summary == ""

    def test_bulk_drift_event_creation(self):
        bulk = BulkDriftEvent(
            event_id=uuid.uuid4(),
            scan_id=uuid.uuid4(),
            affected_modules=["MOD-A"],
            dimension_groups={"arch": 3},
            is_expected=True,
            is_unexpected=False,
        )
        assert bulk.affected_modules == ["MOD-A"]
        assert bulk.dimension_groups == {"arch": 3}


class TestDriftEngineHelpers:
    def test_filter_detectors_light(self, sample_detector, sample_detector_medium, sample_detector_low):
        detectors = [sample_detector, sample_detector_medium, sample_detector_low]
        result = _filter_detectors_by_level(detectors, ScanLevel.LIGHT, None)
        assert len(result) == 1
        assert result[0].severity == Severity.HIGH

    def test_filter_detectors_standard(self, sample_detector, sample_detector_medium, sample_detector_low):
        detectors = [sample_detector, sample_detector_medium, sample_detector_low]
        result = _filter_detectors_by_level(detectors, ScanLevel.STANDARD, None)
        assert len(result) == 2
        assert all(d.severity in (Severity.HIGH, Severity.MEDIUM) for d in result)

    def test_filter_detectors_deep(self, sample_detector, sample_detector_medium, sample_detector_low):
        detectors = [sample_detector, sample_detector_medium, sample_detector_low]
        result = _filter_detectors_by_level(detectors, ScanLevel.DEEP, None)
        assert len(result) == 3

    def test_filter_detectors_scope(self, sample_detector, sample_detector_medium, sample_detector_low):
        detectors = [sample_detector, sample_detector_medium, sample_detector_low]
        result = _filter_detectors_by_level(detectors, ScanLevel.DEEP, ["DET-002"])
        assert len(result) == 1
        assert result[0].id == "DET-002"

    def test_max_parallel(self):
        assert _max_parallel(ScanLevel.LIGHT) == 2
        assert _max_parallel(ScanLevel.STANDARD) == 4
        assert _max_parallel(ScanLevel.DEEP) == 8

    def test_detect_expected_storm_refactor(self):
        assert _detect_expected_storm("REFACTOR: split module") is True

    def test_detect_expected_storm_migration(self):
        assert _detect_expected_storm("MIGRATION: move to new API") is True

    def test_detect_expected_storm_normal(self):
        assert _detect_expected_storm("fix: typo in docs") is False

    def test_event_to_dict_roundtrip(self, sample_event):
        d = _event_to_dict(sample_event)
        assert d["module_id"] == "MOD-INF-023"
        assert d["state"] == "DETECTED"
        parsed = _parse_event(d)
        assert parsed.module_id == sample_event.module_id
        assert parsed.detector_id == sample_event.detector_id
        assert parsed.state == DriftState.DETECTED

    def test_create_bulk_event(self, sample_event):
        scan_id = uuid.uuid4()
        events = [sample_event]
        bulk = _create_bulk_event(scan_id, events, commit_message="REFACTOR: cleanup")
        assert bulk.scan_id == scan_id
        assert bulk.is_expected is True
        assert bulk.is_unexpected is False
        assert sample_event.event_id in bulk.child_event_ids

    def test_create_bulk_event_unexpected(self, sample_event):
        scan_id = uuid.uuid4()
        events = [sample_event]
        bulk = _create_bulk_event(scan_id, events, commit_message="fix: typo")
        assert bulk.is_expected is False
        assert bulk.is_unexpected is True

    def test_load_detector_registry_missing_file(self, tmp_path):
        result = load_detector_registry(str(tmp_path / "nonexistent.yaml"))
        assert result == []

    def test_load_detector_registry_valid(self, tmp_path):
        registry = {
            "detectors": {
                "existing": [
                    {
                        "id": "DET-R1",
                        "drift_dimension": "architecture",
                        "severity": "HIGH",
                        "category": "structural",
                    }
                ],
                "new": [
                    {
                        "id": "DET-R2",
                        "drift_dimension": "interface",
                        "severity": "MEDIUM",
                        "category": "contract",
                        "auto_fixable": True,
                    }
                ],
            }
        }
        reg_path = tmp_path / "test_registry.yaml"
        import yaml

        with open(reg_path, "w", encoding="utf-8") as f:
            yaml.dump(registry, f)
        result = load_detector_registry(str(reg_path))
        assert len(result) == 2
        assert result[0].id == "DET-R1"
        assert result[1].id == "DET-R2"
        assert result[1].auto_fixable is True

    def test_build_report(self, sample_event):
        scan_result = ScanResult(
            scan_id=uuid.uuid4(),
            detectors_run=5,
            total_drift_events=1,
            new_events=[sample_event.event_id],
            events=[sample_event],
        )
        report = build_report(scan_result)
        assert report.active_drift_count == 1
        assert isinstance(report.module_health_index, dict)
        assert len(report.top_drift_dimensions) > 0
        assert report.top_drift_dimensions[0][0] == "architecture"

    def test_build_report_storm(self):
        events = []
        for i in range(STORM_THRESHOLD + 1):
            events.append(
                DriftEvent(
                    event_id=uuid.uuid4(),
                    module_id=f"MOD-{i:03d}",
                    detector_id="DET-STORM",
                    drift_dimension="architecture",
                    baseline_version="0.1.0",
                    state=DriftState.DETECTED,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
            )
        scan_result = ScanResult(
            scan_id=uuid.uuid4(),
            detectors_run=1,
            total_drift_events=len(events),
            new_events=[e.event_id for e in events],
            storm_mode_triggered=True,
            events=events,
        )
        report = build_report(scan_result)
        assert report.active_drift_count == STORM_THRESHOLD + 1


class TestBaselineManager:
    def test_instantiation(self, baseline_mgr, tmp_project):
        baselines_root = os.path.join(str(tmp_project), "data", "drift_baselines")
        assert baseline_mgr._baselines_root == baselines_root
        assert os.path.isdir(baselines_root)

    def test_module_baseline_dir(self, baseline_mgr):
        d = baseline_mgr.module_baseline_dir("MOD-INF-023")
        assert d.endswith("MOD-INF-023")

    def test_snapshot_tree_hash(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        hashes = baseline_mgr.snapshot_tree_hash(module_dir)
        assert len(hashes) > 0
        for rel, sha in hashes.items():
            assert len(sha) == 64

    def test_snapshot_tree_hash_nonexistent(self, baseline_mgr):
        hashes = baseline_mgr.snapshot_tree_hash("/nonexistent/path")
        assert hashes == {}

    def test_snapshot_interface(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        iface = baseline_mgr.snapshot_interface(module_dir)
        assert len(iface) > 0
        core_sigs = iface.get(os.path.join("core.py"), [])
        assert any("def hello" in s for s in core_sigs)
        assert any("class Foo" in s for s in core_sigs)

    def test_snapshot_interface_nonexistent(self, baseline_mgr):
        iface = baseline_mgr.snapshot_interface("/nonexistent/path")
        assert iface == {}

    def test_snapshot_import_graph(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        graph = baseline_mgr.snapshot_import_graph(module_dir)
        assert isinstance(graph, dict)

    def test_snapshot_config_empty(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        config = baseline_mgr.snapshot_config(module_dir)
        assert config == {}

    def test_capture(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        snapshot = baseline_mgr.capture("MOD-TEST-CAPTURE", module_dir)
        assert snapshot["module_id"] == "MOD-TEST-CAPTURE"
        assert snapshot["version"] == 1
        assert "tree_hash" in snapshot
        assert "interface_snapshot" in snapshot
        assert "import_graph" in snapshot

    def test_capture_increments_version(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        s1 = baseline_mgr.capture("MOD-VER-TEST", module_dir)
        s2 = baseline_mgr.capture("MOD-VER-TEST", module_dir)
        assert s1["version"] == 1
        assert s2["version"] == 2

    def test_load_baseline(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        baseline_mgr.capture("MOD-LOAD-TEST", module_dir)
        loaded = baseline_mgr.load_baseline("MOD-LOAD-TEST", "v001")
        assert loaded is not None
        assert loaded["module_id"] == "MOD-LOAD-TEST"
        assert loaded["version"] == 1

    def test_load_baseline_missing(self, baseline_mgr):
        loaded = baseline_mgr.load_baseline("MOD-NONEXISTENT", "v999")
        assert loaded is None

    def test_list_versions(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        baseline_mgr.capture("MOD-LIST-TEST", module_dir)
        baseline_mgr.capture("MOD-LIST-TEST", module_dir)
        versions = baseline_mgr.list_versions("MOD-LIST-TEST")
        assert len(versions) == 2
        assert "v001" in versions
        assert "v002" in versions

    def test_full_diff_no_changes(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        baseline_mgr.capture("MOD-DIFF-NOCHANGE", module_dir)
        report = baseline_mgr.full_diff("MOD-DIFF-NOCHANGE", module_dir)
        assert isinstance(report, DiffReport)
        assert report.module_id == "MOD-DIFF-NOCHANGE"
        assert report.added == []
        assert report.removed == []

    def test_full_diff_with_addition(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        baseline_mgr.capture("MOD-DIFF-ADD", module_dir)
        (tmp_project / "src" / "zephyr" / "sample_mod" / "new_file.py").write_text(
            "def new_func(): pass\n", encoding="utf-8"
        )
        report = baseline_mgr.full_diff("MOD-DIFF-ADD", module_dir)
        assert len(report.added) > 0

    def test_full_diff_with_modification(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        baseline_mgr.capture("MOD-DIFF-MOD", module_dir)
        (tmp_project / "src" / "zephyr" / "sample_mod" / "core.py").write_text(
            "def hello():\n    return 'changed'\n\nclass Bar:\n    pass\n",
            encoding="utf-8",
        )
        report = baseline_mgr.full_diff("MOD-DIFF-MOD", module_dir)
        assert len(report.modified) > 0 or len(report.contract_changes) > 0

    def test_full_diff_with_removal(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        baseline_mgr.capture("MOD-DIFF-REM", module_dir)
        os.remove(os.path.join(module_dir, "core.py"))
        report = baseline_mgr.full_diff("MOD-DIFF-REM", module_dir)
        assert len(report.removed) > 0

    def test_contract_diff(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        baseline_mgr.capture("MOD-CONTRACT", module_dir)
        (tmp_project / "src" / "zephyr" / "sample_mod" / "core.py").write_text(
            "def goodbye():\n    return 'bye'\n\nclass Baz:\n    pass\n",
            encoding="utf-8",
        )
        report = baseline_mgr.contract_diff("MOD-CONTRACT", module_dir)
        assert report.diff_type == "contract_only"
        assert len(report.contract_changes) > 0

    def test_slow_creep_check_single_version(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        baseline_mgr.capture("MOD-CREEP", module_dir)
        report = baseline_mgr.slow_creep_check("MOD-CREEP", module_dir)
        assert report.diff_type == "slow_creep"

    def test_slow_creep_check_multi_version(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        baseline_mgr.capture("MOD-CREEP2", module_dir)
        (tmp_project / "src" / "zephyr" / "sample_mod" / "core.py").write_text(
            "def hello():\n    return 'changed'\n\ndef extra(): pass\n\nclass Foo:\n    pass\n",
            encoding="utf-8",
        )
        baseline_mgr.capture("MOD-CREEP2", module_dir)
        report = baseline_mgr.slow_creep_check("MOD-CREEP2", module_dir)
        assert report.diff_type == "slow_creep"

    def test_on_phase_complete(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        snapshot = baseline_mgr.on_phase_complete("MOD-PHASE", module_dir, "phase_1")
        assert snapshot["module_id"] == "MOD-PHASE"

    def test_manual_capture(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        snapshot = baseline_mgr.manual_capture("MOD-MANUAL", module_dir)
        assert snapshot["module_id"] == "MOD-MANUAL"

    def test_max_versions_cleanup(self, baseline_mgr, tmp_project):
        module_dir = str(tmp_project / "src" / "zephyr" / "sample_mod")
        baseline_mgr.MAX_VERSIONS = 3
        for i in range(5):
            baseline_mgr.capture("MOD-MAXVER", module_dir)
        versions = baseline_mgr.list_versions("MOD-MAXVER")
        assert len(versions) <= 3
        baseline_mgr.MAX_VERSIONS = 10


class TestDriftInfrastructure:
    def test_maintenance_window(self):
        from zephyr.gov_drift.drift_infrastructure import (
            declare_maintenance_window,
            get_maintenance_window,
        )

        window = declare_maintenance_window(hours=1)
        assert window.is_shadow_mode is True
        assert window.time_remaining().total_seconds() > 0
        retrieved = get_maintenance_window()
        assert retrieved is not None

    def test_budget_consume(self):
        from zephyr.gov_drift.drift_infrastructure import consume_budget, get_or_create_budget

        budget = get_or_create_budget("MOD-BUDGET-TEST", "P0")
        assert budget.monthly_budget == 5
        exhausted = consume_budget("MOD-BUDGET-TEST", "P0")
        assert isinstance(exhausted, bool)

    def test_differential_detection_drift(self):
        from zephyr.gov_drift.drift_infrastructure import differential_detection

        diffs = [{"drift_dimension": "architecture"}]
        report = differential_detection("MOD-ENV-TEST", diffs, {})
        assert report.is_true_drift is True
        assert report.diff_type == "DRIFT"

    def test_differential_detection_env_only(self):
        from zephyr.gov_drift.drift_infrastructure import differential_detection

        diffs = [{"drift_dimension": "env_python_version"}]
        report = differential_detection("MOD-ENV-TEST2", diffs, {"python": "3.12"})
        assert report.diff_type == "ENV_DIFF"

    def test_partial_deployment_detection(self):
        from zephyr.gov_drift.drift_infrastructure import detect_partial_deployment

        result = detect_partial_deployment(["MOD-A", "MOD-B"])
        assert result is not None
        assert result.module_a == "MOD-A"
        assert result.module_b == "MOD-B"

    def test_partial_deployment_single_module(self):
        from zephyr.gov_drift.drift_infrastructure import detect_partial_deployment

        result = detect_partial_deployment(["MOD-A"])
        assert result is None
