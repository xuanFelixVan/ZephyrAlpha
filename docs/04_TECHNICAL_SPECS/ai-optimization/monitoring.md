# 多维度量化监控

> 市场监控系统框架
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - AI优化：[self-optimization.md](./self-optimization.md)

***

## 1. 大盘风格识别量化体系

### 1.1 规模风格判断

| 风格类型 | 量化标准 |
|----------|----------|
| 小盘股行情 | 中证1000涨幅 > 沪深300涨幅 × 1.5 |
| 大盘股行情 | 沪深300涨幅 > 中证1000涨幅 × 1.2 |
| 均衡市 | 两者差距 < 20% |

***

### 1.2 行情性质判断

| 行情类型 | 量化标准 |
|----------|----------|
| 进攻性市场 | (科技板块涨幅 - 金融板块涨幅) > 2% |
| 防御性市场 | (金融板块涨幅 - 科技板块涨幅) > 1% |
| 均衡市 | 两者差距 < 1% |

***

### 1.3 资金偏好识别

| 资金类型 | 量化特征 | 操作风格 |
| ---- | -------------------- | ----- |
| 短线资金主导 | 小盘股成交额占比>40%，涨停家数>50 | 打板、追板 |
| 机构主导 | 北向资金持续净流入，权重股上涨 | 趋势跟随 |
| 散户主导 | 换手率高，涨跌家数比接近1:1 | 高频交易 |

***

## 2. 逆势资金量化监控体系

### 2.1 逆势识别算法

| 条件 | 量化标准 |
|------|----------|
| 指数下跌时间窗口 | 大盘下跌确认 |
| 个股逆势 | 个股上涨 OR 个股跌幅 < 指数跌幅 × 0.5 |
| 资金逆势强度 | (个股机构净流入/流通市值) - (指数资金强度) > 阈值 |

***

### 2.2 逆势资金量化指标

| 指标 | 计算公式 | 量化标准 |
| ----- | ------------------------- | ---------- |
| 价格逆势度 | 个股涨幅 - 指数涨幅 | >2%为显著逆势 |
| 资金逆势度 | (个股机构净流入/流通市值) - (指数资金强度) | >0.5%为显著逆势 |
| 持续性验证 | 连续N个5分钟周期逆势 | N≥3确认趋势 |

***

## 3. 情绪风向量化监控体系

### 3.1 情绪识别算法

| 情绪类型 | 量化标准 |
|----------|----------|
| 连板识别 | 自动识别连续涨停股票（连板数≥2） |
| 带动效应 | 跟风股数量 × 跟风股平均涨幅 |
| 梯队分类-第一梯队 | 连板数≥4 OR 带动涨停≥3 |
| 梯队分类-第二梯队 | 连板数≥2 OR 带动涨停≥2 |
| 梯队分类-第三梯队 | 首板涨停但有明确跟风 |
| 强弱转换 | 原强势板块出现跌停 OR 炸板率>30% |

***

### 3.2 情绪梯队量化标准

| 梯队 | 连板要求 | 带动要求 | 情绪贡献 |
| ---- | ---- | ------ | ---- |
| 第一梯队 | ≥4连板 | 带动3+涨停 | 核心主线 |
| 第二梯队 | ≥2连板 | 带动2+涨停 | 次级主线 |
| 第三梯队 | 首板 | 有跟风 | 支线热点 |

***

## 4. KDJ超卖量化筛选体系

### 4.1 超卖信号算法

| 信号级别 | 量化标准 |
|----------|----------|
| 超卖条件 | 日线J值 < 0 AND 120分钟J值 < 0 AND 60分钟J值 < 0 |
| MACD过滤-日线必须 | (DIF > 0) AND (DEA > 0) AND (绿柱第二日缩短) AND (DIF企稳) |
| MACD过滤-短周期任选 | (120分钟 OR 60分钟) AND (绿柱缩短) AND (DIF企稳) |
| 强信号 | 日线+短周期双周期确认 |
| 中信号 | 仅日线周期确认 |
| 弱信号 | 仅短周期确认 |

***

## 5. Python实现

```python
class MarketStyleMonitor:
    """大盘风格监控"""

    def __init__(self, data_source):
        self.data = data_source

    def identify_market_style(self) -> str:
        """
        识别大盘风格
        返回: 'small_cap', 'large_cap', 'balanced'
        """
        cn1000_return = self.get_index_return('sh000852')
        hs300_return = self.get_index_return('sh000300')

        if cn1000_return > hs300_return * 1.5:
            return 'small_cap'
        elif hs300_return > cn1000_return * 1.2:
            return 'large_cap'
        else:
            return 'balanced'

    def identify_market_nature(self) -> str:
        """
        识别行情性质
        返回: 'aggressive', 'defensive', 'balanced'
        """
        tech_return = self.get_sector_return('科技')
        finance_return = self.get_sector_return('金融')

        diff = tech_return - finance_return

        if diff > 2:
            return 'aggressive'
        elif diff < -1:
            return 'defensive'
        else:
            return 'balanced'

    def get_fund_preference(self) -> str:
        """
        识别资金偏好
        返回: 'short_term', 'institutional', 'retail'
        """
        small_cap_ratio = self.get_small_cap_volume_ratio()
        north_flow = self.get_north_money_flow()
        turnover_rate = self.get_market_turnover_rate()

        if small_cap_ratio > 0.4 and north_flow < 0:
            return 'short_term'
        elif north_flow > 0 and self.is_weight_rising():
            return 'institutional'
        else:
            return 'retail'


class SentimentMonitor:
    """情绪监控"""

    def __init__(self, data_source):
        self.data = data_source

    def identify_sentiment_tier(self, stock_code: str) -> dict:
        """
        识别情绪梯队
        返回: {'tier': 1/2/3, 'consecutive_limit': int, 'follow_effect': float}
        """
        consecutive_limit = self.get_consecutive_limit(stock_code)
        follow_effect = self.get_follow_effect(stock_code)

        if consecutive_limit >= 4 or follow_effect >= 3:
            tier = 1
        elif consecutive_limit >= 2 or follow_effect >= 2:
            tier = 2
        else:
            tier = 3

        return {
            'tier': tier,
            'consecutive_limit': consecutive_limit,
            'follow_effect': follow_effect
        }

    def detect_strength_rotation(self) -> bool:
        """
        检测强弱转换
        """
        prev_strong_sector = self.get_prev_strong_sector()
        limit_down_count = self.get_sector_limit_down(prev_strong_sector)
        break_rate = self.get_sector_break_rate(prev_strong_sector)

        return limit_down_count > 0 or break_rate > 0.3


class ContraMoneyMonitor:
    """逆势资金监控"""

    def __init__(self, data_source):
        self.data = data_source

    def detect_contra_money(self, stock_code: str, index_code: str = 'sh000001') -> dict:
        """
        检测逆势资金

        Returns:
        --------
        dict: {
            'is_contra': bool,
            'price_contra_degree': float,
            'fund_contra_degree': float,
            'sustainability': int
        }
        """
        index_return = self.get_index_return(index_code)
        stock_return = self.get_stock_return(stock_code)

        price_contra = stock_return - index_return

        index_fund_strength = self.get_index_fund_strength(index_code)
        stock_fund_strength = self.get_stock_fund_strength(stock_code)
        fund_contra = stock_fund_strength - index_fund_strength

        sustainability = self.get_contra_sustainability(stock_code)

        return {
            'is_contra': stock_return > 0 or stock_return < index_return * 0.5,
            'price_contra_degree': price_contra,
            'fund_contra_degree': fund_contra,
            'sustainability': sustainability
        }
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录M内容 |
