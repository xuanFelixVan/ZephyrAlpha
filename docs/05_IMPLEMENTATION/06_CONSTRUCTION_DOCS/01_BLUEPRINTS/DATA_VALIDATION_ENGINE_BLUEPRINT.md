---
module_id: DATA_VALIDATION_ENGINE_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 实施指南、部署文档
  - 数据验证
  - 业务规则检查
layer: "Layer 1 (数据预处理层)"
---

# 数据验证引擎蓝图

> **核心职责**: 业务规则验证、数据完整性检查、数据一致性验证
> **职责边界**: 
> - ✅ 本文档负责：数据验证、业务规则检查、完整性验证
> - ❌ 本文档不负责：数据清洗（由清洗引擎负责）

## 📋 执行摘要

本蓝图设计基于Great Expectations和Pandera的数据验证引擎，提供专业级数据验证能力，适合个人开发和AI维护。

**核心价值**:
- 业务规则自动验证
- 数据完整性检查
- 跨源数据一致性验证
- 验证报告生成
- 数据质量评分

**开源方案**: Great Expectations + Pandera + Voluptuous

**预估工作量**: 50小时

---

## 1. 模块定位与目标

### 1.1 模块定位

**Layer定位**: Layer 1 - 数据预处理层（数据治理模块）

**核心价值**:
- 确保数据符合业务规则
- 防止脏数据进入系统
- 提供数据质量度量
- 自动化验证流程

**业务价值**:
- 降低数据风险
- 提高数据可信度
- 减少人工审核
- 提升系统稳定性

### 1.2 设计目标

| 目标 | 优先级 | 技术实现 |
|------|--------|----------|
| **业务规则验证** | P0 | Great Expectations |
| **数据完整性检查** | P0 | Pandera Schema |
| **跨源一致性验证** | P0 | 自定义验证器 |
| **验证报告生成** | P1 | Great Expectations Docs |
| **数据质量评分** | P1 | 自定义评分引擎 |

---

## 2. 系统架构设计

### 2.1 架构概览

```mermaid
graph TB
    subgraph "输入层"
        A[待验证数据] --> B[验证接入接口]
    end
    
    subgraph "验证引擎"
        B --> C[业务规则验证器]
        B --> D[完整性验证器]
        B --> E[一致性验证器]
        B --> F[统计验证器]
        
        C --> G[验证规则引擎]
        D --> G
        E --> G
        F --> G
    end
    
    subgraph "输出层"
        G --> H[验证结果]
        G --> I[验证报告]
        G --> J[质量评分]
    end
    
    subgraph "配置管理"
        K[验证规则配置] --> G
        L[期望配置] --> G
    end
```

### 2.2 核心组件

#### 2.2.1 业务规则验证器

**职责**: 验证数据是否符合业务规则

**技术栈**: Great Expectations

**核心功能**:
- 价格范围验证
- 成交量合理性验证
- 时间序列连续性验证
- 市场状态验证

#### 2.2.2 完整性验证器

**职责**: 验证数据完整性

**技术栈**: Pandera

**核心功能**:
- 必填字段检查
- 数据类型验证
- 唯一性约束验证
- 外键约束验证

#### 2.2.3 一致性验证器

**职责**: 验证跨源数据一致性

**技术栈**: 自定义验证器

**核心功能**:
- 跨数据源对比
- 时间戳对齐验证
- 价格一致性验证
- 成交量一致性验证

#### 2.2.4 统计验证器

**职责**: 验证数据统计特性

**技术栈**: Great Expectations

**核心功能**:
- 分布验证
- 统计指标验证
- 异常分布检测
- 趋势验证

---

## 3. 开源方案集成

### 3.1 Great Expectations集成

**GitHub**: https://github.com/great-expectations/great_expectations

**Star数**: 9.8k+

**核心特性**:
- 丰富的内置期望类型
- 自动化数据文档生成
- 验证结果可视化
- 支持多种数据源

**集成方式**:

```python
import great_expectations as gx
from great_expectations.dataset import SparkDataset

class BusinessRuleValidator:
    """业务规则验证器"""
    
    def __init__(self, spark, config):
        self.spark = spark
        self.config = config
        self.context = gx.get_context()
    
    def validate_price_range(self, df, symbol, price_column='close'):
        """
        验证价格范围
        
        Args:
            df: Spark DataFrame
            symbol: 股票代码
            price_column: 价格列名
        
        Returns:
            ValidationResult: 验证结果
        """
        expectations = self.config.get('price_ranges', {}).get(symbol, {})
        
        if not expectations:
            return self._create_warning_result(f"No price range config for {symbol}")
        
        min_price = expectations.get('min', 0)
        max_price = expectations.get('max', float('inf'))
        
        expectation_suite = self.context.add_expectation_suite(
            f"price_range_{symbol}"
        )
        
        expectation_suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeBetween(
                column=price_column,
                min_value=min_price,
                max_value=max_price
            )
        )
        
        validator = self.context.get_validator(
            batch_request=self._create_batch_request(df),
            expectation_suite=expectation_suite
        )
        
        return validator.validate()
    
    def validate_volume(self, df, volume_column='volume'):
        """
        验证成交量合理性
        
        Args:
            df: Spark DataFrame
            volume_column: 成交量列名
        
        Returns:
            ValidationResult: 验证结果
        """
        expectation_suite = self.context.add_expectation_suite("volume_validation")
        
        expectation_suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeBetween(
                column=volume_column,
                min_value=0,
                max_value=1e12
            )
        )
        
        expectation_suite.add_expectation(
            gx.expectations.ExpectColumnValuesToNotBeNull(
                column=volume_column
            )
        )
        
        validator = self.context.get_validator(
            batch_request=self._create_batch_request(df),
            expectation_suite=expectation_suite
        )
        
        return validator.validate()
    
    def validate_time_continuity(self, df, time_column='timestamp', freq='1min'):
        """
        验证时间序列连续性
        
        Args:
            df: Spark DataFrame
            time_column: 时间列名
            freq: 预期频率
        
        Returns:
            ValidationResult: 验证结果
        """
        expectation_suite = self.context.add_expectation_suite("time_continuity")
        
        expectation_suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeUnique(
                column=time_column
            )
        )
        
        expectation_suite.add_expectation(
            gx.expectations.ExpectColumnValuesToNotBeNull(
                column=time_column
            )
        )
        
        validator = self.context.get_validator(
            batch_request=self._create_batch_request(df),
            expectation_suite=expectation_suite
        )
        
        return validator.validate()
```

### 3.2 Pandera集成

**GitHub**: https://github.com/unionai-oss/pandera

**Star数**: 3.2k+

**核心特性**:
- Schema定义与验证
- 数据类型强制转换
- 统计验证
- 支持Spark DataFrame

**集成方式**:

```python
import pandera as pa
from pandera import Column, DataFrameSchema, Check
from pandera.typing import SparkDataFrame

class IntegrityValidator:
    """完整性验证器"""
    
    def __init__(self, spark, config):
        self.spark = spark
        self.config = config
        self.schemas = self._load_schemas()
    
    def _load_schemas(self):
        """加载Schema定义"""
        return {
            'tick_data': DataFrameSchema({
                'symbol': Column(str, Check.str_length(min_value=1)),
                'timestamp': Column(pa.DateTime, nullable=False),
                'open': Column(float, Check.ge(0)),
                'high': Column(float, Check.ge(0)),
                'low': Column(float, Check.ge(0)),
                'close': Column(float, Check.ge(0)),
                'volume': Column(int, Check.ge(0)),
            }, strict=True),
            
            'order_book': DataFrameSchema({
                'symbol': Column(str, Check.str_length(min_value=1)),
                'timestamp': Column(pa.DateTime, nullable=False),
                'bid_price': Column(float, Check.ge(0)),
                'bid_volume': Column(int, Check.ge(0)),
                'ask_price': Column(float, Check.ge(0)),
                'ask_volume': Column(int, Check.ge(0)),
            }, strict=True),
            
            'trade_data': DataFrameSchema({
                'symbol': Column(str, Check.str_length(min_value=1)),
                'timestamp': Column(pa.DateTime, nullable=False),
                'price': Column(float, Check.ge(0)),
                'volume': Column(int, Check.ge(0)),
                'side': Column(str, Check.isin(['buy', 'sell'])),
            }, strict=True)
        }
    
    def validate_schema(self, df, schema_name):
        """
        验证Schema
        
        Args:
            df: Spark DataFrame
            schema_name: Schema名称
        
        Returns:
            ValidationResult: 验证结果
        """
        schema = self.schemas.get(schema_name)
        
        if not schema:
            raise ValueError(f"Unknown schema: {schema_name}")
        
        try:
            validated_df = schema.validate(df)
            return {
                'success': True,
                'errors': [],
                'warnings': []
            }
        except pa.errors.SchemaError as e:
            return {
                'success': False,
                'errors': e.failure_cases.to_dict('records'),
                'warnings': []
            }
    
    def validate_completeness(self, df, required_columns):
        """
        验证数据完整性
        
        Args:
            df: Spark DataFrame
            required_columns: 必填列列表
        
        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        
        for col in required_columns:
            null_count = df.filter(df[col].isNull()).count()
            if null_count > 0:
                errors.append({
                    'column': col,
                    'error': f"Found {null_count} null values",
                    'severity': 'error'
                })
        
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
    
    def validate_uniqueness(self, df, unique_columns):
        """
        验证唯一性约束
        
        Args:
            df: Spark DataFrame
            unique_columns: 唯一性约束列列表
        
        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        
        for cols in unique_columns:
            if isinstance(cols, str):
                cols = [cols]
            
            duplicate_count = df.groupBy(*cols).count().filter('count > 1').count()
            
            if duplicate_count > 0:
                errors.append({
                    'columns': cols,
                    'error': f"Found {duplicate_count} duplicate groups",
                    'severity': 'error'
                })
        
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
```

### 3.3 一致性验证器

**技术栈**: 自定义实现

**核心功能**:
- 跨数据源对比
- 时间戳对齐
- 价格一致性验证

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, abs as spark_abs

class ConsistencyValidator:
    """一致性验证器"""
    
    def __init__(self, spark: SparkSession, config):
        self.spark = spark
        self.config = config
        self.tolerance = config.get('tolerance', 0.01)
    
    def validate_cross_source(self, df1, df2, key_columns, value_columns):
        """
        跨数据源验证
        
        Args:
            df1: 第一个数据源
            df2: 第二个数据源
            key_columns: 键列
            value_columns: 值列
        
        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        
        joined_df = df1.alias('a').join(
            df2.alias('b'),
            on=key_columns,
            how='inner'
        )
        
        for value_col in value_columns:
            diff_col = f"{value_col}_diff"
            joined_df = joined_df.withColumn(
                diff_col,
                spark_abs(col(f"a.{value_col}") - col(f"b.{value_col}")) / col(f"a.{value_col}")
            )
            
            inconsistent_count = joined_df.filter(col(diff_col) > self.tolerance).count()
            
            if inconsistent_count > 0:
                errors.append({
                    'column': value_col,
                    'error': f"Found {inconsistent_count} inconsistent records",
                    'tolerance': self.tolerance,
                    'severity': 'warning'
                })
        
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
    
    def validate_timestamp_alignment(self, df1, df2, timestamp_column='timestamp'):
        """
        验证时间戳对齐
        
        Args:
            df1: 第一个数据源
            df2: 第二个数据源
            timestamp_column: 时间戳列名
        
        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        
        timestamps1 = df1.select(timestamp_column).distinct().collect()
        timestamps2 = df2.select(timestamp_column).distinct().collect()
        
        set1 = set([row[timestamp_column] for row in timestamps1])
        set2 = set([row[timestamp_column] for row in timestamps2])
        
        missing_in_1 = set2 - set1
        missing_in_2 = set1 - set2
        
        if missing_in_1:
            errors.append({
                'source': 'df1',
                'error': f"Missing {len(missing_in_1)} timestamps",
                'severity': 'warning'
            })
        
        if missing_in_2:
            errors.append({
                'source': 'df2',
                'error': f"Missing {len(missing_in_2)} timestamps",
                'severity': 'warning'
            })
        
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
```

---

## 4. 验证规则配置

### 4.1 业务规则配置

```yaml
validation_rules:
  price_range:
    AAPL:
      min: 100
      max: 300
    GOOGL:
      min: 100
      max: 200
    MSFT:
      min: 200
      max: 500
  
  volume_range:
    min: 0
    max: 1000000000
  
  time_continuity:
    allowed_gaps: 5
    gap_unit: minutes
  
  market_state:
    trading_hours:
      start: "09:30:00"
      end: "16:00:00"
    timezone: "America/New_York"
```

### 4.2 完整性规则配置

```yaml
completeness_rules:
  tick_data:
    required_columns:
      - symbol
      - timestamp
      - open
      - high
      - low
      - close
      - volume
    
    unique_constraints:
      - [symbol, timestamp]
    
    not_null_columns:
      - symbol
      - timestamp
      - close
      - volume
  
  order_book:
    required_columns:
      - symbol
      - timestamp
      - bid_price
      - bid_volume
      - ask_price
      - ask_volume
    
    unique_constraints:
      - [symbol, timestamp, level]
    
    not_null_columns:
      - symbol
      - timestamp
      - bid_price
      - ask_price
```

### 4.3 一致性规则配置

```yaml
consistency_rules:
  cross_source:
    sources:
      - name: primary
        type: database
      - name: backup
        type: database
    
    key_columns:
      - symbol
      - timestamp
    
    value_columns:
      - close
      - volume
    
    tolerance: 0.001
  
  timestamp_alignment:
    max_gap: 60
    gap_unit: seconds
```

---

## 5. 验证报告生成

### 5.1 报告模板

```python
from datetime import datetime
from typing import Dict, List, Any

class ValidationReportGenerator:
    """验证报告生成器"""
    
    def __init__(self, config):
        self.config = config
    
    def generate_report(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成验证报告
        
        Args:
            validation_results: 验证结果
        
        Returns:
            Dict: 验证报告
        """
        report = {
            'report_id': self._generate_report_id(),
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(validation_results),
            'details': validation_results,
            'quality_score': self._calculate_quality_score(validation_results),
            'recommendations': self._generate_recommendations(validation_results)
        }
        
        return report
    
    def _generate_summary(self, validation_results):
        """生成摘要"""
        total_checks = len(validation_results)
        passed_checks = sum(1 for r in validation_results.values() if r.get('success', False))
        
        return {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'pass_rate': passed_checks / total_checks if total_checks > 0 else 0
        }
    
    def _calculate_quality_score(self, validation_results):
        """计算数据质量评分"""
        weights = {
            'business_rules': 0.4,
            'completeness': 0.3,
            'consistency': 0.2,
            'statistics': 0.1
        }
        
        scores = {}
        for category, result in validation_results.items():
            if result.get('success', False):
                scores[category] = 100
            else:
                error_count = len(result.get('errors', []))
                scores[category] = max(0, 100 - error_count * 10)
        
        quality_score = sum(
            scores.get(cat, 0) * weight
            for cat, weight in weights.items()
        )
        
        return round(quality_score, 2)
    
    def _generate_recommendations(self, validation_results):
        """生成改进建议"""
        recommendations = []
        
        for category, result in validation_results.items():
            if not result.get('success', False):
                for error in result.get('errors', []):
                    recommendations.append({
                        'category': category,
                        'issue': error.get('error', 'Unknown error'),
                        'recommendation': self._get_recommendation(category, error)
                    })
        
        return recommendations
    
    def _get_recommendation(self, category, error):
        """获取改进建议"""
        recommendations_map = {
            'business_rules': {
                'price_range': '检查数据源价格范围配置',
                'volume_range': '验证成交量数据源可靠性',
                'time_continuity': '检查数据采集频率配置'
            },
            'completeness': {
                'null_values': '检查数据源完整性',
                'unique_constraint': '检查数据去重逻辑'
            },
            'consistency': {
                'cross_source': '检查数据源同步机制',
                'timestamp_alignment': '检查时间戳对齐逻辑'
            }
        }
        
        return recommendations_map.get(category, {}).get(
            error.get('type', ''),
            '检查数据源和处理逻辑'
        )
```

---

## 6. 数据质量评分

### 6.1 评分维度

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| **业务规则符合度** | 40% | 业务规则验证通过率 |
| **数据完整性** | 30% | 必填字段完整率 |
| **数据一致性** | 20% | 跨源一致性比率 |
| **统计特性** | 10% | 统计验证通过率 |

### 6.2 评分计算

```python
class DataQualityScorer:
    """数据质量评分器"""
    
    def __init__(self, config):
        self.config = config
        self.weights = {
            'business_rules': 0.4,
            'completeness': 0.3,
            'consistency': 0.2,
            'statistics': 0.1
        }
    
    def calculate_score(self, validation_results):
        """
        计算数据质量评分
        
        Args:
            validation_results: 验证结果
        
        Returns:
            Dict: 评分结果
        """
        dimension_scores = {}
        
        for dimension, weight in self.weights.items():
            result = validation_results.get(dimension, {})
            dimension_scores[dimension] = self._calculate_dimension_score(result)
        
        overall_score = sum(
            score * self.weights[dim]
            for dim, score in dimension_scores.items()
        )
        
        return {
            'overall_score': round(overall_score, 2),
            'dimension_scores': dimension_scores,
            'grade': self._get_grade(overall_score)
        }
    
    def _calculate_dimension_score(self, result):
        """计算维度评分"""
        if result.get('success', False):
            return 100.0
        
        error_count = len(result.get('errors', []))
        warning_count = len(result.get('warnings', []))
        
        score = 100 - (error_count * 10 + warning_count * 5)
        return max(0, score)
    
    def _get_grade(self, score):
        """获取等级"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
```

---

## 7. 实施计划

### 7.1 阶段一：核心验证功能（20小时）

**目标**: 实现基础验证能力

**任务**:
- [ ] 集成Great Expectations（4小时）
- [ ] 实现业务规则验证器（6小时）
- [ ] 实现完整性验证器（6小时）
- [ ] 编写验证规则配置（4小时）

**交付物**:
- 业务规则验证器
- 完整性验证器
- 验证规则配置文件

### 7.2 阶段二：高级验证功能（15小时）

**目标**: 实现高级验证能力

**任务**:
- [ ] 实现一致性验证器（6小时）
- [ ] 实现统计验证器（5小时）
- [ ] 集成Pandera（4小时）

**交付物**:
- 一致性验证器
- 统计验证器
- Pandera