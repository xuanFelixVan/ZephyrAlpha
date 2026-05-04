"""
PipelineOrchestrator — M1-M11 管线协调器
=========================================
依据：MOD-INF-006 §3.1.3 + §3.1.1 dispatch() + GOV-AI-002 v2.0.0 决策树

双管线架构：
  A区 M1-M5 → 生产（代码生成/校验/打包）
  B区 M6-M11 → 审计（审查/合规/风险评估/门禁）

三层模型策略（GOV-AI-002 §一）：
  DeepSeek V4 Pro → 主力生产（M1-M4 + M6/M8/M9/M10/M11）—— 1.74/3.48/M
  GLM-5.1        → 深度审查（M7 + M5）—— Trae CN免费
  Claude Opus 4.7 → 特种救援（DeepSeek失败3次 / GLM驳回2次 / Owner关键标记 / security标签 / experimental标签）

使用：
    from zephyr.core.models import TaskCard
    from zephyr.pipeline import PipelineOrchestrator, PipelineOrchestratorConfig

    config = PipelineOrchestratorConfig(max_retries=3, claude_rescue_threshold=3)
    orchestrator = PipelineOrchestrator(config)
    result = orchestrator.dispatch(task_card)
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Optional

from zephyr.core.models import TaskCard
from zephyr.pipeline.models import (
    M_MODULES,
    M_MODULE_SPECS,
    ClaudeRescueTrigger,
    ModuleResult,
    ModuleStatus,
    PipelineOrchestratorConfig,
    PipelineResult,
    PipelineStatus,
)

__all__ = ["PipelineOrchestrator"]


class PipelineOrchestrator:
    """M1-M11 双管线模型路由 + 模块编排

    Parameters
    ----------
    config : PipelineOrchestratorConfig
        编排器配置（重试次数 / Claude 触发阈值 / 超时等）
    """

    def __init__(
        self,
        config: Optional[PipelineOrchestratorConfig] = None,
    ) -> None:
        self._cfg = config or PipelineOrchestratorConfig()
        self._failure_log: dict[str, int] = {}
        self._glm_reject_log: dict[str, int] = {}

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def dispatch(self, task_card: TaskCard) -> PipelineResult:
        """接收 TaskCard → 执行管线

        流程：
          ① 模型路由（GOV-AI-002 决策树）
          ② 管线分发（A区 vs B区）
          ③ 逐模块执行
          ④ Claude 救援判定（如触发则调用特种救援）
        """
        pipeline = task_card.assigned_pipeline
        if pipeline not in ("A", "B"):
            return PipelineResult(
                task_id=task_card.task_id,
                pipeline=pipeline,
                overall_status=PipelineStatus.FAILURE,
                modules_executed=[],
                finished_at=datetime.now().isoformat(),
            )

        modules = [m for m in M_MODULES if M_MODULE_SPECS[m]["pipeline"] == pipeline]
        route = self._route_model(task_card)

        results: list[ModuleResult] = []

        for mod_id in modules:
            spec = M_MODULE_SPECS[mod_id]
            assigned_model = spec["model"]

            if pipeline == "B" and route == "claude":
                assigned_model = "claude"
            elif spec.get("pipeline") == task_card.assigned_pipeline:
                pass
            else:
                assigned_model = spec["model"]

            mr = self._execute_module(mod_id, pipeline, assigned_model, task_card)
            results.append(mr)

        rescue = self._check_claude_rescue(task_card, results)

        status = self._determine_status(results)
        if rescue.triggered:
            status = PipelineStatus.CLAUDE_RESCUE

        passed = sum(1 for r in results if r.status == ModuleStatus.SUCCESS)
        partial = passed > 0 and passed < len(results)
        if status == PipelineStatus.SUCCESS and partial:
            status = PipelineStatus.PARTIAL_FAILURE

        return PipelineResult(
            task_id=task_card.task_id,
            pipeline=pipeline,
            modules_executed=results,
            overall_status=status,
            needs_claude_rescue=rescue.triggered,
            rescue_reason=rescue.reason,
            finished_at=datetime.now().isoformat(),
        )

    # ------------------------------------------------------------------
    # 模型路由 — GOV-AI-002 §二 决策树
    # ------------------------------------------------------------------

    def _route_model(self, task_card: TaskCard) -> str:
        model = task_card.execution_model

        if task_card.assigned_pipeline == "C":
            return "none"

        critical_keywords = ["关键", "critical", "rescue"]
        if any(kw in task_card.title.lower() for kw in critical_keywords):
            return "claude"

        if "security" in task_card.tags:
            return "claude"
        if "experimental" in task_card.tags:
            return "claude"

        if task_card.ai_autonomy_level == "unsafe":
            return "claude"

        return deepcopy(model)

    # ------------------------------------------------------------------
    # 单模块执行
    # ------------------------------------------------------------------

    def _execute_module(
        self,
        module_id: str,
        pipeline: str,
        model: str,
        task: TaskCard,
    ) -> ModuleResult:
        started = datetime.now().isoformat()
        last_error: Optional[str] = None

        for attempt in range(1, self._cfg.max_retries + 1):
            try:
                output = self._call_model(module_id, pipeline, model, task)
                return ModuleResult(
                    module_id=module_id,
                    pipeline=pipeline,
                    model=model,
                    status=ModuleStatus.SUCCESS,
                    output=output,
                    tokens_used=output.get("tokens_used", 0),
                    duration_ms=0,
                    started_at=started,
                    finished_at=datetime.now().isoformat(),
                )
            except Exception as exc:
                last_error = f"[{attempt}/{self._cfg.max_retries}] {type(exc).__name__}: {exc}"

        self._failure_log[module_id] = self._failure_log.get(module_id, 0) + 1
        self._failure_log["_task_" + task.task_id] = (
            self._failure_log.get("_task_" + task.task_id, 0) + 1
        )

        return ModuleResult(
            module_id=module_id,
            pipeline=pipeline,
            model=model,
            status=ModuleStatus.FAILURE,
            errors=[last_error] if last_error else ["unknown failure"],
            started_at=started,
            finished_at=datetime.now().isoformat(),
        )

    # ------------------------------------------------------------------
    # Claude 特种救援 — GOV-AI-002 §三
    # ------------------------------------------------------------------

    def _check_claude_rescue(
        self,
        task: TaskCard,
        results: list[ModuleResult],
    ) -> ClaudeRescueTrigger:
        trigger = ClaudeRescueTrigger()

        if "experimental" in task.tags:
            trigger.is_experimental = True
        if "security" in task.tags:
            trigger.has_security_tag = True
        if task.ai_autonomy_level == "unsafe":
            trigger.is_owner_critical = True

        deepseek_fail = sum(
            1
            for r in results
            if r.model == "deepseek" and r.status == ModuleStatus.FAILURE
        )
        glm_reject = sum(
            1
            for r in results
            if r.model == "glm" and r.status == ModuleStatus.FAILURE
        )
        trigger.deepseek_failure_count = deepseek_fail
        trigger.glm_rejection_count = glm_reject

        reasons: list[str] = []

        if deepseek_fail >= self._cfg.claude_rescue_threshold:
            reasons.append(f"DeepSeek failed {deepseek_fail} times (threshold={self._cfg.claude_rescue_threshold})")

        if glm_reject >= self._cfg.glm_rejection_threshold:
            reasons.append(f"GLM rejected {glm_reject} times (threshold={self._cfg.glm_rejection_threshold})")

        if trigger.is_owner_critical:
            reasons.append("Owner marked as critical/unsafe")

        if trigger.has_security_tag:
            reasons.append("Security tag detected")

        if trigger.is_experimental:
            reasons.append("Experimental tag detected")

        if reasons:
            trigger.triggered = True
            trigger.reason = "; ".join(reasons)

        return trigger

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _call_model(
        module_id: str,
        pipeline: str,
        model: str,
        task: TaskCard,
    ) -> dict:
        """调用 AI 模型执行模块

        当前为模拟实现——返回结构化占位结果。
        实际 AI 调用由 context_engine → model_routing_policy 驱动，
        属于 Phase 3+ 集成工作。
        """
        return {
            "module_id": module_id,
            "pipeline": pipeline,
            "model": model,
            "task_id": task.task_id,
            "simulated": True,
            "tokens_used": task.estimated_tokens // len(M_MODULES),
            "summary": f"[{pipeline}区] {model} → {module_id}: {task.title[:60]}",
        }

    @staticmethod
    def _determine_status(results: list[ModuleResult]) -> PipelineStatus:
        total = len(results)
        if total == 0:
            return PipelineStatus.FAILURE
        ok = sum(1 for r in results if r.status == ModuleStatus.SUCCESS)
        if ok == total:
            return PipelineStatus.SUCCESS
        if ok == 0:
            return PipelineStatus.FAILURE
        return PipelineStatus.PARTIAL_FAILURE
