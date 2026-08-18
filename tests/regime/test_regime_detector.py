# [A_test] module_id: MOD-TEST-REGIME-DET | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-001 | docs/03_modules/_domain_regime/regime_detector/blueprint.md | §6
# [MODULE] tests.regime.test_regime_detector
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.core.regime_detector; hmmlearn; numpy
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_hmm;AssertionError->fail
# [TESTS] tests/regime/test_regime_detector.py
# [A_module] module_id=MOD-TEST-REGIME-DET | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-001 #10_regime_detector_spec #11_regime_backtest_validation_plan #ARCH-REGIME-OVERLAY-001
"""test_regime_detector.py — RegimeDetector (MOD-REGIME-001) 单元测试

覆盖 blueprint §6 Phase 1 测试规划（~30 项）：
  - HMM 4态：拟合/predict_proba 9维Σ=1/因果Viterbi末步/walk-forward季度重拟合/降级
  - 覆盖层：3特殊态(CRISIS/RECOVERY/BREAKOUT)触发/不触发/8转换评分
  - 12维合并：无覆盖层退化为纯HMM/覆盖层压缩HMM/归一化Σ=1
  - ConfidenceSignal：max(P) 4档映射/稀有态折扣/边界值/下界0.21
  - RiskSignal：13参数聚合/最严主导/共振惩罚/机会恢复上限+0.25/clamp/7月案例
  - Shrinkage：开/关切换/shrinkage_enabled=False恒=1.0/上下界
  - TransitionTriggered：8转换触发/评分明细完整/未知类型抛错
  - RegimeProbabilities：12维Σ=1/字段完整性

依据: 10_regime_detector_spec v1.3.1 §5.3.4（7月案例）/ 11_regime_backtest_validation_plan §4（验证接口）
"""

from __future__ import annotations

import warnings
from datetime import datetime

import numpy as np
import pytest

from zephyr.regime.core.regime_detector import (
    HMM_STATES,
    OVERLAY_STATES,
    REGIME_STATES,
    TRANSITIONS,
    HMMFittingError,
    OverlayRuleError,
    RegimeDetector,
    RegimeProbabilities,
    ShrinkageResult,
    TransitionTriggered,
)

try:
    import hmmlearn  # noqa: F401
    HMMLEARN_AVAILABLE = True
except Exception:  # pragma: no cover
    HMMLEARN_AVAILABLE = False

skip_no_hmmlearn = pytest.mark.skipif(
    not HMMLEARN_AVAILABLE, reason="hmmlearn 未安装，跳过真实 HMM 拟合测试"
)


# ── fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def detector() -> RegimeDetector:
    """默认 detector（shrinkage 开启，未 fit）。"""
    return RegimeDetector(shrinkage_enabled=True)


@pytest.fixture
def detector_off() -> RegimeDetector:
    """Shrinkage 关闭的 detector（C1 验证基准组）。"""
    return RegimeDetector(shrinkage_enabled=False)


@pytest.fixture
def synthetic_features() -> np.ndarray:
    """合成 HMM 特征：3 段不同 regime（低波上涨/高波下跌/中波震荡），让 HMM 学到结构。"""
    rng = np.random.default_rng(42)
    seg1 = rng.normal([0.2, 0.0, 0.5], 0.1, (350, 3))
    seg2 = rng.normal([0.8, -0.3, 0.2], 0.15, (300, 3))
    seg3 = rng.normal([0.5, 0.1, 0.5], 0.1, (350, 3))
    return np.vstack([seg1, seg2, seg3])


@pytest.fixture
def full_risk_params() -> dict:
    """13 参数全正常（系数 1.0）的 RiskSignal 输入。"""
    return {"params": {i: 1.0 for i in list(range(1, 11)) + [12]}}


# ── 1. RegimeProbabilities 输出 ─────────────────────────────────────


class TestRegimeProbabilitiesOutput:
    def test_7dim_and_sum1(self, detector: RegimeDetector):
        """4 HMM 态 + 3 overlay 态 = 7 维概率分布（13_regime_phase3_engineering_plan §2.1 降态后）。"""
        probs, _ = detector.detect({}, {}, {})
        assert len(probs.probabilities) == 7
        assert set(probs.probabilities.keys()) == set(REGIME_STATES)
        assert abs(sum(probs.probabilities.values()) - 1.0) < 1e-9

    def test_fields_complete(self, detector: RegimeDetector):
        probs, _ = detector.detect({}, {}, {})
        assert isinstance(probs, RegimeProbabilities)
        assert probs.dominant_regime in REGIME_STATES
        assert 0.0 <= probs.confidence <= 1.0
        assert 0.0 <= probs.dominant_frequency <= 1.0
        assert isinstance(probs.timestamp, datetime)
        assert probs.schema_version == "1.0"
        assert set(probs.hmm_probabilities.keys()) == set(HMM_STATES)
        assert set(probs.overlay_probabilities.keys()) == set(OVERLAY_STATES)


# ── 2. HMM 4态 ──────────────────────────────────────────────────────


class TestHMM9States:
    @skip_no_hmmlearn
    @pytest.mark.filterwarnings("ignore")
    def test_fit_predict_proba_9dim_sum1(self, detector, synthetic_features):
        detector.fit({"X": synthetic_features})
        assert detector._hmm_model is not None
        assert not detector._hmm_degraded
        probs, _ = detector.detect({"X": synthetic_features[-50:]}, {}, {})
        assert len(probs.hmm_probabilities) == 4
        assert set(probs.hmm_probabilities.keys()) == set(HMM_STATES)
        assert abs(sum(probs.hmm_probabilities.values()) - 1.0) < 1e-6
        # 学到结构 → 非均匀（存在 dominant 态）
        assert max(probs.hmm_probabilities.values()) > 0.15

    @skip_no_hmmlearn
    @pytest.mark.filterwarnings("ignore")
    def test_causal_viterbi_uses_last_step(self, detector, synthetic_features):
        """因果 Viterbi：predict_proba 取序列末步（防前视，blueprint §3.1）。"""
        detector.fit({"X": synthetic_features})
        X = synthetic_features[-50:]
        probs, _ = detector.detect({"X": X}, {}, {})
        expected = detector._hmm_model.predict_proba(X)[-1]
        for i, s in enumerate(HMM_STATES):
            assert abs(probs.hmm_probabilities[s] - float(expected[i])) < 1e-9

    @skip_no_hmmlearn
    @pytest.mark.filterwarnings("ignore")
    def test_walk_forward_quarterly_refit(self, synthetic_features):
        """walk-forward 季度重拟合：每季 refit，模型被替换（blueprint §3.1）。"""
        d = RegimeDetector()
        quarters = [synthetic_features[i * 250:(i + 1) * 250] for i in range(4)]
        prev = None
        for q in quarters:
            d.fit({"X": q})
            assert d._hmm_model is not None
            if prev is not None:
                assert d._hmm_model is not prev, "walk-forward 模型未刷新"
            prev = d._hmm_model
            p, _ = d.detect({"X": q[-20:]}, {}, {})
            assert abs(sum(p.hmm_probabilities.values()) - 1.0) < 1e-6

    @skip_no_hmmlearn
    @pytest.mark.filterwarnings("ignore")
    def test_multi_sequence_lengths(self, synthetic_features):
        """多序列 lengths 拼接拟合（walk-forward 多段，blueprint §3.1）。"""
        d = RegimeDetector()
        d.fit({"X": synthetic_features, "lengths": [250, 250, 250, 250]})
        assert d._hmm_model is not None
        p, _ = d.detect({"X": synthetic_features[-30:]}, {}, {})
        assert abs(sum(p.hmm_probabilities.values()) - 1.0) < 1e-6

    def test_degraded_uniform_when_not_fit(self, detector: RegimeDetector):
        """未 fit → HMM 降级均匀分布 1/4（blueprint §7.4）。"""
        probs, _ = detector.detect({}, {}, {})
        for s in HMM_STATES:
            assert abs(probs.hmm_probabilities[s] - 1.0 / 4.0) < 1e-9

    @skip_no_hmmlearn
    @pytest.mark.filterwarnings("ignore")
    def test_degraded_on_fit_failure(self, detector: RegimeDetector):
        """fit 失败（含 NaN）→ 抛 HMMFittingError + 标记 degraded。"""
        bad_X = np.array([[1.0, 2.0], [float("nan"), 3.0], [4.0, 5.0]])
        with pytest.raises(HMMFittingError):
            detector.fit({"X": bad_X})
        # detect 仍可降级运行（不抛错）
        probs, _ = detector.detect({}, {}, {})
        for s in HMM_STATES:
            assert abs(probs.hmm_probabilities[s] - 1.0 / 4.0) < 1e-9


# ── 2b. 温度缩放校准（13_regime_phase3_engineering_plan §2.2 P0-E2 Stage 1）────────────


class TestTemperatureScaling:
    """温度缩放校准不变性——防回滚 critical fix（项目 invariant 约定）."""

    @skip_no_hmmlearn
    @pytest.mark.filterwarnings("ignore")
    def test_t1_identity(self, synthetic_features):
        """T=1.0 不缩放——HMM 概率与无温度参数完全一致（基准不变性）。"""
        d_base = RegimeDetector()
        d_t1 = RegimeDetector(temperature=1.0)
        d_base.fit({"X": synthetic_features})
        d_t1.fit({"X": synthetic_features})
        X = synthetic_features[-50:]
        p_base, _ = d_base.detect({"X": X}, {}, {})
        p_t1, _ = d_t1.detect({"X": X}, {}, {})
        for s in HMM_STATES:
            assert abs(p_base.hmm_probabilities[s] - p_t1.hmm_probabilities[s]) < 1e-9

    @skip_no_hmmlearn
    @pytest.mark.filterwarnings("ignore")
    def test_t_gt1_flattens_and_preserves_argmax(self, synthetic_features):
        """T>1 降温：max(P) 下降、Σ=1 保持、argmax 不变（保序性，Guo2017 性质）。"""
        d = RegimeDetector(temperature=3.0)
        d.fit({"X": synthetic_features})
        X = synthetic_features[-50:]
        raw = d._hmm_model.predict_proba(X)[-1]
        raw_max_idx = int(raw.argmax())
        raw_max = float(raw.max())
        probs, _ = d.detect({"X": X}, {}, {})
        cal = [probs.hmm_probabilities[s] for s in HMM_STATES]
        # Σ=1 保持（归一化不变性）
        assert abs(sum(cal) - 1.0) < 1e-9
        # max 下降（降温有效）
        assert max(cal) < raw_max
        # argmax 不变（保序——不改变预测类别）
        assert int(np.argmax(cal)) == raw_max_idx

    @skip_no_hmmlearn
    @pytest.mark.filterwarnings("ignore")
    def test_higher_t_more_flattening(self, synthetic_features):
        """T 越大降温越强：max(P) 随 T 单调递减（tempering 单调性）。"""
        X = synthetic_features[-50:]
        maxes: dict[float, float] = {}
        for T in [1.0, 2.0, 3.0, 5.0]:
            d = RegimeDetector(temperature=T)
            d.fit({"X": synthetic_features})
            probs, _ = d.detect({"X": X}, {}, {})
            maxes[T] = max(probs.hmm_probabilities.values())
        assert maxes[1.0] > maxes[2.0] > maxes[3.0] > maxes[5.0]

    @skip_no_hmmlearn
    @pytest.mark.filterwarnings("ignore")
    def test_t_le_zero_degrades_uniform(self, synthetic_features):
        """T≤0 非法温度 → 降级均匀分布 1/4（防御，防数值爆炸）。"""
        d = RegimeDetector(temperature=1.0)
        d.fit({"X": synthetic_features})
        d.temperature = 0.0  # 运行时改为非法值
        X = synthetic_features[-50:]
        probs, _ = d.detect({"X": X}, {}, {})
        for s in HMM_STATES:
            assert abs(probs.hmm_probabilities[s] - 1.0 / 4.0) < 1e-9


# ── 3. 覆盖层 ───────────────────────────────────────────────────────


class TestOverlay:
    def test_crisis_trigger_s1(self, detector: RegimeDetector):
        """S1 触发 → P_overlay(r10 CRISIS)=0.6（§4.1）。"""
        op = detector._run_overlay({"transitions": {
            "S1": {"vix_panic": 70, "correlation": 65, "liquidity": 40}}})
        assert abs(op["r10"] - 0.6) < 1e-9
        assert op["r11"] == 0.0 and op["r12"] == 0.0

    def test_recovery_trigger_s2(self, detector: RegimeDetector):
        """S2 触发 → P_overlay(r11 RECOVERY)=0.4（§4.12.8）。"""
        op = detector._run_overlay({"transitions": {
            "S2": {"capitulation": 65, "vix": 45, "bad_news_flat": 45}}})
        assert abs(op["r11"] - 0.4) < 1e-9

    def test_breakout_trigger_t1(self, detector: RegimeDetector):
        """T1 触发 → P_overlay(r12 BREAKOUT)=0.8（§4.2）。"""
        op = detector._run_overlay({"transitions": {"T1": {"bqs": 70}}})
        assert abs(op["r12"] - 0.8) < 1e-9

    def test_no_trigger_degrades_to_zero(self, detector: RegimeDetector):
        """无转换触发 → P_overlay 全 0（退化为纯 HMM，blueprint §3.3）。"""
        op = detector._run_overlay({"transitions": {
            "S2": {"capitulation": 30, "vix": 10}}})  # 未达阈值
        assert op == {"r10": 0.0, "r11": 0.0, "r12": 0.0}

    def test_8_transitions_all_recordable(self, detector: RegimeDetector):
        """8 转换均可记录（B4 验证接口，11_regime_backtest_validation_plan §4）。"""
        for tid in TRANSITIONS:
            trig = detector.record_transition(tid, {"_dummy": 1.0})
            assert isinstance(trig, TransitionTriggered)
            assert trig.transition_type == tid
            assert trig.total_score == 1.0
            assert isinstance(trig.score_breakdown, dict)


# ── 3b. overlay #1 门控（方案A，#ARCH-REGIME-OVERLAY-001）─────────


class TestOverlayGating:
    """overlay #1 门控测试（#ARCH-REGIME-OVERLAY-001 方案A固化）。

    门控逻辑：overlay_gated=True（默认）时，detect() 在 _run_overlay 之后检查
    risk_signal_inputs.params[1]：
      - #1 >= 1.0（非危机）→ overlay_probs 置零，overlay 概率不注入
        （避免 T1/S1 假阳性触发系统性压仓致 Sharpe 退化 0.02）；
        但 _run_overlay 已完成转换评估，_last_transitions 保留触发记录
        （S2 在危机结束 #1≥1.0 时点触发，B4 验证需捕获）
      - #1 <  1.0（危机期）→ overlay_probs 保留，overlay 正常生效
    与 _compute_risk_signal 的 #1 门控对齐（#1>=1.0 时 RiskSignal=1.0）。
    """

    @pytest.fixture
    def s1_overlay(self) -> dict:
        """S1 触发的 overlay_signals（CRISIS r10=0.6）。"""
        return {"transitions": {"S1": {"vix_panic": 70, "correlation": 65, "liquidity": 40}}}

    @pytest.fixture
    def s2_overlay(self) -> dict:
        """S2 触发的 overlay_signals（RECOVERY r11=0.4，trigger 阶段）。"""
        return {"transitions": {"S2": {"capitulation": 65, "vix": 45, "bad_news_flat": 45}}}

    def test_default_overlay_gated_is_true(self):
        """默认 overlay_gated=True（治本方案默认开启）。"""
        d = RegimeDetector(shrinkage_enabled=True)
        assert d.overlay_gated is True

    def test_gated_blocks_overlay_when_primary_ge_1(self, s1_overlay):
        """#1>=1.0（非危机）+ overlay_gated=True → overlay 被屏蔽，overlay_probs 全 0。"""
        d = RegimeDetector(shrinkage_enabled=True, overlay_gated=True)
        probs, _ = d.detect({}, s1_overlay, {"params": {1: 1.0}})
        for s in OVERLAY_STATES:
            assert probs.overlay_probabilities[s] == 0.0, f"{s} 应被门控屏蔽"

    def test_gated_keeps_overlay_when_primary_lt_1(self, s1_overlay):
        """#1<1.0（危机期）+ overlay_gated=True → overlay 正常生效，r10=0.6。"""
        d = RegimeDetector(shrinkage_enabled=True, overlay_gated=True)
        probs, _ = d.detect({}, s1_overlay, {"params": {1: 0.5}})
        assert abs(probs.overlay_probabilities["r10"] - 0.6) < 1e-9

    def test_ungated_keeps_overlay_regardless_of_primary(self, s1_overlay):
        """overlay_gated=False → 无论 #1 值，overlay 全程生效（ungated 诊断模式）。"""
        d = RegimeDetector(shrinkage_enabled=True, overlay_gated=False)
        probs, _ = d.detect({}, s1_overlay, {"params": {1: 1.0}})
        assert abs(probs.overlay_probabilities["r10"] - 0.6) < 1e-9

    def test_gated_blocks_when_risk_inputs_missing(self, s1_overlay):
        """risk_signal_inputs 缺失 → 默认 #1=1.0 → overlay 被屏蔽（降级安全）。"""
        d = RegimeDetector(shrinkage_enabled=True, overlay_gated=True)
        probs, _ = d.detect({}, s1_overlay, {})
        for s in OVERLAY_STATES:
            assert probs.overlay_probabilities[s] == 0.0

    def test_gated_blocks_when_risk_inputs_none(self, s1_overlay):
        """risk_signal_inputs=None → 默认 #1=1.0 → overlay 被屏蔽。"""
        d = RegimeDetector(shrinkage_enabled=True, overlay_gated=True)
        probs, _ = d.detect({}, s1_overlay, None)
        for s in OVERLAY_STATES:
            assert probs.overlay_probabilities[s] == 0.0

    def test_gated_just_below_boundary(self, s1_overlay):
        """#1=0.99（略低于 1.0）→ overlay 正常生效（危机期）。"""
        d = RegimeDetector(shrinkage_enabled=True, overlay_gated=True)
        probs, _ = d.detect({}, s1_overlay, {"params": {1: 0.99}})
        assert abs(probs.overlay_probabilities["r10"] - 0.6) < 1e-9

    def test_gated_keeps_transition_records_when_blocked(self, s1_overlay):
        """门控屏蔽概率注入，但保留转换评估记录（B4 验证接口，11_regime_backtest_validation_plan §4 ③）。

        #1>=1.0（非危机）+ overlay_gated=True → overlay_probs 全 0，但 _last_transitions
        仍记录 S1 触发事件（triggered=True, stage=trigger），供 B4 转换触发准确性验证。
        """
        d = RegimeDetector(shrinkage_enabled=True, overlay_gated=True)
        probs, _ = d.detect({}, s1_overlay, {"params": {1: 1.0}})
        # overlay 概率被屏蔽
        for s in OVERLAY_STATES:
            assert probs.overlay_probabilities[s] == 0.0
        # 转换记录仍保留（B4 验证依赖）
        assert len(d._last_transitions) == 1
        trig = d._last_transitions[0]
        assert trig.transition_type == "S1"
        assert trig.triggered is True
        assert trig.stage == "trigger"

    def test_gated_s2_recorded_in_non_crisis(self, s2_overlay):
        """S2(CRISIS→RECOVERY) 在危机结束（#1≥1.0）时点触发，转换记录被保留。

        回归测试：S2 语义恰在危机结束时触发（#1 从 <1.0 恢复到 ≥1.0），
        旧门控在入口清空 overlay_signals 致 S2 转换评估被跳过，B4 验证
        S2 recovery 0/3 漏触发（Phase 2 不闭环）。修复后 _last_transitions
        保留 S2 触发记录，B4 可捕获。
        """
        d = RegimeDetector(shrinkage_enabled=True, overlay_gated=True)
        probs, _ = d.detect({}, s2_overlay, {"params": {1: 1.0}})
        # overlay 概率被屏蔽（Sharpe 保护不变）
        assert probs.overlay_probabilities["r11"] == 0.0
        # S2 转换记录保留（B4 修复核心）
        assert len(d._last_transitions) == 1
        trig = d._last_transitions[0]
        assert trig.transition_type == "S2"
        assert trig.triggered is True
        assert trig.stage == "trigger"


# ── 4. 12维合并归一化 ───────────────────────────────────────────────


class TestMerge:
    def test_no_overlay_degrades_to_hmm(self, detector: RegimeDetector):
        """无覆盖层 → P(r1..r4)=P_hmm，P(r10..r12)=0（blueprint §3.3）。"""
        hmm = {s: 1.0 / 4.0 for s in HMM_STATES}
        merged = detector._merge_probabilities(hmm, {"r10": 0.0, "r11": 0.0, "r12": 0.0})
        for s in HMM_STATES:
            assert abs(merged.probabilities[s] - 1.0 / 4.0) < 1e-9
        for s in OVERLAY_STATES:
            assert merged.probabilities[s] == 0.0

    def test_overlay_compresses_hmm(self, detector: RegimeDetector):
        """S1 触发 P(r10)=0.6 → HMM 4态被压缩到 0.4 等比（blueprint §3.3）。"""
        hmm = {s: 1.0 / 4.0 for s in HMM_STATES}
        merged = detector._merge_probabilities(hmm, {"r10": 0.6, "r11": 0.0, "r12": 0.0})
        assert abs(merged.probabilities["r10"] - 0.6) < 1e-9
        # HMM 4态共享剩余 0.4，各 0.4/4
        for s in HMM_STATES:
            assert abs(merged.probabilities[s] - 0.4 / 4.0) < 1e-9
        assert merged.dominant_regime == "r10"

    def test_normalization_sum1(self, detector: RegimeDetector):
        """覆盖层总概率 >1 时等比压缩回 1.0（blueprint §3.3）。"""
        hmm = {s: 1.0 / 4.0 for s in HMM_STATES}
        # S1 confirm(0.8) + S2 confirm(0.65) 同时 → 总 1.45 > 1
        merged = detector._merge_probabilities(hmm, {"r10": 0.8, "r11": 0.65, "r12": 0.0})
        assert abs(sum(merged.probabilities.values()) - 1.0) < 1e-9
        # r10/r11 等比压缩，比例保持 0.8:0.65
        ratio = merged.probabilities["r10"] / merged.probabilities["r11"]
        assert abs(ratio - 0.8 / 0.65) < 1e-6


# ── 5. ConfidenceSignal ─────────────────────────────────────────────


class TestConfidenceSignal:
    def _probs_with_confidence(self, detector, max_p, freq=0.15):
        """构造指定 max(P) 和 dominant_frequency 的 RegimeProbabilities。"""
        # 把 max_p 放在 r1，其余均分剩余
        rest = (1.0 - max_p) / 11.0
        probs = {s: rest for s in REGIME_STATES}
        probs["r1"] = max_p
        return RegimeProbabilities(
            probabilities=probs, hmm_probabilities={}, overlay_probabilities={},
            dominant_regime="r1", dominant_frequency=freq,
            confidence=max_p, timestamp=datetime.now(),
        )

    @pytest.mark.parametrize("max_p,expected_base", [
        (0.60, 1.0),   # ≥50% → 满部署（4态下0.5已是高置信）
        (0.40, 0.9),   # 30-50% → 轻度收缩
        (0.20, 0.8),   # 15-30% → 中度收缩
        (0.10, 0.7),   # <15% → 强收缩（下限0.7，避免过度压低平时Shrinkage）
    ])
    def test_4_bands(self, detector, max_p, expected_base):
        """四档映射（C1 验证 2026-08-06 校准后阈值，适应 4 态 HMM 概率分散）。

        ConfidenceSignal = base(max_p) × rarity，不含 state_risk（已移除）。
        dominant=r1, freq=0.15(常见态) → rarity=1.0，故 ConfidenceSignal=base。
        """
        p = self._probs_with_confidence(detector, max_p, freq=0.15)  # 常见态
        assert abs(detector._compute_confidence_signal(p) - expected_base) < 1e-9

    @pytest.mark.parametrize("freq,expected_discount", [
        (0.10, 1.0),   # 常见态 >5%
        (0.03, 0.85),  # 中等态 1-5%
        (0.005, 0.7),  # 稀有态 <1%
    ])
    def test_rarity_discount(self, detector, freq, expected_discount):
        """稀有态折扣：max_p=0.90 → base=1.0（≥0.50），ConfidenceSignal=1.0×rarity。"""
        p = self._probs_with_confidence(detector, 0.90, freq=freq)
        assert abs(detector._compute_confidence_signal(p) - 1.0 * expected_discount) < 1e-9

    def test_lower_bound_rare_low_confidence(self, detector):
        """稀有态(<1%) + 低置信(<15%) → 0.7×0.7=0.49（base 下限 0.7 × rarity 下限 0.7）。"""
        p = self._probs_with_confidence(detector, 0.10, freq=0.005)
        assert abs(detector._compute_confidence_signal(p) - 0.49) < 1e-9

    def test_upper_bound_common_high_confidence(self, detector):
        """常见态(>5%) + 高置信(≥50%) → 1.0×1.0=1.0。"""
        p = self._probs_with_confidence(detector, 0.96, freq=0.10)
        assert abs(detector._compute_confidence_signal(p) - 1.0) < 1e-9


# ── 6. RiskSignal ───────────────────────────────────────────────────


class TestRiskSignal:
    def test_base_min_dominant(self, detector, full_risk_params):
        """#1 门控触发后，附加参数 min 聚合生效（§5.3.3 维度6）。

        #1 门控（2026-08-06 二次调优）：#1>=1.0 时附加参数不参与（避免非危机日
        误触发致 Sharpe 退化）。需 #1<1.0 触发门控，附加参数才能经 min 聚合压低 RiskBase。
        """
        params = {**full_risk_params["params"], 1: 0.5, 8: 0.3}  # #1 触发 + 虹吸极端
        r = detector._compute_risk_signal({"params": params})
        # min(0.5, ..., 0.3)=0.3 × 0.95(2异常共振) + 0 = 0.285 → clamp 0.30
        assert abs(r - 0.30) < 0.01

    def test_resonance_penalty(self, detector, full_risk_params):
        """4 异常参数 → 共振惩罚 1-0.05×3=0.85（§5.3.3）。"""
        params = {**full_risk_params["params"], 1: 0.85, 5: 0.85, 9: 0.85, 10: 0.85}
        r = detector._compute_risk_signal({"params": params})
        assert abs(r - 0.72) < 0.02  # 0.85×0.85

    def test_resonance_floor_080(self, detector, full_risk_params):
        """共振惩罚下限 ×0.80（10+ 异常参数，§5.3.3）。"""
        params = {k: 0.6 for k in full_risk_params["params"]}  # 11 个全异常
        r = detector._compute_risk_signal({"params": params})
        # 0.6 × 0.80(下限) + 0 = 0.48
        assert abs(r - 0.48) < 0.02

    def test_opportunity_recovery_cap(self, detector, full_risk_params):
        """机会恢复上限 +0.25（§5.3.2）。"""
        params = {**full_risk_params["params"], 1: 0.6}
        r = detector._compute_risk_signal({
            "params": params,
            "opportunity": {"news_ghost": 0.20, "bad_news_flat": 0.20},  # 合计 0.4 > 上限
        })
        assert abs(r - 0.85) < 0.02  # 0.6×1.0 + 0.25(上限)

    def test_clamp_030_to_100(self, detector, full_risk_params):
        """RiskSignal ∈ [0.30, 1.00]（blueprint §4 INVARIANTS）。"""
        # 下界：RiskBase=0.3 + 无机会 → 0.3
        params = {**full_risk_params["params"], 1: 0.3}
        assert abs(detector._compute_risk_signal({"params": params}) - 0.30) < 0.01
        # 上界：全正常 → 1.0
        assert abs(detector._compute_risk_signal(full_risk_params) - 1.0) < 0.01

    @pytest.mark.financial
    def test_july_case_validation(self, detector, full_risk_params):
        """7月案例 RiskSignal 吻合 §5.3.4：1.0/0.72/0.30/0.85。"""
        full = full_risk_params["params"]
        # 7月上旬：无异常 → 1.0
        assert abs(detector._compute_risk_signal({"params": dict(full)}) - 1.0) < 0.01
        # 7月11-15：4异常 → 0.72
        r = detector._compute_risk_signal({"params": {**full, 1: 0.85, 5: 0.85, 9: 0.85, 10: 0.85}})
        assert abs(r - 0.72) < 0.02
        # 7月17：3异常极端 → 0.30
        r = detector._compute_risk_signal({"params": {**full, 1: 0.3, 7: 0.3, 8: 0.3}})
        assert abs(r - 0.30) < 0.02
        # 8月4：机会恢复 → 0.85
        r = detector._compute_risk_signal({
            "params": {**full, 1: 0.6},
            "opportunity": {"news_ghost": 0.10, "bad_news_flat": 0.15},
        })
        assert abs(r - 0.85) < 0.02

    def test_degraded_when_missing(self, detector: RegimeDetector):
        """RiskSignal 输入缺失 → 1.0（blueprint §7.4 降级）。"""
        assert detector._compute_risk_signal({}) == 1.0
        assert detector._compute_risk_signal(None) == 1.0  # type: ignore[arg-type]


# ── 7. Shrinkage ────────────────────────────────────────────────────


class TestShrinkage:
    def test_enabled_is_product(self, detector: RegimeDetector):
        """shrinkage_enabled=True → value = confidence × risk（§5.2.2）。"""
        s = detector._compute_shrinkage(0.6, 0.7)
        assert s.shrinkage_enabled is True
        assert abs(s.value - 0.42) < 1e-9

    def test_disabled_constant_1(self, detector_off: RegimeDetector):
        """shrinkage_enabled=False → value 恒=1.0（C1 验证基准，11_regime_backtest_validation_plan）。"""
        s = detector_off._compute_shrinkage(0.3, 0.3)
        assert s.shrinkage_enabled is False
        assert s.value == 1.0

    def test_upper_bound_1(self, detector: RegimeDetector):
        """Shrinkage ≤ 1.0（只减不增，blueprint §4 INVARIANTS）。"""
        s = detector._compute_shrinkage(1.0, 1.0)
        assert s.value == 1.0

    def test_lower_bound_rare_crisis(self, detector: RegimeDetector):
        """稀有态+极端风险 → 0.21×0.30=0.063（blueprint §4 下界）。"""
        s = detector._compute_shrinkage(0.21, 0.30)
        assert abs(s.value - 0.063) < 1e-9

    def test_switch_c1_baseline(self, detector, detector_off):
        """C1 开/关对比：同输入下 开<关=1.0（11_regime_backtest_validation_plan 一票否决基准）。"""
        conf, risk = 0.51, 0.85
        s_on = detector._compute_shrinkage(conf, risk)
        s_off = detector_off._compute_shrinkage(conf, risk)
        assert s_on.value < s_off.value == 1.0


# ── 8. TransitionTriggered 事件 ─────────────────────────────────────


class TestTransitionEvents:
    def test_s2_four_stages(self, detector: RegimeDetector):
        """S2 四阶段：trigger/confirm/strong_confirm/fail（§4.12.8）。"""
        t = detector.record_transition("S2", {"capitulation": 65, "vix": 45, "bad_news_flat": 45})
        assert t.stage == "trigger" and t.triggered and not t.confirmed
        t = detector.record_transition("S2", {
            "capitulation": 65, "wyckoff": 65, "vix": 45, "policy": 50,
            "valuation": 45, "bad_news_flat": 45, "fund": 55, "chip": 40})
        assert t.stage == "confirm" and t.confirmed
        t = detector.record_transition("S2", {
            "capitulation": 80, "wyckoff": 70, "vix": 60, "policy": 60, "valuation": 60,
            "bad_news_flat": 60, "fund": 60, "chip": 50, "spring": 1, "three_yang": 1})
        assert t.stage == "strong_confirm"
        t = detector.record_transition("S2", {"break_sc_low": 1, "vix_new_high": 1, "fund_outflow": 1})
        assert t.stage == "fail" and not t.triggered

    def test_score_breakdown_recorded(self, detector: RegimeDetector):
        """评分明细完整记录（B4 验证接口）。"""
        breakdown = {"capitulation": 65, "vix": 45, "bad_news_flat": 45}
        t = detector.record_transition("S2", breakdown)
        assert t.score_breakdown == breakdown
        assert t.total_score == 155.0

    def test_unknown_type_raises(self, detector: RegimeDetector):
        """未知转换类型抛 ValueError（blueprint §3.2）。"""
        with pytest.raises(ValueError):
            detector.record_transition("T9", {"x": 1})

    def test_bad_breakdown_raises(self, detector: RegimeDetector):
        """非 dict 评分抛 OverlayRuleError。"""
        with pytest.raises(OverlayRuleError):
            detector.record_transition("S2", "not a dict")  # type: ignore[arg-type]


# ── 9. 完整链路（端到端）────────────────────────────────────────────


class TestEndToEnd:
    @pytest.mark.financial
    def test_full_chain_s2_confirm_recovery(self, detector, full_risk_params):
        """完整链路：S2 确认 + 底部机会 → dominant=r11(RECOVERY) + Shrinkage 回升（8月4场景）。"""
        overlay = {"transitions": {"S2": {
            "capitulation": 65, "wyckoff": 65, "vix": 45, "policy": 50,
            "valuation": 45, "bad_news_flat": 45, "fund": 55, "chip": 40}}}
        risk = {"params": {**full_risk_params["params"], 1: 0.6},
                "opportunity": {"news_ghost": 0.10, "bad_news_flat": 0.15}}
        probs, shrink = detector.detect({}, overlay, risk)
        assert probs.dominant_regime == "r11"
        # max(P)=0.65 → base 1.0（≥0.50）；r11 freq 0.02 → rarity 0.85 → conf 0.85
        assert abs(shrink.confidence_signal - 0.85) < 0.01
        assert abs(shrink.risk_signal - 0.85) < 0.01
        assert abs(shrink.value - 0.85 * 0.85) < 0.01
        # 转换事件被记录
        assert len(detector._last_transitions) == 1
        assert detector._last_transitions[0].transition_type == "S2"
        assert detector._last_transitions[0].stage == "confirm"

    def test_full_chain_crisis_shrinkage_collapse(self, detector, full_risk_params):
        """完整链路：S1 触发 + 极端风险 → Shrinkage 崩塌至强收缩（7月17场景）。"""
        overlay = {"transitions": {"S1": {"vix_panic": 70, "correlation": 65, "liquidity": 40}}}
        risk = {"params": {**full_risk_params["params"], 1: 0.3, 7: 0.3, 8: 0.3}}
        probs, shrink = detector.detect({}, overlay, risk)
        assert probs.dominant_regime == "r10"  # CRISIS
        assert shrink.risk_signal <= 0.31  # 极端风险
        # conf=1.0(≥0.50)×0.85(r10稀有态)=0.85, risk=0.30 → shrink=0.255（强收缩）
        assert abs(shrink.value - 0.85 * 0.30) < 0.01
