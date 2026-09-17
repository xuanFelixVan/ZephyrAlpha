# [BLUEPRINT] MOD-BT-213 | docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md
# [MODULE] zephyr.strategy_pipeline.daily_gate_snapshot
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.pf_alloc.allocation_inputs(SQL_LATEST_REGIME_SNAPSHOT/validate_date_literal/resolve_reader，只 import 不改);
#   schemas.categories.alloc_budget_daily(SQL_DAY_SLICE，只 import 不改);
#   zephyr.signal_ashare.core.environment_switch(六段×四开关查表，只 import 不改);
#   zephyr.security.access_control.kill_switch(探针); zephyr.position.core.firm_risk_aggregator(约束栈默认面只读);
#   zephyr.infrastructure.database_service(reader 角色，宪法 §9.1)
# [CONSUMERS] zephyr.strategy_pipeline.daily_decision_orchestrator(唯一消费方，S3 步)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 只读采集零判定改动（蓝图 §四.2：门模块一律不改，器侧聚合查询优先）；
#   采集失败不炸拍板——缺席项标 status=absent+error 类型留痕，由编排器降级矩阵（蓝图 §六.2）接管；
#   L5 kill_switch 读态失败=按熔断保守侧处理（保命件方向不猜，D6）；
#   L2 板块门无持久化日度状态=v1 如实标 absent（蓝图原文），不伪造门态；
#   所有读经注入 reader（默认 DatabaseService reader 角色），SQL 模板一律取 schemas/既有真源
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 本模块顶层函数永不外抛（缺席/异常全部折进返回结构 status=absent）；
#   输入日期非法由 validate_date_literal 抛 ValueError（fail-closed，唯一例外）
# [TESTS] tests/strategy_pipeline/test_decision_orchestrator.py
# [A_module] module_id=MOD-BT-213 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] daily-gate-snapshot-mod-bt-213-20260916
"""daily_gate_snapshot — 分层参与门快照采集器（BT-P1-031 刀 2 一闸，蓝图 §四.2）。

定位：日度编排器 S3 步的只读采集面——L1-L5 五层门态一行 JSON 可审计，**零判定改动**
（判断归各层模型：regime 归 MOD-REGIME-001、预算带归 TDM-F-C1 语义、熔断归 kill_switch）。

五层采集源与缺席语义（蓝图 §四.2 原表）：
    L1  regime_snapshot_history PIT 读（对齐 pf_alloc/allocation_inputs 先例）
        缺席→编排器 no_trade（D1 regime_missing）
    L2  signal_ashare/sector/sector_gate.py（三级放行）——纯函数件无持久化日度状态，
        v1 如实标 absent（依赖 L2 门参与的包今日禁用，D2）
    L3  environment_switch 六段×四开关查表（纯函数，六段状态+两市成交额可得时评估；
        成交额代理=kline_index 399317 国证A指 amount/1e8，v0 口径标注）
    L4  alloc_budget_daily 当日 run 切片（SQL_DAY_SLICE 真源复用）+ 约束栈默认面
        缺席→编排器 no_trade（D3 budget_run_missing）
    L5  kill_switch 读态（读态失败=按熔断保守侧，D6）+ drawdown/price_cage/t1_sellable
        可达性登记（v1 无持久化级位可读=absent 如实，保命件横切独立不受影响）

[ALGO_FLOW]
输入: data_date（数据日 YYYY-MM-DD）+ 可选六段状态/成交额（L3 评估用）+ 注入式 reader
前置检查: 日期字面量校验 fail-closed；其余全部 fail-open（缺席折进返回结构）
执行: 逐层采集（L1 PIT 读 → L2 恒 absent → L3 查表 → L4 日切片 → L5 读态）
输出: {"l1":..., "l2":..., "l3":..., "l4":..., "l5":..., "absent_layers": [...]}（JSON 可序列化）
降级: 每层独立 fail-open，单层异常不炸其余层
不变量: 零写入、零判定、零门模块改动
[/ALGO_FLOW]
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Final

from zephyr.pf_alloc.allocation_inputs import (
    SQL_LATEST_REGIME_SNAPSHOT,
    resolve_reader,
    validate_date_literal,
)

log = logging.getLogger(__name__)

__all__: Final = ["collect_gate_snapshot", "read_latest_regime_snapshot", "read_market_turnover_yi", "resolve_table_name"]

Reader = Callable[[str], Any]

# L4 预算日切片 SQL 真源（schemas/categories/alloc_budget_daily.py SQL_DAY_SLICE，禁散落重拼）
_L4_DAY_SLICE_SQL: Final = (
    "SELECT strategy_id, run_id, allocation, global_shrinkage, effective_budget, "  # noqa: bare-sql  模块级 _SQL_ 前缀 SQL 模板常量唯一真源(禁散落重拼)
    "allocated_capital, final_weight, budget_action, current_tier "
    "FROM {table} WHERE trade_date = '{date}' "
    "ORDER BY ingest_ts DESC LIMIT 1 BY strategy_id"
)
# 两市成交额代理源（v0 口径，标注可调）：指数日K 399317 国证A指=全 A 成交额覆盖面，
# amount 单位=元，/1e8 折亿元（L3 环境开关 turnover_amount_yi 口径）。
# 表名经 TableRegistry 真源解析（#ARCH-CH-024，禁硬编码字面量）；解析失败=读数不可得
# （返回 None→L3 absent，诚实降级，不携带 fallback 字面量绕真源）。
_TURNOVER_SYMBOL: Final = "399317"
_TURNOVER_CATEGORY: Final = "market_index_kline"
_TURNOVER_YI_SQL: Final = (
    "SELECT amount FROM {table} "  # noqa: bare-sql  模块级常量真源(表名占位经 TableRegistry 解析)
    "WHERE symbol = '" + _TURNOVER_SYMBOL + "' AND trade_date = '{date}' ORDER BY trade_date DESC LIMIT 1"
)


def resolve_table_name(category: str) -> str:
    """表名 TableRegistry 真源解析（#ARCH-CH-024；解析失败抛错由调用方按通道故障处理）。

    公共件：本模块与 daily_decision_orchestrator 共用（CloneGuard 合并而非新建）。
    """
    from zephyr.data.table_registry import get_registry

    return get_registry().table(category)


def read_latest_regime_snapshot(data_date: str, *, reader: Reader | None = None) -> dict[str, Any]:
    """L1 采集：regime_snapshot_history 最新 PIT 行（trade_date ≤ 数据日）。

    返回 {"status": "ok", ...快照字段} 或 {"status": "absent", "error": 类型}。
    快照行存在但 trade_date 落后多少由编排器判新鲜度（D1 口径），本件只如实带 source_date。
    """
    day = validate_date_literal(data_date)
    sql = SQL_LATEST_REGIME_SNAPSHOT.format(table="c1_backtest.regime_snapshot_history", date=day)
    try:
        rows = list(resolve_reader(reader)(sql))
    except Exception as exc:  # noqa: BLE001 — 采集失败不炸拍板（蓝图 §四.2）
        return {"status": "absent", "error": type(exc).__name__, "layer": "L1"}
    if not rows:
        return {"status": "absent", "error": "no_row", "layer": "L1"}
    cols = (
        "run_id", "trade_date", "p_r1", "p_r2", "p_r3", "p_r4", "p_r10", "p_r11",
        "p_r12", "dominant", "confidence", "confidence_signal", "risk_signal",
        "shrinkage", "probs_json",
    )
    row = dict(zip(cols, [str(x) if i in (0, 9) else x for i, x in enumerate(rows[0])]))
    probs = {k: float(row[f"p_{k}"]) for k in ("r1", "r2", "r3", "r4", "r10", "r11", "r12")}
    return {
        "status": "ok",
        "layer": "L1",
        "run_id": str(row["run_id"]),
        "source_date": str(row["trade_date"]),
        "dominant": str(row["dominant"]),
        "confidence": float(row["confidence"]),
        "confidence_signal": float(row["confidence_signal"]),
        "risk_signal": float(row["risk_signal"]),
        "shrinkage": float(row["shrinkage"]),
        "probabilities": probs,
    }


def read_market_turnover_yi(data_date: str, *, reader: Reader | None = None) -> float | None:
    """两市成交额（亿元）代理读数：kline_index 399317 国证A指 amount/1e8（v0 口径）。

    缺席/异常返回 None（L3 评估降级 absent，不编造 0 值）。
    """
    day = validate_date_literal(data_date)
    try:
        sql = _TURNOVER_YI_SQL.format(table=resolve_table_name(_TURNOVER_CATEGORY), date=day)
        rows = list(resolve_reader(reader)(sql))
    except Exception as exc:  # noqa: BLE001 — fail-open（表名解析/通道故障=读数不可得）
        log.debug("成交额代理读数失败: %s", exc)
        return None
    if not rows or rows[0][0] is None:
        return None
    try:
        yi = float(rows[0][0]) / 1e8
    except (TypeError, ValueError):
        return None
    return yi if yi > 0 else None


def _collect_l2() -> dict[str, Any]:
    """L2 采集：板块门（sector_gate 三级放行）。

    v1 事实：sector_gate 是纯函数件（放行档位=逐票实时判定，无持久化日度门态表），
    蓝图 §四.2 原文口径=缺位如实标 absent——依赖 L2 门参与的包今日禁用（D2）。
    """
    return {"status": "absent", "layer": "L2", "error": "no_persisted_gate_state_v1"}


def _collect_l3(market_state: str | None, turnover_yi: float | None) -> dict[str, Any]:
    """L3 采集：六段×四开关环境开关查表（evaluate_environment_switches，纯函数零改动）。"""
    if not market_state or turnover_yi is None:
        return {"status": "absent", "layer": "L3",
                "error": "state_or_turnover_missing", "layer_note": "六段状态或成交额代理缺席"}
    try:
        from zephyr.signal_ashare.core.environment_switch import evaluate_environment_switches

        switches = evaluate_environment_switches(market_state, turnover_yi)
        return {"status": "ok", "layer": "L3", "switches": switches.to_dict(),
                "turnover_yi_proxy": turnover_yi}
    except Exception as exc:  # noqa: BLE001 — 查表入参非法/模块异常=该层门关
        return {"status": "absent", "layer": "L3", "error": type(exc).__name__}


def _collect_l4(data_date: str, *, reader: Reader | None = None) -> dict[str, Any]:
    """L4 采集：alloc_budget_daily 当日 run 切片 + 约束栈登记（蓝图 §四.2 L4）。"""
    day = validate_date_literal(data_date)
    sql = _L4_DAY_SLICE_SQL.format(table="c1_backtest.alloc_budget_daily", date=day)
    try:
        rows = list(resolve_reader(reader)(sql))
    except Exception as exc:  # noqa: BLE001 — fail-open
        return {"status": "absent", "layer": "L4", "error": type(exc).__name__}
    if not rows:
        return {"status": "absent", "layer": "L4", "error": "no_day_run",
                "layer_note": "当日无 alloc run（预算无来源=不出预算，D3 由编排器接管）"}
    strategies = [
        {"strategy_id": str(r[0]), "run_id": str(r[1]), "allocation": float(r[2]),
         "global_shrinkage": float(r[3]), "effective_budget": float(r[4]),
         "allocated_capital": float(r[5])}
        for r in rows
    ]
    constraints: dict[str, Any] = {"status": "absent", "error": "not_wired_v1"}
    try:  # 约束栈默认面只读登记（firm_risk_aggregator 约束存在性，非当日约束态）
        from zephyr.position.core.firm_risk_aggregator import FirmRiskAggregator

        aggregator = FirmRiskAggregator()
        limits = getattr(aggregator, "risk_limits", None)
        if isinstance(limits, dict) and limits:
            constraints = {"status": "ok", "risk_limit_keys": sorted(limits.keys())}
    except Exception as exc:  # noqa: BLE001 — 约束栈登记失败不炸预算采集
        constraints = {"status": "absent", "error": type(exc).__name__}
    return {
        "status": "ok",
        "layer": "L4",
        "n_strategies": len(strategies),
        "sum_effective_budget": round(sum(s["effective_budget"] for s in strategies), 10),
        "strategies": strategies,
        "constraint_stack": constraints,
    }


def _collect_l5() -> dict[str, Any]:
    """L5 采集：熔断/保命笼子读态（蓝图 §四.2 L5）。

    kill_switch 读态失败=按熔断保守侧处理（D6：保命件方向不猜）——本件返回
    status=absent+conservative=True，由编排器折算 no_trade。
    drawdown/price_cage/t1_sellable：v1 无持久化级位可读=absent 如实登记；
    三者均为横切持续件，本采集缺席不削弱其独立运行（蓝图 §一.5 安全底座）。
    """
    out: dict[str, Any] = {"layer": "L5"}
    try:
        from zephyr.security.access_control.kill_switch import get_kill_switch

        raw = get_kill_switch().state
        state = str(getattr(raw, "value", raw) or "").lower()
        out["kill_switch"] = {"status": "ok", "state": state or "unknown"}
    except Exception as exc:  # noqa: BLE001 — 读态失败=保守侧（D6）
        out["kill_switch"] = {"status": "absent", "error": type(exc).__name__,
                              "conservative_treatment": "tripped"}
    out["drawdown_state_machine"] = {"status": "absent", "error": "no_persisted_level_v1"}
    out["price_cage"] = {"status": "absent", "error": "per_symbol_config_v1"}
    out["t1_sellable"] = {"status": "builtin", "note": "纯函数语义件，无日度状态"}
    return out


def collect_gate_snapshot(
    data_date: str,
    *,
    market_state: str | None = None,
    turnover_yi: float | None = None,
    reader: Reader | None = None,
) -> dict[str, Any]:
    """五层门态只读采集主入口（编排器 S3 步，蓝图 §四.2）。

    Args:
        data_date: 数据日 YYYY-MM-DD（fail-closed 校验）。
        market_state: 六段状态名（L3 查表入参；None=L3 absent）。
        turnover_yi: 两市成交额亿元（None 时自动走代理读数；仍缺=L3 absent）。
        reader: 注入式只读通道（None=DatabaseService reader 角色）。

    Returns:
        JSON 可序列化 dict：{"l1".."l5", "absent_layers": [层名...]}。
        每层 status=ok|absent|builtin；absent 层由编排器降级矩阵接管（D2/D6）。
    """
    day = validate_date_literal(data_date)
    if turnover_yi is None:
        turnover_yi = read_market_turnover_yi(day, reader=reader)
    l1 = read_latest_regime_snapshot(day, reader=reader)
    l2 = _collect_l2()
    l3 = _collect_l3(market_state, turnover_yi)
    l4 = _collect_l4(day, reader=reader)
    l5 = _collect_l5()
    absent_layers = [
        layer for layer, snap in (("L1", l1), ("L2", l2), ("L3", l3), ("L4", l4))
        if snap.get("status") == "absent"
    ]
    if out_ks := l5.get("kill_switch", {}):
        if out_ks.get("status") == "absent":
            absent_layers.append("L5")
    return {"l1": l1, "l2": l2, "l3": l3, "l4": l4, "l5": l5,
            "absent_layers": absent_layers}
