# -*- coding: utf-8 -*-
"""域ID连字符→下划线迁移脚本（分层分批执行）

用法：
    python migrate_domain_id_hyphen_to_underscore.py --dry-run  # 预览
    python migrate_domain_id_hyphen_to_underscore.py --execute   # 执行

每批传入 DOMAIN_MIGRATIONS 列表，脚本完成：
1. pg_dump 备份（--execute 模式）
2. DB 更新：
   a. 临时 drop 8 个 FK 约束（NO ACTION 阻止子表先更新）
   b. 对 17 个含 domain ID 的 text 列执行 REPLACE(col, old_id, new_id)
   c. recreate 8 个 FK 约束
   d. 单事务 commit
3. 文件替换：.py/.yaml/.yml/.md/.json/.ps1/.csv/.txt/.toml 中的精确域ID替换
4. 验证报告

设计决策：
- 使用 REPLACE(col, old, new) 而非 SET col=new WHERE col=old：
  subdomain_id (D_INFRA_A2A-SUB) 和 target_domains (多值/显示名) 需要嵌入式替换
- FK NO ACTION 约束阻止子表先于 domains PK 更新，故 drop→update→recreate
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT, get_depgraph_pg_connection

# L0 基础设施层（5 域）— 已完成 2026-06-29
# 注: old_id 保留连字符格式作为迁移记录；文件替换会把脚本自身的 D-INFRA_* 改掉，
# 此处用字符串拼接防止自修改（迁移脚本不应被自身修改）
_L0 = "D-INFRA"
L0_MIGRATIONS = [
    (_L0 + "_A2A", "D_INFRA_A2A"),
    (_L0 + "_OPS", "D_INFRA_OPS"),
    (_L0 + "_RECOVERY", "D_INFRA_RECOVERY"),
    (_L0 + "_RUNTIME", "D_INFRA_RUNTIME"),
    (_L0 + "_TELEMETRY", "D_INFRA_TELEMETRY"),
]

# L1 基础层（15 域）
_D = "D-"
L1_MIGRATIONS = [
    (_D + "ALT_DATA", "D_ALT_DATA"),
    (_D + "AUTONOMY_CORE", "D_AUTONOMY_CORE"),
    (_D + "BEHAVIORAL_AUDIT", "D_BEHAVIORAL_AUDIT"),
    (_D + "DATA_ENG", "D_DATA_ENG"),
    (_D + "DATA_GOV", "D_DATA_GOV"),
    (_D + "DATA_SEC", "D_DATA_SEC"),
    (_D + "FRONTEND", "D_FRONTEND"),
    (_D + "INTEGRATION", "D_INTEGRATION"),
    (_D + "INTEGRATION_GATEWAY", "D_INTEGRATION_GATEWAY"),
    (_D + "MKT_DATA", "D_MKT_DATA"),
    (_D + "OPS", "D_OPS"),
    (_D + "REPORTING", "D_REPORTING"),
    (_D + "SECURITY", "D_SECURITY"),
    (_D + "SECURITY_LLM", "D_SECURITY_LLM"),
    (_D + "SHARED", "D_SHARED"),
]

# L2 域层（32 域 + 1 无层 = 33 域）
L2_MIGRATIONS = [
    (_D + "ASHARE_SIGNAL", "D_ASHARE_SIGNAL"),
    (_D + "AUDITTEST", "D_AUDITTEST"),
    (_D + "AUTONOMY_PERM", "D_AUTONOMY_PERM"),
    (_D + "BACKTEST", "D_BACKTEST"),
    (_D + "COMPLIANCE", "D_COMPLIANCE"),
    (_D + "CROSS_ASSET", "D_CROSS_ASSET"),
    (_D + "DIGITAL_TWIN", "D_DIGITAL_TWIN"),
    (_D + "EXEC_SIM", "D_EXEC_SIM"),
    (_D + "EX_CORE", "D_EX_CORE"),
    (_D + "EX_SOR", "D_EX_SOR"),
    (_D + "FACTOR", "D_FACTOR"),
    (_D + "FUNDAMENTAL_SIGNAL", "D_FUNDAMENTAL_SIGNAL"),
    (_D + "GOVERNANCE", "D_GOVERNANCE"),
    (_D + "GOV_AUDIT", "D_GOV_AUDIT"),
    (_D + "GOV_DOCS", "D_GOV_DOCS"),
    (_D + "GOV_DRIFT", "D_GOV_DRIFT"),
    (_D + "GOV_ENFORCEMENT", "D_GOV_ENFORCEMENT"),
    (_D + "GOV_RULE", "D_GOV_RULE"),
    (_D + "GOV_SCRIPTS", "D_GOV_SCRIPTS"),
    (_D + "INTELLIGENCE", "D_INTELLIGENCE"),
    (_D + "KNOWLEDGE", "D_KNOWLEDGE"),
    (_D + "ML_SERVE", "D_ML_SERVE"),
    (_D + "ML_TRAIN", "D_ML_TRAIN"),
    (_D + "PF_ALLOC", "D_PF_ALLOC"),
    (_D + "PF_CORE", "D_PF_CORE"),
    (_D + "POSITION", "D_POSITION"),
    (_D + "RISK", "D_RISK"),
    (_D + "SELL_DECISION", "D_SELL_DECISION"),
    (_D + "SIGLEGACY", "D_SIGLEGACY"),
    (_D + "SIGQC", "D_SIGQC"),
    (_D + "SIMULATION", "D_SIMULATION"),
    (_D + "TRADING", "D_TRADING"),
    (_D + "GOV-REPAIR", "D_GOV_REPAIR"),
]

# 所有含 domain ID 的 text 列（从 information_schema 查得，共 16 列 13 表）
# 排除: edges.cross_domain(integer), domains.domain_group(分类名), domains.domain_name(显示名)
# 排除: dep_cycles(VIEW，数据从基表派生，无需更新)
DOMAIN_ID_COLUMNS = [
    ("domains", "domain_id"),  # PK 表
    ("nodes", "domain_id"),
    ("nodes", "subdomain_id"),  # 嵌入式: D-{DOMAIN}-{SUB}
    ("arch_constraints", "from_domain"),
    ("arch_constraints", "to_domain"),
    ("arch_path_mappings", "domain_id"),
    ("arch_directory_tree", "domain_id"),  # 无 FK
    ("contracts", "provider_domain"),
    ("contracts", "consumer_domain"),
    ("domain_dependencies", "from_domain"),
    ("domain_dependencies", "to_domain"),
    ("domain_events", "source_domain"),
    ("domain_events", "target_domains"),  # 嵌入式: 多值/显示名
    ("domain_mapping", "domain_id"),  # 无 FK
    ("domain_mapping", "subdomain_id"),  # 嵌入式: D-{DOMAIN}-{SUB}
    ("rule_bindings", "domain_id"),  # 无 FK
]

# 8 个 FK 约束（全部 NO ACTION，引用 domains.domain_id）
# 格式: (child_table, child_column, constraint_name)
FK_CONSTRAINTS = [
    ("arch_constraints", "from_domain", "arch_constraints_from_domain_fkey"),
    ("arch_constraints", "to_domain", "arch_constraints_to_domain_fkey"),
    ("arch_path_mappings", "domain_id", "arch_path_mappings_domain_id_fkey"),
    ("contracts", "provider_domain", "contracts_provider_domain_fkey"),
    ("contracts", "consumer_domain", "contracts_consumer_domain_fkey"),
    ("domain_dependencies", "from_domain", "domain_dependencies_from_domain_fkey"),
    ("domain_dependencies", "to_domain", "domain_dependencies_to_domain_fkey"),
    ("domain_events", "source_domain", "domain_events_source_domain_fkey"),
]

# 文件扩展名白名单
FILE_EXTENSIONS = {".py", ".yaml", ".yml", ".md", ".json", ".ps1", ".csv", ".txt", ".toml"}


def drop_fks(cur):
    """临时 drop 所有 FK 约束。"""
    print("  DB: dropping 8 FK constraints...")
    for table, col, name in FK_CONSTRAINTS:
        cur.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {name}")
    print("  DB: FK constraints dropped")


def recreate_fks(cur, not_valid: bool = True):
    """recreate 所有 FK 约束（默认 NO ACTION）。

    :param not_valid: True 时使用 NOT VALID 选项，跳过对历史数据的校验。
        contracts 表存在 126 条预存在脏数据（层级 ID/文件路径/模块 ID 等被误填入
        domain 列），与本次 ID 格式迁移无关。NOT VALID 保证未来插入/更新遵守 FK，
        同时不阻塞迁移。可用 ``ALTER TABLE ... VALIDATE CONSTRAINT ...`` 后续校验。
    """
    suffix = " NOT VALID" if not_valid else ""
    print(f"  DB: recreating 8 FK constraints (not_valid={not_valid})...")
    for table, col, name in FK_CONSTRAINTS:
        cur.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT {name} FOREIGN KEY ({col}) REFERENCES domains(domain_id){suffix}"
        )
    print("  DB: FK constraints recreated")


def preview_database(migrations: list[tuple[str, str]]) -> dict:
    """Dry-run: 用 SELECT COUNT 预览影响行数，不修改数据。"""
    stats = {"tables_updated": 0, "rows_updated": 0}
    conn = get_depgraph_pg_connection()
    cur = conn.cursor()
    try:
        for old_id, new_id in migrations:
            print(f"  DB: {old_id} -> {new_id}")
            for table, col in DOMAIN_ID_COLUMNS:
                cur.execute(
                    f"SELECT COUNT(*) AS cnt FROM {table} WHERE {col} LIKE %s",
                    (f"%{old_id}%",),
                )
                row = cur.fetchone()
                cnt = row["cnt"] if row else 0
                if cnt > 0:
                    print(f"    {table}.{col}: {cnt} rows would update")
                    stats["rows_updated"] += cnt
            stats["tables_updated"] += 1
    finally:
        cur.close()
        conn.close()
    return stats


def update_database(migrations: list[tuple[str, str]]) -> dict:
    """执行模式: drop FKs → REPLACE 更新所有列 → recreate FKs → commit。

    使用 REPLACE(col, old, new) 统一处理精确匹配和嵌入式匹配。
    """
    stats = {"tables_updated": 0, "rows_updated": 0}
    conn = get_depgraph_pg_connection()
    cur = conn.cursor()
    try:
        conn.autocommit = False
        # 1. drop FK 约束
        drop_fks(cur)
        # 2. 逐域更新所有列
        for old_id, new_id in migrations:
            print(f"  DB: {old_id} -> {new_id}")
            for table, col in DOMAIN_ID_COLUMNS:
                # REPLACE 统一处理精确/嵌入式匹配
                sql = f"UPDATE {table} SET {col} = REPLACE({col}, %s, %s) WHERE {col} LIKE %s"
                cur.execute(sql, (old_id, new_id, f"%{old_id}%"))
                affected = cur.rowcount
                if affected > 0:
                    print(f"    {table}.{col}: {affected} rows")
                    stats["rows_updated"] += affected
            stats["tables_updated"] += 1
        # 3. recreate FK 约束
        recreate_fks(cur)
        # 4. commit
        conn.commit()
        print("  DB: COMMITTED")
    except Exception as e:
        conn.rollback()
        print(f"  DB ERROR: {e}", file=sys.stderr)
        raise
    finally:
        cur.close()
        conn.close()
    return stats


def replace_in_files(migrations: list[tuple[str, str]], dry_run: bool) -> dict:
    """在文件中精确替换域ID字符串。

    双重保护防止误伤 module_id:
    1. 负向后瞻 (?<![A-Za-z]): D 前不能是字母，防止匹配 MOD-INFRA_* 中的 D-INFRA_*
    2. 负向前瞻 (?!-\\d): D-{DOMAIN} 后不能跟 -数字，防止匹配 D-XXX-NNN 格式 module_id

    匹配示例:
    - D-INFRA_A2A (域ID) → 替换 ✓ (D 前无字母，后无-数字)
    - D-INFRA_A2A-001 (module_id) → 跳过 ✓ (后跟-数字)
    - MOD-INFRA_A2A (module_id) → 跳过 ✓ (D 前是字母O)
    - D-INFRA_A2A-SUBDOMAIN (子域ID) → 替换 ✓ (-后跟字母)
    """
    stats = {"files_changed": 0, "replacements": 0}
    exclude_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv"}

    for old_id, new_id in migrations:
        print(f"  FILES: {old_id} -> {new_id}")
        # 双重保护: 后瞻防MOD-*误伤 + 前瞻防D-XXX-NNN误伤
        pattern = re.compile(r"(?<![A-Za-z])" + re.escape(old_id) + r"(?!\-\d)")
        for root, dirs, files in os.walk(REPO_ROOT):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for fname in files:
                ext = Path(fname).suffix.lower()
                if ext not in FILE_EXTENSIONS:
                    continue
                fpath = Path(root) / fname
                try:
                    text = fpath.read_text(encoding="utf-8")
                except (UnicodeDecodeError, PermissionError, OSError):
                    continue
                new_text, count = pattern.subn(new_id, text)
                if count == 0:
                    continue
                if not dry_run:
                    fpath.write_text(new_text, encoding="utf-8")
                print(f"    {fpath.relative_to(REPO_ROOT)}: {count} replacements")
                stats["files_changed"] += 1
                stats["replacements"] += count
    return stats


def backup_database():
    """pg_dump 备份 depgraph (PostgreSQL)。"""
    import time

    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_file = REPO_ROOT / "data" / "backups" / f"depgraph_pre_hyphen_migration_{ts}.sql"
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    # 从 config/.env.postgres 读取凭据（真源）
    pg_env = REPO_ROOT / "config" / ".env.postgres"
    pg_config: dict[str, str] = {}
    with pg_env.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                pg_config[k.strip()] = v.strip()
    pg_dump = os.getenv("PG_DUMP_PATH", "pg_dump")
    cmd = [
        pg_dump,
        "-h",
        pg_config["POSTGRES_HOST"],
        "-p",
        pg_config["POSTGRES_PORT"],
        "-U",
        pg_config["POSTGRES_USER"],
        "-d",
        pg_config["POSTGRES_DB"],
        "-f",
        str(backup_file),
    ]
    env = os.environ.copy()
    env["PGPASSWORD"] = pg_config["POSTGRES_PASSWORD"]
    print(f"  BACKUP: {backup_file}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if result.returncode != 0:
        print(f"  BACKUP ERROR: {result.stderr}", file=sys.stderr)
        raise RuntimeError(f"pg_dump failed: {result.stderr}")
    print(f"  BACKUP: OK ({backup_file.stat().st_size} bytes)")
    return backup_file


def main():
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="域ID连字符→下划线迁移")
    parser.add_argument("--dry-run", action="store_true", help="预览不执行")
    parser.add_argument("--execute", action="store_true", help="执行迁移")
    parser.add_argument("--migrations", default="L0", help="迁移批次：L0/L1/L2/all")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        args.dry_run = True

    migrations_map = {
        "L0": L0_MIGRATIONS,
        "L1": L1_MIGRATIONS,
        "L2": L2_MIGRATIONS,
        "all": L0_MIGRATIONS + L1_MIGRATIONS + L2_MIGRATIONS,
    }
    migrations = migrations_map.get(args.migrations, L1_MIGRATIONS)

    print(f"=== 域ID迁移 ({args.migrations}) ===")
    print(f"域数: {len(migrations)}")
    for old_id, new_id in migrations:
        print(f"  {old_id} -> {new_id}")
    print(f"模式: {'DRY-RUN' if args.dry_run else 'EXECUTE'}")
    print()

    if args.execute:
        print("--- 1. 备份 ---")
        backup_database()
        print()

    print("--- 2. DB 更新 ---")
    if args.dry_run:
        db_stats = preview_database(migrations)
    else:
        db_stats = update_database(migrations)
    print(f"  汇总: {db_stats['tables_updated']} 域, {db_stats['rows_updated']} 行")
    print()

    print("--- 3. 文件替换 ---")
    file_stats = replace_in_files(migrations, args.dry_run)
    print(f"  汇总: {file_stats['files_changed']} 文件, {file_stats['replacements']} 替换")
    print()

    print("=== 完成 ===")
    if args.dry_run:
        print("（dry-run 模式，未实际修改）")


if __name__ == "__main__":
    main()
