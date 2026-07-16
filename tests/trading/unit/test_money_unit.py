# [A_test] module_id: SRC-TST-2046 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-663 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_money
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/contracts/money.py
================================================
覆盖矩阵：
  Money 构造：
    - 有效 × 4（str、Decimal、int、自动 quantize）
    - 无效 × 3（float 禁止、跨币种运算、除以零）
  Money 运算：
    - 加减乘除 × 4
    - 乘法/除法 float 禁止 × 2
    - 比较运算 × 4（< <= > >=）
    - 正负/绝对值 × 3
  Money 展示：
    - __str__ 格式化 × 3（CNY 2位、JPY 0位、BTC 8位）
    - __repr__ × 1
    - __bool__ × 2
  Money 工具方法：
    - is_zero / is_positive / is_negative × 3
  get_currency_precision：
    - 已知货币 × 3（CNY=2、JPY=0、BTC=8）
    - 未知货币 × 1（默认2位+警告）
  异常层级：
    - MoneyPrecisionError / MoneyCurrencyMismatchError × 2

Safety: HIGH（金融精度契约）
"""

from __future__ import annotations

import warnings
from decimal import Decimal

import pytest

from zephyr.trading.trading_contracts.portfolio.contracts.money import (
    Money,
    MoneyCurrencyMismatchError,
    MoneyPrecisionError,
    get_currency_precision,
)


class TestMoneyConstruction:
    def test_from_string(self):
        m = Money("1234.56", "CNY")
        assert m.amount == Decimal("1234.56")
        assert m.currency == "CNY"

    def test_from_decimal(self):
        m = Money(Decimal("99.99"), "USD")
        assert m.amount == Decimal("99.99")

    def test_from_int(self):
        m = Money(100, "CNY")
        assert m.amount == Decimal("100")

    @pytest.mark.financial
    def test_auto_quantize_cny(self):
        m = Money("123.456", "CNY")
        assert m.amount == Decimal("123.46")

    @pytest.mark.financial
    def test_auto_quantize_jpy(self):
        m = Money("123.6", "JPY")
        assert m.amount == Decimal("124")

    @pytest.mark.financial
    def test_auto_quantize_btc(self):
        m = Money("1.234567890", "BTC")
        assert m.amount == Decimal("1.23456789")

    @pytest.mark.financial
    def test_float_construction_forbidden(self):
        with pytest.raises(MoneyPrecisionError, match="禁止使用 float"):
            Money(1234.56, "CNY")


class TestMoneyArithmetic:
    def test_add_same_currency(self):
        a = Money("100.50", "CNY")
        b = Money("50.25", "CNY")
        result = a + b
        assert result == Money("150.75", "CNY")

    def test_sub_same_currency(self):
        a = Money("100.50", "CNY")
        b = Money("50.25", "CNY")
        result = a - b
        assert result == Money("50.25", "CNY")

    @pytest.mark.financial
    def test_mul_by_int(self):
        a = Money("100.50", "CNY")
        result = a * 2
        assert result == Money("201.00", "CNY")

    @pytest.mark.financial
    def test_mul_by_decimal(self):
        a = Money("100.00", "CNY")
        result = a * Decimal("1.5")
        assert result == Money("150.00", "CNY")

    def test_rmul_by_int(self):
        a = Money("100.00", "CNY")
        result = 3 * a
        assert result == Money("300.00", "CNY")

    @pytest.mark.financial
    def test_truediv_by_int(self):
        a = Money("100.00", "CNY")
        result = a / 2
        assert result == Money("50.00", "CNY")

    @pytest.mark.financial
    def test_truediv_by_decimal(self):
        a = Money("100.00", "CNY")
        result = a / Decimal("4")
        assert result == Money("25.00", "CNY")

    @pytest.mark.financial
    def test_mul_float_forbidden(self):
        a = Money("100", "CNY")
        with pytest.raises(MoneyPrecisionError, match="禁止使用 float"):
            a * 1.5

    @pytest.mark.financial
    def test_div_float_forbidden(self):
        a = Money("100", "CNY")
        with pytest.raises(MoneyPrecisionError, match="禁止使用 float"):
            a / 2.0

    @pytest.mark.financial
    def test_div_by_zero(self):
        a = Money("100", "CNY")
        with pytest.raises(ZeroDivisionError, match="除以零"):
            a / 0

    @pytest.mark.financial
    def test_cross_currency_add_forbidden(self):
        a = Money("100", "CNY")
        b = Money("10", "USD")
        with pytest.raises(MoneyCurrencyMismatchError, match="币种不匹配"):
            a + b

    @pytest.mark.financial
    def test_cross_currency_sub_forbidden(self):
        a = Money("100", "CNY")
        b = Money("10", "USD")
        with pytest.raises(MoneyCurrencyMismatchError, match="币种不匹配"):
            a - b


class TestMoneyComparison:
    def test_lt(self):
        assert Money("50", "CNY") < Money("100", "CNY")

    def test_le(self):
        assert Money("100", "CNY") <= Money("100", "CNY")
        assert Money("50", "CNY") <= Money("100", "CNY")

    def test_gt(self):
        assert Money("100", "CNY") > Money("50", "CNY")

    def test_ge(self):
        assert Money("100", "CNY") >= Money("100", "CNY")
        assert Money("100", "CNY") >= Money("50", "CNY")

    def test_cross_currency_compare_forbidden(self):
        a = Money("100", "CNY")
        b = Money("100", "USD")
        with pytest.raises(MoneyCurrencyMismatchError):
            a < b


class TestMoneyUnary:
    def test_neg(self):
        m = Money("100.50", "CNY")
        result = -m
        assert result.amount == Decimal("-100.50")
        assert result.currency == "CNY"

    def test_abs_positive(self):
        m = Money("100", "CNY")
        assert abs(m) == Money("100", "CNY")

    def test_abs_negative(self):
        m = Money("-100", "CNY")
        assert abs(m) == Money("100", "CNY")


class TestMoneyDisplay:
    def test_str_cny(self):
        m = Money("1234.56", "CNY")
        assert str(m) == "1,234.56 CNY"

    def test_str_jpy(self):
        m = Money("1234", "JPY")
        assert str(m) == "1,234 JPY"

    def test_str_btc(self):
        m = Money("1.23456789", "BTC")
        assert str(m) == "1.23456789 BTC"

    def test_repr(self):
        m = Money("100", "CNY")
        r = repr(m)
        assert "Money" in r
        assert "CNY" in r

    def test_bool_nonzero(self):
        assert bool(Money("100", "CNY")) is True

    def test_bool_zero(self):
        assert bool(Money("0", "CNY")) is False


class TestMoneyUtility:
    def test_is_zero(self):
        assert Money("0", "CNY").is_zero() is True
        assert Money("100", "CNY").is_zero() is False

    def test_is_positive(self):
        assert Money("100", "CNY").is_positive() is True
        assert Money("-50", "CNY").is_positive() is False
        assert Money("0", "CNY").is_positive() is False

    def test_is_negative(self):
        assert Money("-50", "CNY").is_negative() is True
        assert Money("100", "CNY").is_negative() is False
        assert Money("0", "CNY").is_negative() is False


class TestGetCurrencyPrecision:
    def test_cny_precision(self):
        assert get_currency_precision("CNY") == 2

    def test_jpy_precision(self):
        assert get_currency_precision("JPY") == 0

    def test_btc_precision(self):
        assert get_currency_precision("BTC") == 8

    def test_unknown_currency_defaults_to_2(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = get_currency_precision("XYZ")
            assert result == 2
            assert len(w) == 1
            assert "XYZ" in str(w[0].message)


class TestMoneyFrozen:
    def test_frozen_immutable(self):
        m = Money("100", "CNY")
        with pytest.raises(AttributeError):
            m.amount = Decimal("200")

    def test_hashable(self):
        m1 = Money("100", "CNY")
        m2 = Money("100", "CNY")
        assert hash(m1) == hash(m2)
        assert len({m1, m2}) == 1
