# T.04.EX004.盘前计划与买入模式

> 盘前计划校准 + 买入模式分类量化

## 1. 盘前计划吻合度评估

### 1.1 评估结果分类

| 评估结果 | 情形 | 应对策略 |
|----------|------|----------|
| **完全吻合** | 竞价结果与预期一致 | 按计划执行 |
| **部分吻合** | 竞价偏离预期 | 调整策略参数，降低仓位 |
| **完全背离** | 竞价与预期相反 | 放弃原计划，观察等待 |

### 1.2 计划调整决策

| 决策类型 | 条件 | 动作 |
|----------|------|------|
| 降级 | 预期偏高 | 适当降低仓位 |
| 维持 | 预期准确 | 按原计划执行 |
| 放弃 | 市场根本性改变 | 暂不操作 |

```python
class PreMarketPlanCalibrator:
    """盘前计划校准器"""

    def __init__(self):
        self.match_thresholds = {
            'full_match': 0.8,
            'partial_match': 0.5,
        }

    def evaluate_match(self, expected_data, actual_auction_data):
        """
        评估吻合度
        """
        change_diff = abs(expected_data['expected_change'] - actual_auction_data['auction_change'])
        volume_diff = abs(expected_data['expected_volume'] - actual_auction_data['auction_volume']) / expected_data['expected_volume']

        match_score = 1 - (change_diff + volume_diff) / 2

        if match_score >= self.match_thresholds['full_match']:
            return {'result': '完全吻合', 'action': '按计划执行', 'score': match_score}
        elif match_score >= self.match_thresholds['partial_match']:
            return {'result': '部分吻合', 'action': '降低仓位', 'score': match_score}
        else:
            return {'result': '完全背离', 'action': '放弃计划', 'score': match_score}

    def adjust_plan(self, original_plan, match_result, market_data):
        """
        调整计划
        """
        if match_result['result'] == '完全吻合':
            return original_plan

        elif match_result['result'] == '部分吻合':
            adjusted_plan = original_plan.copy()
            adjusted_plan['position'] *= 0.5
            adjusted_plan['note'] = '降低仓位执行'
            return adjusted_plan

        else:
            return {'action': '观望', 'position': 0, 'note': '市场根本性改变'}
```

***

## 2. 突发机会应急评估

### 2.1 机会类型判断

| 机会类型 | 信号特征 | 应对 |
|----------|----------|------|
| **真机会** | 放量突破 + 板块共振 + 机构资金点火 | 可轻仓参与 |
| **假机会** | 缩量拉升 + 孤军深入 + 逆势上涨 | 拒绝参与 |

```python
class OpportunityEvaluator:
    """突发机会评估"""

    def __init__(self):
        self.true_opportunity_signals = {
            'volume_breakout': True,
            'sector_resonance': True,
            'institutional_fire': True,
        }
        self.fake_opportunity_signals = {
            'thin_rally': True,
            'isolated': True,
            'contrarian': True,
        }

    def evaluate_opportunity(self, stock_data, market_data):
        """
        评估机会类型
        """
        true_score = 0
        fake_score = 0

        if stock_data.get('成交量') > stock_data.get('均量') * 1.5:
            true_score += 0.3

        if stock_data.get('板块共振', False):
            true_score += 0.3

        if stock_data.get('机构资金点火', False):
            true_score += 0.4

        if stock_data.get('成交量') < stock_data.get('均量'):
            fake_score += 0.3

        if stock_data.get('孤军深入', False):
            fake_score += 0.3

        if stock_data.get('逆势上涨', False):
            fake_score += 0.4

        if true_score > fake_score and true_score >= 0.6:
            return {
                'type': '真机会',
                'action': '可轻仓参与',
                'score': true_score,
                'position': 0.10
            }
        else:
            return {
                'type': '假机会',
                'action': '拒绝参与',
                'score': fake_score,
                'position': 0
            }
```

***

## 3. 开盘后整体战术决策

### 3.1 战术类型

| 战术类型 | 适用情形 | 执行条件 |
|----------|----------|----------|
| 低吸战术 | 价格回调至关键支撑位 | 支撑位企稳 |
| 突破战术 | 价格突破关键阻力位 | 放量突破确认 |
| 观望战术 | 市场方向不明 | 等待方向明确 |

```python
class OpeningTacticsDecision:
    """开盘后战术决策"""

    def __init__(self):
        self.tactics = {
            '低吸': {
                'condition': '价格回调至支撑位',
                'execution': '支撑位企稳确认'
            },
            '突破': {
                'condition': '价格突破阻力位',
                'execution': '放量突破确认'
            },
            '观望': {
                'condition': '市场方向不明',
                'execution': '等待方向明确'
            }
        }

    def make_decision(self, stock_data, market_data):
        """
        做出战术决策
        """
        support_level = stock_data.get('支撑位', 0)
        resistance_level = stock_data.get('阻力位', 0)
        current_price = stock_data['close']

        if current_price <= support_level * 1.02 and current_price >= support_level * 0.98:
            if self.check_support_stability(stock_data):
                return {
                    'tactic': '低吸',
                    'action': '支撑位企稳买入',
                    'entry_price': current_price,
                    'stop_loss': support_level * 0.97
                }

        if current_price >= resistance_level * 0.98 and current_price <= resistance_level * 1.02:
            if self.check_breakout_confirmation(stock_data):
                return {
                    'tactic': '突破',
                    'action': '放量突破买入',
                    'entry_price': current_price,
                    'stop_loss': resistance_level * 0.97
                }

        return {
            'tactic': '观望',
            'action': '等待方向明确',
            'entry_price': None,
            'stop_loss': None
        }

    def check_support_stability(self, stock_data):
        """
        检查支撑位稳定性
        """
        return stock_data.get('成交量') > stock_data.get('均量') * 1.2

    def check_breakout_confirmation(self, stock_data):
        """
        检查突破确认
        """
        return (
            stock_data.get('成交量') > stock_data.get('均量') * 1.5 and
            stock_data.get('涨幅') > 0.03
        )
```

***

## 4. 买入模式分类

### 4.1 突破模式

| 特征 | 确认信号 | 风险控制 |
|------|----------|----------|
| 价格突破关键阻力位 | 放量突破 + 涨幅>3% | 缩量突破需谨慎 |
| 突破后回踩 | 回踩缩量 + 守住支撑 | 放量下跌止损 |

### 4.2 回调模式

| 特征 | 确认信号 | 风险控制 |
|------|----------|----------|
| 价格回踩支撑位 | 缩量回踩 + 企稳 | 放量下跌止损 |
| 分时均线回踩 | 回踩缩量 + 均线企稳 | 跌破均线止损 |

### 4.3 竞价弱转强模式

| 特征 | 确认信号 | 风险控制 |
|------|----------|----------|
| 竞价弱势但开盘后快速拉升 | 机构逆势吸筹信号 | 拉升太快不追 |
| 竞价低开但开盘后上涨 | 洗盘后的拉升 | 跌破竞价价止损 |

### 4.4 分时突破模式

| 特征 | 确认信号 | 风险控制 |
|------|----------|----------|
| 分时均线下方起量突破 | 突破时放量 | 假突破需止损 |

```python
class BuyPatternClassifier:
    """买入模式分类器"""

    def __init__(self):
        self.patterns = {
            '突破': {
                'min_change': 0.03,
                'min_volume_ratio': 1.5,
            },
            '回调': {
                'max_volume_ratio': 0.8,
            },
            '竞价弱转强': {
                'max_open_change': -0.02,
            },
            '分时突破': {
                'min_volume_ratio': 1.3,
            }
        }

    def classify_pattern(self, stock_data):
        """
        分类买入模式
        """
        patterns = []

        if self.is_breakout_pattern(stock_data):
            patterns.append({
                'pattern': '突破',
                'confidence': self.calculate_breakout_confidence(stock_data)
            })

        if self.is_pullback_pattern(stock_data):
            patterns.append({
                'pattern': '回调',
                'confidence': self.calculate_pullback_confidence(stock_data)
            })

        if self.is_auction_reversal_pattern(stock_data):
            patterns.append({
                'pattern': '竞价弱转强',
                'confidence': self.calculate_auction_reversal_confidence(stock_data)
            })

        if self.is_minute_breakout_pattern(stock_data):
            patterns.append({
                'pattern': '分时突破',
                'confidence': self.calculate_minute_breakout_confidence(stock_data)
            })

        return sorted(patterns, key=lambda x: x['confidence'], reverse=True)

    def is_breakout_pattern(self, stock_data):
        """
        突破模式识别
        """
        params = self.patterns['突破']
        return (
            stock_data.get('涨幅', 0) > params['min_change'] and
            stock_data.get('成交量') > stock_data.get('均量') * params['min_volume_ratio']
        )

    def is_pullback_pattern(self, stock_data):
        """
        回调模式识别
        """
        params = self.patterns['回调']
        return (
            stock_data.get('成交量') < stock_data.get('均量') * params['max_volume_ratio'] and
            stock_data.get('回踩支撑', False)
        )

    def is_auction_reversal_pattern(self, stock_data):
        """
        竞价弱转强模式识别
        """
        params = self.patterns['竞价弱转强']
        auction_change = stock_data.get('竞价涨幅', 0)
        return (
            auction_change < params['max_open_change'] and
            stock_data.get('开盘后拉升', False)
        )

    def is_minute_breakout_pattern(self, stock_data):
        """
        分时突破模式识别
        """
        params = self.patterns['分时突破']
        return (
            stock_data.get('分时突破', False) and
            stock_data.get('成交量') > stock_data.get('均量') * params['min_volume_ratio']
        )
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合盘前计划校准、突发机会评估、开盘战术决策、买入模式分类 |
