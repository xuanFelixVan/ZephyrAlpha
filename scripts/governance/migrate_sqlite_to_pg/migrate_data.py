#!/usr/bin/env python3
# [A_module] module_id=MOD-migrate_sqlite_to_pg | layer=module | stability=stable | safety=H | ai_autonomy=human_gated

# [BLUEPRINT] MOD-migrate_sqlite_to_pg | docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md | §migrate_data
# [MODULE] scripts.governance.migrate_sqlite_to_pg.migrate_data
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); scripts.governance._shared.constants (EXIT codes); psycopg2
# [CONSUMERS] manual（一次性迁移运维脚本）; tests/governance/test_migrate_sqlite_to_pg.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 每表独立事务(BEGIN;DELETE;INSERT;VERIFY;COMMIT per table，一表失败不影响已提交表);触发器恢复在 finally 中保证执行;migration_log 幂等标记(已完成则跳过);YAML 真源种子表不在此迁移(见 seed_from_yaml.py);SQL 集中化(全部 SQL 唯一声明点在模块级 SQL_* 常量，§5.160.2)
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] exit 0=全部表迁移成功或已完成跳过; exit 1=存在失败表/连接失败/前置条件缺失
# [TESTS] tests/governance/test_migrate_sqlite_to_pg.py
# [TTL] task_bound
"""
SQLite → PostgreSQL 运营数据迁移脚本
====================================
将 depgraph.db 的运营数据表迁移到 PostgreSQL。

使用方式:
    python scripts/governance/migrate_sqlite_to_pg/migrate_data.py
    python scripts/governance/migrate_sqlite_to_pg/migrate_data.py --force  # 已完成也强制重跑

前置条件:
    1. PostgreSQL 已启动（Windows 服务运行中）
    2. PG Schema 已创建（01_create_extensions.sql + 02_create_pg_schema.sql 已执行）
    3. depgraph.db 已备份（破坏性操作前三步验证：必要性/真实性/可逆性）
    4. YAML 真源种子表已由 seed_from_yaml.py 灌入（种子表真源在 YAML，不在 SQLite）

退出码:
    0 = 全部表迁移成功（或 migration_log 已完成跳过）
    1 = 存在失败表或异常

设计要点（5.32.2/5.32.4/5.32.10 治本）:
    * 每表独立事务：DELETE+INSERT+VERIFY+COMMIT per table，单表失败 ROLLBACK
      仅影响该表，已提交表数据不受损（治本原单大事务中途失败数据全损）
    * 触发器/FK 通过 session_replication_role='replica' 禁用（session 级设置，
      跨 commit 持续有效），恢复 'origin' 在 finally 中保证执行
    * migration_log 幂等标记：迁移前检查是否已完成（已完成跳过+提示），
      完成后写入记录（completed/partial），重跑不再全清数据
    * 种子表（domains/gates/registries 等 YAML 真源只读表）已拆分到
      seed_from_yaml.py——真源在 YAML（trae_062），从 SQLite 搬旧缓存=搬漂移
    * SQL 集中化：全部 SQL 唯一声明点在模块级 SQL_* 常量（§5.160.2，
      NO-BARE-SQL 门禁），函数体内禁止 SQL 字面量
    * 6 张 IDENTITY 列表用 OVERRIDING SYSTEM VALUE 保持原主键值
    * 迁移后重置 IDENTITY 序列到 MAX(col)+1
    * psycopg2.extras.execute_values 批量插入（性能远高于逐行 executemany）
"""

__manifest__ = """
args: []
description: SQLite → PostgreSQL 运营数据迁移脚本（每表独立事务+migration_log幂等）
dimensions:
- D1
priority: P2
timeout_seconds: 120
warn_only: false
"""


import argparse
import json
import os
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

# Bootstrap: 基于 .git marker 定位仓库根（文件移动不 break，替代 parents[N] 硬编码）
_PROJECT_ROOT = Path(__file__).resolve()
while not (_PROJECT_ROOT / ".git").exists() and _PROJECT_ROOT.parent != _PROJECT_ROOT:
    _PROJECT_ROOT = _PROJECT_ROOT.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓库根真源（SSoT）

# === 路径常量 ===
SQLITE_PATH = str(REPO_ROOT / "data" / "databases" / "depgraph.db")
ENV_PATH = str(REPO_ROOT / "config" / ".env.postgres")

# === 幂等标记（5.32.4 治本） ===
MIGRATION_ID = "sqlite_to_pg_operational_v1"
MIGRATION_LOG_TABLE = "migration_log"

# === SQL 集中化（§5.160.2：全部 SQL 唯一声明点在此，NO-BARE-SQL 门禁豁免 SQL_* 常量定义） ===
SQL_SET_REPLICATION_REPLICA = "SET session_replication_role = 'replica';"
SQL_SET_REPLICATION_ORIGIN = "SET session_replication_role = 'origin';"
SQL_SELECT_IDENTITY_COLS = """
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND is_identity = 'YES'
    ORDER BY table_name
"""
SQL_CREATE_MIGRATION_LOG = f"""
    CREATE TABLE IF NOT EXISTS {MIGRATION_LOG_TABLE} (
        migration_id  TEXT PRIMARY KEY,
        applied_at    TEXT NOT NULL,
        status        TEXT NOT NULL,
        tables_total  INTEGER NOT NULL DEFAULT 0,
        rows_total    INTEGER NOT NULL DEFAULT 0,
        details       TEXT
    )
"""
SQL_SELECT_MIGRATION_STATUS = f"SELECT status FROM {MIGRATION_LOG_TABLE} WHERE migration_id = %s"
SQL_UPSERT_MIGRATION_LOG = f"""
    INSERT INTO {MIGRATION_LOG_TABLE}
        (migration_id, applied_at, status, tables_total, rows_total, details)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (migration_id) DO UPDATE SET
        applied_at   = EXCLUDED.applied_at,
        status       = EXCLUDED.status,
        tables_total = EXCLUDED.tables_total,
        rows_total   = EXCLUDED.rows_total,
        details      = EXCLUDED.details
"""
# 表名/列清单模板（使用时 .format(...) 填充；含双引号防注入，表名来自 MIGRATION_ORDER 白名单）
SQL_DELETE_ALL_ROWS = 'DELETE FROM "{table}"'
SQL_SELECT_ROW_COUNT = 'SELECT COUNT(*) FROM "{table}"'
SQL_SELECT_ALL_ROWS = 'SELECT {cols} FROM "{table}"'
SQL_INSERT_VALUES = 'INSERT INTO "{table}" ({cols}) VALUES %s'
SQL_INSERT_VALUES_OVERRIDING = 'INSERT INTO "{table}" ({cols}) OVERRIDING SYSTEM VALUE VALUES %s'
SQL_RESET_IDENTITY_SEQ = """
    SELECT setval(
        pg_get_serial_sequence('{tbl}', '{col}'),
        GREATEST(COALESCE((SELECT MAX("{col}") FROM "{tbl}"), 0) + 1, 1),
        false
    )
"""

# === YAML 真源种子表（5.32.10 治本：不在此迁移，由 seed_from_yaml.py 从 YAML 灌入） ===
# 真源分类铁律（trae_062）：规则数据真源在 YAML 文件，DB 是只读缓存。
# 从 SQLite 旧缓存搬这些数据 = 搬漂移；应从 YAML 真源灌入。
# 同步能力唯一真源：scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py
SEED_TABLES = frozenset(
    [
        "domains",
        "arch_constraints",
        "arch_directory_tree",
        "arch_path_mappings",
        "blueprint_links",
        "business_streams",
        "contracts",
        "cross_registry_rules",
        "derived_identifier_registry",
        "domain_naming_rules",
        "field_vocabularies",
        "gates",
        "hard_boundaries",
        "infrastructure_components",
        "model_capabilities",
        "registries",
    ]
)

# === 迁移顺序（运营数据，按外键依赖拓扑排序） ===
# 注意：nodes.domain_id 等 FK 引用种子表 domains——seed_from_yaml.py 必须先于
# 本脚本执行（README 执行顺序节）；迁移期间 session_replication_role='replica'
# 亦会禁用 FK RI 触发器作为兜底。
MIGRATION_ORDER = [
    # 层 0: 无 FK 依赖的运营表
    "_schema_version",
    "domain_mapping",
    "governance_audit_logs",
    "nodes_archive_module_lifecycle",
    # 层 1: nodes（被 edges 引用）
    "nodes",
    # 层 2: 依赖 nodes / domains 的运营表
    "domain_dependencies",
    "domain_events",
    "edges",
    "rule_bindings",
]

# === 迁移期间需 DISABLE 触发器的表 ===
# SQLite 未强制 FK，存在脏数据（如历史 contracts.provider_domain 不在 domains 表），
# 迁移时必须禁用 FK 触发器，否则会报 ForeignKeyViolation。
# 迁移后 ENABLE（finally 中保证）重新启用所有约束。
DISABLE_TRIGGER_TABLES = MIGRATION_ORDER[:]


def load_env(path):
    """从 .env.postgres 文件加载连接参数。"""
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def get_identity_columns(pg_conn):
    """查询 PG 中所有 IDENTITY 列，返回 {table_name: column_name}。"""
    identity_cols = {}
    with pg_conn.cursor() as cur:
        cur.execute(SQL_SELECT_IDENTITY_COLS)
        for row in cur:
            identity_cols[row[0]] = row[1]
    return identity_cols


def disable_all_triggers(pg_conn):
    """禁用所有触发器和 FK 约束（需超级用户权限）。

    用 SET session_replication_role = 'replica' 实现（session 级设置，
    跨 commit 持续有效——每表独立事务提交后触发器仍处于禁用态）：
      - 禁用所有用户触发器（含只读保护）
      - 禁用 FK RI 系统触发器（绕过脏数据）
      - 禁用规则

    注意：必须用超级用户（如 postgres）连接，普通用户无权修改 replication_role。
    """
    with pg_conn.cursor() as cur:
        cur.execute(SQL_SET_REPLICATION_REPLICA)
    pg_conn.commit()
    print("[SETUP] 已设置 session_replication_role=replica（禁用所有触发器和 FK）")


def enable_all_triggers(pg_conn):
    """恢复触发器和 FK 约束。在 finally 中调用，保证执行。"""
    with pg_conn.cursor() as cur:
        cur.execute(SQL_SET_REPLICATION_ORIGIN)
    pg_conn.commit()
    print("[CLEANUP] 已恢复 session_replication_role=origin（启用所有触发器和 FK）")


# === migration_log 幂等标记（5.32.4 治本） ===


def ensure_migration_log_table(pg_conn):
    """创建 migration_log 表（若不存在）。"""
    with pg_conn.cursor() as cur:
        cur.execute(SQL_CREATE_MIGRATION_LOG)
    pg_conn.commit()


def migration_already_completed(pg_conn, migration_id):
    """检查指定迁移是否已完成（status='completed'）。partial 不视为完成，允许重跑。"""
    with pg_conn.cursor() as cur:
        cur.execute(SQL_SELECT_MIGRATION_STATUS, (migration_id,))
        row = cur.fetchone()
    return bool(row and row[0] == "completed")


def record_migration_result(pg_conn, migration_id, status, report):
    """写入迁移记录（completed/partial）。ON CONFLICT 更新，保证重跑可覆盖。"""
    applied_at = datetime.now(UTC).isoformat()
    rows_total = sum(c for _, c, s, _ in report if s == "ok")
    details = json.dumps(
        [{"table": t, "rows": c, "status": s, "error": e} for t, c, s, e in report],
        ensure_ascii=False,
    )
    with pg_conn.cursor() as cur:
        cur.execute(
            SQL_UPSERT_MIGRATION_LOG,
            (migration_id, applied_at, status, len(report), rows_total, details),
        )
    pg_conn.commit()
    print(f"[LOG] migration_log 已记录: {migration_id} status={status} tables={len(report)} rows={rows_total}")


def migrate_table(sqlite_conn, pg_conn, table_name, identity_cols):
    """迁移单张表（5.32.2 治本：每表独立事务）。

    事务边界：DELETE（清残留保证幂等）→ INSERT → VERIFY 行数 → COMMIT。
    任一步失败抛异常，由 migrate_all_tables 捕获并 ROLLBACK——仅影响本表，
    已提交的其他表数据不受损。

    返回 (sqlite_count, pg_count)。
    """
    # 1. 从 SQLite 获取列名
    pragma_rows = sqlite_conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    cols = [r[1] for r in pragma_rows]
    if not cols:
        raise RuntimeError(f"表 {table_name} 在 SQLite 中不存在或无列")
    col_list = ", ".join(f'"{c}"' for c in cols)

    # 2. 读取 SQLite 数据
    rows = sqlite_conn.execute(SQL_SELECT_ALL_ROWS.format(cols=col_list, table=table_name)).fetchall()
    data = [tuple(r) for r in rows]
    sqlite_count = len(data)

    # 3. 构造 INSERT SQL（IDENTITY 列需 OVERRIDING SYSTEM VALUE 保持原主键值）
    if table_name in identity_cols:
        insert_sql = SQL_INSERT_VALUES_OVERRIDING.format(cols=col_list, table=table_name)
    else:
        insert_sql = SQL_INSERT_VALUES.format(cols=col_list, table=table_name)

    # 4. 单表事务：DELETE 清残留 → 批量写入 → 行数校验 → COMMIT
    with pg_conn.cursor() as cur:
        cur.execute(SQL_DELETE_ALL_ROWS.format(table=table_name))
        if data:
            execute_values(cur, insert_sql, data, page_size=500)
        cur.execute(SQL_SELECT_ROW_COUNT.format(table=table_name))
        pg_count = cur.fetchone()[0]
    if pg_count != sqlite_count:
        raise RuntimeError(f"表 {table_name} 行数校验失败: SQLite={sqlite_count} PG={pg_count}")
    pg_conn.commit()
    print(f"  [{table_name:<45}] {sqlite_count:>6} 行已写入并提交")
    return sqlite_count, pg_count


def migrate_all_tables(sqlite_conn, pg_conn, tables, identity_cols):
    """逐表独立事务迁移。一表失败仅 ROLLBACK 该表，继续后续表。

    返回 report: [(table, sqlite_count, status, error)]，
    status: 'ok' / 'failed'（sqlite_count 失败时为 -1）。
    """
    report = []
    for tbl in tables:
        try:
            sqlite_count, _ = migrate_table(sqlite_conn, pg_conn, tbl, identity_cols)
            report.append((tbl, sqlite_count, "ok", ""))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            pg_conn.rollback()
            print(f"  [{tbl:<45}] FAILED: {e}（本表已回滚，不影响已提交表）")
            report.append((tbl, -1, "failed", str(e)))
    return report


def reset_identity_sequences(pg_conn, identity_cols, tables):
    """重置已迁移表的 IDENTITY 序列到 MAX(col)，确保后续 INSERT 不冲突。"""
    reset_count = 0
    with pg_conn.cursor() as cur:
        for tbl, col in identity_cols.items():
            if tbl not in tables:
                continue
            cur.execute(SQL_RESET_IDENTITY_SEQ.format(tbl=tbl, col=col))
            reset_count += 1
    pg_conn.commit()
    print(f"[RESET] 已重置 {reset_count} 个 IDENTITY 序列")


def run_migration(sqlite_conn, pg_conn, tables=None, migration_id=MIGRATION_ID, force=False):
    """完整迁移流程（可注入连接，便于测试）。

    流程：ensure migration_log → 已完成检查（跳过）→ 禁用触发器
    → try: 逐表独立事务迁移 → finally: 恢复触发器（保证执行）
    → 重置序列 → 写 migration_log → 返回退出码。

    返回 0=全部成功或已完成跳过，1=存在失败表。
    """
    tables = list(tables) if tables is not None else MIGRATION_ORDER[:]

    # 1. 幂等检查（5.32.4：已完成则跳过+提示，重跑不再全清数据）
    ensure_migration_log_table(pg_conn)
    if not force and migration_already_completed(pg_conn, migration_id):
        print(f"[SKIP] 迁移 {migration_id} 已完成（migration_log 记录存在），跳过。如需重跑请使用 --force")
        return EXIT_PASS

    # 2. 获取 IDENTITY 列信息
    identity_cols = get_identity_columns(pg_conn)
    print(f"[INFO] IDENTITY 列: {identity_cols}")

    # 3. 禁用触发器 → 逐表迁移 → finally 恢复触发器（5.32.2：保证执行）
    disable_all_triggers(pg_conn)
    try:
        print("\n=== 数据迁移开始（每表独立事务） ===")
        report = migrate_all_tables(sqlite_conn, pg_conn, tables, identity_cols)
    finally:
        enable_all_triggers(pg_conn)

    # 4. 重置 IDENTITY 序列
    reset_identity_sequences(pg_conn, identity_cols, set(tables))

    # 5. 汇总 + 写 migration_log
    failed = [r for r in report if r[2] == "failed"]
    status = "completed" if not failed else "partial"
    record_migration_result(pg_conn, migration_id, status, report)

    total_rows = sum(c for _, c, s, _ in report if s == "ok")
    print("\n=== 迁移完成 ===")
    print(f"总表数: {len(report)}（成功 {len(report) - len(failed)} / 失败 {len(failed)}）")
    print(f"总行数: {total_rows}")
    if failed:
        print(f"失败表: {[t for t, _, _, _ in failed]}（已回滚，可修复后重跑）")
    return EXIT_PASS if not failed else EXIT_FINDINGS


def main():
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="SQLite → PostgreSQL 运营数据迁移")
    parser.add_argument(
        "--force",
        action="store_true",
        help="忽略 migration_log 已完成记录，强制重跑（每表事务保证重跑幂等）",
    )
    args = parser.parse_args()

    # 1. 加载连接配置
    if not os.path.exists(ENV_PATH):
        print(f"ERROR: 环境变量文件不存在: {ENV_PATH}")
        sys.exit(EXIT_FINDINGS)
    env = load_env(ENV_PATH)

    if not os.path.exists(SQLITE_PATH):
        print(f"ERROR: SQLite 数据库不存在: {SQLITE_PATH}")
        sys.exit(EXIT_FINDINGS)

    # 2. 连接两个数据库
    # PostgreSQL 连接使用 postgres 超级用户（而非应用用户 zephyr），
    # 因为 SET session_replication_role 需要超级用户权限。
    print(f"[CONNECT] SQLite: {SQLITE_PATH}")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row

    print(
        f"[CONNECT] PostgreSQL (superuser): postgres@{env['POSTGRES_HOST']}:{env['POSTGRES_PORT']}/{env['POSTGRES_DB']}"
    )
    pg_conn = psycopg2.connect(
        host=env["POSTGRES_HOST"],
        port=env["POSTGRES_PORT"],
        dbname=env["POSTGRES_DB"],
        user="postgres",
        password=env["POSTGRES_PASSWORD"],
    )
    pg_conn.autocommit = False

    try:
        exit_code = run_migration(sqlite_conn, pg_conn, force=args.force)
        sys.exit(exit_code)
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        pg_conn.rollback()
        # 失败时尝试重新启用触发器，避免遗留禁用状态
        try:
            enable_all_triggers(pg_conn)
        except psycopg2.Error as trig_err:
            print(f"[WARN] 迁移失败后重新启用触发器失败（可能遗留禁用状态）: {trig_err}")
        print(f"\n[ERROR] 迁移失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(EXIT_FINDINGS)
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
