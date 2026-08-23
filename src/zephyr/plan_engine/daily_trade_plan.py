# [BLUEPRINT] MOD-PLAN-011 | 待统筹登记（缺口总账 GAP-F-09 + 45号 §4 W2）
# [MODULE] zephyr.plan_engine.daily_trade_plan
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.tomorrow_boundary_planner(TomorrowBoundary); zephyr.plan_engine.scenario_planner(ScenarioPlan/SHIFT_STANCE)
# [CONSUMERS] 盘中实时页+总览页"今日交易计划"卡（GAP-F-09 前端消费）; 作战室 W2 格内方案; GAP-F-26 执行偏差归因器（计划侧真源）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 规则模板生成（非 LLM，一句话逻辑=参数化中文模板）; 纯函数计算（不依赖 DB/CH，可单测）; firm 单票 8% 硬顶恒生效（30号 §2.2）; 数量折算 A 股整手（100 股）; 不足一手跳过+notes 留痕; 输入校验 fail-closed; 错误消息不含 session_id
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（trade_date/candidates/holdings/stance/position_scale/config 非法 fail-closed）
# [TESTS] tests/plan_engine/test_daily_trade_plan.py
# [A_module] module_id=MOD-PLAN-011 | layer=module | stability=testing | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

DailyTradePlan — 结构化"今日交易计划"生成器 (MOD-PLAN-011)

缺口总账 GAP-F-09 落码：决策链末端（边界+情景档位之后）输出结构化今日交易
计划——拟买/拟卖清单 + 方向/数量/参考价/一句话逻辑（设计文档 Q5 落地，
45号 §4 W2 格内方案消费）。规则模板生成（参数化中文模板，非 LLM）。

生成口径（写清）：
    - 拟买（候选股）：目标权重上限 = min(boundary.max_add_position × 档位缩放,
      firm 单票 8% 硬顶)（30号 §2.2 firm 硬约束在本模块即截断）；数量 = 上限
      ×总资金 / 计划买入点位（=箱体下沿 box_lower，W2"买入点位 box_lower 附近"
      口径）折算整手（100 股）；不足一手 → 跳过 + notes 留痕。
    - 拟卖（持仓股，预案=条件规则）：①止盈条目——冲必出价 must_exit_price
      （箱体上沿）全出（MOD-PLAN-001"冲上沿必出"纪律）；②减仓条目——回落破
      箱体下沿 box_lower 减仓 reduce_fraction（默认 50%）；持仓股数=权重×
      总资金/参考价折算整手；零股跳过+notes 留痕。
    - 档位缩放：调用方注入（position_scale）；resolve_stance 助手从
      ScenarioPlan.final_scenario 前缀取激活三情景条目 → (stance, 缩放)
      （缩放=SHIFT_STANCE[final_shift]，与 MOD-PLAN-005 §9.5/§9.6 同映射，
      单次缩放不重复施加）。

不做什么：不下单（输出=计划文本+结构化数据，消费方负责执行）/不做盘中实时
         信号/不改 boundary（只读消费）/不用 LLM 生成逻辑句（规则模板）。

依据: 缺口总账 GAP-F-09；45_warroom_playbook §4 W2；30号 §2.2（firm 8% 硬顶）
SSoT: depgraph MOD-PLAN-011（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 候选清单(boundary×role) + 持仓清单(weight×boundary×参考价) + 档位缩放 + 资金配置
# 特征: 目标权重上限 / 计划买入点位 / 止盈减仓触发价 / 整手数量
# 算法: 上限截断（min(缩放后加仓上限, firm 8%)）→ 数量折算整手 → 规则模板一句话逻辑
# 输出: DailyTradePlan（拟买/拟卖清单+notes，纯 frozen dataclass，JSON 可序列化）

"""

from __future__ import annotations

import datetime
import math
from dataclasses import dataclass
from typing import Any, Final, Sequence

from zephyr.plan_engine.scenario_planner import SHIFT_STANCE, ScenarioPlan
from zephyr.plan_engine.tomorrow_boundary_planner import TomorrowBoundary

__all__: Final = [
    "DailyTradePlan",
    "DailyTradePlanConfig",
    "TradePlanCandidate",
    "TradePlanHolding",
    "TradePlanItem",
    "generate_daily_trade_plan",
    "resolve_stance",
]

# ── 口径常量 ──

FIRM_SINGLE_CAP: Final = 0.08  # firm 单票 8% 硬顶（30号 §2.2）
DEFAULT_TOTAL_CAPITAL: Final = 1_000_000.0  # 默认总资金（调用方注入真实资金）
LOT_SIZE: Final = 100  # A 股整手（股）
DEFAULT_REDUCE_FRACTION: Final = 0.5  # 破下沿默认减仓比例
DEFAULT_ROLE_LABEL: Final = "主线候选"  # role 缺省时逻辑句角色标签

# final_scenario 前缀 → 激活三情景条目名（MOD-PLAN-005 9 情景语义）
_SCENARIO_PREFIX_TO_ENTRY: Final = {
    "HIGH_OPEN": "HIGH_OPEN",
    "FLAT_OPEN": "FLAT_OPEN",
    "LOW_OPEN": "LOW_OPEN",
}


def _validate_trade_date(trade_date: object) -> str:
    """交易日校验：YYYY-MM-DD 且为真实日期（fail-closed）。"""
    if not isinstance(trade_date, str):
        raise ValueError(f"trade_date 非法（须 YYYY-MM-DD 字符串）: {trade_date!r}")
    try:
        datetime.date.fromisoformat(trade_date)
    except ValueError as exc:
        raise ValueError(f"trade_date 非真实日期: {trade_date!r}") from exc
    return trade_date


def _validate_positive_finite(value: object, field: str) -> float:
    """正有限实数校验（fail-closed）。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} 非法（须正有限实数）: {value!r}")
    f = float(value)
    if not math.isfinite(f) or f <= 0:
        raise ValueError(f"{field} 非法（须正有限实数）: {value!r}")
    return f


def _floor_lot(shares: float, lot_size: int) -> int:
    """股数向下取整手。"""
    if shares <= 0:
        return 0
    return int(shares // lot_size) * lot_size


# ── 配置与输入契约 ──


@dataclass(frozen=True)
class DailyTradePlanConfig:
    """计划生成配置（默认值=设计口径）。"""

    total_capital: float = DEFAULT_TOTAL_CAPITAL  # 总资金（数量折算分母）
    firm_single_cap: float = FIRM_SINGLE_CAP  # firm 单票硬顶（30号 §2.2）
    lot_size: int = LOT_SIZE  # 整手股数

    def __post_init__(self) -> None:
        _validate_positive_finite(self.total_capital, "total_capital")
        cap = _validate_positive_finite(self.firm_single_cap, "firm_single_cap")
        if cap > 1.0:
            raise ValueError(f"firm_single_cap 非法（须 ∈(0,1]）: {self.firm_single_cap!r}")
        if isinstance(self.lot_size, bool) or not isinstance(self.lot_size, int) or self.lot_size < 1:
            raise ValueError(f"lot_size 非法（须正整数）: {self.lot_size!r}")


DEFAULT_CONFIG: Final = DailyTradePlanConfig()


@dataclass(frozen=True)
class TradePlanCandidate:
    """拟买候选输入（决策链上游：主线候选×边界）。"""

    symbol: str
    boundary: TomorrowBoundary  # MOD-PLAN-001 产出（计划买入点位/加仓上限真源）
    role: str = ""  # 梯队定位（MOD-SIG-062 龙头/中军/跟风，可空）

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError(f"symbol 非法（须非空字符串）: {self.symbol!r}")
        if not isinstance(self.boundary, TomorrowBoundary):
            raise ValueError(f"boundary 非法（须 TomorrowBoundary）: {type(self.boundary).__name__}")
        if not isinstance(self.role, str):
            raise ValueError(f"role 非法（须字符串）: {self.role!r}")


@dataclass(frozen=True)
class TradePlanHolding:
    """持仓输入（拟卖规则生成用）。"""

    symbol: str
    weight: float  # 当前仓位权重 ∈[0,1]
    boundary: TomorrowBoundary  # 该票明日边界
    reference_price: float  # 参考价（权重→股数折算基准，通常昨收）
    reduce_fraction: float = DEFAULT_REDUCE_FRACTION  # 破下沿减仓比例 ∈(0,1]

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError(f"symbol 非法（须非空字符串）: {self.symbol!r}")
        if not isinstance(self.boundary, TomorrowBoundary):
            raise ValueError(f"boundary 非法（须 TomorrowBoundary）: {type(self.boundary).__name__}")
        if isinstance(self.weight, bool) or not isinstance(self.weight, (int, float)):
            raise ValueError(f"weight 非法（须 ∈[0,1] 实数）: {self.weight!r}")
        w = float(self.weight)
        if not math.isfinite(w) or w < 0.0 or w > 1.0:
            raise ValueError(f"weight 非法（须 ∈[0,1] 实数）: {self.weight!r}")
        _validate_positive_finite(self.reference_price, "reference_price")
        frac = _validate_positive_finite(self.reduce_fraction, "reduce_fraction")
        if frac > 1.0:
            raise ValueError(f"reduce_fraction 非法（须 ∈(0,1]）: {self.reduce_fraction!r}")


# ── 输出契约 ──


@dataclass(frozen=True)
class TradePlanItem:
    """计划条目（拟买/拟卖单行，JSON 可序列化）。"""

    symbol: str
    direction: str  # BUY / SELL
    quantity: int  # 数量（股，整手）
    reference_price: float  # 参考价（买入=计划买入点位；卖出=折算基准价）
    logic: str  # 一句话逻辑（规则模板生成）
    trigger_price: float | None = None  # 条件触发价（卖出条目；买入 None）
    cap_weight: float = 0.0  # 目标权重上限（买入条目）

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return {
            "symbol": self.symbol,
            "direction": self.direction,
            "quantity": self.quantity,
            "reference_price": self.reference_price,
            "logic": self.logic,
            "trigger_price": self.trigger_price,
            "cap_weight": self.cap_weight,
        }


@dataclass(frozen=True)
class DailyTradePlan:
    """今日交易计划（GAP-F-09 输出契约，JSON 可序列化）。"""

    date: str  # 计划交易日
    stance: str  # 档位（CONSERVATIVE/DEFENSIVE/NORMAL/OFFENSIVE/AGGRESSIVE）
    position_scale: float  # 档位缩放（已施加于拟买上限）
    buy_list: tuple[TradePlanItem, ...]  # 拟买清单
    sell_list: tuple[TradePlanItem, ...]  # 拟卖清单（条件规则）
    notes: tuple[str, ...]  # 留痕（跳过原因等）

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典（前端"今日交易计划"卡消费契约）。"""
        return {
            "date": self.date,
            "stance": self.stance,
            "position_scale": self.position_scale,
            "buy_list": [i.to_dict() for i in self.buy_list],
            "sell_list": [i.to_dict() for i in self.sell_list],
            "notes": list(self.notes),
        }


# ── 档位解析（ScenarioPlan → stance/缩放）──


def resolve_stance(plan: ScenarioPlan) -> tuple[str, float]:
    """从 ScenarioPlan 解析激活档位的 (stance, position_scale)。

    final_scenario 前缀（HIGH_OPEN/FLAT_OPEN/LOW_OPEN）→ 激活三情景条目；
    缩放=SHIFT_STANCE[final_shift]（44号 §9.5/§9.6 映射，与 MOD-PLAN-005 同源）。
    三情景为空/无匹配条目 → ("NORMAL", 1.0) 降级（fail-open，不阻塞计划生成）。

    Args:
        plan: MOD-PLAN-005 产出（须 ScenarioPlan，fail-closed）。

    Returns:
        (stance, position_scale)。

    Raises:
        ValueError: plan 非 ScenarioPlan（fail-closed）。
    """
    if not isinstance(plan, ScenarioPlan):
        raise ValueError(f"plan 非法（须 ScenarioPlan）: {type(plan).__name__}")
    entry_name = next(
        (entry for prefix, entry in _SCENARIO_PREFIX_TO_ENTRY.items() if plan.final_scenario.startswith(prefix)),
        None,
    )
    for entry in plan.three_scenarios:
        if entry.name == entry_name:
            snapped = max(-1.0, min(1.0, round(entry.final_shift * 2) / 2))
            return entry.stance, SHIFT_STANCE[snapped][1]
    return "NORMAL", 1.0


# ── 计划生成（纯函数）──


def _build_buy_item(
    candidate: TradePlanCandidate,
    stance: str,
    position_scale: float,
    config: DailyTradePlanConfig,
) -> tuple[TradePlanItem | None, str | None]:
    """拟买条目：上限截断 → 整手折算 → 模板逻辑句；不足一手 → (None, note)。"""
    b = candidate.boundary
    cap = min(b.max_add_position * position_scale, float(config.firm_single_cap))
    buy_price = b.box_lower  # 计划买入点位=箱体下沿（45号 §4 W2 口径）
    if buy_price <= 0:
        return None, f"{candidate.symbol} 箱体下沿非正（{buy_price}），跳过拟买"
    quantity = _floor_lot(cap * float(config.total_capital) / buy_price, config.lot_size)
    if quantity <= 0:
        return None, (
            f"{candidate.symbol} 上限 {cap:.1%}×资金折算不足一手（{config.lot_size} 股），跳过拟买"
        )
    role_label = candidate.role.strip() or DEFAULT_ROLE_LABEL
    logic = (
        f"{role_label}·{stance}档：箱体 {b.box_lower:.2f}~{b.box_upper:.2f}，"
        f"下沿附近计划买入 {quantity} 股（加仓上限 {cap:.1%}）；"
        f"禁加价 {b.no_add_price:.2f}，必出 {b.must_exit_price:.2f}"
    )
    return (
        TradePlanItem(
            symbol=candidate.symbol,
            direction="BUY",
            quantity=quantity,
            reference_price=round(buy_price, 4),
            logic=logic,
            trigger_price=None,
            cap_weight=round(cap, 6),
        ),
        None,
    )


def _build_sell_items(
    holding: TradePlanHolding,
    config: DailyTradePlanConfig,
) -> tuple[list[TradePlanItem], list[str]]:
    """拟卖条目：止盈全出 + 破下沿减仓两条条件规则；零股跳过+notes。"""
    b = holding.boundary
    shares = _floor_lot(
        holding.weight * float(config.total_capital) / holding.reference_price,
        config.lot_size,
    )
    if shares <= 0:
        return [], [f"{holding.symbol} 持仓折算零股（weight={holding.weight:.2%}），拟卖跳过"]
    items: list[TradePlanItem] = [
        TradePlanItem(
            symbol=holding.symbol,
            direction="SELL",
            quantity=shares,
            reference_price=round(holding.reference_price, 4),
            logic=(
                f"止盈纪律：冲必出价 {b.must_exit_price:.2f} 全出 {shares} 股（箱体上沿，MOD-PLAN-001 纪律）"
            ),
            trigger_price=round(b.must_exit_price, 4),
            cap_weight=0.0,
        )
    ]
    notes: list[str] = []
    reduce_qty = _floor_lot(shares * holding.reduce_fraction, config.lot_size)
    if reduce_qty > 0:
        items.append(
            TradePlanItem(
                symbol=holding.symbol,
                direction="SELL",
                quantity=reduce_qty,
                reference_price=round(holding.reference_price, 4),
                logic=(
                    f"风控减仓：回落破箱体下沿 {b.box_lower:.2f} 减仓 "
                    f"{holding.reduce_fraction:.0%}（{reduce_qty} 股）"
                ),
                trigger_price=round(b.box_lower, 4),
                cap_weight=0.0,
            )
        )
    else:
        notes.append(
            f"{holding.symbol} 减仓 {holding.reduce_fraction:.0%} 折算不足一手，减仓条目跳过（止盈条目保留）"
        )
    return items, notes


def generate_daily_trade_plan(
    trade_date: str,
    candidates: Sequence[TradePlanCandidate],
    holdings: Sequence[TradePlanHolding],
    *,
    stance: str = "NORMAL",
    position_scale: float = 1.0,
    config: DailyTradePlanConfig | None = None,
) -> DailyTradePlan:
    """生成结构化"今日交易计划"（MOD-PLAN-011 主入口，纯函数）。

    Args:
        trade_date: 计划交易日（YYYY-MM-DD，fail-closed）。
        candidates: 拟买候选清单（TradePlanCandidate 序列）。
        holdings: 持仓清单（TradePlanHolding 序列）。
        stance: 档位名（非空字符串；经 resolve_stance 从 ScenarioPlan 解析注入）。
        position_scale: 档位缩放（正有限实数；施加于 boundary.max_add_position
            后再经 firm 8% 硬顶截断——单次缩放，调用方勿重复施加）。
        config: 生成配置（None=默认 DailyTradePlanConfig()）。

    Returns:
        DailyTradePlan（拟买/拟卖清单+notes，JSON 可序列化）。

    Raises:
        ValueError: 任一输入非法（fail-closed）。
    """
    v_date = _validate_trade_date(trade_date)
    if not isinstance(stance, str) or not stance.strip():
        raise ValueError(f"stance 非法（须非空字符串）: {stance!r}")
    v_scale = _validate_positive_finite(position_scale, "position_scale")
    cfg = config if config is not None else DEFAULT_CONFIG
    if not isinstance(cfg, DailyTradePlanConfig):
        raise ValueError(f"config 非法（须 DailyTradePlanConfig 或 None）: {type(cfg).__name__}")
    for c in candidates:
        if not isinstance(c, TradePlanCandidate):
            raise ValueError(f"candidates 元素非法（须 TradePlanCandidate）: {type(c).__name__}")
    for h in holdings:
        if not isinstance(h, TradePlanHolding):
            raise ValueError(f"holdings 元素非法（须 TradePlanHolding）: {type(h).__name__}")

    buy_list: list[TradePlanItem] = []
    sell_list: list[TradePlanItem] = []
    notes: list[str] = []
    for c in candidates:
        item, note = _build_buy_item(c, stance.strip(), v_scale, cfg)
        if item is not None:
            buy_list.append(item)
        if note is not None:
            notes.append(note)
    for h in holdings:
        items, h_notes = _build_sell_items(h, cfg)
        sell_list.extend(items)
        notes.extend(h_notes)

    return DailyTradePlan(
        date=v_date,
        stance=stance.strip(),
        position_scale=v_scale,
        buy_list=tuple(buy_list),
        sell_list=tuple(sell_list),
        notes=tuple(notes),
    )
