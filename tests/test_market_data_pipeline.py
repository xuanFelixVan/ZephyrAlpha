# [A_test] module_id: SRC-TST-1247 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-405 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_market_data_pipeline
# [INVARIANTS] MarketDataPipeline.run returns (dict, ValidationReport); feature_store grows on write
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_market_data_pipeline.py

from __future__ import annotations

from datetime import date

from zephyr.market_data.market_data_pipeline import (
    AkshareProvider,
    DataValidator,
    FeatureStoreSchema,
    Interval,
    MarketDataPipeline,
    ValidationReport,
    ValidationStatus,
)


class TestInterval:
    def test_all_intervals(self):
        expected = {"daily", "1min", "5min"}
        actual = {i.value for i in Interval}
        assert actual == expected


class TestValidationStatus:
    def test_all_statuses(self):
        expected = {"PASS", "WARN", "VIOLATED"}
        actual = {s.value for s in ValidationStatus}
        assert actual == expected


class TestValidationReport:
    def test_defaults(self):
        report = ValidationReport()
        assert report.completeness_ok is True
        assert report.status == ValidationStatus.PASS


class TestFeatureStoreSchema:
    def test_defaults(self):
        schema = FeatureStoreSchema()
        assert schema.symbol == ""
        assert schema.value == 0.0


class TestAkshareProvider:
    def test_fetch_returns_dict(self):
        provider = AkshareProvider()
        result = provider.fetch("AAPL", "2024-01-01", "2024-12-31")
        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"
        assert result["interval"] == "daily"

    def test_fetch_with_interval(self):
        provider = AkshareProvider()
        result = provider.fetch("AAPL", "2024-01-01", "2024-12-31", Interval.MINUTE_5)
        assert result["interval"] == "5min"


class TestDataValidator:
    def test_validate_returns_report(self):
        validator = DataValidator()
        report = validator.validate({"data": "test"})
        assert isinstance(report, ValidationReport)

    def test_check_completeness(self):
        assert DataValidator.check_completeness({"rows": 100}, 100) is True

    def test_check_timeliness(self):
        assert DataValidator.check_timeliness("2024-01-01T00:00:00") is True

    def test_check_validity(self):
        assert DataValidator.check_validity({"data": "test"}) is True

    def test_check_consistency(self):
        assert DataValidator.check_consistency([{"a": 1}, {"a": 2}]) is True


class TestMarketDataPipeline:
    def test_creation(self):
        pipeline = MarketDataPipeline()
        assert pipeline.feature_store == []

    def test_run_returns_tuple(self):
        pipeline = MarketDataPipeline()
        result = pipeline.run("AAPL", "2024-01-01", "2024-12-31")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], dict)
        assert isinstance(result[1], ValidationReport)

    def test_run_passes_validation(self):
        pipeline = MarketDataPipeline()
        _, report = pipeline.run("AAPL", "2024-01-01", "2024-12-31")
        assert report.status == ValidationStatus.PASS

    def test_write_to_feature_store(self):
        pipeline = MarketDataPipeline()
        schema = FeatureStoreSchema(symbol="AAPL", date=date.today(), factor_name="momentum", value=1.5)
        pipeline.write_to_feature_store(schema)
        assert len(pipeline.feature_store) == 1
        assert pipeline.feature_store[0].symbol == "AAPL"


class TestBoundary:
    def test_run_empty_symbol(self):
        pipeline = MarketDataPipeline()
        result, report = pipeline.run("", "2024-01-01", "2024-12-31")
        assert result["symbol"] == ""

    def test_feature_store_multiple_writes(self):
        pipeline = MarketDataPipeline()
        for i in range(5):
            pipeline.write_to_feature_store(FeatureStoreSchema(symbol=f"S{i}"))
        assert len(pipeline.feature_store) == 5
