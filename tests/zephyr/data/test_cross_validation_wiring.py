# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_cross_validation_wiring
# [DOMAIN] D_DATA
# [DEPENDENCIES] pytest; zephyr.data.scheduler; zephyr.data.cross_source_validator
# [CONSUMERS] F04 断链接线存在性守卫（scheduler cross_validation 槽 ↔ CrossSourceValidator）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] monkeypatch 断言被调——validator 全替身，零真 CH/零网络；schedule.yaml 断言只读
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [A_module] module_id=MOD-L00-004 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""F04 断链接线测试：cross_validation 调度槽确实调用 CrossSourceValidator（monkeypatch 断言被调）。"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, os.path.join(str(_ROOT), "src"))

from zephyr.data import scheduler as sched  # noqa: E402
from zephyr.data.cross_source_validator import ValidationReport  # noqa: E402


class _FakeScheduler:
    def __init__(self):
        self._alerter = MagicMock()


@pytest.fixture()
def validator_calls(monkeypatch):
    """替换 CrossSourceValidator 为记录型替身；返回 (calls, set_report)。

    2026-09-28 st-c9-purify：槽位新增分歧率统计输出侧（divergence_stats），本 fixture
    同步打桩——否则替身 report 会走真统计腿写生产 data/（宪法 §9.6 测试隔离）。
    """
    calls: list[dict] = []
    stats_calls: list = []
    holder: dict = {"report": ValidationReport(check_time=None)}
    monkeypatch.setattr(
        "zephyr.data.divergence_stats.record_report_stats", lambda report: stats_calls.append(report) or {}
    )

    class _FakeValidator:
        def __init__(self, *a, **k):
            pass

        def validate(self, time_window_minutes):
            calls.append({"time_window_minutes": time_window_minutes})
            return holder["report"]

    monkeypatch.setattr("zephyr.data.cross_source_validator.CrossSourceValidator", _FakeValidator)
    return calls, holder, stats_calls


def test_cross_validation_slot_invokes_validator(validator_calls):
    calls, holder, _stats = validator_calls
    holder["report"] = ValidationReport(check_time=None, total_symbols=5, passed=5)
    out = sched._run_special_schedule(_FakeScheduler(), "cross_validation")
    assert out == {"cross_validation": True}
    assert len(calls) == 1
    assert calls[0]["time_window_minutes"] == sched._CROSS_VALIDATION_WINDOW_MINUTES


def test_cross_validation_feeds_divergence_stats(validator_calls):
    """#423 形态锁第二段：槽位必须把校验报告喂给分歧率统计（不喂=两周观察断供）。"""
    calls, holder, stats_calls = validator_calls
    report = ValidationReport(check_time=None, total_symbols=5, passed=5)
    holder["report"] = report
    out = sched._run_special_schedule(_FakeScheduler(), "cross_validation")
    assert out == {"cross_validation": True}
    assert stats_calls == [report], "分歧率统计未接到 cross_validation 槽输出侧"


def test_cross_validation_fail_alerts_and_returns_false(validator_calls):
    calls, holder, _stats = validator_calls
    holder["report"] = ValidationReport(check_time=None, failures=2)
    fake = _FakeScheduler()
    out = sched._run_special_schedule(fake, "cross_validation")
    assert out == {"cross_validation": False}
    assert len(calls) == 1
    fake._alerter.notify.assert_called_once()
    assert fake._alerter.notify.call_args.args[0] == "cross_validation"


def test_cross_validation_exception_degrades_to_alerter(monkeypatch):
    class _BoomValidator:
        def __init__(self, *a, **k):
            pass

        def validate(self, time_window_minutes):
            raise RuntimeError("ch down")

    monkeypatch.setattr("zephyr.data.cross_source_validator.CrossSourceValidator", _BoomValidator)
    fake = _FakeScheduler()
    out = sched._run_special_schedule(fake, "cross_validation")
    assert out == {"cross_validation": False}
    fake._alerter.notify.assert_called_once()
    assert fake._alerter.notify.call_args.kwargs["level"] == "ERROR"


def test_cross_validation_slot_registered_in_schedule_yaml():
    doc = yaml.safe_load((sched._DEFAULT_CONFIG_DIR / "schedule.yaml").read_text(encoding="utf-8"))
    slot = doc["schedules"]["cross_validation"]
    assert slot["cron"] == "15 23 * * 0-4"  # integrity_check(23:00) 之后错峰
    assert slot["executor"] in ("default", "heavy", "realtime", "intraday_minute", "intraday_sector")


def test_cross_validation_slot_is_trading_day_guarded():
    from zephyr.data.trading_calendar import TRADING_DAY_GUARDED_SCHEDULES

    assert "cross_validation" in TRADING_DAY_GUARDED_SCHEDULES
