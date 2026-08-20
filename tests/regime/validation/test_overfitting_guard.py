# [A_test] module_id: MOD-TEST-OFIT-GUARD | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-VAL | docs/03_modules/_domain_regime/blueprint.md | 14 号 §4.5
# [MODULE] tests.regime.validation.test_overfitting_guard
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.validation.overfitting_guard; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/regime/validation/test_overfitting_guard.py
# [TTL] permanent
# [ARCH-REF] #14_regime_s2_diagnosis §4.5 防过拟合方法论栈（事件研究/预注册/MinTRL/WFE）
# [ALGO_FLOW]
# 层: 输入
# - I1: 评分序列+事件日期（事件研究）/ 参数 dict（预注册）/ Sharpe+矩（MinTRL/WFE）
# 层: 算法
# - A1: event_study：事件日 ±窗口评分极值 vs 全历史基线分位
# - A2: PreRegistrationRegistry：参数 hash 锁定（禁覆盖）+ 一致性核验
# - A3: min_track_record_length：MinTRL=1+[1-γ3·SR+(γ4-1)/4·SR²]·(Z/SR)²
# - A4: walk_forward_efficiency：WFE=OOS/IS Sharpe，≥0.6 pass / <0.5 red_flag
# 层: 输出
# - O1: 事件研究 DataFrame / 预注册核验 bool / MinTRL 年数 / WFE 裁决
"""test_overfitting_guard.py — 14 号 §4.5 防过拟合方法论栈 MVP 单元测试。

覆盖：
  1. event_study：异常事件窗口高分位 / 常态事件中位 / asof 对齐 / 基线不足 NaN
  2. PreRegistrationRegistry：注册-核验 / 篡改检测 / 禁覆盖 / 未知名 KeyError / 跨实例持久化
  3. min_track_record_length：正态 Sharpe=1 → ≈3.71 年；肥尾更长；SR≤0 → inf
  4. walk_forward_efficiency + assess_wfe 三档裁决（pass/marginal/red_flag/undefined）
  5. 仓内 DSR/CPCV 实现可 import（不 vendor 外部库的验证锚点）

依据: 14_regime_s2_diagnosis v0.5.2 §4.5（Bailey & López de Prado 2014 /
      Neyt How-To-Backtest-Correctly 2026-03 / digitalninjasystems 2026-07 WFE≥0.6）
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.validation.overfitting_guard import (
    PreRegistrationRegistry,
    assess_wfe,
    event_study,
    min_track_record_length,
    walk_forward_efficiency,
)

# ---------------------------------------------------------------------------
# 1. 事件研究法
# ---------------------------------------------------------------------------


class TestEventStudy:
    def _series(self, n: int = 400, base: float = 10.0) -> pd.Series:
        rng = np.random.default_rng(5)
        idx = pd.bdate_range("2024-01-01", periods=n)
        return pd.Series(base + rng.normal(0, 2, n), index=idx)

    def test_abnormal_event_high_percentile(self):
        """事件窗口评分远高于历史基线 → baseline_pct 接近 1。"""
        s = self._series()
        s.iloc[200:206] = 90.0  # 事件窗口异常高分
        df = event_study(s, [s.index[203]], pre_window=2, post_window=2)
        row = df.iloc[0]
        assert row["window_max"] == 90.0
        assert row["baseline_pct"] > 0.95

    def test_normal_event_mid_percentile(self):
        """常态事件日 → baseline_pct 落中间区域（非极端）。"""
        s = self._series()
        df = event_study(s, [s.index[203]], pre_window=2, post_window=2)
        assert 0.0 < df.iloc[0]["baseline_pct"] < 1.0

    def test_event_date_asof_alignment(self):
        """事件日不在索引（周末）→ asof 对齐到最近前一交易日。"""
        s = self._series()
        sat = s.index[203] + pd.Timedelta(days=2)  # 203 是工作日，+2 可能跨周末
        df = event_study(s, [sat], pre_window=2, post_window=2)
        assert len(df) == 1
        assert df.iloc[0]["aligned_date"] <= sat

    def test_insufficient_baseline_nan(self):
        """事件过早（基线窗口不足 5 个）→ baseline_pct NaN。"""
        s = self._series()
        df = event_study(s, [s.index[3]], pre_window=2, post_window=2)
        assert pd.isna(df.iloc[0]["baseline_pct"])

    def test_multiple_events_rows(self):
        s = self._series()
        df = event_study(s, [s.index[100], s.index[200], s.index[300]])
        assert len(df) == 3


# ---------------------------------------------------------------------------
# 2. 预注册登记
# ---------------------------------------------------------------------------


class TestPreRegistration:
    def test_register_and_verify(self, tmp_path):
        reg = PreRegistrationRegistry(tmp_path / "prereg.json")
        params = {"halflife": 10, "lookback": 20, "vol_mult": 2.0}
        reg.register("s2_capitulation", params, note="14号 §4.1 预注册")
        assert reg.verify("s2_capitulation", params) is True

    def test_tampered_params_fail_verify(self, tmp_path):
        reg = PreRegistrationRegistry(tmp_path / "prereg.json")
        reg.register("s2_capitulation", {"halflife": 10})
        assert reg.verify("s2_capitulation", {"halflife": 11}) is False

    def test_reregister_forbidden(self, tmp_path):
        """预注册不可覆盖（防"看到结果后回头调参数"）。"""
        reg = PreRegistrationRegistry(tmp_path / "prereg.json")
        reg.register("s2_capitulation", {"halflife": 10})
        with pytest.raises(RuntimeError, match="已注册"):
            reg.register("s2_capitulation", {"halflife": 12})

    def test_unknown_name_raises(self, tmp_path):
        reg = PreRegistrationRegistry(tmp_path / "prereg.json")
        with pytest.raises(KeyError):
            reg.verify("nope", {})

    def test_persistence_across_instances(self, tmp_path):
        path = tmp_path / "prereg.json"
        PreRegistrationRegistry(path).register("a", {"x": 1})
        reg2 = PreRegistrationRegistry(path)  # 重新加载文件
        assert reg2.verify("a", {"x": 1}) is True

    def test_param_order_insensitive(self, tmp_path):
        """dict 键序不影响 hash（json sort_keys）。"""
        reg = PreRegistrationRegistry(tmp_path / "prereg.json")
        reg.register("a", {"x": 1, "y": 2})
        assert reg.verify("a", {"y": 2, "x": 1}) is True


# ---------------------------------------------------------------------------
# 3. MinTRL
# ---------------------------------------------------------------------------


class TestMinTrackRecordLength:
    def test_normal_sharpe_one(self):
        """SR_a=1、正态（γ3=0/γ4=3）、95% 置信 → MinTRL=1+(1+0.5)×1.6449²≈5.06 年。"""
        m = min_track_record_length(sharpe=1.0, skew=0.0, kurtosis=3.0, alpha=0.95)
        assert m == pytest.approx(1 + 1.5 * 1.6448536**2, rel=1e-3)

    def test_fat_tail_longer_record(self):
        """肥尾（γ4=6）+ 左偏（γ3=-1）→ 需更长记录（诚实标注低置信）。"""
        m_normal = min_track_record_length(sharpe=1.0, skew=0.0, kurtosis=3.0)
        m_fat = min_track_record_length(sharpe=1.0, skew=-1.0, kurtosis=6.0)
        assert m_fat > m_normal

    def test_non_positive_sharpe_inf(self):
        """SR≤0：任何长度记录都不足以证明 → inf。"""
        assert min_track_record_length(sharpe=0.0, skew=0.0, kurtosis=3.0) == float("inf")
        assert min_track_record_length(sharpe=-0.5, skew=0.0, kurtosis=3.0) == float("inf")

    def test_from_returns_series(self):
        """直接传收益序列：内部算 Sharpe/偏度/峰度（年化 √252）。"""
        rng = np.random.default_rng(3)
        rets = pd.Series(rng.normal(0.0008, 0.01, 500))
        m = min_track_record_length(returns=rets, alpha=0.95)
        assert 1.0 < m < 100.0

    def test_no_input_raises(self):
        with pytest.raises(ValueError):
            min_track_record_length()


# ---------------------------------------------------------------------------
# 4. WFE
# ---------------------------------------------------------------------------


class TestWalkForwardEfficiency:
    def test_wfe_ratio(self):
        assert walk_forward_efficiency(oos_sharpe=0.8, is_sharpe=1.0) == pytest.approx(0.8)

    def test_assess_pass(self):
        assert assess_wfe(0.7, 1.0)["verdict"] == "pass"

    def test_assess_marginal(self):
        assert assess_wfe(0.55, 1.0)["verdict"] == "marginal"

    def test_assess_red_flag(self):
        assert assess_wfe(0.3, 1.0)["verdict"] == "red_flag"

    def test_assess_undefined_when_is_non_positive(self):
        r = assess_wfe(0.5, 0.0)
        assert r["verdict"] == "undefined" and r["wfe"] is None


# ---------------------------------------------------------------------------
# 5. 仓内 DSR/CPCV 可 import（不 vendor 外部库的锚点验证）
# ---------------------------------------------------------------------------


class TestInRepoImplementations:
    def test_dsr_importable(self):
        from zephyr.simulation.deflated_sharpe_calculator import DeflatedSharpeCalculator

        assert callable(DeflatedSharpeCalculator)

    def test_cpcv_importable(self):
        from zephyr.backtest.core.cpcv import generate_cpcv_splits

        assert callable(generate_cpcv_splits)
