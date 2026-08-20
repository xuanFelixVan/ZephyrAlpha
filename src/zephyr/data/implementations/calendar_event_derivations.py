# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.calendar_event_derivations
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.internal_compute_provider（_nth_weekday_of_month/_next_trading_day_on_or_after 纯函数真源复用，同包）
# [CONSUMERS] 待评估登记后由 internal_compute_provider._fetch_calendar_event 接线（17 号 §2.4 待评估项）；当前为函数级 MVP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯函数无副作用; 行格式 (event_date, event_type, description, "internal") 与既有派生函数一致; 范围过滤 [range_start, range_end]; earnings_deadline 遇非交易日取前一交易日（其余顺延）
# [MODIFY-GUARD] 17_special_trading_days_data_assets.md §2.4
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无（纯派生函数，输入为空→空列表）
# [TESTS] tests/zephyr/data/test_calendar_event_derivations.py
# [A_module] module_id=MOD-DATA-CALDERIV | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: by_month{(year,month): 月末交易日} + trading_days_set（A股交易日集合）+ range_start/range_end
# F1: derive_earnings_deadline（优先；每年 4/30、8/31、10/31，遇非交易日取前一交易日）
# F2: derive_mlf_operation（每月 15 日，遇周末顺延下一工作日——与 LPR 派生同口径）
# F3: derive_bond_futures_delivery（国债期货交割日：季月 3/6/9/12 第 2 个周五，非交易日顺延）
# F4: derive_a50_futures_delivery（富时 A50 交割日：每月倒数第 2 个工作日，SGX 口径 Mon-Fri）
# O1: list[tuple(event_date, event_type, description, "internal")]（未去重未排序，由调用方 _dedupe_and_sort_events 收口）
# [/ALGO_FLOW]
"""日历事件派生函数（17 号 §2.4 待评估项，函数级 MVP）。

四个待评估 event_type 的派生实现（行格式与 ``internal_compute_provider`` 既有派生
函数一致，可直接被 ``_fetch_calendar_event`` 接线消费）：

  - ``earnings_deadline``（**优先**，与事件驱动 sleeve G10 联动价值高）：
    财报强制披露截止窗口（季报/年报 4/30、8/31、10/31），遇非交易日取**前一**交易日；
  - ``mlf_operation``：MLF 操作日（每月 15 日，遇周末顺延下一工作日），
    与已覆盖的 lpr_announcement（每月 20 日）互补（MLF→LPR 传导链）；
  - ``bond_futures_delivery``：国债期货交割日（交割月=季月 3/6/9/12 第 2 个周五，
    T/TF/TS，与股指期货第 3 个周五**不同日**），非交易日顺延下一交易日；
  - ``a50_futures_delivery``：富时 A50 期货交割日（每月倒数第 2 个工作日，新交所；
    与 hk_connect_closed 协同刻画北向资金节奏）。

接线纪律：四 event_type 在 17 号 §2.4 均为「登记待评估」——本模块仅交付派生函数 +
测试，**不改动** ``internal_compute_provider._fetch_calendar_event``（接线待评估裁定）。

依据: 17_special_trading_days_data_assets §2.4
Version: 0.1.0
"""

from __future__ import annotations

import datetime
from typing import Final

from zephyr.data.implementations.internal_compute_provider import (
    _next_trading_day_on_or_after,
    _nth_weekday_of_month,
)

__all__: Final = [
    "EARNINGS_DEADLINE_DATES",
    "TREASURY_DELIVERY_MONTHS",
    "derive_a50_futures_delivery",
    "derive_bond_futures_delivery",
    "derive_earnings_deadline",
    "derive_mlf_operation",
]

#: 财报强制披露截止日（月/日，17 号 §2.4：4/30 年报+一季报、8/31 半年报、10/31 三季报）
EARNINGS_DEADLINE_DATES: Final[tuple[tuple[int, int], ...]] = ((4, 30), (8, 31), (10, 31))
#: 国债期货交割月（T/TF/TS 合约月份=季月）
TREASURY_DELIVERY_MONTHS: Final[frozenset[int]] = frozenset({3, 6, 9, 12})
_LOOKBACK_DAYS: Final[int] = 10  # 前向/后向查找上限（覆盖春节/国庆长假）


def _prev_trading_day_on_or_before(
    d: datetime.date,
    trading_days_set: set[datetime.date],
) -> datetime.date | None:
    """d 当日或之前的第一个交易日（d 非交易日时前移，最多查找 10 天）。"""
    for i in range(_LOOKBACK_DAYS):
        cand = d - datetime.timedelta(days=i)
        if cand in trading_days_set:
            return cand
    return None


def _weekday_on_or_after(year: int, month: int, day: int) -> datetime.date:
    """某年某月某日，遇周末顺延下一工作日（与 LPR 派生同口径，工作日=周一~周五）。"""
    d = datetime.date(year, month, day)
    while d.weekday() >= 5:
        d += datetime.timedelta(days=1)
    return d


def _last_business_day_of_month(year: int, month: int, n: int) -> datetime.date | None:
    """每月倒数第 n 个工作日（Mon-Fri，SGX 口径；n=1=月末最后一个工作日）。"""
    if month == 12:
        d = datetime.date(year, 12, 31)
    else:
        d = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    count = 0
    while d.month == month:  # 不出当月（每月工作日 >= 20，n=2 必达）
        if d.weekday() < 5:
            count += 1
            if count == n:
                return d
        d -= datetime.timedelta(days=1)
    return None


def derive_earnings_deadline(
    by_month: dict[tuple[int, int], datetime.date],
    trading_days_set: set[datetime.date],
    range_start: datetime.date,
    range_end: datetime.date,
) -> list[tuple]:
    """财报强制披露截止窗口（每年 4/30、8/31、10/31，遇非交易日取前一交易日）。"""
    rows: list[tuple] = []
    years = sorted({y for y, _ in by_month.keys()})
    for year in years:
        for month, day in EARNINGS_DEADLINE_DATES:
            deadline = _prev_trading_day_on_or_before(
                datetime.date(year, month, day),
                trading_days_set,
            )
            if deadline and range_start <= deadline <= range_end:
                rows.append(
                    (
                        deadline,
                        "earnings_deadline",
                        f"{year}-{month:02d}-{day:02d} 财报披露截止窗口（遇非交易日前移）",
                        "internal",
                    )
                )
    return rows


def derive_mlf_operation(
    by_month: dict[tuple[int, int], datetime.date],
    range_start: datetime.date,
    range_end: datetime.date,
) -> list[tuple]:
    """MLF 操作日（每月 15 日，遇周末顺延下一工作日——与 LPR 派生同口径）。"""
    rows: list[tuple] = []
    for year, month in by_month.keys():
        mlf_day = _weekday_on_or_after(year, month, 15)
        if range_start <= mlf_day <= range_end:
            rows.append((mlf_day, "mlf_operation", f"{year}-{month:02d} MLF操作日（每月15日顺延）", "internal"))
    return rows


def derive_bond_futures_delivery(
    by_month: dict[tuple[int, int], datetime.date],
    trading_days_set: set[datetime.date],
    range_start: datetime.date,
    range_end: datetime.date,
) -> list[tuple]:
    """国债期货交割日（季月 3/6/9/12 第 2 个周五，非交易日顺延下一交易日）。"""
    rows: list[tuple] = []
    for year, month in by_month.keys():
        if month not in TREASURY_DELIVERY_MONTHS:
            continue
        second_friday = _nth_weekday_of_month(year, month, 4, 2)  # 周五=4, 第2个
        if second_friday is None:
            continue
        delivery_day = _next_trading_day_on_or_after(second_friday, trading_days_set)
        if delivery_day and range_start <= delivery_day <= range_end:
            rows.append(
                (
                    delivery_day,
                    "bond_futures_delivery",
                    f"{year}-{month:02d} 国债期货交割日（季月第2个周五）",
                    "internal",
                )
            )
    return rows


def derive_a50_futures_delivery(
    by_month: dict[tuple[int, int], datetime.date],
    range_start: datetime.date,
    range_end: datetime.date,
) -> list[tuple]:
    """富时 A50 期货交割日（每月倒数第 2 个工作日，SGX 口径 Mon-Fri）。"""
    rows: list[tuple] = []
    for year, month in by_month.keys():
        delivery_day = _last_business_day_of_month(year, month, 2)
        if delivery_day and range_start <= delivery_day <= range_end:
            rows.append(
                (
                    delivery_day,
                    "a50_futures_delivery",
                    f"{year}-{month:02d} 富时A50期货交割日（月末倒数第2个工作日）",
                    "internal",
                )
            )
    return rows
