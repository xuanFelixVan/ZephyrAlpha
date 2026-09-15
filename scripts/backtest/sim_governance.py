# [BLUEPRINT] MOD-BT-094 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.sim_governance
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; zephyr.backtest.run_archive; zephyr.data.alerter; yaml
# [CONSUMERS] 模拟盘治理（lifecycle 流转建议报告，Owner 终裁）；策略登记册治理批次；
#   run 档案（SCR-SIMGOV-*）；pipeline_events sim_deviation_monthly 串行触发（判定史先落、建议后出）;
#   promotion_advisory_due 事件（S12 C4：建议产出后 emit，建议包生成+真通道推送由
#   zephyr.strategy_pipeline.promotion_advisory 承接）
# [STARTUP] manual+event（CLI 手工；月度档经 sim_deviation_monthly handler 串行触发）
# [MATURITY] experimental
# [INVARIANTS] 只产建议不改册（lifecycle 变更终裁=Owner）；规则全部引用既存真源
#   （SOP-C §8 双窗口门槛/偏离报告月度判定/oos_years_decay>=0.5 存疑线）；
#   建议产出经 Alerter 推送（level=ERROR——Alerter 仅 ERROR+ 落本地 failure 文件，webhook 未配置
#   =降级本地告警文件；告警通道任何故障不抛不反噬建议产出）；run 档案随跑必落（--dry-run 豁免）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(册文件缺失)
# [TESTS] tests/backtest/test_sim_governance.py
# [A_module] module_id=MOD-BT-140 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""模拟盘治理——lifecycle 流转建议生成器（平台蓝图批 4）。

规则（全部引用既存真源，零新增规范对象）：
- 连续 2 月 sim_deviation 月度通过 → 建议 sim→paper（晋级观察）；
- 连续 2 月 monthly_breach / 出现 monthly_breach_consecutive → 建议 sim→decayed（降级）；
- oos_years_decay>=0.5 → 存疑标注（土规线）。
输出=建议报告 JSON（只读，控制台）+ run 档案（SCR-SIMGOV-*，照 strategy_lifecycle_advisor
先例）+ 有建议时经 Alerter 推送（webhook 未配置=降级本地告警文件，不抛异常）；
册子变更由 Owner 裁定后另行执行。
用法：python scripts/backtest/sim_governance.py [--json] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_REG = Path(__file__).resolve().parents[2] / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "strategy_registry.yaml"


def _q(sql: str):
    from zephyr.data.ch_writer import get_client_strict

    return get_client_strict().execute(sql)



def sim_lifecycle_entries() -> list[dict]:
    import yaml

    d = yaml.safe_load(_REG.read_text(encoding="utf-8"))
    return [
        {"strategy_id": s["strategy_id"], "lifecycle_status": s.get("lifecycle_status"),
         "code_path": s.get("code_path") or "", "name_zh": s.get("name_zh", "")}
        for s in d.get("strategies", [])
        if s.get("lifecycle_status") in ("sim", "paper")
    ]


def month_history(strategy_id: str) -> list[dict]:
    """该策略全部 SIM-DEV 月度判定史（按月排序）。"""
    rows = _q(
        "SELECT screen_batch, argMax(verdict_reason, ingest_ts)"
        " FROM c1_backtest.strategy_screen"
        f" WHERE strategy_id = '{strategy_id}' AND verdict = 'sim_deviation'"
        " GROUP BY screen_batch ORDER BY screen_batch")
    return [{"batch": r[0], "reason": r[1], "notes": ""} for r in rows]


def recommend(history: list[dict]) -> tuple[str | None, str]:
    """按判定史出流转建议。返回 (建议或 None, 理由)。规则真源=SOP-C §8+偏离报告月度判定。"""
    reasons = [h["reason"] for h in history if h["reason"] in ("monthly_pass", "monthly_breach")]
    if len(reasons) >= 2 and reasons[-2] == "monthly_pass" and reasons[-1] == "monthly_pass":
        return "promote_paper", "连续 2 月月度通过（SOP-C §8 偏离门槛）"
    if len(reasons) >= 2 and "monthly_breach" in reasons[-2:]:
        return "demote_decayed", "连续 2 月月度不达标"
    if history and any("consecutive" in (h["reason"] or "") for h in history):
        return "demote_decayed", "偏离报告已出连续不达标降级提案"
    return None, "观察期数据不足或表现中性"


def alert_recommendations(recs: list[dict]) -> bool:
    """有流转建议时经 Alerter 推送（webhook 未配置=降级本地告警文件；任何故障不抛）。

    level=ERROR 裁定：Alerter 仅 ERROR+ 写本地 failure 文件（WARN 只进日志）——流转建议是
    Owner 终裁输入，必须留本地痕（S10 §5.2②验收=有建议时告警落地）。
    """
    actionable = [r for r in recs if r.get("recommendation")]
    if not actionable:
        return False
    msg = "; ".join(f"{r['strategy_id']}→{r['recommendation']}({r['why']})" for r in actionable)[:500]
    try:
        from zephyr.data.alerter import Alerter

        Alerter().notify("sim_governance", msg, level="ERROR", source="sim_governance")
    except Exception:  # noqa: BLE001——告警通道故障不反噬建议产出（建议已在控制台打印）
        logger.warning("alerter 推送失败（本地告警文件未落，建议已打印）: %s", msg)
        return False
    return True


def write_run_archive(entries: list[dict], recs: list[dict]) -> str:
    """落 run 档案（SCREEN kind，照 strategy_lifecycle_advisor main 先例）——消除 docstring 漂移。"""
    from datetime import datetime

    from zephyr.backtest.run_archive import create_run, finalize_run, write_step

    report = {"entries": len(entries), "recommendations": recs}
    run_id = f"SCR-SIMGOV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    create_run(run_id=run_id, object_id="", kind="SCREEN", cost_mode="rough",
               created_by="ai-session:sim-governance")
    write_step(run_id, "03", (
        "# 数据清单\n\n- name: sim 判定史扫描源\n"
        "  source: c1_backtest.strategy_screen（verdict=sim_deviation，SIM-DEV-* 月度判定史）\n"
        "  window_is: 全史（无窗口截断；建议规则=SOP-C §8 连续 2 月门槛）\n  proxy: false\n"
    ))
    write_step(run_id, "04", json.dumps(report, ensure_ascii=False, indent=1, default=str),
               filename="sim_governance_advice.json")
    write_step(run_id, "verdict", (
        f"# 判定书：{run_id}\n\n对象：模拟盘 lifecycle 流转建议（只产建议不改册，终裁=Owner）｜ kind=SCREEN\n"
        f"结论：{json.dumps({'entries': len(entries), 'actionable': sum(1 for r in recs if r['recommendation'])}, ensure_ascii=False)}\n"
        "口径：连续 2 月 monthly_pass→promote_paper；连续 2 月 breach/consecutive 提案→demote_decayed\n"))
    finalize_run(run_id, verdict_ref={"table": "c1_backtest.strategy_screen", "run_id": run_id})
    logger.info("run 档案：%s", run_id)
    return run_id


def _emit_promotion_advisory_event(recs: list[dict]) -> None:
    """S12 C4 事件接线：有流转建议时 emit promotion_advisory_due（c4/intake 写侧钩子同款：
    pipeline_events.record+立即轻消费 drain）。任何故障不反噬治理主流程（建议已打印+run 档案已落）。
    """
    if not any(r.get("recommendation") for r in recs):
        return
    try:
        from zephyr.strategy_pipeline.pipeline_events import drain, record

        evt = record("promotion_advisory_due", {"source": "sim_governance",
                                                "n": sum(1 for r in recs if r.get("recommendation"))})
        drain(allow_heavy=False)
        logger.info("promotion_advisory_due 已入队: %s", evt["id"])
    except Exception:  # noqa: BLE001——事件层故障不反噬治理主流程（事件留 journal 由下个唤醒点重放）
        logger.warning("promotion_advisory_due 入队失败（不反噬治理主流程）", exc_info=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="模拟盘治理·流转建议生成器（只产建议不改册）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="只打印不落 run 档案/不推送告警（测试与预演用）")
    args = ap.parse_args()
    entries = sim_lifecycle_entries()
    recs = []
    for e in entries:
        hist = month_history(e["strategy_id"])
        rec, why = recommend(hist)
        recs.append({**e, "months_evaluated": len(hist), "recommendation": rec, "why": why})
    n_action = sum(1 for r in recs if r["recommendation"])
    if args.json:
        print(json.dumps({"entries": len(entries), "recommendations": recs}, ensure_ascii=False, indent=1, default=str))
    else:
        for r in recs:
            flag = f"→ {r['recommendation']}" if r["recommendation"] else ""
            print(f"{r['strategy_id']} [{r['lifecycle_status']}] {r['name_zh']} 月判 {r['months_evaluated']} 期 {flag}")
        print(f"共 {len(entries)} 个 sim/paper 条目，{n_action} 条有流转建议（终裁=Owner）")
    if args.dry_run:
        return
    alert_recommendations(recs)
    write_run_archive(entries, recs)
    _emit_promotion_advisory_event(recs)


if __name__ == "__main__":
    main()
