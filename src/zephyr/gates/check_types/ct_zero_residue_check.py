# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

# [MODULE] zephyr.gates.check_types.ct_zero_residue_check

# [INVARIANTS] MOD-INF-007 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.gates 内部模块; zephyr.orchestrator

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateError

# [TESTS] tests/gates/

"""[BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

ZeroResidueCheckHandler — ZeroResidueCheckHandler

依据: 蓝图 MOD-INF-007 §3-§7

"""



from __future__ import annotations





from typing import Any





from zephyr.gates.check_types.check_type_registry import CheckTypeHandler, register_check_type


from zephyr.gates.task_types import Task








@register_check_type


class ZeroResidueCheckHandler(CheckTypeHandler):


    name = "zero_residue_check"





    def run(


        self,


        task: Task,


        params: dict[str, Any],


        check: Any,


        project_root: Any,


    ) -> list[dict[str, Any]]:


                violations = []


                try:


                    from zephyr.gates.invariants.zero_residue_check import ZeroResidueScanner


                    scanner = ZeroResidueScanner(project_root=project_root)


                    report = scanner.scan()


                    if not report.is_clean:


                        for fg in report.findings:


                            sev = "P0" if fg.severity == "error" else "P1"


                            violations.append({"message": fg.message, "severity": sev, "detail": f"[{fg.rule_id}] {fg.file_rel}"})


                except Exception as exc:


                    violations.append({"message": f"Zero residue scan failed: {exc}", "severity": "P2"})


                return violations


