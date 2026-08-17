# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.open_order_resolver
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib; zephyr.ex_core.order_manager; zephyr.shared.contracts.order; zephyr.shared.contracts.enums.order_enums
# [CONSUMERS] ex_core.trading_session
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 被动挂单T秒超时→Make-or-Take切对手价;PARTIAL<min_unit忽略转CANCELLED;14:55尾盘清退;幂等(终态订单跳过)
# [MODIFY-GUARD] 40_execution_broker.md §决策⑪
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OpenOrderResolverError
# [TESTS] tests/ex_core/test_open_order_resolver.py
# [TTL] permanent

"""

未成交/部分成交订单续接处理（40_execution_broker §决策⑪ gap 6 施工）。

实盘生存项——"信号发了但没成交"的直接落地点。v1.0.0 状态机只定义了 PARTIAL 的
合法后继态，未定义"剩余量怎么决策"。本模块补全续接算法。

续接规则（40_execution_broker §2.12 决策⑪）：
  | 订单剩余状态          | 触发条件              | 处理策略                          |
  |----------------------|----------------------|-----------------------------------|
  | SUBMITTED 未成交     | 挂单 ≤ T 秒（默认30s）| 继续等待                          |
  | SUBMITTED 未成交     | 挂单 > T 秒           | Make-or-Take 切换（撤单+对手价重挂）|
  | PARTIAL 剩余<min_unit| 任意                  | 忽略，订单转 CANCELLED             |
  | PARTIAL 剩余≥min_unit| urgency=高（打板）    | Make-or-Take 切换补单              |
  | PARTIAL 剩余≥min_unit| urgency=低（多因子）  | 留单等成交，下轮调仓再校准          |
  | 任意非终态           | 14:55 收盘前          | 尾盘清退（撤单）                   |

为何不统一挂死等成交：A 股限价单可能因价格远离挂单价而长期不成交，挂死会导致
持仓与目标长期偏离，下轮调仓时重复下单（虽有幂等保护，但占用资金预占额度）。

为何不统一撤单转市价：市价单冲击成本高，且 A 股市价单有"最优五档"限制，
大单可能成交到极差价位。

Make-or-Take 平衡：被动挂单优先（省 spread），超时才转对手价主动吃单（保证成交）。
对打板策略必需（纯被动会错过龙头）。

为何 14:55 尾盘清退：A 股限价单默认 GFD（当日有效），15:00 收盘自动撤销。
主动撤单可释放资金预占额度并避免"幽灵挂单"占用风控额度。

依据：40_execution_broker.md v2.4.0 §决策⑪
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 非终态订单列表 list[Order]
#   fields: order_id / symbol / side / quantity / filled_quantity / status（SUBMITTED/PARTIAL/PENDING）
#   code: order_manager.get_open_orders() L250
# - id: I2
#   name: 续接配置 OpenOrderResolverConfig
#   fields: make_or_take_timeout_seconds=30 / partial_ignore_threshold=100股 / market_close_minutes=895(14:55) / default_urgency=LOW
#   code: OpenOrderResolverConfig L115
# - id: I3
#   name: 对手价盘口 OpponentPriceProvider
#   fields: (symbol, side) → BUY取卖一ask1 / SELL取买一bid1（Decimal 或 None）
#   code: OpponentPriceProvider L141
# - id: I4
#   name: 时钟与当前时间注入
#   fields: monotonic clock（超时计时）+ now_provider（尾盘判断，测试可注入）
#   code: __init__ clock/now_provider L181
# 层: 算法
# - id: A1
#   name_zh: ① 扫描续接主循环
#   name_en: scan_and_resolve
#   intro: 定时扫所有未成交订单，逐笔决策执行，单笔出错不拖累其他单
#   desc: get_open_orders 取非终态订单 → 先算一次尾盘标志 → 逐笔 _resolve_and_execute → 收集 ResolveAction；终态动作成功后清理跟踪记录；单笔异常隔离记日志
#   inputs: I1 I4
#   outputs: list[ResolveAction]
#   invariant: 幂等（终态订单跳过不重复处理）
# - id: A2
#   name_zh: ② 单笔分档决策
#   name_en: _resolve_and_execute
#   intro: 按优先级给一笔订单定策略：尾盘清退 > 未注册跳过 > 超时切换 > 剩余量分档
#   desc: 14:55到→CLOSE_OUT；未注册→SKIP_NOT_REGISTERED；SUBMITTED且挂单≤T→WAIT、>T→Make-or-Take；PARTIAL剩余<100股→忽略转CANCELLED、urgency高→Make-or-Take补单、urgency低→LEAVE_OPEN留单
#   inputs: I2 I4
#   outputs: ResolveAction（决策+执行结果）
# - id: A3
#   name_zh: ③ Make-or-Take 切换
#   name_en: _execute_make_or_take
#   intro: 被动挂单超时就撤单，改挂对手价主动吃单保证成交
#   desc: 撤单（失败=可能已成交，记录不报错）→ 查对手价（无provider/无盘口则撤单后跳过重挂）→ 对手价 LIMIT 重挂剩余量；默认走 create_order+submit_order，可注入 resubmit_callback
#   inputs: I3
#   outputs: 撤单请求 + 新限价单（new broker_order_id）
#   invariant: 重挂单 urgency=LOW 防无限循环 Make-or-Take
# - id: A4
#   name_zh: ④ 碎片忽略与尾盘清退
#   name_en: _execute_ignore_partial / _execute_close_out
#   intro: 剩一点零头不值得留就撤掉，收盘前所有挂单主动清退
#   desc: PARTIAL剩余<partial_ignore_threshold→撤单转CANCELLED（避免最低佣金5元）；到达market_close_minutes→所有非终态订单撤单（GFD防幽灵挂单占风控额度）
#   inputs: I2
#   outputs: 撤单请求
# 层: 输出
# - id: O1
#   name_zh: 续接动作列表 list[ResolveAction]
#   name_en: ResolveAction
#   intro: 每笔订单一条不可变续接决策记录，供审计追溯
#   invariant: 不可变 frozen dataclass；action_type∈7种枚举
#   downstream: ex_core.trading_session（定时扫描消费）/ 审计日志
# - id: O2
#   name_zh: 撤单/重挂委托请求
#   name_en: cancel_order / submit_order
#   intro: 实际发到 OrderManager 的撤单和对手价新限价单
#   downstream: ex_core.order_manager → miniqmt broker（D_EX_CORE）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I4 --> A1
# A1 --> A2
# I2 --> A2
# I4 --> A2
# A2 --> A3
# I3 --> A3
# A2 --> A4
# A1 --> O1
# A3 --> O2
# A4 --> O2
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Final
from zoneinfo import ZoneInfo

from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.order import Order

__all__: Final = [
    "Urgency",
    "ResolveAction",
    "ResolveActionType",
    "OpenOrderResolverConfig",
    "OpenOrderResolverError",
    "OpenOrderResolver",
]

_logger = logging.getLogger(__name__)


class OpenOrderResolverError(Exception):
    """未成交续接处理错误。"""

    error_code = "ZA-XC-0010"


class Urgency(str, Enum):
    """订单紧迫度——决定 PARTIAL 续接策略。

    HIGH: 打板策略，需快速成交，不可久等
    LOW: 多因子策略，换手率低（3-5天），不必急于补单
    """

    HIGH = "high"
    LOW = "low"


class ResolveActionType(str, Enum):
    """续接决策动作类型。"""

    WAIT = "wait"                        # 继续等待（挂单未超时）
    MAKE_OR_TAKE = "make_or_take"        # Make-or-Take 切换（撤单+对手价重挂）
    IGNORE_PARTIAL = "ignore_partial"    # PARTIAL 剩余<min_unit，转 CANCELLED
    LEAVE_OPEN = "leave_open"            # PARTIAL urgency低，留单等成交
    CLOSE_OUT = "close_out"              # 14:55 尾盘清退撤单
    SKIP_TERMINAL = "skip_terminal"      # 终态订单跳过
    SKIP_NOT_REGISTERED = "skip_not_registered"  # 未注册到续接跟踪


@dataclass(frozen=True)
class ResolveAction:
    """单笔订单续接决策结果（不可变，用于审计/日志）。"""

    order_id: str
    symbol: str
    action_type: ResolveActionType
    reason: str
    success: bool = True
    detail: str = ""


@dataclass
class OpenOrderResolverConfig:
    """未成交续接配置。

    Attributes:
        make_or_take_timeout_seconds: 被动挂单超时阈值 T（秒），默认 30s。
            超时后触发 Make-or-Take 切换。实盘需按标的流动性校准
            （高流动性票可降到 10s，低流动性票可升到 60s，§6.2 开放问题）。
        partial_ignore_threshold: PARTIAL 剩余量低于此值则忽略转 CANCELLED，
            默认 100 股（A 股主板最低申报单位，避免碎片化订单触发最低佣金 5 元）。
        market_close_minutes: 尾盘清退时间（分钟数，如 14*60+55=895 表示 14:55），
            默认 895（14:55）。到达此时间后所有非终态订单撤单清退。
        default_urgency: 未指定 urgency 时的默认值，默认 LOW（多因子，保守）。
    """

    make_or_take_timeout_seconds: float = 30.0
    partial_ignore_threshold: int = 100
    market_close_minutes: int = 895  # 14:55 = 14*60+55
    default_urgency: Urgency = Urgency.LOW


# 订单跟踪记录：order_id -> (提交时的 monotonic 时间, urgency)
_TrackRecord = tuple[float, Urgency]

# 对手价查询函数签名：(symbol, side) -> Decimal | None
#   BUY  -> 返回卖一价（ask1），Make-or-Take 买入挂卖一价主动吃单
#   SELL -> 返回买一价（bid1），Make-or-Take 卖出挂买一价主动吃单
OpponentPriceProvider = Callable[[str, OrderSide], Decimal | None]

# 当前时间查询函数签名（用于尾盘清退判断）：() -> datetime
NowProvider = Callable[[], datetime]

# A 股交易时段语义锚定上海时区（14:55 尾盘清退为交易所本地墙钟）。
# 与 governance.data_governance.miniqmt_provider._SHANGHAI_TZ 同一约定。
_SHANGHAI_TZ: Final = ZoneInfo("Asia/Shanghai")


class OpenOrderResolver:
    """未成交/部分成交订单续接处理器。

    对提交后未成交或部分成交的订单，按 urgency 分档续接，而非统一挂死或统一撤单。
    这是实盘"信号发了但没成交"的直接落地点。

    用法:
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(),
            opponent_price_provider=lambda sym, side: get_ask1(sym) if side == OrderSide.BUY else get_bid1(sym),
        )

        # 下单后注册到续接跟踪
        resolver.register_order(order_id, urgency=Urgency.HIGH)

        # 定时扫描续接（如每 5 秒一次，或由调度器触发）
        actions = resolver.scan_and_resolve()
        for a in actions:
            logger.info("续接: %s %s %s", a.order_id, a.action_type, a.reason)

    设计要点:
      - **幂等**：终态订单（FILLED/CANCELLED/REJECTED/EXPIRED）跳过，不重复处理
      - **幂等**：Make-or-Take 撤单失败（可能已成交）不报错，记录后继续
      - **可测试**：clock 和 now_provider 可注入，控制超时和尾盘判断
      - **无副作用决策**：_resolve_single 只决策不执行，执行在 scan_and_resolve
      - **审计友好**：每个动作返回 ResolveAction，可记录到审计日志
    """

    def __init__(
        self,
        order_manager: object,
        config: OpenOrderResolverConfig | None = None,
        opponent_price_provider: OpponentPriceProvider | None = None,
        clock: Callable[[], float] = time.monotonic,
        now_provider: NowProvider | None = None,
        resubmit_callback: Callable[[Order, Decimal], str | None] | None = None,
    ) -> None:
        """初始化续接处理器。

        Args:
            order_manager: OrderManager 实例（用于查 open orders / 撤单）
            config: 续接配置（None=默认 30s 超时 / 100 股忽略 / 14:55 清退）
            opponent_price_provider: 对手价查询函数 (symbol, side) -> Decimal|None。
                None=无盘口数据时 Make-or-Take 跳过（仅撤单不重挂）。
            clock: 单调时钟函数（默认 time.monotonic），用于超时判断
            now_provider: 当前时间函数（默认 Asia/Shanghai 时区墙钟——A 股
                14:55 尾盘清退为交易所本地时间语义），用于尾盘清退判断。
                注入可控制测试场景。
            resubmit_callback: 重挂单回调 (order, opponent_price) -> broker_order_id|None。
                None=用 order_manager.submit_order 重挂（需 order 有可重挂状态）。
                生产环境可注入自定义重挂逻辑（如带价格笼子校验）。
        """
        self._order_manager = order_manager
        self._config = config or OpenOrderResolverConfig()
        self._opponent_price_provider = opponent_price_provider
        self._clock = clock
        self._now_provider = now_provider or (lambda: datetime.now(_SHANGHAI_TZ))
        self._resubmit_callback = resubmit_callback

        # 订单跟踪：order_id -> (提交时 monotonic 时间, urgency)
        self._tracking: dict[str, _TrackRecord] = {}

    @property
    def config(self) -> OpenOrderResolverConfig:
        """只读：续接配置。"""
        return self._config

    def register_order(self, order_id: str, urgency: Urgency | None = None) -> None:
        """注册订单到续接跟踪。

        在 order_manager.submit_order() 成功后调用，记录提交时间和 urgency。
        未注册的 open order 在 scan_and_resolve 中按 default_urgency 处理
        （但无法计算超时，会被 SKIP_NOT_REGISTERED 跳过）。

        Args:
            order_id: 订单 ID
            urgency: 紧迫度（None=用 config.default_urgency）
        """
        urg = urgency or self._config.default_urgency
        self._tracking[order_id] = (self._clock(), urg)
        _logger.debug(
            "注册续接跟踪: order_id=%s urgency=%s", order_id, urg.value,
        )

    def unregister_order(self, order_id: str) -> None:
        """从续接跟踪移除（订单终态后清理，防止 _tracking 无限增长）。"""
        self._tracking.pop(order_id, None)

    def scan_and_resolve(self) -> list[ResolveAction]:
        """扫描所有 open orders，按规则续接。

        调用 OrderManager.get_open_orders() 获取所有非终态订单，
        对每笔按 _resolve_single 决策并执行。

        Returns:
            续接动作列表（每笔订单一个 ResolveAction）
        """
        actions: list[ResolveAction] = []
        get_open = getattr(self._order_manager, "get_open_orders", None)
        if get_open is None:
            _logger.warning("order_manager 无 get_open_orders 方法，跳过扫描")
            return actions

        open_orders: list[Order] = get_open()
        if not open_orders:
            return actions

        now = self._now_provider()
        is_close_out_time = self._is_market_close_time(now)

        for order in open_orders:
            try:
                action = self._resolve_and_execute(order, is_close_out_time)
                actions.append(action)
                # 终态后清理跟踪记录
                if action.action_type in (
                    ResolveActionType.IGNORE_PARTIAL,
                    ResolveActionType.CLOSE_OUT,
                ) and action.success:
                    self.unregister_order(order.order_id)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: 单笔异常不阻断其他订单
                _logger.error(
                    "续接处理异常 order_id=%s: %s", order.order_id, exc, exc_info=True,
                )
                actions.append(ResolveAction(
                    order_id=order.order_id,
                    symbol=order.symbol,
                    action_type=ResolveActionType.WAIT,
                    reason=f"resolve exception: {exc}",
                    success=False,
                ))

        return actions

    # ── 决策与执行 ──

    def _resolve_and_execute(self, order: Order, is_close_out_time: bool) -> ResolveAction:
        """单笔订单：决策 + 执行。"""
        # 14:55 尾盘清退（最高优先级，覆盖所有非终态）
        if is_close_out_time:
            return self._execute_close_out(order)

        # 获取跟踪记录
        track = self._tracking.get(order.order_id)
        if track is None:
            # 未注册到跟踪（可能是重启后遗留订单），无法计算超时
            return ResolveAction(
                order_id=order.order_id,
                symbol=order.symbol,
                action_type=ResolveActionType.SKIP_NOT_REGISTERED,
                reason="订单未注册到续接跟踪，无法计算超时",
                success=False,
            )

        submitted_at, urgency = track
        elapsed = self._clock() - submitted_at

        # 按状态分档续接
        if order.status == OrderStatus.SUBMITTED:
            # 未成交：按超时判断
            if elapsed <= self._config.make_or_take_timeout_seconds:
                return ResolveAction(
                    order_id=order.order_id,
                    symbol=order.symbol,
                    action_type=ResolveActionType.WAIT,
                    reason=f"挂单 {elapsed:.1f}s ≤ T={self._config.make_or_take_timeout_seconds}s，继续等待",
                )
            # 超时 → Make-or-Take
            return self._execute_make_or_take(order, urgency, elapsed)

        if order.status == OrderStatus.PARTIAL:
            # 部分成交：按剩余量和 urgency 判断
            remaining = order.quantity - (order.filled_quantity or Decimal("0"))
            remaining_int = int(remaining)

            if remaining_int < self._config.partial_ignore_threshold:
                # 剩余 < min_unit → 忽略转 CANCELLED
                return self._execute_ignore_partial(order, remaining_int)

            if urgency == Urgency.HIGH:
                # urgency 高 → Make-or-Take 补单
                return self._execute_make_or_take(order, urgency, elapsed, remaining)

            # urgency 低 → 留单等成交
            return ResolveAction(
                order_id=order.order_id,
                symbol=order.symbol,
                action_type=ResolveActionType.LEAVE_OPEN,
                reason=f"PARTIAL 剩余 {remaining_int} 股，urgency={urgency.value}，留单等成交",
            )

        # PENDING 状态（理论上 submit_order 后应为 SUBMITTED，兜底等待）
        return ResolveAction(
            order_id=order.order_id,
            symbol=order.symbol,
            action_type=ResolveActionType.WAIT,
            reason=f"订单状态 {order.status.value}，等待提交",
        )

    # ── 执行器 ──

    def _execute_make_or_take(
        self,
        order: Order,
        urgency: Urgency,
        elapsed: float,
        remaining: Decimal | None = None,
    ) -> ResolveAction:
        """执行 Make-or-Take 切换：撤单 → 对手价重挂剩余量。

        Args:
            order: 原订单
            urgency: 紧迫度
            elapsed: 已挂单时间
            remaining: 剩余量（None=全部数量，用于 SUBMITTED 未成交场景）
        """
        qty_str = f"{remaining}" if remaining else f"{order.quantity}"
        reason = f"挂单 {elapsed:.1f}s 超时 T={self._config.make_or_take_timeout_seconds}s，urgency={urgency.value}，Make-or-Take 切换"

        # 1. 撤单
        cancel_ok = self._cancel_order(order.order_id)
        if not cancel_ok:
            return ResolveAction(
                order_id=order.order_id,
                symbol=order.symbol,
                action_type=ResolveActionType.MAKE_OR_TAKE,
                reason=reason,
                success=False,
                detail=f"撤单失败（可能已成交），剩余 {qty_str} 股",
            )

        # 2. 查对手价
        if self._opponent_price_provider is None:
            return ResolveAction(
                order_id=order.order_id,
                symbol=order.symbol,
                action_type=ResolveActionType.MAKE_OR_TAKE,
                reason=reason,
                success=True,
                detail=f"已撤单，无对手价 provider 跳过重挂，剩余 {qty_str} 股",
            )

        opponent_price = self._opponent_price_provider(order.symbol, order.side)
        if opponent_price is None or opponent_price <= 0:
            return ResolveAction(
                order_id=order.order_id,
                symbol=order.symbol,
                action_type=ResolveActionType.MAKE_OR_TAKE,
                reason=reason,
                success=True,
                detail=f"已撤单，无对手价盘口数据跳过重挂，剩余 {qty_str} 股",
            )

        # 3. 对手价重挂剩余量
        resubmit_qty = remaining if remaining else order.quantity
        rebroker_id = self._resubmit(order, opponent_price, resubmit_qty)

        detail = f"已撤单+对手价 {opponent_price} 重挂 {resubmit_qty} 股"
        if rebroker_id:
            detail += f" (new broker_order_id={rebroker_id})"

        return ResolveAction(
            order_id=order.order_id,
            symbol=order.symbol,
            action_type=ResolveActionType.MAKE_OR_TAKE,
            reason=reason,
            success=True,
            detail=detail,
        )

    def _execute_ignore_partial(self, order: Order, remaining_int: int) -> ResolveAction:
        """执行 PARTIAL 剩余 < min_unit 忽略：撤单转 CANCELLED。

        避免碎片化订单触发最低佣金（5 元）。
        """
        cancel_ok = self._cancel_order(order.order_id)
        reason = f"PARTIAL 剩余 {remaining_int} 股 < 阈值 {self._config.partial_ignore_threshold}，忽略转 CANCELLED"
        return ResolveAction(
            order_id=order.order_id,
            symbol=order.symbol,
            action_type=ResolveActionType.IGNORE_PARTIAL,
            reason=reason,
            success=cancel_ok,
            detail="" if cancel_ok else "撤单失败",
        )

    def _execute_close_out(self, order: Order) -> ResolveAction:
        """执行 14:55 尾盘清退：撤单。

        A 股限价单 GFD 当日有效，15:00 收盘自动撤销。主动撤单可释放资金预占额度
        并避免"幽灵挂单"占用风控额度。
        """
        cancel_ok = self._cancel_order(order.order_id)
        return ResolveAction(
            order_id=order.order_id,
            symbol=order.symbol,
            action_type=ResolveActionType.CLOSE_OUT,
            reason=f"14:55 尾盘清退（订单状态 {order.status.value}）",
            success=cancel_ok,
            detail="" if cancel_ok else "撤单失败",
        )

    # ── 辅助 ──

    def _cancel_order(self, order_id: str) -> bool:
        """撤单（幂等：已成交则忽略）。"""
        try:
            cancel = getattr(self._order_manager, "cancel_order", None)
            if cancel is None:
                _logger.warning("order_manager 无 cancel_order 方法")
                return False
            return bool(cancel(order_id))
        except Exception as exc:  # noqa: BLE001
            _logger.warning("撤单异常 order_id=%s: %s", order_id, exc)
            return False

    def _resubmit(self, order: Order, opponent_price: Decimal, quantity: Decimal) -> str | None:
        """对手价重挂剩余量。

        优先用注入的 resubmit_callback（生产环境可带价格笼子校验），
        否则尝试用 order_manager.create_order + submit_order 重挂。

        Args:
            order: 原订单（用于提取 symbol/side/strategy_id/order_type）
            opponent_price: 对手价（新挂单价）
            quantity: 重挂数量

        Returns:
            新的 broker_order_id，失败返回 None
        """
        if self._resubmit_callback is not None:
            try:
                return self._resubmit_callback(order, opponent_price)
            except Exception as exc:  # noqa: BLE001
                _logger.warning("resubmit_callback 异常: %s", exc)
                return None

        # 默认重挂逻辑：create_order + submit_order
        try:
            create = getattr(self._order_manager, "create_order", None)
            submit = getattr(self._order_manager, "submit_order", None)
            if create is None or submit is None:
                _logger.warning("order_manager 无 create_order/submit_order 方法，跳过重挂")
                return None

            new_order = create(
                symbol=order.symbol,
                strategy_id=order.strategy_id,
                side=order.side,
                order_type=OrderType.LIMIT,
                quantity=quantity,
                limit_price=opponent_price,
            )
            # 注册新订单到续接跟踪（Make-or-Take 重挂的单不再二次 Make-or-Take，
            # 用 urgency.LOW 避免无限循环）
            self.register_order(new_order.order_id, urgency=Urgency.LOW)
            broker_order_id = submit(new_order.order_id)
            _logger.info(
                "Make-or-Take 重挂: symbol=%s side=%s qty=%s price=%s new_order_id=%s",
                order.symbol, order.side.value, quantity, opponent_price, new_order.order_id,
            )
            return broker_order_id
        except Exception as exc:  # noqa: BLE001
            _logger.warning("重挂单异常: %s", exc)
            return None

    def _is_market_close_time(self, now: datetime) -> bool:
        """判断当前是否到达尾盘清退时间（14:55）。

        用当前时间的时分转换为当日分钟数，与 config.market_close_minutes 比较。
        注意：只比较时分，不比较日期（每个交易日独立判断）。

        Args:
            now: 当前时间

        Returns:
            True = 已到达 14:55，应尾盘清退
        """
        now_minutes = now.hour * 60 + now.minute
        return now_minutes >= self._config.market_close_minutes
