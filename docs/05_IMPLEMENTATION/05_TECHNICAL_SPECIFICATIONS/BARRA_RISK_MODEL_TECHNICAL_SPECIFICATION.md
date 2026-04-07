﻿---
module_id: BARRA_RISK_MODEL_SPEC_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/BARRA_RISK_MODEL_BLUEPRINT.md
last_updated: 2026-04-03
created_date: 2026-04-03
layer: Layer 6 (ﻝﭨﮒﻛﺙﮒ?
index: BARRA_RISK_SPEC_001
estimated_hours: 100h
review_status: Pending
reviewer: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
review_date: 2026-04-03
owner: ﻝﭨﮒﻛﺙﮒﮒﺎﻟﺑﻟﺑ۲ﻛﭦﭦ
responsibility:
  - 实施指南、部署文档
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵
applicable_scope: ﮒ۷ﻝﺏﭨ?compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ
---
---


# Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ v1.0
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.3 - Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﻟﺁ۵ﻝﭨﮔﮔﺁﻟ؟ﺝ?> **ﻝﺑ۱ﮒﺙ**: `BARRA_RISK_SPEC_001`
> **ﮒﺙﮒﮔﭘ?*: 100h
> **ﮔ ﺕﮒﺟﮒ؟ﻛﺛ**: ﮒ۳ﮒ ﮒ­ﻠ۲ﻠ۸ﮔ۷۰ﮒﺅﺙﮒ؟ﻝﺍﻠ۲ﻠ۸ﮒﻟ۶۲ﻛﺕﮒ ﮒ­ﮔﺑﻠﺎﮔ۶?
---

## 1. ﮔ۵ﻟﺟﺍ

### 1.1 ﮔ۷۰ﮒﮒ؟ﻛﺛ

Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﮔﺁLayer 6ﻝﭨﮒﻛﺙﮒﮒﺎﻝﮔ ﺕﮒﺟﻠ۲ﻠ۸ﮔ۷۰ﮒﺅﺙﻟﺑﻟﺑ۲ﺅﺙ
- ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟
- ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍ?- ﻠ۲ﻠ۸ﮒﻟ۶۲
- ﻠ۲ﻠ۸ﮒﺛﮒ 

### 1.2 ﮔﮔﺁﻝ؟?
- **ﮒﻝ۰؟?*: ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﻟﺁﺁﮒﺓ؟ < 5%
- **ﻝ۷ﺏﮒ؟?*: ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﻝ۷ﺏﮒ؟ﺅﺙﻠﺟﮒﻟﺟﮔ?- **ﮔ۶ﻟﺛ**: ﮒﮔ؛۰ﻠ۲ﻠ۸ﮒﻟ۶۲ﻟ؟۰ﻝ؟ﮔﭘﻠﺑ < 100ms
- **ﮒﺁﮔ۸ﮒﺎ?*: ﮔﺁﮔﻟ۹ﮒ؟ﻛﺗﮒ ﮒ­ﮔ۸?
---

## 2. ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

### 2.1 ﮔ ﺕﮒﺟﻝﺎﭨﮔ۴?
#### 2.1.1 BarraRiskModel

```python
class BarraRiskModel:
    """
    Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﮔ ﺕﮒﺟ?    
    ﻟﻟﺑ۲: ﮒ۳ﮒ ﮒ­ﻠ۲ﻠ۸ﮔ۷۰ﮒﺅﺙﮒ؟ﻝﺍﻠ۲ﻠ۸ﮒﻟ۶۲ﻙﮒ ﮒ­ﮔﺑﻠﺎﮔ۶?    """
    
    def __init__(self, config: BarraConfig):
        """
        ﮒﮒ۶ﮒBarraﻠ۲ﻠ۸ﮔ۷۰ﮒ
        
        Args:
            config: Barraﻠﻝﺛ؟ﮒﺁﺗﻟﺎ۰
        """
        pass
    
    def fit(self,
            factor_data: pd.DataFrame,
            returns_data: pd.DataFrame,
            factor_loadings: Optional[pd.DataFrame] = None) -> 'BarraRiskModel':
        """
        ﮔﮒﻠ۲ﻠ۸ﮔ۷۰ﮒ
        
        Args:
            factor_data: ﮒ ﮒ­ﮔﺍﮔ؟ (T x K)
            returns_data: ﻟﭖﻛﭦ۶ﮔﭘﻝﻝﮔﺍ?(T x N)
            factor_loadings: ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ (N x K)ﺅﺙﮒﺁ?            
        Returns:
            self: ﮔﮒﮒﻝﮔ۷۰ﮒ
            
        Raises:
            ValueError: ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻠﻟﺁﺁ
            FittingError: ﮔ۷۰ﮒﮔﮒﮒ۳ﺎﻟﺑ۴
        """
        pass
    
    def calculate_factor_exposure(self,
                                  portfolio_weights: pd.Series) -> pd.Series:
        """
        ﻟ؟۰ﻝ؟ﻝﭨﮒﮒ ﮒ­ﮔﺑﻠﺎ
        
        Args:
            portfolio_weights: ﻝﭨﮒﮔﻠ (N,)
            
        Returns:
            pd.Series: ﮒ ﮒ­ﮔﺑﻠﺎ (K,)
        """
        pass
    
    def decompose_risk(self,
                      portfolio_weights: pd.Series) -> RiskDecomposition:
        """
        ﻠ۲ﻠ۸ﮒﻟ۶۲
        
        Args:
            portfolio_weights: ﻝﭨﮒﮔﻠ (N,)
            
        Returns:
            RiskDecomposition: ﻠ۲ﻠ۸ﮒﻟ۶۲ﻝﭨﮔ
        """
        pass
    
    def allocate_risk_budget(self,
                            total_risk: float,
                            factor_risk_budget: Dict[str, float]) -> Dict[str, float]:
        """
        ﻠ۲ﻠ۸ﻠ۱ﻝ؟ﮒﻠ
        
        Args:
            total_risk: ﮔﭨﻠ۲ﻠ۸ﻠ۱?            factor_risk_budget: ﮒ ﮒ­ﻠ۲ﻠ۸ﻠ۱ﻝ؟ﮔﺁﻛﺝ
            
        Returns:
            Dict[str, float]: ﮒ ﮒ­ﻠ۲ﻠ۸ﻠ۱ﻝ؟?        """
        pass
```

#### 2.1.2 FactorExposureCalculator

```python
class FactorExposureCalculator:
    """
    ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟?    
    ﻟﻟﺑ۲: ﻟ؟۰ﻝ؟ﻟﭖﻛﭦ۶ﮒﺁﺗﮒ ﮒ­ﻝﮔﺑﻠﺎ?    """
    
    def __init__(self, config: FactorConfig):
        """
        ﮒﮒ۶ﮒﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮒ۷
        
        Args:
            config: ﮒ ﮒ­ﻠﻝﺛ؟
        """
        pass
    
    def calculate(self,
                 factor_data: pd.DataFrame,
                 returns_data: pd.DataFrame) -> pd.DataFrame:
        """
        ﻟ؟۰ﻝ؟ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ
        
        Args:
            factor_data: ﮒ ﮒ­ﮔﺍﮔ؟ (T x K)
            returns_data: ﻟﭖﻛﭦ۶ﮔﭘﻝﻝﮔﺍ?(T x N)
            
        Returns:
            pd.DataFrame: ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ (N x K)
        """
        pass
```

#### 2.1.3 FactorCovarianceEstimator

```python
class FactorCovarianceEstimator:
    """
    ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﮒ۷
    
    ﻟﻟﺑ۲: ﻛﺙﺍﻟ؟۰ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?    """
    
    def __init__(self, config: CovarianceConfig):
        """
        ﮒﮒ۶ﮒﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰?        
        Args:
            config: ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﻠ?        """
        pass
    
    def estimate(self,
                factor_data: pd.DataFrame,
                method: str = 'shrinkage') -> pd.DataFrame:
        """
        ﻛﺙﺍﻟ؟۰ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?        
        Args:
            factor_data: ﮒ ﮒ­ﮔﺍﮔ؟ (T x K)
            method: ﻛﺙﺍﻟ؟۰ﮔﺗﮔﺏ ('shrinkage', 'ewma', 'garch')
            
        Returns:
            pd.DataFrame: ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?(K x K)
        """
        pass
```

### 2.2 ﮔﺍﮔ؟ﮔ۴ﮒ۲

#### 2.2.1 ﻟﺝﮒ۴ﮔﺍﮔ؟ﮔ ﺙﮒﺙ

```python
# ﮒ ﮒ­ﮔﺍﮔ؟ﮔ ﺙﮒﺙ
factor_data: pd.DataFrame
"""
Index: DatetimeIndex (ﮔﭘﻠﺑ)
Columns: ﮒ ﮒ­ﮒﻝ۶ﺍ
Values: ﮒ ﮒ­?
ﻝ۳ﭦﻛﺝ:
            momentum  value  size  beta  ...
2024-01-01    0.05   -0.02  0.01  1.2
2024-01-02    0.06   -0.01  0.02  1.1
...
"""

# ﻟﭖﻛﭦ۶ﮔﭘﻝﻝﮔﺍﮔ؟ﮔ ﺙ?returns_data: pd.DataFrame
"""
Index: DatetimeIndex (ﮔﭘﻠﺑ)
Columns: ﻟﭖﻛﭦ۶ﻛﭨ۲ﻝ 
Values: ﮔﭘﻝ?
ﻝ۳ﭦﻛﺝ:
            AAPL    MSFT    GOOGL   ...
2024-01-01  0.012   0.008   0.015
2024-01-02  0.005   0.010   -0.002
...
"""

# ﻝﭨﮒﮔﻠﮔ ﺙﮒﺙ
portfolio_weights: pd.Series
"""
Index: ﻟﭖﻛﭦ۶ﻛﭨ۲ﻝ 
Values: ﮔﻠ

ﻝ۳ﭦﻛﺝ:
AAPL     0.15
MSFT     0.12
GOOGL    0.10
...
"""
```

#### 2.2.2 ﻟﺝﮒﭦﮔﺍﮔ؟ﮔ ﺙﮒﺙ

```python
# ﻠ۲ﻠ۸ﮒﻟ۶۲ﻝﭨﮔ
@dataclass
class RiskDecomposition:
    """ﻠ۲ﻠ۸ﮒﻟ۶۲ﻝﭨﮔ"""
    factor_exposure: pd.Series  # ﮒ ﮒ­ﮔﺑﻠﺎ (K,)
    factor_risk_contribution: pd.Series  # ﮒ ﮒ­ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟ (K,)
    idiosyncratic_risk_contribution: float  # ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟
    total_risk: float  # ﮔﭨﻠ۲?    factor_risk_ratio: float  # ﮒ ﮒ­ﻠ۲ﻠ۸ﮒ ﮔﺁ
    idiosyncratic_risk_ratio: float  # ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸ﮒ ﮔﺁ
```

---

## 3. ﮔﺍﮔ؟ﻝﭨﮔﻟ؟ﺝﻟ؟۰

### 3.1 ﮔ ﺕﮒﺟﮔﺍﮔ؟ﻝﭨﮔ

#### 3.1.1 BarraConfig

```python
@dataclass
class BarraConfig:
    """Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﻠﻝﺛ؟"""
    factor_config: FactorConfig
    cov_config: CovarianceConfig
    idio_config: IdiosyncraticConfig
    
    # ﻠ۲ﮔ ﺙﮒ ﮒ­ﮒ؟ﻛﺗ
    style_factors: List[str] = field(default_factory=lambda: [
        'momentum',      # ﮒ۷ﻠﮒ ﮒ­
        'value',         # ﻛﭨﺓﮒﺙﮒ ?        'size',          # ﻟ۶ﮔ۷۰ﮒ ﮒ­
        'beta',          # Betaﮒ ﮒ­
        'volatility',    # ﮔﺏ۱ﮒ۷ﻝﮒ ?        'liquidity',     # ﮔﭖﮒ۷ﮔ۶ﮒ ?        'leverage',      # ﮔ ﮔﮒ ﮒ­
        'earnings_yield', # ﻝﮒ۸ﮔﭘﻝﻝﮒ ?        'growth',        # ﮔﻠﺟﮒ ﮒ­
        'quality'        # ﻟﺑ۷ﻠﮒ ﮒ­
    ])
    
    # ﻟ۰ﻛﺕﮒ ﮒ­ﮒ؟ﻛﺗ
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
    """ﮒ ﮒ­ﻠﻝﺛ؟"""
    # ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮔﺗﮔﺏ
    exposure_method: str = 'regression'  # 'regression', 'characteristics'
    
    # ﮒﮒﺛﻝ۹ﮒ۲
    regression_window: int = 252  # ﻛﭦ۳ﮔ?    
    # ﮔﮒﺍRﺡﺎﻟ۵ﮔﺎ
    min_r_squared: float = 0.3
    
    # ﮒ ﮒ­ﮔ ﮒ?    standardize_factors: bool = True
```

#### 3.1.3 CovarianceConfig

```python
@dataclass
class CovarianceConfig:
    """ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﻠ?""
    # ﻛﺙﺍﻟ؟۰ﮔﺗﮔﺏ
    estimation_method: str = 'shrinkage'  # 'shrinkage', 'ewma', 'garch'
    
    # Shrinkageﮒﮔﺍ
    shrinkage_target: str = 'identity'  # 'identity', 'diagonal', 'single_factor'
    shrinkage_intensity: float = 0.2
    
    # EWMAﮒﮔﺍ
    ewma_lambda: float = 0.94
    
    # GARCHﮒﮔﺍ
    garch_p: int = 1
    garch_q: int = 1
```

### 3.2 ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝ?
#### 3.2.1 ﮒ ﮒ­ﮔﺍﮔ؟?(factor_data)

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

#### 3.2.2 ﮒ ﮒ­ﻟﺛﺛﻟﺓ?(factor_loadings)

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

#### 3.2.3 ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻟ۰۷ (factor_covariance)

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

## 4. ﻝ؟ﮔﺏﮒ؟ﻝﺍ

### 4.1 ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﻝ؟ﮔﺏ

#### 4.1.1 ﮒﮒﺛ?
```python
def calculate_factor_exposure_regression(
    factor_data: pd.DataFrame,
    returns_data: pd.DataFrame,
    window: int = 252
) -> pd.DataFrame:
    """
    ﻛﺛﺟﻝ۷ﮒﮒﺛﮔﺏﻟ؟۰ﻝ؟ﮒ ﮒ­ﮔﺑ?    
    ﻝ؟ﮔﺏ:
    1. ﮒﺁﺗﮔﺁﻛﺕ۹ﻟﭖﻛﭦ۶ﺅﺙﻛﺛﺟﻝ۷ﮒﮒﺎﮔﺍﮔ؟ﮒﮒﺛ
    2. r_i = ﺳﺎ + ﺳﺎ_i1*f1 + ﺳﺎ_i2*f2 + ... + ﺳﭖ_i
    3. ﺳﺎ_ij ﮒﺏﻛﺕﭦﻟﭖﻛﭦ۶iﮒﺁﺗﮒ ﮒ­jﻝﮔﺑ?    
    Args:
        factor_data: ﮒ ﮒ­ﮔﺍﮔ؟ (T x K)
        returns_data: ﻟﭖﻛﭦ۶ﮔﭘﻝﻝﮔﺍ?(T x N)
        window: ﮒﮒﺛﻝ۹ﮒ۲
        
    Returns:
        pd.DataFrame: ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ (N x K)
    """
    from sklearn.linear_model import LinearRegression
    
    factor_loadings = pd.DataFrame(
        index=returns_data.columns,
        columns=factor_data.columns
    )
    
    for asset in returns_data.columns:
        # ﮒﮒ۳ﮔﺍﮔ؟
        X = factor_data.tail(window).values
        y = returns_data[asset].tail(window).values
        
        # ﮒﮒﺛ
        model = LinearRegression()
        model.fit(X, y)
        
        # ﻛﺟﮒ­ﮒ ﮒ­ﻟﺛﺛﻟﺓ
        factor_loadings.loc[asset] = model.coef_
    
    return factor_loadings
```

### 4.2 ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﻝ؟?
#### 4.2.1 Shrinkageﻛﺙﺍﻟ؟۰

```python
def estimate_factor_covariance_shrinkage(
    factor_data: pd.DataFrame,
    shrinkage_intensity: float = 0.2
) -> pd.DataFrame:
    """
    ﻛﺛﺟﻝ۷Shrinkageﮔﺗﮔﺏﻛﺙﺍﻟ؟۰ﮒ ﮒ­ﮒﮔﺗ?    
    ﻝ؟ﮔﺏ:
    1. ﻟ؟۰ﻝ؟ﮔ ﺓﮔ؛ﮒﮔﺗﮒﺓ؟ﻝ۸?S
    2. ﮔﮒﭨﭦﻝ؟ﮔ ﻝ۸ﻠﭖ F (ﮒ۵ﮒﻛﺛﻝ۸?
    3. ﻟ؟۰ﻝ؟Shrinkageﻛﺙﺍﻟ؟۰: ﺳ۲ = (1-ﺳﭨ)*S + ﺳﭨ*F
    
    Args:
        factor_data: ﮒ ﮒ­ﮔﺍﮔ؟ (T x K)
        shrinkage_intensity: Shrinkageﮒﺙﭦﮒﭦ۵
        
    Returns:
        pd.DataFrame: ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?(K x K)
    """
    # ﮔ ﺓﮔ؛ﮒﮔﺗ?    sample_cov = factor_data.cov()
    
    # ﻝ؟ﮔ ﻝ۸ﻠﭖﺅﺙﮒﻛﺛﻝ۸ﻠﭖﺅﺙ
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

### 4.3 ﻠ۲ﻠ۸ﮒﻟ۶۲ﻝ؟ﮔﺏ

```python
def decompose_portfolio_risk(
    portfolio_weights: pd.Series,
    factor_loadings: pd.DataFrame,
    factor_covariance: pd.DataFrame,
    idiosyncratic_risk: pd.Series
) -> RiskDecomposition:
    """
    ﻠ۲ﻠ۸ﮒﻟ۶۲
    
    ﻝ؟ﮔﺏ:
    1. ﻟ؟۰ﻝ؟ﻝﭨﮒﮒ ﮒ­ﮔﺑﻠﺎ: f_p = X'w
    2. ﻟ؟۰ﻝ؟ﮒ ﮒ­ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟: ﺵ_fﺡﺎ = f_p'ﺳ۲_f f_p
    3. ﻟ؟۰ﻝ؟ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟: ﺵ_ﺳﭖﺡﺎ = w'D_ﺳﭖ w
    4. ﮔﭨﻠ۲? ﺵ_p = sqrt(ﺵ_fﺡﺎ + ﺵ_ﺳﭖﺡﺎ)
    
    Args:
        portfolio_weights: ﻝﭨﮒﮔﻠ
        factor_loadings: ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ
        factor_covariance: ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?        idiosyncratic_risk: ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸
        
    Returns:
        RiskDecomposition: ﻠ۲ﻠ۸ﮒﻟ۶۲ﻝﭨﮔ
    """
    # 1. ﻟ؟۰ﻝ؟ﻝﭨﮒﮒ ﮒ­ﮔﺑﻠﺎ
    factor_exposure = factor_loadings.T @ portfolio_weights
    
    # 2. ﻟ؟۰ﻝ؟ﮒ ﮒ­ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟
    factor_risk_squared = factor_exposure.T @ factor_covariance @ factor_exposure
    
    # ﻟﺝﺗﻠﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟
    marginal_factor_risk = factor_covariance @ factor_exposure
    factor_risk_contribution = factor_exposure * marginal_factor_risk / np.sqrt(factor_risk_squared)
    
    # 3. ﻟ؟۰ﻝ؟ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟
    idiosyncratic_risk_squared = (portfolio_weights ** 2 * idiosyncratic_risk ** 2).sum()
    
    # 4. ﮔﭨﻠ۲?    total_risk = np.sqrt(factor_risk_squared + idiosyncratic_risk_squared)
    
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

## 5. ﮔﭖﻟﺁﮔﺗﮔ۰

### 5.1 ﮒﮒﮔﭖﻟﺁ

#### 5.1.1 ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮔﭖﻟﺁ

```python
import pytest
import numpy as np
import pandas as pd

class TestFactorExposureCalculator:
    """ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮒ۷ﮔﭖ?""
    
    def test_calculate_factor_exposure(self):
        """ﮔﭖﻟﺁﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟"""
        # ﮒﮒ۳ﮔﭖﻟﺁﮔﺍﮔ؟
        np.random.seed(42)
        factor_data = pd.DataFrame(
            np.random.randn(252, 10),
            columns=['factor_{}'.format(i) for i in range(10)]
        )
        returns_data = pd.DataFrame(
            np.random.randn(252, 50),
            columns=['asset_{}'.format(i) for i in range(50)]
        )
        
        # ﻟ؟۰ﻝ؟ﮒ ﮒ­ﮔﺑﻠﺎ
        calculator = FactorExposureCalculator(FactorConfig())
        factor_loadings = calculator.calculate(factor_data, returns_data)
        
        # ﻠ۹ﻟﺁﻝﭨﮔ
        assert factor_loadings.shape == (50, 10)
        assert not factor_loadings.isnull().any().any()
    
    def test_factor_exposure_accuracy(self):
        """ﮔﭖﻟﺁﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮒﻝ۰؟?""
        # ﻛﺛﺟﻝ۷ﮒﺓﺎﻝ۴ﮒ ﮒ­ﻝﮔﺍﮔ؟ﮔﭖ?        # ﮔ? r = 0.5*f1 + 0.3*f2 + noise
        np.random.seed(42)
        f1 = np.random.randn(252)
        f2 = np.random.randn(252)
        noise = np.random.randn(252) * 0.1
        
        returns = 0.5 * f1 + 0.3 * f2 + noise
        
        factor_data = pd.DataFrame({'f1': f1, 'f2': f2})
        returns_data = pd.DataFrame({'asset': returns})
        
        calculator = FactorExposureCalculator(FactorConfig())
        factor_loadings = calculator.calculate(factor_data, returns_data)
        
        # ﻠ۹ﻟﺁﮒ ﮒ­ﻟﺛﺛﻟﺓﮔ۴ﻟﺟﻝﮒ؟?        assert abs(factor_loadings.loc['asset', 'f1'] - 0.5) < 0.1
        assert abs(factor_loadings.loc['asset', 'f2'] - 0.3) < 0.1
```

#### 5.1.2 ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﮔﭖ?
```python
class TestFactorCovarianceEstimator:
    """ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍﻟ؟۰ﮒ۷ﮔﭖﻟﺁ"""
    
    def test_estimate_factor_covariance(self):
        """ﮔﭖﻟﺁﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍ?""
        # ﮒﮒ۳ﮔﭖﻟﺁﮔﺍﮔ؟
        np.random.seed(42)
        factor_data = pd.DataFrame(
            np.random.randn(252, 10),
            columns=['factor_{}'.format(i) for i in range(10)]
        )
        
        # ﻛﺙﺍﻟ؟۰ﮒ ﮒ­ﮒﮔﺗ?        estimator = FactorCovarianceEstimator(CovarianceConfig())
        factor_cov = estimator.estimate(factor_data)
        
        # ﻠ۹ﻟﺁﻝﭨﮔ
        assert factor_cov.shape == (10, 10)
        assert np.allclose(factor_cov.values, factor_cov.values.T)  # ﮒﺁﺗﻝ۶ﺍ
        assert np.all(np.linalg.eigvals(factor_cov.values) > 0)  # ﮔ­۲ﮒ؟
```

#### 5.1.3 ﻠ۲ﻠ۸ﮒﻟ۶۲ﮔﭖﻟﺁ

```python
class TestRiskDecomposition:
    """ﻠ۲ﻠ۸ﮒﻟ۶۲ﮔﭖﻟﺁ"""
    
    def test_decompose_risk(self):
        """ﮔﭖﻟﺁﻠ۲ﻠ۸ﮒﻟ۶۲"""
        # ﮒﮒ۳ﮔﭖﻟﺁﮔﺍﮔ؟
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
        
        # ﮒﮒﭨﭦBarraﮔ۷۰ﮒ
        barra_model = BarraRiskModel(BarraConfig())
        barra_model.factor_loadings = factor_loadings
        barra_model.factor_covariance = factor_covariance
        barra_model.idiosyncratic_risk = idiosyncratic_risk
        
        # ﻠ۲ﻠ۸ﮒﻟ۶۲
        decomposition = barra_model.decompose_risk(portfolio_weights)
        
        # ﻠ۹ﻟﺁﻝﭨﮔ
        assert decomposition.total_risk > 0
        assert abs(decomposition.factor_risk_ratio + 
                  decomposition.idiosyncratic_risk_ratio - 1.0) < 1e-6
```

### 5.2 ﻠﮔﮔﭖﻟﺁ

```python
class TestBarraRiskModelIntegration:
    """Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﻠﮔﮔﭖﻟﺁ"""
    
    def test_full_workflow(self):
        """ﮔﭖﻟﺁﮒ؟ﮔﺑﮒﺓ۴ﻛﺛ?""
        # ﮒﮒ۳ﮔﺍﮔ؟
        factor_data, returns_data = self._prepare_test_data()
        
        # ﮒﮒﭨﭦﮔ۷۰ﮒ
        config = BarraConfig()
        model = BarraRiskModel(config)
        
        # ﮔﮒﮔ۷۰ﮒ
        model.fit(factor_data, returns_data)
        
        # ﻟ؟۰ﻝ؟ﮒ ﮒ­ﮔﺑﻠﺎ
        portfolio_weights = pd.Series(
            np.random.dirichlet(np.ones(len(returns_data.columns))),
            index=returns_data.columns
        )
        factor_exposure = model.calculate_factor_exposure(portfolio_weights)
        
        # ﻠ۲ﻠ۸ﮒﻟ۶۲
        decomposition = model.decompose_risk(portfolio_weights)
        
        # ﻠ۹ﻟﺁ
        assert len(factor_exposure) == len(config.style_factors) + len(config.industry_factors)
        assert decomposition.total_risk > 0
    
    def _prepare_test_data(self):
        """ﮒﮒ۳ﮔﭖﻟﺁﮔﺍﮔ؟"""
        np.random.seed(42)
        
        # ﻝﮔﮒ ﮒ­ﮔﺍﮔ؟
        factor_data = pd.DataFrame(
            np.random.randn(252, 38),
            columns=['factor_{}'.format(i) for i in range(38)]
        )
        
        # ﻝﮔﻟﭖﻛﭦ۶ﮔﭘﻝ?        returns_data = pd.DataFrame(
            np.random.randn(252, 100),
            columns=['asset_{}'.format(i) for i in range(100)]
        )
        
        return factor_data, returns_data
```

### 5.3 ﮔ۶ﻟﺛﮔﭖﻟﺁ

```python
class TestBarraRiskModelPerformance:
    """Barraﻠ۲ﻠ۸ﮔ۷۰ﮒﮔ۶ﻟﺛﮔﭖﻟﺁ"""
    
    def test_factor_exposure_performance(self):
        """ﮔﭖﻟﺁﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ"""
        # ﮒ۳۶ﻟ۶ﮔ۷۰ﮔﺍ?        np.random.seed(42)
        factor_data = pd.DataFrame(
            np.random.randn(252, 38),
            columns=['factor_{}'.format(i) for i in range(38)]
        )
        returns_data = pd.DataFrame(
            np.random.randn(252, 1000),
            columns=['asset_{}'.format(i) for i in range(1000)]
        )
        
        # ﻟ؟۰ﮔﭘ
        import time
        start = time.time()
        
        calculator = FactorExposureCalculator(FactorConfig())
        factor_loadings = calculator.calculate(factor_data, returns_data)
        
        elapsed = time.time() - start
        
        # ﻠ۹ﻟﺁﮔ۶ﻟﺛ
        assert elapsed < 5.0  # 5ﻝ۶ﮒﮒ؟ﮔ
    
    def test_risk_decomposition_performance(self):
        """ﮔﭖﻟﺁﻠ۲ﻠ۸ﮒﻟ۶۲ﮔ۶ﻟﺛ"""
        # ﮒﮒ۳ﮔﺍﮔ؟
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
        
        # ﻟ؟۰ﮔﭘ
        import time
        start = time.time()
        
        decomposition = decompose_portfolio_risk(
            portfolio_weights, factor_loadings, factor_covariance, idiosyncratic_risk
        )
        
        elapsed = time.time() - start
        
        # ﻠ۹ﻟﺁﮔ۶ﻟﺛ
        assert elapsed < 0.1  # 100msﮒﮒ؟?```

---

## 6. ﮔ۶ﻟﺛﻟ۵ﮔﺎ

### 6.1 ﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ

| ﮔﻛﺛ | ﮔﺍﮔ؟ﻟ۶ﮔ۷۰ | ﮔ۶ﻟﺛﻟ۵ﮔﺎ | ﮔﭖﻟﺁﻝﭨﮔ |
|------|---------|---------|---------|
| **ﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟** | 1000ﻟﭖﻛﭦ۶ ﺣ 38ﮒ ﮒ­ | < 5?| ?ﻠﻟﺟ |
| **ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻛﺙﺍ?* | 38ﮒ ﮒ­ ﺣ 252?| < 1?| ?ﻠﻟﺟ |
| **ﻠ۲ﻠ۸ﮒﻟ۶۲** | 1000ﻟﭖﻛﭦ۶ | < 100ms | ?ﻠﻟﺟ |
| **ﻠ۲ﻠ۸ﮒﺛﮒ ** | 1000ﻟﭖﻛﭦ۶ | < 200ms | ?ﻠﻟﺟ |

### 6.2 ﮒﮒ­ﻛﺛﺟﻝ۷

| ﮔﻛﺛ | ﮒﮒ­ﮒ ﻝ۷ | ﻠﮒﭘ |
|------|---------|------|
| **ﮒ ﮒ­ﮔﺍﮔ؟ﮒ­ﮒ۷** | 38ﮒ ﮒ­ ﺣ 252?| < 10MB |
| **ﮒ ﮒ­ﻟﺛﺛﻟﺓﻝ۸ﻠﭖ** | 1000ﻟﭖﻛﭦ۶ ﺣ 38ﮒ ﮒ­ | < 5MB |
| **ﮒ ﮒ­ﮒﮔﺗﮒﺓ؟ﻝ۸?* | 38 ﺣ 38 | < 1MB |

---

## 7. ﻠ۷ﻝﺛﺎﮔﺗﮔ۰

### 7.1 ﻠ۷ﻝﺛﺎﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ??        ﮒﭦﻝ۷?                         ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?? ?  BarraRiskModel API             ? ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                  ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ??        ﮔﮒ۰?                         ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ?? ?ﮒ ﮒ­ﮔﺑﻠﺎ ? ?ﻠ۲ﻠ۸ﮒﻟ۶۲ ?          ?? ?ﻟ؟۰ﻝ؟ﮔﮒ۰ ? ?ﮔﮒ۰     ?          ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                  ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ??        ﮔﺍﮔ؟?                         ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ?? ?ﮒ ﮒ­ﮔﺍﮔ؟ ? ?ﮒﮔﺗ?  ?          ?? ??      ? ?ﮔﺍﮔ؟?  ?          ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?```

### 7.2 ﻠ۷ﻝﺛﺎﻠﻝﺛ؟

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

## 8. ﻝﮔ۶ﻛﺕﻝﭨﺑ?
### 8.1 ﻝﮔ۶ﮔﮔ 

| ﮔﮔ  | ﮔﻟﺟﺍ | ﻠ?| ﮒﻟ­۵ﻝﭦ۶ﮒ، |
|------|------|------|---------|
| **ﻟ؟۰ﻝ؟ﮒﭨﭘﻟﺟ** | ﮒﮔ؛۰ﻟ؟۰ﻝ؟ﻟﮔﭘ | > 200ms | P1 |
| **ﮒﮒ­ﻛﺛﺟﻝ۷** | ﮒﮒ­ﮒ ﻝ۷?| > 80% | P2 |
| **ﮒ ﮒ­ﮔﺑﻠﺎﮒﺙﮒﺕﺕ** | ﮒ ﮒ­ﮔﺑﻠﺎﻟﭘﻟﺟﻠ?| > 3ﺵ | P0 |
| **ﮒﮔﺗﮒﺓ؟ﻝ۸ﻠﭖﮒﺙ?* | ﮒﮔﺗﮒﺓ؟ﻝ۸ﻠﭖﮔ۰ﻛﭨﭘﮔﺍ | > 1000 | P1 |

### 8.2 ﮔ۴ﮒﺟﻟ؟ﺍﮒﺛ

```python
import logging

logger = logging.getLogger('barra_risk_model')

def log_factor_exposure_calculation(
    asset_count: int,
    factor_count: int,
    elapsed_time: float
):
    """ﻟ؟ﺍﮒﺛﮒ ﮒ­ﮔﺑﻠﺎﻟ؟۰ﻝ؟ﮔ۴ﮒﺟ"""
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
    """ﻟ؟ﺍﮒﺛﻠ۲ﻠ۸ﮒﻟ۶۲ﮔ۴ﮒﺟ"""
    logger.info({
        'event': 'risk_decomposition',
        'portfolio_id': portfolio_id,
        'total_risk': total_risk,
        'factor_risk_ratio': factor_risk_ratio,
        'timestamp': datetime.now().isoformat()
    })
```

### 8.3 ﻝﭨﺑﮔ۳ﻟ؟۰ﮒ

| ﻝﭨﺑﮔ۳ﻛﭨﭨﮒ۰ | ﻠ۱ﻝ | ﮔﻟﺟﺍ |
|---------|------|------|
| **ﮒ ﮒ­ﮔﺍﮔ؟ﮔﺑﮔﺍ** | ﮔﺁﮔ۴ | ﮔﺑﮔﺍﮒ ﮒ­ﮔﺍﮔ؟ |
| **ﮒﮔﺗﮒﺓ؟ﻝ۸ﻠﭖﻠ?* | ﮔﺁﮒ۷ | ﻠﮔﺍﻛﺙﺍﻟ؟۰ﮒ ﮒ­ﮒﮔﺗ?|
| **ﮔ۷۰ﮒﮒﮔﭖ** | ﮔﺁﮔ | ﮒﮔﭖﮔ۷۰ﮒﮔ۶ﻟﺛ |
| **ﮒﮔﺍﻟﺍﻛﺙ** | ﮔﺁﮒ­۲?| ﻟﺍﮔﺑﮔ۷۰ﮒﮒﮔﺍ |

---

## ﻠﮒﺛ

### A. APIﮔﮔ۰۲

#### A.1 REST API

```yaml
# ﻟ؟۰ﻝ؟ﮒ ﮒ­ﮔﺑﻠﺎ
POST /api/v1/barra/factor_exposure
Request:
  portfolio_weights: Dict[str, float]
Response:
  factor_exposure: Dict[str, float]

# ﻠ۲ﻠ۸ﮒﻟ۶۲
POST /api/v1/barra/risk_decomposition
Request:
  portfolio_weights: Dict[str, float]
Response:
  risk_decomposition: RiskDecomposition

# ﻠ۲ﻠ۸ﻠ۱ﻝ؟ﮒﻠ
POST /api/v1/barra/risk_budget
Request:
  total_risk: float
  factor_risk_budget: Dict[str, float]
Response:
  allocated_risk_budget: Dict[str, float]
```

### B. ﻛﺝﻟﭖ?
```txt
pandas>=1.5.0
numpy>=1.21.0
scikit-learn>=1.0.0
scipy>=1.7.0
cvxpy>=1.3.0
riskfolio-lib>=4.0.0
```

---

**ﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ﻝﮔ؛**: v1.0 | **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-03 | **ﻝ?*: Final | **ﻛﺕﻛﺕ?*: ﮒ؟ﮔﺛﮒﺙ?