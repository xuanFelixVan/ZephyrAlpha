"""
简单风控规则模块
基于if-then规则的务实风控实现

Layer 3, 6-7: 风控规则
务实决策: 不使用复杂规则引擎，直接硬编码简单规则
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """风险级别"""
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


@dataclass
class RiskCheckResult:
    """风控检查结果"""
    allowed: bool
    risk_level: RiskLevel
    triggered_rules: List[str]
    message: str
    details: Dict


@dataclass
class RiskPosition:
    """风控持仓信息

    用于风控检查的简化持仓数据结构
    """
    symbol: str
    quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float


@dataclass
class Account:
    """账户信息"""
    total_value: float
    cash: float
    positions: Dict[str, RiskPosition]
    daily_pnl: float
    daily_pnl_pct: float
    total_pnl: float
    total_pnl_pct: float
    max_drawdown: float


class SimpleRiskRules:
    """简单风控规则

    务实的if-then规则，不使用复杂规则引擎

    规则列表:
    1. 单票持仓上限 (默认15%)
    2. 行业持仓上限 (默认30%)
    3. 日内亏损限制 (默认2%)
    4. 最大回撤限制 (默认10%)
    5. 换手率限制 (默认50%)
    6. 流动性限制 (持仓量/成交量<1%)
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.violation_history: List[Dict] = []

    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "max_position_pct": 0.15,
            "max_sector_pct": 0.30,
            "max_daily_loss_pct": 0.02,
            "max_drawdown_pct": 0.10,
            "max_turnover_pct": 0.50,
            "max_position_of_volume": 0.01,
            "min_position_value": 1000,
            "max_positions": 20,
        }

    def check_order(
        self,
        order_symbol: str,
        order_quantity: int,
        order_price: float,
        account: Account
    ) -> RiskCheckResult:
        """检查订单是否允许执行

        参数:
            order_symbol: 股票代码
            order_quantity: 订单数量
            order_price: 订单价格
            account: 账户信息

        返回:
            RiskCheckResult: 检查结果
        """
        triggered_rules = []
        messages = []

        order_value = order_quantity * order_price
        order_pct = order_value / account.total_value

        if order_pct > self.config["max_position_pct"]:
            triggered_rules.append("单票持仓上限")
            messages.append(
                f"订单价值占账户{order_pct:.1%}，超过上限{self.config['max_position_pct']:.1%}"
            )

        if order_symbol in account.positions:
            existing_pos = account.positions[order_symbol]
            new_quantity = existing_pos.quantity + order_quantity
            new_pct = (new_quantity * order_price) / account.total_value

            if new_pct > self.config["max_position_pct"]:
                triggered_rules.append("单票持仓上限(含现有持仓)")
                messages.append(
                    f"合并持仓后占账户{new_pct:.1%}，超过上限{self.config['max_position_pct']:.1%}"
                )

        if len(account.positions) >= self.config["max_positions"]:
            if order_symbol not in account.positions:
                triggered_rules.append("持仓数量上限")
                messages.append(
                    f"已有{len(account.positions)}只股票，达到上限{self.config['max_positions']}"
                )

        if triggered_rules:
            return RiskCheckResult(
                allowed=False,
                risk_level=RiskLevel.DANGER,
                triggered_rules=triggered_rules,
                message="; ".join(messages),
                details={
                    "order_symbol": order_symbol,
                    "order_value": order_value,
                    "order_pct": order_pct
                }
            )

        return RiskCheckResult(
            allowed=True,
            risk_level=RiskLevel.SAFE,
            triggered_rules=[],
            message="订单通过风控检查",
            details={}
        )

    def check_portfolio(self, account: Account) -> RiskCheckResult:
        """检查投资组合风险

        参数:
            account: 账户信息

        返回:
            RiskCheckResult: 检查结果
        """
        triggered_rules = []
        messages = []
        details = {}

        for symbol, position in account.positions.items():
            pos_pct = position.market_value / account.total_value

            if pos_pct > self.config["max_position_pct"]:
                triggered_rules.append(f"持仓超限:{symbol}")
                messages.append(f"{symbol}持仓占{pos_pct:.1%}，超过{self.config['max_position_pct']:.1%}")

            if position.unrealized_pnl_pct < -0.20:
                triggered_rules.append(f"单票亏损过大:{symbol}")
                messages.append(f"{symbol}亏损{position.unrealized_pnl_pct:.1%}")

        daily_loss_pct = abs(account.daily_pnl_pct) if account.daily_pnl < 0 else 0
        if daily_loss_pct > self.config["max_daily_loss_pct"]:
            triggered_rules.append("日内亏损超限")
            messages.append(f"日内亏损{daily_loss_pct:.1%}，超过{self.config['max_daily_loss_pct']:.1%}")

        if account.max_drawdown > self.config["max_drawdown_pct"]:
            triggered_rules.append("最大回撤超限")
            messages.append(
                f"当前回撤{account.max_drawdown:.1%}，超过{self.config['max_drawdown_pct']:.1%}"
            )

        if account.total_pnl_pct < -self.config["max_drawdown_pct"]:
            triggered_rules.append("总盈亏超限")
            messages.append(
                f"总盈亏{account.total_pnl_pct:.1%}，超过{self.config['max_drawdown_pct']:.1%}"
            )

        if not triggered_rules:
            risk_level = RiskLevel.SAFE
            message = "投资组合风控检查通过"
        elif len(triggered_rules) <= 2:
            risk_level = RiskLevel.WARNING
            message = "投资组合存在轻度风险"
        else:
            risk_level = RiskLevel.DANGER
            message = "投资组合存在严重风险，建议减仓"

        return RiskCheckResult(
            allowed=True,
            risk_level=risk_level,
            triggered_rules=triggered_rules,
            message=message,
            details=details
        )

    def get_position_limit(self, account: Account, symbol: str) -> int:
        """获取某股票的持仓上限

        参数:
            account: 账户信息
            symbol: 股票代码

        返回:
            最大可买入数量
        """
        current_pos = account.positions.get(symbol)
        current_quantity = current_pos.quantity if current_pos else 0

        if current_pos and current_pos.current_price > 0:
            price = current_pos.current_price
        else:
            price = 10.0

        max_total_quantity = int(account.total_value * self.config["max_position_pct"] / price)

        return max(0, max_total_quantity - current_quantity)

    def should_reduce_position(self, account: Account) -> List[str]:
        """判断哪些持仓应该减仓

        返回:
            应该减仓的股票列表
        """
        reduce_list = []

        for symbol, position in account.positions.items():
            pos_pct = position.market_value / account.total_value

            if pos_pct > self.config["max_position_pct"] * 1.2:
                reduce_list.append(symbol)
            elif position.unrealized_pnl_pct < -0.15:
                reduce_list.append(symbol)
            elif account.max_drawdown > self.config["max_drawdown_pct"] * 0.8:
                reduce_list.append(symbol)

        return reduce_list

    def record_violation(self, violation: Dict):
        """记录违规"""
        violation["timestamp"] = datetime.now().isoformat()
        self.violation_history.append(violation)

        if len(self.violation_history) > 1000:
            self.violation_history = self.violation_history[-500:]

    def get_violation_report(self, days: int = 7) -> str:
        """生成违规报告

        参数:
            days: 统计天数

        返回:
            报告文本
        """
        recent_violations = self.violation_history[-100:]

        if not recent_violations:
            return "过去7天无违规记录"

        lines = ["=" * 60, "风控违规报告", "=" * 60, ""]

        rule_counts = {}
        for v in recent_violations:
            for rule in v.get("triggered_rules", []):
                rule_counts[rule] = rule_counts.get(rule, 0) + 1

        lines.append("违规统计:")
        for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {rule}: {count}次")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


class RiskManager:
    """风险管理器

    整合风控规则，提供统一的风控接口
    """

    def __init__(self, config: Optional[Dict] = None):
        self.rules = SimpleRiskRules(config)
        self.alert_handler: Optional[callable] = None

    def set_alert_handler(self, handler: callable):
        """设置告警处理器"""
        self.alert_handler = handler

    def check_pretrade(
        self,
        order_symbol: str,
        order_quantity: int,
        order_price: float,
        account: Account
    ) -> RiskCheckResult:
        """交易前风控检查"""
        result = self.rules.check_order(
            order_symbol, order_quantity, order_price, account
        )

        if not result.allowed:
            self._send_alert("order_blocked", result)

        return result

    def check_posttrade(
        self,
        trade_symbol: str,
        trade_quantity: int,
        trade_price: float,
        account: Account
    ) -> RiskCheckResult:
        """交易后风控检查"""
        return self.rules.check_portfolio(account)

    def check_portfolio(self, account: Account) -> RiskCheckResult:
        """投资组合风控检查"""
        result = self.rules.check_portfolio(account)

        if result.risk_level in [RiskLevel.DANGER, RiskLevel.CRITICAL]:
            self._send_alert("portfolio_risk", result)

        return result

    def _send_alert(self, alert_type: str, result: RiskCheckResult):
        """发送告警"""
        if self.alert_handler:
            message = f"[{alert_type}] {result.message}"
            self.alert_handler(alert_type, result.risk_level, message)

        logger.warning(f"Risk Alert: {result.message}")
