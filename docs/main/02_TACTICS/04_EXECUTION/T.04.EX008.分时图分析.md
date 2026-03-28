# T.04.EX008.分时图分析

> 分时图分析量化体系
>
> **策略编号**：T.04.EX008
> **所属模块**：04_EXECUTION
> **文档类型**：执行分析
> **优先级**：P2
>
> **配套文档**：
> - [T.04.EX005.开盘竞价信号.md](./T.04.EX005.开盘竞价信号.md) - 竞价信号
> - [T.04.EX006.A股交易规则.md](./T.04.EX006.A股交易规则.md) - 交易规则

---

## 1. 分时时段量化分析

```python
class IntradayPeriodAnalyzer:
    """
    分时时段量化分析

    A股分时时段划分：
    - 集合竞价：9:15-9:25
    - 上午连续竞价：9:30-11:30
    - 午间休市：11:30-13:00
    - 下午连续竞价：13:00-15:00
    - 收盘竞价：14:57-15:00
    """

    PERIODS = {
        'auction': {
            'time': '9:15-9:25',
            'name': '集合竞价',
            'characteristics': [
                '9:15-9:20可撤单，可能虚假',
                '9:20-9:25不可撤单，真实'
            ],
            'strategy': '观察竞价走势，不操作'
        },
        'morning': {
            'time': '9:30-11:30',
            'name': '上午连续竞价',
            'characteristics': [
                '多空双方充分博弈',
                '趋势股最佳操作时段'
            ],
            'strategy': '趋势确认后入场'
        },
        'noon_close': {
            'time': '11:30-13:00',
            'name': '午间休市',
            'characteristics': [
                '信息消化期',
                '部分资金观望'
            ],
            'strategy': '不操作'
        },
        'afternoon': {
            'time': '13:00-15:00',
            'name': '下午连续竞价',
            'characteristics': [
                '尾盘异动多发',
                '2:30后方向选择'
            ],
            'strategy': '关注异动，控制仓位'
        },
        'closing_auction': {
            'time': '14:57-15:00',
            'name': '收盘集合竞价',
            'characteristics': [
                '当日最终定价',
                '大资金操作时段'
            ],
            'strategy': '不追涨杀跌'
        }
    }

    def analyze_current_period(self, current_time) -> dict:
        """
        分析当前时段

        参数:
            current_time: 当前时间

        返回:
            period_info: 时段信息
        """
        hour = current_time.hour
        minute = current_time.minute

        time_value = hour + minute / 60

        if 9 <= time_value < 9.417:
            return self.PERIODS['auction'].copy()
        elif 9.417 <= time_value < 11.5:
            return self.PERIODS['morning'].copy()
        elif 11.5 <= time_value < 13:
            return self.PERIODS['noon_close'].copy()
        elif 13 <= time_value < 14.95:
            return self.PERIODS['afternoon'].copy()
        else:
            return self.PERIODS['closing_auction'].copy()

    def calc_vwap(self, minute_data: pd.DataFrame) -> float:
        """
        计算VWAP（成交均价）

        公式: VWAP = Σ(典型价 × 成交量) / Σ成交量
        典型价 = (最高价 + 最低价 + 收盘价) / 3

        参数:
            minute_data: 分钟数据

        返回:
            vwap: 成交均价
        """
        typical_price = (
            minute_data['high'] +
            minute_data['low'] +
            minute_data['close']
        ) / 3

        vwap = (typical_price * minute_data['volume']).sum() / minute_data['volume'].sum()

        return vwap

    def calc_prev_vwap(self, minute_data: pd.DataFrame,
                      prev_close: float) -> dict:
        """
        计算VWAP偏离度

        参数:
            minute_data: 分钟数据
            prev_close: 昨日收盘价

        返回:
            deviation: VWAP偏离信息
        """
        vwap = self.calc_vwap(minute_data)

        deviation = (vwap - prev_close) / prev_close

        return {
            'vwap': round(vwap, 2),
            'prev_close': prev_close,
            'deviation_pct': round(deviation * 100, 2),
            'above_vwap': vwap > prev_close
        }
```

---

## 2. 分时量价分析

```python
class IntradayVolumePriceAnalyzer:
    """
    分时量价分析器
    """

    def __init__(self):
        self.volume_threshold = 2.0

    def analyze_volume_price(self, minute_data: pd.DataFrame) -> dict:
        """
        分析分时量价关系

        参数:
            minute_data: 分钟数据

        返回:
            analysis: 量价分析
        """
        price_change = self.calc_price_change(minute_data)
        volume_trend = self.calc_volume_trend(minute_data)
        imbalance = self.calc_volume_imbalance(minute_data)

        pattern = self.identify_pattern(price_change, volume_trend, imbalance)

        return {
            'price_change': price_change,
            'volume_trend': volume_trend,
            'volume_imbalance': imbalance,
            'pattern': pattern,
            'signal': self.get_signal(pattern)
        }

    def calc_price_change(self, minute_data: pd.DataFrame) -> dict:
        """
        计算价格变化
        """
        open_price = minute_data['open'].iloc[0]
        close_price = minute_data['close'].iloc[-1]
        high_price = minute_data['high'].max()
        low_price = minute_data['low'].min()

        return {
            'change_pct': round((close_price - open_price) / open_price * 100, 2),
            'high_pct': round((high_price - open_price) / open_price * 100, 2),
            'low_pct': round((low_price - open_price) / open_price * 100, 2),
            'intraday_range': round((high_price - low_price) / open_price * 100, 2)
        }

    def calc_volume_trend(self, minute_data: pd.DataFrame) -> dict:
        """
        计算成交量趋势
        """
        volume = minute_data['volume']
        avg_volume = volume.mean()
        recent_volume = volume.iloc[-30:].mean()

        trend = '平量' if abs(recent_volume / avg_volume - 1) < 0.3 else \
                '放量' if recent_volume > avg_volume * 1.3 else '缩量'

        return {
            'total_volume': volume.sum(),
            'avg_volume': round(avg_volume, 0),
            'recent_volume': round(recent_volume, 0),
            'volume_ratio': round(recent_volume / avg_volume, 2),
            'trend': trend
        }

    def calc_volume_imbalance(self, minute_data: pd.DataFrame) -> dict:
        """
        计算买卖量能失衡
        """
        up_volume = minute_data.loc[minute_data['close'] > minute_data['open'], 'volume'].sum()
        down_volume = minute_data.loc[minute_data['close'] < minute_data['open'], 'volume'].sum()
        total_volume = minute_data['volume'].sum()

        if total_volume == 0:
            return {'imbalance_ratio': 0, 'direction': 'neutral'}

        imbalance = (up_volume - down_volume) / total_volume

        direction = '偏多' if imbalance > 0.2 else \
                   '偏空' if imbalance < -0.2 else '均衡'

        return {
            'up_volume': up_volume,
            'down_volume': down_volume,
            'imbalance_ratio': round(imbalance, 3),
            'direction': direction
        }

    def identify_pattern(self, price_change: dict,
                      volume_trend: dict,
                      imbalance: dict) -> str:
        """
        识别分时图形
        """
        if price_change['change_pct'] > 2 and volume_trend['volume_ratio'] > 1.5:
            return '放量上涨'
        elif price_change['change_pct'] < -2 and volume_trend['volume_ratio'] > 1.5:
            return '放量下跌'
        elif price_change['change_pct'] > 1 and imbalance['direction'] == '偏多':
            return '价升量增'
        elif price_change['change_pct'] < -1 and imbalance['direction'] == '偏空':
            return '价跌量增'
        elif price_change['intraday_range'] < 1:
            return '横盘震荡'
        elif imbalance['direction'] == '均衡':
            return '多空平衡'
        else:
            return '普通走势'

    def get_signal(self, pattern: str) -> str:
        """
        获取信号
        """
        signals = {
            '放量上涨': '积极做多',
            '放量下跌': '规避风险',
            '价升量增': '顺势买入',
            '价跌量增': '观望为主',
            '横盘震荡': '高抛低吸',
            '多空平衡': '方向不明'
        }
        return signals.get(pattern, '观望')
```

---

## 3. 分时均线系统

```python
class IntradayMovingAverageSystem:
    """
    分时均线系统
    """

    def __init__(self):
        self.ma_periods = [5, 10, 20, 60]

    def calculate_ma(self, minute_data: pd.DataFrame) -> dict:
        """
        计算分时均线

        参数:
            minute_data: 分钟数据

        返回:
            ma_values: 均线值
        """
        ma_values = {}

        for period in self.ma_periods:
            ma_values[f'ma{period}'] = round(
                minute_data['close'].rolling(period).mean().iloc[-1], 3
            )

        current_price = minute_data['close'].iloc[-1]

        alignment = self.check_ma_alignment(ma_values, current_price)

        return {
            **ma_values,
            'current_price': current_price,
            'alignment': alignment
        }

    def check_ma_alignment(self, ma_values: dict,
                          current_price: float) -> str:
        """
        检查均线排列

        参数:
            ma_values: 均线值
            current_price: 当前价格

        返回:
            alignment: 排列状态
        """
        ma5 = ma_values.get('ma5', 0)
        ma10 = ma_values.get('ma10', 0)
        ma20 = ma_values.get('ma20', 0)
        ma60 = ma_values.get('ma60', 0)

        if current_price > ma5 > ma10 > ma20 > ma60:
            return '多头排列'
        elif current_price < ma5 < ma10 < ma20 < ma60:
            return '空头排列'
        elif current_price > ma5 and ma5 > ma10:
            return '偏多'
        elif current_price < ma5 and ma5 < ma10:
            return '偏空'
        else:
            return '混乱'

    def generate_signals(self, ma_values: dict,
                        price_change: dict) -> list:
        """
        生成均线信号

        参数:
            ma_values: 均线值
            price_change: 价格变化

        返回:
            signals: 信号列表
        """
        signals = []

        if ma_values['alignment'] == '多头排列' and price_change['change_pct'] > 0:
            signals.append({
                'type': '买入',
                'reason': '均线多头且价格上涨',
                'confidence': '高'
            })

        if ma_values['alignment'] == '空头排列' and price_change['change_pct'] < 0:
            signals.append({
                'type': '卖出',
                'reason': '均线空头且价格下跌',
                'confidence': '高'
            })

        if price_change['change_pct'] > 2:
            signals.append({
                'type': '止盈',
                'reason': '涨幅过大，可能回调',
                'confidence': '中'
            })

        if price_change['change_pct'] < -2:
            signals.append({
                'type': '止损',
                'reason': '跌幅过大，控制风险',
                'confidence': '中'
            })

        return signals
```

---

## 4. 分时MACD分析

```python
class IntradayMACDAnalyzer:
    """
    分时MACD分析
    """

    def __init__(self):
        self.fast_period = 12
        self.slow_period = 26
        self.signal_period = 9

    def calculate_macd(self, minute_data: pd.DataFrame) -> dict:
        """
        计算分时MACD

        参数:
            minute_data: 分钟数据

        返回:
            macd: MACD指标
        """
        ema_fast = minute_data['close'].ewm(span=self.fast_period).mean()
        ema_slow = minute_data['close'].ewm(span=self.slow_period).mean()

        dif = ema_fast - ema_slow
        dea = dif.ewm(span=self.signal_period).mean()
        macd_hist = (dif - dea) * 2

        current_dif = dif.iloc[-1]
        current_dea = dea.iloc[-1]
        current_hist = macd_hist.iloc[-1]

        golden_cross = self.check_golden_cross(dif, dea)
        divergence = self.check_divergence(minute_data, dif)

        return {
            'dif': round(current_dif, 4),
            'dea': round(current_dea, 4),
            'macd_hist': round(current_hist, 4),
            'golden_cross': golden_cross,
            'divergence': divergence,
            'signal': self.get_signal(current_dif, current_dea, current_hist)
        }

    def check_golden_cross(self, dif: pd.Series, dea: pd.Series) -> dict:
        """
        检查金叉死叉
        """
        if len(dif) < 2:
            return {'type': None}

        if dif.iloc[-2] < dea.iloc[-2] and dif.iloc[-1] > dea.iloc[-1]:
            return {'type': '金叉', 'signal': '看涨'}
        elif dif.iloc[-2] > dea.iloc[-2] and dif.iloc[-1] < dea.iloc[-1]:
            return {'type': '死叉', 'signal': '看跌'}

        return {'type': None}

    def check_divergence(self, minute_data: pd.DataFrame,
                       dif: pd.Series) -> str:
        """
        检查背离
        """
        price_trend = minute_data['close'].iloc[-30:].values
        dif_trend = dif.iloc[-30:].values

        price_high = price_trend[-1] > price_trend.max() - 0.01
        dif_high = dif_trend[-1] < dif_trend.max() - 0.01

        price_low = price_trend[-1] < price_trend.min() + 0.01
        dif_low = dif_trend[-1] > dif_trend.min() + 0.01

        if price_high and dif_high:
            return '顶背离'
        elif price_low and dif_low:
            return '底背离'

        return '无背离'

    def get_signal(self, dif: float, dea: float, hist: float) -> str:
        """
        获取信号
        """
        if dif > 0 and hist > 0:
            return '强势上涨'
        elif dif > 0 and hist < 0:
            return '上涨乏力'
        elif dif < 0 and hist < 0:
            return '弱势下跌'
        elif dif < 0 and hist > 0:
            return '下跌抵抗'
        else:
            return '横盘整理'
```

---

## 5. 尾盘异动检测

```python
class ClosingAnomalyDetector:
    """
    尾盘异动检测器
    """

    def __init__(self):
        self.warning_time = '14:30'
        self.critical_time = '14:50'

    def detect_anomaly(self, minute_data: pd.DataFrame) -> dict:
        """
        检测尾盘异动

        参数:
            minute_data: 分钟数据

        返回:
            anomaly: 异动检测结果
        """
        current_time = minute_data.index[-1] if hasattr(minute_data.index, '__getitem__') else None

        if current_time and str(current_time) >= self.warning_time:
            late_anomaly = self.check_late_session(minute_data)
        else:
            late_anomaly = None

        volume_spike = self.check_volume_spike(minute_data)
        price_spike = self.check_price_spike(minute_data)

        return {
            'has_anomaly': any([late_anomaly, volume_spike, price_spike]),
            'late_session': late_anomaly,
            'volume_spike': volume_spike,
            'price_spike': price_spike,
            'risk_level': self.assess_risk(late_anomaly, volume_spike, price_spike)
        }

    def check_late_session(self, minute_data: pd.DataFrame) -> dict:
        """
        检查尾盘时段异动
        """
        late_data = minute_data.iloc[-30:]

        if len(late_data) < 10:
            return None

        late_return = (late_data['close'].iloc[-1] - late_data['close'].iloc[0]) / late_data['close'].iloc[0]

        late_volume_ratio = late_data['volume'].mean() / minute_data['volume'].mean()

        if abs(late_return) > 0.02 or late_volume_ratio > 2:
            return {
                'type': '尾盘异动',
                'return_pct': round(late_return * 100, 2),
                'volume_ratio': round(late_volume_ratio, 2)
            }

        return None

    def check_volume_spike(self, minute_data: pd.DataFrame) -> dict:
        """
        检查成交量突增
        """
        avg_volume = minute_data['volume'].mean()
        std_volume = minute_data['volume'].std()

        recent_volume = minute_data['volume'].iloc[-1]

        z_score = (recent_volume - avg_volume) / std_volume if std_volume > 0 else 0

        if z_score > 3:
            return {
                'type': '量能突增',
                'z_score': round(z_score, 2),
                'volume_ratio': round(recent_volume / avg_volume, 2)
            }

        return None

    def check_price_spike(self, minute_data: pd.DataFrame) -> dict:
        """
        检查价格异动
        """
        returns = minute_data['close'].pct_change()

        avg_return = returns.mean()
        std_return = returns.std()

        recent_return = returns.iloc[-1]

        z_score = (recent_return - avg_return) / std_return if std_return > 0 else 0

        if abs(z_score) > 4:
            return {
                'type': '价格异动',
                'z_score': round(z_score, 2),
                'return_pct': round(recent_return * 100, 2)
            }

        return None

    def assess_risk(self, late_anomaly: dict,
                   volume_spike: dict,
                   price_spike: dict) -> str:
        """
        评估风险等级
        """
        anomaly_count = sum([1 for x in [late_anomaly, volume_spike, price_spike] if x])

        if anomaly_count >= 2:
            return '高风险'
        elif anomaly_count == 1:
            return '中风险'
        else:
            return '正常'
```

---

## 6. 综合分时决策

```python
class IntradayDecisionSystem:
    """
    综合分时决策系统
    """

    def __init__(self):
        self.period_analyzer = IntradayPeriodAnalyzer()
        self.vp_analyzer = IntradayVolumePriceAnalyzer()
        self.ma_system = IntradayMovingAverageSystem()
        self.macd_analyzer = IntradayMACDAnalyzer()

    def make_decision(self, minute_data: pd.DataFrame,
                     current_time: datetime,
                     prev_close: float) -> dict:
        """
        综合分时决策

        参数:
            minute_data: 分钟数据
            current_time: 当前时间
            prev_close: 昨日收盘价

        返回:
            decision: 决策结果
        """
        current_period = self.period_analyzer.analyze_current_period(current_time)
        vp_analysis = self.vp_analyzer.analyze_volume_price(minute_data)
        ma_values = self.ma_system.calculate_ma(minute_data)
        macd = self.macd_analyzer.calculate_macd(minute_data)
        vwap_dev = self.period_analyzer.calc_prev_vwap(minute_data, prev_close)

        composite_score = self.calculate_composite_score(
            vp_analysis, ma_values, macd, vwap_dev
        )

        action = self.decide_action(
            composite_score, vp_analysis, current_period
        )

        return {
            'period': current_period['name'],
            'vwap_deviation': vwap_dev,
            'volume_price': vp_analysis,
            'moving_average': ma_values,
            'macd': macd,
            'composite_score': composite_score,
            'action': action,
            'risk_level': self.assess_overall_risk(vp_analysis, macd)
        }

    def calculate_composite_score(self, vp: dict, ma: dict,
                                 macd: dict, vwap: dict) -> float:
        """
        计算综合评分
        """
        score = 50

        if vp['signal'] in ['放量上涨', '价升量增']:
            score += 15
        elif vp['signal'] in ['放量下跌', '价跌量增']:
            score -= 15

        if ma['alignment'] == '多头排列':
            score += 15
        elif ma['alignment'] == '空头排列':
            score -= 15
        elif ma['alignment'] == '偏多':
            score += 8
        elif ma['alignment'] == '偏空':
            score -= 8

        if macd['signal'] in ['强势上涨', '下跌抵抗']:
            score += 10
        elif macd['signal'] in ['弱势下跌', '上涨乏力']:
            score -= 10

        if vwap['above_vwap']:
            score += 10
        else:
            score -= 10

        return max(0, min(100, score))

    def decide_action(self, score: float, vp: dict,
                     period: dict) -> str:
        """
        决策操作
        """
        if period['name'] in ['午间休市', '收盘集合竞价']:
            return '不操作'

        if score >= 70:
            return '积极买入'
        elif score >= 55:
            return '谨慎买入'
        elif score >= 45:
            return '观望'
        elif score >= 30:
            return '谨慎卖出'
        else:
            return '积极卖出'

    def assess_overall_risk(self, vp: dict, macd: dict) -> str:
        """
        评估整体风险
        """
        risk_factors = 0

        if vp['pattern'] in ['放量下跌', '价跌量增']:
            risk_factors += 1

        if macd.get('divergence') == '顶背离':
            risk_factors += 1

        if risk_factors >= 2:
            return '高风险'
        elif risk_factors == 1:
            return '中风险'
        else:
            return '正常'
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合附录BA：分时图分析量化 |
