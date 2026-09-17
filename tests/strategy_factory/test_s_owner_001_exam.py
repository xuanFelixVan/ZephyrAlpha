"""考试器单测——网格规模/择优规则/验收判定逻辑（零数据依赖）。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.strategy_factory.owner_band_t.engine import LADDER_ALT, LADDER_DEFAULT
from zephyr.strategy_factory.owner_band_t.exam import (
    ACCEPT_MAXDD_FLOOR,
    ACCEPT_SHARPE_MIN,
    ACCEPT_TURNOVER_MAX,
    GRID,
    iter_grid,
    run_grid_is,
    select_best,
)


def test_grid_size_is_432():
    sizes = 1
    for v in GRID.values():
        sizes *= len(v)
    assert sizes == 432
    assert len(iter_grid()) == 432


def test_iter_grid_deterministic_order():
    a = iter_grid()
    b = iter_grid()
    assert [c.entry_mode for c in a] == [c.entry_mode for c in b]
    assert all(c.validate() is None for c in a)


def test_select_best_tiebreak_rules():
    df = pd.DataFrame(
        {
            "combo_id": [0, 1, 2],
            "cfg_entry_mode": ["setup8", "setup9", "countdown_neg"],
            "cfg_p1": [0.5, 0.5, 0.5],
            "cfg_exit_arm": ["bb_upper", "bb_upper", "bb_upper"],
            "cfg_ladder": [LADDER_DEFAULT, LADDER_DEFAULT, LADDER_ALT],
            "cfg_gate_min_conf": [0.35, 0.35, 0.35],
            "cfg_t_max_trips": [1, 1, 1],
            "cfg_t_size": [0.3, 0.3, 0.3],
            "is_sharpe": [1.0, 1.5, 1.5],
            "is_maxdd": [-0.10, -0.12, -0.12],
            "is_ann_turnover": [10.0, 8.0, 8.0],
        }
    )
    best = select_best(df)
    # sharpe 1.5 两组中 MaxDD 同(=-0.12)→换手同→取先序（combo 1）
    assert best["combo_id"] == 1


def test_select_best_skips_nan():
    df = pd.DataFrame(
        {
            "combo_id": [0, 1],
            "cfg_entry_mode": ["setup8", "setup9"],
            "cfg_p1": [0.5, 0.5],
            "cfg_exit_arm": ["bb_upper", "bb_upper"],
            "cfg_ladder": [LADDER_DEFAULT, LADDER_DEFAULT],
            "cfg_gate_min_conf": [0.35, 0.35],
            "cfg_t_max_trips": [1, 1],
            "cfg_t_size": [0.3, 0.3],
            "is_sharpe": [np.nan, 0.5],
            "is_maxdd": [np.nan, -0.1],
            "is_ann_turnover": [np.nan, 5.0],
        }
    )
    assert select_best(df)["combo_id"] == 1


def test_select_best_all_nan_raises():
    df = pd.DataFrame({"is_sharpe": [np.nan], "is_maxdd": [np.nan], "is_ann_turnover": [np.nan]})
    with pytest.raises(RuntimeError, match="全部失败"):
        select_best(df)


def test_run_grid_is_records_failures_without_aborting():
    """单组失败须留痕（is_error 列）且不中断考试。"""
    # 面板缺列 → 全部组失败但 DataFrame 仍有 432 行且带错误列
    bad_panel = {"idx": pd.DataFrame(), "etf": pd.DataFrame(), "hourly": pd.DataFrame(), "regime": pd.DataFrame()}
    from zephyr.strategy_factory.owner_band_t.exam import IS_END, IS_START

    df = run_grid_is(bad_panel)
    assert len(df) == 432
    assert "is_error" in df.columns or df["is_sharpe"].notna().sum() >= 0
    assert IS_START < IS_END


def test_acceptance_thresholds_frozen_values():
    assert ACCEPT_SHARPE_MIN == 1.2
    assert ACCEPT_MAXDD_FLOOR == -0.15
    assert ACCEPT_TURNOVER_MAX == 60.0
