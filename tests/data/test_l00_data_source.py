# [A_test] module_id: MOD-GOV_l00_data_source | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/blueprint.md | §test
# [MODULE] zephyr.l00_data_source
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l00_data_source.py
# [TTL] task_bound

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

provider_base = pytest.importorskip("zephyr.l00_data_source.provider_base")
quality_gate = pytest.importorskip("zephyr.l00_data_source.quality_gate")

QuoteProviderBase = provider_base.QuoteProviderBase
QuoteProviderMeta = provider_base.QuoteProviderMeta

DataQualityGate = quality_gate.DataQualityGate
QualityReport = quality_gate.QualityReport
QualityFailureReason = quality_gate.QualityFailureReason
RecoveryHint = quality_gate.RecoveryHint


class TestQuoteProviderMeta:
    def test_create_frozen(self):
        meta = QuoteProviderMeta(
            provider_id="test_provider",
            provider_name="Test Provider",
            asset_classes=["equity"],
            markets=["US"],
        )
        assert meta.provider_id == "test_provider"
        assert meta.supports_realtime is False
        assert meta.supports_historical is True
        assert meta.supports_local is False
        assert meta.rate_limit_per_min == 60

    def test_frozen_immutable(self):
        meta = QuoteProviderMeta(
            provider_id="p1",
            provider_name="P1",
            asset_classes=["eq"],
            markets=["US"],
        )
        with pytest.raises(AttributeError):
            meta.provider_id = "changed"

    def test_with_realtime(self):
        meta = QuoteProviderMeta(
            provider_id="rt",
            provider_name="RT",
            asset_classes=["fx"],
            markets=["global"],
            supports_realtime=True,
        )
        assert meta.supports_realtime is True


class TestQuoteProviderBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            QuoteProviderBase()

    def test_concrete_subclass(self):
        class MockDataSource(QuoteProviderBase):
            __meta__ = QuoteProviderMeta(
                provider_id="mock",
                provider_name="Mock",
                asset_classes=["equity"],
                markets=["US"],
                supports_local=True,
            )

            def fetch_historical(self, symbol, start, end, interval="1d"):
                import pandas as pd

                return pd.DataFrame({"open": [1], "high": [2], "low": [0.5], "close": [1.5], "volume": [100]})

            def subscribe_realtime(self, symbols):
                pass

        ds = MockDataSource()
        df = ds.fetch_historical("AAPL", datetime(2026, 1, 1), datetime(2026, 1, 31))
        assert len(df) == 1
        assert "close" in df.columns

    def test_validate_schema_valid(self):
        class MockDataSource(QuoteProviderBase):
            __meta__ = QuoteProviderMeta(
                provider_id="mock2",
                provider_name="Mock2",
                asset_classes=["eq"],
                markets=["US"],
            )

            def fetch_historical(self, symbol, start, end, interval="1d"):
                import pandas as pd

                return pd.DataFrame()

            def subscribe_realtime(self, symbols):
                pass

        ds = MockDataSource()
        import pandas as pd

        valid_df = pd.DataFrame({"open": [1], "high": [2], "low": [0.5], "close": [1.5], "volume": [100]})
        assert ds.validate_schema(valid_df) is True

    def test_validate_schema_missing_columns(self):
        class MockDataSource(QuoteProviderBase):
            __meta__ = QuoteProviderMeta(
                provider_id="mock3",
                provider_name="Mock3",
                asset_classes=["eq"],
                markets=["US"],
            )

            def fetch_historical(self, symbol, start, end, interval="1d"):
                import pandas as pd

                return pd.DataFrame()

            def subscribe_realtime(self, symbols):
                pass

        ds = MockDataSource()
        import pandas as pd

        bad_df = pd.DataFrame({"open": [1], "close": [2]})
        assert ds.validate_schema(bad_df) is False

    def test_is_local_property(self):
        class LocalSource(QuoteProviderBase):
            __meta__ = QuoteProviderMeta(
                provider_id="local_src",
                provider_name="Local",
                asset_classes=["eq"],
                markets=["US"],
                supports_local=True,
            )

            def fetch_historical(self, symbol, start, end, interval="1d"):
                import pandas as pd

                return pd.DataFrame()

            def subscribe_realtime(self, symbols):
                pass

        ds = LocalSource()
        assert ds.is_local is True

    def test_is_local_default_false(self):
        class RemoteSource(QuoteProviderBase):
            __meta__ = QuoteProviderMeta(
                provider_id="remote_src",
                provider_name="Remote",
                asset_classes=["eq"],
                markets=["US"],
            )

            def fetch_historical(self, symbol, start, end, interval="1d"):
                import pandas as pd

                return pd.DataFrame()

            def subscribe_realtime(self, symbols):
                pass

        ds = RemoteSource()
        assert ds.is_local is False

    def test_is_local_no_meta(self):
        class NoMetaSource(QuoteProviderBase):
            def fetch_historical(self, symbol, start, end, interval="1d"):
                import pandas as pd

                return pd.DataFrame()

            def subscribe_realtime(self, symbols):
                pass

        ds = NoMetaSource()
        assert ds.is_local is False


class TestQualityFailureReason:
    def test_enum_values(self):
        assert QualityFailureReason.MISSING_TICK.value == "missing_tick"
        assert QualityFailureReason.STALE_DATA.value == "stale_data"
        assert QualityFailureReason.OUTLIER_PRICE.value == "outlier_price"
        assert QualityFailureReason.TIMESTAMP_FUTURE.value == "timestamp_future"
        assert QualityFailureReason.SUSPENSION_DETECTED.value == "suspension_detected"
        assert QualityFailureReason.VOLUME_ZERO.value == "volume_zero"

    def test_from_string(self):
        assert QualityFailureReason("stale_data") is QualityFailureReason.STALE_DATA


class TestRecoveryHint:
    def test_enum_values(self):
        assert RecoveryHint.RETRY.value == "RETRY"
        assert RecoveryHint.SKIP_SYMBOL.value == "SKIP_SYMBOL"
        assert RecoveryHint.SWITCH_SOURCE.value == "SWITCH_SOURCE"
        assert RecoveryHint.HALT.value == "HALT"


class TestQualityReport:
    def test_create_passed(self):
        report = QualityReport(
            symbol="AAPL",
            quality_score=0.95,
            passed=True,
        )
        assert report.passed is True
        assert report.failure_reason is None
        assert report.recovery_hint is RecoveryHint.SKIP_SYMBOL

    def test_create_failed(self):
        report = QualityReport(
            symbol="AAPL",
            quality_score=0.3,
            passed=False,
            failure_reason=QualityFailureReason.OUTLIER_PRICE,
            failed_field="close",
            failed_value="99999.00",
            recovery_hint=RecoveryHint.SKIP_SYMBOL,
        )
        assert report.passed is False
        assert report.failure_reason is QualityFailureReason.OUTLIER_PRICE

    def test_frozen(self):
        report = QualityReport(symbol="AAPL", quality_score=0.9, passed=True)
        with pytest.raises(AttributeError):
            report.symbol = "GOOG"

    def test_default_checked_at(self):
        report = QualityReport(symbol="AAPL", quality_score=0.9, passed=True)
        assert isinstance(report.checked_at, datetime)


class TestDataQualityGate:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            DataQualityGate()

    def test_concrete_subclass(self):
        class MockQualityGate(DataQualityGate):
            __gate_id__ = "mock_gate"

            def check(self, symbol, open_price, high, low, close, volume, timestamp, prev_close=None):
                return QualityReport(
                    symbol=symbol,
                    quality_score=1.0,
                    passed=True,
                )

        gate = MockQualityGate()
        report = gate.check(
            symbol="AAPL",
            open_price=Decimal("150"),
            high=Decimal("155"),
            low=Decimal("149"),
            close=Decimal("152"),
            volume=Decimal("1000000"),
            timestamp=datetime(2026, 1, 15, 10, 0, 0),
        )
        assert report.passed is True
        assert report.quality_score == 1.0

    def test_is_within_normal_range(self):
        result = DataQualityGate.is_within_normal_range(Decimal("110"), Decimal("100"))
        assert result is True

    def test_is_within_normal_range_exceeds(self):
        result = DataQualityGate.is_within_normal_range(Decimal("120"), Decimal("100"))
        assert result is False

    def test_is_within_normal_range_zero_prev(self):
        result = DataQualityGate.is_within_normal_range(Decimal("10"), Decimal("0"))
        assert result is False

    def test_is_within_normal_range_custom_limit(self):
        result = DataQualityGate.is_within_normal_range(Decimal("125"), Decimal("100"), limit_pct=Decimal("0.30"))
        assert result is True

    def test_quality_threshold_constant(self):
        assert DataQualityGate.QUALITY_THRESHOLD == 0.7

    def test_check_with_failure(self):
        class StrictGate(DataQualityGate):
            __gate_id__ = "strict_gate"

            def check(self, symbol, open_price, high, low, close, volume, timestamp, prev_close=None):
                return QualityReport(
                    symbol=symbol,
                    quality_score=0.5,
                    passed=False,
                    failure_reason=QualityFailureReason.OUTLIER_PRICE,
                    recovery_hint=RecoveryHint.SKIP_SYMBOL,
                )

        gate = StrictGate()
        report = gate.check(
            symbol="AAPL",
            open_price=Decimal("150"),
            high=Decimal("155"),
            low=Decimal("149"),
            close=Decimal("152"),
            volume=Decimal("1000000"),
            timestamp=datetime(2026, 1, 15, 10, 0, 0),
        )
        assert report.passed is False
        assert report.quality_score < DataQualityGate.QUALITY_THRESHOLD
