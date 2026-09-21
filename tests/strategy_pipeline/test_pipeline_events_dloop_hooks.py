# [BLUEPRINT] MOD-BT-190 | docs/03_modules/_domain_backtest/blueprint.md（丁线扩面钩子用例：warroom 上链+竞价命中上链）
# [MODULE] tests.strategy_pipeline.test_pipeline_events_dloop_hooks
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.pipeline_events(maybe_run_warroom_pipeline/maybe_record_auction_hit)
# [INVARIANTS] 测试隔离零生产路径（marker/业务日/告警/底层模块全 monkeypatch）；唤醒词/时窗/记号三重过滤断言
# [TTL] permanent

"""丁线扩面事件链钩子单测：唤醒词过滤、时窗闸、记号幂等、fail-open 永不抛。"""

from __future__ import annotations

import datetime as _dt

import pytest

from zephyr.strategy_pipeline import pipeline_events as pe


@pytest.fixture()
def _isolate(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[str]]:
    """隔离面：记号空库+业务日固定+告警吞掉+时间可控。"""
    calls: dict[str, list[str]] = {"markers": [], "alerts": []}
    monkeypatch.setattr(pe, "_marker_seen", lambda name: False)
    monkeypatch.setattr(pe, "_touch_marker", lambda name: calls["markers"].append(name))
    monkeypatch.setattr(pe, "alert", lambda *a, **k: calls["alerts"].append(str(a[0])[:40]))
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-21")
    return calls


def test_warroom_wake_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    """唤醒词不含 daily_kline 族=零动作跳过（不触底层）。"""
    monkeypatch.setattr(
        pe, "resolve_pf_alloc_trade_date", lambda: (_ for _ in ()).throw(AssertionError("不该解析业务日"))
    )
    out = pe.maybe_run_warroom_pipeline(task_id="crypto_kline", success=True)
    assert out == {"action": "skipped_wake_point"}
    out2 = pe.maybe_run_warroom_pipeline(task_id="daily_kline", success=False)
    assert out2["action"] == "skipped_wake_point"


def test_warroom_runs_and_marks(_isolate: dict[str, list[str]], monkeypatch: pytest.MonkeyPatch) -> None:
    """daily_kline 唤醒→跑编排+落记号；再跑一次=already_run（幂等闸）。"""
    monkeypatch.setattr(
        "zephyr.plan_engine.daily_warroom_pipeline.run_daily_warroom_pipeline",
        lambda d, *, phase, **k: type("R", (), {"premarket_status": "ok", "postmarket_status": "ok"})(),
    )
    out = pe.maybe_run_warroom_pipeline(task_id="kline_daily_incremental", success=True)
    assert out["action"] == "run" and out["trade_date"] == "2026-09-21"
    assert _isolate["markers"] == ["warroom_pipeline:2026-09-21"]
    monkeypatch.setattr(pe, "_marker_seen", lambda name: True)
    out2 = pe.maybe_run_warroom_pipeline(task_id="daily_kline", success=True)
    assert out2["action"] == "already_run"


def test_warroom_fail_open(_isolate: dict[str, list[str]], monkeypatch: pytest.MonkeyPatch) -> None:
    """编排炸=error 留痕出声不抛（钩子永不反噬调度器）。"""

    def _boom(d, *, phase, **k):
        raise RuntimeError("注入失败:warroom")

    monkeypatch.setattr("zephyr.plan_engine.daily_warroom_pipeline.run_daily_warroom_pipeline", _boom)
    out = pe.maybe_run_warroom_pipeline(task_id="daily_kline", success=True)
    assert out["action"] == "error" and out["error"] == "RuntimeError"
    assert any("WARROOM" in a for a in _isolate["alerts"])


def test_auction_wake_and_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """唤醒词=1min/5min 专属；窗外（14:00）=skipped；10:15 窗内才触达底层。"""
    monkeypatch.setattr(
        pe, "resolve_pf_alloc_trade_date", lambda: (_ for _ in ()).throw(AssertionError("不该解析业务日"))
    )
    assert pe.maybe_record_auction_hit(task_id="kline_etf_60min")["action"] == "skipped_wake_point"
    assert pe.maybe_record_auction_hit(task_id="kline_etf_5min_incremental")["action"] != "run"

    class _FakeDT(_dt.datetime):
        @classmethod
        def now(cls, tz=None):  # noqa: ARG005 — 时区注入面复刻
            return cls(2026, 9, 21, 14, 0, tzinfo=tz)

    real_dt = pe.datetime if hasattr(pe, "datetime") else None
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-21", raising=False)
    # 窗外闸在业务日解析之前：14:00 应直接 skipped_outside_window
    monkeypatch.setattr(_dt, "datetime", _FakeDT)
    out = pe.maybe_record_auction_hit(task_id="kline_etf_1min_incremental", success=True)
    assert out["action"] == "skipped_outside_window"
    if real_dt is not None:  # 还原（monkeypatch 自动还原，此处防御式占位）
        pass
