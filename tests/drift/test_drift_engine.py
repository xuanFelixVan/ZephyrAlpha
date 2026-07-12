# [A_test] module_id: SRC-TST-0774 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_drift_engine
# [INVARIANTS] 39检测器必须全部执行;不可跳过检测器
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI/CD;drift_engine
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_drift_engine.py
# [TTL] task_bound

import uuid

import yaml

from zephyr.gov_drift.drift_engine import (
    _create_drift_event,
    _detect_expected_storm,
    _event_to_dict,
    _filter_detectors_by_level,
    _max_parallel,
    _parse_event,
    build_report,
    load_detector_registry,
)
from zephyr.gov_drift.drift_models import (
    Detector,
    DriftEvent,
    DriftReport,
    DriftState,
    ScanLevel,
    ScanResult,
    Severity,
)


class TestLoadDetectorRegistry:
    def test_returns_empty_for_missing_file(self, tmp_path):
        result = load_detector_registry(str(tmp_path / "nonexistent.yaml"))
        assert result == []

    def test_loads_valid_registry(self, tmp_path):
        registry_data = {
            "detectors": {
                "existing": [
                    {
                        "id": "det-001",
                        "drift_dimension": "D5_semantic",
                        "severity": "HIGH",
                        "category": "structural",
                        "auto_fixable": True,
                        "check_dims": ["D5-SEMANTIC"],
                    }
                ],
                "new": [],
            }
        }
        reg_path = tmp_path / "_detector-registry.yaml"
        reg_path.write_text(yaml.dump(registry_data), encoding="utf-8")
        result = load_detector_registry(str(reg_path))
        assert len(result) == 1
        assert result[0].id == "det-001"
        assert result[0].severity == Severity.HIGH
        assert result[0].auto_fixable is True

    def test_handles_empty_registry(self, tmp_path):
        reg_path = tmp_path / "_detector-registry.yaml"
        reg_path.write_text("detectors: {}\n", encoding="utf-8")
        result = load_detector_registry(str(reg_path))
        assert result == []


class TestDetectExpectedStorm:
    def test_refactor_keyword(self):
        assert _detect_expected_storm("REFACTOR: split module") is True

    def test_migration_keyword(self):
        assert _detect_expected_storm("MIGRATION: move files") is True

    def test_reformat_keyword(self):
        assert _detect_expected_storm("REFORMAT: code style") is True

    def test_rename_keyword(self):
        assert _detect_expected_storm("RENAME: update names") is True

    def test_no_keyword(self):
        assert _detect_expected_storm("fix: minor bug") is False

    def test_case_insensitive(self):
        assert _detect_expected_storm("refactor: lowercase") is True


class TestCreateDriftEvent:
    def test_creates_event(self):
        det = Detector(
            id="det-001",
            drift_dimension="D5_semantic",
            severity=Severity.HIGH,
            category="structural",
        )
        evt = _create_drift_event(det, "test detail")
        assert evt.detector_id == "det-001"
        assert evt.drift_dimension == "D5_semantic"
        assert evt.state == DriftState.DETECTED
        assert evt.resolution_detail == "test detail"


class TestEventToDict:
    def test_roundtrip(self):
        evt = _create_drift_event(
            Detector(id="d1", drift_dimension="D1", severity=Severity.MEDIUM, category="test"),
            "detail",
        )
        d = _event_to_dict(evt)
        assert d["detector_id"] == "d1"
        assert d["state"] == "DETECTED"
        assert d["drift_dimension"] == "D1"
        assert "event_id" in d
        assert "created_at" in d


class TestParseEvent:
    def test_roundtrip_with_event_to_dict(self):
        evt = _create_drift_event(
            Detector(id="d2", drift_dimension="D2", severity=Severity.LOW, category="test"),
            "roundtrip",
        )
        d = _event_to_dict(evt)
        parsed = _parse_event(d)
        assert parsed.detector_id == "d2"
        assert parsed.drift_dimension == "D2"
        assert parsed.state == DriftState.DETECTED

    def test_missing_fields_use_defaults(self):
        parsed = _parse_event({})
        assert parsed.state == DriftState.DETECTED
        assert parsed.module_id == ""
        assert parsed.auto_fixed is False


class TestFilterDetectorsByLevel:
    def test_light_level_filters_high_severity(self):
        detectors = [
            Detector(id="d1", drift_dimension="D1", severity=Severity.HIGH, category="test"),
            Detector(id="d2", drift_dimension="D2", severity=Severity.MEDIUM, category="test"),
            Detector(id="d3", drift_dimension="D3", severity=Severity.LOW, category="test"),
        ]
        result = _filter_detectors_by_level(detectors, ScanLevel.LIGHT, None)
        assert len(result) == 1
        assert result[0].id == "d1"

    def test_standard_level_filters_high_medium(self):
        detectors = [
            Detector(id="d1", drift_dimension="D1", severity=Severity.HIGH, category="test"),
            Detector(id="d2", drift_dimension="D2", severity=Severity.MEDIUM, category="test"),
            Detector(id="d3", drift_dimension="D3", severity=Severity.LOW, category="test"),
        ]
        result = _filter_detectors_by_level(detectors, ScanLevel.STANDARD, None)
        assert len(result) == 2

    def test_deep_level_returns_all(self):
        detectors = [
            Detector(id="d1", drift_dimension="D1", severity=Severity.HIGH, category="test"),
            Detector(id="d2", drift_dimension="D2", severity=Severity.LOW, category="test"),
        ]
        result = _filter_detectors_by_level(detectors, ScanLevel.DEEP, None)
        assert len(result) == 2

    def test_scope_overrides_level(self):
        detectors = [
            Detector(id="d1", drift_dimension="D1", severity=Severity.HIGH, category="test"),
            Detector(id="d2", drift_dimension="D2", severity=Severity.LOW, category="test"),
        ]
        result = _filter_detectors_by_level(detectors, ScanLevel.LIGHT, ["d2"])
        assert len(result) == 1
        assert result[0].id == "d2"


class TestMaxParallel:
    def test_light(self):
        assert _max_parallel(ScanLevel.LIGHT) == 2

    def test_standard(self):
        assert _max_parallel(ScanLevel.STANDARD) == 4

    def test_deep(self):
        assert _max_parallel(ScanLevel.DEEP) == 8


class TestBuildReport:
    def test_builds_report_from_scan_result(self):
        evt = DriftEvent(
            event_id=uuid.uuid4(),
            module_id="MOD-X",
            detector_id="det-001",
            drift_dimension="D5_semantic",
            baseline_version="0.1.0",
            state=DriftState.DETECTED,
            created_at=__import__("datetime").datetime.utcnow(),
            updated_at=__import__("datetime").datetime.utcnow(),
        )
        result = ScanResult(
            scan_id=uuid.uuid4(),
            detectors_run=1,
            total_drift_events=1,
            events=[evt],
        )
        report = build_report(result)
        assert isinstance(report, DriftReport)
        assert report.active_drift_count == 1
        assert "D5_semantic" in report.module_health_index

    def test_empty_events(self):
        result = ScanResult(
            scan_id=uuid.uuid4(),
            detectors_run=0,
            total_drift_events=0,
        )
        report = build_report(result)
        assert report.active_drift_count == 0
