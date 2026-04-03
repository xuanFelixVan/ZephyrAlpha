---
module_id: COMPLIANCE_CHECKER_001
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: 首席架构师
standard_type: 专业量化机构技术规格书
applicable_scope: Layer 5 策略执行层 | 业务架构: 三级时间框架融合架构
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 已完成
regulatory_basis:
  - name: 证监会《关于短线交易监管的若干规定》
    effective_date: 2026-04-07
    document_id: 证监会公告〔2026〕4号
  - name: 沪深北交易所《程序化交易管理实施细则》
    effective_date: 2025-07-07
    document_id: 上证发〔2025〕52号
---

# 监管合规检查模块技术规格书

> 清风量化系统 v5.2 - 监管合规检查模块详细技术设计
> **模块ID**: `COMPLIANCE_CHECKER_001`
> **版本**: v1.0.0
> **状态**: ✅ 正式

---

## 1. 概述

### 1.1 设计背景与业务目标

**监管背景**：
- **2026年4月7日**：证监会《关于短线交易监管的若干规定》正式施行
- **2025年7月7日**：沪深北交易所《程序化交易管理实施细则》正式施行
- **监管导向**：限速、穿透、平权，A股交易生态迎来根本性重塑

**业务需求**：
- 系统需要符合最新监管要求，避免违规风险
- 需要实时监控交易行为，防止触发高频交易认定
- 需要检查撤单限制，避免撤单率超标
- 需要监控短线交易，遵守6个月锁仓期规定
- 需要生成合规报告，便于监管报备

**预期价值**：
- 确保系统100%符合监管要求，避免违规处罚
- 实时预警合规风险，提前采取应对措施
- 降低合规成本，自动化合规检查流程
- 提升系统专业性，符合机构级标准

### 1.2 技术定位与架构层归属

**Layer定位**: Layer 5 - 策略执行层

**模块类别**: 核心合规模块（P0级）

**架构角色**: 
- 作为Layer 5执行层的合规守门员，确保所有交易行为符合监管要求
- 作为风险控制的关键环节，在订单提交前进行合规检查
- 作为监管报告的数据源，提供完整的合规审计轨迹

### 1.3 核心功能清单

1. **高频交易认定检查**: 检查是否触发高频交易认定标准
2. **撤单限制检查**: 检查撤单频率和撤单率是否符合限制
3. **订单停留时间检查**: 检查订单是否满足最小停留时间要求
4. **短线交易合规检查**: 检查大股东短线交易锁仓期
5. **异常交易行为监控**: 监控四类异常交易行为
6. **合规报告生成**: 生成完整的合规审计报告

---

## 2. 架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 5: 策略执行层                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        ComplianceChecker (合规检查器主模块)           │  │
│  │  - 高频交易认定检查                                    │  │
│  │  - 撤单限制检查                                        │  │
│  │  - 短线交易检查                                        │  │
│  │  - 异常行为监控                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          核心组件                                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │OrderTracker │ │RegulatoryCfg│ │ComplianceRpt│  │  │
│  │  │订单跟踪器    │  │监管配置     │  │合规报告     │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          监管规则库                                    │  │
│  │  - 高频交易认定标准                                    │  │
│  │  - 撤单限制规则                                        │  │
│  │  - 短线交易规则                                        │  │
│  │  - 异常行为判定规则                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Layer定位详细说明

- **Layer归属**: Layer 5 - 策略执行层
- **职责范围**: 交易前合规检查、实时合规监控、合规报告生成
- **上下层接口**: 
  - 上层依赖: Layer 5 SignalGenerator (提供交易信号)
  - 下层依赖: Layer 6 组合优化层 (接收执行结果)

### 2.3 模块职责与边界定义

- **核心职责**: 监管合规检查、合规风险预警、合规报告生成
- **职责边界**: 
  - ✅ 本模块负责: 合规检查、合规监控、合规报告
  - ❌ 本模块不负责: 风险模型、策略决策、订单执行
- **接口契约**: 提供统一的Python API接口

---

## 3. 监管规则详细说明

### 3.1 高频交易认定标准

**监管依据**: 沪深北交易所《程序化交易管理实施细则》第三十三条

**认定标准**:
```python
HIGH_FREQUENCY_TRADING_CRITERIA = {
    'per_second_threshold': 300,      # 每秒申报+撤单≥300笔
    'per_day_threshold': 20000,       # 单日申报+撤单≥20000笔
    'stricter_standard': {
        'per_second': 15,              # 更严格标准：每秒15笔
        'cancel_rate_per_day': 0.15    # 单日撤单率≤15%
    }
}
```

**监管措施**:
- 履行额外报告义务
- 从严管理异常交易行为
- 实行差异化收费标准
- 加收流量费和撤单费

### 3.2 撤单限制规则

**监管依据**: 沪深北交易所《程序化交易管理实施细则》

**限制标准**:
```python
CANCEL_ORDER_LIMITS = {
    'max_cancel_per_second': 15,       # 每秒撤单≤15笔
    'max_cancel_rate_per_day': 0.15,   # 单日撤单率≤15%
    'min_order_duration_microseconds': 50,  # 订单停留≥50微秒
}
```

**违规后果**:
- 大幅提高撤单手续费
- 限制交易权限
- 暂停使用主机托管资源

### 3.3 短线交易监管规则

**监管依据**: 证监会《关于短线交易监管的若干规定》

**核心规则**:
```python
SHORT_TERM_TRADING_RULES = {
    'lock_period_months': 6,              # 6个月锁仓期
    'major_shareholder_threshold': 0.05,  # 5%大股东认定
    'penetration_enabled': True,          # 穿透监管启用
    'applicable_subjects': [
        '持股5%以上股东',
        '董监高',
        '同一实控人/管理人账户穿透合并计算'
    ]
}
```

**锁仓期规定**:
- 买入后6个月内不得卖出
- 卖出后6个月内不得买入
- 买卖时点以证券过户登记日为准

**豁免情形** (13种):
- ETF申赎、可转债转股、优先股转股
- 做市交易、股权激励、司法执行
- 责令回购等

### 3.4 异常交易行为监控

**监管依据**: 沪深北交易所《程序化交易管理实施细则》

**四类异常行为**:

| 异常行为类型 | 定义 | 监控阈值 |
|------------|------|---------|
| **瞬时申报速率异常** | 极短时间内申报笔数巨大 | 1秒内申报、撤单≥300笔 |
| **频繁瞬时撤单** | 日内频繁申报后迅速撤单 | 全日撤单比例≥15% |
| **频繁拉抬打压** | 日内多次小幅拉抬打压 | 价格变动≥2%，发生≥5次 |
| **短时间大额成交** | 短时间内集中同向交易 | 30分钟内成交量≥5倍 |

---

## 4. 核心类设计

### 4.1 ComplianceChecker (合规检查器)

**职责**: 主检查器，协调所有合规检查功能

**核心方法**:
```python
class ComplianceChecker:
    def check_high_frequency_trading() -> ComplianceCheckResult
    def check_cancel_limits() -> ComplianceCheckResult
    def check_order_duration(order: OrderRecord) -> ComplianceCheckResult
    def check_short_term_trading(...) -> ComplianceCheckResult
    def check_abnormal_trading() -> ComplianceCheckResult
    def check_order_before_submission(...) -> ComplianceCheckResult
    def generate_compliance_report() -> Dict
```

### 4.2 OrderTracker (订单跟踪器)

**职责**: 跟踪订单流，统计申报、撤单等数据

**核心方法**:
```python
class OrderTracker:
    def add_order(order: OrderRecord)
    def record_cancel(order_id: str, cancel_time: datetime)
    def get_second_stats(second_timestamp: int) -> Dict
    def get_daily_stats() -> Dict
    def reset_daily()
```

### 4.3 RegulatoryConfig (监管配置)

**职责**: 存储监管参数和阈值

**配置项**:
- 高频交易认定标准
- 撤单限制参数
- 短线交易规则
- 异常行为阈值

### 4.4 数据结构

**OrderRecord (订单记录)**:
```python
@dataclass
class OrderRecord:
    order_id: str
    symbol: str
    direction: str
    quantity: int
    price: float
    order_type: str
    timestamp: datetime
    status: str
    cancel_time: Optional[datetime]
    fill_time: Optional[datetime]
    duration_microseconds: Optional[int]
```

**ComplianceCheckResult (合规检查结果)**:
```python
@dataclass
class ComplianceCheckResult:
    is_compliant: bool
    compliance_level: ComplianceLevel
    behavior_type: TradingBehaviorType
    triggered_rules: List[str]
    warnings: List[str]
    violations: List[str]
    details: Dict
    recommendations: List[str]
```

---

## 5. 接口设计

### 5.1 订单提交前检查接口

```python
def check_order_before_submission(
    self, 
    order: OrderRecord,
    position_pct: float = 0.0,
    last_trade_date: Optional[datetime] = None
) -> ComplianceCheckResult:
    """
    订单提交前合规检查
    
    Args:
        order: 订单记录
        position_pct: 持仓比例
        last_trade_date: 上次交易日期
        
    Returns:
        ComplianceCheckResult: 合规检查结果
    """
```

**使用示例**:
```python
checker = create_compliance_checker()

order = OrderRecord(
    order_id='ORDER_001',
    symbol='000001.SZ',
    direction='buy',
    quantity=1000,
    price=10.5,
    order_type='limit',
    timestamp=datetime.now(),
    status='submitted'
)

result = checker.check_order_before_submission(
    order=order,
    position_pct=0.03,
    last_trade_date=datetime.now() - timedelta(days=30)
)

if not result.is_compliant:
    print(f"订单不合规: {result.violations}")
    # 拒绝订单或采取其他措施
```

### 5.2 实时合规监控接口

```python
def check_abnormal_trading(self) -> ComplianceCheckResult:
    """
    检查异常交易行为
    
    Returns:
        ComplianceCheckResult: 合规检查结果
    """
```

**使用示例**:
```python
# 定期检查（如每分钟）
result = checker.check_abnormal_trading()

if result.compliance_level == ComplianceLevel.WARNING:
    logger.warning(f"合规警告: {result.warnings}")
    
if result.compliance_level == ComplianceLevel.VIOLATION:
    logger.error(f"合规违规: {result.violations}")
    # 触发风控措施
```

### 5.3 合规报告生成接口

```python
def generate_compliance_report(self) -> Dict:
    """
    生成合规报告
    
    Returns:
        Dict: 合规报告字典
    """
```

**使用示例**:
```python
# 每日生成合规报告
report = checker.generate_compliance_report()

print(f"合规率: {report['compliance_summary']['compliance_rate']:.2%}")
print(f"违规次数: {report['compliance_summary']['violation_checks']}")
```

---

## 6. 集成方案

### 6.1 与QMTExecutor集成

**集成位置**: Layer 5 - 策略执行层

**集成方式**:
```python
class QMTExecutor:
    def __init__(self):
        self.compliance_checker = create_compliance_checker()
        
    def submit_order(self, order_data: Dict) -> Result:
        # 1. 创建订单记录
        order = OrderRecord(
            order_id=order_data['order_id'],
            symbol=order_data['symbol'],
            direction=order_data['direction'],
            quantity=order_data['quantity'],
            price=order_data['price'],
            order_type=order_data['order_type'],
            timestamp=datetime.now(),
            status='submitted'
        )
        
        # 2. 合规检查
        compliance_result = self.compliance_checker.check_order_before_submission(
            order=order,
            position_pct=order_data.get('position_pct', 0.0),
            last_trade_date=order_data.get('last_trade_date')
        )
        
        # 3. 根据检查结果决定是否提交
        if not compliance_result.is_compliant:
            logger.error(f"订单不合规: {compliance_result.violations}")
            return Result(success=False, error="订单不合规")
        
        if compliance_result.warnings:
            logger.warning(f"合规警告: {compliance_result.warnings}")
        
        # 4. 提交订单到QMT
        # ... QMT订单提交逻辑 ...
        
        return Result(success=True, data={'order_id': order.order_id})
```

### 6.2 与RiskManager集成

**集成位置**: Layer 5/6 - 风控层

**集成方式**:
```python
class EnhancedRiskManager:
    def __init__(self):
        self.risk_rules = SimpleRiskRules()
        self.compliance_checker = create_compliance_checker()
        
    def check_order(self, order_data: Dict) -> RiskCheckResult:
        # 1. 传统风控检查
        risk_result = self.risk_rules.check_order(
            order_symbol=order_data['symbol'],
            order_quantity=order_data['quantity'],
            ...
        )
        
        # 2. 合规检查
        compliance_result = self.compliance_checker.check_abnormal_trading()
        
        # 3. 综合判断
        allowed = risk_result.allowed and compliance_result.is_compliant
        
        return RiskCheckResult(
            allowed=allowed,
            risk_level=risk_result.risk_level,
            triggered_rules=risk_result.triggered_rules + compliance_result.triggered_rules,
            message=f"{risk_result.message} | {compliance_result.violations}"
        )
```

### 6.3 定时任务集成

**每日重置任务**:
```python
# 在每日开盘前重置合规检查器
def daily_reset_task():
    checker.reset_daily()
    logger.info("合规检查器已重置")
```

**实时监控任务**:
```python
# 每分钟检查一次
def realtime_monitoring_task():
    result = checker.check_abnormal_trading()
    
    if result.compliance_level != ComplianceLevel.COMPLIANT:
        alert_manager.send_alert(
            level=result.compliance_level.value,
            message=result.violations if result.violations else result.warnings
        )
```

---

## 7. 性能要求

### 7.1 响应时间

- **订单提交前检查**: < 10ms
- **实时监控检查**: < 50ms
- **报告生成**: < 500ms

### 7.2 并发处理

- 支持每秒1000次订单检查
- 支持多账户并行检查

### 7.3 内存占用

- 单账户内存占用 < 10MB
- 100个账户总内存占用 < 1GB

---

## 8. 测试方案

### 8.1 单元测试

**测试用例**:
- 高频交易认定测试
- 撤单限制测试
- 短线交易测试
- 异常行为测试

**测试文件**: `tests/test_compliance_checker.py`

### 8.2 集成测试

**测试场景**:
- 与QMTExecutor集成测试
- 与RiskManager集成测试
- 定时任务集成测试

### 8.3 压力测试

**测试指标**:
- 1000 TPS订单检查
- 100个账户并发检查
- 长时间运行稳定性

---

## 9. 部署方案

### 9.1 部署位置

- **代码位置**: `src/modules/compliance_checker.py`
- **配置位置**: `config/compliance_config.yaml`
- **日志位置**: `logs/compliance/`

### 9.2 配置管理

**配置文件**: `config/compliance_config.yaml`

```yaml
compliance:
  high_frequency_criteria:
    per_second_threshold: 300
    per_day_threshold: 20000
    
  cancel_order_limits:
    max_cancel_per_second: 15
    max_cancel_rate_per_day: 0.15
    min_order_duration_microseconds: 50
    
  short_term_trading_rules:
    lock_period_months: 6
    major_shareholder_threshold: 0.05
    
  monitoring:
    enabled: true
    check_interval_seconds: 60
    alert_enabled: true
```

### 9.3 监控告警

**监控指标**:
- 合规检查次数
- 违规次数
- 警告次数
- 合规率

**告警规则**:
- 违规次数 > 0: 立即告警
- 警告次数 > 10: 延迟告警
- 合规率 < 95%: 每日告警

---

## 10. 维护与升级

### 10.1 监管规则更新

**更新流程**:
1. 监管部门发布新规
2. 分析新规影响
3. 更新RegulatoryConfig
4. 测试验证
5. 部署上线

### 10.2 版本管理

**版本号规则**: MAJOR.MINOR.PATCH
- MAJOR: 监管规则重大变更
- MINOR: 新增检查功能
- PATCH: Bug修复

**当前版本**: v1.0.0

---

## 11. 文档与培训

### 11.1 技术文档

- 本技术规格书
- API文档
- 集成指南
- 故障排查手册

### 11.2 使用示例

- 基本使用示例
- 高频交易检查示例
- 撤单限制检查示例
- 短线交易检查示例
- 合规报告示例

**示例文件**: `src/modules/examples/compliance_checker_example.py`

---

## 12. 风险评估

### 12.1 技术风险

| 风险项 | 风险等级 | 缓解措施 |
|-------|---------|---------|
| 性能瓶颈 | 中 | 优化算法，使用缓存 |
| 内存泄漏 | 低 | 定期重置，内存监控 |
| 配置错误 | 中 | 配置验证，默认值保护 |

### 12.2 合规风险

| 风险项 | 风险等级 | 缓解措施 |
|-------|---------|---------|
| 监管规则变更 | 高 | 定期更新，版本管理 |
| 规则理解偏差 | 中 | 专业审核，持续学习 |
| 系统故障 | 中 | 冗余设计，快速恢复 |

---

## 13. 总结

### 13.1 核心价值

- **合规保障**: 确保系统100%符合最新监管要求
- **风险预警**: 实时监控，提前预警合规风险
- **成本降低**: 自动化合规检查，降低人工成本
- **专业提升**: 符合机构级标准，提升系统专业性

### 13.2 实施建议

1. **立即集成**: 将合规检查模块集成到QMTExecutor
2. **定期监控**: 设置定时任务，实时监控合规状态
3. **持续更新**: 关注监管动态，及时更新规则
4. **培训团队**: 确保团队理解合规要求

### 13.3 后续优化

1. **机器学习**: 使用ML优化合规检查算法
2. **规则引擎**: 引入规则引擎，支持动态配置
3. **可视化**: 开发合规监控大屏
4. **API服务**: 提供RESTful API，支持外部调用

---

**文档版本**: v1.0.0
**最后更新**: 2026-04-03
**维护者**: 首席架构师
