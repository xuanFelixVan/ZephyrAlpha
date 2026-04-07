---
module_id: DATA_QUALITY_METRICS_001
version: 1.0.0
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 首席文档架构师
standard_type: 数据质量标准
applicable_scope: 数据质量指标定义
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 已完成
responsibility: 数据质量指标定义与监控
---
---

# 数据质量指标定义

> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: 数据质量指标体系定义
- 定义六大质量维度和评分标准
- 提供质量指标计算方法
- 说明质量评估和改进流程

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 质量控制系统 | [DATA_QUALITY_CONTROL_SYSTEM.md](./DATA_QUALITY_CONTROL_SYSTEM.md) | 实现层 | 质量控制系统实现 |
| 质量索引 | [INDEX.md](./INDEX.md) | 上级索引 | 质量管理模块索引 |

**职责边界**:
- ✅ 本文档负责: 质量指标定义和计算方法
- ❌ 本文档不负责: 质量控制系统实现（由 DATA_QUALITY_CONTROL_SYSTEM.md 负责）

> 清风量化系统 - 数据质量评估标准
> **核心定位**: 提供标准化的数据质量指标体系，指导数据质量评估和改进

---

## 1. 质量维度体系

### 1.1 六大质量维度

| 维度 | 定义 | 重要性 | 权重 |
|------|------|--------|------|
| **完整性** | 数据无缺失 | 🔴 高 | 25% |
| **准确性** | 数据正确无误 | 🔴 高 | 25% |
| **一致性** | 数据格式统一 | 🟡 中 | 15% |
| **时效性** | 数据及时更新 | 🟡 中 | 15% |
| **有效性** | 数据在合理范围内 | 🟡 中 | 10% |
| **唯一性** | 无重复记录 | 🟢 低 | 10% |

### 1.2 质量评分标准

| 评分等级 | 分数范围 | 说明 | 处理建议 |
|----------|----------|------|----------|
| **优秀** | 90-100 | 数据质量优秀，可直接使用 | 继续保持 |
| **良好** | 80-89 | 数据质量良好，基本可用 | 小幅改进 |
| **一般** | 70-79 | 数据质量一般，需要清洗 | 重点改进 |
| **较差** | 60-69 | 数据质量较差，谨慎使用 | 大幅改进 |
| **不可用** | <60 | 数据质量不可用，需重新获取 | 重新采集 |

---

## 2. 完整性指标（Completeness）

### 2.1 指标定义

```python
from dataclasses import dataclass
from typing import List, Dict
import pandas as pd
import numpy as np

@dataclass
class CompletenessMetrics:
    """完整性指标"""
    
    @staticmethod
    def calculate_missing_ratio(df: pd.DataFrame, field: str) -> float:
        """计算字段缺失率"""
        return df[field].isna().sum() / len(df)
    
    @staticmethod
    def calculate_record_completeness(df: pd.DataFrame, required_fields: List[str]) -> float:
        """计算记录完整性"""
        complete_records = df[required_fields].dropna().shape[0]
        return complete_records / len(df)
    
    @staticmethod
    def calculate_field_completeness(df: pd.DataFrame) -> Dict[str, float]:
        """计算各字段完整性"""
        return {
            field: 1 - df[field].isna().sum() / len(df)
            for field in df.columns
        }
    
    @staticmethod
    def calculate_overall_completeness(df: pd.DataFrame, required_fields: List[str]) -> float:
        """计算整体完整性评分"""
        # 字段完整性权重
        field_weights = {field: 1.0 / len(required_fields) for field in required_fields}
        
        # 计算加权完整性
        completeness = 0
        for field in required_fields:
            field_completeness = 1 - df[field].isna().sum() / len(df)
            completeness += field_completeness * field_weights[field]
            
        return completeness * 100
```

### 2.2 完整性标准

| 数据类型 | 完整性要求 | 说明 |
|----------|-----------|------|
| **行情数据** | ≥95% | 日线数据缺失率≤5% |
| **财务数据** | ≥90% | 季度财务数据缺失率≤10% |
| **因子数据** | ≥85% | 因子数据缺失率≤15% |
| **宏观数据** | ≥80% | 宏观数据缺失率≤20% |

---

## 3. 准确性指标（Accuracy）

### 3.1 指标定义

```python
@dataclass
class AccuracyMetrics:
    """准确性指标"""
    
    @staticmethod
    def calculate_price_accuracy(df: pd.DataFrame) -> float:
        """计算价格准确性（基于涨跌幅限制）"""
        # A股涨跌停限制
        pct_chg = df['pct_chg']
        
        # 检查是否在合理范围内
        valid_count = ((pct_chg >= -20) & (pct_chg <= 20)).sum()
        
        return valid_count / len(df) * 100
    
    @staticmethod
    def calculate_financial_accuracy(df: pd.DataFrame) -> float:
        """计算财务数据准确性（基于资产负债平衡）"""
        # 检查资产负债是否平衡
        balance_check = np.abs(
            df['total_assets'] - (df['total_liabilities'] + df['equity'])
        ) / df['total_assets']
        
        # 允许1%误差
        valid_count = (balance_check <= 0.01).sum()
        
        return valid_count / len(df) * 100
    
    @staticmethod
    def calculate_cross_validation_accuracy(df1: pd.DataFrame, df2: pd.DataFrame, key: str) -> float:
        """计算交叉验证准确性"""
        # 合并两个数据源
        merged = pd.merge(df1, df2, on=key, suffixes=('_1', '_2'))
        
        # 比较关键字段
        accuracy_scores = []
        for field in ['close', 'volume']:
            if f'{field}_1' in merged.columns and f'{field}_2' in merged.columns:
                diff = np.abs(merged[f'{field}_1'] - merged[f'{field}_2'])
                max_val = np.maximum(np.abs(merged[f'{field}_1']), np.abs(merged[f'{field}_2']))
                relative_error = diff / (max_val + 1e-10)
                accuracy = (relative_error <= 0.01).sum() / len(merged) * 100
                accuracy_scores.append(accuracy)
        
        return np.mean(accuracy_scores)
```

### 3.2 准确性标准

| 检查类型 | 准确性要求 | 说明 |
|----------|-----------|------|
| **价格合理性** | ≥98% | 价格在合理范围内 |
| **财务平衡性** | ≥95% | 资产负债平衡 |
| **交叉验证** | ≥95% | 多数据源一致性 |

---

## 4. 一致性指标（Consistency）

### 4.1 指标定义

```python
@dataclass
class ConsistencyMetrics:
    """一致性指标"""
    
    @staticmethod
    def calculate_format_consistency(df: pd.DataFrame, field: str, expected_format: str) -> float:
        """计算格式一致性"""
        import re
        
        if expected_format == "date":
            pattern = r'\d{4}-\d{2}-\d{2}'
        elif expected_format == "datetime":
            pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        elif expected_format == "code":
            pattern = r'[0-9]{6}\.[A-Z]{2}'
        else:
            return 100.0
        
        # 检查格式匹配
        matches = df[field].astype(str).str.match(pattern)
        return matches.sum() / len(df) * 100
    
    @staticmethod
    def calculate_temporal_consistency(df: pd.DataFrame, date_field: str) -> float:
        """计算时间一致性"""
        # 检查时间序列是否连续
        df_sorted = df.sort_values(date_field)
        dates = pd.to_datetime(df_sorted[date_field])
        
        # 计算时间间隔
        time_diffs = dates.diff().dropna()
        
        # 检查是否有异常跳跃
        mode_diff = time_diffs.mode()[0]
        consistent_count = (time_diffs == mode_diff).sum()
        
        return consistent_count / len(time_diffs) * 100
    
    @staticmethod
    def calculate_cross_field_consistency(df: pd.DataFrame) -> float:
        """计算跨字段一致性"""
        # 检查OHLC关系
        consistency_checks = [
            df['high'] >= df['low'],
            df['high'] >= df['open'],
            df['high'] >= df['close'],
            df['low'] <= df['open'],
            df['low'] <= df['close']
        ]
        
        # 所有检查都通过
        all_consistent = np.all(consistency_checks, axis=0)
        
        return all_consistent.sum() / len(df) * 100
```

### 4.2 一致性标准

| 检查类型 | 一致性要求 | 说明 |
|----------|-----------|------|
| **格式一致性** | ≥99% | 数据格式统一 |
| **时间一致性** | ≥95% | 时间序列连续 |
| **字段一致性** | ≥98% | 字段间逻辑正确 |

---

## 5. 时效性指标（Timeliness）

### 5.1 指标定义

```python
from datetime import datetime, timedelta

@dataclass
class TimelinessMetrics:
    """时效性指标"""
    
    @staticmethod
    def calculate_update_delay(df: pd.DataFrame, date_field: str, expected_frequency: str) -> float:
        """计算更新延迟"""
        # 获取最新数据日期
        latest_date = pd.to_datetime(df[date_field]).max()
        
        # 计算预期更新日期
        today = datetime.now()
        if expected_frequency == "daily":
            expected_date = today - timedelta(days=1)
        elif expected_frequency == "weekly":
            expected_date = today - timedelta(weeks=1)
        elif expected_frequency == "monthly":
            expected_date = today - timedelta(days=30)
        else:
            expected_date = today
        
        # 计算延迟天数
        delay_days = (expected_date - latest_date).days
        
        return delay_days
    
    @staticmethod
    def calculate_timeliness_score(df: pd.DataFrame, date_field: str, expected_frequency: str) -> float:
        """计算时效性评分"""
        delay_days = TimelinessMetrics.calculate_update_delay(df, date_field, expected_frequency)
        
        # 根据延迟天数计算评分
        if delay_days <= 1:
            return 100.0
        elif delay_days <= 3:
            return 90.0
        elif delay_days <= 7:
            return 80.0
        elif delay_days <= 14:
            return 70.0
        else:
            return max(60.0 - (delay_days - 14) * 2, 0)
```

### 5.2 时效性标准

| 数据类型 | 更新频率 | 时效性要求 |
|----------|----------|-----------|
| **行情数据** | 每日 | 延迟≤1天 |
| **财务数据** | 每季度 | 延迟≤7天 |
| **因子数据** | 每日 | 延迟≤1天 |
| **宏观数据** | 每月 | 延迟≤3天 |

---

## 6. 有效性指标（Validity）

### 6.1 指标定义

```python
@dataclass
class ValidityMetrics:
    """有效性指标"""
    
    @staticmethod
    def calculate_range_validity(df: pd.DataFrame, field: str, min_val: float, max_val: float) -> float:
        """计算范围有效性"""
        valid_count = ((df[field] >= min_val) & (df[field] <= max_val)).sum()
        return valid_count / len(df) * 100
    
    @staticmethod
    def calculate_business_rule_validity(df: pd.DataFrame) -> float:
        """计算业务规则有效性"""
        # 检查业务规则
        valid_checks = [
            df['volume'] >= 0,  # 成交量非负
            df['amount'] >= 0,  # 成交额非负
            df['turnover_rate'] >= 0,  # 换手率非负
            df['turnover_rate'] <= 100,  # 换手率≤100%
        ]
        
        # 所有检查都通过
        all_valid = np.all(valid_checks, axis=0)
        
        return all_valid.sum() / len(df) * 100
```

### 6.2 有效性标准

| 检查类型 | 有效性要求 | 说明 |
|----------|-----------|------|
| **范围有效性** | ≥98% | 数据在合理范围内 |
| **业务规则有效性** | ≥99% | 符合业务规则 |

---

## 7. 唯一性指标（Uniqueness）

### 7.1 指标定义

```python
@dataclass
class UniquenessMetrics:
    """唯一性指标"""
    
    @staticmethod
    def calculate_duplicate_ratio(df: pd.DataFrame, key_fields: List[str]) -> float:
        """计算重复率"""
        total_records = len(df)
        unique_records = df[key_fields].drop_duplicates().shape[0]
        duplicate_ratio = (total_records - unique_records) / total_records
        
        return duplicate_ratio * 100
    
    @staticmethod
    def calculate_uniqueness_score(df: pd.DataFrame, key_fields: List[str]) -> float:
        """计算唯一性评分"""
        duplicate_ratio = UniquenessMetrics.calculate_duplicate_ratio(df, key_fields)
        return 100 - duplicate_ratio
```

### 7.2 唯一性标准

| 数据类型 | 唯一性要求 | 说明 |
|----------|-----------|------|
| **行情数据** | ≥99.9% | 几乎无重复 |
| **财务数据** | ≥99% | 极少重复 |
| **因子数据** | ≥99.5% | 极少重复 |

---

## 8. 综合质量评分

### 8.1 评分计算

```python
@dataclass
class QualityScore:
    """综合质量评分"""
    
    @staticmethod
    def calculate_overall_score(
        completeness: float,
        accuracy: float,
        consistency: float,
        timeliness: float,
        validity: float,
        uniqueness: float
    ) -> float:
        """计算综合质量评分"""
        # 权重配置
        weights = {
            'completeness': 0.25,
            'accuracy': 0.25,
            'consistency': 0.15,
            'timeliness': 0.15,
            'validity': 0.10,
            'uniqueness': 0.10
        }
        
        # 加权计算
        score = (
            completeness * weights['completeness'] +
            accuracy * weights['accuracy'] +
            consistency * weights['consistency'] +
            timeliness * weights['timeliness'] +
            validity * weights['validity'] +
            uniqueness * weights['uniqueness']
        )
        
        return score
    
    @staticmethod
    def get_quality_level(score: float) -> str:
        """获取质量等级"""
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "一般"
        elif score >= 60:
            return "较差"
        else:
            return "不可用"
```

### 8.2 质量报告

```python
def generate_quality_report(df: pd.DataFrame, data_type: str) -> Dict:
    """生成质量报告"""
    report = {
        'data_type': data_type,
        'total_records': len(df),
        'metrics': {
            'completeness': CompletenessMetrics.calculate_overall_completeness(df, ['open', 'high', 'low', 'close', 'volume']),
            'accuracy': AccuracyMetrics.calculate_price_accuracy(df),
            'consistency': ConsistencyMetrics.calculate_cross_field_consistency(df),
            'timeliness': TimelinessMetrics.calculate_timeliness_score(df, 'date', 'daily'),
            'validity': ValidityMetrics.calculate_business_rule_validity(df),
            'uniqueness': UniquenessMetrics.calculate_uniqueness_score(df, ['date', 'code'])
        },
        'overall_score': None,
        'quality_level': None
    }
    
    # 计算综合评分
    report['overall_score'] = QualityScore.calculate_overall_score(**report['metrics'])
    report['quality_level'] = QualityScore.get_quality_level(report['overall_score'])
    
    return report
```

---

## 9. 质量监控

### 9.1 监控指标

```yaml
# 质量监控配置
monitoring:
  # 监控频率
  frequency: "daily"
  
  # 告警阈值
  thresholds:
    completeness: 90
    accuracy: 95
    consistency: 95
    timeliness: 80
    validity: 95
    uniqueness: 99
    overall: 85
  
  # 告警方式
  alert_methods:
    - email
    - slack
    - dashboard
```

### 9.2 质量趋势分析

```python
def analyze_quality_trend(quality_history: List[Dict]) -> Dict:
    """分析质量趋势"""
    import pandas as pd
    
    # 转换为DataFrame
    df = pd.DataFrame(quality_history)
    
    # 计算趋势
    trend = {
        'completeness_trend': df['completeness'].pct_change().mean(),
        'accuracy_trend': df['accuracy'].pct_change().mean(),
        'overall_trend': df['overall_score'].pct_change().mean()
    }
    
    # 判断趋势方向
    if trend['overall_trend'] > 0.01:
        trend['direction'] = "上升"
    elif trend['overall_trend'] < -0.01:
        trend['direction'] = "下降"
    else:
        trend['direction'] = "稳定"
    
    return trend
```

---

## 10. 相关文档

- [数据质量控制系统](DATA_QUALITY_CONTROL_SYSTEM.md) - 质量控制实现
- [数据清洗规则配置](../03_CLEANING/CLEANING_RULES.md) - 清洗规则定义
- [数据采集系统](../DATA_ACQUISITION.md) - 数据采集方案

---

**文档版本**: v1.0.0 | **创建日期**: 2026-04-04 | **维护者**: 首席文档架构师

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
