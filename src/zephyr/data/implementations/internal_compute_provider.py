# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.internal_compute_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.ch_reader; zephyr.factor.technical_indicators
# [CONSUMERS] zephyr.data.scheduler (source=internal 分支)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 内部计算 Provider——不从外部 API 拉数据，而是读 CH K线→本地计算指标→返回 FetchResult
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 失败→返回 FetchResult(error=...) 不抛；CH 读取失败→返回空结果+error
# [TESTS] tests/zephyr/data/test_internal_compute_provider.py
# [A_module] module_id=MOD-L00-004-INTERNAL | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa  M02豁免: 由 scheduler 按 daily_kline 时段调度, 非常驻服务
"""内部计算数据源 Provider（#ARCH-DATA-TI-001，Phase 2 多周期落地 2026-08-10）。

区别于外部数据源 Provider（miniqmt/akshare/tushare 等），本 Provider 不从外部 API 拉数据，
而是：
  1. 从 ClickHouse c1_market.kline_{period} 读取 OHLCV K线数据（9 周期）
  2. 调用 TechnicalIndicatorBase 子类计算 40 个技术指标（5 类全部施工完成）
  3. 返回 FetchResult（指标数据行），由上层 scheduler 写入 c1_market.technical_indicator

多周期支持（Phase 2，方案 A 已裁定）：
  - payload.extra["period"] 指定周期，默认 "daily"
  - period="all" 时遍历全部 9 周期（1min/5min/15min/30min/60min/120min/daily/weekly/monthly）
  - 120min 无原生 K 线表，从 kline_60min 两根聚合（09:30-11:30 / 13:00-15:00）
  - 输出行带 trade_date + trade_time + period 三列，与 technical_indicator 表 ORDER BY 对齐

接入调度器：scheduler.create_provider() 的 `source == "internal"` 分支返回本类实例。
tasks.yaml 中 source=internal 的任务（technical_indicator_incremental/full_refresh）使用本 Provider。
"""

from __future__ import annotations

import csv
import datetime
import io
import logging
import time
from pathlib import Path
from typing import Final, Iterator

import pandas as pd

from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)

log = logging.getLogger("integrator.internal")


# 周期 → (K线源表, 时间戳列, 是否日内) 映射
# 120min 无原生表，源表指向 kline_60min，由 _aggregate_120min 聚合
_PERIOD_MAP: dict[str, tuple[str, str, bool]] = {
    "1min": ("c1_market.kline_1min", "trade_time", True),
    "5min": ("c1_market.kline_5min", "trade_time", True),
    "15min": ("c1_market.kline_15min", "trade_time", True),
    "30min": ("c1_market.kline_30min", "trade_time", True),
    "60min": ("c1_market.kline_60min", "trade_time", True),
    "120min": ("c1_market.kline_60min", "trade_time", True),  # 聚合源
    "daily": ("c1_market.kline_daily", "trade_date", False),
    "weekly": ("c1_market.kline_weekly", "trade_date", False),
    "monthly": ("c1_market.kline_monthly", "trade_date", False),
}

# 全量回算时的周期遍历顺序（日/周/月先行，分钟随后）
ALL_PERIODS: list[str] = [
    "daily",
    "weekly",
    "monthly",
    "60min",
    "120min",
    "30min",
    "15min",
    "5min",
    "1min",
]

# 路由能力集（CAP-CONSISTENCY gate 模式1 识别）
# fetch 按 payload.table 路由，gate 仅识别 _*_CAPABILITIES 变量 / capability=="xxx" 模式，
# 故显式声明路由能力集对齐 meta.capabilities。technical_indicator 为默认分支
# （payload.table 非 calendar_event/hk_trade_calendar 时走指标计算）。
_INTERNAL_COMPUTE_CAPABILITIES = frozenset(
    {
        "technical_indicator",
        "calendar_event",
        "hk_trade_calendar",
    }
)

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀的常量定义行）
_SQL_GET_SYMBOLS = "SELECT DISTINCT symbol FROM {table} WHERE {where} ORDER BY symbol"

_SQL_READ_TRADING_DAYS = (
    "SELECT DISTINCT cal_date FROM c1_market.trade_calendar "
    "WHERE is_open = 1 "
    "AND cal_date >= '{start}' "
    "AND cal_date <= '{end}' "
    "ORDER BY cal_date"
)

_SQL_READ_HK_TRADING_DAYS = (
    "SELECT DISTINCT cal_date FROM c1_market.hk_trade_calendar "
    "WHERE is_open = 1 "
    "AND cal_date >= '{start}' "
    "AND cal_date <= '{end}' "
    "ORDER BY cal_date"
)

_SQL_READ_KLINE = "SELECT {select_cols} FROM {table} WHERE {where_clause} ORDER BY {order_by}"

# XHKG（港交所）日历单例——exchange_calendars 加载较慢，缓存避免重复初始化
# #ARCH-DATA-001: hk_trade_calendar 数据源从 akshare 迁移到 exchange_calendars XHKG
_xhkg_calendar = None
_xhkg_load_failed = False


def _get_xhkg_calendar():
    """懒加载 XHKG 日历单例（同 trading_calendar.py 的 XSHG 模式）。"""
    global _xhkg_calendar, _xhkg_load_failed
    if _xhkg_calendar is not None or _xhkg_load_failed:
        return _xhkg_calendar
    try:
        import exchange_calendars as xcals

        _xhkg_calendar = xcals.get_calendar("XHKG")
        log.info("XHKG 港股交易日历已加载（exchange_calendars）")
    except Exception as e:  # noqa: BLE001
        _xhkg_load_failed = True
        log.warning("exchange_calendars XHKG 不可用: %s", e)
    return _xhkg_calendar


# ============== 日历事件派生纯函数（原 InternalComputeProvider 静态/实例方法，
# 移至模块级以降低类方法数，满足 NO-GOD-CLASS gate ≤ 20 方法限制）==============


def _derive_month_ends(by_month: dict[tuple[int, int], datetime.date]) -> list[tuple]:
    """月末/季末/半年末/年末事件。"""
    rows: list[tuple] = []
    for (year, month), last_day in by_month.items():
        rows.append((last_day, "month_end", f"{year}-{month:02d} 月末（最后交易日）", "internal"))
        if month in (3, 6, 9, 12):
            rows.append((last_day, "quarter_end", f"{year}-Q{(month - 1) // 3 + 1} 季末（最后交易日）", "internal"))
        if month == 6:
            rows.append((last_day, "half_year_end", f"{year} 半年末（最后交易日）", "internal"))
        if month == 12:
            rows.append((last_day, "year_end", f"{year} 年末（最后交易日）", "internal"))
    return rows


def _derive_futures_and_index_option_expiry(
    by_month: dict[tuple[int, int], datetime.date],
    trading_days_set: set[datetime.date],
    range_start: datetime.date,
    range_end: datetime.date,
) -> list[tuple]:
    """股指期货交割日 + 股指期权到期日（每月第3个周五，非交易日顺延）。"""
    rows: list[tuple] = []
    for year, month in by_month.keys():
        third_friday = _nth_weekday_of_month(year, month, 4, 3)  # 周五=4, 第3个
        if third_friday is None:
            continue
        delivery_day = _next_trading_day_on_or_after(third_friday, trading_days_set)
        if delivery_day and range_start <= delivery_day <= range_end:
            rows.append((delivery_day, "futures_delivery", f"{year}-{month:02d} 股指期货交割日", "internal"))
            rows.append((delivery_day, "index_option_expiry", f"{year}-{month:02d} 股指期权到期日", "internal"))
    return rows


def _derive_etf_option_expiry(
    by_month: dict[tuple[int, int], datetime.date],
    trading_days_set: set[datetime.date],
    range_start: datetime.date,
    range_end: datetime.date,
) -> list[tuple]:
    """ETF期权到期日（每月第4个周三，非交易日顺延）。"""
    rows: list[tuple] = []
    for year, month in by_month.keys():
        fourth_wednesday = _nth_weekday_of_month(year, month, 2, 4)  # 周三=2, 第4个
        if fourth_wednesday is None:
            continue
        expiry_day = _next_trading_day_on_or_after(fourth_wednesday, trading_days_set)
        if expiry_day and range_start <= expiry_day <= range_end:
            rows.append((expiry_day, "etf_option_expiry", f"{year}-{month:02d} ETF期权到期日", "internal"))
    return rows


def _derive_lpr_announcement(
    by_month: dict[tuple[int, int], datetime.date],
    range_start: datetime.date,
    range_end: datetime.date,
) -> list[tuple]:
    """LPR公布日（每月20日，遇周末顺延下一工作日）。"""
    rows: list[tuple] = []
    for year, month in by_month.keys():
        lpr_day = _lpr_announcement_date(year, month)
        if range_start <= lpr_day <= range_end:
            rows.append((lpr_day, "lpr_announcement", f"{year}-{month:02d} LPR公布日", "internal"))
    return rows


def _dedupe_and_sort_events(rows: list[tuple]) -> list[tuple]:
    """按 (event_date, event_type) 去重并排序。"""
    seen: set[tuple] = set()
    unique_rows: list[tuple] = []
    for row in rows:
        key = (row[0], row[1])
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)
    unique_rows.sort(key=lambda r: (r[0], r[1]))
    return unique_rows


# ---- manual 手工录入日历事件（17号 §6.3 定稿：CSV 录入 + 一次性 IMPORT 标准填充路径）----
# 低频事件（FOMC 每年 8 次/两会每年 1 次/印花税调整）手工维护台账，可复查、可增量追加，
# 随 calendar_event_refresh 任务同批合并入库（同表同批一次回填）。
# 目录裁定：src/zephyr/ 契约仅许 .py/.yaml/.md（directory_contract.yaml DCR-005），
# CSV 台账放 data/manual/（data/ 兜底规则允许 .csv，git 跟踪，运行时数据区）。
_MANUAL_EVENT_CSV: Final = Path(__file__).resolve().parents[4] / "data" / "manual" / "calendar_event_manual.csv"

# manual event_type 白名单（与 schemas/categories/market_calendar_event.py DDL 注释 12 类对齐：
# 派生类 9 类由规则计算，manual 类仅此 3 类——白名单防台账误写派生类造成双源冲突）
_MANUAL_EVENT_TYPES: Final = frozenset({"fomc_meeting", "major_meeting", "stamp_duty_change"})


def _load_manual_calendar_events(
    range_start: datetime.date,
    range_end: datetime.date,
    csv_path: Path | None = None,
) -> list[tuple]:
    """读取 manual 日历事件台账 CSV，返回 (event_date, event_type, description, "manual") 行。

    行格式：event_date,event_type,description（# 开头为注释行；首行表头自动跳过；
    event_type 限 _MANUAL_EVENT_TYPES 白名单）。

    降级（fail-visible 不阻断派生类填充，与 17号 §2.5 降级哲学一致）：
      - 文件缺失/读取异常 → 告警并返回空列表；
      - 坏行（列数不足/日期非法/event_type 非白名单）→ 逐条跳过并计数告警。
    范围过滤：[range_start, range_end]，与派生类事件同口径（范围外存量不告警）。
    """
    path = csv_path if csv_path is not None else _MANUAL_EVENT_CSV
    if not path.exists():
        log.warning("manual 日历事件台账不存在，跳过 manual 事件合并: %s", path)
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        log.warning("manual 日历事件台账读取失败，跳过: %s", e)
        return []
    rows: list[tuple] = []
    skipped = 0
    for fields in csv.reader(io.StringIO(text)):
        if not fields or fields[0].strip().startswith("#"):
            continue  # 空行/注释行
        if fields[0].strip().lower() == "event_date":
            continue  # 表头
        if len(fields) < 3:
            skipped += 1
            continue
        try:
            d = datetime.date.fromisoformat(fields[0].strip())
        except ValueError:
            skipped += 1
            continue
        etype = fields[1].strip()
        if etype not in _MANUAL_EVENT_TYPES:
            skipped += 1
            continue
        if not (range_start <= d <= range_end):
            continue  # 范围外存量不计（台账允许超前/超旧追加，非坏行）
        desc = fields[2].strip() or f"{d.isoformat()} {etype}（manual 手工录入）"
        rows.append((d, etype, desc, "manual"))
    if skipped:
        log.warning("manual 日历事件台账跳过 %d 条坏行（列数/日期/event_type 非法）", skipped)
    log.info("manual 日历事件合并：%d 条（%s）", len(rows), path.name)
    return rows


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> datetime.date | None:
    """计算某年某月第 n 个星期 weekday 的日期。

    Args:
        year: 年
        month: 月
        weekday: 星期几（0=周一 ... 6=周日）
        n: 第几个（1-based）

    Returns:
        datetime.date，或 None（该月不足 n 个该星期）
    """
    first = datetime.date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    first_target = first + datetime.timedelta(days=offset)
    target = first_target + datetime.timedelta(weeks=n - 1)
    if target.month != month:
        return None
    return target


def _next_trading_day_on_or_after(d: datetime.date, trading_days_set: set) -> datetime.date | None:
    """返回 d 当日或之后的第一个交易日（d 非交易日时顺延）。

    最多向后查找 10 天（覆盖春节/国庆长假），超过返回 None。
    """
    for i in range(10):
        cand = d + datetime.timedelta(days=i)
        if cand in trading_days_set:
            return cand
    return None


def _lpr_announcement_date(year: int, month: int) -> datetime.date:
    """LPR公布日：每月20日，遇周末顺延到下一工作日（工作日=周一~周五）。"""
    d = datetime.date(year, month, 20)
    while d.weekday() >= 5:  # 周六(5)/周日(6)顺延
        d += datetime.timedelta(days=1)
    return d


class InternalComputeProvider(IngestProviderBase):
    """内部计算 Provider——读 CH K线→本地计算指标→返回 FetchResult。

    用法（由 scheduler 自动调用）：
        provider = InternalComputeProvider()
        provider.connect()
        for result in provider.fetch(payload, policy):
            # result.rows 是技术指标数据行
            # result.columns 是列名顺序（与 technical_indicator 表 INSERT_COLUMNS 对齐）
            ...
        provider.disconnect()

    多周期：payload.extra["period"] 指定周期（默认 daily），"all" 遍历全部 9 周期。
    """

    source_name = "internal"
    meta = IngestProviderMeta(
        name="internal",
        display_name="内部计算（技术指标）",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=0,  # 不限流（本地计算）
        capabilities=[
            "technical_indicator",
            # #ARCH-DATA-002 施工项1 语义锚试点（17号 §5.2）：日历类能力标市场/品种
            CapabilityContract("calendar_event", expected_market="a_share", expected_variety="calendar"),
            CapabilityContract("hk_trade_calendar", expected_market="hk", expected_variety="calendar"),
        ],
        known_issues=[],
    )

    # 技术指标表列名顺序（与 schemas/categories/market_technical_indicator.py INSERT_COLUMNS 对齐）
    # 格式：(trade_date, trade_time, symbol, period, 55个指标列, data_source)
    _INDICATOR_COLUMNS: list[str] | None = None  # lazy init from schema

    # 日历事件表列名顺序（与 schemas/categories/market_calendar_event.py INSERT_COLUMNS 对齐）
    # 格式：(event_date, event_type, description, data_source)
    _CALENDAR_EVENT_COLUMNS: list[str] | None = None  # lazy init from schema

    def connect(self) -> None:
        """建立连接——内部计算无需外部连接，直接标记为已连接。"""
        self._connected = True
        self._log.info("InternalComputeProvider 已就绪（本地计算，无需外部连接）")

    def health_check(self) -> bool:
        """探活——检查 ClickHouse 是否可访问。"""
        if not self._connected:
            return False
        try:
            from zephyr.data import ch_reader

            # 简单查询验证 CH 可访问
            result = ch_reader.count("c1_market.kline_daily", limit=1)
            return result >= 0  # count 返回 0 也算健康（表可能空但 CH 可达）
        except Exception as e:  # noqa: BLE001
            self._log.warning("健康检查失败: %s", e)
            return False

    def fetch(self, payload: FetchPayload, policy) -> Iterator[FetchResult]:
        """从 CH 读 K线→计算技术指标→返回 FetchResult（支持多周期）。

        流程：
        1. 从 payload.extra["period"] 读取周期（默认 daily，"all" 遍历 9 周期）
        2. 每个 period：从 c1_market.kline_{period} 读取 OHLCV（120min 从 kline_60min 聚合）
        3. 按标的分组，调用所有已注册 TechnicalIndicatorBase 子类计算指标
        4. 合并所有指标列为宽表行，返回 FetchResult

        Args:
            payload: 下载请求。payload.table 应为 c1_market.technical_indicator。
                payload.symbols=None 表示全市场。
                payload.start/end 为日期范围。
                payload.extra["period"]: 周期字符串或 "all"（默认 daily）。
            policy: 调用策略（本 Provider 不限流，policy 仅用于接口兼容）

        Yields:
            FetchResult：每批一个（按标的分批，避免单批过大）
        """
        # 按 table 路由：calendar_event 走日历事件派生，hk_trade_calendar 走 XHKG 日历，其余走技术指标
        if payload.table == "c1_market.calendar_event":
            yield from self._fetch_calendar_event(payload)
            return
        if payload.table == "c1_market.hk_trade_calendar":
            yield from self._fetch_hk_trade_calendar(payload)
            return
        yield from self._fetch_technical_indicator(payload)

    def _fetch_technical_indicator(self, payload: FetchPayload) -> Iterator[FetchResult]:
        """技术指标默认分支（technical_indicator capability 的命名约定实现）。

        #ARCH-DATA-002 施工项4 接线治本（2026-08-24 G3 批）：frozenset 声明
        technical_indicator 但原默认分支无 _fetch_<cap> 命名方法，声明-实现
        符号一致性双向 gate 接线后会误报"声明残留"——将默认分支收进本命名
        方法，满足命名约定（行为等价：纯移动，逻辑零改动）。

        流程：
        1. 从 payload.extra["period"] 读取周期（默认 daily，"all" 遍历 9 周期）
        2. 每个 period：从 c1_market.kline_{period} 读取 OHLCV（120min 从 kline_60min 聚合）
        3. 按标的分组，调用所有已注册 TechnicalIndicatorBase 子类计算指标
        4. 合并所有指标列为宽表行，返回 FetchResult
        """
        extra = payload.extra or {}
        period = extra.get("period", "daily")
        periods = ALL_PERIODS if period == "all" else [period]

        # 校验周期合法性
        for p in periods:
            if p not in _PERIOD_MAP:
                yield FetchResult(
                    table=payload.table,
                    columns=self._get_indicator_columns(),
                    rows=[],
                    last_key=payload.start.isoformat(),
                    elapsed_sec=0.0,
                    error=f"未知周期: {p}（支持: {list(_PERIOD_MAP.keys())}）",
                )
                return

        for p in periods:
            yield from self._fetch_single_period(payload, p)

    def _fetch_single_period(self, payload: FetchPayload, period: str) -> Iterator[FetchResult]:
        """单个周期的指标计算流程（支持标的分批，防止大数据量 OOM）。

        分批策略：先查标的列表（轻量 DISTINCT 查询），再按 symbol_batch_size
        （默认 100，可通过 payload.extra["symbol_batch_size"] 覆盖）分批读取
        K 线 + 计算指标 + yield FetchResult。每批独立读写，内存占用可控。
        """
        start_time = time.monotonic()
        table = payload.table  # c1_market.technical_indicator
        columns = self._get_indicator_columns()

        try:
            from zephyr.factor.technical_indicators import (
                TechnicalIndicatorRegistry,
                autodiscover_technical_indicators,
            )

            # 确保指标模块已自动发现
            if len(TechnicalIndicatorRegistry.list_all()) == 0:
                autodiscover_technical_indicators()
            registered = TechnicalIndicatorRegistry.list_all()

            # 1. 确定标的列表
            if payload.symbols:
                symbols = list(payload.symbols)
            else:
                symbols = self._get_symbols(payload, period)

            if not symbols:
                self._log.info("无标的可计算（period=%s, %s~%s）", period, payload.start, payload.end)
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=payload.end.isoformat(),
                    elapsed_sec=time.monotonic() - start_time,
                    error=None,
                )
                return

            # 2. 分批处理（防止大数据量 OOM）
            batch_size = (payload.extra or {}).get("symbol_batch_size", 100)
            total_batches = (len(symbols) + batch_size - 1) // batch_size
            self._log.info(
                "[period=%s] 已注册 %d 个技术指标，%d 个标的，分 %d 批（每批 %d），开始计算",
                period,
                len(registered),
                len(symbols),
                total_batches,
                batch_size,
            )

            for batch_idx in range(total_batches):
                batch_start = batch_idx * batch_size
                batch_symbols = symbols[batch_start : batch_start + batch_size]
                batch_time = time.monotonic()

                # 为每批构造子 payload（带 symbol 过滤，限制读取范围）
                batch_payload = FetchPayload(
                    table=payload.table,
                    symbols=batch_symbols,
                    start=payload.start,
                    end=payload.end,
                    incremental=payload.incremental,
                    extra=payload.extra,
                )

                # 读取这批标的的 K 线
                kline_data = self._read_kline_data(batch_payload, period)
                if kline_data.empty:
                    self._log.warning("[period=%s] 批次 %d/%d 无 K线数据", period, batch_idx + 1, total_batches)
                    continue

                # 计算指标
                all_rows: list[tuple] = []
                for symbol in batch_symbols:
                    try:
                        symbol_data = self._filter_symbol(kline_data, symbol, period)
                        if symbol_data.empty:
                            continue
                        indicator_values = self._compute_all_indicators(symbol_data, registered)
                        for bar_ts, row_data in indicator_values.iterrows():
                            row = self._build_row(bar_ts, symbol, period, row_data, columns)
                            all_rows.append(row)
                    except Exception as e:  # noqa: BLE001
                        self._log.error("[period=%s] 标的 %s 指标计算异常: %s", period, symbol, e)
                        continue

                elapsed_batch = time.monotonic() - batch_time
                self._log.info(
                    "[period=%s] 批次 %d/%d 完成: %d 标的 → %d 行, %.1fs",
                    period,
                    batch_idx + 1,
                    total_batches,
                    len(batch_symbols),
                    len(all_rows),
                    elapsed_batch,
                )

                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=all_rows,
                    last_key=payload.end.isoformat(),
                    elapsed_sec=time.monotonic() - start_time,
                    rows_fetched=len(all_rows),
                    error=None,
                )

        except Exception as e:  # noqa: BLE001
            self._log.error("[period=%s] 内部计算 fetch 异常: %s", period, e)
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key=payload.start.isoformat(),
                elapsed_sec=time.monotonic() - start_time,
                error=f"period={period}: {e}",
            )

    def _get_symbols(self, payload: FetchPayload, period: str) -> list[str]:
        """查询指定周期 K 线表中的标的列表（轻量 DISTINCT 查询，不全量读 OHLCV）。"""
        from zephyr.data import ch_reader

        source_table, ts_col, is_intraday = _PERIOD_MAP[period]

        if is_intraday:
            end_next = payload.end + datetime.timedelta(days=1)
            where = f"{ts_col} >= '{payload.start.isoformat()}' AND {ts_col} < '{end_next.isoformat()}'"
        else:
            where = f"trade_date >= '{payload.start.isoformat()}' AND trade_date <= '{payload.end.isoformat()}'"

        sql = _SQL_GET_SYMBOLS.format(table=source_table, where=where)
        tsv = ch_reader.query(sql)
        if not tsv or not tsv.strip():
            return []
        return [line.strip() for line in tsv.strip().split("\n") if line.strip()]

    def disconnect(self) -> None:
        """关闭连接——内部计算无需关闭。"""
        self._connected = False

    # ============== 日历事件派生（calendar_event capability）==============

    def _fetch_calendar_event(self, payload: FetchPayload) -> Iterator[FetchResult]:
        """计算日历事件并返回 FetchResult（月末/季末/交割日/LPR等）。

        从 c1_market.trade_calendar 读取交易日列表，按规则派生全市场日历事件。
        全量重算幂等（ReplacingMergeTree 按 event_date+event_type 去重）。

        事件类型（12 类全覆盖，17号 §3.5 + §6.3）：
            month_end / quarter_end / half_year_end / year_end  月末/季末/半年末/年末
            futures_delivery      股指期货交割日（每月第3个周五，非交易日顺延下一交易日）
            index_option_expiry   股指期权到期日（每月第3个周五）
            etf_option_expiry     ETF期权到期日（每月第4个周三，非交易日顺延）
            lpr_announcement      LPR公布日（每月20日，遇周末顺延下一工作日）
            hk_connect_closed     港股通休市日（A股开盘但港股休市）
            fomc_meeting          美联储FOMC议息日（manual CSV 台账合并）
            major_meeting         重要会议（两会/中央经济工作会议，manual CSV）
            stamp_duty_change     印花税调整日（manual CSV）

        Args:
            payload: 下载请求。payload.start/end 为事件日期范围。
                payload.table 应为 c1_market.calendar_event。

        Yields:
            FetchResult：单批（所有事件一次返回）。
        """
        start_time = time.monotonic()
        table = payload.table
        columns = self._get_calendar_event_columns()

        try:
            # 日历事件需覆盖未来事件（即将到来的交割日/期权到期/LPR等），
            # 但 scheduler 对 full-refresh 任务固定 start=月初/end=today。
            # 故本 Provider 自行计算宽范围 [today-5年, today+2年]，
            # 全量重算幂等（ReplacingMergeTree 按 event_date+event_type 去重）。
            today = datetime.date.today()
            range_start = today.replace(year=today.year - 5)
            range_end = today.replace(year=today.year + 2)

            # 1. 读交易日列表
            trading_days = self._read_trading_days(range_start, range_end)
            if not trading_days:
                self._log.info("无交易日历数据可计算 calendar_event（%s~%s）", range_start, range_end)
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=today.isoformat(),
                    elapsed_sec=time.monotonic() - start_time,
                    error=None,
                )
                return

            trading_days_set = set(trading_days)
            by_month = self._group_trading_days_by_month(trading_days)

            rows: list[tuple] = []
            rows += _derive_month_ends(by_month)
            rows += _derive_futures_and_index_option_expiry(by_month, trading_days_set, range_start, range_end)
            rows += _derive_etf_option_expiry(by_month, trading_days_set, range_start, range_end)
            rows += _derive_lpr_announcement(by_month, range_start, range_end)
            rows += self._derive_hk_connect_closed(trading_days_set, range_start, range_end)
            # manual 三类（fomc_meeting/major_meeting/stamp_duty_change，17号 §6.3）：
            # CSV 台账合并，同表同批一次回填，calendar_event 覆盖 12 类 event_type
            rows += _load_manual_calendar_events(range_start, range_end)

            unique_rows = _dedupe_and_sort_events(rows)

            self._log.info("calendar_event 计算完成：%s~%s 共 %d 个事件", range_start, range_end, len(unique_rows))

            yield FetchResult(
                table=table,
                columns=columns,
                rows=unique_rows,
                last_key=today.isoformat(),
                elapsed_sec=time.monotonic() - start_time,
                rows_fetched=len(unique_rows),
                error=None,
            )

        except Exception as e:  # noqa: BLE001
            self._log.error("calendar_event 计算异常: %s", e)
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key=datetime.date.today().isoformat(),
                elapsed_sec=time.monotonic() - start_time,
                error=f"calendar_event: {e}",
            )

    # ---- calendar_event 派生子方法（拆分以降低循环复杂度，NO-HIGH-COMPLEXITY gate）----

    @staticmethod
    def _group_trading_days_by_month(
        trading_days: list[datetime.date],
    ) -> dict[tuple[int, int], datetime.date]:
        """按 (year, month) 分组取每月最大交易日。"""
        by_month: dict[tuple[int, int], datetime.date] = {}
        for d in trading_days:
            key = (d.year, d.month)
            if key not in by_month or d > by_month[key]:
                by_month[key] = d
        return by_month

    def _derive_hk_connect_closed(
        self,
        trading_days_set: set[datetime.date],
        range_start: datetime.date,
        range_end: datetime.date,
    ) -> list[tuple]:
        """港股通休市日（A股开盘但港股休市，北向资金停摆）。"""
        hk_trading_days = self._read_hk_trading_days(range_start, range_end)
        if not hk_trading_days:
            self._log.warning("hk_trade_calendar 无数据，跳过 hk_connect_closed 计算")
            return []
        hk_open_set = set(hk_trading_days)
        hk_closed_days = sorted(trading_days_set - hk_open_set)
        self._log.info("hk_connect_closed: A股开盘但港股休市 %d 天", len(hk_closed_days))
        return [
            (
                d,
                "hk_connect_closed",
                f"{d.isoformat()} 港股通休市（A股开盘/港股休市，北向资金停摆）",
                "internal",
            )
            for d in hk_closed_days
        ]

    def _fetch_hk_trade_calendar(self, payload: FetchPayload) -> Iterator[FetchResult]:
        """港股交易日历全量刷新（exchange_calendars XHKG），写入 c1_market.hk_trade_calendar。

        #ARCH-DATA-001: 从 akshare tool_trade_date_hist_sina（实为 A 股日历）迁移到
        exchange_calendars XHKG（港交所真日历，含圣诞/复活节/佛诞等休市）。
        akshare 版语义错配已移除——见 akshare_provider 删除记录与本 issue 条目。

        scheduler 对 full-refresh 任务固定 start=月初/end=today，但港股日历需
        覆盖历史+未来，故自行计算宽范围 [today-5年, today+2年]（同 calendar_event
        策略）。全量重算幂等（ReplacingMergeTree 按 cal_date 去重）。

        输出列与历史 akshare 版对齐：cal_date / is_open / pretrade_date，
        其中 is_open 恒为 1（仅产出交易日行，非交易日不入表）。
        """
        start_time = time.monotonic()
        table = payload.table
        columns = ["cal_date", "is_open", "pretrade_date"]

        cal = _get_xhkg_calendar()
        if cal is None:
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key="",
                elapsed_sec=time.monotonic() - start_time,
                error="exchange_calendars XHKG 不可用，无法生成港股交易日历",
            )
            return

        try:
            today = datetime.date.today()
            range_start = today.replace(year=today.year - 5)
            range_end = today.replace(year=today.year + 2)

            # 优先 sessions_in_range（一次性返回，快）；老版本无此 API 时回退 is_session 逐日判断
            trading_days: list[datetime.date] = []
            try:
                sessions = cal.sessions_in_range(range_start.isoformat(), range_end.isoformat())
                trading_days = [pd.Timestamp(d).date() for d in sessions]
            except Exception:  # noqa: BLE001 — 回退逐日判断（与 trading_calendar.is_trading_day 同源）
                trading_days = []
                cur = range_start
                while cur <= range_end:
                    try:
                        if cal.is_session(cur.isoformat()):
                            trading_days.append(cur)
                    except Exception:  # noqa: BLE001 — 越界日期等
                        pass
                    cur += datetime.timedelta(days=1)

            trading_days.sort()
            rows: list[tuple] = []
            for i, d in enumerate(trading_days):
                pretrade = trading_days[i - 1].isoformat() if i > 0 else ""
                rows.append((d.isoformat(), 1, pretrade))

            self._log.info(
                "hk_trade_calendar 计算完成（XHKG）：%s~%s 共 %d 个港股交易日",
                range_start,
                range_end,
                len(rows),
            )
            yield FetchResult(
                table=table,
                columns=columns,
                rows=rows,
                last_key=today.isoformat(),
                elapsed_sec=time.monotonic() - start_time,
                rows_fetched=len(rows),
                error=None,
            )
        except Exception as e:  # noqa: BLE001
            self._log.error("hk_trade_calendar 计算异常: %s", e)
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key="",
                elapsed_sec=time.monotonic() - start_time,
                error=f"hk_trade_calendar: {e}",
            )

    def _read_trading_days(self, start: datetime.date, end: datetime.date) -> list[datetime.date]:
        """从 ClickHouse trade_calendar 读取交易日列表（is_open=1，去重）。"""
        from zephyr.data import ch_reader

        sql = _SQL_READ_TRADING_DAYS.format(start=start.isoformat(), end=end.isoformat())
        tsv = ch_reader.query(sql)
        if not tsv or not tsv.strip():
            return []
        days: list[datetime.date] = []
        for line in tsv.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            days.append(datetime.date.fromisoformat(line))
        return days

    def _read_hk_trading_days(self, start: datetime.date, end: datetime.date) -> list[datetime.date]:
        """从 ClickHouse hk_trade_calendar 读取港股交易日列表（is_open=1，去重）。

        用于 calendar_event 的 hk_connect_closed 计算：A股开盘但港股休市 = 北向资金停摆日。
        """
        from zephyr.data import ch_reader

        sql = _SQL_READ_HK_TRADING_DAYS.format(start=start.isoformat(), end=end.isoformat())
        try:
            tsv = ch_reader.query(sql)
        except Exception as e:  # noqa: BLE001 — 表可能不存在或无数据
            self._log.warning("读取 hk_trade_calendar 失败: %s", e)
            return []
        if not tsv or not tsv.strip():
            return []
        days: list[datetime.date] = []
        for line in tsv.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            days.append(datetime.date.fromisoformat(line))
        return days

    @classmethod
    def _get_calendar_event_columns(cls) -> list[str]:
        """获取 calendar_event 表的列名顺序（lazy init from schema）。"""
        if cls._CALENDAR_EVENT_COLUMNS is not None:
            return cls._CALENDAR_EVENT_COLUMNS
        try:
            from schemas.categories.market_calendar_event import INSERT_COLUMNS

            cols_str = INSERT_COLUMNS.strip("()")
            cls._CALENDAR_EVENT_COLUMNS = [c.strip() for c in cols_str.split(",")]
        except Exception:  # noqa: BLE001
            cls._CALENDAR_EVENT_COLUMNS = ["event_date", "event_type", "description", "data_source"]
        return cls._CALENDAR_EVENT_COLUMNS

    # ============== 内部方法（技术指标）==============

    @classmethod
    def _get_indicator_columns(cls) -> list[str]:
        """获取 technical_indicator 表的列名顺序（lazy init from schema）。

        从 schemas.categories.market_technical_indicator.INSERT_COLUMNS 加载。
        若直接导入失败（如工作目录不在项目根），自动补项目根到 sys.path 重试。
        最终失败时抛 RuntimeError 而非静默 fallback——静默 fallback 到 5 列会
        导致所有指标值被丢弃，是比崩溃更危险的静默错误。
        """
        if cls._INDICATOR_COLUMNS is not None:
            return cls._INDICATOR_COLUMNS

        try:
            try:
                from schemas.categories.market_technical_indicator import INSERT_COLUMNS
            except ImportError:
                # 补项目根到 sys.path（provider 在 src/zephyr/data/implementations/，
                # 项目根 = parents[4]）
                import pathlib
                import sys

                project_root = str(pathlib.Path(__file__).resolve().parents[4])
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                from schemas.categories.market_technical_indicator import INSERT_COLUMNS

            # INSERT_COLUMNS 格式: "(col1, col2, ...)" → 去括号+空格 split
            cols_str = INSERT_COLUMNS.strip("()")
            cls._INDICATOR_COLUMNS = [c.strip() for c in cols_str.split(",")]
        except Exception as e:  # noqa: BLE001
            # 不再静默 fallback 到 5 列——那会导致所有指标值被丢弃
            raise RuntimeError(f"无法加载 technical_indicator 表 INSERT_COLUMNS，指标值将被丢弃: {e}") from e
        return cls._INDICATOR_COLUMNS

    def _read_kline_data(self, payload: FetchPayload, period: str):
        """从 ClickHouse 读取 K线 OHLCV 数据（按 period 选表）。

        120min 特殊处理：从 kline_60min 读取后两根聚合为一根。
        """
        from io import StringIO

        from zephyr.data import ch_reader

        source_table, ts_col, is_intraday = _PERIOD_MAP[period]

        # 构建 WHERE 子句
        # 日/周/月线：用 trade_date 过滤；分钟线：用 trade_time 范围过滤
        # （kline_5min 无 trade_date 列，统一用 trade_time 避免报错）
        if is_intraday:
            end_next = payload.end + datetime.timedelta(days=1)
            where_parts = [
                f"{ts_col} >= '{payload.start.isoformat()}'",
                f"{ts_col} < '{end_next.isoformat()}'",
            ]
        else:
            where_parts = [
                f"trade_date >= '{payload.start.isoformat()}'",
                f"trade_date <= '{payload.end.isoformat()}'",
            ]
        if payload.symbols:
            symbols_str = ",".join(f"'{s}'" for s in payload.symbols)
            where_parts.append(f"symbol IN ({symbols_str})")
        where_clause = " AND ".join(where_parts)

        # SELECT 列：日内用 toDate(trade_time) 派生 trade_date（kline_5min 无原生列）
        if is_intraday:
            select_cols = f"toDate({ts_col}) AS trade_date, {ts_col}, symbol, open, high, low, close, volume, amount"
            order_by = f"symbol, {ts_col}"
        else:
            select_cols = "trade_date, symbol, open, high, low, close, volume, amount"
            order_by = "symbol, trade_date"

        sql = _SQL_READ_KLINE.format(
            select_cols=select_cols, table=source_table, where_clause=where_clause, order_by=order_by
        )

        tsv = ch_reader.query(sql)
        if not tsv or not tsv.strip():
            return pd.DataFrame()

        # 解析 TSV → DataFrame（dtype=str 防止 symbol 前导零被剥离，如 000001→1）
        df = pd.read_csv(StringIO(tsv), sep="\t", header=None, dtype=str)
        if is_intraday:
            df.columns = ["trade_date", ts_col, "symbol", "open", "high", "low", "close", "volume", "amount"]
            df[ts_col] = pd.to_datetime(df[ts_col])
        else:
            df.columns = ["trade_date", "symbol", "open", "high", "low", "close", "volume", "amount"]
        df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date  # 保留为 date 对象
        # 数值列转 float（read_csv dtype=str 全部为字符串，需显式转换）
        for col in ["open", "high", "low", "close", "volume", "amount"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 120min：从 60min 两根聚合
        if period == "120min":
            df = self._aggregate_120min(df)

        return df

    @staticmethod
    def _aggregate_120min(df_60min: pd.DataFrame) -> pd.DataFrame:
        """将 60min K线两根聚合为 120min K线（施工图 §3.4 已裁定）。

        聚合规则：
          - 按 (symbol, trade_date) 分组，组内按 trade_time 排序
          - 每 2 根合并为 1 根 120min（09:30-11:30 / 13:00-15:00）
          - open=第一根 open, high=max, low=min, close=第二根 close, volume=sum
          - 120min 的 trade_time = 第一根 60min 的 trade_time

        若某交易日 60min 根数为奇数（异常），最后一根单独成 120min（不丢弃）。

        向量化实现（替代原逐行 Python 循环，提速 ~20x）。
        """
        if df_60min.empty:
            return df_60min

        # 按 (symbol, trade_date, trade_time) 全局排序
        df = df_60min.sort_values(["symbol", "trade_date", "trade_time"]).reset_index(drop=True)

        # 在每个 (symbol, trade_date) 组内分配 pair_idx（每 2 根一对）
        df["pair_idx"] = df.groupby(["symbol", "trade_date"]).cumcount() // 2

        # 按 (symbol, trade_date, pair_idx) 向量化聚合
        agg_df = (
            df.groupby(["symbol", "trade_date", "pair_idx"], sort=False)
            .agg(
                trade_time=("trade_time", "first"),
                open=("open", "first"),
                high=("high", "max"),
                low=("low", "min"),
                close=("close", "last"),
                volume=("volume", "sum"),
                amount=("amount", "sum") if "amount" in df.columns else ("volume", "sum"),
            )
            .reset_index()
        )

        # 丢弃 pair_idx，恢复原列顺序
        result = agg_df[["trade_date", "trade_time", "symbol", "open", "high", "low", "close", "volume", "amount"]]
        return result

    def _filter_symbol(self, kline_data, symbol, period):
        """从 K线 DataFrame 中过滤出指定标的的数据，设置 bar timestamp 为 index。

        - 日内周期：index = trade_time（DateTime，日内多根 K 线可区分）
        - 日/周/月线：index = trade_date（转 DateTime，午夜）
        """
        _, ts_col, is_intraday = _PERIOD_MAP[period]
        mask = kline_data["symbol"] == symbol
        symbol_data = kline_data[mask].copy()

        if is_intraday:
            symbol_data = symbol_data.set_index(ts_col)
        else:
            symbol_data = symbol_data.set_index("trade_date")
            symbol_data.index = pd.to_datetime(symbol_data.index)

        # 确保列名为 OHLCV（去掉 symbol/trade_date 等非指标列）
        ohlcv_cols = ["open", "high", "low", "close", "volume", "amount"]
        available = [c for c in ohlcv_cols if c in symbol_data.columns]
        return symbol_data[available]

    def _compute_all_indicators(self, symbol_data, registered_indicators):
        """调用所有已注册指标计算，返回合并的 DataFrame。

        Args:
            symbol_data: 单标的 OHLCV DataFrame，index=datetime（bar timestamp）
            registered_indicators: list[TechnicalIndicatorMeta]

        Returns:
            DataFrame，index=bar timestamp，columns=所有指标输出列
        """
        from zephyr.factor.technical_indicators import TechnicalIndicatorRegistry

        results = []
        for meta in registered_indicators:
            try:
                indicator_cls = TechnicalIndicatorRegistry.get(meta.indicator_id)
                indicator = indicator_cls()
                result_df = indicator.compute(symbol_data)
                if result_df is not None and not result_df.empty:
                    results.append(result_df)
            except NotImplementedError:
                # 跳过未实现的指标（Phase 1 完成后不应触发）
                continue

        if not results:
            return pd.DataFrame(index=symbol_data.index)

        # 合并所有指标列
        merged = pd.concat(results, axis=1)
        return merged

    def _build_row(self, bar_ts, symbol, period, row_data, columns) -> tuple:
        """构造一行宽表数据 tuple（与 INSERT_COLUMNS 对齐）。

        Args:
            bar_ts: bar 时间戳（日内=trade_time DateTime，日/周/月=trade_date 午夜 DateTime）
            symbol: 标的代码
            period: 周期字符串
            row_data: 该 bar 的指标值（Series 或 dict）
            columns: 列名顺序
        """
        # 统一转为 datetime（trade_time 写入用）
        bar_dt = pd.Timestamp(bar_ts).to_pydatetime()
        trade_date = bar_dt.date()

        row = []
        for col in columns:
            if col == "trade_date":
                row.append(trade_date)
            elif col == "trade_time":
                row.append(bar_dt)
            elif col == "symbol":
                row.append(symbol)
            elif col == "period":
                row.append(period)
            elif col == "data_source":
                row.append("internal")
            else:
                val = row_data.get(col) if hasattr(row_data, "get") else None
                row.append(val if not (isinstance(val, float) and pd.isna(val)) else None)
        return tuple(row)
