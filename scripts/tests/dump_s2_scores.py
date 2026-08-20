# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] task_bound
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# [ARCH-REF] #Phase2b #S2-recovery-diagnosis
"""S2 复苏检测诊断：dump 3 个历史复苏事件日（±10 天）的 S2 各维度评分 vs 阈值。

定位 S2 0/3 不触发的根因：是分数达不到阈值，还是维度缺失。
仅复用 OverlaySignalsConstructor（规则计算，无需 HMM walk-forward），秒级出结果。

Usage:
  python scripts/tests/dump_s2_scores.py
"""

from __future__ import annotations

import logging
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("zephyr.regime.overlay_signals_builder").setLevel(logging.INFO)

from zephyr.regime.features.regime_data_loader import RegimeDataLoader
from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder

# S2 阈值（与 regime_detector.TRANSITION_CONFIG["S2"] 对齐）
S2_THRESHOLDS = {
    "trigger": {"capitulation": 60, "vix": 40, "bad_news_flat": 40},
    "confirm": {"wyckoff": 60, "policy": 40, "valuation": 40, "fund": 50},
    "strong_confirm": {"spring": 1, "three_yang": 1},  # flag 类（≥1）
}

EVENT_DATES = [
    ("EVT-2015-RECOVERY", "2015-09-15"),
    ("EVT-2020-RECOVERY", "2020-04-10"),
    ("EVT-2024-RECOVERY", "2024-09-24"),
]
WINDOW = 10  # ±10 交易日


def main() -> int:
    print("[s2-diag] 构建 RegimeFeatureBuilder + OverlaySignalsConstructor...")
    data_loader = RegimeDataLoader(data_load_start="2010-01-01", backtest_end="2026-06-30")
    builder = RegimeFeatureBuilder(
        backtest_start="2015-01-01",
        backtest_end="2026-06-30",
        data_load_start="2010-01-01",
        enable_full_risk=True,
        enable_overlay=True,
        enable_phase2c=True,
        data_loader=data_loader,
    )
    # 触发特征构建 + overlay 构造器惰性初始化
    _ = builder.build_features()
    # 复刻 Phase2Runner._ensure_constructors
    from zephyr.regime.overlay_signals_builder import OverlaySignalsConstructor
    from zephyr.regime.risk_signal_builder import RiskSignalConstructor

    if builder._risk_ctor is None:
        builder._risk_ctor = RiskSignalConstructor(
            backtest_start=builder.backtest_start,
            backtest_end=builder.backtest_end,
            data_load_start=builder.data_load_start,
            feature_builder=builder,
            market_proxy=builder.market_proxy,
        )
    if builder._overlay_ctor is None:
        builder._overlay_ctor = OverlaySignalsConstructor(
            backtest_start=builder.backtest_start,
            backtest_end=builder.backtest_end,
            data_load_start=builder.data_load_start,
            feature_builder=builder,
            risk_constructor=builder._risk_ctor,
            market_proxy=builder.market_proxy,
        )
    print("[s2-diag] OverlaySignalsConstructor 就绪\n")

    all_dims = [
        "capitulation",
        "vix",
        "bad_news_flat",
        "wyckoff",
        "policy",
        "valuation",
        "fund",
        "spring",
        "three_yang",
    ]

    for eid, edate_str in EVENT_DATES:
        edate = pd.Timestamp(edate_str)
        print("=" * 90)
        print(f"{eid}  事件日={edate_str}  (±{WINDOW} 交易日)")
        print("=" * 90)
        # 取事件日 ±WINDOW 交易日
        idx = builder.build_features().index
        loc = idx.get_indexer([edate], method="nearest")[0]
        start = max(0, loc - WINDOW)
        end = min(len(idx) - 1, loc + WINDOW)
        window_dates = idx[start : end + 1]

        header = f"{'date':<12} " + " ".join(f"{d:>13}" for d in all_dims) + "  stage"
        print(header)
        print("-" * len(header))
        best_stage = "none"
        best_date = None
        for dt in window_dates:
            sig = builder._overlay_ctor.build_for_date(dt)
            trans = (sig or {}).get("transitions", {})
            s2 = trans.get("S2", {})
            vals = {d: s2.get(d, float("nan")) for d in all_dims}
            # 判定 stage（复刻 record_transition 逻辑）
            stage = _eval_stage(vals)
            row = f"{dt.strftime('%Y-%m-%d'):<12} "
            row += " ".join(f"{_fmt(vals[d]):>13}" for d in all_dims)
            row += f"  {stage}"
            print(row)
            if stage != "none" and best_stage == "none":
                best_stage = stage
                best_date = dt
        print()
        _print_threshold_gap(vals, all_dims)  # 最后一天的差距
        if best_stage != "none":
            print(f"  → 窗口内最高 stage: {best_stage} @ {best_date.date()}")
        else:
            print("  → 窗口内无任何 S2 stage 触发")
        print()

    return 0


def _eval_stage(vals: dict[str, float]) -> str:
    """复刻 record_transition 的 stage 判定（strong_confirm > confirm > trigger > fail > none）。"""
    total = sum(v for v in vals.values() if isinstance(v, (int, float)) and v == v)
    # strong_confirm: total≥250 且 spring≥1 且 three_yang≥1
    if total >= 250 and _ge(vals, "spring", 1) and _ge(vals, "three_yang", 1):
        return "strong_confirm"
    # confirm: wyckoff≥60 ∧ policy≥40 ∧ valuation≥40 ∧ fund≥50
    if _ge(vals, "wyckoff", 60) and _ge(vals, "policy", 40) and _ge(vals, "valuation", 40) and _ge(vals, "fund", 50):
        return "confirm"
    # trigger: capitulation≥60 ∧ vix≥40 ∧ bad_news_flat≥40
    if _ge(vals, "capitulation", 60) and _ge(vals, "vix", 40) and _ge(vals, "bad_news_flat", 40):
        return "trigger"
    return "none"


def _ge(vals: dict[str, float], key: str, thr: float) -> bool:
    v = vals.get(key, float("nan"))
    return isinstance(v, (int, float)) and v == v and v >= thr


def _fmt(v) -> str:
    if isinstance(v, float) and v != v:
        return "—"
    return f"{v:.1f}"


def _print_threshold_gap(vals: dict[str, float], all_dims: list[str]) -> None:
    """打印最后一天的各维度 vs 触发阈值差距。"""
    print("  阈值差距分析（最后一日）:")
    for stage, thrs in S2_THRESHOLDS.items():
        parts = []
        for k, thr in thrs.items():
            v = vals.get(k, float("nan"))
            if isinstance(v, float) and v != v:
                parts.append(f"{k}=缺失(需≥{thr})")
            else:
                mark = "✓" if v >= thr else "✗"
                parts.append(f"{k}={v:.1f}{mark}(需≥{thr})")
        print(f"    {stage}: " + ", ".join(parts))


if __name__ == "__main__":
    sys.exit(main())
