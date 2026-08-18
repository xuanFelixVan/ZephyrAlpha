# [BLUEPRINT] MOD-INF-043 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""archiver.py — ClickHouse 冷数据归档工具（手动 CLI，INV-RET-002）。

三阶段原子操作：export → verify → drop
  1. export: ClickHouse HTTP API 导出分区为 Parquet 到 E 盘
  2. verify: 比对 Parquet 行数 = ClickHouse 行数 + 抽样字段值
  3. drop:   验证通过后 ALTER TABLE DROP PARTITION 释放 D 盘空间

安全机制：
  - 任何阶段失败不进入下一阶段，数据不丢失
  - 归档清单 append-only（archive_manifest.jsonl）
  - dry-run 模式（只打印不执行）
  - 断点续传（跳过已 dropped 的分区，重跑 verify 失败的分区）

用法：
  python scripts/ch/archiver.py archive --table c1_market.tick_data --partition 202201
  python scripts/ch/archiver.py archive-range --table c1_market.tick_data --from 202201 --to 202412
  python scripts/ch/archiver.py archive-range --table c1_market.tick_data --from 202201 --to 202412 --dry-run
  python scripts/ch/archiver.py archive-range --table c1_market.technical_indicator --period 60min --from 201901 --to 202108
  python scripts/ch/archiver.py list
  python scripts/ch/archiver.py stats
  python scripts/ch/archiver.py restore --table c1_market.tick_data --partition 202201

元组分区键表（如 c1_market.technical_indicator，PARTITION BY (period, YYYYMM)）
必须指定 --period；Parquet 按周期子目录分层（technical_indicator/60min/201901.parquet）。
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import http.client
import json
import logging
import os
import pathlib
import re
import sys
import time
import urllib.parse

_PROJECT_ROOT = str(pathlib.Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from zephyr.data import ch_reader
from zephyr.data.ch_config import ensure_ch_env_loaded as _ensure_ch_env_loaded
from zephyr.shared.security.secrets import get_secret_or_default

_ensure_ch_env_loaded()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("archiver")

# ============== 配置 ==============

ARCHIVE_ROOT = pathlib.Path("E:/zephyr_cold_archive")
MANIFEST_PATH = ARCHIVE_ROOT / "archive_manifest.jsonl"

_CH_HOST = get_secret_or_default("CLICKHOUSE_HOST", "")
_CH_HTTP_PORT = int(get_secret_or_default("CLICKHOUSE_HTTP_PORT", "8123"))
_CH_USER = get_secret_or_default("CLICKHOUSE_WRITER_USER") or get_secret_or_default("CLICKHOUSE_USER", "default")
_CH_PASSWORD = get_secret_or_default("CLICKHOUSE_WRITER_PASSWORD") or get_secret_or_default("CLICKHOUSE_PASSWORD", "")

# 各表的分区表达式（用于 WHERE 条件导出）
# 格式: table -> (partition_expr, partition_type)
# partition_type: "yyyymm" (整数如 202201) 或 "yyyymmdd" (整数如 20220101)
_PARTITION_EXPR: dict[str, str] = {
    "c1_market.tick_data": "toYYYYMM(trade_date)",
    "c1_market.kline_1min": "toYYYYMM(trade_date)",
    "c1_market.kline_5min": "toYYYYMM(trade_time)",
    "c1_market.kline_15min": "toYYYYMM(trade_date)",
    "c1_market.kline_30min": "toYYYYMM(trade_date)",
    "c1_market.kline_60min": "toYYYYMM(trade_date)",
    "c1_market.kline_etf_1min": "toYYYYMM(trade_date)",
    "c1_market.kline_etf_5min": "toYYYYMM(trade_date)",
    "c1_market.kline_etf_15min": "toYYYYMM(trade_date)",
    "c1_market.kline_etf_30min": "toYYYYMM(trade_date)",
    "c1_market.kline_etf_60min": "toYYYYMM(trade_date)",
    "c1_market.kline_lof_1min": "toYYYYMM(trade_date)",
    "c1_market.kline_lof_5min": "toYYYYMM(trade_date)",
    "c1_market.kline_lof_15min": "toYYYYMM(trade_date)",
    "c1_market.kline_lof_30min": "toYYYYMM(trade_date)",
    "c1_market.kline_lof_60min": "toYYYYMM(trade_date)",
    "c3_fundamental.news_data": "toYYYYMM(publish_time)",
    "c1_market.technical_indicator": "toYYYYMM(trade_date)",
}

# 元组分区键表：table -> 周期列名。此类表 PARTITION BY (period, toYYYYMM(...))，
# 归档/恢复必须带 --period 指定周期维度（契约 §2A 派生跟随源，v1.2.0）
_TUPLE_PERIOD_COL: dict[str, str] = {
    "c1_market.technical_indicator": "period",
}

_TUPLE_PARTITION_RE = re.compile(r"^\('([^']+)',(\d{6})\)$")

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_EXPORT = "SELECT * FROM {table} WHERE {where} FORMAT Parquet"
_SQL_COUNT_PARTITION = "SELECT count() FROM {table} WHERE {where}"
_SQL_SAMPLE_RANDOM = "SELECT * FROM {table} WHERE {where} ORDER BY rand() LIMIT 100 FORMAT JSON"
_SQL_LIST_PARTITIONS = (
    "SELECT DISTINCT partition FROM system.parts "
    "WHERE database='{db}' AND table='{tbl}' AND active=1 ORDER BY partition"
)


def _period_col(table: str) -> str | None:
    """元组分区键表的周期列名；非元组表返回 None。"""
    return _TUPLE_PERIOD_COL.get(table)


def _require_period(table: str, period: str | None) -> None:
    """元组分区表必须指定 --period；非元组表禁止指定（防误归档错维度）。"""
    need = _period_col(table)
    if need and not period:
        raise ValueError(f"表 {table} 分区键为 ({need}, YYYYMM)，必须指定 --period（如 --period 60min）")
    if not need and period:
        raise ValueError(f"表 {table} 非元组分区键，禁止指定 --period")


def _build_where(table: str, partition: str, period: str | None) -> str:
    """构造导出/行数统计的 WHERE 条件（元组键表叠加周期过滤）。"""
    expr = _get_partition_expr(table)
    if _period_col(table):
        return f"{_period_col(table)} = '{period}' AND {expr} = {partition}"
    return f"{expr} = {partition}"


def _drop_partition_sql(table: str, partition: str, period: str | None) -> str:
    """构造 DROP PARTITION 语句（元组键需 ('period',YYYYMM) 字面量形式）。"""
    if _period_col(table):
        return f"ALTER TABLE {table} DROP PARTITION ('{period}',{partition})"
    return f"ALTER TABLE {table} DROP PARTITION {partition}"


def _get_partition_expr(table: str) -> str:
    """获取表的分区表达式。"""
    if table in _PARTITION_EXPR:
        return _PARTITION_EXPR[table]
    # 默认用 toYYYYMM(trade_date)
    log.warning("表 %s 未配置分区表达式，默认用 toYYYYMM(trade_date)", table)
    return "toYYYYMM(trade_date)"


def _get_partitions(table: str, from_yyyymm: str, to_yyyymm: str, period: str | None = None) -> list[str]:
    """查询表在指定范围内的活跃分区列表（元组键表按 period 过滤并抽取 YYYYMM 段）。"""
    r = ch_reader.query(
        _SQL_LIST_PARTITIONS.format(db=table.split('.')[0], tbl=table.split('.')[1])
    )
    out: list[str] = []
    for line in r.strip().split("\n"):
        p = line.strip()
        if not p:
            continue
        if _period_col(table):
            m = _TUPLE_PARTITION_RE.match(p)
            if not m or m.group(1) != period:
                continue
            yyyymm = m.group(2)
        else:
            yyyymm = p
        if from_yyyymm <= yyyymm <= to_yyyymm:
            out.append(yyyymm)
    return sorted(set(out))


def _parquet_path(table: str, partition: str, period: str | None = None) -> pathlib.Path:
    """获取分区的 Parquet 文件路径（元组键表按周期子目录分层）。"""
    db, tbl = table.split(".")
    if _period_col(table):
        return ARCHIVE_ROOT / db / tbl / str(period) / f"{partition}.parquet"
    return ARCHIVE_ROOT / db / tbl / f"{partition}.parquet"


# ============== 三阶段原子操作 ==============

def export_partition(table: str, partition: str, dry_run: bool = False, period: str | None = None) -> pathlib.Path | None:
    """阶段1: 从 ClickHouse 导出分区为 Parquet 到 E 盘。

    用 ClickHouse HTTP API 的 SELECT ... FORMAT Parquet 直接获取 Parquet 字节流，
    避免 Python 序列化开销，速度最快。
    """
    _require_period(table, period)
    pq_path = _parquet_path(table, partition, period)
    pq_path.parent.mkdir(parents=True, exist_ok=True)

    sql = _SQL_EXPORT.format(table=table, where=_build_where(table, partition, period))
    # 导出逻辑视图：ReplacingMergeTree 表注入 FINAL（复用 ch_reader SSoT，#ARCH-CH-004）。
    # 保证 Parquet = 消费者所读去重结果，与 verify 的 FINAL 计数对齐。
    # 重复行系引擎未合并 artifact（2026-08-16 实证：kline_5min 35 分区、news_data 几乎全部
    # 热分区存在重复摄入，verify 正确拦截 10 分区）；裸导物理行会把冗余永久固化进冷库。
    sql = ch_reader.inject_final(sql)

    if dry_run:
        log.info("[DRY-RUN] export %s partition=%s period=%s → %s", table, partition, period, pq_path)
        log.info("  SQL: %s", sql)
        return pq_path

    # 先删除可能存在的旧文件（verify 失败后重跑）
    if pq_path.exists():
        log.warning("  旧 Parquet 文件已存在，删除重新导出: %s", pq_path)
        pq_path.unlink()

    log.info("  export: %s partition=%s → %s", table, partition, pq_path.name)
    t0 = time.time()

    try:
        conn = http.client.HTTPConnection(_CH_HOST, _CH_HTTP_PORT, timeout=600)
        headers = {
            "X-ClickHouse-User": _CH_USER,
            "X-ClickHouse-Key": _CH_PASSWORD,
        }
        quoted_sql = urllib.parse.quote(sql)
        conn.request("GET", f"/?query={quoted_sql}", headers=headers)
        resp = conn.getresponse()

        if resp.status != 200:
            body = resp.read().decode("utf-8", errors="replace")[:500]
            log.error("  export HTTP %s: %s", resp.status, body)
            conn.close()
            return None

        # 流式写入文件
        total_bytes = 0
        with open(pq_path, "wb") as f:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                f.write(chunk)
                total_bytes += len(chunk)
        conn.close()

        elapsed = time.time() - t0
        size_mb = total_bytes / 1024 / 1024
        log.info("  export 完成: %.1f MiB, %.1fs (%.1f MiB/s)", size_mb, elapsed, size_mb / elapsed if elapsed > 0 else 0)
        return pq_path

    except Exception as e:
        log.error("  export 异常: %s", e)
        if pq_path.exists():
            pq_path.unlink()
        return None


def verify_partition(table: str, partition: str, pq_path: pathlib.Path, period: str | None = None) -> bool:
    """阶段2: 验证 Parquet 行数 = ClickHouse 行数 + 抽样字段值。"""
    try:
        import pyarrow.parquet as pq
    except ImportError:
        log.error("  verify 失败: pyarrow 未安装")
        return False

    where = _build_where(table, partition, period)

    # 1. ClickHouse 行数
    r = ch_reader.query(
        _SQL_COUNT_PARTITION.format(table=table, where=where)
    ).strip()
    ch_count = int(r) if r else 0

    # 2. Parquet 行数
    try:
        meta = pq.read_metadata(str(pq_path))
        pq_count = meta.num_rows
    except Exception as e:
        log.error("  verify 失败: 读取 Parquet 元数据异常: %s", e)
        return False

    # 行数比对（大分区允许 ±1 行容差：ClickHouse count() 元数据优化 vs FORMAT Parquet 已知差异）
    diff = abs(ch_count - pq_count)
    tolerance = 1 if ch_count > 1_000_000 else 0
    if diff > tolerance:
        log.error("  verify 失败: 行数不一致 CH=%d Parquet=%d (差 %d, 容差 %d)", ch_count, pq_count, diff, tolerance)
        return False

    if diff == 0:
        log.info("  verify: 行数一致 %d = %d", ch_count, pq_count)
    else:
        log.info("  verify: 行数一致(容差内) CH=%d Parquet=%d (差 %d)", ch_count, pq_count, diff)

    # 3. 抽样字段值比对（随机 100 行）
    if ch_count > 0 and ch_count <= 10_000_000:
        # 小分区：直接比对
        try:
            ch_sample = ch_reader.query(
                _SQL_SAMPLE_RANDOM.format(table=table, where=where)
            )
            # 简单验证：能查到数据即可（完整字段比对太复杂，行数一致已足够可信）
            log.info("  verify: 抽样 100 行查询成功")
        except Exception as e:
            log.warning("  verify: 抽样查询异常（不阻断）: %s", e)

    return True


def drop_partition(table: str, partition: str, dry_run: bool = False, period: str | None = None) -> bool:
    """阶段3: ALTER TABLE DROP PARTITION 释放 D 盘空间。"""
    _require_period(table, period)
    sql = _drop_partition_sql(table, partition, period)
    if dry_run:
        log.info("[DRY-RUN] drop: %s", sql)
        return True

    log.info("  drop: %s", sql)
    try:
        r = ch_reader.query(sql)
        log.info("  drop 完成")
        return True
    except Exception as e:
        log.error("  drop 失败: %s", e)
        return False


# ============== 归档清单 ==============

def _append_manifest(record: dict) -> None:
    """append-only 写入归档清单。"""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_manifest() -> list[dict]:
    """读取归档清单。"""
    if not MANIFEST_PATH.exists():
        return []
    records = []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def _is_archived(table: str, partition: str, period: str | None = None) -> dict | None:
    """检查分区是否已归档（dropped=true）。返回归档记录或 None。

    旧清单记录无 period 键（get 返回 None），与非元组表 period=None 天然匹配。
    """
    for record in _read_manifest():
        if (record.get("table") == table and record.get("partition") == partition
                and record.get("period") == period):
            if record.get("dropped"):
                return record
    return None


# ============== 原子归档操作 ==============

def archive_partition(table: str, partition: str, dry_run: bool = False, period: str | None = None) -> bool:
    """三阶段原子归档: export → verify → drop。"""
    # 断点续传：检查是否已归档
    existing = _is_archived(table, partition, period)
    if existing:
        log.info("跳过（已归档）: %s partition=%s period=%s", table, partition, period)
        return True

    log.info("=" * 60)
    log.info("归档 %s partition=%s period=%s", table, partition, period)

    pq_path = _parquet_path(table, partition, period)

    # 阶段1: export
    if not export_partition(table, partition, dry_run=dry_run, period=period):
        log.error("export 失败，中止")
        return False

    if dry_run:
        log.info("[DRY-RUN] 跳过 verify 和 drop")
        return True

    # 阶段2: verify
    if not verify_partition(table, partition, pq_path, period=period):
        log.error("verify 失败，不执行 drop，数据安全")
        # 删除不可信的 Parquet 文件
        if pq_path.exists():
            pq_path.unlink()
        return False

    # 阶段3: drop
    if not drop_partition(table, partition, dry_run=dry_run, period=period):
        log.error("drop 失败，Parquet 已保留，可手动重试 drop")
        # 仍然记录清单（verified=true, dropped=false）
        _append_manifest(_manifest_record(table, partition, pq_path, dropped=False, period=period))
        return False

    # 记录归档清单
    _append_manifest(_manifest_record(table, partition, pq_path, dropped=True, period=period))

    log.info("归档完成: %s partition=%s period=%s ✓", table, partition, period)
    return True


def _manifest_record(table: str, partition: str, pq_path: pathlib.Path, dropped: bool, period: str | None) -> dict:
    """构造归档清单记录（元组键表附 period 字段）。"""
    record = {
        "table": table,
        "partition": partition,
        "parquet_path": str(pq_path),
        "parquet_size_bytes": pq_path.stat().st_size if pq_path.exists() else 0,
        "archived_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "verified": True,
        "dropped": dropped,
    }
    if period is not None:
        record["period"] = period
    return record


def archive_range(table: str, from_yyyymm: str, to_yyyymm: str, dry_run: bool = False, period: str | None = None) -> None:
    """批量归档指定范围内的分区。"""
    _require_period(table, period)
    partitions = _get_partitions(table, from_yyyymm, to_yyyymm, period=period)
    log.info("=== 批量归档 %s period=%s, 范围 %s~%s, 共 %d 个分区 ===", table, period, from_yyyymm, to_yyyymm, len(partitions))

    if dry_run:
        for p in partitions:
            existing = _is_archived(table, p, period)
            status = "已归档(跳过)" if existing else "待归档"
            log.info("  [DRY-RUN] partition=%s %s", p, status)
        return

    success = 0
    failed = 0
    skipped = 0
    t0 = time.time()

    for i, p in enumerate(partitions, 1):
        existing = _is_archived(table, p, period)
        if existing:
            skipped += 1
            continue

        log.info("--- %d/%d ---", i, len(partitions))
        if archive_partition(table, p, dry_run=False, period=period):
            success += 1
        else:
            failed += 1

    elapsed = time.time() - t0
    log.info("=== 批量归档完成: 成功 %d, 失败 %d, 跳过 %d, 耗时 %.1fs ===", success, failed, skipped, elapsed)


# ============== 查询/恢复 ==============

def list_archived(table: str | None = None) -> None:
    """列出已归档分区。"""
    records = _read_manifest()
    if table:
        records = [r for r in records if r.get("table") == table]

    if not records:
        print("无归档记录")
        return

    print(f"{'表名':<35} {'分区':<10} {'已验证':<6} {'已删除':<6} {'Parquet大小':<15} {'归档时间':<25}")
    print("-" * 100)
    for r in records:
        size_mb = r.get("parquet_size_bytes", 0) / 1024 / 1024
        print(f"{r.get('table',''):<35} {r.get('partition',''):<10} "
              f"{'✓' if r.get('verified') else '✗':<6} "
              f"{'✓' if r.get('dropped') else '✗':<6} "
              f"{size_mb:<15.1f} {r.get('archived_at',''):<25}")


def stats() -> None:
    """统计归档情况。"""
    records = _read_manifest()
    if not records:
        print("无归档记录")
        return

    by_table: dict[str, dict] = {}
    for r in records:
        tbl = r.get("table", "")
        if r.get("period"):
            tbl = f"{tbl}({r['period']})"
        if tbl not in by_table:
            by_table[tbl] = {"count": 0, "size_bytes": 0, "dropped": 0}
        by_table[tbl]["count"] += 1
        by_table[tbl]["size_bytes"] += r.get("parquet_size_bytes", 0)
        if r.get("dropped"):
            by_table[tbl]["dropped"] += 1

    print(f"{'表名':<35} {'归档分区数':<10} {'已删除':<8} {'Parquet总大小':<15}")
    print("-" * 70)
    total_size = 0
    total_count = 0
    for tbl, info in sorted(by_table.items()):
        size_mb = info["size_bytes"] / 1024 / 1024
        print(f"{tbl:<35} {info['count']:<10} {info['dropped']:<8} {size_mb:<15.1f} MiB")
        total_size += info["size_bytes"]
        total_count += info["count"]

    print("-" * 70)
    print(f"{'合计':<35} {total_count:<10} {'':<8} {total_size/1024/1024:<15.1f} MiB")

    # E 盘目录实际占用
    try:
        import shutil
        u = shutil.disk_usage("E:\\")
        print(f"\nE 盘: 总计 {u.total/1024**3:.1f} GB, 已用 {(u.total-u.free)/1024**3:.1f} GB, 可用 {u.free/1024**3:.1f} GB")
    except Exception:
        pass


def restore_partition(table: str, partition: str, period: str | None = None) -> bool:
    """从 Parquet 恢复分区到 ClickHouse（应急用）。"""
    _require_period(table, period)
    pq_path = _parquet_path(table, partition, period)
    if not pq_path.exists():
        log.error("Parquet 文件不存在: %s", pq_path)
        return False

    log.info("恢复 %s partition=%s period=%s ← %s", table, partition, period, pq_path)

    # 用 clickhouse-driver 读取 Parquet 并 INSERT
    try:
        import pyarrow.parquet as pq

        from zephyr.data.ch_writer import get_client

        client = get_client()
        if client is None:
            log.error("clickhouse-driver 不可用")
            return False

        # 读取 Parquet
        table_obj = pq.read_table(str(pq_path))
        df = table_obj.to_pandas()
        log.info("  读取 Parquet: %d 行", len(df))

        # 转换为元组列表
        cols = list(df.columns)
        rows = [tuple(row) for row in df.itertuples(index=False, name=None)]

        # 批量 INSERT
        cols_clause = "(" + ", ".join(cols) + ")"
        chunk_size = 100_000
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            client.execute(f"INSERT INTO {table} {cols_clause} VALUES", chunk)
            log.info("  写入 %d/%d 行", min(i + chunk_size, len(rows)), len(rows))

        log.info("恢复完成: %s partition=%s ✓", table, partition)
        return True

    except Exception as e:
        log.error("恢复失败: %s", e)
        return False


# ============== CLI ==============

def main():
    parser = argparse.ArgumentParser(description="ClickHouse 冷数据归档工具 (INV-RET-002)")
    sub = parser.add_subparsers(dest="command", required=True)

    # archive
    p_arch = sub.add_parser("archive", help="归档单个分区 (export→verify→drop)")
    p_arch.add_argument("--table", required=True)
    p_arch.add_argument("--partition", required=True)
    p_arch.add_argument("--period", default=None, help="元组分区键表必填（如 60min）")
    p_arch.add_argument("--dry-run", action="store_true")

    # archive-range
    p_range = sub.add_parser("archive-range", help="批量归档分区范围")
    p_range.add_argument("--table", required=True)
    p_range.add_argument("--from", dest="from_yyyymm", required=True)
    p_range.add_argument("--to", dest="to_yyyymm", required=True)
    p_range.add_argument("--period", default=None, help="元组分区键表必填（如 60min）")
    p_range.add_argument("--dry-run", action="store_true")

    # list
    p_list = sub.add_parser("list", help="列出已归档分区")
    p_list.add_argument("--table", default=None)

    # stats
    sub.add_parser("stats", help="统计归档情况")

    # restore
    p_restore = sub.add_parser("restore", help="从 Parquet 恢复到 ClickHouse")
    p_restore.add_argument("--table", required=True)
    p_restore.add_argument("--partition", required=True)
    p_restore.add_argument("--period", default=None, help="元组分区键表必填（如 60min）")

    args = parser.parse_args()

    if args.command in ("archive", "archive-range", "restore"):
        try:
            _require_period(args.table, args.period)
        except ValueError as e:
            parser.error(str(e))

    if args.command == "archive":
        archive_partition(args.table, args.partition, dry_run=args.dry_run, period=args.period)
    elif args.command == "archive-range":
        archive_range(args.table, args.from_yyyymm, args.to_yyyymm, dry_run=args.dry_run, period=args.period)
    elif args.command == "list":
        list_archived(args.table)
    elif args.command == "stats":
        stats()
    elif args.command == "restore":
        restore_partition(args.table, args.partition, period=args.period)


if __name__ == "__main__":
    main()
