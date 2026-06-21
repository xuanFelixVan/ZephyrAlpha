# [A_module] module_id=MOD-GOV_ct_enforcement_mode_check | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_enforcement_mode_check

# [INVARIANTS] MOD-INF-007 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateError

# [TESTS] tests/gates/

"""[BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

EnforcementModeCheckHandler — EnforcementModeCheckHandler

依据: 蓝图 MOD-INF-007 §3-§7

"""




from __future__ import annotations





from typing import Any





from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type


from zephyr.governance.rule_enforcement.task_types import Task








@register_check_type


class EnforcementModeCheckHandler(CheckTypeHandler):


    name = "enforcement_mode_check"





    def run(


        self,


        task: Task,


        params: dict[str, Any],


        check: Any,


        project_root: Any,


    ) -> list[dict[str, Any]]:


                violations = []


                try:


                    from zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator import run_check as en2_check


                    result = en2_check()


                    if not result.passed:


                        for v in result.violations:


                            violations.append({"message": v, "severity": check.severity})


                except Exception as exc:


                    violations.append({"message": f"EN-002 check failed: {exc}", "severity": "P2"})


                return violations


