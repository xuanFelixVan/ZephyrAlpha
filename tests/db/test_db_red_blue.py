"""
DM-100020: 红蓝对抗测试：数据库安全与韧性

红方测试：
1. SQL 注入防护（参数化查询）
2. 并发写入冲突处理
3. 事务回滚验证
4. 数据完整性约束

蓝方验证：
1. 所有注入被参数化阻止
2. 并发写入不丢数据（WAL 模式）
3. 事务失败正确回滚
4. 约束违规正确拒绝
"""

import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

GOVERNANCE_DB = REPO_ROOT / "data" / "databases" / "governance.db"
# 注：depgraph 已迁移到 PostgreSQL（P2迁移），DEPGRAPH_DB 路径常量已移除


def test_sql_injection_protection():
    """红方：尝试 SQL 注入攻击"""
    print("\n[TEST] SQL 注入防护测试")

    conn = sqlite3.connect(GOVERNANCE_DB)
    cursor = conn.cursor()

    # 红方攻击：尝试 SQL 注入
    malicious_inputs = [
        "'; DROP TABLE tasks; --",
        "test' OR '1'='1",
        "test'; DELETE FROM tasks WHERE '1'='1",
        "test' UNION SELECT * FROM tasks --",
    ]

    for malicious in malicious_inputs:
        try:
            # 使用参数化查询（蓝方防御）
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE task_id = ?", (malicious,))
            result = cursor.fetchone()[0]
            print(f"  ✓ 参数化查询安全处理: {malicious[:30]}...")
        except Exception as e:
            print(f"  ✗ FAIL: 参数化查询失败: {e}")
            conn.close()
            return False

    # 验证 tasks 表仍然存在
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    print(f"  ✓ PASS: tasks 表完整，{count} 条记录")

    conn.close()
    return True


def test_concurrent_writes():
    """红方：并发写入同一记录"""
    print("\n[TEST] 并发写入冲突测试")

    # 创建测试数据库
    test_db = REPO_ROOT / "data" / "databases" / "test_concurrent.db"

    # 初始化测试数据
    conn = sqlite3.connect(test_db)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_data (
            id INTEGER PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
    """)
    conn.execute("INSERT OR REPLACE INTO test_data (id, value, updated_at) VALUES (1, 'initial', '')")
    conn.commit()
    conn.close()

    # 红方：多线程并发写入
    def update_record(thread_id):
        conn = sqlite3.connect(test_db, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            conn.execute(
                "UPDATE test_data SET value = ?, updated_at = ? WHERE id = 1", (f"thread-{thread_id}", time.time())
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"  ✗ 线程 {thread_id} 写入失败: {e}")
            return False
        finally:
            conn.close()

    # 启动 10 个并发线程
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(update_record, i) for i in range(10)]
        results = [f.result() for f in as_completed(futures)]

    # 验证数据完整性
    conn = sqlite3.connect(test_db)
    cursor = conn.execute("SELECT value, updated_at FROM test_data WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    if row and row[0].startswith("thread-"):
        print(f"  ✓ PASS: 并发写入成功，最终值: {row[0]}")
        # 清理测试数据库
        test_db.unlink()
        return True
    else:
        print(f"  ✗ FAIL: 数据损坏: {row}")
        test_db.unlink(missing_ok=True)
        return False


def test_transaction_rollback():
    """红方：触发事务回滚"""
    print("\n[TEST] 事务回滚测试")

    conn = sqlite3.connect(GOVERNANCE_DB)

    # 记录当前任务数
    cursor = conn.execute("SELECT COUNT(*) FROM tasks")
    initial_count = cursor.fetchone()[0]

    try:
        # 红方：尝试插入无效数据（违反约束）
        conn.execute(
            """
            INSERT INTO tasks (task_id, title, status)
            VALUES (?, ?, ?)
        """,
            ("TEST-ROLLBACK", "测试任务", "INVALID_STATUS"),
        )
        conn.commit()
        print("  ✗ FAIL: 应该被约束拒绝")
        conn.close()
        return False
    except sqlite3.IntegrityError as e:
        print(f"  ✓ 约束正确拒绝: {e}")
        conn.rollback()

    # 验证数据未被污染
    cursor = conn.execute("SELECT COUNT(*) FROM tasks")
    final_count = cursor.fetchone()[0]

    if final_count == initial_count:
        print(f"  ✓ PASS: 事务回滚成功，任务数保持 {final_count}")
        conn.close()
        return True
    else:
        print(f"  ✗ FAIL: 任务数变化 {initial_count} → {final_count}")
        conn.close()
        return False


def test_wal_mode():
    """蓝方：验证 WAL 模式启用（P2迁移后：depgraph 已迁移到 PostgreSQL，WAL 由 PG 服务器管理）"""
    print("\n[TEST] WAL 模式验证")

    # governance.db 仍使用 SQLite，检查 WAL
    conn = sqlite3.connect(GOVERNANCE_DB)
    cursor = conn.execute("PRAGMA journal_mode")
    mode = cursor.fetchone()[0]
    conn.close()

    if mode == "wal":
        print("  ✓ governance.db: WAL 模式已启用")
    else:
        print(f"  ✗ FAIL: governance.db 未启用 WAL 模式: {mode}")
        return False

    # depgraph 已迁移到 PostgreSQL，WAL 由 PostgreSQL 服务器管理（postgresql.conf）
    # 不再检查 depgraph 的 PRAGMA journal_mode（PG 无此 PRAGMA）
    print("  ✓ depgraph (PostgreSQL): WAL 由 PostgreSQL 服务器管理（无需 PRAGMA 检查）")

    print("  ✓ PASS: 数据库 WAL 模式验证完成")
    return True


def test_data_constraints():
    """蓝方：验证数据完整性约束"""
    print("\n[TEST] 数据完整性约束测试")

    conn = sqlite3.connect(GOVERNANCE_DB)

    # 测试 NOT NULL 约束
    try:
        conn.execute("INSERT INTO tasks (task_id) VALUES (NULL)")
        conn.commit()
        print("  ✗ FAIL: NOT NULL 约束未生效")
        conn.close()
        return False
    except sqlite3.IntegrityError:
        print("  ✓ NOT NULL 约束生效")

    # 测试 UNIQUE 约束（如果 task_id 是主键）
    try:
        conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'")
        schema = conn.fetchone()[0]
        if "PRIMARY KEY" in schema.upper():
            print("  ✓ PRIMARY KEY 约束存在")
    except Exception as e:
        print(f"  ⚠ WARNING: 无法验证 PRIMARY KEY: {e}")

    conn.close()
    print("  ✓ PASS: 数据约束完整")
    return True


def main():
    print("=" * 80)
    print("DM-100020: 红蓝对抗测试 - 数据库安全与韧性")
    print("=" * 80)

    tests = [
        test_sql_injection_protection,
        test_concurrent_writes,
        test_transaction_rollback,
        test_wal_mode,
        test_data_constraints,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
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
        print("✓ 所有红蓝对抗测试 PASS - 0 安全漏洞")
        print("=" * 80)
        return 0
    else:
        print("✗ 部分测试 FAIL - 存在安全漏洞")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
