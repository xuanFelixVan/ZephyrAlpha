﻿---
document_type: P1ﻝﭦ۶ﻠ۲ﻠ۸ﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟?
version: 1.0.0
created_date: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 实施指南、部署文档
  - 数据源
  - 文档治理
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻠ۲ﻠ۸ﻝ؟۰ﻝ
compliance_level: ﻛﺕﻛﺕﮔ ﮒ
status: ﮒﺝﮒ؟ﮔ?
applicable_scope: ﻝﺏﭨﻝﭨﮒ؟ﮔﺛ
parent_document: ../INDEX.md
implementation_status: ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ
module_id: IMP_P1_RISK_MITIGATION_D
last_updated: 2026-04-02---


# P1ﻝﭦ۶ﻠ۲ﻠ۸ﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰ﮔﮔ۰?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02
> **ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶**: P1 (ﻠ،?
> **ﻠ۲ﻠ۸ﮔﺍﻠ**: 18ﻛﺕ?
> **ﮒ۳ﻝﮒﮒ**: ﮒﺙﮒﮒﻟ؟ﺝﻟ؟۰ﮔﺗﮔ۰ﺅﺙﮒﺙﮒﻠﭘﮔ؟ﭖﮒ؟ﮔ?

---

## 1. P1ﻝﭦ۶ﻠ۲ﻠ۸ﮔﺕﮒ?

### 1.1 ﮒ۳ﻠ۷APIﻛﺝﻟﭖﻠ۲ﻠ۸ﺅﺙ?2ﻛﺕ۹ﺅﺙ

| ﻠ۲ﻠ۸ID | ﻠ۲ﻠ۸ﮔﻟﺟﺍ | ﮔﭘﮒﮔ۷۰ﮒ | ﮒﺛﺎﮒﻟﮒﺑ |
|--------|----------|----------|----------|
| **R-LLM-001** | GLM-4-Flash APIﻟﺍﻝ۷ﮒ۳ﺎﻟﺑ۴ | DailyReporter, MonthlyReporter, MarketAnalyzer | AIﮔ۴ﮒﻝﮔﮒ۳ﺎﻟﺑ۴ |
| **R-LLM-002** | GLM-4-Flash APIﻟﭘﮔﭘ | DailyReporter, MonthlyReporter, MarketAnalyzer | ﮔ۴ﮒﻝﮔﮒﭨﭘﻟﺟ |
| **R-LLM-003** | GLM-4-Flash APIﮔﮔ؛ﻟﭘﮔﺁ | ﮔﮔLLMﻠﮔﮔ۷۰ﮒ | ﮔﮔ؛ﮔ۶ﮒﭘﮒ۳ﺎﮔ |
| **R-QMT-001** | QMTﮒ؟۱ﮔﺓﻝ،ﺁﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ?| QMTDataInterface, QMTExecutor | ﮔﺍﮔ؟ﻟﺓﮒﮒ۳ﺎﻟﺑ۴ﻙﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ?|
| **R-QMT-002** | QMT APIﮒﮒﭦﻟﭘﮔﭘ | QMTDataInterface, QMTExecutor | ﮔﺍﮔ؟ﮒﭨﭘﻟﺟﻙﻛﭦ۳ﮔﮒﭨﭘﻟﺟ?|
| **R-IFIND-001** | iFindﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ۷ | iFindConnector | ﮒ ﮒ­ﮔﺍﮔ؟ﻝﺙﭦﮒ۳ﺎ |
| **R-IFIND-002** | iFind APIﻠﮔﭖ | iFindConnector | ﮔﺍﮔ؟ﻟﺓﮒﮒﻠ |
| **R-NEWS-001** | ﮔﺍﻠﭨﻝ؛ﻟ،ﻟ۱،ﮒﺍﻝ۵?| NewsCrawler | ﻟﮔﮔﺍﮔ؟ﻝﺙﭦﮒ۳ﺎ |
| **R-NEWS-002** | ﮔﺍﻠﭨAPIﻛﺕﮒﺁﻝ?| NewsCrawler | ﻟﮔﮔﺍﮔ؟ﻝﺙﭦﮒ۳ﺎ |
| **R-DINGTALK-001** | ﻠﻠAPIﻛﺕﮒﺁﻝ?| NotificationSystem | ﻠﻝ۴ﮒﻠﮒ۳ﺎﻟﺑ?|
| **R-WECHAT-001** | ﻛﺙﻛﺕﮒﺝ؟ﻛﺟ۰APIﻛﺕﮒﺁﻝ?| NotificationSystem | ﻠﻝ۴ﮒﻠﮒ۳ﺎﻟﺑ?|
| **R-SMS-001** | ﻝ­ﻛﺟ۰APIﻛﺕﮒﺁﻝ?| NotificationSystem | ﻠﻝ۴ﮒﻠﮒ۳ﺎﻟﺑ?|

### 1.2 ﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ۷ﻠ۲ﻠ۸ﺅﺙ?ﻛﺕ۹ﺅﺙ

| ﻠ۲ﻠ۸ID | ﻠ۲ﻠ۸ﮔﻟﺟﺍ | ﮔﭘﮒﮔ۷۰ﮒ | ﮒﺛﺎﮒﻟﮒﺑ |
|--------|----------|----------|----------|
| **R-DATA-001** | ﻛﺕﮔﺕﺕﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ۷ | ﮔﮔLayer 0ﮔ۷۰ﮒ | ﮔﺍﮔ؟ﻟﺓﮒﮒ۳ﺎﻟﺑ۴ |
| **R-DATA-002** | ﮔﺍﮔ؟ﮒﭦﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ?| DataStorage, PositionManager | ﮔﺍﮔ؟ﮔﻛﺗﮒﮒ۳ﺎﻟﺑ?|
| **R-DATA-003** | ﻝﺙﮒ­ﮔﮒ۰ﻛﺕﮒﺁﻝ?| ﮔﮔﻝﺙﮒ­ﮔ۷۰ﮒ?| ﮔ۶ﻟﺛﻛﺕﻠ |
| **R-DATA-004** | ﮔﺍﮔ؟ﻟﺑ۷ﻠﮒﺙﮒﺕﺕ | DataValidator, DataCleaner | ﮔﺍﮔ؟ﻠﻟﺁﺁ |
| **R-DATA-005** | ﮔﺍﮔ؟ﮒﭨﭘﻟﺟﻟﺟﻠ، | ﮔﮔﮒ؟ﮔﭘﮔﺍﮔ؟ﮔ۷۰ﮒ?| ﮒ؟ﮔﭘﮔ۶ﻛﺕﻠ?|
| **R-DATA-006** | ﮔﺍﮔ؟ﮒ­ﮒ۷ﻝ۸ﭦﻠﺑﻛﺕﻟﭘﺏ | DataStorage, TradeAuditor | ﮔﺍﮔ؟ﻛﺟﮒ­ﮒ۳ﺎﻟﺑ۴ |

---

## 2. ﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰

### 2.1 LLM APIﻛﺝﻟﭖﻠ۲ﻠ۸ﻝﺙﻟ۶۲ﮔﺗﮔ۰

#### ﮔﺗﮔ۰ﮔ۵ﻟﺟﺍ

**ﮔ ﺕﮒﺟﻝ­ﻝ۴**: ﻠﻝﭦ۶ﮔﺗﮔ۰ + ﻠﻟﺁﮔﭦﮒﭘ + ﮔﮔ؛ﮔ۶ﮒﭘ + ﮒ۳ﮔ۷۰ﮒﮒ۳ﻛﭨ?

#### 2.1.1 ﻠﻝﭦ۶ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰

```python
class LLMFallbackStrategy:
    """LLMﻠﻝﭦ۶ﻝ­ﻝ۴
    
    ﻝﺑ۱ﮒﺙ: RISK.LLM.FALLBACK.001
    """
    
    def __init__(self):
        self.strategies = [
            self._primary_llm,      # ﻛﺕﭨLLM (GLM-4-Flash)
            self._backup_llm,       # ﮒ۳ﻝ۷LLM (GPT-3.5-Turbo)
            self._template_fallback, # ﮔ۷۰ﮔﺟﻠﻝﭦ۶
            self._cache_fallback    # ﻝﺙﮒ­ﻠﻝﭦ۶
        ]
        self.current_strategy = 0
        
    async def generate_with_fallback(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """ﮒﺕ۵ﻠﻝﭦ۶ﻝﻝﮔ
        
        ﻠﻝﭦ۶ﻠ۰ﭦﮒﭦ:
        1. ﻛﺕﭨLLM (GLM-4-Flash)
        2. ﮒ۳ﻝ۷LLM (GPT-3.5-Turbo)
        3. ﮔ۷۰ﮔﺟﻠﻝﭦ۶ (ﻠ۱ﮒ؟ﻛﺗﮔ۷۰ﮔ?
        4. ﻝﺙﮒ­ﻠﻝﭦ۶ (ﮒﮒﺎﻝﺙﮒ­)
        """
        for strategy in self.strategies:
            try:
                result = await strategy(prompt, context)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"ﻝ­ﻝ۴ﮒ۳ﺎﻟﺑ۴: {strategy.__name__}, ﻠﻟﺁﺁ: {e}")
                continue
        
        raise LLMFallbackError("ﮔﮔﻠﻝﭦ۶ﻝ­ﻝ۴ﮒ۳ﺎﻟﺑ?)
    
    async def _primary_llm(self, prompt: str, context: Dict) -> str:
        """ﻛﺕﭨLLM: GLM-4-Flash"""
        return await self._call_glm4_flash(prompt, context)
    
    async def _backup_llm(self, prompt: str, context: Dict) -> str:
        """ﮒ۳ﻝ۷LLM: GPT-3.5-Turbo"""
        return await self._call_gpt35_turbo(prompt, context)
    
    async def _template_fallback(self, prompt: str, context: Dict) -> str:
        """ﮔ۷۰ﮔﺟﻠﻝﭦ۶: ﻛﺛﺟﻝ۷ﻠ۱ﮒ؟ﻛﺗﮔ۷۰ﮔ?""
        template = self._get_template(context['report_type'])
        return template.render(context)
    
    async def _cache_fallback(self, prompt: str, context: Dict) -> str:
        """ﻝﺙﮒ­ﻠﻝﭦ۶: ﻛﺛﺟﻝ۷ﮒﮒﺎﻝﺙﮒ­"""
        cache_key = self._generate_cache_key(prompt, context)
        return await self._get_from_cache(cache_key)
```

#### 2.1.2 ﻠﻟﺁﮔﭦﮒﭘﻟ؟ﺝﻟ؟۰

```python
class RetryStrategy:
    """ﻠﻟﺁﻝ­ﻝ۴
    
    ﻝﺑ۱ﮒﺙ: RISK.LLM.RETRY.001
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
        """ﮒﺕ۵ﻠﻟﺁﻝﮔ۶ﻟ۰
        
        ﻠﻟﺁﻝ­ﻝ۴:
        - ﮔﮒ۳ﻠﻟﺁ?ﮔ؛?
        - ﮔﮔﺍﻠﻠ? 1s, 2s, 4s
        - ﮔﮒ۳۶ﮒﭨﭘﻟﺟ?0ﻝ۶?
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
                        f"ﻝ؛؛{attempt + 1}ﮔ؛۰ﻠﻟﺁﮒ۳ﺎﻟﺑ۴ﺅﺙ{delay}ﻝ۶ﮒﻠﻟﺁ: {e}"
                    )
                    await asyncio.sleep(delay)
        
        raise last_exception
```

#### 2.1.3 ﮔﮔ؛ﮔ۶ﮒﭘﻟ؟ﺝﻟ؟۰

```python
class CostController:
    """ﮔﮔ؛ﮔ۶ﮒﭘﮒ?
    
    ﻝﺑ۱ﮒﺙ: RISK.LLM.COST.001
    """
    
    def __init__(
        self,
        daily_budget: float = 100.0,  # ﮔ۴ﻠ۱ﻝ؟?00ﮒ?
        monthly_budget: float = 2000.0,  # ﮔﻠ۱ﻝ؟?000ﮒ?
        alert_threshold: float = 0.8  # 80%ﮒﻟ­۵
    ):
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.alert_threshold = alert_threshold
        self.daily_cost = 0.0
        self.monthly_cost = 0.0
        
    async def check_budget(self, estimated_cost: float) -> bool:
        """ﮔ۲ﮔ۴ﻠ۱ﻝ؟?
        
        ﻟﺟﮒ:
            bool: ﮔﺁﮒ۵ﮒ۷ﻠ۱ﻝ؟ﻟﮒﺑﮒ
        """
        if self.daily_cost + estimated_cost > self.daily_budget:
            logger.error(f"ﮔ۴ﻠ۱ﻝ؟ﻟﭘﮔ? ﮒﺛﮒ{self.daily_cost}, ﻠ۱ﻝ؟{self.daily_budget}")
            return False
            
        if self.monthly_cost + estimated_cost > self.monthly_budget:
            logger.error(f"ﮔﻠ۱ﻝ؟ﻟﭘﮔ? ﮒﺛﮒ{self.monthly_cost}, ﻠ۱ﻝ؟{self.monthly_budget}")
            return False
            
        return True
    
    async def record_cost(self, actual_cost: float):
        """ﻟ؟ﺍﮒﺛﮔﮔ؛"""
        self.daily_cost += actual_cost
        self.monthly_cost += actual_cost
        
        # ﮔ۲ﮔ۴ﮒﻟ­۵ﻠﮒ?
        if self.daily_cost > self.daily_budget * self.alert_threshold:
            await self._send_alert("ﮔ۴ﻠ۱ﻝ؟ﮒﺏﮒﺍﻟﭘﮔ?)
        if self.monthly_cost > self.monthly_budget * self.alert_threshold:
            await self._send_alert("ﮔﻠ۱ﻝ؟ﮒﺏﮒﺍﻟﭘﮔ?)
```

#### 2.1.4 Tokenﻛﺙﮒﻟ؟ﺝﻟ؟۰

```python
class TokenOptimizer:
    """Tokenﻛﺙﮒﮒ?
    
    ﻝﺑ۱ﮒﺙ: RISK.LLM.TOKEN.001
    """
    
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        
    def optimize_prompt(self, prompt: str, context: Dict) -> str:
        """ﻛﺙﮒPrompt
        
        ﻛﺙﮒﻝ­ﻝ۴:
        1. ﻝ۶ﭨﻠ۳ﮒﻛﺛﻛﺟ۰ﮔﺁ
        2. ﮒﻝﺙ۸ﮔﺍﮔ؟ﮔ ﺙﮒﺙ
        3. ﻛﺛﺟﻝ۷ﻝﺙ۸ﮒ
        """
        # ﻝ۶ﭨﻠ۳ﮒﻛﺛﻝ۸ﭦﻝﺛ
        prompt = ' '.join(prompt.split())
        
        # ﮒﻝﺙ۸ﮔﺍﮔ؟ﮔ ﺙﮒﺙ
        if 'data' in context:
            context['data'] = self._compress_data(context['data'])
        
        # ﻠﮒﭘﮔﺍﮔ؟ﻠ?
        if len(str(context)) > self.max_tokens:
            context = self._truncate_context(context, self.max_tokens)
        
        return prompt.format(**context)
    
    def _compress_data(self, data: Any) -> str:
        """ﮒﻝﺙ۸ﮔﺍﮔ؟"""
        if isinstance(data, pd.DataFrame):
            return data.to_json(orient='records', double_precision=2)
        return str(data)
```

---

### 2.2 QMT APIﻛﺝﻟﭖﻠ۲ﻠ۸ﻝﺙﻟ۶۲ﮔﺗﮔ۰

#### ﮔﺗﮔ۰ﮔ۵ﻟﺟﺍ

**ﮔ ﺕﮒﺟﻝ­ﻝ۴**: ﻟﺟﮔ۴ﮔﺎ?+ ﮒﺟﻟﺓﺏﮔ۲ﮔﭖ?+ ﻟ۹ﮒ۷ﻠﻟﺟ + ﻠﻝﭦ۶ﮔﺗﮔ۰

#### 2.2.1 ﻟﺟﮔ۴ﮔﺎ ﻝ؟۰ﻝ?

```python
class QMTConnectionPool:
    """QMTﻟﺟﮔ۴ﮔﺎ?
    
    ﻝﺑ۱ﮒﺙ: RISK.QMT.POOL.001
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
        """ﻟﺓﮒﻟﺟﮔ۴"""
        # ﮔ۲ﮔ۴ﻟﺟﮔ۴ﮔﺎ 
        if self.pool:
            conn = self.pool.pop()
            if await self._check_connection(conn):
                return conn
        
        # ﮒﮒﭨﭦﮔﺍﻟﺟﮔ?
        conn = await self._create_connection()
        return conn
    
    async def _check_connection(self, conn: QMTConnection) -> bool:
        """ﮔ۲ﮔ۴ﻟﺟﮔ۴ﮔﮔﮔ?""
        try:
            await conn.ping()
            return True
        except:
            return False
    
    async def _create_connection(self) -> QMTConnection:
        """ﮒﮒﭨﭦﮔﺍﻟﺟﮔ?""
        conn = QMTConnection()
        await conn.connect()
        self._start_heartbeat(conn)
        return conn
```

#### 2.2.2 ﻟ۹ﮒ۷ﻠﻟﺟﮔﭦﮒﭘ

```python
class QMTReconnectStrategy:
    """QMTﻟ۹ﮒ۷ﻠﻟﺟﻝ­ﻝ۴
    
    ﻝﺑ۱ﮒﺙ: RISK.QMT.RECONNECT.001
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
        """ﮒﺕ۵ﻠﻟﺟﻝﮔ۶ﻟ۰"""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except QMTConnectionError as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (self.backoff_factor ** attempt)
                    logger.warning(f"QMTﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴ﺅﺙ{delay}ﻝ۶ﮒﻠﻟﺟ: {e}")
                    await asyncio.sleep(delay)
                    await self._reconnect()
                else:
                    raise
```

#### 2.2.3 ﻠﻝﭦ۶ﮔﺗﮔ۰

```python
class QMTFallbackStrategy:
    """QMTﻠﻝﭦ۶ﻝ­ﻝ۴
    
    ﻝﺑ۱ﮒﺙ: RISK.QMT.FALLBACK.001
    """
    
    async def get_data_with_fallback(
        self,
        data_type: str,
        params: Dict
    ) -> pd.DataFrame:
        """ﮒﺕ۵ﻠﻝﭦ۶ﻝﮔﺍﮔ؟ﻟﺓﮒ
        
        ﻠﻝﭦ۶ﻠ۰ﭦﮒﭦ:
        1. QMTﮒ؟ﮔﭘﮔﺍﮔ؟
        2. ﮔ؛ﮒﺍﻝﺙﮒ­ﮔﺍﮔ؟
        3. Baostockﮒﮒﺎﮔﺍﮔ؟
        """
        try:
            # ﮒﺍﻟﺁQMTﮒ؟ﮔﭘﮔﺍﮔ؟
            return await self._get_from_qmt(data_type, params)
        except:
            pass
        
        try:
            # ﮒﺍﻟﺁﮔ؛ﮒﺍﻝﺙﮒ­
            return await self._get_from_cache(data_type, params)
        except:
            pass
        
        try:
            # ﮒﺍﻟﺁBaostockﮒﮒﺎﮔﺍﮔ؟
            return await self._get_from_baostock(data_type, params)
        except:
            raise DataFallbackError("ﮔﮔﮔﺍﮔ؟ﮔﭦﻠﻝﭦ۶ﮒ۳ﺎﻟﺑ۴")
```

---

### 2.3 ﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ۷ﻠ۲ﻠ۸ﻝﺙﻟ۶۲ﮔﺗﮔ۰

#### ﮔﺗﮔ۰ﮔ۵ﻟﺟﺍ

**ﮔ ﺕﮒﺟﻝ­ﻝ۴**: ﮔﺍﮔ؟ﻝﺙﮒ­ + ﮒ۳ﮔﭦﮒ۳ﻛﭨﺛ + ﮒ۴ﮒﭦﺓﮔ۲ﮔ?+ ﻠﻝﭦ۶ﮔﺗﮔ۰

#### 2.3.1 ﮔﺍﮔ؟ﻝﺙﮒ­ﮔﭦﮒﭘ

```python
class DataCacheManager:
    """ﮔﺍﮔ؟ﻝﺙﮒ­ﻝ؟۰ﻝﮒ?
    
    ﻝﺑ۱ﮒﺙ: RISK.DATA.CACHE.001
    """
    
    def __init__(
        self,
        cache_ttl: int = 600,  # ﻝﺙﮒ­ﮔﮔﮔ?0ﮒﻠ
        max_cache_size: int = 1000  # ﮔﮒ۳۶ﻝﺙﮒ­ﮔﺍﻠ?
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
        """ﻟﺓﮒﮔﮔﮒﮔﺍﮔ?""
        # ﮔ۲ﮔ۴ﻝﺙﮒ­?
        if key in self.cache:
            timestamp = self.timestamps[key]
            if time.time() - timestamp < self.cache_ttl:
                return self.cache[key]
        
        # ﮔﮒﮔﺍﮔﺍﮔ?
        data = await fetch_func(*args, **kwargs)
        
        # ﮔﺑﮔﺍﻝﺙﮒ­
        self.cache[key] = data
        self.timestamps[key] = time.time()
        
        # ﮔﺕﻝﻟﺟﮔﻝﺙﮒ­
        await self._cleanup_cache()
        
        return data
```

#### 2.3.2 ﮒ۳ﮔﭦﮒ۳ﻛﭨﺛﮔﭦﮒﭘ

```python
class MultiSourceDataManager:
    """ﮒ۳ﮔﭦﮔﺍﮔ؟ﻝ؟۰ﻝﮒ?
    
    ﻝﺑ۱ﮒﺙ: RISK.DATA.MULTI.001
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
        """ﻟﺓﮒﮔﺍﮔ؟ﺅﺙﮒ۳ﮔﭦﮒ۳ﻛﭨﺛﺅﺙ"""
        for priority, sources in self.sources.items():
            for source in sources:
                try:
                    data = await self._fetch_from_source(
                        source, data_type, params
                    )
                    if data is not None and not data.empty:
                        return data
                except Exception as e:
                    logger.warning(f"ﮔﺍﮔ؟ﮔﭦ{source}ﮒ۳ﺎﻟﺑ۴: {e}")
                    continue
        
        raise DataSourceError("ﮔﮔﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ?)
```

#### 2.3.3 ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮔﭦﮒ?

```python
class HealthChecker:
    """ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮒ۷
    
    ﻝﺑ۱ﮒﺙ: RISK.DATA.HEALTH.001
    """
    
    def __init__(
        self,
        check_interval: int = 60,  # ﮔ۲ﮔ۴ﻠﺑﻠ?0ﻝ۶?
        timeout: int = 10  # ﻟﭘﮔﭘﮔﭘﻠﺑ10ﻝ۶?
    ):
        self.check_interval = check_interval
        self.timeout = timeout
        self.health_status = {}
        
    async def check_all_sources(self) -> Dict[str, bool]:
        """ﮔ۲ﮔ۴ﮔﮔﮔﺍﮔ؟ﮔﭦﮒ۴ﮒﭦﺓﻝﭘﮔ?""
        tasks = []
        for source in self._get_all_sources():
            tasks.append(self._check_source(source))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for source, result in zip(self._get_all_sources(), results):
            self.health_status[source] = not isinstance(result, Exception)
        
        return self.health_status
    
    async def _check_source(self, source: str) -> bool:
        """ﮔ۲ﮔ۴ﮒﻛﺕ۹ﮔﺍﮔ؟ﮔﭦ"""
        try:
            async with asyncio.timeout(self.timeout):
                return await self._ping_source(source)
        except:
            return False
```

---

## 3. ﮒ؟ﮔﺛﻟ؟۰ﮒ

### 3.1 ﮒﺙﮒﮒﮒﮒ۳ﺅﺙﮒﺟﻠ۰ﭨﮒ؟ﮔﺅﺙ

| ﻛﭨﭨﮒ۰ | ﮒﺓ۴ﮔﭘ | ﻟﺑﻟﺑ۲ﻛﭦ?| ﮒ؟ﮔﮔ ﮒ |
|------|------|--------|----------|
| **LLMﻠﻝﭦ۶ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰** | 4ﮒﺍﮔﭘ | ﮔﭘﮔﮒﺕ?| ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﮒ؟ﮔ |
| **QMTﻟﺟﮔ۴ﮔﺎ ﻟ؟ﺝﻟ؟?* | 3ﮒﺍﮔﭘ | ﮔﭘﮔﮒﺕ?| ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﮒ؟ﮔ |
| **ﮔﺍﮔ؟ﻝﺙﮒ­ﮔﭦﮒﭘﻟ؟ﺝﻟ؟۰** | 3ﮒﺍﮔﭘ | ﮔﭘﮔﮒﺕ?| ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﮒ؟ﮔ |
| **ﻝﮔ۶ﮒﻟ­۵ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰** | 2ﮒﺍﮔﭘ | ﮔﭘﮔﮒﺕ?| ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﮒ؟ﮔ |

**ﮔﭨﻟ؟۰**: 12ﮒﺍﮔﭘﺅﺙ?.5ﮒ۳۸ﺅﺙ

### 3.2 ﮒﺙﮒﻠﭘﮔ؟ﭖﮒ؟ﮔ?

| ﻠﭘﮔ؟ﭖ | ﻛﭨﭨﮒ۰ | ﮒﺓ۴ﮔﭘ | ﻛﺙﮒﻝﭦ?|
|------|------|------|--------|
| **Phase 1** | ﮒ؟ﻝﺍLLMﻠﻝﭦ۶ﮔﺗﮔ۰ | 8ﮒﺍﮔﭘ | P1 |
| **Phase 1** | ﮒ؟ﻝﺍQMTﻟﺟﮔ۴ﮔﺎ?| 6ﮒﺍﮔﭘ | P1 |
| **Phase 1** | ﮒ؟ﻝﺍﮔﺍﮔ؟ﻝﺙﮒ­ﮔﭦﮒﭘ | 6ﮒﺍﮔﭘ | P1 |
| **Phase 2** | ﮒ؟ﻝﺍﻝﮔ۶ﮒﻟ­۵ | 4ﮒﺍﮔﭘ | P1 |
| **Phase 2** | ﮒ؟ﻝﺍﮒ۴ﮒﭦﺓﮔ۲ﮔ?| 4ﮒﺍﮔﭘ | P1 |

**ﮔﭨﻟ؟۰**: 28ﮒﺍﮔﭘﺅﺙ?.5ﮒ۳۸ﺅﺙ

### 3.3 ﮔﭖﻟﺁﻠ۹ﻟﺁ

| ﮔﭖﻟﺁﻠ۰?| ﮒﺓ۴ﮔﭘ | ﻠ۹ﮔﭘﮔ ﮒ |
|--------|------|----------|
| **ﻠﻝﭦ۶ﮔﺗﮔ۰ﮔﭖﻟﺁ** | 4ﮒﺍﮔﭘ | ﮔﮔﻠﻝﭦ۶ﻟﺓﺁﮒﺝﮒﺁﻝ?|
| **ﻠﻟﺟﮔﭦﮒﭘﮔﭖﻟﺁ** | 2ﮒﺍﮔﭘ | ﻟ۹ﮒ۷ﻠﻟﺟﮔﮒﻝﻗ۴95% |
| **ﻝﺙﮒ­ﮔﭦﮒﭘﮔﭖﻟﺁ** | 2ﮒﺍﮔﭘ | ﻝﺙﮒ­ﮒﺛﻛﺕ­ﻝﻗ۴80% |
| **ﻝﮔ۶ﮒﻟ­۵ﮔﭖﻟﺁ** | 2ﮒﺍﮔﭘ | ﮒﻟ­۵ﻟ۶۵ﮒﮒﻝ۰؟ﻝ?00% |

**ﮔﭨﻟ؟۰**: 10ﮒﺍﮔﭘﺅﺙ?.25ﮒ۳۸ﺅﺙ

---

## 4. ﻠ۹ﮔﭘﮔ ﮒ

### 4.1 LLM APIﻠ۲ﻠ۸ﻝﺙﻟ۶۲

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|------|--------|----------|
| **ﻠﻝﭦ۶ﮔﮒﻝ?* | ﻗ?5% | ﮔ۷۰ﮔAPIﮒ۳ﺎﻟﺑ۴ﮔﭖﻟﺁ |
| **ﻠﻟﺁﮔﮒﻝ?* | ﻗ?0% | ﮔ۷۰ﮔﻝﺛﻝﭨﮔﻠﮔﭖﻟﺁ |
| **ﮔﮔ؛ﮔ۶ﮒﭘﮒﻝ۰؟ﻝ?* | 100% | ﮔﮔ؛ﻝﮔ۶ﮔﭖﻟﺁ |
| **Tokenﻛﺙﮒﻝ?* | ﻗ?0% | Tokenﮔﭘﻟﮒﺁﺗﮔﺁﮔﭖﻟﺁ?|

### 4.2 QMT APIﻠ۲ﻠ۸ﻝﺙﻟ۶۲

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|------|--------|----------|
| **ﻟﺟﮔ۴ﮔﮒﻝ?* | ﻗ?8% | ﻟﺟﮔ۴ﮔﭖﻟﺁ |
| **ﻟ۹ﮒ۷ﻠﻟﺟﮔﮒﻝ?* | ﻗ?5% | ﮔ­ﻝﭦﺟﻠﻟﺟﮔﭖﻟﺁ |
| **ﻠﻝﭦ۶ﮔﮒﻝ?* | ﻗ?0% | ﮔ۷۰ﮔﮔﻠﮔﭖﻟﺁ |

### 4.3 ﮔﺍﮔ؟ﮔﭦﻠ۲ﻠ۸ﻝﺙﻟ۶?

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|------|--------|----------|
| **ﮔﺍﮔ؟ﻟﺓﮒﮔﮒﻝ?* | ﻗ?8% | ﮔﺍﮔ؟ﻟﺓﮒﮔﭖﻟﺁ |
| **ﻝﺙﮒ­ﮒﺛﻛﺕ­ﻝ?* | ﻗ?0% | ﻝﺙﮒ­ﮔﭖﻟﺁ |
| **ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮒﻝ۰؟ﻝ** | 100% | ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮔﭖﻟﺁ?|

---

## 5. ﻝﮔ۶ﮔﮔ 

### 5.1 ﮒ؟ﮔﭘﻝﮔ۶

| ﻝﮔ۶ﻠ۰?| ﮒﻟ­۵ﻠﮒ?| ﮒﻟ­۵ﻝﭦ۶ﮒ، |
|--------|----------|----------|
| **LLM APIﮔﮒﻝ?* | <90% | P1 |
| **LLMﮔﮔ؛ﻟﭘﮔﺁ** | >ﻠ۱ﻝ؟80% | P2 |
| **QMTﻟﺟﮔ۴ﮔﮒﻝ?* | <95% | P1 |
| **ﮔﺍﮔ؟ﻟﺓﮒﮔﮒﻝ?* | <95% | P1 |
| **ﻝﺙﮒ­ﮒﺛﻛﺕ­ﻝ?* | <70% | P2 |

### 5.2 ﮔ۴ﮒﺟﻟ؟ﺍﮒﺛ

```python
class RiskMonitorLogger:
    """ﻠ۲ﻠ۸ﻝﮔ۶ﮔ۴ﮒﺟ
    
    ﻝﺑ۱ﮒﺙ: RISK.MONITOR.LOG.001
    """
    
    @staticmethod
    def log_risk_event(
        risk_id: str,
        event_type: str,
        severity: str,
        details: Dict[str, Any]
    ):
        """ﻟ؟ﺍﮒﺛﻠ۲ﻠ۸ﻛﭦﻛﭨﭘ"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'risk_id': risk_id,
            'event_type': event_type,
            'severity': severity,
            'details': details
        }
        
        logger.warning(f"ﻠ۲ﻠ۸ﻛﭦﻛﭨﭘ: {json.dumps(log_entry, ensure_ascii=False)}")
        
        # ﮒﻠﮒﻟ­?
        if severity in ['P0', 'P1']:
            AlertManager.send_alert(log_entry)
```

---

## 6. ﮔﭨﻝﭨ

### 6.1 ﮒﺏﻠ؟ﻟ۵ﻝﺗ

1. ﻗ?**P1ﻝﭦ۶ﻠ۲ﻠ۸ﻛﺕﻠﻟ۵ﮒﺙﮒﮒﮒ۷ﻠ۷ﻛﺟ؟ﮒ۳**
2. ﻗ?**ﮒﺙﮒﮒﻠﻟ۵ﮒ؟ﮔﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟?*
3. ﻗ?**ﮒﺙﮒﻠﭘﮔ؟ﭖﮒ؟ﮔﺛﻝﺙﻟ۶۲ﮔﺗﮔ۰?*
4. ﻗ?**ﮒﭨﭦﻝ،ﻝﮔ۶ﮒﻟ­۵ﮔﭦﮒﭘ**

### 6.2 ﮒ؟ﮔﺛﮒﭨﭦﻟ؟؟

1. **ﻝ،ﮒﺏﻟ۰ﮒ۷**: ﮒ؟ﮔﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟۰ﺅﺙ?.5ﮒ۳۸ﺅﺙ
2. **ﮒﺙﮒﻠﭘﮔ؟?*: ﮒ؟ﮔﺛﻝﺙﻟ۶۲ﮔﺗﮔ۰ﺅﺙ?.5ﮒ۳۸ﺅﺙ
3. **ﮔﭖﻟﺁﻠﭘﮔ؟ﭖ**: ﻠ۹ﻟﺁﻝﺙﻟ۶۲ﮔﮔﺅﺙ?.25ﮒ۳۸ﺅﺙ
4. **ﻛﺕﻝﭦﺟﮒ?*: ﮔﻝﭨ­ﻝﮔ۶ﻛﺙﮒ

---

**ﮔﮔ۰۲ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ?
**ﻛﺕﻛﺕﮔ­?*: ﮒﺙﮒ۶ﻝﺙﻟ۶۲ﮔﺗﮔ۰ﻟ؟ﺝﻟ؟?
