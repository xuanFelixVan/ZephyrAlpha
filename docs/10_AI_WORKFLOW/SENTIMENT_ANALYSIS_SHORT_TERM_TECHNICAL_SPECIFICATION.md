---
module_id: SENTIMENT_ANALYSIS_SHORT_TERM_TS_001
version: 1.1.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-04
owner: 首席架构师
standard_type: 技术规格书
applicable_scope: 舆情分析层短期改进模块
compliance_level: 专业标准
parent_document: INDEX.md
applicable_modules:
  - 数据源扩展
  - 深度学习情感分析
  - 实时预警系统
---

## 文档职责说明

**本文档职责**: 短期改进技术规格书
- 数据源扩展、深度学习情感分析、实时预警系统技术规格

# 舆情分析层短期改进模块详细技术规格书
> **版本**: v1.1
> **创建日期**: 2026-04-02
> **最后更新**: 2026-04-04
> **适用模块**: 数据源扩展、深度学习情感分析、实时预警系统
> **标准**: 专业量化机构技术规格标准
---
## 📋 文档目录
1. [æ°æ®æºæ©å±æ¨¡åææ¯è§æ ¼](#ä¸æ°æ®æºæ©å±æ¨¡åææ¯è§æ ?
2. [æ·±åº¦å­¦ä¹ æ
æåææ¨¡åææ¯è§æ ¼](#äºæ·±åº¦å­¦ä¹ æ
æåææ¨¡åææ¯è§æ ?
3. [å®æ¶é¢è­¦ç³»ç»æ¨¡åææ¯è§æ ¼](#ä¸å®æ¶é¢è­¦ç³»ç»æ¨¡åææ¯è§æ ?
4. [æ°æ®å­å
¸](#åæ°æ®å­å
?
5. [API接口规范](#五api接口规范)
6. [算法流程图](#六算法流程图)
7. [性能指标定义](#七性能指标定义)
8. [éè¯¯å¤çè§è](#å
«éè¯¯å¤çè§è?
---
## ããç¯å¢åå¤?
> **éè¦æç¤º**: å¨å¼å§å®æ½åï¼è¯·å
å®æç¯å¢åå¤å·¥ä½ãè¯¦ç»çç¯å¢åå¤æ­¥éª¤è¯·åèåæ¨¡åèå¾ææ¡£ï¼?
### 0.1 æ°æ®æºæ©å±æ¨¡åç¯å¢åå¤?
**åèææ¡?*: [å¦ç±»æ°æ®éææ¨¡åèå¾](./DATA_SOURCE_EXTENSION_BLUEPRINT.md#50-ç¯å¢åå¤)
**环境要求**:
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- APIå¯é¥ï¼TwitterãRedditãFREDï¼?
**å¿«ééªè¯?*:
```bash
# 验证Python版本
python --version
# éªè¯ä¾èµåº?
pip list | grep -E "tweepy|praw|requests|pandas"
# 验证环境变量
python verify_environment.py
```
---
### 0.2 深度学习情感分析模块环境准备
**åèææ¡?*: [æ·±åº¦å­¦ä¹ æ
感分析模块蓝图](./DEEP_LEARNING_SENTIMENT_ANALYZER_BLUEPRINT.md#511-环境准备)
**环境要求**:
- Python 3.9+
- PyTorch 2.1.0+ (支持CUDA 11.8+)
- Transformers 4.35.0+
- GPU（推荐，可选）
**å¿«ééªè¯?*:
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
---
### 0.3 实时预警系统模块环境准备
**åèææ¡?*: [å®æ¶é¢è­¦ç³»ç»æ¨¡åèå¾](./REAL_TIME_ALERT_SYSTEM_BLUEPRINT.md#50-ç¯å¢åå¤)
**环境要求**:
- Python 3.9+
- FastAPI 0.104.1+
- PostgreSQL 12+
- Redis 6+
- æ¨éæå¡é
ç½®ï¼é®ä»¶ãå¾®ä¿¡ãTelegramï¼?
**å¿«ééªè¯?*:
```bash
# 验证Python版本
python --version
# éªè¯ä¾èµåº?
pip list | grep -E "fastapi|uvicorn|redis|yagmail"
# 验证环境变量
python verify_environment.py
```
---
## ä¸ãæ°æ®æºæ©å±æ¨¡åææ¯è§æ ?
### 1.1 模块概述
**模块ID**: AIWF_ADI_001
**模块名称**: Alternative Data Integration (另类数据集成)
**版本**: v1.0.0
**ç¶æ?*: è®¾è®¡ä¸?
### 1.2 详细API接口定义
#### 1.2.1 Twitter APIéé
å¨æ¥å?
**接口名称**: TwitterAPIAdapter
**ç±»å®ä¹?*:
```python
class TwitterAPIAdapter:
    """Twitter APIéé
å?
    
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
        """åå§åTwitter APIéé
å?
        
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
            query: æç´¢æ¥è¯¢å­ç¬¦ä¸?
            max_results: æå¤§ç»ææ°ï¼?0-100ï¼?
            start_time: å¼å§æ¶é?
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
            value: è§åå?
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
            callback: åè°å½æ°ï¼å¤çæ¯æ¡æ¨æ?
        """
        pass
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """è·åéçéå¶ç¶æ?
        
        Returns:
            éçéå¶ç¶æ?
        """
        pass
```
**请求示例**:
```python
# åå§åéé
å?
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
    print(f"æ°æ¨æ? {tweet['text']}")
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
---
#### 1.2.2 Reddit APIéé
å¨æ¥å?
**接口名称**: RedditAPIAdapter
**ç±»å®ä¹?*:
```python
class RedditAPIAdapter:
    """Reddit APIéé
å?
    
    è´è´£ä»Redditééè´¢ç»ç¸å
³å¸å­åè¯è®?
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str
    ):
        """åå§åReddit APIéé
å?
        
        Args:
            client_id: Reddit应用客户端ID
            client_secret: Redditåºç¨å®¢æ·ç«¯å¯é?
            user_agent: ç¨æ·ä»£çå­ç¬¦ä¸?
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
            subreddit: å­çååç§?
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
        """è·åææ°å¸å­?
        
        Args:
            subreddit: å­çååç§?
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
            subreddit: å­çååç§?
            query: 搜索查询
            sort: 排序方式
            limit: 返回数量限制
            
        Returns:
            帖子列表
        """
        pass
    
    def get_subreddit_info(self, subreddit: str) -> Dict[str, Any]:
        """è·åå­çåä¿¡æ?
        
        Args:
            subreddit: å­çååç§?
            
        Returns:
            å­çåä¿¡æ?
        """
        pass
```
**请求示例**:
```python
# åå§åéé
å?
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
---
#### 1.2.3 FRED APIéé
å¨æ¥å?
**接口名称**: FREDAPIAdapter
**ç±»å®ä¹?*:
```python
class FREDAPIAdapter:
    """FRED APIéé
å?
    
    负责从FRED采集美国宏观经济数据
    """
    
    def __init__(self, api_key: str):
        """åå§åFRED APIéé
å?
        
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
            observation_start: å¼å§æ¥æ?(YYYY-MM-DD)
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
# åå§åéé
å?
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
---
#### 1.2.4 SEC EDGAR APIéé
å¨æ¥å?
**接口名称**: SECEdgARAPIAdapter
**ç±»å®ä¹?*:
```python
class SECEdgARAPIAdapter:
    """SEC EDGAR APIéé
å?
    
    负责从SEC EDGAR采集上市公司财务数据
    """
    
    def __init__(self, user_agent: str):
        """åå§åSEC EDGAR APIéé
å?
        
        Args:
            user_agent: ç¨æ·ä»£çå­ç¬¦ä¸²ï¼å¿
é¡»å
å«é®ç®±ï¼?
        """
        pass
    
    def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """获取公司财务数据
        
        Args:
            cik: å
¬å¸CIKå?
            
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
            cik: å
¬å¸CIKå?
            taxonomy: åç±»æ³?(us-gaap, ifrs-full)
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
            cik: å
¬å¸CIKå?
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
            accession_number: ç»è®°å?
            document_name: 文档名称
            
        Returns:
            文档内容
        """
        pass
    
    def get_company_info(self, cik: str) -> Dict[str, Any]:
        """获取公司信息
        
        Args:
            cik: å
¬å¸CIKå?
            
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
# åå§åéé
å?
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
---
## äºãæ·±åº¦å­¦ä¹ æ
æåææ¨¡åææ¯è§æ ?
### 2.1 模块概述
**模块ID**: AIWF_DLSA_001
**æ¨¡ååç§°**: Deep Learning Sentiment Analyzer (æ·±åº¦å­¦ä¹ æ
æåæå?
**版本**: v1.0.0
**ç¶æ?*: è®¾è®¡ä¸?
### 2.2 详细API接口定义
#### 2.2.1 æ·±åº¦å­¦ä¹ æ
æåæå¨æ¥å?
**接口名称**: DLSentimentAnalyzer
**ç±»å®ä¹?*:
```python
class DLSentimentAnalyzer:
    """æ·±åº¦å­¦ä¹ æ
æåæå?
    
    ä½¿ç¨æ·±åº¦å­¦ä¹ æ¨¡åè¿è¡å¤ç»´åº¦æ
æåæ?
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
            model_name: æ¨¡ååç§°æè·¯å¾?
            device: 设备类型 (cpu, cuda)
            max_length: æå¤§åºåé¿åº?
            batch_size: æ¹å¤çå¤§å°?
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
            text: å¾
åæææ?
            return_all_scores: æ¯å¦è¿åææåæ?
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
            return_all_scores: æ¯å¦è¿åææåæ?
            show_progress: æ¯å¦æ¾ç¤ºè¿åº¦æ?
            
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
            text: å¾
åæææ?
            
        Returns:
            è¯¦ç»åæç»æï¼å
å«æ
æãæ
ç»ªãå¼ºåº¦ãå
³é®è¯ç­?
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
            learning_rate: å­¦ä¹ ç?
            num_epochs: 训练轮数
            batch_size: æ¹å¤çå¤§å°?
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
---
## ä¸ãå®æ¶é¢è­¦ç³»ç»æ¨¡åææ¯è§æ ?
### 3.1 模块概述
**模块ID**: AIWF_RTAS_001
**模块名称**: Real-Time Alert System (实时预警系统)
**版本**: v1.0.0
**ç¶æ?*: è®¾è®¡ä¸?
### 3.2 详细API接口定义
#### 3.2.1 实时预警系统接口
**接口名称**: RealTimeAlertSystem
**ç±»å®ä¹?*:
```python
class RealTimeAlertSystem:
    """实时预警系统
    
    å®ç°å®æ¶çæ§ãè§åæ§è¡ãå¤æ¸ éé¢è­¦æ¨é?
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        pusher_config: Dict[str, Any]
    ):
        """åå§åé¢è­¦ç³»ç»?
        
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
        """è·åææé¢è­¦è§å?
        
        Returns:
            预警规则列表
        """
        pass
    
    def process_data(
        self,
        data: Dict[str, Any]
    ) -> Optional[Alert]:
        """å¤çæ°æ®å¹¶è§¦åé¢è­?
        
        Args:
            data: 监控数据
            
        Returns:
            预警信息（如果触发）
        """
        pass
    
    def push_alert(self, alert: Alert) -> bool:
        """æ¨éé¢è­?
        
        Args:
            alert: 预警信息
            
        Returns:
            æ¯å¦æ¨éæå?
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
            start_time: å¼å§æ¶é?
            end_time: 结束时间
            severity: 预警级别
            limit: 返回数量限制
            
        Returns:
            预警历史列表
        """
        pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """è·åç³»ç»ç¶æ?
        
        Returns:
            ç³»ç»ç¶æ?
        """
        pass
    
    def test_pusher(self, channel: str) -> bool:
        """测试推送器
        
        Args:
            channel: æ¨éæ¸ é?
            
        Returns:
            是否测试成功
        """
        pass
```
**请求示例**:
```python
# åå§åé¢è­¦ç³»ç»?
alert_system = RealTimeAlertSystem(
    config={
        "monitoring_interval": 60,  # ç§?
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
    rule_name="è´é¢æ
ææ¿å¢?,
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
    "title": "è´é¢æ
ææ¿å¢é¢è­?,
    "message": "è´é¢æ
æåæ°ä»?.6ä¸éè?.3ï¼ä¸éå¹
åº?0%ï¼è¶
è¿éå?0%",
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
---
## åãæ°æ®å­å
?
### 4.1 Twitteræ°æ®è¡¨å­æ®µè¯´æ?
| å­æ®µå?| æ°æ®ç±»å | è¯´æ | ç¤ºä¾ |
|--------|---------|------|------|
| id | INTEGER | 主键ID | 1 |
| tweet_id | TEXT | 推文ID | "1234567890" |
| text | TEXT | 推文内容 | "Apple stock surges..." |
| user_id | TEXT | 用户ID | "987654321" |
| user_name | TEXT | ç¨æ·å?| "trader_john" |
| user_followers_count | INTEGER | ç²ä¸æ?| 5000 |
| created_at | TIMESTAMP | 创建时间 | "2026-04-02 10:00:00" |
| lang | TEXT | 语言 | "en" |
| hashtags | TEXT | 标签列表(JSON) | ["AAPL", "stocks"] |
| symbols | TEXT | 股票代码(JSON) | ["$AAPL"] |
| like_count | INTEGER | ç¹èµæ?| 150 |
| retweet_count | INTEGER | è½¬åæ?| 45 |
| reply_count | INTEGER | åå¤æ?| 12 |
| collected_at | TIMESTAMP | 采集时间 | "2026-04-02 10:05:00" |
### 4.2 Redditæ°æ®è¡¨å­æ®µè¯´æ?
| å­æ®µå?| æ°æ®ç±»å | è¯´æ | ç¤ºä¾ |
|--------|---------|------|------|
| id | INTEGER | 主键ID | 1 |
| post_id | TEXT | 帖子ID | "abc123" |
| title | TEXT | 帖子标题 | "AAPL to the moon!" |
| selftext | TEXT | 帖子内容 | "Apple just reported..." |
| author | TEXT | ä½è?| "username" |
| subreddit | TEXT | å­çå?| "wallstreetbets" |
| created_utc | TIMESTAMP | 创建时间(UTC) | "2026-04-02 10:00:00" |
| score | INTEGER | 得分 | 1500 |
| num_comments | INTEGER | è¯è®ºæ?| 245 |
| upvote_ratio | REAL | 点赞比例 | 0.95 |
| collected_at | TIMESTAMP | 采集时间 | "2026-04-02 10:05:00" |
### 4.3 FREDæ°æ®è¡¨å­æ®µè¯´æ?
| å­æ®µå?| æ°æ®ç±»å | è¯´æ | ç¤ºä¾ |
|--------|---------|------|------|
| id | INTEGER | 主键ID | 1 |
| series_id | TEXT | 序列ID | "GDP" |
| title | TEXT | 序列标题 | "Gross Domestic Product" |
| observation_date | DATE | 观察日期 | "2026-01-01" |
| value | REAL | æ°å?| 25000.0 |
| frequency | TEXT | 频率 | "Quarterly" |
| units | TEXT | 单位 | "Billions of Dollars" |
| collected_at | TIMESTAMP | 采集时间 | "2026-04-02 10:00:00" |
### 4.4 SEC EDGARæ°æ®è¡¨å­æ®µè¯´æ?
| å­æ®µå?| æ°æ®ç±»å | è¯´æ | ç¤ºä¾ |
|--------|---------|------|------|
| id | INTEGER | 主键ID | 1 |
| cik | TEXT | å
¬å¸CIKå?| "0000320193" |
| company_name | TEXT | 公司名称 | "Apple Inc." |
| form_type | TEXT | 表格类型 | "10-K" |
| filed_at | DATE | 提交日期 | "2026-04-02" |
| fiscal_year | INTEGER | 财年 | 2025 |
| fiscal_period | TEXT | 财期 | "FY" |
| document_url | TEXT | 文档URL | "https://www.sec.gov/..." |
| parsed_data | TEXT | 解析数据(JSON) | {...} |
| collected_at | TIMESTAMP | 采集时间 | "2026-04-02 10:00:00" |
### 4.5 æ
æåæç»æè¡¨å­æ®µè¯´æ?
| å­æ®µå?| æ°æ®ç±»å | è¯´æ | ç¤ºä¾ |
|--------|---------|------|------|
| id | INTEGER | 主键ID | 1 |
| text_hash | TEXT | 文本哈希 | "a1b2c3d4..." |
| text | TEXT | 原始文本 | "Apple's revenue..." |
| source | TEXT | æ°æ®æº?| "twitter" |
| basic_sentiment | TEXT | 基础情感(JSON) | {"label": "positive", ...} |
| emotion | TEXT | 情绪(JSON) | {"fear": 0.05, ...} |
| intensity | TEXT | 强度(JSON) | {"label": "strong", ...} |
| time_horizon | TEXT | 时间维度(JSON) | {"short_term": 0.25, ...} |
| keywords | TEXT | å
³é®è¯?JSON) | ["Apple", "revenue"] |
| entities | TEXT | 实体(JSON) | ["Apple Inc."] |
| confidence | REAL | ç½®ä¿¡åº?| 0.92 |
| model_name | TEXT | 模型名称 | "ProsusAI/finbert" |
| analyzed_at | TIMESTAMP | 分析时间 | "2026-04-02 10:00:00" |
### 4.6 é¢è­¦è§åè¡¨å­æ®µè¯´æ?
| å­æ®µå?| æ°æ®ç±»å | è¯´æ | ç¤ºä¾ |
|--------|---------|------|------|
| id | INTEGER | 主键ID | 1 |
| rule_id | TEXT | 规则ID | "sentiment_negative_spike" |
| rule_name | TEXT | è§ååç§° | "è´é¢æ
ææ¿å¢? |
| description | TEXT | 描述 | "负面情感分数突然下降..." |
| condition | TEXT | 条件(JSON) | {"metric": "sentiment_score", ...} |
| severity | TEXT | 严重级别 | "high" |
| channels | TEXT | æ¨éæ¸ é?JSON) | ["email", "wechat"] |
| enabled | INTEGER | 是否启用 | 1 |
| created_at | TIMESTAMP | 创建时间 | "2026-04-02 10:00:00" |
| updated_at | TIMESTAMP | 更新时间 | "2026-04-02 10:00:00" |
### 4.7 é¢è­¦åå²è¡¨å­æ®µè¯´æ?
| å­æ®µå?| æ°æ®ç±»å | è¯´æ | ç¤ºä¾ |
|--------|---------|------|------|
| id | INTEGER | 主键ID | 1 |
| alert_id | TEXT | 预警ID | "alert_20260402_001" |
| rule_id | TEXT | 规则ID | "sentiment_negative_spike" |
| severity | TEXT | 严重级别 | "high" |
| title | TEXT | æ é¢ | "è´é¢æ
ææ¿å¢é¢è­? |
| message | TEXT | æ¶æ¯ | "è´é¢æ
æåæ°ä»?.6..." |
| data | TEXT | 数据(JSON) | {...} |
| triggered_at | TIMESTAMP | 触发时间 | "2026-04-02 10:30:00" |
| channels | TEXT | æ¨éæ¸ é?JSON) | ["email", "wechat"] |
| status | TEXT | ç¶æ?| "sent" |
| sent_at | TIMESTAMP | åéæ¶é?| "2026-04-02 10:30:05" |
| error_message | TEXT | 错误消息 | NULL |
---
## 五、API接口规范
### 5.1 RESTful API设计规范
#### 5.1.1 URL设计规范
**基础URL**: `http://localhost:8000/api/v1`
**资源命名**:
- 使用复数名词: `/tweets`, `/posts`, `/alerts`
- 使用小写字母和连字符: `/sentiment-results`
- é¿å
æ·±å±åµå¥: æå¤?å±?
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
**è¯·æ±å¤?*:
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
| 401 | Unauthorized | æªææ?|
| 403 | Forbidden | 禁止访问 |
| 404 | Not Found | èµæºä¸å­å?|
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | æå¡å¨å
é¨éè¯?|
---
### 5.2 WebSocket API设计规范
#### 5.2.1 连接建立
**WebSocket URL**: `ws://localhost:8000/ws`
**连接示例**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = function(event) {
    console.log('WebSocketè¿æ¥å·²å»ºç«?);
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
    console.log('WebSocketè¿æ¥å·²å
³é?);
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
**æ¨éæ¶æ?*:
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
---
## 六、算法流程图
### 6.1 数据源扩展模块流程图
```
å¼å§?
  â?
åå§åæ°æ®æºéé
å?
  â?
é
ç½®APIå¯é¥ååæ?
  â?
建立API连接
  â?
[连接成功?]
  ââ å?â?è®°å½éè¯¯æ¥å¿ â?éè¯(æå¤?æ¬? â?å¤±è´¥
  ââ æ?â?
      å¼å§æ°æ®éé?
        â?
      [采集模式?]
        ââ å®æ¶æµå¼ â?å¯å¨æµå¼çå¬ â?æ¥æ¶æ°æ® â?æ°æ®æ¸
洗
        ââ å®æ¶æ¹é â?è®¾ç½®å®æ¶ä»»å¡ â?è§¦åéé â?æ°æ®æ¸
洗
                â?
            æ°æ®æ åå?
                â?
            数据存储
                â?
            更新采集统计
                â?
            [继续采集?]
                ââ æ?â?è¿åæ°æ®éé
                ââ å?â?ç»æ
```
### 6.2 æ·±åº¦å­¦ä¹ æ
æåææ¨¡åæµç¨å?
```
å¼å§?
  â?
å è½½é¢è®­ç»æ¨¡å?
  â?
初始化分词器
  â?
接收文本输入
  â?
ææ¬é¢å¤ç?
  ├─ 去除HTML标签
  ├─ 去除特殊字符
  ├─ 分词
  └─ 编码
  â?
模型推理
  â?
获取情感分数
  â?
[éè¦è¯¦ç»åæ?]
  ââ å?â?è¿ååºç¡æ
感结果
  ââ æ?â?
      å¤ç»´åº¦åæ?
        ├─ 情绪分析
        ├─ 强度评估
        ├─ 时间维度
        ââ å
³é®è¯æå?
          â?
      结果融合
          â?
      返回详细结果
          â?
        结束
```
### 6.3 å®æ¶é¢è­¦ç³»ç»æ¨¡åæµç¨å?
```
å¼å§?
  â?
åå§åé¢è­¦ç³»ç»?
  â?
加载预警规则
  â?
启动监控线程
  â?
[监控模式?]
  ââ è¢«å¨æ¨¡å¼ â?ç­å¾
æ°æ®è¾å
¥ â?æ¥æ¶æ°æ®
  ââ ä¸»å¨æ¨¡å¼ â?å®æ¶ééæ°æ® â?è·åæ°æ®
      â?
  æ°æ®é¢å¤ç?
      â?
  规则匹配
      â?
  [触发规则?]
      ââ å?â?æ´æ°çæ§ææ  â?è¿åçæ§
      ââ æ?â?
          生成预警信息
              â?
          [预警级别?]
              ââ Critical â?ç«å³æ¨é?
              ââ High â?5åéå
æ¨é?
              ââ Medium â?15åéå
æ¨é?
              ââ Low â?æ±æ»æ¨é?
                  â?
              éæ©æ¨éæ¸ é?
                  â?
              [æ¨éæå?]
                  ââ æ?â?è®°å½æ¨éåå?â?æ´æ°ç»è®¡ â?è¿åçæ§
                  ââ å?â?éè¯(æå¤?æ¬? â?[éè¯æå?]
                              ââ æ?â?è®°å½æ¨éåå?â?è¿åçæ§
                              ââ å?â?è®°å½å¤±è´¥æ¥å¿ â?ä½¿ç¨å¤ç¨æ¸ é â?è¿åçæ§
```
---
## 七、性能指标定义
### 7.1 数据源扩展模块性能指标
| ææ åç§° | ç®æ å?| æµéæ¹æ³ | è¯´æ |
|---------|--------|---------|------|
| æ°æ®éééåº¦ | > 100æ?åé | ç»è®¡åä½æ¶é´ééæ°é | æ¯ä¸ªæ°æ®æº?|
| APIååºæ¶é´ | < 2ç§?| è®°å½APIè°ç¨èæ¶ | å¹³åååºæ¶é´ |
| æ°æ®å®æ´æ?| > 95% | ç»è®¡æåééæ¯ä¾ | æåæ?æ»æ° |
| æ°æ®åç¡®æ?| > 95% | æ½æ ·éªè¯æ°æ®è´¨é | æ­£ç¡®æ?æ½æ ·æ?|
| ç³»ç»å¯ç¨æ?| > 99% | çæ§ç³»ç»è¿è¡æ¶é´ | æ­£å¸¸æ¶é´/æ»æ¶é?|
| 错误恢复时间 | < 5分钟 | 记录错误恢复耗时 | 从错误到恢复 |
### 7.2 深度学习情感分析模块性能指标
| ææ åç§° | ç®æ å?| æµéæ¹æ³ | è¯´æ |
|---------|--------|---------|------|
| 单条分析速度 | < 100ms (GPU) | 记录单次分析耗时 | 平均耗时 |
| æ¹éåæéåº¦ | > 100æ?ç§?(GPU) | ç»è®¡æ¹éå¤çéåº¦ | ååé?|
| æ¨¡ååç¡®ç?| > 85% | æµè¯éè¯ä¼?| Accuracy |
| æ¨¡åç²¾ç¡®ç?| > 85% | æµè¯éè¯ä¼?| Precision |
| æ¨¡åå¬åç?| > 85% | æµè¯éè¯ä¼?| Recall |
| F1åæ° | > 0.85 | æµè¯éè¯ä¼?| F1 Score |
| GPUå©ç¨ç?| > 80% | çæ§GPUä½¿ç¨ç?| å¹³åå©ç¨ç?|
| å
å­ä½¿ç¨ | < 4GB | çæ§å
å­ä½¿ç¨ | å³°å¼å
å­?|
### 7.3 实时预警系统模块性能指标
| ææ åç§° | ç®æ å?| æµéæ¹æ³ | è¯´æ |
|---------|--------|---------|------|
| 监控延迟 | < 1分钟 | 记录数据到监控的时间 | 平均延迟 |
| 规则执行速度 | < 100ms | 记录规则执行耗时 | 平均耗时 |
| é¢è­¦æ¨éå»¶è¿?| < 30ç§?| è®°å½è§¦åå°æ¨éçæ¶é´ | å¹³åå»¶è¿ |
| é¢è­¦åç¡®ç?| > 90% | éªè¯é¢è­¦æææ?| ææé¢è­¦/æ»é¢è­?|
| é¢è­¦è¯¯æ¥ç?| < 10% | ç»è®¡è¯¯æ¥æ¯ä¾ | è¯¯æ¥æ?æ»é¢è­?|
| æ¨éæåç | > 95% | ç»è®¡æ¨éæåæ¯ä¾?| æåæ?æ»æ° |
| ç³»ç»ååé?| > 100æ?åé | ç»è®¡å¤çè½å | æ¯åéå¤çæ° |
---
## å
«ãéè¯¯å¤çè§è?
### 8.1 错误分类
#### 8.1.1 æä¸¥éç¨åº¦åç±?
**P0 - é»æ­æ§éè¯?*:
- æ°æ®åºè¿æ¥å¤±è´?
- 模型加载失败
- API认证失败
- 系统崩溃
**P1 - 高优先级错误**:
- 数据采集失败
- 情感分析失败
- é¢è­¦æ¨éå¤±è´?
- 数据存储失败
**P2 - 中优先级错误**:
- 数据质量警告
- 性能降级警告
- 配置错误警告
**P3 - 低优先级错误**:
- 日志记录失败
- 统计更新失败
- éå
³é®åè½å¤±è´?
#### 8.1.2 æéè¯¯ç±»ååç±?
**网络错误**:
- 连接超时
- 连接拒绝
- DNS解析失败
- SSL证书错误
**API错误**:
- 认证失败 (401)
- 权限不足 (403)
- èµæºä¸å­å?(404)
- 速率限制 (429)
- æå¡å¨éè¯?(500)
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
---
### 8.2 错误处理策略
#### 8.2.1 重试策略
**重试条件**:
- 网络错误（连接超时、连接拒绝）
- API速率限制 (429)
- æå¡å¨ä¸´æ¶éè¯?(500, 502, 503)
**重试策略**:
```python
def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0
) -> Any:
    """ææ°éé¿éè¯?
    
    Args:
        func: 要执行的函数
        max_retries: æå¤§éè¯æ¬¡æ?
        base_delay: åºç¡å»¶è¿ï¼ç§ï¼?
        max_delay: 最大延迟（秒）
        backoff_factor: éé¿å å­?
        
    Returns:
        函数执行结果
        
    Raises:
        Exception: éè¯å¤±è´¥åæåºå¼å¸?
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
- GPUä¸å¯ç?â?ä½¿ç¨CPU
- å¤é¨APIä¸å¯ç?â?ä½¿ç¨ç¼å­æ°æ®
- æ°æ®åºä¸å¯ç¨ â?ä½¿ç¨æä»¶å­å¨
**降级示例**:
```python
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """æ
æåæï¼å¸¦éçº§ç­ç¥ï¼?""
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
- è¿ç»­å¤±è´¥æ¬¡æ°è¶
è¿éå¼ï¼å¦?æ¬¡ï¼
- éè¯¯çè¶
è¿éå¼ï¼å¦?0%ï¼?
- ååºæ¶é´è¶
è¿éå¼ï¼å¦?0ç§ï¼
**熔断示例**:
```python
class CircuitBreaker:
    """çæ­å?""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        """
        Args:
            failure_threshold: å¤±è´¥éå?
            timeout: çæ­è¶
æ¶æ¶é´ï¼ç§ï¼?
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
        """è°ç¨å½æ°ï¼å¸¦çæ­ä¿æ¤ï¼?""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                self.success_count = 0
            else:
                raise CircuitBreakerOpenError("çæ­å¨å¤äºæå¼ç¶æ?)
        
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
---
### 8.3 错误日志规范
#### 8.3.1 日志级别
| 级别 | 说明 | 使用场景 |
|------|------|----------|
| DEBUG | è°è¯ä¿¡æ¯ | å¼åè°è¯?|
| INFO | ä¸è¬ä¿¡æ?| æ­£å¸¸æä½ |
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
- `REDDIT_API_500`: Reddit APIæå¡å¨éè¯?
- `FRED_API_TIMEOUT`: FRED API连接超时
- `SEC_API_NOT_FOUND`: SEC EDGARèµæºä¸å­å?
- `MODEL_LOAD_ERROR`: 模型加载失败
- `SENTIMENT_ANALYSIS_ERROR`: 情感分析失败
- `ALERT_PUSH_ERROR`: é¢è­¦æ¨éå¤±è´?
---
## ä¹ãé
ç½®æä»¶è§è?
### 9.1 æ°æ®æºé
ç½®æä»?
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
      name: "å½å
çäº§æ»å?
      frequency: "q"
    - id: "UNRATE"
      name: "å¤±ä¸ç?
      frequency: "m"
    - id: "CPIAUCSL"
      name: "æ¶è´¹è
ä»·æ ¼ææ?
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
  cache_ttl: 3600  # ç§?
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
  monitoring_interval: 60  # ç§?
  max_alerts_per_hour: 100
  alert_history_days: 30
  
# æ¨éæ¸ éé
ç½?
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
    rule_name: "è´é¢æ
ææ¿å¢?
    enabled: true
    condition:
      metric: "sentiment_score"
      operator: "decrease_by"
      threshold: 0.2
      time_window: "5m"
    severity: "high"
    channels: ["email", "wechat"]
    
  - rule_id: "news_volume_spike"
    rule_name: "æ°é»éæ¿å¢?
    enabled: true
    condition:
      metric: "news_count"
      operator: "increase_by"
      threshold: 1.0
      time_window: "10m"
    severity: "medium"
    channels: ["telegram"]
```
---
**çæ¬**: v1.0 | **æ´æ°**: 2026-04-02 | **ç¶æ?*: â?æ´»è·
