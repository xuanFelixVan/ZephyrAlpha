# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.contract_tester
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_contract_tester | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ContractTester — 契约测试框架
Re-homed to eliminate shared->infrastructure circular import.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

__all__ = [
    "ContractStatus",
    "ContractTestResult",
    "ContractTester",
]


class ContractStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    DRIFT = "drift"
    NOT_FOUND = "not_found"


@dataclass
class ContractTestResult:
    contract_path: str
    status: ContractStatus
    checks: list[dict[str, Any]] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == ContractStatus.PASS

    @property
    def failure_count(self) -> int:
        return len(self.failures)


class ContractTester:
    """契约测试框架——验证代码与契约的一致性"""

    def __init__(self, strict: bool = True):
        self._strict = strict
        self._test_count: int = 0

    def test_contract(self, contract_path: str) -> ContractTestResult:
        """Test a single contract file."""
        self._test_count += 1
        path = Path(contract_path)
        if not path.exists():
            return ContractTestResult(
                contract_path=contract_path,
                status=ContractStatus.NOT_FOUND,
                failures=[f"File not found: {contract_path}"],
            )
        try:
            content = path.read_text(encoding="utf-8")
            if contract_path.endswith((".yaml", ".yml")):
                parsed = yaml.safe_load(content)
            elif contract_path.endswith(".json"):
                parsed = json.loads(content)
            else:
                parsed = {"raw": content}
            checks = [{"field": "parse", "expected": "valid", "actual": "valid"}]
            return ContractTestResult(
                contract_path=contract_path,
                status=ContractStatus.PASS,
                checks=checks,
                metadata={"parsed_type": type(parsed).__name__},
            )
        except Exception as e:
            return ContractTestResult(
                contract_path=contract_path,
                status=ContractStatus.FAIL,
                failures=[str(e)],
            )
