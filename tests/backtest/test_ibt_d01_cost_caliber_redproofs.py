# [BLUEPRINT] MOD-BT-191 | docs/03_modules/_domain_backtest/blueprint.md | §IBT D01 成本口径红证
# [MODULE] tests.backtest.test_ibt_d01_cost_caliber_redproofs
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts/backtest/translated/_c4_engine.py; scripts/backtest/cost_model.py
# [CONSUMERS] IBT v2 集成回测成本口径红证（D01 考卷成本面）：冻结土规构成钉死/滑点五档
#   单调/印花单腿/换手折半口径/env 选档 fail-closed/注入点透传
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 红证断言失败即口径漂移；全合成数据零 CH 零生产路径写；常量经引擎模块
#   （COMMISSION_BP/STAMP_BP/SLIPPAGE_BP）禁字面量；遗失重建适配器语义禁伪造（fail-closed 钉）
# [MODIFY-GUARD] scripts/backtest/translated/_c4_engine.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红（R12 xfail(strict=False)=标定档回归后转正钉）
# [TESTS] self
# [TTL] task_bound
# [TEST] tests/backtest/test_ibt_d01_cost_caliber_redproofs.py
# 覆盖（收尾清欠重建，按现行契约修剪自原 19+1xpassed 面12）：R1 缺省=SLIPPAGE_BP 逐位/
#   R2 净线构成式/R3 印花单腿（round-trip 聚合只计一次）/R4 滑点档严格单调/R5 零滑点下界
#   （佣金+印花地板）/R6 恒仓日零成本/R7 换手 |Δw|/2 单边口径/R8-R9 env 缺席=legacy 逐位
#   零漂移/R10 未知档引擎面 fail-closed/R11 注入标量 κ 全程透传/R12 标定档占位 xpass 钉。
# 铁律：不连 CH、不写 data/。
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
_TRANSLATED = _REPO / "scripts" / "backtest" / "translated"
for _p in (str(_REPO / "src"), str(_TRANSLATED)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import itertools

import _c4_engine as eng  # noqa: E402

_ENV_KEY = "ZEPHYR_C4_COST_MODEL"


def _panel(seed: int = 11, days: int = 60, cols: tuple[str, ...] = ("000998", "000999")):
    """合成权重/价格宽表（确定种子；权重含建仓-持有-调仓-清仓全动作）。"""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2026-01-05", periods=days, freq="B")
    px = pd.DataFrame(rng.uniform(50.0, 100.0, size=(days, len(cols))), index=idx, columns=list(cols))
    w = pd.DataFrame(0.0, index=idx, columns=list(cols))
    w.iloc[3:] = 0.6  # 建仓
    w.iloc[20:40, 0] = 0.3  # 调仓
    w.iloc[40:, :] = 0.0  # 清仓
    return w, px


def _gross_turnover(w: pd.DataFrame, px: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    return eng._backtest_core(w, px, backend="cpu")


# ---------- R1 缺省口径 ----------


def test_r1_default_caliber_is_engine_slippage_constant():
    """缺省（slippage_bp=None）逐位=显式 SLIPPAGE_BP 档（冻结土规零漂移）。"""
    w, px = _panel()
    base = eng.daily_net_returns(w, px, backend="cpu")
    pinned = eng.daily_net_returns(w, px, slippage_bp=eng.SLIPPAGE_BP, backend="cpu")
    pd.testing.assert_series_equal(base, pinned)


# ---------- R2/R3 净线构成与印花单腿 ----------


def test_r2_net_line_composition_matches_frozen_formula():
    """net=gross−turnover×(佣金×2+印花+滑点×2)/1e4——常量全部经引擎模块。"""
    w, px = _panel()
    gross, turnover = _gross_turnover(w, px)
    net = eng.daily_net_returns(w, px, slippage_bp=6.0, backend="cpu")
    expect = gross - turnover * (eng.COMMISSION_BP * 2 + eng.STAMP_BP + 6.0 * 2) / 10000.0
    pd.testing.assert_series_equal(net, expect)


def test_r3_stamp_is_single_leg_in_round_trip_aggregate():
    """红证：印花只在卖腿——round-trip 聚合式里 STAMP 恰计一次（双计口径差=turnover×STAMP/1e4）。"""
    w, px = _panel()
    gross, turnover = _gross_turnover(w, px)
    net = eng.daily_net_returns(w, px, slippage_bp=5.0, backend="cpu")
    single_stamp = gross - turnover * (eng.COMMISSION_BP * 2 + eng.STAMP_BP + 5.0 * 2) / 10000.0
    double_stamp = gross - turnover * (eng.COMMISSION_BP * 2 + eng.STAMP_BP * 2 + 5.0 * 2) / 10000.0
    pd.testing.assert_series_equal(net, single_stamp)
    drift = (double_stamp - single_stamp).abs().max()
    assert drift == pytest.approx(float((turnover * eng.STAMP_BP / 10000.0).max()))


# ---------- R4/R5 滑点档与零滑点下界 ----------


def test_r4_net_strictly_monotone_in_slippage_tiers():
    """五档扫描（0/5/10/20/40bp）：净值对滑点全域非增、换手日严格递减（成本只随换手发生）。"""
    w, px = _panel()
    gross, turnover = _gross_turnover(w, px)
    live = turnover > 0.0
    assert live.any()
    nets = [eng.daily_net_returns(w, px, slippage_bp=float(s), backend="cpu") for s in (0, 5, 10, 20, 40)]
    for lo, hi in itertools.pairwise(nets):
        assert (lo >= hi).all()  # 全域非增
        assert (lo[live] > hi[live]).all()  # 换手日严格递减


def test_r5_zero_slippage_floor_is_commission_plus_stamp():
    """零滑点档=佣金双边+印花单腿地板（成本仍>0，禁把 0 档当零成本）。"""
    w, px = _panel()
    gross, turnover = _gross_turnover(w, px)
    net0 = eng.daily_net_returns(w, px, slippage_bp=0.0, backend="cpu")
    expect = gross - turnover * (eng.COMMISSION_BP * 2 + eng.STAMP_BP) / 10000.0
    pd.testing.assert_series_equal(net0, expect)
    assert (net0 < gross).any()  # 地板成本真实扣减


# ---------- R6/R7 成本发生面与换手口径 ----------


def test_r6_constant_weight_days_bear_no_cost():
    """恒仓日（turnover=0）净=毛逐位（无换手无成本——成本只随换手发生）。"""
    w, px = _panel()
    gross, turnover = _gross_turnover(w, px)
    net = eng.daily_net_returns(w, px, slippage_bp=40.0, backend="cpu")
    flat = turnover == 0.0
    assert flat.any()
    assert np.allclose(net[flat].to_numpy(), gross[flat].to_numpy(), rtol=0.0, atol=0.0)


def test_r7_turnover_is_one_sided_half_abs_delta():
    """换手=|Δw|/2 单边口径：单日 0→1 全建仓 turnover=0.5，成本=半名义×round-trip。"""
    idx = pd.date_range("2026-01-05", periods=5, freq="B")
    px = pd.DataFrame(100.0, index=idx, columns=["000997"])
    w = pd.DataFrame(0.0, index=idx, columns=["000997"])
    w.iloc[2:] = 1.0
    gross, turnover = _gross_turnover(w, px)
    assert float(turnover.iloc[2]) == pytest.approx(0.5)
    slip = 8.0
    net = eng.daily_net_returns(w, px, slippage_bp=slip, backend="cpu")
    expect_cost = turnover * (eng.COMMISSION_BP * 2 + eng.STAMP_BP + slip * 2) / 10000.0
    assert np.allclose((gross - net).to_numpy(), expect_cost.to_numpy(), rtol=1e-12)


# ---------- R8/R9/R10 env 选档零漂移与 fail-closed ----------


def test_r8_env_unset_matches_verbatim_bitwise(monkeypatch):
    monkeypatch.delenv(_ENV_KEY, raising=False)
    w, px = _panel(seed=23)
    base = eng.daily_net_returns(w, px, backend="cpu")
    gross, turnover = _gross_turnover(w, px)
    expect = gross - turnover * (eng.COMMISSION_BP * 2 + eng.STAMP_BP + eng.SLIPPAGE_BP * 2) / 10000.0
    pd.testing.assert_series_equal(base, expect)


def test_r9_env_legacy_bit_identical_to_unset(monkeypatch):
    w, px = _panel(seed=23)
    monkeypatch.delenv(_ENV_KEY, raising=False)
    base = eng.daily_net_returns(w, px, backend="cpu")
    monkeypatch.setenv(_ENV_KEY, "legacy")
    legacy = eng.daily_net_returns(w, px, backend="cpu")
    pd.testing.assert_series_equal(base, legacy)


def test_r10_unknown_env_tier_fails_closed_at_engine_seam(monkeypatch):
    """未知档在引擎面 fail-closed（禁静默回落 legacy=禁伪造口径红线）。"""
    monkeypatch.setenv(_ENV_KEY, "participation")
    w, px = _panel(seed=23)
    with pytest.raises(RuntimeError) as ei:
        eng.daily_net_returns(w, px, backend="cpu")
    assert _ENV_KEY in str(ei.value)


# ---------- R11/R12 可插拔注入点 ----------


def test_r11_injected_model_scalar_threads_through_public_api(monkeypatch):
    """注入档经公共 API 全程标量透传（引擎成本式形状不变红线）。"""
    monkeypatch.delenv(_ENV_KEY, raising=False)
    w, px = _panel(seed=31)
    gross, turnover = _gross_turnover(w, px)
    kappa = 33.0

    class _FlatTier:
        def round_trip_bps(self, slippage_bp: float | None = None) -> float:
            return kappa

    net = eng._net_line(gross, turnover, 5.0, cost_model=_FlatTier())
    pd.testing.assert_series_equal(net, gross - turnover * kappa / 10000.0)


@pytest.mark.xfail(
    strict=False,
    reason="标定档（calibrated）原件语义不可考——fail-closed 重建件下本红证仅占位；原件恢复/裁定重建后应转正为五分位 ADV 单调红证",
)
def test_r12_calibrated_tier_quantile_monotonicity_placeholder(monkeypatch):
    """xpass 钉：占位红证在现行 fail-closed 重建面即通过（未知档必抛=无伪标定可溜入）。"""
    monkeypatch.setenv(_ENV_KEY, "calibrated")
    with pytest.raises(RuntimeError):
        eng._cost_model_adapter().resolve_from_env()
