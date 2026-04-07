---
module_id: EVENT_DETECTOR_TECHNICAL_SPECIFICATION
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: IMPL_EVENT_DETECTOR_TECH_SPEC_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席技术评审官
responsibility:
  - 技术规格定义与实施标准制定与实施标准
standard_type: 专业量化机构技术规格书
applicable_scope: Layer 3 舆情分析?| 业务架构: 三级时间框架融合架构
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
---


# EventDetector事件检测模块技术规格书

> 清风量化系统 v5.3 - EventDetector事件检测模块详细技术设?
> **模块ID**: `EVENT_DETECTOR_001`
> **版本**: v1.0.0
> **?*: ?正式


## 1. 概述

### 1.1 设计背景与业务目?
- **业务需?*: 系统需要专业的事件检测能力，从新闻文本中识别和分类财经事?
- **技术痛?*: 
  - 事件识别困难：缺乏统一的事件分类体?
  - 事件影响评估不足：难以量化事件对股价的影?
  - 事件关联分析缺失：无法识别事件之间的关联关系
  - 实时性要求高：需要快速识别和响应重要事件
- **预期?*: 
  - 建立统一的事件分类体?
  - 提供事件影响评估能力
  - 实现事件关联分析
  - 支持实时事件检测和预警

### 1.2 技术定位与架构层归?
- **Layer定位**: Layer 3 - 舆情分析?(符合ARCHITECTURE.md定义)
- **模块类别**: 核心分析模块
- **架构角色**: Layer 3事件分析组件，为策略执行层提供事件信?

### 1.3 版本信息
| 版本 | 日期 | ?| 变更说明 | ?|
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
? ?         EventDetector (主事件检测器)                  ? ?
? ? - 事件分类                                           ? ?
? ? - 事件抽取                                           ? ?
? ? - 影响评估                                           ? ?
? └──────────────────────────────────────────────────────? ?
?                          ?                                 ?
? ┌──────────────────────────────────────────────────────? ?
? ?         事件分析引擎                                 ? ?
? ? ┌─────────────? ┌─────────────? ┌─────────────? ? ?
? ? │EventClass   ? │EventExtract ? │ImpactAssess ? ? ?
? ? └─────────────? └─────────────? └─────────────? ? ?
? └──────────────────────────────────────────────────────? ?
?                          ?                                 ?
? ┌──────────────────────────────────────────────────────? ?
? ?         支撑服务                                     ? ?
? ? - EventPatternLib (事件模式?                      ? ?
? ? - ImpactModel (影响模型)                            ? ?
? ? - EventMonitor (事件监控)                           ? ?
? └──────────────────────────────────────────────────────? ?
?                                                            ?
└─────────────────────────────────────────────────────────────?
```

### 2.2 Layer定位详细说明
- **Layer归属**: Layer 3 - 舆情分析?
- **职责范围**: 负责事件分类、事件抽取、事件影响评估、事件关联分?
- **上下层接?*: 
  - 上层依赖: Layer 5 策略执行?(提供事件信号)
  - 下层依赖: Layer 3 新闻爬虫、情感分?(接收新闻数据)

### 2.3 模块职责与边界定?
- **核心职责**: 事件分类、事件抽取、事件影响评估、事件关联分?
- **职责边界**: 
  - ?本模块负? 事件分类、事件抽取、事件影响评估、事件关联分?
  - ?本模块不负责: 新闻爬取、情感分析、股票匹?
- **接口契约**: 提供统一的Python API接口

### 2.4 依赖关系
| 依赖模块 | 依赖类型 | 接口方式 | 版本要求 | 备注 |
|----------|----------|----------|----------|------|
| pandas | 强依?| Python?| >=1.3.0 | 数据处理核心 |
| numpy | 强依?| Python?| >=1.21.0 | 数值计?|
| jieba | 强依?| Python?| >=0.42.0 | 中文分词 |
| re | 强依?| Python标准?| - | 正则表达?|

---

## 3. 接口定义

### 3.1 API接口规范

#### 3.1.1 主接口类
```python
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import pandas as pd
import re


@dataclass
class EventConfig:
    """事件检测配?""
    event_types: List[str]
    detection_threshold: float
    impact_threshold: float
    enable_realtime: bool


@dataclass
class Event:
    """事件数据"""
    event_id: str
    event_type: str
    event_level: str
    title: str
    content: str
    keywords: List[str]
    mentioned_stocks: List[str]
    impact_score: float
    publish_time: datetime


class EventDetector:
    """事件检测主?""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化事件检测器"""
        pass
    
    def detect_event(
        self,
        news_text: str
    ) -> Optional[Event]:
        """检测事?""
        pass
    
    def classify_event(
        self,
        news_text: str
    ) -> str:
        """分类事件"""
        pass
    
    def extract_event_info(
        self,
        news_text: str,
        event_type: str
    ) -> Dict[str, Any]:
        """抽取事件信息"""
        pass
    
    def assess_event_impact(
        self,
        event: Event,
        stock_code: Optional[str] = None
    ) -> float:
        """评估事件影响"""
        pass
    
    def analyze_event_correlation(
        self,
        events: List[Event]
    ) -> Dict[str, List[str]]:
        """分析事件关联"""
        pass
    
    def batch_detect(
        self,
        news_list: List[str]
    ) -> List[Event]:
        """批量检?""
        pass
    
    def monitor_events(
        self
    ) -> Dict[str, Any]:
        """监控事件?""
        pass


class EventClassifier:
    """事件分类?""
    
    EVENT_PATTERNS = {
        '财报发布': {
            'keywords': ['财报', '业绩', '净利润', '营收', '每股收益'],
            'pattern': r'(财报|业绩|利润).*(发布|公告|显示)',
            'sentiment_impact': 'positive'
        },
        '分红送转': {
            'keywords': ['分红', '送股', '转增', '派息'],
            'pattern': r'(\d+)?\d+)|(\d+)?\d+)',
            'sentiment_impact': 'positive'
        },
        '并购重组': {
            'keywords': ['并购', '重组', '收购', '定增'],
            'pattern': r'(并购|重组|收购).*(完成|通过|公告)',
            'sentiment_impact': 'uncertain'
        },
        '政策利好': {
            'keywords': ['政策', '支持', '鼓励', '补贴', '规划'],
            'pattern': r'(支持|鼓励|补贴|政策).*(行业|产业|公司)',
            'sentiment_impact': 'positive'
        },
        '监管?: {
            'keywords': ['监管?, '问询?, '警示?, '处罚'],
            'pattern': r'(监管|问询|警示).*?,
            'sentiment_impact': 'negative'
        },
        '减持': {
            'keywords': ['减持', '卖出', '转让'],
            'pattern': r'(股东|高管|实际控制?.*(减持|卖出)',
            'sentiment_impact': 'negative'
        }
    }
    
    def classify_event(self, news: str) -> str:
        """识别事件类型"""
        text = news
        
        for event_type, config in self.EVENT_PATTERNS.items():
            keywords = config['keywords']
            pattern = config['pattern']
            
            if any(kw in text for kw in keywords):
                if re.search(pattern, text):
                    return event_type
        
        return '其他'
```

### 3.2 性能指标要求
| 性能指标 | 目标?| 测量方法 |
|----------|--------|----------|
| 单条检测时?| < 100ms | 单条新闻检?|
| 批量检测时?| < 5?| 100条新闻检?|
| 分类准确?| ?85% | 100条新闻分?|
| 影响评估准确?| ?80% | 100条事件评?|
| 监控响应时间 | < 1?| 事件状态查?|

### 3.3 安全机制
- **数据安全**: 事件数据不包含敏感信?
- **访问控制**: 事件检测接口需要认?
- **日志审计**: 记录所有事件检测操?

---

## 4. 数据模型与存?

### 4.1 核心数据结构

#### 4.1.1 事件数据模型
```python
@dataclass
class EventData:
    """事件数据模型"""
    event_id: str
    event_type: str
    event_level: str
    title: str
    content: str
    keywords: List[str]
    mentioned_stocks: List[str]
    mentioned_amount: float
    impact_score: float
    publish_time: datetime
    processed_time: datetime
```

#### 4.1.2 事件分类模型
```python
@dataclass
class EventCategory:
    """事件分类模型"""
    category_id: str
    category_name: str
    parent_category: str
    keywords: List[str]
    patterns: List[str]
    sentiment_impact: str
```

#### 4.1.3 事件影响模型
```python
@dataclass
class EventImpact:
    """事件影响模型"""
    event_id: str
    stock_code: str
    impact_score: float
    impact_direction: str
    confidence: float
    impact_duration: int
```

### 4.2 缓存策略
| 缓存类型 | TTL | 淘汰策略 | 最大容?|
|----------|-----|----------|----------|
| 事件数据缓存 | 24小时 | LRU | 10000?|
| 分类结果缓存 | 7?| LRU | 5000?|
| 影响评估缓存 | 1小时 | LRU | 1000?|

### 4.3 数据持久?
- **持久化需?*: 事件数据、分类结果需要持久化存储
- **存储格式**: JSON或Parquet格式

---

## 5. 算法实现说明

### 5.1 核心算法

#### 5.1.1 事件分类算法
```python
def classify_event(
    self, 
    news_text: str
) -> str:
    """
    事件分类算法
    
    算法原理:
    1. 关键词匹?
    2. 正则表达式匹?
    3. 返回事件类型
    
    复杂? O(n) n为关键词数量
    """
    for event_type, config in self.EVENT_PATTERNS.items():
        keywords = config['keywords']
        pattern = config['pattern']
        
        if any(kw in news_text for kw in keywords):
            if re.search(pattern, news_text):
                return event_type
    
    return '其他'
```

#### 5.1.2 事件抽取算法
```python
def extract_event_info(
    self, 
    news_text: str, 
    event_type: str
) -> Dict[str, Any]:
    """
    事件抽取算法
    
    算法原理:
    1. 识别事件类型
    2. 提取关键信息
    3. 结构化输?
    
    复杂? O(n) n为文本长?
    """
    event_info = {
        'event_type': event_type,
        'keywords': [],
        'mentioned_stocks': [],
        'mentioned_amount': 0.0
    }
    
    config = self.EVENT_PATTERNS.get(event_type, {})
    keywords = config.get('keywords', [])
    
    for kw in keywords:
        if kw in news_text:
            event_info['keywords'].append(kw)
    
    stock_pattern = r'([0-9]{6}\.[A-Z]{2}|[A-Z]{2}[0-9]{6})'
    stocks = re.findall(stock_pattern, news_text)
    event_info['mentioned_stocks'] = stocks
    
    amount_pattern = r'(\d+\.?\d*)\s*(亿|万|千万)'
    amounts = re.findall(amount_pattern, news_text)
    if amounts:
        event_info['mentioned_amount'] = float(amounts[0][0])
    
    return event_info
```

#### 5.1.3 影响评估算法
```python
def assess_event_impact(
    self, 
    event: Event, 
    stock_code: Optional[str] = None
) -> float:
    """
    影响评估算法
    
    算法原理:
    1. 基于事件类型评估
    2. 基于关键词强度评?
    3. 基于历史数据评估
    
    复杂? O(1)
    """
    config = self.EVENT_PATTERNS.get(event.event_type, {})
    sentiment_impact = config.get('sentiment_impact', 'neutral')
    
    base_score = {
        'positive': 0.7,
        'negative': -0.7,
        'uncertain': 0.0,
        'neutral': 0.0
    }.get(sentiment_impact, 0.0)
    
    keyword_boost = len(event.keywords) * 0.05
    
    impact_score = base_score + keyword_boost
    
    return max(-1.0, min(1.0, impact_score))
```

---

## 6. 实施技术栈

### 6.1 语言与框?
| 技术选型 | 版本要求 | ?| 选择理由 |
|----------|----------|------|----------|
| Python | >=3.8 | 主要开发语言 | 量化系统标准语言 |
| pandas | >=1.3.0 | 数据处理 | 数据分析标准?|
| numpy | >=1.21.0 | 数值计?| 科学计算基础?|
| jieba | >=0.42.0 | 中文分词 | 中文NLP基础?|
| re | - | 正则表达?| Python标准?|

### 6.2 第三方依?
```yaml
requirements:
  - pandas>=1.3.0
  - numpy>=1.21.0
  - jieba>=0.42.0
```

---

## 7. 测试策略

### 7.1 单元测试
| 测试?| 测试内容 | 覆盖率目?|
|--------|----------|------------|
| 事件分类 | 分类正确?| 100% |
| 事件抽取 | 抽取正确?| 100% |
| 影响评估 | 评估正确?| 100% |
| 事件监控 | 监控正确?| 100% |

### 7.2 集成测试
```python
def test_event_detector_integration():
    """集成测试示例"""
    detector = EventDetector()
    
    news = "某公司发?025年财报，净利润同比增长50%"
    event = detector.detect_event(news)
    
    assert event is not None
    assert event.event_type == "财报发布"
    assert len(event.keywords) > 0
```

---

## 8. 风险与约?

### 8.1 技术风?
| 风险ID | 风险描述 | 风险等级 | 缓解措施 |
|--------|----------|----------|----------|
| R001 | 分类准确率不?| P1 | 多种分类方法交叉验证 |
| R002 | 影响评估偏差 | P1 | 历史数据验证、模型优?|
| R003 | 实时性不?| P2 | 性能优化、并行处?|
| R004 | 新事件类型识?| P2 | 动态扩展事件模式库 |

### 8.2 约束条件
- **技术约?*: 依赖jieba分词、re正则表达?
- **资源约束**: 内存使用<1GB（批量检测）
- **时间约束**: 预计开发时?5小时
- **质量约束**: 分类准确率≥85%

---

## 9. 验收标准

### 9.1 功能验收标准
| 功能?| 验收标准 | 验证方法 |
|--------|----------|----------|
| 事件分类 | 分类正确 | 单元测试 |
| 事件抽取 | 抽取正确 | 单元测试 |
| 影响评估 | 评估正确 | 单元测试 |
| 事件监控 | 监控正确 | 单元测试 |

### 9.2 性能验收标准
| 性能指标 | 验收标准 | 验证方法 |
|----------|----------|----------|
| 单条检测时?| < 100ms | 性能测试 |
| 分类准确?| ?85% | 性能测试 |

### 9.3 质量验收标准
| 质量指标 | 验收标准 | 验证方法 |
|----------|----------|----------|
| 分类准确?| ?85% | 质量检?|
| 测试覆盖?| ?90% | pytest-cov |

---

## 10. 实施路线?

### 10.1 Phase 1: 核心功能开?(2?
- **Day 1**: 事件分类、事件抽?
- **Day 2**: 影响评估、测试、优?

---

## 附录

### A. 配置示例
```yaml
event_detector:
  event_types:
    - "财报发布"
    - "分红送转"
    - "并购重组"
    - "政策利好"
    - "监管?
    - "减持"
  
  detection:
    threshold: 0.5
    enable_realtime: true
  
  impact:
    threshold: 0.3
    duration_days: 5
```

### B. 错误码定?
| 错误?| 错误类型 | 错误描述 | 处理方式 |
|--------|----------|----------|----------|
| ERR_EVENT_001 | ClassifyError | 分类失败 | 记录日志，返回错?|
| ERR_EVENT_002 | ExtractError | 抽取失败 | 记录日志，返回错?|
| ERR_EVENT_003 | ImpactError | 评估失败 | 记录日志，返回错?|
| ERR_EVENT_004 | MonitorError | 监控失败 | 记录日志，返回错?|

### C. 参考文?
- [架构定义](../../01_FRAMEWORK/ARCHITECTURE.md)
- [模块职责边界](../../01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md)
- [事件总线设计](../../04_EXECUTION/01_EVENT_ENGINE/EVENT_BUS.md)


**文档版本**: v1.0.0 | **创建日期**: 2026-04-02 | **维护?*: 舆情分析层负责人
