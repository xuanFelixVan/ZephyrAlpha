# [BLUEPRINT] MOD-FE-007 | docs/03_modules/_domain_frontend/value_stream_view/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-007 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.frontend.test_value_stream_view
# [TESTS] src/zephyr/frontend/value_stream_view.py
"""MOD-FE-007 单元测试：value_stream_view 价值流泳道视图器。

蓝图验收（B10-02410/CAND-FE-008，A1 M7-S06）：
五段词表闭合（数据/因子/信号/执行/组合）+ 模块→段归属映射 + 段间依赖边
（仅顺流）+ 依赖高亮（选中节点全链上下游传递闭包）。全内存构造，不触库。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.frontend.value_stream_view",
    reason="value_stream_view not importable",
)

from zephyr.frontend.value_stream_view import (  # noqa: E402
    StreamEdge,
    StreamStage,
    ValueStreamError,
    ValueStreamView,
)

_STAGES = {
    "market_data": StreamStage.DATA,
    "momentum_factor": StreamStage.FACTOR,
    "alpha_signal": StreamStage.SIGNAL,
    "t0_executor": StreamStage.EXECUTION,
    "portfolio": StreamStage.PORTFOLIO,
}

_CHAIN_EDGES = [
    StreamEdge("market_data", "momentum_factor"),
    StreamEdge("momentum_factor", "alpha_signal"),
    StreamEdge("alpha_signal", "t0_executor"),
    StreamEdge("t0_executor", "portfolio"),
]


def _view(edges=_CHAIN_EDGES) -> ValueStreamView:
    return ValueStreamView(module_stages=_STAGES, edges=edges)


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_ok(self) -> None:
        view = _view()
        assert view.stage_of("alpha_signal") is StreamStage.SIGNAL

    def test_empty_module_stages_raises(self) -> None:
        with pytest.raises(ValueStreamError):
            ValueStreamView(module_stages={}, edges=[])

    def test_blank_module_id_raises(self) -> None:
        with pytest.raises(ValueStreamError):
            ValueStreamView(module_stages={"": StreamStage.DATA}, edges=[])

    def test_invalid_stage_raises(self) -> None:
        with pytest.raises(ValueStreamError):
            ValueStreamView(module_stages={"m": "data"}, edges=[])  # type: ignore[dict-item]

    def test_edge_unknown_endpoint_raises(self) -> None:
        with pytest.raises(ValueStreamError):
            _view(edges=[StreamEdge("market_data", "ghost")])
        with pytest.raises(ValueStreamError):
            _view(edges=[StreamEdge("ghost", "portfolio")])

    def test_self_edge_raises(self) -> None:
        with pytest.raises(ValueStreamError):
            _view(edges=[StreamEdge("alpha_signal", "alpha_signal")])

    def test_backward_edge_raises(self) -> None:
        with pytest.raises(ValueStreamError):
            _view(edges=[StreamEdge("alpha_signal", "market_data")])  # 信号→数据 逆流

    def test_same_stage_edge_raises(self) -> None:
        stages = {"m1": StreamStage.FACTOR, "m2": StreamStage.FACTOR}
        with pytest.raises(ValueStreamError):
            ValueStreamView(module_stages=stages, edges=[StreamEdge("m1", "m2")])

    def test_skip_stage_edge_ok(self) -> None:
        view = _view(edges=[StreamEdge("market_data", "alpha_signal")])  # 数据→信号 跨段顺流
        assert len(view.stream_edges()) == 1

    def test_duplicate_edge_idempotent(self) -> None:
        view = _view(edges=[StreamEdge("market_data", "momentum_factor")] * 2)
        assert len(view.stream_edges()) == 1


# ──────────────────────────────────────────────────────────────────────────────
# 段归属 / 段间边
# ──────────────────────────────────────────────────────────────────────────────


class TestStageQuery:
    def test_stage_of_unknown_raises(self) -> None:
        with pytest.raises(ValueStreamError):
            _view().stage_of("ghost")

    def test_modules_in_stage_sorted(self) -> None:
        stages = {
            "z_factor": StreamStage.FACTOR,
            "a_factor": StreamStage.FACTOR,
            "data": StreamStage.DATA,
        }
        view = ValueStreamView(module_stages=stages, edges=[])
        assert view.modules_in_stage(StreamStage.FACTOR) == ("a_factor", "z_factor")
        assert view.modules_in_stage(StreamStage.SIGNAL) == ()

    def test_modules_in_stage_invalid_raises(self) -> None:
        with pytest.raises(ValueStreamError):
            _view().modules_in_stage("factor")  # type: ignore[arg-type]

    def test_stream_edges_sorted(self) -> None:
        edges = [StreamEdge("t0_executor", "portfolio"), StreamEdge("market_data", "momentum_factor")]
        view = _view(edges=edges)
        pairs = [(e.source, e.target) for e in view.stream_edges()]
        assert pairs == sorted(pairs)

    def test_stage_pairs_dedup_sorted(self) -> None:
        stages = dict(_STAGES, extra_data=StreamStage.DATA)
        edges = _CHAIN_EDGES + [StreamEdge("extra_data", "momentum_factor")]
        view = ValueStreamView(module_stages=stages, edges=edges)
        pairs = view.stage_pairs()
        assert pairs == (
            (StreamStage.DATA, StreamStage.FACTOR),
            (StreamStage.FACTOR, StreamStage.SIGNAL),
            (StreamStage.SIGNAL, StreamStage.EXECUTION),
            (StreamStage.EXECUTION, StreamStage.PORTFOLIO),
        )


# ──────────────────────────────────────────────────────────────────────────────
# 全链闭包高亮
# ──────────────────────────────────────────────────────────────────────────────


class TestHighlight:
    def test_full_chain_closure(self) -> None:
        payload = _view().highlight("alpha_signal")
        assert payload.selected == "alpha_signal"
        assert payload.upstream == ("market_data", "momentum_factor")
        assert payload.downstream == ("portfolio", "t0_executor")

    def test_source_module_closure(self) -> None:
        payload = _view().highlight("market_data")
        assert payload.upstream == ()
        assert payload.downstream == (
            "alpha_signal",
            "momentum_factor",
            "portfolio",
            "t0_executor",
        )

    def test_sink_module_closure(self) -> None:
        payload = _view().highlight("portfolio")
        assert payload.downstream == ()
        assert payload.upstream == (
            "alpha_signal",
            "market_data",
            "momentum_factor",
            "t0_executor",
        )

    def test_unrelated_excluded(self) -> None:
        stages = dict(_STAGES, side_data=StreamStage.DATA)
        view = ValueStreamView(module_stages=stages, edges=_CHAIN_EDGES)
        payload = view.highlight("alpha_signal")
        assert "side_data" not in payload.upstream
        assert "side_data" not in payload.downstream

    def test_unknown_module_raises(self) -> None:
        with pytest.raises(ValueStreamError):
            _view().highlight("ghost")

    def test_deterministic(self) -> None:
        assert _view().highlight("momentum_factor") == _view().highlight("momentum_factor")
