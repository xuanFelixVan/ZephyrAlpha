# [BLUEPRINT] MOD-MKT-003 | docs/03_modules/_domain_mkt_data/connectors/blueprint.md
# [MODULE] zephyr.market_data.connectors.manager
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.connectors.base; zephyr.shared.foundation.errors
# [CONSUMERS] D_EX_SOR
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] _connectors为dict[str,MarketDataConnector]; 读写加Lock; connector_id唯一
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ConnectorAlreadyRegisteredError(ZA-MKT-0008); ConnectorNotFoundError(ZA-MKT-0009)
# [TESTS] tests/market_data/connectors/test_connector_manager.py
# [A_module] module_id=MOD-MKT-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_MKT_DATA — Connector Manager (连接器管理器)

统一管理多个 MarketDataConnector 的生命周期: 批量连接/断开/健康检查。
线程安全, 容错(单个失败不阻断整体操作)。

属 A 类基础设施(管理器模式), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-003
蓝图: docs/03_modules/_domain_mkt_data/connectors/blueprint.md
"""

from __future__ import annotations

import logging
from threading import Lock

from zephyr.market_data.connectors.base import (
    ConnectionState,
    MarketDataConnector,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class ConnectorAlreadyRegisteredError(ZephyrBaseError):
    """连接器重复注册——connector_id 已存在。"""

    error_code = "ZA-MKT-0008"


class ConnectorNotFoundError(ZephyrBaseError):
    """连接器不存在——查询/注销时 connector_id 未注册。"""

    error_code = "ZA-MKT-0009"


class ConnectorManager:
    """连接器管理器——批量管理连接器生命周期。

    线程安全: 读写操作加 Lock 保护。
    容错: 单个连接器操作失败不阻断整体, 结果记录到返回值。

    Usage:
        mgr = ConnectorManager()
        mgr.register(conn1)
        mgr.register(conn2)

        results = mgr.connect_all()  # {"tushare": True, "akshare": False}
        health = mgr.health_check_all()
        mgr.disconnect_all()
    """

    def __init__(self) -> None:
        self._connectors: dict[str, MarketDataConnector] = {}
        self._lock = Lock()

    def register(self, connector: MarketDataConnector) -> None:
        """注册连接器。

        Args:
            connector: MarketDataConnector 实例

        Raises:
            ConnectorAlreadyRegisteredError: connector_id 已存在
        """
        cid = connector.vendor_id
        with self._lock:
            if cid in self._connectors:
                raise ConnectorAlreadyRegisteredError(
                    f"connector_id={cid!r} 已注册",
                    details={"connector_id": cid},
                )
            self._connectors[cid] = connector
        _logger.info("连接器注册: %s (共 %d 个)", cid, self.count)

    def unregister(self, connector_id: str) -> MarketDataConnector:
        """注销连接器(自动断开)。

        Args:
            connector_id: 连接器 ID

        Returns:
            被注销的连接器实例

        Raises:
            ConnectorNotFoundError: connector_id 不存在
        """
        with self._lock:
            if connector_id not in self._connectors:
                raise ConnectorNotFoundError(
                    f"connector_id={connector_id!r} 未注册",
                    details={"connector_id": connector_id},
                )
            connector = self._connectors.pop(connector_id)
        # 断开(锁外执行, 避免死锁)
        try:
            connector.disconnect()
        except Exception:
            _logger.exception("注销时断开异常(忽略): %s", connector_id)
        _logger.info("连接器注销: %s (剩余 %d 个)", connector_id, self.count)
        return connector

    def get(self, connector_id: str) -> MarketDataConnector | None:
        """按 ID 查询连接器。不存在返回 None。"""
        with self._lock:
            return self._connectors.get(connector_id)

    def list_connectors(
        self, state: ConnectionState | None = None
    ) -> list[MarketDataConnector]:
        """列出所有/按连接状态过滤的连接器。

        Args:
            state: 可选状态过滤, None=全部

        Returns:
            连接器列表(副本)
        """
        with self._lock:
            connectors = list(self._connectors.values())
        if state is not None:
            connectors = [c for c in connectors if c.connection_state == state]
        return connectors

    def connect_all(self) -> dict[str, bool]:
        """批量连接所有已注册连接器。

        容错: 单个失败不阻断, 记录 False。

        Returns:
            {connector_id: success} 映射
        """
        with self._lock:
            connectors = list(self._connectors.values())
        results: dict[str, bool] = {}
        for conn in connectors:
            try:
                conn.connect()
                results[conn.vendor_id] = True
            except Exception:
                _logger.exception("连接失败: %s", conn.vendor_id)
                results[conn.vendor_id] = False
        succeeded = sum(results.values())
        _logger.info(
            "批量连接完成: %d/%d 成功", succeeded, len(results)
        )
        return results

    def disconnect_all(self) -> dict[str, bool]:
        """批量断开所有连接器。

        容错: 单个失败不阻断, 记录 False。

        Returns:
            {connector_id: success} 映射
        """
        with self._lock:
            connectors = list(self._connectors.values())
        results: dict[str, bool] = {}
        for conn in connectors:
            try:
                conn.disconnect()
                results[conn.vendor_id] = True
            except Exception:
                _logger.exception("断开失败: %s", conn.vendor_id)
                results[conn.vendor_id] = False
        succeeded = sum(results.values())
        _logger.info(
            "批量断开完成: %d/%d 成功", succeeded, len(results)
        )
        return results

    def health_check_all(self) -> dict[str, bool]:
        """批量健康检查。

        Returns:
            {connector_id: healthy} 映射
        """
        with self._lock:
            connectors = list(self._connectors.values())
        results: dict[str, bool] = {}
        for conn in connectors:
            try:
                results[conn.vendor_id] = conn.health_check()
            except Exception:
                _logger.exception("健康检查异常: %s", conn.vendor_id)
                results[conn.vendor_id] = False
        return results

    @property
    def count(self) -> int:
        """已注册连接器数量。"""
        with self._lock:
            return len(self._connectors)

    def __repr__(self) -> str:
        with self._lock:
            return f"ConnectorManager(count={len(self._connectors)})"


__all__ = [
    "ConnectorAlreadyRegisteredError",
    "ConnectorManager",
    "ConnectorNotFoundError",
]
