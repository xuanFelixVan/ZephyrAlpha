# [A_test] module_id: SRC-TST-2075 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-692 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_task_completion_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for task_completion_gate.py (T-2-25, C52)
=====================================================
Minimum: 5 tests
"""


from pathlib import Path

from zephyr.gov_enforcement.rule_enforcement.task_completion_gate import (
    Disposition,
    GateReport,
    ResidualFile,
    ResidualType,
    TaskCompletionGate,
)


def _create_file(base: Path, rel: str, content: str = "") -> Path:
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


class TestTaskCompletionGate:
    def test_detect_temp_files(self, tmp_path: Path) -> None:
        _create_file(tmp_path, "temp_output.txt")
        _create_file(tmp_path, "normal.txt")
        gate = TaskCompletionGate(tmp_path)
        report = gate.scan()
        assert report.residual_count == 1
        assert report.residuals[0].residual_type == ResidualType.TEMP

    def test_detect_backup_files(self, tmp_path: Path) -> None:
        _create_file(tmp_path, "data.backup")
        _create_file(tmp_path, "data.csv")
        gate = TaskCompletionGate(tmp_path)
        report = gate.scan()
        assert report.residual_count == 1
        assert report.residuals[0].residual_type == ResidualType.BACKUP

    def test_detect_versioned_files(self, tmp_path: Path) -> None:
        _create_file(tmp_path, "module-v2.py")
        _create_file(tmp_path, "module.py")
        gate = TaskCompletionGate(tmp_path)
        report = gate.scan()
        assert report.residual_count == 1
        assert report.residuals[0].residual_type == ResidualType.VERSIONED

    def test_detect_pycache_and_pyc(self, tmp_path: Path) -> None:
        _create_file(tmp_path, "__pycache__/module.cpython-312.pyc")
        gate = TaskCompletionGate(tmp_path)
        report = gate.scan()
        types = {r.residual_type for r in report.residuals}
        assert ResidualType.PYCACHE in types or ResidualType.PYC in types

    def test_passed_when_no_residuals(self, tmp_path: Path) -> None:
        _create_file(tmp_path, "clean_file.py")
        gate = TaskCompletionGate(tmp_path)
        report = gate.scan()
        assert report.passed is True

    def test_files_in_scope_detection(self, tmp_path: Path) -> None:
        _create_file(tmp_path, "expected.py")
        _create_file(tmp_path, "unexpected.py")
        scope = {"expected.py"}
        gate = TaskCompletionGate(tmp_path, files_in_scope=scope)
        report = gate.scan()
        unexpected = [r for r in report.residuals if "unexpected" in r.rel_path]
        assert len(unexpected) >= 1

    def test_format_report(self, tmp_path: Path) -> None:
        _create_file(tmp_path, "temp_test.txt")
        gate = TaskCompletionGate(tmp_path)
        report = gate.scan()
        text = gate.format_report(report)
        assert "Residual files" in text

    def test_empty_directory(self, tmp_path: Path) -> None:
        gate = TaskCompletionGate(tmp_path)
        report = gate.scan()
        assert report.passed is True
        assert report.residual_count == 0

    def test_nonexistent_directory(self, tmp_path: Path) -> None:
        gate = TaskCompletionGate(tmp_path / "nonexistent")
        report = gate.scan()
        assert report.total_scanned == 0


class TestGateReport:
    def test_by_type(self) -> None:
        report = GateReport()
        report.residuals = [
            ResidualFile(Path("a"), "a", ResidualType.TEMP, Disposition.DELETE, "r"),
            ResidualFile(Path("b"), "b", ResidualType.TEMP, Disposition.DELETE, "r"),
            ResidualFile(Path("c"), "c", ResidualType.BACKUP, Disposition.DELETE, "r"),
        ]
        report.residual_count = 3
        assert report.by_type["temp_file"] == 2
        assert report.by_type["backup_file"] == 1

    def test_by_disposition(self) -> None:
        report = GateReport()
        report.residuals = [
            ResidualFile(Path("a"), "a", ResidualType.TEMP, Disposition.DELETE, "r"),
            ResidualFile(Path("b"), "b", ResidualType.TEMP, Disposition.MOVE, "r"),
        ]
        report.residual_count = 2
        assert report.by_disposition["delete"] == 1
        assert report.by_disposition["move"] == 1
