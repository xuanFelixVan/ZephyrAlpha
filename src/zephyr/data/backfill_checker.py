# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.backfill_checker
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.tick_subscriber
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 查CH实际行数发现缺口; 只补缺失不重复下载; 写入tick_data走ch_writer统一通道(TCP→HTTP→本地落盘); 查询走ch_reader自动注入FINAL
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH查询失败->返回None; CH写入失败->重试3次后返回False; xtquant不可用->返回0
# [TESTS]
# [A_module] module_id=MOD-L00-004-backfill_checker | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
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
import time
from pathlib import Path
from time import sleep

import yaml

from zephyr.data import ch_reader
from zephyr.data import ch_writer
from zephyr.data.tick_subscriber import _safe_int

log = logging.getLogger(__name__)

# ========== 常量 ==========

# tick_data 缺失阈值：每天低于此值视为缺失（正常约2000万行/天）
_TICK_THRESHOLD = 5_000_000

# 补下载默认天数
_DEFAULT_BACKFILL_DAYS = 7

# 每批写入 ClickHouse 的标的数
_BATCH_SYMBOLS = 50

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_TRADE_CALENDAR = (
    "SELECT cal_date FROM c1_market.trade_calendar "
    "WHERE cal_date >= toDate('{start}') AND cal_date <= toDate('{today}') "
    "AND is_open = 1 ORDER BY cal_date"
)
_SQL_KLINE_DISTINCT = (
    "SELECT DISTINCT trade_date FROM c1_market.kline_daily "
    "WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{today}') "
    "ORDER BY trade_date"
)
_SQL_COUNT_BY_DATE = (
    "SELECT count() FROM c1_market.{table} "
    "WHERE trade_date=toDate('{d_str}')"
)

# tick_data 表写入列子句（用于 ch_writer.write_tsv）
_TICK_DATA_COLS = (
    "(trade_date,timestamp,symbol,market_type,price,volume,amount,"
    "direction,data_source,bid_price,ask_price,bid_volume,ask_volume)"
)
_TICK_DATA_TABLE = "c1_market.tick_data"


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
                _TICK_DATA_TABLE, _TICK_DATA_COLS, tsv_bytes, timeout=120,
            )
            if ok:
                return True
            log.warning("CH写入失败(%d/%d)", i + 1, retries)
        except Exception as e:
            log.warning("CH写入异常(%d/%d): %s", i + 1, retries, e)
        sleep(2)
    return False


# ========== 交易日历 ==========

def get_trade_dates(days: int = 7) -> list[datetime.date]:
    """获取过去N天的交易日列表（从 trade_calendar 表查 is_open=1）。

    Fallback: 如果 trade_calendar 无数据，用 kline_daily 中有数据的日期。
    """
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
            log.error("无法获取交易日列表")
            return []

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
    table: str, dates: list[datetime.date], threshold: int,
) -> list[datetime.date]:
    """检测指定表在哪些日期的数据行数低于阈值。

    Args:
        table: 表名（如 tick_data, kline_daily）
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
    "trade_date", "end_date", "report_date", "unlock_date",
    "announce_date", "date", "fdate",
]

# SQL 模板（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_DESCRIBE = "DESCRIBE TABLE {table}"
_SQL_AVG_ROWS_7D = (
    "SELECT avg(cnt) FROM ("
    "SELECT count() AS cnt FROM {table} "
    "WHERE {date_col} >= toDate(today() - 7) "
    "AND {date_col} < today() "
    "GROUP BY {date_col})"
)
_SQL_COUNT_BY_CUSTOM_DATE = (
    "SELECT count() FROM {table} WHERE {date_col}=toDate('{d_str}')"
)


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
    if avg <= 0:
        return 0
    return int(avg * 0.5)


def _discover_backfill_tables() -> list[dict]:
    """从 tasks.yaml 动态发现所有需要补下载的表。

    新增表只需在 tasks.yaml 注册任务，即可自动纳入补下载覆盖范围。
    同表多任务去重，取第一个非 disabled 任务。

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
            }
    # 推断日期列和阈值
    for info in tables.values():
        info["date_column"] = _infer_date_column(info["table"])
        info["threshold"] = _infer_threshold(info["table"], info["date_column"])
    return list(tables.values())


def detect_missing_dates_generic(
    table: str, date_col: str, dates: list[datetime.date], threshold: int,
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
        cnt = ch_reader.query(
            _SQL_COUNT_BY_CUSTOM_DATE.format(table=table, date_col=date_col, d_str=d_str)
        )
        try:
            count = int(cnt.strip()) if cnt and cnt.strip() else 0
        except ValueError:
            count = 0
        if count < threshold:
            log.info("检测到缺失: %s[%s] %s 行数=%d 阈值=%d",
                     table, date_col, d_str, count, threshold)
            missing.append(d)
    return missing


# ========== Tick 数据解析 ==========

def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        f = float(val)
        return f if f == f and f != 0 else None  # 过滤 NaN 和 0
    except Exception:
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

        tsv_lines.append("\t".join([
            trade_date, timestamp_str, symbol, market_type,
            str(price) if price is not None else "\\N",
            str(vol) if vol is not None else "\\N",
            str(amt) if amt is not None else "\\N",
            "", "miniqmt",
            str(bid_price) if bid_price is not None else "\\N",
            str(ask_price) if ask_price is not None else "\\N",
            str(bid_vol) if bid_vol is not None else "\\N",
            str(ask_vol) if ask_vol is not None else "\\N",
        ]))
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
    symbols: list[str], start_str: str, end_str: str, date_label: str,
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
                    date_label, start_str[8:], end_str[8:],
                    i + 1, len(symbols), total_rows, fail_count, speed,
                )
        except Exception as e:
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


# ========== 主入口 ==========

def _backfill_tick_table(
    trade_dates: list[datetime.date], all_missing_tables: list[dict],
) -> int:
    """补下载 tick_data 表缺失日期，返回新增行数。

    缺失日期对应的记录会被追加到 all_missing_tables。
    """
    missing = detect_missing_dates("tick_data", trade_dates, _TICK_THRESHOLD)
    if not missing:
        return 0
    log.info("tick_data 缺失日期: %s", [d.isoformat() for d in missing])
    rows = backfill_tick_data(missing)
    all_missing_tables.append({
        "table": "tick_data",
        "missing_dates": [d.isoformat() for d in missing],
        "rows_backfilled": rows,
    })
    # 验证
    for d in missing:
        d_str = d.isoformat()
        cnt = _ch_query(_SQL_COUNT_BY_DATE.format(table="tick_data", d_str=d_str))
        log.info("  tick_data %s: %s行", d_str, cnt or "0")
    return rows


def _backfill_generic_table(
    info: dict, trade_dates: list[datetime.date], scheduler,
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
    all_missing_tables.append({
        "table": table,
        "missing_dates": [d.isoformat() for d in missing],
        "rows_backfilled": 0,
    })

    # 通过 scheduler 重跑任务补下载
    if scheduler is not None and task_id:
        log.info("通过 scheduler.run_task(%s) 补下载 %s", task_id, table)
        try:
            success = scheduler.run_task(task_id)
            if success:
                log.info("表 %s 补下载成功", table)
            else:
                log.warning("表 %s 补下载失败", table)
        except Exception as e:
            log.error("表 %s 补下载异常: %s", table, e)


def _record_backfill_progress(
    scheduler, total_rows: int, all_missing_tables: list[dict],
) -> None:
    """记录补下载结果到 progress_store 并发送告警（scheduler 可用时）。"""
    if scheduler is None:
        return
    try:
        scheduler._progress_store.save_progress(
            "tick_backfill_weekly", "backfill",
            datetime.date.today().isoformat(),
            "SUCCESS" if total_rows > 0 or not all_missing_tables else "PARTIAL",
            total_rows,
        )
    except Exception:
        pass

    try:
        scheduler._alerter.notify(
            "tick_backfill_weekly",
            f"L10补下载完成: 缺失表={len(all_missing_tables)} 行数={total_rows}",
            level="INFO",
            source="backfill",
        )
    except Exception:
        pass


def run_weekend_backfill(scheduler=None, days: int = _DEFAULT_BACKFILL_DAYS) -> dict:
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

    Returns:
        {"missing_tables": [...], "total_rows": int, "success": bool}
    """
    log.info("=" * 60)
    log.info("L10 周末补下载开始 (回溯%d天, 全表覆盖)", days)
    log.info("=" * 60)

    # 1. 获取交易日
    trade_dates = get_trade_dates(days)
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
        if table == "tick_data" or table.endswith(".tick_data"):
            total_rows += _backfill_tick_table(trade_dates, all_missing_tables)
            continue
        _backfill_generic_table(info, trade_dates, scheduler, all_missing_tables)

    # 4. 记录到 progress_store（如果 scheduler 可用）
    _record_backfill_progress(scheduler, total_rows, all_missing_tables)

    log.info("=" * 60)
    log.info("L10 周末补下载完成: 缺失表=%d 总行数=%d", len(all_missing_tables), total_rows)
    log.info("=" * 60)

    return {
        "missing_tables": all_missing_tables,
        "total_rows": total_rows,
        "success": True,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_weekend_backfill()
