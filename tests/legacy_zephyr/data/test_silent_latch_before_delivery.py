# [MODULE] tests.zephyr.data.test_silent_latch_before_delivery
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.source_health_check; zephyr.data_eng.data_anomaly_alerter; zephyr.trading.resource_optimization; zephyr.trading.health_monitor; zephyr.strategy_pipeline.daily_decision_orchestrator
# [TESTS] 本文件
# [TTL] permanent
"""静默失效模式扫查（车道 st-ff-silent-20260918）收口的**能红测试钉**。

判据同源（#ARCH-327 实证教训）：被断言的那条防线必须是**真对象**，故障只打在
它的协作方/环境上；禁把防线自身 patch 成 MagicMock。

- 数据源连续异常告警闩：真 `Alerter`（failures 目录父段=普通文件 → 真 NotADirectoryError
  → notify 返回 False），断言**落盘的** streaks JSON 里 alerted 仍为 false；
- 数据异常告警器去重戳：真 `DataAnomalyAlerter.evaluate`，sink 第一次真抛；
- 资源压力档位闩：真 `_ExternalNotifier.emit_pressure_event`，event bus 真抛；
- 探针注册/告警通道 DEBUG 放行：真 `HealthMonitor` / 真 `_alert`，故障=真 ImportError、真 ConnectionError。
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from zephyr.data import source_health_check as shc
from zephyr.data_eng.data_anomaly_alerter import AnomalyKind, AnomalySignal, DataAnomalyAlerter
from zephyr.strategy_pipeline import daily_decision_orchestrator as ddo
from zephyr.trading import health_monitor as hm
from zephyr.trading.resource_optimization import (
    PressureLevel,
    _ExternalNotifier,
)


def _blocked_failures_root(tmp_path: Path) -> Path:
    """返回一个**必然落盘失败**的 failures 目录（其父段是普通文件 → 真 NotADirectoryError）。"""
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    return blocker / "failures"


def _seed_streak(monkeypatch, tmp_path: Path, source: str, streak: int) -> Path:
    streaks = tmp_path / "streaks.json"
    today = datetime.now(timezone.utc).date().isoformat()
    streaks.write_text(
        json.dumps({source: {"streak": streak, "alerted": False, "last_date": today}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(shc, "_STREAKS_PATH", streaks)
    return streaks


class TestSourceHealthAlertLatch:
    """F1：告警未落盘时**不得**把"已告警"写进持久化状态。"""

    def test_un_delivered_alert_does_not_latch_in_persisted_state(self, monkeypatch, tmp_path, caplog):
        blocked = _blocked_failures_root(tmp_path)
        monkeypatch.setattr("zephyr.data.alerter._DEFAULT_FAILURES_DIR", blocked)
        streaks = _seed_streak(monkeypatch, tmp_path, "blocked_src", streak=shc._STREAK_ALERT_DAYS)

        with caplog.at_level(logging.DEBUG):
            shc._update_failure_streaks([{"source": "blocked_src", "status": "error", "error": "boom"}])

        persisted = json.loads(streaks.read_text(encoding="utf-8"))
        assert persisted["blocked_src"]["alerted"] is False, (
            "告警从未落盘却被记作已告警并持久化 → 该源余生（含重启）不再告警"
        )
        assert any("未落盘" in r.getMessage() for r in caplog.records), "未送达必须留可见痕"

    def test_delivered_alert_does_latch(self, monkeypatch, tmp_path):
        monkeypatch.setattr("zephyr.data.alerter._DEFAULT_FAILURES_DIR", tmp_path / "failures_ok")
        streaks = _seed_streak(monkeypatch, tmp_path, "live_src", streak=shc._STREAK_ALERT_DAYS)

        shc._update_failure_streaks([{"source": "live_src", "status": "error", "error": "boom"}])

        persisted = json.loads(streaks.read_text(encoding="utf-8"))
        assert persisted["live_src"]["alerted"] is True

    def test_next_run_retries_after_failed_delivery(self, monkeypatch, tmp_path):
        monkeypatch.setattr("zephyr.data.alerter._DEFAULT_FAILURES_DIR", _blocked_failures_root(tmp_path))
        streaks = _seed_streak(monkeypatch, tmp_path, "retry_src", streak=shc._STREAK_ALERT_DAYS)
        payload = [{"source": "retry_src", "status": "error", "error": "boom"}]

        shc._update_failure_streaks(payload)
        shc._update_failure_streaks(payload)  # 两轮都未送达 → 必须仍在重试
        assert json.loads(streaks.read_text(encoding="utf-8"))["retry_src"]["alerted"] is False

        monkeypatch.setattr("zephyr.data.alerter._DEFAULT_FAILURES_DIR", tmp_path / "failures_recovered")
        shc._update_failure_streaks(payload)
        assert json.loads(streaks.read_text(encoding="utf-8"))["retry_src"]["alerted"] is True


class TestAnomalyAlerterDedupStamp:
    """F2：去重戳不得在路由成功之前推进。"""

    @staticmethod
    def _signal() -> AnomalySignal:
        return AnomalySignal(
            kind=AnomalyKind.PRICE_JUMP,
            symbol="600519.SH",
            metric_value=99.0,
            threshold=1.0,
            detail="jump",
        )

    def test_failed_route_is_retried_in_next_window(self, tmp_path):
        calls: list[str] = []

        def sink(task_id: str, message: str, **_kw: Any) -> bool:
            calls.append(task_id)
            if len(calls) == 1:
                raise OSError("route channel down")
            return True

        alerter = DataAnomalyAlerter(alert_sink=sink, merge_window_sec=3600)
        base = datetime(2026, 9, 18, 1, 0, 0, tzinfo=timezone.utc)
        sig = self._signal()

        alerter.evaluate([sig], now_utc=base, source="t")
        assert len(calls) == 1
        alerter.evaluate([sig], now_utc=datetime(2026, 9, 18, 1, 5, 0, tzinfo=timezone.utc), source="t")
        assert len(calls) == 2, "首条未送达却被去重戳吞掉 → 合并窗口内永不重试"

    def test_dedup_stamp_still_suppresses_successful_routes(self):
        calls: list[str] = []

        def sink(task_id: str, message: str, **_kw: Any) -> bool:
            calls.append(task_id)
            return True

        alerter = DataAnomalyAlerter(alert_sink=sink, merge_window_sec=3600)
        sig = self._signal()
        base = datetime(2026, 9, 18, 1, 0, 0, tzinfo=timezone.utc)
        alerter.evaluate([sig], now_utc=base, source="t")
        alerter.evaluate([sig], now_utc=datetime(2026, 9, 18, 1, 1, 0, tzinfo=timezone.utc), source="t")
        assert len(calls) == 1, "已送达的告警必须继续被合并窗口去重（不得放宽）"

    def test_route_failure_log_names_real_exception_type(self, caplog):
        def sink(task_id: str, message: str, **_kw: Any) -> bool:
            raise ValueError("boom-typed")

        alerter = DataAnomalyAlerter(alert_sink=sink, merge_window_sec=60)
        with caplog.at_level(logging.ERROR):
            alerter.evaluate(
                [self._signal()],
                now_utc=datetime(2026, 9, 18, 1, 0, 0, tzinfo=timezone.utc),
                source="t",
            )
        msgs = [r.getMessage() for r in caplog.records if "路由异常" in r.getMessage()]
        assert msgs and "ValueError" in msgs[0], "兜底日志必须带真实异常类型名（不预设失败类别）"


class TestPressureEventLatch:
    """F3：档位闩只在 event bus 真送达后推进。"""

    @staticmethod
    def _engine() -> SimpleNamespace:
        return SimpleNamespace(
            eventbus_enabled=True,
            _eventbus_topic="resource.pressure",
            last_pressure_level=PressureLevel.NORMAL,
        )

    def _snap(self, level: PressureLevel) -> SimpleNamespace:
        return SimpleNamespace(
            pressure=level,
            cpu_percent=91.0,
            memory_percent=93.0,
            process_count=10,
            timestamp=1.0,
        )

    def test_latch_holds_when_emit_fails(self, monkeypatch):
        from zephyr.shared import event_bus as eb

        def boom(*_a: Any, **_kw: Any) -> None:
            raise ConnectionError("bus down")

        monkeypatch.setattr(eb.bus, "emit", boom)
        engine = self._engine()
        _ExternalNotifier.emit_pressure_event(engine, self._snap(PressureLevel.CRITICAL))
        assert engine.last_pressure_level is PressureLevel.NORMAL, "外发失败却推进档位 → 同一压力档余生不再外发"

    def test_latch_advances_and_dedups_on_success(self, monkeypatch):
        emitted: list[tuple] = []
        from zephyr.shared import event_bus as eb

        monkeypatch.setattr(eb.bus, "emit", lambda *a, **kw: emitted.append((a, kw)))
        engine = self._engine()
        _ExternalNotifier.emit_pressure_event(engine, self._snap(PressureLevel.CRITICAL))
        assert engine.last_pressure_level is PressureLevel.CRITICAL
        _ExternalNotifier.emit_pressure_event(engine, self._snap(PressureLevel.CRITICAL))
        assert len(emitted) == 1, "同档位成功送达后仍须去重（不得放宽）"

    def test_retry_after_channel_recovers(self, monkeypatch):
        from zephyr.shared import event_bus as eb

        state = {"down": True}
        seen: list[int] = []

        def maybe_emit(*_a: Any, **_kw: Any) -> None:
            if state["down"]:
                raise ConnectionError("bus down")
            seen.append(1)

        monkeypatch.setattr(eb.bus, "emit", maybe_emit)
        engine = self._engine()
        snap = self._snap(PressureLevel.CRITICAL)
        _ExternalNotifier.emit_pressure_event(engine, snap)
        state["down"] = False
        _ExternalNotifier.emit_pressure_event(engine, snap)
        assert seen == [1], "通道恢复后必须补发"


class TestDebugReleaseVisibility:
    """F4/F5：哨兵自身失明（探针注册失败 / 告警通道不可达）不得只留 DEBUG 痕。"""

    def test_probe_registration_failure_is_warning_visible(self, monkeypatch, tmp_path, caplog):
        monitor = hm.HealthMonitor(snapshot_dir=tmp_path / "snap")

        def boom(*_a: Any, **_kw: Any) -> None:
            raise LookupError("probe registry write failed")

        monitor.register_probe = boom  # 真注册口故障（防线=可见性日志，未 mock）
        with caplog.at_level(logging.WARNING):
            monitor.register_shared_monitoring_probes()
        msgs = [r.getMessage() for r in caplog.records if "注册失败" in r.getMessage()]
        assert msgs, "探针注册失败在 WARNING 档位不可见 = 健康视图静默偏乐观"
        assert all("LookupError" in m for m in msgs), "须带真实异常类型名（本例 LookupError），禁预设失败类别"

    def test_alert_channel_failure_is_error_visible(self, caplog):
        def boom(_msg: str, **_kw: Any) -> None:
            raise ConnectionError("alerter 通道断")

        with caplog.at_level(logging.WARNING):
            ddo._alert(boom, "拍板降级播报", level="WARN")
        recs = [r for r in caplog.records if "告警通道不可达" in r.getMessage()]
        assert recs, "拍板链告警通道故障必须可见"
        assert recs[0].levelno >= logging.ERROR
        assert "ConnectionError" in recs[0].getMessage()
        assert recs[0].exc_info, "必须保留栈"


@pytest.mark.parametrize("rel", ["data/source_health_check.py"])
def test_patched_files_keep_line_endings(rel: str):
    """R-008 换行地雷自检：收口不得整篇改行尾。

    WO-12/C6 判定：.gitattributes 对 *.py 强制 `text eol=lf`，仓库规范行尾
    就是 LF（index=i/lf，规范检出=w/lf）。原断言"全文件纯 CRLF"是旧工作区
    autocrlf 残留的过时口径，与 .gitattributes 直接矛盾，任何规范检出必挂。
    反改雷语义保留：回归=有人把 CRLF 写回来，故断言纯 LF。
    """
    p = Path(__file__).resolve().parents[3] / "src" / "zephyr" / rel
    raw = p.read_bytes()
    assert raw.count(b"\r\n") == 0, f"{rel} 违反 .gitattributes eol=lf（出现 CRLF）"
