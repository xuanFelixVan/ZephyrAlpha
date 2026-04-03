---
module_id: FACTOR_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管理
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 宏观数据源

> 中国及全球宏观数据整合

---

## 1. 宏观数据分类

| 类别 | 数据内容 | 更新频率 | 数据源 |
|------|---------|---------|--------|
| 中国经济 | GDP、PMI、CPI、PPI、失业率 | 月频 | 国家统计局 |
| 货币政策 | LPR、存款准备金率、公开市场操作 | 实时 | 央行 |
| 全球经济 | ISM、CPI、GDP | 月频 | macrotrends |
| 债市 | 国债收益率、信用利差 | 日频 |  Wind/iFind |
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

### 3.2 数据源URL

| 数据 | URL | 说明 |
|------|-----|------|
| 美联储指标 | https://fred.stlouisfed.org | 联邦基金利率、国债收益率 |
| CPI/PPI | https://stats.bls.gov | 美国CPI、PPI |
| GDP | https://bea.gov | 美国GDP |
| VIX | https://www.cboe.com/indices | VIX指数 |

---

## 4. 国债收益率曲线

```python
class BondYieldCurve:
    """国债收益率曲线"""

    def get_china_yield_curve(self) -> pd.DataFrame:
        """获取中国国债收益率曲线"""
        return ak.bond_china_yield()

    def get_us_yield_curve(self) -> pd.DataFrame:
        """获取美国国债收益率曲线"""
        return ak.bond_ust_10y()

    def calculate_spread(
        self,
        yield_curve: pd.DataFrame,
        tenor1: str = '2Y',
        tenor2: str = '10Y'
    ) -> float:
        """计算利差"""
        rate1 = yield_curve[tenor1].iloc[-1]
        rate2 = yield_curve[tenor2].iloc[-1]
        return rate2 - rate1
```

---

## 5. 大宗商品数据

```python
COMMODITIES_DATA = {
    'energy': {
        'wti_oil': {
            'name': 'WTI原油',
            'exchange': 'NYMEX',
            'symbol': 'CL',
            'unit': 'USD/桶'
        },
        'brent_oil': {
            'name': '布伦特原油',
            'exchange': 'ICE',
            'symbol': 'BZ',
            'unit': 'USD/桶'
        },
        'natural_gas': {
            'name': '天然气',
            'exchange': 'NYMEX',
            'symbol': 'NG',
            'unit': 'USD/MMBtu'
        }
    },
    'metals': {
        'gold': {
            'name': '黄金',
            'exchange': 'COMEX',
            'symbol': 'GC',
            'unit': 'USD/盎司'
        },
        'silver': {
            'name': '白银',
            'exchange': 'COMEX',
            'symbol': 'SI',
            'unit': 'USD/盎司'
        },
        'copper': {
            'name': '铜',
            'exchange': 'COMEX',
            'symbol': 'HG',
            'unit': 'USD/磅'
        }
    },
    'agriculture': {
        'corn': {
            'name': '玉米',
            'exchange': 'CBOT',
            'symbol': 'C',
            'unit': '美分/蒲式耳'
        },
        'wheat': {
            'name': '小麦',
            'exchange': 'CBOT',
            'symbol': 'W',
            'unit': '美分/蒲式耳'
        },
        'soybean': {
            'name': '大豆',
            'exchange': 'CBOT',
            'symbol': 'S',
            'unit': '美分/蒲式耳'
        }
    }
}
```

---

## 6. 宏观因子构建

```python
class MacroFactorBuilder:
    """宏观因子构建"""

    def build_money_flow_factor(self) -> pd.Series:
        """流动性因子"""
        # M2同比 - GDP同比
        m2 = self.get_m2_yoy()
        gdp = self.get_gdp_yoy()
        return m2 - gdp

    def build_rate_spread_factor(self) -> pd.Series:
        """利率差因子"""
        lpr = self.get_lpr()
        cpi = self.get_cpi_yoy()
        return lpr - cpi  # 实际利率

    def build_credit_cycle_factor(self) -> pd.Series:
        """信用周期因子"""
        # 社会融资规模存量增速 - 名义GDP增速
        credit = self.get_total_social_financing()
        gdp_nominal = self.get_nominal_gdp()
        return credit - gdp_nominal
```

---

## 7. 数据更新调度

```yaml
macro_data_schedule:
  daily:
    - time: "09:30"
      task: "更新前日宏观数据"
      data: ["国债收益率", "汇率"]
    - time: "17:00"
      task: "更新大宗商品数据"
      data: ["原油", "黄金", "铜"]
    - time: "20:00"
      task: "更新海外宏观数据"
      data: ["美债", "VIX", "美股"]

  monthly:
    - date: "每月第5个工作日"
      task: "更新CPI/PPI数据"
    - date: "每月第10个工作日"
      task: "更新PMI数据"
    - date: "每月第15个工作日"
      task: "更新GDP数据"

  realtime:
    - event: "央行政策发布"
      task: "立即更新LPR/RRR数据"
```

---

**版本**: 1.0 | **更新**: 2026-03-28
