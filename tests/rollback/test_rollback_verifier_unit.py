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

import pytest

from zephyr.infrastructure.rollback.rollback_verifier import (
    HealRefusedError,
    RollbackVerifier,
)


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


# gates/tasks 的建库语句来自 conftest 的活库真源夹具（live_gates_ddl /
# live_tasks_projection_ddl）——旧版此处自建 gates(gate_id, result) 幻影表，
# 生产库无 result 列，与坏写入端共谋出静默空转（WP1 改 1 / 台账 R-A4）。
def _create_test_db(
    db_path: Path,
    *,
    gates_ddl: str,
    tasks_ddl: str,
    tasks: bool = True,
    gates: bool = True,
    events: bool = True,
):
    conn = sqlite3.connect(str(db_path))
    if tasks:
        conn.execute(tasks_ddl)
    if gates:
        conn.execute(gates_ddl)
    if events:
        conn.execute("CREATE TABLE events (event_id TEXT PRIMARY KEY, type TEXT, data TEXT)")
    conn.commit()
    conn.close()


# 活库真实列的行模板（differential_check 只比行数，但建库列集仍须与活库一致）
_DIFF_GATE_INSERT = (
    "INSERT INTO gates (gate_run_id, gate_id, passed, details, created_at) "
    "VALUES ('{}', '{}', 1, '{{}}', '2026-09-19T00:00:00Z')"
)


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
    """heal_db_consistency() — DB 一致性自愈（用例按活库真实列建库，禁幻影表）"""

    def test_db_not_found(self):
        verifier = RollbackVerifier(project_root=Path(tempfile.mkdtemp()))
        report = verifier.heal_db_consistency()
        assert not report.healed
        assert "DB not found" in report.details

    def test_fixes_invalid_task_status(self, live_gates_ddl, live_tasks_projection_ddl):
        with _temp_dir() as root:
            db_path = root / "test_invalid_status.db"
            _create_test_db(db_path, gates_ddl=live_gates_ddl, tasks_ddl=live_tasks_projection_ddl)
            conn = sqlite3.connect(str(db_path))
            conn.execute("INSERT INTO tasks VALUES ('TASK-001', 'Test', 'INVALID_STATUS')")
            # READY 属真源 _DDL_TASKS 的 10 值（旧实现只认 5 值 ⇒ 230 行现值会被冤改）
            conn.execute("INSERT INTO tasks VALUES ('TASK-002', 'Test', 'READY')")
            conn.commit()
            conn.close()

            verifier = RollbackVerifier(project_root=root)
            report = verifier.heal_db_consistency(db_path=db_path, dry_run=False, max_rows=10)
            assert report.healed
            assert report.tasks_fixed == 1

            conn = sqlite3.connect(str(db_path))
            statuses = dict(conn.execute("SELECT task_id, status FROM tasks").fetchall())
            conn.close()
            assert statuses == {"TASK-001": "FAILED", "TASK-002": "READY"}

    def test_fixes_unparseable_gate_details(self, live_gates_ddl, live_tasks_projection_ddl, insert_live_gate_row):
        with _temp_dir() as root:
            db_path = root / "test_bad_gate_details.db"
            _create_test_db(db_path, gates_ddl=live_gates_ddl, tasks_ddl=live_tasks_projection_ddl)
            conn = sqlite3.connect(str(db_path))
            insert_live_gate_row(conn, "GATE-001", details="MAYBE")
            conn.commit()
            conn.close()

            verifier = RollbackVerifier(project_root=root)
            dry = verifier.heal_db_consistency(db_path=db_path)
            assert dry.dry_run is True
            assert dry.gates_fixed == 1
            conn = sqlite3.connect(str(db_path))
            assert conn.execute("SELECT details FROM gates WHERE gate_run_id='GATE-001'").fetchone()[0] == "MAYBE"
            conn.close()

            report = verifier.heal_db_consistency(db_path=db_path, dry_run=False, max_rows=10)
            assert report.healed
            assert report.gates_fixed == 1
            conn = sqlite3.connect(str(db_path))
            # 修复值=活库 gates.details 的列默认值（逐字照抄活库 DDL）
            assert conn.execute("SELECT details FROM gates WHERE gate_run_id='GATE-001'").fetchone()[0] == "{}"
            conn.close()

    def test_phantom_gate_shape_raises_instead_of_silent_noop(self, live_tasks_projection_ddl):
        """负向用例：旧幻影结构 gates(gate_id, result) 在生产库不存在。

        改前：读不存在的 result 列 ⇒ 每行 IndexError ⇒ 被内层 except 吞 ⇒ 恒 gates_fixed=0
        的静默空转（旧用例断言 ==1 只是幻影表自证的假绿）。
        改后：明确抛出，不再"看起来在工作"。
        """
        with _temp_dir() as root:
            db_path = root / "test_phantom_shape.db"
            conn = sqlite3.connect(str(db_path))
            conn.execute(live_tasks_projection_ddl)
            conn.execute("CREATE TABLE gates (gate_id TEXT PRIMARY KEY, result TEXT)")
            conn.execute("INSERT INTO gates VALUES ('GATE-001', 'MAYBE')")
            conn.commit()
            conn.close()

            verifier = RollbackVerifier(project_root=root)
            with pytest.raises(HealRefusedError, match="列集与活库实列不符"):
                verifier.heal_db_consistency(db_path=db_path)

    def test_valid_data_unchanged(self, live_gates_ddl, live_tasks_projection_ddl, insert_live_gate_row):
        with _temp_dir() as root:
            db_path = root / "test_valid.db"
            _create_test_db(db_path, gates_ddl=live_gates_ddl, tasks_ddl=live_tasks_projection_ddl)
            conn = sqlite3.connect(str(db_path))
            conn.execute("INSERT INTO tasks VALUES ('TASK-001', 'Test', 'COMPLETED')")
            insert_live_gate_row(conn, "GATE-001", passed=1, details="[]")
            conn.commit()
            conn.close()

            verifier = RollbackVerifier(project_root=root)
            report = verifier.heal_db_consistency(db_path=db_path, dry_run=False, max_rows=10)
            assert not report.healed

    def test_real_write_without_cap_is_refused(self, live_gates_ddl, live_tasks_projection_ddl, insert_live_gate_row):
        with _temp_dir() as root:
            db_path = root / "test_no_cap.db"
            _create_test_db(db_path, gates_ddl=live_gates_ddl, tasks_ddl=live_tasks_projection_ddl)
            conn = sqlite3.connect(str(db_path))
            insert_live_gate_row(conn, "GATE-001", details="MAYBE")
            conn.commit()
            conn.close()

            verifier = RollbackVerifier(project_root=root)
            with pytest.raises(HealRefusedError, match="max_rows"):
                verifier.heal_db_consistency(db_path=db_path, dry_run=False)
            conn = sqlite3.connect(str(db_path))
            assert conn.execute("SELECT details FROM gates WHERE gate_run_id='GATE-001'").fetchone()[0] == "MAYBE"
            conn.close()


class TestDifferentialCheck:
    """differential_check() — 回滚前后逐行比较"""

    def test_identical_databases_pass(self, live_gates_ddl, live_tasks_projection_ddl):
        with _temp_dir() as root:
            db_before = root / "before.db"
            db_after = root / "after.db"

            for db_name in (db_before, db_after):
                _create_test_db(db_name, gates_ddl=live_gates_ddl, tasks_ddl=live_tasks_projection_ddl)
                conn = sqlite3.connect(str(db_name))
                conn.execute("INSERT INTO tasks VALUES ('T-1', 'T1', 'PENDING')")
                conn.execute("INSERT INTO tasks VALUES ('T-2', 'T2', 'COMPLETED')")
                conn.execute(_DIFF_GATE_INSERT.format("R-1", "G-1"))
                conn.execute("INSERT INTO events VALUES ('E-1', 'drift', '{}')")
                conn.commit()
                conn.close()

            verifier = RollbackVerifier(project_root=root)
            report = verifier.differential_check(db_before, db_after)
            assert report.passed
            assert report.rows_mismatched == 0

    def test_divergent_row_counts_detected(self, live_gates_ddl, live_tasks_projection_ddl):
        with _temp_dir() as root:
            db_before = root / "before2.db"
            db_after = root / "after2.db"

            _create_test_db(db_before, gates_ddl=live_gates_ddl, tasks_ddl=live_tasks_projection_ddl)
            _create_test_db(db_after, gates_ddl=live_gates_ddl, tasks_ddl=live_tasks_projection_ddl)

            conn = sqlite3.connect(str(db_before))
            conn.execute("INSERT INTO tasks VALUES ('T-1', 'T1', 'PENDING')")
            conn.execute("INSERT INTO tasks VALUES ('T-2', 'T2', 'COMPLETED')")
            conn.execute(_DIFF_GATE_INSERT.format("R-1", "G-1"))
            conn.commit()
            conn.close()

            conn = sqlite3.connect(str(db_after))
            conn.execute("INSERT INTO tasks VALUES ('T-1', 'T1', 'PENDING')")
            conn.execute(_DIFF_GATE_INSERT.format("R-1", "G-1"))
            conn.commit()
            conn.close()

            verifier = RollbackVerifier(project_root=root)
            report = verifier.differential_check(db_before, db_after)
            assert not report.passed
            assert report.rows_mismatched > 0
