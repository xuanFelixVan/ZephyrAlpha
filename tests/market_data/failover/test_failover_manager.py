# [BLUEPRINT] MOD-MKT-004 | docs/03_modules/_domain_mkt_data/failover/blueprint.md
# [MODULE] tests.market_data.failover.test_failover_manager
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.failover
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-MKT-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-MKT-004 Failover Manager 单元测试.

覆盖: 初始选择、健康检查失败切换、自动 failback、手动 failover、
无可用源(ALL_FAILED)、轮询策略、事件回调、历史记录、线程安全.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.market_data.failover import (
    FailoverConfig,
    FailoverError,
    FailoverEvent,
    FailoverManager,
    FailoverPolicy,
    FailoverReason,
)
from zephyr.market_data.vendor_base import (
    MarketDataVendor,
    VendorCapabilities,
    VendorError,
    VendorStatus,
)
from zephyr.market_data.vendor_registry import VendorRegistry


class MockVendor(MarketDataVendor):
    """可控制健康状态的 mock vendor。"""

    def __init__(self, vid: str, healthy: bool = True) -> None:
        super().__init__()
        self._vid = vid
        self._healthy = healthy

    @property
    def vendor_id(self) -> str:
        return self._vid

    @property
    def capabilities(self) -> VendorCapabilities:
        return VendorCapabilities()

    def fetch_daily_kline(self, symbol, start_date, end_date):
        if not self._healthy:
            raise VendorError(f"{self._vid} 不可用")
        return []

    def health_check(self) -> bool:
        return self._healthy


def make_registry(*vendors: MockVendor) -> VendorRegistry:
    reg = VendorRegistry()
    for v in vendors:
        v.set_status(VendorStatus.ACTIVE)
        reg.register(v)
    return reg


# ============== 配置校验 ==============


class TestConfig:
    def test_empty_priority_list_rejected(self):
        with pytest.raises(FailoverError, match="priority_list"):
            FailoverManager(VendorRegistry(), FailoverConfig(priority_list=()))

    def test_config_immutable(self):
        cfg = FailoverConfig(priority_list=("a",))
        with pytest.raises(Exception):
            cfg.auto_failback = False  # type: ignore[misc]


# ============== 初始选择 ==============


class TestInitialSelection:
    def test_select_first_healthy(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        event = mgr.check_and_failover()
        assert event is not None
        assert event.to_vendor == "primary"
        assert event.reason == FailoverReason.INITIAL
        assert mgr.active_vendor_id == "primary"

    def test_select_second_if_first_unhealthy(self):
        v1 = MockVendor("primary", healthy=False)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        event = mgr.check_and_failover()
        assert event is not None
        assert event.to_vendor == "secondary"
        assert mgr.active_vendor_id == "secondary"

    def test_all_failed_initial(self):
        v1 = MockVendor("primary", healthy=False)
        v2 = MockVendor("secondary", healthy=False)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        event = mgr.check_and_failover()
        assert event is not None
        assert event.reason == FailoverReason.ALL_FAILED
        assert event.to_vendor is None
        assert mgr.active_vendor_id is None

    def test_no_event_when_already_healthy(self):
        v1 = MockVendor("primary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1),
            FailoverConfig(priority_list=("primary",)),
        )
        mgr.check_and_failover()  # initial -> primary
        event = mgr.check_and_failover()  # already healthy
        assert event is None


# ============== 健康检查失败切换 ==============


class TestHealthCheckFailover:
    def test_failover_on_health_check_fail(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        mgr.check_and_failover()  # -> primary
        assert mgr.active_vendor_id == "primary"

        # primary 挂了
        v1._healthy = False
        event = mgr.check_and_failover()
        assert event is not None
        assert event.from_vendor == "primary"
        assert event.to_vendor == "secondary"
        assert event.reason == FailoverReason.HEALTH_CHECK_FAILED
        assert mgr.active_vendor_id == "secondary"

    def test_failover_marks_old_vendor_error(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        mgr.check_and_failover()
        v1._healthy = False
        mgr.check_and_failover()
        assert v1.status == VendorStatus.ERROR

    def test_all_failed_after_failover(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        mgr.check_and_failover()  # -> primary
        v1._healthy = False
        mgr.check_and_failover()  # -> secondary
        v2._healthy = False
        event = mgr.check_and_failover()  # all failed
        assert event is not None
        assert event.reason == FailoverReason.ALL_FAILED
        assert mgr.active_vendor_id is None

    def test_recover_after_all_failed(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        mgr.check_and_failover()
        v1._healthy = False
        v2._healthy = False
        mgr.check_and_failover()  # all failed
        # 恢复
        v1._healthy = True
        event = mgr.check_and_failover()
        assert event is not None
        assert event.to_vendor == "primary"
        assert event.reason == FailoverReason.INITIAL


# ============== 自动 failback ==============


class TestAutoFailback:
    def test_auto_failback_to_primary(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(
                priority_list=("primary", "secondary"),
                auto_failback=True,
            ),
        )
        mgr.check_and_failover()  # -> primary
        v1._healthy = False
        mgr.check_and_failover()  # -> secondary
        assert mgr.active_vendor_id == "secondary"

        # primary 恢复
        v1._healthy = True
        event = mgr.check_and_failover()
        assert event is not None
        assert event.from_vendor == "secondary"
        assert event.to_vendor == "primary"
        assert event.reason == FailoverReason.AUTO_FAILBACK

    def test_no_failback_when_disabled(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(
                priority_list=("primary", "secondary"),
                auto_failback=False,
            ),
        )
        mgr.check_and_failover()  # -> primary
        v1._healthy = False
        mgr.check_and_failover()  # -> secondary
        v1._healthy = True
        event = mgr.check_and_failover()  # no failback
        assert event is None
        assert mgr.active_vendor_id == "secondary"


# ============== 手动操作 ==============


class TestManualOperations:
    def test_manual_failover(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        mgr.check_and_failover()  # -> primary
        event = mgr.failover("测试手动切换")
        assert event is not None
        assert event.to_vendor == "secondary"
        assert event.reason == FailoverReason.MANUAL

    def test_manual_failback(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(
                priority_list=("primary", "secondary"),
            ),
        )
        mgr.check_and_failover()  # -> primary
        v1._healthy = False
        mgr.check_and_failover()  # -> secondary
        v1._healthy = True
        event = mgr.failback()
        assert event is not None
        assert event.to_vendor == "primary"

    def test_failback_when_primary_unhealthy(self):
        v1 = MockVendor("primary", healthy=False)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        mgr.check_and_failover()  # -> secondary (primary unhealthy)
        assert mgr.failback() is None  # primary still unhealthy

    def test_failback_when_already_primary(self):
        v1 = MockVendor("primary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1),
            FailoverConfig(priority_list=("primary",)),
        )
        mgr.check_and_failover()
        assert mgr.failback() is None


# ============== 轮询策略 ==============


class TestRoundRobin:
    def test_round_robin_failover(self):
        v1 = MockVendor("a", healthy=True)
        v2 = MockVendor("b", healthy=True)
        v3 = MockVendor("c", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2, v3),
            FailoverConfig(
                priority_list=("a", "b", "c"),
                policy=FailoverPolicy.ROUND_ROBIN,
                auto_failback=False,
            ),
        )
        mgr.check_and_failover()  # initial -> a (index 0->1)
        assert mgr.active_vendor_id == "a"

        # 手动切换: round_robin 从 index 1 开始 -> b
        event = mgr.failover()
        assert event.to_vendor == "b"

        # 再切: index 2 -> c
        event = mgr.failover()
        assert event.to_vendor == "c"

        # 再切: index 0 -> a (回环)
        event = mgr.failover()
        assert event.to_vendor == "a"


# ============== 事件回调 / 历史 ==============


class TestEventCallbackHistory:
    def test_callback_fired_on_failover(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        events: list[FailoverEvent] = []
        mgr.on_failover(events.append)
        mgr.check_and_failover()  # initial
        assert len(events) == 1

    def test_callback_exception_isolated(self):
        v1 = MockVendor("primary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1),
            FailoverConfig(priority_list=("primary",)),
        )
        good: list[FailoverEvent] = []

        def bad_cb(_e: FailoverEvent) -> None:
            raise ValueError("boom")

        mgr.on_failover(bad_cb)
        mgr.on_failover(good.append)
        mgr.check_and_failover()
        assert len(good) == 1  # bad callback didn't block good

    def test_history_recorded(self):
        v1 = MockVendor("primary", healthy=True)
        v2 = MockVendor("secondary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("primary", "secondary")),
        )
        mgr.check_and_failover()  # initial
        v1._healthy = False
        mgr.check_and_failover()  # failover
        history = mgr.history
        assert len(history) == 2
        assert history[0].reason == FailoverReason.INITIAL
        assert history[1].reason == FailoverReason.HEALTH_CHECK_FAILED

    def test_history_max_eviction(self):
        v1 = MockVendor("a", healthy=True)
        v2 = MockVendor("b", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(
                priority_list=("a", "b"),
                auto_failback=False,
                history_max=3,
            ),
        )
        mgr.check_and_failover()  # 1
        for _ in range(5):
            mgr.failover()  # 5 more
        history = mgr.history
        assert len(history) <= 3

    def test_event_timestamp(self):
        v1 = MockVendor("primary", healthy=True)
        mgr = FailoverManager(
            make_registry(v1),
            FailoverConfig(priority_list=("primary",)),
        )
        before = datetime.now(timezone.utc)
        event = mgr.check_and_failover()
        after = datetime.now(timezone.utc)
        assert event is not None
        assert before <= event.timestamp <= after


# ============== 线程安全 ==============


class TestThreadSafety:
    def test_concurrent_check_safe(self):
        import threading

        v1 = MockVendor("a", healthy=True)
        v2 = MockVendor("b", healthy=True)
        mgr = FailoverManager(
            make_registry(v1, v2),
            FailoverConfig(priority_list=("a", "b"), auto_failback=False),
        )
        errors: list[Exception] = []

        def worker() -> None:
            try:
                for _ in range(50):
                    mgr.check_and_failover()
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
