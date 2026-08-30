# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.calendar.ashare
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.calendar.base; zephyr.data.trading_calendar; exchange_calendars(pip)
# [CONSUMERS] zephyr.data.scheduler; zephyr.data.multi_timeframe_fusion; zephyr.data.pit_query; 装配层 get_market_calendar("ashare")
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 全方法委托zephyr.data.trading_calendar真源=行为零变化; 无状态可共享单例; is_trading_day永不抛异常（继承真源契约）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §4.1
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 与真源一致（exchange_calendars不可用时回退weekday判断）; 未知周期kline_agg_rule→ValueError
# [TESTS] tests/zephyr/data/calendar/test_market_calendar.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
A股市场日历实现（94号 §4.1：A股实现=现有交易日历逻辑收编）。

收编方式=薄封装委托：is_trading_day / trading_days_in_range 全部委托
zephyr.data.trading_calendar 真源（XSHG 单例，含 weekday 降级链），真源本体
一行不动——这是"A股零行为变化"硬门槛的最稳路径。

session_windows 收编 ex_core/pre_execution_checker._ASHARE_SESSION_WINDOWS
语义（连续竞价两段 09:30-11:30 / 13:00-15:00，复制语义不改 ex_core 文件——
ex_core 为避让施工面，其注入式改造登记后续波次）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ashare.py
# 层: 算法
# - id: A1
#   name_zh: ① ASHareCalendar
#   name_en: ASHareCalendar
#   intro: A股断点日历（交易日历+午休+隔夜+节假日）。
#   desc: A股断点日历（交易日历+午休+隔夜+节假日）。 无状态（全部委托真源模块级函数），可安全共享单例。；公共方法（定义序）: is_trading_day, trading_days_in_range, session_w…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ASHareCalendar
#   downstream: zephyr.data.scheduler; zephyr.data.multi_timeframe_fusion; zephyr.data.pit_quer…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
from typing import Final

from zephyr.data import trading_calendar as _tc
from zephyr.data.calendar.base import KlineAggRule, MarketCalendar

__all__: Final = ["ASHareCalendar"]


class ASHareCalendar(MarketCalendar):
    """A股断点日历（交易日历+午休+隔夜+节假日）。

    无状态（全部委托真源模块级函数），可安全共享单例。
    """

    market: str = "ashare"
    timezone: str = "Asia/Shanghai"

    #: 连续竞价时段（开, 闭），收编 _ASHARE_SESSION_WINDOWS 语义
    _SESSION_WINDOWS: Final = (
        (datetime.time(9, 30), datetime.time(11, 30)),
        (datetime.time(13, 0), datetime.time(15, 0)),
    )

    def is_trading_day(self, day: datetime.date | None = None) -> bool:
        """委托真源 is_trading_day（XSHG 精确历，降级 weekday）。"""
        return _tc.is_trading_day(day)

    def trading_days_in_range(
        self,
        start: datetime.date,
        end: datetime.date,
    ) -> list[datetime.date]:
        """委托真源 trading_days_in_range（与 c1_market.trade_calendar 表同源语义）。"""
        return _tc.trading_days_in_range(start, end)

    def session_windows(self, day: datetime.date) -> tuple[tuple[datetime.time, datetime.time], ...]:
        """恒定返回连续竞价两段（时段语义不随交易日变化，调用方先判 is_trading_day）。"""
        return self._SESSION_WINDOWS

    def kline_agg_rule(self, target_freq: str) -> KlineAggRule:
        """A股聚合规则：120min=2×60min 相邻配对（09:30 锚点致原生 floor 错切）；其余 native。"""
        if target_freq == "120min":
            return KlineAggRule(mode="pair", source_freq="60min", pair_count=2)
        if target_freq in ("1min", "5min", "15min", "30min", "60min", "1d"):
            return KlineAggRule(mode="native")
        raise ValueError(f"未知目标周期: {target_freq!r}（A股合法: 1/5/15/30/60/120min, 1d）")
