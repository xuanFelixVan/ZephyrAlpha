# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_contract_compatibility_check
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.check_types.check_type_registry; zephyr.governance.rule_enforcement.task_types; zephyr.governance.rule_enforcement.invariants.en_003_contract_compatibility
# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MOD-GATE_ENGINE 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateError
# [TESTS] tests/gates/
# [A_module] module_id=MOD-GOV_ct_contract_compatibility_check | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

ContractCompatibilityCheckHandler — ContractCompatibilityCheckHandler

依据: 蓝图 MOD-GATE_ENGINE §3-§7

"""

from __future__ import annotations

from typing import Any

from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


@register_check_type
class ContractCompatibilityCheckHandler(CheckTypeHandler):
    name = "contract_compatibility_check"

    def run(
        self,
        task: Task,
        params: dict[str, Any],
        check: Any,
        project_root: Any,
    ) -> list[dict[str, Any]]:
        violations = []

        try:
            from zephyr.governance.rule_enforcement.invariants.en_003_contract_compatibility import (
                run_check as en3_check,
            )

            result = en3_check()

            if not result.passed:
                for m in result.mismatches:
                    violations.append({"message": m, "severity": check.severity})

        except Exception as exc:
            violations.append({"message": f"EN-003 check failed: {exc}", "severity": "P2"})

        return violations
