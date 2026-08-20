# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# [ARCH-REF] #ARCH-REGIME-OVERLAY-001 #Phase2b
# [TTL] permanent
"""验证方案 A：overlay 仅在 #1<1.0（危机期）生效——与 RiskSignal #1 门控对齐。

基于 dump_overlay_triggers.py 的发现：overlay 退化 Sharpe 的元凶是 T1/S1 在非危机期
误触发（#1=1.0 时附加信号假阳性）。方案 A 在 detect() 入口门控：#1>=1.0 时把
overlay_signals 置空，平时不干预，危机期才允许 overlay 改概率分布。

对比三组 C1（实验组=开 Shrinkage）:
  baseline  : simple/off（Phase 1 简化版，纯 HMM）
  A3 ungated: simple/on（overlay 全程生效，已知 Sharpe -0.02 退化）
  方案 A    : simple/on + #1 门控（overlay 仅 #1<1.0 生效）

预期：方案 A ≈ baseline（不退化），保留危机期 overlay 价值。

Usage:
  python scripts/tests/validate_overlay_gated.py
"""

from __future__ import annotations

import logging
import warnings
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.backtest.regime_validation.c1_runner import run_c1_with_provider
from zephyr.backtest.regime_validation.shrinkage_provider import (
    ScheduleShrinkageProvider,
)
from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry
from zephyr.regime.core.regime_detector import RegimeDetector
from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder

BASKET_SYMBOLS = [
    "600000",
    "000001",
    "600519",
    "600036",
    "601318",
    "000651",
    "600276",
    "000858",
    "600887",
    "601166",
]
REAL_START = "2015-01-01"
REAL_END = "2026-06-30"
DATA_LOAD_START = "2010-01-01"
REPRO_DIR = Path(r"d:\ZephyrAlpha\logs\c1_repro")


def load_basket_hfq(symbols, start, end) -> pd.DataFrame:
    registry = get_registry()
    table = registry.table("market_kline_daily_hfq")
    syms_str = ", ".join([f"'{s}'" for s in symbols])
    sql = (
        f"SELECT trade_date, symbol, open, high, low, close, volume "
        f"FROM {table} FINAL WHERE symbol IN ({syms_str}) "
        f"AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
        f"ORDER BY symbol, trade_date"
    )
    tsv = ch_reader.query(sql)
    rows = [l.split("\t") for l in tsv.strip().split("\n") if l.strip() and len(l.split("\t")) >= 7]
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", "open", "high", "low", "close", "volume"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.rename(columns={"trade_date": "date"}).set_index(["symbol", "date"]).sort_index()
    return df


def make_signals(data: pd.DataFrame) -> pd.DataFrame:
    dates = data.index.get_level_values("date").unique().sort_values()
    return pd.DataFrame(
        {s: 1.0 for s in BASKET_SYMBOLS},
        index=pd.DatetimeIndex(dates, name="date"),
    )


def build_gated_schedule() -> dict:
    """跑 walk-forward（overlay on + #1 门控），返回 gated Shrinkage schedule。

    门控实现：monkey-patch detector.detect，在调用前检查 risk_signal_inputs.params[1]：
      - #1 >= 1.0（非危机）→ overlay_signals 置空（不干预）
      - #1 <  1.0（危机期）→ overlay_signals 原样传入（保留危机期 overlay 价值）
    """
    warnings.filterwarnings("ignore", message=".*not converging.*")
    logging.getLogger("hmmlearn").setLevel(logging.ERROR)

    print("[gated] 构建 RegimeFeatureBuilder（enable_overlay=True, risk=simple）...")
    builder = RegimeFeatureBuilder(
        backtest_start=REAL_START,
        backtest_end=REAL_END,
        data_load_start=DATA_LOAD_START,
        enable_full_risk=False,
        enable_overlay=True,
    )
    detector = RegimeDetector(shrinkage_enabled=True)

    # ── #1 门控 monkey-patch ──
    orig_detect = detector.detect

    def gated_detect(regime_features, overlay_signals, risk_signal_inputs):
        params = (risk_signal_inputs or {}).get("params") or {}
        primary = float(params.get(1, 1.0))
        if primary >= 1.0:
            # 非危机期：overlay 不干预（与 RiskSignal #1 门控对齐）
            overlay_signals = {}
        return orig_detect(regime_features, overlay_signals, risk_signal_inputs)

    detector.detect = gated_detect

    print("[gated] 跑 walk-forward（#1 门控 overlay，预计 2-3 分钟）...")
    schedule = builder.build_shrinkage_schedule(detector, train_years=5, detect_window=60)
    vals = np.array(list(schedule.values()))
    print(f"[gated] schedule: {len(schedule)} 日, 均值={vals.mean():.3f}, <1.0占比={100 * (vals < 1.0).mean():.1f}%")
    return schedule


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    print("[gated] 加载篮子后复权日K...")
    data = load_basket_hfq(BASKET_SYMBOLS, REAL_START, REAL_END)
    signals = make_signals(data)
    print(f"[gated] 篮子: {len(data)} 行, {signals.shape[1]} 标的")

    # 方案 A：#1 门控 overlay schedule
    gated_schedule = build_gated_schedule()
    # 持久化（派生产物不入 git）
    pd.DataFrame([{"date": d.strftime("%Y-%m-%d"), "shrinkage": v} for d, v in gated_schedule.items()]).to_csv(
        REPRO_DIR / "shrinkage_schedule_gated.csv", index=False
    )

    cfg = BacktestConfig(
        initial_capital=Decimal("1000000"),
        commission_rate=Decimal("0.0003"),
        slippage_bps=Decimal("1"),
        risk_free_rate=0.02,
    )

    print("\n[gated] 跑 C1（方案 A: #1 门控 overlay）...")
    r_gated = run_c1_with_provider(
        data,
        signals,
        ScheduleShrinkageProvider(gated_schedule),
        backtest_config=cfg,
        strategy_name="c1-real-gated-overlay",
        initial_capital=Decimal("1000000"),
    )

    # ── 三组对比 ──
    # baseline / A3 ungated 数据来自 a2_a3_validation_report.md（已验证）
    gv = {v.name: v.experiment_value for v in r_gated.metric_verdicts}
    print("\n" + "=" * 80)
    print("三组 C1 对比（实验组=开 Shrinkage）")
    print("=" * 80)
    print(f"{'配置':<24} {'Sharpe':<10} {'MaxDD':<10} {'Calmar':<10} {'Turnover':<10} {'C1'}")
    print("-" * 80)
    print(f"{'baseline simple/off':<24} {0.3474:<10.4f} {0.1485:<10.4f} {0.3694:<10.4f} {2.5522:<10.4f} {'✅'}")
    print(f"{'A3 simple/on (ungated)':<24} {0.3278:<10.4f} {0.1471:<10.4f} {0.3546:<10.4f} {2.5049:<10.4f} {'✅'}")
    print(
        f"{'方案A gated (#1<1.0)':<24} {gv.get('Sharpe', 0):<10.4f} {gv.get('MaxDD', 0):<10.4f} "
        f"{gv.get('Calmar', 0):<10.4f} {gv.get('Turnover', 0):<10.4f} {'✅' if r_gated.passed else '❌'}"
    )
    print("-" * 80)
    # 退化判定
    sharpe_gated = gv.get("Sharpe", 0)
    calmar_gated = gv.get("Calmar", 0)
    print("\n退化判定（方案A vs baseline）:")
    print(
        f"  Sharpe  差 {sharpe_gated - 0.3474:+.4f}  ({'噪声范围✅' if abs(sharpe_gated - 0.3474) < 0.005 else '退化⚠️' if sharpe_gated < 0.3474 else '改善'})"
    )
    print(
        f"  Calmar  差 {calmar_gated - 0.3694:+.4f}  ({'噪声范围✅' if abs(calmar_gated - 0.3694) < 0.005 else '退化⚠️' if calmar_gated < 0.3694 else '改善'})"
    )
    print(f"\n方案A passed={r_gated.passed}")
    print("\n方案 A 详细 verdicts:")
    for v in r_gated.metric_verdicts:
        print(f"  [{v.name}] {v.detail}")
    print("=" * 80)


if __name__ == "__main__":
    main()
