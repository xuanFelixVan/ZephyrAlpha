# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.adapters.okx_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.trading.trading_contracts.broker_interface; zephyr.shared.security.secrets; zephyr.ex_core.rules; zephyr.data.calendar
# [CONSUMERS] zephyr.ex_core.order_manager; zephyr.ex_core.trading_session
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 私有端点签名(HMAC-SHA256); 幂等(INV-007); 回执确认(隔1~2秒查委托,查不到重试并标记疑似丢单); 线程安全(lock)
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §5 CAND-CRYPTO-005
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OkxBrokerError(签名失败/网络异常/限频)
# [TESTS] tests/ex_core/adapters/test_okx_broker.py
# [A_module] module_id=MOD-L06-001 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""OKX 数字货币执行适配器（CAND-CRYPTO-005，94号 Q1 裁定 2026-08-31 修订：OKX 主+币安备[待开发]）。

对接 OKX V5 私有 REST API，提供 BTC/ETH 现货实盘交易能力。
实现 BrokerInterface（OCP-003 扩展点）。

核心特性:
  - 私有端点 HMAC-SHA256 签名（OKX V5 认证）
  - 幂等下单: idempotency_key 防重复（INV-007）
  - 回执确认: 下单后隔 1~2 秒查委托，查到写回执、查不到重试并标记疑似丢单
    （QMT 教训直接沿用，40_execution_broker §决策⑥）
  - 线程安全: threading.Lock 保护共享状态
  - 规则包注入: 按 CryptoRulePack 校验 step_size/tick_size/无涨跌停

约束:
  - OKX V5 私有端点需 API Key + Secret Key + Passphrase（三件套）
  - 限频: 私有端点 20req/2s（与公开端点共享额度）
  - 现货 T+0 无结算周期约束

SSoT: docs/03_modules/_domain_execution_core/blueprint.md §16.7.2 OkxBroker
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Final

import requests

from zephyr.data.calendar import CryptoCalendar
from zephyr.ex_core.rules import CryptoRulePack
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.security.secrets import get_service_secret
from zephyr.trading.trading_contracts.broker_interface import (
    BrokerInterface,
    FillCallback,
)

_logger = logging.getLogger(__name__)

# OKX V5 端点
_BASE_URL = "https://www.okx.com"
_API_PATH = "/api/v5"

# 限频: 20req/2s = 10/s 保守取 5/s（私有端点更敏感）
_RATE_LIMIT_SLEEP = 0.2  # 秒

# 回执确认参数（QMT 教训沿用）
_RECEIPT_CHECK_DELAY = 1.5  # 秒，下单后隔 1~2 秒查委托
_RECEIPT_MAX_RETRIES = 3  # 最大重试次数
_RECEIPT_RETRY_INTERVAL = 2.0  # 秒，重试间隔


class OkxBrokerError(Exception):
    """OKX 券商错误"""

    error_code = "ZA-XC-0002"

    def __init__(self, message: str, error_code: str | None = None):
        super().__init__(message)
        if error_code is not None:
            self.error_code = error_code


class OkxBroker(BrokerInterface):
    """OKX 数字货币执行适配器（对接 OKX V5 私有 REST API）。

    实现 BrokerInterface，提供 BTC/ETH 现货实盘交易能力。

    Usage:
        broker = OkxBroker()
        broker.connect()

        order = Order(
            idempotency_key="order-001",
            order_id="ord-001",
            order_type=OrderType.LIMIT,
            quantity=Decimal("0.001"),
            side=OrderSide.BUY,
            strategy_id="my_strategy",
            symbol="BTC-USDT",
            limit_price=Decimal("50000"),
        )
        broker_order_id = broker.submit_order(order)

        # 回执确认（内置）
        # broker._confirm_receipt(broker_order_id)

        # 查询/撤单
        order_status = broker.query_order(broker_order_id)
        broker.cancel_order(broker_order_id)

        # 查询持仓
        positions = broker.get_positions()
    """

    def __init__(
        self,
        rule_pack: CryptoRulePack | None = None,
        calendar: CryptoCalendar | None = None,
        rate_limit_sleep: float = _RATE_LIMIT_SLEEP,
    ):
        """初始化 OKX 券商适配器。

        Args:
            rule_pack: 币版交易规则包（None=默认 CryptoRulePack 骨架）
            calendar: 币版市场日历（None=默认 CryptoCalendar）
            rate_limit_sleep: 限频休眠秒数
        """
        self._rule_pack = rule_pack or CryptoRulePack()
        self._calendar = calendar or CryptoCalendar()
        self._rate_limit_sleep = rate_limit_sleep

        # API 密钥（懒加载，connect 时读取）
        self._api_key: str | None = None
        self._secret_key: str | None = None
        self._passphrase: str | None = None

        # 连接状态
        self._connected = False
        self._session: requests.Session | None = None

        # 线程安全锁
        self._lock = threading.Lock()

        # 幂等去重：idempotency_key -> broker_order_id
        self._idempotency_map: dict[str, str] = {}

        # 订单状态缓存：broker_order_id -> Order
        self._order_cache: dict[str, Order] = {}

        # 成交回调
        self._fill_callbacks: list[FillCallback] = []

        # 回执确认状态：broker_order_id -> (confirmed, retry_count, suspected_lost)
        self._receipt_status: dict[str, tuple[bool, int, bool]] = {}

        # 限频控制
        self._last_request_ts: float = 0.0

    @property
    def broker_id(self) -> str:
        """券商唯一标识"""
        return "okx"

    def _load_credentials(self) -> None:
        """加载 OKX API 密钥（三件套）。"""
        self._api_key = get_service_secret("OKX_API_KEY", "okx")
        self._secret_key = get_service_secret("OKX_SECRET_KEY", "okx")
        # Passphrase 可选（OKX 2026 新密钥体系可能不需要）
        try:
            self._passphrase = get_service_secret("OKX_PASSPHRASE", "okx")
        except Exception:
            self._passphrase = ""

        if not self._api_key or not self._secret_key:
            raise OkxBrokerError(
                "OKX API 密钥未配置：OKX_API_KEY/OKX_SECRET_KEY 必须设置",
                error_code="MISSING_CREDENTIALS",
            )

    def _sign(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """OKX V5 HMAC-SHA256 签名。

        sign = Base64(HMAC-SHA256(timestamp + method + path + body, secret_key))
        """
        message = timestamp + method.upper() + path + body
        mac = hmac.new(
            self._secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        )
        return base64.b64encode(mac.digest()).decode("utf-8")

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """发送签名请求到 OKX V5 API。

        Args:
            method: HTTP 方法（GET/POST/DELETE）
            path: API 路径（如 /api/v5/trade/order）
            params: URL 查询参数
            body: JSON 请求体

        Returns:
            API 响应 JSON

        Raises:
            OkxBrokerError: 网络异常/API 错误/签名失败
        """
        with self._lock:
            # 限频控制
            now = time.time()
            elapsed = now - self._last_request_ts
            if elapsed < self._rate_limit_sleep:
                time.sleep(self._rate_limit_sleep - elapsed)
            self._last_request_ts = time.time()

            timestamp = datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            body_str = json.dumps(body) if body else ""

            headers = {
                "OK-ACCESS-KEY": self._api_key,
                "OK-ACCESS-SIGN": self._sign(timestamp, method, path, body_str),
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": self._passphrase or "",
                "Content-Type": "application/json",
            }

            url = f"{_BASE_URL}{path}"
            try:
                if method.upper() == "GET":
                    resp = self._session.get(url, params=params, headers=headers, timeout=10)
                elif method.upper() == "POST":
                    resp = self._session.post(url, json=body, headers=headers, timeout=10)
                elif method.upper() == "DELETE":
                    resp = self._session.delete(url, params=params, headers=headers, timeout=10)
                else:
                    raise OkxBrokerError(f"不支持的 HTTP 方法: {method}", error_code="INVALID_METHOD")

                resp.raise_for_status()
                data = resp.json()

                if data.get("code") != "0":
                    raise OkxBrokerError(
                        f"OKX API 错误: {data.get('msg', 'unknown')} (code={data.get('code')})",
                        error_code=data.get("code"),
                    )
                return data

            except requests.exceptions.RequestException as e:
                raise OkxBrokerError(f"网络异常: {e}", error_code="NETWORK_ERROR") from e

    def connect(self) -> bool:
        """建立与 OKX API 的连接（验证密钥有效性）。

        Returns:
            True = 连接成功

        Raises:
            OkxBrokerError: 密钥无效或网络异常
        """
        with self._lock:
            if self._connected:
                return True

            self._load_credentials()
            self._session = requests.Session()

            # 验证密钥：查询账户余额（私有端点）
            try:
                self._request("GET", f"{_API_PATH}/account/balance")
                self._connected = True
                _logger.info("OKX 券商连接成功")
                return True
            except OkxBrokerError as e:
                self._connected = False
                raise OkxBrokerError(f"OKX 连接失败: {e}", error_code="CONNECT_FAILED") from e

    def disconnect(self) -> None:
        """断开连接"""
        with self._lock:
            if self._session is not None:
                self._session.close()
                self._session = None
            self._connected = False
            _logger.info("OKX 券商断开连接")

    def _validate_order(self, order: Order) -> None:
        """按币版规则包校验订单。

        Args:
            order: 待校验订单

        Raises:
            OkxBrokerError: 校验失败（数量/价格非法）
        """
        # 数量校验：step_size 对齐
        lot_rule = self._rule_pack.lot_rule(order.symbol)
        if order.quantity < lot_rule.min_unit:
            raise OkxBrokerError(
                f"数量低于最小申报单位: {order.quantity} < {lot_rule.min_unit}",
                error_code="INVALID_QUANTITY",
            )
        # 数量必须是 increment 的整数倍
        remainder = order.quantity % lot_rule.increment
        if remainder != 0:
            raise OkxBrokerError(
                f"数量未按步进对齐: {order.quantity} % {lot_rule.increment} = {remainder}",
                error_code="INVALID_QUANTITY_STEP",
            )

        # 价格校验：tick_size 对齐（限价单）
        if order.order_type == OrderType.LIMIT and order.limit_price is not None:
            tick = self._rule_pack.price_tick
            remainder = order.limit_price % tick
            if remainder != 0:
                raise OkxBrokerError(
                    f"价格未按最小变动单位对齐: {order.limit_price} % {tick} = {remainder}",
                    error_code="INVALID_PRICE_TICK",
                )

    def submit_order(self, order: Order) -> str:
        """发送委托到 OKX。

        Args:
            order: 订单对象（CTR-004）

        Returns:
            broker_order_id: OKX 返回的订单 ID

        Raises:
            OkxBrokerError: 校验失败/网络异常/API 错误
        """
        with self._lock:
            # 幂等拦截
            if order.idempotency_key in self._idempotency_map:
                existing_id = self._idempotency_map[order.idempotency_key]
                _logger.info("幂等拦截: %s 已存在 broker_order_id=%s", order.idempotency_key, existing_id)
                return existing_id

            # 规则包校验
            self._validate_order(order)

            # 构建 OKX 订单参数
            side_map = {OrderSide.BUY: "buy", OrderSide.SELL: "sell"}
            type_map = {OrderType.LIMIT: "limit", OrderType.MARKET: "market"}

            body = {
                "instId": order.symbol,
                "tdMode": "cash",  # 现货
                "side": side_map[order.side],
                "ordType": type_map[order.order_type],
                "sz": str(order.quantity),
            }
            if order.order_type == OrderType.LIMIT and order.limit_price is not None:
                body["px"] = str(order.limit_price)

            # 发送订单
            data = self._request("POST", f"{_API_PATH}/trade/order", body=body)

            if not data.get("data") or len(data["data"]) == 0:
                raise OkxBrokerError("OKX 返回空订单数据", error_code="EMPTY_RESPONSE")

            broker_order_id = data["data"][0].get("ordId")
            if not broker_order_id:
                raise OkxBrokerError("OKX 未返回 ordId", error_code="MISSING_ORDER_ID")

            # 登记幂等映射与缓存
            self._idempotency_map[order.idempotency_key] = broker_order_id
            order.broker_order_id = broker_order_id
            order.status = OrderStatus.SUBMITTED
            self._order_cache[broker_order_id] = order

            # 启动回执确认（异步线程）
            self._receipt_status[broker_order_id] = (False, 0, False)
            receipt_thread = threading.Thread(
                target=self._confirm_receipt,
                args=(broker_order_id,),
                daemon=True,
            )
            receipt_thread.start()

            _logger.info(
                "OKX 下单成功: %s %s %s @ %s -> %s",
                order.side,
                order.symbol,
                order.quantity,
                order.limit_price,
                broker_order_id,
            )
            return broker_order_id

    def _confirm_receipt(self, broker_order_id: str) -> None:
        """回执确认：下单后隔 1~2 秒查委托，查到写回执、查不到重试并标记疑似丢单。

        QMT 教训沿用（40_execution_broker §决策⑥）：
        下单后不能立即假设成功，需隔 1~2 秒查询委托状态确认。

        Args:
            broker_order_id: OKX 订单 ID
        """
        time.sleep(_RECEIPT_CHECK_DELAY)

        for retry in range(_RECEIPT_MAX_RETRIES):
            try:
                order = self.query_order(broker_order_id)
                if order is not None:
                    with self._lock:
                        self._receipt_status[broker_order_id] = (True, retry, False)
                    _logger.info("回执确认成功: %s (retry=%d)", broker_order_id, retry)
                    return
            except OkxBrokerError as e:
                _logger.warning("回执查询异常: %s retry=%d error=%s", broker_order_id, retry, e)

            if retry < _RECEIPT_MAX_RETRIES - 1:
                time.sleep(_RECEIPT_RETRY_INTERVAL)

        # 重试耗尽仍查不到 → 标记疑似丢单
        with self._lock:
            self._receipt_status[broker_order_id] = (False, _RECEIPT_MAX_RETRIES, True)
        _logger.error("疑似丢单: %s 回执确认失败（%d 次重试耗尽）", broker_order_id, _RECEIPT_MAX_RETRIES)

    def cancel_order(self, broker_order_id: str) -> bool:
        """撤单。

        Args:
            broker_order_id: OKX 订单 ID

        Returns:
            True = 撤单成功
        """
        with self._lock:
            if broker_order_id not in self._order_cache:
                _logger.warning("撤单失败: 订单不存在 %s", broker_order_id)
                return False

            order = self._order_cache[broker_order_id]
            body = {
                "instId": order.symbol,
                "ordId": broker_order_id,
            }

            try:
                self._request("POST", f"{_API_PATH}/trade/cancel-order", body=body)
                order.status = OrderStatus.CANCELLED
                _logger.info("OKX 撤单成功: %s", broker_order_id)
                return True
            except OkxBrokerError as e:
                _logger.error("OKX 撤单失败: %s error=%s", broker_order_id, e)
                return False

    def query_order(self, broker_order_id: str) -> Order | None:
        """查询委托状态。

        Args:
            broker_order_id: OKX 订单 ID

        Returns:
            Order 对象（含最新状态）；未找到返回 None
        """
        with self._lock:
            # 先查缓存
            if broker_order_id in self._order_cache:
                order = self._order_cache[broker_order_id]
            else:
                # 缓存未命中，从 OKX 查询
                params = {"ordId": broker_order_id}
                data = self._request("GET", f"{_API_PATH}/trade/order", params=params)

                if not data.get("data") or len(data["data"]) == 0:
                    return None

                okx_order = data["data"][0]
                order = self._map_okx_order(okx_order)
                self._order_cache[broker_order_id] = order

            # 实时刷新状态（从 OKX 查询最新）
            params = {"ordId": broker_order_id}
            try:
                data = self._request("GET", f"{_API_PATH}/trade/order", params=params)
                if data.get("data") and len(data["data"]) > 0:
                    okx_order = data["data"][0]
                    order = self._map_okx_order(okx_order, base_order=order)
                    self._order_cache[broker_order_id] = order
            except OkxBrokerError as e:
                _logger.warning("刷新订单状态失败: %s error=%s", broker_order_id, e)

            return order

    def _map_okx_order(self, okx_order: dict[str, Any], base_order: Order | None = None) -> Order:
        """将 OKX 订单响应映射为 Order 对象。

        Args:
            okx_order: OKX API 返回的订单数据
            base_order: 基础订单对象（None=新建）

        Returns:
            Order 对象
        """
        status_map = {
            "live": OrderStatus.SUBMITTED,
            "partially_filled": OrderStatus.PARTIAL,
            "filled": OrderStatus.FILLED,
            "canceled": OrderStatus.CANCELLED,
            "mmp_canceled": OrderStatus.CANCELLED,
        }

        side_map = {"buy": OrderSide.BUY, "sell": OrderSide.SELL}
        type_map = {"limit": OrderType.LIMIT, "market": OrderType.MARKET}

        if base_order is None:
            base_order = Order(
                idempotency_key=okx_order.get("clOrdId", ""),
                order_id=okx_order.get("ordId", ""),
                order_type=type_map.get(okx_order.get("ordType"), OrderType.LIMIT),
                quantity=Decimal(okx_order.get("sz", "0")),
                side=side_map.get(okx_order.get("side"), OrderSide.BUY),
                strategy_id="",
                symbol=okx_order.get("instId", ""),
                limit_price=Decimal(okx_order.get("px", "0")) if okx_order.get("px") else None,
            )

        base_order.status = status_map.get(okx_order.get("state"), OrderStatus.SUBMITTED)
        base_order.filled_quantity = Decimal(okx_order.get("accFillSz", "0"))
        if okx_order.get("avgPx"):
            base_order.avg_fill_price = Decimal(okx_order["avgPx"])

        return base_order

    def get_positions(self) -> PositionSnapshot:
        """查询当前持仓（现货余额）。

        Returns:
            PositionSnapshot 持仓快照
        """
        with self._lock:
            data = self._request("GET", f"{_API_PATH}/account/balance")

            # OKX 余额响应: data[0].details[] = [{ccy, availBal, frozenBal, ...}]
            holdings: dict[str, Decimal] = {}
            cash = Decimal("0")

            if data.get("data") and len(data["data"]) > 0:
                details = data["data"][0].get("details", [])
                for item in details:
                    ccy = item.get("ccy", "")
                    avail = Decimal(item.get("availBal", "0"))
                    frozen = Decimal(item.get("frozenBal", "0"))
                    total = avail + frozen

                    if ccy == "USDT":
                        cash = avail
                    elif total > 0:
                        # 映射为交易对格式（如 BTC -> BTC-USDT）
                        symbol = f"{ccy}-USDT"
                        holdings[symbol] = total

            return PositionSnapshot(
                portfolio_id="okx_spot",
                as_of_timestamp=datetime.now(UTC),
                idempotency_key=f"okx-pos-{int(time.time())}",
                cash=cash,
                holdings=holdings,
                market_values={},  # 需要行情数据填充
                total_market_value=Decimal("0"),
            )

    def register_fill_callback(self, callback: FillCallback) -> None:
        """注册成交回调（可选）"""
        with self._lock:
            self._fill_callbacks.append(callback)

    def get_receipt_status(self, broker_order_id: str) -> tuple[bool, int, bool]:
        """查询回执确认状态。

        Args:
            broker_order_id: OKX 订单 ID

        Returns:
            (confirmed, retry_count, suspected_lost)
        """
        with self._lock:
            return self._receipt_status.get(broker_order_id, (False, 0, False))


__all__ = ["OkxBroker", "OkxBrokerError"]
