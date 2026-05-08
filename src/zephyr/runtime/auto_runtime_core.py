"""
AutoRuntimeCore — 三层运行时运营中心（系统大脑）
==================================================
蓝图: ARC-0001 §6.2
借鉴: Microsoft Magentic-One + K8s Controller Manager + Google A2A
"""

from __future__ import annotations

from typing import Any


from zephyr.runtime.ai_audit_logger import AiAuditLogger
from zephyr.runtime.auto_integrator import AutoIntegrator
from zephyr.runtime.capability_registry import CapabilityRegistry
from zephyr.runtime.circadian_scheduler import CircadianScheduler
from zephyr.runtime.dream_cycle import DreamCycle
from zephyr.runtime.feedback_loop import FeedbackLoop
from zephyr.runtime.finalizer import Finalizer
from zephyr.runtime.health_monitor import HealthMonitor, ReconciliationReport
from zephyr.runtime.integration_registry import IntegrationRegistry, IntegrationPoint
from zephyr.runtime.lifecycle_manager import BootReport, LifecycleManager, ShutdownReport
from zephyr.runtime.module_onboarding_scanner import ModuleOnboardingScanner
from zephyr.runtime.night_shift_queue import NightShiftEntry, NightShiftQueue
from zephyr.runtime.orphan_detector import OrphanDetector
from zephyr.runtime.runtime_config import RuntimeConfig
from zephyr.runtime.status_dashboard import StatusDashboard
from zephyr.runtime.stop_gate import StopGate
from zephyr.runtime.work_dag import WorkItem
from zephyr.runtime.work_orchestrator import WorkOrchestrator


class AutoRuntimeCore:
    """三层运行时运营中心——ZephyrAlpha 系统大脑。"""

    def __init__(self, config: RuntimeConfig | None = None) -> None:
        self._config = config or RuntimeConfig()
        self._config.ensure_dirs()

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
        self._circadian_scheduler = CircadianScheduler(self._config.circadian_state_path)
        self._finalizer = Finalizer()
        self._lifecycle = LifecycleManager(self._config)

        src_root = self._config.capability_card_dir.parent.parent / "src" / "zephyr"
        bp_root = self._config.capability_card_dir.parent.parent / "architecture-model"
        self._scanner = ModuleOnboardingScanner(src_root, bp_root, self._registry)
        self._auto_integrator = AutoIntegrator(self._registry, self._config.max_daily_l3_activations)
        self._orphan_detector = OrphanDetector(self._scanner, self._registry)

        self._dashboard = StatusDashboard(
            registry=self._registry,
            health_monitor=self._health_monitor,
            night_shift_queue=self._night_shift_queue,
            work_orchestrator=self._work_orchestrator,
            circadian_scheduler=self._circadian_scheduler,
            orphan_detector=self._orphan_detector,
        )

        self._a2a_registry: Any = None
        self._a2a_protocol_gateway: Any = None
        self._init_a2a()

        self._booted = False
        self._local_scheduler: Any = None
        self._embedding_router: Any = None
        self._ollama_chat: Any = None
        self._task_learner: Any = None
        self._model_router: Any = None

    def boot(self) -> BootReport:
        report = self._lifecycle.boot_sequence(
            audit_logger=self._audit_logger,
            registry=self._registry,
            night_shift_queue=self._night_shift_queue,
            health_monitor=self._health_monitor,
            integration_registry=self._integration_registry,
            work_orchestrator=self._work_orchestrator,
            circadian_scheduler=self._circadian_scheduler,
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
                from zephyr.shared.lifecycle.resource_optimization_engine import ResourceOptimizationEngine
                ResourceOptimizationEngine().start_monitor(interval=30.0)
            except Exception:
                pass

        self._booted = report.success
        return report

    def _ollama_alive(self, timeout_s: float = 2.0) -> bool:
        import requests
        try:
            resp = requests.get(
                f"{self._config.ollama_base_url}/api/tags",
                timeout=timeout_s,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def _ensure_ollama_running(self) -> bool:
        import subprocess
        import os
        import time

        try:
            kwargs: dict[str, object] = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
            }
            if os.name == "nt":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            subprocess.Popen(["ollama", "serve"], **kwargs)  # type: ignore[arg-type]
        except FileNotFoundError:
            return False

        for _ in range(10):
            time.sleep(2.5)
            if self._ollama_alive(timeout_s=1.5):
                return True
        return False

    def _start_local_models(self, report: BootReport) -> None:
        if not self._ollama_alive():
            report.errors.append(
                f"ollama: not reachable at {self._config.ollama_base_url}, attempting auto-start..."
            )
            if self._ensure_ollama_running():
                report.components_started.append("ollama_auto_started")
                report.steps_completed += 1
            else:
                report.errors.append(
                    "ollama: could not auto-start. "
                    "Please install Ollama (https://ollama.com) and run 'ollama serve'"
                )
                return

        try:
            from zephyr.vector_memory.ollama_chat import OllamaChat
            self._ollama_chat = OllamaChat()
            if self._ollama_chat.available:
                self._audit_logger.log_registration("ollama-chat", "VERIFY_OK")
                report.components_started.append("08_ollama_chat_verify")
                report.steps_completed += 1
                import time
                time.sleep(2.0)
            else:
                report.errors.append("ollama_chat: not available (Ollama may not be running)")
        except Exception as e:
            report.errors.append(f"ollama_chat_verify: {e}")

        try:
            from zephyr.vector_memory.embedding_router import EmbeddingRouter
            self._embedding_router = EmbeddingRouter(backend="ollama")
            self._embedding_router.warmup()
            self._audit_logger.log_registration("embedding-router", "WARMUP_OK")
            report.components_started.append("06_embedding_router_warmup")
            report.steps_completed += 1
        except Exception as e:
            report.errors.append(f"embedding_router_warmup: {e}")

        try:
            from zephyr.vector_memory.local_model_scheduler import LocalModelScheduler
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

    def _init_task_learner(self, report: BootReport) -> None:
        try:
            from zephyr.pipeline.model_profiler.task_model_learner import ModelTaskMatrix
            self._task_learner = ModelTaskMatrix()
            report.components_started.append("13_task_learner_init")
            report.steps_completed += 1
        except Exception as e:
            report.errors.append(f"task_learner_init: {e}")

    def _init_model_router(self) -> None:
        try:
            from zephyr.budget_enforcer.model_router import ModelRouter
            self._model_router = ModelRouter()
        except Exception:
            self._model_router = None

    def _benchmark_and_learn(self, report: BootReport) -> None:
        try:
            from zephyr.pipeline.model_profiler import ModelProfiler
            from zephyr.pipeline.model_profiler.results_writer import to_model_benchmark_result

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
        """记录一次任务执行结果——供大脑学习最优任务→模型映射。"""
        if self._task_learner is None:
            return
        self._task_learner.record(task_type, model, duration_ms, tokens, confidence)

    def get_task_model_recommendations(self) -> list[dict[str, object]]:
        """获取当前任务→模型推荐矩阵。"""
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
        """任务→模型学习器摘要。"""
        if self._task_learner is None:
            return "ModelTaskLearner: not initialized"
        return self._task_learner.summary()

    def shutdown(self) -> ShutdownReport:
        if self._local_scheduler is not None:
            try:
                self._local_scheduler.stop()
            except Exception:
                pass
        try:
            from zephyr.shared.lifecycle.resource_optimization_engine import ResourceOptimizationEngine
            ResourceOptimizationEngine().stop_monitor()
        except Exception:
            pass
        report = self._lifecycle.shutdown_sequence(
            stop_gate=self._stop_gate,
            circadian_scheduler=self._circadian_scheduler,
            finalizer=self._finalizer,
            health_monitor=self._health_monitor,
            audit_logger=self._audit_logger,
        )
        self._booted = False
        return report

    def reconcile(self) -> ReconciliationReport:
        orphan_rate = self._orphan_detector.compute_orphan_rate()
        report = self._health_monitor.reconcile(orphan_rate=orphan_rate)
        self._learn_from_completed_tasks()
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

                if count >= 50:
                    break
        except Exception:
            pass

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
            from zephyr.l01_infrastructure.a2a_protocol import card_registry
            from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_gateway import A2AProtocolGateway
            self._a2a_registry = card_registry
            self._a2a_protocol_gateway = A2AProtocolGateway()
            self._integration_registry.register(IntegrationPoint(
                point_id="a2a-protocol",
                target_system="A2AProtocol",
                interface="zephyr.l01_infrastructure.a2a_protocol:card_registry",
                protocol="python_import",
                sla="best_effort",
                status="CONNECTED",
            ))
            self._audit_logger.log_registration("a2a-protocol", "INIT_OK")
        except Exception as e:
            self._integration_registry.register(IntegrationPoint(
                point_id="a2a-protocol",
                target_system="A2AProtocol",
                interface="zephyr.l01_infrastructure.a2a_protocol:card_registry",
                protocol="python_import",
                sla="best_effort",
                status="DISCONNECTED",
            ))

    def sync_a2a_to_capability_registry(self) -> int:
        if self._a2a_registry is None:
            return 0
        synced = 0
        try:
            from zephyr.runtime.capability_card import CapabilityCard, CapabilityCategory
            for card in self._a2a_registry._cards.values():
                cap_id = f"a2a-agent-{card.agent_id}"
                existing = self._registry.get(cap_id)
                if existing is None:
                    cap_card = CapabilityCard(
                        capability_id=cap_id,
                        name=f"A2A Agent: {card.name}",
                        category=CapabilityCategory.SEARCH,
                        description=card.description,
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                        tags=["a2a-agent", card.agent_id] + [c.value for c in card.capabilities],
                        priority="P2",
                        runtime_plane="warm",
                        requires_human=False,
                    )
                    self._registry.register(cap_card)
                    synced += 1
        except Exception:
            pass
        return synced

    @property
    def a2a_registry(self) -> Any:
        return self._a2a_registry
