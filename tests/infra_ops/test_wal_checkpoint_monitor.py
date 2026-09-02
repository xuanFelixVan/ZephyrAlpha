# [BLUEPRINT] MOD-INF-085 | docs/03_modules/_domain_infrastructure_operations/wal_checkpoint_monitor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-085 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_ops.test_wal_checkpoint_monitor
# [TESTS] src/zephyr/infra_ops/wal_checkpoint_monitor.py
"""MOD-INF-085 单元测试：wal_checkpoint_monitor SQLite WAL 检查点监控器。

蓝图验收（B13-04268/CAND-INFRAOPS-003，A3数据架构）：
wal 大小/checkpoint 耗时/写入速率采集（注入 probe）+ 阈值预警分级 +
PASSIVE/TRUNCATE 自动 checkpoint 策略裁决（执行经注入 runner，未注入
Fail-Closed）+ telemetry 指标回调。probe/runner/telemetry/alert 全注入内
存替身；含 tmp_path 真实 sqlite WAL 模式采集路径验证，不触网。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.infra_ops.wal_checkpoint_monitor",
    reason="wal_checkpoint_monitor not importable",
)

from zephyr.infra_ops.wal_checkpoint_monitor import (  # noqa: E402
    AlertLevel,
    CheckpointMode,
    WalCheckpointMonitor,
    WalMetrics,
    WalMonitorError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_WARN = 1_000
_CRIT = 5_000


def _metrics(wal_bytes: int = 100, checkpoint_ms: float = 1.0, write_rate: float = 10.0) -> WalMetrics:
    return WalMetrics(
        wal_bytes=wal_bytes,
        checkpoint_ms=checkpoint_ms,
        write_rate=write_rate,
        collected_at=_T0,
    )


def _monitor(
    probe=None,
    runner=None,
    telemetry: list | None = None,
    alerts: list | None = None,
) -> WalCheckpointMonitor:
    return WalCheckpointMonitor(
        warn_threshold_bytes=_WARN,
        critical_threshold_bytes=_CRIT,
        metrics_probe=probe if probe is not None else (lambda: _metrics()),
        checkpoint_runner=runner,
        telemetry_sink=(lambda n, v: telemetry.append((n, v))) if telemetry is not None else None,
        alert_sink=(lambda lv, m: alerts.append((lv, m))) if alerts is not None else None,
        clock=lambda: _T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造阈值校验
# ──────────────────────────────────────────────────────────────────────────────


class TestThresholds:
    def test_valid_construction(self) -> None:
        m = _monitor()
        assert m.last_metrics is None

    def test_negative_threshold_raises(self) -> None:
        with pytest.raises(WalMonitorError):
            WalCheckpointMonitor(warn_threshold_bytes=-1, critical_threshold_bytes=_CRIT)

    def test_warn_ge_critical_raises(self) -> None:
        with pytest.raises(WalMonitorError):
            WalCheckpointMonitor(warn_threshold_bytes=_CRIT, critical_threshold_bytes=_CRIT)


# ──────────────────────────────────────────────────────────────────────────────
# 采集
# ──────────────────────────────────────────────────────────────────────────────


class TestCollect:
    def test_collect_ok(self) -> None:
        m = _monitor(probe=lambda: _metrics(wal_bytes=256))
        got = m.collect()
        assert got.wal_bytes == 256
        assert m.last_metrics is got

    def test_probe_missing_fail_closed(self) -> None:
        m = WalCheckpointMonitor(warn_threshold_bytes=_WARN, critical_threshold_bytes=_CRIT, clock=lambda: _T0)
        with pytest.raises(WalMonitorError):
            m.collect()

    def test_probe_wrong_type_raises(self) -> None:
        m = _monitor(probe=lambda: {"wal_bytes": 1})
        with pytest.raises(WalMonitorError):
            m.collect()

    def test_negative_metric_raises(self) -> None:
        m = _monitor(probe=lambda: _metrics(wal_bytes=-1))
        with pytest.raises(WalMonitorError):
            m.collect()

    def test_telemetry_emitted(self) -> None:
        telemetry: list = []
        m = _monitor(probe=lambda: _metrics(wal_bytes=7, checkpoint_ms=2.0, write_rate=3.0), telemetry=telemetry)
        m.collect()
        assert dict(telemetry) == {
            "wal_bytes": 7.0,
            "wal_checkpoint_ms": 2.0,
            "wal_write_rate": 3.0,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 分级与策略裁决
# ──────────────────────────────────────────────────────────────────────────────


class TestAssessDecide:
    def test_assess_boundaries(self) -> None:
        m = _monitor()
        assert m.assess(_metrics(wal_bytes=_WARN - 1)) is AlertLevel.OK
        assert m.assess(_metrics(wal_bytes=_WARN)) is AlertLevel.WARN
        assert m.assess(_metrics(wal_bytes=_CRIT - 1)) is AlertLevel.WARN
        assert m.assess(_metrics(wal_bytes=_CRIT)) is AlertLevel.CRITICAL

    def test_decide_checkpoint(self) -> None:
        m = _monitor()
        assert m.decide_checkpoint(_metrics(wal_bytes=0)) is None
        assert m.decide_checkpoint(_metrics(wal_bytes=_WARN)) is CheckpointMode.PASSIVE
        assert m.decide_checkpoint(_metrics(wal_bytes=_CRIT)) is CheckpointMode.TRUNCATE

    def test_deterministic(self) -> None:
        m = _monitor()
        sample = _metrics(wal_bytes=1234)
        assert m.assess(sample) is m.assess(sample)
        assert m.decide_checkpoint(sample) is m.decide_checkpoint(sample)


# ──────────────────────────────────────────────────────────────────────────────
# 巡检主路（自动 checkpoint）
# ──────────────────────────────────────────────────────────────────────────────


class TestTick:
    def test_ok_no_checkpoint(self) -> None:
        ran: list = []
        m = _monitor(probe=lambda: _metrics(wal_bytes=10), runner=lambda mode: ran.append(mode) or True)
        assert m.tick() is AlertLevel.OK
        assert ran == []

    def test_warn_runs_passive_with_alert(self) -> None:
        ran: list = []
        alerts: list = []
        m = _monitor(
            probe=lambda: _metrics(wal_bytes=_WARN),
            runner=lambda mode: ran.append(mode) or True,
            alerts=alerts,
        )
        assert m.tick() is AlertLevel.WARN
        assert ran == [CheckpointMode.PASSIVE]
        assert len(alerts) == 1 and alerts[0][0] is AlertLevel.WARN

    def test_critical_runs_truncate(self) -> None:
        ran: list = []
        m = _monitor(probe=lambda: _metrics(wal_bytes=_CRIT * 2), runner=lambda mode: ran.append(mode) or True)
        assert m.tick() is AlertLevel.CRITICAL
        assert ran == [CheckpointMode.TRUNCATE]

    def test_runner_missing_fail_closed(self) -> None:
        m = _monitor(probe=lambda: _metrics(wal_bytes=_CRIT))
        with pytest.raises(WalMonitorError):
            m.tick()

    def test_runner_nack_raises(self) -> None:
        m = _monitor(probe=lambda: _metrics(wal_bytes=_WARN), runner=lambda mode: False)
        with pytest.raises(WalMonitorError):
            m.tick()

    def test_runner_exception_raises(self) -> None:
        def _boom(mode: CheckpointMode) -> bool:
            raise RuntimeError("io")

        m = _monitor(probe=lambda: _metrics(wal_bytes=_WARN), runner=_boom)
        with pytest.raises(WalMonitorError):
            m.tick()


# ──────────────────────────────────────────────────────────────────────────────
# 真实 sqlite WAL 模式采集路径（tmp_path，不触网）
# ──────────────────────────────────────────────────────────────────────────────


class TestRealSqliteWal:
    def test_collect_from_real_wal_db(self, tmp_path) -> None:
        db = tmp_path / "m.db"
        conn = sqlite3.connect(str(db))
        try:
            assert conn.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
            conn.execute("CREATE TABLE t (v TEXT)")
            for i in range(200):
                conn.execute("INSERT INTO t VALUES (?)", (f"x{i}" * 64,))
            conn.commit()
            wal_file = tmp_path / "m.db-wal"
            assert wal_file.exists()

            def _probe() -> WalMetrics:
                return WalMetrics(
                    wal_bytes=wal_file.stat().st_size if wal_file.exists() else 0,
                    checkpoint_ms=0.5,
                    write_rate=128.0,
                    collected_at=_T0,
                )

            m = _monitor(probe=_probe, runner=lambda mode: True)
            got = m.collect()
            assert got.wal_bytes > 0
            assert m.assess(got) in (AlertLevel.WARN, AlertLevel.CRITICAL)
            level = m.tick()
            assert level is m.assess(got)  # 确定性：同快照同裁决
        finally:
            conn.close()

    def test_small_wal_ok_level(self, tmp_path) -> None:
        db = tmp_path / "s.db"
        conn = sqlite3.connect(str(db))
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("CREATE TABLE t (v INTEGER)")
            conn.commit()
            wal_file = tmp_path / "s.db-wal"
            size = wal_file.stat().st_size if wal_file.exists() else 0
            m = WalCheckpointMonitor(
                warn_threshold_bytes=10**9,
                critical_threshold_bytes=10**10,
                metrics_probe=lambda: _metrics(wal_bytes=size),
                clock=lambda: _T0,
            )
            assert m.tick() is AlertLevel.OK
        finally:
            conn.close()
