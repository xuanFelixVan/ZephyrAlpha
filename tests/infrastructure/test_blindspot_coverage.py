# [A_test] module_id: SRC-TST-1847 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-475 | docs/03_modules/_domain_governance/blueprint.md | §
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
    "A1_execretion_error_handling": "reliability/retry_handler.RetryHandler",
    "A2_dependency_timeout": "reliability/circuit_breaker.CircuitBreaker",
    "A3_task_card_validation": "core/models.TaskCard",
    "A4_decomposition_fidelity": "blueprint_decomposer.BlueprintDecomposer",
    "A5_context_overflow": "context-engine.ContextEngine",
    "A6_diff_accuracy": "reliability/diff_planner.DiffPlanner",
    "A7_forbidden_touch": "reliability/context_guard.ContextGuard",
    "A8_token_budget": "context-engine.ContextEngine",
    "A9_rto_sla": "sla/sla_monitor.SLAMonitor",
    "B1_lifecycle_states": "lifecycle/task_lifecycle_manager.TaskLifecycleManager",
    "B2_gate_integrity": "lifecycle/task_lifecycle_manager.GateID",
    "B3_scope_drift": "lifecycle/scope_guard.ScopeGuard",
    "B4_dependency_cycle": "dependency/dependency-graph.DependencyGraph",
    "B5_blueprint_sync": "sync/blueprint_code_sync.BlueprintCodeSyncService",
    "B6_rollback_instructions": "lifecycle/task_lifecycle_manager.TaskLifecycleManager",
    "B7_context_manifest": "context-engine.ContextEngine",
    "C1_owner_absent": "owner_absent.OwnerAbsent",
    "C2_autonomy_downgrade": "maintenance/autonomy_monitor.AutonomyMonitor",
    "C3_manual_override": "lifecycle/task_lifecycle_manager.TaskLifecycleManager",
    "C4_notification_throttle": "observability/notifier.Notifier",
    "C5_session_continuity": "session/session_continuity.SessionContinuity",
    "D1_trace_missing": "observability/trace_decorator.TraceCollector",
    "D2_cost_blind": "observability/cost_tracker.CostTracker",
    "D3_failure_unknown": "observability/failure_matcher.FailureMatcher",
    "D4_cli_invisible": "observability/cli_summary.CLISummary",
    "D5_healthcheck": "healthcheck_service.HealthcheckService",
    "E1_no_quality_gate": "quality/quality_monitor.QualityMonitor",
    "E2_no_lint": "quality/quality_monitor.QualityMonitor",
    "E3_prompt_versioning": "adaptation/prompt_version_manager.PromptVersionManager",
    "E4_execution_tuning": "adaptation/execution_tuner.ExecutionTuner",
    "F1_no_saga": "compensation/saga_compensator.SagaCompensator",
    "F2_partial_compensation": "compensation/saga_compensator.SagaCompensator",
    "F3_compensation_order": "compensation/saga_compensator.SagaCompensator",
    "G1_event_propagation": "events/event_bus.EventBus",
    "G2_event_persistence": "events/event_store.EventStore",
    "G3_reaction_gap": "events/event_reactor.EventReactor",
    "G4_hook_dispatch": "events/hook_dispatcher.HookDispatcher",
    "G5_task_scheduling": "queue/task_scheduler.TaskScheduler",
    "G6_task_queue": "queue/task_queue.TaskQueue",
    "G7_impact_propagation": "impact/impact_propagator.ImpactPropagator",
    "G8_semantic_impact": "impact/llm_impact_analyzer.LLMImpactAnalyzer",
    "H1_ke_structuring": "knowledge/ke_structurer.KEStructurer",
    "H2_ke_linking": "knowledge/ke_linker.KELinker",
    "H3_kms_interface": "knowledge/kms_interface.KMSInterface",
    "H4_draft_assistant": "draft/draft_assistant.DraftAssistant",
}


def test_blindspot_coverage() -> None:
    resolved = 0
    unresolved: list[str] = []

    for blindspot_id, module_path in BLINDSPOT_TO_CODE.items():
        module_name, class_name = module_path.rsplit(".", 1)

        try:
            importlib.import_module(f"zephyr.orchestrator.core.{module_name}")
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
