# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""诊断 S2 recovery 触发：dump 事件日 ±7 交易日的 S2 score_breakdown + stage。

根因假设：
  - trigger  需 bad_news_flat>=40（NLP stub=0）→ 永不满足
  - confirm  需 policy>=40（NLP stub=0）→ 永不满足
  - strong_confirm 需 total>=250 且 spring>=1 且 three_yang>=1 → 唯一可能命中

本脚本验证 strong_confirm 在事件日附近是否触发，及卡在哪个条件。
"""

from __future__ import annotations

import bisect
import logging
import warnings

import pandas as pd

warnings.filterwarnings("ignore", message=".*not converging.*")
logging.getLogger("hmmlearn").setLevel(logging.ERROR)
logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

from zephyr.regime.core.regime_detector import RegimeDetector  # noqa: E402
from zephyr.regime.overlay_signals_builder import OverlaySignalsConstructor  # noqa: E402
from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder  # noqa: E402

builder = RegimeFeatureBuilder(
    backtest_start="2015-01-01",
    backtest_end="2026-06-30",
    data_load_start="2010-01-01",
    enable_full_risk=True,
    enable_overlay=True,
)
features = builder.build_features()
trading_dates = list(features.index)

if builder._overlay_ctor is None:  # noqa: SLF001
    builder._overlay_ctor = OverlaySignalsConstructor(  # noqa: SLF001
        backtest_start=builder.backtest_start,
        backtest_end=builder.backtest_end,
        data_load_start=builder.data_load_start,
        feature_builder=builder,
        risk_constructor=builder._risk_ctor,  # noqa: SLF001
        market_proxy=builder.market_proxy,
    )
overlay_ctor = builder._overlay_ctor  # noqa: SLF001
detector = RegimeDetector()

EVENTS = [
    ("EVT-2015-RECOVERY", pd.Timestamp("2015-09-15")),
    ("EVT-2020-RECOVERY", pd.Timestamp("2020-04-10")),
    ("EVT-2024-RECOVERY", pd.Timestamp("2024-09-24")),
]

S2_KEYS = [
    "capitulation",
    "vix",
    "wyckoff",
    "valuation",
    "fund",
    "spring",
    "three_yang",
    "break_sc_low",
    "vix_new_high",
    "fund_outflow",
    "policy",
    "bad_news_flat",
]

print("\nS2 strong_confirm 条件: total>=250 且 spring>=1 且 three_yang>=1")
print("S2 confirm 条件:        wyckoff>=60 且 policy>=40 且 valuation>=40 且 fund>=50")
print("S2 trigger 条件:        capitulation>=60 且 vix>=40 且 bad_news_flat>=40")

for eid, event_date in EVENTS:
    print(f"\n{'=' * 78}")
    print(f"{eid}  事件日={event_date.date()}")
    print(f"{'=' * 78}")
    idx = bisect.bisect_left(trading_dates, event_date)
    start = max(0, idx - 7)
    end = min(len(trading_dates), idx + 8)
    for dt in trading_dates[start:end]:
        dt_ts = pd.Timestamp(dt)
        overlay = overlay_ctor.build_for_date(dt_ts)
        s2 = overlay.get("transitions", {}).get("S2", {})
        trig = detector.record_transition("S2", s2)
        marker = " <<< 事件日" if dt_ts == event_date else ""
        flag = "✓" if trig.triggered else " "
        print(
            f"  {flag} {dt_ts.date()} stage={trig.stage:14s} total={trig.total_score:6.1f} "
            f"cap={s2.get('capitulation', 0):5.1f} vix={s2.get('vix', 0):5.1f} "
            f"wyck={s2.get('wyckoff', 0):5.1f} val={s2.get('valuation', 0):5.1f} "
            f"fund={s2.get('fund', 0):5.1f} spring={s2.get('spring', 0):.0f} "
            f"3yang={s2.get('three_yang', 0):.0f} "
            f"pol={s2.get('policy', 0):.0f} badn={s2.get('bad_news_flat', 0):.0f}"
            f"{marker}"
        )
