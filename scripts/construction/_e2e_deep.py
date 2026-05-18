# [BLUEPRINT] MOD-INF-005 | docs/03_modules/l01_infrastructure/governance-automation/blueprint.md | §
# [MODULE] scripts.construction._e2e_deep
# [INVARIANTS] 
# [MODIFY-GUARD] 
# [CONSUMERS] 
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 
# [TESTS] 
import sys, os
from pathlib import Path

ROOT = Path('D:/ZephyrAlpha')
sys.path.insert(0, str(ROOT / 'src'))

tests = [
    ('MOD-INF-016', 'zephyr.shared', ['AiAuditLogger', 'PermissionGuard', 'IdempotencyStore']),
    ('MOD-INF-012', 'zephyr.db', ['TaskRepository', 'ScriptManifestDB']),
    ('MOD-INF-035', 'zephyr.runtime', ['AutoRuntimeCore']),
    ('MOD-INF-002', 'zephyr._cross_layer', []),
    ('MOD-INF-013', 'zephyr.mcp', []),
    ('MOD-INF-006', 'zephyr.task_system', ['TaskRepository']),
    ('MOD-INF-007', 'zephyr.gate_engine', ['GateEngine']),
    ('MOD-INF-009', 'zephyr.pipeline', ['PipelineOrchestrator']),
    ('MOD-INF-005', 'zephyr.script_system', []),
    ('MOD-INF-008', 'zephyr.context_engine', []),
    ('MOD-INF-011', 'zephyr.vector_memory', []),
    ('MOD-INF-014', 'zephyr.llm_security', []),
    ('MOD-INF-034', 'zephyr.model_profiler', []),
    ('MOD-INF-036', 'zephyr.model_capability_exam', []),
    ('MOD-INF-018', 'zephyr.agent_rbac', ['PermissionGuard']),
    ('MOD-INF-019', 'zephyr.agent_spec', []),
    ('MOD-INF-020', 'zephyr.audit_trail', []),
    ('MOD-INF-021', 'zephyr.rollback', []),
    ('MOD-INF-022', 'zephyr.escalation_engine', []),
    ('MOD-INF-024', 'zephyr.budget_enforcer', []),
    ('MOD-INF-025', 'zephyr.l01_infrastructure.a2a_protocol', []),
    ('MOD-INF-010', 'zephyr.feedback_loop', []),
    ('MOD-INF-017', 'zephyr.l01_infrastructure.code_dedup_engine', []),
    ('MOD-INF-023', 'zephyr.behavioral_auditor', []),
    ('MOD-INF-033', 'zephyr.behavioral_auditor', []),
    ('MOD-INF-015', 'zephyr.l01_infrastructure.system_telemetry', []),
    ('MOD-INF-001', 'zephyr.capacity_assurance', []),
    ('MOD-INF-032', 'zephyr.core.lifecycle', []),
    ('MOD-INF-026', 'zephyr.asset_inventory', []),
    ('MOD-INF-027', 'zephyr._cross_layer.audit_orchestrator', []),
    ('MOD-INF-028', 'zephyr._cross_layer.semantic_auditor', []),
    ('MOD-INF-029', 'zephyr._cross_layer.orphan_judge', []),
    ('MOD-INF-030', 'zephyr._cross_layer.red_blue_validator', []),
    ('MOD-INF-031', 'zephyr.auto_fix_engine', []),
    ('MOD-KB-001', 'zephyr.kb', []),
    ('MOD-L00-001', 'zephyr.l00_data_ingestion', []),
    ('MOD-L02-001', 'zephyr.l02_alpha_factors', []),
    ('MOD-L03-001', 'zephyr.l03_signal_generation', []),
    ('MOD-L04-001', 'zephyr.l04_risk_management', []),
    ('MOD-L05-001', 'zephyr.l05_portfolio_construction', []),
    ('MOD-L06-001', 'zephyr.l06_trade_execution', []),
    ('MOD-L07-001', 'zephyr.l07_post_trade_analysis', []),
    ('MOD-L08-001', 'zephyr.l08_dashboard', []),
    ('MOD-L09-001', 'zephyr.l09_research', []),
    ('MOD-L10-001', 'zephyr.l10_compliance', []),
    ('MOD-L11-001', 'zephyr.l11_ml_platform', []),
    ('MOD-L13-001', 'zephyr.l13_experiment', []),
]

import_ok = 0
import_fail = 0
class_ok = 0
class_fail = 0
failures = []

for mid, mod_path, key_classes in tests:
    try:
        mod = __import__(mod_path, fromlist=[''])
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

        status = 'OK'
        if missing:
            status = 'MISSING: ' + ', '.join(missing)
            failures.append((mid, status))

    except Exception as e:
        import_fail += 1
        status = 'IMPORT_FAIL: ' + str(e)[:80]
        failures.append((mid, status))

print(f'Import OK: {import_ok}/{len(tests)}')
print(f'Import FAIL: {import_fail}/{len(tests)}')
print(f'Key classes found: {class_ok}')
print(f'Key classes missing: {class_fail}')
print()

if failures:
    print('Failures:')
    for mid, status in failures:
        print(f'  {mid}: {status}')
else:
    print('All modules import successfully, all key classes found!')
