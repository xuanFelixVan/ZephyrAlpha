---
responsibility:
  - é£é©å½å 
  - é£é©åè§£
  - é£é©æ¥æºåæ
  - é£é©è´¡ç®åº?

module_id: RISK_ATTRIBUTION_SYSTEM_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 7 é£é©ç®¡çå±?
compliance_level: ä¸ä¸æ å
layer: Layer 5.3 (风险管理)
---

# é£é©å½å ç³»ç»èå¾

## 核心定位

负责风险归因分析，分解投资组合风险来源，量化各因子和持仓对风险的贡献，支持风险管理决策。



> **æ ¸å¿èè´£**: å¤ç»´åº¦é£é©åè§£ä¸å½å åæ
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼é£é©åè§£ãé£é©å½å ãé£é©å å­è¯å?
> - â?æ¬ææ¡£ä¸è´è´£ï¼å å­è®¡ç®ï¼ç±å å­æ¨¡åè´è´£ï¼


## 设计目标

### 主要目标

1. **功能完整性**: 确保RISK ATTRIBUTION SYSTEM功能完整，满足业务需求
2. **性能优化**: 提升系统性能，降低资源消耗
3. **可维护性**: 提高代码质量，便于后续维护
4. **可扩展性**: 支持功能扩展，适应业务变化

### 质量目标

- 代码覆盖率: ≥80%
- 性能指标: 满足设计要求
- 文档完整性: 100%


## 核心功能

### 功能清单

1. **数据管理**: 提供数据存储、查询、更新功能
2. **业务逻辑**: 实现核心业务逻辑处理
3. **接口服务**: 提供标准化的API接口
4. **监控告警**: 实时监控系统状态

### 功能特性

- 高可用性设计
- 自动故障恢复
- 灵活配置管理


## 实现方案

### 技术架构

采用RISK ATTRIBUTION SYSTEM化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控


## 1. æ¦è¿°

### 1.1 è®¾è®¡èæ¯ä¸ä¸å¡ç®?
**ä¸å¡é?*?- å½åç³»ç»ä»æç»©æå½å ï¼å¨Layer 7ï¼ï¼ç¼ºä¹é£é©å½å 
- æ æ³åè§£ç»åé£é©æ¥æºï¼å å­é£é©ãè¡ä¸é£é©ãç¹è´¨é£é©ï¼
- æ æ³è¯å«é£é©é©±å¨å ç´ ï¼å¯¼è´é£é©ç®¡çç¼ºä¹é?- æ æ³è¯ä¼°é£é©é¢ç®æ§è¡æåµ

**ææ¯ç?*?- æ å¤ç»´åº¦é£é©å½å è½å
- æ é£é©åè§£ä¸å½å æ¥åçæ
- æ é£é©é¢ç®æ§è¡ç?- æ é£é©è´¡ç®åº¦åæ

**é¢æ?*?- é£é©éæåº¦ï¼æå60%
- é£é©ç®¡çç²¾ç»åï¼æå40%
- é£é©å³ç­æ¯æï¼æ°å¢è½?- ä¸ºTwo Sigmaæ¨¡å¼æä¾æ ¸å¿è½åæ¯æ

### 1.2 ææ¯å®ä½ä¸æ¶æå±å½?
**Layerå®ä½**: Layer 6 - ç»åä¼åå±ï¼é£é©ç®¡çå­å±?
**æ¨¡åç±»å«**: æ ¸å¿æ¨¡åï¼P1çº§ï¼

**æ¶æè§è²**: 
- ä½ä¸ºTwo Sigmaæ¨¡å¼çæ ¸å¿ç»ä»¶ï¼æä¾å¤ç»´åº¦é£é©å½?- ä½ä¸ºé£é©ç®¡ççåæå·¥å·ï¼è¯å«é£é©é©±å¨å ç´ 
- ä½ä¸ºé£é©é¢ç®ççæ§å·¥å·ï¼è¯ä¼°é£é©é¢ç®æ§è¡æåµ

### 1.3 æ ¸å¿åè½æ¸å

1. **å å­é£é©å½å **: åè§£å å­é£é©è´¡ç®
2. **è¡ä¸é£é©å½å **: åè§£è¡ä¸é£é©è´¡ç®
3. **èµäº§é£é©å½å **: åè§£èµäº§é£é©è´¡ç®
4. **é£é©é¢ç®æ§è¡çæ§**: çæ§é£é©é¢ç®æ§è¡æåµ
5. **é£é©å½å æ¥åçæ**: çæå¯è§åå½å æ¥?
---

## 2. æ¶æè®¾è®¡

### 2.1 ç³»ç»æ¶æ?
```
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ??                   é£é©å½å ç³»ç»æ¶æ                              ?ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ??                                                                ?? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? ?? ?             è¾å¥?                                       ? ?? ? âââââââââââââââââââââââ? âââââââââââââââââââââââ?    ? ?? ? ?ç»åæ°æ®              ? ?é£é©æ¨¡å              ?    ? ?? ? ?- ç»åæé            ? ?- å å­è½½è·            ?    ? ?? ? ?- åºåæé            ? ?- å å­åæ¹?         ?    ? ?? ? ?- åå²æ¶ç            ? ?- ç¹è´¨é£é©            ?    ? ?? ? âââââââââââââââââââââââ? âââââââââââââââââââââââ?    ? ?? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? ??                         ?                                     ?? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? ?? ?             é£é©åè§£?                                   ? ?? ? âââââââââââââââââââââââââââââââââââââââââââââââââââââ? ? ?? ? ? Risk Decomposition Engine                         ? ? ?? ? ? - å å­é£é©åè§£                                     ? ? ?? ? ? - è¡ä¸é£é©åè§£                                     ? ? ?? ? ? - èµäº§é£é©åè§£                                     ? ? ?? ? âââââââââââââââââââââââââââââââââââââââââââââââââââââ? ? ?? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? ??                         ?                                     ?? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? ?? ?             å½å åæ?                                   ? ?? ? âââââââââââ? âââââââââââ? âââââââââââ?              ? ?? ? ?å å­å½å  ? ?è¡ä¸å½å  ? ?èµäº§å½å  ?              ? ?? ? ?         ? ?         ? ?         ?              ? ?? ? âââââââââââ? âââââââââââ? âââââââââââ?              ? ?? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? ??                         ?                                     ?? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? ?? ?             æ¥åçæ?                                   ? ?? ? âââââââââââ? âââââââââââ? âââââââââââ?              ? ?? ? ?å½å æ¥å ? ?å¯è§?  ? ?é¢è­¦ä¿¡å· ?              ? ?? ? ?         ? ?å¾è¡¨     ? ?         ?              ? ?? ? âââââââââââ? âââââââââââ? âââââââââââ?              ? ?? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? ?ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?```

### 2.2 æ ¸å¿æ°æ®?
```
ç»åæ°æ® + é£é©æ¨¡å
    ?é£é©åè§£ï¼å ?è¡ä¸/èµäº§?    ?å½å åæï¼è´¡ç®åº¦è®¡ç®?    ?é£é©é¢ç®æ§è¡çæ§
    ?è¾åºï¼å½å æ¥åãå¯è§åå¾è¡¨ãé¢è­¦ä¿¡?```

---

## 3. æ ¸å¿æ¨¡åè®¾è®¡

### 3.1 é£é©å½å ç³»ç»æ ¸å¿ç±»ï¼RiskAttributionSystem?
```python
class RiskAttributionSystem:
    """
    é£é©å½å ç³»ç»æ ¸å¿?    
    ç´¢å¼: RISK_ATTRIBUTION_001-M01
    èè´£: å¤ç»´åº¦é£é©åè§£ä¸å½å åæ
    è¾å¥: ç»åæ°æ®ãé£é©æ¨¡?    è¾åº: å½å æ¥åãå¯è§åå¾è¡¨
    """
    
    def __init__(self, config: AttributionConfig):
        self.config = config
        self.factor_attributor = FactorRiskAttributor(config.factor_config)
        self.industry_attributor = IndustryRiskAttributor(config.industry_config)
        self.asset_attributor = AssetRiskAttributor(config.asset_config)
        self.report_generator = AttributionReportGenerator()
        
    def attribute_risk(self,
                      portfolio_weights: pd.Series,
                      benchmark_weights: Optional[pd.Series],
                      barra_model: BarraRiskModel) -> AttributionResult:
        """
        æ§è¡é£é©å½å 
        
        Args:
            portfolio_weights: ç»åæé
            benchmark_weights: åºåæéï¼å¯éï¼
            barra_model: Barraé£é©æ¨¡å
            
        Returns:
            AttributionResult: å½å ç»æ
        """
        # 1. å å­é£é©å½å 
        factor_attribution = self.factor_attributor.attribute(
            portfolio_weights, benchmark_weights, barra_model
        )
        
        # 2. è¡ä¸é£é©å½å 
        industry_attribution = self.industry_attributor.attribute(
            portfolio_weights, benchmark_weights, barra_model
        )
        
        # 3. èµäº§é£é©å½å 
        asset_attribution = self.asset_attributor.attribute(
            portfolio_weights, benchmark_weights, barra_model
        )
        
        # 4. æ±æ»å½å ç»?        total_attribution = self._aggregate_attribution(
            factor_attribution, industry_attribution, asset_attribution
        )
        
        return AttributionResult(
            factor_attribution=factor_attribution,
            industry_attribution=industry_attribution,
            asset_attribution=asset_attribution,
            total_attribution=total_attribution,
            timestamp=datetime.now()
        )
    
    def monitor_risk_budget(self,
                           portfolio_weights: pd.Series,
                           risk_budget: RiskBudgetAllocation,
                           barra_model: BarraRiskModel) -> RiskBudgetMonitorResult:
        """
        çæ§é£é©é¢ç®æ§è¡æåµ
        
        Args:
            portfolio_weights: ç»åæé
            risk_budget: é£é©é¢ç®åé
            barra_model: Barraé£é©æ¨¡å
            
        Returns:
            RiskBudgetMonitorResult: é£é©é¢ç®çæ§ç»æ
        """
        # 1. è®¡ç®å®éé£é©ä½¿ç¨
        risk_decomposition = barra_model.decompose_risk(portfolio_weights)
        
        # 2. å¯¹æ¯é£é©é¢ç®
        budget_utilization = self._calculate_budget_utilization(
            risk_decomposition, risk_budget
        )
        
        # 3. è¯å«è¶é¢ç®é£?        over_budget_risks = self._identify_over_budget(budget_utilization)
        
        # 4. çæé¢è­¦ä¿¡å·
        alerts = self._generate_alerts(over_budget_risks)
        
        return RiskBudgetMonitorResult(
            budget_utilization=budget_utilization,
            over_budget_risks=over_budget_risks,
            alerts=alerts,
            timestamp=datetime.now()
        )
    
    def generate_report(self,
                       attribution_result: AttributionResult,
                       output_format: str = 'html') -> str:
        """
        çæå½å æ¥å
        
        Args:
            attribution_result: å½å ç»æ
            output_format: è¾åºæ ¼å¼?html', 'pdf', 'markdown'?            
        Returns:
            str: æ¥åæä»¶è·¯å¾
        """
        return self.report_generator.generate(
            attribution_result, output_format
        )
    
    def _aggregate_attribution(self,
                               factor_attr: pd.DataFrame,
                               industry_attr: pd.DataFrame,
                               asset_attr: pd.DataFrame) -> pd.DataFrame:
        """æ±æ»å½å ç»?""
        total = pd.concat([
            factor_attr.sum().to_frame('Factor'),
            industry_attr.sum().to_frame('Industry'),
            asset_attr.sum().to_frame('Asset')
        ], axis=1)
        
        return total
```

### 3.2 å å­é£é©å½å å¨ï¼FactorRiskAttributor?
```python
class FactorRiskAttributor:
    """
    å å­é£é©å½å ?    
    ç´¢å¼: RISK_ATTRIBUTION_001-M02
    èè´£: åè§£å å­é£é©è´¡ç®
    """
    
    def __init__(self, config: FactorAttributionConfig):
        self.config = config
        
    def attribute(self,
                 portfolio_weights: pd.Series,
                 benchmark_weights: Optional[pd.Series],
                 barra_model: BarraRiskModel) -> pd.DataFrame:
        """
        å å­é£é©å½å 
        
        Args:
            portfolio_weights: ç»åæé
            benchmark_weights: åºåæé
            barra_model: Barraé£é©æ¨¡å
            
        Returns:
            pd.DataFrame: å å­é£é©å½å ç»æ
        """
        # 1. è®¡ç®ç»åå å­æ´é²
        portfolio_exposure = barra_model.calculate_factor_exposure(portfolio_weights)
        
        # 2. è®¡ç®åºåå å­æ´é²ï¼å¦æï¼
        if benchmark_weights is not None:
            benchmark_exposure = barra_model.calculate_factor_exposure(benchmark_weights)
            active_exposure = portfolio_exposure - benchmark_exposure
        else:
            benchmark_exposure = None
            active_exposure = portfolio_exposure
        
        # 3. è®¡ç®å å­é£é©è´¡ç®
        factor_risk_contribution = self._calculate_factor_risk_contribution(
            portfolio_exposure, barra_model.factor_covariance
        )
        
        # 4. è®¡ç®ä¸»å¨é£é©å½å ï¼å¦æåºåï¼
        if benchmark_weights is not None:
            active_risk_contribution = self._calculate_active_risk_contribution(
                active_exposure, barra_model.factor_covariance
            )
        else:
            active_risk_contribution = None
        
        # 5. æå»ºå½å ?        attribution = pd.DataFrame({
            'Portfolio_Exposure': portfolio_exposure,
            'Benchmark_Exposure': benchmark_exposure if benchmark_weights is not None else 0,
            'Active_Exposure': active_exposure if benchmark_weights is not None else portfolio_exposure,
            'Risk_Contribution': factor_risk_contribution,
            'Active_Risk_Contribution': active_risk_contribution if active_risk_contribution is not None else factor_risk_contribution
        })
        
        return attribution
    
    def _calculate_factor_risk_contribution(self,
                                           factor_exposure: pd.Series,
                                           factor_covariance: pd.DataFrame) -> pd.Series:
        """
        è®¡ç®å å­é£é©è´¡ç®
        
        ä½¿ç¨è¾¹éé£é©è´¡ç®æ³ï¼
        MRC_i = f_i * (F * f)_i / Ï_p
        """
        # è®¡ç®ç»åé£é©
        F_f = factor_covariance @ factor_exposure
        portfolio_risk = np.sqrt(factor_exposure @ F_f)
        
        # è®¡ç®è¾¹éé£é©è´¡ç®
        marginal_risk_contribution = factor_exposure * F_f / portfolio_risk
        
        # è®¡ç®é£é©è´¡ç®ç¾å?        risk_contribution = marginal_risk_contribution / portfolio_risk
        
        return risk_contribution
    
    def _calculate_active_risk_contribution(self,
                                           active_exposure: pd.Series,
                                           factor_covariance: pd.DataFrame) -> pd.Series:
        """è®¡ç®ä¸»å¨é£é©è´¡ç®"""
        return self._calculate_factor_risk_contribution(active_exposure, factor_covariance)
```

### 3.3 è¡ä¸é£é©å½å å¨ï¼IndustryRiskAttributor?
```python
class IndustryRiskAttributor:
    """
    è¡ä¸é£é©å½å ?    
    ç´¢å¼: RISK_ATTRIBUTION_001-M03
    èè´£: åè§£è¡ä¸é£é©è´¡ç®
    """
    
    def __init__(self, config: IndustryAttributionConfig):
        self.config = config
        
    def attribute(self,
                 portfolio_weights: pd.Series,
                 benchmark_weights: Optional[pd.Series],
                 barra_model: BarraRiskModel) -> pd.DataFrame:
        """
        è¡ä¸é£é©å½å 
        
        Args:
            portfolio_weights: ç»åæé
            benchmark_weights: åºåæé
            barra_model: Barraé£é©æ¨¡å
            
        Returns:
            pd.DataFrame: è¡ä¸é£é©å½å ç»æ
        """
        # 1. è·åè¡ä¸å å­æ´é²
        industry_factors = [f for f in barra_model.factor_loadings.columns 
                          if f.startswith('industry_')]
        
        portfolio_industry_exposure = barra_model.factor_loadings[industry_factors].T @ portfolio_weights
        
        # 2. è®¡ç®åºåè¡ä¸æ´é²ï¼å¦æï¼
        if benchmark_weights is not None:
            benchmark_industry_exposure = barra_model.factor_loadings[industry_factors].T @ benchmark_weights
            active_industry_exposure = portfolio_industry_exposure - benchmark_industry_exposure
        else:
            benchmark_industry_exposure = None
            active_industry_exposure = portfolio_industry_exposure
        
        # 3. è®¡ç®è¡ä¸é£é©è´¡ç®
        industry_covariance = barra_model.factor_covariance.loc[industry_factors, industry_factors]
        industry_risk_contribution = self._calculate_industry_risk_contribution(
            portfolio_industry_exposure, industry_covariance
        )
        
        # 4. æå»ºå½å ?        attribution = pd.DataFrame({
            'Portfolio_Weight': portfolio_industry_exposure,
            'Benchmark_Weight': benchmark_industry_exposure if benchmark_weights is not None else 0,
            'Active_Weight': active_industry_exposure,
            'Risk_Contribution': industry_risk_contribution
        })
        
        return attribution
    
    def _calculate_industry_risk_contribution(self,
                                             industry_exposure: pd.Series,
                                             industry_covariance: pd.DataFrame) -> pd.Series:
        """è®¡ç®è¡ä¸é£é©è´¡ç®"""
        # ç±»ä¼¼å å­é£é©è´¡ç®è®¡ç®
        I_i = industry_covariance @ industry_exposure
        industry_risk = np.sqrt(industry_exposure @ I_i)
        
        risk_contribution = (industry_exposure * I_i) / industry_risk
        
        return risk_contribution
```

### 3.4 èµäº§é£é©å½å å¨ï¼AssetRiskAttributor?
```python
class AssetRiskAttributor:
    """
    èµäº§é£é©å½å ?    
    ç´¢å¼: RISK_ATTRIBUTION_001-M04
    èè´£: åè§£èµäº§é£é©è´¡ç®
    """
    
    def __init__(self, config: AssetAttributionConfig):
        self.config = config
        
    def attribute(self,
                 portfolio_weights: pd.Series,
                 benchmark_weights: Optional[pd.Series],
                 barra_model: BarraRiskModel) -> pd.DataFrame:
        """
        èµäº§é£é©å½å 
        
        Args:
            portfolio_weights: ç»åæé
            benchmark_weights: åºåæé
            barra_model: Barraé£é©æ¨¡å
            
        Returns:
            pd.DataFrame: èµäº§é£é©å½å ç»æ
        """
        # 1. è®¡ç®èµäº§é£é©è´¡ç®
        asset_risk_contribution = self._calculate_asset_risk_contribution(
            portfolio_weights, barra_model.asset_covariance
        )
        
        # 2. è®¡ç®ä¸»å¨æéï¼å¦æåºåï¼
        if benchmark_weights is not None:
            active_weights = portfolio_weights - benchmark_weights
        else:
            active_weights = portfolio_weights
        
        # 3. æå»ºå½å ?        attribution = pd.DataFrame({
            'Portfolio_Weight': portfolio_weights,
            'Benchmark_Weight': benchmark_weights if benchmark_weights is not None else 0,
            'Active_Weight': active_weights,
            'Risk_Contribution': asset_risk_contribution
        })
        
        return attribution
    
    def _calculate_asset_risk_contribution(self,
                                          weights: pd.Series,
                                          asset_covariance: pd.DataFrame) -> pd.Series:
        """
        è®¡ç®èµäº§é£é©è´¡ç®
        
        ä½¿ç¨è¾¹éé£é©è´¡ç®æ³ï¼
        MRC_i = w_i * (Î£ * w)_i / Ï_p
        """
        # è®¡ç®ç»åé£é©
        Sigma_w = asset_covariance @ weights
        portfolio_risk = np.sqrt(weights @ Sigma_w)
        
        # è®¡ç®è¾¹éé£é©è´¡ç®
        marginal_risk_contribution = weights * Sigma_w / portfolio_risk
        
        # è®¡ç®é£é©è´¡ç®ç¾å?        risk_contribution = marginal_risk_contribution / portfolio_risk
        
        return risk_contribution
```

### 3.5 å½å æ¥åçæå¨ï¼AttributionReportGenerator?
```python
class AttributionReportGenerator:
    """
    å½å æ¥åçæ?    
    ç´¢å¼: RISK_ATTRIBUTION_001-M05
    èè´£: çæå¯è§åå½å æ¥?    """
    
    def __init__(self):
        self.template_dir = 'templates/attribution/'
        
    def generate(self,
                attribution_result: AttributionResult,
                output_format: str = 'html') -> str:
        """
        çæå½å æ¥å
        
        Args:
            attribution_result: å½å ç»æ
            output_format: è¾åºæ ¼å¼
            
        Returns:
            str: æ¥åæä»¶è·¯å¾
        """
        # 1. çæå¯è§åå¾?        charts = self._generate_charts(attribution_result)
        
        # 2. çææ¥ååå®¹
        report_content = self._generate_content(attribution_result, charts)
        
        # 3. ä¿å­æ¥å
        report_path = self._save_report(report_content, output_format)
        
        return report_path
    
    def _generate_charts(self, attribution_result: AttributionResult) -> Dict[str, str]:
        """çæå¯è§åå¾?""
        charts = {}
        
        # 1. å å­é£é©è´¡ç®?        charts['factor_risk'] = self._plot_factor_risk_contribution(
            attribution_result.factor_attribution
        )
        
        # 2. è¡ä¸é£é©è´¡ç®?        charts['industry_risk'] = self._plot_industry_risk_contribution(
            attribution_result.industry_attribution
        )
        
        # 3. èµäº§é£é©è´¡ç®å¾ï¼Top 20?        charts['asset_risk'] = self._plot_asset_risk_contribution(
            attribution_result.asset_attribution
        )
        
        return charts
    
    def _plot_factor_risk_contribution(self, factor_attr: pd.DataFrame) -> str:
        """ç»å¶å å­é£é©è´¡ç®?""
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        factor_attr['Risk_Contribution'].plot(kind='bar', ax=ax)
        ax.set_title('Factor Risk Contribution')
        ax.set_xlabel('Factor')
        ax.set_ylabel('Risk Contribution (%)')
        ax.grid(True, alpha=0.3)
        
        chart_path = 'output/factor_risk_contribution.png'
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _plot_industry_risk_contribution(self, industry_attr: pd.DataFrame) -> str:
        """ç»å¶è¡ä¸é£é©è´¡ç®?""
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        industry_attr['Risk_Contribution'].plot(kind='bar', ax=ax)
        ax.set_title('Industry Risk Contribution')
        ax.set_xlabel('Industry')
        ax.set_ylabel('Risk Contribution (%)')
        ax.grid(True, alpha=0.3)
        
        chart_path = 'output/industry_risk_contribution.png'
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _plot_asset_risk_contribution(self, asset_attr: pd.DataFrame) -> str:
        """ç»å¶èµäº§é£é©è´¡ç®å¾ï¼Top 20?""
        import matplotlib.pyplot as plt
        
        # åTop 20
        top_assets = asset_attr.nlargest(20, 'Risk_Contribution')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        top_assets['Risk_Contribution'].plot(kind='bar', ax=ax)
        ax.set_title('Top 20 Asset Risk Contribution')
        ax.set_xlabel('Asset')
        ax.set_ylabel('Risk Contribution (%)')
        ax.grid(True, alpha=0.3)
        
        chart_path = 'output/asset_risk_contribution.png'
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _generate_content(self,
                         attribution_result: AttributionResult,
                         charts: Dict[str, str]) -> str:
        """çææ¥ååå®¹"""
        content = f"""
# Risk Attribution Report
> **æ ¸å¿èè´£**: Risk Attribution Systemèå¾è®¾è®¡
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼Risk Attribution Systemèå¾è®¾è®¡ç¸å³åå®¹
> - â?æ¬ææ¡£ä¸è´è´£ï¼å¶ä»æ¨¡ååå®?


## æ ¸å¿èè´£

é£é©å½å ç³»ç»ï¼è´è´£é£é©æ¥æºçåæåå½å?


---

## ð æ¦è¿°

æ¬ææ¡£å®ä¹äºRISK ATTRIBUTION SYSTEMçæ ¸å¿åè½åææ¯å®ç°ã?


> **æ ¸å¿å®ä½**: Risk Attribution Reportçæ ¸å¿åè½å®ç?


Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Executive Summary

- **Total Portfolio Risk**: {attribution_result.total_attribution.sum().sum():.2%}
- **Factor Risk Ratio**: {attribution_result.factor_attribution['Risk_Contribution'].sum():.2%}
- **Industry Risk Ratio**: {attribution_result.industry_attribution['Risk_Contribution'].sum():.2%}

## 2. Factor Risk Attribution

!Factor Risk Contribution

{attribution_result.factor_attribution.to_markdown()}

## 3. Industry Risk Attribution

!Industry Risk Contribution

{attribution_result.industry_attribution.to_markdown()}

## 4. Asset Risk Attribution (Top 20)

!Asset Risk Contribution

{attribution_result.asset_attribution.nlargest(20, 'Risk_Contribution').to_markdown()}
"""
        return content
    
    def _save_report(self, content: str, output_format: str) -> str:
        """ä¿å­æ¥å"""
        report_path = f'output/risk_attribution_report.{output_format}'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return report_path
```

### 3.6 éç½®ç±»å®?
```python
@dataclass
class AttributionConfig:
    """é£é©å½å éç½®"""
    factor_config: FactorAttributionConfig
    industry_config: IndustryAttributionConfig
    asset_config: AssetAttributionConfig
    
@dataclass
class FactorAttributionConfig:
    """å å­å½å éç½®"""
    include_style_factors: bool = True
    include_industry_factors: bool = True
    
@dataclass
class IndustryAttributionConfig:
    """è¡ä¸å½å éç½®"""
    industry_classification: str = 'gics'  # 'gics', 'sw', 'zz'
    
@dataclass
class AssetAttributionConfig:
    """èµäº§å½å éç½®"""
    top_n_assets: int = 20  # æ¾ç¤ºTop Nèµäº§
```

---

## 4. æ°æ®æ¨¡åå®ä¹

### 4.1 è¾å¥æ°æ®æ¨¡å

```python
@dataclass
class PortfolioData:
    """ç»åæ°æ®"""
    weights: pd.Series  # ç»åæé
    benchmark_weights: Optional[pd.Series]  # åºåæé
    returns: pd.DataFrame  # åå²æ¶ç?```

### 4.2 è¾åºæ°æ®æ¨¡å

```python
@dataclass
class AttributionResult:
    """å½å ç»æ"""
    factor_attribution: pd.DataFrame  # å å­å½å 
    industry_attribution: pd.DataFrame  # è¡ä¸å½å 
    asset_attribution: pd.DataFrame  # èµäº§å½å 
    total_attribution: pd.DataFrame  # æ»å½?    timestamp: datetime
    
@dataclass
class RiskBudgetMonitorResult:
    """é£é©é¢ç®çæ§ç»æ"""
    budget_utilization: pd.DataFrame  # é¢ç®ä½¿ç¨æåµ
    over_budget_risks: List[Dict]  # è¶é¢ç®é£?    alerts: List[Dict]  # é¢è­¦ä¿¡å·
    timestamp: datetime
```

---

## 5. éææ¹æ¡

### 5.1 ä¸Barraé£é©æ¨¡åéæ

```python
class BarraRiskModel:
    """Barraé£é©æ¨¡åï¼éæé£é©å½å ï¼"""
    
    def __init__(self):
        self.risk_attribution_system = RiskAttributionSystem(AttributionConfig())
        
    def attribute_risk(self,
                      portfolio_weights: pd.Series,
                      benchmark_weights: Optional[pd.Series] = None) -> AttributionResult:
        """é£é©å½å """
        return self.risk_attribution_system.attribute_risk(
            portfolio_weights, benchmark_weights, self
        )
```

### 5.2 ä¸ç»åä¼åå¨éæ

```python
class PortfolioOptimizer:
    """ç»åä¼åå¨ï¼éæé£é©å½å ?""
    
    def __init__(self, 
                 barra_model: BarraRiskModel,
                 attribution_system: RiskAttributionSystem):
        self.barra_model = barra_model
        self.attribution_system = attribution_system
        
    def optimize_and_attribute(self,
                              expected_returns: pd.Series,
                              constraints: List[Constraint]) -> Tuple[pd.Series, AttributionResult]:
        """ä¼åå¹¶å½?""
        # 1. ä¼åç»å
        optimal_weights = self.optimize(expected_returns, constraints)
        
        # 2. é£é©å½å 
        attribution = self.attribution_system.attribute_risk(
            optimal_weights, None, self.barra_model
        )
        
        return optimal_weights, attribution
```

---

## 6. å®æ½è·¯çº¿?
### 6.1 å¼åé¶æ®µï¼2å¨ï¼

**Week 1: æ ¸å¿æ¨¡åå¼?*
- Day 1-2: å å­é£é©å½å ?- Day 3-4: è¡ä¸é£é©å½å ?- Day 5: èµäº§é£é©å½å ?
**Week 2: éæä¸æµ?*
- Day 1-2: å½å æ¥åçæ?- Day 3: ä¸Barraæ¨¡åéæ
- Day 4: æµè¯ä¸ä¼?- Day 5: ææ¡£ç¼å

### 6.2 éç¨?
| éç¨?| æ¶é´ | äº¤ä»?| éªæ¶æ å |
|--------|------|--------|----------|
| **M1: å å­å½å å®æ** | Day 2 | å å­é£é©å½å ?| å½å æ­£ç¡® |
| **M2: è¡ä¸å½å å®æ** | Day 4 | è¡ä¸é£é©å½å ?| å½å æ­£ç¡® |
| **M3: èµäº§å½å å®æ** | Day 5 | èµäº§é£é©å½å ?| å½å æ­£ç¡® |
| **M4: æ¥åçæå®æ** | Day 7 | å½å æ¥åçæ?| æ¥åå®æ´ |
| **M5: æµè¯éè¿** | Day 10 | æµè¯æ¥å | æææµè¯éè¿ |

---

## 7. é¢ææ¶çè¯ä¼°

### 7.1 å®éæ¶ç

| ææ  | å½åæ°´å¹³ | ç®æ æ°´å¹³ | æåå¹åº¦ |
|------|---------|---------|---------|
| **é£é©éæ?* | 40% | 90% | +50% |
| **é£é©ç®¡çç²¾ç»?* | 60% | 90% | +30% |
| **é£é©å³ç­æ¯æ** | ?| ?| æ°å¢è½å |
| **Two Sigmaæ¨¡å¼å®æ´?* | 69% | 85% | +16% |

### 7.2 å®æ§æ¶?
- ?å®ç°Two Sigmaæ ¸å¿è½åï¼é£é©å½?- ?å¤ç»´åº¦é£é©åè§£ï¼å å­/è¡ä¸/èµäº§?- ?é£é©é¢ç®æ§è¡çæ§
- ?å¯è§åå½å æ¥?- ?é£é©é¢è­¦æºå¶

---

## 8. ææ¯æ éæ©

### 8.1 æ ¸å¿ä¾èµ?
| åºå | çæ¬ | ?| å¿è¦?|
|------|------|------|--------|
| **pandas** | ?.5 | æ°æ®å¤ç | å¿é |
| **numpy** | ?.21 | æ°å¼è®¡?| å¿é |
| **matplotlib** | ?.5 | å¯è§?| å¿é |
| **jinja2** | ?.0 | æ¥åæ¨¡æ¿ | å¿é |

### 8.2 å®è£å½ä»¤

```bash
pip install pandas>=1.5
pip install numpy>=1.21
pip install matplotlib>=3.5
pip install jinja2>=3.0
```

---

## 9. é£é©è¯ä¼°

### 9.1 ææ¯é£?
| é£é©?| é£é©ç­çº§ | ç¼è§£æªæ½ |
|--------|---------|---------|
| **å½å è®¡ç®ç²¾åº¦** | ?| ä½¿ç¨æ åå½å æ¹æ³ |
| **æ¥åçææ§è½** | ?| ä½¿ç¨æ¨¡æ¿ç¼å­ |
| **å¯è§åè´¨?* | ?| ä½¿ç¨æçç»å¾?|

### 9.2 å®æ½é£é©

| é£é©?| é£é©ç­çº§ | ç¼è§£æªæ½ |
|--------|---------|---------|
| **å¼åæ¶é´è¶?* | ?| åé¶æ®µå®?|
| **éæå°é¾** | ?| ååæµè¯ |
| **æ§è½ä¸è¾¾?* | ?| æ§è½ä¼å |

---

## 10. ææ¡£æ²»ç

### 10.1 System_Manifest.mdç´¢å¼

```markdown
#### Layer 6: ç»åä¼å?
##### 6.6 é£é©å½å ç³»ç»
- **æ¨¡åID**: RISK_ATTRIBUTION_001
- **èå¾ææ¡£**: RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾å?- **èè´£**: å¤ç»´åº¦é£é©å½å ãé£é©é¢ç®çæ§ãå½å æ¥åç?- **?*: è®¾è®¡é¶æ®µ
```

### 10.2 æ¨¡åèè´£è¾¹ç

| æ¨¡å | èè´£ | è¾¹ç |
|------|------|------|
| **é£é©å½å ç³»ç»** | é£é©åè§£ãå½å åæãæ¥åç?| **å½å å±é¢** |
| **Barraé£é©æ¨¡å** | é£é©æ¨¡åãé£é©å?| æä¾é£é©æ¨¡åæ°æ® |
| **ç»åä¼å?* | ç»åæéä¼å | ä½¿ç¨å½å ç»æä¼å |

---

## éå½

### A. åèæ?
1. **é£é©å½å çè®º**:
   - Grinold, R.C. and Kahn, R.N. (2000). "Active Portfolio Management"
   - Menchero, J. (2010). "The Characteristics of Factor Attribution"

2. **Brinsonæ¨¡å**:
   - Brinson, G.P., Hood, L.R., and Beebower, G.L. (1986). "Determinants of Portfolio Performance"

3. **å¼æºé¡¹ç®å?*:
   - pyfolio: https://github.com/quantopian/pyfolio
   - empyrical: https://github.com/quantopian/empyrical

### B. æ¯è¯­?
| æ¯è¯­ | å®ä¹ | ä¸ä¸?|
|------|------|--------|
| **é£é©å½å ** | åæé£é©æ¥æº | é£é©åè§£ |
| **è¾¹éé£é©è´¡ç®** | åä½æéå¢å å¸¦æ¥çé£é©å¢?| é£é©åº¦é |
| **ä¸»å¨é£é©** | ç»åç¸å¯¹åºåçé£?| ç¸å¯¹é£é© |
| **é£é©é¢ç®** | åéç»åå å­çé£é©é?| é£é©ç®¡ç |

---

**èå¾çæ¬**: v1.0 | **åå»ºæ¥æ**: 2026-04-03 | **?*: Final | **ä¸ä¸?*: ææ¯è§æ ¼ä¹¦ç¼å

## ð ç¸å³ææ¡£

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [BARRAé£é©æ¨¡åèå¾](./BARRA_RISK_MODEL_BLUEPRINT.md) | BARRA_RISK_MODEL_001 | å¼ºä¾èµ?| æä¾å å­é£é©æ¨¡å |
| [VaR/ESçæ§èå¾](./VAR_ES_MONITORING_BLUEPRINT.md) | VAR_ES_MONITORING_001 | å¼ºä¾èµ?| æä¾VaR/ESææ  |
| [æ°æ®è´¨éçæ§èå¾](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | DATA_QUALITY_MONITORING_001 | ä¸­ä¾èµ?| æä¾æ°æ®è´¨éææ  |

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [ç»åç»©æè¯ä¼°èå¾](./PORTFOLIO_PERFORMANCE_EVALUATION_BLUEPRINT.md) | PORTFOLIO_PERFORMANCE_EVALUATION_001 | å¼ºä¾èµ?| ç»åç»©æè¯ä¼° |
| [é£é©è´¡ç®åæèå¾](./RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md) | RISK_CONTRIBUTION_ANALYSIS_001 | ä¸­ä¾èµ?| é£é©è´¡ç®åæ |
| [ååæµè¯ç³»ç»èå¾](./STRESS_TESTING_SYSTEM_BLUEPRINT.md) | STRESS_TESTING_SYSTEM_001 | ä¸­ä¾èµ?| ååæµè¯ |

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **NumPy** | 1.24+ | æ°å¼è®¡ç®?| [å®æ¹ææ¡£](https://numpy.org/) |
| **Pandas** | 2.0+ | æ°æ®å¤ç | [å®æ¹ææ¡£](https://pandas.pydata.org/) |
| **SciPy** | 1.10+ | ç§å­¦è®¡ç® | [å®æ¹ææ¡£](https://scipy.org/) |

### å¼ç¨å³ç³»å?

```mermaid
graph LR
    A[BARRAé£é©æ¨¡å] --> B[é£é©å½å ç³»ç»]
    C[VaR/ESçæ§] --> B
    D[æ°æ®è´¨éçæ§] --> B
    
    B --> E[ç»åç»©æè¯ä¼°]
    B --> F[é£é©è´¡ç®åæ]
    B --> G[ååæµè¯ç³»ç»]
    
    style B fill:#ff6b6b
    style A fill:#4ecdc4
    style C fill:#45b7d1
```

---

## åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-03 | åå§çæ¬åå»º | ç»åä¼åå±è´è´£äºº |
| v1.0.1 | 2026-04-06 | è¡¥åYAMLå¤´é¨å­æ®µååæ´åå?| å®¡è®¡ç³»ç» |

---

**èå¾çæ¬**: v1.0.1 | **åå»ºæ¥æ**: 2026-04-03 | **ç¶æ?*: Active
