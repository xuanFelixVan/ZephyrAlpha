"""Turnover 抖动分析——排查 Shrinkage 序列波动对换手率的影响。

C1 复现发现：基准组 1444 笔，实验组 2432 笔（+68%），但 Turnover/yr 只升 12%。
根因假设：Shrinkage 序列波动导致权重频繁微调。本脚本分析抖动分布 + 模拟死区效果。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CSV = Path(r"d:\ZephyrAlpha\logs\c1_repro\shrinkage_schedule.csv")


def main() -> None:
    df = pd.read_csv(CSV, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    df["delta"] = df["shrinkage"].diff().abs()

    print("=" * 70)
    print("Shrinkage 序列抖动分析（排查 Turnover 升高根因）")
    print("=" * 70)
    print(f"总日数:            {len(df)}")
    print(f"Shrinkage 均值:    {df['shrinkage'].mean():.4f}")
    print(f"Shrinkage std:     {df['shrinkage'].std():.4f}")
    print(f"Shrinkage min/max: {df['shrinkage'].min():.4f} / {df['shrinkage'].max():.4f}")
    print(f"<1.0 占比:         {(df['shrinkage'] < 1.0).mean() * 100:.1f}%")
    print()
    print("── 日变化 |Δshrinkage| 分布 ──")
    print(f"日均 |Δ|:          {df['delta'].mean():.4f}")
    print(f"|Δ| > 0.01 天数:   {(df['delta'] > 0.01).sum()} ({(df['delta'] > 0.01).mean() * 100:.1f}%)")
    print(f"|Δ| > 0.05 天数:   {(df['delta'] > 0.05).sum()} ({(df['delta'] > 0.05).mean() * 100:.1f}%)")
    print(f"|Δ| > 0.10 天数:   {(df['delta'] > 0.10).sum()} ({(df['delta'] > 0.10).mean() * 100:.1f}%)")
    print(f"|Δ| > 0.20 天数:   {(df['delta'] > 0.20).sum()} ({(df['delta'] > 0.20).mean() * 100:.1f}%)")
    print()

    # EMA 平滑已有（α=0.15），分析残留抖动
    # 模拟死区：|Δ| < threshold 不调仓（保持上次实际生效值）
    print("── 死区模拟（|Δ| < threshold 不调仓 → 减少无效调仓）──")
    base_changes = (df["delta"] > 1e-9).sum()
    print(f"原始调仓天数（Δ≠0）: {base_changes}")
    for thresh in [0.02, 0.05, 0.10, 0.15]:
        last = df["shrinkage"].iloc[0]
        n_rebalance = 0
        for i in range(1, len(df)):
            cur = df["shrinkage"].iloc[i]
            if abs(cur - last) >= thresh:
                last = cur
                n_rebalance += 1
        reduction = (1 - n_rebalance / base_changes) * 100 if base_changes else 0
        print(f"  死区 {thresh:.2f}: 调仓 {n_rebalance} 次（减少 {reduction:.0f}%）")

    # 连续变化段分析（Shrinkage 在危机期 vs 平稳期的抖动对比）
    print()
    print("── 危机期 vs 平稳期抖动对比 ──")
    crisis = df[df["shrinkage"] < 0.7]
    calm = df[df["shrinkage"] >= 0.9]
    print(f"危机期（shrinkage<0.7）: {len(crisis)} 日, 日均|Δ|={crisis['delta'].mean():.4f}")
    print(f"平稳期（shrinkage≥0.9）: {len(calm)} 日, 日均|Δ|={calm['delta'].mean():.4f}")
    if len(crisis) > 0 and len(calm) > 0:
        ratio = crisis["delta"].mean() / max(calm["delta"].mean(), 1e-9)
        print(f"危机期抖动是平稳期的 {ratio:.1f} 倍")
    print("=" * 70)


if __name__ == "__main__":
    main()
