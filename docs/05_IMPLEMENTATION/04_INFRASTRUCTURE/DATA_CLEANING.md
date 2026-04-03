---
module_id: IMPL_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部署
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 数据清洗

> 自动化数据清洗与质量控制
>
> **版本**: v1.0
> **更新**: 2026-03-28
> **优先级**: P1 - 核心模块
> **Layer**: Layer 0 (数据层)
> **索引**: D.04.CLN.001

---

## 1. 概述

数据清洗是量化系统的基础，确保进入系统的数据准确、完整、一致。

**清洗流程**：
```
原始数据 → 去重 → 缺失值处理 → 异常值检测 → 格式转换 → 标准化 → 质量检查 → 存储
```

---

## 2. 清洗规则配置

```python
CLEANING_RULES = {
    'OHLCV': {
        'deduplication': {
            'keys': ['stock_code', 'trade_date'],
            'keep': 'last'  # last | first
        },
        'missing_value': {
            'open': 'forward_fill',
            'high': 'max',
            'low': 'min',
            'close': 'forward_fill',
            'volume': 0
        },
        'anomaly_detection': [
            'price_inversion',      # high < low
            'negative_volume',      # volume < 0
            'zero_price',           # price == 0
            'limit_move'            # |return| > 0.11
        ],
        'format_conversion': {
            'date': 'datetime',
            'stock_code': 'str'
        }
    },
    'FUNDAMENTAL': {
        'deduplication': {
            'keys': ['stock_code', 'report_date'],
            'keep': 'last'
        },
        'missing_value': {
            'value': 'industry_mean'
        },
        'anomaly_detection': [
            'negative_value',
            'extreme_outlier'
        ],
        'format_conversion': {
            'report_date': 'datetime'
        }
    },
    'MONEY_FLOW': {
        'deduplication': {
            'keys': ['stock_code', 'trade_date'],
            'keep': 'last'
        },
        'missing_value': {
            'value': 0
        },
        'anomaly_detection': [],
        'format_conversion': {}
    }
}
```

---

## 3. 清洗引擎实现

### 3.1 主清洗类

```python
import pandas as pd
import numpy as np
from typing import Callable

class DataCleaner:
    """数据清洗引擎"""

    def __init__(self, rules: dict = None):
        self.rules = rules or CLEANING_RULES

    def clean(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        执行完整清洗流程

        Parameters:
        -----------
        df : pd.DataFrame
            原始数据
        data_type : str
            'OHLCV' | 'FUNDAMENTAL' | 'MONEY_FLOW'

        Returns:
        --------
        pd.DataFrame: 清洗后的数据
        """
        rules = self.rules.get(data_type, {})
        if not rules:
            return df

        df_cleaned = df.copy()

        # 1. 去重
        if 'deduplication' in rules:
            df_cleaned = self._deduplicate(df_cleaned, rules['deduplication'])

        # 2. 缺失值处理
        if 'missing_value' in rules:
            df_cleaned = self._fill_missing(df_cleaned, rules['missing_value'])

        # 3. 异常值检测与处理
        if 'anomaly_detection' in rules:
            df_cleaned, anomalies = self._detect_anomalies(
                df_cleaned,
                rules['anomaly_detection']
            )

        # 4. 格式转换
        if 'format_conversion' in rules:
            df_cleaned = self._convert_format(df_cleaned, rules['format_conversion'])

        return df_cleaned

    def _deduplicate(self, df: pd.DataFrame, config: dict) -> pd.DataFrame:
        """去重处理"""
        keys = config['keys']
        keep = config.get('keep', 'last')
        return df.drop_duplicates(subset=keys, keep=keep)

    def _fill_missing(self, df: pd.DataFrame, config: dict) -> pd.DataFrame:
        """缺失值填充"""
        df_filled = df.copy()

        for col, method in config.items():
            if col not in df_filled.columns:
                continue

            if method == 'forward_fill':
                df_filled[col] = df_filled[col].ffill()
            elif method == 'backward_fill':
                df_filled[col] = df_filled[col].bfill()
            elif method == 'mean':
                df_filled[col] = df_filled[col].fillna(df_filled[col].mean())
            elif method == 'median':
                df_filled[col] = df_filled[col].fillna(df_filled[col].median())
            elif method == 0 or method == '0':
                df_filled[col] = df_filled[col].fillna(0)
            elif method == 'industry_mean':
                # 需要行业信息，简化为全局均值
                df_filled[col] = df_filled[col].fillna(df_filled[col].mean())

        return df_filled

    def _detect_anomalies(
        self,
        df: pd.DataFrame,
        detection_rules: list
    ) -> tuple:
        """异常值检测"""
        anomalies = {}
        df_checked = df.copy()

        for rule in detection_rules:
            if rule == 'price_inversion' and 'high' in df.columns and 'low' in df.columns:
                mask = df_checked['high'] < df_checked['low']
                anomalies['price_inversion'] = mask.sum()
                # 修正：取high和low的均值
                df_checked.loc[mask, 'high'] = df_checked.loc[mask, ['high', 'low']].max(axis=1)
                df_checked.loc[mask, 'low'] = df_checked.loc[mask, ['high', 'low']].min(axis=1)

            elif rule == 'negative_volume' and 'volume' in df.columns:
                mask = df_checked['volume'] < 0
                anomalies['negative_volume'] = mask.sum()
                df_checked.loc[mask, 'volume'] = 0

            elif rule == 'zero_price' and 'close' in df.columns:
                mask = df_checked['close'] <= 0
                anomalies['zero_price'] = mask.sum()
                df_checked.loc[mask, 'close'] = np.nan

            elif rule == 'limit_move' and 'close' in df.columns:
                returns = df_checked['close'].pct_change()
                mask = returns.abs() > 0.11
                anomalies['limit_move'] = mask.sum()
                # 涨跌停数据保留，但标记

        return df_checked, anomalies
```

---

## 4. 数据质量检查

### 4.1 质量检查器

```python
class DataQualityChecker:
    """数据质量检查器"""

    def check(self, df: pd.DataFrame, data_type: str) -> dict:
        """
        检查数据质量

        Returns:
        --------
        dict: {passed: bool, issues: list, score: float}
        """
        issues = []

        # 检查缺失值
        missing = df.isnull().sum()
        if missing.any():
            issues.append({
                'type': 'MISSING_VALUE',
                'columns': missing[missing > 0].to_dict(),
                'severity': 'HIGH'
            })

        # 检查重复
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues.append({
                'type': 'DUPLICATE_ROWS',
                'count': duplicates,
                'severity': 'MEDIUM'
            })

        # 数据类型特定检查
        if data_type == 'OHLCV':
            issues.extend(self._check_ohlcv(df))
        elif data_type == 'FUNDAMENTAL':
            issues.extend(self._check_fundamental(df))

        score = max(0, 100 - len(issues) * 10 - sum(i.get('count', 0) for i in issues) * 0.1)

        return {
            'passed': len([i for i in issues if i['severity'] == 'HIGH']) == 0,
            'issues': issues,
            'score': score,
            'row_count': len(df)
        }

    def _check_ohlcv(self, df: pd.DataFrame) -> list:
        """OHLCV数据特定检查"""
        issues = []

        if 'high' in df.columns and 'low' in df.columns:
            if (df['high'] < df['low']).any():
                issues.append({
                    'type': 'PRICE_INVERSION',
                    'severity': 'HIGH'
                })

        if 'volume' in df.columns:
            if (df['volume'] < 0).any():
                issues.append({
                    'type': 'NEGATIVE_VOLUME',
                    'severity': 'HIGH'
                })

        if 'close' in df.columns:
            if (df['close'] <= 0).any():
                issues.append({
                    'type': 'ZERO_OR_NEGATIVE_PRICE',
                    'severity': 'HIGH'
                })

        return issues

    def _check_fundamental(self, df: pd.DataFrame) -> list:
        """基本面数据特定检查"""
        issues = []

        # 检查负值
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if (df[col] < 0).any():
                issues.append({
                    'type': 'NEGATIVE_VALUE',
                    'column': col,
                    'severity': 'MEDIUM'
                })

        return issues
```

### 4.2 质量报告生成

```python
class QualityReportGenerator:
    """数据质量报告生成器"""

    def generate(self, check_result: dict) -> str:
        """生成质量报告"""
        status = "✅ PASS" if check_result['passed'] else "❌ FAIL"

        report = f"""
# 数据质量报告

## 总体状态
- **状态**: {status}
- **质量评分**: {check_result['score']:.1f}/100
- **数据行数**: {check_result['row_count']}

## 问题列表
"""

        if not check_result['issues']:
            report += "- 无问题\n"
        else:
            for issue in check_result['issues']:
                report += f"""
### {issue['type']}
- **严重程度**: {issue['severity']}
- **详情**: {issue}
"""

        return report
```

---

## 5. 增量更新处理

```python
class IncrementalCleaner:
    """增量数据清洗"""

    def __init__(self, cleaner: DataCleaner, storage):
        self.cleaner = cleaner
        self.storage = storage

    def process_incremental(
        self,
        new_data: pd.DataFrame,
        data_type: str,
        key_columns: list
    ) -> pd.DataFrame:
        """
        处理增量数据：合并新数据和历史数据，去重

        Parameters:
        -----------
        new_data : pd.DataFrame
            新数据
        data_type : str
            数据类型
        key_columns : list
            主键列

        Returns:
        --------
        pd.DataFrame: 合并后的清洗数据
        """
        # 加载历史数据
        historical_data = self.storage.load(data_type)

        if historical_data is not None:
            # 合并
            combined = pd.concat([historical_data, new_data], ignore_index=True)
        else:
            combined = new_data

        # 清洗
        cleaned = self.cleaner.clean(combined, data_type)

        # 只保留最新数据
        cleaned = cleaned.sort_values(key_columns).drop_duplicates(
            subset=key_columns,
            keep='last'
        )

        return cleaned
```

---

## 6. 配置模板

```yaml
# config/data_cleaning.yaml
data_cleaning:
  # 清洗规则
  rules:
    OHLCV:
      deduplication:
        keys: ["stock_code", "trade_date"]
        keep: "last"
      missing_value:
        close: "forward_fill"
        volume: 0
      anomaly_detection:
        - "price_inversion"
        - "negative_volume"
        - "zero_price"

    FUNDAMENTAL:
      deduplication:
        keys: ["stock_code", "report_date"]
        keep: "last"
      missing_value:
        value: "industry_mean"
      anomaly_detection:
        - "negative_value"

  # 质量检查阈值
  quality_thresholds:
    min_score: 90
    max_missing_ratio: 0.05
    max_duplicate_ratio: 0.01
```

---

## 7. 目录位置

```
04_INFRASTRUCTURE/
├── STORAGE_ARCHITECTURE.md      # 存储架构
├── DAILY_PIPELINE.md            # 数据流水线
└── DATA_CLEANING.md            # 本文档 ⭐
```

---

## 8. 接口定义

| 接口 | 说明 |
|------|------|
| **上游接口** | 智能下载调度器、多数据源适配器 |
| **下游接口** | 数据存储、质量报告系统 |
| **输入格式** | pd.DataFrame (原始数据) |
| **输出格式** | pd.DataFrame (清洗后数据) |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |
