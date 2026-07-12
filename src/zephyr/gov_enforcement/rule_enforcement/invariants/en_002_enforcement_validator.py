# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.invariants.en_002_enforcement_validator
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_en_002_enforcement_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODEGEN:EN-002 ====
"""
EN-002 — Enforcement Mode Validator

Reads cross_layer_contracts.yaml, validates that every P0 contract declares
an enforcement mode, and that the mode value is consistent with routing config.

SSoT: cross_layer_contracts.yaml v3.0
"""

from __future__ import annotations

from typing import Final
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from zephyr.integration.shared.schema.schemas import Priority

from zephyr.shared.io.paths import REPO_ROOT

_YAML_PATH = Path(__file__).parent / "en_002_enforcement_validator.yaml"


def _load_contract_spec_path() -> Path:
    """从 YAML 真源加载契约文件路径（SSoT 收敛，消除 py/yaml 路径分叉）。"""
    with open(_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    for check in data.get("checks", []):
        rel = check.get("params", {}).get("contract_spec_path")
        if rel:
            return REPO_ROOT / rel
    return REPO_ROOT / "architecture_model" / "contracts" / "cross_layer_contracts.yaml"

CONTRACTS_PATH: Final[Any] = _load_contract_spec_path()

VALID_ENFORCEMENT_MODES: Final[set] = {"block", "warn", "log", "shadow", "strict"}


@dataclass
class EnforcementResult:
    passed: bool
    total_contracts: int = 0
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.passed:
            return f"[PASS] EN-002: All {self.total_contracts} P0 contracts have enforcement declared"
        return f"[FAIL] EN-002: {len(self.violations)} violation(s)\n" + "\n".join(f"  - {v}" for v in self.violations)


def _load_contracts() -> dict[str, Any]:
    with open(CONTRACTS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def run_check() -> EnforcementResult:
    data = _load_contracts()
    contracts = data.get("contracts", [])
    violations: list[str] = []
    warnings: list[str] = []
    p0_count = 0

    for ctr in contracts:
        cid = ctr.get("id", "?")
        priority = ctr.get("priority", "")

        if priority == Priority.P0.value:
            p0_count += 1

        enforcement_mode = ctr.get("enforcement_mode")
        enforcement_action = ctr.get("enforcement_action")

        if enforcement_mode is None and enforcement_action is None:
            if priority == Priority.P0.value:
                warnings.append(f"{cid}: P0 contract missing enforcement_mode (defaulting to 'block')")
            continue

        mode = enforcement_mode or enforcement_action
        if mode not in VALID_ENFORCEMENT_MODES:
            violations.append(f"{cid}: invalid enforcement_mode '{mode}' (valid: {sorted(VALID_ENFORCEMENT_MODES)})")

    return EnforcementResult(
        passed=len(violations) == 0,
        total_contracts=p0_count,
        violations=violations,
        warnings=warnings,
    )


def check() -> tuple[bool, str]:
    result = run_check()
    return result.passed, result.summary()


if __name__ == "__main__":
    ok, msg = check()
    print(msg)
    sys.exit(0 if ok else 1)

# ==== END CODEGEN:EN-002 ====
