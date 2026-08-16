# [A_test] module_id: MOD-GOV_lifecycle_hooks | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_lifecycle_hooks

# [INVARIANTS] LifecycleManager按注册顺序init+startup;反向shutdown;异常传播

# [MODIFY-GUARD] hooks.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_lifecycle_hooks.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.lifecycle.hooks import (
    LifecycleAware,
    LifecycleManager,
    LifecycleState,
    ModuleHealth,
)
from zephyr.shared.utils.async_utils import run_coroutine_sync


class FakeModule:
    def __init__(self, name: str, fail_init: bool = False, fail_startup: bool = False):
        self._name = name
        self._fail_init = fail_init
        self._fail_startup = fail_startup
        self._state = LifecycleState.CREATED
        self.init_called = False
        self.startup_called = False
        self.shutdown_called = False

    @property
    def module_name(self) -> str:
        return self._name

    async def on_init(self) -> None:
        self.init_called = True
        if self._fail_init:
            raise RuntimeError(f"{self._name} init failed")
        self._state = LifecycleState.INITIALIZED

    async def on_startup(self) -> None:
        self.startup_called = True
        if self._fail_startup:
            raise RuntimeError(f"{self._name} startup failed")
        self._state = LifecycleState.RUNNING

    async def on_shutdown(self) -> None:
        self.shutdown_called = True
        self._state = LifecycleState.STOPPED

    def health_check(self) -> ModuleHealth:
        return ModuleHealth(
            module_name=self._name,
            state=self._state,
            healthy=self._state in (LifecycleState.RUNNING, LifecycleState.INITIALIZED),
        )


class TestLifecycleState:
    def test_members(self):
        assert LifecycleState.CREATED.value == "CREATED"
        assert LifecycleState.RUNNING.value == "RUNNING"
        assert LifecycleState.STOPPED.value == "STOPPED"
        assert LifecycleState.FAILED.value == "FAILED"
        assert LifecycleState.DEGRADED.value == "DEGRADED"


class TestModuleHealth:
    def test_defaults(self):
        h = ModuleHealth(module_name="test", state=LifecycleState.RUNNING, healthy=True)
        assert h.message == ""
        assert h.details == {}

    def test_frozen(self):
        h = ModuleHealth(module_name="test", state=LifecycleState.RUNNING, healthy=True)
        with pytest.raises(AttributeError):
            h.healthy = False


class TestLifecycleAware:
    def test_protocol_check(self):
        mod = FakeModule("test")
        assert isinstance(mod, LifecycleAware)

    def test_non_compliant_fails_protocol(self):
        class NotCompliant:
            pass

        assert not isinstance(NotCompliant(), LifecycleAware)


class TestLifecycleManager:
    def test_register_and_modules(self):
        mgr = LifecycleManager()
        mod = FakeModule("mod-1")
        mgr.register(mod)
        assert len(mgr.modules) == 1
        assert mgr.modules[0].module_name == "mod-1"

    def test_startup_all_order(self):
        mgr = LifecycleManager()
        mod1 = FakeModule("first")
        mod2 = FakeModule("second")
        mgr.register(mod1)
        mgr.register(mod2)
        run_coroutine_sync(mgr.startup_all())
        assert mod1.init_called is True
        assert mod2.init_called is True
        assert mod1.startup_called is True
        assert mod2.startup_called is True

    def test_shutdown_all_reverse_order(self):
        mgr = LifecycleManager()
        mod1 = FakeModule("first")
        mod2 = FakeModule("second")
        mgr.register(mod1)
        mgr.register(mod2)
        run_coroutine_sync(mgr.startup_all())
        run_coroutine_sync(mgr.shutdown_all())
        assert mod1.shutdown_called is True
        assert mod2.shutdown_called is True

    def test_init_failure_propagates(self):
        mgr = LifecycleManager()
        mod = FakeModule("bad", fail_init=True)
        mgr.register(mod)
        with pytest.raises(RuntimeError, match="init failed"):
            run_coroutine_sync(mgr.startup_all())

    def test_startup_failure_propagates(self):
        mgr = LifecycleManager()
        mod = FakeModule("bad", fail_startup=True)
        mgr.register(mod)
        with pytest.raises(RuntimeError, match="startup failed"):
            run_coroutine_sync(mgr.startup_all())

    def test_shutdown_continues_on_error(self):
        mgr = LifecycleManager()
        mod1 = FakeModule("good")
        mod2 = FakeModule("good2")
        mgr.register(mod1)
        mgr.register(mod2)
        run_coroutine_sync(mgr.startup_all())
        run_coroutine_sync(mgr.shutdown_all())
        assert mod1.shutdown_called is True
        assert mod2.shutdown_called is True

    def test_health_check_all(self):
        mgr = LifecycleManager()
        mod1 = FakeModule("healthy")
        mgr.register(mod1)
        run_coroutine_sync(mgr.startup_all())
        results = run_coroutine_sync(mgr.health_check_all())
        assert "healthy" in results
        assert results["healthy"].healthy is True

    def test_health_check_all_catches_exception(self):
        class BadHealth(FakeModule):
            def health_check(self):
                raise RuntimeError("health check boom")

        mgr = LifecycleManager()
        mgr.register(BadHealth("bad"))
        results = run_coroutine_sync(mgr.health_check_all())
        assert "bad" in results
        assert results["bad"].healthy is False
        assert results["bad"].state == LifecycleState.FAILED
