# [BLUEPRINT] MOD-FAC-007 | docs/03_modules/_domain_factor/strategy_iteration_upgrader/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FAC-007 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.research.test_strategy_iteration_upgrader
# [TESTS] src/zephyr/research/strategy_iteration_upgrader.py
"""MOD-FAC-007 单元测试：strategy_iteration_upgrader 策略迭代升级器。

蓝图验收（B10-02221/CAND-FAC-022，A1 D-RESEARCH-17）：
归因→权重调整建议（注入解析）+ 新因子候选（弱点方向映射算子库词表闭合）+
产物入 hypothesis_registry 回调 + 迭代历史留痕（seq 单调递增）。
parser/sink 全注入内存替身，不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.research.strategy_iteration_upgrader",
    reason="strategy_iteration_upgrader not importable",
)

from zephyr.research.strategy_iteration_upgrader import (  # noqa: E402
    DIRECTION_TEMPLATES,
    StrategyIterationUpgrader,
    StrategyUpgradeError,
    WeightAction,
)

_REPORT = [
    {"factor_id": "f_weak_mom", "weight": 0.5, "contribution": 0.01, "direction": "momentum"},
    {"factor_id": "f_strong_vol", "weight": 0.3, "contribution": 0.60, "direction": "volatility"},
    {"factor_id": "f_mid_trend", "weight": 0.2, "contribution": 0.10, "direction": "trend"},
]


def _parser(raw: object) -> list:
    return raw  # type: ignore[return-value]


def _upgrader(sink_records: list | None = None, **kw) -> StrategyIterationUpgrader:
    kw.setdefault("attribution_parser", _parser)
    if sink_records is not None:
        kw.setdefault(
            "hypothesis_sink",
            lambda payload: sink_records.append(payload) or f"HYP-{len(sink_records):04d}",
        )
    else:
        kw.setdefault("hypothesis_sink", lambda payload: "HYP-0001")
    return StrategyIterationUpgrader(**kw)


# ──────────────────────────────────────────────────────────────────────────────
# 构造 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_missing_parser(self) -> None:
        with pytest.raises(StrategyUpgradeError):
            StrategyIterationUpgrader(attribution_parser=None, hypothesis_sink=lambda p: "H")

    def test_missing_sink(self) -> None:
        with pytest.raises(StrategyUpgradeError):
            StrategyIterationUpgrader(attribution_parser=_parser, hypothesis_sink=None)

    def test_threshold_order(self) -> None:
        with pytest.raises(StrategyUpgradeError):
            _upgrader(weak_threshold=0.5, strong_threshold=0.2)

    def test_factor_coefficients(self) -> None:
        with pytest.raises(StrategyUpgradeError):
            _upgrader(increase_factor=0.9)
        with pytest.raises(StrategyUpgradeError):
            _upgrader(decrease_factor=1.5)


# ──────────────────────────────────────────────────────────────────────────────
# 归因解析（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestParse:
    def test_blank_strategy_id(self) -> None:
        with pytest.raises(StrategyUpgradeError):
            _upgrader().upgrade("  ", _REPORT)

    def test_empty_report(self) -> None:
        with pytest.raises(StrategyUpgradeError):
            _upgrader().upgrade("s1", [])

    def test_parser_exception_fail_closed(self) -> None:
        def boom(raw: object) -> list:
            raise RuntimeError("解析故障")

        with pytest.raises(StrategyUpgradeError):
            _upgrader(attribution_parser=boom).upgrade("s1", _REPORT)

    def test_bad_entry_structure(self) -> None:
        with pytest.raises(StrategyUpgradeError):
            _upgrader().upgrade("s1", [{"factor_id": "f1"}])  # 缺键

    def test_duplicate_factor_id(self) -> None:
        report = [dict(_REPORT[0]), dict(_REPORT[0])]
        with pytest.raises(StrategyUpgradeError):
            _upgrader().upgrade("s1", report)

    def test_unknown_direction_fail_closed(self) -> None:
        report = [dict(_REPORT[0], direction="sentiment")]  # 词表外
        with pytest.raises(StrategyUpgradeError):
            _upgrader().upgrade("s1", report)

    def test_negative_weight(self) -> None:
        report = [dict(_REPORT[0], weight=-0.1)]
        with pytest.raises(StrategyUpgradeError):
            _upgrader().upgrade("s1", report)


# ──────────────────────────────────────────────────────────────────────────────
# 权重建议 + 新因子候选 + registry 回调
# ──────────────────────────────────────────────────────────────────────────────


class TestUpgrade:
    def test_weight_suggestions_vocab(self) -> None:
        record = _upgrader().upgrade("s1", _REPORT)
        actions = {s.factor_id: s.action for s in record.weight_suggestions}
        assert actions["f_weak_mom"] is WeightAction.DECREASE
        assert actions["f_strong_vol"] is WeightAction.INCREASE
        assert actions["f_mid_trend"] is WeightAction.KEEP

    def test_suggested_weights_deterministic(self) -> None:
        record = _upgrader().upgrade("s1", _REPORT)
        w = {s.factor_id: s.suggested_weight for s in record.weight_suggestions}
        assert w["f_weak_mom"] == pytest.approx(round(0.5 * 0.8, 6))
        assert w["f_strong_vol"] == pytest.approx(round(0.3 * 1.2, 6))
        assert w["f_mid_trend"] == pytest.approx(0.2)  # keep 原权重

    def test_candidates_only_for_weak(self) -> None:
        record = _upgrader().upgrade("s1", _REPORT)
        assert {c.source_factor_id for c in record.factor_candidates} == {"f_weak_mom"}
        assert len(record.factor_candidates) == len(DIRECTION_TEMPLATES["momentum"])
        assert all(c.direction == "momentum" for c in record.factor_candidates)
        ids = [c.candidate_id for c in record.factor_candidates]
        assert ids == [f"SU-{i + 1:04d}" for i in range(len(ids))]

    def test_products_registered_via_sink(self) -> None:
        sink: list = []
        record = _upgrader(sink_records=sink).upgrade("s1", _REPORT)
        kinds = [p["kind"] for p in sink]
        # 1 条权重调整批（weak+strong 两条非 keep）+ 2 条因子候选
        assert kinds == ["weight_adjustment", "factor_candidate", "factor_candidate"]
        assert record.hypothesis_ids == ("HYP-0001", "HYP-0002", "HYP-0003")
        adj = sink[0]["suggestions"]
        assert {a["factor_id"] for a in adj} == {"f_weak_mom", "f_strong_vol"}

    def test_no_weight_payload_when_all_keep(self) -> None:
        sink: list = []
        report = [dict(_REPORT[2])]  # 仅中贡献 keep
        record = _upgrader(sink_records=sink).upgrade("s1", report)
        assert record.factor_candidates == ()
        assert record.hypothesis_ids == ()
        assert sink == []

    def test_sink_exception_fail_closed(self) -> None:
        def boom(payload: object) -> str:
            raise RuntimeError("登记故障")

        with pytest.raises(StrategyUpgradeError):
            _upgrader(hypothesis_sink=boom).upgrade("s1", _REPORT)

    def test_sink_bad_return_fail_closed(self) -> None:
        with pytest.raises(StrategyUpgradeError):
            _upgrader(hypothesis_sink=lambda p: "").upgrade("s1", _REPORT)


# ──────────────────────────────────────────────────────────────────────────────
# 迭代历史
# ──────────────────────────────────────────────────────────────────────────────


class TestHistory:
    def test_history_seq_monotonic(self) -> None:
        up = _upgrader()
        r1 = up.upgrade("s1", _REPORT)
        r2 = up.upgrade("s1", _REPORT)
        assert (r1.seq, r2.seq) == (1, 2)
        assert [r.seq for r in up.history()] == [1, 2]

    def test_candidate_ids_across_runs(self) -> None:
        up = _upgrader()
        up.upgrade("s1", _REPORT)
        r2 = up.upgrade("s1", _REPORT)
        ids = [c.candidate_id for c in r2.factor_candidates]
        assert ids[0] == "SU-0003"  # 计数器跨轮延续

    def test_full_determinism(self) -> None:
        def run() -> tuple:
            sink: list = []
            record = _upgrader(sink_records=sink).upgrade("s1", _REPORT)
            return (
                tuple((s.factor_id, s.action.value, s.suggested_weight) for s in record.weight_suggestions),
                tuple(c.expression for c in record.factor_candidates),
                record.hypothesis_ids,
            )

        assert run() == run()  # 同输入必同输出
