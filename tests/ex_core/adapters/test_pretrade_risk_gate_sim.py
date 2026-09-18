# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] tests.ex_core.adapters.test_pretrade_risk_gate_sim
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.qmt_file_bridge_broker; zephyr.ex_core.execution_engine; zephyr.ex_core.trading_session
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] 零网零桥（fake validator/MagicMock broker/临时目录）; sim 进桥前校验 fail-closed; real 分流不触校验(裁定#338⑤)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L06-001-QMTFB | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""R-H5E-1 pre-trade 前置校验接线（paper/sim 面）单元测试

覆盖（裁定 #338⑤：paper/sim 准施工，实盘 Owner 门不动）：
  1. sim 桥层闸：HALT 违规 → QmtFileBridgeError，订单不进桥（指令文件零写入）；
  2. 校验器异常 → Fail-Closed 拒单（异常链留痕），订单不进桥；
  3. 校验通过 → 指令正常写入（放行）；
  4. env="real" 分流：注入了校验器也不触发（实盘路径保持现状，Owner 门）；
  5. 未注入校验器 → 既有行为不变（向后兼容）；
  6. TradingSession._is_blocked_by_risk：校验器异常 → Fail-Closed 拦单（True）；
  7. ExecutionEngine.execute_order：校验器异常 → ValueError(fail-closed) 拒单，
     订单不提交 broker；校验通过 → 正常执行（放行）。
零网零桥：全程临时目录 + MagicMock/fake validator，不打真 QMT/HTTP。
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.ex_core.adapters.qmt_file_bridge_broker import (
    QmtFileBridgeBroker,
    QmtFileBridgeError,
)
from zephyr.ex_core.execution_engine import ExecutionEngine
from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.trading_session import TradingSession, TradingSessionConfig
from zephyr.governance.adapters.risk_validation_bridge import RiskViolation
from zephyr.shared.contracts.order import Order, OrderSide, OrderType
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.utils.time_utils import now_utc


# ── 测试工厂 ────────────────────────────────────────────────────────────────


def _make_order(symbol: str = "510300.SH", side: OrderSide = OrderSide.BUY) -> Order:
    return Order(
        order_id="rh5e-001",
        idempotency_key="rh5e-001",
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        side=side,
        strategy_id="test_strategy",
        symbol=symbol,
        limit_price=Decimal("8.10"),
        created_at=now_utc(),
    )


def _halt_violation() -> RiskViolation:
    return RiskViolation(
        constraint="POSITION_LIMIT",
        description="单仓权重超限: 510300.SH",
        limit_value=Decimal("0.10"),
        actual_value=Decimal("0.50"),
        severity="HALT",
    )


def _patched_broker(env: str, **kwargs) -> QmtFileBridgeBroker:
    """临时目录封闭化的 Broker（禁 HTTP 快路径，零外联）。"""
    config = QmtFileBridgeBroker.ENV_CONFIG[env].copy()
    tmp = Path(kwargs.pop("_tmpdir"))
    config["bridge_dir"] = str(tmp)
    config["orders_file"] = str(tmp / f"orders_{env}.csv")
    config["ack_file"] = str(tmp / f"ack_{env}.csv")
    config["stock_dir"] = str(tmp / "Stock")
    with patch.dict(QmtFileBridgeBroker.ENV_CONFIG, {env: config}):
        broker = QmtFileBridgeBroker(env=env, sync_interval=0.1, http_port=None, **kwargs)
    return broker


def _instruction_ids(orders_file: Path) -> set[str]:
    """读指令文件中已写入的 order_id 集合（表头除外）。"""
    if not orders_file.exists():
        return set()
    return {
        line.split(",", 1)[0]
        for line in orders_file.read_text(encoding="ascii").splitlines()
        if line and not line.startswith("#") and not line.startswith("order_id,")
    }


class _FakeValidator:
    """fake 风控校验器（零网零桥注入件）。"""

    def __init__(self, violations: list | None = None, error: Exception | None = None):
        self.violations = violations or []
        self.error = error
        self.calls: list[dict] = []

    def validate_order(self, *, symbol, target_weight, current_holdings, limits):
        self.calls.append({"symbol": symbol, "target_weight": target_weight})
        if self.error is not None:
            raise self.error
        return self.violations

    def validate_portfolio(self, *args, **kwargs):  # pragma: no cover - 本套用例不触
        return []


# ── sim 桥层闸（QmtFileBridgeBroker.submit_order）──────────────────────────


class TestSimBridgePretradeGate:
    @pytest.fixture
    def tmp_bridge(self, tmp_path):
        return tmp_path

    @pytest.fixture
    def sim_orders_file(self, tmp_bridge):
        return tmp_bridge / "orders_sim.csv"

    def test_sim_halt_violation_order_never_enters_bridge(self, tmp_bridge, sim_orders_file):
        """校验 HALT 违规 → 拒单，订单不进桥（指令文件零写入），原因随异常留痕。"""
        validator = _FakeValidator(violations=[_halt_violation()])
        broker = _patched_broker("sim", risk_validator=validator, _tmpdir=tmp_bridge)
        try:
            assert broker.connect() is True
            with pytest.raises(QmtFileBridgeError) as exc_info:
                broker.submit_order(_make_order())
            assert "单仓权重超限" in str(exc_info.value)
        finally:
            broker.disconnect()
        assert "rh5e-001" not in _instruction_ids(sim_orders_file)

    def test_sim_validator_exception_fail_closed(self, tmp_bridge, sim_orders_file):
        """校验器异常 → Fail-Closed 拒单（不许 fail-open），异常链留痕、不进桥。"""
        validator = _FakeValidator(error=RuntimeError("风控状态存储不可达"))
        broker = _patched_broker("sim", risk_validator=validator, _tmpdir=tmp_bridge)
        try:
            assert broker.connect() is True
            with pytest.raises(QmtFileBridgeError) as exc_info:
                broker.submit_order(_make_order())
            assert "fail-closed" in str(exc_info.value)
            assert isinstance(exc_info.value.__cause__, RuntimeError)
        finally:
            broker.disconnect()
        assert "rh5e-001" not in _instruction_ids(sim_orders_file)

    def test_sim_clean_validation_writes_instruction(self, tmp_bridge, sim_orders_file):
        """校验通过 → 放行，指令正常写入（不误伤正常订单）。"""
        validator = _FakeValidator(violations=[])
        broker = _patched_broker("sim", risk_validator=validator, _tmpdir=tmp_bridge)
        try:
            assert broker.connect() is True
            broker_order_id = broker.submit_order(_make_order())
            assert broker_order_id == "rh5e-001"
        finally:
            broker.disconnect()
        assert "rh5e-001" in _instruction_ids(sim_orders_file)
        assert len(validator.calls) == 1

    def test_sim_without_validator_keeps_legacy_behavior(self, tmp_bridge, sim_orders_file):
        """未注入校验器 → 既有行为不变（直接进桥，向后兼容）。"""
        broker = _patched_broker("sim", _tmpdir=tmp_bridge)
        try:
            assert broker.connect() is True
            assert broker.submit_order(_make_order()) == "rh5e-001"
        finally:
            broker.disconnect()
        assert "rh5e-001" in _instruction_ids(sim_orders_file)

    def test_sim_without_validator_logs_visibility_warning(self, tmp_bridge, caplog):
        """红队批回归：sim 未注入校验器=闸不生效（向后兼容语义），但必须日志留痕——
        装配层忘注入时可见，而不是静默裸奔。"""
        import logging

        with caplog.at_level(logging.WARNING,
                             logger="zephyr.ex_core.adapters.qmt_file_bridge_broker"):
            broker = _patched_broker("sim", _tmpdir=tmp_bridge)
        try:
            assert any("未注入 risk_validator" in r.message for r in caplog.records)
        finally:
            broker.disconnect()

    def test_sim_validator_none_return_fail_closed(self, tmp_bridge, sim_orders_file):
        """红队批回归：有 bug 的第三方校验器返回 None → 仍 QmtFileBridgeError 拒单
        且不进桥（旧写法 HALT 扫描在 try 外抛 TypeError，错误契约失真）。"""

        class BuggyNone:
            def validate_order(self, **kwargs):
                return None

        broker = _patched_broker("sim", risk_validator=BuggyNone(), _tmpdir=tmp_bridge)
        try:
            assert broker.connect() is True
            with pytest.raises(QmtFileBridgeError, match="fail-closed"):
                broker.submit_order(_make_order())
        finally:
            broker.disconnect()
        assert "rh5e-001" not in _instruction_ids(sim_orders_file)


# ── real 分流：实盘路径不触校验（裁定 #338⑤ Owner 门）─────────────────────


class TestRealEnvBypass:
    def test_real_env_does_not_invoke_validator(self, tmp_path):
        """env="real"：即便注入了校验器也不触发——实盘路径保持现状。"""
        validator = _FakeValidator(violations=[_halt_violation()])
        broker = _patched_broker("real", risk_validator=validator, _tmpdir=tmp_path)
        try:
            assert broker.connect() is True
            assert broker.submit_order(_make_order()) == "rh5e-001"
        finally:
            broker.disconnect()
        assert validator.calls == []  # 校验器零调用 = 实盘链路未被触碰
        assert "rh5e-001" in _instruction_ids(tmp_path / "orders_real.csv")


# ── TradingSession：校验器异常 Fail-Closed 拦单 ────────────────────────────


def _make_session(risk_validator):
    broker = MagicMock()
    om = OrderManager()
    om.register_broker("test_broker", broker)
    return TradingSession(
        broker=broker,
        strategy=MagicMock(),
        risk_validator=risk_validator,
        signal_provider=lambda symbols: {},
        price_provider=lambda symbols: {},
        order_manager=om,
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )


class TestTradingSessionRiskFailClosed:
    def test_validator_exception_blocks_order(self):
        """校验器异常 → Fail-Closed 拦单（True），不许 fail-open。"""
        validator = _FakeValidator(error=RuntimeError("boom"))
        session = _make_session(validator)
        assert session._is_blocked_by_risk("600519.SH", 0.05, {}) is True

    def test_clean_validation_allows_order(self):
        """校验通过（无 HALT）→ 不拦（False）。"""
        session = _make_session(_FakeValidator(violations=[]))
        assert session._is_blocked_by_risk("600519.SH", 0.05, {}) is False

    def test_halt_violation_blocks_order(self):
        """HALT 违规 → 拦单（既有行为回归钉）。"""
        session = _make_session(_FakeValidator(violations=[_halt_violation()]))
        assert session._is_blocked_by_risk("600519.SH", 0.05, {}) is True

    def test_validator_none_return_blocks_order(self):
        """红队批回归：校验器返回 None（非可迭代）→ Fail-Closed 拦单 True，
        TypeError 不向调用方泄漏（旧写法 HALT 扫描在 try 外抛出）。"""

        class BuggyNone:
            def validate_order(self, **kwargs):
                return None

        session = _make_session(BuggyNone())
        assert session._is_blocked_by_risk("600519.SH", 0.05, {}) is True


# ── ExecutionEngine：校验器异常 Fail-Closed 拒单 ───────────────────────────


class TestExecutionEngineFailClosed:
    def _make_engine(self, validator) -> tuple[ExecutionEngine, OrderManager, MagicMock]:
        broker = MagicMock()
        broker.submit_order.return_value = "brk-001"
        om = OrderManager()
        om.register_broker("test_broker", broker)
        engine = ExecutionEngine(order_manager=om, risk_validator=validator)
        return engine, om, broker

    def test_validator_exception_rejected_as_value_error(self):
        """校验器异常 → ValueError(fail-closed) 拒单，订单不到 broker。"""
        engine, om, broker = self._make_engine(_FakeValidator(error=RuntimeError("boom")))
        with pytest.raises(ValueError, match="fail-closed"):
            engine.execute_order(_make_order(), broker_id="test_broker")
        assert len(om.orders) == 0  # 订单未创建/未提交
        broker.submit_order.assert_not_called()

    def test_clean_validation_executes_order(self):
        """校验通过 → 正常执行（放行），broker 收到申报。"""
        engine, om, broker = self._make_engine(_FakeValidator(violations=[]))
        registered = om.create_order(
            symbol="510300.SH",
            strategy_id="test_strategy",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("8.10"),
            broker_id="test_broker",
        )
        result = engine.execute_order(registered, broker_id="test_broker")
        assert result == "brk-001"
        broker.submit_order.assert_called_once()
