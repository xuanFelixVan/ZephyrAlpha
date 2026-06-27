# [A_test] module_id: SRC-TST-0117 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] DM-100022 | src/zephyr/governance/database_service.py | §22
# [MODULE] tests.governance.test_database_service
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
R2-1: DatabaseService 测试 — DuckDB连接/健康检查/读写/连接池管理

覆盖项：
1. get_market_conn() 返回有效的DuckDB连接
2. health_check() 对market.duckdb执行SELECT 1并返回True
3. market.duckdb 读写验证（INSERT + SELECT + DELETE）
4. 连接池管理：写入锁串行化（单写入线程防护）
5. 批量APPEND：buffer_tick + flush_tick_batch
"""

import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

PROJECT_ROOT = REPO_ROOT  # alias 真源
sys.path.insert(0, str(PROJECT_ROOT / "src"))


@pytest.fixture
def db_service():
    """DatabaseService 实例 fixture（每个测试独立实例）"""
    from zephyr.governance.database_service import DatabaseService

    ds = DatabaseService()
    yield ds
    ds.close_all()


class TestDatabaseServiceConnection:
    """DatabaseService 连接测试"""

    def test_get_market_conn_returns_duckdb_connection(self, db_service):
        """验证 get_market_conn() 返回有效的DuckDB连接"""
        import duckdb

        conn = db_service.get_market_conn()
        assert conn is not None
        assert isinstance(conn, duckdb.DuckDBPyConnection)
        result = conn.execute("SELECT 1").fetchone()
        assert result[0] == 1

    def test_get_governance_conn_returns_sqlite(self, db_service):
        """验证 governance.db 连接"""
        import sqlite3

        conn = db_service.get_governance_conn()
        assert isinstance(conn, sqlite3.Connection)
        result = conn.execute("SELECT 1").fetchone()
        assert result[0] == 1

    def test_get_depgraph_conn_returns_pg(self, db_service):
        """验证 depgraph (PostgreSQL) 连接（P2迁移后：psycopg2）"""
        import psycopg2

        conn = db_service.get_depgraph_conn()
        assert isinstance(conn, psycopg2.extensions.connection)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        # RealDictCursor 返回 RealDictRow，用 values() 兼容数字索引访问
        assert list(result.values())[0] == 1

    def test_get_market_read_conn_works(self, db_service):
        """验证只读连接可执行查询"""
        with db_service.get_market_read_conn() as read_conn:
            result = read_conn.execute("SELECT 1").fetchone()
            assert result[0] == 1


class TestHealthCheck:
    """健康检查测试 — SELECT 1 + WAL检查 + schema版本检查"""

    def test_health_check_returns_dict_with_all_keys(self, db_service):
        """验证 health_check() 返回包含三库键的字典"""
        result = db_service.health_check()
        assert isinstance(result, dict)
        assert "governance" in result
        assert "depgraph" in result
        assert "market" in result

    def test_health_check_market_returns_true(self, db_service):
        """验证 health_check() 对market.duckdb执行SELECT 1并返回True"""
        result = db_service.health_check()
        assert result["market"] is True, f"market健康检查失败: {result}"

    def test_health_check_governance_returns_true(self, db_service):
        """验证 governance.db 健康检查通过"""
        result = db_service.health_check()
        assert result["governance"] is True

    def test_health_check_depgraph_returns_true(self, db_service):
        """验证 depgraph.db 健康检查通过"""
        result = db_service.health_check()
        assert result["depgraph"] is True

    def test_health_check_all_pass(self, db_service):
        """验证三库健康检查全部通过"""
        result = db_service.health_check()
        assert all(result.values()), f"部分数据库健康检查失败: {result}"


class TestMarketSchema:
    """market.duckdb schema版本检查"""

    def test_expected_tables_exist(self, db_service):
        """验证 market.duckdb 预期表全部存在"""
        from zephyr.governance.database_service import DatabaseService

        conn = db_service.get_market_conn()
        tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
        missing = DatabaseService.EXPECTED_MARKET_TABLES - tables
        assert not missing, f"缺失表: {missing}"

    def test_duckdb_version_available(self, db_service):
        """验证 DuckDB 版本可查询（WAL引擎可用性代理检查）"""
        conn = db_service.get_market_conn()
        version_row = conn.execute("PRAGMA version").fetchone()
        assert version_row is not None
        assert version_row[0].startswith("v"), f"DuckDB版本格式异常: {version_row[0]}"


class TestMarketReadWrite:
    """market.duckdb 读写测试"""

    def test_tick_data_insert_select_delete(self, db_service):
        """验证 tick_data 表读写（INSERT + SELECT + DELETE）"""
        conn = db_service.get_market_conn()
        test_symbol = "TEST_R2_1"
        test_ts = datetime(2026, 6, 22, 0, 0, 0, tzinfo=timezone.utc)

        test_tick = {
            "symbol": test_symbol,
            "timestamp": test_ts,
            "price": 100.0,
            "volume": 1000,
            "amount": 100000.0,
            "bid1": 99.9,
            "ask1": 100.1,
            "bid_vol1": 500,
            "ask_vol1": 500,
            "data_source": "test_r2_1",
            "quality_score": 1,
        }
        db_service.insert_tick_data(test_tick)

        try:
            row = conn.execute(
                "SELECT symbol, price, volume, data_source FROM tick_data WHERE symbol=? AND timestamp=?",
                (test_symbol, test_ts),
            ).fetchone()
            assert row is not None, "写入的tick数据未找到"
            assert row[0] == test_symbol
            assert row[1] == 100.0
            assert row[2] == 1000
            assert row[3] == "test_r2_1"
        finally:
            with db_service.market_write_lock():
                conn.execute("DELETE FROM tick_data WHERE symbol=? AND timestamp=?", (test_symbol, test_ts))

    def test_tick_data_cleanup_verified(self, db_service):
        """验证测试数据清理干净（无残留）"""
        conn = db_service.get_market_conn()
        count = conn.execute("SELECT COUNT(*) FROM tick_data WHERE data_source='test_r2_1'").fetchone()[0]
        assert count == 0, f"测试数据残留: {count}条"


class TestConnectionPool:
    """连接池管理测试 — DuckDB单文件锁竞争防护"""

    def test_market_write_lock_acquire_release(self, db_service):
        """验证写入锁可正常获取和释放"""
        with db_service.market_write_lock():
            # 锁内可执行写操作
            conn = db_service.get_market_conn()
            conn.execute("SELECT 1").fetchone()
        # 锁释放后可再次获取
        with db_service.market_write_lock():
            pass

    def test_market_write_lock_not_reentrant(self, db_service):
        """验证写入锁不可重入（单写入线程串行化）"""
        db_service.WRITE_LOCK_TIMEOUT = 0.5
        with db_service.market_write_lock():
            with pytest.raises(TimeoutError):
                with db_service.market_write_lock():
                    pass

    def test_market_write_lock_serializes_threads(self, db_service):
        """验证写入锁串行化多线程写入"""
        db_service.WRITE_LOCK_TIMEOUT = 1.0
        execution_order = []
        lock = threading.Lock()

        def writer(thread_id):
            try:
                with db_service.market_write_lock():
                    with lock:
                        execution_order.append(("start", thread_id))
                    # 模拟写操作
                    conn = db_service.get_market_conn()
                    conn.execute("SELECT 1").fetchone()
                    with lock:
                        execution_order.append(("end", thread_id))
            except TimeoutError:
                with lock:
                    execution_order.append(("timeout", thread_id))

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        # 所有线程应完成（无timeout）
        timeouts = [e for e in execution_order if e[0] == "timeout"]
        assert len(timeouts) == 0, f"线程超时: {timeouts}"
        # 所有线程应串行执行（start-end-start-end模式）
        assert len(execution_order) == 6, f"执行顺序异常: {execution_order}"


class TestBatchAppend:
    """批量APPEND测试 — DuckDB单文件锁竞争缓解"""

    def test_buffer_tick_accumulates(self, db_service):
        """验证 buffer_tick 缓冲累积"""
        base_ts = datetime(2026, 6, 22, 1, 0, 0, tzinfo=timezone.utc)
        for i in range(5):
            count = db_service.buffer_tick(
                {
                    "symbol": "TEST_BUFFER",
                    "timestamp": base_ts.replace(minute=i),
                    "price": 100.0 + i,
                    "volume": 1000,
                    "amount": 100000.0,
                    "bid1": 99.9,
                    "ask1": 100.1,
                    "bid_vol1": 500,
                    "ask_vol1": 500,
                    "data_source": "test_buffer",
                    "quality_score": 1,
                }
            )
        assert count == 5
        # 清理未刷新的缓冲
        db_service._tick_batch_buffer.clear()

    def test_flush_empty_buffer_returns_zero(self, db_service):
        """验证空缓冲区刷新返回0"""
        result = db_service.flush_tick_batch()
        assert result == 0

    def test_batch_insert_and_cleanup(self, db_service):
        """验证批量APPEND写入和清理"""
        conn = db_service.get_market_conn()
        test_symbol = "TEST_BATCH_R2_1"
        base_ts = datetime(2026, 6, 22, 2, 0, 0, tzinfo=timezone.utc)

        for i in range(3):
            db_service.buffer_tick(
                {
                    "symbol": test_symbol,
                    "timestamp": base_ts.replace(minute=i),
                    "price": 200.0 + i,
                    "volume": 2000,
                    "amount": 200000.0,
                    "bid1": 199.9,
                    "ask1": 200.1,
                    "bid_vol1": 1000,
                    "ask_vol1": 1000,
                    "data_source": "test_batch",
                    "quality_score": 1,
                }
            )

        written = db_service.flush_tick_batch()
        assert written == 3, f"预期写入3条，实际{written}"

        try:
            rows = conn.execute(
                "SELECT symbol, price FROM tick_data WHERE symbol=? AND data_source='test_batch' ORDER BY price",
                (test_symbol,),
            ).fetchall()
            assert len(rows) == 3
            assert rows[0][1] == 200.0
            assert rows[1][1] == 201.0
            assert rows[2][1] == 202.0
        finally:
            with db_service.market_write_lock():
                conn.execute("DELETE FROM tick_data WHERE symbol=? AND data_source='test_batch'", (test_symbol,))


class TestCloseAll:
    """连接关闭测试"""

    def test_close_all_resets_connections(self, db_service):
        """验证 close_all() 关闭所有连接"""
        # 先建立连接
        db_service.get_governance_conn()
        db_service.get_depgraph_conn()
        db_service.get_market_conn()
        assert db_service._governance_conn is not None
        assert db_service._depgraph_conn is not None
        assert db_service._market_conn is not None

        db_service.close_all()
        assert db_service._governance_conn is None
        assert db_service._depgraph_conn is None
        assert db_service._market_conn is None

    def test_reconnect_after_close(self, db_service):
        """验证关闭后可重新连接"""
        db_service.get_market_conn()
        db_service.close_all()
        conn = db_service.get_market_conn()
        assert conn is not None
        result = conn.execute("SELECT 1").fetchone()
        assert result[0] == 1
