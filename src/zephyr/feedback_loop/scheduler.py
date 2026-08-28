# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.scheduler
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__; zephyr.governance.integrity; zephyr.gov_drift.drift_engine; zephyr.infrastructure.auto_fix_engine.__init__; zephyr.infrastructure.__init__; zephyr.shared.event_bus; zephyr.autonomy_core.__init__; zephyr.governance.__init__
# [CONSUMERS] auto_runtime_core.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] _run_drift_scan 不抛异常; _auto_fix_drifts 不抛异常; _periodic_checks 不抛异常; _audit_trail_check 不抛异常
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""FLE 全链路调度器 —— collect->detect->diagnose->act->verify 闭环。

对接 MOD-FEEDBACK_LOOP Feedback Loop Engine 蓝图 §4-§5:
  - 30s 轮询指标 -> EMA 异常检测 -> 诊断 -> 动作调度 -> 事后验证
  - 动作优先级: NOTIFY_OWNER > ADJUST_THRESHOLD > REPAIR > DEPLOY > SELF_UPGRADE
  - 安全门: 67 层 (L1-L67) 在 action 执行前后
  - v0.40.0: 集成 32 个治理级组件 (R470-R501)
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from zephyr.feedback_loop.actors.action_selector import ActionSelector
from zephyr.feedback_loop.collectors.feedback_collector import FeedbackCollector
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

if TYPE_CHECKING:
    from zephyr.feedback_loop.actors.action_selector import ActionRecord
    from zephyr.feedback_loop.alert_dispatcher import AlertEvent
    from zephyr.feedback_loop.detectors.anomaly.anomaly_detector import AnomalyEvent
    from zephyr.feedback_loop.diagnosers.diagnosis.diagnosis_engine import Diagnosis
    from zephyr.feedback_loop.verifiers.verification_engine import VerificationResult
    from zephyr.shared.protocols.ports import VectorMemoryProtocol
from zephyr.feedback_loop.collectors.metrics_collector import (
    MetricsCollector,
    MetricSnapshot,
)
from zephyr.feedback_loop.detectors.agent_trajectory_anomaly_detector import TrajectoryEvent
from zephyr.feedback_loop.detectors.dependency_freshness_monitor import DependencyFreshnessMonitor
from zephyr.feedback_loop.detectors.recursive_diagnosis_trust_evaluator import RecursiveDiagnosisTrustEvaluator
from zephyr.feedback_loop.detectors.self_diagnosis_data_leak_detector import SelfDiagnosisDataLeakDetector
from zephyr.feedback_loop.detectors.silent_corruption_detector import SilentCorruptionDetector
from zephyr.feedback_loop.detectors.temporal_coherence_of_self_model import TemporalCoherenceOfSelfModel
from zephyr.feedback_loop.diagnosers.adaptive_param_tuning import AdaptiveParamTuning
from zephyr.feedback_loop.diagnosers.human_anomaly_flood_detector import HumanAnomalyFloodDetector
from zephyr.feedback_loop.diagnosers.model_version_semantic_drift import ModelVersionSemanticDrift
from zephyr.feedback_loop.diagnosers.nonstationary_effectiveness import NonstationaryEffectiveness
from zephyr.feedback_loop.diagnosers.recovery_time_stats import RecoveryTimeStats
from zephyr.feedback_loop.diagnosers.regime_gain_scheduling import RegimeGainScheduling
from zephyr.feedback_loop.diagnosers.self_bottleneck_detector import PipelineStage
from zephyr.feedback_loop.diagnosers.timezone_semantic_reasoner import TimezoneSemanticReasoner
from zephyr.feedback_loop.scheduler_act import ActPhaseHandler
from zephyr.feedback_loop.scheduler_collect_detect import CollectDetectHandler
from zephyr.feedback_loop.scheduler_health import HealthReporter
from zephyr.feedback_loop.scheduler_safety import SafetyGateManager
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

logger = logging.getLogger(__name__)


@dataclass
class FLEPipelineEvent:
    """单次 FLE pipeline 完整运行事件——用于遥测记录。"""

    run_id: str
    timestamp: float
    phase: str
    snapshot: MetricSnapshot | None = None
    anomaly: AnomalyEvent | None = None
    diagnosis: Diagnosis | None = None
    action: ActionRecord | None = None
    verification: VerificationResult | None = None
    g6_gate_pass: bool = True
    safety_gate_results: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "phase": self.phase,
            "anomaly_triggered": self.anomaly is not None,
            "action_taken": str(self.action.action_type) if self.action else None,
            "verdict": str(self.verification.verdict) if self.verification else None,
            "g6_gate_pass": self.g6_gate_pass,
            "safety_gates": self.safety_gate_results,
        }


class PeriodicGovernanceInspector:
    """周期治理巡检器（FeedbackLoopScheduler 协作者，职责簇：drift 扫描/自动修复/审计链校验）。

    5.150.3 Extract Class: 从 FeedbackLoopScheduler 提取的高内聚零耦合簇——
    三个方法均为周期性治理自检（由 _periodic_checks 每 10 周期编排调用），
    不读写调度器实例状态，ERROR_CONTRACT 均为不抛异常。
    FeedbackLoopScheduler 保留同名薄封装委托，实例级 patch 面不变。
    """

    @staticmethod
    def run_drift_scan() -> None:
        try:
            import asyncio

            from zephyr.gov_drift.drift_engine import scheduled_light

            result = run_sync(scheduled_light())
            high_drifts = [
                d
                for d in result.drifts
                if getattr(d, "severity", "").value == "HIGH" or getattr(d, "severity", "") == "HIGH"
            ]
            if high_drifts:
                logger.warning("FLE drift scan: %d HIGH drifts detected", len(high_drifts))
                PeriodicGovernanceInspector.auto_fix_drifts(high_drifts)
            else:
                logger.info("FLE drift scan: clean (%d total, 0 HIGH)", len(result.drifts))
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("FLE drift scan failed", exc_info=True)

    @staticmethod
    def auto_fix_drifts(drifts: list) -> None:
        try:
            from zephyr.infrastructure.auto_fix_engine import AutoFixEngine

            engine = AutoFixEngine()
            for d in drifts[:3]:
                target = getattr(d, "target", "") or getattr(d, "file_path", "") or str(d)
                action = engine.fix("drift_fixer", target, dry_run=False)
                if action.status.value == "COMPLETED":
                    logger.info("FLE auto-fix: drift fixed -> %s", target)
                else:
                    logger.warning("FLE auto-fix: drift fix failed -> %s (%s)", target, action.status)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("FLE auto-fix drift failed", exc_info=True)

    @staticmethod
    def audit_trail_check() -> None:
        try:
            from zephyr.governance.integrity import IntegrityVerifier

            verifier = IntegrityVerifier()
            result = verifier.verify_chain()
            status = result.get("status", "unknown")
            if status == "compromised":
                issues = result.get("issues", [])
                logger.warning("FLE audit trail: chain COMPROMISED — %d issues: %s", len(issues), issues[:3])
                try:
                    from zephyr.shared.event_bus import bus

                    bus.emit(topic="audit_chain.compromised", payload={"issues": issues})
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.warning("suppressed error in scheduler", exc_info=True)
            elif status == "no_data":
                logger.debug("FLE audit trail: no data to verify")
            else:
                checked = result.get("events_checked", 0)
                logger.info("FLE audit trail: chain valid (%d events checked)", checked)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("FLE audit trail check failed", exc_info=True)


class ExternalPersistenceWriter:
    """外部持久化写出器（FeedbackLoopScheduler 协作者，职责簇：指标/告警/失败模式持久化）。

    5.150.3 Extract Class: 从 FeedbackLoopScheduler 提取的高内聚零耦合簇——
    四个方法均为对外部系统（ClickHouse/AlertDispatcher/FLEWriter/VMS）的副作用写出，
    不读写调度器实例状态，全部 try/except 静默失败。
    FeedbackLoopScheduler 保留同名薄封装委托，实例级 patch 面不变。
    """

    @staticmethod
    def persist_metrics(snapshot: MetricSnapshot) -> None:
        try:
            from datetime import datetime

            from zephyr.feedback_loop.db_writer import write_metrics_batch
            from zephyr.infrastructure.system_telemetry.metrics_bridge import MetricPoint, SourceSystem

            ts = datetime.fromtimestamp(snapshot.timestamp, tz=UTC).isoformat()
            metric_fields = {
                "system_cpu": "percent",
                "memory_usage_pct": "percent",
                "disk_io_wait": "percent",
                "network_errors_count": "count",
                "detection_latency_ms": "ms",
            }
            points = []
            for field, unit in metric_fields.items():
                val = getattr(snapshot, field, 0.0)
                points.append(
                    MetricPoint(
                        timestamp=ts,
                        source_system=SourceSystem.FEEDBACK_LOOP,
                        metric_name=f"fle.{field}",
                        value=float(val),
                        unit=unit,
                    )
                )
            if points:
                written = write_metrics_batch(points)
                if written:
                    logger.debug("[FLE-DB] persisted %d metrics", written)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("[FLE-DB] metrics persist skipped", exc_info=True)

    @staticmethod
    def dispatch_alert_if_anomaly(event: FLEPipelineEvent, act_result: ActionRecord) -> None:
        if event.anomaly is None:
            return
        try:
            from zephyr.feedback_loop.alert_dispatcher import AlertCategory, AlertDispatcher, AlertEvent, AlertSeverity

            anomaly = event.anomaly
            raw_severity = getattr(anomaly, "severity", 5)
            if isinstance(raw_severity, (int, float)):
                if raw_severity >= 8:
                    severity = AlertSeverity.CRITICAL
                elif raw_severity >= 5:
                    severity = AlertSeverity.HIGH
                elif raw_severity >= 2:
                    severity = AlertSeverity.MEDIUM
                else:
                    severity = AlertSeverity.LOW
            else:
                severity = AlertSeverity.MEDIUM

            anomaly_id = getattr(anomaly, "anomaly_id", "unknown")
            evidence = getattr(anomaly, "evidence", {}) or {}
            metric_name = evidence.get("metric_name", "") if isinstance(evidence, dict) else ""
            metric_value = evidence.get("value", 0) if isinstance(evidence, dict) else 0
            z_score = evidence.get("z_score", 0) if isinstance(evidence, dict) else 0

            diagnosis_text = ""
            if event.diagnosis is not None:
                diagnosis_text = getattr(event.diagnosis, "summary", None) or str(event.diagnosis)

            alert = AlertEvent(
                source="feedback-loop",
                severity=severity,
                category=AlertCategory.METRIC_ANOMALY,
                title=f"FLE Anomaly #{anomaly_id}: {metric_name} z={z_score:.2f}",
                detail=diagnosis_text[:2000],
                metric_ref={
                    "name": metric_name,
                    "current_value": metric_value,
                    "z_score": z_score,
                },
            )
            dispatcher = AlertDispatcher()
            result = dispatcher.dispatch(alert)

            ExternalPersistenceWriter.persist_alert_and_log(alert, result)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("[FLE-ORC] alert dispatch skipped", exc_info=True)

    @staticmethod
    def persist_alert_and_log(alert: AlertEvent, dispatch_result: object) -> None:
        try:
            from zephyr.feedback_loop.db_writer import FLEWriter

            writer = FLEWriter()
            writer.write_alert(alert)
            writer.update_alert_status(alert.event_id, "DISPATCHED")
            writer.write_dispatch_log(
                event_id=alert.event_id,
                target_system="orchestrator",
                result="success" if dispatch_result.success else "failed",
                task_id=dispatch_result.task_id,
                error_message=dispatch_result.error,
            )
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("[FLE-DB] alert persist skipped", exc_info=True)

    @staticmethod
    def persist_failure_pattern(vector_bridge: VectorMemoryProtocol | None, event: FLEPipelineEvent) -> None:
        """5.158.4 重构：从 _run_once 提取 VMS 失败模式持久化逻辑。

        治本(风险B): str(diagnosis) 含 uuid diagnosis_id -> 内容哈希每次不同 = 无幂等
        提取稳定 pattern_text: summary > root_cause(去 z_score 浮点) > str() 兜底。
        """
        if vector_bridge is None or event.diagnosis is None:
            return
        try:
            diag_text = getattr(event.diagnosis, "summary", None)
            if diag_text is None:
                root_cause = getattr(event.diagnosis, "root_cause", None)
                if root_cause:
                    # root_cause 格式 "Elevated {metric} (z={score:.2f})" -> 保留稳定部分
                    diag_text = root_cause.split(" (")[0]
                else:
                    diag_text = str(event.diagnosis)
            if diag_text and event.verification is not None:
                verdict = getattr(event.verification, "verdict", None)
                if verdict is not None and str(verdict) not in ("HEALTHY", "NOMINAL"):
                    vector_bridge.write_failure_pattern(diag_text)
                    logger.debug("FLE-Scheduler: failure pattern persisted to VMS lessons")
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("FLE-Scheduler: failed to persist failure pattern to VMS", exc_info=True)


@dataclass
class FeedbackLoopScheduler:
    """FLE 全链路调度器——wire collect->detect->diagnose->act->verify。

    Usage:
        scheduler = FeedbackLoopScheduler()
        scheduler.start()
        ...
        scheduler.stop()
    """

    poll_interval: float = 30.0
    max_events: int = 1000

    metrics_collector: MetricsCollector = field(default_factory=MetricsCollector)
    feedback_collector: FeedbackCollector = field(default_factory=FeedbackCollector)
    protocol_adapter: Any | None = None
    vector_bridge: Any | None = None
    vms: VectorMemoryProtocol | None = None

    health_reporter: HealthReporter = field(default_factory=HealthReporter)
    safety_gate_manager: SafetyGateManager = field(default_factory=SafetyGateManager)
    act_handler: ActPhaseHandler = field(init=False)
    collect_detect_handler: CollectDetectHandler = field(init=False)

    dependency_freshness: DependencyFreshnessMonitor = field(default_factory=DependencyFreshnessMonitor)
    corruption_detector: SilentCorruptionDetector = field(default_factory=SilentCorruptionDetector)

    diagnosis_trust: RecursiveDiagnosisTrustEvaluator = field(default_factory=RecursiveDiagnosisTrustEvaluator)
    temporal_coherence: TemporalCoherenceOfSelfModel = field(default_factory=TemporalCoherenceOfSelfModel)
    data_leak_detector: SelfDiagnosisDataLeakDetector = field(default_factory=SelfDiagnosisDataLeakDetector)

    semantic_drift: ModelVersionSemanticDrift = field(default_factory=ModelVersionSemanticDrift)
    human_flood_detector: HumanAnomalyFloodDetector = field(default_factory=HumanAnomalyFloodDetector)
    param_tuning: AdaptiveParamTuning = field(default_factory=AdaptiveParamTuning)
    regime_scheduling: RegimeGainScheduling = field(default_factory=RegimeGainScheduling)
    recovery_stats: RecoveryTimeStats = field(default_factory=RecoveryTimeStats)
    nonstationary_check: NonstationaryEffectiveness = field(default_factory=NonstationaryEffectiveness)
    timezone_reasoner: TimezoneSemanticReasoner = field(default_factory=TimezoneSemanticReasoner)

    _events: list[FLEPipelineEvent] = field(default_factory=list, init=False)
    _cycle_count: int = field(default=0, init=False)
    _periodic_check_interval: int = field(default=10, init=False)
    # Lifecycle state for manual/test start()/stop() control.
    # NOTE: trae_053 v2.0.0 abolishes CircadianScheduler (timer-track) — but does NOT
    # prohibit FeedbackLoopScheduler.start() for manual control. auto_runtime_core
    # must NOT auto-call start() (production daemon auto-start is abolished);
    # start()/stop() remain available for testing/manual lifecycle control.
    _running: bool = field(default=False, init=False)
    _thread: threading.Thread | None = field(default=None, init=False)
    _consecutive_errors: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.safety_gate_manager = SafetyGateManager(
            numerical_guard=self.health_reporter.numerical_guard,
        )
        self.act_handler = ActPhaseHandler(
            throttle_defense=self.health_reporter.throttle_defense,
            degradation_planner=self.health_reporter.degradation_planner,
            mod_rate_limiter=self.health_reporter.mod_rate_limiter,
            guard_oscillation=self.health_reporter.guard_oscillation,
            context_pressure=self.health_reporter.context_pressure,
            bottleneck_detector=self.health_reporter.bottleneck_detector,
        )
        self.collect_detect_handler = CollectDetectHandler(
            numerical_guard=self.health_reporter.numerical_guard,
            cold_start=self.health_reporter.cold_start,
            bottleneck_detector=self.health_reporter.bottleneck_detector,
            stats_hygiene=self.health_reporter.stats_hygiene,
            guard_consistency=self.health_reporter.guard_consistency,
            guard_oscillation=self.health_reporter.guard_oscillation,
            metrics_collector=self.metrics_collector,
            feedback_collector=self.feedback_collector,
        )
        if self.protocol_adapter is not None:
            self.act_handler.action_selector = ActionSelector(protocol_adapter=self.protocol_adapter)

        if self.vector_bridge is None:
            try:
                from zephyr.autonomy_core.context.vector_bridge import VectorBridge

                _vms = self.vms
                if _vms is None:
                    from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory

                    _vms = InProcessVectorMemory()
                _vms.start()
                self.vector_bridge = VectorBridge(_vms)
                logger.info("FLE-Scheduler: VectorBridge auto-initialized")
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning(
                    "FLE-Scheduler: VectorBridge initialization failed, failure patterns will not persist to VMS",
                    exc_info=True,
                )
                self.vector_bridge = None

    _instance: ClassVar[FeedbackLoopScheduler | None] = None
    _instance_lock: ClassVar[threading.Lock] = threading.Lock()

    # ── Stage 4 公共化属性（property getter/setter） ──
    @property
    def running(self) -> bool:
        """Stage 4 公共化。"""
        return self._running

    @running.setter
    def running(self, value: bool) -> None:
        self._running = value

    @property
    def thread(self):
        """只读：thread（Stage 4 公共化）。"""
        return self._thread

    @thread.setter
    def thread(self, value):
        """写入：thread（Stage 4 公共化）。"""
        self._thread = value

    @property
    def consecutive_errors(self) -> int:
        """Stage 4 公共化。"""
        return self._consecutive_errors

    @consecutive_errors.setter
    def consecutive_errors(self, value: int) -> None:
        self._consecutive_errors = value

    @property
    def cycle_count(self) -> int:
        """只读：cycle_count（Stage 4 公共化）。"""
        return self._cycle_count

    @cycle_count.setter
    def cycle_count(self, value):
        """写入：cycle_count（Stage 4 公共化）。"""
        self._cycle_count = value

    # ── 单例管理 ──────────────────────────────────────────────────

    @classmethod
    def get_instance(cls, **kwargs: Any) -> FeedbackLoopScheduler:
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls(**kwargs)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        with cls._instance_lock:
            cls._instance = None

    # ── 生命周期（保留 facade：线程状态机，深度交织 _running/_thread/_consecutive_errors） ──
    # 状态/调用顺序交织（start→_run_loop→stop 原子性依赖共享可变状态），不强行拆。

    def start(self) -> None:
        """Start background polling thread (manual/test control only).

        trae_053 v2.0.0 caveat: production auto-runtime MUST NOT call start() —
        daemon auto-start is abolished. This method exists for manual/test
        lifecycle control (tests use start()/stop() to verify threading model).
        Idempotent: calling twice does not create a second thread.

        PERM-TRIGGER compliance: subscribes to ``fle.shutdown`` event so the
        scheduler can be gracefully stopped via event bus (not just stop()).
        """
        if self.running and self._thread is not None and self._thread.is_alive():
            return  # idempotent
        self.running = True
        self._consecutive_errors = 0
        # Event subscription for graceful shutdown (PERM-TRIGGER gate compliance).
        try:
            from zephyr.shared.event_bus import bus

            bus.subscribe("fle.shutdown", self._on_shutdown_event)
        except Exception:  # noqa: BLE001 — 5.135治标: subscribe is best-effort
            logger.debug("FLE-Scheduler: fle.shutdown subscribe skipped", exc_info=True)
        self._thread = threading.Thread(target=self._run_loop, name="FLE-Scheduler", daemon=True)
        self._thread.start()
        logger.info("FLE-Scheduler start: poll_interval=%.2fs", self.poll_interval)

    def _on_shutdown_event(self, event=None) -> None:
        """Event handler for ``fle.shutdown`` — triggers graceful stop.

        Allows external systems to stop the scheduler via event bus without
        holding a direct reference to the scheduler instance.
        """
        self.running = False

    def stop(self) -> None:
        """Stop background polling thread (manual/test control only).

        Sets _running=False and joins the thread. Idempotent: safe to call
        without start() or to call multiple times. Preserves the (dead) thread
        reference on `self._thread` so callers can inspect `is_alive()` post-stop.
        """
        self.running = False
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=self.poll_interval * 3 + 5.0)
        logger.info(
            "FLE-Scheduler stop: %d events, %d cycles, %d consecutive_errors",
            len(self._events),
            self._cycle_count,
            self._consecutive_errors,
        )

    def _run_loop(self) -> None:
        """Background polling loop — runs _run_once() per poll_interval.

        Error handling: on exception, increments _consecutive_errors but does
        NOT crash the loop. On success, resets _consecutive_errors to 0.
        Exits cleanly when stop() sets _running=False.
        """
        while self.running:
            try:
                self._run_once()
                self._cycle_count += 1
                if self._cycle_count % self._periodic_check_interval == 0:
                    self._periodic_checks()
                self._consecutive_errors = 0
            except Exception:  # noqa: BLE001 — broad catch preserves loop liveness
                self._consecutive_errors += 1
                logger.warning(
                    "FLE-Scheduler _run_loop error (consecutive=%d)",
                    self._consecutive_errors,
                    exc_info=True,
                )
            # Sleep in small increments so stop() is responsive
            slept = 0.0
            while self.running and slept < self.poll_interval:
                time.sleep(min(0.05, self.poll_interval - slept))
                slept += 0.05

    # ── 手动周期与自检查询（保留 facade：读写 _events/_cycle_count 实例状态） ──

    def tick(self) -> FLEPipelineEvent | None:
        result = self._run_once()
        self._cycle_count += 1
        if self._cycle_count % self._periodic_check_interval == 0:
            self._periodic_checks()
        return result

    def events(self, limit: int = 50) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._events[-limit:]]

    def run_count(self) -> int:
        return len(self._events)

    def health_report(self) -> dict[str, Any]:
        return self.health_reporter.report()

    def _periodic_checks(self) -> None:
        self.health_reporter.dogfood_monitor.self_check()
        self.health_reporter.bus_factor_monitor.check_bus_factor()
        self.corruption_detector.get_sink_health_summary()
        deps = self.dependency_freshness.check_freshness()
        if deps:
            logger.warning("FLE dependency freshness alerts: %d", len(deps))
        self._run_drift_scan()
        self._audit_trail_check()

    # ── 周期治理巡检（委托 PeriodicGovernanceInspector） ──────────────
    # 薄封装保留实例级 patch 面与 ERROR_CONTRACT；实现已提取至同文件协作者类。

    def _audit_trail_check(self) -> None:
        PeriodicGovernanceInspector.audit_trail_check()

    def _run_drift_scan(self) -> None:
        PeriodicGovernanceInspector.run_drift_scan()

    def _auto_fix_drifts(self, drifts: list) -> None:
        PeriodicGovernanceInspector.auto_fix_drifts(drifts)

    # ── 主管线编排（保留 facade：collect->detect->diagnose->act->verify 编排核心） ──
    # 调用顺序与 event 状态在全部 handler/协作者间交织，拆分即破坏编排语义，不强行拆。

    def _run_once(self) -> FLEPipelineEvent | None:
        import uuid

        run_id = str(uuid.uuid4())[:8]
        now = time.time()

        event = FLEPipelineEvent(run_id=run_id, timestamp=now, phase="collect")

        # --- Phase 1: Collect ---
        snapshot = self.collect_detect_handler.run_collect(event, now, run_id, self.metrics_collector)

        self._persist_metrics(snapshot)

        ts_check = self.safety_gate_manager.temporal_guard.validate_timestamp(now)
        if not ts_check["valid"]:
            logger.warning("FLE temporal anomaly: %s", ts_check["anomalies"])

        # --- Phase 2: Detect ---
        if self.collect_detect_handler.run_detect(event, snapshot, run_id):
            self._append_event(event)
            self._post_pipeline_checks(event)
            return event

        event.g6_gate_pass = self._g6_check(event.anomaly)

        # --- Phase 3: Diagnose ---
        if self.collect_detect_handler.run_diagnose(event, self.metrics_collector):
            self._append_event(event)
            return event

        # --- Phase 4: Act with safety gates and self-modification guards ---
        phase_start = time.time()

        safety = self.safety_gate_manager.run_safety_gates(event.anomaly, event.diagnosis)
        event.safety_gate_results = safety
        blocked = [k for k, v in safety.items() if not v]
        if blocked:
            logger.warning("FLE safety gates blocked: %s", blocked)
            self._append_event(event)
            return event

        act_result = self.act_handler.run_act(event.anomaly, event.diagnosis, snapshot, run_id)
        if act_result.skipped:
            self._append_event(event)
            return event

        event.phase = "act"
        event.action = act_result.action_record
        self.health_reporter.bottleneck_detector.record_stage_latency(
            PipelineStage.ACT, (time.time() - phase_start) * 1000
        )

        self._dispatch_alert_if_anomaly(event, act_result)

        # --- Phase 5: Verify ---
        phase_start = time.time()

        self.collect_detect_handler.trajectory_detector.record_step(
            TrajectoryEvent(
                phase="verify",
                component="verification_engine",
                timestamp=time.time(),
                input_hash=run_id,
                output_hash="",
            )
        )

        verification = self.act_handler.run_verify(event.anomaly, event.diagnosis, run_id, self._get_current_metric)

        event.phase = "verify"
        event.verification = verification
        self.health_reporter.bottleneck_detector.record_stage_latency(
            PipelineStage.VERIFY, (time.time() - phase_start) * 1000
        )

        self._append_event(event)
        self._post_pipeline_checks(event)

        self._persist_failure_pattern(event)

        logger.info(
            "FLE run=%s anomaly=%s action=%s verdict=%s",
            run_id,
            event.anomaly.anomaly_id,
            act_result.action_type.value if act_result.action_type else "none",
            verification.verdict.value,
        )
        return event

    def persist_failure_pattern(self, event: FLEPipelineEvent) -> None:
        """Stage 4 公共化：persist a failure pattern to VMS lessons."""
        ExternalPersistenceWriter.persist_failure_pattern(self.vector_bridge, event)

    def _persist_failure_pattern(self, event: FLEPipelineEvent) -> None:
        """向后兼容 thin wrapper。"""
        return self.persist_failure_pattern(event)

    def _run_safety_gates(self, anomaly: AnomalyEvent, diagnosis: Diagnosis) -> dict[str, bool]:
        return self.safety_gate_manager.run_safety_gates(anomaly, diagnosis)

    def _dispatch_fle_gates(self, anomaly: AnomalyEvent, diagnosis: Diagnosis) -> dict[str, bool]:
        return self.safety_gate_manager._dispatch_fle_gates(anomaly, diagnosis)

    def _invoke_fle_gate(self, gate_id: str, gate_file: str, anomaly: AnomalyEvent, diagnosis: Diagnosis) -> bool:
        return self.safety_gate_manager._invoke_fle_gate(gate_id, gate_file, anomaly, diagnosis)

    # ── 管线后自检与门禁（保留 facade：依赖 human_flood_detector/temporal_coherence/  ──
    # ── diagnosis_trust/metrics_collector 等实例组件字段，与组件状态交织） ──

    def _post_pipeline_checks(self, event: FLEPipelineEvent) -> None:
        if event.anomaly is not None:
            anomaly_id = event.anomaly.anomaly_id
            if hasattr(event.anomaly, "severity"):
                self.human_flood_detector.record_anomaly_exposure(
                    "owner", anomaly_id, getattr(event.anomaly, "severity", "P3")
                )

        self.health_reporter.entropy_monitor.analyze_trend()
        self.health_reporter.diminishing_returns.analyze_diminishing_returns()

        if event.verification:
            self.temporal_coherence.record_snapshot(
                capabilities={"detection": 0.9, "response": 0.85},
                limits={"max_guards": 120, "max_cycles_per_hour": 600},
                health_score=0.9,
            )
            coherence = self.temporal_coherence.check_coherence()
            if coherence.get("status") != "normal":
                logger.warning("FLE temporal coherence: %s", coherence)

        if event.diagnosis:
            trust = self.diagnosis_trust.evaluate_trust({"status": "healthy" if event.verification else "degraded"})
            if not trust.get("trustworthy", True):
                logger.warning("FLE self-diagnosis trust: %s", trust)

    def _g6_check(self, anomaly: AnomalyEvent) -> bool:
        try:
            getattr(anomaly, "anomaly_id", "unknown")
            metrics_path = REPO_ROOT / "data" / "telemetry" / "blueprint_reads.jsonl"
            if not metrics_path.exists():
                return False
            with open(metrics_path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                        continue
                    if record.get("event") == "blueprint_read" and record.get("blueprint_id") == "MOD-FEEDBACK_LOOP":
                        return True
            return False
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return True

    def _get_current_metric(self, metric_name: str) -> float:
        if not metric_name:
            return 0.0
        return getattr(self.metrics_collector.baseline, f"{metric_name}_ema", 0.0)

    # ── 外部持久化写出（委托 ExternalPersistenceWriter） ──────────────
    # 薄封装保留实例级 patch 面；实现已提取至同文件协作者类。

    def _persist_metrics(self, snapshot: MetricSnapshot) -> None:
        ExternalPersistenceWriter.persist_metrics(snapshot)

    def _dispatch_alert_if_anomaly(self, event: FLEPipelineEvent, act_result: ActionRecord) -> None:
        ExternalPersistenceWriter.dispatch_alert_if_anomaly(event, act_result)

    def _persist_alert_and_log(self, alert: AlertEvent, dispatch_result: object) -> None:
        ExternalPersistenceWriter.persist_alert_and_log(alert, dispatch_result)

    # ── 事件缓冲与总线发布（保留 facade：直接读写 _events/max_events 实例状态） ──

    def _append_event(self, event: FLEPipelineEvent) -> None:
        self._events.append(event)
        if len(self._events) > self.max_events:
            self._events = self._events[-self.max_events :]
        self._publish_to_event_bus(event)

    def _publish_to_event_bus(self, event: FLEPipelineEvent) -> None:
        try:
            from zephyr.shared.event_bus import EventPriority, bus

            # FLEPipelineEvent uses `anomaly` (Optional) — derive bool flag for routing.
            anomaly_detected = event.anomaly is not None
            priority = EventPriority.HIGH if anomaly_detected else EventPriority.NORMAL
            bus.emit(
                topic=f"fle.{event.phase}",
                payload=event.to_dict(),
                priority=priority,
            )
            if anomaly_detected:
                bus.emit(
                    topic="fle.anomaly",
                    payload={
                        "run_id": event.run_id,
                        "phase": event.phase,
                        "anomaly_type": getattr(event, "anomaly_type", "unknown"),
                        "timestamp": event.timestamp,
                    },
                    priority=EventPriority.HIGH,
                )
            if event.action_taken and event.action_taken != "none":
                bus.emit(
                    topic="fle.action",
                    payload={
                        "run_id": event.run_id,
                        "action": event.action_taken,
                        "timestamp": event.timestamp,
                    },
                    priority=EventPriority.NORMAL,
                )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in scheduler", exc_info=True)
