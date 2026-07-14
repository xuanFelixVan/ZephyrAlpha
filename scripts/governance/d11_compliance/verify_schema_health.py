#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.verify_schema_health
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants
# [CONSUMERS] .pre-commit-config.yaml gate-schema-health
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] depgraph_schema.py 是 DDL 真源; DB 物理状态必须与 DDL 声明一致
# [MODIFY-GUARD] depgraph_schema.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 漂移→exit 1; 健康→exit 0; 脚本自身错误→exit 2
# [TESTS] tests/test_verify_schema_health.py
# [TTL] task_bound
"""
verify_schema_health.py — depgraph (PostgreSQL) Schema 健康度校验门禁（#ARCH-016 治本）

校验内容：
  1. DDL 列一致性：DB 实际列 vs _DDL_* 声明列（仅保留表）
  2. 只读触发器存在性：READONLY_TABLES 的 9 张表 × 3 触发器
  3. Schema 版本一致性：MAX(_schema_version) == len(_MIGRATIONS)
  4. PG 运行时健康：死锁计数 / 连接数饱和 / 长事务（P3-T4 改造，替代原计划常驻 monitor_pg.py）

退出码：
  0 = 健康（PASS）
  1 = 发现漂移（FAIL）
  2 = 脚本错误（ERROR）

模式：
  --ci              硬阻断模式（默认行为，与其他 GATE 一致；显式传入便于阅读）
  --warn-only       软警告模式（发现漂移仍 exit 0）——用于观察期
  --skip-runtime    跳过校验4（PG 运行时健康），仅做 Schema 静态校验——用于无 PG 连接或快速 pre-commit
"""
__manifest__ = {
    "args": [
        {"flag": "--ci", "type": "bool", "description": "硬阻断模式（漂移 exit 1，默认行为）"},
        {"flag": "--warn-only", "type": "bool", "description": "软警告模式（漂移仍 exit 0，观察期用）"},
        {"flag": "--skip-runtime", "type": "bool", "description": "跳过 PG 运行时健康检查（校验4），仅做 Schema 静态校验"},
    ],
    "description": "depgraph (PostgreSQL) Schema 健康度校验——DDL 列一致性 + 只读触发器 + 版本一致性 + PG 运行时健康，漂移即阻断。对标 #ARCH-016 治本；P3-T4 改造：事件驱动 PG 运行时监控，替代违反 trae_053 的常驻 monitor_pg.py 方案",
    "dimensions": ["D5"],
    "priority": "P1",
    "timeout_seconds": 30,
    "warn_only": False,
}

import argparse
import re
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR, get_depgraph_pg_connection  # noqa: E402

_REPO_ROOT = str(next(p for p in _THIS_FILE.parents if (p / "src" / "zephyr").exists()))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, str(Path(_REPO_ROOT) / "src"))
from zephyr.governance import depgraph_schema  # noqa: E402

# READONLY_TABLES 真源在 sync_yaml_to_depgraph.py（创建只读触发器的地方），
# 此处动态导入消除硬编码副本，防止真源变更后漂移（红蓝对抗修复-严重1）
from d8_doc_sync.sync_yaml_to_depgraph import READONLY_TABLES  # noqa: E402


def parse_ddl_columns(ddl: str) -> list[str]:
    """从 CREATE TABLE DDL 文本中解析列名列表（跳过表级约束 PRIMARY/FOREIGN/CHECK/UNIQUE/CONSTRAINT）。"""
    match = re.search(r"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)\s*\((.*)\)", ddl, re.DOTALL)
    if not match:
        return []
    body = match.group(2)
    columns = []
    depth = 0
    current = ""
    for char in body:
        if char == "(":
            depth += 1
            current += char
        elif char == ")":
            depth -= 1
            current += char
        elif char == "," and depth == 0:
            col_def = current.strip()
            if col_def:
                toks = col_def.split()
                # 精确匹配首 token：真表级约束子句首 token 恰为关键字(如 CONSTRAINT)，列名 constraint_id 首 token 为 CONSTRAINT_ID 不命中
                if toks[0].upper() not in ("PRIMARY", "FOREIGN", "CHECK", "UNIQUE", "CONSTRAINT"):
                    columns.append(toks[0])
            current = ""
        else:
            current += char
    col_def = current.strip()
    if col_def:
        toks = col_def.split()
        if toks[0].upper() not in ("PRIMARY", "FOREIGN", "CHECK", "UNIQUE", "CONSTRAINT"):
            columns.append(toks[0])
    return columns


# 仅含 21 张保留表（已排除 v14 删除的 3 表 arch_bottlenecks/arch_layers/invariants）；
# DDL 常量全部用非 _V5（v1 migration 真源）
_DDL_MAP = {
    "nodes": depgraph_schema._DDL_NODES,
    "edges": depgraph_schema._DDL_EDGES,
    "domains": depgraph_schema._DDL_DOMAINS,
    "domain_dependencies": depgraph_schema._DDL_DOMAIN_DEPS,
    "domain_events": depgraph_schema._DDL_DOMAIN_EVENTS,
    "contracts": depgraph_schema._DDL_CONTRACTS,
    "rule_bindings": depgraph_schema._DDL_RULE_BINDINGS,
    "arch_constraints": depgraph_schema._DDL_ARCH_CONSTRAINTS,
    "arch_directory_tree": depgraph_schema._DDL_ARCH_DIRECTORY_TREE,
    "arch_path_mappings": depgraph_schema._DDL_ARCH_PATH_MAPPINGS,
    "gates": depgraph_schema._DDL_GATES,
    "governance_audit_logs": depgraph_schema._DDL_GOVERNANCE_AUDIT_LOGS,
    "blueprint_links": depgraph_schema._DDL_BLUEPRINT_LINKS,
    "business_streams": depgraph_schema._DDL_BUSINESS_STREAMS,
    "cross_registry_rules": depgraph_schema._DDL_CROSS_REGISTRY_RULES,
    "field_vocabularies": depgraph_schema._DDL_FIELD_VOCABULARIES,
    "hard_boundaries": depgraph_schema._DDL_HARD_BOUNDARIES,
    "infrastructure_components": depgraph_schema._DDL_INFRASTRUCTURE_COMPONENTS,
    "model_capabilities": depgraph_schema._DDL_MODEL_CAPABILITIES,
    "registries": depgraph_schema._DDL_REGISTRIES,
    "domain_mapping": depgraph_schema._DDL_DOMAIN_MAPPING,
}


def check_ddl_columns(conn, issues: list) -> None:
    """校验1：DB 实际列 vs DDL 声明列。"""
    for table, ddl in _DDL_MAP.items():
        declared = set(parse_ddl_columns(ddl))
        cursor = conn.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name=%s",
            (table,),
        )
        actual = {row["column_name"] for row in cursor.fetchall()}
        if not actual:
            issues.append(f"[DDL-DRIFT] 表 '{table}' 不存在于 DB 中")
            continue
        missing_in_db = declared - actual
        extra_in_db = actual - declared
        if missing_in_db:
            issues.append(f"[DDL-DRIFT] 表 '{table}' DB 缺少列: {sorted(missing_in_db)}")
        if extra_in_db:
            issues.append(f"[DDL-DRIFT] 表 '{table}' DB 多出列（DDL 未声明）: {sorted(extra_in_db)}")


def check_readonly_triggers(conn, issues: list) -> None:
    """校验2：只读触发器存在性（READONLY_TABLES 9 张表 × 3 触发器）。

    P2迁移后说明：PostgreSQL 不支持 SQLite 风格的"只读触发器"（SQLite 用触发器阻断写操作），
    PG 改用权限/RLS 策略实现只读保护。此处在 information_schema.triggers 中按名称查找，
    若 P2 迁移未重建同名触发器，将报告 missing（属预期，只读保护机制已变更）。
    """
    for table in READONLY_TABLES:
        for action in ("insert", "update", "delete"):
            trig_name = f"readonly_{table}_{action}"
            cursor = conn.execute(
                "SELECT trigger_name FROM information_schema.triggers "
                "WHERE trigger_schema='public' AND trigger_name=%s",
                (trig_name,),
            )
            if cursor.fetchone() is None:
                issues.append(
                    f"[TRIGGER-MISSING] 只读触发器 '{trig_name}' 不存在（表 {table} 未受只读保护）"
                )


def check_schema_version(conn, issues: list) -> None:
    """校验3：Schema 版本一致性。"""
    expected = len(depgraph_schema._MIGRATIONS)
    cursor = conn.execute("SELECT COALESCE(MAX(version), 0) AS v FROM _schema_version")
    actual = cursor.fetchone()["v"]
    if actual != expected:
        issues.append(
            f"[VERSION-DRIFT] _schema_version MAX={actual} 但 _MIGRATIONS 有 {expected} 条迁移"
            f"（差 {expected - actual} 条未执行）"
        )


# ── 校验4：PG 运行时健康（P3-T4 改造） ──────────────────────────────────────────
# 裁定背景：原 P3-T4 计划新建 monitor_pg.py --watch 常驻监控（违反 trae_053 定时轨），
# 且 100% AI 开发模式无常驻监听者。治本方案：扩展现有 verify_schema_health.py，
# 在 pre-commit 事件驱动时检查 PG 运行时指标，替代常驻监控。
# 阈值设计：连接>80%（接近耗尽，当前状态可阻断）/ 长事务>300s（真正卡死，当前状态可阻断）
# 死锁计数为累计值（无法区分历史/当前），仅信息性输出不阻断
_LONG_TX_THRESHOLD_SECONDS = 300  # noqa: gate-vocab  治本(ARCH-036 P3-A5): 长事务检测阈值，脚本专用
_CONN_SATURATION_PCT = 80


def check_pg_runtime_health(conn, issues: list) -> None:
    """校验4：PostgreSQL 运行时健康（死锁 / 连接数饱和 / 长事务）。

    只读查询，不修改任何状态。事件驱动（pre-commit / 手动），非常驻轮询——符合 trae_053。
    - 死锁计数（累计值）：仅 print 信息，不加入 issues（历史值无法区分，不阻断提交）
    - 连接数饱和 / 长事务（当前状态）：加入 issues，可阻断（反映实时问题）
    """
    # 4a. 死锁计数（累计值，>0 说明曾发生死锁——信息性输出，不阻断）
    cursor = conn.execute(
        "SELECT deadlocks FROM pg_stat_database WHERE datname = current_database()"
    )
    row = cursor.fetchone()
    if row and row["deadlocks"] is not None and row["deadlocks"] > 0:
        # 累计值不加入 issues（会因历史死锁误阻断），仅信息性提示供 AI 排查
        print(
            f"  [INFO][PG-DEADLOCK] 累计死锁 {row['deadlocks']} 次（pg_stat_database.deadlocks 历史值，"
            f"可用 SELECT pg_stat_reset() 清零基线）"
        )

    # 4b. 连接数饱和度（当前库连接 / max_connections）——当前状态，可阻断
    cursor = conn.execute(
        "SELECT count(*) AS active, "
        "(SELECT setting::int FROM pg_settings WHERE name='max_connections') AS max_conn "
        "FROM pg_stat_activity WHERE datname = current_database()"
    )
    row = cursor.fetchone()
    if row and row["max_conn"] and row["max_conn"] > 0:
        usage_pct = row["active"] / row["max_conn"] * 100
        if usage_pct > _CONN_SATURATION_PCT:
            issues.append(
                f"[PG-CONN-SATURATED] 连接数 {row['active']}/{row['max_conn']}"
                f"（{usage_pct:.0f}%），超过 {_CONN_SATURATION_PCT}% 阈值，存在连接耗尽风险"
            )

    # 4c. 长事务 / 长查询（active 状态超过阈值秒数）——当前状态，可阻断
    cursor = conn.execute(
        "SELECT count(*) AS long_tx FROM pg_stat_activity "
        "WHERE datname = current_database() AND state = 'active' "
        "AND query_start IS NOT NULL "
        f"AND now() - query_start > interval '{_LONG_TX_THRESHOLD_SECONDS} seconds'"
    )
    row = cursor.fetchone()
    if row and row["long_tx"] is not None and row["long_tx"] > 0:
        issues.append(
            f"[PG-LONG-TX] 检测到 {row['long_tx']} 个超过 {_LONG_TX_THRESHOLD_SECONDS}s 的活跃长事务/长查询，可能阻塞迁移或写入"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="depgraph (PostgreSQL) Schema 健康度校验")
    parser.add_argument("--db", default="", help="（已废弃）P2迁移后连接由 get_depgraph_pg_connection 统一管理")
    parser.add_argument("--ci", action="store_true", help="硬阻断模式（默认行为，显式传入便于阅读）")
    parser.add_argument("--warn-only", action="store_true", help="软警告模式（发现漂移仍 exit 0）")
    parser.add_argument("--skip-runtime", action="store_true", help="跳过校验4（PG 运行时健康），仅做 Schema 静态校验")
    args = parser.parse_args()

    # P2迁移后：depgraph 已从 SQLite 迁移到 PostgreSQL，连接由 get_depgraph_pg_connection 统一管理
    # （--db 参数保留以兼容既有 pre-commit 调用，但不再用于连接）
    conn = get_depgraph_pg_connection(autocommit=True)
    issues: list[str] = []
    try:
        check_ddl_columns(conn, issues)
        check_readonly_triggers(conn, issues)
        check_schema_version(conn, issues)
        if not args.skip_runtime:
            check_pg_runtime_health(conn, issues)
    except Exception as e:
        print(f"[ERROR] 校验脚本异常: {e}")
        return EXIT_ERROR
    finally:
        conn.close()

    if issues:
        print(f"[FAIL] 发现 {len(issues)} 项 Schema 健康度问题:")
        for issue in issues:
            print(f"  {issue}")
        # --warn-only 优先；默认（无 flag 或 --ci）硬阻断
        return EXIT_PASS if args.warn_only else EXIT_FINDINGS

    print("[PASS] depgraph (PostgreSQL) Schema 健康度校验通过")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
