---
module_id: TACTICS_YOUZI_OTHER_I_001
version: 1.7.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
responsibility:
  - 交易策略、战术执行
  - 交易执行
  - 数据源
standard_type: 专业量化机构文档
applicable_scope: 全系�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?---


# retail-strategies-i.md
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


# 游资策略补充 (S068-S075)

> 遗漏内容整合补充第二部分
>
> **版本**：v1.7
> **日期**�?026-03-28
> **策略�?*：清风量化交易系�?.0
>
> **配套文档**�?
> - [retail-strategies-h.md](./retail-strategies-h.md) - S059-S067
> -  - 交易规则

---

## 1. 龙飞虎动态仓位管�?(S068)

> 来源：附录BD
>
> 动态仓位管理策�?

### 1.1 仓位计算核心

```python
class DragonFlyTigerPosition:
    """
    龙飞虎动态仓位管�?
    核心：收盘持�?-6成仓位，动态仓�?成上�?
    """

    def calc_position(self, market_open_performance, old_positions, new_signals):
        """
        计算仓位
        """
        base_position = 0.5

        if market_open_performance == 'strong':
            morning_position = 0.8
        elif market_open_performance == 'weak':
            morning_position = 0.3
        else:
            morning_position = 0.5

        old_position_value = self.process_old_positions(old_positions)
        new_position = self.calc_new_position(new_signals, morning_position)

        return {
            'total_position': min(old_position_value + new_position, 1.0),
            'old_position': old_position_value,
            'new_position': new_position,
            'cash_reserve': 1.0 - min(old_position_value + new_position, 1.0)
        }

    def process_old_positions(self, old_positions):
        """
        处理老仓
        """
        total_old = 0
        for pos in old_positions:
            if pos.get('profit_ratio', 0) > 0.05:
                total_old += pos['position'] * 0.8
            elif pos.get('profit_ratio', 0) > 0:
                total_old += pos['position'] * 0.5
            else:
                total_old += pos['position'] * 0.3
        return min(total_old, 0.6)

    def calc_new_position(self, new_signals, morning_position):
        """
        计算新仓
        """
        if not new_signals:
            return 0

        strong_signals = [s for s in new_signals if s.get('signal_strength', 0) >= 0.7]
        return min(len(strong_signals) * 0.1, morning_position)
```

---

## 2. 赵老哥龙头战法 (S069)

> 来源：附录BE
>
> 二板定龙头策�?

### 2.1 二板定龙头量�?

```python
class SecondBoardDragon:
    """
    二板定龙�?
    核心：一板能看出来个毛，二板才是确认
    """

    def select_second_board(self, yesterday_first_board_stocks):
        """
        从昨日首板中选取二板候�?
        """
        candidates = []

        for stock in yesterday_first_board_stocks:
            score = 0

            open_ratio = stock['open_ratio']
            if 0.03 <= open_ratio <= 0.07:
                score += 0.3
            elif open_ratio > 0.07:
                score += 0.1

            if stock['lowest_price'] > stock['yesterday_high'] * 0.80:
                score += 0.25

            if stock['封板时间'] <= '10:00':
                score += 0.25

            if stock['same_theme_first_board'] >= 1:
                score += 0.2

            if score >= 0.7:
                candidates.append({'stock': stock, 'score': score})

        return sorted(candidates, key=lambda x: x['score'], reverse=True)
```

### 2.2 新题材判断量�?

```python
class NewThemeQuantifier:
    """
    新题材判断量�?
    """

    def identify_new_theme(self, market_data, today_turnover):
        """
        判断是否是新题材
        """
        has_story = self.check_theme_story(market_data)
        has_capital = today_turnover > 1000000000
        has_recognition = self.check_plate_recognition(market_data)

        if has_story and has_capital and has_recognition:
            return {
                'is_new_theme': True,
                'confidence': (has_story + has_capital + has_recognition) / 3,
                'action': '积极关注'
            }

        return {
            'is_new_theme': False,
            'confidence': 0,
            'action': '观望'
        }

    def check_theme_story(self, market_data):
        """
        检查是否有重大故事
        """
        story_indicators = ['政策利好', '业绩拐点', '并购重组', '技术突�?]
        return any(indicator in market_data.get('主题', '') for indicator in story_indicators)

    def check_plate_recognition(self, market_data):
        """
        检查板块认同度
        """
        return market_data.get('板块涨停�?, 0) >= 3
```

---

## 3. 艾琳心法量化 (S070)

> 来源：附录BF
>
> 股指期货日内交易系统

### 3.1 策略核心量化

```python
class AilinCoreStrategy:
    """
    艾琳心法核心策略
    操作对象：股指期货主力合�?
    """

    def __init__(self):
        self.max_position = 0.3
        self.profit_target = 0.015
        self.stop_loss = 0.005
        self.trading_hours = ['09:30-11:30', '13:00-15:00']

    def generate_signals(self, minute_data):
        """
        生成日内交易信号
        """
        signals = []

        ma5 = minute_data['close'].rolling(5).mean()
        ma20 = minute_data['close'].rolling(20).mean()

        current = minute_data['close'].iloc[-1]

        if current > ma5.iloc[-1] > ma20.iloc[-1]:
            signals.append({
                'action': 'long',
                'reason': '多头排列',
                'entry': current
            })
        elif current < ma5.iloc[-1] < ma20.iloc[-1]:
            signals.append({
                'action': 'short',
                'reason': '空头排列',
                'entry': current
            })

        return signals

    def execute_trade(self, signal, current_price):
        """
        执行交易
        """
        if signal['action'] == 'long':
            entry = signal['entry']
            if current_price >= entry * (1 + self.profit_target):
                return {'action': '平仓', 'reason': '止盈'}
            if current_price <= entry * (1 - self.stop_loss):
                return {'action': '平仓', 'reason': '止损'}
        return {'action': '持有'}
```

---

## 4. 独股一箭超短线 (S071)

> 来源：附录BG
>
> 超短线操作体�?

### 4.1 超短线核�?

```python
class SingleStockArrow:
    """
    独股一箭超短线
    核心：尾盘选股，次日开盘卖
    """

    def select_overnight_stocks(self, market_data):
        """
        尾盘选股
        """
        candidates = []

        for stock in market_data:
            score = 0

            if stock['change_pct'] >= 3 and stock['change_pct'] <= 8:
                score += 0.3

            if stock['volume_ratio'] >= 1.5:
                score += 0.2

            if stock['close'] > stock['ma5']:
                score += 0.2

            if stock['turnover_rate'] >= 10:
                score += 0.15

            if stock['突破阻力�?]:
                score += 0.15

            if score >= 0.6:
                candidates.append({'stock': stock, 'score': score})

        return sorted(candidates, key=lambda x: x['score'], reverse=True)[:10]

    def execute_next_day(self, stock, open_price):
        """
        次日开盘执�?
        """
        if open_price > stock['收盘�?] * 1.03:
            return {'action': '卖出', 'reason': '高开止盈'}

        if open_price < stock['收盘�?] * 0.97:
            return {'action': '卖出', 'reason': '低开止损'}

        return {'action': '持有观望'}
```

---

## 5. 泽熙/徐翔量化 (S072)

> 来源：附录BH
>
> 泽熙投资理念量化

### 5.1 绝对收益量化

```python
class ZexiAbsoluteReturnQuantifier:
    """
    泽熙绝对收益量化
    泽熙考核：推荐股票要能涨，最好马上涨，涨幅要高过沪深300
    """

    ASSESSMENT_CRITERIA = {
        'price_movement': '推荐的股票要能涨',
        'speed': '最好马上涨',
        'vs_benchmark': '涨幅要高过沪�?00',
        'max_drawdown': '买入后不能下跌超�?0%',
        'stop_loss': '否则无条件止�?,
        'no_add': '不允许补�?
    }

    def evaluate_recommendation(self, stock_return, benchmark_return, max_drawdown):
        """
        评估荐股表现
        """
        vs_benchmark = stock_return - benchmark_return

        if stock_return > 0 and vs_benchmark > 0 and max_drawdown <= 0.1:
            return {'rating': '优秀', 'score': 100}
        elif stock_return > 0 and vs_benchmark > 0:
            return {'rating': '良好', 'score': 80}
        elif max_drawdown > 0.1:
            return {'rating': '不合�?, 'score': 30}
        else:
            return {'rating': '不合�?, 'score': 20}

    def apply_stop_loss(self, entry_price, current_price):
        """
        止损执行
        不允许补�?
        """
        drawdown = (current_price - entry_price) / entry_price

        if drawdown <= -0.1:
            return {'action': '无条件止�?, 'allow_add': False}
        elif drawdown <= -0.05:
            return {'action': '考虑止损', 'allow_add': False}

        return {'action': '持有'}
```

### 5.2 逆向思维量化

```python
class ZexiReverseThinkingQuantifier:
    """
    泽熙逆向思维量化
    市场最热门时要警惕，别人贪婪我恐惧
    """

    def detect_reverse_timing(self, market_data):
        """
        检测逆向时机
        """
        signals = []

        if market_data.get('最热门板块涨幅', 0) > 8:
            signals.append('市场最热门板块涨幅过大，警�?)

        if market_data.get('涨停家数', 0) > 200:
            signals.append('涨停满屏，心生寒�?)

        if market_data.get('市场报告一致�?, 0) > 0.8:
            signals.append('市场报告一片看好，警惕顶部')

        return signals
```

---

## 6. 著名刺客量化 (S073)

> 来源：附录BI
>
> 著名刺客实盘量化经验

### 6.1 情绪逆转大长�?

```python
class AssassinEmotionReversal:
    """
    情绪逆转大长�?
    条件：主�?人气核心+情绪波动
    """

    def select_emotion_reversal_stock(self, market_data, hot_stocks):
        """
        情绪逆转大长腿选股
        """
        candidates = []

        for stock in hot_stocks:
            score = 0

            if stock['is_main_line']:
                score += 0.3

            if stock['popularity_rank'] <= 10:
                score += 0.3

            if stock['today_low'] < stock['yesterday_close'] * 0.95 and \
               stock['current_price'] > stock['today_open']:
                score += 0.4

            if score >= 0.7:
                candidates.append({'stock': stock, 'score': score})

        return sorted(candidates, key=lambda x: x['score'], reverse=True)

    def execute_buy(self, stock):
        """
        买点
        水下低位承接、分时底背离、放量拉升瞬�?
        """
        buy_signals = {
            '水下低位承接': stock['current_price'] < stock['yesterday_close'],
            '分时底背�?: self.check_divergence(stock),
            '放量拉升': stock['volume'] > stock['avg_volume'] * 1.5
        }

        if buy_signals['水下低位承接'] and buy_signals['分时底背�?]:
            return {'action': '买入', 'entry': stock['current_price']}

        if buy_signals['放量拉升']:
            return {'action': '买入', 'entry': stock['current_price']}

        return {'action': '观望'}

    def check_divergence(self, stock):
        """
        检查分时底背离
        """
        return stock.get('分时底背�?, False)
```

### 6.2 连板战法

```python
class AssassinConsecutiveBoard:
    """
    连板战法
    """

    TECHNIQUES = {
        '换手连板': {'投入资金�?, '高换手率'},
        '缩量�?: {'投入资金�?, '缩量'},
        'principle': '只做超强势股'
    }

    def select_consecutive_board(self, stocks):
        """
        选择连板�?
        """
        candidates = []

        for stock in stocks:
            if stock['连续涨停天数'] >= 2:
                candidates.append({
                    'stock': stock,
                    'board_type': '换手连板' if stock['换手�?] > 0.15 else '缩量�?
                })

        return sorted(candidates, key=lambda x: x['stock']['连续涨停天数'], reverse=True)
```

---

## 7. 万狮虎养家心�?(S074)

> 来源：附录BL
>
> 养家心法量化

### 7.1 养家核心心法

```python
class YangjiaMindQuantifier:
    """
    养家心法量化
    """

    def analyze_market_emotion(self, market_data):
        """
        分析市场情绪
        """
        emotion_level = 50

        up_count = market_data.get('上涨家数', 0)
        down_count = market_data.get('下跌家数', 0)
        limit_up = market_data.get('涨停家数', 0)

        if limit_up > 100:
            emotion_level = 80
        elif limit_up > 50:
            emotion_level = 65
        elif up_count > down_count * 1.5:
            emotion_level = 60
        elif down_count > up_count * 1.5:
            emotion_level = 30

        return {
            'emotion_level': emotion_level,
            'suggestion': self.get_suggestion(emotion_level)
        }

    def get_suggestion(self, emotion_level):
        """
        根据情绪获取建议
        """
        if emotion_level >= 70:
            return '积极做多，重仓龙�?
        elif emotion_level >= 50:
            return '稳健操作，控制仓�?
        elif emotion_level >= 30:
            return '谨慎观望，减少操�?
        else:
            return '空仓等待，避免抄�?

    def select_main_line_stocks(self, stocks, market_data):
        """
        选择主线热点
        """
        main_line_stocks = [s for s in stocks if s.get('is_main_line', False)]

        return sorted(main_line_stocks,
                      key=lambda x: x.get('popularity_score', 0),
                      reverse=True)
```

---

## 8. 职业炒手量化 (S075)

> 来源：附录BR
>
> 职业炒手/王元杰量�?

### 8.1 职业炒手核心

```python
class ProfessionalTraderQuantifier:
    """
    职业炒手量化
    """

    def select_high_probability_stocks(self, market_data):
        """
        选取高胜率股�?
        """
        candidates = []

        for stock in market_data:
            score = 0

            if stock['涨幅'] >= 5 and stock['涨幅'] <= 9:
                score += 0.25

            if stock['成交�?] > stock['均量'] * 2:
                score += 0.2

            if stock['封板时间'] <= '10:30':
                score += 0.2

            if stock['换手�?] >= 10:
                score += 0.15

            if stock['属于主线板块']:
                score += 0.2

            if score >= 0.6:
                candidates.append({'stock': stock, 'score': score})

        return sorted(candidates, key=lambda x: x['score'], reverse=True)

    def execute_buy(self, stock):
        """
        买入执行
        """
        if stock['开盘涨�?] > 5:
            return {
                'action': '等待回调买入',
                'wait_for': '回调�?3%左右',
                'max_entry': stock['昨日收盘'] * 1.05
            }

        if -2 <= stock['开盘涨�?] <= 5:
            return {
                'action': '开盘买�?,
                'entry': stock['当前价格']
            }

        return {'action': '观望'}

    def execute_sell(self, stock):
        """
        卖出执行
        """
        if stock['封板失败']:
            return {'action': '立即卖出', 'reason': '封板失败'}

        if stock['持仓收益'] >= 0.07:
            return {'action': '止盈', 'reason': '达到7%收益'}

        if stock['持仓收益'] <= -0.03:
            return {'action': '止损', 'reason': '亏损3%'}

        return {'action': '持有'}
```

---

## 9. 综合交易清单 (S076)

> 来源：附录BK
>
> 综合选股/买入/卖出/仓位清单

### 9.1 选股量化清单

```python
class StockSelectionChecklist:
    """
    选股量化清单
    """

    BASIC_CONDITIONS = {
        '涨幅要求': ('>', 0.07, '放量阳线'),
        '成交量要�?: ('>', 1.5, '倍量'),
        '换手率要�?: ('>', 0.05, '5%以上'),
        '封板时间': ('<=', '14:00', '早板优先')
    }

    def check_selection_conditions(self, stock):
        """
        检查选股条件
        """
        checks = {}

        checks['涨幅'] = stock['change_pct'] > 0.07
        checks['量比'] = stock['volume_ratio'] > 1.5
        checks['换手�?] = stock['turnover_rate'] > 0.05
        checks['封板时间'] = stock['封板时间'] <= '14:00'

        passed = sum(checks.values())
        total = len(checks)

        return {
            'passed': passed,
            'total': total,
            'pass_rate': passed / total,
            'all_passed': passed == total
        }

    def select_stocks(self, stock_pool):
        """
        选股
        """
        selected = []

        for stock in stock_pool:
            check = self.check_selection_conditions(stock)
            if check['all_passed'] or check['pass_rate'] >= 0.75:
                selected.append({
                    'stock': stock,
                    'pass_rate': check['pass_rate']
                })

        return sorted(selected, key=lambda x: x['pass_rate'], reverse=True)
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.7 | 2026-03-28 | 新增遗漏策略：龙飞虎仓位(S068)、赵老哥龙头(S069)、艾琳心�?S070)、独股一�?S071)、泽熙量�?S072)、著名刺�?S073)、万狮虎(S074)、职业炒�?S075)、综合清�?S076) |
