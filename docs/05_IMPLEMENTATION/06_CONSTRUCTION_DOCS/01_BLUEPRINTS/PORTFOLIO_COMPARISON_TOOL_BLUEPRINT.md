---
module_id: PORTFOLIO_COMPARISON_TOOL_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 6 组合优化层
compliance_level: 专业标准
responsibility:
  - 组合方案比较
  - 多维度评估
  - 优劣分析
  - 决策支持
layer: Layer 6 (组合优化层)
---

# 组合比较工具蓝图

## 1. 概述

### 1.1 定位与目标

**核心定位**: 比较不同组合方案的优劣，提供决策支持

**业务价值**:
- 帮助选择最优组合方案
- 提供多维度比较视角
- 支持科学决策

**版本信息**: v1.0.0

### 1.2 职责边界

**负责**:
- 比较组合方案
- 多维度评估
- 优劣分析
- 提供决策建议

**不负责**:
- 生成组合方案（由优化模块负责）
- 执行交易（由执行模块负责）
- 风险管理（由风险模块负责）

## 2. 架构设计

### 2.1 Layer定位

**Layer**: Layer 6 (组合优化层)

**上游依赖**:
- Layer 6: 组合优化模块（组合方案）

**下游服务**:
- Layer 6: 组合优化模块（决策反馈）
- Layer 7: AI报告层（比较报告）

### 2.2 模块架构

```
┌─────────────────────────────────────────────────────────┐
│          组合比较工具 (Portfolio Comparison Tool)        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 收益比较      │  │ 风险比较      │  │ 成本比较      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 效率比较      │  │ 综合评分      │  │ 决策建议      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.3 核心功能模块

| 模块 | 功能 | 开源方案 |
|------|------|----------|
| 收益比较 | 比较预期收益 | numpy + pandas |
| 风险比较 | 比较风险指标 | pyfolio |
| 成本比较 | 比较交易成本 | 自研 |
| 效率比较 | 比较优化效率 | 自研 |
| 综合评分 | 综合评估打分 | 自研 |
| 决策建议 | 提供决策建议 | 自研 |

## 3. 技术实现

### 3.1 技术栈选择

| 技术领域 | 选择方案 | 理由 |
|----------|----------|------|
| 数值计算 | numpy, pandas | 高性能数值计算 |
| 绩效分析 | pyfolio | 风险指标计算 |
| 可视化 | matplotlib, plotly | 比较图表展示 |
| 多准则决策 | 自研 | 决策支持算法 |

### 3.2 核心算法

```python
import numpy as np
import pandas as pd
from typing import List, Dict

class PortfolioComparisonTool:
    def __init__(self):
        self.evaluation_dimensions = [
            'return', 'risk', 'cost', 'efficiency', 
            'diversification', 'liquidity'
        ]
    
    def compare_returns(self, portfolios: List[Dict]) -> Dict:
        comparison = {
            'expected_returns': {},
            'return_ranks': {},
            'return_statistics': {}
        }
        
        for i, portfolio in enumerate(portfolios):
            weights = portfolio['weights']
            expected_returns = portfolio['expected_returns']
            
            portfolio_return = np.dot(weights, expected_returns)
            comparison['expected_returns'][f'portfolio_{i}'] = portfolio_return
        
        sorted_returns = sorted(
            comparison['expected_returns'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for rank, (name, ret) in enumerate(sorted_returns, 1):
            comparison['return_ranks'][name] = rank
        
        returns = list(comparison['expected_returns'].values())
        comparison['return_statistics'] = {
            'mean': np.mean(returns),
            'std': np.std(returns),
            'max': np.max(returns),
            'min': np.min(returns),
            'range': np.max(returns) - np.min(returns)
        }
        
        return comparison
    
    def compare_risks(self, portfolios: List[Dict]) -> Dict:
        comparison = {
            'volatility': {},
            'var_95': {},
            'cvar_95': {},
            'max_drawdown': {},
            'risk_ranks': {}
        }
        
        for i, portfolio in enumerate(portfolios):
            weights = portfolio['weights']
            cov_matrix = portfolio['cov_matrix']
            returns_data = portfolio.get('returns_data')
            
            portfolio_vol = np.sqrt(
                np.dot(weights.T, np.dot(cov_matrix, weights))
            )
            comparison['volatility'][f'portfolio_{i}'] = portfolio_vol
            
            if returns_data is not None:
                portfolio_returns = np.dot(returns_data, weights)
                
                var_95 = np.percentile(portfolio_returns, 5)
                cvar_95 = np.mean(portfolio_returns[portfolio_returns <= var_95])
                
                comparison['var_95'][f'portfolio_{i}'] = var_95
                comparison['cvar_95'][f'portfolio_{i}'] = cvar_95
                
                cumulative = np.cumprod(1 + portfolio_returns)
                running_max = np.maximum.accumulate(cumulative)
                drawdowns = (cumulative - running_max) / running_max
                max_dd = np.min(drawdowns)
                comparison['max_drawdown'][f'portfolio_{i}'] = max_dd
        
        sorted_vol = sorted(
            comparison['volatility'].items(),
            key=lambda x: x[1]
        )
        
        for rank, (name, vol) in enumerate(sorted_vol, 1):
            comparison['risk_ranks'][name] = rank
        
        return comparison
    
    def compare_costs(self, portfolios: List[Dict]) -> Dict:
        comparison = {
            'transaction_costs': {},
            'market_impact': {},
            'total_costs': {},
            'cost_ranks': {}
        }
        
        for i, portfolio in enumerate(portfolios):
            weights = portfolio['weights']
            current_weights = portfolio.get('current_weights', weights)
            liquidity_data = portfolio.get('liquidity_data', {})
            
            turnover = np.sum(np.abs(weights - current_weights))
            
            transaction_cost = turnover * 0.001
            
            market_impact = 0
            for j, w in enumerate(weights):
                trade_size = abs(w - current_weights[j])
                if trade_size > 0:
                    avg_volume = liquidity_data.get(j, {}).get('avg_volume', 1e6)
                    participation_rate = trade_size / avg_volume
                    market_impact += 0.1 * np.sqrt(participation_rate) * trade_size
            
            total_cost = transaction_cost + market_impact
            
            comparison['transaction_costs'][f'portfolio_{i}'] = transaction_cost
            comparison['market_impact'][f'portfolio_{i}'] = market_impact
            comparison['total_costs'][f'portfolio_{i}'] = total_cost
        
        sorted_costs = sorted(
            comparison['total_costs'].items(),
            key=lambda x: x[1]
        )
        
        for rank, (name, cost) in enumerate(sorted_costs, 1):
            comparison['cost_ranks'][name] = rank
        
        return comparison
    
    def compare_efficiency(self, portfolios: List[Dict]) -> Dict:
        comparison = {
            'sharpe_ratio': {},
            'information_ratio': {},
            'sortino_ratio': {},
            'efficiency_ranks': {}
        }
        
        for i, portfolio in enumerate(portfolios):
            weights = portfolio['weights']
            expected_returns = portfolio['expected_returns']
            cov_matrix = portfolio['cov_matrix']
            returns_data = portfolio.get('returns_data')
            
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_vol = np.sqrt(
                np.dot(weights.T, np.dot(cov_matrix, weights))
            )
            
            risk_free_rate = 0.02
            sharpe = (portfolio_return - risk_free_rate) / portfolio_vol
            comparison['sharpe_ratio'][f'portfolio_{i}'] = sharpe
            
            if returns_data is not None:
                portfolio_returns = np.dot(returns_data, weights)
                negative_returns = portfolio_returns[portfolio_returns < 0]
                
                if len(negative_returns) > 0:
                    downside_vol = np.std(negative_returns)
                    sortino = (portfolio_return - risk_free_rate) / downside_vol
                    comparison['sortino_ratio'][f'portfolio_{i}'] = sortino
        
        sorted_sharpe = sorted(
            comparison['sharpe_ratio'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for rank, (name, sr) in enumerate(sorted_sharpe, 1):
            comparison['efficiency_ranks'][name] = rank
        
        return comparison
    
    def calculate_comprehensive_score(self, portfolios: List[Dict], 
                                     weights: Dict = None) -> Dict:
        if weights is None:
            weights = {
                'return': 0.25,
                'risk': 0.25,
                'cost': 0.20,
                'efficiency': 0.20,
                'diversification': 0.10
            }
        
        return_comparison = self.compare_returns(portfolios)
        risk_comparison = self.compare_risks(portfolios)
        cost_comparison = self.compare_costs(portfolios)
        efficiency_comparison = self.compare_efficiency(portfolios)
        
        scores = {}
        
        for i in range(len(portfolios)):
            name = f'portfolio_{i}'
            
            return_score = 1.0 / return_comparison['return_ranks'][name]
            risk_score = 1.0 / risk_comparison['risk_ranks'][name]
            cost_score = 1.0 / cost_comparison['cost_ranks'][name]
            efficiency_score = 1.0 / efficiency_comparison['efficiency_ranks'][name]
            
            diversification_score = self._calculate_diversification_score(
                portfolios[i]['weights']
            )
            
            comprehensive_score = (
                weights['return'] * return_score +
                weights['risk'] * risk_score +
                weights['cost'] * cost_score +
                weights['efficiency'] * efficiency_score +
                weights['diversification'] * diversification_score
            )
            
            scores[name] = {
                'comprehensive_score': comprehensive_score,
                'return_score': return_score,
                'risk_score': risk_score,
                'cost_score': cost_score,
                'efficiency_score': efficiency_score,
                'diversification_score': diversification_score
            }
        
        sorted_scores = sorted(
            scores.items(),
            key=lambda x: x[1]['comprehensive_score'],
            reverse=True
        )
        
        for rank, (name, score) in enumerate(sorted_scores, 1):
            scores[name]['rank'] = rank
        
        return scores
    
    def _calculate_diversification_score(self, weights):
        weights = np.array(weights)
        weights = weights[weights > 0]
        
        if len(weights) == 0:
            return 0
        
        herfindahl = np.sum(weights ** 2)
        
        effective_n = 1.0 / herfindahl
        
        max_diversification = 1.0 / (1.0 / len(weights))
        
        diversification_score = effective_n / max_diversification
        
        return diversification_score
    
    def generate_decision_recommendation(self, portfolios: List[Dict],
                                        preference: str = 'balanced') -> Dict:
        if preference == 'return_oriented':
            weights = {
                'return': 0.40,
                'risk': 0.15,
                'cost': 0.15,
                'efficiency': 0.20,
                'diversification': 0.10
            }
        elif preference == 'risk_averse':
            weights = {
                'return': 0.15,
                'risk': 0.40,
                'cost': 0.15,
                'efficiency': 0.20,
                'diversification': 0.10
            }
        else:
            weights = {
                'return': 0.25,
                'risk': 0.25,
                'cost': 0.20,
                'efficiency': 0.20,
                'diversification': 0.10
            }
        
        scores = self.calculate_comprehensive_score(portfolios, weights)
        
        best_portfolio = max(scores.items(), key=lambda x: x[1]['comprehensive_score'])
        
        return_comparison = self.compare_returns(portfolios)
        risk_comparison = self.compare_risks(portfolios)
        cost_comparison = self.compare_costs(portfolios)
        
        recommendation = {
            'best_portfolio': best_portfolio[0],
            'comprehensive_score': best_portfolio[1]['comprehensive_score'],
            'preference': preference,
            'analysis': {
                'return_comparison': return_comparison,
                'risk_comparison': risk_comparison,
                'cost_comparison': cost_comparison
            },
            'scores': scores,
            'recommendation': self._generate_recommendation_text(
                best_portfolio, scores, preference
            )
        }
        
        return recommendation
    
    def _generate_recommendation_text(self, best_portfolio, scores, preference):
        name = best_portfolio[0]
        score = best_portfolio[1]
        
        text = f"推荐选择{name}，综合得分{score['comprehensive_score']:.3f}。\n"
        text += f"该组合在收益、风险、成本、效率等多维度表现最优。\n"
        
        if preference == 'return_oriented':
            text += f"收益得分{score['return_score']:.3f}，适合追求高收益的投资者。"
        elif preference == 'risk_averse':
            text += f"风险得分{score['risk_score']:.3f}，适合风险厌恶型投资者。"
        else:
            text += f"综合表现均衡，适合大多数投资者。"
        
        return text

## 4. 数据模型

### 4.1 数据结构

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

@dataclass
class PortfolioComparison:
    portfolio_id: str
    expected_return: float
    volatility: float
    sharpe_ratio: float
    total_cost: float
    diversification_score: float

@dataclass
class ComparisonResult:
    best_portfolio: str
    comprehensive_score: float
    scores: Dict[str, Dict]
    recommendation: str
```

### 4.2 存储方案

| 数据类型 | 存储方案 | 保留期限 |
|----------|----------|----------|
| 比较历史 | SQLite | 1年 |
| 决策记录 | SQLite | 永久 |
| 评分规则 | YAML | 永久 |

## 5. 实施路径

### 5.1 Phase 1: 核心功能 (1周)

- [x] 收益比较
- [x] 风险比较
- [x] 成本比较
- [x] 基础比较功能

### 5.2 Phase 2: 高级功能 (1周)

- [ ] 效率比较
- [ ] 综合评分
- [ ] 决策建议
- [ ] 可视化界面

### 5.3 Phase 3: 优化完善 (1周)

- [ ] 性能优化
- [ ] API接口完善
- [ ] 文档完善
- [ ] 测试覆盖

## 6. 文档治理

### 6.1 System_Manifest.md索引

```yaml
- module_id: PORTFOLIO_COMPARISON_TOOL_001
  module_name: 组合比较工具
  layer: Layer 6 (组合优化层)
  status: Active
  blueprint: PORTFOLIO_COMPARISON_TOOL_BLUEPRINT.md
```

### 6.2 模块职责边界

**与组合优化模块的关系**:
- 组合优化模块提供组合方案
- 比较工具比较方案优劣

**与决策支持模块的关系**:
- 比较工具提供比较结果
- 决策支持模块进行最终决策

### 6.3 版本管理策略

- v1.0.0: 初始版本，基础比较功能
- v1.1.0: 增加综合评分功能
- v1.2.0: 增加决策建议功能

## 7. 风险评估

### 7.1 技术风险

| 风险 | 概率 | 应对措施 |
|------|------|----------|
| 比较维度不全 | 中 | 持续完善维度 |
| 评分权重不合理 | 中 | 优化权重设置 |
| 性能瓶颈 | 低 | 使用缓存优化 |

### 7.2 业务风险

| 风险 | 概率 | 应对措施 |
|------|------|----------|
| 比较结果误导 | 中 | 多维度验证 |
| 偏好设置不当 | 中 | 提供默认设置 |
| 决策失误 | 低 | 人工复核机制 |

## 接口与契约（蓝图终稿）

### API契约索引

本模块遵循系统统一接口规范，详见 [API_Contract.md](../../../03_TRADING_TACTICS/API_Contract.md)。

### 核心接口定义

| 接口名称 | 索引 | 说明 |
|----------|------|------|
| 收益比较 | API.PCT.001 | compare_returns接口 |
| 风险比较 | API.PCT.002 | compare_risks接口 |
| 成本比较 | API.PCT.003 | compare_costs接口 |
| 综合评分 | API.PCT.004 | calculate_comprehensive_score接口 |

### 数据格式规范

- 输入格式: List[Dict] (portfolios), Dict (preference_weights)
- 输出格式: Dict (scores, recommendation, analysis)
- 时间戳格式: ISO 8601 UTC

## 验收标准（可检查）

### 功能验收

1. **多维度比较**: 能够从收益、风险、成本、效率、分散度五个维度比较组合
2. **综合评分**: 能够根据偏好权重计算综合评分，排名合理
3. **决策建议**: 能够生成决策建议文本，说明推荐理由
4. **可视化**: 能够生成比较图表，直观展示差异

### 性能验收

| 指标 | 目标值 | 验证方法 |
|------|--------|----------|
| 比较计算时间 | <500ms (10组合) | 性能测试 |
| 报告生成时间 | <1s | 性能测试 |
| 内存占用 | <200MB | 资源监控 |

### 质量验收

| 标准 | 要求 | 验证方法 |
|------|------|----------|
| 代码覆盖率 | ≥80% | pytest-cov |
| 文档完整性 | 100% | 文档审查 |
| 数值精度 | 小数点后4位 | 单元测试 |

## 已知限制

### 技术限制

1. **数据要求**: 需要完整的组合权重、收益、协方差数据
2. **偏好设置**: 权重偏好需要用户手动设置
3. **历史数据**: 风险指标计算需要历史收益数据
4. **基准依赖**: 部分指标需要基准数据

### 功能限制

1. **比较维度**: 当前仅支持5个维度，自定义维度待扩展
2. **评分方法**: 当前仅支持加权平均法，TOPSIS/AHP待扩展
3. **动态比较**: 不支持时变组合的动态比较

### 可选增强（第二期）

- 核心范围已在正文闭合；若追加机构级增强（性能档位、可观测性、多账户等），在本节登记并走版本升级与契约对齐。

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 组合优化层负责人 |
