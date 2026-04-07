---
module_id: GOVERNANCE_DASHBOARD_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
responsibility:
  - 数据质量
  - 因子计算
  - 组合优化
layer: Layer 10 (治理与合规层)
standard_type: 专业量化机构级蓝图
applicable_scope: 治理仪表板系统
compliance_level: 顶级专业标准
reference_models: ["Bridgewater Governance Dashboard", "Citadel Compliance Dashboard", "Two Sigma Risk Dashboard"]
related_documents:
  - GRAFANA_MONITORING_BLUEPRINT.md
  - REALTIME_RISK_MONITORING_BLUEPRINT.md
  - COMPLIANCE_MONITORING_SYSTEM_BLUEPRINT.md
parent_document: ../LAYER_10_GOVERNANCE_COMPLIANCE_INDEX.md
implementation_status: 蓝图设计完成
open_source_projects:
  - name: Grafana
    url: https://github.com/grafana/grafana
    features: 可视化仪表板、实时监控、告警系统
  - name: Streamlit
    url: https://github.com/streamlit/streamlit
    features: 快速仪表板开发、交互式可视化
  - name: Plotly Dash
    url: https://github.com/plotly/dash
    features: 企业级仪表板、实时更新
responsibility_boundary: |
  **本文档职责（Layer 10 治理与合规层）**：
  - 治理状态可视化（实时治理状态、关键指标）
  - 治理指标监控（治理指标采集、指标分析）
  - 治理预警机制（治理异常预警、预警响应）
  - 治理报告展示（治理报告可视化、报告导出）
  
  **与本文档职责边界**：
  - GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md: Layer 10总体架构设计
  - GRAFANA_MONITORING_BLUEPRINT.md: Grafana监控系统
  - REALTIME_RISK_MONITORING_BLUEPRINT.md: 实时风险监控
  - COMPLIANCE_MONITORING_SYSTEM_BLUEPRINT.md: 合规监控系统
---
---


# 治理仪表板系统蓝图
> **核心职责**: Governance Dashboard蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Governance Dashboard蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v1.0.0
> **创建日期**: 2026-04-06
> **实施周期**: 3天
> **开源项目**: Grafana + Streamlit
> **目标**: 构建专业级治理仪表板系统，实时展示治理状态

---

## 📋 执行摘要

### 核心定位

治理仪表板系统是清风量化系统的**治理可视化中枢**，负责：
- 治理状态可视化（实时治理状态、关键指标）
- 治理指标监控（治理指标采集、指标分析）
- 治理预警机制（治理异常预警、预警响应）
- 治理报告展示（治理报告可视化、报告导出）

### 个人使用价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评分 |
|---------|-------------|-------------|---------|
| **治理可视化** | 专业团队 | Grafana + AI配置 | ⭐⭐⭐⭐⭐ |
| **实时监控** | 专业团队 | AI自动监控+告警 | ⭐⭐⭐⭐⭐ |
| **预警机制** | 专业团队 | AI自动预警+建议 | ⭐⭐⭐⭐⭐ |
| **报告展示** | 专业团队 | AI自动生成报告 | ⭐⭐⭐⭐ |

**综合价值评分**: ⭐⭐⭐⭐⭐ (5/5) - **强烈推荐实施**

---

## 一、架构设计

### 1.1 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                 治理仪表板系统架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │             1. 治理指标采集层                              │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 风险指标采集 (Risk Metrics Collection)             │ │ │
│  │  │  ├── 市场风险指标（VaR、波动率、回撤）             │ │ │
│  │  │  ├── 流动性风险指标（LCR、清算时间）               │ │ │
│  │  │  ├── 信用风险指标（交易对手风险、CVA）             │ │ │
│  │  │  └── 操作风险指标（操作风险事件）                  │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 合规指标采集 (Compliance Metrics Collection)       │ │ │
│  │  │  ├── 合规检查通过率（合规检查通过率）              │ │ │
│  │  │  ├── 合规事件数量（合规事件统计）                  │ │ │
│  │  │  ├── 合规报告状态（报告生成状态）                  │ │ │
│  │  │  └── 合规审计状态（审计追踪状态）                  │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 绩效指标采集 (Performance Metrics Collection)      │ │ │
│  │  │  ├── 收益率指标（总收益、超额收益）                │ │ │
│  │  │  ├── 风险调整收益（夏普比率、索提诺比率）          │ │ │
│  │  │  ├── 绩效归因（收益归因、风险归因）                │ │ │
│  │  │  └── 因子绩效（因子IC、因子收益）                  │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ AI治理指标采集 (AI Governance Metrics Collection)  │ │ │
│  │  │  ├── AI决策准确率（AI决策准确率）                  │ │ │
│  │  │  ├── AI可解释性（AI决策可解释性）                  │ │ │
│  │  │  ├── AI信任度（AI信任度评分）                      │ │ │
│  │  │  └── AI错误率（AI错误率统计）                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │             2. 治理指标处理层                              │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 指标聚合 (Metrics Aggregation)                     │ │ │
│  │  │  ├── 时间聚合（分钟、小时、日、周、月）            │ │ │
│  │  │  ├── 维度聚合（按策略、按资产、按因子）            │ │ │
│  │  │  ├── 统计聚合（均值、方差、分位数）                │ │ │
│  │  │  └── 趋势聚合（趋势分析、变化率）                  │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 指标分析 (Metrics Analysis)                        │ │ │
│  │  │  ├── 异常检测（指标异常检测）                      │ │ │
│  │  │  ├── 趋势分析（指标趋势分析）                      │ │ │
│  │  │  ├── 对比分析（指标对比分析）                      │ │ │
│  │  │  └── 预测分析（指标预测分析）                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 指标评分 (Metrics Scoring)                         │ │ │
│  │  │  ├── 治理健康评分（综合治理健康评分）              │ │ │
│  │  │  ├── 风险评分（风险评分）                          │ │ │
│  │  │  ├── 合规评分（合规评分）                          │ │ │
│  │  │  └── 绩效评分（绩效评分）                          │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │             3. 治理可视化层                                │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 实时仪表板 (Real-time Dashboard)                   │ │ │
│  │  │  ├── 治理概览仪表板（治理状态概览）                │ │ │
│  │  │  ├── 风险监控仪表板（风险实时监控）                │ │ │
│  │  │  ├── 合规监控仪表板（合规实时监控）                │ │ │
│  │  │  └── 绩效监控仪表板（绩效实时监控）                │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 历史仪表板 (Historical Dashboard)                  │ │ │
│  │  │  ├── 历史趋势仪表板（历史趋势分析）                │ │ │
│  │  │  ├── 历史对比仪表板（历史对比分析）                │ │ │
│  │  │  ├── 历史事件仪表板（历史事件分析）                │ │ │
│  │  │  └── 历史报告仪表板（历史报告查看）                │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 预警仪表板 (Alert Dashboard)                       │ │ │
│  │  │  ├── 预警概览仪表板（预警状态概览）                │ │ │
│  │  │  ├── 预警历史仪表板（预警历史记录）                │ │ │
│  │  │  ├── 预警分析仪表板（预警统计分析）                │ │ │
│  │  │  └── 预警响应仪表板（预警响应追踪）                │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │             4. 治理预警机制层                              │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 预警规则引擎 (Alert Rule Engine)                   │ │ │
│  │  │  ├── 阈值预警（指标阈值预警）                      │ │ │
│  │  │  ├── 趋势预警（趋势异常预警）                      │ │ │
│  │  │  ├── 异常预警（异常检测预警）                      │ │ │
│  │  │  └── 组合预警（多指标组合预警）                    │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 预警通知系统 (Alert Notification System)           │ │ │
│  │  │  ├── 邮件通知（邮件预警通知）                      │ │ │
│  │  │  ├── 短信通知（短信预警通知）                      │ │ │
│  │  │  ├── 推送通知（推送预警通知）                      │ │ │
│  │  │  └── Webhook通知（Webhook预警通知）                │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 预警响应系统 (Alert Response System)               │ │ │
│  │  │  ├── 预警确认（预警确认机制）                      │ │ │
│  │  │  ├── 预警处理（预警处理流程）                      │ │ │
│  │  │  ├── 预警追踪（预警追踪记录）                      │ │ │
│  │  │  └── 预警分析（预警统计分析）                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │             5. 治理报告展示层                              │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 报告可视化 (Report Visualization)                  │ │ │
│  │  │  ├── 日报展示（日报可视化展示）                    │ │ │
│  │  │  ├── 周报展示（周报可视化展示）                    │ │ │
│  │  │  ├── 月报展示（月报可视化展示）                    │ │ │
│  │  │  └── 自定义报告（自定义报告展示）                  │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 报告导出 (Report Export)                           │ │ │
│  │  │  ├── PDF导出（PDF格式导出）                        │ │ │
│  │  │  ├── Excel导出（Excel格式导出）                    │ │ │
│  │  │  ├── CSV导出（CSV格式导出）                        │ │ │
│  │  │  └── 图片导出（图片格式导出）                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 报告分享 (Report Sharing)                          │ │ │
│  │  │  ├── 链接分享（链接分享报告）                      │ │ │
│  │  │  ├── 邮件分享（邮件分享报告）                      │ │ │
│  │  │  ├── 定时发送（定时发送报告）                      │ │ │
│  │  │  └── 权限控制（报告访问权限控制）                  │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、核心组件详细设计

### 2.1 治理指标采集层

#### 2.1.1 风险指标采集

**核心职责**：
1. **市场风险指标**：VaR、波动率、回撤
2. **流动性风险指标**：LCR、清算时间
3. **信用风险指标**：交易对手风险、CVA
4. **操作风险指标**：操作风险事件

**技术实现**：
```python
from typing import Dict
import pandas as pd
import numpy as np

class RiskMetricsCollector:
    """风险指标采集器"""
    
    def __init__(self):
        pass
        
    def collect_risk_metrics(self, portfolio_data: Dict) -> Dict:
        """采集风险指标"""
        return {
            'market_risk': self._collect_market_risk(portfolio_data),
            'liquidity_risk': self._collect_liquidity_risk(portfolio_data),
            'credit_risk': self._collect_credit_risk(portfolio_data),
            'operational_risk': self._collect_operational_risk(portfolio_data)
        }
    
    def _collect_market_risk(self, data: Dict) -> Dict:
        """采集市场风险指标"""
        returns = data.get('returns', pd.Series())
        
        return {
            'var_95': np.percentile(returns, 5),
            'volatility': returns.std(),
            'max_drawdown': self._calculate_max_drawdown(returns)
        }
    
    def _collect_liquidity_risk(self, data: Dict) -> Dict:
        """采集流动性风险指标"""
        return {
            'lcr': data.get('liquidity_coverage_ratio', 0),
            'liquidation_time': data.get('liquidation_time', 0)
        }
    
    def _collect_credit_risk(self, data: Dict) -> Dict:
        """采集信用风险指标"""
        return {
            'counterparty_risk': data.get('counterparty_risk', 0),
            'cva': data.get('credit_value_adjustment', 0)
        }
    
    def _collect_operational_risk(self, data: Dict) -> Dict:
        """采集操作风险指标"""
        return {
            'operational_events': data.get('operational_events', 0),
            'loss_events': data.get('loss_events', 0)
        }
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """计算最大回撤"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
```

---

### 2.2 治理可视化层

#### 2.2.1 实时仪表板

**核心职责**：
1. **治理概览仪表板**：治理状态概览
2. **风险监控仪表板**：风险实时监控
3. **合规监控仪表板**：合规实时监控
4. **绩效监控仪表板**：绩效实时监控

**技术实现（Grafana）**：
```python
import grafana_api

class GrafanaDashboardManager:
    """Grafana仪表板管理器"""
    
    def __init__(self, grafana_url: str, api_key: str):
        self.grafana = grafana_api.GrafanaFace(
            host=grafana_url,
            api_key=api_key
        )
        
    def create_governance_dashboard(self) -> Dict:
        """创建治理概览仪表板"""
        dashboard = {
            "dashboard": {
                "title": "治理概览仪表板",
                "panels": [
                    self._create_governance_health_panel(),
                    self._create_risk_score_panel(),
                    self._create_compliance_score_panel(),
                    self._create_performance_score_panel()
                ]
            },
            "overwrite": True
        }
        
        return self.grafana.dashboard.update_dashboard(dashboard)
    
    def _create_governance_health_panel(self) -> Dict:
        """创建治理健康面板"""
        return {
            "title": "治理健康评分",
            "type": "gauge",
            "datasource": "Prometheus",
            "targets": [
                {
                    "expr": "governance_health_score",
                    "legendFormat": "健康评分"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "min": 0,
                    "max": 100,
                    "unit": "percent"
                }
            }
        }
    
    def _create_risk_score_panel(self) -> Dict:
        """创建风险评分面板"""
        return {
            "title": "风险评分",
            "type": "stat",
            "datasource": "Prometheus",
            "targets": [
                {
                    "expr": "risk_score",
                    "legendFormat": "风险评分"
                }
            ]
        }
    
    def _create_compliance_score_panel(self) -> Dict:
        """创建合规评分面板"""
        return {
            "title": "合规评分",
            "type": "stat",
            "datasource": "Prometheus",
            "targets": [
                {
                    "expr": "compliance_score",
                    "legendFormat": "合规评分"
                }
            ]
        }
    
    def _create_performance_score_panel(self) -> Dict:
        """创建绩效评分面板"""
        return {
            "title": "绩效评分",
            "type": "stat",
            "datasource": "Prometheus",
            "targets": [
                {
                    "expr": "performance_score",
                    "legendFormat": "绩效评分"
                }
            ]
        }
```

---

## 三、开源项目集成方案

### 3.1 Grafana集成

**Grafana核心功能**：
- 可视化仪表板
- 实时监控
- 告警系统

**集成方案**：
```python
from grafana_api import GrafanaFace
import json

class GrafanaIntegration:
    """Grafana集成"""
    
    def __init__(self, grafana_url: str, api_key: str):
        self.grafana = GrafanaFace(
            host=grafana_url,
            api_key=api_key
        )
        
    def setup_governance_dashboards(self):
        """设置治理仪表板"""
        # 创建数据源
        self._create_datasources()
        
        # 创建仪表板
        self._create_dashboards()
        
        # 设置告警规则
        self._setup_alert_rules()
    
    def _create_datasources(self):
        """创建数据源"""
        datasources = [
            {
                "name": "Prometheus",
                "type": "prometheus",
                "url": "http://localhost:9090"
            },
            {
                "name": "PostgreSQL",
                "type": "postgres",
                "url": "localhost:5432"
            }
        ]
        
        for ds in datasources:
            self.grafana.datasource.create_datasource(ds)
    
    def _create_dashboards(self):
        """创建仪表板"""
        dashboards = [
            "governance_overview",
            "risk_monitoring",
            "compliance_monitoring",
            "performance_monitoring"
        ]
        
        for db in dashboards:
            self._create_dashboard_from_template(db)
    
    def _create_dashboard_from_template(self, dashboard_name: str):
        """从模板创建仪表板"""
        with open(f"templates/{dashboard_name}.json", "r") as f:
            dashboard = json.load(f)
        
        self.grafana.dashboard.update_dashboard({
            "dashboard": dashboard,
            "overwrite": True
        })
    
    def _setup_alert_rules(self):
        """设置告警规则"""
        alert_rules = [
            {
                "name": "治理健康评分过低",
                "condition": "governance_health_score < 70",
                "severity": "warning"
            },
            {
                "name": "风险评分过高",
                "condition": "risk_score > 80",
                "severity": "critical"
            }
        ]
        
        for rule in alert_rules:
            self.grafana.alerting.create_alert_rule(rule)
```

---

### 3.2 Streamlit集成

**Streamlit核心功能**：
- 快速仪表板开发
- 交互式可视化

**集成方案**：
```python
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

class StreamlitDashboard:
    """Streamlit仪表板"""
    
    def __init__(self):
        st.set_page_config(
            page_title="治理仪表板",
            page_icon="📊",
            layout="wide"
        )
        
    def render_governance_dashboard(self, metrics: Dict):
        """渲染治理仪表板"""
        st.title("🏛️ 治理概览仪表板")
        
        # 治理健康评分
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="治理健康评分",
                value=f"{metrics['governance_health_score']:.1f}",
                delta=f"{metrics['governance_health_delta']:.1f}%"
            )
        
        with col2:
            st.metric(
                label="风险评分",
                value=f"{metrics['risk_score']:.1f}",
                delta=f"{metrics['risk_score_delta']:.1f}%"
            )
        
        with col3:
            st.metric(
                label="合规评分",
                value=f"{metrics['compliance_score']:.1f}",
                delta=f"{metrics['compliance_score_delta']:.1f}%"
            )
        
        with col4:
            st.metric(
                label="绩效评分",
                value=f"{metrics['performance_score']:.1f}",
                delta=f"{metrics['performance_score_delta']:.1f}%"
            )
        
        # 治理健康趋势图
        st.subheader("📈 治理健康趋势")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=metrics['dates'],
            y=metrics['governance_health_trend'],
            mode='lines+markers',
            name='治理健康评分'
        ))
        st.plotly_chart(fig, use_container_width=True)
        
        # 风险监控图表
        st.subheader("⚠️ 风险监控")
        risk_col1, risk_col2 = st.columns(2)
        
        with risk_col1:
            fig = go.Figure(data=go.Bar(
                x=['市场风险', '流动性风险', '信用风险', '操作风险'],
                y=[metrics['market_risk'], metrics['liquidity_risk'], 
                   metrics['credit_risk'], metrics['operational_risk']]
            ))
            fig.update_layout(title="风险分布")
            st.plotly_chart(fig, use_container_width=True)
        
        with risk_col2:
            fig = go.Figure(data=go.Pie(
                labels=['低风险', '中风险', '高风险'],
                values=[metrics['low_risk'], metrics['medium_risk'], metrics['high_risk']]
            ))
            fig.update_layout(title="风险等级分布")
            st.plotly_chart(fig, use_container_width=True)
```

---

## 四、个人使用适配方案

### 4.1 AI辅助仪表板配置

**AI辅助功能**：
1. **自动配置仪表板**：AI根据系统状态自动配置仪表板
2. **智能预警规则**：AI自动生成预警规则
3. **报告自动生成**：AI自动生成治理报告

**技术实现**：
```python
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

class AIDashboardAssistant:
    """AI仪表板助手"""
    
    def __init__(self, api_key: str):
        self.llm = OpenAI(api_key=api_key)
        
    def generate_dashboard_config(self, system_state: Dict) -> str:
        """生成仪表板配置"""
        prompt = PromptTemplate(
            template="""
            作为治理仪表板专家，请根据以下系统状态生成Grafana仪表板配置：
            
            系统状态：{system_state}
            
            请提供：
            1. 推荐的仪表板布局
            2. 关键指标面板配置
            3. 预警规则建议
            4. 可视化优化建议
            """,
            input_variables=["system_state"]
        )
        
        return self.llm(prompt.format(system_state=system_state))
    
    def generate_alert_rules(self, metrics: Dict) -> str:
        """生成预警规则"""
        prompt = PromptTemplate(
            template="""
            作为预警规则专家，请根据以下指标生成预警规则：
            
            指标数据：{metrics}
            
            请提供：
            1. 关键预警规则
            2. 预警阈值建议
            3. 预警响应流程
            4. 预警优化建议
            """,
            input_variables=["metrics"]
        )
        
        return self.llm(prompt.format(metrics=metrics))
```

---

## 五、实施计划

### 5.1 实施步骤

| 步骤 | 任务 | 时间 | 交付物 |
|------|------|------|--------|
| **1** | 环境搭建 | 0.5天 | Grafana + Streamlit环境 |
| **2** | 指标采集模块 | 0.5天 | 治理指标采集器 |
| **3** | 仪表板开发 | 1天 | 治理仪表板系统 |
| **4** | 预警机制 | 0.5天 | 预警系统 |
| **5** | 报告展示 | 0.5天 | 报告展示系统 |

---

## 六、总结

治理仪表板系统是Layer 10治理与合规层的关键补充模块，对个人使用场景具有重要价值：

1. **治理可视化**：实时展示治理状态
2. **实时监控**：实时监控治理指标
3. **预警机制**：及时发现治理异常
4. **报告展示**：自动生成治理报告

**推荐立即实施**，使用Grafana + Streamlit开源项目，预计3天完成。

---

**蓝图版本**: v1.0.0
**蓝图创建时间**: 2026-04-06
**蓝图作者**: 首席架构师
**蓝图状态**: 最终版
**下一步行动**: 实施治理仪表板系统
