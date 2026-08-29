# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.backfill_checker
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.tick_subscriber; zephyr.data.provider_base; zephyr.data.policy_registry; zephyr.data.implementations.akshare_provider; zephyr.data.calendar
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 查CH实际行数发现缺口; 只补缺失不重复下载; 写入tick_data走ch_writer统一通道(TCP→HTTP→本地落盘); 查询走ch_reader自动注入FINAL; run_known_gap_backfill()读取known_data_gaps.yaml检测已登记历史缺口(不受7天窗口限制, audit 2.7/3.8治本); 慢变化表(静态重建schedule或业务事件日期列)threshold强制0跳过日频缺口检测(#ARCH-DATA-017); kline_index走专用补下载路径(symbol级差集检测+显式缺失日期窗口经akshare provider回填,绕开last_key超前推进致部分覆盖日补不回缺口, 2026-08-24 D1)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH查询失败->返回None; CH写入失败->重试3次后返回False; xtquant不可用->返回0
# [TESTS]
# [A_module] module_id=MOD-GOV_BACKFILL_CHECKER | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""L10 周末补下载检测器——检测过去N天缺失数据并精准补下载。

设计理念（裁定 #ARCH-BACKFILL-001）：
  - 不依赖 last_key：直接查 ClickHouse 实际行数，发现真实缺口
  - 只补缺失：不重复下载已有数据，节省带宽
  - 写入走 ch_writer 统一通道（TCP→HTTP→本地落盘，Hyper-V 迁移 2026-07-16）

与现有机制的关系：
  - L1-L7（盘中/盘后增量）：依赖 last_key，scheduler 中断时 last_key 不更新
  - L8（全量校准）：重拉全量数据，耗时长
  - L10（本模块）：查 CH 实际行数 → 发现缺口 → 精准补下载

调用方式：
  scheduler.run_schedule("weekend_backfill") → run_weekend_backfill(scheduler)
  也可独立调用：python -c "from zephyr.data.backfill_checker import run_weekend_backfill; run_weekend_backfill()"
"""

from __future__ import annotations

import datetime
import logging
import os
import time
from pathlib import Path
from time import sleep
from typing import Final

import yaml

from zephyr.data import ch_reader, ch_writer
from zephyr.data.calendar import MarketCalendar, get_market_calendar
from zephyr.data.table_registry import get_registry
from zephyr.data.tick_subscriber import _safe_int

log = logging.getLogger(__name__)

# 默认 A 股日历（保持向后兼容，零行为变化）
_DEFAULT_CALENDAR: Final = get_market_calendar("ashare")

# ========== 常量 ==========

# tick_data 缺失阈值：每天低于此值视为缺失（正常约2000万行/天）
_TICK_THRESHOLD = 5_000_000

# 补下载默认天数
_DEFAULT_BACKFILL_DAYS = 7

# 每批写入 ClickHouse 的标的数
_BATCH_SYMBOLS = 50

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_TRADE_CALENDAR = get_registry().table("market_trade_calendar")
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")
_TBL_TICK_DATA = get_registry().table("market_tick")
_TBL_KLINE_INDEX = get_registry().table("market_index_kline")

_SQL_TRADE_CALENDAR = (
    f"SELECT cal_date FROM {_TBL_TRADE_CALENDAR} "
    "WHERE cal_date >= toDate('{start}') AND cal_date <= toDate('{today}') "
    "AND is_open = 1 ORDER BY cal_date"
)
_SQL_KLINE_DISTINCT = (
    f"SELECT DISTINCT trade_date FROM {_TBL_KLINE_DAILY} "
    "WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{today}') "
    "ORDER BY trade_date"
)
# 注：table 须为全名（含 db 前缀，如 c1_market.tick_data）——_TBL_TICK_DATA 来自
# 品类注册表 get_registry().table() 即全名；勿再叠加硬编码前缀（2026-08-14 双重前缀事故）
_SQL_COUNT_BY_DATE = "SELECT count() FROM {table} WHERE trade_date=toDate('{d_str}')"

# tick_data 表写入列子句（用于 ch_writer.write_tsv）
_TICK_DATA_COLS = (
    "(trade_date,timestamp,symbol,market_type,price,volume,amount,"
    "direction,data_source,bid_price,ask_price,bid_volume,ask_volume)"
)
_TICK_DATA_TABLE = _TBL_TICK_DATA


# ========== ClickHouse 查询（统一走 ch_reader，自动注入 FINAL） ==========


def _ch_query(query: str, timeout: int = 30) -> str | None:
    """通过 ch_reader 查询单值（自动注入 FINAL，二级降级 TCP→HTTP）。"""
    result = ch_reader.query(query, timeout=timeout)
    return result.strip() or None


def _ch_insert_tsv(tsv_lines: list[str], retries: int = 3) -> bool:
    """通过 ch_writer 写入 TSV（二级降级 TCP→HTTP，本地落盘兜底）。"""
    tsv_data = "\n".join(tsv_lines) + "\n"
    tsv_bytes = tsv_data.encode("utf-8")

    for i in range(retries):
        try:
            ok = ch_writer.write_tsv(
                _TICK_DATA_TABLE,
                _TICK_DATA_COLS,
                tsv_bytes,
                timeout=120,
            )
            if ok:
                return True
            log.warning("CH写入失败(%d/%d)", i + 1, retries)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning("CH写入异常(%d/%d): %s", i + 1, retries, e)
        sleep(2)
    return False


# ========== 交易日历 ==========


def get_trade_dates(
    days: int = 7,
    *,
    calendar: MarketCalendar | None = None,
) -> list[datetime.date]:
    """获取过去N天的交易日列表（默认 A 股日历，可注入其他市场日历）。

    优先从 trade_calendar 表查 is_open=1；fallback 到 kline_daily 中有数据的日期；
    再 fallback 到日历接口直接生成（适用于 7×24 市场）。

    Args:
        days: 回溯天数
        calendar: 市场日历注入（None=ASHareCalendar 默认，零行为变化）
    """
    cal = calendar or _DEFAULT_CALENDAR
    today = datetime.date.today()
    start = today - datetime.timedelta(days=days)
    query = _SQL_TRADE_CALENDAR.format(start=start, today=today)
    result = _ch_query(query)
    if not result:
        # fallback: 用 kline_daily 中有数据的日期
        log.warning("trade_calendar 无数据，fallback 到 kline_daily")
        query2 = _SQL_KLINE_DISTINCT.format(start=start, today=today)
        result = _ch_query(query2)
        if not result:
            log.warning("kline_daily 也无数据，fallback 到日历接口生成")
            # 最终 fallback：用日历接口直接生成（7×24 市场每日皆交易日）
            return cal.trading_days_in_range(start, today)

    dates = []
    for line in result.strip().split("\n"):
        line = line.strip()
        if line:
            try:
                dates.append(datetime.date.fromisoformat(line))
            except ValueError:
                pass
    return dates


# ========== 缺失检测 ==========


def detect_missing_dates(
    table: str,
    dates: list[datetime.date],
    threshold: int,
) -> list[datetime.date]:
    """检测指定表在哪些日期的数据行数低于阈值。

    Args:
        table: 全表名含 db 前缀（如 c1_market.tick_data，来自品类注册表）
        dates: 待检测的日期列表
        threshold: 行数低于此值视为缺失

    Returns:
        缺失日期列表
    """
    missing = []
    for d in dates:
        d_str = d.isoformat()
        cnt = _ch_query(_SQL_COUNT_BY_DATE.format(table=table, d_str=d_str))
        try:
            count = int(cnt or 0)
        except ValueError:
            count = 0
        if count < threshold:
            log.info("检测到缺失: %s %s 行数=%d 阈值=%d", table, d_str, count, threshold)
            missing.append(d)
        else:
            log.debug("正常: %s %s 行数=%d", table, d_str, count)
    return missing


# ========== 动态发现（从 tasks.yaml 自动检测所有表） ==========

# tasks.yaml 路径
_TASKS_YAML_PATH = Path(__file__).parent / "config" / "tasks.yaml"

# 日期列名优先级（按常见命名排序）
_DATE_COLUMN_PRIORITIES = [
    "trade_date",
    "end_date",
    "report_date",
    "unlock_date",
    "announce_date",
    "date",
    "fdate",
]

# 业务事件日期列（#ARCH-DATA-017 施工项2，2026-08-15 裁定）：
# 这些列的语义是业务事件发生日（解禁日/上市日/生效日/公告日/报告期），而非采集日——
# 用"近7个交易日必有数据"的日频口径检测必然误报（restricted_shares/share_unlock 等实证）。
# 命中即 threshold 强制 0，按"慢变化"类别确定性跳过，不再靠零阈值偶然躲过。
_BUSINESS_EVENT_DATE_COLS = frozenset(
    {
        "unlock_date",  # 解禁日（restricted_shares/share_unlock）
        "list_date",  # 上市日（stock_list）
        "valid_from",  # 生效日（industry_class/concept_board/lof_list 等）
        "setup_date",  # 成立日（etf_list）
        "end_date",  # 截止日（equity_pledge_summary/convertible_bond_list）
        "announce_date",  # 公告日（财报表按季披露，本就应跳过日频检测）
        "report_period",  # 报告期（main_business）
    }
)

# 静态/全量重建类调度时段（#ARCH-DATA-017 施工项2）：
# 月度/周末周期性全量重建的表无日频采集语义，跳过日频缺口检测。
# 注意边界：daily_* 时段的 incremental=false 任务是 #ARCH-REALTIME-ACCUM
# 每日快照积累（weather_data/stock_hot_rank 等，实时源无历史API、错过无法回填），
# 不是静态表，必须保留日频检测——故按 schedule 判定而非裸 incremental 标志。
_STATIC_REFRESH_SCHEDULES = frozenset({"monthly_static", "weekend_calibration"})

# SQL 模板（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_DESCRIBE = "DESCRIBE TABLE {table}"
_SQL_AVG_ROWS_7D = (
    "SELECT avg(cnt) FROM ("
    "SELECT count() AS cnt FROM {table} "
    "WHERE {date_col} >= toDate(today() - 7) "
    "AND {date_col} < today() "
    "GROUP BY toDate({date_col}))"
)
# 注：date_col 统一 toDate() 包裹——Date 列为 no-op，DateTime64 列为正确化
# （修复 kline_5min.trade_time 等 DateTime64 列等值/分组比较恒失真问题）
_SQL_COUNT_BY_CUSTOM_DATE = "SELECT count() FROM {table} WHERE toDate({date_col})=toDate('{d_str}')"


def _load_tasks_yaml() -> list[dict]:
    """加载 tasks.yaml 中的任务列表。"""
    if not _TASKS_YAML_PATH.exists():
        log.warning("tasks.yaml 不存在: %s", _TASKS_YAML_PATH)
        return []
    with open(_TASKS_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("tasks", [])


def _infer_date_column(table: str) -> str:
    """从 DESCRIBE TABLE 推断日期列名。

    优先选 trade_date/end_date/report_date 等常见命名，
    否则取第一个 Date 类型列。

    Returns:
        日期列名。推断失败返回空字符串。
    """
    out = ch_reader.query(_SQL_DESCRIBE.format(table=table))
    if not out or not out.strip():
        return ""
    date_cols = []
    for line in out.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        name, col_type = parts[0], parts[1]
        if "Date" in col_type or "DateTime" in col_type:
            date_cols.append(name)
    if not date_cols:
        return ""
    # 按优先级选
    for priority_name in _DATE_COLUMN_PRIORITIES:
        if priority_name in date_cols:
            return priority_name
    return date_cols[0]


def _infer_threshold(table: str, date_col: str) -> int:
    """从历史7天平均行数推断缺失阈值。

    阈值 = 过去7天日均行数 × 0.5（低于均值50%视为缺失）。
    无历史数据或表为空时返回 0（跳过巡检）。

    Returns:
        阈值行数。
    """
    if not date_col:
        return 0
    out = ch_reader.query(_SQL_AVG_ROWS_7D.format(table=table, date_col=date_col))
    try:
        avg = float(out.strip()) if out and out.strip() else 0.0
    except (ValueError, TypeError):
        return 0
    # NaN 检查：表无近7天数据时 avg() 返回 NaN，int(NaN) 会抛 ValueError
    if avg != avg or avg <= 0:  # noqa: PLR0124 — NaN != NaN 是标准 NaN 检测法
        return 0
    return int(avg * 0.5)


def _discover_backfill_tables() -> list[dict]:
    """从 tasks.yaml 动态发现所有需要补下载的表。

    新增表只需在 tasks.yaml 注册任务，即可自动纳入补下载覆盖范围。
    同表多任务去重，取第一个非 disabled 任务。

    慢变化表口径排除（#ARCH-DATA-017 施工项2，2026-08-15 裁定）：
      - schedule 属于静态/全量重建时段（monthly_static/weekend_calibration）的表
        无日频采集语义（stock_list/index_constituent/sector_list 等）；
      - 日期列属于业务事件日期（unlock_date/list_date/valid_from 等）的表，
        事件日≠采集日，日频口径检测必误报（restricted_shares 等实证）；
      两类均 threshold 强制 0，确定性跳过日频缺口检测，不再靠零阈值偶然躲过。
      边界：daily_* 时段的 incremental=false 任务是 #ARCH-REALTIME-ACCUM 每日
      快照积累（weather_data/stock_hot_rank 等，错过无法回填），保留检测。

    Returns:
        表信息列表，每项含 table/task_id/source/capability/date_column/threshold。
    """
    tasks = _load_tasks_yaml()
    tables: dict[str, dict] = {}
    for task in tasks:
        if (task.get("extra") or {}).get("disabled"):
            continue
        table = task.get("table", "")
        if not table or table.startswith("_"):  # 跳过治理表
            continue
        if table not in tables:
            tables[table] = {
                "table": table,
                "task_id": task.get("task_id", ""),
                "source": task.get("source", ""),
                "capability": task.get("capability", ""),
                "schedule": task.get("schedule", ""),
            }
    # 推断日期列和阈值
    for info in tables.values():
        info["date_column"] = _infer_date_column(info["table"])
        if info["schedule"] in _STATIC_REFRESH_SCHEDULES:
            # 静态/全量重建类：无日频采集语义，跳过日频缺口检测
            info["threshold"] = 0
            info["skip_reason"] = "static_refresh"
        elif info["date_column"] in _BUSINESS_EVENT_DATE_COLS:
            # 业务事件日期列：事件日≠采集日，日频口径必误报
            info["threshold"] = 0
            info["skip_reason"] = "business_event_date"
        else:
            info["threshold"] = _infer_threshold(info["table"], info["date_column"])
    return list(tables.values())


def detect_missing_dates_generic(
    table: str,
    date_col: str,
    dates: list[datetime.date],
    threshold: int,
) -> list[datetime.date]:
    """通用缺失检测（支持任意日期列名）。

    Args:
        table: 表名（如 kline_daily）
        date_col: 日期列名（如 trade_date）
        dates: 待检测的日期列表
        threshold: 行数低于此值视为缺失

    Returns:
        缺失日期列表
    """
    if not date_col or threshold <= 0:
        return []
    missing = []
    for d in dates:
        d_str = d.isoformat()
        cnt = ch_reader.query(_SQL_COUNT_BY_CUSTOM_DATE.format(table=table, date_col=date_col, d_str=d_str))
        try:
            count = int(cnt.strip()) if cnt and cnt.strip() else 0
        except ValueError:
            count = 0
        if count < threshold:
            log.info("检测到缺失: %s[%s] %s 行数=%d 阈值=%d", table, date_col, d_str, count, threshold)
            missing.append(d)
    return missing


# ========== Tick 数据解析 ==========


def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        f = float(val)
        return f if f == f and f != 0 else None  # 过滤 NaN 和 0
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None


def _list_first(lst):
    """取列表第一个元素，非列表直接返回。"""
    if lst is None:
        return None
    if isinstance(lst, (list, tuple)):
        return lst[0] if len(lst) > 0 else None
    return lst


def _detect_market_type(stock_code: str) -> str:
    code = stock_code.split(".")[0].zfill(6)
    suffix = stock_code.split(".")[-1] if "." in stock_code else ""
    if suffix == "BJ":
        return "stock_bj"
    prefix = code[:3]
    if prefix in ("399",) or (prefix == "000" and suffix == "SH"):
        return "index"
    if prefix[:2] in ("15", "51", "52"):
        return "etf"
    if prefix[:2] in ("11", "12"):
        return "cb"
    return "stock"


def _parse_tick_df(df, stock_code: str) -> list[str]:
    """解析 QMT tick DataFrame 为 TSV 行列表。

    QMT tick 列名（实测）：
      lastPrice, open, high, low, lastClose, amount, volume,
      askPrice(列表5档), bidPrice(列表5档), askVol(列表), bidVol(列表), ...
    索引为 YYYYMMDDHHMMSS 格式整数。
    """
    if df is None or len(df) == 0:
        return []

    symbol = stock_code.split(".")[0]
    market_type = _detect_market_type(stock_code)
    tsv_lines = []

    for ts, row in df.iterrows():
        s = str(int(ts))
        if len(s) >= 14:
            dt = datetime.datetime.strptime(s[:14], "%Y%m%d%H%M%S")
        elif len(s) >= 8:
            dt = datetime.datetime.strptime(s[:8], "%Y%m%d")
        else:
            continue

        trade_date = dt.strftime("%Y-%m-%d")
        timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")

        price = _safe_float(row.get("lastPrice"))
        vol = _safe_int(row.get("volume"))
        amt = _safe_float(row.get("amount"))
        bid_price = _safe_float(_list_first(row.get("bidPrice")))
        ask_price = _safe_float(_list_first(row.get("askPrice")))
        bid_vol = _safe_int(_list_first(row.get("bidVol")))
        ask_vol = _safe_int(_list_first(row.get("askVol")))
        # #ARCH-CH-033: UInt64 列不支持负数，QMT 某些指数 tick
        # volume 为 int32 溢出负值（如 399379 vol=-2147422702），
        # 导致 CH INSERT Code 27 解析失败。过滤为 None（TSV \N）。
        if vol is not None and vol < 0:
            vol = None
        if bid_vol is not None and bid_vol < 0:
            bid_vol = None
        if ask_vol is not None and ask_vol < 0:
            ask_vol = None

        tsv_lines.append(
            "\t".join(
                [
                    trade_date,
                    timestamp_str,
                    symbol,
                    market_type,
                    str(price) if price is not None else "\\N",
                    str(vol) if vol is not None else "\\N",
                    str(amt) if amt is not None else "\\N",
                    "",
                    "miniqmt",
                    str(bid_price) if bid_price is not None else "\\N",
                    str(ask_price) if ask_price is not None else "\\N",
                    str(bid_vol) if bid_vol is not None else "\\N",
                    str(ask_vol) if ask_vol is not None else "\\N",
                ]
            )
        )
    return tsv_lines


# ========== Tick 补下载 ==========


def backfill_tick_data(dates: list[datetime.date]) -> int:
    """补下载指定日期的 tick 数据。

    通过 QMT xtdata 下载 + ch_writer 写入 ClickHouse。
    每天分 09:30-10:00 和 10:00-15:30 两个时段（避免单次数据过大）。

    Args:
        dates: 需要补下载的日期列表

    Returns:
        总写入行数
    """
    if not dates:
        log.info("无需补下载 tick 数据")
        return 0

    try:
        from xtquant import xtdata

        xtdata.enable_hello = False
    except ImportError:
        log.error("xtquant 不可用，无法补下载 tick 数据")
        return 0

    symbols = xtdata.get_stock_list_in_sector("沪深A股")
    log.info("补下载 tick: %d个日期, %d只标的", len(dates), len(symbols))

    total_rows = 0
    for d in dates:
        d_str = d.isoformat()
        # 分两个时段：09:30-10:00（开盘）和 10:00-15:30（盘中）
        ranges = [
            (d.strftime("%Y%m%d") + "093000", d.strftime("%Y%m%d") + "100000"),
            (d.strftime("%Y%m%d") + "100000", d.strftime("%Y%m%d") + "153000"),
        ]
        day_rows = 0
        for start_str, end_str in ranges:
            rows = _backfill_tick_range(symbols, start_str, end_str, d_str)
            day_rows += rows
        total_rows += day_rows
        log.info("  %s 完成: %d行", d_str, day_rows)

    return total_rows


def _backfill_tick_range(
    symbols: list[str],
    start_str: str,
    end_str: str,
    date_label: str,
) -> int:
    """补下载一个时间段的 tick 数据。"""
    from xtquant import xtdata

    batch_tsv: list[str] = []
    batch_count = 0
    total_rows = 0
    t0 = time.time()
    fail_count = 0

    for i, sc in enumerate(symbols):
        try:
            xtdata.download_history_data(sc, "tick", start_str, end_str)
            data = xtdata.get_market_data_ex([], [sc], "tick", start_str, end_str)
            df = data.get(sc) if data else None
            tsv_lines = _parse_tick_df(df, sc)

            if tsv_lines:
                batch_tsv.extend(tsv_lines)
                batch_count += 1

            if batch_count >= _BATCH_SYMBOLS:
                if _ch_insert_tsv(batch_tsv):
                    total_rows += len(batch_tsv)
                else:
                    fail_count += batch_count
                batch_tsv = []
                batch_count = 0

            if (i + 1) % 500 == 0:
                elapsed = time.time() - t0
                speed = (i + 1) / elapsed if elapsed > 0 else 0
                log.info(
                    "  %s %s-%s: 进度=%d/%d 行数=%d 失败=%d 速度=%.1f/s",
                    date_label,
                    start_str[8:],
                    end_str[8:],
                    i + 1,
                    len(symbols),
                    total_rows,
                    fail_count,
                    speed,
                )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            fail_count += 1
            if fail_count <= 3:
                log.warning("  %s 失败: %s", sc, e)

    # 最后一批
    if batch_tsv:
        if _ch_insert_tsv(batch_tsv):
            total_rows += len(batch_tsv)
        else:
            fail_count += batch_count

    return total_rows


# ========== 指数日K线（kline_index）补下载 ==========

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_INDEX_SYMBOLS_BY_DATE = "SELECT DISTINCT symbol FROM {table} WHERE trade_date=toDate('{d_str}')"


def _query_index_symbols(table: str, d: datetime.date) -> set[str]:
    """查询 kline_index 某日已有 symbol 集合。"""
    raw = ch_reader.query(_SQL_INDEX_SYMBOLS_BY_DATE.format(table=table, d_str=d.isoformat()))
    if not raw:
        return set()
    return {line.strip() for line in raw.strip().split("\n") if line.strip()}


def _detect_index_symbol_gap(
    table: str,
    dates: list[datetime.date],
    threshold: int,
) -> dict[datetime.date, list[str] | None]:
    """kline_index symbol 级缺口检测。

    表级行数检测（count < threshold）之外再做 symbol 级差集：
    基线 = 窗口内最后一个达标日（count >= threshold）的 symbol 集合；
    缺失日的缺口 = 基线 - 当日已有 symbol（sorted list）。
    窗口内无达标日（全缺失）时缺口记 None（调用方按全量清单补下载）。

    Returns:
        {缺失日期: 缺失 symbol 列表 或 None（全量）}；无缺失返回空 dict。
    """
    if not dates or threshold <= 0:
        return {}

    counts: dict[datetime.date, int] = {}
    for d in dates:
        cnt = ch_reader.query(
            _SQL_COUNT_BY_CUSTOM_DATE.format(table=table, date_col="trade_date", d_str=d.isoformat())
        )
        try:
            counts[d] = int(cnt.strip()) if cnt and cnt.strip() else 0
        except ValueError:
            counts[d] = 0

    baseline_date = None
    for d in dates:
        if counts[d] >= threshold:
            baseline_date = d  # 取最后一个达标日
    baseline = _query_index_symbols(table, baseline_date) if baseline_date else None

    gaps: dict[datetime.date, list[str] | None] = {}
    for d in dates:
        if counts[d] >= threshold:
            continue
        log.info("检测到缺失: %s %s 行数=%d 阈值=%d", table, d.isoformat(), counts[d], threshold)
        if baseline is None:
            gaps[d] = None
        else:
            gaps[d] = sorted(baseline - _query_index_symbols(table, d))
    return gaps


def _get_index_backfill_provider():
    """获取指数补下载 provider（akshare，新浪指数日线源）。

    复用既有指数采集能力，不重造：akshare `_fetch_kline_index` 支持显式
    [start, end] 窗口 + symbols 限定（tasks.yaml kline_index_incremental
    fallback 实证通道；miniqmt 近期持续拒连，akshare 为事实主通道）。
    """
    try:
        from zephyr.data.implementations.akshare_provider import AkshareIngestProvider

        provider = AkshareIngestProvider()
        provider.connect()
        return provider
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.error("akshare provider 不可用，无法补下载 kline_index: %s", e)
        return None


def backfill_kline_index(
    missing_dates: list[datetime.date],
    symbols: list[str] | None = None,
) -> int:
    """补下载 kline_index 指定缺失日期（显式窗口，绕开 last_key）。

    与 scheduler.run_task 增量重跑的本质区别：run_task 窗口下限 = last_key，
    last_key 只要 rows>0 即推进至 end（部分覆盖也超前推进），导致 last_key
    之前的部分覆盖日永远补不回；本函数以检测到的缺失日期为显式窗口
    [min(missing), max(missing)] 直接驱动 provider 回填，写幂等由
    kline_index ReplacingMergeTree 同键去重保证（D1DATA 实证）。

    Args:
        missing_dates: 缺失日期列表
        symbols: 缺失 symbol 限定（None=provider 全量指数清单）

    Returns:
        总写入行数
    """
    if not missing_dates:
        log.info("无需补下载 kline_index")
        return 0

    provider = _get_index_backfill_provider()
    if provider is None:
        return 0

    from zephyr.data.policy_registry import get_registry as _get_policy_registry
    from zephyr.data.provider_base import FetchPayload

    start, end = min(missing_dates), max(missing_dates)
    payload = FetchPayload(
        table=_TBL_KLINE_INDEX,
        symbols=symbols,
        start=start,
        end=end,
        incremental=True,
        extra={"capability": "kline_index"},
    )
    log.info(
        "补下载 kline_index: 窗口=[%s, %s] symbols=%s",
        start,
        end,
        "全量" if symbols is None else f"{len(symbols)}只",
    )

    policy = _get_policy_registry().get_policy("akshare")
    total_rows = 0
    try:
        for result in provider.fetch(payload, policy):
            if result.error:
                log.error("kline_index 补下载 FetchResult.error: %s", result.error)
                continue
            n = len(result.rows or [])
            if n and ch_writer.write_result(result):
                total_rows += n
            elif n:
                log.warning("kline_index 补下载批次写入失败（%d行）", n)
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.error("kline_index 补下载异常: %s", e)
    log.info("kline_index 补下载完成: %d行", total_rows)
    return total_rows


def _backfill_kline_index_table(
    info: dict,
    trade_dates: list[datetime.date],
    all_missing_tables: list[dict],
) -> int:
    """检测并补下载 kline_index 缺失日期（专用路径，替代 generic run_task）。

    缺失记录追加到 all_missing_tables，返回写入行数。
    """
    threshold = info.get("threshold", 0)
    if threshold <= 0:
        log.debug("表 %s 跳过（阈值为0）", info["table"])
        return 0

    gaps = _detect_index_symbol_gap(info["table"], trade_dates, threshold)
    if not gaps:
        log.debug("表 %s 无缺失", info["table"])
        return 0

    missing_dates = sorted(gaps)
    # symbols 并集；任一缺失日无基线（None）→ 全量清单
    if any(v is None for v in gaps.values()):
        symbols = None
    else:
        symbols = sorted({s for v in gaps.values() for s in v})

    log.info(
        "kline_index 缺失日期: %s 缺失标的: %s",
        [d.isoformat() for d in missing_dates],
        "全量" if symbols is None else f"{len(symbols)}只",
    )

    rows = 0
    if symbols is None or symbols:
        rows = backfill_kline_index(missing_dates, symbols=symbols)
    else:
        log.info("kline_index 缺失日 symbol 差集为空，无需补下载")

    all_missing_tables.append(
        {
            "table": info["table"],
            "missing_dates": [d.isoformat() for d in missing_dates],
            "rows_backfilled": rows,
        }
    )
    # 验证
    for d in missing_dates:
        d_str = d.isoformat()
        cnt = _ch_query(_SQL_COUNT_BY_DATE.format(table=info["table"], d_str=d_str))
        log.info("  kline_index %s: %s行", d_str, cnt or "0")
    return rows


# ========== 主入口 ==========


def _backfill_tick_table(
    trade_dates: list[datetime.date],
    all_missing_tables: list[dict],
) -> int:
    """补下载 tick_data 表缺失日期，返回新增行数。

    缺失日期对应的记录会被追加到 all_missing_tables。
    """
    missing = detect_missing_dates(_TBL_TICK_DATA, trade_dates, _TICK_THRESHOLD)
    if not missing:
        return 0
    log.info("tick_data 缺失日期: %s", [d.isoformat() for d in missing])
    rows = backfill_tick_data(missing)
    all_missing_tables.append(
        {
            "table": _TBL_TICK_DATA,
            "missing_dates": [d.isoformat() for d in missing],
            "rows_backfilled": rows,
        }
    )
    # 验证
    for d in missing:
        d_str = d.isoformat()
        cnt = _ch_query(_SQL_COUNT_BY_DATE.format(table=_TBL_TICK_DATA, d_str=d_str))
        log.info("  tick_data %s: %s行", d_str, cnt or "0")
    return rows


def _backfill_generic_table(
    info: dict,
    trade_dates: list[datetime.date],
    scheduler,
    all_missing_tables: list[dict],
) -> None:
    """检测并补下载通用表（非 tick_data）。缺失记录追加到 all_missing_tables。"""
    table = info["table"]
    date_col = info.get("date_column", "")
    threshold = info.get("threshold", 0)
    task_id = info.get("task_id", "")

    # 其他表用通用检测
    if not date_col or threshold <= 0:
        log.debug("表 %s 跳过（无日期列或阈值为0）", table)
        return

    missing = detect_missing_dates_generic(table, date_col, trade_dates, threshold)
    if not missing:
        log.debug("表 %s 无缺失", table)
        return

    log.info("表 %s 缺失日期: %s", table, [d.isoformat() for d in missing])
    all_missing_tables.append(
        {
            "table": table,
            "missing_dates": [d.isoformat() for d in missing],
            "rows_backfilled": 0,
        }
    )

    # 通过 scheduler 重跑任务补下载
    if scheduler is not None and task_id:
        log.info("通过 scheduler.run_task(%s) 补下载 %s", task_id, table)
        try:
            success = scheduler.run_task(task_id)
            if success:
                log.info("表 %s 补下载成功", table)
            else:
                log.warning("表 %s 补下载失败", table)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.error("表 %s 补下载异常: %s", table, e)


def _record_backfill_progress(
    scheduler,
    total_rows: int,
    all_missing_tables: list[dict],
) -> None:
    """记录补下载结果到 progress_store 并发送告警（scheduler 可用时）。"""
    if scheduler is None:
        return
    try:
        scheduler._progress_store.save_progress(
            "tick_backfill_weekly",
            "backfill",
            datetime.date.today().isoformat(),
            "SUCCESS" if total_rows > 0 or not all_missing_tables else "PARTIAL",
            total_rows,
        )
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass

    try:
        scheduler._alerter.notify(
            "tick_backfill_weekly",
            f"L10补下载完成: 缺失表={len(all_missing_tables)} 行数={total_rows}",
            level="INFO",
            source="backfill",
        )
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass


# ========== 已知缺口检测（audit 2.7/3.8 治本，#ARCH-CH-029） ==========

# 已知数据缺口注册表路径
_KNOWN_GAPS_PATH = os.path.join(os.path.dirname(__file__), "config", "known_data_gaps.yaml")

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，audit 2.7/3.8）
_SQL_GAP_DATE_RANGE_COUNTS = (
    "SELECT toDate({date_col}) as d, count() as cnt "
    "FROM {table} "
    "WHERE {date_col} >= toDate('{start}') "
    "AND {date_col} <= toDateTime('{end} 23:59:59') "
    "GROUP BY d ORDER BY d"
)
_SQL_GAP_TABLE_ROW_COUNT = "SELECT count() FROM {table}"


def _load_known_gaps() -> list[dict]:
    """加载已知数据缺口注册表（audit 2.7/3.8 治本）。

    Returns:
        已登记的缺口列表，每项含 id/table/gap_type/start_date/end_date/status 等。
        文件不存在或解析失败时返回空列表（降级为仅 7 天窗口检测）。
    """
    try:
        with open(_KNOWN_GAPS_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        gaps = data.get("gaps", []) if data else []
        log.info("已知缺口注册表加载: %d 条（%s）", len(gaps), _KNOWN_GAPS_PATH)
        return gaps
    except FileNotFoundError:
        log.debug("已知缺口注册表不存在: %s（仅使用 7 天窗口检测）", _KNOWN_GAPS_PATH)
        return []
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.warning("已知缺口注册表加载失败: %s", e)
        return []


def _check_date_range_gap(gap: dict, *, calendar: MarketCalendar | None = None) -> dict:
    """检测 date_range 类型缺口（指定日期范围内行数低于阈值）。

    Args:
        gap: 缺口字典，含 table/start_date/end_date/detection_threshold/date_column
        calendar: 市场日历注入（94号 §4.1/#261；None=ASHareCalendar 默认）

    Returns:
        检测结果 dict: {id, table, missing_dates, total_expected, total_actual, still_missing}
    """
    table = gap["table"]
    start = gap["start_date"]
    end = gap["end_date"]
    date_col = gap.get("date_column", "trade_date")
    threshold = gap.get("detection_threshold", _TICK_THRESHOLD)

    # 查询缺口范围内每个日期的行数
    sql = _SQL_GAP_DATE_RANGE_COUNTS.format(
        date_col=date_col,
        table=table,
        start=start,
        end=end,
    )
    raw = ch_reader.query(sql)
    date_counts: dict[str, int] = {}
    for line in raw.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) == 2:
            date_counts[parts[0]] = int(parts[1])

    # 生成缺口范围内的交易日列表（统一经日历包判定，消除 weekday 手工近似；
    # 缺日历数据时日历包内部降级 weekday——降级路径语义不变）
    from datetime import date as _date

    start_d = _date.fromisoformat(start)
    end_d = _date.fromisoformat(end) if end else _date.today()
    cal = calendar or _DEFAULT_CALENDAR
    all_dates: list[str] = [d.isoformat() for d in cal.trading_days_in_range(start_d, end_d)]

    missing_dates = [d for d in all_dates if date_counts.get(d, 0) < threshold]

    return {
        "id": gap["id"],
        "table": table,
        "missing_dates": missing_dates,
        "total_dates": len(all_dates),
        "still_missing": len(missing_dates),
    }


def _check_empty_table_gap(gap: dict) -> dict:
    """检测 empty_table 类型缺口（整表行数低于阈值）。

    Args:
        gap: 缺口字典，含 table/detection_threshold

    Returns:
        检测结果 dict: {id, table, row_count, still_empty}
    """
    table = gap["table"]
    threshold = gap.get("detection_threshold", 1)
    sql = _SQL_GAP_TABLE_ROW_COUNT.format(table=table)
    raw = ch_reader.query(sql)
    row_count = 0
    try:
        row_count = int(raw.strip())
    except (ValueError, TypeError):
        pass
    return {
        "id": gap["id"],
        "table": table,
        "row_count": row_count,
        "still_empty": row_count < threshold,
    }


def run_known_gap_backfill(scheduler=None, *, calendar: MarketCalendar | None = None) -> dict:
    """检测并补下载已知数据缺口（audit 2.7/3.8 治本，#ARCH-CH-029）。

    与 run_weekend_backfill（7天窗口）互补：
    - run_weekend_backfill: 检测最近 7 天的增量缺口
    - run_known_gap_backfill: 检测已登记的历史缺口（不受 7 天窗口限制）

    Args:
        scheduler: IntegratorScheduler 实例（可选）
        calendar: 市场日历注入（94号 §4.1/#261；None=ASHareCalendar 默认）

    流程：
    1. 加载 known_data_gaps.yaml
    2. 过滤出 status != "completed" 的缺口
    3. 对 date_range 缺口: 检测仍缺失的日期 → 触发 backfill_tick_data()
    4. 对 empty_table 缺口: 检测表行数 → log 告警（不自动 backfill，需人工介入）
    5. backfill 成功的缺口标记 status=completed（需人工确认后更新 YAML）

    Returns:
        {"checked": int, "still_missing": int, "backfilled_rows": int, "details": [...]}
    """
    gaps = _load_known_gaps()
    active_gaps = [g for g in gaps if g.get("status") != "completed"]
    if not active_gaps:
        log.info("已知缺口注册表: 无活跃缺口（全部 completed 或为空）")
        return {"checked": 0, "still_missing": 0, "backfilled_rows": 0, "details": []}

    log.info("=" * 60)
    log.info("已知缺口检测开始 (%d 条活跃缺口)", len(active_gaps))
    log.info("=" * 60)

    details: list[dict] = []
    total_backfilled = 0
    still_missing_count = 0

    for gap in active_gaps:
        gap_type = gap.get("gap_type", "")
        gap_id = gap.get("id", "unknown")

        if gap_type == "date_range":
            result = _check_date_range_gap(gap, calendar=calendar)
            details.append(result)
            if result["still_missing"] > 0:
                still_missing_count += result["still_missing"]
                log.warning(
                    "缺口 %s: %s 仍有 %d/%d 天缺失",
                    gap_id,
                    result["table"],
                    result["still_missing"],
                    result["total_dates"],
                )
                # 对 tick_data 缺口触发 backfill
                if result["table"] == _TBL_TICK_DATA:
                    from datetime import date as _date

                    missing_d = [_date.fromisoformat(d) for d in result["missing_dates"]]
                    if missing_d:
                        log.info("触发 tick_data 补下载: %d 天", len(missing_d))
                        rows = backfill_tick_data(missing_d)
                        total_backfilled += rows
            else:
                log.info("缺口 %s: %s 已补全", gap_id, result["table"])

        elif gap_type == "empty_table":
            result = _check_empty_table_gap(gap)
            details.append(result)
            if result["still_empty"]:
                still_missing_count += 1
                log.warning(
                    "缺口 %s: %s 仍为空 (行数=%d)——%s",
                    gap_id,
                    result["table"],
                    result["row_count"],
                    gap.get("resolution_plan", "需人工介入"),
                )
            else:
                log.info("缺口 %s: %s 已有数据 (行数=%d)", gap_id, result["table"], result["row_count"])

    log.info("=" * 60)
    log.info("已知缺口检测完成: 仍缺失=%d 补下载行数=%d", still_missing_count, total_backfilled)
    log.info("=" * 60)

    return {
        "checked": len(active_gaps),
        "still_missing": still_missing_count,
        "backfilled_rows": total_backfilled,
        "details": details,
    }


def run_weekend_backfill(
    scheduler=None,
    days: int = _DEFAULT_BACKFILL_DAYS,
    skip_known_gaps: bool = False,
    *,
    calendar: MarketCalendar | None = None,
) -> dict:
    """L10 周末补下载主入口（全表覆盖）。

    流程：
    1. 获取过去N天的交易日列表
    2. 动态发现所有表（从 tasks.yaml 自动读取，新增表自动纳入）
    3. 逐表检测缺失日期
    4. tick_data 用专门的 backfill_tick_data() 补下载
    5. 其他表用 scheduler.run_task(task_id) 重跑
    6. 记录结果到 progress_store（如果 scheduler 可用）

    Args:
        scheduler: IntegratorScheduler 实例（可选，用于记录进度和告警）
        days: 回溯天数（默认7天）
        skip_known_gaps: 跳过已知历史缺口检测（每日调用时设True，避免重复检查）
        calendar: 市场日历注入（94号 §4.1/#261；None=ASHareCalendar 默认，零行为变化）

    Returns:
        {"missing_tables": [...], "total_rows": int, "success": bool}
    """
    log.info("=" * 60)
    log.info("L10 周末补下载开始 (回溯%d天, 全表覆盖)", days)
    log.info("=" * 60)

    # 1. 获取交易日
    trade_dates = get_trade_dates(days, calendar=calendar)
    if not trade_dates:
        log.error("无法获取交易日列表，退出")
        return {"missing_tables": [], "total_rows": 0, "success": False}
    log.info("过去%d天交易日: %s", days, [d.isoformat() for d in trade_dates])

    # 2. 动态发现所有表
    tables_info = _discover_backfill_tables()
    log.info("动态发现 %d 张表需要检测", len(tables_info))

    # 3. 逐表检测缺失并补下载
    all_missing_tables = []
    total_rows = 0

    for info in tables_info:
        table = info["table"]
        # tick_data 用专门的补下载逻辑（分时段+批量写入）
        if table == _TBL_TICK_DATA:
            total_rows += _backfill_tick_table(trade_dates, all_missing_tables)
            continue
        # kline_index 用专用路径（symbol 级差集 + 显式缺失日期窗口经 akshare
        # provider 回填），绕开 run_task 增量窗口下限=last_key 导致的
        # "部分覆盖日补不回"缺口（2026-08-24 D1）
        if table == _TBL_KLINE_INDEX:
            total_rows += _backfill_kline_index_table(info, trade_dates, all_missing_tables)
            continue
        _backfill_generic_table(info, trade_dates, scheduler, all_missing_tables)

    # 4. 记录到 progress_store（如果 scheduler 可用）
    _record_backfill_progress(scheduler, total_rows, all_missing_tables)

    log.info("=" * 60)
    log.info("L10 周末补下载完成: 缺失表=%d 总行数=%d", len(all_missing_tables), total_rows)
    log.info("=" * 60)

    # 5. 检测已知历史缺口（audit 2.7/3.8 治本，#ARCH-CH-029）
    #    与 7 天窗口互补：7 天窗口检测增量缺口，known_gap 检测已登记历史缺口
    #    每日调用时跳过（skip_known_gaps=True），历史缺口由周末 L10 负责
    if skip_known_gaps:
        known_result = {"checked": 0, "still_missing": 0, "backfilled_rows": 0, "details": []}
    else:
        known_result = run_known_gap_backfill(scheduler, calendar=calendar)
    total_rows += known_result.get("backfilled_rows", 0)

    return {
        "missing_tables": all_missing_tables,
        "total_rows": total_rows,
        "success": True,
        "known_gaps": known_result,
    }


def run_daily_backfill(scheduler=None) -> dict:
    """L10.5 每日盘后补下载主入口（检测当日缺口并补下载）。

    治本场景（2026-07-30，#ARCH-DATA-TICK-GAP-001）：
      - 7-29 QMT 客户端 15:31 断连 → intraday_realtime tick 采集停止
      - 7-29 仅 4.2M 行（正常 ~20M），7-30 0 行
      - L11 integrity_check 23:00 检测到但只告警，不补下载
      - L10 weekend_backfill 仅周一 02:00 运行 → 要等 5 天才发现
      - 本函数每日盘后 17:00 运行 → 当天发现当天补

    与 run_weekend_backfill 的区别：
      - days=1: 只检测今天，不回溯 7 天
      - skip_known_gaps=True: 跳过历史缺口检测（由周末 L10 负责）
      - 轻量级：正常情况下无缺口，几秒完成；有缺口才触发补下载

    调用方式：
      scheduler.run_schedule("daily_backfill") → run_daily_backfill(scheduler)
      也可独立调用：python -c "from zephyr.data.backfill_checker import run_daily_backfill; run_daily_backfill()"
    """
    log.info("=" * 60)
    log.info("L10.5 每日盘后补下载开始 (检测当日, 治本 #ARCH-DATA-TICK-GAP-001)")
    log.info("=" * 60)

    result = run_weekend_backfill(scheduler, days=1, skip_known_gaps=True)

    log.info("=" * 60)
    log.info(
        "L10.5 每日盘后补下载完成: 缺失表=%d 总行数=%d",
        len(result.get("missing_tables", [])),
        result.get("total_rows", 0),
    )
    log.info("=" * 60)

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_weekend_backfill()
