---
module_id: SENSITIVITY_ANALYSIS_001_8214
version: 1.0.0
status: Active
priority: P2
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 6 组合优化层
compliance_level: 专业标准
responsibility:
- 敏感性分析
layer: layer_06
---



# 敏感性分析模块蓝图



## 核心定位



负责敏感性分析模块的设计与构建和运行和操作，分析参数变化对优化结果的影响，识别关键参数，提供参数稳定性评估，生成敏感性报告。



> **职责边界**:

> - ✅ 本文档负责：敏感性分析、参数敏感性评估、关键参数识别

> - ❌ 本文档不负责：参数优化（由STOCHASTIC_OPTIMIZATION模块负责）



## 设计目标



### 主要目标



1. **敏感性分析**: 分析参数变化对结果的影响

2. **关键参数**: 识别影响最大的关键参数

3. **稳定性评估**: 评估参数稳定性

4. **报告生成**: 生成详细的敏感性报告



### 质量目标



- 分析精度: >95%

- 性能指标: 单次分析<500ms

- 文档完整性: 100%



## 核心功能



### 功能清单



1. **参数敏感性分析**

   - 单参数敏感性

   - 多参数交互敏感性

   - 全局敏感性分析

   - 局部敏感性分析



2. **关键参数识别**

   - 参数重要性排序

   - 敏感性指标计算

   - 关键参数筛选

   - 参数分组



3. **稳定性评估**

   - 参数稳定性评分

   - 结果稳定性评分

   - 稳定性趋势分析

   - 稳定性预警



4. **可视化展示**

   - 敏感性曲线图

   - 龙卷风图

   - 蜘蛛图

   - 热力图



## 技术架构



### 开源方案集成



| 组件 | 推荐方案 | GitHub Stars | 说明 |

|------|----------|--------------|------|

| 敏感性分析 | SALib | 800+ | 专业敏感性分析库 |

| 可视化 | matplotlib | - | 图表绘制 |

| 数值计算 | numpy | - | 数值分析 |



### 核心算法



```python

import numpy as np

from SALib.analyze import sobol, morris

from SALib.sample import saltelli, morris as morris_sample



class SensitivityAnalyzer:

    """敏感性分析器"""



    def __init__(self, optimizer_func, param_names, param_bounds):

        """

        Parameters:

        -----------

        optimizer_func : callable

            优化函数

        param_names : list

            参数名称列表

        param_bounds : list

            参数边界列表 [(min, max), ...]

        """

        self.optimizer_func = optimizer_func

        self.param_names = param_names

        self.param_bounds = param_bounds



    def local_sensitivity(self, base_params, param_deltas=None):

        """

        局部敏感性分析



        Parameters:

        -----------

        base_params : dict

            基准参数值

        param_deltas : dict

            参数变化量

        """

        if param_deltas is None:

            param_deltas = {name: 0.1 for name in self.param_names}



        # 基准结果

        base_result = self.optimizer_func(**base_params)



        sensitivities = {}



        for param_name in self.param_names:

            delta = param_deltas[param_name]

            base_value = base_params[param_name]



            # 正向扰动

            params_plus = base_params.copy()

            params_plus[param_name] = base_value * (1 + delta)

            result_plus = self.optimizer_func(**params_plus)



            # 负向扰动

            params_minus = base_params.copy()

            params_minus[param_name] = base_value * (1 - delta)

            result_minus = self.optimizer_func(**params_minus)



            # 计算敏感性指标

            sensitivities[param_name] = {

                'sensitivity': (result_plus - result_minus) / (2 * delta * base_value),

                'elasticity': ((result_plus - result_minus) / base_result) /

                             ((params_plus[param_name] - params_minus[param_name]) / base_value),

                'impact_plus': (result_plus - base_result) / base_result,

                'impact_minus': (result_minus - base_result) / base_result

            }



        return sensitivities



    def global_sensitivity_sobol(self, n_samples=1000):

        """

        全局敏感性分析 (Sobol方法)



        Parameters:

        -----------

        n_samples : int

            样本数量

        """

        # 定义问题

        problem = {

            'num_vars': len(self.param_names),

            'names': self.param_names,

            'bounds': self.param_bounds

        }



        # 生成样本

        param_values = saltelli.sample(problem, n_samples)



        # 运行模型

        results = []

        for params in param_values:

            param_dict = dict(zip(self.param_names, params))

            result = self.optimizer_func(**param_dict)

            results.append(result)



        results = np.array(results)



        # Sobol分析

        si = sobol.analyze(problem, results)



        return {

            'S1': dict(zip(self.param_names, si['S1'])),  # 一阶敏感性

            'ST': dict(zip(self.param_names, si['ST'])),  # 总敏感性

            'S2': si['S2']  # 二阶敏感性

        }



    def global_sensitivity_morris(self, n_trajectories=10):

        """

        全局敏感性分析 (Morris方法)



        Parameters:

        -----------

        n_trajectories : int

            轨迹数量

        """

        # 定义问题

        problem = {

            'num_vars': len(self.param_names),

            'names': self.param_names,

            'bounds': self.param_bounds

        }



        # 生成样本

        param_values = morris_sample.sample(problem, n_trajectories)



        # 运行模型

        results = []

        for params in param_values:

            param_dict = dict(zip(self.param_names, params))

            result = self.optimizer_func(**param_dict)

            results.append(result)



        results = np.array(results)



        # Morris分析

        si = morris.analyze(problem, param_values, results)



        return {

            'mu': dict(zip(self.param_names, si['mu'])),  # 平均效应

            'mu_star': dict(zip(self.param_names, si['mu_star'])),  # 平均绝对效应

            'sigma': dict(zip(self.param_names, si['sigma']))  # 标准差

        }



    def identify_key_parameters(self, sensitivity_results, threshold=0.1):

        """

        识别关键参数



        Parameters:

        -----------

        sensitivity_results : dict

            敏感性分析结果

        threshold : float

            重要性阈值

        """

        key_params = []



        for param_name, sensitivity in sensitivity_results.items():

            if isinstance(sensitivity, dict):

                sensitivity_value = abs(sensitivity.get('sensitivity', 0))

            else:

                sensitivity_value = abs(sensitivity)



            if sensitivity_value > threshold:

                key_params.append({

                    'name': param_name,

                    'sensitivity': sensitivity_value,

                    'rank': 0

                })



        # 排序

        key_params.sort(key=lambda x: x['sensitivity'], reverse=True)



        # 分配排名

        for i, param in enumerate(key_params):

            param['rank'] = i + 1



        return key_params



    def stability_assessment(self, base_params, n_iterations=100):

        """

        参数稳定性评估



        Parameters:

        -----------

        base_params : dict

            基准参数值

        n_iterations : int

            迭代次数

        """

        results = []



        for _ in range(n_iterations):

            # 添加随机扰动

            perturbed_params = base_params.copy()

            for param_name in self.param_names:

                perturbation = np.random.normal(0, 0.05)  # 5%标准差

                perturbed_params[param_name] *= (1 + perturbation)



            result = self.optimizer_func(**perturbed_params)

            results.append(result)



        results = np.array(results)



        # 计算稳定性指标

        stability_metrics = {

            'mean': np.mean(results),

            'std': np.std(results),

            'cv': np.std(results) / np.mean(results),  # 变异系数

            'min': np.min(results),

            'max': np.max(results),

            'range': np.max(results) - np.min(results),

            'stability_score': 1.0 / (1.0 + np.std(results) / np.mean(results))

        }



        return stability_metrics

```



## 接口设计



### 输入接口



```python

class SensitivityAnalysisInput:

    optimizer_func: callable      # 优化函数

    base_params: dict             # 基准参数

    param_names: list             # 参数名称

    param_bounds: list            # 参数边界

    analysis_type: str            # 分析类型

```



### 输出接口



```python

class SensitivityAnalysisOutput:

    sensitivities: dict           # 敏感性指标

    key_parameters: list          # 关键参数

    stability_metrics: dict       # 稳定性指标

    visualization: dict           # 可视化数据

```



## 实施计划



### 阶段1: 基础功能 (1周)



- [ ] 集成SALib

- [ ] 实现局部敏感性分析

- [ ] 实现全局敏感性分析

- [ ] 单元测试



### 阶段2: 高级功能 (1周)



- [ ] 关键参数识别

- [ ] 稳定性评估

- [ ] 可视化展示

- [ ] 性能优化



### 阶段3: 集成测试 (1周)



- [ ] 与优化模块集成

- [ ] 回测验证

- [ ] 文档完善



## 验收标准（可检查）



| 标准 | 指标 |

|------|------|

| 分析精度 | >95% |

| 性能 | 单次分析<500ms |

| 覆盖率 | 支持主流分析方法 |

| 文档 | API文档完整 |



## 接口与契约（蓝图终稿）



- **契约真源**：`API_Contract.md`

- **对外接口边界**：本模块对外提供敏感性分析任务的计算输出与诊断指标；不执行交易，不替代策略/风控对口径的最终定义。



## 已知限制



- 分析结果对输入假设与数据质量敏感；实施阶段需在契约真源或子契约中固化输入口径、缺失值处理与降级策略。



## 变更历史



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.0 | 2026-04-07 | 初始版本创建 | 组合优化层负责人 |
