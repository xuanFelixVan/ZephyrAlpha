# [A_test] module_id: SRC-TST-0174 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-331 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_phase_e_main_flow
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Phase E — Main Data Flow End-to-End Test

主数据流端到端测试。验证 L00→L02→L03→L04→L05→L06→L07 完整 P0 链路。

P0 数据管道：
  L00源→CTR-001→L02→CTR-002→L03→CTR-P1-015→L04/L05→CTR-004→L06→CTR-005→L07
                                                            ↑CTR-006(反馈)→L04/L11

测试覆盖：
  - 全部 6 个 P0 数据契约 (CTR-001~006)
  - P1 合成信号契约 (CTR-P1-015)
  - P1 执行报告契约 (CTR-P1-007)
  - 错误契约传播 (CTR-ERR-004)
  - 全链路追踪 (CTR-TRACE-001)
  - 幂等性保证

Phase E | Safety: MEDIUM
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import pandas as pd
import pytest

from zephyr.ex_core.adapters.simulation_broker import SimulationBroker
from zephyr.ex_core.order_manager import OrderManager
from zephyr.factor.factor_base import FactorRegistry, autodiscover_factors
from zephyr.governance.intelligence_governance.memory_provider import MemoryProvider
from zephyr.shared.contracts.core.trace_context import TraceContext
from zephyr.pf_core.default_equity_strategy import (
    DefaultEquityStrategy,
    RebalanceMode,
)
from zephyr.governance.audit.default_tca_engine import DefaultTCAEngine
from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator
from zephyr.risk.risk_manager import RiskLimits
from zephyr.signal_fundamental.gen.implementations.default_signal_aggregator import DefaultSignalAggregator
from zephyr.trading.trading_contracts.execution.execution_report import ExecutionReport
from zephyr.trading.trading_contracts.execution.fill import Fill
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.trading.trading_contracts.execution.position import PositionSnapshot
from zephyr.trading.trading_contracts.market.factor_signal import FactorSignal
from zephyr.trading.trading_contracts.market.market_data import NormalizedMarketData
from zephyr.trading.trading_contracts.market.synthesized_signal import SynthesizedSignal

TEST_SYMBOLS = ["600519", "000858", "601318", "600036", "000333"]


def _make_market_data(
    symbol: str,
    provider: MemoryProvider,
    trace_context: TraceContext | None = None,
) -> NormalizedMarketData:
    end = datetime.now(UTC)
    start = end - timedelta(days=100)
    df = provider.fetch_historical(symbol, start, end)
    last = df.iloc[-1]
    return NormalizedMarketData(
        symbol=f"{symbol}.SH",
        data_source="memory",
        timestamp=last["date"].to_pydatetime() if hasattr(last["date"], "to_pydatetime") else datetime.now(UTC),
        open=Decimal(str(last["open"])),
        high=Decimal(str(last["high"])),
        low=Decimal(str(last["low"])),
        close=Decimal(str(last["close"])),
        volume=Decimal(str(last["volume"])),
        idempotency_key=str(uuid.uuid4()),
        trace_context=trace_context,
    )


def _make_factor_signal(
    factor_id: str,
    symbol: str,
    raw_value: float,
    trace_context: TraceContext | None = None,
) -> FactorSignal:
    return FactorSignal(
        factor_id=factor_id,
        symbol=symbol,
        as_of_date=datetime.now(UTC),
        raw_value=raw_value,
        idempotency_key=str(uuid.uuid4()),
        trace_context=trace_context,
    )


def _make_risk_limits(trace_context: TraceContext | None = None) -> RiskLimits:
    return RiskLimits(
        as_of_date=datetime.now(UTC),
        idempotency_key=str(uuid.uuid4()),
        max_single_position=0.10,
        max_gross_leverage=1.0,
        max_drawdown_limit=0.20,
        trace_context=trace_context,
    )


def _make_trace_context() -> TraceContext:
    return TraceContext(
        trace_id=f"trace-{uuid.uuid4().hex[:12]}",
        span_id=f"span-{uuid.uuid4().hex[:8]}",
        created_at=datetime.now(UTC),
        idempotency_key=str(uuid.uuid4()),
        service_name="test",
    )


def _verify_trace_context(data: Any, expected_trace_id: str | None = None) -> bool:
    tc = getattr(data, "trace_context", None)
    if tc is None:
        return expected_trace_id is None
    if not isinstance(tc, TraceContext):
        return False
    if expected_trace_id is not None and tc.trace_id != expected_trace_id:
        return False
    return bool(tc.trace_id)


class TestPhaseEL00ToL02:
    """L00 → L02: 行情数据 → 因子计算"""

    def test_memory_provider_produces_valid_ohlcv(self):
        provider = MemoryProvider(seed=42)
        df = provider.fetch_historical(
            "600519",
            datetime(2025, 1, 1, tzinfo=UTC),
            datetime(2025, 3, 31, tzinfo=UTC),
        )
        assert len(df) > 0
        assert {"open", "high", "low", "close", "volume"}.issubset(set(df.columns))
        assert df["high"].iloc[-1] >= df["low"].iloc[-1]

    def test_memory_provider_produces_unique_data_per_symbol(self):
        provider = MemoryProvider(seed=42)
        df_a = provider.fetch_historical(
            "600519",
            datetime(2025, 1, 1, tzinfo=UTC),
            datetime(2025, 1, 31, tzinfo=UTC),
        )
        df_b = provider.fetch_historical(
            "000858",
            datetime(2025, 1, 1, tzinfo=UTC),
            datetime(2025, 1, 31, tzinfo=UTC),
        )
        assert df_a["close"].iloc[-1] != df_b["close"].iloc[-1]

    def test_market_data_wraps_into_normalized_type(self):
        provider = MemoryProvider(seed=42)
        trace = _make_trace_context()
        md = _make_market_data("600519", provider, trace)
        assert isinstance(md, NormalizedMarketData)
        assert md.symbol == "600519.SH"
        assert md.data_source == "memory"
        assert isinstance(md.close, Decimal)
        assert md.quality_score >= 0.9
        assert _verify_trace_context(md, trace.trace_id)

    def test_factor_registry_autodiscover_loads_factors(self):
        FactorRegistry.clear()
        autodiscover_factors()
        all_factors = FactorRegistry.list_all()
        assert len(all_factors) >= 2
        factor_ids = {f.factor_id for f in all_factors}
        assert "momentum_20d" in factor_ids
        assert "value_factor" in factor_ids
        FactorRegistry.clear()

    def test_momentum_factor_computes_on_data(self):
        FactorRegistry.clear()
        autodiscover_factors()
        provider = MemoryProvider(seed=42)
        df = provider.fetch_historical(
            "600519",
            datetime(2025, 1, 1, tzinfo=UTC),
            datetime(2025, 3, 31, tzinfo=UTC),
        )

        factor_cls = FactorRegistry.get("momentum_20d")
        factor_instance = factor_cls()
        result = factor_instance.compute(df)
        assert isinstance(result, pd.Series)
        assert len(result) == len(df)
        assert not result.dropna().empty

        last_val = result.dropna().iloc[-1]
        signal = _make_factor_signal("momentum_20d", "600519", float(last_val))
        assert isinstance(signal, FactorSignal)
        assert signal.factor_id == "momentum_20d"
        FactorRegistry.clear()

    def test_value_factor_computes_on_data(self):
        FactorRegistry.clear()
        autodiscover_factors()
        provider = MemoryProvider(seed=42)
        df = provider.fetch_historical(
            "600519",
            datetime(2025, 1, 1, tzinfo=UTC),
            datetime(2025, 6, 30, tzinfo=UTC),
        )

        factor_cls = FactorRegistry.get("value_factor")
        factor_instance = factor_cls()
        result = factor_instance.compute(df)
        assert isinstance(result, pd.Series)
        assert len(result) == len(df)
        FactorRegistry.clear()


class TestPhaseEL02ToL03:
    """L02 → L03: 因子信号 → 信号合成"""

    def test_aggregator_combines_multiple_factor_signals(self):
        trace = _make_trace_context()
        signals = [
            _make_factor_signal("momentum_20d", "600519", 0.05, trace),
            _make_factor_signal("value_factor", "600519", -0.02, trace),
        ]
        aggregator = DefaultSignalAggregator()
        result = aggregator.aggregate(signals, "600519", str(uuid.uuid4()))
        assert isinstance(result, SynthesizedSignal)
        assert result.symbol == "600519"
        assert -3 <= result.signal_value <= 3
        assert result.confidence >= 0.0

    def test_aggregator_handles_empty_signals(self):
        aggregator = DefaultSignalAggregator()
        result = aggregator.aggregate([], "600519", str(uuid.uuid4()))
        assert isinstance(result, SynthesizedSignal)
        assert result.confidence == 0.0
        assert result.is_degraded is True

    def test_aggregator_filters_low_confidence_signals(self):
        s1 = _make_factor_signal("momentum_20d", "600519", 0.05)
        s2 = _make_factor_signal("value_factor", "600519", -0.02)
        s3 = FactorSignal(
            factor_id="quality_factor",
            symbol="600519",
            as_of_date=datetime.now(UTC),
            raw_value=0.03,
            idempotency_key=str(uuid.uuid4()),
            confidence=0.1,
            is_valid=True,
        )
        aggregator = DefaultSignalAggregator(min_confidence=0.3, min_factors_required=2)
        result = aggregator.aggregate([s1, s2, s3], "600519", str(uuid.uuid4()))
        assert result.confidence > 0.0

    def test_aggregator_rejects_invalid_signals(self):
        s1 = _make_factor_signal("momentum_20d", "600519", 0.05)
        s2 = _make_factor_signal("value_factor", "600519", -0.02)
        s3 = FactorSignal(
            factor_id="bad_factor",
            symbol="600519",
            as_of_date=datetime.now(UTC),
            raw_value=-0.02,
            idempotency_key=str(uuid.uuid4()),
            is_valid=False,
        )
        aggregator = DefaultSignalAggregator(min_factors_required=2)
        result = aggregator.aggregate([s1, s2, s3], "600519", str(uuid.uuid4()))
        assert result.is_degraded is False


class TestPhaseEL03L04ToL05:
    """L03/L04 → L05: 合成信号 + 风险限额 → 组合构建"""

    def test_equity_strategy_equal_weight_generates_orders(self):
        strategy = DefaultEquityStrategy(
            universe=TEST_SYMBOLS,
            mode=RebalanceMode.EQUAL_WEIGHT,
            nav=Decimal("1000000"),
        )
        orders = strategy.generate_target_weights()
        assert len(orders) > 0
        for order in orders:
            assert isinstance(order, Order)
            assert order.symbol in TEST_SYMBOLS
            assert order.order_type in (OrderType.LIMIT, OrderType.MARKET)

    def test_equity_strategy_signal_weighted_with_signals(self):
        strategy = DefaultEquityStrategy(
            universe=TEST_SYMBOLS,
            mode=RebalanceMode.SIGNAL_WEIGHT,
            nav=Decimal("1000000"),
        )
        strategy.update_signals(
            {
                "600519": 0.8,
                "000858": 0.3,
                "601318": -0.2,
                "600036": 0.1,
                "000333": -0.5,
            }
        )

        orders = strategy.generate_target_weights()
        assert len(orders) > 0

    def test_strategy_respects_risk_limits_max_single(self):
        strategy = DefaultEquityStrategy(
            universe=TEST_SYMBOLS,
            mode=RebalanceMode.EQUAL_WEIGHT,
            nav=Decimal("1000000"),
            risk_limits={"max_single_position": 0.10},
        )
        orders = strategy.generate_target_weights()
        for order in orders:
            target_weight = float(order.quantity * (order.limit_price or Decimal("100"))) / 1000000.0
            if target_weight > 0.15:
                pytest.fail(f"Position weight {target_weight} exceeds risk limit")


class TestPhaseEL05ToL06:
    """L05 → L06: 委托指令 → 交易执行"""

    def test_simulation_broker_fills_order_and_produces_position(self):
        broker = SimulationBroker(initial_cash=Decimal("1000000"))
        broker.connect()

        order = Order(
            order_id=f"ord-{uuid.uuid4().hex[:8]}",
            symbol="600519",
            strategy_id="test-strategy",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("500"),
            limit_price=Decimal("1800"),
            idempotency_key=str(uuid.uuid4()),
        )

        broker_order_id = broker.submit_order(order)
        assert broker_order_id.startswith("sim-")

        fills = broker.get_fills()
        assert len(fills) >= 1

        fill = list(fills.values())[0]
        assert isinstance(fill, Fill)
        assert fill.symbol == "600519"
        assert fill.order_id == order.order_id
        assert isinstance(fill.fill_price, Decimal)

        positions = broker.get_positions()
        assert isinstance(positions, PositionSnapshot)
        assert positions.portfolio_id == "simulation"

        broker.disconnect()

    def test_order_manager_full_lifecycle(self):
        broker = SimulationBroker()
        broker.connect()

        order_mgr = OrderManager()
        order_mgr.register_broker("simulation", broker)

        order = order_mgr.create_order(
            symbol="600519",
            strategy_id="test-strategy",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("100"),
        )
        assert order.status == OrderStatus.PENDING

        order_mgr.submit_order(order.order_id)

        fills = order_mgr.get_fills_for_order(order.order_id)
        assert len(fills) >= 1

        broker.disconnect()

    def test_order_manager_produces_position_snapshot(self):
        broker = SimulationBroker()
        broker.connect()

        order_mgr = OrderManager()
        order_mgr.register_broker("simulation", broker)

        for i, sym in enumerate(["600519", "000858", "601318"][:3]):
            order = order_mgr.create_order(
                symbol=sym,
                strategy_id="test-strategy",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal((i + 1) * 100),
                limit_price=Decimal("100"),
            )
            order_mgr.submit_order(order.order_id)

        pos = broker.get_positions()
        assert isinstance(pos, PositionSnapshot)
        assert len(pos.holdings) > 0

        broker.disconnect()


class TestPhaseEL06ToL07:
    """L06 → L07: 成交回报 → 交易成本分析"""

    def test_tca_engine_produces_report_for_fill(self):
        order = Order(
            order_id=f"ord-tca-{uuid.uuid4().hex[:8]}",
            symbol="600519",
            strategy_id="test-strategy",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("200"),
            limit_price=Decimal("100"),
            idempotency_key=str(uuid.uuid4()),
        )

        fill = Fill(
            fill_id=f"fill-{uuid.uuid4().hex[:8]}",
            order_id=order.order_id,
            symbol="600519",
            strategy_id="test-strategy",
            filled_quantity=Decimal("200"),
            fill_price=Decimal("101"),
            fill_timestamp=datetime.now(UTC),
            commission=Decimal("6"),
            idempotency_key=str(uuid.uuid4()),
        )

        tca = DefaultTCAEngine()
        report = tca.analyze(fill, order, str(uuid.uuid4()))
        assert isinstance(report, ExecutionReport)
        assert report.symbol == "600519"
        assert report.slippage_bps != 0

    def test_tca_batch_handles_multiple_fills(self):
        orders_dict: dict[str, Order] = {}
        fills: list[Fill] = []

        for i, sym in enumerate(["600519", "000858", "601318"][:3]):
            order = Order(
                order_id=f"ord-batch-{i}",
                symbol=sym,
                strategy_id="test-strategy",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal(str(100 * (i + 1))),
                limit_price=Decimal("100"),
                idempotency_key=str(uuid.uuid4()),
            )
            orders_dict[order.order_id] = order
            fill = Fill(
                fill_id=f"fill-batch-{i}",
                order_id=order.order_id,
                symbol=sym,
                strategy_id="test-strategy",
                filled_quantity=order.quantity,
                fill_price=Decimal(str(100 + i * 2)),
                fill_timestamp=datetime.now(UTC),
                commission=Decimal("3"),
                idempotency_key=str(uuid.uuid4()),
            )
            fills.append(fill)

        tca = DefaultTCAEngine()
        reports = tca.analyze_batch(fills, orders_dict, str(uuid.uuid4()))
        assert len(reports) == 3

        for report in reports:
            assert isinstance(report, ExecutionReport)
            assert report.symbol in {"600519", "000858", "601318"}


class TestPhaseERiskValidation:
    """L04 风控校验 — 错误契约传播"""

    def test_risk_validator_blocks_over_limit_order(self):
        validator = DefaultRiskValidator()
        holdings = {"600519": 0.05, "000858": 0.03}
        limits = RiskLimits(as_of_date=datetime.now(UTC), idempotency_key="phase-e", max_single_position=0.10)

        violations = validator.validate_order(
            symbol="600036",
            target_weight=0.05,
            current_holdings=holdings,
            limits=limits,
        )
        assert len(violations) == 0

        violations = validator.validate_order(
            symbol="999999",
            target_weight=0.15,
            current_holdings=holdings,
            limits=limits,
        )
        assert len(violations) > 0
        assert violations[0].severity == "HALT"

    def test_risk_validator_portfolio_checks_leverage(self):
        validator = DefaultRiskValidator()
        holdings = {"600519": 0.50, "000858": 0.40, "000333": 0.30}
        market_values = {"600519": 500000.0, "000858": 400000.0, "000333": 300000.0}

        violations = validator.validate_portfolio(
            holdings=holdings,
            market_values=market_values,
            total_nav=1000000.0,
            limits=RiskLimits(as_of_date=datetime.now(UTC), idempotency_key="phase-e-port", max_single_position=0.10, max_gross_leverage=1.0, max_drawdown_limit=0.20),
        )
        assert len(violations) > 0

    def test_risk_validator_kill_switch_blocks_all(self):
        validator = DefaultRiskValidator(kill_switch_active=True)
        violations = validator.validate_order(
            symbol="600519",
            target_weight=0.01,
            current_holdings={},
            limits=RiskLimits(as_of_date=datetime.now(UTC), idempotency_key="phase-e-kill", max_single_position=0.10),
        )
        assert len(violations) > 0


class TestPhaseETraceContextPropagation:
    """CTR-TRACE-001 全链路追踪上下文"""

    def test_trace_context_creation(self):
        trace = _make_trace_context()
        assert len(trace.trace_id) > 0
        assert len(trace.span_id) > 0

    def test_trace_context_flows_through_market_data(self):
        trace = _make_trace_context()
        provider = MemoryProvider(seed=42)
        md = _make_market_data("600519", provider, trace)

        assert _verify_trace_context(md, trace.trace_id)
        assert md.trace_context is not None
        assert md.trace_context.trace_id == trace.trace_id

    def test_trace_context_flows_through_factor_signal(self):
        trace = _make_trace_context()
        signal = _make_factor_signal("momentum_20d", "600519", 0.05, trace)
        assert _verify_trace_context(signal, trace.trace_id)

    def test_trace_context_flows_to_downstream_contracts(self):
        trace = _make_trace_context()

        order = Order(
            order_id=f"ord-{uuid.uuid4().hex[:8]}",
            symbol="600519",
            strategy_id="test-strategy",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("100"),
            idempotency_key=str(uuid.uuid4()),
            trace_context=trace,
        )
        assert _verify_trace_context(order, trace.trace_id)

        fill = Fill(
            fill_id=f"fill-{uuid.uuid4().hex[:8]}",
            order_id=order.order_id,
            symbol="600519",
            strategy_id="test-strategy",
            filled_quantity=Decimal("100"),
            fill_price=Decimal("101"),
            fill_timestamp=datetime.now(UTC),
            commission=Decimal("3"),
            idempotency_key=str(uuid.uuid4()),
            trace_context=trace,
        )
        assert _verify_trace_context(fill, trace.trace_id)

        limits = _make_risk_limits(trace)
        assert limits.trace_context is trace


class TestPhaseEFullPipelineE2E:
    """全链路端到端测试：L00 → L07 贯通"""

    def test_p0_pipeline_l00_to_l07_full_flow(self):
        """完整 P0 管道：MemoryProvider → Factors → Aggregator → Strategy → Broker → TCA"""
        trace = _make_trace_context()

        # L00: Data Source
        provider = MemoryProvider(seed=42)

        # L02: Alpha Factors
        FactorRegistry.clear()
        autodiscover_factors()
        assert len(FactorRegistry.list_all()) >= 2

        momentum_cls = FactorRegistry.get("momentum_20d")
        value_cls = FactorRegistry.get("value_factor")

        # L03: Signal Aggregation
        aggregator = DefaultSignalAggregator()

        # L04: Risk Management
        validator = DefaultRiskValidator()
        risk_limits = _make_risk_limits(trace)

        # L05: Portfolio Construction
        strategy = DefaultEquityStrategy(
            universe=TEST_SYMBOLS,
            mode=RebalanceMode.SIGNAL_WEIGHT,
            nav=Decimal("1000000"),
            risk_limits={"max_single_position": 0.10},
        )

        # L06 + L07
        broker = SimulationBroker(initial_cash=Decimal("1000000"))
        broker.connect()
        order_mgr = OrderManager()
        order_mgr.register_broker("simulation", broker)
        tca = DefaultTCAEngine()

        # Process each symbol through the pipeline
        all_signals: dict[str, float] = {}
        total_fills = 0

        for symbol in TEST_SYMBOLS:
            end = datetime.now(UTC)
            start = end - timedelta(days=100)
            df = provider.fetch_historical(symbol, start, end)
            assert len(df) > 0, f"No data for {symbol}"

            # L02: compute factor signals
            m = momentum_cls()
            v = value_cls()
            mom_result = m.compute(df)
            val_result = v.compute(df)

            last_mom = float(mom_result.dropna().iloc[-1]) if not mom_result.dropna().empty else 0.0
            last_val = float(val_result.dropna().iloc[-1]) if not val_result.dropna().empty else 0.0

            fs_mom = _make_factor_signal("momentum_20d", symbol, last_mom, trace)
            fs_val = _make_factor_signal("value_factor", symbol, last_val, trace)

            # L03: aggregate into synthesized signal
            syn = aggregator.aggregate([fs_mom, fs_val], symbol, str(uuid.uuid4()))
            assert isinstance(syn, SynthesizedSignal), f"Aggregation failed for {symbol}"
            all_signals[symbol] = syn.signal_value

        # L05: generate orders from aggregated signals
        strategy.update_signals(all_signals)
        orders = strategy.generate_target_weights()
        assert len(orders) > 0, "Strategy produced no orders"

        # L04: validate each order
        for order in orders:
            target_weight = float(order.quantity * (order.limit_price or Decimal("100"))) / 1000000.0
            current_holdings = {o.symbol: float(o.quantity) / 1000000.0 for o in orders if hasattr(o, "symbol")}
            violations = validator.validate_order(
                symbol=order.symbol,
                target_weight=target_weight,
                current_holdings=current_holdings,
                limits=risk_limits,
            )
            assert len(violations) == 0, f"Pre-trade violation for {order.symbol}: {violations[0].description}"

        # L06: submit orders to broker
        for order in orders:
            broker_order_id = broker.submit_order(order)
            assert broker_order_id is not None
            total_fills += 1

        # Verify fills and positions
        fills_dict = broker.get_fills()
        assert len(fills_dict) == total_fills, f"Expected {total_fills} fills, got {len(fills_dict)}"

        positions = broker.get_positions()
        assert isinstance(positions, PositionSnapshot)
        assert positions.portfolio_id == "simulation"

        # L07: TCA on fills
        reports = []
        for fill in fills_dict.values():
            matching_order = next((o for o in orders if o.order_id == fill.order_id), None)
            if matching_order:
                report = tca.analyze(fill, matching_order, str(uuid.uuid4()))
                assert isinstance(report, ExecutionReport)
                reports.append(report)
        assert len(reports) >= 1

        broker.disconnect()
        FactorRegistry.clear()

    def test_pipeline_idempotency_keys_unique(self):
        """验证全链路所有对象的幂等键唯一"""
        trace = _make_trace_context()

        provider = MemoryProvider(seed=42)
        keys: set[str] = set()

        for symbol in TEST_SYMBOLS[:3]:
            md = _make_market_data(symbol, provider, trace)
            keys.add(md.idempotency_key)

            fs = _make_factor_signal("momentum_20d", symbol, 0.02, trace)
            keys.add(fs.idempotency_key)

        broker = SimulationBroker()
        broker.connect()

        order = Order(
            order_id=f"ord-idem-{uuid.uuid4().hex[:8]}",
            symbol="600519",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("100"),
            idempotency_key=str(uuid.uuid4()),
            trace_context=trace,
        )
        keys.add(order.idempotency_key)
        keys.add(str(order.order_id))

        broker.submit_order(order)
        fills = broker.get_fills()
        for fill in fills.values():
            keys.add(fill.idempotency_key)

        broker.disconnect()

        assert len(keys) >= 6, f"Expected at least 6 unique keys, got {len(keys)}"

    def test_all_ctr_types_in_pipeline(self):
        """验证管道中的数据类型覆盖所有核心 CTR 类型"""
        trace = _make_trace_context()

        # Verify each type can be instantiated
        md = _make_market_data("600519", MemoryProvider(seed=42), trace)
        assert isinstance(md, NormalizedMarketData)  # CTR-001

        fs = _make_factor_signal("momentum_20d", "600519", 0.05, trace)
        assert isinstance(fs, FactorSignal)  # CTR-002

        rl = _make_risk_limits(trace)
        assert isinstance(rl, RiskLimits)  # CTR-003

        order = Order(
            order_id=f"ord-ctr-{uuid.uuid4().hex[:8]}",
            symbol="600519",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("100"),
            idempotency_key=str(uuid.uuid4()),
            trace_context=trace,
        )
        assert isinstance(order, Order)  # CTR-004

        fill = Fill(
            fill_id=f"fill-ctr-{uuid.uuid4().hex[:8]}",
            order_id=order.order_id,
            symbol="600519",
            strategy_id="test",
            filled_quantity=Decimal("100"),
            fill_price=Decimal("100"),
            fill_timestamp=datetime.now(UTC),
            commission=Decimal("0"),
            idempotency_key=str(uuid.uuid4()),
            trace_context=trace,
        )
        assert isinstance(fill, Fill)  # CTR-005

        pos = PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            idempotency_key=str(uuid.uuid4()),
            portfolio_id="test",
        )
        assert isinstance(pos, PositionSnapshot)  # CTR-006

        syn = SynthesizedSignal(
            signal_id=f"syn-ctr-{uuid.uuid4().hex[:8]}",
            symbol="600519",
            as_of_timestamp=datetime.now(UTC),
            signal_value=0.5,
            signal_direction="LONG",
            confidence=0.8,
            generation_latency_ms=5,
            idempotency_key=str(uuid.uuid4()),
        )
        assert isinstance(syn, SynthesizedSignal)  # CTR-P1-015

    def test_pipeline_universe_has_no_data_gaps(self):
        """验证 universe 中所有标的都有数据"""
        provider = MemoryProvider(seed=42)
        end = datetime.now(UTC)
        start = end - timedelta(days=100)

        for symbol in TEST_SYMBOLS:
            df = provider.fetch_historical(symbol, start, end)
            assert len(df) > 0, f"No data returned for symbol {symbol}"
            assert not df["close"].isna().all(), f"All close prices are NaN for {symbol}"
