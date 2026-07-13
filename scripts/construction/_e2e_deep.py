# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.construction._e2e_deep
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.construction.check_statuses
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

ROOT = REPO_ROOT  # alias 真源
sys.path.insert(0, str(ROOT / "src"))

tests = [
    ("MOD-INF-016", "zephyr.shared", ["AiAuditLogger", "PermissionGuard", "IdempotencyStore"]),
    ("MOD-DATABASE", "zephyr.governance.persistence", ["TaskRepository", "ScriptManifestDB"]),
    ("MOD-INF-035", "zephyr.trading", ["AutoRuntimeCore"]),
    ("MOD-INF-002", "zephyr.shared._cross_layer", []),
    ("MOD-INF-013", "zephyr.integration.mcp", []),
    ("MOD-TASK_SYSTEM", "zephyr.task_system", ["TaskRepository"]),
    ("MOD-GATE_ENGINE", "zephyr.gate_engine", ["GateEngine"]),
    ("MOD-INF-009", "zephyr.infrastructure.pipeline", ["PipelineOrchestrator"]),
    ("MOD-INF-005", "zephyr.script_system", []),
    ("MOD-CONTEXT_ENGINE", "zephyr.autonomy_core", []),
    ("MOD-INF-011", "zephyr.integration.vector_memory", []),
    ("MOD-LLM_SECURITY", "zephyr.security.llm_defense.llm_security", []),
    ("MOD-INF-034", "zephyr.intelligence.model_profiling", []),
    ("MOD-INF-036", "zephyr.intelligence.model_profiling", []),
    ("MOD-INF-018", "zephyr.security.access_control", ["PermissionGuard"]),
    ("MOD-INF-019", "zephyr.autonomy_core", []),
    ("MOD-INF-020", "zephyr.governance.audit_trail", []),
    ("MOD-INF-021", "zephyr.infrastructure.rollback", []),
    ("MOD-INF-022", "zephyr.resilience.escalation", []),
    ("MOD-INF-024", "zephyr.resilience.budget_enforcement", []),
    ("MOD-INF-025", "zephyr.infrastructure.a2a_protocol", []),
    ("MOD-SHARED-001", "zephyr.shared.protocols.a2a", []),
    ("MOD-FEEDBACK_LOOP", "zephyr.feedback_loop", []),
    ("MOD-INF-017", "zephyr.testing.code_dedup", []),
    ("MOD-INF-023", "zephyr.governance.behavioral_auditor", []),
    ("MOD-INF-033", "zephyr.governance.behavioral_auditor", []),
    ("MOD-INF-015", "zephyr.observability.telemetry", []),
    ("MOD-INF-001", "zephyr.infrastructure.capacity_assurance", []),
    ("MOD-RESOURCE_OPTIMIZATION_ENGINE", "zephyr.infrastructure.shared_services.lifecycle", []),
    ("MOD-INF-026", "zephyr.data.asset_inventory", []),
    ("MOD-INF-027", "zephyr.shared._cross_layer.audit_orchestrator", []),
    ("MOD-INF-028", "zephyr.shared._cross_layer.semantic_auditor", []),
    ("MOD-INF-029", "zephyr.shared._cross_layer.orphan_judge", []),
    ("MOD-INF-030", "zephyr.shared._cross_layer.red_blue_validator", []),
    ("MOD-INF-031", "zephyr.infrastructure.auto_fix_engine", []),
    ("MOD-KB-001", "zephyr.data.knowledge_management.kb", []),
    ("MOD-L00-001", "zephyr.data", []),
    ("MOD-L02-001", "zephyr.portfolio.factors", []),
    ("MOD-L03-001", "zephyr.signal", []),
    ("MOD-L04-001", "zephyr.risk", []),
    ("MOD-L05-001", "zephyr.portfolio.core", []),
    ("MOD-L06-001", "zephyr.ex_core", []),
    ("MOD-L07-001", "zephyr.portfolio.core", []),
    ("MOD-L08-001", "zephyr.infrastructure.frontend", []),
    ("MOD-L09-001", "zephyr.research", []),
    ("MOD-L10-001", "zephyr.governance", []),
    ("MOD-L11-001", "zephyr.ml_train", []),
    ("MOD-L13-001", "zephyr.simulation", []),
]

import_ok = 0
import_fail = 0
class_ok = 0
class_fail = 0
failures = []

for mid, mod_path, key_classes in tests:
    try:
        mod = __import__(mod_path, fromlist=[""])
        import_ok += 1

        missing = []
        for cls_name in key_classes:
            found = hasattr(mod, cls_name)
            if not found:
                for attr in dir(mod):
                    if attr.lower() == cls_name.lower():
                        found = True
                        break
            if not found:
                missing.append(cls_name)
                class_fail += 1
            else:
                class_ok += 1

        status = "OK"
        if missing:
            status = "MISSING: " + ", ".join(missing)
            failures.append((mid, status))

    except Exception as e:
        import_fail += 1
        status = "IMPORT_FAIL: " + str(e)[:80]
        failures.append((mid, status))

print(f"Import OK: {import_ok}/{len(tests)}")
print(f"Import FAIL: {import_fail}/{len(tests)}")
print(f"Key classes found: {class_ok}")
print(f"Key classes missing: {class_fail}")
print()

if failures:
    print("Failures:")
    for mid, status in failures:
        print(f"  {mid}: {status}")
else:
    print("All modules import successfully, all key classes found!")
