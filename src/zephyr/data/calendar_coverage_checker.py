# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.calendar_coverage_checker
# [DOMAIN] D_DATA
# [DEPENDENCIES] std(datetime/logging/dataclasses); zephyr.data.calendar(懒加载); zephyr.data.ch_reader; zephyr.data.alerter(懒加载)
# [CONSUMERS] zephyr.data.scheduler(schedule.yaml calendar_coverage_check 任务槽); 治理报告/人工诊断 CLI
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只读零写入; 事件触发（任务槽/显式调用），禁自建 cron/Timer/sleep-loop 常驻（宪法 §9.3）;
#   判据=交易日历逐日 × 表内日期集合差集（补 max-date 原理性失明：tick 09-17 内部洞/stock_basic 09-16 缺日型盲区）;
#   日历不可用=降级按 weekday 期望并标 degraded（宁报不漏，禁静默绿）; 单表查询失败记 error 计入报告不阻断其余表;
#   检查窗默认止于昨日（盘前运行当日必缺，禁假红）; 期望日须 >= spec.since（通道重建前史不期望，防假红）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_coverage_checker 永不抛（异常降级 ERROR 告警返回 ok=False）;
#   check_table_coverage 对空表返回 missing=全部期望日; runner 异常/空返回→CoverageRow(error=...)
# [TESTS] tests/zephyr/data/test_calendar_coverage_checker.py
# [A_module] module_id=MOD-L00-004-CCC | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""交易日历逐日覆盖检查器（trade_calendar × 表内日期集合差集）。

治什么病：
  停更哨兵（data_supply_sentinel）判「max(date) 新不新」，max-date 有原理性失明——
  表内**内部**缺日（中间洞）对 max 完全不可见：tick 09-17 全缺但 09-16 满、
  stock_basic 09-16 整日缺、daily_valuation 09-16=2,165 行部分写入，三例 max 都绿。
  本模块把「检查窗内每个期望交易日」与「表内实有日期集合」做差集，产出缺日清单
  （missing_days）与多余日清单（extra_days=非交易日落行，如 sector_fund_flow 09-19
  周六写 450 行型污染）。

挂载方式（签字⑨ 已批挂任务表）：
  schedule.yaml calendar_coverage_check 槽（每日 07:10，哨兵 06:50 之后）→
  zephyr.data.scheduler 按 schedule_name 分支调用 run_coverage_checker()。
  随调度器任务槽事件触发，**不自建常驻进程**（禁 cron/Timer/sleep-loop，宪法 §9.3）。

期望日集合（cadence）：
  trading  — 交易日历逐日（A股日频族默认）
  calendar — 自然日逐日（7×24/周末照跑族，如 news_sentiment_window 夜间情绪）

since 通道起点：
  重建/换道后的表（index_quote EOD 快照 09-15 起）此前日期不期望，防把「重建前史」
  报成缺口（零误报红线）。默认名单每格带实测依据，见 DEFAULT_WATCH 注释。

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/data/calendar_coverage_checker.yaml
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Callable, Final

from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

QueryRunner = Callable[[str], str]

#: 默认回看窗（交易日数）：覆盖两周级缺口即够，缺日越久越该由周审收口
_DEFAULT_WINDOW_DAYS: Final = 10

_SQL_DISTINCT_DATES: Final = (
    "SELECT DISTINCT {date_col} FROM {table} "  # noqa: bare-sql  只读 DISTINCT 日期诊断查询，模块级模板常量（表名/列名运行时参数化），非业务写路径，无集中化 SQL 文件可归并
    "WHERE {date_col} >= '{start}' AND {date_col} <= '{end}' ORDER BY {date_col}"
)


@dataclass(frozen=True)
class WatchSpec:
    """单表检查规格：表、日期列、期望日节奏、通道起点。"""

    table: str
    date_col: str
    cadence: str = "trading"  # trading | calendar
    since: str | None = None  # 'YYYY-MM-DD' 期望日下界（通道重建/换道日）


@dataclass
class CoverageRow:
    """单表覆盖检查结果（ok=无缺日无多余日且查询未出错）。"""

    table: str
    date_col: str
    cadence: str
    start: str
    end: str
    expected_days: int = 0
    missing_days: list[str] = field(default_factory=list)
    extra_days: list[str] = field(default_factory=list)
    error: str | None = None
    degraded: bool = False  # True=日历不可用降级 weekday 口径

    @property
    def ok(self) -> bool:
        return self.error is None and not self.missing_days and not self.extra_days


# ---------------------------------------------------------------------------
# 默认观察名单（2026-09-21 WO-3 实测定档）：
#   since=2026-09-17 — stock_basic：09-16 整日缺为快照型**永久洞**（已入 gaps 册
#     stock_basic_snapshot_days_missing verification_20260921），since 推进到洞后=
#     前向监控新洞，禁对已登记永久洞每日重鸣（BRK-046 告警疲劳红线）
#   since=2026-09-15 — index_quote EOD 快照通道重建（此前为巡检式零星快照旧形态，
#     且 09-07~09-11 前史日期属旧形态遗留，双向不期望）
#   since=2026-09-19 — auction_snapshot：09-18 过渡日洞+9 月上旬缺采日（A3 家族永久
#     缺口，已入 gaps 册 auction_20260918_transition_gap）之后=桥流时代前向监控
#   since=2026-09-13 — news_sentiment 夜间接线自愈稳定（09-12 单缺属接线初期）
#   其余表 since=2026-09-05（两周窗自然覆盖，无重建事件）
# news_sentiment_window **不入**默认名单：未注册 TableRegistry 品类（TABLE-NAME-REGISTRY
# 门禁禁硬编码表名；补注册属扩面），其断供/低产已由 data_supply_sentinel 同批 4 行中的
# 日历日 lag3+floor3 腿覆盖；注册品类后可经 specs 参数点名。
# tick_data / tick_depth_5 **不入**默认名单：亿级行 DISTINCT 日期属重 IO，其停更/地板
# 已由 data_supply_sentinel 新鲜度+行数腿覆盖（WO-3 同批 4 行）；临时诊断可用 specs 参数点名。
# ---------------------------------------------------------------------------
_TBL_KLINE_DAILY: Final[str] = get_registry().table("market_kline_daily")
_TBL_DAILY_VALUATION: Final[str] = get_registry().table("market_daily_valuation")
_TBL_STOCK_BASIC: Final[str] = get_registry().table("meta_stock_basic")
_TBL_STOCK_INDICATOR: Final[str] = get_registry().table("market_stock_indicator")
_TBL_AUCTION_SNAPSHOT: Final[str] = get_registry().table("market_auction_snapshot")
_TBL_INDEX_QUOTE: Final[str] = get_registry().table("market_index_quote")
_TBL_MONEY_FLOW: Final[str] = get_registry().table("market_money_flow")

DEFAULT_WATCH: Final[tuple[WatchSpec, ...]] = (
    WatchSpec(_TBL_KLINE_DAILY, "trade_date", since="2026-09-05"),
    WatchSpec(_TBL_DAILY_VALUATION, "trade_date", since="2026-09-05"),
    WatchSpec(_TBL_STOCK_BASIC, "trade_date", since="2026-09-17"),
    WatchSpec(_TBL_STOCK_INDICATOR, "trade_date", since="2026-09-05"),
    WatchSpec(_TBL_AUCTION_SNAPSHOT, "trade_date", since="2026-09-19"),
    WatchSpec(_TBL_INDEX_QUOTE, "trade_date", since="2026-09-15"),
    WatchSpec(_TBL_MONEY_FLOW, "trade_date", since="2026-09-05"),
)


def _default_runner() -> QueryRunner:
    from zephyr.data import ch_reader

    return ch_reader.query


def _trading_days(start: date, end: date) -> tuple[list[date], bool]:
    """交易日序列；日历不可用降级 weekday 口径（更严方向宁报不漏，degraded=True 留痕）。"""
    try:
        from zephyr.data.calendar import get_market_calendar

        cal = get_market_calendar("ashare")
        return cal.trading_days_in_range(start, end), False
    except Exception as exc:  # noqa: BLE001 — 降级取更严口径并在报告留痕
        log.warning("交易日历不可用，降级 weekday 口径: %s", exc)
        days: list[date] = []
        cur = start
        while cur <= end:
            if cur.weekday() < 5:
                days.append(cur)
            cur += timedelta(days=1)
        return days, True


def _calendar_days(start: date, end: date) -> list[date]:
    """自然日序列（calendar 节奏期望日）。"""
    days: list[date] = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += timedelta(days=1)
    return days


def _compute_expected(
    spec: WatchSpec, start: date, end: date, trading_days: list[date] | None
) -> tuple[list[date], bool]:
    """期望日集合：calendar=自然日；trading=交易日（None 时现算并报降级）。"""
    if spec.cadence == "calendar":
        return _calendar_days(start, end), False
    if trading_days is not None:
        return list(trading_days), False
    return _trading_days(start, end)


def _fetch_dates(spec: WatchSpec, start: date, end: date, runner: QueryRunner) -> set[str]:
    """表内实有日期集合；空返回按宁报不漏抛错（由调用方记 error）。"""
    sql = _SQL_DISTINCT_DATES.format(date_col=spec.date_col, table=spec.table, start=start, end=end)
    raw = runner(sql)
    if raw is None or raw == "":
        raise ValueError("runner 空返回（查询失败或真零日期，按宁报不漏计 error）")
    return {line.strip() for line in str(raw).splitlines() if line.strip()}


def _finalize_row(
    row: CoverageRow,
    spec: WatchSpec,
    expected: list[date],
    actual: set[str],
    since: date | None,
    start: date,
    end: date,
) -> None:
    """双向差集落账：since 双向不期望（missing/extra 都不记前史）。"""
    if since is not None:
        expected = [d for d in expected if d >= since]
    row.expected_days = len(expected)
    expected_iso = {d.isoformat() for d in expected}
    actual = {d for d in actual if start.isoformat() <= d <= end.isoformat()}
    if since is not None:
        actual = {d for d in actual if d >= spec.since}
    row.missing_days = sorted(expected_iso - actual)
    if spec.cadence == "trading":
        row.extra_days = sorted(d for d in actual if d not in expected_iso)


def check_table_coverage(
    spec: WatchSpec,
    start: date,
    end: date,
    runner: QueryRunner | None = None,
    trading_days: list[date] | None = None,
    calendar_degraded: bool = False,
) -> CoverageRow:
    """单表逐日差集：期望日集合（交易日/自然日 ∩ [start,end] ∩ >=since）vs 表内实有日期。

    trading_days 注入用于测试与多表共享同一份日历计算；runner 注入同理（tests 只用假
    runner，禁触生产库）。
    """
    row = CoverageRow(
        table=spec.table,
        date_col=spec.date_col,
        cadence=spec.cadence,
        start=start.isoformat(),
        end=end.isoformat(),
        degraded=calendar_degraded,
    )
    runner = runner or _default_runner()
    expected, degraded = _compute_expected(spec, start, end, trading_days)
    row.degraded = row.degraded or degraded
    since = date.fromisoformat(spec.since) if spec.since else None
    try:
        actual = _fetch_dates(spec, start, end, runner)
    except Exception as exc:  # noqa: BLE001 — 单表失败记 error 不阻断其余表
        row.error = f"query error: {str(exc)[:160]}"
        return row
    _finalize_row(row, spec, expected, actual, since, start, end)
    return row


def _check_all_specs(
    specs: tuple[WatchSpec, ...],
    start: date,
    end: date,
    window: list[date],
    degraded: bool,
    runner: QueryRunner | None,
) -> list[CoverageRow]:
    """逐表检查（calendar 节奏表不注入交易日窗，自带自然日期望）。"""
    return [
        check_table_coverage(
            spec,
            start,
            end,
            runner=runner,
            trading_days=None if spec.cadence == "calendar" else list(window),
            calendar_degraded=degraded,
        )
        for spec in specs
    ]


def _notify_breaches(bad: list[CoverageRow], alerter: object | None) -> None:
    """破防表逐表 WARN 告警（告警失败只 warning，不影响检查结论）。"""
    for r in bad:
        msg = (
            f"日历覆盖缺口 {r.table}: missing={r.missing_days} extra={r.extra_days}"
            + (f" error={r.error}" if r.error else "")
            + (" [degraded weekday 口径]" if r.degraded else "")
        )
        log.warning("%s", msg)
        if alerter is None:
            continue
        try:
            alerter.notify(r.table, msg, level="WARN", source="calendar_coverage_checker")
        except Exception as exc:  # noqa: BLE001 — 告警失败不影响检查结论
            log.warning("覆盖检查告警失败: %s", exc)


def _build_report(rows: list[CoverageRow], bad: list[CoverageRow], start: date, end: date, degraded: bool) -> dict:
    """聚合报告 dict（rows 明细按 CoverageRow 字段平铺）。"""
    report = {
        "ok": not bad,
        "checked": len(rows),
        "breached": len(bad),
        "window_start": start.isoformat(),
        "window_end": end.isoformat(),
        "calendar_degraded": degraded,
        "rows": [
            {
                "table": r.table,
                "date_col": r.date_col,
                "cadence": r.cadence,
                "expected_days": r.expected_days,
                "missing_days": r.missing_days,
                "extra_days": r.extra_days,
                "error": r.error,
                "ok": r.ok,
                "degraded": r.degraded,
            }
            for r in rows
        ],
    }
    log.info(
        "日历覆盖检查完成: checked=%d breached=%d window=[%s..%s]",
        report["checked"],
        report["breached"],
        report["window_start"],
        report["window_end"],
    )
    return report


def _degraded_failure(exc: Exception, alerter: object | None) -> dict:
    """检查器故障降级：ERROR 告警 + ok=False（永不抛，不炸调度器）。"""
    log.exception("日历覆盖检查执行异常")
    if alerter is not None:
        try:
            alerter.notify(
                "calendar_coverage_checker",
                f"日历覆盖检查执行异常: {str(exc)[:200]}",
                level="ERROR",
                source="calendar_coverage_checker",
            )
        except Exception:  # noqa: BLE001
            pass
    return {"ok": False, "checked": 0, "breached": 0, "error": str(exc)[:200], "rows": []}


def run_coverage_checker(
    window_days: int = _DEFAULT_WINDOW_DAYS,
    end: date | None = None,
    specs: tuple[WatchSpec, ...] | None = None,
    runner: QueryRunner | None = None,
    alerter: object | None = None,
) -> dict:
    """默认观察名单逐表检查（任务槽入口；永不抛，异常降级告警）。

    end 默认=昨日：盘前运行当日必缺（竞价 09:15 才落、EOD 15:10 才落），禁假红。
    """
    try:
        specs = specs if specs is not None else DEFAULT_WATCH
        end = end or (date.today() - timedelta(days=1))
        # 取 end 前第 window_days 个交易日为窗起：自然日×2 上界内找足，再裁尾
        trading_days, degraded = _trading_days(end - timedelta(days=max(window_days * 3, 21)), end)
        window = trading_days[-window_days:] if len(trading_days) >= window_days else trading_days
        if not window:
            raise RuntimeError(f"交易日历在回看窗内为空（end={end}），拒绝盲跑")
        start = window[0]
        rows = _check_all_specs(specs, start, end, window, degraded, runner)
        bad = [r for r in rows if not r.ok]
        _notify_breaches(bad, alerter)
        return _build_report(rows, bad, start, end, degraded)
    except Exception as exc:  # noqa: BLE001 — 检查器故障降级，不炸调度器
        return _degraded_failure(exc, alerter)


__all__: Final = ["WatchSpec", "CoverageRow", "DEFAULT_WATCH", "check_table_coverage", "run_coverage_checker"]
