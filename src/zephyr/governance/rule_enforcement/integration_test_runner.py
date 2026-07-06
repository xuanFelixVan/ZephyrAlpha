# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.integration_test_runner
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
# [A_module] module_id=MOD-GOV_integration_test_runner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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

from typing import Final
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


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
    "CT-SCRIPT-KB-001",
    "CT-SCRIPT-GATE-001",
    "CT-CE-VMS-001",
    "CT-CE-LSG-001",
    "CT-KB-VMS-001",
    "CT-FLE-ORC-001",
    "CT-FLE-DB-001",
    "CT-TELE-FLE-001",
    "CT-PIPE-ORC-001",
)


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


class IntegrationTestRunner:
    def __init__(self):
        self._results: list[TestResult] = []

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
            tier=tier,
            passed=passed_count == total,
            total_tests=total,
            passed_tests=passed_count,
            results=tier_results,
        )

    def get_triggers(self, tier: CITier) -> list[CITrigger]:
        return TIER_TRIGGERS.get(tier, [])

    def should_run_on(self, tier: CITier, trigger: CITrigger) -> bool:
        return trigger in self.get_triggers(tier)


class SelfTestResult:
    def __init__(self, test_name="", passed=True, duration=0.0, error=None, details=None):
        self.test_name = test_name
        self.passed = passed
        self.duration = duration
        self.error = error
        self.details = details or {}
