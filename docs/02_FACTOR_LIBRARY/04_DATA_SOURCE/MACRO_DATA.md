---
module_id: DATA_MACRO_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-06
owner: 首席文档架构师
responsibility: 宏观经济数据获取与处理
standard_type: 数据源文档
applicable_scope: 宏观经济数据
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 进行中
---


# 宏观数据源

> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: 宏观经济数据源定义
- 整合中国及全球宏观经济数据
- 定义宏观数据指标体系
- 提供宏观数据获取接口

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 数据源适配器 | [DATA_SOURCE_ADAPTERS.md](./DATA_SOURCE_ADAPTERS.md) | 架构层 | 数据源适配器架构 |
| 数据源索引 | [INDEX.md](./INDEX.md) | 上级索引 | 数据源模块总索引 |

**职责边界**:
- ✅ 本文档负责: 定义宏观经济数据指标和获取方式
- ❌ 本文档不负责: 数据源适配器架构（由 DATA_SOURCE_ADAPTERS.md 负责）

> 中国及全球宏观数据整合

---

## 1. 宏观数据分类

| 类别 | 数据内容 | 更新频率 | 数据源 |
|------|---------|---------|--------|
| 中国经济 | GDP、PMI、CPI、PPI、失业率 | 月频 | 国家统计局 |
| 货币政策 | LPR、存款准备金率、公开市场操作 | 实时 | 央行 |
| 全球经济 | ISM、CPI、GDP | 月频 | macrotrends |
| 债市 | 国债收益率、信用利差 | 日频 | Wind/iFind |
| 大宗商品 | 原油、黄金、铜、农产品 | 日频 | 期货交易所 |

---

## 2. 中国宏观数据

### 2.1 核心指标

```python
MACRO_INDICATORS_CN = {
    # 增长类
    'gdp_yoy': {
        'name': 'GDP同比',
        'unit': '%',
        'source': '国家统计局',
        'frequency': '季度',
        'category': '增长'
    },
    'pmi_manufacturing': {
        'name': '制造业PMI',
        'unit': '指数',
        'source': '国家统计局',
        'frequency': '月度',
        'category': '增长'
    },
    'industrial_added_value': {
        'name': '工业增加值同比',
        'unit': '%',
        'source': '国家统计局',
        'frequency': '月度',
        'category': '增长'
    },

    # 通胀类
    'cpi_yoy': {
        'name': 'CPI同比',
        'unit': '%',
        'source': '国家统计局',
        'frequency': '月度',
        'category': '通胀'
    },
    'ppi_yoy': {
        'name': 'PPI同比',
        'unit': '%',
        'source': '国家统计局',
        'frequency': '月度',
        'category': '通胀'
    },

    # 货币类
    'lpr_1y': {
        'name': 'LPR 1年期',
        'unit': '%',
        'source': '央行',
        'frequency': '月度',
        'category': '货币'
    },
    'rrr': {
        'name': '存款准备金率',
        'unit': '%',
        'source': '央行',
        'frequency': '不定期',
        'category': '货币'
    },

    # 就业类
    'urban_unemployment_rate': {
        'name': '城镇调查失业率',
        'unit': '%',
        'source': '国家统计局',
        'frequency': '月度',
        'category': '就业'
    }
}
```

### 2.2 数据获取代码

```python
import akshare as ak
import pandas as pd

class MacroDataCN:
    """中国宏观数据获取"""

    def get_gdp(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取GDP数据"""
        return ak.macro_china_gdp()

    def get_pmi(self) -> pd.DataFrame:
        """获取PMI数据"""
        return ak.macro_china_pmi()

    def get_cpi(self) -> pd.DataFrame:
        """获取CPI数据"""
        return ak.macro_china_cpi()

    def get_lpr(self) -> pd.DataFrame:
        """获取LPR数据"""
        return ak.macro_china_lpr()

    def get_rrr(self) -> pd.DataFrame:
        """获取存款准备金率"""
        return ak.macro_china_rrr()
```

---

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

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
