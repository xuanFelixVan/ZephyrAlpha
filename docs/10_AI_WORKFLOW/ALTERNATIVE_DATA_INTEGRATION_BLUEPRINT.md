# 另类数据集成模块蓝图 (Alternative Data Integration Blueprint)

> **模块ID**: L3_ADI_001
> **版本**: v1.0
> **创建日期**: 2026-04-02
> **Layer定位**: Layer 3 - 舆情分析层
> **优先级**: P0 (阻断性)
> **预计工作量**: 40小时

---

## 一、模块概述

### 1.1 设计背景

**业务需求**:
- 扩展舆情分析数据源，从单一财经新闻扩展到社交媒体、经济数据、财务数据等多源数据
- 提升舆情分析的广度和深度
- 实现多维度舆情监控和分析

**技术痛点**:
- 当前数据源仅限于中文财经新闻（财联社、同花顺、新浪财经）
- 缺少社交媒体数据（Twitter、Reddit等）
- 缺少宏观经济数据（FRED等）
- 缺少财务数据（SEC EDGAR等）

**预期价值**:
- 数据覆盖率提升50%以上
- 实现全球舆情监控
- 提供宏观经济和财务数据支持
- 增强舆情分析的全面性和准确性

### 1.2 模块定位

**Layer归属**: Layer 3 - 舆情分析层
**模块类别**: 核心数据采集模块
**架构角色**: 数据源扩展组件，为情感分析和事件检测提供多源数据

---

## 二、详细架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                    另类数据集成模块架构                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          AlternativeDataIntegrator (主集成器)                 │  │
│  │  - 数据源管理                                                 │  │
│  │  - 数据采集调度                                               │  │
│  │  - 数据清洗标准化                                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ↓                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          数据源适配层                                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────┐ │  │
│  │  │TwitterAPI   │  │RedditAPI    │  │FREDAPI      │  │SEC   │ │  │
│  │  │Adapter      │  │Adapter      │  │Adapter      │  │EDGAR │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └──────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ↓                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          数据处理层                                           │  │
│  │  - 数据清洗 (DataCleaner)                                     │  │
│  │  - 数据标准化 (DataNormalizer)                                │  │
│  │  - 数据存储 (DataStorage)                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ↓                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          监控和管理                                           │  │
│  │  - 采集监控 (CollectionMonitor)                               │  │
│  │  - 质量检查 (QualityChecker)                                  │  │
│  │  - 告警推送 (AlertPusher)                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件设计

#### 2.2.1 Twitter API适配器

**功能**: 采集Twitter财经相关推文

**技术方案**:
- 使用Twitter API v2 (免费额度: 500,000推文/月)
- 关键词过滤: 股票代码、财经关键词
- 用户关注: 财经大V、机构账号

**数据字段**:
```python
{
    "tweet_id": "1234567890",
    "text": "推文内容",
    "user": {
        "id": "用户ID",
        "name": "用户名",
        "followers_count": 粉丝数
    },
    "created_at": "2026-04-02T10:00:00Z",
    "lang": "语言",
    "entities": {
        "hashtags": ["标签"],
        "symbols": ["$AAPL", "$TSLA"]
    },
    "public_metrics": {
        "like_count": 点赞数,
        "retweet_count": 转发数,
        "reply_count": 回复数
    }
}
```

**采集策略**:
- 实时流式采集: 使用Filtered Stream API
- 定时批量采集: 每小时采集热门推文
- 关键词监控: 监控特定股票代码和财经关键词

---

#### 2.2.2 Reddit API适配器

**功能**: 采集Reddit财经相关帖子

**技术方案**:
- 使用Reddit API (免费，无限制)
- 关注subreddit: r/wallstreetbets, r/stocks, r/investing
- 热帖监控: 监控热门帖子和评论

**数据字段**:
```python
{
    "post_id": "abc123",
    "title": "帖子标题",
    "selftext": "帖子内容",
    "author": "作者",
    "subreddit": "wallstreetbets",
    "created_utc": "2026-04-02T10:00:00Z",
    "score": 得分,
    "num_comments": 评论数,
    "upvote_ratio": 点赞比例
}
```

**采集策略**:
- 热帖采集: 每小时采集热门帖子
- 评论采集: 采集热门帖子的前100条评论
- 关键词监控: 监控特定股票代码和财经关键词

---

#### 2.2.3 FRED API适配器

**功能**: 采集美国宏观经济数据

**技术方案**:
- 使用FRED API (免费，无限制)
- 数据类型: GDP、失业率、通胀率、利率等
- 更新频率: 每日更新

**数据字段**:
```python
{
    "series_id": "GDP",
    "title": "国内生产总值",
    "observation_start": "2026-01-01",
    "observation_end": "2026-04-02",
    "frequency": "季度",
    "units": "十亿美元",
    "data": [
        {
            "date": "2026-01-01",
            "value": "25000.0"
        }
    ]
}
```

**采集策略**:
- 定时采集: 每日采集最新数据
- 历史数据: 一次性采集历史数据
- 数据更新: 监控数据发布时间表

---

#### 2.2.4 SEC EDGAR API适配器

**功能**: 采集美国上市公司财务数据

**技术方案**:
- 使用SEC EDGAR API (免费，限制: 10次请求/秒)
- 数据类型: 10-K年报、10-Q季报、8-K重大事件
- 更新频率: 每日更新

**数据字段**:
```python
{
    "cik": "0000320193",  # Apple Inc.
    "company_name": "Apple Inc.",
    "form_type": "10-K",
    "filed_at": "2026-04-02",
    "fiscal_year": "2025",
    "fiscal_period": "FY",
    "documents": [
        {
            "type": "10-K",
            "description": "年度报告",
            "url": "https://www.sec.gov/Archives/edgar/data/..."
        }
    ]
}
```

**采集策略**:
- 定时采集: 每日采集最新财报
- 事件驱动: 监控8-K重大事件
- 数据解析: 解析财报关键财务指标

---

### 2.3 数据处理流程

```
数据采集 → 数据清洗 → 数据标准化 → 数据存储 → 数据分发
    ↓           ↓           ↓           ↓           ↓
  原始数据    清洗后数据   标准化数据   存储数据   分发数据
```

**数据清洗**:
- 去除HTML标签
- 去除特殊字符
- 去除重复数据
- 填充缺失值

**数据标准化**:
- 统一时间格式 (ISO 8601)
- 统一货币单位 (USD)
- 统一语言编码 (UTF-8)
- 统一数据格式 (JSON)

**数据存储**:
- SQLite: 本地存储
- 分区存储: 按日期分区
- 索引优化: 建立时间、股票代码索引
- 压缩存储: 使用gzip压缩

---

## 三、接口定义

### 3.1 主接口类

```python
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import pandas as pd


@dataclass
class DataSourceConfig:
    """数据源配置"""
    source_type: str  # twitter, reddit, fred, sec
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    rate_limit: int = 100  # 每分钟请求限制
    enabled: bool = True


@dataclass
class DataCollectionResult:
    """数据采集结果"""
    source: str
    data_type: str
    records: List[Dict[str, Any]]
    collected_at: datetime
    success: bool
    error_message: Optional[str] = None


class AlternativeDataIntegrator:
    """另类数据集成主类"""
    
    def __init__(self, config: Dict[str, DataSourceConfig]):
        """初始化数据集成器
        
        Args:
            config: 数据源配置字典
        """
        self.config = config
        self.adapters = self._initialize_adapters()
        self.cleaner = DataCleaner()
        self.normalizer = DataNormalizer()
        self.storage = DataStorage()
        self.monitor = CollectionMonitor()
    
    def _initialize_adapters(self) -> Dict[str, Any]:
        """初始化数据源适配器"""
        adapters = {}
        for source_type, source_config in self.config.items():
            if source_type == "twitter":
                adapters[source_type] = TwitterAPIAdapter(source_config)
            elif source_type == "reddit":
                adapters[source_type] = RedditAPIAdapter(source_config)
            elif source_type == "fred":
                adapters[source_type] = FREDAPIAdapter(source_config)
            elif source_type == "sec":
                adapters[source_type] = SECEdgARAPIAdapter(source_config)
        return adapters
    
    def collect_data(
        self,
        source_type: str,
        params: Optional[Dict[str, Any]] = None
    ) -> DataCollectionResult:
        """采集数据
        
        Args:
            source_type: 数据源类型
            params: 采集参数
            
        Returns:
            数据采集结果
        """
        pass
    
    def collect_all_sources(self) -> List[DataCollectionResult]:
        """采集所有数据源
        
        Returns:
            所有数据源的采集结果列表
        """
        pass
    
    def clean_data(
        self,
        raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """清洗数据
        
        Args:
            raw_data: 原始数据
            
        Returns:
            清洗后的数据
        """
        pass
    
    def normalize_data(
        self,
        cleaned_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """标准化数据
        
        Args:
            cleaned_data: 清洗后的数据
            
        Returns:
            标准化后的数据
        """
        pass
    
    def store_data(
        self,
        normalized_data: List[Dict[str, Any]],
        source_type: str
    ) -> bool:
        """存储数据
        
        Args:
            normalized_data: 标准化后的数据
            source_type: 数据源类型
            
        Returns:
            存储是否成功
        """
        pass
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取采集统计信息
        
        Returns:
            采集统计信息
        """
        pass
```

### 3.2 数据源适配器接口

```python
from abc import ABC, abstractmethod


class DataSourceAdapter(ABC):
    """数据源适配器基类"""
    
    @abstractmethod
    def connect(self) -> bool:
        """连接数据源
        
        Returns:
            连接是否成功
        """
        pass
    
    @abstractmethod
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """采集数据
        
        Args:
            params: 采集参数
            
        Returns:
            采集的数据列表
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试连接
        
        Returns:
            连接是否正常
        """
        pass
    
    @abstractmethod
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """获取速率限制状态
        
        Returns:
            速率限制状态
        """
        pass


class TwitterAPIAdapter(DataSourceAdapter):
    """Twitter API适配器"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.client = None
    
    def connect(self) -> bool:
        """连接Twitter API"""
        pass
    
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """采集Twitter数据"""
        pass
    
    def collect_stream(self, keywords: List[str]) -> None:
        """实时流式采集"""
        pass


class RedditAPIAdapter(DataSourceAdapter):
    """Reddit API适配器"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.client = None
    
    def connect(self) -> bool:
        """连接Reddit API"""
        pass
    
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """采集Reddit数据"""
        pass
    
    def get_hot_posts(self, subreddit: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取热门帖子"""
        pass


class FREDAPIAdapter(DataSourceAdapter):
    """FRED API适配器"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.client = None
    
    def connect(self) -> bool:
        """连接FRED API"""
        pass
    
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """采集FRED数据"""
        pass
    
    def get_series_data(
        self,
        series_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """获取序列数据"""
        pass


class SECEdgARAPIAdapter(DataSourceAdapter):
    """SEC EDGAR API适配器"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.client = None
    
    def connect(self) -> bool:
        """连接SEC EDGAR API"""
        pass
    
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """采集SEC EDGAR数据"""
        pass
    
    def get_company_filings(
        self,
        cik: str,
        form_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """获取公司财报"""
        pass
```

---

## 四、数据模型

### 4.1 数据库表结构

#### Twitter数据表

```sql
CREATE TABLE twitter_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT UNIQUE NOT NULL,
    text TEXT NOT NULL,
    user_id TEXT NOT NULL,
    user_name TEXT NOT NULL,
    user_followers_count INTEGER,
    created_at TIMESTAMP NOT NULL,
    lang TEXT,
    hashtags TEXT,  -- JSON array
    symbols TEXT,   -- JSON array
    like_count INTEGER,
    retweet_count INTEGER,
    reply_count INTEGER,
    collected_at TIMESTAMP NOT NULL,
    INDEX idx_created_at (created_at),
    INDEX idx_user_id (user_id),
    INDEX idx_symbols (symbols)
);
```

#### Reddit数据表

```sql
CREATE TABLE reddit_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    selftext TEXT,
    author TEXT NOT NULL,
    subreddit TEXT NOT NULL,
    created_utc TIMESTAMP NOT NULL,
    score INTEGER,
    num_comments INTEGER,
    upvote_ratio REAL,
    collected_at TIMESTAMP NOT NULL,
    INDEX idx_created_utc (created_utc),
    INDEX idx_subreddit (subreddit),
    INDEX idx_score (score)
);
```

#### FRED数据表

```sql
CREATE TABLE fred_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id TEXT NOT NULL,
    title TEXT NOT NULL,
    observation_date DATE NOT NULL,
    value REAL NOT NULL,
    frequency TEXT,
    units TEXT,
    collected_at TIMESTAMP NOT NULL,
    UNIQUE(series_id, observation_date),
    INDEX idx_series_id (series_id),
    INDEX idx_observation_date (observation_date)
);
```

#### SEC EDGAR数据表

```sql
CREATE TABLE sec_edgar_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cik TEXT NOT NULL,
    company_name TEXT NOT NULL,
    form_type TEXT NOT NULL,
    filed_at DATE NOT NULL,
    fiscal_year INTEGER,
    fiscal_period TEXT,
    document_url TEXT,
    parsed_data TEXT,  -- JSON
    collected_at TIMESTAMP NOT NULL,
    INDEX idx_cik (cik),
    INDEX idx_form_type (form_type),
    INDEX idx_filed_at (filed_at)
);
```

---

## 五、实施计划

### 5.0 环境准备

#### 5.0.1 安装Python 3.9+环境

```bash
# Windows系统
# 下载Python 3.9+安装包
# https://www.python.org/downloads/

# 验证安装
python --version  # 应显示 Python 3.9.x 或更高版本

# 创建虚拟环境
python -m venv zephyr_env

# 激活虚拟环境
zephyr_env\Scripts\activate  # Windows
```

#### 5.0.2 安装必要的依赖库

```bash
# 安装核心依赖
pip install tweepy==4.14.0        # Twitter API
pip install praw==7.7.1            # Reddit API
pip install requests==2.31.0       # HTTP请求
pip install pandas==2.1.1          # 数据处理
pip install numpy==1.24.3          # 数值计算

# 安装数据库驱动
pip install psycopg2-binary==2.9.9  # PostgreSQL
pip install redis==5.0.1             # Redis

# 安装工具库
pip install python-dotenv==1.0.0    # 环境变量管理
pip install schedule==1.2.0         # 定时任务
pip install tqdm==4.66.1            # 进度条

# 生成requirements.txt
pip freeze > requirements.txt
```

#### 5.0.3 申请API密钥

**Twitter API申请**:
1. 访问 https://developer.twitter.com/
2. 申请Developer账号
3. 创建App并获取以下密钥：
   - API Key
   - API Secret Key
   - Bearer Token
   - Access Token
   - Access Token Secret

**Reddit API申请**:
1. 访问 https://www.reddit.com/prefs/apps
2. 创建App（script类型）
3. 获取以下信息：
   - Client ID
   - Client Secret
   - User Agent

**FRED API申请**:
1. 访问 https://fred.stlouisfed.org/docs/api/api_key.html
2. 申请API Key（免费）

**SEC EDGAR**:
- 无需API Key
- 需要设置User-Agent（邮箱地址）

#### 5.0.4 配置环境变量

创建 `.env` 文件：

```bash
# .env
# Twitter API
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent

# FRED API
FRED_API_KEY=your_fred_api_key

# SEC EDGAR
SEC_USER_AGENT=your_email@example.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/zephyr_alpha
REDIS_URL=redis://localhost:6379/0
```

**环境验证脚本**:

```python
# verify_environment.py
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("环境验证报告 - 另类数据集成模块")
print("=" * 60)

# 检查Twitter API
twitter_keys = [
    'TWITTER_BEARER_TOKEN',
    'TWITTER_API_KEY',
    'TWITTER_API_SECRET',
    'TWITTER_ACCESS_TOKEN',
    'TWITTER_ACCESS_TOKEN_SECRET'
]
print("\n🐦 Twitter API配置:")
for key in twitter_keys:
    value = os.getenv(key)
    status = "✅" if value else "❌"
    print(f"  {status} {key}: {'已配置' if value else '未配置'}")

# 检查Reddit API
reddit_keys = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT']
print("\n🔴 Reddit API配置:")
for key in reddit_keys:
    value = os.getenv(key)
    status = "✅" if value else "❌"
    print(f"  {status} {key}: {'已配置' if value else '未配置'}")

# 检查FRED API
print("\n📊 FRED API配置:")
fred_key = os.getenv('FRED_API_KEY')
status = "✅" if fred_key else "❌"
print(f"  {status} FRED_API_KEY: {'已配置' if fred_key else '未配置'}")

# 检查数据库
print("\n💾 数据库配置:")
db_url = os.getenv('DATABASE_URL')
redis_url = os.getenv('REDIS_URL')
status_db = "✅" if db_url else "❌"
status_redis = "✅" if redis_url else "❌"
print(f"  {status_db} DATABASE_URL: {'已配置' if db_url else '未配置'}")
print(f"  {status_redis} REDIS_URL: {'已配置' if redis_url else '未配置'}")

print("\n" + "=" * 60)
print("环境验证完成！")
print("=" * 60)
```

---

### 5.1 第1周: Twitter API集成

**任务清单**:
- [ ] 申请Twitter Developer账号
- [ ] 创建Twitter App并获取API密钥
- [ ] 开发TwitterAPIAdapter
- [ ] 实现推文采集功能
- [ ] 实现实时流式采集
- [ ] 开发推文情感分析
- [ ] 测试和验证

**交付物**:
- TwitterAPIAdapter代码
- Twitter数据采集脚本
- 测试报告

---

### 5.2 第2周: Reddit API集成

**任务清单**:
- [ ] 申请Reddit API账号
- [ ] 开发RedditAPIAdapter
- [ ] 实现帖子采集功能
- [ ] 实现评论采集功能
- [ ] 开发热帖监控
- [ ] 测试和验证

**交付物**:
- RedditAPIAdapter代码
- Reddit数据采集脚本
- 测试报告

---

### 5.3 第3周: FRED经济数据集成

**任务清单**:
- [ ] 申请FRED API Key
- [ ] 开发FREDAPIAdapter
- [ ] 实现经济数据采集
- [ ] 实现数据更新机制
- [ ] 开发经济指标监控
- [ ] 测试和验证

**交付物**:
- FREDAPIAdapter代码
- FRED数据采集脚本
- 测试报告

---

### 5.4 第4周: SEC EDGAR财务数据集成

**任务清单**:
- [ ] 学习SEC EDGAR API
- [ ] 开发SECEdgARAPIAdapter
- [ ] 实现财报采集功能
- [ ] 实现财报解析功能
- [ ] 开发财报事件检测
- [ ] 测试和验证

**交付物**:
- SECEdgARAPIAdapter代码
- SEC EDGAR数据采集脚本
- 测试报告

---

## 六、测试策略

### 6.1 单元测试

**测试范围**:
- 各数据源适配器的连接测试
- 数据采集功能测试
- 数据清洗功能测试
- 数据标准化功能测试
- 数据存储功能测试

**测试工具**:
- pytest
- unittest.mock (模拟API响应)

---

### 6.2 集成测试

**测试范围**:
- 端到端数据采集流程测试
- 多数据源并发采集测试
- 数据质量验证测试
- 性能测试

**测试数据**:
- 使用测试账号和测试数据
- 模拟API响应

---

### 6.3 性能测试

**测试指标**:
- 数据采集速度
- 数据处理速度
- 存储速度
- 内存使用

**性能目标**:
- Twitter: 1000条推文/分钟
- Reddit: 100个帖子/分钟
- FRED: 100个序列/分钟
- SEC EDGAR: 10个公司/分钟

---

## 七、风险管理

### 7.1 技术风险

| 风险项 | 概率 | 影响 | 缓解措施 |
|--------|------|------|----------|
| API接口变更 | 中 | 高 | 使用稳定API版本，建立监控 |
| API限流 | 高 | 中 | 实现速率限制，使用队列 |
| 数据质量问题 | 中 | 中 | 数据验证和清洗 |
| 网络故障 | 低 | 高 | 重试机制，备用数据源 |

### 7.2 成本风险

| 风险项 | 概率 | 影响 | 缓解措施 |
|--------|------|------|----------|
| API收费 | 低 | 中 | 使用免费额度，监控使用量 |
| 存储成本 | 低 | 低 | 数据压缩，定期清理 |
| 计算成本 | 低 | 低 | 优化算法，使用缓存 |

---

## 八、验收标准

### 8.1 功能验收

- [ ] Twitter API集成完成，能够采集推文数据
- [ ] Reddit API集成完成，能够采集帖子和评论
- [ ] FRED API集成完成，能够采集经济数据
- [ ] SEC EDGAR API集成完成，能够采集财报数据
- [ ] 数据清洗和标准化功能正常
- [ ] 数据存储功能正常
- [ ] 监控和告警功能正常

### 8.2 性能验收

- [ ] 数据采集速度达到目标
- [ ] 数据处理速度达到目标
- [ ] 存储速度达到目标
- [ ] 内存使用在合理范围内

### 8.3 质量验收

- [ ] 数据完整性 > 95%
- [ ] 数据准确性 > 95%
- [ ] 数据及时性 > 90%
- [ ] 系统稳定性 > 99%

---

## 九、相关文档

| 文档 | 说明 |
|------|------|
| [Layer 3改进实施计划](./LAYER3_IMPROVEMENT_IMPLEMENTATION_PLAN.md) | 总体实施计划 |
| [舆情分析层对比报告](./LAYER3_SENTIMENT_ANALYSIS_COMPARISON_REPORT.md) | 专业对比分析 |
| [架构定义](../01_FRAMEWORK/ARCHITECTURE.md) | 系统架构 |

---

**版本**: v1.0 | **更新**: 2026-04-02 | **状态**: ✅ 活跃
