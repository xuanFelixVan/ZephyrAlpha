# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.ch_reader
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer
# [CONSUMERS] zephyr.data.backfill_checker; zephyr.backtest.core.data_handler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 对 ReplacingMergeTree 表自动注入 FINAL 关键字; 不执行写入操作; 纯读取层
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] query失败->返回空字符串(同ch_writer); count失败->返回0; inject_final纯函数不抛异常
# [TESTS]
# [A_module] module_id=MOD-L00-004-ch_reader | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ClickHouse 统一读取层（裁定 #ARCH-CH-007）。

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
"""
from __future__ import annotations

import logging
import re

from zephyr.data import ch_writer

log = logging.getLogger(__name__)

# FROM 子句表名匹配模式
# 支持: FROM table, FROM db.table, FROM `table`, FROM `db`.`table`
_FROM_PATTERN = re.compile(
    r'\bFROM\s+`?(?P<table>\w+(?:\.\w+)?)`?',
    re.IGNORECASE
)

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
    if re.search(r'\bFINAL\b', sql, re.IGNORECASE):
        return sql

    def _replace(match: re.Match) -> str:
        table = match.group("table")
        # 跳过 system.* 表
        if table.startswith("system."):
            return match.group(0)
        try:
            if ch_writer.is_replacing_engine(table):
                return f"FROM {table} FINAL"
        except Exception:
            pass  # 引擎查询失败则不注入
        return match.group(0)

    return _FROM_PATTERN.sub(_replace, sql)


def query(sql: str, timeout: int = ch_writer._DEFAULT_TIMEOUT) -> str:
    """执行查询，自动对 ReplacingMergeTree 表注入 FINAL。

    基于 ch_writer.query()，返回 TSV 格式字符串。
    失败时返回空字符串（同 ch_writer.query()）。

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
    """
    final = ""
    try:
        if ch_writer.is_replacing_engine(table):
            final = " FINAL"
    except Exception:
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
    except Exception:
        pass
    sql = _SQL_SELECT.format(columns=columns, table=table, final=final)
    if where:
        sql += f" WHERE {where}"
    if order_by:
        sql += f" ORDER BY {order_by}"
    if limit > 0:
        sql += f" LIMIT {limit}"
    return ch_writer.query(sql, timeout=timeout)
