# [BLUEPRINT] MOD-SIM-025 | docs/03_modules/_domain_simulation/blueprint.md
# [MODULE] zephyr.simulation.limit_board_queue
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES]
# [CONSUMERS] 预留(paper matching引擎, 53号§3.2撮合Step②, SHADOW前置)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 封板时同向单排队时间优先FIFO;市价触板转限价排队;逆向单封板价即成交;P(fill)=min(1,counter_volume/(queue_ahead+order_size))
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LimitBoardQueueError(ZA-SIM-0025)
# [TESTS] tests/simulation/test_limit_board_queue.py
# [TTL] permanent
# [A_module] module_id=MOD-SIM-025 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [ALGO_FLOW]
# I1: 订单(side/qty/price/order_type) + 最新价/昨收/涨跌停幅度
# I2: 封单量/对手盘流量(成交概率估算输入, 调用方注入)
# A1: detect_board_state(最新价 vs 昨收×(1±limit_pct) 判板态, 0.01最小价位取整)
# A2: route_order(涨停:BUY排队/SELL即成交;跌停:SELL排队/BUY即成交;市价触板转限价排队)
# A3: LimitBoardQueue.on_counter_volume(对手盘流量FIFO冲销队列, 支持部分成交)
# A4: estimate_fill_probability(min(1, counter_volume/(queue_ahead+order_size)), 53号§3.2公式②)
# O1: OrderRoutingResult(FILLED/QUEUED/CONVERTED_QUEUED) + 队列快照 + 成交概率
# [/ALGO_FLOW]
"""Paper Matching 涨跌停排队引擎(BM-SIM-08)

职责(53号 memo §3.2 撮合 Step② + 公式②, SHADOW 阶段前置):
  - 显式复现 A 股涨跌停硬约束: 涨停板仅撮合 bid 队列(买单按时间优先排队),
    跌停板仅撮合 ask 队列; 触及涨跌停的市价单转为限价单排队
  - 封板成交概率估算: P(fill) ≈ min(1, counter_volume / (queue_ahead + order_size))
  - 消除"模拟通过但实盘被拒"的伪通过(paper-live parity)

约束:
  - 函数级 MVP: 不重建完整撮合引擎, 正常板态(NORMAL)的撮合委托既有链路,
    本模块只承载封板排队语义
  - 价格比较按 A 股最小价位 0.01 元取整; 数量单位为股(整手校验归 OrderManager)
  - 输入注入式: 封单量/对手盘流量由调用方供给, 不连接外部行情

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/53_simulation_live_path.md §3.2
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum

__all__ = [
    "LimitBoardQueueError",
    "BoardState",
    "OrderSide",
    "OrderType",
    "RouteAction",
    "OrderRoutingResult",
    "QueuedOrder",
    "LimitBoardQueue",
    "detect_board_state",
    "route_order",
    "estimate_fill_probability",
    "DEFAULT_LIMIT_PCT",
    "BOARD_LIMIT_PCT",
    "PRICE_TICK",
    "THIN_QUEUE_HANDS",
]

# A 股最小价位(元)
PRICE_TICK = 0.01
# 默认涨跌停幅度(主板 10%)
DEFAULT_LIMIT_PCT = 0.10
# 板块涨跌停幅度三档(53号 §3.2: 10%/20%/30%)
BOARD_LIMIT_PCT: dict[str, float] = {
    "main": 0.10,
    "chinext": 0.20,  # 创业板
    "star": 0.20,  # 科创板
    "bse": 0.30,  # 北交所
}
# 经验阈值: 排队前方 > 1000 手 → 成交概率 < 10%(53号 §3.2 公式②注记, 1手=100股)
THIN_QUEUE_HANDS = 1000


class LimitBoardQueueError(Exception):
    """涨跌停排队引擎错误(输入非法)"""

    error_code = "ZA-SIM-0025"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


class BoardState(str, Enum):
    """板态(涨跌停状态)"""

    NORMAL = "NORMAL"
    LIMIT_UP = "LIMIT_UP"
    LIMIT_DOWN = "LIMIT_DOWN"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class RouteAction(str, Enum):
    """订单路由结果"""

    FILLED = "FILLED"  # 即成交(正常板态或封板逆向单)
    QUEUED = "QUEUED"  # 限价单入队排队
    CONVERTED_QUEUED = "CONVERTED_QUEUED"  # 市价触板转限价入队


@dataclass(frozen=True)
class QueuedOrder:
    """队列中的订单(不可变)

    Attributes:
        order_id: 订单标识
        side: 排队方向(涨停板=BUY 队列, 跌停板=SELL 队列)
        qty: 委托数量(股)
        limit_price: 排队限价(涨/跌停价)
        seq: 入队序号(时间优先 FIFO 依据)
    """

    order_id: str
    side: OrderSide
    qty: int
    limit_price: float
    seq: int


@dataclass(frozen=True)
class OrderRoutingResult:
    """订单路由结果(不可变)

    Attributes:
        action: 路由动作(FILLED/QUEUED/CONVERTED_QUEUED)
        fill_price: 成交价(action=FILLED 时有效)
        fill_qty: 成交数量(action=FILLED 时=委托量, 函数级 MVP 不支持路由即部分成交)
        queue_position: 排队位置(action≠FILLED 时有效, 1=队首)
        queue_ahead: 排队前方累计委托量(股)
        reason: 路由理由
    """

    action: RouteAction
    fill_price: float | None = None
    fill_qty: int = 0
    queue_position: int = 0
    queue_ahead: int = 0
    reason: str = ""


def _round_tick(price: float) -> float:
    """按最小价位 0.01 元取整(四舍五入到分)

    口径与交易所一致：十进制 ROUND_HALF_UP（非 Python 银行家舍入），
    消除 x.xx5 边界 1 分差异（2026-08-20 AI-NIGHT-001 包3.2 登记项#3）。
    """
    return float(Decimal(str(price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def limit_up_price(prev_close: float, limit_pct: float = DEFAULT_LIMIT_PCT) -> float:
    """涨停价 = 昨收 × (1 + limit_pct), 四舍五入到分(ROUND_HALF_UP)

    用 Decimal 精确乘法（str 转换），避免 float 二进制误差翻转 x.xx5
    边界（如 10.35×1.1 真值 11.385 → 交易所 11.39，float 得 11.38）。
    """
    _validate_prev_close_pct(prev_close, limit_pct)
    pc = Decimal(str(prev_close)) * (Decimal("1") + Decimal(str(limit_pct)))
    return float(pc.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def limit_down_price(prev_close: float, limit_pct: float = DEFAULT_LIMIT_PCT) -> float:
    """跌停价 = 昨收 × (1 - limit_pct), 四舍五入到分(ROUND_HALF_UP)

    如 8.45×0.9 真值 7.605 → 交易所 7.61（float 银行家得 7.60）。
    """
    _validate_prev_close_pct(prev_close, limit_pct)
    pc = Decimal(str(prev_close)) * (Decimal("1") - Decimal(str(limit_pct)))
    return float(pc.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _validate_prev_close_pct(prev_close: float, limit_pct: float) -> None:
    if prev_close <= 0:
        raise LimitBoardQueueError(f"prev_close必须>0, got {prev_close}")
    if not 0 < limit_pct < 1:
        raise LimitBoardQueueError(f"limit_pct必须在(0,1), got {limit_pct}")


def detect_board_state(
    last_price: float,
    prev_close: float,
    limit_pct: float = DEFAULT_LIMIT_PCT,
) -> BoardState:
    """判定板态: 最新价触及涨停/跌停价(按 0.01 取整后比较)

    Args:
        last_price: 最新价
        prev_close: 昨收价(>0)
        limit_pct: 涨跌停幅度(默认主板 10%; 创业板/科创板 20%, 北交所 30%)

    Returns:
        BoardState: LIMIT_UP / LIMIT_DOWN / NORMAL

    Raises:
        LimitBoardQueueError: 价格或幅度非法
    """
    _validate_prev_close_pct(prev_close, limit_pct)
    if last_price <= 0:
        raise LimitBoardQueueError(f"last_price必须>0, got {last_price}")
    up = limit_up_price(prev_close, limit_pct)
    down = limit_down_price(prev_close, limit_pct)
    if last_price >= up:
        return BoardState.LIMIT_UP
    if last_price <= down:
        return BoardState.LIMIT_DOWN
    return BoardState.NORMAL


def estimate_fill_probability(
    queue_ahead: int,
    order_size: int,
    counter_volume: int,
) -> float:
    """封板成交概率估算(53号 §3.2 公式②)

    P(fill) ≈ min(1, counter_volume / (queue_ahead + order_size))
      - queue_ahead: 排队前方累计委托(股), 粗估=封单量×下单时刻距开盘比例
      - counter_volume: 对手盘流量(股), 开板时涌入的成交
      - 经验阈值: queue_ahead > 1000 手(=100,000 股)时 P(fill) 通常 < 10%

    Args:
        queue_ahead: 排队前方累计委托量(股, >=0)
        order_size: 本单委托量(股, >0)
        counter_volume: 对手盘流量(股, >=0)

    Returns:
        float: 成交概率 ∈ [0, 1]

    Raises:
        LimitBoardQueueError: 参数非法
    """
    if queue_ahead < 0:
        raise LimitBoardQueueError(f"queue_ahead必须>=0, got {queue_ahead}")
    if order_size <= 0:
        raise LimitBoardQueueError(f"order_size必须>0, got {order_size}")
    if counter_volume < 0:
        raise LimitBoardQueueError(f"counter_volume必须>=0, got {counter_volume}")
    denom = queue_ahead + order_size
    return min(1.0, counter_volume / denom)


def route_order(
    side: OrderSide,
    qty: int,
    board_state: BoardState,
    limit_price: float,
    order_type: OrderType = OrderType.LIMIT,
    queue_ahead: int = 0,
) -> OrderRoutingResult:
    """封板订单路由(53号 §3.2 Step②)

    规则:
      - NORMAL: 不干预(委托既有撮合链路, 本函数返回 FILLED 占位语义, 实际成交
        价格由既有撮合决定——函数级 MVP 仅承载封板语义)
      - LIMIT_UP(涨停封板): BUY 单入 bid 队列排队(市价单转限价单);
        SELL 单以涨停价即成交(对手=bid 队列)
      - LIMIT_DOWN(跌停封板): SELL 单入 ask 队列排队(市价单转限价单);
        BUY 单以跌停价即成交(对手=ask 队列)

    Args:
        side: 订单方向
        qty: 委托数量(股, >0)
        board_state: 当前板态
        limit_price: 涨/跌停价(封板态有效; NORMAL 态忽略)
        order_type: 订单类型(LIMIT/MARKET)
        queue_ahead: 入队时排队前方累计委托量(股, >=0)

    Returns:
        OrderRoutingResult: 路由结果

    Raises:
        LimitBoardQueueError: 参数非法
    """
    if not isinstance(side, OrderSide):
        raise LimitBoardQueueError(f"side必须是OrderSide: {side!r}")
    if not isinstance(board_state, BoardState):
        raise LimitBoardQueueError(f"board_state必须是BoardState: {board_state!r}")
    if not isinstance(order_type, OrderType):
        raise LimitBoardQueueError(f"order_type必须是OrderType: {order_type!r}")
    if qty <= 0:
        raise LimitBoardQueueError(f"qty必须>0, got {qty}")
    if queue_ahead < 0:
        raise LimitBoardQueueError(f"queue_ahead必须>=0, got {queue_ahead}")

    if board_state is BoardState.NORMAL:
        return OrderRoutingResult(
            action=RouteAction.FILLED,
            fill_price=None,
            fill_qty=qty,
            reason="正常板态,委托既有撮合链路(本模块仅承载封板排队语义)",
        )

    if limit_price <= 0:
        raise LimitBoardQueueError(f"封板态limit_price必须>0, got {limit_price}")

    # 封板时同向单排队, 逆向单即成交
    same_direction = (board_state is BoardState.LIMIT_UP and side is OrderSide.BUY) or (
        board_state is BoardState.LIMIT_DOWN and side is OrderSide.SELL
    )
    if not same_direction:
        board_name = "涨停" if board_state is BoardState.LIMIT_UP else "跌停"
        return OrderRoutingResult(
            action=RouteAction.FILLED,
            fill_price=limit_price,
            fill_qty=qty,
            reason=f"{board_name}封板,逆向{side.value}单以{board_name}价{limit_price}即成交",
        )

    if order_type is OrderType.MARKET:
        action = RouteAction.CONVERTED_QUEUED
        reason_prefix = "市价单触板转限价单排队"
    else:
        action = RouteAction.QUEUED
        reason_prefix = "限价单按时间优先入队"
    board_name = "涨停" if board_state is BoardState.LIMIT_UP else "跌停"
    return OrderRoutingResult(
        action=action,
        queue_position=0,  # 由 LimitBoardQueue.enqueue 赋实际位置
        queue_ahead=queue_ahead,
        reason=f"{reason_prefix}({board_name}价{limit_price}, 前方{queue_ahead}股)",
    )


@dataclass
class LimitBoardQueue:
    """封板排队队列(时间优先 FIFO)

    承载单个标的单向(涨停=bid 队列 / 跌停=ask 队列)的排队状态:
      - enqueue: 订单入队尾(时间优先)
      - on_counter_volume: 对手盘流量到达(开板/成交), FIFO 冲销队列,
        支持部分成交(队首订单部分成交后留在队首)
      - queue_ahead_of: 查询某订单前方累计委托量

    函数级 MVP: 单队列语义, 多标的/双侧队列由 paper matching 引擎组合。
    """

    board_state: BoardState
    limit_price: float
    _queue: deque = field(default_factory=deque)
    _seq: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.board_state, BoardState):
            raise LimitBoardQueueError(f"board_state必须是BoardState: {self.board_state!r}")
        if self.board_state is BoardState.NORMAL:
            raise LimitBoardQueueError("NORMAL板态无排队语义,拒绝建队")
        if self.limit_price <= 0:
            raise LimitBoardQueueError(f"limit_price必须>0, got {self.limit_price}")

    @property
    def total_queued(self) -> int:
        """队列累计未成交委托量(股)"""
        return sum(o.qty for o in self._queue)

    @property
    def n_orders(self) -> int:
        return len(self._queue)

    def enqueue(self, order_id: str, side: OrderSide, qty: int) -> QueuedOrder:
        """订单入队尾(时间优先 FIFO)

        Raises:
            LimitBoardQueueError: side 与队列方向不符或 qty 非法
        """
        expected_side = OrderSide.BUY if self.board_state is BoardState.LIMIT_UP else OrderSide.SELL
        if side is not expected_side:
            raise LimitBoardQueueError(f"{self.board_state.value}队列只接受{expected_side.value}单, got {side.value}")
        if qty <= 0:
            raise LimitBoardQueueError(f"qty必须>0, got {qty}")
        self._seq += 1
        order = QueuedOrder(
            order_id=order_id,
            side=side,
            qty=int(qty),
            limit_price=self.limit_price,
            seq=self._seq,
        )
        self._queue.append(order)
        return order

    def queue_ahead_of(self, order_id: str) -> int:
        """某订单前方累计委托量(股); 订单不在队列返回 -1"""
        ahead = 0
        for o in self._queue:
            if o.order_id == order_id:
                return ahead
            ahead += o.qty
        return -1

    def on_counter_volume(self, volume: int) -> list[tuple[str, int, float]]:
        """对手盘流量到达, FIFO 冲销队列(支持部分成交)

        Args:
            volume: 对手盘成交量(股, >=0)

        Returns:
            成交列表 [(order_id, fill_qty, fill_price)], 按时间优先顺序

        Raises:
            LimitBoardQueueError: volume 非法
        """
        if volume < 0:
            raise LimitBoardQueueError(f"volume必须>=0, got {volume}")
        fills: list[tuple[str, int, float]] = []
        remaining = volume
        while remaining > 0 and self._queue:
            head = self._queue[0]
            if head.qty <= remaining:
                fills.append((head.order_id, head.qty, head.limit_price))
                remaining -= head.qty
                self._queue.popleft()
            else:
                # 部分成交: 队首订单余量留存(位置不变, 时间优先)
                fills.append((head.order_id, remaining, head.limit_price))
                self._queue[0] = QueuedOrder(
                    order_id=head.order_id,
                    side=head.side,
                    qty=head.qty - remaining,
                    limit_price=head.limit_price,
                    seq=head.seq,
                )
                remaining = 0
        return fills
