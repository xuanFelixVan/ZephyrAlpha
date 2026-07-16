# [A_test] module_id: SRC-TST-0176 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-333 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_phase_g_perf
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Phase G — Performance Benchmarks & SLA Validation

性能基准与 SLA 验证。测量全链路延迟、吞吐量与内存占用，
对照 cross_layer_contracts.yaml 中声明的 p99_latency_ms 阈值进行合规检查。

SLA 阈值（来自 SSoT）：
  CTR-001 NormalizedMarketData   : p99 ≤ 10ms
  CTR-002 FactorSignal           : p99 ≤ 50ms
  CTR-003 RiskLimits             : p99 ≤ 5ms
  CTR-004 Order                  : p99 ≤ 5ms
  CTR-005 Fill                   : p99 ≤ 100ms
  CTR-006 PositionSnapshot       : p99 ≤ 50ms

基准测试策略：
  - 每层独立测量：warmup 3 次 + 正式 10 次，取中位数
  - 全链路一次贯通测量
  - 批量吞吐量：5/10/20/50 标的批量处理
  - 内存基线：sys.getsizeof + tracemalloc snapshot

Phase G | Safety: LOW (只读性能测量，不修改生产代码)
"""

from __future__ import annotations

import gc
import math
import statistics
import sys
import time
import tracemalloc
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from zephyr.ex_core.adapters.simulation_broker import SimulationBroker
from zephyr.factor.factor_base import FactorRegistry, autodiscover_factors
from zephyr.governance.security_governance.default_security_gateway import DefaultSecurityGateway
from zephyr.governance.intelligence_governance.memory_provider import MemoryProvider
from zephyr.infrastructure.system_telemetry.contract_metrics import ContractMetricsCollector
from zephyr.infrastructure.pipeline.backpressure_manager import BackpressureManager, emit_pause, emit_resume
from zephyr.shared.contracts.core.trace_context import TraceContext
from zephyr.intelligence.model_evaluation.implementations.default_inference_engine import DefaultInferenceEngine
from zephyr.pf_core.default_equity_strategy import (
    DefaultEquityStrategy,
    RebalanceMode,
)
from zephyr.governance.audit.default_tca_engine import DefaultTCAEngine
from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator
from zephyr.risk.risk_manager import RiskLimits
from zephyr.signal_fundamental.gen.implementations.default_signal_aggregator import DefaultSignalAggregator
from zephyr.backtest.core.engine_base import (
    BacktestResult,
)
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)
from zephyr.simulation.implementations.default_experiment_pipeline import DefaultExperimentPipeline
from zephyr.trading.trading_contracts.execution.fill import Fill
from zephyr.trading.trading_contracts.execution.model_serving_request import ModelServingRequest
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderType
from zephyr.trading.trading_contracts.execution.position import PositionSnapshot
from zephyr.shared.contracts.factor_signal import FactorSignal
from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal

ALL_SYMBOLS = [
    "600519",
    "000858",
    "601318",
    "600036",
    "000333",
    "601166",
    "600900",
    "601398",
    "600276",
    "000001",
    "600030",
    "000651",
    "601012",
    "600887",
    "002415",
    "300750",
    "688981",
    "000568",
    "600809",
    "002475",
    "603259",
    "600585",
    "300059",
    "601688",
    "600048",
    "000002",
    "002714",
    "300015",
    "601888",
    "600570",
    "688111",
    "300124",
    "002594",
    "601318",
    "600519",
    "600900",
    "000858",
    "600801",
    "002230",
    "300498",
    "601100",
    "600276",
    "002142",
    "601628",
    "600050",
    "000333",
    "688012",
    "300760",
    "002049",
    "600745",
]

SLA_THRESHOLDS: dict[str, float] = {
    "CTR-001": 10.0,
    "CTR-002": 50.0,
    "CTR-003": 5.0,
    "CTR-004": 5.0,
    "CTR-005": 100.0,
    "CTR-006": 50.0,
}


@dataclass
class PerfSample:
    label: str
    duration_ms: float
    samples: list[float] = field(default_factory=list)
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    mean_ms: float = 0.0
    stdev_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0


class PerfCollector:
    """性能样本收集器——多次运行统计 P50/P95/P99"""

    def __init__(self):
        self._records: dict[str, PerfSample] = {}

    def record(self, label: str, duration_ms: float) -> None:
        if label not in self._records:
            self._records[label] = PerfSample(label=label, duration_ms=duration_ms)
        self._records[label].samples.append(duration_ms)

    def finalize(self) -> dict[str, PerfSample]:
        for sample in self._records.values():
            if not sample.samples:
                continue
            sorted_samples = sorted(sample.samples)
            n = len(sorted_samples)

            def _percentile(p: float) -> float:
                k = (n - 1) * p
                f = int(math.floor(k))
                c = int(math.ceil(k))
                if f == c:
                    return sorted_samples[f]
                return sorted_samples[f] * (c - k) + sorted_samples[c] * (k - f)

            sample.p50_ms = statistics.median(sorted_samples)
            sample.p95_ms = _percentile(0.95)
            sample.p99_ms = _percentile(0.99)
            sample.mean_ms = statistics.mean(sorted_samples)
            sample.stdev_ms = statistics.stdev(sorted_samples) if n >= 2 else 0.0
            sample.min_ms = sorted_samples[0]
            sample.max_ms = sorted_samples[-1]
            sample.duration_ms = sample.p50_ms
        return self._records


@dataclass
class SlaReport:
    contract_id: str
    sla_threshold_ms: float
    measured_p99_ms: float
    passed: bool
    margin_pct: float
    sample_count: int


@contextmanager
def measure_ms(label: str, collector: PerfCollector) -> Iterator[None]:
    """上下文管理器：测量代码块执行时间（毫秒），异常时也记录"""
    t0 = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        collector.record(label, elapsed_ms)


def _make_trace() -> TraceContext:
    return TraceContext(
        trace_id=f"trace-{uuid.uuid4().hex[:12]}",
        span_id=f"span-{uuid.uuid4().hex[:8]}",
        created_at=datetime.now(UTC),
        idempotency_key=str(uuid.uuid4()),
        service_name="benchmark",
    )


def _make_factor_signal(
    factor_id: str,
    symbol: str,
    raw_value: float,
    trace: TraceContext | None = None,
) -> FactorSignal:
    return FactorSignal(
        factor_id=factor_id,
        symbol=symbol,
        as_of_date=datetime.now(UTC),
        raw_value=raw_value,
        idempotency_key=str(uuid.uuid4()),
        trace_context=trace,
    )


class TestPhaseGPerfFramework:
    """性能基准框架自验证"""

    def test_perf_collector_p50_p95_p99(self):
        collector = PerfCollector()
        for val in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
            collector.record("test", val)
        records = collector.finalize()
        s = records["test"]
        assert s.p50_ms == 5.5
        assert abs(s.p95_ms - 9.55) < 0.01
        assert s.p99_ms == 9.91
        assert s.min_ms == 1.0
        assert s.max_ms == 10.0

    def test_perf_collector_single_sample(self):
        collector = PerfCollector()
        collector.record("single", 42.0)
        records = collector.finalize()
        s = records["single"]
        assert s.p50_ms == 42.0
        assert s.p95_ms == 42.0
        assert s.mean_ms == 42.0
        assert s.stdev_ms == 0.0

    def test_perf_collector_empty_is_safe(self):
        collector = PerfCollector()
        records = collector.finalize()
        assert records == {}

    def test_measure_ms_context_manager(self):
        collector = PerfCollector()
        with measure_ms("ctx", collector):
            sum(range(10000))
        records = collector.finalize()
        assert "ctx" in records
        assert records["ctx"].duration_ms > 0.0

    def test_context_manager_preserves_exceptions(self):
        collector = PerfCollector()
        try:
            with measure_ms("exc", collector):
                raise ValueError("test")
        except ValueError:
            pass
        assert "exc" in collector._records


class TestPhaseGLatencyByLayer:
    """逐层延迟基准——L00→L13 独立测量"""

    @pytest.fixture(autouse=True)
    def _setup(self):
        FactorRegistry.clear()
        autodiscover_factors()
        yield
        FactorRegistry.clear()

    def test_l00_data_acquisition_latency(self):
        collector = PerfCollector()
        provider = MemoryProvider(seed=42)
        end = datetime.now(UTC)
        start = end - timedelta(days=100)

        for _ in range(3):
            provider.fetch_historical("600519", start, end)

        for symbol in ["600519", "000858", "601318", "600036", "000333"] * 2:
            with measure_ms("l00_fetch", collector):
                df = provider.fetch_historical(symbol, start, end)
                assert len(df) > 0

        records = collector.finalize()
        s = records["l00_fetch"]
        assert s.p99_ms < 50.0, f"L00 P99={s.p99_ms:.1f}ms exceeds 50ms"

    def test_l01_infrastructure_latency_fast_path(self):
        collector = PerfCollector()
        for _ in range(3):
            _make_trace()

        for _ in range(10):
            with measure_ms("l01_trace_create", collector):
                t = _make_trace()
                assert len(t.trace_id) > 0

        records = collector.finalize()
        s = records["l01_trace_create"]
        assert s.p99_ms < 5.0, f"L01 trace create P99={s.p99_ms:.1f}ms"

    def test_l02_factor_computation_latency(self):
        collector = PerfCollector()
        provider = MemoryProvider(seed=42)
        end = datetime.now(UTC)
        start = end - timedelta(days=100)

        momentum_cls = FactorRegistry.get("momentum_20d")
        value_cls = FactorRegistry.get("value_factor")

        m = momentum_cls()
        v = value_cls()

        for symbol in ALL_SYMBOLS[:3]:
            df = provider.fetch_historical(symbol, start, end)
            m.compute(df)
            v.compute(df)

        for symbol in ALL_SYMBOLS[:10] * 2:
            df = provider.fetch_historical(symbol, start, end)
            with measure_ms("l02_momentum", collector):
                result = m.compute(df)
                assert len(result) == len(df)
            with measure_ms("l02_value", collector):
                result = v.compute(df)
                assert len(result) == len(df)

        records = collector.finalize()
        assert records["l02_momentum"].p99_ms < 50.0, f"L02 momentum P99={records['l02_momentum'].p99_ms:.1f}ms"
        assert records["l02_value"].p99_ms < 50.0, f"L02 value P99={records['l02_value'].p99_ms:.1f}ms"

    def test_l03_signal_aggregation_latency(self):
        collector = PerfCollector()
        aggregator = DefaultSignalAggregator()
        trace = _make_trace()

        signals = [
            _make_factor_signal("momentum_20d", "600519", 0.05, trace),
            _make_factor_signal("value_factor", "600519", -0.02, trace),
        ]
        for _ in range(3):
            aggregator.aggregate(signals, "600519", str(uuid.uuid4()))

        for _ in range(20):
            with measure_ms("l03_aggregate", collector):
                result = aggregator.aggregate(signals, "600519", str(uuid.uuid4()))
                assert isinstance(result, SynthesizedSignal)

        records = collector.finalize()
        s = records["l03_aggregate"]
        assert s.p99_ms < 20.0, f"L03 aggregate P99={s.p99_ms:.1f}ms"

    def test_l04_risk_validation_latency(self):
        collector = PerfCollector()
        validator = DefaultRiskValidator()
        limits = RiskLimits(as_of_date=datetime.now(UTC), idempotency_key="perf-l04", max_single_position=0.10)

        for _ in range(3):
            validator.validate_order("600519", 0.05, {}, limits)

        for _ in range(30):
            with measure_ms("l04_validate_ok", collector):
                violations = validator.validate_order("600519", 0.05, {}, limits)
                assert len(violations) == 0

        records = collector.finalize()
        s = records["l04_validate_ok"]
        assert s.p99_ms < 5.0, f"L04 validate P99={s.p99_ms:.1f}ms"

    def test_l05_portfolio_construction_latency(self):
        collector = PerfCollector()
        strategy = DefaultEquityStrategy(
            universe=ALL_SYMBOLS[:10],
            mode=RebalanceMode.EQUAL_WEIGHT,
            nav=Decimal("1000000"),
        )
        for _ in range(3):
            strategy.generate_target_weights()

        for _ in range(10):
            with measure_ms("l05_generate_weights", collector):
                orders = strategy.generate_target_weights()
                assert len(orders) > 0

        records = collector.finalize()
        s = records["l05_generate_weights"]
        assert s.p99_ms < 20.0, f"L05 generate P99={s.p99_ms:.1f}ms"

    def test_l06_order_execution_latency(self):
        collector = PerfCollector()
        broker = SimulationBroker(initial_cash=Decimal("10000000"))
        broker.connect()

        orders = []
        for i, sym in enumerate(ALL_SYMBOLS[:10]):
            order = Order(
                order_id=f"ord-perf-{i}",
                symbol=sym,
                strategy_id="bench",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal(str(100 * (i + 1))),
                limit_price=Decimal("100"),
                idempotency_key=str(uuid.uuid4()),
            )
            orders.append(order)

        for _ in range(3):
            broker.submit_order(orders[0])
            broker.get_fills()

        for order in orders * 3:
            with measure_ms("l06_submit", collector):
                broker.submit_order(order)
            with measure_ms("l06_get_fills", collector):
                fills = broker.get_fills()

        broker.disconnect()

        records = collector.finalize()
        assert records["l06_submit"].p99_ms < 10.0, f"L06 submit P99={records['l06_submit'].p99_ms:.1f}ms"
        assert records["l06_get_fills"].p99_ms < 10.0, f"L06 fills P99={records['l06_get_fills'].p99_ms:.1f}ms"

    def test_l07_tca_latency(self):
        collector = PerfCollector()
        tca = DefaultTCAEngine()

        order = Order(
            order_id="ord-tca-perf",
            symbol="600519",
            strategy_id="bench",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("200"),
            limit_price=Decimal("100"),
            idempotency_key=str(uuid.uuid4()),
        )

        fill = Fill(
            fill_id="fill-tca-perf",
            order_id=order.order_id,
            symbol="600519",
            strategy_id="bench",
            filled_quantity=Decimal("200"),
            fill_price=Decimal("101"),
            fill_timestamp=datetime.now(UTC),
            commission=Decimal("6"),
            idempotency_key=str(uuid.uuid4()),
        )

        for _ in range(3):
            tca.analyze(fill, order, str(uuid.uuid4()))

        for _ in range(20):
            with measure_ms("l07_tca", collector):
                report = tca.analyze(fill, order, str(uuid.uuid4()))
                assert report.slippage_bps != 0

        records = collector.finalize()
        s = records["l07_tca"]
        assert s.p99_ms < 20.0, f"L07 TCA P99={s.p99_ms:.1f}ms"

    def test_l09_backtest_latency(self):
        collector = PerfCollector()
        engine = DefaultBacktestEngine(BacktestConfig())
        dates = pd.date_range("2025-01-01", "2025-06-30", freq="B")

        prices = pd.DataFrame(
            {
                "close": [100.0 + i * 0.2 for i in range(len(dates))],
                "open": [99.5 + i * 0.2 for i in range(len(dates))],
                "high": [101.0 + i * 0.2 for i in range(len(dates))],
                "low": [99.0 + i * 0.2 for i in range(len(dates))],
                "volume": [1000000.0 for _ in range(len(dates))],
            },
            index=dates,
        )

        signals = pd.DataFrame(
            {"600519": np.where(np.arange(len(dates)) % 40 < 20, 1.0, -1.0)},
            index=dates,
        )

        for _ in range(2):
            engine.run(signals=signals, data=prices, strategy_name="warmup")

        for _ in range(5):
            with measure_ms("l09_backtest", collector):
                result = engine.run(signals=signals, data=prices, strategy_name="bench")
                assert isinstance(result, BacktestResult)
                assert result.trades_count > 0

        records = collector.finalize()
        s = records["l09_backtest"]
        assert s.p99_ms < 100.0, f"L09 backtest P99={s.p99_ms:.1f}ms"

    def test_l10_security_gateway_latency(self):
        collector = PerfCollector()
        gw = DefaultSecurityGateway()

        test_queries = [
            "import numpy as np; x = np.array([1, 2, 3])",
            "os.system('rm -rf /')",
            "subprocess.call(['ls'])",
            "with open('config.txt', 'w') as f: f.write('test')",
        ]

        for q in test_queries * 2:
            gw.security_scan(q)
            gw.decide([], {})

        for q in test_queries * 10:
            with measure_ms("l10_scan", collector):
                gw.security_scan(q)
            with measure_ms("l10_decide", collector):
                gw.decide([], {})

        records = collector.finalize()
        assert records["l10_scan"].p99_ms < 5.0, f"L10 scan P99={records['l10_scan'].p99_ms:.1f}ms"
        assert records["l10_decide"].p99_ms < 5.0, f"L10 decide P99={records['l10_decide'].p99_ms:.1f}ms"

    def test_l11_inference_latency(self):
        collector = PerfCollector()
        engine = DefaultInferenceEngine()

        for _ in range(3):
            request = ModelServingRequest(
                request_id=f"req-warm-{uuid.uuid4().hex[:8]}",
                model_id="test",
                model_version="v1",
                input_features={"a": 1.0},
                idempotency_key=str(uuid.uuid4()),
            )
            engine.predict(request)

        for _ in range(20):
            request = ModelServingRequest(
                request_id=f"req-{uuid.uuid4().hex[:8]}",
                model_id="test",
                model_version="v1",
                input_features={"a": 1.0},
                idempotency_key=str(uuid.uuid4()),
            )
            with measure_ms("l11_predict", collector):
                response = engine.predict(request)

        records = collector.finalize()
        s = records["l11_predict"]
        assert s.p99_ms < 10.0, f"L11 predict P99={s.p99_ms:.1f}ms"

    def test_l12_contract_metrics_latency(self):
        collector = PerfCollector()
        metrics = ContractMetricsCollector()
        metrics.enable()
        metrics._field_baselines["CTR-002:signal_value"] = {"median": 0.01, "std": 0.1}

        for _ in range(3):
            metrics.measure_sla("CTR-001", "trace-warm", 1000, 10000)

        for _ in range(30):
            with measure_ms("l12_measure_sla", collector):
                metrics.measure_sla("CTR-001", "trace-ok", 1000, 10000)
            with measure_ms("l12_detect_drift", collector):
                metrics.detect_contract_drift("CTR-002", "signal_value", 0.02)

        records = collector.finalize()
        assert records["l12_measure_sla"].p99_ms < 5.0, f"L12 SLA measure P99={records['l12_measure_sla'].p99_ms:.1f}ms"
        assert records["l12_detect_drift"].p99_ms < 5.0, f"L12 drift P99={records['l12_detect_drift'].p99_ms:.1f}ms"

    def test_l13_experiment_latency(self):
        collector = PerfCollector()
        pipeline = DefaultExperimentPipeline()

        from zephyr.simulation.pipeline_base import ExperimentConfig

        config = ExperimentConfig(
            experiment_id="exp-perf",
            hypothesis="Test",
            control_params={"sharpe_ratio": 1.0, "max_drawdown": 0.15},
            treatment_params={"sharpe_ratio": 1.2, "max_drawdown": 0.12},
            metrics=["sharpe_ratio", "max_drawdown"],
            start_date="2025-01-01",
            end_date="2025-03-31",
        )

        for _ in range(2):
            pipeline.run(config, str(uuid.uuid4()))

        for _ in range(5):
            with measure_ms("l13_experiment", collector):
                results = pipeline.run(config, str(uuid.uuid4()))
                assert len(results) == 2

        records = collector.finalize()
        s = records["l13_experiment"]
        assert s.p99_ms < 20.0, f"L13 experiment P99={s.p99_ms:.1f}ms"


class TestPhaseGFullPipelineThroughput:
    """全链路吞吐量与批量处理基准"""

    @pytest.fixture(autouse=True)
    def _setup(self):
        FactorRegistry.clear()
        autodiscover_factors()
        yield
        FactorRegistry.clear()

    def test_pipeline_single_symbol_end_to_end(self):
        """单标的全链路 E2E 总延迟（L00→L07 不包括 L09-L13）"""
        trace = _make_trace()
        provider = MemoryProvider(seed=42)
        FactorRegistry.clear()
        autodiscover_factors()

        momentum_cls = FactorRegistry.get("momentum_20d")
        value_cls = FactorRegistry.get("value_factor")
        aggregator = DefaultSignalAggregator()
        validator = DefaultRiskValidator()
        strategy = DefaultEquityStrategy(
            universe=["600519"],
            mode=RebalanceMode.SIGNAL_WEIGHT,
            nav=Decimal("1000000"),
        )
        broker = SimulationBroker()
        broker.connect()
        tca = DefaultTCAEngine()

        collector = PerfCollector()
        end = datetime.now(UTC)
        start = end - timedelta(days=100)

        for _ in range(3):
            df = provider.fetch_historical("600519", start, end)
            m = momentum_cls()
            v = value_cls()
            m.compute(df)
            v.compute(df)

        for _ in range(10):
            with measure_ms("pipeline_full", collector):
                df = provider.fetch_historical("600519", start, end)
                m = momentum_cls()
                v = value_cls()
                mom_result = m.compute(df)
                val_result = v.compute(df)
                last_mom = float(mom_result.dropna().iloc[-1]) if not mom_result.dropna().empty else 0.0
                last_val = float(val_result.dropna().iloc[-1]) if not val_result.dropna().empty else 0.0

                fs_mom = _make_factor_signal("momentum_20d", "600519", last_mom, trace)
                fs_val = _make_factor_signal("value_factor", "600519", last_val, trace)
                syn = aggregator.aggregate([fs_mom, fs_val], "600519", str(uuid.uuid4()))

                strategy.update_signals({"600519": syn.signal_value})
                orders = strategy.generate_target_weights()

                for order in orders:
                    violations = validator.validate_order(
                        symbol=order.symbol,
                        target_weight=0.05,
                        current_holdings={},
                        limits=RiskLimits(as_of_date=datetime.now(UTC), idempotency_key="perf-batch", max_single_position=0.10),
                    )
                    assert len(violations) == 0
                    broker.submit_order(order)

                fills = broker.get_fills()
                for fill in fills.values():
                    matching = next((o for o in orders if o.order_id == fill.order_id), None)
                    if matching:
                        tca.analyze(fill, matching, str(uuid.uuid4()))

        broker.disconnect()

        records = collector.finalize()
        s = records["pipeline_full"]
        assert s.p50_ms < 50.0, f"Pipeline P50={s.p50_ms:.1f}ms (full L00→L07)"
        FactorRegistry.clear()

    def test_throughput_batch_n_symbols(self):
        """批量处理 N 个标的的吞吐量基准"""
        provider = MemoryProvider(seed=42)
        FactorRegistry.clear()
        autodiscover_factors()
        aggregator = DefaultSignalAggregator()
        end = datetime.now(UTC)
        start = end - timedelta(days=100)

        results: dict[int, float] = {}

        for batch_size in [5, 10, 20, 50]:
            symbols = ALL_SYMBOLS[:batch_size]
            collector = PerfCollector()

            for _ in range(min(3, max(1, 50 // batch_size))):
                for sym in symbols:
                    df = provider.fetch_historical(sym, start, end)
                    m = FactorRegistry.get("momentum_20d")()
                    v = FactorRegistry.get("value_factor")()
                    m.compute(df)
                    v.compute(df)

            with measure_ms(f"batch_{batch_size}", collector):
                for sym in symbols:
                    df = provider.fetch_historical(sym, start, end)
                    m = FactorRegistry.get("momentum_20d")()
                    v = FactorRegistry.get("value_factor")()
                    mom = float(m.compute(df).dropna().iloc[-1]) if not m.compute(df).dropna().empty else 0.0
                    val = float(v.compute(df).dropna().iloc[-1]) if not v.compute(df).dropna().empty else 0.0
                    signals = [
                        _make_factor_signal("momentum_20d", sym, mom),
                        _make_factor_signal("value_factor", sym, val),
                    ]
                    aggregator.aggregate(signals, sym, str(uuid.uuid4()))

            records = collector.finalize()
            total_ms = records[f"batch_{batch_size}"].p50_ms
            per_symbol_ms = total_ms / batch_size
            results[batch_size] = per_symbol_ms

        assert results[5] < 50.0, f"5 symbols: {results[5]:.1f}ms/symbol, too slow"
        assert results[10] < 50.0, f"10 symbols: {results[10]:.1f}ms/symbol, too slow"
        FactorRegistry.clear()

    def test_backpressure_signal_roundtrip(self):
        """背压信号往返延迟"""
        collector = PerfCollector()
        mgr = BackpressureManager()

        for _ in range(3):
            emit_pause(mgr, "600519", 10, "warmup")
            emit_resume(mgr, "600519", "warmup")

        for _ in range(50):
            with measure_ms("bp_pause_resume", collector):
                emit_pause(mgr, "000858", 10, "test")
                emit_resume(mgr, "000858", "done")

        mgr.clear()

        records = collector.finalize()
        s = records["bp_pause_resume"]
        assert s.p99_ms < 5.0, f"BP roundtrip P99={s.p99_ms:.1f}ms"


class TestPhaseGSLACompliance:
    """SLA 合规报告——验证各契约延迟是否满足声明阈值"""

    def test_sla_report_all_contracts(self):
        """生成完整 SLA 合规报告"""
        provider = MemoryProvider(seed=42)
        FactorRegistry.clear()
        autodiscover_factors()

        trace = _make_trace()
        end = datetime.now(UTC)
        start = end - timedelta(days=100)
        reports: list[SlaReport] = []

        # CTR-001: NormalizedMarketData
        collector = PerfCollector()
        for _ in range(5):
            with measure_ms("CTR-001", collector):
                df = provider.fetch_historical("600519", start, end)
                NormalizedMarketData(
                    symbol="600519.SH",
                    data_source="memory",
                    timestamp=end,
                    open=Decimal("1800"),
                    high=Decimal("1810"),
                    low=Decimal("1790"),
                    close=Decimal("1805"),
                    volume=Decimal("1000000"),
                    idempotency_key=str(uuid.uuid4()),
                    trace_context=trace,
                )
        r = collector.finalize()["CTR-001"]
        reports.append(
            SlaReport("CTR-001", 10.0, r.p99_ms, r.p99_ms <= 10.0, (10.0 - r.p99_ms) / 10.0 * 100, len(r.samples))
        )

        # CTR-002: FactorSignal
        collector = PerfCollector()
        for _ in range(20):
            with measure_ms("CTR-002", collector):
                _make_factor_signal("momentum_20d", "600519", 0.05, trace)
        r = collector.finalize()["CTR-002"]
        reports.append(
            SlaReport("CTR-002", 50.0, r.p99_ms, r.p99_ms <= 50.0, (50.0 - r.p99_ms) / 50.0 * 100, len(r.samples))
        )

        # CTR-003: RiskLimits
        collector = PerfCollector()
        validator = DefaultRiskValidator()
        for _ in range(30):
            with measure_ms("CTR-003", collector):
                validator.validate_order("600519", 0.05, {}, RiskLimits(as_of_date=datetime.now(UTC), idempotency_key="perf-ctr003", max_single_position=0.10))
        r = collector.finalize()["CTR-003"]
        reports.append(
            SlaReport("CTR-003", 5.0, r.p99_ms, r.p99_ms <= 5.0, (5.0 - r.p99_ms) / 5.0 * 100, len(r.samples))
        )

        # CTR-004: Order
        collector = PerfCollector()
        for _ in range(30):
            with measure_ms("CTR-004", collector):
                Order(
                    order_id=f"ord-sla-{uuid.uuid4().hex[:8]}",
                    symbol="600519",
                    strategy_id="test",
                    side=OrderSide.BUY,
                    order_type=OrderType.LIMIT,
                    quantity=Decimal("100"),
                    limit_price=Decimal("100"),
                    idempotency_key=str(uuid.uuid4()),
                )
        r = collector.finalize()["CTR-004"]
        reports.append(
            SlaReport("CTR-004", 5.0, r.p99_ms, r.p99_ms <= 5.0, (5.0 - r.p99_ms) / 5.0 * 100, len(r.samples))
        )

        # CTR-005: Fill
        broker = SimulationBroker()
        broker.connect()
        order = Order(
            order_id="ord-fill-sla",
            symbol="600519",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("1800"),
            idempotency_key=str(uuid.uuid4()),
        )
        broker.submit_order(order)
        fills = broker.get_fills()
        broker.disconnect()

        collector = PerfCollector()
        fill_template = list(fills.values())[0]
        for _ in range(30):
            with measure_ms("CTR-005", collector):
                Fill(
                    fill_id=f"fill-sla-{uuid.uuid4().hex[:8]}",
                    order_id=order.order_id,
                    symbol="600519",
                    strategy_id="test",
                    filled_quantity=Decimal("100"),
                    fill_price=Decimal("1800"),
                    fill_timestamp=datetime.now(UTC),
                    commission=Decimal("5"),
                    idempotency_key=str(uuid.uuid4()),
                )
        r = collector.finalize()["CTR-005"]
        reports.append(
            SlaReport("CTR-005", 100.0, r.p99_ms, r.p99_ms <= 100.0, (100.0 - r.p99_ms) / 100.0 * 100, len(r.samples))
        )

        # CTR-006: PositionSnapshot
        collector = PerfCollector()
        for _ in range(30):
            with measure_ms("CTR-006", collector):
                PositionSnapshot(
                    as_of_timestamp=datetime.now(UTC),
                    idempotency_key=str(uuid.uuid4()),
                    portfolio_id="test",
                )
        r = collector.finalize()["CTR-006"]
        reports.append(
            SlaReport("CTR-006", 50.0, r.p99_ms, r.p99_ms <= 50.0, (50.0 - r.p99_ms) / 50.0 * 100, len(r.samples))
        )

        failed = [rpt for rpt in reports if not rpt.passed]
        assert len(failed) == 0, (
            f"SLA violations: {[(f.contract_id, f'{f.measured_p99_ms:.1f}ms > {f.sla_threshold_ms}ms') for f in failed]}"
        )

        FactorRegistry.clear()

    def test_sla_violation_detected(self):
        """验证 L12 能正确检测 SLA 违规"""
        metrics = ContractMetricsCollector()
        metrics.enable()

        record_ok = metrics.measure_sla(
            contract_id="CTR-001",
            trace_id="trace-ok",
            latency_us=1000,
            sla_p99_us=10000,
        )
        assert record_ok.passed is True

        record_violation = metrics.measure_sla(
            contract_id="CTR-001",
            trace_id="trace-violation",
            latency_us=50000,
            sla_p99_us=10000,
        )
        assert record_violation.passed is False

    def test_contract_metrics_get_stats(self):
        """验证 L12 get_stats 聚合报告"""
        metrics = ContractMetricsCollector()
        metrics.enable()
        metrics._field_baselines["CTR-001:close"] = {"median": 100.0, "std": 10.0}

        metrics.measure_sla("CTR-001", "t1", 5000, 10000)
        metrics.measure_sla("CTR-001", "t2", 15000, 10000)
        metrics.measure_sla("CTR-002", "t3", 3000, 50000)
        metrics.record_violation("CTR-001")
        metrics.detect_contract_drift("CTR-001", "close", 500.0)

        stats = metrics.get_stats()
        assert stats["total_violations"] >= 1
        assert stats["active_drift_alerts"] >= 0
        assert stats["sla_p99_pass_rate_100"] >= 0

    def test_sla_collector_latency_distribution(self):
        """延迟分布统计——足够多的样本形成有效分布"""
        collector = PerfCollector()
        provider = MemoryProvider(seed=42)
        end = datetime.now(UTC)
        start = end - timedelta(days=100)

        FactorRegistry.clear()
        autodiscover_factors()

        for _ in range(3):
            provider.fetch_historical("600519", start, end)

        for _ in range(100):
            with measure_ms("l00_dist", collector):
                provider.fetch_historical("600519", start, end)

        records = collector.finalize()
        s = records["l00_dist"]
        assert len(s.samples) == 100
        assert s.p99_ms > s.p50_ms, "P99 should exceed P50"
        assert s.stdev_ms >= 0.0
        assert s.min_ms <= s.p50_ms <= s.max_ms
        FactorRegistry.clear()

    def test_full_pipeline_timing_summary(self):
        """打印完整的管线性能总结（不设硬断言，记录基线）"""
        provider = MemoryProvider(seed=42)
        FactorRegistry.clear()
        autodiscover_factors()
        end = datetime.now(UTC)
        start = end - timedelta(days=100)

        collector = PerfCollector()

        for sym in ALL_SYMBOLS[:10] * 2:
            with measure_ms("summary_data", collector):
                provider.fetch_historical(sym, start, end)

            m = FactorRegistry.get("momentum_20d")()
            v = FactorRegistry.get("value_factor")()
            df = provider.fetch_historical(sym, start, end)
            with measure_ms("summary_factor", collector):
                m.compute(df)

            with measure_ms("summary_order_create", collector):
                Order(
                    order_id=f"ord-{uuid.uuid4().hex[:8]}",
                    symbol=sym,
                    strategy_id="test",
                    side=OrderSide.BUY,
                    order_type=OrderType.LIMIT,
                    quantity=Decimal("100"),
                    limit_price=Decimal("100"),
                    idempotency_key=str(uuid.uuid4()),
                )

        records = collector.finalize()
        assert "summary_data" in records
        assert "summary_factor" in records
        assert "summary_order_create" in records

        FactorRegistry.clear()


class TestPhaseGMemoryBaseline:
    """内存占用基线"""

    def test_memory_provider_baseline(self):
        tracemalloc.start()
        gc.collect()
        snap_before = tracemalloc.take_snapshot()

        provider = MemoryProvider(seed=42)
        end = datetime.now(UTC)
        start = end - timedelta(days=252)

        for sym in ALL_SYMBOLS[:20]:
            provider.fetch_historical(sym, start, end)

        gc.collect()
        snap_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = snap_after.compare_to(snap_before, "lineno")
        total_diff = sum(s.size_diff for s in stats)
        total_kb = abs(total_diff) / 1024.0

        provider_size_kb = sys.getsizeof(provider) / 1024.0
        assert provider_size_kb < 1024.0, f"Provider memory {provider_size_kb:.1f}KB > 1MB"

    def test_dataclass_instance_memory(self):
        gc.collect()
        single_order = Order(
            order_id=f"ord-mem-{uuid.uuid4().hex[:8]}",
            symbol="600519",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("100"),
            idempotency_key=str(uuid.uuid4()),
        )
        order_size = sys.getsizeof(single_order)

        n = 1000
        orders = [
            Order(
                order_id=f"ord-bulk-{uuid.uuid4().hex[:8]}",
                symbol="600519",
                strategy_id="test",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("100"),
                limit_price=Decimal("100"),
                idempotency_key=str(uuid.uuid4()),
            )
            for _ in range(n)
        ]
        total_size = sys.getsizeof(orders) + sum(sys.getsizeof(o) for o in orders)
        per_order_kb = total_size / n / 1024.0

        assert per_order_kb < 2.0, f"Order memory {per_order_kb:.2f}KB each, too large"

    def test_backpressure_manager_memory(self):
        gc.collect()
        mgr = BackpressureManager()
        for sym in ALL_SYMBOLS[:50]:
            emit_pause(mgr, sym, 1000, "test")

        mgr_size_kb = sys.getsizeof(mgr) / 1024.0
        mgr.clear()
        assert mgr_size_kb < 1024.0, f"BackpressureManager memory {mgr_size_kb:.1f}KB > 1MB"

    def test_factor_registry_memory(self):
        FactorRegistry.clear()
        autodiscover_factors()

        registry_size_kb = sys.getsizeof(FactorRegistry._registry) / 1024.0
        assert registry_size_kb < 10.0, f"FactorRegistry memory {registry_size_kb:.2f}KB"

        FactorRegistry.clear()
