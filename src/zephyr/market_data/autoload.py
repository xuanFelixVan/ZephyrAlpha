# [BLUEPRINT] MOD-MKT-005 | docs/03_modules/_domain_mkt_data/autoload/blueprint.md
# [MODULE] zephyr.market_data.autoload
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.vendor_registry; zephyr.market_data.vendor_base; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.market_data
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] VendorConfig/AutoloadResult frozen不可变; load()不抛异常(单个失败记录到errors); vendor_factory为Callable[[VendorConfig],MarketDataVendor]; 纯加载层不含具体vendor实现
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AutoloadError(ZA-MKT-0005)
# [TESTS] tests/market_data/test_autoload.py
# [TTL] permanent
"""D_MKT_DATA — Autoload (自动加载器)

从配置列表自动创建 MarketDataVendor 实例并注册到 VendorRegistry。
通过 vendor_factory 回调解调解具体 vendor 创建逻辑, 与具体数据源实现解耦。

属 A 类基础设施(配置驱动加载), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-005
蓝图: docs/03_modules/_domain_mkt_data/autoload/blueprint.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from zephyr.market_data.vendor_base import MarketDataVendor, VendorStatus
from zephyr.market_data.vendor_registry import (
    VendorAlreadyRegisteredError,
    VendorRegistry,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class AutoloadError(ZephyrBaseError):
    """自动加载配置非法——空 vendor_id / 空 vendor_type 等。"""

    error_code = "ZA-MKT-0005"


@dataclass(frozen=True)
class VendorConfig:
    """Vendor 配置——单个数据源的加载配置, 不可变。

    Attributes:
        vendor_id: vendor 唯一标识(如 'tushare')
        vendor_type: vendor 类型(传给 factory 创建对应实现)
        is_default: 是否设为默认数据源
        params: vendor 特定参数(API key/timeout/等)
    """

    vendor_id: str
    vendor_type: str
    is_default: bool = False
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AutoloadResult:
    """自动加载结果——不可变。

    Attributes:
        registered_count: 成功注册的 vendor 数
        default_vendor_id: 设置的默认 vendor ID(未设则为 None)
        errors: 失败的 vendor_id 列表
    """

    registered_count: int
    default_vendor_id: str | None
    errors: tuple[str, ...]


# vendor_factory 类型: 接收 VendorConfig, 返回 MarketDataVendor
VendorFactory = Callable[[VendorConfig], MarketDataVendor]


class MarketDataAutoloader:
    """自动加载器——从配置批量创建+注册 vendor。

    通过 vendor_factory 回调创建具体 vendor 实例, 与 autoload 本身解耦。
    容错: 单个 vendor 创建/注册失败不阻断整体加载, 记录到 errors。

    Usage:
        registry = VendorRegistry()

        def factory(cfg: VendorConfig) -> MarketDataVendor:
            if cfg.vendor_type == "tushare":
                return TushareVendor(**cfg.params)
            raise ValueError(f"未知 vendor_type: {cfg.vendor_type}")

        loader = MarketDataAutoloader(registry, factory)
        result = loader.load([
            VendorConfig("tushare", "tushare", is_default=True, params={"token": "xxx"}),
            VendorConfig("akshare", "akshare"),
        ])

        # result.registered_count == 2
        # result.default_vendor_id == "tushare"
    """

    def __init__(
        self,
        registry: VendorRegistry,
        vendor_factory: VendorFactory,
    ) -> None:
        self._registry = registry
        self._factory = vendor_factory

    def load(self, configs: list[VendorConfig]) -> AutoloadResult:
        """批量加载 vendor: 逐个创建+注册+设默认。

        - 逐个 config 调用 factory 创建 vendor
        - 创建后 set_status(ACTIVE) + register
        - is_default=True 的设为默认源(最后一个生效)
        - 单个失败(创建异常/重复注册)记录到 errors, 不阻断
        - 空 configs 返回 registered_count=0

        Returns:
            AutoloadResult: 含成功数/默认ID/失败列表
        """
        if not configs:
            return AutoloadResult(
                registered_count=0,
                default_vendor_id=None,
                errors=(),
            )

        # 校验配置
        for cfg in configs:
            if not cfg.vendor_id:
                raise AutoloadError(
                    "vendor_id 不能为空",
                    details={"config": str(cfg)},
                )
            if not cfg.vendor_type:
                raise AutoloadError(
                    f"vendor_type 不能为空 (vendor_id={cfg.vendor_id})",
                    details={"vendor_id": cfg.vendor_id},
                )

        registered = 0
        errors: list[str] = []
        default_id: str | None = None

        for cfg in configs:
            try:
                # 1. factory 创建 vendor
                vendor = self._factory(cfg)

                # 2. 激活
                vendor.set_status(VendorStatus.ACTIVE)

                # 3. 注册
                self._registry.register(vendor)
                registered += 1
                _logger.info(
                    "vendor 自动加载成功: %s (type=%s)",
                    cfg.vendor_id,
                    cfg.vendor_type,
                )

                # 4. 设默认
                if cfg.is_default:
                    self._registry.set_default(cfg.vendor_id)
                    default_id = cfg.vendor_id

            except VendorAlreadyRegisteredError:
                _logger.warning(
                    "vendor 自动加载跳过(已注册): %s", cfg.vendor_id
                )
                errors.append(cfg.vendor_id)
            except Exception:
                _logger.exception(
                    "vendor 自动加载失败: %s", cfg.vendor_id
                )
                errors.append(cfg.vendor_id)

        result = AutoloadResult(
            registered_count=registered,
            default_vendor_id=default_id,
            errors=tuple(errors),
        )

        _logger.info(
            "自动加载完成: registered=%d default=%s errors=%d",
            registered,
            default_id,
            len(errors),
        )
        return result


__all__ = [
    "AutoloadError",
    "AutoloadResult",
    "MarketDataAutoloader",
    "VendorConfig",
    "VendorFactory",
]
