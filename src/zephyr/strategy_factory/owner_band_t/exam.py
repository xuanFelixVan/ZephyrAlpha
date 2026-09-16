# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_band_t.exam
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] itertools; json; pathlib; pandas; zephyr.strategy_factory.owner_band_t.engine; zephyr.strategy_factory.owner_band_t.data_loader
# [CONSUMERS] scripts/strategy_factory/run_s_owner_001_exam.py; docs/_working/factory/strategy_cards/（E4 出证报告数据源）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] IS 网格全记录（搜多少组报多少组，CSV 落档防只报最优）；OOS 单次通过（禁迭代/禁复试图救）；择优规则冻结=IS Sharpe 最大→MaxDD 浅→换手低；验收线四条 AND（冻结文档 §7）；三臂+基准缺一不可
# [MODIFY-GUARD] 验收线/窗口/网格域以冻结文档 e4_freeze_s_owner_001_300etf_band_t.md 为唯一真源
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(IS 无合格组)
# [TESTS] tests/strategy_factory/test_s_owner_001_exam.py
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""S-OWNER-001 E4 考试器——IS 网格全记录 + OOS 单次三臂归因 + 验收判定。

流程（冻结文档 §1~§7）:
  1. build_panel() 装载数据（自备 cache .runtime/tmp/sowner001_cache/）
  2. IS 2012-05-28..2023-12-31 全网格 432 组逐组回测，全记录落 CSV
  3. 冻结择优规则取 IS 最优组
  4. OOS 2024-01-01..2026-09-15 单次: A(全策略)/B(无门)/C(无做T)/基准 买入持有
  5. 验收线判定（全 AND）→ summary.json + is_grid_full.csv + nav 曲线 CSV
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any

import pandas as pd

from zephyr.strategy_factory.owner_band_t.engine import (
    LADDER_ALT,
    LADDER_DEFAULT,
    TRADING_DAYS_PER_YEAR,
    StrategyConfig,
    run_backtest,
    run_buy_and_hold,
)

IS_START = "2012-05-28"
IS_END = "2023-12-31"
OOS_START = "2024-01-01"
OOS_END = "2026-09-15"

#: 验收线（冻结文档 §7，禁改）
ACCEPT_SHARPE_MIN = 1.2
ACCEPT_MAXDD_FLOOR = -0.15  # maxdd 记负数（回撤幅度），须 >= -15%
ACCEPT_T_NET_MIN = 0.0  # 元
ACCEPT_TURNOVER_MAX = 60.0  # 单边年化换手

#: IS 网格（冻结文档 §5，3×3×3×2×2×2×2=432 组）
GRID: dict[str, list[Any]] = {
    "entry_mode": ["setup8", "setup9", "countdown_neg"],
    "p1": [0.5, 0.7, 0.9],
    "exit_arm": ["bb_upper", "prior_high", "return_quantile"],
    "ladder": [LADDER_DEFAULT, LADDER_ALT],
    "gate_min_conf": [0.35, 0.50],
    "t_max_trips": [1, 2],
    "t_size": [0.3, 0.5],
}
_GRID_FIELDS = ("entry_mode", "p1", "exit_arm", "ladder", "gate_min_conf", "t_max_trips", "t_size")


def iter_grid() -> list[StrategyConfig]:
    """展开冻结网格为配置列表（顺序固定，可复现）。"""
    keys = list(GRID.keys())
    configs = []
    for values in itertools.product(*(GRID[k] for k in keys)):
        kw = dict(zip(keys, values, strict=True))
        configs.append(StrategyConfig(**kw))
    return configs


def run_grid_is(panel: dict) -> pd.DataFrame:
    """IS 全网格逐组回测（全记录，防只报最优；单组失败如实记录不中断）。"""
    rows = []
    for k, cfg in enumerate(iter_grid()):
        try:
            res = run_backtest(panel, cfg, IS_START, IS_END)
            m = res["metrics"]
            years = m["n_days"] / TRADING_DAYS_PER_YEAR
            turnover_total = res["turnover_band"] + res["turnover_t"]
            rows.append(
                {
                    "combo_id": k,
                    **{f"cfg_{f}": getattr(cfg, f) for f in _GRID_FIELDS},
                    "is_sharpe": m["sharpe"],
                    "is_maxdd": m["maxdd"],
                    "is_ann_return": m["ann_return"],
                    "is_ann_turnover": turnover_total / max(float(res["nav"].mean()), 1e-9) / years,
                    "is_t_net_pnl": res["t_net_pnl"],
                    "is_t_trips": res["t_trips"],
                    "is_band_trades": res["n_band_trades"],
                    "is_exposure": res["exposure_ratio"],
                }
            )
        except Exception as exc:  # noqa: BLE001 —— 失败组留痕
            rows.append(
                {
                    "combo_id": k,
                    **{f"cfg_{f}": getattr(cfg, f) for f in _GRID_FIELDS},
                    "is_sharpe": float("nan"),
                    "is_error": f"{type(exc).__name__}: {exc}",
                }
            )
    return pd.DataFrame(rows)


def select_best(grid_df: pd.DataFrame) -> pd.Series:
    """冻结择优: IS Sharpe 最大 → MaxDD 更浅（更大）→ 换手更低。"""
    ok = grid_df[grid_df["is_sharpe"].notna()].copy()
    if ok.empty:
        raise RuntimeError("IS 网格全部失败——检查数据/引擎")
    ok = ok.sort_values(["is_sharpe", "is_maxdd", "is_ann_turnover"], ascending=[False, False, True])
    return ok.iloc[0]


def _arm_summary(res: dict) -> dict:
    m = res["metrics"]
    years = m["n_days"] / TRADING_DAYS_PER_YEAR
    turnover_total = res["turnover_band"] + res["turnover_t"]
    nav_mean = float(res["nav"].mean())
    return {
        "sharpe": m["sharpe"],
        "maxdd": m["maxdd"],
        "ann_return": m["ann_return"],
        "nav_end": float(res["nav"].iloc[-1]),
        "nav_mean": nav_mean,
        "n_days": m["n_days"],
        "ann_turnover": turnover_total / max(nav_mean, 1e-9) / years if years > 0 else 0.0,
        "t_net_pnl": res["t_net_pnl"],
        "t_trips": res["t_trips"],
        "turnover_band": res["turnover_band"],
        "turnover_t": res["turnover_t"],
        "turnover_total": turnover_total,
        "n_band_trades": res["n_band_trades"],
        "exposure_ratio": res["exposure_ratio"],
    }


def run_oos(panel: dict, best: pd.Series) -> dict[str, Any]:
    """OOS 单次: 三臂 + 基准（同一择优配置；每臂各跑一次，此后禁再触碰 OOS）。"""
    ladder = best["cfg_ladder"]
    if not isinstance(ladder, (list, tuple)):
        ladder = LADDER_DEFAULT
    base_kw = {
        "entry_mode": str(best["cfg_entry_mode"]),
        "p1": float(best["cfg_p1"]),
        "exit_arm": str(best["cfg_exit_arm"]),
        "ladder": tuple(ladder),
        "gate_min_conf": float(best["cfg_gate_min_conf"]),
        "t_max_trips": int(best["cfg_t_max_trips"]),
        "t_size": float(best["cfg_t_size"]),
    }
    arm_a = run_backtest(panel, StrategyConfig(**base_kw), OOS_START, OOS_END)
    arm_b = run_backtest(panel, StrategyConfig(**base_kw, use_gate=False), OOS_START, OOS_END)
    arm_c = run_backtest(panel, StrategyConfig(**base_kw, use_t=False), OOS_START, OOS_END)
    bench = run_buy_and_hold(panel, OOS_START, OOS_END)
    bench_summary = {**bench["metrics"], "nav_end": float(bench["nav"].iloc[-1]), "turnover_total": bench["turnover"]}
    navs = {
        "A_full": arm_a["nav"],
        "B_no_gate": arm_b["nav"],
        "C_no_t": arm_c["nav"],
        "benchmark_bh": bench["nav"],
    }
    return {
        "A_full": _arm_summary(arm_a),
        "B_no_gate": _arm_summary(arm_b),
        "C_no_t": _arm_summary(arm_c),
        "benchmark_bh": bench_summary,
        "navs": navs,
    }


def evaluate_acceptance(oos: dict) -> tuple[dict[str, dict], bool]:
    """验收线四条 AND（冻结线，禁改）。返回(逐条明细, 总判定)。"""
    a = oos["A_full"]
    checks = {
        "sharpe_ge_1.2": {"value": round(a["sharpe"], 4), "threshold": ACCEPT_SHARPE_MIN, "pass": a["sharpe"] >= ACCEPT_SHARPE_MIN},
        "maxdd_le_15pct": {"value": round(a["maxdd"], 4), "threshold": ACCEPT_MAXDD_FLOOR, "pass": a["maxdd"] >= ACCEPT_MAXDD_FLOOR},
        "t_net_gt_0": {"value": round(a["t_net_pnl"], 2), "threshold": ACCEPT_T_NET_MIN, "pass": a["t_net_pnl"] > ACCEPT_T_NET_MIN},
        "turnover_le_60x": {"value": round(a["ann_turnover"], 2), "threshold": ACCEPT_TURNOVER_MAX, "pass": a["ann_turnover"] <= ACCEPT_TURNOVER_MAX},
    }
    return checks, all(c["pass"] for c in checks.values())


def run_full_exam(out_dir: str | Path, panel: dict | None = None) -> dict[str, Any]:
    """完整考试: IS 全网格 → 择优 → OOS 单次三臂 → 验收 → 产物落档。"""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if panel is None:
        from zephyr.strategy_factory.owner_band_t.data_loader import build_panel

        panel = build_panel()

    grid_df = run_grid_is(panel)
    grid_df.to_csv(out / "is_grid_full.csv", index=False, encoding="utf-8-sig")
    best = select_best(grid_df)
    oos = run_oos(panel, best)
    checks, passed = evaluate_acceptance(oos)

    # OOS NAV 曲线留档（三臂+基准，图证）
    navs = oos.pop("navs")
    pd.DataFrame({k: v for k, v in navs.items()}).to_csv(out / "oos_nav_curves.csv", encoding="utf-8-sig")

    summary = {
        "exam": "S-OWNER-001 E4",
        "freeze_doc": "docs/_working/factory/strategy_cards/e4_freeze_s_owner_001_300etf_band_t.md",
        "windows": {"is": [IS_START, IS_END], "oos": [OOS_START, OOS_END], "oos_runs": 1},
        "grid_size": int(len(grid_df)),
        "grid_evaluated": int(grid_df["is_sharpe"].notna().sum()),
        "best_is": {
            "combo_id": int(best["combo_id"]),
            **{f: (list(best[f"cfg_{f}"]) if f == "ladder" else best[f"cfg_{f}"]) for f in _GRID_FIELDS},
            "is_sharpe": round(float(best["is_sharpe"]), 4),
            "is_maxdd": round(float(best["is_maxdd"]), 4),
            "is_ann_turnover": round(float(best["is_ann_turnover"]), 2),
            "is_t_net_pnl": round(float(best["is_t_net_pnl"]), 2),
        },
        "oos": oos,
        "acceptance": checks,
        "verdict": "PASS" if passed else "FAIL",
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return summary
