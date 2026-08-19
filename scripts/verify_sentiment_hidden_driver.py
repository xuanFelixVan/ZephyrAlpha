# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/28_sentiment_cycle_trading.md §3.7
# [MODULE] scripts.verify_sentiment_hidden_driver
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.sentiment_cycle; numpy
# [CONSUMERS] G07 相关性验证批次（人工/CI 运行）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 只读验证脚本：不写库、不改配置；exit 0=验证完成（结果见 JSON 报告）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入 CSV 缺列/长度不一致 → exit 2 + stderr 说明
# [TESTS] tests/scripts/test_verify_sentiment_hidden_driver.py
# [TTL] permanent
"""情绪周期"隐形驱动"验证脚本（28 号 memo §3.7.4，G07 施工前必做）。

验证链路：
  ① Hawkes 自激发建模情绪爆发-传染-衰减（事件序列 → 日度强度 λ(t) 序列，η=α/β 分支比）
  ② 各策略日收益与 λ 的实测相关 ρ_obs（判据：>0.6 强驱动/0.3-0.6 中等/<0.3 弱）
  ③ block-bootstrap 零分布显著性（p<0.05 显著 = 情绪驱动非偶然）
  ④ §3.7.2 分层相关性（按情绪阶段分层后 ρ 应显著下降，否则"多策略=情绪 beta 穿多件衣服"）

用法：
  python scripts/verify_sentiment_hidden_driver.py                 # 合成演示（自检管线）
  python scripts/verify_sentiment_hidden_driver.py --csv data.csv  # 真实数据
      CSV 列：daban,multifactor,event_driven（日收益）+ intensity（日度情绪强度）
      可选列：phase（冰点/反核/主升/疯狂/退潮，用于 §3.7.2 分层）
  --n-bootstrap 2000 --block-size 5 --seed 42

输出：JSON 报告（stdout）。exit 0=完成；exit 2=输入错误。
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

from zephyr.signal_ashare.sentiment_cycle import (
    SentimentHawkesParams,
    SentimentPhase,
    analyze_sentiment_driven_correlation,
    compute_hawkes_intensity,
    estimate_hawkes_branching_ratio,
    validate_sentiment_hidden_driver,
)

_PHASE_BY_VALUE = {p.value: p for p in SentimentPhase}


def simulate_hawkes_events(
    n_days: int,
    lambda_0: float,
    alpha: float,
    beta: float,
    seed: int = 42,
) -> list[float]:
    """Ogata 稀释法模拟 Hawkes 自激发事件时间（单位：日）。"""
    rng = np.random.default_rng(seed)
    events: list[float] = []
    t = 0.0
    while t < n_days:
        lam_bar = lambda_0 + sum(alpha * math.exp(-beta * (t - ti)) for ti in events)
        lam_bar = max(lam_bar, 1e-9)
        t += -math.log(max(rng.random(), 1e-12)) / lam_bar
        if t >= n_days:
            break
        lam_t = lambda_0 + sum(alpha * math.exp(-beta * (t - ti)) for ti in events)
        if rng.random() * lam_bar <= lam_t:
            events.append(t)
    return events


def daily_intensity_series(
    event_times: list[float],
    params: SentimentHawkesParams,
    n_days: int,
) -> list[float]:
    """事件序列 → 日度 Hawkes 强度序列（t=0.5, 1.5, ..., n-0.5 日中点采样）。"""
    return [compute_hawkes_intensity(event_times, params, t + 0.5) for t in range(n_days)]


def _synthetic_dataset(n_days: int, seed: int) -> tuple[dict[str, list[float]], list[float], list[SentimentPhase]]:
    """合成演示数据：Hawkes 情绪强度 + 三策略收益（强/中/弱驱动已知 ρ）+ 阶段标签。"""
    params = SentimentHawkesParams(lambda_0=0.6, alpha=0.45, beta=0.9, critical_ratio=0.5)
    events = simulate_hawkes_events(n_days, params.lambda_0, params.alpha, params.beta, seed)
    lam = np.array(daily_intensity_series(events, params, n_days))
    lam_std = (lam - lam.mean()) / max(lam.std(), 1e-9)
    rng = np.random.default_rng(seed + 1)
    returns = {
        "daban": (0.015 * lam_std + rng.normal(0, 0.012, n_days)).tolist(),  # 强驱动
        "event_driven": (0.007 * lam_std + rng.normal(0, 0.012, n_days)).tolist(),  # 中等
        "multifactor": (0.002 * lam_std + rng.normal(0, 0.012, n_days)).tolist(),  # 弱驱动
    }
    # 强度分位 → 阶段标签（演示用：低→冰点，高→疯狂）
    qs = np.quantile(lam, [0.2, 0.4, 0.6, 0.8])
    phases = []
    for v in lam:
        if v <= qs[0]:
            phases.append(SentimentPhase.FREEZING)
        elif v <= qs[1]:
            phases.append(SentimentPhase.STARTING)
        elif v <= qs[2]:
            phases.append(SentimentPhase.FERMENTING)
        elif v <= qs[3]:
            phases.append(SentimentPhase.CONSENSUS)
        else:
            phases.append(SentimentPhase.EBING)
    return returns, lam.tolist(), phases


def _load_csv(path: Path) -> tuple[dict[str, list[float]], list[float], list[SentimentPhase]]:
    strategies = ("daban", "multifactor", "event_driven")
    returns: dict[str, list[float]] = {s: [] for s in strategies}
    intensity: list[float] = []
    phases: list[SentimentPhase] = []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in (*strategies, "intensity") if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV 缺列: {missing}（需要 {strategies} + intensity，可选 phase）")
        for row in reader:
            for s in strategies:
                returns[s].append(float(row[s]))
            intensity.append(float(row["intensity"]))
            if row.get("phase"):
                phases.append(_PHASE_BY_VALUE[row["phase"].strip()])
    n = len(intensity)
    if any(len(v) != n for v in returns.values()):
        raise ValueError("CSV 列长度不一致")
    if phases and len(phases) != n:
        raise ValueError("phase 列长度与数据行数不一致")
    return returns, intensity, phases


def run_verification(
    strategy_returns: dict[str, list[float]],
    intensity: list[float],
    phases: list[SentimentPhase],
    n_bootstrap: int,
    block_size: int,
) -> dict:
    """③ block-bootstrap 显著性 + ④ 分层相关性 + Hawkes η 摘要。"""
    bootstrap = analyze_sentiment_driven_correlation(
        strategy_returns, intensity,
        n_bootstrap=n_bootstrap, block_size=block_size,
    )
    driver_verdict = {}
    for strat, rho in bootstrap["observed_rho"].items():
        level = "强驱动" if abs(rho) > 0.6 else ("中等驱动" if abs(rho) > 0.3 else "弱驱动")
        driver_verdict[strat] = {
            "rho": round(rho, 4),
            "level": level,
            "p_value": round(bootstrap["p_value"][strat], 4),
            "is_significant": bootstrap["is_significant"][strat],
        }
    stratification = {}
    if phases:
        results = validate_sentiment_hidden_driver(strategy_returns, phases)
        stratification = {
            p.value: {"n_days": r.n_days, "is_pass": r.is_pass}
            for p, r in results.items()
        }
    return {
        "n_days": len(intensity),
        "n_bootstrap": n_bootstrap,
        "block_size": block_size,
        "driver_verdict": driver_verdict,
        "stratification": stratification,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="情绪周期隐形驱动 Hawkes+block-bootstrap 验证")
    parser.add_argument("--csv", type=Path, default=None, help="真实数据 CSV（缺省=合成演示）")
    parser.add_argument("--n-days", type=int, default=250, help="合成模式天数")
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    parser.add_argument("--block-size", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    try:
        if args.csv is not None:
            returns, intensity, phases = _load_csv(args.csv)
            source = f"csv:{args.csv}"
        else:
            returns, intensity, phases = _synthetic_dataset(args.n_days, args.seed)
            source = "synthetic"
        if len(intensity) < max(args.block_size * 2, 10):
            raise ValueError(f"数据量不足: {len(intensity)} 日（至少 {max(args.block_size * 2, 10)} 日）")
    except (ValueError, OSError) as exc:
        print(f"输入错误: {exc}", file=sys.stderr)
        return 2

    report = run_verification(returns, intensity, phases, args.n_bootstrap, args.block_size)
    report["source"] = source
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
