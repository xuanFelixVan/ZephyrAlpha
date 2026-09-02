# [BLUEPRINT] MOD-RK-042 | docs/03_modules/_domain_risk/hedge_execution_skill/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-RK-042 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.risk.test_hedge_execution_skill
# [TESTS] src/zephyr/risk/hedge_execution_skill.py
"""MOD-RK-042 单元测试：hedge_execution_skill 对冲执行技能。

蓝图验收（B11-02591/CAND-RSK-046，A7 技能hedge-execution）：
对冲需求→标的映射（股指期货/ETF词表闭合+基差注入）→腿单生成→执行回调注入→
对冲有效性回写（对冲前后敞口比）+ human_gated 双确认硬约束（风控+人工缺一不执行）。
价格/基差/执行/确认/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.hedge_execution_skill",
    reason="hedge_execution_skill not importable",
)

from zephyr.risk.hedge_execution_skill import (  # noqa: E402
    HedgeEffectiveness,
    HedgeExecutionError,
    HedgeExecutionSkill,
    HedgeInstrumentSpec,
    HedgeInstrumentType,
    HedgeLeg,
    HedgePlan,
    HedgeRequest,
    HedgeStatus,
)

_T0 = datetime.datetime(2026, 8, 25, 14, 30, 0)

_VOCAB = {
    "CSI300": HedgeInstrumentSpec(
        index_code="CSI300",
        future_symbol="IF2609",
        etf_symbol="510300",
        contract_multiplier=Decimal("300"),
    ),
    "CSI500": HedgeInstrumentSpec(
        index_code="CSI500",
        future_symbol="IC2609",
        etf_symbol="510500",
        contract_multiplier=Decimal("200"),
    ),
}

_PRICES = {"IF2609": Decimal("4000"), "IC2609": Decimal("6000"), "510300": Decimal("4"), "510500": Decimal("6")}


def _skill(**overrides) -> HedgeExecutionSkill:
    kwargs = {
        "instrument_vocab": _VOCAB,
        "price_provider": lambda s: _PRICES.get(s),
        "basis_provider": lambda c: Decimal("0"),
        "executor": lambda leg: True,
        "risk_confirmer": lambda plan: True,
        "human_confirmer": lambda plan: True,
        "clock": lambda: _T0,
    }
    kwargs.update(overrides)
    return HedgeExecutionSkill(**kwargs)


def _request(**overrides) -> HedgeRequest:
    kwargs = {
        "request_id": "hr-1",
        "index_code": "CSI300",
        "exposure": Decimal("2400000"),
        "hedge_ratio": Decimal("0.5"),
        "instrument_type": HedgeInstrumentType.STOCK_INDEX_FUTURE,
        "created_at": _T0,
    }
    kwargs.update(overrides)
    return HedgeRequest(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 构造 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_empty_vocab_raises(self) -> None:
        with pytest.raises(HedgeExecutionError):
            HedgeExecutionSkill(instrument_vocab={}, clock=lambda: _T0)

    def test_mismatched_spec_key_raises(self) -> None:
        bad = HedgeInstrumentSpec(
            index_code="OTHER",
            future_symbol="X",
            etf_symbol="Y",
            contract_multiplier=Decimal("300"),
        )
        with pytest.raises(HedgeExecutionError):
            HedgeExecutionSkill(instrument_vocab={"CSI300": bad}, clock=lambda: _T0)

    def test_non_positive_multiplier_raises(self) -> None:
        bad = HedgeInstrumentSpec(
            index_code="CSI300",
            future_symbol="IF",
            etf_symbol="510300",
            contract_multiplier=Decimal("0"),
        )
        with pytest.raises(HedgeExecutionError):
            HedgeExecutionSkill(instrument_vocab={"CSI300": bad}, clock=lambda: _T0)


# ──────────────────────────────────────────────────────────────────────────────
# 腿单生成（标的映射 + 数量计算）
# ──────────────────────────────────────────────────────────────────────────────


class TestPlan:
    def test_future_leg_quantity(self) -> None:
        plan = _skill().plan(_request())
        # 目标名义 = 2400000*0.5 = 1200000；单手 = 4000*300 = 1200000 → 1 手
        assert len(plan.legs) == 1
        leg = plan.legs[0]
        assert leg.symbol == "IF2609"
        assert leg.direction == "sell"
        assert leg.quantity == 1
        assert leg.notional == Decimal("1200000")
        assert plan.total_notional == Decimal("1200000")

    def test_future_leg_rounding_down(self) -> None:
        # 目标名义 1200000，单手 6000*200=1200000 → CSI500 亦 1 手；
        # 敞口改为 1000000 → 目标 500000 → 500000/1200000 = 0 手 → Fail-Closed
        with pytest.raises(HedgeExecutionError):
            _skill().plan(_request(index_code="CSI500", exposure=Decimal("1000000")))

    def test_etf_leg_mapping(self) -> None:
        plan = _skill().plan(_request(instrument_type=HedgeInstrumentType.ETF, exposure=Decimal("120000")))
        leg = plan.legs[0]
        # ETF 乘数 1，价格 4 → 目标名义 60000 → 15000 份
        assert leg.symbol == "510300"
        assert leg.quantity == 15000
        assert leg.notional == Decimal("60000")

    def test_basis_injected_into_plan(self) -> None:
        plan = _skill(basis_provider=lambda c: Decimal("-12.5")).plan(_request())
        assert plan.basis == Decimal("-12.5")

    def test_basis_default_zero_when_not_injected(self) -> None:
        plan = _skill(basis_provider=None).plan(_request())
        assert plan.basis == Decimal("0")

    def test_unknown_index_raises(self) -> None:
        with pytest.raises(HedgeExecutionError):
            _skill().plan(_request(index_code="NASDAQ100"))

    def test_empty_request_id_raises(self) -> None:
        with pytest.raises(HedgeExecutionError):
            _skill().plan(_request(request_id=""))

    def test_non_positive_exposure_raises(self) -> None:
        with pytest.raises(HedgeExecutionError):
            _skill().plan(_request(exposure=Decimal("0")))
        with pytest.raises(HedgeExecutionError):
            _skill().plan(_request(exposure=Decimal("-1")))

    def test_ratio_out_of_range_raises(self) -> None:
        with pytest.raises(HedgeExecutionError):
            _skill().plan(_request(hedge_ratio=Decimal("0")))
        with pytest.raises(HedgeExecutionError):
            _skill().plan(_request(hedge_ratio=Decimal("1.01")))

    def test_price_missing_raises(self) -> None:
        with pytest.raises(HedgeExecutionError):
            _skill(price_provider=lambda s: None).plan(_request())

    def test_price_provider_not_injected_raises(self) -> None:
        with pytest.raises(HedgeExecutionError):
            _skill(price_provider=None).plan(_request())

    def test_plan_deterministic(self) -> None:
        skill = _skill()
        p1 = skill.plan(_request())
        p2 = skill.plan(_request())
        assert p1 == p2


# ──────────────────────────────────────────────────────────────────────────────
# human_gated 双确认硬约束（缺一不执行）
# ──────────────────────────────────────────────────────────────────────────────


class TestDoubleConfirmation:
    def test_execute_ok(self) -> None:
        sent: list[HedgeLeg] = []
        record = _skill(executor=lambda leg: sent.append(leg) or True).execute(_request())
        assert record.status is HedgeStatus.EXECUTED
        assert len(sent) == 1
        assert record.effectiveness is not None

    def test_risk_confirmer_missing_blocks(self) -> None:
        sent: list[HedgeLeg] = []
        record = _skill(risk_confirmer=None, executor=lambda leg: sent.append(leg) or True).execute(_request())
        assert record.status is HedgeStatus.BLOCKED
        assert "风控确认未注入" in record.reason
        assert sent == []  # 缺一不执行

    def test_human_confirmer_missing_blocks(self) -> None:
        sent: list[HedgeLeg] = []
        record = _skill(human_confirmer=None, executor=lambda leg: sent.append(leg) or True).execute(_request())
        assert record.status is HedgeStatus.BLOCKED
        assert "人工确认未注入" in record.reason
        assert sent == []

    def test_risk_reject_blocks(self) -> None:
        record = _skill(risk_confirmer=lambda plan: False).execute(_request())
        assert record.status is HedgeStatus.BLOCKED
        assert "风控确认拒绝" in record.reason

    def test_human_reject_blocks(self) -> None:
        record = _skill(human_confirmer=lambda plan: False).execute(_request())
        assert record.status is HedgeStatus.BLOCKED
        assert "人工确认拒绝" in record.reason

    def test_executor_not_injected_after_confirm_raises(self) -> None:
        with pytest.raises(HedgeExecutionError):
            _skill(executor=None).execute(_request())

    def test_executor_nack_blocked(self) -> None:
        record = _skill(executor=lambda leg: False).execute(_request())
        assert record.status is HedgeStatus.BLOCKED
        assert "执行回调失败" in record.reason

    def test_executor_exception_blocked_not_raised(self) -> None:
        def _boom(leg: HedgeLeg) -> bool:
            raise RuntimeError("执行层宕机")

        record = _skill(executor=_boom).execute(_request())
        assert record.status is HedgeStatus.BLOCKED

    def test_duplicate_request_id_raises(self) -> None:
        skill = _skill()
        skill.execute(_request())
        with pytest.raises(HedgeExecutionError):
            skill.execute(_request())

    def test_confirmer_receives_plan(self) -> None:
        seen: list[HedgePlan] = []
        _skill(risk_confirmer=lambda p: seen.append(p) or True).execute(_request())
        assert len(seen) == 1
        assert seen[0].request_id == "hr-1"


# ──────────────────────────────────────────────────────────────────────────────
# 有效性回写（对冲前后敞口比）
# ──────────────────────────────────────────────────────────────────────────────


class TestEffectiveness:
    def test_effectiveness_full_notional(self) -> None:
        record = _skill().execute(_request())
        eff = record.effectiveness
        assert isinstance(eff, HedgeEffectiveness)
        # 对冲后敞口 = 2400000 - 1200000 = 1200000；有效性 = 1 - 0.5 = 0.5
        assert eff.exposure_before == Decimal("2400000")
        assert eff.exposure_after == Decimal("1200000")
        assert eff.effectiveness == Decimal("0.5")

    def test_effectiveness_basis_reduces_hedge(self) -> None:
        # 基差 -100 → 有效名义 = 1200000 - 100*1 = 1199900
        record = _skill(basis_provider=lambda c: Decimal("-100")).execute(_request())
        eff = record.effectiveness
        assert eff.exposure_after == Decimal("2400000") - Decimal("1199900")

    def test_blocked_record_has_no_effectiveness(self) -> None:
        record = _skill(human_confirmer=None).execute(_request())
        assert record.effectiveness is None

    def test_record_lookup_and_listing(self) -> None:
        skill = _skill()
        skill.execute(_request(request_id="hr-b"))
        skill.execute(_request(request_id="hr-a"))
        assert skill.record_of("hr-a").status is HedgeStatus.EXECUTED
        assert [r.plan.request_id for r in skill.records()] == ["hr-a", "hr-b"]
        with pytest.raises(HedgeExecutionError):
            skill.record_of("ghost")
