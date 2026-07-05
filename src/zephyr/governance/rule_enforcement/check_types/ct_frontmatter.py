# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_frontmatter
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.check_types.check_type_registry; zephyr.governance.rule_enforcement.task_types
# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MOD-GATE_ENGINE 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateError
# [TESTS] tests/gates/
# [A_module] module_id=MOD-GOV_ct_frontmatter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

FrontmatterHandler — FrontmatterHandler

依据: 蓝图 MOD-GATE_ENGINE §3-§7

"""

from __future__ import annotations

from typing import Any

from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


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
