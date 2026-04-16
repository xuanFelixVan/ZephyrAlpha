---
module_id: 10_AI_WORKFLOW_SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION_0447
version: 1.0.0
status: Active
priority: P1
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
- 验证Python版本文档
layer: layer_03
---
## 📋 文档目录



?



5. [API接口规范](#五api接口规范)



6. [算法流程图](#六算法流程图)



7. [性能指标定义](#七性能指标定义)



```
```---
```



**环境要求**:



- Python 3.9+



- PostgreSQL 12+



- Redis 6+



```bash



# 验证Python版本



python --version



pip list | grep -E "tweepy|praw|requests|pandas"



# 验证环境变量



python verify_environment.py



```



```
```---
```



### 0.2 深度学习情感分析模块环境准备



感分析模块蓝图](10_AI_WORKFLOW/DEEP_LEARNING_SENTIMENT_ANALYZER_BLUEPRINT.md)



**环境要求**:



- Python 3.9+



- PyTorch 2.1.0+ (支持CUDA 11.8+)



- Transformers 4.35.0+



- GPU（推荐，可选）



```bash



# 验证Python版本



python --version



# 验证PyTorch和CUDA



python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"



# 验证Transformers



python -c "import transformers; print(f'Transformers: {transformers.__version__}')"



# 验证FinBERT模型



python verify_finbert.py



```



```
```---
```



### 0.3 实时预警系统模块环境准备



**环境要求**:



- Python 3.9+



- FastAPI 0.104.1+



- PostgreSQL 12+



- Redis 6+



```bash



# 验证Python版本



python --version



pip list | grep -E "fastapi|uvicorn|redis|yagmail"



# 验证环境变量



python verify_environment.py



```



```
```---
```



### 1.1 模块概述



**模块ID**: AIWF_ADI_001



**模块名称**: Alternative Data Integration (另类数据集成)



**版本**: v1.0.0



### 1.2 详细API接口定义



#### 1.2.1 Twitter API



?



**接口名称**: TwitterAPIAdapter



```python



class TwitterAPIAdapter:



"""Twitter API



?







    负责从Twitter采集财经相关推文数据



    """







    def __init__(



        self,



        bearer_token: str,



        api_key: str,



        api_secret: str,



        access_token: str,



        access_token_secret: str



    ):



?







        Args:



            bearer_token: Twitter Bearer Token



            api_key: Twitter API Key



            api_secret: Twitter API Secret



            access_token: Access Token



            access_token_secret: Access Token Secret



        """



        pass







    def search_tweets(



        self,



        query: str,



        max_results: int = 100,



        start_time: Optional[datetime] = None,



        end_time: Optional[datetime] = None,



        tweet_fields: List[str] = None



    ) -> Dict[str, Any]:



        """搜索推文







        Args:



            end_time: 结束时间



            tweet_fields: 推文字段列表







        Returns:



            推文数据字典







        Raises:



            TwitterAPIError: Twitter API错误



            RateLimitError: 速率限制错误



        """



        pass







    def get_stream_rules(self) -> List[Dict[str, Any]]:



        """获取流式规则







        Returns:



            规则列表



        """



        pass







    def add_stream_rule(



        self,



        value: str,



        tag: str



    ) -> Dict[str, Any]:



        """添加流式规则







        Args:



value: ?



            tag: 规则标签







        Returns:



            添加结果



        """



        pass







    def delete_stream_rule(self, rule_ids: List[str]) -> Dict[str, Any]:



        """删除流式规则







        Args:



            rule_ids: 规则ID列表







        Returns:



            删除结果



        """



        pass







    def stream_tweets(



        self,



        callback: Callable[[Dict[str, Any]], None]



    ) -> None:



        """流式采集推文







        Args:



        """



        pass







    def get_rate_limit_status(self) -> Dict[str, Any]:







        Returns:



        """



        pass



```



**请求示例**:



```python



?



adapter = TwitterAPIAdapter(



    bearer_token="YOUR_BEARER_TOKEN",



    api_key="YOUR_API_KEY",



    api_secret="YOUR_API_SECRET",



    access_token="YOUR_ACCESS_TOKEN",



    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"



)



# 搜索推文



results = adapter.search_tweets(



    query="$AAPL OR Apple stock",



    max_results=100,



    start_time=datetime(2026, 4, 1),



    end_time=datetime(2026, 4, 2),



    tweet_fields=["created_at", "public_metrics", "entities"]



)



# 流式采集



def process_tweet(tweet):



print(f"? {tweet['text']}")



adapter.stream_tweets(callback=process_tweet)



```



**响应示例**:



```json



{



    "data": [



        {



            "id": "1234567890",



            "text": "Apple stock surges 5% after earnings beat",



            "created_at": "2026-04-02T10:00:00.000Z",



            "public_metrics": {



                "like_count": 150,



                "retweet_count": 45,



                "reply_count": 12,



                "quote_count": 8



            },



            "entities": {



                "hashtags": [{"tag": "AAPL"}],



                "symbols": [{"text": "AAPL"}]



            }



        }



    ],



    "meta": {



        "result_count": 1,



        "newest_id": "1234567890",



        "oldest_id": "1234567889"



    }



}



```



```
```---
```



#### 1.2.2 Reddit API



?



**接口名称**: RedditAPIAdapter



```python



class RedditAPIAdapter:



"""Reddit API



?







    """







    def __init__(



        self,



        client_id: str,



        client_secret: str,



        user_agent: str



    ):



?







        Args:



            client_id: Reddit应用客户端ID



        """



        pass







    def get_hot_posts(



        self,



        subreddit: str,



        limit: int = 100,



        params: Optional[Dict[str, Any]] = None



    ) -> List[Dict[str, Any]]:



        """获取热门帖子







        Args:



            limit: 返回数量限制



            params: 额外参数







        Returns:



            帖子列表



        """



        pass







    def get_new_posts(



        self,



        subreddit: str,



        limit: int = 100



    ) -> List[Dict[str, Any]]:







        Args:



            limit: 返回数量限制







        Returns:



            帖子列表



        """



        pass







    def get_post_comments(



        self,



        post_id: str,



        limit: int = 100,



        depth: int = 5



    ) -> List[Dict[str, Any]]:



        """获取帖子评论







        Args:



            post_id: 帖子ID



            limit: 返回数量限制



            depth: 评论深度







        Returns:



            评论列表



        """



        pass







    def search_posts(



        self,



        subreddit: str,



        query: str,



        sort: str = "relevance",



        limit: int = 100



    ) -> List[Dict[str, Any]]:



        """搜索帖子







        Args:



            query: 搜索查询



            sort: 排序方式



            limit: 返回数量限制







        Returns:



            帖子列表



        """



        pass







    def get_subreddit_info(self, subreddit: str) -> Dict[str, Any]:







        Args:







        Returns:



        """



        pass



```



**请求示例**:



```python



?



adapter = RedditAPIAdapter(



    client_id="YOUR_CLIENT_ID",



    client_secret="YOUR_CLIENT_SECRET",



    user_agent="ZephyrAlpha/1.0"



)



# 获取热门帖子



hot_posts = adapter.get_hot_posts(



    subreddit="wallstreetbets",



    limit=100



)



# 搜索帖子



search_results = adapter.search_posts(



    subreddit="stocks",



    query="AAPL Apple",



    sort="hot",



    limit=50



)



# 获取评论



comments = adapter.get_post_comments(



    post_id="abc123",



    limit=100,



    depth=3



)



```



**响应示例**:



```json



{



    "kind": "Listing",



    "data": {



        "children": [



            {



                "kind": "t3",



                "data": {



                    "id": "abc123",



                    "title": "AAPL to the moon! 🚀",



                    "selftext": "Apple just reported amazing earnings...",



                    "author": "username",



                    "subreddit": "wallstreetbets",



                    "created_utc": 1712054400,



                    "score": 1500,



                    "num_comments": 245,



                    "upvote_ratio": 0.95



                }



            }



        ]



    }



}



```



```
```---
```



#### 1.2.3 FRED API



?



**接口名称**: FREDAPIAdapter



```python



class FREDAPIAdapter:



"""FRED API



?







    负责从FRED采集美国宏观经济数据



    """







    def __init__(self, api_key: str):



?







        Args:



            api_key: FRED API密钥



        """



        pass







    def get_series(



        self,



        series_id: str,



        observation_start: Optional[str] = None,



        observation_end: Optional[str] = None,



        frequency: Optional[str] = None



    ) -> Dict[str, Any]:



        """获取经济数据序列







        Args:



            series_id: 序列ID



            observation_end: 结束日期 (YYYY-MM-DD)



            frequency: 频率 (d, w, m, q, a)







        Returns:



            序列数据



        """



        pass







    def get_series_info(self, series_id: str) -> Dict[str, Any]:



        """获取序列信息







        Args:



            series_id: 序列ID







        Returns:



            序列信息



        """



        pass







    def search_series(



        self,



        search_text: str,



        limit: int = 100



    ) -> List[Dict[str, Any]]:



        """搜索序列







        Args:



            search_text: 搜索文本



            limit: 返回数量限制







        Returns:



            序列列表



        """



        pass







    def get_categories(self, category_id: int = 0) -> List[Dict[str, Any]]:



        """获取分类







        Args:



            category_id: 分类ID







        Returns:



            分类列表



        """



        pass







    def get_releases(



        self,



        release_id: Optional[int] = None,



        limit: int = 100



    ) -> List[Dict[str, Any]]:



        """获取发布







        Args:



            release_id: 发布ID



            limit: 返回数量限制







        Returns:



            发布列表



        """



        pass



```



**请求示例**:



```python



?



adapter = FREDAPIAdapter(api_key="YOUR_FRED_API_KEY")



# 获取GDP数据



gdp_data = adapter.get_series(



    series_id="GDP",



    observation_start="2020-01-01",



    observation_end="2026-04-02",



    frequency="q"



)



# 搜索序列



search_results = adapter.search_series(



    search_text="unemployment rate",



    limit=50



)



# 获取序列信息



series_info = adapter.get_series_info(series_id="GDP")



```



**响应示例**:



```json



{



    "realtime_start": "2026-04-02",



    "realtime_end": "2026-04-02",



    "observation_start": "2020-01-01",



    "observation_end": "2026-04-02",



    "units": "Billions of Dollars",



    "output_type": 1,



    "file_type": "json",



    "order_by": "observation_date",



    "sort_order": "asc",



    "count": 25,



    "offset": 0,



    "limit": 100000,



    "observations": [



        {



            "realtime_start": "2026-04-02",



            "realtime_end": "2026-04-02",



            "date": "2020-01-01",



            "value": "21481.382"



        }



    ]



}



```



```
```---
```



#### 1.2.4 SEC EDGAR API



?



**接口名称**: SECEdgARAPIAdapter



```python



class SECEdgARAPIAdapter:



"""SEC EDGAR API



?







    负责从SEC EDGAR采集上市公司财务数据



    """







    def __init__(self, user_agent: str):



?







        Args:



        """



        pass







    def get_company_facts(self, cik: str) -> Dict[str, Any]:



        """获取公司财务数据







        Args:



cik:



CIK?







        Returns:



            公司财务数据



        """



        pass







    def get_company_concept(



        self,



        cik: str,



        taxonomy: str,



        concept: str



    ) -> Dict[str, Any]:



        """获取公司特定概念数据







        Args:



cik:



CIK?



            concept: 概念名称







        Returns:



            概念数据



        """



        pass







    def get_filings(



        self,



        cik: Optional[str] = None,



        form_type: Optional[str] = None,



        filing_date: Optional[str] = None,



        limit: int = 100



    ) -> List[Dict[str, Any]]:



        """获取财报列表







        Args:



cik:



CIK?



            form_type: 表格类型 (10-K, 10-Q, 8-K)



            filing_date: 提交日期



            limit: 返回数量限制







        Returns:



            财报列表



        """



        pass







    def get_filing_document(



        self,



        accession_number: str,



        document_name: str



    ) -> str:



        """获取财报文档







        Args:



            document_name: 文档名称







        Returns:



            文档内容



        """



        pass







    def get_company_info(self, cik: str) -> Dict[str, Any]:



        """获取公司信息







        Args:



cik:



CIK?







        Returns:



            公司信息



        """



        pass







    def search_companies(



        self,



        query: str,



        limit: int = 100



    ) -> List[Dict[str, Any]]:



        """搜索公司







        Args:



            query: 搜索查询



            limit: 返回数量限制







        Returns:



            公司列表



        """



        pass



```



**请求示例**:



```python



?



adapter = SECEdgARAPIAdapter(



    user_agent="ZephyrAlpha/1.0 (your.email@example.com)"



)



# 获取公司财务数据



company_facts = adapter.get_company_facts(cik="0000320193")  # Apple



# 获取特定概念数据



revenue_data = adapter.get_company_concept(



    cik="0000320193",



    taxonomy="us-gaap",



    concept="Revenues"



)



# 获取财报列表



filings = adapter.get_filings(



    cik="0000320193",



    form_type="10-K",



    limit=10



)



# 搜索公司



companies = adapter.search_companies(



    query="Apple",



    limit=10



)



```



**响应示例**:



```json



{



    "cik": "0000320193",



    "entityName": "Apple Inc.",



    "facts": {



        "us-gaap": {



            "Revenues": {



                "units": {



                    "USD": [



                        {



                            "end": "2025-09-30",



                            "val": 391035000000,



                            "accn": "0000320193-25-000123",



                            "fy": 2025,



                            "fp": "FY",



                            "form": "10-K",



                            "filed": "2025-11-04",



                            "frame": "CY2025"



                        }



                    ]



                }



            }



        }



    }



}



```



```
```---
```



### 2.1 模块概述



**模块ID**: AIWF_DLSA_001



?



**版本**: v1.0.0



### 2.2 详细API接口定义



**接口名称**: DLSentimentAnalyzer



```python



class DLSentimentAnalyzer:



?







?



    """







    def __init__(



        self,



        model_name: str = "ProsusAI/finbert",



        device: str = "cpu",



        max_length: int = 512,



        batch_size: int = 16,



        use_fp16: bool = False



    ):



        """初始化情感分析器







        Args:



            device: 设备类型 (cpu, cuda)



            use_fp16: 是否使用FP16精度



        """



        pass







    def analyze(



        self,



        text: str,



        return_all_scores: bool = False,



        return_emotion: bool = True,



        return_intensity: bool = True



    ) -> SentimentResult:



        """分析单条文本情感







        Args:



text:



?



            return_emotion: 是否返回情绪分析



            return_intensity: 是否返回强度分析







        Returns:



            情感分析结果



        """



        pass







    def analyze_batch(



        self,



        texts: List[str],



        return_all_scores: bool = False,



        show_progress: bool = True



    ) -> List[SentimentResult]:



        """批量分析文本情感







        Args:



            texts: 文本列表







        Returns:



            情感分析结果列表



        """



        pass







    def analyze_with_details(



        self,



        text: str



    ) -> Dict[str, Any]:



        """详细分析文本情感







        Args:



text:



?







        Returns:



        """



        pass







    def fine_tune(



        self,



        train_data: List[Dict[str, Any]],



        val_data: Optional[List[Dict[str, Any]]] = None,



        output_dir: str = "./models/finbert_finetuned",



        learning_rate: float = 2e-5,



        num_epochs: int = 3,



        batch_size: int = 16,



        warmup_steps: int = 500,



        save_steps: int = 500



    ) -> Dict[str, Any]:



        """微调模型







        Args:



            train_data: 训练数据



            val_data: 验证数据



            output_dir: 输出目录



            num_epochs: 训练轮数



            warmup_steps: 预热步数



            save_steps: 保存步数







        Returns:



            训练结果



        """



        pass







    def save_model(self, output_dir: str) -> None:



        """保存模型







        Args:



            output_dir: 输出目录



        """



        pass







    def load_model(self, model_dir: str) -> None:



        """加载模型







        Args:



            model_dir: 模型目录



        """



        pass







    def get_model_info(self) -> Dict[str, Any]:



        """获取模型信息







        Returns:



            模型信息



        """



        pass







    def benchmark(



        self,



        texts: List[str],



        num_runs: int = 10



    ) -> Dict[str, float]:



        """性能基准测试







        Args:



            texts: 测试文本列表



            num_runs: 运行次数







        Returns:



            性能指标



        """



        pass



```



**请求示例**:



```python



# 初始化分析器



analyzer = DLSentimentAnalyzer(



    model_name="ProsusAI/finbert",



    device="cuda",



    max_length=512,



    batch_size=16



)



# 单条文本分析



result = analyzer.analyze(



    text="Apple's revenue increased by 20% in Q4, beating expectations.",



    return_all_scores=True,



    return_emotion=True,



    return_intensity=True



)



# 批量分析



texts = [



    "Apple's revenue increased by 20% in Q4.",



    "The company reported a significant loss.",



    "Market remains stable with moderate growth."



]



results = analyzer.analyze_batch(



    texts=texts,



    return_all_scores=True,



    show_progress=True



)



# 详细分析



detailed_result = analyzer.analyze_with_details(



    text="Apple's revenue increased by 20% in Q4, beating expectations."



)



# 性能基准测试



benchmark_results = analyzer.benchmark(



    texts=texts,



    num_runs=10



)



```



**响应示例**:



```json



{



    "text": "Apple's revenue increased by 20% in Q4, beating expectations.",



    "basic_sentiment": {



        "label": "positive",



        "confidence": 0.92,



        "scores": {



            "positive": 0.92,



            "negative": 0.03,



            "neutral": 0.05



        }



    },



    "emotion": {



        "fear": 0.05,



        "greed": 0.65,



        "anger": 0.02,



        "surprise": 0.18,



        "sadness": 0.03,



        "joy": 0.07



    },



    "intensity": {



        "label": "strong",



        "score": 0.78



    },



    "time_horizon": {



        "short_term": 0.25,



        "medium_term": 0.55,



        "long_term": 0.20



    },



    "keywords": ["Apple", "revenue", "increased", "Q4", "expectations"],



    "entities": ["Apple Inc."],



    "confidence": 0.92,



    "model_info": {



        "model_name": "ProsusAI/finbert",



        "model_version": "1.0",



        "device": "cuda"



    }



}



```



```
```---
```



### 3.1 模块概述



**模块ID**: AIWF_RTAS_001



**模块名称**: Real-Time Alert System (实时预警系统)



**版本**: v1.0.0



### 3.2 详细API接口定义



#### 3.2.1 实时预警系统接口



**接口名称**: RealTimeAlertSystem



```python



class RealTimeAlertSystem:



    """实时预警系统







    """







    def __init__(



        self,



        config: Dict[str, Any],



        pusher_config: Dict[str, Any]



    ):







        Args:



            config: 系统配置



            pusher_config: 推送器配置



        """



        pass







    def start(self) -> None:



        """启动预警系统"""



        pass







    def stop(self) -> None:



        """停止预警系统"""



        pass







    def add_rule(self, rule: AlertRule) -> bool:



        """添加预警规则







        Args:



            rule: 预警规则







        Returns:



            是否添加成功



        """



        pass







    def remove_rule(self, rule_id: str) -> bool:



        """移除预警规则







        Args:



            rule_id: 规则ID







        Returns:



            是否移除成功



        """



        pass







    def update_rule(self, rule: AlertRule) -> bool:



        """更新预警规则







        Args:



            rule: 预警规则







        Returns:



            是否更新成功



        """



        pass







    def get_rules(self) -> List[AlertRule]:







        Returns:



            预警规则列表



        """



        pass







    def process_data(



        self,



        data: Dict[str, Any]



    ) -> Optional[Alert]:







        Args:



            data: 监控数据







        Returns:



            预警信息（如果触发）



        """



        pass







    def push_alert(self, alert: Alert) -> bool:







        Args:



            alert: 预警信息







        Returns:



        """



        pass







    def get_alert_history(



        self,



        start_time: Optional[datetime] = None,



        end_time: Optional[datetime] = None,



        severity: Optional[AlertSeverity] = None,



        limit: int = 100



    ) -> List[Alert]:



        """获取预警历史







        Args:



            end_time: 结束时间



            severity: 预警级别



            limit: 返回数量限制







        Returns:



            预警历史列表



        """



        pass







    def get_system_status(self) -> Dict[str, Any]:







        Returns:



        """



        pass







    def test_pusher(self, channel: str) -> bool:



        """测试推送器







        Args:







        Returns:



            是否测试成功



        """



        pass



```



**请求示例**:



```python



alert_system = RealTimeAlertSystem(



    config={



"monitoring_interval": 60,  # ?



        "max_alerts_per_hour": 100



    },



    pusher_config={



        "email": {



            "smtp_server": "smtp.gmail.com",



            "smtp_port": 587,



            "username": "your.email@gmail.com",



            "password": "your_password"



        },



        "wechat": {



            "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"



        },



        "telegram": {



            "bot_token": "YOUR_BOT_TOKEN",



            "chat_id": "YOUR_CHAT_ID"



        }



    }



)



# 添加预警规则



rule = AlertRule(



    rule_id="sentiment_negative_spike",



rule_name="



?,



    description="负面情感分数突然下降超过20%",



    condition={



        "metric": "sentiment_score",



        "operator": "decrease_by",



        "threshold": 0.2,



        "time_window": "5m"



    },



    severity=AlertSeverity.HIGH,



    channels=["email", "wechat"]



)



alert_system.add_rule(rule)



# 启动系统



alert_system.start()



# 处理数据



data = {



    "sentiment_score": 0.3,



    "previous_sentiment_score": 0.6,



    "timestamp": datetime.now()



}



alert = alert_system.process_data(data)



if alert:



    print(f"触发预警: {alert.title}")



```



**响应示例**:



```json



{



    "alert_id": "alert_20260402_001",



    "rule_id": "sentiment_negative_spike",



    "severity": "high",



"title": "



"message": "



?0%",



    "data": {



        "sentiment_score": 0.3,



        "previous_sentiment_score": 0.6,



        "change_rate": 0.5,



        "timestamp": "2026-04-02T10:30:00Z"



    },



    "triggered_at": "2026-04-02T10:30:05Z",



    "channels": ["email", "wechat"],



    "status": "sent"



}



```



```
```---
```



?



|--------|---------|------|------|



| id | INTEGER | 主键ID | 1 |



| tweet_id | TEXT | 推文ID | "1234567890" |



| text | TEXT | 推文内容 | "Apple stock surges..." |



| user_id | TEXT | 用户ID | "987654321" |



| user_name | TEXT | ?| "trader_john" |



| user_followers_count | INTEGER | ?| 5000 |



| created_at | TIMESTAMP | 创建时间 | "2026-04-02 10:00:00" |



| lang | TEXT | 语言 | "en" |



| hashtags | TEXT | 标签列表(JSON) | ["AAPL", "stocks"] |



| symbols | TEXT | 股票代码(JSON) | ["$AAPL"] |



| like_count | INTEGER | ?| 150 |



| retweet_count | INTEGER | ?| 45 |



| reply_count | INTEGER | ?| 12 |



| collected_at | TIMESTAMP | 采集时间 | "2026-04-02 10:05:00" |



|--------|---------|------|------|



| id | INTEGER | 主键ID | 1 |



| post_id | TEXT | 帖子ID | "abc123" |



| title | TEXT | 帖子标题 | "AAPL to the moon!" |



| selftext | TEXT | 帖子内容 | "Apple just reported..." |



| author | TEXT | ?| "username" |



| subreddit | TEXT | ?| "wallstreetbets" |



| created_utc | TIMESTAMP | 创建时间(UTC) | "2026-04-02 10:00:00" |



| score | INTEGER | 得分 | 1500 |



| upvote_ratio | REAL | 点赞比例 | 0.95 |



| collected_at | TIMESTAMP | 采集时间 | "2026-04-02 10:05:00" |



|--------|---------|------|------|



| id | INTEGER | 主键ID | 1 |



| series_id | TEXT | 序列ID | "GDP" |



| title | TEXT | 序列标题 | "Gross Domestic Product" |



| observation_date | DATE | 观察日期 | "2026-01-01" |



| value | REAL | ?| 25000.0 |



| frequency | TEXT | 频率 | "Quarterly" |



| units | TEXT | 单位 | "Billions of Dollars" |



| collected_at | TIMESTAMP | 采集时间 | "2026-04-02 10:00:00" |



|--------|---------|------|------|



| id | INTEGER | 主键ID | 1 |



| cik | TEXT |



CIK?| "0000320193" |



| company_name | TEXT | 公司名称 | "Apple Inc." |



| form_type | TEXT | 表格类型 | "10-K" |



| filed_at | DATE | 提交日期 | "2026-04-02" |



| fiscal_year | INTEGER | 财年 | 2025 |



| fiscal_period | TEXT | 财期 | "FY" |



| document_url | TEXT | 文档URL | "https://www.sec.gov/..." |



| parsed_data | TEXT | 解析数据(JSON) | {...} |



| collected_at | TIMESTAMP | 采集时间 | "2026-04-02 10:00:00" |



### 4.5



|--------|---------|------|------|



| id | INTEGER | 主键ID | 1 |



| text_hash | TEXT | 文本哈希 | "a1b2c3d4..." |



| text | TEXT | 原始文本 | "Apple's revenue..." |



| basic_sentiment | TEXT | 基础情感(JSON) | {"label": "positive", ...} |



| emotion | TEXT | 情绪(JSON) | {"fear": 0.05, ...} |



| intensity | TEXT | 强度(JSON) | {"label": "strong", ...} |



| time_horizon | TEXT | 时间维度(JSON) | {"short_term": 0.25, ...} |



| keywords | TEXT |



?JSON) | ["Apple", "revenue"] |



| entities | TEXT | 实体(JSON) | ["Apple Inc."] |



| model_name | TEXT | 模型名称 | "ProsusAI/finbert" |



| analyzed_at | TIMESTAMP | 分析时间 | "2026-04-02 10:00:00" |



|--------|---------|------|------|



| id | INTEGER | 主键ID | 1 |



| rule_id | TEXT | 规则ID | "sentiment_negative_spike" |



? |



| description | TEXT | 描述 | "负面情感分数突然下降..." |



| condition | TEXT | 条件(JSON) | {"metric": "sentiment_score", ...} |



| severity | TEXT | 严重级别 | "high" |



| enabled | INTEGER | 是否启用 | 1 |



| created_at | TIMESTAMP | 创建时间 | "2026-04-02 10:00:00" |



| updated_at | TIMESTAMP | 更新时间 | "2026-04-02 10:00:00" |



|--------|---------|------|------|



| id | INTEGER | 主键ID | 1 |



| alert_id | TEXT | 预警ID | "alert_20260402_001" |



| rule_id | TEXT | 规则ID | "sentiment_negative_spike" |



| severity | TEXT | 严重级别 | "high" |



| data | TEXT | 数据(JSON) | {...} |



| triggered_at | TIMESTAMP | 触发时间 | "2026-04-02 10:30:00" |



| status | TEXT | ?| "sent" |



| sent_at | TIMESTAMP | ?| "2026-04-02 10:30:05" |



| error_message | TEXT | 错误消息 | NULL |



```
```---
```



## 五、API接口规范



### 5.1 RESTful API设计规范



#### 5.1.1 URL设计规范



**基础URL**: `http://localhost:8000/api/v1`



**资源命名**:



- 使用复数名词: `/tweets`, `/posts`, `/alerts`



- 使用小写字母和连字符: `/sentiment-results`



-



**示例**:



```



GET    /api/v1/tweets                    # 获取推文列表



GET    /api/v1/tweets/{id}               # 获取单个推文



POST   /api/v1/tweets                    # 创建推文



PUT    /api/v1/tweets/{id}               # 更新推文



DELETE /api/v1/tweets/{id}               # 删除推文



GET    /api/v1/sentiment/analyze         # 情感分析



POST   /api/v1/sentiment/analyze-batch   # 批量情感分析



GET    /api/v1/alerts                    # 获取预警列表



POST   /api/v1/alerts/rules              # 创建预警规则



PUT    /api/v1/alerts/rules/{id}         # 更新预警规则



```



#### 5.1.2 请求格式



```



Content-Type: application/json



Authorization: Bearer {token}



Accept: application/json



```



**请求参数**:



```json



{



    "query": "AAPL",



    "max_results": 100,



    "start_time": "2026-04-01T00:00:00Z",



    "end_time": "2026-04-02T00:00:00Z"



}



```



#### 5.1.3 响应格式



**成功响应**:



```json



{



    "status": "success",



    "code": 200,



    "message": "Request successful",



    "data": {



        // 响应数据



    },



    "meta": {



        "total": 100,



        "page": 1,



        "per_page": 20



    }



}



```



**错误响应**:



```json



{



    "status": "error",



    "code": 400,



    "message": "Invalid request parameters",



    "errors": [



        {



            "field": "query",



            "message": "Query parameter is required"



        }



    ]



}



```



#### 5.1.4 HTTP状态码



| 状态码 | 说明 | 使用场景 |



|--------|------|----------|



| 200 | OK | 成功请求 |



| 201 | Created | 成功创建资源 |



| 204 | No Content | 成功删除资源 |



| 400 | Bad Request | 请求参数错误 |



| 401 | Unauthorized | ?|



| 403 | Forbidden | 禁止访问 |



| 429 | Too Many Requests | 请求过于频繁 |



?|



```
```---
```



### 5.2 WebSocket API设计规范



#### 5.2.1 连接建立



**WebSocket URL**: `ws://localhost:8000/ws`



**连接示例**:



```javascript



const ws = new WebSocket('ws://localhost:8000/ws');



ws.onopen = function(event) {



    // 订阅频道



    ws.send(JSON.stringify({



        action: 'subscribe',



        channel: 'sentiment_stream'



    }));



};



ws.onmessage = function(event) {



    const data = JSON.parse(event.data);



    console.log('收到消息:', data);



};



ws.onerror = function(error) {



    console.error('WebSocket错误:', error);



};



ws.onclose = function(event) {



?);



};



```



#### 5.2.2 消息格式



**订阅消息**:



```json



{



    "action": "subscribe",



    "channel": "sentiment_stream",



    "params": {



        "symbols": ["AAPL", "TSLA"]



    }



}



```



**取消订阅消息**:



```json



{



    "action": "unsubscribe",



    "channel": "sentiment_stream"



}



```



```json



{



    "channel": "sentiment_stream",



    "event": "sentiment_update",



    "data": {



        "symbol": "AAPL",



        "sentiment_score": 0.85,



        "timestamp": "2026-04-02T10:30:00Z"



    }



}



```



```
```---
```



## 六、算法流程图



### 6.1 数据源扩展模块流程图



```



?



?



?



?



?



建立API连接



?



[连接成功?]



??



?



      [采集模式?]



洗



洗



?



?



            数据存储



?



            更新采集统计



?



            [继续采集?]



```



```



?



?



?



初始化分词器



?



接收文本输入



?



  ├─ 去除HTML标签



  ├─ 去除特殊字符



  ├─ 分词



  └─ 编码



?



模型推理



?



获取情感分数



?



感结果



??



        ├─ 情绪分析



        ├─ 强度评估



        ├─ 时间维度



?



      结果融合



?



      返回详细结果



?



        结束



```



```



?



?



?



加载预警规则



?



启动监控线程



?



[监控模式?]



?



?



  规则匹配



?



  [触发规则?]



??



          生成预警信息



?



          [预警级别?]



?



?



?



?



[?]



```



```
```---
```



## 七、性能指标定义



### 7.1 数据源扩展模块性能指标



|---------|--------|---------|------|



| 错误恢复时间 | < 5分钟 | 记录错误恢复耗时 | 从错误到恢复 |



### 7.2 深度学习情感分析模块性能指标



|---------|--------|---------|------|



| 单条分析速度 | < 100ms (GPU) | 记录单次分析耗时 | 平均耗时 |



|



?|



### 7.3 实时预警系统模块性能指标



|---------|--------|---------|------|



| 监控延迟 | < 1分钟 | 记录数据到监控的时间 | 平均延迟 |



| 规则执行速度 | < 100ms | 记录规则执行耗时 | 平均耗时 |



```
```---
```



##



### 8.1 错误分类



- 模型加载失败



- API认证失败



- 系统崩溃



**P1 - 高优先级错误**:



- 数据采集失败



- 情感分析失败



- 数据存储失败



**P2 - 中优先级错误**:



- 数据质量警告



- 性能降级警告



- 配置错误警告



**P3 - 低优先级错误**:



- 日志记录失败



- 统计更新失败



-



**网络错误**:



- 连接超时



- 连接拒绝



- DNS解析失败



- SSL证书错误



**API错误**:



- 认证失败 (401)



- 权限不足 (403)



- 速率限制 (429)



**数据错误**:



- 数据格式错误



- 数据缺失



- 数据重复



- 数据异常



**系统错误**:



- 内存不足



- 磁盘空间不足



- CPU过载



- GPU内存不足



```
```---
```



### 8.2 错误处理策略



#### 8.2.1 重试策略



**重试条件**:



- 网络错误（连接超时、连接拒绝）



- API速率限制 (429)



**重试策略**:



```python



def retry_with_backoff(



    func: Callable,



    max_retries: int = 3,



    base_delay: float = 1.0,



    max_delay: float = 60.0,



    backoff_factor: float = 2.0



) -> Any:







    Args:



        func: 要执行的函数



        max_delay: 最大延迟（秒）







    Returns:



        函数执行结果







    Raises:



    """



    import time



    from functools import wraps







    for attempt in range(max_retries + 1):



        try:



            return func()



        except Exception as e:



            if attempt == max_retries:



                raise e







            delay = min(base_delay * (backoff_factor ** attempt), max_delay)



            time.sleep(delay)



```



#### 8.2.2 降级策略



**降级条件**:



**降级示例**:



```python



def analyze_sentiment(text: str) -> Dict[str, Any]:



"""



    try:



        # 尝试使用GPU



        if torch.cuda.is_available():



            return analyze_with_gpu(text)



        else:



            # 降级到CPU



            return analyze_with_cpu(text)



    except Exception as e:



        # 降级到基础方法



        logger.warning(f"深度学习模型失败，降级到基础方法: {e}")



        return analyze_with_basic_method(text)



```



#### 8.2.3 熔断策略



**熔断条件**:



**熔断示例**:



```python



class CircuitBreaker:



"""?""







    def __init__(



        self,



        failure_threshold: int = 5,



        timeout: int = 60,



        success_threshold: int = 2



    ):



        """



        Args:



timeout:



            success_threshold: 成功阈值（半开状态）



        """



        self.failure_threshold = failure_threshold



        self.timeout = timeout



        self.success_threshold = success_threshold



        self.failure_count = 0



        self.success_count = 0



        self.state = "closed"  # closed, open, half-open



        self.last_failure_time = None







    def call(self, func: Callable, *args, **kwargs) -> Any:



        if self.state == "open":



            if time.time() - self.last_failure_time > self.timeout:



                self.state = "half-open"



                self.success_count = 0



            else:







        try:



            result = func(*args, **kwargs)



            self._on_success()



            return result



        except Exception as e:



            self._on_failure()



            raise e







    def _on_success(self):



        """成功回调"""



        self.failure_count = 0



        if self.state == "half-open":



            self.success_count += 1



            if self.success_count >= self.success_threshold:



                self.state = "closed"







    def _on_failure(self):



        """失败回调"""



        self.failure_count += 1



        self.last_failure_time = time.time()







        if self.state == "half-open":



            self.state = "open"



        elif self.failure_count >= self.failure_threshold:



            self.state = "open"



```



```
```---
```



### 8.3 错误日志规范



#### 8.3.1 日志级别



| 级别 | 说明 | 使用场景 |



|------|------|----------|



| WARNING | 警告信息 | 潜在问题 |



| ERROR | 错误信息 | 错误但可恢复 |



| CRITICAL | 严重错误 | 系统崩溃 |



#### 8.3.2 日志格式



**标准格式**:



```



[时间] [级别] [模块] [函数] - 消息



[2026-04-02 10:30:00] [ERROR] [twitter_adapter] [search_tweets] - API调用失败: 429 Too Many Requests



```



**JSON格式**:



```json



{



    "timestamp": "2026-04-02T10:30:00Z",



    "level": "ERROR",



    "module": "twitter_adapter",



    "function": "search_tweets",



    "message": "API调用失败: 429 Too Many Requests",



    "error_code": "TWITTER_API_429",



    "stack_trace": "...",



    "context": {



        "query": "AAPL",



        "max_results": 100



    }



}



```



#### 8.3.3 错误代码规范



**格式**: `{模块}_{错误类型}_{具体错误}`



**示例**:



- `TWITTER_API_401`: Twitter API认证失败



- `TWITTER_API_429`: Twitter API速率限制



- `FRED_API_TIMEOUT`: FRED API连接超时



- `MODEL_LOAD_ERROR`: 模型加载失败



- `SENTIMENT_ANALYSIS_ERROR`: 情感分析失败



```
```---
```



##



**文件**: `config/data_sources.yaml`



```yaml



# Twitter API配置



twitter:



  enabled: true



  bearer_token: "${TWITTER_BEARER_TOKEN}"



  api_key: "${TWITTER_API_KEY}"



  api_secret: "${TWITTER_API_SECRET}"



  access_token: "${TWITTER_ACCESS_TOKEN}"



  access_token_secret: "${TWITTER_ACCESS_TOKEN_SECRET}"



  rate_limit:



    requests_per_15min: 450



    retry_attempts: 3



    retry_delay: 60



  keywords:



    - "$AAPL"



    - "Apple stock"



    - "iPhone"



  users:



    - "elonmusk"



    - "tim_cook"



# Reddit API配置



reddit:



  enabled: true



  client_id: "${REDDIT_CLIENT_ID}"



  client_secret: "${REDDIT_CLIENT_SECRET}"



  user_agent: "ZephyrAlpha/1.0"



  rate_limit:



    requests_per_minute: 60



    retry_attempts: 3



    retry_delay: 10



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



  rate_limit:



    requests_per_day: 10000



    retry_attempts: 3



    retry_delay: 5



  series:



    - id: "GDP"



name: "



      frequency: "q"



    - id: "UNRATE"



      frequency: "m"



    - id: "CPIAUCSL"



      frequency: "m"



# SEC EDGAR API配置



sec_edgar:



  enabled: true



  user_agent: "ZephyrAlpha/1.0 (your.email@example.com)"



  rate_limit:



    requests_per_second: 10



    retry_attempts: 3



    retry_delay: 1



  companies:



    - cik: "0000320193"



      name: "Apple Inc."



      ticker: "AAPL"



    - cik: "0001067983"



      name: "Berkshire Hathaway Inc"



      ticker: "BRK.A"



```



### 9.2 情感分析配置文件



**文件**: `config/sentiment_analysis.yaml`



```yaml



# 模型配置



model:



  name: "ProsusAI/finbert"



  version: "1.0"



  device: "cuda"  # cpu, cuda



  max_length: 512



  batch_size: 16



  use_fp16: false







# 备用模型



fallback_model:



  enabled: true



  name: "bert-base-chinese"



  device: "cpu"







# 分析配置



analysis:



  return_all_scores: true



  return_emotion: true



  return_intensity: true



  return_keywords: true



  return_entities: true







# 性能配置



performance:



  cache_enabled: true



  cache_size: 10000



cache_ttl: 3600  # ?



  parallel_workers: 4







# 微调配置



fine_tuning:



  enabled: false



  output_dir: "./models/finbert_finetuned"



  learning_rate: 2.0e-5



  num_epochs: 3



  batch_size: 16



  warmup_steps: 500



  save_steps: 500



  eval_steps: 500



```



### 9.3 预警系统配置文件



**文件**: `config/alert_system.yaml`



```yaml



# 系统配置



system:



monitoring_interval: 60  # ?



  max_alerts_per_hour: 100



  alert_history_days: 30







?



pushers:



  email:



    enabled: true



    smtp_server: "smtp.gmail.com"



    smtp_port: 587



    username: "${EMAIL_USERNAME}"



    password: "${EMAIL_PASSWORD}"



    from_address: "alerts@zephyralpha.com"



    to_addresses:



      - "your.email@example.com"







  wechat:



    enabled: true



    webhook_url: "${WECHAT_WEBHOOK_URL}"







  telegram:



    enabled: true



    bot_token: "${TELEGRAM_BOT_TOKEN}"



    chat_id: "${TELEGRAM_CHAT_ID}"







  sms:



    enabled: false



    provider: "twilio"



    account_sid: "${TWILIO_ACCOUNT_SID}"



    auth_token: "${TWILIO_AUTH_TOKEN}"



    from_number: "+1234567890"



    to_numbers:



      - "+0987654321"



# 默认预警规则



default_rules:



  - rule_id: "sentiment_negative_spike"



rule_name: "



?



    enabled: true



    condition:



      metric: "sentiment_score"



      operator: "decrease_by"



      threshold: 0.2



      time_window: "5m"



    severity: "high"



    channels: ["email", "wechat"]







  - rule_id: "news_volume_spike"



    enabled: true



    condition:



      metric: "news_count"



      operator: "increase_by"



      threshold: 1.0



      time_window: "10m"



    severity: "medium"



    channels: ["telegram"]



```



```
```---
```
