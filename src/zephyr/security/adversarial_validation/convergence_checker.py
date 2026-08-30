# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.1 + §6.2 + §16 Phase 2a
# [MODULE] zephyr.security.adversarial_validation.convergence_checker
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models
# [CONSUMERS] validator.py ; escalation-engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 3 consecutive rounds without improvement -> EscalationEngine trigger; blocked_rate threshold 95%; bypass_count MUST decrease monotonically
# [MODIFY-GUARD] Convergence thresholds per blueprint §6.2; escalation logic MUST NOT be bypassed
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ConvergenceFailureError on 3-round stagnation; EscalationTriggerError on escalation failure
# [TESTS] tests/red_blue/test_convergence_checker.py
# [A_module] module_id=MOD-INF-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: convergence_checker.py
# 层: 算法
# - id: A1
#   name_zh: ① ConvergenceChecker
#   name_en: ConvergenceChecker
#   intro: class ConvergenceChecker 源码 L74-L152
#   desc: 公共方法（定义序）: check_convergence, evaluate_round, reset, round_history；源码 L74-L152
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ConvergenceChecker
#   downstream: validator.py ; escalation-engine
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from typing import Final

from zephyr.security.adversarial_validation.models import ConvergenceResult, RedBlueReport

logger = logging.getLogger(__name__)

__all__: list[str] = ["ConvergenceChecker", "ConvergenceFailureError"]

MAX_ROUNDS_WITHOUT_IMPROVEMENT: Final[int] = 3
BLOCKED_RATE_TARGET: Final[float] = 0.95
BYPASS_COUNT_TARGET: Final[int] = 0


class ConvergenceFailureError(RuntimeError):
    error_code = "ZA-SC-0008"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class ConvergenceChecker:
    def __init__(self) -> None:
        self._previous_bypass_count: int = 0
        self._previous_blocked_rate: float = 0.0
        self._rounds_since_improvement: int = 0
        self._round_history: list[ConvergenceResult] = []

    def check_convergence(self, phase: str) -> ConvergenceResult:
        result = ConvergenceResult(
            status="CONTINUE",
            bypass_count=self._previous_bypass_count,
            total_attacks=0,
            previous_bypass_count=self._previous_bypass_count,
            trend="stable",
            rounds_since_improvement=self._rounds_since_improvement,
        )
        self._round_history.append(result)
        return result

    def evaluate_round(self, report: RedBlueReport) -> ConvergenceResult:
        bypass_count = report.bypassed
        blocked_rate = report.blocked_rate
        total = report.total

        improved = False
        if (bypass_count < self._previous_bypass_count and self._previous_bypass_count > 0) or (
            blocked_rate > self._previous_blocked_rate and self._previous_blocked_rate > 0
        ):
            improved = True

        if improved:
            self._rounds_since_improvement = 0
            trend = "improving"
        else:
            self._rounds_since_improvement += 1
            trend = "stagnant"

        self._previous_bypass_count = bypass_count
        self._previous_blocked_rate = blocked_rate

        status = "CONTINUE"
        if blocked_rate >= BLOCKED_RATE_TARGET and bypass_count == 0:
            status = "CONVERGED"
        elif self._rounds_since_improvement >= MAX_ROUNDS_WITHOUT_IMPROVEMENT:
            status = "FAILED"
            logger.error(
                "convergence_failed rounds=%d bypasses=%d blocked_rate=%.2f",
                self._rounds_since_improvement,
                bypass_count,
                blocked_rate,
            )

        result = ConvergenceResult(
            status=status,
            bypass_count=bypass_count,
            total_attacks=total,
            previous_bypass_count=self._previous_bypass_count if not improved else self._previous_bypass_count,
            trend=trend,
            rounds_since_improvement=self._rounds_since_improvement,
        )
        self._round_history.append(result)

        if status == "FAILED":
            raise ConvergenceFailureError(
                f"Convergence check failed after {MAX_ROUNDS_WITHOUT_IMPROVEMENT} rounds without improvement. "
                f"Bypasses: {bypass_count}/{total}, Blocked rate: {blocked_rate:.1%}"
            )

        return result

    def reset(self) -> None:
        self._previous_bypass_count = 0
        self._previous_blocked_rate = 0.0
        self._rounds_since_improvement = 0
        self._round_history = []
        logger.info("convergence_reset")

    def round_history(self) -> list[ConvergenceResult]:
        return list(self._round_history)
