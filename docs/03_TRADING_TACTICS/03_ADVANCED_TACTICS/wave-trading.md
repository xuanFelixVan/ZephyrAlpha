# 波段战法

> 波段交易量化体系
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 技术指标：[technical-indicators.md](./technical-indicators.md)

***

## 1. 波段交易基础

### 1.1 波段划分

| 波段类型 | 量化标准 |
|----------|----------|
| 上升浪 | 连续3日低点抬高 |
| 下降浪 | 连续3日高点降低 |
| 整理浪 | 高点不创新高，低点不创新低 |

***

### 1.2 波段买卖点

| 买点类型 | 量化标准 |
|----------|----------|
| 低吸点 | 回踩MA5企稳 |
| 回踩点 | 回踩MA10/MA20 |
| 突破点 | 突破前高 |
| 确认点 | 缩量回踩后放量阳线 |

***

## 2. Python实现

```python
class WaveTrading:
    """波段交易系统"""

    def __init__(self):
        self.trend_ma = [5, 20, 60]

    def identify_wave(self, df):
        """识别当前波段"""
        ma5 = df['close'].rolling(5).mean()
        ma20 = df['close'].rolling(20).mean()
        ma60 = df['close'].rolling(60).mean()

        if ma5.iloc[-1] > ma20.iloc[-1] > ma60.iloc[-1]:
            return '上升浪'
        elif ma5.iloc[-1] < ma20.iloc[-1] < ma60.iloc[-1]:
            return '下降浪'
        else:
            return '整理浪'

    def get_buy_signal(self, df):
        """获取买入信号"""
        ma5 = df['close'].rolling(5).mean()
        ma20 = df['close'].rolling(20).mean()

        if df['close'].iloc[-1] > ma5.iloc[-1] and ma5.iloc[-1] > ma20.iloc[-1]:
            if self.check_volume_surge(df):
                return {'signal': '买入', 'type': '突破买入'}

        if abs(df['close'].iloc[-1] - ma20.iloc[-1]) / ma20.iloc[-1] < 0.02:
            return {'signal': '买入', 'type': '回踩买入'}

        return None

    def check_volume_surge(self, df):
        """检查是否放量"""
        vol_ma5 = df['volume'].rolling(5).mean()
        return df['volume'].iloc[-1] > vol_ma5.iloc[-1] * 1.5
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合波段战法内容 |
