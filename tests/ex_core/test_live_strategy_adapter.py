# [A_test] module_id: MOD-EXE-live_strategy_adapter_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.ex_core.test_live_strategy_adapter
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""LiveStrategyAdapter — 模拟盘策略常驻服务适配器单元测试（57 号文 GAP-2）。

覆盖：
  - 配置校验：空 slots / 重复 slot_id / 未 start 直接 run → LiveStrategyAdapterError(details)
  - 启动/停止：start 逐 slot 启动+心跳落盘 / start 幂等 / stop 优雅停止+最终心跳 / stop 幂等
  - 心跳：JSON 载荷字段 / tmp→os.replace 原子写（无 .tmp 残留）/ 写出失败不阻断服务
  - 异常隔离：装配失败 / start 失败 / stop 失败不扩散 / 盘中意外停止检测
  - 退避重启：FAILED→重启成功 / 重启上限熔断 EXHAUSTED
  - run() 有界循环：close_at 到点优雅收场 / stop_event 截止 / 每轮心跳+监督
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta
from datetime import time as dtime
from typing import Any
from zoneinfo import ZoneInfo

import pytest

import zephyr.ex_core.live_strategy_adapter as lsa_module
from zephyr.ex_core.live_strategy_adapter import (
    LiveStrategyAdapter,
    LiveStrategyAdapterError,
    SlotState,
    StrategySlot,
)

_SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")


# ---------------------------------------------------------------------
# 测试辅助
# ---------------------------------------------------------------------


class _FakeSession:
    """TradingSession 最小替身（adapter 只消费 start/stop/get_session_report 三方法）。"""

    def __init__(self, *, fail_on_start: bool = False, fail_on_stop: bool = False) -> None:
        self._fail_on_start = fail_on_start
        self._fail_on_stop = fail_on_stop
        self._running = False
        self.start_calls = 0
        self.stop_calls = 0

    def start(self) -> None:
        self.start_calls += 1
        if self._fail_on_start:
            raise ConnectionError("broker unreachable")
        self._running = True

    def stop(self) -> None:
        self.stop_calls += 1
        if self._fail_on_stop:
            raise RuntimeError("stop blew up")
        self._running = False

    def get_session_report(self) -> dict[str, Any]:
        return {"running": self._running, "submitted_count": 0, "blocked_count": 0, "fill_count": 0}


class _FakeClock:
    """假钟：now_fn/sleeper 联动（sleeper 调用推进 now）。"""

    def __init__(self, start: datetime) -> None:
        self.now = start
        self.slept: list[float] = []

    def now_fn(self) -> datetime:
        return self.now

    def sleeper(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += timedelta(seconds=seconds)


def _make_adapter(
    tmp_path,
    slots: list[StrategySlot],
    *,
    clock: _FakeClock | None = None,
    **overrides: Any,
) -> LiveStrategyAdapter:
    clock = clock or _FakeClock(datetime(2026, 8, 28, 9, 30, tzinfo=_SHANGHAI_TZ))
    kwargs: dict[str, Any] = {
        "heartbeat_path": tmp_path / "live_strategy_biz.heartbeat",
        "now_fn": clock.now_fn,
        "sleeper": clock.sleeper,
    }
    kwargs.update(overrides)
    return LiveStrategyAdapter(slots, **kwargs)


def _read_heartbeat(tmp_path) -> dict[str, Any]:
    return json.loads((tmp_path / "live_strategy_biz.heartbeat").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------
# 配置校验
# ---------------------------------------------------------------------


class TestConfigValidation:
    def test_empty_slots_raises(self, tmp_path):
        """空 slots → LiveStrategyAdapterError(details 承载 reason)。"""
        with pytest.raises(LiveStrategyAdapterError) as exc_info:
            _make_adapter(tmp_path, [])
        assert exc_info.value.details == {"reason": "empty_slots"}

    def test_duplicate_slot_id_raises(self, tmp_path):
        """重复 slot_id → LiveStrategyAdapterError(details 承载 slot_ids)。"""
        slots = [StrategySlot("dup", _FakeSession), StrategySlot("dup", _FakeSession)]
        with pytest.raises(LiveStrategyAdapterError) as exc_info:
            _make_adapter(tmp_path, slots)
        assert exc_info.value.details["slot_ids"] == ["dup", "dup"]

    def test_run_before_start_raises(self, tmp_path):
        """未 start 直接 run → LiveStrategyAdapterError（生命周期顺序错误）。"""
        adapter = _make_adapter(tmp_path, [StrategySlot("s1", _FakeSession)])
        with pytest.raises(LiveStrategyAdapterError) as exc_info:
            adapter.run()
        assert exc_info.value.details == {"state": "not_started"}


# ---------------------------------------------------------------------
# 启动 / 停止
# ---------------------------------------------------------------------


class TestLifecycle:
    def test_start_launches_all_slots_and_writes_heartbeat(self, tmp_path):
        """start() → 全部 slot RUNNING + session.start 各调一次 + 心跳落盘。"""
        s1, s2 = _FakeSession(), _FakeSession()
        adapter = _make_adapter(
            tmp_path,
            [StrategySlot("s1", lambda: s1), StrategySlot("s2", lambda: s2)],
        )
        adapter.start()
        assert adapter.is_running
        assert s1.start_calls == 1 and s2.start_calls == 1
        report = adapter.status_report()
        assert report["slots_running"] == 2 and report["slots_total"] == 2
        hb = _read_heartbeat(tmp_path)
        assert hb["service"] == "live_strategy_adapter"
        assert hb["running"] is True
        assert hb["slots_running"] == 2
        assert {s["slot_id"] for s in hb["slots"]} == {"s1", "s2"}
        assert all(s["state"] == "RUNNING" for s in hb["slots"])
        adapter.stop()

    def test_start_idempotent(self, tmp_path):
        """重复 start() → 告警跳过不重复拉起（session.start 仍只调一次）。"""
        session = _FakeSession()
        adapter = _make_adapter(tmp_path, [StrategySlot("s1", lambda: session)])
        adapter.start()
        adapter.start()
        assert session.start_calls == 1
        adapter.stop()

    def test_stop_graceful_and_writes_final_heartbeat(self, tmp_path):
        """stop() → 全部 slot session.stop + 状态 STOPPED + 最终心跳 running=False。"""
        s1, s2 = _FakeSession(), _FakeSession()
        adapter = _make_adapter(
            tmp_path,
            [StrategySlot("s1", lambda: s1), StrategySlot("s2", lambda: s2)],
        )
        adapter.start()
        adapter.stop()
        assert not adapter.is_running
        assert s1.stop_calls == 1 and s2.stop_calls == 1
        report = adapter.status_report()
        assert report["slots_stopped"] == 2
        hb = _read_heartbeat(tmp_path)
        assert hb["running"] is False
        assert all(s["state"] == "STOPPED" for s in hb["slots"])

    def test_stop_idempotent(self, tmp_path):
        """未 start 直接 stop / 重复 stop → 幂等无动作。"""
        session = _FakeSession()
        adapter = _make_adapter(tmp_path, [StrategySlot("s1", lambda: session)])
        adapter.stop()  # 未 start：幂等返回
        adapter.start()
        adapter.stop()
        adapter.stop()
        assert session.stop_calls == 1


# ---------------------------------------------------------------------
# 心跳
# ---------------------------------------------------------------------


class TestHeartbeat:
    def test_atomic_write_leaves_no_tmp_residue(self, tmp_path):
        """tmp→os.replace 原子写：心跳文件存在且无 .tmp 残留。"""
        adapter = _make_adapter(tmp_path, [StrategySlot("s1", _FakeSession)])
        adapter.start()
        assert (tmp_path / "live_strategy_biz.heartbeat").is_file()
        assert not (tmp_path / "live_strategy_biz.tmp").exists()
        adapter.stop()

    def test_heartbeat_payload_carries_slot_error(self, tmp_path):
        """FAILED slot 的 last_error 入心跳可见（崩溃隔离可观测）。"""
        adapter = _make_adapter(
            tmp_path,
            [StrategySlot("bad", lambda: _FakeSession(fail_on_start=True))],
        )
        adapter.start()
        hb = _read_heartbeat(tmp_path)
        slot = hb["slots"][0]
        assert slot["state"] == "FAILED"
        assert "ConnectionError" in slot["last_error"]
        assert hb["slots_failed"] == 1
        adapter.stop()

    def test_heartbeat_write_failure_does_not_break_service(self, tmp_path, monkeypatch):
        """心跳写出失败（os.replace 抛错）→ log 吞没，服务照常启动/停止。"""
        monkeypatch.setattr(lsa_module.os, "replace", lambda *_a: (_ for _ in ()).throw(OSError("disk full")))
        session = _FakeSession()
        adapter = _make_adapter(tmp_path, [StrategySlot("s1", lambda: session)])
        adapter.start()  # 不抛异常即通过
        assert adapter.is_running and session.start_calls == 1
        adapter.stop()
        assert session.stop_calls == 1


# ---------------------------------------------------------------------
# 异常隔离
# ---------------------------------------------------------------------


class TestExceptionIsolation:
    def test_factory_crash_isolated(self, tmp_path):
        """slot 装配（factory）崩溃 → 该 slot FAILED，其余 RUNNING，服务继续。"""
        good = _FakeSession()

        def _bad_factory():
            raise ValueError("assemble failed")

        adapter = _make_adapter(
            tmp_path,
            [StrategySlot("bad", _bad_factory), StrategySlot("good", lambda: good)],
        )
        adapter.start()
        assert adapter.is_running
        assert good.get_session_report()["running"] is True
        states = {s["slot_id"]: s["state"] for s in adapter.status_report()["slots"]}
        assert states == {"bad": "FAILED", "good": "RUNNING"}
        adapter.stop()

    def test_session_start_crash_isolated(self, tmp_path):
        """slot session.start 崩溃（如 broker 掉线）→ FAILED 隔离，其余照常。"""
        good = _FakeSession()
        adapter = _make_adapter(
            tmp_path,
            [
                StrategySlot("bad", lambda: _FakeSession(fail_on_start=True)),
                StrategySlot("good", lambda: good),
            ],
        )
        adapter.start()
        assert good.get_session_report()["running"] is True
        assert adapter.status_report()["slots_failed"] == 1
        adapter.stop()
        assert good.stop_calls == 1

    def test_stop_crash_does_not_block_other_slots(self, tmp_path):
        """单 slot stop 异常 → 已隔离记录，其余 slot 照常停止。"""
        bad, good = _FakeSession(fail_on_stop=True), _FakeSession()
        adapter = _make_adapter(
            tmp_path,
            [StrategySlot("bad", lambda: bad), StrategySlot("good", lambda: good)],
        )
        adapter.start()
        adapter.stop()  # 不抛异常即通过
        assert bad.stop_calls == 1 and good.stop_calls == 1
        assert good.get_session_report()["running"] is False

    def test_unexpected_session_stop_detected_by_supervise(self, tmp_path):
        """RUNNING slot 盘中意外停止（session report running=False）→ 监督标 FAILED。"""
        session = _FakeSession()
        adapter = _make_adapter(tmp_path, [StrategySlot("s1", lambda: session)])
        adapter.start()
        session._running = False  # 模拟盘中崩溃（timer 线程死亡等）
        adapter._supervise_once()
        slot = adapter.status_report()["slots"][0]
        assert slot["state"] == "FAILED"
        assert "session stopped unexpectedly" in slot["last_error"]
        adapter.stop()


# ---------------------------------------------------------------------
# 退避重启
# ---------------------------------------------------------------------


class TestRestart:
    def test_failed_slot_restarted_after_backoff(self, tmp_path, monkeypatch):
        """FAILED slot 退避到期 → 工厂重造新实例重启 RUNNING，restart_count=1。"""
        sessions = [_FakeSession(fail_on_start=True), _FakeSession()]
        factory_calls: list[int] = []

        def _factory():
            factory_calls.append(1)
            return sessions[min(len(factory_calls) - 1, 1)]

        monotonic_holder = {"t": 1000.0}
        monkeypatch.setattr(lsa_module.time, "monotonic", lambda: monotonic_holder["t"])
        adapter = _make_adapter(
            tmp_path,
            [StrategySlot("s1", _factory)],
            restart_backoff_seconds=30.0,
        )
        adapter.start()
        assert adapter.status_report()["slots_failed"] == 1
        # 退避未到期：不重启
        monotonic_holder["t"] += 10.0
        adapter._supervise_once()
        assert adapter.status_report()["slots_failed"] == 1
        # 退避到期：重启成功
        monotonic_holder["t"] += 25.0
        adapter._supervise_once()
        slot = adapter.status_report()["slots"][0]
        assert slot["state"] == "RUNNING"
        assert slot["restart_count"] == 1
        assert len(factory_calls) == 2  # 工厂重造新实例（崩溃重启语义）
        adapter.stop()

    def test_restart_exhaustion_marks_exhausted(self, tmp_path, monkeypatch):
        """重启超限（默认 3 次）→ EXHAUSTED 熔断等人工，不再重启。"""
        factory_calls: list[int] = []

        def _factory():
            factory_calls.append(1)
            return _FakeSession(fail_on_start=True)

        monotonic_holder = {"t": 1000.0}
        monkeypatch.setattr(lsa_module.time, "monotonic", lambda: monotonic_holder["t"])
        adapter = _make_adapter(
            tmp_path,
            [StrategySlot("s1", _factory)],
            max_restart_attempts=3,
            restart_backoff_seconds=30.0,
        )
        adapter.start()
        for _ in range(4):
            monotonic_holder["t"] += 31.0
            adapter._supervise_once()
        slot = adapter.status_report()["slots"][0]
        assert slot["state"] == "EXHAUSTED"
        assert slot["restart_count"] == 3
        assert len(factory_calls) == 4  # 初次 + 3 次重启，第 4 次 supervise 触发熔断不再调工厂
        # EXHAUSTED 后监督不再尝试重启
        monotonic_holder["t"] += 300.0
        adapter._supervise_once()
        assert len(factory_calls) == 4
        adapter.stop()


# ---------------------------------------------------------------------
# run() 有界监督循环
# ---------------------------------------------------------------------


class TestRunLoop:
    def test_run_until_close_time(self, tmp_path):
        """close_at 到点 → 优雅收场：返回 0 + 服务停止 + slot STOPPED + 每轮心跳。"""
        clock = _FakeClock(datetime(2026, 8, 28, 14, 59, 0, tzinfo=_SHANGHAI_TZ))
        session = _FakeSession()
        adapter = _make_adapter(
            tmp_path,
            [StrategySlot("s1", lambda: session)],
            clock=clock,
            heartbeat_interval_seconds=15.0,
        )
        adapter.start()
        rc = adapter.run(close_at=dtime(15, 5))
        assert rc == 0
        assert not adapter.is_running
        assert session.stop_calls == 1
        assert len(clock.slept) > 0  # 监督循环确实跑过
        hb = _read_heartbeat(tmp_path)
        assert hb["running"] is False

    def test_run_stops_on_stop_event(self, tmp_path):
        """外部 stop_event 截止：预置位→零迭代收场；迭代中置位→下轮收场。"""
        clock = _FakeClock(datetime(2026, 8, 28, 9, 30, tzinfo=_SHANGHAI_TZ))
        session = _FakeSession()
        adapter = _make_adapter(tmp_path, [StrategySlot("s1", lambda: session)], clock=clock)
        adapter.start()
        preset = threading.Event()
        preset.set()
        rc = adapter.run(stop_event=preset)
        assert rc == 0 and not adapter.is_running
        assert len(clock.slept) == 0  # 预置位→零迭代
        assert session.stop_calls == 1

        # 迭代中置位：sleeper 第 2 次调用时置位 → 两轮后收场
        clock2 = _FakeClock(datetime(2026, 8, 28, 9, 30, tzinfo=_SHANGHAI_TZ))
        event2 = threading.Event()
        real_sleeper = clock2.sleeper

        def _sleeper_setting_event(seconds: float) -> None:
            real_sleeper(seconds)
            if len(clock2.slept) >= 2:
                event2.set()

        session2 = _FakeSession()
        adapter2 = _make_adapter(
            tmp_path,
            [StrategySlot("s2", lambda: session2)],
            clock=clock2,
            sleeper=_sleeper_setting_event,
        )
        adapter2.start()
        rc2 = adapter2.run(stop_event=event2)
        assert rc2 == 0
        assert len(clock2.slept) == 2

    def test_run_supervises_each_iteration(self, tmp_path, monkeypatch):
        """每轮迭代执行监督：FAILED slot 在 run 循环内被退避重启。"""
        clock = _FakeClock(datetime(2026, 8, 28, 9, 30, tzinfo=_SHANGHAI_TZ))
        sessions = [_FakeSession(fail_on_start=True), _FakeSession()]
        factory_calls: list[int] = []

        def _factory():
            factory_calls.append(1)
            return sessions[min(len(factory_calls) - 1, 1)]

        monotonic_holder = {"t": 1000.0}
        monkeypatch.setattr(lsa_module.time, "monotonic", lambda: monotonic_holder["t"])

        real_sleeper = clock.sleeper

        def _sleeper(seconds: float) -> None:
            real_sleeper(seconds)
            monotonic_holder["t"] += seconds  # 假钟联动退避钟

        adapter = _make_adapter(
            tmp_path,
            [StrategySlot("s1", _factory)],
            clock=clock,
            heartbeat_interval_seconds=15.0,
            restart_backoff_seconds=20.0,
            sleeper=_sleeper,
        )
        adapter.start()
        rc = adapter.run(close_at=dtime(9, 31))  # 两轮迭代即重启
        assert rc == 0
        assert len(factory_calls) == 2  # 循环内完成一次退避重启
