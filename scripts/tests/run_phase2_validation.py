# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# [ARCH-REF] #discussion_003 #MOD-REGIME-VAL-002
# [TTL] permanent
"""Phase 2 模型质量验证执行脚本（discussion_003: A1 + B4 + A2 + B1）

复用 C1 真实模式管线（取数+特征+walk-forward refit），自行执行 detect 收集
A1/B4/B1 所需中间产物（Viterbi 状态序列 / _last_transitions / detect_records）。

数据链（2010-2026）:
  ClickHouse → RegimeFeatureBuilder(指数K线 → HMM 6特征)
    → A1: 全历史 fit + Viterbi 解码 + 计数
    → B4: walk-forward 季度 refit + 逐日 detect + 收集 _last_transitions
          + 匹配 historical_events.yaml（±5 交易日）→ 命中率
    → A2: IS/OOS 交叉解码一致率（IS≤2018, OOS≥2019）
    → B1: detect_records(confidence, dominant_regime) + 后续 20 日收益 → 校准误差

Usage:
  python scripts/tests/run_phase2_validation.py              # 真实数据 Phase 2 全量
  python scripts/tests/run_phase2_validation.py --first-batch  # 仅 A1+B4（跳过 A2+B1）
  python scripts/tests/run_phase2_validation.py --no-overlay   # B4 降级（无 overlay）
  python scripts/tests/run_phase2_validation.py --mock         # 合成数据冒烟

依据: discussion_003 §4
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import warnings
from pathlib import Path

import numpy as np

# real 模式才 import（避免依赖 ClickHouse/hmmlearn）
REAL_DEPS_OK = False
try:
    from zephyr.data import ch_reader  # noqa: F401
    from zephyr.data.table_registry import get_registry  # noqa: F401
    from zephyr.regime.core.regime_detector import RegimeDetector  # noqa: F401
    from zephyr.regime.features.regime_data_loader import RegimeDataLoader
    from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder
    from zephyr.regime.validation.phase2 import Phase2Runner

    REAL_DEPS_OK = True
except Exception as _exc:  # pragma: no cover  # noqa: BLE001
    _REAL_IMPORT_ERROR = _exc


def run_mock() -> int:
    """合成数据冒烟：验证 Phase 2 流程端到端跑通（不代表真实效果）。"""
    print("[mock] Phase 2 冒烟：合成特征矩阵 + A1/B4/A2/B1 流程")
    import pandas as pd

    from zephyr.regime.validation.phase2.a1_sample_sufficiency import A1SampleSufficiency
    from zephyr.regime.validation.phase2.a2_hmm_overfitting import A2HmmOverfitting
    from zephyr.regime.validation.phase2.b1_probability_calibration import (
        B1ProbabilityCalibration,
    )
    from zephyr.regime.validation.phase2.b4_transition_accuracy import (
        B4TransitionAccuracy,
        HistoricalEvent,
    )

    # 合成 9 态分布均衡的特征矩阵（2000 样本 × 6 特征，IS=1000/OOS=1000）
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1, size=(2000, 6))
    a1 = A1SampleSufficiency()
    a1_report = a1.validate(X, standardize=True)
    print(f"[mock] A1: {a1_report.summary}")
    for s in a1_report.state_stats:
        print(f"  {s.state}: {s.count} 天 ({s.frequency:.1%}) → {s.verdict.value}")

    # A2 冒烟：IS=1000, OOS=1000
    a2 = A2HmmOverfitting()
    a2_report = a2.validate(X, is_end_idx=1000, standardize=True)
    print(f"[mock] A2: {a2_report.summary}")

    # B1 冒烟：合成 detect_records + 上涨 close（20 日累计收益需 > 0.5% 才有方向）
    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    # 日均收益 0.5% → 20 日 ~10%，远超 0.5% 阈值
    close = pd.Series(
        np.cumprod(1 + np.random.default_rng(1).normal(0.005, 0.015, 300)) * 100,
        index=dates,
    )
    records = [
        {"timestamp": dates[i], "confidence": 0.6 + 0.3 * (i / 300), "dominant_regime": "r3"} for i in range(250)
    ]
    b1 = B1ProbabilityCalibration()
    b1_report = b1.validate(records, close, forward_days=20)
    print(f"[mock] B1: {b1_report.summary}")

    # B4 冒烟：空 daily_transitions + 1 事件
    b4 = B4TransitionAccuracy()
    events = [
        HistoricalEvent(
            id="EVT-MOCK",
            date=pd.Timestamp("2024-01-15"),
            transition_type="S1",
            expected_stage=["trigger", "confirm"],
            desc="mock",
            in_data_range=True,
        )
    ]
    daily = {pd.Timestamp("2024-01-14"): []}
    b4_report = b4.validate(daily, events=events)
    print(f"[mock] B4: {b4_report.summary}")
    print("[mock] Phase 2 冒烟跑通 ✓")
    return 0


def run_real(
    enable_overlay: bool = True,
    enable_full_risk: bool = True,
    run_second_batch: bool = True,
) -> int:
    """真实数据 Phase 2 验证（2010-2026）。"""
    if not REAL_DEPS_OK:
        print(f"[real] 依赖导入失败: {_REAL_IMPORT_ERROR}")
        print("[real] 请确认 zephyr.regime / zephyr.data 模块可用")
        return 1

    warnings.filterwarnings("ignore", message=".*not converging.*")
    logging.getLogger("hmmlearn").setLevel(logging.ERROR)

    batch_tag = "A1+B4+A2+B1" if run_second_batch else "A1+B4"
    print(f"[real] 配置: enable_overlay={enable_overlay}, enable_full_risk={enable_full_risk}, batch={batch_tag}")
    print("[real] 构建 RegimeFeatureBuilder（复用 C1 真实模式配置）...")
    data_loader = RegimeDataLoader(
        data_load_start="2010-01-01",
        backtest_end="2026-06-30",
    )
    builder = RegimeFeatureBuilder(
        backtest_start="2015-01-01",
        backtest_end="2026-06-30",
        data_load_start="2010-01-01",
        enable_full_risk=enable_full_risk,
        enable_overlay=enable_overlay,
        enable_phase2c=True,
        data_loader=data_loader,
    )

    est = "3-5 分钟" if run_second_batch else "2-3 分钟"
    print(f"[real] 运行 Phase 2（{batch_tag}），预计 {est}...")
    runner = Phase2Runner()
    report = runner.run(
        builder,
        train_years=5,
        detect_window=60,
        run_second_batch=run_second_batch,
    )

    # 打印报告
    print()
    print("=" * 70)
    print(f"Phase 2 模型质量验证结果（{batch_tag}）")
    print("=" * 70)
    print()
    print(f"{'=' * 30} A1 样本充足性 {'=' * 30}")
    print(report.a1.summary)
    print(
        f"  总样本: {report.a1.total_samples}, log-lik: {report.a1.fit_log_likelihood:.2f}, "
        f"degraded={report.a1.degraded}"
    )
    print("  各态统计:")
    for s in report.a1.state_stats:
        flag = "✅" if s.verdict.value == "sufficient" else ("⚠️" if s.verdict.value == "moderate" else "❌")
        print(f"    {s.state}: {s.count:4d} 天 ({s.frequency:5.1%}) {flag} {s.action}")

    print()
    print(f"{'=' * 30} B4 转换触发 {'=' * 30}")
    print(report.b4.summary)
    print("  事件匹配明细:")
    for m in report.b4.matches:
        tag = "✓" if m.hit else "✗"
        if m.triggered_at is not None:
            print(
                f"    {tag} {m.event.id} ({m.event.transition_type}) "
                f"事件日={m.event.date.date()} 触发日={m.triggered_at.date()} "
                f"Δ={m.delta_days:+d}d stage={m.matched_stage}"
            )
        else:
            if not m.event.in_data_range:
                tag2 = "[超出范围]"
            elif not m.event.data_ready:
                tag2 = "[待数据]"
            else:
                tag2 = tag
            print(f"    {tag2} {m.event.id} ({m.event.transition_type}) 事件日={m.event.date.date()} 未触发")
    print("  按转换类型:")
    for tid, st in report.b4.per_transition_hits.items():
        if st["total"] > 0:
            print(f"    {tid}: {st['hit']}/{st['total']}")

    if report.a2 is not None:
        print()
        print(f"{'=' * 30} A2 过拟合 {'=' * 30}")
        print(report.a2.summary)
        print(
            f"  IS_acc={report.a2.is_accuracy:.1%}, OOS_acc={report.a2.oos_accuracy:.1%}, "
            f"OOS/IS={report.a2.ratio:.3f}, KL={report.a2.kl_divergence:.4f}"
        )
        print(f"  标签对齐: {report.a2.label_alignment}")
        print(f"  IS样本={report.a2.is_samples}, OOS样本={report.a2.oos_samples}, degraded={report.a2.degraded}")

    if report.b1 is not None:
        print()
        print(f"{'=' * 30} B1 概率校准度 {'=' * 30}")
        print(report.b1.summary)
        print(
            f"  校准误差={report.b1.calibration_error:.1%}, 最大桶误差={report.b1.max_bucket_error:.1%}, "
            f"样本={report.b1.total_samples}, forward={report.b1.forward_days}d"
        )
        print(f"  各态推断方向: {report.b1.regime_directions}")
        print("  可靠性曲线:")
        for p in report.b1.reliability_curve:
            if p.count > 0:
                print(f"    {p.bucket}: 预测={p.predicted:.3f} 实际={p.actual:.3f} 误差={p.error:.3f} (n={p.count})")

    print()
    print("=" * 70)
    if report.overall_pass:
        print(f"🎉 Phase 2 ({batch_tag}) 通过 → 可进 Phase 3 参数校准")
    else:
        print(f"⛔ Phase 2 需复核: {report.summary}")
    print("=" * 70)

    # 写 JSON 报告到 runtime
    out = Path("runtime/phase2_reports")
    out.mkdir(parents=True, exist_ok=True)
    ts = report.run_at.strftime("%Y%m%d_%H%M%S")
    tag = "full" if run_second_batch else "a1b4"
    json_path = out / f"phase2_{tag}_{ts}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"\n[real] JSON 报告: {json_path}")
    return 0 if report.overall_pass else 1


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Phase 2 模型质量验证（A1 + B4 [+ A2 + B1]）")
    parser.add_argument("--mock", action="store_true", help="合成数据冒烟")
    parser.add_argument("--no-overlay", action="store_true", help="关闭 overlay（B4 将降级）")
    parser.add_argument("--no-full-risk", action="store_true", help="关闭 full risk（回退 Phase 1）")
    parser.add_argument("--first-batch", action="store_true", help="仅跑第一批 A1+B4（跳过 A2+B1）")
    args = parser.parse_args()

    if args.mock:
        sys.exit(run_mock())
    sys.exit(
        run_real(
            enable_overlay=not args.no_overlay,
            enable_full_risk=not args.no_full_risk,
            run_second_batch=not args.first_batch,
        )
    )


if __name__ == "__main__":
    main()
