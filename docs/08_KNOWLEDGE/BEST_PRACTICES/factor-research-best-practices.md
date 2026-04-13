---
module_id: FACTOR_RESEARCH_BEST_PRACTICES_4437
version: 1.0.0
status: Active
created_date: '2026-04-07'
last_updated: '2026-04-07'
owner: 首席文档架构师
responsibility: ''
layer: layer_08
standard_type: 'ﮔﻛﺛﺏﮒ؟ﻟﺓ?applicable_scope: ﮒ۷ﻝﺏﭨﻝﭨ?compliance_level: ﻛﺕﻛﺕﮔﮒ'
parent_document: ../KNOWLEDGE_TRANSFER_SYSTEM.md
implementation_status: 'ﮒﺓﺎﮒ؟ﮔ?owner: ﻠ۵ﮒﺕﮔﮔﺁﮒ؟'
tags: '["ﮔﻛﺛﺏﮒ؟ﻟﺓ?, "ﮒﮒﻝﻝ۸ﭘ", "ﻝﻝ۸ﭘﮔﭖﻝ۷"]'
---
## 1. ﮒﮒﻝﻝ۸ﭘﮔﭖﻝ۷ﮔﻛﺛﺏﮒ؟ﻟﺓ?



### 1.1 ﮔﮒﻝﻝ۸ﭘﮔﭖﻝ۷







```



ﮒﮒﮔﺏﮔﺏ



  ﻗ?ﻝﻟ؟ﭦﻠ۹ﻟﺁ



  ﻗ?ﮔﺍﮔ؟ﮒﮒ۳



ﻗ?ﮒﮒﻟ؟۰ﻝ؟



ﻗ?ﮒﮒﮔﭖﻟﺁ



ﻗ?ﮒﮒﻛﺙﮒ



  ﻗ?ﮒ؟ﻝﻠ۹ﻟﺁ



ﻗ?ﮔﻝﭨﻝﮔ۶



```







```
```---
```







### 1.2 ﮒﻠﭘﮔ؟ﭖﮔﻛﺛﺏﮒ؟ﻟﺓ?



#### ﻠﭘﮔ؟ﭖ1: ﮒﮒﮔﺏﮔﺏ







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻛﭨﻝﭨﮔﭖﮒ۵ﮒﻝﮒﭦﮒ



- ﻗ?ﮒﻟﮒ۵ﮔﺁﮔﻝ?- ﻗ?ﻟ۶ﮒﺁﮒﺕﮒﭦﮒﺙﻟﺎ۰



- ﻗ?ﻝﭨﮒﮔﻟﭖﻝﭨﻠ۹







**ﻠﺟﮒﻠﺓﻠﺎ**:



- ﻗ?ﻝﭦﺁﮔﺍﮔ؟ﮔﮔ?- ﻗ?ﻝﺙﭦﻛﺗﻝﻟ؟ﭦﮔﺁﮔ



- ﻗ?ﻟﺟﮒﭦ۵ﮔﮒﮒﮒﺎﮔﺍﮔ؟







```
```---
```







#### ﻠﭘﮔ؟ﭖ2: ﻝﻟ؟ﭦﻠ۹ﻟﺁ







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﮔﻝ۰؟ﮒﮒﻝﻝﭨﮔﭖﮒ۵ﮒ،ﻛﺗ



- ﻗ?ﻟ۶۲ﻠﮒﮒﻛﺕﭦﻛﭨﻛﺗﮔﮔ?- ﻗ?ﮒﮔﮒﮒﻝﻠﻝ۷ﮒﭦﮔﺁ



- ﻗ?ﻟﺁﻛﺙﺍﮒﮒﻝﮔﻝﭨﮔ?



**ﻝﻟ؟ﭦﻠ۹ﻟﺁﮔﺕﮒ**:



- [ ] ﮒﮒﮔﺁﮒ۵ﮒﺁﻛﭨ۴ﮔﻝﭨﺅﺙ?- [ ] ﮒﮒﻝﮒ؟ﺗﻠﮔﺁﮒ۵ﻟﭘﺏﮒ۳ﺅﺙ







```
```---
```







#### ﻠﭘﮔ؟ﭖ3: ﮔﺍﮔ؟ﮒﮒ۳







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻛﺛﺟﻝ۷ﻠ،ﻟﺑ۷ﻠﮔﺍﮔ؟ﮔﭦ



- ﻗ?ﻟﺟﻟ۰ﮔﺍﮔ؟ﮔﺕﮔﺑ



- ﻗ?ﮒ۳ﻝﻝﺙﭦﮒ۳ﺎﮒﺙﮒﮒﺙﮒﺕﺕﮒ?- ﻗ?ﮔ۲ﮔ۴ﮔﺍﮔ؟ﻛﺕﻟﺑﮔ?



**ﮔﺍﮔ؟ﻟﺑ۷ﻠﮔ۲ﮔ?*:



```python



def check_data_quality(data: pd.DataFrame) -> Dict[str, Any]:



    """



    ﮔﺍﮔ؟ﻟﺑ۷ﻠﮔ۲ﮔ?    



    Args:



        data: ﮒﺝﮔ۲ﮔ۴ﻝﮔﺍﮔ؟



    



    Returns:



        ﮔﺍﮔ؟ﻟﺑ۷ﻠﮔ۴ﮒ



    """



    report = {



        'total_records': len(data),



        'missing_values': data.isnull().sum().to_dict(),



        'duplicate_records': data.duplicated().sum(),



        'outliers': {},



        'statistics': data.describe().to_dict()



    }



    



    for column in data.select_dtypes(include=[np.number]).columns:



        q1 = data[column].quantile(0.25)



        q3 = data[column].quantile(0.75)



        iqr = q3 - q1



        outliers = ((data[column] < (q1 - 1.5 * iqr)) | 



                   (data[column] > (q3 + 1.5 * iqr))).sum()



        report['outliers'][column] = outliers



    



    return report



```







```
```---
```







#### ﻠﭘﮔ؟ﭖ4: ﮒﮒﻟ؟۰ﻝ؟







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻛﺛﺟﻝ۷ﮒﻠﮒﻟ؟۰ﻝ؟?- ﻗ?ﮒ۳ﻝﻟﺝﺗﻝﮔﮒﭖ



- ﻗ?ﮔﺓﭨﮒﮒﺟﻟ۵ﻝﮔﺏ۷ﻠ?- ﻗ?ﻝﺙﮒﮒﮒﮔﭖﻟﺁ







**ﻟ؟۰ﻝ؟ﮔﻝﻛﺙﮒ**:



```python



# ﻛﺙﮒﮒﺅﺙﮒﺝ۹ﻝﺁﻟ؟۰ﻝ؟



def calculate_factor_slow(data: pd.DataFrame) -> pd.Series:



    result = pd.Series(index=data.index)



    for i in range(len(data)):



        result.iloc[i] = data['close'].iloc[i-20:i].mean()



    return result







# ﻛﺙﮒﮒﺅﺙﮒﻠﮒﻟ؟۰ﻝ؟?def calculate_factor_fast(data: pd.DataFrame) -> pd.Series:



    return data['close'].rolling(20).mean()



```







```
```---
```







#### ﻠﭘﮔ؟ﭖ5: ﮒﮒﮔﭖﻟﺁ







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻛﺛﺟﻝ۷ﮒ۳ﻛﺕ۹ﮔﭖﻟﺁﮔﮔ



- ﻗ?ﻟﺟﻟ۰ﮔﺓﮔ؛ﮒ۳ﮔﭖﻟﺁ?- ﻗ?ﮔﭖﻟﺁﻛﺕﮒﮒﺕﮒﭦﻝﺁﮒ۱



- ﻗ?ﻟﺟﻟ۰ﻝ۷ﺏﮒ۴ﮔ۶ﮔ۲ﻠ۹?



**ﮔﭖﻟﺁﮔﮔ**:



| ﮔﮔ | ﻟ؟۰ﻝ؟ﮔﺗﮔﺏ | ﻝ؟ﮔﮒ?|



|------|---------|--------|



| **IC** | ﮒﮒﻛﺕﮔﭘﻝﻝﻝﺕﮒﺏﻝﺏﭨﮔﺍ | >0.05 |



| **IC_IR** | ICﮒﮒ?ICﮔﮒﮒﺓ?| >2.0 |



| **ﮒﻟﺍﮔ?* | ﮒﻝﭨﮔﭘﻝﮒﻟﺍﮔ?| >0.8 |



| **ﻟ۵ﻝﻝ?* | ﮔﮔﮔﺍﮔ؟ﮔﺁﻛﺝ | >95% |







```
```---
```







#### ﻠﭘﮔ؟ﭖ6: ﮒﮒﻛﺙﮒ







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﮒﮒﻝﭨﮒﻛﺙﮒ



- ﻗ?ﮒﮔﺍﮔﮔﮔ۶ﮒﮔ?



**ﻛﺙﮒﮔﺗﮔﺏ**:



```python



def optimize_factor(



    factor_values: pd.Series,



    returns: pd.Series,



    method: str = 'max_ic'



) -> Dict[str, float]:



    """



ﮒﮒﻛﺙﮒ



    



    Args:



factor_values: ﮒﮒﮒ?        returns: ﮔﭘﻝﻝ?        method: ﻛﺙﮒﮔﺗﮔﺏ



    



    Returns:



        ﻛﺙﮒﮒﮔﺍ



    """



    if method == 'max_ic':



        def objective(params):



            adjusted_factor = factor_values * params[0] + params[1]



            ic = adjusted_factor.corr(returns)



            return -ic



        



        result = minimize(objective, [1.0, 0.0])



        return {'scale': result.x[0], 'offset': result.x[1]}



    



    return {}



```







```
```---
```







#### ﻠﭘﮔ؟ﭖ7: ﮒ؟ﻝﻠ۹ﻟﺁ







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﮒﺍﻟ۶ﮔ۷۰ﮔﭖﻟﺁ?- ﻗ?ﻠﮔ۴ﮔ۸ﮒ۳۶ﻟ۶ﮔ۷۰



- ﻗ?ﮔﻝﭨﻝﮔ۶ﻟ۰۷ﻝﺍ



- ﻗ?ﮒﮔﭘﻟﺍﮔﺑﻝﻝ۴







**ﮒ؟ﻝﻠ۹ﻟﺁﮔﺕﮒ**:



- [ ] ﮔﺁﮒ۵ﻛﺕﮒﮔﭖﻝﭨﮔﻛﺕﻟﺑﺅﺙ



- [ ] ﻛﭦ۳ﮔﮔﮔ؛ﮔﺁﮒ۵ﮒﺁﮔ۴ﮒﺅﺙ



- [ ] ﮔﭖﮒ۷ﮔ۶ﮔﺁﮒ۵ﮒﻟﭘﺏﺅﺙ



- [ ] ﻠ۲ﻠ۸ﮔﺁﮒ۵ﮒﺁﮔ۶ﺅﺙ?



```
```---
```







#### ﻠﭘﮔ؟ﭖ8: ﮔﻝﭨﻝﮔ۶







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﮒ؟ﮔﻟﺁﻛﺙﺍﮒﮒﻟ۰۷ﻝﺍ



- ﻗ?ﻝﮔ۶ﮒﮒﻟ۰ﺍﮒ



- ﻗ?ﮒﮔﭘﻟﺍﮔﺑﮒﮒﮔﻠ



- ﻗ?ﻟ؟ﺍﮒﺛﮒﮒﻟ۰۷ﻝﺍ







**ﻝﮔ۶ﮔﮔ**:



```python



def monitor_factor_performance(



    factor_id: str,



    window: int = 20



) -> Dict[str, float]:



    """



ﻝﮔ۶ﮒﮒﻟ۰۷ﻝﺍ



    



    Args:



factor_id: ﮒﮒID



        window: ﻝﮔ۶ﻝ۹ﮒ۲



    



    Returns:



ﻟ۰۷ﻝﺍﮔﮔ



    """



    factor_values = load_factor(factor_id)



    returns = load_returns()



    



    ic_series = factor_values.rolling(window).apply(



        lambda x: x.corr(returns)



    )



    



    return {



        'ic_mean': ic_series.mean(),



        'ic_std': ic_series.std(),



        'ic_ir': ic_series.mean() / ic_series.std(),



        'ic_trend': np.polyfit(range(len(ic_series)), ic_series, 1)[0]



    }



```







```
```---
```







## 2. ﮒﮒﻝﭨﮒﮔﻛﺛﺏﮒ؟ﻟﺓ?



### 2.1 ﮒﮒﻠﮔ۸







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻠﮔ۸ﻛﺛﻝﺕﮒﺏﮔ۶ﻝﮒﮒ



- ﻗ?ﮒﮒﮔﺍﻠﻠﻛﺕﺅﺙ?-10ﻛﺕ۹ﺅﺙ



- ﻗ?ﮒﮒﻝﺎﭨﮒﮒ۳ﮔﺓﮒ?- ﻗ?ﮒﮒﻠﭨﻟﺝﻛﭦﻟ۰۴







**ﮒﮒﻝﺕﮒﺏﮔ۶ﮔ۲ﮔ?*:



```python



def check_factor_correlation(



    factor_values: pd.DataFrame,



    threshold: float = 0.7



) -> pd.DataFrame:



    """



ﮔ۲ﮔ۴ﮒﮒﻝﺕﮒﺏﮔ?



    Args:



factor_values: ﮒﮒﮒﺙﻝ۸ﻠ?        threshold: ﻝﺕﮒﺏﮔ۶ﻠﮒ?



    Returns:



ﻠ،ﻝﺕﮒﺏﮔ۶ﮒﮒﮒﺁﺗ



    """



    corr_matrix = factor_values.corr()



    



    high_corr_pairs = []



    for i in range(len(corr_matrix.columns)):



        for j in range(i+1, len(corr_matrix.columns)):



            if abs(corr_matrix.iloc[i, j]) > threshold:



                high_corr_pairs.append({



                    'factor1': corr_matrix.columns[i],



                    'factor2': corr_matrix.columns[j],



                    'correlation': corr_matrix.iloc[i, j]



                })



    



    return pd.DataFrame(high_corr_pairs)



```







```
```---
```







### 2.2 ﮒﮒﮔﻠ







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻛﺛﺟﻝ۷ﻠ۲ﻠ۸ﮒﺗﺏﻛﭨﺓﮔﺗﮔﺏ



- ﻗ?ﮒ؟ﮔﻟﺍﮔﺑﮔﻠ



- ﻗ?ﻟﻟﮒﮒﻟ۰ﺍﮒ



- ﻗ?ﮔ۶ﮒﭘﮒﮒﮒﮔﻠ?



**ﮔﻠﮒﻠﮔﺗﮔﺏ**:



| ﮔﺗﮔﺏ | ﻛﺙﻝﺗ | ﻝﺙﭦﻝﺗ | ﻠﻝ۷ﮒﭦﮔﺁ |



|------|------|------|---------|



| **ﻝﮔﻠ?* | ﻝ؟ﮒ?| ﮒﺟﺛﻝ۴ﮒﮒﮒﺓ؟ﮒﺙ | ﮒﮔ۴ﮔﭖﻟﺁ |



| **ICﮒﮔ** | ﻟﻟﮒﮒﮔﮔ | ﮒﺁﻟﺛﻟﺟﮔﮒ?| ﮒﮒﮔﮔﻝ۷ﺏﮒ؟ |



| **ﻠ۲ﻠ۸ﮒﺗﺏﻛﭨﺓ** | ﻠ۲ﻠ۸ﮒﻟ۰۰ | ﻟ؟۰ﻝ؟ﮒ۳ﮔ | ﮔ۲ﮒﺙﻛﺛﺟﻝ۷ |



| **ﻛﺙﮒﮔﺗﮔﺏ** | ﮔﮔﮔﻛﺙ?| ﮒﺁﻟﺛﻟﺟﮔﮒ?| ﻠﻟ۵ﻠ۹ﻟﺁ?|







```
```---
```







### 2.3 ﮒﮒﻟﺍﻛﭨ







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻠﮔ۸ﮒﻠﻝﻟﺍﻛﭨﻠ۱ﻝ



- ﻗ?ﮔ۶ﮒﭘﮔ۱ﮔﻝ?- ﻗ?ﻟﻟﻛﭦ۳ﮔﮔﮔ؛



- ﻗ?ﻠﺟﮒﻠ۱ﻝﺗﻟﺍﻛﭨ







**ﻟﺍﻛﭨﻠ۱ﻝﻠﮔ۸**:



| ﻠ۱ﻝ | ﻛﺙﻝﺗ | ﻝﺙﭦﻝﺗ | ﻠﻝ۷ﮒﮒ |



|------|------|------|---------|



| **ﮔ۴ﮒﭦ۵** | ﮒﮔﭘﮔ۶ﮒﺙﭦ | ﮔﮔ؛ﻠ،?| ﻠ،ﻠ۱ﮒﮒ |



| **ﮒ۷ﮒﭦ۵** | ﮒﺗﺏﻟ۰۰ﮔ۶ﮒ۴ﺛ | ﮒﺁﻟﺛﮔﭨﮒ | ﻝﮔﮒﮒ |



| **ﮔﮒﭦ۵** | ﮔﮔ؛ﻛﺛ?| ﮔﭨﮒﮔﮔﺝ | ﻛﺕﻠﺟﮔﮒﮒ?|



| **ﮒ۲ﮒﭦ۵** | ﮔﮔ؛ﮔﻛﺛ?| ﮔﭨﮒﻛﺕ۴ﻠ | ﻠﺟﮔﮒﮒ |







```
```---
```







## 3. ﻠ۲ﻠ۸ﻝ؟۰ﻝﮔﻛﺛﺏﮒ؟ﻟﺓ?



### 3.1 ﮒﮒﻠ۲ﻠ۸ﮔ۶ﮒﭘ







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻟ؟ﺝﻝﺛ؟ﮒﮒﮔﺑﻠﺎﻠﻠ۱







**ﻠ۲ﻠ۸ﻠﻠ۱ﻟ؟ﺝﻝﺛ؟**:



```python



def set_factor_limits(



    factor_id: str,



    risk_tolerance: float = 0.05



) -> Dict[str, float]:



    """



ﻟ؟ﺝﻝﺛ؟ﮒﮒﻠ۲ﻠ۸ﻠﻠ۱



    



    Args:



factor_id: ﮒﮒID



        risk_tolerance: ﻠ۲ﻠ۸ﮒ؟ﺗﮒﺟﮒﭦ?    



    Returns:



        ﻠ۲ﻠ۸ﻠﻠ۱



    """



    factor_values = load_factor(factor_id)



    factor_std = factor_values.std()



    



    return {



        'max_exposure': factor_std * 2,



        'min_exposure': -factor_std * 2,



        'max_turnover': 0.3,



        'max_correlation': 0.7



    }



```







```
```---
```







### 3.2 ﻝﭨﮒﻠ۲ﻠ۸ﮔ۶ﮒﭘ







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻟ؟ﺝﻝﺛ؟ﻝﭨﮒﻠ۲ﻠ۸ﻠﻠ۱



- ﻗ?ﻝﮔ۶ﻝﭨﮒﻠ۲ﻠ۸ﮒﮒﮔﺑﻠﺎ



- ﻗ?ﮔ۶ﮒﭘﻝﭨﮒﮔ۱ﮔﻝ?- ﻗ?ﮒﮔ۲ﮔﻟﭖ







**ﻝﭨﮒﻠ۲ﻠ۸ﻝﮔ۶**:



```python



def monitor_portfolio_risk(



    portfolio: pd.Series,



    risk_factors: pd.DataFrame



) -> Dict[str, float]:



    """



    ﻝﮔ۶ﻝﭨﮒﻠ۲ﻠ۸



    



    Args:



        portfolio: ﻝﭨﮒﮔﻠ



risk_factors: ﻠ۲ﻠ۸ﮒﮒﻝ۸ﻠﭖ



    



    Returns:



ﻠ۲ﻠ۸ﮔﮔ



    """



    factor_exposures = {}



    for factor in risk_factors.columns:



        exposure = (portfolio * risk_factors[factor]).sum()



        factor_exposures[f'exposure_{factor}'] = exposure



    



    portfolio_var = np.dot(portfolio.T, np.dot(risk_factors.cov(), portfolio))



    factor_exposures['portfolio_vol'] = np.sqrt(portfolio_var)



    



    return factor_exposures



```







```
```---
```







## 4. ﮔﮔ۰۲ﻟ؟ﺍﮒﺛﮔﻛﺛﺏﮒ؟ﻟﺓ?



### 4.1 ﮒﮒﮔﮔ۰۲







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻟ؟ﺍﮒﺛﮒﮒﮒ؟ﻛﺗﮒﻠﭨﻟﺝ



- ﻗ?ﻟ؟ﺍﮒﺛﻟ؟۰ﻝ؟ﮒ؛ﮒﺙ



- ﻗ?ﻟ؟ﺍﮒﺛﮒﮔﭖﻝﭨﮔ



- ﻗ?ﻟ؟ﺍﮒﺛﻛﺛﺟﻝ۷ﮔﮒ







**ﮒﮒﮔﮔ۰۲ﮔ۷۰ﮔﺟ**:



```markdown



# ﮒﮒﮒﻝ۶ﺍ







## 1. ﮒﮒﮒ؟ﻛﺗ



- ﮒﮒID



- ﮒﮒﮔﻟﺟﺍ



- ﻝﭨﮔﭖﮒ۵ﮒ،ﻛﺗ?



## 2. ﻟ؟۰ﻝ؟ﮒ؛ﮒﺙ



- ﻟﺁ۵ﻝﭨﮒ؛ﮒﺙ



- ﮒﮔﺍﻟﺁﺑﮔ



- ﻛﭨ۲ﻝﮒ؟ﻝﺍ







## 3. ﮒﮔﭖﻟ۰۷ﻝﺍ



- ICﮔﮔ



- ﮒﻝﭨﮔﭘﻝ



- ﻝ۷ﺏﮒ۴ﮔ۶ﮔ۲ﻠ۹?



## 4. ﮒﭦﻝ۷ﮔﮒ



- ﻠﻝ۷ﮒﭦﮔﺁ



- ﮔﺏ۷ﮔﻛﭦﻠ۰ﺗ



- ﻝﭨﮒﮒﭨﭦﻟ؟؟



```







```
```---
```







### 4.2 ﻝﻝ۸ﭘﻟ؟ﺍﮒﺛ







**ﮔﻛﺛﺏﮒ؟ﻟﺓ?*:



- ﻗ?ﻟ؟ﺍﮒﺛﻝﻝ۸ﭘﻟﺟﻝ۷



- ﻗ?ﻟ؟ﺍﮒﺛﮒﺏﻠ؟ﮒﺏﻝ



- ﻗ?ﻟ؟ﺍﮒﺛﻠ؟ﻠ۱ﮒﻟ۶۲ﮒﺏﮔﺗﮔﺏ?- ﻗ?ﻟ؟ﺍﮒﺛﻝﭨﻠ۹ﮔﻟ؟







**ﻝﻝ۸ﭘﻟ؟ﺍﮒﺛﮔ۷۰ﮔﺟ**:



```markdown



# ﻝﻝ۸ﭘﻟ؟ﺍﮒﺛ







## 1. ﻝﻝ۸ﭘﻝ؟ﮔ



- ﻝﻝ۸ﭘﻠ؟ﻠ۱



- ﻠ۱ﮔﻝﭨﮔ







## 2. ﻝﻝ۸ﭘﻟﺟﻝ۷



- ﮔﺍﮔ؟ﮒﮒ۳



- ﮔﺗﮔﺏﻠﮔ۸



- ﮒ؟ﻠ۹ﻟ؟ﺝﻟ؟۰







## 3. ﻝﻝ۸ﭘﻝﭨﮔ



- ﻛﺕﭨﻟ۵ﮒﻝﺍ



- ﮔﺍﮔ؟ﮔﺁﮔ



- ﻝﭨﻟ؟ﭦﮒﮔ







## 4. ﻝﭨﻠ۹ﮔﻟ؟



- ﮔﮒﻝﭨﻠ۹



- ﮒ۳ﺎﻟﺑ۴ﮔﻟ؟



- ﮔﺗﻟﺟﮒﭨﭦﻟ؟؟



```







```
```---
```







## 5. ﮒﻟﮔﮔ۰?



- ﻝﻝ۸ﭘﮔﺗﮔﺏﻟ؟ﭦ



- ﮒ۷ﻠﮒﮒﮒﭦ



- ﮒ۳ﮒﮒﻝﻝ۴ﮒﭦ







```
```---
```







**ﮔﮔ۰۲ﻝﭘﮔ?*: ﮔ۲ﮒﺙﮔﮒ



**ﻛﺕﮔ؛۰ﮔﺑﮔﺍ**: 2026-07-03



