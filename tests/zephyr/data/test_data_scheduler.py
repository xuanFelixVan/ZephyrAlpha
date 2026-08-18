# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
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
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from src.zephyr.data.ch_writer import WriteDisposition, WriteOutcome
from src.zephyr.data.provider_base import FetchPayload, FetchResult, IngestProviderBase, IngestProviderMeta
from src.zephyr.data.scheduler import IntegratorScheduler

# ============== 测试用 Mock Provider ==============

class _MockProvider(IngestProviderBase):
    """最小可实例化的 IngestProviderBase 子类。"""
    source_name = "mock"
    meta = IngestProviderMeta(
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
        # #ARCH-DATA-015：隔离 live 网络探针（数据源健康检查/CH 探活/破损 part 检测），
        # 防止环境噪声（如 baostock IP 黑名单泄漏 socket）经 filterwarnings=error 放大为测试失败
        startup_probes=False,
    )


class TestInit:
    """初始化测试。"""

    def test_init(self, scheduler):
        assert scheduler.started is False
        assert scheduler.scheduler is None
        assert scheduler.schedules == {}
        assert scheduler.tasks == []

    def test_event_handlers_initialized(self, scheduler):
        assert "config_changed" in scheduler.event_handlers
        assert "shutdown" in scheduler.event_handlers
        assert "task_completed" in scheduler.event_handlers


class TestEventSubscribe:
    """事件订阅测试。"""

    def test_subscribe(self, scheduler):
        called = []
        scheduler.subscribe("task_completed", lambda **kw: called.append(kw))
        assert len(scheduler.event_handlers["task_completed"]) == 1

    def test_emit_event(self, scheduler):
        called = []
        scheduler.subscribe("task_completed", lambda **kw: called.append(kw))
        scheduler.emit_event("task_completed", task_id="t1", success=True)
        assert len(called) == 1
        assert called[0]["task_id"] == "t1"

    def test_emit_event_handler_exception(self, scheduler):
        """handler 异常不抛出。"""
        def bad_handler(**kw):
            raise RuntimeError("boom")
        scheduler.subscribe("task_completed", bad_handler)
        # 不抛异常
        scheduler.emit_event("task_completed", task_id="t1", success=True)

    def test_emit_unknown_event(self, scheduler):
        """未知事件不抛异常。"""
        scheduler.emit_event("nonexistent")


class TestLoadConfig:
    """_load_config 测试。"""

    def test_load_config(self, scheduler):
        scheduler.load_config()
        assert "daily_kline" in scheduler.schedules
        assert len(scheduler.tasks) == 1
        assert scheduler.tasks[0]["task_id"] == "kline_daily_incremental"

    def test_load_config_missing_files(self, tmp_path):
        """配置文件不存在时不抛异常。"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        sched = IntegratorScheduler(
            config_dir=empty_dir,
            progress_db=tmp_path / "p.db",
            jobs_db="sqlite:///" + str(tmp_path / "j.db"),
        )
        sched.load_config()
        assert sched.schedules == {}
        assert sched.tasks == []


class TestCreateProvider:
    """_create_provider 测试。"""

    def test_unknown_source(self, scheduler):
        """未知数据源返回 None。"""
        assert scheduler.create_provider("nonexistent") is None


class TestRunTask:
    """run_task 测试（mock provider + ch_writer）。"""

    def test_run_task_success(self, scheduler):
        """成功执行任务。"""
        scheduler.load_config()
        # mock provider
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler.providers["mock"] = mock_provider
        # 调度器经 BufferedWriter 写入；mock 该层以隔离真实 ClickHouse。
        with patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=True):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is True
        # 进度应记录
        status = scheduler.progress_store.get_task_status("kline_daily_incremental")
        assert status is not None
        assert status["last_status"] == "SUCCESS"
        assert status["last_key"] == "2026-07-05"

    def test_run_task_unknown_task(self, scheduler):
        """未知任务返回 False。"""
        scheduler.load_config()
        ok = scheduler.run_task("nonexistent")
        assert ok is False

    def test_run_task_provider_unavailable(self, scheduler):
        """Provider 不可用返回 False。"""
        scheduler.load_config()
        # 不注册 provider，_get_provider 返回 None
        with patch.object(scheduler, "_get_provider", return_value=None):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False

    def test_run_task_fetch_error(self, scheduler):
        """Provider.fetch 返回 error。"""
        scheduler.load_config()
        mock_provider = MagicMock()
        mock_provider.fetch.return_value = iter([
            FetchResult(table="t", columns=[], rows=[], last_key="", elapsed_sec=0, error="连接超时")
        ])
        scheduler.providers["mock"] = mock_provider
        ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False
        status = scheduler.progress_store.get_task_status("kline_daily_incremental")
        assert status["last_status"] == "FAILED"
        assert "连接超时" in status["error_msg"]

    def test_run_task_ch_write_failure(self, scheduler):
        """CH 写入失败。"""
        scheduler.load_config()
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler.providers["mock"] = mock_provider
        with patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=False):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False
        status = scheduler.progress_store.get_task_status("kline_daily_incremental")
        assert status["last_status"] == "FAILED"

    def test_run_task_local_durable_is_deferred(self, scheduler):
        """本地落盘成功不得被误报为 CH 成功或数据丢失失败。"""
        scheduler.load_config()
        provider = _MockProvider()
        provider.connect()
        scheduler.providers["mock"] = provider
        outcome = WriteOutcome(WriteDisposition.LOCAL_DURABLE, "local_fallback")
        with patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=False), \
             patch.object(IntegratorScheduler.__module__ and __import__("src.zephyr.data.scheduler", fromlist=["BufferedWriter"]).BufferedWriter, "last_outcome", new_callable=PropertyMock, return_value=outcome):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is True
        assert scheduler.progress_store.get_task_status("kline_daily_incremental")["last_status"] == "DEFERRED_PERSISTENCE"

    def test_run_task_provider_exception(self, scheduler):
        """Provider.fetch 抛异常。"""
        scheduler.load_config()
        mock_provider = MagicMock()
        mock_provider.fetch.side_effect = RuntimeError("SDK崩溃")
        scheduler.providers["mock"] = mock_provider
        ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False
        status = scheduler.progress_store.get_task_status("kline_daily_incremental")
        assert status["last_status"] == "FAILED"
        assert "SDK崩溃" in status["error_msg"]

    def test_run_task_event_emitted(self, scheduler):
        """任务完成时触发 task_completed 事件。"""
        scheduler.load_config()
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler.providers["mock"] = mock_provider
        events = []
        scheduler.subscribe("task_completed", lambda **kw: events.append(kw))
        with patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=True):
            scheduler.run_task("kline_daily_incremental")
        assert len(events) == 1
        assert events[0]["success"] is True

    def test_run_task_paused_source(self, scheduler):
        """数据源已熔断（policy.enabled=False）时跳过任务返回 False。"""
        scheduler.load_config()
        # mock provider（可用）
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler.providers["mock"] = mock_provider
        # mock policy.enabled=False（CLI pause 生效点）
        from zephyr.data.policy_registry import SourcePolicy
        with patch.object(scheduler.policy_registry, "get_policy", return_value=SourcePolicy(enabled=False)):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False


class TestRunSchedule:
    """run_schedule 测试。"""

    def test_run_schedule_success(self, scheduler):
        """成功执行时段所有任务。"""
        scheduler.load_config()
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler.providers["mock"] = mock_provider
        # 时间解耦：daily_kline 属交易日历守卫时段（_schedule_should_skip），
        # 非交易日跑测试会 return {}——patch is_trading_day 固定为交易日
        with patch("src.zephyr.data.scheduler.is_trading_day", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=True):
            results = scheduler.run_schedule("daily_kline")
        assert len(results) == 1
        assert results["kline_daily_incremental"] is True

    def test_run_schedule_empty(self, scheduler):
        """无任务的时段返回空字典。"""
        scheduler.load_config()
        results = scheduler.run_schedule("nonexistent")
        assert results == {}

    def test_run_schedule_with_dag(self, scheduler, tmp_path):
        """DAG 依赖：前置完成才执行后续。"""
        # 追加一个依赖任务
        scheduler.load_config()
        scheduler.tasks.append({
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
        scheduler.providers["mock"] = mock_provider
        # 时间解耦：同上（交易日历守卫时段在非交易日 return {}）
        with patch("src.zephyr.data.scheduler.is_trading_day", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True), \
             patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=True):
            results = scheduler.run_schedule("daily_kline")
        assert len(results) == 2
        assert all(results.values())


class TestStartStop:
    """start/stop 生命周期测试（mock APScheduler）。"""

    def test_start(self, scheduler):
        """start 成功启动。"""
        with patch("src.zephyr.data.scheduler.IntegratorScheduler.init_scheduler") as mock_init:
            scheduler.scheduler = MagicMock()
            scheduler.start()
        assert scheduler.started is True
        scheduler.scheduler.start.assert_called_once()

    def test_start_skips_live_probes(self, scheduler):
        """startup_probes=False 时跳过 live 健康检查/CH 探活/破损 part 检测（#ARCH-DATA-015）。"""
        with patch("src.zephyr.data.scheduler.IntegratorScheduler.init_scheduler"), \
             patch("src.zephyr.data.scheduler.IntegratorScheduler._start_ch_health_probe") as mock_ch, \
             patch("src.zephyr.data.scheduler.IntegratorScheduler._start_corrupted_part_detector") as mock_cp, \
             patch("zephyr.data.source_health_check.run_source_health_check") as mock_hc:
            scheduler.scheduler = MagicMock()
            scheduler.start()
        assert scheduler.started is True
        mock_hc.assert_not_called()
        mock_ch.assert_not_called()
        mock_cp.assert_not_called()

    def test_start_already_started(self, scheduler):
        """已启动再 start 返回 True。"""
        scheduler.started = True
        assert scheduler.start() is True

    def test_stop(self, scheduler):
        """stop 优雅关闭。"""
        scheduler.started = True
        scheduler.scheduler = MagicMock()
        mock_provider = MagicMock()
        scheduler.providers["mock"] = mock_provider
        scheduler.stop()
        assert scheduler.started is False
        scheduler.scheduler.shutdown.assert_called_once()
        mock_provider.disconnect.assert_called_once()

    def test_stop_emits_shutdown_event(self, scheduler):
        """stop 触发 shutdown 事件。"""
        called = []
        scheduler.subscribe("shutdown", lambda: called.append(True))
        scheduler.started = True
        scheduler.scheduler = MagicMock()
        scheduler.stop()
        assert len(called) == 1


class TestQueries:
    """查询测试。"""

    def test_get_status(self, scheduler):
        scheduler.load_config()
        status = scheduler.get_status()
        assert status["started"] is False
        assert "daily_kline" in status["schedules"]
        assert status["task_count"] == 1

    def test_list_tasks(self, scheduler):
        scheduler.load_config()
        tasks = scheduler.list_tasks()
        assert len(tasks) == 1
        assert tasks[0]["task_id"] == "kline_daily_incremental"
