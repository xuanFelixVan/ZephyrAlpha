# [BLUEPRINT] MOD-AUTO-L2-001(暂编号，解冻后转正) | docs/_working/automation/campaign/blueprints/promotion_combo_gate_blueprint.md | §
# [MODULE] scripts.backtest.promotion_combo_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.shared.io.file_utils
# [CONSUMERS] Owner 转正人工门（§7/§8 生命周期轴终站）; src/zephyr/strategy_pipeline/promotion_advisory（上游证据，只消费不改）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读生成（注册表/台账/CH 零写触碰）;
#   单策略证据缺失降级不阻断（沿 sim_promotion_memo 范式）;
#   组合门阈值预注册冻结（改阈值走标准库重考历史，见骨架 §8）;
#   建议≠决定——promote_ready 仍须 Owner 门
# [MODIFY-GUARD] 阈值变更须同步 tests 钉值+标准库登记
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] advisory 目录缺失=FileNotFoundError 上抛; CH 不可达→降级 evidence_gaps 不抛
# [TESTS] tests/backtest/test_promotion_combo_gate.py
# [A_module] module_id=MOD-AUTO-L2-001 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""promotion_combo_gate — 模拟盘准入组合门打分器 + 转正建议书渲染（骨架 v1.1 §7/§8 首件）。

消费已有件零重建：data/strategy_intake/promotion_advisories/*.json（MOD-BT-199 产出）
+ c1_backtest.strategy_screen（E4/SCR 考试成绩）+ c1_backtest.sim_pocket_daily / sim_trade_log（纸面账本）。

组合门阈值（Owner 草案预注册，出处 docs/_working/trading_vision/2026-09-16-owner-vision-system-mapping.md L57；
改阈值=修标，走标准库重考历史）：
  ①OOS Sharpe ≥ 1.5   ②最大回撤 ≤ 15%   ③容量证明（纸面成交≥30 笔且成本真实计提）   ④DSR > 0。
四条全过=promote_ready；任一硬败=reject；证据缺失（无法判定）=borderline（不冤枉也不放水）。

用法:
  python scripts/backtest/promotion_combo_gate.py                # 全量扫描 advisory
  python scripts/backtest/promotion_combo_gate.py --strategy-id S-XXX
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc, now_utc_str  # noqa: E402

logger = logging.getLogger(__name__)

ADVISORY_DIR = REPO_ROOT / "data" / "strategy_intake" / "promotion_advisories"
OUT_DIR = REPO_ROOT / "docs" / "_working" / "pipeline-research" / "promotion-reports"
THRESHOLD_SOURCE = "docs/_working/trading_vision/2026-09-16-owner-vision-system-mapping.md#L57"

THRESHOLDS = {
    "oos_sharpe_min": 1.5,
    "max_drawdown_max": 0.15,
    "min_trades": 30,
    "dsr_min": 0.0,
}


def load_advisories(advisory_dir: Path | None = None) -> list[dict]:
    d = Path(advisory_dir or ADVISORY_DIR)
    if not d.exists():
        raise FileNotFoundError(f"advisory 目录缺失: {d}")
    out = []
    for p in sorted(d.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("advisory 不可读 %s: %s", p.name, exc)
            continue
        if isinstance(data, dict):
            data.setdefault("_file", p.name)
            out.append(data)
    return out


def _query_screen(strategy_id: str) -> dict | None:
    """strategy_screen 最近一行（CH 不可达→None 降级）。"""
    try:
        from zephyr.data.ch_reader import query  # noqa: PLC0415

        rows = query(
            "SELECT is_sharpe, oos_sharpe, deflated_sharpe, num_trials, verdict FROM "
            "c1_backtest.strategy_screen WHERE strategy_id = {sid:String} "
            "ORDER BY created_at DESC LIMIT 1",
            params={"sid": strategy_id},
        )
        return rows[0] if rows else None
    except Exception as exc:  # noqa: BLE001 — CH 断连/模块缺失统一降级
        logger.info("strategy_screen 不可达（降级）: %s", exc)
        return None


def _query_pocket(strategy_id: str) -> dict | None:
    """纸面账本证据：最大回撤+成交笔数（CH 不可达→None 降级）。"""
    try:
        from zephyr.data.ch_reader import query  # noqa: PLC0415

        eq_rows = query(
            "SELECT total_equity FROM c1_backtest.sim_pocket_daily "
            "WHERE strategy_id = {sid:String} ORDER BY trade_date ASC",
            params={"sid": strategy_id},
        )
        cnt_rows = query(
            "SELECT count() FROM c1_backtest.sim_trade_log WHERE strategy_id = {sid:String}",
            params={"sid": strategy_id},
        )
        equities = [float(r["total_equity"]) for r in (eq_rows or [])]
        max_dd = _max_drawdown(equities)
        return {"max_drawdown": max_dd, "trades": int(cnt_rows[0]["count()"]) if cnt_rows else 0}
    except Exception as exc:  # noqa: BLE001
        logger.info("sim_pocket_daily/sim_trade_log 不可达（降级）: %s", exc)
        return None


def _max_drawdown(equities: list[float]) -> float | None:
    if len(equities) < 2:
        return None
    peak = equities[0]
    worst = 0.0
    for v in equities:
        peak = max(peak, v)
        if peak > 0:
            worst = max(worst, (peak - v) / peak)
    return worst


def _num(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def score_candidate(adv: dict, screen: dict | None, pocket: dict | None) -> dict:
    """组合门打分（纯函数，测试直喷）。证据缺失=unknown→borderline，不硬败。"""
    sid = str(adv.get("strategy_id") or adv.get("str_id") or adv.get("_file") or "unknown")
    checks: list[dict] = []

    def add(name: str, ok: bool | None, value, threshold, src: str, note: str = "") -> None:
        checks.append({"name": name, "ok": ok, "value": value, "threshold": threshold,
                       "source": src, "note": note})

    oos = _num((screen or {}).get("oos_sharpe")) or _num(adv.get("oos_sharpe"))
    add("oos_sharpe", (oos >= THRESHOLDS["oos_sharpe_min"]) if oos is not None else None,
        oos, THRESHOLDS["oos_sharpe_min"], "strategy_screen/advisory")

    dd = _num((pocket or {}).get("max_drawdown"))
    add("max_drawdown", (dd <= THRESHOLDS["max_drawdown_max"]) if dd is not None else None,
        dd, THRESHOLDS["max_drawdown_max"], "sim_pocket_daily")

    trades = _num((pocket or {}).get("trades"))
    add("capacity_trades", (trades >= THRESHOLDS["min_trades"]) if trades is not None else None,
        trades, THRESHOLDS["min_trades"], "sim_trade_log")

    dsr = _num((screen or {}).get("deflated_sharpe")) or _num(adv.get("deflated_sharpe"))
    add("dsr", (dsr > THRESHOLDS["dsr_min"]) if dsr is not None else None,
        dsr, f"> {THRESHOLDS['dsr_min']}", "strategy_screen")

    if any(c["ok"] is False for c in checks):
        verdict = "reject"
    elif any(c["ok"] is None for c in checks):
        verdict = "borderline"
    else:
        verdict = "promote_ready"
    return {
        "strategy_id": sid,
        "checks": checks,
        "verdict": verdict,
        "evidence_gaps": [c["name"] for c in checks if c["ok"] is None],
    }


def render_report(results: list[dict]) -> str:
    now = now_utc_str()
    lines = [
        "# 转正建议书（组合门打分）",
        "",
        f"- 生成: {now}（机生禁手改）",
        f"- 阈值出处: {THRESHOLD_SOURCE}（预注册冻结，修标走标准库重考历史）",
        f"- 扫描候选: {len(results)}",
        "",
        "| 候选 | OOS Sharpe | 最大回撤 | 成交笔数 | DSR | 裁定 |",
        "|------|-----------|---------|---------|-----|------|",
    ]
    for r in results:
        cells = []
        for c in r["checks"]:
            v = "缺证" if c["ok"] is None else c["value"]
            cells.append(f"{v}")
        lines.append(f"| {r['strategy_id']} | " + " | ".join(cells) + f" | **{r['verdict']}** |")
    lines.append("")
    for r in results:
        lines.append(f"## {r['strategy_id']} — {r['verdict']}")
        for c in r["checks"]:
            state = {True: "PASS", False: "FAIL", None: "GAP"}[c["ok"]]
            lines.append(f"- [{state}] {c['name']}: value={c['value']} threshold={c['threshold']} (source={c['source']})")
        if r["evidence_gaps"]:
            lines.append(f"- 证据缺口: {','.join(r['evidence_gaps'])}（borderline=继续观察，不冤枉不放水）")
        rec = {
            "promote_ready": "建议：提交转正评审（Owner 门终裁）",
            "reject": "建议：驳回（组合门硬败项见上）",
            "borderline": "建议：继续模拟观察，补齐证据缺口后重跑",
        }[r["verdict"]]
        lines.append(f"- **{rec}**")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="模拟盘准入组合门打分器+转正建议书渲染")
    ap.add_argument("--advisory-dir", type=str, default=None)
    ap.add_argument("--strategy-id", type=str, default=None, help="只评指定策略")
    ap.add_argument("--out-dir", type=str, default=None)
    ap.add_argument("--dry-run", action="store_true", help="只打印不落盘")
    args = ap.parse_args()

    advisories = load_advisories(args.advisory_dir)
    if args.strategy_id:
        target = _safe_id(args.strategy_id)
        advisories = [a for a in advisories
                      if str(a.get("strategy_id") or a.get("str_id") or "") == target]
    results = []
    for adv in advisories:
        sid = str(adv.get("strategy_id") or adv.get("str_id") or adv.get("_file") or "unknown")
        results.append(score_candidate(adv, _query_screen(sid), _query_pocket(sid)))
    report = render_report(results)
    if args.dry_run:
        print(report)
        return 0
    out_dir = Path(args.out_dir) if args.out_dir else OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = now_utc().strftime("%Y%m%d-%H%M%S")
    out = out_dir / f"promotion-report-{stamp}.md"
    expected = content_sha256(out.read_text(encoding="utf-8")) if out.exists() else None
    safe_write_text(out, report, expected_base_sha256=expected)
    print(json.dumps({"ok": True, "out": str(out), "candidates": len(results),
                      "verdicts": {r["strategy_id"]: r["verdict"] for r in results}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
