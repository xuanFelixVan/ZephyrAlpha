# [A_test] module_id: SRC-TST-1175 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_self_test
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] test_kb_self_test.py
# [TTL] task_bound

from __future__ import annotations

import json
import sqlite3
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from zephyr.gov_kb.self_test import (
    CheckResult,
    CheckStatus,
    SelfTest,
    SelfTestReport,
    _check_category_coverage,
    _check_filesystem_permissions,
    _check_freeze_state,
    _check_ke_count,
    _check_silent_period,
    _check_sqlite_integrity,
    _check_tombstone_integrity,
    _check_wal_health,
)


def _mock_check_pass(root):
    return CheckResult(99, "Mock", CheckStatus.PASS, "ok")


class TestSelfTest:
    def _make_self_test(self, tmp_path: Path) -> SelfTest:
        st = SelfTest(project_root=tmp_path)
        st.CHECK_FUNCTIONS = [_mock_check_pass]
        return st

    def test_run_returns_report(self, tmp_path: Path):
        st = self._make_self_test(tmp_path)
        report = st.run()
        assert isinstance(report, SelfTestReport)
        assert report.timestamp
        assert isinstance(report.checks, list)
        assert len(report.checks) > 0

    def test_run_counts(self, tmp_path: Path):
        st = self._make_self_test(tmp_path)
        report = st.run()
        total = report.passed + report.warned + report.failed + report.skipped
        assert total == len(report.checks)

    def test_run_overall_status(self, tmp_path: Path):
        st = self._make_self_test(tmp_path)
        report = st.run()
        if report.failed > 0:
            assert report.overall == CheckStatus.FAIL
        elif report.warned > 0:
            assert report.overall == CheckStatus.WARN
        else:
            assert report.overall == CheckStatus.PASS

    def test_print_report_text(self, tmp_path: Path):
        st = self._make_self_test(tmp_path)
        report = st.run()
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            st.print_report(report, json_output=False)
            output = mock_out.getvalue()
            assert "KB System Self-Test Report" in output

    def test_print_report_json(self, tmp_path: Path):
        st = self._make_self_test(tmp_path)
        report = st.run()
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            st.print_report(report, json_output=True)
            output = mock_out.getvalue()
            data = json.loads(output)
            assert "overall" in data
            assert "checks" in data

    def test_summary_string(self, tmp_path: Path):
        st = self._make_self_test(tmp_path)
        report = st.run()
        assert "PASS" in report.summary

    def test_run_with_fail_check(self, tmp_path: Path):
        def _fail_check(root):
            return CheckResult(1, "FailTest", CheckStatus.FAIL, "broken")

        st = SelfTest(project_root=tmp_path)
        st.CHECK_FUNCTIONS = [_fail_check]
        report = st.run()
        assert report.overall == CheckStatus.FAIL
        assert report.failed == 1

    def test_run_with_warn_check(self, tmp_path: Path):
        def _warn_check(root):
            return CheckResult(1, "WarnTest", CheckStatus.WARN, "meh")

        st = SelfTest(project_root=tmp_path)
        st.CHECK_FUNCTIONS = [_warn_check]
        report = st.run()
        assert report.overall == CheckStatus.WARN
        assert report.warned == 1

    def test_run_exception_in_check(self, tmp_path: Path):
        def _boom(root):
            raise RuntimeError("boom")

        st = SelfTest(project_root=tmp_path)
        st.CHECK_FUNCTIONS = [_boom]
        report = st.run()
        assert report.failed == 1


class TestCheckSqliteIntegrity:
    def test_no_db(self, tmp_path: Path):
        result = _check_sqlite_integrity(tmp_path)
        assert result.status == CheckStatus.WARN

    def test_valid_db(self, tmp_path: Path):
        db_path = tmp_path / "data" / "databases" / "governance.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.commit()
        conn.close()
        result = _check_sqlite_integrity(tmp_path)
        assert result.status == CheckStatus.PASS


class TestCheckKeCount:
    def test_no_dir(self, tmp_path: Path):
        result = _check_ke_count(tmp_path)
        assert result.status == CheckStatus.WARN

    def test_few_kes(self, tmp_path: Path):
        ke_dir = tmp_path / "docs" / "08_knowledge" / "01_raw_intake"
        ke_dir.mkdir(parents=True, exist_ok=True)
        for i in range(3):
            (ke_dir / f"KE-{i:03d}.md").write_text("x", encoding="utf-8")
        result = _check_ke_count(tmp_path)
        assert result.status == CheckStatus.WARN

    def test_enough_kes(self, tmp_path: Path):
        ke_dir = tmp_path / "docs" / "08_knowledge" / "01_raw_intake"
        ke_dir.mkdir(parents=True, exist_ok=True)
        for i in range(12):
            (ke_dir / f"KE-{i:03d}.md").write_text("x", encoding="utf-8")
        result = _check_ke_count(tmp_path)
        assert result.status == CheckStatus.PASS


class TestCheckCategoryCoverage:
    def test_no_dir(self, tmp_path: Path):
        result = _check_category_coverage(tmp_path)
        assert result.status == CheckStatus.SKIP

    def test_few_categories(self, tmp_path: Path):
        ke_dir = tmp_path / "docs" / "08_knowledge" / "01_raw_intake"
        ke_dir.mkdir(parents=True, exist_ok=True)
        (ke_dir / "KE-001.md").write_text("---\ncategory: a\n---\nbody", encoding="utf-8")
        result = _check_category_coverage(tmp_path)
        assert result.status == CheckStatus.WARN


class TestCheckWalHealth:
    def test_no_wal_files(self, tmp_path: Path):
        (tmp_path / "data").mkdir(parents=True, exist_ok=True)
        result = _check_wal_health(tmp_path)
        assert result.status == CheckStatus.PASS


class TestCheckFreezeState:
    def test_not_frozen(self, tmp_path: Path):
        result = _check_freeze_state(tmp_path)
        assert result.status == CheckStatus.PASS

    def test_frozen(self, tmp_path: Path):
        snap_dir = tmp_path / "data" / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        (snap_dir / "kb_lock.json").write_text(
            json.dumps({"mode": "safe_mode", "since": "2025-01-01", "reason": "test"}),
            encoding="utf-8",
        )
        result = _check_freeze_state(tmp_path)
        assert result.status == CheckStatus.WARN


class TestCheckTombstoneIntegrity:
    def test_no_db(self, tmp_path: Path):
        result = _check_tombstone_integrity(tmp_path)
        assert result.status == CheckStatus.SKIP

    def test_db_no_table(self, tmp_path: Path):
        db_path = tmp_path / "data" / "databases" / "governance.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE other (id INTEGER)")
        conn.commit()
        conn.close()
        result = _check_tombstone_integrity(tmp_path)
        assert result.status == CheckStatus.WARN

    def test_db_with_table(self, tmp_path: Path):
        db_path = tmp_path / "data" / "databases" / "governance.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute(
            "CREATE TABLE ke_tombstones (tombstone_id TEXT PRIMARY KEY, ke_id TEXT, "
            "deletion_time TEXT, deletion_reason TEXT, source_hash TEXT, chroma_id TEXT, "
            "vector_hash TEXT, purged INTEGER DEFAULT 0, purged_at TEXT)"
        )
        conn.commit()
        conn.close()
        result = _check_tombstone_integrity(tmp_path)
        assert result.status == CheckStatus.PASS


class TestCheckSilentPeriod:
    def test_no_dir(self, tmp_path: Path):
        result = _check_silent_period(tmp_path)
        assert result.status == CheckStatus.SKIP

    def test_recent_ke(self, tmp_path: Path):
        ke_dir = tmp_path / "docs" / "08_knowledge" / "01_raw_intake"
        ke_dir.mkdir(parents=True, exist_ok=True)
        (ke_dir / "KE-001.md").write_text("recent", encoding="utf-8")
        result = _check_silent_period(tmp_path)
        assert result.status == CheckStatus.PASS


class TestCheckFilesystemPermissions:
    def test_writable(self, tmp_path: Path):
        result = _check_filesystem_permissions(tmp_path)
        assert result.status == CheckStatus.PASS


class TestCheckResult:
    def test_creation(self):
        cr = CheckResult(1, "Test", CheckStatus.PASS, "ok")
        assert cr.index == 1
        assert cr.name == "Test"
        assert cr.status == CheckStatus.PASS


class TestCheckStatus:
    def test_values(self):
        assert CheckStatus.PASS.value == "PASS"
        assert CheckStatus.WARN.value == "WARN"
        assert CheckStatus.FAIL.value == "FAIL"
        assert CheckStatus.SKIP.value == "SKIP"
