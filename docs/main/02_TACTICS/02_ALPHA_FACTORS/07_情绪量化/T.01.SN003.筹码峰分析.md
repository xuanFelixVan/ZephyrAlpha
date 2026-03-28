# T.01.SN003.筹码峰量化分析

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
| 因子编号 | T.01.SN003 |
| 因子名称 | 筹码峰量化分析 |
| 因子类型 | 情绪类 |
| 计算周期 | 日频 |
| 数据来源 | 成交量分布/持仓成本 |

**核心理念**：通过分析筹码分布结构，识别机构吸筹/派发信号，判断支撑压力位

**适用场景**：判断主力机构动向、识别支撑压力位、量化筹码集中度

***

## 2. 筹码形态分类

### 2.1 四种基本形态

| 形态 | 集中度 | 特征 | 操作建议 |
|------|--------|------|----------|
| 单峰密集 | >80% | 筹码高度集中于某一价格区间 | 突破方向明确，积极操作 |
| 多峰密集 | 50-80% | 筹码分散于多个价格区间 | 震荡行情，高抛低吸 |
| 筹码发散 | <30% | 筹码分散，无明显集中区 | 观望，等待筹码重新聚集 |
| 过渡形态 | 30-50% | 筹码正在转移 | 谨慎，等待形态明确 |

### 2.2 量化判定标准

```python
def detect_pattern(concentration):
    """
    检测筹码形态

    Parameters:
        concentration: 筹码集中度 (0-1)

    Returns:
        形态类型
    """
    if concentration > 0.8:
        return 'single_peak'      # 单峰密集
    elif concentration > 0.5:
        return 'multi_peak'      # 多峰密集
    elif concentration < 0.3:
        return 'diverged'        # 筹码发散
    else:
        return 'transition'       # 过渡形态
```

***

## 3. 量化规则

### 3.1 筹码集中度计算

```python
def calc_concentration(price_distribution, bins=20):
    """
    计算筹码集中度
    使用成交量加权的价格分布
    """
    total_volume = price_distribution['volume'].sum()

    # 计算成交量加权的位置
    weighted_price = (
        price_distribution['price'] * price_distribution['volume']
    ).sum() / total_volume

    # 计算价格分散度
    variance = (
        price_distribution['volume'] *
        (price_distribution['price'] - weighted_price) ** 2
    ).sum() / total_volume

    std_dev = np.sqrt(variance)

    # 集中度 = 1 - 分散系数
    concentration = 1 - (std_dev / weighted_price)

    return {
        'concentration': concentration,
        'weighted_price': weighted_price,
        'std_dev': std_dev,
        'pattern': detect_pattern(concentration)
    }
```

### 3.2 机构动向识别

```python
def detect_main_force(chip_data, price_data):
    """
    检测机构动向
    通过筹码分布变化判断主力行为
    """

    # 形态识别
    pattern = detect_pattern(chip_data['concentration'])

    # 股价涨但低位筹码减少 = 机构拉高派发
    if price_data['trend'] > 0 and chip_data['low_position_ratio'] < 0.3:
        return {
            'signal': '派发',
            'action': '离场',
            'confidence': 0.8,
            'reason': '股价上涨但低位筹码减少，主力派发'
        }

    # 股价跌但高位筹码减少 = 机构打压吸筹
    elif price_data['trend'] < 0 and chip_data['high_position_ratio'] < 0.3:
        return {
            'signal': '吸筹',
            'action': '关注',
            'confidence': 0.8,
            'reason': '股价下跌但高位筹码减少，主力吸筹'
        }

    # 股价横盘但筹码集中度提升 = 机构锁仓
    elif price_data['trend'] == 0 and chip_data['concentration'] > 0.7:
        return {
            'signal': '锁仓',
            'action': '持有',
            'confidence': 0.6,
            'reason': '筹码高度集中，主力锁仓'
        }

    return {
        'signal': '不明',
        'action': '观望',
        'confidence': 0,
        'reason': '无法判断机构动向'
    }
```

### 3.3 支撑压力位计算

```python
def calc_support_resistance(chip_distribution, price):
    """
    计算支撑位和压力位
    基于筹码密集区
    """
    # 找到成交量加权的密集区
    dense_zones = find_dense_zones(chip_distribution)

    current_price = price

    support_levels = []
    resistance_levels = []

    for zone in dense_zones:
        if zone['price'] < current_price:
            support_levels.append(zone)
        else:
            resistance_levels.append(zone)

    return {
        'support_levels': sorted(support_levels, key=lambda x: x['price'], reverse=True),
        'resistance_levels': sorted(resistance_levels, key=lambda x: x['price'])
    }

def find_dense_zones(chip_distribution, threshold=0.1):
    """
    找到筹码密集区
    成交量占比超过阈值的区间
    """
    total_volume = chip_distribution['volume'].sum()
    dense_zones = []

    for i, row in chip_distribution.iterrows():
        ratio = row['volume'] / total_volume
        if ratio > threshold:
            dense_zones.append({
                'price': row['price'],
                'volume': row['volume'],
                'ratio': ratio
            })

    return dense_zones
```

***

## 4. 信号生成

### 4.1 综合信号

```python
def generate_signal(pattern, main_force, price_position):
    """
    生成综合交易信号
    """
    # 单峰密集 + 吸筹信号 = 强烈买入
    if pattern == 'single_peak' and main_force['signal'] == '吸筹':
        return {
            'signal': 'strong_buy',
            'level': 5,
            'action': '买入',
            'confidence': main_force['confidence']
        }

    # 多峰密集 + 派发信号 = 离场
    elif pattern == 'multi_peak' and main_force['signal'] == '派发':
        return {
            'signal': 'sell',
            'level': 1,
            'action': '离场',
            'confidence': main_force['confidence']
        }

    # 筹码发散 = 观望
    elif pattern == 'diverged':
        return {
            'signal': 'neutral',
            'level': 3,
            'action': '观望',
            'confidence': 0
        }

    # 过渡形态 = 谨慎
    elif pattern == 'transition':
        return {
            'signal': 'caution',
            'level': 2,
            'action': '谨慎',
            'confidence': 0.3
        }

    return {
        'signal': 'neutral',
        'level': 3,
        'action': '观望',
        'confidence': 0
    }
```

### 4.2 信号等级

| 信号等级 | 信号类型 | 操作建议 | 条件 |
|----------|----------|----------|------|
| 5 | 强烈买入 | 重仓 | 单峰密集 + 吸筹信号 |
| 4 | 买入 | 轻仓 | 吸筹信号 + 筹码集中度提升 |
| 3 | 中性 | 观望 | 无明确信号 |
| 2 | 谨慎 | 轻仓 | 过渡形态 |
| 1 | 离场 | 清仓 | 派发信号 |

***

## 5. Python实现

```python
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

class ChipPeakQuantifier:
    """
    筹码峰量化分析
    通过筹码分布结构识别主力动向
    """

    def __init__(self):
        self.name = "筹码峰分析"
        self.factor_code = "T.01.SN003"

    def analyze(self, chip_df: pd.DataFrame, price_df: pd.DataFrame) -> Dict:
        """
        分析筹码结构

        Parameters:
            chip_df: 筹码分布数据
                - price: 价格区间
                - volume: 成交量
            price_df: 价格数据
                - close: 收盘价
                - trend: 涨跌幅

        Returns:
            分析结果字典
        """
        if chip_df.empty:
            return {'signal': 'neutral', 'action': '观望', 'reason': '无筹码数据'}

        concentration_info = self._calc_concentration(chip_df)
        main_force = self._detect_main_force(chip_df, price_df)
        support_resistance = self._calc_support_resistance(chip_df, price_df['close'].iloc[-1])
        signal = self._generate_signal(
            concentration_info['pattern'],
            main_force,
            price_df['close'].iloc[-1] / concentration_info['weighted_price'] - 1
        )

        return {
            'factor_code': self.factor_code,
            'factor_name': self.name,
            'concentration': concentration_info['concentration'],
            'pattern': concentration_info['pattern'],
            'main_force': main_force,
            'support_levels': support_resistance['support_levels'],
            'resistance_levels': support_resistance['resistance_levels'],
            **signal,
            'timestamp': pd.Timestamp.now()
        }

    def _calc_concentration(self, chip_df: pd.DataFrame) -> Dict:
        """计算筹码集中度"""
        total_volume = chip_df['volume'].sum()
        if total_volume == 0:
            return {'concentration': 0, 'pattern': 'diverged', 'weighted_price': 0}

        weighted_price = (
            chip_df['price'] * chip_df['volume']
        ).sum() / total_volume

        variance = (
            chip_df['volume'] *
            (chip_df['price'] - weighted_price) ** 2
        ).sum() / total_volume

        std_dev = np.sqrt(variance)
        concentration = 1 - (std_dev / weighted_price) if weighted_price > 0 else 0

        return {
            'concentration': concentration,
            'weighted_price': weighted_price,
            'std_dev': std_dev,
            'pattern': self._detect_pattern(concentration)
        }

    def _detect_pattern(self, concentration: float) -> str:
        """检测筹码形态"""
        if concentration > 0.8:
            return 'single_peak'
        elif concentration > 0.5:
            return 'multi_peak'
        elif concentration < 0.3:
            return 'diverged'
        else:
            return 'transition'

    def _detect_main_force(self, chip_df: pd.DataFrame, price_df: pd.DataFrame) -> Dict:
        """检测机构动向"""
        if len(price_df) < 2:
            return {'signal': '不明', 'action': '观望', 'confidence': 0}

        current_price = price_df['close'].iloc[-1]
        prev_price = price_df['close'].iloc[-2]
        trend = (current_price - prev_price) / prev_price

        # 计算高位/低位筹码比例
        weighted_price = self._calc_concentration(chip_df)['weighted_price']

        high_ratio = chip_df[chip_df['price'] > weighted_price * 1.1]['volume'].sum() / chip_df['volume'].sum()
        low_ratio = chip_df[chip_df['price'] < weighted_price * 0.9]['volume'].sum() / chip_df['volume'].sum()

        # 股价涨但低位筹码减少 = 派发
        if trend > 0 and low_ratio < 0.3:
            return {
                'signal': '派发',
                'action': '离场',
                'confidence': 0.8,
                'reason': '股价上涨但低位筹码减少'
            }

        # 股价跌但高位筹码减少 = 吸筹
        elif trend < 0 and high_ratio < 0.3:
            return {
                'signal': '吸筹',
                'action': '关注',
                'confidence': 0.8,
                'reason': '股价下跌但高位筹码减少'
            }

        # 筹码高度集中 = 锁仓
        concentration = self._calc_concentration(chip_df)['concentration']
        if concentration > 0.7 and abs(trend) < 0.01:
            return {
                'signal': '锁仓',
                'action': '持有',
                'confidence': 0.6,
                'reason': '筹码高度集中'
            }

        return {'signal': '不明', 'action': '观望', 'confidence': 0, 'reason': '无法判断'}

    def _calc_support_resistance(self, chip_df: pd.DataFrame, current_price: float) -> Dict:
        """计算支撑压力位"""
        total_volume = chip_df['volume'].sum()
        dense_zones = chip_df[chip_df['volume'] / total_volume > 0.1]

        support_levels = dense_zones[dense_zones['price'] < current_price].sort_values(
            'price', ascending=False
        )['price'].tolist()

        resistance_levels = dense_zones[dense_zones['price'] > current_price].sort_values(
            'price'
        )['price'].tolist()

        return {
            'support_levels': support_levels[:3],
            'resistance_levels': resistance_levels[:3]
        }

    def _generate_signal(self, pattern: str, main_force: Dict, price_position: float) -> Dict:
        """生成交易信号"""
        if pattern == 'single_peak' and main_force['signal'] == '吸筹':
            return {
                'signal': 'strong_buy',
                'level': 5,
                'action': '买入',
                'confidence': main_force['confidence']
            }
        elif main_force['signal'] == '派发':
            return {
                'signal': 'sell',
                'level': 1,
                'action': '离场',
                'confidence': main_force['confidence']
            }
        elif pattern == 'diverged':
            return {
                'signal': 'neutral',
                'level': 3,
                'action': '观望',
                'confidence': 0
            }
        else:
            return {
                'signal': 'neutral',
                'level': 3,
                'action': '观望',
                'confidence': 0
            }
```

***

## 6. 使用示例

```python
# 筹码分布数据
chip_data = pd.DataFrame({
    'price': [9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0],
    'volume': [1000, 5000, 20000, 15000, 3000, 1000, 500]
})

# 价格数据
price_data = pd.DataFrame({
    'close': [10.2, 10.5, 10.8],
    'trend': [0.02, 0.03, 0.03]
})

# 分析
analyzer = ChipPeakQuantifier()
result = analyzer.analyze(chip_data, price_data)

print(f"形态: {result['pattern']}")
print(f"集中度: {result['concentration']:.2%}")
print(f"信号: {result['action']}")
print(f"主力动向: {result['main_force']['signal']}")
```

***

## 7. 注意事项

1. **数据来源**：筹码数据需要Level2数据或估算数据
2. **估算方法**：可使用成交量分布估算筹码分布
3. **滞后性**：筹码分析有一定滞后性，需结合其他指标
4. **适用场景**：更适合中线操作，短线需结合其他因子

***

## 8. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |
