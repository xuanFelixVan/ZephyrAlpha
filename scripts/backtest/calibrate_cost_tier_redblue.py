# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md（域挂靠）
# [MODULE] scripts.backtest.calibrate_cost_tier_redblue
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factory_grid_executor; scripts.backtest.translated._c4_engine; zephyr.backtest.regime_validation.exam_cost_gate
# [CONSUMERS] docs/_working/decision_map_campaign_20260924/03_gpu_campaign.md §三.4（GPU 空窗由总指挥人工触发）；单测钉扎=tests/backtest/test_factory_grid_stage_cost_tiers.py
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯标定报告零门禁判定（本件禁当闸用——门=exam_cost_gate 三门）；全档真源=config/exam_scale_cost_gate.yaml（禁双头硬编码）；同格对拍=参考 run manifest 逐格复算，轻/全档指标由同一次五档扫描派生（档位扫描引擎口径唯一=daily_net_returns slippage_bp kwarg，禁二次回测）；零写操作（报告只落 .runtime/tmp/，禁触 data/ 生产路径）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(参考 run 非法/数据缺失)
# [TESTS] tests/backtest/test_factory_grid_stage_cost_tiers.py
# [TTL] permanent
# [A_module] module_id=MOD-BT-196-RB | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""红蓝对拍标定脚本——T1 轻档两档 vs 全档五档成本粗筛排名一致性（方案①两轮制）。

背景: docs/_working/decision_map_campaign_20260924/03_gpu_campaign.md §三.4——方案①
（裁定#413 下一窗口升级案，Owner 2026-09-24 原则批准）以 T1=[0,5] 两档轻档粗筛、
T2 全五档终审，容量 4640→9600。历史基准: 轻/全档排名 Spearman≈1.0、top50 重合
50/50（信息近零损失）。本脚本在同一批格点上复算两套指标，输出:
  1. Spearman 秩相关（轻档 5bp 成本后 sharpe vs 全档 40bp 成本后 sharpe，另附 0bp 对照）;
  2. top-K 重合率（默认 K=50）;
  3. 轻档/全档单格点耗时实测（预算复核口径: 轻档 ≈6-7s/格 验证）。

用法（GPU 空窗，由总指挥执行; 本脚本只做 CPU 向量化回测，不占 GPU）:
  python scripts/backtest/calibrate_cost_tier_redblue.py                     # 自动选最新 grid_* run
  python scripts/backtest/calibrate_cost_tier_redblue.py \
      --run-dir data/strategy_intake/grid_20260924-080309 --n-points 200    # T0 全量对拍
报告: .runtime/tmp/redblue_cost_tier_<run_ts>.json + stdout 摘要。

判读基准（仅供参考，非门禁）: spearman>=0.99 且 top_k_overlap_pct>=0.9 → 轻档粗筛
信息损失可忽略；低于此线 → 升级案需复议（裁定通道）。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "backtest" / "translated"))
sys.path.insert(0, str(_REPO / "scripts" / "backtest"))

#: T1 轻档（方案①预注册草案 budget_caps.cost_gate_t1_tiers_bp 同口径; 0bp=零成本对照）
LIGHT_TIERS_BP: tuple[float, ...] = (0.0, 5.0)
#: 预热窗（与 factory_grid_executor.run_batch 同法，因子/滚动 IC 预热）
WARM_DAYS = 200


def _load_executor():
    """复用 factory_grid_executor 模块函数（零重实现；注册进 sys.modules 与 f06 同法）。"""
    mod = sys.modules.get("factory_grid_executor")
    if mod is None:
        spec = importlib.util.spec_from_file_location(
            "factory_grid_executor", _REPO / "scripts" / "backtest" / "factory_grid_executor.py"
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
    return mod


def load_reference_run(run_dir: Path) -> tuple[pd.DataFrame, tuple[str, str]]:
    """参考 run 的 manifest + 闭卷窗（summary.json window 真源）。

    Raises:
        RuntimeError: run 目录/manifest/window 缺失——参考 run 非法，禁猜测窗口。
    """
    manifest_path = run_dir / "manifest.csv"
    if not manifest_path.exists():
        raise RuntimeError(f"参考 run 非法: {run_dir} 无 manifest.csv")
    manifest = pd.read_csv(manifest_path)
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        raise RuntimeError(f"参考 run 非法: {run_dir} 无 summary.json（window 缺失）")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    window = summary.get("window") or []
    if len(window) != 2:
        raise RuntimeError(f"参考 run 非法: summary.window={window!r}（须 [start, end] 闭卷窗）")
    return manifest, (str(window[0]), str(window[1]))


def rank_agreement(light_scores: dict[str, float], full_scores: dict[str, float], top_k: int = 50) -> dict:
    """轻/全档排名一致性（纯函数，单测钉扎）: Spearman 秩相关 + top-K 重合率。

    Args:
        light_scores/full_scores: recipe_id → 成本后 sharpe（同格点两套指标）。
        top_k: 重合率窗口（默认 50; 超过样本数时取样本数）。

    Returns:
        {n, spearman, top_k, top_k_overlap, top_k_overlap_pct}（样本<2 时统计位=None 诚实缺）。
    """
    ids = sorted(set(light_scores) & set(full_scores))
    if len(ids) < 2:
        return {
            "n": len(ids),
            "spearman": None,
            "top_k": min(top_k, len(ids)),
            "top_k_overlap": None,
            "top_k_overlap_pct": None,
        }
    light = pd.Series({rid: light_scores[rid] for rid in ids})
    full = pd.Series({rid: full_scores[rid] for rid in ids})
    rho = float(light.corr(full, method="spearman"))
    k = min(int(top_k), len(ids))
    top_light = set(light.sort_values(ascending=False).head(k).index)
    top_full = set(full.sort_values(ascending=False).head(k).index)
    overlap = len(top_light & top_full)
    return {
        "n": len(ids),
        "spearman": round(rho, 6),
        "top_k": k,
        "top_k_overlap": overlap,
        "top_k_overlap_pct": round(overlap / k, 4),
    }


def _rebuild_panel(executor, start: str, end: str):
    """数据一次拉取（与 run_batch 同法: 预热 200 日 + ST 过滤 + 派生宽表）。"""
    # st-ddup-20260925 去重改造②适配: _load_engine 7 元组（run_backtest_full 单趟替代两连调）
    load_px, wide, filter_st, load_st_flags, run_backtest_full, daily_net_returns, net_returns_by_tiers = (
        executor._load_engine()
    )

    def run_backtest(weights, px_close, gate_limits=True, slippage_bp=None):
        stats, _net = run_backtest_full(weights, px_close, gate_limits=gate_limits, slippage_bp=slippage_bp)
        return stats

    warm_start = (pd.Timestamp(start) - pd.Timedelta(days=WARM_DAYS)).date().isoformat()
    px = load_px(warm_start, end, fields=("close", "volume"))
    closes_all = wide(px, "close")
    closes = closes_all.loc[(closes_all.index >= pd.Timestamp(start)) & (closes_all.index <= pd.Timestamp(end))]
    flags = load_st_flags(start, end)
    closes_eval = filter_st(closes_all, flags).loc[closes.index]
    vol20 = closes_eval.pct_change().rolling(20).std()
    mkt_cap_w = executor._load_mkt_cap_wide(warm_start, end, closes_all.columns)
    rets_daily = closes_eval.pct_change()
    rets60_mean = rets_daily.rolling(60).mean()
    rets60_var = rets_daily.rolling(60).var()
    try:
        industry_map = executor._industry_map()
    except Exception:  # noqa: BLE001 与 run_batch 同口径: 行业锚失败降级（标 degraded）
        industry_map = None
    return {
        "closes_eval": closes_eval,
        "vol20": vol20,
        "mkt_cap_w": mkt_cap_w,
        "rets60_mean": rets60_mean,
        "rets60_var": rets60_var,
        "industry_map": industry_map,
        "daily_net_returns": daily_net_returns,
        "run_backtest": run_backtest,
    }


def collect_tier_sharpes(
    recipes: list,
    start: str,
    end: str,
    max_points: int,
    timing: bool = True,
) -> dict:
    """同格复算五档 sharpe——一次 evaluate_recipe + 一次全档扫描，轻/全指标同源派生。

    Returns:
        {light_scores, full_scores, gross_scores, per_point_full_s, per_point_light_s,
         full_tiers, eval_skipped, details}
    """
    from zephyr.backtest.regime_validation.exam_cost_gate import run_cost_tier_scan

    executor = _load_executor()
    full_tiers = tuple(float(t) for t in executor._load_cost_gate_tiers())  # 全档真源（禁双头）
    panel = _rebuild_panel(executor, start, end)
    closes_eval: pd.DataFrame = panel["closes_eval"]
    universe_cache: dict[str, set[str]] = {}
    factors_cache: dict[str, dict[str, pd.DataFrame]] = {}
    slice_cache: dict[str, tuple[pd.DataFrame, pd.DataFrame]] = {}

    light_scores: dict[str, float] = {}
    full_scores: dict[str, float] = {}
    gross_scores: dict[str, float] = {}
    details: dict[str, dict] = {}
    eval_skipped = 0
    t_full = t_light = 0.0
    n_timed = 0

    for r in recipes[: int(max_points)]:
        g = r.values["G_universe"]
        if g not in universe_cache:
            try:
                universe_cache[g] = executor._load_universe(g, start, end)
            except Exception:  # noqa: BLE001 与 run_batch 同口径: 记跳过计数，禁静默吞格点
                eval_skipped += 1
                continue
        cols = [c for c in universe_cache[g] if c in closes_eval.columns]
        if len(cols) < 30:
            eval_skipped += 1
            continue
        if g not in factors_cache:
            closes_g = closes_eval[cols]
            factors_cache[g] = executor.compute_v1_factors(closes_g)
            slice_cache[g] = (closes_g, panel["vol20"][cols])
        closes_g, vol20_g = slice_cache[g]
        try:
            weights, _degraded = executor.evaluate_recipe(
                r,
                closes_g,
                factors_cache[g],
                vol20_g,
                cols,
                mkt_cap_w=panel["mkt_cap_w"],
                rets60_mean=panel["rets60_mean"],
                rets60_var=panel["rets60_var"],
                industry_map=panel["industry_map"],
            )
        except Exception:  # noqa: BLE001 求值失败格点跳过（对拍只在成功格上比较）
            eval_skipped += 1
            continue
        sharpes = run_cost_tier_scan(weights, closes_g, panel["daily_net_returns"], tiers_bp=full_tiers)
        light = {bp: sharpes[bp] for bp in LIGHT_TIERS_BP if bp in sharpes}
        if len(light) != len(LIGHT_TIERS_BP):
            raise RuntimeError(f"全档扫描缺轻档 {LIGHT_TIERS_BP}: {sorted(sharpes)}——档位口径漂移")
        light_scores[r.recipe_id] = light[max(LIGHT_TIERS_BP)]  # 轻档主目标=5bp 成本后
        full_scores[r.recipe_id] = sharpes[max(full_tiers)]  # 全档主目标=40bp 全成本档
        gross_scores[r.recipe_id] = sharpes[0.0]  # 0bp 零成本对照（观察项）
        details[r.recipe_id] = {"tier_sharpes": sharpes}
        if timing:
            t0 = time.perf_counter()
            run_cost_tier_scan(weights, closes_g, panel["daily_net_returns"], tiers_bp=LIGHT_TIERS_BP)
            t_light += time.perf_counter() - t0
            t0 = time.perf_counter()
            run_cost_tier_scan(weights, closes_g, panel["daily_net_returns"], tiers_bp=full_tiers)
            t_full += time.perf_counter() - t0
            n_timed += 1
    return {
        "light_scores": light_scores,
        "full_scores": full_scores,
        "gross_scores": gross_scores,
        "full_tiers": list(full_tiers),
        "light_tiers": list(LIGHT_TIERS_BP),
        "eval_skipped": eval_skipped,
        "per_point_full_s": round(t_full / n_timed, 3) if n_timed else None,
        "per_point_light_s": round(t_light / n_timed, 3) if n_timed else None,
        "n_timed": n_timed,
        "details": details,
    }


def latest_run_dir() -> Path:
    """自动选 data/strategy_intake/grid_* 中最新含 manifest.csv 的 run。"""
    base = _REPO / "data" / "strategy_intake"
    candidates = sorted((d for d in base.glob("grid_*") if (d / "manifest.csv").exists()), key=lambda d: d.name)
    if not candidates:
        raise RuntimeError(f"{base} 下无含 manifest.csv 的 grid_* run——先有参考跑批再对拍")
    return candidates[-1]


def main() -> int:
    from zephyr.position.core.position_recipe_compiler import PositionRecipe

    ap = argparse.ArgumentParser(description="方案① 红蓝对拍: T1 轻档两档 vs 全档五档成本粗筛排名一致性标定")
    ap.add_argument("--run-dir", default="", help="参考 grid run 目录（缺省=自动选最新含 manifest 的 grid_*）")
    ap.add_argument("--n-points", type=int, default=100, help="对拍格点数（取 manifest 前 N; T0 全量=200）")
    ap.add_argument("--top-k", type=int, default=50, help="top-K 重合率窗口（默认 50）")
    ap.add_argument("--no-timing", action="store_true", help="跳过轻/全档单格耗时实测（省一半扫描量）")
    ap.add_argument("--out", default="", help="报告路径（缺省=.runtime/tmp/redblue_cost_tier_<run_ts>.json）")
    args = ap.parse_args()

    run_dir = Path(args.run_dir) if args.run_dir else latest_run_dir()
    manifest, window = load_reference_run(run_dir)
    start, end = window
    print(f"[redblue] 参考 run={run_dir.name} 窗口=[{start}, {end}] manifest 行数={len(manifest)}")

    recipes: list = []
    for _, row in manifest.iterrows():
        recipes.append(
            PositionRecipe(
                recipe_id=str(row["recipe_id"]),
                values=json.loads(row["values_json"]),
                folded_dimensions={},
                prefix_key=str(row.get("prefix_key", "")),
            )
        )
    result = collect_tier_sharpes(recipes, start, end, args.n_points, timing=not args.no_timing)
    agreement = rank_agreement(result["light_scores"], result["full_scores"], top_k=args.top_k)
    agreement_gross = rank_agreement(result["light_scores"], result["gross_scores"], top_k=args.top_k)

    report = {
        "run_dir": str(run_dir),
        "window": [start, end],
        "n_requested": int(args.n_points),
        "top_k": int(args.top_k),
        "light_vs_full": agreement,
        "light_vs_gross": agreement_gross,
        "per_point_light_s": result["per_point_light_s"],
        "per_point_full_s": result["per_point_full_s"],
        "n_timed": result["n_timed"],
        "eval_skipped": result["eval_skipped"],
        "full_tiers": result["full_tiers"],
        "light_tiers": result["light_tiers"],
        "reference_baseline": {"spearman": 1.0, "top50_overlap": "50/50", "note": "历史基准（03_gpu_campaign §三.4）"},
        "judgement_hint": "spearman>=0.99 且 top_k_overlap_pct>=0.9 → 轻档粗筛信息损失可忽略（参考线，非门禁）",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    out = Path(args.out) if args.out else _REPO / ".runtime" / "tmp" / f"redblue_cost_tier_{run_dir.name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({k: v for k, v in report.items() if k != "details"}, ensure_ascii=False, indent=2))
    print(f"[redblue] 报告已落 {out}")
    return 0


# noqa: m11-perm-manual-legitimate  红蓝对拍标定件: CLI 人工触发一次性标定作业（与 factory_grid_executor 同类），
# 非常驻永久系统（无常驻状态/无自动循环），每次调用为一次有界批处理
if __name__ == "__main__":
    raise SystemExit(main())
