# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.trading_calendar
# [DOMAIN] D_DATA
# [DEPENDENCIES] exchange_calendars(pip)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] XSHG日历单例缓存; 纯本地计算不依赖网络/DB; exchange_calendars不可用时回退到weekday判断
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] is_trading_day永不抛异常，exchange_calendars不可用时回退到weekday>=5判断
# [TESTS] tests/zephyr/data/test_trading_calendar.py
# [A_module] module_id=MOD-L00-004-trading-calendar | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""A 股交易日历守卫（MOD-L00-004）。

基于 exchange_calendars 包的 XSHG（上海证券交易所）日历，
精确判断每个交易日（含节假日/调休），纯 Python 本地计算不依赖网络/DB。

用途：scheduler 在盘中/盘后时段触发前调用 is_trading_day()，
非交易日自动跳过，避免节假日空跑导致任务失败。

回退策略：exchange_calendars 未安装时降级为 weekday 判断（周一~周五），
保证 scheduler 不因依赖缺失而崩溃。
"""
from __future__ import annotations

import datetime
import logging
from functools import lru_cache

log = logging.getLogger(__name__)

# XSHG 日历单例（exchange_calendars 加载较慢，缓存避免重复初始化）
_xshg_calendar = None
_xshg_load_failed = False


def _get_xshg_calendar():
    """懒加载 XSHG 日历单例。

    Returns:
        exchange_calendars ExchangeCalendar 实例，或 None（加载失败时）
    """
    global _xshg_calendar, _xshg_load_failed
    if _xshg_calendar is not None or _xshg_load_failed:
        return _xshg_calendar
    try:
        import exchange_calendars as xcals
        _xshg_calendar = xcals.get_calendar("XSHG")
        log.info("XSHG 交易日历已加载（exchange_calendars）")
    except Exception as e:
        _xshg_load_failed = True
        log.warning(
            "exchange_calendars 不可用，交易日历降级为 weekday 判断: %s", e
        )
    return _xshg_calendar


def is_trading_day(date: datetime.date | None = None) -> bool:
    """判断给定日期是否为 A 股交易日。

    使用 exchange_calendars 的 XSHG 日历精确判断（含节假日/调休）。
    exchange_calendars 不可用时回退到 weekday 判断（周一~周五）。

    Args:
        date: 待判断日期，None 表示今天

    Returns:
        True=交易日, False=非交易日（周末/节假日）
    """
    if date is None:
        date = datetime.date.today()

    cal = _get_xshg_calendar()
    if cal is not None:
        try:
            return bool(cal.is_session(date.isoformat()))
        except Exception as e:
            log.warning("XSHG is_session 查询失败，回退 weekday: %s", e)

    # 回退：周一~周五视为交易日（无法区分节假日）
    return date.weekday() < 5


# 需要交易日历守卫的调度时段（盘中/盘后/夜间/巡检）
# 事件驱动(event_driven)/周末校准(weekend_calibration)/月初静态(monthly_static)/周末补下载(weekend_backfill)不需要守卫
TRADING_DAY_GUARDED_SCHEDULES = frozenset({
    "intraday_realtime",    # L1 盘中实时层
    "intraday_minute",      # L2 盘中分钟K线层
    "daily_kline",          # L4 盘后日K线层
    "daily_capital",        # L5 盘后资金面层
    "daily_event",          # L6 盘后事件层
    "nightly_financial",    # L7 夜间财务层
    "integrity_check",      # L11 每日完整性巡检层
    "auction_highfreq",     # L0 集合竞价高频层
})
