---
module_id: SENTIMENT_ANALYZER_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席技术评审官
standard_type: 专业量化机构技术规格书
applicable_scope: Layer 3 舆情分析?| 业务架构: 三级时间框架融合架构
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行?
---

# SentimentAnalyzer情感分析模块技术规格书

> 清风量化系统 v5.3 - SentimentAnalyzer情感分析模块详细技术设?
> **模块ID**: `SENTIMENT_ANALYZER_001`
> **版本**: v1.0.0
> **状?*: ?正式


## 1. 概述

### 1.1 设计背景与业务目?
- **业务需?*: 系统需要专业的情感分析能力，量化新闻情绪、舆情方向、市场情绪等
- **技术痛?*: 
  - 新闻情感量化困难：缺乏标准化的情感评分体?
  - 情绪强度评估不足：无法准确判断市场情绪强?
  - 舆情覆盖度分析缺失：难以评估市场关注?
  - 关键词热度追踪不完善：无法及时发现主题热?
- **预期价?*: 
  - 建立标准化的新闻情感评分体系
  - 提供多维度的情绪强度评估
  - 实现舆情覆盖度和关注度分?
  - 支持关键词热度和主题追踪

### 1.2 技术定位与架构层归?
- **Layer定位**: Layer 3 - 舆情分析?(符合ARCHITECTURE.md定义)
- **模块类别**: 核心舆情分析模块
- **架构角色**: Layer 3分析组件，为因子层和策略层提供情感因?

### 1.3 版本信息
| 版本 | 日期 | 作?| 变更说明 | 状?|
|------|------|------|----------|------|
| v1.0.0 | 2026-04-02 | 首席技术评审官 | 初始版本 | Active |

---

## 2. 详细架构设计

### 2.1 系统架构?
```
┌─────────────────────────────────────────────────────────────?
?                   Layer 3: 舆情分析?                      ?
├─────────────────────────────────────────────────────────────?
?                                                            ?
? ┌──────────────────────────────────────────────────────? ?
? ?         SentimentAnalyzer (主情感分析器)             ? ?
? ? - 情感分析流程编排                                   ? ?
? ? - 情绪强度评估                                       ? ?
? ? - 情感报告生成                                       ? ?
? └──────────────────────────────────────────────────────? ?
?                          ?                                 ?
? ┌──────────────────────────────────────────────────────? ?
? ?         分析引擎?                                  ? ?
? ? ┌─────────────? ┌─────────────? ┌─────────────? ? ?
? ? │SentimentScorer?│IntensityAnalyzer?│KeywordTracker? ? ?
? ? └─────────────? └─────────────? └─────────────? ? ?
? └──────────────────────────────────────────────────────? ?
?                          ?                                 ?
? ┌──────────────────────────────────────────────────────? ?
? ?         支撑服务                                     ? ?
? ? - SentimentDictionary (情感词典)                    ? ?
? ? - NLPProcessor (NLP处理)                            ? ?
? ? - CoverageAnalyzer (覆盖度分?                     ? ?
? └──────────────────────────────────────────────────────? ?
?                                                            ?
└─────────────────────────────────────────────────────────────?
```

### 2.2 Layer定位详细说明
- **Layer归属**: Layer 3 - 舆情分析?
- **职责范围**: 负责新闻情感分析、情绪强度评估、舆情覆盖度分析、关键词热度追踪
- **上下层接?*: 
  - 上层依赖: Layer 2 Alpha因子?(提供情感因子)、Layer 5 策略执行?(提供情绪信号)
  - 下层依赖: Layer 3 新闻爬虫、事件检?(接收新闻数据)

### 2.3 模块职责与边界定?
- **核心职责**: 新闻情感分析、情绪强度评估、舆情覆盖度分析、关键词热度追踪
- **职责边界**: 
  - ?本模块负? 情感分析、情绪强度评估、覆盖度分析、关键词追踪
  - ?本模块不负责: 新闻爬取、事件检测、股票匹?
- **接口契约**: 提供统一的Python API接口

### 2.4 依赖关系
| 依赖模块 | 依赖类型 | 接口方式 | 版本要求 | 备注 |
|----------|----------|----------|----------|------|
| pandas | 强依?| Python?| >=1.3.0 | 数据处理核心 |
| numpy | 强依?| Python?| >=1.21.0 | 数值计?|
| jieba | 强依?| Python?| >=0.42.0 | 中文分词 |
| snownlp | 弱依?| Python?| >=0.12.0 | 情感分析 |

---

## 3. 接口定义

### 3.1 API接口规范

#### 3.1.1 主接口类
```python
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class SentimentConfig:
    """情感分析配置"""
    method: str
    dictionary_type: str
    intensity_threshold: float
    coverage_threshold: float


@dataclass
class SentimentResult:
    """情感分析结果"""
    sentiment_score: float
    sentiment_label: str
    intensity: float
    coverage: float
    keywords: List[str]
    confidence: float


class SentimentAnalyzer:
    """情感分析主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化情感分析器"""
        pass
    
    def calculate_sentiment_score(
        self,
        news_text: str,
        method: str = "dictionary"
    ) -> float:
        """计算新闻情感得分"""
        pass
    
    def calculate_news_intensity(
        self,
        news_list: List[str]
    ) -> Dict[str, Any]:
        """计算新闻情绪强度"""
        pass
    
    def analyze_stock_sentiment(
        self,
        stock_code: str,
        news_data: List[Dict[str, Any]]
    ) -> SentimentResult:
        """分析个股新闻情绪"""
        pass
    
    def calculate_coverage(
        self,
        stock_code: str,
        news_count: int,
        total_news: int
    ) -> float:
        """计算舆情覆盖?""
        pass
    
    def track_keywords(
        self,
        news_data: List[Dict[str, Any]],
        keywords: List[str]
    ) -> Dict[str, float]:
        """追踪关键词热?""
        pass
    
    def generate_sentiment_report(
        self,
        stock_code: str,
        news_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成情感分析报告"""
        pass
    
    def batch_analyze(
        self,
        news_batch: List[Dict[str, Any]]
    ) -> List[SentimentResult]:
        """批量情感分析"""
        pass


class NewsSentimentAnalyzer:
    """新闻情绪分析"""
    
    def __init__(self):
        self.sentiment_model = None
        self.keywords_positive = ['超预?, '突破', '增长', '龙头', '看好']
        self.keywords_negative = ['风险', '下调', '亏损', '利空', '警示']
    
    def calculate_sentiment_score(self, news_text: str) -> float:
        """计算新闻情感得分"""
        positive_count = sum(1 for kw in self.keywords_positive if kw in news_text)
        negative_count = sum(1 for kw in self.keywords_negative if kw in news_text)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def calculate_news_intensity(self, news_list: list) -> dict:
        """计算新闻情绪强度"""
        positive = sum(1 for n in news_list if self.calculate_sentiment_score(n) > 0)
        negative = sum(1 for n in news_list if self.calculate_sentiment_score(n) < 0)
        
        intensity = positive / (positive + negative) if (positive + negative) > 0 else 0.5
        
        return {
            'positive_count': positive,
            'negative_count': negative,
            'intensity': intensity,
            'sentiment': 'positive' if intensity > 0.6 else 'negative' if intensity < 0.4 else 'neutral'
        }
    
    def analyze_stock_news(self, stock_code: str, news_data: list) -> dict:
        """分析个股新闻情绪"""
        pass
```

### 3.2 性能指标要求
| 性能指标 | 目标?| 测量方法 |
|----------|--------|----------|
| 单条新闻情感分析时间 | < 50ms | 单条新闻处理 |
| 批量情感分析时间 | < 5?| 100条新闻批量处?|
| 情绪强度计算时间 | < 100ms | 单股票情绪强?|
| 关键词追踪时?| < 200ms | 10个关键词追踪 |
| 情感报告生成时间 | < 2?| 完整报告 |

### 3.3 安全机制
- **数据安全**: 情感分析不修改原始数?
- **结果验证**: 情感结果自动验证
- **日志审计**: 记录所有情感分析操?

---

## 4. 数据模型与存?

### 4.1 核心数据结构

#### 4.1.1 情感分析结果模型
```python
@dataclass
class SentimentAnalysisResult:
    """情感分析结果"""
    news_id: str
    sentiment_score: float
    sentiment_label: str
    confidence: float
    keywords: List[str]
    analysis_time: datetime
```

#### 4.1.2 情绪强度模型
```python
@dataclass
class IntensityResult:
    """情绪强度结果"""
    stock_code: str
    positive_count: int
    negative_count: int
    intensity: float
    sentiment: str
    analysis_date: datetime
```

#### 4.1.3 舆情覆盖度模?
```python
@dataclass
class CoverageResult:
    """舆情覆盖度结?""
    stock_code: str
    news_count: int
    total_news: int
    coverage_ratio: float
    attention_level: str
```

### 4.2 缓存策略
| 缓存类型 | TTL | 淘汰策略 | 最大容?|
|----------|-----|----------|----------|
| 情感分析结果缓存 | 24小时 | LRU | 10000?|
| 情绪强度缓存 | 1小时 | LRU | 5000?|
| 关键词热度缓?| 1小时 | LRU | 1000?|

### 4.3 数据持久?
- **持久化需?*: 情感分析结果、情绪强度需要持久化存储
- **存储格式**: JSON或Parquet格式

---

## 5. 算法实现说明

### 5.1 核心算法

#### 5.1.1 情感得分计算算法
```python
def calculate_sentiment_score(
    self, 
    news_text: str, 
    method: str = "dictionary"
) -> float:
    """
    情感得分计算算法
    
    算法原理:
    1. 文本预处理（分词、清洗）
    2. 情感词典匹配或NLP模型分析
    3. 计算情感得分
    
    复杂? O(n) n为文本长?
    """
    if method == "dictionary":
        positive_count = sum(1 for kw in self.keywords_positive if kw in news_text)
        negative_count = sum(1 for kw in self.keywords_negative if kw in news_text)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    elif method == "nlp":
        from snownlp import SnowNLP
        s = SnowNLP(news_text)
        return s.sentiments * 2 - 1
    else:
        raise ValueError(f"Unknown method: {method}")
```

#### 5.1.2 情绪强度计算算法
```python
def calculate_news_intensity(
    self, 
    news_list: List[str]
) -> Dict[str, Any]:
    """
    情绪强度计算算法
    
    算法原理:
    1. 计算每条新闻的情感得?
    2. 统计正面和负面新闻数?
    3. 计算情绪强度
    
    复杂? O(n) n为新闻数?
    """
    positive = sum(1 for n in news_list if self.calculate_sentiment_score(n) > 0)
    negative = sum(1 for n in news_list if self.calculate_sentiment_score(n) < 0)
    
    intensity = positive / (positive + negative) if (positive + negative) > 0 else 0.5
    
    return {
        'positive_count': positive,
        'negative_count': negative,
        'intensity': intensity,
        'sentiment': 'positive' if intensity > 0.6 else 'negative' if intensity < 0.4 else 'neutral'
    }
```

#### 5.1.3 舆情覆盖度计算算?
```python
def calculate_coverage(
    self, 
    stock_code: str, 
    news_count: int, 
    total_news: int
) -> float:
    """
    舆情覆盖度计算算?
    
    算法原理:
    1. 计算个股新闻占比
    2. 评估市场关注?
    
    复杂? O(1)
    """
    if total_news == 0:
        return 0.0
    
    coverage_ratio = news_count / total_news
    
    return coverage_ratio
```

---

## 6. 实施技术栈

### 6.1 语言与框?
| 技术选型 | 版本要求 | 用?| 选择理由 |
|----------|----------|------|----------|
| Python | >=3.8 | 主要开发语言 | 量化系统标准语言 |
| pandas | >=1.3.0 | 数据处理 | 数据分析标准?|
| numpy | >=1.21.0 | 数值计?| 高性能数值计?|
| jieba | >=0.42.0 | 中文分词 | 中文NLP标准?|
| snownlp | >=0.12.0 | 情感分析 | 中文情感分析?|

### 6.2 第三方依?
```yaml
requirements:
  - pandas>=1.3.0
  - numpy>=1.21.0
  - jieba>=0.42.0
  - snownlp>=0.12.0
```

---

## 7. 测试策略

### 7.1 单元测试
| 测试?| 测试内容 | 覆盖率目?|
|--------|----------|------------|
| 情感得分计算 | 情感得分正确?| 100% |
| 情绪强度计算 | 强度计算正确?| 100% |
| 覆盖度计?| 覆盖度正确?| 100% |
| 关键词追?| 追踪正确?| 100% |

### 7.2 集成测试
```python
def test_sentiment_analyzer_integration():
    """集成测试示例"""
    analyzer = SentimentAnalyzer()
    
    news_text = "公司业绩超预期，股价突破新高，市场看?
    score = analyzer.calculate_sentiment_score(news_text, method="dictionary")
    assert -1.0 <= score <= 1.0
    
    news_list = [
        "公司业绩超预?,
        "股价下跌风险增加",
        "市场看好公司发展"
    ]
    intensity = analyzer.calculate_news_intensity(news_list)
    assert 'intensity' in intensity
    assert 'sentiment' in intensity
```

---

## 8. 风险与约?

### 8.1 技术风?
| 风险ID | 风险描述 | 风险等级 | 缓解措施 |
|--------|----------|----------|----------|
| R001 | 情感词典覆盖不足 | P1 | 多词典融合、持续更?|
| R002 | NLP模型准确性不?| P1 | 多模型对比、人工验?|
| R003 | 中文分词准确?| P2 | 专业词典、自定义分词 |
| R004 | 计算性能瓶颈 | P2 | 并行计算、缓存优?|

### 8.2 约束条件
- **技术约?*: 依赖jieba、snownlp等中文NLP?
- **资源约束**: 内存使用<2GB（批量分析）
- **时间约束**: 预计开发时?小时
- **质量约束**: 情感分析准确率≥80%

---

## 9. 验收标准

### 9.1 功能验收标准
| 功能?| 验收标准 | 验证方法 |
|--------|----------|----------|
| 情感得分计算 | 得分范围[-1, 1] | 单元测试 |
| 情绪强度计算 | 强度范围[0, 1] | 单元测试 |
| 覆盖度计?| 覆盖度范围[0, 1] | 单元测试 |
| 关键词追?| 追踪结果正确 | 单元测试 |

### 9.2 性能验收标准
| 性能指标 | 验收标准 | 验证方法 |
|----------|----------|----------|
| 单条新闻情感分析时间 | < 50ms | 性能测试 |
| 批量情感分析时间 | < 5?| 性能测试 |

### 9.3 质量验收标准
| 质量指标 | 验收标准 | 验证方法 |
|----------|----------|----------|
| 情感分析准确?| ?80% | 质量检?|
| 测试覆盖?| ?90% | pytest-cov |

---

## 10. 实施路线?

### 10.1 Phase 1: 核心功能开?(2?
- **Day 1**: 情感得分计算、情绪强度计?
- **Day 2**: 覆盖度分析、关键词追踪、测?

---

## 附录

### A. 配置示例
```yaml
sentiment_analyzer:
  analysis:
    method: "dictionary"
    dictionary_type: "custom"
  
  intensity:
    positive_threshold: 0.6
    negative_threshold: 0.4
  
  coverage:
    high_threshold: 0.05
    medium_threshold: 0.02
  
  keywords:
    positive: ['超预?, '突破', '增长', '龙头', '看好']
    negative: ['风险', '下调', '亏损', '利空', '警示']
```

### B. 错误码定?
| 错误?| 错误类型 | 错误描述 | 处理方式 |
|--------|----------|----------|----------|
| ERR_SENT_001 | SentimentAnalysisError | 情感分析失败 | 记录日志，返回错?|
| ERR_SENT_002 | IntensityCalculationError | 强度计算失败 | 记录日志，返回错?|
| ERR_SENT_003 | CoverageCalculationError | 覆盖度计算失?| 记录日志，返回错?|
| ERR_SENT_004 | KeywordTrackingError | 关键词追踪失?| 记录日志，返回错?|

### C. 参考文?
- [架构定义](../../01_FRAMEWORK/ARCHITECTURE.md)
- [模块职责边界](../../01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md)
- [另类数据框架](../../02_FACTOR_LIBRARY/04_DATA_SOURCE/ALTERNATIVE_DATA.md)


**文档版本**: v1.0.0 | **创建日期**: 2026-04-02 | **维护?*: 舆情分析层负责人
