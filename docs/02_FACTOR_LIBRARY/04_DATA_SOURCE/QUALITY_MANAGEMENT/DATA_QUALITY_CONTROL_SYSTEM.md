---
module_id: FACTOR_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管�?compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?---

# 数据质量控制系统

> **模块编号**: M-DQ-001 (Data Quality)
> **版本**: 1.0
> **创建日期**: 2026-03-28
> **优先�?*: P0

---

## 1. 系统概述

### 1.1 目标
确保进入系统的数据满足量化分析的质量要求，防�?垃圾进，垃圾�?（GIGO: Garbage In, Garbage Out）�?
### 1.2 数据质量维度

| 维度 | 说明 | 检查方�?|
|------|------|----------|
| **完整�?* | 数据无缺�?| 缺失值检�?|
| **有效�?* | 数据在合理范围内 | 有效性规�?|
| **一致�?* | 数据格式统一 | 格式校验 |
| **时效�?* | 数据及时更新 | 时间戳检�?|
| **准确�?* | 数据正确无误 | 合理性检�?|
| **去重�?* | 无重复记�?| 重复检�?|

---

## 2. 数据质量检查框�?
### 2.1 核心类设�?
```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Callable
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime

class Severity(Enum):
    """问题严重级别"""
    CRITICAL = "critical"  # 致命，数据不可用
    WARNING = "warning"    # 警告，数据可用但需注意
    INFO = "info"         # 信息，提�?
@dataclass
class DataIssue:
    """数据问题"""
    severity: Severity
    category: str
    message: str
    field: str
    row_index: Optional[int] = None
    value: any = None
    expected: any = None

    def __str__(self):
        location = f"[{self.field}]" if self.field else ""
        return f"[{self.severity.value.upper()}] {location} {self.message}"

@dataclass
class DataQualityResult:
    """数据质量检查结�?""
    passed: bool
    issues: List[DataIssue] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.now)
    record_count: int = 0
    issue_count: int = 0
    quality_score: float = 1.0  # 0-1的质量分�?
    def add_issue(self, issue: DataIssue):
        self.issues.append(issue)
        self.issue_count += 1
        if issue.severity == Severity.CRITICAL:
            self.passed = False
            self.quality_score *= 0.5
        elif issue.severity == Severity.WARNING:
            self.quality_score *= 0.8

    def get_summary(self) -> Dict:
        return {
            "passed": self.passed,
            "quality_score": round(self.quality_score, 3),
            "total_issues": self.issue_count,
            "critical_count": len([i for i in self.issues if i.severity == Severity.CRITICAL]),
            "warning_count": len([i for i in self.issues if i.severity == Severity.WARNING]),
            "info_count": len([i for i in self.issues if i.severity == Severity.INFO]),
        }
```

### 2.2 主检查器

```python
class DataQualityChecker:
    """数据质量检查器"""

    def __init__(self, config: 'DataQualityConfig' = None):
        self.config = config or DataQualityConfig()
        self.issues: List[DataIssue] = []

    def check(self, df: pd.DataFrame, data_type: str = "ohlcv") -> DataQualityResult:
        """
        执行完整的数据质量检�?
        参数:
            df: 待检查的数据
            data_type: 数据类型 ("ohlcv", "factor", "fundamental")

        返回:
            DataQualityResult: 检查结�?        """
        result = DataQualityResult(passed=True, record_count=len(df))

        check_methods = {
            "ohlcv": [self._check_missing, self._check_duplicates,
                     self._check_ohlcv_validity, self._check_price_continuity],
            "factor": [self._check_missing, self._check_duplicates,
                      self._check_factor_range, self._check_factor_distribution],
            "fundamental": [self._check_missing, self._check_duplicates,
                          self._check_financial_ratio]
        }

        methods = check_methods.get(data_type, check_methods["ohlcv"])

        for method in methods:
            method(df, result)

        return result

    def check_and_raise(self, df: pd.DataFrame, data_type: str = "ohlcv") -> pd.DataFrame:
        """
        检查数据质量，不合格则抛出异常
        """
        result = self.check(df, data_type)
        if not result.passed:
            issues_str = "\n".join([str(i) for i in result.issues])
            raise DataQualityError(
                f"数据质量检查失�?({result.issue_count} issues):\n{issues_str}"
            )
        return df
```

---

## 3. 缺失值检�?
### 3.1 缺失值检测器

```python
@dataclass
class MissingValueConfig:
    """缺失值检查配�?""
    max_missing_ratio: float = 0.05      # 最大缺失率(5%)
    critical_fields: List[str] = None     # 关键字段，缺失直接失�?    fill_strategies: Dict[str, str] = None  # 填充策略

class MissingValueChecker:
    """缺失值检测器"""

    def _check_missing(self, df: pd.DataFrame, result: DataQualityResult):
        """检查缺失�?""
        config = self.config.missing_value

        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_ratio = missing_count / len(df)

            if missing_count == 0:
                continue

            # 检查是否是关键字段
            if config.critical_fields and col in config.critical_fields:
                if missing_ratio > 0:
                    result.add_issue(DataIssue(
                        severity=Severity.CRITICAL,
                        category="missing",
                        message=f"关键字段缺失 {missing_count} �?({missing_ratio:.2%})",
                        field=col
                    ))
                    continue

            # 检查缺失率阈�?            if missing_ratio > config.max_missing_ratio:
                result.add_issue(DataIssue(
                    severity=Severity.CRITICAL,
                    category="missing",
                    message=f"缺失�?{missing_ratio:.2%} 超过阈�?{config.max_missing_ratio:.2%}",
                    field=col
                ))
            else:
                result.add_issue(DataIssue(
                    severity=Severity.WARNING,
                    category="missing",
                    message=f"字段缺失 {missing_count} �?({missing_ratio:.2%})",
                    field=col
                ))
```

### 3.2 缺失值填充策�?
```python
class MissingValueFiller:
    """缺失值填充器"""

    STRATEGIES = {
        "forward": lambda s: s.fillna(method='ffill'),      # 前向填充
        "backward": lambda s: s.fillna(method='bfill'),    # 后向填充
        "linear": lambda s: s.interpolate(method='linear'), # 线性插�?        "mean": lambda s: s.fillna(s.mean()),               # 均值填�?        "median": lambda s: s.fillna(s.median()),           # 中位数填�?        "zero": lambda s: s.fillna(0),                      # 零填�?        "ffill_then_mean": lambda s: s.fillna(method='ffill').fillna(s.mean()),
    }

    @classmethod
    def fill(cls, df: pd.DataFrame,
             column: str,
             strategy: str = "forward") -> pd.Series:
        """填充指定列的缺失�?""
        if strategy not in cls.STRATEGIES:
            raise ValueError(f"未知填充策略: {strategy}")

        filled = cls.STRATEGIES)
        return filled

    @classmethod
    def fill_ohlcv(cls, df: pd.DataFrame,
                   price_columns: List[str] = None,
                   volume_column: str = "volume") -> pd.DataFrame:
        """
        填充OHLCV数据的缺失�?        价格列用前向填充，成交量�?填充
        """
        df = df.copy()
        price_cols = price_columns or ['open', 'high', 'low', 'close']

        for col in price_cols:
            if col in df.columns:
                df[col] = cls.fill(df, col, "forward")

        if volume_column in df.columns:
            df[volume_column] = cls.fill(df, volume_column, "zero")

        return df
```

---

## 4. 有效性规则检�?
### 4.1 OHLCV有效性检�?
```python
class OHLCVValidityChecker:
    """OHLCV数据有效性检查器"""

    def _check_ohlcv_validity(self, df: pd.DataFrame, result: DataQualityResult):
        """检查OHLCV数据有效�?""

        # 1. 收盘�?>= 0
        if 'close' in df.columns:
            invalid_close = df[df['close'] < 0]
            if len(invalid_close) > 0:
                result.add_issue(DataIssue(
                    severity=Severity.CRITICAL,
                    category="validity",
                    message=f"存在 {len(invalid_close)} 条负价格记录",
                    field="close"
                ))

        # 2. 最高价 >= 最低价
        if 'high' in df.columns and 'low' in df.columns:
            invalid_range = df[df['high'] < df['low']]
            if len(invalid_range) > 0:
                result.add_issue(DataIssue(
                    severity=Severity.CRITICAL,
                    category="validity",
                    message=f"存在 {len(invalid_range)} 条最高价 < 最低价的记�?,
                    field="high/low"
                ))

        # 3. 开盘价和收盘价在高低价范围�?        for _, row in df.iterrows():
            if not (row['low'] <= row['open'] <= row['high']):
                result.add_issue(DataIssue(
                    severity=Severity.WARNING,
                    category="validity",
                    message=f"开盘价 {row['open']} 超出范围 [{row['low']}, {row['high']}]",
                    field="open",
                    row_index=_
                ))
            if not (row['low'] <= row['close'] <= row['high']):
                result.add_issue(DataIssue(
                    severity=Severity.WARNING,
                    category="validity",
                    message=f"收盘�?{row['close']} 超出范围 [{row['low']}, {row['high']}]",
                    field="close",
                    row_index=_
                ))

        # 4. 成交�?>= 0
        if 'volume' in df.columns:
            invalid_volume = df[df['volume'] < 0]
            if len(invalid_volume) > 0:
                result.add_issue(DataIssue(
                    severity=Severity.CRITICAL,
                    category="validity",
                    message=f"存在 {len(invalid_volume)} 条负成交量记�?,
                    field="volume"
                ))
```

### 4.2 股票代码有效性检�?
```python
@dataclass
class SecurityConfig:
    """证券数据配置"""
    valid_exchanges: List[str] = None  # 有效交易所
    valid_tick_pattern: str = r"^\d{6}\.[A-Z]$"  # 6位数�?大写字母

class SecurityChecker:
    """股票代码检查器"""

    def check_symbol(self, symbol: str, config: SecurityConfig = None) -> bool:
        """检查股票代码格�?""
        import re
        config = config or SecurityConfig()
        pattern = config.valid_tick_pattern

        if not re.match(pattern, symbol):
            return False

        # 检查交易所
        exchange = symbol.split('.')[-1]
        if config.valid_exchanges:
            return exchange in config.valid_exchanges

        return True

    def check_data_coverage(self, df: pd.DataFrame,
                            expected_symbols: List[str],
                            date_range: tuple) -> DataQualityResult:
        """检查数据覆盖度"""
        result = DataQualityResult(passed=True)

        # 检查日期范�?        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            start_date, end_date = date_range

            missing_dates = pd.date_range(start_date, end_date).difference(df['date'])
            if len(missing_dates) > 0:
                missing_ratio = len(missing_dates) / (end_date - start_date).days
                if missing_ratio > 0.1:  # 超过10%缺失
                    result.add_issue(DataIssue(
                        severity=Severity.WARNING,
                        category="coverage",
                        message=f"日期覆盖缺失 {len(missing_dates)} �?({missing_ratio:.1%})",
                        field="date"
                    ))

        # 检查股票覆�?        if 'symbol' in df.columns:
            df_symbols = set(df['symbol'].unique())
            expected = set(expected_symbols)
            missing_symbols = expected - df_symbols

            if missing_symbols:
                result.add_issue(DataIssue(
                    severity=Severity.WARNING,
                    category="coverage",
                    message=f"缺少 {len(missing_symbols)} 只股票数�? {list(missing_symbols)[:5]}",
                    field="symbol"
                ))

        return result
```

---

## 5. 重复检�?
### 5.1 重复记录检�?
```python
class DuplicateChecker:
    """重复数据检测器"""

    def _check_duplicates(self, df: pd.DataFrame, result: DataQualityResult):
        """检查重复记�?""

        # 1. 完全重复
        duplicates = df.duplicated()
        dup_count = duplicates.sum()

        if dup_count > 0:
            result.add_issue(DataIssue(
                severity=Severity.CRITICAL,
                category="duplicate",
                message=f"存在 {dup_count} 条完全重复的记录",
                field="__all__"
            ))

        # 2. 关键字段重复 (日期+股票代码)
        if 'date' in df.columns and 'symbol' in df.columns:
            key_dup = df.duplicated(subset=['date', 'symbol'], keep=False)
            key_dup_count = key_dup.sum()

            if key_dup_count > 0:
                result.add_issue(DataIssue(
                    severity=Severity.CRITICAL,
                    category="duplicate",
                    message=f"存在 {key_dup_count} 条日�?股票代码重复的记�?,
                    field="date+symbol"
                ))

        # 3. 重复日期检�?(同一股票同一日期多条记录)
        if 'date' in df.columns and 'symbol' in df.columns:
            grouped = df.groupby(['date', 'symbol']).size()
            multi_records = grouped[grouped > 1]

            if len(multi_records) > 0:
                result.add_issue(DataIssue(
                    severity=Severity.WARNING,
                    category="duplicate",
                    message=f"存在 {len(multi_records)} 个日期存在多条记�?,
                    field="date+symbol"
                ))
```

### 5.2 数据清洗接口

```python
class DataCleaner:
    """数据清洗�?""

    @staticmethod
    def remove_duplicates(df: pd.DataFrame,
                         subset: List[str] = None,
                         keep: str = "last") -> pd.DataFrame:
        """
        移除重复记录

        参数:
            df: 数据
            subset: 用于判断重复的列，None表示所有列
            keep: 保留策略 ("first", "last", False)
        """
        return df.drop_duplicates(subset=subset, keep=keep)

    @staticmethod
    def merge_duplicates(df: pd.DataFrame,
                         groupby_cols: List[str],
                         agg_rules: Dict[str, str]) -> pd.DataFrame:
        """
        合并重复记录
        对同一日期+股票的多条记录取均�?        """
        return df.groupby(groupby_cols).agg(agg_rules).reset_index()
```

---

## 6. 异常值检�?
### 6.1 统计方法检�?
```python
class OutlierDetector:
    """异常值检测器"""

    @staticmethod
    def zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
        """
        Z-Score方法
        超过threshold个标准差的视为异�?        """
        mean = series.mean()
        std = series.std()
        if std == 0:
            return pd.Series([False] * len(series), index=series.index)
        z_scores = np.abs((series - mean) / std)
        return z_scores > threshold

    @staticmethod
    def iqr(series: pd.Series, factor: float = 1.5) -> pd.Series:
        """
        IQR方法
        超过 Q1 - factor*IQR �?Q3 + factor*IQR 的视为异�?        """
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - factor * IQR
        upper = Q3 + factor * IQR
        return (series < lower) | (series > upper)

    @staticmethod
    def percentile(series: pd.Series,
                   lower: float = 0.01,
                   upper: float = 0.99) -> pd.Series:
        """
        百分位方�?        低于lower百分位或高于upper百分位的视为异常
        """
        lower_val = series.quantile(lower)
        upper_val = series.quantile(upper)
        return (series < lower_val) | (series > upper_val)

    @classmethod
    def detect_all(cls, df: pd.DataFrame,
                   column: str,
                   methods: List[str] = None) -> Dict[str, pd.Series]:
        """
        使用多种方法检测异常�?
        返回:
            Dict: {方法�? 异常值Series}
        """
        methods = methods or ["zscore", "iqr"]
        results = {}
        series = df[column]

        for method in methods:
            if method == "zscore":
                results[method] = cls.zscore(series)
            elif method == "iqr":
                results[method] = cls.iqr(series)
            elif method == "percentile":
                results[method] = cls.percentile(series)

        return results

    @classmethod
    def get_outlier_stats(cls, df: pd.DataFrame,
                          column: str,
                          methods: List[str] = None) -> pd.DataFrame:
        """获取异常值统计信�?""
        results = cls.detect_all(df, column, methods)

        stats = []
        for method, outliers in results.items():
            count = outliers.sum()
            ratio = count / len(df)
            indices = df[outliers].index.tolist()[:10]  # 最多显�?0�?
            stats.append({
                "method": method,
                "outlier_count": count,
                "outlier_ratio": f"{ratio:.2%}",
                "sample_indices": indices
            })

        return pd.DataFrame(stats)
```

### 6.2 业务规则检�?
```python
class BusinessRuleDetector:
    """业务规则异常检�?""

    @staticmethod
    def check_price_change(df: pd.DataFrame,
                          max_daily_change: float = 0.5) -> pd.DataFrame:
        """
        检查日内价格变化是否超过阈�?        默认日内涨跌超过50%视为异常
        """
        if 'close' not in df.columns or 'open' not in df.columns:
            return pd.Series([False] * len(df), index=df.index)

        daily_change = (df['close'] - df['open']) / df['open']
        return daily_change.abs() > max_daily_change

    @staticmethod
    def check_volume_spike(df: pd.DataFrame,
                          factor: float = 10.0) -> pd.Series:
        """
        检查成交量是否异常放大
        超过均值factor倍的视为异常
        """
        if 'volume' not in df.columns:
            return pd.Series([False] * len(df), index=df.index)

        mean_vol = df['volume'].mean()
        return df['volume'] > mean_vol * factor

    @staticmethod
    def check_high_low_range(df: pd.DataFrame,
                            max_range: float = 0.5) -> pd.Series:
        """
        检查高低点范围是否合理
        超过max_range(默认50%)的视为异�?        """
        if 'high' not in df.columns or 'low' not in df.columns:
            return pd.Series([False] * len(df), index=df.index)

        price_range = (df['high'] - df['low']) / df['low']
        return price_range > max_range

    @classmethod
    def check_all_rules(cls, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """执行所有业务规则检�?""
        return {
            "price_change": cls.check_price_change(df),
            "volume_spike": cls.check_volume_spike(df),
            "high_low_range": cls.check_high_low_range(df)
        }
```

---

## 7. 数据质量报告

### 7.1 报告生成�?
```python
class DataQualityReport:
    """数据质量报告生成�?""

    @staticmethod
    def generate(result: DataQualityResult,
                df: pd.DataFrame = None,
                data_name: str = "数据") -> str:
        """生成文本报告"""

        summary = result.get_summary()

        report = f"""
================================================================================
                        数据质量检查报�?================================================================================
数据名称: {data_name}
检查时�? {result.checked_at.strftime('%Y-%m-%d %H:%M:%S')}
数据记录�? {result.record_count}
--------------------------------------------------------------------------------
检查结�? {'�?通过' if summary['passed'] else '�?失败'}
质量评分: {summary['quality_score']:.1%}

问题汇�?
  - 致命问题: {summary['critical_count']} �?  - 警告问题: {summary['warning_count']} �?  - 提示信息: {summary['info_count']} �?
================================================================================
                            详细问题列表
================================================================================
"""

        if result.issues:
            for i, issue in enumerate(result.issues, 1):
                severity_icon = {
                    "critical": "🔴",
                    "warning": "🟡",
                    "info": "🔵"
                }[issue.severity.value]

                report += f"""
[{i}] {severity_icon} {issue.severity.value.upper()}: {issue.category}
    字段: {issue.field or 'N/A'}
    描述: {issue.message}
"""
                if issue.value is not None:
                    report += f"    当前�? {issue.value}\n"
                if issue.expected is not None:
                    report += f"    期望�? {issue.expected}\n"

        if df is not None:
            report += f"""
================================================================================
                            数据样本预览
================================================================================
�?�?
{df.head().to_string()}

数据类型:
{df.dtypes.to_string()}
"""

        return report

    @staticmethod
    def generate_html(result: DataQualityResult,
                     df: pd.DataFrame = None) -> str:
        """生成HTML报告"""
        summary = result.get_summary()

        html = f"""
        <html>
        <head><title>数据质量报告</title></head>
        <body>
        <h1>数据质量检查报�?/h1>
        <table border="1">
            <tr><th>检查时�?/th><td>{result.checked_at}</td></tr>
            <tr><th>记录�?/th><td>{result.record_count}</td></tr>
            <tr><th>结果</th><td>{'通过' if summary['passed'] else '失败'}</td></tr>
            <tr><th>质量评分</th><td>{summary['quality_score']:.1%}</td></tr>
        </table>

        <h2>问题汇�?/h2>
        <ul>
            <li>致命: {summary['critical_count']}</li>
            <li>警告: {summary['warning_count']}</li>
            <li>提示: {summary['info_count']}</li>
        </ul>

        <h2>详细问题</h2>
        <table border="1">
            <tr><th>级别</th><th>类别</th><th>字段</th><th>描述</th></tr>
"""

        for issue in result.issues:
            html += f"""
            <tr>
                <td>{issue.severity.value}</td>
                <td>{issue.category}</td>
                <td>{issue.field or 'N/A'}</td>
                <td>{issue.message}</td>
            </tr>
"""

        html += "</table></body></html>"
        return html
```

---

## 8. 与数据管道集�?
### 8.1 在DataHub中使�?
```python
class DataHub:
    """数据中心 - 集成数据质量检�?""

    def __init__(self, config: DataHubConfig):
        self.config = config
        self.quality_checker = DataQualityChecker()

    def get_ohlcv(self, symbol: str,
                 start_date: str,
                 end_date: str,
                 check_quality: bool = True) -> pd.DataFrame:
        """
        获取OHLCV数据，带质量检�?        """
        df = self._fetch_from_source(symbol, start_date, end_date)

        if check_quality:
            result = self.quality_checker.check(df, data_type="ohlcv")

            if not result.passed:
                logger.warning(
                    f"数据质量问题 detected for {symbol}: "
                    f"{result.issue_count} issues"
                )
                # 记录但不阻止返回
                self._log_quality_issues(symbol, result)

            # 自动清洗
            if result.quality_score < 0.8:
                df = self._clean_data(df)

        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """自动清洗数据"""
        # 移除重复
        df = DataCleaner.remove_duplicates(df)

        # 填充缺失�?        if 'close' in df.columns:
            df['close'] = MissingValueFiller.fill(df, 'close', 'forward')

        return df
```

### 8.2 质量配置

```python
@dataclass
class DataQualityConfig:
    """数据质量配置"""
    enabled: bool = True
    fail_on_critical: bool = True  # 致命问题是否抛出异常

    missing_value: MissingValueConfig = field(
        default_factory=lambda: MissingValueConfig(
            max_missing_ratio=0.05,
            critical_fields=['date', 'close'],
            fill_strategies={'close': 'forward', 'volume': 'zero'}
        )
    )

    outlier_detection: bool = True
    outlier_methods: List[str] = field(default_factory=lambda: ["zscore", "iqr"])

    business_rules: bool = True
    max_daily_change: float = 0.5  # 日内最大变�?0%
    max_volume_spike: float = 10.0  # 成交量最大放大倍数
```

---

## 9. 快速使用示�?
```python
# 1. 创建检查器
checker = DataQualityChecker()

# 2. 检查数�?df = pd.read_csv("stock_data.csv")
result = checker.check(df, data_type="ohlcv")

# 3. 查看结果
print(result.get_summary())

# 4. 生成报告
report = DataQualityReport.generate(result, df, "A股数�?)
print(report)

# 5. 自动清洗并重新检�?if not result.passed:
    df_cleaned = DataCleaner.remove_duplicates(df)
    df_cleaned = MissingValueFiller.fill_ohlcv(df_cleaned)
    result2 = checker.check(df_cleaned)
```

---

## 10. 配置文件

```yaml
# config/data_quality.yaml
data_quality:
  enabled: true
  fail_on_critical: false

  missing_value:
    max_missing_ratio: 0.05
    critical_fields:
      - date
      - close
      - symbol
    fill_strategies:
      close: forward
      open: forward
      high: forward
      low: forward
      volume: zero

  outlier_detection:
    enabled: true
    methods:
      - zscore
      - iqr
    zscore_threshold: 3.0
    iqr_factor: 1.5

  business_rules:
    enabled: true
    max_daily_change: 0.5      # 50%
    max_volume_spike: 10.0      # 10�?    max_high_low_range: 0.5     # 50%
```

---

**版本**: 1.0
**更新**: 2026-03-28
**状�?*: 草稿
