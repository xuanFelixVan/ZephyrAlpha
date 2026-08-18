#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""临时冒烟：RegimeFeatureBuilder.build_features() + build_train_matrix()。用完即删。"""
import time

import numpy as np

from zephyr.regime.regime_feature_builder import FEATURE_NAMES, RegimeFeatureBuilder

t0 = time.time()
builder = RegimeFeatureBuilder(
    backtest_start="2015-01-01", backtest_end="2026-06-30", data_load_start="2010-01-01"
)
print(f"[init] {time.time()-t0:.1f}s")

t0 = time.time()
features = builder.build_features()
print(f"[build_features] {time.time()-t0:.1f}s")
print(f"shape={features.shape}, cols={list(features.columns)}")
print(f"区间: {features.index.min()} ~ {features.index.max()}")
print(f"NaN 行数: {features.isna().any(axis=1).sum()} / {len(features)}")
print("\n各特征统计（dropna后）:")
for c in FEATURE_NAMES:
    s = features[c].dropna()
    print(f"  {c:20s} n={len(s):4d} min={s.min():.3f} max={s.max():.3f} mean={s.mean():.3f}")

# 2015 股灾区间特征抽样
print("\n2015 股灾区间（8-9月）特征抽样:")
sub = features.loc["2015-08-01":"2015-09-30", ["realized_vol_pct", "hurst_dfa", "volume_anomaly"]].dropna()
print(sub.head(10).to_string())

t0 = time.time()
train = builder.build_train_matrix("2010-01-01", "2014-12-31")
print(f"\n[build_train_matrix 2010-2014] {time.time()-t0:.1f}s")
print(f"X shape={train['X'].shape}, finite={np.isfinite(train['X']).all()}")

train2 = builder.build_train_matrix("2020-01-01", "2020-12-31")
print(f"[build_train_matrix 2020] X shape={train2['X'].shape}")
