# [A_test] module_id: MOD-GOV_rollback_abuse_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_abuse_detector
# [INVARIANTS] exit_code_44=ABUSE;max_5/h;max_20/day;max_3_same_file
# [MODIFY-GUARD] blueprint.md §4;src/zephyr/rollback/__init__.py
# [CONSUMERS] CI;pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError;json.JSONDecodeError
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from zephyr.infrastructure.rollback.rollback_abuse_detector import (
    AbuseReport,
    RollbackAbuseDetector,
)


class TestAbuseReport:
    def test_instantiation(self):
        r = AbuseReport(
            detected=True,
            rollback_count_1h=6,
            rollback_count_24h=10,
            target_file_abuse=["file1.py"],
            exit_code=44,
            recommendation="ABUSE detected",
        )
        assert r.detected is True
        assert r.rollback_count_1h == 6
        assert r.rollback_count_24h == 10
        assert r.target_file_abuse == ["file1.py"]
        assert r.exit_code == 44
        assert r.recommendation == "ABUSE detected"

    def test_no_abuse_report(self):
        r = AbuseReport(
            detected=False,
            rollback_count_1h=0,
            rollback_count_24h=0,
            target_file_abuse=[],
            exit_code=0,
            recommendation="",
        )
        assert r.detected is False
        assert r.exit_code == 0


class TestRollbackAbuseDetector:
    def test_instantiation_with_path(self, tmp_path):
        detector = RollbackAbuseDetector(project_root=tmp_path)
        assert detector._project_root == tmp_path

    def test_instantiation_default(self):
        detector = RollbackAbuseDetector()
        assert detector._project_root == Path.cwd()

    def test_check_abuse_no_audit_log(self, tmp_path):
        detector = RollbackAbuseDetector(project_root=tmp_path)
        report = detector.check_abuse()
        assert isinstance(report, AbuseReport)
        assert report.detected is False
        assert report.rollback_count_1h == 0
        assert report.rollback_count_24h == 0
        assert report.exit_code == 0

    def test_check_abuse_within_limits(self, tmp_path):
        detector = RollbackAbuseDetector(project_root=tmp_path)
        audit_dir = tmp_path / ".zephyr" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_path = audit_dir / "rollback_operations_audit.jsonl"
        now = datetime.now(UTC)
        entries = []
        for i in range(3):
            entries.append(
                {
                    "timestamp_utc": (now - timedelta(minutes=10)).isoformat(),
                    "details": {"files": [f"file{i}.py"]},
                }
            )
        audit_path.write_text(
            "\n".join(json.dumps(e) for e in entries) + "\n",
            encoding="utf-8",
        )
        report = detector.check_abuse()
        assert report.detected is False
        assert report.rollback_count_1h == 3
        assert report.exit_code == 0

    def test_check_abuse_exceeds_hourly_limit(self, tmp_path):
        detector = RollbackAbuseDetector(project_root=tmp_path)
        audit_dir = tmp_path / ".zephyr" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_path = audit_dir / "rollback_operations_audit.jsonl"
        now = datetime.now(UTC)
        entries = []
        for i in range(6):
            entries.append(
                {
                    "timestamp_utc": (now - timedelta(minutes=10)).isoformat(),
                    "details": {"files": [f"file{i}.py"]},
                }
            )
        audit_path.write_text(
            "\n".join(json.dumps(e) for e in entries) + "\n",
            encoding="utf-8",
        )
        report = detector.check_abuse()
        assert report.detected is True
        assert report.rollback_count_1h == 6
        assert report.exit_code == 44
        assert "ABUSE" in report.recommendation

    def test_check_abuse_same_file_consecutive(self, tmp_path):
        detector = RollbackAbuseDetector(project_root=tmp_path)
        audit_dir = tmp_path / ".zephyr" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_path = audit_dir / "rollback_operations_audit.jsonl"
        now = datetime.now(UTC)
        entries = []
        for _ in range(3):
            entries.append(
                {
                    "timestamp_utc": (now - timedelta(minutes=10)).isoformat(),
                    "details": {"files": ["problematic.py"]},
                }
            )
        audit_path.write_text(
            "\n".join(json.dumps(e) for e in entries) + "\n",
            encoding="utf-8",
        )
        report = detector.check_abuse()
        assert report.detected is True
        assert "problematic.py" in report.target_file_abuse
        assert report.exit_code == 44

    def test_check_abuse_old_entries_not_counted(self, tmp_path):
        detector = RollbackAbuseDetector(project_root=tmp_path)
        audit_dir = tmp_path / ".zephyr" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_path = audit_dir / "rollback_operations_audit.jsonl"
        old_time = datetime.now(UTC) - timedelta(hours=48)
        entries = []
        for i in range(10):
            entries.append(
                {
                    "timestamp_utc": old_time.isoformat(),
                    "details": {"files": [f"old_file{i}.py"]},
                }
            )
        audit_path.write_text(
            "\n".join(json.dumps(e) for e in entries) + "\n",
            encoding="utf-8",
        )
        report = detector.check_abuse()
        assert report.rollback_count_1h == 0
        assert report.rollback_count_24h == 0
        assert report.detected is False

    def test_check_abuse_malformed_entries_skipped(self, tmp_path):
        detector = RollbackAbuseDetector(project_root=tmp_path)
        audit_dir = tmp_path / ".zephyr" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_path = audit_dir / "rollback_operations_audit.jsonl"
        audit_path.write_text("not json\n\nalso not json\n", encoding="utf-8")
        report = detector.check_abuse()
        assert report.detected is False
        assert report.rollback_count_1h == 0

    def test_constants(self):
        assert RollbackAbuseDetector.EXIT_CODE_ABUSE == 44
        assert RollbackAbuseDetector.MAX_ROLLBACKS_PER_HOUR == 5
        assert RollbackAbuseDetector.MAX_ROLLBACKS_PER_DAY == 20
        assert RollbackAbuseDetector.MAX_SAME_FILE_CONSECUTIVE == 3
