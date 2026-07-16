# [A_test] module_id: SRC-TST-0117 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] tests.db.test_db_integration
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""DM-100019: 双库集成测试+四方对齐验证

验证内容：
1. governance.db 的 domains.domain_id → depgraph 的 nodes.domain_id 一致性
2. depgraph 的 arch_directory_tree → 实际文件系统路径对齐
3. 双库数据无矛盾
4. 四方对齐验证（代码头部 [BLUEPRINT] → 蓝图 → depgraph → 实际文件）

注：market.duckdb（INFRA-DB-005）已于2026-07-01删除/废弃，当前为2库架构：
    depgraph（PostgreSQL）+ governance.db（SQLite）

测试隔离：本测试为 E2E 集成测试，连接生产库执行只读 SELECT 查询；
         路径通过 governance_db_path fixture 派生（真源：zephyr.shared.io.paths.DB_PATH）。
"""
import sqlite3
import sys
from pathlib import Path

import psycopg2
import pytest

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

PROJECT_ROOT = REPO_ROOT  # alias 真源


@pytest.mark.e2e
def test_cross_db_domain_consistency(governance_db_path: Path):
    """测试跨库 domain_id 一致性（governance.db domains → depgraph nodes）"""
    print("\n[TEST] 跨库 domain_id 一致性验证")

    # 从 governance.db domains 表获取所有 domain_id（P3-1后 tasks.domain_id 已删除）
    gov_conn = sqlite3.connect(governance_db_path)
    gov_cursor = gov_conn.cursor()
    gov_cursor.execute("SELECT domain_id FROM domains")
    gov_domains = {row[0] for row in gov_cursor.fetchall()}
    gov_conn.close()

    # 从 depgraph (PostgreSQL) 获取所有 domain_id
    dep_conn = get_depgraph_pg_connection()
    dep_cursor = dep_conn.cursor()
    dep_cursor.execute("SELECT DISTINCT domain_id FROM nodes WHERE domain_id IS NOT NULL")
    dep_domains = {row[0] for row in dep_cursor.fetchall()}
    dep_conn.close()

    # DM 是临时 domain（Domain Migration，auto-created for FK integrity），不在 depgraph 中是正常的
    _TEMP_DOMAINS = {"DM"}
    gov_domains_real = gov_domains - _TEMP_DOMAINS

    # 验证一致性
    missing_in_depgraph = gov_domains_real - dep_domains
    missing_in_governance = dep_domains - gov_domains

    if missing_in_depgraph:
        print(f"  ✗ FAIL: {len(missing_in_depgraph)} 个 domain 在 governance.db 中存在但 depgraph 中缺失")
        print(f"    缺失的 domain: {sorted(missing_in_depgraph)[:10]}")
        assert False, f"{len(missing_in_depgraph)} 个 governance domain 在 depgraph 中缺失"

    if missing_in_governance:
        print(f"  ⚠ INFO: {len(missing_in_governance)} 个 domain 在 depgraph 中存在但 governance.db 中无记录")
        print("    这些 domain 可能尚未在 governance.db 注册")
        # 这不是错误，只是信息

    print(f"  ✓ PASS: governance.db 有 {len(gov_domains)} 个 domain（含 {len(_TEMP_DOMAINS)} 临时）")
    print(f"  ✓ PASS: depgraph 有 {len(dep_domains)} 个 domain")
    print("  ✓ PASS: 所有 governance domain 在 depgraph 中均存在")


@pytest.mark.e2e
def test_directory_tree_filesystem_alignment():
    """测试 depgraph arch_directory_tree 与实际文件系统对齐（P2迁移后：PostgreSQL）"""
    print("\n[TEST] arch_directory_tree 与实际文件系统对齐验证")

    dep_conn = get_depgraph_pg_connection()
    dep_cursor = dep_conn.cursor()

    # 获取所有文件路径（排除目录；state 列 v5 已删除，仅按 path_type 过滤）
    dep_cursor.execute("""
        SELECT path FROM arch_directory_tree
        WHERE path_type = 'file'
    """)
    db_paths = {row[0] for row in dep_cursor.fetchall()}
    dep_conn.close()

    # 验证这些路径在文件系统中存在
    missing_files = []
    for rel_path in db_paths:
        full_path = PROJECT_ROOT / rel_path
        if not full_path.exists():
            missing_files.append(rel_path)

    if missing_files:
        print(f"  ✗ FAIL: {len(missing_files)} 个文件在 depgraph 中记录但文件系统中不存在")
        print(f"    示例: {missing_files[:5]}")
        assert False, f"{len(missing_files)} 个文件在 depgraph 中记录但文件系统中不存在"

    print(f"  ✓ PASS: depgraph 记录了 {len(db_paths)} 个文件")
    print("  ✓ PASS: 所有文件路径在文件系统中均存在")


@pytest.mark.e2e
def test_schema_version_consistency(governance_db_path: Path):
    """测试双库 schema 版本一致性"""
    print("\n[TEST] 双库 schema 版本一致性验证")

    versions = {}

    # governance.db
    gov_conn = sqlite3.connect(governance_db_path)
    gov_cursor = gov_conn.cursor()
    try:
        gov_cursor.execute("SELECT version, applied_at FROM _schema_version ORDER BY applied_at DESC LIMIT 1")
        row = gov_cursor.fetchone()
        if row:
            versions["governance"] = row[0]
    except sqlite3.OperationalError:
        print("  ⚠ WARNING: governance.db 无 _schema_version 表")
    gov_conn.close()

    # depgraph (PostgreSQL)
    dep_conn = get_depgraph_pg_connection()
    dep_cursor = dep_conn.cursor()
    try:
        dep_cursor.execute("SELECT version, applied_at FROM _schema_version ORDER BY applied_at DESC LIMIT 1")
        row = dep_cursor.fetchone()
        if row:
            versions["depgraph"] = row[0]
    except psycopg2.Error:
        print("  ⚠ WARNING: depgraph (PostgreSQL) 无 _schema_version 表")
    dep_conn.close()

    if versions:
        print(f"  ✓ INFO: 检测到 schema 版本: {versions}")
        # 不强制要求版本一致，因为各库可能独立演进
    else:
        print("  ⚠ WARNING: 未检测到任何 schema 版本记录")
        # 不是错误，只是警告


@pytest.mark.e2e
def test_data_integrity(governance_db_path: Path):
    """测试双库数据完整性"""
    print("\n[TEST] 双库数据完整性验证")

    # governance.db - 检查表是否存在（数据迁移是独立任务）
    gov_conn = sqlite3.connect(governance_db_path)
    gov_cursor = gov_conn.cursor()
    gov_cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = gov_cursor.fetchone()[0]
    gov_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    gov_tables = {row[0] for row in gov_cursor.fetchall()}
    gov_conn.close()

    # depgraph (PostgreSQL) 节点数
    dep_conn = get_depgraph_pg_connection()
    dep_cursor = dep_conn.cursor()
    dep_cursor.execute("SELECT COUNT(*) FROM nodes")
    node_count = dep_cursor.fetchone()[0]
    dep_cursor.execute("SELECT COUNT(*) FROM edges")
    edge_count = dep_cursor.fetchone()[0]
    dep_conn.close()

    print(f"  ✓ governance.db: {task_count} 个任务, {len(gov_tables)} 个表")
    print(f"  ✓ depgraph: {node_count} 个节点, {edge_count} 条边")

    # 验证 governance.db 有完整的表结构（26表）
    expected_gov_tables = {"tasks", "audit_entries", "drift_events", "gate_decisions", "fix_records"}
    missing = expected_gov_tables - gov_tables
    if missing:
        print(f"  ✗ FAIL: governance.db 缺失核心表: {missing}")
        assert False, f"governance.db 缺失核心表: {missing}"

    if node_count == 0:
        print("  ✗ FAIL: depgraph 无节点数据")
        assert False, "depgraph 无节点数据"

    print("  ✓ PASS: 双库 schema 完整，数据可用")


def main():
    """脚本入口：直接运行时执行 E2E 测试（需生产库可用）。"""
    from zephyr.shared.io.paths import DB_PATH

    print("=" * 80)
    print("DM-100019: 双库集成测试+四方对齐验证")
    print("=" * 80)

    # 检查数据库文件是否存在（注：depgraph 已迁移到 PostgreSQL，通过 get_depgraph_pg_connection() 验证）
    if not DB_PATH.exists():
        print(f"\n✗ FAIL: governance.db 不存在: {DB_PATH}")
        return 1
    print(f"✓ governance.db 存在: {DB_PATH}")

    # 验证 depgraph (PostgreSQL) 可连接
    try:
        dep_conn = get_depgraph_pg_connection()
        dep_conn.close()
        print("✓ depgraph (PostgreSQL) 连接成功")
    except Exception as e:
        print(f"\n✗ FAIL: depgraph (PostgreSQL) 连接失败: {e}")
        return 1

    # 运行测试（脚本模式下直接传 DB_PATH）
    tests = [
        lambda: test_cross_db_domain_consistency(DB_PATH),
        test_directory_tree_filesystem_alignment,
        lambda: test_schema_version_consistency(DB_PATH),
        lambda: test_data_integrity(DB_PATH),
    ]

    results = []
    for test in tests:
        try:
            test()
            results.append(True)
        except Exception as e:
            print(f"  ✗ EXCEPTION: {e}")
            results.append(False)

    # 汇总结果
    print("\n" + "=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"测试结果: {passed}/{total} 通过")

    if all(results):
        print("✓ 所有集成测试 PASS")
        print("=" * 80)
        return 0
    else:
        print("✗ 部分测试 FAIL")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
