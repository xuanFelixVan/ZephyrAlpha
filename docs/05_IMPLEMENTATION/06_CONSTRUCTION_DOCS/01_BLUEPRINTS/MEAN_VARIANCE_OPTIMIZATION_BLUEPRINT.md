---
responsibility:
  - 实施指南、部署文档
  - 风险预算
  - 数据质量

module_id: MEAN_VARIANCE_OPTIMIZATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 6 组合优化层
compliance_level: 专业标准
layer: "Layer 6 (组合优化层)"
---

# Mean Variance Optimization

> **核心职责**: 均值方差优化
> **职责边界**: 
> - ✅ 本文档负责：均值方差优化、有效前沿计算、最优组合求解
> - ❌ 本文档不负责：因子中性约束（由FACTOR_NEUTRAL_OPTIMIZATION负责）

## 核心定位

均值方差优化器，负责基于预期收益和风险协方差矩阵，求解最优投资组合权重


## 1. 模块概述

### 1.1 核心职责

**单一职责**: 实现Markowitz均值方差优化理论，提供有效前沿计算和最优组合求解能力

**职责边界**:
- ✅ 负责: 均值方差优化、有效前沿计算、最优组合求解
- ❌ 不负责: 因子中性约束（由FACTOR_NEUTRAL_OPTIMIZATION负责）
- ❌ 不负责: 鲁棒优化（由ROBUST_OPTIMIZATION负责）
- ❌ 不负责: 交易成本建模（由TRANSACTION_COST_MODEL负责）

### 1.2 开源依赖

| 库名 | 版本 | 用途 | GitHub Stars |
|
layer: "Layer 6 (组合优化层)"
## 2. 功能设计

### 2.1 核心功能

#### 2.1.1 有效前沿计算

```python
class EfficientFrontierCalculator:
    """
    有效前沿计算器
    
    开源依赖: PyPortfolioOpt.EfficientFrontier
    """
    
    def calculate_efficient_frontier(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        n_points: int = 100
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        计算有效前沿
        
        参数:
            expected_returns: 预期收益向量 (n_assets,)
            covariance_matrix: 协方差矩阵 (n_assets, n_assets)
            n_points: 有效前沿点数
            
        返回:
            returns: 收益率数组
            volatilities: 波动率数组
            weights: 权重矩阵 (n_points, n_assets)
        """
        pass
```

#### 2.1.2 最优组合求解

```python
class OptimalPortfolioSolver:
    """
    最优组合求解器
    
    开源依赖: PyPortfolioOpt
    """
    
    def max_sharpe_portfolio(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        risk_free_rate: float = 0.02,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        最大夏普比率组合
        
        返回:
            weights: 最优权重
            expected_return: 预期收益
            volatility: 波动率
            sharpe_ratio: 夏普比率
        """
        pass
    
    def min_volatility_portfolio(
        self,
        covariance_matrix: np.ndarray,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        最小方差组合
        """
        pass
    
    def max_return_portfolio(
        self,
        expected_returns: np.ndarray,
        target_volatility: float,
        covariance_matrix: np.ndarray,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        给定风险水平下的最大收益组合
        """
        pass
```

#### 2.1.3 离散分配转换

```python
class DiscreteAllocationConverter:
    """
    离散分配转换器
    
    开源依赖: PyPortfolioOpt.discrete_allocation
    """
    
    def convert_to_discrete(
        self,
        weights: Dict[str, float],
        latest_prices: Dict[str, float],
        total_portfolio_value: float,
        method: str = 'greedy'
    ) -> Tuple[Dict[str, int], float]:
        """
        将连续权重转换为实际可购买数量
        
        参数:
            weights: 资产权重字典
            latest_prices: 最新价格字典
            total_portfolio_value: 总投资金额
            method: 分配方法 ('greedy' 或 'round')
            
        返回:
            allocation: 资产数量字典
            leftover: 剩余资金
        """
        pass
```

### 2.2 参数估计

#### 2.2.1 预期收益估计

```python
class ExpectedReturnsEstimator:
    """
    预期收益估计器
    
    开源依赖: PyPortfolioOpt.expected_returns
    """
    
    def mean_historical_return(
        self,
        prices: pd.DataFrame,
        frequency: int = 252
    ) -> pd.Series:
        """
        历史均值收益
        """
        pass
    
    def ema_historical_return(
        self,
        prices: pd.DataFrame,
        span: int = 500,
        frequency: int = 252
    ) -> pd.Series:
        """
        指数加权移动平均收益
        """
        pass
    
    def capm_return(
        self,
        prices: pd.DataFrame,
        market_prices: pd.DataFrame,
        risk_free_rate: float = 0.02,
        frequency: int = 252
    ) -> pd.Series:
        """
        CAPM预期收益
        """
        pass
```

#### 2.2.2 协方差估计

```python
class CovarianceEstimator:
    """
    协方差估计器
    
    开源依赖: PyPortfolioOpt.risk_models
    """
    
    def sample_cov(
        self,
        returns: pd.DataFrame,
        frequency: int = 252
    ) -> pd.DataFrame:
        """
        样本协方差
        """
        pass
    
    def semicovariance(
        self,
        returns: pd.DataFrame,
        benchmark: float = 0.0,
        frequency: int = 252
    ) -> pd.DataFrame:
        """
        半协方差（下行风险）
        """
        pass
    
    def exp_cov(
        self,
        returns: pd.DataFrame,
        span: int = 180,
        frequency: int = 252
    ) -> pd.DataFrame:
        """
        指数加权协方差
        """
        pass
    
    def ledoit_wolf_shrinkage(
        self,
        returns: pd.DataFrame,
        frequency: int = 252
    ) -> pd.DataFrame:
        """
        Ledoit-Wolf收缩估计
        """
        pass
```

### 2.3 约束处理

```python
class ConstraintHandler:
    """
    约束处理器
    
    开源依赖: PyPortfolioOpt约束系统
    """
    
    def add_weight_constraint(
        self,
        min_weight: float = 0.0,
        max_weight: float = 1.0
    ) -> None:
        """
        权重约束（长仓/短仓限制）
        """
        pass
    
    def add_sector_constraint(
        self,
        sector_mapping: Dict[str, str],
        sector_weights: Dict[str, Tuple[float, float]]
    ) -> None:
        """
        行业权重约束
        """
        pass
    
    def add_leverage_constraint(
        self,
        max_leverage: float = 1.0
    ) -> None:
        """
        杠杆约束
        """
        pass
```

---
## 3. 技术规格

### 3.1 接口设计

```python
class MeanVarianceOptimizer:
    """
    均值方差优化器
    
    主要接口类，封装PyPortfolioOpt功能
    """
    
    def __init__(
        self,
        returns_data: pd.DataFrame,
        risk_free_rate: float = 0.02,
        frequency: int = 252
    ):
        """
        初始化优化器
        
        参数:
            returns_data: 收益率数据 (date × ticker)
            risk_free_rate: 无风险利率
            frequency: 年化频率
        """
        self.returns = returns_data
        self.risk_free_rate = risk_free_rate
        self.frequency = frequency
        
        # 初始化估计器
        self.mu_estimator = ExpectedReturnsEstimator()
        self.cov_estimator = CovarianceEstimator()
        self.solver = OptimalPortfolioSolver()
        self.converter = DiscreteAllocationConverter()
    
    def optimize(
        self,
        objective: str = 'max_sharpe',
        method_mu: str = 'mean',
        method_cov: str = 'sample',
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        执行优化
        
        参数:
            objective: 优化目标 ('max_sharpe', 'min_volatility', 'max_return')
            method_mu: 收益估计方法
            method_cov: 协方差估计方法
            constraints: 约束条件
            
        返回:
            优化结果字典
        """
        pass
    
    def get_efficient_frontier(
        self,
        n_points: int = 100
    ) -> pd.DataFrame:
        """
        获取有效前沿数据
        """
        pass
    
    def get_discrete_allocation(
        self,
        weights: Dict[str, float],
        latest_prices: Dict[str, float],
        total_value: float
    ) -> Tuple[Dict[str, int], float]:
        """
        获取离散分配方案
        """
        pass
```

### 3.2 数据结构

```python
@dataclass
class OptimizationResult:
    """优化结果数据结构"""
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    method_mu: str
    method_cov: str
    constraints: Dict
    timestamp: datetime

@dataclass
class EfficientFrontierPoint:
    """有效前沿点数据结构"""
    return_: float
    volatility: float
    sharpe_ratio: float
    weights: np.ndarray
```

### 3.3 配置参数

```yaml
mean_variance_optimization:
  # 收益估计配置
  expected_returns:
    method: 'mean'  # mean, ema, capm
    ema_span: 500
    capm_benchmark: 'SPY'
    
  # 协方差估计配置
  covariance:
    method: 'ledoit_wolf'  # sample, exp, ledoit_wolf, semicov
    exp_span: 180
    shrinkage_target: 'single_factor'
    
  # 优化配置
  optimization:
    objective: 'max_sharpe'
    risk_free_rate: 0.02
    frequency: 252
    
  # 约束配置
  constraints:
    min_weight: 0.0  # 不允许做空
    max_weight: 0.10  # 单资产最大10%
    max_leverage: 1.0  # 不使用杠杆
    
  # 离散分配配置
  discrete_allocation:
    method: 'greedy'
    min_remaining: 100  # 最小剩余资金
```

---

## 4. 实现路径

### 4.1 开源集成方案

```python
# 基于PyPortfolioOpt的实现
> **核心职责**: Mean Variance Optimization蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Mean Variance Optimization蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


## 核心职责

均值方差优化，负责基于风险收益的组合优化


---

## 📋 概述

本文档定义了MEAN VARIANCE OPTIMIZATION的核心功能和技术实现。

from pypfopt import EfficientFrontier, expected_returns, risk_models
from pypfopt.discrete_allocation import DiscreteAllocation

class PyPortfolioOptAdapter(MeanVarianceOptimizer):
    """
    PyPortfolioOpt适配器
    
    直接使用PyPortfolioOpt的核心功能
    """
    
    def optimize(self, objective: str, **kwargs) -> Dict:
        # 计算预期收益
        mu = expected_returns.mean_historical_return(self.returns)
        
        # 计算协方差矩阵
        S = risk_models.risk_models.sample_cov(self.returns)
        
        # 创建有效前沿对象
        ef = EfficientFrontier(mu, S)
        
        # 添加约束
        if self.constraints:
            self._add_constraints(ef)
        
        # 执行优化
        if objective == 'max_sharpe':
            weights = ef.max_sharpe()
        elif objective == 'min_volatility':
            weights = ef.min_volatility()
        
        # 获取组合统计
        ret, vol, sharpe = ef.portfolio_performance()
        
        return {
            'weights': weights,
            'expected_return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe
        }
```

### 4.2 开发里程碑

| 阶段 | 任务 | 工作量 | 依赖 |
|------|------|--------|------|
| 第1天 | PyPortfolioOpt集成测试 | 8h | - |
| 第2天 | 预期收益估计器实现 | 8h | 第1天 |
| 第3天 | 协方差估计器实现 | 8h | 第1天 |
| 第4天 | 约束处理器实现 | 8h | 第2-3天 |
| 第5天 | 离散分配转换实现 | 8h | 第4天 |
| 第6天 | 接口封装和测试 | 8h | 第5天 |
| 第7天 | 文档和集成测试 | 8h | 第6天 |

---

## 5. 测试规格

### 5.1 单元测试

```python
class TestMeanVarianceOptimizer:
    
    def test_max_sharpe_portfolio(self):
        """测试最大夏普比率组合"""
        pass
    
    def test_min_volatility_portfolio(self):
        """测试最小方差组合"""
        pass
    
    def test_efficient_frontier(self):
        """测试有效前沿计算"""
        pass
    
    def test_discrete_allocation(self):
        """测试离散分配"""
        pass
    
    def test_constraints(self):
        """测试约束处理"""
        pass
```

### 5.2 集成测试

```python
class TestIntegration:
    
    def test_with_black_litterman(self):
        """测试与Black-Litterman模型集成"""
        pass
    
    def test_with_risk_parity(self):
        """测试与风险平价策略集成"""
        pass
    
    def test_with_rebalancing(self):
        """测试与再平衡系统集成"""
        pass
```

---

## 6. 性能指标

### 6.1 计算性能

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 优化时间（100资产） | <100ms | 时间测试 |
| 有效前沿计算（100点） | <1s | 时间测试 |
| 内存占用 | <100MB | 内存监控 |

### 6.2 数值稳定性

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 权重和 | 1.0±1e-6 | 数值验证 |
| 约束满足率 | 100% | 约束检查 |
| 收敛率 | >99% | 优化日志 |

---

## 7. 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-07 | **状态**: Active

## 8. 文档治理

### 8.1 文档索引

**本文档在系统中的位置**:
- **所属层级**: Layer 6 (组合优化层)
- **模块索引**: 001
- **模块名称**: MEAN_VARIANCE_OPTIMIZATION
- **文档路径**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/

### 8.2 版本管理

**版本历史**:
- v1.0.0 (2026-04-07): 初始版本

### 8.3 维护责任

**文档维护**:
- **责任模块**: MEAN_VARIANCE_OPTIMIZATION
- **维护周期**: 每季度审查
- **变更流程**: 提交变更申请 → 技术评审 → 更新文档

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-07 | **状态**: Active
