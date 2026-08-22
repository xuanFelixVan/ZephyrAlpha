---
module_id: MOD-RPT-008
title: "风险报告引擎蓝图 — 日度/周度/事件/月度4类风险报告生成"
doc_type: blueprint
status: Active
version: "0.1.2"
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

# MOD-RPT-008 Risk Report Engine — 风险报告引擎 蓝图

> **module_id**: MOD-RPT-008 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-010(报告归档/审计)
> **SSoT**: depgraph MOD-RPT-008 | **设计真源**: D:\临时工作区\依赖图\10-D-REPORTING-报告域.md §1.2 D-REPORTING-08, §2.2 CTR-P1-008/CTR-P1-011, §5.1 风险报告

## 1. 定位

风险报告引擎——D_REPORTING 域 P1 基础设施。消费 D-RISK 诊断结果
(RiskDashboardSnapshot + RiskMetricsReport), 生成 4 类风险报告:

1. **日度风险摘要** (DailyRiskSummary): 每日收盘, VaR/CVaR/回撤/杠杆/集中度/告警
2. **周度风险深度** (WeeklyRiskDeep): 每周聚合, 日度趋势 + 周均值/极值
3. **事件风险快报** (EventRiskFlash): 事件触发, 告警详情 + 影响评估 + 处置建议
4. **月度风险治理** (MonthlyRiskGovernance): 每月聚合, 月度统计 + 风险评分分布

属 A 类基础设施(确定性报告生成), 纯消费层不发布事件(D-RPT-D01)。
**纯基础设施: 不做风险诊断, 只负责"消费诊断结果→生成报告"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | RiskDashboardSnapshot (CTR-P1-008) | VaR/回撤/杠杆/集中度/告警 |
| 输入 | RiskMetricsReport (CTR-P1-011) | VaR/CVaR/Sharpe/Sortino/Beta/波动率 |
| 输出 | DailyRiskSummary | 日度风险摘要报告 |
| 输出 | WeeklyRiskDeep | 周度风险深度报告 |
| 输出 | EventRiskFlash | 事件风险快报 |
| 输出 | MonthlyRiskGovernance | 月度风险治理报告 |

## 3. 核心规则

### 3.1 日度风险摘要 (DailyRiskSummary)

- 数据源: 1 个 RiskDashboardSnapshot + 1 个 RiskMetricsReport
- 字段: report_date / portfolio_id / var_1d_95 / var_1d_99 / cvar_1d_95 / cvar_1d_99 /
  current_drawdown / max_drawdown / gross_leverage / top_position_concentration /
  overall_risk_score / sharpe_ratio / sortino_ratio / beta / volatility_1d /
  sector_concentrations / active_alerts / alert_count
- 风险等级判定: overall_risk_score <0.3=LOW / 0.3-0.6=MEDIUM / 0.6-0.8=HIGH / >0.8=CRITICAL
  （分级/趋势阈值默认值真源=alert_threshold_registry.yaml THD-REPORT-001~004，fail-closed 统读，2026-08-17 AI-THD-001；构造传参可覆盖）

### 3.2 事件风险快报 (EventRiskFlash)

- 触发: RiskDashboardSnapshot.active_alerts 非空时生成
- 字段: event_time / portfolio_id / alert_messages / impact_assessment / recommendations
- 影响评估: 基于 overall_risk_score + alert_count 量化影响等级
- 处置建议: 按 risk_level 给出标准化建议(LOW=监控/MEDIUM=审查/HIGH=减仓/CRITICAL=止损)

### 3.3 周度风险深度 (WeeklyRiskDeep)

- 数据源: 一周(≤7天)的 DailyRiskSummary 列表
- 字段: week_start / week_end / portfolio_id / daily_count / avg_var_1d_95 /
  max_var_1d_95 / min_var_1d_95 / avg_drawdown / max_drawdown / avg_risk_score /
  max_risk_score / trend_direction (上升/下降/平稳) / alert_total
- 趋势判定: 比较 week 前半段 vs 后半段 avg_risk_score

### 3.4 月度风险治理 (MonthlyRiskGovernance)

- 数据源: 一个月的 DailyRiskSummary 列表
- 字段: month / portfolio_id / trading_days / avg_var_1d_95 / max_var_1d_99 /
  avg_drawdown / max_drawdown / avg_risk_score / risk_score_distribution /
  total_alerts / high_risk_days / critical_risk_days
- 风险评分分布: 按 LOW/MEDIUM/HIGH/CRITICAL 统计天数

## 4. 数据模型

```python
class RiskLevel(str, Enum):
    LOW = "LOW"          # overall_risk_score < 0.3
    MEDIUM = "MEDIUM"    # 0.3 <= score < 0.6
    HIGH = "HIGH"        # 0.6 <= score < 0.8
    CRITICAL = "CRITICAL"  # score >= 0.8

class TrendDirection(str, Enum):
    RISING = "RISING"
    FALLING = "FALLING"
    STABLE = "STABLE"

@dataclass(frozen=True)
class DailyRiskSummary:
    report_id: str
    report_date: str          # YYYY-MM-DD
    portfolio_id: str
    risk_level: RiskLevel
    var_1d_95: float
    var_1d_99: float
    cvar_1d_95: float
    cvar_1d_99: float
    current_drawdown: float
    max_drawdown: float
    gross_leverage: float
    top_position_concentration: float
    overall_risk_score: float
    sharpe_ratio: float
    sortino_ratio: float
    beta: float
    volatility_1d: float
    sector_concentrations: dict[str, float]
    active_alerts: list[str]
    alert_count: int
    generated_at: datetime
    schema_version: str = "1.0"

@dataclass(frozen=True)
class EventRiskFlash:
    report_id: str
    event_time: datetime
    portfolio_id: str
    risk_level: RiskLevel
    alert_messages: list[str]
    alert_count: int
    overall_risk_score: float
    impact_assessment: str
    recommendations: list[str]
    schema_version: str = "1.0"

@dataclass(frozen=True)
class WeeklyRiskDeep:
    report_id: str
    week_start: str
    week_end: str
    portfolio_id: str
    daily_count: int
    avg_var_1d_95: float
    max_var_1d_95: float
    min_var_1d_95: float
    avg_drawdown: float
    max_drawdown: float
    avg_risk_score: float
    max_risk_score: float
    trend_direction: TrendDirection
    alert_total: int
    generated_at: datetime
    schema_version: str = "1.0"

@dataclass(frozen=True)
class MonthlyRiskGovernance:
    report_id: str
    month: str                # YYYY-MM
    portfolio_id: str
    trading_days: int
    avg_var_1d_95: float
    max_var_1d_99: float
    avg_drawdown: float
    max_drawdown: float
    avg_risk_score: float
    risk_score_distribution: dict[str, int]  # RiskLevel → days
    total_alerts: int
    high_risk_days: int
    critical_risk_days: int
    generated_at: datetime
    schema_version: str = "1.0"
```

## 5. API

```python
class RiskReportEngine:
    def __init__(self) -> None: ...

    def generate_daily(
        self, snapshot: RiskDashboardSnapshot, metrics: RiskMetricsReport
    ) -> DailyRiskSummary: ...

    def generate_event_flash(
        self, snapshot: RiskDashboardSnapshot
    ) -> EventRiskFlash | None: ...

    def generate_weekly(
        self, daily_summaries: list[DailyRiskSummary]
    ) -> WeeklyRiskDeep: ...

    def generate_monthly(
        self, daily_summaries: list[DailyRiskSummary]
    ) -> MonthlyRiskGovernance: ...
```

## 6. 依赖

| 依赖 | 类型 | 契约 | 就绪 |
|------|------|------|------|
| RiskDashboardSnapshot | contract | CTR-P1-008 | ✓ production |
| RiskMetricsReport | contract | CTR-P1-011 | ✓ production |
| errors foundation | import_depends | ZephyrBaseError | ✓ production |

## 7. 阶段划分

| 阶段 | 内容 | 状态 |
|------|------|------|
| 阶段1 | 4类报告基础版(本实现) | ✅ |
| 阶段2 | 压力测试/漂移趋势/策略拥挤度/模型健康度 | 待定 |

## 8. 合规对标

- §4.2 审计日志: 风险报告纳入审计链(≥7年), 哈希链防篡改
- §5.1 风险报告: 4类报告对标(日度/周度/事件/月度)
- §5.2 风控审计: 否决日志/参数变更/Kill Switch/漂移检测纳入月度治理

## 9. 测试计划

- 日度报告: 字段映射正确 / risk_level 判定 / 空告警 / 多告警
- 事件快报: 有告警生成 / 无告警返回None / 影响评估 / 处置建议
- 周度报告: 聚合计算 / 趋势判定(上升/下降/平稳) / 空列表边界
- 月度报告: 分布统计 / high/critical天数 / 空列表边界
- frozen不可变 / Decimal精度 / 边界值

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RPT-008`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RPT-008` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RPT-008` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RPT-008 | MOD-RPT-008 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/reporting/risk_report_engine.py` | ✅ 已实现 | |

### 10.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/reporting/test_risk_report_engine.py` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


