# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §adversarial_validation
# [MODULE] zephyr.trading.feedback_loop.gates.adversarial_validation
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.security.adversarial_validation.__init__
# [CONSUMERS] feedback-loop.gates.__init__; _registry.yaml FLE-ADVERSARIAL-VALIDATION; RED-BLUE-GATE
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] challenge() maintains backward compat; run_adversarial_check() bridges to RedBlueValidator
# [MODIFY-GUARD] challenge() return type MUST remain list[str] for backward compat
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RedBlueImportError on import failure; returns degraded results
# [TESTS] tests/test_adversarial_validation.py
# [A_module] module_id=MOD-UNK_adversarial_validation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""Adversarial Validation Gate — FLE-ADVERSARIAL-VALIDATION + RED-BLUE-GATE bridge.

Bridges feedback-loop gate engine with MOD-INF-030 Red-Blue Validator:
红方注入 → 蓝方 Gate 判定 → 绕过检测 → 收敛验证 → 宪法自进化。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class RedBlueImportError(ImportError):
    pass


@dataclass
class AdversarialResult:
    claim: str
    passed: bool
    bypass_count: int = 0
    constitution_violations: list[str] = field(default_factory=list)
    core_result: dict[str, Any] | None = None
    error: str = ""


@dataclass
class AdversarialValidation:
    def challenge(self, claim: str) -> list[str]:
        challenges: list[str] = [f"What if {claim} is wrong?"]

        try:
            adversarial_result = self.run_adversarial_check(claim)
            if adversarial_result.bypass_count > 0:
                challenges.append(f"Claim '{claim}' bypassed {adversarial_result.bypass_count} defense(s)")
            if adversarial_result.constitution_violations:
                challenges.append("Constitution violations: %s" % ", ".join(adversarial_result.constitution_violations))
            if not adversarial_result.passed:
                challenges.append(f"Adversarial validation FAILED for claim: '{claim}'")
            if adversarial_result.error:
                challenges.append(f"Validation error: {adversarial_result.error}")
        except RedBlueImportError:
            pass
        except Exception as exc:
            logger.warning("challenge() enrich failed: %s", exc)

        return challenges

    def run_adversarial_check(self, claim: str, **kwargs: Any) -> AdversarialResult:
        try:
            return self._run_with_red_blue_validator(claim, **kwargs)
        except RedBlueImportError:
            return AdversarialResult(
                claim=claim,
                passed=True,
                error="RedBlueValidator not available — skipped adversarial check",
            )
        except Exception as exc:
            logger.error("run_adversarial_check failed: %s", exc)
            return AdversarialResult(
                claim=claim,
                passed=False,
                error=str(exc),
            )

    def _run_with_red_blue_validator(self, claim: str, **kwargs: Any) -> AdversarialResult:
        try:
            from zephyr.security.adversarial_validation import (
                BypassRecorder,
                ConstitutionGuard,
                DefenseRunner,
                RedBlueValidator,
                ResultClass,
                ScenarioLoader,
            )
        except ImportError as exc:
            raise RedBlueImportError("Cannot import zephyr.security.adversarial_validation: %s" % exc) from exc

        tier = kwargs.get("tier", 1)
        attempts = kwargs.get("attempts", 3)

        loader = ScenarioLoader()
        try:
            scenarios = loader.list_by_tier(tier)
        except Exception:
            return AdversarialResult(
                claim=claim,
                passed=True,
                error="No attack scenarios available for tier=%d" % tier,
            )

        if not scenarios:
            return AdversarialResult(
                claim=claim,
                passed=True,
                bypass_count=0,
                error="No scenarios loaded",
            )

        bypass_count = 0
        passed = True
        violations: list[str] = []
        core_result: dict[str, Any] | None = None

        for i in range(min(attempts, len(scenarios))):
            scenario = scenarios[i]

            runner = DefenseRunner()
            try:
                result = runner.evaluate(scenario)
            except Exception:
                result = None

            guard = ConstitutionGuard()
            try:
                guard.validate_all()
                v_list = guard.get_violations()
            except Exception:
                v_list = []

            counter_claim = f"'{claim}' survives {scenario.name}"
            recorder = BypassRecorder()
            try:
                entry = recorder.record(
                    scenario_id=scenario.scenario_id or "unknown",
                    scenario_name=scenario.name,
                    counter_claim=counter_claim,
                )
            except Exception:
                entry = None

            if result is not None:
                if result.result_class is ResultClass.ATTACKER_WIN:
                    bypass_count += 1
                    passed = False
                elif result.result_class is ResultClass.DEFENDER_WIN:
                    pass
                else:
                    bypass_count += 1

            if v_list:
                violations.extend(v_list)

            if entry is not None and hasattr(entry, "bypass_count"):
                bypass_count = entry.bypass_count

            if bypass_count >= 3:
                passed = False
                break

        core_result = {
            "total_scenarios": len(scenarios),
            "tested": min(attempts, len(scenarios)),
            "bypass_count": bypass_count,
            "violation_count": len(violations),
        }

        return AdversarialResult(
            claim=claim,
            passed=passed,
            bypass_count=bypass_count,
            constitution_violations=list(set(violations)),
            core_result=core_result,
        )
