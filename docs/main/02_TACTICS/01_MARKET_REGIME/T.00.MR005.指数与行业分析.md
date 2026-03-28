# T.00.MR005.指数与行业分析

> 主要指数特征分析与行业优先级量化体系

## 1. 主要指数分析框架

> **来源**：量化策略专业分层方案_v3.0 附录AZ

### 1.1 主要指数特征库

```python
class IndexAnalysisFramework:
    """
    主要指数分析框架
    """

    INDEX_CHARACTERISTICS = {
        '上证指数': {
            'scope': '上交所全部股票',
            'represents': '整体市场',
            '权重行业': ['银行', '白酒', '石油'],
            'analysis_tips': '反映整体市场情绪'
        },
        '深证成指': {
            'scope': '深交所主板',
            'represents': '深圳市场整体',
            '权重行业': ['新能源', '消费电子', '医药']
        },
        '创业板指': {
            'scope': '创业板100只',
            'represents': '成长股市场',
            '权重行业': ['电力设备', '医药', '电子'],
            '风险': '高波动',
            'tips': '高风险高收益，择时重要'
        },
        '科创50': {
            'scope': '科创板50只',
            'represents': '科技创新',
            '权重行业': ['半导体', '软件', '生物医药'],
            '风险': '高波动，政策敏感',
            'tips': '政策驱动明显，需关注政策导向'
        },
        '沪深300': {
            'scope': '市值TOP300',
            'represents': '大盘蓝筹',
            'characteristics': '稳健',
            'tips': '适合资产配置基准'
        },
        '中证500': {
            'scope': '市值301-800名',
            'represents': '中盘股',
            'characteristics': '经济复苏优选',
            'tips': '经济复苏期表现较好'
        },
        '中证1000': {
            'scope': '市值801-1800名',
            'represents': '小盘股',
            'characteristics': '高弹性',
            'tips': '流动性好时表现好'
        }
    }

    def analyze_index(self, index_code, price_data):
        """
        分析指数
        """
        info = self.INDEX_CHARACTERISTICS.get(index_code, {})

        trend = self.calc_trend(price_data)
        volatility = self.calc_volatility(price_data)

        return {
            'index': index_code,
            'scope': info.get('scope'),
            'represents': info.get('represents'),
            'trend': trend,
            'volatility': volatility,
            'suggestion': self.get_suggestion(index_code, trend, volatility)
        }

    def get_suggestion(self, index_code, trend, volatility):
        """
        获取操作建议
        """
        if index_code in ['创业板指', '科创50']:
            if trend == 'down' and volatility > 0.3:
                return '谨慎，等待趋势明朗'
            else:
                return '高风险高收益，择时重要'
        elif index_code in ['沪深300', '中证500']:
            return '稳健型，适合资产配置'
        else:
            return '综合分析，结合板块'

    def calc_trend(self, price_data):
        """计算趋势"""
        if len(price_data) < 20:
            return 'unknown'
        ma5 = price_data['close'].rolling(5).mean()
        ma20 = price_data['close'].rolling(20).mean()
        if ma5.iloc[-1] > ma20.iloc[-1] * 1.02:
            return 'up'
        elif ma5.iloc[-1] < ma20.iloc[-1] * 0.98:
            return 'down'
        return 'sideways'

    def calc_volatility(self, price_data):
        """计算波动率"""
        returns = price_data['close'].pct_change()
        return returns.std() * np.sqrt(252)
```

### 1.2 指数相关性矩阵

```python
INDEX_CORRELATION = {
    ('沪深300', '中证500'): 0.92,
    ('沪深300', '创业板指'): 0.78,
    ('沪深300', '科创50'): 0.65,
    ('中证500', '中证1000'): 0.95,
    ('创业板指', '科创50'): 0.82,
    ('上证指数', '深证成指'): 0.96,
}
```

---

## 2. 行业优先级量化

### 2.1 通胀受益板块优先级

```python
class InflationSectorPriority:
    """
    通胀受益板块优先级
    """

    PRIORITY = {
        '核心配置': {
            '板块': ['石油', '天然气', '煤化工', '农业'],
            '理由': '最安全，要么坚挺要么逆势上涨',
            '权重': 0.8
        },
        '防御配置': {
            '板块': ['电力', '电网', '煤炭发电', '水电'],
            '理由': '防守性强',
            '权重': 0.15
        },
        '回避配置': {
            '板块': ['科技股', '机器人', 'AI算力', '消费'],
            '理由': '高估值+高利率环境风险大',
            '权重': 0.0
        },
        '谨慎配置': {
            '板块': ['消费'],
            '理由': '未到底，没有催化剂',
            '权重': 0.05
        }
    }

    def get_conflict_strategy(self):
        """
        地缘冲突策略
        """
        return {
            'cash_ratio': 0.30,
            'safe_allocation': {
                '石油天然气': 0.25,
                '煤化工': 0.20,
                '农业': 0.20,
                '电力电网': 0.10
            },
            'abandon': ['科技', '机器人', 'AI', '消费', '顺周期']
        }
```

### 2.2 化工细分板块量化

```python
class ChemicalSectorQuantifier:
    """
    化工细分板块量化
    """

    CHEMICAL_OUTLOOK = {
        '煤化工': {'outlook': '正面', 'reason': '预期非常好'},
        '农业化工': {'outlook': '正面', 'reason': '成本转移顺畅'},
        '钛化工': {'outlook': '负面', 'reason': '成本增加，需求差'},
        '有机硅': {'outlook': '负面', 'reason': '成本增加，需求差'},
        '航空炼化': {'outlook': '负面', 'reason': '成本增加，需求不差'}
    }

    def get_sector_signals(self):
        """
        获取板块信号
        """
        signals = []
        for sector, data in self.CHEMICAL_OUTLOOK.items():
            signals.append({
                'sector': sector,
                'outlook': data['outlook'],
                'action': '配置' if data['outlook'] == '正面' else '回避',
                'confidence': 0.7 if data['outlook'] == '正面' else 0.6
            })

        return sorted(signals, key=lambda x: x['confidence'], reverse=True)
```

---

## 3. A股周期性规律

### 3.1 暴跌时间窗口量化

```python
class CrashTimeWindowQuantifier:
    """
    A股四大暴跌时间窗口量化
    """

    TIME_WINDOWS = {
        'december': {
            'period': '12月中下旬',
            'risk_level': 5,
            'reasons': ['年末银行收贷', '机构年终排名', '油资大户年底卸币'],
            'defense': '空仓或轻仓过节',
            'typical_drop': '20-30%'
        },
        'april_end': {
            'period': '4月底',
            'risk_level': 4,
            'reasons': ['年报季报爆雷期', '业绩变脸可能ST退市'],
            'defense': '回避业绩差股票',
            'typical_drop': '10-20%'
        },
        'august_end': {
            'period': '8月底',
            'risk_level': 3,
            'reasons': ['红利兑现期', '利好消化完资金了结'],
            'defense': '关注止盈',
            'typical_drop': '5-15%'
        },
        'october': {
            'period': '10月前后',
            'risk_level': 3,
            'reasons': ['国庆7天休市', '资金避险/消费需求'],
            'defense': '谨慎操作',
            'typical_drop': '5-10%'
        }
    }

    def get_current_window_risk(self, current_date):
        """
        获取当前时间窗口风险
        """
        month = current_date.month
        day = current_date.day

        if month == 12 and day >= 15:
            return self.TIME_WINDOWS['december']
        elif month == 4 and day >= 25:
            return self.TIME_WINDOWS['april_end']
        elif month == 8 and day >= 20:
            return self.TIME_WINDOWS['august_end']
        elif month == 10 and day >= 20:
            return self.TIME_WINDOWS['october']
        else:
            return {'risk_level': 0, 'period': '正常交易期'}

    def adjust_position(self, base_position, risk_info):
        """
        根据时间窗口调整仓位
        """
        risk = risk_info.get('risk_level', 0)

        if risk >= 5:
            return base_position * 0.3
        elif risk >= 4:
            return base_position * 0.5
        elif risk >= 3:
            return base_position * 0.7
        else:
            return base_position
```

---

## 4. 市场环境判断矩阵

### 4.1 五级市场环境分类

```python
class MarketEnvironmentMatrix:
    """
    市场环境判断矩阵
    """

    MATRIX = {
        '强势': {
            '赚钱效应': ('>', 0.6),
            '恐慌效应': ('<', 0.2),
            '操作策略': '追热点',
            '仓位上限': 1.0
        },
        '偏强': {
            '赚钱效应': (0.5, 0.6),
            '恐慌效应': (0.2, 0.3),
            '操作策略': '做龙头',
            '仓位上限': 0.8
        },
        '平衡': {
            '赚钱效应': (0.4, 0.5),
            '恐慌效应': (0.3, 0.4),
            '操作策略': '快进快出',
            '仓位上限': 0.5
        },
        '偏弱': {
            '赚钱效应': (0.3, 0.4),
            '恐慌效应': (0.4, 0.5),
            '操作策略': '控仓超跌',
            '仓位上限': 0.3
        },
        '弱势': {
            '赚钱效应': ('<', 0.3),
            '恐慌效应': ('>', 0.5),
            '操作策略': '等买点',
            '仓位上限': 0.1
        }
    }

    def classify_market(self, profit_ratio, panic_ratio):
        """
        市场分类
        """
        for environment, thresholds in self.MATRIX.items():
            if self.match_thresholds(profit_ratio, panic_ratio, thresholds):
                return {
                    'environment': environment,
                    'strategy': thresholds['操作策略'],
                    'max_position': thresholds['仓位上限']
                }
        return {'environment': '平衡', 'strategy': '快进快出', 'max_position': 0.5}

    def match_thresholds(self, profit_ratio, panic_ratio, thresholds):
        """匹配阈值"""
        profit_thresh = thresholds['赚钱效应']
        panic_thresh = thresholds['恐慌效应']

        if isinstance(profit_thresh, tuple):
            if not (profit_thresh[0] <= profit_ratio <= profit_thresh[1]):
                return False
        elif profit_thresh[0] == '>':
            if profit_ratio <= profit_thresh[1]:
                return False
        elif profit_thresh[0] == '<':
            if profit_ratio >= profit_thresh[1]:
                return False

        if isinstance(panic_thresh, tuple):
            if not (panic_thresh[0] <= panic_ratio <= panic_thresh[1]):
                return False
        elif panic_thresh[0] == '<':
            if panic_ratio >= panic_thresh[1]:
                return False
        elif panic_thresh[0] == '>':
            if panic_ratio <= panic_thresh[1]:
                return False

        return True
```

---

## 5. 综合选股量化模型

### 5.1 短线选股模型

```python
class ComprehensiveStockSelector:
    """
    综合选股量化模型
    """

    def short_term_selection(self, stock_data):
        """
        短线选股（3-10天）
        评分 = 题材热度×0.3 + 资金流入×0.3 + 技术形态×0.2 + 板块效应×0.2
        """
        scores = {}

        scores['theme_hotness'] = self.calc_theme_hotness(stock_data) * 0.3
        scores['capital_inflow'] = self.calc_capital_inflow(stock_data) * 0.3
        scores['tech_pattern'] = self.calc_tech_breakout(stock_data) * 0.2
        scores['sector_effect'] = self.calc_sector_effect(stock_data) * 0.2

        total_score = sum(scores.values())

        return {
            'total_score': total_score,
            'breakdown': scores,
            'action': '买入' if total_score > 0.7 else '观望'
        }

    def band_selection(self, stock_data):
        """
        波段选股（10-30天）
        评分 = 趋势强度×0.3 + 估值优势×0.25 + 机构关注×0.25 + 催化剂×0.2
        """
        scores = {}

        scores['trend_strength'] = self.calc_trend_strength(stock_data) * 0.3
        scores['valuation'] = self.calc_valuation_advantage(stock_data) * 0.25
        scores['institution_attention'] = self.calc_institution_attention(stock_data) * 0.25
        scores['catalyst'] = self.calc_catalyst(stock_data) * 0.2

        total_score = sum(scores.values())

        return {
            'total_score': total_score,
            'breakdown': scores,
            'action': '买入' if total_score > 0.6 else '观望'
        }

    def calc_theme_hotness(self, stock_data):
        """题材热度"""
        return 0.5

    def calc_capital_inflow(self, stock_data):
        """资金流入"""
        return 0.5

    def calc_tech_breakout(self, stock_data):
        """技术突破"""
        return 0.5

    def calc_sector_effect(self, stock_data):
        """板块效应"""
        return 0.5

    def calc_trend_strength(self, stock_data):
        """趋势强度"""
        return 0.5

    def calc_valuation_advantage(self, stock_data):
        """估值优势"""
        return 0.5

    def calc_institution_attention(self, stock_data):
        """机构关注"""
        return 0.5

    def calc_catalyst(self, stock_data):
        """催化剂"""
        return 0.5
```

---

## 6. 输出格式

```json
{
  "指数分析": {
    "主要指数": {
      "沪深300": {"trend": "up", "volatility": 0.15, "suggestion": "稳健配置"},
      "创业板指": {"trend": "sideways", "volatility": 0.28, "suggestion": "谨慎择时"}
    },
    "行业优先级": {
      "通胀受益": ["石油", "天然气", "煤化工", "农业"],
      "回避": ["科技股", "机器人", "AI算力"]
    }
  },
  "周期风险": {
    "当前窗口": "正常交易期",
    "风险等级": 0
  },
  "市场环境": {
    "分类": "平衡",
    "仓位上限": 0.5,
    "操作策略": "快进快出"
  }
}
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合附录AZ/AR/AS指数分析、板块轮动、周期规律 |
