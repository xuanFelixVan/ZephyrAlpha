---
module_id: QUALITY_SCORING_SYSTEM_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
---

# 数据质量评分系统蓝图

> 清风量化系统 v5.2 - 数据质量评分系统详细设计
> **模块ID**: `QUALITY_SCORING_SYSTEM_001`
> **实施周期**: Week 10（1周）
> **优先级**: P1（核心）
> **预期收益**: 量化数据质量，提供改进依据


## 一、设计背景与目标

### 1.1 业务需求

**当前痛点**:
- ❌ 缺少量化的数据质量评分
- ❌ 无法横向对比不同数据源的质量
- ❌ 缺少质量改进依据

**业务目标**:
- ✅ 建立多维度数据质量评分体系
- ✅ 自动计算数据质量评分
- ✅ 提供质量改进依据

### 1.2 技术目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **评分覆盖率** | ≥90% | 90%以上的数据有质量评分 |
| **评分准确性** | ≥85% | 评分与实际质量相符 |
| **评分更新频率** | 实时 | 评分实时更新 |

---

## 二、评分体系设计

### 2.1 评分维度

| 维度 | 权重 | 评分标准 | 计算方法 |
|------|------|---------|---------|
| **完整性** | 25% | 缺失值比例 | 1 - (缺失值数 / 总值数) |
| **准确性** | 25% | 异常值比例 | 1 - (异常值数 / 总值数) |
| **时效性** | 20% | 数据更新延迟 | max(0, 1 - 延迟时间 / 阈值) |
| **一致性** | 15% | 数据一致性 | 一致记录数 / 总记录数 |
| **有效性** | 15% | 格式正确率 | 格式正确数 / 总数 |

### 2.2 评分等级

| 评分范围 | 等级 | 说明 |
|---------|------|------|
| 90-100 | A+ | 优秀 |
| 80-89 | A | 良好 |
| 70-79 | B | 中等 |
| 60-69 | C | 及格 |
| 0-59 | D | 不及格 |

---

## 三、核心模块设计

### 3.1 质量评分器 (QualityScorer)

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime
import pandas as pd
import numpy as np

@dataclass
class QualityScore:
    """质量评分"""
    score_id: str
    data_source: str
    table_name: str
    overall_score: float
    dimension_scores: Dict[str, float]
    grade: str
    scored_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class QualityScorer:
    """质量评分器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化质量评分器
        
        Args:
            config: 配置信息
                - dimension_weights: 维度权重
                - thresholds: 阈值配置
        """
        self.config = config
        
        # 维度权重
        self.dimension_weights = config.get('dimension_weights', {
            'completeness': 0.25,
            'accuracy': 0.25,
            'timeliness': 0.20,
            'consistency': 0.15,
            'validity': 0.15
        })
        
    def calculate_completeness(
        self,
        data: pd.DataFrame
    ) -> float:
        """
        计算完整性评分
        
        Args:
            data: 数据DataFrame
            
        Returns:
            float: 完整性评分（0-1）
        """
        total_cells = data.size
        missing_cells = data.isnull().sum().sum()
        
        completeness = 1 - (missing_cells / total_cells)
        return completeness
    
    def calculate_accuracy(
        self,
        data: pd.DataFrame
    ) -> float:
        """
        计算准确性评分
        
        Args:
            data: 数据DataFrame
            
        Returns:
            float: 准确性评分（0-1）
        """
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return 1.0
        
        outlier_count = 0
        total_count = 0
        
        for col in numeric_cols:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = data[(data[col] < lower_bound) | (data[col] > upper_bound)]
            outlier_count += len(outliers)
            total_count += len(data)
        
        accuracy = 1 - (outlier_count / total_count) if total_count > 0 else 1.0
        return accuracy
    
    def calculate_timeliness(
        self,
        data: pd.DataFrame,
        timestamp_col: str,
        threshold_hours: int = 24
    ) -> float:
        """
        计算时效性评分
        
        Args:
            data: 数据DataFrame
            timestamp_col: 时间戳列名
            threshold_hours: 阈值小时数
            
        Returns:
            float: 时效性评分（0-1）
        """
        if timestamp_col not in data.columns:
            return 1.0
        
        latest_time = data[timestamp_col].max()
        current_time = datetime.now()
        
        delay_hours = (current_time - latest_time).total_seconds() / 3600
        
        timeliness = max(0, 1 - delay_hours / threshold_hours)
        return timeliness
    
    def calculate_consistency(
        self,
        data: pd.DataFrame,
        consistency_rules: Dict[str, Any]
    ) -> float:
        """
        计算一致性评分
        
        Args:
            data: 数据DataFrame
            consistency_rules: 一致性规则
            
        Returns:
            float: 一致性评分（0-1）
        """
        if not consistency_rules:
            return 1.0
        
        consistent_count = 0
        total_count = len(data)
        
        for rule_name, rule in consistency_rules.items():
            # 应用一致性规则
            pass
        
        consistency = consistent_count / total_count if total_count > 0 else 1.0
        return consistency
    
    def calculate_validity(
        self,
        data: pd.DataFrame,
        validity_rules: Dict[str, str]
    ) -> float:
        """
        计算有效性评分
        
        Args:
            data: 数据DataFrame
            validity_rules: 有效性规则（字段名 -> 正则表达式）
            
        Returns:
            float: 有效性评分（0-1）
        """
        import re
        
        if not validity_rules:
            return 1.0
        
        valid_count = 0
        total_count = 0
        
        for col, pattern in validity_rules.items():
            if col not in data.columns:
                continue
            
            for value in data[col]:
                if pd.isnull(value):
                    continue
                
                total_count += 1
                if re.match(pattern, str(value)):
                    valid_count += 1
        
        validity = valid_count / total_count if total_count > 0 else 1.0
        return validity
    
    def calculate_overall_score(
        self,
        dimension_scores: Dict[str, float]
    ) -> float:
        """
        计算总体评分
        
        Args:
            dimension_scores: 各维度评分
            
        Returns:
            float: 总体评分（0-100）
        """
        overall_score = 0.0
        
        for dimension, score in dimension_scores.items():
            weight = self.dimension_weights.get(dimension, 0)
            overall_score += score * weight
        
        # 转换为百分制
        return overall_score * 100
    
    def determine_grade(
        self,
        score: float
    ) -> str:
        """
        确定评分等级
        
        Args:
            score: 评分（0-100）
            
        Returns:
            str: 评分等级
        """
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"
    
    def score_data(
        self,
        data: pd.DataFrame,
        data_source: str,
        table_name: str,
        config: Dict[str, Any]
    ) -> QualityScore:
        """
        对数据进行质量评分
        
        Args:
            data: 数据DataFrame
            data_source: 数据源
            table_name: 表名
            config: 配置信息
            
        Returns:
            QualityScore: 质量评分
        """
        # 计算各维度评分
        dimension_scores = {
            'completeness': self.calculate_completeness(data),
            'accuracy': self.calculate_accuracy(data),
            'timeliness': self.calculate_timeliness(
                data,
                config.get('timestamp_col'),
                config.get('threshold_hours', 24)
            ),
            'consistency': self.calculate_consistency(
                data,
                config.get('consistency_rules', {})
            ),
            'validity': self.calculate_validity(
                data,
                config.get('validity_rules', {})
            )
        }
        
        # 计算总体评分
        overall_score = self.calculate_overall_score(dimension_scores)
        
        # 确定评分等级
        grade = self.determine_grade(overall_score)
        
        # 创建评分对象
        score = QualityScore(
            score_id=f"score_{data_source}_{table_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            data_source=data_source,
            table_name=table_name,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            grade=grade
        )
        
        return score
```

---

## 四、实施步骤

### 4.1 Week 10: 数据质量评分系统实施

#### Day 1-2: 评分模型开发

**任务**:
1. 实现QualityScorer质量评分器
2. 实现多维度评分计算
3. 编写单元测试

#### Day 3-4: 可视化开发

**任务**:
1. 实现评分可视化（Grafana）
2. 实现评分趋势图
3. 实现对比分析

#### Day 5: 集成与部署

**任务**:
1. 集成到现有系统
2. API服务开发
3. 部署上线

---

## 五、验收标准

### 5.1 功能验收

| 验收项 | 验收标准 | 验收方法 |
|--------|---------|---------|
| **评分覆盖率** | ≥90% | 配置检查 |
| **评分准确性** | ≥85% | 人工审核 |
| **评分更新频率** | 实时 | 功能测试 |

---

## 六、文档治理

**版本历史**:
- v1.0.0 (2026-04-02): 初始版本，完成数据质量评分系统设计

---

**蓝图版本**: v1.0 | **创建日期**: 2026-04-02 | **状态**: ✅ 正式 | **维护者**: ZephyrAlpha技术团队
