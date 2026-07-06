# [A_test] module_id: SRC-TST-0167 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-324 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_e2e_pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
E2E 集成测试：全流水线贯通测试
=================================

测试场景：从数据源到 TCA 的完整 C-track 流水线。

测试链路：
  L00 (MockProvider) → L05 (DefaultEquityStrategy)
    → L04 (RiskValidator) → L06 (SimulationBroker + OrderManager)
      → L07 (DefaultTCAEngine)

设计原则：
  - 使用 Mock/Memory Provider 代替真实 Akshare，避免外部依赖
  - 所有 concrete class 实例化 + 方法调用验证
  - 验证 CTR 数据类型在链路各段正确传递

Phase D | Safety: MEDIUM
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pandas as pd

from zephyr.ex_core.adapters.simulation_broker import SimulationBroker
from zephyr.ex_core.execution_engine import (
    AlgoType,
    ExecutionConfig,
    ExecutionEngine,
)
from zephyr.ex_core.order_manager import OrderManager
from zephyr.governance.security_governance.default_security_gateway import (
    DefaultSecurityGateway,
)
from zephyr.governance.rule_enforcement.default_quality_gate import (
    DefaultQualityGate,
)
from zephyr.intelligence.model_evaluation.implementations.default_inference_engine import (
    DefaultInferenceEngine,
)
from zephyr.pf_core.default_equity_strategy import (
    DefaultEquityStrategy,
    RebalanceMode,
)
from zephyr.governance.audit.default_tca_engine import (
    DefaultTCAEngine,
)
from zephyr.risk.implementations.default_risk_limits_calculator import (
    DefaultRiskLimitsCalculator,
)
from zephyr.risk.implementations.default_risk_manager_orchestrator import (
    DefaultRiskManagerOrchestrator,
)
from zephyr.risk.implementations.default_risk_validator import (
    DefaultRiskValidator,
)
from zephyr.risk.risk_manager import RiskLimits
from zephyr.risk.stop_loss import evaluate_stop_loss
from zephyr.signal_fundamental.gen.implementations.default_signal_aggregator import (
    DefaultSignalAggregator,
)
from zephyr.signal_fundamental.strategy.implementations.default_capital_allocator import (
    AllocationMethod,
    DefaultCapitalAllocator,
)
from zephyr.backtest.implementations.vectorized_engine import (
    DefaultBacktestEngine,
)
from zephyr.simulation.implementations.default_experiment_pipeline import (
    DefaultExperimentPipeline,
)
from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult
from zephyr.trading.trading_contracts.execution.fill import Fill
from zephyr.trading.trading_contracts.execution.model_serving_request import ModelServingRequest
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.trading.trading_contracts.market.synthesized_signal import SynthesizedSignal

UNIVERSE_CSI300 = [
    "600519",
    "000858",
    "601318",
    "600036",
    "000333",
    "601166",
    "600900",
    "601398",
    "600276",
    "000001",  # top-10 representative
]


class TestE2EFullPipeline:
    """全流水线 E2E 测试"""

    def test_all_phases_import_successfully(self):
        """验证所有 Phase C concrete class 可正常导入"""
        assert SimulationBroker is not None
        assert DefaultRiskManagerOrchestrator is not None
        assert DefaultEquityStrategy is not None
        assert DefaultTCAEngine is not None
        assert DefaultSignalAggregator is not None
        assert DefaultCapitalAllocator is not None
        assert DefaultBacktestEngine is not None
        assert DefaultSecurityGateway is not None
        assert DefaultInferenceEngine is not None
        assert DefaultExperimentPipeline is not None

    def test_l06_broker_connect_and_submit(self):
        """L06: 模拟券商连接 + 下单 + 成交"""
        broker = SimulationBroker(initial_cash=Decimal("1000000"))
        broker.connect()

        order = Order(
            order_id="ord-test-001",
            symbol="600519",
            strategy_id="default-equity",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("1800"),
            idempotency_key=str(uuid.uuid4()),
        )

        broker_order_id = broker.submit_order(order)
        assert broker_order_id.startswith("sim-")

        fills = broker.get_fills()
        assert len(fills) == 1

        positions = broker.get_positions()
        assert positions is not None
        assert positions.total_market_value is not None

        broker.disconnect()

    def test_l05_integration_with_l06(self):
        """L05 + L06: 策略生成订单 → 券商执行"""
        broker = SimulationBroker(initial_cash=Decimal("1000000"))
        broker.connect()

        order_mgr = OrderManager()
        order_mgr.register_broker("simulation", broker)

        strategy = DefaultEquityStrategy(
            universe=UNIVERSE_CSI300[:5],
            mode=RebalanceMode.EQUAL_WEIGHT,
            nav=Decimal("1000000"),
        )

        orders = strategy.generate_target_weights()

        assert len(orders) > 0
        for order in orders:
            assert order.symbol in UNIVERSE_CSI300[:5]
            assert order.side in (OrderSide.BUY, OrderSide.SELL)
            assert order.quantity > 0
            broker.submit_order(order)

        fills = broker.get_fills()
        assert len(fills) >= 1

        broker.disconnect()

    def test_l04_risk_validator_pre_trade(self):
        """L04: 风险校验器拒绝超限订单"""
        validator = DefaultRiskValidator()

        holdings = {"600519": 0.08, "000858": 0.04}
        limits = RiskLimits(as_of_date=datetime.now(UTC), idempotency_key="e2e-pretrade", max_single_position=0.10)

        violations_normal = validator.validate_order(
            symbol="600036",
            target_weight=0.05,
            current_holdings=holdings,
            limits=limits,
        )
        assert len(violations_normal) == 0

        violations_over_limit = validator.validate_order(
            symbol="999999",
            target_weight=0.15,
            current_holdings=holdings,
            limits=limits,
        )
        assert len(violations_over_limit) > 0
        assert violations_over_limit[0].severity == "HALT"

    def test_l04_risk_validator_portfolio(self):
        """L04: 全组合风控校验"""
        validator = DefaultRiskValidator()

        holdings = {"600519": 0.12, "000858": 0.05, "000333": 0.05}
        market_values = {"600519": 120000.0, "000858": 50000.0, "000333": 50000.0}

        violations = validator.validate_portfolio(
            holdings=holdings,
            market_values=market_values,
            total_nav=1000000.0,
            limits=RiskLimits(as_of_date=datetime.now(UTC), idempotency_key="e2e-portfolio", max_single_position=0.10, max_gross_leverage=1.0, max_drawdown_limit=0.20),
        )

        assert len(violations) > 0

    def test_l07_tca_on_fill(self):
        """L07: TCA 引擎分析成交"""
        tca_engine = DefaultTCAEngine()

        order = Order(
            order_id="ord-tca-001",
            symbol="600519",
            strategy_id="default-equity",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("200"),
            limit_price=Decimal("100"),
            idempotency_key=str(uuid.uuid4()),
        )

        fill = Fill(
            fill_id="fill-tca-001",
            order_id="ord-tca-001",
            symbol="600519",
            strategy_id="default-equity",
            filled_quantity=Decimal("200"),
            fill_price=Decimal("101"),
            fill_timestamp=datetime.now(UTC),
            commission=Decimal("6"),
            idempotency_key=str(uuid.uuid4()),
        )

        report = tca_engine.analyze(fill, order, str(uuid.uuid4()))
        assert report is not None
        assert report.symbol == "600519"
        assert report.slippage_bps != 0

    def test_l04_stop_loss_trigger(self):
        """L04: 止损触发逻辑"""
        position = {"entry_price": 10.0, "qty": 100}
        rules = {"method": "fixed_pct", "stop_loss_pct": 0.05}
        assert evaluate_stop_loss(position, current_price=9.4, rules=rules) is True

    def test_l09_backtest_basic(self):
        """L09: 回测引擎基础运行"""
        engine = DefaultBacktestEngine()

        dates = pd.date_range("2025-01-01", periods=20, freq="B")
        data = pd.DataFrame(
            {
                "date": dates,
                "open": 100.0,
                "high": 102.0,
                "low": 98.0,
                "close": 101.0,
                "volume": 1000000,
            }
        ).set_index("date")

        signals = pd.DataFrame(
            1.0,
            index=dates,
            columns=["600519"],
        )

        result = engine.run(data, signals, initial_capital=1000000.0)
        assert result is not None
        assert result.sharpe_ratio is not None
        assert result.total_return is not None

    def test_l10_security_gateway_blocks(self):
        """L10: 安全网关阻断危险代码"""
        gateway = DefaultSecurityGateway()
        assert gateway.pre_filter("print('hello')", "test") is True

        risks = gateway.security_scan("os.system('rm -rf /')")
        assert len(risks) > 0
        assert any("BLOCK:" in r for r in risks)

        decision = gateway.decide(risks, {"source": "test"})
        assert decision.action is not None
        assert decision.action.name in ("BLOCK", "ALLOW", "FLAG")

    def test_l10_security_gateway_allow_safe(self):
        """L10: 安全网关放行安全代码"""
        gateway = DefaultSecurityGateway()
        risks = gateway.security_scan("print('hello world')")
        assert len(risks) == 0

        decision = gateway.decide(risks, {"source": "test"})
        assert decision.action.name == "ALLOW"

    def test_l11_inference_no_model(self):
        """L11: 推理引擎——模型未加载时返回空结果"""
        engine = DefaultInferenceEngine()
        request = ModelServingRequest(
            model_id="nonexistent",
            model_version="1.0",
            request_id=str(uuid.uuid4()),
            input_features={"feature_1": 0.5},
            idempotency_key=str(uuid.uuid4()),
        )
        result = engine.predict(request)
        assert result.confidence == 0.0

    def test_l13_experiment_pipeline(self):
        """L13: 实验管线 A/B 对照"""
        pipeline = DefaultExperimentPipeline()
        from zephyr.simulation.pipeline_base import ExperimentConfig

        config = ExperimentConfig(
            experiment_id="exp-test-001",
            hypothesis="Momentum factor >= 1.5x Sharpe",
            metrics=["sharpe", "max_dd"],
            control_params={"sharpe": 1.0, "max_dd": 0.15},
            treatment_params={"sharpe": 1.5, "max_dd": 0.10},
            start_date="2025-01-01",
            end_date="2025-06-30",
        )

        metrics = pipeline.run(config, str(uuid.uuid4()))
        assert len(metrics) >= 1
        assert metrics[0].p_value is not None


class TestCrossLayerContractAlignment:
    """跨层契约对齐测试"""

    def test_l04_produces_risk_limits_type(self):
        """L04 → CTR-003: RiskLimitsCalculator 输出正确的 RiskLimits 类型"""
        calculator = DefaultRiskLimitsCalculator()
        limits = calculator.calculate(
            positions={"600519": 0.8},
            market_values={"600519": 800000.0},
            total_nav=1000000.0,
        )
        assert isinstance(limits, RiskLimits)
        assert limits.max_single_position > 0

    def test_l03_produces_capital_allocation_type(self):
        """L03 → CTR-P1-003: CapitalAllocator 输出正确的 CapitalAllocationResult 类型"""
        allocator = DefaultCapitalAllocator(method=AllocationMethod.EQUAL)
        signal = SynthesizedSignal(
            signal_id="syn-001",
            symbol="600519",
            signal_value=0.8,
            signal_direction="COMPOSITE",
            confidence=0.9,
            as_of_timestamp=datetime.now(UTC),
            generation_latency_ms=5,
            idempotency_key=str(uuid.uuid4()),
            regime="momentum",
            suggested_position_pct=0.08,
            contributing_factors={"momentum": 0.6, "value": 0.4},
        )

        result = allocator.allocate([signal], str(uuid.uuid4()))
        assert isinstance(result, CapitalAllocationResult)
        assert len(result.strategy_allocations) > 0

    def test_l00_quality_gate_produces_report(self):
        """L00 → CTR-ERR-001: QualityGate 输出正确的 QualityReport"""
        from zephyr.data.quality_gate import QualityReport

        gate = DefaultQualityGate()
        report = gate.check(
            symbol="600519",
            open_price=100.0,
            high=102.0,
            low=99.0,
            close=101.0,
            volume=1000000,
            timestamp=datetime.now(UTC),
        )
        assert isinstance(report, QualityReport)
        assert report.quality_score > 0.5
        assert report.passed is True


class TestOrderManagerLifecycle:
    """订单管理器生命周期测试"""

    def test_full_lifecycle(self):
        """订单 PENDING → SUBMITTED → FILLED 全生命周期"""

        broker = SimulationBroker()
        broker.connect()

        order_mgr = OrderManager()
        order_mgr.register_broker("simulation", broker)

        order = order_mgr.create_order(
            symbol="600519",
            strategy_id="default-equity",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("500"),
            limit_price=Decimal("100"),
        )

        assert order.status == OrderStatus.PENDING
        order_mgr.submit_order(order.order_id)

        fills = order_mgr.get_fills_for_order(order.order_id)
        assert len(fills) >= 1

        broker.disconnect()

    def test_execution_engine_twap(self):
        """执行引擎：TWAP 算法单"""
        broker = SimulationBroker()
        broker.connect()

        order_mgr = OrderManager()
        order_mgr.register_broker("simulation", broker)

        config = ExecutionConfig(
            default_algo=AlgoType.TWAP,
            twap_window_minutes=30,
            twap_slices=4,
        )
        engine = ExecutionEngine(order_manager=order_mgr, risk_validator=DefaultRiskValidator(), config=config)

        order = order_mgr.create_order(
            symbol="600519",
            strategy_id="default-equity",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("400"),
            limit_price=Decimal("100"),
        )

        broker_order_id = engine.execute_order(order, algo=AlgoType.TWAP)
        assert broker_order_id is not None

        broker.disconnect()
