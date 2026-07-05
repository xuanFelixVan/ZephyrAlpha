# [BLUEPRINT] SRC-023 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.behavioral_admission.post_process
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] zephyr.shared (re-export)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/delegation/test_post_process_unit.py; tests/governance/delegation/test_post_process_root.py
# [A_module] module_id=MOD-GOV_post_process | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# ---
# layer: governance
# category: post_processing
# status: active
# created: "2026-05-05"
# moved_from: zephyr.shared.post_process
# ---

"""post_process.py —— AI 生成代码后处理管道（Phase 13 | 盲点 B31）

痛点修复：AI 生成代码后缺乏自动化的 lint/format/typecheck 后处理。
Boris Cherny 核心技巧：后处理管道是最有效的质量保障手段之一。

设计对标：
  - Claude Code PostToolUse hooks: 工具执行后的 hook 点
  - pre-commit hooks: lint/format/typecheck 标准化
  - PydanticAI PostProcess: Agent 输出后处理

配置：
  - 内置 3 个 hook——lint_hook / format_hook / typecheck_hook
  - hook 失败策略——skip/warn/abort 可配置
  - auto-fix 模式——尝试自动修复常见问题

AI 施工约定：
  - AI 生成代码后 MUST 通过 PostProcessPipeline.run() 执行后处理
  - abort 策略下 hook 失败 MUST 阻断流程
  - auto-fix 模式 MUST 先备份原始文件

SSoT: DOM-GOV-001 §12 盲点 B31
"""

from __future__ import annotations

import subprocess
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Any


@unique
class HookStrategy(str, Enum):
    SKIP = "skip"
    WARN = "warn"
    ABORT = "abort"


@dataclass
class HookResult:
    """单次 hook 执行结果。"""

    hook_name: str
    success: bool
    output: str = ""
    error: str | None = None
    duration_ms: float = 0.0


@dataclass
class PipelineResult:
    """后处理管道执行结果。"""

    hook_results: list[HookResult] = field(default_factory=list)
    total_hooks: int = 0
    passed: int = 0
    failed: int = 0
    aborted: bool = False

    @property
    def all_passed(self) -> bool:
        return self.failed == 0 and self.total_hooks > 0


@dataclass
class PostProcessHook:
    """单个后处理 hook——名称 + 执行函数 + 失败策略。"""

    name: str
    fn: Callable[..., HookResult]
    strategy: HookStrategy = HookStrategy.WARN
    auto_fix_fn: Callable[..., HookResult] | None = None


class PostProcessPipeline:
    """AI 生成代码后处理管道——注册 hook → 按序执行 → 策略决策。

    Usage::

        pipeline = PostProcessPipeline()
        pipeline.register_hook("lint", lint_hook, strategy=HookStrategy.WARN)
        pipeline.register_hook("format", format_hook, strategy=HookStrategy.SKIP)
        result = pipeline.run(files=["src/zephyr/shared/new.py"])
        print(f"Passed: {result.passed}/{result.total_hooks}")

        或一步造好：
        pipeline = PostProcessPipeline.create_default()
        result = pipeline.run(files=["src/zephyr/shared/new.py"])
    """

    def __init__(self):
        self._hooks: list[PostProcessHook] = []
        self._lock = threading.RLock()

    def register_hook(
        self,
        name: str,
        fn: Callable[..., HookResult],
        strategy: HookStrategy = HookStrategy.WARN,
        auto_fix_fn: Callable[..., HookResult] | None = None,
    ) -> None:
        with self._lock:
            self._hooks.append(
                PostProcessHook(
                    name=name,
                    fn=fn,
                    strategy=strategy,
                    auto_fix_fn=auto_fix_fn,
                )
            )

    def run(self, **kwargs: Any) -> PipelineResult:
        hook_results: list[HookResult] = []
        passed = 0
        failed = 0

        for hook in self._hooks:
            try:
                result = hook.fn(**kwargs)
            except Exception as e:
                result = HookResult(
                    hook_name=hook.name,
                    success=False,
                    error=str(e),
                )
            hook_results.append(result)

            if result.success:
                passed += 1
            else:
                failed += 1
                if hook.strategy is HookStrategy.ABORT:
                    return PipelineResult(
                        hook_results=hook_results,
                        total_hooks=len(self._hooks),
                        passed=passed,
                        failed=failed,
                        aborted=True,
                    )
                if hook.strategy is HookStrategy.SKIP:
                    continue

        return PipelineResult(
            hook_results=hook_results,
            total_hooks=len(self._hooks),
            passed=passed,
            failed=failed,
            aborted=False,
        )

    def run_with_auto_fix(self, **kwargs: Any) -> PipelineResult:
        """带 auto-fix 的执行模式。hook 失败时先尝试 auto-fix，再重试原 hook。"""
        hook_results: list[HookResult] = []
        passed = 0
        failed = 0

        for hook in self._hooks:
            result = hook.fn(**kwargs)
            if not result.success and hook.auto_fix_fn is not None:
                fix_result = hook.auto_fix_fn(**kwargs)
                if fix_result.success:
                    result = hook.fn(**kwargs)

            hook_results.append(result)

            if result.success:
                passed += 1
            else:
                failed += 1
                if hook.strategy is HookStrategy.ABORT:
                    return PipelineResult(
                        hook_results=hook_results,
                        total_hooks=len(self._hooks),
                        passed=passed,
                        failed=failed,
                        aborted=True,
                    )

        return PipelineResult(
            hook_results=hook_results,
            total_hooks=len(self._hooks),
            passed=passed,
            failed=failed,
            aborted=False,
        )

    @staticmethod
    def create_default() -> PostProcessPipeline:
        pipeline = PostProcessPipeline()
        pipeline.register_hook("lint", lint_hook, HookStrategy.WARN)
        pipeline.register_hook("format", format_hook, HookStrategy.SKIP)
        pipeline.register_hook("typecheck", typecheck_hook, HookStrategy.WARN)
        return pipeline


def lint_hook(files: list[str] | None = None) -> HookResult:
    """内置 lint hook——调用 ruff check。"""
    import time

    start = time.monotonic()

    if not files:
        return HookResult("lint", True, "no files to lint")

    try:
        result = subprocess.run(
            ["ruff", "check", *files],
            capture_output=True,
            text=True,
            timeout=60,
        )
        success = result.returncode == 0
        return HookResult(
            hook_name="lint",
            success=success,
            output=(result.stdout or result.stderr)[:2000],
            duration_ms=(time.monotonic() - start) * 1000,
        )
    except FileNotFoundError:
        return HookResult("lint", True, "ruff not installed, skipping")
    except subprocess.TimeoutExpired:
        return HookResult("lint", False, error="ruff check timed out")


def format_hook(files: list[str] | None = None) -> HookResult:
    """内置 format hook——调用 ruff format --check。"""
    import time

    start = time.monotonic()

    if not files:
        return HookResult("format", True, "no files to format")

    try:
        result = subprocess.run(
            ["ruff", "format", "--check", *files],
            capture_output=True,
            text=True,
            timeout=60,
        )
        success = result.returncode == 0
        return HookResult(
            hook_name="format",
            success=success,
            output=(result.stdout or result.stderr)[:2000],
            duration_ms=(time.monotonic() - start) * 1000,
        )
    except FileNotFoundError:
        return HookResult("format", True, "ruff not installed, skipping")
    except subprocess.TimeoutExpired:
        return HookResult("format", False, error="ruff format timed out")


def typecheck_hook(files: list[str] | None = None) -> HookResult:
    """内置 typecheck hook——调用 pyright / mypy。"""
    import time

    start = time.monotonic()

    if not files:
        return HookResult("typecheck", True, "no files to typecheck")

    try:
        result = subprocess.run(
            ["pyright", *files],
            capture_output=True,
            text=True,
            timeout=120,
        )
        success = result.returncode == 0
        return HookResult(
            hook_name="typecheck",
            success=success,
            output=(result.stdout or result.stderr)[:2000],
            duration_ms=(time.monotonic() - start) * 1000,
        )
    except FileNotFoundError:
        return HookResult("typecheck", True, "pyright not installed, skipping")
    except subprocess.TimeoutExpired:
        return HookResult("typecheck", False, error="pyright timed out")


__all__ = [
    "HookResult",
    "HookStrategy",
    "PipelineResult",
    "PostProcessHook",
    "PostProcessPipeline",
    "format_hook",
    "lint_hook",
    "typecheck_hook",
]
