# [A_test] module_id: MOD-GOV_infrastructure_base | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §infrastructure_base
# [MODULE] tests.test_infrastructure_base
# [INVARIANTS] ABC子类必须实现所有抽象方法; SystemHealth为frozen dataclass
# [MODIFY-GUARD] 仅当infrastructure_base公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_infrastructure_base.py -q
# [TTL] task_bound


import pytest

from zephyr.infrastructure.infrastructure_base import (
    ConfigManagerBase,
    InfrastructureManagerBase,
    KillSwitchManagerBase,
    SystemHealth,
)


class TestSystemHealth:
    def test_default_construction(self):
        health = SystemHealth(is_healthy=True)
        assert health.is_healthy is True
        assert health.checks == {}
        assert health.message == ""
        assert health.timestamp is not None

    def test_frozen(self):
        health = SystemHealth(is_healthy=True)
        with pytest.raises(AttributeError):
            health.is_healthy = False

    def test_custom_values(self):
        health = SystemHealth(
            is_healthy=False,
            checks={"db": False, "cache": True},
            message="db connection failed",
        )
        assert health.is_healthy is False
        assert health.checks["db"] is False
        assert health.message == "db connection failed"


class TestInfrastructureManagerBase:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            InfrastructureManagerBase()

    def test_concrete_implementation(self):
        class TestManager(InfrastructureManagerBase):
            def initialize(self) -> bool:
                return True

            def health(self) -> SystemHealth:
                return SystemHealth(is_healthy=True)

            def shutdown(self) -> None:
                pass

        manager = TestManager()
        assert manager.initialize() is True
        assert manager.health().is_healthy is True
        manager.shutdown()

    def test_partial_implementation_fails(self):
        class PartialManager(InfrastructureManagerBase):
            def initialize(self) -> bool:
                return True

        with pytest.raises(TypeError):
            PartialManager()


class TestConfigManagerBase:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            ConfigManagerBase()

    def test_concrete_implementation(self):
        class TestConfigManager(ConfigManagerBase):
            def load(self, source=None):
                return {"env": "test"}

            def validate(self, config):
                return "env" in config

        mgr = TestConfigManager()
        config = mgr.load()
        assert config == {"env": "test"}
        assert mgr.validate(config) is True

    def test_reload_calls_load_and_validate(self):
        class TestConfigManager(ConfigManagerBase):
            def __init__(self):
                self.load_count = 0

            def load(self, source=None):
                self.load_count += 1
                return {"env": "test"}

            def validate(self, config):
                return True

        mgr = TestConfigManager()
        result = mgr.reload()
        assert result == {"env": "test"}
        assert mgr.load_count == 1

    def test_reload_raises_on_invalid(self):
        class BadConfigManager(ConfigManagerBase):
            def load(self, source=None):
                return {"bad": True}

            def validate(self, config):
                return False

        mgr = BadConfigManager()
        with pytest.raises(ValueError, match="failed validation"):
            mgr.reload()


class TestKillSwitchManagerBase:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            KillSwitchManagerBase()

    def test_concrete_implementation(self):
        class TestKillSwitch(KillSwitchManagerBase):
            def __init__(self):
                self._active = False

            def trigger(self, reason, scope="all"):
                self._active = True
                return True

            def reset(self, confirmation):
                self._active = False
                return True

            def is_active(self):
                return self._active

            def latency_us(self):
                return 0.5

        ks = TestKillSwitch()
        assert ks.is_active() is False
        assert ks.trigger("test") is True
        assert ks.is_active() is True
        assert ks.latency_us() == 0.5
        assert ks.reset("confirm") is True
        assert ks.is_active() is False
