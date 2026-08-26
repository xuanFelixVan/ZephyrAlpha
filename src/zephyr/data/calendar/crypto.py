# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.calendar.crypto
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.calendar.base（纯本地计算，零网络/DB/pip 依赖）
# [CONSUMERS] 装配层 get_market_calendar("crypto"); 币版 K线聚合（4h 周期）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 7×24连续=is_trading_day恒True; 行为完全确定（无外部真源）; 纯本地计算
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §4.1
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] is_trading_day/is_open_at永不抛异常; 未知周期kline_agg_rule→ValueError
# [TESTS] tests/zephyr/data/calendar/test_market_calendar.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数字货币市场日历实现（94号 §4.1：币实现=7×24 连续日历）。

7×24 连续：无交易日历/午休/隔夜/节假日概念——每日皆交易日，全天单一时段。
日历日归属 UTC（交易所 K 线惯例 UTC 00:00 锚定日界，币安/OKX 一致）。

顺带支持 4h 周期（现有 A股 9 周期未含）：7×24 连续下 4h=240min 原生 floor
锚定 UTC 00:00 天然正确，无需配对聚合。
"""

from __future__ import annotations

import datetime
from typing import Final

from zephyr.data.calendar.base import KlineAggRule, MarketCalendar

__all__: Final = ["CryptoCalendar"]


class CryptoCalendar(MarketCalendar):
    """数字货币 7×24 连续日历。无状态、行为完全确定，可安全共享单例。"""

    market: str = "crypto"
    timezone: str = "UTC"

    #: 全天连续单一时段（00:00 含, 24:00 含——以 time.max 表示 24:00 端点）
    _SESSION_WINDOWS: Final = ((datetime.time(0, 0), datetime.time.max),)

    #: 合法目标周期（9 周期对齐 + 4h 币特有）
    _KNOWN_FREQS: Final = ("1min", "5min", "15min", "30min", "60min", "120min", "4h", "1d")

    def is_trading_day(self, day: datetime.date | None = None) -> bool:
        """7×24：每日皆交易日，恒 True。"""
        return True

    def trading_days_in_range(
        self,
        start: datetime.date,
        end: datetime.date,
    ) -> list[datetime.date]:
        """返回 [start, end] 闭区间全部自然日（升序）；end < start 返回空列表。"""
        if end < start:
            return []
        days = (end - start).days
        return [start + datetime.timedelta(days=i) for i in range(days + 1)]

    def session_windows(self, day: datetime.date) -> tuple[tuple[datetime.time, datetime.time], ...]:
        """全天连续单一时段。"""
        return self._SESSION_WINDOWS

    def is_open_at(self, moment: datetime.datetime) -> bool:
        """7×24：恒 True。"""
        return True

    def kline_agg_rule(self, target_freq: str) -> KlineAggRule:
        """币聚合规则：全部 native（连续市场，4h 锚定 UTC 00:00 天然正确）。"""
        if target_freq in self._KNOWN_FREQS:
            return KlineAggRule(mode="native")
        raise ValueError(f"未知目标周期: {target_freq!r}（币合法: {self._KNOWN_FREQS}）")
