# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

# [MODULE] zephyr.gates.check_types.ct_leverage_limit

# [INVARIANTS] MOD-INF-007 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.gates 内部模块; zephyr.orchestrator

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateError

# [TESTS] tests/gates/

"""[BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

LeverageLimitHandler — LeverageLimitHandler

依据: 蓝图 MOD-INF-007 §3-§7

"""



from __future__ import annotations





from typing import Any





from zephyr.gates.check_types.check_type_registry import CheckTypeHandler, register_check_type


from zephyr.gates.task_types import Task








@register_check_type


class LeverageLimitHandler(CheckTypeHandler):


    name = "leverage_limit"





    def run(


        self,


        task: Task,


        params: dict[str, Any],


        check: Any,


        project_root: Any,


    ) -> list[dict[str, Any]]:


                violations = []


                from zephyr.gates.risk_ssot import load_risk_params_ssot


                ssot = load_risk_params_ssot(project_root)


                lev = params.get("max_gross_leverage_default")


                cap = ssot.get("max_gross_leverage")


                if lev is not None and cap is not None and float(lev) > float(cap) + 1e-12:


                    violations.append({"message": f"G11 SSoT conflict: max_gross_leverage_default={lev} > {cap}", "severity": check.severity})


                return violations


