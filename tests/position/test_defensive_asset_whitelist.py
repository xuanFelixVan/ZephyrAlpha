# [BLUEPRINT] MOD-POS-026 | docs/03_modules/_domain_position/defensive_asset_whitelist/blueprint.md
# [DOMAIN] D_POSITION
# [TTL] permanent
"""MOD-POS-026 defensive_asset_whitelist 单元测试（红蓝对抗：红-边界/红-契约/红-故障姿态）。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.position.core.defensive_asset_whitelist import (
    DEFAULT_CONFIG,
    CircuitLevel,
    DefensiveAdditionRequest,
    DefensiveWhitelistConfig,
    DefensiveWhitelistError,
    Direction,
    NationalTeamSignal,
    ReasonCode,
    ReversalSignal,
    WhitelistTier,
    evaluate_defensive_addition,
)


def _req(**overrides) -> DefensiveAdditionRequest:
    """完美条件请求（全门满足），仅休眠默认挡住——按需覆写制造败因。"""
    base = dict(
        symbol="510300",
        direction=Direction.BUY,
        circuit_level=CircuitLevel.L2,
        reversal=ReversalSignal(kdj_j=-12.5, volume_ratio=2.4, systemic_bad_news=False),
        nt_signal=NationalTeamSignal.NONE,
        reserve_budget=Decimal("30000"),
        total_capital=Decimal("500000"),
        deployed_amount=Decimal("0"),
        tranches_done=0,
        confirm_recovered=False,
    )
    base.update(overrides)
    return DefensiveAdditionRequest(**base)


_ENABLED = DefensiveWhitelistConfig(enabled=True)


class TestDormantIronRule:
    """D114 休眠铁律：默认配置恒拒（fail-closed 姿态）。"""

    def test_default_config_is_dormant(self):
        assert DEFAULT_CONFIG.enabled is False

    def test_dormant_rejects_perfect_conditions(self):
        v = evaluate_defensive_addition(_req())  # 其余全门满足
        assert v.allowed is False
        assert v.reason_codes == (ReasonCode.DORMANT,)
        assert v.tier is None and v.tranche is None

    def test_dormant_rejects_even_l4_and_sell(self):
        v = evaluate_defensive_addition(_req(circuit_level=CircuitLevel.L4, direction="SELL"))
        assert v.reason_codes == (ReasonCode.DORMANT,)


class TestDirectionAndWhitelist:
    """门a 方向=买入核对 + 门b 白名单来源固化。"""

    def test_sell_rejected(self):
        v = evaluate_defensive_addition(_req(direction=Direction.SELL), _ENABLED)
        assert v.allowed is False
        assert v.reason_codes == (ReasonCode.DIRECTION_NOT_BUY,)

    @pytest.mark.parametrize("symbol,tier", [
        ("510300", WhitelistTier.T1_BROAD_ETF),
        ("512100", WhitelistTier.T1_BROAD_ETF),
        ("510880", WhitelistTier.T1_BROAD_ETF),
        ("512800", WhitelistTier.T2_BANK_DIVIDEND),
        ("512890", WhitelistTier.T2_BANK_DIVIDEND),
    ])
    def test_whitelist_tiers(self, symbol, tier):
        v = evaluate_defensive_addition(_req(symbol=symbol), _ENABLED)
        assert v.allowed is True
        assert v.tier is tier

    def test_off_whitelist_rejected(self):
        v = evaluate_defensive_addition(_req(symbol="600519"), _ENABLED)
        assert v.reason_codes == (ReasonCode.NOT_WHITELISTED,)

    def test_tier2_rejected_when_removed_from_config(self):
        cfg = DefensiveWhitelistConfig(enabled=True, tier2=())
        v = evaluate_defensive_addition(_req(symbol="512800"), cfg)
        assert v.reason_codes == (ReasonCode.NOT_WHITELISTED,)


class TestLevelGate:
    """门① 状态门：只有 L2/L3 开窄门。"""

    @pytest.mark.parametrize("level", [CircuitLevel.L0, CircuitLevel.L1, CircuitLevel.L4])
    def test_non_l2_l3_rejected(self, level):
        v = evaluate_defensive_addition(_req(circuit_level=level), _ENABLED)
        assert v.reason_codes == (ReasonCode.LEVEL_GATE_FAIL,)

    @pytest.mark.parametrize("level", [CircuitLevel.L2, CircuitLevel.L3])
    def test_l2_l3_pass(self, level):
        v = evaluate_defensive_addition(_req(circuit_level=level), _ENABLED)
        assert v.allowed is True


class TestSignalGate:
    """门② 信号门：D110 三组件合成 或 国家队明牌。"""

    def test_d110_requires_kdj_below_threshold(self):
        v = evaluate_defensive_addition(
            _req(reversal=ReversalSignal(kdj_j=-10.0, volume_ratio=2.4)), _ENABLED
        )
        # J=-10 不严格小于 -10 → D110 不成立，国家队也无 → 信号门败
        assert v.reason_codes == (ReasonCode.SIGNAL_GATE_FAIL,)

    def test_d110_requires_volume_above_two(self):
        v = evaluate_defensive_addition(
            _req(reversal=ReversalSignal(kdj_j=-12.0, volume_ratio=2.0)), _ENABLED
        )
        assert v.reason_codes == (ReasonCode.SIGNAL_GATE_FAIL,)

    def test_d110_rejected_on_systemic_bad_news(self):
        v = evaluate_defensive_addition(
            _req(reversal=ReversalSignal(kdj_j=-12.0, volume_ratio=2.4, systemic_bad_news=True)),
            _ENABLED,
        )
        assert v.reason_codes == (ReasonCode.SIGNAL_GATE_FAIL,)

    def test_nt_signal_alone_passes(self):
        v = evaluate_defensive_addition(
            _req(
                reversal=ReversalSignal(kdj_j=5.0, volume_ratio=0.8),
                nt_signal=NationalTeamSignal.ETF_VOLUME_SURGE,
            ),
            _ENABLED,
        )
        assert v.allowed is True

    def test_official_announcement_alone_passes(self):
        v = evaluate_defensive_addition(
            _req(
                reversal=ReversalSignal(kdj_j=5.0, volume_ratio=0.8),
                nt_signal=NationalTeamSignal.OFFICIAL_ANNOUNCEMENT,
            ),
            _ENABLED,
        )
        assert v.allowed is True


class TestTrancheGate:
    """门③ 分批门：首笔 1/3；第 2/3 笔须确认收复；上限 3 笔。"""

    def test_first_tranche_needs_no_confirmation(self):
        v = evaluate_defensive_addition(_req(tranches_done=0), _ENABLED)
        assert v.allowed is True
        assert v.tranche.tranche_no == 1

    def test_second_tranche_blocked_without_confirmation(self):
        v = evaluate_defensive_addition(_req(tranches_done=1, confirm_recovered=False), _ENABLED)
        assert v.reason_codes == (ReasonCode.CONFIRMATION_REQUIRED,)

    def test_second_tranche_allowed_with_confirmation(self):
        v = evaluate_defensive_addition(_req(tranches_done=1, confirm_recovered=True), _ENABLED)
        assert v.allowed is True
        assert v.tranche.tranche_no == 2

    def test_third_tranche_limit_boundary(self):
        v = evaluate_defensive_addition(_req(tranches_done=3, confirm_recovered=True), _ENABLED)
        assert v.reason_codes == (ReasonCode.TRANCHE_LIMIT_REACHED,)

    def test_custom_max_tranches(self):
        cfg = DefensiveWhitelistConfig(enabled=True, max_tranches=1)
        v = evaluate_defensive_addition(_req(tranches_done=1, confirm_recovered=True), cfg)
        assert v.reason_codes == (ReasonCode.TRANCHE_LIMIT_REACHED,)


class TestBudgetGate:
    """预算闸：cap=min(尾部弹药, 总资金×10%)；首笔=cap/3 向下取分；耗尽拒。"""

    def test_cap_takes_min_of_reserve_and_capital_cap(self):
        # 总资金 500000 × 10% = 50000 > 尾部弹药 30000 → cap=30000，首笔=10000.00
        v = evaluate_defensive_addition(_req(), _ENABLED)
        assert v.allowed is True
        assert v.tranche.amount == Decimal("10000.00")
        assert v.remaining_budget == Decimal("20000.00")

    def test_cap_bounded_by_capital_when_reserve_huge(self):
        # 尾部弹药 1000000 > 总资金 500000×10%=50000 → cap=50000，首笔=16666.66
        v = evaluate_defensive_addition(
            _req(reserve_budget=Decimal("1000000")), _ENABLED
        )
        assert v.tranche.amount == Decimal("16666.66")

    def test_budget_exhausted(self):
        v = evaluate_defensive_addition(
            _req(reserve_budget=Decimal("900"), deployed_amount=Decimal("900")), _ENABLED
        )
        assert v.reason_codes == (ReasonCode.BUDGET_EXHAUSTED,)
        assert v.remaining_budget == Decimal("0.00")

    def test_tiny_remaining_rounds_to_reject(self):
        # cap=1.00，首笔=0.33，deployed=0.90 → remaining=0.10 < 0.33 → amount=0.10 放行
        v = evaluate_defensive_addition(
            _req(reserve_budget=Decimal("1.00"), deployed_amount=Decimal("0.90")), _ENABLED
        )
        assert v.allowed is True
        assert v.tranche.amount == Decimal("0.10")

    def test_deployed_beyond_cap_rejected(self):
        v = evaluate_defensive_addition(
            _req(deployed_amount=Decimal("30001")), _ENABLED
        )
        assert v.reason_codes == (ReasonCode.BUDGET_EXHAUSTED,)


class TestFailClosedContract:
    """红-契约：Decimal-only、非法输入 fail-closed、纯函数确定性。"""

    @pytest.mark.parametrize("field,value", [
        ("reserve_budget", 30000.0),
        ("total_capital", 500000),
        ("deployed_amount", 0),
    ])
    def test_float_and_int_amounts_rejected(self, field, value):
        with pytest.raises(DefensiveWhitelistError):
            evaluate_defensive_addition(_req(**{field: value}), _ENABLED)

    def test_bool_amount_rejected(self):
        with pytest.raises(DefensiveWhitelistError):
            evaluate_defensive_addition(_req(reserve_budget=True), _ENABLED)

    def test_negative_amounts_rejected(self):
        with pytest.raises(DefensiveWhitelistError):
            evaluate_defensive_addition(_req(reserve_budget=Decimal("-1")), _ENABLED)
        with pytest.raises(DefensiveWhitelistError):
            evaluate_defensive_addition(_req(deployed_amount=Decimal("-0.01")), _ENABLED)
        with pytest.raises(DefensiveWhitelistError):
            evaluate_defensive_addition(_req(tranches_done=-1), _ENABLED)

    def test_zero_capital_rejected(self):
        with pytest.raises(DefensiveWhitelistError):
            evaluate_defensive_addition(_req(total_capital=Decimal("0")), _ENABLED)

    def test_empty_symbol_rejected(self):
        with pytest.raises(DefensiveWhitelistError):
            evaluate_defensive_addition(_req(symbol=""), _ENABLED)

    def test_unknown_enum_values_rejected(self):
        with pytest.raises(DefensiveWhitelistError):
            evaluate_defensive_addition(_req(direction="HOLD"), _ENABLED)
        with pytest.raises(DefensiveWhitelistError):
            evaluate_defensive_addition(_req(circuit_level="L9"), _ENABLED)
        with pytest.raises(DefensiveWhitelistError):
            evaluate_defensive_addition(_req(nt_signal="RUMOR"), _ENABLED)

    def test_config_validation(self):
        with pytest.raises(DefensiveWhitelistError):
            DefensiveWhitelistConfig(enabled=True, max_total_pct=Decimal("0.15"))  # 超 D114 上限
        with pytest.raises(DefensiveWhitelistError):
            DefensiveWhitelistConfig(enabled=True, tranche_numer=3, tranche_denom=1)
        with pytest.raises(DefensiveWhitelistError):
            DefensiveWhitelistConfig(enabled=True, max_tranches=0)
        with pytest.raises(DefensiveWhitelistError):
            DefensiveWhitelistConfig(enabled=True, max_total_pct=0.10)  # float 拒

    def test_determinism(self):
        r1 = evaluate_defensive_addition(_req(), _ENABLED)
        r2 = evaluate_defensive_addition(_req(), _ENABLED)
        assert r1 == r2

    def test_verdict_is_frozen(self):
        v = evaluate_defensive_addition(_req(), _ENABLED)
        with pytest.raises(Exception):
            v.allowed = False
