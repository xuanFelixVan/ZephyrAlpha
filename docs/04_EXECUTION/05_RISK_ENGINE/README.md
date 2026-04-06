---
module_id: EXECUTION_RISK_ENGINE_001
version: 2.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-04
owner: 首席文档架构�?
standard_type: 专业量化机构交易执行标准
applicable_scope: 交易执行与监�?
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行�?
related_documents:
  - 03_TRADING_TACTICS/09_RISK_RULES/BLUEPRINT.md (风控规则体系框架)
  - 03_TRADING_TACTICS/09_RISK_RULES/RISK_REPORT.md (风险报告生成�?
  - 01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md (实时风险监控仪表�?
responsibility:
  - 风险预算 (Layer 3)
  - 市场状态识别 (Layer 4)
---

# 风控规则引擎

> **Layer 6: 风险监控** - 风险规则引擎、实时检查、告警触�?
>
> **版本**: v2.0 (合并�?
> **更新**: 2026-04-04
> **说明**: 本文档整合了�?`03_TRADING_TACTICS/09_RISK_RULES/RISK_RULE_ENGINE.md` 的内�?

---

## 设计原则

| 原则 | 说明 |
|------|------|
| **规则即配�?* | 风控规则以YAML配置，不写死代码 |
| **三层防御** | 事前检�?�?事中监控 �?事后分析 |
| **快速失�?* | 风控触发时立即行动，不等待人�?|
| **完整审计** | 所有风控事件完整记�?|

---

## 文档层级关系

```
┌─────────────────────────────────────────────────────────────�?
�? 框架�? 01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md  �?
�? (定义实时风险监控的整体架构和设计原则)                        �?
└─────────────────────────────────────────────────────────────�?
                              �?
┌─────────────────────────────────────────────────────────────�?
�? 战术�? 03_TRADING_TACTICS/09_RISK_RULES/BLUEPRINT.md       �?
�? (定义风控规则体系和三层防御架�?                             �?
└─────────────────────────────────────────────────────────────�?
                              �?
┌─────────────────────────────────────────────────────────────�?
�? 执行�? 本文�?(04_EXECUTION/05_RISK_ENGINE/README.md)      �?
�? (实现风控规则引擎核心功能)                                   �?
└─────────────────────────────────────────────────────────────�?
```

---

## 1. 系统架构

```
风控规则引擎
├── 规则定义�?(Rule Definition)
�?  ├── 规则DSL语法
�?  ├── 规则模板�?
�?  └── 规则版本管理
├── 规则执行�?(Rule Engine)
�?  ├── 规则解析�?
�?  ├── 规则评估�?
�?  └── 规则组合�?
├── 实时检查层 (Real-time Check)
�?  ├── 持仓检�?
�?  ├── 交易检�?
�?  └── 市场检�?
├── 告警触发�?(Alert Trigger)
�?  ├── 告警分级
�?  ├── 通知渠道
�?  └── 告警抑制
└── 风控报告生成
    ├── 风险摘要
    ├── 违规记录
    └── 趋势分析
```

---

## 2. 规则定义

### 2.1 规则数据结构

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import operator


class RuleType(Enum):
    """规则类型"""
    POSITION_LIMIT = "position_limit"        # 持仓限制
    SECTOR_LIMIT = "sector_limit"            # 行业限制
    SINGLE_STOCK_LIMIT = "single_stock_limit" # 单票限制
    TURNOVER_LIMIT = "turnover_limit"       # 换手限制
    DRAWDAWN_LIMIT = "drawdown_limit"       # 回撤限制
    LOSS_LIMIT = "loss_limit"               # 亏损限制
    LIQUIDITY_LIMIT = "liquidity_limit"     # 流动性限�?
    VOLATILITY_LIMIT = "volatility_limit"   # 波动率限�?
    CORRELATION_LIMIT = "correlation_limit"  # 相关性限�?
    CUSTOM = "custom"                       # 自定义规�?


class RuleSeverity(Enum):
    """规则严重级别"""
    INFO = "info"           # 信息
    WARNING = "warning"     # 警告
    ERROR = "error"         # 错误
    CRITICAL = "critical"   # 严重


class RuleStatus(Enum):
    """规则状�?""
    ENABLED = "enabled"
    DISABLED = "disabled"
    SUSPENDED = "suspended"


@dataclass
class RuleCondition:
    """规则条件"""
    field: str                    # 字段�?
    operator: str                # 操作�? >, <, >=, <=, ==, !=, in, not in
    value: Any                   # 比较�?

    def evaluate(self, context: Dict) -> bool:
        """评估条件"""
        field_value = self._get_field_value(context, self.field)

        ops = {
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
            "in": lambda a, b: a in b,
            "not in": lambda a, b: a not in b
        }

        op_func = ops.get(self.operator)
        if op_func is None:
            return False

        try:
            return op_func(field_value, self.value)
        except:
            return False

    def _get_field_value(self, context: Dict, field: str) -> Any:
        """获取字段�?""
        parts = field.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None

        return value


@dataclass
class Rule:
    """风控规则"""
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    severity: RuleSeverity
    conditions: List[RuleCondition]
    actions: List[str]           # 触发动作: ['log', 'warn', 'block', 'close']
    parameters: Dict[str, Any]    # 规则参数
    status: RuleStatus = RuleStatus.ENABLED
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def evaluate(self, context: Dict) -> bool:
        """评估规则是否触发"""
        if self.status != RuleStatus.ENABLED:
            return False

        return all(condition.evaluate(context) for condition in self.conditions)


@dataclass
class RuleViolation:
    """规则违规记录"""
    violation_id: str
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    context: Dict
    triggered_at: datetime
    action_taken: List[str]
    resolved: bool = False
    resolved_at: Optional[datetime] = None
```

### 2.2 预定义规则模�?

```python
class RuleTemplates:
    """风控规则模板"""

    @staticmethod
    def single_stock_position_limit(
        max_position_pct: float = 0.15
    ) -> Rule:
        """单票持仓上限

        参数:
            max_position_pct: 最大持仓比�?(默认15%)
        """
        return Rule(
            rule_id="R001",
            name="单票持仓上限",
            description=f"单一股票持仓不得超过账户总资产的{max_position_pct:.0%}",
            rule_type=RuleType.SINGLE_STOCK_LIMIT,
            severity=RuleSeverity.ERROR,
            conditions=[
                RuleCondition("position.stock_pct", ">", max_position_pct)
            ],
            actions=["block", "warn"],
            parameters={"max_pct": max_position_pct}
        )

    @staticmethod
    def sector_position_limit(
        max_sector_pct: float = 0.30
    ) -> Rule:
        """行业持仓上限"""
        return Rule(
            rule_id="R002",
            name="行业持仓上限",
            description=f"单一行业持仓不得超过账户总资产的{max_sector_pct:.0%}",
            rule_type=RuleType.SECTOR_LIMIT,
            severity=RuleSeverity.WARNING,
            conditions=[
                RuleCondition("position.sector_pct", ">", max_sector_pct)
            ],
            actions=["warn"],
            parameters={"max_pct": max_sector_pct}
        )

    @staticmethod
    def daily_loss_limit(max_loss_pct: float = 0.02) -> Rule:
        """日内亏损限制"""
        return Rule(
            rule_id="R003",
            name="日内亏损限制",
            description=f"日内亏损不得超过账户总资产的{max_loss_pct:.0%}",
            rule_type=RuleType.LOSS_LIMIT,
            severity=RuleSeverity.CRITICAL,
            conditions=[
                RuleCondition("daily_pnl.pct", "<", -max_loss_pct)
            ],
            actions=["block", "close_all", "alert"],
            parameters={"max_loss_pct": max_loss_pct}
        )

    @staticmethod
    def max_drawdown_limit(max_dd_pct: float = 0.10) -> Rule:
        """最大回撤限�?""
        return Rule(
            rule_id="R004",
            name="最大回撤限�?,
            description=f"账户最大回撤不得超过{max_dd_pct:.0%}",
            rule_type=RuleType.DRAWDAWN_LIMIT,
            severity=RuleSeverity.CRITICAL,
            conditions=[
                RuleCondition("portfolio.max_drawdown", ">", max_dd_pct)
            ],
            actions=["block", "reduce_position", "alert"],
            parameters={"max_dd_pct": max_dd_pct}
        )

    @staticmethod
    def turnover_limit(
        max_turnover_pct: float = 0.50,
        window: int = 1
    ) -> Rule:
        """换手率限�?""
        return Rule(
            rule_id="R005",
            name="换手率限�?,
            description=f"{window}日内累计换手率不得超过{max_turnover_pct:.0%}",
            rule_type=RuleType.TURNOVER_LIMIT,
            severity=RuleSeverity.WARNING,
            conditions=[
                RuleCondition(f"turnover.cumsum_{window}d", ">", max_turnover_pct)
            ],
            actions=["warn", "throttle"],
            parameters={
                "max_turnover_pct": max_turnover_pct,
                "window": window
            }
        )

    @staticmethod
    def liquidity_limit(
        min_daily_volume: float = 1000000,
        max_position_pct_of_volume: float = 0.01
    ) -> Rule:
        """流动性限�?""
        return Rule(
            rule_id="R006",
            name="流动性限�?,
            description="持仓量不得超过当日成交量�?%",
            rule_type=RuleType.LIQUIDITY_LIMIT,
            severity=RuleSeverity.WARNING,
            conditions=[
                RuleCondition(
                    "position.quantity / market.volume",
                    ">",
                    max_position_pct_of_volume
                )
            ],
            actions=["warn", "throttle"],
            parameters={
                "min_volume": min_daily_volume,
                "max_pct_of_volume": max_position_pct_of_volume
            }
        )

    @staticmethod
    def price_volatility_limit(
        max_volatility: float = 0.05,
        window: int = 20
    ) -> Rule:
        """价格波动率限�?""
        return Rule(
            rule_id="R007",
            name="波动率限�?,
            description=f"持仓股票{window}日波动率不得超过{max_volatility:.0%}",
            rule_type=RuleType.VOLATILITY_LIMIT,
            severity=RuleSeverity.WARNING,
            conditions=[
                RuleCondition(f"stock.volatility_{window}d", ">", max_volatility)
            ],
            actions=["warn"],
            parameters={
                "max_volatility": max_volatility,
                "window": window
            }
        )
```

---

## 3. 规则引擎核心

### 3.1 风控执行�?

```python
class RiskControlEngine:
    """风控规则引擎"""

    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self.violations: List[RuleViolation] = []
        self.alert_handler: Optional[Callable] = None
        self.logger = logging.getLogger(__name__)

    def register_rule(self, rule: Rule):
        """注册风控规则"""
        self.rules[rule.rule_id] = rule
        self.logger.info(f"Registered rule: {rule.rule_id} - {rule.name}")

    def register_rules(self, rules: List[Rule]):
        """批量注册规则"""
        for rule in rules:
            self.register_rule(rule)

    def set_alert_handler(self, handler: Callable):
        """设置告警处理�?""
        self.alert_handler = handler

    def check_pretrade(self, order: Order, context: Dict) -> CheckResult:
        """交易前检�?

        参数:
            order: 订单
            context: 上下文（持仓、市场等�?

        返回:
            检查结�?
        """
        context["order"] = order.to_dict()
        context["action"] = "pretrade"

        triggered_rules = self._evaluate_rules(context)

        if triggered_rules:
            return CheckResult(
                allowed=False,
                triggered_rules=triggered_rules,
                blocked=True,
                message=self._format_block_message(triggered_rules)
            )

        return CheckResult(allowed=True, triggered_rules=[], blocked=False)

    def check_posttrade(self, trade: Trade, context: Dict) -> CheckResult:
        """交易后检�?""
        context["trade"] = trade.to_dict()
        context["action"] = "posttrade"

        triggered_rules = self._evaluate_rules(context)

        return CheckResult(
            allowed=True,
            triggered_rules=triggered_rules,
            blocked=False
        )

    def check_portfolio(self, portfolio: Portfolio, context: Dict) -> CheckResult:
        """投资组合检�?""
        context["portfolio"] = portfolio.to_dict()
        context["position"] = portfolio.get_position_summary()
        context["action"] = "portfolio_check"

        triggered_rules = self._evaluate_rules(context)

        if any(r.severity == RuleSeverity.CRITICAL for r in triggered_rules):
            return CheckResult(
                allowed=False,
                triggered_rules=triggered_rules,
                blocked=True,
                message="Portfolio risk limits breached"
            )

        return CheckResult(
            allowed=True,
            triggered_rules=triggered_rules,
            blocked=False
        )

    def check_market(self, market_data: Dict, context: Dict) -> CheckResult:
        """市场状态检�?""
        context["market"] = market_data
        context["action"] = "market_check"

        triggered_rules = self._evaluate_rules(context)

        return CheckResult(
            allowed=True,
            triggered_rules=triggered_rules,
            blocked=False
        )

    def _evaluate_rules(self, context: Dict) -> List[Rule]:
        """评估所有规�?""
        triggered = []

        for rule in self.rules.values():
            if rule.status != RuleStatus.ENABLED:
                continue

            try:
                if rule.evaluate(context):
                    violation = self._record_violation(rule, context)
                    self._execute_actions(rule, violation, context)
                    triggered.append(rule)

            except Exception as e:
                self.logger.error(f"Rule {rule.rule_id} evaluation error: {e}")

        return triggered

    def _record_violation(self, rule: Rule, context: Dict) -> RuleViolation:
        """记录违规"""
        violation = RuleViolation(
            violation_id=f"V{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            rule_id=rule.rule_id,
            rule_name=rule.name,
            severity=rule.severity,
            context=context.copy(),
            triggered_at=datetime.now(),
            action_taken=[]
        )

        self.violations.append(violation)
        self.logger.warning(f"Rule violation: {rule.name} ({rule.severity.value})")

        return violation

    def _execute_actions(
        self,
        rule: Rule,
        violation: RuleViolation,
        context: Dict
    ):
        """执行规则动作"""
        for action in rule.actions:
            if action == "log":
                violation.action_taken.append("log")
                self.logger.info(f"Logged violation: {violation.violation_id}")

            elif action == "warn":
                violation.action_taken.append("warn")
                self._send_warning(rule, violation, context)

            elif action == "block":
                violation.action_taken.append("block")
                self.logger.error(f"Blocked by rule: {rule.name}")

            elif action == "alert":
                violation.action_taken.append("alert")
                self._send_alert(rule, violation, context)

            elif action == "close":
                violation.action_taken.append("close")
                self._execute_closing(rule, violation, context)

    def _send_warning(self, rule: Rule, violation: RuleViolation, context: Dict):
        """发送警�?""
        message = f"Risk Warning: {rule.name} triggered"

        if self.alert_handler:
            self.alert_handler("warning", message)

    def _send_alert(self, rule: Rule, violation: RuleViolation, context: Dict):
        """发送告�?""
        message = f"Risk Alert [{rule.severity.value.upper()}]: {rule.name}"

        if self.alert_handler:
            self.alert_handler("alert", message)

    def _execute_closing(self, rule: Rule, violation: RuleViolation, context: Dict):
        """执行平仓"""
        pass

    def _format_block_message(self, triggered_rules: List[Rule]) -> str:
        """格式化阻止消�?""
        rule_names = [r.name for r in triggered_rules]
        return f"Blocked by risk rules: {', '.join(rule_names)}"


@dataclass
class CheckResult:
    """检查结�?""
    allowed: bool
    triggered_rules: List[Rule]
    blocked: bool
    message: str = ""
```

---

## 4. 实时监控

### 4.1 风控监控�?

```python
class RiskMonitor:
    """实时风险监控�?""

    def __init__(self, engine: RiskControlEngine):
        self.engine = engine
        self.portfolio_state: Dict = {}
        self.market_state: Dict = {}
        self.daily_stats: Dict = {}
        self.alerts: List[Alert] = []

    def update_portfolio(self, portfolio: Portfolio):
        """更新组合状�?""
        self.portfolio_state = {
            "total_value": portfolio.total_value,
            "positions": portfolio.positions,
            "cash": portfolio.cash,
            "daily_pnl": portfolio.daily_pnl,
            "total_pnl": portfolio.total_pnl,
            "max_drawdown": portfolio.max_drawdown,
            "volatility": portfolio.volatility,
            "beta": portfolio.beta,
            "timestamp": datetime.now()
        }

        context = {
            "portfolio": portfolio.to_dict(),
            "position": portfolio.get_position_summary()
        }

        result = self.engine.check_portfolio(portfolio, context)

        if result.triggered_rules:
            self._process_triggered_rules(result.triggered_rules, context)

    def update_market(self, market_data: Dict):
        """更新市场状�?""
        self.market_state.update(market_data)

        context = {"market": self.market_state}

        result = self.engine.check_market(market_data, context)

        if result.triggered_rules:
            self._process_triggered_rules(result.triggered_rules, context)

    def update_daily_stats(self, stats: Dict):
        """更新每日统计"""
        self.daily_stats.update(stats)

    def _process_triggered_rules(
        self,
        triggered_rules: List[Rule],
        context: Dict
    ):
        """处理触发的规�?""
        for rule in triggered_rules:
            if rule.severity == RuleSeverity.CRITICAL:
                alert = Alert(
                    alert_id=f"A{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    severity=AlertSeverity.CRITICAL,
                    title=f"Critical Risk: {rule.name}",
                    message=rule.description,
                    triggered_at=datetime.now(),
                    rules_triggered=[rule.rule_id]
                )

                self.alerts.append(alert)
                self._handle_critical_alert(alert)

    def _handle_critical_alert(self, alert: Alert):
        """处理严重告警"""
        self.logger.critical(f"CRITICAL ALERT: {alert.title}")

        if self.engine.alert_handler:
            self.engine.alert_handler("critical", alert.message)

    def get_risk_summary(self) -> Dict:
        """获取风险摘要"""
        return {
            "portfolio": self.portfolio_state,
            "market": self.market_state,
            "daily_stats": self.daily_stats,
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "violations_today": len([
                v for v in self.engine.violations
                if v.triggered_at.date() == datetime.now().date()
            ])
        }


@dataclass
class Alert:
    """告警"""
    alert_id: str
    severity: str
    title: str
    message: str
    triggered_at: datetime
    rules_triggered: List[str]
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

---

## 5. 风控报告

### 5.1 报告生成�?

```python
class RiskReportGenerator:
    """风控报告生成�?""

    def __init__(self, engine: RiskControlEngine, monitor: RiskMonitor):
        self.engine = engine
        self.monitor = monitor

    def generate_daily_report(self, date: date) -> str:
        """生成日报"""
        violations = [
            v for v in self.engine.violations
            if v.triggered_at.date() == date
        ]

        critical_count = sum(
            1 for v in violations
            if v.severity == RuleSeverity.CRITICAL
        )

        lines = [
            "=" * 80,
            f"风险控制日报 - {date}",
            "=" * 80,
            "",
            "1. 风险指标摘要",
            "-" * 40,
        ]

        summary = self.monitor.get_risk_summary()

        if summary.get("portfolio"):
            p = summary["portfolio"]
            lines.append(f"  账户总�? {p.get('total_value', 0):,.2f}")
            lines.append(f"  今日盈亏: {p.get('daily_pnl', 0):,.2f} ({p.get('daily_pnl_pct', 0):.2%})")
            lines.append(f"  最大回�? {p.get('max_drawdown', 0):.2%}")
            lines.append(f"  波动�? {p.get('volatility', 0):.2%}")

        lines.append("")
        lines.append("2. 规则触发统计")
        lines.append("-" * 40)

        rule_stats = {}
        for v in violations:
            rule_stats[v.rule_name] = rule_stats.get(v.rule_name, 0) + 1

        for rule_name, count in sorted(rule_stats.items(), key=lambda x: -x[1]):
            lines.append(f"  {rule_name}: {count}�?)

        if critical_count > 0:
            lines.append("")
            lines.append(f"⚠️ 严重告警: {critical_count}�?)

        lines.append("")
        lines.append("3. 违规详情")
        lines.append("-" * 40)

        for v in violations[:10]:
            lines.append(f"  [{v.triggered_at.strftime('%H:%M:%S')}] {v.rule_name}")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def generate_violation_report(
        self,
        start_date: date = None,
        end_date: date = None
    ) -> str:
        """生成违规报告"""
        violations = self.engine.violations

        if start_date:
            violations = [v for v in violations if v.triggered_at.date() >= start_date]

        if end_date:
            violations = [v for v in violations if v.triggered_at.date() <= end_date]

        lines = [
            "=" * 80,
            "违规记录报告",
            "=" * 80,
            ""
        ]

        by_severity = {}
        for v in violations:
            severity = v.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

        lines.append("按严重级别统�?")
        for severity, count in by_severity.items():
            lines.append(f"  {severity}: {count}")

        lines.append("")
        lines.append("详细记录:")
        lines.append("-" * 80)

        for v in violations[:50]:
            lines.append(
                f"{v.triggered_at} | {v.severity.value:8} | {v.rule_name}"
            )

        return "\n".join(lines)
```

---

## 6. 使用示例

```python
def example_risk_control():
    """风控系统使用示例"""

    engine = RiskControlEngine()

    engine.register_rule(RuleTemplates.single_stock_position_limit(0.15))
    engine.register_rule(RuleTemplates.sector_position_limit(0.30))
    engine.register_rule(RuleTemplates.daily_loss_limit(0.02))
    engine.register_rule(RuleTemplates.max_drawdown_limit(0.10))

    def alert_handler(level, message):
        print(f"[{level.upper()}] {message}")

    engine.set_alert_handler(alert_handler)

    monitor = RiskMonitor(engine)

    portfolio = Portfolio(
        total_value=1000000,
        cash=500000,
        positions={"000001.SZ": Position(stock_code="000001.SZ", quantity=10000, avg_cost=10.5)}
    )

    monitor.update_portfolio(portfolio)

    order = Order(
        order_id="O001",
        stock_code="000001.SZ",
        direction="buy",
        quantity=5000,
        price=10.8
    )

    context = {
        "portfolio": portfolio.to_dict(),
        "position": portfolio.get_position_summary()
    }

    result = engine.check_pretrade(order, context)

    if result.blocked:
        print(f"Order blocked: {result.message}")
    else:
        print("Order allowed")
```

---

## 6. 规则配置 (YAML)

```yaml
# config/risk/rules.yaml

rules:
  # ============ 事前风控规则 ============

  - rule_id: RISK_001
    name: "单股仓位限制"
    category: pre_trade
    severity: danger
    enabled: true
    params:
      max_position_ratio: 0.10  # 单股最大仓�?0%
      max_position_value: 1000000  # 单股最大市�?00�?
    condition: "check_position_limit"
    action: "reject_order"

  - rule_id: RISK_002
    name: "总仓位限�?
    category: pre_trade
    severity: danger
    enabled: true
    params:
      max_total_ratio: 0.80  # 总仓位最�?0%
    condition: "check_total_position"
    action: "reject_order"

  - rule_id: RISK_003
    name: "资金充足检�?
    category: pre_trade
    severity: danger
    enabled: true
    params:
      min_cash_reserve: 0.05  # 最�?%现金储备
    condition: "check_fund_sufficiency"
    action: "reject_order"

  - rule_id: RISK_004
    name: "ST股票限制"
    category: pre_trade
    severity: warning
    enabled: true
    params:
      allowed: false
    condition: "check_st_stock"
    action: "reject_order"

  - rule_id: RISK_005
    name: "涨停不买"
    category: pre_trade
    severity: warning
    enabled: true
    params: {}
    condition: "check_limit_up"
    action: "reject_order"

  # ============ 事中风控规则 ============

  - rule_id: RISK_006
    name: "单股回撤止损"
    category: in_trade
    severity: critical
    enabled: true
    params:
      max_loss_ratio: 0.08  # 单股最大回�?%
    condition: "check_stock_stop_loss"
    action: "close_position"

  - rule_id: RISK_007
    name: "组合回撤止损"
    category: in_trade
    severity: critical
    enabled: true
    params:
      max_portfolio_loss: 0.05  # 组合最大回�?%
    condition: "check_portfolio_stop_loss"
    action: "close_all_positions"

  - rule_id: RISK_008
    name: "移动止损"
    category: in_trade
    severity: danger
    enabled: true
    params:
      trailing_ratio: 0.03  # 移动止损3%
    condition: "check_trailing_stop"
    action: "reduce_position"

  - rule_id: RISK_009
    name: "波动率预�?
    category: in_trade
    severity: warning
    enabled: true
    params:
      vol_threshold: 0.30  # 波动率阈�?0%
    condition: "check_volatility"
    action: "send_alert"

  - rule_id: RISK_010
    name: "流动性预�?
    category: in_trade
    severity: warning
    enabled: true
    params:
      min_volume: 1000000  # 最小成交量100�?
      min_turnover: 500000  # 最小成交额50�?
    condition: "check_liquidity"
    action: "send_alert"
```

---

## 7. 风控API

```python
# API: /api/v1/risk

risk_router = APIRouter()

class RiskEndpoints:
    """风控接口

    索引: API_RISK_001
    """

    @risk_router.get("/rules")
    async def list_rules(
        category: str = None,
        auth: dict = Depends(verify_auth)
    ) -> List[RiskRule]:
        """列出风控规则

        参数:
            category: pre_trade / in_trade / post_trade
        """
        rules = RiskRuleEngine.get_rules(category=category)
        return rules

    @risk_router.post("/rules")
    async def create_rule(
        rule: RiskRuleConfig,
        auth: dict = Depends(verify_auth)
    ) -> RiskRule:
        """创建风控规则"""
        if not check_permission(auth['role'], 'risk:write'):
            raise HTTPException(status_code=403, detail="无权�?)

        return RiskRuleEngine.create_rule(rule)

    @risk_router.put("/rules/{rule_id}")
    async def update_rule(
        rule_id: str,
        rule: RiskRuleConfig,
        auth: dict = Depends(verify_auth)
    ) -> RiskRule:
        """更新风控规则"""

    @risk_router.post("/rules/{rule_id}/enable")
    async def enable_rule(
        rule_id: str,
        auth: dict = Depends(verify_auth)
    ) -> Response:
        """启用规则"""
        RiskRuleEngine.enable_rule(rule_id)
        return Response(code=0, message="规则已启�?)

    @risk_router.post("/rules/{rule_id}/disable")
    async def disable_rule(
        rule_id: str,
        auth: dict = Depends(verify_auth)
    ) -> Response:
        """禁用规则"""
        RiskRuleEngine.disable_rule(rule_id)
        return Response(code=0, message="规则已禁�?)

    @risk_router.get("/violations")
    async def get_violations(
        start_date: str = None,
        end_date: str = None,
        auth: dict = Depends(verify_auth)
    ) -> List[Violation]:
        """查询违规记录"""
        return RiskRuleEngine.get_violations(start_date, end_date)

    @risk_router.get("/alerts")
    async def get_alerts(
        start_date: str = None,
        end_date: str = None,
        auth: dict = Depends(verify_auth)
    ) -> List[Alert]:
        """查询告警记录"""
        return RiskRuleEngine.get_alerts(start_date, end_date)
```

---

## 8. 开发任务分�?

| 任务 | 时间 | 说明 |
|------|------|------|
| 规则引擎核心 | 8h | RiskRuleEngine |
| 规则条件实现 | 10h | 10+种条�?|
| 规则动作实现 | 6h | 5种动�?|
| 规则配置加载 | 4h | YAML配置解析 |
| 告警管理 | 4h | AlertManager |
| API�?| 4h | REST API |
| 测试 | 4h | 单元测试 |
| **总计** | **40h** | |

---

## 9. 相关文档

| 文档 | 层级 | 说明 |
|------|------|------|
| [实时风险监控仪表板](../../01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md) | 框架�?| 定义整体架构和设计原�?|
| [风控规则体系蓝图](../../03_TRADING_TACTICS/09_RISK_RULES/BLUEPRINT.md) | 战术�?| 定义规则体系和三层防�?|
| [风险报告生成器](../../03_TRADING_TACTICS/09_RISK_RULES/RISK_REPORT.md) | 战术�?| 风险报告生成 |

---

**版本**: v2.0 (合并�?
**更新**: 2026-04-04
**Layer**: Layer 6 (风险监控)
**索引**: EXECUTION_RISK_ENGINE_001
**上游接口**: PortfolioOptimizer, TradeExecutor
**下游接口**: AlertManager, PerformanceAnalyzer
**合并来源**: �?`03_TRADING_TACTICS/09_RISK_RULES/RISK_RULE_ENGINE.md` 已整合至�?
