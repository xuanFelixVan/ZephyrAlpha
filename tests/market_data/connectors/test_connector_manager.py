# [BLUEPRINT] MOD-MKT-003 | docs/03_modules/_domain_mkt_data/connectors/blueprint.md
# [MODULE] tests.market_data.connectors.test_connector_manager
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.connectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-MKT-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-MKT-003 Connector Manager 单元测试.

覆盖: 注册/注销/查询、批量连接/断开/健康检查、容错(单个失败不阻断)、
重复注册拒绝、注销自动断开.
"""

from __future__ import annotations

import pytest

from zephyr.market_data.connectors import (
    ConnectorConfig,
    ConnectorManager,
    MarketDataConnector,
)
from zephyr.market_data.connectors.manager import (
    ConnectorAlreadyRegisteredError,
    ConnectorNotFoundError,
)
from zephyr.market_data.vendor_base import VendorCapabilities


class StubConnector(MarketDataConnector):
    """测试用 stub 连接器。"""

    def __init__(self, vid: str, connect_fails: bool = False) -> None:
        super().__init__(ConnectorConfig(endpoint="stub://", vendor_id=vid))
        self._fails = connect_fails
        self.disconnected_called = False

    @property
    def capabilities(self) -> VendorCapabilities:
        return VendorCapabilities()

    def _do_connect(self) -> None:
        if self._fails:
            raise RuntimeError("stub connect fail")

    def _do_disconnect(self) -> None:
        self.disconnected_called = True

    def fetch_daily_kline(self, symbol, start_date, end_date):
        return []


class TestRegisterUnregister:
    def test_register(self):
        mgr = ConnectorManager()
        mgr.register(StubConnector("a"))
        assert mgr.count == 1

    def test_duplicate_register_rejected(self):
        mgr = ConnectorManager()
        mgr.register(StubConnector("a"))
        with pytest.raises(ConnectorAlreadyRegisteredError):
            mgr.register(StubConnector("a"))

    def test_unregister_disconnects(self):
        mgr = ConnectorManager()
        conn = StubConnector("a")
        mgr.register(conn)
        conn.connect()
        removed = mgr.unregister("a")
        assert removed is conn
        assert removed.disconnected_called is True
        assert mgr.count == 0

    def test_unregister_nonexistent(self):
        mgr = ConnectorManager()
        with pytest.raises(ConnectorNotFoundError):
            mgr.unregister("nope")

    def test_get(self):
        mgr = ConnectorManager()
        conn = StubConnector("a")
        mgr.register(conn)
        assert mgr.get("a") is conn
        assert mgr.get("nope") is None

    def test_list_all(self):
        mgr = ConnectorManager()
        mgr.register(StubConnector("a"))
        mgr.register(StubConnector("b"))
        assert len(mgr.list_connectors()) == 2


class TestBatchOperations:
    def test_connect_all(self):
        mgr = ConnectorManager()
        mgr.register(StubConnector("a"))
        mgr.register(StubConnector("b"))
        results = mgr.connect_all()
        assert results == {"a": True, "b": True}

    def test_connect_all_with_failure(self):
        mgr = ConnectorManager()
        mgr.register(StubConnector("a"))
        mgr.register(StubConnector("b", connect_fails=True))
        results = mgr.connect_all()
        assert results["a"] is True
        assert results["b"] is False

    def test_disconnect_all(self):
        mgr = ConnectorManager()
        mgr.register(StubConnector("a"))
        mgr.register(StubConnector("b"))
        mgr.connect_all()
        results = mgr.disconnect_all()
        assert results == {"a": True, "b": True}

    def test_health_check_all(self):
        mgr = ConnectorManager()
        mgr.register(StubConnector("a"))
        mgr.register(StubConnector("b"))
        mgr.connect_all()
        health = mgr.health_check_all()
        assert health == {"a": True, "b": True}

    def test_health_check_all_unhealthy(self):
        mgr = ConnectorManager()
        mgr.register(StubConnector("a"))
        # not connected -> unhealthy
        health = mgr.health_check_all()
        assert health == {"a": False}

    def test_empty_manager(self):
        mgr = ConnectorManager()
        assert mgr.connect_all() == {}
        assert mgr.disconnect_all() == {}
        assert mgr.health_check_all() == {}
        assert mgr.count == 0
