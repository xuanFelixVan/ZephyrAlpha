---

module_id: PORTFOLIO_HEALTH_SCORING_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 实施团队

standard_type: 专业量化机构蓝图

applicable_scope: Layer 6 组合优化层

compliance_level: 专业标准

responsibility:

  - 组合健康度评分

  - 多维度健康评估

  - 健康度趋势追踪

  - 预警机制

layer: layer_06

---



# 组合健康度评分系统蓝图



## 核心定位



负责组合健康度评分系统的设计与构建和运行和操作，综合评估组合质量，提供多维度健康度指标，追踪健康度趋势，建立预警机制。



> **职责边界**: 

> - ✅ 本文档负责：组合健康度评分、多维度健康评估、健康度趋势追踪

> - ❌ 本文档不负责：绩效分析（由PORTFOLIO_PERFORMANCE_EVALUATION模块负责）



## 设计目标



### 主要目标



1. **健康度评分**: 综合评估组合质量

2. **多维度评估**: 从多个维度评估健康度

3. **趋势追踪**: 追踪健康度变化趋势

4. **预警机制**: 建立健康度预警系统



### 质量目标



- 评分准确性: >90%

- 性能指标: 单次评分<200ms

- 文档完整性: 100%



## 核心功能



### 功能清单



1. **健康度维度**

   - 风险健康度

   - 收益健康度

   - 流动性健康度

   - 集中度健康度

   - 稳定性健康度



2. **评分模型**

   - 加权评分模型

   - 层次分析法(AHP)

   - 熵权法

   - 模糊综合评价



3. **趋势分析**

   - 健康度历史曲线

   - 趋势预测

   - 异常检测

   - 变化率分析



4. **预警系统**

   - 阈值预警

   - 趋势预警

   - 综合预警

   - 预警通知



## 技术架构



### 开源方案集成



| 组件 | 推荐方案 | 说明 |

|------|----------|------|

| 绩效分析 | pyfolio | 健康度计算基础 |

| 可视化 | matplotlib | 健康度图表 |

| 数据库 | SQLite | 历史数据存储 |



### 核心算法



```python

import numpy as np

import pandas as pd

from datetime import datetime, timedelta



class PortfolioHealthScorer:

    """组合健康度评分器"""

    

    def __init__(self, weights, returns, cov_matrix, volumes, 

                 risk_free_rate=0.03):

        """

        Parameters:

        -----------

        weights : np.array

            投资组合权重

        returns : np.array

            历史收益率

        cov_matrix : np.array

            协方差矩阵

        volumes : np.array

            成交量

        risk_free_rate : float

            无风险利率

        """

        self.weights = weights

        self.returns = returns

        self.cov = cov_matrix

        self.volumes = volumes

        self.rf = risk_free_rate

    

    def calculate_health_score(self):

        """计算综合健康度评分"""

        # 1. 风险健康度

        risk_health = self._calculate_risk_health()

        

        # 2. 收益健康度

        return_health = self._calculate_return_health()

        

        # 3. 流动性健康度

        liquidity_health = self._calculate_liquidity_health()

        

        # 4. 集中度健康度

        concentration_health = self._calculate_concentration_health()

        

        # 5. 稳定性健康度

        stability_health = self._calculate_stability_health()

        

        # 6. 综合评分 (加权平均)

        weights = {

            'risk': 0.25,

            'return': 0.25,

            'liquidity': 0.20,

            'concentration': 0.15,

            'stability': 0.15

        }

        

        overall_score = (

            weights['risk'] * risk_health +

            weights['return'] * return_health +

            weights['liquidity'] * liquidity_health +

            weights['concentration'] * concentration_health +

            weights['stability'] * stability_health

        )

        

        return {

            'overall_score': overall_score,

            'dimension_scores': {

                'risk': risk_health,

                'return': return_health,

                'liquidity': liquidity_health,

                'concentration': concentration_health,

                'stability': stability_health

            },

            'health_grade': self._get_health_grade(overall_score),

            'timestamp': datetime.now().isoformat()

        }

    

    def _calculate_risk_health(self):

        """计算风险健康度"""

        portfolio_return = np.mean(self.returns @ self.weights) * 252

        portfolio_vol = np.sqrt(self.weights @ self.cov @ self.weights) * np.sqrt(252)

        sharpe = (portfolio_return - self.rf) / portfolio_vol if portfolio_vol > 0 else 0

        

        # 最大回撤

        cumulative = (1 + self.returns @ self.weights).cumprod()

        running_max = np.maximum.accumulate(cumulative)

        drawdown = (cumulative - running_max) / running_max

        max_dd = np.min(drawdown)

        

        # VaR

        var_95 = np.percentile(self.returns @ self.weights, 5)

        

        # 风险健康度评分 (0-100)

        sharpe_score = min(max(sharpe * 25, 0), 100)

        dd_score = min(max((1 + max_dd) * 100, 0), 100)

        var_score = min(max((1 + var_95 * 10) * 50, 0), 100)

        

        risk_health = (sharpe_score + dd_score + var_score) / 3

        

        return risk_health

    

    def _calculate_return_health(self):

        """计算收益健康度"""

        portfolio_returns = self.returns @ self.weights

        

        # 年化收益

        annual_return = np.mean(portfolio_returns) * 252

        

        # 正收益比例

        positive_ratio = np.sum(portfolio_returns > 0) / len(portfolio_returns)

        

        # 收益稳定性

        return_std = np.std(portfolio_returns)

        stability = 1 / (1 + return_std * 10)

        

        # 收益健康度评分 (0-100)

        return_score = min(max(annual_return * 200, 0), 100)

        positive_score = positive_ratio * 100

        stability_score = stability * 100

        

        return_health = (return_score + positive_score + stability_score) / 3

        

        return return_health

    

    def _calculate_liquidity_health(self):

        """计算流动性健康度"""

        # 加权平均成交量

        weighted_volume = np.sum(self.weights * self.volumes)

        

        # 流动性覆盖率

        liquidity_coverage = weighted_volume / np.sum(self.volumes)

        

        # 流动性集中度

        volume_concentration = np.sum(np.sort(self.weights)[-5:] * 

                                      np.sort(self.volumes)[-5:]) / weighted_volume

        

        # 流动性健康度评分 (0-100)

        coverage_score = liquidity_coverage * 100

        concentration_score = (1 - volume_concentration) * 100

        

        liquidity_health = (coverage_score + concentration_score) / 2

        

        return liquidity_health

    

    def _calculate_concentration_health(self):

        """计算集中度健康度"""

        # HHI指数

        hhi = np.sum(self.weights ** 2)

        

        # 有效资产数量

        effective_n = 1 / hhi if hhi > 0 else 0

        

        # 最大权重

        max_weight = np.max(self.weights)

        

        # 前5大权重

        top5_weight = np.sum(np.sort(self.weights)[-5:])

        

        # 集中度健康度评分 (0-100)

        hhi_score = min(max((1 - hhi) * 100, 0), 100)

        effective_n_score = min(max(effective_n * 10, 0), 100)

        max_weight_score = min(max((1 - max_weight) * 100, 0), 100)

        top5_score = min(max((1 - top5_weight) * 100, 0), 100)

        

        concentration_health = (hhi_score + effective_n_score + 

                               max_weight_score + top5_score) / 4

        

        return concentration_health

    

    def _calculate_stability_health(self):

        """计算稳定性健康度"""

        portfolio_returns = self.returns @ self.weights

        

        # 收益波动率

        volatility = np.std(portfolio_returns)

        

        # 偏度

        skewness = pd.Series(portfolio_returns).skew()

        

        # 峰度

        kurtosis = pd.Series(portfolio_returns).kurtosis()

        

        # 自相关性

        autocorr = pd.Series(portfolio_returns).autocorr()

        

        # 稳定性健康度评分 (0-100)

        vol_score = min(max((1 - volatility * 10) * 100, 0), 100)

        skew_score = min(max((1 - abs(skewness) / 2) * 100, 0), 100)

        kurt_score = min(max((1 - abs(kurtosis) / 10) * 100, 0), 100)

        autocorr_score = min(max((1 - abs(autocorr)) * 100, 0), 100)

        

        stability_health = (vol_score + skew_score + kurt_score + autocorr_score) / 4

        

        return stability_health

    

    def _get_health_grade(self, score):

        """获取健康度等级"""

        if score >= 90:

            return 'A+'

        elif score >= 80:

            return 'A'

        elif score >= 70:

            return 'B+'

        elif score >= 60:

            return 'B'

        elif score >= 50:

            return 'C'

        else:

            return 'D'

    

    def track_health_trend(self, history_days=30):

        """追踪健康度趋势"""

        # 这里需要历史数据

        # 简化实现：返回模拟数据

        dates = pd.date_range(end=datetime.now(), periods=history_days, freq='D')

        

        trend_data = []

        for date in dates:

            # 模拟历史健康度

            score = 70 + np.random.randn() * 10

            trend_data.append({

                'date': date,

                'score': max(min(score, 100), 0)

            })

        

        return pd.DataFrame(trend_data)

    

    def generate_health_alert(self, score, thresholds=None):

        """生成健康度预警"""

        if thresholds is None:

            thresholds = {

                'critical': 40,

                'warning': 60,

                'attention': 75

            }

        

        alerts = []

        

        if score < thresholds['critical']:

            alerts.append({

                'level': 'critical',

                'message': f'组合健康度严重不足: {score:.1f}',

                'action': '立即检查并调整组合'

            })

        elif score < thresholds['warning']:

            alerts.append({

                'level': 'warning',

                'message': f'组合健康度较低: {score:.1f}',

                'action': '建议优化组合结构'

            })

        elif score < thresholds['attention']:

            alerts.append({

                'level': 'attention',

                'message': f'组合健康度需关注: {score:.1f}',

                'action': '建议监控组合表现'

            })

        

        return alerts

```



## 接口设计



### 输入接口



```python

class HealthScoringInput:

    weights: np.array            # 投资组合权重

    returns: np.array            # 历史收益率

    cov_matrix: np.array         # 协方差矩阵

    volumes: np.array            # 成交量

    risk_free_rate: float        # 无风险利率

```



### 输出接口



```python

class HealthScoringOutput:

    overall_score: float         # 综合评分

    dimension_scores: dict       # 各维度评分

    health_grade: str            # 健康度等级

    trend_data: pd.DataFrame     # 趋势数据

    alerts: list                 # 预警信息

```



## 实施计划



### 阶段1: 基础功能 (1周)



- [ ] 健康度维度设计

- [ ] 评分模型实现

- [ ] 单元测试



### 阶段2: 高级功能 (1周)



- [ ] 趋势追踪

- [ ] 预警系统

- [ ] 可视化展示

- [ ] 性能优化



### 阶段3: 集成测试 (1周)



- [ ] 与优化模块集成

- [ ] 回测验证

- [ ] 文档完善



## 验收标准



| 标准 | 指标 |

|------|------|

| 评分准确性 | >90% |

| 性能 | 单次评分<200ms |

| 覆盖率 | 5个健康度维度 |

| 文档 | API文档完整 |



## 接口与契约（蓝图终稿）



- **契约真源**：`API_Contract.md`

- **对外接口边界**：本模块提供健康度评分与维度分解的查询/批处理计算能力；不替代绩效归因与风险模型的权威输出。



## 验收标准（可检查）



- 在给定一组权重、收益率与协方差矩阵输入时，能够稳定输出综合评分与各维度评分，并满足文档中声明的性能指标（单次评分 < 200ms）与维度覆盖（≥5 个维度）。



## 已知限制



- 评分维度权重与阈值属于策略/风控共同配置项，实施阶段需要与契约真源对齐并固化默认值；在此之前仅保证接口形态与可追溯计算链路。



## 变更历史



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.0 | 2026-04-07 | 初始版本创建 | 组合优化层负责人 |

