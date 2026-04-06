---
module_id: WAVE_TRADING_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 因子计算
  - 交易执行
  - 系统架构
---

---
module_id: TACTICS_WAVE_TRADING_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
responsibility:
  - 因子计算
  - 交易执行
  - 系统架构
standard_type: 专业量化机构文档
applicable_scope: 全系�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?---


# 波段战法
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 波段交易量化体系
>
> **配套文档**�?
> - 主文档：
> - 技术指标：[technical-indicators.md](../99_ARCHIVE/technical-indicators.md)

***

## 1. 波段交易基础

### 1.1 波段划分

| 波段类型 | 量化标准 |
|----------|----------|
| 上升�?| 连续3日低点抬�?|
| 下降�?| 连续3日高点降�?|
| 整理�?| 高点不创新高，低点不创新�?|

***

### 1.2 波段买卖�?

| 买点类型 | 量化标准 |
|----------|----------|
| 低吸�?| 回踩MA5企稳 |
| 回踩�?| 回踩MA10/MA20 |
| 突破�?| 突破前高 |
| 确认�?| 缩量回踩后放量阳�?|

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
            return '上升�?
        elif ma5.iloc[-1] < ma20.iloc[-1] < ma60.iloc[-1]:
            return '下降�?
        else:
            return '整理�?

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
        """检查是否放�?""
        vol_ma5 = df['volume'].rolling(5).mean()
        return df['volume'].iloc[-1] > vol_ma5.iloc[-1] * 1.5
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合波段战法内容 |
