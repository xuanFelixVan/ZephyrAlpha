# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_orphan_integration
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
Orphan Integration Tests — 验证 shared/ 下35个孤儿模块的导入与核心功能
按集群组织，每个模块测试：导入、实例化、核心方法
"""
import pytest


class TestAdaptiveSampler:
    def test_import(self):
        from zephyr.shared.adaptive_sampler import AdaptiveSampler

    def test_instantiate(self):
        from zephyr.shared.adaptive_sampler import AdaptiveSampler
        sampler = AdaptiveSampler()
        assert sampler.CPU_BUDGET == 0.01
        assert sampler.MEMORY_BUDGET_MB == 5

    def test_should_sample_and_report(self):
        from zephyr.shared.adaptive_sampler import AdaptiveSampler
        sampler = AdaptiveSampler()
        sampler._current_interval = 0.0
        assert sampler.should_sample() is True
        sampler.report_overhead(0.005, 3.0)
        stats = sampler.get_stats()
        assert stats["total_samples"] >= 1

    def test_overhead_triggers_interval_increase(self):
        from zephyr.shared.adaptive_sampler import AdaptiveSampler
        sampler = AdaptiveSampler()
        sampler.report_overhead(0.5, 10.0)
        assert sampler._current_interval > 10.0


class TestAIAuditGuard:
    def test_import(self):
        from zephyr.shared.ai_audit_guard import AuditGuardEngine, AuditAction, RiskLevel, AuditVerdict

    def test_instantiate_no_rules_file(self):
        from zephyr.shared.ai_audit_guard import AuditGuardEngine
        guard = AuditGuardEngine()
        assert len(guard.rules) > 0

    def test_evaluate_blocked_pattern(self):
        from zephyr.shared.ai_audit_guard import AuditGuardEngine, AuditAction, AuditRequest
        guard = AuditGuardEngine()
        request = AuditRequest(
            agent_id="test-agent",
            action=AuditAction.MODIFY,
            target="docs/01_policies_and_standards/some_file.md",
        )
        result = guard.evaluate(request)
        assert result.verdict.value == "block"

    def test_evaluate_allowed(self):
        from zephyr.shared.ai_audit_guard import AuditGuardEngine, AuditAction, AuditRequest
        guard = AuditGuardEngine()
        request = AuditRequest(
            agent_id="test-agent",
            action=AuditAction.CREATE,
            target="src/zephyr/l02_alpha_factor/new_factor.py",
        )
        result = guard.evaluate(request)
        assert result.verdict.value in ("allow", "flag")

    def test_get_guard_singleton(self):
        from zephyr.shared.ai_audit_guard import get_guard
        g1 = get_guard()
        g2 = get_guard()
        assert g1 is g2


class TestAIUnderstandabilityConstraint:
    def test_import(self):
        from zephyr.shared.ai_understandability_constraint import AIUnderstandabilityConstraint

    def test_check_readability_pass(self):
        from zephyr.shared.ai_understandability_constraint import AIUnderstandabilityConstraint
        constraint = AIUnderstandabilityConstraint()

        class WellNamed:
            description: str
            module_name: str

        result = constraint.check_readability(WellNamed)
        assert result["verdict"] in ("PASS", "FAIL")

    def test_audit_format_change(self):
        from zephyr.shared.ai_understandability_constraint import AIUnderstandabilityConstraint
        constraint = AIUnderstandabilityConstraint()
        result = constraint.audit_format_change({"a": 1}, {"a": 1, "b": 2})
        assert "Added fields" in result


class TestAlertEscalation:
    def test_import(self):
        from zephyr.shared.alert_escalation import AlertEscalation, AlertSeverity

    def test_register_and_acknowledge(self):
        from zephyr.shared.alert_escalation import AlertEscalation, AlertSeverity
        ae = AlertEscalation()
        ae.register_alert("test-1", AlertSeverity.SEV_2)
        state = ae.check("test-1")
        assert state.alert_id == "test-1"
        ae.acknowledge("test-1")
        state = ae.check("test-1")
        assert state.acknowledged is True


class TestAlertManager:
    def test_import(self):
        from zephyr.shared.alert_manager import AlertManager, Severity

    def test_fire_and_dedup(self):
        from zephyr.shared.alert_manager import AlertManager, Severity
        am = AlertManager()
        alert1 = am.fire("sli-1", Severity.SEV_1, 0.95, 0.90, "test alert")
        assert alert1 is not None
        alert2 = am.fire("sli-1", Severity.SEV_1, 0.96, 0.90, "dup")
        assert alert2 is None

    def test_get_report(self):
        from zephyr.shared.alert_manager import AlertManager, Severity
        am = AlertManager()
        am.fire("sli-1", Severity.SEV_2, 0.95, 0.90)
        report = am.get_report()
        assert "Alerts:" in report


class TestAlertPrecisionTracker:
    def test_import(self):
        from zephyr.shared.alert_precision_tracker import AlertPrecisionTracker

    def test_metrics_calculation(self):
        from zephyr.shared.alert_precision_tracker import AlertPrecisionTracker
        tracker = AlertPrecisionTracker()
        tracker.record_true_positive("rule-1")
        tracker.record_true_positive("rule-1")
        tracker.record_false_positive("rule-1")
        metrics = tracker.get_metrics("rule-1")
        assert metrics["precision"] == 0.67
        assert metrics["suppressed"] is False


class TestDualChannelAlert:
    def test_import(self):
        from zephyr.shared.dual_channel_alert import DualChannelAlertManager, AlertChannel

    def test_send_all_channels(self):
        from zephyr.shared.dual_channel_alert import DualChannelAlertManager, AlertChannel
        mgr = DualChannelAlertManager()
        results = mgr.send("test alert", [AlertChannel.TERMINAL])
        assert AlertChannel.TERMINAL.value in results
        assert results[AlertChannel.TERMINAL.value] is True


class TestBlueprintCodeAuditor:
    def test_import(self):
        from zephyr.shared.blueprint_code_auditor import BlueprintCodeAuditor

    def test_audit_missing_blueprint(self):
        from zephyr.shared.blueprint_code_auditor import BlueprintCodeAuditor
        auditor = BlueprintCodeAuditor(blueprint_path="/nonexistent/blueprint.md")
        result = auditor.audit()
        assert result["drift_detected"] is True


class TestSLOReviewAssistant:
    def test_import(self):
        from zephyr.shared.slo_review_assistant import SLOReviewAssistant, SLOHealthReport

    def test_generate_review(self):
        from zephyr.shared.slo_review_assistant import SLOReviewAssistant
        assistant = SLOReviewAssistant(slo_registry=[{"id": "sli-1"}])
        reports = assistant.generate_review()
        assert len(reports) == 1
        assert reports[0].sli_id == "sli-1"

    def test_summary(self):
        from zephyr.shared.slo_review_assistant import SLOReviewAssistant
        assistant = SLOReviewAssistant(slo_registry=[{"id": "sli-1"}])
        summary = assistant.summary()
        assert "SLO Review Summary" in summary


class TestBudgetAwarePromptMerger:
    def test_import(self):
        from zephyr.shared.budget_aware_prompt import BudgetAwarePromptMerger, MergeMode

    def test_full_build_mode(self):
        from zephyr.shared.budget_aware_prompt import BudgetAwarePromptMerger
        merger = BudgetAwarePromptMerger(budget_remaining_pct=0.8)
        result = merger.merge("base prompt", {"budget_remaining": "80%"}, "extra")
        assert "base prompt" in result
        assert "extra" in result

    def test_minimal_viable_mode(self):
        from zephyr.shared.budget_aware_prompt import BudgetAwarePromptMerger
        merger = BudgetAwarePromptMerger(budget_remaining_pct=0.05)
        result = merger.merge("base prompt", {"budget_remaining": "5%"})
        assert "base prompt" in result


class TestCodeEconomyAnalyzer:
    def test_import(self):
        from zephyr.shared.code_economy_analyzer import CodeEconomyAnalyzer

    def test_register_and_analyze(self):
        from zephyr.shared.code_economy_analyzer import CodeEconomyAnalyzer
        analyzer = CodeEconomyAnalyzer()
        analyzer.register_module("test_mod", __file__)
        analyzer.record_call("test_mod")
        result = analyzer.analyze()
        assert result["total_modules"] == 1
        assert "test_mod" in result["active"]


class TestCostEstimator:
    def test_import(self):
        from zephyr.shared.cost_estimator import CostEstimator, CostEstimate, ModelPricing

    def test_estimate_affordable(self):
        from zephyr.shared.cost_estimator import CostEstimator
        est = CostEstimator()
        result = est.estimate(1000, "deepseek-chat", 500)
        assert result.affordable is True
        assert result.estimated_cost_usd > 0

    def test_estimate_unknown_model(self):
        from zephyr.shared.cost_estimator import CostEstimator
        est = CostEstimator()
        result = est.estimate(1000, "unknown-model")
        assert result.affordable is False

    def test_suggest_alternative(self):
        from zephyr.shared.cost_estimator import CostEstimator
        est = CostEstimator()
        alt = est.suggest_alternative("deepseek-reasoner")
        assert alt == "deepseek-chat"

    def test_get_cost_estimator_singleton(self):
        from zephyr.shared.cost_estimator import get_cost_estimator
        e1 = get_cost_estimator()
        e2 = get_cost_estimator()
        assert e1 is e2


class TestErrorBudgetTracker:
    def test_import(self):
        from zephyr.shared.error_budget_tracker import ErrorBudgetTracker, ResponseTier

    def test_evaluate_no_db(self):
        from zephyr.shared.error_budget_tracker import ErrorBudgetTracker
        tracker = ErrorBudgetTracker(db_path="/nonexistent/capacity.db")
        result = tracker.evaluate()
        assert "tier" in result
        assert result["tier"] == "L0_HEALTHY"

    def test_get_budget_tracker_singleton(self):
        from zephyr.shared.error_budget_tracker import get_budget_tracker
        t1 = get_budget_tracker()
        t2 = get_budget_tracker()
        assert t1 is t2


class TestCapacityCalibrator:
    def test_import(self):
        from zephyr.shared.capacity_calibrator import CapacityCalibrator

    def test_record_and_correction(self):
        from zephyr.shared.capacity_calibrator import CapacityCalibrator
        cal = CapacityCalibrator()
        factor = cal.record(100, 50.0, 65.0)
        assert factor == 1.3
        assert cal.apply_correction(100.0) == pytest.approx(130.0)


class TestCapacityDigitalTwin:
    def test_import(self):
        from zephyr.shared.capacity_digital_twin import CapacityDigitalTwin

    def test_predict(self):
        from zephyr.shared.capacity_digital_twin import CapacityDigitalTwin
        twin = CapacityDigitalTwin()
        twin.calibrate(100, 50.0, 0.1, 5000.0)
        result = twin.predict(10)
        assert "estimated_memory_mb" in result
        assert result["estimated_memory_mb"] > 0


class TestCapacityFingerprint:
    def test_import(self):
        from zephyr.shared.capacity_fingerprint import CapacityFingerprinter, CapacityFingerprint

    def test_compare_no_degradation(self):
        from zephyr.shared.capacity_fingerprint import CapacityFingerprinter, CapacityFingerprint
        fp = CapacityFingerprinter()
        fp.set_baseline(CapacityFingerprint(module_name="mod1", memory_mb=10.0, import_time_ms=50.0))
        fp.record(CapacityFingerprint(module_name="mod1", memory_mb=12.0, import_time_ms=60.0))
        result = fp.compare("mod1")
        assert result["degraded"] is False

    def test_compare_with_degradation(self):
        from zephyr.shared.capacity_fingerprint import CapacityFingerprinter, CapacityFingerprint
        fp = CapacityFingerprinter()
        fp.set_baseline(CapacityFingerprint(module_name="mod1", memory_mb=10.0, import_time_ms=50.0))
        fp.record(CapacityFingerprint(module_name="mod1", memory_mb=25.0, import_time_ms=200.0))
        result = fp.compare("mod1")
        assert result["degraded"] is True


class TestCapacityGovernanceLoop:
    def test_import(self):
        from zephyr.shared.capacity_governance_loop import CapacityGovernanceLoop, GovernanceLevel

    def test_evaluate_no_db(self):
        from zephyr.shared.capacity_governance_loop import CapacityGovernanceLoop, GovernanceLevel
        loop = CapacityGovernanceLoop(db_path="/nonexistent/capacity.db")
        state = loop.evaluate()
        assert state.level == GovernanceLevel.L0_HEALTHY

    def test_act_healthy(self):
        from zephyr.shared.capacity_governance_loop import CapacityGovernanceLoop, GovernanceLevel, GovernanceState
        loop = CapacityGovernanceLoop()
        state = GovernanceState(
            level=GovernanceLevel.L0_HEALTHY,
            sli_values={}, error_budget_remaining=1.0,
            burn_rate=0.0, timestamp="2026-01-01T00:00:00Z",
        )
        actions = loop.act(state)
        assert len(actions) == 0

    def test_act_emergency(self):
        from zephyr.shared.capacity_governance_loop import CapacityGovernanceLoop, GovernanceLevel, GovernanceState
        loop = CapacityGovernanceLoop()
        state = GovernanceState(
            level=GovernanceLevel.L4_EMERGENCY,
            sli_values={}, error_budget_remaining=0.0,
            burn_rate=10.0, timestamp="2026-01-01T00:00:00Z",
        )
        actions = loop.act(state)
        assert len(actions) >= 2
        assert any("KILL_SWITCH" in a for a in actions)

    def test_get_governance_loop_singleton(self):
        from zephyr.shared.capacity_governance_loop import get_governance_loop
        l1 = get_governance_loop()
        l2 = get_governance_loop()
        assert l1 is l2


class TestCapacityRunbookGenerator:
    def test_import(self):
        from zephyr.shared.capacity_runbook_generator import CapacityRunbookGenerator

    def test_generate_and_export(self):
        from zephyr.shared.capacity_runbook_generator import CapacityRunbookGenerator
        gen = CapacityRunbookGenerator()
        rb = gen.generate("INC-001", "SEV-1", "OOM", ["l02_alpha_factor"])
        assert rb.incident_id == "INC-001"
        exported = gen.export()
        assert "INC-001" in exported


class TestDependencyCapacityGuard:
    def test_import(self):
        from zephyr.shared.dependency_capacity_guard import DependencyCapacityGuard

    def test_check_all(self):
        from zephyr.shared.dependency_capacity_guard import DependencyCapacityGuard
        guard = DependencyCapacityGuard()
        results = guard.check_all()
        assert "chromadb" in results
        assert results["chromadb"]["healthy"] is True

    def test_mark_unhealthy(self):
        from zephyr.shared.dependency_capacity_guard import DependencyCapacityGuard
        guard = DependencyCapacityGuard()
        guard.mark_unhealthy("sqlite")
        result = guard.check_dependency("sqlite")
        assert result["healthy"] is False


class TestLongevityMonitor:
    def test_import(self):
        from zephyr.shared.longevity_monitor import LongevityMonitor

    def test_monthly_check_no_data_dir(self):
        from zephyr.shared.longevity_monitor import LongevityMonitor
        monitor = LongevityMonitor()
        monitor.take_baseline()
        result = monitor.monthly_check(data_dir="/nonexistent")
        assert "healthy" in result


class TestModelCapacityProbe:
    def test_import(self):
        from zephyr.shared.model_capacity_probe import ModelCapacityProbe, ProbeResult

    def test_probe_no_drift(self):
        from zephyr.shared.model_capacity_probe import ModelCapacityProbe, ProbeResult
        probe = ModelCapacityProbe()
        probe.set_baseline("deepseek-chat", ProbeResult(
            model="deepseek-chat", latency_ms=1000.0, tokens_output=500, code_lines=50
        ))
        result = probe.probe("deepseek-chat", 1200.0, 550, 55)
        assert result.drift_detected is False

    def test_probe_with_drift(self):
        from zephyr.shared.model_capacity_probe import ModelCapacityProbe, ProbeResult
        probe = ModelCapacityProbe()
        probe.set_baseline("deepseek-chat", ProbeResult(
            model="deepseek-chat", latency_ms=1000.0, tokens_output=500, code_lines=50
        ))
        result = probe.probe("deepseek-chat", 5000.0, 1000, 100)
        assert result.drift_detected is True


class TestCombinatorialGate:
    def test_import(self):
        from zephyr.shared.combinatorial_gate import CombinatorialGate

    def test_below_threshold_not_blocked(self):
        from zephyr.shared.combinatorial_gate import CombinatorialGate
        gate = CombinatorialGate()
        changes = [{"id": "c1"}, {"id": "c2"}]
        result = gate.evaluate(changes, cost_fn=lambda c: 1.0)
        assert result["blocked"] is False

    def test_above_threshold_blocked(self):
        from zephyr.shared.combinatorial_gate import CombinatorialGate
        gate = CombinatorialGate()
        changes = [{"id": f"c{i}"} for i in range(4)]
        def cost_fn(c):
            if len(c) == 1:
                return 1.0
            return len(c) * 2.0
        result = gate.evaluate(changes, cost_fn=cost_fn)
        assert result["blocked"] is True


class TestCoreIntegrityGuard:
    def test_import(self):
        from zephyr.shared.core_integrity_guard import CoreIntegrityGuard

    def test_verify_no_baseline(self):
        from zephyr.shared.core_integrity_guard import CoreIntegrityGuard
        guard = CoreIntegrityGuard(project_root="/nonexistent")
        result = guard.verify()
        assert "intact" in result


class TestOwnerTrustGauge:
    def test_import(self):
        from zephyr.shared.owner_trust_gauge import OwnerTrustGauge, TrustLevel

    def test_high_trust(self):
        from zephyr.shared.owner_trust_gauge import OwnerTrustGauge, TrustLevel
        gauge = OwnerTrustGauge()
        gauge.record_alert()
        gauge.record_alert()
        assert gauge.evaluate() in (TrustLevel.HIGH, TrustLevel.NORMAL)

    def test_critically_low_trust(self):
        from zephyr.shared.owner_trust_gauge import OwnerTrustGauge, TrustLevel
        gauge = OwnerTrustGauge()
        for _ in range(10):
            gauge.record_alert()
            gauge.record_dismissal()
        assert gauge.evaluate() == TrustLevel.CRITICALLY_LOW


class TestDegradationChain:
    def test_import(self):
        from zephyr.shared.degradation_chain import DegradationChainManager, DegradationTrigger

    def test_check_trigger(self):
        from zephyr.shared.degradation_chain import DegradationChainManager
        mgr = DegradationChainManager()
        assert mgr.check_trigger("cost-degradation", 10.0) is True
        assert mgr.check_trigger("cost-degradation", 1.0) is False

    def test_degrade_and_recover(self):
        from zephyr.shared.degradation_chain import DegradationChainManager
        mgr = DegradationChainManager()
        model = mgr.degrade("cost-degradation", "cost exceeded")
        assert model is not None
        state = mgr.get_state("cost-degradation")
        assert state.degraded is True

    def test_get_degradation_manager_singleton(self):
        from zephyr.shared.degradation_chain import get_degradation_manager
        m1 = get_degradation_manager()
        m2 = get_degradation_manager()
        assert m1 is m2


class TestFaultIsolator:
    def test_import(self):
        from zephyr.shared.fault_isolator import FaultIsolator, FaultDomainStatus

    def test_execute_success(self):
        from zephyr.shared.fault_isolator import FaultIsolator
        fi = FaultIsolator()
        result = fi.execute("critical_runtime", lambda: 42)
        assert result == 42

    def test_execute_with_fallback(self):
        from zephyr.shared.fault_isolator import FaultIsolator
        fi = FaultIsolator()
        fi.isolate("external_services")
        result = fi.execute("external_services", lambda: 1, fallback=lambda: 99)
        assert result == 99

    def test_isolate_and_restore(self):
        from zephyr.shared.fault_isolator import FaultIsolator
        fi = FaultIsolator()
        fi.isolate("file_operations")
        assert fi.is_healthy("file_operations") is False
        fi.restore("file_operations")
        assert fi.is_healthy("file_operations") is True


class TestEventBusUpgrade:
    def test_import(self):
        from zephyr.shared.events.event_bus_upgrade import EventBusUpgrader, EventSchema

    def test_register_and_upgrade(self):
        from zephyr.shared.events.event_bus_upgrade import EventBusUpgrader, EventSchema
        upgrader = EventBusUpgrader()
        upgrader.register(EventSchema(
            event_type="task.created", version=1, fields=["id", "name"]
        ))
        upgrader.register(EventSchema(
            event_type="task.created", version=2,
            fields=["id", "name", "priority"],
            deprecated_fields=[],
            migration_fn=lambda d: {**d, "priority": "normal"},
        ))
        result = upgrader.upgrade("task.created", {"id": "1", "name": "test"}, 1, 2)
        assert result["priority"] == "normal"

    def test_check_compatibility(self):
        from zephyr.shared.events.event_bus_upgrade import EventBusUpgrader, EventSchema
        upgrader = EventBusUpgrader()
        upgrader.register(EventSchema(event_type="test", version=1, fields=["a"]))
        assert upgrader.check_compatibility("test", 1) is True
        assert upgrader.check_compatibility("test", 0) is False


class TestHeartbeatServer:
    def test_import(self):
        from zephyr.shared.heartbeat_server import HeartbeatServer

    def test_health_check(self):
        from zephyr.shared.heartbeat_server import HeartbeatServer
        server = HeartbeatServer(port=0)
        assert server.check_health() is True
        server.mark_unhealthy()
        assert server.check_health() is False


class TestTaskHeartbeat:
    def test_import(self):
        from zephyr.shared.task_heartbeat import TaskHeartbeatMonitor

    def test_register_and_check(self):
        from zephyr.shared.task_heartbeat import TaskHeartbeatMonitor
        monitor = TaskHeartbeatMonitor()
        monitor.register("task-1")
        zombies = monitor.check_zombies()
        assert len(zombies) == 0

    def test_rollback_zombie(self):
        from zephyr.shared.task_heartbeat import TaskHeartbeatMonitor
        monitor = TaskHeartbeatMonitor()
        monitor.register("task-1")
        monitor._tasks["task-1"].status = "zombie"
        assert monitor.rollback_zombie("task-1") is True
        assert "task-1" not in monitor._tasks


class TestTTLCleanupEngine:
    def test_import(self):
        from zephyr.shared.ttl_cleanup_engine import TTLCleanupEngine

    def test_run_no_db(self):
        from zephyr.shared.ttl_cleanup_engine import TTLCleanupEngine
        engine = TTLCleanupEngine(db_path="/nonexistent/capacity.db")
        result = engine.run(project_root="/nonexistent")
        assert "database_cleanup" in result
        assert "ttl_days" in result

    def test_get_cleanup_engine_singleton(self):
        from zephyr.shared.ttl_cleanup_engine import get_cleanup_engine
        e1 = get_cleanup_engine()
        e2 = get_cleanup_engine()
        assert e1 is e2


class TestModuleBirthRegistry:
    def test_import(self):
        from zephyr.shared.module_birth_registry import ModuleBirthRegistry

    def test_register_and_check(self):
        from zephyr.shared.module_birth_registry import ModuleBirthRegistry
        registry = ModuleBirthRegistry()
        record = registry.register("test_module", "2.6.0", ["dep1"])
        assert record.module_name == "test_module"
        all_records = registry.get_all()
        assert "test_module" in all_records


class TestReasoningSpans:
    def test_import(self):
        from zephyr.shared.reasoning_spans import ReasoningSpan

    def test_fallback_trace(self):
        from zephyr.shared.reasoning_spans import ReasoningSpan
        spans = ReasoningSpan(enable_otel=False)
        with spans.trace_reasoning("agent-1", "test task") as ctx:
            spans.add_step(ctx, "step-1", "detail")
        assert ctx["steps_count"] == 1

    def test_get_reasoning_spans_singleton(self):
        from zephyr.shared.reasoning_spans import get_reasoning_spans
        s1 = get_reasoning_spans()
        s2 = get_reasoning_spans()
        assert s1 is s2


class TestZephyrLogger:
    def test_import(self):
        from zephyr.shared.zephyr_logger import ZephyrLogger, LogEntry

    def test_info_log(self):
        from zephyr.shared.zephyr_logger import ZephyrLogger
        logger = ZephyrLogger(module="test", enable_otel=False)
        entry = logger.info("test message")
        assert entry.message == "test message"
        assert entry.level == "INFO"

    def test_log_entry_as_dict(self):
        from zephyr.shared.zephyr_logger import LogEntry
        entry = LogEntry(timestamp="2026-01-01", level="INFO", message="test")
        d = entry.as_dict()
        assert d["level"] == "INFO"

    def test_get_logger_singleton(self):
        from zephyr.shared.zephyr_logger import get_logger
        l1 = get_logger()
        l2 = get_logger()
        assert l1 is l2


class TestSandboxExecutor:
    def test_import(self):
        from zephyr.shared.sandbox_executor import SandboxExecutor, SandboxAction, SandboxResult

    def test_dry_run_file_delete(self):
        from zephyr.shared.sandbox_executor import SandboxExecutor, SandboxAction, SandboxResult
        executor = SandboxExecutor()
        result, _ = executor.execute(SandboxAction.FILE_DELETE, lambda: None)
        assert result == SandboxResult.DRY_RUN

    def test_execute_allowed(self):
        from zephyr.shared.sandbox_executor import SandboxExecutor, SandboxAction, SandboxResult
        executor = SandboxExecutor()
        result, value = executor.execute(SandboxAction.EXTERNAL_API_CALL, lambda: 42)
        assert result == SandboxResult.ALLOWED
        assert value == 42


class TestVibeExperimentTracker:
    def test_import(self):
        from zephyr.shared.vibe_experiment_tracker import VibeExperimentTracker

    def test_can_experiment(self):
        from zephyr.shared.vibe_experiment_tracker import VibeExperimentTracker
        tracker = VibeExperimentTracker()
        assert tracker.can_experiment(1000) is True

    def test_record_and_status(self):
        from zephyr.shared.vibe_experiment_tracker import VibeExperimentTracker
        tracker = VibeExperimentTracker()
        tracker.record_experiment(5000, "/tmp/product.md")
        status = tracker.get_status()
        assert status["experiments_today"] == 1
        assert status["tokens_used_today"] == 5000
