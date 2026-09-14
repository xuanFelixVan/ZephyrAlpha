# [BLUEPRINT] MOD-BT-197 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.factory_grid_anova
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factory_grid_executor
# [CONSUMERS] 结构知识报告（立项稿 §十三 硬指标：维度重要性表+显著交互+可砍维度清单）；批次 B 子空间压缩
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只消费非降级格点（degraded 结果剔除防污染结构知识）；主效应占比=组间方差/总方差（正交抽样精确解）；交互=二维组间方差−两主效应（增量语义）；方法=经典 ANOVA 引方法不引代码（fanova license 非商业限制，裁定记录 §十四-9）
# [MODIFY-GUARD] tests/backtest/test_factory_grid_anova.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(输入不足/降级格点未剔除)
# [TESTS] tests/backtest/test_factory_grid_anova.py
# [A_module] module_id=MOD-BT-197 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""F-06 结构知识——经典 ANOVA 方差分解（MOD-BT-197，立项稿 §十三/§十四-9）。

输入 = 批次 A manifest（配方矩阵, 绩效 sharpe）。全因子网格下主效应/交互效应
可直接用经典 ANOVA 方差分解精确计算（Hutter 2014 的随机森林替代模型为散点
采样设计；我们分层抽样近似正交，组间方差分解即精确主效应）。

产出三件套（缺一不算完成，立项稿 §十三）:
  1. 维度重要性表（每维主效应方差占比）
  2. 显著交互清单（二维交互增量占比 ≥ 阈值）
  3. 可砍维度清单（主效应占比+交互贡献合计 < 砍维阈值的维度）

用法: python scripts/backtest/factory_grid_anova.py --manifest data/strategy_intake/grid_<ts>/manifest.csv
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import pandas as pd

# 砍维阈值: 主效应+全部交互贡献合计低于此占比 → 可砍（信息量≈0）
PRUNE_THRESHOLD = 0.005
# 显著交互阈值: 交互增量占比
INTERACTION_THRESHOLD = 0.01
# 离散绩效分箱（sharpe 连续值→组间分解需要组；用五分位）
PERF_QUANTILES = 5


def load_manifest(manifest_csv: str | Path) -> pd.DataFrame:
    """读 manifest 并剔除降级格点（降级结果混入会污染结构知识——fail-closed）。"""
    df = pd.read_csv(manifest_csv)
    if "degraded_dimensions" not in df.columns or "sharpe" not in df.columns:
        raise ValueError("manifest 缺少 degraded_dimensions/sharpe 列")
    clean = df[df["degraded_dimensions"].isna() | (df["degraded_dimensions"].astype(str) == "[]")].copy()
    if len(clean) < 50:
        raise ValueError(f"非降级格点不足 50（当前 {len(clean)}）——批次 A 规模不足以支撑结构知识")
    clean["perf_bin"] = pd.qcut(clean["sharpe"], q=PERF_QUANTILES, labels=False, duplicates="drop")
    return clean


def _parse_values(df: pd.DataFrame) -> pd.DataFrame:
    """values_json → 各维度列。"""
    import json

    parsed = df["values_json"].apply(json.loads).apply(pd.Series)
    return pd.concat([df[["recipe_id", "sharpe", "perf_bin"]].reset_index(drop=True),
                      parsed.reset_index(drop=True)], axis=1)


def _between_var(groups: pd.Series, y: pd.Series) -> float:
    """组间方差 Σ n_g (mean_g - mean)² / n —— 主效应的分子（总方差分母统一在外）。"""
    overall = y.mean()
    gm = y.groupby(groups).agg(["count", "mean"])
    return float((gm["count"] * (gm["mean"] - overall) ** 2).sum() / len(y))


def importance_table(df: pd.DataFrame, dims: list[str]) -> pd.DataFrame:
    """维度重要性表：主效应组间方差占比（降序）。"""
    total_var = float(df["sharpe"].var())
    rows = []
    for d in dims:
        if d not in df.columns:
            continue
        between = _between_var(df[d], df["sharpe"])
        rows.append({"dimension": d, "main_effect_ratio": between / total_var if total_var > 0 else 0.0})
    return pd.DataFrame(rows).sort_values("main_effect_ratio", ascending=False).reset_index(drop=True)


def interaction_table(df: pd.DataFrame, dims: list[str], top_main: list[str],
                      max_pairs: int = 40) -> pd.DataFrame:
    """二维交互增量 = Var(E[y|d1,d2]) − Var(E[y|d1]) − Var(E[y|d2])，占比降序。

    交互对只在双方主效应都进 top_main（前 6 维）里找——78 对全算会稀释显著性。
    """
    total_var = float(df["sharpe"].var())
    main_ratio = {d: _between_var(df[d], df["sharpe"]) / total_var for d in top_main}
    rows = []
    for d1, d2 in combinations(top_main, 2):
        pair = df.groupby([d1, d2])["sharpe"].transform("mean")
        between_pair = float(((pair - df["sharpe"].mean()) ** 2).mean())
        inter = between_pair / total_var - main_ratio[d1] - main_ratio[d2]
        rows.append({"dim_1": d1, "dim_2": d2, "interaction_ratio": round(inter, 6)})
    out = pd.DataFrame(rows).sort_values("interaction_ratio", ascending=False)
    return out.head(max_pairs).reset_index(drop=True)


def prunable_dims(importance: pd.DataFrame, interactions: pd.DataFrame) -> list[dict]:
    """可砍维度: 主效应+该维参与的全部交互合计 < PRUNE_THRESHOLD。"""
    inter_sum = {}
    for _, r in interactions.iterrows():
        for k in (r["dim_1"], r["dim_2"]):
            inter_sum[k] = inter_sum.get(k, 0.0) + max(float(r["interaction_ratio"]), 0.0)
    out = []
    for _, r in importance.iterrows():
        total = float(r["main_effect_ratio"]) + inter_sum.get(r["dimension"], 0.0)
        if total < PRUNE_THRESHOLD:
            out.append({"dimension": r["dimension"],
                        "main_ratio": round(float(r["main_effect_ratio"]), 6),
                        "interaction_sum": round(inter_sum.get(r["dimension"], 0.0), 6),
                        "total_ratio": round(total, 6)})
    return out


def run_anova(manifest_csv: str | Path, out_dir: str | Path | None = None) -> dict:
    """结构知识主入口：三件套产出。"""
    df = _parse_values(load_manifest(manifest_csv))
    meta_dims = ["recipe_id", "sharpe", "perf_bin"]
    dims = [c for c in df.columns if c not in meta_dims]
    imp = importance_table(df, dims)
    top_main = imp.head(6)["dimension"].tolist()
    inter = interaction_table(df, dims, top_main)
    significant = inter[inter["interaction_ratio"] >= INTERACTION_THRESHOLD]
    prunable = prunable_dims(imp, inter)
    report = {
        "manifest": str(manifest_csv),
        "n_recipes_used": len(df),
        "degraded_excluded": True,
        "importance": imp.to_dict(orient="records"),
        "significant_interactions": significant.to_dict(orient="records"),
        "prunable_dims": prunable,
        "thresholds": {"interaction": INTERACTION_THRESHOLD, "prune": PRUNE_THRESHOLD},
    }
    if out_dir is not None:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "structure_knowledge.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="F-06 结构知识 ANOVA")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()
    report = run_anova(args.manifest, args.out_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


# noqa: m11-perm-manual-legitimate  F-06 批处理跑批件: CLI 手动/计划任务触发与 c4_batch_screen 同类，
# 非常驻永久系统（无常驻状态/无自动循环），每次调用为一次有界批处理作业
if __name__ == "__main__":
    raise SystemExit(main())
