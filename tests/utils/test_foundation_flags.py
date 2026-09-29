# [A_test] module_id: MOD-GOV_foundation_flags | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_foundation_flags
# [DOMAIN] D_SHARED

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


class TestAuditRotation:
    """审计 jsonl 超限翻代（2026-09-30：2.1GB 无轮转事故治本，gate_survival_adjudication §6）。"""

    def test_oversized_audit_rotates(self, tmp_path):
        import json as _json
        from pathlib import Path as _Path

        from zephyr.shared.foundation.flags import FlagRegistry as _FR

        audit = tmp_path / "feature_flags.jsonl"
        reg = _FR(audit_path=audit)

        # 阈值压到 200 字节构造翻代条件（不改类常量，走 monkeypatch 式子类覆写）
        class _Small(_FR):
            _AUDIT_ROTATE_BYTES = 200

        reg2 = _Small(audit_path=audit)
        reg2.register(FeatureFlag("a1", state=FlagState.ALWAYS_ON, description="x" * 80))
        reg2.register(FeatureFlag("a2", state=FlagState.ALWAYS_OFF, description="y" * 80))
        # 两次 100+ 字节追加已超 200 → 第二次写入前翻代：.1 存在且当前文件只剩最后一条
        rotated = audit.with_name(audit.name + ".1")
        assert rotated.exists(), "oversized audit must rotate to .1"
        lines_now = audit.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines_now) == 1, lines_now
        _json.loads(lines_now[0])

    def test_small_audit_no_rotate(self, tmp_path):
        from zephyr.shared.foundation.flags import FlagRegistry as _FR

        audit = tmp_path / "feature_flags.jsonl"
        reg = _FR(audit_path=audit)
        reg.register(FeatureFlag("ok1", state=FlagState.ALWAYS_ON))
        reg.register(FeatureFlag("ok2", state=FlagState.ALWAYS_OFF))
        assert not audit.with_name(audit.name + ".1").exists()
        assert len(audit.read_text(encoding="utf-8").strip().splitlines()) == 2
