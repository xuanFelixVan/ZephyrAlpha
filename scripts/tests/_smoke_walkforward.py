#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""临时冒烟：walk-forward 小范围(2020-2021)验证。用完即删。"""
import time

import numpy as np

from zephyr.regime.core.regime_detector import RegimeDetector
from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder

builder = RegimeFeatureBuilder(
    backtest_start="2020-01-01", backtest_end="2021-12-31", data_load_start="2010-01-01"
)
detector = RegimeDetector(shrinkage_enabled=True)

t0 = time.time()
schedule = builder.build_shrinkage_schedule(detector, train_years=5, detect_window=60)
print(f"\n[walk-forward 2020-2021] {time.time()-t0:.1f}s, {len(schedule)} 日")

vals = np.array(list(schedule.values()))
print(f"Shrinkage: min={vals.min():.3f} max={vals.max():.3f} mean={vals.mean():.3f}")
print(f"<1.0 占比: {100*(vals<1.0).mean():.1f}%")
print(f"分布: 1.0={100*(vals==1.0).mean():.1f}% [0.8,1)={100*((vals>=0.8)&(vals<1.0)).mean():.1f}% [0.6,0.8)={100*((vals>=0.6)&(vals<0.8)).mean():.1f}% <0.6={100*(vals<0.6).mean():.1f}%")

# 2020 新冠崩盘期(3月)抽样
print("\n2020 新冠崩盘期(3月) Shrinkage 抽样:")
for dt, v in sorted(schedule.items()):
    if "2020-03-01" <= dt.strftime("%Y-%m-%d") <= "2020-03-31":
        print(f"  {dt.strftime('%Y-%m-%d')}  shrinkage={v:.3f}")
