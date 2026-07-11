# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.policy_tree_validator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/rule_enforcement/test_policy_tree_validator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/code_dedup/test_policy_tree_validator.py
# [A_module] module_id=MOD-UNK_policy_tree_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""策略树自动一致性校验器 — 虚线箭头影响分析."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ValidationViolation:
    path: str = ""
    rule: str = ""
    actual: object = None
    expected: object = None
    severity: str = "WARN"


@dataclass
class PolicyTreeReport:
    valid: bool = False
    violations: list[ValidationViolation] = field(default_factory=list)
    impact_analysis: str = ""


class PolicyTreeValidator:
    """策略树一致性 + 影响分析."""

    _REQUIRED_KEYS: dict[str, type] = {
        "version": str,
        "cloning_detection": dict,
        "thresholds": dict,
        "auto_fix": dict,
        "monoculture_immunity": dict,
        "simplicity_audit": dict,
    }

    def validate(self, policy: dict[str, Any]) -> PolicyTreeReport:
        """校验策略树完整性."""
        violations: list[ValidationViolation] = []

        for key, expected_type in self._REQUIRED_KEYS.items():
            if key not in policy:
                violations.append(
                    ValidationViolation(
                        path=f"root.{key}",
                        rule="required_key_missing",
                        actual=None,
                        expected=expected_type.__name__,
                        severity="ERROR",
                    )
                )
            elif not isinstance(policy[key], expected_type):
                violations.append(
                    ValidationViolation(
                        path=f"root.{key}",
                        rule="type_mismatch",
                        actual=type(policy[key]).__name__,
                        expected=expected_type.__name__,
                        severity="ERROR",
                    )
                )

        if "thresholds" in policy and isinstance(policy["thresholds"], dict):
            t = policy["thresholds"]
            for th_key in ["high_confidence", "medium_confidence", "low_confidence"]:
                if th_key in t and not (0 < t[th_key] <= 1):
                    violations.append(
                        ValidationViolation(
                            path=f"thresholds.{th_key}",
                            rule="out_of_range",
                            actual=t[th_key],
                            expected="0.0-1.0",
                            severity="ERROR",
                        )
                    )

        if "auto_fix" in policy and isinstance(policy["auto_fix"], dict):
            af = policy["auto_fix"]
            if af.get("doom_loop_max_attempts", 0) < 1:
                violations.append(
                    ValidationViolation(
                        path="auto_fix.doom_loop_max_attempts",
                        rule="must_be_positive",
                        actual=af["doom_loop_max_attempts"],
                        expected=">=1",
                        severity="WARN",
                    )
                )

        valid = len([v for v in violations if v.severity == "ERROR"]) == 0

        impact = self._analyze_impact(policy, violations)

        return PolicyTreeReport(
            valid=valid,
            violations=violations,
            impact_analysis=impact,
        )

    def validate_from_file(self, config_path: str | Path) -> PolicyTreeReport:
        """从 Python config 对象校验."""
        from zephyr.governance.code_dedup.config import POLICY_TREE

        return self.validate(POLICY_TREE)

    @staticmethod
    def _analyze_impact(policy: dict[str, Any], violations: list[ValidationViolation]) -> str:
        if not violations:
            return "策略树配置一致——无虚线箭头影响"
        error_count = sum(1 for v in violations if v.severity == "ERROR")
        if error_count > 0:
            return f"策略树有{error_count}个ERROR级违规——引擎可能降级运行"
        return f"策略树有{len(violations)}个WARN级警告——引擎可正常运行"
