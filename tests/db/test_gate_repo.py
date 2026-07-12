# [A_test] module_id: SRC-TST-1858 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-485 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.db.test_gate_repo
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
=============================================
覆盖矩阵：
  GateRepo.persist:
    - 正常持久化 × 1
    - 带 conn 参数 × 1
    - 返回 gate_run_id × 1
  GateRepo.query_by_task:
    - 按任务查询 × 1
    - limit 参数 × 1
    - 无匹配返回空 × 1
  GateRunRecord:
    - frozen dataclass × 1
=============================================
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.gov_enforcement.commit_gates.gate_repo import GateRepo, GateRunRecord
from zephyr.shared.utils.db_utils import ensure_schema


def _insert_task(db_path: Path, task_id: str = "OPS-1") -> None:
    import sqlite3

    from zephyr.shared.utils.time_utils import now_iso

    conn = sqlite3.connect(str(db_path), isolation_level=None)
    try:
        now = now_iso()
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "INSERT OR IGNORE INTO tasks (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, files_in_scope, depends_on, created_at, updated_at) VALUES (?, ?, ?, ?, 'PENDING', 'P2', 2, 'deepseek', 'M', '[]', '[]', ?, ?)",
            (task_id, task_id.split("-")[0], 1, f"test {task_id}", now, now),
        )
        conn.execute("COMMIT")
    finally:
        conn.close()


@pytest.fixture()
def repo(tmp_path: Path) -> GateRepo:
    db = tmp_path / "test_gates.db"
    ensure_schema(db)
    _insert_task(db, "OPS-1")
    _insert_task(db, "OPS-2")
    _insert_task(db, "OPS-3")
    _insert_task(db, "OPS-100")
    _insert_task(db, "OPS-200")
    r = GateRepo(db_path=db)
    yield r
    r.close()


class TestGateRepoPersist:
    def test_persist_returns_gate_run_id(self, repo: GateRepo) -> None:
        run_id = repo.persist(
            gate_id="G0",
            task_id="OPS-1",
            passed=True,
            violations=[],
        )
        assert run_id.startswith("gr-")

    def test_persist_with_violations(self, repo: GateRepo) -> None:
        run_id = repo.persist(
            gate_id="G1",
            task_id="OPS-2",
            passed=False,
            violations=[{"severity": "P0", "message": "test violation"}],
        )
        assert run_id.startswith("gr-")

    def test_persist_with_conn(self, tmp_path: Path) -> None:
        db = tmp_path / "test_conn.db"
        ensure_schema(db)
        _insert_task(db, "OPS-3")
        import sqlite3

        conn = sqlite3.connect(str(db), isolation_level=None)
        conn.row_factory = None
        repo = GateRepo(db_path=db)
        try:
            conn.execute("BEGIN IMMEDIATE")
            run_id = repo.persist(
                gate_id="G2",
                task_id="OPS-3",
                passed=True,
                violations=[],
                conn=conn,
            )
            conn.execute("COMMIT")
            assert run_id.startswith("gr-")
        finally:
            repo.close()
            conn.close()


class TestGateRepoQuery:
    def test_query_by_task(self, repo: GateRepo) -> None:
        repo.persist(
            gate_id="G0",
            task_id="OPS-100",
            passed=True,
            violations=[],
        )
        records = repo.query_by_task("OPS-100")
        assert len(records) >= 1
        assert records[0].task_id == "OPS-100"
        assert records[0].gate_id.startswith("G0")
        assert records[0].passed is True

    def test_query_by_task_no_match(self, repo: GateRepo) -> None:
        records = repo.query_by_task("NONEXISTENT-999")
        assert records == []

    def test_query_by_task_limit(self, repo: GateRepo) -> None:
        for i in range(5):
            repo.persist(
                gate_id="G0",
                task_id="OPS-200",
                passed=True,
                violations=[],
            )
        records = repo.query_by_task("OPS-200", limit=3)
        assert len(records) == 3


class TestGateRunRecord:
    def test_frozen(self) -> None:
        r = GateRunRecord(
            gate_run_id="gr-test",
            gate_id="G0",
            passed=True,
            details="{}",
            artifact_path=None,
            session_id=None,
            task_id="OPS-1",
            created_at="2026-01-01T00:00:00",
        )
        with pytest.raises(AttributeError):
            r.passed = False  # type: ignore[misc]
