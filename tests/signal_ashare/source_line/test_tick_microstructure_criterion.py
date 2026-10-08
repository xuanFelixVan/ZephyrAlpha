# [BLUEPRINT] MOD-SIG-156 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SIG-156 tick_microstructure_criterion 单元测试（st-fg-srcline1-20261005）。

红蓝对抗手法覆盖：
- 红-边界：空/过短/NaN/非正价量/不等长/方向非法 fail-closed
- 红-前视：纯函数确定性（同输入必同输出）
- 红-契约：不平衡五档阈值边界、冲击成本代理手算对拍、尾段动量窗口
- 红-故障：build_from_ticks 缺陷笔跳过记 notes
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.source_line.tick_microstructure_criterion import (
    BUY_MIN,
    STRONG_BUY_MIN,
    TAIL_MIN_TICKS,
    DirectionLean,
    ImbalanceTier,
    TickMicroCriterion,
    TickMicroInputError,
    build_from_ticks,
    build_tick_micro_criterion,
    classify_imbalance_tier,
    direction_lean_of,
)

# ── 构造辅助 ────────────────────────────────────────────────────────────────


def _ticks(n: int, side="B", drift: float = 0.01):
    """合成 tick 序列：价格线性漂移，等量，方向可控。"""
    prices = [10.0 + drift * i for i in range(n)]
    volumes = [100.0] * n
    sides = [side] * n
    return prices, volumes, sides


# ── 档位分类 ────────────────────────────────────────────────────────────────


class TestImbalanceTier:
    def test_five_tiers_boundary(self):
        assert classify_imbalance_tier(STRONG_BUY_MIN) == ImbalanceTier.STRONG_BUY
        assert classify_imbalance_tier(BUY_MIN) == ImbalanceTier.BUY
        assert classify_imbalance_tier(0.0) == ImbalanceTier.NEUTRAL
        assert classify_imbalance_tier(-BUY_MIN) == ImbalanceTier.SELL
        assert classify_imbalance_tier(-STRONG_BUY_MIN) == ImbalanceTier.STRONG_SELL

    def test_just_below_thresholds(self):
        assert classify_imbalance_tier(STRONG_BUY_MIN - 1e-9) == ImbalanceTier.BUY
        assert classify_imbalance_tier(-STRONG_BUY_MIN + 1e-9) == ImbalanceTier.SELL


class TestDirectionLean:
    def test_aligned_follows_imbalance(self):
        assert direction_lean_of(ImbalanceTier.STRONG_BUY, True) == DirectionLean.LONG
        assert direction_lean_of(ImbalanceTier.STRONG_SELL, False) == DirectionLean.SHORT

    def test_divergence_flat(self):
        assert direction_lean_of(ImbalanceTier.STRONG_BUY, False) == DirectionLean.FLAT
        assert direction_lean_of(ImbalanceTier.STRONG_SELL, True) == DirectionLean.FLAT

    def test_neutral_or_unknown_flat(self):
        assert direction_lean_of(ImbalanceTier.NEUTRAL, True) == DirectionLean.FLAT
        assert direction_lean_of(ImbalanceTier.BUY, None) == DirectionLean.FLAT


# ── 主入口契约 ──────────────────────────────────────────────────────────────


class TestBuildCriterion:
    def test_all_buy_strong(self):
        prices, volumes, sides = _ticks(60, side="B")
        crit = build_tick_micro_criterion("600000", prices, volumes, sides)
        assert crit.imbalance == pytest.approx(1.0)
        assert crit.imbalance_tier == ImbalanceTier.STRONG_BUY
        assert crit.direction_lean == DirectionLean.LONG

    def test_all_sell_strong(self):
        prices, volumes, sides = _ticks(60, side="S", drift=-0.01)
        crit = build_tick_micro_criterion("600000", prices, volumes, sides)
        assert crit.imbalance == pytest.approx(-1.0)
        assert crit.imbalance_tier == ImbalanceTier.STRONG_SELL
        assert crit.direction_lean == DirectionLean.SHORT

    def test_mixed_neutral_flat(self):
        prices, volumes, _ = _ticks(60)
        sides = ["B", "S"] * 30
        crit = build_tick_micro_criterion("600000", prices, volumes, sides)
        assert crit.imbalance == pytest.approx(0.0)
        assert crit.imbalance_tier == ImbalanceTier.NEUTRAL
        assert crit.direction_lean == DirectionLean.FLAT

    def test_impact_coef_handcheck(self):
        # 价格 10,11,13 量 100,100：|Δp| = 1+2 = 3，Σv（后笔）=200 → 0.015
        crit = build_tick_micro_criterion("600000", [10.0, 11.0, 13.0], [100.0, 100.0, 100.0], ["B", "B", "B"])
        assert crit.impact_coef == pytest.approx(3.0 / 200.0)

    def test_side_alias_normalization(self):
        # buy/1 与 sell/0/-1 别名等价归一
        prices, volumes, _ = _ticks(20)
        crit_a = build_tick_micro_criterion("600000", prices, volumes, ["B"] * 20)
        crit_b = build_tick_micro_criterion("600000", prices, volumes, ["buy"] * 20)
        crit_c = build_tick_micro_criterion("600000", prices, volumes, ["1"] * 20)
        assert crit_a.imbalance == crit_b.imbalance == crit_c.imbalance

    def test_divergence_note(self):
        # 买向不平衡 + 尾段跌价 → 背离 flat + notes
        prices = [20.0 - 0.1 * i for i in range(60)]  # 单边下跌
        volumes = [100.0] * 60
        sides = ["B"] * 50 + ["S"] * 10
        crit = build_tick_micro_criterion("600000", prices, volumes, sides)
        assert crit.imbalance_tier in (ImbalanceTier.STRONG_BUY, ImbalanceTier.BUY)
        assert crit.direction_lean == DirectionLean.FLAT
        assert any("背离" in n for n in crit.notes)

    def test_to_dict_json_serializable(self):
        prices, volumes, sides = _ticks(30)
        crit = build_tick_micro_criterion("600000", prices, volumes, sides)
        d = crit.to_dict()
        assert json.dumps(d, ensure_ascii=False)
        assert set(d) == {
            "symbol",
            "n_ticks",
            "imbalance",
            "imbalance_tier",
            "impact_coef",
            "tail_ret",
            "direction_lean",
            "notes",
        }

    def test_deterministic(self):
        prices, volumes, sides = _ticks(50)
        a = build_tick_micro_criterion("600000", prices, volumes, sides)
        b = build_tick_micro_criterion("600000", prices, volumes, sides)
        assert a == b


# ── fail-closed 契约 ───────────────────────────────────────────────────────


class TestFailClosed:
    def test_empty_and_short(self):
        with pytest.raises(TickMicroInputError, match="过短"):
            build_tick_micro_criterion("600000", [10.0], [1.0], ["B"])
        with pytest.raises(TickMicroInputError, match="过短"):
            build_tick_micro_criterion("600000", [], [], [])

    def test_length_mismatch(self):
        with pytest.raises(TickMicroInputError, match="不等长"):
            build_tick_micro_criterion("600000", [10.0] * 5, [1.0] * 4, ["B"] * 5)

    def test_nonpositive_price(self):
        with pytest.raises(TickMicroInputError, match="成交价非法"):
            build_tick_micro_criterion("600000", [10.0, 0.0], [1.0, 1.0], ["B", "B"])

    def test_negative_volume(self):
        with pytest.raises(TickMicroInputError, match="成交量非法"):
            build_tick_micro_criterion("600000", [10.0, 11.0], [1.0, -5.0], ["B", "B"])

    def test_nan_price(self):
        with pytest.raises(TickMicroInputError, match="成交价非法"):
            build_tick_micro_criterion("600000", [10.0, float("nan")], [1.0, 1.0], ["B", "B"])

    def test_illegal_side(self):
        with pytest.raises(TickMicroInputError, match="方向非法"):
            build_tick_micro_criterion("600000", [10.0, 11.0], [1.0, 1.0], ["B", "X"])


# ── DS 读入形态（build_from_ticks） ─────────────────────────────────────────


class TestBuildFromTicks:
    def test_defective_ticks_skipped_with_notes(self):
        ticks = [{"price": 10.0 + 0.01 * i, "volume": 100.0, "side": "B"} for i in range(30)]
        ticks.append({"price": 11.0})  # 缺 volume/side
        ticks.append({"price": "abc", "volume": 1, "side": "B"})  # 非法值
        crit = build_from_ticks("600000", ticks)
        assert any("跳过缺陷 tick 2" in n for n in crit.notes)

    def test_all_defective_fails_closed(self):
        with pytest.raises(TickMicroInputError):
            build_from_ticks("600000", [{"price": 10.0}])
