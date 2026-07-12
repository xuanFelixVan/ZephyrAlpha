# [A_test] module_id: SRC-TST-2053 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-670 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_post_process
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for post_process.py
"""

from zephyr.gov_enforcement.behavioral_admission.post_process import (
    HookResult,
    HookStrategy,
    PipelineResult,
    PostProcessPipeline,
    format_hook,
    lint_hook,
    typecheck_hook,
)


class TestHookResult:
    def test_success(self):
        result = HookResult("lint", True, "clean")
        assert result.hook_name == "lint"
        assert result.success is True
        assert result.output == "clean"

    def test_failure(self):
        result = HookResult("typecheck", False, "errors", error="type mismatch")
        assert result.success is False
        assert result.error == "type mismatch"


class TestPipelineResult:
    def test_all_passed(self):
        result = PipelineResult(hook_results=[], total_hooks=2, passed=2, failed=0)
        assert result.all_passed is True

    def test_not_all_passed(self):
        result = PipelineResult(hook_results=[], total_hooks=3, passed=2, failed=1)
        assert result.all_passed is False

    def test_empty(self):
        result = PipelineResult()
        assert result.total_hooks == 0
        assert not result.all_passed


class TestPostProcessPipeline:
    def test_build_and_run(self):
        runs: list[str] = []

        def mock_hook(**kwargs):
            runs.append(kwargs.get("file", ""))
            return HookResult("mock", True, "ok")

        pipeline = PostProcessPipeline()
        pipeline.register_hook("mock1", mock_hook)
        pipeline.register_hook("mock2", mock_hook)

        result = pipeline.run(file="test.py")
        assert result.total_hooks == 2
        assert result.passed == 2
        assert result.failed == 0
        assert len(runs) == 2

    def test_hook_failure_warn_strategy(self):
        def failing(**kwargs):
            return HookResult("bad", False, error="error")

        pipeline = PostProcessPipeline()
        pipeline.register_hook("bad", failing, strategy=HookStrategy.WARN)
        pipeline.register_hook("good", lambda **kw: HookResult("good", True, "ok"))

        result = pipeline.run()
        assert result.passed == 1
        assert result.failed == 1
        assert not result.aborted

    def test_hook_failure_abort_strategy(self):
        def failing(**kwargs):
            return HookResult("bad", False, error="fatal")

        pipeline = PostProcessPipeline()
        pipeline.register_hook("bad", failing, strategy=HookStrategy.ABORT)
        pipeline.register_hook("never", lambda **kw: HookResult("never", True, ""), strategy=HookStrategy.WARN)

        result = pipeline.run()
        assert result.failed == 1
        assert result.aborted is True

    def test_hook_failure_skip_strategy(self):
        def failing(**kwargs):
            return HookResult("skip_me", False, error="meh")

        called_after: list[str] = []
        pipeline = PostProcessPipeline()
        pipeline.register_hook("skip_me", failing, strategy=HookStrategy.SKIP)
        pipeline.register_hook("after", lambda **kw: called_after.append("yes") or HookResult("after", True, ""))

        result = pipeline.run()
        assert result.passed == 1
        assert result.failed == 1
        assert not result.aborted
        assert "yes" in called_after

    def test_create_default(self):
        pipeline = PostProcessPipeline.create_default()
        assert len(pipeline._hooks) == 3
        names = [h.name for h in pipeline._hooks]
        assert "lint" in names
        assert "format" in names
        assert "typecheck" in names

    def test_run_with_auto_fix(self):
        def sometimes_fails(**kwargs):
            call_count = getattr(sometimes_fails, "count", 0)
            sometimes_fails.count = call_count + 1
            if call_count == 0:
                return HookResult("flaky", False, error="first fail")
            return HookResult("flaky", True, "fixed")

        sometimes_fails.count = 0

        def fixer(**kwargs):
            return HookResult("fixer", True, "applied fix")

        pipeline = PostProcessPipeline()
        pipeline.register_hook("flaky", sometimes_fails, strategy=HookStrategy.WARN, auto_fix_fn=fixer)

        result = pipeline.run_with_auto_fix()
        assert result.passed == 1
        assert result.failed == 0

    def test_lint_hook_no_files(self):
        result = lint_hook()
        assert result.success is True

    def test_format_hook_no_files(self):
        result = format_hook()
        assert result.success is True

    def test_typecheck_hook_no_files(self):
        result = typecheck_hook()
        assert result.success is True
