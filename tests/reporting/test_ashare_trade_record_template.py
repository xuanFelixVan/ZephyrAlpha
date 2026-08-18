# [BLUEPRINT] MOD-RPT-027 | docs/03_modules/_domain_reporting/ashare_trade_record_template/blueprint.md
# [MODULE] tests.reporting.test_ashare_trade_record_template
# [DOMAIN] D_REPORTING
# [INVARIANTS] 11必填字段强制校验; amount=quantity×price; stamp_duty仅SELL>0; quantity为100整数倍; frozen不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTradeRecordError(ZA-RPT-0005)
# [TESTS] self
# [A_module] module_id=MOD-RPT-027 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-027 A股交易记录模板引擎 单元测试.

覆盖（blueprint §7）:
  - 11字段完整校验: 每字段缺/类型错/值非法
  - amount一致性: amount ≠ qty×price 拒绝
  - 印花税规则: BUY时stamp_duty>0拒绝
  - quantity规则: 非100整数倍拒绝
  - 模板版本: get_required_fields/get_template_version
  - frozen不可变 / 类型 coercion
"""

from __future__ import annotations

import dataclasses
from decimal import Decimal

import pytest

from zephyr.reporting.ashare_trade_record_template import (
    AShareTradeRecordTemplate,
    InvalidTradeRecordError,
    TradeRecordEntry,
)

# ── 辅助构造 ──


def make_valid_entry(**overrides) -> dict:
    """构造合法的 11 字段交易记录字典。"""
    base = {
        "trade_date": "2026-08-02",
        "symbol": "600000",
        "side": "BUY",
        "quantity": "100",
        "price": "10.00",
        "amount": "1000.00",
        "commission": "5.00",
        "stamp_duty": "0",
        "transfer_fee": "0.10",
        "strategy_id": "S001",
        "account_id": "A001",
    }
    base.update(overrides)
    return base


# ── 合法记录测试 ──


class TestValidEntry:
    def test_valid_buy_entry(self) -> None:
        """合法买入记录。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry())
        assert entry.trade_date == "2026-08-02"
        assert entry.symbol == "600000"
        assert entry.side == "BUY"
        assert entry.quantity == Decimal("100")
        assert entry.price == Decimal("10.00")
        assert entry.amount == Decimal("1000.00")
        assert entry.commission == Decimal("5.00")
        assert entry.stamp_duty == Decimal("0")
        assert entry.transfer_fee == Decimal("0.10")
        assert entry.strategy_id == "S001"
        assert entry.account_id == "A001"
        assert entry.schema_version == "1.0"

    def test_valid_sell_entry(self) -> None:
        """合法卖出记录(含印花税)。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(
            side="SELL",
            stamp_duty="0.50",
        ))
        assert entry.side == "SELL"
        assert entry.stamp_duty == Decimal("0.50")

    def test_side_case_insensitive(self) -> None:
        """side 大小写不敏感。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(side="buy"))
        assert entry.side == "BUY"

    def test_quantity_large_lot(self) -> None:
        """大批量(1000股)。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(
            quantity="1000",
            amount="10000.00",
        ))
        assert entry.quantity == Decimal("1000")

    def test_int_values_coerced(self) -> None:
        """int 值自动转 Decimal。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(
            quantity=100,
            price=10,
            amount=1000,
            commission=5,
            stamp_duty=0,
            transfer_fee=0,
        ))
        assert entry.quantity == Decimal("100")
        assert entry.price == Decimal("10")

    def test_float_values_coerced(self) -> None:
        """float 值自动转 Decimal。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(
            quantity=100.0,
            price=10.5,
            amount=1050.0,
            commission=5.0,
            stamp_duty=0.0,
            transfer_fee=0.1,
        ))
        assert entry.price == Decimal("10.5")
        assert entry.amount == Decimal("1050.0")

    def test_decimal_values_pass_through(self) -> None:
        """Decimal 值直接通过。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(
            quantity=Decimal("200"),
            price=Decimal("15.50"),
            amount=Decimal("3100.00"),
        ))
        assert entry.quantity == Decimal("200")
        assert entry.price == Decimal("15.50")

    def test_strategy_id_whitespace_stripped(self) -> None:
        """strategy_id 前后空白去除。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(strategy_id="  S001  "))
        assert entry.strategy_id == "S001"


# ── 缺字段测试 ──


class TestMissingFields:
    @pytest.mark.parametrize("missing_field", [
        "trade_date", "symbol", "side", "quantity", "price",
        "amount", "commission", "stamp_duty", "transfer_fee",
        "strategy_id", "account_id",
    ])
    def test_missing_each_field(self, missing_field: str) -> None:
        """缺任一必填字段拒绝。"""
        tpl = AShareTradeRecordTemplate()
        entry = make_valid_entry()
        del entry[missing_field]
        with pytest.raises(InvalidTradeRecordError) as exc_info:
            tpl.validate(entry)
        assert exc_info.value.error_code == "ZA-RPT-0005"
        assert missing_field in exc_info.value.message


# ── 字段格式校验 ──


class TestFieldFormat:
    def test_trade_date_wrong_format(self) -> None:
        """trade_date 格式错。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(trade_date="2026/08/02"))

    def test_trade_date_not_string(self) -> None:
        """trade_date 非字符串。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(trade_date=20260802))

    def test_symbol_wrong_length(self) -> None:
        """symbol 非6位。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(symbol="60000"))

    def test_symbol_non_numeric(self) -> None:
        """symbol 含非数字。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(symbol="60000A"))

    def test_side_invalid(self) -> None:
        """side 非法值。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(side="HOLD"))

    def test_strategy_id_empty(self) -> None:
        """strategy_id 空串拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(strategy_id=""))

    def test_strategy_id_whitespace_only(self) -> None:
        """strategy_id 纯空白拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(strategy_id="   "))

    def test_account_id_empty(self) -> None:
        """account_id 空串拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(account_id=""))


# ── 数值校验 ──


class TestNumericValidation:
    def test_quantity_zero(self) -> None:
        """quantity=0 拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(quantity="0", amount="0.00"))

    def test_quantity_negative(self) -> None:
        """quantity 负数拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(quantity="-100", amount="-1000.00"))

    def test_quantity_not_lot_multiple(self) -> None:
        """quantity 非100整数倍拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError) as exc_info:
            tpl.validate(make_valid_entry(
                quantity="150",
                amount="1500.00",
            ))
        assert "100" in exc_info.value.message

    def test_price_zero(self) -> None:
        """price=0 拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(price="0", amount="0.00"))

    def test_price_negative(self) -> None:
        """price 负数拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(price="-10", amount="-1000.00"))

    def test_commission_negative(self) -> None:
        """commission 负数拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(commission="-5"))

    def test_stamp_duty_negative(self) -> None:
        """stamp_duty 负数拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(stamp_duty="-1"))

    def test_transfer_fee_negative(self) -> None:
        """transfer_fee 负数拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(transfer_fee="-0.1"))


# ── 业务规则校验 ──


class TestBusinessRules:
    def test_amount_mismatch(self) -> None:
        """amount ≠ quantity × price 拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError) as exc_info:
            tpl.validate(make_valid_entry(
                quantity="100",
                price="10.00",
                amount="999.00",  # 应为 1000.00
            ))
        assert "amount" in exc_info.value.message.lower() or "不一致" in exc_info.value.message

    def test_amount_mismatch_large(self) -> None:
        """amount 严重不一致拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(
                quantity="100",
                price="10.00",
                amount="5000.00",
            ))

    def test_stamp_duty_on_buy_rejected(self) -> None:
        """买入时 stamp_duty>0 拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError) as exc_info:
            tpl.validate(make_valid_entry(
                side="BUY",
                stamp_duty="0.50",
            ))
        assert "stamp_duty" in exc_info.value.message

    def test_stamp_duty_zero_on_buy_ok(self) -> None:
        """买入时 stamp_duty=0 通过。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(side="BUY", stamp_duty="0"))
        assert entry.stamp_duty == Decimal("0")

    def test_stamp_duty_positive_on_sell_ok(self) -> None:
        """卖出时 stamp_duty>0 通过。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(
            side="SELL",
            stamp_duty="0.50",
        ))
        assert entry.stamp_duty == Decimal("0.50")

    def test_stamp_duty_zero_on_sell_ok(self) -> None:
        """卖出时 stamp_duty=0 也通过(免税场景)。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(side="SELL", stamp_duty="0"))
        assert entry.stamp_duty == Decimal("0")

    def test_amount_consistent_with_decimal_precision(self) -> None:
        """amount 一致性含小数精度。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry(
            quantity="200",
            price="15.50",
            amount="3100.00",
        ))
        assert entry.amount == Decimal("3100.00")


# ── 类型与入口校验 ──


class TestEntryType:
    def test_non_dict_entry(self) -> None:
        """entry 非 dict 拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate([1, 2, 3])  # type: ignore[arg-type]

    def test_quantity_non_numeric_string(self) -> None:
        """quantity 非数字字符串拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(quantity="abc", amount="abc"))

    def test_price_non_numeric_string(self) -> None:
        """price 非数字字符串拒绝。"""
        tpl = AShareTradeRecordTemplate()
        with pytest.raises(InvalidTradeRecordError):
            tpl.validate(make_valid_entry(price="xyz", amount="xyz"))


# ── 模板版本测试 ──


class TestTemplateVersion:
    def test_get_required_fields_count(self) -> None:
        """11 必填字段。"""
        tpl = AShareTradeRecordTemplate()
        fields = tpl.get_required_fields()
        assert len(fields) == 11

    def test_get_required_fields_content(self) -> None:
        """必填字段名正确。"""
        tpl = AShareTradeRecordTemplate()
        fields = set(tpl.get_required_fields())
        expected = {
            "trade_date", "symbol", "side", "quantity", "price",
            "amount", "commission", "stamp_duty", "transfer_fee",
            "strategy_id", "account_id",
        }
        assert fields == expected

    def test_get_required_fields_returns_copy(self) -> None:
        """返回副本, 修改不影响内部。"""
        tpl = AShareTradeRecordTemplate()
        fields = tpl.get_required_fields()
        fields.clear()
        assert len(tpl.get_required_fields()) == 11

    def test_get_template_version(self) -> None:
        """模板版本=1.0。"""
        tpl = AShareTradeRecordTemplate()
        assert tpl.get_template_version() == "1.0"

    def test_entry_schema_version_matches(self) -> None:
        """记录 schema_version 与模板版本一致。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry())
        assert entry.schema_version == tpl.get_template_version()


# ── 不可变测试 ──


class TestImmutability:
    def test_entry_frozen(self) -> None:
        """TradeRecordEntry frozen。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry())
        with pytest.raises(dataclasses.FrozenInstanceError):
            entry.symbol = "000001"  # type: ignore[misc]

    def test_entry_quantity_frozen(self) -> None:
        """quantity 不可重新赋值。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry())
        with pytest.raises(dataclasses.FrozenInstanceError):
            entry.quantity = Decimal("999")  # type: ignore[misc]

    def test_entry_side_frozen(self) -> None:
        """side 不可重新赋值。"""
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate(make_valid_entry())
        with pytest.raises(dataclasses.FrozenInstanceError):
            entry.side = "SELL"  # type: ignore[misc]
