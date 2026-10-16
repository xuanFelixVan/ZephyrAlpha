# [MODULE] tests.zephyr.data.test_tick_subscriber_biz_ts
# [DOMAIN] D_DATA
# [A_module] module_id=test-tick-subscriber-biz-ts | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""TickSubscriber._note_biz_ts 单测（#ZOMBIE-REPLAY 判活口径，2026-10-14）。

背景（实测事故）：桥文件 E:\\qmt_bridge_sim\\ticks3.csv 自 2026-10-12 11:29 冻结，
进程重启后反复重放这 359,176 行（timetag 全为 10-12），盖上今日 ingest_ts。
业务心跳当时显示 last_tick_ts=今日 16:40:44、today_rows=139,599、errors=0 → 全绿。
根因：判活用的是**墙钟接收时刻**与**写入行数**，两者都无法区分"新数据"与"重放的旧数据"。

本件只验证业务时间戳追踪这一最小判据面（不构造完整 TickSubscriber，避免拉起
QMT/CH/线程池依赖）：
1. 今日业务时间戳 → rows_biz_today 累加、last_biz_dt 推进
2. 陈旧业务时间戳（僵尸回放形态） → rows_biz_today 恒 0、last_biz_dt 停在旧日期
3. 乱序到达：旧时间戳不回退 last_biz_dt
4. 缺 time 字段 / 非法值 → 静默跳过，不抛
"""

from __future__ import annotations

import datetime
import time

import zephyr.data.tick_subscriber as ts_mod
from zephyr.data.tick_subscriber import TickSubscriber

_NOW = datetime.datetime(2026, 10, 14, 21, 0, 0)


class _Stub:
    """只承载 _note_biz_ts 所需状态的最小宿主（避免构造完整 TickSubscriber）。"""

    _last_biz_dt: datetime.datetime | None = None
    _rows_biz_today = 0

    _note_biz_ts = TickSubscriber._note_biz_ts


def _ms(dt: datetime.datetime) -> int:
    return int(dt.timestamp() * 1000)


def _tick(dt: datetime.datetime) -> dict:
    return {"time": _ms(dt), "lastPrice": 10.0}


def test_fresh_business_timestamp_counts_today(monkeypatch):
    """今日业务时间戳 → rows_biz_today 累加。

    _biz_today 显式 patch：测试与运行日期解耦（原版写死 2026-10-14 依赖"当天跑"，是时间炸弹）。
    """
    monkeypatch.setattr(ts_mod, "_biz_today", lambda: _NOW.date())
    s = _Stub()
    s._note_biz_ts(_tick(_NOW))
    assert s._last_biz_dt == _NOW.replace(microsecond=0)
    assert s._rows_biz_today == 1


def test_stale_replay_never_counts_today(monkeypatch):
    """僵尸回放形态：10-12 的陈旧 tick 被反复灌入，rows_biz_today 必须恒为 0。"""
    monkeypatch.setattr(ts_mod, "_biz_today", lambda: _NOW.date())  # 今天=10-14 ≠ 10-12
    s = _Stub()
    stale = datetime.datetime(2026, 10, 12, 11, 29, 56)
    for _ in range(1000):
        s._note_biz_ts(_tick(stale))
    assert s._last_biz_dt == stale
    assert s._rows_biz_today == 0, "陈旧业务时间戳被误判为今日数据（判活口径失效）"


def test_out_of_order_does_not_rewind():
    s = _Stub()
    s._note_biz_ts(_tick(_NOW))
    s._note_biz_ts(_tick(datetime.datetime(2026, 10, 12, 9, 19, 3)))
    assert s._last_biz_dt == _NOW.replace(microsecond=0), "乱序旧 tick 回退了最新业务时间戳"


def test_missing_or_invalid_time_is_ignored():
    s = _Stub()
    for bad in ({}, {"time": 0}, {"time": None}, {"time": "not-a-number"}):
        s._note_biz_ts(bad)
    assert s._last_biz_dt is None
    assert s._rows_biz_today == 0


def test_now_ms_timestamps_accepted():
    s = _Stub()
    s._note_biz_ts({"time": int(time.time() * 1000)})
    assert s._last_biz_dt is not None
    assert s._rows_biz_today == 1
