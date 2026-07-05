"""progress_store 单测（MOD-L00-004 阶段2）。

测试内容：
- 建表（task_progress + task_runs）
- 断点续传：get_last_key / save_progress
- 运行记录：start_run / finish_run
- 查询：list_recent_runs / list_failed_tasks / list_tasks_by_source / list_all_tasks
- 线程安全（并发 save_progress 不崩溃）

用 tmp_path fixture 隔离测试库，不污染生产 data/integrator_progress.db。
"""
import datetime
import threading
import pytest

from src.zephyr.data.progress_store import ProgressStore


@pytest.fixture
def store(tmp_path):
    """每个测试用独立临时库。"""
    db = tmp_path / "test_progress.db"
    s = ProgressStore(db)
    yield s
    s.close()


class TestInitDb:
    """建表测试。"""

    def test_tables_created(self, store):
        """task_progress 和 task_runs 表应存在。"""
        cur = store._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [r[0] for r in cur.fetchall()]
        assert "task_progress" in tables
        assert "task_runs" in tables

    def test_wal_mode(self, store):
        """WAL 模式应启用（提升并发读性能）。"""
        cur = store._conn.execute("PRAGMA journal_mode")
        mode = cur.fetchone()[0]
        assert mode == "wal"


class TestSaveAndGetLastKey:
    """断点续传测试。"""

    def test_get_last_key_none_for_new_task(self, store):
        """从未运行过的任务返回 None。"""
        assert store.get_last_key("nonexistent") is None

    def test_save_and_get_last_key(self, store):
        """保存后应能查到 last_key。"""
        assert store.save_progress("kline_daily", "ifind", "2026-07-05", "SUCCESS", 1000)
        assert store.get_last_key("kline_daily") == "2026-07-05"

    def test_save_progress_upsert(self, store):
        """重复保存应 UPDATE 而非 INSERT（UPSERT）。"""
        store.save_progress("kline_daily", "ifind", "2026-07-05", "SUCCESS", 1000)
        store.save_progress("kline_daily", "ifind", "2026-07-06", "SUCCESS", 2000)
        status = store.get_task_status("kline_daily")
        assert status["last_key"] == "2026-07-06"
        assert status["rows_total"] == 2000
        # 应只有 1 行（UPSERT）
        cur = store._conn.execute("SELECT COUNT(*) FROM task_progress WHERE task_id='kline_daily'")
        assert cur.fetchone()[0] == 1

    def test_save_progress_with_error(self, store):
        """失败状态应保存 error_msg。"""
        store.save_progress("margin_trading", "ifind", "2026-07-05", "FAILED", 0, "连接超时")
        status = store.get_task_status("margin_trading")
        assert status["last_status"] == "FAILED"
        assert status["error_msg"] == "连接超时"


class TestRunRecords:
    """运行记录测试。"""

    def test_start_and_finish_run(self, store):
        """start_run 返回 run_id，finish_run 更新状态。"""
        run_id = store.start_run("kline_daily")
        assert run_id is not None
        assert isinstance(run_id, int)

        assert store.finish_run(run_id, "SUCCESS", rows_fetched=500, rows_written=500)
        cur = store._conn.execute("SELECT * FROM task_runs WHERE run_id=?", (run_id,))
        row = dict(cur.fetchone())
        assert row["status"] == "SUCCESS"
        assert row["rows_fetched"] == 500
        assert row["rows_written"] == 500
        assert row["finished_at"] is not None

    def test_start_run_multiple(self, store):
        """同一任务可多次运行（每次新 run_id）。"""
        rid1 = store.start_run("kline_daily")
        rid2 = store.start_run("kline_daily")
        assert rid1 != rid2

    def test_finish_run_nonexistent(self, store):
        """finish_run 不存在的 run_id 应返回 True（UPDATE 0 行不报错）。"""
        assert store.finish_run(99999, "SUCCESS")


class TestQueries:
    """查询测试。"""

    def test_list_recent_runs(self, store):
        """list_recent_runs 按时间倒序。"""
        for i in range(5):
            rid = store.start_run(f"task_{i}")
            store.finish_run(rid, "SUCCESS", rows_fetched=i * 100)
        runs = store.list_recent_runs(limit=3)
        assert len(runs) == 3
        # 最新的在前面
        assert runs[0]["task_id"] == "task_4"

    def test_list_failed_tasks(self, store):
        """list_failed_tasks 只返回 FAILED。"""
        store.save_progress("task_ok", "ifind", "2026-07-05", "SUCCESS", 100)
        store.save_progress("task_fail1", "ifind", "2026-07-05", "FAILED", 0, "超时")
        store.save_progress("task_fail2", "akshare", "2026-07-05", "FAILED", 0, "SSL错误")
        failed = store.list_failed_tasks()
        assert len(failed) == 2
        task_ids = {f["task_id"] for f in failed}
        assert task_ids == {"task_fail1", "task_fail2"}

    def test_list_tasks_by_source(self, store):
        """list_tasks_by_source 按数据源过滤。"""
        store.save_progress("t1", "ifind", "d1", "SUCCESS", 100)
        store.save_progress("t2", "ifind", "d2", "SUCCESS", 200)
        store.save_progress("t3", "akshare", "d3", "SUCCESS", 300)
        ifind_tasks = store.list_tasks_by_source("ifind")
        assert len(ifind_tasks) == 2
        akshare_tasks = store.list_tasks_by_source("akshare")
        assert len(akshare_tasks) == 1

    def test_list_all_tasks(self, store):
        """list_all_tasks 返回全部。"""
        store.save_progress("t1", "ifind", "d1", "SUCCESS", 100)
        store.save_progress("t2", "akshare", "d2", "SUCCESS", 200)
        all_tasks = store.list_all_tasks()
        assert len(all_tasks) == 2


class TestThreadSafety:
    """线程安全测试。"""

    def test_concurrent_save_progress(self, store):
        """多线程并发 save_progress 不崩溃，最终状态一致。"""
        results = []

        def worker(i):
            for j in range(20):
                ok = store.save_progress("shared_task", "ifind", f"2026-07-{j:02d}", "SUCCESS", i * 20 + j)
                results.append(ok)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 全部成功
        assert all(results)
        assert len(results) == 100
        # 最终状态一致（只有 1 行）
        cur = store._conn.execute("SELECT COUNT(*) FROM task_progress WHERE task_id='shared_task'")
        assert cur.fetchone()[0] == 1

    def test_concurrent_start_run(self, store):
        """多线程并发 start_run 各得不同 run_id。"""
        run_ids = []
        lock = threading.Lock()

        def worker():
            rid = store.start_run("concurrent_task")
            with lock:
                run_ids.append(rid)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(run_ids) == 10
        assert len(set(run_ids)) == 10  # 全部唯一
