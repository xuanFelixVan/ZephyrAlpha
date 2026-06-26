# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.models
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.models
# [CONSUMERS] zephyr.governance.audit_orchestration.batch_orchestrator; zephyr.governance.audit_orchestration.finding_bridge; zephyr.infrastructure.task_manager_server; zephyr.infrastructure.db.base_repo; zephyr.infrastructure.pipeline.ct_pipe_routing; zephyr.infrastructure.pipeline.model_router; zephyr.integration.pipeline_orchestrator; zephyr.integration.ct_pipe_routing; zephyr.integration.model_router; zephyr.integration.pipeline_orchestrator; zephyr.integration.mcp.task_manager_server; zephyr.shared.blueprint_decomposer; zephyr.trading.autopilot; zephyr.trading.conductor; zephyr.trading.orchestrator.alert_handler; zephyr.trading.orchestrator.batch_orchestrator; zephyr.trading.orchestrator.finding_bridge; scripts.construction.d_init_task_system; scripts.governance.meta.create_task_from_finding; tests.test_autopilot; tests.test_auto_split; tests.test_blueprint_decomposer; tests.test_boot_hooks_unlock; tests.test_core_models; tests.test_db; tests.adversarial.test_cross_layer_systems_red_team; tests.verify_b54_b56_b59_deep; tests.adversarial.test_task_system_red_team; tests.contract.test_schema_stability; tests.infrastructure.test_drift_e2e_pipeline; tests.integration.test_gate_e2e; tests.integration.test_pipeline_skill_injection; tests.integration.test_verify_b54_b56_b59_deep; tests.unit.test_gate_engine_unit; tests.unit.test_pipeline_orchestrator_unit; tests.unit.test_task_repo_unit; tests.unit.test_task_manager_mcp; tests.unit.db.test_task_repo_db; tests.unit.gates.test_gate_engine_gates; tests.unit.pipeline.test_pipeline_orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# Proxy module - redirects to actual location
# Created by create_shared_services_proxies.py
# Actual source: zephyr.shared.models
import importlib as _il

from zephyr.shared.models import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.models")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
