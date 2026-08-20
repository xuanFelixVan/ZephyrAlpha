# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""诊断 Shrinkage schedule 分布与危机时段表现。

目的：判断 C1 MaxDD 改善不足的根因
  - HMM 在危机时段是否给出了强收缩信号（raw<0.6）？
  - EMA 平滑是否稀释了危机收缩？
  - 节流力度是否过于温和（均值过高）？

输出：raw vs smoothed 的分位数分布 + 4 个危机时段切片。
"""

from __future__ import annotations

import logging
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

warnings.filterwarnings("ignore", message=".*not converging.*")
logging.getLogger("hmmlearn").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder  # noqa: E402

# 危机时段（A股历史急跌）
CRISIS_PERIODS = [
    ("2015股灾Q3", "2015-06-15", "2015-09-15"),
    ("2018熊市Q4", "2018-10-01", "2018-12-31"),
    ("2020疫情Q1", "2020-02-01", "2020-04-30"),
    ("2024回调Q1", "2024-01-01", "2024-02-29"),
    ("2025 Q1", "2025-01-01", "2025-04-30"),
]


def describe(name: str, vals: np.ndarray) -> None:
    if len(vals) == 0:
        print(f"  {name}: 空")
        return
    qs = np.quantile(vals, [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
    print(
        f"  {name}: n={len(vals)} 均值={vals.mean():.3f} "
        f"min={vals.min():.3f} p1={qs[0]:.3f} p5={qs[1]:.3f} "
        f"p25={qs[2]:.3f} p50={qs[3]:.3f} p75={qs[4]:.3f} "
        f"p95={qs[5]:.3f} p99={qs[6]:.3f} max={vals.max():.3f}"
    )
    print(
        f"    <0.6占比={100 * (vals < 0.6).mean():.1f}%  "
        f"<0.85占比={100 * (vals < 0.85).mean():.1f}%  "
        f"==1.0占比={100 * (vals >= 0.999).mean():.1f}%"
    )


def main() -> None:
    print("=" * 72)
    print("Shrinkage 分布诊断（raw vs EMA smoothed）")
    print("=" * 72)

    # 只跑一次 walk-forward 拿 raw（禁用 EMA），smoothed 在脚本内手动算
    print("\n[1/1] 构建 raw schedule（ema_alpha=None，walk-forward 一次）...")
    builder_raw = RegimeFeatureBuilder(
        backtest_start="2015-01-01",
        backtest_end="2026-06-30",
        data_load_start="2010-01-01",
        shrinkage_ema_alpha=None,
    )
    from zephyr.regime.core.regime_detector import RegimeDetector

    det = RegimeDetector(shrinkage_enabled=True)
    raw = builder_raw.build_shrinkage_schedule(det, train_years=5, detect_window=60)
    raw_s = pd.Series(raw).sort_index()
    print(f"  raw: {len(raw_s)} 日")

    # 手动 EMA 平滑（复用 builder 的静态方法，α=0.15）
    sm_dict = RegimeFeatureBuilder._ema_smooth_schedule({k: float(v) for k, v in raw_s.items()}, alpha=0.15)
    sm_s = pd.Series(sm_dict).sort_index()

    print("\n" + "─" * 72)
    print("全样本分布对比")
    print("─" * 72)
    describe("raw      ", raw_s.to_numpy())
    describe("smoothed ", sm_s.to_numpy())

    print("\n" + "─" * 72)
    print("危机时段切片（raw vs smoothed 均值）")
    print("─" * 72)
    print(f"  {'时段':<16} {'区间':<24} {'raw均值':>8} {'sm均值':>8} {'raw<0.6%':>9} {'sm<0.6%':>9}")
    for label, start, end in CRISIS_PERIODS:
        r = raw_s.loc[start:end]
        s = sm_s.loc[start:end]
        if len(r) == 0:
            print(f"  {label:<16} {start}~{end}  无数据")
            continue
        print(
            f"  {label:<16} {start}~{end}  {r.mean():>8.3f} {s.mean():>8.3f} "
            f"{100 * (r < 0.6).mean():>8.1f}% {100 * (s < 0.6).mean():>8.1f}%"
        )

    # 逐日危机切片（2015股灾峰值）
    print("\n" + "─" * 72)
    print("2015股灾峰值时段逐日（raw vs smoothed）")
    print("─" * 72)
    seg = raw_s.loc["2015-07-01":"2015-09-15"]
    seg_sm = sm_s.loc["2015-07-01":"2015-09-15"]
    for dt, rv in seg.items():
        sv = seg_sm.get(dt, float("nan"))
        flag = "  <<<强收缩" if rv < 0.6 else ""
        print(f"  {dt.strftime('%Y-%m-%d')} raw={rv:.3f} sm={sv:.3f}{flag}")

    print("\n" + "=" * 72)
    print("诊断完成")


if __name__ == "__main__":
    main()
