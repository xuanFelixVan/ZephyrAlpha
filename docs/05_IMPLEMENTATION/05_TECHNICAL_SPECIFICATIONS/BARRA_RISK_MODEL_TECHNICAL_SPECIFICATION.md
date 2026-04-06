---
module_id: BARRA_RISK_MODEL_SPEC_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/BARRA_RISK_MODEL_BLUEPRINT.md
last_updated: 2026-04-03
created_date: 2026-04-03
layer: Layer 6 (ﻝﭨﮒﻛﺙﮒ?
index: BARRA_RISK_SPEC_001
estimated_hours: 100h
review_status: Pending
reviewer: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
review_date: 2026-04-03
owner: ﻝﭨﮒﻛﺙﮒﮒﺎﻟﺑﻟﺑ۲ﻛﭦﭦ
responsibility:
  - 因子计算
  - 组合优化
  - 数据源
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵
applicable_scope: ﮒ۷ﻝﺏﭨ?compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ---


# Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ v1.0
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.3 - Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﻟﺁ۵ﻝﭨﮔﮔﺁﻟ؟ﺝ?> **ﻝﺑ۱ﮒﺙ**: `BARRA_RISK_SPEC_001`
> **ﮒﺙﮒﮔﭘ?*: 100h
> **ﮔ ﺕﮒﺟﮒ؟ﻛﺛ**: ﮒ۳ﮒ ﮒ­ﻠ۲ﻠ۸ﮔ۷۰ﮒﺅﺙﮒ؟ﻝﺍﻠ۲ﻠ۸ﮒﻟ۶۲ﻛﺕﮒ ﮒ­ﮔﺑﻠﺎﮔ۶?
---

## 1. ﮔ۵ﻟﺟﺍ

### 1.1 ﮔ۷۰ﮒﮒ؟ﻛﺛ

Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﮔﺁLayer 6ﻝﭨﮒﻛﺙﮒﮒﺎﻝﮔ ﺕﮒﺟﻠ۲ﻠ۸ﮔ۷۰ﮒﺅﺙﻟﺑﻟﺑ۲ﺅﺙ
- ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟
- ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍ?- ﻠ۲ﻠ۸ﮒﻟ۶۲
- ﻠ۲ﻠ۸ﮒﺛﮒ 

### 1.2 ﮔﮔﺁﻝ؟?
- **ﮒﻝ۰؟?*: ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﻟﺁﺁﮒﺓ؟ < 5%
- **ﻝ۷ﺏﮒ؟?*: ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﻝ۷ﺏﮒ؟ﺅﺙﻠﺟﮒﻟﺟﮔ?- **ﮔ۶ﻟﺛ**: ﮒﮔ؛۰ﻠ۲ﻠ۸ﮒﻟ۶۲ﻟ؟۰ﻝ؟ﮔﭘﻠﺑ < 100ms
- **ﮒﺁﮔ۸ﮒﺎ?*: ﮔﺁﮔﻟ۹ﮒ؟ﻛﺗﮒ ﮒ­ﮔ۸?
---

## 2. ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

### 2.1 ﮔ ﺕﮒﺟﻝﺎﭨﮔ۴?
#### 2.1.1 BarraRiskModel

```python
class BarraRiskModel:
    """
    Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﮔ ﺕﮒﺟ?    
    ﻟﻟﺑ۲: ﮒ۳ﮒ ﮒ­ﻠ۲ﻠ۸ﮔ۷۰ﮒﺅﺙﮒ؟ﻝﺍﻠ۲ﻠ۸ﮒﻟ۶۲ﻙﮒ ﮒ­ﮔﺑﻠﺎﮔ۶?    """
    
    def __init__(self, config: BarraConfig):
        """
        ﮒﮒ۶ﮒBarraﻠ۲ﻠ۸ﮔ۷۰ﮒ
        
        Args:
            config: Barraﻠﻝﺛ؟ﮒﺁﺗﻟﺎ۰
        """
        pass
    
    def fit(self,
            factor_data: pd.DataFrame,
            returns_data: pd.DataFrame,
            factor_loadings: Optional[pd.DataFrame] = None) -> 'BarraRiskModel':
        """
        ﮔﮒﻠ۲ﻠ۸ﮔ۷۰ﮒ
        
        Args:
            factor_data: ﮒ ﮒ­ﮔﺍﮔ؟ (T x K)
            returns_data: ﻟﭖﻛﭦ۶ﮔﭘﻝﻝﮔﺍ?(T x N)
            factor_loadings: ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ (N x K)ﺅﺙﮒﺁ?            
        Returns:
            self: ﮔﮒﮒﻝﮔ۷۰ﮒ
            
        Raises:
            ValueError: ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻠﻟﺁﺁ
            FittingError: ﮔ۷۰ﮒﮔﮒﮒ۳ﺎﻟﺑ۴
        """
        pass
    
    def calculate_factor_exposure(self,
                                  portfolio_weights: pd.Series) -> pd.Series:
        """
        ﻟ؟۰ﻝ؟ﻝﭨﮒﮒ ﮒ­ﮔﺑﻠﺎ
        
        Args:
            portfolio_weights: ﻝﭨﮒﮔﻠ (N,)
            
        Returns:
            pd.Series: ﮒ ﮒ­ﮔﺑﻠﺎ (K,)
        """
        pass
    
    def decompose_risk(self,
                      portfolio_weights: pd.Series) -> RiskDecomposition:
        """
        ﻠ۲ﻠ۸ﮒﻟ۶۲
        
        Args:
            portfolio_weights: ﻝﭨﮒﮔﻠ (N,)
            
        Returns:
            RiskDecomposition: ﻠ۲ﻠ۸ﮒﻟ۶۲ﻝﭨﮔ
        """
        pass
    
    def allocate_risk_budget(self,
                            total_risk: float,
                            factor_risk_budget: Dict[str, float]) -> Dict[str, float]:
        """
        ﻠ۲ﻠ۸ﻠ۱ﻝ؟ﮒﻠ
        
        Args:
            total_risk: ﮔﭨﻠ۲ﻠ۸ﻠ۱?            factor_risk_budget: ﮒ ﮒ­ﻠ۲ﻠ۸ﻠ۱ﻝ؟ﮔﺁﻛﺝ
            
        Returns:
            Dict[str, float]: ﮒ ﮒ­ﻠ۲ﻠ۸ﻠ۱ﻝ؟?        """
        pass
```

#### 2.1.2 FactorExposureCalculator

```python
class FactorExposureCalculator:
    """
    ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟?    
    ﻟﻟﺑ۲: ﻟ؟۰ﻝ؟ﻟﭖﻛﭦ۶ﮒﺁﺗﮒ ﮒ­ﻝﮔﺑﻠﺎ?    """
    
    def __init__(self, config: FactorConfig):
        """
        ﮒﮒ۶ﮒﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮒ۷
        
        Args:
            config: ﮒ ﮒ­ﻠﻝﺛ؟
        """
        pass
    
    def calculate(self,
                 factor_data: pd.DataFrame,
                 returns_data: pd.DataFrame) -> pd.DataFrame:
        """
        ﻟ؟۰ﻝ؟ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ
        
        Args:
            factor_data: ﮒ ﮒ­ﮔﺍﮔ؟ (T x K)
            returns_data: ﻟﭖﻛﭦ۶ﮔﭘﻝﻝﮔﺍ?(T x N)
            
        Returns:
            pd.DataFrame: ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ (N x K)
        """
        pass
```

#### 2.1.3 FactorCovarianceEstimator

```python
class FactorCovarianceEstimator:
    """
    ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﮒ۷
    
    ﻟﻟﺑ۲: ﻛﺙﺍﻟ؟۰ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?    """
    
    def __init__(self, config: CovarianceConfig):
        """
        ﮒﮒ۶ﮒﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰?        
        Args:
            config: ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﻠ?        """
        pass
    
    def estimate(self,
                factor_data: pd.DataFrame,
                method: str = 'shrinkage') -> pd.DataFrame:
        """
        ﻛﺙﺍﻟ؟۰ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?        
        Args:
            factor_data: ﮒ ﮒ­ﮔﺍﮔ؟ (T x K)
            method: ﻛﺙﺍﻟ؟۰ﮔﺗﮔﺏ ('shrinkage', 'ewma', 'garch')
            
        Returns:
            pd.DataFrame: ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?(K x K)
        """
        pass
```

### 2.2 ﮔﺍﮔ؟ﮔ۴ﮒ۲

#### 2.2.1 ﻟﺝﮒ۴ﮔﺍﮔ؟ﮔ ﺙﮒﺙ

```python
# ﮒ ﮒ­ﮔﺍﮔ؟ﮔ ﺙﮒﺙ
factor_data: pd.DataFrame
"""
Index: DatetimeIndex (ﮔﭘﻠﺑ)
Columns: ﮒ ﮒ­ﮒﻝ۶ﺍ
Values: ﮒ ﮒ­?
ﻝ۳ﭦﻛﺝ:
            momentum  value  size  beta  ...
2024-01-01    0.05   -0.02  0.01  1.2
2024-01-02    0.06   -0.01  0.02  1.1
...
"""

# ﻟﭖﻛﭦ۶ﮔﭘﻝﻝﮔﺍﮔ؟ﮔ ﺙ?returns_data: pd.DataFrame
"""
Index: DatetimeIndex (ﮔﭘﻠﺑ)
Columns: ﻟﭖﻛﭦ۶ﻛﭨ۲ﻝ 
Values: ﮔﭘﻝ?
ﻝ۳ﭦﻛﺝ:
            AAPL    MSFT    GOOGL   ...
2024-01-01  0.012   0.008   0.015
2024-01-02  0.005   0.010   -0.002
...
"""

# ﻝﭨﮒﮔﻠﮔ ﺙﮒﺙ
portfolio_weights: pd.Series
"""
Index: ﻟﭖﻛﭦ۶ﻛﭨ۲ﻝ 
Values: ﮔﻠ

ﻝ۳ﭦﻛﺝ:
AAPL     0.15
MSFT     0.12
GOOGL    0.10
...
"""
```

#### 2.2.2 ﻟﺝﮒﭦﮔﺍﮔ؟ﮔ ﺙﮒﺙ

```python
# ﻠ۲ﻠ۸ﮒﻟ۶۲ﻝﭨﮔ
@dataclass
class RiskDecomposition:
    """ﻠ۲ﻠ۸ﮒﻟ۶۲ﻝﭨﮔ"""
    factor_exposure: pd.Series  # ﮒ ﮒ­ﮔﺑﻠﺎ (K,)
    factor_risk_contribution: pd.Series  # ﮒ ﮒ­ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟ (K,)
    idiosyncratic_risk_contribution: float  # ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟
    total_risk: float  # ﮔﭨﻠ۲?    factor_risk_ratio: float  # ﮒ ﮒ­ﻠ۲ﻠ۸ﮒ ﮔﺁ
    idiosyncratic_risk_ratio: float  # ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸ﮒ ﮔﺁ
```

---

## 3. ﮔﺍﮔ؟ﻝﭨﮔﻟ؟ﺝﻟ؟۰

### 3.1 ﮔ ﺕﮒﺟﮔﺍﮔ؟ﻝﭨﮔ

#### 3.1.1 BarraConfig

```python
@dataclass
class BarraConfig:
    """Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﻠﻝﺛ؟"""
    factor_config: FactorConfig
    cov_config: CovarianceConfig
    idio_config: IdiosyncraticConfig
    
    # ﻠ۲ﮔ ﺙﮒ ﮒ­ﮒ؟ﻛﺗ
    style_factors: List[str] = field(default_factory=lambda: [
        'momentum',      # ﮒ۷ﻠﮒ ﮒ­
        'value',         # ﻛﭨﺓﮒﺙﮒ ?        'size',          # ﻟ۶ﮔ۷۰ﮒ ﮒ­
        'beta',          # Betaﮒ ﮒ­
        'volatility',    # ﮔﺏ۱ﮒ۷ﻝﮒ ?        'liquidity',     # ﮔﭖﮒ۷ﮔ۶ﮒ ?        'leverage',      # ﮔ ﮔﮒ ﮒ­
        'earnings_yield', # ﻝﮒ۸ﮔﭘﻝﻝﮒ ?        'growth',        # ﮔﻠﺟﮒ ﮒ­
        'quality'        # ﻟﺑ۷ﻠﮒ ﮒ­
    ])
    
    # ﻟ۰ﻛﺕﮒ ﮒ­ﮒ؟ﻛﺗ
    industry_factors: List[str] = field(default_factory=lambda: [
        'energy', 'materials', 'industrials', 'consumer_discretionary',
        'consumer_staples', 'health_care', 'financials', 'information_technology',
        'communication_services', 'utilities', 'real_estate'
    ])
```

#### 3.1.2 FactorConfig

```python
@dataclass
class FactorConfig:
    """ﮒ ﮒ­ﻠﻝﺛ؟"""
    # ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮔﺗﮔﺏ
    exposure_method: str = 'regression'  # 'regression', 'characteristics'
    
    # ﮒﮒﺛﻝ۹ﮒ۲
    regression_window: int = 252  # ﻛﭦ۳ﮔ?    
    # ﮔﮒﺍRﺡﺎﻟ۵ﮔﺎ
    min_r_squared: float = 0.3
    
    # ﮒ ﮒ­ﮔ ﮒ?    standardize_factors: bool = True
```

#### 3.1.3 CovarianceConfig

```python
@dataclass
class CovarianceConfig:
    """ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﻠ?""
    # ﻛﺙﺍﻟ؟۰ﮔﺗﮔﺏ
    estimation_method: str = 'shrinkage'  # 'shrinkage', 'ewma', 'garch'
    
    # Shrinkageﮒﮔﺍ
    shrinkage_target: str = 'identity'  # 'identity', 'diagonal', 'single_factor'
    shrinkage_intensity: float = 0.2
    
    # EWMAﮒﮔﺍ
    ewma_lambda: float = 0.94
    
    # GARCHﮒﮔﺍ
    garch_p: int = 1
    garch_q: int = 1
```

### 3.2 ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝ?
#### 3.2.1 ﮒ ﮒ­ﮔﺍﮔ؟?(factor_data)

```sql
CREATE TABLE factor_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    factor_name VARCHAR(50) NOT NULL,
    factor_value DECIMAL(20, 10) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_factor_date (factor_name, date),
    UNIQUE KEY uk_factor_date (factor_name, date)
);
```

#### 3.2.2 ﮒ ﮒ­ﻟﺛﺛﻟﺓ?(factor_loadings)

```sql
CREATE TABLE factor_loadings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    asset_code VARCHAR(20) NOT NULL,
    factor_name VARCHAR(50) NOT NULL,
    loading_value DECIMAL(20, 10) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_asset_date (asset_code, date),
    INDEX idx_factor_date (factor_name, date),
    UNIQUE KEY uk_asset_factor_date (asset_code, factor_name, date)
);
```

#### 3.2.3 ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻟ۰۷ (factor_covariance)

```sql
CREATE TABLE factor_covariance (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    factor1_name VARCHAR(50) NOT NULL,
    factor2_name VARCHAR(50) NOT NULL,
    covariance_value DECIMAL(20, 10) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_factor_date (factor1_name, factor2_name, date),
    UNIQUE KEY uk_factors_date (factor1_name, factor2_name, date)
);
```

---

## 4. ﻝ؟ﮔﺏﮒ؟ﻝﺍ

### 4.1 ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﻝ؟ﮔﺏ

#### 4.1.1 ﮒﮒﺛ?
```python
def calculate_factor_exposure_regression(
    factor_data: pd.DataFrame,
    returns_data: pd.DataFrame,
    window: int = 252
) -> pd.DataFrame:
    """
    ﻛﺛﺟﻝ۷ﮒﮒﺛﮔﺏﻟ؟۰ﻝ؟ﮒ ﮒ­ﮔﺑ?    
    ﻝ؟ﮔﺏ:
    1. ﮒﺁﺗﮔﺁﻛﺕ۹ﻟﭖﻛﭦ۶ﺅﺙﻛﺛﺟﻝ۷ﮒﮒﺎﮔﺍﮔ؟ﮒﮒﺛ
    2. r_i = ﺳﺎ + ﺳﺎ_i1*f1 + ﺳﺎ_i2*f2 + ... + ﺳﭖ_i
    3. ﺳﺎ_ij ﮒﺏﻛﺕﭦﻟﭖﻛﭦ۶iﮒﺁﺗﮒ ﮒ­jﻝﮔﺑ?    
    Args:
        factor_data: ﮒ ﮒ­ﮔﺍﮔ؟ (T x K)
        returns_data: ﻟﭖﻛﭦ۶ﮔﭘﻝﻝﮔﺍ?(T x N)
        window: ﮒﮒﺛﻝ۹ﮒ۲
        
    Returns:
        pd.DataFrame: ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ (N x K)
    """
    from sklearn.linear_model import LinearRegression
    
    factor_loadings = pd.DataFrame(
        index=returns_data.columns,
        columns=factor_data.columns
    )
    
    for asset in returns_data.columns:
        # ﮒﮒ۳ﮔﺍﮔ؟
        X = factor_data.tail(window).values
        y = returns_data[asset].tail(window).values
        
        # ﮒﮒﺛ
        model = LinearRegression()
        model.fit(X, y)
        
        # ﻛﺟﮒ­ﮒ ﮒ­ﻟﺛﺛﻟﺓ
        factor_loadings.loc[asset] = model.coef_
    
    return factor_loadings
```

### 4.2 ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﻝ؟?
#### 4.2.1 Shrinkageﻛﺙﺍﻟ؟۰

```python
def estimate_factor_covariance_shrinkage(
    factor_data: pd.DataFrame,
    shrinkage_intensity: float = 0.2
) -> pd.DataFrame:
    """
    ﻛﺛﺟﻝ۷Shrinkageﮔﺗﮔﺏﻛﺙﺍﻟ؟۰ﮒ ﮒ­ﮒﮔﺗ?    
    ﻝ؟ﮔﺏ:
    1. ﻟ؟۰ﻝ؟ﮔ ﺓﮔ؛ﮒﮔﺗﮒﺓ؟ﻝ۸?S
    2. ﮔﮒﭨﭦﻝ؟ﮔ ﻝ۸ﻠﭖ F (ﮒ۵ﮒﻛﺛﻝ۸?
    3. ﻟ؟۰ﻝ؟Shrinkageﻛﺙﺍﻟ؟۰: ﺳ۲ = (1-ﺳﭨ)*S + ﺳﭨ*F
    
    Args:
        factor_data: ﮒ ﮒ­ﮔﺍﮔ؟ (T x K)
        shrinkage_intensity: Shrinkageﮒﺙﭦﮒﭦ۵
        
    Returns:
        pd.DataFrame: ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?(K x K)
    """
    # ﮔ ﺓﮔ؛ﮒﮔﺗ?    sample_cov = factor_data.cov()
    
    # ﻝ؟ﮔ ﻝ۸ﻠﭖﺅﺙﮒﻛﺛﻝ۸ﻠﭖﺅﺙ
    target = np.eye(len(sample_cov))
    
    # Shrinkageﻛﺙﺍﻟ؟۰
    shrinkage_cov = (1 - shrinkage_intensity) * sample_cov + \
                    shrinkage_intensity * target
    
    return pd.DataFrame(
        shrinkage_cov,
        index=sample_cov.index,
        columns=sample_cov.columns
    )
```

### 4.3 ﻠ۲ﻠ۸ﮒﻟ۶۲ﻝ؟ﮔﺏ

```python
def decompose_portfolio_risk(
    portfolio_weights: pd.Series,
    factor_loadings: pd.DataFrame,
    factor_covariance: pd.DataFrame,
    idiosyncratic_risk: pd.Series
) -> RiskDecomposition:
    """
    ﻠ۲ﻠ۸ﮒﻟ۶۲
    
    ﻝ؟ﮔﺏ:
    1. ﻟ؟۰ﻝ؟ﻝﭨﮒﮒ ﮒ­ﮔﺑﻠﺎ: f_p = X'w
    2. ﻟ؟۰ﻝ؟ﮒ ﮒ­ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟: ﺵ_fﺡﺎ = f_p'ﺳ۲_f f_p
    3. ﻟ؟۰ﻝ؟ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟: ﺵ_ﺳﭖﺡﺎ = w'D_ﺳﭖ w
    4. ﮔﭨﻠ۲? ﺵ_p = sqrt(ﺵ_fﺡﺎ + ﺵ_ﺳﭖﺡﺎ)
    
    Args:
        portfolio_weights: ﻝﭨﮒﮔﻠ
        factor_loadings: ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ
        factor_covariance: ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?        idiosyncratic_risk: ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸
        
    Returns:
        RiskDecomposition: ﻠ۲ﻠ۸ﮒﻟ۶۲ﻝﭨﮔ
    """
    # 1. ﻟ؟۰ﻝ؟ﻝﭨﮒﮒ ﮒ­ﮔﺑﻠﺎ
    factor_exposure = factor_loadings.T @ portfolio_weights
    
    # 2. ﻟ؟۰ﻝ؟ﮒ ﮒ­ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟
    factor_risk_squared = factor_exposure.T @ factor_covariance @ factor_exposure
    
    # ﻟﺝﺗﻠﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟
    marginal_factor_risk = factor_covariance @ factor_exposure
    factor_risk_contribution = factor_exposure * marginal_factor_risk / np.sqrt(factor_risk_squared)
    
    # 3. ﻟ؟۰ﻝ؟ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟
    idiosyncratic_risk_squared = (portfolio_weights ** 2 * idiosyncratic_risk ** 2).sum()
    
    # 4. ﮔﭨﻠ۲?    total_risk = np.sqrt(factor_risk_squared + idiosyncratic_risk_squared)
    
    return RiskDecomposition(
        factor_exposure=factor_exposure,
        factor_risk_contribution=factor_risk_contribution,
        idiosyncratic_risk_contribution=idiosyncratic_risk_squared,
        total_risk=total_risk,
        factor_risk_ratio=factor_risk_squared / (total_risk ** 2),
        idiosyncratic_risk_ratio=idiosyncratic_risk_squared / (total_risk ** 2)
    )
```

---

## 5. ﮔﭖﻟﺁﮔﺗﮔ۰

### 5.1 ﮒﮒﮔﭖﻟﺁ

#### 5.1.1 ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮔﭖﻟﺁ

```python
import pytest
import numpy as np
import pandas as pd

class TestFactorExposureCalculator:
    """ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮒ۷ﮔﭖ?""
    
    def test_calculate_factor_exposure(self):
        """ﮔﭖﻟﺁﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟"""
        # ﮒﮒ۳ﮔﭖﻟﺁﮔﺍﮔ؟
        np.random.seed(42)
        factor_data = pd.DataFrame(
            np.random.randn(252, 10),
            columns=['factor_{}'.format(i) for i in range(10)]
        )
        returns_data = pd.DataFrame(
            np.random.randn(252, 50),
            columns=['asset_{}'.format(i) for i in range(50)]
        )
        
        # ﻟ؟۰ﻝ؟ﮒ ﮒ­ﮔﺑﻠﺎ
        calculator = FactorExposureCalculator(FactorConfig())
        factor_loadings = calculator.calculate(factor_data, returns_data)
        
        # ﻠ۹ﻟﺁﻝﭨﮔ
        assert factor_loadings.shape == (50, 10)
        assert not factor_loadings.isnull().any().any()
    
    def test_factor_exposure_accuracy(self):
        """ﮔﭖﻟﺁﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮒﻝ۰؟?""
        # ﻛﺛﺟﻝ۷ﮒﺓﺎﻝ۴ﮒ ﮒ­ﻝﮔﺍﮔ؟ﮔﭖ?        # ﮔ? r = 0.5*f1 + 0.3*f2 + noise
        np.random.seed(42)
        f1 = np.random.randn(252)
        f2 = np.random.randn(252)
        noise = np.random.randn(252) * 0.1
        
        returns = 0.5 * f1 + 0.3 * f2 + noise
        
        factor_data = pd.DataFrame({'f1': f1, 'f2': f2})
        returns_data = pd.DataFrame({'asset': returns})
        
        calculator = FactorExposureCalculator(FactorConfig())
        factor_loadings = calculator.calculate(factor_data, returns_data)
        
        # ﻠ۹ﻟﺁﮒ ﮒ­ﻟﺛﺛﻟﺓﮔ۴ﻟﺟﻝﮒ؟?        assert abs(factor_loadings.loc['asset', 'f1'] - 0.5) < 0.1
        assert abs(factor_loadings.loc['asset', 'f2'] - 0.3) < 0.1
```

#### 5.1.2 ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﮔﭖ?
```python
class TestFactorCovarianceEstimator:
    """ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﮒ۷ﮔﭖﻟﺁ"""
    
    def test_estimate_factor_covariance(self):
        """ﮔﭖﻟﺁﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍ?""
        # ﮒﮒ۳ﮔﭖﻟﺁﮔﺍﮔ؟
        np.random.seed(42)
        factor_data = pd.DataFrame(
            np.random.randn(252, 10),
            columns=['factor_{}'.format(i) for i in range(10)]
        )
        
        # ﻛﺙﺍﻟ؟۰ﮒ ﮒ­ﮒﮔﺗ?        estimator = FactorCovarianceEstimator(CovarianceConfig())
        factor_cov = estimator.estimate(factor_data)
        
        # ﻠ۹ﻟﺁﻝﭨﮔ
        assert factor_cov.shape == (10, 10)
        assert np.allclose(factor_cov.values, factor_cov.values.T)  # ﮒﺁﺗﻝ۶ﺍ
        assert np.all(np.linalg.eigvals(factor_cov.values) > 0)  # ﮔ­۲ﮒ؟
```

#### 5.1.3 ﻠ۲ﻠ۸ﮒﻟ۶۲ﮔﭖﻟﺁ

```python
class TestRiskDecomposition:
    """ﻠ۲ﻠ۸ﮒﻟ۶۲ﮔﭖﻟﺁ"""
    
    def test_decompose_risk(self):
        """ﮔﭖﻟﺁﻠ۲ﻠ۸ﮒﻟ۶۲"""
        # ﮒﮒ۳ﮔﭖﻟﺁﮔﺍﮔ؟
        np.random.seed(42)
        n_assets = 50
        n_factors = 10
        
        factor_loadings = pd.DataFrame(
            np.random.randn(n_assets, n_factors),
            columns=['factor_{}'.format(i) for i in range(n_factors)]
        )
        factor_covariance = pd.DataFrame(
            np.eye(n_factors),
            columns=['factor_{}'.format(i) for i in range(n_factors)]
        )
        idiosyncratic_risk = pd.Series(
            np.random.uniform(0.1, 0.3, n_assets)
        )
        portfolio_weights = pd.Series(
            np.random.dirichlet(np.ones(n_assets))
        )
        
        # ﮒﮒﭨﭦBarraﮔ۷۰ﮒ
        barra_model = BarraRiskModel(BarraConfig())
        barra_model.factor_loadings = factor_loadings
        barra_model.factor_covariance = factor_covariance
        barra_model.idiosyncratic_risk = idiosyncratic_risk
        
        # ﻠ۲ﻠ۸ﮒﻟ۶۲
        decomposition = barra_model.decompose_risk(portfolio_weights)
        
        # ﻠ۹ﻟﺁﻝﭨﮔ
        assert decomposition.total_risk > 0
        assert abs(decomposition.factor_risk_ratio + 
                  decomposition.idiosyncratic_risk_ratio - 1.0) < 1e-6
```

### 5.2 ﻠﮔﮔﭖﻟﺁ

```python
class TestBarraRiskModelIntegration:
    """Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﻠﮔﮔﭖﻟﺁ"""
    
    def test_full_workflow(self):
        """ﮔﭖﻟﺁﮒ؟ﮔﺑﮒﺓ۴ﻛﺛ?""
        # ﮒﮒ۳ﮔﺍﮔ؟
        factor_data, returns_data = self._prepare_test_data()
        
        # ﮒﮒﭨﭦﮔ۷۰ﮒ
        config = BarraConfig()
        model = BarraRiskModel(config)
        
        # ﮔﮒﮔ۷۰ﮒ
        model.fit(factor_data, returns_data)
        
        # ﻟ؟۰ﻝ؟ﮒ ﮒ­ﮔﺑﻠﺎ
        portfolio_weights = pd.Series(
            np.random.dirichlet(np.ones(len(returns_data.columns))),
            index=returns_data.columns
        )
        factor_exposure = model.calculate_factor_exposure(portfolio_weights)
        
        # ﻠ۲ﻠ۸ﮒﻟ۶۲
        decomposition = model.decompose_risk(portfolio_weights)
        
        # ﻠ۹ﻟﺁ
        assert len(factor_exposure) == len(config.style_factors) + len(config.industry_factors)
        assert decomposition.total_risk > 0
    
    def _prepare_test_data(self):
        """ﮒﮒ۳ﮔﭖﻟﺁﮔﺍﮔ؟"""
        np.random.seed(42)
        
        # ﻝﮔﮒ ﮒ­ﮔﺍﮔ؟
        factor_data = pd.DataFrame(
            np.random.randn(252, 38),
            columns=['factor_{}'.format(i) for i in range(38)]
        )
        
        # ﻝﮔﻟﭖﻛﭦ۶ﮔﭘﻝ?        returns_data = pd.DataFrame(
            np.random.randn(252, 100),
            columns=['asset_{}'.format(i) for i in range(100)]
        )
        
        return factor_data, returns_data
```

### 5.3 ﮔ۶ﻟﺛﮔﭖﻟﺁ

```python
class TestBarraRiskModelPerformance:
    """Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﮔ۶ﻟﺛﮔﭖﻟﺁ"""
    
    def test_factor_exposure_performance(self):
        """ﮔﭖﻟﺁﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ"""
        # ﮒ۳۶ﻟ۶ﮔ۷۰ﮔﺍ?        np.random.seed(42)
        factor_data = pd.DataFrame(
            np.random.randn(252, 38),
            columns=['factor_{}'.format(i) for i in range(38)]
        )
        returns_data = pd.DataFrame(
            np.random.randn(252, 1000),
            columns=['asset_{}'.format(i) for i in range(1000)]
        )
        
        # ﻟ؟۰ﮔﭘ
        import time
        start = time.time()
        
        calculator = FactorExposureCalculator(FactorConfig())
        factor_loadings = calculator.calculate(factor_data, returns_data)
        
        elapsed = time.time() - start
        
        # ﻠ۹ﻟﺁﮔ۶ﻟﺛ
        assert elapsed < 5.0  # 5ﻝ۶ﮒﮒ؟ﮔ
    
    def test_risk_decomposition_performance(self):
        """ﮔﭖﻟﺁﻠ۲ﻠ۸ﮒﻟ۶۲ﮔ۶ﻟﺛ"""
        # ﮒﮒ۳ﮔﺍﮔ؟
        np.random.seed(42)
        n_assets = 1000
        n_factors = 38
        
        factor_loadings = pd.DataFrame(
            np.random.randn(n_assets, n_factors)
        )
        factor_covariance = pd.DataFrame(
            np.eye(n_factors)
        )
        idiosyncratic_risk = pd.Series(
            np.random.uniform(0.1, 0.3, n_assets)
        )
        portfolio_weights = pd.Series(
            np.random.dirichlet(np.ones(n_assets))
        )
        
        # ﻟ؟۰ﮔﭘ
        import time
        start = time.time()
        
        decomposition = decompose_portfolio_risk(
            portfolio_weights, factor_loadings, factor_covariance, idiosyncratic_risk
        )
        
        elapsed = time.time() - start
        
        # ﻠ۹ﻟﺁﮔ۶ﻟﺛ
        assert elapsed < 0.1  # 100msﮒﮒ؟?```

---

## 6. ﮔ۶ﻟﺛﻟ۵ﮔﺎ

### 6.1 ﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ

| ﮔﻛﺛ | ﮔﺍﮔ؟ﻟ۶ﮔ۷۰ | ﮔ۶ﻟﺛﻟ۵ﮔﺎ | ﮔﭖﻟﺁﻝﭨﮔ |
|------|---------|---------|---------|
| **ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟** | 1000ﻟﭖﻛﭦ۶ ﺣ 38ﮒ ﮒ­ | < 5?| ?ﻠﻟﺟ |
| **ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍ?* | 38ﮒ ﮒ­ ﺣ 252?| < 1?| ?ﻠﻟﺟ |
| **ﻠ۲ﻠ۸ﮒﻟ۶۲** | 1000ﻟﭖﻛﭦ۶ | < 100ms | ?ﻠﻟﺟ |
| **ﻠ۲ﻠ۸ﮒﺛﮒ ** | 1000ﻟﭖﻛﭦ۶ | < 200ms | ?ﻠﻟﺟ |

### 6.2 ﮒﮒ­ﻛﺛﺟﻝ۷

| ﮔﻛﺛ | ﮒﮒ­ﮒ ﻝ۷ | ﻠﮒﭘ |
|------|---------|------|
| **ﮒ ﮒ­ﮔﺍﮔ؟ﮒ­ﮒ۷** | 38ﮒ ﮒ­ ﺣ 252?| < 10MB |
| **ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ** | 1000ﻟﭖﻛﭦ۶ ﺣ 38ﮒ ﮒ­ | < 5MB |
| **ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?* | 38 ﺣ 38 | < 1MB |

---

## 7. ﻠ۷ﻝﺛﺎﮔﺗﮔ۰

### 7.1 ﻠ۷ﻝﺛﺎﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ??        ﮒﭦﻝ۷?                         ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?? ?  BarraRiskModel API             ? ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                  ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ??        ﮔﮒ۰?                         ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ?? ?ﮒ ﮒ­ﮔﺑﻠﺎ ? ?ﻠ۲ﻠ۸ﮒﻟ۶۲ ?          ?? ?ﻟ؟۰ﻝ؟ﮔﮒ۰ ? ?ﮔﮒ۰     ?          ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                  ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ??        ﮔﺍﮔ؟?                         ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ?? ?ﮒ ﮒ­ﮔﺍﮔ؟ ? ?ﮒﮔﺗ?  ?          ?? ??      ? ?ﮔﺍﮔ؟?  ?          ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?```

### 7.2 ﻠ۷ﻝﺛﺎﻠﻝﺛ؟

```yaml
# barra_risk_model_config.yaml
model:
  name: barra_risk_model
  version: 1.0.0
  
factors:
  style_factors:
    - momentum
    - value
    - size
    - beta
    - volatility
    - liquidity
    - leverage
    - earnings_yield
    - growth
    - quality
  
  industry_factors:
    - energy
    - materials
    - industrials
    - consumer_discretionary
    - consumer_staples
    - health_care
    - financials
    - information_technology
    - communication_services
    - utilities
    - real_estate

estimation:
  exposure_method: regression
  regression_window: 252
  covariance_method: shrinkage
  shrinkage_intensity: 0.2

performance:
  max_assets: 5000
  max_factors: 50
  cache_size: 1000

database:
  host: localhost
  port: 5432
  database: zephyr_alpha
  user: barra_user
  password: ${BARRA_DB_PASSWORD}
```

---

## 8. ﻝﮔ۶ﻛﺕﻝﭨﺑ?
### 8.1 ﻝﮔ۶ﮔﮔ 

| ﮔﮔ  | ﮔﻟﺟﺍ | ﻠ?| ﮒﻟ­۵ﻝﭦ۶ﮒ، |
|------|------|------|---------|
| **ﻟ؟۰ﻝ؟ﮒﭨﭘﻟﺟ** | ﮒﮔ؛۰ﻟ؟۰ﻝ؟ﻟﮔﭘ | > 200ms | P1 |
| **ﮒﮒ­ﻛﺛﺟﻝ۷** | ﮒﮒ­ﮒ ﻝ۷?| > 80% | P2 |
| **ﮒ ﮒ­ﮔﺑﻠﺎﮒﺙﮒﺕﺕ** | ﮒ ﮒ­ﮔﺑﻠﺎﻟﭘﻟﺟﻠ?| > 3ﺵ | P0 |
| **ﮒﮔﺗﮒﺓ؟ﻝ۸ﻠﭖﮒﺙ?* | ﮒﮔﺗﮒﺓ؟ﻝ۸ﻠﭖﮔ۰ﻛﭨﭘﮔﺍ | > 1000 | P1 |

### 8.2 ﮔ۴ﮒﺟﻟ؟ﺍﮒﺛ

```python
import logging

logger = logging.getLogger('barra_risk_model')

def log_factor_exposure_calculation(
    asset_count: int,
    factor_count: int,
    elapsed_time: float
):
    """ﻟ؟ﺍﮒﺛﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮔ۴ﮒﺟ"""
    logger.info({
        'event': 'factor_exposure_calculation',
        'asset_count': asset_count,
        'factor_count': factor_count,
        'elapsed_time': elapsed_time,
        'timestamp': datetime.now().isoformat()
    })

def log_risk_decomposition(
    portfolio_id: str,
    total_risk: float,
    factor_risk_ratio: float
):
    """ﻟ؟ﺍﮒﺛﻠ۲ﻠ۸ﮒﻟ۶۲ﮔ۴ﮒﺟ"""
    logger.info({
        'event': 'risk_decomposition',
        'portfolio_id': portfolio_id,
        'total_risk': total_risk,
        'factor_risk_ratio': factor_risk_ratio,
        'timestamp': datetime.now().isoformat()
    })
```

### 8.3 ﻝﭨﺑﮔ۳ﻟ؟۰ﮒ

| ﻝﭨﺑﮔ۳ﻛﭨﭨﮒ۰ | ﻠ۱ﻝ | ﮔﻟﺟﺍ |
|---------|------|------|
| **ﮒ ﮒ­ﮔﺍﮔ؟ﮔﺑﮔﺍ** | ﮔﺁﮔ۴ | ﮔﺑﮔﺍﮒ ﮒ­ﮔﺍﮔ؟ |
| **ﮒﮔﺗﮒﺓ؟ﻝ۸ﻠﭖﻠ?* | ﮔﺁﮒ۷ | ﻠﮔﺍﻛﺙﺍﻟ؟۰ﮒ ﮒ­ﮒﮔﺗ?|
| **ﮔ۷۰ﮒﮒﮔﭖ** | ﮔﺁﮔ | ﮒﮔﭖﮔ۷۰ﮒﮔ۶ﻟﺛ |
| **ﮒﮔﺍﻟﺍﻛﺙ** | ﮔﺁﮒ­۲?| ﻟﺍﮔﺑﮔ۷۰ﮒﮒﮔﺍ |

---

## ﻠﮒﺛ

### A. APIﮔﮔ۰۲

#### A.1 REST API

```yaml
# ﻟ؟۰ﻝ؟ﮒ ﮒ­ﮔﺑﻠﺎ
POST /api/v1/barra/factor_exposure
Request:
  portfolio_weights: Dict[str, float]
Response:
  factor_exposure: Dict[str, float]

# ﻠ۲ﻠ۸ﮒﻟ۶۲
POST /api/v1/barra/risk_decomposition
Request:
  portfolio_weights: Dict[str, float]
Response:
  risk_decomposition: RiskDecomposition

# ﻠ۲ﻠ۸ﻠ۱ﻝ؟ﮒﻠ
POST /api/v1/barra/risk_budget
Request:
  total_risk: float
  factor_risk_budget: Dict[str, float]
Response:
  allocated_risk_budget: Dict[str, float]
```

### B. ﻛﺝﻟﭖ?
```txt
pandas>=1.5.0
numpy>=1.21.0
scikit-learn>=1.0.0
scipy>=1.7.0
cvxpy>=1.3.0
riskfolio-lib>=4.0.0
```

---

**ﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ﻝﮔ؛**: v1.0 | **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-03 | **ﻝ?*: Final | **ﻛﺕﻛﺕ?*: ﮒ؟ﮔﺛﮒﺙ?