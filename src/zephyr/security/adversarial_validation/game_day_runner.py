# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.1 + §8.3 + §16 Phase 2b
# [MODULE] zephyr.security.adversarial_validation.game_day_runner
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.validator; zephyr.security.adversarial_validation.models; zephyr.security.adversarial_validation.blast_radius; zephyr.security.adversarial_validation.convergence_checker
# [CONSUMERS] game_day_scheduler.py; cli.py; CI/CD workflow
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 4 frequency levels: PER_COMMIT(FILE) / DAILY(MODULE) / WEEKLY(CROSS_MODULE) / MONTHLY(SYSTEM); each run produces GameDayResult with report
# [MODIFY-GUARD] Adding frequency MUST add entry to GameDayFrequency enum and run_game_day() dispatch; report format per GameDayResult model
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GameDayError on validation failure within game day session
# [TESTS] tests/red_blue/test_game_day_runner.py
# [A_module] module_id=MOD-INF-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: game_day_runner.py
# 层: 算法
# - id: A1
#   name_zh: ① GameDayRunner
#   name_en: GameDayRunner
#   intro: class GameDayRunner 源码 L104-L158
#   desc: 公共方法（定义序）: run_game_day, run_full_cycle；源码 L104-L158
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: GameDayRunner
#   downstream: game_day_scheduler.py; cli.py; CI/CD workflow
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from enum import Enum

from zephyr.security.adversarial_validation.blast_radius import AbortThresholdError
from zephyr.security.adversarial_validation.models import (
    AttackTier,
    BlastRadiusLevel,
    GameDayResult,
    RedBlueReport,
)
from zephyr.security.adversarial_validation.validator import RedBlueValidator

logger = logging.getLogger(__name__)

__all__: list[str] = ["GameDayError", "GameDayFrequency", "GameDayRunner"]


class GameDayFrequency(str, Enum):
    PER_COMMIT = "per_commit"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

    @property
    def tier(self) -> AttackTier:
        mapping: dict[str, AttackTier] = {
            "per_commit": AttackTier.TIER_1,
            "daily": AttackTier.TIER_2,
            "weekly": AttackTier.TIER_3,
            "monthly": AttackTier.TIER_6,
        }
        return mapping.get(self.value, AttackTier.TIER_1)

    @property
    def blast_radius(self) -> BlastRadiusLevel:
        mapping: dict[str, BlastRadiusLevel] = {
            "per_commit": BlastRadiusLevel.FILE,
            "daily": BlastRadiusLevel.MODULE,
            "weekly": BlastRadiusLevel.CROSS_MODULE,
            "monthly": BlastRadiusLevel.SYSTEM,
        }
        return mapping.get(self.value, BlastRadiusLevel.FILE)


class GameDayError(RuntimeError):
    error_code = "ZA-SC-0006"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class GameDayRunner:
    def __init__(self) -> None:
        self._validator = RedBlueValidator()

    def run_game_day(self, frequency: GameDayFrequency) -> GameDayResult:
        tier = frequency.tier
        radius = frequency.blast_radius

        try:
            report: RedBlueReport = self._validator.run_adversarial_session(
                session_name=f"gameday-{frequency.value}",
                tier=tier,
                blast_radius=radius,
            )
        except AbortThresholdError as e:
            report = RedBlueReport(
                session_id=f"gameday-{frequency.value}-aborted",
                circuit_breaker_open=True,
            )
            logger.warning("game_day_aborted frequency=%s reason=%s", frequency.value, str(e))
            return GameDayResult(
                total_attacks=0,
                bypasses=0,
                passed=0,
                report=report,
            )

        result = GameDayResult(
            total_attacks=report.total,
            bypasses=report.bypassed,
            passed=report.blocked,
            report=report,
        )

        logger.info(
            "game_day_complete frequency=%s attacks=%d blocked=%d bypassed=%d rate=%.1f%%",
            frequency.value,
            report.total,
            report.blocked,
            report.bypassed,
            report.blocked_rate * 100,
        )
        return result

    def run_full_cycle(self) -> dict[GameDayFrequency, GameDayResult]:
        results: dict[GameDayFrequency, GameDayResult] = {}
        order = [
            GameDayFrequency.PER_COMMIT,
            GameDayFrequency.DAILY,
            GameDayFrequency.WEEKLY,
            GameDayFrequency.MONTHLY,
        ]
        for freq in order:
            results[freq] = self.run_game_day(freq)
        return results
