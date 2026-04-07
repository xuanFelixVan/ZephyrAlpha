---



# T.03.RF002.申万行业因子
> **核心职责**: 申万行业因子体系定义，涉及申万行业因子
> **职责边界**: 
> - ✅ 本文档负责：申万行业因子体系定义相关内容
> - ❌ 本文档不负责：其他模块内容


> 行业因子体系（A股适配?
>
> **配套文档**?
> - 主文档：[../../INDEX.md](../../03_TRADING_TACTICS/INDEX.md)
> - 因子库索引：../../04_DATA_SOURCE/iFind/FACTOR_MASTER_INDEX.md
> - 风险因子：风险因子 README

***

## 1. 因子概述

| 属?| 内容 |
|------|------|
| 因子编号 | T.03.RF002 |
| 因子名称 | 申万行业因子 |
| 因子类型 | 行业因子 |
| 因子数量 | 28个一级行?|
| 数据来源 | Baostock / AkShare |

**核心理念**：基于申万行业分类体系，构建A股行业因子，用于行业轮动和风险控?

**适用场景**：行业轮动策略、行业风险控制、行业暴露分?

***

## 2. 申万一级行业分?

### 2.1 28个一级行?

```python
SW_INDUSTRY_L1 = {
    '农林牧渔': ['种植?, '渔业', '林业', '饲料', '畜禽养殖', '动物保健', '农业综合'],
    '采掘': ['煤炭开?, '石油开?, '天然气开?, '金属非金属采?, '采掘服务'],
    '化工': ['化学原料', '化学制品', '化学纤维', '橡胶', '塑料'],
    '钢铁': ['普钢', '特钢', '冶钢原料'],
    '有色金属': ['黄金', '?, '?, '锌铅', '锡锑', '?, '稀?, '?, '金属新材?],
    '电子': ['半导?, '元件', '光学光电?, '消费电子', '其他电子'],
    '汽车': ['汽车整车', '汽车零部?, '汽车服务', '其他汽车'],
    '家用电器': ['白色家电', '黑色家电', '小家?, '厨卫电器'],
    '食品饮料': ['白酒', '啤酒', '其他酒类', '食品加工', '调味?, '乳品', '饮料制?],
    '纺织服装': ['纺织制?, '服装家纺', '饰品'],
    '轻工制?: ['造纸', '包装印刷', '家用轻工'],
    '医药生物': ['化学制药', '中药', '生物制品', '医药商业', '医疗器械', '医疗服务'],
    '公用事业': ['电力', '燃气', '水务', '环保', '供热'],
    '交通运?: ['航空机场', '公路铁路', '航运港口', '物流'],
    '房地?: ['房地产开?, '房地产服?],
    '商业贸易': ['一般零?, '专业连锁', '商业物业经营', '贸易'],
    '休闲服务': ['酒店餐饮', '旅游综合', '景点', '其他休闲服务'],
    '建筑材料': ['水泥制?, '玻璃制?, '其他建材'],
    '建筑装饰': ['房屋建设', '装修装饰', '园林工程', '基础建设', '专业工程'],
    '电气设备': ['电机', '电气自动化设?, '电源设备', '风电设备', '光伏设备', '储能设备'],
    '国防军工': ['航空装备', '航天装备', '地面兵装', '船舶制?],
    '计算?: ['计算机设?, 'IT服务', '软件开?, '互联网服?],
    '传媒': ['广告营销', '影视院线', '游戏', '出版', '数字媒体'],
    '通信': ['通信设备', '通信服务'],
    '银行': ['国有大型银行', '股份制银?, '城商?, '农商?],
    '非银金融': ['证券', '保险', '多元金融'],
    '机械设备': ['通用设备', '专用设备', '仪器仪表', '金属制品'],
    '综合': ['综合']
}
```

### 2.2 行业代码映射

```python
SW_CODE_MAP = {
    '农林牧渔': '801010',
    '采掘': '801020',
    '化工': '801030',
    '钢铁': '801040',
    '有色金属': '801050',
    '电子': '801080',
    '汽车': '801110',
    '家用电器': '801110',
    '食品饮料': '801120',
    '纺织服装': '801130',
    '轻工制?: '801140',
    '医药生物': '801150',
    '公用事业': '801160',
    '交通运?: '801170',
    '房地?: '801180',
    '商业贸易': '801200',
    '休闲服务': '801210',
    '建筑材料': '801220',
    '建筑装饰': '801230',
    '电气设备': '801730',
    '国防军工': '801740',
    '计算?: '801750',
    '传媒': '801760',
    '通信': '801770',
    '银行': '801780',
    '非银金融': '801790',
    '机械设备': '801890',
    '综合': '801900'
}
```

***

## 3. 行业因子计算

### 3.1 行业暴露度计?

```python
class IndustryFactor:
    """
    行业因子计算
    """

    def calc_industry_exposure(self, stock_industry):
        """
        计算行业暴露度（独热编码?

        Parameters:
            stock_industry: 股票所属申万一级行?

        Returns:
            dict: 各行业暴露度
        """
        industries = list(SW_INDUSTRY_L1.keys())
        exposure = {ind: 0.0 for ind in industries}

        if stock_industry in industries:
            exposure[stock_industry] = 1.0

        return exposure

    def calc_industry_exposure_matrix(self, stocks_industries):
        """
        计算行业暴露矩阵

        Parameters:
            stocks_industries: dict, {stock_code: industry_name}

        Returns:
            DataFrame: 行业暴露矩阵
        """
        industries = list(SW_INDUSTRY_L1.keys())
        n_stocks = len(stocks_industries)

        matrix = np.zeros((n_stocks, len(industries)))

        for i, (stock, industry) in enumerate(stocks_industries.items()):
            if industry in industries:
                j = industries.index(industry)
                matrix[i, j] = 1.0

        return pd.DataFrame(matrix, index=stocks_industries.keys(), columns=industries)
```

### 3.2 行业收益率计?

```python
def calc_industry_return(self, industry_stocks, price_df):
    """
    计算行业收益率（成分股加权）

    Parameters:
        industry_stocks: list, 行业成分股列?
        price_df: DataFrame, 价格数据

    Returns:
        Series: 各行业收益率
    """
    industry_returns = {}

    for industry, stocks in SW_INDUSTRY_L1.items():
        stock_returns = []
        weights = []

        for stock in stocks:
            if stock in price_df.columns:
                ret = price_df[stock].pct_change().iloc[-1]
                weight = self.get_float_market_cap(stock)
                stock_returns.append(ret)
                weights.append(weight)

        if stock_returns:
            industry_ret = np.average(stock_returns, weights=weights)
            industry_returns[industry] = industry_ret

    return pd.Series(industry_returns)
```

### 3.3 行业市值权?

```python
def calc_industry_market_weight(self, trade_date):
    """
    计算申万行业在全市场的市值权?

    Parameters:
        trade_date: 交易日期

    Returns:
        Series: 各行业市值权?
    """
    all_stocks = self.get_all_stocks(trade_date)
    industry_weights = {}

    total_market_cap = 0
    for stock in all_stocks:
        industry = self.get_sw_industry(stock)
        market_cap = self.get_float_market_cap(stock, trade_date)
        industry_weights[industry] = industry_weights.get(industry, 0) + market_cap
        total_market_cap += market_cap

    industry_weights = {
        k: v / total_market_cap
        for k, v in industry_weights.items()
    }

    return pd.Series(industry_weights)
```

***

## 4. 行业轮动模型

### 4.1 美林时钟定位

```python
class IndustryRotationModel:
    """
    行业轮动模型
    基于美林时钟进行行业配置
    """

    ROTATION_MATRIX = {
        '复苏': {
            'preferred': ['可选消?, '金融', '信息技?, '原材?],
            'avoid': ['公用事业', '必需消费']
        },
        '过热': {
            'preferred': ['信息技?, '医疗保健', '能源', '原材?],
            'avoid': ['金融', '房地?]
        },
        '滞胀': {
            'preferred': ['能源', '医药', '公用事业', '金融'],
            'avoid': ['可选消?, '信息技?]
        },
        '衰退': {
            'preferred': ['公用事业', '金融', '必需消费', '通信'],
            'avoid': ['可选消?, '房地?, '信息技?]
        }
    }

    def get_clock_phase(self, macro_indicator):
        """
        获取美林时钟定位

        Parameters:
            macro_indicator: dict
                - gdp产出缺口
                - inflation 通胀?
                - PMI

        Returns:
            str: 时钟阶段
        """
        gdp_gap = macro_indicator.get('gdp_gap', 0)
        inflation = macro_indicator.get('inflation', 0)

        if gdp_gap > 0 and inflation < 0.03:
            return '复苏'
        elif gdp_gap > 0 and inflation > 0.03:
            return '过热'
        elif gdp_gap < 0 and inflation > 0.03:
            return '滞胀'
        else:
            return '衰退'

    def predict_rotation(self, macro_indicator):
        """
        预测行业轮动方向

        Returns:
            dict: 推荐的行业配?
        """
        clock_phase = self.get_clock_phase(macro_indicator)
        rotation = self.ROTATION_MATRIX.get(clock_phase, {})

        return {
            'clock_phase': clock_phase,
            'preferred_industries': rotation.get('preferred', []),
            'avoid_industries': rotation.get('avoid', [])
        }
```

### 4.2 行业动量轮动

```python
def calc_industry_momentum(self, industry_returns, lookback=20):
    """
    计算行业动量

    Parameters:
        industry_returns: DataFrame, 行业收益?
        lookback: int, 回溯?

    Returns:
        Series: 行业动量排名
    """
    cumulative_return = (1 + industry_returns.tail(lookback)).prod() - 1
    momentum_rank = cumulative_return.sort_values(ascending=False)

    return momentum_rank
```

***

## 5. Python实现

```python
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class SWIndustryFactor:
    """
    申万行业因子计算?
    """

    INDUSTRIES = list(SW_INDUSTRY_L1.keys())

    def __init__(self):
        self.name = "申万行业因子"
        self.factor_code = "T.03.RF002"

    def get_industry_exposure(self, stock_code: str, stock_industry: str) -> np.ndarray:
        """
        获取个股的行业暴露度向量

        Returns:
            ndarray: 28维行业暴露向?
        """
        exposure = np.zeros(len(self.INDUSTRIES))

        if stock_industry in self.INDUSTRIES:
            idx = self.INDUSTRIES.index(stock_industry)
            exposure[idx] = 1.0

        return exposure

    def get_portfolio_industry_exposure(self, holdings: Dict[str, float]) -> np.ndarray:
        """
        获取组合的行业暴露度

        Parameters:
            holdings: dict, {stock_code: weight}

        Returns:
            ndarray: 加权行业暴露向量
        """
        portfolio_exposure = np.zeros(len(self.INDUSTRIES))

        for stock, weight in holdings.items():
            industry = self.get_stock_industry(stock)
            exposure = self.get_industry_exposure(stock, industry)
            portfolio_exposure += exposure * weight

        return portfolio_exposure

    def calc_industry_factor_return(self, industry: str, price_df: pd.DataFrame) -> float:
        """
        计算行业因子收益

        Parameters:
            industry: 行业名称
            price_df: 价格数据

        Returns:
            float: 行业收益?
        """
        stocks = SW_INDUSTRY_L1.get(industry, [])
        returns = []
        weights = []

        for stock in stocks:
            if stock in price_df.columns:
                ret = price_df[stock].pct_change().iloc[-1]
                weight = self.get_stock_weight(stock)
                returns.append(ret)
                weights.append(weight)

        if returns:
            return np.average(returns, weights=weights)
        return 0.0

    def build_industry_covariance(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """
        构建行业协方差矩?

        Returns:
            DataFrame: 28x28行业协方差矩?
        """
        return returns_df.cov()
```

***

## 6. 使用示例

```python
# 初始?
industry_factor = SWIndustryFactor()

# 获取个股行业暴露
exposure = industry_factor.get_industry_exposure('000001', '银行')
print(f"行业暴露向量形状: {exposure.shape}")

# 获取组合行业暴露
holdings = {
    '000001': 0.1,
    '000002': 0.05,
    '600000': 0.08,
}
portfolio_exposure = industry_factor.get_portfolio_industry_exposure(holdings)
print(f"组合行业暴露: {portfolio_exposure}")

# 行业轮动
rotation_model = IndustryRotationModel()
macro = {'gdp_gap': 0.5, 'inflation': 0.02}
rotation = rotation_model.predict_rotation(macro)
print(f"时钟阶段: {rotation['clock_phase']}")
print(f"首选行? {rotation['preferred_industries']}")
```

***

## 7. 注意事项

1. **行业分类**：需定期更新申万行业分类
2. **成分股变?*：行业成分股可能调整，需动态更?
3. **停牌处理**：停牌股票收益率?计算
4. **权重计算**：建议使用流通市值加?

***

## 8. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本，整合附录AG申万行业因子体系 |

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
