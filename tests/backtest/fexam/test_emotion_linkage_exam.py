# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | tests/backtest/fexam/test_emotion_linkage_exam.py | 情绪联动考单测（合成序列零CH零DB）
"""emotion_linkage_exam 单测：标签偏移正确性/月度桶 IC/窗统计/retain/三线判定/PIT 检查（tmp_path 注入）。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

FEXAM = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam"
if str(FEXAM) not in sys.path:
    sys.path.insert(0, str(FEXAM))

from emotion_linkage_exam import (  # noqa: E402
    ExamDataError,
    check_asof,
    check_key_uniqueness,
    check_ts_semantics,
    judge,
    monthly_ic,
    offset_labels,
    retain_stat,
    window_stats,
)


def _daily_index(n: int = 400, start: str = "2024-01-01") -> pd.DatetimeIndex:
    return pd.bdate_range(start, periods=n)


def test_offset_labels_zero_overlap_with_signal_day() -> None:
    """主标签必须是 t+1 起算：close 等差段逐点验。"""
    idx = _daily_index(10)
    close = pd.Series(np.arange(1, 11, dtype=float), index=idx)  # close(t)=t+1
    lab = offset_labels(close, h=5)
    # t=0: fwd5_off = close(5)/close(1)-1 = 6/2-1 = 2；旧口径 = close(5)/close(0)-1 = 6/1-1 = 5
    assert lab["fwd5_off"].iloc[0] == pytest.approx(2.0)
    assert lab["fwd5_old"].iloc[0] == pytest.approx(5.0)
    # leg5 = close(6)/close(1)-1 = 7/2-1 = 2.5
    assert lab["fwd5_leg5"].iloc[0] == pytest.approx(2.5)
    # 尾部越窗 NaN：t=5 起 t+5>9 → off NaN；t=9 全 NaN
    assert pd.isna(lab["fwd5_off"].iloc[5])
    assert pd.isna(lab["fwd5_off"].iloc[9])
    # ret_t 同期：t=3 → close(3)/close(2)-1 = 4/3-1
    assert lab["ret_t"].iloc[3] == pytest.approx(4 / 3 - 1)


def test_monthly_ic_perfect_and_na_buckets() -> None:
    """桶内单调关系→IC≈±1；有效对不足→NaN 桶。"""
    idx = _daily_index(60)  # 2024-01/02/03 三个月（23/21/16 个交易日）
    e = pd.Series(np.linspace(0, 1, 60), index=idx)
    lab = pd.Series(np.linspace(0, 1, 60), index=idx)  # 完全同调
    ic = monthly_ic(e, lab, min_pairs=10)
    assert len(ic) == 3
    assert ic.dropna().round(6).eq(1.0).all()
    # min_pairs 提到 30 → 每月 <30 对 → 全 NaN
    ic2 = monthly_ic(e, lab, min_pairs=30)
    assert ic2.isna().all()


def test_window_stats_min_buckets_guard() -> None:
    """月桶不足 → n/a（ic_mean=None），不产出伪读数。"""
    ic = pd.Series([0.1, 0.2, 0.3], index=pd.date_range("2025-01-31", periods=3, freq="ME"))
    st = window_stats(ic, min_buckets=6)
    assert st["na"] is True and st["ic_mean"] is None and st["n_buckets"] == 3
    ic6 = pd.Series([0.1] * 6, index=pd.date_range("2025-01-31", periods=6, freq="ME"))
    st6 = window_stats(ic6, min_buckets=6)
    assert st6["na"] is False and st6["ic_mean"] == pytest.approx(0.1) and st6["icir"] is None  # std=0


def test_retain_and_judge_three_lines() -> None:
    """三线 AND：全过/IC 不足/retain 不可判 三分支。"""
    assert retain_stat(0.04, 0.08) == pytest.approx(0.5)
    assert retain_stat(0.04, 0.0) is None
    ok, detail = judge(0.05, 0.5, 0.8)
    assert ok and "三线全过" in detail
    # IC 差线（|0.015|<0.02）
    ok2, detail2 = judge(0.015, 0.5, 0.8)
    assert not ok2 and "未全过" in detail2
    # 负 IC 两向判定：|-0.05|>0.02 过线（方向两可冻结口径）
    ok3, _ = judge(-0.05, -0.5, 0.8)
    assert ok3
    # retain 不可判
    ok4, detail4 = judge(0.05, 0.5, None)
    assert not ok4 and "不可判" in detail4


def test_pit_checks_on_synthetic_frames() -> None:
    """a ts 时点/b asof 越界/c 同键异值 三检在合成帧上各出正确违例数（含 tz-aware 表示）。"""
    df = pd.DataFrame(
        {
            "td": ["2026-01-05", "2026-01-06"],
            "stage": ["close_final"] * 2,
            "ts": [
                pd.Timestamp("2026-01-05 15:10:00+08:00"),
                pd.Timestamp("2026-01-07 09:00:00+08:00"),
            ],  # 行2: 时点错+日期错位（tz-aware 表示须剥尾缀判，冻结口径=wall time 15:10:00）
            "emotion_index": [0.5, 0.6],
            "components": [
                json.dumps([{"name": "C1", "asof": "2026-01-05"}]),
                json.dumps([{"name": "C1", "asof": "2026-01-07"}]),  # 越界
            ],
            "version": ["v0.1.0"] * 2,
        }
    )
    a = check_ts_semantics(df, "2026-01-01", "2026-01-31")
    assert a["n"] == 2 and a["ts_suffix_violations"] == 1 and a["ts_date_mismatch"] == 1
    b = check_asof(df, "2026-01-01", "2026-01-31")
    assert b["asof_future_violations"] == 1 and b["per_component"] == {"C1": 1}
    c = check_key_uniqueness(df)
    assert c["duplicate_keys"] == 0 and c["multi_value_keys"] == 0


def test_check_key_uniqueness_flags_multi_value() -> None:
    df = pd.DataFrame(
        {
            "td": ["2026-01-05", "2026-01-05"],
            "stage": ["close_final"] * 2,
            "ts": [pd.Timestamp("2026-01-05 15:10:00+08:00")] * 2,
            "emotion_index": [0.5, 0.7],
            "components": ["[]", "[]"],
            "version": ["v0.1.0"] * 2,
        }
    )
    c = check_key_uniqueness(df)
    assert c["duplicate_keys"] == 1 and c["multi_value_keys"] == 1


def test_load_signal_rejects_duplicate_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """FINAL 后同键多行 → ExamDataError（fail-closed）。"""
    import datetime as _dt

    import emotion_linkage_exam as ex

    rows = [
        (
            _dt.date(2026, 1, 5),
            "close_final",
            _dt.datetime(2026, 1, 5, 15, 10),
            0.5,
            "[]",
            "v0.1.0",
            _dt.datetime(2026, 1, 5, 15, 30),
        ),
        (
            _dt.date(2026, 1, 5),
            "close_final",
            _dt.datetime(2026, 1, 5, 15, 10),
            0.7,
            "[]",
            "v0.1.0",
            _dt.datetime(2026, 1, 6, 9, 0),
        ),
    ]
    monkeypatch.setattr(ex.ch_reader, "query_rows", lambda sql: rows)
    with pytest.raises(ExamDataError):
        ex.load_signal()
