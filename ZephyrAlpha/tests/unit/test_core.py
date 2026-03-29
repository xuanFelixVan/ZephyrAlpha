"""
核心基础类单元测试
"""
import pytest
from datetime import datetime

from src.core.base import Result, Signal, Order, Position


class TestResult:
    """测试 Result 数据类"""

    def test_success_result(self):
        """测试成功结果"""
        result = Result(success=True, data={"price": 100.0})

        assert result.success is True
        assert result.data == {"price": 100.0}
        assert result.error is None

    def test_failure_result(self):
        """测试失败结果"""
        result = Result(success=False, error="Data not found")

        assert result.success is False
        assert result.error == "Data not found"

    def test_is_success_property(self):
        """测试 is_success 属性"""
        result = Result(success=True)
        assert result.is_success is True

    def test_is_failure_property(self):
        """测试 is_failure 属性"""
        result = Result(success=False)
        assert result.is_failure is True

    def test_metadata_default(self):
        """测试默认元数据"""
        result = Result(success=True)
        assert result.metadata == {}

    def test_metadata_custom(self):
        """测试自定义元数据"""
        result = Result(success=True, metadata={"key": "value"})
        assert result.metadata == {"key": "value"}

    def test_metadata_none_handling(self):
        """测试 None 元数据"""
        result = Result(success=True, metadata=None)
        assert result.metadata == {}


class TestSignal:
    """测试 Signal 数据类"""

    def test_valid_signal(self):
        """测试有效信号"""
        signal = Signal(
            signal_id="S001",
            strategy_id="STRAT_001",
            stock_code="000001",
            direction="long",
            strength=0.8,
            entry_price=10.5,
            timestamp=datetime.now()
        )

        assert signal.signal_id == "S001"
        assert signal.direction == "long"
        assert signal.strength == 0.8

    def test_invalid_direction(self):
        """测试无效方向"""
        with pytest.raises(ValueError) as exc_info:
            Signal(
                signal_id="S001",
                strategy_id="STRAT_001",
                stock_code="000001",
                direction="invalid",
                strength=0.8,
                entry_price=10.5,
                timestamp=datetime.now()
            )

        assert "direction must be 'long' or 'short'" in str(exc_info.value)

    def test_invalid_strength_low(self):
        """测试强度过低"""
        with pytest.raises(ValueError) as exc_info:
            Signal(
                signal_id="S001",
                strategy_id="STRAT_001",
                stock_code="000001",
                direction="long",
                strength=-0.1,
                entry_price=10.5,
                timestamp=datetime.now()
            )

        assert "strength must be between 0.0 and 1.0" in str(exc_info.value)

    def test_invalid_strength_high(self):
        """测试强度过高"""
        with pytest.raises(ValueError) as exc_info:
            Signal(
                signal_id="S001",
                strategy_id="STRAT_001",
                stock_code="000001",
                direction="long",
                strength=1.5,
                entry_price=10.5,
                timestamp=datetime.now()
            )

        assert "strength must be between 0.0 and 1.0" in str(exc_info.value)

    def test_short_direction(self):
        """测试做空方向"""
        signal = Signal(
            signal_id="S001",
            strategy_id="STRAT_001",
            stock_code="000001",
            direction="short",
            strength=0.7,
            entry_price=10.5,
            timestamp=datetime.now()
        )

        assert signal.direction == "short"


class TestOrder:
    """测试 Order 数据类"""

    def test_valid_order(self):
        """测试有效订单"""
        order = Order(
            order_id="O001",
            signal_id="S001",
            stock_code="000001",
            direction="buy",
            order_type="limit",
            price=10.5,
            quantity=100
        )

        assert order.order_id == "O001"
        assert order.direction == "buy"
        assert order.quantity == 100

    def test_invalid_direction(self):
        """测试无效方向"""
        with pytest.raises(ValueError) as exc_info:
            Order(
                order_id="O001",
                signal_id="S001",
                stock_code="000001",
                direction="invalid",
                order_type="limit",
                price=10.5,
                quantity=100
            )

        assert "direction must be 'buy' or 'sell'" in str(exc_info.value)

    def test_invalid_order_type(self):
        """测试无效订单类型"""
        with pytest.raises(ValueError) as exc_info:
            Order(
                order_id="O001",
                signal_id="S001",
                stock_code="000001",
                direction="buy",
                order_type="stop",
                price=10.5,
                quantity=100
            )

        assert "order_type must be 'market' or 'limit'" in str(exc_info.value)

    def test_invalid_quantity(self):
        """测试无效数量"""
        with pytest.raises(ValueError) as exc_info:
            Order(
                order_id="O001",
                signal_id="S001",
                stock_code="000001",
                direction="buy",
                order_type="limit",
                price=10.5,
                quantity=0
            )

        assert "quantity must be positive" in str(exc_info.value)

    def test_invalid_price(self):
        """测试无效价格"""
        with pytest.raises(ValueError) as exc_info:
            Order(
                order_id="O001",
                signal_id="S001",
                stock_code="000001",
                direction="buy",
                order_type="limit",
                price=-10.5,
                quantity=100
            )

        assert "price must be positive" in str(exc_info.value)

    def test_default_timestamp(self):
        """测试默认时间戳"""
        order = Order(
            order_id="O001",
            signal_id="S001",
            stock_code="000001",
            direction="buy",
            order_type="limit",
            price=10.5,
            quantity=100
        )

        assert order.timestamp is not None

    def test_default_status(self):
        """测试默认状态"""
        order = Order(
            order_id="O001",
            signal_id="S001",
            stock_code="000001",
            direction="buy",
            order_type="limit",
            price=10.5,
            quantity=100
        )

        assert order.status == "pending"


class TestPosition:
    """测试 Position 数据类"""

    def test_valid_position(self):
        """测试有效持仓"""
        position = Position(
            stock_code="000001",
            quantity=1000,
            avg_cost=10.0,
            current_price=10.5
        )

        assert position.stock_code == "000001"
        assert position.quantity == 1000

    def test_unrealized_pnl_calculation(self):
        """测试浮动盈亏计算"""
        position = Position(
            stock_code="000001",
            quantity=1000,
            avg_cost=10.0,
            current_price=10.5
        )

        assert position.unrealized_pnl == 500.0

    def test_market_value_property(self):
        """测试市值属性"""
        position = Position(
            stock_code="000001",
            quantity=1000,
            avg_cost=10.0,
            current_price=10.5
        )

        assert position.market_value == 10500.0

    def test_cost_value_property(self):
        """测试成本属性"""
        position = Position(
            stock_code="000001",
            quantity=1000,
            avg_cost=10.0,
            current_price=10.5
        )

        assert position.cost_value == 10000.0

    def test_pnl_pct_property(self):
        """测试盈亏比例属性"""
        position = Position(
            stock_code="000001",
            quantity=1000,
            avg_cost=10.0,
            current_price=10.5
        )

        assert abs(position.pnl_pct - 0.05) < 0.001

    def test_pnl_pct_zero_cost(self):
        """测试零成本盈亏比例"""
        position = Position(
            stock_code="000001",
            quantity=1000,
            avg_cost=0.0,
            current_price=10.5
        )

        assert position.pnl_pct == 0.0

    def test_negative_pnl(self):
        """测试亏损情况"""
        position = Position(
            stock_code="000001",
            quantity=1000,
            avg_cost=10.5,
            current_price=10.0
        )

        assert position.unrealized_pnl == -500.0
        assert position.pnl_pct < 0
