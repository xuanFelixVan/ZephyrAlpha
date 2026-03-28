# AI自我优化参数管理

> AI参数优化体系
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 监控系统：[monitoring.md](./monitoring.md)

***

## 1. 参数分类体系：三类参数管理策略

### 1.1 第一类：完全AI自我优化参数（60-70%）

| 参数类别 | 具体参数 | 优化方法 | 搜索空间/说明 |
| :--------- | :---------------- | :-------- | :------------------------------------ |
| **技术指标参数** | MACD周期参数(12,26,9) | 贝叶斯优化 | 快速EMA[8-20]，慢速EMA[20-40]，信号线[5-15] |
| | RSI周期参数(14) | 网格搜索 | 搜索空间[7-21] |
| | 布林带标准差倍数(2) | 自适应调整 | 基于市场波动率动态调整[1.5-2.5] |
| **预测模型参数** | 机器学习模型超参数 | 贝叶斯优化 | 学习率、正则化系数、树深度等 |
| | 神经网络结构参数 | 遗传算法 | 层数、神经元数量、激活函数 |
| **仓位计算参数** | 凯利公式风险系数 | 基于历史胜率 | 动态调整 |
| | 波动率倒数权重系数 | 基于风险调整后收益 | 动态调整 |
| **风险控制参数** | 止损止盈比例 | 基于波动率和胜率 | 动态调整 |
| | 仓位限制阈值 | 基于最大回撤容忍度 | 动态调整 |

***

### 1.2 第二类：半自动优化参数（20-30%）

| 参数类别 | 说明 | 管理方式 |
| :------------ | :------------- | :----- |
| **最大仓位限制** | AI建议范围 | 人工最终确认 |
| **单日最大亏损限制** | 基于风险偏好设定 | 人工设定边界 |
| **模型结构重大变更** | 如：从线性模型切换到神经网络 | 需人工审核 |
| **策略逻辑根本性调整** | 如：从趋势跟踪切换到均值回归 | 需人工审核 |

***

### 1.3 第三类：人工设定参数（10-20%）

| 参数类别 | 具体参数 | 设定依据 |
| :----------- | :--------------- | :---------- |
| **核心风险偏好参数** | 最大回撤容忍度（如：-20%） | 基于个人风险承受能力 |
| | 年化收益目标（如：15-25%） | 基于投资目标和市场环境 |
| **资金管理参数** | 初始资金规模 | 基于可用资金 |
| | 单笔最大投资比例 | 基于分散化需求 |
| **系统运行参数** | 数据更新频率 | 基于数据源限制 |
| | 交易执行延迟容忍度 | 基于技术条件 |

***

## 2. AI自我优化三层架构

### 2.1 实时微调层（分钟级）

- **优化对象**：技术指标敏感参数（如：RSI超买超卖阈值）
- **优化方法**：在线学习
- **优化频率**：每分钟/每笔交易后

***

### 2.2 周期优化层（日/周级）

- **优化对象**：模型参数和策略参数（如：预测模型权重、仓位系数）
- **优化方法**：批量优化
- **优化频率**：每日收盘后/每周

***

### 2.3 结构进化层（月/季度级）

- **优化对象**：模型结构和策略逻辑（如：特征选择、模型类型）
- **优化方法**：遗传算法/强化学习
- **优化频率**：每月/每季度

***

## 3. 优化算法选择矩阵

| 算法 | 适用场景 | 示例 | 优点 |
| :---- | :---------- | :------- | :-------- |
| 贝叶斯优化 | 连续参数，计算成本高 | 神经网络超参数 | 样本效率高，收敛快 |
| 遗传算法 | 离散/混合参数，多模态 | 特征组合选择 | 全局搜索能力强 |
| 强化学习 | 序列决策问题 | 动态仓位调整 | 适应动态环境 |
| 网格搜索 | 参数少，搜索空间小 | 简单技术指标参数 | 简单可靠，全面搜索 |

***

## 4. 安全边界与约束条件

- **参数变化幅度限制**：单次优化变化不超过±20%
- **性能回撤保护机制**：优化后回测表现下降超过5%则回滚
- **过拟合检测**：样本外测试表现必须优于样本内
- **稳定性检验**：参数在多个市场环境下保持稳定

***

## 5. 监控与评估体系

### 5.1 实时监控指标

- **参数变化轨迹**：记录每次优化的参数值
- **优化效果跟踪**：记录优化前后的绩效对比

***

### 5.2 定期评估报告

- **周度优化报告**：总结本周参数优化情况
- **月度进化报告**：总结本月策略进化情况

***

## 6. Python实现

```python
from abc import ABC, abstractmethod
from typing import Any, Callable
import numpy as np

class ParameterOptimizer(ABC):
    """参数优化基类"""

    @abstractmethod
    def optimize(self, objective_func: Callable, param_space: dict) -> dict:
        """
        执行参数优化

        Parameters:
        -----------
        objective_func : Callable
            目标函数（如：回测收益）
        param_space : dict
            参数空间定义

        Returns:
        --------
        dict: 最优参数
        """
        pass

    @abstractmethod
    def set_constraints(self, constraints: dict) -> None:
        """设置约束条件"""
        pass


class BayesianOptimizer(ParameterOptimizer):
    """贝叶斯优化器"""

    def __init__(self, n_iter: int = 50):
        self.n_iter = n_iter
        self.constraints = {}

    def optimize(self, objective_func: Callable, param_space: dict) -> dict:
        """贝叶斯优化实现"""
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import RBF, ConstantKernel

        results = []

        for i in range(self.n_iter):
            if i == 0:
                params = self._random_sample(param_space)
            else:
                params = self._propose_next_point()

            value = objective_func(**params)
            results.append({**params, 'value': value})

            if self._check_convergence(results):
                break

        best = max(results, key=lambda x: x['value'])
        return {k: v for k, v in best.items() if k != 'value'}

    def set_constraints(self, constraints: dict) -> None:
        """设置约束条件"""
        self.constraints = constraints

    def _random_sample(self, param_space: dict) -> dict:
        """随机采样"""
        return {k: np.random.uniform(v['min'], v['max'])
                for k, v in param_space.items()}

    def _propose_next_point(self) -> dict:
        """基于高斯过程提出下一个采样点"""
        pass

    def _check_convergence(self, results: list) -> bool:
        """检查收敛"""
        if len(results) < 10:
            return False
        recent = [r['value'] for r in results[-10:]]
        return np.std(recent) < 1e-6


class GeneticAlgorithm(ParameterOptimizer):
    """遗传算法优化器"""

    def __init__(self, population_size: int = 50, n_generations: int = 100,
                 mutation_rate: float = 0.1, crossover_rate: float = 0.8):
        self.population_size = population_size
        self.n_generations = n_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.constraints = {}

    def optimize(self, objective_func: Callable, param_space: dict) -> dict:
        """遗传算法实现"""
        population = self._initialize_population(param_space)

        for generation in range(self.n_generations):
            fitness = [objective_func(**individual) for individual in population]

            parents = self._select_parents(population, fitness)

            offspring = []
            for i in range(0, len(parents), 2):
                if i + 1 < len(parents):
                    child1, child2 = self._crossover(parents[i], parents[i+1])
                    offspring.extend([child1, child2])

            population = [self._mutate(ind, param_space)
                          if np.random.random() < self.mutation_rate else ind
                          for ind in offspring]

            if self._check_termination(fitness):
                break

        best_idx = np.argmax(fitness)
        return population[best_idx]

    def set_constraints(self, constraints: dict) -> None:
        self.constraints = constraints

    def _initialize_population(self, param_space: dict) -> list:
        pass

    def _select_parents(self, population: list, fitness: list) -> list:
        pass

    def _crossover(self, parent1: dict, parent2: dict) -> tuple:
        pass

    def _mutate(self, individual: dict, param_space: dict) -> dict:
        pass

    def _check_termination(self, fitness: list) -> bool:
        pass
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录L内容 |
