---
module_id: STANDARDS_TAXONOMY_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# 因子分类�?(Factor Taxonomy)

> 因子分类体系与参数配置标�?
>
> **职责**: 定义因子分类体系和参数配�?
> **注册�?*: [../06_REGISTRY/FACTOR_CATALOG.md](../06_REGISTRY/FACTOR_CATALOG.md) - 因子清单和元数据
> **计算框架**: [FACTOR_CALCULATION_FRAMEWORK.md](FACTOR_CALCULATION_FRAMEWORK.md) - 计算引擎和调度器

---

## 1. 因子分类体系

```python
FACTOR_TAXONOMY = {
    '技术指�?: {
        '趋势�?: {
            'indicators': ['MA', 'EMA', 'SMA', 'DEMA', 'TEMA'],
            'sub_indicators': ['MACD', 'ADX', 'SAR', 'AROON']
        },
        '动量�?: {
            'indicators': ['RSI', 'KDJ', 'WR', 'CCI', 'ROC'],
            'sub_indicators': ['MOM', 'CMF']
        },
        '波动�?: {
            'indicators': ['ATR', 'STDDEV', 'BBANDS_WIDTH'],
            'sub_indicators': ['NATR']
        },
        '成交量类': {
            'indicators': ['OBV', 'MFI', 'VR', 'AD'],
            'sub_indicators': ['VWAP', 'EMV']
        }
    },
    '基本�?: {
        '估值类': {
            'indicators': ['PE', 'PB', 'PS', 'PCF', 'DY'],
            'sub_indicators': ['SP', 'EV_EBITDA']
        },
        '成长�?: {
            'indicators': ['REVENUE_GROWTH', 'PROFIT_GROWTH', 'ROE_GROWTH'],
            'sub_indicators': ['OPERATING_INCOME_GROWTH', 'GROSS_MARGIN_GROWTH']
        },
        '质量�?: {
            'indicators': ['ROE', 'ROA', 'ROIC', 'GROSS_MARGIN'],
            'sub_indicators': ['NET_MARGIN', 'EBIT_MARGIN']
        },
        '规模�?: {
            'indicators': ['TOTAL_MARKET_CAP', 'FREE_MARKET_CAP'],
            'sub_indicators': ['LOG_MARKET_CAP']
        },
        '杠杆�?: {
            'indicators': ['DEBT_RATIO', 'CURRENT_RATIO', 'QUICK_RATIO'],
            'sub_indicators': ['NET_DEBT_TO_EBITDA']
        }
    },
    '资金流向': {
        '主力资金': {
            'indicators': ['MAIN_NET_BUY', 'HUGE_NET_BUY', 'LARGE_NET_BUY'],
            'sub_indicators': ['MAIN_CAPITAL_FLOW']
        },
        '北向资金': {
            'indicators': ['NORTH_NET_BUY', 'NORTH_HOLD_RATIO'],
            'sub_indicators': ['NORTH_HOLD_CHANGE']
        },
        '融资融券': {
            'indicators': ['MARGIN_BALANCE', 'SHORT_BALANCE', 'MARGIN_NET_BUY'],
            'sub_indicators': ['SHORT_NET_BUY', 'MARGIN_TURNOVER']
        }
    },
    '另类数据': {
        '新闻舆情': {
            'indicators': ['SENTIMENT_SCORE', 'KEYWORD_HOTNESS'],
            'sub_indicators': ['NEWS_COUNT', 'BULLISH_RATIO']
        },
        '网络搜索': {
            'indicators': ['SEARCH_INDEX', 'SEARCH_CHANGE'],
            'sub_indicators': ['SEARCH_ACCELERATION']
        },
        '社交媒体': {
            'indicators': ['DISCUSSION_HEAT', 'SOCIAL_SENTIMENT'],
            'sub_indicators': ['INFLUENCER_SCORE']
        }
    },
    '市场结构': {
        '动量�?: {
            'indicators': ['PRICE_MOMENTUM', 'SECTOR_MOMENTUM'],
            'sub_indicators': ['RELATIVE_STRENGTH']
        },
        '趋势�?: {
            'indicators': ['TREND_STRENGTH', 'TREND_DIRECTION'],
            'sub_indicators': ['TREND_PERSISTENCE']
        },
        '反转�?: {
            'indicators': ['MEAN_REVERSION', 'SHORT_TERM_REVERSAL'],
            'sub_indicators': ['LONG_TERM_REVERSAL']
        }
    }
}
```

---

## 2. 因子参数配置

```python
FACTOR_PARAMETERS = {
    'MA': {
        'description': '移动平均�?,
        'category': '技术指�?趋势�?,
        'parameters': {
            'periods': {
                'type': 'list[int]',
                'default': [5, 10, 20, 30, 60],
                'description': '计算周期列表'
            },
            'ma_type': {
                'type': 'enum',
                'default': 'SMA',
                'options': ['SMA', 'EMA', 'WMA', 'DEMA', 'TEMA'],
                'description': '均线类型'
            }
        },
        'output_columns': ['MA{period}', 'MA{period}_{ma_type}'],
        'dependencies': []
    },

    'RSI': {
        'description': '相对强弱指数',
        'category': '技术指�?动量�?,
        'parameters': {
            'periods': {
                'type': 'list[int]',
                'default': [6, 12, 24],
                'description': 'RSI计算周期'
            }
        },
        'output_columns': ['RSI{period}'],
        'dependencies': ['PRICE_CHANGE']
    },

    'MACD': {
        'description': '指数平滑异同移动平均�?,
        'category': '技术指�?趋势�?,
        'parameters': {
            'fast_period': {
                'type': 'int',
                'default': 12,
                'range': [5, 30]
            },
            'slow_period': {
                'type': 'int',
                'default': 26,
                'range': [10, 50]
            },
            'signal_period': {
                'type': 'int',
                'default': 9,
                'range': [5, 20]
            }
        },
        'output_columns': ['DIF', 'DEA', 'MACD'],
        'dependencies': ['EMA']
    },

    'BBANDS': {
        'description': '布林�?,
        'category': '技术指�?波动�?,
        'parameters': {
            'period': {
                'type': 'int',
                'default': 20,
                'range': [5, 50]
            },
            'std_dev': {
                'type': 'float',
                'default': 2.0,
                'range': [1.0, 4.0]
            }
        },
        'output_columns': ['BBAND_UPPER', 'BBAND_MIDDLE', 'BBAND_LOWER', 'BBAND_WIDTH', 'BBAND_PCTB'],
        'dependencies': ['MA', 'STDDEV']
    },

    'PE': {
        'description': '市盈�?,
        'category': '基本�?估值类',
        'parameters': {
            'type': {
                'type': 'enum',
                'default': 'TTM',
                'options': ['TTM', 'LYR', 'FWD'],
                'description': 'PE类型'
            }
        },
        'output_columns': ['PE_{type}'],
        'dependencies': []
    },

    'ROE': {
        'description': '净资产收益�?,
        'category': '基本�?质量�?,
        'parameters': {
            'period': {
                'type': 'enum',
                'default': 'TTM',
                'options': ['TTM', 'YTD', 'ANNUAL'],
                'description': '计算周期'
            }
        },
        'output_columns': ['ROE_{period}'],
        'dependencies': ['NET_INCOME', 'EQUITY']
    }
}
```

---

## 3. 因子依赖关系�?

```python
FACTOR_DEPENDENCY_GRAPH = {
    'MACD': {
        'dependencies': ['EMA'],
        'description': '依赖快线和慢线EMA计算'
    },
    'BBANDS': {
        'dependencies': ['MA', 'STDDEV'],
        'description': '依赖中轨MA和标准差计算'
    },
    'RSI': {
        'dependencies': ['PRICE_CHANGE'],
        'description': '依赖价格变动计算涨跌'
    },
    'CCI': {
        'dependencies': ['SMA', 'MAD'],
        'description': '依赖典型价的均值和平均偏差'
    },
    'MFI': {
        'dependencies': ['TP', 'MONEY_FLOW'],
        'description': '依赖典型价和资金流量'
    },
    'KDJ': {
        'dependencies': ['RSV'],
        'description': '依赖原始随机�?
    },
    'WR': {
        'dependencies': ['HHV', 'LLV'],
        'description': '依赖N日最高价和最低价'
    },
    'OBV': {
        'dependencies': ['PRICE_CHANGE'],
        'description': '依赖价格变动方向'
    },

    # 复合因子
    'COMPOSITE_MOMENTUM': {
        'dependencies': ['RSI', 'MACD', 'ROC'],
        'description': '多动量因子组�?
    },
    'VALUE_QUALITY': {
        'dependencies': ['PE', 'PB', 'ROE', 'GROSS_MARGIN'],
        'description': '价值质量因子组�?
    },
    'CAPITAL_FLOW': {
        'dependencies': ['MAIN_NET_BUY', 'NORTH_NET_BUY', 'MARGIN_NET_BUY'],
        'description': '资金流向因子组合'
    }
}
```

### 3.1 依赖解析算法

```python
def resolve_dependency_chain(target_factor: str) -> list:
    """解析因子的完整依赖链（按计算顺序�?

    使用拓扑排序确保按正确顺序计�?

    返回:
        依赖链列表，从最底层依赖到目标因�?
    """
    visited = set()
    chain = []

    def _resolve(factor: str):
        if factor in visited:
            return
        visited.add(factor)

        dependencies = FACTOR_DEPENDENCY_GRAPH.get(factor, {}).get('dependencies', [])
        for dep in dependencies:
            _resolve(dep)

        chain.append(factor)

    _resolve(target_factor)
    return chain
```

---

## 4. 因子元数据表结构

```sql
-- 因子定义�?
CREATE TABLE factor_definitions (
    factor_id VARCHAR(50) PRIMARY KEY,
    factor_name VARCHAR(100),
    factor_type ENUM('technical', 'fundamental', 'flow', 'alternative', 'macro'),
    category_path VARCHAR(100),  -- e.g., '技术指�?趋势�?
    description TEXT,
    formula_expression TEXT,     -- 数学表达�?
    parameters JSON,             -- 参数配置
    dependencies JSON,           -- 依赖列表
    created_time DATETIME,
    updated_time DATETIME,
    version INT DEFAULT 1,
    status ENUM('active', 'deprecated', 'testing', 'failed') DEFAULT 'testing',
    created_by VARCHAR(50),
    tags JSON                   -- 自定义标�?
);

-- 因子参数�?
CREATE TABLE factor_parameters (
    param_id VARCHAR(50) PRIMARY KEY,
    factor_id VARCHAR(50),
    param_name VARCHAR(50),
    param_type ENUM('int', 'float', 'list', 'string', 'enum'),
    default_value JSON,
    value_range JSON,
    description TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (factor_id) REFERENCES factor_definitions(factor_id)
);

-- 因子计算结果�?
CREATE TABLE factor_values (
    stock_code VARCHAR(20),
    trade_date DATE,
    factor_id VARCHAR(50),
    factor_value DECIMAL(20,6),
    data_source VARCHAR(50),
    calculated_time DATETIME,
    version INT DEFAULT 1,
    quality_score DECIMAL(5,2),  -- 数据质量评分
    PRIMARY KEY (stock_code, trade_date, factor_id),
    INDEX idx_factor_date (factor_id, trade_date),
    INDEX idx_date (trade_date)
);

-- 因子绩效�?
CREATE TABLE factor_performance (
    factor_id VARCHAR(50),
    calc_date DATE,
    ic DECIMAL(10,6),
    icir DECIMAL(10,6),
    returns DECIMAL(10,6),
    turnover DECIMAL(10,6),
    sample_count INT,
    created_time DATETIME,
    PRIMARY KEY (factor_id, calc_date),
    FOREIGN KEY (factor_id) REFERENCES factor_definitions(factor_id)
);

-- 因子版本历史
CREATE TABLE factor_version_history (
    version_id INT PRIMARY KEY AUTO_INCREMENT,
    factor_id VARCHAR(50),
    version INT,
    change_log TEXT,
    changed_by VARCHAR(50),
    changed_time DATETIME,
    FOREIGN KEY (factor_id) REFERENCES factor_definitions(factor_id)
);
```

---

## 5. 因子质量检�?

```python
class FactorQualityChecker:
    """因子质量检查器"""

    def check_factor_quality(
        self,
        factor_values: pd.DataFrame,
        factor_id: str
    ) -> dict:
        """执行完整质量检�?

        返回:
            质量报告
        """
        checks = {
            'missing_rate': self._check_missing(factor_values),
            'outlier_rate': self._check_outliers(factor_values),
            'distribution': self._check_distribution(factor_values),
            'stability': self._check_stability(factor_values),
            'correlation': self._check_correlation(factor_values)
        }

        overall_score = self._calculate_quality_score(checks)

        return {
            'factor_id': factor_id,
            'checks': checks,
            'overall_score': overall_score,
            'passed': overall_score >= 0.7,
            'recommendations': self._generate_recommendations(checks)
        }

    def _check_missing(self, df: pd.DataFrame) -> dict:
        """检查缺失率"""
        missing_rate = df.isnull().mean()
        return {
            'missing_rate': missing_rate.mean(),
            'max_missing': missing_rate.max(),
            'passed': missing_rate.mean() < 0.1
        }

    def _check_outliers(self, df: pd.DataFrame, n_std: float = 5.0) -> dict:
        """检查异常�?""
        z_scores = np.abs((df - df.mean()) / df.std())
        outlier_rate = (z_scores > n_std).mean()
        return {
            'outlier_rate': outlier_rate,
            'passed': outlier_rate < 0.05
        }

    def _calculate_quality_score(self, checks: dict) -> float:
        """计算综合质量分数"""
        weights = {
            'missing_rate': 0.3,
            'outlier_rate': 0.2,
            'distribution': 0.2,
            'stability': 0.2,
            'correlation': 0.1
        }

        score = 0.0
        for check_name, weight in weights.items():
            check_result = checks.get(check_name, {})
            passed = check_result.get('passed', True)
            score += weight if passed else 0.0

        return score
```

---

## 6. 因子流水�?

```python
class FactorPipeline:
    """因子计算流水�?""

    def __init__(self, factor_ids: list):
        self.factor_ids = factor_ids
        self.dependency_resolver = DependencyResolver()
        self.quality_checker = FactorQualityChecker()
        self.results = {}

    def execute(
        self,
        start_date: str,
        end_date: str,
        stock_list: list = None
    ) -> dict:
        """执行因子计算流水�?""

        # 阶段1: 解析依赖�?
        all_factors = self._resolve_all_dependencies(self.factor_ids)

        # 阶段2: 获取基础数据
        raw_data = self._fetch_raw_data(all_factors, start_date, end_date, stock_list)

        # 阶段3: 按依赖顺序计�?
        for factor_id in all_factors:
            config = FACTOR_PARAMETERS.get(factor_id, {})
            self.results[factor_id] = self._calculate_factor(
                factor_id, config, raw_data
            )

        # 阶段4: 质量检�?
        quality_reports = {}
        for factor_id, values in self.results.items():
            quality_reports[factor_id] = self.quality_checker.check_factor_quality(
                values, factor_id
            )

        # 阶段5: 存储结果
        self._store_results(self.results, quality_reports)

        return {
            'results': self.results,
            'quality_reports': quality_reports
        }

    def _resolve_all_dependencies(self, factor_ids: list) -> list:
        """解析所有因子的依赖�?""
        all_factors = []
        for fid in factor_ids:
            chain = self.dependency_resolver.resolve_dependency_chain(fid)
            for f in chain:
                if f not in all_factors:
                    all_factors.append(f)
        return all_factors
```

---

## 7. 因子监控与预�?

```python
FACTOR_ALERT_RULES = {
    'icir_threshold': {
        'warning': 0.5,
        'critical': 0.3,
        'check_period': 'weekly'
    },
    'decay_rate': {
        'warning': 0.3,  # 5日IC衰减超过30%
        'critical': 0.5,
        'window': 5
    },
    'turnover': {
        'warning': 0.5,  # 日换手率超过50%
        'critical': 0.8
    },
    'missing_rate': {
        'warning': 0.05,
        'critical': 0.1
    }
}

class FactorMonitor:
    """因子有效性监�?""

    def check_alerts(self, factor_id: str, recent_icir: float,
                     recent_turnover: float) -> list:
        """检查是否触发告�?""
        alerts = []

        if recent_icir < FACTOR_ALERT_RULES['icir_threshold']['critical']:
            alerts.append({
                'type': 'icir_critical',
                'factor_id': factor_id,
                'icir': recent_icir,
                'message': f'因子{factor_id}的ICIR持续低迷，建议暂停使�?
            })
        elif recent_icir < FACTOR_ALERT_RULES['icir_threshold']['warning']:
            alerts.append({
                'type': 'icir_warning',
                'factor_id': factor_id,
                'icir': recent_icir,
                'message': f'因子{factor_id}的ICIR下降，需关注'
            })

        if recent_turnover > FACTOR_ALERT_RULES['turnover']['critical']:
            alerts.append({
                'type': 'turnover_critical',
                'factor_id': factor_id,
                'turnover': recent_turnover,
                'message': f'因子{factor_id}换手率过高，交易成本�?
            })

        return alerts
```

---

## 8. 因子统计总览

| 因子类别 | 因子数量 | 文档位置 |
|----------|----------|----------|
| Alpha趋势 | 14+ | [02_ALPHA_FACTORS_INDEX.md](../02_ALPHA_FACTORS_INDEX.md) |
| Alpha均值回�?| 12+ | [02_ALPHA_FACTORS_INDEX.md](../02_ALPHA_FACTORS_INDEX.md) |
| Alpha价�?| 11+ | [02_ALPHA_FACTORS_INDEX.md](../02_ALPHA_FACTORS_INDEX.md) |
| Alpha成长 | 10+ | [02_ALPHA_FACTORS_INDEX.md](../02_ALPHA_FACTORS_INDEX.md) |
| Alpha质量 | 17+ | [02_ALPHA_FACTORS_INDEX.md](../02_ALPHA_FACTORS_INDEX.md) |
| Alpha动量 | 9+ | [02_ALPHA_FACTORS_INDEX.md](../02_ALPHA_FACTORS_INDEX.md) |
| Alpha情绪 | 14+ | [02_ALPHA_FACTORS_INDEX.md](../02_ALPHA_FACTORS_INDEX.md) |
| Barra风格 | 10 | [T.03.RF001.barra_style_factors.md](../03_RISK_FACTORS/T.03.RF001.barra_style_factors.md) |
| 行业因子 | 28+ | [T.03.RF002.industry_factors.md](../03_RISK_FACTORS/T.03.RF002.industry_factors.md) |
| 尾部风险 | 8+ | [T.03.RF003.tail_risk_factors.md](../03_RISK_FACTORS/T.03.RF003.tail_risk_factors.md) |
| THS_BD数据�?| 5700+ | [THS_BD_COMPLETE_INDICATOR_LIST.md](../04_DATA_SOURCE/IFIND/financial_statements/THS_BD_COMPLETE_INDICATOR_LIST.md) |
| **合计** | **5900+** | |

---

## 9. 快速导�?

| 需�?| 路径 |
|------|------|
| Alpha因子列表 | [02_ALPHA_FACTORS_INDEX.md](../02_ALPHA_FACTORS_INDEX.md) |
| 风险因子列表 | [03_RISK_FACTORS/](../03_RISK_FACTORS/) |
| THS_BD完整指标 | [THS_BD_COMPLETE_INDICATOR_LIST.md](../04_DATA_SOURCE/IFIND/financial_statements/THS_BD_COMPLETE_INDICATOR_LIST.md) |
| 因子注册�?| [FACTOR_CATALOG.md](../06_REGISTRY/FACTOR_CATALOG.md) |
| 因子计算框架 | [FACTOR_CALCULATION_FRAMEWORK.md](FACTOR_CALCULATION_FRAMEWORK.md) |

---

**版本**: 2.0 | **更新**: 2026-04-03 | **合并**: FACTOR_TAXONOMY.md
