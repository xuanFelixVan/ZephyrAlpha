# [BLUEPRINT] MOD-MKT-001 | docs/03_modules/_domain_mkt_data/vendor_registry/blueprint.md
# [MODULE] tests.market_data.test_vendor_registry
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.vendor_registry; zephyr.market_data.vendor_base
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
"""MOD-MKT-001 Vendor Registry 单元测试.

覆盖: 注册/注销/查询/默认源/重复注册报错/不存在报错/状态过滤/计数/repr.
"""

from __future__ import annotations

import pytest

from zephyr.market_data.vendor_base import (
    MarketDataVendor,
    VendorCapabilities,
    VendorStatus,
)
from zephyr.market_data.vendor_registry import (
    VendorAlreadyRegisteredError,
    VendorNotFoundError,
    VendorRegistry,
)


class MockVendor(MarketDataVendor):
    """测试用 mock vendor。"""

    def __init__(self, vid: str, caps: VendorCapabilities | None = None) -> None:
        super().__init__()
        self._vid = vid
        self._caps = caps if caps is not None else VendorCapabilities()

    @property
    def vendor_id(self) -> str:
        return self._vid

    @property
    def capabilities(self) -> VendorCapabilities:
        return self._caps

    def fetch_daily_kline(self, symbol, start_date, end_date):
        return []

    def health_check(self) -> bool:
        return True


class TestRegister:
    def test_register_single(self):
        registry = VendorRegistry()
        v = MockVendor("tushare")
        registry.register(v)
        assert registry.count == 1

    def test_register_multiple(self):
        registry = VendorRegistry()
        registry.register(MockVendor("tushare"))
        registry.register(MockVendor("akshare"))
        registry.register(MockVendor("wind"))
        assert registry.count == 3

    def test_duplicate_raises(self):
        registry = VendorRegistry()
        registry.register(MockVendor("tushare"))
        with pytest.raises(VendorAlreadyRegisteredError):
            registry.register(MockVendor("tushare"))

    def test_error_code(self):
        assert VendorAlreadyRegisteredError.error_code == "ZA-MKT-0001"


class TestUnregister:
    def test_unregister_existing(self):
        registry = VendorRegistry()
        v = MockVendor("tushare")
        registry.register(v)
        removed = registry.unregister("tushare")
        assert removed is v
        assert registry.count == 0

    def test_unregister_nonexistent_raises(self):
        registry = VendorRegistry()
        with pytest.raises(VendorNotFoundError):
            registry.unregister("nonexistent")

    def test_unregister_default_clears_default(self):
        registry = VendorRegistry()
        registry.register(MockVendor("tushare"))
        registry.set_default("tushare")
        assert registry.default_vendor_id == "tushare"

        registry.unregister("tushare")
        assert registry.default_vendor_id is None
        assert registry.get_default() is None


class TestGet:
    def test_get_existing(self):
        registry = VendorRegistry()
        v = MockVendor("tushare")
        registry.register(v)
        assert registry.get("tushare") is v

    def test_get_nonexistent_returns_none(self):
        registry = VendorRegistry()
        assert registry.get("nonexistent") is None


class TestListVendors:
    def test_list_all(self):
        registry = VendorRegistry()
        registry.register(MockVendor("tushare"))
        registry.register(MockVendor("akshare"))
        vendors = registry.list_vendors()
        assert len(vendors) == 2

    def test_list_empty(self):
        registry = VendorRegistry()
        assert registry.list_vendors() == []

    def test_list_by_status(self):
        registry = VendorRegistry()
        v1 = MockVendor("tushare")
        v1.set_status(VendorStatus.ACTIVE)
        v2 = MockVendor("akshare")
        v2.set_status(VendorStatus.DEGRADED)
        v3 = MockVendor("wind")
        v3.set_status(VendorStatus.ACTIVE)
        registry.register(v1)
        registry.register(v2)
        registry.register(v3)

        active = registry.list_vendors(status=VendorStatus.ACTIVE)
        assert len(active) == 2
        degraded = registry.list_vendors(status=VendorStatus.DEGRADED)
        assert len(degraded) == 1

    def test_list_returns_copy(self):
        """list_vendors 返回副本, 不反映后续变更。"""
        registry = VendorRegistry()
        registry.register(MockVendor("tushare"))
        vendors = registry.list_vendors()
        registry.register(MockVendor("akshare"))
        assert len(vendors) == 1  # 副本不变
        assert registry.count == 2


class TestDefaultVendor:
    def test_set_and_get_default(self):
        registry = VendorRegistry()
        v = MockVendor("tushare")
        registry.register(v)
        registry.set_default("tushare")
        assert registry.default_vendor_id == "tushare"
        assert registry.get_default() is v

    def test_set_default_nonexistent_raises(self):
        registry = VendorRegistry()
        with pytest.raises(VendorNotFoundError):
            registry.set_default("nonexistent")

    def test_get_default_when_unset(self):
        registry = VendorRegistry()
        assert registry.get_default() is None
        assert registry.default_vendor_id is None

    def test_get_default_after_unregister(self):
        registry = VendorRegistry()
        registry.register(MockVendor("tushare"))
        registry.set_default("tushare")
        registry.unregister("tushare")
        assert registry.get_default() is None

    def test_change_default(self):
        registry = VendorRegistry()
        registry.register(MockVendor("tushare"))
        registry.register(MockVendor("akshare"))
        registry.set_default("tushare")
        registry.set_default("akshare")
        assert registry.default_vendor_id == "akshare"


class TestCount:
    def test_empty_count(self):
        assert VendorRegistry().count == 0

    def test_count_after_ops(self):
        registry = VendorRegistry()
        registry.register(MockVendor("a"))
        registry.register(MockVendor("b"))
        assert registry.count == 2
        registry.unregister("a")
        assert registry.count == 1


class TestRepr:
    def test_repr_format(self):
        registry = VendorRegistry()
        registry.register(MockVendor("tushare"))
        registry.set_default("tushare")
        r = repr(registry)
        assert "count=1" in r
        assert "tushare" in r
