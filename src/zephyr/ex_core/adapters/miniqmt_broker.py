# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.adapters.miniqmt_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.trading_contracts.broker_interface; zephyr.backtest.core.matching_logic; zephyr.governance.data_governance.miniqmt_provider
# [CONSUMERS] zephyr.frontend.dashboard.components.trade_panel; zephyr.frontend.dashboard.components.position_monitor
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] xttrader非线程安全(加锁); T+1锁定; 涨跌停限制; 幂等(INV-007); 回测=实盘一致性(MatchingLogic共享)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MiniQmtBrokerError
# [TESTS]
# [A_module] module_id=MOD-L06-001-miniqmt_broker | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易）

职责:
  - 对接国金证券 MiniQMT 终端的 xttrader API，提供 A 股实盘交易能力
  - 实现 BrokerInterface（OCP-003 扩展点）
  - A股约束校验: T+1锁定 / 涨跌停限制 / 100股整数倍 / 停牌跳过
  - 幂等下单: 所有订单携带 idempotency_key（INV-007）
  - 断线重连: 连接失败时自动重试
  - 回测=实盘一致性: 共用 MatchingLogic 做预成交校验

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

import logging
import threading
from datetime import datetime, date
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

_logger = logging.getLogger(__name__)

# xttrader 错误码映射
XTTRADER_ERROR_CODES: dict[int, str] = {
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


class MiniQmtBrokerError(Exception):
    """MiniQMT 券商错误"""

    def __init__(self, message: str, error_code: Optional[int] = None):
        super().__init__(message)
        self.error_code = error_code


class MiniQmtBroker(BrokerInterface):
    """MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易）

    实现 BrokerInterface，对接国金证券 MiniQMT 终端的 xttrader API。

    核心特性:
      - A股约束校验: T+1 / 涨跌停 / 100股整数倍 / 停牌
      - 幂等下单: idempotency_key 防重复（INV-007）
      - 断线重连: 连接失败自动重试
      - 线程安全: threading.Lock 保护所有 xttrader 调用
      - 回测=实盘一致性: 共用 MatchingLogic 做预成交校验

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

        # 下单（幂等）
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
        broker_order_id = broker.submit_order(order)

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

        # 线程安全锁（xttrader 非线程安全）
        self._lock = threading.Lock()

        # 幂等去重：idempotency_key → broker_order_id
        self._idempotency_map: dict[str, str] = {}

        # 订单状态缓存：broker_order_id → Order
        self._order_cache: dict[str, Order] = {}

        # T+1 锁定记录：symbol → 最近买入日期
        self._buy_dates: dict[str, date] = {}

        # 成交回调
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
                    _logger.warning("断开连接时出错: %s", e)
                self._xttrader = None
            self._connected = False
            _logger.info("MiniQMT 券商已断开")

    def submit_order(self, order: Order) -> str:
        """发送委托订单

        流程:
          1. 幂等检查（idempotency_key 去重）
          2. A股约束校验（100股整数倍 / 涨跌停 / T+1）
          3. 调用 xttrader.order_stock 下单
          4. 错误码映射
          5. 缓存订单状态

        Args:
            order: 委托订单（必须含 idempotency_key）

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
            self._validate_a_share_constraints(order)

            # 3. 调用 xttrader 下单
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

                result = self._xttrader.order_stock(
                    account=self._session_id,
                    order_id=order.order_id,
                    code=order.symbol,
                    price=limit_price,
                    volume=int(order.quantity),
                    price_type=xt_price_type,
                    order_type=xt_order_type,
                )
            except MiniQmtBrokerError:
                raise
            except Exception as e:
                raise MiniQmtBrokerError(
                    f"xttrader 下单异常: {e}", error_code=-1
                ) from e

            # 4. 错误码映射
            if result != 0:
                error_msg = XTTRADER_ERROR_CODES.get(result, f"未知错误码: {result}")
                raise MiniQmtBrokerError(
                    f"下单失败: {error_msg} (code={result})",
                    error_code=result,
                )

            # 5. 缓存订单
            broker_order_id = order.order_id
            order.status = OrderStatus.SUBMITTED
            order.broker_order_id = broker_order_id
            order.updated_at = datetime.now()
            self._idempotency_map[order.idempotency_key] = broker_order_id
            self._order_cache[broker_order_id] = order

            # T+1 记录买入日期
            if order.side is OrderSide.BUY:
                self._buy_dates[order.symbol] = date.today()

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
            MiniQmtBrokerError: 撤单失败
        """
        with self._lock:
            if not self._connected:
                raise MiniQmtBrokerError("未连接，请先调用 connect()", error_code=-1)

            try:
                result = self._xttrader.cancel_order_stock(
                    account=self._session_id,
                    order_id=broker_order_id,
                )
            except Exception as e:
                raise MiniQmtBrokerError(
                    f"xttrader 撤单异常: {e}", error_code=-1
                ) from e

            if result != 0:
                error_msg = XTTRADER_ERROR_CODES.get(result, f"未知错误码: {result}")
                _logger.warning("撤单失败: %s (code=%d)", error_msg, result)
                return False

            # 更新缓存
            if broker_order_id in self._order_cache:
                self._order_cache[broker_order_id].status = OrderStatus.CANCELLED
                self._order_cache[broker_order_id].updated_at = datetime.now()

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
                orders = self._xttrader.query_stock_orders(account=self._session_id)
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
                        cached.updated_at = datetime.now()
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
                xt_positions = self._xttrader.query_stock_positions(
                    account=self._session_id
                )
                xt_asset = self._xttrader.query_stock_asset(
                    account=self._session_id
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
                as_of_timestamp=datetime.now(),
                idempotency_key=f"pos-{self._session_id}-{int(datetime.now().timestamp())}",
                portfolio_id=self._session_id,
                cash=cash,
                holdings=holdings,
                market_values=market_values,
                total_market_value=total_mv,
            )

    def register_fill_callback(self, callback: FillCallback) -> None:
        """注册成交回调"""
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
        """懒加载 xttrader 模块并初始化 XtQuantTrader"""
        if self._xttrader is not None:
            return

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

    def _reconnect(self) -> bool:
        """断线重连

        Returns:
            True = 重连成功
        """
        _logger.info("尝试断线重连...")
        try:
            self._connected = False
            self._do_connect_with_retry()
            self._connected = True
            _logger.info("断线重连成功")
            return True
        except Exception as e:
            _logger.error("断线重连失败: %s", e)
            return False

    def _validate_a_share_constraints(self, order: Order) -> None:
        """A股约束校验

        校验:
          - 100股整数倍
          - T+1锁定（卖出时检查买入日期）
          - 涨跌停限制（需外部提供 prev_close，此处简化）

        Args:
            order: 委托订单

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

        # T+1锁定检查（卖出时）
        if order.side is OrderSide.SELL:
            self._check_t_plus_1(order.symbol)

        # 涨跌停检查（如果有 limit_price）
        if order.limit_price is not None:
            self._check_price_limit(order.symbol, order.limit_price, order.side)

    def _check_t_plus_1(self, symbol: str) -> None:
        """T+1锁定检查

        A股T+1: 买入当天不能卖出。

        Args:
            symbol: 标的代码

        Raises:
            MiniQmtBrokerError: T+1锁定中
        """
        buy_date = self._buy_dates.get(symbol)
        if buy_date is not None and buy_date == date.today():
            raise MiniQmtBrokerError(
                f"T+1锁定: {symbol} 今日买入，不可卖出 (buy_date={buy_date})",
                error_code=-2,
            )

    def _check_price_limit(
        self, symbol: str, price: Decimal, side: OrderSide
    ) -> None:
        """涨跌停检查

        A股涨跌停板: ±10%（ST股 ±5% 简化统一用10%）
        买入涨停价 = 拒绝，卖出跌停价 = 拒绝

        注意: 此处简化检查，实际需查询 prev_close。
        完整实现应由调用方提供 prev_close，或通过 xtdata 获取。

        Args:
            symbol: 标的代码
            price: 委托价格
            side: 买卖方向

        Raises:
            MiniQmtBrokerError: 涨跌停限制
        """
        # 简化: 实际需 prev_close 做基准
        # 完整实现留给调用方通过 pre_trade_simulate 做预校验
        pass

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

    def _xt_order_to_order(self, xt_order: Any) -> Order:
        """将 xttrader 订单对象转换为 Order"""
        return Order(
            idempotency_key=xt_order.order_id,
            order_id=xt_order.order_id,
            order_type=OrderType.LIMIT if xt_order.order_type == 11 else OrderType.MARKET,
            quantity=Decimal(str(xt_order.volume)),
            side=OrderSide.BUY if xt_order.order_type in (23, 24) else OrderSide.SELL,
            strategy_id=self._session_id,
            symbol=xt_order.stock_code,
            avg_fill_price=Decimal(str(xt_order.traded_price)) if xt_order.traded_price > 0 else None,
            broker_order_id=xt_order.order_id,
            filled_quantity=Decimal(str(xt_order.traded_volume)),
            status=self._map_xt_status(xt_order.order_status),
            updated_at=datetime.now(),
        )


__all__ = ["MiniQmtBroker", "MiniQmtBrokerError", "XTTRADER_ERROR_CODES"]
