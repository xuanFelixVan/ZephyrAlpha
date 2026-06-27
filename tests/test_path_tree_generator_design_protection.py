"""
DM-100027: 极端红蓝测试：路径树生成器vs设计态保护
红方：模拟所有可能覆盖设计态目录的场景
蓝方：验证设计态保护机制
"""

import subprocess
import sys
from pathlib import Path

from zephyr.governance.depgraph_schema import get_db_connection
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

DB_PATH = REPO_ROOT / "data" / "databases" / "depgraph.db"
GENERATOR_SCRIPT = REPO_ROOT / "scripts" / "governance" / "generate_project_path_tree.py"


def red_team_tests():
    """红方测试：尝试覆盖设计态"""
    print("=" * 80)
    print("红方测试：尝试覆盖设计态目录")
    print("=" * 80)

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 插入测试设计态目录节点（state 列 v5 已删除，改用 design_maturity）
    print("\n[红方] 插入设计态测试目录节点...")
    cursor.execute("""
        INSERT INTO arch_directory_tree
        (path, parent_path, path_type, domain_id, design_maturity, blueprint_id, change_policy, modification_permission)
        VALUES ('test/design/directory', 'test/design', 'directory', 'D-TEST', 'design', 'TEST-BLUEPRINT', 'stable', 'human_gated')
        ON CONFLICT (path) DO UPDATE SET
            parent_path=EXCLUDED.parent_path,
            path_type=EXCLUDED.path_type,
            domain_id=EXCLUDED.domain_id,
            design_maturity=EXCLUDED.design_maturity,
            blueprint_id=EXCLUDED.blueprint_id,
            change_policy=EXCLUDED.change_policy,
            modification_permission=EXCLUDED.modification_permission
    """)
    conn.commit()

    # 验证插入成功
    cursor.execute("SELECT COUNT(*) FROM arch_directory_tree WHERE path = 'test/design/directory'")
    count = cursor.fetchone()[0]
    print(f"  ✓ 设计态目录节点已插入: {count} 个")

    # 2. 运行路径树生成器（红方攻击）
    print("\n[红方] 运行路径树生成器（尝试覆盖设计态）...")
    result = subprocess.run(
        [sys.executable, str(GENERATOR_SCRIPT), "--output-db", str(DB_PATH)],
        capture_output=True,
        text=True,
        timeout=300,
    )
    print(f"  生成器退出码: {result.returncode}")
    if result.returncode != 0:
        print(f"  生成器错误: {result.stderr[:500]}")

    # 3. 验证设计态目录节点是否被保护
    print("\n[蓝方] 验证设计态目录节点保护...")
    cursor.execute("SELECT COUNT(*) FROM arch_directory_tree WHERE path = 'test/design/directory'")
    count = cursor.fetchone()[0]

    if count == 0:
        print("  ✗ 失败: 设计态目录节点被删除！")
        conn.close()
        return False

    print(f"  ✓ 设计态目录节点仍存在: {count} 个")

    # 4. 验证字段未被覆盖（state 列 v5 已删除，改用 design_maturity）
    cursor.execute("""
        SELECT design_maturity, blueprint_id
        FROM arch_directory_tree WHERE path = 'test/design/directory'
    """)
    row = cursor.fetchone()
    if row:
        design_maturity, blueprint_id = row
        print("  ✓ 字段保护验证:")
        print(f"    design_maturity: {design_maturity} (应为 'design')")
        print(f"    blueprint_id: {blueprint_id} (应为 'TEST-BLUEPRINT')")

        if design_maturity != "design":
            print("  ✗ 失败: 字段被覆盖！")
            conn.close()
            return False

    # 5. 连续运行10次测试
    print("\n[红方] 连续运行生成器10次...")
    for i in range(10):
        result = subprocess.run(
            [sys.executable, str(GENERATOR_SCRIPT), "--output-db", str(DB_PATH)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            print(f"  第 {i + 1} 次运行失败: {result.stderr[:200]}")

    # 6. 最终验证设计态目录节点
    cursor.execute("SELECT COUNT(*) FROM arch_directory_tree WHERE path = 'test/design/directory'")
    count = cursor.fetchone()[0]

    if count == 0:
        print("  ✗ 失败: 连续运行后设计态目录节点被删除！")
        conn.close()
        return False

    print(f"  ✓ 连续运行10次后设计态目录节点仍存在: {count} 个")

    # 7. 清理测试数据
    print("\n[清理] 删除测试节点...")
    cursor.execute("DELETE FROM arch_directory_tree WHERE path LIKE 'test/%'")
    conn.commit()

    conn.close()
    return True


def main():
    print("\n" + "=" * 80)
    print("DM-100027: 极端红蓝测试 - 路径树生成器vs设计态保护")
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


def test_path_tree_generator_design_protection():
    """路径树生成器设计态保护验证——委托给 main()，pytest 收集入口。"""
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
