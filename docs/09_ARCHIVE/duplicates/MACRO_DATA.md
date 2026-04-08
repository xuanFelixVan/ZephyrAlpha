---
module_id: 02_FACTOR_LIBRARY_04_DATA_SOURCE_001_ARCHIVED_8
```python
MACRO_INDICATORS_GLOBAL = {
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
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
---

> **非真源声明（duplicates）**：本文档位于 `docs/09_ARCHIVE/duplicates/`，仅用于追溯，不作为权威真源（canonical）。  
> **canonical_path**：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/ECONOMIC_REGIME_ENGINE_BLUEPRINT.md`  
> **处置建议**：merge_then_delete（宏观数据更贴近经济范式/宏观环境模块；后续如独立成“宏观数据源”文档再调整 canonical）。

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
