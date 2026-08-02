---
module_id: MOD-RPT-006
title: "监管报告生成器蓝图 — 4类监管报告+数据完整性校验+哈希指纹"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L07_reporting
layer_name: reporting
functional_domain: reporting
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RPT-006 Regulatory Report Generator — 监管报告生成器 蓝图

> **module_id**: MOD-RPT-006 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-010(报告归档/审计)
> **SSoT**: depgraph MOD-RPT-006 | **设计真源**: D:\临时工作区\依赖图\10-D-REPORTING-报告域.md §1.2 D-REPORTING-06, §4.8 监管报送

## 1. 定位

监管报告生成器——生成证监会/交易所要求的 4 类监管报告（基础版, 手动生成）:
1. **程序化交易报告**: 一次性+变更, 合规架构信息
2. **异常交易自报**: 事件驱动, 异常交易行为记录
3. **持仓报告**: 月/季, 持仓结构/集中度/行业偏离
4. **绩效报告**: 季/年, 收益/风险/归因摘要

基础版不含自动化报送接口（受 GATE-002/GATE-003 门禁）。
属 A 类基础设施(确定性报告生成), 纯消费层不发布事件。

## 2. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | 报告类型 + 报告期 + 结构化数据(持仓/交易/绩效) |
| 输出 | RegulatoryReport (含 content + data_hash 完整性指纹) |

## 3. 核心规则

### 3.1 报告类型

| 类型 | 频率 | 必填内容 |
|------|------|---------|
| programmatic_trading | 一次性+变更 | 策略架构/参数/风控规则 |
| abnormal_trading | 事件驱动 | 异常事件/触发条件/处置动作 |
| position | 月/季 | 持仓结构/集中度/行业偏离 |
| performance | 季/年 | 收益率/最大回撤/Sharpe/归因摘要 |

### 3.2 数据完整性

- data_hash = SHA-256(canonical_json(content)) 防篡改
- validate_report 重算 data_hash 比对
- 必填字段缺失拒绝

### 3.3 阶段划分

| 阶段 | 内容 | 状态 |
|------|------|------|
| 阶段1 | 4类报告基础版(手动生成+完整性校验) | ✅ |
| 阶段2 | 自动化报送接口(券商/监管API) | ❌GATE-002/003 |

## 4. 数据模型

```python
class ReportType(str, Enum):
    PROGRAMMATIC_TRADING = "programmatic_trading"
    ABNORMAL_TRADING = "abnormal_trading"
    POSITION = "position"
    PERFORMANCE = "performance"

@dataclass(frozen=True)
class RegulatoryReport:
    report_id: str
    report_type: ReportType
    reporting_period: str
    portfolio_id: str
    generated_at: datetime
    content: dict
    data_hash: str
    schema_version: str = "1.0"
```

## 5. API

```python
class RegulatoryReportGenerator:
    def generate_programmatic_trading(portfolio_id, period, strategies, risk_rules) -> RegulatoryReport
    def generate_abnormal_trading(portfolio_id, period, events) -> RegulatoryReport
    def generate_position(portfolio_id, period, holdings) -> RegulatoryReport
    def generate_performance(portfolio_id, period, metrics) -> RegulatoryReport
    def validate_report(report) -> bool
```

## 6. 依赖

| 依赖 | 类型 | 就绪 |
|------|------|------|
| errors foundation | import_depends | ✓ production |

## 7. 测试计划

- 4类报告生成: 字段正确 / data_hash 计算
- 完整性校验: 内容匹配 / 篡改检测
- 必填字段: 缺字段拒绝
- frozen不可变 / 边界值
