# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.audit_domain_nodes
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""SRC-100200: Audit 13 over-capacity domains granularity distribution.
P0-4升级：4类检测（跨域违规+容量超限+孤儿节点+层级违规）
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── _shared 模块 import bootstrap（P2迁移：复用 get_depgraph_pg_connection）──
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402


# ============================================================================
# P0-4 升级：4类检测函数
# ============================================================================


def detect_cross_domain_violations(cur) -> list:
    """检测1: 跨域违规（import跨越域边界但未在domain_dependencies中声明）"""
    cur.execute("""
    SELECT e.from_node_id, e.to_node_id, n1.domain_id AS from_domain_id,
           n2.domain_id AS to_domain_id, e.dep_type
    FROM edges e
    JOIN nodes n1 ON e.from_node_id = n1.node_id
    JOIN nodes n2 ON e.to_node_id = n2.node_id
    WHERE n1.domain_id != n2.domain_id
    AND n1.domain_id IS NOT NULL AND n1.domain_id != ''
    AND n2.domain_id IS NOT NULL AND n2.domain_id != ''
    AND e.dep_maturity = 'active'
    AND NOT EXISTS (
        SELECT 1 FROM domain_dependencies dd
        WHERE dd.from_domain = n1.domain_id
        AND dd.to_domain = n2.domain_id
    )
    """)
    return [
        {
            "type": "cross_domain",
            "from_node": r["from_node_id"],
            "to_node": r["to_node_id"],
            "from_domain": r["from_domain_id"],
            "to_domain": r["to_domain_id"],
            "dep_type": r["dep_type"],
        }
        for r in cur.fetchall()
    ]


def detect_capacity_violations(cur) -> list:
    """检测2: 容量超限（production 节点数 > domains.max_modules）

    ARCH-CAP-001 模块定义口径：production 节点 = design_maturity='production' 的真实代码文件。
    design/prototype 节点不计入模块容量（trae_055 ARCH-CAP-001）。
    禁止使用 current_modules（含三态节点）做容量判定。
    """
    cur.execute("""
    SELECT n.domain_id, COUNT(*) as production_count, d.max_modules
    FROM nodes n
    JOIN domains d ON n.domain_id = d.domain_id
    WHERE n.design_maturity = 'production'
    GROUP BY n.domain_id
    HAVING COUNT(*) > d.max_modules
    """)
    return [
        {"type": "capacity_exceeded", "domain_id": r["domain_id"], "production_nodes": r["production_count"], "max": r["max_modules"]} for r in cur.fetchall()
    ]


def detect_hard_limit_violations(cur) -> list:
    """检测2b: 硬上限违规（production 节点数 > 150，ARCH-CAP-002 硬上限）

    独立于 domains.max_modules 字段判定——即使 max_modules 被设为过高的旧口径反推值，
    也能检出超过 150 硬上限的域。150 是 AI 可维护性硬上限（trae_055 ARCH-CAP-002 v1.0.8 二元规则）。
    """
    cur.execute("""
    SELECT n.domain_id, COUNT(*) as production_count, d.max_modules
    FROM nodes n
    JOIN domains d ON n.domain_id = d.domain_id
    WHERE n.design_maturity = 'production'
    GROUP BY n.domain_id
    HAVING COUNT(*) > 150
    """)
    return [
        {"type": "hard_limit_exceeded", "domain_id": r["domain_id"], "production_nodes": r["production_count"], "hard_limit": 150, "max": r["max_modules"]}
        for r in cur.fetchall()
    ]


def detect_orphan_nodes(cur) -> list:
    """检测3: 孤儿节点（路径未注册到目录树的节点）DM-3005修正"""
    cur.execute("""
    SELECT n.node_id, n.path
    FROM nodes n
    LEFT JOIN arch_directory_tree a ON n.path = a.path
    WHERE a.path IS NULL
    AND (n.design_maturity != 'design' OR n.design_maturity IS NULL)
    LIMIT 100
    """)
    return [{"type": "orphan_node", "node_id": r["node_id"], "path": r["path"]} for r in cur.fetchall()]


def detect_layer_violations(cur) -> list:
    """检测4: 层级违规（通过domains.layer_id+layer_level数值比较）DM-3007修正 v6: arch_domain_layers已合并"""
    # DM-3007: 使用layer_level数值比较替代硬编码LIKE字符串匹配
    cur.execute("""
    SELECT e.from_node_id, e.to_node_id, n1.domain_id AS from_domain_id,
           n2.domain_id AS to_domain_id, d1.layer_id AS from_layer_id, d2.layer_id AS to_layer_id
    FROM edges e
    JOIN nodes n1 ON e.from_node_id = n1.node_id
    JOIN nodes n2 ON e.to_node_id = n2.node_id
    JOIN domains d1 ON n1.domain_id = d1.domain_id
    JOIN domains d2 ON n2.domain_id = d2.domain_id
    WHERE CAST(SUBSTR(d1.layer_id, 2, 1) AS INTEGER) < CAST(SUBSTR(d2.layer_id, 2, 1) AS INTEGER)
    AND e.dep_maturity = 'active'
    LIMIT 100
    """)
    return [
        {
            "type": "layer_violation",
            "from": r["from_node_id"],
            "to": r["to_node_id"],
            "from_domain": r["from_domain_id"],
            "to_domain": r["to_domain_id"],
            "from_layer": r["from_layer_id"],
            "to_layer": r["to_layer_id"],
        }
        for r in cur.fetchall()
    ]


def write_violations(cur, violations: list):
    """DM-3009: 将4类检测结果持久化到arch_constraints表"""
    for v in violations:
        cur.execute(
            "INSERT INTO arch_constraints (constraint_type, violation_status, details, detected_at) VALUES (%s, 'open', %s, now())",
            (v["type"], str(v)),
        )


def check_all():
    """DM-3008: 清空旧检测结果并执行4类检测"""
    conn = get_depgraph_pg_connection(autocommit=False)
    try:
        cur = conn.cursor()
        # 清空旧检测结果
        cur.execute("DELETE FROM arch_constraints WHERE violation_status = 'open'")
        # 执行4类检测
        cross_domain_violations = detect_cross_domain_violations(cur)
        capacity_violations = detect_capacity_violations(cur)
        hard_limit_violations = detect_hard_limit_violations(cur)
        orphan_violations = detect_orphan_nodes(cur)
        layer_violations = detect_layer_violations(cur)
        # 持久化结果
        all_violations = (
            cross_domain_violations + capacity_violations + hard_limit_violations + orphan_violations + layer_violations
        )
        write_violations(cur, all_violations)
        conn.commit()
        print(f"[check_all] 已清空旧检测结果并写入 {len(all_violations)} 条新违规")
    finally:
        conn.close()


def run_4class_check():
    """执行4类检测，输出报告"""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        cur = conn.cursor()

        print("=" * 60)
        print("=== P0-4 4类架构检测报告 ===")
        print("=" * 60)

        # 检测1: 跨域违规
        print("\n--- 检测1: 跨域违规 ---")
        cross_violations = detect_cross_domain_violations(cur)
        print(f"跨域违规数: {len(cross_violations)}")
        if cross_violations:
            for v in cross_violations[:5]:
                print(f"  {v['from_domain']} -> {v['to_domain']} ({v['dep_type']})")
            if len(cross_violations) > 5:
                print(f"  ... 共{len(cross_violations)}条")

        # 检测2: 容量超限
        print("\n--- 检测2: 容量超限（production 节点口径，ARCH-CAP-001）---")
        capacity_violations = detect_capacity_violations(cur)
        print(f"容量超限域数: {len(capacity_violations)}")
        for v in capacity_violations:
            print(f"  {v['domain_id']}: production_nodes={v['production_nodes']}, max={v['max']}")

        # 检测2b: 硬上限违规（ARCH-CAP-002，独立于 max_modules）
        print("\n--- 检测2b: 硬上限违规（production 节点 > 150，ARCH-CAP-002）---")
        hard_limit_violations = detect_hard_limit_violations(cur)
        print(f"硬上限违规域数: {len(hard_limit_violations)}")
        for v in hard_limit_violations:
            print(
                f"  {v['domain_id']}: production_nodes={v['production_nodes']}, hard_limit={v['hard_limit']}, max={v['max']}"
            )

        # 检测3: 孤儿节点
        print("\n--- 检测3: 孤儿节点 ---")
        orphan_violations = detect_orphan_nodes(cur)
        print(f"孤儿节点数: {len(orphan_violations)}")
        if orphan_violations:
            for v in orphan_violations[:5]:
                print(f"  node_id={v['node_id']}, path={v['path']}")

        # 检测4: 层级违规
        print("\n--- 检测4: 层级违规 ---")
        layer_violations = detect_layer_violations(cur)
        print(f"层级违规数: {len(layer_violations)}")
        if layer_violations:
            for v in layer_violations[:5]:
                print(f"  {v['from_layer']} -> {v['to_layer']}: {v['from_domain']} -> {v['to_domain']}")

        # 汇总
        print("\n" + "=" * 60)
        total = (
            len(cross_violations)
            + len(capacity_violations)
            + len(hard_limit_violations)
            + len(orphan_violations)
            + len(layer_violations)
        )
        print(f"=== 检测汇总: 共{total}个违规 ===")
        print(f"  跨域违规: {len(cross_violations)}")
        print(f"  容量超限: {len(capacity_violations)}")
        print(f"  硬上限违规(>150): {len(hard_limit_violations)}")
        print(f"  孤儿节点: {len(orphan_violations)}")
        print(f"  层级违规: {len(layer_violations)}")
        print("=" * 60)

    finally:
        conn.close()


def load_arch_constraints(project_root: str) -> list[dict]:
    """Scan architecture_model/*.yaml for constraint definitions.

    H8 fix: Replace hardcoded arch_constraints with real data from YAML.
    """
    constraints: list[dict] = []
    yaml_dir = os.path.join(project_root, "architecture_model")
    if not os.path.isdir(yaml_dir):
        return constraints

    for yaml_path in sorted(glob.glob(os.path.join(yaml_dir, "**", "*.yaml"), recursive=True)):
        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data or not isinstance(data, dict):
                continue

            for key in ("constraints", "arch_constraints"):
                entries = data.get(key, [])
                if not entries:
                    continue
                if isinstance(entries, dict):
                    entries = [{"id": k, **v} for k, v in entries.items() if isinstance(v, dict)]
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    constraint = {
                        "constraint_id": entry.get("id", entry.get("constraint_id", "")),
                        "name": entry.get("name", ""),
                        "constraint_type": entry.get("type", entry.get("constraint_type", "architectural")),
                        "from_domain": entry.get("from_domain", entry.get("source_domain", "")),
                        "to_domain": entry.get("to_domain", entry.get("target_domain", "")),
                        "rule_definition": json.dumps(entry, ensure_ascii=False)
                        if entry.get("rule") or entry.get("definition")
                        else "",
                        "severity": entry.get("severity", "medium"),
                        "enforcement": entry.get("enforcement", "advisory"),
                        "description": entry.get("description", ""),
                    }
                    if constraint["constraint_id"] or constraint["name"]:
                        constraints.append(constraint)
        except Exception as e:
            print(f"  [H8] Warning: Failed to parse {yaml_path}: {e}")

    return constraints


domains_13 = [
    "D_PF_CORE",
    "D_MKT_DATA",
    "D_RISK",
    "D_INTEGRATION",
    "D_OPS",
    "D_SECURITY",
    "D_AUTONOMY_CORE",
    "D_ML_TRAIN",
    "D_GOVERNANCE",
    "D_COMPLIANCE",
    "D_FACTOR",
    "D_SIGLEGACY",
    "D_INFRA_RUNTIME",
]


def main():
    parser = argparse.ArgumentParser(description="Audit domain nodes - P0-4升级含4类检测")
    parser.add_argument(
        "--check", action="store_true", help="P0-4: 执行4类架构检测（跨域违规+容量超限+孤儿节点+层级违规）"
    )
    args = parser.parse_args()

    # P0-4: --check模式执行4类检测
    if args.check:
        run_4class_check()
        sys.exit(0)

    conn = get_depgraph_pg_connection(autocommit=False)
    try:
        cur = conn.cursor()

        # STEP 2
        print("STEP 2: Node type distribution")
        step2 = {}
        for d in domains_13:
            cur.execute(
                "SELECT node_type, COUNT(*) AS cnt FROM nodes WHERE domain_id=%s AND design_maturity='design' GROUP BY node_type ORDER BY COUNT(*) DESC",
                (d,),
            )
            rows = cur.fetchall()
            step2[d] = {r["node_type"]: r["cnt"] for r in rows}
            total = sum(step2[d].values())
            print(f"  {d}: total={total} -> {step2[d]}")

        # STEP 3
        print("STEP 3: belongs_to fill rate")
        step3 = {}
        for d in domains_13:
            cur.execute(
                # feature/reference/implementation 已废弃，迁移到 module/service/doc/script（见 node_type_vocabulary.yaml）
                "SELECT COUNT(*) as total, SUM(CASE WHEN belongs_to IS NOT NULL AND belongs_to != '' THEN 1 ELSE 0 END) as has_parent FROM nodes WHERE domain_id=%s AND design_maturity='design' AND node_type IN ('module','service','doc','script')",
                (d,),
            )
            row = cur.fetchone()
            step3[d] = {"total": row["total"], "has_parent": row["has_parent"]} if row["total"] > 0 else {"total": 0, "has_parent": 0}
            print(f"  {d}: total_fri={step3[d]['total']}, has_parent={step3[d]['has_parent']}")

        # STEP 4
        print("STEP 4: D_SIGLEGACY / D_SIMULATION details")
        for dom in ["D_SIGLEGACY", "D_SIMULATION"]:
            cur.execute(
                "SELECT node_id, node_name, node_type FROM nodes WHERE domain_id=%s AND design_maturity='design' ORDER BY node_id",
                (dom,),
            )
            rows = cur.fetchall()
            print(f"  {dom}: {len(rows)} nodes")
            for r in rows:
                print(f"    {r['node_id']} | {r['node_name'] or '(empty)'} | {r['node_type']}")

        # STEP 5
        print("STEP 5: Duplicate names")
        cur.execute(
            "SELECT node_name, domain_id, COUNT(*) as cnt FROM nodes WHERE design_maturity='design' AND node_name IS NOT NULL AND node_name != '' GROUP BY node_name, domain_id HAVING COUNT(*) > 1 ORDER BY cnt DESC"
        )
        dup_rows = cur.fetchall()
        step5 = [{"node_name": r["node_name"], "domain_id": r["domain_id"], "count": r["cnt"]} for r in dup_rows]
        print(f"  Duplicate groups: {len(step5)}")
        for r in step5:
            print(f'    name="{r["node_name"]}" | domain={r["domain_id"]} | count={r["count"]}')

        # STEP 6
        print("STEP 6: Empty names")
        cur.execute(
            "SELECT domain_id, node_type, COUNT(*) AS cnt FROM nodes WHERE design_maturity='design' AND (node_name IS NULL OR node_name = '') GROUP BY domain_id, node_type ORDER BY COUNT(*) DESC"
        )
        empty_rows = cur.fetchall()
        step6 = [{"domain_id": r["domain_id"], "node_type": r["node_type"], "count": r["cnt"]} for r in empty_rows]
        total_empty = sum(r["count"] for r in step6)
        print(f"  Empty name nodes: {total_empty} across {len(step6)} groups")
        for r in step6:
            print(f"    domain={r['domain_id']}, type={r['node_type']}, count={r['count']}")

        # STEP 7
        print("STEP 7: Write arch_constraints")

        # H8 fix: Load real constraints from architecture_model/*.yaml
        arch_constraints = load_arch_constraints(PROJECT_ROOT)
        valid_domains = set()
        try:
            cur.execute("SELECT domain_id FROM domains")
            valid_domains = {row["domain_id"] for row in cur.fetchall()}
        except Exception as e:
            if "no such table" not in str(e).lower() and "does not exist" not in str(e).lower():
                print(f"  [H8] Error querying domains table: {e}")
            # If table doesn't exist, that's expected - skip silently

        # Delete old hardcoded constraints with SYSTEM domain
        try:
            cur.execute("DELETE FROM arch_constraints WHERE from_domain='SYSTEM' AND to_domain='SYSTEM'")
        except Exception:
            pass

        inserted = 0
        skipped = 0
        for c in arch_constraints:
            from_d = c.get("from_domain", "")
            to_d = c.get("to_domain", "")
            if from_d and from_d not in valid_domains:
                skipped += 1
                continue
            if to_d and to_d not in valid_domains:
                skipped += 1
                continue
            try:
                cur.execute(
                    """INSERT INTO arch_constraints
                               (constraint_id, name, constraint_type, from_domain, to_domain,
                                rule_definition, severity, enforcement, description)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                               ON CONFLICT (constraint_id) DO UPDATE SET
                                name=EXCLUDED.name, constraint_type=EXCLUDED.constraint_type,
                                from_domain=EXCLUDED.from_domain, to_domain=EXCLUDED.to_domain,
                                rule_definition=EXCLUDED.rule_definition, severity=EXCLUDED.severity,
                                enforcement=EXCLUDED.enforcement, description=EXCLUDED.description""",
                    (
                        c["constraint_id"],
                        c["name"],
                        c["constraint_type"],
                        from_d,
                        to_d,
                        c["rule_definition"],
                        c["severity"],
                        c["enforcement"],
                        c["description"],
                    ),
                )
                inserted += 1
            except Exception as e:
                print(f"  [H8] Warning: Failed to insert constraint {c.get('constraint_id', '?')}: {e}")

        conn.commit()
        print(f"  [H8] Inserted {inserted} arch_constraints from YAML, skipped {skipped} with invalid domain refs")

        # Verify
        cur.execute("SELECT COUNT(*) AS cnt FROM arch_constraints")
        count = cur.fetchone()["cnt"]
        print(f"  Verification: {count} record(s) in arch_constraints")

        print("=== SRC-100200 COMPLETE ===")
        print(f"RESULT: count={count}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
