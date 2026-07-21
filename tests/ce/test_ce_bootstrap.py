# [A_test] module_id: MOD-GOV_ce_bootstrap | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_ce_bootstrap
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_ce_bootstrap.py
# [TTL] task_bound

import pytest

from zephyr.autonomy_core.context.ce_bootstrap import (
    BootstrapGate,
    CEBootstrap,
    CEBootstrapLevel,
    ce_bootstrap_default,
)


class TestCEBootstrapLevel:
    def test_all_levels_exist(self):
        assert CEBootstrapLevel.CE_MVP.value == "ce_mvp"
        assert CEBootstrapLevel.FUNCTIONAL.value == "functional"
        assert CEBootstrapLevel.FULL_CE.value == "full_ce"

    def test_member_count(self):
        assert len(CEBootstrapLevel) == 3


class TestBootstrapGate:
    def test_instantiation_defaults(self):
        gate = BootstrapGate(level=CEBootstrapLevel.CE_MVP)
        assert gate.level == CEBootstrapLevel.CE_MVP
        assert gate.required_ke_count == 0
        assert gate.required_test_pass_rate == 0.9
        assert gate.passed is False
        assert gate.graduation_log == []

    def test_instantiation_custom(self):
        gate = BootstrapGate(
            level=CEBootstrapLevel.FUNCTIONAL,
            required_ke_count=50,
            required_test_pass_rate=0.95,
            passed=True,
            graduation_log=["step1", "step2"],
        )
        assert gate.required_ke_count == 50
        assert gate.required_test_pass_rate == 0.95
        assert gate.passed is True
        assert len(gate.graduation_log) == 2

    def test_missing_level_raises(self):
        with pytest.raises(TypeError):
            BootstrapGate()


class TestCEBootstrap:
    def test_instantiation(self):
        cb = CEBootstrap()
        assert cb is not None

    def test_current_level_starts_at_mvp(self):
        cb = CEBootstrap()
        assert cb.current_level == CEBootstrapLevel.CE_MVP

    def test_graduate_returns_gate(self):
        cb = CEBootstrap()
        gate = cb.graduate(CEBootstrapLevel.FUNCTIONAL)
        assert isinstance(gate, BootstrapGate)
        assert gate.level == CEBootstrapLevel.FUNCTIONAL

    def test_graduate_to_full_ce(self):
        cb = CEBootstrap()
        gate = cb.graduate(CEBootstrapLevel.FULL_CE)
        assert gate.level == CEBootstrapLevel.FULL_CE

    def test_graduate_to_mvp(self):
        cb = CEBootstrap()
        gate = cb.graduate(CEBootstrapLevel.CE_MVP)
        assert gate.level == CEBootstrapLevel.CE_MVP


class TestCeBootstrapDefault:
    def test_default_instance_exists(self):
        assert ce_bootstrap_default is not None
        assert isinstance(ce_bootstrap_default, CEBootstrap)

    def test_default_current_level(self):
        assert ce_bootstrap_default.current_level == CEBootstrapLevel.CE_MVP
