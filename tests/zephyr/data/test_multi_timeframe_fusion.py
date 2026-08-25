# [BLUEPRINT] MOD-DAT-MTF-FUSION | tests/zephyr/data/test_multi_timeframe_fusion.py
# [MODULE] tests.zephyr.data.test_multi_timeframe_fusion
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.multi_timeframe_fusion
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT-MTF-FUSION | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MultiTimeframeFusion 单元测试——多周期数据融合（CAND-DAT-016 / B13-04249 / D-DATA-25）。

覆盖：
    1. 频率校验：未知频率/缺必需列/粒度倒挂 → ValueError fail-closed
    2. OHLC 聚合正确性（open 首/high max/low min/close 尾/volume sum）
    3. 时间戳归一 bar close 口径（右闭右标）
    4. 交易日历对齐：日历外目标桶剔除
    5. ffill 上限 ≤3 根，超限留 NaN 并计入质量
    6. 质量评分：coverage_ratio/alignment_error/quality_flag 分级
"""

from __future__ import annotations

import datetime

import pandas as pd
import pytest

from zephyr.data.multi_timeframe_fusion import (
    FusionConfig,
    MultiTimeframeFusion,
    SUPPORTED_FREQS,
)

TS = pd.Timestamp


def _bars_1min(day: str = "2026-08-03", n: int = 30, start: str = "09:30") -> pd.DataFrame:
    base = pd.Timestamp(f"{day} {start}")
    rows = []
    price = 100.0
    for i in range(n):
        ts = base + pd.Timedelta(minutes=i)
        rows.append(
            {
                "timestamp": ts,
                "open": price,
                "high": price + 1,
                "low": price - 1,
                "close": price + 0.5,
                "volume": 1000 + i,
            }
        )
        price += 0.5
    return pd.DataFrame(rows)


# ── 1. 频率校验 ──


def test_supported_freqs_cover_1min_to_1d():
    for f in ("1min", "5min", "15min", "30min", "60min", "1d"):
        assert f in SUPPORTED_FREQS


def test_unknown_freq_fail_closed():
    fz = MultiTimeframeFusion()
    with pytest.raises(ValueError):
        fz.resample(_bars_1min(), "3min", "15min")
    with pytest.raises(ValueError):
        fz.resample(_bars_1min(), "1min", "3min")


def test_missing_columns_fail_closed():
    fz = MultiTimeframeFusion()
    bad = pd.DataFrame({"timestamp": [TS("2026-08-03 09:30")], "close": [1.0]})
    with pytest.raises(ValueError):
        fz.resample(bad, "1min", "5min")


def test_granularity_inversion_fail_closed():
    fz = MultiTimeframeFusion()
    with pytest.raises(ValueError):
        fz.resample(_bars_1min(), "15min", "5min")


# ── 2. OHLC 聚合正确性 ──


def test_ohlcv_aggregation_correct():
    fz = MultiTimeframeFusion()
    df = _bars_1min(n=30)  # 30 根 1min → 6 根 5min
    out = fz.resample(df, "1min", "5min")
    res = out.data
    assert len(res) == 6
    first5 = df.iloc[:5]
    row0 = res.iloc[0]
    assert row0["open"] == first5.iloc[0]["open"]
    assert row0["high"] == first5["high"].max()
    assert row0["low"] == first5["low"].min()
    assert row0["close"] == first5.iloc[-1]["close"]
    assert row0["volume"] == first5["volume"].sum()


# ── 3. 时间戳归一（bar close）──


def test_timestamp_normalized_to_bar_close():
    fz = MultiTimeframeFusion()
    out = fz.resample(_bars_1min(n=10), "1min", "5min")
    # bar close 口径：第一桶 09:30-09:34 → 归一 09:35
    assert out.data.iloc[0]["timestamp"] == TS("2026-08-03 09:35")
    assert out.data.iloc[1]["timestamp"] == TS("2026-08-03 09:40")


# ── 4. 交易日历对齐 ──


def test_trading_calendar_alignment_drops_outside_days():
    fz = MultiTimeframeFusion()
    d1 = _bars_1min(day="2026-08-03", n=10)
    d2 = _bars_1min(day="2026-08-04", n=10)
    df = pd.concat([d1, d2], ignore_index=True)
    out = fz.resample(df, "1min", "5min", trading_days=[datetime.date(2026, 8, 3)])
    days = {t.date() for t in out.data["timestamp"]}
    assert days == {datetime.date(2026, 8, 3)}


# ── 5. ffill 上限 ──


def test_ffill_within_limit_and_beyond_left_nan():
    fz = MultiTimeframeFusion(config=FusionConfig(ffill_limit=3, good_coverage=1.1, degraded_coverage=1.05))
    # 09:30-09:34 有数据（桶0），09:35-09:54 缺口（桶1-4），09:55-09:59 有数据（桶5）
    part1 = _bars_1min(n=5, start="09:30")
    part2 = _bars_1min(n=5, start="09:55")
    df = pd.concat([part1, part2], ignore_index=True)
    out = fz.resample(df, "1min", "5min", expected_start=TS("2026-08-03 09:30"), expected_end=TS("2026-08-03 10:00"))
    closes = list(out.data["close"])
    # 缺口 4 桶：前 3 桶 ffill，第 4 桶 NaN
    assert closes[1] == closes[0]
    assert closes[2] == closes[0]
    assert closes[3] == closes[0]
    assert pd.isna(closes[4])
    assert out.quality.ffill_used == 3


# ── 6. 质量评分 ──


def test_quality_flag_good_on_full_coverage():
    fz = MultiTimeframeFusion()
    out = fz.resample(_bars_1min(n=30), "1min", "5min")
    q = out.quality
    assert q.expected_bars == 6 and q.actual_bars == 6
    assert q.coverage_ratio == pytest.approx(1.0)
    assert q.alignment_error_count == 0
    assert q.quality_flag == "good"


def test_quality_flag_degrades_on_low_coverage():
    cfg = FusionConfig(ffill_limit=0, good_coverage=0.95, degraded_coverage=0.80)
    fz = MultiTimeframeFusion(config=cfg)
    part1 = _bars_1min(n=5, start="09:30")
    part2 = _bars_1min(n=5, start="09:55")
    df = pd.concat([part1, part2], ignore_index=True)
    out = fz.resample(df, "1min", "5min", expected_start=TS("2026-08-03 09:30"), expected_end=TS("2026-08-03 10:00"))
    # 6 应到桶仅 2 桶有效 → coverage 0.33 → poor
    assert out.quality.coverage_ratio == pytest.approx(2 / 6, abs=0.01)
    assert out.quality.quality_flag == "poor"


def test_alignment_error_counted_for_off_boundary_bars():
    fz = MultiTimeframeFusion()
    df = _bars_1min(n=6)
    df.loc[0, "timestamp"] = TS("2026-08-03 09:30:30")  # 30 秒偏移，不落地 5min 边界
    out = fz.resample(df, "1min", "5min")
    assert out.quality.alignment_error_count == 1
