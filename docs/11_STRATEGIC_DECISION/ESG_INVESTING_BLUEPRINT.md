---
module_id: ESG_002
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
layer: Layer 9 (治理层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---

﻿---
module_id: ESG_INVESTING_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 11.16 - ESG投资系统
compliance_level: 专业标准
reference_models: ["MSCI ESG Ratings", "Sustainalytics", "Bloomberg ESG"]
open_source_solution: "PyPortfolioOpt ESG约束"
priority: P2
---

# ESG投资系统蓝图

## 📋 文档职责说明

### 核心职责

本文档是**模块蓝图，负责特定功能的实现**。

### 职责边界

**负责**：
- ✅ 核心功能实现
- ✅ 接口定义
- ✅ 数据模型设计

**不负责**：
- ❌ 其他模块职责
- ❌ 跨模块协调

### 对接模块

**上游模块**：
- 上游模块

**下游模块**：
- 下游模块

---
> **版本**: v1.0
> **创建日期**: 2026-04-06
> **优先级**: 🟢 P2 - 可选增强
> **开源方案**: PyPortfolioOpt ESG约束
> **目标**: 构建ESG投资支持系统，支持可持续投资决策

---

## 📋 执行摘要

### 核心定位

ESG投资系统是Layer 11战略决策层的**可持续投资模块**，负责：
- ESG数据整合与评分管理
- ESG约束投资组合优化
- ESG绩效归因分析
- ESG合规报告生成

### 专业价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评级 |
|---------|-------------|-------------|---------|
| **ESG评分整合** | 专业ESG数据供应商 | 公开数据+简化模型 | ⭐⭐⭐ |
| **ESG约束优化** | 专业优化系统 | PyPortfolioOpt集成 | ⭐⭐⭐⭐ |
| **ESG归因** | 专业归因团队 | 简化归因模型 | ⭐⭐⭐ |
| **ESG报告** | 专业报告团队 | 自动化报告生成 | ⭐⭐⭐ |

**综合价值评级**: ⭐⭐⭐ (3/5) - **可选实施**

---

## 一、架构设计

### 1.1 系统整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│              ESG投资系统架构 (ESG Investing System)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.16.1 ESG数据管理层                          │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ ESG数据整合引擎 (ESG Data Integration)              │  │ │
│  │  │ ├── ESG评分获取（第三方数据源）                      │  │ │
│  │  │ ├── ESG数据清洗（数据质量检查）                      │  │ │
│  │  │ ├── ESG数据映射（股票代码映射）                      │  │ │
│  │  │ └── ESG数据更新（定期数据更新）                      │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ ESG评分计算器 (ESG Score Calculator)                │  │ │
│  │  │ ├── 综合ESG评分（E+S+G加权）                         │  │ │
│  │  │ ├── E环境评分（碳排放、资源利用）                    │  │ │
│  │  │ ├── S社会评分（员工、社区、供应链）                  │  │ │
│  │  │ └── G治理评分（董事会、股东权益）                    │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.16.2 ESG约束优化层                         │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ ESG约束定义 (ESG Constraint Definition)             │  │ │
│  │  │ ├── 最低ESG评分约束（组合ESG评分下限）               │  │ │
│  │  │ ├── ESG排除列表（争议性行业排除）                    │  │ │
│  │  │ ├── ESG主题投资（绿色投资主题）                      │  │ │
│  │  │ └── ESG倾斜策略（ESG因子倾斜）                       │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ ESG优化引擎 (ESG Optimization Engine)               │  │ │
│  │  │ ├── ESG约束优化（ESG约束下的组合优化）               │  │ │
│  │  │ ├── ESG-收益权衡（ESG与收益平衡）                    │  │ │
│  │  │ ├── ESG-风险权衡（ESG与风险平衡）                    │  │ │
│  │  │ └── 多目标优化（ESG+收益+风险多目标）                │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.16.3 ESG归因分析层                         │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ ESG绩效归因 (ESG Performance Attribution)           │  │ │
│  │  │ ├── ESG收益贡献（ESG因子收益贡献）                   │  │ │
│  │  │ ├── ESG风险贡献（ESG因子风险贡献）                   │  │ │
│  │  │ ├── ESG评分变化归因（评分变化影响）                  │  │ │
│  │  │ └── ESG事件归因（ESG事件影响分析）                   │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ ESG影响力评估 (ESG Impact Assessment)               │  │ │
│  │  │ ├── 碳足迹计算（组合碳排放量）                       │  │ │
│  │  │ ├── 社会影响力（社会贡献评估）                       │  │ │
│  │  │ ├── 可持续发展目标（SDG贡献）                        │  │ │
│  │  │ └── 影响力报告（影响力评估报告）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.16.4 ESG报告与合规层                       │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ ESG报告生成 (ESG Report Generator)                  │  │ │
│  │  │ ├── ESG月报（月度ESG表现报告）                       │  │ │
│  │  │ ├── ESG季报（季度ESG分析报告）                       │  │ │
│  │  │ ├── ESG年报（年度ESG综合报告）                       │  │ │
│  │  │ └── 定制报告（特定主题ESG报告）                      │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ ESG合规检查 (ESG Compliance Check)                  │  │ │
│  │  │ ├── ESG标准合规（PRI、UNGP等标准）                   │  │ │
│  │  │ ├── ESG披露合规（ESG披露要求）                       │  │ │
│  │  │ ├── ESG投资原则（责任投资原则）                      │  │ │
│  │  │ └── 合规报告（ESG合规报告）                          │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、核心组件详细设计

### 2.1 ESG数据管理层

```python
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

@dataclass
class ESGScore:
    """ESG评分"""
    stock_code: str
    total_score: float
    e_score: float  # 环境评分
    s_score: float  # 社会评分
    g_score: float  # 治理评分
    rating_date: datetime
    data_source: str
    controversies: List[str] = field(default_factory=list)

class ESGDataManager:
    """ESG数据管理器"""
    
    def __init__(self):
        self.esg_scores: Dict[str, ESGScore] = {}
        self.exclusion_list: List[str] = []
        
    def add_esg_score(self, score: ESGScore):
        """添加ESG评分"""
        self.esg_scores[score.stock_code] = score
    
    def get_esg_score(self, stock_code: str) -> Optional[ESGScore]:
        """获取ESG评分"""
        return self.esg_scores.get(stock_code)
    
    def add_to_exclusion_list(self, stock_code: str, reason: str):
        """添加到排除列表"""
        self.exclusion_list.append(stock_code)
    
    def calculate_portfolio_esg_score(self, 
                                     weights: Dict[str, float]) -> float:
        """计算组合ESG评分"""
        total_score = 0
        total_weight = 0
        
        for stock, weight in weights.items():
            if stock in self.esg_scores:
                total_score += weight * self.esg_scores[stock].total_score
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def get_low_esg_stocks(self, 
                          threshold: float = 50) -> List[str]:
        """获取低ESG评分股票"""
        return [
            stock for stock, score in self.esg_scores.items()
            if score.total_score < threshold
        ]
```

### 2.2 ESG约束优化层

```python
from pypfopt import EfficientFrontier

class ESGOptimizer:
    """ESG优化器"""
    
    def __init__(self, 
                 esg_manager: ESGDataManager,
                 expected_returns: pd.Series,
                 cov_matrix: pd.DataFrame):
        self.esg_manager = esg_manager
        self.expected_returns = expected_returns
        self.cov_matrix = cov_matrix
    
    def optimize_with_esg_constraint(self,
                                    min_esg_score: float = 60,
                                    max_weight: float = 0.1) -> Dict[str, float]:
        """ESG约束优化"""
        ef = EfficientFrontier(self.expected_returns, self.cov_matrix)
        
        assets = list(self.expected_returns.index)
        esg_scores = np.array([
            self.esg_manager.esg_scores.get(asset, ESGScore(asset, 0, 0, 0, 0, datetime.now(), '')).total_score
            for asset in assets
        ])
        
        ef.add_constraint(lambda w: w <= max_weight)
        
        n_assets = len(assets)
        ef.add_constraint(
            lambda w: sum(w[i] * esg_scores[i] for i in range(n_assets)) >= min_esg_score
        )
        
        for stock in self.esg_manager.exclusion_list:
            if stock in assets:
                idx = assets.index(stock)
                ef.add_constraint(lambda w, idx=idx: w[idx] == 0)
        
        weights = ef.max_sharpe()
        return ef.clean_weights()
```

---

## 三、实施路径

### Phase 1: 数据管理（3天）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| ESG数据整合 | 1天 | ESGDataManager |
| ESG评分计算 | 1天 | ESGScoreCalculator |
| 数据更新机制 | 1天 | 数据更新脚本 |

### Phase 2: 约束优化（3天）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| ESG约束定义 | 1天 | ESGConstraintDefinition |
| ESG优化引擎 | 2天 | ESGOptimizer |

### Phase 3: 报告分析（2天）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| ESG归因分析 | 1天 | ESGAttribution |
| ESG报告生成 | 1天 | ESGReportGenerator |

---

## 四、相关文档

| 文档 | 说明 |
|------|------|
| [BLUEPRINT.md](./BLUEPRINT.md) | Layer 11主蓝图 |
| [INVESTMENT_CONSTRAINT_BLUEPRINT.md](./INVESTMENT_CONSTRAINT_BLUEPRINT.md) | 投资限制管理系统 |

---

**版本**: v1.0 | **更新**: 2026-04-06 | **状态**: ✅ 活跃
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Esg Investing
- **模块ID**: ESG_INVESTING_001
- **蓝图文档**: [ESG_INVESTING_BLUEPRINT.md](./11_STRATEGIC_DECISION\ESG_INVESTING_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: Layer 11.16 - ESG投资系统
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Esg Investing** | Layer 11.16 - ESG投资系统 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
