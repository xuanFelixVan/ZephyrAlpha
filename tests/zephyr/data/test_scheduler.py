"""scheduler 单测（MOD-L00-004 阶段2）。

测试内容：
- IntegratorScheduler 初始化
- subscribe / _emit_event 事件订阅
- _load_config 从 yaml 加载
- _create_provider 创建 Provider
- run_task 执行单个任务（mock provider + ch_writer）
- run_schedule 执行时段任务（mock run_task）
- start/stop 生命周期（mock APScheduler）
- get_status / list_tasks 查询

不依赖真实 APScheduler/Provider/ClickHouse，用 mock 替换。
"""
import datetime
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from src.zephyr.data.scheduler import IntegratorScheduler
from src.zephyr.data.provider_base import FetchPayload, FetchResult, DataSourceBase, DataSourceMeta
from src.zephyr.data.ch_writer import WriteDisposition, WriteOutcome


# ============== 测试用 Mock Provider ==============

class _MockProvider(DataSourceBase):
    """最小可实例化的 DataSourceBase 子类。"""
    source_name = "mock"
    meta = DataSourceMeta(
        name="mock", display_name="Mock", auth_type="anonymous",
        requires_process=False, thread_safety="shared", rate_limit_default=0,
    )

    def connect(self):
        self._connected = True

    def health_check(self):
        return self._connected

    def fetch(self, payload, policy):
        """返回单批数据。"""
        yield FetchResult(
            table=payload.table,
            columns=["code", "date", "close"],
            rows=[("000001", "2026-07-05", 10.5)],
            last_key="2026-07-05",
            elapsed_sec=0.1,
            rows_fetched=1,
        )

    def disconnect(self):
        self._connected = False


@pytest.fixture
def scheduler(tmp_path):
    """用临时配置目录和数据库的 IntegratorScheduler。"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    # 写入最小配置
    (config_dir / "schedule.yaml").write_text(
        'schedules:\n  daily_kline:\n    cron: "30 16 * * 1-5"\n    executor: heavy\n',
        encoding="utf-8",
    )
    (config_dir / "tasks.yaml").write_text(
        'tasks:\n'
        '  - task_id: kline_daily_incremental\n'
        '    table: c1_market.kline_daily\n'
        '    source: mock\n'
        '    schedule: daily_kline\n'
        '    incremental: true\n'
        '    dependencies: []\n'
        '    capability: kline_daily\n'
        '    symbols: null\n',
        encoding="utf-8",
    )
    progress_db = tmp_path / "progress.db"
    jobs_db = "sqlite:///" + str(tmp_path / "jobs.db")
    return IntegratorScheduler(
        config_dir=config_dir,
        progress_db=progress_db,
        jobs_db=jobs_db,
    )


class TestInit:
    """初始化测试。"""

    def test_init(self, scheduler):
        assert scheduler._started is False
        assert scheduler._scheduler is None
        assert scheduler._schedules == {}
        assert scheduler._tasks == []

    def test_event_handlers_initialized(self, scheduler):
        assert "config_changed" in scheduler._event_handlers
        assert "shutdown" in scheduler._event_handlers
        assert "task_completed" in scheduler._event_handlers


class TestEventSubscribe:
    """事件订阅测试。"""

    def test_subscribe(self, scheduler):
        called = []
        scheduler.subscribe("task_completed", lambda **kw: called.append(kw))
        assert len(scheduler._event_handlers["task_completed"]) == 1

    def test_emit_event(self, scheduler):
        called = []
        scheduler.subscribe("task_completed", lambda **kw: called.append(kw))
        scheduler._emit_event("task_completed", task_id="t1", success=True)
        assert len(called) == 1
        assert called[0]["task_id"] == "t1"

    def test_emit_event_handler_exception(self, scheduler):
        """handler 异常不抛出。"""
        def bad_handler(**kw):
            raise RuntimeError("boom")
        scheduler.subscribe("task_completed", bad_handler)
        # 不抛异常
        scheduler._emit_event("task_completed", task_id="t1", success=True)

    def test_emit_unknown_event(self, scheduler):
        """未知事件不抛异常。"""
        scheduler._emit_event("nonexistent")


class TestLoadConfig:
    """_load_config 测试。"""

    def test_load_config(self, scheduler):
        scheduler._load_config()
        assert "daily_kline" in scheduler._schedules
        assert len(scheduler._tasks) == 1
        assert scheduler._tasks[0]["task_id"] == "kline_daily_incremental"

    def test_load_config_missing_files(self, tmp_path):
        """配置文件不存在时不抛异常。"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        sched = IntegratorScheduler(
            config_dir=empty_dir,
            progress_db=tmp_path / "p.db",
            jobs_db="sqlite:///" + str(tmp_path / "j.db"),
        )
        sched._load_config()
        assert sched._schedules == {}
        assert sched._tasks == []


class TestCreateProvider:
    """_create_provider 测试。"""

    def test_unknown_source(self, scheduler):
        """未知数据源返回 None。"""
        assert scheduler._create_provider("nonexistent") is None

    def test_create_ifind(self, scheduler):
        """ifind 源创建 IFindProvider（import 可能失败，用 mock）。"""
        with patch("zephyr.data.implementations.ifind_provider.IFindProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            provider = scheduler._create_provider("ifind")
            assert provider is not None


class TestRunTask:
    """run_task 测试（mock provider + ch_writer）。"""

    def test_run_task_success(self, scheduler):
        """成功执行任务。"""
        scheduler._load_config()
        # mock provider
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler._providers["mock"] = mock_provider
        # 调度器经 BufferedWriter 写入；mock 该层以隔离真实 ClickHouse。
        with patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=True):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is True
        # 进度应记录
        status = scheduler._progress_store.get_task_status("kline_daily_incremental")
        assert status is not None
        assert status["last_status"] == "SUCCESS"
        assert status["last_key"] == "2026-07-05"

    def test_run_task_unknown_task(self, scheduler):
        """未知任务返回 False。"""
        scheduler._load_config()
        ok = scheduler.run_task("nonexistent")
        assert ok is False

    def test_run_task_provider_unavailable(self, scheduler):
        """Provider 不可用返回 False。"""
        scheduler._load_config()
        # 不注册 provider，_get_provider 返回 None
        with patch.object(scheduler, "_get_provider", return_value=None):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False

    def test_run_task_fetch_error(self, scheduler):
        """Provider.fetch 返回 error。"""
        scheduler._load_config()
        mock_provider = MagicMock()
        mock_provider.fetch.return_value = iter([
            FetchResult(table="t", columns=[], rows=[], last_key="", elapsed_sec=0, error="连接超时")
        ])
        scheduler._providers["mock"] = mock_provider
        ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False
        status = scheduler._progress_store.get_task_status("kline_daily_incremental")
        assert status["last_status"] == "FAILED"
        assert "连接超时" in status["error_msg"]

    def test_run_task_ch_write_failure(self, scheduler):
        """CH 写入失败。"""
        scheduler._load_config()
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler._providers["mock"] = mock_provider
        with patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=False):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False
        status = scheduler._progress_store.get_task_status("kline_daily_incremental")
        assert status["last_status"] == "FAILED"

    def test_run_task_local_durable_is_deferred(self, scheduler):
        """本地落盘成功不得被误报为 CH 成功或数据丢失失败。"""
        scheduler._load_config()
        provider = _MockProvider()
        provider.connect()
        scheduler._providers["mock"] = provider
        outcome = WriteOutcome(WriteDisposition.LOCAL_DURABLE, "local_fallback")
        with patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=False), \
             patch.object(IntegratorScheduler.__module__ and __import__("src.zephyr.data.scheduler", fromlist=["BufferedWriter"]).BufferedWriter, "last_outcome", new_callable=PropertyMock, return_value=outcome):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is True
        assert scheduler._progress_store.get_task_status("kline_daily_incremental")["last_status"] == "DEFERRED_PERSISTENCE"

    def test_run_task_provider_exception(self, scheduler):
        """Provider.fetch 抛异常。"""
        scheduler._load_config()
        mock_provider = MagicMock()
        mock_provider.fetch.side_effect = RuntimeError("SDK崩溃")
        scheduler._providers["mock"] = mock_provider
        ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False
        status = scheduler._progress_store.get_task_status("kline_daily_incremental")
        assert status["last_status"] == "FAILED"
        assert "SDK崩溃" in status["error_msg"]

    def test_run_task_event_emitted(self, scheduler):
        """任务完成时触发 task_completed 事件。"""
        scheduler._load_config()
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler._providers["mock"] = mock_provider
        events = []
        scheduler.subscribe("task_completed", lambda **kw: events.append(kw))
        with patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=True):
            scheduler.run_task("kline_daily_incremental")
        assert len(events) == 1
        assert events[0]["success"] is True

    def test_run_task_paused_source(self, scheduler):
        """数据源已熔断（policy.enabled=False）时跳过任务返回 False。"""
        scheduler._load_config()
        # mock provider（可用）
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler._providers["mock"] = mock_provider
        # mock policy.enabled=False（CLI pause 生效点）
        from zephyr.data.policy_registry import SourcePolicy
        with patch.object(scheduler._policy_registry, "get_policy", return_value=SourcePolicy(enabled=False)):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False


class TestRunSchedule:
    """run_schedule 测试。"""

    def test_run_schedule_success(self, scheduler):
        """成功执行时段所有任务。"""
        scheduler._load_config()
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler._providers["mock"] = mock_provider
        with patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=True):
            results = scheduler.run_schedule("daily_kline")
        assert len(results) == 1
        assert results["kline_daily_incremental"] is True

    def test_run_schedule_empty(self, scheduler):
        """无任务的时段返回空字典。"""
        scheduler._load_config()
        results = scheduler.run_schedule("nonexistent")
        assert results == {}

    def test_run_schedule_with_dag(self, scheduler, tmp_path):
        """DAG 依赖：前置完成才执行后续。"""
        # 追加一个依赖任务
        scheduler._load_config()
        scheduler._tasks.append({
            "task_id": "daily_valuation_incremental",
            "table": "c1_market.daily_valuation",
            "source": "mock",
            "schedule": "daily_kline",
            "incremental": True,
            "dependencies": ["kline_daily_incremental"],
            "capability": "daily_valuation",
            "symbols": None,
            "extra": {},
        })
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler._providers["mock"] = mock_provider
        with patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=True):
            results = scheduler.run_schedule("daily_kline")
        assert len(results) == 2
        assert all(results.values())


class TestStartStop:
    """start/stop 生命周期测试（mock APScheduler）。"""

    def test_start(self, scheduler):
        """start 成功启动。"""
        with patch("src.zephyr.data.scheduler.IntegratorScheduler._init_scheduler") as mock_init:
            scheduler._scheduler = MagicMock()
            scheduler.start()
        assert scheduler._started is True
        scheduler._scheduler.start.assert_called_once()

    def test_start_already_started(self, scheduler):
        """已启动再 start 返回 True。"""
        scheduler._started = True
        assert scheduler.start() is True

    def test_stop(self, scheduler):
        """stop 优雅关闭。"""
        scheduler._started = True
        scheduler._scheduler = MagicMock()
        mock_provider = MagicMock()
        scheduler._providers["mock"] = mock_provider
        scheduler.stop()
        assert scheduler._started is False
        scheduler._scheduler.shutdown.assert_called_once()
        mock_provider.disconnect.assert_called_once()

    def test_stop_emits_shutdown_event(self, scheduler):
        """stop 触发 shutdown 事件。"""
        called = []
        scheduler.subscribe("shutdown", lambda: called.append(True))
        scheduler._started = True
        scheduler._scheduler = MagicMock()
        scheduler.stop()
        assert len(called) == 1


class TestQueries:
    """查询测试。"""

    def test_get_status(self, scheduler):
        scheduler._load_config()
        status = scheduler.get_status()
        assert status["started"] is False
        assert "daily_kline" in status["schedules"]
        assert status["task_count"] == 1

    def test_list_tasks(self, scheduler):
        scheduler._load_config()
        tasks = scheduler.list_tasks()
        assert len(tasks) == 1
        assert tasks[0]["task_id"] == "kline_daily_incremental"
