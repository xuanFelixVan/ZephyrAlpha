# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

# [MODULE] zephyr.gates.check_types.ct_circular_dependency_scan

# [INVARIANTS] MOD-INF-007 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.gates 内部模块; zephyr.orchestrator

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateError

# [TESTS] tests/gates/

"""[BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

CircularDependencyScanHandler — CircularDependencyScanHandler

依据: 蓝图 MOD-INF-007 §3-§7

"""



from __future__ import annotations





from typing import Any





from zephyr.gates.check_types.check_type_registry import CheckTypeHandler, register_check_type


from zephyr.gates.task_types import Task








@register_check_type


class CircularDependencyScanHandler(CheckTypeHandler):


    name = "circular_dependency_scan"





    def run(


        self,


        task: Task,


        params: dict[str, Any],


        check: Any,


        project_root: Any,


    ) -> list[dict[str, Any]]:


                violations = []


                try:


                    from zephyr.gates.invariants.en_001_circular_dependency import run_scan


                    result = run_scan()


                    if not result.passed:


                        for cycle in result.cycles:


                            violations.append({"message": f"Circular dependency: {' -> '.join(cycle)} -> {cycle[0]}", "severity": check.severity})


                except Exception as exc:


                    violations.append({"message": f"EN-001 scan failed: {exc}", "severity": "P2"})


                return violations


