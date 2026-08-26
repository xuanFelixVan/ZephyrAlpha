# [BLUEPRINT] MOD-DATA_GOV-012 | docs/03_modules/_domain_data_governance/column_lineage_tracker/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATA_GOV-012 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_governance.test_column_lineage_tracker
# [TESTS] src/zephyr/data_governance/column_lineage_tracker.py
"""MOD-DATA_GOV-012 单元测试：column_lineage_tracker 列级血缘追踪器。

蓝图验收（B10-02321/CAND-DATGOV-009，A1 M8-NEW-02）：
列级映射边（source_col->target_col+transform 表达式）+ 登记接口（环检测/幂
等更新）+ 列级上下游查询（上游列链/下游影响列闭包）+ 删列影响面分析。
纯内存确定性，不触网不触盘。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.data_governance.column_lineage_tracker",
    reason="column_lineage_tracker not importable",
)

from zephyr.data_governance.column_lineage_tracker import (  # noqa: E402
    ColumnLineageError,
    ColumnLineageTracker,
    ColumnMapping,
    ColumnRef,
)


def _tracker() -> ColumnLineageTracker:
    t = ColumnLineageTracker()
    # kline.close -> mom20.value -> alpha.score
    t.register("kline", "close", "mom20", "value", "sma(close,20)")
    t.register("mom20", "value", "alpha", "score", "rank(value)")
    return t


# ──────────────────────────────────────────────────────────────────────────────
# ColumnRef 解析
# ──────────────────────────────────────────────────────────────────────────────


class TestColumnRef:
    def test_parse_ok(self) -> None:
        ref = ColumnRef.parse("kline.close")
        assert ref.table == "kline" and ref.column == "close"
        assert str(ref) == "kline.close"

    def test_parse_no_dot_raises(self) -> None:
        with pytest.raises(ColumnLineageError):
            ColumnRef.parse("klineclose")

    def test_parse_two_dots_raises(self) -> None:
        with pytest.raises(ColumnLineageError):
            ColumnRef.parse("db.kline.close")

    def test_parse_empty_side_raises(self) -> None:
        with pytest.raises(ColumnLineageError):
            ColumnRef.parse(".close")
        with pytest.raises(ColumnLineageError):
            ColumnRef.parse("kline.")


# ──────────────────────────────────────────────────────────────────────────────
# 映射登记
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_ok_and_transform_recorded(self) -> None:
        t = _tracker()
        m = t.mappings()
        assert len(m) == 2
        assert m[0].transform == "sma(close,20)"

    def test_empty_name_raises(self) -> None:
        t = ColumnLineageTracker()
        with pytest.raises(ColumnLineageError):
            t.register("", "close", "mom20", "value")
        with pytest.raises(ColumnLineageError):
            t.register("kline", "", "mom20", "value")
        with pytest.raises(ColumnLineageError):
            t.register("kline", "close", "", "value")
        with pytest.raises(ColumnLineageError):
            t.register("kline", "close", "mom20", "")

    def test_self_mapping_raises(self) -> None:
        t = ColumnLineageTracker()
        with pytest.raises(ColumnLineageError):
            t.register("kline", "close", "kline", "close")

    def test_cycle_rejected(self) -> None:
        t = _tracker()
        with pytest.raises(ColumnLineageError):
            t.register("alpha", "score", "kline", "close")  # 成环

    def test_duplicate_edge_updates_transform(self) -> None:
        t = _tracker()
        t.register("kline", "close", "mom20", "value", "ema(close,20)")
        transforms = [m.transform for m in t.mappings()]
        assert "ema(close,20)" in transforms and "sma(close,20)" not in transforms
        assert len(t.mappings()) == 2  # 幂等不新增

    def test_register_mapping_equivalent(self) -> None:
        t = ColumnLineageTracker()
        m = ColumnMapping(ColumnRef("a", "x"), ColumnRef("b", "y"), "f(x)")
        t.register_mapping(m)
        assert t.mappings() == (m,)

    def test_register_mapping_empty_endpoint_raises(self) -> None:
        t = ColumnLineageTracker()
        with pytest.raises(ColumnLineageError):
            t.register_mapping(ColumnMapping(ColumnRef("", "x"), ColumnRef("b", "y")))


# ──────────────────────────────────────────────────────────────────────────────
# 上下游查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_direct_upstream(self) -> None:
        t = _tracker()
        assert t.direct_upstream("mom20", "value") == (ColumnRef("kline", "close"),)

    def test_direct_downstream(self) -> None:
        t = _tracker()
        assert t.direct_downstream("mom20", "value") == (ColumnRef("alpha", "score"),)

    def test_upstream_closure_transitive(self) -> None:
        t = _tracker()
        assert t.upstream_columns("alpha", "score") == (
            ColumnRef("kline", "close"),
            ColumnRef("mom20", "value"),
        )

    def test_downstream_closure_transitive(self) -> None:
        t = _tracker()
        assert t.downstream_columns("kline", "close") == (
            ColumnRef("alpha", "score"),
            ColumnRef("mom20", "value"),
        )

    def test_unknown_node_returns_empty(self) -> None:
        t = _tracker()
        assert t.upstream_columns("ghost", "x") == ()
        assert t.downstream_columns("ghost", "x") == ()

    def test_diamond_dedup(self) -> None:
        t = ColumnLineageTracker()
        t.register("a", "x", "b", "y")
        t.register("a", "x", "c", "y")
        t.register("b", "y", "d", "z")
        t.register("c", "y", "d", "z")
        down = t.downstream_columns("a", "x")
        assert down == (ColumnRef("b", "y"), ColumnRef("c", "y"), ColumnRef("d", "z"))

    def test_output_sorted_deterministic(self) -> None:
        t = ColumnLineageTracker()
        t.register("s", "c", "t2", "c2")
        t.register("s", "c", "t1", "c2")
        t.register("s", "c", "t1", "c1")
        down = t.downstream_columns("s", "c")
        assert down == tuple(sorted(down))


# ──────────────────────────────────────────────────────────────────────────────
# 删列影响面
# ──────────────────────────────────────────────────────────────────────────────


class TestDropImpact:
    def test_drop_source_column_full_surface(self) -> None:
        t = _tracker()
        impact = t.drop_column_impact("kline", "close")
        assert impact == (ColumnRef("alpha", "score"), ColumnRef("mom20", "value"))

    def test_drop_mid_chain_partial_surface(self) -> None:
        t = _tracker()
        impact = t.drop_column_impact("mom20", "value")
        assert impact == (ColumnRef("alpha", "score"),)

    def test_drop_leaf_no_impact(self) -> None:
        t = _tracker()
        assert t.drop_column_impact("alpha", "score") == ()
