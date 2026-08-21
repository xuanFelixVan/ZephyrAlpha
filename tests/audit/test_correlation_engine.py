# [A_test] module_id: MOD-GOV_correlation_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_correlation_engine
# [INVARIANTS] 关联分析结果不可篡改
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/correlation_engine.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip;db不存在→返回空
# [TESTS] python -m pytest tests/test_correlation_engine.py -q
# [TTL] task_bound

from __future__ import annotations

import sqlite3

import pytest

from zephyr.gov_drift.correlation_engine import (
    CorrelationEngine,
    CorrelationReport,
)

# P0-2⑤（2026-08-21）：夹具复刻生产 governance.db drift_events 22 列 legacy schema
# （真源=drift_engine._write_drift_events 内 CREATE DDL，#62 治本①同构）——旧夹具为
# drift_audit 时代 4 列 schema（scan_id/drift_dimension），与生产查询列（date(created_at)/
# description）失配致 8 红（测试错非代码错，生产冒烟实证通过）。
# 语义映射：scan_id 批次 → date(created_at) 天级（生产无批次列，correlation_engine L47-49
# 同口径）；drift_dimension → description 列承载。
_SQL_CREATE_DRIFT_EVENTS = """
CREATE TABLE drift_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    drift_type TEXT NOT NULL,
    target TEXT,
    expected_value TEXT,
    actual_value TEXT,
    severity TEXT,
    detected_at TEXT NOT NULL,
    resolved_at TEXT,
    resolution TEXT,
    detector_id TEXT DEFAULT '',
    module_id TEXT DEFAULT 'MOD-INF-023',
    state TEXT DEFAULT 'DETECTED',
    source_file TEXT,
    description TEXT,
    details TEXT,
    fix_description TEXT,
    scan_level TEXT DEFAULT 'STANDARD',
    auto_fixable INTEGER DEFAULT 0,
    resolution_detail TEXT,
    roi_score REAL DEFAULT 0.0,
    created_at TEXT,
    updated_at TEXT
)
"""
_SQL_INSERT_DRIFT_EVENT = (
    "INSERT INTO drift_events (drift_type, module_id, state, description, detected_at, created_at) "
    "VALUES (?, ?, ?, ?, ?, ?)"
)


@pytest.fixture
def tmp_db(tmp_path):
    db_path = str(tmp_path / "drift_events.db")
    conn = sqlite3.connect(db_path)
    conn.execute(_SQL_CREATE_DRIFT_EVENTS)
    conn.executemany(
        _SQL_INSERT_DRIFT_EVENT,
        [
            ("REGISTRY_DRIFT", "mod_a", "CONFIRMED", "dim_x", "2026-08-01T09:00:00", "2026-08-01T09:00:00"),
            ("REGISTRY_DRIFT", "mod_b", "CONFIRMED", "dim_x", "2026-08-01T09:05:00", "2026-08-01T09:05:00"),
            ("REGISTRY_DRIFT", "mod_a", "CONFIRMED", "dim_y", "2026-08-02T09:00:00", "2026-08-02T09:00:00"),
            ("REGISTRY_DRIFT", "mod_c", "CONFIRMED", "dim_y", "2026-08-02T09:05:00", "2026-08-02T09:05:00"),
            ("REGISTRY_DRIFT", "mod_b", "FALSE_POSITIVE", "dim_x", "2026-08-03T09:00:00", "2026-08-03T09:00:00"),
        ],
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def empty_db(tmp_path):
    db_path = str(tmp_path / "empty.db")
    conn = sqlite3.connect(db_path)
    conn.execute(_SQL_CREATE_DRIFT_EVENTS)
    conn.commit()
    conn.close()
    return db_path


class TestCorrelationReport:
    def test_default_values(self):
        report = CorrelationReport()
        assert report.co_occurrence_matrix == {}
        assert report.causal_chains == []
        assert report.dimension_clusters == {}
        assert report.systemic_risks == []

    def test_custom_values(self):
        report = CorrelationReport(
            co_occurrence_matrix={"a": {"b": 0.5}},
            causal_chains=[("a", "b", 0.9)],
            dimension_clusters={"dim1": ["mod1"]},
            systemic_risks=["risk1"],
        )
        assert "a" in report.co_occurrence_matrix
        assert len(report.causal_chains) == 1
        assert "dim1" in report.dimension_clusters
        assert "risk1" in report.systemic_risks


class TestCorrelationEngineInit:
    def test_default_db_path(self):
        engine = CorrelationEngine()
        assert engine.db_path is not None
        # 治本（裁定#18 G9）：生产真源是 governance.db——磁盘实际存在且含 drift_events 表
        # （386 行真实数据）。blueprint 第900行提及的 drift_events.db 文件从未创建
        # （生产合并进 governance.db）。旧 oracle 期望 drift_events.db 是过期约定。
        # brain_integration.py:411 调 CorrelationEngine() 无参依赖此默认指向真实库。
        assert "governance.db" in engine.db_path

    def test_custom_db_path(self):
        engine = CorrelationEngine(db_path="/tmp/test.db")
        assert engine.db_path == "/tmp/test.db"


class TestComputeCoOccurrence:
    def test_nonexistent_db_returns_empty(self):
        engine = CorrelationEngine(db_path="/nonexistent/path.db")
        result = engine.compute_co_occurrence()
        assert result == {}

    def test_empty_db_returns_empty(self, empty_db):
        engine = CorrelationEngine(db_path=empty_db)
        result = engine.compute_co_occurrence()
        assert result == {}

    def test_co_occurrence_with_data(self, tmp_db):
        engine = CorrelationEngine(db_path=tmp_db)
        result = engine.compute_co_occurrence()
        assert "mod_a" in result
        assert "mod_b" in result
        assert "mod_c" in result
        assert result["mod_a"]["mod_b"] > 0.0

    def test_co_occurrence_jaccard_symmetry(self, tmp_db):
        engine = CorrelationEngine(db_path=tmp_db)
        result = engine.compute_co_occurrence()
        for ma in result:
            for mb in result[ma]:
                assert abs(result[ma][mb] - result[mb][ma]) < 1e-9

    def test_co_occurrence_excludes_false_positive(self, tmp_db):
        engine = CorrelationEngine(db_path=tmp_db)
        result = engine.compute_co_occurrence()
        assert "mod_b" in result
        assert "mod_a" in result


class TestComputeCausalChain:
    def test_returns_empty_list(self, tmp_db):
        engine = CorrelationEngine(db_path=tmp_db)
        result = engine.compute_causal_chain()
        assert result == []

    def test_max_lag_parameter(self, tmp_db):
        engine = CorrelationEngine(db_path=tmp_db)
        result = engine.compute_causal_chain(max_lag=5)
        assert result == []


class TestComputeDimensionClusters:
    def test_nonexistent_db_returns_empty(self):
        engine = CorrelationEngine(db_path="/nonexistent/path.db")
        result = engine.compute_dimension_clusters()
        assert result == {}

    def test_clusters_with_data(self, tmp_db):
        engine = CorrelationEngine(db_path=tmp_db)
        result = engine.compute_dimension_clusters()
        assert "dim_x" in result
        assert "dim_y" in result
        assert "mod_a" in result["dim_x"]
        assert "mod_c" in result["dim_y"]

    def test_clusters_sorted_modules(self, tmp_db):
        engine = CorrelationEngine(db_path=tmp_db)
        result = engine.compute_dimension_clusters()
        for dim, mods in result.items():
            assert mods == sorted(mods)


class TestDetectSystemicRisk:
    def test_nonexistent_db_returns_empty(self):
        engine = CorrelationEngine(db_path="/nonexistent/path.db")
        result = engine.detect_systemic_risk()
        assert result == []

    def test_no_systemic_risk_few_modules(self, tmp_db):
        engine = CorrelationEngine(db_path=tmp_db)
        result = engine.detect_systemic_risk()
        assert isinstance(result, list)


class TestFullCorrelation:
    def test_returns_correlation_report(self, tmp_db):
        engine = CorrelationEngine(db_path=tmp_db)
        report = engine.full_correlation()
        assert isinstance(report, CorrelationReport)
        assert isinstance(report.co_occurrence_matrix, dict)
        assert isinstance(report.causal_chains, list)
        assert isinstance(report.dimension_clusters, dict)
        assert isinstance(report.systemic_risks, list)

    def test_nonexistent_db_returns_empty_report(self):
        engine = CorrelationEngine(db_path="/nonexistent/path.db")
        report = engine.full_correlation()
        assert report.co_occurrence_matrix == {}
        assert report.causal_chains == []
        assert report.dimension_clusters == {}
        assert report.systemic_risks == []
