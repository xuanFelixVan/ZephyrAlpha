# [A_test] module_id: SRC-TST-0400 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_ba_handoff_manager
# [INVARIANTS] 交接包完整性不可破坏
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_ba_handoff_manager.py
# [TTL] task_bound

from __future__ import annotations

import json
import os

from zephyr.gov_drift.handoff_manager import (
    FileIntegrityRecord,
    HandoffPackage,
    abort_handoff,
    build_handoff_package,
    load_package,
    resume_workflow,
    serialize_package,
    verify_integrity,
)


class TestFileIntegrityRecord:
    def test_default_fields(self):
        fir = FileIntegrityRecord(file_path="/tmp/test.py")
        assert fir.file_path == "/tmp/test.py"
        assert fir.sha256_before == ""
        assert fir.sha256_after == ""
        assert fir.verified is False

    def test_custom_fields(self):
        fir = FileIntegrityRecord(
            file_path="/tmp/test.py",
            sha256_before="abc123",
            sha256_after="abc123",
            verified=True,
        )
        assert fir.verified is True


class TestHandoffPackage:
    def test_default_fields(self):
        pkg = HandoffPackage(
            package_id="hp-001",
            drift_event_id="de-001",
            detector_id="det-1",
            severity="MAJOR",
            runbook_summary="test runbook",
            git_bisect_log="bisect log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
        )
        assert pkg.package_id == "hp-001"
        assert pkg.status == "READY"
        assert pkg.token_estimate == 0
        assert pkg.owner_id == ""
        assert pkg.created_at != ""
        assert pkg.last_verified_at is None

    def test_custom_fields(self):
        pkg = HandoffPackage(
            package_id="hp-002",
            drift_event_id="de-002",
            detector_id="det-2",
            severity="CRITICAL",
            runbook_summary="critical runbook",
            git_bisect_log="bisect log",
            pre_fix_snapshot={"file.py": "content"},
            baseline_diff={"file.py": ["diff"]},
            related_drift_ids=["rd-1"],
            owner_id="owner-1",
            token_estimate=500,
        )
        assert pkg.owner_id == "owner-1"
        assert pkg.token_estimate == 500


class TestBuildHandoffPackage:
    def test_basic_build(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')", encoding="utf-8")
        pkg = build_handoff_package(
            drift_event_id="de-001",
            detector_id="det-1",
            severity="MAJOR",
            source_file=str(test_file),
            related_files=[str(test_file)],
        )
        assert pkg.drift_event_id == "de-001"
        assert pkg.detector_id == "det-1"
        assert pkg.severity == "MAJOR"
        assert pkg.status == "READY"
        assert len(pkg.file_integrity) == 1

    def test_build_with_no_related_files(self):
        pkg = build_handoff_package(
            drift_event_id="de-002",
            detector_id="det-2",
            severity="LOW",
            source_file="test.py",
            related_files=[],
        )
        assert pkg.file_integrity == []
        assert pkg.pre_fix_snapshot == {}

    def test_build_with_nonexistent_files(self):
        pkg = build_handoff_package(
            drift_event_id="de-003",
            detector_id="det-3",
            severity="HIGH",
            source_file="missing.py",
            related_files=["/nonexistent/file.py"],
        )
        assert len(pkg.file_integrity) == 1
        assert pkg.file_integrity[0].sha256_before == ""

    def test_build_package_id_format(self, tmp_path):
        pkg = build_handoff_package(
            drift_event_id="de/001",
            detector_id="det-1",
            severity="MAJOR",
            source_file="test.py",
            related_files=[],
        )
        assert "/" not in pkg.package_id

    def test_token_estimate_within_max(self):
        pkg = build_handoff_package(
            drift_event_id="de-004",
            detector_id="det-1",
            severity="MAJOR",
            source_file="test.py",
            related_files=[],
            max_tokens=100,
        )
        assert pkg.token_estimate <= 100


class TestSerializePackage:
    def test_serialize_creates_file(self, tmp_path):
        pkg = HandoffPackage(
            package_id="hp-001",
            drift_event_id="de-001",
            detector_id="det-1",
            severity="MAJOR",
            runbook_summary="test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
        )
        output_dir = str(tmp_path / "handoff_output")
        path = serialize_package(pkg, output_dir)
        assert os.path.exists(path)

    def test_serialize_json_content(self, tmp_path):
        pkg = HandoffPackage(
            package_id="hp-002",
            drift_event_id="de-002",
            detector_id="det-2",
            severity="CRITICAL",
            runbook_summary="critical",
            git_bisect_log="log",
            pre_fix_snapshot={"a.py": "content"},
            baseline_diff={},
            related_drift_ids=["rd-1"],
        )
        output_dir = str(tmp_path / "handoff_output2")
        path = serialize_package(pkg, output_dir)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["package_id"] == "hp-002"
        assert data["severity"] == "CRITICAL"

    def test_serialize_safe_id(self, tmp_path):
        pkg = HandoffPackage(
            package_id="hp/with/slashes",
            drift_event_id="de-001",
            detector_id="det-1",
            severity="MAJOR",
            runbook_summary="test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
        )
        output_dir = str(tmp_path / "handoff_output3")
        path = serialize_package(pkg, output_dir)
        assert "/" not in os.path.basename(path)


class TestLoadPackage:
    def test_load_nonexistent_file(self):
        result = load_package("/nonexistent/file.json")
        assert result is None

    def test_load_valid_file(self, tmp_path):
        pkg = HandoffPackage(
            package_id="hp-load",
            drift_event_id="de-load",
            detector_id="det-load",
            severity="MAJOR",
            runbook_summary="load test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
        )
        output_dir = str(tmp_path / "handoff_load")
        path = serialize_package(pkg, output_dir)
        loaded = load_package(path)
        assert loaded is not None
        assert loaded.package_id == "hp-load"
        assert loaded.drift_event_id == "de-load"

    def test_load_invalid_json(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json{{{", encoding="utf-8")
        result = load_package(str(bad_file))
        assert result is None

    def test_roundtrip(self, tmp_path):
        pkg = HandoffPackage(
            package_id="hp-rt",
            drift_event_id="de-rt",
            detector_id="det-rt",
            severity="HIGH",
            runbook_summary="roundtrip test",
            git_bisect_log="bisect log",
            pre_fix_snapshot={"f.py": "code"},
            baseline_diff={"f.py": ["diff line"]},
            related_drift_ids=["rd-1", "rd-2"],
            owner_id="owner-rt",
            token_estimate=300,
        )
        output_dir = str(tmp_path / "handoff_rt")
        path = serialize_package(pkg, output_dir)
        loaded = load_package(path)
        assert loaded is not None
        assert loaded.package_id == pkg.package_id
        assert loaded.severity == pkg.severity
        assert loaded.owner_id == pkg.owner_id
        assert loaded.token_estimate == pkg.token_estimate


class TestVerifyIntegrity:
    def test_verify_with_no_files(self):
        pkg = HandoffPackage(
            package_id="hp-v",
            drift_event_id="de-v",
            detector_id="det-v",
            severity="MAJOR",
            runbook_summary="verify test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
            file_integrity=[],
        )
        ok, violations = verify_integrity(pkg)
        assert ok is True
        assert violations == []
        assert pkg.status == "VERIFIED"

    def test_verify_with_nonexistent_file(self):
        fir = FileIntegrityRecord(file_path="/nonexistent/file.py", sha256_before="abc123")
        pkg = HandoffPackage(
            package_id="hp-v2",
            drift_event_id="de-v2",
            detector_id="det-v2",
            severity="MAJOR",
            runbook_summary="verify test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
            file_integrity=[fir],
        )
        ok, violations = verify_integrity(pkg)
        assert ok is False
        assert len(violations) > 0
        assert pkg.status == "DIVERGED"

    def test_verify_with_matching_sha(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("hello", encoding="utf-8")
        import hashlib

        with open(str(test_file), "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        fir = FileIntegrityRecord(file_path=str(test_file), sha256_before=sha)
        pkg = HandoffPackage(
            package_id="hp-v3",
            drift_event_id="de-v3",
            detector_id="det-v3",
            severity="MAJOR",
            runbook_summary="verify test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
            file_integrity=[fir],
        )
        ok, violations = verify_integrity(pkg)
        assert ok is True
        assert pkg.status == "VERIFIED"

    def test_verify_updates_last_verified_at(self):
        pkg = HandoffPackage(
            package_id="hp-v4",
            drift_event_id="de-v4",
            detector_id="det-v4",
            severity="MAJOR",
            runbook_summary="verify test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
            file_integrity=[],
        )
        verify_integrity(pkg)
        assert pkg.last_verified_at is not None


class TestResumeWorkflow:
    def test_resume_with_verified_package(self):
        pkg = HandoffPackage(
            package_id="hp-r",
            drift_event_id="de-r",
            detector_id="det-r",
            severity="MAJOR",
            runbook_summary="resume test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
            file_integrity=[],
        )
        result = resume_workflow(pkg, "/tmp")
        assert result["status"] == "RESUMED"
        assert result["package_id"] == "hp-r"
        assert "injected_context" in result

    def test_resume_with_diverged_package(self):
        fir = FileIntegrityRecord(file_path="/nonexistent/file.py", sha256_before="abc123")
        pkg = HandoffPackage(
            package_id="hp-r2",
            drift_event_id="de-r2",
            detector_id="det-r2",
            severity="MAJOR",
            runbook_summary="resume test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
            file_integrity=[fir],
        )
        result = resume_workflow(pkg, "/tmp")
        assert result["status"] == "ABORT"

    def test_resume_sets_target_state(self):
        pkg = HandoffPackage(
            package_id="hp-r3",
            drift_event_id="de-r3",
            detector_id="det-r3",
            severity="MAJOR",
            runbook_summary="resume test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
            file_integrity=[],
        )
        resume_workflow(pkg, "/tmp", target_state="FIXING")
        assert pkg.status == "FIXING"


class TestAbortHandoff:
    def test_abort_sets_status(self):
        pkg = HandoffPackage(
            package_id="hp-a",
            drift_event_id="de-a",
            detector_id="det-a",
            severity="MAJOR",
            runbook_summary="abort test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
        )
        result = abort_handoff(pkg, reason="test abort")
        assert pkg.status == "ABORTED"
        assert result["status"] == "ABORTED"
        assert result["reason"] == "test abort"

    def test_abort_default_reason(self):
        pkg = HandoffPackage(
            package_id="hp-a2",
            drift_event_id="de-a2",
            detector_id="det-a2",
            severity="MAJOR",
            runbook_summary="abort test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
        )
        result = abort_handoff(pkg)
        assert "inconsistent" in result["reason"].lower() or result["reason"] != ""

    def test_abort_returns_package_id(self):
        pkg = HandoffPackage(
            package_id="hp-a3",
            drift_event_id="de-a3",
            detector_id="det-a3",
            severity="MAJOR",
            runbook_summary="abort test",
            git_bisect_log="log",
            pre_fix_snapshot={},
            baseline_diff={},
            related_drift_ids=[],
        )
        result = abort_handoff(pkg)
        assert result["package_id"] == "hp-a3"
        assert result["action_required"] == "regenerate_handoff"
