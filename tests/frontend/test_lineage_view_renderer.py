# [BLUEPRINT] MOD-FE-008 | docs/03_modules/_domain_frontend/lineage_view_renderer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-008 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.frontend.test_lineage_view_renderer
# [TESTS] src/zephyr/frontend/lineage_view_renderer.py
"""MOD-FE-008 单元测试：lineage_view_renderer 血缘DAG渲染数据器。

蓝图验收（B10-02413/CAND-FE-009，A1 M8-S08）：
上下游高亮闭包（选中实体 N 跳邻居）+ 变更影响范围着色（变更实体→下游
影响集合，changed 优先于 impacted）+ 布局分层数据。实体/边快照全内存
构造（DI 注入），不重建 lineage_tracker。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.frontend.lineage_view_renderer",
    reason="lineage_view_renderer not importable",
)

from zephyr.frontend.lineage_view_renderer import (  # noqa: E402
    COLOR_CHANGED,
    COLOR_IMPACTED,
    COLOR_NORMAL,
    LineageEdge,
    LineageViewError,
    LineageViewRenderer,
)

# kline → momentum → alpha → t0；kline → volume → alpha
_ENTITIES = ("kline", "momentum", "volume", "alpha", "t0")
_EDGES = [
    LineageEdge("kline", "momentum", "compute"),
    LineageEdge("kline", "volume", "compute"),
    LineageEdge("momentum", "alpha", "generate"),
    LineageEdge("volume", "alpha", "generate"),
    LineageEdge("alpha", "t0", "execute"),
]


def _renderer(
    entities=_ENTITIES,
    edges=_EDGES,
) -> LineageViewRenderer:
    return LineageViewRenderer(entities=entities, edges=edges)


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_ok(self) -> None:
        renderer = _renderer()
        assert len(renderer.layout_layers()) == 4

    def test_empty_entities_raises(self) -> None:
        with pytest.raises(LineageViewError):
            LineageViewRenderer(entities=[], edges=[])

    def test_blank_entity_raises(self) -> None:
        with pytest.raises(LineageViewError):
            LineageViewRenderer(entities=["kline", ""], edges=[])

    def test_duplicate_entity_raises(self) -> None:
        with pytest.raises(LineageViewError):
            LineageViewRenderer(entities=["kline", "kline"], edges=[])

    def test_edge_unknown_endpoint_raises(self) -> None:
        with pytest.raises(LineageViewError):
            LineageViewRenderer(entities=["a"], edges=[LineageEdge("a", "ghost")])
        with pytest.raises(LineageViewError):
            LineageViewRenderer(entities=["a"], edges=[LineageEdge("ghost", "a")])

    def test_self_loop_raises(self) -> None:
        with pytest.raises(LineageViewError):
            LineageViewRenderer(entities=["a"], edges=[LineageEdge("a", "a")])

    def test_cycle_raises(self) -> None:
        edges = [LineageEdge("a", "b"), LineageEdge("b", "c"), LineageEdge("c", "a")]
        with pytest.raises(LineageViewError):
            LineageViewRenderer(entities=["a", "b", "c"], edges=edges)

    def test_duplicate_edge_idempotent(self) -> None:
        renderer = _renderer(edges=[LineageEdge("kline", "momentum")] * 2)
        payload = renderer.neighborhood("kline", hops=1)
        assert payload.downstream == ("momentum",)


# ──────────────────────────────────────────────────────────────────────────────
# N 跳上下游闭包
# ──────────────────────────────────────────────────────────────────────────────


class TestNeighborhood:
    def test_hops1_both_sides(self) -> None:
        payload = _renderer().neighborhood("momentum", hops=1)
        assert payload.selected == "momentum"
        assert payload.upstream == ("kline",)
        assert payload.downstream == ("alpha",)

    def test_hops2_transitive(self) -> None:
        payload = _renderer().neighborhood("momentum", hops=2)
        assert payload.downstream == ("alpha", "t0")

    def test_hops_bounded(self) -> None:
        # N 跳有界：hops=1 不到达隔代 kline
        payload = _renderer().neighborhood("alpha", hops=1)
        assert payload.upstream == ("momentum", "volume")
        assert payload.downstream == ("t0",)
        assert "kline" not in payload.upstream

    def test_source_entity_no_upstream(self) -> None:
        payload = _renderer().neighborhood("kline", hops=1)
        assert payload.upstream == ()
        assert payload.downstream == ("momentum", "volume")

    def test_unknown_entity_raises(self) -> None:
        with pytest.raises(LineageViewError):
            _renderer().neighborhood("ghost")

    def test_invalid_hops_raises(self) -> None:
        renderer = _renderer()
        with pytest.raises(LineageViewError):
            renderer.neighborhood("kline", hops=0)
        with pytest.raises(LineageViewError):
            renderer.neighborhood("kline", hops=-2)


# ──────────────────────────────────────────────────────────────────────────────
# 变更影响着色
# ──────────────────────────────────────────────────────────────────────────────


class TestImpactColors:
    def test_changed_and_downstream_colored(self) -> None:
        colors = _renderer().impact_colors(["kline"])
        assert colors["kline"] == COLOR_CHANGED
        assert colors["momentum"] == COLOR_IMPACTED
        assert colors["volume"] == COLOR_IMPACTED
        assert colors["alpha"] == COLOR_IMPACTED
        assert colors["t0"] == COLOR_IMPACTED

    def test_unrelated_normal(self) -> None:
        renderer = _renderer(entities=_ENTITIES + ("isolated",))
        colors = renderer.impact_colors(["momentum"])
        assert colors["momentum"] == COLOR_CHANGED
        assert colors["alpha"] == COLOR_IMPACTED
        assert colors["t0"] == COLOR_IMPACTED
        assert colors["kline"] == COLOR_NORMAL
        assert colors["volume"] == COLOR_NORMAL
        assert colors["isolated"] == COLOR_NORMAL

    def test_changed_precedence_over_impacted(self) -> None:
        # alpha 既是 kline 下游又自身变更 → changed 优先
        colors = _renderer().impact_colors(["kline", "alpha"])
        assert colors["kline"] == COLOR_CHANGED
        assert colors["alpha"] == COLOR_CHANGED
        assert colors["t0"] == COLOR_IMPACTED

    def test_empty_changed_raises(self) -> None:
        with pytest.raises(LineageViewError):
            _renderer().impact_colors([])

    def test_unknown_changed_raises(self) -> None:
        with pytest.raises(LineageViewError):
            _renderer().impact_colors(["ghost"])

    def test_result_covers_all_sorted(self) -> None:
        colors = _renderer().impact_colors(["alpha"])
        assert list(colors.keys()) == sorted(_ENTITIES)


# ──────────────────────────────────────────────────────────────────────────────
# 布局分层
# ──────────────────────────────────────────────────────────────────────────────


class TestLayoutLayers:
    def test_longest_path_layers(self) -> None:
        layers = _renderer().layout_layers()
        by_layer = {d.layer: d.entities for d in layers}
        assert by_layer[0] == ("kline",)
        assert by_layer[1] == ("momentum", "volume")
        assert by_layer[2] == ("alpha",)
        assert by_layer[3] == ("t0",)

    def test_entities_sorted_within_layer(self) -> None:
        layers = _renderer().layout_layers()
        for data in layers:
            assert list(data.entities) == sorted(data.entities)

    def test_deterministic(self) -> None:
        r1 = _renderer()
        r2 = _renderer(entities=tuple(reversed(_ENTITIES)))
        assert r1.layout_layers() == r2.layout_layers()
