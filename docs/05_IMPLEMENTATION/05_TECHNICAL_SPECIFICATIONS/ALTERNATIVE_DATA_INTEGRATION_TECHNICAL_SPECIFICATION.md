---
module_id: ALT_DATA_SPEC_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席技术评审官
standard_type: 专业量化机构技术规格书
applicable_scope: Layer 2 Alpha因子层 - 另类数据源集成 | 业务架构: 三级时间框架融合架构
compliance_level: 专业标准
parent_document: ./ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md
implementation_status: 规划阶段
---

# 另类数据源集成技术规格书

> **规格书编号**: SPEC-ALT-DATA-2026-001
> **规格书版本**: v1.0
> **创建日期**: 2026-04-02
> **技术评审官**: 首席技术评审官
> **评审状态**: ✅ 已批准

---

## 📋 技术规格书概述

### 文档目的

本技术规格书详细定义了另类数据源集成项目的所有技术细节，包括架构设计、接口定义、数据模型、算法实现、测试策略等，为开发团队提供完整的技术指导。

### 适用范围

本规格书适用于：
- 数据工程师：数据源接入和数据采集
- NLP工程师：情感分析和事件提取
- 因子研究员：因子构建和验证
- 测试工程师：系统测试和质量保证

---

## 一、概述

### 1.1 设计背景

根据Layer 2 Alpha因子层技术评审结果，**数据源广度不足**是P0级阻断性风险。当前系统仅依赖iFinD、Baostock、AkShare三个数据源，缺少新闻、社交媒体、分析师预期等另类数据，严重限制了因子研究深度和原创性。

### 1.2 技术定位

**Layer定位**: Layer 2 - Alpha因子层（数据源扩展）

**技术成熟度**: 成熟（基于公开API和开源工具）

**实施复杂度**: 中等（需要NLP处理和因子构建）

### 1.3 版本信息

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-04-02 | 初始版本 | 首席技术评审官 |

---

## 二、详细架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                    另类数据源集成架构                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 1: 数据源层 (Data Sources)                                   │
│  ├── 新闻数据源                                                     │
│  │   ├── 财联社API (CailianNewsDataSource)                         │
│  │   ├── 新浪财经API (SinaFinanceDataSource)                       │
│  │   └── 东方财富API (EastMoneyDataSource)                         │
│  ├── 社交媒体数据源                                                 │
│  │   ├── 微博API (WeiboDataSource)                                 │
│  │   ├── 雪球网爬虫 (XueqiuDataSource)                             │
│  │   └── 东方财富股吧 (GubaDataSource)                             │
│  └── 分析师预期数据源                                               │
│      ├── 东方财富分析师预期 (AnalystExpectationDataSource)          │
│      └── 同花顺研报 (ResearchReportDataSource)                      │
│                                                                     │
│  Layer 2: 数据采集层 (Data Collection)                              │
│  ├── API适配器 (APIAdapter)                                        │
│  │   ├── 统一API调用接口                                           │
│  │   ├── 错误处理和重试机制                                         │
│  │   └── 频率限制控制                                               │
│  ├── 爬虫引擎 (CrawlerEngine)                                      │
│  │   ├── Scrapy框架                                                │
│  │   ├── Selenium动态页面                                          │
│  │   └── 反爬虫策略                                                 │
│  ├── 实时数据流 (DataStream)                                       │
│  │   ├── WebSocket连接                                             │
│  │   └── Kafka消息队列（可选）                                      │
│  └── 数据调度器 (DataScheduler)                                    │
│      ├── Apache Airflow                                            │
│      └── 定时任务管理                                               │
│                                                                     │
│  Layer 3: 数据处理层 (Data Processing)                              │
│  ├── 数据清洗 (DataCleaner)                                        │
│  │   ├── 去重、去噪                                                │
│  │   ├── 格式标准化                                                 │
│  │   └── 异常检测                                                   │
│  ├── NLP处理 (NLPProcessor)                                        │
│  │   ├── 情感分析 (SentimentAnalyzer)                              │
│  │   ├── 事件提取 (EventExtractor)                                 │
│  │   ├── 实体识别 (EntityRecognizer)                               │
│  │   └── 关系抽取 (RelationExtractor)                              │
│  └── 向量化 (Vectorizer)                                           │
│      ├── 文本向量化                                                 │
│      └── 向量存储                                                   │
│                                                                     │
│  Layer 4: 因子构建层 (Factor Construction)                          │
│  ├── 新闻因子 (NewsFactors)                                        │
│  │   ├── 情感因子 (SentimentFactor)                                │
│  │   ├── 事件驱动因子 (EventDrivenFactor)                          │
│  │   └── 热度因子 (HeatFactor)                                     │
│  ├── 情绪因子 (SentimentFactors)                                   │
│  │   ├── 市场情绪 (MarketSentimentFactor)                          │
│  │   └── 个股情绪 (StockSentimentFactor)                           │
│  ├── 预期因子 (ExpectationFactors)                                 │
│  │   ├── 预期差异因子 (ExpectationGapFactor)                       │
│  │   └── 评级变化因子 (RatingChangeFactor)                         │
│  └── 关注度因子 (AttentionFactors)                                 │
│      └── 社交媒体热度因子 (SocialHeatFactor)                        │
│                                                                     │
│  Layer 5: 因子管理层 (Factor Management)                            │
│  ├── 因子存储 (FactorStorage)                                      │
│  │   ├── SQLite数据库                                              │
│  │   └── ChromaDB向量数据库                                         │
│  ├── IC验证 (ICValidator)                                          │
│  │   ├── IC计算                                                    │
│  │   ├── ICIR计算                                                  │
│  │   └── 有效性检验                                                 │
│  ├── 因子监控 (FactorMonitor)                                      │
│  │   ├── 实时监控                                                   │
│  │   └── 衰减检测                                                   │
│  └── 因子注册 (FactorRegistry)                                     │
│      ├── 自动注册                                                   │
│      └── 元数据管理                                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Layer定位说明

| Layer | 定位 | 职责 | 技术栈 |
|-------|------|------|--------|
| **Layer 1** | 数据源层 | 提供原始数据 | 公开API、爬虫 |
| **Layer 2** | 数据采集层 | 数据采集和调度 | Requests、Scrapy、Airflow |
| **Layer 3** | 数据处理层 | 数据清洗和NLP处理 | GLM-4-Flash、正则表达式 |
| **Layer 4** | 因子构建层 | 因子计算和构建 | NumPy、Pandas |
| **Layer 5** | 因子管理层 | 因子存储和验证 | SQLite、ChromaDB |

### 2.3 模块职责边界

```
数据源层 → 数据采集层 → 数据处理层 → 因子构建层 → 因子管理层
    ↓           ↓           ↓           ↓           ↓
 原始数据    采集数据    清洗数据    因子数据    注册因子
```

**职责边界**:
- **数据源层**: 仅负责提供原始数据，不涉及数据处理
- **数据采集层**: 仅负责数据采集，不涉及业务逻辑
- **数据处理层**: 仅负责数据清洗和NLP处理，不涉及因子计算
- **因子构建层**: 仅负责因子计算，不涉及数据存储
- **因子管理层**: 仅负责因子存储和验证，不涉及因子计算

---

## 三、接口定义

### 3.1 数据源接口

#### 3.1.1 新闻数据源接口

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

class NewsDataSource(ABC):
    """新闻数据源基类"""
    
    @abstractmethod
    def get_realtime_news(self, limit: int = 100) -> List[Dict]:
        """
        获取实时新闻
        
        Args:
            limit: 返回新闻数量
            
        Returns:
            新闻列表，每个新闻包含：
            - news_id: 新闻ID
            - title: 标题
            - content: 内容
            - publish_time: 发布时间
            - source: 数据源
            - url: 链接
        """
        pass
    
    @abstractmethod
    def get_stock_news(self, 
                       stock_code: str, 
                       start_date: datetime, 
                       end_date: datetime) -> List[Dict]:
        """
        获取个股相关新闻
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            新闻列表
        """
        pass
    
    @abstractmethod
    def search_news(self, 
                    keyword: str, 
                    start_date: datetime, 
                    end_date: datetime) -> List[Dict]:
        """
        搜索新闻
        
        Args:
            keyword: 关键词
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            新闻列表
        """
        pass
```

#### 3.1.2 社交媒体数据源接口

```python
class SocialMediaDataSource(ABC):
    """社交媒体数据源基类"""
    
    @abstractmethod
    def get_stock_posts(self, 
                        stock_code: str, 
                        page: int = 1) -> List[Dict]:
        """
        获取股票相关讨论
        
        Args:
            stock_code: 股票代码
            page: 页码
            
        Returns:
            讨论列表，每个讨论包含：
            - post_id: 帖子ID
            - user_id: 用户ID
            - user_name: 用户名
            - content: 内容
            - publish_time: 发布时间
            - likes: 点赞数
            - comments: 评论数
            - reposts: 转发数
        """
        pass
    
    @abstractmethod
    def get_hot_topics(self) -> List[Dict]:
        """
        获取热门话题
        
        Returns:
            热门话题列表
        """
        pass
    
    @abstractmethod
    def get_user_posts(self, 
                       user_id: str, 
                       limit: int = 50) -> List[Dict]:
        """
        获取用户发布内容
        
        Args:
            user_id: 用户ID
            limit: 返回数量
            
        Returns:
            用户发布内容列表
        """
        pass
```

#### 3.1.3 分析师预期数据源接口

```python
class AnalystExpectationDataSource(ABC):
    """分析师预期数据源基类"""
    
    @abstractmethod
    def get_analyst_rating(self, stock_code: str) -> List[Dict]:
        """
        获取分析师评级
        
        Args:
            stock_code: 股票代码
            
        Returns:
            评级列表，每个评级包含：
            - analyst_name: 分析师姓名
            - institution: 机构名称
            - rating: 评级
            - target_price: 目标价
            - report_date: 报告日期
        """
        pass
    
    @abstractmethod
    def get_consensus_forecast(self, stock_code: str) -> Dict:
        """
        获取一致预期
        
        Args:
            stock_code: 股票代码
            
        Returns:
            一致预期数据：
            - eps_forecast: EPS预测
            - revenue_forecast: 营收预测
            - rating_consensus: 评级一致预期
        """
        pass
    
    @abstractmethod
    def get_rating_history(self, 
                          stock_code: str, 
                          start_date: datetime, 
                          end_date: datetime) -> List[Dict]:
        """
        获取评级历史
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            评级历史列表
        """
        pass
```

### 3.2 NLP处理接口

#### 3.2.1 情感分析接口

```python
class SentimentAnalyzer:
    """情感分析器"""
    
    def analyze_sentiment(self, text: str) -> float:
        """
        分析文本情感
        
        Args:
            text: 文本内容
            
        Returns:
            情感得分（-1到1）
            -1: 极度负面
            0: 中性
            1: 极度正面
        """
        pass
    
    def batch_analyze(self, texts: List[str]) -> List[float]:
        """
        批量情感分析
        
        Args:
            texts: 文本列表
            
        Returns:
            情感得分列表
        """
        pass
```

#### 3.2.2 事件提取接口

```python
class EventExtractor:
    """事件提取器"""
    
    def extract_events(self, text: str) -> Dict:
        """
        提取新闻事件
        
        Args:
            text: 新闻文本
            
        Returns:
            事件信息：
            - event_type: 事件类型
            - event_summary: 事件摘要
            - related_stocks: 相关股票
            - impact_level: 影响等级（高/中/低）
            - sentiment: 情感倾向（正面/负面/中性）
        """
        pass
```

#### 3.2.3 实体识别接口

```python
class EntityRecognizer:
    """实体识别器"""
    
    def extract_stocks(self, text: str) -> List[str]:
        """
        提取股票代码
        
        Args:
            text: 文本内容
            
        Returns:
            股票代码列表
        """
        pass
    
    def extract_companies(self, text: str) -> List[str]:
        """
        提取公司名称
        
        Args:
            text: 文本内容
            
        Returns:
            公司名称列表
        """
        pass
```

### 3.3 因子计算接口

#### 3.3.1 因子计算基类

```python
from abc import ABC, abstractmethod

class FactorCalculator(ABC):
    """因子计算基类"""
    
    @abstractmethod
    def calculate(self, 
                  stock_code: str, 
                  date: datetime, 
                  **kwargs) -> float:
        """
        计算因子值
        
        Args:
            stock_code: 股票代码
            date: 计算日期
            **kwargs: 其他参数
            
        Returns:
            因子值
        """
        pass
    
    @abstractmethod
    def batch_calculate(self, 
                       stock_codes: List[str], 
                       date: datetime) -> pd.Series:
        """
        批量计算因子
        
        Args:
            stock_codes: 股票代码列表
            date: 计算日期
            
        Returns:
            因子值序列（index=stock_code）
        """
        pass
    
    def get_factor_info(self) -> Dict:
        """
        获取因子信息
        
        Returns:
            因子信息：
            - factor_name: 因子名称
            - factor_type: 因子类型
            - description: 因子描述
            - update_frequency: 更新频率
            - data_window: 数据窗口
            - expected_ic: 预期IC
        """
        pass
```

#### 3.3.2 新闻因子接口

```python
class NewsSentimentFactor(FactorCalculator):
    """新闻情感因子"""
    
    def calculate(self, 
                  stock_code: str, 
                  date: datetime, 
                  window: int = 7) -> float:
        """
        计算新闻情感因子
        
        Args:
            stock_code: 股票代码
            date: 计算日期
            window: 时间窗口（天）
            
        Returns:
            因子值（-1到1）
        """
        pass

class EventDrivenFactor(FactorCalculator):
    """事件驱动因子"""
    
    def calculate(self, 
                  stock_code: str, 
                  date: datetime) -> float:
        """
        计算事件驱动因子
        
        Args:
            stock_code: 股票代码
            date: 计算日期
            
        Returns:
            因子值（事件影响得分）
        """
        pass

class NewsHeatFactor(FactorCalculator):
    """新闻热度因子"""
    
    def calculate(self, 
                  stock_code: str, 
                  date: datetime, 
                  window: int = 7) -> float:
        """
        计算新闻热度因子
        
        Args:
            stock_code: 股票代码
            date: 计算日期
            window: 时间窗口（天）
            
        Returns:
            因子值（热度得分）
        """
        pass
```

### 3.4 因子管理接口

#### 3.4.1 因子注册接口

```python
class FactorRegistry:
    """因子注册表"""
    
    def register_factor(self, 
                       factor_name: str,
                       factor_type: str,
                       calculator: FactorCalculator,
                       metadata: Dict) -> str:
        """
        注册因子
        
        Args:
            factor_name: 因子名称
            factor_type: 因子类型
            calculator: 因子计算器
            metadata: 因子元数据
            
        Returns:
            因子ID
        """
        pass
    
    def get_factor(self, factor_id: str) -> Dict:
        """
        获取因子信息
        
        Args:
            factor_id: 因子ID
            
        Returns:
            因子信息
        """
        pass
    
    def list_factors(self, factor_type: Optional[str] = None) -> List[Dict]:
        """
        列出因子
        
        Args:
            factor_type: 因子类型（可选）
            
        Returns:
            因子列表
        """
        pass
```

#### 3.4.2 IC验证接口

```python
class ICValidator:
    """IC验证器"""
    
    def calculate_ic(self, 
                     factor_values: pd.Series,
                     returns: pd.Series) -> float:
        """
        计算IC值
        
        Args:
            factor_values: 因子值序列
            returns: 收益率序列
            
        Returns:
            IC值
        """
        pass
    
    def calculate_icir(self, 
                      ic_series: pd.Series) -> float:
        """
        计算ICIR值
        
        Args:
            ic_series: IC时间序列
            
        Returns:
            ICIR值
        """
        pass
    
    def validate_factor(self, 
                       factor_values: pd.DataFrame,
                       returns: pd.DataFrame,
                       min_ic: float = 0.03,
                       min_icir: float = 1.0) -> Dict:
        """
        验证因子有效性
        
        Args:
            factor_values: 因子值（index=date, columns=stock_code）
            returns: 收益率（index=date, columns=stock_code）
            min_ic: 最小IC阈值
            min_icir: 最小ICIR阈值
            
        Returns:
            验证结果：
            - ic_mean: IC均值
            - icir: ICIR
            - ic_std: IC标准差
            - is_valid: 是否有效
        """
        pass
```

---

## 四、数据模型与存储

### 4.1 数据库表结构

#### 4.1.1 新闻数据表

```sql
CREATE TABLE news_data (
    news_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    publish_time TIMESTAMP NOT NULL,
    source TEXT NOT NULL,
    url TEXT,
    stock_codes TEXT,  -- JSON array
    sentiment REAL,
    event_type TEXT,
    event_summary TEXT,
    impact_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_publish_time ON news_data(publish_time);
CREATE INDEX idx_news_source ON news_data(source);
CREATE INDEX idx_news_sentiment ON news_data(sentiment);
CREATE INDEX idx_news_event_type ON news_data(event_type);
```

**字段说明**:
| 字段名 | 类型 | 说明 | 索引 |
|--------|------|------|------|
| news_id | TEXT | 新闻唯一ID（主键） | PRIMARY |
| title | TEXT | 新闻标题 | - |
| content | TEXT | 新闻正文 | - |
| publish_time | TIMESTAMP | 发布时间 | INDEX |
| source | TEXT | 数据来源 | INDEX |
| url | TEXT | 原文链接 | - |
| stock_codes | TEXT | 相关股票代码（JSON） | - |
| sentiment | REAL | 情感得分（-1到1） | INDEX |
| event_type | TEXT | 事件类型 | INDEX |
| event_summary | TEXT | 事件摘要 | - |
| impact_level | TEXT | 影响等级 | - |

---

#### 4.1.2 社交媒体数据表

```sql
CREATE TABLE social_posts (
    post_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,  -- weibo, xueqiu, guba
    user_id TEXT,
    user_name TEXT,
    content TEXT NOT NULL,
    publish_time TIMESTAMP NOT NULL,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    stock_codes TEXT,  -- JSON array
    sentiment REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_platform ON social_posts(platform);
CREATE INDEX idx_posts_publish_time ON social_posts(publish_time);
CREATE INDEX idx_posts_sentiment ON social_posts(sentiment);
CREATE INDEX idx_posts_user ON social_posts(user_id);
```

---

#### 4.1.3 分析师预期数据表

```sql
CREATE TABLE analyst_expectations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,
    analyst_name TEXT,
    institution TEXT,
    rating TEXT,
    target_price REAL,
    eps_forecast REAL,
    revenue_forecast REAL,
    report_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analyst_stock ON analyst_expectations(stock_code);
CREATE INDEX idx_analyst_date ON analyst_expectations(report_date);
CREATE INDEX idx_analyst_institution ON analyst_expectations(institution);
```

---

#### 4.1.4 因子数据表

```sql
CREATE TABLE alternative_factors (
    factor_id TEXT PRIMARY KEY,
    factor_name TEXT NOT NULL,
    factor_type TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    date DATE NOT NULL,
    factor_value REAL NOT NULL,
    data_source TEXT,
    calculation_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(factor_name, stock_code, date)
);

CREATE INDEX idx_factor_type ON alternative_factors(factor_type);
CREATE INDEX idx_factor_date ON alternative_factors(date);
CREATE INDEX idx_factor_stock ON alternative_factors(stock_code);
CREATE INDEX idx_factor_name ON alternative_factors(factor_name);
```

---

#### 4.1.5 因子元数据表

```sql
CREATE TABLE factor_metadata (
    factor_id TEXT PRIMARY KEY,
    factor_name TEXT NOT NULL UNIQUE,
    factor_type TEXT NOT NULL,
    description TEXT,
    update_frequency TEXT,  -- daily, weekly, monthly
    data_window INTEGER,
    expected_ic REAL,
    ic_mean REAL,
    icir REAL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metadata_type ON factor_metadata(factor_type);
CREATE INDEX idx_metadata_active ON factor_metadata(is_active);
```

---

### 4.2 向量数据库设计

#### 4.2.1 ChromaDB Collection设计

```python
from chromadb import Client
from chromadb.config import Settings

class VectorStore:
    """向量存储"""
    
    def __init__(self, persist_directory: str = "./data/vector_db"):
        self.client = Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        
        # 新闻向量集合
        self.news_collection = self.client.get_or_create_collection(
            name="news_vectors",
            metadata={"description": "新闻文本向量"}
        )
        
        # 社交媒体向量集合
        self.posts_collection = self.client.get_or_create_collection(
            name="posts_vectors",
            metadata={"description": "社交媒体文本向量"}
        )
```

#### 4.2.2 向量存储格式

**新闻向量**:
```python
{
    "id": "news_001",
    "embedding": [0.1, 0.2, ...],  # 768维向量
    "metadata": {
        "news_id": "news_001",
        "title": "新闻标题",
        "publish_time": "2026-04-02T10:00:00",
        "source": "cailian",
        "sentiment": 0.8
    },
    "document": "新闻正文内容"
}
```

**社交媒体向量**:
```python
{
    "id": "post_001",
    "embedding": [0.1, 0.2, ...],  # 768维向量
    "metadata": {
        "post_id": "post_001",
        "platform": "weibo",
        "publish_time": "2026-04-02T10:00:00",
        "likes": 100,
        "sentiment": 0.6
    },
    "document": "微博内容"
}
```

---

### 4.3 数据流设计

```
数据源 → 数据采集 → 数据清洗 → NLP处理 → 因子计算 → 因子存储
  ↓         ↓          ↓          ↓          ↓          ↓
原始数据  采集数据   清洗数据   结构化数据  因子数据   注册因子
```

**数据流转过程**:

1. **数据采集**: 从数据源获取原始数据
2. **数据清洗**: 去重、去噪、格式标准化
3. **NLP处理**: 情感分析、事件提取、实体识别
4. **因子计算**: 基于处理后的数据计算因子
5. **因子存储**: 存储因子数据和元数据
6. **因子注册**: 注册因子到因子库

---

## 五、算法实现说明

### 5.1 情感分析算法

#### 5.1.1 算法原理

使用GLM-4-Flash进行情感分析，通过Prompt Engineering引导模型输出情感得分。

#### 5.1.2 实现代码

```python
class SentimentAnalyzer:
    """情感分析器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "glm-4-flash"
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
    def analyze_sentiment(self, text: str) -> float:
        """
        分析文本情感
        
        Args:
            text: 文本内容
            
        Returns:
            情感得分（-1到1）
        """
        prompt = f"""
        请分析以下财经新闻的情感倾向，返回-1到1之间的情感得分：
        -1表示极度负面，0表示中性，1表示极度正面
        
        新闻内容：{text}
        
        请只返回情感得分数值，不要其他解释。
        """
        
        response = self._call_api(prompt)
        sentiment_score = float(response.strip())
        
        # 确保得分在[-1, 1]范围内
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        return sentiment_score
    
    def _call_api(self, prompt: str) -> str:
        """调用GLM-4 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        result = response.json()
        
        return result['choices'][0]['message']['content']
```

#### 5.1.3 复杂度分析

- **时间复杂度**: O(n)，其中n为文本长度
- **空间复杂度**: O(1)
- **API调用成本**: 0.1元/百万tokens

---

### 5.2 事件提取算法

#### 5.2.1 算法原理

使用GLM-4-Flash进行事件提取，识别新闻中的关键事件、影响等级和相关股票。

#### 5.2.2 实现代码

```python
class EventExtractor:
    """事件提取器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "glm-4-flash"
        self.event_types = [
            '业绩公告', '并购重组', '股权变动', '高管变动',
            '产品发布', '政策影响', '行业动态', '市场事件'
        ]
        
    def extract_events(self, text: str) -> Dict:
        """
        提取新闻事件
        
        Args:
            text: 新闻文本
            
        Returns:
            事件信息字典
        """
        prompt = f"""
        请从以下财经新闻中提取关键事件信息：
        
        新闻内容：{text}
        
        请返回JSON格式：
        {{
            "event_type": "事件类型（从以下选择：{', '.join(self.event_types)}）",
            "event_summary": "事件摘要（50字以内）",
            "related_stocks": ["相关股票代码"],
            "impact_level": "影响等级（高/中/低）",
            "sentiment": "情感倾向（正面/负面/中性）"
        }}
        
        只返回JSON，不要其他解释。
        """
        
        response = self._call_api(prompt)
        event_info = json.loads(response)
        
        return event_info
```

---

### 5.3 因子计算算法

#### 5.3.1 新闻情感因子算法

```python
class NewsSentimentFactor(FactorCalculator):
    """新闻情感因子"""
    
    def __init__(self, news_data_source, sentiment_analyzer):
        self.news_data_source = news_data_source
        self.sentiment_analyzer = sentiment_analyzer
        
    def calculate(self, 
                  stock_code: str, 
                  date: datetime, 
                  window: int = 7) -> float:
        """
        计算新闻情感因子
        
        算法步骤：
        1. 获取过去window天的相关新闻
        2. 计算每条新闻的情感得分
        3. 加权平均（近期新闻权重更高）
        
        Args:
            stock_code: 股票代码
            date: 计算日期
            window: 时间窗口（天）
            
        Returns:
            因子值（-1到1）
        """
        # 1. 获取过去window天的相关新闻
        start_date = date - timedelta(days=window)
        news_list = self.news_data_source.get_stock_news(
            stock_code, start_date, date
        )
        
        if not news_list:
            return 0.0
        
        # 2. 计算每条新闻的情感得分
        sentiments = []
        for news in news_list:
            if news.get('sentiment') is not None:
                sentiment = news['sentiment']
            else:
                sentiment = self.sentiment_analyzer.analyze_sentiment(
                    news['content']
                )
            sentiments.append(sentiment)
        
        # 3. 加权平均（近期新闻权重更高）
        weights = np.exp(np.linspace(-1, 0, len(sentiments)))
        weights = weights / weights.sum()
        
        factor_value = np.average(sentiments, weights=weights)
        
        return factor_value
```

**算法复杂度**:
- 时间复杂度: O(n)，其中n为新闻数量
- 空间复杂度: O(n)

---

#### 5.3.2 事件驱动因子算法

```python
class EventDrivenFactor(FactorCalculator):
    """事件驱动因子"""
    
    # 事件影响基准得分
    EVENT_IMPACT_MAP = {
        '业绩公告': 0.8,
        '并购重组': 0.9,
        '股权变动': 0.7,
        '高管变动': 0.5,
        '产品发布': 0.6,
        '政策影响': 0.8,
        '行业动态': 0.4,
        '市场事件': 0.3
    }
    
    def __init__(self, news_data_source, event_extractor):
        self.news_data_source = news_data_source
        self.event_extractor = event_extractor
        
    def calculate(self, stock_code: str, date: datetime) -> float:
        """
        计算事件驱动因子
        
        算法步骤：
        1. 获取近期重大事件
        2. 计算每个事件的影响得分
        3. 综合评估事件影响
        
        Args:
            stock_code: 股票代码
            date: 计算日期
            
        Returns:
            因子值（事件影响得分）
        """
        # 1. 获取近期重大事件
        start_date = date - timedelta(days=30)
        news_list = self.news_data_source.get_stock_news(
            stock_code, start_date, date
        )
        
        # 2. 提取事件信息
        events = []
        for news in news_list:
            if news.get('event_type'):
                event_info = {
                    'event_type': news['event_type'],
                    'impact_level': news.get('impact_level', '中'),
                    'sentiment': news.get('sentiment', '中性'),
                    'publish_time': news['publish_time']
                }
                events.append(event_info)
        
        if not events:
            return 0.0
        
        # 3. 计算事件影响得分
        impact_scores = []
        for event in events:
            # 基准得分
            base_score = self.EVENT_IMPACT_MAP.get(event['event_type'], 0.5)
            
            # 影响等级乘数
            level_multiplier = {'高': 1.0, '中': 0.6, '低': 0.3}.get(
                event['impact_level'], 0.6
            )
            
            # 情感乘数
            sentiment_multiplier = {'正面': 1.0, '负面': -1.0, '中性': 0.0}.get(
                event['sentiment'], 0.0
            )
            
            # 时间衰减（近期事件权重更高）
            days_ago = (date - event['publish_time']).days
            time_decay = np.exp(-days_ago / 30)  # 30天衰减周期
            
            # 综合得分
            score = base_score * level_multiplier * sentiment_multiplier * time_decay
            impact_scores.append(score)
        
        # 4. 综合评估
        factor_value = np.mean(impact_scores)
        
        return factor_value
```

---

## 六、实施技术栈

### 6.1 编程语言和框架

| 技术领域 | 技术选型 | 版本 | 说明 |
|---------|---------|------|------|
| **编程语言** | Python | 3.9+ | 主要开发语言 |
| **爬虫框架** | Scrapy | 2.11+ | 数据采集 |
| **动态页面** | Selenium | 4.15+ | JavaScript渲染 |
| **HTTP请求** | Requests | 2.31+ | API调用 |
| **数据处理** | Pandas | 2.1+ | 数据处理 |
| **数值计算** | NumPy | 1.26+ | 数值计算 |

### 6.2 第三方依赖

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| **chromadb** | 0.4.0+ | 向量数据库 |
| **zhipuai** | 2.0.0+ | GLM-4 API |
| **apache-airflow** | 2.7.0+ | 任务调度 |
| **redis** | 5.0.0+ | 缓存 |
| **sqlalchemy** | 2.0.0+ | ORM |

### 6.3 环境要求

| 环境 | 要求 |
|------|------|
| **操作系统** | Windows 10/11, Linux, macOS |
| **内存** | ≥8GB |
| **存储** | ≥50GB可用空间 |
| **网络** | 稳定的互联网连接 |

---

## 七、测试策略

### 7.1 单元测试

#### 7.1.1 测试范围

| 模块 | 测试内容 | 覆盖率目标 |
|------|---------|-----------|
| **数据采集** | API调用、数据解析 | >85% |
| **NLP处理** | 情感分析、事件提取 | >80% |
| **因子计算** | 因子计算逻辑 | >90% |
| **数据存储** | 数据库操作 | >85% |

#### 7.1.2 测试用例示例

```python
import pytest
from datetime import datetime

class TestNewsSentimentFactor:
    """新闻情感因子测试"""
    
    def test_calculate_with_positive_news(self):
        """测试正面新闻的因子计算"""
        factor = NewsSentimentFactor(mock_news_source, mock_sentiment_analyzer)
        
        # 模拟正面新闻
        mock_news_source.get_stock_news.return_value = [
            {
                'news_id': '001',
                'title': '利好消息',
                'content': '公司业绩大幅增长',
                'publish_time': datetime(2026, 4, 1),
                'sentiment': 0.8
            }
        ]
        
        factor_value = factor.calculate('000001.SZ', datetime(2026, 4, 2))
        
        assert factor_value > 0
        assert factor_value <= 1
    
    def test_calculate_with_no_news(self):
        """测试无新闻时的因子计算"""
        factor = NewsSentimentFactor(mock_news_source, mock_sentiment_analyzer)
        
        mock_news_source.get_stock_news.return_value = []
        
        factor_value = factor.calculate('000001.SZ', datetime(2026, 4, 2))
        
        assert factor_value == 0.0
```

---

### 7.2 集成测试

#### 7.2.1 测试场景

| 场景 | 测试内容 | 验收标准 |
|------|---------|---------|
| **数据采集流程** | 从数据源到数据库的完整流程 | 数据完整性>95% |
| **NLP处理流程** | 从原始文本到结构化数据 | 准确率>80% |
| **因子计算流程** | 从数据到因子的完整流程 | IC>0.03 |

---

### 7.3 性能测试

#### 7.3.1 性能指标

| 指标 | 目标值 | 测试方法 |
|------|--------|---------|
| **数据采集延迟** | <5分钟 | 压力测试 |
| **因子计算延迟** | <10秒 | 性能测试 |
| **并发处理能力** | >100请求/秒 | 并发测试 |

---

## 八、风险与约束

### 8.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| **API频率限制** | 中 | 高 | 请求队列、多账号轮换 |
| **数据质量不稳定** | 高 | 中 | 数据清洗、异常检测 |
| **NLP准确率不足** | 高 | 中 | 模型优化、人工标注 |
| **系统性能瓶颈** | 中 | 低 | 异步处理、缓存优化 |

### 8.2 实施风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| **进度延期** | 高 | 中 | 预留缓冲、并行开发 |
| **资源不足** | 中 | 低 | 优先级管理 |
| **需求变更** | 中 | 低 | 需求冻结 |

### 8.3 约束条件

1. **数据源约束**: 仅使用免费公开API
2. **成本约束**: 月成本<200元
3. **时间约束**: 8周内完成
4. **技术约束**: 使用现有技术栈

---

## 九、验收标准

### 9.1 功能验收

| 功能 | 验收标准 | 测试方法 |
|------|---------|---------|
| **数据采集** | 数据完整性>95% | 数据质量检查 |
| **NLP处理** | 情感分析准确率>80% | 人工标注验证 |
| **因子计算** | 因子数量≥8个 | 功能测试 |
| **IC验证** | IC均值>0.03 | 统计检验 |

### 9.2 性能验收

| 指标 | 目标值 | 测试方法 |
|------|--------|---------|
| **数据采集延迟** | <5分钟 | 性能测试 |
| **因子计算延迟** | <10秒 | 性能测试 |
| **系统可用性** | >99% | 监控统计 |

### 9.3 质量验收

| 指标 | 目标值 | 测试方法 |
|------|--------|---------|
| **代码覆盖率** | >80% | 单元测试 |
| **文档完整性** | 100% | 文档审查 |
| **系统稳定性** | >99% | 压力测试 |

---

## 十、实施路线图

### 10.1 Phase 1: 数据源接入（Week 1-3）

**目标**: 完成数据源接入和数据采集

**关键任务**:
1. 新闻数据源接入
2. 社交媒体数据源接入
3. 分析师预期数据源接入
4. 数据库表结构设计
5. 数据采集调度系统

**验收标准**:
- 至少3个数据源接入
- 数据质量>95%
- 定时采集正常运行

---

### 10.2 Phase 2: NLP处理（Week 4-5）

**目标**: 完成NLP处理模块

**关键任务**:
1. GLM-4-Flash API集成
2. 情感分析模块开发
3. 事件提取模块开发
4. 实体识别模块开发
5. 向量数据库集成

**验收标准**:
- 情感分析准确率>80%
- 事件提取完整
- 实体识别准确率>90%

---

### 10.3 Phase 3: 因子构建（Week 6-7）

**目标**: 完成因子构建和验证

**关键任务**:
1. 新闻因子构建
2. 情绪因子构建
3. 预期因子构建
4. 关注度因子构建
5. IC验证

**验收标准**:
- 至少8个因子
- IC均值>0.03
- 因子注册完成

---

### 10.4 Phase 4: 测试验证（Week 8）

**目标**: 完成系统测试和项目验收

**关键任务**:
1. 单元测试
2. 集成测试
3. 性能测试
4. 回测验证
5. 文档编写

**验收标准**:
- 所有测试通过
- 文档完整
- 项目交付

---

## 附录

### A. API文档

详见: [ALTERNATIVE_DATA_API_DOCUMENTATION.md](./ALTERNATIVE_DATA_API_DOCUMENTATION.md)

### B. 数据字典

详见: [ALTERNATIVE_DATA_DICTIONARY.md](./ALTERNATIVE_DATA_DICTIONARY.md)

### C. 测试报告

详见: [ALTERNATIVE_DATA_TEST_REPORT.md](./ALTERNATIVE_DATA_TEST_REPORT.md)

---

**技术规格书版本**: v1.0  
**创建日期**: 2026-04-02  
**评审状态**: ✅ 已批准  
**下一步行动**: 开始Phase 1实施
