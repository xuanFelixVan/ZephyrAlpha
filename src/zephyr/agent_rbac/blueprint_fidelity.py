# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.blueprint_fidelity

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""蓝图保真——验证实现与蓝图一致性:字段数/API签名/异常类型/导入路径."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class FidelityCheck(BaseModel):
    module: str
    check_type: str
    expected: str
    actual: str
    match: bool


class BlueprintFidelity:
    def __init__(self) -> None:
        self._checks: list[FidelityCheck] = []

    def check_field_count(self, module: str, expected: int, actual: int) -> FidelityCheck:
        fc = FidelityCheck(
            module=module,
            check_type="field_count",
            expected=str(expected),
            actual=str(actual),
            match=expected == actual,
        )
        self._checks.append(fc)
        return fc

    def check_api_contract(self, module: str, func_name: str, expected_params: list[str], actual_params: list[str]) -> FidelityCheck:
        match = set(expected_params) == set(actual_params)
        fc = FidelityCheck(
            module=module,
            check_type=f"api_contract:{func_name}",
            expected=str(sorted(expected_params)),
            actual=str(sorted(actual_params)),
            match=match,
        )
        self._checks.append(fc)
        return fc

    def summary(self) -> dict[str, Any]:
        total = len(self._checks)
        passed = sum(1 for c in self._checks if c.match)
        return {"total_checks": total, "passed": passed, "failed": total - passed, "fidelity_pct": passed / max(total, 1) * 100}
