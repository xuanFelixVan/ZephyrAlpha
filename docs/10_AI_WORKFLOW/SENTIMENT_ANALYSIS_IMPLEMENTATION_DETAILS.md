---
module_id: SENTIMENT_ANALYSIS_IMPLEMENTATION_DETAILS
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: SENTIMENT_ANALYSIS_IMPLEMENTATION_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-04
owner: 首席架构师
layer: Layer 3 (舆情分析层)
responsibility:
  - 系统实施与部署管理与优化维护
standard_type: 实施指南
applicable_scope: 舆情分析层改进模块实施
compliance_level: 专业标准
parent_document: INDEX.md
---
---



## 文档职责说明

**本文档职责**: 实施细节文档
- 环境搭建、代码示例、配置模板、部署架构

# 舆情分析层改进模块实施细节文

> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v1.0
> **创建日期**: 2026-04-02
> **文档类型**: 实施指南
> **状*: 活跃

---

## 📋 文档目录

1. [环境搭建指南](#一环境搭建指南)
2. [代码示例](#二代码示
3. [配置文件模板](#三配置文件模
4. [部署架构](#四部署架
5. [数据库设计](#五数据库设计)
6. [监控与日志](#六监控与日志)

---

## 一、环境搭建指

### 1.1 系统要求

#### 硬件要求

| 组件 | 最低要| 推荐配置 | 说明 |
|------|---------|---------|------|
| CPU | 4核心 | 8核心+ | 多线程处|
| 内存 | 16GB | 32GB+ | 模型加载和数据处|
| GPU | NVIDIA GTX 1060 | NVIDIA RTX 3080+ | 深度学习推理 |
| GPU内存 | 6GB | 10GB+ | 模型加载 |
| 存储 | 100GB SSD | 500GB+ SSD | 数据和模型存|

#### 软件要求

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.9+ | 编程语言 |
| CUDA | 11.8+ | GPU加|
| cuDNN | 8.6+ | 深度学习|
| Docker | 20.10+ | 容器化部|
| Docker Compose | 2.0+ | 容器编排 |

### 1.2 Python环境配置

#### 创建虚拟环境

```bash
# 使用conda创建虚拟环境
conda create -n zephyr-alpha python=3.9
conda activate zephyr-alpha

# 或使用venv创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

#### 安装依赖

**requirements.txt**:
```txt
# 核心依赖
numpy==1.24.3
pandas==2.0.3
scipy==1.11.1

# 深度学习框架
torch==2.0.1
transformers==4.30.2
sentence-transformers==2.2.2

# API框架
fastapi==0.100.0
uvicorn==0.23.1
pydantic==2.0.3

# 数据
sqlalchemy==2.0.19
psycopg2-binary==2.9.6
redis==4.6.0

# 消息队列
kafka-python==2.0.2
pyspark==3.4.1

# 图数据库
neo4j==5.10.0
py2neo==2021.2.3

# NLP工具
spacy==3.6.0
langdetect==1.0.9
nltk==3.8.1

# 图像处理
Pillow==10.0.0
opencv-python==4.8.0.74

# 音频处理
librosa==0.10.1
soundfile==0.12.1

# 向量数据
chromadb==0.4.6
faiss-cpu==1.7.4

# 可视
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.15.0

# 监控和日
prometheus-client==0.17.1
loguru==0.7.0

# 测试
pytest==7.4.0
pytest-asyncio==0.21.1

# 工具
python-dotenv==1.0.0
pyyaml==6.0
requests==2.31.0
```

```bash
# 安装依赖
pip install -r requirements.txt

# 安装spaCy模型
python -m spacy download en_core_web_sm
python -m spacy download zh_core_web_sm

# 安装NLTK数据
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
```

### 1.3 Docker环境配置

#### Dockerfile

```dockerfile
# 基础镜像
FROM nvidia/cuda:11.8-cudnn8-runtime-ubuntu22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    python3.9-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置Python版本
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  # API服务
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/zephyr_alpha
      - REDIS_URL=redis://redis:6379/0
      - NEO4J_URI=bolt://neo4j:7687
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    depends_on:
      - postgres
      - redis
      - neo4j
      - kafka
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # PostgreSQL数据
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=zephyr_alpha
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis缓存
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Neo4j图数据库
  neo4j:
    image: neo4j:5.10
    environment:
      - NEO4J_AUTH=neo4j/password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  # Kafka消息队列
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  # Spark服务
  spark:
    image: bitnami/spark:3.4
    environment:
      - SPARK_MODE=master
    ports:
      - "7077:7077"
      - "8080:8080"

  spark-worker:
    image: bitnami/spark:3.4
    depends_on:
      - spark
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark:7077

volumes:
  postgres_data:
  redis_data:
  neo4j_data:
```

```bash
# 启动所有服
docker-compose up -d

# 查看服务状
docker-compose ps

# 查看日志
docker-compose logs -f api

# 停止所有服
docker-compose down
```

---

## 二、代码示

### 2.1 数据源扩展模块代码示

#### Twitter API适配器实

```python
import tweepy
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TwitterAPIAdapter:
    """Twitter API适配器实""
    
    def __init__(
        self,
        bearer_token: str,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str
    ):
        """初始化Twitter API适配""
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        # 初始化API客户
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # 初始化流式监听器
        self.stream_listener = None
    
    def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tweet_fields: List[str] = None
    ) -> Dict[str, Any]:
        """搜索推文"""
        try:
            if tweet_fields is None:
                tweet_fields = [
                    'created_at', 'public_metrics', 'entities',
                    'author_id', 'lang'
                ]
            
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                start_time=start_time,
                end_time=end_time,
                tweet_fields=tweet_fields
            )
            
            return {
                'data': [self._format_tweet(tweet) for tweet in response.data],
                'meta': response.meta
            }
            
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API错误: {e}")
            raise
    
    def stream_tweets(
        self,
        keywords: List[str],
        callback: callable
    ) -> None:
        """流式采集推文"""
        try:
            # 创建流式规则
            rule = tweepy.StreamRule(
                value=" OR ".join(keywords)
            )
            
            # 删除现有规则
            existing_rules = self.client.get_rules()
            if existing_rules.data:
                rule_ids = [rule.id for rule in existing_rules.data]
                self.client.delete_rules(rule_ids)
            
            # 添加新规
            self.client.add_rules(rule)
            
            # 启动流式监听
            stream = tweepy.StreamingClient(
                self.bearer_token,
                daemon=True
            )
            
            stream.on_tweet = callback
            stream.filter()
            
        except Exception as e:
            logger.error(f"流式采集错误: {e}")
            raise
    
    def _format_tweet(self, tweet) -> Dict[str, Any]:
        """格式化推文数""
        return {
            'id': tweet.id,
            'text': tweet.text,
            'created_at': tweet.created_at.isoformat(),
            'author_id': tweet.author_id,
            'lang': tweet.lang,
            'public_metrics': {
                'like_count': tweet.public_metrics['like_count'],
                'retweet_count': tweet.public_metrics['retweet_count'],
                'reply_count': tweet.public_metrics['reply_count'],
                'quote_count': tweet.public_metrics['quote_count']
            },
            'entities': tweet.entities
        }


# 使用示例
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    adapter = TwitterAPIAdapter(
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        api_key=os.getenv("TWITTER_API_KEY"),
        api_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
    
    # 搜索推文
    results = adapter.search_tweets(
        query="$AAPL OR Apple stock",
        max_results=10
    )
    
    for tweet in results['data']:
        print(f"推文: {tweet['text']}")
        print(f"点赞 {tweet['public_metrics']['like_count']}")
        print("-" * 50)
```

#### 深度学习情感分析器实

```python
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, Any, List, Optional
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """情感分析结果"""
    text: str
    label: str
    confidence: float
    scores: Dict[str, float]
    keywords: List[str]
    entities: List[str]


class DLSentimentAnalyzer:
    """深度学习情感分析器实""
    
    def __init__(
        self,
        model_name: str = "ProsusAI/finbert",
        device: str = "cpu",
        max_length: int = 512
    ):
        """初始化情感分析器"""
        self.model_name = model_name
        self.device = torch.device(device)
        self.max_length = max_length
        
        # 加载模型和分词器
        logger.info(f"加载模型: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # 标签映射
        self.label_map = {
            0: "negative",
            1: "neutral",
            2: "positive"
        }
    
    def analyze(
        self,
        text: str,
        return_all_scores: bool = True
    ) -> SentimentResult:
        """分析单条文本情感"""
        try:
            # 分词
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 模型推理
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)
            
            # 获取结果
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
            label = self.label_map[predicted_class]
            
            # 获取所有分
            scores = {}
            if return_all_scores:
                for idx, prob in enumerate(probabilities[0]):
                    scores[self.label_map[idx]] = prob.item()
            
            # 提取关键词和实体
            keywords = self._extract_keywords(text)
            entities = self._extract_entities(text)
            
            return SentimentResult(
                text=text,
                label=label,
                confidence=confidence,
                scores=scores,
                keywords=keywords,
                entities=entities
            )
            
        except Exception as e:
            logger.error(f"情感分析错误: {e}")
            raise
    
    def analyze_batch(
        self,
        texts: List[str],
        batch_size: int = 16
    ) -> List[SentimentResult]:
        """批量分析文本情感"""
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # 分词
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 模型推理
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)
            
            # 处理结果
            for j, text in enumerate(batch):
                predicted_class = torch.argmax(probabilities[j]).item()
                confidence = probabilities[j][predicted_class].item()
                label = self.label_map[predicted_class]
                
                scores = {}
                for idx, prob in enumerate(probabilities[j]):
                    scores[self.label_map[idx]] = prob.item()
                
                keywords = self._extract_keywords(text)
                entities = self._extract_entities(text)
                
                results.append(SentimentResult(
                    text=text,
                    label=label,
                    confidence=confidence,
                    scores=scores,
                    keywords=keywords,
                    entities=entities
                ))
        
        return results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键""
        # 简单实现：提取大写单词和特殊标
        import re
        keywords = []
        
        # 提取股票代码 ($AAPL)
        tickers = re.findall(r'\$[A-Z]+', text)
        keywords.extend(tickers)
        
        # 提取大写单词
        caps = re.findall(r'\b[A-Z]{2,}\b', text)
        keywords.extend(caps)
        
        return list(set(keywords))
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取实体"""
        # 简单实现：使用正则表达
        import re
        entities = []
        
        # 提取公司名称
        companies = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc\.|Corp\.|LLC|Ltd\.)', text)
        entities.extend(companies)
        
        return list(set(entities))


# 使用示例
if __name__ == "__main__":
    analyzer = DLSentimentAnalyzer(
        model_name="ProsusAI/finbert",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    
    # 单条分析
    text = "Apple's revenue increased by 20% in Q4, beating expectations."
    result = analyzer.analyze(text)
    
    print(f"文本: {result.text}")
    print(f"情感: {result.label}")
    print(f"置信 {result.confidence:.2f}")
    print(f"分数: {result.scores}")
    print(f"关键 {result.keywords}")
    print(f"实体: {result.entities}")
    
    # 批量分析
    texts = [
        "Apple's revenue increased by 20% in Q4.",
        "The company reported a significant loss.",
        "Market remains stable with moderate growth."
    ]
    
    results = analyzer.analyze_batch(texts)
    
    for result in results:
        print(f"\n文本: {result.text}")
        print(f"情感: {result.label}, 置信 {result.confidence:.2f}")
```

---

## 三、配置文件模

### 3.1 主配置文

**config/config.yaml**:
```yaml
# 应用配置
app:
  name: "ZephyrAlpha"
  version: "1.0.0"
  environment: "development"  # development, staging, production
  debug: true
  
# API配置
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: true
  
# 数据库配
database:
  postgres:
    host: "localhost"
    port: 5432
    database: "zephyr_alpha"
    user: "${POSTGRES_USER}"
    password: "${POSTGRES_PASSWORD}"
    pool_size: 20
    max_overflow: 10
    
  redis:
    host: "localhost"
    port: 6379
    db: 0
    password: "${REDIS_PASSWORD}"
    
  neo4j:
    uri: "bolt://localhost:7687"
    user: "neo4j"
    password: "${NEO4J_PASSWORD}"
    database: "neo4j"
    
# 消息队列配置
message_queue:
  kafka:
    bootstrap_servers: "localhost:9092"
    topics:
      - "news-stream"
      - "sentiment-stream"
      - "event-stream"
      
# 日志配置
logging:
  level: "INFO"
  format: "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
  file: "logs/app.log"
  max_size: 10485760  # 10MB
  backup_count: 5
  
# 监控配置
monitoring:
  enabled: true
  prometheus:
    port: 9090
  metrics:
    - "request_count"
    - "request_latency"
    - "error_count"
```

### 3.2 数据源配置文

**config/data_sources.yaml**:
```yaml
# Twitter API配置
twitter:
  enabled: true
  bearer_token: "${TWITTER_BEARER_TOKEN}"
  api_key: "${TWITTER_API_KEY}"
  api_secret: "${TWITTER_API_SECRET}"
  access_token: "${TWITTER_ACCESS_TOKEN}"
  access_token_secret: "${TWITTER_ACCESS_TOKEN_SECRET}"
  
  # 速率限制
  rate_limit:
    requests_per_15min: 450
    retry_attempts: 3
    retry_delay: 60
    
  # 监控关键
  keywords:
    - "$AAPL"
    - "Apple stock"
    - "iPhone"
    
  # 监控用户
  users:
    - "elonmusk"
    - "tim_cook"

# Reddit API配置
reddit:
  enabled: true
  client_id: "${REDDIT_CLIENT_ID}"
  client_secret: "${REDDIT_CLIENT_SECRET}"
  user_agent: "ZephyrAlpha/1.0"
  
  # 子版
  subreddits:
    - name: "wallstreetbets"
      limit: 100
    - name: "stocks"
      limit: 100
    - name: "investing"
      limit: 50

# FRED API配置
fred:
  enabled: true
  api_key: "${FRED_API_KEY}"
  
  # 经济指标
  series:
    - id: "GDP"
      name: "国内生产总
      frequency: "q"
    - id: "UNRATE"
      name: "失业
      frequency: "m"

# SEC EDGAR API配置
sec_edgar:
  enabled: true
  user_agent: "ZephyrAlpha/1.0 (your.email@example.com)"
  
  # 监控公司
  companies:
    - cik: "0000320193"
      name: "Apple Inc."
      ticker: "AAPL"
```

### 3.3 模型配置文件

**config/models.yaml**:
```yaml
# 情感分析模型配置
sentiment:
  text:
    name: "ProsusAI/finbert"
    device: "cuda"
    max_length: 512
    batch_size: 16
    
  image:
    name: "google/vit-base-patch16-224"
    device: "cuda"
    image_size: 224
    
  audio:
    name: "facebook/wav2vec2-base-960h"
    device: "cuda"
    sample_rate: 16000
    
  video:
    name: "MCG-NJU/videomae-base"
    device: "cuda"
    num_frames: 16

# 多语言模型配置
multilingual:
  translation:
    model: "Helsinki-NLP/opus-mt"
    cache_enabled: true
    
  sentiment_models:
    en: "ProsusAI/finbert"
    zh: "bert-base-chinese"
    ja: "cl-tohoku/bert-base-japanese"
    ko: "monologg/kobert"

# 实体识别模型配置
entity_recognition:
  model: "en_core_web_sm"
  custom_patterns:
    TICKER:
      - "AAPL"
      - "TSLA"
      - "MSFT"

# 关系抽取模型配置
relation_extraction:
  model: "bert-base-uncased"
  relation_types:
    - "INVEST"
    - "COOPERATE"
    - "COMPETE"
```

---

## 四、部署架

### 4.1 单机部署架构

```
┌─────────────────────────────────────────────────────────────
                     单机部署架构                             
├─────────────────────────────────────────────────────────────
                                                            
 ┌───────────────────────────────────────────────────────
              Nginx (反向代理)                          
              - 负载均衡                                
              - SSL终止                                 
 └───────────────────────────────────────────────────────
                                                          
 ┌───────────────────────────────────────────────────────
              FastAPI应用                               
              - RESTful API                             
              - WebSocket                               
              - 业务逻辑                                
 └───────────────────────────────────────────────────────
                                                          
 ┌─────────────┬─────────────┬─────────────┬────────────
 PostgreSQL     Redis      Neo4j       Kafka    
  (关系     (缓存)     (图数据库) (消息队列) 
 └─────────────┴─────────────┴─────────────┴────────────
                                                            
 ┌───────────────────────────────────────────────────────
              GPU服务                                
              - 深度学习模型                            
              - 情感分析                                
              - 多模态处                             
 └───────────────────────────────────────────────────────
                                                            
└─────────────────────────────────────────────────────────────
```

### 4.2 分布式部署架

```
┌─────────────────────────────────────────────────────────────────────
                       分布式部署架                                
├─────────────────────────────────────────────────────────────────────
                                                                    
 ┌───────────────────────────────────────────────────────────────
                    负载均衡                                 
  ┌───────────── ┌───────────── ┌─────────────         
    Nginx 1      Nginx 2      Nginx 3            
  └───────────── └───────────── └─────────────         
 └───────────────────────────────────────────────────────────────
                                                                  
 ┌───────────────────────────────────────────────────────────────
                    API服务                                  
  ┌───────────── ┌───────────── ┌─────────────         
   API Pod 1    API Pod 2    API Pod 3           
  └───────────── └───────────── └─────────────         
 └───────────────────────────────────────────────────────────────
                                                                  
 ┌───────────────────────────────────────────────────────────────
                    数据                                     
  ┌────────────── ┌────────────── ┌──────────────      
  PostgreSQL    Redis Cluster Neo4j Cluster      
    Cluster                                      
  └────────────── └────────────── └──────────────      
  ┌────────────── ┌──────────────                        
  │Kafka Cluster  │Spark Cluster                         
                                                     
  └────────────── └──────────────                        
 └───────────────────────────────────────────────────────────────
                                                                  
 ┌───────────────────────────────────────────────────────────────
                    GPU计算                                  
  ┌────────────── ┌────────────── ┌──────────────      
   GPU Node 1    GPU Node 2    GPU Node 3        
   (RTX 3080)    (RTX 3080)    (RTX 3080)        
  └────────────── └────────────── └──────────────      
 └───────────────────────────────────────────────────────────────
                                                                    
└─────────────────────────────────────────────────────────────────────
```

---

## 五、数据库设计

### 5.1 PostgreSQL数据库设

#### 创建数据库和

```sql
-- 创建数据
CREATE DATABASE zephyr_alpha;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建推文
CREATE TABLE tweets (
    id SERIAL PRIMARY KEY,
    tweet_id TEXT UNIQUE NOT NULL,
    text TEXT NOT NULL,
    user_id TEXT,
    user_name TEXT,
    user_followers_count INTEGER,
    created_at TIMESTAMP NOT NULL,
    lang TEXT,
    hashtags JSONB,
    symbols JSONB,
    like_count INTEGER,
    retweet_count INTEGER,
    reply_count INTEGER,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_tweets_created_at ON tweets(created_at);
CREATE INDEX idx_tweets_user_id ON tweets(user_id);
CREATE INDEX idx_tweets_lang ON tweets(lang);

-- 创建Reddit帖子
CREATE TABLE reddit_posts (
    id SERIAL PRIMARY KEY,
    post_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    selftext TEXT,
    author TEXT,
    subreddit TEXT NOT NULL,
    created_utc TIMESTAMP NOT NULL,
    score INTEGER,
    num_comments INTEGER,
    upvote_ratio REAL,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建情感分析结果
CREATE TABLE sentiment_results (
    id SERIAL PRIMARY KEY,
    text_hash TEXT UNIQUE NOT NULL,
    text TEXT NOT NULL,
    source TEXT NOT NULL,
    basic_sentiment JSONB NOT NULL,
    emotion JSONB,
    intensity JSONB,
    time_horizon JSONB,
    keywords JSONB,
    entities JSONB,
    confidence REAL NOT NULL,
    model_name TEXT NOT NULL,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建预警规则
CREATE TABLE alert_rules (
    id SERIAL PRIMARY KEY,
    rule_id TEXT UNIQUE NOT NULL,
    rule_name TEXT NOT NULL,
    description TEXT,
    condition JSONB NOT NULL,
    severity TEXT NOT NULL,
    channels JSONB NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建预警历史
CREATE TABLE alert_history (
    id SERIAL PRIMARY KEY,
    alert_id TEXT UNIQUE NOT NULL,
    rule_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    triggered_at TIMESTAMP NOT NULL,
    channels JSONB,
    status TEXT NOT NULL,
    sent_at TIMESTAMP,
    error_message TEXT
);

-- 创建知识库表
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    knowledge_id TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    category TEXT,
    tags JSONB,
    embedding VECTOR(768),  -- 需要pgvector扩展
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建向量索引
CREATE INDEX idx_knowledge_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
```

### 5.2 Neo4j图数据库设计

#### 创建约束和索

```cypher
// 创建唯一约束
CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT industry_id IF NOT EXISTS FOR (i:Industry) REQUIRE i.id IS UNIQUE;

// 创建索引
CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name);
CREATE INDEX company_ticker IF NOT EXISTS FOR (c:Company) ON (c.ticker);
CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name);
CREATE INDEX event_date IF NOT EXISTS FOR (e:Event) ON (e.date);

// 示例：创建公司节
CREATE (apple:Company {
    id: 'AAPL',
    name: 'Apple Inc.',
    ticker: 'AAPL',
    sector: 'Technology',
    market_cap: 2500000000000,
    country: 'USA'
});

// 示例：创建人物节
CREATE (tim:Person {
    id: 'tim_cook',
    name: 'Tim Cook',
    position: 'CEO'
});

// 示例：创建关
MATCH (p:Person {id: 'tim_cook'}), (c:Company {id: 'AAPL'})
CREATE (p)-[:BELONG_TO {role: 'CEO', since: '2011'}]->(c);

// 查询示例：查找苹果公司的所有关
MATCH (c:Company {id: 'AAPL'})-[r]-(n)
RETURN c, r, n;

// 查询示例：查找影响传导路
MATCH path = (c:Company {id: 'AAPL'})-[:INFLUENCE*1..3]->(target)
RETURN path;
```

---

## 六、监控与日志

### 6.1 Prometheus监控配置

**prometheus.yml**:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # API服务监控
  - job_name: 'zephyr-alpha-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    
  # PostgreSQL监控
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']
      
  # Redis监控
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
      
  # Neo4j监控
  - job_name: 'neo4j'
    static_configs:
      - targets: ['localhost:2004']
      
  # Kafka监控
  - job_name: 'kafka'
    static_configs:
      - targets: ['localhost:7071']
```

### 6.2 应用监控代码

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Response
import time

# 定义指标
REQUEST_COUNT = Counter(
    'request_count',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'active_requests',
    'Number of active requests'
)

SENTIMENT_ANALYSIS_COUNT = Counter(
    'sentiment_analysis_count',
    'Total sentiment analysis count',
    ['model', 'language']
)

SENTIMENT_ANALYSIS_LATENCY = Histogram(
    'sentiment_analysis_latency_seconds',
    'Sentiment analysis latency in seconds',
    ['model']
)

# FastAPI中间
app = FastAPI()

@app.middleware("http")
async def monitor_requests(request, call_next):
    ACTIVE_REQUESTS.inc()
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # 记录请求计数
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        # 记录请求延迟
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(latency)
        
        return response
        
    finally:
        ACTIVE_REQUESTS.dec()

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### 6.3 日志配置

```python
from loguru import logger
import sys

# 配置日志
logger.remove()  # 移除默认处理

# 控制台日
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# 文件日志
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO"
)

# 错误日志
logger.add(
    "logs/error_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="90 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
    level="ERROR",
    backtrace=True,
    diagnose=True
)

# 使用示例
logger.info("应用启动")
logger.debug("调试信息")
logger.warning("警告信息")
logger.error("错误信息")

try:
    # 可能出错的代
    result = 1 / 0
except Exception as e:
    logger.exception("发生异常")
```

---

**版本**: v1.0 | **更新**: 2026-04-02 | **状*: 活跃
