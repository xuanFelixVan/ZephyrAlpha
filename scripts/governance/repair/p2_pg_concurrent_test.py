#!/usr/bin/env python3
"""P2-T6 PostgreSQL 40并发写入红蓝测试。

验证 PG 迁移后能否支持 40 AI 并发写入（SQLite 时代的核心痛点）。

测试场景：
  T1: 40 并发 INSERT（独立行，无冲突）—— 验证基础并发写入
  T2: 40 并发 UPDATE 同一行 —— 验证行锁串行化（无死锁）
  T3: 40 并发 INSERT + 40 并发 SELECT —— 验证 MVCC 读写不阻塞
  T4: 2 个事务死锁场景 —— 验证 PG 死锁检测与自动恢复
  T5: 40 并发连接 + 事务回滚 —— 验证事务隔离

安全保证：
  - 使用独立测试表 _p2_concurrent_test，不污染生产数据
  - 测试完成后自动清理测试表
  - 所有写入在事务中，可回滚
"""
from __future__ import annotations

__manifest__ = """
args: []
description: P2-T6 PostgreSQL 40并发写入红蓝测试。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
for p in (str(_REPO_ROOT), str(_SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)

import psycopg2
from _shared.constants import EXIT_ERROR
from psycopg2.extras import RealDictCursor

from zephyr.governance.depgraph_schema import _load_pg_config, get_depgraph_pg_connection

RESULTS: list[tuple[str, bool, str]] = []
TEST_TABLE = "_p2_concurrent_test"


def _get_pg_user() -> str:
    """获取普通 PG 用户名（用于 GRANT）。"""
    return _load_pg_config()["POSTGRES_USER"]


def _record(name: str, ok: bool, detail: str) -> None:
    """_record implementation."""
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name}: {detail[:120]}")
    RESULTS.append((name, ok, detail))


def _setup_test_table() -> None:
    """创建临时测试表（如果存在则先删除），并 GRANT 权限给普通用户。"""
    pg_user = _get_pg_user()
    conn = get_depgraph_pg_connection(autocommit=True, superuser=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"DROP TABLE IF EXISTS {TEST_TABLE}")
            cur.execute(f"""
                CREATE TABLE {TEST_TABLE} (
                    id INTEGER PRIMARY KEY,
                    worker_id INTEGER NOT NULL,
                    value TEXT,
                    counter INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            # GRANT 权限给普通用户（测试 worker 用普通用户连接）
            cur.execute(f"GRANT ALL ON TABLE {TEST_TABLE} TO {pg_user}")
            # 授予序列权限（虽然此表无 SERIAL，但为完整性保留）
            cur.execute(f"GRANT ALL ON SCHEMA public TO {pg_user}")
        print(f"[SETUP] 测试表 {TEST_TABLE} 已创建，权限已授予 {pg_user}")
    finally:
        conn.close()


def _cleanup_test_table() -> None:
    """清理测试表。"""
    conn = get_depgraph_pg_connection(autocommit=True, superuser=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"DROP TABLE IF EXISTS {TEST_TABLE}")
        print(f"[CLEANUP] 测试表 {TEST_TABLE} 已删除")
    finally:
        conn.close()


# ============================================================================
# T1: 40 并发 INSERT（独立行，无冲突）
# ============================================================================

def _t1_worker(worker_id: int) -> tuple[int, bool, str]:
    """每个 worker 插入一行。"""
    try:
        conn = get_depgraph_pg_connection(autocommit=False)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {TEST_TABLE} (id, worker_id, value) VALUES (%s, %s, %s)",
                    (worker_id, worker_id, f"value-{worker_id}"),
                )
            conn.commit()
            return (worker_id, True, "OK")
        except Exception as e:
            conn.rollback()
            return (worker_id, False, str(e)[:100])
        finally:
            conn.close()
    except Exception as e:
        return (worker_id, False, f"connect: {str(e)[:100]}")


def test_t1_concurrent_insert() -> None:
    """T1: 40 并发 INSERT。"""
    print("\n=== T1: 40 并发 INSERT ===")
    start = time.time()
    with ThreadPoolExecutor(max_workers=40) as pool:
        futures = [pool.submit(_t1_worker, i) for i in range(40)]
        results = [f.result() for f in as_completed(futures)]
    elapsed = time.time() - start

    ok_count = sum(1 for _, ok, _ in results if ok)
    fail_count = 40 - ok_count
    # 验证数据完整性
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS cnt FROM {TEST_TABLE}")
            row_count = cur.fetchone()[0]
    finally:
        conn.close()

    passed = ok_count == 40 and row_count == 40
    _record("T1 40并发INSERT",
            passed,
            f"成功={ok_count}/40, 表行数={row_count}, 耗时={elapsed:.2f}s, 失败={fail_count}")


# ============================================================================
# T2: 40 并发 UPDATE 同一行（验证行锁串行化）
# ============================================================================

def _t2_worker(worker_id: int) -> tuple[int, bool, str]:
    """每个 worker 更新同一行的 counter。"""
    try:
        conn = get_depgraph_pg_connection(autocommit=False)
        try:
            with conn.cursor() as cur:
                # SELECT ... FOR UPDATE 获取行锁
                cur.execute(f"SELECT counter FROM {TEST_TABLE} WHERE id=0 FOR UPDATE")
                row = cur.fetchone()
                if row is None:
                    return (worker_id, False, "row not found")
                new_val = row[0] + 1
                cur.execute(
                    f"UPDATE {TEST_TABLE} SET counter=%s WHERE id=0",
                    (new_val,),
                )
            conn.commit()
            return (worker_id, True, f"counter→{new_val}")
        except Exception as e:
            conn.rollback()
            return (worker_id, False, str(e)[:100])
        finally:
            conn.close()
    except Exception as e:
        return (worker_id, False, f"connect: {str(e)[:100]}")


def test_t2_concurrent_update_same_row() -> None:
    """T2: 40 并发 UPDATE 同一行。"""
    print("\n=== T2: 40 并发 UPDATE 同一行（行锁串行化）===")
    # 清理 T1 残留数据，然后插入 id=0 的行
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {TEST_TABLE}")
            cur.execute(f"INSERT INTO {TEST_TABLE} (id, worker_id, counter) VALUES (0, 0, 0)")
    finally:
        conn.close()

    start = time.time()
    with ThreadPoolExecutor(max_workers=40) as pool:
        futures = [pool.submit(_t2_worker, i) for i in range(40)]
        results = [f.result() for f in as_completed(futures)]
    elapsed = time.time() - start

    ok_count = sum(1 for _, ok, _ in results if ok)
    # 验证 counter 最终值
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT counter FROM {TEST_TABLE} WHERE id=0")
            row = cur.fetchone()
            final_counter = row[0] if row else -1
    finally:
        conn.close()

    # 行锁串行化下，counter 应该正好 +40（无丢失更新）
    passed = ok_count == 40 and final_counter == 40
    _record("T2 40并发UPDATE同行",
            passed,
            f"成功={ok_count}/40, counter={final_counter}(期望40), 耗时={elapsed:.2f}s")


# ============================================================================
# T3: 40 并发 INSERT + 40 并发 SELECT（MVCC 读写不阻塞）
# ============================================================================

def _t3_writer(worker_id: int) -> tuple[int, bool, str]:
    """写入者：插入行。"""
    try:
        conn = get_depgraph_pg_connection(autocommit=False)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {TEST_TABLE} (id, worker_id, value) VALUES (%s, %s, %s)",
                    (1000 + worker_id, worker_id, f"write-{worker_id}"),
                )
            conn.commit()
            return (worker_id, True, "OK")
        except Exception as e:
            conn.rollback()
            return (worker_id, False, str(e)[:100])
        finally:
            conn.close()
    except Exception as e:
        return (worker_id, False, f"connect: {str(e)[:100]}")


def _t3_reader(worker_id: int) -> tuple[int, bool, str]:
    """读取者：查询表。"""
    try:
        conn = get_depgraph_pg_connection(autocommit=True)
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) AS cnt FROM {TEST_TABLE}")
                cnt = cur.fetchone()[0]
            return (worker_id, True, f"count={cnt}")
        finally:
            conn.close()
    except Exception as e:
        return (worker_id, False, str(e)[:100])


def test_t3_concurrent_read_write() -> None:
    """T3: 40 并发写 + 40 并发读。"""
    print("\n=== T3: 40 并发写 + 40 并发读（MVCC 读写不阻塞）===")
    # 清理之前的测试数据
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {TEST_TABLE} WHERE id >= 1000")
    finally:
        conn.close()

    start = time.time()
    with ThreadPoolExecutor(max_workers=80) as pool:
        write_futures = [pool.submit(_t3_writer, i) for i in range(40)]
        read_futures = [pool.submit(_t3_reader, i) for i in range(40)]
        all_results = [f.result() for f in as_completed(write_futures + read_futures)]
    elapsed = time.time() - start

    write_results = [r for r in all_results if r[0] < 1000]  # writer_id 0-39
    read_results = [r for r in all_results if r[0] >= 1000]  # reader 用 1000+ 标记？不对

    # 重新分类：writer 和 reader 都用 0-39，需要通过 future 区分
    # 简化：只看总数
    ok_count = sum(1 for _, ok, _ in all_results if ok)
    fail_count = len(all_results) - ok_count

    # 验证写入的 40 行存在
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS cnt FROM {TEST_TABLE} WHERE id >= 1000")
            write_count = cur.fetchone()[0]
    finally:
        conn.close()

    passed = ok_count == 80 and write_count == 40
    _record("T3 40并发读写",
            passed,
            f"成功={ok_count}/80, 写入行={write_count}(期望40), 耗时={elapsed:.2f}s, 失败={fail_count}")


# ============================================================================
# T4: 死锁检测与自动恢复
# ============================================================================

def _t4_deadlock_worker_a() -> tuple[bool, str]:
    """Worker A: 先锁 id=2000，再锁 id=2001。"""
    try:
        conn = get_depgraph_pg_connection(autocommit=False)
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT counter FROM {TEST_TABLE} WHERE id=2000 FOR UPDATE")
                time.sleep(0.5)  # 等待 B 锁定 2001
                cur.execute(f"SELECT counter FROM {TEST_TABLE} WHERE id=2001 FOR UPDATE")
            conn.commit()
            return (True, "A OK")
        except psycopg2.errors.DeadlockDetected:
            conn.rollback()
            return (True, "A deadlock-detected-and-recovered")
        except Exception as e:
            conn.rollback()
            return (False, f"A error: {str(e)[:80]}")
        finally:
            conn.close()
    except Exception as e:
        return (False, f"A connect: {str(e)[:80]}")


def _t4_deadlock_worker_b() -> tuple[bool, str]:
    """Worker B: 先锁 id=2001，再锁 id=2000（相反顺序，制造死锁）。"""
    try:
        conn = get_depgraph_pg_connection(autocommit=False)
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT counter FROM {TEST_TABLE} WHERE id=2001 FOR UPDATE")
                time.sleep(0.5)  # 等待 A 锁定 2000
                cur.execute(f"SELECT counter FROM {TEST_TABLE} WHERE id=2000 FOR UPDATE")
            conn.commit()
            return (True, "B OK")
        except psycopg2.errors.DeadlockDetected:
            conn.rollback()
            return (True, "B deadlock-detected-and-recovered")
        except Exception as e:
            conn.rollback()
            return (False, f"B error: {str(e)[:80]}")
        finally:
            conn.close()
    except Exception as e:
        return (False, f"B connect: {str(e)[:80]}")


def test_t4_deadlock_detection() -> None:
    """T4: 死锁检测与自动恢复。"""
    print("\n=== T4: 死锁检测与自动恢复 ===")
    # 清理并插入两行用于死锁测试
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {TEST_TABLE} WHERE id IN (2000, 2001)")
            cur.execute(f"INSERT INTO {TEST_TABLE} (id, worker_id, counter) VALUES (2000, 0, 0)")
            cur.execute(f"INSERT INTO {TEST_TABLE} (id, worker_id, counter) VALUES (2001, 0, 0)")
    finally:
        conn.close()

    start = time.time()
    with ThreadPoolExecutor(max_workers=2) as pool:
        fa = pool.submit(_t4_deadlock_worker_a)
        fb = pool.submit(_t4_deadlock_worker_b)
        ra = fa.result()
        rb = fb.result()
    elapsed = time.time() - start

    # 预期：一个成功，一个被死锁检测中止（PG 自动检测并回滚其中一个）
    # 两个都不应 hang
    both_ok = ra[0] and rb[0]
    one_deadlock = "deadlock" in ra[1].lower() or "deadlock" in rb[1].lower()
    passed = both_ok and (one_deadlock or elapsed < 5)
    _record("T4 死锁检测",
            passed,
            f"A={ra[1]}, B={rb[1]}, 耗时={elapsed:.2f}s")


# ============================================================================
# T5: 40 并发事务回滚（验证事务隔离）
# ============================================================================

def _t5_worker(worker_id: int) -> tuple[int, bool, str]:
    """每个 worker 开启事务，插入后回滚。"""
    try:
        conn = get_depgraph_pg_connection(autocommit=False)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {TEST_TABLE} (id, worker_id, value) VALUES (%s, %s, %s)",
                    (3000 + worker_id, worker_id, f"rollback-{worker_id}"),
                )
            conn.rollback()  # 显式回滚
            return (worker_id, True, "rolled back")
        except Exception as e:
            conn.rollback()
            return (worker_id, False, str(e)[:100])
        finally:
            conn.close()
    except Exception as e:
        return (worker_id, False, f"connect: {str(e)[:100]}")


def test_t5_concurrent_rollback() -> None:
    """T5: 40 并发事务回滚。"""
    print("\n=== T5: 40 并发事务回滚（事务隔离）===")
    start = time.time()
    with ThreadPoolExecutor(max_workers=40) as pool:
        futures = [pool.submit(_t5_worker, i) for i in range(40)]
        results = [f.result() for f in as_completed(futures)]
    elapsed = time.time() - start

    ok_count = sum(1 for _, ok, _ in results if ok)
    # 验证回滚的行不存在
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS cnt FROM {TEST_TABLE} WHERE id >= 3000")
            rolled_back_count = cur.fetchone()[0]
    finally:
        conn.close()

    passed = ok_count == 40 and rolled_back_count == 0
    _record("T5 40并发事务回滚",
            passed,
            f"成功={ok_count}/40, 残留行={rolled_back_count}(期望0), 耗时={elapsed:.2f}s")


# ============================================================================
# 主流程
# ============================================================================

def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    print("=" * 70)
    print("P2-T6 PostgreSQL 40并发写入红蓝测试")
    print("=" * 70)

    # 前置检查：PG 连接
    try:
        conn = get_depgraph_pg_connection(autocommit=True)
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
        conn.close()
        print(f"[PG] 连接成功: {version[:60]}")
    except Exception as e:
        print(f"[PG] 连接失败: {e}")
        return EXIT_ERROR
    try:
        _setup_test_table()
        test_t1_concurrent_insert()
        test_t2_concurrent_update_same_row()
        test_t3_concurrent_read_write()
        test_t4_deadlock_detection()
        test_t5_concurrent_rollback()
    finally:
        _cleanup_test_table()

    print("\n" + "=" * 70)
    print("汇总")
    print("=" * 70)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = sum(1 for _, ok, _ in RESULTS if not ok)
    for name, ok, detail in RESULTS:
        mark = "OK" if ok else "XX"
        print(f"  [{mark}] {name}: {detail[:100]}")
    print(f"\n总计: {passed} PASS / {failed} FAIL / {len(RESULTS)} ALL")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
