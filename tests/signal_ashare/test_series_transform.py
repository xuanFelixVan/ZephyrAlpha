# [BLUEPRINT] MOD-SIG-146 | tests/signal_ashare/test_series_transform.py
# [MODULE] tests.signal_ashare.test_series_transform
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.series_transform
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 合成数据，禁触 CH/生产路径；PIT 断言=只用 close 构造（不读 high/low）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/signal_ashare/test_series_transform.py
# [TTL] permanent
"""series_transform 单测（P2-c）——Renko/P&F/Kagi 构造语义 + PIT + 适配器。"""

from __future__ import annotations

from datetime import date

import pytest

from zephyr.signal_ashare.strategy_signal.series_transform import (
    KagiTransform,
    PnFTransform,
    RenkoTransform,
    adapt_to_engine,
)

_DATES4 = [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3), date(2026, 1, 4)]


# ── Renko ─────────────────────────────────────────────────────


def test_renko_up_and_down_bricks():
    s = RenkoTransform(brick_size=0.5)
    out = s.transform([10.0, 10.2, 10.55, 9.4])
    kinds = [(e.direction, e.price_lo, e.price_hi) for e in out.events]
    assert kinds == [("up", 10.0, 10.5), ("down", 9.5, 10.0)]
    assert out.events[0].confirmed_idx == 2  # 10.55 收盘过界 → 锚 bar2
    assert out.events[1].confirmed_idx == 3


def test_renko_multi_brick_on_jump():
    out = RenkoTransform(0.5).transform([10.0, 11.2])
    assert len(out.events) == 2  # 一次大跳两块砖
    assert [e.price_lo for e in out.events] == [10.0, 10.5]


def test_renko_pit_no_close_no_brick():
    # 盘中曾越过界（high 11.0）但收盘未过 → 不出砖（本层只看 close，天然无盘中触格）
    out = RenkoTransform(0.5).transform([10.0, 10.3, 10.2])
    assert len(out.events) == 0


# ── P&F ───────────────────────────────────────────────────────


def test_pnf_x_boxes_then_reversal_to_o():
    s = PnFTransform(box_size=0.3, reversal_boxes=3)
    out = s.transform([10.0, 10.4, 10.7, 9.6])
    dirs = [e.direction for e in out.events]
    assert dirs[0] == "up" and dirs[1] == "up"  # 两个 X 格
    assert dirs[-1] == "down"  # 逆走 3 格换 O 列
    # 换列首格=自列顶下一格
    last = out.events[-1]
    assert last.price_hi == pytest.approx(10.6)
    assert last.price_lo == pytest.approx(10.3)


def test_pnf_no_premature_reversal():
    out = PnFTransform(0.3, reversal_boxes=3).transform([10.0, 10.4, 10.2, 10.3])
    assert all(e.direction == "up" for e in out.events)  # 未满 3 格不换列


# ── Kagi ──────────────────────────────────────────────────────


def test_kagi_turn_on_threshold():
    out = KagiTransform(reversal_threshold=1.0).transform(
        [10.0, 10.5, 11.2, 10.1, 9.9],
    )
    assert len(out.events) == 1
    ev = out.events[0]
    assert ev.direction == "down" and ev.kind == "turn"
    assert ev.price_hi == pytest.approx(11.2)  # 自段极值回撤
    assert ev.confirmed_idx == 3


def test_kagi_no_turn_below_threshold():
    out = KagiTransform(1.0).transform([10.0, 10.5, 10.6, 10.2])
    assert len(out.events) == 0  # 最大回撤 0.4 < 1.0


# ── 参数校验 / 适配器 ─────────────────────────────────────────


def test_param_and_input_validation():
    with pytest.raises(ValueError, match="brick_size"):
        RenkoTransform(brick_size=0)
    with pytest.raises(ValueError, match="box_size"):
        PnFTransform(box_size=-1)
    with pytest.raises(ValueError, match="reversal_threshold"):
        KagiTransform(0)
    with pytest.raises(ValueError, match="长度>=2"):
        RenkoTransform(0.5).transform([10.0])
    with pytest.raises(ValueError, match="正有限"):
        RenkoTransform(0.5).transform([10.0, -1.0])


def test_adapter_and_ohlcv_like():
    out = RenkoTransform(0.5).transform([10.0, 10.2, 10.55, 9.4], _DATES4)
    pseudo = out.to_ohlcv_like()
    assert pseudo["closes"] == [10.5, 9.5]  # up 砖收顶/down 砖收底
    assert pseudo["highs"] == [10.5, 10.0]
    assert pseudo["lows"] == [10.0, 9.5]
    adapted = adapt_to_engine(out, "600519")
    assert adapted["symbol"] == "600519"
    assert len(adapted["closes"]) == len(adapted["highs"]) == len(adapted["lows"]) == 2
