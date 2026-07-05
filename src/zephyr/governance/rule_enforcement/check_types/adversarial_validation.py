# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.adversarial_validation
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.adversarial_validation; zephyr.governance.rule_enforcement.adversarial_strategies; zephyr.governance.rule_enforcement.check_types.check_type_registry; zephyr.governance.rule_enforcement.task_types
# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MOD-GATE_ENGINE 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GateError
# [TESTS] tests/test_adversarial_gate_integration.py
# [A_module] module_id=MOD-GOV_adversarial_validation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AdversarialValidation check type handler — registers with check_type_registry."""

from __future__ import annotations

from typing import Any

from zephyr.governance.rule_enforcement.adversarial_strategies import AdversarialSampleGenerator
from zephyr.governance.rule_enforcement.gate_engine.adversarial_validation import AdversarialValidationGate
from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


@register_check_type
class AdversarialValidationHandler(CheckTypeHandler):
    name = "adversarial_validation"

    def __init__(self) -> None:
        self._gate = AdversarialValidationGate()
        self._generator = AdversarialSampleGenerator()

    def run(
        self,
        task: Task,
        params: dict[str, Any],
        check: Any,
        project_root: Any,
    ) -> list[dict[str, Any]]:
        violations: list[dict[str, Any]] = []
        confidence_threshold = params.get("confidence_threshold", 0.7)
        strategies = params.get("strategies", [])

        output = params.get("output", "")
        if not output:
            desc = getattr(task, "description", "") or ""
            output = desc

        self._gate._confidence_threshold = confidence_threshold
        result = self._gate.validate(output, {"task_id": getattr(task, "task_id", "")})

        if not result.passed:
            violations.append(
                {
                    "message": "Adversarial validation failed: confidence=%.2f violations=%d"
                    % (result.confidence, len(result.violations)),
                    "severity": getattr(check, "severity", "P1"),
                    "details": {
                        "confidence": result.confidence,
                        "violations": result.violations,
                    },
                }
            )

        if strategies:
            test_results = self._gate.adversarial_test(output, strategies)
            for tr in test_results:
                if not tr.passed:
                    violations.append(
                        {
                            "message": "Adversarial strategy '%s' failed: score=%.2f" % (tr.strategy_name, tr.score),
                            "severity": getattr(check, "severity", "P1"),
                            "details": {
                                "strategy": tr.strategy_name,
                                "score": tr.score,
                            },
                        }
                    )

        return violations
