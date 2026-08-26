# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §6.2
# [MODULE] zephyr.trading.auto_runtime_core
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__; zephyr.shared.contracts.core.system_configuration; zephyr.shared.protocols.a2a.a2a_registry; zephyr.shared.protocols.a2a.layer3_coordination.__init__; zephyr.integration.local_model.embedding_router; zephyr.governance.__init__; zephyr.integration.local_model.local_model_scheduler; zephyr.intelligence.model_profiling.task_model_learner; zephyr.feedback_loop.__init__; zephyr.infrastructure.queue.task_queue; zephyr.gov_enforcement.rule_enforcement.triple_alignment; zephyr.intelligence.model_profiling.__init__; zephyr.intelligence.model_profiling.results_writer; zephyr.trading.resource_optimization; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.integration.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: boot/shutdown阶段的一次性等待(time.sleep等待ollama启动稳定/proc.wait(timeout)等待子进程终止),非周期轮询循环
"""
AutoRuntimeCore — 三层运行时运营中心（系统大脑）
==================================================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
借鉴: Microsoft Magentic-One + K8s Controller Manager + Google A2A
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING

import requests

# 5.160.11 修复：TaskStatus字符串替换为Enum引用
from zephyr.shared.foundation.constants import TaskStatus
from zephyr.shared.infra.process_pool import spawn_python_hidden
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

if TYPE_CHECKING:
    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol
    from zephyr.shared.protocols.a2a.a2a_registry import A2ARegistryProtocol as A2ARegistry


# 5.174-M5 治本：原函数内延迟 import 经 import 探针逐一验证无真实循环（目标模块
# 均不传递性引用本模块），全部提升为模块级 import；重复延迟 import 合并为单 import。
# 各函数内 try/except 保留——守护的是运行时实例化/外部资源（ollama/DB/网络），非 import。
from zephyr.feedback_loop import FeedbackLoop
from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler
from zephyr.gov_enforcement.rule_enforcement.triple_alignment import check_triple_alignment
from zephyr.governance.intelligence_governance.model_router import ModelRouter
from zephyr.governance.ops_governance.coldstart_manager import ColdstartManager
from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.governance.services.adapter import auto_subscribe_eventbus
from zephyr.infrastructure.a2a_protocol.a2a_card_registry import card_registry
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_gateway import A2AProtocolGateway
from zephyr.infrastructure.file_watcher import BlueprintWatcher
from zephyr.infrastructure.queue.task_queue import TaskQueue
from zephyr.integration.local_model.deepseek_chat import DeepSeekChat
from zephyr.integration.local_model.embedding_router import EmbeddingRouter, EmbeddingRouterProtocol
from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler
from zephyr.integration.local_model.ollama_chat import OllamaChat
from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator
from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory
from zephyr.intelligence.model_profiling import ModelProfiler
from zephyr.intelligence.model_profiling.results_writer import load_latest_benchmark_results
from zephyr.intelligence.model_profiling.task_model_learner import ModelTaskMatrix
from zephyr.security.access_control.genesis_bootstrap import get_genesis_bootstrap
from zephyr.shared.contracts.core.system_configuration import SystemConfiguration
from zephyr.shared.event_bus import EventBus, EventType
from zephyr.trading.ai_audit_logger import AiAuditLogger
from zephyr.trading.auto_integrator import AutoIntegrator
from zephyr.trading.boot_hooks import register_boot_hooks
from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.capability_sync import CapabilitySync
from zephyr.trading.dream_cycle import DreamCycle
from zephyr.trading.finalizer import Finalizer
from zephyr.trading.health_monitor import HealthMonitor, ReconciliationReport
from zephyr.trading.integration_registry import IntegrationPoint, IntegrationRegistry
from zephyr.trading.lifecycle_manager import BootReport, LifecycleManager, ShutdownReport
from zephyr.trading.module_onboarding_scanner import ModuleOnboardingScanner
from zephyr.trading.night_shift_queue import NightShiftEntry, NightShiftQueue
from zephyr.trading.orphan_detector import OrphanDetector
from zephyr.trading.resource_optimization import ResourceOptimizationEngine
from zephyr.trading.runtime_config import RuntimeConfig, ensure_runtime_dirs
from zephyr.trading.status_dashboard import StatusDashboard
from zephyr.trading.stop_gate import StopGate
from zephyr.trading.work_dag import WorkItem
from zephyr.trading.work_orchestrator import WorkOrchestrator

logger = logging.getLogger(__name__)

# 5.137.1 修复：魔数提取为命名常量
_OLLAMA_POLL_MAX_ATTEMPTS = 10
_OLLAMA_POLL_INTERVAL_S = 2.5
# 5.137.2 修复：任务学习器采样上限魔数
_TASK_LEARNER_SAMPLE_LIMIT = 50


class AutoRuntimeCore:
    """三层运行时运营中心——ZephyrAlpha 系统大脑。

    5.150.2 God Class 治本：4 个高内聚零耦合职责簇已提取为同文件协作者类
    （置于本类之后，见文件末尾协作者注释块）——
    ollama 进程生命周期（_OllamaProcessManager）、本地模型栈启动编排（_LocalModelBootstrap）、
    boot 子系统注册（_BootSubsystemRegistrar）、任务-模型学习（_TaskModelLearning）。
    公共 API 零变化：簇内方法由本类同名薄封装委托（实例级 patch 面不变），状态保留在
    本类实例上（测试直接读写），协作者仅经 core 参数读写、不反向持有引用。
    boot/shutdown 编排、组件装配、RBAC 生命周期、状态面板/任务分发/夜班/A2A 访问器
    与单例状态/调用顺序/副作用深度交织，不外移，理由见各职责分区注释块。
    """

    # ── 组件装配区（交织保留：16 个子系统实例化 + module-level patch 面） ──
    # 保留理由：装配顺序即依赖拓扑（registry→orchestrator→dashboard→scanner），
    # 且测试 patch zephyr.trading.auto_runtime_core.<Name> 模块级类名，移出即断 patch 面。
    def __init__(
        self,
        config: RuntimeConfig | None = None,
        system_config: SystemConfiguration | None = None,
        embedding_router: EmbeddingRouterProtocol | None = None,
        ollama_chat: OllamaChat | None = None,
        local_scheduler: LocalModelScheduler | None = None,
        vms: InProcessVectorMemory | None = None,
        model_router: ModelRouter | None = None,
        model_profiler: ModelProfiler | None = None,
        task_repo: TaskRepositoryProtocol | None = None,
    ) -> None:
        self._config = config or RuntimeConfig()
        self._system_config = system_config
        ensure_runtime_dirs(self._config)

        self._audit_logger = AiAuditLogger(self._config.audit_log_dir)
        self._registry = CapabilityRegistry(self._config.capability_card_dir)
        self._night_shift_queue = NightShiftQueue(self._config.night_shift_storage_path)
        self._stop_gate = StopGate()
        self._dream_cycle = DreamCycle(self._config.dream_archive_dir, self._config.audit_log_dir)
        self._feedback_loop = FeedbackLoop(self._config.feedback_proposal_dir)
        self._health_monitor = HealthMonitor(self._config.health_snapshot_dir)
        self._integration_registry = IntegrationRegistry()
        self._work_orchestrator = WorkOrchestrator(
            self._registry,
            dag_dir=self._config.work_dag_dir,
            max_parallel_l1=self._config.max_parallel_l1,
            max_parallel_l2=self._config.max_parallel_l2,
            max_parallel_l3=self._config.max_parallel_l3,
        )
        self._finalizer = Finalizer()
        self._lifecycle = LifecycleManager(self._config)

        src_root = self._config.capability_card_dir.parent.parent / "src" / "zephyr"
        bp_root = self._config.capability_card_dir.parent.parent / "architecture_model"
        self._scanner = ModuleOnboardingScanner(src_root, bp_root, self._registry)
        self._auto_integrator = AutoIntegrator(self._registry, self._config.max_daily_l3_activations)
        self._orphan_detector = OrphanDetector(self._scanner, self._registry)

        self._dashboard = StatusDashboard(
            registry=self._registry,
            health_monitor=self._health_monitor,
            night_shift_queue=self._night_shift_queue,
            work_orchestrator=self._work_orchestrator,
            orphan_detector=self._orphan_detector,
        )

        self._a2a_registry: A2ARegistry | None = None
        self._a2a_protocol_gateway: A2AProtocolGateway | None = None
        self.init_a2a()

        self._booted = False
        self._local_scheduler: LocalModelScheduler | None = local_scheduler
        self._fle_scheduler: FeedbackLoopScheduler | None = None
        self._embedding_router: EmbeddingRouter | None = embedding_router
        self._ollama_chat: OllamaChat | None = ollama_chat
        self._ollama_proc: object | None = None  # 5.49.1 修复：保存 Popen 引用避免孤儿进程
        self._task_learner: ModelTaskMatrix | None = None
        self._model_router: ModelRouter | None = model_router
        self._vms: InProcessVectorMemory | None = vms
        self._model_profiler: ModelProfiler | None = model_profiler
        self._task_repo: TaskRepositoryProtocol | None = task_repo

    # ── Stage 4 公共化属性（property getter/setter） ──
    @property
    def lifecycle(self) -> LifecycleManager:
        """只读：lifecycle（Stage 4 公共化）。"""
        return self._lifecycle

    @lifecycle.setter
    def lifecycle(self, value):
        """写入：lifecycle（Stage 4 公共化）。"""
        self._lifecycle = value

    @property
    def booted(self) -> bool:
        """Stage 4 公共化。"""
        return self._booted

    @booted.setter
    def booted(self, value: bool) -> None:
        self._booted = value

    @property
    def fle_scheduler(self) -> FeedbackLoopScheduler | None:
        """Stage 4 公共化。"""
        return self._fle_scheduler

    @fle_scheduler.setter
    def fle_scheduler(self, value: FeedbackLoopScheduler | None) -> None:
        self._fle_scheduler = value

    @property
    def local_scheduler(self) -> LocalModelScheduler | None:
        """Stage 4 公共化。"""
        return self._local_scheduler

    @local_scheduler.setter
    def local_scheduler(self, value: LocalModelScheduler | None) -> None:
        self._local_scheduler = value

    @property
    def vms(self) -> InProcessVectorMemory | None:
        """Stage 4 公共化。"""
        return self._vms

    @vms.setter
    def vms(self, value: InProcessVectorMemory | None) -> None:
        self._vms = value

    @property
    def registry(self) -> CapabilityRegistry:
        """只读：registry（Stage 4 公共化）。"""
        return self._registry

    @registry.setter
    def registry(self, value):
        """写入：registry（Stage 4 公共化）。"""
        self._registry = value

    @property
    def audit_logger(self) -> AiAuditLogger:
        """Stage 4 公共化。"""
        return self._audit_logger

    @audit_logger.setter
    def audit_logger(self, value: AiAuditLogger) -> None:
        self._audit_logger = value

    @property
    def night_shift_queue(self) -> NightShiftQueue:
        """只读：night_shift_queue（Stage 4 公共化）。"""
        return self._night_shift_queue

    @night_shift_queue.setter
    def night_shift_queue(self, value):
        """写入：night_shift_queue（Stage 4 公共化）。"""
        self._night_shift_queue = value

    @property
    def dream_cycle(self) -> DreamCycle:
        """只读：dream_cycle（Stage 4 公共化）。"""
        return self._dream_cycle

    @dream_cycle.setter
    def dream_cycle(self, value):
        """写入：dream_cycle（Stage 4 公共化）。"""
        self._dream_cycle = value

    @property
    def health_monitor(self) -> HealthMonitor:
        """只读：health_monitor（Stage 4 公共化）。"""
        return self._health_monitor

    @health_monitor.setter
    def health_monitor(self, value):
        """写入：health_monitor（Stage 4 公共化）。"""
        self._health_monitor = value

    @property
    def task_learner(self) -> ModelTaskMatrix | None:
        """Stage 4 公共化。"""
        return self._task_learner

    @task_learner.setter
    def task_learner(self, value: ModelTaskMatrix | None) -> None:
        self._task_learner = value

    @property
    def ollama_chat(self) -> OllamaChat | None:
        """Stage 4 公共化。"""
        return self._ollama_chat

    @ollama_chat.setter
    def ollama_chat(self, value: OllamaChat | None) -> None:
        self._ollama_chat = value

    @property
    def embedding_router(self) -> EmbeddingRouter | None:
        """Stage 4 公共化。"""
        return self._embedding_router

    @embedding_router.setter
    def embedding_router(self, value: EmbeddingRouter | None) -> None:
        self._embedding_router = value

    # ── boot 编排区（交织保留：调用顺序即语义） ──
    # 保留理由：boot_sequence→L2 模型栈→benchmark→资源引擎→RBAC→子系统注册 的顺序
    # 与 report 累积语义/_booted 状态翻转/降级标记深度交织，是纯编排而非职责簇。
    def boot(self) -> BootReport:
        report = self.lifecycle.boot_sequence(
            audit_logger=self._audit_logger,
            registry=self._registry,
            night_shift_queue=self._night_shift_queue,
            health_monitor=self._health_monitor,
            integration_registry=self._integration_registry,
            work_orchestrator=self._work_orchestrator,
            dream_cycle=self._dream_cycle,
            feedback_loop=self._feedback_loop,
            stop_gate=self._stop_gate,
            finalizer=self._finalizer,
        )

        if report.success and self._config.auto_start_l2:
            self._start_local_models(report)

        if report.success and self._ollama_chat is not None:
            self._init_task_learner(report)
            self._benchmark_and_learn(report)

        if report.success:
            try:
                ResourceOptimizationEngine().start_monitor(interval=30.0)
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                # 5.70.1 修复：原 except: pass 完全无日志。资源压力监控、自愈、降级矩阵全部失效且无告警。
                # 添加 logger.warning + _resource_engine_degraded 降级标记，供运行时检测降级状态。
                logger.warning("ResourceOptimizationEngine startup failed, running in degraded mode", exc_info=True)
                self._resource_engine_degraded = True

            self._bootstrap_rbac()
            self.register_task_system_cron_jobs()
            self.register_task_system_hooks()
            self.start_task_queue()
            self.start_blueprint_watcher()
            self.start_fle_scheduler()
            self.run_boot_triple_alignment()
            self.init_escalation_protocol()

        self.booted = report.success
        return report

    # ── RBAC 生命周期区（交织保留：boot 成功末段启动 / shutdown 最先关闭） ──
    # 保留理由：仅 2 个方法且与 boot/shutdown 编排顺序强耦合（启动顺序敏感：
    # RBAC 必须在所有子系统就绪后 bootstrap、在任何清理前 shutdown），量小不独立成簇。
    def _bootstrap_rbac(self) -> None:
        """启动RBAC系统 — Agent权限/身份/熔断器/superadmin."""
        try:
            genesis = get_genesis_bootstrap()
            state = genesis.bootstrap(config={"version": "0.14.0"})
            if state.is_ready:
                logger.info(
                    "RBAC bootstrap COMPLETED: phase=%s checks=%d/%d progress=%.0f%%",
                    state.phase.value,
                    state.checks_passed,
                    state.total_checks,
                    state.progress * 100,
                )
            else:
                logger.error(
                    "RBAC bootstrap FAILED: phase=%s error=%s",
                    state.phase.value,
                    state.error,
                )
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("RBAC bootstrap exception: %s", exc, exc_info=True)

    def _shutdown_rbac(self) -> None:
        """关闭RBAC系统 — 清理资源."""
        try:
            genesis = get_genesis_bootstrap()
            genesis.shutdown()
            logger.info("RBAC shutdown completed")
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("RBAC shutdown exception: %s", exc, exc_info=True)

    # ── ollama 进程生命周期（委托 _OllamaProcessManager） ──
    def ollama_alive(self, timeout_s: float = 2.0) -> bool:
        """Stage 4 公共化，primary。"""
        return _OllamaProcessManager.ollama_alive(self._config.ollama_base_url, timeout_s)

    def _ollama_alive(self, timeout_s: float = 2.0) -> bool:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.ollama_alive(timeout_s)

    def ensure_ollama_running(self) -> bool:
        """Stage 4 公共化，primary。"""
        return _OllamaProcessManager.ensure_running(self)

    def _ensure_ollama_running(self) -> bool:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.ensure_ollama_running()

    def _ensure_ollama_available(self, report: BootReport) -> bool:
        """检查 ollama 存活，必要时自动启动。返回 True 表示可用。"""
        return _OllamaProcessManager.ensure_available(self, report)

    # ── boot 子系统注册（委托 _BootSubsystemRegistrar） ──
    def init_escalation_protocol(self) -> None:
        """Stage 4 公共化，primary。"""
        return _BootSubsystemRegistrar.init_escalation_protocol(self)

    def _init_escalation_protocol(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.init_escalation_protocol()

    def register_task_system_cron_jobs(self) -> None:
        """Stage 4 公共化，primary。注册任务系统定时作业的残留事件订阅（容错——失败仅告警，不阻断 boot）。

        历史：原 boot_cron_jobs.register_boot_cron_jobs 已于 2026-06-26 裁定随
        CircadianScheduler 定时调度机制一并废除；本方法保留为 boot 流程钩子，
        注册任务系统残留的事件订阅（EventBus 任务生命周期事件），满足项目铁律
        "永久系统必须全自动（自动触发/运行/维护/关闭）"——定时调度虽废除，但任务
        系统仍需通过事件订阅自动响应任务状态变更。
        """
        return _BootSubsystemRegistrar.register_task_system_cron_jobs(self)

    def _register_task_system_cron_jobs(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.register_task_system_cron_jobs()

    def register_task_system_hooks(self) -> None:
        """Stage 4 公共化，primary。"""
        return _BootSubsystemRegistrar.register_task_system_hooks(self)

    def _register_task_system_hooks(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.register_task_system_hooks()

    def start_task_queue(self) -> None:
        """Stage 4 公共化，primary。"""
        return _BootSubsystemRegistrar.start_task_queue(self)

    def _start_task_queue(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.start_task_queue()

    def start_blueprint_watcher(self) -> None:
        """Stage 4 公共化，primary。"""
        return _BootSubsystemRegistrar.start_blueprint_watcher(self)

    def _start_blueprint_watcher(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.start_blueprint_watcher()

    def start_fle_scheduler(self) -> None:
        """Stage 4 公共化，primary。"""
        return _BootSubsystemRegistrar.start_fle_scheduler(self)

    def _start_fle_scheduler(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.start_fle_scheduler()

    def run_boot_triple_alignment(self) -> None:
        """Stage 4 公共化，primary。"""
        return _BootSubsystemRegistrar.run_boot_triple_alignment(self)

    def _run_boot_triple_alignment(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.run_boot_triple_alignment()

    # ── 本地模型栈启动编排（委托 _LocalModelBootstrap） ──
    def start_local_models(self, report: BootReport) -> None:
        """Stage 4 公共化，primary。启动本地模型组件——编排 ollama/chat/embedding/scheduler/vms。

        5.158.11 重构：extract method（chat backend 保留 inline 维持 warmup sleep 语义，
        避免 time.sleep 迁移触发 PERM-TRIGGER 误判）。主函数 McCabe 16→8。
        """
        return _LocalModelBootstrap.start_local_models(self, report)

    def _start_local_models(self, report: BootReport) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.start_local_models(report)

    def _warmup_embedding_router(self, report: BootReport) -> None:
        """初始化并预热 embedding router。"""
        return _LocalModelBootstrap.warmup_embedding_router(self, report)

    def _start_local_scheduler(self, report: BootReport) -> None:
        """启动本地模型调度器。"""
        return _LocalModelBootstrap.start_local_scheduler(self, report)

    def _start_vms(self) -> None:
        """启动向量记忆存储（容错——失败仅警告）。"""
        return _LocalModelBootstrap.start_vms(self)

    # ── 任务-模型学习（委托 _TaskModelLearning） ──
    def _init_task_learner(self, report: BootReport) -> None:
        return _TaskModelLearning.init_task_learner(self, report)

    def _init_model_router(self) -> None:
        return _TaskModelLearning.init_model_router(self)

    def _benchmark_and_learn(self, report: BootReport) -> None:
        return _TaskModelLearning.benchmark_and_learn(self, report)

    def learn_from_task_result(
        self, task_type: str, model: str, duration_ms: float, tokens: int, confidence: float = 0.0
    ) -> None:
        """记录一次任务执行结果——供大脑学习最优任务->模型映射。"""
        return _TaskModelLearning.learn_from_task_result(self, task_type, model, duration_ms, tokens, confidence)

    def get_task_model_recommendations(self) -> list[dict[str, object]]:
        """获取当前任务->模型推荐矩阵。"""
        return _TaskModelLearning.get_task_model_recommendations(self)

    def learner_summary(self) -> str:
        """任务->模型学习器摘要。"""
        return _TaskModelLearning.learner_summary(self)

    def _learn_from_completed_tasks(self) -> int:
        """从已完成的任务中学习最优模型映射。"""
        return _TaskModelLearning.learn_from_completed_tasks(self)

    # ── 关停编排区（交织保留：关停顺序即语义） ──
    # 保留理由：RBAC→ollama proc→schedulers→vms→资源引擎→lifecycle 的顺序与
    # _booted 状态翻转（try/finally 保证）深度交织，是纯编排而非职责簇。
    def shutdown(self) -> ShutdownReport:
        self._shutdown_rbac()
        # 5.49.1 修复：shutdown 时终止 ollama 进程，避免孤儿进程
        _OllamaProcessManager.terminate_proc(self)
        if self.local_scheduler is not None:
            try:
                self.local_scheduler.stop()
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                # 5.12.1 修复：原 except: pass 静默吞本地模型调度器关闭失败
                logger.exception("local_scheduler.stop() failed during shutdown", exc_info=True)
        if hasattr(self, "fle_scheduler") and self.fle_scheduler is not None:
            try:
                self.fle_scheduler.stop()
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                # 5.12.1 修复：原 except: pass 静默吞 FLE 调度器关闭失败
                logger.exception("fle_scheduler.stop() failed during shutdown", exc_info=True)
        if self.vms is not None:
            try:
                self.vms.shutdown()
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                # 5.12.1 修复：原 except: pass 静默吞向量内存关闭失败
                logger.exception("vms.shutdown() failed during shutdown", exc_info=True)
        try:
            ResourceOptimizationEngine().stop_monitor()
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            # 5.12.1 修复：原 except: pass 静默吞资源监控停止失败
            logger.exception("ResourceOptimizationEngine.stop_monitor() failed during shutdown", exc_info=True)
        # 5.144.4 修复: shutdown_sequence() 无 try/except, 若抛异常则 self._booted = False 不执行,
        # 运行时状态卡在"已关闭但 booted=True"。用 try/finally 保证 _booted=False 必定执行
        try:
            report = self.lifecycle.shutdown_sequence(
                stop_gate=self._stop_gate,
                finalizer=self._finalizer,
                health_monitor=self._health_monitor,
                audit_logger=self._audit_logger,
            )
        finally:
            self.booted = False
        return report

    # ── 对账编排区（交织保留：orphan→reconcile→学习→双 sync 顺序敏感） ──
    def reconcile(self) -> ReconciliationReport:
        orphan_rate = self._orphan_detector.compute_orphan_rate()
        report = self._health_monitor.reconcile(orphan_rate=orphan_rate)
        self._learn_from_completed_tasks()
        self.sync_a2a_to_capability_registry()
        self.sync_skills_to_capability_registry()
        return report

    # ── 状态面板区（已极简薄委托，无簇可提） ──
    def health(self) -> dict:
        return self._health_monitor.dump_last_snapshot()

    def status_panel(self) -> str:
        return self._dashboard.render_tui()

    def status_json(self) -> dict:
        return self._dashboard.render_json()

    # ── 任务分发区（已极简薄委托，无簇可提） ──
    def dispatch_task(self, task: WorkItem) -> str:
        return self._work_orchestrator.submit(task)

    def submit_work(self, work: WorkItem) -> str:
        return self._work_orchestrator.submit(work)

    def submit_dag(self, dag_id: str, params: dict | None = None) -> str:
        return self._work_orchestrator.submit_dag(dag_id, params)

    # ── 夜班队列区（已极简薄委托，无簇可提） ──
    def get_night_shift_queue(self) -> list[NightShiftEntry]:
        return self._night_shift_queue.pending()

    def resolve_night_shift(self, entry_id: str, decision: str, notes: str = "") -> bool:
        return self._night_shift_queue.resolve(entry_id, decision, notes)

    # ── 子系统访问器区（外部消费者直接依赖，保留） ──
    @property
    def capability_registry(self) -> CapabilityRegistry:
        return self._registry

    @property
    def integration_registry(self) -> IntegrationRegistry:
        return self._integration_registry

    @property
    def work_orchestrator(self) -> WorkOrchestrator:
        return self._work_orchestrator

    @property
    def orphan_detector(self) -> OrphanDetector:
        return self._orphan_detector

    @property
    def onboarding_scanner(self) -> ModuleOnboardingScanner:
        return self._scanner

    @property
    def stop_gate(self) -> StopGate:
        return self._stop_gate

    def can_stop(self) -> bool:
        return self._stop_gate.can_stop(
            audit_has_new_entries=not self._audit_logger.has_pending_flush(),
            night_shift_all_resolved=not self._night_shift_queue.has_unresolved(),
            dream_cycle_archived=not self._dream_cycle.needs_archival(),
        )

    # ── A2A 集成区（交织保留：_init_a2a 为 class-level patch 面，sync 已极简） ──
    # 保留理由：全部测试 patch AutoRuntimeCore._init_a2a（类级 patch 面），
    # 两个 sync 方法已是 CapabilitySync 薄委托（2 行），无簇可提。
    def init_a2a(self) -> None:
        """Stage 4 公共化，primary。"""
        try:
            self._a2a_registry = card_registry
            self._a2a_protocol_gateway = A2AProtocolGateway()
            self._integration_registry.register(
                IntegrationPoint(
                    point_id="a2a-protocol",
                    target_system="A2AProtocol",
                    interface="zephyr.infrastructure.a2a_protocol:card_registry",
                    protocol="python_import",
                    sla="best_effort",
                    status="CONNECTED",
                )
            )
            self._audit_logger.log_registration("a2a-protocol", "INIT_OK")
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._integration_registry.register(
                IntegrationPoint(
                    point_id="a2a-protocol",
                    target_system="A2AProtocol",
                    interface="zephyr.infrastructure.a2a_protocol:card_registry",
                    protocol="python_import",
                    sla="best_effort",
                    status="DISCONNECTED",
                )
            )

    def _init_a2a(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.init_a2a()

    def sync_a2a_to_capability_registry(self) -> int:
        return CapabilitySync(self._registry).sync_a2a(self._a2a_registry)

    def sync_skills_to_capability_registry(self) -> int:
        skill_registry_path = Path(__file__).resolve().parent.parent / "agent-spec" / "skill-registry.yaml"
        return CapabilitySync(self._registry).sync_skills(skill_registry_path)

    @property
    def a2a_registry(self) -> A2ARegistry | None:
        return self._a2a_registry

    # ── 三层运行时运营中心（轻量骨架：监控/调度/自愈接口位+最小实现，INF-035 缩减补齐 2026-08-23） ──
    # 补齐口径：不新增子系统、不改动 boot/shutdown 编排（MODIFY-GUARD），仅把既有组件
    # （HealthMonitor / LocalModelScheduler|FeedbackLoopScheduler / ResourceOptimizationEngine）
    # 按"监控/调度/自愈"三层语义暴露统一接口位，供运营面消费。
    def ops_layer(self, name: str) -> object | None:
        """三层运营接口位。name ∈ {monitor, scheduler, self_heal}；未知层 → ValueError。"""
        if name == "monitor":
            return self._health_monitor
        if name == "scheduler":
            return self.local_scheduler or self.fle_scheduler
        if name == "self_heal":
            if getattr(self, "_resource_engine_degraded", False):
                return None
            try:
                return ResourceOptimizationEngine()
            except Exception:  # noqa: BLE001 — 自愈层不可用即降级为 None（fail-visible 经 ops_layers_status）
                logger.warning("ops_layer(self_heal): ResourceOptimizationEngine 不可用", exc_info=True)
                return None
        raise ValueError(f"未知运营层: {name}（monitor/scheduler/self_heal）")

    def ops_layers_status(self) -> dict[str, dict[str, object]]:
        """三层运营状态快照（可用性/组件名/降级标记）。"""
        degraded = bool(getattr(self, "_resource_engine_degraded", False))
        scheduler = self.local_scheduler or self.fle_scheduler
        self_heal = self.ops_layer("self_heal")
        return {
            "monitor": {
                "available": self._health_monitor is not None,
                "component": type(self._health_monitor).__name__ if self._health_monitor is not None else None,
            },
            "scheduler": {
                "available": scheduler is not None,
                "component": type(scheduler).__name__ if scheduler is not None else None,
            },
            "self_heal": {
                "available": self_heal is not None,
                "component": "ResourceOptimizationEngine",
                "degraded": degraded,
            },
        }


# 5.150.2 Extract Class 协作者（God Class 治本：高内聚零耦合职责簇）
#   - 依赖 core 状态的方法由 core 同名薄封装委托（实例级 patch 面不变）
#   - 协作者内部跨方法调用一律经 core 属性查找（core._ollama_alive 等），
#     保留 patch.object(core, "_ollama_alive", ...) 等实例级 patch 拦截点
# 协作者均无状态——配置/子系统句柄/进程引用等状态保留在 core 上（测试直接读写），
# 协作者仅经 core 参数读写，不反向持有引用。
# 置于类后（非试点的前置布局）：NO-GOD-CLASS gate 按 diff added 行检测新 ClassDef，
# 协作者后置保证 AutoRuntimeCore 类行锚定为上文 context（类行不位移、不进 added 行集），
# 门禁确定性通过；运行时安全——薄封装在调用时解析协作者全局名，注解经
# `from __future__ import annotations` 惰性求值。


class _OllamaProcessManager:
    """ollama 进程生命周期协作者（职责簇：存活探测 / 自动启动 / 可用性确保 / 进程终止）。

    仅读写 core._config.ollama_base_url 与 core._ollama_proc，与其余子系统零耦合。
    ensure_available 经 core 属性查找调用 core._ollama_alive / core._ensure_ollama_running，
    实例级 patch（patch.object(core, "_ollama_alive", ...)）语义不变。
    """

    @staticmethod
    def ollama_alive(base_url: str, timeout_s: float = 2.0) -> bool:
        try:
            resp = requests.get(
                f"{base_url}/api/tags",
                timeout=timeout_s,
            )
            # 5.56.1 修复：原仅接受 200，改为 2xx 范围判定（与 gpu_consensus_scheduler.py 一致）。
            return 200 <= resp.status_code < 300
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("_ollama_alive: ollama health check failed (%s: %s)", type(e).__name__, e, exc_info=True)
            return False

    @staticmethod
    def ensure_running(core: AutoRuntimeCore) -> bool:
        try:
            # 5.49.1 修复：保存 Popen 引用，shutdown 时可 terminate
            # TRAE-067 铁律2：复用 process_pool 统一无窗口 spawn 入口
            core._ollama_proc = spawn_python_hidden(["ollama", "serve"])  # type: ignore[arg-type]
        except FileNotFoundError as e:
            logger.warning("_ensure_ollama_running: ollama binary not found (%s: %s)", type(e).__name__, e)
            return False

        for _ in range(10):
            time.sleep(2.5)
            if core._ollama_alive(timeout_s=1.5):
                return True
        return False

    @staticmethod
    def ensure_available(core: AutoRuntimeCore, report: BootReport) -> bool:
        """检查 ollama 存活，必要时自动启动。返回 True 表示可用。"""
        if core._ollama_alive():
            return True
        report.errors.append(f"ollama: not reachable at {core._config.ollama_base_url}, attempting auto-start...")
        if core._ensure_ollama_running():
            report.components_started.append("ollama_auto_started")
            report.steps_completed += 1
            return True
        report.errors.append(
            "ollama: could not auto-start. Please install Ollama (https://ollama.com) and run 'ollama serve'"
        )
        return False

    @staticmethod
    def terminate_proc(core: AutoRuntimeCore) -> None:
        """终止 core._ollama_proc 引用的 ollama 子进程（5.49.1 孤儿进程防护）。"""
        if core._ollama_proc is None:
            return
        try:
            core._ollama_proc.terminate()
            core._ollama_proc.wait(timeout=5)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.exception("ollama_proc.terminate() failed during shutdown", exc_info=True)
        finally:
            core._ollama_proc = None


class _LocalModelBootstrap:
    """本地模型栈启动编排协作者（职责簇：chat backend 选择+降级 / embedding 预热 /
    本地调度器启动 / VMS 启动）。

    仅读写 core 的 _ollama_chat/_embedding_router/_local_scheduler/_vms/_audit_logger，
    DeepSeekChat/OllamaChat/EmbeddingRouter/LocalModelScheduler 经模块级名称解析
    （zephyr.trading.auto_runtime_core.<Name> module-level patch 面不变）。
    """

    @staticmethod
    def l0_supply_chain_verify(core: AutoRuntimeCore, report: BootReport) -> None:
        """L0 启动供应链验证（#255③ / #ARCH-159 缺口落地，2026-08-22 Owner"全部执行"授权）。

        模型加载前调 verify_model/scan_dependencies 并缓存结果（core._l0_verify_results）。
        真源=config/model_digests.yaml（可选）：缺失/空 models 表=跳过不空转；
        dependency_scan.enabled 默认关（pip-audit 子进程上限 60s 不进 boot 热路径）。
        失败语义=fail-visible（report.errors+审计 L0_VERIFY_MISMATCH）不 raise——
        与 boot 既有 errors 收集语义一致，硬阻断属 Owner 政策位。
        """
        core._l0_verify_results = {}
        cfg_path = REPO_ROOT / "config" / "model_digests.yaml"
        if not cfg_path.exists():
            logger.debug("L0 supply chain verify skipped: %s 不存在", cfg_path)
            return
        try:
            import yaml

            from zephyr.security.llm_defense.llm_security.layers.l0_supply_chain import SupplyChainGuard
        except ImportError as e:
            logger.debug("L0 supply chain verify skipped (import): %s", e)
            return
        try:
            cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        except Exception as e:  # noqa: BLE001 — 配置解析失败 fail-visible 不阻断 boot
            report.errors.append(f"l0_supply_chain_verify: config parse failed: {e}")
            return
        results: dict[str, object] = {}
        guard: SupplyChainGuard | None = None
        models = cfg.get("models") or {}
        if models:
            guard = SupplyChainGuard(model_digest_registry=models)
            for path, expected in models.items():
                fp = Path(path)
                if not fp.is_absolute():
                    fp = REPO_ROOT / fp
                r = guard.verify_model(str(fp), expected)
                results[path] = r.status
                if r.status == "verified":
                    core._audit_logger.log_registration(f"l0-model:{path}", "L0_VERIFY_OK")
                else:
                    core._audit_logger.log_registration(f"l0-model:{path}", f"L0_VERIFY_{r.status.upper()}")
                    report.errors.append(f"l0_supply_chain_verify: {path} {r.status}")
        dep_cfg = cfg.get("dependency_scan") or {}
        if dep_cfg.get("enabled"):
            if guard is None:
                guard = SupplyChainGuard()
            deps = guard.scan_dependencies()
            unsafe = [d.name for d in deps if not d.is_safe]
            results["dependency_scan"] = {"scanned": len(deps), "unsafe": unsafe}
            if unsafe:
                report.errors.append(f"l0_supply_chain_verify: unsafe dependencies {unsafe}")
        core._l0_verify_results = results

    @staticmethod
    def start_local_models(core: AutoRuntimeCore, report: BootReport) -> None:
        # L0 供应链验证：模型加载前（#255③，空注册表=零成本跳过）
        _LocalModelBootstrap.l0_supply_chain_verify(core, report)
        # chat backend 选择保留 inline 维持 warmup sleep 语义（5.158.11），
        # 避免 time.sleep 跨文件迁移触发 PERM-TRIGGER 误判。
        if not core._ensure_ollama_available(report):
            return

        # 优先使用 DeepSeek API（更强、更快），降级到 OllamaChat
        if core._ollama_chat is None:
            try:
                deepseek_chat = DeepSeekChat()  # 5.141.1 修复: 使用DEFAULT_MODEL默认值, 避免硬编码
                if deepseek_chat.available:
                    core._ollama_chat = deepseek_chat  # 接口兼容，复用变量名
                    core._audit_logger.log_registration("deepseek-chat", "VERIFY_OK")
                    report.components_started.append("08_deepseek_chat_verify")
                    report.steps_completed += 1
                    logger.info("DeepSeekChat 已启用作为推理后端 (deepseek-v4-flash)")
                else:
                    logger.warning("DeepSeekChat 不可用，降级到 OllamaChat")
                    raise RuntimeError("DeepSeekChat not available")
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("DeepSeekChat 初始化失败: %s，降级到 OllamaChat", e, exc_info=True)
                try:
                    core._ollama_chat = OllamaChat()
                    if core._ollama_chat.available:
                        core._audit_logger.log_registration("ollama-chat", "VERIFY_OK")
                        report.components_started.append("08_ollama_chat_verify")
                        report.steps_completed += 1
                        time.sleep(2.0)
                    else:
                        report.errors.append("ollama_chat: not available (Ollama may not be running)")
                except Exception as e2:  # noqa: BLE001 — 5.135治标: broad exception catch
                    report.errors.append(f"ollama_chat_verify: {e2}")

        core._warmup_embedding_router(report)
        core._start_local_scheduler(report)
        core._start_vms()

    @staticmethod
    def warmup_embedding_router(core: AutoRuntimeCore, report: BootReport) -> None:
        """初始化并预热 embedding router。"""
        try:
            if core._embedding_router is None:
                core._embedding_router = EmbeddingRouter(backend="ollama")
            core._embedding_router.warmup()
            core._audit_logger.log_registration("embedding-router", "WARMUP_OK")
            report.components_started.append("06_embedding_router_warmup")
            report.steps_completed += 1
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            report.errors.append(f"embedding_router_warmup: {e}")

    @staticmethod
    def start_local_scheduler(core: AutoRuntimeCore, report: BootReport) -> None:
        """启动本地模型调度器。"""
        if core.local_scheduler is not None:
            try:
                core.local_scheduler.start()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                report.errors.append(f"local_scheduler_start: {e}")
            return
        try:
            core.local_scheduler = LocalModelScheduler(
                embedding_router=core._embedding_router,
                ollama_chat=core._ollama_chat,
            )
            core.local_scheduler.start()
            core._audit_logger.log_registration("local-model-scheduler", "STARTED")
            report.components_started.append("12_local_scheduler_start")
            report.steps_completed += 1
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            report.errors.append(f"local_scheduler_start: {e}")

    @staticmethod
    def start_vms(core: AutoRuntimeCore) -> None:
        """启动向量记忆存储（容错——失败仅警告）。"""
        if core.vms is None:
            try:
                core.vms = InProcessVectorMemory()
                core.vms.start()
                logger.info("VMS started via AutoRuntimeCore.boot()")
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("VMS auto-start skipped: %s", e, exc_info=True)
        else:
            try:
                core.vms.start()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("VMS auto-start skipped: %s", e, exc_info=True)


class _BootSubsystemRegistrar:
    """boot 子系统注册协作者（职责簇：cron 事件订阅 / boot hooks / TaskQueue /
    BlueprintWatcher / FLE scheduler / triple alignment / escalation protocol）。

    仅读写 core 的 _task_queue/_blueprint_watcher/_fle_scheduler/_task_repo，
    各子系统启动彼此独立（任一失败仅告警不阻断 boot），与 boot 主流程单向耦合。
    """

    @staticmethod
    def init_escalation_protocol(core: AutoRuntimeCore) -> None:
        try:
            cm = ColdstartManager()
            cm.initialize()
            logger.info("Escalation coldstart initialized: ready=%s", cm.ready)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            # 5.70.2 修复：原 logger.debug 在生产环境默认日志级别下不可见，运维无感知。
            logger.warning("EscalationProtocol initialization failed", exc_info=True)

        try:
            auto_subscribe_eventbus()
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("Escalation EventBus auto-subscribe skipped", exc_info=True)

    @staticmethod
    def register_task_system_cron_jobs(core: AutoRuntimeCore) -> None:
        """注册任务系统残留的事件订阅（容错——失败仅告警，不阻断 boot）。"""
        try:
            bus = EventBus.get_instance()

            def _on_task_completed(event: object) -> None:
                """任务完成事件订阅——记录任务完成用于运维可观测性。"""
                task_id = getattr(event, "task_id", "")
                logger.debug("task.completed cron-subscription received: task_id=%s", task_id)

            bus.subscribe(EventType.TASK_COMPLETED, _on_task_completed)
            logger.info("Task system cron jobs (event subscriptions) registered")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            # 容错：事件订阅失败不阻断 boot，运维通过日志感知降级状态
            logger.warning("Failed to register task system cron jobs: %s", e, exc_info=True)

    @staticmethod
    def register_task_system_hooks(core: AutoRuntimeCore) -> None:
        register_boot_hooks()

    @staticmethod
    def start_task_queue(core: AutoRuntimeCore) -> None:
        try:
            core._task_queue = TaskQueue()

            def _dispatch_handler(item: object) -> bool:
                try:
                    tr = core._task_repo
                    if tr is None:
                        tr = TaskRepository()
                    po = PipelineOrchestrator()
                    task_id = getattr(item, "task_id", "")
                    task = tr.get(task_id)
                    if task and task.get("status") in (TaskStatus.READY, TaskStatus.PENDING):
                        po.dispatch(task)
                        return True
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                    # 5.12.1 修复：原 except: pass 静默吞任务派发失败（任务黑洞）
                    logger.exception("TaskQueue dispatch_handler failed for task_id=%s", task_id, exc_info=True)
                return False

            core._task_queue.set_dispatch_handler(_dispatch_handler)
            core._task_queue.start_polling()
            logger.info("TaskQueue polling started (interval=300s)")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("Failed to start TaskQueue: %s", e, exc_info=True)

    @staticmethod
    def start_blueprint_watcher(core: AutoRuntimeCore) -> None:
        try:
            core._blueprint_watcher = BlueprintWatcher(poll_interval=60.0, auto_decompose=True)
            core._blueprint_watcher.start()
            logger.info("BlueprintWatcher started (interval=60s, auto_decompose=True)")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("Failed to start BlueprintWatcher: %s", e, exc_info=True)

    @staticmethod
    def start_fle_scheduler(core: AutoRuntimeCore) -> None:
        try:
            core.fle_scheduler = FeedbackLoopScheduler(poll_interval=30.0)
            # trae_053 v2.0.0: 禁止 daemon 线程模式，FLE 调度器仅实例化供 tick() 单次执行使用。
            # 定时轮询已废除，FLE 反馈循环由事件驱动（commit 事件/状态变更事件）。
            logger.info("FLE Scheduler instantiated (daemon mode abolished per trae_053 v2.0.0)")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("Failed to instantiate FLE Scheduler: %s", e, exc_info=True)

    @staticmethod
    def run_boot_triple_alignment(core: AutoRuntimeCore) -> None:
        try:
            result = check_triple_alignment(warn_only=True)
            errors = [v for v in result.violations if v.severity.value == "ERROR"]
            if errors:
                logger.warning(
                    "G-TRIPLE-ALIGN boot check: %d ERROR, %d WARN across %d modules",
                    len(errors),
                    len(result.violations) - len(errors),
                    result.checked_modules,
                )
            else:
                logger.info(
                    "G-TRIPLE-ALIGN boot check: PASS (%d modules, %d WARN)",
                    result.checked_modules,
                    len(result.violations),
                )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("G-TRIPLE-ALIGN boot check failed: %s", e, exc_info=True)


class _TaskModelLearning:
    """任务-模型学习协作者（职责簇：学习器初始化 / benchmark 播种 / 执行结果记录 /
    推荐矩阵 / 已完成任务采样学习）。

    仅读写 core 的 _task_learner/_model_router/_model_profiler/_local_scheduler/_audit_logger，
    与 boot 编排/子系统注册零耦合（仅在 boot 成功且 ollama_chat 就绪后被调用）。
    """

    @staticmethod
    def init_task_learner(core: AutoRuntimeCore, report: BootReport) -> None:
        try:
            core._task_learner = ModelTaskMatrix()
            report.components_started.append("13_task_learner_init")
            report.steps_completed += 1
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            report.errors.append(f"task_learner_init: {e}")

    @staticmethod
    def init_model_router(core: AutoRuntimeCore) -> None:
        if core._model_router is not None:
            return
        try:
            core._model_router = ModelRouter()
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            core._model_router = None

    @staticmethod
    def benchmark_and_learn(core: AutoRuntimeCore, report: BootReport) -> None:
        """#ARCH-208 治本：benchmark 移出 boot 关键路径。

        启动路径零跑分——仅读取上次落盘的 benchmark 结果（results_writer 持久化层）：
        新鲜→播种 learner/router 供健康判断；缺失/过期→降级"未知"状态不阻断启动。
        跑分本体由独立 CLI 异步执行并落盘：
        ``python -m zephyr.intelligence.model_profiling.cli benchmark``
        """
        try:
            results, meta = load_latest_benchmark_results()
            if not results:
                core._audit_logger.log_registration(
                    "model-benchmark", f"degraded_unknown:{meta.get('state', 'missing')}"
                )
                report.components_started.append("16_model_benchmark_degraded_unknown")
                report.steps_completed += 1
                return

            if core._task_learner is not None:
                core._task_learner.load_benchmark_baseline(results)
                report.components_started.append("14_learner_seeded")
                report.steps_completed += 1

            if core._model_router is None:
                core._init_model_router()
            if core._model_router is not None:
                core._model_router.load_benchmark_profiles(results)
                report.components_started.append("15_router_seeded")
                report.steps_completed += 1

            age_hours = meta.get("age_hours")
            age_txt = f"{age_hours:.1f}h" if isinstance(age_hours, (int, float)) else "unknown"
            core._audit_logger.log_registration(
                "model-benchmark", f"{len(results)}_models_from_cache age={age_txt}"
            )
            report.components_started.append("16_model_benchmark")
            report.steps_completed += 1
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            report.errors.append(f"model_benchmark: {e}")

    @staticmethod
    def learn_from_task_result(
        core: AutoRuntimeCore, task_type: str, model: str, duration_ms: float, tokens: int, confidence: float = 0.0
    ) -> None:
        """记录一次任务执行结果——供大脑学习最优任务->模型映射。"""
        if core._task_learner is None:
            return
        core._task_learner.record(task_type, model, duration_ms, tokens, confidence)

    @staticmethod
    def get_task_model_recommendations(core: AutoRuntimeCore) -> list[dict[str, object]]:
        """获取当前任务->模型推荐矩阵。"""
        if core._task_learner is None:
            return []
        recs = core._task_learner.recommend_all()
        return [
            {
                "task_type": r.task_type,
                "best_model": r.best_model,
                "score": r.score,
                "sample_count": r.sample_count,
                "source": r.source,
                "alternatives": r.alternatives,
            }
            for r in recs
        ]

    @staticmethod
    def learner_summary(core: AutoRuntimeCore) -> str:
        """任务->模型学习器摘要。"""
        if core._task_learner is None:
            return "ModelTaskLearner: not initialized"
        return core._task_learner.summary()

    @staticmethod
    def learn_from_completed_tasks(core: AutoRuntimeCore) -> int:
        """从已完成的任务中学习最优模型映射。"""
        if core._task_learner is None or core.local_scheduler is None:
            return 0

        count = 0
        try:
            results = getattr(core.local_scheduler, "_results", {})
            for tid, task in list(results.items()):
                if getattr(task, "status", "") != "completed":
                    continue
                result = getattr(task, "result", None)
                if result is None:
                    continue
                mod_id = None
                model = None
                dur = 0.0
                toks = 0
                conf = 0.0

                if isinstance(result, dict):
                    mod_id = result.get("module_id")
                    model = result.get("model")
                    dur = float(result.get("duration_ms", 0))
                    toks = int(result.get("tokens_used", 0))
                    conf = float(result.get("confidence", 0))

                if mod_id and model and dur > 0:
                    core._task_learner.record(mod_id, model, dur, toks, conf)
                    count += 1

                if count >= _TASK_LEARNER_SAMPLE_LIMIT:
                    break
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            # 5.12.1 修复：原 except: pass 静默吞任务学习失败（学习回路断链不可见）
            logger.exception("_learn_from_completed_tasks failed", exc_info=True)

        if count > 0:
            core._task_learner._save()
        return count
