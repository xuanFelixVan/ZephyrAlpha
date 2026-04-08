---
module_id: FACTOR_PORTFOLIO_OPT_001
version: v1.0
status: planning
created_date: 2026-04-08
owner: ZephyrAlpha Team
responsibility: 因子组合优化、均值方差优化、风险平价、Black-Litterman模型
---

# 因子组合优化模块蓝图

## 1. 概述

### 1.1 定位与目标

**模块定位**: Layer 2 - Alpha因子层 - 组合优化模块

**核心目标**:
- 实现多因子组合优化
- 支持多种优化方法
- 提供约束条件管理
- 优化求解器集成

**业务价值**:
- 提升组合收益
- 控制组合风险
- 满足投资约束
- 优化资金配置

### 1.2 版本信息

- **当前版本**: v1.0
- **创建日期**: 2026-04-08
- **最后更新**: 2026-04-08
- **状态**: 规划中

---

## 2. 架构设计

### 2.1 Layer定位

**Layer 2 - Alpha因子层**

```
Layer 2: Alpha因子层
  ├── 因子挖掘
  ├── 因子正交化
  ├── 多因子合成
  └── 组合优化 ← 本模块
```

### 2.2 模块职责

**核心职责**:
1. **优化方法**: 均值方差、风险平价、Black-Litterman
2. **约束管理**: 行业中性、风格中性、换手率约束
3. **求解器**: 二次规划、凸优化、启发式算法
4. **结果输出**: 最优权重、组合指标、优化报告

**职责边界**:
- ✅ 负责: 组合优化和求解
- ✅ 负责: 约束条件管理
- ❌ 不负责: 因子计算（因子计算模块职责）
- ❌ 不负责: 风险模型（风险模型模块职责）

---

## 3. 技术实现

### 3.1 技术栈选择

**核心开源项目**:

#### 方案1: cvxpy（推荐）
- **GitHub**: https://github.com/cvxgrp/cvxpy
- **Stars**: 4000+
- **适用性**: ⭐⭐⭐⭐⭐ 专业优化求解
- **优势**: 
  - 专业凸优化库
  - 支持多种求解器
  - 灵活的约束定义

```python
import cvxpy as cp
import numpy as np

class PortfolioOptimizer:
    '''组合优化器'''
    
    def mean_variance_opt(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        target_return: float = None
    ) -> np.ndarray:
        '''均值方差优化'''
        n = len(expected_returns)
        
        # 定义变量
        weights = cp.Variable(n)
        
        # 目标函数：最小化风险
        portfolio_variance = cp.quad_form(weights, cov_matrix)
        
        # 约束条件
        constraints = [
            cp.sum(weights) == 1,  # 权重和为1
            weights >= 0,  # 非负约束
        ]
        
        if target_return:
            constraints.append(
                expected_returns @ weights >= target_return
            )
        
        # 求解
        problem = cp.Problem(cp.Minimize(portfolio_variance), constraints)
        problem.solve()
        
        return weights.value
```

#### 方案2: PyPortfolioOpt
- **GitHub**: https://github.com/robertmartin8/PyPortfolioOpt
- **Stars**: 3000+
- **适用性**: ⭐⭐⭐⭐⭐ 组合优化
- **优势**: 
  - 专业的组合优化库
  - 多种优化方法
  - 易于使用

```python
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

# 计算预期收益和协方差
mu = expected_returns.mean_historical_return(prices)
S = risk_models.sample_cov(prices)

# 优化
ef = EfficientFrontier(mu, S)
weights = ef.max_sharpe()
```

#### 方案3: Riskfolio-Lib
- **GitHub**: https://github.com/dcajasn/Riskfolio-Lib
- **Stars**: 2000+
- **适用性**: ⭐⭐⭐⭐⭐ 专业组合优化
- **优势**: 
  - 丰富的优化方法
  - 风险模型集成
  - 专业级功能

```python
import riskfolio as rp

# 构建组合优化
port = rp.Portfolio(returns=Y)

# 优化方法
method = 'mv'  # 均值方差
w = port.optimization(method=method)
```

### 3.2 关键算法

#### Black-Litterman模型

```python
class BlackLittermanOptimizer:
    '''Black-Litterman优化器'''
    
    def __init__(
        self,
        market_caps: np.ndarray,
        cov_matrix: np.ndarray,
        risk_aversion: float = 2.5
    ):
        self.market_caps = market_caps
        self.cov_matrix = cov_matrix
        self.risk_aversion = risk_aversion
    
    def optimize(
        self,
        views: dict,
        view_confidences: np.ndarray
    ) -> np.ndarray:
        '''Black-Litterman优化'''
        
        # 市场均衡收益
        market_weights = self.market_caps / np.sum(self.market_caps)
        pi = self.risk_aversion * self.cov_matrix @ market_weights
        
        # 观点矩阵
        P = self._build_view_matrix(views)
        Q = np.array(list(views.values()))
        
        # 观点协方差
        omega = np.diag(1.0 / view_confidences)
        
        # Black-Litterman收益
        tau = 0.025
        M1 = np.linalg.inv(tau * self.cov_matrix)
        M2 = P.T @ np.linalg.inv(omega) @ P
        M3 = M1 @ pi + P.T @ np.linalg.inv(omega) @ Q
        
        bl_returns = np.linalg.inv(M1 + M2) @ M3
        
        # 优化权重
        weights = self._optimize_weights(bl_returns)
        
        return weights
```

### 3.3 性能要求

- **优化速度**: 单次优化 < 1秒
- **支持规模**: 支持100+资产
- **求解精度**: 高精度求解
- **稳定性**: 数值稳定

---

## 4. 数据模型

### 4.1 数据结构

#### 优化结果

```python
@dataclass
class OptimizationResult:
    weights: np.ndarray          # 最优权重
    expected_return: float       # 预期收益
    expected_risk: float         # 预期风险
    sharpe_ratio: float          # 夏普比率
    constraints_satisfied: bool  # 约束满足
    solver_status: str           # 求解状态
```

---

## 5. 实施路径

### 5.1 Phase 1: 核心功能（第1周）

**目标**: 建立基础优化能力

**任务清单**:
1. ✅ 集成cvxpy
2. ✅ 实现均值方差优化
3. ✅ 实现风险平价优化
4. ✅ 实现基础约束

**交付成果**:
- 均值方差优化模块
- 风险平价优化模块
- 约束管理模块

### 5.2 Phase 2: 扩展功能（第2周）

**目标**: 完善优化方法

**任务清单**:
1. ✅ 实现Black-Litterman模型
2. ✅ 实现最大夏普比率优化
3. ✅ 实现最小相关性优化
4. ✅ 实现高级约束

**交付成果**:
- Black-Litterman模块
- 高级优化方法
- 完整约束体系

---

## 6. 文档治理

### 6.1 System_Manifest.md索引

```yaml
- module_id: FACTOR_PORTFOLIO_OPT_001
  module_name: 因子组合优化模块
  layer: Layer 2 - Alpha因子层
  directory: docs/02_FACTOR_LIBRARY/29_FACTOR_PORTFOLIO_OPT
  blueprint: FACTOR_PORTFOLIO_OPT_BLUEPRINT.md
  status: planning
  priority: P0
  open_source: cvxpy, PyPortfolioOpt, Riskfolio-Lib
  description: 因子组合优化、均值方差优化、风险平价、Black-Litterman模型
```

---

## 7. 总结

本蓝图为Layer 2 Alpha因子层提供了完整的组合优化解决方案，通过集成cvxpy、PyPortfolioOpt、Riskfolio-Lib等成熟开源项目，实现了专业机构级的组合优化功能。

**核心优势**:
1. ✅ 多种优化方法
2. ✅ 灵活的约束管理
3. ✅ 专业求解器
4. ✅ 高效稳定

**实施建议**:
- 优先使用cvxpy进行优化求解
- 结合PyPortfolioOpt快速实现
- 根据需求选择优化方法

**预期成果**:
- 优化效率: 提升5x+
- 组合收益: 提升10%+
- 风险控制: 专业级
