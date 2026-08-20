# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""分析死区优化为何未降低 Turnover。

假设: 等权策略 Turnover 主驱是「价格漂移再平衡」，而非 Shrinkage 变化。
死区只过滤 Shrinkage 变化点，对价格漂移无能为力，故 Turnover 不降。

验证:
  1. 原序列 vs 死区序列的 Shrinkage 变化点数（确认死区确实减少了变化点）
  2. |Δ| 分布对比
  3. 估算 Shrinkage 变化贡献的调仓量占比（若 << 价格漂移贡献，则死区无效）
"""

from __future__ import annotations

import logging
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from zephyr.backtest.regime_validation.shrinkage_provider import (
    DeadzoneShrinkageProvider,
    ScheduleShrinkageProvider,
)

REPRO_DIR = Path(r"d:\ZephyrAlpha\logs\c1_repro")


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    warnings.filterwarnings("ignore")

    df = pd.read_csv(REPRO_DIR / "shrinkage_schedule.csv", parse_dates=["date"])
    schedule = {d.to_pydatetime(): float(v) for d, v in zip(df["date"], df["shrinkage"])}
    dates = sorted(schedule.keys())
    print(f"[analyze] Shrinkage 序列: {len(dates)} 日, 均值={np.mean(list(schedule.values())):.4f}")

    # ── 1. 原序列 vs 死区序列 ──────────────────────────────────────
    raw_vals = [schedule[d] for d in dates]
    raw_deltas = [abs(raw_vals[i] - raw_vals[i - 1]) for i in range(1, len(raw_vals))]
    raw_change_points = sum(1 for d in raw_deltas if d > 1e-9)
    raw_significant = sum(1 for d in raw_deltas if d >= 0.02)

    dz = DeadzoneShrinkageProvider(ScheduleShrinkageProvider(schedule), deadzone=0.02)
    dz_vals = [dz.get_shrinkage(d) for d in dates]
    dz_deltas = [abs(dz_vals[i] - dz_vals[i - 1]) for i in range(1, len(dz_vals))]
    dz_change_points = sum(1 for d in dz_deltas if d > 1e-9)

    print("\n" + "=" * 70)
    print("1. Shrinkage 变化点对比")
    print("=" * 70)
    print(f"  原序列 变化点(Δ>0):       {raw_change_points} 天")
    print(f"  原序列 显著变化(Δ≥0.02):  {raw_significant} 天")
    print(f"  死区序列 变化点(Δ>0):     {dz_change_points} 天")
    if raw_change_points > 0:
        print(f"  死区减少变化点:           {(1 - dz_change_points / raw_change_points) * 100:.1f}%")
    print(f"  原序列 |Δ|<0.02 占比:     {sum(1 for d in raw_deltas if d < 0.02) / len(raw_deltas) * 100:.1f}%")

    print("\n  |Δ| 分位数 (原序列):")
    for q in [50, 75, 90, 95, 99]:
        print(f"    P{q}: {np.percentile(raw_deltas, q):.5f}")
    print(f"    均值 |Δ|: {np.mean(raw_deltas):.5f}  最大: {np.max(raw_deltas):.5f}")

    # ── 2. 调仓来源分解：Shrinkage 变化 vs 价格漂移 ────────────────
    # 等权策略: target_weight_i = 1/N (等权), 实际权重 w_i = (shares_i * price_i) / NAV
    # Shrinkage 缩放: deploy_weight_i = target_i * shrinkage / sum(target * shrinkage)
    # 当 shrinkage 变化 → deploy_weight 变 → 调仓
    # 当 price 变化 → w_i 漂移偏离 target → 再平衡调仓
    # 估算两者贡献:
    #   - shrinkage 变化导致的 deploy_weight 变化 (所有标的同向, 不改变相对权重)
    #   - 价格漂移导致的相对权重偏离 (改变各标的占比)
    print("\n" + "=" * 70)
    print("2. Turnover 来源分解（等权 + Shrinkage 缩放）")
    print("=" * 70)
    # 关键: shrinkage 对所有标的同向缩放 → deploy_weight_i = (1/N * s) / (1/N * s * N) = 1/N
    # 即 shrinkage 不改变等权策略的相对权重! 它只改变总仓位 (1-s 部分闲置)
    # 所以 shrinkage 变化 → 总仓位变 → 各标的同比例加减仓 (调仓量 = |Δs| * NAV / N_per_symbol)
    # 价格漂移 → 相对权重偏离 → 再平衡调仓
    print("  等权策略下 shrinkage 不改变相对权重（各标的同向缩放）:")
    print("  deploy_weight_i = (1/N × s) / (N × 1/N × s) = 1/N  ← 相对权重恒等")
    print("  shrinkage 只改变总仓位 (1-s 部分闲置现金)")
    print()
    # 估算 shrinkage 变化贡献的调仓量
    # 每日因 shrinkage 变化的调仓 = |Δs| × NAV × (部署比例) / N 标的 × 2(买卖双边)
    # 价格漂移贡献的调仓 ≈ 日均 Turnover - shrinkage 贡献
    avg_abs_delta_s = np.mean(raw_deltas)
    avg_s = np.mean(raw_vals)
    # shrinkage 贡献的单边调仓比例 = |Δs| × avg_s (部署部分需同步调)
    shrink_contrib = avg_abs_delta_s * avg_s  # 粗估单边
    print(f"  shrinkage 日均 |Δs|={avg_abs_delta_s:.5f}, 均值 s={avg_s:.4f}")
    print(f"  shrinkage 变化贡献的单边调仓比例(粗估): {shrink_contrib:.6f}/日")
    print(f"  实测 Turnover(无死区)=2.5522/yr → 日均 {2.5522 / 252:.6f}/日")
    print(f"  shrinkage 贡献占比 ≈ {shrink_contrib / (2.5522 / 252) * 100:.1f}%")
    print()
    print("  → 若 shrinkage 贡献占比很低，说明 Turnover 主驱是价格漂移，")
    print("    死区过滤 shrinkage 变化对 Turnover 影响有限。")

    # ── 3. 死区副作用：积压后大调 ──────────────────────────────────
    print("\n" + "=" * 70)
    print("3. 死区副作用——积压后单次大调")
    print("=" * 70)
    # 死区把多次小 Δ 合并成少次大 Δ，单次调仓幅度增大
    raw_total = sum(raw_deltas)
    dz_total = sum(dz_deltas)
    print(f"  原序列 Σ|Δs| = {raw_total:.4f}  (总变化量)")
    print(f"  死区序列 Σ|Δs| = {dz_total:.4f}  (总变化量)")
    print(f"  总变化量差异: {(dz_total - raw_total) / raw_total * 100:+.2f}%")
    print(f"  原序列 max|Δs| = {max(raw_deltas):.4f}")
    print(f"  死区序列 max|Δs| = {max(dz_deltas):.4f}  (积压释放 → 单次更大)")
    print()
    print("  → 死区不改变总变化量（只重排时点），把多次小调合并为少次大调，")
    print("    Turnover（按调仓量计）几乎不降，甚至因大调的滑点/摩擦略升。")


if __name__ == "__main__":
    main()
