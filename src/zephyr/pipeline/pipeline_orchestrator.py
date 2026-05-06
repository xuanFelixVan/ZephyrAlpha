"""
PipelineOrchestrator — M1-M11 管线协调器
=========================================
依据：MOD-INF-006 §3.1.3 + §3.1.1 dispatch() + GOV-AI-002 v2.0.0 决策树
     + CT-PIPE-ORC-001（蓝图 MOD-MASTER-001 §2.7，见 ct_pipe_routing.py）

**真源边界（AUDIT-08，与 route_manifest task_dual_pipeline 一致）**
  - **M1–M11 入口与模块切片**：``TaskCard``（含 ct_pipe 提示）+ ``ct_pipe_routing.resolve_ct_pipe_orc001``
    + 本协调器；**不以** ``config/blueprint_routing.yaml`` 解析 Mx 节点。
  - **blueprint_routing.yaml**：关键词 / 路径模式 → 蓝图文献与人类检索（含 ``blueprint_search`` MCP），
    属 **MOD-INF-009 路由表**，与 **CT-PIPE** 编排正交。

**模拟边界**：在默认实现中，非 dry_run 的 ``_call_model`` 仍产出 ``simulated: True``
的占位结果（用于 token/成本估算与 LSG 净化链），**不调用外部 LLM API**，
亦不代表各 Mx 阶段已完成真实语义上的代码生成/审查。生产级多模型接入需在集成层替换该路径。

双管线架构：
  A区 M1-M5 → 生产（代码生成/校验/打包）
  B区 M6-M11 → 审计（审查/合规/风险评估/门禁）

三层模型策略（GOV-AI-002 §一）：
  DeepSeek V4 Pro → 主力生产（M1-M4 + M6/M8/M9/M10/M11）—— 1.74/3.48/M
  GLM-5.1        → 深度审查（M7 + M5）—— Trae CN免费
  Claude Opus 4.7 → 特种救援（DeepSeek失败3次 / GLM驳回2次 / Owner关键标记 / security标签 / experimental标签）

v0.3.2 集成：PipelineOrchestrator ↔ TaskRepository 修桥
  - dispatch() 开始 → task_repo.transition(PENDING→IN_PROGRESS)
  - dispatch() 成功 → task_repo.transition(IN_PROGRESS→COMPLETED)
  - dispatch() 失败 → task_repo.transition(IN_PROGRESS→FAILED)
  - task_repo 可选——为 None 时跳过状态流转（向后兼容测试场景）

使用：
    from zephyr.core.models import TaskCard
    from zephyr.pipeline import PipelineOrchestrator, PipelineOrchestratorConfig

    config = PipelineOrchestratorConfig(max_retries=3, claude_rescue_threshold=3)
    orchestrator = PipelineOrchestrator(config, task_repo=repo)
    result = orchestrator.dispatch(task_card)
"""

from __future__ import annotations

import hashlib
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any

from zephyr.core.models import TaskCard
from zephyr.pipeline.ct_pipe_routing import (
    PipelineRoutingInputsError,
    ct_pipe_hints_from_task_card,
    modules_slice_from_node,
    resolve_ct_pipe_orc001,
)
from zephyr.pipeline.models import (
    M_MODULE_SPECS,
    M_MODULES,
    ABExperimentRoute,
    AIImpactAssessment,
    CircuitBreakerState,
    ClaudeRescueTrigger,
    CostRecord,
    DeadLetterEntry,
    EmergencyFallbackPlan,
    ExperimentVariant,
    ModelCollapseAlert,
    ModelConfidence,
    ModelVersionInfo,
    ModuleResult,
    ModuleStatus,
    PipelineArtifact,
    PipelineArtifactManifest,
    PipelineLineageChain,
    PipelineLineageEntry,
    PipelineOrchestratorConfig,
    PipelineResult,
    PipelineStatus,
    PreemptionRecord,
    validate_module_output,
)
from zephyr.pipeline.pipeline_lock import LockResult, PipelineLock
from zephyr.pipeline.routing_plugins import PipelineRouter
from zephyr.shared.schemas import TaskStatus

if TYPE_CHECKING:
    from zephyr.db.task_repo import TaskRepository
    from zephyr.shared.events.event_schemas import TaskEventPayload

__all__ = ["PipelineOrchestrator"]


class PipelineOrchestrator:
    """M1-M11 双管线模型路由 + 模块编排

    Parameters
    ----------
    config : PipelineOrchestratorConfig
        编排器配置（重试次数 / Claude 触发阈值 / 超时等）
    task_repo : TaskRepository | None
        SQLite 任务仓库——为 None 时跳过状态流转（测试兼容模式）
    """

    def __init__(
        self,
        config: PipelineOrchestratorConfig | None = None,
        task_repo: TaskRepository | None = None,
        router: PipelineRouter | None = None,
        pipeline_lock: PipelineLock | None = None,
        agent_orchestrator: object | None = None,
    ) -> None:
        self._cfg = config or PipelineOrchestratorConfig()
        self._task_repo = task_repo
        self._router = router
        self._pipeline_lock = pipeline_lock
        self._agent_orchestrator = agent_orchestrator
        self._failure_log: dict[str, int] = {}
        self._glm_reject_log: dict[str, int] = {}
        self._preempt_log: dict[str, PreemptionRecord] = {}
        self._priority_cutoff: str = "P2"

        self._metrics: dict[str, int] = {}
        self._latency_samples: dict[str, list[float]] = {}
        self._observer: Any | None = None
        self._lifecycle_mgr: Any | None = None
        self._initialized: bool = False

        self._token_budget_total: int = 0
        self._token_budget_consumed: dict[str, int] = {}
        self._active_dispatches: set[str] = set()
        self._log_buffer: list[tuple[str, str, str]] = []

        self._dispatched_ids: set[str] = set()
        self._circuit_breaker_states: dict[str, CircuitBreakerState] = {}
        self._circuit_breaker_failures: dict[str, list[float]] = {}
        self._rate_limit_timestamps: dict[str, list[float]] = {}
        self._cost_total: float = 0.0
        self._cost_records: list[CostRecord] = []
        self._dead_letters: list[DeadLetterEntry] = []
        self._accuracy_data: dict[str, list[float]] = {}
        self._active_experiments: dict[str, ABExperimentRoute] = {}

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def dispatch(self, task_card: TaskCard, *, dry_run: bool = False) -> PipelineResult:
        """接收 TaskCard → 执行管线（含状态机集成）

        流程：
          ① CT-PIPE-ORC-001：若 TaskCard 激活路由提示 → 从入口 Mx 切片执行；否则整链
          ② 状态流转 PENDING→IN_PROGRESS（如 task_repo 注入）
          ③ 模型路由（GOV-AI-002 决策树）
          ④ 逐模块执行（含 LSG 安全闸门 + 数据血缘追踪）
          ⑤ Claude 救援判定
          ⑥ 模型崩塌检测（M3+M7+Claude 同质化预警）
          ⑦ 状态流转 IN_PROGRESS→COMPLETED/FAILED（如 task_repo 注入）

        Parameters
        ----------
        dry_run : bool
            True 时只模拟路由和校验，不实际调用 AI 模型。
        """
        ct_warnings: list[str] = []
        ct_decision = None
        hints = ct_pipe_hints_from_task_card(task_card)

        _dispatch_start = datetime.now()

        self._active_dispatches.add(task_card.task_id)
        self._log("INFO", f"dispatch[{task_card.task_id}] started pipeline={task_card.assigned_pipeline} dry_run={dry_run}")

        if task_card.task_id in self._dispatched_ids:
            self._active_dispatches.discard(task_card.task_id)
            self._log("WARN", f"dispatch[{task_card.task_id}] idempotency guard: already dispatched, rejecting duplicate")
            return PipelineResult(
                task_id=task_card.task_id,
                pipeline=task_card.assigned_pipeline,
                overall_status=PipelineStatus.FAILURE,
                modules_executed=[],
                finished_at=datetime.now().isoformat(),
                is_dry_run=dry_run,
                ct_pipe_warnings=["IDEMPOTENCY: duplicate dispatch rejected——同一TaskCard已执行过"],
            )
        self._dispatched_ids.add(task_card.task_id)

        impact = self._assess_impact(task_card)
        if impact.human_review_required:
            ct_warnings.append(
                f"IMPACT: risk_tier={impact.risk_tier} autonomy={impact.autonomy_level} "
                f"——NIST AI RMF MAP函数要求人工复核"
            )

        experiment_route = self._resolve_experiment(task_card)
        if experiment_route is not None:
            ct_warnings.append(
                f"AB-EXPERIMENT: experiment={experiment_route.experiment_id} "
                f"variant={experiment_route.variant.value}"
            )

        if hints is None:
            pipeline = task_card.assigned_pipeline
            if pipeline not in ("A", "B"):
                self._active_dispatches.discard(task_card.task_id)
                return PipelineResult(
                    task_id=task_card.task_id,
                    pipeline=pipeline,
                    overall_status=PipelineStatus.FAILURE,
                    modules_executed=[],
                    finished_at=datetime.now().isoformat(),
                    is_dry_run=dry_run,
                )
            modules = [m for m in M_MODULES if M_MODULE_SPECS[m]["pipeline"] == pipeline]
        else:
            try:
                ct_decision = self._resolve_ct_pipe(hints)
                pipeline, modules = modules_slice_from_node(ct_decision.node_id)
            except PipelineRoutingInputsError as exc:
                self._active_dispatches.discard(task_card.task_id)
                return PipelineResult(
                    task_id=task_card.task_id,
                    pipeline=task_card.assigned_pipeline,
                    overall_status=PipelineStatus.FAILURE,
                    modules_executed=[],
                    finished_at=datetime.now().isoformat(),
                    is_dry_run=dry_run,
                    ct_pipe_route=None,
                    ct_pipe_warnings=[str(exc)],
                )
            if task_card.assigned_pipeline not in ("A", "B"):
                ct_warnings.append(
                    f"assigned_pipeline={task_card.assigned_pipeline!r} 非 A/B；"
                    f"CT-PIPE 已强制使用 {pipeline} 区自 {ct_decision.node_id}"
                )
            elif task_card.assigned_pipeline != pipeline:
                ct_warnings.append(
                    f"CT-PIPE 区段 {pipeline} 与 assigned_pipeline={task_card.assigned_pipeline} 不一致——以 CT-PIPE 为准"
                )

        tw = self._transition(task_card.task_id, TaskStatus.IN_PROGRESS)
        if tw:
            ct_warnings.append(tw)

        lineage_chain = PipelineLineageChain(run_id=task_card.task_id)

        try:
            route = self._route_model(task_card)

            task_type = (
                getattr(task_card, "pipeline_task_type", None)
                or (hints.task_type if hints else None)
                or task_card.assigned_pipeline
                or "unknown"
            ).lower()
            node_id = ct_decision.node_id if ct_decision and ct_decision.node_id else modules[0]
            self._record_telemetry_decision(task_type, node_id)

            sod_warnings = self._check_separation_of_duties(task_card)
            ct_warnings.extend(sod_warnings)

            token_budget_ok, budget_warning = self._check_token_budget(task_card)
            if not token_budget_ok:
                ct_warnings.append(budget_warning)

            preemptions = self._preempt_check(task_card)
            for pr in preemptions:
                ct_warnings.append(
                    f"PREEMPT: {pr.preempted_task_id} (P={pr.preempted_priority}) "
                    f"suspended by {task_card.task_id} (P={task_card.priority})"
                )

            lock_result = self._acquire_pipeline_lock(task_card, hints)
            if lock_result is not None and not lock_result.acquired:
                self._active_dispatches.discard(task_card.task_id)
                return PipelineResult(
                    task_id=task_card.task_id,
                    pipeline=task_card.assigned_pipeline,
                    overall_status=PipelineStatus.LOCKED,
                    modules_executed=[],
                    finished_at=datetime.now().isoformat(),
                    is_dry_run=dry_run,
                    ct_pipe_route=ct_decision,
                    ct_pipe_warnings=ct_warnings
                    + [f"LOCK: files={lock_result.locked_files} conflict_with={lock_result.conflict_tasks}"],
                )

            results: list[ModuleResult] = []
            manifest = PipelineArtifactManifest(run_id=task_card.task_id)
            prev_module: str | None = None
            executed_module_ids: list[str] = []

            for mod_id in modules:
                if prev_module is not None:
                    zone_warnings = self._validate_zone_crossing(task_card, prev_module, mod_id)
                    for zw in zone_warnings:
                        if "VIOLATION" in zw:
                            raise ValueError(zw)
                        ct_warnings.append(zw)

                spec = M_MODULE_SPECS[mod_id]
                assigned_model = spec["model"]

                if pipeline == "B" and route == "claude":
                    assigned_model = "claude"
                elif spec.get("pipeline") == pipeline:
                    pass
                else:
                    assigned_model = spec["model"]

                prior_artifacts = [a for a in manifest.artifacts if a.produced_by != mod_id]

                mr = self._execute_module(
                    mod_id,
                    pipeline,
                    assigned_model,
                    task_card,
                    token_divisor=len(modules),
                    prior_artifacts=prior_artifacts,
                    dry_run=dry_run,
                )
                results.append(mr)

                consumed_keys = [a.artifact_key for a in prior_artifacts if a.produced_by != mod_id]
                produced_keys: list[str] = []
                for art_dict in mr.output.get("artifacts", []):
                    try:
                        artifact = PipelineArtifact(**art_dict)
                        manifest.artifacts.append(artifact)
                        produced_keys.append(artifact.artifact_key)
                    except Exception:
                        pass

                if mr.output.get("artifact_key") and mr.output.get("artifact_type"):
                    try:
                        artifact = PipelineArtifact(
                            artifact_key=mr.output["artifact_key"],
                            produced_by=mod_id,
                            artifact_type=mr.output["artifact_type"],
                            file_paths=mr.output.get("file_paths", []),
                            summary=str(mr.output.get("summary", ""))[:200],
                        )
                        manifest.artifacts.append(artifact)
                        produced_keys.append(artifact.artifact_key)
                    except Exception:
                        pass

                lineage_entry = PipelineLineageEntry(
                    module_id=mod_id,
                    pipeline=pipeline,
                    upstream_module_ids=[m for m in executed_module_ids if m != mod_id],
                    consumed_artifact_keys=consumed_keys,
                    produced_artifact_keys=produced_keys,
                    started_at=mr.started_at or "",
                    finished_at=mr.finished_at or "",
                )
                lineage_chain.add_entry(lineage_entry)
                executed_module_ids.append(mod_id)

                prev_module = mod_id

            rescue = self._check_claude_rescue(task_card, results)

            collapse_alert = self._verify_model_diversity(results, task_card)

            status = self._determine_status(results)
            if rescue.triggered:
                status = PipelineStatus.CLAUDE_RESCUE

            passed = sum(1 for r in results if r.status == ModuleStatus.SUCCESS)
            partial = passed > 0 and passed < len(results)
            if status == PipelineStatus.SUCCESS and partial:
                status = PipelineStatus.PARTIAL_FAILURE

            total_tokens = sum(r.tokens_used for r in results if r.tokens_used > 0)
            if total_tokens > 0:
                self._token_budget_consumed[task_card.task_id] = total_tokens
            uw = self._update_runtime_metrics(task_card.task_id, total_tokens)
            if uw:
                ct_warnings.append(uw)

            if status in (PipelineStatus.SUCCESS, PipelineStatus.PARTIAL_FAILURE):
                tw = self._transition(task_card.task_id, TaskStatus.COMPLETED)
            else:
                tw = self._transition(task_card.task_id, TaskStatus.FAILED)
            if tw:
                ct_warnings.append(tw)

            self._release_pipeline_lock(task_card.task_id)

            _latency_ms = (datetime.now() - _dispatch_start).total_seconds() * 1000
            self._record_telemetry_latency(task_type, _latency_ms)

            cost_records = self._compute_module_costs(results)

            emergency_fallback = self._emergency_fallback(results, task_card)
            dead_letter = self._maybe_dead_letter(task_card, results, status)
            cb_state = self._circuit_breaker_states.get(task_card.task_id)

            bridge_result = None
            if self._agent_orchestrator is not None:
                try:
                    from zephyr.pipeline.pipeline_agent_bridge import PipelineAgentBridge

                    bridge = PipelineAgentBridge(self._agent_orchestrator)
                    bridge_result = bridge.bridge(
                        PipelineResult(
                            task_id=task_card.task_id,
                            pipeline=pipeline,
                            modules_executed=results,
                            overall_status=status,
                        ),
                        token_budget=total_tokens if total_tokens > 0 else None,
                    )
                except Exception:
                    self._log("WARN", f"dispatch[{task_card.task_id}] bridge failed")

            return PipelineResult(
                task_id=task_card.task_id,
                pipeline=pipeline,
                modules_executed=results,
                overall_status=status,
                needs_claude_rescue=rescue.triggered,
                rescue_reason=rescue.reason,
                finished_at=datetime.now().isoformat(),
                is_dry_run=dry_run,
                ct_pipe_route=ct_decision,
                ct_pipe_warnings=ct_warnings,
                artifact_manifest=manifest,
                lineage=lineage_chain if lineage_chain.entries else None,
                model_collapse=collapse_alert if collapse_alert.detected else None,
                pipeline_version="0.9.0",
                cost_total_usd=sum(c.cost_usd for c in cost_records),
                cost_records=cost_records,
                impact_assessment=impact,
                fallback_plan=emergency_fallback if emergency_fallback.activated else None,
                dead_letter=dead_letter,
                circuit_breaker_state=cb_state,
                bridge_result=bridge_result,
            )
        except Exception:
            self._log("ERROR", f"dispatch[{task_card.task_id}] failed with exception")
            self._release_pipeline_lock(task_card.task_id)
            self._active_dispatches.discard(task_card.task_id)
            tw = self._transition(task_card.task_id, TaskStatus.FAILED)
            if tw:
                self._failure_log[f"dispatch_exc_{task_card.task_id}"] = (
                    self._failure_log.get(f"dispatch_exc_{task_card.task_id}", 0) + 1
                )
            raise
        finally:
            self._active_dispatches.discard(task_card.task_id)

    # ------------------------------------------------------------------
    # 状态机集成
    # ------------------------------------------------------------------

    def _transition(self, task_id: str, to_status: TaskStatus) -> str | None:
        """任务状态流转。失败返回 warning 字符串，成功返回 None。"""
        if self._task_repo is None:
            return None
        try:
            task = self._task_repo.get(task_id)
            if task is None:
                return f"_transition[{task_id}→{to_status.name}]: task not found in repo"
            if task.status == to_status:
                return None
            from_status = task.status.name if hasattr(task.status, "name") else str(task.status).split(".")[-1]
            self._task_repo.transition(task_id, to_status)
            self._emit_task_event(task_id, from_status, to_status.name)
            return None
        except Exception as exc:
            self._failure_log[f"transition_{task_id}"] = self._failure_log.get(f"transition_{task_id}", 0) + 1
            return f"_transition[{task_id}→{to_status.name}]: {type(exc).__name__}: {exc}"

    def _update_runtime_metrics(self, task_id: str, total_tokens: int) -> str | None:
        """更新运行时指标。失败返回 warning 字符串，成功返回 None。"""
        if self._task_repo is None or total_tokens <= 0:
            return None
        try:
            self._task_repo.update(task_id, actual_hours=0.0, tokens_consumed=total_tokens)
            return None
        except Exception as exc:
            self._failure_log["metrics_update"] = self._failure_log.get("metrics_update", 0) + 1
            return f"_update_runtime_metrics[{task_id}]: {type(exc).__name__}: {exc}"

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

        return model

    # ------------------------------------------------------------------
    # CT-PIPE 路由解析
    # ------------------------------------------------------------------

    def _resolve_ct_pipe(self, hints):
        if self._router is not None:
            return self._router.route(hints)
        return resolve_ct_pipe_orc001(hints)

    # ------------------------------------------------------------------
    # 优先级抢占——对标 K8s Priority Preemption
    # ------------------------------------------------------------------

    _PREEMPTIBLE_PRIORITIES = frozenset({"P3", "P2"})

    def _preempt_check(self, task_card: TaskCard) -> list[PreemptionRecord]:
        """检查是否需要抢占低优先级任务。

        P0/P1 可抢占仍为 IN_PROGRESS 的 P2/P3。被抢占任务迁移到 **WAITING**
        （ADR-0030 十态之一），waiting_for 记录抢占方 task_id；
        并允许后续重新 ``dispatch``（从内存幂等集合中摘除该 tid）。
        """
        if self._task_repo is None:
            return []

        pri_raw = getattr(task_card.priority, "value", task_card.priority)
        pri = str(pri_raw or "").upper().strip()
        if pri not in ("P0", "P1"):
            return []

        records: list[PreemptionRecord] = []
        try:
            preemptible = self._task_repo.list(
                status=TaskStatus.IN_PROGRESS,
                limit=50,
            )
        except (TypeError, AttributeError):
            return []

        for t in preemptible:
            tp_raw = getattr(getattr(t, "priority", None), "value", getattr(t, "priority", ""))
            tp = str(tp_raw or "").upper().strip()
            if tp in self._PREEMPTIBLE_PRIORITIES:
                try:
                    self._task_repo.transition(
                        t.task_id,
                        TaskStatus.WAITING,
                        waiting_for=f"pipeline_preempted:{task_card.task_id}",
                    )
                except Exception:
                    continue

                self._dispatched_ids.discard(t.task_id)
                self._active_dispatches.discard(t.task_id)

                record = PreemptionRecord(
                    preempted_task_id=t.task_id,
                    preempted_by_task_id=task_card.task_id,
                    preempted_priority=tp,
                )
                self._preempt_log[t.task_id] = record
                records.append(record)

        return records

    def resume_preempted(
        self,
        completed_task_id: str,
    ) -> list[PipelineResult]:
        """完成高优先级任务后，恢复被其抢占的低优先级任务并重新 dispatch。"""
        resumed: list[PipelineResult] = []
        if self._task_repo is None:
            return resumed

        for tid, record in list(self._preempt_log.items()):
            if record.preempted_by_task_id != completed_task_id:
                continue
            if record.resumed_at is not None:
                continue

            task = self._task_repo.get(tid)
            if task is None:
                continue
            try:
                if task.status == TaskStatus.WAITING:
                    self._task_repo.transition(tid, TaskStatus.READY)
                elif task.status == TaskStatus.READY:
                    pass
                else:
                    continue
                task = self._task_repo.get(tid)
            except Exception:
                continue
            if task is None:
                continue

            self._dispatched_ids.discard(tid)
            self._active_dispatches.discard(tid)

            try:
                result = self.dispatch(task)
            except Exception:
                raise
            record.resumed_at = datetime.now().isoformat()
            resumed.append(result)

        return resumed

    # ------------------------------------------------------------------
    # Pipeline 并发锁
    # ------------------------------------------------------------------

    def _acquire_pipeline_lock(self, task_card, hints) -> LockResult | None:
        """尝试获取 Pipeline 文件锁。

        从 TaskCard 的 ct_pipe.layer 提取 target_layer，
        锁定该层级的受影响文件。无 pipeline_lock 或无 layer
        时返回 None（跳过锁定）。
        """
        if self._pipeline_lock is None:
            return None

        layer = None
        if hints is not None:
            layer = getattr(hints, "target_layer", None)
        if not layer:
            layer = getattr(task_card, "target_layer", None)

        if not layer:
            return None

        layer_locks = [layer]
        file_paths: list[str] = []

        files_in_scope = getattr(task_card, "files_in_scope", []) or []
        allowed_touch = getattr(task_card, "allowed_touch", []) or []
        downstream = getattr(task_card, "downstream_outputs", []) or []

        for item in downstream:
            if isinstance(item, dict):
                path = item.get("path", "")
            else:
                path = str(item)
            if path:
                file_paths.append(path)

        for fp in files_in_scope:
            file_paths.append(fp)
        for fp in allowed_touch:
            file_paths.append(fp)

        if not file_paths:
            return None

        return self._pipeline_lock.acquire(
            task_card.task_id,
            file_paths,
            layer_locks=layer_locks,
            timeout_s=5.0,
        )

    # ------------------------------------------------------------------
    # 状态持久化
    # ------------------------------------------------------------------

    def save_state(self) -> dict:
        """导出当前 Pipeline 状态（供持久化）——B153 含配置。"""
        return {
            "config": self._cfg.model_dump(),
            "failure_log": dict(self._failure_log),
            "glm_reject_log": dict(self._glm_reject_log),
            "preempt_log": {k: v.model_dump() for k, v in self._preempt_log.items()},
            "priority_cutoff": self._priority_cutoff,
            "metrics": dict(self._metrics),
            "latency_samples": {k: v[:] for k, v in self._latency_samples.items()},
            "cost_total": self._cost_total,
            "cost_records": [c.model_dump() for c in self._cost_records[-100:]],
            "dead_letters": [d.model_dump() for d in self._dead_letters],
        }

    def load_state(self, state: dict) -> None:
        """从持久化字典恢复编排器状态——B153 含配置恢复。"""
        if "config" in state:
            self._cfg = PipelineOrchestratorConfig(**state["config"])
        self._failure_log = dict(state.get("failure_log", {}))
        self._glm_reject_log = dict(state.get("glm_reject_log", {}))
        self._priority_cutoff = state.get("priority_cutoff", "P2")
        preempt_raw = state.get("preempt_log", {})
        self._preempt_log = {tid: PreemptionRecord(**data) for tid, data in preempt_raw.items()}
        self._cost_total = float(state.get("cost_total", 0.0))
        self._cost_records = [CostRecord(**c) for c in state.get("cost_records", [])]
        self._dead_letters = [DeadLetterEntry(**d) for d in state.get("dead_letters", [])]

    def _release_pipeline_lock(self, task_id: str) -> None:
        if self._pipeline_lock is not None:
            self._pipeline_lock.release(task_id)

    # ------------------------------------------------------------------
    # 模型降级 Fallback 链 —— GOV-AI-002 §三 补充
    # ------------------------------------------------------------------

    _FALLBACK_CHAIN: dict[str, list[str]] = {
        "deepseek": ["glm", "claude"],
        "glm": ["deepseek", "claude"],
        "claude": [],
    }

    def _run_with_fallback(
        self,
        module_id: str,
        pipeline: str,
        primary_model: str,
        task: TaskCard,
        *,
        token_divisor: int,
        prior_artifacts: list | None = None,
        dry_run: bool = False,
    ) -> tuple[ModuleResult, str]:
        chain = [primary_model] + self._FALLBACK_CHAIN.get(primary_model, [])
        last_error: str | None = None

        for model in chain:
            try:
                output = self._call_model(
                    module_id,
                    pipeline,
                    model,
                    task,
                    token_divisor=token_divisor,
                    prior_artifacts=prior_artifacts,
                    dry_run=dry_run,
                )
                return (
                    ModuleResult(
                        module_id=module_id,
                        pipeline=pipeline,
                        model=model,
                        status=ModuleStatus.SUCCESS,
                        output=output,
                        tokens_used=output.get("tokens_used", 0),
                        duration_ms=0,
                        started_at=datetime.now().isoformat(),
                        finished_at=datetime.now().isoformat(),
                        fallback_from=primary_model if model != primary_model else None,
                    ),
                    model,
                )
            except Exception as exc:
                last_error = f"[{model}] {type(exc).__name__}: {exc}"
                if model in self._FALLBACK_CHAIN:
                    self._failure_log[f"fallback_{module_id}_{model}"] = (
                        self._failure_log.get(f"fallback_{module_id}_{model}", 0) + 1
                    )

        self._failure_log[module_id] = self._failure_log.get(module_id, 0) + 1
        return (
            ModuleResult(
                module_id=module_id,
                pipeline=pipeline,
                model=primary_model,
                status=ModuleStatus.FAILURE,
                errors=[last_error] if last_error else ["all fallback models failed"],
                started_at=datetime.now().isoformat(),
                finished_at=datetime.now().isoformat(),
                fallback_from=None,
            ),
            primary_model,
        )

    # ------------------------------------------------------------------
    # 多模型双盲审查 —— M3(DeepSeek) + M7(GLM) 并行→取交集
    # ------------------------------------------------------------------

    def _blind_review(
        self,
        task: TaskCard,
        pipeline: str,
        *,
        token_divisor: int,
        dry_run: bool = False,
    ) -> tuple[ModuleResult | None, ModuleResult | None, bool]:
        if dry_run:
            m3_mr = ModuleResult(
                module_id="M3",
                pipeline=pipeline,
                model="deepseek",
                status=ModuleStatus.SUCCESS,
                output={"summary": f"[DRY-RUN BLIND] M3: {task.title[:60]}"},
                started_at=datetime.now().isoformat(),
                finished_at=datetime.now().isoformat(),
                blind_review_role="generator",
            )
            m7_mr = ModuleResult(
                module_id="M7",
                pipeline=pipeline,
                model="glm",
                status=ModuleStatus.SUCCESS,
                output={"summary": f"[DRY-RUN BLIND] M7: {task.title[:60]}"},
                started_at=datetime.now().isoformat(),
                finished_at=datetime.now().isoformat(),
                blind_review_role="reviewer",
            )
            return m3_mr, m7_mr, True

        m3_result, m3_model = self._run_with_fallback(
            "M3",
            pipeline,
            "deepseek",
            task,
            token_divisor=max(token_divisor, 2),
            dry_run=dry_run,
        )
        m3_result.blind_review_role = "generator"

        m7_result, m7_model = self._run_with_fallback(
            "M7",
            pipeline,
            "glm",
            task,
            token_divisor=max(token_divisor, 2),
            dry_run=dry_run,
        )
        m7_result.blind_review_role = "reviewer"

        consensus = False
        if m3_result.status == ModuleStatus.SUCCESS and m7_result.status == ModuleStatus.SUCCESS:
            m3_verdict = m3_result.output.get("verdict", "ok")
            m7_verdict = m7_result.output.get("verdict", "ok")
            consensus = m3_verdict == m7_verdict

        return m3_result, m7_result, consensus

    def _execute_module(
        self,
        module_id: str,
        pipeline: str,
        model: str,
        task: TaskCard,
        *,
        token_divisor: int | None = None,
        prior_artifacts: list | None = None,
        dry_run: bool = False,
    ) -> ModuleResult:
        started = datetime.now().isoformat()
        last_error: str | None = None
        divisor = token_divisor if token_divisor and token_divisor > 0 else len(M_MODULES)

        cb_key = f"{task.task_id}:{module_id}:{model}"
        if self._cfg.circuit_breaker_enabled:
            cb_state = self._check_circuit_breaker(cb_key, model)
            if cb_state == CircuitBreakerState.OPEN:
                return ModuleResult(
                    module_id=module_id,
                    pipeline=pipeline,
                    model=model,
                    status=ModuleStatus.FAILURE,
                    errors=[f"CIRCUIT-OPEN: {model} 断路器已断开——短路跳过重试"],
                    started_at=started,
                    finished_at=datetime.now().isoformat(),
                )

        if not dry_run and self._cfg.rate_limit_per_model:
            rate_limited, wait_s = self._check_rate_limit(model)
            if rate_limited:
                time.sleep(wait_s)

        for attempt in range(1, self._cfg.max_retries + 1):
            try:
                output = self._call_model(
                    module_id, pipeline, model, task,
                    token_divisor=divisor,
                    prior_artifacts=prior_artifacts,
                    dry_run=dry_run,
                )
                output = validate_module_output(module_id, output)

                confidence = self._generate_confidence(model, output)

                cost_usd = output.get("cost_usd", 0.0)
                self._cost_total += cost_usd
                self._cost_records.append(CostRecord(
                    model=model,
                    tokens_input=output.get("tokens_used", 0),
                    cost_usd=cost_usd,
                ))

                if self._cfg.circuit_breaker_enabled:
                    self._circuit_breaker_failures.pop(cb_key, None)

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
                    confidence=confidence,
                )
            except Exception as exc:
                last_error = f"[{attempt}/{self._cfg.max_retries}] {type(exc).__name__}: {exc}"
                if self._cfg.circuit_breaker_enabled:
                    self._circuit_breaker_failures.setdefault(cb_key, []).append(time.time())
                if attempt < self._cfg.max_retries:
                    time.sleep(min(2 ** attempt, 30))

        self._failure_log[module_id] = self._failure_log.get(module_id, 0) + 1
        self._failure_log["_task_" + task.task_id] = self._failure_log.get("_task_" + task.task_id, 0) + 1

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

    def _check_claude_rescue(self, task_card: TaskCard, results: list[ModuleResult]) -> ClaudeRescueTrigger:
        """判断是否触发 Claude 救援。

        tags 检查与 _route_model() 共享规则集——新增 tag 需同步修改两处。
        """
        trigger = ClaudeRescueTrigger()

        if "experimental" in (task_card.tags or ()):
            trigger.is_experimental = True
        if "security" in (task_card.tags or ()):
            trigger.has_security_tag = True
        if task_card.ai_autonomy_level == "unsafe":
            trigger.is_owner_critical = True

        deepseek_fail = sum(1 for r in results if r.model == "deepseek" and r.status == ModuleStatus.FAILURE)
        glm_reject = sum(1 for r in results if r.model == "glm" and r.status == ModuleStatus.FAILURE)
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

    _MODEL_VERSION_MAP: dict[str, str] = {
        "deepseek": "deepseek-v4-pro",
        "glm": "glm-5.1",
        "claude": "claude-opus-4.7",
    }

    _MODEL_CONTEXT_LIMITS: dict[str, int] = {
        "deepseek": 128_000,
        "glm": 128_000,
        "claude": 200_000,
    }

    _MODEL_COST_PER_1K_INPUT: dict[str, float] = {
        "deepseek": 0.00174,
        "glm": 0.0,
        "claude": 0.005,
    }

    _MODEL_COST_PER_1K_OUTPUT: dict[str, float] = {
        "deepseek": 0.00348,
        "glm": 0.0,
        "claude": 0.025,
    }

    # B154 响应缓存——静态方法 _call_model 需要类属性访问
    _response_cache: dict[str, tuple[float, dict]] = {}
    _response_cache_ttl_s: float = 3600.0

    @staticmethod
    def _call_model(
        module_id: str,
        pipeline: str,
        model: str,
        task: TaskCard,
        *,
        token_divisor: int,
        prior_artifacts: list | None = None,
        dry_run: bool = False,
    ) -> dict:
        """调用 AI 模型执行模块

        **模拟边界**：非 dry_run 时默认仍返回 ``simulated: True`` 的占位输出，直至接入真实 LLM。
        详见 :class:`PipelineOrchestrator` 模块文档。

        v0.9.0 新增：
          - B150 模型版本锁定——返回 model_version 字段
          - B154 响应缓存——相同 task_id module_id 返回缓存
          - B161 $成本追踪——返回 cost_usd 字段
          - B170 上下文窗口校验——estimated_tokens vs model context_limit
        """
        model_version = PipelineOrchestrator._MODEL_VERSION_MAP.get(model, model)
        context_limit = PipelineOrchestrator._MODEL_CONTEXT_LIMITS.get(model, 128_000)

        if task.estimated_tokens > context_limit:
            return {
                "module_id": module_id,
                "pipeline": pipeline,
                "model": model,
                "model_version": model_version,
                "task_id": task.task_id,
                "simulated": True,
                "dry_run": dry_run,
                "tokens_used": 0,
                "cost_usd": 0.0,
                "summary": (
                    f"[CONTEXT-OVERFLOW] {module_id}: estimated_tokens={task.estimated_tokens} "
                    f"> model context_limit={context_limit} ——B170告警"
                ),
                "context_overflow": True,
            }

        if dry_run:
            return {
                "module_id": module_id,
                "pipeline": pipeline,
                "model": model,
                "model_version": model_version,
                "task_id": task.task_id,
                "simulated": True,
                "dry_run": True,
                "tokens_used": 0,
                "cost_usd": 0.0,
                "summary": f"[DRY-RUN {pipeline}区] {model}({model_version}) → {module_id}: {task.title[:60]}",
            }

        cache_key = f"{task.task_id}:{module_id}:{model}"
        if cache_key in PipelineOrchestrator._response_cache:
            cached_at, cached = PipelineOrchestrator._response_cache[cache_key]
            if time.time() - cached_at < PipelineOrchestrator._response_cache_ttl_s:
                return dict(cached, _from_cache=True)

        sanitized_title = PipelineOrchestrator._lsg_sanitize_input(task.title)
        sanitized_desc = PipelineOrchestrator._lsg_sanitize_input(task.description)

        tokens_used = task.estimated_tokens // max(token_divisor, 1)
        cost_input = (tokens_used / 1000.0) * PipelineOrchestrator._MODEL_COST_PER_1K_INPUT.get(model, 0.0)
        cost_output = (tokens_used / 1000.0) * PipelineOrchestrator._MODEL_COST_PER_1K_OUTPUT.get(model, 0.0)
        cost_usd = round(cost_input + cost_output, 6)

        artifact_keys = [a.artifact_key for a in (prior_artifacts or [])]
        raw_output = {
            "module_id": module_id,
            "pipeline": pipeline,
            "model": model,
            "model_version": model_version,
            "task_id": task.task_id,
            "simulated": True,
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "summary": f"[{pipeline}区] {model}({model_version}) → {module_id}: {sanitized_title[:60]}",
            "prior_artifact_keys": artifact_keys,
        }

        PipelineOrchestrator._response_cache[cache_key] = (time.time(), dict(raw_output))

        return PipelineOrchestrator._lsg_sanitize_output(module_id, raw_output)

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

    # ------------------------------------------------------------------
    # LifecycleAware 协议 —— B68
    # ------------------------------------------------------------------

    def on_init(self, lifecycle_mgr: Any) -> None:
        """LifecycleManager 回调：初始化后注册 Pipeline 组件。"""
        self._lifecycle_mgr = lifecycle_mgr
        try:
            from zephyr.shared.observer import Observer

            self._observer = lifecycle_mgr.resolve("observer", Observer)
        except Exception:
            self._observer = None
        self._initialized = True

    def on_startup(self) -> None:
        """LifecycleManager 回调：启动时从持久化恢复状态。"""
        self.load_state()

    def on_shutdown(self) -> None:
        """LifecycleManager 回调：关闭时等待活跃 dispatch + 持久化状态 + 释放所有锁。"""
        if self._active_dispatches:
            self._log("INFO", f"on_shutdown: waiting for {len(self._active_dispatches)} active dispatches")
            deadline = time.time() + 30.0
            while self._active_dispatches and time.time() < deadline:
                time.sleep(0.2)
            if self._active_dispatches:
                self._log("WARN", f"on_shutdown: {len(self._active_dispatches)} dispatches still active after 30s, forcing")
        self.save_state()
        if self._pipeline_lock is not None:
            active_locks = self._pipeline_lock.list_all() if hasattr(self._pipeline_lock, "list_all") else {}
            for task_id in list(active_locks.keys()):
                self._release_pipeline_lock(task_id)

    def health_check(self) -> dict:
        """LifecycleManager 回调：返回 Pipeline 健康状态（含 B168 自愈建议）。"""
        deepseek_fail = sum(v for k, v in self._failure_log.items() if "deepseek" in k.lower())
        glm_fail = sum(v for k, v in self._failure_log.items() if "glm" in k.lower())
        claude_fail = sum(v for k, v in self._failure_log.items() if "claude" in k.lower())
        active_preemptions = sum(1 for r in self._preempt_log.values() if r.resumed_at is None)
        cb_open = sum(1 for s in self._circuit_breaker_states.values() if s == CircuitBreakerState.OPEN)

        health: dict[str, Any] = {
            "module": "PipelineOrchestrator",
            "module_id": "MOD-INF-009",
            "status": "healthy",
            "initialized": self._initialized,
            "failure_summary": {
                "deepseek_failures": deepseek_fail,
                "glm_failures": glm_fail,
                "claude_failures": claude_fail,
            },
            "active_preemptions": active_preemptions,
            "circuit_breakers_open": cb_open,
            "active_dispatches": len(self._active_dispatches),
            "dead_letters": len(self._dead_letters),
            "cost_total_usd": round(self._cost_total, 4),
            "metrics": dict(self._metrics),
        }

        total_fail = deepseek_fail + glm_fail + claude_fail
        if total_fail > self._cfg.health_degraded_threshold:
            health["status"] = "degraded"
            health["warning"] = f"High failure count ({total_fail}) detected across models"
        if hasattr(self._task_repo, "total_tasks") and self._task_repo is not None and self._task_repo.total_tasks > 0:
            failure_ratio = total_fail / self._task_repo.total_tasks
            if failure_ratio > self._cfg.health_critical_failure_ratio:
                health["status"] = "critical"
                health["warning"] = f"Failure ratio {failure_ratio:.2%} exceeds threshold {self._cfg.health_critical_failure_ratio:.2%}"

        if cb_open > 0:
            health.setdefault("self_healing_suggestions", []).append(
                f"{cb_open} circuit breaker(s) open——建议手动调用 reset_circuit_breakers() 或等待冷却"
            )

        return health

    # ------------------------------------------------------------------
    # Telemetry 遥测 —— B67
    # ------------------------------------------------------------------

    def _record_telemetry_decision(self, task_type: str, node_id: str) -> None:
        """记录单次路由决策（pipe_routing_decision_count）。"""
        label = f"decision_{task_type}_{node_id}"
        self._metrics[label] = self._metrics.get(label, 0) + 1

    def _record_telemetry_latency(self, task_type: str, latency_ms: float) -> None:
        """记录路由延迟（pipe_routing_latency_ms histogram 采样）。"""
        key = f"latency_{task_type}"
        if key not in self._latency_samples:
            self._latency_samples[key] = []
        self._latency_samples[key].append(latency_ms)

    def _record_zone_crossing(self, from_zone: str, to_zone: str) -> None:
        """记录跨区事件（pipe_zone_crossing_count）。"""
        label = f"zone_{from_zone}→{to_zone}"
        self._metrics[label] = self._metrics.get(label, 0) + 1

    def get_telemetry_snapshot(self) -> dict[str, Any]:
        """导出当前遥测快照（供检查/测试使用）。"""
        return {
            "metrics": dict(self._metrics),
            "latency_samples": {k: v[:] for k, v in self._latency_samples.items()},
        }

    # ------------------------------------------------------------------
    # EventBus 集成 —— B71
    # ------------------------------------------------------------------

    def _emit_task_event(
        self,
        task_id: str,
        from_status: str,
        to_status: str,
    ) -> None:
        """通过 Observer 发布 TASK_EVENT。"""
        if self._observer is None:
            return
        try:
            payload: dict[str, Any] = {
                "task_id": task_id,
                "event_type": "TASK_EVENT",
                "from_status": from_status,
                "to_status": to_status,
                "timestamp": datetime.now().isoformat(),
                "source": "PipelineOrchestrator",
            }
            self._observer.emit("TASK_EVENT", payload)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Zone Crossing 防线 —— B70（AP2: A区→B区 M6边界标记校验）
    # ------------------------------------------------------------------

    def _validate_zone_crossing(
        self,
        task_card: TaskCard,
        prev_module_id: str,
        next_module_id: str,
    ) -> list[str]:
        """校验跨区操作的 AP2 合规性。

        A区(M1-M5)产出物不得直接流入B区(M6-M11)——
        必须经过M6边界标记。返回违规 warning 列表。
        """
        warnings: list[str] = []

        prev_spec = M_MODULE_SPECS.get(prev_module_id)
        next_spec = M_MODULE_SPECS.get(next_module_id)
        if prev_spec is None or next_spec is None:
            return warnings

        prev_pipeline = prev_spec.get("pipeline")
        next_pipeline = next_spec.get("pipeline")

        if prev_pipeline == "A" and next_pipeline == "B":
            if prev_module_id != "M5":
                warnings.append(
                    f"ZONE-CROSSING VIOLATION: A区{prev_module_id}→B区{next_module_id}"
                    f" 未经M5打包和M6边界标记（AP2）——policy:[A区产出物不得直接流入B区]"
                )
            else:
                self._record_zone_crossing("A", "B")

        return warnings

    # ------------------------------------------------------------------
    # LSG 安全闸门集成 —— B131（MOD-INF-014 LLM Security Gateway）
    # ------------------------------------------------------------------

    @staticmethod
    def _lsg_sanitize_input(text: str) -> str:
        """L1 输入检测：sanitize prompt 内容。

        懒加载 LSG——模块不存在时优雅降级为透传。
        层防御：
          - L1.1: Prompt injection 检测（DAN/角色扮演/ignore instructions）
          - L1.2: 敏感数据泄露检测（API key/password/token 模式）
          - L1.3: SQL/XSS injection 模式过滤
        """
        try:
            from zephyr.security.llm_security import LSGSecurityGateway

            gw = LSGSecurityGateway()
            result = gw.scan_input(text, source="PipelineOrchestrator")
            if result.blocked:
                return f"[LSG-BLOCKED] {result.sanitized[:200]}"
            return result.sanitized or text
        except ImportError:
            return text
        except Exception:
            return text

    @staticmethod
    def _lsg_sanitize_output(module_id: str, output: dict) -> dict:
        """L3 输出检测：sanitize 模型输出。

        懒加载 LSG——模块不存在时优雅降级为透传。
        层防御：
          - L3.1: 敏感信息脱敏（PII/credential 模式匹配）
          - L3.2: 有害内容过滤（hate/violence/self-harm classifiers）
          - L3.3: 对抗性输出检测（jailbreak 响应模式）
        """
        try:
            from zephyr.security.llm_security import LSGSecurityGateway

            gw = LSGSecurityGateway()
            for key in ("summary", "verdict", "detail", "minority_report"):
                if key in output and isinstance(output[key], str):
                    scan = gw.scan_output(output[key], source=f"Pipeline.{module_id}")
                    if scan.blocked:
                        output[key] = f"[LSG-BLOCKED] {scan.sanitized[:200]}"
                    elif scan.sanitized:
                        output[key] = scan.sanitized
            return output
        except ImportError:
            return output
        except Exception:
            return output

    # ------------------------------------------------------------------
    # 模型崩塌检测 —— B132（三模同质化预警 + 少数派报告）
    # ------------------------------------------------------------------

    def _verify_model_diversity(
        self,
        results: list[ModuleResult],
        task_card: TaskCard,
    ) -> ModelCollapseAlert:
        """检测 M3(DeepSeek) + M7(GLM) 输出是否高度同质化。

        崩塌判定条件：
          1. 两模 verdict 完全相同
          2. **且** 摘要相似度 > 80%（使用简单的 Jaccard/dice 相似度）
          3. → 标记为 warn；三模(hypothetical Claude rescue)均一致 → critical

        少数派报告：
          当两模一致但摘要或结论有细微差异时，记录 difference signal。
        """
        m3_results = [r for r in results if r.module_id == "M3"]
        m7_results = [r for r in results if r.module_id == "M7"]

        if not m3_results or not m7_results:
            return ModelCollapseAlert()

        m3 = m3_results[0]
        m7 = m7_results[0]

        if m3.status != ModuleStatus.SUCCESS or m7.status != ModuleStatus.SUCCESS:
            return ModelCollapseAlert()

        m3_verdict = m3.output.get("verdict", "")
        m7_verdict = m7.output.get("verdict", "")

        if not m3_verdict or not m7_verdict:
            return ModelCollapseAlert()

        if m3_verdict == m7_verdict:
            m3_summary = str(m3.output.get("summary", ""))
            m7_summary = str(m7.output.get("summary", ""))

            sim = self._text_similarity(m3_summary, m7_summary)
            detail_parts: list[str] = []

            if sim > 0.8:
                detail_parts.append(f"M3(DeepSeek)与M7(GLM)输出高度趋同(相似度={sim:.1%})")
                detail_parts.append(f"共同verdict: {m3_verdict!r}")
                detail_parts.append(
                    f"任务标题: {task_card.title[:80]}"
                )
                detail_parts.append(
                    "建议: 引入 Cross-Encoder reranker 或 adversarial prompt 打破同质化"
                )

                severity = "warn" if sim < 0.95 else "critical"
                self._log("WARN", f"ModelCollapse: M3+M7 similarity={sim:.1%} verdict={m3_verdict!r}")

                return ModelCollapseAlert(
                    detected=True,
                    severity=severity,
                    affected_modules=["M3", "M7"],
                    homogeneous_verdict=m3_verdict,
                    detail="; ".join(detail_parts),
                )
            elif sim > 0.5:
                return ModelCollapseAlert(
                    detected=True,
                    severity="info",
                    affected_modules=["M3", "M7"],
                    homogeneous_verdict=None,
                    detail=f"M3(DeepSeek)与M7(GLM)共识但摘要差异显著(相似度={sim:.1%})——可能存在细微分歧",
                    minority_report=f"verdict一致({m3_verdict!r})但摘要差异度={1-sim:.1%}",
                )

        return ModelCollapseAlert()

    @staticmethod
    def _text_similarity(a: str, b: str) -> float:
        """简单 Jaccard 相似度——word-level。

        生产环境应替换为 sentence-transformers cosine similarity。
        """
        if not a or not b:
            return 0.0
        words_a = set(c.lower() for c in a.split() if len(c) > 2)
        words_b = set(c.lower() for c in b.split() if len(c) > 2)
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union) if union else 0.0

    # ------------------------------------------------------------------
    # Token 预算协调 —— B135（跨 dispatch 预算协调）
    # ------------------------------------------------------------------

    _DEFAULT_TOKEN_BUDGET = 200_000

    def _check_token_budget(self, task_card: TaskCard) -> tuple[bool, str]:
        """检查跨 dispatch token 预算是否充足。

        当前活跃 dispatch 的已消耗 token 总计不应超过
        _DEFAULT_TOKEN_BUDGET 的 80%。
        """
        consumed_now = sum(self._token_budget_consumed.values())
        remaining = max(0, self._DEFAULT_TOKEN_BUDGET - consumed_now)
        usage_pct = consumed_now / self._DEFAULT_TOKEN_BUDGET if self._DEFAULT_TOKEN_BUDGET > 0 else 0

        if usage_pct > 0.8:
            self._log(
                "WARN",
                f"Token budget: {consumed_now}/{self._DEFAULT_TOKEN_BUDGET} ({usage_pct:.1%}) consumed across {len(self._active_dispatches)} active dispatches",
            )
            return False, (
                f"TOKEN-BUDGET: {consumed_now}/{self._DEFAULT_TOKEN_BUDGET} ({usage_pct:.1%}) consumed; "
                f"remaining={remaining}. Task {task_card.task_id} may be throttled."
            )

        if usage_pct > 0.5:
            return True, ""

        return True, ""

    def set_token_budget(self, budget: int) -> None:
        """设置全局 token 预算上限。"""
        self._token_budget_total = budget

    # ------------------------------------------------------------------
    # 职责分离 SoD —— B137（SOC2 CC5.3 Separation of Duties）
    # ------------------------------------------------------------------

    def _check_separation_of_duties(self, task_card: TaskCard) -> list[str]:
        """SoD 检查桩——防止同一主体同时承担生成+审批角色。

        当前为桩实现：检查 author == reviewer 模式。
        生产环境应接入 RBAC 系统（MOD-INF-008）验证角色分配。
        """
        warnings: list[str] = []
        author = getattr(task_card, "author", None) or getattr(task_card, "created_by", None)
        reviewer = getattr(task_card, "reviewer", None)
        if author and reviewer and author == reviewer:
            warnings.append(
                f"SOD-VIOLATION: Task {task_card.task_id} author={author} == reviewer={reviewer}. "
                "SOC2 CC5.3 requires Separation of Duties. Pipeline continuing with warning."
            )
        return warnings

    # ------------------------------------------------------------------
    # 结构化日志 —— B144（DEBUG/INFO/WARN/ERROR）
    # ------------------------------------------------------------------

    _LOG_LEVELS = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
    _DEFAULT_LOG_LEVEL = "INFO"

    @classmethod
    def _should_log(cls, level: str, threshold: str | None = None) -> bool:
        threshold = threshold or cls._DEFAULT_LOG_LEVEL
        return cls._LOG_LEVELS.get(level, 0) >= cls._LOG_LEVELS.get(threshold, 20)

    def _log(self, level: str, message: str) -> None:
        """结构化日志——B148 有界缓冲区（max=_cfg.log_buffer_max=2000）。"""
        ts = datetime.now().isoformat()
        self._log_buffer.append((ts, level, message))
        limit = self._cfg.log_buffer_max
        if len(self._log_buffer) > limit:
            self._log_buffer = self._log_buffer[-limit:]
        if self._should_log(level):
            print(f"[PipelineOrchestrator][{ts}][{level}] {message}", flush=True)

    def get_logs(self, *, level: str | None = None, limit: int = 100) -> list[tuple[str, str, str]]:
        """获取日志缓冲区——按 level 过滤。"""
        entries = self._log_buffer[-limit:]
        if level:
            entries = [(ts, lv, msg) for ts, lv, msg in entries if lv == level]
        return entries

    # ------------------------------------------------------------------
    # Circuit Breaker —— B151（对标 Netflix Hystrix）
    # ------------------------------------------------------------------

    _CB_FAILURE_WINDOW_S = 60.0
    _CB_FAILURE_THRESHOLD = 3
    _CB_COOLDOWN_S = 30.0

    def _check_circuit_breaker(self, cb_key: str, model: str) -> CircuitBreakerState:
        """检查断路器状态。

        CLOSED → OPEN：窗口内失败 >= _CB_FAILURE_THRESHOLD
        OPEN → HALF_OPEN：超过 _CB_COOLDOWN_S
        HALF_OPEN → CLOSED/OPEN：下一次调用结果决定
        """
        now = time.time()
        state = self._circuit_breaker_states.get(cb_key, CircuitBreakerState.CLOSED)

        if state == CircuitBreakerState.OPEN:
            failures = self._circuit_breaker_failures.get(cb_key, [])
            if failures:
                last_fail = max(failures)
                if now - last_fail >= self._CB_COOLDOWN_S:
                    self._circuit_breaker_states[cb_key] = CircuitBreakerState.HALF_OPEN
                    self._log("INFO", f"CircuitBreaker[{model}] OPEN→HALF_OPEN (冷却{self._CB_COOLDOWN_S}s后尝试恢复)")
                    return CircuitBreakerState.HALF_OPEN
            return CircuitBreakerState.OPEN

        if state == CircuitBreakerState.CLOSED:
            failures = self._circuit_breaker_failures.get(cb_key, [])
            recent = [t for t in failures if now - t <= self._CB_FAILURE_WINDOW_S]
            if len(recent) >= self._CB_FAILURE_THRESHOLD:
                self._circuit_breaker_states[cb_key] = CircuitBreakerState.OPEN
                self._log("WARN", f"CircuitBreaker[{model}] CLOSED→OPEN ({len(recent)} failures in {self._CB_FAILURE_WINDOW_S}s)")
                return CircuitBreakerState.OPEN
            return CircuitBreakerState.CLOSED

        return state

    def reset_circuit_breakers(self) -> int:
        """重置所有断路器到 CLOSED 状态。返回重置数量。"""
        count = len(self._circuit_breaker_states)
        self._circuit_breaker_states.clear()
        self._circuit_breaker_failures.clear()
        self._log("INFO", f"reset_circuit_breakers: {count} breaker(s) reset to CLOSED")
        return count

    # ------------------------------------------------------------------
    # 三模全失败降级 —— B147
    # ------------------------------------------------------------------

    def _emergency_fallback(
        self,
        results: list[ModuleResult],
        task_card: TaskCard,
    ) -> EmergencyFallbackPlan:
        """检测三模全失败并生成降级计划。"""
        failed_models: set[str] = set()
        for r in results:
            if r.status == ModuleStatus.FAILURE:
                failed_models.add(r.model)

        if len(failed_models) < 3:
            return EmergencyFallbackPlan()

        all_failed = sorted(failed_models)
        return EmergencyFallbackPlan(
            activated=True,
            all_models_failed=all_failed,
            recommended_action="WAIT_AND_RETRY",
            wait_before_retry_s=300,
            fallback_routes=["local-cache", "human-escalation", "kimi-k2"],
        )

    # ------------------------------------------------------------------
    # $ 成本计算 —— B161
    # ------------------------------------------------------------------

    def _compute_module_costs(self, results: list[ModuleResult]) -> list[CostRecord]:
        """从 ModuleResult 汇总逐模块成本。"""
        records: list[CostRecord] = []
        for r in results:
            cost_val = r.output.get("cost_usd", 0.0) if isinstance(r.output, dict) else 0.0
            records.append(CostRecord(
                model=r.model,
                tokens_input=r.tokens_used,
                cost_usd=float(cost_val),
            ))
        return records

    # ------------------------------------------------------------------
    # 死信队列 —— B169
    # ------------------------------------------------------------------

    def _maybe_dead_letter(
        self,
        task_card: TaskCard,
        results: list[ModuleResult],
        status: PipelineStatus,
    ) -> DeadLetterEntry | None:
        """永久失败任务写入死信队列。"""
        if status not in (PipelineStatus.FAILURE, PipelineStatus.CLAUDE_RESCUE):
            return None
        all_failed = all(r.status == ModuleStatus.FAILURE for r in results)
        if not all_failed:
            return None
        entry = DeadLetterEntry(
            task_id=task_card.task_id,
            failure_reason=f"All {len(results)} modules failed",
            retry_count=self._cfg.max_retries,
            last_error=results[0].errors[0] if results and results[0].errors else "unknown",
        )
        self._dead_letters.append(entry)
        return entry

    def get_dead_letters(self) -> list[DeadLetterEntry]:
        return list(self._dead_letters)

    # ------------------------------------------------------------------
    # 速率限制感知 —— B162
    # ------------------------------------------------------------------

    def _check_rate_limit(self, model: str) -> tuple[bool, float]:
        """检查模型调用速率。返回 (is_limited: bool, wait_seconds: float)。"""
        rate = self._cfg.rate_limit_per_model.get(model, 999.0)
        now = time.time()
        self._rate_limit_timestamps.setdefault(model, [])
        recent = [t for t in self._rate_limit_timestamps[model] if now - t <= 1.0]
        self._rate_limit_timestamps[model] = recent

        if len(recent) >= rate:
            if recent:
                wait_s = 1.0 - (now - recent[0]) + 0.1
                return True, max(wait_s, 0.05)
            return True, 0.1

        self._rate_limit_timestamps[model].append(now)
        return False, 0.0

    # ------------------------------------------------------------------
    # AI 影响评估 —— B157（NIST AI RMF MAP 函数）
    # ------------------------------------------------------------------

    def _assess_impact(self, task_card: TaskCard) -> AIImpactAssessment:
        """对 TaskCard 执行 AI 影响评估。"""
        tags_lower = [t.lower() for t in (task_card.tags or [])]

        risk_tier = "low"
        if any(kw in tags_lower for kw in ("security", "auth", "credential", "pii")):
            risk_tier = "critical"
        elif any(kw in tags_lower for kw in ("experimental", "breaking", "migration")):
            risk_tier = "high"
        elif hasattr(task_card, "execution_model") and task_card.execution_model == "claude":
            risk_tier = "medium"

        human_review = risk_tier in ("high", "critical")

        stakeholders = []
        if "l01_infrastructure" in tags_lower or "infrastructure" in tags_lower:
            stakeholders.append("infrastructure-team")
        if any(kw in tags_lower for kw in ("gov", "compliance", "audit", "policy")):
            stakeholders.append("compliance-officer")

        return AIImpactAssessment(
            risk_tier=risk_tier,
            affected_stakeholders=stakeholders,
            data_sensitivity_level="internal",
            autonomy_level="assistive" if human_review else "autonomous",
            human_review_required=human_review,
        )

    # ------------------------------------------------------------------
    # 置信度估算 —— B158
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_confidence(model: str, output: dict) -> ModelConfidence | None:
        """基于模型特性估算置信度——生产环境应替换为实际 logprob。"""
        scores = {"deepseek": 0.65, "glm": 0.88, "claude": 0.92}
        base = scores.get(model, 0.5)
        simulated = output.get("simulated", False)
        if simulated:
            return None
        return ModelConfidence(
            score=base,
            source="static_estimate",
            calibration_note=f"{model} 基准估算——生产环境需接入 logprob API",
        )

    # ------------------------------------------------------------------
    # A/B 实验路由 —— B159
    # ------------------------------------------------------------------

    def _resolve_experiment(self, task_card: TaskCard) -> ABExperimentRoute | None:
        """基于 task_id hash 决定 A/B 实验变体。"""
        if not self._active_experiments:
            return None
        for exp_id, exp_route in self._active_experiments.items():
            h = int(hashlib.md5(task_card.task_id.encode()).hexdigest()[:8], 16)
            variant = ExperimentVariant.TREATMENT if (h % 100) < 50 else ExperimentVariant.CONTROL
            return ABExperimentRoute(
                experiment_id=exp_id,
                variant=variant,
                routing_hash=f"hash={h} bucket={h % 100}",
                control_route=exp_route.control_route,
                treatment_route=exp_route.treatment_route,
            )
        return None

    def register_experiment(self, experiment_id: str, control: str, treatment: str) -> None:
        """注册 A/B 实验。"""
        self._active_experiments[experiment_id] = ABExperimentRoute(
            experiment_id=experiment_id,
            variant=ExperimentVariant.CONTROL,
            control_route=control,
            treatment_route=treatment,
        )
        self._log("INFO", f"Experiment[{experiment_id}] registered: control={control}, treatment={treatment}")

    def get_experiments(self) -> dict[str, ABExperimentRoute]:
        return dict(self._active_experiments)

    # ------------------------------------------------------------------
    # 偏差检测 —— B156（桩实现）
    # ------------------------------------------------------------------

    @staticmethod
    def _check_bias(output: dict) -> list[str]:
        """检测模型输出中的受保护属性偏差——NIST AI RMF MEASURE 2.6。

        桩实现：返回空列表。生产环境接入 bias-detection 模型。
        """
        return []

    # ------------------------------------------------------------------
    # 准确率追踪 —— B155（桩实现）
    # ------------------------------------------------------------------

    def _track_accuracy(self, task_id: str, module_id: str, model: str, score: float) -> None:
        """记录模型准确率分数——Langfuse Score 对标。"""
        if not self._cfg.accuracy_tracking_enabled:
            return
        key = f"{model}:{module_id}"
        self._accuracy_data.setdefault(key, []).append(score)
        if len(self._accuracy_data[key]) > 1000:
            self._accuracy_data[key] = self._accuracy_data[key][-1000:]

    def get_accuracy_summary(self) -> dict[str, dict[str, float]]:
        """返回各模型×模块的准确率摘要。"""
        summary: dict[str, dict[str, float]] = {}
        for key, scores in self._accuracy_data.items():
            if not scores:
                continue
            summary[key] = {
                "count": len(scores),
                "mean": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
            }
        return summary

    # ------------------------------------------------------------------
    # 成本统计公开 API
    # ------------------------------------------------------------------

    def get_cost_summary(self) -> dict[str, Any]:
        return {
            "total_usd": round(self._cost_total, 4),
            "by_model": {
                m: round(sum(c.cost_usd for c in self._cost_records if c.model == m), 4)
                for m in ("deepseek", "glm", "claude")
                if any(c.model == m for c in self._cost_records)
            },
            "record_count": len(self._cost_records),
        }
