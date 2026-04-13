---
module_id: PERFORMANCE_ATTRIBUTION
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 业绩归因分析文档
layer: layer_04
standard_type: 专业量化机构交易执行标准
applicable_scope: 交易执行与监控
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?---
> **核心职责**: 文档内容说明
---
## 1. 归因分析概述







```



业绩归因分析



├── 收益归因



?  ├── 单期归因（单次交易）



?  ├── 区间归因（日/??年）



?  └── 超额收益分解



├── 风险归因



?  ├── 波动率归?



?  ├── 最大回撤归?



?  └── 风险因子暴露



├── Brinson归因



?  ├── 配置效应



?  ├── 选择效应



?  └── 交互效应



└── 因子归因



    ├── 因子暴露



    ├── 因子收益贡献



    └── 因子波动贡献



```







```---







## 2. 收益归因







### 2.1 基础收益计算







```python



import pandas as pd



import numpy as np



from typing import Dict, List, Tuple







class ReturnAttribution:



    """收益归因分析"""







    def calculate_returns(



        self,



        portfolio_value: pd.Series



    ) -> pd.DataFrame:



        """计算收益率序?







        参数:



            portfolio_value: 组合净值序?



        """



        returns = portfolio_value.pct_change()



        cumulative_return = (1 + returns).cumprod() - 1







        return pd.DataFrame({



            'value': portfolio_value,



            'returns': returns,



            'cumulative_return': cumulative_return



        })







    def calculate_period_returns(



        self,



        portfolio_value: pd.Series,



        periods: List[str] = None



    ) -> Dict[str, float]:



        """计算区间收益







        参数:



            periods: ['1d', '1w', '1m', '3m', '6m', '1y']



        """



        if periods is None:



            periods = ['1d', '1w', '1m', '3m']







        results = {}



        for period in periods:



            if period == '1d':



                ret = (portfolio_value.iloc[-1] / portfolio_value.iloc[-2]) - 1



            elif period == '1w':



                ret = (portfolio_value.iloc[-1] / portfolio_value.iloc[-6]) - 1



            elif period == '1m':



                ret = (portfolio_value.iloc[-1] / portfolio_value.iloc[-22]) - 1



            elif period == '3m':



                ret = (portfolio_value.iloc[-1] / portfolio_value.iloc[-66]) - 1



            else:



                ret = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1







            results[period] = ret







        return results



```







### 2.2 超额收益分解







```python



    def decompose_excess_return(



        self,



        portfolio_returns: pd.Series,



        benchmark_returns: pd.Series



    ) -> Dict[str, float]:



        """分解超额收益







        超额收益 = 管理人收?- 基准收益







        参数:



            portfolio_returns: 组合收益序列



            benchmark_returns: 基准收益序列



        """



        portfolio_cumulative = (1 + portfolio_returns).cumprod().iloc[-1] - 1



        benchmark_cumulative = (1 + benchmark_returns).cumprod().iloc[-1] - 1







        excess_return = portfolio_cumulative - benchmark_cumulative







        # 跟踪误差



        tracking_error = (portfolio_returns - benchmark_returns).std() * np.sqrt(252)







        # 信息比率



        ir = excess_return / tracking_error if tracking_error > 0 else 0







        # Beta



        covariance = portfolio_returns.cov(benchmark_returns)



        benchmark_variance = benchmark_returns.var()



        beta = covariance / benchmark_variance if benchmark_variance > 0 else 1







        # Alpha



        risk_free_rate = 0.03  # 假设无风险利?



        alpha = portfolio_cumulative - (risk_free_rate + beta * (benchmark_cumulative - risk_free_rate))







        return {



            'excess_return': excess_return,



            'tracking_error': tracking_error,



            'information_ratio': ir,



            'beta': beta,



            'alpha': alpha,



            'portfolio_return': portfolio_cumulative,



            'benchmark_return': benchmark_cumulative



        }



```







```---







## 3. 风险归因







### 3.1 波动率归?







```python



class RiskAttribution:



    """风险归因分析"""







    def calculate_volatility_contribution(



        self,



        returns: pd.Series,



        weights: pd.Series = None



    ) -> Dict[str, float]:



        """计算波动率贡?







        参数:



            returns: 收益序列



            weights: 持仓权重



        """



        # 年化波动?



        annual_vol = returns.std() * np.sqrt(252)







        # VaR (Value at Risk)



        var_95 = returns.quantile(0.05)



        var_99 = returns.quantile(0.01)







        # CVaR (Conditional VaR)



        cvar_95 = returns[returns <= var_95].mean()



        cvar_99 = returns[returns <= var_99].mean()







        # 最大回?



        cumulative = (1 + returns).cumprod()



        rolling_max = cumulative.cummax()



        drawdown = (cumulative - rolling_max) / rolling_max



        max_drawdown = drawdown.min()







        return {



            'annual_volatility': annual_vol,



            'var_95': var_95,



            'var_99': var_99,



            'cvar_95': cvar_95,



            'cvar_99': cvar_99,



            'max_drawdown': max_drawdown,



            'calmar_ratio': (returns.mean() * 252) / abs(max_drawdown) if max_drawdown != 0 else 0



        }



```







### 3.2 因子风险暴露







```python



    def factor_risk_contribution(



        self,



        portfolio_returns: pd.Series,



        factor_returns: pd.DataFrame



    ) -> Dict[str, float]:



        """计算因子风险贡献







        参数:



            portfolio_returns: 组合收益



            factor_returns: 因子收益（包含各因子?



        """



        # 回归分析



        from scipy import stats







        exposures = {}



        factor_names = factor_returns.columns







        for factor in factor_names:



            # 计算因子暴露（协方差 / 因子方差?



            factor_var = factor_returns[factor].var()



            covariance = portfolio_returns.cov(factor_returns[factor])



            exposure = covariance / factor_var if factor_var > 0 else 0



            exposures[factor] = exposure







        # 计算各因子贡献的风险



        total_risk = portfolio_returns.var()



        risk_contributions = {}







        for factor in factor_names:



            # 因子风险贡献 = 暴露  因子方差



            factor_var = factor_returns[factor].var()



            contribution = (exposures[factor] ** 2) * factor_var



            risk_contributions[factor] = contribution / total_risk







        return {



            'exposures': exposures,



            'risk_contributions': risk_contributions,



            'total_risk': total_risk * 252,  # 年化



            'r_squared': self._calculate_r_squared(portfolio_returns, factor_returns)



        }







    def _calculate_r_squared(



        self,



        portfolio_returns: pd.Series,



        factor_returns: pd.DataFrame



    ) -> float:



        """计算R"""



        from scipy import stats



        X = factor_returns.values



        y = portfolio_returns.values







        # 添加常数?



        X = np.column_stack([np.ones(len(y)), X])







        # OLS回归



        try:



            coeffs = np.linalg.lstsq(X, y, rcond=None)[0]



            y_pred = X @ coeffs



            ss_res = np.sum((y - y_pred) ** 2)



            ss_tot = np.sum((y - np.mean(y)) ** 2)



            r_squared = 1 - (ss_res / ss_tot)



        except:



            r_squared = 0







        return r_squared



```







```---







## 4. Brinson归因







### 4.1 多期Brinson模型







```python



class BrinsonAttribution:



    """Brinson归因模型







    用于分解主动管理收益



    """







    def __init__(self):



        self.benchmark_weights = None



        self.portfolio_weights = None



        self.benchmark_returns = None



        self.portfolio_returns = None







    def calculate_brinson(



        self,



        benchmark_weights: pd.Series,



        portfolio_weights: pd.Series,



        asset_returns: pd.DataFrame



    ) -> Dict[str, float]:



        """计算Brinson归因







        参数:



            benchmark_weights: 基准配置权重



            portfolio_weights: 组合配置权重



            asset_returns: 各资产收?







        返回:



            配置效应、选择效应、交互效?



        """



        # 资产类别收益



        asset_returns = asset_returns.mean()  # 区间收益







        # 总收?



        benchmark_total = (benchmark_weights * asset_returns).sum()



        portfolio_total = (portfolio_weights * asset_returns).sum()







        # 配置效应：归因于权重差异



        allocation_effect = ((portfolio_weights - benchmark_weights) * asset_returns).sum()







        # 选择效应：归因于选股差异



        selection_effect = (benchmark_weights * (asset_returns - asset_returns.mean())).sum()







        # 交互效应：权重和选股共同作用



        interaction_effect = portfolio_total - benchmark_total - allocation_effect - selection_effect







        return {



            'total_return': portfolio_total,



            'benchmark_return': benchmark_total,



            'active_return': portfolio_total - benchmark_total,



            'allocation_effect': allocation_effect,



            'selection_effect': selection_effect,



            'interaction_effect': interaction_effect,



            'attribution_sum': allocation_effect + selection_effect + interaction_effect



        }



```







### 4.2 行业归因







```python



    def sector_attribution(



        self,



        benchmark_weights: pd.DataFrame,



        portfolio_weights: pd.DataFrame,



        sector_returns: pd.DataFrame



    ) -> pd.DataFrame:



        """行业归因







        参数:



            benchmark_weights: 基准行业权重



            portfolio_weights: 组合行业权重



            sector_returns: 各行业收?



        """



        attribution_data = []







        sectors = benchmark_weights.columns







        for sector in sectors:



            bw = benchmark_weights[sector]



            pw = portfolio_weights[sector]



            sr = sector_returns[sector]







            # 各行业贡?



            benchmark_contribution = bw * sr



            portfolio_contribution = pw * sr







            # 效应分解



            allocation = (pw - bw) * sr



            selection = bw * (sr - sr.mean())



            interaction = (pw - bw) * (sr - sr.mean())







            attribution_data.append({



                'sector': sector,



                'benchmark_weight': bw,



                'portfolio_weight': pw,



                'sector_return': sr,



                'benchmark_contribution': benchmark_contribution,



                'portfolio_contribution': portfolio_contribution,



                'allocation_effect': allocation,



                'selection_effect': selection,



                'interaction_effect': interaction,



                'active_contribution': portfolio_contribution - benchmark_contribution



            })







        return pd.DataFrame(attribution_data)



```







```---







## 5. 因子归因







### 5.1 Barra因子归因







```python



class BarraFactorAttribution:



    """Barra风格因子归因"""







    def __init__(self):



        self.factors = [



            'market', 'size', 'beta', 'momentum',



            'value', 'quality', 'volatility',



            'growth', 'leverage', 'liquidity'



        ]







    def calculate_factor_returns(self, stocks: pd.DataFrame) -> pd.DataFrame:



        """计算因子收益







        参数:



            stocks: 包含因子暴露和收益的股票数据



        """



        factor_returns = {}







        for factor in self.factors:



            if factor in stocks.columns:



                # 因子收益 = 加权平均收益



                factor_returns[factor] = (stocks[factor] * stocks['return']).sum()







        return pd.DataFrame([factor_returns])







    def calculate_exposure_contribution(



        self,



        portfolio_exposures: pd.Series,



        factor_returns: pd.Series



    ) -> Dict[str, float]:



        """计算因子暴露贡献







        参数:



            portfolio_exposures: 组合在各因子的暴?



            factor_returns: 各因子的收益



        """



        contributions = {}







        for factor in self.factors:



            if factor in portfolio_exposures.index and factor in factor_returns.index:



                contributions[factor] = (



                    portfolio_exposures[factor] * factor_returns[factor]



                )







        total_return = sum(contributions.values())







        # 归一化为百分?



        contribution_pct = {



            k: v / total_return * 100 if total_return != 0 else 0



            for k, v in contributions.items()



        }







        return {



            'absolute_contributions': contributions,



            'percentage_contributions': contribution_pct,



            'total_return': total_return



        }



```







```---







## 6. 归因报告生成







```python



class AttributionReport:



    """归因报告生成?""







    def generate_report(



        self,



        portfolio_value: pd.Series,



        benchmark_value: pd.Series,



        positions: pd.DataFrame,



        factor_returns: pd.DataFrame = None



    ) -> Dict:



        """生成完整归因报告







        参数:



            portfolio_value: 组合净?



            benchmark_value: 基准净?



            positions: 持仓明细



            factor_returns: 因子收益（可选）



        """



        returns = portfolio_value.pct_change().dropna()



        benchmark_returns = benchmark_value.pct_change().dropna()







        # 1. 收益归因



        return_attr = ReturnAttribution()



        returns_analysis = return_attr.decompose_excess_return(



            returns, benchmark_returns



        )







        # 2. 风险归因



        risk_attr = RiskAttribution()



        risk_analysis = risk_attr.calculate_volatility_contribution(returns)







        # 3. Brinson归因（如果有持仓?



        brinson_result = None



        if positions is not None and len(positions) > 0:



            brinson = BrinsonAttribution()



            # 简化版Brinson



            brinson_result = {



                'total_return': returns_analysis['portfolio_return'],



                'active_return': returns_analysis['excess_return']



            }







        # 4. 因子归因（如果有因子数据?



        factor_result = None



        if factor_returns is not None:



            barra = BarraFactorAttribution()



            # 简化处?







        return {



            'period': {



                'start': portfolio_value.index[0].strftime('%Y-%m-%d'),



                'end': portfolio_value.index[-1].strftime('%Y-%m-%d'),



                'days': len(portfolio_value)



            },



            'returns': returns_analysis,



            'risk': risk_analysis,



            'brinson': brinson_result,



            'factors': factor_result,



            'summary': self._generate_summary(returns_analysis, risk_analysis)



        }







    def _generate_summary(



        self,



        returns_analysis: Dict,



        risk_analysis: Dict



    ) -> str:



        """生成摘要"""



        summary = f"""



        业绩归因摘要



        =============



        区间收益: {returns_analysis['portfolio_return']:.2%}



        基准收益: {returns_analysis['benchmark_return']:.2%}



        超额收益: {returns_analysis['excess_return']:.2%}







        信息比率: {returns_analysis['information_ratio']:.2f}



        Alpha: {returns_analysis['alpha']:.2%}







        年化波动? {risk_analysis['annual_volatility']:.2%}



        最大回? {risk_analysis['max_drawdown']:.2%}



        Calmar比率: {risk_analysis['calmar_ratio']:.2f}



        """



        return summary



```







```---







## 7. 归因指标速查







| 指标 | 计算公式 | 说明 |



|------|---------|------|



| 超额收益 | 组合收益 - 基准收益 | 主动管理收益 |



| 信息比率 | 超额收益 / 跟踪误差 | 主动收益效率 |



| Alpha | $R_p - (R_f + \beta(R_m - R_f))$ | 主动选股能力 |



| Beta | $\cov(R_p, R_m) / \var(R_m)$ | 市场敏感?|



| 配置效应 | $\sum(w_p - w_b) \times R_i$ | 权重贡献 |



| 选择效应 | $\sum w_b \times (R_{p,i} - R_{b,i})$ | 选股贡献 |



| 跟踪误差 | $std(R_p - R_b) \times \sqrt{252}$ | 主动风险 |







```---







**版本**: 1.0 | **更新**: 2026-03-28



