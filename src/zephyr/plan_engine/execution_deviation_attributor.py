# [BLUEPRINT] MOD-PLAN-016 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-26 行）
# [MODULE] zephyr.plan_engine.execution_deviation_attributor
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.daily_trade_plan(DailyTradePlan，计划侧真源，MOD-PLAN-011)
# [CONSUMERS] （候选：盘后复盘页「执行回看」卡——计划 vs 实际 + 偏差归类）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 归因六类封闭（按计划/滑点/流动性/风控/拒单/未执行）；滑点恶化方向双边一致（BUY=(avg−ref)/ref，SELL=(ref−avg)/ref，恶化>0）；多笔成交按数量 VWAP 聚合；计划外成交不参评仅 notes 留痕；数量 0 且无任何记录=未执行（原因待核，不硬编）；输入校验 fail-closed；纯函数不触库；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-26 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] plan 非 DailyTradePlan / executions·vetoes 元素类型非法→ValueError（fail-closed）
# [TESTS] tests/plan_engine/test_execution_deviation_attributor.py
# [A_module] module_id=MOD-PLAN-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-PLAN-016 — 执行偏差归因器（GAP-F-26，复盘页「执行回看」后端）。

计划 vs 实际对账（规则 MVP，纯函数）：
- **计划侧**：MOD-PLAN-011 DailyTradePlan（buy_list/sell_list 结构化条目，
  reference_price=计划参考价真源）。
- **实际侧**：ExecutionRecord 注入（消费方从执行引擎委托/成交记录映射——
  CTR-005 Fill/拒单/撤单；status ∈ filled/partial/rejected/cancelled）。
- **归因六类**（封闭）：
  ① 按计划 ON_PLAN=足额成交且 |滑点| ≤ 阈值；
  ② 滑点 SLIPPAGE=足额成交但滑点恶化超阈（BUY 买贵为正/SELL 卖低为正，
  双边恶化方向一致）；
  ③ 流动性 LIQUIDITY=0 < 成交 < 计划（部分成交，含 status=partial）；
  ④ 风控 RISK_BLOCK=零成交 + veto 记录（veto 优先于拒单——先被拦就没到券商）；
  ⑤ 拒单 REJECTED=零成交 + rejected 记录；
  ⑥ 未执行 UNFILLED=零成交且无任何记录（原因待核，不硬编）。
- 计划外成交（计划无此 symbol+direction 条目）不参评，仅 notes 留痕。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 DailyTradePlan（MOD-PLAN-011 产出）
# - id: I2 ExecutionRecord 列表（成交/拒单/撤单）
# - id: I3 VetoRecord 列表（风控拦截，注入位）
# 层: 算法
# - id: A1 (symbol,direction) 匹配 + 多笔 VWAP 聚合
# - id: A2 六类归因 + 汇总
# 层: 输出
# - id: O1 ExecutionDeviationReport（items + category_counts + notes）
# [/ALGO_FLOW]
#
# 边:
# I1,I2,I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final, Sequence

from zephyr.plan_engine.daily_trade_plan import DailyTradePlan, TradePlanItem

logger = logging.getLogger(__name__)

__all__: Final = [
    "CATEGORY_LIQUIDITY",
    "CATEGORY_ON_PLAN",
    "CATEGORY_REJECTED",
    "CATEGORY_RISK_BLOCK",
    "CATEGORY_SLIPPAGE",
    "CATEGORY_UNFILLED",
    "DeviationConfig",
    "ExecutionDeviationItem",
    "ExecutionDeviationReport",
    "ExecutionRecord",
    "VetoRecord",
    "attribute_execution_deviation",
]

#: 归因六类（封闭集合）
CATEGORY_ON_PLAN: Final[str] = "按计划"
CATEGORY_SLIPPAGE: Final[str] = "滑点"
CATEGORY_LIQUIDITY: Final[str] = "流动性"
CATEGORY_RISK_BLOCK: Final[str] = "风控"
CATEGORY_REJECTED: Final[str] = "拒单"
CATEGORY_UNFILLED: Final[str] = "未执行"


@dataclass(frozen=True, slots=True)
class DeviationConfig:
    """归因配置（初拍阈值，待实盘标定）。"""

    slippage_threshold_pct: float = 1.0  # 恶化滑点 > 1% → 滑点偏差（有利滑点不归偏差）


@dataclass(frozen=True, slots=True)
class ExecutionRecord:
    """实际执行记录（CTR-005 Fill/拒单/撤单的消费侧映射）。"""

    symbol: str
    direction: str  # BUY / SELL
    filled_quantity: int
    avg_price: float = 0.0  # VWAP（无成交 0.0）
    status: str = "filled"  # filled/partial/rejected/cancelled
    reason: str = ""  # 拒单/撤单原因（券商原文留痕）


@dataclass(frozen=True, slots=True)
class VetoRecord:
    """风控拦截记录（risk veto 注入位）。"""

    symbol: str
    reason: str = ""


@dataclass(frozen=True, slots=True)
class ExecutionDeviationItem:
    """单计划条目偏差归因。"""

    symbol: str
    direction: str
    planned_quantity: int
    filled_quantity: int
    fill_ratio: float
    reference_price: float
    avg_price: float
    slippage_pct: float  # 恶化方向为正（BUY 买贵/SELL 卖低）
    category: str  # 六类封闭
    note: str = ""


@dataclass(frozen=True, slots=True)
class ExecutionDeviationReport:
    """执行偏差归因输出（复盘页消费，不接交易）。"""

    date: str
    items: list[ExecutionDeviationItem] = field(default_factory=list)
    category_counts: dict[str, int] = field(default_factory=dict)
    planned_count: int = 0
    executed_count: int = 0  # 足额成交条目数
    planned_value: float = 0.0
    executed_value: float = 0.0
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 主核（纯函数）
# ------------------------------------------------------------------


def _classify(
    planned: TradePlanItem,
    filled_qty: int,
    avg_price: float,
    statuses: list[str],
    reasons: list[str],
    veto: VetoRecord | None,
    cfg: DeviationConfig,
) -> tuple[str, float, str]:
    """六类归因（返回 (category, slippage_pct, note)）。"""
    ref = float(planned.reference_price)
    if filled_qty > 0 and ref > 0:
        if planned.direction == "BUY":
            slippage = (avg_price - ref) / ref * 100.0
        else:
            slippage = (ref - avg_price) / ref * 100.0
    else:
        slippage = 0.0
    if filled_qty <= 0:
        if veto is not None:
            return CATEGORY_RISK_BLOCK, slippage, f"风控拦截：{veto.reason or '未注明'}"
        if "rejected" in statuses:
            return CATEGORY_REJECTED, slippage, f"拒单：{'; '.join(r for r in reasons if r) or '未注明'}"
        if statuses and all(s == "cancelled" for s in statuses):
            return CATEGORY_UNFILLED, slippage, "委托已撤单（原因待核）"
        return CATEGORY_UNFILLED, slippage, "无成交记录（原因待核）"
    if filled_qty < planned.quantity or "partial" in statuses:
        return CATEGORY_LIQUIDITY, slippage, f"部分成交 {filled_qty}/{planned.quantity}"
    if slippage > cfg.slippage_threshold_pct:
        return CATEGORY_SLIPPAGE, slippage, f"滑点 {slippage:+.2f}% 超阈 +{cfg.slippage_threshold_pct}%（恶化方向）"
    return CATEGORY_ON_PLAN, slippage, ""


def attribute_execution_deviation(
    plan: DailyTradePlan,
    executions: Sequence[ExecutionRecord],
    vetoes: Sequence[VetoRecord] | None = None,
    config: DeviationConfig | None = None,
) -> ExecutionDeviationReport:
    """执行偏差归因主核（纯函数，不触库）。

    Args:
        plan: MOD-PLAN-011 产出（fail-closed）。
        executions: 实际执行记录（成交/拒单/撤单；同条目多笔按数量 VWAP 聚合）。
        vetoes: 风控拦截记录注入位（None=无 veto 腿）。
        config: 配置（None 用默认）。

    Returns:
        ExecutionDeviationReport。

    Raises:
        ValueError: plan/executions/vetoes 元素类型非法（fail-closed）。
    """
    if not isinstance(plan, DailyTradePlan):
        raise ValueError(f"plan 非法（须 DailyTradePlan）: {type(plan).__name__}")
    cfg = config or DeviationConfig()
    veto_map: dict[str, VetoRecord] = {}
    for v in vetoes or []:
        if not isinstance(v, VetoRecord):
            raise ValueError(f"vetoes 元素非法（须 VetoRecord）: {type(v).__name__}")
        veto_map[v.symbol] = v

    exec_map: dict[tuple[str, str], list[ExecutionRecord]] = {}
    notes: list[str] = []
    planned_keys = {(i.symbol, i.direction) for i in plan.buy_list + plan.sell_list}
    for e in executions:
        if not isinstance(e, ExecutionRecord):
            raise ValueError(f"executions 元素非法（须 ExecutionRecord）: {type(e).__name__}")
        key = (e.symbol, e.direction)
        if key not in planned_keys:
            notes.append(f"计划外成交 {e.symbol} {e.direction} {e.filled_quantity} 股，不参评仅留痕")
        exec_map.setdefault(key, []).append(e)

    items: list[ExecutionDeviationItem] = []
    planned_value = 0.0
    executed_value = 0.0
    executed_count = 0
    for planned in plan.buy_list + plan.sell_list:
        planned_value += planned.quantity * planned.reference_price
        records = exec_map.get((planned.symbol, planned.direction), [])
        filled_qty = sum(int(r.filled_quantity) for r in records)
        if filled_qty > 0:
            avg_price = sum(int(r.filled_quantity) * float(r.avg_price) for r in records) / filled_qty
        else:
            avg_price = 0.0
        category, slippage, note = _classify(
            planned,
            filled_qty,
            avg_price,
            [r.status for r in records],
            [r.reason for r in records],
            veto_map.get(planned.symbol),
            cfg,
        )
        fill_ratio = round(filled_qty / planned.quantity, 4) if planned.quantity > 0 else 0.0
        executed_value += filled_qty * avg_price
        if filled_qty >= planned.quantity and planned.quantity > 0:
            executed_count += 1
        items.append(
            ExecutionDeviationItem(
                symbol=planned.symbol,
                direction=planned.direction,
                planned_quantity=planned.quantity,
                filled_quantity=filled_qty,
                fill_ratio=fill_ratio,
                reference_price=planned.reference_price,
                avg_price=round(avg_price, 4),
                slippage_pct=round(slippage, 4),
                category=category,
                note=note,
            )
        )
    category_counts: dict[str, int] = {}
    for i in items:
        category_counts[i.category] = category_counts.get(i.category, 0) + 1
    return ExecutionDeviationReport(
        date=plan.date,
        items=items,
        category_counts=category_counts,
        planned_count=len(items),
        executed_count=executed_count,
        planned_value=round(planned_value, 2),
        executed_value=round(executed_value, 2),
        notes=notes,
    )
