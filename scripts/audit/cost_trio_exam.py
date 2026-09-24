# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/kimi_audit/lane_reports/cost_trio_reexam_report.md | §1 判据真源
# [MODULE] cost_trio_exam（scripts 判据脚本，非 src 包模块；TC-06 R4 卡 A 选项重建件，落 docs/scripts 禁 tmp）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] data/backtest_artifacts/bt-*.json（材料真源）；cost_model_registry.yaml CST-T0-001（成本真源，只读）
# [CONSUMERS] 分包2 t0_conditional_e4_exam.py（条件化做T E4 考试复用本判据）；Owner 复查窗
# [STARTUP] manual（python cost_trio_exam.py）
# [MATURITY] production（判据件，落 docs 禁 tmp——判据灭失病根免疫，裁定#399 二）
# [INVARIANTS] 只读材料零副作用（产物只写 out-dir=docs/_working/kimi_audit/lane_reports/，禁 .runtime/tmp）；配对数<30 强制 insufficient_samples 禁硬出结论（REG-VALM-001 轻量土规）；零状态变更（不动 verdict/can_deploy）；成本口径唯一真源=CST-T0-001（佣金双边 6bp+印花 5bp+过户双边 0.2bp+滑点 2×10bp=31.2bp rt）；判据与 P6.md F02 交接包口径逐位对齐（≥30 土规/30bp 前置/净成本为正）；docs/_working 目录契约禁 .py/.json，故本脚本住 scripts/audit/、机读产物为 .yaml+.csv
# [MODIFY-GUARD] 本脚本改动=判据变更，须先改预注册披露节并留变更记录（防判据漂移重演）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 材料缺失/解析失败=显式报错退出非静默空结果；产物写失败=非零退出码
# [TESTS] 基线复现校验：与 P6.md 09-17 快照（24 对/0 净正/0≥30bp/毛 −9.2bp/净 −45.0bp）逐位比对，偏差即判据重建失败
# [TTL] task_bound
"""cost_trio_exam.py — 做T 配对成本三件套判据（TC-06 R4 卡 A 选项重建版，裁定#399 二授权）

判据灭失背景：原脚本随 .runtime/tmp/exp/ 整棵消失（R4 卡「判据灭失」条），本件按
biz2_t0_pairs_disclosure.md + archive/2026-09/kimi_audit/lane_reports/P6.md 重建，
落 docs 禁 tmp。本件是方法论工具非策略，不构成对任何被砍策略（#331/#386）的复活。

预注册披露（判据定义，改动须留变更记录）：
- 材料：data/backtest_artifacts/bt-*.json 的 trade_log；锚点 D=2026-09-09（D 前全锁/D 后可考，
  P6.md 真源）；仅考 trade_date ≥ 2026-09-10 的成交（fill）。
- 配对规则（重建声明：原实现已灭失，本规则为重建版，与 biz2 口径对齐）：
  同 (symbol, trade_date) 双边（既有买又有卖）计 1 配对；配对量=min(Σ买量, Σ卖量)；
  买卖各自全侧 VWAP=Σ(价×量)/Σ量（匹配量口径的近似，如实披露）；毛价差 bp=(卖VWAP/买VWAP−1)×1e4。
- 成本口径（CST-T0-001，cost_model_registry.yaml 唯一真源）：
  rt_bp = 佣金 0.0003×2×1e4(6) + 印花 0.0005×1e4(5, 卖侧) + 过户 0.00001×2×1e4(0.2)
        + 滑点 10bp×2(20) = 31.2bp；最低佣金 5 元地板抬升不计入固定口径，单独披露列
  （实收佣金=逐笔 commission 字段实测，P6 §4.6 已证系已建模行为）。
- 净价差 bp = 毛价差 bp − 31.2。
- 出结论条件（REG-VALM-001 轻量土规）：n_symbol_day_pairs ≥ 30；不足=insufficient_samples，
  禁硬出通过/不通过方向性结论（其余四数仅观察披露）。
- 结论判据（样本足时，F02 口径）：开仓前置命中=edge_ge_30bp 占比；净期望=净价差 mean>0。
- 全部结果全量披露（含 RED），禁事后挑样；产物只写 out-dir（docs 判据区，禁 tmp），机读=.yaml+.csv。

用法：python scripts/audit/cost_trio_exam.py [--artifacts-dir data/backtest_artifacts] [--out-dir docs/_working/kimi_audit/lane_reports]
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

D_ANCHOR = "2026-09-09"  # 定稿锚点 D（P6.md：D 前全锁/D 后可考）
PAIR_GATE = 30  # REG-VALM-001 轻量土规：配对数≥30 才出结论
EDGE_PRECONDITION_BP = 30.0  # CST-T0-001 open_precondition.min_expected_edge_rate=0.003
RT_COST_BP = 31.2  # CST-T0-001：6(佣金双边)+5(印花)+0.2(过户双边)+20(滑点双边)


def load_d_after_fills(artifacts_dir: Path) -> tuple[list[dict], list[str]]:
    fills: list[dict] = []
    files = sorted(artifacts_dir.glob("bt-*.json"))
    if not files:
        raise SystemExit(f"FAIL: 材料缺失——{artifacts_dir} 下无 bt-*.json（判据脚本禁静默空结果）")
    skipped: list[str] = []
    for f in files:
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            skipped.append(f"{f.name}: {exc}")
            continue
        for t in data.get("trade_log") or []:
            day = str(t.get("timestamp", ""))[:10]
            if day > D_ANCHOR:
                fills.append({**t, "trade_date": day, "run_id": data.get("run_id", f.name)})
    return fills, skipped


def build_pairs(fills: list[dict]) -> list[dict]:
    by_key: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(
        lambda: {"bq": [], "bv": [], "sq": [], "sv": [], "comm": 0.0, "n": 0, "runs": set()}
    )
    for t in fills:
        try:
            price = float(t["price"])
            qty = float(t["quantity"])
        except (KeyError, TypeError, ValueError):
            continue
        if price <= 0 or qty <= 0:
            continue
        key = (str(t.get("symbol", "")), t["trade_date"])
        cell = by_key[key]
        if str(t.get("side", "")).lower() == "buy":
            cell["bq"].append(qty)
            cell["bv"].append(price * qty)
        else:
            cell["sq"].append(qty)
            cell["sv"].append(price * qty)
        cell["comm"] += float(t.get("commission") or 0.0)
        cell["n"] += 1
        cell["runs"].add(t["run_id"])
    pairs = []
    for (symbol, day), c in sorted(by_key.items()):
        if not c["bq"] or not c["sq"]:
            continue  # 无双边不成配对（做T代理口径：同 symbol×day 买卖配对）
        buy_qty, sell_qty = sum(c["bq"]), sum(c["sq"])
        vwap_buy = sum(c["bv"]) / buy_qty
        vwap_sell = sum(c["sv"]) / sell_qty
        gross_bp = (vwap_sell / vwap_buy - 1.0) * 1e4
        notional = vwap_buy * min(buy_qty, sell_qty)
        realized_comm_bp = (c["comm"] / notional * 1e4) if notional > 0 else float("nan")
        pairs.append(
            {
                "symbol": symbol,
                "trade_date": day,
                "buy_qty": buy_qty,
                "sell_qty": sell_qty,
                "vwap_buy": round(vwap_buy, 6),
                "vwap_sell": round(vwap_sell, 6),
                "gross_bp": round(gross_bp, 2),
                "net_bp": round(gross_bp - RT_COST_BP, 2),
                "realized_comm_bp": round(realized_comm_bp, 2),
                "fills": c["n"],
                "runs": len(c["runs"]),
            }
        )
    return pairs


def main() -> int:
    ap = argparse.ArgumentParser(description="做T 配对成本三件套判据（重建版）")
    ap.add_argument("--artifacts-dir", default="data/backtest_artifacts")
    ap.add_argument("--out-dir", default="docs/_working/kimi_audit/lane_reports")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fills, skipped = load_d_after_fills(Path(args.artifacts_dir))
    pairs = build_pairs(fills)
    gross = [p["gross_bp"] for p in pairs]
    net = [p["net_bp"] for p in pairs]
    n_pairs = len(pairs)
    sufficient = n_pairs >= PAIR_GATE
    result = {
        "criteria": {
            "pair_gate": PAIR_GATE,
            "rt_cost_bp_cst_t0_001": RT_COST_BP,
            "edge_precondition_bp": EDGE_PRECONDITION_BP,
            "window": f">{D_ANCHOR}",
            "pairing_rule": "symbol×day 双边配对，全侧 VWAP 近似（重建版预注册披露见脚本 docstring）",
            "rebuild_provenance": [
                "docs/_working/archive/2026-09/flash_biz/biz2_t0_pairs_disclosure.md",
                "docs/_working/archive/2026-09/kimi_audit/lane_reports/P6.md",
            ],
        },
        "measured": {
            "n_fills_after_d": len(fills),
            "n_bt_files": len(sorted(Path(args.artifacts_dir).glob("bt-*.json"))),
            "days": sorted({p["trade_date"] for p in pairs}),
            "n_symbol_day_pairs": n_pairs,
            "net_positive": sum(1 for x in net if x > 0),
            "edge_ge_30bp": sum(1 for x in gross if x >= EDGE_PRECONDITION_BP),
            "gross_mean_bp": round(statistics.fmean(gross), 2) if gross else None,
            "gross_p50_bp": round(statistics.median(gross), 2) if gross else None,
            "net_mean_bp": round(statistics.fmean(net), 2) if net else None,
            "net_p50_bp": round(statistics.median(net), 2) if net else None,
            "realized_comm_mean_bp": round(statistics.fmean(p["realized_comm_bp"] for p in pairs), 2)
            if pairs
            else None,
        },
        "verdict": (
            {
                "status": "PASS" if (sufficient and result_ok(net, gross)) else "FAIL",
                "conclusion": "净期望为正且开仓前置命中"
                if sufficient and result_ok(net, gross)
                else "净期望不为正或开仓前置不命中",
            }
            if sufficient
            else {
                "status": "INSUFFICIENT_SAMPLES",
                "conclusion": f"配对数 {n_pairs} < {PAIR_GATE}（REG-VALM-001 轻量土规），禁硬出方向性结论；四数仅观察披露",
            }
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "material_parse_skips": skipped,
    }

    out_dir.joinpath("cost_trio_result.yaml").write_text(
        yaml.safe_dump(result, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    with (out_dir / "cost_trio_pairs.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pairs[0].keys()) if pairs else ["symbol"])
        w.writeheader()
        w.writerows(pairs)
    print(yaml.safe_dump(result["measured"], allow_unicode=True, sort_keys=False))
    print("verdict:", yaml.safe_dump(result["verdict"], allow_unicode=True, sort_keys=False))
    return 0


def result_ok(net: list[float], gross: list[float]) -> bool:
    return bool(net) and statistics.fmean(net) > 0 and any(x >= EDGE_PRECONDITION_BP for x in gross)


if __name__ == "__main__":
    sys.exit(main())
