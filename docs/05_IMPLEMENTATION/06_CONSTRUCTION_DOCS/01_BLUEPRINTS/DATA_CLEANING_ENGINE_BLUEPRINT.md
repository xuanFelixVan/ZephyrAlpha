---
module_id: DATA_CLEANING_ENGINE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®å±?
compliance_level: ä¸ä¸æ å
responsibility:
  - æ°æ®æ¸æ´å¼æ
  - æ°æ®æ¸æ´
  - å¼å¸¸å¼å¤ç?
  - ç¼ºå¤±å¼å¡«å?
layer: "Layer 1 (æ°æ®å±?"
---

# æ°æ®æ¸æ´å¼æèå¾

## 核心定位

负责数据清洗引擎的设计与实现，基于数据清洗技术，处理数据质量问题，提升数据可用性。



> **æ ¸å¿èè´£**: å¼å¸¸å¼æ£æµä¸å¤çãç¼ºå¤±å¼æºè½å¡«åãéå¤æ°æ®å»é?
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼æ°æ®æ¸æ´ãå¼å¸¸å¼å¤çãç¼ºå¤±å¼å¡«å?
> - â?æ¬ææ¡£ä¸è´è´£ï¼æ°æ®éªè¯ï¼ç±éªè¯å¼æè´è´£ï¼

## æ ¸å¿å®ä½

è´è´£æ°æ®æ¸æ´å¼æçå®ç°ï¼æä¾æ°æ®è´¨éæ£æµãæ°æ®æ¸æ´è§ååæ°æ®ä¿®å¤åè½ï¼ç¡®ä¿æ°æ®è´¨éã?

## ð æ§è¡æè¦

æ¬èå¾è®¾è®¡åºäºGreat ExpectationsåApache Sparkçæ°æ®æ¸æ´å¼æï¼æä¾ä¸ä¸çº§æ°æ®æ¸æ´è½åï¼éåä¸ªäººå¼ååAIç»´æ¤ã?

**æ ¸å¿ä»·å?*:
- èªå¨åå¼å¸¸å¼æ£æµä¸å¤ç
- æºè½ç¼ºå¤±å¼å¡«å?
- éå¤æ°æ®å»é
- æ°æ®æ ¼å¼æ åå?
- æ¸æ´è§åå¯éç½?

**å¼æºæ¹æ¡?*: Great Expectations + Apache Spark

**é¢ä¼°å·¥ä½é?*: 60å°æ¶

---

## 1. æ¨¡åå®ä½ä¸ç®æ ?

### 1.1 æ¨¡åå®ä½

**Layerå®ä½**: Layer 1 - æ°æ®é¢å¤çå±ï¼æ°æ®å¤çæ¨¡åï¼

**æ ¸å¿ä»·å?*:
- æåæ°æ®è´¨é
- åå°æ°æ®é®é¢å¯¼è´çäº¤ææå¤?
- èªå¨åæ°æ®æ¸æ´æµç¨?
- å¯éç½®çæ¸æ´è§å

**ä¸å¡ä»·å?*:
- åå°äººå·¥å¹²é¢
- æé«æ°æ®å¯ä¿¡åº?
- éä½æ°æ®é£é©
- æåç³»ç»ç¨³å®æ?

### 1.2 è®¾è®¡ç®æ 

| ç®æ  | ä¼åçº?| ææ¯å®ç?|
|------|--------|----------|
| **å¼å¸¸å¼æ£æµ?* | P0 | ç»è®¡æ¹æ³ + æºå¨å­¦ä¹  |
| **ç¼ºå¤±å¼å¡«å?* | P0 | æå?+ æºå¨å­¦ä¹ é¢æµ |
| **éå¤æ°æ®å»é** | P0 | åå¸ + ç¸ä¼¼åº¦å¹é?|
| **æ°æ®æ ¼å¼æ åå?* | P1 | è§åå¼æ |
| **æ¸æ´è§åå¯éç½?* | P1 | YAMLéç½® |

---

## 2. ç³»ç»æ¶æè®¾è®¡

### 2.1 æ¶ææ¦è§

```mermaid
graph TB
    subgraph "è¾å¥å±?
        A[åå§æ°æ®] --> B[æ°æ®æ¥å¥æ¥å£]
    end
    
    subgraph "æ¸æ´å¼æ"
        B --> C[å¼å¸¸å¼æ£æµå¨]
        B --> D[ç¼ºå¤±å¼å¤çå¨]
        B --> E[éå¤æ°æ®å»éå¨]
        B --> F[æ ¼å¼æ ååå¨]
        
        C --> G[æ¸æ´è§åå¼æ]
        D --> G
        E --> G
        F --> G
    end
    
    subgraph "è¾åºå±?
        G --> H[æ¸æ´åæ°æ®]
        G --> I[æ¸æ´æ¥å]
        G --> J[è´¨éææ ]
    end
    
    subgraph "éç½®ç®¡ç"
        K[æ¸æ´è§åéç½®] --> G
        L[éå¼éç½®] --> G
    end
```

### 2.2 æ ¸å¿ç»ä»¶è®¾è®¡

#### **2.2.1 å¼å¸¸å¼æ£æµå¨**

```python
from great_expectations.dataset import SparkDFDataset
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from typing import Dict, List, Any
import numpy as np

class AnomalyDetector:
    """å¼å¸¸å¼æ£æµå¨"""
    
    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        self.spark = spark
        self.config = config
        self.methods = {
            'zscore': self._zscore_detection,
            'iqr': self._iqr_detection,
            'isolation_forest': self._isolation_forest_detection,
            'dbscan': self._dbscan_detection
        }
    
    def detect_anomalies(self, df, columns: List[str], method: str = 'zscore'):
        """
        æ£æµå¼å¸¸å?
        
        Args:
            df: Spark DataFrame
            columns: éè¦æ£æµçå?
            method: æ£æµæ¹æ³?(zscore, iqr, isolation_forest, dbscan)
        
        Returns:
            DataFrame: åå«å¼å¸¸å¼æ è®°çDataFrame
        """
        detector = self.methods.get(method)
        if not detector:
            raise ValueError(f"ä¸æ¯æçæ£æµæ¹æ³? {method}")
        
        return detector(df, columns)
    
    def _zscore_detection(self, df, columns: List[str], threshold: float = 3.0):
        """Z-Scoreå¼å¸¸å¼æ£æµ?""
        for col_name in columns:
            stats = df.select(
                F.mean(col(col_name)).alias('mean'),
                F.stddev(col(col_name)).alias('std')
            ).collect()[0]
            
            mean_val = stats['mean']
            std_val = stats['std']
            
            if std_val and std_val > 0:
                df = df.withColumn(
                    f"{col_name}_is_anomaly",
                    when(
                        F.abs((col(col_name) - mean_val) / std_val) > threshold,
                        True
                    ).otherwise(False)
                )
        
        return df
    
    def _iqr_detection(self, df, columns: List[str], multiplier: float = 1.5):
        """IQRå¼å¸¸å¼æ£æµ?""
        for col_name in columns:
            quantiles = df.approxQuantile(col_name, [0.25, 0.75], 0.05)
            q1, q3 = quantiles[0], quantiles[1]
            iqr = q3 - q1
            
            lower_bound = q1 - multiplier * iqr
            upper_bound = q3 + multiplier * iqr
            
            df = df.withColumn(
                f"{col_name}_is_anomaly",
                when(
                    (col(col_name) < lower_bound) | (col(col_name) > upper_bound),
                    True
                ).otherwise(False)
            )
        
        return df
    
    def _isolation_forest_detection(self, df, columns: List[str], contamination: float = 0.1):
        """Isolation Forestå¼å¸¸å¼æ£æµ?""
        from pyspark.ml.feature import VectorAssembler
        from pyspark.ml.iforest import IsolationForest
        
        # åå¤ç¹å¾åé
        assembler = VectorAssembler(
            inputCols=columns,
            outputCol="features"
        )
        df_features = assembler.transform(df)
        
        # è®­ç»Isolation Forestæ¨¡å
        iforest = IsolationForest(
            numTrees=100,
            maxSamples=256,
            contamination=contamination,
            maxDepth=10,
            seed=42
        )
        
        model = iforest.fit(df_features)
        
        # é¢æµå¼å¸¸å?
        predictions = model.transform(df_features)
        
        return predictions.withColumn(
            "is_anomaly",
            when(col("prediction") == 1, False).otherwise(True)
        )
    
    def _dbscan_detection(self, df, columns: List[str], eps: float = 0.5, min_samples: int = 5):
        """DBSCANèç±»å¼å¸¸å¼æ£æµ?""
        from pyspark.ml.feature import VectorAssembler
        from pyspark.ml.clustering import DBSCAN
        
        # åå¤ç¹å¾åé
        assembler = VectorAssembler(
            inputCols=columns,
            outputCol="features"
        )
        df_features = assembler.transform(df)
        
        # DBSCANèç±»
        dbscan = DBSCAN(
            eps=eps,
            minSamples=min_samples,
            featuresCol="features",
            predictionCol="cluster"
        )
        
        model = dbscan.fit(df_features)
        predictions = model.transform(df_features)
        
        # æ è®°åªå£°ç¹ä¸ºå¼å¸¸å?
        return predictions.withColumn(
            "is_anomaly",
            when(col("cluster") == -1, True).otherwise(False)
        )
```

#### **2.2.2 ç¼ºå¤±å¼å¤çå¨**

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, mean
from pyspark.sql.window import Window
from typing import Dict, List, Any

class MissingValueHandler:
    """ç¼ºå¤±å¼å¤çå¨"""
    
    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        self.spark = spark
        self.config = config
        self.strategies = {
            'drop': self._drop_missing,
            'mean': self._fill_with_mean,
            'median': self._fill_with_median,
            'mode': self._fill_with_mode,
            'forward_fill': self._forward_fill,
            'backward_fill': self._backward_fill,
            'interpolation': self._interpolation,
            'ml_prediction': self._ml_prediction
        }
    
    def handle_missing_values(self, df, strategy_config: Dict[str, str]):
        """
        å¤çç¼ºå¤±å?
        
        Args:
            df: Spark DataFrame
            strategy_config: åå -> å¡«åç­ç¥çæ å°?
        
        Returns:
            DataFrame: å¤çåçDataFrame
        """
        for col_name, strategy in strategy_config.items():
            handler = self.strategies.get(strategy)
            if not handler:
                raise ValueError(f"ä¸æ¯æçå¡«åç­ç¥: {strategy}")
            
            df = handler(df, col_name)
        
        return df
    
    def _drop_missing(self, df, col_name: str):
        """å é¤ç¼ºå¤±å?""
        return df.dropna(subset=[col_name])
    
    def _fill_with_mean(self, df, col_name: str):
        """ä½¿ç¨åå¼å¡«å?""
        mean_val = df.select(mean(col(col_name))).collect()[0][0]
        return df.fillna({col_name: mean_val})
    
    def _fill_with_median(self, df, col_name: str):
        """ä½¿ç¨ä¸­ä½æ°å¡«å?""
        median_val = df.approxQuantile(col_name, [0.5], 0.05)[0]
        return df.fillna({col_name: median_val})
    
    def _fill_with_mode(self, df, col_name: str):
        """ä½¿ç¨ä¼æ°å¡«å"""
        mode_val = df.groupBy(col_name).count().orderBy('count', ascending=False).first()[0]
        return df.fillna({col_name: mode_val})
    
    def _forward_fill(self, df, col_name: str, order_col: str = 'timestamp'):
        """ååå¡«å"""
        window = Window.orderBy(order_col).rowsBetween(Window.unboundedPreceding, 0)
        
        return df.withColumn(
            col_name,
            when(
                col(col_name).isNull(),
                F.last(col(col_name), ignorenulls=True).over(window)
            ).otherwise(col(col_name))
        )
    
    def _backward_fill(self, df, col_name: str, order_col: str = 'timestamp'):
        """ååå¡«å"""
        window = Window.orderBy(order_col).rowsBetween(0, Window.unboundedFollowing)
        
        return df.withColumn(
            col_name,
            when(
                col(col_name).isNull(),
                F.first(col(col_name), ignorenulls=True).over(window)
            ).otherwise(col(col_name))
        )
    
    def _interpolation(self, df, col_name: str, order_col: str = 'timestamp', method: str = 'linear'):
        """æå¼å¡«å?""
        from pyspark.sql.window import Window
        import pyspark.sql.functions as F
        
        # è·åååéç©ºå?
        window_before = Window.orderBy(order_col).rowsBetween(Window.unboundedPreceding, -1)
        window_after = Window.orderBy(order_col).rowsBetween(1, Window.unboundedFollowing)
        
        df = df.withColumn(
            'prev_value',
            F.last(col(col_name), ignorenulls=True).over(window_before)
        ).withColumn(
            'next_value',
            F.first(col(col_name), ignorenulls=True).over(window_after)
        ).withColumn(
            'prev_time',
            F.last(col(order_col), ignorenulls=True).over(window_before)
        ).withColumn(
            'next_time',
            F.first(col(order_col), ignorenulls=True).over(window_after)
        )
        
        # çº¿æ§æå?
        if method == 'linear':
            df = df.withColumn(
                col_name,
                when(
                    col(col_name).isNull(),
                    col('prev_value') + 
                    (col('next_value') - col('prev_value')) * 
                    (col(order_col) - col('prev_time')) / 
                    (col('next_time') - col('prev_time'))
                ).otherwise(col(col_name))
            )
        
        return df.drop('prev_value', 'next_value', 'prev_time', 'next_time')
    
    def _ml_prediction(self, df, col_name: str, feature_cols: List[str]):
        """ä½¿ç¨æºå¨å­¦ä¹ é¢æµå¡«å"""
        from pyspark.ml.feature import VectorAssembler
        from pyspark.ml.regression import RandomForestRegressor
        
        # åç¦»æå¼åæ å¼çæ°æ®
        df_with_value = df.filter(col(col_name).isNotNull())
        df_missing = df.filter(col(col_name).isNull())
        
        # è®­ç»æ¨¡å
        assembler = VectorAssembler(
            inputCols=feature_cols,
            outputCol="features"
        )
        
        train_data = assembler.transform(df_with_value)
        
        rf = RandomForestRegressor(
            featuresCol="features",
            labelCol=col_name,
            numTrees=100,
            maxDepth=10,
            seed=42
        )
        
        model = rf.fit(train_data)
        
        # é¢æµç¼ºå¤±å?
        test_data = assembler.transform(df_missing)
        predictions = model.transform(test_data)
        
        # åå¹¶ç»æ
        return df_with_value.union(predictions.drop("features"))
```

#### **2.2.3 éå¤æ°æ®å»éå?*

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, md5, concat_ws
from typing import Dict, List, Any

class DuplicateRemover:
    """éå¤æ°æ®å»éå?""
    
    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        self.spark = spark
        self.config = config
        self.methods = {
            'exact': self._exact_dedup,
            'hash': self._hash_dedup,
            'fuzzy': self._fuzzy_dedup,
            'time_window': self._time_window_dedup
        }
    
    def remove_duplicates(self, df, method: str = 'exact', **kwargs):
        """
        å»é¤éå¤æ°æ®
        
        Args:
            df: Spark DataFrame
            method: å»éæ¹æ³
            **kwargs: æ¹æ³åæ°
        
        Returns:
            DataFrame: å»éåçDataFrame
        """
        remover = self.methods.get(method)
        if not remover:
            raise ValueError(f"ä¸æ¯æçå»éæ¹æ³: {method}")
        
        return remover(df, **kwargs)
    
    def _exact_dedup(self, df, subset: List[str] = None):
        """ç²¾ç¡®å»é"""
        return df.dropDuplicates(subset=subset)
    
    def _hash_dedup(self, df, columns: List[str]):
        """åå¸å»é"""
        # çæåå¸é?
        df = df.withColumn(
            'hash_key',
            md5(concat_ws('|', *[col(c) for c in columns]))
        )
        
        # å»é
        return df.dropDuplicates(['hash_key']).drop('hash_key')
    
    def _fuzzy_dedup(self, df, columns: List[str], threshold: float = 0.9):
        """æ¨¡ç³å»éï¼åºäºç¸ä¼¼åº¦ï¼?""
        from pyspark.ml.feature import MinHashLSH, HashingTF, Tokenizer
        from pyspark.sql.functions import udf
        from pyspark.sql.types import FloatType
        
        # å¯¹æ¯ä¸ªåè¿è¡åè¯ååå¸?
        for col_name in columns:
            tokenizer = Tokenizer(inputCol=col_name, outputCol=f"{col_name}_tokens")
            df = tokenizer.transform(df)
            
            hashingTF = HashingTF(
                inputCol=f"{col_name}_tokens",
                outputCol=f"{col_name}_features",
                numFeatures=1024
            )
            df = hashingTF.transform(df)
        
        # ä½¿ç¨MinHash LSHè¿è¡ç¸ä¼¼åº¦å¹é?
        mh = MinHashLSH(
            inputCol=f"{columns[0]}_features",
            outputCol="hashes",
            numHashTables=5
        )
        
        model = mh.fit(df)
        
        # æ¾åºç¸ä¼¼åº¦è¶è¿éå¼çè®°å½å¯?
        similar_pairs = model.approxSimilarityJoin(
            df, df, 1 - threshold, distCol="distance"
        ).filter(col("distance") < (1 - threshold))
        
        # æ è®°éå¤è®°å½
        duplicate_ids = similar_pairs.select("datasetB.id").distinct()
        
        # è¿æ»¤æéå¤è®°å½?
        return df.join(duplicate_ids, on="id", how="left_anti")
    
    def _time_window_dedup(self, df, time_col: str, window_size: str = '1 hour'):
        """æ¶é´çªå£å»é"""
        from pyspark.sql.window import Window
        import pyspark.sql.functions as F
        
        window = Window.partitionBy(
            F.window(col(time_col), window_size)
        ).orderBy(col(time_col))
        
        return df.withColumn(
            'row_num',
            F.row_number().over(window)
        ).filter(col('row_num') == 1).drop('row_num')
```

---

## 3. å¼æºæ¹æ¡éæ?

### 3.1 Great Expectationséæ

```python
import great_expectations as gx
from great_expectations.dataset import SparkDFDataset
from typing import Dict, List

class GreatExpectationsCleaner:
    """Great Expectationsæ°æ®æ¸æ´å?""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.context = gx.get_context()
        self.expectation_suite = self._load_expectation_suite()
    
    def _load_expectation_suite(self):
        """å è½½ææå¥ä»¶"""
        suite_name = self.config.get('suite_name', 'data_cleaning_suite')
        
        try:
            return self.context.get_expectation_suite(suite_name)
        except:
            # åå»ºæ°çææå¥ä»¶
            suite = self.context.create_expectation_suite(suite_name)
            return self._build_default_expectations(suite)
    
    def _build_default_expectations(self, suite):
        """æå»ºé»è®¤ææ"""
        # ä»·æ ¼æ°æ®ææ
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="price",
                min_value=0,
                max_value=1000000
            )
        )
        
        # æ°éæ°æ®ææ
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="volume",
                min_value=0,
                max_value=1e12
            )
        )
        
        # æ¶é´æ³ææ?
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToNotBeNull(
                column="timestamp"
            )
        )
        
        return suite
    
    def validate_and_clean(self, df):
        """éªè¯å¹¶æ¸æ´æ°æ?""
        # è½¬æ¢ä¸ºGreat Expectations Dataset
        gx_df = SparkDFDataset(df)
        
        # è¿è¡éªè¯
        results = gx_df.validate(
            expectation_suite=self.expectation_suite,
            result_format="COMPLETE"
        )
        
        # æ ¹æ®éªè¯ç»ææ¸æ´æ°æ®
        if not results.success:
            df = self._apply_cleaning_rules(df, results)
        
        return df, results
    
    def _apply_cleaning_rules(self, df, validation_results):
        """åºç¨æ¸æ´è§å"""
        for result in validation_results.results:
            if not result.success:
                expectation_type = result.expectation_config.expectation_type
                column = result.expectation_config.kwargs.get('column')
                
                if expectation_type == 'expect_column_values_to_be_between':
                    min_val = result.expectation_config.kwargs.get('min_value')
                    max_val = result.expectation_config.kwargs.get('max_value')
                    
                    # è¿æ»¤å¼å¸¸å?
                    df = df.filter(
                        (col(column) >= min_val) & (col(column) <= max_val)
                    )
                
                elif expectation_type == 'expect_column_values_to_not_be_null':
                    # å é¤ç©ºå?
                    df = df.dropna(subset=[column])
        
        return df
```

### 3.2 Apache Sparkéæ

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit
from typing import Dict, List, Any

class SparkDataCleaner:
    """Sparkæ°æ®æ¸æ´å?""
    
    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        self.spark = spark
        self.config = config
        self.anomaly_detector = AnomalyDetector(spark, config)
        self.missing_handler = MissingValueHandler(spark, config)
        self.duplicate_remover = DuplicateRemover(spark, config)
    
    def clean_data(self, df, cleaning_config: Dict[str, Any]):
        """
        æ§è¡æ°æ®æ¸æ´
        
        Args:
            df: è¾å¥DataFrame
            cleaning_config: æ¸æ´éç½®
        
        Returns:
            DataFrame: æ¸æ´åçDataFrame
            Dict: æ¸æ´æ¥å
        """
        report = {
            'input_count': df.count(),
            'anomalies_removed': 0,
            'missing_values_filled': 0,
            'duplicates_removed': 0,
            'output_count': 0
        }
        
        # 1. å¼å¸¸å¼æ£æµåå¤ç
        if cleaning_config.get('detect_anomalies', False):
            df = self.anomaly_detector.detect_anomalies(
                df,
                columns=cleaning_config['anomaly_columns'],
                method=cleaning_config.get('anomaly_method', 'zscore')
            )
            
            # è¿æ»¤å¼å¸¸å?
            anomaly_cols = [c for c in df.columns if c.endswith('_is_anomaly')]
            for anomaly_col in anomaly_cols:
                before_count = df.count()
                df = df.filter(col(anomaly_col) == False).drop(anomaly_col)
                report['anomalies_removed'] += before_count - df.count()
        
        # 2. ç¼ºå¤±å¼å¤ç?
        if cleaning_config.get('handle_missing', False):
            before_count = df.count()
            df = self.missing_handler.handle_missing_values(
                df,
                strategy_config=cleaning_config['missing_strategy']
            )
            report['missing_values_filled'] = before_count - df.count()
        
        # 3. éå¤æ°æ®å»é
        if cleaning_config.get('remove_duplicates', False):
            before_count = df.count()
            df = self.duplicate_remover.remove_duplicates(
                df,
                method=cleaning_config.get('dedup_method', 'exact'),
                subset=cleaning_config.get('dedup_columns')
            )
            report['duplicates_removed'] = before_count - df.count()
        
        report['output_count'] = df.count()
        
        return df, report
```

---

## 4. éç½®ç®¡ç

### 4.1 æ¸æ´è§åéç½®

```yaml
# data_cleaning_config.yaml

# å¼å¸¸å¼æ£æµéç½?
anomaly_detection:
  enabled: true
  method: zscore  # zscore, iqr, isolation_forest, dbscan
  columns:
    - price
    - volume
    - turnover
  thresholds:
    zscore: 3.0
    iqr_multiplier: 1.5
    contamination: 0.1

# ç¼ºå¤±å¼å¤çéç½?
missing_value_handling:
  enabled: true
  strategies:
    price: interpolation
    volume: mean
    turnover: forward_fill
    timestamp: drop
  interpolation:
    method: linear  # linear, spline, polynomial
    order: 3

# éå¤æ°æ®å»ééç½®
duplicate_removal:
  enabled: true
  method: exact  # exact, hash, fuzzy, time_window
  columns:
    - symbol
    - timestamp
  fuzzy_threshold: 0.9
  time_window: 1 hour

# æ°æ®æ ¼å¼æ ååéç½?
format_standardization:
  enabled: true
  date_format: "%Y-%m-%d %H:%M:%S"
  number_format:
    precision: 2
    rounding: half_up

# æ¸æ´è§åéç½®
cleaning_rules:
  - name: price_range_check
    type: range
    column: price
    min: 0
    max: 1000000
    action: remove
  
  - name: volume_positive_check
    type: positive
    column: volume
    action: remove
  
  - name: timestamp_not_null
    type: not_null
    column: timestamp
    action: remove
```

### 4.2 éç½®å è½½å?

```python
import yaml
from typing import Dict, Any

class CleaningConfigLoader:
    """æ¸æ´éç½®å è½½å?""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """å è½½éç½®æä»¶"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_anomaly_config(self) -> Dict[str, Any]:
        """è·åå¼å¸¸å¼æ£æµéç½?""
        return self.config.get('anomaly_detection', {})
    
    def get_missing_config(self) -> Dict[str, Any]:
        """è·åç¼ºå¤±å¼å¤çéç½?""
        return self.config.get('missing_value_handling', {})
    
    def get_dedup_config(self) -> Dict[str, Any]:
        """è·åå»ééç½®"""
        return self.config.get('duplicate_removal', {})
    
    def get_format_config(self) -> Dict[str, Any]:
        """è·åæ ¼å¼æ ååéç½?""
        return self.config.get('format_standardization', {})
    
    def get_cleaning_rules(self) -> List[Dict[str, Any]]:
        """è·åæ¸æ´è§å"""
        return self.config.get('cleaning_rules', [])
```

---

## 5. é¨ç½²æ¶æ

### 5.1 åæºé¨ç½²

```yaml
# docker-compose.yml
version: '3.8'

services:
  spark-master:
    image: bitnami/spark:latest
    container_name: spark-master
    environment:
      - SPARK_MODE=master
      - SPARK_MASTER_HOST=spark-master
    ports:
      - "8080:8080"
      - "7077:7077"
    volumes:
      - ./data:/data
      - ./config:/config
  
  spark-worker:
    image: bitnami/spark:latest
    container_name: spark-worker
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
    depends_on:
      - spark-master
    volumes:
      - ./data:/data
      - ./config:/config
  
  data-cleaning-engine:
    build: .
    container_name: data-cleaning-engine
    environment:
      - SPARK_MASTER=spark://spark-master:7077
      - CONFIG_PATH=/config/data_cleaning_config.yaml
    depends_on:
      - spark-master
    volumes:
      - ./data:/data
      - ./config:/config
```

### 5.2 æ¸æ´å¼æDockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# å®è£ä¾èµ
RUN pip install --no-cache-dir \
    pyspark==3.4.0 \
    great-expectations==0.17.0 \
    pyyaml==6.0 \
    pandas==2.0.0 \
    numpy==1.24.0

# å¤å¶ä»£ç 
COPY src/ /app/src/
COPY config/ /app/config/

# å¯å¨å½ä»¤
CMD ["python", "src/data_cleaning_engine.py"]
```

---

## 6. ä½¿ç¨ç¤ºä¾

### 6.1 åºæ¬ä½¿ç¨

```python
from pyspark.sql import SparkSession
from data_cleaning_engine import SparkDataCleaner
from config_loader import CleaningConfigLoader

# åå§åSpark
spark = SparkSession.builder \
    .appName("DataCleaningEngine") \
    .getOrCreate()

# å è½½éç½®
config_loader = CleaningConfigLoader("config/data_cleaning_config.yaml")

# åå»ºæ¸æ´å?
cleaner = SparkDataCleaner(spark, config_loader.config)

# è¯»åæ°æ®
df = spark.read.parquet("data/raw/market_data.parquet")

# æ§è¡æ¸æ´
cleaned_df, report = cleaner.clean_data(
    df,
    cleaning_config={
        'detect_anomalies': True,
        'anomaly_columns': ['price', 'volume'],
        'anomaly_method': 'zscore',
        'handle_missing': True,
        'missing_strategy': {
            'price': 'interpolation',
            'volume': 'mean'
        },
        'remove_duplicates': True,
        'dedup_method': 'exact',
        'dedup_columns': ['symbol', 'timestamp']
    }
)

# ä¿å­æ¸æ´åçæ°æ®
cleaned_df.write.parquet("data/cleaned/market_data.parquet", mode='overwrite')

# æå°æ¸æ´æ¥å
print("æ¸æ´æ¥å:")
print(f"è¾å¥è®°å½æ? {report['input_count']}")
print(f"å¼å¸¸å¼ç§»é? {report['anomalies_removed']}")
print(f"ç¼ºå¤±å¼å¡«å? {report['missing_values_filled']}")
print(f"éå¤å¼ç§»é? {report['duplicates_removed']}")
print(f"è¾åºè®°å½æ? {report['output_count']}")
```

### 6.2 ä¸Great Expectationséæ

```python
from great_expectations_cleaner import GreatExpectationsCleaner

# åå»ºGreat Expectationsæ¸æ´å?
gx_cleaner = GreatExpectationsCleaner({
    'suite_name': 'market_data_cleaning_suite'
})

# éªè¯å¹¶æ¸æ´æ°æ?
cleaned_df, validation_results = gx_cleaner.validate_and_clean(df)

# æ¥çéªè¯ç»æ
print(f"éªè¯æå: {validation_results.success}")
print(f"éè¿ç? {validation_results.statistics.success_percent:.2f}%")
```

---

## 7. æ§è½ä¼å

### 7.1 Sparkä¼åéç½®

```python
# Sparkæ§è½ä¼åéç½®
spark = SparkSession.builder \
    .appName("DataCleaningEngine") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.executor.memory", "4g") \
    .config("spark.executor.cores", "2") \
    .config("spark.driver.memory", "2g") \
    .config("spark.sql.execution.arrow.enabled", "true") \
    .getOrCreate()
```

### 7.2 ç¼å­ç­ç¥

```python
# æ°æ®ç¼å­ç­ç¥
def clean_data_with_cache(df, cleaning_config):
    # ç¼å­åå§æ°æ®
    df.cache()
    
    # æ§è¡æ¸æ´
    cleaned_df = cleaner.clean_data(df, cleaning_config)
    
    # ç¼å­æ¸æ´åçæ°æ®
    cleaned_df.cache()
    
    # éæ¾åå§æ°æ®ç¼å­
    df.unpersist()
    
    return cleaned_df
```

---

## 8. çæ§ä¸åè­?

### 8.1 æ¸æ´è´¨éçæ§

```python
from prometheus_client import Counter, Histogram, Gauge

# å®ä¹çæ§ææ 
cleaning_counter = Counter(
    'data_cleaning_total',
    'æ°æ®æ¸æ´æ»æ¬¡æ?
)

anomaly_counter = Counter(
    'anomaly_detected_total',
    'æ£æµå°çå¼å¸¸å¼æ°é?
)

missing_counter = Counter(
    'missing_values_filled_total',
    'å¡«åçç¼ºå¤±å¼æ°é?
)

quality_score = Gauge(
    'data_quality_score',
    'æ°æ®è´¨éè¯å'
)

cleaning_duration = Histogram(
    'data_cleaning_duration_seconds',
    'æ°æ®æ¸æ´èæ¶'
)

# çæ§è£é¥°å?
def monitor_cleaning(func):
    def wrapper(*args, **kwargs):
        cleaning_counter.inc()
        
        with cleaning_duration.time():
            result = func(*args, **kwargs)
        
        # æ´æ°çæ§ææ 
        if isinstance(result, tuple):
            df, report = result
            anomaly_counter.inc(report['anomalies_removed'])
            missing_counter.inc(report['missing_values_filled'])
            quality_score.set(
                report['output_count'] / report['input_count'] * 100
            )
        
        return result
    
    return wrapper
```

---

## 9. å¼åè·¯çº¿å¾

### 9.1 é¶æ®µä¸ï¼åºç¡åè½ (2å?

- â?å¼å¸¸å¼æ£æµå¨å®ç°
- â?ç¼ºå¤±å¼å¤çå¨å®ç°
- â?éå¤æ°æ®å»éå¨å®ç?
- â?åºæ¬éç½®ç®¡ç

### 9.2 é¶æ®µäºï¼é«çº§åè½ (2å?

- â?Great Expectationséæ
- â?æºå¨å­¦ä¹ é¢æµå¡«å
- â?æ¨¡ç³å»éåè½
- â?é«çº§æå¼æ¹æ³?

### 9.3 é¶æ®µä¸ï¼æ§è½ä¼å (1å?

- â?Sparkæ§è½ä¼å
- â?ç¼å­ç­ç¥ä¼å
- â?å¹¶è¡å¤çä¼å
- â?åå­ç®¡çä¼å

### 9.4 é¶æ®µåï¼çæ§è¿ç»´ (1å?

- â?Prometheusçæ§éæ
- â?æ¸æ´æ¥åçæ
- â?è´¨éææ ç»è®¡
- â?åè­¦æºå¶

---

## 10. ææ¬æçåæ

### 10.1 å¼åææ?

| é¡¹ç® | å·¥ä½é?| ææ¬ |
|------|--------|------|
| æ ¸å¿åè½å¼å?| 40h | Â¥4,000 |
| æµè¯ä¸ä¼å?| 15h | Â¥1,500 |
| ææ¡£ç¼å | 5h | Â¥500 |
| **æ»è®¡** | **60h** | **Â¥6,000** |

### 10.2 æ¶çè¯ä¼°

| æ¶çé¡?| ä¼°ç®ä»·å?| è¯´æ |
|--------|---------|------|
| æ°æ®è´¨éæå | Â¥20,000 | åå°æ°æ®é®é¢å¯¼è´çæå¤?|
| äººå·¥ææ¬èçº¦ | Â¥10,000 | èªå¨åæ¸æ´åå°äººå·¥å¹²é¢?|
| ç³»ç»ç¨³å®æ§æå?| Â¥15,000 | åå°å æ°æ®é®é¢å¯¼è´çç³»ç»æé |
| **æ»æ¶ç?* | **Â¥45,000** | |

**ROI**: (45,000 - 6,000) / 6,000 = 650%

---

## ð åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**ææ¡£ç»æ**
