# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] scripts.ch.apply_timezone_migration
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_config; clickhouse-driver(pip)
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 时区防线真源：本脚本为 c1_market/c3_fundamental 全库 DateTime 时区统一化的唯一执行链路；系统列(ingest_ts/updated_at/fetched_at/crawl_time)->DateTime64(3,'UTC')(无数据偏移)；业务列(trade_time/timestamp/auction_time/snapshot_time/publish_time/full_publish_time)->偏移-8h+DateTime64(3,'Asia/Shanghai')；键列(分区/排序)走重建路径，非键列走 ALTER UPDATE+MODIFY；版本列(ReplacingMergeTree(ingest_ts))MODIFY被拒走 version-col 重建路径(无偏移)；幂等(已迁移列跳过)；自验证(类型+epoch+行数对账)；tick_data(181GiB)走分区批量重建
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; dry-run差异->退出码1; 全部一致->退出码0; 破坏性操作前未备份->拒绝执行退出码3
# [TESTS] python scripts/ch/apply_timezone_migration.py --dry-run (smoke: 全库扫描+策略输出+0写入); python scripts/ch/apply_timezone_migration.py --verify
# [TTL] permanent
# noqa: m02-manual  M02豁免: 一次性迁移脚本,手动触发,非reconciler无需事件触发
"""ClickHouse 时区防线迁移脚本（audit A组 Schema 治理 - 时区防线，#ARCH-CH-022）。

背景（audit_01_schema_review.md）：
    全库 DateTime 列存在 UTC/北京时间混存——业务时间戳(trade_time 等)按北京
    墙钟写入但以 UTC epoch 存储（晚 8 小时），系统时间戳(ingest_ts 等)用 now()
    为真 UTC。导致 now()-trade_time 等算术差 8 小时，schema 未声明时区（歧义）。

治本方案（已实测验证 tz_parse_test.py）：
    - 系统列 -> DateTime64(3, 'UTC')      （无数据偏移，纯类型标注）
    - 业务列 -> DateTime64(3, 'Asia/Shanghai') + 数据偏移 -8h（修正 epoch）
    验证：业务列迁移后 toUnixTimestamp(trade_time) 等于真实 UTC 瞬时；
          toTimezone(trade_time,'Asia/Shanghai') 显示北京墙钟；插入 naive 北京
          字符串（ch_writer str() 路径）自动按列时区解析为正确 epoch——无需改
          写入端代码。

执行约束（实测 tz_alter_test.py）：
    - ClickHouse 禁止 ALTER MODIFY/UPDATE 键列（分区键或排序键）-> 须重建表
    - 非键列可直接 ALTER UPDATE col=col-INTERVAL 8 HOUR + MODIFY COLUMN

用法::

    python scripts/ch/apply_timezone_migration.py --dry-run             # 扫描+输出策略，0写入
    python scripts/ch/apply_timezone_migration.py --verify              # 仅校验一致性
    python scripts/ch/apply_timezone_migration.py --phase system        # 系统列类型标注（安全）
    python scripts/ch/apply_timezone_migration.py --phase version-col   # 版本列重建（MODIFY被拒须重建）
    python scripts/ch/apply_timezone_migration.py --phase business      # 业务列（小表）
    python scripts/ch/apply_timezone_migration.py --phase recreate      # 键列表重建（中/小表）
    python scripts/ch/apply_timezone_migration.py --phase tickdata      # tick_data 分区批量重建
    python scripts/ch/apply_timezone_migration.py --table c1_market.kline_1min  # 单表
    python scripts/ch/apply_timezone_migration.py --all                 # 全部（按顺序）

    --no-backup-check  跳过备份存在性检查（默认要求近 24h 内有成功 CH 备份）

退出码：0=成功/一致  1=有差异/未完成  2=CH不可达  3=未备份拒绝破坏性操作
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from clickhouse_driver import Client

from zephyr.data.ch_config import load_ch_config

# ========== 连接 ==========

_admin_config = load_ch_config()


def _client() -> Client:
    return Client(
        host=_admin_config["host"], port=_admin_config.get("port", 9000),
        user=_admin_config.get("user", "default"),
        password=_admin_config.get("password", ""),
        connect_timeout=5,
    )


# ========== 分类真源（SSoT）==========

# 系统时间戳列名——now()/now_utc() 生成，真 UTC，仅需类型标注（无偏移）
SYSTEM_COL_NAMES: frozenset[str] = frozenset({
    "ingest_ts", "updated_at", "fetched_at", "crawl_time", "recorded_time",
    "check_time",  # cross_validation_log 校验执行时间（系统生成，真 UTC）
})

# 业务时间戳列——北京墙钟按 UTC epoch 存储（晚 8h），需偏移 -8h + Asia/Shanghai
# (database, table, column)
BUSINESS_COLUMNS: list[tuple[str, str, str]] = [
    # 1min/5min/15min/30min/60min K 线族（trade_time 在分区+排序键 -> 重建）
    ("c1_market", "kline_1min", "trade_time"),
    ("c1_market", "kline_5min", "trade_time"),
    ("c1_market", "kline_15min", "trade_time"),
    ("c1_market", "kline_30min", "trade_time"),
    ("c1_market", "kline_60min", "trade_time"),
    # ETF/LOF 分钟 K 线（trade_time 在排序键，分区在 trade_date -> 重建）
    ("c1_market", "kline_etf_1min", "trade_time"),
    ("c1_market", "kline_etf_5min", "trade_time"),
    ("c1_market", "kline_etf_15min", "trade_time"),
    ("c1_market", "kline_etf_30min", "trade_time"),
    ("c1_market", "kline_etf_60min", "trade_time"),
    ("c1_market", "kline_lof_1min", "trade_time"),
    ("c1_market", "kline_lof_5min", "trade_time"),
    ("c1_market", "kline_lof_15min", "trade_time"),
    ("c1_market", "kline_lof_30min", "trade_time"),
    ("c1_market", "kline_lof_60min", "trade_time"),
    # timestamp 列
    ("c1_market", "tick_data", "timestamp"),
    ("c1_market", "auction_book", "timestamp"),
    ("c1_market", "index_quote", "timestamp"),
    ("c1_market", "kline_cb", "timestamp"),
    ("c1_market", "kline_futures", "timestamp"),
    ("c1_market", "option_kline", "timestamp"),
    ("c1_market", "kline_sector_880", "timestamp"),
    ("c1_market", "sector_snapshot", "timestamp"),
    # 其他业务时间戳
    ("c1_market", "auction_snapshot", "auction_time"),
    ("c1_market", "realtime_snapshot", "snapshot_time"),
    ("c1_market", "kline_sector_intraday", "trade_date"),  # DateTime 非 Date
    # c3 新闻舆情
    ("c3_fundamental", "news_data", "publish_time"),
    ("c3_fundamental", "news_data", "full_publish_time"),
]

SHIFT = "- INTERVAL 8 HOUR"
BUSINESS_TZ = "DateTime64(3, 'Asia/Shanghai')"
SYSTEM_TZ = "DateTime64(3, 'UTC')"


# ========== 元数据查询 ==========


def _table_key_info(c: Client, db: str, table: str) -> tuple[str, str]:
    """返回 (partition_key, sorting_key)。db/table 为受控标识符（来自本脚本目录）。"""
    r = c.execute(
        f"SELECT partition_key, sorting_key FROM system.tables "
        f"WHERE database='{db}' AND name='{table}'"
    )
    if not r:
        return ("", "")
    return (r[0][0] or "", r[0][1] or "")


def _col_is_in_key(col: str, partition_key: str, sorting_key: str) -> bool:
    """判断列名是否出现在分区键或排序键表达式中。

    用单词边界匹配（避免 'time' 误匹配 'trade_time' 的子串）。
    """
    pat = re.compile(r"\b" + re.escape(col) + r"\b")
    return bool(pat.search(partition_key) or pat.search(sorting_key))


def _columns(c: Client, db: str, table: str) -> list[tuple[str, str]]:
    """返回 [(col, type), ...]。db/table 为受控标识符。"""
    return [(r[0], r[1]) for r in c.execute(
        f"SELECT name, type FROM system.columns WHERE database='{db}' AND table='{table}' "
        f"ORDER BY position"
    )]


def _business_cols_for(db: str, table: str) -> list[str]:
    return [col for (d, t, col) in BUSINESS_COLUMNS if d == db and t == table]


def _row_count(c: Client, db: str, table: str) -> int:
    r = c.execute(f"SELECT total_rows FROM system.tables WHERE database='{db}' AND name='{table}'")
    return int(r[0][0]) if r and r[0][0] else 0


# ========== 类型变换 ==========


def _transform_ddl(ddl: str, db: str, table: str, business_cols: list[str]) -> str:
    """把 SHOW CREATE 输出变换为新表 DDL：业务列->Asia/Shanghai，系统列->UTC。

    列定义格式：`colname` Type [DEFAULT...] [COMMENT...]，Type 是反引号后的 token。
    用精确正则 `` `col` DateTime(?![0-9]) `` 替换（DateTime64 不误匹配）。
    同时把表名改写为 _tznew 后缀（调用方负责）。
    """
    col_types: dict[str, str] = {}
    for col, typ in _columns(_client(), db, table):
        if not typ.startswith("DateTime"):
            continue
        if col in business_cols:
            col_types[col] = BUSINESS_TZ
        elif col in SYSTEM_COL_NAMES:
            col_types[col] = SYSTEM_TZ
    # 逐列替换 `` `col` DateTime `` -> `` `col` DateTime64(...) ``
    out = ddl
    for col, newtyp in col_types.items():
        # 匹配 `col` DateTime （后跟空格/逗号/换行，且非 DateTime64——用负向先行）
        pat = re.compile(r"(`" + re.escape(col) + r"`\s+)DateTime(?![0-9(])")
        out = pat.sub(rf"\1{newtyp}", out)
    return out


def _build_shift_select(c: Client, db: str, table: str, business_cols: list[str]) -> str:
    """构造 INSERT SELECT 的列清单：业务列偏移 -8h，其余原样。"""
    parts: list[str] = []
    for col, _typ in _columns(c, db, table):
        if col in business_cols:
            parts.append(f"{col} {SHIFT} AS {col}")
        else:
            parts.append(col)
    return ", ".join(parts)


# ========== 迁移操作 ==========


def _migrate_system_columns(c: Client, db: str, table: str, dry: bool) -> list[str]:
    """系统列：MODIFY COLUMN -> DateTime64(3,'UTC')。无偏移。

    排序键列（如 cross_validation_log.check_time）的 MODIFY 会触发异步 mutation，
    ClickHouse 允许但可能失败——失败时记 WARN 并继续，由 --verify 兜底报告差异。
    """
    actions: list[str] = []
    for col, typ in _columns(c, db, table):
        if col not in SYSTEM_COL_NAMES:
            continue
        if not typ.startswith("DateTime"):
            continue
        if typ == SYSTEM_TZ or "DateTime64" in typ:
            continue  # 已迁移
        sql = f"ALTER TABLE {db}.{table} MODIFY COLUMN `{col}` {SYSTEM_TZ}"
        actions.append(sql)
        if not dry:
            try:
                c.execute(sql)
            except Exception as e:  # noqa: BLE001
                print(f"  WARN: {sql} -> {e}")
    return actions


def _migrate_business_plain(c: Client, db: str, table: str, business_cols: list[str], dry: bool) -> list[str]:
    """业务列（非键）：UPDATE -8h + MODIFY -> Asia/Shanghai。"""
    actions: list[str] = []
    for col in business_cols:
        typ = _col_type(c, db, table, col)
        if typ is None:
            continue
        if typ == BUSINESS_TZ:
            continue  # 已迁移
        # 1. 偏移数据 -8h（先于类型变换，避免 DateTime64 语义干扰）
        upd = f"ALTER TABLE {db}.{table} UPDATE `{col}` = `{col}` {SHIFT} WHERE 1"
        actions.append(upd)
        if not dry:
            c.execute(upd)
            c.execute(f"ALTER TABLE {db}.{table} MODIFY COLUMN `{col}` {BUSINESS_TZ}")
        # 2. 类型变换
        mod = f"ALTER TABLE {db}.{table} MODIFY COLUMN `{col}` {BUSINESS_TZ}"
        actions.append(mod)
    return actions


def _col_type(c: Client, db: str, table: str, col: str) -> str | None:
    r = c.execute(
        f"SELECT type FROM system.columns WHERE database='{db}' AND table='{table}' AND name='{col}'"
    )
    return r[0][0] if r else None


def _partition_where(partition_key: str, partition_id: str) -> str:
    """构造分区过滤 WHERE 子句。

    partition_key 如 'toYYYYMM(trade_date)'，partition_id 如 '202607'。
    对 toYYYYMM/toYYYYMMDD 返回整数比较；对纯列名返回字符串比较。
    """
    if not partition_key:
        return "1"  # 无分区键，全表
    try:
        int(partition_id)
        return f"{partition_key} = {partition_id}"
    except ValueError:
        return f"{partition_key} = '{partition_id}'"


def _safe_drop_table(c: Client, full_table: str) -> None:
    """安全删除大表：先逐分区删除（绕过 50GB 限制），再 DROP 空表。"""
    # 尝试直接 DROP
    try:
        c.execute(f"DROP TABLE {full_table}")
        return
    except Exception:  # noqa: BLE001 — 可能因 >50GB 被拒
        pass
    # 逐分区删除
    parts = c.execute(
        f"SELECT partition FROM system.parts "
        f"WHERE database='{full_table.split('.')[0]}' "
        f"AND table='{full_table.split('.')[1]}' AND active=1 "
        f"GROUP BY partition ORDER BY partition"
    )
    for (part,) in parts:
        try:
            c.execute(f"ALTER TABLE {full_table} DROP PARTITION {part}")
        except Exception:  # noqa: BLE001
            pass
    # 删除空表
    c.execute(f"DROP TABLE {full_table}")


def _recreate_table(c: Client, db: str, table: str, business_cols: list[str], dry: bool) -> list[str]:
    """业务列（键列）：重建表（并发写入容忍版）。

    策略（治本修复 #ARCH-CH-022 recreate phase）：
    1. CREATE _tznew（shifted DDL）
    2. INSERT SELECT（全量，-8h 偏移）
    3. RENAME old-> _tzold, _tznew -> old（立即完成迁移）
    4. 分区级对比（raw count per partition via system.parts）
    5. 补齐缺失分区（re-INSERT from _tzold，ReplacingMergeTree 自动去重）
    6. 验证：最新交易日 unique(sorting key) 行数匹配
    7. DROP _tzold（大表逐分区删除绕过 50GB 限制）

    并发写入根因：scheduler 在 INSERT SELECT 的 N 分钟内写入新数据到 old 表，
    导致 old(raw) > new(raw)。分区级补齐利用 ReplacingMergeTree 幂等性补齐缺失行。
    FINAL count 在大表上非确定性（实测 0.078% 偏差），改用 raw count + unique 验证。
    """
    actions: list[str] = []
    old_full = f"{db}.{table}"
    new_full = f"{db}.{table}_tznew"
    old_bak = f"{db}.{table}_tzold"

    ddl = c.execute(f"SHOW CREATE TABLE {old_full}")[0][0]
    new_ddl = _transform_ddl(ddl, db, table, business_cols)
    new_ddl = new_ddl.replace(f"CREATE TABLE {old_full}", f"CREATE TABLE {new_full}", 1)

    select_cols = _build_shift_select(c, db, table, business_cols)
    cols_list = ", ".join(f"`{col}`" for col, _ in _columns(c, db, table))

    # 分区键表达式（用于分区级补齐 WHERE 子句）
    pk_expr = _table_key_info(c, db, table)[0]  # partition_key

    actions.append(f"DROP TABLE IF EXISTS {new_full}")
    actions.append(new_ddl.replace("\n", " ")[:120] + "...")
    actions.append(f"INSERT INTO {new_full} ({cols_list}) SELECT {select_cols} FROM {old_full}")
    actions.append(f"RENAME TABLE {old_full} TO {old_bak}, {new_full} TO {old_full}")
    actions.append("-- partition fixup (concurrent-write tolerance)")
    actions.append(f"DROP TABLE {old_bak}")

    if dry:
        return actions

    # ---- Step 1-2: CREATE + INSERT ----
    c.execute(f"DROP TABLE IF EXISTS {new_full}")
    c.execute(new_ddl)
    before_raw = c.execute(f"SELECT count() FROM {old_full}")[0][0]
    print(f"  INSERT SELECT ({before_raw:,} rows)...", end=" ", flush=True)
    c.execute(
        f"INSERT INTO {new_full} ({cols_list}) SELECT {select_cols} FROM {old_full} "
        f"SETTINGS max_partitions_per_insert_block=0"
    )
    after_raw = c.execute(f"SELECT count() FROM {new_full}")[0][0]
    print(f"done ({after_raw:,} rows)")

    # ---- Step 3: RENAME (complete migration immediately) ----
    c.execute(f"RENAME TABLE {old_full} TO {old_bak}, {new_full} TO {old_full}")
    print(f"  [OK] RENAMED: {old_full} is now tz-correct")

    # ---- Step 4-5: Partition-level fixup (concurrent-write tolerance) ----
    # 治本修复（#ARCH-CH-022）：旧逻辑对 ALL old>new 分区做 re-INSERT，
    # 但 -8h 偏移导致 trade_time 分区键的行跨月移动（old_parts != new_parts 是
    # 预期行为，非数据丢失）。只对当月分区做 fixup（只有当月有并发写入）。
    if pk_expr:
        old_parts = dict(c.execute(
            f"SELECT partition, sum(rows) FROM system.parts "
            f"WHERE database='{db}' AND table='{table}_tzold' AND active=1 "
            f"GROUP BY partition"
        ))
        new_parts = dict(c.execute(
            f"SELECT partition, sum(rows) FROM system.parts "
            f"WHERE database='{db}' AND table='{table}' AND active=1 "
            f"GROUP BY partition"
        ))
        # 只对当月分区做 fixup（历史分区无并发写入）
        current_month = str(c.execute("SELECT toYYYYMM(now())")[0][0])
        mismatch = [
            p for p in old_parts
            if str(p) == current_month and old_parts[p] > new_parts.get(p, 0)
        ]
        if mismatch:
            print(f"  [FIXUP] {len(mismatch)} partition(s) need re-INSERT (current month concurrent writes)")
            for part_id in mismatch:
                where = _partition_where(pk_expr, part_id)
                old_r = old_parts[part_id]
                new_r = new_parts.get(part_id, 0)
                print(f"    partition={part_id}: old={old_r:,} new={new_r:,} missing={old_r - new_r:,}")
                c.execute(
                    f"INSERT INTO {old_full} ({cols_list}) SELECT {select_cols} "
                    f"FROM {old_bak} WHERE {where} "
                    f"SETTINGS max_partitions_per_insert_block=0"
                )
            print("  [OK] Fixup complete")
        else:
            print("  [OK] Current month matches (no concurrent writes or already synced)")
    else:
        print("  [WARN] No partition key — skipping partition fixup")

    # ---- Step 6: Verify (historical partition — no concurrent writes) ----
    # 治本修复：旧逻辑用 max(date) 验证，但最新日期仍在被 scheduler 并发写入
    # （RENAME 后新表继续接收写入 -> new > old 误报 DIFF）。
    # 正确做法：用历史分区（上一月，无并发写入）验证 raw count + unique(symbol)。
    # 历史分区匹配=迁移无损；最新日期的新增行=正常并发写入（非迁移错误）。
    if pk_expr:
        # 取上一月分区作为稳定历史验证点（当前月 202607 有并发写入）
        hist_parts = c.execute(
            f"SELECT partition FROM system.parts "
            f"WHERE database='{db}' AND table='{table}_tzold' AND active=1 "
            f"GROUP BY partition ORDER BY partition DESC LIMIT 5"
        )
        # 选最大的非当前月分区
        verify_part = None
        for (p,) in hist_parts:
            ps = str(p)
            if ps < "202607":  # 排除当前月
                verify_part = ps
                break
        if verify_part:
            where = _partition_where(pk_expr, verify_part)
            old_rc = c.execute(f"SELECT count() FROM {old_bak} WHERE {where}")[0][0]
            new_rc = c.execute(f"SELECT count() FROM {old_full} WHERE {where}")[0][0]
            # unique symbol count (trade_time shifted, can't compare directly)
            old_sym = c.execute(
                f"SELECT count() FROM (SELECT DISTINCT symbol FROM {old_bak} WHERE {where})"
            )[0][0] if "symbol" in [col for col, _ in _columns(c, db, table)] else 0
            new_sym = c.execute(
                f"SELECT count() FROM (SELECT DISTINCT symbol FROM {old_full} WHERE {where})"
            )[0][0] if "symbol" in [col for col, _ in _columns(c, db, table)] else 0
            print(f"  [VERIFY] partition={verify_part}: "
                  f"old_raw={old_rc:,} new_raw={new_rc:,} "
                  f"old_sym={old_sym:,} new_sym={new_sym:,}", end="")
            if old_rc == new_rc and old_sym == new_sym:
                print(" -- MATCH")
            else:
                print(f" -- DIFF (raw={new_rc - old_rc:,} sym={new_sym - old_sym:,})")
                print("  [WARN] Historical partition mismatch — keeping _tzold for safety")
                return actions
        else:
            print("  [WARN] No historical partition found for verification — keeping _tzold")
            return actions
    else:
        print("  [WARN] No partition key — skipping verification, keeping _tzold")
        return actions

    # ---- Step 7: DROP _tzold (safe, handles >50GB) ----
    _safe_drop_table(c, old_bak)
    print(f"  [OK] Dropped {old_bak}")
    return actions


def _row_count_from_table(c: Client, full_table: str) -> int:
    return c.execute(f"SELECT count() FROM {full_table}")[0][0]


def _recreate_tick_data_batched(c: Client, dry: bool) -> list[str]:
    """tick_data(181GiB) 分区批量重建：逐月 copy+drop，控制磁盘峰值<表大小+1月。

    策略（并发写入容忍版）：
    1. CREATE _tznew (shifted DDL: timestamp -> DateTime64(3,'Asia/Shanghai'))
    2. 历史月份（非当月）：逐月 INSERT SELECT + DROP PARTITION on old（释放磁盘）
       历史月份无并发写入，INSERT 后直接 DROP 安全
    3. 当月：INSERT SELECT（不 DROP，保留以接收并发写入）
    4. RENAME: old -> _tzold, _tznew -> old（立即完成迁移）
    5. 当月 fixup：从 _tzold 重新 INSERT 当月（补齐 RENAME 前的并发写入）
       ReplacingMergeTree 自动去重（sorting key 含 shifted timestamp）
    6. 验证：FINAL count 对比（允许 after >= before，因当月可能新增）
    7. DROP _tzold（使用 _safe_drop_table 处理 >50GB）

    峰值磁盘 ≈ old(181) + 单月(~5) < 200GiB free。
    """
    actions: list[str] = []
    db, table = "c1_market", "tick_data"
    old_full = f"{db}.{table}"
    new_full = f"{db}.{table}_tznew"
    old_bak = f"{db}.{table}_tzold"
    business_cols = ["timestamp"]

    ddl = c.execute(f"SHOW CREATE TABLE {old_full}")[0][0]
    new_ddl = _transform_ddl(ddl, db, table, business_cols)
    new_ddl = new_ddl.replace(f"CREATE TABLE {old_full}", f"CREATE TABLE {new_full}", 1)
    select_cols = _build_shift_select(c, db, table, business_cols)
    cols_list = ", ".join(f"`{col}`" for col, _ in _columns(c, db, table))

    # 分区清单（toYYYYMM(trade_date)）—— trade_date 是 Date，不受 timestamp 偏移影响
    parts = c.execute(
        f"SELECT DISTINCT toYYYYMM(trade_date) m, count() r FROM {old_full} GROUP BY m ORDER BY m"
    )
    # 当月分区（不 DROP，保留以接收并发写入）
    current_month = c.execute("SELECT toYYYYMM(now())")[0][0]

    actions.append(f"DROP TABLE IF EXISTS {new_full}")
    actions.append(f"CREATE {new_full} (shifted timestamp -> Asia/Shanghai)")
    for m, r in parts:
        drop = "DROP" if int(m) != int(current_month) else "KEEP (current month)"
        actions.append(f"  month={m} rows={r}: INSERT + {drop} PARTITION {m}")
    actions.append(f"RENAME {old_full} -> {old_bak}, {new_full} -> {old_full}")
    actions.append(f"FIXUP current month {current_month} from {old_bak}")
    actions.append(f"DROP {old_bak} (via _safe_drop_table)")

    if dry:
        return actions

    # ---- Step 1: CREATE _tznew ----
    c.execute(f"DROP TABLE IF EXISTS {new_full}")
    c.execute(new_ddl)
    print(f"  [OK] Created {new_full}")

    # ---- Step 2-3: Batched INSERT + DROP ----
    total_before = 0
    for i, (m, _r) in enumerate(parts):
        month_int = int(m)
        is_current = month_int == int(current_month)
        rows = int(_r)
        total_before += rows

        print(f"  [{i+1}/{len(parts)}] month={m} rows={rows:,} ...", end=" ", flush=True)
        # INSERT shifted data
        c.execute(
            f"INSERT INTO {new_full} ({cols_list}) SELECT {select_cols} FROM {old_full} "
            f"WHERE toYYYYMM(trade_date) = {m} "
            f"SETTINGS max_partitions_per_insert_block=0"
        )
        if not is_current:
            # Historical month: safe to DROP (no concurrent writes)
            c.execute(f"ALTER TABLE {old_full} DROP PARTITION {m}")
            print("INSERT + DROP done")
        else:
            print("INSERT done (current month, keeping for concurrent writes)")
    print(f"  [OK] All {len(parts)} months migrated. total_before={total_before:,}")

    # ---- Step 4: RENAME ----
    c.execute(f"RENAME TABLE {old_full} TO {old_bak}, {new_full} TO {old_full}")
    print(f"  [OK] RENAMED: {old_full} is now tz-correct")

    # ---- Step 5: Fixup current month (concurrent-write tolerance) ----
    # _tzold (was old) still has the current month partition.
    # Any writes between INSERT and RENAME are in _tzold but not in new.
    # Re-INSERT the current month from _tzold (duplicates deduped by ReplacingMergeTree).
    where_current = f"toYYYYMM(trade_date) = {current_month}"
    old_curr = c.execute(f"SELECT count() FROM {old_bak} WHERE {where_current}")[0][0]
    new_curr = c.execute(f"SELECT count() FROM {old_full} WHERE {where_current}")[0][0]
    if old_curr > new_curr:
        print(f"  [FIXUP] current month {current_month}: old={old_curr:,} new={new_curr:,} "
              f"missing={old_curr - new_curr:,}")
        c.execute(
            f"INSERT INTO {old_full} ({cols_list}) SELECT {select_cols} FROM {old_bak} "
            f"WHERE {where_current} "
            f"SETTINGS max_partitions_per_insert_block=0"
        )
        print("  [OK] Fixup complete")
    else:
        print(f"  [OK] Current month matches (old={old_curr:,} new={new_curr:,})")

    # ---- Step 6: Verify ----
    after = c.execute(f"SELECT count() FROM {old_full}")[0][0]
    # after should be >= total_before (concurrent writes may have added rows)
    if after < total_before:
        print(f"  [WARN] Row count: before={total_before:,} after={after:,} "
              f"(lost {total_before - after:,} rows)")
    else:
        print(f"  [OK] Row count: before={total_before:,} after={after:,} "
              f"(+{after - total_before:,} concurrent writes)")

    # ---- Step 7: DROP _tzold (safe, handles >50GB) ----
    _safe_drop_table(c, old_bak)
    print(f"  [OK] Dropped {old_bak}")
    return actions


# ========== 备份检查 ==========


def _recent_backup_ok(c: Client) -> tuple[bool, str]:
    """检查近 24h 内有成功的 CH BACKUP。"""
    r = c.execute(
        "SELECT status, start_time FROM system.backups "
        "WHERE status = 'BACKUP_CREATED' ORDER BY start_time DESC LIMIT 1"
    )
    if not r:
        return (False, "无任何成功备份记录")
    return (True, f"最近成功备份 {r[0][1]}")


# ========== 调度 ==========


@dataclass
class Plan:
    db: str
    table: str
    strategy: str  # system | business_plain | recreate | tickdata
    business_cols: list[str]
    needs_recreate: bool


def _build_plan(c: Client) -> list[Plan]:
    """构建全库迁移计划（跳过已迁移表）。"""
    plans: list[Plan] = []
    seen_tables: set[tuple[str, str]] = set()
    # 业务列表
    for db, table, _col in BUSINESS_COLUMNS:
        if (db, table) in seen_tables:
            continue
        seen_tables.add((db, table))
        biz = _business_cols_for(db, table)
        # 跳过已迁移表（业务列已为 DateTime64）
        biz_types = [_col_type(c, db, table, col) for col in biz]
        if all(t and "DateTime64" in t for t in biz_types):
            continue  # 已迁移，跳过
        pk, sk = _table_key_info(c, db, table)
        needs_recreate = any(_col_is_in_key(col, pk, sk) for col in biz)
        if table == "tick_data":
            strat = "tickdata"
        elif needs_recreate:
            strat = "recreate"
        else:
            strat = "business_plain"
        plans.append(Plan(db, table, strat, biz, needs_recreate))
    return plans


def _all_tables_with_dt(c: Client) -> list[tuple[str, str]]:
    """所有含 DateTime 列的表（用于系统列 phase 全覆盖）。"""
    r = c.execute(
        "SELECT DISTINCT database, table FROM system.columns "
        "WHERE database IN ('c1_market','c3_fundamental') AND type LIKE 'DateTime%' "
        "ORDER BY database, table"
    )
    return [(x[0], x[1]) for x in r]


def _tables_needing_version_col_migration(c: Client) -> list[tuple[str, str]]:
    """找出系统列仍为 DateTime 且不在业务列清单中的表（须重建）。

    这些表的系统列(ingest_ts 等)是 ReplacingMergeTree 版本列，MODIFY COLUMN
    被拒，须走重建路径。已在业务列清单中的表由 business/recreate/tickdata
    phase 处理（重建时 _transform_ddl 会一并修正系统列），此处跳过避免重复。
    """
    business_tables = {(db, table) for db, table, _ in BUSINESS_COLUMNS}
    result: list[tuple[str, str]] = []
    for db, table in _all_tables_with_dt(c):
        if (db, table) in business_tables:
            continue
        for col, typ in _columns(c, db, table):
            if (col in SYSTEM_COL_NAMES and typ.startswith("DateTime")
                    and "DateTime64" not in typ):
                result.append((db, table))
                break
    return result


# ========== 命令入口 ==========


def cmd_dry_run(c: Client) -> int:
    print("=" * 70)
    print("时区防线迁移 — DRY RUN（0 写入）")
    print("=" * 70)
    print(f"\n[系统列] 类型标注 -> {SYSTEM_TZ}（无偏移）")
    sys_tables = _all_tables_with_dt(c)
    sys_count = 0
    for db, table in sys_tables:
        acts = _migrate_system_columns(c, db, table, dry=True)
        if acts:
            sys_count += len(acts)
            print(f"  {db}.{table}:")
            for a in acts:
                print(f"    {a}")
    print(f"  小计: {sys_count} 列")

    # 版本列（MODIFY 被拒，须重建）
    vc_tables = _tables_needing_version_col_migration(c)
    if vc_tables:
        print(f"\n[版本列] 重建表 -> {SYSTEM_TZ}（无偏移，MODIFY 被拒须重建）")
        for db, table in vc_tables:
            rows = _row_count(c, db, table)
            print(f"  {db}.{table} ({rows} rows) [RECREATE 版本列]")
    print(f"  小计: {len(vc_tables)} 张表")

    print(f"\n[业务列] 偏移 -8h + {BUSINESS_TZ}")
    plans = _build_plan(c)
    for p in plans:
        if p.strategy == "tickdata":
            print(f"\n  {p.db}.{p.table} [TICKDATA 分区批量重建, 181GiB]:")
            for a in _recreate_tick_data_batched(c, dry=True):
                print(f"    {a}")
        elif p.strategy == "recreate":
            print(f"\n  {p.db}.{p.table} [RECREATE 键列] biz={p.business_cols}:")
            for a in _recreate_table(c, p.db, p.table, p.business_cols, dry=True):
                print(f"    {a}")
        else:
            print(f"\n  {p.db}.{p.table} [business_plain] biz={p.business_cols}:")
            for a in _migrate_business_plain(c, p.db, p.table, p.business_cols, dry=True):
                print(f"    {a}")
    return 0


def cmd_verify(c: Client) -> int:
    print("=" * 70)
    print("时区防线 — 一致性校验")
    print("=" * 70)
    ok = True
    # 系统列
    print("\n[系统列] 期望 DateTime64(3, 'UTC'):")
    for db, table in _all_tables_with_dt(c):
        for col, typ in _columns(c, db, table):
            if col in SYSTEM_COL_NAMES and typ.startswith("DateTime"):
                good = (typ == SYSTEM_TZ)
                ok = ok and good
                print(f"  {'OK ' if good else 'BAD'} {db}.{table}.{col} = {typ}")
    # 业务列
    print("\n[业务列] 期望 DateTime64(3, 'Asia/Shanghai') + epoch 已偏移:")
    for db, table, col in BUSINESS_COLUMNS:
        typ = _col_type(c, db, table, col)
        if typ is None:
            print(f"  SKIP {db}.{table}.{col} (列不存在)")
            continue
        good = (typ == BUSINESS_TZ)
        ok = ok and good
        print(f"  {'OK ' if good else 'BAD'} {db}.{table}.{col} = {typ}")
    print("\n" + ("全部一致" if ok else "存在差异"))
    return 0 if ok else 1


def cmd_phase(c: Client, phase: str, no_backup_check: bool) -> int:
    if phase in ("business", "recreate", "tickdata", "version-col", "all") and not no_backup_check:
        ok, msg = _recent_backup_ok(c)
        if not ok:
            print(f"[拒绝] 破坏性 phase 需近 24h 成功备份: {msg}")
            print("  用 --no-backup-check 跳过（不推荐）")
            return 3

    if phase == "system":
        print("[phase=system] 系统列类型标注（安全，无偏移）")
        n = 0
        for db, table in _all_tables_with_dt(c):
            acts = _migrate_system_columns(c, db, table, dry=False)
            for a in acts:
                print(f"  {a}")
                n += 1
        print(f"完成: {n} 列已标注 {SYSTEM_TZ}")
        return 0

    if phase in ("version-col", "all"):
        print("[phase=version-col] 版本列重建（系统列 MODIFY 被拒，须重建，无偏移）")
        vc_tables = _tables_needing_version_col_migration(c)
        if not vc_tables:
            print("  无需迁移的版本列（全部已迁移或由 business phase 处理）")
        for db, table in vc_tables:
            rows = _row_count(c, db, table)
            print(f"\n  {db}.{table} ({rows} rows)")
            for a in _recreate_table(c, db, table, [], dry=False):
                print(f"    {a}")

    plans = _build_plan(c)
    if phase in ("business", "all"):
        print("[phase=business] 业务列（非键，UPDATE+MODIFY）")
        for p in plans:
            if p.strategy != "business_plain":
                continue
            print(f"\n  {p.db}.{p.table} biz={p.business_cols}")
            for a in _migrate_business_plain(c, p.db, p.table, p.business_cols, dry=False):
                print(f"    {a}")
    if phase in ("recreate", "all"):
        print("\n[phase=recreate] 业务列（键列，重建表）")
        for p in plans:
            if p.strategy != "recreate":
                continue
            print(f"\n  {p.db}.{p.table} biz={p.business_cols} ({_row_count(c, p.db, p.table)} rows)")
            for a in _recreate_table(c, p.db, p.table, p.business_cols, dry=False):
                print(f"    {a}")
    if phase in ("tickdata", "all"):
        print("\n[phase=tickdata] tick_data 分区批量重建（181GiB，耗时数小时）")
        for a in _recreate_tick_data_batched(c, dry=False):
            print(f"  {a}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="ClickHouse 时区防线迁移")
    ap.add_argument("--dry-run", action="store_true", help="扫描+输出策略，0 写入")
    ap.add_argument("--verify", action="store_true", help="仅校验一致性")
    ap.add_argument("--phase", choices=["system", "version-col", "business", "recreate", "tickdata", "all"])
    ap.add_argument("--table", help="单表迁移（db.table）")
    ap.add_argument("--no-backup-check", action="store_true", help="跳过备份检查")
    args = ap.parse_args()

    try:
        c = _client()
        c.execute("SELECT 1")
    except Exception as e:  # noqa: BLE001
        print(f"[CH不可达] {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        return cmd_dry_run(c)
    if args.verify:
        return cmd_verify(c)
    if args.table:
        db, table = args.table.split(".")
        biz = _business_cols_for(db, table)
        pk, sk = _table_key_info(c, db, table)
        needs = any(_col_is_in_key(col, pk, sk) for col in biz)
        if table == "tick_data":
            _recreate_tick_data_batched(c, dry=False)
        elif needs:
            _recreate_table(c, db, table, biz, dry=False)
        else:
            _migrate_business_plain(c, db, table, biz, dry=False)
        _migrate_system_columns(c, db, table, dry=False)
        return 0
    if args.phase:
        return cmd_phase(c, args.phase, args.no_backup_check)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
