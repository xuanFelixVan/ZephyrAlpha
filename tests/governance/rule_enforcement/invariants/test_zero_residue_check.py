# [A_test] module_id: SRC-TST-1811 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_zero_residue_check
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit code reflects pass/fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.gov_enforcement.rule_enforcement.invariants.zero_residue_check import (
    ResidueFinding,
    ResidueReport,
    ZeroResidueScanner,
)


class TestResidueFinding:
    def test_creation(self):
        rf = ResidueFinding(
            rule_id="ZR-001",
            message="temp file found",
            severity="error",
            file_rel="src/_temp_thing.py",
        )
        assert rf.rule_id == "ZR-001"
        assert rf.message == "temp file found"
        assert rf.severity == "error"
        assert rf.file_rel == "src/_temp_thing.py"

    def test_equality(self):
        rf1 = ResidueFinding(rule_id="ZR-001", message="x", severity="error", file_rel="a.py")
        rf2 = ResidueFinding(rule_id="ZR-001", message="x", severity="error", file_rel="a.py")
        assert rf1 == rf2

    def test_inequality(self):
        rf1 = ResidueFinding(rule_id="ZR-001", message="x", severity="error", file_rel="a.py")
        rf2 = ResidueFinding(rule_id="ZR-002", message="x", severity="error", file_rel="a.py")
        assert rf1 != rf2

    def test_empty_file_rel(self):
        rf = ResidueFinding(rule_id="ZR-001", message="x", severity="warning", file_rel="")
        assert rf.file_rel == ""


class TestResidueReport:
    def test_default_clean(self):
        report = ResidueReport()
        assert report.is_clean is True
        assert report.findings == []

    def test_add_changes_is_clean(self):
        report = ResidueReport()
        report.add("ZR-001", "found temp file", "error", "src/_temp.py")
        assert report.is_clean is False
        assert len(report.findings) == 1

    def test_add_multiple_findings(self):
        report = ResidueReport()
        report.add("ZR-001", "temp file", "error", "a.py")
        report.add("ZR-003", "orphan py", "warning", "b.py")
        assert report.is_clean is False
        assert len(report.findings) == 2

    def test_add_finding_fields(self):
        report = ResidueReport()
        report.add("ZR-005", "ruins ref", "error", "c.py")
        f = report.findings[0]
        assert isinstance(f, ResidueFinding)
        assert f.rule_id == "ZR-005"
        assert f.message == "ruins ref"
        assert f.severity == "error"
        assert f.file_rel == "c.py"

    def test_add_without_file_rel(self):
        report = ResidueReport()
        report.add("ZR-006", "residual", "warning")
        assert report.findings[0].file_rel == ""

    def test_stays_dirty_after_multiple_adds(self):
        report = ResidueReport()
        report.add("ZR-001", "x", "error")
        report.add("ZR-002", "y", "warning")
        report.add("ZR-003", "z", "error")
        assert report.is_clean is False
        assert len(report.findings) == 3


class TestZeroResidueScanner:
    def test_init_default_root(self):
        scanner = ZeroResidueScanner()
        assert scanner._root.exists()

    def test_init_custom_root(self, tmp_path):
        scanner = ZeroResidueScanner(project_root=tmp_path)
        assert scanner._root == tmp_path

    def test_scripts_dir_set(self, tmp_path):
        scanner = ZeroResidueScanner(project_root=tmp_path)
        assert scanner._scripts_dir == tmp_path / "scripts" / "governance"

    @patch.object(ZeroResidueScanner, "_scan_temp_files")
    @patch.object(ZeroResidueScanner, "_scan_residual_files")
    @patch.object(ZeroResidueScanner, "_scan_ruins_references")
    @patch.object(ZeroResidueScanner, "_scan_orphan_py")
    @patch.object(ZeroResidueScanner, "_scan_orphan_docs")
    def test_scan_returns_report(self, mock_docs, mock_py, mock_ruins, mock_residual, mock_temp):
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = scanner.scan()
        assert isinstance(report, ResidueReport)

    @patch.object(ZeroResidueScanner, "_scan_temp_files")
    @patch.object(ZeroResidueScanner, "_scan_residual_files")
    @patch.object(ZeroResidueScanner, "_scan_ruins_references")
    @patch.object(ZeroResidueScanner, "_scan_orphan_py")
    @patch.object(ZeroResidueScanner, "_scan_orphan_docs")
    def test_scan_calls_all_subscanners(self, mock_docs, mock_py, mock_ruins, mock_residual, mock_temp):
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        scanner.scan()
        mock_temp.assert_called_once()
        mock_residual.assert_called_once()
        mock_ruins.assert_called_once()
        mock_py.assert_called_once()
        mock_docs.assert_called_once()


class TestRunScript:
    def test_script_not_found(self, tmp_path):
        scanner = ZeroResidueScanner(project_root=tmp_path)
        code, out, err = scanner._run_script("nonexistent/script.py")
        assert code == 1
        assert "Script not found" in err

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.zero_residue_check.subprocess.run")
    def test_script_success(self, mock_run, tmp_path):
        scripts_dir = tmp_path / "scripts" / "governance" / "d1_structure"
        scripts_dir.mkdir(parents=True)
        script = scripts_dir / "detect_temp_files.py"
        script.write_text("print('ok')", encoding="utf-8")

        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")

        scanner = ZeroResidueScanner(project_root=tmp_path)
        code, out, err = scanner._run_script("d1_structure/detect_temp_files.py")
        assert code == 0

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.zero_residue_check.subprocess.run")
    def test_script_timeout(self, mock_run, tmp_path):
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="script", timeout=120)

        scripts_dir = tmp_path / "scripts" / "governance" / "d1_structure"
        scripts_dir.mkdir(parents=True)
        script = scripts_dir / "detect_temp_files.py"
        script.write_text("import time; time.sleep(999)", encoding="utf-8")

        scanner = ZeroResidueScanner(project_root=tmp_path)
        code, out, err = scanner._run_script("d1_structure/detect_temp_files.py")
        assert code == 1
        assert "timed out" in err.lower()

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.zero_residue_check.subprocess.run")
    def test_script_exception(self, mock_run, tmp_path):
        mock_run.side_effect = OSError("permission denied")

        scripts_dir = tmp_path / "scripts" / "governance" / "d1_structure"
        scripts_dir.mkdir(parents=True)
        script = scripts_dir / "detect_temp_files.py"
        script.write_text("pass", encoding="utf-8")

        scanner = ZeroResidueScanner(project_root=tmp_path)
        code, out, err = scanner._run_script("d1_structure/detect_temp_files.py")
        assert code == 1
        assert "permission denied" in err.lower()


class TestParseFindings:
    def test_exit_code_zero_no_findings(self):
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        result = scanner._parse_findings(0, "")
        assert result == []

    def test_parses_issue_lines(self):
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        stderr = "[ZR-001] Found _temp file: _temp_thing.py\n=== Section ===\n--- Divider ---\n"
        result = scanner._parse_findings(1, stderr)
        assert any("_temp" in r for r in result)

    def test_skips_separator_lines(self):
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        stderr = "=== Section ===\n--- Divider ---\n[ZR-001] Issue\n"
        result = scanner._parse_findings(1, stderr)
        assert not any(r.startswith("===") or r.startswith("---") for r in result)

    def test_skips_banner_lines(self):
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        stderr = "[TEMP-FILES] Scanning...\n[RESIDUAL] Done\n[RUINS-SCAN] OK\n[ORPHAN-PY] Check\n[ORPHAN-DOC] Check\n"
        result = scanner._parse_findings(1, stderr)
        assert result == []

    def test_skips_scanned_count(self):
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        stderr = "Scanned 42 files\n[ZR-001] Real issue\n"
        result = scanner._parse_findings(1, stderr)
        assert len(result) == 1
        assert "Real issue" in result[0]

    def test_empty_stderr(self):
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        result = scanner._parse_findings(1, "")
        assert result == []

    def test_short_lines_skipped(self):
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        stderr = "ab\n[ZR-001] This is a real issue that is long enough\n"
        result = scanner._parse_findings(1, stderr)
        assert any("real issue" in r for r in result)


class TestScanTempFiles:
    @patch.object(ZeroResidueScanner, "_run_script")
    def test_no_issues(self, mock_run):
        mock_run.return_value = (0, "", "")
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = ResidueReport()
        for rule_id, message, severity, file_rel in scanner._scan_temp_files():
            report.add(rule_id, message, severity, file_rel)
        assert report.is_clean is True

    @patch.object(ZeroResidueScanner, "_run_script")
    def test_with_issues(self, mock_run):
        mock_run.return_value = (1, "", "[ZR-001] _temp_file.py found\n")
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = ResidueReport()
        for rule_id, message, severity, file_rel in scanner._scan_temp_files():
            report.add(rule_id, message, severity, file_rel)
        assert report.is_clean is False
        assert any(f.rule_id == "ZR-001" for f in report.findings)


class TestScanResidualFiles:
    @patch.object(ZeroResidueScanner, "_run_script")
    def test_no_issues(self, mock_run):
        mock_run.return_value = (0, "", "")
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = ResidueReport()
        for rule_id, message, severity, file_rel in scanner._scan_residual_files():
            report.add(rule_id, message, severity, file_rel)
        assert report.is_clean is True

    @patch.object(ZeroResidueScanner, "_run_script")
    def test_with_issues(self, mock_run):
        mock_run.return_value = (1, "", "leftover.yaml found in project root\n")
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = ResidueReport()
        for rule_id, message, severity, file_rel in scanner._scan_residual_files():
            report.add(rule_id, message, severity, file_rel)
        assert report.is_clean is False
        assert any(f.rule_id == "ZR-006" for f in report.findings)


class TestScanRuinsReferences:
    @patch.object(ZeroResidueScanner, "_run_script")
    def test_no_issues(self, mock_run):
        mock_run.return_value = (0, "", "")
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = ResidueReport()
        for rule_id, message, severity, file_rel in scanner._scan_ruins_references():
            report.add(rule_id, message, severity, file_rel)
        assert report.is_clean is True

    @patch.object(ZeroResidueScanner, "_run_script")
    def test_with_issues(self, mock_run):
        mock_run.return_value = (1, "", "dead reference to deleted.py in imports\n")
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = ResidueReport()
        for rule_id, message, severity, file_rel in scanner._scan_ruins_references():
            report.add(rule_id, message, severity, file_rel)
        assert report.is_clean is False
        assert any(f.rule_id == "ZR-005" for f in report.findings)


class TestScanOrphanPy:
    @patch.object(ZeroResidueScanner, "_run_script")
    def test_no_issues(self, mock_run):
        mock_run.return_value = (0, "", "")
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = ResidueReport()
        for rule_id, message, severity, file_rel in scanner._scan_orphan_py():
            report.add(rule_id, message, severity, file_rel)
        assert report.is_clean is True

    @patch.object(ZeroResidueScanner, "_run_script")
    def test_with_issues(self, mock_run):
        mock_run.return_value = (1, "", "unregistered.py not in __init__.py\n")
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = ResidueReport()
        for rule_id, message, severity, file_rel in scanner._scan_orphan_py():
            report.add(rule_id, message, severity, file_rel)
        assert report.is_clean is False
        assert any(f.rule_id == "ZR-003" for f in report.findings)


class TestScanOrphanDocs:
    @patch.object(ZeroResidueScanner, "_run_script")
    def test_no_issues(self, mock_run):
        mock_run.return_value = (0, "", "")
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = ResidueReport()
        for rule_id, message, severity, file_rel in scanner._scan_orphan_docs():
            report.add(rule_id, message, severity, file_rel)
        assert report.is_clean is True

    @patch.object(ZeroResidueScanner, "_run_script")
    def test_with_issues(self, mock_run):
        mock_run.return_value = (1, "", "stray.md not referenced anywhere\n")
        scanner = ZeroResidueScanner(project_root=Path("/tmp"))
        report = ResidueReport()
        for rule_id, message, severity, file_rel in scanner._scan_orphan_docs():
            report.add(rule_id, message, severity, file_rel)
        # ZR-004 保持 warning：孤儿文档可能是新文件尚未提交，不阻断 is_clean
        assert report.is_clean is True
        assert any(f.rule_id == "ZR-004" for f in report.findings)
