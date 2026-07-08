# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.adapters.miniqmt_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.trading_contracts.broker_interface; zephyr.backtest.core.matching_logic; zephyr.governance.data_governance.miniqmt_provider
# [CONSUMERS] zephyr.frontend.dashboard.components.trade_panel; zephyr.frontend.dashboard.components.position_monitor
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] xttrader非线程安全(加锁); T+1锁定(查持仓available_quantity); 涨跌停限制; 幂等(INV-007); 回测=实盘一致性(MatchingLogic共享, submit_order内置预校验)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MiniQmtBrokerError
# [TESTS]
# [A_module] module_id=MOD-L06-001-miniqmt_broker | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易）

职责:
  - 对接国金证券 MiniQMT 终端的 xttrader API，提供 A 股实盘交易能力
  - 实现 BrokerInterface（OCP-003 扩展点）
  - A股约束校验: T+1锁定(查持仓available_quantity) / 涨跌停限制 / 100股整数倍 / 停牌跳过
  - 幂等下单: 所有订单携带 idempotency_key（INV-007）
  - 断线重连: 连接失败时自动重试；xttrader调用失败自动触发_reconnect
  - 回测=实盘一致性: 共用 MatchingLogic 做预成交校验（submit_order内置）

约束:
  - xttrader 非线程安全，所有调用需加锁（threading.Lock）
  - MiniQMT 仅 Windows，必须先启动 XtMiniQmt.exe 终端
  - xttrader 需开通 A 股实盘权限
  - 与 D_DATA MiniQmtProvider 共用 xtquant 连接（shared_xtquant_conn）

xttrader 错误码映射:
  0=成功, -1=连接失败, -2=未就绪, -3=订单号重复,
  50=涨停, 51=跌停, 52=数量不合法, 53=价格不合法,
  54=资金不足, 55=持仓不足

A股约束:
  - t_plus=1 (T+1锁定，买入当天不能卖出)
  - min_order_qty=100 (最小交易单位100股)
  - price_tick=0.01 (价格最小变动单位)
  - asset_classes=[stock, etf, convertible_bond]

SSoT: docs/03_modules/_domain_execution_core/blueprint.md §16.7.1 MiniQmtBroker
"""

from __future__ import annotations

from typing import Final
import logging
import threading
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from zephyr.backtest.core.matching_logic import (
    MatchingConfig,
    MatchingFill,
    MatchingLogic,
    MatchOrderInput,
    OrderBookSnapshot,
)
from zephyr.governance.trading_contracts.broker_interface import (
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
from zephyr.shared.utils.time_utils import now_utc

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

# xttrader 订单类型映射
_XTTRADER_ORDER_TYPE = {
    OrderType.MARKET: 5,    # 市价单
    OrderType.LIMIT: 11,    # 限价单（ xttrader LATEST_PRICE=11）
}

# xttrader 价格类型映射
_XTTRADER_PRICE_TYPE = {
    OrderType.MARKET: -1,   # 市价：最新价
    OrderType.LIMIT: 0,     # 限价：指定价格
}

# xttrader 方向常量（XtOrder.order_type 字段值，参考 xtquant 文档）
_XT_BUY_ORDER_TYPES = {23, 25, 27, 29}  # 买限价/买市价/买开/买平
_XT_SELL_ORDER_TYPES = {24, 26, 28, 30}  # 卖限价/卖市价/卖开/卖平


class MiniQmtBrokerError(Exception):
    """MiniQMT 券商错误"""
    error_code = "ZA-XC-0001"

    def __init__(self, message: str, error_code: Optional[int] = None):
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
        # 与 D_DATA 共用 xtquant 连接
        provider = MiniQmtProvider(path="D:/国金QMT/userdata_mini")
        broker = MiniQmtBroker(
            path="D:/国金QMT/userdata_mini",
            session_id="zephyr_session",
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
    MIN_ORDER_QTY = 100
    PRICE_TICK = Decimal("0.01")
    PRICE_LIMIT_PCT = Decimal("0.10")  # 涨跌停 ±10%（ST股 ±5% 简化）
    ASSET_CLASSES = ["stock", "etf", "convertible_bond"]

    def __init__(
        self,
        path: str = "",
        session_id: str = "zephyr_session",
        shared_xtquant_conn: Optional[Any] = None,
        matching_logic: Optional[MatchingLogic] = None,
        matching_config: Optional[MatchingConfig] = None,
        reconnect_max_retries: int = 3,
    ):
        """初始化 MiniQMT 券商适配器

        Args:
            path: miniQMT 安装路径（userdata_mini 目录）
            session_id: 会话 ID（用于 xttrader 连接标识）
            shared_xtquant_conn: 与 D_DATA 共用的 MiniQmtProvider 实例（可选）
                若提供，则复用其 xtquant 连接，避免重复 connect 到 miniQMT 终端
            matching_logic: 与 D_BACKTEST 共用的 MatchingLogic 实例（可选）
            matching_config: 撮合配置（matching_logic 为空时用此创建，可选）
            reconnect_max_retries: 断线重连最大重试次数
        """
        self._path = path
        self._session_id = session_id
        self._shared_conn = shared_xtquant_conn
        self._matching_logic = matching_logic or MatchingLogic(
            matching_config or MatchingConfig()
        )
        self._reconnect_max_retries = reconnect_max_retries

        # xttrader 懒加载
        self._xttrader: Any = None
        self._connected = False

        # 线程安全锁（xttrader 非线程安全；保护共享状态如 _fill_callbacks）
        self._lock = threading.Lock()

        # 幂等去重：idempotency_key -> broker_order_id
        self._idempotency_map: dict[str, str] = {}

        # 订单状态缓存：broker_order_id -> Order
        self._order_cache: dict[str, Order] = {}

        # 成交回调（受 _lock 保护）
        self._fill_callbacks: list[FillCallback] = []

    # ------------------------------------------------------------------
    # BrokerInterface 实现
    # ------------------------------------------------------------------

    @property
    def broker_id(self) -> str:
        """券商唯一标识"""
        return "miniqmt"

    def connect(self) -> bool:
        """建立与 MiniQMT 终端的连接

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
                self._do_connect_with_retry()
                self._connected = True
                _logger.info("MiniQMT 券商连接成功 path=%s session=%s", self._path, self._session_id)
                return True
            except Exception as e:
                self._connected = False
                raise MiniQmtBrokerError(
                    f"MiniQMT 连接失败: {e}", error_code=-1
                ) from e

    def disconnect(self) -> None:
        """断开连接"""
        with self._lock:
            if self._xttrader is not None:
                try:
                    self._xttrader.stop()
                except Exception as e:
                    _logger.warning("断开连接时出错: %s", e, exc_info=True)
                self._xttrader = None
            self._connected = False
            _logger.info("MiniQMT 券商已断开")

    def submit_order(
        self,
        order: Order,
        order_book: Optional[OrderBookSnapshot] = None,
        prev_close: Optional[Decimal] = None,
    ) -> str:
        """发送委托订单

        流程:
          1. 幂等检查（idempotency_key 去重）
          2. A股约束校验（100股整数倍 / 涨跌停 / T+1查持仓available_quantity）
          3. 回测=实盘一致性预校验（可选 order_book，调用 MatchingLogic 模拟成交）
          4. 调用 xttrader.order_stock 下单
          5. 错误码映射
          6. 缓存订单状态

        Args:
            order: 委托订单（必须含 idempotency_key）
            order_book: 当前5档盘口快照（可选，提供则做 MatchingLogic 预校验）
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
                    order.idempotency_key, existing_id,
                )
                return existing_id

            # 2. A股约束校验
            self._validate_a_share_constraints(order, prev_close)

            # 3. 回测=实盘一致性预校验（B方案核心：下单路径经过 MatchingLogic）
            if order_book is not None:
                fill_preview = self._pre_trade_simulate_locked(order, order_book)
                _logger.info(
                    "预成交校验: symbol=%s 预估均价=%s 预估成交量=%s",
                    order.symbol, fill_preview.avg_fill_price, fill_preview.filled_quantity,
                )

            # 4. 调用 xttrader 下单
            if not self._connected:
                raise MiniQmtBrokerError("未连接，请先调用 connect()", error_code=-1)

            try:
                seq = self._xttrader.start()
                if seq < 0:
                    raise MiniQmtBrokerError(
                        f"xttrader.start() 失败: {XTTRADER_ERROR_CODES.get(seq, '未知错误')}",
                        error_code=seq,
                    )

                # 构造 xttrader 订单
                xt_order_type = _XTTRADER_ORDER_TYPE.get(order.order_type, 11)
                xt_price_type = _XTTRADER_PRICE_TYPE.get(order.order_type, 0)
                limit_price = float(order.limit_price) if order.limit_price else 0.0

                result = self._call_xttrader_with_reconnect(
                    lambda: self._xttrader.order_stock(
                        account=self._session_id,
                        order_id=order.order_id,
                        code=order.symbol,
                        price=limit_price,
                        volume=int(order.quantity),
                        price_type=xt_price_type,
                        order_type=xt_order_type,
                    )
                )
            except MiniQmtBrokerError:
                raise
            except Exception as e:
                raise MiniQmtBrokerError(
                    f"xttrader 下单异常: {e}", error_code=-1
                ) from e

            # 5. 错误码映射
            if result != 0:
                error_msg = XTTRADER_ERROR_CODES.get(result, f"未知错误码: {result}")
                raise MiniQmtBrokerError(
                    f"下单失败: {error_msg} (code={result})",
                    error_code=result,
                )

            # 6. 缓存订单
            broker_order_id = order.order_id
            order.status = OrderStatus.SUBMITTED
            order.broker_order_id = broker_order_id
            order.updated_at = now_utc()
            self._idempotency_map[order.idempotency_key] = broker_order_id
            self._order_cache[broker_order_id] = order

            _logger.info(
                "下单成功: broker_order_id=%s symbol=%s side=%s qty=%s",
                broker_order_id, order.symbol, order.side.value, order.quantity,
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
                        account=self._session_id,
                        order_id=broker_order_id,
                    )
                )
            except Exception as e:
                raise MiniQmtBrokerError(
                    f"xttrader 撤单异常: {e}", error_code=-1
                ) from e

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

    def query_order(self, broker_order_id: str) -> Optional[Order]:
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
                orders = self._call_xttrader_with_reconnect(
                    lambda: self._xttrader.query_stock_orders(account=self._session_id)
                )
            except Exception as e:
                raise MiniQmtBrokerError(
                    f"xttrader 查询订单异常: {e}", error_code=-1
                ) from e

            if not orders:
                return self._order_cache.get(broker_order_id)

            # 查找匹配的订单
            for xt_order in orders:
                if xt_order.order_id == broker_order_id:
                    # 更新缓存
                    cached = self._order_cache.get(broker_order_id)
                    if cached:
                        cached.status = self._map_xt_status(xt_order.order_status)
                        cached.filled_quantity = Decimal(str(xt_order.traded_volume))
                        cached.avg_fill_price = (
                            Decimal(str(xt_order.traded_price))
                            if xt_order.traded_price > 0
                            else None
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
                    lambda: self._xttrader.query_stock_positions(
                        account=self._session_id
                    )
                )
                xt_asset = self._call_xttrader_with_reconnect(
                    lambda: self._xttrader.query_stock_asset(
                        account=self._session_id
                    )
                )
            except Exception as e:
                raise MiniQmtBrokerError(
                    f"xttrader 查询持仓异常: {e}", error_code=-1
                ) from e

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
            order_book: 当前5档盘口快照（从 MiniQmtProvider.get_order_book 获取）

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
        """懒加载 xttrader 模块并初始化 XtQuantTrader

        若提供了 shared_xtquant_conn（D_DATA MiniQmtProvider），优先复用其连接，
        避免重复 connect 到 miniQMT 终端（Blueprint §16.7.1 F 共用 xtquant 连接）。
        """
        if self._xttrader is not None:
            return

        # 优先复用 D_DATA MiniQmtProvider 的 xttrader 连接
        if self._shared_conn is not None:
            shared_trader = getattr(self._shared_conn, "xttrader", None) \
                or getattr(self._shared_conn, "_xttrader", None)
            if shared_trader is not None:
                self._xttrader = shared_trader
                _logger.info("复用 D_DATA MiniQmtProvider 的 xttrader 连接")
                return

        # 懒加载 xtquant 并新建 XtQuantTrader
        try:
            from xtquant.xttrader import XtQuantTrader  # type: ignore[import-not-found]
        except ImportError as e:
            raise MiniQmtBrokerError(
                "xtquant 未安装。请从 QMT 安装目录 bin.x64/Lib/site-packages/xtquant "
                "拷贝到 Python 环境的 site-packages。",
                error_code=-1,
            ) from e

        self._xttrader = XtQuantTrader(self._path, self._session_id)

    def _do_connect_with_retry(self) -> None:
        """带重试的连接"""
        last_error: Optional[Exception] = None
        for attempt in range(self._reconnect_max_retries):
            try:
                result = self._xttrader.connect()
                if result == 0:
                    return
                last_error = MiniQmtBrokerError(
                    f"连接返回错误码: {XTTRADER_ERROR_CODES.get(result, result)}",
                    error_code=result,
                )
            except Exception as e:
                last_error = e

            _logger.warning(
                "连接重试 %d/%d: %s", attempt + 1, self._reconnect_max_retries, last_error,
            )
            if attempt < self._reconnect_max_retries - 1:
                import time

                time.sleep(1.0)

        raise MiniQmtBrokerError(
            f"连接失败（超过最大重试次数 {self._reconnect_max_retries}）: {last_error}",
            error_code=-1,
        )

    def _call_xttrader_with_reconnect(self, func: Any) -> Any:
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
        except Exception as e:
            _logger.warning("xttrader 调用失败，尝试断线重连: %s", e, exc_info=True)
            if self._reconnect():
                return func()
            raise

    def _reconnect(self) -> bool:
        """断线重连

        Returns:
            True = 重连成功
        """
        _logger.info("尝试断线重连...")
        try:
            self._connected = False
            self._xttrader = None
            self._init_xttrader()
            self._do_connect_with_retry()
            self._connected = True
            _logger.info("断线重连成功")
            return True
        except Exception as e:
            _logger.error("断线重连失败: %s", e, exc_info=True)
            return False

    def _validate_a_share_constraints(
        self, order: Order, prev_close: Optional[Decimal] = None
    ) -> None:
        """A股约束校验

        校验:
          - 100股整数倍
          - T+1锁定（卖出时查持仓 available_quantity）
          - 涨跌停限制（需提供 prev_close，否则跳过并 warn）

        Args:
            order: 委托订单
            prev_close: 昨收价（可选，提供则校验涨跌停）

        Raises:
            MiniQmtBrokerError: 校验失败
        """
        # 100股整数倍
        qty = int(order.quantity)
        if qty < self.MIN_ORDER_QTY:
            raise MiniQmtBrokerError(
                f"数量不合法: 最小 {self.MIN_ORDER_QTY} 股, got {qty}",
                error_code=52,
            )
        if qty % self.MIN_ORDER_QTY != 0:
            raise MiniQmtBrokerError(
                f"数量不合法: 必须 {self.MIN_ORDER_QTY} 股整数倍, got {qty}",
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
            positions = self._xttrader.query_stock_positions(account=self._session_id)
        except Exception as e:
            _logger.warning("T+1校验查询持仓失败，跳过: %s", e, exc_info=True)
            return

        if not positions:
            return

        for pos in positions:
            if pos.stock_code != symbol:
                continue
            # xttrader 的 XtPosition 有 can_sell_volume 字段（可用卖出，已扣T+1）
            can_sell = getattr(pos, "can_sell_volume", None) \
                or getattr(pos, "avail_volume", None) \
                or getattr(pos, "available", None)
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
        prev_close: Optional[Decimal] = None,
    ) -> None:
        """涨跌停检查

        A股涨跌停板: ±10%（ST股 ±5%，当前简化统一用10%）
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
                "涨跌停校验跳过: symbol=%s 缺少 prev_close", symbol,
            )
            return

        upper_limit = prev_close * (Decimal("1") + self.PRICE_LIMIT_PCT)
        lower_limit = prev_close * (Decimal("1") - self.PRICE_LIMIT_PCT)

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
    def _map_xt_side(xt_order: Any) -> OrderSide:
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

    def _xt_order_to_order(self, xt_order: Any) -> Order:
        """将 xttrader 订单对象转换为 Order"""
        return Order(
            idempotency_key=xt_order.order_id,
            order_id=xt_order.order_id,
            order_type=OrderType.LIMIT if xt_order.order_type in (11, 23, 24) else OrderType.MARKET,
            quantity=Decimal(str(xt_order.volume)),
            side=self._map_xt_side(xt_order),
            strategy_id=self._session_id,
            symbol=xt_order.stock_code,
            avg_fill_price=Decimal(str(xt_order.traded_price)) if xt_order.traded_price > 0 else None,
            broker_order_id=xt_order.order_id,
            filled_quantity=Decimal(str(xt_order.traded_volume)),
            status=self._map_xt_status(xt_order.order_status),
            updated_at=now_utc(),
        )


__all__ = ["MiniQmtBroker", "MiniQmtBrokerError", "XTTRADER_ERROR_CODES"]
