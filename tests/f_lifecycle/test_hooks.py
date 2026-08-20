# [A_test] module_id: MOD-GOV_hooks | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-394 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_hooks
# [INVARIANTS] LifecycleManager is per-instance; no shared state
# [MODIFY-GUARD] hooks.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] re-raises on init/startup failure
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.shared.lifecycle.hooks import (
    LifecycleAware,
    LifecycleManager,
    LifecycleState,
    ModuleHealth,
)
from zephyr.shared.utils.async_utils import run_coroutine_sync


class FakeModule:
    def __init__(self, name: str = "mod_a") -> None:
        self.module_name = name
        self.init_called = False
        self.startup_called = False
        self.shutdown_called = False
        self.health_called = False
        self._healthy = True
        self._init_raises = False
        self._startup_raises = False

    @property
    def startup_raises(self):
        """只读：startup_raises（R5 公共化）。"""
        return self._startup_raises

    @property
    def init_raises(self):
        """只读：init_raises（R5 公共化）。"""
        return self._init_raises

    @property
    def healthy(self):
        """只读：healthy（R5 公共化）。"""
        return self._healthy

    async def on_init(self) -> None:
        self.init_called = True
        if self._init_raises:
            raise RuntimeError("init failed")

    async def on_startup(self) -> None:
        self.startup_called = True
        if self._startup_raises:
            raise RuntimeError("startup failed")

    async def on_shutdown(self) -> None:
        self.shutdown_called = True

    def health_check(self) -> ModuleHealth:
        self.health_called = True
        return ModuleHealth(
            module_name=self.module_name,
            state=LifecycleState.RUNNING if self._healthy else LifecycleState.FAILED,
            healthy=self._healthy,
        )


class FailingHealthModule(FakeModule):
    def health_check(self) -> ModuleHealth:
        raise RuntimeError("health check crashed")


def _run(coro):
    return run_coroutine_sync(coro)


class TestModuleHealth:
    def test_defaults(self):
        h = ModuleHealth(module_name="x", state=LifecycleState.CREATED, healthy=True)
        assert h.module_name == "x"
        assert h.state == LifecycleState.CREATED
        assert h.healthy is True
        assert h.message == ""
        assert h.details == {}

    def test_custom(self):
        h = ModuleHealth(
            module_name="y",
            state=LifecycleState.FAILED,
            healthy=False,
            message="error",
            details={"code": 500},
        )
        assert h.healthy is False
        assert h.message == "error"
        assert h.details["code"] == 500

    def test_frozen(self):
        h = ModuleHealth(module_name="z", state=LifecycleState.RUNNING, healthy=True)
        with pytest.raises(Exception):
            h.healthy = False


class TestLifecycleState:
    def test_all_values(self):
        expected = [
            "CREATED",
            "INITIALIZING",
            "INITIALIZED",
            "STARTING",
            "RUNNING",
            "DEGRADED",
            "STOPPING",
            "STOPPED",
            "FAILED",
        ]
        actual = [s.value for s in LifecycleState]
        assert actual == expected


class TestLifecycleManagerRegister:
    def test_register_single(self):
        mgr = LifecycleManager()
        mod = FakeModule()
        mgr.register(mod)
        assert len(mgr.modules) == 1
        assert mgr.modules[0].module_name == "mod_a"

    def test_register_multiple(self):
        mgr = LifecycleManager()
        mgr.register(FakeModule("a"))
        mgr.register(FakeModule("b"))
        assert len(mgr.modules) == 2

    def test_modules_returns_copy(self):
        mgr = LifecycleManager()
        mgr.register(FakeModule())
        mods = mgr.modules
        mods.clear()
        assert len(mgr.modules) == 1


class TestLifecycleManagerStartupAll:
    def test_startup_all_success(self):
        mgr = LifecycleManager()
        mod = FakeModule()
        mgr.register(mod)
        _run(mgr.startup_all())
        assert mod.init_called is True
        assert mod.startup_called is True

    def test_startup_all_init_failure_raises(self):
        mgr = LifecycleManager()
        mod = FakeModule()
        mod._init_raises = True
        mgr.register(mod)
        with pytest.raises(RuntimeError, match="init failed"):
            _run(mgr.startup_all())

    def test_startup_all_startup_failure_raises(self):
        mgr = LifecycleManager()
        mod = FakeModule()
        mod._startup_raises = True
        mgr.register(mod)
        with pytest.raises(RuntimeError, match="startup failed"):
            _run(mgr.startup_all())

    def test_startup_all_empty(self):
        mgr = LifecycleManager()
        _run(mgr.startup_all())


class TestLifecycleManagerShutdownAll:
    def test_shutdown_all(self):
        mgr = LifecycleManager()
        mod = FakeModule()
        mgr.register(mod)
        _run(mgr.shutdown_all())
        assert mod.shutdown_called is True

    def test_shutdown_all_reversed_order(self):
        mgr = LifecycleManager()
        order = []
        a = FakeModule("a")
        b = FakeModule("b")
        a_orig = a.on_shutdown
        b_orig = b.on_shutdown

        async def a_shutdown():
            order.append("a")
            await a_orig()

        async def b_shutdown():
            order.append("b")
            await b_orig()

        a.on_shutdown = a_shutdown
        b.on_shutdown = b_shutdown
        mgr.register(a)
        mgr.register(b)
        _run(mgr.shutdown_all())
        assert order == ["b", "a"]

    def test_shutdown_all_exception_does_not_raise(self):
        mgr = LifecycleManager()
        mod = FakeModule()
        orig = mod.on_shutdown

        async def bad_shutdown():
            raise RuntimeError("shutdown boom")

        mod.on_shutdown = bad_shutdown
        mgr.register(mod)
        _run(mgr.shutdown_all())


class TestLifecycleManagerHealthCheckAll:
    def test_health_check_all_healthy(self):
        mgr = LifecycleManager()
        mgr.register(FakeModule("a"))
        mgr.register(FakeModule("b"))
        results = _run(mgr.health_check_all())
        assert len(results) == 2
        assert results["a"].healthy is True
        assert results["b"].healthy is True

    def test_health_check_all_unhealthy(self):
        mgr = LifecycleManager()
        mod = FakeModule()
        mod._healthy = False
        mgr.register(mod)
        results = _run(mgr.health_check_all())
        assert results["mod_a"].healthy is False
        assert results["mod_a"].state == LifecycleState.FAILED

    def test_health_check_all_exception(self):
        mgr = LifecycleManager()
        mod = FailingHealthModule("broken")
        mgr.register(mod)
        results = _run(mgr.health_check_all())
        assert results["broken"].healthy is False
        assert results["broken"].state == LifecycleState.FAILED

    def test_health_check_all_empty(self):
        mgr = LifecycleManager()
        results = _run(mgr.health_check_all())
        assert results == {}


class TestLifecycleAwareProtocol:
    def test_protocol_check(self):
        mod = FakeModule()
        assert isinstance(mod, LifecycleAware)

    def test_non_conforming_not_protocol(self):
        class NotAModule:
            name: str = "x"

        assert not isinstance(NotAModule(), LifecycleAware)
