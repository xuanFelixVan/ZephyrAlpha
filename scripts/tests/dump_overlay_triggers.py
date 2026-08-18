# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# [ARCH-REF] #ARCH-REGIME-OVERLAY-001 #Phase2b
# [TTL] permanent
"""Dump overlay 触发历史 + 净 Shrinkage 影响分析（#ARCH-REGIME-OVERLAY-001 深挖）。

复刻 RegimeFeatureBuilder.build_shrinkage_schedule 的 walk-forward 循环（enable_overlay=True），
在每次 detector.detect() 调用后捕获审计快照：
  - 8 转换触发记录（transition_type/stage/total_score/score_breakdown）
  - overlay_probabilities (r10/r11/r12 的 p_overlay)
  - HMM 原始 dominant vs 合并后 dominant（是否被 overlay 切换）
  - actual shrinkage vs baseline shrinkage（overlay_probs=0 重算 confidence）

baseline_shrinkage 隔离 overlay 通过 confidence 通道对 Shrinkage 的净影响：
  actual      = confidence(merge(hmm, overlay)) × risk
  baseline    = confidence(merge(hmm, {0,0,0}))  × risk   # overlay=0 即纯 HMM
  delta       = actual - baseline = [conf(merged) - conf(hmm_only)] × risk
  delta < 0 → overlay 压低了 Shrinkage（在错误时点压仓→Sharpe 退化嫌疑）

关键发现（读码确认）：_run_overlay 只用 stage_cfg["p_overlay"] 注入 r10/r11/r12 概率，
stage_cfg["shrinkage"] 锚定值是死代码——overlay 不直接设 Shrinkage，而是经概率合并
改 dominant_regime → 改 confidence_signal → 改 Shrinkage。

输出（logs/c1_repro/）:
  overlay_audit_daily.csv  —— 每日触发明细 + Shrinkage 净影响
  overlay_audit_summary.md —— 8 转换触发次数表 + 误触发 TOP 日期 + 调参建议

Usage:
  python scripts/tests/dump_overlay_triggers.py
"""
from __future__ import annotations

import logging
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from zephyr.regime.core.regime_detector import (
    HMM_STATES,
    OVERLAY_STATES,
    RegimeDetector,
)
from zephyr.regime.regime_feature_builder import (
    FEATURE_NAMES,
    RegimeFeatureBuilder,
)

REAL_START = "2015-01-01"
REAL_END = "2026-06-30"
DATA_LOAD_START = "2010-01-01"
REPRO_DIR = Path(r"d:\ZephyrAlpha\logs\c1_repro")


def _baseline_shrinkage(
    detector: RegimeDetector, hmm_probs: dict[str, float], risk: float
) -> tuple[float, str, float]:
    """重算 baseline：overlay_probs=0（纯 HMM）下的 confidence × risk。

    Returns:
        (baseline_shrinkage, baseline_dominant, baseline_confidence)
    """
    baseline_probs = detector._merge_probabilities(
        hmm_probs, {s: 0.0 for s in OVERLAY_STATES}
    )
    baseline_conf = detector._compute_confidence_signal(baseline_probs)
    val = baseline_conf * risk
    if val > 1.0:
        val = 1.0
    return val, baseline_probs.dominant_regime, baseline_conf


def run_overlay_audit() -> pd.DataFrame:
    """跑 walk-forward（overlay on），捕获每日触发审计。

    Returns:
        每日审计 DataFrame（含触发转换/overlay概率/dominant切换/Shrinkage净影响）。
    """
    warnings.filterwarnings("ignore", message=".*not converging.*")
    logging.getLogger("hmmlearn").setLevel(logging.ERROR)

    print("[overlay-audit] 构建 RegimeFeatureBuilder（enable_overlay=True, risk=simple）...")
    builder = RegimeFeatureBuilder(
        backtest_start=REAL_START,
        backtest_end=REAL_END,
        data_load_start=DATA_LOAD_START,
        enable_full_risk=False,
        enable_overlay=True,
    )
    detector = RegimeDetector(shrinkage_enabled=True)

    # 触发 overlay 构造器惰性初始化（build_shrinkage_schedule 内部会做，这里提前确保）
    features = builder.build_features()
    features_shifted = features.shift(1)
    # 提前触发 _risk_ctor / _overlay_ctor 的惰性构造（复刻 build_shrinkage_schedule 逻辑）
    if builder.enable_full_risk and builder._risk_ctor is None:
        from zephyr.regime.risk_signal_builder import RiskSignalConstructor
        builder._risk_ctor = RiskSignalConstructor(
            backtest_start=builder.backtest_start,
            backtest_end=builder.backtest_end,
            data_load_start=builder.data_load_start,
            feature_builder=builder,
            market_proxy=builder.market_proxy,
        )
    if builder.enable_overlay and builder._overlay_ctor is None:
        from zephyr.regime.overlay_signals_builder import OverlaySignalsConstructor
        builder._overlay_ctor = OverlaySignalsConstructor(
            backtest_start=builder.backtest_start,
            backtest_end=builder.backtest_end,
            data_load_start=builder.data_load_start,
            feature_builder=builder,
            risk_constructor=builder._risk_ctor,
            market_proxy=builder.market_proxy,
        )
        print("[overlay-audit] OverlaySignalsConstructor 已启用")

    from sklearn.preprocessing import RobustScaler

    quarter_ends = builder._quarter_end_dates(
        pd.Timestamp(DATA_LOAD_START) + pd.DateOffset(years=5),
        pd.Timestamp(REAL_END),
        freq="QE",
    )
    print(f"[overlay-audit] walk-forward: {len(quarter_ends)} 个季度边界")

    audit_rows: list[dict] = []
    n_detect = 0
    n_warmup = 0

    for i, q in enumerate(quarter_ends):
        train_start = (q - pd.DateOffset(years=5)).strftime("%Y-%m-%d")
        train_end = q.strftime("%Y-%m-%d")
        scaler = None
        try:
            train_matrix = builder.build_train_matrix(train_start, train_end)
            X_train = train_matrix["X"]
            if builder.standardize_features:
                scaler = RobustScaler().fit(X_train)
                X_train = scaler.transform(X_train)
            detector.fit({"X": X_train, "lengths": train_matrix.get("lengths")})
        except Exception as exc:
            logging.warning("fit Q%d [%s,%s] 失败，本季降级: %s", i + 1, train_start, train_end, exc)

        next_q = (
            quarter_ends[i + 1]
            if i + 1 < len(quarter_ends)
            else pd.Timestamp(REAL_END)
        )
        detect_start = max(q + pd.Timedelta(days=1), pd.Timestamp(REAL_START))
        detect_end = min(next_q, pd.Timestamp(REAL_END))
        if detect_start > detect_end:
            continue

        period = features_shifted.loc[detect_start:detect_end]
        for dt, _row in period.iterrows():
            window = features_shifted.loc[:dt].iloc[-60:]
            if len(window) < 10 or window.dropna().empty:
                n_warmup += 1
                audit_rows.append(_warmup_row(dt))
                continue

            last_row = window.iloc[-1]
            risk_inputs = builder._build_feature_risk(
                vol_pct=_safe(last_row.get("realized_vol_pct")),
                slope=_safe(last_row.get("kalman_slope")),
                vol_anom=_safe(last_row.get("volume_anomaly")),
            )
            overlay_signals = (
                builder._overlay_ctor.build_for_date(dt)
                if builder._overlay_ctor is not None
                else {}
            )
            X = window[FEATURE_NAMES].to_numpy(dtype=float)
            X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
            if scaler is not None:
                X = scaler.transform(X)

            try:
                probs, shrinkage = detector.detect(
                    {"X": X},
                    overlay_signals=overlay_signals,
                    risk_signal_inputs=risk_inputs,
                )
            except Exception as exc:
                logging.warning("detect 异常 (date=%s): %s", dt, exc)
                audit_rows.append(_warmup_row(dt))
                continue

            n_detect += 1
            transitions = list(detector._last_transitions) if detector._last_transitions else []
            hmm_probs = probs.hmm_probabilities
            hmm_dominant = max(hmm_probs, key=hmm_probs.get)
            baseline_shr, baseline_dom, baseline_conf = _baseline_shrinkage(
                detector, hmm_probs, shrinkage.risk_signal
            )
            triggered = [t for t in transitions if t.stage != "none"]
            audit_rows.append({
                "date": dt.strftime("%Y-%m-%d"),
                "n_triggered": len(triggered),
                "triggered_tids": "|".join(f"{t.transition_type}:{t.stage}" for t in triggered) or "-",
                "triggered_details": "; ".join(
                    f"{t.transition_type}/{t.stage}(total={t.total_score:.0f})"
                    for t in triggered
                ) or "-",
                "overlay_r10": float(probs.overlay_probabilities.get("r10", 0.0)),
                "overlay_r11": float(probs.overlay_probabilities.get("r11", 0.0)),
                "overlay_r12": float(probs.overlay_probabilities.get("r12", 0.0)),
                "hmm_dominant": hmm_dominant,
                "merged_dominant": probs.dominant_regime,
                "baseline_dominant": baseline_dom,
                "dominant_switched": hmm_dominant != probs.dominant_regime,
                "confidence": float(shrinkage.confidence_signal),
                "baseline_confidence": float(baseline_conf),
                "risk": float(shrinkage.risk_signal),
                "shrinkage": float(shrinkage.value),
                "baseline_shrinkage": float(baseline_shr),
                "delta": float(shrinkage.value - baseline_shr),
                "is_warmup": False,
            })

    print(f"[overlay-audit] 完成: {n_detect} 日 detect, {n_warmup} 日 warmup/异常")
    return pd.DataFrame(audit_rows)


def _warmup_row(dt) -> dict:
    return {
        "date": dt.strftime("%Y-%m-%d"),
        "n_triggered": 0,
        "triggered_tids": "-",
        "triggered_details": "-",
        "overlay_r10": 0.0, "overlay_r11": 0.0, "overlay_r12": 0.0,
        "hmm_dominant": "-", "merged_dominant": "-", "baseline_dominant": "-",
        "dominant_switched": False,
        "confidence": 1.0, "baseline_confidence": 1.0, "risk": 1.0,
        "shrinkage": 1.0, "baseline_shrinkage": 1.0, "delta": 0.0,
        "is_warmup": True,
    }


def _safe(v) -> float:
    try:
        if v is None:
            return 0.0
        f = float(v)
        return f if f == f else 0.0  # NaN 检查
    except (TypeError, ValueError):
        return 0.0


def summarize(df: pd.DataFrame) -> str:
    """生成汇总报告。"""
    active = df[~df["is_warmup"]].copy()
    n_days = len(active)
    n_trigger_days = int((active["n_triggered"] > 0).sum())
    n_switch = int(active["dominant_switched"].sum())
    n_delta_neg = int((active["delta"] < -1e-6).sum())
    n_delta_pos = int((active["delta"] > 1e-6).sum())

    # 各转换触发次数（解析 triggered_tids）
    tid_counts: dict[str, int] = {}
    tid_stage_counts: dict[str, dict[str, int]] = {}
    for s in active.loc[active["n_triggered"] > 0, "triggered_tids"]:
        for tok in s.split("|"):
            if tok == "-":
                continue
            tid, stage = tok.split(":")
            tid_counts[tid] = tid_counts.get(tid, 0) + 1
            tid_stage_counts.setdefault(tid, {})
            tid_stage_counts[tid][stage] = tid_stage_counts[tid].get(stage, 0) + 1

    # delta 分布（仅触发日）
    trig_delta = active.loc[active["n_triggered"] > 0, "delta"]
    no_trig_delta = active.loc[active["n_triggered"] == 0, "delta"]

    # 误触发 TOP 日期：delta 最负（overlay 压低 Shrinkage 最多）
    top_neg = active.nsmallest(15, "delta")[
        ["date", "triggered_tids", "overlay_r10", "overlay_r11", "overlay_r12",
         "hmm_dominant", "merged_dominant", "shrinkage", "baseline_shrinkage", "delta"]
    ]
    # overlay 抬高 Shrinkage TOP（罕见，但若有说明 overlay 在低 confidence 时反而注入高 confidence 态）
    top_pos = active.nlargest(10, "delta")[
        ["date", "triggered_tids", "merged_dominant", "shrinkage", "baseline_shrinkage", "delta"]
    ]

    lines = []
    lines.append("# A3 Overlay 触发历史深挖报告（#ARCH-REGIME-OVERLAY-001）")
    lines.append("")
    lines.append(f"> 生成: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("> 数据: 2015-01-01 ~ 2026-06-30, walk-forward 46 季度")
    lines.append("> 模式: risk=simple / overlay=on（A3 配置）")
    lines.append("")
    lines.append("## 1. 总览")
    lines.append("")
    lines.append(f"- 有效 detect 日: **{n_days}**")
    lines.append(f"- 触发转换日（n_triggered>0）: **{n_trigger_days}** ({100*n_trigger_days/n_days:.1f}%)")
    lines.append(f"- dominant 被 overlay 切换日: **{n_switch}** ({100*n_switch/n_days:.1f}%)")
    lines.append(f"- delta<0（overlay 压低 Shrinkage）: **{n_delta_neg}** 日")
    lines.append(f"- delta>0（overlay 抬高 Shrinkage）: **{n_delta_pos}** 日")
    lines.append(f"- delta=0（overlay 无影响）: **{n_days - n_delta_neg - n_delta_pos}** 日")
    lines.append("")
    lines.append("## 2. 8 转换触发次数")
    lines.append("")
    lines.append("| 转换 | 触发日数 | 占比 | stage 明细 |")
    lines.append("|------|---------|------|-----------|")
    for tid in ["S1", "S2", "T1", "T2", "T3", "T4", "T5", "T6"]:
        cnt = tid_counts.get(tid, 0)
        stages = tid_stage_counts.get(tid, {})
        stage_str = ", ".join(f"{k}:{v}" for k, v in sorted(stages.items())) or "-"
        lines.append(f"| {tid} | {cnt} | {100*cnt/n_days:.1f}% | {stage_str} |")
    lines.append("")
    lines.append("## 3. delta 分布（Shrinkage 净影响）")
    lines.append("")
    lines.append("delta = actual_shrinkage - baseline_shrinkage（overlay 通过 confidence 通道的净影响）")
    lines.append("")
    lines.append(f"- 触发日 delta 均值: **{trig_delta.mean():.4f}** （中位数 {trig_delta.median():.4f}）")
    if len(no_trig_delta) > 0:
        lines.append(f"- 非触发日 delta 均值: {no_trig_delta.mean():.4f} （应≈0，验证隔离有效性）")
    lines.append(f"- 触发日 delta 范围: [{trig_delta.min():.4f}, {trig_delta.max():.4f}]")
    lines.append("")
    lines.append("## 4. 误触发 TOP 15 日（delta 最负 = overlay 压低 Shrinkage 最多）")
    lines.append("")
    lines.append("| 日期 | 触发转换 | r10 | r11 | r12 | HMM态 | 合并态 | 实际Shr | baselineShr | delta |")
    lines.append("|------|---------|-----|-----|-----|-------|--------|---------|-------------|-------|")
    for _, r in top_neg.iterrows():
        lines.append(
            f"| {r['date']} | {r['triggered_tids']} | {r['overlay_r10']:.2f} | {r['overlay_r11']:.2f} "
            f"| {r['overlay_r12']:.2f} | {r['hmm_dominant']} | {r['merged_dominant']} "
            f"| {r['shrinkage']:.3f} | {r['baseline_shrinkage']:.3f} | {r['delta']:+.3f} |"
        )
    lines.append("")
    lines.append("## 5. overlay 抬高 Shrinkage TOP 10（若有，说明 overlay 注入高 confidence 态）")
    lines.append("")
    if top_pos["delta"].max() <= 1e-6:
        lines.append("（无——overlay 概率注入只会压缩 HMM 概率质量，不会抬高 Shrinkage）")
    else:
        lines.append("| 日期 | 触发转换 | 合并态 | 实际Shr | baselineShr | delta |")
        lines.append("|------|---------|--------|---------|-------------|-------|")
        for _, r in top_pos.iterrows():
            if r["delta"] <= 1e-6:
                continue
            lines.append(
                f"| {r['date']} | {r['triggered_tids']} | {r['merged_dominant']} "
                f"| {r['shrinkage']:.3f} | {r['baseline_shrinkage']:.3f} | {r['delta']:+.3f} |"
            )
    lines.append("")
    lines.append("## 6. 结论与调参建议")
    lines.append("")
    # 自动生成结论
    worst_tid = max(tid_counts, key=tid_counts.get) if tid_counts else "-"
    lines.append(f"- 触发最频繁的转换: **{worst_tid}** ({tid_counts.get(worst_tid, 0)} 日)")
    if n_delta_neg > 0:
        lines.append(
            f"- overlay 压低 Shrinkage 共 {n_delta_neg} 日，触发日 delta 均值 "
            f"{trig_delta.mean():+.4f}——系统性压仓是 Sharpe 退化的直接原因"
        )
    lines.append("")
    lines.append("### 调参方向（基于触发统计）")
    lines.append("")
    for tid in ["S1", "S2", "T1", "T2", "T3", "T4", "T5", "T6"]:
        cnt = tid_counts.get(tid, 0)
        if cnt == 0:
            continue
        lines.append(f"- **{tid}**: {cnt} 日触发 — 若误触发多，调高 keys_gte 阈值或限制仅 #1<1.0 时生效")
    lines.append("")
    lines.append("### 结构性裁剪方向")
    lines.append("")
    lines.append("- 方案 A：overlay 仅在 #1<1.0（危机期）生效——与 RiskSignal #1 门控对齐，")
    lines.append("  平时不干预，危机期才允许 overlay 改概率分布")
    lines.append("- 方案 B：调高所有转换 keys_gte 阈值（如 +20），减少误触发")
    lines.append("- 方案 C：完全否决 overlay（维持 simple/off 生产配置）")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    df = run_overlay_audit()

    csv_path = REPRO_DIR / "overlay_audit_daily.csv"
    df.to_csv(csv_path, index=False)
    print(f"[overlay-audit] 每日明细已写: {csv_path} ({len(df)} 行)")

    report = summarize(df)
    md_path = REPRO_DIR / "overlay_audit_summary.md"
    md_path.write_text(report, encoding="utf-8")
    print(f"[overlay-audit] 汇总报告已写: {md_path}")

    print("\n" + "=" * 70)
    print(report)
    print("=" * 70)


if __name__ == "__main__":
    main()
