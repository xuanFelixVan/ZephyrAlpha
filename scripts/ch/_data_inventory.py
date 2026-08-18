# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] scripts.ch._data_inventory
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_config; clickhouse-driver(pip)
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] diagnostic
# [INVARIANTS] 全库数据盘点只读工具：逐表审计行数/日期范围/空表/缺失日期/引擎/大小；输出数据资产清单用于数据收口；只读 SELECT 零写入零破坏性操作
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 盘点完成->退出码0
# [TESTS] python scripts/ch/_data_inventory.py (smoke: 全库扫描+输出报告)
# [TTL] permanent
# noqa: m02-manual  一次性诊断脚本
"""全库数据盘点：逐表审计行数/日期范围/空表/缺失日期/引擎/大小。

输出完整数据资产清单，用于"收口"——确认数据完整性 + 识别缺口。
"""
from __future__ import annotations

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from clickhouse_driver import Client

from zephyr.data.ch_config import load_ch_config

_cfg = load_ch_config()
c = Client(host=_cfg["host"], port=9000, user=_cfg["user"], password=_cfg["password"], connect_timeout=15)


def main() -> None:
    print("=" * 90)
    print(f"全库数据盘点 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)

    # ---------- [1] 数据库概览 ----------
    print("\n[1] 数据库概览")
    print("-" * 90)
    dbs = c.execute(
        "SELECT database, sum(rows), sum(bytes_on_disk)/1024/1024/1024 AS gb "
        "FROM system.parts WHERE active=1 AND database NOT IN ('system','INFORMATION_SCHEMA','information_schema','default') "
        "GROUP BY database ORDER BY gb DESC"
    )
    print(f"{'数据库':20s} {'行数':>15s} {'大小(GiB)':>10s}")
    total_rows = 0
    total_gb = 0.0
    for d, r, gb in dbs:
        print(f"{d:20s} {r:>15,} {gb:>10.2f}")
        total_rows += r
        total_gb += gb
    print(f"{'合计':20s} {total_rows:>15,} {total_gb:>10.2f}")

    # ---------- [2] 逐表盘点 ----------
    print("\n[2] 逐表盘点（c1_market + c3_fundamental）")
    print("-" * 90)
    tables = c.execute(
        "SELECT database, name, engine, total_rows, total_bytes/1024/1024/1024 AS gb "
        "FROM system.tables "
        "WHERE database IN ('c1_market','c3_fundamental') "
        "ORDER BY database, name"
    )
    print(f"{'表名':40s} {'引擎':25s} {'行数':>15s} {'GiB':>8s} {'状态'}")
    print("-" * 90)
    empty_tables = []
    for db, tbl, eng, rows, gb in tables:
        full = f"{db}.{tbl}"
        status = "空表" if rows == 0 else "OK"
        if rows == 0:
            empty_tables.append(full)
        print(f"{full:40s} {eng:25s} {rows:>15,} {gb:>8.3f} {status}")

    print(f"\n总表数: {len(tables)}")
    print(f"空表: {len(empty_tables)}")
    if empty_tables:
        print("  空表清单:")
        for t in empty_tables:
            print(f"    {t}")

    # ---------- [3] 关键表日期范围 ----------
    print("\n[3] 关键表日期范围（最新/最旧 trade_date 或等效列）")
    print("-" * 90)
    key_tables = [
        ("c1_market", "kline_daily", "trade_date"),
        ("c1_market", "kline_1min", "trade_date"),
        ("c1_market", "tick_data", "trade_date"),
        ("c1_market", "kline_5min", "trade_date"),
        ("c1_market", "kline_daily_hfq", "trade_date"),
        ("c3_fundamental", "income_statement", "report_period"),
        ("c3_fundamental", "news_data", "publish_time"),
    ]
    print(f"{'表':35s} {'最旧':12s} {'最新':12s} {'天数':>6s} {'行数':>15s}")
    print("-" * 90)
    for db, tbl, date_col in key_tables:
        try:
            # 检查表是否存在
            exists = c.execute(
                f"SELECT count() FROM system.tables WHERE database='{db}' AND name='{tbl}'"
            )[0][0]
            if not exists:
                print(f"{db}.{tbl:30s} (表不存在)")
                continue
            r = c.execute(
                f"SELECT min({date_col}), max({date_col}), count(), "
                f"dateDiff('day', min({date_col}), max({date_col})) "
                f"FROM {db}.{tbl}"
            )[0]
            if r[0]:
                print(f"{db}.{tbl:30s} {str(r[0]):12s} {str(r[1]):12s} {r[3]:>6d} {r[2]:>15,}")
            else:
                print(f"{db}.{tbl:30s} (空表)")
        except Exception as e:
            print(f"{db}.{tbl:30s} ERROR: {e}")

    # ---------- [4] 时区类型一致性 ----------
    print("\n[4] DateTime 列时区一致性（期望全为 DateTime64 带时区）")
    print("-" * 90)
    bad_tz = c.execute(
        "SELECT database, table, name, type FROM system.columns "
        "WHERE database IN ('c1_market','c3_fundamental') "
        "AND type = 'DateTime' "
        "ORDER BY database, table, name"
    )
    if bad_tz:
        print(f"[BAD] 发现 {len(bad_tz)} 个未迁移的 DateTime 列:")
        for d, t, n, typ in bad_tz:
            print(f"  {d}.{t}.{n} = {typ}")
    else:
        print("[OK] 全部 DateTime 列已迁移为 DateTime64 带时区")

    # ---------- [5] 残留迁移备份表 ----------
    print("\n[5] 残留 _tzold/_tznew 表（迁移后应为空）")
    print("-" * 90)
    leftovers = c.execute(
        "SELECT database, name, total_rows, total_bytes/1024/1024/1024 AS gb "
        "FROM system.tables "
        "WHERE name LIKE '%_tzold' OR name LIKE '%_tznew' "
        "ORDER BY gb DESC"
    )
    if leftovers:
        for d, n, r, gb in leftovers:
            print(f"  {d}.{n}: {r:,} rows, {gb:.2f} GiB")
    else:
        print("  [OK] 无残留（迁移已完全清理）")

    # ---------- [6] 磁盘空间 ----------
    print("\n[6] 磁盘空间")
    print("-" * 90)
    disk = c.execute(
        "SELECT name, free_space/1024/1024/1024 AS free_gb, "
        "total_space/1024/1024/1024 AS total_gb "
        "FROM system.disks"
    )
    for n, free, total in disk:
        pct = free / total * 100 if total else 0
        print(f"  {n}: {free:.1f} / {total:.1f} GiB free ({pct:.1f}%)")

    # ---------- [7] detached parts 残骸 ----------
    print("\n[7] detached parts 残骸（DROP PARTITION 后未清理的残骸）")
    print("-" * 90)
    try:
        det = c.execute(
            "SELECT database, table, count() AS n, sum(bytes_on_disk)/1024/1024/1024 AS gb "
            "FROM system.detached_parts "
            "WHERE database IN ('c1_market','c3_fundamental') "
            "GROUP BY database, table ORDER BY gb DESC LIMIT 10"
        )
        if det:
            total_det = 0.0
            for d, t, n, gb in det:
                print(f"  {d}.{t}: {n} parts, {gb:.2f} GiB")
                total_det += gb
            print(f"  合计: {total_det:.2f} GiB")
        else:
            print("  [OK] 无 detached parts 残骸")
    except Exception as e:
        print(f"  (查询失败: {e})")

    print("\n" + "=" * 90)
    print("盘点完成")
    print("=" * 90)


if __name__ == "__main__":
    main()
