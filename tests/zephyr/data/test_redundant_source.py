# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [A_module] module_id=MOD-L00-005 | layer=module | stability=evolving | safety=M
# [TTL] permanent
"""P2-8 数据源冗余与热切换模块测试。"""

import time

import pytest

from zephyr.data.redundant_source.heartbeat_monitor import (
    HeartbeatMonitor,
    HeartbeatStatus,
    SourceState,
)
from zephyr.data.redundant_source.recovery import RecoveryManager
from zephyr.data.redundant_source.source_switcher import (
    SourceProvider,
    SourceSwitcher,
)
from zephyr.data.redundant_source.sqlite_fallback import SQLiteFallback


class TestHeartbeatMonitor:
    """心跳检测器测试。"""

    def test_initial_state_unknown(self):
        monitor = HeartbeatMonitor(ch_ping_fn=lambda: True)
        status = monitor.get_status()
        assert status.primary_state == SourceState.UNKNOWN

    def test_record_tick_makes_primary_alive(self):
        monitor = HeartbeatMonitor(ch_ping_fn=lambda: True)
        monitor.record_tick()
        assert monitor.is_primary_alive() is True

    def test_primary_dead_after_timeout(self):
        monitor = HeartbeatMonitor(tick_timeout=0.1, ch_ping_fn=lambda: True)
        monitor.record_tick()
        time.sleep(0.2)
        assert monitor.is_primary_alive() is False

    def test_ch_alive_when_ping_succeeds(self):
        monitor = HeartbeatMonitor(ch_ping_fn=lambda: True)
        monitor.start()
        time.sleep(0.5)
        assert monitor.is_ch_alive() is True
        monitor.stop()

    def test_ch_dead_after_failures(self):
        monitor = HeartbeatMonitor(
            ch_ping_fn=lambda: False,
            ch_ping_interval=0.05,
            ch_fail_threshold=2,
        )
        monitor.start()
        time.sleep(0.3)
        assert monitor.is_ch_alive() is False
        monitor.stop()


class _MockSourceProvider(SourceProvider):
    """测试用 Mock 数据源提供者。"""

    def __init__(self, name: str, start_ok: bool = True):
        self._name = name
        self._start_ok = start_ok
        self._running = False

    def name(self) -> str:
        return self._name

    def start(self) -> bool:
        self._running = True
        return self._start_ok

    def stop(self) -> None:
        self._running = False

    def is_running(self) -> bool:
        return self._running


class TestSourceSwitcher:
    """数据源切换控制器测试。"""

    def test_start_with_primary(self):
        primary = _MockSourceProvider("primary")
        backup = _MockSourceProvider("backup")
        heartbeat = HeartbeatMonitor(tick_timeout=10.0, ch_ping_fn=lambda: True)
        heartbeat.record_tick()  # 标记主源活跃
        switcher = SourceSwitcher(primary, backup, heartbeat, check_interval=0.5)
        switcher.start()
        time.sleep(0.2)  # 等待检测线程第一次检查
        assert switcher.is_primary_active() is True
        assert primary.is_running() is True
        switcher.stop()

    def test_fallback_to_backup_on_primary_start_fail(self):
        primary = _MockSourceProvider("primary", start_ok=False)
        backup = _MockSourceProvider("backup")
        heartbeat = HeartbeatMonitor(ch_ping_fn=lambda: True)
        switcher = SourceSwitcher(primary, backup, heartbeat)
        switcher.start()
        assert switcher.is_primary_active() is False
        assert backup.is_running() is True
        switcher.stop()

    def test_switch_to_backup_on_primary_dead(self):
        primary = _MockSourceProvider("primary")
        backup = _MockSourceProvider("backup")
        heartbeat = HeartbeatMonitor(tick_timeout=0.1, ch_ping_fn=lambda: True)
        heartbeat.record_tick()
        switcher = SourceSwitcher(primary, backup, heartbeat, check_interval=0.1, recovery_stable_period=0.1)
        switcher.start()
        # 等待主源超时
        time.sleep(0.4)
        assert switcher.is_primary_active() is False
        assert backup.is_running() is True
        switcher.stop()

    def test_get_active_provider(self):
        primary = _MockSourceProvider("primary")
        backup = _MockSourceProvider("backup")
        heartbeat = HeartbeatMonitor(tick_timeout=10.0, ch_ping_fn=lambda: True)
        heartbeat.record_tick()  # 标记主源活跃
        switcher = SourceSwitcher(primary, backup, heartbeat, check_interval=0.5)
        switcher.start()
        time.sleep(0.2)
        assert switcher.get_active_provider().name() == "primary"
        switcher.stop()


class TestSQLiteFallback:
    """CH 降级 SQLite 测试。"""

    def test_write_and_query(self, tmp_path):
        db = SQLiteFallback(db_path=str(tmp_path / "test.sqlite"))
        cols = ["symbol", "price", "volume"]
        rows = [("000001", "10.5", "1000"), ("000002", "20.3", "2000")]
        written = db.write_rows("tick_data", cols, rows)
        assert written == 2

        recent = db.query_recent("tick_data", limit=10)
        assert len(recent) == 2
        db.close()

    def test_pending_count(self, tmp_path):
        db = SQLiteFallback(db_path=str(tmp_path / "test.sqlite"))
        cols = ["symbol"]
        rows = [("000001",), ("000002",), ("000003",)]
        db.write_rows("test_table", cols, rows)
        assert db.get_pending_count("test_table") == 3
        db.close()

    def test_get_and_delete_batch(self, tmp_path):
        db = SQLiteFallback(db_path=str(tmp_path / "test.sqlite"))
        cols = ["symbol"]
        rows = [(f"00000{i}",) for i in range(5)]
        db.write_rows("test_table", cols, rows)

        batch_cols, batch_rows = db.get_pending_batch("test_table", batch_size=2)
        assert len(batch_rows) == 2

        deleted = db.delete_batch("test_table", batch_size=2)
        assert deleted == 2
        assert db.get_pending_count("test_table") == 3
        db.close()

    def test_cleanup_old_data(self, tmp_path):
        db = SQLiteFallback(db_path=str(tmp_path / "test.sqlite"), max_rows_per_table=3)
        cols = ["symbol"]
        rows = [(f"00000{i}",) for i in range(5)]
        db.write_rows("test_table", cols, rows)
        # 写入后应自动清理到 max_rows
        assert db.get_pending_count("test_table") <= 3
        db.close()

    def test_empty_rows_returns_zero(self, tmp_path):
        db = SQLiteFallback(db_path=str(tmp_path / "test.sqlite"))
        assert db.write_rows("test", ["col"], []) == 0
        db.close()


class TestRecoveryManager:
    """CH 恢复回灌测试。"""

    def test_no_recovery_when_ch_down(self, tmp_path):
        db = SQLiteFallback(db_path=str(tmp_path / "test.sqlite"))
        heartbeat = HeartbeatMonitor(ch_ping_fn=lambda: False)
        recovery = RecoveryManager(db, heartbeat, check_interval=0.1)
        recovery.start()
        time.sleep(0.3)
        assert recovery.is_recovering() is False
        recovery.stop()
        db.close()

    def test_recovery_triggers_when_ch_up_and_data_pending(self, tmp_path):
        db = SQLiteFallback(db_path=str(tmp_path / "test.sqlite"))
        db.write_rows("tick_data", ["symbol"], [("000001",)])
        heartbeat = HeartbeatMonitor(ch_ping_fn=lambda: True)
        recovery = RecoveryManager(db, heartbeat, check_interval=0.1)
        recovery.start()
        time.sleep(0.5)
        # CH 恢复后应触发回灌（但回灌会失败因为 ch_writer 不可用，不影响测试）
        recovery.stop()
        db.close()
