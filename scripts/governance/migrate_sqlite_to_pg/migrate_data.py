#!/usr/bin/env python3
"""
SQLite → PostgreSQL 数据迁移脚本
================================
将 depgraph.db 的全部 25 张表数据迁移到 PostgreSQL。

使用方式:
    python scripts/governance/migrate_sqlite_to_pg/migrate_data.py

前置条件:
    1. PostgreSQL 已启动（Windows 服务运行中）
    2. PG Schema 已创建（02_create_pg_schema.sql 已执行）
    3. depgraph.db 已备份（.bak.pre_pg_migration_* 文件已生成）

退出码:
    0 = 全部表行数匹配
    1 = 存在不匹配或异常

设计要点:
    * 按外键依赖顺序迁移 25 张表
    * 9 张只读表的 BEFORE INSERT 触发器迁移期间临时 DISABLE，迁移后 ENABLE
    * 6 张 IDENTITY 列表用 OVERRIDING SYSTEM VALUE 保持原主键值
    * 迁移后重置 IDENTITY 序列到 MAX(col)+1
    * psycopg2.extras.execute_values 批量插入（性能远高于逐行 executemany）
    * 迁移结束逐表对比 SQLite/PG 行数
"""

__manifest__ = """
args: []
description: SQLite → PostgreSQL 数据迁移脚本
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import os
import sys
import sqlite3
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

# Bootstrap: 基于 .git marker 定位仓库根（文件移动不 break，替代 parents[N] 硬编码）
_PROJECT_ROOT = Path(__file__).resolve()
while not (_PROJECT_ROOT / ".git").exists() and _PROJECT_ROOT != _PROJECT_ROOT.parent:
    _PROJECT_ROOT = _PROJECT_ROOT.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓库根真源（SSoT）

# === 路径常量 ===
SQLITE_PATH = str(REPO_ROOT / "data" / "databases" / "depgraph.db")
ENV_PATH = str(REPO_ROOT / "config" / ".env.postgres")

# === 迁移顺序（按外键依赖拓扑排序） ===
# 1. 无 FK 依赖的表先迁移
# 2. nodes 在 edges/rule_bindings 之前
# 3. domains 在所有引用它的表之前
MIGRATION_ORDER = [
    # 层 0: 无 FK 依赖
    'domains',
    '_schema_version',
    'arch_directory_tree',
    'blueprint_links',
    'business_streams',
    'cross_registry_rules',
    'derived_identifier_registry',
    'domain_mapping',
    'domain_naming_rules',
    'field_vocabularies',
    'gates',
    'governance_audit_logs',
    'hard_boundaries',
    'infrastructure_components',
    'model_capabilities',
    'nodes_archive_module_lifecycle',
    'registries',
    # 层 1: 依赖 domains
    'arch_constraints',
    'arch_path_mappings',
    'contracts',
    'domain_dependencies',
    'domain_events',
    # 层 2: nodes（被 edges/rule_bindings 引用）
    'nodes',
    # 层 3: 依赖 nodes
    'edges',
    'rule_bindings',
]

# === 迁移期间需 DISABLE 触发器的表 ===
# 包括：
#   1. 9 张只读表（BEFORE INSERT 触发器会阻止数据导入）
#   2. 所有 25 张表（PG 的 FK 约束由内部 RI 触发器实现，DISABLE TRIGGER ALL 可绕过）
# SQLite 未强制 FK，存在脏数据（如 contracts.provider_domain='L00' 不在 domains 表），
# 迁移时必须禁用 FK 触发器，否则会报 ForeignKeyViolation。
# 迁移后 ENABLE TRIGGER ALL 重新启用所有约束。
DISABLE_TRIGGER_TABLES = MIGRATION_ORDER[:]  # 全部 25 张表


def load_env(path):
    """从 .env.postgres 文件加载连接参数。"""
    env = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def get_identity_columns(pg_conn):
    """查询 PG 中所有 IDENTITY 列，返回 {table_name: column_name}。"""
    identity_cols = {}
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND is_identity = 'YES'
            ORDER BY table_name
        """)
        for row in cur:
            identity_cols[row[0]] = row[1]
    return identity_cols


def disable_all_triggers(pg_conn):
    """禁用所有触发器和 FK 约束（需超级用户权限）。

    用 SET session_replication_role = 'replica' 实现：
      - 禁用所有用户触发器（含只读保护）
      - 禁用 FK RI 系统触发器（绕过脏数据）
      - 禁用规则

    必要性：SQLite 未强制 FK，存在脏数据（如 contracts.provider_domain='L00'）；
    PG 强制 FK 会报 ForeignKeyViolation。session_replication_role='replica'
    是 PG 官方推荐的数据迁移/复制模式，迁移后恢复 'origin'。

    注意：必须用超级用户（如 postgres）连接，普通用户无权修改 replication_role。
    """
    with pg_conn.cursor() as cur:
        cur.execute("SET session_replication_role = 'replica';")
    pg_conn.commit()
    print('[SETUP] 已设置 session_replication_role=replica（禁用所有触发器和 FK）')


def enable_all_triggers(pg_conn):
    """恢复触发器和 FK 约束。"""
    with pg_conn.cursor() as cur:
        cur.execute("SET session_replication_role = 'origin';")
    pg_conn.commit()
    print('[CLEANUP] 已恢复 session_replication_role=origin（启用所有触发器和 FK）')


def truncate_all_tables(pg_conn):
    """清空所有表数据（用于失败重试时确保 PG 干净）。

    按反向依赖顺序 TRUNCATE，CASCADE 处理 FK。
    """
    with pg_conn.cursor() as cur:
        # TRUNCATE CASCADE 一次性清空所有表
        tables_sql = ', '.join(f'"{t}"' for t in MIGRATION_ORDER)
        cur.execute(f'TRUNCATE {tables_sql} RESTART IDENTITY CASCADE;')
    pg_conn.commit()
    print(f'[CLEAN] 已 TRUNCATE {len(MIGRATION_ORDER)} 张表（RESTART IDENTITY CASCADE）')


def reset_identity_sequences(pg_conn, identity_cols):
    """重置 IDENTITY 序列到 MAX(col)，确保后续 INSERT 不冲突。"""
    with pg_conn.cursor() as cur:
        for tbl, col in identity_cols.items():
            cur.execute(f"""
                SELECT setval(
                    pg_get_serial_sequence('{tbl}', '{col}'),
                    GREATEST(COALESCE((SELECT MAX("{col}") FROM "{tbl}"), 0) + 1, 1),
                    false
                )
            """)
    pg_conn.commit()
    print(f'[RESET] 已重置 {len(identity_cols)} 个 IDENTITY 序列')


def migrate_table(sqlite_conn, pg_conn, table_name, identity_cols):
    """迁移单张表。返回 (sqlite_count, pg_count_before_commit)。"""
    # 1. 从 SQLite 获取列名
    pragma_rows = sqlite_conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    cols = [r[1] for r in pragma_rows]
    if not cols:
        raise RuntimeError(f'表 {table_name} 在 SQLite 中不存在或无列')
    col_list = ', '.join(f'"{c}"' for c in cols)

    # 2. 读取 SQLite 数据
    rows = sqlite_conn.execute(f'SELECT {col_list} FROM "{table_name}"').fetchall()
    data = [tuple(r) for r in rows]
    sqlite_count = len(data)

    if sqlite_count == 0:
        print(f'  [{table_name:<45}] 0 行（空表，跳过）')
        return 0

    # 3. 构造 INSERT SQL
    # IDENTITY 列需要 OVERRIDING SYSTEM VALUE 保持原主键值
    # execute_values 用单个 %s 占位符自动展开
    if table_name in identity_cols:
        sql = f'INSERT INTO "{table_name}" ({col_list}) OVERRIDING SYSTEM VALUE VALUES %s'
    else:
        sql = f'INSERT INTO "{table_name}" ({col_list}) VALUES %s'

    # 4. 批量写入 PG
    with pg_conn.cursor() as cur:
        execute_values(cur, sql, data, page_size=500)

    print(f'  [{table_name:<45}] {sqlite_count:>6} 行已写入')
    return sqlite_count


def verify_row_counts(sqlite_conn, pg_conn, report):
    """逐表对比 SQLite/PG 行数。返回 all_match 布尔值。"""
    print('\n=== 行数对比校验 ===')
    print(f'{"表名":<45} {"SQLite":>8} {"PG":>8} {"匹配":>6}')
    print('-' * 72)
    all_match = True
    for tbl, sqlite_count in report:
        with pg_conn.cursor() as cur:
            cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
            pg_count = cur.fetchone()[0]
        match = 'OK' if sqlite_count == pg_count else 'FAIL'
        if sqlite_count != pg_count:
            all_match = False
        print(f'{tbl:<45} {sqlite_count:>8} {pg_count:>8} {match:>6}')
    print('-' * 72)
    print(f'结果: {"全部匹配" if all_match else "存在不匹配"}')
    return all_match


def main():
    # 1. 加载连接配置
    if not os.path.exists(ENV_PATH):
        print(f'ERROR: 环境变量文件不存在: {ENV_PATH}')
        sys.exit(EXIT_FINDINGS)
    env = load_env(ENV_PATH)

    if not os.path.exists(SQLITE_PATH):
        print(f'ERROR: SQLite 数据库不存在: {SQLITE_PATH}')
        sys.exit(EXIT_FINDINGS)

    # 2. 连接两个数据库
    # PostgreSQL 连接使用 postgres 超级用户（而非应用用户 zephyr），
    # 因为 SET session_replication_role 需要超级用户权限。
    # 密码与 .env.postgres 中的 POSTGRES_PASSWORD 相同（安装时统一设置）。
    print(f'[CONNECT] SQLite: {SQLITE_PATH}')
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row

    print(f'[CONNECT] PostgreSQL (superuser): postgres@{env["POSTGRES_HOST"]}:{env["POSTGRES_PORT"]}/{env["POSTGRES_DB"]}')
    pg_conn = psycopg2.connect(
        host=env['POSTGRES_HOST'],
        port=env['POSTGRES_PORT'],
        dbname=env['POSTGRES_DB'],
        user='postgres',
        password=env['POSTGRES_PASSWORD'],
    )
    pg_conn.autocommit = False

    try:
        # 3. 获取 IDENTITY 列信息
        identity_cols = get_identity_columns(pg_conn)
        print(f'[INFO] IDENTITY 列: {identity_cols}')

        # 4. 清空 PG 所有表（防止失败重试时残留数据）
        truncate_all_tables(pg_conn)

        # 5. 禁用所有表的触发器（含只读保护和 FK RI 触发器）
        disable_all_triggers(pg_conn)

        # 6. 按顺序迁移所有表
        print('\n=== 数据迁移开始 ===')
        report = []
        for tbl in MIGRATION_ORDER:
            count = migrate_table(sqlite_conn, pg_conn, tbl, identity_cols)
            report.append((tbl, count))

        # 7. 重置 IDENTITY 序列
        reset_identity_sequences(pg_conn, identity_cols)

        # 8. 启用所有表的触发器（含只读保护和 FK 约束）
        enable_all_triggers(pg_conn)

        # 9. 行数对比校验
        all_match = verify_row_counts(sqlite_conn, pg_conn, report)

        # 10. 汇总
        total_rows = sum(c for _, c in report)
        print(f'\n=== 迁移完成 ===')
        print(f'总表数: {len(report)}')
        print(f'总行数: {total_rows}')
        print(f'行数校验: {"PASS" if all_match else "FAIL"}')

        sys.exit(0 if all_match else 1)

    except Exception as e:
        pg_conn.rollback()
        # 失败时尝试重新启用触发器，避免遗留禁用状态
        try:
            enable_all_triggers(pg_conn)
        except psycopg2.Error as trig_err:
            print(f'[WARN] 迁移失败后重新启用触发器失败（可能遗留禁用状态）: {trig_err}')
        print(f'\n[ERROR] 迁移失败: {e}')
        import traceback

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS


        traceback.print_exc()
        sys.exit(EXIT_FINDINGS)
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == '__main__':
    main()
