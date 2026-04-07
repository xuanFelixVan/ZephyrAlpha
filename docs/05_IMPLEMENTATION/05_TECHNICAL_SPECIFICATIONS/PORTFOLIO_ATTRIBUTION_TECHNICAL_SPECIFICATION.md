﻿---
module_id: PORTFOLIO_ATTRIBUTION_TECH_SPEC_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_ATTRIBUTION_BLUEPRINT.md
last_updated: 2026-04-07
created_date: 2026-04-07
layer: Layer 7 (风险管理/绩效评估层)
index: PORTFOLIO_ATTRIBUTION_TECH_SPEC_001
estimated_hours: 18
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-07
owner: 实施团队
responsibility:
  - 实施指南、部署文档
  - 归因分析实现
  - Brinson归因
standard_type: 专业量化机构技术规格书
applicable_scope: Layer 7 风险管理/绩效评估层
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 待实施
---

# Portfolio Attribution技术规格书 v1.0

> **核心职责**: 组合归因分析详细技术实现规范
> **职责边界**: 
> - ✅ 本文档负责：Brinson归因、因子归因、收益分解
> - ❌ 本文档不负责：绩效评估、风险监控

> 清风量化系统 v5.3 - Portfolio Attribution详细技术设计
> **索引**: `PORTFOLIO_ATTRIBUTION_TECH_SPEC_001`
> **开发工时**: 18h
> **核心定位**: 组合归因分析的技术实现

---

## 1. 概述

### 1.1 设计背景与业务目标
- **业务需求**: 分解组合收益来源，识别超额收益驱动因素
- **技术痛点**: 
  - 归因模型选择：Brinson、因子归因等
  - 多层次分解：资产配置、证券选择、交互效应
  - 数据要求：需要持仓、基准、收益等数据
- **预期收益**: 
  - 提供收益来源分析能力
  - 支持多维度归因
  - 帮助优化投资决策

### 1.2 技术定位与架构层归属
- **Layer定位**: Layer 7 - 风险管理/绩效评估层
- **模块类别**: 核心归因分析模块

---

## 2. 详细架构设计

### 2.1 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                   Layer 7: 绩效评估层                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │       AttributionAnalyzer (主模块)                   │  │
│  │ - Brinson归因                                         │  │
│  │ - 因子归因                                            │  │
│  │ - 收益分解                                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         核心组件                                      │  │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │  │
│  │ │BrinsonAttri │ │FactorAttrib │ │ReturnDecomp │     │  │
│  │ │Brinson归因  │ │因子归因     │ │收益分解     │     │  │
│  │ └─────────────┘ └─────────────┘ └─────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 接口定义

### 3.1 API接口规范

```python
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
import numpy as np
import pandas as pd
import logging


@dataclass
class BrinsonAttributionResult:
    """Brinson归因结果"""
    allocation_effect: float
    selection_effect: float
    interaction_effect: float
    total_active_return: float
    category_breakdown: Dict[str, Dict[str, float]]


@dataclass
class FactorAttributionResult:
    """因子归因结果"""
    factor_returns: Dict[str, float]
    factor_exposures: Dict[str, float]
    factor_contributions: Dict[str, float]
    specific_return: float
    total_return: float


class BrinsonAttribution:
    """Brinson归因分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
        categories: pd.Series
    ) -> BrinsonAttributionResult:
        """
        执行Brinson归因分析
        
        参数:
            portfolio_weights: 组合权重
            benchmark_weights: 基准权重
            portfolio_returns: 组合收益
            benchmark_returns: 基准收益
            categories: 类别映射
            
        返回:
            Brinson归因结果
        """
        unique_categories = categories.unique()
        
        allocation_effect = 0.0
        selection_effect = 0.0
        interaction_effect = 0.0
        category_breakdown = {}
        
        for cat in unique_categories:
            cat_mask = categories == cat
            
            w_p = portfolio_weights[cat_mask].sum()
            w_b = benchmark_weights[cat_mask].sum()
            r_p = (portfolio_weights[cat_mask] * portfolio_returns[cat_mask]).sum() / w_p if w_p > 0 else 0
            r_b = (benchmark_weights[cat_mask] * benchmark_returns[cat_mask]).sum() / w_b if w_b > 0 else 0
            
            alloc = (w_p - w_b) * r_b
            select = w_b * (r_p - r_b)
            interact = (w_p - w_b) * (r_p - r_b)
            
            allocation_effect += alloc
            selection_effect += select
            interaction_effect += interact
            
            category_breakdown[cat] = {
                "allocation": alloc,
                "selection": select,
                "interaction": interact,
                "total": alloc + select + interact
            }
        
        total_active_return = allocation_effect + selection_effect + interaction_effect
        
        result = BrinsonAttributionResult(
            allocation_effect=allocation_effect,
            selection_effect=selection_effect,
            interaction_effect=interaction_effect,
            total_active_return=total_active_return,
            category_breakdown=category_breakdown
        )
        
        self.logger.info(f"Brinson归因完成，总主动收益={total_active_return:.6f}")
        
        return result


class FactorAttribution:
    """因子归因分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze(
        self,
        portfolio_returns: pd.Series,
        factor_returns: pd.DataFrame,
        factor_exposures: pd.DataFrame
    ) -> FactorAttributionResult:
        """
        执行因子归因分析
        
        参数:
            portfolio_returns: 组合收益
            factor_returns: 因子收益
            factor_exposures: 因子暴露
            
        返回:
            因子归因结果
        """
        factor_names = factor_returns.columns.tolist()
        
        factor_contributions = {}
        for factor in factor_names:
            exposure = factor_exposures[factor].mean()
            ret = factor_returns[factor].mean()
            contribution = exposure * ret
            factor_contributions[factor] = contribution
        
        total_factor_return = sum(factor_contributions.values())
        specific_return = portfolio_returns.mean() - total_factor_return
        
        result = FactorAttributionResult(
            factor_returns=factor_returns.mean().to_dict(),
            factor_exposures=factor_exposures.mean().to_dict(),
            factor_contributions=factor_contributions,
            specific_return=specific_return,
            total_return=portfolio_returns.mean()
        )
        
        self.logger.info(f"因子归因完成，因子收益={total_factor_return:.6f}")
        
        return result


class AttributionAnalyzer:
    """归因分析器主类"""
    
    def __init__(self):
        self.brinson = BrinsonAttribution()
        self.factor = FactorAttribution()
        self.logger = logging.getLogger(__name__)
    
    def analyze_brinson(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
        categories: pd.Series
    ) -> BrinsonAttributionResult:
        """执行Brinson归因"""
        return self.brinson.analyze(
            portfolio_weights, benchmark_weights,
            portfolio_returns, benchmark_returns, categories
        )
    
    def analyze_factor(
        self,
        portfolio_returns: pd.Series,
        factor_returns: pd.DataFrame,
        factor_exposures: pd.DataFrame
    ) -> FactorAttributionResult:
        """执行因子归因"""
        return self.factor.analyze(
            portfolio_returns, factor_returns, factor_exposures
        )
```

---

## 4. 性能指标与SLA要求
| 指标 | 目标值 | 测量方法 | 备注 |
|------|--------|----------|------|
| **响应时间** | <300ms | P95延迟 | 归因计算 |
| **吞吐量** | 15 QPS | 每秒请求数 | 峰值要求 |
| **可用性** | 99.9% | 每月宕机时间 | SLA要求 |

---

## 5. 实施路线图

### 5.1 Phase 1：核心功能（1周）
| 任务 | 优先级 | 预计工时 | 交付物 | 完成标准 |
|------|--------|----------|--------|----------|
| Brinson归因 | P0 | 6h | 归因模块 | 单元测试通过 |
| 因子归因 | P0 | 6h | 归因模块 | 单元测试通过 |

### 5.2 Phase 2：功能增强（0.5周）
| 任务 | 优先级 | 预计工时 | 交付物 | 完成标准 |
|------|--------|----------|--------|----------|
| 多期归因 | P1 | 4h | 扩展模块 | 单元测试通过 |
| 数据库集成 | P1 | 2h | SQL脚本 | 数据库创建成功 |

---

## 附录

### A. 术语表
| 术语 | 定义 | 缩写 |
|------|------|------|
| 资产配置效应 | 权重差异带来的收益 | - |
| 证券选择效应 | 收益差异带来的收益 | - |
| 交互效应 | 权重和收益差异的综合效应 | - |

### B. 变更记录
| 日期 | 版本 | 变更内容 | 变更人 | 审核人 |
|------|------|----------|--------|--------|
| 2026-04-07 | v1.0 | 初始版本 | 实施团队 | 首席技术评审官 |

---

**版本**: v1.0 | **创建**: 2026-04-07 | **状态**: Active | **维护者**: ZephyrAlpha技术团队
