"""
DM-100026: 极端红蓝测试：depgraph生成器vs设计态保护
红方：模拟所有可能覆盖设计态的场景
蓝方：验证设计态保护机制

治本修订（2026-07-09）：
- 修复外键约束：用真实域 D_GOVERNANCE 替代不存在的 D-TEST
- 优化测试速度：去掉连续运行10次的冗余测试（1次足够验证 DELETE WHERE 子句）
- 用 path 而非 node_id 固定值（避免与真实数据冲突）

#ARCH-084 收编（2026-10-01，st-fullscore-20260930）：
- DB_PATH（--output-db）重定向 tmp 沙箱，禁触真仓 data/databases/ 区；
- PG depgraph 不可达时 pytest.skip（CI 无 PG 环境零错误收集）；
- 隔离边界如实声明：本测试是 DM-100026 真 PG 集成钉——PG 侧 INSERT/DELETE
  严格限 test/design_protection/% 前缀路径（LIKE 无前导通配，不可能命中真实
  节点）+ 终态自清理；生成器对 PG 的重建属派生数据幂等再生（真源=repo 扫描），
  全量 PG 沙箱需 config/.env.postgres.test（当前环境未配置）。
"""

import subprocess
import sys
from pathlib import Path

import pytest

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

DB_PATH = REPO_ROOT / "data" / "databases" / "depgraph"
GENERATOR_SCRIPT = REPO_ROOT / "scripts" / "governance" / "generate_project_depgraph.py"

# 测试用唯一路径前缀（避免与真实数据冲突）
_TEST_PATH_MODULE = "test/design_protection/module.py"
_TEST_PATH_RULE = "test/design_protection/rule.yaml"
_TEST_PATH_TEMPLATE = "test/design_protection/template.yaml"
# 用真实存在的域（外键约束要求 domain_id 必须在 domains 表中存在）
_TEST_DOMAIN = "D_AUTONOMY_CORE"


def _cleanup_test_nodes(conn):
    """清理测试插入的节点（幂等，可重复调用）。"""
    cur = conn.cursor()
    cur.execute("DELETE FROM nodes WHERE path LIKE 'test/design_protection/%'")
    cur.execute(
        "DELETE FROM edges WHERE from_node_id IN "
        "(SELECT node_id FROM nodes WHERE path LIKE 'test/design_protection/%') "
        "OR to_node_id IN "
        "(SELECT node_id FROM nodes WHERE path LIKE 'test/design_protection/%')"
    )
    conn.commit()


def red_team_tests():
    """红方测试：尝试覆盖设计态。

    测试策略：
    1. 插入 design 节点（module/rule/template 三种类型）
    2. 运行生成器（红方攻击）
    3. 验证 design 节点未被删除、字段未被覆盖
    """
    print("=" * 80)
    print("红方测试：尝试覆盖设计态节点")
    print("=" * 80)

    conn = None
    try:
        conn = get_depgraph_pg_connection()
    except Exception as exc:  # noqa: BLE001 — CI/无 PG 环境降级 skip，不误报 error
        pytest.skip(f"PG depgraph 不可达（真 PG 集成钉，无 PG 环境跳过）: {exc}")
    cursor = conn.cursor()

    # 先清理可能残留的旧测试数据
    _cleanup_test_nodes(conn)

    # 1. 插入测试设计态节点（module/rule/template 三种）
    print("\n[红方] 插入设计态测试节点（module/rule/template 三种）...")
    cursor.execute(
        """
        INSERT INTO nodes
        (node_type, domain_id, path, design_maturity, deployment_lifecycle, impact_level, modification_permission)
        VALUES
        ('module', %s, %s, 'design', 'stable', 'M', 'human_gated'),
        ('rule', %s, %s, 'design', 'stable', 'M', 'human_gated'),
        ('template', %s, %s, 'design', 'stable', 'M', 'human_gated')
    """,
        (_TEST_DOMAIN, _TEST_PATH_MODULE, _TEST_DOMAIN, _TEST_PATH_RULE, _TEST_DOMAIN, _TEST_PATH_TEMPLATE),
    )
    conn.commit()

    # 验证插入成功
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE path LIKE 'test/design_protection/%'")
    count = cursor.fetchone()[0]
    print(f"  ✓ 设计态节点已插入: {count} 个")
    assert count == 3, f"应插入 3 个节点，实际 {count}"

    # 2. 运行生成器（红方攻击：生成器 DELETE WHERE design_maturity != 'design' 应跳过这些节点）
    print("\n[红方] 运行 depgraph 生成器（尝试覆盖设计态）...")
    result = subprocess.run(
        [sys.executable, str(GENERATOR_SCRIPT), "--output-db", str(DB_PATH), "--max-workers", "8"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    print(f"  生成器退出码: {result.returncode}")
    if result.returncode != 0:
        print(f"  生成器 stderr: {result.stderr[:500]}")

    # 3. 蓝方验证：设计态节点未被删除
    print("\n[蓝方] 验证设计态节点保护...")
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE path LIKE 'test/design_protection/%'")
    count = cursor.fetchone()[0]

    if count == 0:
        print("  ✗ 失败: 设计态节点被删除！")
        _cleanup_test_nodes(conn)
        conn.close()
        return False

    print(f"  ✓ 设计态节点仍存在: {count} 个")
    assert count == 3, f"应保留 3 个节点，实际 {count}"

    # 4. 蓝方验证：字段未被覆盖
    cursor.execute("""
        SELECT path, design_maturity, deployment_lifecycle, impact_level, modification_permission
        FROM nodes WHERE path LIKE 'test/design_protection/%'
        ORDER BY path
    """)
    rows = cursor.fetchall()
    print("  ✓ 字段保护验证:")
    for row in rows:
        path = row["path"] if isinstance(row, dict) else row[0]
        dm = row["design_maturity"] if isinstance(row, dict) else row[1]
        dl = row["deployment_lifecycle"] if isinstance(row, dict) else row[2]
        il = row["impact_level"] if isinstance(row, dict) else row[3]
        mp = row["modification_permission"] if isinstance(row, dict) else row[4]
        print(f"    {path}: design_maturity={dm}, deployment_lifecycle={dl}, impact_level={il}, mod_perm={mp}")

        if dm != "design" or dl != "stable":
            print(f"  ✗ 失败: {path} 字段被覆盖！")
            _cleanup_test_nodes(conn)
            conn.close()
            return False

    # 5. 清理测试数据
    print("\n[清理] 删除测试节点...")
    _cleanup_test_nodes(conn)

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
        print("  验证点：")
        print("  1. 生成器 DELETE WHERE design_maturity != 'design' 跳过设计态节点 ✓")
        print("  2. 设计态节点字段（design_maturity/deployment_lifecycle 等）未被覆盖 ✓")
        print("  3. module/rule/template 三种节点类型均受保护 ✓")
        print("=" * 80)
        return 0
    else:
        print("✗ 测试失败 - 设计态保护机制存在缺陷")
        print("=" * 80)
        return 1


def test_depgraph_generator_design_protection():
    """depgraph 生成器设计态保护验证——委托给 main()，pytest 收集入口。"""
    assert main() == 0


@pytest.fixture(autouse=True)
def _sandbox_output_db(monkeypatch, tmp_path):
    """#ARCH-084 收编：--output-db 锚 tmp 沙箱（P2 迁移后该参数=PG 库名而非文件
    路径，重定向零语义影响；防未来参数语义回摆时测试误写真仓 data/ 区）。"""
    sandbox = tmp_path / "depgraph_sandbox.db"
    sandbox.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(sys.modules[__name__], "DB_PATH", sandbox)


if __name__ == "__main__":
    sys.exit(main())
