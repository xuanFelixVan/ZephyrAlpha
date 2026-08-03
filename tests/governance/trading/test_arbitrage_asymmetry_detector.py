# [A_test] module_id: MOD-GOV_arbitrage_asymmetry_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_arbitrage_asymmetry_detector
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_arbitrage_asymmetry_detector.py -q
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.financial_governance.arbitrage_asymmetry_detector import ArbitrageAsymmetryDetector


class TestArbitrageAsymmetryDetectorInstantiation:
    def test_creates_instance(self):
        detector = ArbitrageAsymmetryDetector()
        assert detector is not None

    def test_is_correct_type(self):
        detector = ArbitrageAsymmetryDetector()
        assert isinstance(detector, ArbitrageAsymmetryDetector)


class TestDetect:
    def test_detects_spread_above_threshold(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "exchange_a": {"BTC": 100.0, "ETH": 50.0},
            "exchange_b": {"BTC": 110.0, "ETH": 50.1},
        }
        results = detector.detect(prices, threshold_pct=0.5)
        btc_opps = [r for r in results if r["symbol"] == "BTC"]
        assert len(btc_opps) >= 1
        assert btc_opps[0]["spread_pct"] > 0.5

    def test_no_opportunity_below_threshold(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "exchange_a": {"BTC": 100.0},
            "exchange_b": {"BTC": 100.1},
        }
        results = detector.detect(prices, threshold_pct=1.0)
        assert len(results) == 0

    def test_custom_threshold(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "exchange_a": {"BTC": 100.0},
            "exchange_b": {"BTC": 101.0},
        }
        results_low = detector.detect(prices, threshold_pct=0.5)
        results_high = detector.detect(prices, threshold_pct=2.0)
        assert len(results_low) >= 1
        assert len(results_high) == 0

    def test_multiple_exchanges(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "ex_a": {"BTC": 100.0},
            "ex_b": {"BTC": 110.0},
            "ex_c": {"BTC": 105.0},
        }
        results = detector.detect(prices, threshold_pct=0.5)
        assert len(results) >= 2

    def test_different_symbols_per_exchange(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "ex_a": {"BTC": 100.0, "ETH": 50.0},
            "ex_b": {"BTC": 110.0},
        }
        results = detector.detect(prices, threshold_pct=0.5)
        symbols = {r["symbol"] for r in results}
        assert "BTC" in symbols
        assert "ETH" not in symbols

    def test_empty_prices_returns_empty(self):
        detector = ArbitrageAsymmetryDetector()
        results = detector.detect({}, threshold_pct=0.5)
        assert results == []

    def test_single_exchange_returns_empty(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {"ex_a": {"BTC": 100.0}}
        results = detector.detect(prices, threshold_pct=0.5)
        assert results == []

    def test_result_structure(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "ex_a": {"BTC": 100.0},
            "ex_b": {"BTC": 110.0},
        }
        results = detector.detect(prices, threshold_pct=0.5)
        assert len(results) >= 1
        r = results[0]
        assert "a" in r
        assert "b" in r
        assert "symbol" in r
        assert "spread_pct" in r


class TestBoundaryConditions:
    def test_zero_threshold_detects_any_spread(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "ex_a": {"BTC": 100.0},
            "ex_b": {"BTC": 100.001},
        }
        results = detector.detect(prices, threshold_pct=0.0)
        assert len(results) >= 1

    def test_identical_prices_no_spread(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "ex_a": {"BTC": 100.0},
            "ex_b": {"BTC": 100.0},
        }
        results = detector.detect(prices, threshold_pct=0.0)
        assert len(results) == 0

    def test_very_large_spread(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "ex_a": {"BTC": 1.0},
            "ex_b": {"BTC": 1000000.0},
        }
        results = detector.detect(prices, threshold_pct=0.5)
        assert len(results) >= 1
        assert results[0]["spread_pct"] > 99.0

    def test_negative_threshold_treated_as_no_spread(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "ex_a": {"BTC": 100.0},
            "ex_b": {"BTC": 110.0},
        }
        results = detector.detect(prices, threshold_pct=-1.0)
        assert len(results) >= 1

    def test_exchange_with_empty_symbol_dict(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "ex_a": {},
            "ex_b": {"BTC": 100.0},
        }
        results = detector.detect(prices, threshold_pct=0.5)
        assert results == []

    def test_spread_pct_rounded_to_two_decimals(self):
        detector = ArbitrageAsymmetryDetector()
        prices = {
            "ex_a": {"BTC": 100.0},
            "ex_b": {"BTC": 103.456},
        }
        results = detector.detect(prices, threshold_pct=0.5)
        if results:
            spread = results[0]["spread_pct"]
            assert spread == round(spread, 2)
