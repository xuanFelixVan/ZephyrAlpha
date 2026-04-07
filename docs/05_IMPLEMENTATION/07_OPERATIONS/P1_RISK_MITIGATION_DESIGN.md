---
document_type: P1ﻝﭦ۶ﻠ۲ﻠ۸ﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟?
version: 1.0.0
created_date: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 实施指南、部署文档
  - 数据源
  - 文档治理
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻠ۲ﻠ۸ﻝ؟۰ﻝ
compliance_level: ﻛﺕﻛﺕﮔ ﮒ
status: ﮒﺝﮒ؟ﮔ?
applicable_scope: ﻝﺏﭨﻝﭨﮒ؟ﮔﺛ
parent_document: ../INDEX.md
implementation_status: ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ
module_id: IMP_P1_RISK_MITIGATION_D
last_updated: 2026-04-02---


# P1ﻝﭦ۶ﻠ۲ﻠ۸ﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰ﮔﮔ۰?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02
> **ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶**: P1 (ﻠ،?
> **ﻠ۲ﻠ۸ﮔﺍﻠ**: 18ﻛﺕ?
> **ﮒ۳ﻝﮒﮒ**: ﮒﺙﮒﮒﻟ؟ﺝﻟ؟۰ﮔﺗﮔ۰ﺅﺙﮒﺙﮒﻠﭘﮔ؟ﭖﮒ؟ﮔ?

---

## 1. P1ﻝﭦ۶ﻠ۲ﻠ۸ﮔﺕﮒ?

### 1.1 ﮒ۳ﻠ۷APIﻛﺝﻟﭖﻠ۲ﻠ۸ﺅﺙ?2ﻛﺕ۹ﺅﺙ

| ﻠ۲ﻠ۸ID | ﻠ۲ﻠ۸ﮔﻟﺟﺍ | ﮔﭘﮒﮔ۷۰ﮒ | ﮒﺛﺎﮒﻟﮒﺑ |
|--------|----------|----------|----------|
| **R-LLM-001** | GLM-4-Flash APIﻟﺍﻝ۷ﮒ۳ﺎﻟﺑ۴ | DailyReporter, MonthlyReporter, MarketAnalyzer | AIﮔ۴ﮒﻝﮔﮒ۳ﺎﻟﺑ۴ |
| **R-LLM-002** | GLM-4-Flash APIﻟﭘﮔﭘ | DailyReporter, MonthlyReporter, MarketAnalyzer | ﮔ۴ﮒﻝﮔﮒﭨﭘﻟﺟ |
| **R-LLM-003** | GLM-4-Flash APIﮔﮔ؛ﻟﭘﮔﺁ | ﮔﮔLLMﻠﮔﮔ۷۰ﮒ | ﮔﮔ؛ﮔ۶ﮒﭘﮒ۳ﺎﮔ |
| **R-QMT-001** | QMTﮒ؟۱ﮔﺓﻝ،ﺁﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ?| QMTDataInterface, QMTExecutor | ﮔﺍﮔ؟ﻟﺓﮒﮒ۳ﺎﻟﺑ۴ﻙﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ?|
| **R-QMT-002** | QMT APIﮒﮒﭦﻟﭘﮔﭘ | QMTDataInterface, QMTExecutor | ﮔﺍﮔ؟ﮒﭨﭘﻟﺟﻙﻛﭦ۳ﮔﮒﭨﭘﻟﺟ?|
| **R-IFIND-001** | iFindﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ۷ | iFindConnector | ﮒ ﮒ­ﮔﺍﮔ؟ﻝﺙﭦﮒ۳ﺎ |
| **R-IFIND-002** | iFind APIﻠﮔﭖ | iFindConnector | ﮔﺍﮔ؟ﻟﺓﮒﮒﻠ |
| **R-NEWS-001** | ﮔﺍﻠﭨﻝ؛ﻟ،ﻟ۱،ﮒﺍﻝ۵?| NewsCrawler | ﻟﮔﮔﺍﮔ؟ﻝﺙﭦﮒ۳ﺎ |
| **R-NEWS-002** | ﮔﺍﻠﭨAPIﻛﺕﮒﺁﻝ?| NewsCrawler | ﻟﮔﮔﺍﮔ؟ﻝﺙﭦﮒ۳ﺎ |
| **R-DINGTALK-001** | ﻠﻠAPIﻛﺕﮒﺁﻝ?| NotificationSystem | ﻠﻝ۴ﮒﻠﮒ۳ﺎﻟﺑ?|
| **R-WECHAT-001** | ﻛﺙﻛﺕﮒﺝ؟ﻛﺟ۰APIﻛﺕﮒﺁﻝ?| NotificationSystem | ﻠﻝ۴ﮒﻠﮒ۳ﺎﻟﺑ?|
| **R-SMS-001** | ﻝ­ﻛﺟ۰APIﻛﺕﮒﺁﻝ?| NotificationSystem | ﻠﻝ۴ﮒﻠﮒ۳ﺎﻟﺑ?|

### 1.2 ﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ۷ﻠ۲ﻠ۸ﺅﺙ?ﻛﺕ۹ﺅﺙ

| ﻠ۲ﻠ۸ID | ﻠ۲ﻠ۸ﮔﻟﺟﺍ | ﮔﭘﮒﮔ۷۰ﮒ | ﮒﺛﺎﮒﻟﮒﺑ |
|--------|----------|----------|----------|
| **R-DATA-001** | ﻛﺕﮔﺕﺕﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ۷ | ﮔﮔLayer 0ﮔ۷۰ﮒ | ﮔﺍﮔ؟ﻟﺓﮒﮒ۳ﺎﻟﺑ۴ |
| **R-DATA-002** | ﮔﺍﮔ؟ﮒﭦﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ?| DataStorage, PositionManager | ﮔﺍﮔ؟ﮔﻛﺗﮒﮒ۳ﺎﻟﺑ?|
| **R-DATA-003** | ﻝﺙﮒ­ﮔﮒ۰ﻛﺕﮒﺁﻝ?| ﮔﮔﻝﺙﮒ­ﮔ۷۰ﮒ?| ﮔ۶ﻟﺛﻛﺕﻠ |
| **R-DATA-004** | ﮔﺍﮔ؟ﻟﺑ۷ﻠﮒﺙﮒﺕﺕ | DataValidator, DataCleaner | ﮔﺍﮔ؟ﻠﻟﺁﺁ |
| **R-DATA-005** | ﮔﺍﮔ؟ﮒﭨﭘﻟﺟﻟﺟﻠ، | ﮔﮔﮒ؟ﮔﭘﮔﺍﮔ؟ﮔ۷۰ﮒ?| ﮒ؟ﮔﭘﮔ۶ﻛﺕﻠ?|
| **R-DATA-006** | ﮔﺍﮔ؟ﮒ­ﮒ۷ﻝ۸ﭦﻠﺑﻛﺕﻟﭘﺏ | DataStorage, TradeAuditor | ﮔﺍﮔ؟ﻛﺟﮒ­ﮒ۳ﺎﻟﺑ۴ |

---

## 2. ﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰

### 2.1 LLM APIﻛﺝﻟﭖﻠ۲ﻠ۸ﻝﺙﻟ۶۲ﮔﺗﮔ۰

#### ﮔﺗﮔ۰ﮔ۵ﻟﺟﺍ

**ﮔ ﺕﮒﺟﻝ­ﻝ۴**: ﻠﻝﭦ۶ﮔﺗﮔ۰ + ﻠﻟﺁﮔﭦﮒﭘ + ﮔﮔ؛ﮔ۶ﮒﭘ + ﮒ۳ﮔ۷۰ﮒﮒ۳ﻛﭨ?

#### 2.1.1 ﻠﻝﭦ۶ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰

```python
class LLMFallbackStrategy:
    """LLMﻠﻝﭦ۶ﻝ­ﻝ۴
    
    ﻝﺑ۱ﮒﺙ: RISK.LLM.FALLBACK.001
    """
    
    def __init__(self):
        self.strategies = [
            self._primary_llm,      # ﻛﺕﭨLLM (GLM-4-Flash)
            self._backup_llm,       # ﮒ۳ﻝ۷LLM (GPT-3.5-Turbo)
            self._template_fallback, # ﮔ۷۰ﮔﺟﻠﻝﭦ۶
            self._cache_fallback    # ﻝﺙﮒ­ﻠﻝﭦ۶
        ]
        self.current_strategy = 0
        
    async def generate_with_fallback(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """ﮒﺕ۵ﻠﻝﭦ۶ﻝﻝﮔ
        
        ﻠﻝﭦ۶ﻠ۰ﭦﮒﭦ:
        1. ﻛﺕﭨLLM (GLM-4-Flash)
        2. ﮒ۳ﻝ۷LLM (GPT-3.5-Turbo)
        3. ﮔ۷۰ﮔﺟﻠﻝﭦ۶ (ﻠ۱ﮒ؟ﻛﺗﮔ۷۰ﮔ?
        4. ﻝﺙﮒ­ﻠﻝﭦ۶ (ﮒﮒﺎﻝﺙﮒ­)
        """
        for strategy in self.strategies:
            try:
                result = await strategy(prompt, context)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"ﻝ­ﻝ۴ﮒ۳ﺎﻟﺑ۴: {strategy.__name__}, ﻠﻟﺁﺁ: {e}")
                continue
        
        raise LLMFallbackError("ﮔﮔﻠﻝﭦ۶ﻝ­ﻝ۴ﮒ۳ﺎﻟﺑ?)
    
    async def _primary_llm(self, prompt: str, context: Dict) -> str:
        """ﻛﺕﭨLLM: GLM-4-Flash"""
        return await self._call_glm4_flash(prompt, context)
    
    async def _backup_llm(self, prompt: str, context: Dict) -> str:
        """ﮒ۳ﻝ۷LLM: GPT-3.5-Turbo"""
        return await self._call_gpt35_turbo(prompt, context)
    
    async def _template_fallback(self, prompt: str, context: Dict) -> str:
        """ﮔ۷۰ﮔﺟﻠﻝﭦ۶: ﻛﺛﺟﻝ۷ﻠ۱ﮒ؟ﻛﺗﮔ۷۰ﮔ?""
        template = self._get_template(context['report_type'])
        return template.render(context)
    
    async def _cache_fallback(self, prompt: str, context: Dict) -> str:
        """ﻝﺙﮒ­ﻠﻝﭦ۶: ﻛﺛﺟﻝ۷ﮒﮒﺎﻝﺙﮒ­"""
        cache_key = self._generate_cache_key(prompt, context)
        return await self._get_from_cache(cache_key)
```

#### 2.1.2 ﻠﻟﺁﮔﭦﮒﭘﻟ؟ﺝﻟ؟۰

```python
class RetryStrategy:
    """ﻠﻟﺁﻝ­ﻝ۴
    
    ﻝﺑ۱ﮒﺙ: RISK.LLM.RETRY.001
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """ﮒﺕ۵ﻠﻟﺁﻝﮔ۶ﻟ۰
        
        ﻠﻟﺁﻝ­ﻝ۴:
        - ﮔﮒ۳ﻠﻟﺁ?ﮔ؛?
        - ﮔﮔﺍﻠﻠ? 1s, 2s, 4s
        - ﮔﮒ۳۶ﮒﭨﭘﻟﺟ?0ﻝ۶?
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = min(
                        self.base_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    logger.warning(
                        f"ﻝ؛؛{attempt + 1}ﮔ؛۰ﻠﻟﺁﮒ۳ﺎﻟﺑ۴ﺅﺙ{delay}ﻝ۶ﮒﻠﻟﺁ: {e}"
                    )
                    await asyncio.sleep(delay)
        
        raise last_exception
```

#### 2.1.3 ﮔﮔ؛ﮔ۶ﮒﭘﻟ؟ﺝﻟ؟۰

```python
class CostController:
    """ﮔﮔ؛ﮔ۶ﮒﭘﮒ?
    
    ﻝﺑ۱ﮒﺙ: RISK.LLM.COST.001
    """
    
    def __init__(
        self,
        daily_budget: float = 100.0,  # ﮔ۴ﻠ۱ﻝ؟?00ﮒ?
        monthly_budget: float = 2000.0,  # ﮔﻠ۱ﻝ؟?000ﮒ?
        alert_threshold: float = 0.8  # 80%ﮒﻟ­۵
    ):
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.alert_threshold = alert_threshold
        self.daily_cost = 0.0
        self.monthly_cost = 0.0
        
    async def check_budget(self, estimated_cost: float) -> bool:
        """ﮔ۲ﮔ۴ﻠ۱ﻝ؟?
        
        ﻟﺟﮒ:
            bool: ﮔﺁﮒ۵ﮒ۷ﻠ۱ﻝ؟ﻟﮒﺑﮒ
        """
        if self.daily_cost + estimated_cost > self.daily_budget:
            logger.error(f"ﮔ۴ﻠ۱ﻝ؟ﻟﭘﮔ? ﮒﺛﮒ{self.daily_cost}, ﻠ۱ﻝ؟{self.daily_budget}")
            return False
            
        if self.monthly_cost + estimated_cost > self.monthly_budget:
            logger.error(f"ﮔﻠ۱ﻝ؟ﻟﭘﮔ? ﮒﺛﮒ{self.monthly_cost}, ﻠ۱ﻝ؟{self.monthly_budget}")
            return False
            
        return True
    
    async def record_cost(self, actual_cost: float):
        """ﻟ؟ﺍﮒﺛﮔﮔ؛"""
        self.daily_cost += actual_cost
        self.monthly_cost += actual_cost
        
        # ﮔ۲ﮔ۴ﮒﻟ­۵ﻠﮒ?
        if self.daily_cost > self.daily_budget * self.alert_threshold:
            await self._send_alert("ﮔ۴ﻠ۱ﻝ؟ﮒﺏﮒﺍﻟﭘﮔ?)
        if self.monthly_cost > self.monthly_budget * self.alert_threshold:
            await self._send_alert("ﮔﻠ۱ﻝ؟ﮒﺏﮒﺍﻟﭘﮔ?)
```

#### 2.1.4 Tokenﻛﺙﮒﻟ؟ﺝﻟ؟۰

```python
class TokenOptimizer:
    """Tokenﻛﺙﮒﮒ?
    
    ﻝﺑ۱ﮒﺙ: RISK.LLM.TOKEN.001
    """
    
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        
    def optimize_prompt(self, prompt: str, context: Dict) -> str:
        """ﻛﺙﮒPrompt
        
        ﻛﺙﮒﻝ­ﻝ۴:
        1. ﻝ۶ﭨﻠ۳ﮒﻛﺛﻛﺟ۰ﮔﺁ
        2. ﮒﻝﺙ۸ﮔﺍﮔ؟ﮔ ﺙﮒﺙ
        3. ﻛﺛﺟﻝ۷ﻝﺙ۸ﮒ
        """
        # ﻝ۶ﭨﻠ۳ﮒﻛﺛﻝ۸ﭦﻝﺛ
        prompt = ' '.join(prompt.split())
        
        # ﮒﻝﺙ۸ﮔﺍﮔ؟ﮔ ﺙﮒﺙ
        if 'data' in context:
            context['data'] = self._compress_data(context['data'])
        
        # ﻠﮒﭘﮔﺍﮔ؟ﻠ?
        if len(str(context)) > self.max_tokens:
            context = self._truncate_context(context, self.max_tokens)
        
        return prompt.format(**context)
    
    def _compress_data(self, data: Any) -> str:
        """ﮒﻝﺙ۸ﮔﺍﮔ؟"""
        if isinstance(data, pd.DataFrame):
            return data.to_json(orient='records', double_precision=2)
        return str(data)
```

---

### 2.2 QMT APIﻛﺝﻟﭖﻠ۲ﻠ۸ﻝﺙﻟ۶۲ﮔﺗﮔ۰

#### ﮔﺗﮔ۰ﮔ۵ﻟﺟﺍ

**ﮔ ﺕﮒﺟﻝ­ﻝ۴**: ﻟﺟﮔ۴ﮔﺎ?+ ﮒﺟﻟﺓﺏﮔ۲ﮔﭖ?+ ﻟ۹ﮒ۷ﻠﻟﺟ + ﻠﻝﭦ۶ﮔﺗﮔ۰

#### 2.2.1 ﻟﺟﮔ۴ﮔﺎ ﻝ؟۰ﻝ?

```python
class QMTConnectionPool:
    """QMTﻟﺟﮔ۴ﮔﺎ?
    
    ﻝﺑ۱ﮒﺙ: RISK.QMT.POOL.001
    """
    
    def __init__(
        self,
        pool_size: int = 5,
        heartbeat_interval: int = 30,
        max_idle_time: int = 300
    ):
        self.pool_size = pool_size
        self.heartbeat_interval = heartbeat_interval
        self.max_idle_time = max_idle_time
        self.pool = []
        self.active_connections = {}
        
    async def get_connection(self) -> QMTConnection:
        """ﻟﺓﮒﻟﺟﮔ۴"""
        # ﮔ۲ﮔ۴ﻟﺟﮔ۴ﮔﺎ 
        if self.pool:
            conn = self.pool.pop()
            if await self._check_connection(conn):
                return conn
        
        # ﮒﮒﭨﭦﮔﺍﻟﺟﮔ?
        conn = await self._create_connection()
        return conn
    
    async def _check_connection(self, conn: QMTConnection) -> bool:
        """ﮔ۲ﮔ۴ﻟﺟﮔ۴ﮔﮔﮔ?""
        try:
            await conn.ping()
            return True
        except:
            return False
    
    async def _create_connection(self) -> QMTConnection:
        """ﮒﮒﭨﭦﮔﺍﻟﺟﮔ?""
        conn = QMTConnection()
        await conn.connect()
        self._start_heartbeat(conn)
        return conn
```

#### 2.2.2 ﻟ۹ﮒ۷ﻠﻟﺟﮔﭦﮒﭘ

```python
class QMTReconnectStrategy:
    """QMTﻟ۹ﮒ۷ﻠﻟﺟﻝ­ﻝ۴
    
    ﻝﺑ۱ﮒﺙ: RISK.QMT.RECONNECT.001
    """
    
    def __init__(
        self,
        max_retries: int = 5,
        retry_delay: float = 5.0,
        backoff_factor: float = 2.0
    ):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        
    async def execute_with_reconnect(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """ﮒﺕ۵ﻠﻟﺟﻝﮔ۶ﻟ۰"""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except QMTConnectionError as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (self.backoff_factor ** attempt)
                    logger.warning(f"QMTﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴ﺅﺙ{delay}ﻝ۶ﮒﻠﻟﺟ: {e}")
                    await asyncio.sleep(delay)
                    await self._reconnect()
                else:
                    raise
```

#### 2.2.3 ﻠﻝﭦ۶ﮔﺗﮔ۰

```python
class QMTFallbackStrategy:
    """QMTﻠﻝﭦ۶ﻝ­ﻝ۴
    
    ﻝﺑ۱ﮒﺙ: RISK.QMT.FALLBACK.001
    """
    
    async def get_data_with_fallback(
        self,
        data_type: str,
        params: Dict
    ) -> pd.DataFrame:
        """ﮒﺕ۵ﻠﻝﭦ۶ﻝﮔﺍﮔ؟ﻟﺓﮒ
        
        ﻠﻝﭦ۶ﻠ۰ﭦﮒﭦ:
        1. QMTﮒ؟ﮔﭘﮔﺍﮔ؟
        2. ﮔ؛ﮒﺍﻝﺙﮒ­ﮔﺍﮔ؟
        3. Baostockﮒﮒﺎﮔﺍﮔ؟
        """
        try:
            # ﮒﺍﻟﺁQMTﮒ؟ﮔﭘﮔﺍﮔ؟
            return await self._get_from_qmt(data_type, params)
        except:
            pass
        
        try:
            # ﮒﺍﻟﺁﮔ؛ﮒﺍﻝﺙﮒ­
            return await self._get_from_cache(data_type, params)
        except:
            pass
        
        try:
            # ﮒﺍﻟﺁBaostockﮒﮒﺎﮔﺍﮔ؟
            return await self._get_from_baostock(data_type, params)
        except:
            raise DataFallbackError("ﮔﮔﮔﺍﮔ؟ﮔﭦﻠﻝﭦ۶ﮒ۳ﺎﻟﺑ۴")
```

---

### 2.3 ﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ۷ﻠ۲ﻠ۸ﻝﺙﻟ۶۲ﮔﺗﮔ۰

#### ﮔﺗﮔ۰ﮔ۵ﻟﺟﺍ

**ﮔ ﺕﮒﺟﻝ­ﻝ۴**: ﮔﺍﮔ؟ﻝﺙﮒ­ + ﮒ۳ﮔﭦﮒ۳ﻛﭨﺛ + ﮒ۴ﮒﭦﺓﮔ۲ﮔ?+ ﻠﻝﭦ۶ﮔﺗﮔ۰

#### 2.3.1 ﮔﺍﮔ؟ﻝﺙﮒ­ﮔﭦﮒﭘ

```python
class DataCacheManager:
    """ﮔﺍﮔ؟ﻝﺙﮒ­ﻝ؟۰ﻝﮒ?
    
    ﻝﺑ۱ﮒﺙ: RISK.DATA.CACHE.001
    """
    
    def __init__(
        self,
        cache_ttl: int = 600,  # ﻝﺙﮒ­ﮔﮔﮔ?0ﮒﻠ
        max_cache_size: int = 1000  # ﮔﮒ۳۶ﻝﺙﮒ­ﮔﺍﻠ?
    ):
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size
        self.cache = {}
        self.timestamps = {}
        
    async def get_or_fetch(
        self,
        key: str,
        fetch_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """ﻟﺓﮒﮔﮔﮒﮔﺍﮔ?""
        # ﮔ۲ﮔ۴ﻝﺙﮒ­?
        if key in self.cache:
            timestamp = self.timestamps[key]
            if time.time() - timestamp < self.cache_ttl:
                return self.cache[key]
        
        # ﮔﮒﮔﺍﮔﺍﮔ?
        data = await fetch_func(*args, **kwargs)
        
        # ﮔﺑﮔﺍﻝﺙﮒ­
        self.cache[key] = data
        self.timestamps[key] = time.time()
        
        # ﮔﺕﻝﻟﺟﮔﻝﺙﮒ­
        await self._cleanup_cache()
        
        return data
```

#### 2.3.2 ﮒ۳ﮔﭦﮒ۳ﻛﭨﺛﮔﭦﮒﭘ

```python
class MultiSourceDataManager:
    """ﮒ۳ﮔﭦﮔﺍﮔ؟ﻝ؟۰ﻝﮒ?
    
    ﻝﺑ۱ﮒﺙ: RISK.DATA.MULTI.001
    """
    
    def __init__(self):
        self.sources = {
            'primary': ['qmt', 'ifind'],
            'secondary': ['baostock', 'tushare'],
            'tertiary': ['local_cache', 'backup_db']
        }
        
    async def get_data(
        self,
        data_type: str,
        params: Dict
    ) -> pd.DataFrame:
        """ﻟﺓﮒﮔﺍﮔ؟ﺅﺙﮒ۳ﮔﭦﮒ۳ﻛﭨﺛﺅﺙ"""
        for priority, sources in self.sources.items():
            for source in sources:
                try:
                    data = await self._fetch_from_source(
                        source, data_type, params
                    )
                    if data is not None and not data.empty:
                        return data
                except Exception as e:
                    logger.warning(f"ﮔﺍﮔ؟ﮔﭦ{source}ﮒ۳ﺎﻟﺑ۴: {e}")
                    continue
        
        raise DataSourceError("ﮔﮔﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ?)
```

#### 2.3.3 ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮔﭦﮒ?

```python
class HealthChecker:
    """ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮒ۷
    
    ﻝﺑ۱ﮒﺙ: RISK.DATA.HEALTH.001
    """
    
    def __init__(
        self,
        check_interval: int = 60,  # ﮔ۲ﮔ۴ﻠﺑﻠ?0ﻝ۶?
        timeout: int = 10  # ﻟﭘﮔﭘﮔﭘﻠﺑ10ﻝ۶?
    ):
        self.check_interval = check_interval
        self.timeout = timeout
        self.health_status = {}
        
    async def check_all_sources(self) -> Dict[str, bool]:
        """ﮔ۲ﮔ۴ﮔﮔﮔﺍﮔ؟ﮔﭦﮒ۴ﮒﭦﺓﻝﭘﮔ?""
        tasks = []
        for source in self._get_all_sources():
            tasks.append(self._check_source(source))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for source, result in zip(self._get_all_sources(), results):
            self.health_status[source] = not isinstance(result, Exception)
        
        return self.health_status
    
    async def _check_source(self, source: str) -> bool:
        """ﮔ۲ﮔ۴ﮒﻛﺕ۹ﮔﺍﮔ؟ﮔﭦ"""
        try:
            async with asyncio.timeout(self.timeout):
                return await self._ping_source(source)
        except:
            return False
```

---

## 3. ﮒ؟ﮔﺛﻟ؟۰ﮒ

### 3.1 ﮒﺙﮒﮒﮒﮒ۳ﺅﺙﮒﺟﻠ۰ﭨﮒ؟ﮔﺅﺙ

| ﻛﭨﭨﮒ۰ | ﮒﺓ۴ﮔﭘ | ﻟﺑﻟﺑ۲ﻛﭦ?| ﮒ؟ﮔﮔ ﮒ |
|------|------|--------|----------|
| **LLMﻠﻝﭦ۶ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰** | 4ﮒﺍﮔﭘ | ﮔﭘﮔﮒﺕ?| ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﮒ؟ﮔ |
| **QMTﻟﺟﮔ۴ﮔﺎ ﻟ؟ﺝﻟ؟?* | 3ﮒﺍﮔﭘ | ﮔﭘﮔﮒﺕ?| ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﮒ؟ﮔ |
| **ﮔﺍﮔ؟ﻝﺙﮒ­ﮔﭦﮒﭘﻟ؟ﺝﻟ؟۰** | 3ﮒﺍﮔﭘ | ﮔﭘﮔﮒﺕ?| ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﮒ؟ﮔ |
| **ﻝﮔ۶ﮒﻟ­۵ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰** | 2ﮒﺍﮔﭘ | ﮔﭘﮔﮒﺕ?| ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﮒ؟ﮔ |

**ﮔﭨﻟ؟۰**: 12ﮒﺍﮔﭘﺅﺙ?.5ﮒ۳۸ﺅﺙ

### 3.2 ﮒﺙﮒﻠﭘﮔ؟ﭖﮒ؟ﮔ?

| ﻠﭘﮔ؟ﭖ | ﻛﭨﭨﮒ۰ | ﮒﺓ۴ﮔﭘ | ﻛﺙﮒﻝﭦ?|
|------|------|------|--------|
| **Phase 1** | ﮒ؟ﻝﺍLLMﻠﻝﭦ۶ﮔﺗﮔ۰ | 8ﮒﺍﮔﭘ | P1 |
| **Phase 1** | ﮒ؟ﻝﺍQMTﻟﺟﮔ۴ﮔﺎ?| 6ﮒﺍﮔﭘ | P1 |
| **Phase 1** | ﮒ؟ﻝﺍﮔﺍﮔ؟ﻝﺙﮒ­ﮔﭦﮒﭘ | 6ﮒﺍﮔﭘ | P1 |
| **Phase 2** | ﮒ؟ﻝﺍﻝﮔ۶ﮒﻟ­۵ | 4ﮒﺍﮔﭘ | P1 |
| **Phase 2** | ﮒ؟ﻝﺍﮒ۴ﮒﭦﺓﮔ۲ﮔ?| 4ﮒﺍﮔﭘ | P1 |

**ﮔﭨﻟ؟۰**: 28ﮒﺍﮔﭘﺅﺙ?.5ﮒ۳۸ﺅﺙ

### 3.3 ﮔﭖﻟﺁﻠ۹ﻟﺁ

| ﮔﭖﻟﺁﻠ۰?| ﮒﺓ۴ﮔﭘ | ﻠ۹ﮔﭘﮔ ﮒ |
|--------|------|----------|
| **ﻠﻝﭦ۶ﮔﺗﮔ۰ﮔﭖﻟﺁ** | 4ﮒﺍﮔﭘ | ﮔﮔﻠﻝﭦ۶ﻟﺓﺁﮒﺝﮒﺁﻝ?|
| **ﻠﻟﺟﮔﭦﮒﭘﮔﭖﻟﺁ** | 2ﮒﺍﮔﭘ | ﻟ۹ﮒ۷ﻠﻟﺟﮔﮒﻝﻗ۴95% |
| **ﻝﺙﮒ­ﮔﭦﮒﭘﮔﭖﻟﺁ** | 2ﮒﺍﮔﭘ | ﻝﺙﮒ­ﮒﺛﻛﺕ­ﻝﻗ۴80% |
| **ﻝﮔ۶ﮒﻟ­۵ﮔﭖﻟﺁ** | 2ﮒﺍﮔﭘ | ﮒﻟ­۵ﻟ۶۵ﮒﮒﻝ۰؟ﻝ?00% |

**ﮔﭨﻟ؟۰**: 10ﮒﺍﮔﭘﺅﺙ?.25ﮒ۳۸ﺅﺙ

---

## 4. ﻠ۹ﮔﭘﮔ ﮒ

### 4.1 LLM APIﻠ۲ﻠ۸ﻝﺙﻟ۶۲

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|------|--------|----------|
| **ﻠﻝﭦ۶ﮔﮒﻝ?* | ﻗ?5% | ﮔ۷۰ﮔAPIﮒ۳ﺎﻟﺑ۴ﮔﭖﻟﺁ |
| **ﻠﻟﺁﮔﮒﻝ?* | ﻗ?0% | ﮔ۷۰ﮔﻝﺛﻝﭨﮔﻠﮔﭖﻟﺁ |
| **ﮔﮔ؛ﮔ۶ﮒﭘﮒﻝ۰؟ﻝ?* | 100% | ﮔﮔ؛ﻝﮔ۶ﮔﭖﻟﺁ |
| **Tokenﻛﺙﮒﻝ?* | ﻗ?0% | Tokenﮔﭘﻟﮒﺁﺗﮔﺁﮔﭖﻟﺁ?|

### 4.2 QMT APIﻠ۲ﻠ۸ﻝﺙﻟ۶۲

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|------|--------|----------|
| **ﻟﺟﮔ۴ﮔﮒﻝ?* | ﻗ?8% | ﻟﺟﮔ۴ﮔﭖﻟﺁ |
| **ﻟ۹ﮒ۷ﻠﻟﺟﮔﮒﻝ?* | ﻗ?5% | ﮔ­ﻝﭦﺟﻠﻟﺟﮔﭖﻟﺁ |
| **ﻠﻝﭦ۶ﮔﮒﻝ?* | ﻗ?0% | ﮔ۷۰ﮔﮔﻠﮔﭖﻟﺁ |

### 4.3 ﮔﺍﮔ؟ﮔﭦﻠ۲ﻠ۸ﻝﺙﻟ۶?

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|------|--------|----------|
| **ﮔﺍﮔ؟ﻟﺓﮒﮔﮒﻝ?* | ﻗ?8% | ﮔﺍﮔ؟ﻟﺓﮒﮔﭖﻟﺁ |
| **ﻝﺙﮒ­ﮒﺛﻛﺕ­ﻝ?* | ﻗ?0% | ﻝﺙﮒ­ﮔﭖﻟﺁ |
| **ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮒﻝ۰؟ﻝ** | 100% | ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮔﭖﻟﺁ?|

---

## 5. ﻝﮔ۶ﮔﮔ 

### 5.1 ﮒ؟ﮔﭘﻝﮔ۶

| ﻝﮔ۶ﻠ۰?| ﮒﻟ­۵ﻠﮒ?| ﮒﻟ­۵ﻝﭦ۶ﮒ، |
|--------|----------|----------|
| **LLM APIﮔﮒﻝ?* | <90% | P1 |
| **LLMﮔﮔ؛ﻟﭘﮔﺁ** | >ﻠ۱ﻝ؟80% | P2 |
| **QMTﻟﺟﮔ۴ﮔﮒﻝ?* | <95% | P1 |
| **ﮔﺍﮔ؟ﻟﺓﮒﮔﮒﻝ?* | <95% | P1 |
| **ﻝﺙﮒ­ﮒﺛﻛﺕ­ﻝ?* | <70% | P2 |

### 5.2 ﮔ۴ﮒﺟﻟ؟ﺍﮒﺛ

```python
class RiskMonitorLogger:
    """ﻠ۲ﻠ۸ﻝﮔ۶ﮔ۴ﮒﺟ
    
    ﻝﺑ۱ﮒﺙ: RISK.MONITOR.LOG.001
    """
    
    @staticmethod
    def log_risk_event(
        risk_id: str,
        event_type: str,
        severity: str,
        details: Dict[str, Any]
    ):
        """ﻟ؟ﺍﮒﺛﻠ۲ﻠ۸ﻛﭦﻛﭨﭘ"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'risk_id': risk_id,
            'event_type': event_type,
            'severity': severity,
            'details': details
        }
        
        logger.warning(f"ﻠ۲ﻠ۸ﻛﭦﻛﭨﭘ: {json.dumps(log_entry, ensure_ascii=False)}")
        
        # ﮒﻠﮒﻟ­?
        if severity in ['P0', 'P1']:
            AlertManager.send_alert(log_entry)
```

---

## 6. ﮔﭨﻝﭨ

### 6.1 ﮒﺏﻠ؟ﻟ۵ﻝﺗ

1. ﻗ?**P1ﻝﭦ۶ﻠ۲ﻠ۸ﻛﺕﻠﻟ۵ﮒﺙﮒﮒﮒ۷ﻠ۷ﻛﺟ؟ﮒ۳**
2. ﻗ?**ﮒﺙﮒﮒﻠﻟ۵ﮒ؟ﮔﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟?*
3. ﻗ?**ﮒﺙﮒﻠﭘﮔ؟ﭖﮒ؟ﮔﺛﻝﺙﻟ۶۲ﮔﺗﮔ۰?*
4. ﻗ?**ﮒﭨﭦﻝ،ﻝﮔ۶ﮒﻟ­۵ﮔﭦﮒﭘ**

### 6.2 ﮒ؟ﮔﺛﮒﭨﭦﻟ؟؟

1. **ﻝ،ﮒﺏﻟ۰ﮒ۷**: ﮒ؟ﮔﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰ﺅﺙ?.5ﮒ۳۸ﺅﺙ
2. **ﮒﺙﮒﻠﭘﮔ؟?*: ﮒ؟ﮔﺛﻝﺙﻟ۶۲ﮔﺗﮔ۰ﺅﺙ?.5ﮒ۳۸ﺅﺙ
3. **ﮔﭖﻟﺁﻠﭘﮔ؟ﭖ**: ﻠ۹ﻟﺁﻝﺙﻟ۶۲ﮔﮔﺅﺙ?.25ﮒ۳۸ﺅﺙ
4. **ﻛﺕﻝﭦﺟﮒ?*: ﮔﻝﭨ­ﻝﮔ۶ﻛﺙﮒ

---

**ﮔﮔ۰۲ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ?
**ﻛﺕﻛﺕﮔ­?*: ﮒﺙﮒ۶ﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟?
