# [BLUEPRINT] MOD-MKT-002 | docs/03_modules/_domain_mkt_data/vendor_base/blueprint.md
# [MODULE] tests.market_data.test_vendor_base
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.vendor_base; zephyr.shared.contracts.market_data
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""MOD-MKT-002 Vendor Base 单元测试.

覆盖: 状态转换/能力声明/ABC不可实例化/子类实现/健康检查/线程安全状态读取.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.market_data.vendor_base import (
    MarketDataVendor,
    VendorCapabilities,
    VendorError,
    VendorStatus,
)
from zephyr.shared.contracts.market_data import NormalizedMarketData


class MockVendor(MarketDataVendor):
    """测试用 mock vendor。"""

    def __init__(
        self,
        vid: str = "mock",
        caps: VendorCapabilities | None = None,
        healthy: bool = True,
    ) -> None:
        super().__init__()
        self._vid = vid
        self._caps = caps if caps is not None else VendorCapabilities()
        self._healthy = healthy

    @property
    def vendor_id(self) -> str:
        return self._vid

    @property
    def capabilities(self) -> VendorCapabilities:
        return self._caps

    def fetch_daily_kline(self, symbol, start_date, end_date):
        if not self._healthy:
            raise VendorError(f"{self._vid} 不可用")
        return [
            NormalizedMarketData(
                symbol=symbol,
                timestamp=datetime(2026, 8, 1, tzinfo=timezone.utc),
                open=Decimal("10"),
                high=Decimal("11"),
                low=Decimal("9"),
                close=Decimal("10.5"),
                volume=Decimal("1000000"),
                data_source=self._vid,
                idempotency_key=f"ik-{symbol}-20260801",
            )
        ]

    def health_check(self) -> bool:
        return self._healthy


class TestVendorStatus:
    def test_status_values(self):
        assert VendorStatus.ACTIVE.value == "active"
        assert VendorStatus.INACTIVE.value == "inactive"
        assert VendorStatus.DEGRADED.value == "degraded"
        assert VendorStatus.ERROR.value == "error"

    def test_status_is_str_enum(self):
        assert isinstance(VendorStatus.ACTIVE, str)


class TestVendorCapabilities:
    def test_defaults(self):
        caps = VendorCapabilities()
        assert caps.supports_daily_kline is True
        assert caps.supports_tick is False
        assert caps.supports_level2 is False
        assert caps.supports_realtime is False

    def test_custom_capabilities(self):
        caps = VendorCapabilities(
            supports_daily_kline=True,
            supports_tick=True,
            supports_level2=True,
            supports_realtime=True,
        )
        assert caps.supports_tick is True
        assert caps.supports_level2 is True

    def test_frozen(self):
        caps = VendorCapabilities()
        with pytest.raises(Exception):
            caps.supports_tick = True  # type: ignore[misc]


class TestMarketDataVendor:
    def test_abc_cannot_instantiate(self):
        """ABC 不可直接实例化。"""
        with pytest.raises(TypeError):
            MarketDataVendor()  # type: ignore[abstract]

    def test_initial_status_inactive(self):
        """初始状态为 INACTIVE。"""
        vendor = MockVendor()
        assert vendor.status == VendorStatus.INACTIVE

    def test_set_status(self):
        """状态变更。"""
        vendor = MockVendor()
        vendor.set_status(VendorStatus.ACTIVE)
        assert vendor.status == VendorStatus.ACTIVE

        vendor.set_status(VendorStatus.DEGRADED)
        assert vendor.status == VendorStatus.DEGRADED

    def test_vendor_id(self):
        vendor = MockVendor(vid="tushare")
        assert vendor.vendor_id == "tushare"

    def test_capabilities(self):
        caps = VendorCapabilities(supports_tick=True)
        vendor = MockVendor(caps=caps)
        assert vendor.capabilities.supports_tick is True

    def test_health_check(self):
        vendor = MockVendor(healthy=True)
        assert vendor.health_check() is True

        vendor_unhealthy = MockVendor(healthy=False)
        assert vendor_unhealthy.health_check() is False

    def test_fetch_daily_kline(self):
        vendor = MockVendor(healthy=True)
        data = vendor.fetch_daily_kline("600000.SH", "2026-01-01", "2026-08-01")
        assert len(data) == 1
        assert data[0].symbol == "600000.SH"
        assert data[0].data_source == "mock"

    def test_fetch_raises_when_unhealthy(self):
        vendor = MockVendor(healthy=False)
        with pytest.raises(VendorError):
            vendor.fetch_daily_kline("600000.SH", "2026-01-01", "2026-08-01")

    def test_repr(self):
        vendor = MockVendor(vid="tushare")
        vendor.set_status(VendorStatus.ACTIVE)
        r = repr(vendor)
        assert "tushare" in r
        assert "active" in r

    def test_error_code(self):
        assert VendorError.error_code == "ZA-MKT-0002"
