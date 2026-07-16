# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §4.1
# [MODULE] zephyr.integration.pipeline_orchestrator
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.__init__; zephyr.shared.__init__; zephyr.shared.contracts.protocols; zephyr.shared.models; zephyr.intelligence.model_profiling.pipeline_routing.profiler; zephyr.integration.local_model.local_model_scheduler; zephyr.governance.__init__; zephyr.gov_audit.writer; zephyr.autonomy_core.__init__; zephyr.shared.contracts.task_repository_protocol; zephyr.intelligence.model_profiling.pipeline_routing.results_writer; zephyr.shared.contracts.llm_gateway_protocol; zephyr.shared.infra.observer; zephyr.security.llm_defense.llm_security.gateway; zephyr.shared.contracts.security.__init__; zephyr.shared.protocols.a2a.layer3_coordination.__init__; zephyr.integration.local_model.embedding_router; zephyr.intelligence.model_evaluation.reranker; zephyr.infrastructure.pipeline.models; zephyr.infrastructure.pipeline.circuit_breaker_manager; zephyr.infrastructure.pipeline.cost_tracker; zephyr.infrastructure.pipeline.ct_pipe_routing; zephyr.infrastructure.pipeline.dead_letter_queue; zephyr.infrastructure.pipeline.model_router; zephyr.infrastructure.pipeline.pipeline_lock; zephyr.infrastructure.pipeline.preemption_manager; zephyr.infrastructure.pipeline.routing_plugins
# [CONSUMERS] zephyr.trading.auto_runtime_core; tests/trading/test_pipeline_orchestrator_unit.py; tests/pipeline/test_pipeline_orchestrator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
PipelineOrchestrator — M1-M11 管线协调器
=========================================
依据：MOD-TASK_SYSTEM §3.1.3 + §3.1.1 dispatch() + GOV-AI-002 v2.0.0 决策树
     + CT-PIPE-ORC-001（蓝图 MOD-MASTER_BLUEPRINT §2.7，见 ct_pipe_routing.py）

**真源边界（AUDIT-08，与 route_manifest task_dual_pipeline 一致）**
  - **M1–M11 入口与模块切片**：``TaskCard``（含 ct_pipe 提示）+ ``ct_pipe_routing.resolve_ct_pipe_orc001``
    + 本协调器；**不以** ``config/blueprint_routing.yaml`` 解析 Mx 节点。
  - **blueprint_routing.yaml**：关键词 / 路径模式 -> 蓝图文献与人类检索（含 ``blueprint_search`` MCP），
    属 **MOD-INF-009 路由表**，与 **CT-PIPE** 编排正交。

**真实 LLM API 集成**：
  - ``_call_model`` 通过 ``LLMGateway`` 调用真实 LLM API（DeepSeek / GLM / Claude / OpenAI）
  - 成功时返回 ``simulated=False``，使用 LLM 实际输出
  - fallback 路径仅在 API 不可用时返回 ``simulated=True`` 占位（防御性降级）

双管线架构：
  A区 M1-M5 -> 生产（代码生成/校验/打包）
  B区 M6-M11 -> 审计（审查/合规/风险评估/门禁）

三层模型策略（GOV-AI-002 §一）：
  DeepSeek V4 Pro -> 主力生产（M1-M4 + M6/M8/M9/M10/M11）—— 1.74/3.48/M
  GLM-5.1        -> 深度审查（M7 + M5）—— Trae CN免费
  Claude Opus 4.7 -> 特种救援（DeepSeek失败3次 / GLM驳回2次 / Owner关键标记 / security标签 / experimental标签）

v0.3.2 集成：PipelineOrchestrator ↔ TaskRepository 修桥
  - dispatch() 开始 -> task_repo.transition(PENDING->IN_PROGRESS)
  - dispatch() 成功 -> task_repo.transition(IN_PROGRESS->COMPLETED)
  - dispatch() 失败 -> task_repo.transition(IN_PROGRESS->FAILED)
  - task_repo 可选——为 None 时跳过状态流转（向后兼容测试场景）

使用：
    from zephyr.shared.foundation.models import TaskCard
    from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator
from zephyr.infrastructure.pipeline.models import PipelineOrchestratorConfig
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

    config = PipelineOrchestratorConfig(max_retries=3, claude_rescue_threshold=3)
    orchestrator = PipelineOrchestrator(config, task_repo=repo)
    result = orchestrator.dispatch(task_card)

裁定#216 Tier1 P4 重构（2026-07-15，Extract Method）
----------------------------------------------------
原 dispatch 305 行 McCabe=51（orchestrator state machine，try/except/finally
内 ~25+ 分支串联，P4 orchestrator pattern）。治本：Extract Method 提取为 4 个
helper（_resolve_pipeline_and_modules / _setup_lock_and_skills /
_finalize_and_build_result / _handle_dispatch_exception，均 McCabe≤10），dispatch
简化为 ~80 行 skeleton（McCabe≈11）。行为等价契约：
  - _state dict {"lock_acquired": bool, "final_status": PipelineStatus|None}
    替代原局部变量，跨 try/except/finally 共享可变状态
  - 前置检查（幂等/rollback/RBAC/impact/experiment）保持 inline（仅 5 分支）
  - 管线解析（hints None vs CT-PIPE）提取到 _resolve_pipeline_and_modules
  - 锁/SOD/token/preempt/G6/skill 提取到 _setup_lock_and_skills
  - 状态终结/结果构建提取到 _finalize_and_build_result
  - 异常处理提取到 _handle_dispatch_exception
  - finally 块保持原样（discard + 条件 release lock）
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import hashlib
import json
import os
import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler
    from zephyr.intelligence.model_profiling.pipeline_routing.profiler import ModelProfiler
    from zephyr.shared.foundation.models import TaskCard

from zephyr.infrastructure.pipeline.circuit_breaker_manager import CircuitBreakerManager
from zephyr.infrastructure.pipeline.cost_tracker import CostTracker
from zephyr.infrastructure.pipeline.ct_pipe_routing import (
    PipelineRoutingInputsError,
    ct_pipe_hints_from_task_card,
    modules_slice_from_node,
    resolve_ct_pipe_orc001,
)
from zephyr.infrastructure.pipeline.dead_letter_queue import DeadLetterQueue
from zephyr.infrastructure.pipeline.model_router import ModelRouter
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.async_utils import run_sync  # DM-100252/LSG-fix: 实际 import（原 L53 在 docstring 内非真实 import）
from zephyr.infrastructure.pipeline.models import (
    M_MODULE_SPECS,
    M_MODULES,
    ABExperimentRoute,
    AIImpactAssessment,
    ClaudeRescueTrigger,
    DeadLetterEntry,
    EmergencyFallbackPlan,
    ExecutionMode,
    ExperimentVariant,
    ModelCollapseAlert,
    ModelConfidence,
    ModuleResult,
    ModuleStatus,
    NightShiftAmbiguityLogEntry,
    PipelineArtifact,
    PipelineArtifactManifest,
    PipelineLineageChain,
    PipelineLineageEntry,
    PipelineOrchestratorConfig,
    PipelineResult,
    PipelineStatus,
    validate_module_output,
)
from zephyr.infrastructure.pipeline.pipeline_lock import LockResult, PipelineLock
from zephyr.infrastructure.pipeline.preemption_manager import PreemptionManager
from zephyr.infrastructure.pipeline.routing_plugins import PipelineRouter
from zephyr.shared.schema.task_types import TaskStatus
from zephyr.shared.utils.time_utils import now_utc

_RBAC_AVAILABLE = False
try:
    from zephyr.governance.agent_spec.rbac_bridge import EscalationRBACBridge, RBACCheckResult

    _RBAC_AVAILABLE = True
except ImportError:
    EscalationRBACBridge = None  # type: ignore[misc,assignment]
    RBACCheckResult = None  # type: ignore[misc,assignment]

_AUDIT_AVAILABLE = False
try:
    from zephyr.gov_audit.writer import AuditWriter
    from zephyr.shared.contracts.protocols import AuditWriterProtocol

    _AUDIT_AVAILABLE = True
except ImportError:
    AuditWriter = None  # type: ignore[misc,assignment]

_SKILL_BRIDGE_AVAILABLE = False
try:
    from zephyr.autonomy_core.integration.pipeline_bridge import (
        PipelineSkillBridge,
        SkillInjectionResult,
    )

    _SKILL_BRIDGE_AVAILABLE = True
except ImportError:
    PipelineSkillBridge = None  # type: ignore[misc,assignment]
    SkillInjectionResult = None  # type: ignore[misc,assignment]

_LOCAL_SCHEDULER_AVAILABLE = False
try:
    from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler

    _LOCAL_SCHEDULER_AVAILABLE = True
except ImportError:
    LocalModelScheduler = None  # type: ignore[assignment,misc]

_PROFILER_AVAILABLE = False
try:
    from zephyr.intelligence.model_profiling.pipeline_routing.profiler import ModelProfiler

    _PROFILER_AVAILABLE = True
except ImportError:
    ModelProfiler = None  # type: ignore[assignment,misc]

if TYPE_CHECKING:
    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol
    from zephyr.integration.local_model.embedding_router import EmbeddingRouterProtocol
    from zephyr.shared.protocols.ports import RerankerProtocol
    from zephyr.governance.ops_governance.budget_engine import BudgetEngineProtocol
    from zephyr.autonomy_core.integration.pipeline_bridge import PipelineSkillBridge
    from zephyr.shared.lifecycle.hooks import LifecycleManager

__all__ = ["PipelineOrchestrator"]


# === 裁定#216 Tier1 P4 参数对象（2026-07-15）===
# _finalize_and_build_result 原 16 参数（>7，违反 NO-LONG-PARAM-LIST）。
# 治本：用 dataclass 封装 15 个非 task_card 参数，签名降为 (task_card, ctx) 2 参数。
@dataclass
class _DispatchFinalizeContext:
    """_finalize_and_build_result 参数对象（避免 >7 参数列表，§5.150）。"""

    pipeline: str
    execution_mode: Any
    route: str
    results: list[ModuleResult]
    dry_run: bool
    ct_decision: Any
    ct_warnings: list[str]
    manifest: PipelineArtifactManifest
    lineage_chain: PipelineLineageChain
    impact: Any
    skill_injection: Any
    task_type: str
    night_shift_log: list
    _dispatch_start: Any
    _state: dict[str, Any]


def _process_zone_warnings(
    orch: PipelineOrchestrator,
    task_card: TaskCard,
    prev_module: str | None,
    mod_id: str,
    ct_warnings: list[str],
) -> None:
    """校验 zone 跨界；VIOLATION 抛错，其余告警追加到 ct_warnings。"""
    if prev_module is None:
        return
    zone_warnings = orch._validate_zone_crossing(task_card, prev_module, mod_id)
    for zw in zone_warnings:
        if "VIOLATION" in zw:
            raise ValueError(zw)
        ct_warnings.append(zw)


def _resolve_assigned_model(mod_id: str, pipeline: str, route: str) -> str:
    """根据 pipeline/route 与模块 spec 决定本模块使用的模型。"""
    spec = M_MODULE_SPECS[mod_id]
    assigned_model = spec["model"]
    if pipeline == "B" and route == "claude":
        assigned_model = "claude"
    elif spec.get("pipeline") == pipeline:
        pass
    else:
        assigned_model = spec["model"]
    return assigned_model


def _record_skill_feedback(
    skill_injection: SkillInjectionResult | None,
    mr: ModuleResult,
    task_card: TaskCard,
) -> None:
    """记录 skill 反馈到学习回路；失败仅 debug 日志，不影响主流程。"""
    if not (_SKILL_BRIDGE_AVAILABLE and skill_injection is not None and skill_injection.loaded):
        return
    try:
        from zephyr.autonomy_core.skills.skill_feedback import SkillFeedback

        fb = SkillFeedback()
        for skid in [skill_injection.domain_skill_id, skill_injection.role_skill_id]:
            if skid:
                fb.record_module_result(skid, mr, task_card.task_id)
    except Exception:
        # 5.12.1 修复：原 except: pass 静默吞 skill feedback 失败（学习回路断链）
        logger.debug("skill feedback record failed for task=%s", task_card.task_id, exc_info=True)


def _process_module_artifacts(
    mr: ModuleResult,
    mod_id: str,
    manifest: PipelineArtifactManifest,
    prior_artifacts: list[PipelineArtifact],
) -> tuple[list[str], list[str]]:
    """解析本模块产出/消费的 artifact，追加到 manifest；返回 (consumed_keys, produced_keys)。"""
    consumed_keys = [a.artifact_key for a in prior_artifacts if a.produced_by != mod_id]
    produced_keys: list[str] = []
    for art_dict in mr.output.get("artifacts", []):
        try:
            artifact = PipelineArtifact(**art_dict)
            manifest.artifacts.append(artifact)
            produced_keys.append(artifact.artifact_key)
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞 artifact 解析失败（产物丢失不可见）
            logger.debug("artifact dict parse failed for mod=%s", mod_id, exc_info=True)

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
            # 5.12.1 修复：原 except: pass 静默吞 artifact 构造失败（产物丢失不可见）
            logger.debug(
                "artifact build failed for mod=%s key=%s",
                mod_id,
                mr.output.get("artifact_key"),
                exc_info=True,
            )
    return consumed_keys, produced_keys


def _load_read_blueprint_ids(metrics_path: Path) -> set[str] | None:
    """读取 blueprint_reads.jsonl，返回已读蓝图 ID 集合。

    返回 None 表示读取失败（OSError），调用方据此生成 G6-BLOCKED 消息。
    """
    try:
        read_blueprints: set[str] = set()
        with open(metrics_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except Exception:
                    continue
                if record.get("event") == "blueprint_read":
                    read_blueprints.add(record.get("blueprint_id", ""))
    except OSError:
        return None
    return read_blueprints


def _compute_missing_blueprint_ids(candidates: list[dict], read_blueprints: set[str]) -> list[str]:
    """计算候选蓝图中尚未被读取的 blueprint_id 列表（取前 3 个）。"""
    missing: list[str] = []
    for c in candidates[:3]:
        bpid = c.get("blueprint_id", "")
        if bpid and bpid not in read_blueprints:
            missing.append(bpid)
    return missing


def _format_g6_violation(missing: list[str], candidates: list[dict], task_desc: str) -> str:
    """构造 G6 Phase 2 硬合规阻断消息。"""
    hint = candidates[0].get("hint", "")
    return (
        f"G6 Phase 2 硬合规阻断: AI 未读取以下蓝图即尝试执行 Pipeline"
        f"——{'·'.join(missing)}。"
        f"Phase 2 hard_compliance=true -> dispatch REJECTED。"
        f"Action: invoke find_relevant_blueprint('{task_desc[:60]}') -> read §1-§5 -> record_blueprint_read() -> retry。"
        + (f" Hint: {hint}" if hint else "")
    )


class PipelineOrchestrator:
    """M1-M11 双管线模型路由 + 模块编排

    Parameters
    ----------
    config : PipelineOrchestratorConfig
        编排器配置（重试次数 / Claude 触发阈值 / 超时等）
    task_repo : TaskRepositoryProtocol | None
        SQLite 任务仓库——为 None 时跳过状态流转（测试兼容模式）
    """

    _lsg_gateway = None
    _lsg_gateway_lock = threading.Lock()  # 5.16.4 修复：保护 _lsg_gateway 懒加载竞态

    def __init__(
        self,
        config: PipelineOrchestratorConfig | None = None,
        task_repo: TaskRepositoryProtocol | None = None,
        router: PipelineRouter | None = None,
        pipeline_lock: PipelineLock | None = None,
        agent_orchestrator: object | None = None,
        telemetry: object | None = None,
        embedding_router: EmbeddingRouterProtocol | None = None,
        reranker: RerankerProtocol | None = None,
        budget_engine: BudgetEngineProtocol | None = None,
    ) -> None:
        self._cfg = config or PipelineOrchestratorConfig()
        self._task_repo = task_repo
        self._router = router
        self._pipeline_lock = pipeline_lock
        self._agent_orchestrator = agent_orchestrator
        self._telemetry = telemetry
        self._embedding_router: EmbeddingRouterProtocol | None = embedding_router
        self._reranker_instance: RerankerProtocol | None = reranker
        # 5.133.2 DI: 注入 BudgetEngine，避免 _check_token_budget 硬编码实例化
        self._budget_engine: BudgetEngineProtocol | None = budget_engine
        self._failure_log: dict[str, int] = {}
        # PENDING: ref to make _dispatched_ids / _active_dispatches exist before _preempt_mgr

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
        self._preempt_mgr = PreemptionManager(
            task_repo=self._task_repo,
            dispatched_ids=self._dispatched_ids,
            active_dispatches=self._active_dispatches,
            re_dispatch_callback=self.dispatch,
            priority_cutoff="P2",
        )
        self._cb_manager = CircuitBreakerManager(log_fn=self._log)
        self._rate_limit_timestamps: dict[str, list[float]] = {}
        self._cost_tracker = CostTracker()
        self._dlq = DeadLetterQueue()
        self._accuracy_data: dict[str, list[float]] = {}
        self._active_experiments: dict[str, ABExperimentRoute] = {}
        self._rbac_bridge = EscalationRBACBridge() if _RBAC_AVAILABLE else None
        self._audit_writer = AuditWriter() if _AUDIT_AVAILABLE else None
        self._skill_bridge = PipelineSkillBridge() if _SKILL_BRIDGE_AVAILABLE else None
        self._night_shift_counter: int = 0
        self._local_scheduler: LocalModelScheduler | None = (
            LocalModelScheduler() if _LOCAL_SCHEDULER_AVAILABLE else None
        )
        self._model_profiler: ModelProfiler | None = ModelProfiler() if _PROFILER_AVAILABLE else None
        self._periodic_profile_interval_s: float = self._cfg.periodic_profile_interval_s
        self._auto_profile_on_startup: bool = self._cfg.auto_profile_on_startup
        self._profile_thread: threading.Thread | None = None
        self._profile_results: list[dict[str, object]] = []

        if self._auto_profile_on_startup and self._model_profiler is not None:
            self._start_auto_profile()

    # ------------------------------------------------------------------
    # 模型性能检测 — 触发策略
    # ------------------------------------------------------------------

    def _start_auto_profile(self) -> None:
        """启动时自动运行一次 benchmark（后台线程，不阻塞初始化）。"""
        import threading

        def _run():
            self._log("INFO", "ModelProfiler: auto-startup benchmark initiated")
            try:
                results = self.run_model_benchmark()
                self._feed_results_to_router(results)
                self._log("INFO", f"ModelProfiler: auto-startup complete ({len(results)} models)")
            except Exception as exc:
                self._log("WARN", f"ModelProfiler: auto-startup failed: {exc}")

        t = threading.Thread(target=_run, daemon=True, name="model-profiler-startup")
        t.start()
        self._profile_thread = t

    def start_periodic_profile(self) -> None:
        """启动定时 benchmark（每隔 periodic_profile_interval_s 秒运行一次）。"""
        import threading

        if self._periodic_profile_interval_s <= 0:
            self._log("INFO", "ModelProfiler: periodic profiling disabled (interval <= 0)")
            return

        def _loop():
            import time

            while True:
                time.sleep(self._periodic_profile_interval_s)
                try:
                    self._log("INFO", "ModelProfiler: periodic benchmark triggered")
                    results = self.run_model_benchmark()
                    self._feed_results_to_router(results)
                    for r in results:
                        name = r.get("model_name", "")
                        if name:
                            drift = self.detect_model_drift(str(name))
                            if drift and drift.get("drift_detected"):
                                self._log("WARN", f"ModelDrift: {name} drift detected — {drift.get('details', {})}")
                except Exception as exc:
                    self._log("WARN", f"ModelProfiler: periodic failed: {exc}")

        t = threading.Thread(target=_loop, daemon=True, name="model-profiler-periodic")
        t.start()
        self._log("INFO", f"ModelProfiler: periodic profiling every {self._periodic_profile_interval_s}s")

    def _feed_results_to_router(self, results: list[dict[str, object]]) -> None:
        """将 benchmark 结果注入 ModelRouter。"""
        if self._router is None:
            return
        try:
            count = self._router.load_benchmark_profiles(results)  # type: ignore[union-attr]
            self._log("INFO", f"ModelProfiler: fed {count} profiles to ModelRouter")
        except Exception as exc:
            self._log("WARN", f"ModelProfiler: failed to feed router: {exc}")

    def run_model_benchmark(self) -> list[dict[str, object]]:
        """运行全量模型性能 benchmark，返回排名结果列表。"""
        if self._model_profiler is None:
            self._log("WARN", "ModelProfiler not available")
            return []

        profiles = self._model_profiler.profile_ollama_only()
        from zephyr.intelligence.model_profiling.pipeline_routing.results_writer import (
            to_model_benchmark_result,
            write_benchmark_results,
        )

        write_benchmark_results(profiles)
        results = [to_model_benchmark_result(p) for p in profiles if p.available]
        self._profile_results = results
        return results

    def get_best_model(self) -> dict[str, object] | None:
        """获取当前 benchmark 排名第一的模型信息。"""
        if self._model_profiler is None:
            return None

        profiles = self._model_profiler.profile_ollama_only()
        best = next((p for p in profiles if p.rank == 1 and p.available), None)
        if best is None:
            return None

        from zephyr.intelligence.model_profiling.pipeline_routing.results_writer import (
            to_model_benchmark_result,
        )

        return to_model_benchmark_result(best)

    def detect_model_drift(self, model_name: str) -> dict[str, object] | None:
        """检测指定模型是否发生性能漂移。"""
        try:
            from zephyr.intelligence.model_profiling.pipeline_routing.results_writer import (
                detect_drift,
                load_benchmark_history,
            )
        except ImportError:
            return None

        history = load_benchmark_history(model_name)
        if len(history) < 2:
            return {"drift_detected": False, "reason": "insufficient_history", "model_name": model_name}
        return detect_drift(history)

    @property
    def profile_results(self) -> list[dict[str, object]]:
        return self._profile_results

    @property
    def has_profiles(self) -> bool:
        return len(self._profile_results) > 0

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def start_local_scheduler(self) -> None:
        if self._local_scheduler is not None and not self._local_scheduler.running:
            self._local_scheduler.start()
            self._log("INFO", "LocalModelScheduler started (L2 24/7)")

    def stop_local_scheduler(self) -> None:
        if self._local_scheduler is not None and self._local_scheduler.running:
            self._local_scheduler.stop()
            self._log("INFO", "LocalModelScheduler stopped")

    def dispatch(self, task_card: TaskCard, *, dry_run: bool = False) -> PipelineResult:
        """接收 TaskCard -> 执行管线（含状态机集成）

        流程：
          ① CT-PIPE-ORC-001：若 TaskCard 激活路由提示 -> 从入口 Mx 切片执行；否则整链
          ② 状态流转 PENDING->IN_PROGRESS（如 task_repo 注入）
          ③ 模型路由（GOV-AI-002 决策树）
          ④ 逐模块执行（含 LSG 安全闸门 + 数据血缘追踪）
          ⑤ Claude 救援判定
          ⑥ 模型崩塌检测（M3+M7+Claude 同质化预警）
          ⑦ 状态流转 IN_PROGRESS->COMPLETED/FAILED（如 task_repo 注入）

        Parameters
        ----------
        dry_run : bool
            True 时只模拟路由和校验，不实际调用 AI 模型。
        """
        ct_warnings: list[str] = []
        ct_decision = None
        hints = ct_pipe_hints_from_task_card(task_card)

        _dispatch_start = now_utc()

        self._active_dispatches.add(task_card.task_id)
        self._log(
            "INFO", f"dispatch[{task_card.task_id}] started pipeline={task_card.assigned_pipeline} dry_run={dry_run}"
        )

        # --- 前置检查（幂等/rollback/RBAC/impact/experiment）---
        idempotency_result = self._check_idempotency(task_card, dry_run)
        if idempotency_result is not None:
            return idempotency_result

        rollback_result, rollback_warnings = self._handle_rollback_exit(task_card, dry_run)
        if rollback_result is not None:
            return rollback_result
        ct_warnings.extend(rollback_warnings)

        rbac_result = self._check_rbac(task_card, dry_run)
        if rbac_result is not None:
            return rbac_result

        impact = self._assess_impact(task_card)
        if impact.human_review_required:
            ct_warnings.append(
                f"IMPACT: risk_tier={impact.risk_tier} autonomy={impact.autonomy_level} "
                f"——NIST AI RMF MAP函数要求人工复核"
            )

        experiment_route = self._resolve_experiment(task_card)
        if experiment_route is not None:
            ct_warnings.append(
                f"AB-EXPERIMENT: experiment={experiment_route.experiment_id} variant={experiment_route.variant.value}"
            )

        # --- 管线解析（裁定#216 P4：提取到 _resolve_pipeline_and_modules）---
        resolve_result = self._resolve_pipeline_and_modules(task_card, hints, dry_run, ct_warnings)
        if isinstance(resolve_result, PipelineResult):
            return resolve_result
        pipeline, modules, ct_decision = resolve_result

        tw = self._transition(task_card.task_id, TaskStatus.IN_PROGRESS)
        if tw:
            ct_warnings.append(tw)

        lineage_chain = PipelineLineageChain(run_id=task_card.task_id)

        # 5.142.1 修复: 用 _state dict 跨 try/except/finally 共享 lock_acquired/final_status
        _state: dict[str, Any] = {"lock_acquired": False, "final_status": None}
        try:
            setup = self._setup_lock_and_skills(
                task_card, hints, ct_decision, ct_warnings, dry_run, modules, _state
            )
            if isinstance(setup, PipelineResult):
                return setup
            route, execution_mode, night_shift_log, task_type, skill_injection = setup

            manifest = PipelineArtifactManifest(run_id=task_card.task_id)
            executed_module_ids: list[str] = []
            results = self._execute_modules_loop(
                task_card, modules, pipeline, route, manifest,
                lineage_chain, executed_module_ids, skill_injection,
                dry_run, ct_warnings,
            )

            return self._finalize_and_build_result(
                task_card,
                _DispatchFinalizeContext(
                    pipeline=pipeline,
                    execution_mode=execution_mode,
                    route=route,
                    results=results,
                    dry_run=dry_run,
                    ct_decision=ct_decision,
                    ct_warnings=ct_warnings,
                    manifest=manifest,
                    lineage_chain=lineage_chain,
                    impact=impact,
                    skill_injection=skill_injection,
                    task_type=task_type,
                    night_shift_log=night_shift_log,
                    _dispatch_start=_dispatch_start,
                    _state=_state,
                ),
            )
        except Exception as exc:
            self._handle_dispatch_exception(task_card, exc, _state, ct_warnings)
        finally:
            self._active_dispatches.discard(task_card.task_id)
            # 5.142.1 修复: 锁释放移入 finally, 用标志位避免双重释放
            if _state["lock_acquired"]:
                self._release_pipeline_lock(task_card.task_id)

    # ------------------------------------------------------------------
    # 裁定#216 Tier1 P4 Extract Method helpers（2026-07-15）
    # ------------------------------------------------------------------

    def _resolve_pipeline_and_modules(
        self,
        task_card: TaskCard,
        hints: Any,
        dry_run: bool,
        ct_warnings: list[str],
    ) -> tuple[str, list[str], Any] | PipelineResult:
        """解析管线与模块切片（hints None → 整链；否则 CT-PIPE 路由）。

        裁定#216 P4：从 dispatch 提取。返回 (pipeline, modules, ct_decision)
        或 PipelineResult（路由失败 early exit）。ct_warnings 就地扩展。
        """
        if hints is None:
            pipeline = task_card.assigned_pipeline
            if pipeline not in ("A", "B"):
                self._active_dispatches.discard(task_card.task_id)
                return PipelineResult(
                    task_id=task_card.task_id,
                    pipeline=pipeline,
                    overall_status=PipelineStatus.FAILURE,
                    modules_executed=[],
                    finished_at=now_utc().isoformat(),
                    is_dry_run=dry_run,
                )
            modules = [m for m in M_MODULES if M_MODULE_SPECS[m]["pipeline"] == pipeline]
            return pipeline, modules, None
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
                finished_at=now_utc().isoformat(),
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
        return pipeline, modules, ct_decision

    def _setup_lock_and_skills(
        self,
        task_card: TaskCard,
        hints: Any,
        ct_decision: Any,
        ct_warnings: list[str],
        dry_run: bool,
        modules: list[str],
        _state: dict[str, Any],
    ) -> tuple[str, Any, list, str, Any] | PipelineResult:
        """执行模型路由/SOD/token/preempt/lock/G6/skill injection 设置。

        裁定#216 P4：从 dispatch 提取。返回 (route, execution_mode, night_shift_log,
        task_type, skill_injection) 或 PipelineResult（lock/G6 失败 early exit）。
        _state["lock_acquired"] 在锁获取成功后置 True。
        """
        route = self._route_model(task_card)
        execution_mode = self._resolve_execution_mode(task_card)
        night_shift_log: list[NightShiftAmbiguityLogEntry] = []

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

        preemptions = self._preempt_mgr.preempt(task_card)
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
                finished_at=now_utc().isoformat(),
                is_dry_run=dry_run,
                ct_pipe_route=ct_decision,
                ct_pipe_warnings=ct_warnings
                + [f"LOCK: files={lock_result.locked_files} conflict_with={lock_result.conflict_tasks}"],
            )

        # 5.142.1 修复: 标记锁已获取, finally 块统一释放
        _state["lock_acquired"] = True

        g6_violation = self._check_g6_blueprint_compliance(task_card, modules)
        if g6_violation is not None:
            self._active_dispatches.discard(task_card.task_id)
            # 5.142.1 修复: 移除显式 release, 由 finally 统一释放
            return PipelineResult(
                task_id=task_card.task_id,
                pipeline=task_card.assigned_pipeline,
                overall_status=PipelineStatus.G6_BLOCKED,
                modules_executed=[],
                finished_at=now_utc().isoformat(),
                is_dry_run=dry_run,
                ct_pipe_route=ct_decision,
                ct_pipe_warnings=ct_warnings + [g6_violation],
            )

        skill_injection = self._inject_skill(task_card, hints, ct_warnings)

        return route, execution_mode, night_shift_log, task_type, skill_injection

    def _inject_skill(
        self,
        task_card: TaskCard,
        hints: Any,
        ct_warnings: list[str],
    ) -> SkillInjectionResult | None:
        """技能注入（裁定#216 P4：从 _setup_lock_and_skills 提取以降低复杂度）。

        _skill_bridge 为 None 时返回 None；注入失败时记录 debug 日志并返回 None。
        """
        if self._skill_bridge is None:
            return None
        stage_hint = (hints.target_layer if hints and hints.target_layer else None) or "construction"
        task_desc = (
            (getattr(task_card, "description", "") or "")
            + " "
            + (getattr(task_card, "title", "") or "")
            + " "
            + (", ".join(getattr(task_card, "tags", []) or []))
        )
        try:
            skill_injection = self._skill_bridge.inject_for_task(
                task_description=task_desc,
                stage=stage_hint,
            )
            if skill_injection.loaded:
                ct_warnings.append(
                    f"SKILL-LOADED: domain={skill_injection.domain_skill_id} "
                    f"role={skill_injection.role_skill_id} "
                    f"tokens={skill_injection.token_budget.get('total_tokens', '?')}"
                )
            return skill_injection
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞 skill injection 失败（技能增强静默失效）
            logger.debug("skill injection failed for task=%s", task_card.task_id, exc_info=True)
            return None

    def _finalize_and_build_result(
        self,
        task_card: TaskCard,
        ctx: _DispatchFinalizeContext,
    ) -> PipelineResult:
        """执行状态终结 + 构建 PipelineResult。

        裁定#216 P4：从 dispatch 提取。计算 rescue/collapse_alert/status，执行状态流转，
        记录 telemetry，构建并返回 PipelineResult。ctx._state["final_status"] 记录最终状态。
        """
        rescue = self._check_claude_rescue(task_card, ctx.results)
        collapse_alert = self._verify_model_diversity(ctx.results, task_card)

        status = self._determine_status(ctx.results)
        if rescue.triggered:
            status = PipelineStatus.CLAUDE_RESCUE

        passed = sum(1 for r in ctx.results if r.status == ModuleStatus.SUCCESS)
        partial = passed > 0 and passed < len(ctx.results)
        if status == PipelineStatus.SUCCESS and partial:
            status = PipelineStatus.PARTIAL_FAILURE

        total_tokens = sum(r.tokens_used for r in ctx.results if r.tokens_used > 0)
        if total_tokens > 0:
            self._token_budget_consumed[task_card.task_id] = total_tokens
        uw = self._update_runtime_metrics(task_card.task_id, total_tokens)
        if uw:
            ctx.ct_warnings.append(uw)

        if status in (PipelineStatus.SUCCESS, PipelineStatus.PARTIAL_FAILURE):
            tw = self._transition(task_card.task_id, TaskStatus.COMPLETED)
        else:
            tw = self._transition(task_card.task_id, TaskStatus.FAILED)
        if tw:
            ctx.ct_warnings.append(tw)

        # 5.142.1 修复: 记录已成功的 status, 防止后续异常导致 except 块误转 FAILED
        ctx._state["final_status"] = status
        # 5.142.1 修复: 移除显式 release, 由 finally 统一释放

        _latency_ms = (now_utc() - ctx._dispatch_start).total_seconds() * 1000
        self._record_telemetry_latency(ctx.task_type, _latency_ms)

        cost_records = self._cost_tracker.records

        emergency_fallback = self._emergency_fallback(ctx.results, task_card)
        dead_letter = self._dlq.enqueue(task_card, ctx.results, status, self._cfg.max_retries)
        cb_state = self._cb_manager.status(task_card.task_id).get(task_card.task_id)

        bridge_result = None
        if self._agent_orchestrator is not None:
            try:
                from zephyr.infrastructure.pipeline.pipeline_agent_bridge import PipelineAgentBridge

                bridge = PipelineAgentBridge(self._agent_orchestrator)
                bridge_result = bridge.bridge(
                    PipelineResult(
                        task_id=task_card.task_id,
                        pipeline=ctx.pipeline,
                        modules_executed=ctx.results,
                        overall_status=status,
                    ),
                    token_budget=total_tokens if total_tokens > 0 else None,
                )
            except Exception:
                self._log("WARN", f"dispatch[{task_card.task_id}] bridge failed")

        self._write_audit_event(
            task_card.task_id,
            f"pipeline.{ctx.pipeline}",
            status.value,
            {"modules_executed": len(ctx.results), "cost_total_usd": sum(c.cost_usd for c in cost_records)},
        )
        return self._build_dispatch_result(
            task_card=task_card, pipeline=ctx.pipeline, execution_mode=ctx.execution_mode,
            results=ctx.results, status=status, rescue=rescue, collapse_alert=collapse_alert,
            dry_run=ctx.dry_run, ct_decision=ctx.ct_decision, ct_warnings=ctx.ct_warnings,
            manifest=ctx.manifest, lineage_chain=ctx.lineage_chain, impact=ctx.impact,
            skill_injection=ctx.skill_injection, cost_records=cost_records,
            emergency_fallback=emergency_fallback, dead_letter=dead_letter,
            cb_state=cb_state, bridge_result=bridge_result, night_shift_log=ctx.night_shift_log,
        )

    def _handle_dispatch_exception(
        self,
        task_card: TaskCard,
        exc: Exception,
        _state: dict[str, Any],
        ct_warnings: list[str],
    ) -> None:
        """处理 dispatch 异常：记录日志/发布事件/条件性 FAILED 流转/重抛。

        裁定#216 P4：从 dispatch 提取。读取 _state["final_status"] 判断是否已成功
        （避免误转 FAILED）。始终 raise。
        """
        self._log("ERROR", f"dispatch[{task_card.task_id}] failed with exception")
        try:
            from datetime import UTC, datetime

            from zephyr.shared.event_bus import EventBusBackpressure

            EventBusBackpressure().emit(
                "pipeline_failed",
                payload={
                    "timestamp": datetime.now(UTC).isoformat(),
                    "pipeline_id": task_card.task_id,
                    "error_type": type(exc).__name__,
                    "error_detail": f"dispatch[{task_card.task_id}] failed: {exc}",
                },
            )
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞 EventBus 失败事件发布失败（故障信号丢失）
            logger.warning("EventBus pipeline_failed emit failed for task=%s", task_card.task_id, exc_info=True)
        # 5.142.1 修复: 移除显式 release, 由 finally 统一释放
        self._active_dispatches.discard(task_card.task_id)
        # 5.142.1 修复: 若 pipeline 已成功(SUCCESS/PARTIAL_FAILURE), 后续异常不应误转 FAILED
        if _state["final_status"] not in (PipelineStatus.SUCCESS, PipelineStatus.PARTIAL_FAILURE):
            tw = self._transition(task_card.task_id, TaskStatus.FAILED)
            if tw:
                self._failure_log[f"dispatch_exc_{task_card.task_id}"] = (
                    self._failure_log.get(f"dispatch_exc_{task_card.task_id}", 0) + 1
                )
        raise

    # ------------------------------------------------------------------
    # dispatch 子方法（5.140.1 修复：从 461 行 dispatch 中提取）
    # ------------------------------------------------------------------

    def _check_idempotency(self, task_card: TaskCard, dry_run: bool) -> PipelineResult | None:
        """幂等性检查：同一 TaskCard 不重复执行。未重复时返回 None 并登记 task_id。"""
        if task_card.task_id in self._dispatched_ids:
            self._active_dispatches.discard(task_card.task_id)
            self._log(
                "WARN", f"dispatch[{task_card.task_id}] idempotency guard: already dispatched, rejecting duplicate"
            )
            return PipelineResult(
                task_id=task_card.task_id,
                pipeline=task_card.assigned_pipeline,
                overall_status=PipelineStatus.FAILURE,
                modules_executed=[],
                finished_at=now_utc().isoformat(),
                is_dry_run=dry_run,
                ct_pipe_warnings=["IDEMPOTENCY: duplicate dispatch rejected——同一TaskCard已执行过"],
            )
        self._dispatched_ids.add(task_card.task_id)
        return None

    def _handle_rollback_exit(self, task_card: TaskCard, dry_run: bool) -> tuple[PipelineResult | None, list[str]]:
        """处理 rollback_exit 标签。返回 (early_result, warnings)。early_result 非 None 时阻断 dispatch。"""
        warnings: list[str] = []
        tags = set(task_card.tags or ())
        if "rollback_exit" not in tags:
            return None, warnings
        exit_code_tag = [t for t in tags if t.startswith("rollback_exit:")]
        exit_code = int(exit_code_tag[0].split(":")[1]) if exit_code_tag else -1
        try:
            from zephyr.infrastructure.rollback.contract import get_gate_action, get_pipeline_action

            gate_action, desc = get_gate_action(exit_code)
            pipeline_action = get_pipeline_action(gate_action)
            if gate_action in ("BLOCK", "BLOCK_AUTO", "FAIL", "L3_KILL", "L2_KILL"):
                self._active_dispatches.discard(task_card.task_id)
                _exit_detail = (
                    f"Rollback exit code {exit_code} blocked dispatch: {gate_action} -> {pipeline_action}"
                )
                self._log("WARN", f"dispatch[{task_card.task_id}] {_exit_detail}")
                return PipelineResult(
                    task_id=task_card.task_id,
                    pipeline=task_card.assigned_pipeline,
                    overall_status=PipelineStatus.FAILURE,
                    modules_executed=[],
                    finished_at=now_utc().isoformat(),
                    is_dry_run=dry_run,
                    ct_pipe_warnings=[_exit_detail],
                ), warnings
            elif gate_action in ("WARN", "ROLLBACK", "PAUSE_AGENT", "PAUSE_AUTO", "REDUCE_TIER"):
                warnings.append(
                    f"ROLLBACK_EXIT: exit_code={exit_code} gate={gate_action} pipeline={pipeline_action}"
                )
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞 rollback_exit 门禁决策失败（安全门禁失效不可见）
            logger.warning("rollback_exit gate parse failed for task=%s exit_code=%s",
                           task_card.task_id, exit_code, exc_info=True)
        return None, warnings

    def _check_rbac(self, task_card: TaskCard, dry_run: bool) -> PipelineResult | None:
        """RBAC 权限校验。通过返回 None，失败返回 PipelineResult(FAILURE)。"""
        rbac_result = self._rbac_check(task_card)
        if rbac_result is not None and not rbac_result.passed:
            self._active_dispatches.discard(task_card.task_id)
            self._write_audit_event(
                task_card.task_id,
                f"pipeline.{task_card.assigned_pipeline}",
                "RBAC_BLOCKED",
                {"layer": rbac_result.layer, "rule": rbac_result.rule_id, "reason": rbac_result.reason},
            )
            self._log(
                "WARN",
                f"dispatch[{task_card.task_id}] RBAC blocked: {rbac_result.reason} layer={rbac_result.layer} rule={rbac_result.rule_id}",
            )
            _tags = task_card.tags or ()
            _needs_rescue = "security" in _tags or "experimental" in _tags
            return PipelineResult(
                task_id=task_card.task_id,
                pipeline=task_card.assigned_pipeline,
                overall_status=PipelineStatus.FAILURE,
                modules_executed=[],
                finished_at=now_utc().isoformat(),
                is_dry_run=dry_run,
                ct_pipe_warnings=[f"RBAC BLOCKED [{rbac_result.layer}/{rbac_result.rule_id}]: {rbac_result.reason}"],
                needs_claude_rescue=_needs_rescue,
                rescue_reason="Security/Experimental tag detected — RBAC blocked but Claude review required"
                if _needs_rescue
                else "",
            )
        return None

    def _execute_modules_loop(
        self,
        task_card: TaskCard,
        modules: list[str],
        pipeline: str,
        route: str,
        manifest: PipelineArtifactManifest,
        lineage_chain: PipelineLineageChain,
        executed_module_ids: list[str],
        skill_injection: SkillInjectionResult | None,
        dry_run: bool,
        ct_warnings: list[str],
    ) -> list[ModuleResult]:
        """逐模块执行循环。返回模块结果列表，副作用修改 manifest/lineage_chain/executed_module_ids/ct_warnings。"""
        results: list[ModuleResult] = []
        prev_module: str | None = None
        for mod_id in modules:
            _process_zone_warnings(self, task_card, prev_module, mod_id, ct_warnings)

            assigned_model = _resolve_assigned_model(mod_id, pipeline, route)

            prior_artifacts = [a for a in manifest.artifacts if a.produced_by != mod_id]

            mr = self._execute_module(
                mod_id,
                pipeline,
                assigned_model,
                task_card,
                token_divisor=len(modules),
                prior_artifacts=prior_artifacts,
                dry_run=dry_run,
                skill_injection=skill_injection,
            )
            results.append(mr)

            _record_skill_feedback(skill_injection, mr, task_card)

            consumed_keys, produced_keys = _process_module_artifacts(mr, mod_id, manifest, prior_artifacts)

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

        return results

    def _build_dispatch_result(
        self,
        *,
        task_card: TaskCard,
        pipeline: str,
        execution_mode: str,
        results: list[ModuleResult],
        status: PipelineStatus,
        rescue: object,
        collapse_alert: object,
        dry_run: bool,
        ct_decision: object,
        ct_warnings: list[str],
        manifest: PipelineArtifactManifest,
        lineage_chain: PipelineLineageChain,
        impact: object,
        skill_injection: SkillInjectionResult | None,
        cost_records: list,
        emergency_fallback: object,
        dead_letter: object,
        cb_state: object,
        bridge_result: object,
        night_shift_log: list,
    ) -> PipelineResult:
        """构造 dispatch 的最终 PipelineResult。"""
        return PipelineResult(
            task_id=task_card.task_id,
            pipeline=pipeline,
            execution_mode=execution_mode,
            modules_executed=results,
            overall_status=status,
            needs_claude_rescue=rescue.triggered,
            rescue_reason=rescue.reason,
            finished_at=now_utc().isoformat(),
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
            skill_injection=(
                {
                    "loaded": skill_injection.loaded,
                    "domain_skill_id": skill_injection.domain_skill_id,
                    "role_skill_id": skill_injection.role_skill_id,
                    "total_tokens": skill_injection.token_budget.get("total_tokens"),
                    "context": skill_injection.injection_context[:500],
                }
                if skill_injection is not None
                else None
            ),
            night_shift_log=night_shift_log,
        )

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
                return f"_transition[{task_id}->{to_status.name}]: task not found in repo"
            if task.status == to_status:
                return None
            from_status = task.status.name if hasattr(task.status, "name") else str(task.status).split(".")[-1]
            self._task_repo.transition(task_id, to_status)
            self._emit_task_event(task_id, from_status, to_status.name)
            return None
        except Exception as exc:
            self._failure_log[f"transition_{task_id}"] = self._failure_log.get(f"transition_{task_id}", 0) + 1
            return f"_transition[{task_id}->{to_status.name}]: {type(exc).__name__}: {exc}"

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
        return ModelRouter.resolve_model(task_card)

    # ------------------------------------------------------------------
    # 三层执行模式解析 —— 根据人类在场 + 任务类型路由
    # ------------------------------------------------------------------

    _LOCAL_ONLY_CAPABILITIES: frozenset[str] = frozenset(
        {
            "vector_embedding",
            "semantic_search",
            "reranking",
        }
    )

    def _is_human_present(self) -> bool:
        method = self._cfg.human_detection_method
        if method == "manual_switch":
            return getattr(self._cfg, "_manual_override_human_present", True)
        if method == "time_window":
            now_hour = now_utc().hour
            return self._cfg.working_hours_start <= now_hour < self._cfg.working_hours_end
        return True

    def _resolve_execution_mode(self, task_card: TaskCard) -> ExecutionMode:
        if self._is_human_present():
            return ExecutionMode.TRAE

        task_type = getattr(task_card, "execution_model", "")
        capabilities = getattr(task_card, "capabilities", []) or []
        tags = getattr(task_card, "tags", []) or []

        for cap in capabilities:
            if cap in self._LOCAL_ONLY_CAPABILITIES:
                return ExecutionMode.LOCAL

        creative_tags = {"codegen", "architecture", "design", "creative", "generate"}
        if any(t in creative_tags for t in tags):
            return ExecutionMode.API

        deterministic_types = {"audit", "compliance", "cleanup", "repair", "format", "lint"}
        if task_type in deterministic_types or any(t in deterministic_types for t in tags):
            return ExecutionMode.API

        return ExecutionMode.API

    def _record_night_shift_ambiguity(
        self,
        task_id: str,
        module: str,
        context: str,
        options: list[dict[str, str]] | None = None,
    ) -> NightShiftAmbiguityLogEntry:
        self._night_shift_counter += 1
        entry = NightShiftAmbiguityLogEntry(
            id=f"NSL-{self._night_shift_counter:04d}",
            task_id=task_id,
            module=module,
            context=context,
            options=options or [],
            auto_decision="C",
            requires_human=True,
        )
        self._log("WARN", f"NightShiftAmbiguity: {entry.id} task={task_id} module={module}: {context[:80]}")
        return entry

    # ------------------------------------------------------------------
    # CT-PIPE 路由解析
    # ------------------------------------------------------------------

    def _resolve_ct_pipe(self, hints):
        if self._router is not None:
            return self._router.route(hints)
        return resolve_ct_pipe_orc001(hints)

    # ------------------------------------------------------------------
    # 优先级抢占——已提取至 PreemptionManager（SRC-0027）
    # ------------------------------------------------------------------

    def resume_preempted(
        self,
        completed_task_id: str,
    ) -> list[PipelineResult]:
        """完成高优先级任务后，恢复被其抢占的低优先级任务并重新 dispatch。

        委托至 ``PreemptionManager.resume_preempted()``。
        """
        return self._preempt_mgr.resume_preempted(completed_task_id)

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
            "preempt_mgr": self._preempt_mgr.save_state(),
            "metrics": dict(self._metrics),
            "latency_samples": {k: v[:] for k, v in self._latency_samples.items()},
            "cost_tracker": self._cost_tracker.save_state(),
            "dead_letters": self._dlq.save_state(),
        }

    def load_state(self, state: dict) -> None:
        """从持久化字典恢复编排器状态——B153 含配置恢复。"""
        if "config" in state:
            self._cfg = PipelineOrchestratorConfig(**state["config"])
        self._failure_log = dict(state.get("failure_log", {}))
        self._preempt_mgr.load_state(state.get("preempt_mgr", {}))
        self._cost_tracker.load_state(state.get("cost_tracker", {}))
        self._dlq.load_state(state.get("dead_letters", []))

    def _release_pipeline_lock(self, task_id: str) -> None:
        if self._pipeline_lock is not None:
            self._pipeline_lock.release(task_id)

    # ------------------------------------------------------------------
    # 模型降级 Fallback 链 —— GOV-AI-002 §三 补充
    # ------------------------------------------------------------------

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
        chain = [primary_model] + ModelRouter.FALLBACK_CHAIN.get(primary_model, [])
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
                        started_at=now_utc().isoformat(),
                        finished_at=now_utc().isoformat(),
                        fallback_from=primary_model if model != primary_model else None,
                    ),
                    model,
                )
            except Exception as exc:
                last_error = f"[{model}] {type(exc).__name__}: {exc}"
                if model in ModelRouter.FALLBACK_CHAIN:
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
                started_at=now_utc().isoformat(),
                finished_at=now_utc().isoformat(),
                fallback_from=None,
            ),
            primary_model,
        )

    # ------------------------------------------------------------------
    # 多模型双盲审查 —— M3(DeepSeek) + M7(GLM) 并行->取交集
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
                started_at=now_utc().isoformat(),
                finished_at=now_utc().isoformat(),
                blind_review_role="generator",
            )
            m7_mr = ModuleResult(
                module_id="M7",
                pipeline=pipeline,
                model="glm",
                status=ModuleStatus.SUCCESS,
                output={"summary": f"[DRY-RUN BLIND] M7: {task.title[:60]}"},
                started_at=now_utc().isoformat(),
                finished_at=now_utc().isoformat(),
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
        skill_injection: PipelineSkillBridge | None = None,
    ) -> ModuleResult:
        started = now_utc().isoformat()
        last_error: str | None = None
        divisor = token_divisor if token_divisor and token_divisor > 0 else len(M_MODULES)

        cb_key = f"{task.task_id}:{module_id}:{model}"
        if self._cfg.circuit_breaker_enabled:
            if not self._cb_manager.allow_request(cb_key, model):
                return ModuleResult(
                    module_id=module_id,
                    pipeline=pipeline,
                    model=model,
                    status=ModuleStatus.FAILURE,
                    errors=[f"CIRCUIT-OPEN: {model} 断路器已断开——短路跳过重试"],
                    started_at=started,
                    finished_at=now_utc().isoformat(),
                )

        if not dry_run and self._cfg.rate_limit_per_model:
            rate_limited, wait_s = self._check_rate_limit(model)
            if rate_limited:
                time.sleep(wait_s)

        for attempt in range(1, self._cfg.max_retries + 1):
            try:
                output = self._call_model(
                    module_id,
                    pipeline,
                    model,
                    task,
                    token_divisor=divisor,
                    prior_artifacts=prior_artifacts,
                    dry_run=dry_run,
                    skill_injection=skill_injection,
                )
                output = validate_module_output(module_id, output)

                confidence = self._generate_confidence(model, output)

                cost_usd = output.get("cost_usd", 0.0)
                self._cost_tracker.record_call(
                    model=model,
                    tokens_input=output.get("tokens_used", 0),
                    cost_usd=cost_usd,
                )

                if self._cfg.circuit_breaker_enabled:
                    self._cb_manager.record_result(cb_key, success=True)

                return ModuleResult(
                    module_id=module_id,
                    pipeline=pipeline,
                    model=model,
                    status=ModuleStatus.SUCCESS,
                    output=output,
                    tokens_used=output.get("tokens_used", 0),
                    duration_ms=0,
                    started_at=started,
                    finished_at=now_utc().isoformat(),
                    confidence=confidence,
                )
            except Exception as exc:
                last_error = f"[{attempt}/{self._cfg.max_retries}] {type(exc).__name__}: {exc}"
                if self._cfg.circuit_breaker_enabled:
                    self._cb_manager.record_result(cb_key, success=False)
                if attempt < self._cfg.max_retries:
                    # 5.72.6 修复：原无jitter，多任务并发重试同一模型端点时可能产生惊群效应。
                    # 添加 ±10% 随机抖动，避免重试同步化。
                    delay = min(2**attempt, 30)
                    delay = delay + random.uniform(0, delay * 0.1)
                    time.sleep(delay)

        self._failure_log[module_id] = self._failure_log.get(module_id, 0) + 1
        self._failure_log["_task_" + task.task_id] = self._failure_log.get("_task_" + task.task_id, 0) + 1

        return ModuleResult(
            module_id=module_id,
            pipeline=pipeline,
            model=model,
            status=ModuleStatus.FAILURE,
            errors=[last_error] if last_error else ["unknown failure"],
            started_at=started,
            finished_at=now_utc().isoformat(),
        )

    # ------------------------------------------------------------------
    # 本地模型集成 —— 24/7常驻 EmbeddingRouter + Reranker
    # ------------------------------------------------------------------

    _embedding_router: EmbeddingRouterProtocol | None = None
    _reranker_instance: RerankerProtocol | None = None

    def _ensure_local_models(self) -> None:
        if self._cfg.local_model_always_on and self._embedding_router is None:
            try:
                from zephyr.integration.local_model.embedding_router import EmbeddingRouter

                self._embedding_router = EmbeddingRouter()
                self._embedding_router.warmup()
                self._log("INFO", "Local models warmed up: EmbeddingRouter + Reranker ready")
            except Exception as exc:
                self._log("WARN", f"Local model warmup failed: {exc}")

    def embed_text(self, text: str, collection_name: str) -> list[float]:
        self._ensure_local_models()
        if self._embedding_router is None:
            self._log("ERROR", "EmbeddingRouter not available, returning zero vector")
            return self._zero_vector(512)
        return self._embedding_router.embed(text, collection_name)

    def rerank_documents(self, query: str, documents: list[str]) -> list:
        self._ensure_local_models()
        if self._reranker_instance is None:
            try:
                from zephyr.intelligence.model_evaluation.reranker import Reranker

                self._reranker_instance = Reranker()
            except Exception as exc:
                self._log("WARN", f"Reranker init failed: {exc}")
                self._reranker_instance = False
        if self._reranker_instance is False or self._reranker_instance is None:
            return documents
        return self._reranker_instance.rerank(query, documents)

    @staticmethod
    def _zero_vector(dim: int) -> list[float]:
        import numpy as np

        return np.zeros(dim, dtype=np.float32)

    # ------------------------------------------------------------------
    # Claude 特种救援 — GOV-AI-002 §三
    # ------------------------------------------------------------------

    def _populate_claude_trigger_flags(
        self, trigger: ClaudeRescueTrigger, task_card: TaskCard
    ) -> None:
        """Set tag/owner-based flags on the trigger object."""
        if "experimental" in (task_card.tags or ()):
            trigger.is_experimental = True
        if "security" in (task_card.tags or ()):
            trigger.has_security_tag = True
        if task_card.ai_autonomy_level == "unsafe":
            trigger.is_owner_critical = True

    def _build_claude_rescue_reasons(
        self,
        trigger: ClaudeRescueTrigger,
        deepseek_fail: int,
        glm_reject: int,
    ) -> list[str]:
        """Build human-readable reasons list for Claude rescue trigger."""
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

        return reasons

    def _check_claude_rescue(self, task_card: TaskCard, results: list[ModuleResult]) -> ClaudeRescueTrigger:
        """判断是否触发 Claude 救援。

        tags 检查与 _route_model() 共享规则集——新增 tag 需同步修改两处。
        """
        trigger = ClaudeRescueTrigger()
        self._populate_claude_trigger_flags(trigger, task_card)

        deepseek_fail = sum(1 for r in results if r.model == "deepseek" and r.status == ModuleStatus.FAILURE)
        glm_reject = sum(1 for r in results if r.model == "glm" and r.status == ModuleStatus.FAILURE)
        trigger.deepseek_failure_count = deepseek_fail
        trigger.glm_rejection_count = glm_reject

        reasons = self._build_claude_rescue_reasons(trigger, deepseek_fail, glm_reject)
        if reasons:
            trigger.triggered = True
            trigger.reason = "; ".join(reasons)

        return trigger

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    # B154 响应缓存——静态方法 _call_model 需要类属性访问
    _response_cache: dict[str, tuple[float, dict]] = {}
    _response_cache_ttl_s: float = 3600.0

    @staticmethod
    def _build_skill_context(skill_injection: PipelineSkillBridge | None) -> str:
        """Build agent skill context string from the skill injection bridge."""
        if skill_injection is None:
            return ""
        if hasattr(skill_injection, "injection_context") and skill_injection.injection_context:
            return skill_injection.injection_context
        if not hasattr(skill_injection, "l2_domain_body"):
            return ""
        parts: list[str] = []
        if skill_injection.l2_domain_body:
            parts.append(f"[Domain Skill: {skill_injection.domain_skill_id}]\n{skill_injection.l2_domain_body}")
        if hasattr(skill_injection, "l2_role_body") and skill_injection.l2_role_body:
            parts.append(f"[Role Skill: {skill_injection.role_skill_id}]\n{skill_injection.l2_role_body}")
        return "\n\n".join(parts)

    @staticmethod
    def _call_llm_gateway(messages: list[dict], model: str):
        """Call LLM gateway; return response or None on ImportError."""
        # SRC-0022: Real LLM API via LLMGateway with explicit model ID mapping
        #   Model -> API ID: DeepSeek-V4-Pro/deepseek -> deepseek-chat, GLM-5.1/glm -> glm-4-flash
        #   Provider config (base_url, api_key_env, default_model) defined in
        #   zephyr.infrastructure.pipeline.llm_gateway._PROVIDERS.
        try:
            from zephyr.shared.contracts.llm_gateway_protocol import LLMGatewayProtocol as LLMGateway
            from zephyr.shared.contracts.llm_gateway_protocol import LLMResponse

            return LLMGateway.call(
                messages,
                provider=model if model in LLMGateway.list_providers() else "deepseek",
                max_tokens=4096,
                temperature=0.3,
            )
        except ImportError:
            return None

    @staticmethod
    def _compute_simulated_fields(
        task: TaskCard,
        token_divisor: int,
        model: str,
        pipeline: str,
        module_id: str,
        model_version: str,
        sanitized_title: str,
    ) -> tuple:
        """Compute simulated (non-real-LLM) response fields.

        Returns (tokens_used, cost_usd, summary_content, simulated, provider_used).
        """
        tokens_used = task.estimated_tokens // max(token_divisor, 1)
        # SRC-0022 fix: use ModelRouter constants directly (was self._cost_tracker.estimate_cost
        # which crashes in @staticmethod — self is not defined)
        cost_usd = round(
            (tokens_used / 1000.0) * ModelRouter.MODEL_COST_PER_1K_INPUT.get(model, 0.0)
            + (tokens_used / 1000.0) * ModelRouter.MODEL_COST_PER_1K_OUTPUT.get(model, 0.0),
            6,
        )
        summary_content = f"[{pipeline}区] {model}({model_version}) -> {module_id}: {sanitized_title[:60]}"
        return tokens_used, cost_usd, summary_content, True, model

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
        skill_injection: PipelineSkillBridge | None = None,
    ) -> dict:
        """调用 AI 模型执行模块

        **模拟边界**：非 dry_run 时默认仍返回 ``simulated: True`` 的占位输出，直至接入真实 LLM。
        详见 :class:`PipelineOrchestrator` 模块文档。

        v0.9.0 新增：
          - B150 模型版本锁定——返回 model_version 字段
          - B154 响应缓存——相同 task_id module_id 返回缓存
          - B161 $成本追踪——返回 cost_usd 字段
        v0.10.0 新增：
          - skill_injection: PipelineSkillBridge 注入的 Domain+Role Skill 上下文
        """
        skill_context = PipelineOrchestrator._build_skill_context(skill_injection)

        model_version = ModelRouter.MODEL_VERSION_MAP.get(model, model)
        context_limit = ModelRouter.MODEL_CONTEXT_LIMITS.get(model, 128_000)

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
                "skill_context": skill_context,
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
                "summary": f"[DRY-RUN {pipeline}区] {model}({model_version}) -> {module_id}: {task.title[:60]}",
                "skill_context": skill_context,
            }

        cache_key = f"{task.task_id}:{module_id}:{model}"
        if cache_key in PipelineOrchestrator._response_cache:
            cached_at, cached = PipelineOrchestrator._response_cache[cache_key]
            if time.time() - cached_at < PipelineOrchestrator._response_cache_ttl_s:
                return dict(cached, _from_cache=True)

        sanitized_title = PipelineOrchestrator._lsg_sanitize_input(task.title)
        sanitized_desc = PipelineOrchestrator._lsg_sanitize_input(task.description)

        system_msg = (
            f"You are an expert agent in the [{pipeline}] zone of ZephyrAlpha. "
            f"Execute module [{module_id}] for task [{task.task_id}]. "
            f"Follow the constraints below precisely."
        )
        user_msg = f"Task: {sanitized_title}\n\nDescription: {sanitized_desc}"

        if skill_context:
            system_msg += f"\n\n--- AGENT SKILL CONTEXT ---\n{skill_context}\n--- END SKILL CONTEXT ---"

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        llm_resp = PipelineOrchestrator._call_llm_gateway(messages, model)

        if llm_resp is not None and not llm_resp.simulated:
            tokens_used = llm_resp.tokens_input + llm_resp.tokens_output
            cost_usd = llm_resp.cost_usd
            summary_content = llm_resp.content
            simulated = False
            provider_used = llm_resp.provider
        else:
            (
                tokens_used,
                cost_usd,
                summary_content,
                simulated,
                provider_used,
            ) = PipelineOrchestrator._compute_simulated_fields(
                task, token_divisor, model, pipeline, module_id, model_version, sanitized_title
            )

        artifact_keys = [a.artifact_key for a in (prior_artifacts or [])]
        raw_output = {
            "module_id": module_id,
            "pipeline": pipeline,
            "model": model,
            "model_version": model_version,
            "task_id": task.task_id,
            "simulated": simulated,
            "provider": provider_used,
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "summary": summary_content,
            "prior_artifact_keys": artifact_keys,
            "skill_context": skill_context if skill_context else "",
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

    def on_init(self, lifecycle_mgr: LifecycleManager) -> None:
        """LifecycleManager 回调：初始化后注册 Pipeline 组件。"""
        self._lifecycle_mgr = lifecycle_mgr
        try:
            from zephyr.shared.infra.observer import Observer

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
                self._log(
                    "WARN", f"on_shutdown: {len(self._active_dispatches)} dispatches still active after 30s, forcing"
                )
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
        active_preemptions = self._preempt_mgr.active_count
        cb_open = self._cb_manager.open_count

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
            "dead_letters": self._dlq.count,
            "cost_total_usd": round(self._cost_tracker.total_cost(), 4),
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
                health["warning"] = (
                    f"Failure ratio {failure_ratio:.2%} exceeds threshold {self._cfg.health_critical_failure_ratio:.2%}"
                )

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
        if self._telemetry is not None and hasattr(self._telemetry, "ai_behavior"):
            try:
                self._telemetry.ai_behavior.record(
                    decision="pipe_route",
                    model=node_id,
                    reason=task_type,
                )
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞遥测记录失败（指标丢失不可见）
                logger.debug("telemetry ai_behavior.record failed for task_type=%s", task_type, exc_info=True)
        label = f"decision_{task_type}_{node_id}"
        self._metrics[label] = self._metrics.get(label, 0) + 1

    def _record_telemetry_latency(self, task_type: str, latency_ms: float) -> None:
        """记录路由延迟（pipe_routing_latency_ms histogram 采样）。"""
        if self._telemetry is not None and hasattr(self._telemetry, "metrics"):
            try:
                self._telemetry.metrics.histogram(
                    f"pipe_routing_latency_{task_type}",
                    latency_ms,
                )
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞延迟遥测失败（指标丢失不可见）
                logger.debug("telemetry metrics.histogram failed for task_type=%s", task_type, exc_info=True)
        key = f"latency_{task_type}"
        if key not in self._latency_samples:
            self._latency_samples[key] = []
        self._latency_samples[key].append(latency_ms)

    def _record_zone_crossing(self, from_zone: str, to_zone: str) -> None:
        """记录跨区事件（pipe_zone_crossing_count）。"""
        if self._telemetry is not None and hasattr(self._telemetry, "metrics"):
            try:
                self._telemetry.metrics.counter(
                    "pipe_zone_crossing",
                    tags={"from": from_zone, "to": to_zone},
                )
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞跨区遥测失败（指标丢失不可见）
                logger.debug("telemetry metrics.counter failed for %s->%s", from_zone, to_zone, exc_info=True)
        label = f"zone_{from_zone}->{to_zone}"
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
        """直接调用 EventBusBackpressure 发布 TASK_EVENT（F14 统一，不再走 Observer 抽象层）。"""
        try:
            from datetime import UTC, datetime

            from zephyr.shared.event_bus import EventBusBackpressure

            payload: dict[str, Any] = {
                "task_id": task_id,
                "event_type": "TASK_EVENT",
                "from_status": from_status,
                "to_status": to_status,
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "PipelineOrchestrator",
            }
            EventBusBackpressure().emit("TASK_EVENT", payload=payload)
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞 TASK_EVENT 发布失败（状态变更信号丢失）
            logger.debug("EventBus TASK_EVENT emit failed for task=%s %s->%s", task_id, from_status, to_status, exc_info=True)

    # ------------------------------------------------------------------
    # Zone Crossing 防线 —— B70（AP2: A区->B区 M6边界标记校验）
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
                    f"ZONE-CROSSING VIOLATION: A区{prev_module_id}->B区{next_module_id}"
                    f" 未经M5打包和M6边界标记（AP2）——policy:[A区产出物不得直接流入B区]"
                )
            else:
                self._record_zone_crossing("A", "B")

        return warnings

    # ------------------------------------------------------------------
    # LSG 安全闸门集成 —— B131（MOD-LLM_SECURITY LLM Security Gateway）
    # ------------------------------------------------------------------

    @staticmethod
    def _lsg_sanitize_input(text: str) -> str:
        """L0-L2+L5 输入检测：sanitize prompt 内容.

        懒加载 LSG——模块不存在时优雅降级为透传.
        层防御：
          - L0: 供应链安全（模型验证/依赖扫描）
          - L1: Prompt injection 检测（DAN/角色扮演/ignore instructions）
          - L2: Prompt 保护（防泄露/话题边界）
          - L5: 资源保护（Token预算/速率限制）

        fail-closed: LSG 运行时异常 -> 返回 [LSG-BLOCKED] 标记，不静默透传.
        """
        try:
            import asyncio

            from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway, SecurityDecision

            if PipelineOrchestrator._lsg_gateway is None:
                with PipelineOrchestrator._lsg_gateway_lock:
                    if PipelineOrchestrator._lsg_gateway is None:
                        PipelineOrchestrator._lsg_gateway = LSGSecurityGateway()
            gw = PipelineOrchestrator._lsg_gateway
            # 5.100.5 修复: 原 run_coroutine_threadsafe + future.result() 在 loop 线程内调用会死锁
            # (get_running_loop 成功=当前在 loop 线程, future.result 阻塞 loop 线程但协程需在 loop 上执行)
            # run_sync 统一处理: 无运行 loop->asyncio.run; 有运行 loop->新线程+新 loop
            result = run_sync(gw.scan_input(text, source="PipelineOrchestrator"))
            if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
                return f"[LSG-BLOCKED] {text[:200]}"
            return text
        except ImportError:
            return text
        except Exception:
            return f"[LSG-BLOCKED] {text[:200]}"

    @staticmethod
    def _lsg_sanitize_output(module_id: str, output: dict) -> dict:
        """L3+L6 输出检测：sanitize 模型输出.

        懒加载 LSG——模块不存在时优雅降级为透传.
        层防御：
          - L3: 敏感信息脱敏（PII/credential 模式匹配）+ 有害内容过滤
          - L6: 可观测性（安全日志/异常告警）

        fail-closed: LSG 运行时异常 -> 输出字段替换为 [LSG-BLOCKED]，不静默透传.
        """
        try:
            import asyncio

            from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway
            from zephyr.shared.contracts.security import SecurityDecision

            if PipelineOrchestrator._lsg_gateway is None:
                with PipelineOrchestrator._lsg_gateway_lock:
                    if PipelineOrchestrator._lsg_gateway is None:
                        PipelineOrchestrator._lsg_gateway = LSGSecurityGateway()
            gw = PipelineOrchestrator._lsg_gateway
            for key in ("summary", "verdict", "detail", "minority_report"):
                if key in output and isinstance(output[key], str):
                    # 5.100.6 修复: 同 _lsg_sanitize_input, run_coroutine_threadsafe+future.result 死锁
                    result = run_sync(
                        gw.scan_output(
                            output[key],
                            source=f"Pipeline.{module_id}",
                        )
                    )
                    if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
                        output[key] = f"[LSG-BLOCKED] {output[key][:200]}"
            return output
        except ImportError:
            import logging

            logging.getLogger("pipeline.lsg").warning(
                "LSG Security Gateway (MOD-LLM_SECURITY) not available — output sanitization skipped (fail-open). "
                "Install: pip install -e . or verify src/zephyr/llm-security/ exists."
            )
            return output
        except Exception:
            for key in ("summary", "verdict", "detail", "minority_report"):
                if key in output and isinstance(output[key], str):
                    output[key] = f"[LSG-BLOCKED] {output[key][:200]}"
            return output

    @staticmethod
    def _lsg_scan_agent_action(tool_name: str, tool_params: dict) -> str | None:
        """L4+L5+L8 Agent动作安全扫描.

        懒加载 LSG——模块不存在时优雅降级为放行.
        层防御：
          - L4: Agent安全（权限/HITL/金融合规）
          - L5: 资源保护（Token预算/速率限制）
          - L8: 多Agent安全（跨Agent权限/信任链）

        Returns: blocked_by layer name if blocked, None if allowed.
        """
        try:
            import asyncio
            import json

            from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway
            from zephyr.shared.contracts.security import SecurityDecision

            if PipelineOrchestrator._lsg_gateway is None:
                with PipelineOrchestrator._lsg_gateway_lock:
                    if PipelineOrchestrator._lsg_gateway is None:
                        PipelineOrchestrator._lsg_gateway = LSGSecurityGateway()
            gw = PipelineOrchestrator._lsg_gateway
            text = json.dumps(tool_params, ensure_ascii=False) if tool_params else tool_name
            # 5.100.7 修复: 同 _lsg_sanitize_input, run_coroutine_threadsafe+future.result 死锁
            result = run_sync(
                gw.scan_agent_action(
                    text=text,
                    tool_name=tool_name,
                    tool_params=tool_params,
                    metadata={"source": "PipelineOrchestrator"},
                )
            )
            if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
                return result.blocked_by or "lsg_agent_scan"
            return None
        except ImportError:
            return None
        except Exception:
            return "lsg_exception_fail_closed"

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
          3. -> 标记为 warn；三模(hypothetical Claude rescue)均一致 -> critical

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
                detail_parts.append(f"任务标题: {task_card.title[:80]}")
                detail_parts.append("建议: 引入 Cross-Encoder reranker 或 adversarial prompt 打破同质化")

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
                    minority_report=f"verdict一致({m3_verdict!r})但摘要差异度={1 - sim:.1%}",
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

        优先使用 BudgetEngine.pre_flight_check()；若不可用则回退到本地简单检查。
        """
        try:
            engine = self._budget_engine
            if engine is None:
                from zephyr.governance.ops_governance.budget_engine import BudgetEngine

                engine = BudgetEngine()
            result = engine.pre_flight_check(
                operation_id=f"pipeline-{task_card.task_id}",
                estimated_tokens=_DEFAULT_TOKEN_BUDGET // 10,
                estimated_cost=0.01,
            )
            from zephyr.governance.ops_governance.budget_models import GateDecision

            if result.decision is GateDecision.DENY:
                self._log(
                    "WARN",
                    f"BudgetEngine DENY: {result.reason} (remaining_daily={result.remaining_daily})",
                )
                return False, (
                    f"BUDGET-DENY: {result.reason}; "
                    f"remaining_daily={result.remaining_daily}. Task {task_card.task_id} blocked by BudgetEngine."
                )
            if result.decision in (GateDecision.DEGRADE, GateDecision.NARROW):
                return True, f"BUDGET-WARN: {result.reason}; tier={result.model_tier}"
            return True, ""
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞预算门禁决策失败（预算失控不可见）
            logger.warning("BudgetEngine decision failed for task=%s", task_card.task_id, exc_info=True)

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
        生产环境应接入 RBAC 系统（MOD-CONTEXT_ENGINE）验证角色分配。
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
        ts = now_utc().isoformat()
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

    def _rbac_check(self, task_card: TaskCard) -> RBACCheckResult | None:
        """G-CT-005：管线前置 RBAC 权限检查.

        RBAC 不可用时返回 None（通过），不阻塞管线.
        """
        if self._rbac_bridge is None:
            return None
        return self._rbac_bridge.pre_execute_check(
            session_id=task_card.task_id,
            operation=f"pipeline.{task_card.assigned_pipeline}",
            target_path=task_card.source_blueprint or "",
        )

    def _write_audit_event(
        self,
        task_id: str,
        operation: str,
        status: str,
        details: dict | None = None,
    ) -> None:
        """G-CT-001：写入不可变审计日志."""
        if self._audit_writer is None:
            return
        try:
            self._audit_writer.write(
                {
                    "task_id": task_id,
                    "operation": operation,
                    "status": status,
                    "details": details or {},
                }
            )
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞审计写入失败（审计链断链不可见）
            logger.warning("audit_writer.write failed for task=%s op=%s", task_id, operation, exc_info=True)

    # ------------------------------------------------------------------
    # Circuit Breaker —— B151（对标 Netflix Hystrix），委托至 CircuitBreakerManager（SRC-0024）
    # ------------------------------------------------------------------

    def reset_circuit_breakers(self) -> int:
        """重置所有断路器到 CLOSED 状态。返回重置数量。"""
        return self._cb_manager.reset_all()

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
    # 死信队列 —— B169（委托到 DeadLetterQueue）
    # ------------------------------------------------------------------

    def _maybe_dead_letter(
        self,
        task_card: TaskCard,
        results: list[ModuleResult],
        status: PipelineStatus,
    ) -> DeadLetterEntry | None:
        """永久失败任务写入死信队列。"""
        return self._dlq.enqueue(task_card, results, status, self._cfg.max_retries)

    def get_dead_letters(self) -> list[DeadLetterEntry]:
        return self._dlq.entries

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
        if "infra_ops" in tags_lower or "infrastructure" in tags_lower:
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
    # G6 蓝图合规检查 —— Phase 2 硬合规 (T-V2-011 G6)
    # ------------------------------------------------------------------

    def _check_g6_blueprint_compliance(self, task_card: TaskCard, modules: list[str]) -> str | None:
        """G6 Phase 2 硬合规——AI 在修改代码前 MUST 已读对应蓝图。

        检查逻辑：
        1. 从 TaskCard 提取目标文件路径
        2. 通过 BlueprintSearchServer 定位相关的蓝图
        3. 查询 blueprint_reads.jsonl 确认蓝图已被读取
        4. 若 hard_compliance=true 且未读 -> 返回 violation 消息（阻断 dispatch）
        5. 若已读 -> 返回 None（PASS）

        返回 None 表示通过，返回 str 表示 G6-BLOCKED 原因。
        """
        try:
            from zephyr.shared.protocols.a2a.layer3_coordination import BlueprintSearchServer
        except ImportError:
            return None

        if not self._cfg.g6_enabled:
            return None

        # pytest 环境自动跳过 G6（测试不需要蓝图合规）
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return None

        task_desc = getattr(task_card, "description", "") or task_card.title or ""
        all_files: list[str] = []
        for sf in getattr(task_card, "source_files", []) or []:
            all_files.append(str(sf))

        server = BlueprintSearchServer()
        search_result = server._find_relevant_blueprint(task_desc, num_results=3)

        candidates = search_result.get("results", [])
        if not candidates:
            return None

        metrics_path = REPO_ROOT / "data" / "telemetry" / "blueprint_reads.jsonl"
        if not metrics_path.exists():
            return (
                f"G6-BLOCKED: No blueprint_reads.jsonl found ({metrics_path}). "
                f"AI MUST call blueprint_search.find_relevant_blueprint() BEFORE code change. "
                f"Top blueprint: {candidates[0].get('blueprint_id', 'N/A')}"
            )

        read_blueprints = _load_read_blueprint_ids(metrics_path)
        if read_blueprints is None:
            return f"G6-BLOCKED: Cannot read {metrics_path}. Confirm blueprint_read instrumentation is active."

        missing = _compute_missing_blueprint_ids(candidates, read_blueprints)
        if missing:
            return _format_g6_violation(missing, candidates, task_desc)
        return None

    # ------------------------------------------------------------------
    # 成本统计公开 API
    # ------------------------------------------------------------------

    def get_cost_summary(self) -> dict[str, Any]:
        return self._cost_tracker.summary()


# ── EventBusBackpressure 订阅 (DM-2507-E) ──────────────────────────────

_subscribed = False


def subscribe_eventbus() -> None:
    """订阅 EventBusBackpressure 的 pipeline_start 事件。

    幂等：重复调用安全。Backpressure 总线不可用时静默跳过。
    供 boot_hooks 统一调用。

    说明: pipeline_start 事件到达时仅记录日志——
    真正的 dispatch 需要完整 TaskCard，由调用方主动触发，
    不从事件 payload 幻觉构造 TaskCard 以避免数据损坏。
    """
    global _subscribed
    if _subscribed:
        return
    try:
        from zephyr.shared.event_bus import EventBusBackpressure

        bus = EventBusBackpressure()
        bus.subscribe("pipeline_start", _on_pipeline_start)
        _subscribed = True
        logger.info("PipelineOrchestrator: subscribed to pipeline_start event")
    except Exception as e:
        logger.warning("PipelineOrchestrator: subscribe_eventbus failed: %s", e, exc_info=True)


def _on_pipeline_start(payload: object) -> None:
    """pipeline_start 事件：管线启动信号。轻量handler——仅日志记录。

    payload 期望字段: {timestamp, source_function, severity, detail}
    真正的 dispatch 由调用方主动触发（需完整 TaskCard）。
    """
    try:
        data = payload if isinstance(payload, dict) else {}
        detail = data.get("detail", str(payload))
        source = data.get("source_function", "unknown")
        logger.info(
            "PipelineOrchestrator: pipeline_start event received "
            "(source=%s, detail=%s) — dispatch deferred to caller",
            source,
            detail,
        )
    except Exception as e:
        logger.error("PipelineOrchestrator: _on_pipeline_start failed: %s", e, exc_info=True)