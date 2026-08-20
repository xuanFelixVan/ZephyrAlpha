# [BLUEPRINT] MOD-MKT-005 | docs/03_modules/_domain_mkt_data/autoload/blueprint.md
# [MODULE] tests.market_data.test_autoload
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.autoload; zephyr.market_data.vendor_base; zephyr.market_data.vendor_registry
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-MKT-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-MKT-005 Autoload 单元测试.

覆盖: 正常加载/默认源设置/容错(单个失败不阻断)/空配置/
重复vendor跳过/结果统计/输入校验/不可变性.
"""

from __future__ import annotations

import pytest

from zephyr.market_data.autoload import (
    AutoloadError,
    AutoloadResult,
    MarketDataAutoloader,
    VendorConfig,
)
from zephyr.market_data.vendor_base import (
    MarketDataVendor,
    VendorCapabilities,
    VendorStatus,
)
from zephyr.market_data.vendor_registry import VendorRegistry


class MockVendor(MarketDataVendor):
    def __init__(self, vid, **kwargs):
        super().__init__()
        self._vid = vid

    @property
    def vendor_id(self):
        return self._vid

    @property
    def capabilities(self):
        return VendorCapabilities()

    def fetch_daily_kline(self, symbol, start_date, end_date):
        return []

    def health_check(self):
        return True


def make_factory(healthy_types: set[str] | None = None):
    """创建 factory, healthy_types 中的类型正常创建, 其余抛异常。"""
    if healthy_types is None:
        healthy_types = {"tushare", "akshare", "wind"}

    def factory(cfg: VendorConfig) -> MarketDataVendor:
        if cfg.vendor_type not in healthy_types:
            raise ValueError(f"未知 vendor_type: {cfg.vendor_type}")
        return MockVendor(cfg.vendor_id, **cfg.params)

    return factory


class TestVendorConfig:
    def test_defaults(self):
        cfg = VendorConfig("tushare", "tushare")
        assert cfg.vendor_id == "tushare"
        assert cfg.vendor_type == "tushare"
        assert cfg.is_default is False
        assert cfg.params == {}

    def test_with_params(self):
        cfg = VendorConfig("tushare", "tushare", is_default=True, params={"token": "xxx"})
        assert cfg.is_default is True
        assert cfg.params["token"] == "xxx"

    def test_frozen(self):
        cfg = VendorConfig("tushare", "tushare")
        with pytest.raises(Exception):
            cfg.vendor_id = "x"  # type: ignore[misc]


class TestLoad:
    def test_single_vendor(self):
        registry = VendorRegistry()
        loader = MarketDataAutoloader(registry, make_factory())
        result = loader.load([VendorConfig("tushare", "tushare")])

        assert result.registered_count == 1
        assert result.default_vendor_id is None
        assert len(result.errors) == 0
        assert registry.count == 1
        assert registry.get("tushare") is not None
        assert registry.get("tushare").status == VendorStatus.ACTIVE

    def test_multiple_vendors(self):
        registry = VendorRegistry()
        loader = MarketDataAutoloader(registry, make_factory())
        result = loader.load(
            [
                VendorConfig("tushare", "tushare"),
                VendorConfig("akshare", "akshare"),
                VendorConfig("wind", "wind"),
            ]
        )

        assert result.registered_count == 3
        assert len(result.errors) == 0
        assert registry.count == 3

    def test_default_vendor_set(self):
        registry = VendorRegistry()
        loader = MarketDataAutoloader(registry, make_factory())
        result = loader.load(
            [
                VendorConfig("tushare", "tushare", is_default=True),
                VendorConfig("akshare", "akshare"),
            ]
        )

        assert result.default_vendor_id == "tushare"
        assert registry.default_vendor_id == "tushare"
        assert registry.get_default() is not None

    def test_last_default_wins(self):
        registry = VendorRegistry()
        loader = MarketDataAutoloader(registry, make_factory())
        result = loader.load(
            [
                VendorConfig("tushare", "tushare", is_default=True),
                VendorConfig("akshare", "akshare", is_default=True),
            ]
        )

        assert result.default_vendor_id == "akshare"
        assert registry.default_vendor_id == "akshare"

    def test_empty_configs(self):
        registry = VendorRegistry()
        loader = MarketDataAutoloader(registry, make_factory())
        result = loader.load([])

        assert result.registered_count == 0
        assert result.default_vendor_id is None
        assert len(result.errors) == 0


class TestFaultTolerance:
    def test_failed_vendor_does_not_block(self):
        """单个 vendor 创建失败不阻断整体加载。"""
        registry = VendorRegistry()
        # factory 仅支持 tushare, akshare 未知
        loader = MarketDataAutoloader(registry, make_factory({"tushare"}))
        result = loader.load(
            [
                VendorConfig("tushare", "tushare"),
                VendorConfig("akshare", "akshare"),  # 会失败
            ]
        )

        assert result.registered_count == 1
        assert "akshare" in result.errors
        assert registry.count == 1
        assert registry.get("tushare") is not None

    def test_duplicate_vendor_skipped(self):
        """重复注册的 vendor 跳过并记录到 errors。"""
        registry = VendorRegistry()
        # 预先注册一个
        existing = MockVendor("tushare")
        registry.register(existing)

        loader = MarketDataAutoloader(registry, make_factory())
        result = loader.load(
            [
                VendorConfig("tushare", "tushare"),  # 已存在, 跳过
                VendorConfig("akshare", "akshare"),  # 正常
            ]
        )

        assert result.registered_count == 1
        assert "tushare" in result.errors
        assert registry.count == 2

    def test_all_fail(self):
        """全部失败——registered_count=0, errors含全部。"""
        registry = VendorRegistry()
        loader = MarketDataAutoloader(registry, make_factory(set()))  # 无支持的type
        result = loader.load(
            [
                VendorConfig("tushare", "tushare"),
                VendorConfig("akshare", "akshare"),
            ]
        )

        assert result.registered_count == 0
        assert len(result.errors) == 2
        assert "tushare" in result.errors
        assert "akshare" in result.errors

    def test_default_failed_not_set(self):
        """设为默认的 vendor 创建失败——默认源不设。"""
        registry = VendorRegistry()
        loader = MarketDataAutoloader(registry, make_factory({"akshare"}))
        result = loader.load(
            [
                VendorConfig("tushare", "tushare", is_default=True),  # 会失败
                VendorConfig("akshare", "akshare"),
            ]
        )

        assert result.registered_count == 1
        assert result.default_vendor_id is None  # tushare 失败, 默认未设
        assert registry.get_default() is None


class TestInputValidation:
    def test_empty_vendor_id_raises(self):
        registry = VendorRegistry()
        loader = MarketDataAutoloader(registry, make_factory())
        with pytest.raises(AutoloadError):
            loader.load([VendorConfig("", "tushare")])

    def test_empty_vendor_type_raises(self):
        registry = VendorRegistry()
        loader = MarketDataAutoloader(registry, make_factory())
        with pytest.raises(AutoloadError):
            loader.load([VendorConfig("tushare", "")])

    def test_error_code(self):
        assert AutoloadError.error_code == "ZA-MKT-0005"


class TestImmutability:
    def test_autoload_result_frozen(self):
        result = AutoloadResult(
            registered_count=1,
            default_vendor_id="tushare",
            errors=(),
        )
        with pytest.raises(Exception):
            result.registered_count = 99  # type: ignore[misc]
