# T.05.RC002.风险控制量化体系

> 风险控制量化体系
>
> **策略编号**：T.05.RC002
> **所属模块**：05_RISK_CONTROL
> **文档类型**：风险控制
> **优先级**：P1
>
> **配套文档**：
> - [T.05.RC001.实时风险监控.md](./T.05.RC001.实时风险监控.md) - 实时风控
> - [T.04.EX006.A股交易规则.md](../02_TACTICS/04_EXECUTION/T.04.EX006.A股交易规则.md) - 交易规则

---

## 1. 仓位管理量化

```python
class PositionManagementQuantifier:
    """
    仓位管理量化

    核心理念：
    - 核心仓位：趋势明确的标的
    - 防守仓位：防御性品种
    - 现金仓位：应对极端情况
    """

    POSITION_CONFIGS = {
        'aggressive': {
            'core': 0.6,
            'defensive': 0.2,
            'cash': 0.2
        },
        'neutral': {
            'core': 0.5,
            'defensive': 0.2,
            'cash': 0.3
        },
        'conservative': {
            'core': 0.4,
            'defensive': 0.3,
            'cash': 0.3
        }
    }

    def calc_core_position(self, total_capital: float,
                         risk_preference: str = 'neutral') -> dict:
        """
        计算核心仓位配置

        参数:
            total_capital: 总资金
            risk_preference: 风险偏好

        返回:
            position_allocation: 仓位配置
        """
        config = self.POSITION_CONFIGS.get(risk_preference, self.POSITION_CONFIGS['neutral'])

        return {
            'core_position': total_capital * config['core'],
            'defensive_position': total_capital * config['defensive'],
            'cash_reserve': total_capital * config['cash'],
            'total_usable': total_capital * (config['core'] + config['defensive'])
        }

    def adjust_for_geopolitical_risk(self, base_position: float,
                                    risk_level: str = 'medium') -> dict:
        """
        根据地缘冲突风险调整仓位

        参数:
            base_position: 基础仓位
            risk_level: 风险等级

        返回:
            adjustment: 调整方案
        """
        adjustments = {
            'high': {
                'cash_ratio': 0.30,
                'safe_allocation': 0.70 * 0.80,
                'abandon_sectors': ['科技', '机器人', 'AI']
            },
            'medium': {
                'cash_ratio': 0.20,
                'safe_allocation': 0.70 * 0.60,
                'abandon_sectors': []
            },
            'low': {
                'cash_ratio': 0.10,
                'safe_allocation': 0.70,
                'abandon_sectors': []
            }
        }

        return adjustments.get(risk_level, adjustments['medium'])

    def calc_dynamic_position(self, signal_strength: float,
                            market_volatility: float,
                            max_position: float = 0.20) -> float:
        """
        计算动态仓位

        公式: position = signal_strength * (1 / volatility) * base_position

        参数:
            signal_strength: 信号强度 (0-1)
            market_volatility: 市场波动率
            max_position: 最大仓位

        返回:
            position: 建议仓位
        """
        base_position = 0.10

        position = signal_strength * (1 / market_volatility) * base_position

        return min(position, max_position)

    def calc Kelly_position(self, win_rate: float, avg_win: float,
                          avg_loss: float) -> float:
        """
        Kelly公式计算仓位

        公式: f* = (p × b - q) / b
        其中: p=胜率, q=败率, b=盈亏比

        参数:
            win_rate: 胜率
            avg_win: 平均盈利
            avg_loss: 平均亏损

        返回:
            kelly_fraction: Kelly仓位比例
        """
        if avg_loss == 0:
            return 0

        b = avg_win / avg_loss
        q = 1 - win_rate
        p = win_rate

        kelly = (p * b - q) / b

        return max(0, min(kelly * 0.5, 0.25))
```

---

## 2. 止损止盈量化

```python
class StopLossTakeProfitQuantifier:
    """
    止损止盈量化

    止损方法：
    - 成本降低法：成本降低2-3个点
    - 趋势止损：跌破30日均线
    - 追踪止损：从高点回落一定比例
    """

    def calc_stop_loss(self, entry_price: float,
                      method: str = 'trailing',
                      current_high: float = None) -> dict:
        """
        计算止损价

        参数:
            entry_price: 入场价格
            method: 止损方法
            current_high: 当前最高价（用于追踪止损）

        返回:
            stop_loss: 止损方案
        """
        methods = {
            'cost_reduction': {
                'stop_price': entry_price * 0.97,
                'description': '成本降低3%止损',
                'use_case': '短线交易'
            },
            'trend': {
                'ma30_price': entry_price * 0.90,
                'description': '跌破30日均线减仓',
                'use_case': '趋势交易'
            },
            'trailing': {
                'initial_stop': entry_price * 0.95,
                'trailing_pct': 0.05,
                'current_high': current_high or entry_price,
                'dynamic_stop': (current_high or entry_price) * (1 - 0.05),
                'description': '从高点回落5%止损'
            }
        }

        return methods.get(method, methods['trailing'])

    def check_take_profit_signals(self, price_data: pd.DataFrame) -> dict:
        """
        检查止盈信号

        参数:
            price_data: 价格数据

        返回:
            signals: 止盈信号
        """
        signals = []

        if self.check_death_cross(price_data):
            signals.append(('death_cross', 0.8))

        if self.check_top_divergence(price_data):
            signals.append(('top_divergence', 0.9))

        rsi = self.calc_rsi(price_data)
        if rsi > 80:
            signals.append(('rsi_overbought', 0.7))

        avg_pct = sum(s[1] for s in signals) / len(signals) if signals else 0

        return {
            'signals': signals,
            'should_take_profit': len(signals) >= 2 or avg_pct > 0.8,
            'confidence': avg_pct
        }

    def calc_rsi(self, price_data: pd.DataFrame, period: int = 14) -> float:
        """
        计算RSI
        """
        delta = price_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]

    def check_death_cross(self, price_data: pd.DataFrame) -> bool:
        """
        检查死叉
        """
        ma5 = price_data['close'].rolling(5).mean()
        ma20 = price_data['close'].rolling(20).mean()

        if len(ma5) < 2 or len(ma20) < 2:
            return False

        return ma5.iloc[-2] > ma20.iloc[-2] and ma5.iloc[-1] < ma20.iloc[-1]

    def check_top_divergence(self, price_data: pd.DataFrame) -> bool:
        """
        检查顶背离
        """
        if len(price_data) < 30:
            return False

        recent_high = price_data['high'].iloc[-30:].max()
        current_high = price_data['high'].iloc[-1]

        rsi = self.calc_rsi(price_data)

        return current_high > recent_high and rsi < 70

    def calc_partial_stop(self, entry_price: float,
                         current_price: float,
                         position_size: float) -> dict:
        """
        计算分批止损

        参数:
            entry_price: 入场价格
            current_price: 当前价格
            position_size: 持仓数量

        返回:
            partial_stop: 分批止损方案
        """
        profit_pct = (current_price - entry_price) / entry_price

        if profit_pct > 0.15:
            return {
                'action': '清仓',
                'position_to_sell': position_size,
                'reason': '盈利达到15%'
            }
        elif profit_pct > 0.10:
            return {
                'action': '卖出一半',
                'position_to_sell': position_size * 0.5,
                'reason': '盈利达到10%，锁定部分利润'
            }
        elif profit_pct > 0.05:
            return {
                'action': '止损位移动',
                'new_stop': entry_price * 1.02,
                'reason': '盈利5%，移动止损到成本价'
            }
        else:
            return {
                'action': '持有',
                'stop': entry_price * 0.97,
                'reason': '亏损3%止损'
            }
```

---

## 3. 个股风险识别量化

```python
class StockRiskIdentifier:
    """
    个股风险识别量化

    风险类型：
    - 股东减持风险
    - 业绩变脸风险
    - 主力出货风险
    - RSI超买风险
    """

    def identify_risks(self, stock_data: dict,
                      market_data: dict = None) -> list:
        """
        识别个股风险

        参数:
            stock_data: 股票数据
            market_data: 市场数据

        返回:
            risks: 风险列表
        """
        risks = []

        if self.check_major_shareholder_reduction(stock_data):
            risks.append({
                'type': '股东减持',
                'severity': 'high',
                'action': '警惕离场'
            })

        if self.is_april_risk_period():
            if self.check_earnings_warning(stock_data):
                risks.append({
                    'type': '业绩变脸',
                    'severity': 'critical',
                    'action': '回避'
                })

        if self.check_main_distribution(stock_data):
            risks.append({
                'type': '主力出货',
                'severity': 'high',
                'action': '跟随离场'
            })

        rsi = stock_data.get('rsi', 0)
        if rsi > 80:
            risks.append({
                'type': 'RSI超买',
                'severity': 'medium',
                'action': '考虑减仓'
            })

        if self.check_limit_down_risk(stock_data):
            risks.append({
                'type': '跌停风险',
                'severity': 'high',
                'action': '禁止买入'
            })

        return risks

    def check_major_shareholder_reduction(self, stock_data: dict) -> bool:
        """
        检查股东减持风险
        """
        reduction_ratio = stock_data.get('shareholder_reduction_ratio', 0)
        return reduction_ratio > 0.05

    def is_april_risk_period(self) -> bool:
        """
        是否是4月年报风险期
        """
        from datetime import datetime
        month = datetime.now().month
        return month == 4

    def check_earnings_warning(self, stock_data: dict) -> bool:
        """
        检查业绩变脸风险
        """
        earnings_change = stock_data.get('earnings_change', 0)
        return earnings_change < -0.5

    def check_main_distribution(self, stock_data: dict) -> bool:
        """
        检测主力出货
        筹码上移：低位筹码减少

        参数:
            stock_data: 股票数据

        返回:
            is_distributing: 是否在出货
        """
        low_position_ratio = stock_data.get('low_position_ratio', 1.0)
        price_change_20d = stock_data.get('price_change_20d', 0)

        return price_change_20d > 0.10 and low_position_ratio < 0.30

    def check_main_accumulation(self, stock_data: dict) -> bool:
        """
        检测主力吸筹
        筹码下移：高位筹码减少

        参数:
            stock_data: 股票数据

        返回:
            is_accumulating: 是否在吸筹
        """
        high_position_ratio = stock_data.get('high_position_ratio', 1.0)
        price_change_20d = stock_data.get('price_change_20d', 0)

        return price_change_20d < -0.10 and high_position_ratio < 0.30

    def check_limit_down_risk(self, stock_data: dict) -> bool:
        """
        检查跌停风险
        """
        change_pct = stock_data.get('change_pct', 0)
        volume_ratio = stock_data.get('volume_ratio', 1)

        return change_pct < -8 and volume_ratio > 2

    def calculate_risk_score(self, stock_data: dict,
                           market_data: dict = None) -> dict:
        """
        计算风险评分

        参数:
            stock_data: 股票数据
            market_data: 市场数据

        返回:
            risk_score: 风险评分
        """
        risks = self.identify_risks(stock_data, market_data)

        severity_weights = {'critical': 1.0, 'high': 0.7, 'medium': 0.4}

        total_risk = sum(
            severity_weights.get(r['severity'], 0.5)
            for r in risks
        )

        return {
            'risk_score': min(total_risk, 1.0),
            'risk_level': '极高' if total_risk > 0.8 else \
                         '高' if total_risk > 0.5 else \
                         '中' if total_risk > 0.3 else '低',
            'risks': risks,
            'action': self.get_risk_action(total_risk)
        }

    def get_risk_action(self, risk_score: float) -> str:
        """
        获取风险应对操作
        """
        if risk_score >= 0.8:
            return '立即清仓'
        elif risk_score >= 0.5:
            return '减仓50%'
        elif risk_score >= 0.3:
            return '谨慎持有'
        else:
            return '正常持有'
```

---

## 4. VaR风险度量

```python
class VaRCalculator:
    """
    VaR风险价值计算

    VaR: 在给定置信水平下，组合在特定时间内可能遭受的最大损失
    """

    def __init__(self):
        self.confidence_levels = [0.95, 0.99]

    def calculate_var_historical(self, returns: pd.Series,
                                confidence: float = 0.95,
                                time_horizon: int = 1) -> float:
        """
        历史模拟法计算VaR

        参数:
            returns: 收益率序列
            confidence: 置信水平
            time_horizon: 时间跨度

        返回:
            var: VaR值
        """
        percentile = (1 - confidence) * 100

        var = returns.quantile(1 - confidence)

        return var * np.sqrt(time_horizon)

    def calculate_var_parametric(self, returns: pd.Series,
                               confidence: float = 0.95,
                               time_horizon: int = 1) -> float:
        """
        参数法计算VaR

        假设收益率服从正态分布

        参数:
            returns: 收益率序列
            confidence: 置信水平
            time_horizon: 时间跨度

        返回:
            var: VaR值
        """
        from scipy import stats

        mean = returns.mean()
        std = returns.std()

        z_score = stats.norm.ppf(1 - confidence)

        var = mean - z_score * std

        return var * np.sqrt(time_horizon)

    def calculate_cvar(self, returns: pd.Series,
                       confidence: float = 0.95) -> float:
        """
        计算CVaR（条件风险价值）

        CVaR: 超过VaR的平均损失

        参数:
            returns: 收益率序列
            confidence: 置信水平

        返回:
            cvar: CVaR值
        """
        var = self.calculate_var_historical(returns, confidence)

        tail_returns = returns[returns <= var]

        if len(tail_returns) == 0:
            return var

        return tail_returns.mean()

    def calculate_portfolio_var(self, weights: np.ndarray,
                              cov_matrix: np.ndarray,
                              mean_returns: np.ndarray,
                              confidence: float = 0.95) -> dict:
        """
        计算组合VaR

        参数:
            weights: 权重向量
            cov_matrix: 协方差矩阵
            mean_returns: 平均收益率
            confidence: 置信水平

        返回:
            portfolio_var: 组合VaR
        """
        from scipy import stats

        portfolio_return = np.dot(weights, mean_returns)
        portfolio_std = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))

        z_score = stats.norm.ppf(1 - confidence)

        var = portfolio_return - z_score * portfolio_std

        return {
            'var_95': var,
            'portfolio_std': portfolio_std,
            'z_score': z_score
        }
```

---

## 5. 尾部风险对冲

```python
class TailRiskHedger:
    """
    尾部风险对冲

    方法：
    - 买入看跌期权
    - 卖出期货
    - 持有黄金/国债
    """

    def __init__(self):
        self.hedge_instruments = {
            'put_option': {'cost': '期权费', 'protection': '下行保护'},
            'short_future': {'cost': '无', 'protection': '有限'},
            'gold': {'cost': '机会成本', 'protection': '避险'}
        }

    def calc_hedge_ratio(self, portfolio_value: float,
                        option_strike: float,
                        option_price: float,
                        beta: float = 1.0) -> dict:
        """
        计算对冲比率

        参数:
            portfolio_value: 组合价值
            option_strike: 期权执行价
            option_price: 期权价格
            beta: 组合Beta

        返回:
            hedge_ratio: 对冲方案
        """
        notional_exposure = portfolio_value * beta

        hedge_ratio = notional_exposure / option_strike

        option_value_if_exercised = max(0, option_strike - option_strike)

        net_protection = option_value_if_exercised - option_price * hedge_ratio

        return {
            'hedge_ratio': hedge_ratio,
            'option_cost': option_price * hedge_ratio * portfolio_value,
            'net_protection': net_protection,
            'cost_per_unit': option_price
        }

    def select_hedge_strategy(self, risk_budget: float,
                            market_volatility: float) -> dict:
        """
        选择对冲策略

        参数:
            risk_budget: 风险预算
            market_volatility: 市场波动率

        返回:
            strategy: 对冲策略
        """
        if market_volatility > 0.30:
            return {
                'strategy': '积极对冲',
                'allocation': {'put_options': 0.10, 'gold': 0.05},
                'cost': '较高'
            }
        elif market_volatility > 0.15:
            return {
                'strategy': '选择性对冲',
                'allocation': {'put_options': 0.05, 'gold': 0.02},
                'cost': '中等'
            }
        else:
            return {
                'strategy': '不对冲',
                'allocation': {'cash': 0.05},
                'cost': '最低'
            }

    def rebalance_hedge(self, current_hedge: dict,
                       market_data: dict,
                       target_var: float) -> dict:
        """
        再平衡对冲

        参数:
            current_hedge: 当前对冲
            market_data: 市场数据
            target_var: 目标VaR

        返回:
            rebalance: 再平衡建议
        """
        current_var = market_data.get('current_var', 0)

        if current_var > target_var * 1.2:
            return {
                'action': '增加对冲',
                'increase_ratio': 0.20,
                'reason': 'VaR超过目标20%'
            }
        elif current_var < target_var * 0.5:
            return {
                'action': '减少对冲',
                'decrease_ratio': 0.30,
                'reason': 'VaR远低于目标'
            }

        return {
            'action': '维持不变',
            'reason': 'VaR在可接受范围'
        }
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合附录AX：风险控制量化体系 |
