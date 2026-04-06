---
module_id: IMPL_BARRA_RISK_MODEL_BP_001
version: 1.0.2
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: '2026-04-06'
created_date: 2026-04-03
layer: Layer 6 (组合优化层)
index: BARRA_RISK_MODEL_001
estimated_hours: 100h
estimated_effort: 2.5周
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-03
owner: 组合优化层负责人
standard_type: 专业量化机构蓝图文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
personal_development: true
ai_maintenance: true
open_source_dependency: numpy, pandas, scipy
priority: P0
---

?---
module_id: IMPL_BARRA_RISK_MODEL_BP_001
version: 1.0.1
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-03
created_date: 2026-04-03
layer: Layer 6 (����Ż�??
index: BARRA_RISK_MODEL_001
estimated_hours: 100h
review_status: Pending
reviewer: ��ϯ���������
review_date: 2026-04-03
owner: ����Ż��㸺����
standard_type: רҵ����������ͼ�ĵ�
applicable_scope: ȫϵ??compliance_level: רҵ��׼
parent_document: ../INDEX.md
implementation_status: ��ƽ׶�
personal_development: true
ai_maintenance: true
---

# Barra����ģ����ͼ v1.0

> �������ϵͳ v5.3 - Barra����ģ����ϸ���
> **����**: `BARRA_RISK_001`
> **����ʱ??*: 100h��Լ2.5�ܣ�
> **���Ķ�λ**: �����ӷ���ģ�ͣ�ʵ�ַ��շֽ⡢���ӱ�¶���ơ�����Ԥ���??> **�Ա����**: ��ˮ����Bridgewater Associates??> **���˿�������??*: ???? ��ȫ����
> **AIά���Ѷ�**: ??
---

## 1. ����

### 1.1 ��Ʊ�����ҵ��Ŀ??
**ҵ����??*??- ��ǰϵͳ���л�����Э���������ƣ�ȱ�������ӷ���ģ��
- �޷���ȷ�ֽ���Ϸ�����Դ�����ӷ�??vs ���ʷ���??- �޷��������ӱ�¶��������Ϸ��ղ��ɿ�
- �޷�ʵ�־�ȷ�ķ���Ԥ���??
**����ʹ??*??- �޶����ӷ���ģ��ʵ��
- �����ӱ�¶������??- �޷��շֽ����������
- �����ӷ���Ԥ�������??
**Ԥ�ڼ�??*??- ���շֽ⾫������??0%
- ���ӱ�¶������������??- ����Ԥ����侫�ȣ���??0%
- ���չ��������������??- Ϊ��ˮ����ƽ���ṩ����֧??
### 1.2 ������λ��ܹ����??
**Layer��λ**: Layer 6 - ����Ż��㣨���չ����Ӳ�??
**ģ�����**: ����ģ�飨P0����

**�ܹ���ɫ**: 
- ��Ϊ��ˮ����ƽ�۵ĺ���������ṩ��ȷ�ķ��շ�??- ��Ϊ����Ż��ķ���Լ�����������ӱ�¶
- ��Ϊ����Ԥ�����Ļ�����ʵ�־�ϸ�����չ���

### 1.3 ���Ĺ����嵥

1. **���ӱ�¶����**: ��������ڸ������ϵı�¶??2. **���շֽ�**: ����Ϸ��շֽ�Ϊ���ӷ��պ����ʷ�??3. **����Э�����??*: �������Ӽ��Э�����??4. **���ʷ��չ���**: ���Ƹ��ʲ������ʷ���
5. **���չ���**: ����������Դ�����ɹ���??6. **����Ԥ�����**: �������ӷ��ս���Ԥ�����

---

## 2. �ܹ����

### 2.1 ϵͳ�ܹ�??
```
������������������������������������������������������������������������������������������������������������������������������������????                   Barra����ģ��ϵͳ�ܹ�                          ??������������������������������������������������������������������������������������������������������������������������������������????                                                                ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ����??                                       ?? ???? ?? ����������������������������������������������?? ����������������������������������������������??    ?? ???? ?? ??��������              ?? ??�ʲ���������??       ??    ?? ???? ?? ??- �������??0����    ?? ??- ��ʷ����??         ??    ?? ???? ?? ??- ��ҵ����??8����    ?? ??- �г�����            ??    ?? ???? ?? ����������������������������������������������?? ����������������������������������������������??    ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ���ӱ�¶����??                               ?? ???? ?? ����������������������������������������������������������������������������������������������������������?? ?? ???? ?? ?? Factor Exposure Calculator                        ?? ?? ???? ?? ?? - ������ӱ�¶����                                 ?? ?? ???? ?? ?? - ��ҵ���ӱ�¶����                                 ?? ?? ???? ?? ?? - ���ӱ�¶���󹹽�                                 ?? ?? ???? ?? ����������������������������������������������������������������������������������������������������������?? ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ����ģ�͹���??                               ?? ???? ?? ����������������������?? ����������������������?? ����������������������??              ?? ???? ?? ??����Э���  ??���ʷ��� ?? ??Э�������               ?? ???? ?? ??����     ?? ??����     ?? ??�ع�      ??              ?? ???? ?? ����������������������?? ����������������������?? ����������������������??              ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ���շֽ�������                              ?? ???? ?? ����������������������?? ����������������������?? ����������������������??              ?? ???? ?? ??���շֽ� ?? ??���չ��� ?? ??���ձ��� ??              ?? ???? ?? ??         ?? ??         ?? ??         ??              ?? ???? ?? ����������������������?? ����������������������?? ����������������������??              ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ????                         ??                                     ???? ����������������������������������������������������������������������������������������������������������������������?? ???? ??             ���??                                       ?? ???? ?? ����������������������?? ����������������������?? ����������������������??              ?? ???? ?? ??���ӱ�¶ ?? ??���շֽ� ?? ??����Ԥ�� ??              ?? ???? ?? ??����     ?? ??���     ?? ??����     ??              ?? ???? ?? ����������������������?? ����������������������?? ����������������������??              ?? ???? ����������������������������������������������������������������������������������������������������������������������?? ??������������������������������������������������������������������������������������������������������������������������������������??```

### 2.2 ��������??
```
�������� + �ʲ���������??    ??���ӱ�¶���㣨�ع������
    ??����Э������ƣ�ͳ��ģ��??    ??���ʷ��չ��ƣ��в������
    ??Э���������??    ??���շֽ����??    ??��������ӱ�¶�����շֽ⡢����Ԥ??```

---

## 3. ����ģ�����

### 3.1 Barra����ģ�ͺ����ࣨBarraRiskModel??
```python
class BarraRiskModel:
    """
    Barra����ģ�ͺ���??    
    ����: BARRA_RISK_001-M01
    ְ��: �����ӷ���ģ�ͣ�ʵ�ַ��շֽ⡢���ӱ�¶��??    ����: �������ݡ��ʲ�����������
    ���: ���ӱ�¶�����շֽ⡢����Ԥ??    """
    
    def __init__(self, config: BarraConfig):
        self.config = config
        self.factor_exposure_calculator = FactorExposureCalculator(config.factor_config)
        self.factor_covariance_estimator = FactorCovarianceEstimator(config.cov_config)
        self.idiosyncratic_risk_estimator = IdiosyncraticRiskEstimator(config.idio_config)
        self.risk_decomposer = RiskDecomposer()
        self.risk_attributor = RiskAttributor()
        
    def fit(self, 
            factor_data: pd.DataFrame, 
            returns_data: pd.DataFrame,
            factor_loadings: Optional[pd.DataFrame] = None) -> 'BarraRiskModel':
        """
        ���Barra����ģ��
        
        Args:
            factor_data: �������ݣ�DataFrame����Ϊ���ӣ�
            returns_data: �ʲ����������ݣ�DataFrame����Ϊ�ʲ���
            factor_loadings: �����غɾ��󣨿�ѡ������֪��
            
        Returns:
            self: ��Ϻ��ģ��ʵ��
        """
        # 1. �������ӱ�¶
        if factor_loadings is None:
            self.factor_loadings = self.factor_exposure_calculator.calculate(
                factor_data, returns_data
            )
        else:
            self.factor_loadings = factor_loadings
        
        # 2. ��������Э�����??        self.factor_covariance = self.factor_covariance_estimator.estimate(
            factor_data
        )
        
        # 3. �������ʷ���
        self.idiosyncratic_risk = self.idiosyncratic_risk_estimator.estimate(
            returns_data, self.factor_loadings
        )
        
        # 4. �ع��ʲ�Э�����??        self.asset_covariance = self._reconstruct_covariance(
            self.factor_loadings, self.factor_covariance, self.idiosyncratic_risk
        )
        
        return self
    
    def calculate_factor_exposure(self, 
                                 portfolio_weights: pd.Series) -> pd.Series:
        """
        ������ϵ����ӱ�??        
        Args:
            portfolio_weights: ���Ȩ�أ�Series������Ϊ�ʲ�??            
        Returns:
            pd.Series: ���ӱ�¶������Ϊ����??        """
        # ������ӱ�¶ = ���Ȩ�� �� �����غɾ���
        factor_exposure = portfolio_weights @ self.factor_loadings
        
        return factor_exposure
    
    def decompose_risk(self, 
                      portfolio_weights: pd.Series) -> RiskDecomposition:
        """
        �ֽ���Ϸ���
        
        Args:
            portfolio_weights: ���Ȩ�أ�Series������Ϊ�ʲ�??            
        Returns:
            RiskDecomposition: ���շֽ���
        """
        # 1. ����������ӱ�¶
        factor_exposure = self.calculate_factor_exposure(portfolio_weights)
        
        # 2. �������ӷ��չ���
        factor_risk_contribution = self.risk_decomposer.calculate_factor_risk(
            factor_exposure, self.factor_covariance
        )
        
        # 3. �������ʷ��չ���
        idiosyncratic_risk_contribution = self.risk_decomposer.calculate_idiosyncratic_risk(
            portfolio_weights, self.idiosyncratic_risk
        )
        
        # 4. �����ܷ�??        total_risk = np.sqrt(
            factor_risk_contribution.sum() + idiosyncratic_risk_contribution
        )
        
        return RiskDecomposition(
            factor_exposure=factor_exposure,
            factor_risk_contribution=factor_risk_contribution,
            idiosyncratic_risk_contribution=idiosyncratic_risk_contribution,
            total_risk=total_risk,
            factor_risk_ratio=factor_risk_contribution.sum() / total_risk**2,
            idiosyncratic_risk_ratio=idiosyncratic_risk_contribution / total_risk**2
        )
    
    def attribute_risk(self, 
                      portfolio_weights: pd.Series,
                      benchmark_weights: Optional[pd.Series] = None) -> RiskAttribution:
        """
        ���չ������
        
        Args:
            portfolio_weights: ���Ȩ��
            benchmark_weights: ��׼Ȩ�أ���ѡ��
            
        Returns:
            RiskAttribution: ���չ�����
        """
        # 1. ��Ϸ��շֽ�
        portfolio_decomposition = self.decompose_risk(portfolio_weights)
        
        # 2. ��׼���շֽ⣨���У�
        if benchmark_weights is not None:
            benchmark_decomposition = self.decompose_risk(benchmark_weights)
        else:
            benchmark_decomposition = None
        
        # 3. ���չ���
        attribution = self.risk_attributor.attribute(
            portfolio_decomposition, benchmark_decomposition
        )
        
        return attribution
    
    def allocate_risk_budget(self,
                            target_risk: float,
                            risk_budget_constraints: Optional[Dict] = None) -> RiskBudgetAllocation:
        """
        ����Ԥ�����
        
        Args:
            target_risk: Ŀ�����ˮƽ���껯������??            risk_budget_constraints: ����Ԥ��Լ������ѡ��
            
        Returns:
            RiskBudgetAllocation: ����Ԥ����䷽��
        """
        # 1. ��������ӵķ���Ԥ��
        factor_risk_budget = self._calculate_factor_risk_budget(
            target_risk, risk_budget_constraints
        )
        
        # 2. �������ʷ���Ԥ��
        idiosyncratic_risk_budget = self._calculate_idiosyncratic_risk_budget(
            target_risk, factor_risk_budget
        )
        
        return RiskBudgetAllocation(
            factor_risk_budget=factor_risk_budget,
            idiosyncratic_risk_budget=idiosyncratic_risk_budget,
            total_risk_budget=target_risk
        )
    
    def _reconstruct_covariance(self,
                                factor_loadings: pd.DataFrame,
                                factor_covariance: pd.DataFrame,
                                idiosyncratic_risk: pd.Series) -> pd.DataFrame:
        """�ع��ʲ�Э�����??""
        # �� = B * F * B' + D
        # B: �����غɾ���
        # F: ����Э�����??        # D: ���ʷ��նԽǾ���
        
        B = factor_loadings.values
        F = factor_covariance.values
        D = np.diag(idiosyncratic_risk.values)
        
        asset_covariance = B @ F @ B.T + D
        
        return pd.DataFrame(
            asset_covariance,
            index=factor_loadings.index,
            columns=factor_loadings.index
        )
```

### 3.2 ���ӱ�¶��������FactorExposureCalculator??
```python
class FactorExposureCalculator:
    """
    ���ӱ�¶����??    
    ����: BARRA_RISK_001-M02
    ְ��: �����ʲ��ڸ������ϵı�¶??    """
    
    def __init__(self, config: FactorConfig):
        self.config = config
        self.style_factors = config.style_factors  # 10�������??        self.industry_factors = config.industry_factors  # 28����ҵ��??        
    def calculate(self,
                 factor_data: pd.DataFrame,
                 returns_data: pd.DataFrame) -> pd.DataFrame:
        """
        �������ӱ�¶����
        
        Args:
            factor_data: ��������
            returns_data: �ʲ���������??            
        Returns:
            pd.DataFrame: ���ӱ�¶������Ϊ�ʲ�����Ϊ����??        """
        # 1. ������ӱ�¶���㣨�ع������
        style_exposures = self._calculate_style_exposures(factor_data, returns_data)
        
        # 2. ��ҵ���ӱ�¶���㣨�Ʊ���??        industry_exposures = self._calculate_industry_exposures(factor_data)
        
        # 3. �ϲ����ӱ�¶����
        factor_loadings = pd.concat([style_exposures, industry_exposures], axis=1)
        
        return factor_loadings
    
    def _calculate_style_exposures(self,
                                   factor_data: pd.DataFrame,
                                   returns_data: pd.DataFrame) -> pd.DataFrame:
        """���������ӱ�¶"""
        style_exposures = {}
        
        for asset in returns_data.columns:
            # ��ÿ���ʲ�����ʱ�����л�??            # r_i = �� + ��_1*f_1 + ... + ��_k*f_k + ��
            X = factor_data[self.style_factors].values
            y = returns_data[asset].values
            
            # ʹ��OLS�ع�
            model = LinearRegression()
            model.fit(X, y)
            
            style_exposures[asset] = model.coef_
        
        return pd.DataFrame(style_exposures, index=self.style_factors).T
    
    def _calculate_industry_exposures(self,
                                     factor_data: pd.DataFrame) -> pd.DataFrame:
        """������ҵ���ӱ�¶���Ʊ���??""
        # ��ҵ���ӱ�¶���Ʊ���??????        industry_exposures = pd.get_dummies(factor_data['industry'])
        
        return industry_exposures
```

### 3.3 ����Э�����������FactorCovarianceEstimator??
```python
class FactorCovarianceEstimator:
    """
    ����Э���������
    
    ����: BARRA_RISK_001-M03
    ְ��: �������Ӽ��Э�����??    """
    
    def __init__(self, config: CovarianceConfig):
        self.config = config
        self.estimation_method = config.estimation_method  # 'sample', 'shrinkage', 'ewma'
        
    def estimate(self, factor_data: pd.DataFrame) -> pd.DataFrame:
        """
        ��������Э�����??        
        Args:
            factor_data: ��������
            
        Returns:
            pd.DataFrame: ����Э�����??        """
        if self.estimation_method == 'sample':
            # ����Э�����??            factor_cov = factor_data.cov()
            
        elif self.estimation_method == 'shrinkage':
            # Ledoit-Wolf��������
            from sklearn.covariance import LedoitWolf
            lw = LedoitWolf()
            lw.fit(factor_data.values)
            factor_cov = pd.DataFrame(
                lw.covariance_,
                index=factor_data.columns,
                columns=factor_data.columns
            )
            
        elif self.estimation_method == 'ewma':
            # ָ����Ȩ�ƶ�ƽ��
            factor_cov = self._ewma_covariance(factor_data)
            
        else:
            raise ValueError(f"��֧�ֵĹ��Ʒ���: {self.estimation_method}")
        
        return factor_cov
    
    def _ewma_covariance(self, 
                        factor_data: pd.DataFrame,
                        lambda_: float = 0.94) -> pd.DataFrame:
        """EWMAЭ�����??""
        # ָ����ȨЭ�����??        weights = np.array([(1 - lambda_) * lambda_**i 
                           for i in range(len(factor_data))])
        weights = weights[::-1] / weights.sum()
        
        # ��ȨЭ��??        demeaned = factor_data - factor_data.mean()
        factor_cov = (demeaned.T * weights) @ demeaned
        
        return factor_cov
```

### 3.4 ���ʷ��չ�������IdiosyncraticRiskEstimator??
```python
class IdiosyncraticRiskEstimator:
    """
    ���ʷ��չ���??    
    ����: BARRA_RISK_001-M04
    ְ��: ���Ƹ��ʲ������ʷ���
    """
    
    def __init__(self, config: IdiosyncraticConfig):
        self.config = config
        
    def estimate(self,
                returns_data: pd.DataFrame,
                factor_loadings: pd.DataFrame) -> pd.Series:
        """
        �������ʷ���
        
        Args:
            returns_data: �ʲ���������??            factor_loadings: �����غɾ���
            
        Returns:
            pd.Series: ���ʷ��գ�����Ϊ�ʲ�??        """
        idiosyncratic_risk = {}
        
        for asset in returns_data.columns:
            # ����в�����??            # ��_i = r_i - B_i * F
            asset_returns = returns_data[asset].values
            asset_loadings = factor_loadings.loc[asset].values
            
            # ʹ������ģ��Ԥ������??            predicted_returns = asset_loadings @ factor_loadings.T @ returns_data.T
            
            # ����в�
            residuals = asset_returns - predicted_returns
            
            # �������ʷ��գ��в��׼��??            idiosyncratic_risk[asset] = np.std(residuals, ddof=1)
        
        return pd.Series(idiosyncratic_risk)
```

### 3.5 ���շֽ�����RiskDecomposer??
```python
class RiskDecomposer:
    """
    ���շֽ�??    
    ����: BARRA_RISK_001-M05
    ְ��: ����Ϸ��շֽ�Ϊ���ӷ��պ����ʷ�??    """
    
    def calculate_factor_risk(self,
                             factor_exposure: pd.Series,
                             factor_covariance: pd.DataFrame) -> pd.Series:
        """
        �������ӷ��չ���
        
        Args:
            factor_exposure: ���ӱ�¶
            factor_covariance: ����Э�����??            
        Returns:
            pd.Series: �����ӵķ��չ���
        """
        # ���ӷ��չ��� = f_i * (F * f)_i
        # f: ���ӱ�¶����
        # F: ����Э�����??        
        F_f = factor_covariance @ factor_exposure
        factor_risk_contribution = factor_exposure * F_f
        
        return factor_risk_contribution
    
    def calculate_idiosyncratic_risk(self,
                                    portfolio_weights: pd.Series,
                                    idiosyncratic_risk: pd.Series) -> float:
        """
        �������ʷ��չ���
        
        Args:
            portfolio_weights: ���Ȩ��
            idiosyncratic_risk: ���ʷ���
            
        Returns:
            float: ���ʷ��չ���
        """
        # ���ʷ��չ��� = �� w_i^2 * ��_i^2
        # w: ���Ȩ��
        # ��: ���ʷ���
        
        idiosyncratic_risk_contribution = (
            portfolio_weights**2 * idiosyncratic_risk**2
        ).sum()
        
        return idiosyncratic_risk_contribution
```

### 3.6 �����ඨ??
```python
@dataclass
class BarraConfig:
    """Barra����ģ������"""
    factor_config: FactorConfig
    cov_config: CovarianceConfig
    idio_config: IdiosyncraticConfig
    
@dataclass
class FactorConfig:
    """��������"""
    style_factors: List[str] = field(default_factory=lambda: [
        'momentum', 'value', 'size', 'quality', 'volatility',
        'growth', 'leverage', 'liquidity', 'yield', 'beta'
    ])  # 10�������??    industry_factors: List[str] = field(default_factory=lambda: [
        # GICSһ����ҵ��11����
        'energy', 'materials', 'industrials', 'consumer_discretionary',
        'consumer_staples', 'healthcare', 'financials', 'technology',
        'communication', 'utilities', 'real_estate',
        # GICS������ҵ��չ��24����
        'energy_equipment', 'chemicals', 'construction', 'aerospace_defense',
        'auto_components', 'consumer_services', 'food_beverage', 'pharmaceuticals',
        'biotechnology', 'banks', 'insurance', 'software', 'semiconductors',
        'telecom', 'media', 'electric_utilities', 'gas_utilities',
        'retail_reits', 'residential_reits', 'diversified_financials',
        'capital_markets', 'real_estate_management', 'trading_companies',
        'commercial_services'
    ])  # 35����ҵ���ӣ�11��һ�� + 24��������չ��
    
    # ��ҵ���Ӳ㼶����
    industry_hierarchy: Dict[str, List[str]] = field(default_factory=lambda: {
        'energy': ['energy_equipment'],
        'materials': ['chemicals', 'construction'],
        'industrials': ['aerospace_defense', 'auto_components', 'commercial_services'],
        'consumer_discretionary': ['consumer_services', 'auto_components'],
        'consumer_staples': ['food_beverage'],
        'healthcare': ['pharmaceuticals', 'biotechnology'],
        'financials': ['banks', 'insurance', 'diversified_financials', 'capital_markets'],
        'technology': ['software', 'semiconductors'],
        'communication': ['telecom', 'media'],
        'utilities': ['electric_utilities', 'gas_utilities'],
        'real_estate': ['retail_reits', 'residential_reits', 'real_estate_management']
    })��ʾ��??    
@dataclass
class CovarianceConfig:
    """Э���������??""
    estimation_method: str = 'shrinkage'  # 'sample', 'shrinkage', 'ewma'
    lookback_period: int = 252  # �ؿ��ڣ������գ�
    
@dataclass
class IdiosyncraticConfig:
    """���ʷ��չ�������"""
    estimation_method: str = 'residual'  # 'residual', 'garch'
```

---

## 4. ����ģ�Ͷ���

### 4.1 ��������ģ��

```python
@dataclass
class FactorData:
    """��������"""
    date: datetime
    style_factors: Dict[str, float]  # �������??    industry: str  # ��ҵ����
    
@dataclass
class ReturnsData:
    """��������??""
    date: datetime
    asset_returns: Dict[str, float]  # �ʲ�����??```

### 4.2 �������ģ��

```python
@dataclass
class RiskDecomposition:
    """���շֽ���"""
    factor_exposure: pd.Series  # ���ӱ�¶
    factor_risk_contribution: pd.Series  # ���ӷ��չ���
    idiosyncratic_risk_contribution: float  # ���ʷ��չ���
    total_risk: float  # �ܷ�??    factor_risk_ratio: float  # ���ӷ���ռ��
    idiosyncratic_risk_ratio: float  # ���ʷ���ռ��
    
@dataclass
class RiskAttribution:
    """���չ�����"""
    factor_attribution: pd.DataFrame  # ���ӹ���
    industry_attribution: pd.DataFrame  # ��ҵ����
    total_attribution: pd.DataFrame  # �ܹ�??    
@dataclass
class RiskBudgetAllocation:
    """����Ԥ�����"""
    factor_risk_budget: pd.Series  # ���ӷ���Ԥ��
    idiosyncratic_risk_budget: float  # ���ʷ���Ԥ��
    total_risk_budget: float  # �ܷ���Ԥ??```

---

## 5. ���ɷ���

### 5.1 ������Ż�������

```python
class PortfolioOptimizer:
    """����Ż���������Barra����ģ��??""
    
    def __init__(self, barra_model: BarraRiskModel):
        self.barra_model = barra_model
        
    def optimize_with_factor_constraints(self,
                                        expected_returns: pd.Series,
                                        factor_exposure_limits: Dict[str, Tuple[float, float]],
                                        target_risk: float) -> pd.Series:
        """������Լ��������Ż�"""
        # 1. ��ȡBarra����ģ�Ͳ���
        factor_loadings = self.barra_model.factor_loadings
        factor_covariance = self.barra_model.factor_covariance
        idiosyncratic_risk = self.barra_model.idiosyncratic_risk
        
        # 2. �����Ż�����
        n_assets = len(expected_returns)
        w = cp.Variable(n_assets)
        
        # Ŀ�꺯�������Ԥ������
        objective = cp.Maximize(expected_returns.values @ w)
        
        # Լ������
        constraints = [
            cp.sum(w) == 1,  # Ȩ�غ�Ϊ1
            w >= 0,  # �Ǹ�Ȩ��
        ]
        
        # ���ӱ�¶Լ��
        for factor, (lower, upper) in factor_exposure_limits.items():
            factor_loading = factor_loadings[factor].values
            constraints.append(factor_loading @ w >= lower)
            constraints.append(factor_loading @ w <= upper)
        
        # ����Լ��
        portfolio_risk = cp.sqrt(
            cp.quad_form(w, self.barra_model.asset_covariance.values)
        )
        constraints.append(portfolio_risk <= target_risk)
        
        # ����Ż�����
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        return pd.Series(w.value, index=expected_returns.index)
```

### 5.2 �����Ԥ��ϵͳ��??
```python
class RiskBudgetSystem:
    """����Ԥ��ϵͳ������Barra����ģ��??""
    
    def __init__(self, barra_model: BarraRiskModel):
        self.barra_model = barra_model
        
    def allocate_risk_budget_by_factors(self,
                                       target_risk: float,
                                       factor_risk_targets: Dict[str, float]) -> RiskBudgetAllocation:
        """�������ӵķ���Ԥ���??""
        # 1. �������ӷ���Ԥ��
        factor_risk_budget = pd.Series(factor_risk_targets)
        
        # 2. �������ʷ���Ԥ��
        factor_risk_total = np.sqrt((factor_risk_budget**2).sum())
        idiosyncratic_risk_budget = np.sqrt(
            target_risk**2 - factor_risk_total**2
        )
        
        return RiskBudgetAllocation(
            factor_risk_budget=factor_risk_budget,
            idiosyncratic_risk_budget=idiosyncratic_risk_budget,
            total_risk_budget=target_risk
        )
```

---

## 6. ʵʩ·��??
### 6.1 �����׶Σ�2.5�ܣ�

**Week 1: ����ģ�鿪??*
- Day 1-2: ���ӱ�¶����??- Day 3-4: ����Э���������
- Day 5: ���ʷ��չ���??
**Week 2: ���շֽ��뼯??*
- Day 1-2: ���շֽ��������??- Day 3-4: ������Ż�������
- Day 5: �����Ԥ��ϵͳ��??
**Week 3: ��������??*
- Day 1-2: ��Ԫ����
- Day 3: ���ɲ���
- Day 4: �ĵ���д
- Day 5: �����Ż�

### 6.2 ���??
| ���??| ʱ�� | ����??| ���ձ�׼ |
|--------|------|--------|----------|
| **M1: ���ӱ�¶�������** | Day 2 | ���ӱ�¶����??| ��¶������ȷ |
| **M2: Э���������??* | Day 4 | Э��������� | ���ƺ��� |
| **M3: ���շֽ����** | Day 7 | ���շֽ�??| �ֽ�׼ȷ |
| **M4: �������** | Day 9 | ����ϵͳ | ���нӿ���??|
| **M5: ����ͨ��** | Day 12 | ���Ա��� | ���в���ͨ�� |

---

## 7. Ԥ����������

### 7.1 ��������

| ָ�� | ��ǰˮƽ | Ŀ��ˮƽ | �������� |
|------|---------|---------|---------|
| **���շֽ⾫��** | ���� | ��ȷ | +50% |
| **���ӱ�¶����** | ??| ??| �������� |
| **����Ԥ�㾫��** | 70% | 90% | +20% |
| **���չ�������** | ??| ??| �������� |

### 7.2 ������??
- ??ʵ����ˮ����ƽ�ۺ�������
- ??��ȷ�ķ��շֽ������
- ??���ӱ�¶��������
- ??����Ԥ�㾫ϸ����??- ??Ϊ����Ż��ṩ����Լ??
---

## 8. ����ջѡ��

### 8.1 ��������??
| ���� | �汾 | ��??| ��Ҫ??|
|------|------|------|--------|
| **riskfolio-lib** | ??.0 | ����ģ�͡�����Ԥ??| ���� |
| **CVXPY** | ??.3 | Լ���Ż� | ���� |
| **scikit-learn** | ??.0 | �ع������������??| ���� |
| **pandas** | ??.5 | ���ݴ��� | ���� |
| **numpy** | ??.21 | ��ֵ��??| ���� |

### 8.2 ��װ����

```bash
pip install riskfolio-lib>=3.0
pip install cvxpy>=1.3
pip install scikit-learn>=1.0
pip install pandas>=1.5
pip install numpy>=1.21
```

---

## 9. ��������

### 9.1 ������??
| ����??| ���յȼ� | �����ʩ |
|--------|---------|---------|
| **������������** | ??| ������Դ��֤��������??|
| **ģ�͹������** | ??| ʹ���������ơ�������??|
| **��������** | ??| ʹ�����������㡢�����??|

### 9.2 ʵʩ����

| ����??| ���յȼ� | �����ʩ |
|--------|---------|---------|
| **����ʱ�䳬??* | ??| �ֽ׶�ʵʩ����̱����� |
| **��������** | ??| ��ֲ��ԡ��ӿ��ĵ���??|
| **���ܲ���??* | ??| �����Ż����㷨��??|

---

## 10. �ĵ�����

### 10.1 System_Manifest.md����

```markdown
#### Layer 6: ����Ż�??
##### 6.4 Barra����ģ��
- **ģ��ID**: BARRA_RISK_001
- **��ͼ�ĵ�**: [BARRA_RISK_MODEL_BLUEPRINT.md](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/BARRA_RISK_MODEL_BLUEPRINT.md)
- **���������**: ����??- **ְ��**: �����ӷ���ģ�͡����շֽ⡢���ӱ�¶��??- **״??*: ��ƽ׶�
```

### 10.2 ģ��ְ��߽�

| ģ�� | ְ�� | �߽� |
|------|------|------|
| **Barra����ģ��** | ���ӱ�¶���㡢���շֽ⡢���չ�??| **����ģ�Ͳ���** |
| **����Ż�??* | ���Ȩ���Ż� | ʹ��Barraģ�͵ķ���Լ??|
| **����Ԥ��ϵͳ** | ����Ԥ����� | ʹ��Barraģ�͵ķ��շ�??|

---

## ��¼

### A. �ο���??
1. **Barra����ģ��**:
   - Barra Risk Model Handbook
   - Grinold, R.C. and Kahn, R.N. (2000). "Active Portfolio Management"

2. **����ģ������**:
   - Ross, S.A. (1976). "The Arbitrage Theory of Capital Asset Pricing"
   - Fama, E.F. and French, K.R. (1993). "Common Risk Factors in the Returns on Stocks and Bonds"

3. **��Դ��Ŀ��??*:
   - riskfolio-lib: https://github.com/dcajasn/Riskfolio-Lib
   - PyPortfolioOpt: https://github.com/robertmartin8/PyPortfolioOpt

### B. ����??
| ���� | ���� | ����??|
|------|------|--------|
| **Barraģ��** | �����ӷ���ģ??| ���շֽ����??|
| **���ӱ�¶** | �ʲ������ӵ�����??| �����غ� |
| **���ʷ���** | �޷������ӽ��͵ķ��� | �в���� |
| **���չ���** | ����������Դ | ���շֽ� |

---

**��ͼ�汾**: v1.0 | **��������**: 2026-04-03 | **״??*: Final | **��һ??*: ����������д

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-03 | 初始版本创建 | 组合优化层负责人 |
| v1.0.1 | 2026-04-06 | 补充YAML头部字段和变更历史 | 审计系统 |

---

**蓝图版本**: v1.0.1 | **创建日期**: 2026-04-03 | **状态**: Active
