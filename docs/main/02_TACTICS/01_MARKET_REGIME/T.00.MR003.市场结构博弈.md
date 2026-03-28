# T.00.MR003.市场结构博弈

> 多空博弈结构与市场结构量化分析
>
> **策略编号**：T.00.MR003
> **所属模块**：01_MARKET_REGIME
> **文档类型**：市场状态
> **优先级**：P2
>
> **配套文档**：
> - [T.00.MR001.市场趋势识别.md](./T.00.MR001.市场趋势识别.md) - 五维市场状态
> - [T.00.MR002.量能周期体系.md](./T.00.MR002.量能周期体系.md) - 量能周期

---

## 1. 市场结构理论基础

```python
class MarketStructureAnalyzer:
    """
    市场结构分析器

    核心理论：
    - 市场价格走势由多空双方博弈决定
    - 结构突破先于价格突破
    - 支撑阻力位是博弈的均衡点
    - 板块轮动反映资金流向
    """

    STRUCTURE_TYPES = ['上涨结构', '下跌结构', '震荡结构', '突破结构']
    GAME_PLAYERS = ['机构', '游资', '散户', '外资']
```

---

## 2. 多空博弈结构

### 2.1 多空力量量化

```python
class MultiShortForceAnalyzer:
    """
    多空力量分析器
    """

    def __init__(self):
        self.player_characteristics = {
            '机构': {
                'time_horizon': '中长期',
                'position_pattern': '逐步建仓',
                'trade_impact': '持续影响',
                '识别特征': ['持续净流入', '下跌吸筹', '换手率适中']
            },
            '游资': {
                'time_horizon': '超短线',
                'position_pattern': '快进快出',
                'trade_impact': '脉冲影响',
                '识别特征': ['涨停板', '龙虎榜', '高换手率']
            },
            '散户': {
                'time_horizon': '不确定',
                'position_pattern': '追涨杀跌',
                'trade_impact': '顺趋势',
                '识别特征': ['分散', '羊群效应']
            },
            '外资': {
                'time_horizon': '中长期',
                'position_pattern': '价值投资',
                'trade_impact': '稳定器',
                '识别特征': ['北向资金', '低估值偏好']
            }
        }

    def calculate_force_balance(self, market_data: pd.DataFrame) -> dict:
        """
        计算多空力量对比

        参数:
            market_data: 市场数据，包含北向资金、融资融券、涨跌家数等

        返回:
            balance: 多空力量对比
        """
        north_flow = market_data.get('north_flow', 0)
        margin_balance_change = market_data.get('margin_balance_change', 0)
        limit_up_count = market_data.get('limit_up_count', 0)
        limit_down_count = market_data.get('limit_down_count', 0)

        long_force = 0
        short_force = 0

        if north_flow > 0:
            long_force += min(north_flow / 30, 1) * 30
        else:
            short_force += min(abs(north_flow) / 30, 1) * 30

        if margin_balance_change > 0:
            long_force += min(margin_balance_change / 50, 1) * 25
        else:
            short_force += min(abs(margin_balance_change) / 50, 1) * 25

        long_force += min(limit_up_count / 50, 1) * 25
        short_force += min(limit_down_count / 30, 1) * 20

        total_force = long_force + short_force
        if total_force == 0:
            return {
                'long_force': 50,
                'short_force': 50,
                'balance': '势均力敌',
                'net_force': 0
            }

        net = long_force - short_force

        if net > 20:
            balance = '多头主导'
        elif net > 5:
            balance = '偏多'
        elif net < -20:
            balance = '空头主导'
        elif net < -5:
            balance = '偏空'
        else:
            balance = '势均力敌'

        return {
            'long_force': round(long_force, 1),
            'short_force': round(short_force, 1),
            'balance': balance,
            'net_force': round(net, 1)
        }

    def identify_dominant_player(self, stock_data: pd.DataFrame) -> dict:
        """
        识别主导资金类型

        参数:
            stock_data: 个股数据

        返回:
            dominant: 主导资金类型
        """
        turnover_rate = stock_data.get('turnover_rate', 0)
        north_hold_change = stock_data.get('north_hold_change', 0)
        retail_flow = stock_data.get('retail_flow', 0)
        limit_up = stock_data.get('limit_up', False)

        scores = {
            '机构': 0,
            '游资': 0,
            '散户': 0,
            '外资': 0
        }

        if turnover_rate > 0.15:
            scores['游资'] += 3
        elif turnover_rate < 0.03:
            scores['机构'] += 2
            scores['外资'] += 2

        if abs(north_hold_change) > 0.01:
            if north_hold_change > 0:
                scores['外资'] += 3
            else:
                scores['机构'] += 1

        if limit_up:
            scores['游资'] += 4

        if retail_flow > 0:
            scores['散户'] += 2

        dominant = max(scores, key=scores.get)

        return {
            'dominant_player': dominant,
            'scores': scores,
            'confidence': scores[dominant] / sum(scores.values()) if sum(scores.values()) > 0 else 0
        }
```

---

## 3. 支撑阻力结构

```python
class SupportResistanceAnalyzer:
    """
    支撑阻力分析器
    """

    def __init__(self):
        self.lookback_periods = [5, 20, 60, 120]

    def find_support_resistance_levels(self, price_data: pd.Series,
                                       volume_data: pd.Series = None) -> dict:
        """
        寻找支撑阻力位

        参数:
            price_data: 价格数据
            volume_data: 成交量数据（可选）

        返回:
            levels: 支撑阻力位
        """
        levels = {
            '阻力位': [],
            '支撑位': [],
            '强弱分界': None
        }

        for period in self.lookback_periods:
            if len(price_data) < period:
                continue

            period_data = price_data.iloc[-period:]

            high = period_data.max()
            low = period_data.min()
            current = price_data.iloc[-1]

            resistance = high
            support = low

            distance_from_high = (high - current) / current
            distance_from_low = (current - low) / low

            if distance_from_high < 0.05:
                levels['阻力位'].append({
                    'level': high,
                    'type': '近期高点',
                    'period': period,
                    'strength': '强'
                })

            if distance_from_low < 0.03:
                levels['支撑位'].append({
                    'level': low,
                    'type': '近期低点',
                    'period': period,
                    'strength': '强'
                })

            pivot_high = self.calc_pivot_high(period_data)
            pivot_low = self.calc_pivot_low(period_data)

            if pivot_high:
                levels['阻力位'].append({
                    'level': pivot_high,
                    'type': '枢轴高点',
                    'period': period,
                    'strength': '中'
                })

            if pivot_low:
                levels['支撑位'].append({
                    'level': pivot_low,
                    'type': '枢轴低点',
                    'period': period,
                    'strength': '中'
                })

        if volume_data is not None:
            vol_levels = self.find_volume_profile_levels(price_data, volume_data)
            levels['成交量加权'] = vol_levels

        levels['强弱分界'] = price_data.iloc[-20:].mean()

        return levels

    def calc_pivot_high(self, data: pd.Series) -> float:
        """
        计算枢轴高点
        """
        if len(data) < 5:
            return None

        pivot_idx = data.idxmax()
        return data[pivot_idx]

    def calc_pivot_low(self, data: pd.Series) -> float:
        """
        计算枢轴低点
        """
        if len(data) < 5:
            return None

        pivot_idx = data.idxmin()
        return data[pivot_idx]

    def find_volume_profile_levels(self, price_data: pd.Series,
                                   volume_data: pd.Series) -> list:
        """
        寻找成交量加权支撑阻力位

        原理：高频成交区域形成强支撑/阻力
        """
        price_range = price_data.max() - price_data.min()
        bin_count = 20
        bin_size = price_range / bin_count

        volume_profile = {}

        for i in range(len(price_data)):
            price_bin = int((price_data.iloc[i] - price_data.min()) / bin_size)
            price_level = price_data.min() + (price_bin + 0.5) * bin_size

            if price_level not in volume_profile:
                volume_profile[price_level] = 0
            volume_profile[price_level] += volume_data.iloc[i]

        sorted_levels = sorted(volume_profile.items(), key=lambda x: x[1], reverse=True)

        high_volume_levels = [level for level, vol in sorted_levels[:3]]

        return high_volume_levels

    def calculate_breakout_strength(self, price_data: pd.Series,
                                    volume_data: pd.Series,
                                    breakout_price: float) -> dict:
        """
        计算突破强度

        参数:
            price_data: 价格数据
            volume_data: 成交量数据
            breakout_price: 突破价位

        返回:
            strength: 突破强度
        """
        current_price = price_data.iloc[-1]
        prev_prices = price_data.iloc[-5:-1]

        price_momentum = (current_price - breakout_price) / breakout_price

        vol_before = volume_data.iloc[-5:-1].mean()
        vol_after = volume_data.iloc[-1]

        volume_surge = vol_after / vol_before if vol_before > 0 else 1

        if current_price > breakout_price and price_momentum > 0.02 and volume_surge > 1.5:
            strength = '强突破'
            reliability = '高'
        elif current_price > breakout_price:
            strength = '弱突破'
            reliability = '中'
        else:
            strength = '假突破'
            reliability = '低'

        return {
            'breakout_price': breakout_price,
            'current_price': current_price,
            'price_momentum': round(price_momentum * 100, 2),
            'volume_surge': round(volume_surge, 2),
            'strength': strength,
            'reliability': reliability,
            'recommendation': self.get_breakout_recommendation(strength, reliability)
        }

    def get_breakout_recommendation(self, strength: str, reliability: str) -> str:
        """
        获取突破操作建议
        """
        if strength == '强突破' and reliability == '高':
            return '积极买入，趋势确认'
        elif strength == '强突破' and reliability == '中':
            return '轻仓试探，确认加仓'
        elif strength == '弱突破':
            return '观望为主，等待回踩'
        else:
            return '拒绝参与，规避风险'
```

---

## 4. 板块轮动博弈

```python
class SectorRotationAnalyzer:
    """
    板块轮动分析器
    """

    def __init__(self):
        self.sector_classification = {
            '周期股': ['煤炭', '钢铁', '有色', '化工', '建材'],
            '金融股': ['银行', '保险', '证券', '多元金融'],
            '消费股': ['白酒', '食品', '家电', '汽车', '服装'],
            '科技股': ['半导体', '软件', '通信设备', '电子'],
            '防御股': ['医药', '公用事业', '高速公路', '港口']
        }

    def analyze_rotation_pattern(self, sector_data: pd.DataFrame) -> dict:
        """
        分析轮动模式

        参数:
            sector_data: 板块数据，包含各板块涨跌幅

        返回:
            pattern: 轮动模式
        """
        if len(sector_data) < 5:
            return {'pattern': '数据不足'}

        sector_returns = sector_data.iloc[-1].sort_values(ascending=False)

        leading_sector = sector_returns.index[0]
        lagging_sector = sector_returns.index[-1]

        top3_return = sector_returns.iloc[:3].mean()
        bottom3_return = sector_returns.iloc[-3:].mean()
        spread = top3_return - bottom3_return

        rotation_speed = self.calc_rotation_speed(sector_data)

        if spread > 3 and rotation_speed > 0.7:
            pattern = '快速轮动'
        elif spread > 1.5:
            pattern = '慢速轮动'
        elif abs(spread) < 1:
            pattern = '无明显轮动'
        else:
            pattern = '震荡调整'

        return {
            'pattern': pattern,
            'leading_sector': leading_sector,
            'lagging_sector': lagging_sector,
            'top3_return': round(top3_return, 2),
            'bottom3_return': round(bottom3_return, 2),
            'spread': round(spread, 2),
            'rotation_speed': round(rotation_speed, 2),
            'recommendation': self.get_rotation_recommendation(pattern, leading_sector)
        }

    def calc_rotation_speed(self, sector_data: pd.DataFrame) -> float:
        """
        计算轮动速度

        返回0-1之间的值，1表示完全轮动
        """
        if len(sector_data) < 2:
            return 0

        rank_changes = []

        for i in range(1, len(sector_data)):
            prev_rank = sector_data.iloc[i-1].rank(ascending=False)
            curr_rank = sector_data.iloc[i].rank(ascending=False)

            rank_diff = abs(curr_rank - prev_rank).mean()
            max_diff = len(sector_data.columns) - 1
            rank_changes.append(rank_diff / max_diff)

        return sum(rank_changes) / len(rank_changes) if rank_changes else 0

    def get_rotation_recommendation(self, pattern: str, leading_sector: str) -> str:
        """
        获取轮动操作建议
        """
        recommendations = {
            '快速轮动': f'市场活跃但节奏过快，追热点风险大，建议潜伏{leading_sector}',
            '慢速轮动': f'资金有序轮动，可跟涨前期强势板块',
            '无明显轮动': '市场方向不明，宜观望',
            '震荡调整': '市场调整，静待新主线出现'
        }
        return recommendations.get(pattern, '观望')

    def predict_next_sector(self, sector_data: pd.DataFrame,
                           lookback: int = 5) -> list:
        """
        预测下一个强势板块

        参数:
            sector_data: 历史板块数据
            lookback: 回溯天数

        返回:
            predictions: 预测排名
        """
        if len(sector_data) < lookback:
            return []

        recent_trend = sector_data.iloc[-lookback:].mean()
        momentum = sector_data.iloc[-1] - sector_data.iloc[-lookback]

        combined_score = recent_trend * 0.6 + momentum * 0.4

        predictions = combined_score.sort_values(ascending=False)

        return [
            {'rank': i+1, 'sector': sector, 'score': round(score, 4)}
            for i, (sector, score) in enumerate(predictions.items())
        ]
```

---

## 5. 市场结构综合评估

```python
class MarketStructureEvaluator:
    """
    市场结构综合评估器
    """

    def __init__(self):
        self.force_analyzer = MultiShortForceAnalyzer()
        self.sr_analyzer = SupportResistanceAnalyzer()
        self.rotation_analyzer = SectorRotationAnalyzer()

    def comprehensive_evaluation(self, market_data: pd.DataFrame) -> dict:
        """
        综合评估市场结构

        参数:
            market_data: 市场数据

        返回:
            evaluation: 综合评估结果
        """
        force_balance = self.force_analyzer.calculate_force_balance(market_data)

        price_data = market_data['close']
        volume_data = market_data.get('volume')

        sr_levels = self.sr_analyzer.find_support_resistance_levels(price_data, volume_data)

        if 'sector_data' in market_data.columns:
            rotation = self.rotation_analyzer.analyze_rotation_pattern(
                market_data['sector_data']
            )
        else:
            rotation = None

        structure_type = self.identify_structure_type(
            price_data, volume_data, sr_levels
        )

        overall_signal = self.synthesize_structure_signals(
            force_balance, sr_levels, structure_type, rotation
        )

        return {
            'force_balance': force_balance,
            'support_resistance': sr_levels,
            'structure_type': structure_type,
            'rotation': rotation,
            'overall_signal': overall_signal
        }

    def identify_structure_type(self, price_data: pd.Series,
                               volume_data: pd.Series,
                               sr_levels: dict) -> dict:
        """
        识别市场结构类型
        """
        current_price = price_data.iloc[-1]
        ma20 = price_data.rolling(20).mean().iloc[-1]
        ma60 = price_data.rolling(60).mean().iloc[-1]

        if current_price > ma20 > ma60:
            trend_direction = '上涨'
        elif current_price < ma20 < ma60:
            trend_direction = '下跌'
        else:
            trend_direction = '震荡'

        volatility = price_data.rolling(20).std().iloc[-1] / price_data.rolling(20).mean().iloc[-1]

        if volatility > 0.03:
            volatility_level = '高波动'
        elif volatility > 0.015:
            volatility_level = '中波动'
        else:
            volatility_level = '低波动'

        strongest_resistance = sr_levels['阻力位'][0] if sr_levels['阻力位'] else None
        strongest_support = sr_levels['支撑位'][0] if sr_levels['支撑位'] else None

        return {
            'trend_direction': trend_direction,
            'volatility': volatility_level,
            'volatility_value': round(volatility * 100, 2),
            'nearest_resistance': strongest_resistance,
            'nearest_support': strongest_support,
            'market_position': self.calc_market_position(
                current_price, strongest_support, strongest_resistance
            )
        }

    def calc_market_position(self, current: float, support: dict,
                           resistance: dict) -> str:
        """
        计算市场当前位置
        """
        if support is None or resistance is None:
            return '位置不明'

        support_level = support.get('level', 0)
        resistance_level = resistance.get('level', 0)

        if support_level == 0 or resistance_level == 0:
            return '位置不明'

        position = (current - support_level) / (resistance_level - support_level)

        if position > 0.8:
            return '接近阻力'
        elif position < 0.2:
            return '接近支撑'
        else:
            return '中间位置'

    def synthesize_structure_signals(self, force_balance: dict,
                                    sr_levels: dict,
                                    structure_type: dict,
                                    rotation: dict) -> dict:
        """
        综合市场结构信号
        """
        bullish_score = 0
        bearish_score = 0

        if force_balance['balance'] in ['多头主导', '偏多']:
            bullish_score += 2
        elif force_balance['balance'] in ['空头主导', '偏空']:
            bearish_score += 2

        position = structure_type.get('market_position', '')
        if position == '接近支撑':
            bullish_score += 1
        elif position == '接近阻力':
            bearish_score += 1

        if structure_type['trend_direction'] == '上涨':
            bullish_score += 1
        elif structure_type['trend_direction'] == '下跌':
            bearish_score += 1

        if rotation and rotation['pattern'] in ['慢速轮动']:
            bullish_score += 1

        if bullish_score > bearish_score + 2:
            signal = '积极做多'
        elif bullish_score > bearish_score:
            signal = '谨慎看多'
        elif bearish_score > bullish_score + 2:
            signal = '规避风险'
        elif bearish_score > bullish_score:
            signal = '谨慎看空'
        else:
            signal = '中性观望'

        return {
            'signal': signal,
            'bullish_score': bullish_score,
            'bearish_score': bearish_score,
            'confidence': '高' if abs(bullish_score - bearish_score) > 2 else '中'
        }
```

---

## 6. 博弈策略建议

```python
class GameTheoryStrategy:
    """
    博弈策略建议
    """

    def generate_strategy(self, evaluation: dict) -> dict:
        """
        根据市场结构评估生成策略建议

        参数:
            evaluation: 综合评估结果

        返回:
            strategy: 策略建议
        """
        signal = evaluation['overall_signal']['signal']

        if '做多' in signal:
            return self.bullish_strategy(evaluation)
        elif '规避' in signal or '看空' in signal:
            return self.bearish_strategy(evaluation)
        else:
            return self.neutral_strategy(evaluation)

    def bullish_strategy(self, evaluation: dict) -> dict:
        """
        多头策略
        """
        sr = evaluation['support_resistance']
        structure = evaluation['structure_type']

        return {
            'strategy_type': '多头策略',
            'entry_conditions': [
                '回调至支撑位买',
                '缩量回踩均线买',
                '突破阻力位追'
            ],
            'position_management': {
                'initial_position': 0.3,
                'add_on_pullback': 0.2,
                'max_position': 0.7
            },
            'stop_loss': {
                'level': sr['支撑位'][-1]['level'] if sr['支撑位'] else None,
                'risk_per_trade': 0.03
            },
            'key_observations': [
                f"当前位于{sr['强弱分界']}附近",
                f"趋势{sructure['trend_direction']}"
            ]
        }

    def bearish_strategy(self, evaluation: dict) -> dict:
        """
        空头策略
        """
        return {
            'strategy_type': '防守策略',
            'entry_conditions': [
                '禁止追高',
                '只考虑超跌反弹',
                '快进快出'
            ],
            'position_management': {
                'initial_position': 0.1,
                'max_position': 0.3
            },
            'stop_loss': {
                'level': None,
                'risk_per_trade': 0.015
            },
            'key_observations': [
                '降低仓位控制风险',
                '等待市场企稳信号'
            ]
        }

    def neutral_strategy(self, evaluation: dict) -> dict:
        """
        中性策略
        """
        return {
            'strategy_type': '中性策略',
            'entry_conditions': [
                '只在支撑位买',
                '只在阻力位卖',
                '不做突破尝试'
            ],
            'position_management': {
                'initial_position': 0.2,
                'max_position': 0.4
            },
            'key_observations': [
                '震荡格局，高抛低吸',
                '设置严格止损'
            ]
        }
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 新建市场结构博弈文档 |
