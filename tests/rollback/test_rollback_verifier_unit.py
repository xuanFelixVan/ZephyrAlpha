# [A_test] module_id: MOD-GOV_rollback_verifier_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-678 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_rollback_verifier
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for RollbackVerifier — 回滚后验证器 (MOD-INF-021 §7 Phase 1.4).

Tests: g0_verify, clean_pycache, heal_db_consistency, differential_check.
"""


import sqlite3
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

from zephyr.infrastructure.rollback.rollback_verifier import RollbackVerifier


@contextmanager
def _temp_dir():
    tmp = tempfile.mkdtemp()
    root = Path(tmp)
    try:
        yield root
    finally:
        import gc

        gc.collect()
        for _ in range(100):
            try:
                for f in root.rglob("*"):
                    if f.is_file():
                        f.unlink(missing_ok=True)
                for d in sorted(root.rglob("*"), reverse=True):
                    if d.is_dir():
                        d.rmdir()
                root.rmdir()
                break
            except (PermissionError, OSError):
                time.sleep(0.01)


def _create_test_db(db_path: Path, *, tasks: bool = True, gates: bool = True, events: bool = True):
    conn = sqlite3.connect(str(db_path))
    if tasks:
        conn.execute("CREATE TABLE tasks (task_id TEXT PRIMARY KEY, title TEXT, status TEXT)")
    if gates:
        conn.execute("CREATE TABLE gates (gate_id TEXT PRIMARY KEY, result TEXT)")
    if events:
        conn.execute("CREATE TABLE events (event_id TEXT PRIMARY KEY, type TEXT, data TEXT)")
    conn.commit()
    conn.close()


class TestG0Verify:
    """g0_verify() — G0 门禁：文件存在性 + 语法 + Lint"""

    def test_all_files_clean(self):
        with _temp_dir() as root:
            src_dir = root / "src"
            src_dir.mkdir()
            py_file = src_dir / "clean.py"
            py_file.write_text('"""Module docstring."""\ndef foo():\n    return 42\n', encoding="utf-8")
            verifier = RollbackVerifier(project_root=root)
            report = verifier.g0_verify(files=[str(py_file.relative_to(root))])
            assert report.passed
            assert len(report.missing_files) == 0
            assert len(report.syntax_errors) == 0

    def test_missing_file(self):
        verifier = RollbackVerifier()
        report = verifier.g0_verify(files=["nonexistent.py"])
        assert not report.passed
        assert "nonexistent.py" in report.missing_files

    def test_python_syntax_error(self):
        with _temp_dir() as root:
            py_file = root / "broken.py"
            py_file.write_text("def foo(\n", encoding="utf-8")
            verifier = RollbackVerifier(project_root=root)
            report = verifier.g0_verify(files=[str(py_file.relative_to(root))])
            assert not report.passed
            assert len(report.syntax_errors) > 0
            assert "broken.py" in report.syntax_errors[0]

    def test_yaml_parse_error(self):
        with _temp_dir() as root:
            yaml_file = root / "bad.yaml"
            yaml_file.write_text("key: [unclosed\n", encoding="utf-8")
            verifier = RollbackVerifier(project_root=root)
            report = verifier.g0_verify(files=[str(yaml_file.relative_to(root))])
            assert not report.passed
            assert len(report.syntax_errors) > 0

    def test_json_parse_error(self):
        with _temp_dir() as root:
            json_file = root / "bad.json"
            json_file.write_text("{invalid json", encoding="utf-8")
            verifier = RollbackVerifier(project_root=root)
            report = verifier.g0_verify(files=[str(json_file.relative_to(root))])
            assert not report.passed
            assert len(report.syntax_errors) > 0

    def test_missing_module_docstring(self):
        with _temp_dir() as root:
            py_file = root / "no_docstring.py"
            py_file.write_text("def foo():\n    return 1\n", encoding="utf-8")
            verifier = RollbackVerifier(project_root=root)
            report = verifier.g0_verify(files=[str(py_file.relative_to(root))])
            assert not report.passed
            assert any("docstring" in issue for issue in report.lint_issues)

    def test_init_py_missing_docstring_allowed(self):
        with _temp_dir() as root:
            init_file = root / "__init__.py"
            init_file.write_text("", encoding="utf-8")
            verifier = RollbackVerifier(project_root=root)
            report = verifier.g0_verify(files=[str(init_file.relative_to(root))])
            assert report.passed


class TestCleanPycache:
    """clean_pycache() — 删除所有 __pycache__ bytecode 缓存"""

    def test_clean_pycache_removes_dirs(self):
        with _temp_dir() as root:
            pycache = root / "__pycache__"
            pycache.mkdir()
            (pycache / "test.cpython-311.pyc").write_text("", encoding="utf-8")
            verifier = RollbackVerifier(project_root=root)
            removed = verifier.clean_pycache()
            assert removed >= 1


class TestHealDBConsistency:
    """heal_db_consistency() — DB 一致性自愈"""

    def test_db_not_found(self):
        verifier = RollbackVerifier(project_root=Path(tempfile.mkdtemp()))
        report = verifier.heal_db_consistency()
        assert not report.healed
        assert "DB not found" in report.details

    def test_fixes_invalid_task_status(self):
        with _temp_dir() as root:
            db_path = root / "test_invalid_status.db"
            _create_test_db(db_path, tasks=True, gates=True, events=True)
            conn = sqlite3.connect(str(db_path))
            conn.execute("INSERT INTO tasks VALUES ('TASK-001', 'Test', 'INVALID_STATUS')")
            conn.commit()
            conn.close()

            verifier = RollbackVerifier(project_root=root)
            report = verifier.heal_db_consistency(db_path=db_path)
            assert report.healed
            assert report.tasks_fixed == 1

    def test_fixes_invalid_gate_result(self):
        with _temp_dir() as root:
            db_path = root / "test_invalid_gate.db"
            _create_test_db(db_path, tasks=True, gates=True, events=True)
            conn = sqlite3.connect(str(db_path))
            conn.execute("INSERT INTO gates VALUES ('GATE-001', 'MAYBE')")
            conn.commit()
            conn.close()

            verifier = RollbackVerifier(project_root=root)
            report = verifier.heal_db_consistency(db_path=db_path)
            assert report.healed
            assert report.gates_fixed == 1

    def test_valid_data_unchanged(self):
        with _temp_dir() as root:
            db_path = root / "test_valid.db"
            _create_test_db(db_path, tasks=True, gates=True, events=True)
            conn = sqlite3.connect(str(db_path))
            conn.execute("INSERT INTO tasks VALUES ('TASK-001', 'Test', 'COMPLETED')")
            conn.execute("INSERT INTO gates VALUES ('GATE-001', 'PASS')")
            conn.commit()
            conn.close()

            verifier = RollbackVerifier(project_root=root)
            report = verifier.heal_db_consistency(db_path=db_path)
            assert not report.healed


class TestDifferentialCheck:
    """differential_check() — 回滚前后逐行比较"""

    def test_identical_databases_pass(self):
        with _temp_dir() as root:
            db_before = root / "before.db"
            db_after = root / "after.db"

            for db_name in (db_before, db_after):
                _create_test_db(db_name, tasks=True, gates=True, events=True)
                conn = sqlite3.connect(str(db_name))
                conn.execute("INSERT INTO tasks VALUES ('T-1', 'T1', 'PENDING')")
                conn.execute("INSERT INTO tasks VALUES ('T-2', 'T2', 'COMPLETED')")
                conn.execute("INSERT INTO gates VALUES ('G-1', 'PASS')")
                conn.execute("INSERT INTO events VALUES ('E-1', 'drift', '{}')")
                conn.commit()
                conn.close()

            verifier = RollbackVerifier(project_root=root)
            report = verifier.differential_check(db_before, db_after)
            assert report.passed
            assert report.rows_mismatched == 0

    def test_divergent_row_counts_detected(self):
        with _temp_dir() as root:
            db_before = root / "before2.db"
            db_after = root / "after2.db"

            _create_test_db(db_before, tasks=True, gates=True, events=True)
            _create_test_db(db_after, tasks=True, gates=True, events=True)

            conn = sqlite3.connect(str(db_before))
            conn.execute("INSERT INTO tasks VALUES ('T-1', 'T1', 'PENDING')")
            conn.execute("INSERT INTO tasks VALUES ('T-2', 'T2', 'COMPLETED')")
            conn.commit()
            conn.close()

            conn = sqlite3.connect(str(db_after))
            conn.execute("INSERT INTO tasks VALUES ('T-1', 'T1', 'PENDING')")
            conn.commit()
            conn.close()

            verifier = RollbackVerifier(project_root=root)
            report = verifier.differential_check(db_before, db_after)
            assert not report.passed
            assert report.rows_mismatched > 0
