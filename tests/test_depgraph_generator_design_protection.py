"""
DM-100026: 极端红蓝测试：depgraph生成器vs设计态保护
红方：模拟所有可能覆盖设计态的场景
蓝方：验证设计态保护机制
"""

import subprocess
import sys
from pathlib import Path

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

DB_PATH = REPO_ROOT / "data" / "databases" / "depgraph.db"
GENERATOR_SCRIPT = REPO_ROOT / "scripts" / "governance" / "generate_project_depgraph.py"


def red_team_tests():
    """红方测试：尝试覆盖设计态"""
    print("=" * 80)
    print("红方测试：尝试覆盖设计态节点")
    print("=" * 80)

    conn = get_depgraph_pg_connection()
    cursor = conn.cursor()

    # 1. 插入测试设计态节点
    print("\n[红方] 插入设计态测试节点...")
    cursor.execute("""
        INSERT INTO nodes
        (node_id, node_type, domain_id, path, design_maturity, deployment_lifecycle, impact_level, modification_permission)
        OVERRIDING SYSTEM VALUE
        VALUES (900001, 'module', 'D-TEST', 'test/design/module.py', 'design', 'stable', 'M', 'human_gated')
        ON CONFLICT (node_id) DO UPDATE SET
            node_type=EXCLUDED.node_type,
            domain_id=EXCLUDED.domain_id,
            path=EXCLUDED.path,
            design_maturity=EXCLUDED.design_maturity,
            deployment_lifecycle=EXCLUDED.deployment_lifecycle,
            impact_level=EXCLUDED.impact_level,
            modification_permission=EXCLUDED.modification_permission
    """)
    conn.commit()

    # 验证插入成功
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE node_id = 900001")
    count = cursor.fetchone()[0]
    print(f"  ✓ 设计态节点已插入: {count} 个")

    # 2. 运行生成器（红方攻击）
    print("\n[红方] 运行 depgraph 生成器（尝试覆盖设计态）...")
    result = subprocess.run(
        [sys.executable, str(GENERATOR_SCRIPT), "--output-db", str(DB_PATH), "--max-workers", "8"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    print(f"  生成器退出码: {result.returncode}")
    if result.returncode != 0:
        print(f"  生成器错误: {result.stderr[:500]}")

    # 3. 验证设计态节点是否被保护
    print("\n[蓝方] 验证设计态节点保护...")
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE node_id = 900001")
    count = cursor.fetchone()[0]

    if count == 0:
        print("  ✗ 失败: 设计态节点被删除！")
        conn.close()
        return False

    print(f"  ✓ 设计态节点仍存在: {count} 个")

    # 4. 验证字段未被覆盖
    cursor.execute("""
        SELECT design_maturity, deployment_lifecycle, impact_level, modification_permission
        FROM nodes WHERE node_id = 900001
    """)
    row = cursor.fetchone()
    if row:
        design_maturity, deployment_lifecycle, impact_level, modification_permission = row
        print("  ✓ 字段保护验证:")
        print(f"    design_maturity: {design_maturity} (应为 'design')")
        print(f"    deployment_lifecycle: {deployment_lifecycle} (应为 'stable')")
        print(f"    impact_level: {impact_level} (应为 'M')")
        print(f"    modification_permission: {modification_permission} (应为 'human_gated')")

        if design_maturity != "design" or deployment_lifecycle != "stable":
            print("  ✗ 失败: 字段被覆盖！")
            conn.close()
            return False

    # 5. 连续运行10次测试
    print("\n[红方] 连续运行生成器10次...")
    for i in range(10):
        result = subprocess.run(
            [sys.executable, str(GENERATOR_SCRIPT), "--output-db", str(DB_PATH), "--max-workers", "8"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            print(f"  第 {i + 1} 次运行失败: {result.stderr[:200]}")

    # 6. 最终验证设计态节点
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE node_id = 900001")
    count = cursor.fetchone()[0]

    if count == 0:
        print("  ✗ 失败: 连续运行后设计态节点被删除！")
        conn.close()
        return False

    print(f"  ✓ 连续运行10次后设计态节点仍存在: {count} 个")

    # 7. 测试 rule/template 节点保护
    print("\n[红方] 插入 rule 和 template 测试节点...")
    cursor.execute("""
        INSERT INTO nodes
        (node_id, node_type, domain_id, path, design_maturity)
        OVERRIDING SYSTEM VALUE
        VALUES
        (900002, 'rule', 'D-TEST', 'test/rule.yaml', 'design'),
        (900003, 'template', 'D-TEST', 'test/template.yaml', 'design')
        ON CONFLICT (node_id) DO UPDATE SET
            node_type=EXCLUDED.node_type,
            domain_id=EXCLUDED.domain_id,
            path=EXCLUDED.path,
            design_maturity=EXCLUDED.design_maturity
    """)
    conn.commit()

    # 运行生成器
    result = subprocess.run(
        [sys.executable, str(GENERATOR_SCRIPT), "--output-db", str(DB_PATH), "--max-workers", "8"],
        capture_output=True,
        text=True,
        timeout=300,
    )

    # 验证 rule/template 节点
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE node_id IN (900002, 900003)")
    count = cursor.fetchone()[0]

    if count < 2:
        print(f"  ✗ 失败: rule/template 节点被删除！剩余 {count} 个")
        conn.close()
        return False

    print(f"  ✓ rule/template 节点保护成功: {count} 个")

    # 8. 清理测试数据
    print("\n[清理] 删除测试节点...")
    # node_id 为 bigint，用 IN 替代 LIKE（v5 migration 后 node_id 从 TEXT 改为 INTEGER）
    cursor.execute("DELETE FROM nodes WHERE node_id IN (900001, 900002, 900003)")
    cursor.execute("DELETE FROM edges WHERE from_node_id IN (900001, 900002, 900003) OR to_node_id IN (900001, 900002, 900003)")
    conn.commit()

    conn.close()
    return True


def main():
    print("\n" + "=" * 80)
    print("DM-100026: 极端红蓝测试 - depgraph生成器vs设计态保护")
    print("=" * 80 + "\n")

    success = red_team_tests()

    print("\n" + "=" * 80)
    if success:
        print("✓ 所有测试通过 - 设计态保护机制有效")
        print("=" * 80)
        return 0
    else:
        print("✗ 测试失败 - 设计态保护机制存在缺陷")
        print("=" * 80)
        return 1


def test_depgraph_generator_design_protection():
    """depgraph 生成器设计态保护验证——委托给 main()，pytest 收集入口。"""
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
