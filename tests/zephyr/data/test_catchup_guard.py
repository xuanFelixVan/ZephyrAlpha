# [BLUEPRINT] MOD-L00-021 | docs/03_modules/_domain_data/catchup_guard/blueprint.md
# [MODULE] tests.zephyr.data.test_catchup_guard
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.catchup_guard; pytest; monkeypatch
# [CONSUMERS] pytest 循环验收
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 全部外部依赖(ProgressStore/scheduler/CH/日历/tasks.yaml)注入 mock；不触网不触库
# [MODIFY-GUARD] docs/03_modules/_domain_data/catchup_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即用例失败
# [TESTS] tests/zephyr/data/test_catchup_guard.py（自包含）
# [TTL] permanent
"""catchup_guard 单元测试：档期判定 5 桶 / 空表兜底 / 交易日晚点 / RUNNING 跳过 / 上限截断 / 单实例锁。"""

from __future__ import annotations

import datetime
import os

import pytest

from zephyr.data import catchup_guard as cg
from zephyr.data.alerter import LEVEL_ERROR, LEVEL_INFO

TODAY = datetime.date(2026, 9, 3)  # 周四（交易日）


class FakeStore:
    """progress_store 替身：task_id → {last_run_at, last_status}。"""

    def __init__(self, records: dict | None = None):
        self.records = records or {}
        self.saved = []

    def get_task_status(self, task_id):
        return self.records.get(task_id)

    def save_progress(self, task_id, source, last_key, status, rows_total=0, error_msg=None):
        self.saved.append((task_id, status))
        return True


class FakeAlerter:
    def __init__(self):
        self.calls = []

    def notify(self, task_id, error, level="INFO", source=None, extra=None):
        self.calls.append((task_id, level, error))
        return True


class FakeScheduler:
    def __init__(self, records=None, run_results=None):
        self._progress_store = FakeStore(records)
        self._alerter = FakeAlerter()
        self.run_results = run_results or {}
        self.ran = []

    def run_task(self, task_id):
        self.ran.append(task_id)
        return self.run_results.get(task_id, True)


class FakeCalendar:
    def __init__(self, trade_days, trading_today=True):
        self.trade_days = set(trade_days)
        self.trading_today = trading_today

    def is_trading_day(self, day=None):
        return self.trading_today

    def trading_days_in_range(self, start, end):
        return sorted(d for d in self.trade_days if start <= d <= end)


def _iso(d: datetime.date) -> str:
    return datetime.datetime(d.year, d.month, d.day, 12, 0, 0).isoformat()


@pytest.fixture
def patched(monkeypatch):
    """patch 模块内延迟导入的 tasks.yaml / 日历；返回日历句柄供用例定制。"""
    cal = FakeCalendar(
        [TODAY - datetime.timedelta(days=d) for d in range(1, 9)] + [TODAY]
    )
    monkeypatch.setattr("zephyr.data.calendar.get_market_calendar", lambda name="ashare": cal)
    tasks_holder = {"tasks": []}
    monkeypatch.setattr(
        "zephyr.data.backfill_checker._load_tasks_yaml", lambda: tasks_holder["tasks"]
    )
    return cal, tasks_holder


def _run(sched, monkeypatch, lock_path):
    return cg.run_catchup_guard(sched, lock_path=lock_path)


def test_monthly_overdue_and_fresh(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [
        {"task_id": "m_stale", "schedule": "monthly_static", "table": "t1"},
        {"task_id": "m_fresh", "schedule": "monthly_static", "table": "t2"},
    ]
    sched = FakeScheduler(
        records={
            "m_stale": {"last_run_at": _iso(datetime.date(2026, 8, 1)), "last_status": "SUCCESS"},
            "m_fresh": {"last_run_at": _iso(datetime.date(2026, 9, 1)), "last_status": "SUCCESS"},
        }
    )
    monkeypatch.setattr(cg, "_table_is_empty", lambda table: False)
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert sched.ran == ["m_stale"]
    assert r["rerun"] == {"m_stale": True}
    assert r["success"] is True


def test_weekly_bucket(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [
        {"task_id": "w_old", "schedule": "weekend_calibration", "table": "t3"},
        {"task_id": "w_new", "schedule": "weekend_backfill", "table": "t4"},
    ]
    sched = FakeScheduler(
        records={
            "w_old": {"last_run_at": _iso(TODAY - datetime.timedelta(days=8)), "last_status": "SUCCESS"},
            "w_new": {"last_run_at": _iso(TODAY - datetime.timedelta(days=3)), "last_status": "SUCCESS"},
        }
    )
    monkeypatch.setattr(cg, "_table_is_empty", lambda table: False)
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert sched.ran == ["w_old"]


def test_daily_and_intraday_overdue(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [
        {"task_id": "d_miss", "schedule": "daily_kline"},
        {"task_id": "d_ok", "schedule": "daily_capital"},
        {"task_id": "i_miss", "schedule": "intraday_minute"},
        {"task_id": "i_ok", "schedule": "intraday_realtime"},
    ]
    last_completed = TODAY - datetime.timedelta(days=1)
    sched = FakeScheduler(
        records={
            "d_miss": {"last_run_at": _iso(TODAY - datetime.timedelta(days=3)), "last_status": "SUCCESS"},
            "d_ok": {"last_run_at": _iso(last_completed), "last_status": "SUCCESS"},
            "i_miss": {"last_run_at": _iso(TODAY - datetime.timedelta(days=4)), "last_status": "SUCCESS"},
            "i_ok": {"last_run_at": _iso(last_completed), "last_status": "SUCCESS"},
        }
    )
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert sorted(sched.ran) == ["d_miss", "i_miss"]


def test_always_on_bucket(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [
        {"task_id": "a_miss", "schedule": "event_driven"},
        {"task_id": "a_ok", "schedule": "news_slow"},
    ]
    sched = FakeScheduler(
        records={
            "a_miss": {"last_run_at": _iso(TODAY - datetime.timedelta(days=3)), "last_status": "SUCCESS"},
            "a_ok": {"last_run_at": _iso(TODAY - datetime.timedelta(days=1)), "last_status": "SUCCESS"},
        }
    )
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert sched.ran == ["a_miss"]


def test_empty_table_fallback(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [
        {"task_id": "m_empty", "schedule": "monthly_static", "table": "c1_market.x"},
    ]
    # 打卡本月成功，但表空 → 兜底触发补跑
    sched = FakeScheduler(
        records={"m_empty": {"last_run_at": _iso(datetime.date(2026, 9, 1)), "last_status": "SUCCESS"}}
    )
    monkeypatch.setattr(cg, "_table_is_empty", lambda table: True)
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert sched.ran == ["m_empty"]
    assert r["empty_table"] == ["c1_market.x"]


def test_trading_day_only_deferred_on_holiday(patched, monkeypatch, tmp_path):
    cal, holder = patched
    cal.trading_today = False  # 假日
    holder["tasks"] = [{"task_id": "qmt_t", "schedule": "monthly_static", "table": "t9",
                        "extra": {"trading_day_only": True}}]
    sched = FakeScheduler()
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert sched.ran == []
    assert r["deferred"] == ["qmt_t"]
    assert r["overdue"] == []


def test_running_skipped_and_never_ran_due(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [
        {"task_id": "run_fly", "schedule": "daily_kline"},
        {"task_id": "never", "schedule": "daily_kline"},
    ]
    sched = FakeScheduler(
        records={
            "run_fly": {"last_run_at": _iso(TODAY), "last_status": "RUNNING"},
            # never: 无任何打卡记录
        }
    )
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert r["skipped_running"] == ["run_fly"]
    assert sched.ran == ["never"]


def test_cap_deferred(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [
        {"task_id": f"m{i:02d}", "schedule": "monthly_static", "table": f"t{i}"}
        for i in range(20)
    ]
    sched = FakeScheduler()  # 全部无记录 → 全 overdue
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert len(sched.ran) == cg.MAX_RERUN_PER_RUN
    assert len(r["cap_deferred"]) == 20 - cg.MAX_RERUN_PER_RUN


def test_disabled_and_unknown_schedule_skipped(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [
        {"task_id": "dead", "schedule": "daily_kline", "extra": {"disabled": True}},
        {"task_id": "odd", "schedule": "mystery_schedule"},
        {"task_id": "sys", "schedule": "integrity_check"},
    ]
    sched = FakeScheduler()
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert sched.ran == []
    assert r["overdue"] == []


def test_priority_order_monthly_first(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [
        {"task_id": "dly", "schedule": "daily_kline"},
        {"task_id": "mth", "schedule": "monthly_static", "table": "t"},
    ]
    sched = FakeScheduler()
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert sched.ran == ["mth", "dly"]


def test_lock_single_instance(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [{"task_id": "m1", "schedule": "monthly_static", "table": "t"}]
    lock = str(tmp_path / "lock")
    monkeypatch.setattr(cg, "_table_is_empty", lambda table: False)
    sched = FakeScheduler()
    r1 = _run(sched, monkeypatch, lock)
    assert r1["success"] is True
    # 锁文件已释放（正常路径 finally 释放）→ 第二次可再跑
    assert not os.path.exists(lock)
    r2 = _run(sched, monkeypatch, lock)
    assert r2["success"] is True


def test_lock_held_by_live_pid(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [{"task_id": "m1", "schedule": "monthly_static", "table": "t"}]
    lock = str(tmp_path / "lock")
    with open(lock, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))  # 自己的 PID ≠ guard 分支（pid==os.getpid 会直接放行）——用伪造活 PID
    # 写入一个真实存活的 PID（当前进程的父进程大概率存活；用 psutil 找一个活进程）
    import psutil

    live = next(p.pid for p in psutil.process_iter(["pid"]) if p.pid != os.getpid())
    with open(lock, "w", encoding="utf-8") as f:
        f.write(str(live))
    sched = FakeScheduler()
    r = _run(sched, monkeypatch, lock)
    assert r["success"] is False and r["rerun"] == {}


def test_alert_levels(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [{"task_id": "m1", "schedule": "monthly_static", "table": "t"}]
    monkeypatch.setattr(cg, "_table_is_empty", lambda table: False)
    sched = FakeScheduler(run_results={"m1": False})  # 补跑失败 → ERROR 级
    r = _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert r["rerun"] == {"m1": False}
    assert sched._alerter.calls[-1][1] == LEVEL_ERROR
    # 无 overdue → INFO 级
    sched2 = FakeScheduler(records={"m1": {"last_run_at": _iso(datetime.date(2026, 9, 2)), "last_status": "SUCCESS"}})
    monkeypatch.setattr("zephyr.data.calendar.get_market_calendar", lambda name="ashare": FakeCalendar(
        [TODAY - datetime.timedelta(days=d) for d in range(1, 9)] + [TODAY]))
    r2 = _run(sched2, monkeypatch, str(tmp_path / "lock2"))
    assert sched2._alerter.calls[-1][1] == LEVEL_INFO
    assert r2["success"] is True


def test_summary_saved(patched, monkeypatch, tmp_path):
    _cal, holder = patched
    holder["tasks"] = [{"task_id": "m1", "schedule": "monthly_static", "table": "t"}]
    monkeypatch.setattr(cg, "_table_is_empty", lambda table: False)
    sched = FakeScheduler()
    _run(sched, monkeypatch, str(tmp_path / "lock"))
    assert ("catchup_guard", "SUCCESS") in sched._progress_store.saved
