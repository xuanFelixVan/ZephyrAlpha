# [A_test] module_id: MOD-GOV_finalizer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_finalizer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tests never raise; all assertions within pytest
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.trading.finalizer import Finalizer


class TestFinalizerInit:
    def test_init_empty(self) -> None:
        f = Finalizer()
        assert f.cleanup_fns == []


class TestRegister:
    def test_register_single(self) -> None:
        f = Finalizer()
        f.register("db", lambda: None)
        assert len(f.cleanup_fns) == 1
        assert f.cleanup_fns[0][0] == "db"

    def test_register_multiple(self) -> None:
        f = Finalizer()
        f.register("db", lambda: None)
        f.register("cache", lambda: None)
        f.register("logs", lambda: None)
        assert len(f.cleanup_fns) == 3


class TestRun:
    def test_run_no_cleanup_fns(self) -> None:
        f = Finalizer()
        result = f.run()
        assert result == {}

    def test_run_successful_cleanup(self) -> None:
        f = Finalizer()
        called = []
        f.register("resource_a", lambda: called.append("a"))
        f.register("resource_b", lambda: called.append("b"))
        result = f.run()
        assert result == {"resource_a": True, "resource_b": True}
        assert called == ["a", "b"]

    def test_run_exception_marks_false(self) -> None:
        f = Finalizer()

        def failing():
            raise RuntimeError("cleanup failed")

        f.register("good", lambda: None)
        f.register("bad", failing)
        result = f.run()
        assert result["good"] is True
        assert result["bad"] is False

    def test_run_continues_after_exception(self) -> None:
        f = Finalizer()
        order = []

        def fail_first():
            order.append("fail")
            raise ValueError("boom")

        def succeed_second():
            order.append("ok")

        f.register("first", fail_first)
        f.register("second", succeed_second)
        result = f.run()
        assert result["first"] is False
        assert result["second"] is True
        assert order == ["fail", "ok"]

    def test_run_idempotent_multiple_calls(self) -> None:
        f = Finalizer()
        counter = {"val": 0}
        f.register("counter", lambda: counter.update(val=counter["val"] + 1))
        f.run()
        f.run()
        assert counter["val"] == 2

    def test_run_empty_resource_type(self) -> None:
        f = Finalizer()
        f.register("", lambda: None)
        result = f.run()
        assert "" in result
        assert result[""] is True
