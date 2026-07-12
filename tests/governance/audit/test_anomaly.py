# [A_test] module_id: SRC-TST-0316 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5
# [MODULE] tests.test_anomaly
# [INVARIANTS] AnomalyDetector.scan returns list; AnomalyResult.to_dict serializable
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_anomaly.py -q
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.gov_audit.anomaly import AnomalyDetector, AnomalyResult, AnomalySignature
from zephyr.gov_audit.models import AuditEventType


class TestAnomalySignature:
    def test_enum_has_thirteen_members(self):
        assert len(AnomalySignature) == 13

    def test_values_are_anm_prefixed(self):
        for member in AnomalySignature:
            assert member.value.startswith("ANM-")


class TestAnomalyResult:
    def test_to_dict_contains_all_fields(self):
        result = AnomalyResult(
            signature=AnomalySignature.UNAUTHORIZED_ACCESS,
            severity="high",
            description="test",
            evidence={"key": "val"},
            score=0.9,
        )
        d = result.to_dict()
        assert d["signature"] == "ANM-001"
        assert d["name"] == "UNAUTHORIZED_ACCESS"
        assert d["severity"] == "high"
        assert d["description"] == "test"
        assert d["evidence"] == {"key": "val"}
        assert d["score"] == 0.9
        assert "detected_at" in d

    def test_default_evidence_and_score(self):
        result = AnomalyResult(
            signature=AnomalySignature.BULK_DELETE,
            severity="critical",
            description="bulk",
        )
        assert result.evidence == {}
        assert result.score == 0.0

    def test_detected_at_is_iso_format(self):
        result = AnomalyResult(
            signature=AnomalySignature.GATE_BYPASS,
            severity="critical",
            description="gate",
        )
        assert result.detected_at != ""
        assert "T" in result.detected_at


class TestAnomalyDetectorInstantiation:
    def test_default_path(self):
        detector = AnomalyDetector()
        assert detector._event_log_path == Path("data/audit-trail/events.jsonl")

    def test_custom_path(self, tmp_path):
        p = tmp_path / "custom.jsonl"
        detector = AnomalyDetector(p)
        assert detector._event_log_path == p

    def test_string_path_converted(self):
        detector = AnomalyDetector("data/other/events.jsonl")
        assert isinstance(detector._event_log_path, Path)


class TestAnomalyDetectorScan:
    def test_scan_empty_events(self):
        detector = AnomalyDetector()
        results = detector.scan(events=[])
        assert results == []

    def test_scan_none_events_loads_from_file(self, tmp_path):
        log_file = tmp_path / "events.jsonl"
        log_file.write_text("", encoding="utf-8")
        detector = AnomalyDetector(log_file)
        results = detector.scan(events=None)
        assert results == []

    def test_scan_unauthorized_access_permission_violation(self):
        detector = AnomalyDetector()
        events = [
            {"event_type": AuditEventType.PERMISSION_VIOLATION.value, "agent_id": "a1", "target_path": "f1"},
        ]
        results = detector.scan(events=events)
        ua = [r for r in results if r.signature == AnomalySignature.UNAUTHORIZED_ACCESS]
        assert len(ua) == 1
        assert ua[0].score == 0.9

    def test_scan_unauthorized_access_gate_fail(self):
        detector = AnomalyDetector()
        events = [
            {"event_type": AuditEventType.GATE_FAIL.value, "agent_id": "a2", "target_path": "f2"},
        ]
        results = detector.scan(events=events)
        ua = [r for r in results if r.signature == AnomalySignature.UNAUTHORIZED_ACCESS]
        assert len(ua) == 1

    def test_scan_unauthorized_access_denied_status(self):
        detector = AnomalyDetector()
        events = [{"status": "denied", "agent_id": "a1", "target_path": "f1"}]
        results = detector.scan(events=events)
        ua = [r for r in results if r.signature == AnomalySignature.UNAUTHORIZED_ACCESS]
        assert len(ua) == 1

    def test_scan_unauthorized_access_blocked_status(self):
        detector = AnomalyDetector()
        events = [{"status": "blocked", "agent_id": "a1", "target_path": "f1"}]
        results = detector.scan(events=events)
        ua = [r for r in results if r.signature == AnomalySignature.UNAUTHORIZED_ACCESS]
        assert len(ua) == 1

    def test_scan_unauthorized_access_rejected_status(self):
        detector = AnomalyDetector()
        events = [{"status": "rejected", "agent_id": "a1", "target_path": "f1"}]
        results = detector.scan(events=events)
        ua = [r for r in results if r.signature == AnomalySignature.UNAUTHORIZED_ACCESS]
        assert len(ua) == 1

    def test_scan_bulk_delete_triggers_at_three(self):
        detector = AnomalyDetector()
        events = [
            {"event_type": "file_delete", "agent_id": "a1"},
            {"event_type": "file_delete", "agent_id": "a1"},
            {"event_type": "file_delete", "agent_id": "a1"},
        ]
        results = detector.scan(events=events)
        bd = [r for r in results if r.signature == AnomalySignature.BULK_DELETE]
        assert len(bd) == 1
        assert bd[0].severity == "critical"

    def test_scan_bulk_delete_below_threshold(self):
        detector = AnomalyDetector()
        events = [
            {"event_type": "file_delete", "agent_id": "a1"},
            {"event_type": "file_delete", "agent_id": "a1"},
        ]
        results = detector.scan(events=events)
        bd = [r for r in results if r.signature == AnomalySignature.BULK_DELETE]
        assert len(bd) == 0

    def test_scan_gate_bypass(self):
        detector = AnomalyDetector()
        events = [{"event_type": AuditEventType.GATE_BYPASS.value, "agent_id": "a1"}]
        results = detector.scan(events=events)
        gb = [r for r in results if r.signature == AnomalySignature.GATE_BYPASS]
        assert len(gb) == 1
        assert gb[0].severity == "critical"

    def test_scan_off_hours_before_six(self):
        detector = AnomalyDetector()
        events = [{"timestamp": "2026-05-22T03:00:00+00:00", "agent_id": "a1"}]
        results = detector.scan(events=events)
        oh = [r for r in results if r.signature == AnomalySignature.OFF_HOURS_ACTIVITY]
        assert len(oh) == 1
        assert oh[0].evidence["hour"] == 3

    def test_scan_off_hours_after_twenty_two(self):
        detector = AnomalyDetector()
        events = [{"timestamp": "2026-05-22T23:00:00+00:00", "agent_id": "a1"}]
        results = detector.scan(events=events)
        oh = [r for r in results if r.signature == AnomalySignature.OFF_HOURS_ACTIVITY]
        assert len(oh) == 1

    def test_scan_off_hours_during_business(self):
        detector = AnomalyDetector()
        events = [{"timestamp": "2026-05-22T10:00:00+00:00", "agent_id": "a1"}]
        results = detector.scan(events=events)
        oh = [r for r in results if r.signature == AnomalySignature.OFF_HOURS_ACTIVITY]
        assert len(oh) == 0

    def test_scan_high_frequency(self):
        detector = AnomalyDetector()
        events = []
        for i in range(12):
            events.append(
                {
                    "agent_id": "a1",
                    "timestamp": f"2026-05-22T10:00:{i:02d}+00:00",
                }
            )
        results = detector.scan(events=events)
        hf = [r for r in results if r.signature == AnomalySignature.HIGH_FREQUENCY]
        assert len(hf) == 1
        assert hf[0].evidence["max_ops_per_minute"] >= 10

    def test_scan_high_frequency_below_threshold(self):
        detector = AnomalyDetector()
        events = [
            {"agent_id": "a1", "timestamp": "2026-05-22T10:00:00+00:00"},
            {"agent_id": "a1", "timestamp": "2026-05-22T10:05:00+00:00"},
        ]
        results = detector.scan(events=events)
        hf = [r for r in results if r.signature == AnomalySignature.HIGH_FREQUENCY]
        assert len(hf) == 0

    def test_scan_cross_agent_conflict(self):
        detector = AnomalyDetector()
        events = [
            {"agent_id": "a1", "target_path": "shared.py"},
            {"agent_id": "a2", "target_path": "shared.py"},
            {"agent_id": "a3", "target_path": "shared.py"},
        ]
        results = detector.scan(events=events)
        ca = [r for r in results if r.signature == AnomalySignature.CROSS_AGENT_CONFLICT]
        assert len(ca) == 1
        assert len(set(ca[0].evidence["agents"])) >= 3

    def test_scan_cross_agent_conflict_below_threshold(self):
        detector = AnomalyDetector()
        events = [
            {"agent_id": "a1", "target_path": "shared.py"},
            {"agent_id": "a2", "target_path": "shared.py"},
        ]
        results = detector.scan(events=events)
        ca = [r for r in results if r.signature == AnomalySignature.CROSS_AGENT_CONFLICT]
        assert len(ca) == 0

    def test_scan_impersonation(self):
        detector = AnomalyDetector()
        events = [{"event_type": AuditEventType.AGENT_IMPERSONATION.value, "agent_id": "a1"}]
        results = detector.scan(events=events)
        imp = [r for r in results if r.signature == AnomalySignature.IMPERSONATION]
        assert len(imp) == 1
        assert imp[0].severity == "critical"

    def test_scan_delegation_chain_anomaly_depth_exceeded(self):
        detector = AnomalyDetector()
        events = [{"agent_id": "a1", "delegation_depth": 6}]
        results = detector.scan(events=events)
        dc = [r for r in results if r.signature == AnomalySignature.DELEGATION_CHAIN_ANOMALY]
        assert len(dc) == 1

    def test_scan_delegation_chain_anomaly_depth_within_limit(self):
        detector = AnomalyDetector()
        events = [{"agent_id": "a1", "delegation_depth": 5}]
        results = detector.scan(events=events)
        dc = [r for r in results if r.signature == AnomalySignature.DELEGATION_CHAIN_ANOMALY]
        assert len(dc) == 0

    def test_scan_collusion_pattern(self):
        detector = AnomalyDetector()
        events = [{"event_type": AuditEventType.COLLUSION_PATTERN.value, "agent_id": "a1"}]
        results = detector.scan(events=events)
        cp = [r for r in results if r.signature == AnomalySignature.COLLUSION_PATTERN]
        assert len(cp) == 1

    def test_scan_indirect_operation_flag(self):
        detector = AnomalyDetector()
        events = [{"indirect_operation": True, "indirect_method": "proxy", "agent_id": "a1"}]
        results = detector.scan(events=events)
        io = [r for r in results if r.signature == AnomalySignature.INDIRECT_OPERATION]
        assert len(io) == 1

    def test_scan_indirect_operation_event_type(self):
        detector = AnomalyDetector()
        events = [{"event_type": AuditEventType.INDIRECT_OPERATION.value, "agent_id": "a1"}]
        results = detector.scan(events=events)
        io = [r for r in results if r.signature == AnomalySignature.INDIRECT_OPERATION]
        assert len(io) == 1

    def test_scan_trust_trend_declining(self):
        detector = AnomalyDetector()
        events = [
            {"agent_id": "a1", "trust-score": 0.9},
            {"agent_id": "a1", "trust-score": 0.8},
            {"agent_id": "a1", "trust-score": 0.7},
            {"agent_id": "a1", "trust-score": 0.2},
            {"agent_id": "a1", "trust-score": 0.1},
            {"agent_id": "a1", "trust-score": 0.05},
        ]
        results = detector.scan(events=events)
        tt = [r for r in results if r.signature == AnomalySignature.TRUST_TREND]
        assert len(tt) >= 1

    def test_scan_trust_trend_stable(self):
        detector = AnomalyDetector()
        events = [
            {"agent_id": "a1", "trust-score": 0.8},
            {"agent_id": "a1", "trust-score": 0.8},
            {"agent_id": "a1", "trust-score": 0.8},
        ]
        results = detector.scan(events=events)
        tt = [r for r in results if r.signature == AnomalySignature.TRUST_TREND]
        assert len(tt) == 0

    def test_scan_dry_run_mismatch(self):
        detector = AnomalyDetector()
        events = [{"dry_run": True, "dry_run_real_diff": True, "dry_run_real_diff_score": 0.5, "agent_id": "a1"}]
        results = detector.scan(events=events)
        dr = [r for r in results if r.signature == AnomalySignature.DRY_RUN_MISMATCH]
        assert len(dr) == 1
        assert dr[0].evidence["diff_score"] == 0.5

    def test_scan_dry_run_mismatch_below_threshold(self):
        detector = AnomalyDetector()
        events = [{"dry_run": True, "dry_run_real_diff": True, "dry_run_real_diff_score": 0.2, "agent_id": "a1"}]
        results = detector.scan(events=events)
        dr = [r for r in results if r.signature == AnomalySignature.DRY_RUN_MISMATCH]
        assert len(dr) == 0

    def test_scan_dry_run_mismatch_event_type(self):
        detector = AnomalyDetector()
        events = [{"event_type": AuditEventType.DRY_RUN_MISMATCH.value, "agent_id": "a1"}]
        results = detector.scan(events=events)
        dr = [r for r in results if r.signature == AnomalySignature.DRY_RUN_MISMATCH]
        assert len(dr) == 1


class TestBoundaryConditions:
    def test_bulk_delete_exactly_three(self):
        detector = AnomalyDetector()
        events = [{"event_type": "file_delete", "agent_id": "a1"} for _ in range(3)]
        results = detector.scan(events=events)
        bd = [r for r in results if r.signature == AnomalySignature.BULK_DELETE]
        assert len(bd) == 1

    def test_delegation_depth_exactly_five_not_triggered(self):
        detector = AnomalyDetector()
        events = [{"agent_id": "a1", "delegation_depth": 5}]
        results = detector.scan(events=events)
        dc = [r for r in results if r.signature == AnomalySignature.DELEGATION_CHAIN_ANOMALY]
        assert len(dc) == 0

    def test_delegation_depth_six_triggered(self):
        detector = AnomalyDetector()
        events = [{"agent_id": "a1", "delegation_depth": 6}]
        results = detector.scan(events=events)
        dc = [r for r in results if r.signature == AnomalySignature.DELEGATION_CHAIN_ANOMALY]
        assert len(dc) == 1

    def test_dry_run_diff_score_exactly_threshold(self):
        detector = AnomalyDetector()
        events = [{"dry_run": True, "dry_run_real_diff": True, "dry_run_real_diff_score": 0.3, "agent_id": "a1"}]
        results = detector.scan(events=events)
        dr = [r for r in results if r.signature == AnomalySignature.DRY_RUN_MISMATCH]
        assert len(dr) == 0

    def test_off_hours_boundary_hour_six(self):
        detector = AnomalyDetector()
        events = [{"timestamp": "2026-05-22T06:00:00+00:00", "agent_id": "a1"}]
        results = detector.scan(events=events)
        oh = [r for r in results if r.signature == AnomalySignature.OFF_HOURS_ACTIVITY]
        assert len(oh) == 0

    def test_off_hours_boundary_hour_twenty_two(self):
        detector = AnomalyDetector()
        events = [{"timestamp": "2026-05-22T22:00:00+00:00", "agent_id": "a1"}]
        results = detector.scan(events=events)
        oh = [r for r in results if r.signature == AnomalySignature.OFF_HOURS_ACTIVITY]
        assert len(oh) == 0

    def test_cross_agent_exactly_two_not_triggered(self):
        detector = AnomalyDetector()
        events = [
            {"agent_id": "a1", "target_path": "f.py"},
            {"agent_id": "a2", "target_path": "f.py"},
        ]
        results = detector.scan(events=events)
        ca = [r for r in results if r.signature == AnomalySignature.CROSS_AGENT_CONFLICT]
        assert len(ca) == 0

    def test_invalid_timestamp_ignored(self):
        detector = AnomalyDetector()
        events = [{"timestamp": "not-a-date", "agent_id": "a1"}]
        results = detector.scan(events=events)
        oh = [r for r in results if r.signature == AnomalySignature.OFF_HOURS_ACTIVITY]
        assert len(oh) == 0
