# T.01.SN002.龙虎榜跟庄量化

> 情绪类Alpha因子
>
> **配套文档**：
> - 主文档：[SPEC.md](../../../../SPEC.md)
> - 因子库索引：[因子库主索引](../../../../../factor-library/04_DATA_SOURCE/因子主索引.md)
> - 情绪量化：[情绪量化 README](./README.md)

***

## 1. 因子概述

| 属性 | 内容 |
|------|------|
| 因子编号 | T.01.SN002 |
| 因子名称 | 龙虎榜跟庄量化 |
| 因子类型 | 情绪类 |
| 计算周期 | 日频 |
| 数据来源 | 龙虎榜数据 |

**核心理念**：通过分析龙虎榜席位资金流向，跟随机构/北向资金操作，规避游资主导的短线风险

**适用场景**：机构重仓股筛选、北向资金跟踪、跟庄操作

***

## 2. 龙虎榜数据结构

### 2.1 数据字段

| 字段 | 类型 | 说明 |
|------|------|------|
| date | str | 交易日期 |
| code | str | 股票代码 |
| name | str | 股票名称 |
| buy_seats | list | 买方席位列表 |
| sell_seats | list | 卖方席位列表 |
| seat_type | str | 席位类型（机构专用/游资/北向） |
| buy_amount | float | 买入金额（万元） |
| sell_amount | float | 卖出金额（万元） |
| net_amount | float | 净买入金额 |

### 2.2 席位分类

```python
SEAT_TYPES = {
    '机构专用': ['机构专用', 'QFII'],
    '北向资金': ['沪股通', '深股通'],
    '顶级游资': ['中信证券', '华泰证券', '国泰君安', '招商证券'],
    '一线游资': ['光大证券', '银河证券', '申万宏源'],
    '普通席位': ['其他券商']
}
```

***

## 3. 量化规则

### 3.1 机构席位分析

```python
def calc_institution_net(data):
    """
    计算机构净买入
    机构席位：机构专用、QFII
    """
    institution_buy = data[
        data['seat_type'] == '机构专用'
    ]['buy_amount'].sum()

    institution_sell = data[
        data['seat_type'] == '机构专用'
    ]['sell_amount'].sum()

    institution_net = institution_buy - institution_sell

    return {
        'institution_buy': institution_buy,
        'institution_sell': institution_sell,
        'institution_net': institution_net,
        'signal': '买入' if institution_net > 0 else '卖出'
    }
```

### 3.2 北向资金分析

```python
def calc_north_net(data):
    """
    计算北向净买入
    北向席位：沪股通、深股通
    """
    north_buy = data[
        data['seat_type'].isin(['沪股通', '深股通'])
    ]['buy_amount'].sum()

    north_sell = data[
        data['seat_type'].isin(['沪股通', '深股通'])
    ]['sell_amount'].sum()

    north_net = north_buy - north_sell

    return {
        'north_buy': north_buy,
        'north_sell': north_sell,
        'north_net': north_net,
        'signal': '买入' if north_net > 0 else '卖出'
    }
```

### 3.3 游资席位分析

```python
def calc_hot_money_net(data):
    """
    计算游资净买入
    游资席位：顶级游资、一线游资
    """
    hot_buy = data[
        data['seat_type'].isin(['顶级游资', '一线游资'])
    ]['buy_amount'].sum()

    hot_sell = data[
        data['seat_type'].isin(['顶级游资', '一线游资'])
    ]['sell_amount'].sum()

    hot_money_net = hot_buy - hot_sell

    return {
        'hot_buy': hot_buy,
        'hot_sell': hot_sell,
        'hot_money_net': hot_money_net,
        'signal': '买入' if hot_money_net > 0 else '卖出'
    }
```

***

## 4. 信号生成

### 4.1 综合信号判定

```python
def generate_signal(institution_net, north_net, hot_money_net):
    """
    生成综合交易信号
    """
    if institution_net > 0 and north_net > 0:
        return {
            'signal': 'strong_buy',
            'level': 5,
            'action': '强烈买入',
            'reason': '机构+北向双买入'
        }

    elif institution_net > 0 and north_net == 0:
        return {
            'signal': 'institution_buy',
            'level': 4,
            'action': '机构买入',
            'reason': '机构单独买入'
        }

    elif institution_net < 0:
        return {
            'signal': 'institution_sell',
            'level': 1,
            'action': '警惕',
            'reason': '机构净卖出'
        }

    elif hot_money_net > institution_net * 2:
        return {
            'signal': 'hot_money_buy',
            'level': 2,
            'action': '短线机会',
            'reason': '游资主导，短线机会'
        }

    else:
        return {
            'signal': 'neutral',
            'level': 3,
            'action': '观望',
            'reason': '无明确信号'
        }
```

### 4.2 信号等级

| 信号等级 | 信号类型 | 操作建议 | 持仓周期 |
|----------|----------|----------|----------|
| 5 | 强烈买入 | 机构+北向双买入 | 5-10天 |
| 4 | 机构买入 | 机构单独买入 | 3-7天 |
| 3 | 中性 | 观望 | - |
| 2 | 短线机会 | 游资主导，快进快出 | 1-3天 |
| 1 | 警惕 | 机构净卖出 | 回避 |

***

## 5. Python实现

```python
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class DragonTigerQuantifier:
    """
    龙虎榜量化跟庄
    通过分析龙虎榜席位资金流向，跟随机构/北向资金
    """

    SEAT_CLASSIFICATION = {
        '机构': ['机构专用', 'QFII', '社保基金', '公募基金'],
        '北向': ['沪股通', '深股通', '北向资金'],
        '顶级游资': [
            '中信证券股份有限公司上海分公司',
            '华泰证券股份有限公司深圳益田路证券营业部',
            '国泰君安证券股份有限公司上海江苏路证券营业部'
        ],
        '一线游资': [
            '光大证券股份有限公司宁波解放南路证券营业部',
            '中国银河证券股份有限公司绍兴证券营业部'
        ]
    }

    def __init__(self):
        self.name = "龙虎榜跟庄"
        self.factor_code = "T.01.SN002"

    def analyze(self, dragon_tiger_df: pd.DataFrame) -> Dict:
        """
        分析龙虎榜数据

        Parameters:
            dragon_tiger_df: 龙虎榜数据DataFrame
                - code: 股票代码
                - date: 交易日期
                - seat_name: 席位名称
                - buy_amount: 买入金额(万元)
                - sell_amount: 卖出金额(万元)

        Returns:
            分析结果字典
        """
        if dragon_tiger_df.empty:
            return {'signal': 'neutral', 'action': '观望', 'reason': '无数据'}

        institution_net = self._calc_institution_net(dragon_tiger_df)
        north_net = self._calc_north_net(dragon_tiger_df)
        hot_money_net = self._calc_hot_money_net(dragon_tiger_df)

        signal_info = self._generate_signal(institution_net, north_net, hot_money_net)

        return {
            'factor_code': self.factor_code,
            'factor_name': self.name,
            'institution_net': institution_net,
            'north_net': north_net,
            'hot_money_net': hot_money_net,
            **signal_info,
            'timestamp': pd.Timestamp.now()
        }

    def _classify_seat(self, seat_name: str) -> str:
        """席位分类"""
        for category, names in self.SEAT_CLASSIFICATION.items():
            if any(name in seat_name for name in names):
                return category
        return '普通席位'

    def _calc_institution_net(self, df: pd.DataFrame) -> float:
        """计算机构净买入"""
        institution_df = df[df['seat_name'].apply(self._classify_seat) == '机构']
        if institution_df.empty:
            return 0.0
        return (institution_df['buy_amount'] - institution_df['sell_amount']).sum()

    def _calc_north_net(self, df: pd.DataFrame) -> float:
        """计算北向净买入"""
        north_df = df[df['seat_name'].apply(self._classify_seat) == '北向']
        if north_df.empty:
            return 0.0
        return (north_df['buy_amount'] - north_df['sell_amount']).sum()

    def _calc_hot_money_net(self, df: pd.DataFrame) -> float:
        """计算游资净买入"""
        hot_df = df[df['seat_name'].apply(
            lambda x: self._classify_seat(x) in ['顶级游资', '一线游资']
        )]
        if hot_df.empty:
            return 0.0
        return (hot_df['buy_amount'] - hot_df['sell_amount']).sum()

    def _generate_signal(self, institution_net: float,
                         north_net: float,
                         hot_money_net: float) -> Dict:
        """生成交易信号"""
        if institution_net > 0 and north_net > 0:
            return {
                'signal': 'strong_buy',
                'level': 5,
                'action': '强烈买入',
                'reason': f'机构净买入{institution_net:.0f}万+北向净买入{north_net:.0f}万'
            }
        elif institution_net > 0:
            return {
                'signal': 'institution_buy',
                'level': 4,
                'action': '机构买入',
                'reason': f'机构净买入{institution_net:.0f}万'
            }
        elif institution_net < 0:
            return {
                'signal': 'caution',
                'level': 1,
                'action': '警惕',
                'reason': f'机构净卖出{-institution_net:.0f}万'
            }
        elif hot_money_net > abs(institution_net) * 2:
            return {
                'signal': 'hot_money_buy',
                'level': 2,
                'action': '短线机会',
                'reason': '游资主导，注意风险'
            }
        else:
            return {
                'signal': 'neutral',
                'level': 3,
                'action': '观望',
                'reason': '无明确信号'
            }
```

***

## 6. 使用示例

```python
# 示例数据
data = {
    'code': ['000001', '000001', '000001'],
    'date': ['2024-01-15', '2024-01-15', '2024-01-15'],
    'seat_name': [
        '机构专用',
        '沪股通',
        '中信证券股份有限公司上海分公司'
    ],
    'buy_amount': [5000, 3000, 2000],
    'sell_amount': [1000, 500, 800]
}

df = pd.DataFrame(data)

# 分析
analyzer = DragonTigerQuantifier()
result = analyzer.analyze(df)

print(f"信号: {result['action']}")
print(f"等级: {result['level']}")
print(f"原因: {result['reason']}")
```

***

## 7. 注意事项

1. **数据延迟**：龙虎榜数据通常T+1日公布，需注意数据时效性
2. **席位识别**：席位名称可能有变体，需维护席位映射表
3. **跟庄风险**：机构买入不一定立即上涨，需结合其他因子
4. **游资风险**：游资主导的股票波动大，适合短线操作

***

## 8. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |
