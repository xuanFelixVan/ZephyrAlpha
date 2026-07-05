# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_fle_gate
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
# [A_module] module_id=MOD-GOV_ct_fle_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

FleGateHandler — FleGateHandler

依据: 蓝图 MOD-GATE_ENGINE §3-§7

"""

from __future__ import annotations

from typing import Any

from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


@register_check_type
class FleGateHandler(CheckTypeHandler):
    name = "fle_gate"

    def run(
        self,
        task: Task,
        params: dict[str, Any],
        check: Any,
        project_root: Any,
    ) -> list[dict[str, Any]]:
        violations = []

        gate_module = str(params.get("gate_module", ""))

        gate_method = str(params.get("gate_method", "check"))

        if not gate_module:
            violations.append({"message": "fle_gate missing gate_module", "severity": check.severity})

        else:
            try:
                import importlib

                mod = importlib.import_module(gate_module)

                candidates = [a for a in dir(mod) if isinstance(getattr(mod, a), type) and not a.startswith("_")]

                if not candidates:
                    violations.append(
                        {"message": f"FLE module {gate_module} has no usable class", "severity": check.severity}
                    )

                else:
                    gate_cls = getattr(mod, candidates[0])

                    try:
                        gate_inst = gate_cls()

                    except TypeError:
                        gate_inst = gate_cls

                    method = getattr(gate_inst, gate_method, None)

                    if method is None:
                        violations.append(
                            {"message": f"FLE {gate_module} has no {gate_method} method", "severity": check.severity}
                        )

                    else:
                        import inspect

                        sig = inspect.signature(method)

                        p = list(sig.parameters.keys())

                        result = method() if len(p) == 0 else method(task.task_id)

                        if isinstance(result, dict):
                            if not result.get("allowed", result.get("passed", result.get("ok", True))):
                                violations.append(
                                    {
                                        "message": f"FLE {gate_module}.{gate_method} rejected",
                                        "severity": check.severity,
                                        "detail": str(result),
                                    }
                                )

                        elif isinstance(result, bool) and not result:
                            violations.append(
                                {
                                    "message": f"FLE {gate_module}.{gate_method} returned False",
                                    "severity": check.severity,
                                }
                            )

            except Exception as exc:
                violations.append({"message": f"fle_gate init failed (degrade P2): {exc}", "severity": "P2"})

        return violations
