# [BLUEPRINT] MOD-POS-030 | docs/03_modules/_domain_position/position_checkup_orchestrator/blueprint.md（挖干处方=docs/_working/fullconnect_campaign/e_decision_chain/06_f42_p1_position_checkup.md G42-1）
# [MODULE] zephyr.position.core.position_checkup_orchestrator
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.position_state_machine(PositionState); zephyr.sell_decision.core.position_triage(PositionTriage/SellPositionSnapshot/StrategyType); zephyr.plan_engine.thesis_survival(evaluate_thesis/ThesisEvidence/ThesisType); zephyr.risk.core.ashare_stop_loss_engine(AshareStopLossRuleEngine); zephyr.position.core.position_drift_monitor(PositionDriftMonitor); zephyr.position.core.position_adjudication_center(PositionAdjudicationCenter/AdjudicationRequest/IntendedAction)
# [CONSUMERS] zephyr.plan_engine.daily_loop_master_switch(_stage_position_checkup，dloop premarket 段，dloop_post 16:45 自动圈)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只编排不重造(六段全委托既有件 MOD-POS-002/MOD-SELL-000/MOD-PLAN-024/MOD-RK-09/MOD-POS-003/MOD-POS-024); 单持仓单段失败 fail-open 留痕继续; 动作映射确定性(止损信号∨thesis DEAD→EXIT; 漂移越带→REDUCE; 其余→HOLD); EXIT/REDUCE 交易意图必过裁决中心(四层 callable 注入,缺装配=人工确认默认态不裁决); 输入缺席=skipped 留痕(禁伪造持仓数据); 审计 JSONL append-only; 零下单(观察记录面,裁定#305 同族安全态)
# [MODIFY-GUARD] tests/position/test_position_checkup_orchestrator.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(data_date 格式非法 fail-closed)；单段异常→该段 result["status"]="error" 留痕；输入缺失→skipped
# [TESTS] tests/position/test_position_checkup_orchestrator.py
# [A_module] module_id=MOD-POS-030 | layer=module | stability=evolving | safety=L | ai_modifiable
# [TTL] permanent
"""

position_checkup_orchestrator — P1 持仓体检棒（F42 G42-1 编排接线，st-c9-f42）

体检五件（P1-01..05）建成未接线（日循环编排入口零命中，2026-09-25/09-29 双重复核实证），
本件=那根"体检棒"：按 TDM-P-P1 边序把五件+裁决中心串成一条盘前链，挂 dloop premarket 段
（dloop_post 16:45 自动圈，事件驱动，无 cron/无 sleep-loop）：

    对账快照(P1-01 态合法性) → 分级(P1-02) → 逻辑存活(P1-03) → 风险否决(P1-04)
    → 组合级(P1-05, 整组合一次) → 结论动作清单(P1-06 动作映射+裁决中心+审计)

只编排不重造：六段全委托既有件；每持仓逐段 fail-open；组合级漂移全组合跑一次。
动作映射（确定性，"单票看对错，组合看结构"）：
    止损信号触发 或 thesis=DEAD → EXIT（转离场）
    组合漂移越带命中该标的   → REDUCE（减仓）
    其余                     → HOLD（维持）
EXIT/REDUCE 属交易意图 → 过 PositionAdjudicationCenter（四层 callable 由装配方注入）；
缺装配=人工确认默认态（P1-06 fallback 同款），不裁决不下单。

输入面（取数契约）：上游 F57 盘后对账产物投放 `inputs_<data_date>.json` 于
`data/runtime/position_checkup/`；生产对账取数面未接线（工单卷"对账上游衔接=待核"），
缺席=skipped 留痕——编排先通，取数面留接口，禁伪造持仓数据。
输出面：PositionCheckupReport（JSON 可序列化 dict）+ 审计 JSONL 追加
（默认 data/runtime/position_checkup/audit_<data_date>.jsonl，append-only）。

SSoT: docs/_working/fullconnect_campaign/e_decision_chain/06_f42_p1_position_checkup.md
# [ALGO_FLOW] external: docs/03_modules/_domain_position/algo_flow/position_checkup_orchestrator.yaml
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.paths import REPO_ROOT

__all__: Final[list[str]] = [
    "CheckupPositionInput",
    "CheckupSegmentError",
    "default_positions_loader",
    "run_position_checkup",
]

_DATE_LEN: Final = 10
_CHECKUP_DIRNAME: Final = "position_checkup"
_ACTION_HOLD: Final = "HOLD"
_ACTION_REDUCE: Final = "REDUCE"
_ACTION_EXIT: Final = "EXIT"
# 四层 callable 表（portfolio/strategy/symbol/dynamic），装配方注入
AdjudicationLayers = Mapping[str, Callable[[Any], Any]]


class CheckupSegmentError(ValueError):
    """体检输入非法（单持仓 fail-open 收敛为该段 error，不炸全链）。"""


@dataclass(frozen=True)
class CheckupPositionInput:
    """单持仓体检输入（上游对账产物投放契约，缺维度=None=该段降级/跳过）。

    Attributes:
        symbol: 标的代码（必填）
        strategy_id: 归属策略标识（裁决请求审计用）
        state: 状态机态（P1-01 台账快照，PositionState 值集）
        entry_price / current_price: 分级+止损判据价
        stop_loss_price: 当前止损锚定价（P1-02/P1-04）
        atr_value: ATR(14)（缺失=P1-02 降级 MONITOR，模块自守）
        strategy_type: 分级策略类型（position_triage.StrategyType 值，默认 other）
        thesis_type: 买入理由类型（ThesisType 值；None=跳过 P1-03）
        thesis_evidence: ThesisEvidence 四字段键值（仅相关维度）
        stop_loss_inputs: 止损引擎扩展判据（support_level/vwap/sector_momentum/logic_valid）
        weight_actual / weight_target: 组合权重（P1-05 漂移+裁决 intended_weight）
        triage_threshold_delta: 分级双向反馈调整量（BM-POS-09，默认 0.0）
    """

    symbol: str
    strategy_id: str = "default"
    state: str = "ACTIVE"
    entry_price: float | None = None
    current_price: float | None = None
    stop_loss_price: float | None = None
    atr_value: float | None = None
    strategy_type: str = "other"
    thesis_type: str | None = None
    thesis_evidence: Mapping[str, Any] = field(default_factory=dict)
    stop_loss_inputs: Mapping[str, Any] = field(default_factory=dict)
    weight_actual: float | None = None
    weight_target: float | None = None
    triage_threshold_delta: float = 0.0


def _seg_ok(**kw: Any) -> dict[str, Any]:
    return {"status": "ok", **kw}


def _seg_skip(reason: str) -> dict[str, Any]:
    return {"status": "skipped", "reason": reason}


def _seg_err(exc: Exception) -> dict[str, Any]:
    return {"status": "error", "error": f"{type(exc).__name__}: {exc}"[:300]}


# ── P1-01 对账快照（态合法性+台账快照记录；状态转移归事件入口不在此重造）───────


def _seg_snapshot(pos: CheckupPositionInput) -> dict[str, Any]:
    from zephyr.position.core.position_state_machine import PositionState

    try:
        state = PositionState(pos.state)
    except ValueError as exc:
        raise CheckupSegmentError(f"非法状态机态: {pos.state!r}") from exc
    if not pos.symbol:
        raise CheckupSegmentError("symbol 不能为空")
    return _seg_ok(state=state.value)


# ── P1-02 持仓分级（委托 MOD-SELL-000）───────────────────────────────────────


def _seg_triage(pos: CheckupPositionInput) -> dict[str, Any]:
    from zephyr.sell_decision.core.position_triage import PositionTriage, SellPositionSnapshot, StrategyType

    if pos.entry_price is None or pos.current_price is None or pos.stop_loss_price is None:
        return _seg_skip("missing_price_inputs")
    level = PositionTriage.triage(
        SellPositionSnapshot(
            symbol=pos.symbol,
            entry_price=pos.entry_price,
            current_price=pos.current_price,
            strategy_type=StrategyType(pos.strategy_type),
        ),
        pos.atr_value,
        pos.stop_loss_price,
        threshold_delta=pos.triage_threshold_delta,
    )
    return _seg_ok(triage=level.value)


# ── P1-03 逻辑存活（委托 MOD-PLAN-024）───────────────────────────────────────


def _seg_thesis(pos: CheckupPositionInput) -> dict[str, Any]:
    from zephyr.plan_engine.thesis_survival import ThesisEvidence, evaluate_thesis

    if pos.thesis_type is None:
        return _seg_skip("no_thesis_annotated")
    verdict = evaluate_thesis(pos.thesis_type, ThesisEvidence(**dict(pos.thesis_evidence)))
    return _seg_ok(state=verdict.state.value, reason=verdict.reason)


# ── P1-04 风险否决（委托 MOD-RK-09）──────────────────────────────────────────


def _seg_stop_loss(pos: CheckupPositionInput) -> dict[str, Any]:
    from zephyr.risk.core.ashare_stop_loss_engine import AshareStopLossRuleEngine

    if pos.entry_price is None or pos.current_price is None:
        return _seg_skip("missing_price_inputs")
    signals = AshareStopLossRuleEngine().check_position(
        symbol=pos.symbol,
        entry_price=pos.entry_price,
        current_price=pos.current_price,
        **dict(pos.stop_loss_inputs),
    )
    return _seg_ok(
        triggers=[s.trigger_type.value for s in signals],
        max_severity=max((s.severity.value for s in signals), default=None),
    )


# ── P1-05 组合级漂移（整组合一次，委托 MOD-POS-003）──────────────────────────


def _seg_portfolio_drift(positions: Sequence[CheckupPositionInput]) -> dict[str, Any]:
    from zephyr.position.core.position_drift_monitor import PositionDriftMonitor

    actual = {p.symbol: p.weight_actual for p in positions if p.weight_actual is not None}
    target = {p.symbol: p.weight_target for p in positions if p.weight_target is not None}
    common = sorted(set(actual) & set(target))
    if not common:
        return _seg_skip("missing_weights")
    result = PositionDriftMonitor().check(
        actual_weights={k: actual[k] for k in common},
        target_weights={k: target[k] for k in common},
    )
    alerts = result.all_alerts
    drifted = sorted({a.symbol for a in alerts if a.symbol})
    return _seg_ok(
        has_drift=result.has_drift,
        drifted_symbols=drifted,
        portfolio_alert=None if result.portfolio_alert is None else result.portfolio_alert.drift,
        alert_count=len(alerts),
    )


# ── P1-06 结论动作清单（映射+裁决中心+审计）──────────────────────────────────


def _derive_action(seg: dict[str, dict[str, Any]], drifted: bool) -> str:
    """确定性动作映射：止损∨DEAD→EXIT；漂移越带→REDUCE；其余→HOLD。"""
    sl = seg.get("stop_loss", {})
    if sl.get("status") == "ok" and sl.get("triggers"):
        return _ACTION_EXIT
    th = seg.get("thesis", {})
    if th.get("status") == "ok" and th.get("state") == "DEAD":
        return _ACTION_EXIT
    if drifted:
        return _ACTION_REDUCE
    return _ACTION_HOLD


def _seg_adjudicate(
    pos: CheckupPositionInput,
    action: str,
    data_date: str,
    layers: AdjudicationLayers | None,
) -> dict[str, Any]:
    """EXIT/REDUCE 过裁决中心（MOD-POS-024）；缺装配=人工确认默认态。"""
    if action == _ACTION_HOLD:
        return _seg_ok(adjudicated=False, note="无交易意图不裁决")
    if layers is None:
        return {"status": "skipped", "reason": "adjudication_layers_not_wired", "manual_confirmation": True}
    from zephyr.position.core.position_adjudication_center import (
        AdjudicationRequest,
        IntendedAction,
        PositionAdjudicationCenter,
    )

    center = PositionAdjudicationCenter(
        portfolio_layer=layers["portfolio"],
        strategy_layer=layers["strategy"],
        symbol_layer=layers["symbol"],
        dynamic_layer=layers["dynamic"],
    )
    intended = (
        0.0 if action == _ACTION_EXIT else (pos.weight_target if pos.weight_target is not None else pos.weight_actual)
    )
    if intended is None:  # 减仓意图但无权重锚 → 人工确认（fail-closed 不猜数）
        return {"status": "skipped", "reason": "no_weight_anchor_for_reduce", "manual_confirmation": True}
    plan = center.adjudicate(
        AdjudicationRequest(
            request_id=f"chk-{data_date}-{pos.symbol}",
            strategy_id=pos.strategy_id,
            symbol=pos.symbol,
            action=IntendedAction.EXIT if action == _ACTION_EXIT else IntendedAction.REDUCE,
            intended_weight=float(intended),
            context={"source": "position_checkup", "data_date": data_date},
        )
    )
    if not plan.allowed:
        return {
            "status": "ok",
            "adjudicated": True,
            "allowed": False,
            "manual_confirmation": True,
            "reason": plan.reason,
        }
    return _seg_ok(adjudicated=True, allowed=True, final_weight=plan.final_weight, adjudication_id=plan.adjudication_id)


def _append_audit(report: dict[str, Any], audit_path: Path) -> None:
    """审计 JSONL 追加（append-only；写后进程外可见，读方自证行完整）。"""
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(report, ensure_ascii=False, default=str)
    with audit_path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def run_position_checkup(
    positions: Sequence[CheckupPositionInput],
    *,
    data_date: str,
    adjudication_layers: AdjudicationLayers | None = None,
    audit_path: Path | str | None = None,
) -> dict[str, Any]:
    """跑一遍 P1 持仓体检链（TDM-P-P1-01..06 边序），返回 JSON 可序列化报告。

    单持仓单段失败 fail-open 留痕；组合级漂移全组合跑一次；零下单（观察记录面）。
    """
    if len(data_date) != _DATE_LEN or data_date.count("-") != 2:
        raise ValueError(f"data_date 非法（期望 YYYY-MM-DD）: {data_date}")

    drift_seg = _seg_portfolio_drift(positions)
    drifted_symbols: set[str] = set(drift_seg.get("drifted_symbols", []) or [])

    rows: list[dict[str, Any]] = []
    counts = {"ok": 0, "skipped": 0, "error": 0}
    action_counts: dict[str, int] = {}
    for pos in positions:
        seg: dict[str, dict[str, Any]] = {}
        for name, fn in (
            ("snapshot", lambda p=pos: _seg_snapshot(p)),
            ("triage", lambda p=pos: _seg_triage(p)),
            ("thesis", lambda p=pos: _seg_thesis(p)),
            ("stop_loss", lambda p=pos: _seg_stop_loss(p)),
        ):
            try:
                seg[name] = fn()
            except Exception as exc:  # noqa: BLE001 — 单段 fail-open 留痕
                seg[name] = _seg_err(exc)
        action = _derive_action(seg, drifted=pos.symbol in drifted_symbols)
        try:
            seg["adjudication"] = _seg_adjudicate(pos, action, data_date, adjudication_layers)
        except Exception as exc:  # noqa: BLE001 — 裁决段 fail-open 留痕
            seg["adjudication"] = _seg_err(exc)
        manual = any(s.get("manual_confirmation") for s in seg.values() if isinstance(s, dict))
        row = {
            "symbol": pos.symbol,
            "strategy_id": pos.strategy_id,
            "segments": seg,
            "derived_action": action,
            "action": "MANUAL_CONFIRM" if manual else action,
            "manual_confirmation": manual,
        }
        rows.append(row)
        action_counts[row["action"]] = action_counts.get(row["action"], 0) + 1
        for s in seg.values():
            counts[str(s.get("status", "error")) if str(s.get("status")) in counts else "error"] += 1

    report: dict[str, Any] = {
        "data_date": data_date,
        "node": "TDM-P-P1",
        "mode": "observe_record_only_zero_orders",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "portfolio_drift": drift_seg,
        "positions": rows,
        "summary": {"segments": counts, "actions": action_counts},
    }
    sink = (
        Path(audit_path)
        if audit_path
        else Path(REPO_ROOT) / "data" / "runtime" / _CHECKUP_DIRNAME / f"audit_{data_date}.jsonl"
    )
    try:
        _append_audit(report, sink)
        report["audit_path"] = str(sink)
    except OSError as exc:  # 审计盘故障不炸体检链（fail-open 留痕）
        report["audit_error"] = f"{type(exc).__name__}: {exc}"[:200]
    return report


def default_positions_loader(data_date: str) -> list[dict[str, Any]]:
    """投放面读数：inputs_<data_date>.json（上游 F57 对账产物契约）。

    缺席=空表（调用方 skipped 留痕）——生产对账取数面未接线，禁伪造持仓数据。
    """
    path = Path(REPO_ROOT) / "data" / "runtime" / _CHECKUP_DIRNAME / f"inputs_{data_date}.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, list) else []
