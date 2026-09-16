# [A_test] module_id: MOD-TEST-SYNTH-VIX-IV | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4.9 Phase2c
# [MODULE] tests.regime.test_synthetic_vix_iv_path
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.synthetic_vix; pandas; numpy
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] tests/regime/test_synthetic_vix_iv_path.py
# [INVARIANTS] 输入 iv=小数/输出 VIX=百分数(×100)；双标的 50ETF+300ETF 取均值、单标的降级；ATM 边界 |abs(delta)-0.5|<0.15 严格小于（0.15 本身被排除）；无可插值到期日→退化为可用 IV 均值；数据缺失→空 Series 不抛；vix_pct∈[0,1]
# [A_module] module_id: MOD-TEST-SYNTH-VIX-IV | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-002 #10_regime_detector_spec §4.9 #Phase2c #SVX-2 #SVX-1
"""test_synthetic_vix_iv_path.py — 合成 VIX **期权 IV 主路径**（MOD-REGIME-002 Phase 2c）单元测试。

兄弟文件 tests/regime/test_synthetic_vix.py 只覆盖 P0 后备路径 synthetic_vix_pct；
本文件补齐主路径 compute_synthetic_vix / vix_pct_from_vix 的 8 项空白：

  ① 30 天线性插值数值正确性（手算期望值，非 self-consistent）
  ② 单标的缺失降级（只 510050 / 只 510300）
  ③ 双标的均值口径 + 部分覆盖日（skipna）
  ④ ATM 筛选边界：源码用严格 `<`，故 |abs(delta)-0.5| 恰为 0.15 的行被排除
  ⑤ 无可插值到期日（单一 DTE / 两个 DTE 同侧）→ 退化为可用侧 IV 均值
  ⑥ 全空输入（None / 空表 / 全非 ATM / iv 全 NaN / 空 vix）→ 空 Series 且不抛
  ⑦ vix_pct_from_vix 值域 [0,1] 与 warmup 期 NaN（含 rank 端点精确值）
  ⑧ IV 量纲回归：输入必须是**小数**（0.20）、输出是**百分数**（20.0）
  ＋ PIT 粗检（截断输入与全量前缀严格相等）＋ 零 delta 曲面的 fail-closed 显式降级

量纲判定依据（⑧）：本模块头 §CBOE 简化公式第 4 步 "VIX = σ_30 × 100（百分数）"，
且唯一进料口 src/zephyr/data/implementations/miniqmt_provider.py::_solve_iv 用
Black-Scholes + Newton-Raphson（初值 σ=0.3）反解 → 落库 iv 为小数波动率；
故 c1_market.option_iv_surface.iv=0.20 ↔ VIX=20.0（A 股 ATM IV 常态 15%~25%）。

依据: 10_regime_detector_spec v1.3.1 §4.9 / Phase 2c 计划 §任务4
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features.synthetic_vix import compute_synthetic_vix, vix_pct_from_vix

# ---------------------------------------------------------------------------
# 测试数据构造（MultiIndex(trade_date, underlying)，列含 strike/expiry/iv/option_type/delta/vega）
# ---------------------------------------------------------------------------

Record = tuple[str, str, str, float, float, str]  # date, underlying, expiry, iv, delta, opt_type


def _surface(records: list[Record]) -> pd.DataFrame:
    """紧凑记录 → 生产形态的 IV 曲面 DataFrame（MultiIndex(trade_date, underlying)）。"""
    df = pd.DataFrame(
        {
            "trade_date": pd.to_datetime([r[0] for r in records]),
            "underlying": [r[1] for r in records],
            "expiry": [r[2] for r in records],
            "iv": [r[3] for r in records],
            "delta": [r[4] for r in records],
            "option_type": [r[5] for r in records],
            "strike": [2.5] * len(records),
            "vega": [0.05] * len(records),
        }
    )
    return df.set_index(["trade_date", "underlying"]).sort_index()


def _interp_expected(iv_near: float, iv_far: float, t1: int, t2: int, target: int = 30) -> float:
    """手算真值：σ_30 = iv1 + (iv2-iv1)×(30-t1)/(t2-t1)，再 ×100 转百分数。"""
    return (iv_near + (iv_far - iv_near) * (target - t1) / (t2 - t1)) * 100


class TestInterpolationTo30Days:
    """① 已知 iv/delta/dte → 30 天线性插值数值正确（期望值手算写进断言）。"""

    def test_two_leg_interp_matches_hand_computation(self) -> None:
        """DTE 18/46、near IV 均值 0.22、far IV 均值 0.32 → σ30=0.26285714…→ VIX 26.285714…

        手算：0.22 + (0.32-0.22)×(30-18)/(46-18) = 0.22 + 0.10×12/28 = 0.262857142857…
        """
        df = _surface(
            [
                ("2024-06-03", "510050", "2024-06-21", 0.20, 0.55, "call"),  # near dte=18
                ("2024-06-03", "510050", "2024-06-21", 0.24, -0.45, "put"),  # near dte=18
                ("2024-06-03", "510050", "2024-07-19", 0.30, 0.50, "call"),  # far dte=46
                ("2024-06-03", "510050", "2024-07-19", 0.34, -0.50, "put"),  # far dte=46
            ]
        )
        vix = compute_synthetic_vix(df)
        expected = _interp_expected(0.22, 0.32, 18, 46)
        assert expected == pytest.approx(26.285714285714285, rel=1e-12)  # 手算复核真值本身
        assert len(vix) == 1
        assert vix.iloc[0] == pytest.approx(expected, rel=1e-12)
        assert vix.name == "vix"
        assert vix.index[0] == pd.Timestamp("2024-06-03")

    def test_symmetric_midpoint_gives_exact_arithmetic_mean(self) -> None:
        """DTE 20/40 → 30 天恰为二者中点 → σ30 = (0.20+0.30)/2 = 0.25 → VIX=25.0（整值）。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-06-21", 0.20, 0.50, "call"),  # dte=20
                ("2024-06-01", "510050", "2024-07-11", 0.30, 0.50, "call"),  # dte=40
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(25.0, rel=1e-12)

    def test_dte_bucket_split_at_30_is_inclusive_for_near(self) -> None:
        """DTE≤30 归近月：t1=30 → 权重 (30-30)/(40-30)=0 → 结果=iv_near（近月被完全取用）。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.18, 0.50, "call"),  # dte=30 → near
                ("2024-06-01", "510050", "2024-07-11", 0.40, 0.50, "call"),  # dte=40 → far
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(18.0, rel=1e-12)

    def test_call_and_put_both_enter_atm_mean(self):
        """call+put 同侧 IV 取均值（源码按 ATM 池整体 mean，put 用 abs(delta) 归 ATM）。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-06-11", 0.20, 0.52, "call"),  # dte=10
                ("2024-06-01", "510050", "2024-06-11", 0.26, -0.48, "put"),  # dte=10
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(23.0, rel=1e-12)  # mean(0.20,0.26)=0.23 ×100


class TestSingleUnderlyingDegradation:
    """② 单标的缺失 → 用可用标的，不报错、不缩放。"""

    def test_only_510050_present(self) -> None:
        """只有 50ETF：输出即 50ETF 单标的 VIX（dte=30 无远月 → 退化用近月 IV）。"""
        df = _surface([("2024-06-01", "510050", "2024-07-01", 0.20, 0.50, "call")])
        vix = compute_synthetic_vix(df)
        assert len(vix) == 1
        assert vix.iloc[0] == pytest.approx(20.0, rel=1e-12)

    def test_only_300etf_present(self) -> None:
        """只有 300ETF：与只 50ETF 对称（均值口径不因标的身份改变）。"""
        df = _surface([("2024-06-01", "510300", "2024-07-01", 0.20, 0.50, "call")])
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(20.0, rel=1e-12)

    def test_single_underlying_full_interp_not_halved(self) -> None:
        """单标的走 `vix_list[0] * 100` 分支：插值结果不得被均值口径二次缩放。"""
        df = _surface(
            [
                ("2024-06-03", "510300", "2024-06-21", 0.22, 0.50, "call"),
                ("2024-06-03", "510300", "2024-07-19", 0.32, 0.50, "call"),
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(_interp_expected(0.22, 0.32, 18, 46), rel=1e-12)

    def test_one_underlying_drops_out_when_all_its_dates_are_nan(self) -> None:
        """某标的 ATM 行 iv 全 NaN → 该标的被剔除（`if not vix.empty`），存活标的单独输出。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.20, 0.50, "call"),
                ("2024-06-01", "510300", "2024-07-01", np.nan, 0.50, "call"),
            ]
        )
        vix = compute_synthetic_vix(df)
        assert len(vix) == 1
        assert vix.iloc[0] == pytest.approx(20.0, rel=1e-12)


class TestDualUnderlyingMean:
    """③ 双标的取均值 VIX = (VIX_50 + VIX_300)/2。"""

    def test_mean_of_two_underlyings(self) -> None:
        """50ETF=20 / 300ETF=30 → 均值 25（源码 concat().mean(axis=1)×100）。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.20, 0.50, "call"),
                ("2024-06-01", "510300", "2024-07-01", 0.30, 0.50, "call"),
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(25.0, rel=1e-12)

    def test_vix_space_mean_equals_iv_space_mean_by_linearity(self) -> None:
        """两标的期限结构斜率不同，仍与"先在 IV 空间取均值再插值"完全相等。

        数学依据：近月/次月线性插值 σ30 = iv1 + (iv2-iv1)·w 对 (iv1, iv2) 是线性算子，
        均值亦是线性算子 → 两者可交换；×100 只是纯尺度变换，不破坏等价。
        本用例把"均值口径放在 VIX 空间"钉成可核对的代数事实（若日后引入
        方差加权/VIX 非线性合成，此等式会首先破红）。
        """
        df = _surface(
            [
                ("2024-06-03", "510050", "2024-06-21", 0.20, 0.50, "call"),
                ("2024-06-03", "510050", "2024-07-19", 0.20, 0.50, "call"),
                ("2024-06-03", "510300", "2024-06-21", 0.10, 0.50, "call"),
                ("2024-06-03", "510300", "2024-07-19", 0.40, 0.50, "call"),
            ]
        )
        vix = compute_synthetic_vix(df)
        per_underlying = (20.0 + _interp_expected(0.10, 0.40, 18, 46)) / 2
        iv_space_first = _interp_expected((0.20 + 0.10) / 2, (0.20 + 0.40) / 2, 18, 46)
        assert vix.iloc[0] == pytest.approx(per_underlying, rel=1e-12)
        assert vix.iloc[0] == pytest.approx(iv_space_first, rel=1e-12)  # 线性 ⇒ 两序等价

    def test_partial_coverage_day_falls_back_to_available_underlying(self) -> None:
        """部分覆盖日：某日只有 50ETF → 该日=50ETF 值（mean(axis=1) skipna=True），非 NaN。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.20, 0.50, "call"),
                ("2024-06-01", "510300", "2024-07-01", 0.30, 0.50, "call"),
                ("2024-06-02", "510050", "2024-07-02", 0.20, 0.50, "call"),  # 该日无 300ETF
            ]
        )
        vix = compute_synthetic_vix(df).sort_index()
        assert vix.iloc[0] == pytest.approx(25.0, rel=1e-12)
        assert vix.iloc[1] == pytest.approx(20.0, rel=1e-12)
        assert vix.notna().all()

    def test_three_underlyings_averaged_equally(self) -> None:
        """非双标的（第三个标的混入）→ 等权算术均值（当前无权重口径，钉住现状）。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.10, 0.50, "call"),
                ("2024-06-01", "510300", "2024-07-01", 0.20, 0.50, "call"),
                ("2024-06-01", "588000", "2024-07-01", 0.30, 0.50, "call"),
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(20.0, rel=1e-12)  # mean(10,20,30)


class TestAtmFilterBoundary:
    """④ ATM 边界：源码 `(df["delta_abs"] - 0.5).abs() < 0.15` 用严格 `<` → 0.15 被排除。"""

    def test_boundary_delta_excluded_strict_less_than(self) -> None:
        """|abs(delta)-0.5| 恰为 0.15（delta=0.65 / 0.35 / -0.65）不入选 ATM 池。

        浮点事实核对：0.65-0.5=0.15000000000000002、abs(0.35-0.5)=0.15000000000000002 → 均 > 0.15。
        """
        assert 0.65 - 0.5 > 0.15  # 边界行在 float 语义下确实落在 `<` 之外
        assert abs(0.35 - 0.5) > 0.15
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.20, 0.64, "call"),  # 入选（0.14）
                ("2024-06-01", "510050", "2024-07-01", 0.30, -0.64, "put"),  # 入选（abs→0.14）
                ("2024-06-01", "510050", "2024-07-01", 0.90, 0.65, "call"),  # 边界 0.15 → 排除
                ("2024-06-01", "510050", "2024-07-01", 0.99, 0.35, "call"),  # 边界 0.15 → 排除
                ("2024-06-01", "510050", "2024-07-01", 0.10, 0.20, "call"),  # 深 OTM → 排除
            ]
        )
        vix = compute_synthetic_vix(df)
        # 只有 iv=0.20/0.30 两行入池 → mean=0.25 → 25.0；若边界被含入则≈59.75，可判别
        assert vix.iloc[0] == pytest.approx(25.0, rel=1e-12)

    def test_put_negative_delta_uses_abs_so_atm_put_included(self) -> None:
        """put delta=-0.5 经 abs 后与 call 同归 ATM（源码用 delta.abs()，非直接比 0.5）。"""
        df = _surface([("2024-06-01", "510050", "2024-07-01", 0.20, -0.50, "put")])
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(20.0, rel=1e-12)

    def test_delta_abs_exactly_one_or_zero_filtered(self) -> None:
        """|delta|=1（深 ITM）与 |delta|=0（深 OTM）被排除；全排除 → 空 Series。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.20, 1.00, "call"),
                ("2024-06-01", "510050", "2024-07-01", 0.30, 0.00, "put"),
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.empty
        assert vix.name == "vix"

    def test_sign_symmetry_between_call_and_put_at_same_moneyness(self) -> None:
        """同 |delta| 的 call/put 入池后均值对称（0.20/0.20 → 20.0）。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.20, 0.60, "call"),
                ("2024-06-01", "510050", "2024-07-01", 0.20, -0.60, "put"),
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(20.0, rel=1e-12)


class TestNoInterpolableExpiry:
    """⑤ 无可插值到期日 → 行为与源码一致（退化用可用侧 IV/均值，不做外推）。"""

    def test_only_far_expiry_returns_far_iv(self) -> None:
        """唯一 DTE=45 > 30 → iv_near=NaN → 直接返回 far IV（28.0），无外推。"""
        df = _surface([("2024-06-01", "510050", "2024-07-16", 0.28, 0.50, "call")])
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(28.0, rel=1e-12)

    def test_only_near_expiry_returns_near_iv(self) -> None:
        """唯一 DTE=10 ≤ 30 → 直接返回 near IV（20.0），不外推到 30 天。"""
        df = _surface([("2024-06-01", "510050", "2024-06-11", 0.20, 0.50, "call")])
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(20.0, rel=1e-12)

    def test_two_expiries_both_below_30_use_mean(self) -> None:
        """两个 DTE 同侧（10/25 均 ≤30）→ far=NaN → 用近月池**均值**（0.25→25.0）。

        钉住源码语义：不是取"最接近 30 天"的那档，而是跨档 mean（同侧多档会稀释期限结构）。
        """
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-06-11", 0.20, 0.50, "call"),  # dte=10
                ("2024-06-01", "510050", "2024-06-26", 0.30, 0.50, "call"),  # dte=25
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(25.0, rel=1e-12)

    def test_two_expiries_both_above_30_use_mean(self) -> None:
        """两个 DTE 同侧（40/60 均 >30）→ 用远月池均值（0.30→30.0）。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-11", 0.20, 0.50, "call"),  # dte=40
                ("2024-06-01", "510050", "2024-07-31", 0.40, 0.50, "call"),  # dte=60
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(30.0, rel=1e-12)

    def test_already_expired_contract_is_counted_as_near(self) -> None:
        """负 DTE（到期日早于 trade_date 的陈旧行）未过滤：dte<0 落进近月池参与均值。

        钉住现状 = 进料口需自带卫生（quality_flag=1 不含已退市合约）；
        0.20(dte=30) 与 0.60(dte=-2) → mean 0.40 → 40.0。
        """
        df = _surface(
            [
                ("2024-06-03", "510050", "2024-07-03", 0.20, 0.50, "call"),  # dte=30
                ("2024-06-03", "510050", "2024-06-01", 0.60, 0.50, "call"),  # dte=-2 陈旧
            ]
        )
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(40.0, rel=1e-12)

    def test_date_with_only_nan_iv_dropped_from_output(self) -> None:
        """某日全部 ATM 行 iv=NaN → 该日 NaN 被 dropna，不留空洞、不抛。"""
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.20, 0.50, "call"),
                ("2024-06-02", "510050", "2024-07-02", np.nan, 0.50, "call"),
            ]
        )
        vix = compute_synthetic_vix(df)
        assert list(vix.index) == [pd.Timestamp("2024-06-01")]
        assert vix.iloc[0] == pytest.approx(20.0, rel=1e-12)


class TestEmptyInputs:
    """⑥ 全空输入 → 空 Series 且不抛（调用方按 INVARIANTS 回退 vol_pct）。"""

    def test_none_returns_empty_series(self) -> None:
        out = compute_synthetic_vix(None)
        assert isinstance(out, pd.Series)
        assert out.empty
        assert out.name == "vix"

    def test_empty_dataframe_returns_empty_series(self) -> None:
        out = compute_synthetic_vix(pd.DataFrame())
        assert out.empty and out.name == "vix"

    def test_zero_row_surface_keeps_columns_but_returns_empty(self) -> None:
        """列齐全但 0 行 → 走 `option_iv_df.empty` 分支（不触发 KeyError）。"""
        df = _surface([("2024-06-01", "510050", "2024-07-01", 0.20, 0.50, "call")]).iloc[0:0]
        out = compute_synthetic_vix(df)
        assert out.empty and out.name == "vix"

    def test_all_rows_outside_atm_returns_empty(self) -> None:
        """全部非 ATM（delta 极端）→ atm.empty 分支 → 空 Series。"""
        df = _surface([("2024-06-01", "510050", "2024-07-01", 0.20, 0.95, "call")])
        out = compute_synthetic_vix(df)
        assert out.empty and out.name == "vix"

    def test_all_nan_iv_returns_empty_not_raise(self) -> None:
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", np.nan, 0.50, "call"),
                ("2024-06-01", "510300", "2024-07-01", np.nan, 0.50, "call"),
            ]
        )
        out = compute_synthetic_vix(df)
        assert out.empty and out.name == "vix"

    def test_vix_pct_from_empty_vix_returns_empty_series(self) -> None:
        for empty in (compute_synthetic_vix(None), pd.Series(dtype=float, name="vix")):
            pct = vix_pct_from_vix(empty)
            assert pct.empty and pct.name == "vix_pct"

    def test_missing_delta_column_raises_keyerror_by_contract(self) -> None:
        """契约：曲面必须带 delta 列。缺列 → KeyError（调用方 try/except 已兜底降级）。

        SVX-1-P0 治本后（2026-09-16）：唯一写入方
        miniqmt_provider._fetch_option_iv_surface 的 columns 清单已声明
        delta/gamma/theta/vega（此前未声明 → 被 BufferedWriter 列过滤丢弃 →
        落库恒为 DDL DEFAULT 0 → 主路径静默空降级），列缺失现由该清单守护。
        真库 2026-01-29~2026-09-16 存量 9653 行仍为 delta=0，待回灌，
        见 TestZeroDeltaSurfaceFailClosed 与
        tests/data/implementations/test_option_iv_surface_delta_feed.py。
        """
        df = _surface([("2024-06-01", "510050", "2024-07-01", 0.20, 0.50, "call")]).drop(columns=["delta"])
        with pytest.raises(KeyError):
            compute_synthetic_vix(df)


class TestVixPctFromVix:
    """⑦ vix_pct_from_vix 值域 [0,1] 与 warmup 期 NaN。"""

    @staticmethod
    def _vix(n: int = 300, start: float = 15.0, stop: float = 25.0) -> pd.Series:
        return pd.Series(np.linspace(start, stop, n), index=pd.bdate_range("2023-01-02", periods=n), name="vix")

    def test_range_within_unit_interval(self) -> None:
        pct = vix_pct_from_vix(self._vix())
        valid = pct.dropna()
        assert len(valid) > 0
        assert (valid >= 0).all() and (valid <= 1).all()
        assert pct.name == "vix_pct"

    def test_warmup_nan_count_exactly_window_minus_one(self) -> None:
        """rolling(250).rank 需满窗 → 前 249 个为 NaN，第 250 个起非 NaN。"""
        pct = vix_pct_from_vix(self._vix(), window=250)
        assert pct.iloc[:249].isna().all()
        assert pct.notna().sum() == 300 - 249
        assert pd.notna(pct.iloc[249])

    def test_rank_endpoints_on_monotone_series(self) -> None:
        """单调递增序列：满窗首日 rank=1/250，末日 rank=250/250=1.0（端点精确值）。"""
        pct = vix_pct_from_vix(self._vix(n=300), window=250)
        assert pct.iloc[249] == pytest.approx(1.0, rel=1e-12)
        assert pct.iloc[-1] == pytest.approx(1.0, rel=1e-12)

    def test_decreasing_series_sits_at_window_minimum_rank(self) -> None:
        """单调递减：每日都是窗内最小 → rank pct = 1/window（等权秩定义可核对）。"""
        vix = self._vix(n=260, start=25.0, stop=15.0)
        pct = vix_pct_from_vix(vix, window=5)
        tail = pct.dropna()
        assert tail.iloc[0] == pytest.approx(1 / 5, rel=1e-12)
        assert (tail <= 1).all() and (tail >= 0).all()

    def test_constant_vix_gives_uniform_rank(self) -> None:
        """恒定 VIX → 满窗后分位恒等（rank 平摊），且仍在 [0,1]。"""
        vix = pd.Series(np.full(260, 20.0), index=pd.bdate_range("2023-01-02", periods=260), name="vix")
        pct = vix_pct_from_vix(vix, window=50).dropna()
        assert pct.nunique() == 1
        assert 0.0 <= pct.iloc[0] <= 1.0

    def test_short_series_below_window_all_nan(self) -> None:
        """样本数 < window → 全 NaN（不满窗不出分位），但索引与长度保持。"""
        pct = vix_pct_from_vix(self._vix(n=100), window=250)
        assert pct.isna().all()
        assert len(pct) == 100

    def test_pit_no_future_leakage_in_pct(self) -> None:
        """PIT：截断后的分位与全量前缀逐点相等（rolling 只回看不前瞻）。"""
        vix = self._vix(n=300)
        full = vix_pct_from_vix(vix, window=250)
        head = vix.iloc[:260]
        trunc = vix_pct_from_vix(head, window=250)
        pd.testing.assert_series_equal(trunc, full.loc[head.index], check_names=True)


class TestIvDimensionRegression:
    """⑧ IV 量纲回归：输入小数 → 输出百分数（×100），不可双重缩放也不可漏缩放。"""

    def test_decimal_iv_produces_plausible_vix_level(self) -> None:
        """A 股期权 ATM IV 常态 15%~25%（小数 0.15~0.25）→ VIX 应落在 15~25 档位。"""
        df = _surface([("2024-06-01", "510050", "2024-07-01", 0.20, 0.50, "call")])
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(20.0, rel=1e-12)
        assert 15.0 <= vix.iloc[0] <= 25.0

    def test_percent_iv_is_inflated_100x_documents_contract(self) -> None:
        """反证量纲契约：若上游误传百分数 20.0 → 输出 2000.0（100× 虚高，可被下游阈值全灭）。

        判定依据：模块头 §CBOE 公式第 4 步 "VIX = σ_30 × 100（百分数）" + 进料口
        miniqmt_provider._solve_iv 以 σ=0.3 为初值做 BS 反解（小数量纲）。
        本用例把"输入=小数"钉成可执行契约，任何一侧改量纲都会红。
        """
        df = _surface([("2024-06-01", "510050", "2024-07-01", 20.0, 0.50, "call")])
        vix = compute_synthetic_vix(df)
        assert vix.iloc[0] == pytest.approx(2000.0, rel=1e-12)

    def test_scale_is_linear_in_iv(self) -> None:
        """线性性：IV 翻倍 → VIX 翻倍（×100 是纯尺度变换，不引入非线性）。"""
        base = _surface([("2024-06-01", "510050", "2024-07-01", 0.20, 0.50, "call")])
        doubled = _surface([("2024-06-01", "510050", "2024-07-01", 0.40, 0.50, "call")])
        assert compute_synthetic_vix(doubled).iloc[0] == pytest.approx(
            2 * compute_synthetic_vix(base).iloc[0], rel=1e-12
        )

    def test_pct_of_pct_would_double_scale_guard(self) -> None:
        """端到端量纲：compute_synthetic_vix→vix_pct_from_vix 只出分位，不再乘 100。"""
        vix = compute_synthetic_vix(
            _surface([("2024-06-01", "510050", "2024-07-01", 0.20, 0.50, "call")])
        )
        assert vix.max() < 100  # VIX 档位 <100，若被二次 ×100 则必然 >100
        pct = vix_pct_from_vix(vix, window=1)
        assert pct.dropna().between(0, 1).all()


class TestZeroDeltaSurfaceFailClosed:
    """零 delta 曲面 fail-closed（SVX-1-P0 治本后语义）：仍不产出，但**必须出声**。

    治本前：delta 恒 0 是**生产形态**（进料口未声明该列），主路径静默零产出半年。
    治本后：进料口按 BS 真源落 delta；库内 2026-01-29~2026-09-16 的 9653 存量行
    仍是 delta=0（待回灌），故零 delta 输入必须 fail-closed——不猜 ATM、不静默降级。
    """

    def test_all_zero_delta_yields_empty_vix_but_warns(self, caplog) -> None:
        """delta 全 0 → |0-0.5|=0.5 → 全被排除 → 空 Series；且 WARNING 点名 delta。

        本用例不是"期望行为"的美化版：它同时钉住两件事——
        ① 不产出（宁可回退后备路径，也不用 0 delta 猜 ATM 池）；
        ② 非静默（降级必须能被日志发现，禁静默零值）。
        """
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.20, 0.0, "call"),
                ("2024-06-01", "510300", "2024-07-01", 0.30, 0.0, "put"),
            ]
        )
        with caplog.at_level(logging.WARNING):
            out = compute_synthetic_vix(df)
        assert out.empty
        msgs = " | ".join(r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING)
        assert "delta" in msgs, f"零产出未点名可疑字段：{msgs}"

    def test_all_zero_delta_end_to_end_pct_is_empty(self) -> None:
        df = _surface([("2024-06-01", "510050", "2024-07-01", 0.20, 0.0, "call")])
        pct = vix_pct_from_vix(compute_synthetic_vix(df))
        assert pct.empty
        assert pct.name == "vix_pct"

    def test_same_surface_with_real_delta_now_produces(self) -> None:
        """治本对照：同一天、同 IV，delta 换成进料口真值（BS ATM 0.53/-0.47）→ 出数。

        与上一用例构成"唯一变量是 delta"的对照，锁住进料口补 delta 的因果。
        """
        df = _surface(
            [
                ("2024-06-01", "510050", "2024-07-01", 0.20, 0.53, "call"),
                ("2024-06-01", "510300", "2024-07-01", 0.30, -0.47, "put"),
            ]
        )
        vix = compute_synthetic_vix(df)
        assert not vix.empty
        assert vix.iloc[0] == pytest.approx(25.0, rel=1e-12)  # mean(0.20,0.30)×100
        assert vix_pct_from_vix(vix, window=1).iloc[0] == pytest.approx(1.0, rel=1e-12)


class TestChainIntegrationAndPit:
    """多日曲面 → VIX → vix_pct 全链路 + PIT 截断一致性。"""

    @staticmethod
    def _multi_day_surface(n_dates: int = 300, seed: int = 7) -> pd.DataFrame:
        """每日双标的、近月 dte=18 / 次月 dte=46，IV 在 0.15~0.28 随机游走。"""
        dates = pd.bdate_range("2023-01-02", periods=n_dates)
        rng = np.random.default_rng(seed)
        records: list[Record] = []
        for i, d in enumerate(dates):
            base = 0.18 + 0.05 * np.sin(i / 21.0) + 0.01 * rng.standard_normal()
            stamp = d.strftime("%Y-%m-%d")
            for underlying in ("510050", "510300"):
                near = (d + pd.Timedelta(days=18)).strftime("%Y-%m-%d")
                far = (d + pd.Timedelta(days=46)).strftime("%Y-%m-%d")
                skew = 0.02 if underlying == "510300" else 0.0
                records.append((stamp, underlying, near, base + skew, 0.52, "call"))
                records.append((stamp, underlying, near, base + skew + 0.02, -0.47, "put"))
                records.append((stamp, underlying, far, base + skew + 0.01, 0.50, "call"))
                records.append((stamp, underlying, far, base + skew + 0.03, -0.50, "put"))
                records.append((stamp, underlying, near, 0.90, 0.80, "call"))  # 非 ATM 噪声行
        return _surface(records)

    def test_vix_level_in_expected_band(self) -> None:
        """全链路 VIX 档位落在 [10, 40]（IV 0.15~0.28 → 百分数），无 100×/0.01× 漂移。"""
        vix = compute_synthetic_vix(self._multi_day_surface())
        assert len(vix) == 300
        assert vix.between(10.0, 40.0).all()

    def test_pct_output_in_unit_interval_with_warmup(self) -> None:
        vix = compute_synthetic_vix(self._multi_day_surface())
        pct = vix_pct_from_vix(vix, window=250)
        assert pct.iloc[:249].isna().all()
        assert pct.dropna().between(0.0, 1.0).all()

    def test_pit_truncated_input_matches_full_prefix(self) -> None:
        """PIT：只用前 120 日输入计算的 VIX 与全量前缀逐点相等（无未来信息回流）。"""
        df = self._multi_day_surface()
        full = compute_synthetic_vix(df)
        cutoff = full.index[119]
        head = df[df.index.get_level_values("trade_date") <= cutoff]
        trunc = compute_synthetic_vix(head)
        pd.testing.assert_series_equal(trunc, full.loc[:cutoff], check_names=True)

    def test_extra_non_atm_noise_rows_do_not_move_result(self) -> None:
        """非 ATM 噪声行被筛除后，与不含噪声行的曲面结果完全一致（ATM 筛选有效性）。"""
        df = self._multi_day_surface(n_dates=20)
        clean = df[np.abs(df["delta"].abs() - 0.5) < 0.15]
        pd.testing.assert_series_equal(
            compute_synthetic_vix(df), compute_synthetic_vix(clean), check_names=True
        )

    def test_index_is_trade_date_sorted(self) -> None:
        vix = compute_synthetic_vix(self._multi_day_surface(n_dates=50))
        assert vix.index.is_monotonic_increasing
        assert isinstance(vix.index, pd.DatetimeIndex)
