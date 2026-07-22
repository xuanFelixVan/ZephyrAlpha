# [A_test] module_id: MOD-GOV_rollback_verifier_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §7
# [MODULE] tests.test_rollback_verifier
# [INVARIANTS] g0_verify returns G0Report; heal_db_consistency returns DBHealReport; differential_check returns DifferentialReport
# [MODIFY-GUARD] Do not change test data without updating source module
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] All public methods return dataclass results even on error
# [TESTS] pytest tests/test_rollback_verifier.py -q
# [TTL] task_bound

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from zephyr.infrastructure.rollback.rollback_verifier import (
    G0Report,
    RollbackVerifier,
)


@pytest.fixture
def tmp_project(tmp_path):
    src = tmp_path / "src" / "zephyr"
    src.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def verifier(tmp_project):
    return RollbackVerifier(project_root=tmp_project)


class TestInstantiation:
    def test_custom_root(self, tmp_project):
        v = RollbackVerifier(project_root=tmp_project)
        assert v._project_root == tmp_project

    def test_none_root_defaults_to_cwd(self):
        v = RollbackVerifier(project_root=None)
        assert v._project_root == Path.cwd()


class TestG0Verify:
    def test_empty_files_list_scans_project(self, verifier, tmp_project):
        py_file = tmp_project / "src" / "zephyr" / "hello.py"
        py_file.write_text('"""Module."""\nx = 1\n', encoding="utf-8")
        report = verifier.g0_verify(files=[])
        assert isinstance(report, G0Report)
        assert report.passed is True
        assert report.missing_files == []
        assert report.syntax_errors == []

    def test_missing_file_reported(self, verifier):
        report = verifier.g0_verify(files=["nonexistent.py"])
        assert report.passed is False
        assert "nonexistent.py" in report.missing_files

    def test_python_syntax_error_detected(self, verifier, tmp_project):
        bad_py = tmp_project / "bad.py"
        bad_py.write_text("def broken(\n", encoding="utf-8")
        report = verifier.g0_verify(files=["bad.py"])
        assert report.passed is False
        assert len(report.syntax_errors) == 1
        assert "bad.py" in report.syntax_errors[0]

    def test_valid_python_passes(self, verifier, tmp_project):
        good_py = tmp_project / "good.py"
        good_py.write_text('"""Doc."""\nx = 1\n', encoding="utf-8")
        report = verifier.g0_verify(files=["good.py"])
        assert report.passed is True

    def test_yaml_syntax_error_detected(self, verifier, tmp_project):
        bad_yaml = tmp_project / "bad.yaml"
        bad_yaml.write_text("key: [unclosed\n", encoding="utf-8")
        report = verifier.g0_verify(files=["bad.yaml"])
        assert report.passed is False
        assert len(report.syntax_errors) == 1

    def test_json_syntax_error_detected(self, verifier, tmp_project):
        bad_json = tmp_project / "bad.json"
        bad_json.write_text("{invalid json}", encoding="utf-8")
        report = verifier.g0_verify(files=["bad.json"])
        assert report.passed is False
        assert len(report.syntax_errors) == 1

    def test_none_files_treated_as_empty(self, verifier, tmp_project):
        py_file = tmp_project / "src" / "zephyr" / "mod.py"
        py_file.write_text('"""M."""\ny = 2\n', encoding="utf-8")
        report = verifier.g0_verify(files=None)
        assert isinstance(report, G0Report)


class TestCleanPycache:
    def test_removes_pycache_dirs(self, verifier, tmp_project):
        cache = tmp_project / "src" / "__pycache__"
        cache.mkdir(parents=True)
        (cache / "mod.cpython-311.pyc").write_bytes(b"\x00")
        removed = verifier.clean_pycache()
        assert removed == 1
        assert not cache.exists()

    def test_no_pycache_returns_zero(self, verifier):
        removed = verifier.clean_pycache()
        assert removed == 0


class TestHealDbConsistency:
    def test_db_not_found(self, verifier, tmp_project):
        report = verifier.heal_db_consistency()
        assert report.healed is False
        assert "DB not found" in report.details

    def test_db_with_invalid_task_status(self, verifier, tmp_project):
        db_path = tmp_project / "data" / "databases" / "governance.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE tasks (task_id TEXT PRIMARY KEY, status TEXT)")
        conn.execute("CREATE TABLE gates (gate_id TEXT PRIMARY KEY, result TEXT)")
        conn.execute("INSERT INTO tasks VALUES ('t1', 'INVALID_STATUS')")
        conn.execute("INSERT INTO gates VALUES ('g1', 'PASS')")
        conn.commit()
        conn.close()

        report = verifier.heal_db_consistency(db_path=db_path)
        assert report.healed is True
        assert report.tasks_fixed == 1
        assert report.gates_fixed == 0

    def test_db_with_invalid_gate_result(self, verifier, tmp_project):
        db_path = tmp_project / "data" / "databases" / "governance.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE tasks (task_id TEXT PRIMARY KEY, status TEXT)")
        conn.execute("CREATE TABLE gates (gate_id TEXT PRIMARY KEY, result TEXT)")
        conn.execute("INSERT INTO tasks VALUES ('t1', 'PENDING')")
        conn.execute("INSERT INTO gates VALUES ('g1', 'BROKEN')")
        conn.commit()
        conn.close()

        report = verifier.heal_db_consistency(db_path=db_path)
        assert report.healed is True
        assert report.gates_fixed == 1

    def test_db_all_valid(self, verifier, tmp_project):
        db_path = tmp_project / "data" / "databases" / "governance.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE tasks (task_id TEXT PRIMARY KEY, status TEXT)")
        conn.execute("CREATE TABLE gates (gate_id TEXT PRIMARY KEY, result TEXT)")
        conn.execute("INSERT INTO tasks VALUES ('t1', 'PENDING')")
        conn.execute("INSERT INTO gates VALUES ('g1', 'PASS')")
        conn.commit()
        conn.close()

        report = verifier.heal_db_consistency(db_path=db_path)
        assert report.healed is False
        assert report.tasks_fixed == 0
        assert report.gates_fixed == 0


class TestDifferentialCheck:
    def test_identical_dbs(self, tmp_project):
        db_before = tmp_project / "before.db"
        db_after = tmp_project / "after.db"
        for db_path in (db_before, db_after):
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE tasks (id INTEGER, name TEXT)")
            conn.execute("INSERT INTO tasks VALUES (1, 'a')")
            conn.execute("CREATE TABLE gates (id INTEGER, name TEXT)")
            conn.execute("INSERT INTO gates VALUES (1, 'g')")
            conn.execute("CREATE TABLE events (id INTEGER, name TEXT)")
            conn.execute("INSERT INTO events VALUES (1, 'e')")
            conn.commit()
            conn.close()

        v = RollbackVerifier(project_root=tmp_project)
        report = v.differential_check(db_before, db_after)
        assert report.passed is True
        assert report.rows_mismatched == 0

    def test_different_row_counts(self, tmp_project):
        db_before = tmp_project / "before.db"
        db_after = tmp_project / "after.db"

        conn = sqlite3.connect(str(db_before))
        conn.execute("CREATE TABLE tasks (id INTEGER)")
        conn.execute("INSERT INTO tasks VALUES (1)")
        conn.execute("INSERT INTO tasks VALUES (2)")
        conn.execute("CREATE TABLE gates (id INTEGER)")
        conn.execute("CREATE TABLE events (id INTEGER)")
        conn.commit()
        conn.close()

        conn = sqlite3.connect(str(db_after))
        conn.execute("CREATE TABLE tasks (id INTEGER)")
        conn.execute("INSERT INTO tasks VALUES (1)")
        conn.execute("CREATE TABLE gates (id INTEGER)")
        conn.execute("CREATE TABLE events (id INTEGER)")
        conn.commit()
        conn.close()

        v = RollbackVerifier(project_root=tmp_project)
        report = v.differential_check(db_before, db_after)
        assert report.passed is False
        assert report.rows_mismatched == 1
        assert "tasks" in report.table_changes

    def test_nonexistent_db_returns_error(self, tmp_project):
        v = RollbackVerifier(project_root=tmp_project)
        report = v.differential_check(tmp_project / "no_before.db", tmp_project / "no_after.db")
        assert report.passed is False
        assert "error" in report.table_changes
