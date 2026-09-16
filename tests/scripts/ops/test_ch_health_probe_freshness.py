# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §A3-freshness
# [MODULE] tests.scripts.ops.test_ch_health_probe_freshness
# [DOMAIN] D_DATA
# [A_module] module_id=test-ch-health-probe-freshness | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ch_health_probe 盘中 tick 新鲜度检查单测（A3 推进度看门狗，2026-09-16）。

背景：09:36 实时链路断供 3 小时而全部既有监控绿灯——既有看门狗锚定订阅侧
last_tick_ts，写入侧断链照样刷新。A3 锚定 CH 侧 max(timestamp) 端到端判定。

覆盖（纯 mock，不触真 CH）：
1. 盘中窗口判定（上午/午休/下午/收盘后）
2. 新鲜数据不告警
3. 落后超阈值告警（Alerter 记录一次）
4. 今日零数据且已过开盘缓冲→告警
5. 非交易日/盘外不告警
"""

from __future__ import annotations

import datetime
import importlib.util
from pathlib import Path

_PROBE_PATH = Path(__file__).resolve().parents[3] / "scripts" / "ops" / "ch_health_probe.py"


def _load():
    spec = importlib.util.spec_from_file_location("ch_health_probe_under_test", _PROBE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeAlerter:
    def __init__(self):
        self.calls: list[tuple] = []

    def notify(self, *args, **kwargs):
        self.calls.append((args, kwargs))


def test_in_tick_window():
    mod = _load()
    assert mod._in_tick_window(datetime.datetime(2026, 9, 16, 9, 30)) is True
    assert mod._in_tick_window(datetime.datetime(2026, 9, 16, 10, 0)) is True
    assert mod._in_tick_window(datetime.datetime(2026, 9, 16, 12, 0)) is False  # 午休
    assert mod._in_tick_window(datetime.datetime(2026, 9, 16, 14, 0)) is True
    assert mod._in_tick_window(datetime.datetime(2026, 9, 16, 15, 1)) is False  # 收盘后


def test_fresh_data_no_alert(monkeypatch):
    mod = _load()
    alerts = _FakeAlerter()
    monkeypatch.setattr("zephyr.data.ch_reader.query", lambda q, timeout=10: "2026-09-16 09:59:00")
    monkeypatch.setattr(mod.trading_calendar, "is_trading_day", lambda d=None: True)
    mod._check_tick_freshness(15.0, alerts, now=datetime.datetime(2026, 9, 16, 10, 0))
    assert alerts.calls == []  # 落后 1 分钟 < 阈值


def test_stale_data_alerts(monkeypatch):
    mod = _load()
    alerts = _FakeAlerter()
    monkeypatch.setattr("zephyr.data.ch_reader.query", lambda q, timeout=10: "2026-09-16 09:30:00")
    monkeypatch.setattr(mod.trading_calendar, "is_trading_day", lambda d=None: True)
    mod._check_tick_freshness(15.0, alerts, now=datetime.datetime(2026, 9, 16, 10, 0))
    assert len(alerts.calls) == 1  # 落后 30 分钟 ≥ 阈值
    assert "tick_freshness" in alerts.calls[0][0]


def test_no_data_today_after_open_buffer_alerts(monkeypatch):
    mod = _load()
    alerts = _FakeAlerter()
    monkeypatch.setattr("zephyr.data.ch_reader.query", lambda q, timeout=10: "")
    monkeypatch.setattr(mod.trading_calendar, "is_trading_day", lambda d=None: True)
    mod._check_tick_freshness(15.0, alerts, now=datetime.datetime(2026, 9, 16, 9, 50))
    assert len(alerts.calls) == 1  # 过开盘缓冲仍零数据=链路自始断供


def test_no_data_today_within_open_buffer_no_alert(monkeypatch):
    mod = _load()
    alerts = _FakeAlerter()
    monkeypatch.setattr("zephyr.data.ch_reader.query", lambda q, timeout=10: "")
    monkeypatch.setattr(mod.trading_calendar, "is_trading_day", lambda d=None: True)
    mod._check_tick_freshness(15.0, alerts, now=datetime.datetime(2026, 9, 16, 9, 35))
    assert alerts.calls == []  # 开盘缓冲期内宽容


def test_outside_window_no_alert(monkeypatch):
    mod = _load()
    alerts = _FakeAlerter()
    monkeypatch.setattr("zephyr.data.ch_reader.query", lambda q, timeout=10: "2026-09-16 09:30:00")
    monkeypatch.setattr(mod.trading_calendar, "is_trading_day", lambda d=None: True)
    mod._check_tick_freshness(15.0, alerts, now=datetime.datetime(2026, 9, 16, 12, 30))  # 午休
    assert alerts.calls == []


def test_non_trading_day_no_alert(monkeypatch):
    mod = _load()
    alerts = _FakeAlerter()
    monkeypatch.setattr("zephyr.data.ch_reader.query", lambda q, timeout=10: "2026-09-16 09:30:00")
    monkeypatch.setattr(mod.trading_calendar, "is_trading_day", lambda d=None: False)  # 节假日
    mod._check_tick_freshness(15.0, alerts, now=datetime.datetime(2026, 10, 1, 10, 0))
    assert alerts.calls == []
