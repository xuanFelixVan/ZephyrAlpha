"""
风险管理器单元测试
"""
import pytest
from datetime import datetime

from src.modules.risk_manager import (
    RiskManager,
    SimpleRiskRules,
    RiskCheckResult,
    Account,
    RiskPosition,
    RiskLevel,
)


def create_account(
    total_value: float = 1000000.0,
    cash: float = 500000.0,
    positions: dict = None
) -> Account:
    """创建测试账户"""
    if positions is None:
        positions = {
            "000001": RiskPosition(
                symbol="000001",
                quantity=10000,
                avg_cost=10.0,
                current_price=10.5,
                market_value=105000.0,
                unrealized_pnl=5000.0,
                unrealized_pnl_pct=0.05
            )
        }

    return Account(
        total_value=total_value,
        cash=cash,
        positions=positions,
        daily_pnl=1000.0,
        daily_pnl_pct=0.001,
        total_pnl=10000.0,
        total_pnl_pct=0.01,
        max_drawdown=0.05
    )


class TestRiskLevel:
    """测试风险级别枚举"""

    def test_risk_levels_exist(self):
        """测试风险级别存在"""
        assert RiskLevel.SAFE.value == "safe"
        assert RiskLevel.WARNING.value == "warning"
        assert RiskLevel.DANGER.value == "danger"
        assert RiskLevel.CRITICAL.value == "critical"


class TestSimpleRiskRulesInit:
    """测试 SimpleRiskRules 初始化"""

    def test_default_config(self):
        """测试默认配置"""
        rules = SimpleRiskRules()

        assert rules.config["max_position_pct"] == 0.15
        assert rules.config["max_sector_pct"] == 0.30
        assert rules.config["max_daily_loss_pct"] == 0.02
        assert rules.config["max_drawdown_pct"] == 0.10

    def test_custom_config(self):
        """测试自定义配置"""
        config = {
            "max_position_pct": 0.20,
            "max_sector_pct": 0.40,
            "max_daily_loss_pct": 0.03,
            "max_drawdown_pct": 0.15,
        }

        rules = SimpleRiskRules(config)

        assert rules.config["max_position_pct"] == 0.20
        assert rules.config["max_sector_pct"] == 0.40


class TestCheckOrder:
    """测试订单检查"""

    def test_order_within_limits(self):
        """测试正常订单"""
        rules = SimpleRiskRules()
        account = create_account()

        result = rules.check_order(
            order_symbol="000002",
            order_quantity=1000,
            order_price=9.0,
            account=account
        )

        assert result.allowed is True
        assert result.risk_level == RiskLevel.SAFE
        assert len(result.triggered_rules) == 0

    def test_order_exceeds_position_limit(self):
        """测试超过单票持仓上限"""
        rules = SimpleRiskRules()
        account = create_account()

        result = rules.check_order(
            order_symbol="000002",
            order_quantity=200000,
            order_price=5.0,
            account=account
        )

        assert result.allowed is False
        assert result.risk_level == RiskLevel.DANGER
        assert "单票持仓上限" in result.triggered_rules[0]

    def test_order_for_existing_position(self):
        """测试加仓订单"""
        rules = SimpleRiskRules()
        account = create_account()

        result = rules.check_order(
            order_symbol="000001",
            order_quantity=100000,
            order_price=10.5,
            account=account
        )

        assert result.allowed is False
        assert "单票持仓上限(含现有持仓)" in result.triggered_rules[0]

    def test_max_positions_reached(self):
        """测试达到最大持仓数"""
        rules = SimpleRiskRules(config={"max_positions": 1})
        account = create_account()

        result = rules.check_order(
            order_symbol="000002",
            order_quantity=1000,
            order_price=9.0,
            account=account
        )

        assert result.allowed is False
        assert "持仓数量上限" in result.triggered_rules[0]


class TestCheckPortfolio:
    """测试投资组合检查"""

    def test_portfolio_within_limits(self):
        """测试正常投资组合"""
        rules = SimpleRiskRules()
        account = create_account()

        result = rules.check_portfolio(account)

        assert result.allowed is True
        assert result.risk_level == RiskLevel.SAFE
        assert len(result.triggered_rules) == 0

    def test_portfolio_with_large_loss(self):
        """测试大亏损投资组合"""
        rules = SimpleRiskRules()
        account = create_account(
            positions={
                "000001": RiskPosition(
                    symbol="000001",
                    quantity=10000,
                    avg_cost=10.0,
                    current_price=7.5,
                    market_value=75000.0,
                    unrealized_pnl=-25000.0,
                    unrealized_pnl_pct=-0.25
                )
            }
        )

        result = rules.check_portfolio(account)

        assert "单票亏损过大" in result.triggered_rules[0]

    def test_portfolio_exceeds_daily_loss(self):
        """测试超过日内亏损限制"""
        rules = SimpleRiskRules()
        account = create_account(
            total_value=1000000.0,
            cash=500000.0,
            daily_pnl=-30000.0,
            daily_pnl_pct=-0.03
        )

        result = rules.check_portfolio(account)

        assert "日内亏损超限" in result.triggered_rules[0]

    def test_portfolio_exceeds_max_drawdown(self):
        """测试超过最大回撤"""
        rules = SimpleRiskRules()
        account = create_account(max_drawdown=0.15)

        result = rules.check_portfolio(account)

        assert "最大回撤超限" in result.triggered_rules[0]


class TestGetPositionLimit:
    """测试获取持仓上限"""

    def test_no_existing_position(self):
        """测试无现有持仓"""
        rules = SimpleRiskRules()
        account = create_account()

        limit = rules.get_position_limit(account, "000002")

        assert limit > 0

    def test_with_existing_position(self):
        """测试有现有持仓"""
        rules = SimpleRiskRules()
        account = create_account()

        limit = rules.get_position_limit(account, "000001")

        assert limit >= 0

    def test_zero_price_handling(self):
        """测试零价格处理"""
        rules = SimpleRiskRules()
        account = create_account(
            positions={
                "000001": RiskPosition(
                    symbol="000001",
                    quantity=10000,
                    avg_cost=10.0,
                    current_price=0.0,
                    market_value=0.0,
                    unrealized_pnl=-100000.0,
                    unrealized_pnl_pct=-1.0
                )
            }
        )

        limit = rules.get_position_limit(account, "000001")

        assert limit >= 0


class TestShouldReducePosition:
    """测试是否应该减仓"""

    def test_no_reduce_needed(self):
        """测试不需要减仓"""
        rules = SimpleRiskRules()
        account = create_account()

        reduce_list = rules.should_reduce_position(account)

        assert len(reduce_list) == 0

    def test_reduce_large_position(self):
        """测试超比例持仓需要减仓"""
        rules = SimpleRiskRules()
        account = create_account(
            positions={
                "000001": RiskPosition(
                    symbol="000001",
                    quantity=200000,
                    avg_cost=10.0,
                    current_price=10.5,
                    market_value=2100000.0,
                    unrealized_pnl=100000.0,
                    unrealized_pnl_pct=0.05
                )
            },
            total_value=1500000.0
        )

        reduce_list = rules.should_reduce_position(account)

        assert "000001" in reduce_list

    def test_reduce_large_loss(self):
        """测试大亏损需要减仓"""
        rules = SimpleRiskRules()
        account = create_account(
            positions={
                "000001": RiskPosition(
                    symbol="000001",
                    quantity=10000,
                    avg_cost=10.0,
                    current_price=8.0,
                    market_value=80000.0,
                    unrealized_pnl=-20000.0,
                    unrealized_pnl_pct=-0.20
                )
            }
        )

        reduce_list = rules.should_reduce_position(account)

        assert "000001" in reduce_list


class TestViolationRecording:
    """测试违规记录"""

    def test_record_violation(self):
        """测试记录违规"""
        rules = SimpleRiskRules()

        rules.record_violation({
            "rule": "单票持仓上限",
            "symbol": "000001",
            "details": {}
        })

        assert len(rules.violation_history) == 1

    def test_violation_history_limit(self):
        """测试违规历史限制"""
        rules = SimpleRiskRules()

        for i in range(1005):
            rules.record_violation({"rule": f"rule_{i}"})

        assert len(rules.violation_history) <= 1000

    def test_get_violation_report(self):
        """测试获取违规报告"""
        rules = SimpleRiskRules()

        rules.record_violation({"rule": "单票持仓上限", "triggered_rules": ["规则1"]})
        rules.record_violation({"rule": "日内亏损超限", "triggered_rules": ["规则2"]})
        rules.record_violation({"rule": "单票持仓上限", "triggered_rules": ["规则1"]})

        report = rules.get_violation_report()

        assert "风控违规报告" in report
        assert "单票持仓上限: 2次" in report


class TestRiskManager:
    """测试 RiskManager"""

    def test_risk_manager_init(self):
        """测试 RiskManager 初始化"""
        manager = RiskManager()

        assert manager.rules is not None
        assert manager.alert_handler is None

    def test_set_alert_handler(self):
        """测试设置告警处理器"""
        manager = RiskManager()

        called = []

        def handler(alert_type, level, message):
            called.append((alert_type, level, message))

        manager.set_alert_handler(handler)
        assert manager.alert_handler is not None

    def test_check_pretrade_allows_valid_order(self):
        """测试交易前检查允许正常订单"""
        manager = RiskManager()
        account = create_account()

        result = manager.check_pretrade(
            order_symbol="000002",
            order_quantity=1000,
            order_price=9.0,
            account=account
        )

        assert result.allowed is True

    def test_check_pretrade_blocks_invalid_order(self):
        """测试交易前检查阻止异常订单"""
        manager = RiskManager()
        account = create_account()

        result = manager.check_pretrade(
            order_symbol="000002",
            order_quantity=200000,
            order_price=5.0,
            account=account
        )

        assert result.allowed is False

    def test_check_portfolio_with_alert(self):
        """测试投资组合检查触发告警"""
        manager = RiskManager()
        account = create_account(max_drawdown=0.15)

        alert_called = []

        def handler(alert_type, level, message):
            alert_called.append((alert_type, level, message))

        manager.set_alert_handler(handler)

        manager.check_portfolio(account)

        assert len(alert_called) == 1
        assert alert_called[0][0] == "portfolio_risk"
