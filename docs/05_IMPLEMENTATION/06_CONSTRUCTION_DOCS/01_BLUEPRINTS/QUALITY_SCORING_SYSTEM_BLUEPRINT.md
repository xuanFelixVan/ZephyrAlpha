---
module_id: QUALITY_SCORING_SYSTEM_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 9 çæ§å±?
compliance_level: 专业标准
responsibility:
  - 数据质量评分
  - 质量指标计算
  - 质量等级评定
  - 质量趋势分析
layer: Layer 5 (策略执行层)
---

# 数据质量评分系统蓝图

> **核心职责**: 数据质量评分，计算和评定数据质量等级
> **职责边界**: 
> - â?æ¬ææ¡£è´è´£ï¼æ°æ®è´¨éè¯åãè´¨éææ è®¡ç®ãè´¨éç­çº§è¯å®ãè´¨éè¶å¿åæ?
> - â?æ¬ææ¡£ä¸è´è´£ï¼æ°æ®è´¨éçæ§ãæ°æ®è´¨éæ²»çãæ°æ®è´¨éæ¥å?
ï»? æ°æ®è´¨éè¯åç³»ç»èå¾

> **æ ¸å¿å®ä½**: æ°æ®è´¨éè¯åç³»ç»èå¾çæ ¸å¿åè½å®ç?


> **模块ID**: `QUALITY_SCORING_001`
> **å®æ½å¨æ**: Week 8-9ï¼?å¨ï¼
> **ä¼å
çº?*: P1ï¼éè¦ï¼
> **预期收益**: 提升数据质量透明度，降低数据问题风险50%

## 核心定位

> 核心职责: Quality Scoring System蓝图设计
> 职责边界: 
> - â?æ¬ææ¡£è´è´£ï¼Quality Scoring Systemèå¾è®¾è®¡ç¸å
³å
å®¹
> - â?æ¬ææ¡£ä¸è´è´£ï¼å
¶ä»æ¨¡åå
å®¹ï¼ç¡®ä¿ç³»ç»åè½çç¨³å®è¿è¡...


## 设计目标

### 主要目标

1. **功能完整性**: 确保QUALITY SCORING SYSTEM功能完整，满足业务需求
2. **性能优化**: 提升系统性能，降低资源消耗
3. **可维护性**: 提高代码质量，便于后续维护
4. **可扩展性**: 支持功能扩展，适应业务变化

### 质量目标

- 代码覆盖率: ≥80%
- 性能指标: 满足设计要求
- 文档完整性: 100%


## 核心功能

### 功能清单

1. **数据管理**: 提供数据存储、查询、更新功能
2. **业务逻辑**: 实现核心业务逻辑处理
3. **接口服务**: 提供标准化的API接口
4. **监控告警**: 实时监控系统状态

### 功能特性

- 高可用性设计
- 自动故障恢复
- 灵活配置管理


## 实现方案

### 技术架构

采用QUALITY SCORING SYSTEM化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控


## 一、设计背景与目标

### 1.1 ä¸å¡éæ±?

**当前痛点**:
- ç¼ºå°ç»ä¸çæ°æ®è´¨éè¯åæ å?
- 无法量化评估数据质量水平
- æ°æ®è´¨éé®é¢é¾ä»¥è¿½è¸ªåæ¹è¿?
- 缺少数据质量趋势分析

**业务目标**:
- å»ºç«å¤ç»´åº¦æ°æ®è´¨éè¯åä½ç³?
- æä¾å®æ¶æ°æ®è´¨éè¯ååè¶å¿åæ?
- 支持数据质量改进追踪
- 生成数据质量报告和可视化

### 1.2 ææ¯ç®æ ?

| ææ  | ç®æ å?| è¯´æ |
|------|--------|------|
| **è¯åç»´åº¦** | â?ä¸?| è³å°è¦ç6ä¸ªè´¨éç»´åº?|
| **è¯åå®æ¶æ?* | <30ç§?| è¯åè®¡ç®ååºæ¶é´<30ç§?|
| **è¯ååç¡®æ?* | â?5% | è¯åç»æåç¡®çâ¥95% |
| **åå²æ°æ®ä¿ç** | â?å¹?| ä¿çè³å°1å¹´çåå²è¯åæ°æ® |

## ä¸ãæ ¸å¿æ¨¡åè®¾è®?

### 3.1 评分维度定义 (QualityDimensions)

**职责**: 定义和计算各维度质量评分

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import pandas as pd
import numpy as np

class QualityDimension(Enum):
    """质量维度"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    TIMELINESS = "timeliness"
    CONSISTENCY = "consistency"
    UNIQUENESS = "uniqueness"
    VALIDITY = "validity"

@dataclass
class DimensionScore:
    """维度评分"""
    dimension: QualityDimension
    score: float
    weight: float
    details: Dict[str, Any] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=datetime.now)

class QualityScorer:
    """è´¨éè¯åå?""
    
    def __init__(self):
        self.dimension_weights = {
            QualityDimension.COMPLETENESS: 0.20,
            QualityDimension.ACCURACY: 0.25,
            QualityDimension.TIMELINESS: 0.15,
            QualityDimension.CONSISTENCY: 0.15,
            QualityDimension.UNIQUENESS: 0.10,
            QualityDimension.VALIDITY: 0.15
        }
    
    def calculate_completeness_score(self, df: pd.DataFrame) -> DimensionScore:
        """è®¡ç®å®æ´æ§è¯å?""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        completeness = 1 - (missing_cells / total_cells)
        
        details = {
            "total_cells": total_cells,
            "missing_cells": missing_cells,
            "completeness_ratio": completeness,
            "columns_with_missing": df.columns[df.isnull().any()].tolist()
        }
        
        return DimensionScore(
            dimension=QualityDimension.COMPLETENESS,
            score=completeness,
            weight=self.dimension_weights[QualityDimension.COMPLETENESS],
            details=details
        )
    
    def calculate_accuracy_score(self, df: pd.DataFrame, 
                                  rules: Dict[str, Any]) -> DimensionScore:
        """è®¡ç®åç¡®æ§è¯å?""
        accuracy_scores = []
        
        for column, rule in rules.items():
            if column in df.columns:
                if rule.get("type") == "range":
                    min_val = rule.get("min")
                    max_val = rule.get("max")
                    valid_count = df[(df[column] >= min_val) & 
                                    (df[column] <= max_val)][column].count()
                    total_count = df[column].count()
                    accuracy = valid_count / total_count if total_count > 0 else 0
                    accuracy_scores.append(accuracy)
        
        overall_accuracy = np.mean(accuracy_scores) if accuracy_scores else 0
        
        details = {
            "rules_applied": len(rules),
            "accuracy_scores": accuracy_scores,
            "overall_accuracy": overall_accuracy
        }
        
        return DimensionScore(
            dimension=QualityDimension.ACCURACY,
            score=overall_accuracy,
            weight=self.dimension_weights[QualityDimension.ACCURACY],
            details=details
        )
    
    def calculate_timeliness_score(self, df: pd.DataFrame,
                                    timestamp_column: str,
                                    expected_frequency: str) -> DimensionScore:
        """è®¡ç®æ¶ææ§è¯å?""
        if timestamp_column not in df.columns:
            return DimensionScore(
                dimension=QualityDimension.TIMELINESS,
                score=0.0,
                weight=self.dimension_weights[QualityDimension.TIMELINESS],
                details={"error": "Timestamp column not found"}
            )
        
        df_sorted = df.sort_values(timestamp_column)
        timestamps = pd.to_datetime(df_sorted[timestamp_column])
        
        time_diffs = timestamps.diff().dropna()
        
        if expected_frequency == "daily":
            expected_diff = pd.Timedelta(days=1)
        elif expected_frequency == "hourly":
            expected_diff = pd.Timedelta(hours=1)
        else:
            expected_diff = pd.Timedelta(days=1)
        
        timely_count = (time_diffs <= expected_diff * 1.1).sum()
        total_count = len(time_diffs)
        timeliness = timely_count / total_count if total_count > 0 else 0
        
        details = {
            "expected_frequency": expected_frequency,
            "timely_count": timely_count,
            "total_count": total_count,
            "timeliness_ratio": timeliness
        }
        
        return DimensionScore(
            dimension=QualityDimension.TIMELINESS,
            score=timeliness,
            weight=self.dimension_weights[QualityDimension.TIMELINESS],
            details=details
        )
    
    def calculate_consistency_score(self, df: pd.DataFrame,
                                     consistency_rules: List[Dict]) -> DimensionScore:
        """è®¡ç®ä¸è´æ§è¯å?""
        consistency_scores = []
        
        for rule in consistency_rules:
            rule_type = rule.get("type")
            
            if rule_type == "cross_column":
                col1 = rule.get("column1")
                col2 = rule.get("column2")
                condition = rule.get("condition")
                
                if col1 in df.columns and col2 in df.columns:
                    if condition == "equal":
                        consistent = (df[col1] == df[col2]).sum()
                        total = len(df)
                        consistency_scores.append(consistent / total)
        
        overall_consistency = np.mean(consistency_scores) if consistency_scores else 0
        
        details = {
            "rules_applied": len(consistency_rules),
            "consistency_scores": consistency_scores,
            "overall_consistency": overall_consistency
        }
        
        return DimensionScore(
            dimension=QualityDimension.CONSISTENCY,
            score=overall_consistency,
            weight=self.dimension_weights[QualityDimension.CONSISTENCY],
            details=details
        )
    
    def calculate_uniqueness_score(self, df: pd.DataFrame,
                                    unique_columns: List[str]) -> DimensionScore:
        """è®¡ç®å¯ä¸æ§è¯å?""
        uniqueness_scores = []
        
        for column in unique_columns:
            if column in df.columns:
                total_count = len(df)
                unique_count = df[column].nunique()
                uniqueness = unique_count / total_count if total_count > 0 else 0
                uniqueness_scores.append(uniqueness)
        
        overall_uniqueness = np.mean(uniqueness_scores) if uniqueness_scores else 0
        
        details = {
            "columns_checked": unique_columns,
            "uniqueness_scores": uniqueness_scores,
            "overall_uniqueness": overall_uniqueness
        }
        
        return DimensionScore(
            dimension=QualityDimension.UNIQUENESS,
            score=overall_uniqueness,
            weight=self.dimension_weights[QualityDimension.UNIQUENESS],
            details=details
        )
    
    def calculate_validity_score(self, df: pd.DataFrame,
                                  validity_rules: Dict[str, Any]) -> DimensionScore:
        """è®¡ç®æææ§è¯å?""
        validity_scores = []
        
        for column, rule in validity_rules.items():
            if column in df.columns:
                if rule.get("type") == "regex":
                    import re
                    pattern = rule.get("pattern")
                    valid_count = df[column].astype(str).str.match(pattern, na=False).sum()
                    total_count = df[column].count()
                    validity = valid_count / total_count if total_count > 0 else 0
                    validity_scores.append(validity)
                elif rule.get("type") == "enum":
                    allowed_values = rule.get("values")
                    valid_count = df[column].isin(allowed_values).sum()
                    total_count = df[column].count()
                    validity = valid_count / total_count if total_count > 0 else 0
                    validity_scores.append(validity)
        
        overall_validity = np.mean(validity_scores) if validity_scores else 0
        
        details = {
            "rules_applied": len(validity_rules),
            "validity_scores": validity_scores,
            "overall_validity": overall_validity
        }
        
        return DimensionScore(
            dimension=QualityDimension.VALIDITY,
            score=overall_validity,
            weight=self.dimension_weights[QualityDimension.VALIDITY],
            details=details
        )
```

### 3.2 ç»¼åè¯åè®¡ç®å?(OverallScoreCalculator)

**职责**: 计算综合质量评分

```python
from dataclasses import dataclass
from typing import List
import pandas as pd

@dataclass
class OverallQualityScore:
    """综合质量评分"""
    table_name: str
    overall_score: float
    dimension_scores: List[DimensionScore]
    grade: str
    calculated_at: datetime
    metadata: Dict[str, Any]

class OverallScoreCalculator:
    """ç»¼åè¯åè®¡ç®å?""
    
    def __init__(self):
        self.grade_thresholds = {
            "A": 0.90,
            "B": 0.80,
            "C": 0.70,
            "D": 0.60,
            "F": 0.0
        }
    
    def calculate_overall_score(self, table_name: str,
                                 dimension_scores: List[DimensionScore]) -> OverallQualityScore:
        """计算综合评分"""
        weighted_sum = sum(
            ds.score * ds.weight for ds in dimension_scores
        )
        total_weight = sum(ds.weight for ds in dimension_scores)
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        grade = self._determine_grade(overall_score)
        
        return OverallQualityScore(
            table_name=table_name,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            grade=grade,
            calculated_at=datetime.now()
        )
    
    def _determine_grade(self, score: float) -> str:
        """确定评分等级"""
        for grade, threshold in self.grade_thresholds.items():
            if score >= threshold:
                return grade
        return "F"
```

### 3.3 è¯ååå²ç®¡çå?(ScoreHistoryManager)

**职责**: 管理评分历史数据

```python
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

class ScoreHistoryManager:
    """è¯ååå²ç®¡çå?""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def save_score(self, score: OverallQualityScore):
        """保存评分记录"""
        query = """
        INSERT INTO quality_scores 
        (table_name, overall_score, grade, dimension_scores, calculated_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        self.db.execute(query, (
            score.table_name,
            score.overall_score,
            score.grade,
            json.dumps([ds.__dict__ for ds in score.dimension_scores]),
            score.calculated_at
        ))
    
    def get_score_history(self, table_name: str, 
                          days: int = 30) -> List[Dict[str, Any]]:
        """获取评分历史"""
        query = """
        SELECT * FROM quality_scores
        WHERE table_name = %s
        AND calculated_at >= %s
        ORDER BY calculated_at DESC
        """
        
        start_date = datetime.now() - timedelta(days=days)
        results = self.db.fetch_all(query, (table_name, start_date))
        
        return results
    
    def get_score_trend(self, table_name: str,
                        days: int = 30) -> Dict[str, Any]:
        """获取评分趋势"""
        history = self.get_score_history(table_name, days)
        
        if not history:
            return {"trend": "no_data"}
        
        scores = [h['overall_score'] for h in history]
        
        if len(scores) < 2:
            return {"trend": "insufficient_data"}
        
        recent_avg = np.mean(scores[:7]) if len(scores) >= 7 else np.mean(scores)
        older_avg = np.mean(scores[-7:]) if len(scores) >= 7 else np.mean(scores)
        
        if recent_avg > older_avg * 1.05:
            trend = "improving"
        elif recent_avg < older_avg * 0.95:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "recent_average": recent_avg,
            "older_average": older_avg,
            "change_percentage": ((recent_avg - older_avg) / older_avg) * 100
        }
```

---

## 四、数据流设计

### 4.1 评分计算流程

```
æ°æ®è¡?â?ç»´åº¦è¯åè®¡ç® â?æéå æ â?ç»¼åè¯å â?ç­çº§å¤å® â?å­å¨
```

### 4.2 趋势分析流程

```
åå²è¯å â?è¶å¿è®¡ç® â?ååæ£æµ?â?è¶å¿æ¥å â?å¯è§å?
```

---

## äºãæ¥å£è®¾è®?

### 5.1 RESTful API

#### 5.1.1 获取质量评分

```http
GET /api/v1/quality/score/{table_name}
```

**响应示例**:
```json
{
  "table_name": "stock_prices",
  "overall_score": 0.92,
  "grade": "A",
  "dimension_scores": [
    {
      "dimension": "completeness",
      "score": 0.95,
      "weight": 0.20
    },
    {
      "dimension": "accuracy",
      "score": 0.90,
      "weight": 0.25
    }
  ],
  "calculated_at": "2026-04-06T10:30:00Z"
}
```

#### 5.1.2 获取评分趋势

```http
GET /api/v1/quality/trend/{table_name}?days=30
```

**响应示例**:
```json
{
  "table_name": "stock_prices",
  "trend": "improving",
  "recent_average": 0.92,
  "older_average": 0.88,
  "change_percentage": 4.5
}
```

---

## å
­ãé¨ç½²æ¶æ?

### 6.1 å®¹å¨åé¨ç½?

```yaml
version: '3.8'
services:
  quality-scorer:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=quality_scores
      - POSTGRES_PASSWORD=password
    volumes:
      - pg-data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    volumes:
      - redis-data:/data

volumes:
  pg-data:
  redis-data:
```

---

## ä¸ãçæ§ææ ?

### 7.1 核心指标

| 指标名称 | 指标类型 | 说明 |
|---------|---------|------|
| `quality_score_overall` | Gauge | 综合质量评分 |
| `quality_score_dimension` | Gauge | åç»´åº¦è´¨éè¯å?|
| `quality_score_calculation_duration_seconds` | Histogram | 评分计算耗时 |
| `quality_score_history_count` | Gauge | åå²è¯åè®°å½æ?|

---

## å
«ãå®æ½è®¡å?

### 8.1 å¼åé¶æ®?

| é¶æ®µ | ä»»å¡ | é¢è®¡æ¶é´ | è´è´£äº?|
|------|------|---------|--------|
| **é¶æ®µ1** | å¼åè¯åç»´åº¦è®¡ç®å¨ | 2å¤?| åç«¯å·¥ç¨å¸?|
| **é¶æ®µ2** | å¼åç»¼åè¯åè®¡ç®å¨ | 1å¤?| åç«¯å·¥ç¨å¸?|
| **é¶æ®µ3** | å¼ååå²ç®¡çå¨ | 1å¤?| åç«¯å·¥ç¨å¸?|
| **é¶æ®µ4** | å¼åAPIæ¥å£ | 1å¤?| åç«¯å·¥ç¨å¸?|
| **é¶æ®µ5** | éææµè¯åé¨ç½?| 1å¤?| QAå·¥ç¨å¸?|

### 8.2 验收标准

- [ ] æ¯æ6ä¸ªè´¨éç»´åº¦è¯å?
- [ ] è¯åè®¡ç®ååºæ¶é´<30ç§?
- [ ] 评分准确率≥95%
- [ ] åå²æ°æ®ä¿çâ?å¹?
- [ ] 趋势分析功能正常

---

## ä¹ãé£é©ç®¡ç?

### 9.1 ææ¯é£é?

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| è¯åè§åä¸åç?| é«?| ä¸å¡ä¸å®¶å®¡æ ¸ï¼æç»­ä¼å?|
| è¯åè®¡ç®æ§è½ç¶é¢ | ä¸?| ç¼å­æºå¶ï¼å¼æ­¥è®¡ç®?|
| åå²æ°æ®å­å¨è¨è | ä½?| æ°æ®åç¼©ï¼å®æå½æ¡?|

---

## ð ç¸å
³ææ¡£

### 上游依赖

| 文档名称 | module_id | 依赖类型 | 说明 |
|---------|-----------|---------|------|
| [æ°æ®è´¨éçæ§èå¾](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | DATA_QUALITY_MONITORING_001 | å¼ºä¾èµ?| æä¾æ°æ®è´¨éææ  |
| [è´¨éæ¥åèªå¨åèå¾](./QUALITY_REPORT_AUTOMATION_BLUEPRINT.md) | QUALITY_REPORT_AUTOMATION_001 | å¼ºä¾èµ?| æä¾è´¨éæ¥åæ°æ® |
| [æ°æ®ç®å½èå¾](./DATA_CATALOG_BLUEPRINT.md) | DATA_CATALOG_001 | ä¸­ä¾èµ?| æä¾æ°æ®å
æ°æ?|

### 下游依赖

| 文档名称 | module_id | 依赖类型 | 说明 |
|---------|-----------|---------|------|
| [èªå¨åæ°æ®ä¿®å¤å¼æèå¾](./AUTO_REPAIR_ENGINE_BLUEPRINT.md) | AUTO_REPAIR_ENGINE_001 | å¼ºä¾èµ?| èªå¨åæ°æ®ä¿®å¤?|
| [å¢å¼ºåè­¦ç³»ç»èå¾](./ENHANCED_ALERT_SYSTEM_BLUEPRINT.md) | ENHANCED_ALERT_SYSTEM_001 | ä¸­ä¾èµ?| å¢å¼ºåè­¦ç³»ç» |
| [çæ§ä»ªè¡¨æ¿å¢å¼ºèå¾](./MONITORING_DASHBOARD_ENHANCEMENT_BLUEPRINT.md) | MONITORING_DASHBOARD_ENHANCEMENT_001 | ä¸­ä¾èµ?| çæ§ä»ªè¡¨æ¿å¢å¼?|

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **NumPy** | 1.24+ | æ°å¼è®¡ç®?| [å®æ¹ææ¡£](https://numpy.org/) |
| **Pandas** | 2.0+ | 数据处理 | [官方文档](https://pandas.pydata.org/) |
| **Redis** | 7.0+ | 缓存系统 | [官方文档](https://redis.io/) |
| **PostgreSQL** | 15+ | æ°æ®åº?| [å®æ¹ææ¡£](https://www.postgresql.org/) |

### å¼ç¨å
³ç³»å?

```mermaid
graph LR
    A[数据质量监控] --> B[质量评分系统]
    C[质量报告自动化] --> B
    D[数据目录] --> B
    
    B --> E[自动化数据修复引擎]
    B --> F[增强告警系统]
    B --> G[监控仪表板增强]
    
    style B fill:#ff6b6b
    style A fill:#4ecdc4
    style C fill:#45b7d1
```

---

**ææ¡£çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç»´æ¤è?*: é¦å¸­èå¾æ¶æå¸?
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 6: ç»åä¼åå±?
##### 6.001. Quality Scoring System
- **模块ID**: QUALITY_SCORING_SYSTEM_001
- **蓝图文档**: QUALITY_SCORING_SYSTEM_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾
åå»?
- **职责**: Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构
- **ç¶æ?*: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Quality Scoring System** | Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构 | **核心模块** |

### 1.3 版本管理

| çæ¬ | æ¥æ | åæ´å
å®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active

## 变更历史

| çæ¬ | æ¥æ | åæ´å
å®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 实施团队 |


---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-07 | **ç¶æ?*: Active
