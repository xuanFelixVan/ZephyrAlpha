# [MODULE] tests.scripts.ops.test_ch_health_probe_replay
# [DOMAIN] D_DATA
# [A_module] module_id=test-ch-health-probe-replay | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ch_health_probe 僵尸回放 / 业务时间戳滞后检查单测（#ZOMBIE-REPLAY，2026-10-14）。

背景（实测）：c1_market.tick_depth_5 的 max(ingest_ts)=2026-10-14 16:41（今日），
而 max(timestamp)=2026-10-12 11:14——桥文件自 10-12 冻结后进程反复重启重放，
陈旧业务数据被盖上新入库时间。既有判活口径（wall clock 心跳 / ingest_ts / 文件 mtime）
对这一形态全绿。本件把判活口径换成**业务时间戳**，并专设回放检测。

覆盖（纯 mock，不触真 CH）：
1. 僵尸回放：ingest_ts 大幅领先 timestamp → 告警 tick_replay
2. 健康态：ingest_ts 与 timestamp 相差数分钟 → 无告警
3. 业务时间戳滞后：max(timestamp) 落后 N 个交易日 → 告警 tick_biz_lag
4. 同日业务时间戳 → 无滞后告警
5. 业务时间戳缺失（空表/全损）→ 告警
6. 交易日区间口径：(start, end] 不含 start 当日
"""

from __future__ import annotations

import datetime
import importlib.util
from pathlib import Path

_PROBE_PATH = Path(__file__).resolve().parents[4] / "scripts" / "ops" / "ch_health_probe.py"


def _load():
    spec = importlib.util.spec_from_file_location("ch_health_probe_replay_under_test", _PROBE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeAlerter:
    def __init__(self):
        self.calls: list[tuple] = []

    def notify(self, *args, **kwargs):
        self.calls.append((args, kwargs))


def _patch_query(mod, monkeypatch, max_ts: str, max_ingest: str):
    monkeypatch.setattr(
        "zephyr.data.ch_reader.query",
        lambda q, timeout=10: f"{max_ts}\t{max_ingest}",
    )


def _patch_calendar(mod, monkeypatch, days: list[datetime.date]):
    monkeypatch.setattr(
        mod.trading_calendar,
        "trading_days_in_range",
        lambda s, e: [d for d in days if s <= d <= e],
    )


def test_zombie_replay_alerts(monkeypatch):
    """真实事故形态：ingest 10-14 16:41 / timestamp 10-12 11:14（领先约 53 小时）。"""
    mod = _load()
    alerts = _FakeAlerter()
    _patch_query(mod, monkeypatch, "2026-10-12 11:14:47+08:00", "2026-10-14 08:41:08+00:00")
    _patch_calendar(mod, monkeypatch, [datetime.date(2026, 10, d) for d in (12, 13, 14)])
    mod._check_tick_replay(24.0, 1, alerts, now=datetime.datetime(2026, 10, 14, 21, 0))
    kinds = [c[0][0] for c in alerts.calls]
    assert "tick_replay" in kinds, f"僵尸回放未告警: {kinds}"
    assert "tick_biz_lag" in kinds, f"业务时间戳滞后未告警: {kinds}"


def test_healthy_no_alert(monkeypatch):
    """健康态：ingest 仅领先业务时间戳 3 分钟，且业务时间戳就是今天。"""
    mod = _load()
    alerts = _FakeAlerter()
    _patch_query(mod, monkeypatch, "2026-10-14 10:00:00+08:00", "2026-10-14 02:03:00+00:00")
    _patch_calendar(mod, monkeypatch, [datetime.date(2026, 10, 14)])
    mod._check_tick_replay(24.0, 1, alerts, now=datetime.datetime(2026, 10, 14, 10, 5))
    assert alerts.calls == [], f"健康态误告警: {alerts.calls}"


def test_biz_lag_alerts(monkeypatch):
    """业务时间戳落后 2 个交易日（10-12 → 10-14），即便 ingest 是新的也须告警。"""
    mod = _load()
    alerts = _FakeAlerter()
    _patch_query(mod, monkeypatch, "2026-10-12 11:14:47+08:00", "2026-10-14 08:41:08+00:00")
    _patch_calendar(mod, monkeypatch, [datetime.date(2026, 10, d) for d in (12, 13, 14)])
    mod._check_tick_replay(24.0, 1, alerts, now=datetime.datetime(2026, 10, 14, 21, 0))
    lag_calls = [c for c in alerts.calls if c[0][0] == "tick_biz_lag"]
    assert len(lag_calls) == 1
    assert "2 个交易日" in lag_calls[0][0][1], lag_calls[0][0][1]


def test_same_day_no_lag_alert(monkeypatch):
    mod = _load()
    alerts = _FakeAlerter()
    _patch_query(mod, monkeypatch, "2026-10-14 09:35:00+08:00", "2026-10-14 01:36:00+00:00")
    _patch_calendar(mod, monkeypatch, [datetime.date(2026, 10, 14)])
    mod._check_tick_replay(24.0, 1, alerts, now=datetime.datetime(2026, 10, 14, 9, 40))
    assert [c for c in alerts.calls if c[0][0] == "tick_biz_lag"] == []


def test_missing_biz_timestamp_alerts(monkeypatch):
    mod = _load()
    alerts = _FakeAlerter()
    _patch_query(mod, monkeypatch, "0000-00-00 00:00:00", "2026-10-14 08:41:08+00:00")
    _patch_calendar(mod, monkeypatch, [datetime.date(2026, 10, 14)])
    mod._check_tick_replay(24.0, 1, alerts, now=datetime.datetime(2026, 10, 14, 21, 0))
    assert len(alerts.calls) == 1
    assert alerts.calls[0][0][0] == "tick_replay"


def test_trading_days_between_excludes_start_day(monkeypatch):
    """(start, end] 口径：同日=0，次日=1，跨 2 日=2。"""
    mod = _load()
    _DAYS = [datetime.date(2026, 10, d) for d in (12, 13, 14)]
    _patch_calendar(mod, monkeypatch, _DAYS)
    assert mod._trading_days_between(datetime.date(2026, 10, 14), datetime.date(2026, 10, 14)) == 0
    assert mod._trading_days_between(datetime.date(2026, 10, 12), datetime.date(2026, 10, 13)) == 1
    assert mod._trading_days_between(datetime.date(2026, 10, 12), datetime.date(2026, 10, 14)) == 2


def test_trading_days_falls_back_to_calendar_days(monkeypatch):
    """日历包不可用 → 退化为日历日（更严），不静默返回 0。"""
    mod = _load()

    def _boom(s, e):
        raise RuntimeError("calendar unavailable")

    monkeypatch.setattr(mod.trading_calendar, "trading_days_in_range", _boom)
    assert mod._trading_days_between(datetime.date(2026, 10, 12), datetime.date(2026, 10, 14)) == 2
