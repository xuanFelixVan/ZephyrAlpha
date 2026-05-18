# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

# [MODULE] zephyr.gates.check_types.ct_frontmatter

# [INVARIANTS] MOD-INF-007 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.gates 内部模块; zephyr.orchestrator

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateError

# [TESTS] tests/gates/

"""[BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

FrontmatterHandler — FrontmatterHandler

依据: 蓝图 MOD-INF-007 §3-§7

"""



from __future__ import annotations





from typing import Any





from zephyr.gates.check_types.check_type_registry import CheckTypeHandler, register_check_type


from zephyr.gates.task_types import Task








@register_check_type


class FrontmatterHandler(CheckTypeHandler):


    name = "frontmatter"





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


                required_fields = list(params.get("required_fields", []))


                import re as _re


                for fp in dep_paths:


                    try:


                        text = fp.read_text(encoding="utf-8")


                    except (FileNotFoundError, UnicodeDecodeError):


                        continue


                    m = _re.match(r"^---\s*\n(.*?)\n---", text, _re.DOTALL)


                    if not m:


                        violations.append({"message": f"No frontmatter: {fp}", "severity": check.severity})


                        continue


                    import yaml as _yaml


                    try:


                        fm = _yaml.safe_load(m.group(1)) or {}


                    except Exception:


                        violations.append({"message": f"Invalid frontmatter YAML: {fp}", "severity": check.severity})


                        continue


                    for f in required_fields:


                        if f not in fm or not fm[f]:


                            violations.append({"message": f"Missing frontmatter field '{f}': {fp}", "severity": check.severity})


                return violations


