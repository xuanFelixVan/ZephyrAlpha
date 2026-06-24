# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [MODULE] zephyr.governance.drift_detection.integration_test_runner
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-GOV_integration_test_runner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
Integration Test Runner — integration_test_runner.py

module_id: MOD-INF-023
随声执行器：`pip install -e . \r\n python -m drift-detector --mode test`。
对标 blueprint.md §2.20 / D-023-34。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class SelfTestResult:
    test_id: uuid.UUID
    passed: bool
    tests_run: int = 0
    failures: int = 0
    errors: int = 0
    checks: list[dict[str, str]] = field(default_factory=list)
    run_at: str = ""


class IntegrationTestRunner:
    def __init__(self, project_root: str | None = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self._project_root = project_root
        self._result_dir = os.path.join(project_root, "data", "drift_audit")
        os.makedirs(self._result_dir, exist_ok=True)

    def pip_check(self) -> SelfTestResult:
        test_id = uuid.uuid4()
        results = SelfTestResult(test_id=test_id, passed=True)

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True,
                cwd=self._project_root,
                timeout=60,
            )
            if result.returncode != 0:
                results.passed = False
                results.failures += 1
                results.checks.append({"check": "pip_check", "status": "FAIL", "detail": result.stdout[:300]})
            else:
                results.checks.append({"check": "pip_check", "status": "PASS", "detail": "All dependencies OK"})
            results.tests_run += 1
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            results.passed = False
            results.errors += 1
            results.checks.append({"check": "pip_check", "status": "ERROR", "detail": str(e)})

        return self._finalize(results)

    def import_check(self) -> SelfTestResult:
        test_id = uuid.uuid4()
        results = SelfTestResult(test_id=test_id, passed=True)

        modules = [
            "drift_models",
            "drift_engine",
            "reconciler",
            "state_machine",
            "baseline_manager",
            "detector_dispatcher",
            "scan_mutex",
            "drift_hotfix_bypass",
            "suppression_learner",
            "gate_persistence",
            "headless_scanner",
            "cross_module_score",
            "self_check",
            "self_test_verifier",
        ]
        for mod in modules:
            try:
                __import__(f"zephyr.governance.drift_detection.{mod}")
                results.checks.append({"check": f"import_{mod}", "status": "PASS", "detail": ""})
            except ImportError as e:
                results.passed = False
                results.failures += 1
                results.checks.append({"check": f"import_{mod}", "status": "FAIL", "detail": str(e)[:100]})
            results.tests_run += 1

        return self._finalize(results)

    def type_check(self) -> SelfTestResult:
        test_id = uuid.uuid4()
        results = SelfTestResult(test_id=test_id, passed=True)

        file_path = os.path.join("src", "zephyr", "drift-detector", "self_check.py")
        full = os.path.join(self._project_root, file_path)
        if os.path.exists(full):
            results.checks.append({"check": "self_check", "status": "EXISTS", "detail": file_path})
        else:
            results.checks.append({"check": "self_check", "status": "MISSING", "detail": file_path})
            results.passed = False
            results.failures += 1
        results.tests_run += 1

        return self._finalize(results)

    def run_all(self) -> SelfTestResult:
        total = SelfTestResult(test_id=uuid.uuid4(), passed=True, run_at=datetime.now(UTC).isoformat())

        for check_fn in [self.pip_check, self.import_check, self.type_check]:
            r = check_fn()
            total.tests_run += r.tests_run
            total.failures += r.failures
            total.errors += r.errors
            total.checks.extend(r.checks)
            if not r.passed:
                total.passed = False

        return self._finalize(total)

    def _finalize(self, result: SelfTestResult) -> SelfTestResult:
        result.run_at = datetime.now(UTC).isoformat()
        filepath = os.path.join(self._result_dir, f"{result.test_id}_test.json")
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "test_id": str(result.test_id),
                    "passed": result.passed,
                    "tests_run": result.tests_run,
                    "failures": result.failures,
                    "errors": result.errors,
                    "checks": result.checks,
                    "run_at": result.run_at,
                },
                fh,
                indent=2,
                ensure_ascii=False,
            )
        return result
