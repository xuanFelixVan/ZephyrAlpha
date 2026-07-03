#!/usr/bin/env python3
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/check_pg_domain_consistency.py | §pg-consistency
# [MODULE] scripts.governance.d5_architecture.check_pg_domain_consistency
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] AI session; architecture health review
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读核对，禁止修改任何表；动态发现含 domain_id 列的表；输出 JSON + 控制台摘要
# [MODIFY-GUARD] 无（只读）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 连接失败→exit 1；核对完成→exit 0（warn-only，不阻断）
# [TESTS] 无（一次性核对脚本，结果对账即验证）
# [TTL] task_bound
"""
PG depgraph 域级表间一致性核对脚本。

核对内容：
  1. domains 表基础健康度（域数/格式/NOT NULL 字段/build_status 分布）
  2. 动态发现所有含 domain_id / from_domain / to_domain / source_domain 列的表
  3. 对每张表检查域引用完整性（幽灵域 = 引用的 domain_id 不在 domains 表中）
  4. 反向检查：domains 表中无 nodes 引用的空壳域
  5. arch_directory_tree FK 完整性（有 FK 约束，但报告历史脏数据）

输出：控制台摘要 + JSON 报告（--json）
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import get_depgraph_pg_connection  # noqa: E402

# 含域引用的列名（动态发现时匹配）
DOMAIN_COLUMN_PATTERNS = ("domain_id", "from_domain", "to_domain", "source_domain", "target_domain")


def q(cur, sql, params=None):
    """执行查询并返回所有行（dict）"""
    cur.execute(sql, params or ())
    return cur.fetchall()


def qone(cur, sql, params=None):
    """执行查询并返回单值"""
    cur.execute(sql, params or ())
    row = cur.fetchone()
    if row is None:
        return None
    # RealDictCursor 返回 dict，取第一个值
    return next(iter(row.values()))


def check_domains_base(cur) -> dict:
    """domains 表基础健康度检查"""
    print("\n[1/5] domains 表基础健康度检查")
    result = {}

    # 总数
    total = qone(cur, "SELECT COUNT(*) AS n FROM domains")
    result["total"] = total
    print(f"  域总数: {total}")

    # 格式检查（psycopg2 的 % 需转义为 %%，因无参数传入）
    d_underscore = qone(cur, "SELECT COUNT(*) AS n FROM domains WHERE domain_id LIKE 'D\\_%%'")
    d_hyphen = qone(cur, "SELECT COUNT(*) AS n FROM domains WHERE domain_id LIKE 'D-%%'")
    lowercase = qone(
        cur,
        "SELECT COUNT(*) AS n FROM domains WHERE domain_id NOT LIKE 'D\\_%%' AND domain_id NOT LIKE 'D-%%'",
    )
    result["format"] = {
        "D_underscore_pass": d_underscore,
        "D_hyphen_violation": d_hyphen,
        "lowercase_violation": lowercase,
    }
    print(
        f"  格式: D_前缀 PASS={d_underscore}, D-连字符违规={d_hyphen}, 小写违规={lowercase}"
    )

    # 重复（PK 保证无重复，但报告）
    dup_count = qone(
        cur,
        "SELECT COUNT(*) AS n FROM (SELECT domain_id, COUNT(*) AS c FROM domains GROUP BY domain_id HAVING COUNT(*) > 1) t",
    )
    result["duplicates"] = dup_count
    print(f"  重复域（PK 应=0）: {dup_count}")

    # NOT NULL 字段完整性
    nn_violations = {}
    for col in ("domain_name", "domain_group", "created_at", "updated_at"):
        n = qone(cur, f"SELECT COUNT(*) AS n FROM domains WHERE {col} IS NULL")
        if n > 0:
            nn_violations[col] = n
    result["not_null_violations"] = nn_violations
    if nn_violations:
        print(f"  NOT NULL 违规: {nn_violations}")
    else:
        print("  NOT NULL 字段: 全部 PASS")

    # build_status 分布
    cur.execute(
        "SELECT build_status, COUNT(*) AS n FROM domains GROUP BY build_status ORDER BY n DESC"
    )
    status_dist = {r["build_status"]: r["n"] for r in cur.fetchall()}
    result["build_status_distribution"] = status_dist
    print(f"  build_status 分布: {status_dist}")

    return result


def discover_domain_ref_tables(cur) -> list[dict]:
    """动态发现所有含 domain_id / from_domain / to_domain / source_domain 列的表"""
    print("\n[2/5] 动态发现含域引用列的表")
    cur.execute(
        """
        SELECT t.table_name, c.column_name
        FROM information_schema.columns c
        JOIN information_schema.tables t
          ON c.table_name = t.table_name AND t.table_schema = 'public'
        WHERE t.table_type = 'BASE TABLE'
          AND c.column_name IN ('domain_id', 'from_domain', 'to_domain',
                                'source_domain', 'target_domains')
        ORDER BY t.table_name, c.column_name
        """
    )
    tables = {}
    for r in cur.fetchall():
        tbl = r["table_name"]
        col = r["column_name"]
        tables.setdefault(tbl, []).append(col)

    result = [{"table": t, "columns": cs} for t, cs in sorted(tables.items())]
    print(f"  发现 {len(result)} 张表含域引用列:")
    for entry in result:
        print(f"    {entry['table']}: {entry['columns']}")
    return result


def check_ghost_domains(cur, ref_tables: list[dict]) -> dict:
    """对每张表检查幽灵域（引用的 domain_id 不在 domains 表中）"""
    print("\n[3/5] 幽灵域检查（引用的 domain_id 不在 domains 表中）")
    result = {}

    for entry in ref_tables:
        tbl = entry["table"]
        cols = entry["columns"]
        table_ghosts = {}

        for col in cols:
            # target_domains 是 TEXT（逗号分隔），跳过精确匹配检查
            if col == "target_domains":
                continue
            # 幽灵域 = 引用了 domains 表中不存在的 domain_id
            # 排除 NULL 和空字符串（空字符串是脏数据，单独检查）
            cur.execute(
                f"""
                SELECT DISTINCT {col} AS d FROM {tbl}
                WHERE {col} IS NOT NULL
                  AND {col} != ''
                  AND {col} NOT IN (SELECT domain_id FROM domains)
                """
            )
            ghosts = [r["d"] for r in cur.fetchall()]
            if ghosts:
                table_ghosts[col] = ghosts

            # 单独检查空字符串脏数据
            cur.execute(
                f"SELECT COUNT(*) AS n FROM {tbl} WHERE {col} = ''"
            )
            empty_str_count = qone(cur, f"SELECT COUNT(*) AS n FROM {tbl} WHERE {col} = ''")
            if empty_str_count > 0:
                table_ghosts.setdefault("_empty_string_dirty", {})[col] = empty_str_count

        if table_ghosts:
            result[tbl] = table_ghosts
            for col, ghosts in table_ghosts.items():
                if col == "_empty_string_dirty":
                    for dirty_col, cnt in ghosts.items():
                        print(f"  {tbl}.{dirty_col}: {cnt} 条空字符串脏数据")
                else:
                    print(f"  {tbl}.{col}: {len(ghosts)} 个幽灵域 → {ghosts[:10]}")
        else:
            print(f"  {tbl}: PASS（无幽灵域）")

    return result


def check_empty_domains(cur) -> dict:
    """反向检查：domains 表中无 nodes 引用的空壳域"""
    print("\n[4/5] 空壳域检查（domains 表中无 nodes 引用的域）")
    result = {}

    # domains 表中域，但 nodes 表无对应 domain_id 节点
    cur.execute(
        """
        SELECT d.domain_id, d.domain_name, d.build_status
        FROM domains d
        LEFT JOIN nodes n ON n.domain_id = d.domain_id
        WHERE n.node_id IS NULL
        ORDER BY d.domain_id
        """
    )
    empty_in_nodes = [dict(r) for r in cur.fetchall()]
    result["empty_in_nodes"] = empty_in_nodes
    print(f"  无 nodes 引用的域: {len(empty_in_nodes)} 个")
    for e in empty_in_nodes[:15]:
        print(f"    {e['domain_id']} (build_status={e['build_status']})")

    # domains 表中域，但 arch_path_mappings 无对应映射
    cur.execute(
        """
        SELECT d.domain_id, d.domain_name
        FROM domains d
        LEFT JOIN arch_path_mappings apm ON apm.domain_id = d.domain_id
        WHERE apm.mapping_id IS NULL
        ORDER BY d.domain_id
        """
    )
    empty_in_paths = [r["domain_id"] for r in cur.fetchall()]
    result["empty_in_arch_path_mappings"] = empty_in_paths
    print(f"  无 arch_path_mappings 引用的域: {len(empty_in_paths)} 个")
    if empty_in_paths:
        print(f"    {empty_in_paths[:15]}")

    return result


def check_arch_directory_tree_fk(cur) -> dict:
    """arch_directory_tree FK 完整性（有 FK 约束，检查是否实际无违规）"""
    print("\n[5/5] arch_directory_tree FK 完整性（有 FK 约束，验证无违规）")
    n = qone(
        cur,
        "SELECT COUNT(*) AS n FROM arch_directory_tree WHERE domain_id IS NOT NULL AND domain_id NOT IN (SELECT domain_id FROM domains)",
    )
    result = {"fk_violations": n}
    if n > 0:
        print(f"  FK 违规: {n} 条（应有 FK 约束保护，需排查）")
    else:
        print("  FK 违规: 0（PASS，FK 约束有效）")
    return result


def main():
    parser = argparse.ArgumentParser(description="PG depgraph 域级表间一致性核对")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    parser.add_argument(
        "--output", type=str, default=None, help="JSON 报告输出路径（默认只打印控制台）"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("PG depgraph 域级表间一致性核对")
    print(f"时间: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    conn = get_depgraph_pg_connection(autocommit=True)
    cur = conn.cursor()

    try:
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "domains_base": check_domains_base(cur),
                "domain_ref_tables": discover_domain_ref_tables(cur),
                "ghost_domains": None,  # 填充
                "empty_domains": None,
                "arch_directory_tree_fk": None,
            },
        }
        # 复用已发现的表
        report["checks"]["ghost_domains"] = check_ghost_domains(
            cur, report["checks"]["domain_ref_tables"]
        )
        report["checks"]["empty_domains"] = check_empty_domains(cur)
        report["checks"]["arch_directory_tree_fk"] = check_arch_directory_tree_fk(cur)

        # 汇总
        print("\n" + "=" * 70)
        print("核对汇总")
        print("=" * 70)
        db = report["checks"]["domains_base"]
        ghost = report["checks"]["ghost_domains"]
        empty = report["checks"]["empty_domains"]
        fk = report["checks"]["arch_directory_tree_fk"]

        total_ghosts = 0
        total_empty_str_dirty = 0
        for tbl_ghosts in ghost.values():
            for key, val in tbl_ghosts.items():
                if key == "_empty_string_dirty":
                    total_empty_str_dirty += sum(val.values())
                else:
                    total_ghosts += len(val)
        total_empty_nodes = len(empty["empty_in_nodes"])
        total_empty_paths = len(empty["empty_in_arch_path_mappings"])

        print(f"  domains 总数: {db['total']}")
        print(
            f"  格式违规: D-连字符={db['format']['D_hyphen_violation']}, 小写={db['format']['lowercase_violation']}"
        )
        print(f"  NOT NULL 违规: {len(db['not_null_violations'])} 列")
        print(f"  幽灵域总数: {total_ghosts}（跨 {len(ghost)} 张表）")
        print(f"  空字符串脏数据: {total_empty_str_dirty} 条")
        print(f"  空壳域（无 nodes）: {total_empty_nodes}")
        print(f"  空壳域（无 arch_path_mappings）: {total_empty_paths}")
        print(f"  arch_directory_tree FK 违规: {fk['fk_violations']}")

        # 整体健康度判定（空壳域不计入 FAIL，因 planned/deprecated 状态合理）
        healthy = (
            db["format"]["D_hyphen_violation"] == 0
            and db["format"]["lowercase_violation"] == 0
            and db["duplicates"] == 0
            and len(db["not_null_violations"]) == 0
            and total_ghosts == 0
            and total_empty_str_dirty == 0
            and fk["fk_violations"] == 0
        )
        print(f"\n  整体健康度: {'PASS' if healthy else 'FAIL'}")
        report["overall_healthy"] = healthy

        if args.json or args.output:
            json_str = json.dumps(report, ensure_ascii=False, indent=2, default=str)
            if args.output:
                Path(args.output).write_text(json_str, encoding="utf-8")
                print(f"\nJSON 报告已写入: {args.output}")
            elif args.json:
                print("\n--- JSON 报告 ---")
                print(json_str)

    finally:
        cur.close()
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
