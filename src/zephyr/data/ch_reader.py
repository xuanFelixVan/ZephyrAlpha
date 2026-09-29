# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.ch_reader
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer
# [CONSUMERS] zephyr.data.backfill_checker; zephyr.backtest.core.data_handler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 对 ReplacingMergeTree 表自动注入 FINAL 关键字; 不执行写入操作; 纯读取层; 严格读通道（query_rows/count_strict/inject_final_strict）失败必抛且仅允许只读语句
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] query失败->返回空字符串(同ch_writer，**判据类读数禁用**，改走 query_rows); count失败->返回0(**判据类读数禁用**，改走 count_strict); inject_final纯函数不抛异常; inject_final_strict/query_rows/count_strict失败->raise ch_writer.ClickHouseQueryError（W-180.1）
# [TESTS]
# [A_module] module_id=MOD-GOV-ch_reader | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ClickHouse 统一读取层（裁定 #ARCH-CH-007）。

对 ReplacingMergeTree 表自动注入 FINAL 关键字，
保证查询返回去重后的数据。

背景：裁定 #ARCH-CH-002 统一使用 ReplacingMergeTree + 直接 INSERT，
但 ReplacingMergeTree 的去重是异步的（后台 merge 时才去重）。
在 merge 完成前，查询会返回重复行。
查询时加 FINAL 关键字可强制去重。

100% AI 开发模式下，AI 不会主动在查询中加 FINAL（裁定 #ARCH-CH-004 教训），
本模块通过统一查询层自动注入，消除对 AI 自觉的依赖。

公共接口：
- inject_final(sql): 纯函数，对 SQL 中的 ReplacingMergeTree 表注入 FINAL
- query(sql): 执行查询（自动注入 FINAL），返回 TSV 字符串
- count(table, where): 计数查询（自动注入 FINAL），返回 int
- query_table(table, columns, where, ...): 便捷表查询

严格读通道（W-180.1，判据类读数唯一合法入口）：
- query_rows(sql): 返回 list[tuple] 行集；传输/引擎探测失败 ⇒ raise ClickHouseQueryError
- count_strict(table, where): 返回 int；失败必抛，"真 0 行"与"查询失败"两态可分
- inject_final_strict(sql): 同 inject_final，但引擎探测失败必抛
  （FINAL 缺失会让 ReplacingMergeTree 计数虚高，判据读数不能吞这个错）

⚠ 为什么两套并存（终审卷 §7.2 病根）：`query()` 返回的是 **TSV 字符串**，
`query(x)[0][0]` 取到的是"首行的首字符"、`for r in query(x)` 迭代的是**字符**——
2026-09-26 审计员自己踩出"467→4、729→7、128→1"的首位数字假象；且失败时返回 `""`
与真空不可分。存量 12+ 正确消费者（变量名多叫 `tsv`）零迁移成本，故**不改旧行为**，
新读数一律走严格通道（红线：判据类读数 query_rows / count_strict / ch_probe 三选一）。

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/ch_reader.yaml
"""

from __future__ import annotations

import logging
import re

from zephyr.data import ch_writer

log = logging.getLogger(__name__)

# FROM 子句表名匹配模式
# 支持: FROM table, FROM db.table, FROM `table`, FROM `db`.`table`
_FROM_PATTERN = re.compile(r"\bFROM\s+`?(?P<table>\w+(?:\.\w+)?)`?", re.IGNORECASE)

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_COUNT = "SELECT count() FROM {table}{final}"
_SQL_SELECT = "SELECT {columns} FROM {table}{final}"


def inject_final(sql: str) -> str:
    """对 SQL 中的 ReplacingMergeTree 表自动注入 FINAL 关键字。

    纯函数，不执行查询，不抛异常。

    规则：
    - 检测 FROM 子句中的表名
    - 对 ReplacingMergeTree 引擎的表，在表名后插入 FINAL
    - 已有 FINAL 的 SQL 不重复注入
    - system.* 表不注入（系统表不是 ReplacingMergeTree）
    - 引擎查询失败不注入（降级为普通查询）

    Args:
        sql: SQL 查询语句

    Returns:
        可能注入了 FINAL 的 SQL 语句
    """
    # 已有 FINAL 则跳过
    if re.search(r"\bFINAL\b", sql, re.IGNORECASE):
        return sql

    def _replace(match: re.Match) -> str:
        table = match.group("table")
        # 跳过 system.* 表
        if table.startswith("system."):
            return match.group(0)
        try:
            if ch_writer.is_replacing_engine(table):
                return f"FROM {table} FINAL"
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            pass  # 引擎查询失败则不注入
        return match.group(0)

    return _FROM_PATTERN.sub(_replace, sql)


def query(sql: str, timeout: int = ch_writer._DEFAULT_TIMEOUT) -> str:
    """执行查询，自动对 ReplacingMergeTree 表注入 FINAL。

    基于 ch_writer.query()，返回 TSV 格式字符串。
    失败时返回空字符串（同 ch_writer.query()）。

    ⚠⚠ 高危契约（W-180.1）：返回 **str 不是行集**——
      `query(sql)[0][0]` ＝ 首行首字符（"467" 读成 "4"）；
      `for r in query(sql)` ＝ 逐字符迭代；
      返回 `""` 既可能是"查询失败"也可能是"零行"，两态不可分。
    判据类读数（清单/尺/案卷/呈裁证据）**禁用本函数**，改走 `query_rows()` 或 `ch_probe.py`。
    本函数行为按内收原则保持不动（存量 12+ 消费者零迁移）。

    Args:
        sql: SQL 查询语句
        timeout: 超时秒数

    Returns:
        TSV 格式字符串
    """
    sql = inject_final(sql)
    return ch_writer.query(sql, timeout=timeout)


def count(table: str, where: str = "", timeout: int = 30) -> int:
    """计数查询，自动注入 FINAL。

    对 ReplacingMergeTree 表，执行 SELECT count() FROM table FINAL，
    保证计数不含重复行。

    Args:
        table: 表名（如 "c1_market.kline_daily"）
        where: WHERE 条件（如 "trade_date = '2026-07-14'"），可选
        timeout: 超时秒数

    Returns:
        行数。查询失败返回 0。

    ⚠ 高危契约（W-180.1）：失败态＝0 与"真 0 行"不可分 ⇒ 判据类计数（空壳表清单/
      新鲜度尺/对账表/呈裁证据）禁用本函数，改走 `count_strict()`（失败必抛）。
    """
    final = ""
    try:
        if ch_writer.is_replacing_engine(table):
            final = " FINAL"
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass
    sql = _SQL_COUNT.format(table=table, final=final)
    if where:
        sql += f" WHERE {where}"
    result = ch_writer.query(sql, timeout=timeout)
    try:
        return int(result.strip() or 0)
    except ValueError:
        log.warning("count(%s) 返回非数字: %s", table, result[:100])
        return 0


def query_table(
    table: str,
    columns: str = "*",
    where: str = "",
    order_by: str = "",
    limit: int = 0,
    timeout: int = ch_writer._DEFAULT_TIMEOUT,
) -> str:
    """便捷表查询，自动注入 FINAL。

    Args:
        table: 表名（如 "c1_market.kline_daily"）
        columns: 列名（如 "date, symbol, close"），默认 "*"
        where: WHERE 条件，可选
        order_by: ORDER BY 子句，可选
        limit: LIMIT 行数，0 表示不限
        timeout: 超时秒数

    Returns:
        TSV 格式字符串
    """
    final = ""
    try:
        if ch_writer.is_replacing_engine(table):
            final = " FINAL"
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass
    sql = _SQL_SELECT.format(columns=columns, table=table, final=final)
    if where:
        sql += f" WHERE {where}"
    if order_by:
        sql += f" ORDER BY {order_by}"
    if limit > 0:
        sql += f" LIMIT {limit}"
    return ch_writer.query(sql, timeout=timeout)


# ---------------------------------------------------------------------------
# W-180.1 严格读通道（判据类读数唯一合法入口）
# 契约：失败必抛、禁把异常吞成空值/空表；"真空 0 行"与"查询失败"两态显式可分。
# 内收：复用 ch_writer 传输层与自愈钩子，不新建连接层；不改 query()/count() 存量行为。
# ---------------------------------------------------------------------------

#: 严格读异常（从 ch_writer 转发，让调用方 `from zephyr.data.ch_reader import ClickHouseQueryError`）
ClickHouseQueryError = ch_writer.ClickHouseQueryError


def _final_suffix_strict(table: str) -> str:
    """引擎探测 + FINAL 后缀；探测失败必抛（FINAL 缺失会让 ReplacingMergeTree 计数虚高）。"""
    try:
        replacing = ch_writer.is_replacing_engine(table)
    except Exception as e:  # noqa: BLE001 — 契约要求转严格异常
        raise ClickHouseQueryError(f"<engine-probe {table}>", [("engine_probe", f"{type(e).__name__}: {e}")]) from e
    return " FINAL" if replacing else ""


def inject_final_strict(sql: str) -> str:
    """`inject_final` 的严格版：引擎探测失败 ⇒ raise，而不是静默降级为非 FINAL 查询。"""
    if re.search(r"\bFINAL\b", sql, re.IGNORECASE):
        return sql

    def _replace(match: re.Match) -> str:
        table = match.group("table")
        if table.startswith("system."):
            return match.group(0)
        if _final_suffix_strict(table):
            return f"FROM {table} FINAL"
        return match.group(0)

    return _FROM_PATTERN.sub(_replace, sql)


def query_rows(sql: str, timeout: int = ch_writer._DEFAULT_TIMEOUT) -> list[tuple]:
    """严格行集读：返回 `list[tuple]`，失败必抛 `ClickHouseQueryError`。

    与 `query()` 的关系＝同一传输层、两套错误契约（存量消费者零迁移）：
      - `query()`  失败 → `""`（与真空不可分，判据类读数禁用）
      - `query_rows()` 失败 → raise；真空 → `[]`

    ReplacingMergeTree 表仍自动注入 FINAL（走严格版引擎探测，探测失败即抛）。
    """
    return ch_writer.query_strict(inject_final_strict(sql), timeout=timeout)


def count_strict(table: str, where: str = "", timeout: int = 30) -> int:
    """严格计数：查询失败/结果形状异常必抛，返回 int（真 0 行＝确证的空表）。

    `count()` 的失败态是 0，会被下游当"空壳表"证据（W-34 清单污染风险）；
    本函数把失败与真空分成两态，调用方必须显式处理异常。
    """
    sql = _SQL_COUNT.format(table=table, final=_final_suffix_strict(table))
    if where:
        sql += f" WHERE {where}"
    rows = ch_writer.query_strict(sql, timeout=timeout)
    if len(rows) != 1 or len(rows[0]) != 1:
        raise ClickHouseQueryError(sql, [("shape", f"count 期望 1x1，实得 {len(rows)}x{len(rows[0]) if rows else 0}")])
    try:
        return int(str(rows[0][0]).strip())
    except ValueError as e:
        raise ClickHouseQueryError(sql, [("shape", f"count 返回非整数: {rows[0][0]!r}")]) from e


def query_rows_table(
    table: str,
    columns: str = "*",
    where: str = "",
    order_by: str = "",
    limit: int = 0,
    timeout: int = ch_writer._DEFAULT_TIMEOUT,
) -> list[tuple]:
    """`query_table` 的严格版（同样必抛），判据类逐行读数用。"""
    sql = _SQL_SELECT.format(columns=columns, table=table, final=_final_suffix_strict(table))
    if where:
        sql += f" WHERE {where}"
    if order_by:
        sql += f" ORDER BY {order_by}"
    if limit > 0:
        sql += f" LIMIT {limit}"
    return ch_writer.query_strict(sql, timeout=timeout)
