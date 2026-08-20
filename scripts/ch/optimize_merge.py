# [BLUEPRINT] MOD-L04-001 | scripts/ch/optimize_merge.py | §
# [MODULE] scripts.ch.optimize_merge
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader;zephyr.data.ch_config
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] INV-RET-001;分区级幂等 OPTIMIZE FINAL;失败隔离断点重跑
# [MODIFY-GUARD] docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml;scripts/script-manifest.yaml
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单分区失败返回False不中断批处理;exit 1=存在失败分区
# [TESTS] tests/scripts/test_optimize_merge.py
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 按需调用 runner（人工追补 + 外部 Windows 计划任务周期触发），非 cron 常驻服务——对标 apply_depgraph.py 同类 CLI 工具豁免
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""optimize_merge.py — ReplacingMergeTree 合并维护工具（分区级 OPTIMIZE FINAL 去重）。

背景（2026-08-16 实证）：全部业务表均为 ReplacingMergeTree，摄入幂等靠引擎键去重，
但 ClickHouse 不保证 merge 完成——未合并重复行持续累积（实证：kline_5min 35 分区、
news_data 几乎全部热分区、technical_indicator 全热窗口约 1.7x 物理冗余）。
三防线闭环：读取由 ch_reader FINAL 屏蔽（#ARCH-CH-004）、归档由 archiver FINAL 导出
（冷分层裁定批 commit 276c722548）、物理去重由本工具兜底。

用法：
  python scripts/ch/optimize_merge.py --all --dry-run                 # 全业务表扫描（干跑）
  python scripts/ch/optimize_merge.py --table c1_market.kline_5min --from 202109 --to 202608
  python scripts/ch/optimize_merge.py --table c3_fundamental.news_data --from 201001 --to 202608
  python scripts/ch/optimize_merge.py --weekly                        # 周期维护：各表近3个月分区

安全：
  - 分区级逐个 OPTIMIZE（失败隔离，幂等可断点重跑）
  - dry-run 只打印不执行
  - 表清单自发现（system.tables 查 ReplacingMergeTree，无硬编码 SSoT 漂移）
  - 仅含 YYYYMM 月份段的分区才纳入（非时间分区跳过并记日志）
"""

from __future__ import annotations

import argparse
import datetime
import logging
import pathlib
import re
import sys
import time

_PROJECT_ROOT = str(pathlib.Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from zephyr.data import ch_reader
from zephyr.data.ch_config import ensure_ch_env_loaded as _ensure_ch_env_loaded

_ensure_ch_env_loaded()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("optimize_merge")

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_REPLACING_TABLES = (
    "SELECT database, name FROM system.tables "
    "WHERE database IN ('c0_meta','c1_market','c2_alternative','c3_fundamental') "
    "AND engine='ReplacingMergeTree' ORDER BY database, name"
)
_SQL_PARTITIONS = (
    "SELECT DISTINCT partition FROM system.parts "
    "WHERE database='{db}' AND table='{tbl}' AND active=1 ORDER BY partition"
)
_SQL_OPTIMIZE = "OPTIMIZE TABLE {table} PARTITION {partition_literal} FINAL"

_MONTH_RE = re.compile(r"(\d{6})")
_TUPLE_MONTH_RE = re.compile(r"^\('[^']+',(\d{6})\)$")

_BUSINESS_DBS = ("c0_meta", "c1_market", "c2_alternative", "c3_fundamental")


def extract_month(partition: str) -> str | None:
    """从分区标识提取 YYYYMM 月份段；非时间分区返回 None。

    支持：裸月份 201901、元组键 ('60min',201901)、其他含月份段的形式。
    """
    m = _TUPLE_MONTH_RE.match(partition)
    if m:
        return m.group(1)
    if partition.isdigit() and len(partition) == 6:
        return partition
    m = _MONTH_RE.search(partition)
    return m.group(1) if m else None


def partition_literal(partition: str) -> str:
    """构造 OPTIMIZE ... PARTITION 字面量（元组键原样，裸月份直填，其余加引号）。"""
    if _TUPLE_MONTH_RE.match(partition):
        return partition
    if partition.isdigit():
        return partition
    return "'" + partition.replace("'", "\\'") + "'"


def weekly_cutoff(today: datetime.date | None = None, months: int = 3) -> str:
    """周期维护月份下界：today 往前 months 个月的 YYYYMM。"""
    today = today or datetime.date.today()
    y, m = today.year, today.month - months
    while m <= 0:
        y -= 1
        m += 12
    return f"{y}{m:02d}"


def list_replacing_tables() -> list[str]:
    """自发现全部业务库 ReplacingMergeTree 表。"""
    r = ch_reader.query(_SQL_REPLACING_TABLES)
    return [line.strip().replace("\t", ".") for line in r.strip().split("\n") if line.strip()]


def list_partitions(table: str, from_yyyymm: str | None, to_yyyymm: str | None) -> list[str]:
    """查询表活跃分区并按月份范围过滤（非时间分区跳过）。"""
    db, tbl = table.split(".")
    r = ch_reader.query(_SQL_PARTITIONS.format(db=db, tbl=tbl))
    out: list[str] = []
    for line in r.strip().split("\n"):
        p = line.strip()
        if not p:
            continue
        month = extract_month(p)
        if month is None:
            log.warning("跳过非时间分区: %s %s", table, p)
            continue
        if from_yyyymm and month < from_yyyymm:
            continue
        if to_yyyymm and month > to_yyyymm:
            continue
        out.append(p)
    return out


def optimize_partition(table: str, partition: str, dry_run: bool = False) -> bool:
    """单分区 OPTIMIZE FINAL（幂等，失败返回 False 不中断批处理）。"""
    sql = _SQL_OPTIMIZE.format(table=table, partition_literal=partition_literal(partition))
    if dry_run:
        log.info("[DRY-RUN] %s", sql)
        return True
    log.info("optimize: %s", sql)
    t0 = time.time()
    try:
        ch_reader.query(sql, timeout=7200)
        log.info("optimize 完成: %s %s (%.1fs)", table, partition, time.time() - t0)
        return True
    except Exception as e:
        log.error("optimize 失败: %s %s: %s", table, partition, e)
        return False


def optimize_table(
    table: str, from_yyyymm: str | None, to_yyyymm: str | None, dry_run: bool = False
) -> tuple[int, int]:
    """表级批量 OPTIMIZE，返回 (成功, 失败)。"""
    partitions = list_partitions(table, from_yyyymm, to_yyyymm)
    log.info("=== %s: %d 个分区待 OPTIMIZE ===", table, len(partitions))
    ok = fail = 0
    for i, p in enumerate(partitions, 1):
        log.info("--- %s %d/%d ---", table, i, len(partitions))
        if optimize_partition(table, p, dry_run=dry_run):
            ok += 1
        else:
            fail += 1
    log.info("=== %s 完成: 成功 %d, 失败 %d ===", table, ok, fail)
    return ok, fail


def main() -> int:
    parser = argparse.ArgumentParser(description="ReplacingMergeTree 合并维护（分区级 OPTIMIZE FINAL 去重）")
    parser.add_argument("--table", default=None, help="单表（db.table）")
    parser.add_argument("--all", action="store_true", help="全部业务库 ReplacingMergeTree 表")
    parser.add_argument("--from", dest="from_yyyymm", default=None, help="起始月份 YYYYMM（含）")
    parser.add_argument("--to", dest="to_yyyymm", default=None, help="截止月份 YYYYMM（含）")
    parser.add_argument("--weekly", action="store_true", help="周期维护模式：各表近3个月分区")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.weekly:
        args.from_yyyymm = weekly_cutoff()
        log.info("weekly 模式: from=%s", args.from_yyyymm)

    if args.table:
        tables = [args.table]
    elif args.all or args.weekly:
        tables = list_replacing_tables()
    else:
        parser.error("必须指定 --table 或 --all 或 --weekly")

    log.info("=== 待处理表: %d ===", len(tables))
    total_ok = total_fail = 0
    for t in tables:
        ok, fail = optimize_table(t, args.from_yyyymm, args.to_yyyymm, dry_run=args.dry_run)
        total_ok += ok
        total_fail += fail
    log.info("=== 全部完成: 成功 %d, 失败 %d ===", total_ok, total_fail)
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
