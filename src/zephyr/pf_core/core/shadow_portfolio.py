# [BLUEPRINT] MOD-PF-007 | docs/03_modules/_domain_portfolio_core/performance_attribution_engine/blueprint.md
# [MODULE] zephyr.pf_core.core.shadow_portfolio
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.shared.contracts.execution_report(CTR-P1-007,decision_timestamp=IS 锚点);
#   zephyr.shared.foundation.errors
# [CONSUMERS] FAC-E9 影子组合工作流（实盘/sim 账本旁只读对照，M7 接线后经
#   ExecutionReportSource 拉取口供数；sim/paper 面=sim_trade_log 适配器）;
#   tests/pf_core/test_shadow_portfolio.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯只读对照件：零触真实订单路径（实盘四禁），零写库零网络——本件只算不执行；
#   四分解守恒不变量：total_shortfall = delay + execution + opportunity + fee（逐 symbol 对平，
#   容差 1e-6，破恒等式即抛 ShadowDataIncompleteError——禁静默不平账）；
#   锚点缺席=显式 unavailable（decision 锚缺→delay/execution/opportunity 三项不判，只出
#   fee 与持仓差——禁墙钟伪造决策时刻/禁用 0 冒充缺失，R-014 同款病禁复发）；
#   方向语义=不利为正（BUY 买贵/SELL 卖贱=正成本）；sim 适配器复用账本 cost_paid 真值
#   不复算成本常量（成本口径唯一真源=sim_paper_ledger，越权复算即漂移）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ShadowDataIncompleteError(strict 模式锚点缺失/守恒破裂)；非 strict 降级出
#   带 unavailable 标记的部分分解
# [TESTS] tests/pf_core/test_shadow_portfolio.py
# [A_module] module_id=MOD-PF-030 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] shadow-portfolio-mod-pf-030-20260927
"""shadow_portfolio——影子组合只读对照引擎（FAC-E9 差件治本第一段，2026-09-27）。

真源：b2_f28 挖矿簿 FAC-E9"影子组合工作流未建"+algo_note"实盘账本旁跑信号复刻影子
组合做对照"+IS 分解（Perold 1988：延迟/执行/机会/费用）。

对照语义（Millennium/QuantConnect 对账范式）：

    决策时刻（decision_timestamp）──假想──▶ 影子腿：P0 全量成交（零滑点零费用口径另注）
         │
         实际执行（first fill→avg fill，实际费用）
         ▼
    度量时刻（measurement price，默认当日收盘/期末价）
         ──对照──▶ 四分解：延迟 + 执行 + 机会 + 费用 ≡ 实际盈亏 − 影子盈亏（守恒）

两个供数适配器（本件不做采集，采集归 M7/sim 管线——施工单另列）：
  - from_execution_reports：实盘面，走 CTR-P1-007 契约（decision_timestamp=2026-09-27
    V2 扩展即 IS 延迟项锚点）；
  - from_sim_trade_log：sim/paper 面假想流对照（真单流=账本行，决策锚缺→降级部分分解）。

日账管线/持久化表/实盘接线=施工单移交（本窗交付=可测引擎+契约适配，零采集零落库）。

# [ALGO_FLOW] external: docs/03_modules/_domain_portfolio_core/algo_flow/shadow_portfolio.yaml
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Final, Iterable, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ShadowDataIncompleteError",
    "ShadowDecision",
    "ShadowFill",
    "ShadowComparison",
    "ShadowPortfolioEngine",
]

_CONSERVATION_TOL = 1e-6


class ShadowDataIncompleteError(ZephyrBaseError):
    """影子对照数据不完备（strict 模式锚点缺失/守恒破裂）——fail-closed。"""

    error_code = "ZA-PF-0087"


@dataclass(frozen=True)
class ShadowDecision:
    """决策锚（影子腿起点）：决策时刻以 decision_price 全量成交的假想单。"""

    symbol: str
    side: str  # BUY | SELL
    quantity: float  # 计划量（股）
    decision_price: float | None  # None=锚点缺席（降级模式）
    decision_ts: datetime | None = None
    paper_fee: float = 0.0  # 影子腿计入的费用（默认零费用口径，另注）


@dataclass(frozen=True)
class ShadowFill:
    """实际腿成交片段（聚合成一腿即可，多片段取首笔为执行起点锚）。"""

    quantity: float
    price: float
    fee: float = 0.0
    ts: datetime | None = None


@dataclass(frozen=True)
class ShadowComparison:
    """单 symbol 对照结果（不利为正；None=锚点缺席未判）。"""

    symbol: str
    side: str
    planned_quantity: float
    filled_quantity: float
    decision_available: bool
    delay_cost: float | None = None
    execution_cost: float | None = None
    opportunity_cost: float | None = None
    fee_cost: float | None = None
    total_shortfall: float | None = None
    actual_pnl: float | None = None
    shadow_pnl: float | None = None
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "planned_quantity": self.planned_quantity,
            "filled_quantity": self.filled_quantity,
            "decision_available": self.decision_available,
            "delay_cost": self.delay_cost,
            "execution_cost": self.execution_cost,
            "opportunity_cost": self.opportunity_cost,
            "fee_cost": self.fee_cost,
            "total_shortfall": self.total_shortfall,
            "actual_pnl": self.actual_pnl,
            "shadow_pnl": self.shadow_pnl,
            "notes": list(self.notes),
        }


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ShadowDataIncompleteError(f"{name} 必须为有限数值", details={"value": repr(value)})
    return float(value)


class ShadowPortfolioEngine:
    """影子组合对照引擎：真单流 vs 假设流的四分解对照（纯函数，零副作用）。"""

    def compare_symbol(
        self,
        decision: ShadowDecision,
        actual_fills: Sequence[ShadowFill],
        measurement_price: float,
        *,
        strict: bool = False,
    ) -> ShadowComparison:
        """单 symbol 四分解对照。

        Args:
            decision: 决策锚（计划方向/数量/决策价）。
            actual_fills: 实际成交片段（≥1 笔；首笔=执行起点锚）。
            measurement_price: 度量时刻价格（期末/收盘）。
            strict: True=锚点缺失即抛 ShadowDataIncompleteError（fail-closed）；
                False=降级出带 unavailable 的部分分解。

        Returns:
            ShadowComparison（守恒：total = delay + execution + opportunity + fee）。
        """
        symbol = decision.symbol
        if decision.side not in ("BUY", "SELL"):
            raise ShadowDataIncompleteError(f"{symbol} side 越枚举（BUY|SELL）", details={"side": decision.side})
        planned_q = _finite(decision.quantity, "planned_quantity")
        if planned_q < 0:
            raise ShadowDataIncompleteError(f"{symbol} 计划量不能为负")
        if not actual_fills:
            raise ShadowDataIncompleteError(f"{symbol} 实际腿为空——无对照面（禁空转伪造零差）")
        measurement = _finite(measurement_price, "measurement_price")
        if measurement <= 0:
            raise ShadowDataIncompleteError(f"{symbol} 度量价必须为正", details={"value": measurement})

        filled_q = sum(_finite(f.quantity, "fill.quantity") for f in actual_fills)
        first_price = _finite(actual_fills[0].price, "fill.price")
        avg_price = sum(f.price * f.quantity for f in actual_fills) / filled_q if filled_q > 0 else 0.0
        actual_fee = sum(_finite(f.fee, "fill.fee") for f in actual_fills)

        notes: list[str] = []
        decision_available = decision.decision_price is not None
        if not decision_available:
            notes.append("decision_anchor_missing: 决策价缺席——延迟/执行/机会三项不判（禁伪造锚点）")
            if strict:
                raise ShadowDataIncompleteError(f"{symbol} strict 模式要求决策锚在位")

        delay_cost: float | None = None
        execution_cost: float | None = None
        opportunity_cost: float | None = None
        total_shortfall: float | None = None
        actual_pnl: float | None = None
        shadow_pnl: float | None = None

        if decision_available:
            p0 = _finite(decision.decision_price or 0.0, "decision_price")
            if p0 <= 0:
                raise ShadowDataIncompleteError(f"{symbol} 决策价必须为正", details={"value": p0})
            sign = 1.0 if decision.side == "BUY" else -1.0
            missed_q = max(planned_q - filled_q, 0.0)
            # 延迟=决策价→首笔成交价漂移 × 成交量；执行=首笔→均价的额外滑点；机会=决策价→
            # 度量价漂移 × 未成交量；全部"不利为正"。SELL 反号（卖贱=不利）。
            delay_cost = sign * (first_price - p0) * filled_q
            execution_cost = sign * (avg_price - first_price) * filled_q
            opportunity_cost = sign * (measurement - p0) * missed_q
            fee_cost = actual_fee - decision.paper_fee
            total_shortfall = delay_cost + execution_cost + opportunity_cost + fee_cost
            # 守恒验证：影子盈亏−实际盈亏（=不利成本口径的四分解和）必须对平
            actual_pnl = sign * (measurement - avg_price) * filled_q - actual_fee
            shadow_pnl = sign * (measurement - p0) * planned_q - decision.paper_fee
            residual = (shadow_pnl - actual_pnl) - total_shortfall
            if abs(residual) > _CONSERVATION_TOL * max(1.0, abs(total_shortfall)):
                raise ShadowDataIncompleteError(f"{symbol} 四分解守恒破裂（residual={residual}）——禁静默不平账")
        else:
            fee_cost = actual_fee - decision.paper_fee

        if filled_q > planned_q:
            notes.append(f"overfill: 成交 {filled_q} 超计划 {planned_q}（超量部分入 delay/execution 口径）")

        return ShadowComparison(
            symbol=symbol,
            side=decision.side,
            planned_quantity=planned_q,
            filled_quantity=filled_q,
            decision_available=decision_available,
            delay_cost=delay_cost,
            execution_cost=execution_cost,
            opportunity_cost=opportunity_cost,
            fee_cost=fee_cost,
            total_shortfall=total_shortfall,
            actual_pnl=actual_pnl,
            shadow_pnl=shadow_pnl,
            notes=tuple(notes),
        )

    def compare_portfolio(self, comparisons: Iterable[ShadowComparison], *, strict: bool = False) -> dict[str, Any]:
        """组合级聚合：四分解逐项求和（None 项跳过并计数——缺席面如实呈现）。"""

        def _sum(attr: str) -> tuple[float | None, int]:
            vals = [getattr(c, attr) for c in comparisons]
            known = [v for v in vals if v is not None]
            return (sum(known), len(vals) - len(known))

        total, missing = _sum("total_shortfall")
        delay, d_missing = _sum("delay_cost")
        execution, e_missing = _sum("execution_cost")
        opportunity, o_missing = _sum("opportunity_cost")
        fee, f_missing = _sum("fee_cost")
        out: dict[str, Any] = {
            "symbols": len(list(comparisons)) if hasattr(comparisons, "__len__") else None,
            "total_shortfall": total,
            "delay_cost": delay,
            "execution_cost": execution,
            "opportunity_cost": opportunity,
            "fee_cost": fee,
            "degraded_symbols": max(d_missing, e_missing, o_missing) if d_missing or e_missing or o_missing else 0,
        }
        if strict and missing:
            raise ShadowDataIncompleteError(f"组合聚合 strict 模式：{missing} 个 symbol 决策锚缺席")
        return out


# ── 供数适配器（只读；本件不做采集）──────────────────────────────────


def from_execution_reports(
    reports: Iterable[Any],
    measurement_prices: dict[str, float],
    engine: ShadowPortfolioEngine | None = None,
) -> list[ShadowComparison]:
    """实盘面适配：CTR-P1-007 契约行 → 对照（decision_timestamp/decision 价=intended_price）。

    同 order_id 幂等由调用方保证（契约层 ReplacingMergeTree 同键替换口径）；
    measurement_prices 缺席的 symbol=跳过并记 note（度量锚是另一根独立锚）。
    """
    engine = engine or ShadowPortfolioEngine()
    by_order: dict[str, list[Any]] = {}
    for r in reports:
        by_order.setdefault(r.order_id, []).append(r)
    out: list[ShadowComparison] = []
    for order_id, group in by_order.items():
        rep = group[0]
        if rep.symbol not in measurement_prices:
            continue
        decision_ts = None
        if rep.decision_timestamp:
            try:
                decision_ts = datetime.fromisoformat(str(rep.decision_timestamp))
            except ValueError:
                decision_ts = None  # 非法时戳=缺席（禁伪造）
        decision = ShadowDecision(
            symbol=rep.symbol,
            side=rep.direction,
            quantity=float(rep.intended_quantity),
            decision_price=float(rep.intended_price),
            decision_ts=decision_ts,
            paper_fee=0.0,
        )
        fills = [
            ShadowFill(quantity=float(rep.actual_quantity), price=float(rep.vwap_price), fee=float(rep.commission))
        ]
        out.append(engine.compare_symbol(decision, fills, measurement_prices[rep.symbol]))
    return out


def _sim_group_legs(rows: Iterable[dict[str, Any]]) -> dict[tuple[str, str], dict[str, list[dict[str, Any]]]]:
    """sim 行按 (strategy_id, symbol) 归组分侧（entry/exit）。"""
    legs: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = {}
    for row in rows:
        key = (str(row.get("strategy_id") or ""), str(row.get("symbol") or ""))
        action = str(row.get("action") or "")
        legs.setdefault(key, {"entry": [], "exit": []}).setdefault(action, []).append(row)
    return legs


def _sim_compare_leg(
    engine: ShadowPortfolioEngine,
    strategy_id: str,
    symbol: str,
    entries: list[dict[str, Any]],
    exits: list[dict[str, Any]],
    measurement_price: float,
) -> ShadowComparison | None:
    """单腿对照（降级模式：账本无决策锚，禁伪造零延迟；成本真值=cost_paid 禁复算）。"""
    bought = sum(float(r.get("shares") or 0.0) for r in entries)
    if bought <= 0:
        return None
    sold = sum(float(r.get("shares") or 0.0) for r in exits)
    fees = sum(float(r.get("cost_paid") or 0.0) for r in entries) + sum(float(r.get("cost_paid") or 0.0) for r in exits)
    all_rows = entries + exits
    gross_value = sum(float(r.get("shares") or 0.0) * float(r.get("price") or 0.0) for r in all_rows)
    gross_shares = sum(float(r.get("shares") or 0.0) for r in all_rows)
    leg_price = (gross_value / gross_shares) if gross_shares > 0 else measurement_price
    decision = ShadowDecision(
        symbol=symbol,
        side="SELL" if exits else "BUY",
        quantity=sold if exits else bought,
        decision_price=None,  # 账本无决策锚——降级模式，禁伪造
        paper_fee=0.0,
    )
    fills = [ShadowFill(quantity=sold or bought, price=leg_price, fee=fees)]
    comparison = engine.compare_symbol(decision, fills, measurement_price)
    return ShadowComparison(
        symbol=f"{strategy_id}:{symbol}",
        side=comparison.side,
        planned_quantity=comparison.planned_quantity,
        filled_quantity=comparison.filled_quantity,
        decision_available=False,
        fee_cost=comparison.fee_cost,
        notes=comparison.notes + (f"sim_leg_strategy={strategy_id}",),
    )


def from_sim_trade_log(
    rows: Iterable[dict[str, Any]],
    measurement_prices: dict[str, float],
    engine: ShadowPortfolioEngine | None = None,
) -> list[ShadowComparison]:
    """sim/paper 面适配：sim_trade_log 行（dict 形）→ 降级对照。

    账本行按 (strategy_id, symbol) 归组，entry/exit 配对成腿；账本无决策价锚
    （方案C=收盘价成交）→ decision_price=None 降级模式，只出 fee 与持仓差真值，
    禁用收盘价冒充决策价伪造零延迟（口径铁律）。
    """
    engine = engine or ShadowPortfolioEngine()
    out: list[ShadowComparison] = []
    for (strategy_id, symbol), sides in _sim_group_legs(rows).items():
        if symbol not in measurement_prices:
            continue
        comparison = _sim_compare_leg(
            engine, strategy_id, symbol, sides.get("entry") or [], sides.get("exit") or [], measurement_prices[symbol]
        )
        if comparison is not None:
            out.append(comparison)
    return out


if __name__ == "__main__":  # 入口豁免（孤儿门）；worked example=BUY 延迟+费用两分解演示
    _engine = ShadowPortfolioEngine()
    _cmp = _engine.compare_symbol(
        ShadowDecision(symbol="600000.SH", side="BUY", quantity=100, decision_price=10.0),
        [ShadowFill(quantity=100, price=10.6, fee=5.0)],
        measurement_price=11.0,
    )
    import json as _json

    print(_json.dumps(_cmp.as_dict(), ensure_ascii=False, indent=2))
