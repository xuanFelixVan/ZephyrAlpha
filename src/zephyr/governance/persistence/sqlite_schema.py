# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.governance.persistence.sqlite_schema
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.sqlite_schema
# [CONSUMERS] zephyr.frontend.dashboard.app; zephyr.governance.audit_schema; zephyr.governance.database_manager; zephyr.governance.dlq_retry_policy; zephyr.governance.event_store; zephyr.governance.gate_event_adapter; zephyr.governance.olap_engine; zephyr.governance.projection_engine; zephyr.governance.query_metrics; zephyr.governance.snapshot_manager; zephyr.governance.sqlite_dumper; zephyr.governance._service_registration; zephyr.governance.drift_detection.gate_persistence; zephyr.governance.drift_detection.trend_analyzer; zephyr.infra_ops.dashboard.app; zephyr.infrastructure.db.audit_schema; zephyr.infrastructure.db.olap_engine; zephyr.infrastructure.db.database_manager; zephyr.infrastructure.db.sqlite_schema; zephyr.infrastructure.db.query_metrics; zephyr.infrastructure.rollback.sqlite_dumper; zephyr.intelligence.model_evaluation.sync_engine; zephyr.ops.alert_dispatcher; zephyr.ops.db_bridge; zephyr.ops.db_writer; zephyr.ops.metrics_collector; zephyr.behavioral_audit.gate_persistence; zephyr.behavioral_audit.trend_analyzer; zephyr.security.access_control.orphan_judge.db; zephyr.trading.orchestrator.alert_handler; scripts.construction.check_statuses; scripts.construction.d_init_task_system; scripts.construction.reset_test_task; scripts.construction.test_event_hook; scripts.construction.finalize_tasks; scripts.governance.task_self_check; scripts.governance.task_summary; scripts.governance.meta.create_task_from_finding; tests.conftest; tests.test_event_store_stress; tests.integration.test_gate_e2e; tests.unit.test_audit_schema_unit; tests.unit.test_circuit_breaker_unit; tests.unit.test_context_injector_unit; tests.unit.test_graph_validator_unit; tests.unit.test_knowledge_activation_rate_unit; tests.unit.test_kb_repo_unit; tests.unit.test_olap_engine_unit; tests.unit.test_query_metrics_unit; tests.unit.test_rollback_manager_unit; tests.unit.test_sqlite_schema_unit; tests.unit.test_system_snapshot_unit; tests.unit.test_state_synchronizer_unit; tests.unit.test_task_repo_unit; tests.unit.test_wave_generator_unit; tests.unit.context_engine.test_context_injector_context_engine; tests.unit.context_engine.test_system_snapshot_context_engine; tests.unit.db.test_sqlite_schema_db; tests.unit.db.test_olap_engine_db; tests.unit.db.test_task_repo_db; tests.unit.gates.test_circuit_breaker_gates; tests.unit.kb.test_graph_validator_kb; tests.unit.kb.test_kb_repo; tests.unit.kb.test_knowledge_activation_rate_kb; tests.unit.orchestrator.test_state_synchronizer_orchestrator; tests.unit.orchestrator.test_rollback_manager_orchestrator; tests.unit.orchestrator.test_wave_generator_orchestrator; frontend.app
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# 代理模块：将 zephyr.governance.persistence.sqlite_schema 重定向到 zephyr.governance.sqlite_schema
from zephyr.governance.sqlite_schema import (
    DB_PATH,
    SchemaManager,
    get_db_connection,
    init_db,
    schema_version,
    table_names,
    view_names,
)

__all__ = [
    "DB_PATH",
    "SchemaManager",
    "get_db_connection",
    "init_db",
    "schema_version",
    "table_names",
    "view_names",
]
