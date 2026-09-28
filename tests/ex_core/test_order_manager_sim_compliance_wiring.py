# [A_test] module_id: MOD-EXE-order_manager_sim_compliance_wiring_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.ex_core.test_order_manager_sim_compliance_wiring_test
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""F62 P0-10 模拟侧执法接线红绿测试（程序化报备闸 + 信息空窗回避闸）。

覆盖（全部 synthetic，tmp_path，无网络/无 broker/无 CH）：
  - 程序化报备闸（G07，40 号 §决策⑱）：LIVE 未报备 → ComplianceGateBlockError
    （reason_code=PROGRAMMATIC_REGISTRATION_BLOCKED_UNREGISTERED，broker 零调用，
    订单保持 PENDING）；SIMULATION 模式 → 豁免放行（模拟盘零行为变化）；
    守卫异常 → Fail-Closed 拒发（REGISTRATION_GUARD_FAILED）。
  - 信息空窗回避闸（G09，MOD-CMP-014）：标的命中回避名单 → 拒发
    （INFO_ASYMMETRY_AVOIDED）；干净标的 → 放行；检测异常 → Fail-Closed
    （AVOIDANCE_DETECTOR_FAILED）。
  - 向后兼容：全 None 未注入 → 既有行为不变（订单正常发出）。
"""

from __future__ import annotations

import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from zephyr.compliance.info_asymmetry_manipulation_detector import (
    InfoAsymmetryManipulationDetector,
    ManipulationFeatures,
)
from zephyr.ex_core.order_manager import ComplianceGateBlockError, OrderManager
from zephyr.ex_core.programmatic_trading_guard import (
    ProgrammaticTradingGuard,
    ProgrammaticTradingGuardConfig,
    TradingMode,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType

# ---------------------------------------------------------------------
# 测试辅助
# ---------------------------------------------------------------------

_SYMBOL = "600519.SH"


def _make_broker() -> MagicMock:
    broker = MagicMock()
    broker.submit_order.return_value = "broker-oid-1"
    return broker


def _make_om(broker: MagicMock, **gates) -> OrderManager:
    om = OrderManager(**gates)
    om.register_broker("test_broker", broker)
    return om


def _create_and_submit(om: OrderManager, symbol: str = _SYMBOL) -> str:
    order = om.create_order(
        symbol=symbol,
        strategy_id="test",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("10"),
        broker_id="test_broker",
    )
    return om.submit_order(order.order_id, "test_broker")


def _zero_features() -> ManipulationFeatures:
    return ManipulationFeatures(
        deviation=0.0,
        cancel_rate=0.0,
        order_intervals=(),
        volume_concentration=0.0,
        tail_volume_ratio=0.0,
        tail_deviation=0.0,
        self_trade_ratio=0.0,
    )


def _flat_returns() -> list[float]:
    """微幅交替收益（方差非零 → z_scan 合法；|z| 远低于 2.0 → 无波动异常）。"""
    return [0.001, -0.001, 0.002, -0.002, 0.001, 0.0, -0.001, 0.001, 0.0, 0.002]


def _detector_with_avoided(symbol: str) -> InfoAsymmetryManipulationDetector:
    """真实检测器：登记披露远超 90 天空窗 → scan 命中 → 入回避名单（确定性）。"""
    detector = InfoAsymmetryManipulationDetector()
    detector.register_disclosure(symbol, datetime.date(2025, 1, 1))
    detector.scan(
        symbol,
        datetime.date(2026, 9, 28),
        _flat_returns(),
        _zero_features(),
    )
    assert symbol in detector.avoid_symbols()
    return detector


def _reason_code(exc: ComplianceGateBlockError) -> str:
    return str(exc.details.get("reason_code", ""))


# ---------------------------------------------------------------------
# G07 程序化报备闸
# ---------------------------------------------------------------------


class TestRegistrationGateWiring:
    def test_live_unregistered_refuses(self):
        """红：LIVE 模式未报备 → 拒发（先报备后交易保险丝），broker 零调用。"""
        broker = _make_broker()
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.LIVE,
                live_broker_ids={"test_broker"},
            ),
        )
        om = _make_om(broker, registration_guard=guard)
        order = om.create_order(
            symbol=_SYMBOL,
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10"),
            broker_id="test_broker",
        )
        with pytest.raises(ComplianceGateBlockError) as excinfo:
            om.submit_order(order.order_id, "test_broker")
        assert _reason_code(excinfo.value) == "PROGRAMMATIC_REGISTRATION_BLOCKED_UNREGISTERED"
        broker.submit_order.assert_not_called()
        assert order.status is OrderStatus.PENDING

    def test_simulation_mode_exempt_passes(self):
        """绿：SIMULATION 模式天然豁免 → 放行（模拟盘零行为变化）。"""
        broker = _make_broker()
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.SIMULATION,
                live_broker_ids={"test_broker"},
            ),
        )
        om = _make_om(broker, registration_guard=guard)
        assert _create_and_submit(om) == "broker-oid-1"
        broker.submit_order.assert_called_once()

    def test_guard_exception_fail_closed(self):
        """红：守卫自身失效 → Fail-Closed 拒发（REGISTRATION_GUARD_FAILED）。"""

        class _BrokenGuard:
            def check_can_trade(self, broker_id: str):
                raise RuntimeError("guard exploded")

        broker = _make_broker()
        om = _make_om(broker, registration_guard=_BrokenGuard())
        with pytest.raises(ComplianceGateBlockError) as excinfo:
            _create_and_submit(om)
        assert _reason_code(excinfo.value) == "REGISTRATION_GUARD_FAILED"
        broker.submit_order.assert_not_called()


# ---------------------------------------------------------------------
# G09 信息空窗回避闸
# ---------------------------------------------------------------------


class TestAvoidanceGateWiring:
    def test_avoided_symbol_refused(self):
        """红：标的命中回避名单 → 拒发（INFO_ASYMMETRY_AVOIDED）。"""
        broker = _make_broker()
        om = _make_om(broker, avoidance_detector=_detector_with_avoided(_SYMBOL))
        with pytest.raises(ComplianceGateBlockError) as excinfo:
            _create_and_submit(om)
        assert _reason_code(excinfo.value) == "INFO_ASYMMETRY_AVOIDED"
        broker.submit_order.assert_not_called()

    def test_clean_symbol_passes(self):
        """绿：干净标的（空回避名单）→ 放行（零误拒）。"""
        broker = _make_broker()
        om = _make_om(broker, avoidance_detector=InfoAsymmetryManipulationDetector())
        assert _create_and_submit(om) == "broker-oid-1"
        broker.submit_order.assert_called_once()

    def test_other_symbol_not_refused(self):
        """绿：名单只拦命中标的，其他标的正常放行。"""
        broker = _make_broker()
        om = _make_om(broker, avoidance_detector=_detector_with_avoided("000001.SZ"))
        assert _create_and_submit(om, _SYMBOL) == "broker-oid-1"

    def test_detector_failure_fail_closed(self):
        """红：检测失效 → Fail-Closed 拒发（AVOIDANCE_DETECTOR_FAILED）。"""

        class _BrokenDetector:
            def avoid_symbols(self) -> tuple[str, ...]:
                raise RuntimeError("detector exploded")

        broker = _make_broker()
        om = _make_om(broker, avoidance_detector=_BrokenDetector())
        with pytest.raises(ComplianceGateBlockError) as excinfo:
            _create_and_submit(om)
        assert _reason_code(excinfo.value) == "AVOIDANCE_DETECTOR_FAILED"
        broker.submit_order.assert_not_called()


# ---------------------------------------------------------------------
# 向后兼容
# ---------------------------------------------------------------------


class TestBackwardCompat:
    def test_no_gates_wired_unchanged(self):
        """全 None 未注入 → 既有行为不变（订单正常发出）。"""
        broker = _make_broker()
        om = _make_om(broker)
        assert _create_and_submit(om) == "broker-oid-1"
        broker.submit_order.assert_called_once()
