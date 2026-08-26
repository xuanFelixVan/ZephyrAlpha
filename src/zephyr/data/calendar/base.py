# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.calendar.base
# [DOMAIN] D_DATA
# [DEPENDENCIES] 标准库（abc/dataclasses/datetime）
# [CONSUMERS] zephyr.data.scheduler; zephyr.data.multi_timeframe_fusion; zephyr.data.pit_query
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 接口纯定义零IO; 实现方is_trading_day永不抛异常; session_windows当日无交易=空元组
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §4.1
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯接口无异常约定; KlineAggRule.freq单位分钟>0
# [TESTS] tests/zephyr/data/calendar/test_market_calendar.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""市场日历抽象接口（Market Calendar，CAND-CRYPTO-001 / 94号 §4.1）。

定义"什么时间有交易、K 线如何切分"的策略对象。双市场同内核的第一地基：
A股=断点日历（交易日历+午休+隔夜+节假日），数字货币=7×24 连续日历。

纪律（94号 §4.1 裁定）：
- 所有时间相关计算改为注入日历实例，不直接读 A股历；
- 禁止业务代码 if/else 判市场——市场差异只走"按市场注入实现"（策略模式）；
- 硬门槛：A股现有逻辑零行为变化（A股实现=trading_calendar 真源收编）。

同名区分：feedback_loop.collectors.market_calendar.MarketCalendar 为 FLE 假日
防误报采集器（holiday 集合 dataclass），与本接口语义不同，以包路径区分。
"""

from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Final, Literal

__all__: Final = ["KlineAggRule", "MarketCalendar"]


@dataclass(frozen=True)
class KlineAggRule:
    """K 线聚合切分规则（某目标周期在本市场的切桶方式）。

    Attributes:
        mode: "native"=连续原生切桶（pandas floor 锚定日界，7×24 市场天然正确）；
            "pair"=源频率相邻配对（断点市场时段不齐，如 A股 120min=2×60min 配对）。
        source_freq: pair 模式的源频率（如 "60min"）；native 模式为 None。
        pair_count: pair 模式每根目标 bar 的源 bar 根数（如 2）；native 模式为 None。
    """

    mode: Literal["native", "pair"]
    source_freq: str | None = None
    pair_count: int | None = None


# class-name-alias: 94号 §4.1 钦定接口名 market_calendar；feedback_loop.collectors.market_calendar.MarketCalendar 为 FLE 假日防误报采集器（holiday 集合 dataclass），同名不同义已评审（docs/_working/audit/architecture-reviews/2026-08-26-market-calendar-abstraction.md §1），以包路径区分
class MarketCalendar(ABC):
    """市场日历策略对象（抽象接口）。

    属性：
        market: 市场标签（"ashare"/"crypto"，治理闸市场标注用）。
        timezone: 日历日归属时区（A股="Asia/Shanghai"；币="UTC"，交易所 K 线惯例
            UTC 00:00 锚定日界）。
    """

    market: str = ""
    timezone: str = ""

    @abstractmethod
    def is_trading_day(self, day: datetime.date | None = None) -> bool:
        """判断给定日期（日历日时区口径）是否有交易。永不抛异常。"""

    @abstractmethod
    def trading_days_in_range(
        self,
        start: datetime.date,
        end: datetime.date,
    ) -> list[datetime.date]:
        """返回 [start, end] 闭区间内有交易的日历日列表（升序、去重）。"""

    @abstractmethod
    def session_windows(self, day: datetime.date) -> tuple[tuple[datetime.time, datetime.time], ...]:
        """返回给定日历日的连续交易时段对序列（开, 闭)。

        A股=((09:30,11:30),(13:00,15:00))（非交易日返回空元组由实现方决定，
        A股实现为恒定返回两段——时段语义不随交易日变化，调用方先判 is_trading_day）；
        币=((00:00, 24:00)) 全天连续（以 time.max 表示 24:00 端点）。
        """

    def is_open_at(self, moment: datetime.datetime) -> bool:
        """判断给定时刻是否处于连续交易时段内（默认实现：交易日+任一时段内）。

        7×24 市场实现可覆写为恒 True。
        """
        if not self.is_trading_day(moment.date()):
            return False
        now_t = moment.time()
        return any(start_t <= now_t <= end_t for start_t, end_t in self.session_windows(moment.date()))

    @abstractmethod
    def kline_agg_rule(self, target_freq: str) -> KlineAggRule:
        """返回目标周期在本市场的聚合切分规则。

        A股：120min→pair("60min", 2)（09:30 锚点导致原生 120min floor 错切）；
            其余周期→native。
        币：全部 native（7×24 连续，4h 锚定 UTC 00:00 天然正确）。
        未知周期由实现方抛 ValueError。
        """
