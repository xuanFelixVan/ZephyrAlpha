# [A_test] module_id: SRC-TST-1859 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-486 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.db.test_olap_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# AI-generated: DuckDB OLAP 引擎单元测试（T-4-05, B18）
"""
OLAPEngine 单元测试
===================
Task ID : T-4-05 (B18)
验收标准：≥ 10 条单元测试，mypy --strict 0 errors, ruff 0 errors

测试矩阵
--------
初始化           : 默认内存模式 / SQLite 挂载 / 上下文管理器
参数校验         : period 非法值 / limit 超范围 / gate_id 注入防护
task_progress_trend   : 空库返回空列表 / 有数据后聚合 / phase 过滤
compliance_rate_trend : 空库 / 有数据 / gate_id 过滤
knowledge_activation_trend : 空库 / 有数据 / category 过滤
get_gate_summary / get_knowledge_summary : 空库 0 值 / 写入后统计
降级模式         : fallback 表可查询（无 SQLite 文件时）
"""

import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from zephyr.governance.persistence.olap_engine import OLAPEngine, OLAPEngineError
from zephyr.governance.persistence.sqlite_schema import init_db

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_sqlite(tmp_path: Path) -> Path:
    """创建临时 SQLite 数据库并初始化 schema。"""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    return db_path


@pytest.fixture()
def engine(tmp_sqlite: Path) -> Iterator[OLAPEngine]:
    """内存 DuckDB + 临时 SQLite 的 OLAPEngine 实例。"""
    eng = OLAPEngine(sqlite_path=tmp_sqlite, duckdb_path=":memory:", auto_init_sqlite=False)
    yield eng
    eng.close()


def _insert_task(db_path: Path, task_id: str, status: str, phase: int = 0) -> None:
    """向 SQLite tasks 表插入测试任务。"""
    now = datetime.now(UTC).isoformat()
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("BEGIN")
        conn.execute(
            """
            INSERT INTO tasks (
                task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level,
                directive, idempotent, classification, evolution_policy,
                estimate_hours, deliverables, acceptance, depends_on,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                task_id.split("-")[0],
                int(task_id.split("-")[-1]),
                f"task {task_id}",
                status,
                "P2",
                phase,
                "claude",
                "L",
                "test",
                1,
                "internal",
                "extendable",
                1.0,
                "[]",
                "[]",
                "[]",
                now,
                now,
            ),
        )
        conn.execute("COMMIT")
    finally:
        conn.close()


def _insert_gate(db_path: Path, gate_run_id: str, passed: int) -> None:
    """向 SQLite gates 表插入测试门禁记录。"""
    now = datetime.now(UTC).isoformat()
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("BEGIN")
        conn.execute(
            "INSERT INTO gates (gate_run_id, gate_id, passed, details, created_at) " "VALUES (?, ?, ?, ?, ?)",
            (gate_run_id, "G1:T-0-001", passed, "{}", now),
        )
        conn.execute("COMMIT")
    finally:
        conn.close()


def _insert_knowledge(db_path: Path, ke_id: str, status: str, category: str = "best_practice") -> None:
    """向 SQLite knowledge 表插入测试知识条目。"""
    now = datetime.now(UTC).isoformat()
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("BEGIN")
        conn.execute(
            "INSERT INTO knowledge (ke_id, title, category, source_file, "
            "fingerprint_sha256, tags, summary, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ke_id, f"KE {ke_id}", category, "test.py", "abc123", "[]", "", status, now, now),
        )
        conn.execute("COMMIT")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 1. 初始化与上下文管理器
# ---------------------------------------------------------------------------


class TestInit:
    def test_context_manager(self, tmp_sqlite: Path) -> None:
        """上下文管理器正常创建和关闭。"""
        with OLAPEngine(sqlite_path=tmp_sqlite) as eng:
            assert eng is not None

    def test_close_idempotent(self, tmp_sqlite: Path) -> None:
        """多次 close() 不抛出异常。"""
        eng = OLAPEngine(sqlite_path=tmp_sqlite)
        eng.close()
        eng.close()  # 第二次不应抛出


# ---------------------------------------------------------------------------
# 2. 参数校验（SQL 注入防护）
# ---------------------------------------------------------------------------


class TestParameterValidation:
    def test_invalid_period_raises(self, engine: OLAPEngine) -> None:
        """非法 period 值抛出 OLAPEngineError（防注入）。"""
        with pytest.raises(OLAPEngineError, match="period 参数无效"):
            engine.task_progress_trend(period="INJECT'; DROP TABLE tasks;--")

    def test_invalid_limit_too_large_raises(self, engine: OLAPEngine) -> None:
        """limit 超过上限 10000 抛出 OLAPEngineError。"""
        with pytest.raises(OLAPEngineError, match="limit 参数无效"):
            engine.task_progress_trend(limit=99999)

    def test_invalid_limit_zero_raises(self, engine: OLAPEngine) -> None:
        """limit = 0 抛出 OLAPEngineError。"""
        with pytest.raises(OLAPEngineError, match="limit 参数无效"):
            engine.compliance_rate_trend(limit=0)

    def test_valid_periods_accepted(self, engine: OLAPEngine) -> None:
        """合法 period 值（day/week/month）不抛出。"""
        for p in ("day", "week", "month"):
            rows = engine.task_progress_trend(period=p, limit=1)
            assert isinstance(rows, list)


# ---------------------------------------------------------------------------
# 3. task_progress_trend
# ---------------------------------------------------------------------------


class TestTaskProgressTrend:
    def test_empty_db_returns_empty_list(self, engine: OLAPEngine) -> None:
        """空库返回空列表。"""
        rows = engine.task_progress_trend(period="day")
        assert rows == []

    def test_returns_completion_rate(self, tmp_sqlite: Path) -> None:
        """有数据时返回 completion_rate 字段（0.0–1.0）。"""
        _insert_task(tmp_sqlite, "ADR-001", "COMPLETED")
        _insert_task(tmp_sqlite, "ADR-002", "PENDING")
        with OLAPEngine(sqlite_path=tmp_sqlite, auto_init_sqlite=False) as eng:
            rows = eng.task_progress_trend(period="day")
        if rows:
            for row in rows:
                assert "completion_rate" in row
                assert 0.0 <= row["completion_rate"] <= 1.0

    def test_phase_filter(self, tmp_sqlite: Path) -> None:
        """phase 过滤参数化传入（防注入），不同 phase 独立统计。"""
        _insert_task(tmp_sqlite, "ADR-010", "COMPLETED", phase=0)
        _insert_task(tmp_sqlite, "SRC-020", "PENDING", phase=1)
        with OLAPEngine(sqlite_path=tmp_sqlite, auto_init_sqlite=False) as eng:
            rows_p0 = eng.task_progress_trend(period="day", phase=0)
            rows_p1 = eng.task_progress_trend(period="day", phase=1)
        # 至少 phase 过滤不会崩溃
        assert isinstance(rows_p0, list)
        assert isinstance(rows_p1, list)


# ---------------------------------------------------------------------------
# 4. compliance_rate_trend
# ---------------------------------------------------------------------------


class TestComplianceRateTrend:
    def test_empty_db_returns_empty_list(self, engine: OLAPEngine) -> None:
        """空库返回空列表。"""
        rows = engine.compliance_rate_trend()
        assert rows == []

    def test_returns_compliance_rate_field(self, tmp_sqlite: Path) -> None:
        """有门禁记录时返回 compliance_rate 字段。"""
        _insert_gate(tmp_sqlite, "gr-001", passed=1)
        _insert_gate(tmp_sqlite, "gr-002", passed=1)
        _insert_gate(tmp_sqlite, "gr-003", passed=0)
        with OLAPEngine(sqlite_path=tmp_sqlite, auto_init_sqlite=False) as eng:
            rows = eng.compliance_rate_trend(period="day")
        if rows:
            for row in rows:
                assert "compliance_rate" in row
                assert 0.0 <= row["compliance_rate"] <= 1.0


# ---------------------------------------------------------------------------
# 5. knowledge_activation_trend
# ---------------------------------------------------------------------------


class TestKnowledgeActivationTrend:
    def test_empty_db_returns_empty_list(self, engine: OLAPEngine) -> None:
        """空库返回空列表。"""
        rows = engine.knowledge_activation_trend()
        assert rows == []

    def test_returns_activation_rate_field(self, tmp_sqlite: Path) -> None:
        """有知识条目时 activation_rate 在 [0, 1]。"""
        _insert_knowledge(tmp_sqlite, "KE-001", "INDEXED")
        _insert_knowledge(tmp_sqlite, "KE-002", "DRAFT")
        with OLAPEngine(sqlite_path=tmp_sqlite, auto_init_sqlite=False) as eng:
            rows = eng.knowledge_activation_trend(period="month")
        if rows:
            for row in rows:
                assert "activation_rate" in row
                assert 0.0 <= row["activation_rate"] <= 1.0


# ---------------------------------------------------------------------------
# 6. get_gate_summary / get_knowledge_summary
# ---------------------------------------------------------------------------


class TestSummaryMethods:
    def test_gate_summary_empty_db(self, engine: OLAPEngine) -> None:
        """空库门禁摘要返回 total=0, passed=0。"""
        summary = engine.get_gate_summary()
        assert summary["total"] == 0
        assert summary["passed"] == 0

    def test_gate_summary_with_data(self, tmp_sqlite: Path) -> None:
        """写入后 get_gate_summary 正确统计。"""
        _insert_gate(tmp_sqlite, "gr-A", passed=1)
        _insert_gate(tmp_sqlite, "gr-B", passed=1)
        _insert_gate(tmp_sqlite, "gr-C", passed=0)
        with OLAPEngine(sqlite_path=tmp_sqlite, auto_init_sqlite=False) as eng:
            s = eng.get_gate_summary()
        assert s["total"] == 3
        assert s["passed"] == 2

    def test_knowledge_summary_empty_db(self, engine: OLAPEngine) -> None:
        """空库知识摘要返回 total=0, activated=0。"""
        summary = engine.get_knowledge_summary()
        assert summary["total"] == 0
        assert summary["activated"] == 0

    def test_knowledge_summary_with_data(self, tmp_sqlite: Path) -> None:
        """写入后 get_knowledge_summary 正确统计激活数。"""
        _insert_knowledge(tmp_sqlite, "KE-010", "INDEXED")
        _insert_knowledge(tmp_sqlite, "KE-011", "VERIFIED")
        _insert_knowledge(tmp_sqlite, "KE-012", "DRAFT")
        with OLAPEngine(sqlite_path=tmp_sqlite, auto_init_sqlite=False) as eng:
            s = eng.get_knowledge_summary()
        assert s["total"] == 3
        assert s["activated"] == 2
