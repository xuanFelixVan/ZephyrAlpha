"""
单元测试：src/zephyr/l01_infrastructure/infrastructure_base.py
=============================================================

覆盖矩阵：
  InfrastructureManagerBase (ABC):
    - 抽象类不可实例化 × 1
  ConfigManagerBase (ABC):
    - 抽象类不可实例化 × 1
    - reload() 默认实现：validate 失败时抛出 ValueError × 1
    - reload() 默认实现：validate 通过时返回 config × 1
  KillSwitchManagerBase (ABC):
    - 抽象类不可实例化 × 1
  SystemHealth:
    - 默认值 × 1
    - frozen × 1
"""

from datetime import datetime

import pytest
from zephyr.l01_infrastructure.infrastructure_base import (
    ConfigManagerBase,
    InfrastructureManagerBase,
    KillSwitchManagerBase,
    SystemHealth,
)


class TestSystemHealth:
    def test_defaults(self):
        h = SystemHealth(is_healthy=True)
        assert h.is_healthy is True
        assert h.checks == {}
        assert h.message == ""
        assert isinstance(h.timestamp, datetime)

    def test_frozen(self):
        h = SystemHealth(is_healthy=True)
        with pytest.raises(AttributeError):
            h.is_healthy = False


class TestInfrastructureManagerBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            InfrastructureManagerBase()


class TestConfigManagerBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            ConfigManagerBase()

    def test_reload_validate_failure_raises(self):
        class FailingConfigManager(ConfigManagerBase):
            def load(self, source=None):
                return {"env": "bad"}

            def validate(self, config):
                return False

        mgr = FailingConfigManager()
        with pytest.raises(ValueError, match="Reloaded config failed validation"):
            mgr.reload()

    def test_reload_validate_pass_returns_config(self):
        class PassingConfigManager(ConfigManagerBase):
            def load(self, source=None):
                return {"env": "prod"}

            def validate(self, config):
                return True

        mgr = PassingConfigManager()
        result = mgr.reload()
        assert result == {"env": "prod"}


class TestKillSwitchManagerBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            KillSwitchManagerBase()

    def test_concrete_implementation(self):
        class MockKillSwitch(KillSwitchManagerBase):
            __killer_id__ = "mock"

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
                return 50.0

        ks = MockKillSwitch()
        assert ks.is_active() is False
        assert ks.trigger("test") is True
        assert ks.is_active() is True
        assert ks.latency_us() == 50.0
        assert ks.reset("confirmed") is True
        assert ks.is_active() is False
