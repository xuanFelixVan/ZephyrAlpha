# [A_test] module_id: SRC-TST-1392 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-417 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_post_process
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_enforcement.behavioral_admission.post_process import (
    HookResult,
    HookStrategy,
    PipelineResult,
    PostProcessPipeline,
    format_hook,
    lint_hook,
    typecheck_hook,
)


class TestHookStrategy:
    def test_enum_values(self):
        assert HookStrategy.SKIP == "skip"
        assert HookStrategy.WARN == "warn"
        assert HookStrategy.ABORT == "abort"

    def test_enum_members_count(self):
        assert len(HookStrategy) == 3


class TestHookResult:
    def test_default_values(self):
        result = HookResult(hook_name="test", success=True)
        assert result.hook_name == "test"
        assert result.success is True
        assert result.output == ""
        assert result.error is None
        assert result.duration_ms == 0.0

    def test_with_error(self):
        result = HookResult(hook_name="test", success=False, error="something failed")
        assert result.success is False
        assert result.error == "something failed"


class TestPipelineResult:
    def test_all_passed_true(self):
        result = PipelineResult(total_hooks=3, passed=3, failed=0)
        assert result.all_passed is True

    def test_all_passed_false_with_failures(self):
        result = PipelineResult(total_hooks=3, passed=2, failed=1)
        assert result.all_passed is False

    def test_all_passed_false_with_zero_hooks(self):
        result = PipelineResult(total_hooks=0, passed=0, failed=0)
        assert result.all_passed is False


class TestPostProcessPipeline:
    def test_register_and_run_hook(self):
        pipeline = PostProcessPipeline()
        pipeline.register_hook(
            "test_hook",
            fn=lambda **kw: HookResult(hook_name="test_hook", success=True),
        )
        result = pipeline.run()
        assert result.all_passed is True
        assert result.total_hooks == 1

    def test_run_with_failing_hook_warn(self):
        pipeline = PostProcessPipeline()
        pipeline.register_hook(
            "fail_hook",
            fn=lambda **kw: HookResult(hook_name="fail_hook", success=False),
            strategy=HookStrategy.WARN,
        )
        result = pipeline.run()
        assert result.failed == 1
        assert result.aborted is False

    def test_run_with_failing_hook_abort(self):
        pipeline = PostProcessPipeline()
        pipeline.register_hook(
            "abort_hook",
            fn=lambda **kw: HookResult(hook_name="abort_hook", success=False),
            strategy=HookStrategy.ABORT,
        )
        pipeline.register_hook(
            "never_runs",
            fn=lambda **kw: HookResult(hook_name="never_runs", success=True),
        )
        result = pipeline.run()
        assert result.aborted is True
        assert result.failed == 1

    def test_run_with_exception_in_hook(self):
        pipeline = PostProcessPipeline()

        def bad_hook(**kw):
            raise RuntimeError("boom")

        pipeline.register_hook("bad", fn=bad_hook, strategy=HookStrategy.WARN)
        result = pipeline.run()
        assert result.failed == 1

    def test_run_with_auto_fix(self):
        call_count = {"n": 0}

        def failing_hook(**kw):
            call_count["n"] += 1
            return HookResult(hook_name="fixable", success=call_count["n"] > 1)

        def fix_fn(**kw):
            return HookResult(hook_name="fix", success=True)

        pipeline = PostProcessPipeline()
        pipeline.register_hook("fixable", fn=failing_hook, auto_fix_fn=fix_fn)
        result = pipeline.run_with_auto_fix()
        assert result.passed == 1

    def test_empty_pipeline(self):
        pipeline = PostProcessPipeline()
        result = pipeline.run()
        assert result.total_hooks == 0
        assert result.all_passed is False

    def test_create_default(self):
        pipeline = PostProcessPipeline.create_default()
        assert len(pipeline._hooks) == 3


class TestLintHook:
    def test_no_files(self):
        result = lint_hook(files=None)
        assert result.success is True

    def test_empty_files(self):
        result = lint_hook(files=[])
        assert result.success is True


class TestFormatHook:
    def test_no_files(self):
        result = format_hook(files=None)
        assert result.success is True


class TestTypecheckHook:
    def test_no_files(self):
        result = typecheck_hook(files=None)
        assert result.success is True
