# [BLUEPRINT] MOD-REGIME-007 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [MODULE] scripts.backtest.alg01_ab_redo
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.regime_feature_builder; zephyr.regime.core.regime_detector; numpy; pandas
# [CONSUMERS] Owner/施工班（ALG-01 转正评估证据产出；裁定#257④ ALG2-3）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 双臂唯一差异=enable_cross_sectional；臂配置=生产配置（full+overlay+phase2c）；
#              指标含事件检出力对照（2024-02 微盘踩踏/2025-04 关税冲击窗）与 NAV 对照；
#              全程只读 CH，产出=markdown 报告（禁写库）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一臂 schedule 为空→RuntimeError（fail-closed，禁半份报告）
# [TESTS] 手动实弹（CH 依赖重，不进 CI）；逻辑面由 tests/regime/test_cross_sectional_features.py 覆盖
# [A_module] module_id=MOD-REGIME-007-ab | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# TTL 注记：裁定#257④ ALG-01 转正评估对照实验件；重跑=手动实弹（诊断工具非生产常驻）
"""ALG-01 横截面特征 A/B 重做（可复现版，裁定#257④ ALG2-3）。

旧 A/B（docs/_archive/2026-08-22-alg01-cross-sectional-ab.md）三重方法学缺陷：
生成脚本不存在（不可复现）、臂配置≠生产配置（简化管线）、只测"一致性"不测
"检出力"。本脚本一次到位：

1. 可复现：本脚本即生成代码，参数全 CLI 化，输出含完整配置回显。
2. 臂=生产配置：双臂均 full+overlay+phase2c（对齐 print_regime_history 生产默认），
   唯一差异=enable_cross_sectional。
3. 检出力优先：报告含事件窗口两臂对照——
   - 2024-02 微盘踩踏（模块立项要抓的目标事件，池修复后应可见）
   - 2025-04 关税冲击（第二事件窗）
   指标=窗口内两臂 schedule 均值/最小值、|Δ|、横截面 4 特征在事件峰值的
   trailing-250 日分位。
4. NAV 对照：schedule_{t-1}×指数日收益 的策略 NAV vs 买入持有（诊断口径，
   非认证回测，标签明示）。

用法：
    python scripts/backtest/alg01_ab_redo.py \
        --start 2024-01-01 --end 2026-06-30 \
        --load-start 2019-01-01 --detect-window 60 \
        --out docs/_working/alg01
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from zephyr.regime.core.regime_detector import RegimeDetector
from zephyr.regime.features.regime_data_loader import RegimeDataLoader
from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder

logger = logging.getLogger("alg01_ab_redo")

# NAV 基准指数收盘（NO-BARE-SQL 豁免前缀）
_SQL_INDEX_CLOSE = "SELECT trade_date, toFloat64(close) FROM {table} WHERE symbol='000300' ORDER BY trade_date"

# 事件窗（检出力对照；ALG2-1/ALG2-3 裁定口径）
EVENT_WINDOWS: list[tuple[str, str, str]] = [
    ("2024-02 微盘踩踏", "2024-01-15", "2024-03-15"),
    ("2025-04 关税冲击", "2025-04-01", "2025-04-30"),
]


def _run_arm(name: str, *, start: str, end: str, load_start: str, detect_window: int,
             train_years: int, cross: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    """跑一臂 walk-forward，返回 (schedule_df, features)。"""
    data_loader = RegimeDataLoader(data_load_start=load_start, backtest_end=end)
    builder = RegimeFeatureBuilder(
        backtest_start=start,
        backtest_end=end,
        data_load_start=load_start,
        enable_full_risk=True,     # 生产配置（ALG2-3②：臂=生产）
        enable_overlay=True,
        enable_phase2c=True,
        enable_cross_sectional=cross,
        data_loader=data_loader,
    )
    detector = RegimeDetector(shrinkage_enabled=True)
    schedule = builder.build_shrinkage_schedule(
        detector, train_years=train_years, detect_window=detect_window
    )
    if not schedule:
        raise RuntimeError(f"{name} 臂 schedule 为空（fail-closed，禁半份报告）")
    sdf = pd.DataFrame(sorted(schedule.items()), columns=["date", "schedule"]).set_index("date")
    return sdf, builder.build_features()


def _event_stats(sched: pd.DataFrame, feats: pd.DataFrame, ev_start: str, ev_end: str,
                 cs_cols: list[str]) -> dict:
    """单臂事件窗统计：schedule 均值/最小 + 横截面特征事件日值的 trailing 分位。"""
    win = sched.loc[ev_start:ev_end, "schedule"]
    out: dict = {
        "schedule_mean": float(win.mean()) if len(win) else float("nan"),
        "schedule_min": float(win.min()) if len(win) else float("nan"),
    }
    for col in cs_cols:
        if col not in feats.columns:
            continue
        s = feats[col].dropna()
        if s.empty:
            continue
        ev_vals = s.loc[ev_start:ev_end]
        if ev_vals.empty:
            continue
        peak_date = ev_vals.abs().idxmax()
        hist = s.loc[:peak_date].tail(250)
        out[f"{col}_peak"] = float(ev_vals.loc[peak_date])
        out[f"{col}_peak_pctile250d"] = float((hist < ev_vals.loc[peak_date]).mean())
    return out


def _nav(sched: pd.DataFrame, end: str) -> dict:
    """NAV 对照（诊断口径）：pos=1-schedule（低收缩=多头暴露），次日 000300 收益。"""
    import io

    from zephyr.data.ch_reader import query
    from zephyr.data.table_registry import get_registry

    ki = get_registry().table("market_index_kline")
    raw = query(_SQL_INDEX_CLOSE.format(table=ki))
    idx = pd.read_csv(io.StringIO(raw), sep="\t", names=["date", "close"])
    idx["date"] = pd.to_datetime(idx["date"])
    ret = idx.set_index("date")["close"].pct_change(fill_method=None).dropna()
    ret = ret.loc[(ret.index >= sched.index.min()) & (ret.index <= end)]
    pos = (1.0 - sched["schedule"]).reindex(ret.index).shift(1).fillna(0.0)
    strat = (1.0 + pos * ret).cumprod()
    bh = (1.0 + ret).cumprod()

    def _mdd(series: pd.Series) -> float:
        return float((series / series.cummax() - 1.0).min())

    return {
        "strat_total_return": float(strat.iloc[-1] - 1.0),
        "bh_total_return": float(bh.iloc[-1] - 1.0),
        "strat_max_drawdown": _mdd(strat),
        "bh_max_drawdown": _mdd(bh),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="ALG-01 A/B 重做（可复现+检出力版）")
    ap.add_argument("--start", default="2024-01-01")
    ap.add_argument("--end", default="2026-06-30")
    ap.add_argument("--load-start", default="2018-06-01")  # 覆盖 2024-02 检出窗（首季界 2023-09）
    ap.add_argument("--train-years", type=int, default=5)
    ap.add_argument("--detect-window", type=int, default=60)
    ap.add_argument("--out", default="docs/_working/alg01")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

    logger.info("A 臂（cross=off）walk-forward ...")
    sched_a, feats_a = _run_arm(
        "A", start=args.start, end=args.end, load_start=args.load_start,
        detect_window=args.detect_window, train_years=args.train_years, cross=False,
    )
    logger.info("B 臂（cross=on，全市场池+hfq）walk-forward ...")
    sched_b, feats_b = _run_arm(
        "B", start=args.start, end=args.end, load_start=args.load_start,
        detect_window=args.detect_window, train_years=args.train_years, cross=True,
    )

    cs_cols = ["cross_dispersion", "avg_pairwise_corr", "vol_dispersion", "momentum_breadth"]
    joined = sched_a.join(sched_b, how="inner", lsuffix="_a", rsuffix="_b")
    joined["abs_diff"] = (joined["schedule_a"] - joined["schedule_b"]).abs()
    corr = float(joined["schedule_a"].corr(joined["schedule_b"]))

    lines: list[str] = []
    lines.append("# ALG-01 A/B 重做报告（可复现+检出力版）\n")
    lines.append("> 裁定#257④ ALG2-3；生成=scripts/backtest/alg01_ab_redo.py（本报告的生成代码）\n")
    lines.append("## 0 配置回显（复现命令）\n")
    lines.append(f"- 窗口: [{args.start}, {args.end}]，load_start={args.load_start}，"
                 f"train_years={args.train_years}，detect_window={args.detect_window}")
    lines.append("- 双臂=生产配置 full+overlay+phase2c；B 臂=+enable_cross_sectional"
                 "（池=全市场 quality_flag=1，收益=hfq close×adj_factor）\n")
    lines.append("## 1 一致性（降位为辅助指标）\n")
    lines.append(f"- 两臂 schedule Pearson={corr:.4f}，|Δ|均值={joined['abs_diff'].mean():.4f}，"
                 f"|Δ|max={joined['abs_diff'].max():.4f}\n")
    lines.append("## 2 事件检出力对照（核心指标）\n")
    lines.append("A 臂无横截面列（开关关）记 nan；schedule 在 walk-forward 首窗前记 nan。\n")
    lines.append("| 事件窗 | 指标 | A 臂(off) | B 臂(on) |")
    lines.append("|---|---|---|---|")
    for name, s, e in EVENT_WINDOWS:
        sa = _event_stats(sched_a, feats_a, s, e, cs_cols)
        sb = _event_stats(sched_b, feats_b, s, e, cs_cols)
        keys = ["schedule_mean", "schedule_min"] + [f"{c}_peak_pctile250d" for c in cs_cols]
        for k in keys:
            va = sa.get(k, float("nan"))
            vb = sb.get(k, float("nan"))
            lines.append(f"| {name} | {k} | {va:.4f} | {vb:.4f} |")
    lines.append("")
    lines.append("## 3 NAV 对照（诊断口径，非认证回测；000300 多头×(1-schedule) 次日暴露）\n")
    nav_a = _nav(sched_a, args.end)
    nav_b = _nav(sched_b, args.end)
    lines.append(f"- A 臂: {json.dumps(nav_a, ensure_ascii=False)}")
    lines.append(f"- B 臂: {json.dumps(nav_b, ensure_ascii=False)}\n")
    lines.append("## 4 结论模板（按数字填）\n")
    lines.append("- B 臂在 2024-02 微盘踩踏窗的 momentum_breadth 事件峰分位是否显著低于 "
                 "A 臂（池修复后目标事件应可见）；vol_dispersion 分位是否抬升；"
                 "schedule_min 是否下探（危机确认更充分）。")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.date.today().isoformat()
    out_path = out_dir / f"{stamp}-alg01-ab-redo.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("报告已写: %s", out_path)


if __name__ == "__main__":
    main()
