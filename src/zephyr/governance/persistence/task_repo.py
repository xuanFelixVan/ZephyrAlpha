# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.governance.persistence.task_repo
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.task_repo
# [CONSUMERS] zephyr.frontend.dashboard.app; zephyr.governance.phase_check_registry; zephyr.governance._service_registration; zephyr.governance.audit_orchestration.finding_bridge; zephyr.governance.ops_governance.phase_check_registry; zephyr.infra_ops.dashboard.app; zephyr.infrastructure.db.task_repo; zephyr.integration.pipeline_orchestrator; zephyr.infrastructure.pipeline.preemption_manager; zephyr.infrastructure.rollback.phase_check_registry; zephyr.trading.auto_dispatcher; zephyr.trading.autopilot; zephyr.trading.auto_runtime_core; zephyr.trading.boot_cron_jobs; zephyr.trading.boot_hooks; zephyr.trading.conductor; zephyr.trading.ide_health_daemon; zephyr.trading.orchestrator.alert_handler; zephyr.trading.orchestrator.finding_bridge; scripts.construction.check_statuses; scripts.construction.check_transition_code; scripts.construction.d_init_task_system; scripts.construction.test_event_hook; scripts.construction.finalize_tasks; scripts.governance.create_alignment_tasks; scripts.governance.task_self_check; scripts.governance.task_summary; scripts.governance.meta.create_task_from_finding; tests.test_autopilot; tests.test_auto_split; tests.test_boot_hooks_unlock; tests.test_core_models; tests.test_db_query; tests.test_db_transition; tests.test_mcp_task_claim; tests.test_rule_red_blue; tests.verify_b54_b56_b59_deep; tests.adversarial.test_task_system_red_team; tests.integration.test_gate_e2e; tests.integration.test_verify_b54_b56_b59_deep; tests.unit.test_gate_engine_unit; tests.unit.test_task_repo_unit; tests.unit.test_task_manager_mcp; tests.unit.db.test_dm400_stale_task_fix; tests.unit.db.test_gate_repo; tests.unit.db.test_task_repo_db; tests.unit.gates.test_gate_engine_gates; frontend.app
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# 代理模块：将 zephyr.governance.persistence.task_repo 重定向到 zephyr.governance.task_repo
from zephyr.governance.rule_enforcement.gate_types import GateViolationError
from zephyr.governance.task_repo import (
    InvalidTransitionError,
    P0InflationFrozenError,
    TaskNotFoundError,
    TaskRepository,
    allowed_transitions,
    is_terminal,
)

__all__ = [
    "GateViolationError",
    "InvalidTransitionError",
    "P0InflationFrozenError",
    "TaskNotFoundError",
    "TaskRepository",
    "allowed_transitions",
    "is_terminal",
]
