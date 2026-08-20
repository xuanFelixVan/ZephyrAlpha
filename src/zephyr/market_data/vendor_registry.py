# [BLUEPRINT] MOD-MKT-001 | docs/03_modules/_domain_mkt_data/vendor_registry/blueprint.md
# [MODULE] zephyr.market_data.vendor_registry
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.vendor_base; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.market_data.autoload; zephyr.market_data.connectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] _vendors为dict[str,MarketDataVendor]; 读写加threading.Lock; default_vendor_id为str|None; vendor_id唯一
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VendorAlreadyRegisteredError(ZA-MKT-0001); VendorNotFoundError(ZA-MKT-0007)
# [TESTS] tests/market_data/test_vendor_registry.py
# [A_module] module_id=MOD-MKT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_MKT_DATA — Vendor Registry (行情数据源注册表)

管理所有已注册的 MarketDataVendor 实例。提供注册/注销/查询/默认源管理功能,
供 autoload(MOD-MKT-005)自动加载和 connectors(MOD-MKT-003)适配查找。

属 A 类基础设施(注册表模式), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-001
蓝图: docs/03_modules/_domain_mkt_data/vendor_registry/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: MarketDataVendor 实例
#   fields: 待注册的数据源对象（实现 vendor_id/capabilities/fetch_daily_kline/health_check）
#   code: register() L79
# - id: I2
#   name: 查询/管理条件
#   fields: vendor_id 字符串 / VendorStatus 状态过滤 / 默认源 ID
#   code: get() L125 / list_vendors() L134 / set_default() L151
# 层: 算法
# - id: A1
#   name_zh: ① 注册与注销
#   name_en: VendorRegistry.register/unregister
#   intro: 把数据源实例登记进注册表或摘除，保证 vendor_id 唯一
#   desc: Lock 保护；重复注册 raise VendorAlreadyRegisteredError(ZA-MKT-0001)；注销不存在 raise VendorNotFoundError；注销默认源时自动清空 default
#   inputs: I1
#   outputs: _vendors 注册表
#   invariant: vendor_id 唯一；读写加 Lock
# - id: A2
#   name_zh: ② 查询与状态过滤
#   name_en: VendorRegistry.get/list_vendors
#   intro: O(1) 按 ID 查数据源，或按状态过滤列出全部
#   desc: dict.get 按 vendor_id 查找（无则 None）；list_vendors 返回副本，可按 VendorStatus 过滤
#   inputs: I2 A1
#   outputs: vendor 实例或列表
# - id: A3
#   name_zh: ③ 默认数据源管理
#   name_en: VendorRegistry.set_default/get_default
#   intro: 指定并读取默认行情数据源
#   desc: set_default 校验已注册否则 raise VendorNotFoundError；get_default 未设置或已注销返回 None
#   inputs: I2 A1
#   outputs: 默认 vendor 实例
# 层: 输出
# - id: O1
#   name_zh: 注册表查询结果与默认源
#   name_en: VendorRegistry 查询返回
#   intro: 供自动加载与连接器层查找可用数据源及默认源
#   invariant: default_vendor_id 指向已注册 vendor 或 None
#   downstream: autoload MOD-MKT-005；connectors MOD-MKT-003（#[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A2
# I2 --> A3
# A1 --> A3
# A2 --> O1
# A3 --> O1
"""

from __future__ import annotations

import logging
from threading import Lock

from zephyr.market_data.vendor_base import MarketDataVendor, VendorStatus
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class VendorAlreadyRegisteredError(ZephyrBaseError):
    """Vendor 重复注册——vendor_id 已存在。"""

    error_code = "ZA-MKT-0001"


class VendorNotFoundError(ZephyrBaseError):
    """Vendor 不存在——查询/注销/设默认时 vendor_id 未注册。"""

    error_code = "ZA-MKT-0007"


class VendorRegistry:
    """行情数据源注册表——管理 vendor 实例的注册/查询/默认源。

    注册表模式: 集中管理所有已注册的 MarketDataVendor, 提供 O(1) 查找。
    线程安全: 读写操作加 threading.Lock 保护。

    Usage:
        registry = VendorRegistry()

        vendor = TushareVendor()
        vendor.set_status(VendorStatus.ACTIVE)
        registry.register(vendor)
        registry.set_default("tushare")

        # 查询
        v = registry.get("tushare")
        default = registry.get_default()
        active_vendors = registry.list_vendors(status=VendorStatus.ACTIVE)

        # 注销
        registry.unregister("tushare")
    """

    def __init__(self) -> None:
        self._vendors: dict[str, MarketDataVendor] = {}
        self._default_vendor_id: str | None = None
        self._lock = Lock()

    def register(self, vendor: MarketDataVendor) -> None:
        """注册一个 vendor。

        Args:
            vendor: 要注册的 MarketDataVendor 实例

        Raises:
            VendorAlreadyRegisteredError: vendor_id 已存在
        """
        vid = vendor.vendor_id
        with self._lock:
            if vid in self._vendors:
                raise VendorAlreadyRegisteredError(
                    f"vendor_id={vid!r} 已注册",
                    details={"vendor_id": vid},
                )
            self._vendors[vid] = vendor
        _logger.info("vendor 注册成功: %s (共 %d 个)", vid, self.count)

    def unregister(self, vendor_id: str) -> MarketDataVendor:
        """注销一个 vendor。

        Args:
            vendor_id: 要注销的 vendor ID

        Returns:
            被注销的 MarketDataVendor 实例

        Raises:
            VendorNotFoundError: vendor_id 不存在
        """
        with self._lock:
            if vendor_id not in self._vendors:
                raise VendorNotFoundError(
                    f"vendor_id={vendor_id!r} 未注册",
                    details={"vendor_id": vendor_id},
                )
            vendor = self._vendors.pop(vendor_id)
            if self._default_vendor_id == vendor_id:
                self._default_vendor_id = None
                _logger.info("默认 vendor %s 已注销, 默认源清空", vendor_id)
        _logger.info("vendor 注销成功: %s (剩余 %d 个)", vendor_id, self.count)
        return vendor

    def get(self, vendor_id: str) -> MarketDataVendor | None:
        """按 ID 查询 vendor。

        Returns:
            MarketDataVendor 实例, 不存在返回 None
        """
        with self._lock:
            return self._vendors.get(vendor_id)

    def list_vendors(self, status: VendorStatus | None = None) -> list[MarketDataVendor]:
        """列出所有/按状态过滤的 vendor。

        Args:
            status: 可选状态过滤, None=全部

        Returns:
            vendor 列表(副本, 不反映后续变更)
        """
        with self._lock:
            vendors = list(self._vendors.values())
        if status is not None:
            vendors = [v for v in vendors if v.status == status]
        return vendors

    def set_default(self, vendor_id: str) -> None:
        """设置默认数据源。

        Args:
            vendor_id: 要设为默认的 vendor ID

        Raises:
            VendorNotFoundError: vendor_id 未注册
        """
        with self._lock:
            if vendor_id not in self._vendors:
                raise VendorNotFoundError(
                    f"无法设默认: vendor_id={vendor_id!r} 未注册",
                    details={"vendor_id": vendor_id},
                )
            self._default_vendor_id = vendor_id
        _logger.info("默认 vendor 设置: %s", vendor_id)

    def get_default(self) -> MarketDataVendor | None:
        """获取默认数据源。

        Returns:
            默认 MarketDataVendor, 未设置或已注销返回 None
        """
        with self._lock:
            if self._default_vendor_id is None:
                return None
            return self._vendors.get(self._default_vendor_id)

    @property
    def default_vendor_id(self) -> str | None:
        """默认 vendor ID(只读)。"""
        with self._lock:
            return self._default_vendor_id

    @property
    def count(self) -> int:
        """已注册 vendor 数量。"""
        with self._lock:
            return len(self._vendors)

    def __repr__(self) -> str:
        with self._lock:
            return f"VendorRegistry(count={len(self._vendors)}, default={self._default_vendor_id!r})"


__all__ = [
    "VendorAlreadyRegisteredError",
    "VendorNotFoundError",
    "VendorRegistry",
]
