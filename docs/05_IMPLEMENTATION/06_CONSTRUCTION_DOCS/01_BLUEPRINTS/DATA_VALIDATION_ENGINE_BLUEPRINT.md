---
module_id: DATA_VALIDATION_ENGINE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®å±?
compliance_level: ä¸ä¸æ å
responsibility:
  - æ°æ®éªè¯å¼æ
  - æ°æ®éªè¯
  - ä¸å¡è§åæ£æ?
  - æ°æ®å®æ´æ§æ£æ?
layer: Layer 5.1 (数据处理)
---

# æ°æ®éªè¯å¼æèå¾

## 核心定位

负责数据验证引擎的设计与实现，基于验证规则，检查数据有效性，确保数据质量。


## æ ¸å¿å®ä½

è´è´£æ°æ®éªè¯å¼æçå®ç°ï¼æä¾æ°æ®å®æ´æ§ãä¸è´æ§ååç¡®æ§éªè¯åè½ï¼ç¡®ä¿æ°æ®è´¨éã?

## ð æ§è¡æè¦

æ¬èå¾è®¾è®¡åºäºGreat ExpectationsåPanderaçæ°æ®éªè¯å¼æï¼æä¾ä¸ä¸çº§æ°æ®éªè¯è½åï¼éåä¸ªäººå¼ååAIç»´æ¤ã?

**æ ¸å¿ä»·å?*:
- ä¸å¡è§åèªå¨éªè¯
- æ°æ®å®æ´æ§æ£æ?
- è·¨æºæ°æ®ä¸è´æ§éªè¯?
- éªè¯æ¥åçæ
- æ°æ®è´¨éè¯å

**å¼æºæ¹æ¡?*: Great Expectations + Pandera + Voluptuous

**é¢ä¼°å·¥ä½é?*: 50å°æ¶

---

## 1. æ¨¡åå®ä½ä¸ç®æ ?

### 1.1 æ¨¡åå®ä½

**Layerå®ä½**: Layer 1 - æ°æ®é¢å¤çå±ï¼æ°æ®æ²»çæ¨¡åï¼

**æ ¸å¿ä»·å?*:
- ç¡®ä¿æ°æ®ç¬¦åä¸å¡è§å
- é²æ­¢èæ°æ®è¿å¥ç³»ç»?
- æä¾æ°æ®è´¨éåº¦é
- èªå¨åéªè¯æµç¨?

**ä¸å¡ä»·å?*:
- éä½æ°æ®é£é©
- æé«æ°æ®å¯ä¿¡åº?
- åå°äººå·¥å®¡æ ¸
- æåç³»ç»ç¨³å®æ?

### 1.2 è®¾è®¡ç®æ 

| ç®æ  | ä¼åçº?| ææ¯å®ç?|
|------|--------|----------|
| **ä¸å¡è§åéªè¯** | P0 | Great Expectations |
| **æ°æ®å®æ´æ§æ£æ?* | P0 | Pandera Schema |
| **è·¨æºä¸è´æ§éªè¯?* | P0 | èªå®ä¹éªè¯å¨ |
| **éªè¯æ¥åçæ** | P1 | Great Expectations Docs |
| **æ°æ®è´¨éè¯å** | P1 | èªå®ä¹è¯åå¼æ?|

---

## 2. ç³»ç»æ¶æè®¾è®¡

### 2.1 æ¶ææ¦è§

```mermaid
graph TB
    subgraph "è¾å¥å±?
        A[å¾éªè¯æ°æ®] --> B[éªè¯æ¥å¥æ¥å£]
    end
    
    subgraph "éªè¯å¼æ"
        B --> C[ä¸å¡è§åéªè¯å¨]
        B --> D[å®æ´æ§éªè¯å¨]
        B --> E[ä¸è´æ§éªè¯å¨]
        B --> F[ç»è®¡éªè¯å¨]
        
        C --> G[éªè¯è§åå¼æ]
        D --> G
        E --> G
        F --> G
    end
    
    subgraph "è¾åºå±?
        G --> H[éªè¯ç»æ]
        G --> I[éªè¯æ¥å]
        G --> J[è´¨éè¯å]
    end
    
    subgraph "éç½®ç®¡ç"
        K[éªè¯è§åéç½®] --> G
        L[ææéç½®] --> G
    end
```

### 2.2 æ ¸å¿ç»ä»¶

#### 2.2.1 ä¸å¡è§åéªè¯å?

**èè´£**: éªè¯æ°æ®æ¯å¦ç¬¦åä¸å¡è§å

**ææ¯æ **: Great Expectations

**æ ¸å¿åè½**:
- ä»·æ ¼èå´éªè¯
- æäº¤éåçæ§éªè¯?
- æ¶é´åºåè¿ç»­æ§éªè¯?
- å¸åºç¶æéªè¯?

#### 2.2.2 å®æ´æ§éªè¯å¨

**èè´£**: éªè¯æ°æ®å®æ´æ?

**ææ¯æ **: Pandera

**æ ¸å¿åè½**:
- å¿å¡«å­æ®µæ£æ?
- æ°æ®ç±»åéªè¯
- å¯ä¸æ§çº¦æéªè¯?
- å¤é®çº¦æéªè¯

#### 2.2.3 ä¸è´æ§éªè¯å¨

**èè´£**: éªè¯è·¨æºæ°æ®ä¸è´æ?

**ææ¯æ **: èªå®ä¹éªè¯å¨

**æ ¸å¿åè½**:
- è·¨æ°æ®æºå¯¹æ¯
- æ¶é´æ³å¯¹é½éªè¯?
- ä»·æ ¼ä¸è´æ§éªè¯?
- æäº¤éä¸è´æ§éªè¯?

#### 2.2.4 ç»è®¡éªè¯å?

**èè´£**: éªè¯æ°æ®ç»è®¡ç¹æ?

**ææ¯æ **: Great Expectations

**æ ¸å¿åè½**:
- åå¸éªè¯
- ç»è®¡ææ éªè¯
- å¼å¸¸åå¸æ£æµ?
- è¶å¿éªè¯

---

## 3. å¼æºæ¹æ¡éæ?

### 3.1 Great Expectationséæ

**GitHub**: https://github.com/great-expectations/great_expectations

**Staræ?*: 9.8k+

**æ ¸å¿ç¹æ?*:
- ä¸°å¯çåç½®ææç±»å?
- èªå¨åæ°æ®ææ¡£çæ?
- éªè¯ç»æå¯è§å?
- æ¯æå¤ç§æ°æ®æº?

**éææ¹å¼**:

```python
import great_expectations as gx
from great_expectations.dataset import SparkDataset

class BusinessRuleValidator:
    """ä¸å¡è§åéªè¯å?""
    
    def __init__(self, spark, config):
        self.spark = spark
        self.config = config
        self.context = gx.get_context()
    
    def validate_price_range(self, df, symbol, price_column='close'):
        """
        éªè¯ä»·æ ¼èå´
        
        Args:
            df: Spark DataFrame
            symbol: è¡ç¥¨ä»£ç 
            price_column: ä»·æ ¼åå
        
        Returns:
            ValidationResult: éªè¯ç»æ
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
        éªè¯æäº¤éåçæ?
        
        Args:
            df: Spark DataFrame
            volume_column: æäº¤éåå?
        
        Returns:
            ValidationResult: éªè¯ç»æ
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
        éªè¯æ¶é´åºåè¿ç»­æ?
        
        Args:
            df: Spark DataFrame
            time_column: æ¶é´åå
            freq: é¢æé¢ç
        
        Returns:
            ValidationResult: éªè¯ç»æ
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

### 3.2 Panderaéæ

**GitHub**: https://github.com/unionai-oss/pandera

**Staræ?*: 3.2k+

**æ ¸å¿ç¹æ?*:
- Schemaå®ä¹ä¸éªè¯?
- æ°æ®ç±»åå¼ºå¶è½¬æ¢
- ç»è®¡éªè¯
- æ¯æSpark DataFrame

**éææ¹å¼**:

```python
import pandera as pa
from pandera import Column, DataFrameSchema, Check
from pandera.typing import SparkDataFrame

class IntegrityValidator:
    """å®æ´æ§éªè¯å¨"""
    
    def __init__(self, spark, config):
        self.spark = spark
        self.config = config
        self.schemas = self._load_schemas()
    
    def _load_schemas(self):
        """å è½½Schemaå®ä¹"""
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
        éªè¯Schema
        
        Args:
            df: Spark DataFrame
            schema_name: Schemaåç§°
        
        Returns:
            ValidationResult: éªè¯ç»æ
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
        éªè¯æ°æ®å®æ´æ?
        
        Args:
            df: Spark DataFrame
            required_columns: å¿å¡«ååè¡?
        
        Returns:
            ValidationResult: éªè¯ç»æ
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
        éªè¯å¯ä¸æ§çº¦æ?
        
        Args:
            df: Spark DataFrame
            unique_columns: å¯ä¸æ§çº¦æååè¡¨
        
        Returns:
            ValidationResult: éªè¯ç»æ
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

### 3.3 ä¸è´æ§éªè¯å¨

**ææ¯æ **: èªå®ä¹å®ç?

**æ ¸å¿åè½**:
- è·¨æ°æ®æºå¯¹æ¯
- æ¶é´æ³å¯¹é½?
- ä»·æ ¼ä¸è´æ§éªè¯?

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, abs as spark_abs

class ConsistencyValidator:
    """ä¸è´æ§éªè¯å¨"""
    
    def __init__(self, spark: SparkSession, config):
        self.spark = spark
        self.config = config
        self.tolerance = config.get('tolerance', 0.01)
    
    def validate_cross_source(self, df1, df2, key_columns, value_columns):
        """
        è·¨æ°æ®æºéªè¯
        
        Args:
            df1: ç¬¬ä¸ä¸ªæ°æ®æº
            df2: ç¬¬äºä¸ªæ°æ®æº
            key_columns: é®å
            value_columns: å¼å
        
        Returns:
            ValidationResult: éªè¯ç»æ
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
        éªè¯æ¶é´æ³å¯¹é½?
        
        Args:
            df1: ç¬¬ä¸ä¸ªæ°æ®æº
            df2: ç¬¬äºä¸ªæ°æ®æº
            timestamp_column: æ¶é´æ³åå?
        
        Returns:
            ValidationResult: éªè¯ç»æ
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

## 4. éªè¯è§åéç½®

### 4.1 ä¸å¡è§åéç½®

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

### 4.2 å®æ´æ§è§åéç½?

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

### 4.3 ä¸è´æ§è§åéç½?

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

## 5. éªè¯æ¥åçæ

### 5.1 æ¥åæ¨¡æ¿

```python
from datetime import datetime
from typing import Dict, List, Any

class ValidationReportGenerator:
    """éªè¯æ¥åçæå?""
    
    def __init__(self, config):
        self.config = config
    
    def generate_report(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        çæéªè¯æ¥å
        
        Args:
            validation_results: éªè¯ç»æ
        
        Returns:
            Dict: éªè¯æ¥å
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
        """çææè¦"""
        total_checks = len(validation_results)
        passed_checks = sum(1 for r in validation_results.values() if r.get('success', False))
        
        return {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'pass_rate': passed_checks / total_checks if total_checks > 0 else 0
        }
    
    def _calculate_quality_score(self, validation_results):
        """è®¡ç®æ°æ®è´¨éè¯å"""
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
        """çææ¹è¿å»ºè®®"""
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
        """è·åæ¹è¿å»ºè®®"""
        recommendations_map = {
            'business_rules': {
                'price_range': 'æ£æ¥æ°æ®æºä»·æ ¼èå´éç½®',
                'volume_range': 'éªè¯æäº¤éæ°æ®æºå¯é æ?,
                'time_continuity': 'æ£æ¥æ°æ®ééé¢çéç½?
            },
            'completeness': {
                'null_values': 'æ£æ¥æ°æ®æºå®æ´æ?,
                'unique_constraint': 'æ£æ¥æ°æ®å»éé»è¾'
            },
            'consistency': {
                'cross_source': 'æ£æ¥æ°æ®æºåæ­¥æºå¶',
                'timestamp_alignment': 'æ£æ¥æ¶é´æ³å¯¹é½é»è¾'
            }
        }
        
        return recommendations_map.get(category, {}).get(
            error.get('type', ''),
            'æ£æ¥æ°æ®æºåå¤çé»è¾'
        )
```

---

## 6. æ°æ®è´¨éè¯å

### 6.1 è¯åç»´åº¦

| ç»´åº¦ | æé | è¯åæ å |
|------|------|----------|
| **ä¸å¡è§åç¬¦ååº?* | 40% | ä¸å¡è§åéªè¯éè¿ç?|
| **æ°æ®å®æ´æ?* | 30% | å¿å¡«å­æ®µå®æ´ç?|
| **æ°æ®ä¸è´æ?* | 20% | è·¨æºä¸è´æ§æ¯ç?|
| **ç»è®¡ç¹æ?* | 10% | ç»è®¡éªè¯éè¿ç?|

### 6.2 è¯åè®¡ç®

```python
class DataQualityScorer:
    """æ°æ®è´¨éè¯åå?""
    
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
        è®¡ç®æ°æ®è´¨éè¯å
        
        Args:
            validation_results: éªè¯ç»æ
        
        Returns:
            Dict: è¯åç»æ
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
        """è®¡ç®ç»´åº¦è¯å"""
        if result.get('success', False):
            return 100.0
        
        error_count = len(result.get('errors', []))
        warning_count = len(result.get('warnings', []))
        
        score = 100 - (error_count * 10 + warning_count * 5)
        return max(0, score)
    
    def _get_grade(self, score):
        """è·åç­çº§"""
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

## 7. å®æ½è®¡å

### 7.1 é¶æ®µä¸ï¼æ ¸å¿éªè¯åè½ï¼20å°æ¶ï¼?

**ç®æ **: å®ç°åºç¡éªè¯è½å

**ä»»å¡**:
- [ ] éæGreat Expectationsï¼?å°æ¶ï¼?
- [ ] å®ç°ä¸å¡è§åéªè¯å¨ï¼6å°æ¶ï¼?
- [ ] å®ç°å®æ´æ§éªè¯å¨ï¼?å°æ¶ï¼?
- [ ] ç¼åéªè¯è§åéç½®ï¼?å°æ¶ï¼?

**äº¤ä»ç?*:
- ä¸å¡è§åéªè¯å?
- å®æ´æ§éªè¯å¨
- éªè¯è§åéç½®æä»¶

### 7.2 é¶æ®µäºï¼é«çº§éªè¯åè½ï¼?5å°æ¶ï¼?

**ç®æ **: å®ç°é«çº§éªè¯è½å

**ä»»å¡**:
- [ ] å®ç°ä¸è´æ§éªè¯å¨ï¼?å°æ¶ï¼?
- [ ] å®ç°ç»è®¡éªè¯å¨ï¼5å°æ¶ï¼?
- [ ] éæPanderaï¼?å°æ¶ï¼?

**äº¤ä»ç?*:
- ä¸è´æ§éªè¯å¨
- ç»è®¡éªè¯å?
- Panderaéæ

### 7.3 é¶æ®µä¸ï¼æ¥åä¸è¯åï¼15å°æ¶ï¼?

**ç®æ **: å®åéªè¯æ¥å

**ä»»å¡**:
- [ ] å®ç°éªè¯æ¥åçæå¨ï¼6å°æ¶ï¼?
- [ ] å®ç°æ°æ®è´¨éè¯åå¨ï¼5å°æ¶ï¼?
- [ ] çæéªè¯ææ¡£ï¼?å°æ¶ï¼?

**äº¤ä»ç?*:
- éªè¯æ¥åçæå?
- æ°æ®è´¨éè¯åå?
- éªè¯ææ¡£

---

## 8. çæ§ä¸è¿ç»?

### 8.1 å³é®ææ 

| ææ  | ç®æ å?| çæ§æ¹å¼ |
|------|--------|----------|
| **éªè¯éè¿ç?* | â?5% | Great Expectations |
| **éªè¯å»¶è¿** | â?ç§?| Prometheus |
| **æ°æ®è´¨éè¯å** | â?5å?| èªå®ä¹è¯åå¨ |
| **éªè¯è¦çç?* | 100% | éç½®æ£æ?|

### 8.2 åè­¦è§å

```yaml
alerts:
  - name: validation_failure_rate_high
    condition: validation_failure_rate > 0.05
    severity: critical
    message: "éªè¯å¤±è´¥çè¶è¿?%"
  
  - name: data_quality_score_low
    condition: data_quality_score < 70
    severity: warning
    message: "æ°æ®è´¨éè¯åä½äº70å?
  
  - name: validation_latency_high
    condition: validation_latency > 10
    severity: warning
    message: "éªè¯å»¶è¿è¶è¿10ç§?
```

---

## 9. ææ¬æçåæ

### 9.1 å¼åææ?

| é¡¹ç® | å·¥ä½é?| ææ¬ |
|------|--------|------|
| **æ ¸å¿éªè¯åè½** | 20å°æ¶ | Â¥2,000 |
| **é«çº§éªè¯åè½** | 15å°æ¶ | Â¥1,500 |
| **æ¥åä¸è¯å?* | 15å°æ¶ | Â¥1,500 |
| **æ»è®¡** | **50å°æ¶** | **Â¥5,000** |

### 9.2 æ¶çè¯ä¼°

| æ¶çé¡?| å¹´åä»·å?|
|--------|----------|
| **åå°æ°æ®é®é¢æå¤±** | Â¥50,000 |
| **éä½äººå·¥å®¡æ ¸ææ¬** | Â¥20,000 |
| **æé«æ°æ®å¯ä¿¡åº?* | Â¥30,000 |
| **æ»è®¡** | **Â¥100,000** |

**ROI**: (100,000 - 5,000) / 5,000 = 1900%

---

## 10. é£é©ä¸ç¼è§?

### 10.1 ææ¯é£é?

| é£é© | å½±å | ç¼è§£æªæ½ |
|------|------|----------|
| **éªè¯è§åéç½®éè¯¯** | é«?| éç½®éªè¯ + æµè¯ç¯å¢ |
| **éªè¯æ§è½ç¶é¢** | ä¸?| å¹¶è¡éªè¯ + ç¼å­ |
| **å¼æºçæ¬å¼å®¹æ?* | ä½?| çæ¬éå® + æµè¯ |

### 10.2 ä¸å¡é£é©

| é£é© | å½±å | ç¼è§£æªæ½ |
|------|------|----------|
| **éªè¯è§åè¿ä¸¥** | ä¸?| è§åå¯éç½?+ ç°åº¦åå¸ |
| **è¯¯æ¥çé«** | ä¸?| éå¼è°ä¼?+ ç½åå?|
| **éªè¯å»¶è¿å½±åä¸å¡** | ä½?| å¼æ­¥éªè¯ + ä¼åçº§éå?|

---

## 11. åç»­ä¼åæ¹å

### 11.1 ç­æä¼åï¼?-3ä¸ªæï¼?

- [ ] å¢å æ´å¤ä¸å¡è§åæ¨¡æ¿
- [ ] ä¼åéªè¯æ§è½
- [ ] å®åéªè¯æ¥å

### 11.2 ä¸­æä¼åï¼?-6ä¸ªæï¼?

- [ ] æºå¨å­¦ä¹ è¾å©éªè¯
- [ ] èªå¨è§åçæ
- [ ] éªè¯è§åæ¨è

### 11.3 é¿æä¼åï¼?-12ä¸ªæï¼?

- [ ] æ°æ®è´¨éé¢æµ
- [ ] æºè½å¼å¸¸æ£æµ?
- [ ] èªéåºéªè¯

---

## 12. åèèµæ?

### 12.1 å¼æºé¡¹ç?

- [Great Expectations](https://github.com/great-expectations/great_expectations)
- [Pandera](https://github.com/unionai-oss/pandera)
- [Voluptuous](https://github.com/alecthomas/voluptuous)

### 12.2 ææ¯ææ¡?

- [Great Expectationså®æ¹ææ¡£](https://docs.greatexpectations.io/)
- [Panderaå®æ¹ææ¡£](https://pandera.readthedocs.io/)
- [Spark DataFrameéªè¯æä½³å®è·µ](https://spark.apache.org/docs/latest/)

---

**ææ¡£çæ¬**: v1.0.0
**æåæ´æ?*: 2026-04-07
**ç»´æ¤è?*: ä¸ªäººå¼åè?
**å®¡æ ¸ç¶æ?*: å¾å®¡æ ?
