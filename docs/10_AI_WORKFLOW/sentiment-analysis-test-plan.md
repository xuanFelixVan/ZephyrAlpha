---
module_id: 10_AI_WORKFLOW_SENTIMENT_ANALYSIS_TEST_PLAN
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
  - 测试数据库配文档
layer: layer_00
**本文档职责**: 测试计划文档
> **核心职责**: 文档内容说明
> **版本**: v1.0
> **创建日期**: 2026-04-02
> **文档类型**: 测试计划
> **状*: 活跃
---
## 📋 文档目录



1. [测试策略](#一测试策略)

2. [单元测试计划](#二单元测试计

3. [集成测试计划](#三集成测试计

4. [性能测试计划](#四性能测试计划)

5. [验收测试计划](#五验收测试计

6. [测试数据准备](#六测试数据准



---



## 一、测试策



### 1.1 测试目标



确保舆情分析层改进模块的功能正确性、性能达标、稳定可靠，满足专业量化机构技术标准。



### 1.2 测试范围



| 模块 | 测试类型 | 测试范围 |

|------|---------|---------|

| **数据源扩展模* | 单元测试、集成测试、性能测试 | Twitter、Reddit、FRED、SEC EDGAR API适配|

| **深度学习情感分析模块** | 单元测试、集成测试、性能测试 | FinBERT模型、多维度分析、批量处|

| **实时预警系统模块** | 单元测试、集成测试、性能测试 | 规则引擎、预警推送、历史记|

| **知识图谱模块** | 单元测试、集成测试、性能测试 | 实体识别、关系抽取、图谱查|

| **流式处理架构** | 单元测试、集成测试、性能测试 | Kafka、Spark Streaming、消息处|

| **多语言支持模块** | 单元测试、集成测试、性能测试 | 语言检测、翻译、多语言情感分析 |

| **多模态分析模* | 单元测试、集成测试、性能测试 | 文本、图像、音频、视频分|

| **AI虚拟研究团队** | 单元测试、集成测试、性能测试 | AI助手、知识管理、报告生|



### 1.3 测试工具



| 工具类型 | 工具名称 | 用|

|---------|---------|------|

| 单元测试 | pytest | Python单元测试框架 |

| 集成测试 | pytest + requests | API集成测试 |

| 性能测试 | Locust | 负载测试和性能测试 |

| 代码覆盖| pytest-cov | 代码覆盖率统|

| 持续集成 | GitHub Actions | 自动化测试流|

| 测试数据 | Faker | 生成测试数据 |



### 1.4 测试环境



| 环境 | 配置 | 用|

|------|------|------|

| **开发环* | 本地开发机| 开发和调试 |

| **测试环境** | 独立测试服务| 集成测试和性能测试 |

| **预生产环* | 生产环境副本 | 验收测试 |

| **生产环境** | 生产服务| 生产运行 |



---



## 二、单元测试计



### 2.1 数据源扩展模块单元测



#### Twitter API适配器测



**测试文件**: `tests/unit/test_twitter_adapter.py`



```python

import pytest

from unittest.mock import Mock, patch, MagicMock

from datetime import datetime

from src.adapters.twitter_adapter import TwitterAPIAdapter





class TestTwitterAPIAdapter:

    """Twitter API适配器单元测""

    

    @pytest.fixture

    def twitter_adapter(self):

        """创建Twitter适配器实""

        return TwitterAPIAdapter(

            bearer_token="test_bearer_token",

            api_key="test_api_key",

            api_secret="test_api_secret",

            access_token="test_access_token",

            access_token_secret="test_access_token_secret"

        )

    

    def test_init(self, twitter_adapter):

        """测试初始""

        assert twitter_adapter.bearer_token == "test_bearer_token"

        assert twitter_adapter.api_key == "test_api_key"

    

    @patch('tweepy.Client')

    def test_search_tweets_success(self, mock_client, twitter_adapter):

        """测试搜索推文成功"""

        # 模拟API响应

        mock_response = Mock()

        mock_response.data = [

            Mock(

                id="123",

                text="Apple stock surges 5%",

                created_at=datetime(2026, 4, 2, 10, 0, 0),

                author_id="456",

                lang="en",

                public_metrics={

                    'like_count': 150,

                    'retweet_count': 45,

                    'reply_count': 12,

                    'quote_count': 8

                },

                entities={}

            )

        ]

        mock_response.meta = {'result_count': 1}

        

        mock_client.return_value.search_recent_tweets.return_value = mock_response

        

        # 执行测试

        result = twitter_adapter.search_tweets(

            query="$AAPL",

            max_results=10

        )

        

        # 验证结果

        assert len(result['data']) == 1

        assert result['data'][0]['text'] == "Apple stock surges 5%"

        assert result['meta']['result_count'] == 1

    

    @patch('tweepy.Client')

    def test_search_tweets_rate_limit(self, mock_client, twitter_adapter):

        """测试搜索推文速率限制"""

        import tweepy

        

        # 模拟速率限制错误

        mock_client.return_value.search_recent_tweets.side_effect = \

            tweepy.TooManyRequests("Rate limit exceeded")

        

        # 验证异常

        with pytest.raises(tweepy.TooManyRequests):

            twitter_adapter.search_tweets(query="$AAPL", max_results=10)

    

    @patch('tweepy.StreamingClient')

    def test_stream_tweets(self, mock_stream, twitter_adapter):

        """测试流式采集推文"""

        # 模拟流式监听

        mock_stream_instance = Mock()

        mock_stream.return_value = mock_stream_instance

        

        # 执行测试

        callback = Mock()

        twitter_adapter.stream_tweets(

            keywords=["$AAPL", "Apple"],

            callback=callback

        )

        

        # 验证调用

        mock_stream_instance.filter.assert_called_once()

```



#### 深度学习情感分析器测



**测试文件**: `tests/unit/test_sentiment_analyzer.py`



```python

import pytest

import torch

from unittest.mock import Mock, patch, MagicMock

from src.analyzers.dl_sentiment_analyzer import DLSentimentAnalyzer, SentimentResult





class TestDLSentimentAnalyzer:

    """深度学习情感分析器单元测""

    

    @pytest.fixture

    def sentiment_analyzer(self):

        """创建情感分析器实""

        with patch('transformers.AutoTokenizer.from_pretrained') as mock_tokenizer, \

             patch('transformers.AutoModelForSequenceClassification.from_pretrained') as mock_model:

            

            # 模拟tokenizer

            mock_tokenizer.return_value = Mock()

            

            # 模拟模型

            mock_model_instance = Mock()

            mock_model_instance.eval.return_value = mock_model_instance

            mock_model_instance.to.return_value = mock_model_instance

            mock_model.return_value = mock_model_instance

            

            analyzer = DLSentimentAnalyzer(

                model_name="ProsusAI/finbert",

                device="cpu"

            )

            

            return analyzer

    

    @patch('torch.softmax')

    @patch('torch.argmax')

    def test_analyze_positive_sentiment(self, mock_argmax, mock_softmax, sentiment_analyzer):

        """测试正面情感分析"""

        # 模拟模型输出

        mock_outputs = Mock()

        mock_outputs.logits = torch.tensor([[0.1, 0.2, 0.7]])

        

        sentiment_analyzer.model.return_value = mock_outputs

        

        # 模拟softmax和argmax

        mock_softmax.return_value = torch.tensor([[0.1, 0.2, 0.7]])

        mock_argmax.return_value = torch.tensor([2])  # positive

        

        # 执行测试

        result = sentiment_analyzer.analyze("Apple's revenue increased by 20%")

        

        # 验证结果

        assert result.label == "positive"

        assert result.confidence > 0.5

    

    @patch('torch.softmax')

    @patch('torch.argmax')

    def test_analyze_negative_sentiment(self, mock_argmax, mock_softmax, sentiment_analyzer):

        """测试负面情感分析"""

        # 模拟模型输出

        mock_outputs = Mock()

        mock_outputs.logits = torch.tensor([[0.8, 0.1, 0.1]])

        

        sentiment_analyzer.model.return_value = mock_outputs

        

        # 模拟softmax和argmax

        mock_softmax.return_value = torch.tensor([[0.8, 0.1, 0.1]])

        mock_argmax.return_value = torch.tensor([0])  # negative

        

        # 执行测试

        result = sentiment_analyzer.analyze("The company reported a significant loss")

        

        # 验证结果

        assert result.label == "negative"

        assert result.confidence > 0.5

    

    def test_extract_keywords(self, sentiment_analyzer):

        """测试关键词提""

        text = "Apple Inc. announced $AAPL stock buyback program"

        

        keywords = sentiment_analyzer._extract_keywords(text)

        

        assert "$AAPL" in keywords

        assert "AAPL" in keywords or "Apple" in keywords

    

    def test_extract_entities(self, sentiment_analyzer):

        """测试实体提取"""

        text = "Apple Inc. announced a partnership with Tesla Inc."

        

        entities = sentiment_analyzer._extract_entities(text)

        

        assert any("Apple" in entity for entity in entities)

```



### 2.2 实时预警系统模块单元测试



**测试文件**: `tests/unit/test_alert_system.py`



```python

import pytest

from datetime import datetime

from unittest.mock import Mock, patch

from src.alert_system.real_time_alert_system import RealTimeAlertSystem, AlertRule, AlertSeverity, Alert





class TestRealTimeAlertSystem:

    """实时预警系统单元测试"""

    

    @pytest.fixture

    def alert_system(self):

        """创建预警系统实例"""

        config = {

            "monitoring_interval": 60,

            "max_alerts_per_hour": 100

        }

        

        pusher_config = {

            "email": {

                "smtp_server": "smtp.gmail.com",

                "smtp_port": 587,

                "username": "test@example.com",

                "password": "password"

            }

        }

        

        return RealTimeAlertSystem(config, pusher_config)

    

    @pytest.fixture

    def sample_rule(self):

        """创建示例规则"""

        return AlertRule(

            rule_id="sentiment_negative_spike",

            rule_name="负面情感激,

            description="负面情感分数突然下降超过20%",

            condition={

                "metric": "sentiment_score",

                "operator": "decrease_by",

                "threshold": 0.2,

                "time_window": "5m"

            },

            severity=AlertSeverity.HIGH,

            channels=["email"]

        )

    

    def test_add_rule(self, alert_system, sample_rule):

        """测试添加规则"""

        result = alert_system.add_rule(sample_rule)

        

        assert result is True

        assert sample_rule.rule_id in alert_system.get_rules()

    

    def test_remove_rule(self, alert_system, sample_rule):

        """测试移除规则"""

        alert_system.add_rule(sample_rule)

        

        result = alert_system.remove_rule(sample_rule.rule_id)

        

        assert result is True

        assert sample_rule.rule_id not in alert_system.get_rules()

    

    def test_process_data_trigger_alert(self, alert_system, sample_rule):

        """测试处理数据触发预警"""

        alert_system.add_rule(sample_rule)

        

        data = {

            "sentiment_score": 0.3,

            "previous_sentiment_score": 0.6,

            "timestamp": datetime.now()

        }

        

        alert = alert_system.process_data(data)

        

        assert alert is not None

        assert alert.severity == AlertSeverity.HIGH

        assert "负面情感激 in alert.title

    

    def test_process_data_no_alert(self, alert_system, sample_rule):

        """测试处理数据不触发预""

        alert_system.add_rule(sample_rule)

        

        data = {

            "sentiment_score": 0.55,

            "previous_sentiment_score": 0.6,

            "timestamp": datetime.now()

        }

        

        alert = alert_system.process_data(data)

        

        assert alert is None

    

    @patch('src.alert_system.pushers.EmailPusher.push')

    def test_push_alert_success(self, mock_push, alert_system):

        """测试推送预警成""

        mock_push.return_value = True

        

        alert = Alert(

            alert_id="alert_001",

            rule_id="sentiment_negative_spike",

            severity=AlertSeverity.HIGH,

            title="测试预警",

            message="测试消息",

            data={},

            triggered_at=datetime.now(),

            channels=["email"],

            status="pending"

        )

        

        result = alert_system.push_alert(alert)

        

        assert result is True

        assert alert.status == "sent"

    

    def test_get_alert_history(self, alert_system):

        """测试获取预警历史"""

        # 添加一些预警历

        # ...

        

        history = alert_system.get_alert_history(limit=10)

        

        assert isinstance(history, list)

```



---



## 三、集成测试计



### 3.1 API集成测试



**测试文件**: `tests/integration/test_api_integration.py`



```python

import pytest

from fastapi.testclient import TestClient

from main import app





client = TestClient(app)





class TestAPIIntegration:

    """API集成测试"""

    

    def test_health_check(self):

        """测试健康检""

        response = client.get("/health")

        

        assert response.status_code == 200

        assert response.json()["status"] == "healthy"

    

    def test_analyze_sentiment(self):

        """测试情感分析API"""

        response = client.post(

            "/api/v1/sentiment/analyze",

            json={

                "text": "Apple's revenue increased by 20% in Q4.",

                "return_all_scores": True

            }

        )

        

        assert response.status_code == 200

        data = response.json()

        

        assert "sentiment" in data

        assert "label" in data["sentiment"]

        assert "confidence" in data["sentiment"]

    

    def test_analyze_batch_sentiment(self):

        """测试批量情感分析API"""

        response = client.post(

            "/api/v1/sentiment/analyze-batch",

            json={

                "texts": [

                    "Apple's revenue increased by 20%.",

                    "The company reported a significant loss."

                ]

            }

        )

        

        assert response.status_code == 200

        data = response.json()

        

        assert len(data["results"]) == 2

    

    def test_search_tweets(self):

        """测试推文搜索API"""

        response = client.get(

            "/api/v1/twitter/search",

            params={

                "query": "$AAPL",

                "max_results": 10

            }

        )

        

        assert response.status_code == 200

        data = response.json()

        

        assert "data" in data

        assert "meta" in data

    

    def test_create_alert_rule(self):

        """测试创建预警规则API"""

        response = client.post(

            "/api/v1/alerts/rules",

            json={

                "rule_id": "test_rule_001",

                "rule_name": "测试规则",

                "description": "测试预警规则",

                "condition": {

                    "metric": "sentiment_score",

                    "operator": "decrease_by",

                    "threshold": 0.2

                },

                "severity": "high",

                "channels": ["email"]

            }

        )

        

        assert response.status_code == 201

        data = response.json()

        

        assert data["rule_id"] == "test_rule_001"

    

    def test_get_alert_history(self):

        """测试获取预警历史API"""

        response = client.get(

            "/api/v1/alerts/history",

            params={

                "limit": 10

            }

        )

        

        assert response.status_code == 200

        data = response.json()

        

        assert isinstance(data["alerts"], list)

```



### 3.2 数据库集成测



**测试文件**: `tests/integration/test_database_integration.py`



```python

import pytest

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Tweet, SentimentResult

from src.database.connection import get_db





# 测试数据库配

TEST_DATABASE_URL = "postgresql://test:test@localhost:5432/test_zephyr_alpha"





@pytest.fixture(scope="function")

def db_session():

    """创建测试数据库会""

    engine = create_engine(TEST_DATABASE_URL)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    

    # 创建

    Base.metadata.create_all(bind=engine)

    

    session = SessionLocal()

    

    yield session

    

    # 清理

    session.close()

    Base.metadata.drop_all(bind=engine)





class TestDatabaseIntegration:

    """数据库集成测""

    

    def test_insert_tweet(self, db_session):

        """测试插入推文"""

        tweet = Tweet(

            tweet_id="1234567890",

            text="Apple stock surges 5%",

            user_id="987654321",

            user_name="test_user",

            user_followers_count=5000,

            created_at=datetime.now(),

            lang="en",

            like_count=150,

            retweet_count=45

        )

        

        db_session.add(tweet)

        db_session.commit()

        

        # 查询验证

        result = db_session.query(Tweet).filter_by(tweet_id="1234567890").first()

        

        assert result is not None

        assert result.text == "Apple stock surges 5%"

    

    def test_insert_sentiment_result(self, db_session):

        """测试插入情感分析结果"""

        result = SentimentResult(

            text_hash="abc123",

            text="Apple's revenue increased by 20%",

            source="twitter",

            basic_sentiment={"label": "positive", "confidence": 0.92},

            confidence=0.92,

            model_name="ProsusAI/finbert"

        )

        

        db_session.add(result)

        db_session.commit()

        

        # 查询验证

        saved = db_session.query(SentimentResult).filter_by(text_hash="abc123").first()

        

        assert saved is not None

        assert saved.basic_sentiment["label"] == "positive"

    

    def test_query_tweets_by_date_range(self, db_session):

        """测试按日期范围查询推""

        # 插入测试数据

        # ...

        

        # 查询

        start_date = datetime(2026, 4, 1)

        end_date = datetime(2026, 4, 3)

        

        results = db_session.query(Tweet).filter(

            Tweet.created_at >= start_date,

            Tweet.created_at <= end_date

        ).all()

        

        assert isinstance(results, list)

```



---



## 四、性能测试计划



### 4.1 负载测试



**测试文件**: `tests/performance/locustfile.py`



```python

from locust import HttpUser, task, between





class ZephyrAlphaUser(HttpUser):

    """模拟用户负载"""

    

    wait_time = between(1, 3)

    

    @task(3)

    def analyze_sentiment(self):

        """测试情感分析API"""

        self.client.post(

            "/api/v1/sentiment/analyze",

            json={

                "text": "Apple's revenue increased by 20% in Q4.",

                "return_all_scores": True

            }

        )

    

    @task(2)

    def search_tweets(self):

        """测试推文搜索API"""

        self.client.get(

            "/api/v1/twitter/search",

            params={

                "query": "$AAPL",

                "max_results": 10

            }

        )

    

    @task(1)

    def get_alert_history(self):

        """测试获取预警历史API"""

        self.client.get(

            "/api/v1/alerts/history",

            params={

                "limit": 10

            }

        )

```



**运行负载测试**:

```bash

# 启动Locust

locust -f tests/performance/locustfile.py --host=http://localhost:8000



# 访问 http://localhost:8089 进行测试配置

```



### 4.2 性能基准测试



**测试文件**: `tests/performance/test_benchmark.py`



```python

import pytest

import time

from src.analyzers.dl_sentiment_analyzer import DLSentimentAnalyzer





class TestPerformanceBenchmark:

    """性能基准测试"""

    

    @pytest.fixture

    def analyzer(self):

        """创建分析器实""

        return DLSentimentAnalyzer(

            model_name="ProsusAI/finbert",

            device="cuda"

        )

    

    def test_single_analysis_latency(self, analyzer):

        """测试单次分析延迟"""

        text = "Apple's revenue increased by 20% in Q4, beating expectations."

        

        # 预热

        analyzer.analyze(text)

        

        # 测试

        start_time = time.time()

        for _ in range(100):

            analyzer.analyze(text)

        end_time = time.time()

        

        avg_latency = (end_time - start_time) / 100

        

        # 验证延迟 < 100ms

        assert avg_latency < 0.1, f"平均延迟 {avg_latency}s 超过目标 0.1s"

    

    def test_batch_analysis_throughput(self, analyzer):

        """测试批量分析吞吐""

        texts = [

            "Apple's revenue increased by 20%.",

            "The company reported a significant loss.",

            "Market remains stable with moderate growth."

        ] * 100  # 300条文

        

        start_time = time.time()

        results = analyzer.analyze_batch(texts, batch_size=16)

        end_time = time.time()

        

        throughput = len(texts) / (end_time - start_time)

        

        # 验证吞吐> 100

        assert throughput > 100, f"吞吐{throughput}低于目标 100

    

    def test_api_response_time(self):

        """测试API响应时间"""

        import requests

        

        url = "http://localhost:8000/api/v1/sentiment/analyze"

        data = {

            "text": "Apple's revenue increased by 20%.",

            "return_all_scores": True

        }

        

        response_times = []

        

        for _ in range(100):

            start_time = time.time()

            response = requests.post(url, json=data)

            end_time = time.time()

            

            assert response.status_code == 200

            response_times.append(end_time - start_time)

        

        avg_response_time = sum(response_times) / len(response_times)

        

        # 验证响应时间 < 200ms

        assert avg_response_time < 0.2, f"平均响应时间 {avg_response_time}s 超过目标 0.2s"

```



---



## 五、验收测试计



### 5.1 功能验收测试清单



#### 数据源扩展模块验



| 测试| 验收标准 | 测试方法 | 状|

|--------|---------|---------|------|

| Twitter API连接 | 成功连接并获取数| 执行API调用 | 待测|

| Twitter数据采集 | 采集速度>100分钟 | 性能测试 | 待测|

| Reddit API连接 | 成功连接并获取数| 执行API调用 | 待测|

| FRED API连接 | 成功获取经济数据 | 执行API调用 | 待测|

| SEC EDGAR API连接 | 成功获取财务数据 | 执行API调用 | 待测|

| 数据存储 | 数据正确存储到数据库 | 数据验证 | 待测|



#### 深度学习情感分析模块验收



| 测试| 验收标准 | 测试方法 | 状|

|--------|---------|---------|------|

| 模型加载 | 成功加载FinBERT模型 | 功能测试 | 待测|

| 单条分析 | 分析速度<100ms | 性能测试 | 待测|

| 批量分析 | 吞吐100| 性能测试 | 待测|

| 模型准确| Accuracy>85% | 测试集评| 待测|

| 多维度分| 返回情感、情绪、强度等 | 功能测试 | 待测|



#### 实时预警系统模块验收



| 测试| 验收标准 | 测试方法 | 状|

|--------|---------|---------|------|

| 规则引擎 | 正确执行预警规则 | 功能测试 | 待测|

| 预警触发 | 触发延迟<30| 性能测试 | 待测|

| 预警推| 推送成功率>95% | 功能测试 | 待测|

| 历史记录 | 正确记录预警历史 | 数据验证 | 待测|



### 5.2 性能验收测试清单



| 指标 | 目标| 实际| 状|

|------|--------|--------|------|

| API平均响应时间 | <200ms | - | 待测|

| API吞吐| >100 req/s | - | 待测|

| 情感分析延迟 | <100ms | - | 待测|

| 批量分析吞吐| >100| - | 待测|

| 预警触发延迟 | <30| - | 待测|

| 系统可用| >99% | - | 待测|



### 5.3 安全验收测试清单



| 测试| 验收标准 | 测试方法 | 状|

|--------|---------|---------|------|

| API认证 | 未授权请求被拒绝 | 安全测试 | 待测|

| SQL注入 | 无SQL注入漏洞 | 安全扫描 | 待测|

| XSS攻击 | 无XSS漏洞 | 安全扫描 | 待测|

| 数据加密 | 敏感数据加密存储 | 安全审计 | 待测|

| 访问控制 | 权限正确控制 | 功能测试 | 待测|



---



## 六、测试数据准



### 6.1 测试数据



#### 情感分析测试数据



**文件**: `tests/data/sentiment_test_data.json`



```json

[

    {

        "text": "Apple's revenue increased by 20% in Q4, beating expectations.",

        "expected_sentiment": "positive",

        "confidence_threshold": 0.8

    },

    {

        "text": "The company reported a significant loss in Q3.",

        "expected_sentiment": "negative",

        "confidence_threshold": 0.8

    },

    {

        "text": "Market remains stable with moderate growth.",

        "expected_sentiment": "neutral",

        "confidence_threshold": 0.7

    }

]

```



#### 预警规则测试数据



**文件**: `tests/data/alert_rules_test_data.json`



```json

[

    {

        "rule_id": "test_sentiment_spike",

        "rule_name": "情感激增测,

        "condition": {

            "metric": "sentiment_score",

            "operator": "increase_by",

            "threshold": 0.3

        },

        "test_data": {

            "sentiment_score": 0.8,

            "previous_sentiment_score": 0.4

        },

        "expected_trigger": true

    }

]

```



### 6.2 测试数据生成脚本



**文件**: `tests/data/generate_test_data.py`



```python

from faker import Faker

import json

import random



fake = Faker()





def generate_tweets(count=100):

    """生成测试推文数据"""

    tweets = []

    

    for i in range(count):

        tweet = {

            "tweet_id": fake.uuid4(),

            "text": fake.sentence(nb_words=15),

            "user_id": fake.uuid4(),

            "user_name": fake.user_name(),

            "user_followers_count": random.randint(100, 10000),

            "created_at": fake.date_time_between(start_date="-30d").isoformat(),

            "lang": random.choice(["en", "zh", "ja"]),

            "like_count": random.randint(0, 1000),

            "retweet_count": random.randint(0, 500)

        }

        tweets.append(tweet)

    

    return tweets





def generate_sentiment_texts(count=100):

    """生成情感分析测试文本"""

    texts = []

    

    positive_templates = [

        "{}'s revenue increased by {}% in Q4.",

        "The company announced record-breaking sales.",

        "Stock price surges after positive earnings report."

    ]

    

    negative_templates = [

        "The company reported a significant loss of ${}.",

        "Stock price drops {}% after disappointing earnings.",

        "Analysts downgrade {} stock to sell."

    ]

    

    neutral_templates = [

        "Market remains stable with moderate growth.",

        "The company announced a new product launch.",

        "Trading volume remains average."

    ]

    

    for i in range(count):

        sentiment = random.choice(["positive", "negative", "neutral"])

        

        if sentiment == "positive":

            template = random.choice(positive_templates)

            text = template.format(

                fake.company(),

                random.randint(10, 50)

            )

        elif sentiment == "negative":

            template = random.choice(negative_templates)

            text = template.format(

                random.randint(100, 1000),

                random.randint(5, 20),

                fake.company()

            )

        else:

            text = random.choice(neutral_templates)

        

        texts.append({

            "text": text,

            "expected_sentiment": sentiment

        })

    

    return texts





if __name__ == "__main__":

    # 生成推文数据

    tweets = generate_tweets(100)

    with open("tests/data/tweets_test_data.json", "w") as f:

        json.dump(tweets, f, indent=2)

    

    # 生成情感分析数据

    texts = generate_sentiment_texts(100)

    with open("tests/data/sentiment_test_data.json", "w") as f:

        json.dump(texts, f, indent=2)

    

    print("测试数据生成完成")

```



---



## 七、测试执行流



### 7.1 测试执行步骤



```

1. 准备测试环境

   ├─ 安装依赖

   ├─ 配置数据

   └─ 启动服务



2. 执行单元测试

   ├─ 运行pytest

   └─ 生成覆盖率报



3. 执行集成测试

   ├─ API集成测试

   ├─ 数据库集成测

   └─ 第三方服务集成测



4. 执行性能测试

   ├─ 负载测试

   ├─ 压力测试

   └─ 基准测试



5. 执行验收测试

   ├─ 功能验收

   ├─ 性能验收

   └─ 安全验收



6. 生成测试报告

   ├─ 测试结果汇

   ├─ 问题清单

   └─ 改进建议

```



### 7.2 测试命令



```bash

# 运行所有单元测

pytest tests/unit/ -v --cov=src --cov-report=html



# 运行所有集成测

pytest tests/integration/ -v



# 运行性能测试

pytest tests/performance/ -v



# 运行所有测

pytest tests/ -v --cov=src --cov-report=html



# 生成测试报告

pytest tests/ --html=reports/test_report.html --self-contained-html

```



---



**版本**: v1.0 | **更新**: 2026-04-02 | **状*: 活跃

