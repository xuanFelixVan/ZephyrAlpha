# [A_module] module_id=MOD-GOV_ct_circuit_breaker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_circuit_breaker

# [INVARIANTS] MOD-INF-007 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateError

# [TESTS] tests/gates/

"""[BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

CircuitBreakerHandler — CircuitBreakerHandler

依据: 蓝图 MOD-INF-007 §3-§7

"""




from __future__ import annotations





from typing import Any





from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type


from zephyr.governance.rule_enforcement.task_types import Task








@register_check_type


class CircuitBreakerHandler(CheckTypeHandler):


    name = "circuit_breaker"





    def run(


        self,


        task: Task,


        params: dict[str, Any],


        check: Any,


        project_root: Any,


    ) -> list[dict[str, Any]]:


                violations = []


                caller = str(params.get("caller_module", ""))


                target = str(params.get("target_module", ""))


                if not caller or not target:


                    violations.append({"message": "circuit_breaker check missing caller_module/target_module", "severity": "P2"})


                else:


                    try:


                        from zephyr.governance.rule_enforcement.circuit_breaker import CircuitBreakerCheck


                        cb = CircuitBreakerCheck(caller_module=caller, target_module=target)


                        if cb.is_open():


                            violations.append({"message": cb.violation_message(), "severity": check.severity})


                    except Exception as exc:


                        violations.append({"message": f"circuit_breaker init failed (degrade P2): {exc}", "severity": "P2"})


                return violations


