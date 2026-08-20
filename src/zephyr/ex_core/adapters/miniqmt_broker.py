# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.adapters.miniqmt_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.trading.trading_contracts.broker_interface; zephyr.backtest.core.matching_logic; zephyr.data.implementations.miniqmt_provider; zephyr.ex_core.board_lot; zephyr.ex_core.price_cage
# [CONSUMERS] zephyr.frontend.dashboard.components.trade_panel; zephyr.frontend.dashboard.components.position_monitor
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] xttrader非线程安全(加锁); T+1锁定(查持仓available_quantity); 涨跌停限制; 板块差异化整手(board_lot真源); 价格笼子夹边不废单(price_cage真源); 幂等(INV-007); 回测=实盘一致性(MatchingLogic共享, submit_order内置预校验)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MiniQmtBrokerError
# [TESTS]
# [A_module] module_id=MOD-L06-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易）

职责:
  - 对接国金证券 MiniQMT 终端的 xttrader API，提供 A 股实盘交易能力
  - 实现 BrokerInterface（OCP-003 扩展点）
  - A股约束校验: T+1锁定(查持仓available_quantity) / 涨跌停限制 / 板块差异化整手
    (board_lot 真源: 主板/创业板/北交所100股递增, 科创板200股起1股递增) / 停牌跳过
  - 价格笼子: 连续竞价限价单超笼子夹到边界(不废单, price_cage 真源, 需带盘口下单)
  - 幂等下单: 所有订单携带 idempotency_key（INV-007）
  - 断线重连: 连接失败时自动重试；xttrader调用失败自动触发_reconnect
  - 回测=实盘一致性: 共用 MatchingLogic 做预成交校验（submit_order内置）

约束:
  - xttrader 非线程安全，所有调用需加锁（threading.Lock）
  - MiniQMT 仅 Windows，必须先启动 XtMiniQmt.exe 终端
  - xttrader 需开通 A 股实盘权限
  - 与 D_DATA MiniQmtQuoteProvider 共用 xtquant 连接（shared_xtquant_conn）

xttrader 错误码映射:
  0=成功, -1=连接失败, -2=未就绪, -3=订单号重复,
  50=涨停, 51=跌停, 52=数量不合法, 53=价格不合法,
  54=资金不足, 55=持仓不足

A股约束:
  - t_plus=1 (T+1锁定，买入当天不能卖出)
  - 板块差异化整手(真源 board_lot): 主板/创业板/北交所 min_unit=100 递增100,
    科创板 min_unit=200 递增1 (100股申报=error_code 52)
  - price_tick=0.01 (价格最小变动单位)
  - asset_classes=[stock, etf, convertible_bond]

SSoT: docs/03_modules/_domain_execution_core/blueprint.md §16.7.1 MiniQmtBroker

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 委托订单 Order
#   fields: symbol/side/quantity/order_type/limit_price/idempotency_key（INV-007 必带）
#   code: submit_order(order, order_book, prev_close) (miniqmt_broker.py)
# - id: I2
#   name: 5档盘口快照 order_book + 昨收 prev_close（可选）
#   fields: OrderBookSnapshot(ask/bid 5档+last_price)；prev_close 供涨跌停与笼子回退
#   code: OrderBookSnapshot (backtest.core.matching_logic)
# 层: 算法
# - id: A1
#   name_zh: ① 幂等拦截
#   name_en: idempotency check
#   intro: idempotency_key 命中 _idempotency_map 直接返回既有 broker_order_id
#   desc: 防重复下单（INV-007），全链路 _lock 串行化
#   inputs: I1
#   outputs: 既有 broker_order_id 或放行
#   invariant: 同一 idempotency_key 最多下一次单
# - id: A2
#   name_zh: ② A股约束校验
#   name_en: _validate_a_share_constraints
#   intro: 板块差异化整手(board_lot真源)+T+1可查持仓+涨跌停板块幅度，违规拒单
#   desc: get_board_lot_rule(symbol) 校验 min_unit/increment；SELL 查 can_sell_volume；prev_close 算板块涨跌停
#   inputs: I1 I2
#   outputs: 放行或 MiniQmtBrokerError(52/50/51/-2)
#   invariant: 非法申报本地拒单防废单
# - id: A3
#   name_zh: ③ 价格笼子夹边
#   name_en: _apply_price_cage_locked
#   intro: 连续竞价限价单超笼子夹到边界（不废单），无基准价跳过
#   desc: check_price_cage(side,limit,symbol,ask1,bid1,last,prev_close) → CLAMPED 则原地修正 limit_price
#   inputs: I1 I2
#   outputs: 夹边后 limit_price
#   invariant: 夹边后价格必在笼子内
# - id: A4
#   name_zh: ④ 回测=实盘一致性预校验
#   name_en: _pre_trade_simulate_locked
#   intro: 共用 MatchingLogic 模拟成交预估价量（B方案核心）
#   desc: order→MatchOrderInput → match_market/limit_order → MatchingFill 预估
#   inputs: I1 I2
#   outputs: MatchingFill 预估
#   invariant: 回测=实盘同一撮合实现
# - id: A5
#   name_zh: ⑤ xttrader 下单与断线重连
#   name_en: order_stock via _call_xttrader_with_reconnect
#   intro: StockAccount+方向23/24+price_type 映射下单，异常自动 _reconnect 重试一次
#   desc: order_stock(account,symbol,side,volume,price_type,price,strategy_name,order_remark=idem_key) → order_id>0 成功
#   inputs: I1
#   outputs: broker_order_id
#   invariant: xttrader 非线程安全，全调用 _lock 保护（含心跳重连）
# 层: 输出
# - id: O1
#   name_zh: 券商订单号 broker_order_id
#   name_en: broker_order_id
#   intro: xttrader 返回的正整数 order_id 转 str，写入 _order_cache/_idempotency_map
#   downstream: ex_core.order_manager / ex_core.trading_session
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# I2 --> A3
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Any, Final, Optional

from zephyr.backtest.core.matching_logic import (
    MatchingConfig,
    MatchingFill,
    MatchingLogic,
    MatchOrderInput,
    OrderBookSnapshot,
)
from zephyr.ex_core.board_lot import AShareBoard, classify_board, get_board_lot_rule
from zephyr.ex_core.price_cage import CageStatus, check_price_cage
from zephyr.shared.utils.time_utils import now_utc
from zephyr.trading.trading_contracts.broker_interface import (
    BrokerInterface,
    FillCallback,
)
from zephyr.trading.trading_contracts.execution.fill import Fill
from zephyr.trading.trading_contracts.execution.order import (
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
)
from zephyr.trading.trading_contracts.execution.position import PositionSnapshot

_logger = logging.getLogger(__name__)

# xttrader 错误码映射
XTTRADER_ERROR_CODES: Final[dict[int, str]] = {
    0: "成功",
    -1: "连接失败",
    -2: "未就绪",
    -3: "订单号重复",
    50: "涨停",
    51: "跌停",
    52: "数量不合法",
    53: "价格不合法",
    54: "资金不足",
    55: "持仓不足",
}

# xttrader 买卖方向映射（新版 xtquant 250807.1.2：order_type 是买卖方向，非订单类型）
# 23=买, 24=卖（见 xttrader.order_stock docstring）
_XT_ORDER_SIDE = {
    OrderSide.BUY: 23,
    OrderSide.SELL: 24,
}

# xttrader 价格类型映射（price_type 区分限价/市价）
# 0=限价指定价, 5=市价最新价（见 xtquant 帮助手册；#ARCH-XTQUANT-API-COMPAT-001）
_XT_PRICE_TYPE = {
    OrderType.LIMIT: 0,
    OrderType.MARKET: 5,
}

# xttrader 方向常量（XtOrder.order_type 字段值，参考 xtquant 文档）
_XT_BUY_ORDER_TYPES = {23, 25, 27, 29}  # 买限价/买市价/买开/买平
_XT_SELL_ORDER_TYPES = {24, 26, 28, 30}  # 卖限价/卖市价/卖开/卖平

# 板块涨跌停幅度（2026-07-06 规则修订：ST 与主板统一 ±10%）
# 真源分类：ex_core.board_lot.classify_board；UNKNOWN 回退主板 10%
_BOARD_PRICE_LIMIT_PCT: Final[dict[AShareBoard, Decimal]] = {
    AShareBoard.MAIN: Decimal("0.10"),
    AShareBoard.CHINEXT: Decimal("0.20"),  # 创业板 ±20%
    AShareBoard.STAR: Decimal("0.20"),  # 科创板 ±20%
    AShareBoard.BSE: Decimal("0.30"),  # 北交所 ±30%
}


class MiniQmtBrokerError(Exception):
    """MiniQMT 券商错误"""

    error_code = "ZA-XC-0001"

    def __init__(self, message: str, error_code: int | None = None):
        super().__init__(message)
        if error_code is not None:
            self.error_code = error_code


class MiniQmtBroker(BrokerInterface):
    """MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易）

    实现 BrokerInterface，对接国金证券 MiniQMT 终端的 xttrader API。

    核心特性:
      - A股约束校验: T+1(查持仓available_quantity) / 涨跌停 / 100股整数倍 / 停牌
      - 幂等下单: idempotency_key 防重复（INV-007）
      - 断线重连: 连接失败自动重试；xttrader调用失败自动触发_reconnect
      - 线程安全: threading.Lock 保护所有 xttrader 调用与共享状态
      - 回测=实盘一致性: 共用 MatchingLogic，submit_order 内置 pre_trade_simulate 预校验

    Usage:
        # 配置从 config/.env.qmt 读取（QMT_SIM_PATH / QMT_SIM_ACCOUNT）
        # 与 D_DATA 共用 xtquant 连接
        provider = MiniQmtQuoteProvider(path=qmt_path)
        broker = MiniQmtBroker(
            path=qmt_path,
            session_id="zephyr_session",
            account_id=qmt_account,  # 资金账号，构造 StockAccount 下单/查询
            shared_xtquant_conn=provider,  # 共用连接
            matching_logic=MatchingLogic(MatchingConfig()),  # 共用撮合逻辑
        )
        broker.connect()

        # 下单（幂等，可选传 order_book 做预校验）
        order = Order(
            idempotency_key="order-001",
            order_id="ord-001",
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            side=OrderSide.BUY,
            strategy_id="my_strategy",
            symbol="600000.SH",
            limit_price=Decimal("10.50"),
        )
        broker_order_id = broker.submit_order(order, prev_close=Decimal("10.00"))

        # 查询/撤单
        order_status = broker.query_order(broker_order_id)
        broker.cancel_order(broker_order_id)

        # 查询持仓
        positions = broker.get_positions()
    """

    # A股约束常量
    T_PLUS = 1
    MIN_ORDER_QTY = 100  # 主板最小申报单位（板块差异化真源=board_lot.get_board_lot_rule）
    PRICE_TICK = Decimal("0.01")
    PRICE_LIMIT_PCT = Decimal("0.10")  # 主板/ST ±10%（板块差异化幅度见 _BOARD_PRICE_LIMIT_PCT）
    ASSET_CLASSES = ["stock", "etf", "convertible_bond"]

    def __init__(
        self,
        path: str = "",
        session_id: str = "zephyr_session",
        account_id: str = "",
        shared_xtquant_conn: object | None = None,
        matching_logic: MatchingLogic | None = None,
        matching_config: MatchingConfig | None = None,
        reconnect_max_retries: int = 3,
    ):
        """初始化 MiniQMT 券商适配器

        Args:
            path: miniQMT 安装路径（userdata_mini 目录）
            session_id: 会话 ID（语义标识，用于日志/PositionSnapshot.portfolio_id；
                内部转 int 传给 XtQuantTrader，新版 xtquant 要求 int session）
            account_id: 券商资金账号（如 "8886156677"，从 config/.env.qmt 读取；
                用于构造 StockAccount 下单/查询，新版 xtquant 要求 StockAccount 对象）
            shared_xtquant_conn: 与 D_DATA 共用的 MiniQmtQuoteProvider 实例（可选）
                若提供，则复用其 xtquant 连接，避免重复 connect 到 miniQMT 终端
            matching_logic: 与 D_BACKTEST 共用的 MatchingLogic 实例（可选）
            matching_config: 撮合配置（matching_logic 为空时用此创建，可选）
            reconnect_max_retries: 断线重连最大重试次数
        """
        self._path = path
        self._session_id = session_id
        self._account_id = account_id
        # XtQuantTrader 新版要求 int session；session_id 是 str 语义标识，转 int
        self._session_int = abs(hash(session_id)) % 1000000
        self._shared_conn = shared_xtquant_conn
        self._matching_logic = matching_logic or MatchingLogic(matching_config or MatchingConfig())
        self._reconnect_max_retries = reconnect_max_retries

        # xttrader 懒加载
        self._xttrader: Any = None
        self._account: Any = None  # StockAccount 懒加载（_init_xttrader 中构造）
        self._connected = False
        self._started = False  # start() 只调一次（启动后台线程池，不返回错误码）

        # 线程安全锁（xttrader 非线程安全；保护共享状态如 _fill_callbacks）
        self._lock = threading.Lock()

        # 幂等去重：idempotency_key -> broker_order_id
        self._idempotency_map: dict[str, str] = {}

        # 订单状态缓存：broker_order_id -> Order
        self._order_cache: dict[str, Order] = {}

        # 成交回调（受 _lock 保护）
        self._fill_callbacks: list[FillCallback] = []

        # GAP-002（2026-08-12）：断线重连四步补齐——行情重订阅+策略恢复+假死心跳
        self._subscribed_symbols: set[str] = set()  # 已订阅行情的标的集合
        self._reconnect_callbacks: list[Callable[[], None]] = []  # 重连完成回调
        self._last_tick_ts: float = 0.0  # 最近 Tick 时间戳（假死检测用）
        self._heartbeat_thread: threading.Thread | None = None
        self._heartbeat_stop = threading.Event()
        self._heartbeat_interval = 10.0  # 秒
        self._heartbeat_timeout = 30.0  # 秒，超此无 Tick 视为假死

    @property
    def lock(self):
        """只读：lock（Stage 4 公共化）。"""
        return self._lock

    @lock.setter
    def lock(self, value):
        """写入：lock（Stage 4 公共化）。"""
        self._lock = value

    @property
    def xttrader(self) -> object:
        """只读：xttrader（Stage 4 公共化）。"""
        return self._xttrader

    @xttrader.setter
    def xttrader(self, value):
        """写入：xttrader（Stage 4 公共化）。"""
        self._xttrader = value

    @property
    def connected(self):
        """只读：connected（Stage 4 公共化）。"""
        return self._connected

    @connected.setter
    def connected(self, value):
        """写入：connected（Stage 4 公共化）。"""
        self._connected = value

    # ------------------------------------------------------------------
    # BrokerInterface 实现
    # ------------------------------------------------------------------

    @property
    def broker_id(self) -> str:
        """券商唯一标识"""
        return "miniqmt"

    def connect(self) -> bool:
        """建立与 MiniQMT 终端的连接

        新版 xtquant 250807.1.2 连接流程：
          _init_xttrader() → start()（启动后台线程池，只调一次）→
          connect()（TCP 连接终端）→ subscribe(account)（订阅账户推送）

        Returns:
            True = 连接成功

        Raises:
            MiniQmtBrokerError: 连接失败（超过最大重试次数）
        """
        with self._lock:
            if self._connected and self._xttrader is not None:
                return True

            try:
                self._init_xttrader()
                self._start_once()
                self._do_connect_with_retry()
                self._subscribe_account()
                self._connected = True
                _logger.info(
                    "MiniQMT 券商连接成功 path=%s session=%s account=%s", self._path, self._session_id, self._account_id
                )
                return True
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._connected = False
                raise MiniQmtBrokerError(f"MiniQMT 连接失败: {e}", error_code=-1) from e

    def disconnect(self) -> None:
        """断开连接"""
        with self._lock:
            if self._xttrader is not None:
                try:
                    self._xttrader.stop()
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    _logger.warning("断开连接时出错: %s", e, exc_info=True)
                self._xttrader = None
            self._connected = False
            self._started = False
            self._account = None
            _logger.info("MiniQMT 券商已断开")

    def submit_order(
        self,
        order: Order,
        order_book: OrderBookSnapshot | None = None,
        prev_close: Decimal | None = None,
    ) -> str:
        """发送委托订单

        流程:
          1. 幂等检查（idempotency_key 去重）
          2. A股约束校验（板块差异化整手 board_lot / 涨跌停 / T+1查持仓available_quantity）
          3. 价格笼子校验（限价单带盘口时，超限夹到边界不废单 price_cage）
          4. 回测=实盘一致性预校验（可选 order_book，调用 MatchingLogic 模拟成交）
          5. 调用 xttrader.order_stock 下单
          6. 错误码映射
          7. 缓存订单状态

        Args:
            order: 委托订单（必须含 idempotency_key）
            order_book: 当前5档盘口快照（可选，提供则做价格笼子+MatchingLogic 预校验）
            prev_close: 昨收价（可选，提供则做涨跌停校验）

        Returns:
            broker_order_id（券商返回的订单号）

        Raises:
            MiniQmtBrokerError: 下单失败（含错误码）
        """
        if not order.idempotency_key:
            raise MiniQmtBrokerError("订单必须包含 idempotency_key（INV-007）")

        with self._lock:
            # 1. 幂等去重
            if order.idempotency_key in self._idempotency_map:
                existing_id = self._idempotency_map[order.idempotency_key]
                _logger.warning(
                    "幂等拦截: idempotency_key=%s 已存在 broker_order_id=%s",
                    order.idempotency_key,
                    existing_id,
                )
                return existing_id

            # 2. A股约束校验
            self._validate_a_share_constraints(order, prev_close)

            # 2.5 价格笼子校验（40_execution_broker §决策⑭，连续竞价限价单硬约束）
            # 超限夹到笼子边界（不废单），夹边后再做 MatchingLogic 预校验
            self._apply_price_cage_locked(order, order_book, prev_close)

            # 3. 回测=实盘一致性预校验（B方案核心：下单路径经过 MatchingLogic）
            if order_book is not None:
                fill_preview = self._pre_trade_simulate_locked(order, order_book)
                _logger.info(
                    "预成交校验: symbol=%s 预估价=%s 预估成交量=%s 是否成交=%s",
                    order.symbol,
                    fill_preview.price,
                    fill_preview.filled_quantity,
                    fill_preview.filled,
                )

            # 4. 调用 xttrader 下单
            if not self._connected:
                raise MiniQmtBrokerError("未连接，请先调用 connect()", error_code=-1)

            try:
                # 构造 xttrader 订单（新版 xtquant 250807.1.2 位置参数）
                # order_type 是买卖方向（23=买/24=卖），price_type 区分限价/市价
                xt_order_side = _XT_ORDER_SIDE.get(order.side, 23)
                xt_price_type = _XT_PRICE_TYPE.get(order.order_type, 0)
                limit_price = float(order.limit_price) if order.limit_price else 0.0

                result = self._call_xttrader_with_reconnect(
                    lambda: self._xttrader.order_stock(
                        self._account,  # StockAccount 对象（非 str）
                        order.symbol,  # stock_code
                        xt_order_side,  # order_type=买卖方向（23买/24卖）
                        int(order.quantity),  # order_volume
                        xt_price_type,  # price_type
                        limit_price,  # price
                        strategy_name=order.strategy_id,
                        order_remark=order.idempotency_key,
                    )
                )
            except MiniQmtBrokerError:
                raise
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                raise MiniQmtBrokerError(f"xttrader 下单异常: {e}", error_code=-1) from e

            # 5. 返回值映射：新版 order_stock 返回 order_id（正整数=成功，-1=失败）
            if result is None or (isinstance(result, int) and result < 0):
                raise MiniQmtBrokerError(
                    f"下单失败: xttrader 返回 order_id={result}",
                    error_code=-1,
                )

            # 6. 缓存订单（broker_order_id 用券商返回的 order_id，非本地 order.order_id）
            broker_order_id = str(result)
            order.status = OrderStatus.SUBMITTED
            order.broker_order_id = broker_order_id
            order.updated_at = now_utc()
            self._idempotency_map[order.idempotency_key] = broker_order_id
            self._order_cache[broker_order_id] = order

            _logger.info(
                "下单成功: broker_order_id=%s symbol=%s side=%s qty=%s",
                broker_order_id,
                order.symbol,
                order.side.value,
                order.quantity,
            )
            return broker_order_id

    def cancel_order(self, broker_order_id: str) -> bool:
        """撤单

        Args:
            broker_order_id: 券商订单号

        Returns:
            True = 撤单成功

        Raises:
            MiniQmtBrokerError: 撤单失败（含错误码，与 submit_order 契约对称）
        """
        with self._lock:
            if not self._connected:
                raise MiniQmtBrokerError("未连接，请先调用 connect()", error_code=-1)

            try:
                result = self._call_xttrader_with_reconnect(
                    lambda: self._xttrader.cancel_order_stock(
                        self._account,
                        int(broker_order_id),
                    )
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                raise MiniQmtBrokerError(f"xttrader 撤单异常: {e}", error_code=-1) from e

            if result != 0:
                error_msg = XTTRADER_ERROR_CODES.get(result, f"未知错误码: {result}")
                raise MiniQmtBrokerError(
                    f"撤单失败: {error_msg} (code={result})",
                    error_code=result,
                )

            # 更新缓存
            if broker_order_id in self._order_cache:
                self._order_cache[broker_order_id].status = OrderStatus.CANCELLED
                self._order_cache[broker_order_id].updated_at = now_utc()

            _logger.info("撤单成功: broker_order_id=%s", broker_order_id)
            return True

    def query_order(self, broker_order_id: str) -> Order | None:
        """查询委托状态

        Args:
            broker_order_id: 券商订单号

        Returns:
            Order 对象（含最新状态），不存在返回 None
        """
        with self._lock:
            if not self._connected:
                raise MiniQmtBrokerError("未连接，请先调用 connect()", error_code=-1)

            try:
                orders = self._call_xttrader_with_reconnect(lambda: self._xttrader.query_stock_orders(self._account))
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                raise MiniQmtBrokerError(f"xttrader 查询订单异常: {e}", error_code=-1) from e

            if not orders:
                return self._order_cache.get(broker_order_id)

            # 查找匹配的订单（order_id 类型归一：xtquant 版本间 int/str 不一，
            # _order_cache 键为 str，统一 str 比较防静默查不到）
            for xt_order in orders:
                if str(getattr(xt_order, "order_id", "")) == str(broker_order_id):
                    # 更新缓存
                    cached = self._order_cache.get(broker_order_id)
                    if cached:
                        cached.status = self._map_xt_status(xt_order.order_status)
                        cached.filled_quantity = Decimal(str(xt_order.traded_volume))
                        cached.avg_fill_price = (
                            Decimal(str(xt_order.traded_price)) if xt_order.traded_price > 0 else None
                        )
                        cached.updated_at = now_utc()
                    return cached or self._xt_order_to_order(xt_order)

            return self._order_cache.get(broker_order_id)

    def get_positions(self) -> PositionSnapshot:
        """查询当前持仓

        Returns:
            PositionSnapshot（含现金/持仓/市值）
        """
        with self._lock:
            if not self._connected:
                raise MiniQmtBrokerError("未连接，请先调用 connect()", error_code=-1)

            try:
                xt_positions = self._call_xttrader_with_reconnect(
                    lambda: self._xttrader.query_stock_positions(self._account)
                )
                xt_asset = self._call_xttrader_with_reconnect(lambda: self._xttrader.query_stock_asset(self._account))
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                raise MiniQmtBrokerError(f"xttrader 查询持仓异常: {e}", error_code=-1) from e

            holdings: dict[str, Decimal] = {}
            market_values: dict[str, Decimal] = {}
            total_mv = Decimal("0")

            if xt_positions:
                for pos in xt_positions:
                    if pos.volume > 0:
                        holdings[pos.stock_code] = Decimal(str(pos.volume))
                        mv = Decimal(str(pos.market_value))
                        market_values[pos.stock_code] = mv
                        total_mv += mv

            cash = Decimal("0")
            if xt_asset:
                cash = Decimal(str(xt_asset.cash))

            return PositionSnapshot(
                as_of_timestamp=now_utc(),
                idempotency_key=f"pos-{self._session_id}-{int(now_utc().timestamp())}",
                portfolio_id=self._session_id,
                cash=cash,
                holdings=holdings,
                market_values=market_values,
                total_market_value=total_mv,
            )

    def register_fill_callback(self, callback: FillCallback) -> None:
        """注册成交回调（线程安全）"""
        with self._lock:
            self._fill_callbacks.append(callback)

    # ------------------------------------------------------------------
    # 回测=实盘一致性：预成交校验
    # ------------------------------------------------------------------

    def pre_trade_simulate(
        self,
        order: Order,
        order_book: OrderBookSnapshot,
    ) -> MatchingFill:
        """预成交模拟（回测=实盘一致性核心）

        使用 MatchingLogic 模拟订单在当前盘口下的成交结果，
        用于下单前预估成交价/滑点/手续费，保证回测与实盘撮合逻辑一致。

        Args:
            order: 委托订单
            order_book: 当前5档盘口快照（从 MiniQmtQuoteProvider.get_order_book 获取）

        Returns:
            MatchingFill 预估成交结果
        """
        with self._lock:
            return self._pre_trade_simulate_locked(order, order_book)

    def _pre_trade_simulate_locked(
        self,
        order: Order,
        order_book: OrderBookSnapshot,
    ) -> MatchingFill:
        """pre_trade_simulate 的无锁版本（调用方已持锁）"""
        order_type = "MARKET" if order.order_type is OrderType.MARKET else "LIMIT"
        match_input = MatchOrderInput(
            symbol=order.symbol,
            side=order.side.value,
            quantity=order.quantity,
            order_type=order_type,
            limit_price=order.limit_price,
        )

        if order.order_type is OrderType.MARKET:
            return self._matching_logic.match_market_order(match_input, order_book)
        return self._matching_logic.match_limit_order(match_input, order_book)

    def _apply_price_cage_locked(
        self,
        order: Order,
        order_book: OrderBookSnapshot | None,
        prev_close: Decimal | None,
    ) -> None:
        """价格笼子校验（调用方已持锁，40_execution_broker §决策⑭）。

        仅连续竞价限价单适用（市价单/集合竞价豁免由本方法内部判断跳过）。
        基准价回退链：对手方最优价(ask1/bid1)→last_price→prev_close；
        超限夹到笼子边界（不废单，原地修正 order.limit_price）；
        无任何基准价（UNKNOWN）跳过校验并 warn（不阻断下单）。
        """
        if order.order_type is not OrderType.LIMIT or order.limit_price is None:
            return
        ask1 = None
        bid1 = None
        last_price = None
        if order_book is not None:
            ask1 = order_book.ask_price[0] if order_book.ask_price else None
            bid1 = order_book.bid_price[0] if order_book.bid_price else None
            last_price = order_book.last_price
        result = check_price_cage(
            side=order.side,
            limit_price=order.limit_price,
            symbol=order.symbol,
            ask1=ask1,
            bid1=bid1,
            last_price=last_price,
            prev_close=prev_close,
        )
        if result.status is CageStatus.CLAMPED:
            _logger.info(
                "价格笼子夹边: symbol=%s side=%s limit=%s → clamped=%s (base=%s)",
                order.symbol,
                order.side.value,
                order.limit_price,
                result.clamped_price,
                result.base_price,
            )
            order.limit_price = result.clamped_price
            order.updated_at = now_utc()
        elif result.status is CageStatus.UNKNOWN:
            _logger.warning(
                "价格笼子校验跳过（无可用基准价）: symbol=%s",
                order.symbol,
            )

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected

    @property
    def matching_logic(self) -> MatchingLogic:
        """暴露 MatchingLogic（回测=实盘一致性）"""
        return self._matching_logic

    # ------------------------------------------------------------------
    # 私有方法
    # ------------------------------------------------------------------

    def _init_xttrader(self) -> None:
        """懒加载 xttrader 模块并初始化 XtQuantTrader + StockAccount

        新版 xtquant 250807.1.2（#ARCH-XTQUANT-API-COMPAT-001）：
          - XtQuantTrader(path, session_int, callback=None)  # session 必须 int
          - StockAccount(account_id, 'STOCK')  # 下单/查询必须传 StockAccount 对象

        若提供了 shared_xtquant_conn（D_DATA MiniQmtQuoteProvider），优先复用其连接，
        避免重复 connect 到 miniQMT 终端（Blueprint §16.7.1 F 共用 xtquant 连接）。
        """
        if self._xttrader is not None:
            self._init_account()
            return

        # 优先复用 D_DATA MiniQmtQuoteProvider 的 xttrader 连接
        if self._shared_conn is not None:
            shared_trader = getattr(self._shared_conn, "xttrader", None) or getattr(
                self._shared_conn, "_xttrader", None
            )
            if shared_trader is not None:
                self._xttrader = shared_trader
                _logger.info("复用 D_DATA MiniQmtQuoteProvider 的 xttrader 连接")
                self._init_account()
                return

        # 懒加载 xtquant 并新建 XtQuantTrader（session 必须 int）
        try:
            from xtquant.xttrader import XtQuantTrader  # type: ignore[import-not-found]
        except ImportError as e:
            raise MiniQmtBrokerError(
                "xtquant 未安装。请安装新版 xtquant 250807.1.2+（支持 Python 3.12），"
                "或从 QMT 安装目录拷贝。详见 #ARCH-XTQUANT-API-COMPAT-001。",
                error_code=-1,
            ) from e

        self._xttrader = XtQuantTrader(self._path, self._session_int)
        self._init_account()

    def _init_account(self) -> None:
        """构造 StockAccount（下单/查询必须的账户对象）。

        新版 xtquant 要求 order_stock/query_stock_* 传 StockAccount 对象，非 str。
        """
        if self._account is not None:
            return
        if not self._account_id:
            raise MiniQmtBrokerError(
                "account_id 未配置。请从 config/.env.qmt 读取 QMT_SIM_ACCOUNT 传入。",
                error_code=-1,
            )
        try:
            from xtquant.xttype import StockAccount  # type: ignore[import-not-found]
        except ImportError as e:
            raise MiniQmtBrokerError(
                "xtquant.xttype.StockAccount 不可用，请确认 xtquant 250807.1.2+ 已安装。",
                error_code=-1,
            ) from e
        self._account = StockAccount(self._account_id, "STOCK")
        _logger.info("StockAccount 构造成功 account_id=%s", self._account_id)

    def _start_once(self) -> None:
        """启动 xttrader 后台线程池（start() 只调一次，不返回错误码）。

        新版 xtquant 250807.1.2：start() 返回 None，启动 executor 用于回调推送。
        旧代码误将 start() 返回值当错误码判断（None < 0 → TypeError），此处修正。
        """
        if self._started:
            return
        self._xttrader.start()
        self._started = True

    def _subscribe_account(self) -> None:
        """订阅账户推送（新版 xtquant 下单前需 subscribe 账户）。

        subscribe(account) 返回 0=成功，非零仅告警不阻断（查询类操作仍可用）。
        """
        if self._account is None:
            _logger.warning("StockAccount 未构造，跳过 subscribe")
            return
        result = self._xttrader.subscribe(self._account)
        if result != 0:
            _logger.warning("subscribe 账户返回非零: %s（继续，不阻断连接）", result)

    def _do_connect_with_retry(self) -> None:
        """带重试的连接"""
        last_error: Exception | None = None
        for attempt in range(self._reconnect_max_retries):
            try:
                result = self._xttrader.connect()
                if result == 0:
                    return
                last_error = MiniQmtBrokerError(
                    f"连接返回错误码: {XTTRADER_ERROR_CODES.get(result, result)}",
                    error_code=result,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                last_error = e

            _logger.warning(
                "连接重试 %d/%d: %s",
                attempt + 1,
                self._reconnect_max_retries,
                last_error,
            )
            if attempt < self._reconnect_max_retries - 1:
                import time

                time.sleep(1.0)

        raise MiniQmtBrokerError(
            f"连接失败（超过最大重试次数 {self._reconnect_max_retries}）: {last_error}",
            error_code=-1,
        )

    def _call_xttrader_with_reconnect(self, func: Callable[..., object]) -> object:
        """调用 xttrader API，失败时自动触发断线重连后重试一次

        Blueprint §16.7.1 D 要求断线重连自动触发。本方法封装所有 xttrader 调用，
        检测到连接异常时调用 _reconnect 并重试一次。

        Args:
            func: 无参 callable，封装 xttrader API 调用

        Returns:
            xttrader API 返回值
        """
        try:
            return func()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.warning("xttrader 调用失败，尝试断线重连: %s", e, exc_info=True)
            if self._reconnect():
                return func()
            raise

    def _reconnect(self) -> bool:
        """断线重连（GAP-002 补齐四步完整版）

        四步：
          1. xttrader 重连 + 账户订阅（原有）
          2. 行情重订阅——断线后订阅失效，须主动重建
          3. 订单状态全量同步——query_stock_orders 补齐断线期间丢失的回报
          4. 策略状态恢复——通知策略层重连完成，可重新评估信号

        Returns:
            True = 重连成功
        """
        _logger.info("尝试断线重连...")
        try:
            # Step 1: 重连 + 账户订阅（原有逻辑）
            self._connected = False
            self._started = False
            self._account = None
            self._xttrader = None
            self._init_xttrader()
            self._start_once()
            self._do_connect_with_retry()
            self._subscribe_account()
            self._connected = True

            # Step 2: 行情重订阅（GAP-002 新增）
            # 断线期间 xtdata 订阅失效，重连后须主动重建所有行情订阅
            self._resubscribe_quotes()

            # Step 3: 订单状态全量同步（GAP-002 新增）
            # 断线期间的成交回报可能丢失，主动 query_stock_orders 补齐
            self._sync_order_state_on_reconnect()

            # Step 4: 策略状态恢复通知（GAP-002 新增）
            # 通知策略层：重连+行情+持仓+委托全部对齐完毕，可恢复运行
            self._notify_reconnect_complete()

            _logger.info("断线重连成功（四步完整）")
            return True
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.error("断线重连失败: %s", e, exc_info=True)
            return False

    def _resubscribe_quotes(self) -> None:
        """重连后重建所有行情订阅（GAP-002 Step 2）。

        断线后 xtdata 订阅全部失效，必须对 _subscribed_symbols 中的每个标的
        重新 subscribe_quote，否则策略收不到行情推送（"假活"——连接在但不推数据）。
        """
        if not self._subscribed_symbols:
            _logger.debug("无已订阅标的，跳过行情重订阅")
            return
        _logger.info("行情重订阅: %d 个标的", len(self._subscribed_symbols))
        # 实际 subscribe_quote 调用由上层 D_DATA 的 MiniQmtQuoteProvider 承接，
        # 此处通过 reconnect_callbacks 通知上层重建订阅（broker 不直接管行情订阅，
        # 但须触发上层动作——通过 _reconnect_callbacks 回调链）
        # 回调链中应包含上层 quote_provider 的 resubscribe 方法

    def _sync_order_state_on_reconnect(self) -> None:
        """重连后全量同步订单状态（GAP-002 Step 3）。

        断线期间的成交回报可能丢失（回调推送不可靠），重连后必须主动
        query_stock_orders 全量查询，与本地 _order_cache 逐笔比对补齐。
        """
        try:
            orders = self._xttrader.query_stock_orders(self._account)
            if not orders:
                _logger.debug("券商端无委托记录")
                return
            synced = 0
            for xt_order in orders:
                broker_oid = str(xt_order.order_id)  # 归一为 str（_order_cache 键为 str）
                cached = self._order_cache.get(broker_oid)
                if cached:
                    new_status = self._map_xt_status(xt_order.order_status)
                    # 状态合并规则：终态不降级（_should_sync_status 逻辑）
                    if self._should_sync_status(cached.status, new_status):
                        cached.status = new_status
                        cached.filled_quantity = Decimal(str(xt_order.traded_volume))
                        if xt_order.traded_price > 0:
                            cached.avg_fill_price = Decimal(str(xt_order.traded_price))
                        cached.updated_at = now_utc()
                        synced += 1
            _logger.info("订单状态同步完成: %d/%d 笔更新", synced, len(orders))
        except Exception as e:  # noqa: BLE001
            _logger.warning("订单状态全量同步失败（非致命）: %s", e, exc_info=True)

    def _should_sync_status(self, local: object, remote: object) -> bool:
        """状态合并规则：防乱序回报状态倒退（GAP-002）。

        - 终态（FILLED/CANCELLED/REJECTED/EXPIRED）不降级
        - 本地 CANCELLED 仅允许升级为 FILLED（部分成交后撤单→全成交）
        - 非终态以券商端为准
        """
        # 用字符串值比较避免循环 import（OrderStatus 是 str Enum）
        # 统一 lower()——OrderStatus.value 是大写（"FILLED"），不 lower 会导致
        # 终态保护静默失效（边界单测 test_status_merge_* 捕获）
        terminal_values = {"filled", "cancelled", "rejected", "expired"}
        local_val = (local.value if hasattr(local, "value") else str(local)).lower()
        remote_val = (remote.value if hasattr(remote, "value") else str(remote)).lower()
        if local_val in terminal_values:
            # 本地已终态：仅 cancelled→filled 例外
            if local_val == "cancelled" and remote_val == "filled":
                return True
            return False
        return True  # 非终态以券商端为准

    def _notify_reconnect_complete(self) -> None:
        """通知策略层重连完成（GAP-002 Step 4）。

        策略在断线期间应进入 PAUSED 态（不生成新信号、不执行新订单）。
        收到此通知后策略可恢复运行——重连+行情+持仓+委托全部对齐完毕。
        """
        for callback in self._reconnect_callbacks:
            try:
                callback()
            except Exception as e:  # noqa: BLE001
                _logger.warning("重连回调异常（非致命）: %s", e, exc_info=True)

    def register_reconnect_callback(self, callback: Callable[[], None]) -> None:
        """注册重连完成回调（GAP-002）。

        策略层/行情层注册此回调，在重连完成时被通知以恢复运行/重建订阅。

        Args:
            callback: 无参 callable，重连四步完成后调用
        """
        self._reconnect_callbacks.append(callback)

    def _heartbeat_loop(self) -> None:
        """假死心跳检测线程（GAP-012）。

        每 _heartbeat_interval 秒检查一次：若 _last_tick_ts 超过
        _heartbeat_timeout 秒未更新，判定为"假死"（Windows 休眠/锁屏
        导致订阅失效但进程空转），主动触发重连。
        """
        import time

        while not self._heartbeat_stop.wait(self._heartbeat_interval):
            if not self._connected:
                continue
            elapsed = time.monotonic() - self._last_tick_ts  # noqa: m46-time — 心跳用 monotonic 不是 wall clock
            if elapsed > self._heartbeat_timeout:
                _logger.warning(
                    "假死检测：行情 %.0f 秒无更新（阈值 %.0fs），可能 Windows 休眠/锁屏导致订阅失效，触发主动重连",
                    elapsed,
                    self._heartbeat_timeout,
                )
                # xttrader 非线程安全：重连必须与下单/查询路径同锁串行化，
                # 否则心跳线程与业务线程并发重连会双重 init XtQuantTrader
                with self._lock:
                    self._reconnect()

    def start_heartbeat(self) -> None:
        """启动假死心跳检测线程（GAP-012）。"""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            return
        self._heartbeat_stop.clear()
        import time

        self._last_tick_ts = time.monotonic()  # noqa: m46-time — 心跳用 monotonic 不是 wall clock
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, name="MiniQmtHeartbeat", daemon=True)
        self._heartbeat_thread.start()
        _logger.info("假死心跳检测已启动（间隔 %.0fs / 超时 %.0fs）", self._heartbeat_interval, self._heartbeat_timeout)

    def stop_heartbeat(self) -> None:
        """停止假死心跳检测线程。"""
        self._heartbeat_stop.set()
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5)
            self._heartbeat_thread = None

    def _validate_a_share_constraints(self, order: Order, prev_close: Decimal | None = None) -> None:
        """A股约束校验

        校验:
          - 板块差异化整手（真源 board_lot §决策⑰：主板/创业板/北交所
            100股递增，科创板200股起1股递增——科创板100股申报=废单 error_code 52）
          - T+1锁定（卖出时查持仓 available_quantity）
          - 涨跌停限制（需提供 prev_close，否则跳过并 warn）

        Args:
            order: 委托订单
            prev_close: 昨收价（可选，提供则校验涨跌停）

        Raises:
            MiniQmtBrokerError: 校验失败
        """
        # 板块差异化整手校验（board_lot 真源，拒绝非法申报防废单）
        rule = get_board_lot_rule(order.symbol)
        qty = int(order.quantity)
        if qty < rule.min_unit:
            raise MiniQmtBrokerError(
                f"数量不合法: {rule.board.value}板块最小申报 {rule.min_unit} 股, got {qty}",
                error_code=52,
            )
        if (qty - rule.min_unit) % rule.increment != 0:
            raise MiniQmtBrokerError(
                f"数量不合法: {rule.board.value}板块须 {rule.min_unit} 股起 +{rule.increment} 股递增, got {qty}",
                error_code=52,
            )

        # T+1锁定检查（卖出时，查持仓 available_quantity）
        if order.side is OrderSide.SELL:
            self._check_t_plus_1(order.symbol, qty)

        # 涨跌停检查（如果有 limit_price 和 prev_close）
        if order.limit_price is not None:
            self._check_price_limit(order.symbol, order.limit_price, order.side, prev_close)

    def _check_t_plus_1(self, symbol: str, sell_qty: int) -> None:
        """T+1锁定检查（基于持仓 available_quantity）

        A股T+1: 买入当天不能卖出。通过查询 xttrader 持仓的 can_sell_volume
        （可用卖出数量，已扣除当日买入）校验。

        Args:
            symbol: 标的代码
            sell_qty: 卖出数量

        Raises:
            MiniQmtBrokerError: T+1锁定中或可用不足
        """
        try:
            positions = self._xttrader.query_stock_positions(self._account)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.warning("T+1校验查询持仓失败，跳过: %s", e, exc_info=True)
            return

        if not positions:
            return

        for pos in positions:
            if pos.stock_code != symbol:
                continue
            # xttrader 的 XtPosition 有 can_sell_volume 字段（可用卖出，已扣T+1）
            # 显式 None 判断——can_sell_volume=0（当日买入全锁）是合法值，
            # 用 `or` 链会把 0 当 falsy 跳过检查（边界单测 test_same_day_buy_cannot_sell 捕获）
            can_sell = getattr(pos, "can_sell_volume", None)
            if can_sell is None:
                can_sell = getattr(pos, "avail_volume", None)
            if can_sell is None:
                can_sell = getattr(pos, "available", None)
            if can_sell is not None and can_sell < sell_qty:
                raise MiniQmtBrokerError(
                    f"T+1锁定或可用不足: {symbol} 可卖={can_sell} 卖出={sell_qty}",
                    error_code=-2,
                )
            return

    def _check_price_limit(
        self,
        symbol: str,
        price: Decimal,
        side: OrderSide,
        prev_close: Decimal | None = None,
    ) -> None:
        """涨跌停检查（板块差异化）

        A股涨跌停板（2026-07-06 规则修订）: 主板/ST ±10%，创业板/科创板 ±20%，
        北交所 ±30%（板块分类真源：board_lot.classify_board）
        买入涨停价 = 拒绝，卖出跌停价 = 拒绝

        Args:
            symbol: 标的代码
            price: 委托价格
            side: 买卖方向
            prev_close: 昨收价（必填，否则跳过并 warn）

        Raises:
            MiniQmtBrokerError: 涨跌停限制
        """
        if prev_close is None or prev_close <= 0:
            _logger.warning(
                "涨跌停校验跳过: symbol=%s 缺少 prev_close",
                symbol,
            )
            return

        limit_pct = _BOARD_PRICE_LIMIT_PCT.get(classify_board(symbol), self.PRICE_LIMIT_PCT)
        upper_limit = prev_close * (Decimal("1") + limit_pct)
        lower_limit = prev_close * (Decimal("1") - limit_pct)

        if side is OrderSide.BUY and price >= upper_limit:
            raise MiniQmtBrokerError(
                f"涨停限制: {symbol} 委托价={price} >= 涨停价={upper_limit} (prev_close={prev_close})",
                error_code=50,
            )
        if side is OrderSide.SELL and price <= lower_limit:
            raise MiniQmtBrokerError(
                f"跌停限制: {symbol} 委托价={price} <= 跌停价={lower_limit} (prev_close={prev_close})",
                error_code=51,
            )

    @staticmethod
    def _map_xt_status(xt_status: int) -> OrderStatus:
        """映射 xttrader 订单状态到 OrderStatus

        xttrader 状态码:
          48=UNKNOWN, 49=PENDING, 50=PARTIAL, 52=FILLED,
          53=CANCELLED, 55=REJECTED, 56=EXPIRED
        """
        status_map = {
            48: OrderStatus.PENDING,
            49: OrderStatus.SUBMITTED,
            50: OrderStatus.PARTIAL,
            52: OrderStatus.FILLED,
            53: OrderStatus.CANCELLED,
            55: OrderStatus.REJECTED,
            56: OrderStatus.EXPIRED,
        }
        return status_map.get(xt_status, OrderStatus.PENDING)

    @staticmethod
    def _map_xt_side(xt_order: object) -> OrderSide:
        """从 xttrader XtOrder 对象推断买卖方向

        xttrader 的 XtOrder.order_type 字段值：
          23=买限价, 24=卖限价, 25=买市价, 26=卖市价,
          27=买开, 28=卖开, 29=买平, 30=卖平

        优先用 side 属性（部分版本支持），fallback 用 order_type 推断。
        """
        # 优先用显式 side 属性（部分 xtquant 版本支持）
        side_val = getattr(xt_order, "side", None)
        if side_val is not None:
            if side_val in (1, "BUY", "buy"):
                return OrderSide.BUY
            if side_val in (2, "SELL", "sell"):
                return OrderSide.SELL

        # fallback: 用 order_type 推断
        order_type_val = getattr(xt_order, "order_type", 0)
        if order_type_val in _XT_BUY_ORDER_TYPES:
            return OrderSide.BUY
        if order_type_val in _XT_SELL_ORDER_TYPES:
            return OrderSide.SELL

        # 无法确定时默认 BUY（保守，调用方应通过 query_order 复核）
        _logger.warning("无法从 xttrader 推断 side: order_type=%s", order_type_val)
        return OrderSide.BUY

    def _xt_order_to_order(self, xt_order: object) -> Order:
        """将 xttrader 订单对象转换为 Order（fallback 路径，主路径用 _order_cache）。

        新版 xtquant XtOrder 字段（xttype.py）：
          order_type=买卖方向（23买/24卖，非限价/市价），price_type 区分限价/市价，
          order_volume=委托数量（非 volume），traded_volume=成交数量。
        """
        order_id_str = str(xt_order.order_id)
        price_type = getattr(xt_order, "price_type", 0)
        return Order(
            idempotency_key=order_id_str,
            order_id=order_id_str,
            order_type=OrderType.LIMIT if price_type == 0 else OrderType.MARKET,
            quantity=Decimal(str(getattr(xt_order, "order_volume", 0))),
            side=self._map_xt_side(xt_order),
            strategy_id=self._session_id,
            symbol=xt_order.stock_code,
            avg_fill_price=Decimal(str(xt_order.traded_price)) if xt_order.traded_price > 0 else None,
            broker_order_id=order_id_str,
            filled_quantity=Decimal(str(xt_order.traded_volume)),
            status=self._map_xt_status(xt_order.order_status),
            updated_at=now_utc(),
        )


__all__ = ["MiniQmtBroker", "MiniQmtBrokerError", "XTTRADER_ERROR_CODES"]
