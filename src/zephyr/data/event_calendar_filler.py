# [BLUEPRINT] MOD-DATA-068 | 待统筹登记（blueprint 未建，真源=candidate_module_registry CAND-DAT-021 行 + 2026-08-25-news-sentiment-upgrade-discussion.md §8 Q2-B）
# [MODULE] zephyr.data.event_calendar_filler
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.table_registry（表名真源）; zephyr.data.calendar（MarketCalendar 注入）; zephyr.data.implementations.calendar_event_derivations（顺延口径复用）; zephyr.data.ch_reader（消费方注入 query_fn）
# [CONSUMERS] 新闻可预测性打标（CAND-NLP-004 的正解：新闻流 join 日历判 scheduled/unscheduled）；盘前预案（未来 60 日可预见事件清单）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数+注入式数据读取（不直接连 CH）；幂等——同事件重复填充按 (event_date,event_type,symbol_scope) 去重；只登记填充时点已公告/规则可推导的事件（PIT 纪律）；单数据源读取失败跳过该源不阻断整体（fail-open）
# [MODIFY-GUARD] candidate_module_registry.yaml CAND-DAT-021；event_calendar_registry.yaml（REG-EVT-001 事件类型 taxonomy）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无自定义异常——行级解析失败跳过；query_fn 异常→该源空清单+log；未知参数边界（horizon_days<=0）→仅宏观规则源仍生成（range 为空则全空）
# [TESTS] tests/zephyr/data/test_event_calendar_filler.py
# [A_module] module_id=MOD-DATA-068 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""EventCalendarFiller — event_calendar 前瞻填充器（CAND-DAT-021，Q2-B 正解）。

背景
----
event_calendar_registry.yaml（REG-EVT-001）仅是事件**类型**注册表；本模块装配
"未来 N 日（默认 60）可预见事件"的**实例级**结构化日历，供两类消费：
- 新闻可预测性打标（新闻流与日历 join → scheduled/unscheduled，CAND-NLP-004
  MVP 字段的正解，日历上线后该字段退役）；
- 盘前预案（未来 60 日财报披露/解禁/宏观发布清单）。

数据源装配（三路）
-----------------
1. 财报披露计划：c3_fundamental.disclosure_plan（fund_disclosure_plan，已登记；
   akshare stock_report_disclosure 按报告期灌入）。actual_date 已定→confirmed；
   仅 scheduled_date 预约→scheduled。
2. 限售解禁：c3_fundamental.share_unlock（fund_share_unlock；akshare_provider
   有解禁接口 stock_restricted_release_detail_em 灌入，非降级）。交易所披露表
   口径→scheduled。
3. 宏观发布日历（固定日程规则，trading_calendar/calendar_event_derivations 同族
   先例）：LPR 每月 20 日顺延、MLF 每月 15 日顺延（规则推导 rule_derived）；
   官方 PMI 每月最后一日（统计局含周末照常发布）；CPI 每月 9-15 日窗口
   （取窗口首日 9 日顺延为锚，rule_window 估计——统计局日程年初公布但逐月漂移）。

PIT 纪律：只登记填充时点已公告（披露计划/解禁表）或规则可推导（宏观固定日程）
的事件；规则推导条目带 certainty 分级，下游按等级决定置信使用。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Final, Iterable, Sequence

from zephyr.data.calendar import MarketCalendar, get_market_calendar
from zephyr.data.implementations.calendar_event_derivations import _trading_day_on_or_after
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

# 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024，门禁：禁硬编码表名）
_TBL_DISCLOSURE_PLAN: Final[str] = get_registry().table("fund_disclosure_plan")
_TBL_SHARE_UNLOCK: Final[str] = get_registry().table("fund_share_unlock")

# ── 事件类型（对齐 event_calendar_registry REG-EVT-001 taxonomy）──
ET_EARNINGS_DISCLOSURE: Final[str] = "earnings_disclosure"  # EVT-EARN-001 财报披露计划
ET_SHARE_UNLOCK: Final[str] = "share_unlock"  # EVT-CA-002 限售解禁
ET_LPR: Final[str] = "lpr_announcement"  # EVT-MACRO-001 族：LPR 公布日
ET_MLF: Final[str] = "mlf_operation"  # EVT-MACRO-001 族：MLF 操作日
ET_PMI: Final[str] = "pmi_release"  # EVT-MACRO-001 族：官方 PMI 发布
ET_CPI: Final[str] = "cpi_release"  # EVT-MACRO-001 族：CPI 发布窗口

# ── 确定性等级 ──
CERT_CONFIRMED: Final[str] = "confirmed"  # 公告值已定（actual_date 披露日确定）
CERT_SCHEDULED: Final[str] = "scheduled"  # 官方预约/交易所披露表（可改期）
CERT_RULE_DERIVED: Final[str] = "rule_derived"  # 固定日程规则推导（LPR/MLF/PMI）
CERT_RULE_WINDOW: Final[str] = "rule_window"  # 窗口估计（CPI 9-15 日，锚首日顺延）

#: 宏观级事件的 symbol_scope 取值（非个股事件）
SCOPE_MARKET: Final[str] = "MARKET"
#: 宏观规则源标识（非表源）
SOURCE_MACRO_RULE: Final[str] = "macro_fixed_schedule_rule"

DEFAULT_HORIZON_DAYS: Final[int] = 60
_EPOCH_SENTINEL_YEAR: Final[int] = 1971  # 1970 纪元哨兵=日期缺失

# SQL 集中化（NO-BARE-SQL gate 豁免 _SQL_ 前缀；日期由 date.isoformat 注入，无注入面）
_SQL_DISCOVERY_WINDOW: Final[str] = (
    "SELECT symbol, report_period, scheduled_date, actual_date "
    "FROM {table} "
    "WHERE (toDate(scheduled_date) BETWEEN '{start}' AND '{end}') "
    "OR (toDate(actual_date) BETWEEN '{start}' AND '{end}')"
)
_SQL_UNLOCK_WINDOW: Final[str] = (
    "SELECT symbol, unlock_date, shares, ratio, amount "
    "FROM {table} "
    "WHERE unlock_date BETWEEN '{start}' AND '{end}'"
)


@dataclass(frozen=True, slots=True)
class EventCalendarEntry:
    """事件日历条目（CAND-DAT-021 输出契约）。

    Attributes
    ----------
    event_date : 事件日期（日历日）。
    event_type : 事件类型（对齐 REG-EVT-001 taxonomy，见模块常量 ET_*）。
    symbol_scope : 标的代码（如 600519）或 "MARKET"（宏观级）。
    certainty : 确定性等级（confirmed/scheduled/rule_derived/rule_window）。
    source : 来源标识（TableRegistry 派生全限定表名或 macro_fixed_schedule_rule）。
    description : 备注（报告期/解禁规模等）。
    """

    event_date: datetime.date
    event_type: str
    symbol_scope: str
    certainty: str
    source: str
    description: str = ""


def _parse_date(raw: object) -> datetime.date | None:
    """解析 CH TSV 日期/日期时间单元格；NULL（\\N）/纪元哨兵/非法 → None。"""
    text = str(raw or "").strip()
    if not text or text == r"\N":
        return None
    try:
        d = datetime.date.fromisoformat(text[:10])
    except ValueError:
        return None
    return None if d.year < _EPOCH_SENTINEL_YEAR else d


def _iter_year_months(start: datetime.date, end: datetime.date) -> Iterable[tuple[int, int]]:
    """[start, end] 覆盖的 (year, month) 序列（含两端月）。"""
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        yield year, month
        month += 1
        if month > 12:
            year, month = year + 1, 1


def _monthly_shifted_date(year: int, month: int, day: int, calendar: MarketCalendar) -> datetime.date:
    """某年某月某日遇非交易日顺延（复用 calendar_event_derivations 同族口径）。"""
    return _trading_day_on_or_after(year, month, day, calendar=calendar)


def macro_rule_events(
    start: datetime.date,
    end: datetime.date,
    *,
    calendar: MarketCalendar | None = None,
) -> list[EventCalendarEntry]:
    """宏观固定日程规则事件（LPR/MLF/PMI/CPI，trading_calendar 同族先例）。

    - LPR：每月 20 日，非交易日顺延（rule_derived）；
    - MLF：每月 15 日，非交易日顺延（rule_derived）；
    - PMI：每月最后一日（统计局含周末照常发布，不顺延，rule_derived）；
    - CPI：每月 9-15 日窗口，锚 9 日顺延（rule_window 估计，逐月以统计局公告为准）。
    """
    if end < start:
        return []
    cal = calendar or get_market_calendar("ashare")
    entries: list[EventCalendarEntry] = []
    for year, month in _iter_year_months(start, end):
        lpr_day = _monthly_shifted_date(year, month, 20, cal)
        if start <= lpr_day <= end:
            entries.append(
                EventCalendarEntry(lpr_day, ET_LPR, SCOPE_MARKET, CERT_RULE_DERIVED, SOURCE_MACRO_RULE,
                                   f"{year}-{month:02d} LPR 公布日（每月20日顺延）")
            )
        mlf_day = _monthly_shifted_date(year, month, 15, cal)
        if start <= mlf_day <= end:
            entries.append(
                EventCalendarEntry(mlf_day, ET_MLF, SCOPE_MARKET, CERT_RULE_DERIVED, SOURCE_MACRO_RULE,
                                   f"{year}-{month:02d} MLF 操作日（每月15日顺延）")
            )
        pmi_day = _last_day_of_month(year, month)
        if start <= pmi_day <= end:
            entries.append(
                EventCalendarEntry(pmi_day, ET_PMI, SCOPE_MARKET, CERT_RULE_DERIVED, SOURCE_MACRO_RULE,
                                   f"{year}-{month:02d} 官方 PMI 发布（月末日，含周末照常）")
            )
        cpi_day = _monthly_shifted_date(year, month, 9, cal)
        if start <= cpi_day <= end:
            entries.append(
                EventCalendarEntry(cpi_day, ET_CPI, SCOPE_MARKET, CERT_RULE_WINDOW, SOURCE_MACRO_RULE,
                                   f"{year}-{month:02d} CPI 发布窗口（9-15日，锚首日顺延估计）")
            )
    return entries


def _last_day_of_month(year: int, month: int) -> datetime.date:
    """月末日历日（PMI 发布日口径：统计局含周末照常发布，不做交易日顺延）。"""
    if month == 12:
        return datetime.date(year, 12, 31)
    return datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)


def entries_from_disclosure_rows(
    rows: Iterable[tuple],
    start: datetime.date,
    end: datetime.date,
) -> list[EventCalendarEntry]:
    """财报披露计划行 → 日历条目（行=(symbol, report_period, scheduled_date, actual_date)）。

    actual_date 落在窗口→confirmed；否则 scheduled_date 落窗→scheduled。
    两者均缺/超窗→跳过。PIT 纪律：仅登记已公告的预约/实际披露日。
    """
    entries: list[EventCalendarEntry] = []
    for row in rows:
        if len(row) < 4:
            continue
        symbol = str(row[0] or "").strip()
        if not symbol:
            continue
        report_period = str(row[1] or "").strip()
        actual = _parse_date(row[3])
        scheduled = _parse_date(row[2])
        if actual is not None and start <= actual <= end:
            entries.append(
                EventCalendarEntry(actual, ET_EARNINGS_DISCLOSURE, symbol, CERT_CONFIRMED,
                                   _TBL_DISCLOSURE_PLAN, f"报告期 {report_period} 实际披露日")
            )
        elif scheduled is not None and start <= scheduled <= end:
            entries.append(
                EventCalendarEntry(scheduled, ET_EARNINGS_DISCLOSURE, symbol, CERT_SCHEDULED,
                                   _TBL_DISCLOSURE_PLAN, f"报告期 {report_period} 预约披露日（可改期）")
            )
    return entries


def entries_from_unlock_rows(
    rows: Iterable[tuple],
    start: datetime.date,
    end: datetime.date,
) -> list[EventCalendarEntry]:
    """限售解禁行 → 日历条目（行=(symbol, unlock_date, shares, ratio, amount)）。

    交易所披露表口径→scheduled（数量/比例入 description 供下游量级评估）。
    """
    entries: list[EventCalendarEntry] = []
    for row in rows:
        if len(row) < 2:
            continue
        symbol = str(row[0] or "").strip()
        unlock = _parse_date(row[1])
        if not symbol or unlock is None or not (start <= unlock <= end):
            continue
        ratio = row[3] if len(row) > 3 else ""
        entries.append(
            EventCalendarEntry(unlock, ET_SHARE_UNLOCK, symbol, CERT_SCHEDULED,
                               _TBL_SHARE_UNLOCK, f"解禁占解禁前流通市值比例 {ratio}")
        )
    return entries


def load_disclosure_entries(
    query_fn: Callable[[str], str],
    start: datetime.date,
    end: datetime.date,
) -> list[EventCalendarEntry]:
    """从 disclosure_plan 表装配财报披露条目（注入式读取，fail-open）。"""
    sql = _SQL_DISCOVERY_WINDOW.format(table=_TBL_DISCLOSURE_PLAN, start=start.isoformat(), end=end.isoformat())
    try:
        tsv = query_fn(sql)
    except Exception as exc:  # noqa: BLE001 — 单源失败不阻断整体装配
        log.warning("disclosure_plan 读取失败，跳过该源: %s", exc)
        return []
    rows = [tuple(line.split("\t")) for line in (tsv or "").splitlines() if line.strip()]
    return entries_from_disclosure_rows(rows, start, end)


def load_unlock_entries(
    query_fn: Callable[[str], str],
    start: datetime.date,
    end: datetime.date,
) -> list[EventCalendarEntry]:
    """从 share_unlock 表装配解禁条目（注入式读取，fail-open）。"""
    sql = _SQL_UNLOCK_WINDOW.format(table=_TBL_SHARE_UNLOCK, start=start.isoformat(), end=end.isoformat())
    try:
        tsv = query_fn(sql)
    except Exception as exc:  # noqa: BLE001 — 单源失败不阻断整体装配
        log.warning("share_unlock 读取失败，跳过该源: %s", exc)
        return []
    rows = [tuple(line.split("\t")) for line in (tsv or "").splitlines() if line.strip()]
    return entries_from_unlock_rows(rows, start, end)


def dedupe_entries(entries: Iterable[EventCalendarEntry]) -> list[EventCalendarEntry]:
    """幂等去重：同 (event_date, event_type, symbol_scope) 重复填充只保留首条。"""
    seen: set[tuple[datetime.date, str, str]] = set()
    unique: list[EventCalendarEntry] = []
    for entry in entries:
        key = (entry.event_date, entry.event_type, entry.symbol_scope)
        if key in seen:
            continue
        seen.add(key)
        unique.append(entry)
    unique.sort(key=lambda e: (e.event_date, e.event_type, e.symbol_scope))
    return unique


def fill_event_calendar(
    as_of: datetime.date | None = None,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    *,
    query_fn: Callable[[str], str] | None = None,
    calendar: MarketCalendar | None = None,
    extra_entries: Iterable[EventCalendarEntry] = (),
) -> list[EventCalendarEntry]:
    """生成未来 N 日（默认 60）可预见事件日历（幂等）。

    Parameters
    ----------
    as_of : 填充基准日（None=今天）。PIT 锚点——只登记基准日时点上已公告/
        规则可推导的事件。
    horizon_days : 前瞻窗口天数（<=0 时窗口为空，返回空清单）。
    query_fn : CH 查询注入（TSV str）；None=跳过库内源（仅宏观规则事件，
        纯内存降级路径）。
    calendar : 市场日历注入（顺延判定；None=ASHareCalendar 默认单例）。
    extra_entries : 额外条目注入（手工事件/其他源装配结果）。

    Returns
    -------
    list[EventCalendarEntry] —— 按 (event_date, event_type, symbol_scope) 升序去重。
    """
    base = as_of or datetime.date.today()
    if horizon_days <= 0:
        return []
    end = base + datetime.timedelta(days=horizon_days)

    entries: list[EventCalendarEntry] = list(macro_rule_events(base, end, calendar=calendar))
    if query_fn is not None:
        entries.extend(load_disclosure_entries(query_fn, base, end))
        entries.extend(load_unlock_entries(query_fn, base, end))
    entries.extend(extra_entries)
    return dedupe_entries(entries)


__all__: Final = [
    "CERT_CONFIRMED",
    "CERT_RULE_DERIVED",
    "CERT_RULE_WINDOW",
    "CERT_SCHEDULED",
    "DEFAULT_HORIZON_DAYS",
    "ET_CPI",
    "ET_EARNINGS_DISCLOSURE",
    "ET_LPR",
    "ET_MLF",
    "ET_PMI",
    "ET_SHARE_UNLOCK",
    "SCOPE_MARKET",
    "SOURCE_MACRO_RULE",
    "EventCalendarEntry",
    "dedupe_entries",
    "entries_from_disclosure_rows",
    "entries_from_unlock_rows",
    "fill_event_calendar",
    "load_disclosure_entries",
    "load_unlock_entries",
    "macro_rule_events",
]
