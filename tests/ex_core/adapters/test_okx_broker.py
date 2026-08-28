# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §test
# [MODULE] tests.ex_core.adapters.test_okx_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.okx_broker
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_okx_broker.py
# [A_test] module_id: MOD-L06-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-L06-001 单元测试: OkxBroker — OKX 数字货币执行适配器。

覆盖: 连接/断开/下单/撤单/查询/持仓/规则包校验/幂等/回执确认。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip(
    "zephyr.ex_core.adapters.okx_broker",
    reason="okx_broker not importable",
)

from zephyr.ex_core.adapters.okx_broker import OkxBroker, OkxBrokerError  # noqa: E402
from zephyr.ex_core.rules import CryptoRulePack  # noqa: E402
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType  # noqa: E402
from zephyr.shared.contracts.order import Order  # noqa: E402


def _make_order(
    symbol: str = "BTC-USDT",
    side: OrderSide = OrderSide.BUY,
    quantity: str = "0.001",
    order_type: OrderType = OrderType.LIMIT,
    limit_price: str | None = "50000",
    idempotency_key: str = "test-001",
) -> Order:
    return Order(
        idempotency_key=idempotency_key,
        order_id=f"ord-{idempotency_key}",
        order_type=order_type,
        quantity=Decimal(quantity),
        side=side,
        strategy_id="test_strategy",
        symbol=symbol,
        limit_price=Decimal(limit_price) if limit_price else None,
    )


class TestOkxBrokerInit:
    def test_default_init(self):
        broker = OkxBroker()
        assert broker.broker_id == "okx"
        assert broker._rule_pack is not None
        assert broker._calendar is not None

    def test_custom_rule_pack(self):
        pack = CryptoRulePack()
        broker = OkxBroker(rule_pack=pack)
        assert broker._rule_pack is pack


class TestOkxBrokerValidation:
    def test_quantity_below_min_unit_rejected(self):
        broker = OkxBroker()
        order = _make_order(quantity="0.000001")  # 低于默认 min_unit 0.00001
        with pytest.raises(OkxBrokerError, match="数量低于最小申报单位"):
            broker._validate_order(order)

    def test_quantity_step_misaligned_rejected(self):
        broker = OkxBroker()
        order = _make_order(quantity="0.000015")  # 不是 0.00001 的整数倍
        with pytest.raises(OkxBrokerError, match="数量未按步进对齐"):
            broker._validate_order(order)

    def test_price_tick_misaligned_rejected(self):
        broker = OkxBroker()
        order = _make_order(limit_price="50000.001")  # 不是 0.01 的整数倍
        with pytest.raises(OkxBrokerError, match="价格未按最小变动单位对齐"):
            broker._validate_order(order)

    def test_valid_order_passes(self):
        broker = OkxBroker()
        order = _make_order(quantity="0.001", limit_price="50000")
        broker._validate_order(order)  # 不应抛异常

    def test_market_order_skips_price_check(self):
        broker = OkxBroker()
        order = _make_order(order_type=OrderType.MARKET, limit_price=None)
        broker._validate_order(order)  # 市价单不校验价格


class TestOkxBrokerSignature:
    def test_sign_format(self):
        broker = OkxBroker()
        broker._secret_key = "test_secret"
        sign = broker._sign("2026-08-28T00:00:00.000Z", "GET", "/api/v5/trade/order")
        # Base64 编码的 HMAC-SHA256
        assert isinstance(sign, str)
        assert len(sign) == 44  # Base64 SHA256 = 44 chars
        assert sign.endswith("=")


class TestOkxBrokerIdempotency:
    @patch.object(OkxBroker, "_request")
    def test_duplicate_idempotency_key_returns_existing(self, mock_request):
        broker = OkxBroker()
        broker._connected = True
        broker._session = MagicMock()

        # 第一次下单
        mock_request.return_value = {"code": "0", "data": [{"ordId": "12345"}]}
        order = _make_order(idempotency_key="dup-001")
        first_id = broker.submit_order(order)
        assert first_id == "12345"

        # 第二次相同 idempotency_key
        second_id = broker.submit_order(order)
        assert second_id == "12345"
        # _request 只应被调用一次（第二次被幂等拦截）
        assert mock_request.call_count == 1


class TestOkxBrokerReceiptConfirmation:
    @patch.object(OkxBroker, "query_order")
    @patch("time.sleep")
    def test_receipt_confirmed_on_first_try(self, mock_sleep, mock_query):
        broker = OkxBroker()
        broker._lock = MagicMock()
        mock_query.return_value = _make_order()

        broker._confirm_receipt("12345")
        mock_query.assert_called_once_with("12345")
        # 确认状态应为 (True, 0, False)
        assert broker._receipt_status["12345"] == (True, 0, False)

    @patch.object(OkxBroker, "query_order")
    @patch("time.sleep")
    def test_receipt_suspected_lost_after_retries(self, mock_sleep, mock_query):
        broker = OkxBroker()
        broker._lock = MagicMock()
        mock_query.return_value = None  # 查不到订单

        broker._confirm_receipt("12345")
        assert mock_query.call_count == 3  # 最大重试 3 次
        # 确认状态应为 (False, 3, True) = 疑似丢单
        assert broker._receipt_status["12345"] == (False, 3, True)


class TestOkxBrokerOrderMapping:
    def test_map_okx_order_live(self):
        broker = OkxBroker()
        okx_order = {
            "ordId": "12345",
            "clOrdId": "test-001",
            "instId": "BTC-USDT",
            "side": "buy",
            "ordType": "limit",
            "sz": "0.001",
            "px": "50000",
            "state": "live",
            "accFillSz": "0",
        }
        order = broker._map_okx_order(okx_order)
        assert order.symbol == "BTC-USDT"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.LIMIT
        assert order.quantity == Decimal("0.001")
        assert order.limit_price == Decimal("50000")

    def test_map_okx_order_filled(self):
        broker = OkxBroker()
        okx_order = {
            "ordId": "12345",
            "instId": "BTC-USDT",
            "side": "sell",
            "ordType": "market",
            "sz": "0.001",
            "state": "filled",
            "accFillSz": "0.001",
            "avgPx": "50100",
        }
        order = broker._map_okx_order(okx_order)
        assert order.status.value == "FILLED"
        assert order.filled_quantity == Decimal("0.001")
        assert order.avg_fill_price == Decimal("50100")


class TestOkxBrokerError:
    def test_error_code(self):
        err = OkxBrokerError("test error", error_code="TEST_001")
        assert str(err) == "test error"
        assert err.error_code == "TEST_001"

    def test_missing_credentials(self):
        broker = OkxBroker()
        with patch("zephyr.ex_core.adapters.okx_broker.get_service_secret") as mock_secret:
            mock_secret.return_value = None
            with pytest.raises(OkxBrokerError, match="OKX API 密钥未配置"):
                broker._load_credentials()
