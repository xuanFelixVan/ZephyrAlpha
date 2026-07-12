# [A_test] module_id: SRC-TST-0342 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5
# [MODULE] tests.test_audit_anomaly
# [INVARIANTS] AnomalyDetector.scan returns list; AnomalyResult.to_dict serializable
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.gov_audit.anomaly import AnomalyDetector, AnomalyResult, AnomalySignature


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


class TestAnomalyDetectorInstantiation:
    def test_default_path(self):
        detector = AnomalyDetector()
        assert detector._event_log_path == Path("data/audit-trail/events.jsonl")

    def test_custom_path(self, tmp_path):
        p = tmp_path / "custom.jsonl"
        detector = AnomalyDetector(p)
        assert detector._event_log_path == p


class TestAnomalyDetectorScan:
    def test_scan_empty_events(self):
        detector = AnomalyDetector()
        results = detector.scan(events=[])
        assert results == []

    def test_scan_unauthorized_access(self):
        detector = AnomalyDetector()
        events = [
            {"event_type": "permission_violation", "agent_id": "a1", "target_path": "f1"},
            {"event_type": "gate_fail", "agent_id": "a2", "target_path": "f2"},
        ]
        results = detector.scan(events=events)
        ua_results = [r for r in results if r.signature == AnomalySignature.UNAUTHORIZED_ACCESS]
        assert len(ua_results) == 2

    def test_scan_bulk_delete(self):
        detector = AnomalyDetector()
        events = [
            {"event_type": "file_delete", "agent_id": "a1"},
            {"event_type": "file_delete", "agent_id": "a1"},
            {"event_type": "file_delete", "agent_id": "a1"},
        ]
        results = detector.scan(events=events)
        bd_results = [r for r in results if r.signature == AnomalySignature.BULK_DELETE]
        assert len(bd_results) == 1
        assert bd_results[0].severity == "critical"

    def test_scan_gate_bypass(self):
        detector = AnomalyDetector()
        events = [{"event_type": "gate_bypass", "agent_id": "a1"}]
        results = detector.scan(events=events)
        gb_results = [r for r in results if r.signature == AnomalySignature.GATE_BYPASS]
        assert len(gb_results) == 1

    def test_scan_off_hours(self):
        detector = AnomalyDetector()
        events = [{"timestamp": "2026-05-22T03:00:00+00:00", "agent_id": "a1"}]
        results = detector.scan(events=events)
        oh_results = [r for r in results if r.signature == AnomalySignature.OFF_HOURS_ACTIVITY]
        assert len(oh_results) == 1

    def test_scan_denied_status(self):
        detector = AnomalyDetector()
        events = [{"status": "denied", "agent_id": "a1", "target_path": "f1"}]
        results = detector.scan(events=events)
        ua_results = [r for r in results if r.signature == AnomalySignature.UNAUTHORIZED_ACCESS]
        assert len(ua_results) == 1

    def test_scan_impersonation(self):
        detector = AnomalyDetector()
        events = [{"event_type": "agent_impersonation", "agent_id": "a1"}]
        results = detector.scan(events=events)
        imp_results = [r for r in results if r.signature == AnomalySignature.IMPERSONATION]
        assert len(imp_results) == 1

    def test_scan_delegation_chain_anomaly_depth(self):
        detector = AnomalyDetector()
        events = [{"delegation_depth": 6, "agent_id": "a1"}]
        results = detector.scan(events=events)
        dc_results = [r for r in results if r.signature == AnomalySignature.DELEGATION_CHAIN_ANOMALY]
        assert len(dc_results) == 1

    def test_scan_indirect_operation_flag(self):
        detector = AnomalyDetector()
        events = [{"indirect_operation": True, "indirect_method": "proxy", "agent_id": "a1"}]
        results = detector.scan(events=events)
        io_results = [r for r in results if r.signature == AnomalySignature.INDIRECT_OPERATION]
        assert len(io_results) == 1

    def test_scan_dry_run_mismatch(self):
        detector = AnomalyDetector()
        events = [{"dry_run": True, "dry_run_real_diff": True, "dry_run_real_diff_score": 0.5, "agent_id": "a1"}]
        results = detector.scan(events=events)
        dr_results = [r for r in results if r.signature == AnomalySignature.DRY_RUN_MISMATCH]
        assert len(dr_results) == 1

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
        tt_results = [r for r in results if r.signature == AnomalySignature.TRUST_TREND]
        assert len(tt_results) >= 1

    def test_scan_none_events_loads_from_file(self, tmp_path):
        log_file = tmp_path / "events.jsonl"
        log_file.write_text("", encoding="utf-8")
        detector = AnomalyDetector(log_file)
        results = detector.scan(events=None)
        assert results == []
