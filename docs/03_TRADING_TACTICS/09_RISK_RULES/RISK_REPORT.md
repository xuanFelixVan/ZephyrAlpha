﻿---
module_id: RISK_REPORT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 交易策略、战术执行

---
---

---
module_id: TACTICS_RISK_REPORT_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 因子计算
  - 组合优化
  - 交易执行
standard_type: 专业量化机构文档
applicable_scope: 全系?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?---



# 风险报告生成器蓝?
> **核心职责**: 分析报告和评估结果
> **职责边界**: 
> - ✅ 本文档负责：分析报告和评估结果相关内容
> - ❌ 本文档不负责：其他模块内容


> 清风量化系统 v5.0 - 风险报告生成?
> **索引**: `RISK.RPT.001`
> **开发时?*: 6h
> **核心定位**: 生成定期和按需的风险报告，支持?监督)决策


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **自动?* | 日报自动生成，周报月报按需 |
| **可视?* | 关键指标图表化，一目了?|
| **可追?* | 历史报告存档，支持对?|
| **分层** | 摘要+详情，满足不同阅读需?|


## 2. 报告类型

### 2.1 报告分类

| 类型 | 频率 | 受众 | 生成时间 |
|------|------|------|----------|
| **日报** | 每日收盘?| 全部 | 16:00自动 |
| **周报** | 每周五收盘后 | 全部 | 16:30自动 |
| **月报** | 每月最后一个交易日 | 全部 | 收盘?|
| **实时告警** | 触发?| 风控人员 | 实时 |
| **专题报告** | 按需 | 指定人员 | 手动触发 |


## 3. 核心实现

### 3.1 报告生成?

```python
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from enum import Enum
import pandas as pd

class ReportType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALERT = "alert"
    SPECIAL = "special"

class ReportFormat(Enum):
    HTML = "html"
    PDF = "pdf"
    MARKDOWN = "markdown"
    JSON = "json"

@dataclass
class RiskMetrics:
    """风险指标

    索引: RISK.RPT.001-D01
    """
    date: date
    portfolio_value: float
    daily_return: float
    cumulative_return: float
    volatility: float
    max_drawdown: float
    var_95: float
    cvar_95: float
    sharpe_ratio: float
    sortino_ratio: float

@dataclass
class PositionRisk:
    """持仓风险

    索引: RISK.RPT.001-D02
    """
    symbol: str
    quantity: int
    market_value: float
    weight: float
    daily_return: float
    contribution: float
    var: float

@dataclass
class RiskAlert:
    """风险告警

    索引: RISK.RPT.001-D03
    """
    alert_id: str
    timestamp: datetime
    severity: str
    rule_id: str
    message: str
    action_taken: str

class RiskReportGenerator:
    """风险报告生成?

    索引: RISK.RPT.001-M01
    上游: RiskManager, PositionManager
    下游: ReportStorage, NotificationSystem
    """

    def __init__(self, config: Dict):
        self.config = config
        self.template_dir = config.get('template_dir', 'templates/risk')
        self.output_dir = config.get('output_dir', 'reports/risk')

    def generate_daily_report(self, trading_date: date) -> RiskReport:
        """生成日报

        参数:
            trading_date: 交易日期

        返回:
            RiskReport: 风险报告
        """
        report_date = pd.Timestamp(trading_date)

        metrics = self._calculate_daily_metrics(report_date)
        positions = self._get_position_risks(report_date)
        alerts = self._get_daily_alerts(report_date)
        events = self._get_significant_events(report_date)

        content = self._build_daily_content(metrics, positions, alerts, events)
        summary = self._generate_summary(metrics, alerts)

        return RiskReport(
            report_type=ReportType.DAILY,
            report_date=trading_date,
            title=f"风险日报 - {trading_date.strftime('%Y-%m-%d')}",
            summary=summary,
            content=content,
            metrics=metrics,
            positions=positions,
            alerts=alerts
        )

    def generate_weekly_report(self, week_ending: date) -> RiskReport:
        """生成周报

        参数:
            week_ending: 周结束日?通常为周?

        返回:
            RiskReport: 风险报告
        """
        start_date = week_ending - pd.Timedelta(days=6)

        metrics = self._calculate_weekly_metrics(start_date, week_ending)
        positions = self._get_position_risks(pd.Timestamp(week_ending))
        alerts = self._get_period_alerts(start_date, week_ending)
        attribution = self._calculate_weekly_attribution(start_date, week_ending)

        content = self._build_weekly_content(metrics, positions, alerts, attribution)
        summary = self._generate_weekly_summary(metrics)

        return RiskReport(
            report_type=ReportType.WEEKLY,
            report_date=week_ending,
            title=f"风险周报 - {start_date.strftime('%Y-%m-%d')} ~ {week_ending.strftime('%Y-%m-%d')}",
            summary=summary,
            content=content,
            metrics=metrics,
            positions=positions,
            alerts=alerts,
            attribution=attribution
        )

    def _calculate_daily_metrics(self, report_date: pd.Timestamp) -> RiskMetrics:
        """计算日度风险指标

        参数:
            report_date: 报告日期

        返回:
            RiskMetrics: 日度风险指标
        """
        portfolio_value = self._get_portfolio_value(report_date)
        daily_return = self._get_daily_return(report_date)
        cumulative_return = self._get_cumulative_return(report_date)
        volatility = self._calculate_volatility(report_date, window=20)
        max_drawdown = self._calculate_max_drawdown(report_date)
        var_95 = self._calculate_var(report_date, confidence=0.95)
        cvar_95 = self._calculate_cvar(report_date, confidence=0.95)
        sharpe = self._calculate_sharpe_ratio(report_date)
        sortino = self._calculate_sortino_ratio(report_date)

        return RiskMetrics(
            date=report_date.date(),
            portfolio_value=portfolio_value,
            daily_return=daily_return,
            cumulative_return=cumulative_return,
            volatility=volatility,
            max_drawdown=max_drawdown,
            var_95=var_95,
            cvar_95=cvar_95,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino
        )
```

### 3.2 VaR/CVaR计算

```python
class VaRCalculator:
    """VaR/CVaR计算?

    索引: RISK.RPT.001-M02
    """

    def calculate_historical_var(
        self,
        returns: pd.Series,
        confidence: float = 0.95,
        horizon: int = 1
    ) -> float:
        """历史法VaR计算

        参数:
            returns: 收益率序?
            confidence: 置信?
            horizon: 持有?

        返回:
            VaR?
        """
        if horizon > 1:
            returns = returns * np.sqrt(horizon)

        var_percentile = (1 - confidence) * 100
        var = np.percentile(returns, var_percentile)
        return abs(var)

    def calculate_parametric_var(
        self,
        returns: pd.Series,
        confidence: float = 0.95,
        horizon: int = 1
    ) -> float:
        """参数法VaR计算(方差-协方差法)

        参数:
            returns: 收益率序?
            confidence: 置信?
            horizon: 持有?

        返回:
            VaR?
        """
        mean = returns.mean()
        std = returns.std()

        if horizon > 1:
            std = std * np.sqrt(horizon)

        z_score = scipy.stats.norm.ppf(1 - confidence)
        var = mean - z_score * std
        return abs(var)

    def calculate_monte_carlo_var(
        self,
        returns: pd.Series,
        confidence: float = 0.95,
        simulations: int = 10000,
        horizon: int = 1
    ) -> float:
        """蒙特卡洛VaR计算

        参数:
            returns: 收益率序?
            confidence: 置信?
            simulations: 模拟次数
            horizon: 持有?

        返回:
            VaR?
        """
        mean = returns.mean()
        std = returns.std()

        simulated_returns = np.random.normal(mean, std, simulations * horizon)
        if horizon > 1:
            simulated_returns = simulated_returns.reshape(simulations, horizon).sum(axis=1)

        var_percentile = (1 - confidence) * 100
        var = np.percentile(simulated_returns, var_percentile)
        return abs(var)

    def calculate_cvar(
        self,
        returns: pd.Series,
        confidence: float = 0.95
    ) -> float:
        """CVaR计算(条件VaR, Expected Shortfall)

        参数:
            returns: 收益率序?
            confidence: 置信?

        返回:
            CVaR?
        """
        var = self.calculate_historical_var(returns, confidence)
        cvar = returns[returns <= -var].mean()
        return abs(cvar) if not np.isnan(cvar) else var
```


## 4. 报告模板

### 4.1 日报模板

```markdown
# 风险日报

**报告日期**: {{ date }}
**生成时间**: {{ generated_at }}


## 一、概?

| 指标 | 今日 | 昨日 | 变化 |
|------|------|------|------|
| 组合净?| {{ portfolio_value }} | {{ prev_value }} | {{ change }} |
| 日收益率 | {{ daily_return }}% | {{ prev_return }}% | - |
| 最大回?| {{ max_drawdown }}% | - | - |
| VaR(95%) | {{ var_95 }}% | - | - |
| 夏普比率 | {{ sharpe_ratio }} | - | - |

## 二、仓位风?

| 股票 | 持仓?| 市?| 权重 | 日涨?| 贡献 |
|------|--------|------|------|--------|------|
{{ positions_table }}

## 三、告警事?

{{ if alerts }}
| 时间 | 级别 | 规则 | 描述 | 处理 |
|------|------|------|------|------|
{{ alerts_table }}
{{ else }}
今日无告警事件?
{{ endif }}

## 四、风险提?

{{ risk_notes }}


*本报告由清风量化交易系统自动生成*
```


## 5. 报告存储

### 5.1 存储结构

```python
# reports/risk/
# ├── 2026/
# ?  ├── 03/
# ?  ?  ├── daily_2026-03-01.html
# ?  ?  ├── daily_2026-03-02.html
# ?  ?  ├── weekly_2026-03-07.html
# ?  ?  └── monthly_2026-03.html
# ?  └── 04/
# └── index.json  # 报告索引
```

### 5.2 报告索引

```python
@dataclass
class ReportIndex:
    """报告索引

    索引: RISK.RPT.001-D04
    """
    reports: List[ReportSummary] = field(default_factory=list)

    def add_report(self, report: RiskReport):
        """添加报告到索?""
        self.reports.append(ReportSummary(
            report_id=report.report_id,
            report_type=report.report_type.value,
            report_date=report.report_date,
            file_path=self._get_file_path(report)
        ))

    def get_reports(
        self,
        report_type: Optional[ReportType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ReportSummary]:
        """查询报告"""
        results = self.reports

        if report_type:
            results = [r for r in results if r.report_type == report_type.value]

        if start_date:
            results = [r for r in results if r.report_date >= start_date]

        if end_date:
            results = [r for r in results if r.report_date <= end_date]

        return results
```


## 6. 集成接口

### 6.1 上游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| RiskManager | get_risk_metrics() | 获取风险指标 |
| PositionManager | get_positions() | 获取持仓 |
| AlertManager | get_alerts() | 获取告警 |
| DataHub | get_market_data() | 获取市场数据 |

### 6.2 下游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| NotificationSystem | send_report() | 发送报?|
| ReportStorage | save() | 存储报告 |
| Dashboard | display() | 展示报告 |


## 7. 监控指标

| 指标 | 说明 | 阈?|
|------|------|------|
| report_generation_time | 报告生成耗时 | <60s |
| report_delivery_time | 报告送达时间 | <5min |
| report_accuracy | 报告数据准确?| >99% |


## 8. 开发任务分?6h)

| 任务 | 时间 | 交付?|
|------|------|--------|
| VaR/CVaR计算?| 1.5h | VaRCalculator |
| 报告生成?| 1.5h | RiskReportGenerator |
| 报告模板 | 1h | markdown模板 |
| 报告存储 | 1h | ReportStorage |
| 邮件/通知集成 | 0.5h | NotificationSystem |
| 单元测试 | 0.5h | test_risk_report.py |


**维护?*: 清风量化系统
**索引**: `RISK.RPT.001`
**最后更?*: 2026-03-29
