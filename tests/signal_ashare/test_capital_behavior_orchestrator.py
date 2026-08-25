# [A_test] module_id: MOD-SIG-088 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-088 | docs/03_modules/_domain_signal/capital_behavior_orchestrator/blueprint.md
# [MODULE] tests.signal_ashare.test_capital_behavior_orchestrator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""C-011 资金行为分析（MOD-SIG-088，B1-00152）施工验证测试。

覆盖：
- 七类主力画像封闭集与观测校验（占比/置信度越界 fail-closed）；
- 合力方向：多空阈值判定、空观测 NEUTRAL、置信度加权；
- 六阶段推演：做多沿主链进一步、末端保持、做空向出货、NEUTRAL 保持、UNKNOWN 处理；
- 预测-复盘自迭代：预测错→类偏置 EMA 修正且限幅，后续 analyze 应用偏置；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.capital_behavior_orchestrator import (
    CalibrationReport,
    CapitalBehaviorConfig,
    CapitalBehaviorOrchestrator,
    CapitalClass,
    CapitalObservation,
    ForceDirection,
)
from zephyr.signal_ashare.institutional_behavior_analyzer import BehaviorPhase


def _obs(
    cls: CapitalClass = CapitalClass.HOT_MONEY,
    net: float = 1000.0,
    part: float = 0.2,
    conf: float = 1.0,
) -> CapitalObservation:
    return CapitalObservation(capital_class=cls, net_inflow=net, participation=part, confidence=conf)


def _orch() -> CapitalBehaviorOrchestrator:
    return CapitalBehaviorOrchestrator(
        CapitalBehaviorConfig(long_threshold=0.15, short_threshold=-0.15, calibration_alpha=0.3)
    )


class TestObservationValidation:
    def test_seven_classes_closed_set(self) -> None:
        assert len(CapitalClass) == 7

    @pytest.mark.parametrize("kw", [{"participation": 1.5}, {"participation": -0.1}, {"confidence": 2.0}, {"confidence": -0.1}])
    def test_invalid_observation_fail_closed(self, kw: dict) -> None:
        base = {"capital_class": CapitalClass.QUANT, "net_inflow": 100.0, "participation": 0.1, "confidence": 1.0}
        base.update(kw)
        with pytest.raises(ValueError):
            CapitalObservation(**base)


class TestConsensus:
    def test_long_consensus(self) -> None:
        c = _orch().analyze(
            "600000.SH",
            [_obs(CapitalClass.HOT_MONEY, 2000.0), _obs(CapitalClass.NORTHBOUND, 1000.0)],
        )
        assert c.direction is ForceDirection.LONG
        assert c.strength == pytest.approx(1.0)
        assert len(c.profiles) == 2

    def test_short_consensus(self) -> None:
        c = _orch().analyze("600000.SH", [_obs(CapitalClass.PUBLIC_FUND, -3000.0)])
        assert c.direction is ForceDirection.SHORT

    def test_neutral_when_empty(self) -> None:
        c = _orch().analyze("600000.SH", [])
        assert c.direction is ForceDirection.NEUTRAL
        assert c.strength == 0.0

    def test_neutral_when_balanced(self) -> None:
        c = _orch().analyze(
            "600000.SH",
            [_obs(CapitalClass.HOT_MONEY, 1000.0), _obs(CapitalClass.RETAIL, -1000.0)],
        )
        assert c.direction is ForceDirection.NEUTRAL

    def test_confidence_weighting(self) -> None:
        # 高置信做多 vs 低置信做空 → 合力偏多
        c = _orch().analyze(
            "600000.SH",
            [
                _obs(CapitalClass.HOT_MONEY, 1000.0, conf=1.0),
                _obs(CapitalClass.RETAIL, -1000.0, conf=0.1),
            ],
        )
        assert c.direction is ForceDirection.LONG
        assert c.strength == pytest.approx((1000 - 100) / 1100)


class TestPhaseInference:
    def test_long_advances_phase(self) -> None:
        c = _orch().analyze("600000.SH", [_obs()], phase=BehaviorPhase.BUILDING)
        assert c.phase is BehaviorPhase.BUILDING
        assert c.expected_next_phase is BehaviorPhase.WASHING

    def test_last_phase_holds(self) -> None:
        c = _orch().analyze("600000.SH", [_obs()], phase=BehaviorPhase.DISTRIBUTING)
        assert c.expected_next_phase is BehaviorPhase.DISTRIBUTING

    def test_short_from_pulling_to_distributing(self) -> None:
        c = _orch().analyze("600000.SH", [_obs(net=-2000.0)], phase=BehaviorPhase.PULLING)
        assert c.expected_next_phase is BehaviorPhase.DISTRIBUTING

    def test_neutral_holds_phase(self) -> None:
        c = _orch().analyze("600000.SH", [], phase=BehaviorPhase.TESTING)
        assert c.expected_next_phase is BehaviorPhase.TESTING

    def test_unknown_phase_long_to_building(self) -> None:
        c = _orch().analyze("600000.SH", [_obs()], phase=BehaviorPhase.UNKNOWN)
        assert c.expected_next_phase is BehaviorPhase.BUILDING


class TestReviewCalibration:
    def test_review_wrong_prediction_adjusts_bias(self) -> None:
        o = _orch()
        cons = o.analyze("600000.SH", [_obs(CapitalClass.HOT_MONEY, 1000.0)])
        rep = o.review(cons, ForceDirection.SHORT)
        assert isinstance(rep, CalibrationReport)
        assert rep.hit is False
        assert CapitalClass.HOT_MONEY in rep.adjusted
        # 复盘后偏置压低同类后续打分
        cons2 = o.analyze("600000.SH", [_obs(CapitalClass.HOT_MONEY, 1000.0)])
        assert cons2.profiles[0].calibrated_bias < 0.0

    def test_review_hit_no_negative_bias(self) -> None:
        o = _orch()
        cons = o.analyze("600000.SH", [_obs(CapitalClass.HOT_MONEY, 1000.0)])
        rep = o.review(cons, ForceDirection.LONG)
        assert rep.hit is True
        assert rep.adjusted == ()

    def test_bias_clipped(self) -> None:
        o = _orch()
        for _ in range(20):
            cons = o.analyze("600000.SH", [_obs(CapitalClass.HOT_MONEY, 1000.0)])
            o.review(cons, ForceDirection.SHORT)
        cons = o.analyze("600000.SH", [_obs(CapitalClass.HOT_MONEY, 1000.0)])
        assert cons.profiles[0].calibrated_bias >= -0.5


class TestContract:
    def test_frozen_and_json(self) -> None:
        c = _orch().analyze("600000.SH", [_obs()])
        with pytest.raises(dataclasses.FrozenInstanceError):
            c.strength = 0.0  # type: ignore[misc]
        json.dumps(c.to_dict(), ensure_ascii=False)

    def test_empty_symbol_rejected(self) -> None:
        with pytest.raises(ValueError):
            _orch().analyze("", [_obs()])
