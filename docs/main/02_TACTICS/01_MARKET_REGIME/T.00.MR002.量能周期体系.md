# T.00.MR002.量能周期体系

> 市场量能周期与牛熊转换量化
>
> **策略编号**：T.00.MR002
> **所属模块**：01_MARKET_REGIME
> **文档类型**：市场状态
> **优先级**：P1
>
> **配套文档**：
> - [T.00.MR001.市场趋势识别.md](./T.00.MR001.市场趋势识别.md) - 五维市场状态
> - [T.00.MR003.市场结构博弈.md](./T.00.MR003.市场结构博弈.md) - 多空博弈结构

---

## 1. 量能周期理论基础

```python
class VolumeCycleAnalyzer:
    """
    量能周期分析器

    核心理论：
    - 量先于价：成交量放大往往先于价格变化
    - 天量天价：成交量峰值对应价格顶部
    - 地量地价：成交量谷值对应价格底部
    - 量价背离：顶背离看跌，底背离看涨
    """

    VOLUME_STATES = ['天量', '放量', '平量', '缩量', '地量']
    CYCLE_STATES = ['吸筹期', '拉升期', '派发期', '砸盘期']
```

---

## 2. 量能状态量化标准

### 2.1 五档量能状态

```python
class VolumeStateClassifier:
    """
    量能状态分类器
    """

    VOLUME_RATIO_THRESHOLDS = {
        '天量': 3.0,
        '放量': 1.5,
        '平量上限': 1.2,
        '平量下限': 0.8,
        '缩量': 0.5,
        '地量': 0.3
    }

    def classify_volume_state(self, current_volume: float,
                             average_volume: float,
                             historical_high: float = None,
                             historical_low: float = None) -> dict:
        """
        量能状态分类

        参数:
            current_volume: 当期成交量
            average_volume: 平均成交量（20日均量）
            historical_high: 历史最高成交量（可选）
            historical_low: 历史最低成交量（可选）

        返回:
            classification: 分类结果
        """
        ratio = current_volume / average_volume if average_volume > 0 else 0

        if ratio >= self.VOLUME_RATIO_THRESHOLDS['天量']:
            state = '天量'
            signal = '警惕顶部'
        elif ratio >= self.VOLUME_RATIO_THRESHOLDS['放量']:
            state = '放量'
            signal = '关注方向'
        elif ratio >= self.VOLUME_RATIO_THRESHOLDS['平量上限']:
            state = '平量'
            signal = '观望'
        elif ratio >= self.VOLUME_RATIO_THRESHOLDS['平量下限']:
            state = '缩量'
            signal = '趋势延续'
        elif ratio >= self.VOLUME_RATIO_THRESHOLDS['地量']:
            state = '地量'
            signal = '关注底部'
        else:
            state = '极度地量'
            signal = '可能反转'

        if historical_high and current_volume >= historical_high * 0.95:
            state = '天量'
            signal = '历史天量，警惕顶部'

        if historical_low and current_volume <= historical_low * 1.05:
            state = '地量'
            signal = '历史地量，关注底部'

        return {
            'state': state,
            'volume_ratio': round(ratio, 2),
            'signal': signal,
            'action': self.get_action_by_state(state)
        }

    def get_action_by_state(self, state: str) -> str:
        """
        根据量能状态获取操作建议
        """
        actions = {
            '天量': '减仓/止盈',
            '放量': '顺势而为',
            '平量': '观望等待',
            '缩量': '持仓观察',
            '地量': '逆向布局',
            '极度地量': '分批建仓'
        }
        return actions.get(state, '观望')
```

---

## 3. 量价背离识别

```python
class VolumePriceDivergenceDetector:
    """
    量价背离检测器

    检测类型：
    - 顶背离：价格创新高但量能不足
    - 底背离：价格创新低但量能放大
    - 二次背离：连续两次背离，确认信号更强
    """

    def __init__(self):
        self.min_lookback = 20
        self.divergence_threshold = 0.8

    def detect_divergence(self, price_data: pd.Series,
                         volume_data: pd.Series,
                         window: int = 20) -> list:
        """
        检测量价背离

        参数:
            price_data: 价格序列
            volume_data: 成交量序列
            window: 检测窗口

        返回:
            divergences: 背离信号列表
        """
        divergences = []

        price_pivot = self.find_pivots(price_data, window)
        volume_pivot = self.find_pivots(volume_data, window)

        for i in range(len(price_pivot)):
            if price_pivot[i]['type'] == 'top':
                divergence = self.check_top_divergence(
                    i, price_pivot, volume_pivot, price_data, volume_data
                )
                if divergence:
                    divergences.append(divergence)

            elif price_pivot[i]['type'] == 'bottom':
                divergence = self.check_bottom_divergence(
                    i, price_pivot, volume_pivot, price_data, volume_data
                )
                if divergence:
                    divergences.append(divergence)

        return divergences

    def find_pivots(self, data: pd.Series, window: int) -> list:
        """
        寻找极值点

        返回:
            pivots: [{'index': int, 'type': 'top'/'bottom', 'value': float}]
        """
        pivots = []

        for i in range(window, len(data) - window):
            is_top = True
            is_bottom = True

            for j in range(1, window + 1):
                if data.iloc[i] < data.iloc[i - j]:
                    is_top = False
                if data.iloc[i] > data.iloc[i + j]:
                    is_bottom = False

            if is_top:
                pivots.append({'index': i, 'type': 'top', 'value': data.iloc[i]})
            if is_bottom:
                pivots.append({'index': i, 'type': 'bottom', 'value': data.iloc[i]})

        return pivots

    def check_top_divergence(self, pivot_idx: int,
                            price_pivots: list,
                            volume_pivots: list,
                            price_data: pd.Series,
                            volume_data: pd.Series) -> dict:
        """
        检查顶背离

        条件：价格创新高，但量能未创新高
        """
        current_pivot = price_pivots[pivot_idx]

        prev_tops = [p for p in price_pivots
                    if p['type'] == 'top' and p['index'] < current_pivot['index']]

        if not prev_tops or len(prev_tops) < 2:
            return None

        prev_top = prev_tops[-1]
        prev_top2 = prev_tops[-2]

        if current_pivot['value'] > prev_top['value']:
            current_volume = volume_data.iloc[current_pivot['index']]
            prev_volume = volume_data.iloc[prev_top['index']]

            if current_volume < prev_volume * self.divergence_threshold:
                return {
                    'type': '顶背离',
                    'price_trend': '新高',
                    'volume_trend': '萎缩',
                    'signal': '看跌',
                    'strength': '强' if current_volume < prev_volume * 0.5 else '中',
                    'index': current_pivot['index']
                }

        return None

    def check_bottom_divergence(self, pivot_idx: int,
                               price_pivots: list,
                               volume_pivots: list,
                               price_data: pd.Series,
                               volume_data: pd.Series) -> dict:
        """
        检查底背离

        条件：价格创新低，但量能放大
        """
        current_pivot = price_pivots[pivot_idx]

        prev_bottoms = [p for p in price_pivots
                       if p['type'] == 'bottom' and p['index'] < current_pivot['index']]

        if not prev_bottoms or len(prev_bottoms) < 2:
            return None

        prev_bottom = prev_bottoms[-1]
        prev_bottom2 = prev_bottoms[-2]

        if current_pivot['value'] < prev_bottom['value']:
            current_volume = volume_data.iloc[current_pivot['index']]
            prev_volume = volume_data.iloc[prev_bottom['index']]

            if current_volume > prev_volume * (2 - self.divergence_threshold):
                return {
                    'type': '底背离',
                    'price_trend': '新低',
                    'volume_trend': '放大',
                    'signal': '看涨',
                    'strength': '强' if current_volume > prev_volume * 1.5 else '中',
                    'index': current_pivot['index']
                }

        return None
```

---

## 4. 牛熊周期量化

```python
class BullBearCycleAnalyzer:
    """
    牛熊周期分析器
    """

    def __init__(self):
        self.ma_params = {
            'short': 5,
            'medium': 20,
            'long': 60
        }

    def identify_market_cycle(self, index_data: pd.DataFrame) -> dict:
        """
        识别市场周期阶段

        参数:
            index_data: 指数数据，包含 close, volume

        返回:
            cycle_info: 周期信息
        """
        close = index_data['close']

        ma5 = close.rolling(self.ma_params['short']).mean()
        ma20 = close.rolling(self.ma_params['medium']).mean()
        ma60 = close.rolling(self.ma_params['long']).mean()

        current_price = close.iloc[-1]
        ma5_current = ma5.iloc[-1]
        ma20_current = ma20.iloc[-1]
        ma60_current = ma60.iloc[-1]

        if ma5_current > ma20_current > ma60_current:
            trend = '多头排列'
            cycle = self._identify_bull_phase(index_data)
        elif ma5_current < ma20_current < ma60_current:
            trend = '空头排列'
            cycle = self._identify_bear_phase(index_data)
        else:
            trend = '震荡整理'
            cycle = {'phase': '震荡市', 'position': '中期'}

        return {
            'trend': trend,
            'ma5': round(ma5_current, 2),
            'ma20': round(ma20_current, 2),
            'ma60': round(ma60_current, 2),
            'cycle': cycle,
            'price_vs_ma60': round((current_price - ma60_current) / ma60_current * 100, 2)
        }

    def _identify_bull_phase(self, index_data: pd.DataFrame) -> dict:
        """
        识别牛市阶段
        """
        close = index_data['close']
        volume = index_data['volume']

        current_price = close.iloc[-1]
        price_peak = close.iloc[-60:].max()
        price_change = (current_price - close.iloc[-60]) / close.iloc[-60]

        current_vol = volume.iloc[-1]
        avg_vol = volume.iloc[-20:].mean()

        if price_change < 0.1:
            phase = '牛市初期'
            position = '估值修复'
        elif price_change < 0.3:
            phase = '牛市中期'
            position = '赚钱效应'
        elif current_price >= price_peak * 0.98:
            phase = '牛市后期'
            position = '泡沫积累'
        else:
            phase = '牛市中期'
            position = '震荡上行'

        if current_vol > avg_vol * 2:
            position += '（天量警告）'

        return {'phase': phase, 'position': position}

    def _identify_bear_phase(self, index_data: pd.DataFrame) -> dict:
        """
        识别熊市阶段
        """
        close = index_data['close']
        volume = index_data['volume']

        current_price = close.iloc[-1]
        price_trough = close.iloc[-60:].min()
        price_change = (current_price - close.iloc[-60]) / close.iloc[-60]

        current_vol = volume.iloc[-1]
        avg_vol = volume.iloc[-20:].mean()

        if price_change > -0.1:
            phase = '熊市初期'
            position = '估值消化'
        elif price_change > -0.3:
            phase = '熊市中期'
            position = '亏钱效应'
        elif current_vol <= avg_vol * 0.5:
            phase = '熊市末期'
            position = '情绪冰点'
        else:
            phase = '熊市中期'
            position = '震荡寻底'

        return {'phase': phase, 'position': position}

    def detect_cycle_transformation(self, index_data: pd.DataFrame) -> dict:
        """
        检测周期转换信号

        返回:
            transformation: 转换信号
        """
        close = index_data['close']
        volume = index_data['volume']

        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()

        price_above_60 = close.iloc[-1] > ma60.iloc[-1]
        price_below_60 = close.iloc[-1] < ma60.iloc[-1]

        vol_surge = volume.iloc[-1] > volume.iloc[-20:].mean() * 1.5

        if not price_above_60 and close.iloc[-3] < ma60.iloc[-3] and close.iloc[-1] > ma60.iloc[-1]:
            return {
                'transformation': '熊转牛',
                'signal': '价格突破60日线',
                'confidence': '高' if vol_surge else '中',
                'action': '逐步建仓'
            }

        if price_above_60 and close.iloc[-3] > ma60.iloc[-3] and close.iloc[-1] < ma60.iloc[-1]:
            return {
                'transformation': '牛转熊',
                'signal': '价格跌破60日线',
                'confidence': '高' if vol_surge else '中',
                'action': '逐步减仓'
            }

        return {
            'transformation': '无明显转换',
            'signal': '趋势延续',
            'confidence': '-',
            'action': '持仓观望'
        }
```

---

## 5. 周期仓位管理

```python
class CycleBasedPositionManager:
    """
    基于周期的仓位管理器
    """

    POSITION_RULES = {
        '牛市初期': {'target_position': 0.6, 'add_condition': '回调至MA20'},
        '牛市中期': {'target_position': 0.8, 'add_condition': '回踩不破MA5'},
        '牛市后期': {'target_position': 0.4, 'add_condition': '突破新高'},
        '熊市初期': {'target_position': 0.0, 'add_condition': '禁止加仓'},
        '熊市中期': {'target_position': 0.2, 'add_condition': '超跌反弹'},
        '熊市末期': {'target_position': 0.4, 'add_condition': '估值底部'},
        '震荡市': {'target_position': 0.3, 'add_condition': '支撑位买入'}
    }

    def calculate_target_position(self, cycle_info: dict,
                                 current_position: float) -> dict:
        """
        计算目标仓位

        参数:
            cycle_info: 周期信息
            current_position: 当前仓位

        返回:
            position_plan: 仓位计划
        """
        phase = cycle_info['cycle']['phase']

        rules = self.POSITION_RULES.get(phase, {'target_position': 0.3})

        target = rules['target_position']
        action = self.calculate_action(current_position, target)

        return {
            'current_phase': phase,
            'target_position': target,
            'current_position': current_position,
            'action': action,
            'position_change': target - current_position,
            'add_condition': rules['add_condition']
        }

    def calculate_action(self, current: float, target: float) -> str:
        """
        计算操作指令
        """
        diff = target - current

        if abs(diff) < 0.05:
            return '持仓不动'
        elif diff > 0:
            return f'加仓{int(diff * 100)}%'
        else:
            return f'减仓{int(abs(diff) * 100)}%'
```

---

## 6. 量能周期综合评估

```python
class VolumeCycleEvaluator:
    """
    量能周期综合评估器
    """

    def __init__(self):
        self.volume_classifier = VolumeStateClassifier()
        self.divergence_detector = VolumePriceDivergenceDetector()
        self.cycle_analyzer = BullBearCycleAnalyzer()

    def comprehensive_evaluation(self, index_data: pd.DataFrame) -> dict:
        """
        综合评估

        参数:
            index_data: 包含 close, volume 的DataFrame

        返回:
            evaluation: 综合评估结果
        """
        close = index_data['close']
        volume = index_data['volume']

        avg_vol_20 = volume.rolling(20).mean().iloc[-1]
        current_vol = volume.iloc[-1]
        hist_high_vol = volume.iloc[-60:].max()
        hist_low_vol = volume.iloc[-60:].min()

        volume_state = self.volume_classifier.classify_volume_state(
            current_vol, avg_vol_20, hist_high_vol, hist_low_vol
        )

        divergences = self.divergence_detector.detect_divergence(
            close, volume, window=20
        )
        recent_divergences = [d for d in divergences if d['index'] > len(close) - 30]

        cycle_info = self.cycle_analyzer.identify_market_cycle(index_data)

        transformation = self.cycle_analyzer.detect_cycle_transformation(index_data)

        overall_signal = self.synthesize_signals(
            volume_state, recent_divergences, cycle_info, transformation
        )

        return {
            'volume_state': volume_state,
            'divergences': recent_divergences,
            'cycle_info': cycle_info,
            'transformation': transformation,
            'overall_signal': overall_signal
        }

    def synthesize_signals(self, volume_state: dict,
                         divergences: list,
                         cycle_info: dict,
                         transformation: dict) -> dict:
        """
        综合信号合成
        """
        bullish_signals = 0
        bearish_signals = 0

        if volume_state['state'] in ['放量', '平量']:
            bullish_signals += 1
        elif volume_state['state'] in ['天量', '缩量']:
            bearish_signals += 1

        for d in divergences:
            if d['type'] == '底背离':
                bullish_signals += 2
            elif d['type'] == '顶背离':
                bearish_signals += 2

        if '多头' in cycle_info['trend']:
            bullish_signals += 1
        elif '空头' in cycle_info['trend']:
            bearish_signals += 1

        if transformation['transformation'] == '熊转牛':
            bullish_signals += 3
        elif transformation['transformation'] == '牛转熊':
            bearish_signals += 3

        if bullish_signals > bearish_signals + 2:
            signal = '积极做多'
            confidence = '高'
        elif bullish_signals > bearish_signals:
            signal = '谨慎看多'
            confidence = '中'
        elif bearish_signals > bullish_signals + 2:
            signal = '规避风险'
            confidence = '高'
        elif bearish_signals > bullish_signals:
            signal = '谨慎看空'
            confidence = '中'
        else:
            signal = '中性观望'
            confidence = '低'

        return {
            'signal': signal,
            'confidence': confidence,
            'bullish_score': bullish_signals,
            'bearish_score': bearish_signals
        }
```

---

## 7. 使用示例

```python
def example_volume_cycle_analysis():
    """
    量能周期分析示例
    """
    evaluator = VolumeCycleEvaluator()
    position_manager = CycleBasedPositionManager()

    index_data = pd.read_csv('index_data.csv')

    result = evaluator.comprehensive_evaluation(index_data)

    print(f"量能状态: {result['volume_state']['state']}")
    print(f"量比: {result['volume_state']['volume_ratio']}")
    print(f"信号: {result['volume_state']['signal']}")

    print(f"\n趋势: {result['cycle_info']['trend']}")
    print(f"周期: {result['cycle_info']['cycle']['phase']}")
    print(f"位置: {result['cycle_info']['cycle']['position']}")

    print(f"\n整体信号: {result['overall_signal']['signal']}")
    print(f"置信度: {result['overall_signal']['confidence']}")

    if result['divergences']:
        print("\n背离信号:")
        for d in result['divergences']:
            print(f"  {d['type']}: {d['signal']} (强度: {d['strength']})")

    position_plan = position_manager.calculate_target_position(
        result['cycle_info'],
        current_position=0.5
    )
    print(f"\n仓位计划: {position_plan['action']}")
    print(f"目标仓位: {position_plan['target_position']*100:.0f}%")
```

---

## 8. 量能状态速查表

| 量能状态 | 量比范围 | 市场含义 | 操作建议 |
|----------|----------|----------|----------|
| 天量 | ≥3.0 | 顶部预警 | 减仓止盈 |
| 放量 | 1.5~3.0 | 方向确认 | 顺势而为 |
| 平量 | 0.8~1.5 | 趋势延续 | 观望 |
| 缩量 | 0.3~0.8 | 趋势延续 | 持仓 |
| 地量 | <0.3 | 底部区域 | 逆向布局 |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合量能周期体系，量价背离识别，牛熊周期量化 |
