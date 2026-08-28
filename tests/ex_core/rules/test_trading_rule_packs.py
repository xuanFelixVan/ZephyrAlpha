# [BLUEPRINT] MOD-EX-RULES-001 | docs/03_modules/_domain_execution_core/blueprint.md | §test
# [MODULE] tests.ex_core.rules.test_trading_rule_packs
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.rules
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_trading_rule_packs.py
# [A_test] module_id: MOD-EX-RULES-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-EX-RULES-001 单元测试: Trading Rule Packs — 交易规则参数化。

覆盖: 工厂方法/A股规则委托收编/币版骨架默认/零行为变化对照。
"""

from __future__ import annotations

from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.ex_core.rules",
    reason="trading rule packs not importable",
)

from zephyr.ex_core.board_lot import get_board_lot_rule as _bl_rule  # noqa: E402
from zephyr.ex_core.price_cage import _get_cage_params as _pc_params  # noqa: E402
from zephyr.ex_core.rules import (  # noqa: E402
    AshareRulePack,
    CryptoRulePack,
    get_trading_rule_pack,
)


class TestRulePackFactory:
    def test_get_ashare_pack(self):
        pack = get_trading_rule_pack("ashare")
        assert isinstance(pack, AshareRulePack)
        assert pack.market == "ashare"

    def test_get_crypto_pack(self):
        pack = get_trading_rule_pack("crypto")
        assert isinstance(pack, CryptoRulePack)
        assert pack.market == "crypto"

    def test_unknown_market_raises(self):
        with pytest.raises(ValueError, match="未知市场"):
            get_trading_rule_pack("unknown")

    def test_factory_returns_singleton(self):
        assert get_trading_rule_pack("ashare") is get_trading_rule_pack("ashare")
        assert get_trading_rule_pack("crypto") is get_trading_rule_pack("crypto")


class TestAshareRulePack:
    def test_settlement_cycle_t1(self):
        assert AshareRulePack().settlement_cycle == 1

    def test_price_tick(self):
        assert AshareRulePack().price_tick == Decimal("0.01")

    def test_lot_rule_matches_board_lot(self):
        """零行为变化：A股规则包委托 board_lot 真源，结果必须一致。"""
        pack = AshareRulePack()
        for symbol in ["600519.SH", "300001.SZ", "688001.SH", "830799.BJ"]:
            rule = pack.lot_rule(symbol)
            expected = _bl_rule(symbol)
            assert rule.min_unit == Decimal(expected.min_unit), f"{symbol} min_unit mismatch"
            assert rule.increment == Decimal(expected.increment), f"{symbol} increment mismatch"

    def test_price_cage_rule_matches_price_cage(self):
        """零行为变化：A股规则包委托 price_cage 真源，结果必须一致。"""
        pack = AshareRulePack()
        for symbol in ["600519.SH", "300001.SZ", "688001.SH", "830799.BJ"]:
            rule = pack.price_cage_rule(symbol)
            expected_pct, expected_floor = _pc_params(symbol)
            assert rule.pct == expected_pct, f"{symbol} pct mismatch"
            assert rule.floor_yuan == expected_floor, f"{symbol} floor_yuan mismatch"

    def test_has_price_cage_true(self):
        assert AshareRulePack().has_price_cage("600519.SH") is True


class TestCryptoRulePack:
    def test_settlement_cycle_t0(self):
        assert CryptoRulePack().settlement_cycle == 0

    def test_price_tick_default(self):
        assert CryptoRulePack().price_tick == Decimal("0.01")

    def test_lot_rule_default(self):
        pack = CryptoRulePack()
        rule = pack.lot_rule("BTC-USDT")
        assert rule.min_unit == Decimal("0.00001")
        assert rule.increment == Decimal("0.00001")

    def test_price_cage_rule_none(self):
        pack = CryptoRulePack()
        rule = pack.price_cage_rule("BTC-USDT")
        assert rule.pct == Decimal("1.0")
        assert rule.floor_yuan is None

    def test_has_price_cage_false(self):
        assert CryptoRulePack().has_price_cage("BTC-USDT") is False

    def test_lot_rule_any_symbol(self):
        """MVP 骨架：任意 symbol 返回默认兜底。"""
        pack = CryptoRulePack()
        for symbol in ["BTC-USDT", "ETH-USDT", "SOL-USDT"]:
            rule = pack.lot_rule(symbol)
            assert rule.min_unit == Decimal("0.00001")
            assert rule.increment == Decimal("0.00001")
