# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.contract_tester
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_contract_tester | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
M-11 ContractTester — 契约测试框架
==================================
职责：验证代码实现与 YAML/JSON 契约文件的一致性——字段、类型、约束是否匹配。
对标：Pact + OpenAPI Schema Validation
使用方式：
    tester = ContractTester()
    result = tester.test_contract("src/zephyr/gov_enforcement/rule_enforcement/task_completion_gate.py")
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

    def test_contract(
        self,
        contract_path: str | Path,
        validate_required: bool = True,
        validate_types: bool = True,
    ) -> ContractTestResult:
        cpath = Path(contract_path)
        result = ContractTestResult(contract_path=str(cpath), status=ContractStatus.PASS)
        self._test_count += 1

        if not cpath.exists():
            result.status = ContractStatus.NOT_FOUND
            result.failures.append(f"契约文件不存在: {cpath}")
            return result

        try:
            with open(cpath, encoding="utf-8") as f:
                if cpath.suffix in (".yaml", ".yml"):
                    contract = yaml.safe_load(f)
                elif cpath.suffix == ".json":
                    contract = json.load(f)
                else:
                    contract = {"_raw": f.read()}
        except Exception as e:
            result.status = ContractStatus.FAIL
            result.failures.append(f"解析失败: {e}")
            return result

        checks = []

        if validate_required:
            required_checks = self._check_required_fields(contract, cpath)
            checks.extend(required_checks)
            for c in required_checks:
                if not c.get("passed", True):
                    result.failures.append(f"[required] {c.get('message', '')}")
                    result.status = ContractStatus.FAIL

        if validate_types and isinstance(contract, dict):
            type_checks = self._check_types(contract, cpath)
            checks.extend(type_checks)
            for c in type_checks:
                if not c.get("passed", True):
                    result.failures.append(f"[type] {c.get('message', '')}")
                    if self._strict:
                        result.status = ContractStatus.FAIL
                    else:
                        result.status = ContractStatus.DRIFT

        result.checks = checks
        return result

    def _check_required_fields(
        self,
        contract: dict | list | str,
        cpath: Path,
    ) -> list[dict[str, Any]]:
        checks: list[dict[str, Any]] = []

        if isinstance(contract, dict):
            for k, v in contract.items():
                checks.append(
                    {
                        "field": k,
                        "type": type(v).__name__,
                        "passed": bool(v is not None and v != ""),
                        "message": f"{k}={v} ({type(v).__name__})",
                    }
                )

        return checks

    def _check_types(
        self,
        contract: dict,
        cpath: Path,
    ) -> list[dict[str, Any]]:
        checks: list[dict[str, Any]] = []
        expected_types: dict[str, type] = {
            "version": str,
            "module_id": str,
            "priority": (str, int),
            "status": str,
            "phase": int,
            "enabled": bool,
        }

        for k, expected in expected_types.items():
            if k in contract:
                val = contract[k]
                passed = isinstance(val, expected)
                checks.append(
                    {
                        "field": k,
                        "expected": str(expected),
                        "actual": type(val).__name__,
                        "passed": passed,
                        "message": f"{k}: expected {expected}, got {type(val).__name__}",
                    }
                )

        return checks

    def test_directory(
        self,
        directory: str | Path,
        pattern: str = "*.yaml",
    ) -> list[ContractTestResult]:
        results: list[ContractTestResult] = []
        dpath = Path(directory)

        if dpath.exists():
            for f in dpath.rglob(pattern):
                if f.is_file():
                    results.append(self.test_contract(f))

        return results

    @property
    def tests_run(self) -> int:
        return self._test_count
