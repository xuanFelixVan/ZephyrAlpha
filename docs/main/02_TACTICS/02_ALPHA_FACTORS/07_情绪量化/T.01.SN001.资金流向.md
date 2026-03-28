# T.01.SN001.资金流向情绪策略

> 资金流向情绪因子 - 量化A股特色资金情绪

## 1. 资金流向因子体系

### 1.1 因子分类

| 因子类别 | 因子名称 | 计算方法 | 信号说明 |
|----------|----------|----------|----------|
| 机构净流入 | 机构净流入率 | (机构净流入/成交额)×100% | >5%强烈买入 |
| 逆势资金 | 逆势资金因子 | 大盘下跌时个股上涨且资金净流入 | 重要Alpha来源 |
| 超大单占比 | 超大单占比 | 超大单净流入/机构净流入 | >50%机构行为 |

### 1.2 逆势资金因子（完整算法）

> **A股特色**：大盘下跌时逆势流入的个股/板块，是重要的Alpha来源

```python
class CounterTrendFlowFactor:
    """逆势资金因子"""

    def __init__(self):
        self.monitor_indices = ['上证', '深指', '创业', '科创', '沪深300', '中证500', '中证1000']

    def identify_downtrend_periods(self, minute_data):
        """
        识别大盘下跌时间段
        下跌判断：5分钟K线收盘价 < 前一根5分钟K线收盘价
        """
        downtrend_periods = []
        for index in self.monitor_indices:
            index_data = minute_data[index]
            for i in range(1, len(index_data)):
                if index_data[i]['close'] < index_data[i-1]['close']:
                    downtrend_periods.append({
                        'index': index,
                        'start_time': index_data[i]['time'],
                        'end_time': index_data[i]['time'],
                        'magnitude': (index_data[i]['close'] - index_data[i-1]['close']) / index_data[i-1]['close']
                    })
        return downtrend_periods

    def calculate_counter_trend_strength(self, stock_code, downtrend_periods, stock_data):
        """
        计算个股逆势强度
        """
        counter_trend_count = 0
        counter_trend_flow = 0

        for period in downtrend_periods:
            period_data = self.get_stock_data_in_period(stock_code, period, stock_data)
            if period_data['change_pct'] > 0 and period_data['net_flow'] > 0:
                counter_trend_count += 1
                counter_trend_flow += period_data['net_flow']

        strength = counter_trend_count * counter_trend_flow
        return {
            'strength': strength,
            'count': counter_trend_count,
            'flow': counter_trend_flow
        }

    def aggregate_theme_counter_trend(self, theme_name, component_stocks, downtrend_periods):
        """
        题材逆势资金聚合
        """
        total_count = 0
        total_flow = 0
        stock_details = []

        for stock in component_stocks:
            result = self.calculate_counter_trend_strength(stock['code'], downtrend_periods, stock)
            if result['count'] > 0:
                total_count += result['count']
                total_flow += result['flow']
                stock_details.append({
                    'code': stock['code'],
                    'count': result['count'],
                    'flow': result['flow']
                })

        return {
            'theme': theme_name,
            'total_strength': total_count * total_flow,
            'total_count': total_count,
            'total_flow': total_flow,
            'stock_count': len(stock_details),
            'details': sorted(stock_details, key=lambda x: x['flow'], reverse=True)
        }
```

***

## 2. KDJ多周期共振筛选

### 2.1 共振条件

| 条件 | 量化标准 |
|------|----------|
| 日线J值 | < 0 |
| 120分钟J值 | < 0 |
| 60分钟J值 | < 0 |
| MACD确认 | 多头信号 |

### 2.2 筛选公式

```
筛选条件：
    日线J < 0
    AND 120分钟J < 0
    AND 60分钟J < 0
    AND MACD多头确认
```

```python
class KDJMultiPeriodFilter:
    """KDJ多周期共振筛选"""

    def __init__(self):
        self.parameters = {
            'daily_j_max': 0,
            'minute120_j_max': 0,
            'minute60_j_max': 0,
        }

    def check共振(self, stock_data):
        """
        检查多周期KDJ共振
        """
        params = self.parameters

        daily_j = stock_data.get('日线J值', 50)
        m120_j = stock_data.get('120分钟J值', 50)
        m60_j = stock_data.get('60分钟J值', 50)
        macd_signal = stock_data.get('MACD信号', '空头')

        if daily_j > params['daily_j_max']:
            return False, '日线J值未达标'

        if m120_j > params['minute120_j_max']:
            return False, '120分钟J值未达标'

        if m60_j > params['minute60_j_max']:
            return False, '60分钟J值未达标'

        if macd_signal != '多头':
            return False, 'MACD未确认多头'

        return True, '共振条件满足'
```

***

## 3. 情绪-分布对照表

> **说明**：将情绪指标作为PDF模型输入特征，观察输出分布的偏度和尾部变化

### 3.1 构建方法

| 步骤 | 内容 | 输出 |
|------|------|------|
| 1. 收集历史情绪指标 | 恐慌/贪婪指数、北向资金等 | 情绪指标时间序列 |
| 2. 对应收益率数据 | 收集对应时期的收益率数据 | 收益分布 |
| 3. 分箱统计 | 按情绪高低分箱 | 各箱收益分布 |
| 4. 分析偏度变化 | 观察左偏/右偏 | 偏度表 |
| 5. 分析尾部变化 | 观察厚尾/薄尾 | 尾部厚度表 |

### 3.2 情绪状态与分布特征

| 情绪状态 | 预期分布特征 | 操作建议 |
|----------|--------------|----------|
| 恐慌（<30） | 左偏+厚尾 | 提高仓位，逆向布局 |
| 中性（30-70） | 基本正态 | 均衡配置 |
| 过热（>70） | 右偏+厚尾 | 降低仓位，谨慎追高 |

```python
class SentimentDistributionModel:
    """情绪-分布对照模型"""

    def __init__(self):
        self.sentiment_thresholds = {
            '恐慌': 30,
            '中性': (30, 70),
            '过热': 70
        }

    def build_distribution_by_sentiment(self, sentiment_data, return_data):
        """
        按情绪分箱构建分布
        """
        result = {}

        for level, threshold in self.sentiment_thresholds.items():
            if isinstance(threshold, tuple):
                mask = (sentiment_data >= threshold[0]) & (sentiment_data < threshold[1])
            else:
                mask = sentiment_data < threshold

            subset_returns = return_data[mask]

            result[level] = {
                'mean': subset_returns.mean(),
                'std': subset_returns.std(),
                'skewness': subset_returns.skew(),
                'kurtosis': subset_returns.kurtosis(),
                'VaR_5': subset_returns.quantile(0.05),
                'VaR_95': subset_returns.quantile(0.95),
            }

        return result

    def get_action_by_sentiment(self, current_sentiment):
        """
        根据当前情绪获取操作建议
        """
        if current_sentiment < self.sentiment_thresholds['恐慌']:
            return {
                'state': '恐慌',
                'distribution': '左偏+厚尾',
                'action': '提高仓位，逆向布局',
                'position_multiplier': 1.2
            }
        elif current_sentiment > self.sentiment_thresholds['过热']:
            return {
                'state': '过热',
                'distribution': '右偏+厚尾',
                'action': '降低仓位，谨慎追高',
                'position_multiplier': 0.7
            }
        else:
            return {
                'state': '中性',
                'distribution': '基本正态',
                'action': '均衡配置',
                'position_multiplier': 1.0
            }
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合逆势资金因子、KDJ多周期共振、情绪-分布对照模型 |
