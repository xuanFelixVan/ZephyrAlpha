# [BLUEPRINT] 35_drawdown_protocol_impl | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/35_drawdown_protocol_impl.md | §3.4/§6.1
# [MODULE] zephyr.risk.core.drawdown_forced_rest
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] RiskOrchestrator(§6.5 接线位); Kill Switch 复位链(§3.14 人工复位前置校验)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Level4触发后强制休息5个交易日(§2.5.2); 休息期=触发日之后5个交易日(触发日当日不计); 交易日由调用方注入有序日历(无隐藏节假日依赖); 计时器与人工复位正交(§3.7不可覆盖: 休息期满≠自动恢复,仍须人工复位); 未触发/rest_trading_days<1输入抛错
# [MODIFY-GUARD] tests/risk/test_drawdown_forced_rest.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidForcedRestInputError(ZA-RK-0065)
# [TESTS] tests/risk/test_drawdown_forced_rest.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: trigger(trade_date)记录Level4触发日 + clear()人工清除
# I2: ForcedRestConfig(rest_trading_days=5, §2.5.2 Level4) + 有序交易日历list[date](调用方注入)
# F1: is_resting(current_date,trading_days)→触发日后已完成休息交易日数<5即休息中
# F2: remaining_rest_days(current_date,trading_days)→max(0, 5-已完成休息交易日数)
# O1: bool休息中 / int剩余休息天数 (消费方: 复位链前置校验+盘前启动闸门)
# [/ALGO_FLOW]
"""D_RISK — Level 4 强制休息 5 天自动计时器（35 号 memo §6.1 施工，§3.4 落地）。

痛点（§3.4 恢复机制表"强制休息"行）：§2.5.2 要求 Level 4 触发后强制休息
5 个交易日，代码只有 requires_manual_reset（人工复位），无自动 5 天计时器——
人工复位过快会导致根因未修复即二次进场（§6.1 P0）。

本模块落地（配置级 + 计时函数）：
  - ForcedRestConfig：rest_trading_days=5（C 类可调参数，§2.5.2 真源）。
  - ForcedRestTimer：trigger(trade_date) 记录触发日；is_resting /
    remaining_rest_days 以调用方注入的有序交易日历计"触发日之后已过去的
    交易日数"，< 5 即休息中（触发日当日不计入休息）。
  - 与人工复位正交（§3.7 不可覆盖）：休息期满 ≠ 自动恢复——复位链
    （§3.14 request_manual_reset）前置校验"休息期未满拒绝复位"，
    休息期满仍须人工复位确认。本模块只计时，不解除任何锁定。

日历注入约定：trading_days 为有序交易日列表（含触发日与查询日可不在表中——
按"严格大于触发日且 ≤ 查询日的交易日数"计休息进度，日历缺日按列表实际计）。
SSoT: 35_drawdown_protocol_impl §3.4 + §6.1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Final, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidForcedRestInputError",
    "ForcedRestConfig",
    "ForcedRestTimer",
]

_logger = logging.getLogger(__name__)


class InvalidForcedRestInputError(ZephyrBaseError):
    """强制休息计时输入非法（配置越界/触发日在查询日之后/日历未排序）。"""

    error_code = "ZA-RK-0065"


@dataclass(frozen=True)
class ForcedRestConfig:
    """强制休息配置（C 类可调参数，默认值真源=§2.5.2 Level 4）。

    Attributes:
        rest_trading_days: 强制休息交易日数（默认 5）
    """

    rest_trading_days: int = 5

    def __post_init__(self) -> None:
        if self.rest_trading_days < 1:
            raise InvalidForcedRestInputError(
                f"rest_trading_days 须 >= 1, got {self.rest_trading_days}"
            )


class ForcedRestTimer:
    """Level 4 强制休息计时器。

    用法:
        timer = ForcedRestTimer()
        timer.trigger(trade_date=d0)                 # Level 4 触发
        timer.is_resting(d1, trading_days)           # True=休息中，复位链拒绝
        timer.remaining_rest_days(d1, trading_days)  # 剩余休息交易日数

    语义：休息期 = 触发日之后 rest_trading_days 个交易日（触发日当日不计）。
    与人工复位正交（§3.7）：休息期满不自动恢复，仅解除"复位前置拒绝"。
    """

    def __init__(self, config: ForcedRestConfig | None = None) -> None:
        self._config = config or ForcedRestConfig()
        self._trigger_date: date | None = None

    @property
    def trigger_date(self) -> date | None:
        """最近触发日（None=未触发）。"""
        return self._trigger_date

    @property
    def config(self) -> ForcedRestConfig:
        return self._config

    def trigger(self, trade_date: date) -> None:
        """记录 Level 4 触发日（重复触发刷新计时，对齐"取最严"原则）。"""
        if self._trigger_date is not None and self._trigger_date != trade_date:
            _logger.warning(
                "FORCED_REST_RETRIGGER %s -> %s（计时刷新）",
                self._trigger_date, trade_date,
            )
        self._trigger_date = trade_date
        _logger.warning("FORCED_REST_TRIGGERED date=%s rest_days=%d",
                        trade_date, self._config.rest_trading_days)

    def clear(self) -> None:
        """人工清除计时（人工复位完成/根因修复确认后调用，留痕）。"""
        if self._trigger_date is not None:
            _logger.info("FORCED_REST_CLEARED date=%s", self._trigger_date)
        self._trigger_date = None

    def _elapsed_rest_days(
        self, current_date: date, trading_days: Sequence[date]
    ) -> int:
        """触发日之后 ≤ current_date 的交易日数（触发日当日不计）。"""
        if self._trigger_date is None:
            raise InvalidForcedRestInputError("未触发（trigger_date 为空）")
        if current_date < self._trigger_date:
            raise InvalidForcedRestInputError(
                f"current_date {current_date} 早于触发日 {self._trigger_date}"
            )
        days = list(trading_days)
        if days != sorted(days):
            raise InvalidForcedRestInputError("trading_days 必须升序")
        return sum(1 for d in days if self._trigger_date < d <= current_date)

    def is_resting(self, current_date: date, trading_days: Sequence[date]) -> bool:
        """是否休息中。未触发=False（无休息约束）。"""
        if self._trigger_date is None:
            return False
        return self._elapsed_rest_days(current_date, trading_days) < (
            self._config.rest_trading_days
        )

    def remaining_rest_days(self, current_date: date, trading_days: Sequence[date]) -> int:
        """剩余休息交易日数。未触发=0。"""
        if self._trigger_date is None:
            return 0
        elapsed = self._elapsed_rest_days(current_date, trading_days)
        return max(0, self._config.rest_trading_days - elapsed)
