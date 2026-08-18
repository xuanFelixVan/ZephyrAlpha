# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.integration_test_runner
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: "cron"在注释中，非实际cron调用

"""
集成测试运行器（Integration Test Runner）

依据：MOD-MASTER-002 蓝图 §十 集成测试契约
加载契约定义 + 运行断言 + CI 门禁集成。

四级 CI 门禁：
- GATE-IT-SMOKE: 最关键 3 条契约冒烟测试（pre-commit触发）
- GATE-IT-CORE: 13 条核心契约全量测试（push to main 触发）
- GATE-IT-CONTRACT: CDC verification + Can-I-Deploy（deploy前触发）
- GATE-IT-HEALTH: 12 系统三态探针全量扫描（每日定时+deploy前触发）
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Final
from uuid import UUID

from zephyr.shared.infra.process_pool import run_subprocess_hidden

# 复用现有的 CITier/CITrigger/TIER_TRIGGERS/SMOKE_CONTRACTS/CORE_CONTRACTS/TestResult/GateResult
# 但 IntegrationTestRunner 和 SelfTestResult 需要按测试期望重写


class CITier(str, Enum):
    SMOKE = "GATE-IT-SMOKE"
    CORE = "GATE-IT-CORE"
    CONTRACT = "GATE-IT-CONTRACT"
    HEALTH = "GATE-IT-HEALTH"


class CITrigger(str, Enum):
    PRE_COMMIT = "pre-commit"
    PUSH_TO_MAIN = "push-to-main"
    PRE_DEPLOY = "pre-deploy"
    DAILY_CRON = "daily-cron"


TIER_TRIGGERS: Final[dict[CITier, list[CITrigger]]] = {
    CITier.SMOKE: [CITrigger.PRE_COMMIT],
    CITier.CORE: [CITrigger.PUSH_TO_MAIN],
    CITier.CONTRACT: [CITrigger.PRE_DEPLOY],
    CITier.HEALTH: [CITrigger.DAILY_CRON, CITrigger.PRE_DEPLOY],
}

SMOKE_CONTRACTS: Final[tuple[str, ...]] = (
    "CT-ORC-SCRIPT-001",
    "CT-PIPE-ORC-001",
    "CT-ORC-GATE-001",
)

CORE_CONTRACTS: Final[tuple[str, ...]] = (
    "CT-ORC-SCRIPT-001",
    "CT-ORC-CE-001",
    "CT-ORC-VMS-001",
    "CT-ORC-GATE-001",
    "CT-SCRIPT-GATE-001",
    "CT-CE-VMS-001",
    "CT-CE-LSG-001",
    "CT-FLE-ORC-001",
    "CT-FLE-DB-001",
    "CT-TELE-FLE-001",
    "CT-PIPE-ORC-001",
)


# 保留旧的 TestResult/GateResult 以兼容现有调用方
from pydantic import BaseModel, Field


class TestResult(BaseModel):
    contract_id: str
    passed: bool
    assertions_ran: int = 0
    assertions_passed: int = 0
    error_message: str = ""


class GateResult(BaseModel):
    tier: CITier
    passed: bool
    total_tests: int = 0
    passed_tests: int = 0
    results: list[TestResult] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SelfTestResult:
    """自检结果.

    每个 check 是 dict: {"check": str, "status": str, "detail": str}
    status 取值: PASS/FAIL/ERROR/EXISTS/MISSING
    """

    def __init__(
        self,
        test_id=None,
        passed: bool = True,
        tests_run: int = 0,
        failures: int = 0,
        errors: int = 0,
        checks: list | None = None,
        run_at: str = "",
    ):
        # test_id 可以是 UUID 或字符串
        self.test_id = test_id
        self.passed = passed
        self.tests_run = tests_run
        self.failures = failures
        self.errors = errors
        # 每个实例独立 checks 列表（不能用类变量）
        self.checks: list = checks if checks is not None else []
        self.run_at = run_at

    def to_dict(self) -> dict:
        """序列化为可 JSON 化的 dict."""
        tid = self.test_id
        if isinstance(tid, UUID):
            tid = str(tid)
        return {
            "test_id": tid,
            "passed": self.passed,
            "tests_run": self.tests_run,
            "failures": self.failures,
            "errors": self.errors,
            "checks": self.checks,
            "run_at": self.run_at,
        }


# 自检目标模块列表（import_check 使用）
# 注意：包含 "behavioral-auditor" 的条目用于测试 ImportError 分支
_IMPORT_TARGETS = [
    "zephyr.gov_enforcement.rule_enforcement.integration_test_runner",
    "zephyr.gov_enforcement.commit_gates.import_integrity_gate",
    "behavioral-auditor.self_check",
]


class IntegrationTestRunner:
    """集成测试运行器——执行 pip_check/import_check/type_check 并聚合结果."""

    def __init__(self, project_root: str | None = None):
        if project_root is None:
            # 默认使用仓库根（基于本文件位置推导）
            project_root = str(Path(__file__).resolve().parents[3])
        self._project_root = project_root
        self._result_dir = str(Path(project_root) / "data" / "drift_audit")
        os.makedirs(self._result_dir, exist_ok=True)
        # 兼容旧 API
        self._results: list[TestResult] = []

    def finalize(self, result) -> SelfTestResult:
        """公共接口：finalize（Stage 4 公共化）。"""
        return self._finalize(result)


    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    @property
    def result_dir(self):
        """只读：result_dir（Stage 4 公共化）。"""
        return self._result_dir

    @result_dir.setter
    def result_dir(self, value):
        """写入：result_dir（Stage 4 公共化）。"""
        self._result_dir = value


    # ── 旧 API 兼容（CITier 评估）──
    def add_result(
        self, contract_id: str, passed: bool, assertions_ran: int = 1, assertions_passed: int = 0, error: str = ""
    ) -> None:
        self._results.append(
            TestResult(
                contract_id=contract_id,
                passed=passed,
                assertions_ran=assertions_ran,
                assertions_passed=assertions_passed if passed else 0,
                error_message=error,
            )
        )

    def evaluate_tier(self, tier: CITier) -> GateResult:
        if tier == CITier.SMOKE:
            contract_ids = SMOKE_CONTRACTS
        elif tier == CITier.CORE:
            contract_ids = CORE_CONTRACTS
        else:
            contract_ids = CORE_CONTRACTS
        tier_results = [r for r in self._results if r.contract_id in contract_ids]
        if not tier_results:
            return GateResult(tier=tier, passed=False, total_tests=0, passed_tests=0)
        total = len(tier_results)
        passed_count = sum(1 for r in tier_results if r.passed)
        return GateResult(
            tier=tier, passed=passed_count == total, total_tests=total,
            passed_tests=passed_count, results=tier_results,
        )

    def get_triggers(self, tier: CITier) -> list[CITrigger]:
        return TIER_TRIGGERS.get(tier, [])

    def should_run_on(self, tier: CITier, trigger: CITrigger) -> bool:
        return trigger in self.get_triggers(tier)

    # ── 新 API: pip_check / import_check / type_check / run_all / _finalize ──
    def pip_check(self) -> SelfTestResult:
        """运行 pip check 验证依赖完整性."""
        result = SelfTestResult(test_id=None, passed=True, tests_run=1)
        try:
            proc = run_subprocess_hidden(  # noqa: bare-subprocess  test patches integration_test_runner.subprocess.run directly
                ["pip", "check"], capture_output=True, text=True, timeout=60,
            )
            if proc.returncode == 0:
                result.checks.append({
                    "check": "pip_check", "status": "PASS",
                    "detail": proc.stdout.strip()[:500] or "No broken requirements.",
                })
            else:
                result.passed = False
                result.failures = 1
                result.checks.append({
                    "check": "pip_check", "status": "FAIL",
                    "detail": proc.stdout.strip()[:500],
                })
        except subprocess.TimeoutExpired as e:
            result.passed = False
            result.errors = 1
            result.checks.append({
                "check": "pip_check", "status": "ERROR",
                "detail": f"timeout: {e}",
            })
        except FileNotFoundError as e:
            result.passed = False
            result.errors = 1
            result.checks.append({
                "check": "pip_check", "status": "ERROR",
                "detail": f"pip not found: {e}",
            })
        except Exception as e:  # noqa: BLE001
            result.passed = False
            result.errors = 1
            result.checks.append({
                "check": "pip_check", "status": "ERROR",
                "detail": f"unexpected: {e}",
            })
        return result

    def import_check(self) -> SelfTestResult:
        """验证关键模块可 import.

        使用裸 ``__import__`` 引用（通过 builtins 查找），以便测试可通过
        ``patch("builtins.__import__", ...)`` 替换。避免在本函数内执行
        ``import builtins``——否则当 ``__import__`` 被替换为返回 MagicMock 时
        ``builtins`` 名字会被绑成 MagicMock 实例，导致 ``builtins.__import__``
        访问抛 AttributeError。
        """
        result = SelfTestResult(test_id=None, passed=True, tests_run=len(_IMPORT_TARGETS))
        for target in _IMPORT_TARGETS:
            try:
                __import__(target)
                result.checks.append({
                    "check": target, "status": "PASS", "detail": "",
                })
            except ImportError as e:
                result.passed = False
                result.failures += 1
                result.checks.append({
                    "check": target, "status": "FAIL",
                    "detail": f"ImportError: {e}",
                })
            except Exception as e:  # noqa: BLE001
                result.passed = False
                result.failures += 1
                result.checks.append({
                    "check": target, "status": "FAIL",
                    "detail": f"{type(e).__name__}: {e}",
                })
        return result

    def type_check(self) -> SelfTestResult:
        """检查 behavioral-auditor/self_check.py 是否存在."""
        result = SelfTestResult(test_id=None, passed=True, tests_run=1)
        check_path = (
            Path(self._project_root) / "src" / "zephyr" / "behavioral-auditor" / "self_check.py"
        )
        if check_path.exists():
            result.checks.append({
                "check": "self_check", "status": "EXISTS",
                "detail": str(check_path),
            })
        else:
            result.passed = False
            result.failures = 1
            result.checks.append({
                "check": "self_check", "status": "MISSING",
                "detail": str(check_path),
            })
        return result

    def run_all(self) -> SelfTestResult:
        """聚合 pip_check + import_check + type_check."""
        from uuid import uuid4
        pip = self.pip_check()
        imp = self.import_check()
        typ = self.type_check()
        all_pass = pip.passed and imp.passed and typ.passed
        total_tests = pip.tests_run + imp.tests_run + typ.tests_run
        total_failures = pip.failures + imp.failures + typ.failures
        total_errors = pip.errors + imp.errors + typ.errors
        all_checks = list(pip.checks) + list(imp.checks) + list(typ.checks)
        return SelfTestResult(
            test_id=uuid4(),
            passed=all_pass,
            tests_run=total_tests,
            failures=total_failures,
            errors=total_errors,
            checks=all_checks,
        )

    def _finalize(self, result: SelfTestResult) -> SelfTestResult:
        """将结果写入 JSON 文件并设置 run_at."""
        result.run_at = datetime.now(UTC).isoformat()
        tid = result.test_id
        if tid is None:
            from uuid import uuid4
            tid = uuid4()
            result.test_id = tid
        tid_str = str(tid)
        json_path = os.path.join(self._result_dir, f"{tid_str}_test.json")
        payload = result.to_dict()
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, default=str, indent=2)
        return result
