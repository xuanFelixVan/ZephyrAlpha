---
module_id: FACTOR_BLUEPRINT_002
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-02
owner: 首席文档架构师
standard_type: 专业量化机构蓝图
applicable_scope: 全系统架构设计
compliance_level: 初始标准
parent_document: ../README.md
implementation_status: 设计阶段
implementation_progress: 0%
---


# 数据清洗引擎蓝图

> 清风量化系统 v5.0 - 自动化数据清洗引擎
> **索引**: `DATA.CLN.001`
> **开发时间**: 10h
> **核心定位**: 确保数据质量，为因子计算和策略回测提供可靠数据


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **自动化** | 规则配置化，减少人工干预 |
| **可追溯** | 记录所有清洗操作，支持回溯 |
| **保守清洗** | 保留原始数据，只标记异常 |
| **可配置** | 清洗规则通过YAML配置 |


## 2. 系统架构

### 2.1 清洗引擎架构

```
┌─────────────────────────────────────────────────────────────┐
│                    数据清洗引擎                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  原始数据   │───▶│  规则引擎   │───▶│  清洗结果   │     │
│  │  Raw Data  │    │ RuleEngine │    │ CleanResult │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                            │                                 │
│                            ▼                                 │
│                     ┌─────────────┐                         │
│                     │  异常记录   │                         │
│                     │ AuditLog   │                         │
│                     └─────────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 清洗流程

```
原始数据 ──▶ 缺失值处理 ──▶ 异常值检测 ──▶ 类型转换 ──▶ 范围校验 ──▶ 清洗后数据
              │               │              │              │
              ▼               ▼              ▼              ▼
          填充/删除       标记/裁剪     格式统一       边界处理
```


## 3. 核心实现

### 3.1 清洗规则定义

```python
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Dict
from enum import Enum
import pandas as pd
import numpy as np

class CleaningOperation(Enum):
    FILL_FORWARD = "fill_forward"
    FILL_BACKWARD = "fill_backward"
    FILL_VALUE = "fill_value"
    DROP = "drop"
    FLAG = "flag"
    CLIP = "clip"
    INTERPOLATE = "interpolate"

class AnomalyType(Enum):
    MISSING_VALUE = "missing_value"
    OUTLIER = "outlier"
    INVALID_TYPE = "invalid_type"
    OUT_OF_RANGE = "out_of_range"
    INCONSISTENT = "inconsistent"

@dataclass
class CleaningRule:
    """清洗规则定义

    索引: DATA.CLN.001-R01
    """
    rule_id: str
    column: str
    operation: CleaningOperation
    params: Dict[str, Any]
    condition: Optional[Callable] = None
    severity: str = "warning"

@dataclass
class ValidationRule:
    """验证规则定义

    索引: DATA.CLN.001-R02
    """
    rule_id: str
    column: str
    validator: Callable[[Any], bool]
    error_message: str
    severity: str = "error"
```

### 3.2 清洗引擎核心

```python
class DataCleaningEngine:
    """数据清洗引擎

    索引: DATA.CLN.001-M01
    上游: IntelligentScheduler
    下游: DataStorage, FactorCalculator
    """

    def __init__(self, config: Dict):
        self.config = config
        self.rules: List[CleaningRule] = []
        self.validation_rules: List[ValidationRule] = []
        self.audit_log: List[CleaningRecord] = []
        self.rule_loader = RuleLoader(config)

    def load_rules(self, rule_config: List[Dict]) -> None:
        """加载清洗规则

        参数:
            rule_config: 规则配置列表
        """
        for rule_dict in rule_config:
            rule = CleaningRule(**rule_dict)
            self.rules.append(rule)

    def clean(self, df: pd.DataFrame, data_type: str = "ohlcv") -> CleaningResult:
        """执行数据清洗

        参数:
            df: 原始数据DataFrame
            data_type: 数据类型 (ohlcv, fundamental, etc.)

        返回:
            CleaningResult {
                'data': pd.DataFrame,      # 清洗后数据
                'records': List[CleaningRecord], # 操作记录
                'summary': CleaningSummary    # 清洗摘要
            }
        """
        df_clean = df.copy()
        records = []
        stats = CleaningStats()

        for rule in self.rules:
            if rule.column not in df_clean.columns:
                continue

            before_count = df_clean[rule.column].isna().sum()
            df_clean, record = self._apply_rule(df_clean, rule)
            after_count = df_clean[rule.column].isna().sum()

            records.append(record)
            stats.add_record(rule.rule_id, before_count, after_count)

        validation_result = self._validate(df_clean)

        return CleaningResult(
            data=df_clean,
            records=records,
            summary=CleaningSummary(stats=stats, validation=validation_result)
        )

    def _apply_rule(self, df: pd.DataFrame, rule: CleaningRule) -> tuple:
        """应用单条规则

        参数:
            df: 数据
            rule: 规则

        返回:
            (处理后数据, 清洗记录)
        """
        record = CleaningRecord(
            rule_id=rule.rule_id,
            column=rule.column,
            operation=rule.operation.value,
            before_count=df[rule.column].isna().sum()
        )

        if rule.condition and not rule.condition(df):
            record.skipped = True
            return df, record

        if rule.operation == CleaningOperation.FILL_FORWARD:
            df[rule.column] = df[rule.column].ffill()

        elif rule.operation == CleaningOperation.FILL_BACKWARD:
            df[rule.column] = df[rule.column].bfill()

        elif rule.operation == CleaningOperation.FILL_VALUE:
            fill_value = rule.params.get('value', 0)
            df[rule.column] = df[rule.column].fillna(fill_value)

        elif rule.operation == CleaningOperation.DROP:
            df = df.dropna(subset=[rule.column])

        elif rule.operation == CleaningOperation.FLAG:
            mask = df[rule.column].isna()
            df[f"{rule.column}_clean_flag"] = mask.astype(int)

        elif rule.operation == CleaningOperation.CLIP:
            lower = rule.params.get('lower', -np.inf)
            upper = rule.params.get('upper', np.inf)
            df[rule.column] = df[rule.column].clip(lower, upper)

        elif rule.operation == CleaningOperation.INTERPOLATE:
            method = rule.params.get('method', 'linear')
            df[rule.column] = df[rule.column].interpolate(method=method)

        record.after_count = df[rule.column].isna().sum()
        record.rows_affected = record.before_count - record.after_count

        return df, record

    def _validate(self, df: pd.DataFrame) -> ValidationResult:
        """验证清洗结果

        参数:
            df: 清洗后数据

        返回:
            验证结果
        """
        errors = []
        warnings = []

        for rule in self.validation_rules:
            if rule.column not in df.columns:
                continue

            try:
                valid = rule.validator(df[rule.column])
                if not valid:
                    if rule.severity == "error":
                        errors.append(rule.error_message)
                    else:
                        warnings.append(rule.error_message)
            except Exception as e:
                errors.append(f"Validation error for {rule.column}: {str(e)}")

        return ValidationResult(errors=errors, warnings=warnings)
```

### 3.3 异常值检测

```python
class OutlierDetector:
    """异常值检测器

    索引: DATA.CLN.001-M02
    """

    @staticmethod
    def detect_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
        """Z-Score异常值检测

        参数:
            series: 数据序列
            threshold: Z-Score阈值

        返回:
            布尔序列，True表示异常
        """
        mean = series.mean()
        std = series.std()
        z_scores = np.abs((series - mean) / std)
        return z_scores > threshold

    @staticmethod
    def detect_iqr(series: pd.Series, factor: float = 1.5) -> pd.Series:
        """IQR异常值检测

        参数:
            series: 数据序列
            factor: IQR倍数

        返回:
            布尔序列，True表示异常
        """
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        return (series < lower_bound) | (series > upper_bound)

    @staticmethod
    def detect_mad(series: pd.Series, threshold: float = 3.5) -> pd.Series:
        """MAD异常值检测（适合金融数据）

        参数:
            series: 数据序列
            threshold: MAD倍数

        返回:
            布尔序列，True表示异常
        """
        median = series.median()
        mad = np.median(np.abs(series - median))
        modified_z_scores = 0.6745 * (series - median) / mad
        return np.abs(modified_z_scores) > threshold
```


## 4. OHLCV清洗规则

### 4.1 标准OHLCV规则

```yaml
# config/cleaning_rules/ohlcv.yaml

rules:
  - rule_id: CLN_OHLCV_001
    column: open
    operation: fill_forward
    params:
      limit: 5
    severity: warning

  - rule_id: CLN_OHLCV_002
    column: high
    operation: flag
    severity: warning

  - rule_id: CLN_OHLCV_003
    column: low
    operation: flag
    severity: warning

  - rule_id: CLN_OHLCV_004
    column: close
    operation: interpolate
    params:
      method: linear
    severity: warning

  - rule_id: CLN_OHLCV_005
    column: volume
    operation: fill_value
    params:
      value: 0
    severity: warning

  - rule_id: CLN_OHLCV_006
    column: close
    operation: clip
    params:
      lower: 0.01
      upper: null
    severity: error

  - rule_id: CLN_OHLCV_007
    column: high
    operation: validate_high_low
    params:
      min_ratio: 0.5
      max_ratio: 2.0
    severity: error
```

### 4.2 异常检测规则

```yaml
# config/cleaning_rules/outlier_detection.yaml

outlier_detection:
  method: zscore  # zscore, iqr, mad
  threshold: 3.0

  apply_to:
    - close
    - volume

  actions:
    - flag  # flag, clip, drop
    preserve_original: true  # 保留原始值，只标记
```


## 5. 清洗结果

### 5.1 结果数据结构

```python
@dataclass
class CleaningRecord:
    """清洗记录

    索引: DATA.CLN.001-D01
    """
    rule_id: str
    column: str
    operation: str
    before_count: int
    after_count: int
    rows_affected: int
    timestamp: datetime = field(default_factory=datetime.now)
    skipped: bool = False

@dataclass
class CleaningStats:
    """清洗统计

    索引: DATA.CLN.001-D02
    """
    total_rows_processed: int = 0
    total_missing_filled: int = 0
    total_outliers_flagged: int = 0
    total_errors: int = 0
    by_rule: Dict[str, Dict] = field(default_factory=dict)

    def add_record(self, rule_id: str, before: int, after: int):
        self.total_missing_filled += (before - after)
        if rule_id not in self.by_rule:
            self.by_rule[rule_id] = {'filled': 0, 'flagged': 0}
        self.by_rule[rule_id]['filled'] += (before - after)

@dataclass
class CleaningResult:
    """清洗结果

    索引: DATA.CLN.001-D03
    """
    data: pd.DataFrame
    records: List[CleaningRecord]
    summary: CleaningSummary
```

### 5.2 清洗报告

```python
class CleaningReport:
    """清洗报告生成器

    索引: DATA.CLN.001-M03
    """

    def generate(self, result: CleaningResult) -> str:
        """生成清洗报告

        参数:
            result: 清洗结果

        返回:
            Markdown格式报告
        """
        report = f"""
# 数据清洗报告

## 清洗摘要

| 指标 | 值 |
|------|-----|
| 处理行数 | {result.summary.stats.total_rows_processed} |
| 缺失值填充 | {result.summary.stats.total_missing_filled} |
| 异常值标记 | {result.summary.stats.total_outliers_flagged} |
| 错误数 | {result.summary.stats.total_errors} |

## 清洗详情

| 规则ID | 列 | 操作 | 处理前行 | 处理后行 | 影响行数 |
|--------|-----|------|----------|----------|----------|
"""

        for record in result.records:
            if record.skipped:
                continue
            report += f"| {record.rule_id} | {record.column} | {record.operation} | {record.before_count} | {record.after_count} | {record.rows_affected} |\n"

        return report
```


## 6. 集成接口

### 6.1 上游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| IntelligentScheduler | schedule() | 获取待清洗数据 |
| DataSourceAdapter | fetch() | 获取原始数据 |

### 6.2 下游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| DataStorage | save() | 存储清洗后数据 |
| FactorCalculator | calculate() | 使用清洗后数据 |


## 7. 监控指标

| 指标 | 说明 | 阈值 |
|------|------|------|
| cleaning_rows_processed | 处理行数/批次 | - |
| cleaning_missing_filled | 缺失值填充数 | <10% |
| cleaning_outlier_rate | 异常值比例 | <5% |
| cleaning_error_rate | 清洗错误率 | <0.1% |
| cleaning_latency | 清洗耗时 | <1s/千行 |


## 8. 开发任务分解(10h)

| 任务 | 时间 | 交付物 |
|------|------|--------|
| 清洗规则引擎 | 3h | CleaningRule, RuleEngine |
| 缺失值处理 | 1h | Fill/Interolate实现 |
| 异常值检测 | 2h | OutlierDetector |
| 验证框架 | 1h | ValidationRule, Validator |
| 报告生成 | 1h | CleaningReport |
| OHLCV规则配置 | 1h | ohlcv.yaml |
| 单元测试 | 1h | test_cleaning_engine.py |


**维护者**: 清风量化系统
**索引**: `DATA.CLN.001`
**最后更新**: 2026-03-29
