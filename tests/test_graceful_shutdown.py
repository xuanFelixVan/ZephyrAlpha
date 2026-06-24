# [A_test] module_id: SRC-TST-1077 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_graceful_shutdown
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_graceful_shutdown.py

import pytest

mod = pytest.importorskip("zephyr.ops.capacity_assurance.graceful_shutdown", reason="graceful_shutdown not available")
GracefulShutdown = mod.GracefulShutdown


class TestGracefulShutdown:
    def test_instantiation(self):
        gs = GracefulShutdown()
        assert gs.is_shutting_down is False
        assert gs.signal_file is None

    def test_instantiation_with_signal_file(self):
        gs = GracefulShutdown(signal_file="/tmp/test_signal")
        assert gs.signal_file == "/tmp/test_signal"

    def test_register_handler(self):
        gs = GracefulShutdown()
        results = []
        gs.register_handler(lambda: results.append(1))
        gs.run_handlers()
        assert results == [1]

    def test_run_handlers_exception_safe(self):
        gs = GracefulShutdown()
        results = []
        gs.register_handler(lambda: 1 / 0)
        gs.register_handler(lambda: results.append(2))
        gs.run_handlers()
        assert results == [2]

    def test_snapshot_window_constant(self):
        assert GracefulShutdown.SNAPSHOT_WINDOW_MS == 1750

    def test_take_snapshot(self):
        gs = GracefulShutdown()
        snapshot = gs.take_snapshot()
        assert "timestamp" in snapshot
        assert "shutdown_graceful" in snapshot
        assert snapshot["shutdown_graceful"] is True
