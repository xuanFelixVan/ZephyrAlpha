# [BLUEPRINT] MOD-POS-018 | docs/03_modules/MOD-POS-018/
# [MODULE] zephyr.position.core.intraday_position_constraint
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/position/test_intraday_position_constraint.py
# [TTL] permanent
"""intraday_position_constraint（盘中仓位约束，T+1 配套）单元测试。

覆盖：
- T+1 内生：当日买入不可卖（卖出>可卖量→T1_FROZEN 违规）
- 今日已卖从可卖量扣减（复用 t1_sellable 口径）
- 单标的上限/总仓位上限盘后投影校验
- 违规结构化留痕；全合规→allowed=True
- 非法输入 → InvalidIntradayConstraintInputError
"""

from __future__ import annotations

import pytest

from zephyr.position.core.intraday_position_constraint import (
    IntradayConstraintInput,
    InvalidIntradayConstraintInputError,
    ViolationCode,
    check_intraday_constraints,
)


def _input(**kw) -> IntradayConstraintInput:
    base = {
        "last_session_weights": {"A": 0.10, "B": 0.05},
        "today_bought_weights": {},
        "today_sold_weights": {},
        "intended_sells": {},
        "intended_buys": {},
        "max_single_weight": 0.20,
        "max_total_weight": 0.90,
    }
    base.update(kw)
    return IntradayConstraintInput(**base)


class TestT1Frozen:
    def test_sell_within_sellable_allowed(self) -> None:
        """卖出≤昨仓 → 允许。"""
        r = check_intraday_constraints(_input(intended_sells={"A": 0.05}))
        assert r.allowed is True
        assert r.violations == ()

    def test_sell_above_last_session_rejected(self) -> None:
        """卖出>昨仓 → T1_FROZEN。"""
        r = check_intraday_constraints(_input(intended_sells={"A": 0.15}))
        assert r.allowed is False
        assert any(v.code is ViolationCode.T1_FROZEN and v.symbol == "A" for v in r.violations)

    def test_today_bought_not_sellable(self) -> None:
        """当日买入部分不可卖：昨仓 0.10+今买 0.05，卖 0.12 → 违规。"""
        r = check_intraday_constraints(
            _input(today_bought_weights={"A": 0.05}, intended_sells={"A": 0.12})
        )
        assert r.allowed is False
        assert any(v.code is ViolationCode.T1_FROZEN for v in r.violations)

    def test_today_sold_deducts_sellable(self) -> None:
        """今日已卖 0.06 → 可卖仅剩 0.04，再卖 0.05 → 违规。"""
        r = check_intraday_constraints(
            _input(today_sold_weights={"A": 0.06}, intended_sells={"A": 0.05})
        )
        assert r.allowed is False

    def test_sell_symbol_not_held_rejected(self) -> None:
        """卖出未持有标的 → 违规（可卖=0）。"""
        r = check_intraday_constraints(_input(intended_sells={"ZZZ": 0.01}))
        assert r.allowed is False
        assert any(v.code is ViolationCode.T1_FROZEN and v.symbol == "ZZZ" for v in r.violations)


class TestCaps:
    def test_single_cap_breach(self) -> None:
        """买入后单标的 0.22 > 上限 0.20 → SINGLE_CAP。"""
        r = check_intraday_constraints(_input(intended_buys={"A": 0.12}))
        assert r.allowed is False
        assert any(v.code is ViolationCode.SINGLE_CAP and v.symbol == "A" for v in r.violations)

    def test_total_cap_breach(self) -> None:
        """买入后总仓 0.95 > 上限 0.90 → TOTAL_CAP。"""
        r = check_intraday_constraints(_input(intended_buys={"C": 0.80}))
        assert r.allowed is False
        assert any(v.code is ViolationCode.TOTAL_CAP for v in r.violations)

    def test_sell_reduces_total_below_cap(self) -> None:
        """卖出后总仓下降 → 不触发 TOTAL_CAP。"""
        r = check_intraday_constraints(_input(intended_sells={"A": 0.10, "B": 0.05}))
        assert r.allowed is True

    def test_post_trade_weights_projected(self) -> None:
        """post_trade_weights 投影=昨仓+今买+拟买−今卖−拟卖。"""
        r = check_intraday_constraints(
            _input(intended_buys={"C": 0.03}, intended_sells={"B": 0.05})
        )
        assert r.post_trade_weights["A"] == pytest.approx(0.10)
        assert r.post_trade_weights["B"] == pytest.approx(0.0)
        assert r.post_trade_weights["C"] == pytest.approx(0.03)

    def test_t1_sellable_echoed(self) -> None:
        """结果回传 T+1 可卖口径（供下游复用）。"""
        r = check_intraday_constraints(_input(today_sold_weights={"A": 0.04}))
        assert r.t1_sellable["A"] == pytest.approx(0.06)


class TestInvalidInput:
    def test_negative_sell_intent(self) -> None:
        with pytest.raises(InvalidIntradayConstraintInputError):
            check_intraday_constraints(_input(intended_sells={"A": -0.01}))

    def test_negative_buy_intent(self) -> None:
        with pytest.raises(InvalidIntradayConstraintInputError):
            check_intraday_constraints(_input(intended_buys={"A": -0.01}))

    def test_invalid_caps(self) -> None:
        with pytest.raises(InvalidIntradayConstraintInputError):
            check_intraday_constraints(_input(max_single_weight=0.0))
        with pytest.raises(InvalidIntradayConstraintInputError):
            check_intraday_constraints(_input(max_total_weight=1.5))

    def test_single_cap_above_total_cap(self) -> None:
        with pytest.raises(InvalidIntradayConstraintInputError):
            check_intraday_constraints(
                _input(max_single_weight=0.95, max_total_weight=0.90)
            )

    def test_non_finite_weights(self) -> None:
        with pytest.raises(InvalidIntradayConstraintInputError):
            check_intraday_constraints(
                _input(last_session_weights={"A": float("nan")})
            )
