# T.04.EX006.A股交易规则

> A股市场交易制度量化体系
>
> **策略编号**：T.04.EX006
> **所属模块**：04_EXECUTION
> **文档类型**：交易规则
> **优先级**：P1
>
> **配套文档**：
> - [T.04.EX005.开盘竞价信号.md](./T.04.EX005.开盘竞价信号.md) - 竞价信号
> - [T.04.EX007.做T策略量化.md](./T.04.EX007.做T策略量化.md) - 日内回转交易

---

## 1. T+1交易制度

```python
class T1TradingSystem:
    """
    T+1交易制度量化
    A股当天买入，第二天才能卖出
    """

    T1_RULES = {
        '当日买入锁定': True,
        '次日解除限制': True,
        '适用范围': 'A股市场所有品种',
        '例外情况': ['ETF基金', '可转债', '期权', '货币基金']
    }

    def __init__(self):
        self.position_tracker = {}
        self.trading_calendar = self._load_trading_calendar()

    def check_sell_permission(self, stock_code: str, buy_date: str,
                             current_date: str) -> dict:
        """
        检查卖出权限

        参数:
            stock_code: 股票代码
            buy_date: 买入日期
            current_date: 当前日期

        返回:
            permission: 卖出权限信息
        """
        if buy_date == current_date:
            next_trading_day = self.get_next_trading_day(buy_date)
            return {
                'can_sell': False,
                'reason': 'T+1制度：当日买入不能卖出',
                'available_date': next_trading_day,
                'days_waiting': self._calc_trading_days(buy_date, current_date)
            }
        return {'can_sell': True, 'reason': 'T+1限制已解除'}

    def get_next_trading_day(self, current_date: str) -> str:
        """
        获取下一个交易日
        """
        idx = self.trading_calendar.index(current_date)
        if idx + 1 < len(self.trading_calendar):
            return self.trading_calendar[idx + 1]
        return None

    def calc_available_position(self, stock_code: str, total_position: float,
                               buy_date: str, current_date: str) -> float:
        """
        计算可用持仓

        参数:
            stock_code: 股票代码
            total_position: 总持仓
            buy_date: 买入日期
            current_date: 当前日期

        返回:
            available_position: 可用持仓
        """
        if self.check_sell_permission(stock_code, buy_date, current_date)['can_sell']:
            return total_position
        return 0.0

    def calc_margin_impact(self, position: float, margin_ratio: float = 0.25) -> dict:
        """
        计算保证金影响
        T+1限制了当日对冲能力
        """
        locked_margin = position * margin_ratio
        market_rate = 0.03
        opportunity_cost = locked_margin * market_rate / 365

        return {
            'locked_margin': locked_margin,
            'daily_opportunity_cost': opportunity_cost,
            'recommendation': '避免当日大幅加仓',
            'max_intraday_addition': position * 0.5
        }

    def _load_trading_calendar(self) -> list:
        """
        加载交易日历（简化版）
        实际应从数据源获取
        """
        return []

    def _calc_trading_days(self, start_date: str, end_date: str) -> int:
        """
        计算交易日天数
        """
        start_idx = self.trading_calendar.index(start_date)
        end_idx = self.trading_calendar.index(end_date)
        return max(0, end_idx - start_idx)
```

---

## 2. 涨跌停板制度

```python
class LimitUpDownSystem:
    """
    涨跌停板制度量化
    """

    LIMIT_RULES = {
        '主板_沪市': {
            'stock_code_prefix': '60',
            'limit_rate': 0.10,
            'st_rate': 0.05,
            'new_listing_rate': 0.44,
            'new_listing_days': 5
        },
        '主板_深市': {
            'stock_code_prefix': '000',
            'limit_rate': 0.10,
            'st_rate': 0.05,
            'new_listing_rate': 0.44,
            'new_listing_days': 5
        },
        '创业板': {
            'stock_code_prefix': '300',
            'limit_rate': 0.20,
            'st_rate': 0.20,
            'new_listing_rate': 0.44,
            'new_listing_days': 5
        },
        '科创板': {
            'stock_code_prefix': '688',
            'limit_rate': 0.20,
            'st_rate': 0.20,
            'new_listing_rate': None,
            'new_listing_days': 0
        },
        'ST股票': {
            'rule': '特别处理',
            'limit_rate': 0.05,
            'applicable': ['ST', '*ST', 'SST', 'S*ST']
        }
    }

    def __init__(self):
        self.cache = {}

    def get_limit_rate(self, stock_code: str, is_st: bool = False,
                      listing_days: int = 999) -> float:
        """
        获取涨跌停幅度

        参数:
            stock_code: 股票代码
            is_st: 是否ST股票
            listing_days: 上市天数

        返回:
            limit_rate: 涨跌停幅度
        """
        prefix = self._get_code_prefix(stock_code)

        rules = self.LIMIT_RULES

        if prefix == '688':
            return 0.20
        elif prefix == '300':
            return 0.20
        elif prefix in ['60', '000']:
            if listing_days <= rules['主板_沪市']['new_listing_days']:
                return 0.44
            return 0.05 if is_st else 0.10

        return 0.10

    def calc_limit_price(self, pre_close: float, stock_code: str,
                        is_st: bool = False, listing_days: int = 999) -> dict:
        """
        计算涨跌停价格

        参数:
            pre_close: 昨收价
            stock_code: 股票代码
            is_st: 是否ST

        返回:
            limit_prices: 涨跌停价格
        """
        limit_rate = self.get_limit_rate(stock_code, is_st, listing_days)

        return {
            'pre_close': pre_close,
            'limit_up_price': round(pre_close * (1 + limit_rate), 2),
            'limit_down_price': round(pre_close * (1 - limit_rate), 2),
            'limit_rate': limit_rate,
            'up_pct': limit_rate * 100,
            'down_pct': -limit_rate * 100
        }

    def check_limit_status(self, current_price: float, pre_close: float,
                          stock_code: str, is_st: bool = False) -> dict:
        """
        检查涨跌停状态

        参数:
            current_price: 当前价格
            pre_close: 昨收价
            stock_code: 股票代码
            is_st: 是否ST

        返回:
            status: 涨跌停状态
        """
        limit_prices = self.calc_limit_price(pre_close, stock_code, is_st)

        change_pct = (current_price - pre_close) / pre_close * 100

        if current_price >= limit_prices['limit_up_price']:
            return {
                'status': '涨停',
                'is_limit_up': True,
                'is_limit_down': False,
                'change_pct': change_pct,
                'limit_price': limit_prices['limit_up_price']
            }
        elif current_price <= limit_prices['limit_down_price']:
            return {
                'status': '跌停',
                'is_limit_up': False,
                'is_limit_down': True,
                'change_pct': change_pct,
                'limit_price': limit_prices['limit_down_price']
            }
        else:
            return {
                'status': '正常',
                'is_limit_up': False,
                'is_limit_down': False,
                'change_pct': change_pct,
                'limit_up_price': limit_prices['limit_up_price'],
                'limit_down_price': limit_prices['limit_down_price']
            }

    def is_buyable(self, auction: dict, limit_status: dict) -> dict:
        """
        判断涨停股是否可买入

        参数:
            auction: 竞价数据
            limit_status: 涨跌停状态

        返回:
            buyable: 是否可买入
        """
        if limit_status['is_limit_up']:
            auction_change = auction.get('change_pct', 0)
            if auction_change >= 9.8:
                return {
                    'buyable': False,
                    'reason': '一字涨停，买入通道关闭'
                }
            return {
                'buyable': True,
                'reason': '非一字涨停，可排队买入'
            }
        return {'buyable': True, 'reason': '未涨停'}

    def _get_code_prefix(self, stock_code: str) -> str:
        """
        获取股票代码前缀
        """
        if stock_code.startswith('688'):
            return '688'
        elif stock_code.startswith('300'):
            return '300'
        elif stock_code.startswith('60'):
            return '60'
        elif stock_code.startswith('000'):
            return '000'
        elif stock_code.startswith('002'):
            return '002'
        return 'other'
```

---

## 3. 交易费用计算

```python
class TradingFeeCalculator:
    """
    A股交易费用计算器

    费用组成:
    1. 佣金: 双向收费，最低5元
    2. 印花税: 卖出时收取，1‰
    3. 过户费: 沪市双向收取，0.01‰
    4. 规费: 双向收取，0.02‰
    """

    FEE_RATES = {
        'commission': {'rate': 0.0003, 'min': 5, 'double': True},
        'stamp_tax': {'rate': 0.001, 'min': 0, 'double': False, 'sell_only': True},
        'transfer_fee': {'rate': 0.00001, 'min': 1, 'double': True, 'market': 'SH'},
        'regulatory_fee': {'rate': 0.00002, 'min': 0, 'double': True}
    }

    def __init__(self, commission_rate: float = 0.0003,
                 min_commission: float = 5.0):
        self.commission_rate = commission_rate
        self.min_commission = min_commission

    def calc_buy_fees(self, stock_code: str, price: float, volume: int) -> dict:
        """
        计算买入费用

        参数:
            stock_code: 股票代码
            price: 买入价格
            volume: 买入数量

        返回:
            fees: 费用明细
        """
        amount = price * volume

        commission = max(amount * self.commission_rate, self.min_commission)

        transfer_fee = 0
        if stock_code.startswith('6'):
            transfer_fee = max(amount * 0.00001, 1)

        regulatory_fee = amount * 0.00002

        total_fees = commission + transfer_fee + regulatory_fee

        return {
            'stock_code': stock_code,
            'price': price,
            'volume': volume,
            'amount': amount,
            'commission': round(commission, 2),
            'transfer_fee': round(transfer_fee, 2),
            'regulatory_fee': round(regulatory_fee, 2),
            'total_fees': round(total_fees, 2),
            'cost_per_share': round((amount + total_fees) / volume, 4)
        }

    def calc_sell_fees(self, stock_code: str, price: float, volume: int) -> dict:
        """
        计算卖出费用

        参数:
            stock_code: 股票代码
            price: 卖出价格
            volume: 卖出数量

        返回:
            fees: 费用明细
        """
        amount = price * volume

        commission = max(amount * self.commission_rate, self.min_commission)

        stamp_tax = amount * 0.001

        transfer_fee = 0
        if stock_code.startswith('6'):
            transfer_fee = max(amount * 0.00001, 1)

        regulatory_fee = amount * 0.00002

        total_fees = commission + stamp_tax + transfer_fee + regulatory_fee

        net_amount = amount - total_fees

        return {
            'stock_code': stock_code,
            'price': price,
            'volume': volume,
            'amount': amount,
            'commission': round(commission, 2),
            'stamp_tax': round(stamp_tax, 2),
            'transfer_fee': round(transfer_fee, 2),
            'regulatory_fee': round(regulatory_fee, 2),
            'total_fees': round(total_fees, 2),
            'net_amount': round(net_amount, 2),
            'net_per_share': round(net_amount / volume, 4)
        }

    def calc_round_trip_fees(self, stock_code: str, buy_price: float,
                            sell_price: float, volume: int) -> dict:
        """
        计算往返费用（买入+卖出）

        参数:
            stock_code: 股票代码
            buy_price: 买入价格
            sell_price: 卖出价格
            volume: 交易数量

        返回:
            round_trip: 往返费用
        """
        buy_fees = self.calc_buy_fees(stock_code, buy_price, volume)
        sell_fees = self.calc_sell_fees(stock_code, sell_price, volume)

        total_fees = buy_fees['total_fees'] + sell_fees['total_fees']
        gross_profit = (sell_price - buy_price) * volume
        net_profit = gross_profit - total_fees

        breakeven_pct = total_fees / (buy_price * volume) * 100
        profit_pct = net_profit / (buy_price * volume) * 100

        return {
            'buy_details': buy_fees,
            'sell_details': sell_fees,
            'total_fees': round(total_fees, 2),
            'gross_profit': round(gross_profit, 2),
            'net_profit': round(net_profit, 2),
            'breakeven_change_pct': round(breakeven_pct, 3),
            'net_profit_pct': round(profit_pct, 3)
        }

    def calc_min_profitable_price(self, buy_price: float, volume: int = 100) -> float:
        """
        计算最小盈利价格（覆盖交易费用）

        参数:
            buy_price: 买入价格
            volume: 交易数量

        返回:
            min_sell_price: 最小卖出价格
        """
        buy_amount = buy_price * volume
        buy_fees = self.calc_buy_fees('000001', buy_price, volume)

        min_profit = buy_fees['total_fees'] + buy_fees['total_fees'] * 0.5

        min_sell_price = (buy_amount + min_profit) / volume

        return round(min_sell_price, 2)
```

---

## 4. 仓位管理规则

```python
class PositionManagementRules:
    """
    A股仓位管理规则
    """

    POSITION_LIMITS = {
        '单票上限': 0.20,
        '单行业上限': 0.30,
        '创业板持仓上限': 0.40,
        '科创板持仓上限': 0.30,
        'ST持仓上限': 0.05,
        '涨跌停持仓规则': {
            '涨停卖出条件': '持仓>10%且盈利>5%',
            '跌停止损条件': '亏损>7%'
        }
    }

    def check_position_limit(self, stock_code: str, target_position: float,
                           current_positions: dict, total_capital: float) -> dict:
        """
        检查仓位限制

        参数:
            stock_code: 股票代码
            target_position: 目标仓位
            current_positions: 当前持仓
            total_capital: 总资金

        返回:
            check_result: 检查结果
        """
        position_value = target_position * total_capital

        prefix = self._get_code_prefix(stock_code)
        if prefix == '688' and target_position > self.POSITION_LIMITS['科创板持仓上限']:
            return {
                'approved': False,
                'reason': f'科创板持仓超限，最大{self.POSITION_LIMITS["科创板持仓上限"]*100}%',
                'adjusted_position': self.POSITION_LIMITS['科创板持仓上限']
            }

        if prefix == '300' and target_position > self.POSITION_LIMITS['创业板持仓上限']:
            return {
                'approved': False,
                'reason': f'创业板持仓超限，最大{self.POSITION_LIMITS["创业板持仓上限"]*100}%',
                'adjusted_position': self.POSITION_LIMITS['创业板持仓上限']
            }

        if target_position > self.POSITION_LIMITS['单票上限']:
            return {
                'approved': False,
                'reason': f'单票持仓超限，最大{self.POSITION_LIMITS["单票上限"]*100}%',
                'adjusted_position': self.POSITION_LIMITS['单票上限']
            }

        industry = self._get_industry(stock_code)
        industry_position = current_positions.get(industry, 0)
        if industry_position + target_position > self.POSITION_LIMITS['单行业上限']:
            available = self.POSITION_LIMITS['单行业上限'] - industry_position
            return {
                'approved': False,
                'reason': f'{industry}行业持仓超限',
                'adjusted_position': max(0, available)
            }

        return {
            'approved': True,
            'reason': '仓位检查通过',
            'adjusted_position': target_position
        }

    def calc_stop_loss(self, buy_price: float, limit_status: dict = None) -> dict:
        """
        计算止损位

        参数:
            buy_price: 买入价格
            limit_status: 涨跌停状态

        返回:
            stop_loss: 止损信息
        """
        normal_stop = buy_price * 0.93

        if limit_status and limit_status.get('is_limit_down'):
            return {
                'stop_loss_price': buy_price * 0.90,
                'stop_loss_pct': -0.10,
                'immediate_action': True,
                'reason': '跌停时扩大止损范围'
            }

        return {
            'stop_loss_price': normal_stop,
            'stop_loss_pct': -0.07,
            'immediate_action': False,
            'reason': '标准7%止损'
        }

    def _get_code_prefix(self, stock_code: str) -> str:
        if stock_code.startswith('688'):
            return '688'
        elif stock_code.startswith('300'):
            return '300'
        return 'main'

    def _get_industry(self, stock_code: str) -> str:
        return 'default'
```

---

## 5. 交易时间规则

```python
class TradingTimeRules:
    """
    A股交易时间规则
    """

    TRADING_SCHEDULE = {
        '早盘集合竞价': {
            'start': '09:15',
            'end': '09:20',
            'match': '09:25',
            'description': '可申报可撤单'
        },
        '早盘集合竞价2': {
            'start': '09:20',
            'end': '09:25',
            'match': '09:25',
            'description': '可申报不可撤单'
        },
        '连续竞价1': {
            'start': '09:25',
            'end': '11:30',
            'description': '连续竞价'
        },
        '午间休市': {
            'start': '11:30',
            'end': '13:00',
            'description': '休市1.5小时'
        },
        '连续竞价2': {
            'start': '13:00',
            'end': '14:57',
            'description': '下午连续竞价'
        },
        '尾盘集合竞价': {
            'start': '14:57',
            'end': '15:00',
            'match': '15:00',
            'description': '收盘集合竞价'
        }
    }

    def is_trading_time(self, current_time: str) -> dict:
        """
        判断是否在交易时间内
        """
        t = current_time

        if '09:15' <= t <= '09:25':
            return {'in_trading': True, 'period': '集合竞价'}
        elif '09:25' < t < '11:30':
            return {'in_trading': True, 'period': '早盘连续竞价'}
        elif '11:30' <= t < '13:00':
            return {'in_trading': False, 'period': '午间休市'}
        elif '13:00' <= t < '14:57':
            return {'in_trading': True, 'period': '午后连续竞价'}
        elif '14:57' <= t <= '15:00':
            return {'in_trading': True, 'period': '尾盘竞价'}
        else:
            return {'in_trading': False, 'period': '非交易时间'}

    def get_order_validity(self, order_time: str) -> dict:
        """
        获取订单有效期
        """
        return {
            '当日有效': True,
            '说明': '未成交订单当日收盘自动撤销'
        }
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录BM内容 |
| v1.1 | 2026-03-28 | 补充T.04模块编号，完善规则细节 |
