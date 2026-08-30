# [BLUEPRINT] MOD-RK-24 | docs/03_modules/MOD-RK-24/
# [MODULE] zephyr.risk.core.risk_veto_engine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.risk_data_pipeline; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-EX-024(Pre-Execution Checker) ; MOD-L06-001(Execution Core 下单前硬拦)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 否决判定纯函数(同输入必同输出); 否决清单按priority升序; 全量评估不短路(结构化输出全部触发规则); 规则异常→RULE_ERROR否决(Fail-Closed,宁可误拦不可漏拦); 减仓方向(SELL)在限额真源缺失时放行(风险收敛不拦); 非法请求(quantity<=0/负价)→InvalidVetoRequestError
# [MODIFY-GUARD] docs/03_modules/MOD-RK-24/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidVetoRequestError
# [TESTS] tests/risk/core/test_risk_veto_engine.py
# [A_module] module_id=MOD-RK-24 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Risk Veto Engine — 风险否决引擎 (MOD-RK-24)

硬规则 veto 清单 + 优先级 + 否决理由结构化输出。消费 MOD-RK-25 统一风控快照
(RiskSnapshot)，对单笔委托意图 (OrderRiskRequest) 做下单前硬否决判定。

内置硬规则（按 priority 升序评估，全部命中全量输出，不短路）：
  P10 MISSING_PRICE         标的缺价（无法定价风险，双向否决）
  P15 LIMITS_UNAVAILABLE    限额真源缺失（BUY 否决；SELL 减仓放行——风险收敛不拦）
  P20 SUSPENDED_SYMBOL      停牌标的（双向否决，L-003/交易规则映射）
  P30 SELL_EXCEEDS_POSITION 卖出超持仓（纯多头体系无裸卖空，B-018）
  P35 T1_SELLABLE_EXCEEDED  T+1 可卖数量不足（约束四；sellable 无真源时跳过不臆测）
  P40 SINGLE_POSITION_LIMIT 买入后单仓权重超限（CTR-003 L1 硬限制，含 symbol_overrides）
  P50 GROSS_LEVERAGE_LIMIT  买入后总杠杆超限（CTR-003 L1 硬限制）

规则异常统一转 RULE_ERROR 否决（Fail-Closed：§6 可用性 vs 安全性→安全性优先）。
扩展点：RiskVetoEngine(rules=[...]) 注入自定义 VetoRule（OCP）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: request 参数
#   fields: 参数 request，类型注解 OrderRiskRequest
#   code: risk_veto_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: snapshot 参数
#   fields: 参数 snapshot，类型注解 RiskSnapshot
#   code: risk_veto_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: rules 参数
#   fields: 参数 rules，类型注解 tuple[VetoRule, ...] | None
#   code: risk_veto_engine.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: evaluated_at 参数
#   fields: 参数 evaluated_at（无注解）
#   code: risk_veto_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① VetoRule
#   name_en: VetoRule
#   intro: 否决规则协议（OCP 扩展点）。
#   desc: 否决规则协议（OCP 扩展点）。 priority 数值越小越先评估（数据完整性 < 交易约束 < 限额）。 check 返回 None=通过，返回 VetoVerdict=否决。；公共方法（定义序）: check；源…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② build_default_veto_rules
#   name_en: build_default_veto_rules
#   intro: 内置硬规则清单（priority 升序）。
#   desc: 内置硬规则清单（priority 升序）。；源码 L389-L399
#   inputs: 无参数
#   outputs: tuple[VetoRule, ...]
# - id: A3
#   name_zh: ③ evaluate_vetoes
#   name_en: evaluate_vetoes
#   intro: 评估委托请求是否被风险否决（纯函数：同输入必同输出）。
#   desc: 评估委托请求是否被风险否决（纯函数：同输入必同输出）。 全量评估所有规则（不短路），vetoes 按 priority 升序输出； 任一规则抛异常 → 转 RULE_ERROR…；源码 L420-L460
#   inputs: request snapshot rules evaluated_at
#   outputs: VetoDecision
# - id: A4
#   name_zh: ④ RiskVetoEngine
#   name_en: RiskVetoEngine
#   intro: 风险否决引擎（薄封装：规则集持有 + evaluate 入口 + 否决留痕日志）。
#   desc: 风险否决引擎（薄封装：规则集持有 + evaluate 入口 + 否决留痕日志）。；公共方法（定义序）: rules, evaluate；源码 L463-L492
#   inputs: rules
#   outputs: 返回值
#   （注：A4 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: tuple[VetoRule, ...]
#   name_en: tuple[VetoRule, ...]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-EX-024(Pre-Execution Checker) ; MOD-L06-001(Execution Core 下单前硬拦)
# - id: O2
#   name_zh: VetoDecision
#   name_en: VetoDecision
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-EX-024(Pre-Execution Checker) ; MOD-L06-001(Execution Core 下单前硬拦)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Final, Protocol

from zephyr.risk.core.risk_data_pipeline import RiskSnapshot
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "InvalidVetoRequestError",
    "OrderRiskRequest",
    "RiskVetoEngine",
    "VetoDecision",
    "VetoRule",
    "VetoVerdict",
    "build_default_veto_rules",
    "evaluate_vetoes",
]


class InvalidVetoRequestError(ZephyrBaseError):
    """否决请求非法（quantity<=0 / 负价格——请求本身脏，拒绝评估）。"""

    error_code = "ZA-RK-0071"


# ──────────────────────────────────────────────────────────────────────────────
# 契约
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class OrderRiskRequest:
    """单笔委托风控请求（下单前判定输入）。"""

    symbol: str
    side: OrderSide
    quantity: Decimal
    price: Decimal | None  # None=市价单（按快照最新价估算风险）
    strategy_id: str
    request_id: str = field(default_factory=lambda: f"vr-{uuid.uuid4().hex[:12]}")


@dataclass(frozen=True)
class VetoVerdict:
    """单条否决判定（结构化否决理由）。"""

    rule_id: str
    priority: int
    reason_code: str
    message: str
    details: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class VetoDecision:
    """否决决策输出（vetoes 为空即放行；按 priority 升序）。"""

    approved: bool
    vetoes: tuple[VetoVerdict, ...]
    rules_evaluated: int
    snapshot_id: str
    request_id: str
    evaluated_at: datetime


class VetoRule(Protocol):
    """否决规则协议（OCP 扩展点）。

    priority 数值越小越先评估（数据完整性 < 交易约束 < 限额）。
    check 返回 None=通过，返回 VetoVerdict=否决。
    """

    rule_id: str
    priority: int

    def check(self, request: OrderRiskRequest, snapshot: RiskSnapshot) -> VetoVerdict | None: ...


# ──────────────────────────────────────────────────────────────────────────────
# 内置硬规则（纯函数判定核心）
# ──────────────────────────────────────────────────────────────────────────────

_PRIORITY_MISSING_PRICE: Final = 10
_PRIORITY_LIMITS_UNAVAILABLE: Final = 15
_PRIORITY_SUSPENDED: Final = 20
_PRIORITY_SELL_EXCEEDS: Final = 30
_PRIORITY_T1_SELLABLE: Final = 35
_PRIORITY_SINGLE_POSITION: Final = 40
_PRIORITY_GROSS_LEVERAGE: Final = 50


@dataclass(frozen=True)
class _MissingPriceRule:
    rule_id: str = "hard_missing_price"
    priority: int = _PRIORITY_MISSING_PRICE

    def check(self, request: OrderRiskRequest, snapshot: RiskSnapshot) -> VetoVerdict | None:
        if request.symbol in snapshot.missing_price_symbols:
            return VetoVerdict(
                rule_id=self.rule_id,
                priority=self.priority,
                reason_code="MISSING_PRICE",
                message=f"标的缺价，无法定价风险: {request.symbol}（快照降级缺价，双向否决）",
                details=(("symbol", request.symbol),),
            )
        return None


@dataclass(frozen=True)
class _LimitsUnavailableRule:
    rule_id: str = "hard_limits_unavailable"
    priority: int = _PRIORITY_LIMITS_UNAVAILABLE

    def check(self, request: OrderRiskRequest, snapshot: RiskSnapshot) -> VetoVerdict | None:
        if snapshot.limits is None and request.side is OrderSide.BUY:
            return VetoVerdict(
                rule_id=self.rule_id,
                priority=self.priority,
                reason_code="LIMITS_UNAVAILABLE",
                message="限额真源缺失，无法验证买入合规性（Fail-Closed 拒买；减仓卖出不拦）",
                details=(("side", str(request.side)),),
            )
        return None


@dataclass(frozen=True)
class _SuspendedSymbolRule:
    rule_id: str = "hard_suspended_symbol"
    priority: int = _PRIORITY_SUSPENDED

    def check(self, request: OrderRiskRequest, snapshot: RiskSnapshot) -> VetoVerdict | None:
        if request.symbol in snapshot.suspended_held_symbols:
            return VetoVerdict(
                rule_id=self.rule_id,
                priority=self.priority,
                reason_code="SUSPENDED_SYMBOL",
                message=f"标的停牌，双向禁止委托: {request.symbol}",
                details=(("symbol", request.symbol),),
            )
        return None


@dataclass(frozen=True)
class _SellExceedsPositionRule:
    rule_id: str = "hard_sell_exceeds_position"
    priority: int = _PRIORITY_SELL_EXCEEDS

    def check(self, request: OrderRiskRequest, snapshot: RiskSnapshot) -> VetoVerdict | None:
        if request.side is not OrderSide.SELL:
            return None
        held = Decimal("0")
        for view in snapshot.positions:
            if view.symbol == request.symbol:
                held = view.quantity
                break
        if request.quantity > held:
            return VetoVerdict(
                rule_id=self.rule_id,
                priority=self.priority,
                reason_code="SELL_EXCEEDS_POSITION",
                message=(f"卖出超持仓: {request.symbol} sell={request.quantity} > held={held}（纯多头体系无裸卖空）"),
                details=(
                    ("symbol", request.symbol),
                    ("quantity", str(request.quantity)),
                    ("held", str(held)),
                ),
            )
        return None


@dataclass(frozen=True)
class _T1SellableRule:
    rule_id: str = "hard_t1_sellable"
    priority: int = _PRIORITY_T1_SELLABLE

    def check(self, request: OrderRiskRequest, snapshot: RiskSnapshot) -> VetoVerdict | None:
        if request.side is not OrderSide.SELL:
            return None
        for view in snapshot.positions:
            if view.symbol != request.symbol:
                continue
            sellable = view.sellable_quantity
            if sellable is None:
                return None  # T+1 可卖无真源 → 接口位跳过，不臆测
            if request.quantity > sellable:
                return VetoVerdict(
                    rule_id=self.rule_id,
                    priority=self.priority,
                    reason_code="T1_SELLABLE_EXCEEDED",
                    message=(
                        f"T+1 可卖不足: {request.symbol} sell={request.quantity} "
                        f"> sellable={sellable}（当日买入部分不可卖）"
                    ),
                    details=(
                        ("symbol", request.symbol),
                        ("quantity", str(request.quantity)),
                        ("sellable", str(sellable)),
                    ),
                )
            return None
        return None


def _order_value(request: OrderRiskRequest, snapshot: RiskSnapshot) -> Decimal | None:
    """委托估值：限价优先，市价取快照最新价；两者皆无→None（缺价规则已否决）。"""
    if request.price is not None:
        return request.quantity * request.price
    for view in snapshot.positions:
        if view.symbol == request.symbol and view.last_price is not None:
            return request.quantity * view.last_price
    return None


@dataclass(frozen=True)
class _SinglePositionLimitRule:
    rule_id: str = "hard_single_position_limit"
    priority: int = _PRIORITY_SINGLE_POSITION

    def check(self, request: OrderRiskRequest, snapshot: RiskSnapshot) -> VetoVerdict | None:
        if request.side is not OrderSide.BUY or snapshot.limits is None:
            return None
        order_value = _order_value(request, snapshot)
        if order_value is None:
            return None
        limits = snapshot.limits
        effective = limits.symbol_overrides.get(request.symbol, limits.max_single_position)
        current_mv = Decimal("0")
        for view in snapshot.positions:
            if view.symbol == request.symbol and view.market_value is not None:
                current_mv = view.market_value
                break
        post_weight = float((current_mv + order_value) / snapshot.nav)
        if post_weight > effective:
            return VetoVerdict(
                rule_id=self.rule_id,
                priority=self.priority,
                reason_code="SINGLE_POSITION_LIMIT",
                message=(f"买入后单仓权重超限: {request.symbol} post_weight={post_weight:.4f} > limit={effective:.4f}"),
                details=(
                    ("symbol", request.symbol),
                    ("post_weight", f"{post_weight:.6f}"),
                    ("limit", f"{effective:.6f}"),
                ),
            )
        return None


@dataclass(frozen=True)
class _GrossLeverageLimitRule:
    rule_id: str = "hard_gross_leverage_limit"
    priority: int = _PRIORITY_GROSS_LEVERAGE

    def check(self, request: OrderRiskRequest, snapshot: RiskSnapshot) -> VetoVerdict | None:
        if request.side is not OrderSide.BUY or snapshot.limits is None:
            return None
        order_value = _order_value(request, snapshot)
        if order_value is None:
            return None
        max_leverage = snapshot.limits.max_gross_leverage
        post_leverage = float((snapshot.total_market_value + order_value) / snapshot.nav)
        if post_leverage > max_leverage:
            return VetoVerdict(
                rule_id=self.rule_id,
                priority=self.priority,
                reason_code="GROSS_LEVERAGE_LIMIT",
                message=(f"买入后总杠杆超限: post_leverage={post_leverage:.4f} > limit={max_leverage:.4f}"),
                details=(
                    ("post_leverage", f"{post_leverage:.6f}"),
                    ("limit", f"{max_leverage:.6f}"),
                ),
            )
        return None


def build_default_veto_rules() -> tuple[VetoRule, ...]:
    """内置硬规则清单（priority 升序）。"""
    return (
        _MissingPriceRule(),
        _LimitsUnavailableRule(),
        _SuspendedSymbolRule(),
        _SellExceedsPositionRule(),
        _T1SellableRule(),
        _SinglePositionLimitRule(),
        _GrossLeverageLimitRule(),
    )


# ──────────────────────────────────────────────────────────────────────────────
# 判定核心（纯函数）
# ──────────────────────────────────────────────────────────────────────────────


def _validate_request(request: OrderRiskRequest) -> None:
    if request.quantity <= 0:
        raise InvalidVetoRequestError(
            f"委托数量非法: quantity={request.quantity}（必须为正）",
            details={"quantity": str(request.quantity)},
        )
    if request.price is not None and request.price <= 0:
        raise InvalidVetoRequestError(
            f"委托价格非法: price={request.price}（必须为正或 None=市价）",
            details={"price": str(request.price)},
        )


def evaluate_vetoes(
    request: OrderRiskRequest,
    snapshot: RiskSnapshot,
    rules: tuple[VetoRule, ...] | None = None,
    *,
    evaluated_at: datetime | None = None,
) -> VetoDecision:
    """评估委托请求是否被风险否决（纯函数：同输入必同输出）。

    全量评估所有规则（不短路），vetoes 按 priority 升序输出；
    任一规则抛异常 → 转 RULE_ERROR 否决（Fail-Closed，宁可误拦不可漏拦）。
    """
    _validate_request(request)
    active_rules = rules if rules is not None else build_default_veto_rules()
    ordered = sorted(active_rules, key=lambda r: r.priority)

    vetoes: list[VetoVerdict] = []
    for rule in ordered:
        try:
            verdict = rule.check(request, snapshot)
        except Exception as exc:  # noqa: BLE001 — Fail-Closed 规则异常即否决
            _logger.error("VETO_RULE_ERROR fail-closed rule=%s error=%s", rule.rule_id, exc)
            verdict = VetoVerdict(
                rule_id=rule.rule_id,
                priority=rule.priority,
                reason_code="RULE_ERROR",
                message=f"规则执行异常，Fail-Closed 否决: {rule.rule_id}",
                details=(("error", str(exc)),),
            )
        if verdict is not None:
            vetoes.append(verdict)

    vetoes.sort(key=lambda v: v.priority)
    return VetoDecision(
        approved=not vetoes,
        vetoes=tuple(vetoes),
        rules_evaluated=len(ordered),
        snapshot_id=snapshot.snapshot_id,
        request_id=request.request_id,
        evaluated_at=evaluated_at or datetime.now(tz=UTC),
    )


class RiskVetoEngine:
    """风险否决引擎（薄封装：规则集持有 + evaluate 入口 + 否决留痕日志）。"""

    def __init__(self, rules: tuple[VetoRule, ...] | list[VetoRule] | None = None) -> None:
        if rules is None:
            self._rules: tuple[VetoRule, ...] = build_default_veto_rules()
        else:
            self._rules = tuple(rules)

    @property
    def rules(self) -> tuple[VetoRule, ...]:
        return self._rules

    def evaluate(
        self,
        request: OrderRiskRequest,
        snapshot: RiskSnapshot,
        *,
        evaluated_at: datetime | None = None,
    ) -> VetoDecision:
        decision = evaluate_vetoes(request, snapshot, self._rules, evaluated_at=evaluated_at)
        if not decision.approved:
            _logger.warning(
                "RISK_VETO request=%s symbol=%s side=%s reasons=%s",
                decision.request_id,
                request.symbol,
                request.side,
                [v.reason_code for v in decision.vetoes],
            )
        return decision
