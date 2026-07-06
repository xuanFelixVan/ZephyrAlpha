# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §adversarial_validation
# [MODULE] zephyr.governance.rule_enforcement.gate_engine.adversarial_validation
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.rule_enforcement.check_types.adversarial_validation;zephyr.governance.rule_enforcement.gate_pipeline
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] validate() MUST return pass/fail with confidence; adversarial_test() MUST test all provided strategies
# [MODIFY-GUARD] blueprint.md §adversarial_validation; _registry.yaml
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AdversarialValidationError on invalid input
# [TESTS] tests/test_adversarial_validation_gate.py
# [A_module] module_id=MOD-GOV_adversarial_validation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AdversarialValidationGate — validates outputs against adversarial attacks."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

__all__: list[str] = [
    "AdversarialTestResult",
    "AdversarialValidationError",
    "AdversarialValidationGate",
    "ValidationResult",
]


class AdversarialValidationError(RuntimeError):
    error_code = "ZA-GV-0044"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


@dataclass
class ValidationResult:
    passed: bool
    confidence: float
    violations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AdversarialTestResult:
    strategy_name: str
    passed: bool
    score: float
    details: dict[str, Any] = field(default_factory=dict)


class AdversarialValidationGate:
    SAFETY_LEVEL = "H"

    def __init__(self, confidence_threshold: float = 0.7) -> None:
        self._confidence_threshold = confidence_threshold
        self._history: list[ValidationResult] = []

    def validate(self, output: str, context: dict[str, Any] | None = None) -> ValidationResult:
        context = context or {}
        violations: list[str] = []
        confidence = 1.0

        if not output or not output.strip():
            violations.append("Empty output")
            confidence = 0.0
            result = ValidationResult(passed=False, confidence=confidence, violations=violations)
            self._history.append(result)
            return result

        injection_patterns = [
            r"(?i)ignore\s+(previous|above|all|prior)\s+instructions",
            r"(?i)system\s*:\s*",
            r"(?i)you\s+are\s+now\s+",
            r"(?i)jailbreak",
            r"(?i)DAN\s+mode",
            r"(?i)\[ADMIN\]",
            r"(?i)DISREGARD\s+ALL",
            r"(?i)bypass\s+(all\s+)?(safety|filter)",
            r"(?i)developer\s+mode",
            r"\[EVASION",
            r"\[POISONED_DATA",
            r"\[MANIPULATED",
        ]
        for pattern in injection_patterns:
            if re.search(pattern, output):
                violations.append("Potential injection pattern detected: %s" % pattern)
                confidence -= 0.2

        if len(output) > 100000:
            violations.append("Output exceeds maximum length")
            confidence -= 0.1

        confidence = max(0.0, min(1.0, confidence))
        passed = confidence >= self._confidence_threshold and len(violations) == 0

        result = ValidationResult(
            passed=passed,
            confidence=confidence,
            violations=violations,
            details={"output_length": len(output), "context_keys": list(context.keys())},
        )
        self._history.append(result)
        logger.info(
            "AdversarialValidationGate: validate passed=%s confidence=%.2f violations=%d",
            passed,
            confidence,
            len(violations),
        )
        return result

    def adversarial_test(self, output: str, strategies: list[dict[str, Any]]) -> list[AdversarialTestResult]:
        results: list[AdversarialTestResult] = []
        for strategy in strategies:
            name = strategy.get("name", "unknown")
            test_type = strategy.get("type", "pattern")
            params = strategy.get("params", {})

            try:
                score = self._run_strategy_test(output, test_type, params)
                passed = score >= self._confidence_threshold
                results.append(
                    AdversarialTestResult(
                        strategy_name=name,
                        passed=passed,
                        score=score,
                        details={"test_type": test_type},
                    )
                )
            except Exception as exc:
                results.append(
                    AdversarialTestResult(
                        strategy_name=name,
                        passed=False,
                        score=0.0,
                        details={"error": str(exc)},
                    )
                )
                logger.error("AdversarialValidationGate: strategy %s failed: %s", name, exc)

        return results

    def _run_strategy_test(self, output: str, test_type: str, params: dict[str, Any]) -> float:
        if test_type == "pattern":
            patterns = params.get("patterns", [])
            matches = 0
            for pattern in patterns:
                if re.search(pattern, output):
                    matches += 1
            if not patterns:
                return 1.0
            return 1.0 - (matches / len(patterns))
        elif test_type == "length":
            max_length = params.get("max_length", 100000)
            if len(output) <= max_length:
                return 1.0
            return max(0.0, 1.0 - (len(output) - max_length) / max_length)
        elif test_type == "entropy":
            min_entropy = params.get("min_entropy", 0.1)
            if not output:
                return 0.0
            char_counts: dict[str, int] = {}
            for c in output:
                char_counts[c] = char_counts.get(c, 0) + 1
            import math

            entropy = -sum((count / len(output)) * math.log2(count / len(output)) for count in char_counts.values())
            max_entropy = math.log2(len(char_counts)) if len(char_counts) > 1 else 1.0
            normalized = entropy / max_entropy if max_entropy > 0 else 0.0
            return 1.0 if normalized >= min_entropy else normalized / min_entropy
        else:
            return 1.0

    def get_score(self, output: str) -> float:
        result = self.validate(output)
        return result.confidence

    def get_history(self) -> list[ValidationResult]:
        return list(self._history)


class AdversarialValidation:
    def __init__(self, config=None):
        self.config = config or {}

    def validate(self, target):
        return True

    def run_checks(self):
        return []
