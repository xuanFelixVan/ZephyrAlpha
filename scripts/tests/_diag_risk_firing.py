# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""诊断：各 risk 参数在 2015-2026 的触发率（%<1.0）和均值，定位过度收缩元凶。"""

import warnings

warnings.filterwarnings("ignore")
import logging

logging.getLogger("hmmlearn").setLevel(logging.ERROR)

import numpy as np
import pandas as pd

from zephyr.regime.features import risk_features as rf
from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder

builder = RegimeFeatureBuilder(
    backtest_start="2015-01-01",
    backtest_end="2026-06-30",
    data_load_start="2010-01-01",
)
features = builder.build_features()
index_df = builder.get_index_kline()
proxy = index_df.xs("000300", level="symbol")
pc = proxy["close"].astype(float).reindex(features.index)
pct = pc.pct_change()

# 限定回测区间
feat = features.loc["2015-01-01":"2026-06-30"]
pc = pc.loc["2015-01-01":"2026-06-30"]
pct = pct.loc["2015-01-01":"2026-06-30"]

# 注：index_kline 无 high/low，#9 KDJ 在真实 Phase 2a 降级为 1.0，故诊断跳过 #9
params = {
    1: ("realized_vol", rf.realized_vol_coef(feat["realized_vol_pct"], feat["kalman_slope"])),
    2: ("volume_anomaly", rf.volume_anomaly_coef(feat["volume_anomaly"], pct)),
    3: ("price_pattern", rf.price_pattern_coef(pc)),
    5: ("space_position", rf.space_position_coef(pc)),
    6: ("cross_asset_corr", rf.cross_asset_corr_coef(feat["cross_asset_corr"])),
    7: ("ad_ratio_extreme", rf.ad_ratio_extreme_coef(feat["ad_ratio"])),
    10: ("trend_slope_decay", rf.trend_slope_decay_coef(feat["kalman_slope"], feat["hurst_dfa"])),
}

print(f"{'#':>3} {'param':<20} {'mean':>6} {'%<1.0':>7} {'%<0.85':>8} {'%<=0.6':>8}")
print("-" * 60)
for pid, (name, s) in params.items():
    s = s.dropna()
    print(
        f"{pid:>3} {name:<20} {s.mean():>6.3f} {100 * (s < 1.0).mean():>6.1f}% "
        f"{100 * (s < 0.85).mean():>7.1f}% {100 * (s <= 0.6).mean():>7.1f}%"
    )

# min 聚合模拟
allc = pd.DataFrame({pid: s for pid, (_, s) in params.items()})
risk_base = allc.min(axis=1).dropna()
anom = (allc < 1.0).sum(axis=1).loc[risk_base.index]
resonance = np.maximum(0.80, 1.0 - 0.05 * np.maximum(0, anom - 1))
risk_signal = np.clip(risk_base * resonance, 0.30, 1.00)
print("-" * 60)
print(f"risk_base (min)  mean={risk_base.mean():.3f}  %<1.0={100 * (risk_base < 1.0).mean():.1f}%")
print(f"RiskSignal       mean={risk_signal.mean():.3f}  %<1.0={100 * (risk_signal < 1.0).mean():.1f}%")
print(f"anomaly_count    mean={anom.mean():.2f}")
