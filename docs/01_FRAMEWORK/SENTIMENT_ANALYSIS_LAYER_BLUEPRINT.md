---
module_id: LAYER_008
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席架构师
responsibility:
  - 提供sentiment analysis layer blueprint的完整架构设计、技术选型和实施路径规划
layer: Layer 4 (机器学习层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---
---


﻿---
module_id: SENTIMENT_ANALYSIS_LAYER_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-05
last_updated: 2026-04-05
owner: 首席架构师
layer: Layer 3 (舆情分析层)
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 3 - 舆情分析层
compliance_level: 顶级专业标准
reference_models: ["Two Sigma NLP", "Citadel Alternative Data", "Renaissance Sentiment Analysis"]
related_documents:
  - ARCHITECTURE.md
  - DATA_PREPROCESSING_LAYER_BLUEPRINT.md
  - NEWS_SENTIMENT_ANALYSIS_BLUEPRINT.md
parent_document: ../INDEX.md
implementation_status: 设计阶段
---
# Layer 3: 舆情分析层蓝图
> **核心职责**: 提供sentiment analysis layer blueprint的完整架构设计、技术选型和实施路径规划
> **职责边界**: 
> - ✅ 本文档负责：Sentiment Analysis Layer蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v1.0
> **创建日期**: 2026-04-05
> **实施周期**: 1周
> **目标**: 构建专业级舆情分析体系，对标Two Sigma、Citadel另类数据标准

---

## 📋 执行摘要

### 核心定位

Layer 3舆情分析层是清风量化系统的**信息情报中心**，负责：
- 新闻情感分析（财经新闻、公告解读）
- 社交媒体分析（雪球、东方财富股吧）
- 分析师预测整合（研报情感、评级变化）
- 舆情风险预警（负面舆情、异常波动）

### 个人使用价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评分 |
|---------|-------------|-------------|---------|
| **新闻情感** | 专业NLP团队 | FinBERT+规则引擎 | ⭐⭐⭐⭐⭐ |
| **社交媒体** | 社交媒体监控平台 | 雪球API+情感分析 | ⭐⭐⭐⭐ |
| **分析师预测** | Bloomberg分析师数据 | iFind研报数据 | ⭐⭐⭐⭐ |
| **舆情预警** | 实时监控系统 | AI预警+人工确认 | ⭐⭐⭐⭐ |

**综合价值评分**: ⭐⭐⭐⭐⭐ (5/5) - **强烈推荐实施**

---

## 一、架构设计

### 1.1 Layer 3整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                  Layer 3: 舆情分析层架构                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              3.1 新闻情感分析层                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 新闻采集器 (News Collector)                         │ │ │
│  │  │  ├── 财经新闻API                                  │ │ │
│  │  │  ├── 公告爬虫                                     │ │ │
│  │  │  ├── RSS订阅                                      │ │ │
│  │  │  └── 新闻去重                                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 情感分析器 (Sentiment Analyzer)                    │ │ │
│  │  │  ├── FinBERT模型                                  │ │ │
│  │  │  ├── 规则引擎                                     │ │ │
│  │  │  ├── 情感词典                                     │ │ │
│  │  │  └── 情感评分                                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 事件提取器 (Event Extractor)                       │ │ │
│  │  │  ├── NER实体识别                                  │ │ │
│  │  │  ├── 事件分类                                     │ │ │
│  │  │  ├── 影响评估                                     │ │ │
│  │  │  └── 关联股票                                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              3.2 社交媒体分析层                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 社交数据采集 (Social Data Collector)               │ │ │
│  │  │  ├── 雪球API                                      │ │ │
│  │  │  ├── 东方财富股吧                                 │ │ │
│  │  │  ├── 微博财经                                     │ │ │
│  │  │  └── 数据清洗                                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 舆情热度分析 (Sentiment Heat Analyzer)             │ │ │
│  │  │  ├── 讨论热度                                     │ │ │
│  │  │  ├── 情感倾向                                     │ │ │
│  │  │  ├── 关键意见领袖                                 │ │ │
│  │  │  └── 传播路径                                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              3.3 分析师预测层                             │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 研报数据采集 (Research Report Collector)           │ │ │
│  │  │  ├── iFind研报数据                                │ │ │
│  │  │  ├── 分析师评级                                   │ │ │
│  │  │  ├── 盈利预测                                     │ │ │
│  │  │  └── 目标价                                       │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 预测整合分析 (Forecast Integration)                │ │ │
│  │  │  ├── 一致预期                                     │ │ │
│  │  │  ├── 预测分歧                                     │ │ │
│  │  │  ├── 历史准确率                                   │ │ │
│  │  │  └── 预测调整                                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              3.4 舆情风险预警层                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 风险监控器 (Risk Monitor)                          │ │ │
│  │  │  ├── 负面舆情监控                                 │ │ │
│  │  │  ├── 异常波动检测                                 │ │ │
│  │  │  ├── 舆情趋势分析                                 │ │ │
│  │  │  └── 风险评分                                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 预警系统 (Alert System)                            │ │ │
│  │  │  ├── 实时预警                                     │ │ │
│  │  │  ├── 阈值告警                                     │ │ │
│  │  │  ├── 风险报告                                     │ │ │
│  │  │  └── 人工确认                                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责边界

| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |
|------|---------|------|------|---------|
| **新闻情感分析层** | 新闻情感分析 | 新闻文本 | 情感评分/事件 | 社交媒体分析层 |
| **社交媒体分析层** | 社交舆情分析 | 社交数据 | 热度/情感 | 分析师预测层 |
| **分析师预测层** | 预测数据整合 | 研报数据 | 一致预期 | 舆情风险预警层 |
| **舆情风险预警层** | 风险监控预警 | 舆情数据 | 风险报告 | Layer 4-5 |

---

## 二、核心组件详细设计

### 2.1 新闻情感分析层

#### 2.1.1 新闻采集器 (News Collector)

**核心职责**：
1. **多源新闻采集**：财经新闻API、公告爬虫、RSS订阅
2. **新闻去重**：基于标题和内容的去重
3. **新闻分类**：按行业、主题、重要性分类
4. **新闻存储**：结构化存储新闻数据

**技术实现**：

```python
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime

class NewsCollector:
    """新闻采集器"""
    
    def __init__(self):
        self.sources = {
            'sina_finance': 'https://finance.sina.com.cn',
            'eastmoney': 'https://www.eastmoney.com',
            'cls_cn': 'https://www.cls.cn'
        }
        self.seen_hashes = set()
        
    def collect_news(
        self,
        keywords: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """采集新闻"""
        
        all_news = []
        
        for source_name, source_url in self.sources.items():
            try:
                news = self._fetch_from_source(
                    source_name,
                    source_url,
                    keywords,
                    start_date,
                    end_date
                )
                all_news.extend(news)
            except Exception as e:
                print(f"Error fetching from {source_name}: {e}")
        
        deduplicated = self._deduplicate(all_news)
        
        return deduplicated
    
    def _fetch_from_source(
        self,
        source_name: str,
        source_url: str,
        keywords: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """从数据源获取新闻"""
        
        pass
    
    def _deduplicate(self, news_list: List[Dict]) -> List[Dict]:
        """去重"""
        
        unique_news = []
        for news in news_list:
            content_hash = self._compute_hash(news['title'] + news['content'])
            if content_hash not in self.seen_hashes:
                self.seen_hashes.add(content_hash)
                unique_news.append(news)
        
        return unique_news
    
    def _compute_hash(self, text: str) -> str:
        """计算文本哈希"""
        return hashlib.md5(text.encode()).hexdigest()
```

#### 2.1.2 情感分析器 (Sentiment Analyzer)

**核心职责**：
1. **FinBERT模型**：使用金融领域预训练模型
2. **规则引擎**：基于金融词典的规则匹配
3. **情感词典**：金融情感词典
4. **情感评分**：综合评分输出

**技术实现**：

```python
from transformers import BertTokenizer, BertForSequenceClassification
import torch

class SentimentAnalyzer:
    """情感分析器"""
    
    def __init__(self, model_path: str = 'yiyanghkust/finbert-tone'):
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.sentiment_dict = self._load_sentiment_dict()
        
    def analyze(self, text: str) -> Dict:
        """分析情感"""
        
        bert_score = self._analyze_with_bert(text)
        
        rule_score = self._analyze_with_rules(text)
        
        final_score = self._combine_scores(bert_score, rule_score)
        
        return {
            'text': text,
            'bert_sentiment': bert_score,
            'rule_sentiment': rule_score,
            'final_sentiment': final_score,
            'analyzed_at': datetime.now()
        }
    
    def _analyze_with_bert(self, text: str) -> Dict:
        """使用FinBERT分析"""
        
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)
            
        labels = ['negative', 'neutral', 'positive']
        scores = {
            label: prob.item()
            for label, prob in zip(labels, probabilities[0])
        }
        
        return scores
    
    def _analyze_with_rules(self, text: str) -> Dict:
        """使用规则分析"""
        
        positive_words = self.sentiment_dict['positive']
        negative_words = self.sentiment_dict['negative']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        total = positive_count + negative_count
        if total == 0:
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
        
        return {
            'positive': positive_count / total,
            'negative': negative_count / total,
            'neutral': 0.0
        }
    
    def _combine_scores(
        self,
        bert_score: Dict,
        rule_score: Dict
    ) -> Dict:
        """综合评分"""
        
        bert_weight = 0.7
        rule_weight = 0.3
        
        return {
            'positive': bert_score['positive'] * bert_weight + rule_score['positive'] * rule_weight,
            'negative': bert_score['negative'] * bert_weight + rule_score['negative'] * rule_weight,
            'neutral': bert_score['neutral'] * bert_weight + rule_score['neutral'] * rule_weight
        }
    
    def _load_sentiment_dict(self) -> Dict:
        """加载情感词典"""
        
        return {
            'positive': ['增长', '盈利', '利好', '上涨', '突破', '创新高'],
            'negative': ['亏损', '下跌', '利空', '暴跌', '风险', '违约']
        }
```

---

### 2.2 社交媒体分析层

#### 2.2.1 社交数据采集 (Social Data Collector)

**核心职责**：
1. **雪球API**：采集雪球讨论数据
2. **东方财富股吧**：采集股吧帖子
3. **微博财经**：采集微博财经话题
4. **数据清洗**：去除噪声数据

**技术实现**：

```python
import requests
import json

class SocialDataCollector:
    """社交数据采集器"""
    
    def __init__(self):
        self.xueqiu_api = 'https://xueqiu.com/statuses'
        self.eastmoney_api = 'https://guba.eastmoney.com'
        
    def collect_xueqiu(
        self,
        stock_code: str,
        limit: int = 100
    ) -> List[Dict]:
        """采集雪球数据"""
        
        try:
            url = f"{self.xueqiu_api}/original.json"
            params = {
                'symbol': stock_code,
                'count': limit
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            posts = []
            for item in data.get('list', []):
                posts.append({
                    'platform': 'xueqiu',
                    'stock_code': stock_code,
                    'user_id': item.get('user_id'),
                    'user_name': item.get('user').get('screen_name'),
                    'title': item.get('title'),
                    'content': item.get('text'),
                    'created_at': datetime.fromtimestamp(
                        item.get('created_at') / 1000
                    ),
                    'retweet_count': item.get('retweet_count'),
                    'reply_count': item.get('reply_count'),
                    'like_count': item.get('like_count')
                })
            
            return posts
        except Exception as e:
            print(f"Error collecting from Xueqiu: {e}")
            return []
    
    def collect_eastmoney(
        self,
        stock_code: str,
        limit: int = 100
    ) -> List[Dict]:
        """采集东方财富股吧数据"""
        
        pass
```

---

## 三、数据模型设计

### 3.1 核心数据模型

```python
@dataclass
class NewsData:
    """新闻数据"""
    news_id: str
    title: str
    content: str
    source: str
    published_at: datetime
    sentiment: str
    sentiment_score: float
    importance_score: float
    related_stocks: List[str]
    events: List[str]

@dataclass
class SocialMediaData:
    """社交媒体数据"""
    post_id: str
    platform: str
    stock_code: str
    user_id: str
    user_name: str
    content: str
    created_at: datetime
    sentiment: str
    engagement_metrics: Dict[str, int]

@dataclass
class AnalystForecast:
    """分析师预测"""
    stock_code: str
    analyst_name: str
    institution: str
    rating: str
    target_price: float
    eps_forecast: float
    report_date: datetime
    accuracy_score: float
```

---

## 四、实施路线

### 4.1 Phase 1: 新闻情感分析（Week 1）

**任务清单**：
- [ ] 实现新闻采集器
- [ ] 实现情感分析器
- [ ] 实现事件提取器
- [ ] 单元测试

---

### 4.2 Phase 2: 社交媒体分析（Week 1）

**任务清单**：
- [ ] 实现社交数据采集
- [ ] 实现舆情热度分析
- [ ] 实现关键意见领袖识别
- [ ] 集成测试

---

### 4.3 Phase 3: 分析师预测（Week 1）

**任务清单**：
- [ ] 实现研报数据采集
- [ ] 实现预测整合分析
- [ ] 实现历史准确率统计
- [ ] 性能测试

---

## 五、质量保证

### 5.1 测试策略

| 测试类型 | 覆盖率目标 | 测试工具 |
|---------|-----------|---------|
| **单元测试** | ≥90% | pytest |
| **集成测试** | ≥80% | pytest |
| **性能测试** | 关键路径 | locust |

---

## 六、成功指标

| 指标 | 目标值 |
|------|--------|
| **情感准确率** | ≥80% |
| **新闻覆盖率** | ≥90% |
| **处理速度** | ≤1秒/条新闻 |
| **预警及时性** | ≤5分钟 |

---

## 七、相关文档

| 文档 | 说明 |
|------|------|
| [NEWS_SENTIMENT_ANALYSIS_BLUEPRINT.md](#) | 新闻情感分析蓝图 |
| [DATA_PREPROCESSING_LAYER_BLUEPRINT.md](./DATA_PREPROCESSING_LAYER_BLUEPRINT.md) | 数据预处理层蓝图 |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 系统架构文档 |

---

**版本**: v1.0 | **更新**: 2026-04-05 | **状态**: 活跃
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 3: 舆情分析层
##### 0.001. Sentiment Analysis Layer Blueprint
- **模块ID**: SENTIMENT_ANALYSIS_LAYER_BLUEPRINT_001
- **蓝图文档**: [SENTIMENT_ANALYSIS_LAYER_BLUEPRINT.md](#)
- **技术规格书**: 待创建
- **职责**: Layer 3 - 舆情分析层
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Sentiment Analysis Layer Blueprint** | Layer 3 - 舆情分析层 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-05 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-05 | **状态**: Active
