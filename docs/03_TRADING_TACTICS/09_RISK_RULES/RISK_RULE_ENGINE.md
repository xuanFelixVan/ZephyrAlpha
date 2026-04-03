---
module_id: TACTICS_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---


# 风控规则引擎蓝图

> 清风量化系统 v5.0 - 风控规则引擎
> **索引**: `RISK.001`
> **开发时间**: 40h
> **核心定位**: 实现"规则定义 → 实时检查 → 告警/执行 → 记录"的完整风控闭环


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **规则即配置** | 风控规则以YAML配置，不写死代码 |
| **三层防御** | 事前检查 → 事中监控 → 事后分析 |
| **快速失败** | 风控触发时立即行动，不等待人工 |
| **完整审计** | 所有风控事件完整记录 |


## 2. 风控架构

### 2.1 三层风控

```
┌─────────────────────────────────────────────────────────────┐
│                    三层风控体系                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 3: 事前风控 (Pre-Trade)                             │
│  ├── 下单前检查                                            │
│  ├── 仓位限制检查                                          │
│  └── 资金充足检查                                          │
│                            │                                │
│                            ▼                                │
│  Layer 6: 事中风控 (In-Trade)                             │
│  ├── 实时持仓监控                                          │
│  ├── 动态止损检查                                          │
│  └── 波动率监控                                            │
│                            │                                │
│                            ▼                                │
│  Layer 7: 事后风控 (Post-Trade)                           │
│  ├── 日终风险报告                                          │
│  ├── 归因分析                                              │
│  └── 规则复盘                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 风控流程

```
信号 → 事前风控 → 订单生成 → 事中风控 → 成交回报
                          ↓
                    风控规则引擎
                          ↓
                    告警/执行动作
```


## 3. 核心实现

### 3.1 规则定义

```python
class RiskRule:
    """风控规则

    索引: RISK.001-M01
    """

    def __init__(
        self,
        rule_id: str,
        name: str,
        category: str,  # pre_trade / in_trade / post_trade
        severity: str,  # info / warning / danger / critical
        condition: Callable,
        action: Callable,
        enabled: bool = True
    ):
        self.rule_id = rule_id
        self.name = name
        self.category = category
        self.severity = severity
        self.condition = condition
        self.action = action
        self.enabled = enabled

    def check(self, context: dict) -> CheckResult:
        """检查规则

        参数:
            context: 上下文 (order/position/market_data)

        返回:
            CheckResult
        """
        if not self.enabled:
            return CheckResult(passed=True)

        try:
            triggered, details = self.condition(context)
            if triggered:
                return CheckResult(
                    passed=False,
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    details=details
                )
            return CheckResult(passed=True)
        except Exception as e:
            return CheckResult(
                passed=True,
                warning=f"规则检查异常: {e}"
            )
```

### 3.2 规则配置

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
      max_position_ratio: 0.10  # 单股最大仓位10%
      max_position_value: 1000000  # 单股最大市值100万
    condition: "check_position_limit"
    action: "reject_order"

  - rule_id: RISK_002
    name: "总仓位限制"
    category: pre_trade
    severity: danger
    enabled: true
    params:
      max_total_ratio: 0.80  # 总仓位最大80%
    condition: "check_total_position"
    action: "reject_order"

  - rule_id: RISK_003
    name: "资金充足检查"
    category: pre_trade
    severity: danger
    enabled: true
    params:
      min_cash_reserve: 0.05  # 最低5%现金储备
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
      max_loss_ratio: 0.08  # 单股最大回撤8%
    condition: "check_stock_stop_loss"
    action: "close_position"

  - rule_id: RISK_007
    name: "组合回撤止损"
    category: in_trade
    severity: critical
    enabled: true
    params:
      max_portfolio_loss: 0.05  # 组合最大回撤5%
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
    name: "波动率预警"
    category: in_trade
    severity: warning
    enabled: true
    params:
      vol_threshold: 0.30  # 波动率阈值30%
    condition: "check_volatility"
    action: "send_alert"

  - rule_id: RISK_010
    name: "流动性预警"
    category: in_trade
    severity: warning
    enabled: true
    params:
      min_volume: 1000000  # 最小成交量100万
      min_turnover: 500000  # 最小成交额50万
    condition: "check_liquidity"
    action: "send_alert"
```

### 3.3 规则引擎

```python
class RiskRuleEngine:
    """风控规则引擎

    索引: RISK.001-M02
    上游: StrategyEngine, OrderGenerator
    下游: OrderExecutor, AlertManager
    """

    def __init__(self):
        self.rules = []
        self.alert_manager = AlertManager()
        self.event_bus = EventBus()

    def load_rules(self, config_path: str):
        """加载规则配置

        参数:
            config_path: 规则配置文件路径
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        for rule_config in config['rules']:
            rule = self._create_rule(rule_config)
            self.rules.append(rule)

        logger.info(f"加载了 {len(self.rules)} 条风控规则")

    def check_pre_trade(self, order: Order, context: dict) -> CheckResult:
        """事前风控检查

        参数:
            order: 订单
            context: 上下文

        返回:
            CheckResult
        """
        context['order'] = order

        violations = []
        for rule in self.rules:
            if rule.category != 'pre_trade':
                continue

            result = rule.check(context)
            if not result.passed:
                violations.append(result)
                self._publish_violation(rule, result)

        if violations:
            return CheckResult(
                passed=False,
                violations=violations,
                action='reject'
            )

        return CheckResult(passed=True)

    def check_in_trade(self, position: Position, context: dict) -> CheckResult:
        """事中风控检查

        参数:
            position: 持仓
            context: 上下文

        返回:
            CheckResult
        """
        context['position'] = position

        alerts = []
        actions = []

        for rule in self.rules:
            if rule.category != 'in_trade':
                continue

            result = rule.check(context)
            if not result.passed:
                alerts.append(result)
                actions.append(rule.action)

                self._publish_alert(rule, result)

        if actions:
            return CheckResult(
                passed=True,
                alerts=alerts,
                actions=actions,
                action='execute' if 'close' in str(actions) else 'alert'
            )

        return CheckResult(passed=True)

    def _publish_violation(self, rule: RiskRule, result: CheckResult):
        """发布违规事件"""
        self.event_bus.publish('risk.violation', {
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'severity': rule.severity,
            'details': result.details
        })

    def _publish_alert(self, rule: RiskRule, result: CheckResult):
        """发布告警事件"""
        self.event_bus.publish('risk.alert', {
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'severity': rule.severity,
            'details': result.details
        })
```

### 3.4 规则条件实现

```python
class RiskConditions:
    """风控条件实现

    索引: RISK.001-M03
    """

    @staticmethod
    def check_position_limit(order: Order, context: dict, params: dict) -> tuple:
        """检查单股仓位限制"""
        account = context['account']
        symbol = order.symbol
        target_quantity = order.quantity

        current_pos = account.get_position(symbol)
        current_value = current_pos.quantity * order.price if current_pos else 0
        target_value = target_quantity * order.price
        new_ratio = (current_value + target_value) / account.total_value

        if new_ratio > params['max_position_ratio']:
            return True, f"单股仓位 {new_ratio:.2%} 超过限制 {params['max_position_ratio']:.2%}"

        if current_value + target_value > params['max_position_value']:
            return True, f"单股市值超过限制 {params['max_position_value']}"

        return False, None

    @staticmethod
    def check_total_position(order: Order, context: dict, params: dict) -> tuple:
        """检查总仓位限制"""
        account = context['account']
        current_value = account.total_value - account.cash
        target_value = order.quantity * order.price
        new_ratio = (current_value + target_value) / account.total_value

        if new_ratio > params['max_total_ratio']:
            return True, f"总仓位 {new_ratio:.2%} 超过限制 {params['max_total_ratio']:.2%}"

        return False, None

    @staticmethod
    def check_stock_stop_loss(position: Position, context: dict, params: dict) -> tuple:
        """检查单股止损"""
        if not position:
            return False, None

        current_price = context['market_data'].get_price(position.symbol).last
        entry_price = position.avg_price
        loss_ratio = (entry_price - current_price) / entry_price

        if loss_ratio > params['max_loss_ratio']:
            return True, f"单股回撤 {loss_ratio:.2%} 超过限制 {params['max_loss_ratio']:.2%}"

        return False, None

    @staticmethod
    def check_trailing_stop(position: Position, context: dict, params: dict) -> tuple:
        """检查移动止损"""
        if not position:
            return False, None

        current_price = context['market_data'].get_price(position.symbol).last
        highest_price = position.highest_price
        trailing_ratio = params['trailing_ratio']

        # 从最高点回撤超过阈值
        if highest_price and (highest_price - current_price) / highest_price > trailing_ratio:
            return True, f"移动止损触发: 回撤 {(highest_price - current_price) / highest_price:.2%}"

        return False, None
```

### 3.5 规则动作实现

```python
class RiskActions:
    """风控动作实现

    索引: RISK.001-M04
    """

    @staticmethod
    def reject_order(order: Order, result: CheckResult) -> None:
        """拒绝订单"""
        logger.warning(f"风控拒绝订单: {order.id} - {result.details}")
        raise OrderRejectedError(order.id, result.details)

    @staticmethod
    def close_position(position: Position, result: CheckResult) -> Order:
        """平仓"""
        logger.warning(f"风控平仓: {position.symbol} - {result.details}")

        close_order = Order(
            symbol=position.symbol,
            action='sell' if position.quantity > 0 else 'buy',
            quantity=abs(position.quantity),
            order_type='market',
            reason=f"风控平仓: {result.details}"
        )

        return close_order

    @staticmethod
    def close_all_positions(result: CheckResult) -> List[Order]:
        """清空所有持仓"""
        logger.critical(f"风控清空所有持仓: {result.details}")

        orders = []
        for position in account.get_all_positions():
            order = Order(
                symbol=position.symbol,
                action='sell' if position.quantity > 0 else 'buy',
                quantity=abs(position.quantity),
                order_type='market',
                reason=f"风控清仓: {result.details}"
            )
            orders.append(order)

        return orders

    @staticmethod
    def send_alert(result: CheckResult) -> None:
        """发送告警"""
        alert = {
            'severity': result.severity,
            'title': f"风控告警: {result.rule_name}",
            'message': result.details
        }
        AlertManager().send(alert)
```


## 4. 风控API

### 4.1 风控接口

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
            raise HTTPException(status_code=403, detail="无权限")

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
        return Response(code=0, message="规则已启用")

    @risk_router.post("/rules/{rule_id}/disable")
    async def disable_rule(
        rule_id: str,
        auth: dict = Depends(verify_auth)
    ) -> Response:
        """禁用规则"""
        RiskRuleEngine.disable_rule(rule_id)
        return Response(code=0, message="规则已禁用")

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


## 5. 告警管理

### 5.1 告警管理器

```python
class AlertManager:
    """告警管理器

    索引: RISK.001-M05
    """

    def __init__(self):
        self.channels = {
            'email': EmailChannel(),
            'dingtalk': DingTalkChannel(),
            'wechat': WeChatChannel()
        }

    def send(self, alert: dict):
        """发送告警

        参数:
            alert: {
                'severity': 'info/warning/danger/critical',
                'title': str,
                'message': str,
                'channels': ['email', 'dingtalk']  # 可选，默认识别
            }
        """
        severity = alert.get('severity', 'info')
        channels = alert.get('channels', self._get_default_channels(severity))

        for channel in channels:
            if channel in self.channels:
                self.channels[channel].send(alert)

    def _get_default_channels(self, severity: str) -> List[str]:
        """获取默认渠道"""
        if severity == 'critical':
            return ['dingtalk', 'email']  # 严重告警两个都发
        elif severity == 'danger':
            return ['dingtalk']
        elif severity == 'warning':
            return ['email']
        else:
            return []  # info不发送
```


## 6. 开发任务分解

### 6.1 任务分解 (40h)

| 任务 | 时间 | 说明 |
|------|------|------|
| 规则引擎核心 | 8h | RiskRuleEngine |
| 规则条件实现 | 10h | 10+种条件 |
| 规则动作实现 | 6h | 5种动作 |
| 规则配置加载 | 4h | YAML配置解析 |
| 告警管理 | 4h | AlertManager |
| API层 | 4h | REST API |
| 测试 | 4h | 单元测试 |
