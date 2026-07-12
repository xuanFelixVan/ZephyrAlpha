# [A_test] module_id: SRC-TST-1248 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_market_event_integrator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.market_event_integrator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_market_event_integrator.py
# [TTL] task_bound

from zephyr.feedback_loop.collectors.market_event_integrator import (
    MarketEvent,
    MarketEventIntegrator,
    MarketMode,
)


class TestMarketModeEnum:
    def test_normal_value(self):
        assert MarketMode.NORMAL == "NORMAL"

    def test_caution_value(self):
        assert MarketMode.CAUTION == "CAUTION"

    def test_emergency_value(self):
        assert MarketMode.EMERGENCY == "EMERGENCY"

    def test_holiday_value(self):
        assert MarketMode.HOLIDAY == "HOLIDAY"


class TestMarketEventInstantiation:
    def test_market_event_fields(self):
        ev = MarketEvent(
            event_type="CIRCUIT_BREAKER",
            timestamp=1000.0,
            mode=MarketMode.EMERGENCY,
            description="Test event",
        )
        assert ev.event_type == "CIRCUIT_BREAKER"
        assert ev.timestamp == 1000.0
        assert ev.mode == MarketMode.EMERGENCY
        assert ev.description == "Test event"


class TestMarketEventIntegratorInstantiation:
    def test_default_state(self):
        integrator = MarketEventIntegrator()
        assert integrator.current_mode == MarketMode.NORMAL
        assert integrator.events == []


class TestMarketEventIntegratorOnCircuitBreaker:
    def test_sets_emergency_mode(self):
        integrator = MarketEventIntegrator()
        integrator.on_circuit_breaker("NYSE")
        assert integrator.current_mode == MarketMode.EMERGENCY

    def test_appends_event(self):
        integrator = MarketEventIntegrator()
        integrator.on_circuit_breaker("NYSE")
        assert len(integrator.events) == 1
        assert integrator.events[0].event_type == "CIRCUIT_BREAKER"
        assert "NYSE" in integrator.events[0].description

    def test_multiple_circuit_breakers(self):
        integrator = MarketEventIntegrator()
        integrator.on_circuit_breaker("NYSE")
        integrator.on_circuit_breaker("LSE")
        assert len(integrator.events) == 2


class TestMarketEventIntegratorOnFomc:
    def test_sets_caution_mode(self):
        integrator = MarketEventIntegrator()
        integrator.on_fomc()
        assert integrator.current_mode == MarketMode.CAUTION

    def test_appends_fomc_event(self):
        integrator = MarketEventIntegrator()
        integrator.on_fomc()
        assert len(integrator.events) == 1
        assert integrator.events[0].event_type == "FOMC"


class TestMarketEventIntegratorOnHoliday:
    def test_sets_holiday_mode(self):
        integrator = MarketEventIntegrator()
        integrator.on_holiday("Independence Day")
        assert integrator.current_mode == MarketMode.HOLIDAY

    def test_appends_holiday_event(self):
        integrator = MarketEventIntegrator()
        integrator.on_holiday("Christmas")
        assert len(integrator.events) == 1
        assert integrator.events[0].event_type == "HOLIDAY"
        assert "Christmas" in integrator.events[0].description


class TestMarketEventIntegratorShouldSuppressAnomaly:
    def test_normal_mode_suppresses_nothing(self):
        integrator = MarketEventIntegrator()
        assert integrator.should_suppress_anomaly("missing_data") is False
        assert integrator.should_suppress_anomaly("high_volatility") is False

    def test_holiday_mode_suppresses_missing_data(self):
        integrator = MarketEventIntegrator()
        integrator.on_holiday("New Year")
        assert integrator.should_suppress_anomaly("missing_data") is True
        assert integrator.should_suppress_anomaly("low_volume") is True

    def test_holiday_mode_does_not_suppress_high_volatility(self):
        integrator = MarketEventIntegrator()
        integrator.on_holiday("New Year")
        assert integrator.should_suppress_anomaly("high_volatility") is False

    def test_emergency_mode_suppresses_high_volatility(self):
        integrator = MarketEventIntegrator()
        integrator.on_circuit_breaker("NYSE")
        assert integrator.should_suppress_anomaly("high_volatility") is True
        assert integrator.should_suppress_anomaly("latency_spike") is True

    def test_emergency_mode_does_not_suppress_missing_data(self):
        integrator = MarketEventIntegrator()
        integrator.on_circuit_breaker("NYSE")
        assert integrator.should_suppress_anomaly("missing_data") is False

    def test_caution_mode_suppresses_nothing(self):
        integrator = MarketEventIntegrator()
        integrator.on_fomc()
        assert integrator.should_suppress_anomaly("missing_data") is False
        assert integrator.should_suppress_anomaly("high_volatility") is False

    def test_mode_transition_overrides_suppression(self):
        integrator = MarketEventIntegrator()
        integrator.on_holiday("Christmas")
        assert integrator.should_suppress_anomaly("missing_data") is True
        integrator.on_circuit_breaker("NYSE")
        assert integrator.should_suppress_anomaly("missing_data") is False
        assert integrator.should_suppress_anomaly("high_volatility") is True
