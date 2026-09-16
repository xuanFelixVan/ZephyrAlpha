"""TD 序列单测——合成序列逐段核验（setup 计数/countdown/极值）。"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.strategy_factory.owner_band_t.td_sequence import (
    COUNTDOWN_THRESHOLD,
    SETUP_THRESHOLD,
    td_sequential,
)


def _mk(prices: list[float]) -> pd.DataFrame:
    s = pd.Series(prices, dtype=float)
    return td_sequential(s, s * 0.995)


def test_setup_counts_consecutive_declines():
    # 连续 close < close[4]: 跌段第 4..12 根（0 基）计数 1..9，之后封顶 9
    px = [10, 10, 10, 10, 9.9, 9.8, 9.7, 9.6, 9.5, 9.4, 9.3, 9.2, 9.1, 9.0]
    td = _mk(px)
    assert td["setup_count"].tolist()[4:13] == list(range(1, 10))
    assert td["setup_count"].tolist()[13] == 9  # TD 封顶，不再累计


def test_setup_resets_on_up_bar():
    px = [10, 10, 10, 10, 9.9, 9.8, 11.0, 9.6, 9.5, 9.4, 9.3, 9.2, 9.1, 9.0]
    td = _mk(px)
    sc = td["setup_count"].tolist()
    assert sc[6] == 0  # 上涨 bar 中断
    assert max(sc) < SETUP_THRESHOLD  # 未再计满


def test_countdown_after_setup_and_exhaustion():
    # 深跌 9 根完成 setup，随后继续阴跌触发 countdown 与极值
    px = [20, 20, 20, 20]
    px += list(np.linspace(19, 12, 9))  # setup 9 连跌
    px += list(np.linspace(11.5, 9.0, 10))  # countdown 段
    s = pd.Series(px, dtype=float)
    td = td_sequential(s, s * 0.999)
    assert td["setup_count"].max() >= SETUP_THRESHOLD
    # countdown 有推进
    assert td["countdown_count"].max() >= 1
    # 极值出现（low 创阶段新低）
    assert td["exhaustion"].any()


def test_countdown_neg_window_8_to_12():
    """冻结口径B: c-13<0 且 c>=8 -> 计数窗口 [8,12]（到 13 前提前入场）。"""
    assert COUNTDOWN_THRESHOLD == 13
    # 口径由 engine.build_entry_signal 落地: (c>=8)&(c<=12)
    px = [20, 20, 20, 20]
    px += list(np.linspace(19, 12, 9))
    px += list(np.linspace(11.8, 10.0, 14))
    s = pd.Series(px, dtype=float)
    td = td_sequential(s, s * 0.999)
    sig = (td["countdown_count"] >= 8) & (td["countdown_count"] <= 12)
    # 信号存在且非负计数
    assert sig.any()
    assert (td["countdown_count"] >= 0).all()


def test_length_mismatch_raises():
    import pytest

    with pytest.raises(ValueError, match="长度不一致"):
        td_sequential(pd.Series([1, 2, 3], dtype=float), pd.Series([1, 2], dtype=float))
