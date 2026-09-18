# [A_test] module_id: MOD-GOV_rollback_verifier_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §7
# [MODULE] tests.test_rollback_verifier
# [INVARIANTS] g0_verify returns G0Report; heal_db_consistency returns DBHealReport; differential_check returns DifferentialReport
# [MODIFY-GUARD] Do not change test data without updating source module
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] g0_verify/differential_check 返回 dataclass 结果；heal_db_consistency 在
#   表列集与活库不符 / 词表派生失败 / 真写未给 max_rows / 超行数上限时抛 HealRefusedError（WP1 改 1，fail-closed）
# [TESTS] pytest tests/test_rollback_verifier.py -q
# [TTL] task_bound

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from zephyr.infrastructure.rollback.rollback_verifier import (
    G0Report,
    HealRefusedError,
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
        assert v.project_root == tmp_project

    def test_none_root_defaults_to_cwd(self):
        v = RollbackVerifier(project_root=None)
        assert v.project_root == Path.cwd()


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


def _read_gate_row(db_path: Path, gate_run_id: str) -> tuple[int, str]:
    """进程外读回活库结构 gates 的行（证明 dry-run 真的没落库）。"""
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT passed, details FROM gates WHERE gate_run_id=?", (gate_run_id,)
        ).fetchone()
    finally:
        conn.close()
    assert row is not None, f"missing gate_run_id={gate_run_id}"
    return int(row[0]), row[1]


def _read_task_status(db_path: Path, task_id: str) -> str:
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute("SELECT status FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    finally:
        conn.close()
    assert row is not None, f"missing task_id={task_id}"
    return row[0]


class TestHealDbConsistency:
    """heal_db_consistency() — 用例一律按**活库真实列**建库（WP1 改 1 / 台账 R-A4）。

    旧用例自建 `gates(gate_id, result)` 幻影表并断言 `gates_fixed == 1`，与"读不存在的
    result 列 + 异常被吞"的坏写入端共谋，52 例全绿却查不出生产结构上的静默空转。
    """

    def _make_db(self, tmp_project, live_gates_ddl, live_tasks_projection_ddl):
        db_path = tmp_project / "data" / "databases" / "governance.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute(live_tasks_projection_ddl)
        conn.execute(live_gates_ddl)
        return db_path, conn

    def test_db_not_found(self, verifier, tmp_project):
        report = verifier.heal_db_consistency()
        assert report.healed is False
        assert "DB not found" in report.details

    def test_valid_live_rows_need_no_fix(self, verifier, tmp_project, live_gates_ddl, live_tasks_projection_ddl, insert_live_gate_row):
        db_path, conn = self._make_db(tmp_project, live_gates_ddl, live_tasks_projection_ddl)
        conn.execute("INSERT INTO tasks VALUES ('t1', 'T1', 'READY')")
        insert_live_gate_row(conn, "run-ok", passed=1, details="[]")
        conn.commit()
        conn.close()

        report = verifier.heal_db_consistency(db_path=db_path)
        assert report.healed is False
        assert report.tasks_fixed == 0
        assert report.gates_fixed == 0

    def test_unparseable_gate_details_is_detected_without_writing(
        self, verifier, tmp_project, live_gates_ddl, live_tasks_projection_ddl, insert_live_gate_row
    ):
        """活库真能非法的面：gates.details 是 `TEXT NOT NULL DEFAULT '{}'`、无 CHECK。

        改前：本方法读不存在的 result 列 ⇒ IndexError 被吞 ⇒ gates_fixed 恒 0（空转）。
        改后：默认 dry_run 只出计划，且**不落库**。
        """
        db_path, conn = self._make_db(tmp_project, live_gates_ddl, live_tasks_projection_ddl)
        insert_live_gate_row(conn, "run-bad-details", details="{not json at all")
        conn.commit()
        conn.close()

        report = verifier.heal_db_consistency(db_path=db_path)
        assert report.dry_run is True
        assert report.gates_fixed == 1
        assert report.tasks_fixed == 0
        assert any("details 非 JSON" in line for line in report.details)
        assert _read_gate_row(db_path, "run-bad-details") == (1, "{not json at all")

    def test_unparseable_gate_details_repaired_only_on_explicit_write(
        self, verifier, tmp_project, live_gates_ddl, live_tasks_projection_ddl, insert_live_gate_row
    ):
        db_path, conn = self._make_db(tmp_project, live_gates_ddl, live_tasks_projection_ddl)
        insert_live_gate_row(conn, "run-bad-details", details="{not json at all")
        conn.commit()
        conn.close()

        report = verifier.heal_db_consistency(db_path=db_path, dry_run=False, max_rows=5)
        assert report.dry_run is False
        assert report.gates_fixed == 1
        # 修复值 = 活库列默认值 '{}'（逐字照抄活库 DDL，不自造）
        assert _read_gate_row(db_path, "run-bad-details") == (1, "{}")

    def test_phantom_gate_columns_raise_instead_of_silent_noop(
        self, verifier, tmp_project, live_tasks_projection_ddl
    ):
        """负向用例（改 1 的验收硬要求）：幻影结构不再被吞成"0 行需修"的假绿。"""
        db_path = tmp_project / "data" / "databases" / "governance.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute(live_tasks_projection_ddl)
        conn.execute("CREATE TABLE gates (gate_id TEXT PRIMARY KEY, result TEXT)")
        conn.execute("INSERT INTO gates VALUES ('g1', 'BROKEN')")
        conn.commit()
        conn.close()

        with pytest.raises(HealRefusedError, match="列集与活库实列不符"):
            verifier.heal_db_consistency(db_path=db_path)

    def test_task_status_uses_derived_vocabulary_not_hardcoded_five(
        self, verifier, tmp_project, live_gates_ddl, live_tasks_projection_ddl
    ):
        """C-0 地雷的用例面：READY/BLOCKED 属真源 10 值 ⇒ 不得被判脏。"""
        db_path, conn = self._make_db(tmp_project, live_gates_ddl, live_tasks_projection_ddl)
        conn.execute("INSERT INTO tasks VALUES ('t-ready', 'R', 'READY')")
        conn.execute("INSERT INTO tasks VALUES ('t-blocked', 'B', 'BLOCKED')")
        conn.execute("INSERT INTO tasks VALUES ('t-bogus', 'X', 'NOT_A_STATUS')")
        conn.commit()
        conn.close()

        report = verifier.heal_db_consistency(db_path=db_path)
        assert report.tasks_fixed == 1
        assert any("t-bogus" in line for line in report.details)
        assert not any("t-ready" in line or "t-blocked" in line for line in report.details)
        assert _read_task_status(db_path, "t-ready") == "READY"
        assert _read_task_status(db_path, "t-blocked") == "BLOCKED"
        assert _read_task_status(db_path, "t-bogus") == "NOT_A_STATUS"  # dry-run 不落库

    def test_real_write_without_row_cap_is_refused(
        self, verifier, tmp_project, live_gates_ddl, live_tasks_projection_ddl, insert_live_gate_row
    ):
        db_path, conn = self._make_db(tmp_project, live_gates_ddl, live_tasks_projection_ddl)
        insert_live_gate_row(conn, "run-bad-details", details="[[[broken")
        conn.commit()
        conn.close()

        with pytest.raises(HealRefusedError, match="max_rows"):
            verifier.heal_db_consistency(db_path=db_path, dry_run=False)

    def test_row_cap_exceeded_refuses_write(
        self, verifier, tmp_project, live_gates_ddl, live_tasks_projection_ddl, insert_live_gate_row
    ):
        db_path, conn = self._make_db(tmp_project, live_gates_ddl, live_tasks_projection_ddl)
        insert_live_gate_row(conn, "run-1", details="[[[broken")
        insert_live_gate_row(conn, "run-2", details="]]]broken")
        conn.commit()
        conn.close()

        with pytest.raises(HealRefusedError, match="拒写"):
            verifier.heal_db_consistency(db_path=db_path, dry_run=False, max_rows=1)
        assert _read_gate_row(db_path, "run-1")[1] == "[[[broken"
        assert _read_gate_row(db_path, "run-2")[1] == "]]]broken"


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
