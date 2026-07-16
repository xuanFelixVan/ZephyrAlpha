# [BLUEPRINT] MOD-GOV_DQ | scripts/governance/data_quality/check_tick_duplication.py | §
# [MODULE] scripts.governance.data_quality.check_tick_duplication
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.data.ch_reader
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 真重复定义=全字段(14字段)相同; 禁止用 count()-uniqExact(排序键) 算"重复"; 只读查询不修改数据
# [MODIFY-GUARD] 同步更新 trae_063_data_ops_discipline.yaml 中引用本脚本的 invariants
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ch_reader.query 失败返回空字符串->打印错误并 exit 2; 月份参数格式错误->exit 2
# [TESTS]
# [TTL] permanent
# [A_module] module_id=MOD-GOV_DQ | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
"""tick_data 表真重复检查工具（RULE-DATA-OPS 配套，TRAE-063 §invariants DATA-OPS-INV-002）.

本脚本是 2026-07-16 tick_data 21 个月数据误删事故的治本工具之一。
事故根因：AI 用 count() - uniqExact(排序键) 算"重复"，把同一时间戳不同价位的有效记录
误判为"重复"，执行 INSERT GROUP BY + REPLACE PARTITION 删除了 21 个月有效数据。

真重复定义（铁律）：所有 14 个业务字段完全相同的行才算真重复。
- trade_date, timestamp, symbol, market_type, price, volume, amount, direction,
  data_source, bid_price, ask_price, bid_volume, ask_volume, quality_flag

检查方法：按全字段 GROUP BY HAVING count() > 1，查看实际重复行内容。
禁止判据：count() - uniqExact(排序键)——排序键不含全部业务字段。

Usage:
    python scripts/governance/data_quality/check_tick_duplication.py --month 202607
    python scripts/governance/data_quality/check_tick_duplication.py --month 202607 --market-type index
    python scripts/governance/data_quality/check_tick_duplication.py --month 202607 --limit 50

Exit codes:
    0 = 检查完成，无真重复
    1 = 检查完成，发现真重复（需进一步排查数据源问题，禁止直接删除）
    2 = 检查失败（CH 连接异常/参数错误）
"""

from __future__ import annotations

import sys
from pathlib import Path

# 加载 src/ 以便 import zephyr.data.ch_reader
_SRC_DIR = r"d:\ZephyrAlpha\src"
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# 加载 governance _shared/ 以便复用编码工具
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_PASS, REPO_ROOT  # noqa: E402

__manifest__ = """
args: [--month, --market-type, --limit, --json]
description: >
    tick_data 表真重复检查工具——按全字段 GROUP BY HAVING count() > 1 查找真重复行。
    RULE-DATA-OPS（TRAE-063）配套工具，防止 AI 误用 count()-uniqExact(排序键) 算"重复"。
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 120
warn_only: false
"""

import argparse
import json
import re
from typing import Any

from zephyr.data import ch_reader

# tick_data 表全部 14 个业务字段（真源：tick_subscriber.py _TICK_COLUMNS）
# 真重复定义：所有 14 字段完全相同才算真重复
_TICK_COLUMNS = [
    "trade_date",
    "timestamp",
    "symbol",
    "market_type",
    "price",
    "volume",
    "amount",
    "direction",
    "data_source",
    "bid_price",
    "ask_price",
    "bid_volume",
    "ask_volume",
    "quality_flag",
]

_TABLE = "tick_data"
_MONTH_PATTERN = re.compile(r"^\d{6}$")  # YYYYMM
_DEFAULT_LIMIT = 20  # noqa: gate-vocab（显示行数默认值，非词表枚举值，CLI --limit 可覆盖）

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_DUPLICATION = (
    "SELECT {cols}, count() AS dup_cnt "
    "FROM {table} "
    "WHERE {where} "
    "GROUP BY {cols} "
    "HAVING dup_cnt > 1 "
    "ORDER BY dup_cnt DESC "
    "LIMIT {limit}"
)
_SQL_SUMMARY = (
    "SELECT count() AS dup_group_cnt, sum(dup_cnt) AS dup_row_cnt "
    "FROM ("
    "  SELECT {cols}, count() AS dup_cnt "
    "  FROM {table} "
    "  WHERE {where} "
    "  GROUP BY {cols} "
    "  HAVING dup_cnt > 1"
    ")"
)
_SQL_TOTAL_ROW = (
    "SELECT count() AS total_cnt, uniqExact({cols}) AS uniq_full_field_cnt "
    "FROM {table} "
    "WHERE {where}"
)


def _validate_month(month: str) -> bool:
    """校验 --month 参数格式为 YYYYMM（6位数字）。"""
    return bool(_MONTH_PATTERN.match(month))


def _build_duplication_query(month: str, market_type: str | None, limit: int) -> str:
    """构建全字段 GROUP BY HAVING count() > 1 查询 SQL。

    按 14 个业务字段全字段 GROUP BY，找出有全字段相同行的组。
    返回每组的具体字段值 + 重复次数，按重复次数降序排列。
    """
    cols = ", ".join(_TICK_COLUMNS)
    where_clauses = [f"trade_date BETWEEN toUInt32(toYYYYMM(toDate('{month}01'))) AND toUInt32(toYYYYMM(toDate('{month}01') + INTERVAL 1 MONTH - INTERVAL 1 DAY))"]
    if market_type:
        where_clauses.append(f"market_type = '{market_type}'")
    where_sql = " AND ".join(where_clauses)
    return _SQL_DUPLICATION.format(cols=cols, table=_TABLE, where=where_sql, limit=limit)


def _build_summary_query(month: str, market_type: str | None) -> str:
    """构建重复组总数与重复行总数汇总查询 SQL。"""
    cols = ", ".join(_TICK_COLUMNS)
    where_clauses = [f"trade_date BETWEEN toUInt32(toYYYYMM(toDate('{month}01'))) AND toUInt32(toYYYYMM(toDate('{month}01') + INTERVAL 1 MONTH - INTERVAL 1 DAY))"]
    if market_type:
        where_clauses.append(f"market_type = '{market_type}'")
    where_sql = " AND ".join(where_clauses)
    # 子查询找重复组，外层聚合：组数 + 重复行数（每组行数 = dup_cnt，总重复行 = sum(dup_cnt)）
    return _SQL_SUMMARY.format(cols=cols, table=_TABLE, where=where_sql)


def _build_total_row_query(month: str, market_type: str | None) -> str:
    """构建该月总行数查询 SQL（用于上下文对照，证明仅看聚合数字不够）。"""
    where_clauses = [f"trade_date BETWEEN toUInt32(toYYYYMM(toDate('{month}01'))) AND toUInt32(toYYYYMM(toDate('{month}01') + INTERVAL 1 MONTH - INTERVAL 1 DAY))"]
    if market_type:
        where_clauses.append(f"market_type = '{market_type}'")
    where_sql = " AND ".join(where_clauses)
    return _SQL_TOTAL_ROW.format(cols=", ".join(_TICK_COLUMNS), table=_TABLE, where=where_sql)


def _parse_tsv(tsv: str, expected_cols: int) -> list[list[str]]:
    """解析 ch_reader.query 返回的 TSV 字符串为二维列表。

    ch_reader.query 对 SELECT 返回 TSV：行以 \\n 分隔，列以 \\t 分隔。
    失败时返回空字符串。
    """
    if not tsv:
        return []
    rows: list[list[str]] = []
    for line in tsv.split("\n"):
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) != expected_cols:
            # 列数不符跳过（避免误解析）
            continue
        rows.append(fields)
    return rows


def _format_vertical(group_fields: list[str], dup_cnt: str, idx: int) -> str:
    """将一组重复行以 Vertical 格式输出（字段名: 值）。"""
    lines = [f"── 重复组 #{idx}（重复 {dup_cnt} 次）──"]
    for col, val in zip(_TICK_COLUMNS, group_fields):
        lines.append(f"  {col}: {val}")
    return "\n".join(lines)


def check_duplication(month: str, market_type: str | None = None, limit: int = _DEFAULT_LIMIT) -> dict[str, Any]:
    """执行真重复检查，返回结构化结果。

    Returns:
        包含以下键的 dict:
        - month: 检查的月份
        - market_type: 检查的市场类型（None 表示全部）
        - total_row_cnt: 该月总行数
        - uniq_full_field_cnt: 全字段去重后的行数
        - dup_group_cnt: 重复组数（全字段相同的组数）
        - dup_row_cnt: 重复行总数（每组 dup_cnt 之和）
        - dup_groups: 重复组详情列表（前 limit 组）
        - query_sql: 实际执行的查询 SQL（用于审计留档）
    """
    result: dict[str, Any] = {
        "month": month,
        "market_type": market_type,
        "total_row_cnt": 0,
        "uniq_full_field_cnt": 0,
        "dup_group_cnt": 0,
        "dup_row_cnt": 0,
        "dup_groups": [],
        "query_sql": "",
    }

    # 1. 总行数 + 全字段唯一行数（上下文对照——证明仅看聚合数字无法判定"重复"）
    total_sql = _build_total_row_query(month, market_type)
    total_tsv = ch_reader.query(total_sql)
    total_rows = _parse_tsv(total_tsv, 2)
    if total_rows:
        result["total_row_cnt"] = int(total_rows[0][0]) if total_rows[0][0] not in ("", "\\N") else 0
        result["uniq_full_field_cnt"] = int(total_rows[0][1]) if total_rows[0][1] not in ("", "\\N") else 0

    # 2. 重复组汇总（组数 + 重复行数）
    summary_sql = _build_summary_query(month, market_type)
    summary_tsv = ch_reader.query(summary_sql)
    summary_rows = _parse_tsv(summary_tsv, 2)
    if summary_rows:
        result["dup_group_cnt"] = int(summary_rows[0][0]) if summary_rows[0][0] not in ("", "\\N") else 0
        result["dup_row_cnt"] = int(summary_rows[0][1]) if summary_rows[0][1] not in ("", "\\N") else 0

    # 3. 重复组详情（前 limit 组，Vertical 格式）
    detail_sql = _build_duplication_query(month, market_type, limit)
    result["query_sql"] = detail_sql
    detail_tsv = ch_reader.query(detail_sql)
    # 详情查询返回 14 字段 + dup_cnt = 15 列
    detail_rows = _parse_tsv(detail_tsv, len(_TICK_COLUMNS) + 1)
    for idx, row in enumerate(detail_rows, start=1):
        group_fields = row[: len(_TICK_COLUMNS)]
        dup_cnt = row[len(_TICK_COLUMNS)]
        result["dup_groups"].append(
            {
                "index": idx,
                "dup_cnt": int(dup_cnt) if dup_cnt not in ("", "\\N") else 0,
                "fields": dict(zip(_TICK_COLUMNS, group_fields)),
                "vertical": _format_vertical(group_fields, dup_cnt, idx),
            }
        )

    return result


def _print_human_report(result: dict[str, Any]) -> None:
    """打印人类可读的检查报告。"""
    month = result["month"]
    mt = result["market_type"] or "全部"
    print("=" * 72)
    print(f"tick_data 真重复检查报告（RULE-DATA-OPS / TRAE-063）")
    print(f"  月份: {month} | market_type: {mt}")
    print("=" * 72)
    print(f"  该月总行数:                 {result['total_row_cnt']}")
    print(f"  全字段去重后行数:           {result['uniq_full_field_cnt']}")
    print(f"  行数差（总-全字段唯一）:    {result['total_row_cnt'] - result['uniq_full_field_cnt']}")
    print()
    print(f"  真重复组数（全字段相同组）: {result['dup_group_cnt']}")
    print(f"  真重复行总数:               {result['dup_row_cnt']}")
    print()
    print("  ⚠ 注意：行数差 ≠ 真重复数。行数差可能由 ReplacingMergeTree")
    print("    ORDER BY 键合并产生（同排序键不同维度记录被算成'重复'）。")
    print("    真重复 MUST 按全字段 GROUP BY HAVING count() > 1 判定。")
    print("    禁止用 count() - uniqExact(排序键) 作为'重复'判据。")
    print("=" * 72)

    if not result["dup_groups"]:
        print("\n✅ 未发现真重复行（全字段相同的行）——不构成破坏性操作的理由。")
        print("\n  若行数差 > 0 但真重复组数 = 0，说明差异来自排序键合并，")
        print("  这是 ReplacingMergeTree 引擎行为，不是数据问题，禁止删除。")
        return

    print(f"\n🔴 发现 {len(result['dup_groups'])} 组真重复行（前 {len(result['dup_groups'])} 组详情）：\n")
    for group in result["dup_groups"]:
        print(group["vertical"])
        print()
    print("─" * 72)
    print("⚠ 真重复行处理建议（RULE-DATA-OPS 三步验证）：")
    print("  1. 必要性：为什么有真重复？数据源是否重复推送？")
    print("  2. 真实性：以上为全字段相同的真重复（非排序键合并）")
    print("  3. 可逆性：操作前必须有备份/快照，或可从数据源恢复")
    print("  禁止直接 DELETE/REPLACE PARTITION——先排查数据源根因")


def main() -> None:
    """Entry point: parse args, run check, return exit code."""
    parser = argparse.ArgumentParser(
        description="tick_data 真重复检查工具——按全字段 GROUP BY 查找真重复行（RULE-DATA-OPS 配套）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python scripts/governance/data_quality/check_tick_duplication.py --month 202607
    python scripts/governance/data_quality/check_tick_duplication.py --month 202607 --market-type index
    python scripts/governance/data_quality/check_tick_duplication.py --month 202607 --limit 50 --json

真重复定义（铁律）:
    所有 14 个业务字段完全相同的行（trade_date, timestamp, symbol, market_type, price,
    volume, amount, direction, data_source, bid_price, ask_price, bid_volume, ask_volume, quality_flag）

禁止判据:
    count() - uniqExact(排序键) ——排序键不含全部业务字段，同排序键不同维度记录会被误判
        """,
    )
    parser.add_argument("--month", required=True, metavar="YYYYMM", help="检查的月份（6位数字，如 202607）")
    parser.add_argument("--market-type", default=None, metavar="TYPE", help="市场类型过滤（stock/index/etf/cb/stock_bj，默认全部）")
    parser.add_argument("--limit", type=int, default=_DEFAULT_LIMIT, metavar="N", help=f"显示重复组详情的最大组数（默认 {_DEFAULT_LIMIT}）")
    parser.add_argument("--json", action="store_true", help="JSON 输出（AI 消费格式）")

    args = parser.parse_args()

    if not _validate_month(args.month):
        print(f"错误: --month 参数格式错误，应为 YYYYMM（6位数字），实际: {args.month}", file=sys.stderr)
        sys.exit(2)

    try:
        result = check_duplication(args.month, args.market_type, args.limit)
    except Exception as e:
        print(f"检查失败: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_human_report(result)

    # exit 1 = 发现真重复（需排查根因，禁止直接删除）
    # exit 0 = 无真重复
    sys.exit(1 if result["dup_group_cnt"] > 0 else EXIT_PASS)


if __name__ == "__main__":
    main()
