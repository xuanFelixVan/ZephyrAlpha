# [A_module] module_id=MOD-GOV_ct_drift_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_drift_budget

# [INVARIANTS] MOD-INF-007 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateError

# [TESTS] tests/gates/

from __future__ import annotations

"""[BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

DriftBudgetHandler — DriftBudgetHandler

依据: 蓝图 MOD-INF-007 §3-§7

"""





"""CheckType: drift_budget — 漂移预算检查 (T-V2-012 G1/G6 experimental)"""



from typing import Any





from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type


from zephyr.governance.rule_enforcement.task_types import Task








@register_check_type


class DriftBudgetHandler(CheckTypeHandler):


    name = "drift_budget"





    def run(


        self,


        task: Task,


        params: dict[str, Any],


        check: Any,


        project_root: Any,


    ) -> list[dict[str, Any]]:


                violations = []


                target_module = str(params.get("target_module", task.task_id))


                try:


                    from zephyr.behavioral_audit.drift_infrastructure import check_budget_for_gate


                    budget = check_budget_for_gate(target_module)


                    if not budget.get("allowed", False):


                        violations.append({"message": f"Drift budget exhausted for {target_module}", "severity": check.severity, "detail": budget.get("reason", "")})


                except Exception as exc:


                    violations.append({"message": f"drift_budget check failed (degrade P2): {exc}", "severity": "P2"})


                return violations


