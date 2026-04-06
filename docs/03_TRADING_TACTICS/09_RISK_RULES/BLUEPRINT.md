---
module_id: BLUEPRINT_002
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 交易策略团队
responsibility:
  - 风险预算
  - 因子计算
  - 组合优化
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准---


﻿---
module_id: TACTICS_RISK_RULES_BP_001
version: 1.0.2
status: Active
created_date: 2026-04-01
last_updated: 2026-04-04
owner: 首席文档架构�?
standard_type: 专业量化机构蓝图
applicable_scope: 全系统架构设�?
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
related_documents:
  upstream:
    - 01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md (框架层架构定�?
  downstream:
    - 04_EXECUTION/05_RISK_ENGINE/README.md (执行层实�?
    - 03_TRADING_TACTICS/09_RISK_RULES/RISK_REPORT.md (风险报告生成�?
---

# 风控规则体系蓝图

> 清风量化系统 v5.0 的风险控制规则体�?
> **索引**: `RSK_001`
> **版本**: v1.0.1
> **更新**: 2026-04-04

---

## 文档层级关系

```
┌─────────────────────────────────────────────────────────────�?
�? 框架�? 01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md  �?
�? 定义实时风险监控的整体架构和设计原则                          �?
└─────────────────────────────────────────────────────────────�?
                              �?
┌─────────────────────────────────────────────────────────────�?
�? 本文�? 战术�?- 定义风控规则体系和三层防御架�?              �?
└─────────────────────────────────────────────────────────────�?
                              �?
┌─────────────────────────────────────────────────────────────�?
�? 执行�? 04_EXECUTION/05_RISK_ENGINE/README.md               �?
�? 实现风控规则引擎核心功能                                     �?
└─────────────────────────────────────────────────────────────�?
```

**上游文档**: [实时风险监控仪表板](../../01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md) - 框架层架构定�?

**下游文档**:
- [风控规则引擎](../../04_EXECUTION/05_RISK_ENGINE/README.md) - 执行层实�?
- [风险报告生成器](./RISK_REPORT.md) - 报告生成

---


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| 三层防御 | 事前预防 �?事中监控 �?事后分析 |
| 零信�?| 所有订单必须过风控，不信任任何信号�?|
| 快速失�?| 风控触发时立即行动，不等待人工确�?|
| 可追�?| 所有风控事件完整记录，便于审计 |


## 2. 风控规则分层

### 2.1 规则层级架构

```
┌─────────────────────────────────────────────────────────────�?
�?                   Layer 3: 风险因子计算                      �?
�? ┌─────────────────────────────────────────────────────�?   �?
�? �?             事前风控规则 (Pre-Trade)                 �?   �?
�? �? -仓位限制  -对手方限�? -价格限制  -合约限制         �?   �?
�? └─────────────────────────────────────────────────────�?   �?
└─────────────────────────────────────────────────────────────�?
                            �?
┌─────────────────────────────────────────────────────────────�?
�?                   Layer 6: 风险监控                          �?
�? ┌─────────────────────────────────────────────────────�?   �?
�? �?             事中风控规则 (In-Trade)                 �?   �?
�? �? -实时盯盘  -动态止�? -流动性监�? -波动率监�?      �?   �?
�? └─────────────────────────────────────────────────────�?   �?
└─────────────────────────────────────────────────────────────�?
                            �?
┌─────────────────────────────────────────────────────────────�?
�?                   Layer 7: 绩效归因                          �?
�? ┌─────────────────────────────────────────────────────�?   �?
�? �?             事后风控规则 (Post-Trade)               �?   �?
�? �? -日终检�? -归因分析  -报告生成  -规则复盘          �?   �?
�? └─────────────────────────────────────────────────────�?   �?
└─────────────────────────────────────────────────────────────�?
```

### 2.2 规则分类矩阵

| 类别 | 层级 | 触发时机 | 执行方式 | 示例 |
|------|------|----------|----------|------|
| 仓位规则 | 事前 | 下单�?| 拒绝/修改 | 单股仓位<10% |
| 价格规则 | 事前 | 下单�?| 拒绝/修改 | 涨跌停不买入 |
| 合约规则 | 事前 | 下单�?| 拒绝 | ST股票不买 |
| 止损规则 | 事中 | 持仓�?| 自动平仓 | 回撤>5% |
| 流动性规�?| 事中 | 持仓�?| 预警/减仓 | 成交�?100�?|
| 波动率规�?| 事中 | 持仓�?| 预警/对冲 | IV>30% |
| 日终规则 | 事后 | 收盘�?| 报告 | 风险敞口报告 |
| 归因规则 | 事后 | 日终 | 分析 | P&L归因 |


## 3. 核心风控规则定义

### 3.1 事前风控规则 (Pre-Trade)

```yaml
# config/risk_rules/pre_trade.yaml

pre_trade_rules:
  # 仓位限制
  position_limit:
    single_stock_max_ratio: 0.10      # 单股最大仓�?0%
    single_stock_max_value: 1000000   # 单股最大市�?00�?
    sector_max_ratio: 0.30           # 单行业最大仓�?0%
    total_position_max: 0.80         # 总仓位最�?0%

  # 价格限制
  price_limit:
    no_buy_on_limit_up: true          # 涨停不买�?
    no_sell_on_limit_down: true       # 跌停不卖�?
    price_deviation_threshold: 0.02   # 偏离昨收2%需确认

  # 合约限制
  contract_limit:
    no_st_stock: true                # 不买ST�?
    no_new_stock_days: 60             # 次新股限制天�?
    no_suspended_stock: true          # 不买停牌�?

  # 资金限制
  fund_limit:
    min_cash_reserve: 0.05           # 最�?%现金储备
    max_single_order_ratio: 0.02     # 单笔订单最大占总资�?%
    daily_order_count_max: 100       # 单日最大订单数
```

### 3.2 事中风控规则 (In-Trade)

```yaml
# config/risk_rules/in_trade.yaml

in_trade_rules:
  # 止损规则
  stop_loss:
    portfolio_max_loss: 0.05         # 组合总回�?%止损
    single_stock_max_loss: 0.08      # 单股回撤8%止损
    trailing_stop_enabled: true     # 启用移动止损
    trailing_stop_ratio: 0.03       # 移动止损3%

  # 流动性监�?
  liquidity:
    min_daily_volume: 1000000        # 最小日成交�?00�?
    min_market_depth: 50000         # 最小买卖盘50�?
    liquidity_warning_ratio: 0.20   # 流动性预警比�?

  # 波动率监�?
  volatility:
    portfolio_vol_max: 0.25          # 组合波动率上�?5%
    single_stock_vol_max: 0.40      # 单股波动率上�?0%
    volatility_warning: 0.15        # 波动率预警阈�?

  # 盈亏监控
  pnl:
    daily_profit_target: 0.02       # 日盈利目�?%
    daily_loss_limit: 0.03          # 日亏损限�?%
    profit_take_ratio: 0.05         # 止盈比例5%
```

### 3.3 事后风控规则 (Post-Trade)

```yaml
# config/risk_rules/post_trade.yaml

post_trade_rules:
  # 日终检�?
  daily_check:
    generate_risk_report: true       # 生成日风险报�?
    check_overnight_positions: true # 检查隔夜持�?
    verify_settlement: true         # 核对结算

  # 归因分析
  attribution:
    factor_attribution: true         # 因子收益归因
    sector_attribution: true        # 行业收益归因
    transaction_cost_analysis: true # 交易成本分析

  # 规则复盘
  review:
    rule_trigger_review: true       # 规则触发复盘
    missed_opportunity_review: true # 错过机会复盘
    false_signal_review: true       # 假信号复�?
```


## 4. 风控规则引擎设计

### 4.1 规则引擎架构

```python
class RiskRuleEngine:
    """风控规则引擎

    索引: RSK_001-R01
    上游: StrategyEngine(信号), TradeExecutor(订单)
    下游: AlertManager(告警), TradeExecutor(执行控制)
    """

    def __init__(self):
        self.rules = {}
        self.rule_loader = RuleLoader()
        self.rule_executor = RuleExecutor()
        self.event_bus = EventBus()

    def load_rules(self, rule_config: dict):
        """加载风控规则

        参数:
            rule_config: 规则配置字典
        """
        for rule_name, rule_params in rule_config.items():
            rule = self._create_rule(rule_name, rule_params)
            self.rules[rule_name] = rule

    def check_pre_trade(self, order: Order) -> CheckResult:
        """事前风控检�?

        参数:
            order: 订单对象

        返回:
            CheckResult {
                'passed': bool,
                'rejected': bool,
                'modified': bool,
                'reasons': List[str]
            }
        """
        violations = []
        for rule_name, rule in self.rules.items():
            if rule.category != 'pre_trade':
                continue

            result = rule.check(order)
            if not result.passed:
                violations.append({
                    'rule': rule_name,
                    'reason': result.reason,
                    'severity': result.severity
                })

                self.event_bus.publish('risk.violation', {
                    'rule': rule_name,
                    'order': order,
                    'reason': result.reason
                })

        return CheckResult(
            passed=len(violations) == 0,
            violations=violations,
            action=self._determine_action(violations)
        )

    def check_in_trade(self, position: Position, market_data: MarketData) -> MonitorResult:
        """事中风控监控

        参数:
            position: 持仓对象
            market_data: 市场数据

        返回:
            MonitorResult {
                'status': str,  # normal/warning/danger
                'alerts': List[Alert],
                'actions': List[Action]
            }
        """
        alerts = []
        actions = []

        for rule_name, rule in self.rules.items():
            if rule.category != 'in_trade':
                continue

            result = rule.monitor(position, market_data)
            if result.triggered:
                alerts.append(result.alert)
                if result.action_required:
                    actions.append(result.action)

                    self.event_bus.publish('risk.alert', {
                        'rule': rule_name,
                        'position': position,
                        'alert': result.alert
                    })

        return MonitorResult(
            status=self._determine_status(alerts),
            alerts=alerts,
            actions=actions
        )

    def check_post_trade(self, trading_date: date) -> ReportResult:
        """事后风控检�?

        参数:
            trading_date: 交易日期

        返回:
            ReportResult: 日终风控报告
        """
        report = RiskReport(trading_date)

        for rule_name, rule in self.rules.items():
            if rule.category != 'post_trade':
                continue

            result = rule.analyze(trading_date)
            report.add_analysis(rule_name, result)

        return report

    def _create_rule(self, rule_name: str, rule_params: dict) -> RiskRule:
        """创建规则实例

        参数:
            rule_name: 规则名称
            rule_params: 规则参数

        返回:
            RiskRule: 规则实例
        """
        rule_class = self.rule_loader.get_rule_class(rule_name)
        return rule_class(**rule_params)
```

### 4.2 规则执行�?

```python
class RuleExecutor:
    """规则执行�?

    索引: RSK_001-R02
    上游: RiskRuleEngine
    下游: TradeExecutor, AlertManager
    """

    def execute_pre_trade(self, order: Order, check_result: CheckResult) -> Order:
        """执行事前风控

        参数:
            order: 原始订单
            check_result: 风控检查结�?

        返回:
            处理后的订单(可能被拒�?修改)
        """
        if check_result.rejected:
            self._reject_order(order, check_result.violations)
            raise OrderRejectedError(order, check_result.violations)

        if check_result.modified:
            order = self._modify_order(order, check_result.modifications)

        order.risk_checked = True
        return order

    def execute_in_trade(self, actions: List[Action]) -> List[ExecutionResult]:
        """执行事中风控动作

        参数:
            actions: 动作列表

        返回:
            执行结果列表
        """
        results = []
        for action in actions:
            if action.type == 'close_position':
                result = self._close_position(action.position, action.reason)
            elif action.type == 'reduce_position':
                result = self._reduce_position(action.position, action.ratio)
            elif action.type == 'send_alert':
                result = self._send_alert(action.alert)
            else:
                result = ExecutionResult(success=False, reason='Unknown action')

            results.append(result)
            self._log_action(action, result)

        return results

    def _reject_order(self, order: Order, violations: List):
        """拒绝订单"""
        logger.warning(f"Order {order.order_id} rejected: {violations}")
        self.event_bus.publish('order.rejected', {
            'order': order,
            'violations': violations
        })

    def _modify_order(self, order: Order, modifications: dict) -> Order:
        """修改订单"""
        if 'quantity' in modifications:
            order.quantity = modifications['quantity']
        if 'price' in modifications:
            order.price = modifications['price']
        logger.info(f"Order {order.order_id} modified: {modifications}")
        return order

    def _close_position(self, position: Position, reason: str) -> ExecutionResult:
        """平仓"""
        order = Order(
            symbol=position.symbol,
            action='sell' if position.quantity > 0 else 'buy',
            quantity=abs(position.quantity),
            order_type='market'
        )
        return self.trade_executor.execute(order)

    def _send_alert(self, alert: Alert) -> ExecutionResult:
        """发送告�?""
        self.alert_manager.send(alert)
        return ExecutionResult(success=True)
```


## 5. 规则配置接口

### 5.1 规则配置格式

```yaml
# 规则定义示例
rules:
  - id: RSK_001_R01
    name: "单股仓位限制"
    category: pre_trade
    severity: high
    params:
      max_ratio: 0.10
      max_value: 1000000
    enabled: true

  - id: RSK_001_R02
    name: "移动止损"
    category: in_trade
    severity: critical
    params:
      trailing_ratio: 0.03
      check_interval: 60  # �?
    enabled: true
```

### 5.2 规则API接口

```python
# API: /api/v1/risk/rules

class RiskRuleAPI:
    """风控规则API

    索引: API_RSK_001
    Layer: Layer 0
    """

    @router.get("/rules")
    def list_rules(self) -> List[RuleInfo]:
        """获取规则列表"""

    @router.post("/rules")
    def create_rule(self, rule: RuleCreate) -> RuleInfo:
        """创建规则"""

    @router.put("/rules/{rule_id}")
    def update_rule(self, rule_id: str, rule: RuleUpdate) -> RuleInfo:
        """更新规则"""

    @router.delete("/rules/{rule_id}")
    def delete_rule(self, rule_id: str) -> None:
        """删除规则"""

    @router.post("/rules/{rule_id}/enable")
    def enable_rule(self, rule_id: str) -> None:
        """启用规则"""

    @router.post("/rules/{rule_id}/disable")
    def disable_rule(self, rule_id: str) -> None:
        """禁用规则"""

    @router.get("/rules/{rule_id}/history")
    def get_rule_history(self, rule_id: str) -> List[RuleEvent]:
        """获取规则触发历史"""

    @router.post("/rules/backtest")
    def backtest_rules(self, config: RuleConfig) -> BacktestResult:
        """回测规则效果"""
```


## 6. 风控事件�?

### 6.1 事件总线设计

```python
# 风控事件定义
RISK_EVENTS = {
    # 事前事件
    'risk.pre_trade.check': '下单前风控检�?,
    'risk.pre_trade.passed': '风控检查通过',
    'risk.pre_trade.rejected': '风控检查拒�?,
    'risk.pre_trade.modified': '风控修改订单',

    # 事中事件
    'risk.in_trade.monitor': '持仓监控',
    'risk.alert.warning': '预警',
    'risk.alert.danger': '危险告警',
    'risk.action.close': '执行平仓',
    'risk.action.reduce': '执行减仓',

    # 事后事件
    'risk.post_trade.report': '日终报告',
    'risk.attribution.complete': '归因完成',

    # 规则事件
    'risk.rule.triggered': '规则触发',
    'risk.rule.violation': '规则违反',
    'risk.rule.disabled': '规则禁用'
}

# 事件订阅示例
event_bus.subscribe('risk.alert.*', self._handle_risk_alert)
event_bus.subscribe('risk.action.*', self._handle_risk_action)
```

### 6.2 告警级别定义

| 级别 | 颜色 | 含义 | 动作 |
|------|------|------|------|
| INFO | 蓝色 | 正常监控信息 | 记录 |
| WARNING | 黄色 | 需要关�?| 人工确认 |
| DANGER | 橙色 | 危险信号 | 自动减仓 |
| CRITICAL | 红色 | 极端风险 | 自动清仓 |


## 7. 规则执行优先�?

| 优先�?| 规则类型 | 执行方式 | 超时限制 |
|--------|----------|----------|----------|
| 1 | 资金风控 | 同步, 必须执行 | <10ms |
| 2 | 仓位风控 | 同步, 必须执行 | <10ms |
| 3 | 价格风控 | 同步, 必须执行 | <10ms |
| 4 | 止损风控 | 异步, 自动执行 | <100ms |
| 5 | 流动性风�?| 异步, 预警+执行 | <1s |
| 6 | 波动率风�?| 异步, 预警+对冲 | <1s |


## 8. 监控指标

### 8.1 核心指标

| 指标 | 说明 | 阈�?|
|------|------|------|
| risk_pre_trade_check_time | 事前风控检查耗时 | <10ms |
| risk_rule_trigger_count | 规则触发次数/�?| <100 |
| risk_false_positive_rate | 误报�?| <5% |
| risk_blocked_order_ratio | 被拒绝订单比�?| <1% |
| risk_alert_response_time | 告警响应时间 | <1s |

### 8.2 监控面板

```
┌─────────────────────────────────────────────────────────────�?
�?                   风控监控面板                              �?
├─────────────────────────────────────────────────────────────�?
�? 规则状�?        当前持仓风险:      今日告警:              �?
�? 12/15 启用       VaR: 2.3%          WARNING: 3            �?
�?                  CVaR: 4.1%         DANGER: 1              �?
�?                  波动�? 18%         CRITICAL: 0           �?
├─────────────────────────────────────────────────────────────�?
�? 最近告�?                                                �?
�? 14:32 ST股票买入被拒�?- RSK_001_R03                       �?
�? 14:28 单股仓位超限 - RSK_001_R01                          �?
�? 14:15 移动止损触发 - RSK_001_R05                          �?
└─────────────────────────────────────────────────────────────�?
```


## 9. 集成接口

### 9.1 上游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| StrategyEngine | generate_signal() | 接收交易信号 |
| TradeExecutor | submit_order() | 接收订单请求 |
| DataHub | get_market_data() | 获取市场数据 |
| ConfigManager | get_risk_config() | 获取风控配置 |

### 9.2 下游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| TradeExecutor | execute_action() | 执行风控动作 |
| AlertManager | send_alert() | 发送告�?|
| PerformanceAnalyzer | report() | 生成报告 |
| LogManager | log_event() | 记录日志 |


## 10. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |


**维护�?*: 清风量化系统
**索引**: `RSK_001`
---

## 11. 文档治理

### 11.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Tactics Risk Rules Bp
- **模块ID**: TACTICS_RISK_RULES_BP_001
- **蓝图文档**: [BLUEPRINT.md](./03_TRADING_TACTICS\09_RISK_RULES\BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: 全系统架构设�?
- **状态**: Active
```

### 11.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Tactics Risk Rules Bp** | 全系统架构设�? | **核心模块** |

### 11.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-01 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-01 | **状态**: Active
