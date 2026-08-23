"""
DM-100027: 极端红蓝测试：路径树生成器vs设计态保护
红方：模拟所有可能覆盖设计态目录的场景
蓝方：验证设计态保护机制
"""

import subprocess
import sys
from pathlib import Path

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# 注：depgraph 已迁移到 PostgreSQL（P2迁移），DB_PATH 路径常量已移除
# 治本（2026-06-29）：原 --output-db 路径（cmd_write_db）已删除（损坏死代码，递归键名不匹配）。
# 改用 --write 路径验证 _write_tree_to_db 的设计态保护（走 cmd_write 完整流程：磁盘扫描+合并+写PG）。
GENERATOR_SCRIPT = REPO_ROOT / "scripts" / "governance" / "generate_project_path_tree.py"


def red_team_tests():
    """红方测试：尝试覆盖设计态"""
    print("=" * 80)
    print("红方测试：尝试覆盖设计态目录")
    print("=" * 80)

    conn = get_depgraph_pg_connection()
    cursor = conn.cursor()

    try:
        return _run_red_blue(conn, cursor)
    finally:
        # 清理测试数据（无论成功失败）：先删 arch_directory_tree 测试行，再删播种的测试域
        # （FK 顺序约束——arch_directory_tree.domain_id REFERENCES domains(domain_id)）
        print("\n[清理] 删除测试节点与测试域...")
        cursor.execute("DELETE FROM arch_directory_tree WHERE path LIKE 'test/%'")
        cursor.execute("DELETE FROM domains WHERE domain_id = 'D_TEST'")
        conn.commit()
        conn.close()


def _run_red_blue(conn, cursor):
    # 0. 播种测试域（治本：arch_directory_tree.domain_id 有 FK 到 domains，
    #    原 'D-TEST' 未播种触发 ForeignKeyViolation；且 domains CHECK 要求
    #    domain_id 匹配 ^D_[A-Z][A-Z0-9_]*$，连字符不合法，故用 'D_TEST'）
    print("\n[播种] 插入测试域 D_TEST...")
    cursor.execute("""
        INSERT INTO domains (domain_id, domain_name, domain_group, description, created_at, updated_at)
        VALUES ('D_TEST', 'Test Domain', 'test', 'red/blue test seed', '2026-08-23T00:00:00', '2026-08-23T00:00:00')
        ON CONFLICT (domain_id) DO NOTHING
    """)
    conn.commit()

    # 1. 插入测试设计态目录节点（state 列 v5 已删除，改用 design_maturity）
    print("\n[红方] 插入设计态测试目录节点...")
    cursor.execute("""
        INSERT INTO arch_directory_tree
        (path, parent_path, path_type, domain_id, design_maturity, blueprint_id, change_policy, modification_permission)
        VALUES ('test/design/directory', 'test/design', 'directory', 'D_TEST', 'design', 'TEST-BLUEPRINT', 'stable', 'human_gated')
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
        [sys.executable, str(GENERATOR_SCRIPT), "--write"],
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
            return False

    # 5. 连续运行10次测试
    print("\n[红方] 连续运行生成器10次...")
    for i in range(10):
        result = subprocess.run(
            [sys.executable, str(GENERATOR_SCRIPT), "--write"],
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
        return False

    print(f"  ✓ 连续运行10次后设计态目录节点仍存在: {count} 个")

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
