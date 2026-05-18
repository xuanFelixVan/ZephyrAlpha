# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

# [MODULE] zephyr.gates.check_types.ct_content_quality

# [INVARIANTS] MOD-INF-007 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.gates 内部模块; zephyr.orchestrator

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateError

# [TESTS] tests/gates/

"""[BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

ContentQualityHandler — ContentQualityHandler

依据: 蓝图 MOD-INF-007 §3-§7

"""



from __future__ import annotations





from typing import Any





from zephyr.gates.check_types.check_type_registry import CheckTypeHandler, register_check_type


from zephyr.gates.task_types import Task








@register_check_type


class ContentQualityHandler(CheckTypeHandler):


    name = "content_quality"





    def run(


        self,


        task: Task,


        params: dict[str, Any],


        check: Any,


        project_root: Any,


    ) -> list[dict[str, Any]]:


                violations = []


                deliverables = list(task.deliverables or [])


                dep_paths = [project_root / p for p in deliverables]


                min_lines = int(params.get("min_lines", 5))


                for fp in dep_paths:


                    try:


                        lines = fp.read_text(encoding="utf-8").splitlines()


                    except (FileNotFoundError, UnicodeDecodeError):


                        continue


                    non_empty = [l for l in lines if l.strip() and not l.strip().startswith("#")]


                    if len(non_empty) < min_lines:


                        violations.append({"message": f"Empty shell: {fp} ({len(non_empty)} lines)", "severity": check.severity})


                return violations


