# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""B1 forward_days 参数扫描脚本（12_regime_phase2_validation §10.4 P2）。

B1 基线误差 17.7%，80-100% 桶预测 0.982 实际 0.524（HMM 过度自信）。
但 forward_days=20 可能太短——HMM 6 特征含 Hurst/vol_pct 是中期特征，
更长窗口（60/120 日）可能更好地体现 regime 的收益预测力。

本脚本跑一次 walk-forward 收集 detect_records，然后扫描多个 forward_days，
找出校准误差最低的窗口。纯测量探索，不改模型，无 C1 退化风险。

Usage:
    python scripts/tests/scan_b1_forward_days.py
"""

from __future__ import annotations

import logging
import warnings

import pandas as pd

from zephyr.regime.regime_feature_builder import FEATURE_NAMES, RegimeFeatureBuilder
from zephyr.regime.validation.phase2 import Phase2Runner
from zephyr.regime.validation.phase2.b1_probability_calibration import (
    B1ProbabilityCalibration,
)

warnings.filterwarnings("ignore", message=".*not converging.*")
logging.getLogger("hmmlearn").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    print("[scan] 构建 RegimeFeatureBuilder（复用 Phase 2 配置）...")
    builder = RegimeFeatureBuilder(
        backtest_start="2015-01-01",
        backtest_end="2026-06-30",
        data_load_start="2010-01-01",
        enable_full_risk=True,
        enable_overlay=True,
    )

    runner = Phase2Runner()
    features = builder.build_features()
    feature_names = list(FEATURE_NAMES)

    print("[scan] walk-forward 逐日 detect 收集 detect_records（约 3 分钟）...")
    _daily, _dates, detect_records = runner._collect_daily_transitions(  # noqa: SLF001
        builder,
        features,
        feature_names,
        train_years=5,
        detect_window=60,
        refit_freq="QE",
    )
    print(f"[scan] 收集 {len(detect_records)} 条 detect_records")

    close = runner._get_index_close(builder)  # noqa: SLF001
    if close is None or close.empty:
        print("[scan] 无法获取 index close，退出")
        return

    b1 = B1ProbabilityCalibration()
    forward_days_list = [10, 20, 40, 60, 90, 120]

    print()
    print("=" * 78)
    print("B1 forward_days 参数扫描（校准误差 vs 后续收益窗口）")
    print("=" * 78)
    print(f"{'forward_days':>12} {'误差':>8} {'最大桶误差':>10} {'判定':>8}   80-100%桶(预测/实际/误差/n)")
    print("-" * 78)

    for fd in forward_days_list:
        report = b1.validate(detect_records, close, forward_days=fd)
        # 找 80-100% 桶
        hi = next((p for p in report.reliability_curve if p.bucket == "80-100%" and p.count > 0), None)
        hi_str = f"{hi.predicted:.3f}/{hi.actual:.3f}/{hi.error:.3f}/n={hi.count}" if hi else "—"
        print(
            f"{fd:>12} {report.calibration_error:>7.1%} {report.max_bucket_error:>9.1%} "
            f"{report.verdict.value:>8}   {hi_str}"
        )

    print("=" * 78)
    print("解读：若长窗口（60/120日）误差显著下降 → HMM 非过度自信，20日窗口太短")
    print("      若长窗口仍高误差 → HMM 确实过度自信，需温度缩放校准")


if __name__ == "__main__":
    main()
