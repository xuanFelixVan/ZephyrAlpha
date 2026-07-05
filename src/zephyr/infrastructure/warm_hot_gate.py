# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.warm_hot_gate
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_warm_hot_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
M-14 WarmHotGate — Warm→Hot 阻断门
===================================
职责：在系统进入 Hot 状态前强制检查——确保所有 Warm 阶段验证通过后才能进入 Hot 真正执行阶段。
对标：K8s Admission Controller + CI/CD deployment gate
使用方式：
    gate = WarmHotGate()
    result = gate.check(operation_context)
    if result.blocked:
        raise WarmHotBlocked(result.reason)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

__all__ = [
    "GateCheckResult",
    "WarmHotGate",
    "WarmHotStatus",
]


class WarmHotStatus(str, Enum):
    PASSED = "passed"
    BLOCKED = "blocked"
    REQUIRES_APPROVAL = "requires_approval"
    SKIPPED = "skipped"


@dataclass
class GateCheckResult:
    status: WarmHotStatus
    reason: str = ""
    checks_performed: int = 0
    checks_passed: int = 0
    checks_failed: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return self.status == WarmHotStatus.BLOCKED

    @property
    def requires_approval(self) -> bool:
        return self.status.value in ("blocked", "requires_approval")


class WarmHotGate:
    """Warm→Hot 阻断门

    在系统状态从 Warm（准备就绪）切换到 Hot（真正执行）之前的最后一道闸门。
    检查项：
    1. 契约一致性验证
    2. 配置完整性检查
    3. 安全扫描结果
    4. 依赖可用性
    5. 资源充足性
    """

    def __init__(self, require_all_passed: bool = True):
        self._require_all = require_all_passed
        self._check_count: int = 0

    def check(
        self,
        context: dict[str, Any],
        verify_contracts: bool = True,
        verify_configs: bool = True,
        verify_dependencies: bool = True,
        verify_resources: bool = True,
    ) -> GateCheckResult:
        self._check_count += 1
        result = GateCheckResult(status=WarmHotStatus.PASSED)
        checks: list[tuple[bool, str]] = []

        if verify_contracts:
            checks.append(self._verify_contracts(context))

        if verify_configs:
            checks.append(self._verify_configs(context))

        if verify_dependencies:
            checks.append(self._verify_dependencies(context))

        if verify_resources:
            checks.append(self._verify_resources(context))

        result.checks_performed = len(checks)
        for passed, msg in checks:
            if passed:
                result.checks_passed += 1
            else:
                result.checks_failed.append(msg)

        if any(msg for p, msg in checks if not p and "BLOCKING" in msg.upper()):
            result.status = WarmHotStatus.BLOCKED
            result.blocking_issues = [msg for _, msg in checks if "BLOCKING" in msg.upper()]
        elif result.checks_failed and self._require_all:
            result.status = WarmHotStatus.BLOCKED
            result.blocking_issues = result.checks_failed[:]
        elif result.checks_failed:
            result.status = WarmHotStatus.REQUIRES_APPROVAL

        return result

    def _verify_contracts(self, context: dict) -> tuple[bool, str]:
        contract_paths = context.get("contracts", [])
        if not contract_paths:
            return True, "无契约文件需要验证"

        try:
            from zephyr.infrastructure.contract_tester import ContractTester

            tester = ContractTester(strict=True)
            for cpath in contract_paths:
                result = tester.test_contract(cpath)
                if not result.passed:
                    return False, f"BLOCKING 契约验证失败: {cpath} ({result.failure_count} failures)"
            return True, "所有契约验证通过"
        except ImportError:
            return False, "BLOCKING ContractTester不可用"

    def _verify_configs(self, context: dict) -> tuple[bool, str]:
        config_paths = context.get("configs", [])
        if not config_paths:
            return True, "无配置文件需要验证"

        try:
            from zephyr.infrastructure.config_validator import ConfigValidator

            validator = ConfigValidator()
            for cp in config_paths:
                result = validator.validate(cp, strict=True)
                if not result.valid:
                    return False, f"BLOCKING 配置验证失败: {cp} ({len(result.errors)} errors)"
            return True, "所有配置验证通过"
        except ImportError:
            return False, "BLOCKING ConfigValidator不可用"

    def _verify_dependencies(self, context: dict) -> tuple[bool, str]:
        required_modules = context.get("required_modules", [])
        for mod in required_modules:
            try:
                __import__(mod)
            except ImportError:
                return False, f"BLOCKING 依赖不可用: {mod}"
        return True, "所有依赖可用"

    def _verify_resources(self, context: dict) -> tuple[bool, str]:
        import shutil

        min_disk_free_mb = context.get("min_disk_free_mb", 100)
        import tempfile

        tmp_dir = tempfile.gettempdir()
        usage = shutil.disk_usage(tmp_dir)
        free_mb = usage.free / (1024 * 1024)
        if free_mb < min_disk_free_mb:
            return False, f"BLOCKING 磁盘空间不足: {free_mb:.0f}MB < {min_disk_free_mb}MB"
        return True, f"磁盘空间充足 ({free_mb:.0f}MB free)"

    @property
    def checks_performed(self) -> int:
        return self._check_count
