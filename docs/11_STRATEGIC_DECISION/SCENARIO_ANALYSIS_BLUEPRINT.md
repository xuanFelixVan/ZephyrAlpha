---
module_id: SCENARIO_ANALYSIS_BLUEPRINT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - SCENARIO_ANALYSIS蓝图设计
---

﻿---
module_id: LAYER_021
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
layer: Layer 6 (组合优化层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
responsibility:
  - 系统架构蓝图设计与实施指导与实施方案

---
---

﻿---
module_id: SCENARIO_ANALYSIS_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 11.12 - 情景分析系统
compliance_level: 专业机构标准
reference_models: ["Fed Stress Test", "ECB Stress Test", "IMF Scenario Analysis"]
related_documents:
  - BLUEPRINT.md
  - ARCHITECTURE.md
  - LIQUIDITY_MANAGEMENT_BLUEPRINT.md
  - PORTFOLIO_INSURANCE_BLUEPRINT.md
parent_document: BLUEPRINT.md
implementation_status: 设计阶段
---

# Layer 11.12: 情景分析系统蓝图
> **核心职责**: 情景分析系统蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：情景分析系统蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容

> **核心职责**: Scenario Analysis蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Scenario Analysis蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


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
> **实施周期**: 1周  
> **目标**: 构建多维度情景分析体系，评估极端情况下的组合表现

---

## 📋 执行摘要

### 核心定位

Layer 11.12情景分析系统是清风量化系统的**风险预警雷达**，负责：
- 情景定义与构建（历史情景、假设情景、极端情景）
- 情景模拟计算（蒙特卡洛、历史模拟、压力测试）
- 情景影响评估（收益分布、风险指标、流动性影响）
- 应对策略生成（对冲建议、仓位调整、风险缓释）

### 专业机构对标

| 机构 | 情景分析策略 | 应用场景 | 您的实现 |
|------|-------------|---------|---------|
| **美联储** | CCAR压力测试 | 银行资本充足率 | ✅ 极端情景测试 |
| **IMF** | 全球情景分析 | 宏观风险评估 | ✅ 宏观情景模拟 |
| **桥水** | 全天候情景 | 组合稳健性 | ✅ 多情景优化 |
| **高盛** | 情景风险报告 | 客户风险披露 | ✅ 情景报告生成 |

### 业务价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评级 |
|---------|-------------|------------|---------|
| **风险预警** | 提前识别极端风险 | 情景压力测试 | ⭐⭐⭐⭐⭐ |
| **决策支持** | 情景化决策依据 | 情景收益分布 | ⭐⭐⭐⭐ |
| **策略优化** | 情景稳健性优化 | 多情景组合优化 | ⭐⭐⭐⭐ |
| **合规披露** | 风险情景披露 | 情景报告生成 | ⭐⭐⭐ |

**综合价值评级**: ⭐⭐⭐⭐ (4/5) - **建议实施**

---

## 一、架构设计

### 1.1 情景分析系统整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│           Layer 11.12: 情景分析系统架构                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │         11.12.1 情景定义与构建系统                         │ │
│  │  ├── 历史情景重现 (Historical Scenario Replay)            │ │
│  │  │   └── 2008金融危机/2020疫情/2015股灾等                │ │
│  │  ├── 假设情景构建 (Hypothetical Scenario Construction)    │ │
│  │  │   └── 利率上升/通胀加剧/地缘政治等                    │ │
│  │  ├── 极端情景设计 (Extreme Scenario Design)               │ │
│  │  │   └── 尾部风险/黑天鹅事件                            │ │
│  │  └── 自定义情景 (Custom Scenario)                         │ │
│  │      └── 用户定义的特定情景                              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │         11.12.2 情景模拟引擎                               │ │
│  │  ├── 蒙特卡洛模拟 (Monte Carlo Simulation)                │ │
│  │  │   └── 参数化/非参数化/历史重采样                      │ │
│  │  ├── 历史模拟 (Historical Simulation)                     │ │
│  │  │   └── 历史数据回放/情景映射                          │ │
│  │  ├── 因子情景模拟 (Factor Scenario Simulation)            │ │
│  │  │   └── 因子冲击/因子相关性变化                        │ │
│  │  └── 压力测试 (Stress Testing)                            │ │
│  │      └── 极端冲击测试/敏感性分析                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │         11.12.3 情景影响评估系统                           │ │
│  │  ├── 收益分布分析 (Return Distribution Analysis)          │ │
│  │  ├── 风险指标计算 (Risk Metrics Calculation)              │ │
│  │  ├── 流动性影响评估 (Liquidity Impact Assessment)         │ │
│  │  └── 敞口变化分析 (Exposure Change Analysis)              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │         11.12.4 应对策略生成系统                           │ │
│  │  ├── 对冲建议生成 (Hedge Recommendation)                  │ │
│  │  ├── 仓位调整建议 (Position Adjustment Suggestion)        │ │
│  │  ├── 风险缓释策略 (Risk Mitigation Strategy)              │ │
│  │  └── 应急预案 (Emergency Plan)                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │         11.12.5 情景报告系统                               │ │
│  │  ├── 情景分析报告 (Scenario Analysis Report)              │ │
│  │  ├── 压力测试报告 (Stress Test Report)                    │ │
│  │  ├── 风险预警报告 (Risk Warning Report)                   │ │
│  │  └── 可视化展示 (Visualization)                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责边界

| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |
|------|---------|------|------|---------|
| **情景定义** | 构建分析情景 | 历史数据、用户输入 | 情景定义 | Layer 11.4 |
| **情景模拟** | 执行情景模拟 | 情景定义、组合数据 | 模拟结果 | Layer 5, 7 |
| **影响评估** | 评估情景影响 | 模拟结果 | 影响报告 | Layer 11.2, 11.8 |
| **策略生成** | 生成应对策略 | 影响报告 | 策略建议 | Layer 11.4, 11.5 |
| **报告系统** | 生成报告 | 所有数据 | 可视化报告 | Layer 8 |

---

## 二、核心组件详细设计

### 2.1 情景定义与构建系统

#### 2.1.1 核心原理

**情景定义模型**：

```
历史情景:
Scenario_Historical = {Date_Range, Market_Conditions, Factor_Shocks}

假设情景:
Scenario_Hypothetical = {Factor_Shocks, Correlation_Changes, Volatility_Changes}

极端情景:
Scenario_Extreme = {
    Tail_Risk_Level: 99.9%,
Factor_Shock_Multiplier: 3σ,
    Correlation_Shock: +0.3
}

情景参数:
Scenario_Params = {
    Duration: T,
    Factor_Shocks: {f1: Δf1, f2: Δf2, ...},
    Correlation_Matrix: Σ',
    Volatility_Surface: σ'
}
```

#### 2.1.2 技术实现

```python
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd

class ScenarioType(Enum):
    """情景类型"""
    HISTORICAL = "historical"
    HYPOTHETICAL = "hypothetical"
    EXTREME = "extreme"
    CUSTOM = "custom"

@dataclass
class ScenarioDefinition:
    """情景定义"""
    scenario_id: str
    scenario_name: str
    scenario_type: ScenarioType
    description: str
    duration_days: int
    factor_shocks: Dict[str, float]      # 因子冲击
    correlation_changes: Dict           # 相关性变化
    volatility_changes: Dict[str, float] # 波动率变化
    probability: float                   # 发生概率
    severity: str                        # 严重程度
    created_at: datetime

class ScenarioBuilder:
    """情景构建引擎"""
    
    def __init__(self):
        self.historical_scenarios = {
            '2008_financial_crisis': {
                'name': '2008年金融危机',
                'start_date': '2008-09-01',
                'end_date': '2008-11-30',
                'factor_shocks': {
                    'market': -0.45,
                    'size': -0.25,
                    'value': -0.15,
                    'momentum': -0.30
                },
                'volatility_multiplier': 3.5
            },
            '2020_covid': {
                'name': '2020年新冠疫情',
                'start_date': '2020-02-20',
                'end_date': '2020-03-23',
                'factor_shocks': {
                    'market': -0.35,
                    'size': -0.20,
                    'value': -0.25,
                    'momentum': 0.10
                },
                'volatility_multiplier': 4.0
            },
            '2015_china_crash': {
                'name': '2015年股灾',
                'start_date': '2015-06-12',
                'end_date': '2015-07-08',
                'factor_shocks': {
                    'market': -0.35,
                    'size': -0.40,
                    'value': -0.10,
                    'momentum': -0.20
                },
                'volatility_multiplier': 3.0
            }
        }
        
    def create_historical_scenario(self, 
                                  scenario_key: str) -> ScenarioDefinition:
        """创建历史情景"""
        if scenario_key not in self.historical_scenarios:
            raise ValueError(f"未知历史情景: {scenario_key}")
        
        config = self.historical_scenarios[scenario_key]
        
        return ScenarioDefinition(
            scenario_id=f"HIST_{scenario_key}",
            scenario_name=config['name'],
            scenario_type=ScenarioType.HISTORICAL,
            description=f"历史情景重现: {config['name']}",
            duration_days=30,
            factor_shocks=config['factor_shocks'],
            correlation_changes={},
            volatility_changes={'all': config['volatility_multiplier']},
            probability=0.01,
            severity='high',
            created_at=datetime.now()
        )
    
    def create_hypothetical_scenario(self, 
                                    name: str,
                                    factor_shocks: Dict[str, float],
                                    volatility_multiplier: float = 2.0,
                                    correlation_shift: float = 0.0) -> ScenarioDefinition:
        """创建假设情景"""
        correlation_changes = {
            'shift': correlation_shift,
            'description': f"相关性整体偏移{correlation_shift:+.2f}"
        }
        
        volatility_changes = {
            factor: volatility_multiplier 
            for factor in factor_shocks
        }
        
        return ScenarioDefinition(
            scenario_id=f"HYPO_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            scenario_name=name,
            scenario_type=ScenarioType.HYPOTHETICAL,
            description=f"假设情景: {name}",
            duration_days=30,
            factor_shocks=factor_shocks,
            correlation_changes=correlation_changes,
            volatility_changes=volatility_changes,
            probability=0.05,
            severity='medium',
            created_at=datetime.now()
        )
    
    def create_extreme_scenario(self, 
                               name: str,
                               tail_percentile: float = 99.9,
                               shock_multiplier: float = 3.0) -> ScenarioDefinition:
        """创建极端情景"""
        factor_shocks = {
            'market': -0.50 * shock_multiplier,
            'size': -0.30 * shock_multiplier,
            'value': -0.20 * shock_multiplier,
            'momentum': -0.25 * shock_multiplier,
            'quality': 0.15 * shock_multiplier
        }
        
        correlation_changes = {
            'shift': 0.3,
            'description': "危机模式下相关性急剧上升"
        }
        
        volatility_changes = {
            factor: 5.0 for factor in factor_shocks
        }
        
        return ScenarioDefinition(
            scenario_id=f"EXTR_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            scenario_name=name,
            scenario_type=ScenarioType.EXTREME,
            description=f"极端情景: {name} (尾部{tail_percentile}%)",
            duration_days=60,
            factor_shocks=factor_shocks,
            correlation_changes=correlation_changes,
            volatility_changes=volatility_changes,
            probability=0.001,
            severity='critical',
            created_at=datetime.now()
        )
    
    def create_custom_scenario(self, 
                              name: str,
                              factor_shocks: Dict[str, float],
                              duration_days: int = 30,
                              probability: float = 0.10) -> ScenarioDefinition:
        """创建自定义情景"""
        return ScenarioDefinition(
            scenario_id=f"CUST_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            scenario_name=name,
            scenario_type=ScenarioType.CUSTOM,
            description=f"自定义情景: {name}",
            duration_days=duration_days,
            factor_shocks=factor_shocks,
            correlation_changes={},
            volatility_changes={},
            probability=probability,
            severity='medium',
            created_at=datetime.now()
        )
    
    def create_scenario_library(self) -> List[ScenarioDefinition]:
        """创建情景库"""
        scenarios = []
        
        for key in self.historical_scenarios:
            scenarios.append(self.create_historical_scenario(key))
        
        scenarios.append(self.create_hypothetical_scenario(
            "利率上升情景",
            {'market': -0.15, 'value': -0.10, 'growth': -0.20},
            volatility_multiplier=1.5
        ))
        
        scenarios.append(self.create_hypothetical_scenario(
            "通胀加剧情景",
            {'market': -0.20, 'value': 0.05, 'inflation': 0.15},
            volatility_multiplier=2.0
        ))
        
        scenarios.append(self.create_extreme_scenario("黑天鹅事件"))
        
        return scenarios
```

---

### 2.2 情景模拟引擎

#### 2.2.1 核心原理

**情景模拟模型**：

```
蒙特卡洛模拟:
R_scenario ~ N(μ_scenario, Σ_scenario)
其中:
μ_scenario = μ_base + Factor_Exposure  Factor_Shock
Σ_scenario = Σ_base  Volatility_Multiplier

历史模拟:
R_scenario = Historical_Returns[Scenario_Period]

因子情景模拟:
R_asset = α + Σ β_i  (F_i + ΔF_i) + ε

压力测试:
Impact = Portfolio_Value  Σ (w_i  ΔP_i)
```

#### 2.2.2 技术实现

```python
@dataclass
class SimulationResult:
    """模拟结果"""
    scenario_id: str
    portfolio_id: str
    simulated_returns: np.ndarray    # 模拟收益序列
    final_values: np.ndarray         # 最终组合价值
    statistics: Dict                 # 统计指标
    timestamp: datetime

class ScenarioSimulationEngine:
    """情景模拟引擎"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.n_simulations = config.get('n_simulations', 10000)
        
    def run_monte_carlo_simulation(self, 
                                  scenario: ScenarioDefinition,
                                  portfolio_weights: Dict[str, float],
                                  factor_exposures: pd.DataFrame,
                                  base_returns: pd.Series,
                                  base_covariance: pd.DataFrame) -> SimulationResult:
        """执行蒙特卡洛模拟"""
        
        n_assets = len(portfolio_weights)
        assets = list(portfolio_weights.keys())
        
        scenario_mean = self._calculate_scenario_mean(
            portfolio_weights, factor_exposures, scenario
        )
        
        scenario_cov = self._calculate_scenario_covariance(
            base_covariance, scenario
        )
        
        simulated_returns = np.random.multivariate_normal(
            scenario_mean,
            scenario_cov,
            size=self.n_simulations
        )
        
        portfolio_returns = simulated_returns @ np.array(list(portfolio_weights.values()))
        
        final_values = 1000000 * (1 + portfolio_returns)
        
        statistics = {
            'mean_return': np.mean(portfolio_returns),
            'median_return': np.median(portfolio_returns),
            'std_return': np.std(portfolio_returns),
            'var_95': np.percentile(portfolio_returns, 5),
            'var_99': np.percentile(portfolio_returns, 1),
            'cvar_95': np.mean(portfolio_returns[portfolio_returns < np.percentile(portfolio_returns, 5)]),
            'max_drawdown': self._calculate_max_drawdown(portfolio_returns),
            'positive_pct': np.mean(portfolio_returns > 0)
        }
        
        return SimulationResult(
            scenario_id=scenario.scenario_id,
            portfolio_id='PORTFOLIO_001',
            simulated_returns=portfolio_returns,
            final_values=final_values,
            statistics=statistics,
            timestamp=datetime.now()
        )
    
    def _calculate_scenario_mean(self, 
                                portfolio_weights: Dict[str, float],
                                factor_exposures: pd.DataFrame,
                                scenario: ScenarioDefinition) -> np.ndarray:
        """计算情景均值"""
        n_assets = len(portfolio_weights)
        assets = list(portfolio_weights.keys())
        
        base_mean = np.zeros(n_assets)
        
        for i, asset in enumerate(assets):
            exposures = factor_exposures.loc[asset] if asset in factor_exposures.index else pd.Series()
            
            shock_impact = 0
            for factor, shock in scenario.factor_shocks.items():
                exposure = exposures.get(factor, 0)
                shock_impact += exposure * shock
            
            base_mean[i] = shock_impact
        
        return base_mean
    
    def _calculate_scenario_covariance(self, 
                                      base_covariance: pd.DataFrame,
                                      scenario: ScenarioDefinition) -> np.ndarray:
        """计算情景协方差"""
        scenario_cov = base_covariance.values.copy()
        
        vol_multiplier = scenario.volatility_changes.get('all', 1.0)
        scenario_cov = scenario_cov * (vol_multiplier ** 2)
        
        if scenario.correlation_changes:
            shift = scenario.correlation_changes.get('shift', 0)
            if shift != 0:
                n = scenario_cov.shape[0]
                std_diag = np.sqrt(np.diag(scenario_cov))
                corr = scenario_cov / np.outer(std_diag, std_diag)
                corr = np.clip(corr + shift, -1, 1)
                scenario_cov = corr * np.outer(std_diag, std_diag)
        
        return scenario_cov
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """计算最大回撤"""
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = (cumulative - running_max) / running_max
        return np.min(drawdowns)
    
    def run_historical_simulation(self, 
                                 scenario: ScenarioDefinition,
                                 portfolio_weights: Dict[str, float],
                                 historical_returns: pd.DataFrame,
                                 scenario_period: Tuple[str, str]) -> SimulationResult:
        """执行历史模拟"""
        start_date, end_date = scenario_period
        
        period_returns = historical_returns.loc[start_date:end_date]
        
        weights = np.array(list(portfolio_weights.values()))
        portfolio_returns = period_returns.values @ weights
        
        n_simulations = len(portfolio_returns)
        
        final_values = 1000000 * np.cumprod(1 + portfolio_returns)
        
        statistics = {
            'mean_return': np.mean(portfolio_returns),
            'median_return': np.median(portfolio_returns),
            'std_return': np.std(portfolio_returns),
            'var_95': np.percentile(portfolio_returns, 5),
            'var_99': np.percentile(portfolio_returns, 1),
            'max_drawdown': self._calculate_max_drawdown(portfolio_returns),
            'period_days': n_simulations
        }
        
        return SimulationResult(
            scenario_id=scenario.scenario_id,
            portfolio_id='PORTFOLIO_001',
            simulated_returns=portfolio_returns,
            final_values=final_values,
            statistics=statistics,
            timestamp=datetime.now()
        )
    
    def run_factor_shock_simulation(self, 
                                   scenario: ScenarioDefinition,
                                   portfolio_weights: Dict[str, float],
                                   factor_exposures: pd.DataFrame,
                                   factor_returns: pd.DataFrame) -> SimulationResult:
        """执行因子冲击模拟"""
        assets = list(portfolio_weights.keys())
        weights = np.array(list(portfolio_weights.values()))
        
        portfolio_exposures = np.zeros(len(scenario.factor_shocks))
        factors = list(scenario.factor_shocks.keys())
        
        for i, factor in enumerate(factors):
            for j, asset in enumerate(assets):
                exposure = factor_exposures.loc[asset, factor] if asset in factor_exposures.index else 0
                portfolio_exposures[i] += weights[j] * exposure
        
        factor_shocks = np.array([scenario.factor_shocks[f] for f in factors])
        
        portfolio_shock = portfolio_exposures @ factor_shocks
        
        n_simulations = self.n_simulations
        simulated_returns = np.random.normal(
            portfolio_shock,
            abs(portfolio_shock) * 0.5,
            n_simulations
        )
        
        final_values = 1000000 * (1 + simulated_returns)
        
        statistics = {
            'expected_shock': portfolio_shock,
            'mean_return': np.mean(simulated_returns),
            'var_95': np.percentile(simulated_returns, 5),
            'var_99': np.percentile(simulated_returns, 1)
        }
        
        return SimulationResult(
            scenario_id=scenario.scenario_id,
            portfolio_id='PORTFOLIO_001',
            simulated_returns=simulated_returns,
            final_values=final_values,
            statistics=statistics,
            timestamp=datetime.now()
        )
    
    def run_stress_test(self, 
                       scenario: ScenarioDefinition,
                       portfolio_positions: Dict[str, Dict],
                       shock_function: callable = None) -> SimulationResult:
        """执行压力测试"""
        total_impact = 0
        asset_impacts = {}
        
        for asset, position in portfolio_positions.items():
            quantity = position['quantity']
            current_price = position['price']
            current_value = quantity * current_price
            
            asset_shock = 0
            for factor, shock in scenario.factor_shocks.items():
                beta = position.get(f'beta_{factor}', 1.0)
                asset_shock += beta * shock
            
            price_change = current_price * asset_shock
            impact = quantity * price_change
            
            asset_impacts[asset] = {
                'current_value': current_value,
                'price_change_pct': asset_shock,
                'impact': impact
            }
            
            total_impact += impact
        
        portfolio_value = sum(p['quantity'] * p['price'] for p in portfolio_positions.values())
        portfolio_return = total_impact / portfolio_value
        
        simulated_returns = np.array([portfolio_return])
        
        statistics = {
            'total_impact': total_impact,
            'portfolio_return': portfolio_return,
            'asset_impacts': asset_impacts,
            'portfolio_value': portfolio_value
        }
        
        return SimulationResult(
            scenario_id=scenario.scenario_id,
            portfolio_id='PORTFOLIO_001',
            simulated_returns=simulated_returns,
            final_values=np.array([portfolio_value + total_impact]),
            statistics=statistics,
            timestamp=datetime.now()
        )
```

---

### 2.3 情景影响评估系统

#### 2.3.1 核心原理

**影响评估模型**：

```
收益分布分析:
P(R < R_threshold) = ∫_{-∞}^{R_threshold} f(R) dR

风险指标:
VaR_α = percentile(R, α)
CVaR_α = E[R | R < VaR_α]
MaxDD = max(peak - trough) / peak

流动性影响:
Liquidity_Impact = Σ (Position_i / ADV_i)  Impact_Factor

敞口变化:
Exposure_Change = Σ |w_new_i - w_current_i|
```

#### 2.3.2 技术实现

```python
@dataclass
class ImpactAssessment:
    """影响评估结果"""
    scenario_id: str
    portfolio_id: str
    return_distribution: Dict
    risk_metrics: Dict
    liquidity_impact: Dict
    exposure_changes: Dict
    overall_severity: str
    recommendations: List[str]
    timestamp: datetime

class ImpactAssessmentEngine:
    """影响评估引擎"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    def assess_impact(self, 
                     simulation_result: SimulationResult,
                     portfolio_positions: Dict[str, Dict],
                     current_risk_metrics: Dict) -> ImpactAssessment:
        """评估情景影响"""
        
        return_dist = self._analyze_return_distribution(
            simulation_result.simulated_returns
        )
        
        risk_metrics = self._calculate_risk_metrics(
            simulation_result.simulated_returns,
            current_risk_metrics
        )
        
        liquidity_impact = self._assess_liquidity_impact(
            portfolio_positions,
            simulation_result.statistics
        )
        
        exposure_changes = self._analyze_exposure_changes(
            portfolio_positions,
            simulation_result.statistics
        )
        
        severity = self._determine_severity(
            return_dist, risk_metrics, liquidity_impact
        )
        
        recommendations = self._generate_recommendations(
            severity, risk_metrics, liquidity_impact
        )
        
        return ImpactAssessment(
            scenario_id=simulation_result.scenario_id,
            portfolio_id=simulation_result.portfolio_id,
            return_distribution=return_dist,
            risk_metrics=risk_metrics,
            liquidity_impact=liquidity_impact,
            exposure_changes=exposure_changes,
            overall_severity=severity,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _analyze_return_distribution(self, 
                                    simulated_returns: np.ndarray) -> Dict:
        """分析收益分布"""
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        
        return {
            'mean': np.mean(simulated_returns),
            'std': np.std(simulated_returns),
            'skewness': self._calculate_skewness(simulated_returns),
            'kurtosis': self._calculate_kurtosis(simulated_returns),
            'percentiles': {
                f'p{p}': np.percentile(simulated_returns, p) 
                for p in percentiles
            },
            'worst_case': np.min(simulated_returns),
            'best_case': np.max(simulated_returns)
        }
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """计算偏度"""
        n = len(data)
        mean = np.mean(data)
        std = np.std(data)
        return np.sum(((data - mean) / std) ** 3) / n
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """计算峰度"""
        n = len(data)
        mean = np.mean(data)
        std = np.std(data)
        return np.sum(((data - mean) / std) ** 4) / n - 3
    
    def _calculate_risk_metrics(self, 
                               simulated_returns: np.ndarray,
                               current_metrics: Dict) -> Dict:
        """计算风险指标"""
        var_95 = np.percentile(simulated_returns, 5)
        var_99 = np.percentile(simulated_returns, 1)
        
        cvar_95 = np.mean(simulated_returns[simulated_returns <= var_95])
        cvar_99 = np.mean(simulated_returns[simulated_returns <= var_99])
        
        max_dd = self._calculate_max_drawdown(simulated_returns)
        
        current_var = current_metrics.get('var_95', -0.05)
        var_change = (var_95 - current_var) / abs(current_var) if current_var != 0 else 0
        
        return {
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'max_drawdown': max_dd,
            'var_change_pct': var_change,
            'risk_increase': var_change > 0.5
        }
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """计算最大回撤"""
        if len(returns) < 2:
            return 0.0
        
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = (cumulative - running_max) / running_max
        return np.min(drawdowns)
    
    def _assess_liquidity_impact(self, 
                                portfolio_positions: Dict[str, Dict],
                                statistics: Dict) -> Dict:
        """评估流动性影响"""
        total_position = sum(p['quantity'] * p['price'] for p in portfolio_positions.values())
        
        liquidity_scores = {}
        for asset, position in portfolio_positions.items():
            adv = position.get('adv', position['quantity'] * position['price'] * 10)
            position_value = position['quantity'] * position['price']
            participation = position_value / adv if adv > 0 else 1.0
            
            liquidity_scores[asset] = {
                'participation_rate': participation,
                'liquidity_risk': 'high' if participation > 0.1 else 'medium' if participation > 0.05 else 'low'
            }
        
        high_risk_count = sum(1 for s in liquidity_scores.values() if s['liquidity_risk'] == 'high')
        
        return {
            'asset_liquidity': liquidity_scores,
            'high_risk_assets': high_risk_count,
            'overall_liquidity_risk': 'high' if high_risk_count > 3 else 'medium' if high_risk_count > 0 else 'low'
        }
    
    def _analyze_exposure_changes(self, 
                                 portfolio_positions: Dict[str, Dict],
                                 statistics: Dict) -> Dict:
        """分析敞口变化"""
        return {
            'equity_exposure_change': statistics.get('expected_shock', 0),
            'factor_exposure_changes': {},
            'concentration_change': 0
        }
    
    def _determine_severity(self, 
                           return_dist: Dict,
                           risk_metrics: Dict,
                           liquidity_impact: Dict) -> str:
        """确定严重程度"""
        var_95 = risk_metrics['var_95']
        
        if var_95 < -0.30 or liquidity_impact['overall_liquidity_risk'] == 'high':
            return 'critical'
        elif var_95 < -0.20:
            return 'high'
        elif var_95 < -0.10:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, 
                                 severity: str,
                                 risk_metrics: Dict,
                                 liquidity_impact: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if severity == 'critical':
            recommendations.append("立即降低仓位，减少风险敞口")
            recommendations.append("考虑购买看跌期权对冲尾部风险")
        
        if risk_metrics['var_change_pct'] > 0.5:
            recommendations.append("风险显著增加，建议重新评估风险预算")
        
        if liquidity_impact['overall_liquidity_risk'] == 'high':
            recommendations.append("部分资产流动性风险较高，建议分批减仓")
        
        if risk_metrics['max_drawdown'] < -0.20:
            recommendations.append("潜在最大回撤较大，建议设置止损")
        
        if not recommendations:
            recommendations.append("组合在当前情景下表现稳健")
        
        return recommendations
```

---

### 2.4 应对策略生成系统

```python
@dataclass
class MitigationStrategy:
    """缓释策略"""
    strategy_id: str
    scenario_id: str
    strategy_type: str
    actions: List[Dict]
    expected_impact: Dict
    implementation_cost: float
    priority: int
    timestamp: datetime

class MitigationStrategyGenerator:
    """应对策略生成器"""
    
    def __init__(self):
        pass
        
    def generate_strategies(self, 
                           assessment: ImpactAssessment,
                           portfolio_positions: Dict[str, Dict]) -> List[MitigationStrategy]:
        """生成应对策略"""
        strategies = []
        
        if assessment.overall_severity in ['critical', 'high']:
            hedge_strategy = self._generate_hedge_strategy(
                assessment, portfolio_positions
            )
            strategies.append(hedge_strategy)
        
        position_strategy = self._generate_position_adjustment(
            assessment, portfolio_positions
        )
        strategies.append(position_strategy)
        
        risk_strategy = self._generate_risk_mitigation(
            assessment, portfolio_positions
        )
        strategies.append(risk_strategy)
        
        strategies.sort(key=lambda x: x.priority)
        
        return strategies
    
    def _generate_hedge_strategy(self, 
                                assessment: ImpactAssessment,
                                positions: Dict[str, Dict]) -> MitigationStrategy:
        """生成对冲策略"""
        total_value = sum(p['quantity'] * p['price'] for p in positions.values())
        
        actions = [
            {
                'action': 'buy_put',
                'underlying': 'HS300ETF',
                'quantity': int(total_value * 0.3 / 10000),
                'strike_pct': 0.95,
                'expected_cost': total_value * 0.3 * 0.02
            }
        ]
        
        return MitigationStrategy(
            strategy_id=f"HEDGE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            scenario_id=assessment.scenario_id,
            strategy_type='hedge',
            actions=actions,
            expected_impact={
                'var_reduction': 0.3,
                'max_loss_limit': 0.15
            },
            implementation_cost=total_value * 0.006,
            priority=1,
            timestamp=datetime.now()
        )
    
    def _generate_position_adjustment(self, 
                                     assessment: ImpactAssessment,
                                     positions: Dict[str, Dict]) -> MitigationStrategy:
        """生成仓位调整策略"""
        actions = []
        
        for asset, position in positions.items():
            if position.get('risk_contribution', 0) > 0.1:
                actions.append({
                    'action': 'reduce',
                    'asset': asset,
                    'current_weight': position['weight'],
                    'target_weight': position['weight'] * 0.7,
                    'reason': '高风险贡献资产减仓'
                })
        
        return MitigationStrategy(
            strategy_id=f"POS_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            scenario_id=assessment.scenario_id,
            strategy_type='position_adjustment',
            actions=actions,
            expected_impact={
                'risk_reduction': 0.2,
                'return_impact': -0.02
            },
            implementation_cost=0,
            priority=2,
            timestamp=datetime.now()
        )
    
    def _generate_risk_mitigation(self, 
                                 assessment: ImpactAssessment,
                                 positions: Dict[str, Dict]) -> MitigationStrategy:
        """生成风险缓释策略"""
        actions = [
            {
                'action': 'set_stop_loss',
                'level': -0.10,
                'scope': 'all'
            },
            {
                'action': 'reduce_leverage',
                'target_leverage': 1.0
            }
        ]
        
        return MitigationStrategy(
            strategy_id=f"RISK_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            scenario_id=assessment.scenario_id,
            strategy_type='risk_mitigation',
            actions=actions,
            expected_impact={
                'max_loss_limit': 0.10,
                'margin_improvement': 0.2
            },
            implementation_cost=0,
            priority=3,
            timestamp=datetime.now()
        )
```

---

## 三、与其他模块的集成

### 3.1 与Layer 11.2风险预算的集成

```
Layer 11.2 风险预算
    ↓ 风险预算约束
Layer 11.12 情景分析
    ├── 情景下风险预算检查
    ├── 风险预算超限预警
    └── 返回调整建议
    ↓ 调整建议
Layer 11.1 战略资产配置
```

### 3.2 与Layer 11.5投资组合保险的集成

```
Layer 11.12 情景分析
    ↓ 极端情景识别
Layer 11.5 投资组合保险
    ├── 触发保险机制
    ├── 调整保护层
    └── 返回保险状态
    ↓ 保险状态
Layer 8 监控报告
```

### 3.3 与Layer 11.8流动性管理的集成

```
Layer 11.12 情景分析
    ↓ 流动性影响评估
Layer 11.8 流动性管理
    ├── 流动性压力测试
    ├── 流动性预警
    └── 返回流动性状态
    ↓ 流动性状态
Layer 11.4 战略调整决策
```

---

## 四、实施路径

### 4.1 Phase 1: 核心功能（3天）

| 任务 | 时间 | 交付成果 |
|------|------|---------|
| 情景构建引擎 | 1天 | 情景定义功能 |
| 模拟引擎 | 1天 | 模拟计算功能 |
| 影响评估 | 1天 | 评估功能 |

### 4.2 Phase 2: 策略与报告（2天）

| 任务 | 时间 | 交付成果 |
|------|------|---------|
| 策略生成 | 1天 | 应对策略功能 |
| 报告系统 | 1天 | 报告生成功能 |

---

## 五、A股市场特色功能

### 5.1 涨跌停情景

```python
class LimitUpDownScenario:
    """涨跌停情景分析"""
    
    def create_limit_scenario(self, 
                             limit_type: str = 'down') -> ScenarioDefinition:
        """创建涨跌停情景"""
        if limit_type == 'down':
            factor_shocks = {
                'market': -0.10,
                'sentiment': -0.30
            }
        else:
            factor_shocks = {
                'market': 0.10,
                'sentiment': 0.30
            }
        
        return ScenarioDefinition(
            scenario_id=f"LIMIT_{limit_type.upper()}",
            scenario_name=f"{'跌停' if limit_type == 'down' else '涨停'}情景",
            scenario_type=ScenarioType.HYPOTHETICAL,
            description="涨跌停板限制下的情景分析",
            duration_days=1,
            factor_shocks=factor_shocks,
            correlation_changes={},
            volatility_changes={'all': 2.0},
            probability=0.05,
            severity='medium',
            created_at=datetime.now()
        )
```

### 5.2 政策冲击情景

```python
class PolicyShockScenario:
    """政策冲击情景"""
    
    def create_policy_scenario(self, 
                              policy_type: str) -> ScenarioDefinition:
        """创建政策冲击情景"""
        policy_shocks = {
            'monetary_tighten': {
                'market': -0.15,
                'rate_sensitive': -0.25,
                'financial': -0.20
            },
            'regulation_tighten': {
                'market': -0.10,
                'regulated_sector': -0.30
            },
            'stimulus': {
                'market': 0.10,
                'infrastructure': 0.20
            }
        }
        
        shocks = policy_shocks.get(policy_type, {'market': -0.10})
        
        return ScenarioDefinition(
            scenario_id=f"POLICY_{policy_type.upper()}",
            scenario_name=f"政策冲击: {policy_type}",
            scenario_type=ScenarioType.HYPOTHETICAL,
            description=f"政策变化情景: {policy_type}",
            duration_days=30,
            factor_shocks=shocks,
            correlation_changes={'shift': 0.1},
            volatility_changes={'all': 1.5},
            probability=0.10,
            severity='medium',
            created_at=datetime.now()
        )
```

---

## 六、风险评估

### 6.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| **模型假设失效** | 高 | 多模型验证 |
| **参数估计误差** | 中 | 敏感性分析 |
| **计算性能** | 低 | 分布式计算 |

### 6.2 业务风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| **情景覆盖不全** | 中 | 定期更新情景库 |
| **误判风险** | 中 | 多情景交叉验证 |
| **过度反应** | 低 | 人工审核机制 |

---

## 七、质量保证

### 7.1 测试标准

| 测试类型 | 覆盖率要求 | 通过标准 |
|---------|-----------|---------|
| **单元测试** | ≥85% | 所有测试通过 |
| **集成测试** | ≥80% | 关键路径通过 |
| **情景验证** | 历史情景 | 误差<10% |

### 7.2 监控指标

| 指标 | 目标值 | 监控频率 |
|------|--------|---------|
| **模拟准确率** | >90% | 月频 |
| **预警准确率** | >85% | 季频 |
| **报告生成时间** | <60秒 | 实时 |

---

## 八、相关文档

| 文档 | 说明 |
|------|------|
| BLUEPRINT.md | Layer 11主蓝图 |
| [ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) | 系统架构 |
| [LIQUIDITY_MANAGEMENT_BLUEPRINT.md](./LIQUIDITY_MANAGEMENT_BLUEPRINT.md) | 流动性管理系统 |
| [PORTFOLIO_INSURANCE_BLUEPRINT.md](./PORTFOLIO_INSURANCE_BLUEPRINT.md) | 投资组合保险系统 |

---

## 九、版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v1.0 | 2026-04-06 | 初始版本，完成情景分析系统设计 |

---

**文档状态**: ✅ 设计完成  
**下一步**: 更新Layer 11主蓝图文档
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Scenario Analysis Blueprint
- **模块ID**: SCENARIO_ANALYSIS_BLUEPRINT_001
- **蓝图文档**: SCENARIO_ANALYSIS_BLUEPRINT.md
- **技术规格书**: 待创建
- **职责**: Layer 11.12 - 情景分析系统
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Scenario Analysis Blueprint** | Layer 11.12 - 情景分析系统 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
