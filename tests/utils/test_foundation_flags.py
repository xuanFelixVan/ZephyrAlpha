# [A_test] module_id: MOD-GOV_foundation_flags | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_foundation_flags

# [INVARIANTS] FeatureFlag不可变;FlagRegistry单次注册;FlagNotFoundError继承ZephyrBaseError

# [MODIFY-GUARD] flags.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] FlagNotFoundError

# [TESTS] pytest tests/test_foundation_flags.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.foundation.flags import (
    FeatureFlag,
    FlagNotFoundError,
    FlagRegistry,
    FlagState,
)


class TestFlagState:
    def test_members(self):
        assert FlagState.ALWAYS_ON.value == "ALWAYS_ON"
        assert FlagState.CONDITIONAL.value == "CONDITIONAL"
        assert FlagState.ALWAYS_OFF.value == "ALWAYS_OFF"


class TestFeatureFlag:
    def test_default_state_is_off(self):
        flag = FeatureFlag("test_flag")
        assert flag.state == FlagState.ALWAYS_OFF
        assert flag.is_enabled() is False

    def test_always_on(self):
        flag = FeatureFlag("on_flag", state=FlagState.ALWAYS_ON)
        assert flag.is_enabled() is True

    def test_always_off(self):
        flag = FeatureFlag("off_flag", state=FlagState.ALWAYS_OFF)
        assert flag.is_enabled() is False

    def test_conditional_no_restrictions(self):
        flag = FeatureFlag("cond_flag", state=FlagState.CONDITIONAL)
        assert flag.is_enabled() is True

    def test_conditional_with_allowed_modules_match(self):
        flag = FeatureFlag(
            "mod_flag",
            state=FlagState.CONDITIONAL,
            allowed_modules=["MOD-INF-016"],
        )
        assert flag.is_enabled(module_id="MOD-INF-016") is True

    def test_conditional_with_allowed_modules_no_match(self):
        flag = FeatureFlag(
            "mod_flag",
            state=FlagState.CONDITIONAL,
            allowed_modules=["MOD-INF-016"],
        )
        assert flag.is_enabled(module_id="MOD-INF-999") is False

    def test_conditional_with_allowed_agents_match(self):
        flag = FeatureFlag(
            "agent_flag",
            state=FlagState.CONDITIONAL,
            allowed_agents=["agent-build"],
        )
        assert flag.is_enabled(agent_id="agent-build") is True

    def test_conditional_with_allowed_agents_no_match(self):
        flag = FeatureFlag(
            "agent_flag",
            state=FlagState.CONDITIONAL,
            allowed_agents=["agent-build"],
        )
        assert flag.is_enabled(agent_id="agent-review") is False

    def test_rollout_pct(self):
        flag = FeatureFlag(
            "rollout_flag",
            state=FlagState.CONDITIONAL,
            rollout_pct=50,
        )
        results = [flag.is_enabled(module_id=f"mod-{i}") for i in range(100)]
        enabled_count = sum(results)
        assert 0 < enabled_count < 100

    def test_frozen(self):
        flag = FeatureFlag("frozen_flag")
        with pytest.raises(AttributeError):
            flag.key = "changed"


class TestFlagRegistry:
    @pytest.fixture(autouse=True)
    def _clean_registry(self):
        registry = FlagRegistry()
        registry.reset()
        yield
        registry.reset()

    def test_register_and_get(self):
        registry = FlagRegistry()
        flag = FeatureFlag("test_flag", state=FlagState.ALWAYS_ON)
        registry.register(flag)
        retrieved = registry.get("test_flag")
        assert retrieved.key == "test_flag"
        assert retrieved.state == FlagState.ALWAYS_ON

    def test_get_not_found_raises(self):
        registry = FlagRegistry()
        with pytest.raises(FlagNotFoundError) as exc_info:
            registry.get("nonexistent")
        assert "nonexistent" in str(exc_info.value)

    def test_is_enabled(self):
        registry = FlagRegistry()
        registry.register(FeatureFlag("feat", state=FlagState.ALWAYS_ON))
        assert registry.is_enabled("feat") is True

    def test_is_enabled_not_found_raises(self):
        registry = FlagRegistry()
        with pytest.raises(FlagNotFoundError):
            registry.is_enabled("missing")

    def test_unregister(self):
        registry = FlagRegistry()
        registry.register(FeatureFlag("temp_flag"))
        registry.unregister("temp_flag")
        with pytest.raises(FlagNotFoundError):
            registry.get("temp_flag")

    def test_unregister_nonexistent_no_error(self):
        registry = FlagRegistry()
        registry.unregister("no_such_flag")

    def test_list_all(self):
        registry = FlagRegistry()
        registry.register(FeatureFlag("a"))
        registry.register(FeatureFlag("b"))
        all_flags = registry.list_all()
        assert "a" in all_flags
        assert "b" in all_flags

    def test_reset(self):
        registry = FlagRegistry()
        registry.register(FeatureFlag("x"))
        registry.reset()
        with pytest.raises(FlagNotFoundError):
            registry.get("x")

    def test_register_overwrites(self):
        registry = FlagRegistry()
        registry.register(FeatureFlag("dup", state=FlagState.ALWAYS_OFF))
        registry.register(FeatureFlag("dup", state=FlagState.ALWAYS_ON))
        assert registry.get("dup").state == FlagState.ALWAYS_ON


class TestFlagNotFoundError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = FlagNotFoundError("not found", details={"key": "x"})
        assert isinstance(err, ZephyrBaseError)
