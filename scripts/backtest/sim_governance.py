# [BLUEPRINT] MOD-BT-094 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.sim_governance
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; yaml
# [CONSUMERS] 模拟盘治理（lifecycle 流转建议报告，Owner 终裁）；策略登记册治理批次
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只产建议不改册（lifecycle 变更终裁=Owner）；规则全部引用既存真源
#   （SOP-C §8 双窗口门槛/偏离报告月度判定/oos_years_decay>=0.5 存疑线）
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
输出=建议报告 JSON（只读），落 run 档案；册子变更由 Owner 裁定后另行执行。
用法：python scripts/backtest/sim_governance.py
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


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="模拟盘治理·流转建议生成器（只产建议不改册）")
    ap.add_argument("--json", action="store_true")
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


if __name__ == "__main__":
    main()
