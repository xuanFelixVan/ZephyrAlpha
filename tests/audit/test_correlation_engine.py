# [A_test] module_id: SRC-TST-0629 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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


@pytest.fixture
def tmp_db(tmp_path):
    db_path = str(tmp_path / "drift_events.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE drift_events (scan_id TEXT, module_id TEXT, drift_dimension TEXT, state TEXT)")
    conn.executemany(
        "INSERT INTO drift_events VALUES (?,?,?,?)",
        [
            ("s1", "mod_a", "dim_x", "CONFIRMED"),
            ("s1", "mod_b", "dim_x", "CONFIRMED"),
            ("s2", "mod_a", "dim_y", "CONFIRMED"),
            ("s2", "mod_c", "dim_y", "CONFIRMED"),
            ("s3", "mod_b", "dim_x", "FALSE_POSITIVE"),
        ],
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def empty_db(tmp_path):
    db_path = str(tmp_path / "empty.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE drift_events (scan_id TEXT, module_id TEXT, drift_dimension TEXT, state TEXT)")
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
        assert engine._db_path is not None
        assert "drift_events.db" in engine._db_path

    def test_custom_db_path(self):
        engine = CorrelationEngine(db_path="/tmp/test.db")
        assert engine._db_path == "/tmp/test.db"


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
