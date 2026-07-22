# [A_test] module_id: MOD-GOV_skill_feature_flags | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_feature_flags
# [INVARIANTS] _PREDEFINED_FLAGS is the global default; env overrides take precedence
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_feature_flags.py -q
# [TTL] task_bound

from __future__ import annotations

import os

from zephyr.autonomy_core.skills.skill_feature_flags import _PREDEFINED_FLAGS, SkillFeatureFlags


class TestSkillFeatureFlagsInstantiation:
    def test_class_exists(self):
        assert SkillFeatureFlags is not None

    def test_has_set_flag(self):
        assert callable(getattr(SkillFeatureFlags, "set_flag", None))

    def test_has_get_flag(self):
        assert callable(getattr(SkillFeatureFlags, "get_flag", None))

    def test_has_get_all_flags(self):
        assert callable(getattr(SkillFeatureFlags, "get_all_flags", None))

    def test_has_is_strict_mode(self):
        assert callable(getattr(SkillFeatureFlags, "is_strict_mode", None))


class TestSetAndGetFlag:
    def test_set_and_get_flag(self):
        SkillFeatureFlags.set_flag("SKILL-TEST-001", "strict_mode", False)
        result = SkillFeatureFlags.get_flag("SKILL-TEST-001", "strict_mode")
        assert result is False
        SkillFeatureFlags.reset_skill("SKILL-TEST-001")

    def test_get_default_flag(self):
        result = SkillFeatureFlags.get_flag("SKILL-NONEXIST", "strict_mode")
        assert result == _PREDEFINED_FLAGS["strict_mode"]

    def test_get_unknown_flag_defaults_false(self):
        result = SkillFeatureFlags.get_flag("SKILL-TEST", "totally_unknown_flag_xyz")
        assert result is False

    def test_set_flag_returns_dict(self):
        result = SkillFeatureFlags.set_flag("SKILL-TEST-002", "audit_enabled", True)
        assert result["skill_id"] == "SKILL-TEST-002"
        assert result["flag"] == "audit_enabled"
        assert result["value"] is True
        SkillFeatureFlags.reset_skill("SKILL-TEST-002")

    def test_set_multiple_flags_for_same_skill(self):
        SkillFeatureFlags.set_flag("SKILL-MULTI", "strict_mode", False)
        SkillFeatureFlags.set_flag("SKILL-MULTI", "audit_enabled", False)
        assert SkillFeatureFlags.get_flag("SKILL-MULTI", "strict_mode") is False
        assert SkillFeatureFlags.get_flag("SKILL-MULTI", "audit_enabled") is False
        SkillFeatureFlags.reset_skill("SKILL-MULTI")


class TestGetAllFlags:
    def test_returns_all_predefined_flags(self):
        SkillFeatureFlags.reset_skill("SKILL-ALL-TEST")
        result = SkillFeatureFlags.get_all_flags("SKILL-ALL-TEST")
        for key in _PREDEFINED_FLAGS:
            assert key in result

    def test_skill_overrides_applied(self):
        SkillFeatureFlags.set_flag("SKILL-OVERRIDE", "strict_mode", False)
        result = SkillFeatureFlags.get_all_flags("SKILL-OVERRIDE")
        assert result["strict_mode"] is False
        SkillFeatureFlags.reset_skill("SKILL-OVERRIDE")

    def test_no_skill_overrides_uses_defaults(self):
        SkillFeatureFlags.reset_skill("SKILL-DEFAULTS")
        result = SkillFeatureFlags.get_all_flags("SKILL-DEFAULTS")
        assert result["strict_mode"] == _PREDEFINED_FLAGS["strict_mode"]


class TestEnvOverride:
    def test_env_override_true(self):
        os.environ["ZEPHYR_SKILL_SKILL_ENV_TEST_STRICT_MODE"] = "true"
        result = SkillFeatureFlags.get_flag("SKILL-ENV-TEST", "strict_mode")
        assert result is True
        del os.environ["ZEPHYR_SKILL_SKILL_ENV_TEST_STRICT_MODE"]

    def test_env_override_false(self):
        os.environ["ZEPHYR_SKILL_SKILL_ENV_TEST_STRICT_MODE"] = "0"
        result = SkillFeatureFlags.get_flag("SKILL-ENV-TEST", "strict_mode")
        assert result is False
        del os.environ["ZEPHYR_SKILL_SKILL_ENV_TEST_STRICT_MODE"]

    def test_env_override_takes_precedence(self):
        SkillFeatureFlags.set_flag("SKILL-ENV-PRECEDE", "strict_mode", True)
        os.environ["ZEPHYR_SKILL_SKILL_ENV_PRECEDE_STRICT_MODE"] = "false"
        result = SkillFeatureFlags.get_flag("SKILL-ENV-PRECEDE", "strict_mode")
        assert result is False
        del os.environ["ZEPHYR_SKILL_SKILL_ENV_PRECEDE_STRICT_MODE"]
        SkillFeatureFlags.reset_skill("SKILL-ENV-PRECEDE")

    def test_no_env_uses_set_flag(self):
        os.environ.pop("ZEPHYR_SKILL_SKILL_NOENV_AUDIT_ENABLED", None)
        SkillFeatureFlags.set_flag("SKILL-NOENV", "audit_enabled", False)
        result = SkillFeatureFlags.get_flag("SKILL-NOENV", "audit_enabled")
        assert result is False
        SkillFeatureFlags.reset_skill("SKILL-NOENV")


class TestEnableDisableForAll:
    def test_enable_for_all(self):
        original = _PREDEFINED_FLAGS.get("sandbox_preview", False)
        SkillFeatureFlags.enable_for_all("sandbox_preview")
        assert _PREDEFINED_FLAGS["sandbox_preview"] is True
        _PREDEFINED_FLAGS["sandbox_preview"] = original

    def test_disable_for_all(self):
        original = _PREDEFINED_FLAGS.get("audit_enabled", True)
        SkillFeatureFlags.disable_for_all("audit_enabled")
        assert _PREDEFINED_FLAGS["audit_enabled"] is False
        _PREDEFINED_FLAGS["audit_enabled"] = original


class TestResetSkill:
    def test_reset_removes_skill_flags(self):
        SkillFeatureFlags.set_flag("SKILL-RESET", "strict_mode", False)
        assert SkillFeatureFlags.get_flag("SKILL-RESET", "strict_mode") is False
        SkillFeatureFlags.reset_skill("SKILL-RESET")
        result = SkillFeatureFlags.get_flag("SKILL-RESET", "strict_mode")
        assert result == _PREDEFINED_FLAGS["strict_mode"]

    def test_reset_nonexistent_skill_no_error(self):
        SkillFeatureFlags.reset_skill("SKILL-NONEXIST-RESET")


class TestIsStrictMode:
    def test_strict_mode_default(self):
        SkillFeatureFlags.reset_skill("SKILL-STRICT-DEFAULT")
        result = SkillFeatureFlags.is_strict_mode("SKILL-STRICT-DEFAULT")
        assert result == _PREDEFINED_FLAGS["strict_mode"]

    def test_strict_mode_overridden(self):
        SkillFeatureFlags.set_flag("SKILL-STRICT-OVR", "strict_mode", False)
        assert SkillFeatureFlags.is_strict_mode("SKILL-STRICT-OVR") is False
        SkillFeatureFlags.reset_skill("SKILL-STRICT-OVR")
