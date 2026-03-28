# T.08.AI003.AI自我优化框架

> AI自主参数优化与策略进化框架
>
> **策略编号**：T.08.AI003
> **所属模块**：ai-optimization
> **文档类型**：AI优化
> **优先级**：P2
>
> **配套文档**：
> - [T.08.AI001.因子衰减检测.md](./T.08.AI001.因子衰减检测.md) - 因子衰减检测
> - [T.08.AI002.ICIR监控.md](./T.08.AI002.ICIR监控.md) - IC/IR监控
> - [self-optimization.md](./self-optimization.md) - AI优化完整文档

---

## 1. 三层优化架构

```python
class AISelfOptimizationFramework:
    """
    AI自我优化三层架构

    Layer 1: 实时微调层 (分钟级)
    Layer 2: 周期优化层 (日/周级)
    Layer 3: 结构进化层 (月/季度级)
    """

    OPTIMIZATION_LAYERS = {
        'realtime': {
            'frequency': 'minute/trade',
            'target': 'indicator parameters',
            'method': 'online learning'
        },
        'periodic': {
            'frequency': 'daily/weekly',
            'target': 'model weights, position coefficients',
            'method': 'batch optimization'
        },
        'structural': {
            'frequency': 'monthly/quarterly',
            'target': 'model structure, strategy logic',
            'method': 'genetic algorithm / reinforcement learning'
        }
    }
```

---

## 2. 参数分类体系

```python
class ParameterCategory:
    """
    参数分类体系
    三类参数：AI自主/半自动/人工
    """

    PARAMETER_CATEGORIES = {
        'ai_auto': {
            'ratio': 0.65,
            'description': 'AI完全自主优化',
            'examples': [
                '技术指标参数 (MACD/RSI周期)',
                '模型超参数 (学习率/正则化)',
                '仓位计算系数 (凯利公式)',
                '风控阈值 (止损比例)'
            ]
        },
        'semi_auto': {
            'ratio': 0.25,
            'description': 'AI建议 + 人工确认',
            'examples': [
                '最大仓位限制',
                '单日最大亏损',
                '模型结构重大变更',
                '策略逻辑根本调整'
            ]
        },
        'manual': {
            'ratio': 0.10,
            'description': '人工设定',
            'examples': [
                '最大回撤容忍度',
                '年化收益目标',
                '初始资金规模',
                '数据更新频率'
            ]
        }
    }
```

---

## 3. 实时微调层

```python
class RealtimeOptimizer:
    """
    实时微调优化器
    """

    def __init__(self):
        self.learning_rate = 0.01
        self.adaptation_window = 100

    def online_optimize(self, current_params: dict,
                      market_state: str,
                      recent_performance: float) -> dict:
        """
        在线优化参数

        参数:
            current_params: 当前参数
            market_state: 市场状态
            recent_performance: 近期表现

        返回:
            optimized_params: 优化后参数
        """
        optimized = current_params.copy()

        if market_state == '趋势市':
            optimized = self.adjust_for_trend_market(
                optimized, recent_performance
            )
        elif market_state == '震荡市':
            optimized = self.adjust_for_range_market(
                optimized, recent_performance
            )
        elif market_state == '高波动':
            optimized = self.adjust_for_high_volatility(
                optimized, recent_performance
            )

        optimized = self.apply_constraints(optimized)

        return optimized

    def adjust_for_trend_market(self, params: dict,
                              performance: float) -> dict:
        """
        趋势市场参数调整
        """
        if performance > 0:
            params['stop_loss'] *= 1.05
            params['position_size'] *= 1.02
            params['momentum_weight'] *= 1.10
        else:
            params['stop_loss'] *= 0.98
            params['position_size'] *= 0.98

        return params

    def adjust_for_range_market(self, params: dict,
                              performance: float) -> dict:
        """
        震荡市场参数调整
        """
        params['mean_reversion_weight'] *= 1.10
        params['bollinger_multiplier'] *= 0.95
        params['position_size'] *= 0.95

        return params

    def adjust_for_high_volatility(self, params: dict,
                                 performance: float) -> dict:
        """
        高波动市场参数调整
        """
        params['stop_loss'] *= 0.90
        params['position_size'] *= 0.85
        params['volatility_threshold'] *= 1.20

        return params

    def apply_constraints(self, params: dict) -> dict:
        """
        应用参数约束
        """
        constraints = {
            'stop_loss': (0.03, 0.15),
            'position_size': (0.05, 0.30),
            'learning_rate': (0.001, 0.1)
        }

        for param, (min_val, max_val) in constraints.items():
            if param in params:
                params[param] = max(min_val, min(max_val, params[param]))

        return params
```

---

## 4. 周期优化层

```python
class PeriodicOptimizer:
    """
    周期优化器
    """

    def __init__(self):
        self.optimization_history = []
        self.performance_threshold = 0.05

    def bayesian_optimize(self, objective_func: callable,
                        param_space: dict,
                        n_iter: int = 50) -> dict:
        """
        贝叶斯优化

        参数:
            objective_func: 目标函数
            param_space: 参数空间
            n_iter: 迭代次数

        返回:
            best_params: 最优参数
        """
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import RBF, ConstantKernel

        results = []

        for i in range(n_iter):
            if i == 0:
                params = self._random_sample(param_space)
            else:
                params = self._propose_next_point(
                    results, param_space
                )

            value = objective_func(**params)
            results.append({**params, 'value': value})

            if self._check_convergence(results):
                break

        best = max(results, key=lambda x: x['value'])
        return {k: v for k, v in best.items() if k != 'value'}

    def _random_sample(self, param_space: dict) -> dict:
        """随机采样"""
        import numpy as np
        return {k: np.random.uniform(v['min'], v['max'])
                for k, v in param_space.items()}

    def _propose_next_point(self, results: list,
                          param_space: dict) -> dict:
        """基于高斯过程提议下一个点"""
        import numpy as np

        best = max(results, key=lambda x: x['value'])
        proposals = []

        for _ in range(10):
            proposal = {}
            for k, v in param_space.items():
                if 'choice' in v:
                    proposal[k] = np.random.choice(v['choice'])
                else:
                    proposal[k] = np.random.uniform(v['min'], v['max'])
            proposals.append(proposal)

        return proposals[np.random.randint(len(proposals))]

    def _check_convergence(self, results: list) -> bool:
        """检查收敛"""
        import numpy as np
        if len(results) < 10:
            return False
        recent = [r['value'] for r in results[-10:]]
        return np.std(recent) < 1e-6

    def genetic_optimize(self, objective_func: callable,
                       param_space: dict,
                       population_size: int = 50,
                       n_generations: int = 100) -> dict:
        """
        遗传算法优化

        参数:
            objective_func: 目标函数
            param_space: 参数空间
            population_size: 种群大小
            n_generations: 迭代代数

        返回:
            best_params: 最优参数
        """
        import numpy as np

        population = [
            self._random_sample(param_space)
            for _ in range(population_size)
        ]

        for generation in range(n_generations):
            fitness = [objective_func(**ind) for ind in population]

            parents_idx = np.argsort(fitness)[-20:]
            parents = [population[i] for i in parents_idx]

            offspring = []
            for i in range(0, len(parents), 2):
                if i + 1 < len(parents):
                    child1, child2 = self._crossover(
                        parents[i], parents[i+1], param_space
                    )
                    offspring.extend([child1, child2])

            population = parents + offspring

            if self._check_termination(fitness):
                break

        best_idx = np.argmax(fitness)
        return population[best_idx]

    def _crossover(self, parent1: dict, parent2: dict,
                  param_space: dict) -> tuple:
        """交叉"""
        import numpy as np

        child1, child2 = {}, {}
        for k in param_space.keys():
            if np.random.random() < 0.5:
                child1[k] = parent1[k]
                child2[k] = parent2[k]
            else:
                child1[k] = parent2[k]
                child2[k] = parent1[k]

        return child1, child2

    def _check_termination(self, fitness: list) -> bool:
        """检查终止条件"""
        import numpy as np
        if len(fitness) < 30:
            return False
        recent = fitness[-30:]
        return np.std(recent) / (np.mean(recent) + 1e-10) < 0.01

    def backtest_validation(self, new_params: dict,
                          backtest_func: callable,
                          baseline_performance: float) -> dict:
        """
        回测验证优化结果

        返回:
            validation_result: 验证结果
        """
        new_performance = backtest_func(**new_params)

        performance_change = (
            (new_performance - baseline_performance) / baseline_performance
        )

        rollback = performance_change < -self.performance_threshold

        return {
            'new_performance': new_performance,
            'baseline_performance': baseline_performance,
            'performance_change': performance_change,
            'should_rollback': rollback,
            'approved': not rollback
        }
```

---

## 5. 结构进化层

```python
class StructuralEvolution:
    """
    结构进化层
    """

    def __init__(self):
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8

    def evolve_model_structure(self, current_model: dict,
                            performance_history: list) -> dict:
        """
        进化模型结构

        参数:
            current_model: 当前模型
            performance_history: 性能历史

        返回:
            evolved_model: 进化后模型
        """
        trend = self.analyze_performance_trend(performance_history)

        if trend == 'declining':
            return self.perform_structural_mutation(current_model)
        elif trend == 'stable':
            return self.explore_alternative_structures(current_model)
        else:
            return current_model

    def analyze_performance_trend(self, history: list) -> str:
        """
        分析性能趋势
        """
        if len(history) < 10:
            return 'insufficient_data'

        recent = history[-5:]
        early = history[:5]

        recent_avg = sum(recent) / len(recent)
        early_avg = sum(early) / len(early)

        change = (recent_avg - early_avg) / early_avg if early_avg != 0 else 0

        if change > 0.05:
            return 'improving'
        elif change < -0.05:
            return 'declining'
        else:
            return 'stable'

    def perform_structural_mutation(self, model: dict) -> dict:
        """
        执行结构突变
        """
        new_model = model.copy()

        mutation_types = ['add_layer', 'remove_layer', 'change_activation']

        mutation = np.random.choice(mutation_types)

        if mutation == 'add_layer' and model.get('n_layers', 1) < 5:
            new_model['n_layers'] = model.get('n_layers', 1) + 1

        elif mutation == 'remove_layer' and model.get('n_layers', 1) > 2:
            new_model['n_layers'] = model.get('n_layers', 1) - 1

        elif mutation == 'change_activation':
            activations = ['relu', 'tanh', 'sigmoid', 'leaky_relu']
            current = model.get('activation', 'relu')
            alternatives = [a for a in activations if a != current]
            new_model['activation'] = np.random.choice(alternatives)

        return new_model

    def explore_alternative_structures(self, model: dict) -> dict:
        """
        探索替代结构
        """
        alternatives = [
            {'type': 'linear', 'n_features': 20},
            {'type': 'tree', 'max_depth': 5},
            {'type': 'ensemble', 'n_estimators': 100}
        ]

        return np.random.choice(alternatives)
```

---

## 6. 安全边界与约束

```python
class SafetyConstraints:
    """
    安全约束系统
    """

    def __init__(self):
        self.max_param_change_rate = 0.20
        self.max_drawdown_threshold = 0.15
        self.overfitting_threshold = 0.05

    def validate_param_change(self, old_params: dict,
                            new_params: dict) -> dict:
        """
        验证参数变更是否安全
        """
        violations = []

        for key in new_params:
            if key in old_params:
                old_val = old_params[key]
                new_val = new_params[key]

                if old_val != 0:
                    change_rate = abs(new_val - old_val) / abs(old_val)

                    if change_rate > self.max_param_change_rate:
                        violations.append({
                            'param': key,
                            'old_value': old_val,
                            'new_value': new_val,
                            'change_rate': change_rate,
                            'max_allowed': self.max_param_change_rate
                        })

        return {
            'is_safe': len(violations) == 0,
            'violations': violations,
            'adjusted_params': self.adjust_violations(new_params, violations)
        }

    def adjust_violations(self, params: dict,
                        violations: list) -> dict:
        """
        调整违规参数
        """
        adjusted = params.copy()

        for v in violations:
            param = v['param']
            max_change = self.max_param_change_rate
            old_val = v['old_value']

            new_val = adjusted[param]
            max_new = old_val * (1 + max_change)
            min_new = old_val * (1 - max_change)

            adjusted[param] = max(min_new, min(max_new, new_val))

        return adjusted

    def check_drawdown_protection(self, current_drawdown: float) -> dict:
        """
        检查回撤保护
        """
        if current_drawdown < -self.max_drawdown_threshold:
            return {
                'protection_triggered': True,
                'action': '自动减仓至50%',
                'current_drawdown': current_drawdown
            }

        return {
            'protection_triggered': False,
            'current_drawdown': current_drawdown
        }

    def validate_overfitting(self, in_sample_perf: float,
                          out_sample_perf: float) -> dict:
        """
        验证过拟合
        """
        gap = in_sample_perf - out_sample_perf

        return {
            'is_overfitting': gap > self.overfitting_threshold,
            'in_sample': in_sample_perf,
            'out_sample': out_sample_perf,
            'gap': gap,
            'message': '过拟合严重' if gap > self.overfitting_threshold else '正常'
        }
```

---

## 7. 优化效果评估

```python
class OptimizationEvaluator:
    """
    优化效果评估器
    """

    def __init__(self):
        self.baseline_metrics = {}

    def evaluate_optimization_result(self,
                                   before_params: dict,
                                   after_params: dict,
                                   before_performance: float,
                                   after_performance: float,
                                   backtest_results: dict) -> dict:
        """
        评估优化结果

        参数:
            before_params: 优化前参数
            after_params: 优化后参数
            before_performance: 优化前表现
            after_performance: 优化后表现
            backtest_results: 回测结果

        返回:
            evaluation: 评估报告
        """
        performance_improvement = (
            (after_performance - before_performance) / before_performance
        )

        param_efficiency = self.calculate_param_efficiency(
            before_params, after_params
        )

        stability = self.evaluate_stability(backtest_results)

        overall_score = (
            performance_improvement * 0.4 +
            param_efficiency * 0.3 +
            stability * 0.3
        )

        return {
            'performance_improvement': round(performance_improvement * 100, 2),
            'param_efficiency': round(param_efficiency, 4),
            'stability_score': round(stability, 4),
            'overall_score': round(overall_score, 4),
            'grade': self.get_grade(overall_score),
            'recommendation': self.get_recommendation(
                overall_score, performance_improvement
            )
        }

    def calculate_param_efficiency(self, before: dict,
                                  after: dict) -> float:
        """
        计算参数效率
        """
        total_change = 0
        for key in after:
            if key in before:
                change = abs(after[key] - before[key])
                total_change += change

        return 1 / (1 + total_change)

    def evaluate_stability(self, backtest_results: dict) -> float:
        """
        评估稳定性
        """
        returns = backtest_results.get('daily_returns', [])

        if not returns:
            return 0.5

        sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        max_drawdown = self.calculate_max_drawdown(returns)

        return max(0, min(1, (sharpe / 2 - max_drawdown)))

    def calculate_max_drawdown(self, returns: list) -> float:
        """计算最大回撤"""
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max

        return abs(np.min(drawdown))

    def get_grade(self, score: float) -> str:
        """评级"""
        if score >= 0.8:
            return 'A (优秀)'
        elif score >= 0.6:
            return 'B (良好)'
        elif score >= 0.4:
            return 'C (一般)'
        else:
            return 'D (较差)'

    def get_recommendation(self, score: float,
                         perf_improvement: float) -> str:
        """建议"""
        if score >= 0.7 and perf_improvement > 0:
            return '优化效果优秀，采纳新参数'
        elif score >= 0.5:
            return '优化效果一般，继续观察'
        elif perf_improvement < -0.05:
            return '优化效果负向，回滚参数'
        else:
            return '优化效果不明显，维持原参数'
```

---

## 8. 使用示例

```python
def example_ai_self_optimization():
    """
    AI自我优化示例
    """
    framework = AISelfOptimizationFramework()

    realtime_opt = RealtimeOptimizer()
    periodic_opt = PeriodicOptimizer()
    structural_ev = StructuralEvolution()
    safety = SafetyConstraints()
    evaluator = OptimizationEvaluator()

    current_params = {
        'stop_loss': 0.07,
        'position_size': 0.15,
        'learning_rate': 0.01,
        'momentum_weight': 0.6
    }

    market_state = '趋势市'
    recent_performance = 0.05

    realtime_params = realtime_opt.online_optimize(
        current_params, market_state, recent_performance
    )
    print(f"实时优化后参数: {realtime_params}")

    param_space = {
        'stop_loss': {'min': 0.03, 'max': 0.15},
        'position_size': {'min': 0.05, 'max': 0.30}
    }

    def objective(**params):
        return backtest_strategy(**params)

    periodic_params = periodic_opt.bayesian_optimize(
        objective, param_space, n_iter=50
    )
    print(f"周期优化后参数: {periodic_params}")

    safety_check = safety.validate_param_change(
        current_params, periodic_params
    )
    print(f"安全检查: {'通过' if safety_check['is_safe'] else '未通过'}")

    backtest_results = run_backtest(periodic_params)
    evaluation = evaluator.evaluate_optimization_result(
        current_params, periodic_params,
        0.10, 0.12, backtest_results
    )
    print(f"优化评级: {evaluation['grade']}")
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 新建AI自我优化框架文档 |
