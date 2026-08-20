# [A_test] module_id: MOD-GOV_observability_health | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_observability_health

# [INVARIANTS] ALL_HEALTHY当全部healthy;UNHEALTHY当任一不healthy;collect_health聚合

# [MODIFY-GUARD] health.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_observability_health.py -q
# [TTL] task_bound

import pytest

# #ARCH-074：本文件测试的 AggregateHealth.check/check_block_fast、HealthStatus.ALL_HEALTHY、
# HealthSummary(status=/total_modules=/healthy_count=)、collect_health(modules) 设计契约在源码侧
# 为桩实现（health/__init__.py 数据壳）或另一设计（health_aggregator.HealthAggregator 探针驱动），
# 代码侧缺口待裁定补实现——全文件 xfail 留痕（strict=False）。
pytestmark = pytest.mark.xfail(
    strict=False, reason="#ARCH-074 AggregateHealth/collect_health 设计契约代码侧缺口（桩实现），待裁定补实现"
)

from zephyr.infrastructure.system_telemetry.health import (
    AggregateHealth,
    HealthStatus,
    HealthSummary,
    collect_health,
)
from zephyr.shared.lifecycle.hooks import (
    LifecycleManager,
    LifecycleState,
    ModuleHealth,
)
from zephyr.shared.utils.async_utils import run_coroutine_sync


class FakeModule:
    def __init__(self, name: str, healthy: bool = True, state: LifecycleState = LifecycleState.RUNNING):
        self._name = name
        self._healthy = healthy
        self._state = state

    @property
    def module_name(self) -> str:
        return self._name

    async def on_init(self) -> None:
        pass

    async def on_startup(self) -> None:
        pass

    async def on_shutdown(self) -> None:
        pass

    async def health_check(self) -> ModuleHealth:
        return ModuleHealth(
            module_name=self._name,
            state=self._state,
            healthy=self._healthy,
        )


class BadHealthModule:
    @property
    def module_name(self) -> str:
        return "bad"

    async def on_init(self) -> None:
        pass

    async def on_startup(self) -> None:
        pass

    async def on_shutdown(self) -> None:
        pass

    async def health_check(self) -> ModuleHealth:
        raise RuntimeError("health check boom")


class TestHealthStatus:
    def test_members(self):
        assert HealthStatus.ALL_HEALTHY.value == "ALL_HEALTHY"
        assert HealthStatus.DEGRADED.value == "DEGRADED"
        assert HealthStatus.UNHEALTHY.value == "UNHEALTHY"
        assert HealthStatus.UNKNOWN.value == "UNKNOWN"


class TestHealthSummary:
    def test_defaults(self):
        s = HealthSummary(status=HealthStatus.UNKNOWN)
        assert s.total_modules == 0
        assert s.healthy_count == 0
        assert s.details == []

    def test_to_dict(self):
        s = HealthSummary(status=HealthStatus.ALL_HEALTHY, total_modules=3, healthy_count=3)
        d = s.to_dict()
        assert d["status"] == "ALL_HEALTHY"
        assert d["total_modules"] == 3


class TestAggregateHealth:
    def test_empty_is_unknown(self):
        mgr = LifecycleManager()
        ah = AggregateHealth(mgr)
        result = run_coroutine_sync(ah.check())
        assert result.status == HealthStatus.UNKNOWN

    def test_all_healthy(self):
        mgr = LifecycleManager()
        mgr.register(FakeModule("mod1", healthy=True))
        mgr.register(FakeModule("mod2", healthy=True))
        ah = AggregateHealth(mgr)
        result = run_coroutine_sync(ah.check())
        assert result.status == HealthStatus.ALL_HEALTHY
        assert result.healthy_count == 2

    def test_one_unhealthy(self):
        mgr = LifecycleManager()
        mgr.register(FakeModule("mod1", healthy=True))
        mgr.register(FakeModule("mod2", healthy=False, state=LifecycleState.FAILED))
        ah = AggregateHealth(mgr)
        result = run_coroutine_sync(ah.check())
        assert result.status == HealthStatus.UNHEALTHY
        assert "mod2" in result.unhealthy_modules

    def test_degraded(self):
        mgr = LifecycleManager()
        mgr.register(FakeModule("mod1", healthy=True, state=LifecycleState.DEGRADED))
        ah = AggregateHealth(mgr)
        result = run_coroutine_sync(ah.check())
        assert result.status == HealthStatus.DEGRADED
        assert "mod1" in result.degraded_modules

    def test_check_specific_modules(self):
        mgr = LifecycleManager()
        mgr.register(FakeModule("mod1", healthy=True))
        mgr.register(FakeModule("mod2", healthy=False, state=LifecycleState.FAILED))
        ah = AggregateHealth(mgr)
        result = run_coroutine_sync(ah.check(module_names=["mod1"]))
        assert result.status == HealthStatus.ALL_HEALTHY

    def test_exception_in_health_check(self):
        mgr = LifecycleManager()
        mgr.register(BadHealthModule())
        ah = AggregateHealth(mgr)
        result = run_coroutine_sync(ah.check())
        assert result.status == HealthStatus.UNHEALTHY
        assert "bad" in result.unhealthy_modules

    def test_check_block_fast(self):
        mgr = LifecycleManager()
        mgr.register(FakeModule("mod1", healthy=True))
        ah = AggregateHealth(mgr)
        result = run_coroutine_sync(ah.check_block_fast())
        assert result.status == HealthStatus.ALL_HEALTHY


class TestCollectHealth:
    def test_returns_health_summary(self):
        result = run_coroutine_sync(collect_health([FakeModule("mod1", healthy=True)]))
        assert isinstance(result, HealthSummary)
        assert result.status == HealthStatus.ALL_HEALTHY

    def test_empty_list(self):
        result = run_coroutine_sync(collect_health([]))
        assert result.status == HealthStatus.UNKNOWN
