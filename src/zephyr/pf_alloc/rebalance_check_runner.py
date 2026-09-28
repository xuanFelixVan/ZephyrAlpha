# [BLUEPRINT] MOD-PA-030 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] zephyr.pf_alloc.rebalance_check_runner
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.pf_core.core.rebalance_scheduler(MOD-PF-003 四触发源决策，只调不抄);
#   zephyr.pf_alloc.allocation_inputs(日期校验); schemas.categories.alloc_budget_daily(读模板真源);
#   zephyr.shared.io.file_utils(safe_write_text CAS); zephyr.data.ch_reader(默认读角色，可注入)
# [CONSUMERS] zephyr.data.scheduler(_run_special_schedule "pf_alloc_rebalance_check" 槽，2026-09-27
#   FAC-E8 再平衡调度接线); CLI python -m zephyr.pf_alloc.rebalance_check_runner（人工/排障）
# [STARTUP] scheduled（data scheduler 05:45 交易日档；本件只读+告警，分配链本体仍=事件驱动禁 cron）
# [MATURITY] experimental
# [INVARIANTS] 纯只读对照件：不写任何 CH 表、不产订单、不改预算——再平衡动作仍归分配链
#   正门（maybe_emit_pf_alloc_daily→BudgetChangeHandler 防抖），本件只出决策读数与告警；
#   决策逻辑零复制=逐字复用 MOD-PF-003 RebalanceScheduler.evaluate（optimizer=None 纯评估）；
#   目标权重真源=alloc_budget_daily.final_weight（SQL_DAY_SLICE 最近 run），当前权重真源=
#   sim_pocket_daily 钱包市值/组合总权益，两眼都缺=闸门失明必告警（certifier 先例）；
#   读数失败 fail-open 降级告警不炸调度器（cross_validation 同族先例）；资金常量零硬编码
#   （阈值全数承 RebalanceConfig C 类可调参数）；写报告文件必经 safe_write_text CAS
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据缺席/读数异常→告警+ok=False（不向外抛）；权重非法（负值等）→
#   InvalidRebalanceInputError 捕获降级告警（读数脏=巡检失明，非调度器故障）
# [TESTS] tests/pf_alloc/test_rebalance_check_runner.py; tests/zephyr/data/test_pf_alloc_rebalance_check_wiring.py
# [A_module] module_id=MOD-PA-044 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] rebalance-check-runner-mod-pa-044-20260927
"""rebalance_check_runner——组合再平衡巡检读数件（FAC-E8 再平衡调度接线，2026-09-27）。

真源：b2_f27 挖矿簿 FAC-E8"再平衡调度未闭环"缺口 + PFA-4③ 治本口径
（再权节拍=SIM_DAILY 事件，防抖在 BudgetChangeHandler 内，本件不重复该节拍）。

本件补的是缺的第三面：**组合级漂移巡检**。MOD-PF-003 四触发源（漂移/日历/事件/风控）
+ 成本感知判定（benefit>2×cost）是 production 实件但全仓无生产调用方（有件无消费，
PFA-1 同款病）——本件把它挂上 data scheduler 巡检槽：

    alloc_budget_daily.final_weight（目标面）
        ── SQL_DAY_SLICE 最近 run ──▶
    sim_pocket_daily 钱包市值（当前面）          ├─▶ RebalanceScheduler.evaluate
        ── 市值/总权益 ──▶                      │    (optimizer=None，只评估不重优化)
                                                └─▶ data/runtime/pf_alloc_rebalance_check.json
                                                     + REBALANCE 决策 Advisory 告警

职责边界（铁律）：
  - 决策=rebalance/skip 读数与告警，**不执行**——执行仍走分配链事件正门；
  - 触发词表与阈值零复制零新设：全部承 MOD-PF-003 RebalanceConfig；
  - 日历触发（周五档）语义=MOD-PF-003 calendar_weekday，槽位 05:45 只是巡检时钟，
    两者正交（巡检日≠触发源）。

# [ALGO_FLOW] external: docs/03_modules/_domain_portfolio_alloc/algo_flow/rebalance_check_runner.yaml
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Protocol

try:
    from zephyr.shared.io.paths import REPO_ROOT as _REPO_ROOT
except Exception:  # noqa: BLE001 — 仅路径解析降级
    _REPO_ROOT = Path(__file__).resolve().parents[2]

# schemas/ DDL-as-Code 真源在仓根（不在 src 包内）——同 allocation_persistence 挂载理由
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from schemas.categories import alloc_budget_daily  # noqa: E402
from zephyr.pf_core.core.rebalance_scheduler import (  # noqa: E402
    RebalanceDecision,
    RebalanceScheduler,
)

logger = logging.getLogger(__name__)

__all__: Final = ["REPORT_PATH", "run_rebalance_check"]

# 巡检报告落点（.runtime 卫生铁律：产物归 data/runtime 运行面，非 .runtime 根直写）
REPORT_PATH = _REPO_ROOT / "data" / "runtime" / "pf_alloc_rebalance_check.json"

# 钱包当前面（SQL 单值常量，feedback_prior._SQL_ATTRIBUTION_LATEST 同款豁免形态；
# LIMIT 1 BY 取每钱包最新一行，mode=sim_daily=模拟盘正式档）
_SQL_POCKET_LATEST = (  # noqa: bare-sql  巡检读数常量（_SQL_ 前缀；列序真源=schemas sim_pocket_daily）
    "SELECT strategy_id, position_value, equity FROM ("
    "SELECT strategy_id, position_value, equity "
    # noqa: ch-final  sim_pocket_daily=MergeTree 只增流水（非 Replacing），ORDER BY+LIMIT 1 BY 已自带每钱包最新行去重语义，FINAL 冗余
    "FROM c1_backtest.sim_pocket_daily WHERE mode = 'sim_daily' "
    "ORDER BY trade_date DESC, ingest_ts DESC LIMIT 1 BY strategy_id)"
)


# 读缝：SQL -> 位置行序列（复用 allocation_inputs.resolve_reader，禁平行实现——FUNCTION-DUP）
Reader = Callable[[str], Sequence[Any]]


def _load_target_weights(reader: Reader) -> tuple[str, dict[str, float]]:
    """目标面=alloc_budget_daily 最近 run 的 final_weight（planned exposure 口径）。"""
    rows = reader(alloc_budget_daily.SQL_LATEST_TRADE_DATE.format(table=alloc_budget_daily.TABLE_NAME))
    if not rows or rows[0][0] is None:
        return "", {}
    latest_day = str(rows[0][0])
    slice_rows = reader(alloc_budget_daily.SQL_DAY_SLICE.format(table=alloc_budget_daily.TABLE_NAME, date=latest_day))
    # SQL_DAY_SLICE 列序（DDL 真源）: strategy_id, run_id, allocation, global_shrinkage,
    # effective_budget, allocated_capital, final_weight, budget_action, current_tier
    targets = {str(r[0]): float(r[6]) for r in slice_rows}
    return latest_day, targets


def _load_current_weights(reader: Reader) -> tuple[dict[str, float], float]:
    """当前面=钱包市值/组合总权益（sim_daily 档；总权益=Σ 各钱包最新 equity）。"""
    rows = reader(_SQL_POCKET_LATEST)
    position_by_sid = {str(r[0]): max(float(r[1]), 0.0) for r in rows}
    total_equity = sum(max(float(r[2]), 0.0) for r in rows)
    if total_equity <= 0:
        return {}, 0.0
    current = {sid: value / total_equity for sid, value in position_by_sid.items()}
    return current, total_equity


class RebalanceAlerter(Protocol):
    """告警通道最小协议（notify 鸭子型；实瓶见各 LSG/告警适配件）。"""

    def notify(self, topic: str, text: str, *, level: str, source: str) -> None: ...


def run_rebalance_check(
    *,
    reader: Reader | None = None,
    alerter: RebalanceAlerter | None = None,
    now: datetime | None = None,
    out_path: str | Path | None = None,
    market_state: int = 0,
) -> dict[str, Any]:
    """一轮组合再平衡巡检（只读对照 → MOD-PF-003 决策读数 → 报告+告警）。

    Returns:
        {"ok": bool, "trade_date": str, "decision": {...}, "drift": {...},
         "wallets": int, "portfolio_equity": float, "report_path": str, ...}
        ok=False=数据面失明或读数异常（已告警，不抛）。
    """
    from zephyr.pf_alloc.allocation_inputs import resolve_reader

    reader = resolve_reader(reader)
    now = now or datetime.now(UTC)
    out_path = Path(out_path) if out_path else REPORT_PATH
    report: dict[str, Any] = {
        "kind": "pf_alloc_rebalance_check",
        "trade_date": "",
        "wallets": 0,
        "portfolio_equity": 0.0,
        "decision": None,
        "ok": False,
    }

    def _notify(level: str, text: str) -> None:
        if alerter is not None:
            try:
                alerter.notify("pf_alloc_rebalance_check", text[:200], level=level, source="rebalance_check_runner")
            except Exception:  # noqa: BLE001 — 告警通道自身故障不再上抛（同族先例）
                pass

    try:
        budgets_day, targets = _load_target_weights(reader)
        current, total_equity = _load_current_weights(reader)
    except Exception as exc:  # noqa: BLE001 — 巡检读数降级告警，不炸调度器
        logger.warning("pf_alloc_rebalance_check 读数失败: %s", exc)
        _notify("ERROR", f"再平衡巡检读数异常: {exc!s}")
        report["error"] = str(exc)[:200]
        _write_report(out_path, report)
        return report

    report["trade_date"] = budgets_day
    report["portfolio_equity"] = round(total_equity, 2)
    if not targets or not current:
        # 闸门失明：任一面缺证必出声（strategy_decay_certifier 零行输入同款铁律）
        _notify(
            "WARN",
            f"再平衡巡检失明: 预算面 {'有' if targets else '空'} / 钱包面 {'有' if current else '空'}"
            f"（trade_date={budgets_day or '无行'}）",
        )
        report["error"] = "blind_scan: budgets/pockets 缺证"
        _write_report(out_path, report)
        return report

    union: dict[str, float] = {}
    for sid in set(targets) | set(current):
        union[sid] = 0.0
    weights_current = {**union, **{k: v for k, v in current.items()}}
    weights_target = {**union, **{k: v for k, v in targets.items()}}

    try:
        evaluation = RebalanceScheduler().evaluate(
            current_weights=weights_current,
            target_weights=weights_target,
            market_state=market_state,
            now=now,
        )
    except Exception as exc:  # noqa: BLE001 — 权重脏数据=巡检失明，降级告警
        logger.warning("pf_alloc_rebalance_check 决策失败: %s", exc)
        _notify("WARN", f"再平衡巡检决策异常（权重面脏数据？）: {exc!s}")
        report["error"] = str(exc)[:200]
        _write_report(out_path, report)
        return report

    report["decision"] = evaluation.to_dict()
    report["drift"] = {
        "portfolio_drift": round(evaluation.portfolio_drift, 8),
        "max_single_drift": round(evaluation.max_single_drift, 8),
    }
    report["wallets"] = len(weights_current)
    report["ok"] = True
    if evaluation.decision == RebalanceDecision.REBALANCE:
        # Advisory 告警：动作仍归分配链正门 + Owner 门位（本件不执行，只出声）
        _notify(
            "WARN",
            f"组合漂移触发再平衡建议: drift={evaluation.portfolio_drift:.4f} "
            f"max_single={evaluation.max_single_drift:.4f}（advisory——执行归分配链正门）",
        )
    _write_report(out_path, report)
    return report


def _write_report(out_path: Path, report: dict[str, Any]) -> None:
    """报告落盘（safe_write_text CAS；写失败只记日志——巡检产物不得反噬调度器）。"""
    import json

    from zephyr.shared.io.file_utils import safe_write_text

    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        safe_write_text(out_path, json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    except Exception as exc:  # noqa: BLE001 — 报告面故障不反噬
        logger.warning("rebalance 巡检报告写盘失败 (%s): %s", out_path, exc)


if __name__ == "__main__":  # pragma: no cover — CLI 人工/排障入口
    import json as _json

    print(_json.dumps(run_rebalance_check(), ensure_ascii=False, indent=2))
