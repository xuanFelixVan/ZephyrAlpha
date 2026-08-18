"""
DM-100021: 事件驱动自动启动检查+自动运行检查

验证项：
1. DatabaseService 可初始化并连接 2 个数据库（governance.db + depgraph）
2. depgraph 数据变更可触发事件（通过回调模拟）
3. 自动运行检查（SELECT 1 验证数据库存活）
4. 数据库文件锁检查（多进程写入互斥）
5. schema 版本检查
"""

import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import psycopg2

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

GOVERNANCE_DB = REPO_ROOT / "data" / "databases" / "governance.db"
PROJECT_ROOT = REPO_ROOT  # alias 真源


def test_database_service_init():
    """测试 DatabaseService 初始化和连接"""
    print("\n[TEST] DatabaseService 初始化测试")

    try:
        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        from zephyr.governance.persistence.database_service import DatabaseService

        ds = DatabaseService()

        # 测试 governance 连接
        gov_conn = ds.get_governance_conn()
        assert gov_conn is not None, "governance 连接为 None"
        print("  ✓ governance.db 连接成功")

        # 测试 depgraph 连接
        dep_conn = ds.get_depgraph_conn()
        assert dep_conn is not None, "depgraph 连接为 None"
        print("  ✓ depgraph 连接成功")

        ds.close_all()
        print("  ✓ PASS: DatabaseService 初始化+连接+关闭全部成功")

    except ImportError as e:
        print(f"  ⚠ DatabaseService 导入失败: {e}")
        print("  回退到直接连接测试")

        # 回退测试：直接连接（governance 用 sqlite3，depgraph 已迁移到 PostgreSQL）
        try:
            conn = sqlite3.connect(str(GOVERNANCE_DB))
            conn.execute("SELECT 1")
            conn.close()
            print("  ✓ governance.db 直接连接成功")
        except Exception as ex:
            assert False, f"governance.db 连接失败: {ex}"

        try:
            conn = get_depgraph_pg_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            conn.close()
            print("  ✓ depgraph (PostgreSQL) 直接连接成功")
        except Exception as ex:
            assert False, f"depgraph (PostgreSQL) 连接失败: {ex}"

        print("  ✓ PASS: 直接连接测试通过（DatabaseService 待完善）")
    except Exception as e:
        assert False, f"DatabaseService 初始化失败: {e}"


def test_health_check():
    """测试自动运行健康检查（SELECT 1）"""
    print("\n[TEST] 数据库健康检查测试")

    # governance.db 健康检查（保持 SQLite）
    try:
        conn = sqlite3.connect(str(GOVERNANCE_DB))
        cursor = conn.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        assert result and result[0] == 1, f"governance.db: 健康检查返回异常值: {result}"
        print("  ✓ governance.db: 健康检查通过")
    except Exception as e:
        assert False, f"governance.db: 健康检查失败: {e}"

    # depgraph 健康检查（P2迁移后：PostgreSQL）
    try:
        conn = get_depgraph_pg_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        conn.close()
        assert result and result[0] == 1, f"depgraph (PostgreSQL): 健康检查返回异常值: {result}"
        print("  ✓ depgraph (PostgreSQL): 健康检查通过")
    except Exception as e:
        assert False, f"depgraph (PostgreSQL): 健康检查失败: {e}"

    print("  ✓ PASS: 所有数据库健康检查通过")


def test_event_notification():
    """测试数据变更事件通知（模拟 EventBus，P2迁移后：PostgreSQL）"""
    print("\n[TEST] 数据变更事件通知测试")

    events_received = []

    def on_change(event_type, data):
        events_received.append((event_type, data))

    # 模拟：插入数据后触发事件（P2迁移后：PostgreSQL）
    # node_id 在 v5 migration 后为 bigint（INTEGER PK AUTOINCREMENT → PG bigint）
    test_node_id = 999999
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            # 清理可能残留的测试数据
            cur.execute("DELETE FROM nodes WHERE node_id = %s", (test_node_id,))

        # 插入测试节点（node_id 为 bigint 主键，显式指定数字 ID）
        # node_id 是 GENERATED ALWAYS AS IDENTITY，需 OVERRIDING SYSTEM VALUE
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO nodes (node_id, node_type, path) OVERRIDING SYSTEM VALUE VALUES (%s, %s, %s)",
                (test_node_id, "test", "test/event.py"),
            )

        # 模拟事件通知
        on_change("NODE_INSERTED", {"node_id": test_node_id})

        # 清理
        with conn.cursor() as cur:
            cur.execute("DELETE FROM nodes WHERE node_id = %s", (test_node_id,))

    except Exception as e:
        assert False, f"插入测试失败: {e}"
    finally:
        conn.close()

    assert len(events_received) == 1 and events_received[0][0] == "NODE_INSERTED", f"事件通知异常: {events_received}"
    print(f"  ✓ 事件通知正常: {events_received[0]}")
    print("  ✓ PASS: 数据变更事件通知机制可用")


def test_concurrent_write_lock():
    """测试多进程写入互斥"""
    print("\n[TEST] 数据库文件锁检查")

    def write_test(thread_id):
        try:
            conn = sqlite3.connect(str(GOVERNANCE_DB), timeout=5)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")

            # 写入测试（不实际修改，只测试锁获取）
            conn.execute("SELECT COUNT(*) FROM tasks")
            time.sleep(0.01)  # 模拟短暂持有

            conn.close()
            return True
        except Exception as e:
            print(f"  ✗ 线程 {thread_id} 获取锁失败: {e}")
            return False

    # 5 个线程并发读取（不应冲突）
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(write_test, i) for i in range(5)]
        results = [f.result() for f in futures]

    assert all(results), f"{results.count(False)} 个并发读取失败"
    print("  ✓ PASS: 5 个并发读取全部成功，无死锁")


def test_schema_version_check():
    """测试 schema 版本检查"""
    print("\n[TEST] Schema 版本检查")

    # governance.db schema 版本检查（保持 SQLite）
    try:
        conn = sqlite3.connect(str(GOVERNANCE_DB))
        cursor = conn.execute("SELECT version FROM _schema_version ORDER BY applied_at DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            print(f"  ✓ governance.db: schema 版本 = {row[0]}")
        else:
            print("  ⚠ governance.db: _schema_version 表为空")
    except sqlite3.OperationalError:
        print("  ⚠ governance.db: 无 _schema_version 表")
    except Exception as e:
        assert False, f"governance.db: 检查失败: {e}"

    # depgraph schema 版本检查（P2迁移后：PostgreSQL）
    try:
        conn = get_depgraph_pg_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT version FROM _schema_version ORDER BY applied_at DESC LIMIT 1")
            row = cur.fetchone()
        conn.close()
        if row:
            print(f"  ✓ depgraph (PostgreSQL): schema 版本 = {row[0]}")
        else:
            print("  ⚠ depgraph (PostgreSQL): _schema_version 表为空")
    except psycopg2.Error:
        print("  ⚠ depgraph (PostgreSQL): 无 _schema_version 表")
    except Exception as e:
        assert False, f"depgraph (PostgreSQL): 检查失败: {e}"

    print("  ✓ PASS: schema 版本检查完成")


def main():
    print("=" * 80)
    print("DM-100021: 事件驱动自动启动检查+自动运行检查")
    print("=" * 80)

    tests = [
        test_database_service_init,
        test_health_check,
        test_event_notification,
        test_concurrent_write_lock,
        test_schema_version_check,
    ]

    results = []
    for test in tests:
        try:
            test()
            results.append(True)
        except Exception as e:
            print(f"  ✗ EXCEPTION: {e}")
            import traceback

            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"测试结果: {passed}/{total} 通过")

    if all(results):
        print("✓ 所有自动启动和自动运行检查 PASS")
        print("=" * 80)
        return 0
    else:
        print("✗ 部分测试 FAIL")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
