# [BLUEPRINT] MOD-SIG-159 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SIG-159 capital_flow_direction_criterion 单元测试（st-fullflow2-20261008）。

红蓝对抗手法覆盖：
- 红-边界：标的族空/收盘缺标的/序列过短/不等长/非法值 fail-closed；零流动窗口 conviction=0 判 NONE
- 红-前视：纯函数确定性（同输入必同输出）
- 红-契约：conviction 手算对拍、streak 带符号语义（正流/负流/零流断号）、四档边界、背离注记
- 红-故障：build_from_moneyflow_rows 缺陷行跳过、乱序重排
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.source_line.capital_flow_direction_criterion import (
    CONVICTION_FOLLOW_MIN,
    CONVICTION_WATCH_MIN,
    DEFAULT_WINDOW,
    STREAK_FOLLOW_MIN,
    CapitalFlowInputError,
    CapitalFlowSnapshot,
    FlowTier,
    SymbolFlowCriterion,
    build_capital_flow_snapshot,
    build_from_moneyflow_rows,
    classify_flow_tier,
    flow_streak,
)

# ── 构造辅助 ────────────────────────────────────────────────────────────────

N = DEFAULT_WINDOW + 1


def _closes(n: int = N, base: float = 10.0, daily: float = 0.0) -> list[float]:
    return [base * (1.0 + daily) ** i for i in range(n)]


@pytest.fixture()
def steady_in_symbol():
    """连续 11 日净流入+价格上行的标的。"""
    return "IN600", [1.0e6 + 1.0e5 * i for i in range(N)], _closes(daily=0.005)


# ── 单元：classify_flow_tier ───────────────────────────────────────────────


class TestClassifyFlowTier:
    def test_follow_in_boundary(self):
        assert classify_flow_tier(CONVICTION_FOLLOW_MIN, STREAK_FOLLOW_MIN) == FlowTier.FOLLOW_IN
        assert classify_flow_tier(CONVICTION_FOLLOW_MIN - 0.01, STREAK_FOLLOW_MIN) == FlowTier.WATCH

    def test_follow_out_boundary(self):
        assert classify_flow_tier(-CONVICTION_FOLLOW_MIN, STREAK_FOLLOW_MIN) == FlowTier.FOLLOW_OUT
        assert classify_flow_tier(-CONVICTION_FOLLOW_MIN, -STREAK_FOLLOW_MIN) == FlowTier.FOLLOW_OUT
        assert classify_flow_tier(-CONVICTION_FOLLOW_MIN, STREAK_FOLLOW_MIN - 1) == FlowTier.WATCH

    def test_watch_and_none(self):
        assert classify_flow_tier(CONVICTION_WATCH_MIN, 0) == FlowTier.WATCH
        assert classify_flow_tier(CONVICTION_WATCH_MIN - 0.01, 9) == FlowTier.NONE
        assert classify_flow_tier(0.0, 5) == FlowTier.NONE


# ── 单元：flow_streak 带符号语义 ───────────────────────────────────────────


class TestFlowStreak:
    def test_positive_streak(self):
        assert flow_streak([1.0, 1.0, 1.0]) == 3

    def test_negative_streak(self):
        assert flow_streak([-1.0, -2.0]) == -2

    def test_zero_breaks_sign(self):
        assert flow_streak([1.0, 1.0, 0.0]) == 0
        assert flow_streak([-1.0, -1.0, 0.0, -1.0]) == -1

    def test_sign_flip_resets(self):
        assert flow_streak([1.0, 1.0, -1.0]) == -1

    def test_empty(self):
        assert flow_streak([]) == 0


# ── 快照主入口 ─────────────────────────────────────────────────────────────


class TestBuildSnapshot:
    def test_steady_inflow_is_follow_in(self, steady_in_symbol):
        sym, flows, closes = steady_in_symbol
        snap = build_capital_flow_snapshot({sym: flows}, {sym: closes})
        assert snap.follow_in_symbols == (sym,)
        c = snap.symbols[0]
        assert c.conviction == pytest.approx(1.0)
        assert c.streak == N
        assert c.flow_tier == FlowTier.FOLLOW_IN
        assert c.price_ret_window > 0.0

    def test_outflow_with_price_drop_is_follow_out(self):
        flows = [-(1.0e6 + 1.0e5 * i) for i in range(N)]
        closes = _closes(daily=-0.004)
        snap = build_capital_flow_snapshot({"OUT1": flows}, {"OUT1": closes})
        assert snap.follow_out_symbols == ("OUT1",)
        assert snap.symbols[0].divergence == ""

    def test_top_divergence_noted_not_retiered(self):
        """价格上行而持续净流出 → 顶背离 note，档位仍按流判。"""
        flows = [-(1.0e6 + 1.0e5 * i) for i in range(N)]
        closes = _closes(daily=0.006)
        snap = build_capital_flow_snapshot({"DIV": flows}, {"DIV": closes})
        c = snap.symbols[0]
        assert c.divergence == "TOP"
        assert c.flow_tier == FlowTier.FOLLOW_OUT

    def test_bottom_divergence_noted(self):
        """价格下行而持续净流入 → 底背离 note。"""
        flows = [1.0e6 + 1.0e5 * i for i in range(N)]
        closes = _closes(daily=-0.006)
        snap = build_capital_flow_snapshot({"DIV2": flows}, {"DIV2": closes})
        assert snap.symbols[0].divergence == "BOTTOM"

    def test_zero_flow_window_is_none_with_note(self):
        flows = [0.0] * N
        snap = build_capital_flow_snapshot({"FLAT": flows}, {"FLAT": _closes()})
        c = snap.symbols[0]
        assert c.conviction == 0.0
        assert c.flow_tier == FlowTier.NONE
        assert any("零流动" in s for s in c.notes)

    def test_sorted_by_abs_conviction_desc(self, steady_in_symbol):
        sym, flows, closes = steady_in_symbol
        mixed = {sym: flows, "WEAK": [1.0e6] + [1.0e4] * (N - 1)}
        mixed_closes = {sym: closes, "WEAK": _closes()}
        snap = build_capital_flow_snapshot(mixed, mixed_closes)
        convs = [abs(c.conviction) for c in snap.symbols]
        assert convs == sorted(convs, reverse=True)

    def test_determinism(self, steady_in_symbol):
        sym, flows, closes = steady_in_symbol
        a = build_capital_flow_snapshot({sym: flows}, {sym: closes}).to_dict()
        b = build_capital_flow_snapshot({sym: flows}, {sym: closes}).to_dict()
        assert a == b
        json.dumps(a, ensure_ascii=False)  # JSON 可序列化

    def test_to_dict_round_shape(self, steady_in_symbol):
        sym, flows, closes = steady_in_symbol
        d = build_capital_flow_snapshot({sym: flows}, {sym: closes}).to_dict()
        assert set(d) == {"window", "symbols", "follow_in_symbols", "follow_out_symbols", "notes"}
        assert set(d["symbols"][0]) == set(SymbolFlowCriterion.__dataclass_fields__)


# ── fail-closed 面 ─────────────────────────────────────────────────────────


class TestFailClosed:
    def test_empty_family(self):
        with pytest.raises(CapitalFlowInputError, match="标的族为空"):
            build_capital_flow_snapshot({}, {})

    def test_missing_close_symbol(self):
        with pytest.raises(CapitalFlowInputError, match="收盘表缺标的"):
            build_capital_flow_snapshot({"S1": [1.0] * N}, {})

    def test_short_series_symbol_skipped_alongside_valid(self, steady_in_symbol):
        """部分缺陷跳过记 notes：合法标的存活可判（标准化语义）。"""
        sym, flows, closes = steady_in_symbol
        snap = build_capital_flow_snapshot({"S1": [1.0] * 5, sym: flows}, {"S1": [10.0] * 5, sym: closes})
        assert [c.symbol for c in snap.symbols] == [sym]
        assert any("跳过标的 S1" in s for s in snap.notes)

    def test_all_invalid_raises_with_skip_notes(self):
        """全败=先例同款 raise（sector_rotation 全板块过短同款），错误信息携带 per-标的跳过原因。"""
        with pytest.raises(CapitalFlowInputError, match="无可判标的.*跳过标的 S1"):
            build_capital_flow_snapshot(
                {"S1": [1.0] * 3, "S2": [2.0] * 3},
                {"S1": [10.0] * 3, "S2": [20.0] * 3},
            )

    def test_nan_flow_symbol_skipped_alongside_valid(self, steady_in_symbol):
        sym, flows, closes = steady_in_symbol
        bad = list(flows)
        bad[3] = float("nan")
        snap = build_capital_flow_snapshot({sym: bad, "G": flows}, {sym: closes, "G": closes})
        assert [c.symbol for c in snap.symbols] == ["G"]
        assert any("跳过标的" in s for s in snap.notes)

    def test_negative_close_symbol_skipped_alongside_valid(self, steady_in_symbol):
        sym, flows, _ = steady_in_symbol
        bad = [-10.0] + [10.0] * (N - 1)
        snap = build_capital_flow_snapshot({sym: flows, "G": flows}, {sym: bad, "G": _closes()})
        assert [c.symbol for c in snap.symbols] == ["G"]

    def test_length_mismatch_symbol_skipped_alongside_valid(self, steady_in_symbol):
        sym, flows, closes = steady_in_symbol
        extra_flow = list(flows) + [1.0e5]  # 12 流水 vs 11 收盘：双过短判定各自过关后触发不等长
        snap = build_capital_flow_snapshot({sym: extra_flow, "G": flows}, {sym: closes, "G": closes})
        assert [c.symbol for c in snap.symbols] == ["G"]
        assert any("不等长" in s for s in snap.notes)


# ── DS 读入形态 ────────────────────────────────────────────────────────────


class TestBuildFromMoneyflowRows:
    def test_rows_group_and_sort(self, steady_in_symbol):
        sym, flows, closes = steady_in_symbol
        rows = [
            {"symbol": sym, "trade_date": f"2026100{i:02d}" if i < 10 else f"202610{i}", "net_main_amount": f}
            for i, f in enumerate(reversed(flows))
        ]
        snap = build_from_moneyflow_rows(rows, {sym: closes})
        assert snap.follow_in_symbols == (sym,)
        assert snap.symbols[0].streak == N

    def test_defect_rows_skipped(self, steady_in_symbol):
        sym, flows, closes = steady_in_symbol
        rows = [{"symbol": sym, "trade_date": i, "net_main_amount": f} for i, f in enumerate(flows)]
        rows.append({"symbol": sym, "trade_date": 99})  # 缺 flow 字段
        rows.append({"symbol": sym, "trade_date": 100, "net_main_amount": "x"})  # 非法值
        snap = build_from_moneyflow_rows(rows, {sym: closes})
        assert snap.symbols[0].streak == N
        assert any("缺陷 moneyflow 行 2 行" in s for s in snap.notes)
