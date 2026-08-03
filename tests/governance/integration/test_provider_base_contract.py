# [A_test] module_id: MOD-GOV_provider_base_contract | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-673 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_provider_base_contract
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-673 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from __future__ import annotations

"""L00 provider_base — QuoteProviderBase 最小可实例化桩与注册。"""


from datetime import datetime

import pandas as pd

from zephyr.governance.intelligence_governance.provider_base import QuoteProviderBase, QuoteProviderMeta

_META = QuoteProviderMeta(
    provider_id="unit-stub-provider",
    provider_name="Unit Stub",
    asset_classes=["equity"],
    markets=["CN"],
)


class _UnitStubProvider(QuoteProviderBase):
    __meta__ = _META

    def fetch_historical(self, symbol: str, start: datetime, end: datetime, interval: str = "1d") -> pd.DataFrame:
        _ = symbol, start, end, interval
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

    def subscribe_realtime(self, symbols: list[str]) -> None:
        _ = symbols


def test_stub_provider_registers_in_registry() -> None:
    assert QuoteProviderBase.registry.get("unit-stub-provider") is _UnitStubProvider


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
    df = pd.DataFrame([{"open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100.0}])
    assert p.validate_schema(df)
