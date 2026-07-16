# [A_test] module_id: SRC-TST-1205 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md | §test
# [MODULE] zephyr.signal
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l03_signal_generation.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime

import pytest

aggregator_base = pytest.importorskip("zephyr.signal_fundamental.gen.aggregator_base")
signal_synthesizer = pytest.importorskip("zephyr.signal_fundamental.synth.signal_synthesizer")
degradation_monitor_base_mod = pytest.importorskip("zephyr.signal_quality.degradation_monitor_base")

SignalAggregatorBase = aggregator_base.SignalAggregatorBase
CapitalAllocatorBase = aggregator_base.CapitalAllocatorBase
DegradationMonitorBase = degradation_monitor_base_mod.DegradationMonitorBase

SignalSynthesizerBase = signal_synthesizer.SignalSynthesizerBase

try:
    from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult
    from zephyr.trading.trading_contracts.market.factor_signal import FactorSignal
    from zephyr.trading.trading_contracts.market.synthesized_signal import SynthesizedSignal

    HAS_CONTRACTS = True
except Exception:
    HAS_CONTRACTS = False


class TestSignalAggregatorBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            SignalAggregatorBase()

    def test_normalize_signal_within_range(self):
        result = SignalAggregatorBase.normalize_signal(1.5)
        assert result == 1.5

    def test_normalize_signal_clips_high(self):
        result = SignalAggregatorBase.normalize_signal(5.0)
        assert result == 3.0

    def test_normalize_signal_clips_low(self):
        result = SignalAggregatorBase.normalize_signal(-5.0)
        assert result == -3.0

    def test_normalize_signal_custom_range(self):
        result = SignalAggregatorBase.normalize_signal(10.0, clip_range=(-1.0, 1.0))
        assert result == 1.0

    def test_normalize_signal_at_boundary(self):
        assert SignalAggregatorBase.normalize_signal(3.0) == 3.0
        assert SignalAggregatorBase.normalize_signal(-3.0) == -3.0

    @pytest.mark.skipif(not HAS_CONTRACTS, reason="Trading contracts not importable")
    def test_concrete_subclass(self):
        class MockAggregator(SignalAggregatorBase):
            def aggregate(self, factor_signals, symbol, idempotency_key):
                total = sum(fs.raw_value for fs in factor_signals)
                norm = self.normalize_signal(total)
                return SynthesizedSignal(
                    signal_id=f"sig-{symbol}",
                    symbol=symbol,
                    signal_value=norm,
                    signal_direction="LONG" if norm > 0 else "SHORT",
                    confidence=0.8,
                    idempotency_key=idempotency_key,
                    as_of_timestamp=datetime.now(UTC),
                    generation_latency_ms=10,
                )

        agg = MockAggregator()
        signals = [
            FactorSignal(
                as_of_date=datetime.now(UTC),
                factor_id="f1",
                idempotency_key="ik1",
                raw_value=0.5,
                symbol="AAPL",
            ),
            FactorSignal(
                as_of_date=datetime.now(UTC),
                factor_id="f2",
                idempotency_key="ik2",
                raw_value=0.3,
                symbol="AAPL",
            ),
        ]
        result = agg.aggregate(signals, "AAPL", "ik-agg-1")
        assert result.symbol == "AAPL"
        assert result.signal_value == 0.8


class TestCapitalAllocatorBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            CapitalAllocatorBase()

    @pytest.mark.skipif(not HAS_CONTRACTS, reason="Trading contracts not importable")
    def test_concrete_subclass(self):
        class EqualWeightAllocator(CapitalAllocatorBase):
            def allocate(self, signals, idempotency_key):
                n = len(signals)
                weight = 1.0 / n if n > 0 else 0.0
                allocs = {s.symbol: weight for s in signals}
                return CapitalAllocationResult(
                    allocation_date="2026-01-15",
                    total_allocated_weight=1.0,
                    allocation_method="equal_weight",
                    idempotency_key=idempotency_key,
                    strategy_allocations=allocs,
                )

        allocator = EqualWeightAllocator()
        synth_signals = [
            SynthesizedSignal(
                signal_id="s1",
                symbol="AAPL",
                signal_value=1.0,
                signal_direction="LONG",
                confidence=0.9,
                idempotency_key="ik1",
                as_of_timestamp=datetime.now(UTC),
                generation_latency_ms=5,
            ),
            SynthesizedSignal(
                signal_id="s2",
                symbol="GOOG",
                signal_value=-0.5,
                signal_direction="SHORT",
                confidence=0.8,
                idempotency_key="ik2",
                as_of_timestamp=datetime.now(UTC),
                generation_latency_ms=5,
            ),
        ]
        result = allocator.allocate(synth_signals, "ik-alloc-1")
        assert result.total_allocated_weight == 1.0
        assert result.allocation_method == "equal_weight"
        assert abs(result.strategy_allocations["AAPL"] - 0.5) < 1e-6


class TestDegradationMonitorBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            DegradationMonitorBase()


class TestSignalSynthesizerBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            SignalSynthesizerBase()

    def test_normalize_signal_within_range(self):
        assert SignalSynthesizerBase.normalize_signal(2.0) == 2.0

    def test_normalize_signal_clips_high(self):
        assert SignalSynthesizerBase.normalize_signal(5.0) == 3.0

    def test_normalize_signal_clips_low(self):
        assert SignalSynthesizerBase.normalize_signal(-5.0) == -3.0

    def test_normalize_signal_at_boundary(self):
        assert SignalSynthesizerBase.normalize_signal(3.0) == 3.0
        assert SignalSynthesizerBase.normalize_signal(-3.0) == -3.0

    def test_direction_from_value_long(self):
        assert SignalSynthesizerBase.direction_from_value(1.0) == "LONG"

    def test_direction_from_value_short(self):
        assert SignalSynthesizerBase.direction_from_value(-1.0) == "SHORT"

    def test_direction_from_value_neutral(self):
        assert SignalSynthesizerBase.direction_from_value(0.0) == "NEUTRAL"

    def test_direction_from_value_custom_threshold(self):
        assert SignalSynthesizerBase.direction_from_value(0.1, threshold=0.2) == "NEUTRAL"
        assert SignalSynthesizerBase.direction_from_value(0.3, threshold=0.2) == "LONG"

    def test_direction_from_value_at_threshold(self):
        assert SignalSynthesizerBase.direction_from_value(0.2001) == "LONG"
        assert SignalSynthesizerBase.direction_from_value(-0.2001) == "SHORT"
        assert SignalSynthesizerBase.direction_from_value(0.2) == "NEUTRAL"
        assert SignalSynthesizerBase.direction_from_value(-0.2) == "NEUTRAL"

    def test_default_idempotency_key(self):
        ts = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)
        key = SignalSynthesizerBase.default_idempotency_key("AAPL", ts)
        assert "AAPL" in key
        assert "syn-" in key

    @pytest.mark.skipif(not HAS_CONTRACTS, reason="Trading contracts not importable")
    def test_concrete_subclass(self):
        class EqualWeightSynthesizer(SignalSynthesizerBase):
            __synthesizer_id__ = "equal_weight"

            def synthesize(self, factor_signals, symbol, as_of_timestamp, weights=None):
                if not factor_signals:
                    val = 0.0
                else:
                    val = sum(fs.raw_value for fs in factor_signals) / len(factor_signals)
                norm_val = self.normalize_signal(val)
                direction = self.direction_from_value(norm_val)
                ik = self.default_idempotency_key(symbol, as_of_timestamp)
                return SynthesizedSignal(
                    signal_id=f"syn-{symbol}-{as_of_timestamp.isoformat()}",
                    symbol=symbol,
                    signal_value=norm_val,
                    signal_direction=direction,
                    confidence=0.8,
                    idempotency_key=ik,
                    as_of_timestamp=as_of_timestamp,
                    generation_latency_ms=5,
                )

        synth = EqualWeightSynthesizer()
        signals = [
            FactorSignal(
                as_of_date=datetime.now(UTC),
                factor_id="f1",
                idempotency_key="ik1",
                raw_value=1.5,
                symbol="AAPL",
            ),
        ]
        ts = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)
        result = synth.synthesize(signals, "AAPL", ts)
        assert result.symbol == "AAPL"
        assert result.signal_value == 1.5
        assert result.signal_direction == "LONG"

    @pytest.mark.skipif(not HAS_CONTRACTS, reason="Trading contracts not importable")
    def test_concrete_subclass_empty_signals(self):
        class EmptySynth(SignalSynthesizerBase):
            __synthesizer_id__ = "empty_synth"

            def synthesize(self, factor_signals, symbol, as_of_timestamp, weights=None):
                val = 0.0
                norm_val = self.normalize_signal(val)
                direction = self.direction_from_value(norm_val)
                return SynthesizedSignal(
                    signal_id="empty",
                    symbol=symbol,
                    signal_value=norm_val,
                    signal_direction=direction,
                    confidence=0.0,
                    idempotency_key="ik-empty",
                    as_of_timestamp=as_of_timestamp,
                    generation_latency_ms=0,
                )

        synth = EmptySynth()
        ts = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)
        result = synth.synthesize([], "AAPL", ts)
        assert result.signal_value == 0.0
        assert result.signal_direction == "NEUTRAL"
