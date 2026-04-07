---

module_id: 02_FACTOR_LIBRARY_04_DATA_SOURCE_001


## 3. 全球宏观数据

### 3.1 核心指标

```python
MACRO_INDICATORS_GLOBAL = {
    # 美国
    'us_gdp_qoq': {
        'name': '美国GDP环比',
        'region': '美国',
        'source': 'BEA',
        'frequency': '季度'
    },
    'us_cpi_yoy': {
        'name': '美国CPI同比',
        'region': '美国',
        'source': 'BLS',
        'frequency': '月度'
    },
    'fed_funds_rate': {
        'name': '联邦基金利率',
        'region': '美国',
        'source': 'Fed',
        'frequency': '日频'
    },
    'us_10y_2y_spread': {
        'name': '美债10Y-2Y利差',
        'region': '美国',
        'source': 'FRED',
        'frequency': '日频'
    },
    'vix': {
        'name': 'VIX恐慌指数',
        'region': '美国',
        'source': 'CBOE',
        'frequency': '日频'
    },

    # 欧元区
    'eu_gdp_yoy': {
        'name': '欧元区GDP同比',
        'region': '欧盟',
        'source': 'Eurostat',
        'frequency': '季度'
    },
    'ecb_rate': {
        'name': '欧央行利率',
        'region': '欧盟',
        'source': 'ECB',
        'frequency': '不定期'
    },

    # 全球
    'wti_oil': {
        'name': 'WTI原油期货',
        'region': '全球',
        'source': 'NYMEX',
        'frequency': '日频'
    },
    'gold': {
        'name': '黄金期货',
        'region': '全球',
        'source': 'COMEX',
        'frequency': '日频'
    }
}
```

responsibility:
  - 管理因子库
---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
