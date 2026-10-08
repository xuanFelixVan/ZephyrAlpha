# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | tests/backtest/fexam/test_conditional_exam.py | CYC条件变量考场单测（合成已知真值零DB）
"""conditional_exam 单测：相位分桶边界/宽度阈值/N_fam 冻结/HAC 统计量恢复/植入异质性判活。

真值策略（预注册卡 §5 判据的统计量正确性验证）：
- 分桶：卡 §2 切点常数逐值断言（floor 语义边界 90/180/270 归下一层）。
- 宽度阈值：99 三元组=缺失、100=计算（卡 §4.2）。
- N_fam：层有效日数冻结规则 C(3,2)=3、(3,4,2,2)→11（卡 §5.2）。
- HAC：与 statsmodels 恰同调用逐位对拍 + 植入均值漂移的恢复力。
- 判活：植入层间 IC 异质（层内秩相关 0.5 vs 0）→ pass；同质噪声 → fail。
测试零 DB：全部合成面板；无 data/ 写入（T10）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

FEXAM = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam"
if str(FEXAM) not in sys.path:
    sys.path.insert(0, str(FEXAM))

from conditional_exam import (  # noqa: E402
    MIN_SECTION_WIDTH,
    blind_layer_counts,
    daily_cross_ic,
    hac_t_test,
    run_indicator,
    strata_dcperiod,
    strata_dcphase,
    strata_sine,
    strata_trendmode,
)

RNG = np.random.default_rng(20261008)


def _panel(values: np.ndarray) -> pd.DataFrame:
    idx = pd.date_range("2025-01-01", periods=values.shape[0], freq="B")
    cols = [f"S{i:04d}" for i in range(values.shape[1])]
    return pd.DataFrame(values, index=idx, columns=cols)


# ── 相位分桶：切点=实现常数，floor 边界语义 ────────────────────────────────────


def test_strata_dcphase_floor_boundaries() -> None:
    phase = _panel(np.array([[0.0, 89.99, 90.0, 179.99, 180.0, 269.99, 270.0, 359.99, 360.0, np.nan]]))
    labels = strata_dcphase(phase)
    row = labels.iloc[0]
    expect = ["P1", "P1", "P2", "P2", "P3", "P3", "P4", "P4", None, None]
    for got, want in zip(row.tolist(), expect, strict=True):
        assert got == want or (want is None and pd.isna(got))


def test_strata_dcperiod_cuts() -> None:
    dc = _panel(np.array([[6.0, 20.0, 20.5, 35.0, 35.5, 50.0, np.nan]]))
    row = strata_dcperiod(dc).iloc[0]
    expect = ["D1", "D1", "D2", "D2", "D3", "D3", None]
    for got, want in zip(row.tolist(), expect, strict=True):
        assert got == want or (want is None and pd.isna(got))


def test_strata_sine_and_trendmode() -> None:
    sine = _panel(np.array([[1.0, 0.5, np.nan]]))
    lead = _panel(np.array([[0.5, 1.0, 1.0]]))
    row = strata_sine(sine, lead).iloc[0]
    assert row.tolist()[0] == "W1" and row.tolist()[1] == "W0" and pd.isna(row.tolist()[2])
    tm = _panel(np.array([[1.0, 0.0, 2.0, np.nan]]))
    row = strata_trendmode(tm).iloc[0]
    assert row.tolist()[0] == "M1" and row.tolist()[1] == "M0"
    assert row.tolist()[2] is None or pd.isna(row.tolist()[2])
    assert pd.isna(row.tolist()[3])


# ── 宽度阈值与已知 IC 值 ──────────────────────────────────────────────────────


def test_daily_cross_ic_width_threshold_and_known_value() -> None:
    t = pd.Timestamp("2025-01-06")
    # 99 有效 → 缺失（卡 §4.3：<100 记缺失）
    b99 = _panel(RNG.normal(size=(1, 99)))
    r99 = _panel(RNG.normal(size=(1, 99)))
    assert pd.isna(daily_cross_ic(b99, r99).iloc[0])
    # 100 有效、完美单调 → IC=1.0（spearman 已知真值）
    b100 = _panel(np.arange(100, dtype=float).reshape(1, 100))
    r100 = _panel(np.arange(100, dtype=float).reshape(1, 100) * 2.0 + 1.0)
    ic = daily_cross_ic(b100, r100)
    assert int((ic.notna()).sum()) == 1
    assert abs(ic.iloc[0] - 1.0) < 1e-12
    # 反向完美单调 → IC=-1.0
    rrev = _panel((-np.arange(100)).reshape(1, 100))
    assert abs(daily_cross_ic(b100, rrev).iloc[0] + 1.0) < 1e-12
    assert MIN_SECTION_WIDTH == 100


def test_stratum_daily_ic_matches_manual_spearman() -> None:
    rng = np.random.default_rng(7)
    b = _panel(rng.normal(size=(3, 300)))
    r5 = _panel(rng.normal(size=(3, 300)))
    label = _panel(np.array([["A"] * 150 + ["B"] * 150] * 3, dtype=object))
    from conditional_exam import stratum_daily_ic

    ic_a = stratum_daily_ic(b, r5, label, "A")
    # 手工真值：第 0 日 A 层子截面 spearman
    sub_b = b.iloc[0, :150]
    sub_r = r5.iloc[0, :150]
    want = sub_b.corr(sub_r, method="spearman")
    assert abs(ic_a.iloc[0] - want) < 1e-12
    # 伪造一层宽度不足 → NaN
    label_small = _panel(np.array([["A"] * 5 + ["B"] * 295] * 3, dtype=object))
    assert pd.isna(stratum_daily_ic(b, r5, label_small, "A").iloc[0])


# ── HAC 统计量：恰同调用对拍 + 漂移恢复 ───────────────────────────────────────


def test_hac_t_test_matches_statsmodels_exactly() -> None:
    import statsmodels.api as sm

    rng = np.random.default_rng(11)
    d = pd.Series(rng.normal(loc=0.03, scale=0.2, size=200))
    stat = hac_t_test(d)
    res = sm.OLS(endog=d.to_numpy(dtype="float64"), exog=np.ones((200, 1))).fit(
        cov_type="HAC", cov_kwds={"maxlags": 10}
    )
    assert stat["n_days"] == 200
    assert stat["t_hac"] == pytest.approx(float(res.tvalues[0]), abs=0, rel=1e-12)
    assert stat["p_raw"] == pytest.approx(float(res.pvalues[0]), abs=0, rel=1e-12)
    assert stat["mean_d"] == pytest.approx(float(d.mean()), abs=0, rel=1e-12)


def test_hac_t_test_power_and_degenerate() -> None:
    rng = np.random.default_rng(13)
    strong = pd.Series(rng.normal(loc=0.5, scale=0.2, size=250))
    assert hac_t_test(strong)["p_raw"] < 1e-10
    silent = pd.Series(rng.normal(loc=0.0, scale=0.2, size=250))
    assert abs(hac_t_test(silent)["t_hac"]) < 3.0  # 零漂移不假阳（5σ 保险外）
    assert hac_t_test(pd.Series([1.0]))["degenerate"] is True
    assert hac_t_test(pd.Series([1.0, 1.0, 1.0]))["degenerate"] is True  # se=0


# ── N_fam 冻结（卡 §5.2：层有效日数规则→族大小）───────────────────────────────


def _labels(n_days: int, layout: dict[str, int]) -> pd.DataFrame:
    vals = []
    for _s, n in layout.items():
        vals += [_s] * n
    arr = np.array([vals] * n_days, dtype=object)
    idx = pd.date_range("2025-01-01", periods=n_days, freq="B")
    cols = [f"S{i:04d}" for i in range(len(vals))]  # 列名与 _panel 同款，保证按位对齐
    return pd.DataFrame(arr, index=idx, columns=cols)


def test_blind_layer_counts_family_size_freeze() -> None:
    days = 40
    layout = {"A": 150, "B": 150, "C": 150, "TINY": 40}  # TINY 恒 <100 宽 → 剔除
    label = _labels(days, layout)
    b = _panel(RNG.normal(size=(days, 490)))
    r5 = _panel(RNG.normal(size=(days, 490)))
    blind = blind_layer_counts(
        {"IND-X": label},
        b,
        r5,
        (str(b.index[0].date()), str(b.index[-1].date())),
        strata_order={"IND-X": ["A", "B", "C", "TINY"]},
    )
    assert blind["k_eff"]["IND-X"] == 3  # TINY 因宽度<100 全缺失被剔
    assert blind["family_size"] == 3  # C(3,2)
    assert set(blind["stratum_day_counts"]["IND-X"]) == {"A", "B", "C", "TINY"}
    assert blind["stratum_day_counts"]["IND-X"]["TINY"] == 0
    assert blind["voided"] == {}


def test_blind_layer_counts_void_when_single_layer() -> None:
    days = 40
    label = _labels(days, {"A": 200, "B": 10})  # B 恒 <100 宽
    b = _panel(RNG.normal(size=(days, 210)))
    r5 = _panel(RNG.normal(size=(days, 210)))
    blind = blind_layer_counts(
        {"IND-Y": label},
        b,
        r5,
        (str(b.index[0].date()), str(b.index[-1].date())),
        strata_order={"IND-Y": ["A", "B"]},
    )
    assert blind["k_eff"]["IND-Y"] == 1
    assert blind["family_size"] == 0
    assert "IND-Y" in blind["voided"]


# ── 植入异质性端到端：判活/判死方向正确（合成已知真值）─────────────────────────


def _planted_panel(hetero: bool, n_days: int = 120) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """三层层标签；hetero=True 时 A 层内 r5=0.5*rank(B) 秩信息+噪声，B/C 纯噪声。"""
    rng = np.random.default_rng(489)
    layout = {"A": 120, "B": 150, "C": 130}
    label = _labels(n_days, layout)
    b = _panel(rng.normal(size=(n_days, 400)))
    r5 = np.empty((n_days, 400))
    idx_a = list(range(layout["A"]))  # 布局顺序：A 在前
    idx_rest = list(range(layout["A"], 400))
    for t in range(n_days):
        row = rng.normal(size=400)
        if hetero:
            rank_z = pd.Series(b.iloc[t, idx_a].to_numpy()).rank(pct=True).to_numpy()
            row[idx_a] = 0.8 * (rank_z - rank_z.mean()) + rng.normal(size=len(idx_a))
        row[idx_rest] = rng.normal(size=len(idx_rest))
        r5[t] = row
    return b, _panel(r5), label


def test_run_indicator_pass_on_planted_heterogeneity() -> None:
    b, r5, label = _planted_panel(hetero=True)
    out = run_indicator(
        "IND-X",
        label,
        b,
        r5,
        (str(b.index[0].date()), str(b.index[-1].date())),
        3,
        None,
        strata_list=["A", "B", "C"],
    )
    assert out["verdict"] == "pass"
    assert out["best_stratum"] == "A"
    assert out["gain"] > 0
    sig = [p for p in out["pairs"] if p["p_adj"] < 0.05]
    assert len(sig) >= 1
    assert abs(out["strata"]["A"]["mu_s"]) > 0.15  # 植入 0.8·pct_rank 对 std=1 噪声→理论 spearman≈0.23


def test_run_indicator_fail_on_homogeneous_noise() -> None:
    b, r5, label = _planted_panel(hetero=False)
    out = run_indicator(
        "IND-X",
        label,
        b,
        r5,
        (str(b.index[0].date()), str(b.index[-1].date())),
        3,
        None,
        strata_list=["A", "B", "C"],
    )
    assert out["verdict"] == "fail"
    assert not [p for p in out["pairs"] if p["p_adj"] < 0.05]


def test_run_indicator_void_branch() -> None:
    b, r5, label = _planted_panel(hetero=True)
    out = run_indicator(
        "IND-X",
        label,
        b,
        r5,
        (str(b.index[0].date()), str(b.index[-1].date())),
        3,
        "有效层不足 2",
        strata_list=["A", "B", "C"],
    )
    assert out["verdict"] == "void"
    assert out["void_reason"] == "有效层不足 2"
    assert out["pairs"] == []
