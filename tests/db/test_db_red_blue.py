# [A_test] module_id: SRC-TST-0118 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] tests.db.test_db_red_blue
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""DM-100020: 红蓝对抗测试：数据库安全与韧性

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

测试隔离：本测试使用 tmp_db fixture（init_db 初始化的临时 SQLite）隔离生产库；
         WAL 模式验证为 E2E 只读测试，使用 governance_db_path fixture。
         路径通过 fixture 派生（真源：zephyr.shared.io.paths.DB_PATH）。
"""
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pytest
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


def _seed_tasks(db_path: Path) -> None:
    """向临时库 tasks 表插入测试数据（满足所有 NOT NULL + CHECK 约束）。"""
    now = datetime.now().isoformat()
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT OR REPLACE INTO tasks
           (task_id, namespace, seq, title, status, priority, phase,
            execution_model, safety_level, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("RED-BLUE-001", "DM", 1, "红蓝对抗基线任务", "COMPLETED", "P2", 0, "glm", "L", now, now),
    )
    conn.commit()
    conn.close()


def test_sql_injection_protection(tmp_db: Path):
    """红方：尝试 SQL 注入攻击（隔离 tmp_db，不污染生产库）"""
    print("\n[TEST] SQL 注入防护测试")
    _seed_tasks(tmp_db)

    conn = sqlite3.connect(tmp_db)
    cursor = conn.cursor()

    # 红方攻击：尝试 SQL 注入
    malicious_inputs = [
        "'; DROP TABLE tasks; --",
        "test' OR '1'='1",
        "test'; DELETE FROM tasks WHERE '1'='1",
        "test' UNION SELECT * FROM tasks --",
    ]

    for malicious in malicious_inputs:
        # 使用参数化查询（蓝方防御）
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE task_id = ?", (malicious,))
        cursor.fetchone()  # 不崩溃即通过
        print(f"  ✓ 参数化查询安全处理: {malicious[:30]}...")

    # 验证 tasks 表仍然存在
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    assert count == 1, f"tasks 表应只有 1 条记录，实际 {count}"
    print(f"  ✓ PASS: tasks 表完整，{count} 条记录")

    conn.close()


def test_concurrent_writes(tmp_path: Path):
    """红方：并发写入同一记录（隔离 tmp_path，不污染生产库目录）"""
    print("\n[TEST] 并发写入冲突测试")

    # 创建测试数据库（tmp_path 隔离）
    test_db = tmp_path / "test_concurrent.db"

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

    assert all(results), "部分线程写入失败"

    # 验证数据完整性
    conn = sqlite3.connect(test_db)
    cursor = conn.execute("SELECT value, updated_at FROM test_data WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "数据损坏：未找到记录"
    assert row[0].startswith("thread-"), f"数据损坏: {row}"
    print(f"  ✓ PASS: 并发写入成功，最终值: {row[0]}")


def test_transaction_rollback(tmp_db: Path):
    """红方：触发事务回滚（隔离 tmp_db，不污染生产库）"""
    print("\n[TEST] 事务回滚测试")
    _seed_tasks(tmp_db)

    conn = sqlite3.connect(tmp_db)

    # 记录当前任务数
    cursor = conn.execute("SELECT COUNT(*) FROM tasks")
    initial_count = cursor.fetchone()[0]

    # 红方：尝试插入无效数据（违反 CHECK 约束，其他字段满足 NOT NULL）
    now = datetime.now().isoformat()
    with pytest.raises(sqlite3.IntegrityError) as exc_info:
        conn.execute(
            """
            INSERT INTO tasks
            (task_id, namespace, seq, title, status, priority, phase,
             execution_model, safety_level, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            ("TEST-ROLLBACK", "DM", 2, "测试任务", "INVALID_STATUS", "P2", 0, "glm", "L", now, now),
        )
        conn.commit()
    print(f"  ✓ 约束正确拒绝: {exc_info.value}")
    conn.rollback()

    # 验证数据未被污染
    cursor = conn.execute("SELECT COUNT(*) FROM tasks")
    final_count = cursor.fetchone()[0]
    assert final_count == initial_count, f"任务数变化 {initial_count} → {final_count}"
    print(f"  ✓ PASS: 事务回滚成功，任务数保持 {final_count}")

    conn.close()


@pytest.mark.e2e
def test_wal_mode(governance_db_path: Path):
    """蓝方：验证 WAL 模式启用（E2E 只读，验证生产 governance.db 配置）"""
    print("\n[TEST] WAL 模式验证")

    # governance.db 仍使用 SQLite，检查 WAL
    conn = sqlite3.connect(governance_db_path)
    cursor = conn.execute("PRAGMA journal_mode")
    mode = cursor.fetchone()[0]
    conn.close()

    assert mode == "wal", f"governance.db 未启用 WAL 模式: {mode}"
    print("  ✓ governance.db: WAL 模式已启用")

    # depgraph 已迁移到 PostgreSQL，WAL 由 PostgreSQL 服务器管理（postgresql.conf）
    print("  ✓ depgraph (PostgreSQL): WAL 由 PostgreSQL 服务器管理（无需 PRAGMA 检查）")
    print("  ✓ PASS: 数据库 WAL 模式验证完成")


def test_data_constraints(tmp_db: Path):
    """蓝方：验证数据完整性约束（隔离 tmp_db，不污染生产库）"""
    print("\n[TEST] 数据完整性约束测试")

    conn = sqlite3.connect(tmp_db)

    # 测试 NOT NULL 约束
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO tasks (task_id) VALUES (NULL)")
        conn.commit()
    print("  ✓ NOT NULL 约束生效")

    # 测试 PRIMARY KEY 约束
    cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'")
    schema = cursor.fetchone()[0]
    assert "PRIMARY KEY" in schema.upper(), "PRIMARY KEY 约束不存在"
    print("  ✓ PRIMARY KEY 约束存在")

    conn.close()
    print("  ✓ PASS: 数据约束完整")


def main():
    """脚本入口：直接运行时执行测试（需生产库可用 + tmp 隔离）。"""
    from zephyr.shared.io.paths import DB_PATH
    import tempfile
    from zephyr.governance.persistence.sqlite_schema import init_db

    print("=" * 80)
    print("DM-100020: 红蓝对抗测试 - 数据库安全与韧性")
    print("=" * 80)

    # 为脚本模式创建 tmp_db（隔离）
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_db_path = Path(tmp_dir) / "test_zalpha.db"
        init_db(tmp_db_path)

        tests = [
            ("SQL 注入防护", lambda: test_sql_injection_protection(tmp_db_path)),
            ("并发写入", lambda: test_concurrent_writes(Path(tmp_dir))),
            ("事务回滚", lambda: test_transaction_rollback(tmp_db_path)),
            ("WAL 模式", lambda: test_wal_mode(DB_PATH)),
            ("数据约束", lambda: test_data_constraints(tmp_db_path)),
        ]

        results = []
        for name, test_fn in tests:
            try:
                test_fn()
                results.append(True)
            except Exception as e:
                print(f"  ✗ EXCEPTION [{name}]: {e}")
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
    sys.exit(main())
