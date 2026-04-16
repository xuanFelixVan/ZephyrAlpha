---
module_id: OPTIMIZER_DIAGNOSTICS_001_2699
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
- 优化器诊断
layer: layer_06
---



# 优化器诊断工具蓝图



## 核心定位



负责优化器诊断工具的设计与构建和运行和操作，诊断优化器为什么给出某个解，检测数值问题，提供优化失败原因分析，生成诊断报告，确保优化结果的可靠性。



> **职责边界**: 

> - ✅ 本文档负责：优化器诊断、数值稳定性检查、优化失败分析

> - ❌ 本文档不负责：优化求解（由CONSTRAINT_SOLVER_INTEGRATION模块负责）



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。优化器诊断对外输入（优化问题、求解状态、解向量、约束与参数）与输出（诊断结论、问题清单、改进建议、告警事件）如以接口/事件对外提供，其口径以该真源为准。



## 验收标准（可检查）



- 对至少 1 个“可行解”与 1 个“不可行/不收敛”样例，能输出不同的诊断结论，并包含可复核的关键指标（如收敛状态、违反约束量、条件数/对偶间隙等）。

- 诊断结果结构化可机器读取（JSON/表格均可），便于流水线门禁或审计系统消费。

- 对外输出/事件能在 `API_Contract.md` 中定位到契约入口（或在“已知限制”列出未闭合项）。



## 已知限制



- 不同求解器（OSQP/SCS/ECOS 等）的状态码与诊断指标口径不同；落地阶段需固化映射表与回归用例，并回填契约真源。



## 设计目标



### 主要目标



1. **诊断功能**: 诊断优化器为什么给出某个解

2. **数值检查**: 检测条件数、奇异性等数值问题

3. **失败分析**: 提供优化失败原因分析

4. **报告生成**: 生成详细的诊断报告



### 质量目标



- 诊断准确率: >95%

- 性能指标: 单次诊断<100ms

- 文档完整性: 100%



## 核心功能



### 功能清单



1. **数值稳定性检查**

   - 条件数检查

   - 矩阵奇异性检测

   - 数值精度验证

   - 溢出/下溢检测



2. **优化结果诊断**

   - KKT条件验证

   - 对偶间隙检查

   - 约束活跃性分析

   - 目标函数梯度检查



3. **失败原因分析**

   - 无可行解诊断

   - 无界解诊断

   - 收敛失败诊断

   - 数值问题诊断



4. **诊断报告**

   - 问题摘要

   - 详细诊断结果

   - 改进建议

   - 可视化展示



## 技术架构



### 开源方案集成



| 组件 | 推荐方案 | 说明 |

|------|----------|------|

| 优化诊断 | cvxpy | 内置诊断功能 |

| 数值计算 | numpy | 数值检查 |

| 可视化 | matplotlib | 诊断可视化 |



### 核心算法



```python

import numpy as np

import cvxpy as cp



class OptimizerDiagnostics:

    """优化器诊断器"""

    

    def __init__(self):

        self.issues = []

        self.warnings = []

        self.info = []

    

    def diagnose_optimization(self, problem, solution, expected_returns, cov_matrix):

        """

        全面诊断优化结果

        

        Parameters:

        -----------

        problem : cp.Problem

            优化问题

        solution : np.array

            优化结果

        expected_returns : np.array

            预期收益

        cov_matrix : np.array

            协方差矩阵

        """

        self.issues = []

        self.warnings = []

        self.info = []

        

        # 1. 数值稳定性检查

        self._check_numerical_stability(cov_matrix)

        

        # 2. 优化状态检查

        self._check_optimization_status(problem)

        

        # 3. KKT条件验证

        self._check_kkt_conditions(problem, solution)

        

        # 4. 约束满足检查

        self._check_constraint_satisfaction(problem, solution)

        

        # 5. 结果合理性检查

        self._check_solution_rationality(solution, expected_returns, cov_matrix)

        

        return self._generate_report()

    

    def _check_numerical_stability(self, cov_matrix):

        """检查数值稳定性"""

        # 条件数检查

        cond = np.linalg.cond(cov_matrix)

        if cond > 1e10:

            self.issues.append({

                'type': 'numerical_instability',

                'severity': 'high',

                'message': f'协方差矩阵条件数过高: {cond:.2e}',

                'suggestion': '考虑使用收缩估计或因子模型'

            })

        elif cond > 1e6:

            self.warnings.append({

                'type': 'numerical_warning',

                'severity': 'medium',

                'message': f'协方差矩阵条件数较高: {cond:.2e}',

                'suggestion': '建议检查数据质量'

            })

        

        # 奇异性检查

        eigenvalues = np.linalg.eigvalsh(cov_matrix)

        min_eigenvalue = np.min(eigenvalues)

        if min_eigenvalue < 1e-10:

            self.issues.append({

                'type': 'singular_matrix',

                'severity': 'high',

                'message': f'协方差矩阵接近奇异，最小特征值: {min_eigenvalue:.2e}',

                'suggestion': '添加正则化或使用伪逆'

            })

        

        # 数值范围检查

        if np.any(np.isnan(cov_matrix)) or np.any(np.isinf(cov_matrix)):

            self.issues.append({

                'type': 'invalid_values',

                'severity': 'high',

                'message': '协方差矩阵包含NaN或Inf',

                'suggestion': '检查数据预处理流程'

            })

    

    def _check_optimization_status(self, problem):

        """检查优化状态"""

        status = problem.status

        

        if status == 'infeasible':

            self.issues.append({

                'type': 'infeasible',

                'severity': 'high',

                'message': '优化问题无可行解',

                'suggestion': '检查约束条件是否冲突'

            })

        elif status == 'unbounded':

            self.issues.append({

                'type': 'unbounded',

                'severity': 'high',

                'message': '优化问题无界',

                'suggestion': '检查目标函数和约束条件'

            })

        elif status == 'solver_error':

            self.issues.append({

                'type': 'solver_error',

                'severity': 'high',

                'message': '求解器错误',

                'suggestion': '尝试其他求解器或检查问题表述'

            })

        elif status != 'optimal':

            self.warnings.append({

                'type': 'suboptimal',

                'severity': 'medium',

                'message': f'优化状态: {status}',

                'suggestion': '结果可能不是最优解'

            })

    

    def _check_kkt_conditions(self, problem, solution):

        """验证KKT条件"""

        try:

            # 获取对偶变量

            dual_vars = self._extract_dual_variables(problem)

            

            # 检查对偶间隙

            primal_value = problem.value

            dual_value = self._compute_dual_value(dual_vars)

            duality_gap = abs(primal_value - dual_value)

            

            if duality_gap > 1e-4:

                self.warnings.append({

                    'type': 'duality_gap',

                    'severity': 'medium',

                    'message': f'对偶间隙较大: {duality_gap:.6f}',

                    'suggestion': '可能未达到最优解'

                })

        except Exception as e:

            self.info.append({

                'type': 'kkt_check',

                'message': f'KKT条件检查失败: {str(e)}'

            })

    

    def _check_constraint_satisfaction(self, problem, solution):

        """检查约束满足情况"""

        for constraint in problem.constraints:

            violation = self._compute_constraint_violation(constraint, solution)

            

            if violation > 1e-4:

                self.issues.append({

                    'type': 'constraint_violation',

                    'severity': 'high',

                    'message': f'约束违反: {constraint}',

                    'violation': violation,

                    'suggestion': '检查约束定义或求解器精度'

                })

    

    def _check_solution_rationality(self, solution, expected_returns, cov_matrix):

        """检查结果合理性"""

        # 权重和检查

        weight_sum = np.sum(solution)

        if abs(weight_sum - 1.0) > 1e-4:

            self.issues.append({

                'type': 'weight_sum',

                'severity': 'high',

                'message': f'权重和不等于1: {weight_sum:.6f}',

                'suggestion': '检查约束条件'

            })

        

        # 负权重检查

        if np.any(solution < -1e-6):

            self.warnings.append({

                'type': 'negative_weights',

                'severity': 'medium',

                'message': f'存在负权重: {np.min(solution):.6f}',

                'suggestion': '检查是否允许做空'

            })

        

        # 集中度检查

        max_weight = np.max(np.abs(solution))

        if max_weight > 0.5:

            self.warnings.append({

                'type': 'high_concentration',

                'severity': 'medium',

                'message': f'单资产权重过大: {max_weight:.2%}',

                'suggestion': '考虑添加集中度约束'

            })

    

    def _generate_report(self):

        """生成诊断报告"""

        return {

            'status': 'healthy' if len(self.issues) == 0 else 'issues_found',

            'total_issues': len(self.issues),

            'total_warnings': len(self.warnings),

            'issues': self.issues,

            'warnings': self.warnings,

            'info': self.info,

            'recommendations': self._generate_recommendations()

        }

    

    def _generate_recommendations(self):

        """生成改进建议"""

        recommendations = []

        

        for issue in self.issues:

            if 'suggestion' in issue:

                recommendations.append(issue['suggestion'])

        

        return list(set(recommendations))

    

    def _extract_dual_variables(self, problem):

        """提取对偶变量"""

        dual_vars = {}

        for i, constraint in enumerate(problem.constraints):

            if hasattr(constraint, 'dual_value'):

                dual_vars[f'constraint_{i}'] = constraint.dual_value

        return dual_vars

    

    def _compute_dual_value(self, dual_vars):

        """计算对偶值"""

        return sum(np.sum(np.abs(v)) for v in dual_vars.values() if v is not None)

    

    def _compute_constraint_violation(self, constraint, solution):

        """计算约束违反程度"""

        try:

            if hasattr(constraint, 'violation'):

                return constraint.violation()

            else:

                return 0.0

        except:

            return 0.0

```



## 接口设计



### 输入接口



```python

class OptimizerDiagnosticsInput:

    problem: cp.Problem          # 优化问题

    solution: np.array           # 优化结果

    expected_returns: np.array   # 预期收益

    cov_matrix: np.array         # 协方差矩阵

    constraints: list            # 约束列表

```



### 输出接口



```python

class OptimizerDiagnosticsOutput:

    status: str                  # 诊断状态

    issues: list                 # 问题列表

    warnings: list               # 警告列表

    recommendations: list        # 改进建议

    report: dict                 # 详细报告

```



## 实施计划



### 阶段1: 基础诊断 (1周)



- [ ] 数值稳定性检查

- [ ] 优化状态检查

- [ ] 约束满足检查

- [ ] 单元测试



### 阶段2: 高级诊断 (1周)



- [ ] KKT条件验证

- [ ] 结果合理性检查

- [ ] 失败原因分析

- [ ] 性能优化



### 阶段3: 集成测试 (1周)



- [ ] 与优化模块集成

- [ ] 可视化

- [ ] 文档完善



## 验收标准



| 标准 | 指标 |

|------|------|

| 诊断准确率 | >95% |

| 性能 | 单次诊断<100ms |

| 覆盖率 | 支持主流优化问题 |

| 文档 | API文档完整 |



## 变更历史



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.0 | 2026-04-07 | 初始版本创建 | 组合优化层负责人 |

