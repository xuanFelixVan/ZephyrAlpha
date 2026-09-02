# [BLUEPRINT] MOD-DATA_GOV-007 | docs/03_modules/_domain_data_governance/column_lineage_analyzer/blueprint.md | §test
# [MODULE] tests.data_governance.test_column_lineage_analyzer
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] zephyr.data_governance.core.column_lineage_analyzer
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_column_lineage_analyzer.py
# [A_test] module_id: MOD-DATA_GOV-007 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-DATA_GOV-007 单元测试: M8-NEW-02 列级血缘分析器。

覆盖: 列节点命名 table.column 与 Fail-Closed 校验、sqlglot 缺失显式不可用错误、
列边→DAG 入图复用 S01 语义（去重/幂等/环拒记）、字段级影响面查询上游/下游、
未知节点空结果、端到端 建边→影响面。
"""

from __future__ import annotations

import pytest

from zephyr.data_governance.core.lineage_tracker import LineageTracker
from zephyr.data_governance.core.column_lineage_analyzer import (
    ColumnImpact,
    ColumnLineageEdge,
    ColumnLineageError,
    column_impact,
    column_node,
    extract_column_lineage,
    ingest_columns_into_tracker,
)


def _has_sqlglot() -> bool:
    try:
        import sqlglot  # noqa: F401
    except ImportError:
        return False
    return True


class TestColumnNode:
    def test_normal_naming(self) -> None:
        assert column_node("market.kline_daily", "close") == "market.kline_daily.close"

    def test_empty_table_fail_closed(self) -> None:
        with pytest.raises(ColumnLineageError):
            column_node("  ", "close")

    def test_empty_column_fail_closed(self) -> None:
        with pytest.raises(ColumnLineageError):
            column_node("t", "")


class TestExtractColumnLineage:
    def test_empty_sql_fail_closed(self) -> None:
        with pytest.raises(ColumnLineageError):
            extract_column_lineage("  ", target_table="factor_out")

    def test_empty_target_fail_closed(self) -> None:
        with pytest.raises(ColumnLineageError):
            extract_column_lineage("SELECT a FROM s", target_table=" ")

    def test_sqlglot_missing_fail_closed(self) -> None:
        if not _has_sqlglot():
            with pytest.raises(ColumnLineageError):
                extract_column_lineage("SELECT a FROM s", target_table="factor_out")
        else:
            edges = extract_column_lineage("SELECT a AS x, b + c AS y FROM src", target_table="factor_out")
            pairs = {(e.source_column, e.target_column) for e in edges}
            assert ("a", "x") in pairs
            assert ("b", "y") in pairs and ("c", "y") in pairs
            assert all(e.target_table == "factor_out" for e in edges)


class TestIngestColumnsIntoTracker:
    def _edges(self) -> list[ColumnLineageEdge]:
        return [
            ColumnLineageEdge("src", "close", "factor_out", "momentum", "close / prev_close - 1"),
            ColumnLineageEdge("src", "volume", "factor_out", "momentum", "volume * sign"),
        ]

    def test_ingest_builds_column_dag(self) -> None:
        tracker = LineageTracker()
        report = ingest_columns_into_tracker(self._edges(), tracker)
        assert report.edges == 2
        assert report.added == 2
        assert "src.close" in tracker.get_nodes()
        assert "factor_out.momentum" in tracker.get_downstream("src.close")
        assert "factor_out.momentum" in tracker.get_downstream("src.volume")

    def test_ingest_dedup_and_idempotent(self) -> None:
        tracker = LineageTracker()
        edges = self._edges() + [self._edges()[0]]  # 批内重复
        report = ingest_columns_into_tracker(edges, tracker)
        assert report.added == 2
        assert report.skipped == 1
        report2 = ingest_columns_into_tracker(self._edges(), tracker)
        assert report2.added == 0
        assert report2.updated == 2

    def test_ingest_none_tracker_fail_closed(self) -> None:
        with pytest.raises(ColumnLineageError):
            ingest_columns_into_tracker(self._edges(), None)


class TestColumnImpact:
    def _tracker(self) -> LineageTracker:
        tracker = LineageTracker()
        tracker.add_edge("market.kline_daily.close", "factor.momentum.value", "column:ratio")
        tracker.add_edge("factor.momentum.value", "signal.alpha.score", "column:map")
        return tracker

    def test_impact_mid_chain(self) -> None:
        tracker = self._tracker()
        impact = column_impact(tracker, "factor.momentum", "value")
        assert isinstance(impact, ColumnImpact)
        assert impact.node == "factor.momentum.value"
        assert impact.upstream == ("market.kline_daily.close",)
        assert impact.downstream == ("signal.alpha.score",)

    def test_impact_source_leaf(self) -> None:
        tracker = self._tracker()
        impact = column_impact(tracker, "market.kline_daily", "close")
        assert impact.upstream == ()
        assert impact.downstream == ("factor.momentum.value", "signal.alpha.score")

    def test_impact_unknown_node_empty(self) -> None:
        tracker = self._tracker()
        impact = column_impact(tracker, "nope", "nope_col")
        assert impact.upstream == ()
        assert impact.downstream == ()

    def test_impact_empty_ident_fail_closed(self) -> None:
        tracker = self._tracker()
        with pytest.raises(ColumnLineageError):
            column_impact(tracker, "", "value")
