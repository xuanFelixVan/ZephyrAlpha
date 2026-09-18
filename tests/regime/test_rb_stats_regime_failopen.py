# [BLUEPRINT] MOD-REGIME-001 | docs/03_modules/_domain_regime/regime_detector/blueprint.md（被测件挂靠）
# [MODULE] tests.regime.test_rb_stats_regime_failopen
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.core.regime_detector
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 本件钉住 regime 供数降级面的三件事：①R-055a 数值侧 fail-closed——断供时 RiskSignal 落地板值、危机概率不得被主腿门清零，Shrinkage 只会收紧禁放量；②ShrinkageResult.degraded_legs 非空 ⇔ RiskSignal 有腿没供上数，且判腿函数与 _compute_risk_signal 的降级分支严格同构；③降级必须带 risk_signal_source 溯源，与"13 参数全正常"三者皆可区分；全件合成数据零真库/零 hmmlearn 依赖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""红队 RB-STATS 车道 · regime 断供 fail-closed 测试（攻面二，R-055a 已落地）。

钉住的事实（全部由本件机械复现，不靠散文）：
  1. **改前病灶（留档，防回退）**：危机信号已触发（S1 vix_panic/correlation 满格）时
     只要 RiskSignal 那条腿没供上数，检测器就把 r10 危机概率清零、dominant 翻成 r1，
     Shrinkage 从 0.255 松到 0.80 = 危机中断供反而多给 3.14 倍敞口，且 `{}`/None/
     `{"params":{}}`/缺 #1 与"13 参数全正常"输出**逐位相同**。
  2. **R-055a 现行（方向=加严）**：缺数即 RiskSignal 落 RISK_SIGNAL_FLOOR(0.30)、
     覆盖层危机概率**保留**（主腿门要求正证据），Shrinkage 断供 ≤ 有供数，
     并由 degraded_legs + risk_signal_source 双字段区分"降级"与"正常"。
  3. missing_risk_legs 与 _compute_risk_signal 的降级分支严格同构。

R-K9"断供 fail-closed 不允许交易"的数值侧落点 = 本件；选型对齐房内正例
`pf_alloc/allocation_inputs.py::resolve_risk_signal`（无教材→总节流最深档 + 溯源标签）。
"""

from __future__ import annotations

import logging

import pytest

from zephyr.regime.core.regime_detector import (
    RISK_LEG_INPUTS_ABSENT,
    RISK_LEG_PARAMS_ABSENT,
    RISK_LEG_PRIMARY_ABSENT,
    RISK_SIGNAL_FLOOR,
    RISK_SOURCE_NEUTRAL_FAIL_CLOSED,
    RISK_SOURCE_SUPPLIED,
    RegimeDetector,
    missing_risk_legs,
)

# S1 = Any→CRISIS trigger 档（keys_gte: vix_panic>=60 ∧ correlation>=60 → p_overlay r10=0.60）
CRISIS_OVERLAY = {"transitions": {"S1": {"vix_panic": 100.0, "correlation": 100.0, "liquidity": 90.0}}}
NO_OVERLAY: dict = {"transitions": {}}
RISK_SUPPLIED = {"params": {1: 0.35, 2: 0.4, 3: 0.5, 7: 0.3}, "opportunity": {}}
RISK_TRULY_CALM = {"params": {i: 1.0 for i in range(1, 11)}}  # 主腿有数且确为无风险


def _detect(risk_inputs, overlay=CRISIS_OVERLAY):
    return RegimeDetector(shrinkage_enabled=True, overlay_gated=True).detect(
        {"X": None}, overlay, risk_inputs
    )


class TestCrisisFailsClosedWhenRiskLegBroken:
    """R-055a 能红判据①：断腿 ⇒ Shrinkage 收紧，绝不放量。"""

    def test_crisis_with_risk_data_throttles_hard(self) -> None:
        probs, shr = _detect(RISK_SUPPLIED)
        assert probs.probabilities["r10"] > 0.5, "有供数时危机态概率应显著"
        assert shr.risk_signal < 0.5
        assert shr.value == pytest.approx(0.255), "正常路径数值零漂移（加严不许顺手改坏有数路径）"
        assert shr.degraded_legs == ()
        assert shr.risk_signal_source == RISK_SOURCE_SUPPLIED

    @pytest.mark.parametrize(
        "shape",
        [{}, None, {"params": {}}, {"params": None}, {"opportunity": {}},
         {"params": {1: None}}, {"params": {1: "abc"}}, {"params": {2: 0.1, 3: 0.1}}],
    )
    def test_no_data_shape_throttles_not_loosens(self, shape) -> None:
        """红队判据①：断一条腿 ⇒ Shrinkage 必须**收紧**（≤有供数危机值），不得放量 3.14×。"""
        probs, supplied = _detect(RISK_SUPPLIED)
        _p, shr = _detect(shape)
        assert shr.risk_signal == pytest.approx(RISK_SIGNAL_FLOOR), f"缺数形态 {shape!r} 未落 fail-closed 地板值"
        assert shr.value <= supplied.value + 1e-12, "断供反而放量=fail-open 回退"
        assert shr.value < 0.4, "断供必须落危机级节流（0.30 档），不是 0.80 的松绑档"
        assert shr.degraded_legs, f"缺数形态 {shape!r} 未被 degraded_legs 检出"
        assert shr.risk_signal_source == RISK_SOURCE_NEUTRAL_FAIL_CLOSED

    def test_crisis_probability_survives_supply_loss(self) -> None:
        """红队判据①的机制侧：主腿门不再把"没数"读成"没风险"——r10 危机概率必须保留。"""
        probs, shr = _detect({})
        assert probs.probabilities["r10"] > 0.5, "断供时危机概率被清零=fail-open（R-055a 已治，禁回退）"
        assert probs.dominant_regime == "r10", "断供不得把 dominant 从危机态翻成低波震荡"
        assert "crisis_overlay_preserved_no_primary_evidence" in shr.degraded_legs

    def test_calm_with_positive_evidence_still_shields_overlay(self) -> None:
        """对照面（防把门做成永久拆掉）：主腿**真的**报了 #1≥1.0 时仍按 #ARCH-REGIME-OVERLAY-001 屏蔽。"""
        probs, shr = _detect(RISK_TRULY_CALM)
        assert probs.probabilities["r10"] == 0.0, "有正证据的平静期仍应屏蔽 overlay 注入"
        assert shr.risk_signal == 1.0
        assert shr.risk_signal_source == RISK_SOURCE_SUPPLIED


class TestNoDataVersusNoRiskDistinguishable:
    """红队判据②③：`{}` 与"13 参数全正常"必须**可区分**，且降级必须带可溯源字段。"""

    def test_values_now_differ_and_labels_differ(self) -> None:
        _pb, broken = _detect({}, overlay=NO_OVERLAY)
        _pc, calm = _detect(RISK_TRULY_CALM, overlay=NO_OVERLAY)
        assert broken.value != calm.value, "改前此处逐位相同（fail-open 温床），现在必须不同"
        assert broken.value < calm.value, "断供侧必须比平静侧更紧"
        assert broken.degraded_legs != calm.degraded_legs
        assert broken.risk_signal_source == RISK_SOURCE_NEUTRAL_FAIL_CLOSED
        assert calm.risk_signal_source == RISK_SOURCE_SUPPLIED

    def test_calm_with_primary_data_is_not_marked(self) -> None:
        assert missing_risk_legs(RISK_TRULY_CALM) == ()

    def test_degraded_legs_always_nonempty_when_no_data(self) -> None:
        for shape in ({}, None, {"params": {}}, {"params": {1: None}}, {"params": {2: 0.1}}):
            _p, shr = _detect(shape)
            assert shr.degraded_legs, f"缺数形态 {shape!r} 未被检出"


class TestMissingLegsIsomorphicWithRiskSignal:
    """判腿函数与 _compute_risk_signal 的降级分支同构（改一边必红另一边）。"""

    @pytest.mark.parametrize(
        "shape,expected",
        [
            ({}, (RISK_LEG_INPUTS_ABSENT,)),
            (None, (RISK_LEG_INPUTS_ABSENT,)),
            ({"opportunity": {}}, (RISK_LEG_PARAMS_ABSENT,)),
            ({"params": {}}, (RISK_LEG_PARAMS_ABSENT,)),
            ({"params": {2: 0.1, 3: 0.1}}, (RISK_LEG_PRIMARY_ABSENT,)),
            ({"params": {1: 0.35}}, ()),
            (RISK_TRULY_CALM, ()),
        ],
    )
    def test_leg_labels(self, shape, expected) -> None:
        assert missing_risk_legs(shape) == expected

    def test_marked_shapes_yield_floor_unmarked_keep_aggregation(self) -> None:
        det = RegimeDetector()
        for shape in ({}, None, {"params": {}}, {"params": {2: 0.1}}, {"params": {1: None}}):
            assert missing_risk_legs(shape), shape
            assert det._compute_risk_signal(shape) == RISK_SIGNAL_FLOOR, f"{shape!r} 缺数却未落地板值"
        # 未标记（主腿有数）⇒ 走原聚合语义，不许被 fail-closed 兜底吞掉
        assert det._compute_risk_signal(RISK_TRULY_CALM) == 1.0
        assert det._compute_risk_signal(RISK_SUPPLIED) < 0.5
        assert det._compute_risk_signal({"params": {1: 0.9}}) == pytest.approx(0.9)


class TestDegradationSpeaksOutLoud:
    """六向⑥「失败会响」：断供必须出声，禁静默放行。"""

    def test_warning_logged(self, caplog) -> None:
        with caplog.at_level(logging.WARNING, logger="zephyr.regime.core.regime_detector"):
            _detect({})
        msgs = [r.getMessage() for r in caplog.records]
        assert any("RB-STATS-02" in m for m in msgs), "断供未 WARNING 出声"
        assert any("neutral_fail_closed" in m for m in msgs), "降级出声须带溯源标签"

    def test_no_warning_when_supplied(self, caplog) -> None:
        with caplog.at_level(logging.WARNING, logger="zephyr.regime.core.regime_detector"):
            _detect(RISK_SUPPLIED)
        assert not any("RB-STATS-02" in r.getMessage() for r in caplog.records)
