# [BLUEPRINT] MOD-BT-IBT-REEXAM | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.exam_cost_reexam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/backtest/ibt/ibt_mining_matrix; scripts/backtest/translated/_c4_engine; zephyr.backtest.regime_validation.exam_cost_gate; pandas
# [CONSUMERS] 批C 照妖镜验收（4440 必拦+成本合格名单）；批D 新鲜窗重考（同一机械）；批F 搜索轨成本门
# [STARTUP] manual CLI
# [MATURITY] experimental
# [INVARIANTS] E4 存活池逐条重过成本门（五档滑点单调性+全成本档存活+E7 换手≤8x 预注册档，config/exam_scale_cost_gate.yaml 冻结）；池清单单一真源=ibt_mining_matrix.POOL（禁复制）；引擎口径唯一=_c4_engine 冻结土规（滑点档覆盖仅侧向扫描）；裁定#325 口径逐条出数字证据禁"全绿"；fail-closed 证据不足判不通过；4440（超短）必须被本门拦截=照妖镜验收判据；不接实盘不下单
# [MODIFY-GUARD] none（名单产物 yaml 逐批冻结，改名单=重跑非手改）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(池文件缺失)；单策略失败记入名单 err/INSUFFICIENT 字段不中断全池
# [TESTS] none（门判定逻辑 tests/backtest/test_exam_cost_gate.py 覆盖；本件=编排面，照妖镜 4440 判据即其验收）
# [TTL] permanent
# [A_module] module_id=MOD-BT-IBT-REEXAM | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""E4 存活池成本门重考 runner（批C 照妖镜 / 批D 新鲜窗机械，MOD-BT-IBT-REEXAM）.

对 E4 存活池（单一真源=ibt_mining_matrix.POOL，17 条含 2 死刑参照）逐条:
  build(start,end) 权重+价格 → _c4_engine 冻结土规回测（换手/天数）
  → 五档滑点扫描（exam_cost_gate.run_cost_tier_scan）
  → 三道门判定（单调性+全成本档存活+E7 换手≤8x 预注册档）
产出: docs/_working/integrated_backtest/cost_qualified_list.yaml
      （逐条判定+成本合格名单；照妖镜判据=4440 必拦）
用法:
  python scripts/backtest/exam_cost_reexam.py --window 2020-01-01 2025-08-31
  python scripts/backtest/exam_cost_reexam.py --window 2025-09-01 2026-09-19 --tag fresh  # 批D 新鲜窗
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "backtest" / "translated"))
sys.path.insert(0, str(ROOT / "scripts" / "backtest" / "ibt"))

import pandas as pd  # noqa: E402

OUT_DEFAULT = ROOT / "docs" / "_working" / "integrated_backtest" / "cost_qualified_list.yaml"


def _load_cost_config():
    """预注册参数（config/exam_scale_cost_gate.yaml 冻结档；缺省=模块默认）。"""
    import yaml

    from zephyr.backtest.regime_validation.exam_cost_gate import CostGateConfig

    cfg_path = ROOT / "config" / "exam_scale_cost_gate.yaml"
    if not cfg_path.exists():
        return CostGateConfig()
    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    cg = raw.get("cost_gate") or {}
    tg = raw.get("turnover_gate") or {}
    return CostGateConfig(
        tiers_bp=tuple(cg.get("tiers_bp", CostGateConfig().tiers_bp)),
        survival_floor=float(cg.get("survival_floor", CostGateConfig().survival_floor)),
        monotonic_tol=float(cg.get("monotonic_tol", CostGateConfig().monotonic_tol)),
        min_days=int(cg.get("min_days", CostGateConfig().min_days)),
        turnover_cap_annual_x=float(tg.get("cap_annual_x", CostGateConfig().turnover_cap_annual_x)),
        turnover_days_basis=int(tg.get("days_basis", CostGateConfig().turnover_days_basis)),
    )


def _norm_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """面板归一：时间索引+裸码列（与 ibt_runner 同款纪律）。"""
    frame.index = pd.to_datetime(pd.Index(frame.index))
    frame.columns = [str(c).split(".")[0] for c in frame.columns]
    return frame


def _run_pool(start: str, end: str, cfg) -> list[dict]:
    from _c4_engine import daily_net_returns, run_backtest  # 引擎口径唯一（冻结土规）
    from ibt_mining_matrix import POOL  # 池清单单一真源（禁复制）

    from zephyr.backtest.regime_validation.exam_cost_gate import (
        evaluate_exam_cost_gate,
        run_cost_tier_scan,
    )

    rows: list[dict] = []
    for sid, fname, dr in POOL:
        t0 = time.time()
        row: dict = {"strategy_id": sid, "file": fname, "death_row_ref": bool(dr)}
        try:
            spec = importlib.util.spec_from_file_location(
                f"reex_{sid}", ROOT / "scripts" / "backtest" / "translated" / fname
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            weights, closes = mod.build(start, end)
            weights = _norm_frame(weights).fillna(0.0)
            closes = _norm_frame(closes)
            if weights.empty or float(weights.abs().sum().sum()) <= 0:
                row.update({"verdict": "INSUFFICIENT", "reason": "窗内零信号", "wall_sec": round(time.time() - t0, 1)})
                rows.append(row)
                print(f"[{sid}] INSUFFICIENT 零信号", flush=True)
                continue
            stats = run_backtest(weights, closes)
            tier_sharpes = run_cost_tier_scan(weights, closes, daily_net_returns, cfg)
            v = evaluate_exam_cost_gate(
                tier_sharpes,
                mean_daily_turnover_1side=float(stats.get("avg_turnover_1side", 0.0)),
                days=int(stats.get("days", 0)),
                config=cfg,
            )
            row.update(
                {
                    "verdict": "COST_PASS" if v.passed else "COST_FAIL",
                    "annual_turnover_x": round(v.annual_turnover_x, 2)
                    if v.annual_turnover_x == v.annual_turnover_x
                    else None,
                    "tier_sharpes": {str(k): val for k, val in v.tier_sharpes.items()},
                    "monotonic": v.monotonic,
                    "full_cost_survived": v.full_cost_survived,
                    "turnover_within_cap": v.turnover_within_cap,
                    "frozen_caliber_sharpe": stats.get("sharpe"),
                    "reasons": list(v.reasons),
                    "wall_sec": round(time.time() - t0, 1),
                }
            )
            print(f"[{sid}] {row['verdict']} turnover={row['annual_turnover_x']}x", flush=True)
        except Exception as exc:  # noqa: BLE001
            row.update(
                {"verdict": "ERROR", "err": f"{type(exc).__name__}: {exc}", "wall_sec": round(time.time() - t0, 1)}
            )
            print(f"[{sid}] ERROR {exc}", flush=True)
        rows.append(row)
    return rows


def _record_ledger(tag: str, start: str, end: str, n_trials: int) -> str:
    """批F E7 防线：每次重考批次登记 N 账本（累计可审计试验数，DSR 分母浮动真源）。"""
    try:
        from zephyr.backtest.core.n_trial_ledger import TrialLedger

        ledger = TrialLedger()
        ledger.record_run(
            kind="exam_cost_reexam",
            batch_id=f"{tag}_{start}_{end}",
            n_trials=int(n_trials),
            note=f"st-ibt-remedy-cf-20260923 cost gate re-exam window={start}..{end}",
            recorded_by="st-ibt-remedy-cf-20260923",
        )
        return "recorded"
    except Exception as exc:  # noqa: BLE001 — 账本故障不阻断重考本体，但必须留痕
        return f"ledger_error: {type(exc).__name__}: {exc}"


def main() -> int:
    import yaml

    ap = argparse.ArgumentParser(description="E4 存活池成本门重考（照妖镜/批D 机械）")
    ap.add_argument("--window", nargs=2, default=["2020-01-01", "2025-08-31"], metavar=("START", "END"))
    ap.add_argument("--tag", default="exam_scale", help="名单标签（exam_scale/fresh）")
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--no-ledger", action="store_true", help="跳过 N 账本登记（默认登记，批F E7 防线）")
    args = ap.parse_args()
    start, end = args.window
    cfg = _load_cost_config()
    rows = _run_pool(start, end, cfg)

    # 死刑参照件（death_row_ref）一律不入名单——INVARIANTS 第 6 条"仅记录不参与名单"此前
    # 只有文字没有代码：FACT-4db4c41e（dr=True，turnover 0.1x 恰过成本门）实测漏进
    # docs/_working/integrated_backtest/cost_qualified_list.yaml 的 7 条名单（2026-09-23 复现）。
    qualified = [r["strategy_id"] for r in rows if r.get("verdict") == "COST_PASS" and not r.get("death_row_ref")]
    mirror = next((r for r in rows if "4440" in r["strategy_id"]), None)
    ledger_status = "skipped" if args.no_ledger else _record_ledger(args.tag, start, end, len(rows))
    out = {
        "schema": "exam_cost_reexam/v1",
        "tag": args.tag,
        "window": [start, end],
        "config": "config/exam_scale_cost_gate.yaml (批C 预注册冻结档: 五档单调+全成本存活+E7≤8x)",
        "caliber_note": "裁定#325 口径：逐条判档出数字证据，禁全绿表述；死刑参照件仅记录不参与名单",
        "n_trial_ledger": ledger_status,
        "pool_size": len(rows),
        "cost_qualified": qualified,
        "cost_qualified_n": len(qualified),
        "mirror_4440": {
            "verdict": mirror.get("verdict") if mirror else None,
            "annual_turnover_x": mirror.get("annual_turnover_x") if mirror else None,
            "blocked": bool(mirror and mirror.get("verdict") == "COST_FAIL"),
            "note": "照妖镜判据：4440 必须被成本门拦截（blocked=true 为过）",
        },
        "rows": rows,
    }
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(yaml.dump(out, allow_unicode=True, sort_keys=False, default_flow_style=False), encoding="utf-8")
    print(
        f"saved -> {dest} | qualified {len(qualified)}/{len(rows)} | 4440 blocked={out['mirror_4440']['blocked']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# noqa: m11-perm-manual-legitimate  存活池成本门重考批处理件: CLI 手动触发与 f06_e4_wfa_exam 同类，
# 非常驻永久系统（每次运行为一次封闭的全池成本门重考，无自动循环无守驻状态）
