# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.pipeline_orchestrator
# [DOMAIN] D-AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__; zephyr.shared.shared_services.infra_06.observer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_pipeline_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
PipelineOrchestrator — 多阶段流水线编排 (P3 beta)
===================================================
Task ID    : MOD-INF-008-TASK-010
Priority   : P3 (beta)
Depends    : MOD-INF-008-TASK-002~005 (四阶段流水线完成)

职责
----
编排 Build->Compress->Validate->Inject 四阶段流水线, 作为 CE 的统一入口.

已有测试 Ghost: tests/test_pipeline_orchestrator.py

SRC-0043: 版本分叉 -- 与 pipeline/pipeline_orchestrator.py 职责不同, 保留独立实现
  - 本模块负责 Context Injection 四阶段流水线 (Build->Compress->Validate->Inject)
  - pipeline/pipeline_orchestrator.py 负责 M1-M11 管线协调 (生产+审计双管线)
  - 两个模块的类型系统 (PipelineMetrics/PipelineResult vs PipelineStatus/ModuleResult)
    语义完全不同, 不需要共享类型导入
  - 如未来需要统一上下文注入与 M 管线编排, 应通过组合而非合并
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from zephyr.autonomy_core.context_assembler import RawContext, build_context
from zephyr.autonomy_core.context_budget_tracker import ContextBudgetTracker
from zephyr.autonomy_core.context_injector import (
    InjectionResult,
    ValidatedContext,
    inject,
)
from zephyr.autonomy_core.pattern_library import (
    DangerousPatternLibrary,
    validate_context,
)
from zephyr.shared.shared_services.infra_06.observer import Observer


@dataclass
class PipelineMetrics:
    """流水线各阶段耗时统计 (ms)。"""

    build_ms: float = 0.0
    compress_ms: float = 0.0
    validate_ms: float = 0.0
    inject_ms: float = 0.0
    total_ms: float = 0.0

    @property
    def as_dict(self) -> dict[str, float]:
        return {
            "build_ms": self.build_ms,
            "compress_ms": self.compress_ms,
            "validate_ms": self.validate_ms,
            "inject_ms": self.inject_ms,
            "total_ms": self.total_ms,
        }


@dataclass
class PipelineResult:
    """四阶段流水线运行结果。"""

    success: bool = False
    raw_context: RawContext | None = None
    injection_result: InjectionResult | None = None
    metrics: PipelineMetrics = field(default_factory=PipelineMetrics)
    degraded: bool = False
    degradation_reason: str = ""
    errors: list[str] = field(default_factory=list)


class PipelineOrchestrator:
    """多阶段流水线编排器。

    Using::

        orchestrator = PipelineOrchestrator(vms=vms_client)
        result = orchestrator.run(
            task_type="CODE_GEN",
            target_layer="L01",
            session_id="session-001",
        )
        if result.success:
            print(f"Injected {result.injection_result.token_count} tokens")
    """

    def __init__(
        self,
        *,
        vms: Any | None = None,
        budget_tracker: ContextBudgetTracker | None = None,
        pattern_library: DangerousPatternLibrary | None = None,
        session_limit: int = 8000,
        pipeline_timeout_s: float = 10.0,
    ) -> None:
        self._vms = vms
        self._budget_tracker = budget_tracker or ContextBudgetTracker(Observer())
        self._pattern_lib = pattern_library or DangerousPatternLibrary()
        self._session_limit = session_limit
        self._timeout_s = pipeline_timeout_s

    def run(
        self,
        *,
        task_type: str = "",
        target_layer: str = "",
        session_id: str = "",
        user_prompt: str = "",
        task: Any | None = None,
    ) -> PipelineResult:
        """运行完整四阶段流水线。

        Returns
        -------
        PipelineResult
        """
        metrics = PipelineMetrics()
        errors: list[str] = []
        pipeline_start = time.monotonic()

        phase_start = time.monotonic()
        raw_ctx = build_context(
            task=task,
            task_type=task_type,
            target_layer=target_layer,
            session_id=session_id,
            vms=self._vms,
        )
        metrics.build_ms = (time.monotonic() - phase_start) * 1000

        if raw_ctx.degraded:
            degraded_vc = ValidatedContext(
                system_rules=raw_ctx.embedded_defaults,
                is_clean=True,
            )
            inj_result = inject(degraded_vc, session_limit=self._session_limit)
            metrics.total_ms = (time.monotonic() - pipeline_start) * 1000
            return PipelineResult(
                success=inj_result.injected_successfully,
                raw_context=raw_ctx,
                injection_result=inj_result,
                metrics=metrics,
                degraded=True,
                degradation_reason="VMS unavailable — using embedded defaults",
            )

        combined_text = "\n\n".join(
            raw_ctx.ke_entries + raw_ctx.vibe_rules + raw_ctx.blueprints + raw_ctx.failure_patterns
        )

        phase_start = time.monotonic()
        clean_text, pattern_matches = validate_context(combined_text, library=self._pattern_lib)
        metrics.validate_ms = (time.monotonic() - phase_start) * 1000

        has_error_matches = any(m.pattern.severity == "error" for m in pattern_matches)

        vc = ValidatedContext(
            system_rules=raw_ctx.embedded_defaults or _SYSTEM_RULES,
            contracts=raw_ctx.vibe_rules + raw_ctx.blueprints,
            ke_entries=raw_ctx.ke_entries + raw_ctx.failure_patterns,
            examples=[],
            is_clean=not has_error_matches,
            validation_warnings=[m.pattern.name for m in pattern_matches],
        )

        phase_start = time.monotonic()
        elapsed_so_far = time.monotonic() - pipeline_start
        remaining_timeout = max(0.1, self._timeout_s - elapsed_so_far)
        inj_result = inject(
            vc,
            session_limit=self._session_limit,
            lsg_passed=not has_error_matches,
            timeout_s=remaining_timeout,
        )
        metrics.inject_ms = (time.monotonic() - phase_start) * 1000

        metrics.total_ms = (time.monotonic() - pipeline_start) * 1000

        return PipelineResult(
            success=inj_result.injected_successfully,
            raw_context=raw_ctx,
            injection_result=inj_result,
            metrics=metrics,
            degraded=raw_ctx.degraded or has_error_matches,
            degradation_reason="CE pipeline degraded" if raw_ctx.degraded or has_error_matches else "",
            errors=errors,
        )


_SYSTEM_RULES: list[str] = [
    "R-ONLY-CREATE: Never delete files",
    "R-NO-ASK: Never ask questions",
    "R-UTF8: Always use encoding='utf-8'",
    "R-ATOMIC: Related changes in same commit",
    "R-AUDIT: Post-task audit mandatory",
]
