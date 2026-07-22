# [A_test] module_id: MOD-GOV_resilience_fallback | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_resilience_fallback

# [INVARIANTS] FallbackChain至少一步;全部失败抛FallbackExhaustedError;策略链按序执行

# [MODIFY-GUARD] fallback.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] FallbackExhaustedError

# [TESTS] pytest tests/test_resilience_fallback.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.resilience.fallback import (
    FallbackChain,
    FallbackExhaustedError,
    FallbackStep,
    fallback,
)


class TestFallbackStep:
    def test_creation(self):
        step = FallbackStep(name="primary", func=lambda: 42, description="main", is_primary=True)
        assert step.name == "primary"
        assert step.is_primary is True

    def test_frozen(self):
        step = FallbackStep(name="s", func=lambda: 1)
        with pytest.raises(AttributeError):
            step.name = "changed"


class TestFallbackChain:
    def test_empty_steps_raises(self):
        with pytest.raises(ValueError, match="at least one step"):
            FallbackChain("test", [])

    def test_primary_succeeds(self):
        chain = FallbackChain(
            "test",
            [
                FallbackStep("primary", lambda: "ok", is_primary=True),
            ],
        )
        result = chain.execute()
        assert result == "ok"

    def test_falls_back_to_second(self):
        chain = FallbackChain(
            "test",
            [
                FallbackStep("fail", lambda: (_ for _ in ()).throw(ValueError("fail")), is_primary=True),
                FallbackStep("backup", lambda: "backup_ok"),
            ],
        )
        result = chain.execute()
        assert result == "backup_ok"

    def test_all_fail_raises(self):
        def raise_val():
            raise ValueError("fail")

        chain = FallbackChain(
            "test",
            [
                FallbackStep("a", raise_val),
                FallbackStep("b", raise_val),
            ],
        )
        with pytest.raises(FallbackExhaustedError) as exc_info:
            chain.execute()
        assert "exhausted" in str(exc_info.value).lower()
        assert exc_info.value.details["step_count"] == 2

    def test_chain_name(self):
        chain = FallbackChain("my_chain", [FallbackStep("s", lambda: 1)])
        assert chain.chain_name == "my_chain"

    def test_step_count(self):
        chain = FallbackChain(
            "test",
            [
                FallbackStep("a", lambda: 1),
                FallbackStep("b", lambda: 2),
            ],
        )
        assert chain.step_count == 2

    def test_three_step_chain(self):
        call_log = []

        def fail_a():
            call_log.append("a")
            raise RuntimeError("a failed")

        def fail_b():
            call_log.append("b")
            raise RuntimeError("b failed")

        def succeed_c():
            call_log.append("c")
            return "c_ok"

        chain = FallbackChain(
            "test",
            [
                FallbackStep("a", fail_a, is_primary=True),
                FallbackStep("b", fail_b),
                FallbackStep("c", succeed_c),
            ],
        )
        result = chain.execute()
        assert result == "c_ok"
        assert call_log == ["a", "b", "c"]


class TestFallbackChainAsync:
    @pytest.mark.asyncio
    async def test_async_primary_succeeds(self):
        async def primary():
            return "async_ok"

        chain = FallbackChain(
            "test",
            [
                FallbackStep("primary", primary, is_primary=True),
            ],
        )
        result = await chain.execute_async()
        assert result == "async_ok"

    @pytest.mark.asyncio
    async def test_async_fallback(self):
        async def fail():
            raise ValueError("async fail")

        async def backup():
            return "async_backup"

        chain = FallbackChain(
            "test",
            [
                FallbackStep("fail", fail, is_primary=True),
                FallbackStep("backup", backup),
            ],
        )
        result = await chain.execute_async()
        assert result == "async_backup"

    @pytest.mark.asyncio
    async def test_async_all_fail(self):
        async def fail():
            raise ValueError("async fail")

        chain = FallbackChain(
            "test",
            [
                FallbackStep("a", fail),
                FallbackStep("b", fail),
            ],
        )
        with pytest.raises(FallbackExhaustedError):
            await chain.execute_async()


class TestFallbackDecorator:
    def test_basic_usage(self):
        def primary():
            return 1

        def backup():
            return 2

        fn = fallback(primary, backup, chain_name="test_chain")
        assert fn() == 1

    def test_no_functions_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            fallback()

    def test_fallback_activates(self):
        def fail():
            raise RuntimeError("nope")

        def succeed():
            return "recovered"

        fn = fallback(fail, succeed)
        assert fn() == "recovered"


class TestFallbackExhaustedError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = FallbackExhaustedError("exhausted", details={"step_count": 3})
        assert isinstance(err, ZephyrBaseError)
