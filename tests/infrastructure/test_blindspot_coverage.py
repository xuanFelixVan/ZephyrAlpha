# [A_test] module_id: MOD-GOV_blindspot_coverage | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-475 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.core.test_blindspot_coverage
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
48盲点覆盖审计 — 盲点 vs 代码实现覆盖检查。
TASK-INF-0130 产出物
"""


import importlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

BLINDSPOT_TO_CODE = {
    # 2026-08-16 契约漂移对齐：zephyr.orchestrator.core 旧树退役，
    # 映射更新为现行 canonical 模块路径（类名探针实测定位）。
    "A1_execretion_error_handling": "zephyr.shared.reliability.retry_handler.RetryHandler",
    "A2_dependency_timeout": "zephyr.infrastructure.reliability.circuit_breaker.CircuitBreaker",
    "A3_task_card_validation": "zephyr.shared.foundation.models.TaskCard",
    "A4_decomposition_fidelity": "zephyr.shared.blueprint_tools.blueprint_decomposer.BlueprintDecomposer",
    "A5_context_overflow": "zephyr.shared.context.context_engine.ContextEngine",
    "A6_diff_accuracy": "zephyr.shared.reliability.diff_planner.DiffPlanner",
    "A7_forbidden_touch": "zephyr.infrastructure.reliability.context_guard.ContextGuard",
    "A8_token_budget": "zephyr.shared.context.context_engine.ContextEngine",
    "A9_rto_sla": "zephyr.infrastructure.sla.sla_monitor.SLAMonitor",
    "B1_lifecycle_states": "zephyr.infrastructure.lifecycle.task_lifecycle_manager.TaskLifecycleManager",
    "B2_gate_integrity": "zephyr.infrastructure.lifecycle.task_lifecycle_manager.GateID",
    "B3_scope_drift": "zephyr.infrastructure.lifecycle.scope_guard.ScopeGuard",
    "B4_dependency_cycle": "zephyr.shared.dependency.dependency_graph.DependencyGraph",
    "B5_blueprint_sync": "zephyr.infrastructure.blueprint_code_sync.BlueprintCodeSyncService",
    "B6_rollback_instructions": "zephyr.infrastructure.lifecycle.task_lifecycle_manager.TaskLifecycleManager",
    "B7_context_manifest": "zephyr.shared.context.context_engine.ContextEngine",
    "C1_owner_absent": "zephyr.governance.escalation.owner_absent.OwnerAbsent",
    "C2_autonomy_downgrade": "zephyr.shared.maintenance.autonomy_monitor.AutonomyMonitor",
    "C3_manual_override": "zephyr.infrastructure.lifecycle.task_lifecycle_manager.TaskLifecycleManager",
    "C4_notification_throttle": "zephyr.infrastructure.observability.notifier.Notifier",
    "C5_session_continuity": "zephyr.shared.session.session_continuity.SessionContinuity",
    "D1_trace_missing": "zephyr.infrastructure.observability.trace_decorator.TraceCollector",
    "D2_cost_blind": "zephyr.infrastructure.cost_tracker.CostTracker",
    "D3_failure_unknown": "zephyr.orchestrator.resilience.failure_matcher.FailureMatcher",
    "D4_cli_invisible": "zephyr.shared.utils.cli_summary.CLISummary",
    "D5_healthcheck": "zephyr.shared.lifecycle.healthcheck_service.HealthcheckService",
    "E1_no_quality_gate": "zephyr.infrastructure.quality.quality_monitor.QualityMonitor",
    "E2_no_lint": "zephyr.infrastructure.quality.quality_monitor.QualityMonitor",
    "E3_prompt_versioning": "zephyr.shared.adaptation.prompt_version_manager.PromptVersionManager",
    "E4_execution_tuning": "zephyr.shared.adaptation.execution_tuner.ExecutionTuner",
    "F1_no_saga": "zephyr.shared.compensation.saga_compensator.SagaCompensator",
    "F2_partial_compensation": "zephyr.shared.compensation.saga_compensator.SagaCompensator",
    "F3_compensation_order": "zephyr.shared.compensation.saga_compensator.SagaCompensator",
    "G1_event_propagation": "zephyr.shared.event_bus.EventBus",
    "G2_event_persistence": "zephyr.infrastructure.events.event_store.EventStore",
    "G3_reaction_gap": "zephyr.shared.events.event_reactor.EventReactor",
    "G4_hook_dispatch": "zephyr.shared.events.hook_dispatcher.HookDispatcher",
    "G5_task_scheduling": "zephyr.infrastructure.queue.task_scheduler.TaskScheduler",
    "G6_task_queue": "zephyr.infrastructure.queue.task_queue.TaskQueue",
    "G7_impact_propagation": "zephyr.infrastructure.impact.impact_propagator.ImpactPropagator",
    "G8_semantic_impact": "zephyr.infrastructure.impact.llm_impact_analyzer.LLMImpactAnalyzer",
    "H4_draft_assistant": "zephyr.shared.draft.draft_assistant.DraftAssistant",
}


def test_blindspot_coverage() -> None:
    resolved = 0
    unresolved: list[str] = []

    for blindspot_id, module_path in BLINDSPOT_TO_CODE.items():
        module_name, class_name = module_path.rsplit(".", 1)

        try:
            mod = importlib.import_module(module_name)
            if not hasattr(mod, class_name):
                raise ImportError(f"{module_name} 缺少 {class_name}")
            resolved += 1
        except ImportError:
            unresolved.append(f"{blindspot_id} → {module_path}")

    total = len(BLINDSPOT_TO_CODE)
    coverage = resolved / total * 100

    print(f"Blindspot Coverage: {resolved}/{total} ({coverage:.1f}%)")

    if unresolved:
        print(f"\nUnresolved blindspots ({len(unresolved)}):")
        for u in unresolved:
            print(f"  - {u}")

    assert coverage >= 80, f"Coverage too low: {coverage:.1f}%"


if __name__ == "__main__":
    test_blindspot_coverage()
