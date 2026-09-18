# [BLUEPRINT] MOD-REGIME-001 | docs/03_modules/_domain_regime/regime_detector/blueprint.md（被测件挂靠）
# [MODULE] tests.regime.test_rb_stats_regime_failopen
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.core.regime_detector
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 本件钉住 regime 供数降级面的两件事：①断供时的 fail-open 数值形态（危机态概率被主腿门清零、RiskSignal=1.0）必须可复现，禁被"看起来正常"掩盖；②ShrinkageResult.degraded_legs 非空 ⇔ RiskSignal 有腿没供上数，且判腿函数与 _compute_risk_signal 的降级分支严格同构；全件合成数据零真库/零 hmmlearn 依赖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""红队 RB-STATS 车道 · regime 断供 fail-open 测试（攻面二）。

钉住的事实（全部由本件机械复现，不靠散文）：
  1. 危机信号已触发（S1 vix_panic/correlation 满格）时，只要 RiskSignal 那条腿
     没供上数，检测器就把 r10 危机概率**清零**、dominant 翻成 r1（低波震荡），
     同时 Shrinkage 从 0.255 松到 0.80 —— 危机中断供=多给约 3.1 倍风险敞口。
  2. "断供"与"确无风险"在 value/risk_signal 上**逐位相同**，故唯一可机检的判别
     载体是 ShrinkageResult.degraded_legs（RB-STATS-02 新增）。
  3. missing_risk_legs 与 _compute_risk_signal 的三条 `return 1.0` 分支严格同构。

R-K9 要求"断供 fail-closed 不允许交易"；本件不擅自改档位数值（那会动已验证的
C1/B 系列历史口径，属总包/Owner 门位），只保证**断供可被机械检出**。
"""

from __future__ import annotations

import logging

import pytest

from zephyr.regime.core.regime_detector import (
    RISK_LEG_INPUTS_ABSENT,
    RISK_LEG_PARAMS_ABSENT,
    RISK_LEG_PRIMARY_ABSENT,
    RegimeDetector,
    missing_risk_legs,
)

# S1 = Any→CRISIS trigger 档（keys_gte: vix_panic>=60 ∧ correlation>=60 → p_overlay r10=0.60）
CRISIS_OVERLAY = {"transitions": {"S1": {"vix_panic": 100.0, "correlation": 100.0, "liquidity": 90.0}}}
RISK_SUPPLIED = {"params": {1: 0.35, 2: 0.4, 3: 0.5, 7: 0.3}, "opportunity": {}}
RISK_TRULY_CALM = {"params": {i: 1.0 for i in range(1, 11)}}  # 主腿有数且确为无风险


def _detect(risk_inputs):
    return RegimeDetector(shrinkage_enabled=True, overlay_gated=True).detect(
        {"X": None}, CRISIS_OVERLAY, risk_inputs
    )


class TestCrisisBlindWhenRiskLegBroken:
    """钉住 fail-open 数值形态 + 新观测位。"""

    def test_crisis_with_risk_data_throttles_hard(self) -> None:
        probs, shr = _detect(RISK_SUPPLIED)
        assert probs.probabilities["r10"] > 0.5, "有供数时危机态概率应显著"
        assert shr.risk_signal < 0.5
        assert shr.value < 0.4
        assert shr.degraded_legs == ()

    def test_crisis_without_risk_data_loosens_and_is_marked(self) -> None:
        probs, shr = _detect({})
        assert probs.probabilities["r10"] == 0.0, "断供时主腿门把危机概率清零（实测形态）"
        assert probs.dominant_regime == "r1", "断供时 dominant 翻成低波震荡（=默认'正常'）"
        assert shr.risk_signal == 1.0 and shr.value > 0.7
        assert shr.degraded_legs, "断供必须被 degraded_legs 检出，否则 R-K9 无从执行"

    def test_break_crisis_throttle_is_3x_looser_than_supplied(self) -> None:
        """断供相对有供数的节流松绑倍数——本数字一变即说明有人动了降级分支。"""
        _p1, supplied = _detect(RISK_SUPPLIED)
        _p2, broken = _detect({})
        assert broken.value / supplied.value > 3.0

    @pytest.mark.parametrize(
        "shape",
        [{}, None, {"params": {}}, {"params": None}, {"opportunity": {}},
         {"params": {1: None}}, {"params": {1: "abc"}}],
    )
    def test_every_no_data_shape_is_marked(self, shape) -> None:
        _probs, shr = _detect(shape)
        assert shr.degraded_legs, f"缺数形态 {shape!r} 未被检出"
        assert shr.risk_signal == 1.0


class TestNoDataVersusNoRiskIndistinguishableByValue:
    """核心病灶：断供与"确无风险"输出逐位相同 ⇒ 唯一判别载体是 degraded_legs。"""

    def test_values_identical_labels_differ(self) -> None:
        _pb, broken = _detect({})
        _pc, calm = _detect(RISK_TRULY_CALM)
        assert broken.value == calm.value and broken.risk_signal == calm.risk_signal
        assert broken.degraded_legs != calm.degraded_legs, "观测位必须区分二者"

    def test_calm_with_primary_data_is_not_marked(self) -> None:
        assert missing_risk_legs(RISK_TRULY_CALM) == ()


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

    def test_every_marked_shape_yields_risk_signal_1(self) -> None:
        det = RegimeDetector()
        for shape in ({}, None, {"params": {}}, {"params": {2: 0.1}}, {"params": {1: None}}):
            if missing_risk_legs(shape):
                assert det._compute_risk_signal(shape) == 1.0, f"{shape!r} 被判缺数却未落 1.0"


class TestDegradationSpeaksOutLoud:
    """六向⑥「失败会响」：断供必须出声，禁静默放行。"""

    def test_warning_logged(self, caplog) -> None:
        with caplog.at_level(logging.WARNING, logger="zephyr.regime.core.regime_detector"):
            _detect({})
        assert any("RB-STATS-02" in r.getMessage() for r in caplog.records), "断供未 WARNING 出声"

    def test_no_warning_when_supplied(self, caplog) -> None:
        with caplog.at_level(logging.WARNING, logger="zephyr.regime.core.regime_detector"):
            _detect(RISK_SUPPLIED)
        assert not any("RB-STATS-02" in r.getMessage() for r in caplog.records)
