# [BLUEPRINT] MOD-DT-001 | docs/03_modules/_domain_digital_twin/market_twin_simulator/blueprint.md
# [MODULE] zephyr.digital_twin.market_twin_simulator
# [DOMAIN] D_DIGITAL_TWIN
# [DEPENDENCIES] 无（纯内存/DI；BDI 规则库/情绪邻接/统计器/时钟/审计回调全注入）
# [CONSUMERS] 运行时装配批（规则库绑定 / 邻接网络注入 / 审计路由绑定 / 压测验证编排装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三撮合模式词表闭合(limit|market|call_auction); 输出载荷 simulated=True 硬标注(仅验证压测不可实盘); 撮合确定性(价格优先+时间优先, 集合竞价最大量平局取低价); 情绪传染同步更新(顺序无关); 统计校验数据不足 Fail-Closed; 审计异常不阻断; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_digital_twin/market_twin_simulator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] MarketTwinError(占位 ZA-DT-UNREGISTERED-MARKET-TWIN)——非法agent/非法订单/硬标注违反/未知邻接/非法模式/校验数据不足时抛
# [TESTS] tests/digital_twin/test_market_twin_simulator.py
# [A_module] module_id=MOD-DT-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""MarketTwinSimulator — 数字孪生市场仿真（MOD-DT-001，Phase1 规则 ABM 纯 CPU）。

B10-01864（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-DIGITALT-001，A1 §29.23）：
**多智能体**（信念→愿望→意图 BDI 规则库注入）+ **订单驱动撮合**（限价
连续竞价 / 市价吃簿 / 集合竞价三模式）+ **社交网络情绪传染**（邻接注入，
同步更新）+ **复现统计特征校验**（波动率聚集 / 肥尾 / 量自相关，注入统
计器，缺省内置纯 math 实现）+ 输出载荷 **simulated=True 硬标注**（仅验
证压测不可实盘）+ 行为写**审计回调**。Phase2/3 不施工。

查重分工（蓝图 §0）：本件=市场级 ABM 孪生体（多智能体+撮合+情绪+统计校
验协议面）；ex_core 撮合=实盘订单路由（零交集）；strategy_simulator=单
策略 NAV 回放（无多智能体/无情绪传染）。随机源不内置——需要噪声的规则
由调用方在注入规则库闭包内自带。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AuditEvent",
    "BDIRuleBook",
    "MarketTwinError",
    "MarketTwinSimulator",
    "MarketView",
    "MatchMode",
    "Order",
    "OrderSide",
    "OrderType",
    "RoundResult",
    "StylizedFactReport",
    "StylizedFactThresholds",
    "Trade",
    "TwinAgent",
    "TwinSeries",
    "TwinSnapshot",
]


class MarketTwinError(Exception):
    """数字孪生市场仿真输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DT-UNREGISTERED-MARKET-TWIN。
    """


class OrderSide(str, Enum):
    """订单方向（词表闭合）。"""

    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """订单类型（词表闭合）。"""

    LIMIT = "limit"
    MARKET = "market"


class MatchMode(str, Enum):
    """撮合模式（词表闭合）：限价连续竞价 / 市价吃簿 / 集合竞价。"""

    LIMIT = "limit"
    MARKET = "market"
    CALL_AUCTION = "call_auction"


def _check_simulated(flag: bool, *, what: str) -> None:
    """simulated=True 硬标注校验：任何输出载荷禁止伪造为实盘。"""
    if flag is not True:
        raise MarketTwinError(
            f"{what} simulated 硬标注必须为 True（仅验证压测，不可实盘），got {flag!r}"
        )


@dataclass(frozen=True)
class TwinAgent:
    """孪生智能体（frozen；cash/position 为注册初值，账本由引擎维护）。"""

    agent_id: str
    cash: float
    position: int
    sentiment: float = 0.0


@dataclass(frozen=True)
class Order:
    """订单（frozen；simulated=True 硬标注）。"""

    order_id: str
    agent_id: str
    side: OrderSide
    order_type: OrderType
    price: float | None
    quantity: int
    submitted_at: datetime.datetime | None = None
    simulated: bool = True

    def __post_init__(self) -> None:
        _check_simulated(self.simulated, what="Order")


@dataclass(frozen=True)
class Trade:
    """成交（frozen；simulated=True 硬标注）。"""

    trade_id: str
    buy_order_id: str
    sell_order_id: str
    buy_agent: str
    sell_agent: str
    price: float
    quantity: int
    mode: MatchMode
    matched_at: datetime.datetime
    simulated: bool = True

    def __post_init__(self) -> None:
        _check_simulated(self.simulated, what="Trade")


@dataclass(frozen=True)
class MarketView:
    """BDI 规则库消费的市场视图（frozen）。"""

    last_price: float
    round_no: int
    sentiments: Mapping = field(default_factory=dict)
    simulated: bool = True

    def __post_init__(self) -> None:
        _check_simulated(self.simulated, what="MarketView")


@dataclass(frozen=True)
class BDIRuleBook:
    """BDI 规则库（注入）：信念→愿望→意图三段式。

    belief_fn(agent, view) -> 公允价信念 float；
    desire_fn(agent, belief, view) -> 目标净持仓 int；
    intention_fn(agent, desire, view, order_id) -> Order | None
    （order_id 由引擎确定性供给，规则库只决定下不下单）。
    """

    belief_fn: Callable[[TwinAgent, MarketView], float]
    desire_fn: Callable[[TwinAgent, float, MarketView], int]
    intention_fn: Callable[[TwinAgent, int, MarketView, str], Order | None]


@dataclass(frozen=True)
class AuditEvent:
    """审计事件（frozen；kind 词表：order_submitted/trade_matched/sentiment_step/round_done/stylized_check）。"""

    kind: str
    detail: Mapping
    raised_at: datetime.datetime
    simulated: bool = True

    def __post_init__(self) -> None:
        _check_simulated(self.simulated, what="AuditEvent")


@dataclass(frozen=True)
class StylizedFactThresholds:
    """统计特征校验阈值（frozen；三项指标须严格大于阈值）。"""

    min_volatility_clustering: float = 0.0
    min_excess_kurtosis: float = 0.0
    min_volume_autocorr: float = 0.0


@dataclass(frozen=True)
class TwinSeries:
    """统计校验输入序列（frozen；returns 为 prices 的 log 收益）。"""

    prices: tuple[float, ...]
    volumes: tuple[float, ...]
    returns: tuple[float, ...]


@dataclass(frozen=True)
class StylizedFactReport:
    """统计特征校验报告（frozen；simulated=True 硬标注）。"""

    volatility_clustering: float
    excess_kurtosis: float
    volume_autocorr: float
    passed: bool
    detail: str
    simulated: bool = True

    def __post_init__(self) -> None:
        _check_simulated(self.simulated, what="StylizedFactReport")


@dataclass(frozen=True)
class TwinSnapshot:
    """孪生体快照（frozen；agents 按 agent_id 确定性排序 (id,cash,position,sentiment)）。"""

    agents: tuple[tuple[str, float, int, float], ...]
    last_price: float
    round_no: int
    simulated: bool = True

    def __post_init__(self) -> None:
        _check_simulated(self.simulated, what="TwinSnapshot")


@dataclass(frozen=True)
class RoundResult:
    """单轮运行结果（frozen）。"""

    round_no: int
    orders_submitted: int
    trades: tuple[Trade, ...]
    sentiments: Mapping
    simulated: bool = True

    def __post_init__(self) -> None:
        _check_simulated(self.simulated, what="RoundResult")


# ── 内置统计器（确定性纯 math，可由 stats_verifier 注入替换）──────────────────


def _autocorr_lag1(xs: tuple[float, ...] | list[float]) -> float:
    """滞后 1 皮尔逊自相关（ddof=0；n<3 或零方差 → 0.0）。"""
    n = len(xs)
    if n < 3:
        return 0.0
    a, b = xs[:-1], xs[1:]
    ma = sum(a) / (n - 1)
    mb = sum(b) / (n - 1)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (n - 1)
    va = sum((x - ma) ** 2 for x in a) / (n - 1)
    vb = sum((y - mb) ** 2 for y in b) / (n - 1)
    if va == 0 or vb == 0:
        return 0.0
    return cov / math.sqrt(va * vb)


def _excess_kurtosis(xs: tuple[float, ...] | list[float]) -> float:
    """超额峰度 m4/m2²-3（n<4 或零方差 → 0.0）。"""
    n = len(xs)
    if n < 4:
        return 0.0
    m = sum(xs) / n
    m2 = sum((x - m) ** 2 for x in xs) / n
    if m2 == 0:
        return 0.0
    m4 = sum((x - m) ** 4 for x in xs) / n
    return m4 / (m2 * m2) - 3.0


class MarketTwinSimulator:
    """数字孪生市场仿真器（Phase1 规则 ABM：BDI + 三模式撮合 + 情绪传染 + 统计校验）。"""

    def __init__(
        self,
        *,
        initial_price: float,
        rules: BDIRuleBook | None = None,
        adjacency: Mapping[str, tuple[str, ...]] | None = None,
        contagion_weight: float = 0.3,
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[AuditEvent], None] | None = None,
        stats_verifier: Callable[[TwinSeries], StylizedFactReport] | None = None,
        thresholds: StylizedFactThresholds | None = None,
    ) -> None:
        if not isinstance(initial_price, (int, float)) or isinstance(initial_price, bool) or initial_price <= 0:
            raise MarketTwinError(f"initial_price 必须为正数: {initial_price!r}")
        if not 0.0 <= contagion_weight <= 1.0:
            raise MarketTwinError(f"contagion_weight 须 ∈ [0,1]: {contagion_weight!r}")
        self._last_price = float(initial_price)
        self._rules = rules
        self._adjacency: dict[str, tuple[str, ...]] = {
            str(k): tuple(v) for k, v in (adjacency or {}).items()
        }
        self._w = float(contagion_weight)
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        self._stats_verifier = stats_verifier
        self._thresholds = thresholds or StylizedFactThresholds()
        self._cash: dict[str, float] = {}
        self._position: dict[str, int] = {}
        self._sentiment: dict[str, float] = {}
        self._orders: dict[str, Order] = {}
        self._remaining: dict[str, int] = {}
        self._order_seq: dict[str, int] = {}
        self._trades: list[Trade] = []
        self._price_history: list[float] = [self._last_price]
        self._volume_history: list[float] = [0.0]
        self._round_no = 0
        self._order_counter = 0
        self._trade_counter = 0

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _audit(self, kind: str, detail: Mapping) -> None:
        event = AuditEvent(kind=kind, detail=dict(detail), raised_at=self._clock())
        if self._audit_sink is not None:
            try:
                self._audit_sink(event)
            except Exception:  # noqa: BLE001 — 审计异常不阻断仿真
                _log.exception("audit_sink 写审计失败: %s", kind)

    def _agent_of(self, agent_id: str) -> None:
        if agent_id not in self._cash:
            raise MarketTwinError(f"未知 agent: {agent_id!r}（未注册）")

    # ── 智能体注册 ────────────────────────────────────────────────────────

    def register_agent(self, agent: TwinAgent) -> None:
        """注册智能体：id 非空唯一；cash/position 非负。"""
        if not agent.agent_id:
            raise MarketTwinError("agent_id 为空")
        if agent.agent_id in self._cash:
            raise MarketTwinError(f"agent 重复注册: {agent.agent_id!r}")
        if agent.cash < 0:
            raise MarketTwinError(f"cash 不能为负: {agent.cash!r}")
        if agent.position < 0:
            raise MarketTwinError(f"position 不能为负: {agent.position!r}")
        self._cash[agent.agent_id] = float(agent.cash)
        self._position[agent.agent_id] = int(agent.position)
        self._sentiment[agent.agent_id] = float(agent.sentiment)

    # ── 订单 ─────────────────────────────────────────────────────────────

    def submit_order(self, order: Order) -> None:
        """订单入簿：限价单须正价；市价单不得带价；数量正；agent 已注册。"""
        if not order.order_id:
            raise MarketTwinError("order_id 为空")
        if order.order_id in self._orders:
            raise MarketTwinError(f"order_id 重复: {order.order_id!r}")
        self._agent_of(order.agent_id)
        if not isinstance(order.side, OrderSide) or not isinstance(order.order_type, OrderType):
            raise MarketTwinError(f"非法订单方向/类型: {order.side!r}/{order.order_type!r}")
        if not isinstance(order.quantity, int) or isinstance(order.quantity, bool) or order.quantity <= 0:
            raise MarketTwinError(f"quantity 须为正整数: {order.quantity!r}")
        if order.order_type is OrderType.LIMIT:
            if order.price is None or order.price <= 0:
                raise MarketTwinError(f"限价单价格须为正: {order.price!r}")
        elif order.price is not None:
            raise MarketTwinError(f"市价单不得携带价格: {order.price!r}")
        if order.submitted_at is None:
            order = replace(order, submitted_at=self._clock())
        self._order_counter += 1
        self._orders[order.order_id] = order
        self._remaining[order.order_id] = order.quantity
        self._order_seq[order.order_id] = self._order_counter
        self._audit("order_submitted", {
            "order_id": order.order_id, "agent_id": order.agent_id,
            "side": order.side.value, "order_type": order.order_type.value,
            "price": order.price, "quantity": order.quantity,
        })

    # ── 撮合（三模式） ────────────────────────────────────────────────────

    def _resting(self, side: OrderSide, order_type: OrderType) -> list[Order]:
        return [
            self._orders[oid]
            for oid, rem in self._remaining.items()
            if rem > 0
            and self._orders[oid].side is side
            and self._orders[oid].order_type is order_type
        ]

    def _execute(self, buy: Order, sell: Order, price: float, qty: int, mode: MatchMode) -> Trade:
        self._trade_counter += 1
        trade = Trade(
            trade_id=f"trd-{self._trade_counter:05d}",
            buy_order_id=buy.order_id, sell_order_id=sell.order_id,
            buy_agent=buy.agent_id, sell_agent=sell.agent_id,
            price=price, quantity=qty, mode=mode, matched_at=self._clock(),
        )
        self._remaining[buy.order_id] -= qty
        self._remaining[sell.order_id] -= qty
        self._cash[buy.agent_id] -= price * qty
        self._position[buy.agent_id] += qty
        self._cash[sell.agent_id] += price * qty
        self._position[sell.agent_id] -= qty
        self._last_price = price
        self._trades.append(trade)
        self._audit("trade_matched", {
            "trade_id": trade.trade_id, "price": price, "quantity": qty,
            "buy_agent": trade.buy_agent, "sell_agent": trade.sell_agent,
            "mode": mode.value,
        })
        return trade

    def _match_continuous(self) -> list[Trade]:
        """限价连续竞价：价格优先+时间优先；成交价=先挂（被动）方价格。"""
        trades: list[Trade] = []
        buys = sorted(
            self._resting(OrderSide.BUY, OrderType.LIMIT),
            key=lambda o: (-o.price, self._order_seq[o.order_id]),
        )
        sells = sorted(
            self._resting(OrderSide.SELL, OrderType.LIMIT),
            key=lambda o: (o.price, self._order_seq[o.order_id]),
        )
        i = j = 0
        while i < len(buys) and j < len(sells):
            b, s = buys[i], sells[j]
            if b.price < s.price:
                break
            qty = min(self._remaining[b.order_id], self._remaining[s.order_id])
            passive = b if self._order_seq[b.order_id] < self._order_seq[s.order_id] else s
            trades.append(self._execute(b, s, passive.price, qty, MatchMode.LIMIT))
            if self._remaining[b.order_id] == 0:
                i += 1
            if self._remaining[s.order_id] == 0:
                j += 1
        return trades

    def _match_market(self) -> list[Trade]:
        """市价吃簿：市价单按时间序吃对手限价簿，未成交部分取消（IOC）。"""
        trades: list[Trade] = []
        for mkt_side, lim_side in (
            (OrderSide.BUY, OrderSide.SELL),
            (OrderSide.SELL, OrderSide.BUY),
        ):
            markets = sorted(
                self._resting(mkt_side, OrderType.MARKET),
                key=lambda o: self._order_seq[o.order_id],
            )
            for m in markets:
                limits = sorted(
                    self._resting(lim_side, OrderType.LIMIT),
                    key=lambda o: (
                        o.price if lim_side is OrderSide.SELL else -o.price,
                        self._order_seq[o.order_id],
                    ),
                )
                for lim in limits:
                    if self._remaining[m.order_id] == 0:
                        break
                    qty = min(self._remaining[m.order_id], self._remaining[lim.order_id])
                    buy, sell = (m, lim) if mkt_side is OrderSide.BUY else (lim, m)
                    trades.append(self._execute(buy, sell, lim.price, qty, MatchMode.MARKET))
                self._remaining[m.order_id] = 0  # 未成交部分取消
        return trades

    def _match_call_auction(self) -> list[Trade]:
        """集合竞价：最大成交量统一出清价（平局取低价），按统一价结算。"""
        bids = self._resting(OrderSide.BUY, OrderType.LIMIT) + self._resting(OrderSide.BUY, OrderType.MARKET)
        asks = self._resting(OrderSide.SELL, OrderType.LIMIT) + self._resting(OrderSide.SELL, OrderType.MARKET)
        if not bids or not asks:
            return []
        candidates = sorted({o.price for o in bids + asks if o.price is not None})
        if any(o.order_type is OrderType.MARKET for o in bids + asks):
            candidates = sorted(set(candidates) | {self._last_price})

        def _buy_qty(p: float) -> int:
            return sum(
                self._remaining[o.order_id]
                for o in bids
                if o.order_type is OrderType.MARKET or o.price >= p
            )

        def _sell_qty(p: float) -> int:
            return sum(
                self._remaining[o.order_id]
                for o in asks
                if o.order_type is OrderType.MARKET or o.price <= p
            )

        best_price, best_qty = None, 0
        for p in candidates:  # 升序遍历 → 平局天然取低价（确定性）
            vol = min(_buy_qty(p), _sell_qty(p))
            if vol > best_qty:
                best_price, best_qty = p, vol
        if best_price is None or best_qty == 0:
            return []

        buy_side = sorted(
            bids,
            key=lambda o: (
                0 if o.order_type is OrderType.MARKET else 1,
                -(o.price or 0.0), self._order_seq[o.order_id],
            ),
        )
        sell_side = sorted(
            asks,
            key=lambda o: (
                0 if o.order_type is OrderType.MARKET else 1,
                o.price or 0.0, self._order_seq[o.order_id],
            ),
        )
        trades: list[Trade] = []
        left = best_qty
        for b in buy_side:
            if left == 0:
                break
            for s in sell_side:
                if left == 0 or self._remaining[b.order_id] == 0:
                    break
                if self._remaining[s.order_id] == 0:
                    continue
                qty = min(self._remaining[b.order_id], self._remaining[s.order_id], left)
                trades.append(self._execute(b, s, best_price, qty, MatchMode.CALL_AUCTION))
                left -= qty
        for o in bids + asks:  # 市价单未成交部分取消；限价单保留回簿
            if o.order_type is OrderType.MARKET:
                self._remaining[o.order_id] = 0
        return trades

    def match(self, mode: MatchMode) -> tuple[Trade, ...]:
        """按模式撮合簿内订单（限价/市价/集合竞价词表闭合）。"""
        if not isinstance(mode, MatchMode):
            raise MarketTwinError(f"非法撮合模式: {mode!r}（词表闭合 limit|market|call_auction）")
        if mode is MatchMode.LIMIT:
            trades = self._match_continuous()
        elif mode is MatchMode.MARKET:
            trades = self._match_market()
        else:
            trades = self._match_call_auction()
        return tuple(trades)

    # ── 情绪传染（邻接注入，同步更新） ────────────────────────────────────

    def step_sentiment(self) -> Mapping[str, float]:
        """情绪传染一步：new = (1-w)·own + w·mean(邻接)；无邻接不变；同步更新。"""
        new: dict[str, float] = {}
        for agent_id in sorted(self._sentiment):
            neighbors = self._adjacency.get(agent_id, ())
            for nb in neighbors:
                if nb not in self._sentiment:
                    raise MarketTwinError(f"邻接引用未知 agent: {agent_id!r} -> {nb!r}")
            if not neighbors:
                new[agent_id] = self._sentiment[agent_id]
            else:
                mean_nb = sum(self._sentiment[nb] for nb in neighbors) / len(neighbors)
                new[agent_id] = (1.0 - self._w) * self._sentiment[agent_id] + self._w * mean_nb
        self._sentiment.update(new)
        self._audit("sentiment_step", {"sentiments": dict(sorted(new.items()))})
        return dict(sorted(new.items()))

    def sentiment_of(self, agent_id: str) -> float:
        """单 agent 情绪查询（未知 → Fail-Closed）。"""
        self._agent_of(agent_id)
        return self._sentiment[agent_id]

    # ── 运行（BDI → 下单 → 撮合 → 情绪） ─────────────────────────────────

    def run_round(self, mode: MatchMode = MatchMode.LIMIT) -> RoundResult:
        """单轮：BDI 规则库产意图（按 agent_id 排序）→ 下单 → 撮合 → 情绪传染。"""
        if self._rules is None:
            raise MarketTwinError("rules 未注入（BDI 规则库缺失，Fail-Closed 不空转）")
        self._round_no += 1
        view = MarketView(
            last_price=self._last_price, round_no=self._round_no,
            sentiments=dict(sorted(self._sentiment.items())),
        )
        submitted = 0
        for agent_id in sorted(self._cash):
            agent = TwinAgent(
                agent_id=agent_id, cash=self._cash[agent_id],
                position=self._position[agent_id], sentiment=self._sentiment[agent_id],
            )
            belief = float(self._rules.belief_fn(agent, view))
            desire = int(self._rules.desire_fn(agent, belief, view))
            order_id = f"ord-r{self._round_no:04d}-{agent_id}"
            order = self._rules.intention_fn(agent, desire, view, order_id)
            if order is not None:
                self.submit_order(order)
                submitted += 1
        trades = self.match(mode)
        sentiments = self.step_sentiment()
        self._price_history.append(self._last_price)
        self._volume_history.append(float(sum(t.quantity for t in trades)))
        self._audit("round_done", {
            "round_no": self._round_no, "orders_submitted": submitted,
            "trades": len(trades), "last_price": self._last_price,
        })
        return RoundResult(
            round_no=self._round_no, orders_submitted=submitted,
            trades=trades, sentiments=sentiments,
        )

    # ── 统计特征校验（注入统计器优先，缺省内置） ──────────────────────────

    def verify_stylized_facts(
        self,
        prices: tuple[float, ...] | list[float] | None = None,
        volumes: tuple[float, ...] | list[float] | None = None,
    ) -> StylizedFactReport:
        """复现统计特征校验：波动率聚集 / 肥尾 / 量自相关。

        序列缺省取仿真记录；可显式注入序列（纯内存 DI）。价格点 <5
        （收益 <4）Fail-Closed——校验不可执行即防护未生效，拒绝出具结论。
        """
        px = tuple(float(p) for p in (prices if prices is not None else self._price_history))
        vol = tuple(float(v) for v in (volumes if volumes is not None else self._volume_history))
        if len(px) < 5:
            raise MarketTwinError(
                f"统计校验数据不足: 价格点 {len(px)} < 5（Fail-Closed 拒出结论）"
            )
        rets = tuple(math.log(px[i] / px[i - 1]) for i in range(1, len(px)))
        series = TwinSeries(prices=px, volumes=vol, returns=rets)
        if self._stats_verifier is not None:
            report = self._stats_verifier(series)
            if not isinstance(report, StylizedFactReport):
                raise MarketTwinError(f"stats_verifier 返回非法类型: {type(report)!r}")
        else:
            vc = _autocorr_lag1(tuple(abs(r) for r in rets))
            ek = _excess_kurtosis(rets)
            va = _autocorr_lag1(vol)
            th = self._thresholds
            passed = (
                vc > th.min_volatility_clustering
                and ek > th.min_excess_kurtosis
                and va > th.min_volume_autocorr
            )
            report = StylizedFactReport(
                volatility_clustering=vc, excess_kurtosis=ek, volume_autocorr=va,
                passed=passed,
                detail="三项指标均超阈值" if passed else "存在未达阈值指标",
            )
        self._audit("stylized_check", {
            "volatility_clustering": report.volatility_clustering,
            "excess_kurtosis": report.excess_kurtosis,
            "volume_autocorr": report.volume_autocorr,
            "passed": report.passed,
        })
        return report

    # ── 查询 ─────────────────────────────────────────────────────────────

    @property
    def trades(self) -> tuple[Trade, ...]:
        """全部成交（时间序）。"""
        return tuple(self._trades)

    def snapshot(self) -> TwinSnapshot:
        """孪生体快照（agents 按 id 确定性排序；simulated=True 硬标注）。"""
        return TwinSnapshot(
            agents=tuple(
                (aid, self._cash[aid], self._position[aid], self._sentiment[aid])
                for aid in sorted(self._cash)
            ),
            last_price=self._last_price,
            round_no=self._round_no,
        )
