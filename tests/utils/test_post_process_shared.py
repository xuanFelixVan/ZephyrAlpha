# [A_test] module_id: SRC-TST-1954 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-571 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_post_process
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/post_process.py
=============================================
覆盖矩阵：
  HookStrategy：
    - 枚举值完整性 × 1
  HookResult / PipelineResult：
    - 构造 × 2
    - PipelineResult.all_passed × 3
  PostProcessHook：
    - 构造 × 1
    - auto_fix_fn 可选 × 1
  PostProcessPipeline：
    - register_hook × 1
    - run 正常流程（全部通过）× 1
    - run WARN 策略失败不退 × 1
    - run ABORT 策略失败阻断 × 1
    - run SKIP 策略失败不阻断 × 1
    - run 异常不阻断 × 1
    - run_with_auto_fix × 1
    - create_default 包含 3 个 hook × 1
  lint_hook / format_hook / typecheck_hook：
    - 无文件时跳过 × 3
    - ruff 不可用时跳过 × 3

Safety: HIGH（后处理管道是代码质量的最后防线）
"""

from zephyr.gov_enforcement.behavioral_admission.post_process import (
    HookResult,
    HookStrategy,
    PipelineResult,
    PostProcessHook,
    PostProcessPipeline,
    format_hook,
    lint_hook,
    typecheck_hook,
)


class TestHookStrategy:
    def test_all_strategies(self):
        values = {s.value for s in HookStrategy}
        assert "skip" in values
        assert "warn" in values
        assert "abort" in values


class TestHookResult:
    def test_construction(self):
        r = HookResult(hook_name="lint", success=True, output="All clean", duration_ms=123.4)
        assert r.hook_name == "lint"
        assert r.success is True
        assert r.output == "All clean"
        assert r.duration_ms == 123.4
        assert r.error is None

    def test_with_error(self):
        r = HookResult(hook_name="typecheck", success=False, error="pyright not found")
        assert r.success is False
        assert r.error == "pyright not found"


class TestPipelineResult:
    def test_construction(self):
        r = PipelineResult(
            hook_results=[HookResult("lint", True, "ok")],
            total_hooks=3,
            passed=1,
            failed=0,
            aborted=False,
        )
        assert r.total_hooks == 3
        assert r.passed == 1
        assert r.failed == 0

    def test_all_passed_true(self):
        r = PipelineResult(
            hook_results=[HookResult("lint", True, "ok")],
            total_hooks=1,
            passed=1,
            failed=0,
        )
        assert r.all_passed is True

    def test_all_passed_false_with_failures(self):
        r = PipelineResult(total_hooks=1, passed=0, failed=1)
        assert r.all_passed is False

    def test_all_passed_false_empty(self):
        r = PipelineResult()
        assert r.all_passed is False


class TestPostProcessHook:
    def test_construction(self):
        def my_hook(**kwargs):
            return HookResult("my_hook", True, "done")

        hook = PostProcessHook(name="my_hook", fn=my_hook, strategy=HookStrategy.WARN)
        assert hook.name == "my_hook"
        assert hook.strategy == HookStrategy.WARN
        assert hook.auto_fix_fn is None

    def test_with_auto_fix(self):
        def my_hook(**kwargs):
            return HookResult("h", False, "fail")

        def auto_fix(**kwargs):
            return HookResult("fix", True, "fixed")

        hook = PostProcessHook(
            name="h",
            fn=my_hook,
            strategy=HookStrategy.WARN,
            auto_fix_fn=auto_fix,
        )
        assert hook.auto_fix_fn is auto_fix


class TestPostProcessPipeline:
    @staticmethod
    def _passing_hook(**kwargs):
        return HookResult("pass", True, "ok")

    @staticmethod
    def _failing_hook(**kwargs):
        return HookResult("fail", False, "bad", error="failure")

    @staticmethod
    def _throwing_hook(**kwargs):
        raise RuntimeError("boom")

    def test_register_hook(self):
        pipeline = PostProcessPipeline()
        pipeline.register_hook("lint", self._passing_hook)
        assert len(pipeline._hooks) == 1

    def test_run_all_pass(self):
        pipeline = PostProcessPipeline()
        pipeline.register_hook("h1", self._passing_hook)
        pipeline.register_hook("h2", self._passing_hook)
        result = pipeline.run()
        assert result.passed == 2
        assert result.failed == 0
        assert result.aborted is False

    def test_run_warn_strategy_continues(self):
        pipeline = PostProcessPipeline()
        pipeline.register_hook("h1", self._passing_hook, HookStrategy.WARN)
        pipeline.register_hook("h2", self._failing_hook, HookStrategy.WARN)
        pipeline.register_hook("h3", self._passing_hook, HookStrategy.WARN)
        result = pipeline.run()
        assert result.passed == 2
        assert result.failed == 1
        assert result.aborted is False

    def test_run_abort_stops(self):
        pipeline = PostProcessPipeline()
        pipeline.register_hook("h1", self._passing_hook, HookStrategy.WARN)
        pipeline.register_hook("h2", self._failing_hook, HookStrategy.ABORT)
        pipeline.register_hook("h3", self._passing_hook, HookStrategy.WARN)
        result = pipeline.run()
        assert result.aborted is True
        assert result.failed >= 1

    def test_run_skip_continues(self):
        pipeline = PostProcessPipeline()
        pipeline.register_hook("h1", self._passing_hook, HookStrategy.WARN)
        pipeline.register_hook("h2", self._failing_hook, HookStrategy.SKIP)
        pipeline.register_hook("h3", self._passing_hook, HookStrategy.WARN)
        result = pipeline.run()
        assert result.aborted is False
        assert result.failed >= 1
        assert result.passed == 2

    def test_run_handles_exceptions(self):
        pipeline = PostProcessPipeline()
        pipeline.register_hook("err", self._throwing_hook, HookStrategy.WARN)
        pipeline.register_hook("ok", self._passing_hook, HookStrategy.WARN)
        result = pipeline.run()
        assert result.failed >= 1
        assert result.passed == 1

    def test_run_with_auto_fix(self):
        fixing = {"attempts": 0}

        def flaky_hook(**kwargs):
            fixing["attempts"] += 1
            if fixing["attempts"] == 1:
                return HookResult("flaky", False, "first fail")
            return HookResult("flaky", True, "second pass")

        def auto_fix(**kwargs):
            return HookResult("fix", True, "fixed")

        pipeline = PostProcessPipeline()
        pipeline.register_hook(
            "flaky",
            flaky_hook,
            HookStrategy.WARN,
            auto_fix_fn=auto_fix,
        )
        result = pipeline.run_with_auto_fix()
        assert result.passed == 1

    def test_create_default(self):
        pipeline = PostProcessPipeline.create_default()
        assert len(pipeline._hooks) == 3
        names = [h.name for h in pipeline._hooks]
        assert "lint" in names
        assert "format" in names
        assert "typecheck" in names


class TestBuiltinHooks:
    def test_lint_hook_no_files(self):
        result = lint_hook(files=None)
        assert result.success is True

    def test_lint_hook_empty_files(self):
        result = lint_hook(files=[])
        assert result.success is True

    def test_format_hook_no_files(self):
        result = format_hook(files=None)
        assert result.success is True

    def test_format_hook_empty_files(self):
        result = format_hook(files=[])
        assert result.success is True

    def test_typecheck_hook_no_files(self):
        result = typecheck_hook(files=None)
        assert result.success is True

    def test_typecheck_hook_empty_files(self):
        result = typecheck_hook(files=[])
        assert result.success is True
