# T.03.RM002.波动率目标管理

> 目标波动率策略 - 基于VaR/CVaR的科学风险预算分配

## 1. 风险预算动态调整

### 1.1 市场状态条件下的风险上限

| 市场状态 | 风险预算上限 | 最大回撤限制 |
|----------|--------------|--------------|
| 牛市 | 总风险×1.2 | -15% |
| 熊市 | 总风险×0.5 | -8% |
| 震荡市 | 总风险×0.8 | -10% |
| 妖股周期 | 总风险×0.7 | -12% |

### 1.2 风险预算调整规则

```python
class RiskBudgetManager:
    """风险预算动态调整"""

    def __init__(self):
        self.state_risk_multipliers = {
            '牛市': 1.2,
            '熊市': 0.5,
            '震荡市': 0.8,
            '妖股周期': 0.7,
        }
        self.max_drawdown_limits = {
            '牛市': -0.15,
            '熊市': -0.08,
            '震荡市': -0.10,
            '妖股周期': -0.12,
        }

    def get_adjusted_risk_budget(self, base_budget, market_state):
        """
        根据市场状态调整风险预算
        """
        multiplier = self.state_risk_multipliers.get(market_state, 1.0)
        adjusted = base_budget * multiplier

        max_drawdown = self.max_drawdown_limits.get(market_state, -0.10)

        return {
            'adjusted_budget': adjusted,
            'max_drawdown': max_drawdown,
            'state': market_state,
            'multiplier': multiplier
        }

    def check_drawdown_trigger(self, current_drawdown, market_state):
        """
        检查是否触发回撤预警
        """
        max_drawdown = self.max_drawdown_limits.get(market_state, -0.10)

        if current_drawdown < max_drawdown * 0.5:
            return {'level': '一级预警', 'action': '警告'}
        elif current_drawdown < max_drawdown * 0.8:
            return {'level': '二级预警', 'action': '减仓25%'}
        elif current_drawdown < max_drawdown:
            return {'level': '三级预警', 'action': '减仓50%'}
        else:
            return {'level': '正常', 'action': '正常操作'}
```

***

## 2. VaR与CVaR计算

### 2.1 VaR计算方法

```python
class VaRCalculator:
    """VaR计算"""

    def __init__(self, confidence=0.95, holding_period=1, window=252):
        self.confidence = confidence
        self.holding_period = holding_period
        self.window = window

    def historical_var(self, returns):
        """
        历史模拟法
        VaR_95 = np.percentile(收益率序列, 5)
        """
        var = np.percentile(returns, (1 - self.confidence) * 100)
        return var

    def parametric_var(self, returns):
        """
        参数法（假设正态分布）
        VaR_95 = 均值 - 1.65 × 标准差
        """
        import scipy.stats as stats
        z = stats.norm.ppf(1 - self.confidence)
        mu = np.mean(returns)
        sigma = np.std(returns)
        var = mu + z * sigma
        return var

    def cornish_fisher_var(self, returns):
        """
        Cornish-Fisher展开（考虑偏度和峰度）
        """
        import scipy.stats as stats
        z = stats.norm.ppf(1 - self.confidence)
        S = stats.skew(returns)
        K = stats.kurtosis(returns)

        z_cf = z + (z**2 - 1) * S / 6 + (z**3 - 3*z) * K / 24 - (2*z**3 - 5*z) * S**2 / 36

        mu = np.mean(returns)
        sigma = np.std(returns)
        var = mu + z_cf * sigma
        return var

    def calculate_cvar(self, returns, var):
        """
        CVaR = E[Loss | Loss > VaR]
        """
        losses = returns[returns < var]
        if len(losses) > 0:
            cvar = -np.mean(losses)
        else:
            cvar = -var
        return cvar
```

***

## 3. 概率感知投资决策（凯利公式增强版）

### 3.1 凯利公式优化版

| 公式类型 | 公式 | 说明 |
|----------|------|------|
| 基础凯利 | f = (p×b - q) / b | p=胜率, q=1-p, b=盈亏比 |
| 波动率凯利 | f = (E(R) - r_f) / σ² | E(R)=预期收益, σ=波动率 |
| 简化凯利 | f = E(R) / σ² | 仅考虑收益率和波动率 |
| 半凯利 | f = 基础凯利 × 0.5 | 保守仓位 |
| 分数凯利 | f = 基础凯利 × α | α通常取0.25-0.5 |

### 3.2 置信度调节机制

```python
class KellyPositionCalculator:
    """凯利仓位计算器"""

    def __init__(self):
        self.parameters = {
            'kelly_fraction': 0.5,
            'min_confidence_low': 0.4,
            'min_confidence_high': 0.6,
        }

    def calculate_kelly_position(self, expected_return, volatility, win_rate, profit_loss_ratio):
        """
        计算凯利仓位
        """
        p = win_rate
        q = 1 - p
        b = profit_loss_ratio

        kelly_f = (p * b - q) / b

        kelly_f = max(0, kelly_f)

        fraction = self.parameters['kelly_fraction']
        final_position = kelly_f * fraction

        return max(0, min(final_position, 0.5))

    def adjust_by_confidence(self, base_position, confidence):
        """
        置信度调节
        """
        params = self.parameters

        if confidence < params['min_confidence_low']:
            return base_position * 0.25
        elif confidence < params['min_confidence_high']:
            return base_position * 0.5
        else:
            return base_position

    def adjust_by_time_expectation(self, base_position, holding_days):
        """
        时间预期调节
        持有不足5日降低仓位
        """
        time_factor = min(holding_days / 5, 1.0)
        return base_position * time_factor
```

***

## 4. 压力测试场景

### 4.1 压力测试场景定义

| 场景 | 模拟条件 | 触发阈值 |
|------|----------|----------|
| 大盘下跌5% | 组合回撤>3% | 一级预警 |
| 大盘下跌10% | 组合回撤>6% | 二级预警 |
| 单票跌停 | 持仓单票跌停 | 三级预警 |
| 流动性枯竭 | 成交额<均量50% | 四级预警 |

### 4.2 应急预案

| 触发条件 | 应急预案 | 动作 |
|----------|---------|------|
| 单日回撤 > 5% | 暂停新开仓 | 停止操作 |
| 单日回撤 > 8% | 减仓50% | 减半 |
| VaR突破限额 | 减仓至合规 | 降至VaR内 |
| 连续3日跑输基准 | 评审策略有效性 | 暂停或调整 |

```python
class StressTestScenario:
    """压力测试场景"""

    def __init__(self):
        self.scenarios = {
            'market_drop_5pct': {
                'market_change': -0.05,
                'portfolio_threshold': -0.03,
                'warning_level': '一级预警'
            },
            'market_drop_10pct': {
                'market_change': -0.10,
                'portfolio_threshold': -0.06,
                'warning_level': '二级预警'
            },
            'single_limit_down': {
                'stock_change': -0.10,
                'warning_level': '三级预警'
            },
            'liquidity_crisis': {
                'volume_ratio': 0.5,
                'warning_level': '四级预警'
            }
        }

    def run_stress_test(self, portfolio_data, market_scenarios):
        """
        运行压力测试
        """
        results = []

        for scenario_name, scenario_params in self.scenarios.items():
            if scenario_name == 'market_drop_5pct':
                result = self.simulate_market_drop(portfolio_data, scenario_params)
            elif scenario_name == 'market_drop_10pct':
                result = self.simulate_market_drop(portfolio_data, scenario_params)
            elif scenario_name == 'single_limit_down':
                result = self.simulate_limit_down(portfolio_data, scenario_params)
            elif scenario_name == 'liquidity_crisis':
                result = self.simulate_liquidity(portfolio_data, scenario_params)

            results.append(result)

        return results

    def get_emergency_action(self, trigger_condition):
        """
        获取应急预案
        """
        emergency_rules = {
            '单日回撤>5%': {'action': '暂停新开仓', 'position_change': 0},
            '单日回撤>8%': {'action': '减仓50%', 'position_change': -0.5},
            'VaR突破': {'action': '减仓至合规', 'position_change': -0.3},
            '连续3日跑输基准': {'action': '评审策略有效性', 'position_change': 0},
        }

        return emergency_rules.get(trigger_condition, {'action': '正常', 'position_change': 0})
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合VaR/CVaR计算、凯利仓位公式、压力测试场景 |
