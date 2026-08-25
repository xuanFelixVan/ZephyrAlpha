# [BLUEPRINT] MOD-POS-024 | docs/03_modules/_domain_position/position_adjudication_center/blueprint.md | §test
# [MODULE] tests.position.test_position_adjudication_center
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.position_adjudication_center
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_position_adjudication_center.py
# [A_test] module_id: MOD-POS-024 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-POS-024 单元测试: C-047 仓位管理唯一裁决中心。

覆盖: 四层全过最保守 min 收敛/任一层拒绝即终审拒绝/层异常 Fail-Closed/
幂等同请求同令牌不重复签发/旁路令牌缺失或不符检测/畸形请求 Fail-Closed。
"""

from __future__ import annotations

import pytest

from zephyr.position.core.position_adjudication_center import (
    AdjudicatedPositionPlan,
    AdjudicationRequest,
    IntendedAction,
    LayerVerdict,
    PositionAdjudicationCenter,
    PositionAdjudicationError,
)


def _req(weight: float = 0.10) -> AdjudicationRequest:
    return AdjudicationRequest(
        request_id="req-001",
        strategy_id="strat_a",
        symbol="000001.SZ",
        action=IntendedAction.ADD,
        intended_weight=weight,
        context={"portfolio_exposure": 0.6},
    )


def _ok(layer: str, weight: float) -> LayerVerdict:
    return LayerVerdict(layer=layer, allowed=True, adjusted_weight=weight, violations=(), reason="ok")


def _deny(layer: str, violation: str) -> LayerVerdict:
    return LayerVerdict(
        layer=layer, allowed=False, adjusted_weight=0.0, violations=(violation,), reason="deny"
    )


def _center_all_ok() -> PositionAdjudicationCenter:
    return PositionAdjudicationCenter(
        portfolio_layer=lambda r: _ok("portfolio", 0.20),
        strategy_layer=lambda r: _ok("strategy", 0.15),
        symbol_layer=lambda r: _ok("symbol", 0.08),
        dynamic_layer=lambda r: _ok("dynamic", 0.12),
    )


class TestRequestValidation:
    def test_weight_bounds(self) -> None:
        with pytest.raises(PositionAdjudicationError):
            _req(weight=1.5)
        with pytest.raises(PositionAdjudicationError):
            _req(weight=-0.1)

    def test_empty_ids_rejected(self) -> None:
        with pytest.raises(PositionAdjudicationError):
            AdjudicationRequest(
                request_id="",
                strategy_id="s",
                symbol="000001.SZ",
                action=IntendedAction.ADD,
                intended_weight=0.1,
                context={},
            )

    def test_context_must_be_mapping(self) -> None:
        with pytest.raises(PositionAdjudicationError):
            AdjudicationRequest(
                request_id="r",
                strategy_id="s",
                symbol="000001.SZ",
                action=IntendedAction.ADD,
                intended_weight=0.1,
                context=["not-a-dict"],
            )


class TestAdjudicate:
    def test_all_pass_conservative_min(self) -> None:
        plan = _center_all_ok().adjudicate(_req())
        assert plan.allowed is True
        assert plan.final_weight == pytest.approx(0.08)  # 最保守收敛=min
        assert [v.layer for v in plan.layer_verdicts] == [
            "portfolio", "strategy", "symbol", "dynamic",
        ]

    def test_any_layer_deny_rejects(self) -> None:
        center = PositionAdjudicationCenter(
            portfolio_layer=lambda r: _ok("portfolio", 0.20),
            strategy_layer=lambda r: _deny("strategy", "BUDGET_EXCEEDED"),
            symbol_layer=lambda r: _ok("symbol", 0.10),
            dynamic_layer=lambda r: _ok("dynamic", 0.10),
        )
        plan = center.adjudicate(_req())
        assert plan.allowed is False
        assert plan.final_weight == 0.0
        assert "BUDGET_EXCEEDED" in plan.layer_verdicts[1].violations

    def test_layer_exception_fail_closed(self) -> None:
        def _boom(_r):
            raise RuntimeError("layer down")

        center = PositionAdjudicationCenter(
            portfolio_layer=lambda r: _ok("portfolio", 0.20),
            strategy_layer=_boom,
            symbol_layer=lambda r: _ok("symbol", 0.10),
            dynamic_layer=lambda r: _ok("dynamic", 0.10),
        )
        plan = center.adjudicate(_req())
        assert plan.allowed is False
        assert plan.final_weight == 0.0
        assert plan.layer_verdicts[1].allowed is False

    def test_idempotent_same_token(self) -> None:
        center = _center_all_ok()
        p1 = center.adjudicate(_req())
        p2 = center.adjudicate(_req())
        assert p1.adjudication_id == p2.adjudication_id
        assert p1 is p2  # 幂等：返回首份裁决不重发令牌

    def test_distinct_request_distinct_token(self) -> None:
        center = _center_all_ok()
        p1 = center.adjudicate(_req())
        p2 = center.adjudicate(
            AdjudicationRequest(
                request_id="req-002",
                strategy_id="strat_a",
                symbol="000002.SZ",
                action=IntendedAction.OPEN,
                intended_weight=0.05,
                context={},
            )
        )
        assert p1.adjudication_id != p2.adjudication_id


class TestBypass:
    def test_missing_token_is_bypass(self) -> None:
        center = _center_all_ok()
        center.adjudicate(_req())
        assert center.verify_bypass(_req(), token=None) is True

    def test_wrong_token_is_bypass(self) -> None:
        center = _center_all_ok()
        center.adjudicate(_req())
        assert center.verify_bypass(_req(), token="deadbeefdeadbeef") is True

    def test_valid_token_not_bypass(self) -> None:
        center = _center_all_ok()
        plan = center.adjudicate(_req())
        assert center.verify_bypass(_req(), token=plan.adjudication_id) is False

    def test_unadjudicated_request_is_bypass(self) -> None:
        center = _center_all_ok()
        assert center.verify_bypass(_req(), token="anything12345678") is True
