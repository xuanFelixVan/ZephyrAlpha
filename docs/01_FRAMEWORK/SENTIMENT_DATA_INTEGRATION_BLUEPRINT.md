---
module_id: SENTIMENT_DATA_INTEGRATION_BLUEPRINT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: SENTIMENT_DATA_INTEGRATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席架构师
layer: Layer 3 (策略层)
standard_type: 专业量化机构级蓝图
applicable_scope: 舆情数据源集成模块
compliance_level: 顶级专业标准
reference_models: ["Bloomberg Terminal", "Refinitiv", "Wind"]
responsibility:
  - 数据管理架构设计与实施规范与优化维护

---
---

# 舆情数据源集成蓝图
> **核心职责**: Sentiment Data Integration蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Sentiment Data Integration蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v1.0  
> **创建日期**: 2026-04-07  
> **优先级**: P0级核心模块  
> **实施周期**: 2周

---

## 一、模块概述

### 1.1 核心定位

舆情数据源集成模块负责整合多源舆情数据，包括新闻、社交媒体、研报、公告等，为舆情分析提供统一的数据接入层。

### 1.2 业务价值

| 价值维度 | 说明 |
|---------|------|
| **数据整合** | 统一接入多源舆情数据，避免数据孤岛 |
| **实时性** | 实时获取舆情信息，快速响应市场变化 |
| **数据质量** | 标准化数据格式，提升数据质量 |
| **成本优化** | 智能选择数据源，优化数据成本 |

### 1.3 技术选型

| 组件 | 方案 | 开源项目 | Stars | 替代率 |
|------|------|---------|-------|--------|
| 新闻爬虫 | Scrapy | scrapy | 50k+ | 70% |
| 社交媒体API | Tweepy | tweepy | 10k+ | 80% |
| 数据清洗 | BeautifulSoup | beautifulsoup4 | 30k+ | 85% |
| 消息队列 | RabbitMQ | rabbitmq | 12k+ | 90% |

---

## 二、架构设计

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────┐
│            舆情数据源集成架构                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ 新闻源    │  │ 社交媒体 │  │ 研报数据 │  │ 公告数据 ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
│       │              │              │              │     │
│       └──────────────┼──────────────┼──────────────┘     │
│                      │              │                    │
│              ┌───────▼──────────────▼───────┐            │
│              │     数据采集层               │            │
│              └───────┬──────────────┬───────┘            │
│                      │              │                    │
│              ┌───────▼──────────────▼───────┐            │
│              │     数据清洗层               │            │
│              └───────┬──────────────┬───────┘            │
│                      │              │                    │
│              ┌───────▼──────────────▼───────┐            │
│              │     数据存储层               │            │
│              └──────────────────────────────┘            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

#### 2.2.1 数据采集器

```python
import scrapy
from scrapy.crawler import CrawlerProcess
from typing import List, Dict, Optional
import tweepy
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pandas as pd

class SentimentDataCollector:
    """舆情数据采集器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.news_sources = config.get('news_sources', [])
        self.social_media_config = config.get('social_media', {})
        self.research_sources = config.get('research_sources', [])
        
    def collect_news(self, 
                    keywords: List[str],
                    start_date: str,
                    end_date: str) -> pd.DataFrame:
        """采集新闻数据"""
        
        news_data = []
        
        for source in self.news_sources:
            if source['type'] == 'rss':
                news_data.extend(self._collect_rss_news(source, keywords))
            elif source['type'] == 'web':
                news_data.extend(self._collect_web_news(source, keywords))
        
        df = pd.DataFrame(news_data)
        
        if not df.empty:
            df = df[(df['publish_time'] >= start_date) & 
                   (df['publish_time'] <= end_date)]
        
        return df
    
    def _collect_rss_news(self, source: Dict, keywords: List[str]) -> List[Dict]:
        """采集RSS新闻"""
        
        import feedparser
        
        news_items = []
        
        try:
            feed = feedparser.parse(source['url'])
            
            for entry in feed.entries:
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                
                if any(keyword in title or keyword in summary for keyword in keywords):
                    news_items.append({
                        'source': source['name'],
                        'title': title,
                        'content': summary,
                        'publish_time': entry.get('published', ''),
                        'url': entry.get('link', ''),
                        'type': 'news'
                    })
        except Exception as e:
            print(f"Error collecting RSS news from {source['name']}: {e}")
        
        return news_items
    
    def _collect_web_news(self, source: Dict, keywords: List[str]) -> List[Dict]:
        """采集网页新闻"""
        
        news_items = []
        
        try:
            response = requests.get(source['url'], headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all(source.get('article_tag', 'article'))
            
            for article in articles:
                title_tag = article.find(source.get('title_tag', 'h2'))
                content_tag = article.find(source.get('content_tag', 'p'))
                
                if title_tag and content_tag:
                    title = title_tag.get_text(strip=True)
                    content = content_tag.get_text(strip=True)
                    
                    if any(keyword in title or keyword in content for keyword in keywords):
                        news_items.append({
                            'source': source['name'],
                            'title': title,
                            'content': content,
                            'publish_time': datetime.now().isoformat(),
                            'url': source['url'],
                            'type': 'news'
                        })
        except Exception as e:
            print(f"Error collecting web news from {source['name']}: {e}")
        
        return news_items
    
    def collect_social_media(self,
                           keywords: List[str],
                           platforms: List[str] = ['twitter'],
                           limit: int = 100) -> pd.DataFrame:
        """采集社交媒体数据"""
        
        social_data = []
        
        if 'twitter' in platforms:
            social_data.extend(self._collect_twitter(keywords, limit))
        
        df = pd.DataFrame(social_data)
        return df
    
    def _collect_twitter(self, keywords: List[str], limit: int) -> List[Dict]:
        """采集Twitter数据"""
        
        twitter_data = []
        
        try:
            auth = tweepy.OAuthHandler(
                self.social_media_config['twitter']['consumer_key'],
                self.social_media_config['twitter']['consumer_secret']
            )
            auth.set_access_token(
                self.social_media_config['twitter']['access_token'],
                self.social_media_config['twitter']['access_token_secret']
            )
            
            api = tweepy.API(auth, wait_on_rate_limit=True)
            
            query = ' OR '.join(keywords)
            tweets = tweepy.Cursor(api.search_tweets, q=query, lang='zh').items(limit)
            
            for tweet in tweets:
                twitter_data.append({
                    'source': 'twitter',
                    'title': f"@{tweet.user.screen_name}",
                    'content': tweet.text,
                    'publish_time': tweet.created_at.isoformat(),
                    'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                    'type': 'social_media',
                    'user': tweet.user.screen_name,
                    'followers': tweet.user.followers_count,
                    'retweets': tweet.retweet_count,
                    'likes': tweet.favorite_count
                })
        except Exception as e:
            print(f"Error collecting Twitter data: {e}")
        
        return twitter_data
    
    def collect_research_reports(self,
                                stock_codes: List[str],
                                start_date: str,
                                end_date: str) -> pd.DataFrame:
        """采集研报数据"""
        
        research_data = []
        
        for source in self.research_sources:
            if source['type'] == 'api':
                research_data.extend(self._collect_api_research(source, stock_codes))
            elif source['type'] == 'web':
                research_data.extend(self._collect_web_research(source, stock_codes))
        
        df = pd.DataFrame(research_data)
        
        if not df.empty:
            df = df[(df['publish_time'] >= start_date) & 
                   (df['publish_time'] <= end_date)]
        
        return df
    
    def _collect_api_research(self, source: Dict, stock_codes: List[str]) -> List[Dict]:
        """采集API研报数据"""
        
        research_items = []
        
        try:
            headers = {'Authorization': f"Bearer {source['api_key']}"}
            
            for stock_code in stock_codes:
                response = requests.get(
                    f"{source['url']}/research/{stock_code}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('reports', []):
                        research_items.append({
                            'source': source['name'],
                            'title': item.get('title', ''),
                            'content': item.get('summary', ''),
                            'publish_time': item.get('publish_date', ''),
                            'url': item.get('url', ''),
                            'type': 'research_report',
                            'stock_code': stock_code,
                            'analyst': item.get('analyst', ''),
                            'rating': item.get('rating', ''),
                            'target_price': item.get('target_price', 0)
                        })
        except Exception as e:
            print(f"Error collecting API research from {source['name']}: {e}")
        
        return research_items
    
    def _collect_web_research(self, source: Dict, stock_codes: List[str]) -> List[Dict]:
        """采集网页研报数据"""
        
        research_items = []
        
        try:
            for stock_code in stock_codes:
                url = f"{source['url']}/research/{stock_code}"
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(response.content, 'html.parser')
                
                reports = soup.find_all(source.get('report_tag', 'div'), 
                                       class_=source.get('report_class'))
                
                for report in reports:
                    title_tag = report.find(source.get('title_tag', 'h3'))
                    summary_tag = report.find(source.get('summary_tag', 'p'))
                    
                    if title_tag:
                        research_items.append({
                            'source': source['name'],
                            'title': title_tag.get_text(strip=True),
                            'content': summary_tag.get_text(strip=True) if summary_tag else '',
                            'publish_time': datetime.now().isoformat(),
                            'url': url,
                            'type': 'research_report',
                            'stock_code': stock_code
                        })
        except Exception as e:
            print(f"Error collecting web research from {source['name']}: {e}")
        
        return research_items
```

#### 2.2.2 数据清洗器

```python
import re
import jieba
import jieba.analyse
from typing import List, Dict

class SentimentDataCleaner:
    """舆情数据清洗器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.stop_words = self._load_stop_words()
        
    def clean_text(self, text: str) -> str:
        """清洗文本"""
        
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        text = re.sub(r'\@\w+|\#\w+', '', text)
        
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """分词"""
        
        words = jieba.cut(text)
        
        words = [w for w in words if w not in self.stop_words and len(w) > 1]
        
        return words
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        
        keywords = jieba.analyse.extract_tags(text, topK=top_k)
        return keywords
    
    def clean_sentiment_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """清洗舆情数据"""
        
        if data.empty:
            return data
        
        data['cleaned_content'] = data['content'].apply(self.clean_text)
        data['tokens'] = data['cleaned_content'].apply(self.tokenize)
        data['keywords'] = data['cleaned_content'].apply(
            lambda x: self.extract_keywords(x, top_k=5)
        )
        
        data = data.drop_duplicates(subset=['title', 'publish_time'])
        
        data = data[data['cleaned_content'].str.len() > 10]
        
        return data
    
    def _load_stop_words(self) -> set:
        """加载停用词"""
        
        default_stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就',
            '不', '人', '都', '一', '一个', '上', '也', '很',
            '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这'
        }
        
        return default_stop_words
```

---

## 三、接口设计

### 3.1 核心接口

```python
class SentimentDataIntegrationInterface:
    """舆情数据源集成接口"""
    
    def collect_all_sentiment(self,
                             keywords: List[str],
                             start_date: str,
                             end_date: str) -> pd.DataFrame:
        """采集所有舆情数据"""
        pass
    
    def get_sentiment_by_stock(self,
                              stock_code: str,
                              start_date: str,
                              end_date: str) -> pd.DataFrame:
        """获取指定股票的舆情数据"""
        pass
    
    def get_sentiment_by_source(self,
                               source: str,
                               start_date: str,
                               end_date: str) -> pd.DataFrame:
        """获取指定来源的舆情数据"""
        pass
```

### 3.2 数据接口

```python
@dataclass
class SentimentData:
    """舆情数据"""
    id: str
    source: str
    title: str
    content: str
    cleaned_content: str
    publish_time: datetime
    url: str
    type: str
    stock_codes: List[str]
    keywords: List[str]
    sentiment_score: float
    importance_score: float
```

---

## 四、实施路径

### 4.1 实施步骤

| 阶段 | 任务 | 时间 | 交付物 |
|------|------|------|--------|
| Phase 1 | 新闻采集器开发 | 3天 | 新闻采集模块 |
| Phase 2 | 社交媒体采集器开发 | 3天 | 社交媒体采集模块 |
| Phase 3 | 研报采集器开发 | 2天 | 研报采集模块 |
| Phase 4 | 数据清洗器开发 | 2天 | 数据清洗模块 |
| Phase 5 | 测试验证 | 2天 | 测试报告 |

### 4.2 依赖安装

```bash
pip install scrapy
pip install tweepy
pip install beautifulsoup4
pip install feedparser
pip install jieba
pip install pandas numpy
```

### 4.3 配置示例

```yaml
news_sources:
  - name: '新浪财经'
    type: 'rss'
    url: 'http://finance.sina.com.cn/rss/'
  - name: '东方财富'
    type: 'web'
    url: 'https://www.eastmoney.com/'
    article_tag: 'div'
    title_tag: 'h2'
    content_tag: 'p'

social_media:
  twitter:
    consumer_key: 'your_consumer_key'
    consumer_secret: 'your_consumer_secret'
    access_token: 'your_access_token'
    access_token_secret: 'your_access_token_secret'

research_sources:
  - name: '研报API'
    type: 'api'
    url: 'https://api.research.com'
    api_key: 'your_api_key'
```

---

## 五、质量保证

### 5.1 测试标准

- 单元测试覆盖率 ≥ 80%
- 集成测试通过率 = 100%
- 性能测试：采集1000条数据 < 5分钟

### 5.2 数据质量标准

- 数据完整性 ≥ 95%
- 数据准确性 ≥ 90%
- 数据时效性：实时延迟 < 5分钟

---

## 六、成本评估

| 成本项 | 数量 | 单价 | 总价 |
|--------|------|------|------|
| 开发时间 | 2周 | - | 0 |
| 云服务器 | 1个月 | 500 | 500 |
| Twitter API | 1个月 | 0 | 0 |
| 研报API | 1个月 | 500 | 500 |
| **总计** | - | - | **1000** |

---

**版本**: v1.0 | **更新**: 2026-04-07 | **状态**: ✅ 活跃
