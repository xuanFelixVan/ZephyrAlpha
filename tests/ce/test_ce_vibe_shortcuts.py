# [A_test] module_id: MOD-GOV_ce_vibe_shortcuts | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_ce_vibe_shortcuts
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_ce_vibe_shortcuts.py
# [TTL] task_bound

import pytest

from zephyr.autonomy_core.context.ce_vibe_shortcuts import (
    _MODE_CONFIGS,
    CEMode,
    ModeConfig,
    ce_strict,
    ce_vibe,
)


class TestCEMode:
    def test_vibe_value(self):
        assert CEMode.VIBE.value == "vibe"

    def test_strict_value(self):
        assert CEMode.STRICT.value == "strict"

    def test_member_count(self):
        assert len(CEMode) == 2


class TestModeConfig:
    def test_instantiation(self):
        config = ModeConfig(mode=CEMode.VIBE, top_k=5, similarity_threshold=0.7)
        assert config.mode == CEMode.VIBE
        assert config.top_k == 5
        assert config.similarity_threshold == 0.7

    def test_missing_field_raises(self):
        with pytest.raises(TypeError):
            ModeConfig()


class TestModeConfigs:
    def test_both_modes_configured(self):
        assert CEMode.VIBE in _MODE_CONFIGS
        assert CEMode.STRICT in _MODE_CONFIGS

    def test_vibe_has_higher_top_k(self):
        assert _MODE_CONFIGS[CEMode.VIBE].top_k > _MODE_CONFIGS[CEMode.STRICT].top_k

    def test_vibe_has_lower_threshold(self):
        assert _MODE_CONFIGS[CEMode.VIBE].similarity_threshold < _MODE_CONFIGS[CEMode.STRICT].similarity_threshold


class TestCeVibe:
    def test_returns_vibe_config(self):
        config = ce_vibe()
        assert config.mode == CEMode.VIBE
        assert config.top_k == 8
        assert config.similarity_threshold == 0.6

    def test_returns_modeconfig_instance(self):
        config = ce_vibe()
        assert isinstance(config, ModeConfig)


class TestCeStrict:
    def test_returns_strict_config(self):
        config = ce_strict()
        assert config.mode == CEMode.STRICT
        assert config.top_k == 3
        assert config.similarity_threshold == 0.8

    def test_returns_modeconfig_instance(self):
        config = ce_strict()
        assert isinstance(config, ModeConfig)
