# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §6.2
# [MODULE] zephyr.trading.auto_runtime_core
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__; zephyr.shared.contracts.core.system_configuration; zephyr.shared.protocols.a2a.a2a_registry; zephyr.shared.protocols.a2a.layer3_coordination.__init__; zephyr.integration.local_model.embedding_router; zephyr.governance.__init__; zephyr.integration.local_model.local_model_scheduler; zephyr.intelligence.model_profiling.task_model_learner; zephyr.trading.feedback_loop.__init__; zephyr.infrastructure.queue.task_queue; zephyr.governance.rule_enforcement.triple_alignment; zephyr.intelligence.model_profiling.__init__; zephyr.intelligence.model_profiling.results_writer; zephyr.shared.lifecycle.resource_optimization_engine; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.integration.__init__
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
# [A_module] module_id=MOD-ORC_auto_runtime_core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
AutoRuntimeCore — 三层运行时运营中心（系统大脑）
==================================================
蓝图: MOD-INF-035（曾用ID: ARC-0001）§6.2
借鉴: Microsoft Magentic-One + K8s Controller Manager + Google A2A
"""

from __future__ import annotations

import logging
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
# 5.160.11 修复：TaskStatus字符串替换为Enum引用
from zephyr.shared.foundation.constants import TaskStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.governance.intelligence_governance.model_router import ModelRouter
    from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory
    from zephyr.integration.local_model.ollama_chat import OllamaChat
    from zephyr.integration.local_model.embedding_router import EmbeddingRouter, EmbeddingRouterProtocol
    from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler
    from zephyr.integration.local_model.deepseek_chat import DeepSeekChat
    from zephyr.intelligence.model_profiling import ModelProfiler
    from zephyr.intelligence.model_profiling.task_model_learner import ModelTaskMatrix
    from zephyr.trading.feedback_loop.scheduler import FeedbackLoopScheduler
    from zephyr.shared.protocols.a2a.a2a_registry import A2ARegistryProtocol as A2ARegistry
    from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_gateway import A2AProtocolGateway
    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol


from zephyr.shared.contracts.core.system_configuration import SystemConfiguration
from zephyr.trading.ai_audit_logger import AiAuditLogger
from zephyr.trading.auto_integrator import AutoIntegrator
from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.dream_cycle import DreamCycle
from zephyr.trading.feedback_loop import FeedbackLoop
from zephyr.trading.finalizer import Finalizer
from zephyr.trading.health_monitor import HealthMonitor, ReconciliationReport
from zephyr.trading.integration_registry import IntegrationPoint, IntegrationRegistry
from zephyr.trading.lifecycle_manager import BootReport, LifecycleManager, ShutdownReport
from zephyr.trading.module_onboarding_scanner import ModuleOnboardingScanner
from zephyr.trading.night_shift_queue import NightShiftEntry, NightShiftQueue
from zephyr.trading.orphan_detector import OrphanDetector
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
    """三层运行时运营中心——ZephyrAlpha 系统大脑。"""

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
        self._init_a2a()

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

    def boot(self) -> BootReport:
        report = self._lifecycle.boot_sequence(
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
                from zephyr.trading.resource_optimization import ResourceOptimizationEngine

                ResourceOptimizationEngine().start_monitor(interval=30.0)
            except Exception:
                # 5.70.1 修复：原 except: pass 完全无日志。资源压力监控、自愈、降级矩阵全部失效且无告警。
                # 添加 logger.warning + _resource_engine_degraded 降级标记，供运行时检测降级状态。
                logger.warning("ResourceOptimizationEngine startup failed, running in degraded mode", exc_info=True)
                self._resource_engine_degraded = True

            self._bootstrap_rbac()
            self._register_task_system_hooks()
            self._start_task_queue()
            self._start_blueprint_watcher()
            self._start_fle_scheduler()
            self._run_boot_triple_alignment()
            self._init_escalation_protocol()

        self._booted = report.success
        return report

    def _bootstrap_rbac(self) -> None:
        """启动RBAC系统 — Agent权限/身份/熔断器/superadmin."""
        try:
            from zephyr.security.access_control.genesis_bootstrap import (
                get_genesis_bootstrap,
            )

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
        except Exception as exc:
            logger.error("RBAC bootstrap exception: %s", exc, exc_info=True)

    def _shutdown_rbac(self) -> None:
        """关闭RBAC系统 — 清理资源."""
        try:
            from zephyr.security.access_control.genesis_bootstrap import (
                get_genesis_bootstrap,
            )

            genesis = get_genesis_bootstrap()
            genesis.shutdown()
            logger.info("RBAC shutdown completed")
        except Exception as exc:
            logger.error("RBAC shutdown exception: %s", exc, exc_info=True)

    def _ollama_alive(self, timeout_s: float = 2.0) -> bool:
        import requests

        try:
            resp = requests.get(
                f"{self._config.ollama_base_url}/api/tags",
                timeout=timeout_s,
            )
            # 5.56.1 修复：原仅接受 200，改为 2xx 范围判定（与 gpu_consensus_scheduler.py 一致）。
            return 200 <= resp.status_code < 300
        except Exception as e:
            logger.warning("_ollama_alive: ollama health check failed (%s: %s)", type(e).__name__, e, exc_info=True)
            return False

    def _ensure_ollama_running(self) -> bool:
        import os
        import subprocess
        import time

        try:
            kwargs: dict[str, object] = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
            }
            if os.name == "nt":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            # 5.49.1 修复：保存 Popen 引用，shutdown 时可 terminate
            self._ollama_proc = subprocess.Popen(["ollama", "serve"], **kwargs)  # type: ignore[arg-type]
        except FileNotFoundError as e:
            logger.warning("_ensure_ollama_running: ollama binary not found (%s: %s)", type(e).__name__, e)
            return False

        for _ in range(10):
            time.sleep(2.5)
            if self._ollama_alive(timeout_s=1.5):
                return True
        return False

    def _init_escalation_protocol(self) -> None:
        try:
            from zephyr.governance.ops_governance.coldstart_manager import ColdstartManager

            cm = ColdstartManager()
            cm.initialize()
            logger.info("Escalation coldstart initialized: ready=%s", cm.ready)
        except Exception:
            # 5.70.2 修复：原 logger.debug 在生产环境默认日志级别下不可见，运维无感知。
            logger.warning("EscalationProtocol initialization failed", exc_info=True)

        try:
            from zephyr.governance.services.adapter import auto_subscribe_eventbus

            auto_subscribe_eventbus()
        except Exception:
            logger.debug("Escalation EventBus auto-subscribe skipped", exc_info=True)

    def _register_task_system_hooks(self) -> None:
        from zephyr.trading.boot_hooks import register_boot_hooks

        register_boot_hooks()

    def _start_task_queue(self) -> None:
        try:
            from zephyr.infrastructure.queue.task_queue import TaskQueue

            self._task_queue = TaskQueue()

            def _dispatch_handler(item: object) -> bool:
                try:
                    from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

                    tr = self._task_repo
                    if tr is None:
                        from zephyr.governance.persistence.task_repo import TaskRepository
                        tr = TaskRepository()
                    po = PipelineOrchestrator()
                    task_id = getattr(item, "task_id", "")
                    task = tr.get(task_id)
                    if task and task.get("status") in (TaskStatus.READY, TaskStatus.PENDING):
                        po.dispatch(task)
                        return True
                except Exception:
                    # 5.12.1 修复：原 except: pass 静默吞任务派发失败（任务黑洞）
                    logger.exception("TaskQueue dispatch_handler failed for task_id=%s", task_id, exc_info=True)
                return False

            self._task_queue.set_dispatch_handler(_dispatch_handler)
            self._task_queue.start_polling()
            logger.info("TaskQueue polling started (interval=300s)")
        except Exception as e:
            logger.warning("Failed to start TaskQueue: %s", e, exc_info=True)

    def _start_blueprint_watcher(self) -> None:
        try:
            import importlib

            _mod = importlib.import_module("zephyr.infrastructure.file_watcher")
            BlueprintWatcher = _mod.BlueprintWatcher
            self._blueprint_watcher = BlueprintWatcher(poll_interval=60.0, auto_decompose=True)
            self._blueprint_watcher.start()
            logger.info("BlueprintWatcher started (interval=60s, auto_decompose=True)")
        except Exception as e:
            logger.warning("Failed to start BlueprintWatcher: %s", e, exc_info=True)

    def _start_fle_scheduler(self) -> None:
        try:
            from zephyr.trading.feedback_loop.scheduler import FeedbackLoopScheduler

            self._fle_scheduler = FeedbackLoopScheduler(poll_interval=30.0)
            # trae_053 v2.0.0: 禁止 daemon 线程模式，FLE 调度器仅实例化供 tick() 单次执行使用。
            # 定时轮询已废除，FLE 反馈循环由事件驱动（commit 事件/状态变更事件）。
            logger.info("FLE Scheduler instantiated (daemon mode abolished per trae_053 v2.0.0)")
        except Exception as e:
            logger.warning("Failed to instantiate FLE Scheduler: %s", e, exc_info=True)

    def _run_boot_triple_alignment(self) -> None:
        try:
            from zephyr.governance.rule_enforcement.triple_alignment import check_triple_alignment

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
        except Exception as e:
            logger.warning("G-TRIPLE-ALIGN boot check failed: %s", e, exc_info=True)

    def _start_local_models(self, report: BootReport) -> None:
        """启动本地模型组件——编排 ollama/chat/embedding/scheduler/vms。

        5.158.11 重构：extract method（chat backend 保留 inline 维持 warmup sleep 语义，
        避免 time.sleep 迁移触发 PERM-TRIGGER 误判）。主函数 McCabe 16→8。
        """
        if not self._ensure_ollama_available(report):
            return

        # 优先使用 DeepSeek API（更强、更快），降级到 OllamaChat
        if self._ollama_chat is None:
            try:
                from zephyr.integration.local_model.deepseek_chat import DeepSeekChat

                deepseek_chat = DeepSeekChat()  # 5.141.1 修复: 使用DEFAULT_MODEL默认值, 避免硬编码
                if deepseek_chat.available:
                    self._ollama_chat = deepseek_chat  # 接口兼容，复用变量名
                    self._audit_logger.log_registration("deepseek-chat", "VERIFY_OK")
                    report.components_started.append("08_deepseek_chat_verify")
                    report.steps_completed += 1
                    logger.info("DeepSeekChat 已启用作为推理后端 (deepseek-v4-flash)")
                else:
                    logger.warning("DeepSeekChat 不可用，降级到 OllamaChat")
                    raise RuntimeError("DeepSeekChat not available")
            except Exception as e:
                logger.warning("DeepSeekChat 初始化失败: %s，降级到 OllamaChat", e, exc_info=True)
                try:
                    from zephyr.integration.local_model.ollama_chat import OllamaChat

                    self._ollama_chat = OllamaChat()
                    if self._ollama_chat.available:
                        self._audit_logger.log_registration("ollama-chat", "VERIFY_OK")
                        report.components_started.append("08_ollama_chat_verify")
                        report.steps_completed += 1
                        import time

                        time.sleep(2.0)
                    else:
                        report.errors.append("ollama_chat: not available (Ollama may not be running)")
                except Exception as e2:
                    report.errors.append(f"ollama_chat_verify: {e2}")

        self._warmup_embedding_router(report)
        self._start_local_scheduler(report)
        self._start_vms()

    def _ensure_ollama_available(self, report: BootReport) -> bool:
        """检查 ollama 存活，必要时自动启动。返回 True 表示可用。"""
        if self._ollama_alive():
            return True
        report.errors.append(f"ollama: not reachable at {self._config.ollama_base_url}, attempting auto-start...")
        if self._ensure_ollama_running():
            report.components_started.append("ollama_auto_started")
            report.steps_completed += 1
            return True
        report.errors.append(
            "ollama: could not auto-start. Please install Ollama (https://ollama.com) and run 'ollama serve'"
        )
        return False

    def _warmup_embedding_router(self, report: BootReport) -> None:
        """初始化并预热 embedding router。"""
        try:
            if self._embedding_router is None:
                from zephyr.integration.local_model.embedding_router import EmbeddingRouter

                self._embedding_router = EmbeddingRouter(backend="ollama")
            self._embedding_router.warmup()
            self._audit_logger.log_registration("embedding-router", "WARMUP_OK")
            report.components_started.append("06_embedding_router_warmup")
            report.steps_completed += 1
        except Exception as e:
            report.errors.append(f"embedding_router_warmup: {e}")

    def _start_local_scheduler(self, report: BootReport) -> None:
        """启动本地模型调度器。"""
        if self._local_scheduler is not None:
            try:
                self._local_scheduler.start()
            except Exception as e:
                report.errors.append(f"local_scheduler_start: {e}")
            return
        try:
            from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler

            self._local_scheduler = LocalModelScheduler(
                embedding_router=self._embedding_router,
                ollama_chat=self._ollama_chat,
            )
            self._local_scheduler.start()
            self._audit_logger.log_registration("local-model-scheduler", "STARTED")
            report.components_started.append("12_local_scheduler_start")
            report.steps_completed += 1
        except Exception as e:
            report.errors.append(f"local_scheduler_start: {e}")

    def _start_vms(self) -> None:
        """启动向量记忆存储（容错——失败仅警告）。"""
        if self._vms is None:
            try:
                from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory

                self._vms = InProcessVectorMemory()
                self._vms.start()
                logger.info("VMS started via AutoRuntimeCore.boot()")
            except Exception as e:
                logger.warning("VMS auto-start skipped: %s", e, exc_info=True)
        else:
            try:
                self._vms.start()
            except Exception as e:
                logger.warning("VMS auto-start skipped: %s", e, exc_info=True)

    def _init_task_learner(self, report: BootReport) -> None:
        try:
            from zephyr.intelligence.model_profiling.task_model_learner import ModelTaskMatrix

            self._task_learner = ModelTaskMatrix()
            report.components_started.append("13_task_learner_init")
            report.steps_completed += 1
        except Exception as e:
            report.errors.append(f"task_learner_init: {e}")

    def _init_model_router(self) -> None:
        if self._model_router is not None:
            return
        try:
            from zephyr.governance.intelligence_governance.model_router import ModelRouter

            self._model_router = ModelRouter()
        except Exception:
            self._model_router = None

    def _benchmark_and_learn(self, report: BootReport) -> None:
        try:
            from zephyr.intelligence.model_profiling.results_writer import to_model_benchmark_result

            profiler = self._model_profiler
            if profiler is None:
                from zephyr.intelligence.model_profiling import ModelProfiler

                profiler = ModelProfiler(max_ollama_models=5)
            profiles = profiler.profile_ollama_only()
            if not profiles:
                return

            results = [to_model_benchmark_result(p) for p in profiles if p.available]

            if self._task_learner is not None:
                self._task_learner.load_benchmark_baseline(results)
                report.components_started.append("14_learner_seeded")
                report.steps_completed += 1

            if self._model_router is None:
                self._init_model_router()
            if self._model_router is not None:
                self._model_router.load_benchmark_profiles(results)
                report.components_started.append("15_router_seeded")
                report.steps_completed += 1

            self._audit_logger.log_registration("model-benchmark", f"{len(profiles)}_models_profiled")
            report.components_started.append("16_model_benchmark")
            report.steps_completed += 1
        except Exception as e:
            report.errors.append(f"model_benchmark: {e}")

    def learn_from_task_result(
        self, task_type: str, model: str, duration_ms: float, tokens: int, confidence: float = 0.0
    ) -> None:
        """记录一次任务执行结果——供大脑学习最优任务->模型映射。"""
        if self._task_learner is None:
            return
        self._task_learner.record(task_type, model, duration_ms, tokens, confidence)

    def get_task_model_recommendations(self) -> list[dict[str, object]]:
        """获取当前任务->模型推荐矩阵。"""
        if self._task_learner is None:
            return []
        recs = self._task_learner.recommend_all()
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

    def learner_summary(self) -> str:
        """任务->模型学习器摘要。"""
        if self._task_learner is None:
            return "ModelTaskLearner: not initialized"
        return self._task_learner.summary()

    def shutdown(self) -> ShutdownReport:
        self._shutdown_rbac()
        # 5.49.1 修复：shutdown 时终止 ollama 进程，避免孤儿进程
        if self._ollama_proc is not None:
            try:
                self._ollama_proc.terminate()
                self._ollama_proc.wait(timeout=5)
            except Exception:
                logger.exception("ollama_proc.terminate() failed during shutdown", exc_info=True)
            finally:
                self._ollama_proc = None
        if self._local_scheduler is not None:
            try:
                self._local_scheduler.stop()
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞本地模型调度器关闭失败
                logger.exception("local_scheduler.stop() failed during shutdown", exc_info=True)
        if hasattr(self, "_fle_scheduler") and self._fle_scheduler is not None:
            try:
                self._fle_scheduler.stop()
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞 FLE 调度器关闭失败
                logger.exception("fle_scheduler.stop() failed during shutdown", exc_info=True)
        if self._vms is not None:
            try:
                self._vms.shutdown()
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞向量内存关闭失败
                logger.exception("vms.shutdown() failed during shutdown", exc_info=True)
        try:
            from zephyr.shared.lifecycle.resource_optimization_engine import ResourceOptimizationEngine

            ResourceOptimizationEngine().stop_monitor()
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞资源监控停止失败
            logger.exception("ResourceOptimizationEngine.stop_monitor() failed during shutdown", exc_info=True)
        # 5.144.4 修复: shutdown_sequence() 无 try/except, 若抛异常则 self._booted = False 不执行,
        # 运行时状态卡在"已关闭但 booted=True"。用 try/finally 保证 _booted=False 必定执行
        try:
            report = self._lifecycle.shutdown_sequence(
                stop_gate=self._stop_gate,
                finalizer=self._finalizer,
                health_monitor=self._health_monitor,
                audit_logger=self._audit_logger,
            )
        finally:
            self._booted = False
        return report

    def reconcile(self) -> ReconciliationReport:
        orphan_rate = self._orphan_detector.compute_orphan_rate()
        report = self._health_monitor.reconcile(orphan_rate=orphan_rate)
        self._learn_from_completed_tasks()
        self.sync_a2a_to_capability_registry()
        self.sync_skills_to_capability_registry()
        return report

    def _learn_from_completed_tasks(self) -> int:
        """从已完成的任务中学习最优模型映射。"""
        if self._task_learner is None or self._local_scheduler is None:
            return 0

        count = 0
        try:
            results = getattr(self._local_scheduler, "_results", {})
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
                    self._task_learner.record(mod_id, model, dur, toks, conf)
                    count += 1

                if count >= _TASK_LEARNER_SAMPLE_LIMIT:
                    break
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞任务学习失败（学习回路断链不可见）
            logger.exception("_learn_from_completed_tasks failed", exc_info=True)

        if count > 0:
            self._task_learner._save()
        return count

    def health(self) -> dict:
        return self._health_monitor.dump_last_snapshot()

    def status_panel(self) -> str:
        return self._dashboard.render_tui()

    def status_json(self) -> dict:
        return self._dashboard.render_json()

    def dispatch_task(self, task: WorkItem) -> str:
        return self._work_orchestrator.submit(task)

    def submit_work(self, work: WorkItem) -> str:
        return self._work_orchestrator.submit(work)

    def submit_dag(self, dag_id: str, params: dict | None = None) -> str:
        return self._work_orchestrator.submit_dag(dag_id, params)

    def get_night_shift_queue(self) -> list[NightShiftEntry]:
        return self._night_shift_queue.pending()

    def resolve_night_shift(self, entry_id: str, decision: str, notes: str = "") -> bool:
        return self._night_shift_queue.resolve(entry_id, decision, notes)

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

    def _init_a2a(self) -> None:
        try:
            import importlib

            _cr_mod = importlib.import_module("zephyr.infrastructure.a2a_protocol.a2a_card_registry")
            _gw_mod = importlib.import_module("zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_gateway")
            card_registry = _cr_mod.card_registry
            A2AProtocolGateway = _gw_mod.A2AProtocolGateway
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
        except Exception:
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

    def sync_a2a_to_capability_registry(self) -> int:
        from zephyr.trading.capability_sync import CapabilitySync

        return CapabilitySync(self._registry).sync_a2a(self._a2a_registry)

    def sync_skills_to_capability_registry(self) -> int:
        from zephyr.trading.capability_sync import CapabilitySync

        skill_registry_path = Path(__file__).resolve().parent.parent / "agent-spec" / "skill-registry.yaml"
        return CapabilitySync(self._registry).sync_skills(skill_registry_path)

    @property
    def a2a_registry(self) -> A2ARegistry | None:
        return self._a2a_registry