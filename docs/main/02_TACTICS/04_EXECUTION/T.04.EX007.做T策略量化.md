# T.04.EX007.做T策略量化

> 日内回转交易（T+0）策略量化
>
> **策略编号**：T.04.EX007
> **所属模块**：04_EXECUTION
> **文档类型**：执行策略
> **优先级**：P2
>
> **配套文档**：
> - [T.04.EX006.A股交易规则.md](./T.04.EX006.A股交易规则.md) - T+1规则
> - [T.04.EX005.开盘竞价信号.md](./T.04.EX005.开盘竞价信号.md) - 开盘信号

---

## 1. 做T策略概述

```python
class IntradayTradingStrategy:
    """
    日内回转交易（做T）策略

    适用场景:
    - 持有底仓的情况下，当日进行买卖套利
    - 利用T+0品种（ETF、可转债、期权）进行当日买卖
    - 融券账户进行日内回转

    策略类型:
    1. 正向做T: 先买后卖，适合震荡上行
    2. 反向做T: 先卖后买，适合震荡下行
    3. 锁利做T: 涨停打开时卖出，回调时买回
    """

    def __init__(self):
        self.strategy_params = {
            '正T_买入比例': 0.50,
            '反T_卖出比例': 0.50,
            '止盈阈值': 0.015,
            '止损阈值': 0.008,
            '最大持仓时间': 240,
            '回调买入深度': 0.01
        }
```

---

## 2. 正向做T（先买后卖）

```python
class PositiveT_Strategy:
    """
    正向做T策略
    先买入部分仓位，当日高价卖出同等数量

    适用场景:
    - 震荡上行行情
    - 早盘低开后企稳
    - 回调至支撑位时买入
    """

    def __init__(self):
        self.params = {
            'buy_ratio': 0.50,
            'profit_target': 0.015,
            'stop_loss': 0.008,
            'max_hold_minutes': 180
        }

    def generate_signals(self, minute_data: pd.DataFrame,
                        position: dict) -> list:
        """
        生成正向做T信号

        参数:
            minute_data: 分钟线数据
            position: 当前持仓信息
                - avg_cost: 持仓成本
                - volume: 持仓数量
                - current_price: 当前价

        返回:
            signals: 操作信号列表
        """
        signals = []

        current_price = minute_data['close'].iloc[-1]
        avg_cost = position['avg_cost']
        hold_volume = position['volume']

        if not self._should_buy(avg_cost, current_price, minute_data):
            return signals

        buy_volume = int(hold_volume * self.params['buy_ratio'])

        signals.append({
            'action': 'buy',
            'volume': buy_volume,
            'price': current_price,
            'reason': '正向做T买入',
            'target_sell_price': current_price * (1 + self.params['profit_target']),
            'stop_loss_price': current_price * (1 - self.params['stop_loss'])
        })

        return signals

    def _should_buy(self, avg_cost: float, current_price: float,
                   minute_data: pd.DataFrame) -> bool:
        """
        判断是否应该买入
        """
        if current_price < avg_cost * 0.99:
            return True

        ma5 = minute_data['close'].rolling(5).mean().iloc[-1]
        ma10 = minute_data['close'].rolling(10).mean().iloc[-1]

        if current_price > ma5 and current_price > ma10:
            return False

        volume = minute_data['volume'].iloc[-1]
        avg_vol = minute_data['volume'].rolling(20).mean().iloc[-1]

        if volume < avg_vol * 0.5:
            return True

        return False

    def should_sell(self, buy_price: float, current_price: float,
                   hold_minutes: int) -> dict:
        """
        判断是否应该卖出

        返回:
            decision: {'should_sell': bool, 'reason': str}
        """
        profit_pct = (current_price - buy_price) / buy_price

        if profit_pct >= self.params['profit_target']:
            return {
                'should_sell': True,
                'reason': '达到止盈目标',
                'profit_pct': profit_pct
            }

        if profit_pct <= -self.params['stop_loss']:
            return {
                'should_sell': True,
                'reason': '触发止损',
                'profit_pct': profit_pct
            }

        if hold_minutes >= self.params['max_hold_minutes']:
            if profit_pct > 0:
                return {
                    'should_sell': True,
                    'reason': '时间到期且盈利',
                    'profit_pct': profit_pct
                }
            else:
                return {
                    'should_sell': True,
                    'reason': '时间到期，强制平仓',
                    'profit_pct': profit_pct
                }

        return {'should_sell': False, 'reason': None, 'profit_pct': profit_pct}
```

---

## 3. 反向做T（先卖后买）

```python
class ReverseT_Strategy:
    """
    反向做T策略
    先卖出部分仓位，当日低价买回同等数量

    适用场景:
    - 震荡下行行情
    - 早盘高开后回落
    - 反弹至压力位时卖出
    """

    def __init__(self):
        self.params = {
            'sell_ratio': 0.50,
            'profit_target': 0.015,
            'stop_loss': 0.010,
            'max_hold_minutes': 180,
            'buy_back_depth': 0.01
        }

    def generate_signals(self, minute_data: pd.DataFrame,
                        position: dict) -> list:
        """
        生成反向做T信号

        参数:
            minute_data: 分钟线数据
            position: 持仓信息

        返回:
            signals: 操作信号列表
        """
        signals = []

        current_price = minute_data['close'].iloc[-1]
        avg_cost = position['avg_cost']
        hold_volume = position['volume']

        if not self._should_sell(avg_cost, current_price, minute_data):
            return signals

        sell_volume = int(hold_volume * self.params['sell_ratio'])

        signals.append({
            'action': 'sell',
            'volume': sell_volume,
            'price': current_price,
            'reason': '反向做T卖出',
            'target_buy_price': current_price * (1 - self.params['profit_target']),
            'stop_buy_price': current_price * (1 + self.params['stop_loss'])
        })

        return signals

    def _should_sell(self, avg_cost: float, current_price: float,
                   minute_data: pd.DataFrame) -> bool:
        """
        判断是否应该卖出
        """
        if current_price > avg_cost * 1.02:
            return True

        ma5 = minute_data['close'].rolling(5).mean().iloc[-1]
        ma10 = minute_data['close'].rolling(10).mean().iloc[-1]

        if current_price < ma5 and current_price < ma10:
            return True

        volume = minute_data['volume'].iloc[-1]
        avg_vol = minute_data['volume'].rolling(20).mean().iloc[-1]

        if volume > avg_vol * 1.5:
            return True

        return False

    def should_buy_back(self, sell_price: float, current_price: float,
                      hold_minutes: int) -> dict:
        """
        判断是否应该买回

        返回:
            decision: {'should_buy': bool, 'reason': str}
        """
        discount_pct = (sell_price - current_price) / sell_price

        if discount_pct >= self.params['profit_target']:
            return {
                'should_buy': True,
                'reason': '达到买回目标',
                'discount_pct': discount_pct
            }

        if discount_pct <= -self.params['stop_loss']:
            return {
                'should_buy': True,
                'reason': '触发止损被迫买回',
                'discount_pct': discount_pct
            }

        if hold_minutes >= self.params['max_hold_minutes']:
            return {
                'should_buy': True,
                'reason': '时间到期，强制买回',
                'discount_pct': discount_pct
            }

        return {'should_buy': False, 'reason': None, 'discount_pct': discount_pct}
```

---

## 4. 锁利做T策略

```python
class LockProfitT_Strategy:
    """
    锁利做T策略

    适用场景:
    - 持仓个股涨停后打开
    - 重大利好兑现
    - 股价在涨停价附近反复打开

    策略逻辑:
    - 涨停打开时卖出部分持仓
    - 回调时买回同等数量
    - 若继续涨停则持有不动
    """

    def __init__(self):
        self.params = {
            'sell_ratio': 0.30,
            'rebuy_depth': 0.03,
            'limit_up_open_threshold': 0.09,
            'trailing_stop': 0.005
        }

    def detect_limit_up_open(self, minute_data: pd.DataFrame,
                            pre_close: float) -> dict:
        """
        检测涨停打开

        参数:
            minute_data: 分钟数据
            pre_close: 昨收价

        返回:
            status: {'is_open': bool, 'details': dict}
        """
        current_price = minute_data['close'].iloc[-1]
        high_price = minute_data['high'].iloc[-1]
        limit_up_price = pre_close * 1.10

        reached_limit = high_price >= limit_up_price
        is_open = reached_limit and current_price < limit_up_price * 0.995

        return {
            'is_limit_up_reached': reached_limit,
            'is_limit_up_open': is_open,
            'limit_up_price': limit_up_price,
            'current_price': current_price,
            'open_depth': (limit_up_price - current_price) / limit_up_price if is_open else 0
        }

    def should_sell_on_limit_open(self, limit_status: dict,
                                  position: dict) -> dict:
        """
        判断涨停打开时是否卖出

        参数:
            limit_status: 涨停状态
            position: 持仓

        返回:
            decision: 卖出决策
        """
        if not limit_status['is_limit_up_open']:
            return {'should_sell': False, 'reason': '未涨停打开'}

        open_depth = limit_status['open_depth']
        hold_days = position.get('hold_days', 0)

        if open_depth >= 0.02:
            return {
                'should_sell': True,
                'sell_ratio': self.params['sell_ratio'] * 1.5,
                'reason': '深度打开，卖出避险',
                'risk_level': 'high'
            }

        if hold_days < 3:
            return {
                'should_sell': True,
                'sell_ratio': self.params['sell_ratio'],
                'reason': '新持股，锁定利润',
                'risk_level': 'medium'
            }

        return {
            'should_sell': True,
            'sell_ratio': self.params['sell_ratio'],
            'reason': '涨停打开，锁利卖出',
            'risk_level': 'medium'
        }

    def should_buy_on_pullback(self, current_price: float,
                              sell_price: float) -> dict:
        """
        判断回调时是否买回

        参数:
            current_price: 当前价格
            sell_price: 卖出价格

        返回:
            decision: 买回决策
        """
        pullback_depth = (sell_price - current_price) / sell_price

        if pullback_depth >= self.params['rebuy_depth']:
            return {
                'should_buy': True,
                'buy_ratio': 1.0,
                'reason': '回调到位，买回持仓',
                'pullback_depth': pullback_depth
            }

        trailing_stop = self.params['trailing_stop']
        if current_price > sell_price * (1 + trailing_stop):
            return {
                'should_buy': True,
                'buy_ratio': 1.0,
                'reason': '价格回升，突破卖出价，追买',
                'pullback_depth': -trailing_stop
            }

        return {
            'should_buy': False,
            'reason': '回调深度不足',
            'pullback_depth': pullback_depth
        }
```

---

## 5. 做T执行管理器

```python
class IntradayTradingManager:
    """
    日内交易管理器
    统一管理正向做T、反向做T、锁利做T
    """

    def __init__(self, capital: float = 1000000):
        self.capital = capital
        self.positive_t = PositiveT_Strategy()
        self.reverse_t = ReverseT_Strategy()
        self.lock_profit_t = LockProfitT_Strategy()
        self.position_tracker = {}
        self.daily_t_profit = 0

    def run_intraday_strategy(self, stock_code: str,
                            minute_data: pd.DataFrame,
                            position: dict,
                            market_regime: str) -> dict:
        """
        运行日内策略

        参数:
            stock_code: 股票代码
            minute_data: 分钟数据
            position: 持仓信息
            market_regime: 市场状态 ('bull', 'bear', '震荡')

        返回:
            result: 执行结果
        """
        signals = []

        if market_regime == '震荡上行':
            signals.extend(self.positive_t.generate_signals(minute_data, position))
        elif market_regime == '震荡下行':
            signals.extend(self.reverse_t.generate_signals(minute_data, position))
        elif market_regime == '高位震荡':
            signals.extend(self.lock_profit_t.detect_limit_up_open(
                minute_data, position.get('pre_close', position['avg_cost'])
            ))

        executed_signals = self.execute_signals(signals)

        self.update_position_tracker(executed_signals)

        return {
            'signals_generated': len(signals),
            'signals_executed': len(executed_signals),
            'executed_signals': executed_signals,
            'daily_t_profit': self.daily_t_profit,
            'position_tracker': self.position_tracker
        }

    def execute_signals(self, signals: list) -> list:
        """
        执行信号

        参数:
            signals: 信号列表

        返回:
            executed: 已执行信号
        """
        executed = []

        for signal in signals:
            if self._validate_signal(signal):
                executed.append({
                    **signal,
                    'executed': True,
                    'execution_time': self._get_current_time()
                })

                if signal['action'] == 'buy':
                    self.daily_t_profit -= signal['volume'] * signal['price']
                elif signal['action'] == 'sell':
                    self.daily_t_profit += signal['volume'] * signal['price']

        return executed

    def _validate_signal(self, signal: dict) -> bool:
        """
        验证信号有效性
        """
        if signal['volume'] <= 0:
            return False

        if signal['price'] <= 0:
            return False

        return True

    def _get_current_time(self) -> str:
        """
        获取当前时间
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def update_position_tracker(self, executed_signals: list):
        """
        更新持仓追踪器
        """
        for signal in executed_signals:
            code = signal.get('stock_code')
            if code not in self.position_tracker:
                self.position_tracker[code] = {
                    'volume': 0,
                    'avg_cost': 0,
                    't_positions': []
                }

            pt = self.position_tracker[code]

            if signal['action'] == 'buy':
                total_cost = pt['avg_cost'] * pt['volume'] + signal['volume'] * signal['price']
                pt['volume'] += signal['volume']
                pt['avg_cost'] = total_cost / pt['volume'] if pt['volume'] > 0 else 0
                pt['t_positions'].append({
                    'action': 'buy',
                    'volume': signal['volume'],
                    'price': signal['price']
                })
            elif signal['action'] == 'sell':
                pt['volume'] -= signal['volume']
                pt['t_positions'].append({
                    'action': 'sell',
                    'volume': signal['volume'],
                    'price': signal['price']
                })

    def calculate_daily_t_profit(self) -> dict:
        """
        计算当日做T收益
        """
        total_profit = self.daily_t_profit

        buy_count = 0
        sell_count = 0
        for code, pt in self.position_tracker.items():
            for t_pos in pt['t_positions']:
                if t_pos['action'] == 'buy':
                    buy_count += 1
                else:
                    sell_count += 1

        return {
            'total_t_profit': round(total_profit, 2),
            'profit_rate': round(total_profit / self.capital * 100, 3),
            'buy_count': buy_count,
            'sell_count': sell_count,
            'net_profit_per_trade': round(total_profit / max(buy_count + sell_count, 1), 2)
        }
```

---

## 6. 做T风险控制

```python
class IntradayRiskControl:
    """
    日内交易风控
    """

    def __init__(self):
        self.limits = {
            '单日最大T次数': 3,
            '单次最大T比例': 0.50,
            '单日最大亏损': 0.02,
            '禁止做T条件': ['一字板', '停牌', '流动性枯竭']
        }

    def check_t_permission(self, stock_data: dict,
                          today_t_count: int) -> dict:
        """
        检查是否允许做T

        参数:
            stock_data: 股票数据
            today_t_count: 今日做T次数

        返回:
            permission: 权限检查结果
        """
        if today_t_count >= self.limits['单日最大T次数']:
            return {
                'allowed': False,
                'reason': f'今日做T次数已达上限({self.limits["单日最大T次数"]}次)'
            }

        if stock_data.get('is_limit_up', False):
            return {
                'allowed': False,
                'reason': '涨停股不做T'
            }

        if stock_data.get('is_limit_down', False):
            return {
                'allowed': False,
                'reason': '跌停股不做T'
            }

        if stock_data.get('is_suspended', False):
            return {
                'allowed': False,
                'reason': '停牌股票不做T'
            }

        turnover = stock_data.get('turnover_rate', 0)
        if turnover < 0.5:
            return {
                'allowed': False,
                'reason': '流动性不足，不宜做T'
            }

        return {'allowed': True, 'reason': '检查通过'}

    def calculate_t_risk(self, position: dict, t_price: float,
                        action: str) -> dict:
        """
        计算做T风险

        参数:
            position: 持仓
            t_price: 做T价格
            action: 'buy' or 'sell'

        返回:
            risk: 风险评估
        """
        avg_cost = position['avg_cost']
        current_price = position.get('current_price', t_price)

        if action == 'buy':
            potential_loss = (current_price - t_price) * position['volume']
            risk_pct = abs(potential_loss) / (avg_cost * position['volume'])

            return {
                'risk_type': '买入风险',
                'potential_loss': potential_loss,
                'risk_pct': risk_pct,
                'risk_level': self._get_risk_level(risk_pct)
            }
        else:
            potential_miss = (t_price - current_price) * position['volume']
            risk_pct = abs(potential_miss) / (avg_cost * position['volume'])

            return {
                'risk_type': '卖出风险',
                'potential_miss': potential_miss,
                'risk_pct': risk_pct,
                'risk_level': self._get_risk_level(risk_pct)
            }

    def _get_risk_level(self, risk_pct: float) -> str:
        """
        风险等级评估
        """
        if risk_pct < 0.005:
            return '低'
        elif risk_pct < 0.01:
            return '中'
        else:
            return '高'
```

---

## 7. 使用示例

```python
def example_intraday_trading():
    """
    日内交易示例
    """
    manager = IntradayTradingManager(capital=1000000)
    risk_control = IntradayRiskControl()

    position = {
        'stock_code': '000001',
        'avg_cost': 12.50,
        'volume': 10000,
        'current_price': 12.60,
        'pre_close': 12.45,
        'hold_days': 5
    }

    minute_data = pd.read_csv('minute_data.csv')

    market_regime = '震荡上行'

    check = risk_control.check_t_permission(
        {'turnover_rate': 2.5, 'is_limit_up': False},
        today_t_count=0
    )

    if check['allowed']:
        result = manager.run_intraday_strategy(
            '000001',
            minute_data,
            position,
            market_regime
        )

        print(f"生成信号: {result['signals_generated']}")
        print(f"执行信号: {result['signals_executed']}")
        print(f"做T收益: {result['daily_t_profit']:.2f}")

    profit_summary = manager.calculate_daily_t_profit()
    print(f"当日做T总结: {profit_summary}")
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 新建做T策略量化文档 |
