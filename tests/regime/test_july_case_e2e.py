# [A_test] module_id: MOD-TEST-JULY-E2E | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §5.3.4 Phase2c
# [MODULE] tests.regime.test_july_case_e2e
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.risk_signal_builder; zephyr.regime.overlay_signals_builder; zephyr.regime.core.regime_detector; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] tests/regime/test_july_case_e2e.py
# [A_module] module_id: MOD-TEST-JULY-E2E | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-002 #discussion_001 §5.3.4 #Phase2c #July-2026-crash
"""test_july_case_e2e.py — 2026年7月A股暴跌案例 §5.3.4 精确值端到端测试。

验证 discussion_001 §5.3.4 定义的 5 阶段 RiskSignal 精确值 + S1/S2 overlay 触发。
**年份是 2026**（spec §5.3.4 明确"2026年7月 A股暴跌"，非 2015）。

5 阶段 RiskSignal 精确值（公式 RiskSignal = clamp[0.30, RiskBase×共振惩罚+机会恢复, 1.00]）:
    | 日期          | 异常参数(系数)              | RiskBase | 共振惩罚 | 机会恢复 | RiskSignal |
    |---------------|---------------------------|---------|---------|---------|-----------|
    | 7月上旬        | 无(#1=1.0)                | —       | —       | —       | 1.00       |
    | 7月11-15日     | #1(0.85)#5(0.85)#9#10     | 0.85    | ×0.85   | 0       | 0.72       |
    | 7月17日黑周五   | #1(0.3)#7(0.3)#8(0.3)     | 0.30    | ×0.90   | 0       | 0.30(clamp)|
    | 7月下旬         | #1(0.6)#3(0.6)#8(0.3)     | 0.30    | ×0.90   | 0       | 0.30(clamp)|
    | 8月4日(S2确认) | #1(0.6)+#11(+0.15)#13(+0.10)| 0.60   | ×1.00   | +0.25   | 0.85       |

测试结构:
  1. TestJulyCaseRiskSignalFormula — 5 阶段精确值（直接注入参数，验证 §5.3.4 公式，容差 ±0.01）
  2. TestJulyCaseS1Trigger — 7/17 黑周五 S1 CRISIS 触发（vol_pct>0.90 + corr>0.95 → r10>0）
  3. TestJulyCaseS2NlpGated — S2 trigger/confirm 被 NLP stub 阻断的契约守护
     （bad_news_flat/policy stub=0 → S2 trigger 需 ≥40 无法满足 → r11=0；
      待 NLP 管道接入后此测试需翻转为 r11>0）

S2 strong_confirm/fail 不依赖 NLP stub，但需复杂 Wyckoff Spring OHLCV 序列构造，
由 test_wyckoff_engine.py 单独覆盖阶段识别；本文件聚焦 §5.3.4 精确值 + S1 触发。

依据: discussion_001 v1.3.1 §5.3.4 / Phase 2c 计划 §任务6
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.core.regime_detector import RegimeDetector
from zephyr.regime.overlay_signals_builder import OverlaySignalsConstructor
from zephyr.regime.risk_signal_builder import RiskSignalConstructor

# ---------------------------------------------------------------------------
# 公共：Mock feature_builder（与 test_overlay_signals_builder 同构）
# ---------------------------------------------------------------------------


class _MockFeatureBuilder:
    """模拟 RegimeFeatureBuilder 的 build_features + get_index_kline。"""

    def __init__(self, features: pd.DataFrame, index_df: pd.DataFrame) -> None:
        self._features = features
        self._index_df = index_df

    def build_features(self) -> pd.DataFrame:
        return self._features

    def get_index_kline(self) -> pd.DataFrame:
        return self._index_df


def _make_index_df(
    dates: pd.DatetimeIndex,
    close_arr: np.ndarray,
    volume_arr: np.ndarray,
    symbol: str = "000300",
) -> pd.DataFrame:
    """构造 MultiIndex(symbol, trade_date) index_df。"""
    idx = pd.MultiIndex.from_product([[symbol], dates], names=["symbol", "trade_date"])
    return pd.DataFrame({"close": close_arr, "volume": volume_arr}, index=idx)


def _make_dates(start: str = "2026-01-01", end: str = "2026-08-10") -> pd.DatetimeIndex:
    return pd.bdate_range(start=start, end=end)


def _first_on_or_after(dates: pd.DatetimeIndex, target: str) -> pd.Timestamp:
    """返回 dates 中 ≥ target 的首个交易日（避免周末 get_loc 失败）。"""
    mask = dates >= pd.Timestamp(target)
    if not mask.any():
        raise ValueError(f"{target} 之后无交易日")
    return dates[mask][0]


# ---------------------------------------------------------------------------
# 测试1：5 阶段 RiskSignal 精确值（§5.3.4 核心交付）
# ---------------------------------------------------------------------------


class TestJulyCaseRiskSignalFormula:
    """§5.3.4 五阶段 RiskSignal 精确值断言（直接注入参数，容差 ±0.01）。

    验证 RegimeDetector._compute_risk_signal 的公式：
        RiskSignal = clamp[0.30, RiskBase × (1−0.05×(异常数−1)) + 机会恢复, 1.00]
    + #1 门控：#1=1.0 时直接 return 1.0（附加参数不参与）。

    参数注入而非特征驱动：§5.3.4 表给的是"异常参数(系数)"（公式输入），
    而非特征值；特征→系数映射是阶梯函数（如 #1 ∈ {1.0,0.80,0.60,0.50,0.30}），
    无法精确复现 0.85 等表值。直接注入验证公式精确性，特征驱动触发由 S1 测试覆盖。
    """

    @pytest.mark.parametrize(
        "stage,desc,params,opportunity,expected",
        [
            (
                "stage1_early_july",
                "7月上旬：#1=1.0（无风险）→ #1门控直接return 1.0",
                {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 12: 1.0},
                {"news_ghost": 0.0, "bad_news_flat": 0.0},
                1.00,
            ),
            (
                "stage2_jul11_15",
                "7月11-15日：#1#5#9#10=0.85（4异常）→ 0.85×0.85=0.7225",
                {1: 0.85, 2: 1.0, 3: 1.0, 4: 1.0, 5: 0.85, 6: 1.0, 7: 1.0, 8: 1.0, 9: 0.85, 10: 0.85, 12: 1.0},
                {"news_ghost": 0.0, "bad_news_flat": 0.0},
                0.72,
            ),
            (
                "stage3_black_friday",
                "7月17日黑周五：#1#7#8=0.3（3异常）→ 0.30×0.90=0.27→clamp 0.30",
                {1: 0.30, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 0.30, 8: 0.30, 9: 1.0, 10: 1.0, 12: 1.0},
                {"news_ghost": 0.0, "bad_news_flat": 0.0},
                0.30,
            ),
            (
                "stage4_late_july",
                "7月下旬：#1#3=0.6,#8=0.3（3异常）→ 0.30×0.90=0.27→clamp 0.30",
                {1: 0.60, 2: 1.0, 3: 0.60, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0, 8: 0.30, 9: 1.0, 10: 1.0, 12: 1.0},
                {"news_ghost": 0.0, "bad_news_flat": 0.0},
                0.30,
            ),
            (
                "stage5_aug4_recovery",
                "8月4日：#1=0.6（1异常）+ #11(0.15)+#13(0.10)→ 0.60×1.0+0.25=0.85",
                {1: 0.60, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 12: 1.0},
                {"news_ghost": 0.15, "bad_news_flat": 0.10},
                0.85,
            ),
        ],
    )
    def test_five_stage_risk_signal_precision(self, stage, desc, params, opportunity, expected):
        """5 阶段 RiskSignal 精确值断言（容差 ±0.01，对齐 §5.3.4 表）。"""
        risk_inputs = {"params": params, "opportunity": opportunity}
        detector = RegimeDetector(shrinkage_enabled=True)
        risk = detector._compute_risk_signal(risk_inputs)
        assert risk == pytest.approx(expected, abs=0.01), f"{stage} ({desc}): 期望 RiskSignal={expected}，实际 {risk}"

    def test_stage1_primary_gating_mechanism(self):
        """Stage1 #1门控：#1=1.0 时即使附加参数<1.0 仍 return 1.0。

        这是 Phase 2a 治本 Sharpe 退化的核心机制——非危机日附加参数不参与。
        """
        risk_inputs = {
            "params": {1: 1.0, 7: 0.30, 8: 0.30, 9: 0.30},  # #1=1.0 但附加极端
            "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0},
        }
        detector = RegimeDetector(shrinkage_enabled=True)
        assert detector._compute_risk_signal(risk_inputs) == 1.0

    def test_resonance_penalty_formula(self):
        """共振惩罚 = max(0.80, 1−0.05×(异常数−1))：4异常→0.85, 3异常→0.90, 1异常→1.0。"""
        detector = RegimeDetector(shrinkage_enabled=True)
        # 4 异常（#1#5#9#10=0.85）→ resonance=1−0.05×3=0.85 → 0.85×0.85=0.7225
        r4 = detector._compute_risk_signal(
            {
                "params": {1: 0.85, 5: 0.85, 9: 0.85, 10: 0.85},
                "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0},
            }
        )
        # 3 异常（#1#7#8=0.3）→ resonance=1−0.05×2=0.90 → 0.30×0.90=0.27→clamp 0.30
        r3 = detector._compute_risk_signal(
            {
                "params": {1: 0.30, 7: 0.30, 8: 0.30},
                "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0},
            }
        )
        # 1 异常（#1=0.6）→ resonance=1−0.05×0=1.00 → 0.60×1.0=0.60
        r1 = detector._compute_risk_signal(
            {
                "params": {1: 0.60},
                "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0},
            }
        )
        assert r4 == pytest.approx(0.72, abs=0.01)
        assert r3 == pytest.approx(0.30, abs=0.01)
        assert r1 == pytest.approx(0.60, abs=0.01)

    def test_opportunity_recovery_cap(self):
        """机会恢复上限 +0.25（#11+#13 超 0.25 仍只 +0.25，不能完全抵消危机）。"""
        detector = RegimeDetector(shrinkage_enabled=True)
        # #1=0.6 + #11(0.5)+#13(0.5)=1.0 → recovery cap 0.25 → 0.60×1.0+0.25=0.85
        r = detector._compute_risk_signal(
            {
                "params": {1: 0.60},
                "opportunity": {"news_ghost": 0.50, "bad_news_flat": 0.50},
            }
        )
        assert r == pytest.approx(0.85, abs=0.01), f"机会恢复 cap 0.25：0.60+0.25=0.85，实际 {r}"


# ---------------------------------------------------------------------------
# 测试2：7/17 黑周五 S1 CRISIS 触发（特征驱动）
# ---------------------------------------------------------------------------


class TestJulyCaseS1Trigger:
    """7/17 黑周五 S1 Any→CRISIS 触发（vol_pct>0.90 + corr>0.95 → r10>0）。

    S1 trigger 条件（TRANSITION_CONFIG）：keys_gte {vix_panic: 60, correlation: 60}
    → p_overlay {r10: 0.60}。

    构造合成特征：7/14-7/16 危机积聚（vol_pct=0.92, corr=0.96），
    build_for_date(7/17) shift(1) 取 7/16 数据 → vix_panic=85, correlation=80
    → S1 trigger → overlay_probs["r10"]=0.60 > 0。
    """

    def _build_crisis_scenario(self):
        """构造 2026-01-01~08-10 合成特征，7/14-7/16 危机积聚。"""
        dates = _make_dates("2026-01-01", "2026-08-10")
        n = len(dates)
        # 7/14-7/16 危机段（vol_pct>0.90, corr>0.95）；其余常态
        crisis_mask = (dates >= "2026-07-14") & (dates <= "2026-07-16")
        vol_pct = np.where(crisis_mask, 0.92, 0.30)
        corr = np.where(crisis_mask, 0.96, 0.50)
        slope = np.where(crisis_mask, -0.4, 0.0)  # 危机段下跌
        vol_anom = np.where(crisis_mask, 2.5, 0.0)
        feat = pd.DataFrame(
            {
                "realized_vol_pct": vol_pct,
                "hurst_dfa": np.full(n, 0.5),
                "kalman_slope": slope,
                "cross_asset_corr": corr,
                "ad_ratio": np.zeros(n),
                "volume_anomaly": vol_anom,
            },
            index=dates,
        )
        # close：平稳 3000 → 危机段缓跌 → 不影响 S1（S1 只用 vol_pct/corr/vol_z）
        close = np.full(n, 3000.0)
        close[crisis_mask] = np.linspace(3000, 2850, crisis_mask.sum())
        idx_df = _make_index_df(dates, close, np.full(n, 1e8))
        return dates, feat, idx_df

    def test_s1_trigger_produces_r10(self):
        """7/17 查询 → 7/16 危机数据 → S1 trigger → overlay_probs['r10'] > 0。"""
        dates, feat, idx_df = self._build_crisis_scenario()
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2026-01-01",
            backtest_end="2026-08-10",
            data_load_start="2026-01-01",
            feature_builder=fb,
        )
        dt = _first_on_or_after(dates, "2026-07-17")
        result = ctor.build_for_date(dt)
        s1 = result["transitions"]["S1"]
        # shift(1) 取 7/16 数据：vol_pct=0.92>0.90→vix_panic=85; corr=0.96>0.95→correlation=80
        assert s1["vix_panic"] >= 60, f"7/17 S1 vix_panic={s1['vix_panic']} 应≥60（7/16 vol_pct=0.92）"
        assert s1["correlation"] >= 60, f"7/17 S1 correlation={s1['correlation']} 应≥60（7/16 corr=0.96）"
        # S1 trigger: vix_panic≥60 AND correlation≥60 → r10: 0.60
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(result)
        assert overlay_probs["r10"] > 0, f"7/17 S1 应触发 CRISIS(r10)>0，实际 overlay_probs={overlay_probs}"

    def test_s1_no_trigger_before_crisis(self):
        """7/10（危机前）→ 常态数据 → S1 不触发 → r10=0（C1 不退化前提）。"""
        dates, feat, idx_df = self._build_crisis_scenario()
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2026-01-01",
            backtest_end="2026-08-10",
            data_load_start="2026-01-01",
            feature_builder=fb,
        )
        dt = _first_on_or_after(dates, "2026-07-10")
        result = ctor.build_for_date(dt)
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(result)
        assert overlay_probs["r10"] == 0.0, f"7/10 危机前不应触发 S1，实际 r10={overlay_probs['r10']}"

    def test_s1_trigger_e2e_with_risk_signal(self):
        """7/17 S1 overlay + 危机 risk_inputs → detect 产出有效 Shrinkage。"""
        dates, feat, idx_df = self._build_crisis_scenario()
        fb = _MockFeatureBuilder(feat, idx_df)
        overlay_ctor = OverlaySignalsConstructor(
            backtest_start="2026-01-01",
            backtest_end="2026-08-10",
            data_load_start="2026-01-01",
            feature_builder=fb,
        )
        dt = _first_on_or_after(dates, "2026-07-17")
        overlay = overlay_ctor.build_for_date(dt)
        # 危机 risk_inputs（#1=0.30 黑周五危机地板）
        risk_inputs = {
            "params": {1: 0.30, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 0.30, 8: 0.30, 9: 1.0, 10: 1.0, 12: 1.0},
            "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0},
        }
        detector = RegimeDetector(shrinkage_enabled=True)
        regime_features = {"X": np.zeros((60, 6))}
        probs, shrinkage = detector.detect(regime_features, overlay_signals=overlay, risk_signal_inputs=risk_inputs)
        # 危机 Shrinkage 应显著<1.0（risk=0.30 × confidence）
        assert shrinkage.value < 0.5, f"7/17 危机 Shrinkage 应<0.5，实际 {shrinkage.value}"
        assert len(probs.probabilities) == 7  # 7态(4 HMM r1-r4 + 3 overlay r10-r12),见 REGIME_STATES


# ---------------------------------------------------------------------------
# 测试3：S2 trigger/confirm 被 NLP stub 阻断（契约守护）
# ---------------------------------------------------------------------------


class TestJulyCaseS2NlpGated:
    """S2 trigger/confirm 被 NLP stub（bad_news_flat/policy=0）阻断的契约守护。

    S2 trigger 需 keys_gte {capitulation: 60, vix: 40, bad_news_flat: 40}，
    S2 confirm 需 keys_gte {wyckoff: 60, policy: 40, valuation: 40, fund: 50}。
    bad_news_flat/policy 是 NLP stub（=0.0），故 trigger/confirm 无法满足 → r11=0。

    Phase 2c 现状：仅 S2 strong_confirm（spring+three_yang+total≥250）和
    S2 fail（break_sc_low+vix_new_high+fund_outflow）可触发（不依赖 NLP）。
    待 NLP 管道接入 policy/bad_news_flat 后，本测试需翻转为 r11>0。
    """

    def _build_capitulation_scenario(self):
        """构造 7/27 投降式抛售场景（capitulation≥60 + vix≥40，但 bad_news_flat=0）。

        用索引定位连续两个交易日（避免 7/26 周末导致 d26==d27）：
        i26=危机高位日, i27=i26+1=投降式抛售日, 查询 i27+1 → shift(1) 取 i27 数据。
        """
        dates = _make_dates("2026-01-01", "2026-08-10")
        n = len(dates)
        # 定位 7/27 附近的交易日索引（i27），i26=i27-1 为前日
        i27 = int(np.where(dates >= "2026-07-27")[0][0])
        i26 = i27 - 1
        vol_pct = np.full(n, 0.30)
        vol_pct[i26] = 0.95  # 前日危机高位
        vol_pct[i27] = 0.80  # 当日下降（vix 见顶回落）
        vol_anom = np.full(n, 0.0)
        vol_anom[i27] = 3.5  # 放量
        slope = np.zeros(n)
        slope[i27] = -0.5  # 暴跌趋势
        feat = pd.DataFrame(
            {
                "realized_vol_pct": vol_pct,
                "hurst_dfa": np.full(n, 0.5),
                "kalman_slope": slope,
                "cross_asset_corr": np.full(n, 0.50),
                "ad_ratio": np.zeros(n),
                "volume_anomaly": vol_anom,
            },
            index=dates,
        )
        # close：i27 暴跌 4.5%（capitulation z>3 & pct<-4% → 90）
        close = np.full(n, 3000.0)
        close[i27] = close[i27 - 1] * (1 - 0.045)
        idx_df = _make_index_df(dates, close, np.full(n, 1e8))
        return dates, feat, idx_df, i27

    def test_s2_trigger_blocked_by_bad_news_flat_stub(self):
        """7/27 capitulation≥60 + vix≥40 但 bad_news_flat=0(stub) → S2 trigger 不满足 → r11=0。

        契约守护：S2 trigger 需 bad_news_flat≥40，NLP 未接入时 stub=0 → 永不满足。
        待 NLP 接入后此断言翻转为 r11>0（test 将在 NLP 管道落地时更新）。
        """
        dates, feat, idx_df, i27 = self._build_capitulation_scenario()
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2026-01-01",
            backtest_end="2026-08-10",
            data_load_start="2026-01-01",
            feature_builder=fb,
        )
        # 查 i27+1 → shift(1) 取 i27 投降式抛售数据
        dt = dates[i27 + 1]
        result = ctor.build_for_date(dt)
        s2 = result["transitions"]["S2"]
        # 验证 capitulation 和 vix 确实达标（证明数据构造正确）
        assert s2["capitulation"] >= 60, f"7/27 capitulation={s2['capitulation']} 应≥60（z>3 & pct<-4%）"
        assert s2["vix"] >= 40, f"7/27 vix={s2['vix']} 应≥40（前日>0.90 & 当日降）"
        # 但 bad_news_flat 是 NLP stub = 0.0
        assert s2["bad_news_flat"] == 0.0, "bad_news_flat 应为 NLP stub=0.0"
        assert s2["policy"] == 0.0, "policy 应为 NLP stub=0.0"
        # S2 trigger 需 bad_news_flat≥40 → stub=0 不满足。
        # 直接检查 S2 自身 stage（不依赖 overlay_probs——后者会被 T6 fail 的
        # p_overlay{r11:0.40} 污染，无法隔离 S2 对 r11 的贡献）。
        detector = RegimeDetector(shrinkage_enabled=False)
        s2_trig = detector.record_transition("S2", s2)
        assert s2_trig.stage != "trigger", (
            f"S2 trigger 应被 bad_news_flat stub=0 阻断（需≥40），实际 stage={s2_trig.stage}"
        )
        assert not s2_trig.triggered, (
            f"S2 trigger/confirm/strong_confirm 均被 NLP stub 阻断，triggered 应 False；"
            f"stage={s2_trig.stage}。若 stage∈trigger/confirm/strong_confirm 说明 NLP 已接入，"
            f"需翻转此测试。"
        )

    def test_s2_confirm_blocked_by_policy_stub(self):
        """S2 confirm 需 policy≥40，NLP stub=0 → confirm 不满足（即使 wyckoff/valuation/fund 达标）。

        构造 wyckoff/valuation/fund 三维度均达标的见底场景，验证 policy stub=0 仍阻断
        confirm。日期范围从 2025-01-01 起（valuation 需 250 日 rolling_max 历史）。

        close 构造：前 250 日 3000 高点 → 线性下跌至 1000 → 末期 25 日窄幅上倾
        （吸筹整理，close 在 20 日区间上部）。末期上倾使 MVP wyckoff 满足
        range_pct<0.02 & pos>0.6 → 70（≥60）；深跌使 valuation pos<0.40 → 60。
        """
        dates = _make_dates("2025-01-01", "2026-08-10")
        n = len(dates)
        decline_start = 260  # 250 日窗口填满后开始下跌
        rise_start = n - 25  # 末期 25 日窄幅上倾（吸筹）
        close = np.full(n, 3000.0)
        close[decline_start:rise_start] = np.linspace(3000, 1000, rise_start - decline_start)
        close[rise_start:] = np.linspace(1000, 1012, n - rise_start)  # 上倾<1.2%，range<2%
        # 放量：与吸筹段对齐，使 build_for_date(dates[-5]) 的近 20 日均量=2e8、
        # 前 20 日均量=1e8 → 均量比≈2.0 → fund=70（≥50）。
        # rise_start=n-25：近窗 [n-25,n-6] 全 2e8，前窗 [n-45,n-26] 全 1e8。
        volume = np.full(n, 1e8)
        volume[rise_start:] = 2e8
        feat = pd.DataFrame(
            {
                "realized_vol_pct": np.full(n, 0.30),
                "hurst_dfa": np.full(n, 0.5),
                "kalman_slope": np.zeros(n),
                "cross_asset_corr": np.full(n, 0.50),
                "ad_ratio": np.zeros(n),
                "volume_anomaly": np.zeros(n),
            },
            index=dates,
        )
        idx_df = _make_index_df(dates, close, volume)
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2025-01-01",
            backtest_end="2026-08-10",
            data_load_start="2025-01-01",
            feature_builder=fb,
        )
        dt = dates[-5]  # 末期（吸筹 + 放量，250 日窗口已填满）
        result = ctor.build_for_date(dt)
        s2 = result["transitions"]["S2"]
        # 验证 wyckoff/valuation/fund 三维度均达标（证明非 NLP 维度可满足）
        assert s2["wyckoff"] >= 60, f"wyckoff={s2['wyckoff']} 应≥60（窄幅上倾吸筹）"
        assert s2["valuation"] >= 40, f"valuation={s2['valuation']} 应≥40（深度折价）"
        assert s2["fund"] >= 50, f"fund={s2['fund']} 应≥50（放量）"
        # 但 policy stub=0 阻断 confirm（confirm 需 wyckoff/policy/valuation/fund 同时达标）
        assert s2["policy"] == 0.0, "policy 应为 NLP stub=0.0"
        # 直接检查 S2 自身 stage（不依赖 overlay_probs——后者会被其他转换的
        # p_overlay 污染，无法隔离 S2 的贡献）。
        detector = RegimeDetector(shrinkage_enabled=False)
        s2_trig = detector.record_transition("S2", s2)
        assert s2_trig.stage != "confirm", (
            f"S2 confirm 应被 policy stub=0 阻断（需≥40，其余维度已达标），实际 stage={s2_trig.stage}"
        )
        assert s2_trig.stage != "strong_confirm", (
            f"S2 strong_confirm 需 spring+three_yang+total≥250，本场景不应触发；实际 stage={s2_trig.stage}"
        )
        assert not s2_trig.triggered, (
            f"S2 confirm/trigger 均被 NLP stub 阻断，triggered 应 False；"
            f"stage={s2_trig.stage}。若 stage∈trigger/confirm/strong_confirm 说明 NLP 已接入，"
            f"需翻转此测试。"
        )
