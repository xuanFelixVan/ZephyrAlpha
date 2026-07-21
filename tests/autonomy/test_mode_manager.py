# [A_test] module_id: MOD-GOV_mode_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_mode_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_mode_manager.py -q
# [TTL] task_bound
from zephyr.autonomy_core.context.mode_manager import CEMode, ModeManager


class TestCEMode:
    def test_vibe_value(self):
        assert CEMode.VIBE.value == "vibe"

    def test_strict_value(self):
        assert CEMode.STRICT.value == "strict"

    def test_learning_value(self):
        assert CEMode.LEARNING.value == "learning"

    def test_production_value(self):
        assert CEMode.PRODUCTION.value == "production"

    def test_all_modes_count(self):
        assert len(CEMode) == 4


class TestModeManagerInstantiation:
    def test_default_mode_is_vibe(self):
        mgr = ModeManager()
        assert mgr.current_mode == CEMode.VIBE

    def test_explicit_mode_constructor(self):
        mgr = ModeManager(mode=CEMode.STRICT)
        assert mgr.current_mode == CEMode.STRICT

    def test_constructor_with_learning(self):
        mgr = ModeManager(mode=CEMode.LEARNING)
        assert mgr.current_mode == CEMode.LEARNING

    def test_constructor_with_production(self):
        mgr = ModeManager(mode=CEMode.PRODUCTION)
        assert mgr.current_mode == CEMode.PRODUCTION


class TestModeManagerTransition:
    def test_transition_vibe_to_strict(self):
        mgr = ModeManager(mode=CEMode.VIBE)
        result = mgr.transition(CEMode.STRICT)
        assert result is True
        assert mgr.current_mode == CEMode.STRICT

    def test_transition_strict_to_learning(self):
        mgr = ModeManager(mode=CEMode.STRICT)
        result = mgr.transition(CEMode.LEARNING)
        assert result is True
        assert mgr.current_mode == CEMode.LEARNING

    def test_transition_to_same_mode(self):
        mgr = ModeManager(mode=CEMode.VIBE)
        result = mgr.transition(CEMode.VIBE)
        assert result is True
        assert mgr.current_mode == CEMode.VIBE

    def test_transition_returns_bool(self):
        mgr = ModeManager()
        result = mgr.transition(CEMode.PRODUCTION)
        assert isinstance(result, bool)

    def test_sequential_transitions(self):
        mgr = ModeManager(mode=CEMode.VIBE)
        mgr.transition(CEMode.STRICT)
        mgr.transition(CEMode.LEARNING)
        mgr.transition(CEMode.PRODUCTION)
        assert mgr.current_mode == CEMode.PRODUCTION

    def test_transition_all_modes(self):
        mgr = ModeManager()
        for mode in CEMode:
            mgr.transition(mode)
            assert mgr.current_mode == mode
