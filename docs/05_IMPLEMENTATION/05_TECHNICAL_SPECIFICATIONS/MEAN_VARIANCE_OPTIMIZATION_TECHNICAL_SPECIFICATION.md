---
module_id: MEAN_VARIANCE_OPTIMIZATION_TECH_SPEC_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MEAN_VARIANCE_OPTIMIZATION_BLUEPRINT.md
last_updated: 2026-04-07
created_date: 2026-04-07
layer: Layer 6 (组合优化层)
index: MEAN_VARIANCE_OPTIMIZATION_TECH_SPEC_001
estimated_hours: 20
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-07
owner: 实施团队
responsibility:
  - 实施指南、部署文档
  - 均值方差优化实现
  - 有效前沿计算
standard_type: 专业量化机构技术规格书
applicable_scope: Layer 6 组合优化层
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 待实施
---

# Mean Variance Optimization技术规格书 v1.0

> **核心职责**: 均值方差优化详细技术实现规范
> **职责边界**: 
> - ✅ 本文档负责：均值方差优化、有效前沿计算、最优组合求解
> - ❌ 本文档不负责：因子中性约束、鲁棒优化、交易成本建模

> 清风量化系统 v5.3 - Mean Variance Optimization详细技术设计
> **索引**: `MEAN_VARIANCE_OPTIMIZATION_TECH_SPEC_001`
> **开发工时**: 20h
> **核心定位**: 基于Markowitz理论的组合优化技术实现

---

## 1. 概述

### 1.1 设计背景与业务目标
- **业务需求**: 实现Markowitz均值方差优化理论，提供有效前沿计算和最优组合求解能力
- **技术痛点**: 
  - 参数估计敏感：预期收益和协方差估计误差对优化结果影响大
  - 约束处理复杂：需要支持多种约束条件（权重、行业、杠杆等）
  - 数值稳定性：协方差矩阵可能病态导致优化失败
  - 离散化问题：连续权重转换为实际可交易数量
- **预期收益**: 
  - 提供标准化的均值方差优化框架
  - 支持多种优化目标（最大夏普、最小方差、有效前沿）
  - 实现灵活的约束处理机制

### 1.2 技术定位与架构层归属
- **Layer定位**: Layer 6 - 组合优化层 (符合ARCHITECTURE.md定义)
- **模块类别**: 核心组合优化模块
- **架构角色**: Layer 6组合优化基础，提供均值方差优化核心能力

### 1.3 版本信息
| 版本 | 日期 | 作者 | 变更说明 | 状态 |
|------|------|------|----------|------|
| v1.0.0 | 2026-04-07 | 实施团队 | 初始版本 | Active |

---

## 2. 详细架构设计

### 2.1 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                   Layer 6: 组合优化层                        │
├─────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       MeanVarianceOptimizer (主模块)                 │  │
│  │ - 有效前沿计算                                        │  │
│  │ - 最优组合求解                                        │  │
│  │ - 约束处理                                            │  │
│  │ - 离散分配                                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         核心组件                                      │  │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │  │
│  │ │EfficientFron│ │OptimalPortfo│ │ConstraintHan│     │  │
│  │ │有效前沿计算 │ │最优组合求解 │ │约束处理器   │     │  │
│  │ └─────────────┘ └─────────────┘ └─────────────┘     │  │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │  │
│  │ │ExpectedRetE │ │CovarianceEs │ │DiscreteAlloc│     │  │
│  │ │预期收益估计 │ │协方差估计   │ │离散分配转换 │     │  │
│  │ └─────────────┘ └─────────────┘ └─────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         第三方库集成                                  │  │
│  │ - PyPortfolioOpt (均值方差优化核心)                  │  │
│  │ - CVXPY (凸优化求解)                                 │  │
│  │ - NumPy (数值计算)                                   │  │
│  │ - Pandas (数据处理)                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Layer定位详细说明
- **Layer归属**: Layer 6 - 组合优化层
- **职责范围**: 均值方差优化、有效前沿计算、最优组合求解、约束处理
- **上下层接口**: 
  - 上层依赖: Layer 5 交易成本层 (提供交易成本约束)
  - 下层依赖: Layer 7 风险管理层 (接收优化结果进行风险监控)

### 2.3 模块职责与边界定义
- **核心职责**: 均值方差优化、有效前沿计算、最优组合求解
- **职责边界**: 
  - ✓本模块负责: 均值方差优化、有效前沿计算、最优组合求解
  - ✗本模块不负责: 因子中性约束、鲁棒优化、交易成本建模
- **接口契约**: 提供统一的Python API接口

### 2.4 依赖关系
| 依赖模块 | 依赖类型 | 接口方式 | 版本要求 | 备注 |
|----------|----------|----------|----------|------|
| PyPortfolioOpt | 强依赖 | Python包 | >=1.5.0 | 均值方差优化核心 |
| CVXPY | 强依赖 | Python包 | >=1.4.0 | 凸优化求解 |
| NumPy | 强依赖 | Python包 | >=1.24.0 | 数值计算 |
| Pandas | 强依赖 | Python包 | >=2.0.0 | 数据处理 |
| SciPy | 强依赖 | Python包 | >=1.10.0 | 优化求解 |

---

## 3. 接口定义

### 3.1 API接口规范

#### 3.1.1 主接口类
```python
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
import logging


class OptimizationObjective(Enum):
    """优化目标枚举"""
    MAX_SHARPE = "max_sharpe"
    MIN_VOLATILITY = "min_volatility"
    MAX_QUADRATIC_UTILITY = "max_quadratic_utility"
    EFFICIENT_RISK = "efficient_risk"
    EFFICIENT_RETURN = "efficient_return"


class CovarianceMethod(Enum):
    """协方差估计方法枚举"""
    SAMPLE = "sample_cov"
    SEMICOVARIANCE = "semicovariance"
    EXP_COV = "exp_cov"
    LEDOIT_WOLF = "ledoit_wolf"
    ORACLE_APPROX = "oracle_approximating"


class ExpectedReturnMethod(Enum):
    """预期收益估计方法枚举"""
    MEAN_HISTORICAL = "mean_historical"
    EMA_HISTORICAL = "ema_historical"
    CAPM = "capm"


@dataclass
class OptimizationConfig:
    """优化配置"""
    objective: OptimizationObjective
    risk_free_rate: float = 0.02
    weight_bounds: Tuple[float, float] = (0.0, 1.0)
    sector_constraints: Optional[Dict[str, Tuple[float, float]]] = None
    max_leverage: float = 1.0
    target_volatility: Optional[float] = None
    target_return: Optional[float] = None


@dataclass
class OptimizationResult:
    """优化结果"""
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    risk_contribution: Dict[str, float]
    optimization_time: float
    timestamp: datetime


class ExpectedReturnsEstimator:
    """预期收益估计器"""
    
    def __init__(self, method: ExpectedReturnMethod = ExpectedReturnMethod.MEAN_HISTORICAL):
        self.method = method
        self.logger = logging.getLogger(__name__)
    
    def estimate(
        self,
        prices: pd.DataFrame,
        frequency: int = 252,
        **kwargs
    ) -> pd.Series:
        """
        估计预期收益
        
        参数:
            prices: 价格数据
            frequency: 年化频率
            **kwargs: 其他参数
            
        返回:
            预期收益序列
        """
        from pypfopt import expected_returns
        
        if self.method == ExpectedReturnMethod.MEAN_HISTORICAL:
            returns = expected_returns.mean_historical_return(
                prices, frequency=frequency
            )
        elif self.method == ExpectedReturnMethod.EMA_HISTORICAL:
            span = kwargs.get("span", 500)
            returns = expected_returns.ema_historical_return(
                prices, span=span, frequency=frequency
            )
        elif self.method == ExpectedReturnMethod.CAPM:
            market_prices = kwargs.get("market_prices")
            returns = expected_returns.capm_return(
                prices, market_prices=market_prices, 
                risk_free_rate=kwargs.get("risk_free_rate", 0.02),
                frequency=frequency
            )
        else:
            returns = expected_returns.mean_historical_return(
                prices, frequency=frequency
            )
        
        self.logger.info(f"预期收益估计完成，方法={self.method.value}")
        
        return returns


class CovarianceEstimator:
    """协方差估计器"""
    
    def __init__(self, method: CovarianceMethod = CovarianceMethod.LEDOIT_WOLF):
        self.method = method
        self.logger = logging.getLogger(__name__)
    
    def estimate(
        self,
        prices: pd.DataFrame,
        frequency: int = 252,
        **kwargs
    ) -> pd.DataFrame:
        """
        估计协方差矩阵
        
        参数:
            prices: 价格数据
            frequency: 年化频率
            **kwargs: 其他参数
            
        返回:
            协方差矩阵
        """
        from pypfopt import risk_models
        
        returns = prices.pct_change().dropna()
        
        if self.method == CovarianceMethod.SAMPLE:
            cov = risk_models.sample_cov(returns, frequency=frequency)
        elif self.method == CovarianceMethod.SEMICOVARIANCE:
            benchmark = kwargs.get("benchmark", 0.0)
            cov = risk_models.semicovariance(
                returns, benchmark=benchmark, frequency=frequency
            )
        elif self.method == CovarianceMethod.EXP_COV:
            span = kwargs.get("span", 180)
            cov = risk_models.exp_cov(returns, span=span, frequency=frequency)
        elif self.method == CovarianceMethod.LEDOIT_WOLF:
            cov = risk_models.CovarianceShrinkage(
                returns, frequency=frequency
            ).ledoit_wolf()
        elif self.method == CovarianceMethod.ORACLE_APPROX:
            cov = risk_models.CovarianceShrinkage(
                returns, frequency=frequency
            ).oracle_approximating()
        else:
            cov = risk_models.sample_cov(returns, frequency=frequency)
        
        self.logger.info(f"协方差估计完成，方法={self.method.value}")
        
        return cov


class EfficientFrontierCalculator:
    """有效前沿计算器"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        self.logger = logging.getLogger(__name__)
    
    def calculate(
        self,
        expected_returns: pd.Series,
        covariance_matrix: pd.DataFrame,
        n_points: int = 100,
        weight_bounds: Tuple[float, float] = (0.0, 1.0)
    ) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, float]]]:
        """
        计算有效前沿
        
        参数:
            expected_returns: 预期收益
            covariance_matrix: 协方差矩阵
            n_points: 有效前沿点数
            weight_bounds: 权重边界
            
        返回:
            (收益率数组, 波动率数组, 权重列表)
        """
        from pypfopt import EfficientFrontier
        
        min_vol_ef = EfficientFrontier(
            expected_returns, covariance_matrix, weight_bounds=weight_bounds
        )
        min_vol_weights = min_vol_ef.min_volatility()
        min_vol_performance = min_vol_ef.portfolio_performance(risk_free_rate=self.risk_free_rate)
        min_vol = min_vol_performance[1]
        
        max_ret_ef = EfficientFrontier(
            expected_returns, covariance_matrix, weight_bounds=weight_bounds
        )
        max_ret_weights = max_ret_ef.efficient_return(min_vol_performance[0] + 0.5)
        max_ret_performance = max_ret_ef.portfolio_performance(risk_free_rate=self.risk_free_rate)
        max_vol = max_ret_performance[1]
        
        target_vols = np.linspace(min_vol, max_vol, n_points)
        
        returns = []
        volatilities = []
        weights_list = []
        
        for target_vol in target_vols:
            ef = EfficientFrontier(
                expected_returns, covariance_matrix, weight_bounds=weight_bounds
            )
            try:
                ef.efficient_risk(target_vol)
                weights = ef.clean_weights()
                performance = ef.portfolio_performance(risk_free_rate=self.risk_free_rate)
                
                returns.append(performance[0])
                volatilities.append(performance[1])
                weights_list.append(weights)
            except Exception as e:
                self.logger.warning(f"目标波动率 {target_vol} 优化失败: {e}")
        
        self.logger.info(f"有效前沿计算完成，{len(returns)}个点")
        
        return np.array(returns), np.array(volatilities), weights_list


class OptimalPortfolioSolver:
    """最优组合求解器"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def solve(
        self,
        expected_returns: pd.Series,
        covariance_matrix: pd.DataFrame
    ) -> OptimizationResult:
        """
        求解最优组合
        
        参数:
            expected_returns: 预期收益
            covariance_matrix: 协方差矩阵
            
        返回:
            优化结果
        """
        from pypfopt import EfficientFrontier
        
        start_time = datetime.now()
        
        ef = EfficientFrontier(
            expected_returns, 
            covariance_matrix,
            weight_bounds=self.config.weight_bounds
        )
        
        if self.config.objective == OptimizationObjective.MAX_SHARPE:
            weights = ef.max_sharpe(risk_free_rate=self.config.risk_free_rate)
        elif self.config.objective == OptimizationObjective.MIN_VOLATILITY:
            weights = ef.min_volatility()
        elif self.config.objective == OptimizationObjective.MAX_QUADRATIC_UTILITY:
            risk_aversion = 1.0
            weights = ef.max_quadratic_utility(risk_aversion=risk_aversion)
        elif self.config.objective == OptimizationObjective.EFFICIENT_RISK:
            target_vol = self.config.target_volatility or 0.15
            weights = ef.efficient_risk(target_vol)
        elif self.config.objective == OptimizationObjective.EFFICIENT_RETURN:
            target_ret = self.config.target_return or 0.10
            weights = ef.efficient_return(target_ret)
        else:
            weights = ef.max_sharpe(risk_free_rate=self.config.risk_free_rate)
        
        cleaned_weights = ef.clean_weights()
        
        performance = ef.portfolio_performance(risk_free_rate=self.config.risk_free_rate)
        
        risk_contribution = self._calculate_risk_contribution(
            pd.Series(cleaned_weights), covariance_matrix
        )
        
        end_time = datetime.now()
        optimization_time = (end_time - start_time).total_seconds()
        
        result = OptimizationResult(
            weights=cleaned_weights,
            expected_return=performance[0],
            volatility=performance[1],
            sharpe_ratio=performance[2],
            risk_contribution=risk_contribution,
            optimization_time=optimization_time,
            timestamp=end_time
        )
        
        self.logger.info(f"优化完成，目标={self.config.objective.value}，耗时{optimization_time:.2f}秒")
        
        return result
    
    def _calculate_risk_contribution(
        self,
        weights: pd.Series,
        covariance_matrix: pd.DataFrame
    ) -> Dict[str, float]:
        """计算风险贡献"""
        portfolio_risk = np.sqrt(weights @ covariance_matrix @ weights)
        
        marginal_risk = covariance_matrix @ weights / portfolio_risk
        
        risk_contribution = weights * marginal_risk
        
        return (risk_contribution / portfolio_risk).to_dict()


class ConstraintHandler:
    """约束处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def add_weight_constraint(
        self,
        ef: Any,
        min_weight: float = 0.0,
        max_weight: float = 1.0
    ) -> None:
        """添加权重约束"""
        n_assets = len(ef.tickers)
        
        ef.add_constraint(lambda w: w >= min_weight)
        ef.add_constraint(lambda w: w <= max_weight)
        
        self.logger.info(f"添加权重约束: [{min_weight}, {max_weight}]")
    
    def add_sector_constraint(
        self,
        ef: Any,
        sector_mapping: Dict[str, str],
        sector_weights: Dict[str, Tuple[float, float]]
    ) -> None:
        """添加行业约束"""
        for sector, (min_w, max_w) in sector_weights.items():
            sector_indices = [
                i for i, ticker in enumerate(ef.tickers) 
                if sector_mapping.get(ticker) == sector
            ]
            
            if sector_indices:
                ef.add_constraint(
                    lambda w, idx=sector_indices, min_w=min_w: sum(w[i] for i in idx) >= min_w
                )
                ef.add_constraint(
                    lambda w, idx=sector_indices, max_w=max_w: sum(w[i] for i in idx) <= max_w
                )
        
        self.logger.info(f"添加行业约束: {len(sector_weights)}个行业")
    
    def add_leverage_constraint(
        self,
        ef: Any,
        max_leverage: float = 1.0
    ) -> None:
        """添加杠杆约束"""
        ef.add_constraint(lambda w: sum(abs(wi) for wi in w) <= max_leverage)
        
        self.logger.info(f"添加杠杆约束: 最大杠杆={max_leverage}")


class DiscreteAllocationConverter:
    """离散分配转换器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def convert(
        self,
        weights: Dict[str, float],
        latest_prices: pd.Series,
        total_portfolio_value: float,
        min_ratio: float = 0.01
    ) -> Tuple[Dict[str, int], float]:
        """
        将连续权重转换为离散分配
        
        参数:
            weights: 权重字典
            latest_prices: 最新价格
            total_portfolio_value: 总投资金额
            min_ratio: 最小持仓比例
            
        返回:
            (资产数量字典, 剩余资金)
        """
        from pypfopt import DiscreteAllocation
        
        da = DiscreteAllocation(
            weights, latest_prices, total_portfolio_value=total_portfolio_value
        )
        
        allocation, leftover = da.greedy_portfolio()
        
        self.logger.info(f"离散分配完成，剩余资金={leftover:.2f}")
        
        return allocation, leftover


class MeanVarianceOptimizer:
    """均值方差优化器主类"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        
        self.expected_returns_estimator = ExpectedReturnsEstimator(
            method=ExpectedReturnMethod.MEAN_HISTORICAL
        )
        
        self.covariance_estimator = CovarianceEstimator(
            method=CovarianceMethod.LEDOIT_WOLF
        )
        
        self.efficient_frontier_calculator = EfficientFrontierCalculator(
            risk_free_rate=config.risk_free_rate
        )
        
        self.optimal_solver = OptimalPortfolioSolver(config)
        
        self.constraint_handler = ConstraintHandler()
        
        self.discrete_converter = DiscreteAllocationConverter()
        
        self.logger = logging.getLogger(__name__)
    
    def optimize(
        self,
        prices: pd.DataFrame,
        **kwargs
    ) -> OptimizationResult:
        """
        执行优化
        
        参数:
            prices: 价格数据
            **kwargs: 其他参数
            
        返回:
            优化结果
        """
        expected_returns = self.expected_returns_estimator.estimate(
            prices, **kwargs
        )
        
        covariance_matrix = self.covariance_estimator.estimate(
            prices, **kwargs
        )
        
        result = self.optimal_solver.solve(expected_returns, covariance_matrix)
        
        return result
    
    def get_efficient_frontier(
        self,
        prices: pd.DataFrame,
        n_points: int = 100,
        **kwargs
    ) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, float]]]:
        """
        获取有效前沿
        
        参数:
            prices: 价格数据
            n_points: 点数
            **kwargs: 其他参数
            
        返回:
            (收益率数组, 波动率数组, 权重列表)
        """
        expected_returns = self.expected_returns_estimator.estimate(
            prices, **kwargs
        )
        
        covariance_matrix = self.covariance_estimator.estimate(
            prices, **kwargs
        )
        
        returns, volatilities, weights_list = self.efficient_frontier_calculator.calculate(
            expected_returns, covariance_matrix, n_points
        )
        
        return returns, volatilities, weights_list
```

### 3.2 数据格式与协议定义

#### 3.2.1 输入数据格式
```json
{
  "prices": {
    "format": "DataFrame",
    "columns": ["asset1", "asset2", "..."],
    "index": "datetime",
    "description": "资产历史价格数据"
  },
  "config": {
    "objective": "max_sharpe",
    "risk_free_rate": 0.02,
    "weight_bounds": [0.0, 1.0],
    "target_volatility": null,
    "target_return": null
  }
}
```

#### 3.2.2 输出数据格式
```json
{
  "weights": {
    "format": "Dict[str, float]",
    "example": {"asset1": 0.3, "asset2": 0.25, "..."},
    "description": "优化后的组合权重"
  },
  "expected_return": {
    "format": "float",
    "description": "预期年化收益率"
  },
  "volatility": {
    "format": "float",
    "description": "预期年化波动率"
  },
  "sharpe_ratio": {
    "format": "float",
    "description": "夏普比率"
  }
}
```

### 3.3 性能指标与SLA要求
| 指标 | 目标值 | 测量方法 | 备注 |
|------|--------|----------|------|
| **响应时间** | <300ms | P95延迟 | 100个资产以内 |
| **吞吐量** | 20 QPS | 每秒请求数 | 峰值要求 |
| **可用性** | 99.9% | 每月宕机时间 | SLA要求 |
| **错误率** | <0.1% | 错误请求比例 | 生产环境 |

---

## 4. 数据模型与存储

### 4.1 数据库表结构设计

#### 4.1.1 优化结果存储表
```sql
CREATE TABLE IF NOT EXISTS mv_optimization_results (
    result_id VARCHAR(50) PRIMARY KEY,
    portfolio_id VARCHAR(50) NOT NULL,
    optimization_date TIMESTAMP NOT NULL,
    
    objective VARCHAR(30) NOT NULL,
    weights_json TEXT NOT NULL,
    expected_return DECIMAL(10, 6),
    volatility DECIMAL(10, 6),
    sharpe_ratio DECIMAL(10, 4),
    
    risk_free_rate DECIMAL(5, 4),
    weight_bounds_json TEXT,
    
    covariance_method VARCHAR(30),
    expected_return_method VARCHAR(30),
    
    optimization_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_portfolio (portfolio_id),
    INDEX idx_optimization_date (optimization_date)
);

COMMENT ON TABLE mv_optimization_results IS '均值方差优化结果存储表';
```

#### 4.1.2 有效前沿缓存表
```sql
CREATE TABLE IF NOT EXISTS mv_efficient_frontier (
    frontier_id VARCHAR(50) PRIMARY KEY,
    portfolio_id VARCHAR(50) NOT NULL,
    calculation_date TIMESTAMP NOT NULL,
    
    returns_json TEXT NOT NULL,
    volatilities_json TEXT NOT NULL,
    weights_list_json TEXT NOT NULL,
    
    n_points INTEGER,
    
    valid_until TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_portfolio (portfolio_id),
    INDEX idx_valid_until (valid_until)
);

COMMENT ON TABLE mv_efficient_frontier IS '有效前沿缓存表';
```

### 4.2 缓存策略与数据一致性方案
- **缓存类型**: 内存缓存
- **缓存策略**: TTL=1小时，LRU淘汰
- **一致性保证**: 最终一致性
- **失效策略**: 数据更新时主动失效

---

## 5. 算法实现说明

### 5.1 核心算法原理与数学公式

#### 5.1.1 均值方差优化
```
算法名称: 均值方差优化
数学公式: 
min: w'Σw
s.t.: w'μ >= r_target
      w'1 = 1
      w >= 0

其中:
- w: 权重向量 (n×1)
- Σ: 协方差矩阵 (n×n)
- μ: 预期收益向量 (n×1)
- r_target: 目标收益

时间复杂度: O(n³)
空间复杂度: O(n²)
```

#### 5.1.2 最大夏普比率
```
算法名称: 最大夏普比率
数学公式: 
max: (w'μ - rf) / sqrt(w'Σw)
s.t.: w'1 = 1
      w >= 0

其中:
- rf: 无风险利率

时间复杂度: O(n³)
空间复杂度: O(n²)
```

### 5.2 时间复杂度与空间复杂度分析
| 操作 | 时间复杂度 | 空间复杂度 | 说明 |
|------|------------|------------|------|
| 预期收益估计 | O(T×n) | O(n) | T为时间点数 |
| 协方差估计 | O(T×n²) | O(n²) | T为时间点数 |
| 有效前沿计算 | O(n³×k) | O(n²) | k为点数 |
| 最优组合求解 | O(n³) | O(n²) | 凸优化 |

### 5.3 参数配置与调优指南
```yaml
# 均值方差优化参数配置
mean_variance_params:
  objective: max_sharpe           # 优化目标
  risk_free_rate: 0.02            # 无风险利率
  
  # 权重约束
  weight_bounds: [0.0, 1.0]       # 权重边界
  
  # 参数估计方法
  expected_return_method: mean_historical
  covariance_method: ledoit_wolf
  
  # 数值稳定性参数
  max_condition_number: 1000
  regularization: 1e-6
```

### 5.4 测试用例设计

#### 5.4.1 单元测试
```python
import pytest
import numpy as np
import pandas as pd


class TestExpectedReturnsEstimator:
    """预期收益估计器测试"""
    
    def test_mean_historical_return(self):
        """测试历史均值收益"""
        estimator = ExpectedReturnsEstimator(
            method=ExpectedReturnMethod.MEAN_HISTORICAL
        )
        
        dates = pd.date_range("2025-01-01", periods=100, freq="D")
        np.random.seed(42)
        prices = pd.DataFrame({
            "asset1": 100 * np.cumprod(1 + np.random.randn(100) * 0.02),
            "asset2": 100 * np.cumprod(1 + np.random.randn(100) * 0.03)
        }, index=dates)
        
        returns = estimator.estimate(prices)
        
        assert isinstance(returns, pd.Series)
        assert len(returns) == 2


class TestCovarianceEstimator:
    """协方差估计器测试"""
    
    def test_ledoit_wolf(self):
        """测试Ledoit-Wolf收缩估计"""
        estimator = CovarianceEstimator(
            method=CovarianceMethod.LEDOIT_WOLF
        )
        
        dates = pd.date_range("2025-01-01", periods=100, freq="D")
        np.random.seed(42)
        prices = pd.DataFrame({
            "asset1": 100 * np.cumprod(1 + np.random.randn(100) * 0.02),
            "asset2": 100 * np.cumprod(1 + np.random.randn(100) * 0.03)
        }, index=dates)
        
        cov = estimator.estimate(prices)
        
        assert isinstance(cov, pd.DataFrame)
        assert cov.shape == (2, 2)


class TestOptimalPortfolioSolver:
    """最优组合求解器测试"""
    
    def test_max_sharpe(self):
        """测试最大夏普比率"""
        config = OptimizationConfig(
            objective=OptimizationObjective.MAX_SHARPE,
            risk_free_rate=0.02
        )
        
        solver = OptimalPortfolioSolver(config)
        
        expected_returns = pd.Series({"a1": 0.10, "a2": 0.12})
        cov_matrix = pd.DataFrame(
            [[0.04, 0.02], [0.02, 0.09]],
            index=["a1", "a2"], columns=["a1", "a2"]
        )
        
        result = solver.solve(expected_returns, cov_matrix)
        
        assert isinstance(result, OptimizationResult)
        assert abs(sum(result.weights.values()) - 1.0) < 1e-6
        assert result.sharpe_ratio > 0
```

---

## 6. 实施技术栈

### 6.1 编程语言与框架版本
| 技术组件 | 版本 | 选择理由 | 替代方案 |
|----------|------|----------|----------|
| Python | 3.11+ | 生态系统完善 | - |
| PyPortfolioOpt | 1.5+ | 成熟的组合优化库 | Riskfolio-Lib |
| CVXPY | 1.4+ | 凸优化求解 | SciPy.optimize |
| NumPy | 1.24+ | 数值计算基础 | - |
| Pandas | 2.0+ | 数据处理 | - |

### 6.2 第三方库依赖与版本约束
```txt
# requirements.txt
python>=3.11
pypfopt>=1.5.0
cvxpy>=1.4.0
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
```

---

## 7. 测试策略

### 7.1 单元测试范围与覆盖率要求
- **覆盖率目标**: ≥80% 代码覆盖率
- **测试范围**: 所有公共接口和核心算法
- **测试框架**: pytest + coverage

### 7.2 集成测试场景设计
| 测试场景 | 测试目标 | 预期结果 | 通过标准 |
|----------|----------|----------|----------|
| 完整优化流程 | 端到端优化 | 正确权重输出 | 权重和为1 |
| 有效前沿计算 | 多点计算 | 曲线单调递增 | 收益随风险增加 |
| 约束处理 | 约束满足 | 满足所有约束 | 约束检查通过 |

---

## 8. 风险与约束

### 8.1 技术风险识别与缓解措施

#### P0（高风险-阻断性）
1. **风险**: 参数估计误差导致优化结果不稳定
   - **影响**: 优化结果可能偏离实际
   - **概率**: 高
   - **缓解措施**: 使用收缩估计、稳健优化方法
   - **责任人**: 实施团队

### 8.2 实施风险与应对方案
- **技能缺口**: 提供详细技术文档和代码示例
- **时间风险**: 分阶段实施，优先核心功能
- **依赖风险**: 锁定第三方库版本

---

## 9. 验收标准

### 9.1 功能验收标准
| 功能点 | 验收条件 | 测试方法 | 通过标准 |
|--------|----------|----------|----------|
| 预期收益估计 | 正确计算预期收益 | 单元测试 | 与理论值误差<5% |
| 协方差估计 | 正确计算协方差 | 单元测试 | 矩阵正定 |
| 最优组合求解 | 正确输出权重 | 端到端测试 | 权重和为1 |

### 9.2 性能验收标准
- **响应时间**: P95 <300ms（100资产）
- **吞吐量**: ≥20 QPS
- **可用性**: ≥99.9%

### 9.3 质量验收标准
- **代码质量**: 通过pylint检查
- **测试覆盖率**: ≥80% 单元测试覆盖率
- **文档完整性**: 所有章节完整

---

## 10. 实施路线图

### 10.1 Phase 1：核心功能（1周）
**目标**: 实现均值方差优化核心功能

| 任务 | 优先级 | 预计工时 | 交付物 | 完成标准 |
|------|--------|----------|--------|----------|
| 预期收益估计 | P0 | 3h | 估计模块 | 单元测试通过 |
| 协方差估计 | P0 | 3h | 估计模块 | 单元测试通过 |
| 最优组合求解 | P0 | 4h | 求解模块 | 集成测试通过 |
| 有效前沿计算 | P0 | 3h | 计算模块 | 单元测试通过 |

### 10.2 Phase 2：功能增强（0.5周）
**目标**: 增强功能和系统集成

| 任务 | 优先级 | 预计工时 | 交付物 | 完成标准 |
|------|--------|----------|--------|----------|
| 约束处理器 | P1 | 3h | 处理模块 | 单元测试通过 |
| 离散分配转换 | P1 | 2h | 转换模块 | 单元测试通过 |
| 数据库集成 | P1 | 2h | SQL脚本 | 数据库创建成功 |

### 10.3 Phase 3：测试与文档（0.5周）
**目标**: 完成测试和文档

| 任务 | 优先级 | 预计工时 | 交付物 | 完成标准 |
|------|--------|----------|--------|----------|
| 单元测试 | P0 | 3h | 测试代码 | 覆盖率≥80% |
| 集成测试 | P0 | 2h | 测试报告 | 所有场景通过 |
| 文档编写 | P1 | 2h | 用户手册 | 文档完整 |

### 10.4 资源评估
- **开发人力**: 1人 × 1.5周
- **测试人力**: 1人 × 0.5周
- **环境资源**: 本地Python环境
- **预算评估**: 无额外预算需求

---

## 附录

### A. 术语表
| 术语 | 定义 | 缩写 |
|------|------|------|
| 均值方差优化 | Markowitz组合优化理论 | MVO |
| 有效前沿 | 最优风险-收益组合集合 | EF |
| 夏普比率 | 风险调整后收益指标 | SR |

### B. 参考文献
1. [ARCHITECTURE.md](../../01_FRAMEWORK/ARCHITECTURE.md) - Layer 0-11架构定义
2. Markowitz, H. (1952). Portfolio Selection. The Journal of Finance.

### C. 变更记录
| 日期 | 版本 | 变更内容 | 变更人 | 审核人 |
|------|------|----------|--------|--------|
| 2026-04-07 | v1.0 | 初始版本 | 实施团队 | 首席技术评审官 |

---

**版本**: v1.0 | **创建**: 2026-04-07 | **状态**: Active | **维护者**: ZephyrAlpha技术团队
