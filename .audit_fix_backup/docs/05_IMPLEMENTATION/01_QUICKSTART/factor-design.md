---
module_id: FACTOR_DESIGN
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_05
responsibility: 01_QUICKSTART
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管?
compliance_level: 研究标准
parent_document: ../INDEX.md
implementation_status: 进行?---
> **核心职责**: 文档内容说明
---
## 1. 因子概述











### 1.1 什么是因子?











**因子 = 股票的特征数?*











| 因子类型 | 示例 | 含义 |





|----------|------|------|





| 估值因?| PE、PB | 股票贵不?|





| 动量因子 | 20日涨?| 股票强不?|





| 质量因子 | ROE、毛利率 | 公司好不?|





| 规模因子 | 市?| 公司大不?|





| 波动?| 日波动率 | 股票稳不?|











### 1.2 因子选股流程











```





┌─────────────────────────────────────────────────────────────?





?                   因子选股流程                             ?





├─────────────────────────────────────────────────────────────?





?                                                            ?





? 获取数据 ──?计算因子 ──?因子排序 ──?选股 ──?回测验证   ?





?                                                            ?





? 每日: 计算各股票因??按因子值排??选Top50 ?等权持有    ?





?                                                            ?





└─────────────────────────────────────────────────────────────?





```











```---











## 2. 因子计算模块











### 2.1 目录结构











```





src/modules/





├── factors/





?  ├── __init__.py





?  ├── factor_base.py          # 因子基类





?  ├── value_factors.py        # 估值因?





?  ├── momentum_factors.py     # 动量因子





?  ├── quality_factors.py      # 质量因子





?  └── factor_portfolio.py     # 因子组合





```











### 2.2 因子基类 (factor_base.py)











```python





"""





因子基类 - 所有因子的父类





"""





import pandas as pd





import numpy as np





from abc import ABC, abstractmethod

















class FactorBase(ABC):





    """





    因子基类











    所有因子计算类都需要继承此?





    """











    def __init__(self, name: str, category: str):





        self.name = name





        self.category = category











    @abstractmethod





    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """





        计算因子











        Args:





            data: 包含OHLCV等数据的DataFrame











        Returns:





            因子值Series，index为股票代?





        """





        pass











    def validate_data(self, data: pd.DataFrame) -> bool:





        """验证数据完整?""





        required_cols = ['close', 'volume']





        return all(col in data.columns for col in required_cols)











    def handle_missing(self, values: pd.Series) -> pd.Series:





        """处理缺失?""





        # 用中位数填充





        return values.fillna(values.median())

















class ValueFactor(FactorBase):





    """估值因子基?""











    def __init__(self):





        super().__init__('value', 'valuation')

















class MomentumFactor(FactorBase):





    """动量因子基类"""











    def __init__(self):





        super().__init__('momentum', 'momentum')

















class QualityFactor(FactorBase):





    """质量因子基类"""











    def __init__(self):





        super().__init__('quality', 'quality')





```











### 2.3 估值因?(value_factors.py)











```python





"""





估值因?- 计算股票的估值指?





"""





import pandas as pd





import numpy as np





from .factor_base import ValueFactor

















class PE(FactorBase):





    """





    市盈率因?(Price-to-Earning Ratio)











    计算方式: 市?/ 净利润





    使用方式: 越低越便宜（但要结合行业?





    """











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算PE"""





        market_cap = data['market_cap']  # 市?





        net_profit = data['net_profit']  # 净利润











        pe = market_cap / net_profit











        # 处理异常?





        pe = pe.replace([np.inf, -np.inf], np.nan)





        pe = self.handle_missing(pe)











        return pe

















class PB(FactorBase):





    """





    市净率因?(Price-to-Book Ratio)











    计算方式: 市?/ 净资产





    使用方式: 越低越便?





    """











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算PB"""





        market_cap = data['market_cap']  # 市?





        book_value = data['total_assets'] - data['total_liabilities']  # 净资产











        pb = market_cap / book_value











        pb = pb.replace([np.inf, -np.inf], np.nan)





        pb = self.handle_missing(pb)











        return pb

















class PS(FactorBase):





    """





    市销率因?(Price-to-Sales Ratio)











    计算方式: 市?/ 营业收入





    使用方式: 越低越便?





    """











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算PS"""





        market_cap = data['market_cap']





        revenue = data['revenue']  # 营业收入











        ps = market_cap / revenue











        ps = ps.replace([np.inf, -np.inf], np.nan)





        ps = self.handle_missing(ps)











        return ps

















class PCF(ValueFactor):





    """





    现金流市值比











    计算方式: 经营现金?/ 市?





    使用方式: 越高越好





    """











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算PCF"""





        operating_cf = data['operating_cash_flow']  # 经营现金?





        market_cap = data['market_cap']











        pcf = operating_cf / market_cap











        pcf = pcf.replace([np.inf, -np.inf], np.nan)





        pcf = self.handle_missing(pcf)











        return pcf





```











### 2.4 动量因子 (momentum_factors.py)











```python





"""





动量因子 - 计算股票的动量指?





"""





import pandas as pd





import numpy as np





from .factor_base import MomentumFactor

















class ReturnN(MomentumFactor):





    """





    N日收益率因子











    计算方式: (今日收盘?- N日前收盘? / N日前收盘?





    使用方式: 越高表示近期涨势越强





    """











    def __init__(self, period: int = 20):





        self.period = period





        super().__init__()











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算N日收益率"""





        close = data['close']











        returns = close.pct_change(self.period)











        return returns.replace([np.inf, -np.inf], np.nan).fillna(0)

















class VolumeRatio(MomentumFactor):





    """





    量比因子











    计算方式: 今日成交?/ 过去N日平均成交量





    使用方式: 大于1表示放量





    """











    def __init__(self, period: int = 5):





        self.period = period





        super().__init__()











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算量比"""





        volume = data['volume']





        avg_volume = volume.rolling(self.period).mean()











        ratio = volume / avg_volume











        return ratio.replace([np.inf, -np.inf], np.nan).fillna(1)

















class RSRS(MomentumFactor):





    """





    阻力支撑相对强度因子 (RSRS)











    计算方式:





    1. 取过去N日最高价和最低价





    2. 用线性回归计算斜?





    3. 斜率标准?











    使用方式: 越高表示支撑越强





    """











    def __init__(self, period: int = 18):





        self.period = period





        super().__init__()











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算RSRS"""





        high = data['high']





        low = data['low']











        rsrs = pd.Series(index=data.index, dtype=float)











        for i in range(self.period, len(data)):





            y = high.iloc[i-self.period:i].values





            x = low.iloc[i-self.period:i].values











            # 简单线性回?





            if len(x) > 0 and len(y) > 0:





                slope = np.polyfit(x, y, 1)[0]





                rsrs.iloc[i] = slope





            else:





                rsrs.iloc[i] = 1.0











        return rsrs.replace([np.inf, -np.inf], np.nan).fillna(1.0)

















class MACD_signal(MomentumFactor):





    """





    MACD信号因子











    计算方式: DIF - DEA





    使用方式: 大于0表示多头





    """











    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):





        self.fast = fast





        self.slow = slow





        self.signal = signal





        super().__init__()











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算MACD信号"""





        close = data['close']











        # 计算EMA





        ema_fast = close.ewm(span=self.fast).mean()





        ema_slow = close.ewm(span=self.slow).mean()











        # DIF





        dif = ema_fast - ema_slow











        # DEA





        dea = dif.ewm(span=self.signal).mean()











        # MACD?





        macd = (dif - dea) * 2











        return macd.replace([np.inf, -np.inf], np.nan).fillna(0)





```











### 2.5 质量因子 (quality_factors.py)











```python





"""





质量因子 - 计算公司的质量指?





"""





import pandas as pd





import numpy as np





from .factor_base import QualityFactor

















class ROE(QualityFactor):





    """





    净资产收益?(Return on Equity)











    计算方式: 净利润 / 净资产





    使用方式: 越高表示盈利能力越强





    """











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算ROE"""





        net_profit = data['net_profit']





        equity = data['total_assets'] - data['total_liabilities']











        roe = net_profit / equity











        return roe.replace([np.inf, -np.inf], np.nan).fillna(0)

















class GrossMargin(QualityFactor):





    """





    毛利?











    计算方式: (营业收入 - 营业成本) / 营业收入





    使用方式: 越高表示竞争力越?





    """











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算毛利?""





        revenue = data['revenue']





        cost = data['operating_cost']











        margin = (revenue - cost) / revenue











        return margin.replace([np.inf, -np.inf], np.nan).fillna(0)

















class DebtToAsset(QualityFactor):





    """





    资产负债率











    计算方式: 总负?/ 总资?





    使用方式: 越低表示财务越健康（不宜过低?





    """











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算资产负债率"""





        total_liabilities = data['total_liabilities']





        total_assets = data['total_assets']











        debt_ratio = total_liabilities / total_assets











        return debt_ratio.replace([np.inf, -np.inf], np.nan).fillna(0.5)

















class CurrentRatio(QualityFactor):





    """





    流动比率











    计算方式: 流动资产 / 流动负?





    使用方式: 大于1表示短期偿债能力良?





    """











    def calculate(self, data: pd.DataFrame) -> pd.Series:





        """计算流动比率"""





        current_assets = data['current_assets']





        current_liabilities = data['current_liabilities']











        ratio = current_assets / current_liabilities











        return ratio.replace([np.inf, -np.inf], np.nan).fillna(1.0)





```











```---











## 3. 因子组合











### 3.1 因子组合?(factor_portfolio.py)











```python





"""





因子组合?- 将多个因子组合成选股策略





"""





import pandas as pd





import numpy as np





from typing import List, Dict

















class FactorPortfolio:





    """





    因子组合?











    功能:





    1. 计算多个因子





    2. 因子去极值和标准?





    3. 等权合成或加权合?





    4. 生成选股列表





    """











    def __init__(self, name: str = "default"):





        self.name = name





        self.factors = {}





        self.weights = {}











    def add_factor(self, name: str, factor: pd.Series, weight: float = 1.0):





        """





        添加因子











        Args:





            name: 因子名称





            factor: 因子?





            weight: 因子权重





        """





        self.factors[name] = factor





        self.weights[name] = weight











    def neutralize(self, factor: pd.Series, market_cap: pd.Series) -> pd.Series:





        """





        市值中性化











        用市值对因子做回归，取残差作为中性化后的因子











        Args:





            factor: 原始因子





            market_cap: 市?











        Returns:





            中性化后的因子





        """





        # 对数市?





        log_mcap = np.log(market_cap)











        # 计算因子与市值的相关?





        valid_idx = ~(factor.isna() | log_mcap.isna())





        if valid_idx.sum() < 10:





            return factor











        # 简单线性回?





        x = log_mcap[valid_idx].values





        y = factor[valid_idx].values











        slope, intercept = np.polyfit(x, y, 1)











        # 残差





        neutral = factor - (slope * log_mcap + intercept)











        return neutral











    def winsorize(self, factor: pd.Series, n_std: float = 3.0) -> pd.Series:





        """





        去极?











        将超过n倍标准差的值替换为边界?











        Args:





            factor: 因子?





            n_std: 标准差倍数











        Returns:





            去极值后的因?





        """





        mean = factor.mean()





        std = factor.std()











        lower = mean - n_std * std





        upper = mean + n_std * std











        return factor.clip(lower, upper)











    def standardize(self, factor: pd.Series) -> pd.Series:





        """





        标准?(Z-Score)











        Args:





            factor: 因子?











        Returns:





            标准化后的因?(均值为0，标准差?)





        """





        mean = factor.mean()





        std = factor.std()











        if std == 0:





            return factor - mean











        return (factor - mean) / std











    def combine(self, neutralize_market: bool = True) -> pd.Series:





        """





        组合因子











        步骤:





        1. 去极?





        2. 标准?





        3. 市值中性化（可选）





        4. 加权求和











        Returns:





            合成因子





        """





        combined = pd.Series(dtype=float)











        for name, factor in self.factors.items():





            # 去极?





            factor = self.winsorize(factor)











            # 标准?





            factor = self.standardize(factor)











            # 合成





            if combined.empty:





                combined = factor * self.weights[name]





            else:





                combined += factor * self.weights[name]











        return combined











    def select_stocks(self, n: int = 50, ascending: bool = False) -> List[str]:





        """





        选股











        Args:





            n: 选股数量





            ascending: False表示选因子值高?











        Returns:





            选中的股票代码列?





        """





        combined = self.combine()











        # 排序并选前N





        selected = combined.sort_values(ascending=ascending).head(n)











        return selected.index.tolist()





```











```---











## 4. 因子分析











### 4.1 IC分析 (因子预测能力)











```python





"""





IC分析 - 评估因子的预测能?





"""





import pandas as pd





import numpy as np





from scipy import stats

















def calculate_ic(factor: pd.Series, forward_return: pd.Series) -> Dict:





    """





    计算IC (Information Coefficient)











    IC = 因子的排序与下期收益的排序相关?











    Args:





        factor: 因子?





        forward_return: 未来N日收益率











    Returns:





        IC统计?





    """





    # 合并数据





    data = pd.DataFrame({





        'factor': factor,





        'return': forward_return





    }).dropna()











    if len(data) < 10:





        return {'ic': 0, 'p_value': 1}











    # 计算Spearman相关系数





    ic, p_value = stats.spearmanr(data['factor'], data['return'])











    return {





        'ic': ic,





        'p_value': p_value,





        'sample_size': len(data)





    }

















def calculate_rolling_ic(





    factor_df: pd.DataFrame,





    return_df: pd.DataFrame,





    window: int = 20





) -> pd.DataFrame:





    """





    计算滚动IC











    Args:





        factor_df: 因子?(index=日期, columns=股票)





        return_df: 收益?(index=日期, columns=股票)





        window: 滚动窗口











    Returns:





        滚动IC序列





    """





    ic_series = []











    dates = factor_df.index











    for i in range(window, len(dates)):





        factor_window = factor_df.iloc[i - window:i].iloc[-1]  # 取最后一?





        return_next = return_df.iloc[i]  # 下期收益











        ic = calculate_ic(factor_window, return_next)['ic']





        ic_series.append({'date': dates[i], 'ic': ic})











    return pd.DataFrame(ic_series).set_index('date')

















def analyze_factor(factor: pd.Series, returns: pd.Series) -> Dict:





    """





    因子分析报告











    Args:





        factor: 因子?





        returns: 收益?











    Returns:





        分析报告





    """





    ic_result = calculate_ic(factor, returns)











    # 分组回测





    data = pd.DataFrame({'factor': factor, 'return': returns}).dropna()











    # 按因子值分?





    data['group'] = pd.qcut(data['factor'], q=5, labels=[1, 2, 3, 4, 5])











    # 计算每组收益





    group_returns = data.groupby('group')['return'].mean()











    return {





        'ic': ic_result['ic'],





        'p_value': ic_result['p_value'],





        'ic_ir': ic_result['ic'] / ic_result.get('std', 1),  # IC_IR





        'group_returns': group_returns.to_dict(),





        'top_minus_bottom': group_returns.get(5, 0) - group_returns.get(1, 0)





    }





```











```---











## 5. 使用示例











### 5.1 完整选股流程











```python





"""





因子选股示例





"""





import pandas as pd





import numpy as np





from src.modules.factors.value_factors import PE, PB





from src.modules.factors.momentum_factors import ReturnN, VolumeRatio





from src.modules.factors.quality_factors import ROE, GrossMargin





from src.modules.factors.factor_portfolio import FactorPortfolio

















def run_factor_selection(stock_data: Dict[str, pd.DataFrame]) -> list:





    """





    运行因子选股











    Args:





        stock_data: 股票数据 {股票代码: DataFrame}











    Returns:





        选中的股票列?





    """











    # 合并数据





    df = pd.DataFrame(stock_data).T











    # 创建因子组合?





    portfolio = FactorPortfolio("value_momentum_quality")











    # 添加估值因?





    pe = PE().calculate(df)





    pb = PB().calculate(df)





    portfolio.add_factor('pe', pe, weight=0.2)





    portfolio.add_factor('pb', pb, weight=0.1)











    # 添加动量因子





    ret20 = ReturnN(20).calculate(df)





    vol_ratio = VolumeRatio(5).calculate(df)





    portfolio.add_factor('ret20', ret20, weight=0.3)





    portfolio.add_factor('vol_ratio', vol_ratio, weight=0.1)











    # 添加质量因子





    roe = ROE().calculate(df)





    margin = GrossMargin().calculate(df)





    portfolio.add_factor('roe', roe, weight=0.2)





    portfolio.add_factor('margin', margin, weight=0.1)











    # 市值中性化





    market_cap = df['market_cap']





    combined = portfolio.neutralize(portfolio.combine(), market_cap)











    # 更新组合





    portfolio.factors['combined'] = combined











    # 选股





    selected = portfolio.select_stocks(n=50, ascending=False)











    return selected

















# 使用





stock_data = {





    '000001.SZ': get_stock_data('000001.SZ'),





    '000002.SZ': get_stock_data('000002.SZ'),





    # ... 更多股票





}











selected_stocks = run_factor_selection(stock_data)





print(f"选中{len(selected_stocks)}只股? {selected_stocks}")





```











```---











## 6. 因子库索?











| 因子ID | 因子名称 | 类别 | 说明 |





|--------|----------|------|------|





| F001 | PE | 估?| 市盈?|





| F002 | PB | 估?| 市净?|





| F003 | PS | 估?| 市销?|





| F004 | PCF | 估?| 现金流市值比 |





| F011 | ReturnN | 动量 | N日收益率 |





| F012 | VolumeRatio | 动量 | 量比 |





| F013 | RSRS | 动量 | 阻力支撑相对强度 |





| F014 | MACD_signal | 动量 | MACD信号 |





| F021 | ROE | 质量 | 净资产收益?|





| F022 | GrossMargin | 质量 | 毛利?|





| F023 | DebtToAsset | 质量 | 资产负债率 |





| F024 | CurrentRatio | 质量 | 流动比率 |











```---











## 7. 下一?











学完因子计算后，您可以：











1. **进行IC分析**: 评估因子的预测能力





2. **组合更多因子**: 尝试不同的因子组?





3. **进入Phase 2**: 完整选股回测











```---











**最后更?*: 2026-03-29





**版本**: v5.0





**前置文档**: PHASE1_DESIGN.md





**下一步文?*: 





