"""L00 provider_base — DataSourceBase 最小可实例化桩与注册。"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from zephyr.l00_data_source.provider_base import DataSourceBase, DataSourceMeta


_META = DataSourceMeta(
    provider_id="unit-stub-provider",
    provider_name="Unit Stub",
    asset_classes=["equity"],
    markets=["CN"],
)


class _UnitStubProvider(DataSourceBase):
    __meta__ = _META

    def fetch_historical(
        self, symbol: str, start: datetime, end: datetime, interval: str = "1d"
    ) -> pd.DataFrame:
        _ = symbol, start, end, interval
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

    def subscribe_realtime(self, symbols: list[str]) -> None:
        _ = symbols


def test_stub_provider_registers_in_registry() -> None:
    assert DataSourceBase._registry.get("unit-stub-provider") is _UnitStubProvider


def test_stub_validate_schema_empty_frame_columns_only_ok() -> None:
    """列齐全但无行时仍视为通过 schema 检查（常见空查询结果）。"""
    p = _UnitStubProvider()
    df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    assert p.validate_schema(df)


def test_stub_validate_schema_missing_column_fails() -> None:
    p = _UnitStubProvider()
    df = pd.DataFrame([{"open": 1.0}])
    assert not p.validate_schema(df)


def test_stub_validate_schema_full_row_ok() -> None:
    p = _UnitStubProvider()
    df = pd.DataFrame(
        [{"open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100.0}]
    )
    assert p.validate_schema(df)
