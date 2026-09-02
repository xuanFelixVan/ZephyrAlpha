# [A_test] module_id: MOD-RK-BSS | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RK-011 | §3.5.1/§6.11
# [MODULE] tests.risk.test_drawdown_broker_side_stop
# [INVARIANTS] 缺 stop_price 抛错(fail-closed); stop≥reference 抛错; qty 覆盖+价格容差内=受保护; 未保护/错配→coverage_ok=False; 空仓不产出意图
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions raised from tests
# [TESTS] tests/risk/test_drawdown_broker_side_stop.py
# [TTL] task_bound
"""L2 broker 端硬止损测试（35 号 §6.11，§3.5.1 四层架构 L2 落地）。"""

from __future__ import annotations

import pytest

from zephyr.risk.core.drawdown_broker_side_stop import (
    BrokerSideStopConfig,
    InvalidBrokerSideStopInputError,
    build_protective_stop_plan,
    reconcile_broker_side_stops,
)


def _pos(qty=1000, stop_price=9.5, reference_price=10.0):
    pos = {"qty": qty, "stop_price": stop_price}
    if reference_price is not None:
        pos["reference_price"] = reference_price
    return pos


class TestBuildProtectiveStopPlan:
    def test_basic_intent(self):
        intents = build_protective_stop_plan({"000001.SZ": _pos()})
        assert len(intents) == 1
        i = intents[0]
        assert i.symbol == "000001.SZ" and i.qty == 1000 and i.stop_price == 9.5
        assert i.side == "SELL"

    def test_zero_qty_skipped(self):
        """qty=0 非在持仓位，不产出意图。"""
        intents = build_protective_stop_plan({"000001.SZ": _pos(qty=0)})
        assert intents == []

    def test_multi_positions_order_preserved(self):
        intents = build_protective_stop_plan({"A": _pos(), "B": _pos(), "C": _pos(qty=0)})
        assert [i.symbol for i in intents] == ["A", "B"]

    def test_missing_stop_price_fail_closed(self):
        """缺 stop_price 即抛错——安全价不可臆造（fail-closed）。"""
        with pytest.raises(InvalidBrokerSideStopInputError, match="stop_price"):
            build_protective_stop_plan({"A": {"qty": 100}})

    def test_non_positive_stop_price(self):
        with pytest.raises(InvalidBrokerSideStopInputError):
            build_protective_stop_plan({"A": _pos(stop_price=0)})

    def test_negative_qty(self):
        with pytest.raises(InvalidBrokerSideStopInputError):
            build_protective_stop_plan({"A": _pos(qty=-1)})

    def test_stop_above_reference_inverted(self):
        """止损价不低于参考价=保护方向倒挂，抛错。"""
        with pytest.raises(InvalidBrokerSideStopInputError, match="须低于参考价"):
            build_protective_stop_plan({"A": _pos(stop_price=10.5, reference_price=10.0)})

    def test_stop_equal_reference_inverted(self):
        with pytest.raises(InvalidBrokerSideStopInputError):
            build_protective_stop_plan({"A": _pos(stop_price=10.0, reference_price=10.0)})

    def test_no_reference_price_ok(self):
        """无参考价时只做正向校验（调用方未供价不否决）。"""
        intents = build_protective_stop_plan({"A": _pos(reference_price=None)})
        assert len(intents) == 1

    def test_non_mapping_position(self):
        with pytest.raises(InvalidBrokerSideStopInputError):
            build_protective_stop_plan({"A": "not_a_mapping"})


class TestReconcileBrokerSideStops:
    def test_full_coverage(self):
        positions = {"A": _pos(), "B": _pos(stop_price=19.0, reference_price=20.0)}
        orders = [
            {"symbol": "A", "qty": 1000, "stop_price": 9.5},
            {"symbol": "B", "qty": 1000, "stop_price": 19.0},
        ]
        r = reconcile_broker_side_stops(positions, orders)
        assert r.coverage_ok is True
        assert r.unprotected == () and r.mismatched == ()
        assert len(r.intents) == 2

    def test_no_orders_all_unprotected(self):
        """broker 端无任何止损单 → 全部未保护（fail-closed）。"""
        r = reconcile_broker_side_stops({"A": _pos()}, None)
        assert r.coverage_ok is False
        assert r.unprotected == ("A",)

    def test_empty_orders_all_unprotected(self):
        r = reconcile_broker_side_stops({"A": _pos()}, [])
        assert r.coverage_ok is False
        assert r.unprotected == ("A",)

    def test_qty_insufficient_mismatch(self):
        """止损单数量不足 → 错配（保护不足）。"""
        r = reconcile_broker_side_stops({"A": _pos(qty=1000)}, [{"symbol": "A", "qty": 500, "stop_price": 9.5}])
        assert r.coverage_ok is False
        assert r.unprotected == ()
        assert len(r.mismatched) == 1 and "保护不足" in r.mismatched[0][1]

    def test_price_within_tolerance_ok(self):
        """tick 取整差异在默认 0.1% 容差内 → 受保护。"""
        r = reconcile_broker_side_stops(
            {"A": _pos(stop_price=9.5)}, [{"symbol": "A", "qty": 1000, "stop_price": 9.501}]
        )
        assert r.coverage_ok is True

    def test_price_beyond_tolerance_mismatch(self):
        r = reconcile_broker_side_stops({"A": _pos(stop_price=9.5)}, [{"symbol": "A", "qty": 1000, "stop_price": 9.4}])
        assert r.coverage_ok is False
        assert "超容差" in r.mismatched[0][1]

    def test_zero_tolerance_exact_match(self):
        cfg = BrokerSideStopConfig(price_tolerance_ratio=0.0)
        r = reconcile_broker_side_stops(
            {"A": _pos(stop_price=9.5)},
            [{"symbol": "A", "qty": 1000, "stop_price": 9.5}],
            config=cfg,
        )
        assert r.coverage_ok is True
        r2 = reconcile_broker_side_stops(
            {"A": _pos(stop_price=9.5)},
            [{"symbol": "A", "qty": 1000, "stop_price": 9.500001}],
            config=cfg,
        )
        assert r2.coverage_ok is False

    def test_multiple_orders_same_symbol_take_max_qty(self):
        """同标的多张止损单按最覆盖口径（qty 最大者）对账。"""
        orders = [
            {"symbol": "A", "qty": 500, "stop_price": 9.5},
            {"symbol": "A", "qty": 1000, "stop_price": 9.5},
        ]
        r = reconcile_broker_side_stops({"A": _pos(qty=1000)}, orders)
        assert r.coverage_ok is True

    def test_invalid_order_fields(self):
        with pytest.raises(InvalidBrokerSideStopInputError):
            reconcile_broker_side_stops({"A": _pos()}, [{"symbol": "A", "qty": 0, "stop_price": 9.5}])

    def test_invalid_order_payload(self):
        with pytest.raises(InvalidBrokerSideStopInputError):
            reconcile_broker_side_stops({"A": _pos()}, ["not_a_mapping"])

    def test_invalid_config_tolerance(self):
        with pytest.raises(InvalidBrokerSideStopInputError):
            BrokerSideStopConfig(price_tolerance_ratio=-0.1)
        with pytest.raises(InvalidBrokerSideStopInputError):
            BrokerSideStopConfig(price_tolerance_ratio=1.0)
