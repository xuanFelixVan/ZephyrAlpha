# [A_test] module_id: SRC-TST-1680 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_startup_guard
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_startup_guard.py

import pytest

mod = pytest.importorskip("zephyr.ops.capacity_assurance.startup_guard", reason="startup_guard not available")
StartupGuard = mod.StartupGuard


class TestStartupGuard:
    def test_instantiation(self):
        sg = StartupGuard()
        assert sg._boot_success is True
        assert len(sg._loaded) == 0

    def test_is_grace_period(self):
        sg = StartupGuard()
        assert sg.is_grace_period() is True

    def test_register_load(self):
        sg = StartupGuard()
        sg.register_load("module_a")
        sg.register_load("module_b")
        assert "module_a" in sg._loaded
        assert "module_b" in sg._loaded

    def test_load_order_ok_matching(self):
        sg = StartupGuard()
        sg.register_load("module_a")
        sg.register_load("module_b")
        assert sg.load_order_ok(["module_a", "module_b"]) is True

    def test_load_order_ok_mismatch(self):
        sg = StartupGuard()
        sg.register_load("module_a")
        assert sg.load_order_ok(["module_a", "module_b"]) is False

    def test_get_boot_status(self):
        sg = StartupGuard()
        sg.register_load("mod_1")
        status = sg.get_boot_status()
        assert "grace_period_active" in status
        assert "boot_elapsed_seconds" in status
        assert status["modules_loaded"] == 1
        assert status["boot_slo_target"] == 0.95

    def test_constants(self):
        assert StartupGuard.GRACE_PERIOD == 30.0
        assert StartupGuard.BOOT_SLO_TARGET == 0.95
