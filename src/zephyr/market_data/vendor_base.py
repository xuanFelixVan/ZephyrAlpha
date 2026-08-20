# [BLUEPRINT] MOD-MKT-002 | docs/03_modules/_domain_mkt_data/vendor_base/blueprint.md
# [MODULE] zephyr.market_data.vendor_base
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.shared.contracts.market_data; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.market_data.vendor_registry; zephyr.market_data.connectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] VendorStatus/VendorCapabilities frozen不可变; MarketDataVendor为ABC不可直接实例化; status变更通过set_status; 纯抽象层不含具体数据源实现
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VendorError(ZA-MKT-0002)
# [TESTS] tests/market_data/test_vendor_base.py
# [A_module] module_id=MOD-MKT-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_MKT_DATA — Vendor Base (行情数据源基类)

定义所有行情数据 vendor 的统一抽象接口。提供状态管理(ACTIVE/INACTIVE/
DEGRADED/ERROR)、能力声明(支持K线/Tick/Level2/实时)和健康检查接口,
供 VendorRegistry 注册管理和 Connectors 适配。

属 A 类基础设施(抽象接口定义), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-002
蓝图: docs/03_modules/_domain_mkt_data/vendor_base/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Vendor 子类实现参数
#   fields: vendor_id/capabilities/fetch_daily_kline/health_check 由子类实现
#   code: MarketDataVendor ABC L74
# - id: I2
#   name: 目标运行状态
#   fields: VendorStatus 4 级枚举（ACTIVE/INACTIVE/DEGRADED/ERROR）
#   code: VendorStatus L51 / set_status L124
# 层: 算法
# - id: A1
#   name_zh: ① Vendor 状态机管理
#   name_en: MarketDataVendor.set_status
#   intro: 线程安全地切换数据源运行状态并记录变更日志
#   desc: Lock 保护读写 _status；初始 INACTIVE；状态变化时 logger.info 记录 old→new
#   inputs: I2
#   outputs: 当前 VendorStatus
#   invariant: 状态变更加 Lock 线程安全
# - id: A2
#   name_zh: ② 能力声明契约
#   name_en: VendorCapabilities
#   intro: 不可变声明该数据源支持日K/Tick/Level2/实时哪几类数据
#   desc: frozen dataclass 4 项布尔能力位；供 Registry 与 Connectors 选源时参考
#   inputs: I1
#   outputs: VendorCapabilities 实例
#   invariant: frozen 不可变
# - id: A3
#   name_zh: ③ 抽象接口契约定义
#   name_en: MarketDataVendor.fetch_daily_kline/health_check
#   intro: 规定所有行情数据源必须实现的取数与健康检查接口
#   desc: ABC 抽象方法：fetch_daily_kline 返回按时间升序的 NormalizedMarketData 列表（失败 raise VendorError ZA-MKT-0002）；health_check 返回 bool
#   inputs: I1
#   outputs: 统一接口签名
#   invariant: ABC 不可直接实例化
# 层: 输出
# - id: O1
#   name_zh: 统一 Vendor 抽象接口
#   name_en: MarketDataVendor
#   intro: 所有行情数据源（tushare/akshare/wind 等）的统一基类与状态/能力契约
#   downstream: vendor_registry MOD-MKT-001；connectors MOD-MKT-003（#[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I1 --> A2
# I1 --> A3
# A1 --> O1
# A2 --> O1
# A3 --> O1
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from threading import Lock

from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class VendorError(ZephyrBaseError):
    """Vendor 操作异常——健康检查失败/数据获取失败等。"""

    error_code = "ZA-MKT-0002"


class VendorStatus(str, Enum):
    """Vendor 运行状态——4级。"""

    ACTIVE = "active"  # 正常运行
    INACTIVE = "inactive"  # 未激活/已停用
    DEGRADED = "degraded"  # 降级运行(延迟/部分不可用)
    ERROR = "error"  # 错误状态(不可用)


@dataclass(frozen=True)
class VendorCapabilities:
    """Vendor 能力声明——不可变。

    声明该 vendor 支持的数据类型和功能, 供 Registry 和 Connectors
    在选择数据源时参考。
    """

    supports_daily_kline: bool = True  # 支持日K数据
    supports_tick: bool = False  # 支持Tick数据
    supports_level2: bool = False  # 支持Level2行情
    supports_realtime: bool = False  # 支持实时推送


class MarketDataVendor(ABC):
    """行情数据源抽象基类——所有 vendor 实现的统一接口。

    子类(tushare/akshare/wind 等)需实现:
      - vendor_id (property): vendor 唯一标识
      - capabilities (property): 能力声明
      - fetch_daily_kline(): 获取日K数据
      - health_check(): 健康检查

    状态管理:
      - 初始状态为 INACTIVE
      - set_status() 切换状态(ACTIVE/INACTIVE/DEGRADED/ERROR)
      - status 变更加 Lock 保护, 线程安全

    Usage:
        class TushareVendor(MarketDataVendor):
            @property
            def vendor_id(self): return "tushare"
            @property
            def capabilities(self): return VendorCapabilities(supports_daily_kline=True)
            def fetch_daily_kline(self, symbol, start, end): ...
            def health_check(self): return True

        vendor = TushareVendor()
        vendor.set_status(VendorStatus.ACTIVE)
        data = vendor.fetch_daily_kline("600000.SH", "2026-01-01", "2026-08-01")
    """

    def __init__(self) -> None:
        self._status: VendorStatus = VendorStatus.INACTIVE
        self._status_lock = Lock()

    @property
    @abstractmethod
    def vendor_id(self) -> str:
        """Vendor 唯一标识(如 'tushare', 'akshare')。"""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> VendorCapabilities:
        """Vendor 能力声明。"""
        ...

    @property
    def status(self) -> VendorStatus:
        """当前运行状态(线程安全读取)。"""
        with self._status_lock:
            return self._status

    def set_status(self, status: VendorStatus) -> None:
        """设置运行状态(线程安全)。

        Args:
            status: 目标状态(ACTIVE/INACTIVE/DEGRADED/ERROR)
        """
        with self._status_lock:
            old = self._status
            self._status = status
        if old != status:
            _logger.info(
                "vendor %s 状态变更: %s -> %s",
                self.vendor_id,
                old.value,
                status.value,
            )

    @abstractmethod
    def fetch_daily_kline(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> list[NormalizedMarketData]:
        """获取日K线数据(抽象方法)。

        Args:
            symbol: 标的代码(标准化格式, 如 "600000.SH")
            start_date: 开始日期(YYYY-MM-DD)
            end_date: 结束日期(YYYY-MM-DD)

        Returns:
            list[NormalizedMarketData]: 日K数据列表(按时间升序)

        Raises:
            VendorError: 数据获取失败
        """
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """健康检查(抽象方法)。

        Returns:
            True=健康, False=不可用
        """
        ...

    def __repr__(self) -> str:
        return f"{type(self).__name__}(vendor_id={self.vendor_id!r}, status={self.status.value})"


__all__ = [
    "MarketDataVendor",
    "VendorCapabilities",
    "VendorError",
    "VendorStatus",
]
