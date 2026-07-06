#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.d5_architecture.detect_constraint_violations
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] GitCommitGateway post-commit reconciler (GATE-CONSTRAINT-DETECT)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只写 constraint_type IN (cross_domain_violation/capacity_exceeded/hard_limit_exceeded/orphan_node/layer_violation); 不碰 architecture_contract/architecture_rule
# [MODIFY-GUARD] 修改需通过架构裁定
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 检测失败→exit 1; 无违规→exit 0
# [TESTS] tests/test_detect_constraint_violations.py
# [TTL] permanent
# [ARCH-REF] #ARCH-CAP-001 #ARCH-CAP-002
"""G9-Detect: 架构约束违规检测器（对照 depgraph 实际数据检测 5 类违规）

病根：generate_constraint_violations.py 只读 arch_constraints 表生成 MD 报告，
但没有任何检测器实际检测违规并写入 violation_status/details/detected_at。
导致报告中 56 条约束全部默认 'open'，无法区分真违规和正常约束。

治本（补齐断链的检测层）：
  1. DELETE 旧检测结果（只删检测器写入的 5 类，保留 sync 写入的规则定义）
  2. 执行 5 类检测
  3. INSERT 新检测结果（完整字段 + violation_status='open' + detected_at）

5 类检测：
  1. cross_domain_violation — 跨域违规（import 跨域但未在 domain_dependencies 声明）
  2. capacity_exceeded — 容量超限（production 节点 > max_modules，ARCH-CAP-001）
  3. hard_limit_exceeded — 硬上限违规（production 节点 > 150，ARCH-CAP-002 v1.0.8 二元规则）
  4. orphan_node — 孤儿节点（路径未注册到 arch_directory_tree）
  5. layer_violation — 层级违规（低层依赖高层）

约束分类（区分规则定义和检测结果）：
  - architecture_contract / architecture_rule = 规则定义（sync_yaml_to_depgraph.py 写入）
  - *_violation / *_exceeded / orphan_node = 检测结果（本脚本写入）

触发：GitCommitGateway post-commit reconciler (GATE-CONSTRAINT-DETECT, priority=625)
  - 在 GATE-ARCH-DIAGRAM (630) 之前跑，生成器依赖检测结果

用法
----
    python scripts/governance/d5_architecture/detect_constraint_violations.py
    python scripts/governance/d5_architecture/detect_constraint_violations.py --clean-legacy
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402

# 检测器写入的 constraint_type 集合（DELETE 时只删这些，保留 sync 写入的）
DETECTOR_TYPES = (
    "cross_domain_violation",
    "capacity_exceeded",
    "hard_limit_exceeded",
    "orphan_node",
    "layer_violation",
)

# 历史遗留脏数据类型（写入脚本已删除，需 --clean-legacy 一次性清理）
LEGACY_TYPES = (
    "capacity_limit",  # 32 条，constraint_id 格式 F1-CAPACITY-*
    "stability",       # 23 条，constraint_id 格式 CONSTRAINT_D-*-*
)


# ============================================================================
# 5 类检测函数
# ============================================================================


def detect_cross_domain_violations(cur) -> list[dict]:
    """检测1: 跨域违规（import 跨越域边界但未在 domain_dependencies 中声明）

    规则：edges 表中 n1.domain_id != n2.domain_id 且 dep_maturity='active'，
    但 domain_dependencies 表中没有对应的 from_domain → to_domain 记录。
    """
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
        LIMIT 200
    """)
    return [
        {
            "constraint_id": f"V-CROSS-{r['from_domain_id']}-{r['to_domain_id']}",
            "name": f"跨域违规: {r['from_domain_id']} -> {r['to_domain_id']}",
            "constraint_type": "cross_domain_violation",
            "from_domain": r["from_domain_id"],
            "to_domain": r["to_domain_id"],
            "rule_definition": (
                f"import {r['from_node_id']} -> {r['to_node_id']} "
                f"({r['dep_type']}) 跨域但未在 domain_dependencies 声明"
            ),
            "severity": "error",
            "enforcement": "gate",
            "description": (
                f"跨域依赖未声明: {r['from_domain_id']} -> {r['to_domain_id']}"
            ),
        }
        for r in cur.fetchall()
    ]


def detect_capacity_violations(cur) -> list[dict]:
    """检测2: 容量超限（production 节点数 > domains.max_modules，ARCH-CAP-001）

    模块定义口径：production 节点 = design_maturity='production' 的真实代码文件。
    design/prototype 节点不计入模块容量（trae_055 ARCH-CAP-001）。
    """
    cur.execute("""
        SELECT n.domain_id, d.domain_name, COUNT(*) AS production_count, d.max_modules
        FROM nodes n
        JOIN domains d ON n.domain_id = d.domain_id
        WHERE n.design_maturity = 'production'
        GROUP BY n.domain_id, d.domain_name, d.max_modules
        HAVING COUNT(*) > d.max_modules
    """)
    return [
        {
            "constraint_id": f"V-CAP-{r['domain_id']}",
            "name": f"容量超限: {r['domain_id']}",
            "constraint_type": "capacity_exceeded",
            "from_domain": r["domain_id"],
            "to_domain": None,
            "rule_definition": (
                f"production_nodes({r['production_count']}) > max_modules({r['max_modules']})"
            ),
            "severity": "hard",
            "enforcement": "gate",
            "description": (
                f"域 {r['domain_id']}({r['domain_name']}) production 节点 "
                f"{r['production_count']} 超过上限 {r['max_modules']}，"
                f"需拆分或提升上限 (ARCH-CAP-001)"
            ),
        }
        for r in cur.fetchall()
    ]


def detect_hard_limit_violations(cur) -> list[dict]:
    """检测3: 硬上限违规（production 节点数 > 150，ARCH-CAP-002 硬上限）

    独立于 domains.max_modules 字段判定——即使 max_modules 被设为过高的旧口径反推值，
    也能检出超过 150 硬上限的域。150 是 AI 可维护性硬上限（ARCH-CAP-002 v1.0.8 二元规则）。
    """
    cur.execute("""
        SELECT n.domain_id, d.domain_name, COUNT(*) AS production_count, d.max_modules
        FROM nodes n
        JOIN domains d ON n.domain_id = d.domain_id
        WHERE n.design_maturity = 'production'
        GROUP BY n.domain_id, d.domain_name, d.max_modules
        HAVING COUNT(*) > 150
    """)
    return [
        {
            "constraint_id": f"V-HARD150-{r['domain_id']}",
            "name": f"硬上限违规: {r['domain_id']}",
            "constraint_type": "hard_limit_exceeded",
            "from_domain": r["domain_id"],
            "to_domain": None,
            "rule_definition": (
                f"production_nodes({r['production_count']}) > hard_limit(150)"
            ),
            "severity": "error",
            "enforcement": "gate",
            "description": (
                f"域 {r['domain_id']}({r['domain_name']}) production 节点 "
                f"{r['production_count']} 超过硬上限 150 "
                f"(ARCH-CAP-002 v1.0.8 二元规则)"
            ),
        }
        for r in cur.fetchall()
    ]


def detect_orphan_nodes(cur) -> list[dict]:
    """检测4: 孤儿节点（路径未注册到 arch_directory_tree 的节点）

    排除 design_maturity='design' 的节点（设计态节点路径可能尚未创建）。
    """
    cur.execute("""
        SELECT n.node_id, n.path, n.domain_id
        FROM nodes n
        LEFT JOIN arch_directory_tree a ON n.path = a.path
        WHERE a.path IS NULL
        AND (n.design_maturity != 'design' OR n.design_maturity IS NULL)
        LIMIT 100
    """)
    return [
        {
            "constraint_id": f"V-ORPHAN-{r['node_id']}",
            "name": f"孤儿节点: {r['node_id']}",
            "constraint_type": "orphan_node",
            "from_domain": r["domain_id"],
            "to_domain": None,
            "rule_definition": f"path={r['path']} 未注册到 arch_directory_tree",
            "severity": "warn",
            "enforcement": "advisory",
            "description": f"节点 {r['node_id']} 路径 {r['path']} 未注册到目录树",
        }
        for r in cur.fetchall()
    ]


def detect_layer_violations(cur) -> list[dict]:
    """检测5: 层级违规（低层依赖高层）

    通过 domains.layer_id 数值比较：L1 < L2 < L3 ...
    低层依赖高层 = from_layer_id 数值 < to_layer_id 数值（违反分层架构原则）。
    """
    cur.execute("""
        SELECT e.from_node_id, e.to_node_id, n1.domain_id AS from_domain_id,
               n2.domain_id AS to_domain_id, d1.layer_id AS from_layer_id,
               d2.layer_id AS to_layer_id
        FROM edges e
        JOIN nodes n1 ON e.from_node_id = n1.node_id
        JOIN nodes n2 ON e.to_node_id = n2.node_id
        JOIN domains d1 ON n1.domain_id = d1.domain_id
        JOIN domains d2 ON n2.domain_id = d2.domain_id
        WHERE CAST(SUBSTR(d1.layer_id, 2, 1) AS INTEGER)
            < CAST(SUBSTR(d2.layer_id, 2, 1) AS INTEGER)
        AND e.dep_maturity = 'active'
        LIMIT 100
    """)
    return [
        {
            "constraint_id": f"V-LAYER-{r['from_domain_id']}-{r['to_domain_id']}",
            "name": f"层级违规: {r['from_layer_id']} -> {r['to_layer_id']}",
            "constraint_type": "layer_violation",
            "from_domain": r["from_domain_id"],
            "to_domain": r["to_domain_id"],
            "rule_definition": (
                f"{r['from_layer_id']}({r['from_domain_id']}) -> "
                f"{r['to_layer_id']}({r['to_domain_id']}): 低层依赖高层"
            ),
            "severity": "error",
            "enforcement": "gate",
            "description": (
                f"层级违规: {r['from_node_id']} -> {r['to_node_id']} "
                f"({r['from_layer_id']} -> {r['to_layer_id']})"
            ),
        }
        for r in cur.fetchall()
    ]


# ============================================================================
# 主检测流程
# ============================================================================


def run_detection(conn, clean_legacy: bool = False) -> dict:
    """执行 5 类检测，写入 arch_constraints 表。

    Args:
        conn: PG 连接（autocommit=False，本函数内部 commit）
        clean_legacy: 是否清理历史遗留脏数据（capacity_limit/stability）

    Returns:
        {"total": N, "cross_domain": N, "capacity": N, "hard_limit": N, "orphan": N, "layer": N}
    """
    now_iso = datetime.now().isoformat(timespec="seconds")

    with conn.cursor() as cur:
        # 1. DELETE 旧检测结果（只删检测器写入的 5 类，保留 sync 写入的规则定义）
        cur.execute(
            "DELETE FROM arch_constraints WHERE constraint_type = ANY(%s)",
            (list(DETECTOR_TYPES),),
        )
        deleted = cur.rowcount
        print(f"  清理旧检测结果: {deleted} 条")

        # 1b. 清理历史遗留脏数据（可选，--clean-legacy）
        if clean_legacy:
            cur.execute(
                "DELETE FROM arch_constraints WHERE constraint_type = ANY(%s)",
                (list(LEGACY_TYPES),),
            )
            legacy_deleted = cur.rowcount
            print(
                f"  清理历史遗留脏数据 (capacity_limit/stability): "
                f"{legacy_deleted} 条"
            )

        # 2. 执行 5 类检测
        all_violations: list[dict] = []

        cross = detect_cross_domain_violations(cur)
        print(f"  跨域违规: {len(cross)} 条")
        all_violations.extend(cross)

        capacity = detect_capacity_violations(cur)
        print(f"  容量超限 (ARCH-CAP-001): {len(capacity)} 条")
        all_violations.extend(capacity)

        hard_limit = detect_hard_limit_violations(cur)
        print(f"  硬上限违规 (ARCH-CAP-002): {len(hard_limit)} 条")
        all_violations.extend(hard_limit)

        orphan = detect_orphan_nodes(cur)
        print(f"  孤儿节点: {len(orphan)} 条")
        all_violations.extend(orphan)

        layer = detect_layer_violations(cur)
        print(f"  层级违规: {len(layer)} 条")
        all_violations.extend(layer)

        # 3. INSERT 新检测结果（ON CONFLICT 更新）
        for v in all_violations:
            cur.execute(
                """
                INSERT INTO arch_constraints
                    (constraint_id, name, constraint_type, from_domain, to_domain,
                     rule_definition, severity, enforcement, description,
                     violation_status, detected_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'open', %s)
                ON CONFLICT (constraint_id) DO UPDATE SET
                    name=excluded.name,
                    constraint_type=excluded.constraint_type,
                    from_domain=excluded.from_domain,
                    to_domain=excluded.to_domain,
                    rule_definition=excluded.rule_definition,
                    severity=excluded.severity,
                    enforcement=excluded.enforcement,
                    description=excluded.description,
                    violation_status='open',
                    detected_at=excluded.detected_at
                """,
                (
                    v["constraint_id"],
                    v["name"],
                    v["constraint_type"],
                    v["from_domain"],
                    v["to_domain"],
                    v["rule_definition"],
                    v["severity"],
                    v["enforcement"],
                    v["description"],
                    now_iso,
                ),
            )

        conn.commit()

        return {
            "total": len(all_violations),
            "cross_domain": len(cross),
            "capacity": len(capacity),
            "hard_limit": len(hard_limit),
            "orphan": len(orphan),
            "layer": len(layer),
        }


def main():
    parser = argparse.ArgumentParser(
        description="G9-Detect: 架构约束违规检测器（5 类检测 -> arch_constraints 表）"
    )
    parser.add_argument(
        "--clean-legacy",
        action="store_true",
        help="清理历史遗留脏数据 (capacity_limit/stability 类型，写入脚本已删除)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("G9-Detect: 架构约束违规检测器")
    print("=" * 60)

    conn = get_depgraph_pg_connection()
    try:
        result = run_detection(conn, clean_legacy=args.clean_legacy)
        print("\n" + "=" * 60)
        print(f"检测完成: 共 {result['total']} 条违规")
        print(f"  跨域违规: {result['cross_domain']}")
        print(f"  容量超限 (ARCH-CAP-001): {result['capacity']}")
        print(f"  硬上限违规 (ARCH-CAP-002): {result['hard_limit']}")
        print(f"  孤儿节点: {result['orphan']}")
        print(f"  层级违规: {result['layer']}")
        print("=" * 60)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
