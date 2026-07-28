# [A_test] module_id: MOD-GOV_security_capability | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_security_capability

# [INVARIANTS] deny规则不可绕过;default_deny兜底;glob匹配fnmatch语义

# [MODIFY-GUARD] capability.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] CapabilityDenied

# [TESTS] pytest tests/test_security_capability.py -q
# [TTL] task_bound

import warnings

import pytest

from zephyr.shared.security.capability import (
    Capability,
    CapabilityDenied,
    CapabilityRegistry,
    capability_check,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    CapabilityRegistry.reset()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        yield
    CapabilityRegistry.reset()


class TestCapability:
    def test_creation(self):
        cap = Capability(name="test", allow=["src/**"], deny=["src/secrets/**"])
        assert cap.name == "test"
        assert cap.allow == ["src/**"]
        assert cap.deny == ["src/secrets/**"]

    def test_frozen(self):
        cap = Capability(name="test")
        with pytest.raises(Exception):
            cap.name = "changed"

    def test_empty_name_raises(self):
        with pytest.raises(Exception):
            Capability(name="")


class TestCapabilityDenied:
    def test_attributes(self):
        err = CapabilityDenied(action="write", target_path="secret.key", rule_name="deny_secrets")
        assert err.action == "write"
        assert err.target_path == "secret.key"
        assert err.rule_name == "deny_secrets"
        assert "write" in str(err)
        assert "deny_secrets" in str(err)

    def test_default_reason(self):
        err = CapabilityDenied("read", "path", "rule")
        assert err.reason == "deny"


class TestCapabilityRegistry:
    def test_singleton(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            r1 = CapabilityRegistry()
            r2 = CapabilityRegistry()
            assert r1 is r2

    def test_reset_creates_new(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            r1 = CapabilityRegistry()
        CapabilityRegistry.reset()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            r2 = CapabilityRegistry()
            assert r1 is not r2

    def test_check_with_empty_registry(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            registry = CapabilityRegistry()
        registry.capabilities = []
        ok, info = registry.check("read", "any/path")
        assert ok is False
        assert info["reason"] == "no_matching_rule"

    def test_check_allow_rule(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            registry = CapabilityRegistry()
        registry.capabilities = [
            Capability(name="allow_src", allow=["src/**"], deny=[]),
        ]
        ok, info = registry.check("read", "src/zephyr/main.py")
        assert ok is True
        assert info["reason"] == "allow"

    def test_check_deny_rule(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            registry = CapabilityRegistry()
        registry.capabilities = [
            Capability(name="deny_secrets", allow=[], deny=["*.pem"]),
        ]
        ok, info = registry.check("read", "key.pem")
        assert ok is False
        assert info["reason"] == "deny"

    def test_deny_overrides_allow(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            registry = CapabilityRegistry()
        registry.capabilities = [
            Capability(name="mixed", allow=["src/**"], deny=["key.pem"]),
        ]
        ok, info = registry.check("read", "key.pem")
        assert ok is False

    def test_glob_star_star(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            registry = CapabilityRegistry()
        registry.capabilities = [
            Capability(name="allow_all", allow=["**"], deny=[]),
        ]
        ok, info = registry.check("read", "any/deep/path/file.py")
        assert ok is True

    def test_simple_glob(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            registry = CapabilityRegistry()
        registry.capabilities = [
            Capability(name="allow_py", allow=["*.py"], deny=[]),
        ]
        ok, info = registry.check("read", "test.py")
        assert ok is True
        ok2, _ = registry.check("read", "test.txt")
        assert ok2 is False

    def test_match_any_glob(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            registry = CapabilityRegistry()
        registry.capabilities = [
            Capability(name="multi", allow=["src/**", "tests/**"], deny=[]),
        ]
        ok1, _ = registry.check("read", "src/main.py")
        ok2, _ = registry.check("read", "tests/test_main.py")
        ok3, _ = registry.check("read", "docs/readme.md")
        assert ok1 is True
        assert ok2 is True
        assert ok3 is False


class TestCapabilityCheck:
    def test_allowed_does_not_raise(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            registry = CapabilityRegistry()
        registry.capabilities = [
            Capability(name="allow_all", allow=["**"], deny=[]),
        ]
        ok, info = capability_check("read", "any/path")
        assert ok is True

    def test_denied_raises(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            registry = CapabilityRegistry()
        registry.capabilities = []
        with pytest.raises(CapabilityDenied) as exc_info:
            capability_check("write", "secret.key")
        assert exc_info.value.rule_name == "default_deny"
