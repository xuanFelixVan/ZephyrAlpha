# [BLUEPRINT] MOD-BT-187 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.strategy_lifecycle_advisor
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.backtest.run_archive
# [CONSUMERS] 模拟盘平台蓝图批 4（治理自动化）；Owner lifecycle 终裁输入
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 规则纯函数（可测）；只建议不终裁（lifecycle 终裁=Owner）；台账只读零写入；decay 公式与 c4_batch_screen OOS 批一致 ((IS-OOS)/|IS|/2.5 钳[0,1])
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(台账查询失败)
# [TESTS] tests/backtest/test_strategy_lifecycle_advisor.py
# [A_module] module_id=MOD-BT-187 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""策略 lifecycle 流转建议器（平台蓝图批 4）——decay_watch 台账扫描件。

对每个既有 IS（translated_c4）又有 OOS（oos_tested）成绩的策略计算样本外衰减，
按预注册规则产出流转建议（只建议不终裁）：
  decay>=0.5            → decay_watch（存疑：冻结晋级资格，进入观察）
  IS<0 且 OOS<0         → reject（双窗皆负：不具备晋级资格）
  IS>=0.5 且 OOS>=0.5   → candidate（双窗达标：可走 SOP-C §8 bothwin 通道）
  其余                   → hold（证据不足，维持现状）
用法：python scripts/backtest/strategy_lifecycle_advisor.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

DECAY_SUSPECT_LINE = 0.5   # 蓝图批 4 存疑线（oos_years_decay）
CANDIDATE_LINE = 0.5       # bothwin 通道达标线（IS 与 OOS 双侧）
OOS_YEARS = 2.5


def compute_decay(is_sharpe: float, oos_sharpe: float) -> float:
    """样本外年化衰减率（与 c4_batch_screen OOS 批公式一致，钳 [0,1]）。"""
    denom = max(abs(float(is_sharpe)), 1e-9)
    return round(min(1.0, max(0.0, (float(is_sharpe) - float(oos_sharpe)) / denom / OOS_YEARS)), 4)


def advise(is_sharpe: float | None, oos_sharpe: float | None) -> tuple[str, str]:
    """流转建议规则（纯函数）。返回 (verdict, reason)。"""
    if is_sharpe is None or oos_sharpe is None:
        return "hold", "证据不足（缺 IS 或 OOS 成绩）"
    decay = compute_decay(is_sharpe, oos_sharpe)
    if is_sharpe < 0 and oos_sharpe < 0:
        return "reject", f"双窗皆负（IS={is_sharpe}/OOS={oos_sharpe}），不具备晋级资格"
    if decay >= DECAY_SUSPECT_LINE:
        return "decay_watch", f"样本外衰减 {decay} ≥ 存疑线 {DECAY_SUSPECT_LINE}，冻结晋级资格进入观察"
    if is_sharpe >= CANDIDATE_LINE and oos_sharpe >= CANDIDATE_LINE:
        return "candidate", f"双窗达标（IS={is_sharpe}/OOS={oos_sharpe}），可走 SOP-C §8 bothwin 通道"
    return "hold", f"衰减 {decay} 未越线但双侧未同时达标，维持现状"


def collect() -> list[dict]:
    """台账扫描：每策略最新 IS（translated_c4）与最新 OOS（oos_tested）。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from strategy_screen_query import _q

    table = "c1_backtest.strategy_screen"
    is_rows = dict(_q(
        f"SELECT strategy_id, argMax(is_sharpe, screened_at) FROM {table} "
        f"WHERE verdict='translated_c4' AND is_sharpe IS NOT NULL GROUP BY strategy_id"))
    oos_rows = dict(_q(
        f"SELECT strategy_id, argMax(is_sharpe, screened_at) FROM {table} "
        f"WHERE verdict='oos_tested' AND is_sharpe IS NOT NULL GROUP BY strategy_id"))
    out = []
    for sid in sorted(set(is_rows) | set(oos_rows)):
        isv, oosv = is_rows.get(sid), oos_rows.get(sid)
        verdict, reason = advise(isv, oosv)
        out.append({"strategy_id": sid, "is_sharpe": isv, "oos_sharpe": oosv,
                    "decay": compute_decay(isv, oosv) if isv is not None and oosv is not None else None,
                    "advice": verdict, "reason": reason})
    return out


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="策略 lifecycle 流转建议器（蓝图批 4）")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写 run 档案")
    args = parser.parse_args()

    items = collect()
    summary: dict[str, int] = {}
    for it in items:
        summary[it["advice"]] = summary.get(it["advice"], 0) + 1
    report = {"total": len(items), "summary": summary, "items": items}
    print(json.dumps(report, ensure_ascii=False, indent=1, default=str))

    if not args.dry_run:
        from datetime import datetime

        from zephyr.backtest.run_archive import create_run, finalize_run, write_step

        run_id = f"SCR-LIFE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        create_run(run_id=run_id, object_id="", kind="SCREEN",
                   window={"start": "2020-01-01", "end": "2026-06-30"},
                   cost_mode="frozen_l0", created_by="ai-session:strategy-lifecycle-advisor")
        write_step(run_id, "03", (
            "# 数据清单\n\n- name: lifecycle 建议扫描源\n"
            "  source: c1_backtest.strategy_screen（verdict IN (translated_c4, oos_tested) 双窗最新行）\n"
            "  window_is: 2020-01-01..2026-06-30\n"
            "  pit_note: 'decay=(IS-OOS)/|IS|/2.5 钳[0,1]，存疑线 0.5；只建议不终裁'\n  proxy: false\n"
        ))
        write_step(run_id, "04", json.dumps(report, ensure_ascii=False, indent=1, default=str),
                   filename="lifecycle_advice.json")
        write_step(run_id, "verdict", (
            f"# 判定书：{run_id}\n\n对象：策略 lifecycle 流转建议（蓝图批 4，只建议不终裁）｜ kind=SCREEN\n"
            f"结论：{json.dumps(summary, ensure_ascii=False)}\n"
            "口径：decay=(IS-OOS)/|IS|/2.5 钳[0,1]，存疑线 0.5；数据源=strategy_screen 双窗最新行\n"))
        finalize_run(run_id, verdict_ref={"table": "c1_backtest.strategy_screen", "run_id": run_id})
        logger.info("run 档案：%s", run_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
