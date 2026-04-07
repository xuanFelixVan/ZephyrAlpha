---
module_id: TECH_SPEC_MARKET_PARTICIPANT_SIM_SUPPLEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 归档文档、历史版本
standard_type: ﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ﻟ۰۴ﮒﮔﮔ۰۲
applicable_scope: ﮒﺕﮒﭦﮒﻛﺕﻟﻟ۰ﻛﺕﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨ?compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ./MARKET_PARTICIPANT_SIMULATION_SPEC.md
implementation_status: ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ
---
---


# ﮒﺕﮒﭦﮒﻛﺕﻟﻟ۰ﻛﺕﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨ?- ﮒﺟﻠ۰ﭨﮔﺗﻟﺟﻠ۰ﺗﻟ۰۴ﮒﻟ؟ﺝﻟ؟?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

> **ﻝﮔ؛**: v1.0
> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02
> **ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟**: Spec-Approver (ﮒ؟۰ﮔﺗﮔﭦﻟﺛﻛﺛ?
> **ﻝ؟ﻝ**: ﻟ۰۴ﮒﻛﺕﻛﺕ۹ﮒﺟﻠ۰ﭨﮔﺗﻟﺟﻠ۰ﺗﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰,ﻝ۰؟ﻛﺟﻟﮒﺝﮒ؟ﮔﺑﮔ?> **ﻛﺙﮒﻝﭦ?*: P0 (24ﮒﺍﮔﭘﮒﮒ؟ﮔ?

---

## ﻭ ﻛﺕﻙﮔﺗﻟﺟﻠ۰ﺗﮔ۵ﻟﺟﺍ

ﮔ ﺗﮔ؟ﮔﮔﺁﻟﺁﮒ؟۰ﮔ۴ﮒ?ﻠﻟ۵ﻟ۰۴ﮒﻛﭨ۴ﻛﺕﻛﺕﻛﺕ۹ﮒﺟﻠ۰ﭨﮔﺗﻟﺟﻠ۰ﺗ:

| ﮔﺗﻟﺟﻠ۰ﺗID | ﮔﺗﻟﺟﮒﮒ؟ﺗ | ﻛﺙﮒﻝﭦ?| ﮒ؟ﮔﮔ ﮒ |
|---------|---------|--------|---------|
| **IMP-001** | ﻟ۰۴ﮒﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒ?| P0 | ﮔﮔﮔ۴ﮒ۲ﻠﺛﮔﮒﺙﮒﺕﺕﮒ۳ﻝ?ﻠﻟﺁﮔﭦﮒﭘﮒ؟ﮒ |
| **IMP-002** | ﮒ؟ﮒRLﮔ۷۰ﮒﻟ؟­ﻝﭨﻝﮔ۶ﮔﮔ  | P1 | ﻟ؟­ﻝﭨﻟﺟﻝ۷ﮒﺁﻟ۶ﮒ?ﮔ۶ﻟﺛﮔﮔ ﮒ؟ﮔﭘﻝﮔ۶ |
| **IMP-003** | ﻟ۰۴ﮒﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮔ ۰ﮒﮔﺗﮔ۰ | P1 | ﮔ ۰ﮒﮔﭖﻝ۷ﮔﺕﮔﺍ,ﻠ۹ﻟﺁﮔ ﮒﮔﻝ۰؟ |

---

## ﻭ۶ ﻛﭦﻙIMP-001: ﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒﭘﻟ؟ﺝﻟ؟?
### 2.1 ﮒﺙﮒﺕﺕﮒ۳ﻝﮔﭘﮔ

#### 2.1.1 ﮒﺙﮒﺕﺕﮒﺎﮔ؛۰ﻝﭨﮔ

```python
class MarketSimulationException(Exception):
    """ﮒﺕﮒﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨﮒﭦﻝ۰ﮒﺙﮒﺕﺕ
    
    ﻝﺑ۱ﮒﺙ: EXCEPTION.BASE.001
    """
    def __init__(self, message: str, error_code: str = None, context: Dict = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.context = context or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)


class DataAcquisitionException(MarketSimulationException):
    """ﮔﺍﮔ؟ﻠﻠﮒﺙﮒﺕﺕ
    
    ﻝﺑ۱ﮒﺙ: EXCEPTION.DATA.001
    ﮒﭦﮔﺁ: ﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ۷ﻙﮔﺍﮔ؟ﮔ ﺙﮒﺙﻠﻟﺁﺁﻙﮔﺍﮔ؟ﻝﺙﭦﮒ۳?    """
    def __init__(self, source: str, message: str, **kwargs):
        self.source = source
        error_code = f"DATA_ACQUISITION_{source.upper()}"
        super().__init__(message, error_code, **kwargs)


class AgentDecisionException(MarketSimulationException):
    """ﮔﭦﻟﺛﻛﺛﮒﺏﻝ­ﮒﺙﮒﺕ?    
    ﻝﺑ۱ﮒﺙ: EXCEPTION.AGENT.001
    ﮒﭦﮔﺁ: ﮔﭦﻟﺛﻛﺛﮒﺏﻝ­ﮒ۳ﺎﻟﺑ۴ﻙﻝﭘﮔﮒﺙﮒﺕﺕﻙﮒﮔﺍﻠﻟﺁ?    """
    def __init__(self, agent_type: str, message: str, **kwargs):
        self.agent_type = agent_type
        error_code = f"AGENT_DECISION_{agent_type.upper()}"
        super().__init__(message, error_code, **kwargs)


class RLTrainingException(MarketSimulationException):
    """RLﻟ؟­ﻝﭨﮒﺙﮒﺕﺕ
    
    ﻝﺑ۱ﮒﺙ: EXCEPTION.RL.001
    ﮒﭦﮔﺁ: ﮔ۷۰ﮒﻟ؟­ﻝﭨﮒ۳ﺎﻟﺑ۴ﻙﮔ۱ﺁﮒﭦ۵ﻝﻝﺕﻙﮔﭘﮔﮒ۳ﺎﻟﺑ?    """
    def __init__(self, model_name: str, message: str, **kwargs):
        self.model_name = model_name
        error_code = f"RL_TRAINING_{model_name.upper()}"
        super().__init__(message, error_code, **kwargs)


class MarketImpactException(MarketSimulationException):
    """ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮒﺙﮒﺕﺕ
    
    ﻝﺑ۱ﮒﺙ: EXCEPTION.MARKET_IMPACT.001
    ﮒﭦﮔﺁ: ﮒﺕﮒﭦﮒﺎﮒﭨﻟ؟۰ﻝ؟ﮒ۳ﺎﻟﺑ۴ﻙﮒﮔﺍﮔ ۰ﮒﻠﻟﺁ?    """
    def __init__(self, message: str, **kwargs):
        error_code = "MARKET_IMPACT_ERROR"
        super().__init__(message, error_code, **kwargs)
```

#### 2.1.2 ﮒﺙﮒﺕﺕﮒ۳ﻝﮒ۷ﻟ؟ﺝﻟ؟?
```python
class ExceptionHandler:
    """ﻝﭨﻛﺕﮒﺙﮒﺕﺕﮒ۳ﻝﮒ?    
    ﻝﺑ۱ﮒﺙ: HANDLER.EXCEPTION.001
    ﻟﻟﺑ۲: ﻝﭨﻛﺕﮒ۳ﻝﻝﺏﭨﻝﭨﮒﺙﮒﺕﺕ,ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟ,ﮒﻠﮒﻟ­?    """
    
    def __init__(self, config: ExceptionHandlerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.alert_manager = AlertManager()
        self.error_recorder = ErrorRecorder()
        
    def handle_exception(self, 
                        exception: MarketSimulationException,
                        context: Dict = None) -> ExceptionHandlingResult:
        """ﮒ۳ﻝﮒﺙﮒﺕﺕ
        
        ﮒ۳ﻝﮔﭖﻝ۷:
        1. ﻟ؟ﺍﮒﺛﮒﺙﮒﺕﺕﮔ۴ﮒﺟ
        2. ﮒ۳ﮔ­ﮒﺙﮒﺕﺕﻝﭦ۶ﮒ،
        3. ﮒﻠﮒﻟ­?ﮒ۵ﻠﻟ۵?
        4. ﻟ؟ﺍﮒﺛﮒﺍﻠﻟﺁﺁﮔﺍﮔ؟ﮒﭦ
        5. ﻟﺟﮒﮒ۳ﻝﻝﭨﮔ
        """
        # 1. ﻟ؟ﺍﮒﺛﮒﺙﮒﺕﺕﮔ۴ﮒﺟ
        self._log_exception(exception, context)
        
        # 2. ﮒ۳ﮔ­ﮒﺙﮒﺕﺕﻝﭦ۶ﮒ،
        severity = self._determine_severity(exception)
        
        # 3. ﮒﻠﮒﻟ­?        if severity in ['HIGH', 'CRITICAL']:
            self._send_alert(exception, severity)
        
        # 4. ﻟ؟ﺍﮒﺛﮒﺍﻠﻟﺁﺁﮔﺍﮔ؟ﮒﭦ
        self._record_error(exception, severity)
        
        # 5. ﻟﺟﮒﮒ۳ﻝﻝﭨﮔ
        return ExceptionHandlingResult(
            exception_id=self._generate_exception_id(),
            severity=severity,
            handled=True,
            timestamp=datetime.now()
        )
    
    def _log_exception(self, exception: MarketSimulationException, context: Dict):
        """ﻟ؟ﺍﮒﺛﮒﺙﮒﺕﺕﮔ۴ﮒﺟ"""
        log_data = {
            'error_code': exception.error_code,
            'message': exception.message,
            'context': {**exception.context, **(context or {})},
            'timestamp': exception.timestamp.isoformat(),
            'stack_trace': traceback.format_exc()
        }
        
        self.logger.error(
            f"Exception occurred: {exception.error_code} - {exception.message}",
            extra=log_data
        )
    
    def _determine_severity(self, exception: MarketSimulationException) -> str:
        """ﮒ۳ﮔ­ﮒﺙﮒﺕﺕﻛﺕ۴ﻠﻝﭦ۶ﮒ،
        
        ﻝﭦ۶ﮒ،ﮒ؟ﻛﺗ:
        - CRITICAL: ﻝﺏﭨﻝﭨﮒﺑ۸ﮔﭦﻙﮔﺍﮔ؟ﻛﺕ۱ﮒ۳?        - HIGH: ﮔ ﺕﮒﺟﮒﻟﺛﮒ۳ﺎﮔ
        - MEDIUM: ﻠ۷ﮒﮒﻟﺛﻠﻝﭦ۶
        - LOW: ﮒﺁﮒﺟﺛﻝ۴ﻝﮒﺙﮒﺕﺕ
        """
        severity_mapping = {
            'DATA_ACQUISITION': 'HIGH',
            'AGENT_DECISION': 'HIGH',
            'RL_TRAINING': 'CRITICAL',
            'MARKET_IMPACT': 'MEDIUM',
            'UNKNOWN_ERROR': 'LOW'
        }
        
        error_prefix = exception.error_code.split('_')[0]
        return severity_mapping.get(error_prefix, 'LOW')
    
    def _send_alert(self, exception: MarketSimulationException, severity: str):
        """ﮒﻠﮒﻟ­?""
        alert = Alert(
            level=severity,
            title=f"ﮒﺕﮒﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨﮒﺙﮒﺕﺕ: {exception.error_code}",
            message=exception.message,
            context=exception.context,
            timestamp=datetime.now()
        )
        
        self.alert_manager.send_alert(alert)
    
    def _record_error(self, exception: MarketSimulationException, severity: str):
        """ﻟ؟ﺍﮒﺛﻠﻟﺁﺁﮒﺍﮔﺍﮔ؟ﮒﭦ"""
        error_record = ErrorRecord(
            error_id=self._generate_exception_id(),
            error_code=exception.error_code,
            message=exception.message,
            severity=severity,
            context=exception.context,
            timestamp=datetime.now()
        )
        
        self.error_recorder.record(error_record)
    
    def _generate_exception_id(self) -> str:
        """ﻝﮔﮒﺙﮒﺕﺕID"""
        import uuid
        return f"EXC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
```

### 2.2 ﻠﻟﺁﮔﭦﮒﭘﻟ؟ﺝﻟ؟۰

#### 2.2.1 ﻠﻟﺁﻝ­ﻝ۴

```python
from enum import Enum
from typing import Callable, Any
import time
from functools import wraps

class RetryStrategy(Enum):
    """ﻠﻟﺁﻝ­ﻝ۴ﮔﻛﺕﺝ"""
    FIXED_INTERVAL = "fixed_interval"  # ﮒﭦﮒ؟ﻠﺑﻠ
    EXPONENTIAL_BACKOFF = "exponential_backoff"  # ﮔﮔﺍﻠﻠ?    LINEAR_BACKOFF = "linear_backoff"  # ﻝﭦﺟﮔ۶ﻠﻠ?

class RetryConfig:
    """ﻠﻟﺁﻠﻝﺛ؟
    
    ﻝﺑ۱ﮒﺙ: CONFIG.RETRY.001
    """
    def __init__(self,
                 max_retries: int = 3,
                 strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 retryable_exceptions: List[Type[Exception]] = None):
        self.max_retries = max_retries
        self.strategy = strategy
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions or [Exception]


class RetryExecutor:
    """ﻠﻟﺁﮔ۶ﻟ۰ﮒ?    
    ﻝﺑ۱ﮒﺙ: EXECUTOR.RETRY.001
    ﻟﻟﺑ۲: ﮔ۶ﻟ۰ﮒﺕ۵ﻠﻟﺁﮔﭦﮒﭘﻝﮔﻛﺛ
    """
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def execute_with_retry(self, 
                          operation: Callable[[], Any],
                          operation_name: str = "operation") -> Any:
        """ﮔ۶ﻟ۰ﮒﺕ۵ﻠﻟﺁﮔﭦﮒﭘﻝﮔﻛﺛ
        
        ﮔ۶ﻟ۰ﮔﭖﻝ۷:
        1. ﮔ۶ﻟ۰ﮔﻛﺛ
        2. ﮒ۵ﮔﮒ۳ﺎﻟﺑ۴,ﮔ ﺗﮔ؟ﻠﻟﺁﻝ­ﻝ۴ﻝ­ﮒﺝ
        3. ﻠﻟﺁﮔﻛﺛ
        4. ﻟﺝﺝﮒﺍﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔﺍﮒﮔﮒﭦﮒﺙﮒﺕﺕ
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                result = operation()
                if attempt > 0:
                    self.logger.info(
                        f"Operation '{operation_name}' succeeded on attempt {attempt + 1}"
                    )
                return result
                
            except Exception as e:
                last_exception = e
                
                # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻛﺕﭦﮒﺁﻠﻟﺁﮒﺙﮒﺕ?                if not self._is_retryable_exception(e):
                    self.logger.error(
                        f"Operation '{operation_name}' failed with non-retryable exception: {e}"
                    )
                    raise
                
                # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟﺝﺝﮒﺍﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ?                if attempt >= self.config.max_retries:
                    self.logger.error(
                        f"Operation '{operation_name}' failed after {self.config.max_retries} retries"
                    )
                    raise
                
                # ﻟ؟۰ﻝ؟ﻝ­ﮒﺝﮔﭘﻠﺑ
                delay = self._calculate_delay(attempt)
                
                self.logger.warning(
                    f"Operation '{operation_name}' failed on attempt {attempt + 1}, "
                    f"retrying in {delay:.2f}s. Error: {e}"
                )
                
                time.sleep(delay)
        
        raise last_exception
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻛﺕﭦﮒﺁﻠﻟﺁﮒﺙﮒﺕ?""
        return any(
            isinstance(exception, retryable_exc) 
            for retryable_exc in self.config.retryable_exceptions
        )
    
    def _calculate_delay(self, attempt: int) -> float:
        """ﻟ؟۰ﻝ؟ﻠﻟﺁﮒﭨﭘﻟﺟﮔﭘﻠﺑ"""
        if self.config.strategy == RetryStrategy.FIXED_INTERVAL:
            delay = self.config.base_delay
            
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = min(
                self.config.base_delay * (self.config.exponential_base ** attempt),
                self.config.max_delay
            )
            
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = min(
                self.config.base_delay * (attempt + 1),
                self.config.max_delay
            )
            
        else:
            delay = self.config.base_delay
        
        return delay


def retry_on_failure(config: RetryConfig):
    """ﻠﻟﺁﻟ۲ﻠ۴ﺍﮒ?    
    ﻝﺑ۱ﮒﺙ: DECORATOR.RETRY.001
    ﻝ۷ﮔﺏ: @retry_on_failure(RetryConfig(max_retries=3))
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            operation = lambda: func(*args, **kwargs)
            return executor.execute_with_retry(operation, func.__name__)
        return wrapper
    return decorator
```

#### 2.2.2 ﮒﺓﻛﺛﮒﭦﻝ۷ﮒﭦﮔﺁ

```python
class DataCollectorWithRetry:
    """ﮒﺕ۵ﻠﻟﺁﮔﭦﮒﭘﻝﮔﺍﮔ؟ﻠﻠﮒ?    
    ﻝﺑ۱ﮒﺙ: COLLECTOR.DATA.RETRY.001
    """
    
    def __init__(self):
        self.retry_config = RetryConfig(
            max_retries=3,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            base_delay=2.0,
            max_delay=30.0,
            retryable_exceptions=[
                ConnectionError,
                TimeoutError,
                DataAcquisitionException
            ]
        )
        self.executor = RetryExecutor(self.retry_config)
        
    @retry_on_failure(RetryConfig(max_retries=3, base_delay=2.0))
    def collect_longhubang_data(self, date: str) -> pd.DataFrame:
        """ﻠﻠﻠﺝﻟﮔ۵ﮔﺍﮔ?ﮒﺕ۵ﻠﻟﺁ?"""
        try:
            import akshare as ak
            data = ak.stock_lhb_detail_em(start_date=date, end_date=date)
            return data
        except Exception as e:
            raise DataAcquisitionException(
                source="longhubang",
                message=f"Failed to collect longhubang data for {date}: {e}",
                context={'date': date}
            )
    
    @retry_on_failure(RetryConfig(max_retries=5, base_delay=5.0))
    def collect_level2_data(self, symbol: str, date: str) -> Dict:
        """ﻠﻠLevel-2ﮔﺍﮔ؟(ﮒﺕ۵ﻠﻟﺁ?"""
        try:
            # ﮔ۷۰ﮔLevel-2ﮔﺍﮔ؟ﻠﻠ
            data = self._fetch_level2_from_source(symbol, date)
            return data
        except Exception as e:
            raise DataAcquisitionException(
                source="level2",
                message=f"Failed to collect Level-2 data for {symbol} on {date}: {e}",
                context={'symbol': symbol, 'date': date}
            )


class AgentDecisionWithRetry:
    """ﮒﺕ۵ﻠﻟﺁﮔﭦﮒﭘﻝﮔﭦﻟﺛﻛﺛﮒﺏﻝ­?    
    ﻝﺑ۱ﮒﺙ: AGENT.DECISION.RETRY.001
    """
    
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.retry_config = RetryConfig(
            max_retries=2,
            strategy=RetryStrategy.FIXED_INTERVAL,
            base_delay=1.0,
            retryable_exceptions=[AgentDecisionException]
        )
        self.executor = RetryExecutor(self.retry_config)
        
    def generate_decision_with_retry(self, market_state: MarketState) -> AgentDecision:
        """ﻝﮔﮒﺏﻝ­(ﮒﺕ۵ﻠﻟﺁ?"""
        operation = lambda: self.agent.generate_trading_decision(market_state)
        
        try:
            return self.executor.execute_with_retry(
                operation, 
                f"{self.agent.__class__.__name__}.generate_trading_decision"
            )
        except Exception as e:
            # ﮒ۵ﮔﻠﻟﺁﮒ۳ﺎﻟﺑ۴,ﻟﺟﮒﻠﭨﻟ؟۳ﮒﺏﻝ­
            self.logger.error(
                f"Agent decision failed after retries, returning default decision: {e}"
            )
            return AgentDecision(
                action="HOLD",
                target_stocks=[],
                position_size={},
                confidence=0.0,
                reasoning=f"Decision failed after retries: {e}",
                agent_type=self.agent.__class__.__name__,
                timestamp=datetime.now()
            )
```

---

## ﻭ ﻛﺕﻙIMP-002: RLﮔ۷۰ﮒﻟ؟­ﻝﭨﻝﮔ۶ﮔﮔ ﻟ؟ﺝﻟ؟۰

### 3.1 ﻝﮔ۶ﮔﮔ ﻛﺛﻝﺏﭨ

#### 3.1.1 ﮔ ﺕﮒﺟﻝﮔ۶ﮔﮔ 

```python
@dataclass
class RLTrainingMetrics:
    """RLﻟ؟­ﻝﭨﻝﮔ۶ﮔﮔ 
    
    ﻝﺑ۱ﮒﺙ: METRICS.RL.001
    """
    # ﮒﭦﻝ۰ﮔﮔ 
    episode: int  # ﮒﺛﮒﮒﮒ
    step: int  # ﮒﺛﮒﮔ­۴ﮔﺍ
    timestamp: datetime  # ﮔﭘﻠﺑﮔ?    
    # ﮒ۴ﮒﺎﮔﮔ 
    episode_reward: float  # ﮒﮒﮔﭨﮒ۴ﮒ?    average_reward: float  # ﮒﺗﺏﮒﮒ۴ﮒﺎ
    reward_std: float  # ﮒ۴ﮒﺎﮔ ﮒﮒﺓ?    
    # ﮔﮒ۳ﺎﮔﮔ 
    actor_loss: float  # Actorﮔﮒ۳ﺎ
    critic_loss: float  # Criticﮔﮒ۳ﺎ
    entropy: float  # ﻝ?ﮔ۱ﻝﺑ۱ﻝ۷ﮒﭦ۵)
    
    # ﮔ۶ﻟﺛﮔﮔ 
    sharpe_ratio: float  # ﮒ۳ﮔ؟ﮔﺁﻝ
    max_drawdown: float  # ﮔﮒ۳۶ﮒﮔ?    win_rate: float  # ﻟﻝ
    profit_factor: float  # ﻝﻛﭦﮔﺁ?    
    # ﻟ؟­ﻝﭨﻝ۷ﺏﮒ؟ﮔ۶ﮔﮔ ?    gradient_norm: float  # ﮔ۱ﺁﮒﭦ۵ﻟﮔﺍ
    learning_rate: float  # ﮒ­۵ﻛﺗ ﻝ?    exploration_rate: float  # ﮔ۱ﻝﺑ۱ﻝ?    
    # ﻟﭖﮔﭦﮔﮔ 
    gpu_memory_used: float  # GPUﮒﮒ­ﻛﺛﺟﻝ۷
    training_time: float  # ﻟ؟­ﻝﭨﮔﭘﻠﺑ


class RLTrainingMonitor:
    """RLﻟ؟­ﻝﭨﻝﮔ۶ﮒ?    
    ﻝﺑ۱ﮒﺙ: MONITOR.RL.001
    ﻟﻟﺑ۲: ﮒ؟ﮔﭘﻝﮔ۶RLﻟ؟­ﻝﭨﻟﺟﻝ۷,ﻟ؟ﺍﮒﺛﮔﮔ ,ﻝﮔﮔ۴ﮒ
    """
    
    def __init__(self, config: RLTrainingMonitorConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics_history: List[RLTrainingMetrics] = []
        self.tensorboard_writer = SummaryWriter(config.log_dir)
        self.alert_manager = AlertManager()
        
    def record_metrics(self, metrics: RLTrainingMetrics):
        """ﻟ؟ﺍﮒﺛﻟ؟­ﻝﭨﮔﮔ 
        
        ﻟ؟ﺍﮒﺛﮔﭖﻝ۷:
        1. ﮔﺓﭨﮒ ﮒﺍﮒﮒﺎﻟ؟ﺍﮒﺛ?        2. ﮒﮒ۴TensorBoard
        3. ﮔ۲ﮔ۴ﮒﺙﮒﺕﺕﮔﮔ ?        4. ﮒﻠﮒﻟ­?ﮒ۵ﻠﻟ۵?
        """
        # 1. ﮔﺓﭨﮒ ﮒﺍﮒﮒﺎﻟ؟ﺍﮒﺛ?        self.metrics_history.append(metrics)
        
        # 2. ﮒﮒ۴TensorBoard
        self._write_to_tensorboard(metrics)
        
        # 3. ﮔ۲ﮔ۴ﮒﺙﮒﺕﺕﮔﮔ ?        anomalies = self._check_anomalies(metrics)
        
        # 4. ﮒﻠﮒﻟ­?        if anomalies:
            self._send_training_alert(metrics, anomalies)
    
    def _write_to_tensorboard(self, metrics: RLTrainingMetrics):
        """ﮒﮒ۴TensorBoard"""
        # ﮒ۴ﮒﺎﮔﮔ 
        self.tensorboard_writer.add_scalar(
            'Reward/Episode_Reward', metrics.episode_reward, metrics.episode
        )
        self.tensorboard_writer.add_scalar(
            'Reward/Average_Reward', metrics.average_reward, metrics.episode
        )
        
        # ﮔﮒ۳ﺎﮔﮔ 
        self.tensorboard_writer.add_scalar(
            'Loss/Actor_Loss', metrics.actor_loss, metrics.episode
        )
        self.tensorboard_writer.add_scalar(
            'Loss/Critic_Loss', metrics.critic_loss, metrics.episode
        )
        
        # ﮔ۶ﻟﺛﮔﮔ 
        self.tensorboard_writer.add_scalar(
            'Performance/Sharpe_Ratio', metrics.sharpe_ratio, metrics.episode
        )
        self.tensorboard_writer.add_scalar(
            'Performance/Max_Drawdown', metrics.max_drawdown, metrics.episode
        )
        
        # ﻟ؟­ﻝﭨﻝ۷ﺏﮒ؟ﮔ۶ﮔﮔ ?        self.tensorboard_writer.add_scalar(
            'Training/Gradient_Norm', metrics.gradient_norm, metrics.episode
        )
        self.tensorboard_writer.add_scalar(
            'Training/Entropy', metrics.entropy, metrics.episode
        )
    
    def _check_anomalies(self, metrics: RLTrainingMetrics) -> List[str]:
        """ﮔ۲ﮔ۴ﮒﺙﮒﺕﺕﮔﮔ ?""
        anomalies = []
        
        # ﮔ۲ﮔ۴ﮒ۴ﮒﺎﮒﺙﮒﺕ?        if metrics.episode_reward < self.config.reward_lower_bound:
            anomalies.append(f"Episode reward too low: {metrics.episode_reward}")
        
        # ﮔ۲ﮔ۴ﮔﮒ۳ﺎﮒﺙﮒﺕ?        if abs(metrics.actor_loss) > self.config.loss_upper_bound:
            anomalies.append(f"Actor loss too high: {metrics.actor_loss}")
        
        if abs(metrics.critic_loss) > self.config.loss_upper_bound:
            anomalies.append(f"Critic loss too high: {metrics.critic_loss}")
        
        # ﮔ۲ﮔ۴ﮔ۱ﺁﮒﭦ۵ﻝﻝ?        if metrics.gradient_norm > self.config.gradient_norm_threshold:
            anomalies.append(f"Gradient explosion detected: {metrics.gradient_norm}")
        
        # ﮔ۲ﮔ۴ﮔ۶ﻟﺛﻛﺕﻠ
        if len(self.metrics_history) >= 10:
            recent_sharpe = [m.sharpe_ratio for m in self.metrics_history[-10:]]
            if metrics.sharpe_ratio < np.mean(recent_sharpe) * 0.5:
                anomalies.append(f"Performance degradation: Sharpe ratio dropped to {metrics.sharpe_ratio}")
        
        return anomalies
    
    def _send_training_alert(self, metrics: RLTrainingMetrics, anomalies: List[str]):
        """ﮒﻠﻟ؟­ﻝﭨﮒﻟ­?""
        alert = Alert(
            level='HIGH',
            title=f"RLﻟ؟­ﻝﭨﮒﺙﮒﺕﺕ: Episode {metrics.episode}",
            message=f"ﮔ۲ﮔﭖﮒﺍﻛﭨ۴ﻛﺕﮒﺙﮒﺕﺕ:\n" + "\n".join(anomalies),
            context={
                'episode': metrics.episode,
                'metrics': asdict(metrics),
                'anomalies': anomalies
            },
            timestamp=datetime.now()
        )
        
        self.alert_manager.send_alert(alert)
    
    def generate_training_report(self) -> str:
        """ﻝﮔﻟ؟­ﻝﭨﮔ۴ﮒ"""
        if not self.metrics_history:
            return "No training data available"
        
        latest_metrics = self.metrics_history[-1]
        
        report = f"""
# RLﻟ؟­ﻝﭨﮔ۴ﮒ

## ﻟ؟­ﻝﭨﮔ۵ﻟ۶
- **ﮒﺛﮒﮒﮒ**: {latest_metrics.episode}
- **ﻟ؟­ﻝﭨﮔﭘﻠﺑ**: {latest_metrics.training_time:.2f}ﻝ۶?- **GPUﮒﮒ­ﻛﺛﺟﻝ۷**: {latest_metrics.gpu_memory_used:.2f}GB

## ﮒ۴ﮒﺎﮔﮔ 
- **ﮒﮒﮔﭨﮒ۴ﮒ?*: {latest_metrics.episode_reward:.4f}
- **ﮒﺗﺏﮒﮒ۴ﮒﺎ**: {latest_metrics.average_reward:.4f}
- **ﮒ۴ﮒﺎﮔ ﮒﮒﺓ?*: {latest_metrics.reward_std:.4f}

## ﮔ۶ﻟﺛﮔﮔ 
- **ﮒ۳ﮔ؟ﮔﺁﻝ**: {latest_metrics.sharpe_ratio:.4f}
- **ﮔﮒ۳۶ﮒﮔ?*: {latest_metrics.max_drawdown:.4f}
- **ﻟﻝ**: {latest_metrics.win_rate:.2%}
- **ﻝﻛﭦﮔﺁ?*: {latest_metrics.profit_factor:.4f}

## ﻟ؟­ﻝﭨﻝ۷ﺏﮒ؟ﮔ?- **ﮔ۱ﺁﮒﭦ۵ﻟﮔﺍ**: {latest_metrics.gradient_norm:.4f}
- **ﮒ­۵ﻛﺗ ﻝ?*: {latest_metrics.learning_rate:.6f}
- **ﮔ۱ﻝﺑ۱ﻝ?*: {latest_metrics.exploration_rate:.4f}

## ﮔﮒ۳ﺎﮔﮔ 
- **Actorﮔﮒ۳ﺎ**: {latest_metrics.actor_loss:.4f}
- **Criticﮔﮒ۳ﺎ**: {latest_metrics.critic_loss:.4f}
- **ﻝ?*: {latest_metrics.entropy:.4f}
"""
        
        return report
```

#### 3.1.2 ﻟ؟­ﻝﭨﻟﺟﻝ۷ﮒﺁﻟ۶ﮒ?
```python
class RLTrainingVisualizer:
    """RLﻟ؟­ﻝﭨﮒﺁﻟ۶ﮒﮒ۷
    
    ﻝﺑ۱ﮒﺙ: VISUALIZER.RL.001
    ﻟﻟﺑ۲: ﻝﮔﻟ؟­ﻝﭨﻟﺟﻝ۷ﮒﺁﻟ۶ﮒﮒﺝﻟ۰?    """
    
    def __init__(self, monitor: RLTrainingMonitor):
        self.monitor = monitor
        
    def plot_training_curves(self, save_path: str = None):
        """ﻝﭨﮒﭘﻟ؟­ﻝﭨﮔﺎﻝﭦﺟ"""
        import matplotlib.pyplot as plt
        
        metrics = self.monitor.metrics_history
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # ﮒ۴ﮒﺎﮔﺎﻝﭦﺟ
        episodes = [m.episode for m in metrics]
        rewards = [m.episode_reward for m in metrics]
        axes[0, 0].plot(episodes, rewards)
        axes[0, 0].set_title('Episode Reward')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Reward')
        
        # ﮔﮒ۳ﺎﮔﺎﻝﭦﺟ
        actor_losses = [m.actor_loss for m in metrics]
        critic_losses = [m.critic_loss for m in metrics]
        axes[0, 1].plot(episodes, actor_losses, label='Actor Loss')
        axes[0, 1].plot(episodes, critic_losses, label='Critic Loss')
        axes[0, 1].set_title('Training Losses')
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        
        # ﮒ۳ﮔ؟ﮔﺁﻝﮔﺎﻝﭦﺟ
        sharpe_ratios = [m.sharpe_ratio for m in metrics]
        axes[0, 2].plot(episodes, sharpe_ratios)
        axes[0, 2].set_title('Sharpe Ratio')
        axes[0, 2].set_xlabel('Episode')
        axes[0, 2].set_ylabel('Sharpe Ratio')
        
        # ﮔﮒ۳۶ﮒﮔ۳ﮔﺎﻝﭦ?        max_drawdowns = [m.max_drawdown for m in metrics]
        axes[1, 0].plot(episodes, max_drawdowns)
        axes[1, 0].set_title('Max Drawdown')
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Drawdown')
        
        # ﮔ۱ﺁﮒﭦ۵ﻟﮔﺍﮔﺎﻝﭦﺟ
        gradient_norms = [m.gradient_norm for m in metrics]
        axes[1, 1].plot(episodes, gradient_norms)
        axes[1, 1].set_title('Gradient Norm')
        axes[1, 1].set_xlabel('Episode')
        axes[1, 1].set_ylabel('Norm')
        
        # ﮔ۱ﻝﺑ۱ﻝﮔﺎﻝﭦ?        exploration_rates = [m.exploration_rate for m in metrics]
        axes[1, 2].plot(episodes, exploration_rates)
        axes[1, 2].set_title('Exploration Rate')
        axes[1, 2].set_xlabel('Episode')
        axes[1, 2].set_ylabel('Rate')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        
        return fig
```

### 3.2 ﻟ؟­ﻝﭨﻝﮔ۶ﻠﻝﺛ؟

```yaml
rl_training_monitor:
  log_dir: "logs/rl_training/"
  
  monitoring_interval: 100  # ﮔﺁ?00ﮔ­۴ﻟ؟ﺍﮒﺛﻛﺕﮔ؛?  
  anomaly_detection:
    reward_lower_bound: -1000.0
    loss_upper_bound: 10000.0
    gradient_norm_threshold: 100.0
    
  alert_thresholds:
    consecutive_low_reward: 10  # ﻟﺟﻝﭨ­10ﮒﮒﻛﺛﮒ۴ﮒ?    performance_degradation: 0.5  # ﮔ۶ﻟﺛﻛﺕﻠ50%
    
  visualization:
    enabled: true
    update_interval: 1000  # ﮔﺁ?000ﮔ­۴ﮔﺑﮔﺍﮒﺝﻟ۰?    save_dir: "reports/rl_training/"
    
  early_stopping:
    enabled: true
    patience: 50  # 50ﮒﮒﮔ ﮔﺗﮒﮒﮒﮔ­۱
    min_delta: 0.01  # ﮔﮒﺍﮔﺗﮒﻠﮒ?```

---

## ﻭﺁ ﮒﻙIMP-003: ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮔ ۰ﮒﮔﺗﮔ۰

### 4.1 ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﻟ؟ﺝﻟ؟۰

#### 4.1.1 ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮒﭦﻝ۰

```python
class MarketImpactModel:
    """ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒ
    
    ﻝﺑ۱ﮒﺙ: MODEL.MARKET_IMPACT.001
    ﻝﻟ؟ﭦﮒﭦﻝ۰: Almgren-Chrissﮔ۷۰ﮒ + ﮒ؟ﻠﮒﺕﮒﭦﮔﺍﮔ؟ﮔ ۰ﮒ
    """
    
    def __init__(self, config: MarketImpactConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # ﮔ۷۰ﮒﮒﮔﺍ
        self.temporary_impact_coef = None  # ﻛﺕﺑﮔﭘﮒﺎﮒﭨﻝﺏﭨﮔﺍ
        self.permanent_impact_coef = None  # ﮔﺍﺕﻛﺗﮒﺎﮒﭨﻝﺏﭨﮔﺍ
        self.volatility_coef = None  # ﮔﺏ۱ﮒ۷ﻝﻝﺏﭨﮔ?        self.liquidity_coef = None  # ﮔﭖﮒ۷ﮔ۶ﻝﺏﭨﮔ?        
        # ﮔ ۰ﮒﻝﭘﮔ?        self.is_calibrated = False
        self.calibration_date = None
        self.calibration_metrics = {}
        
    def calculate_market_impact(self,
                               order_size: float,
                               average_volume: float,
                               volatility: float,
                               execution_time: float) -> MarketImpactResult:
        """ﻟ؟۰ﻝ؟ﮒﺕﮒﭦﮒﺎﮒﭨ
        
        ﮒﮔﺍ:
            order_size: ﻟ؟۱ﮒﮒ۳۶ﮒﺍ(ﻟ۰ﮔﺍ)
            average_volume: ﮒﺗﺏﮒﮔﻛﭦ۳ﻠ?            volatility: ﮔﺏ۱ﮒ۷ﻝ?            execution_time: ﮔ۶ﻟ۰ﮔﭘﻠﺑ(ﮒ۳?
            
        ﻟﺟﮒ:
            MarketImpactResult: ﮒﺕﮒﭦﮒﺎﮒﭨﻝﭨﮔ
        """
        if not self.is_calibrated:
            raise MarketImpactException("Model not calibrated. Please calibrate first.")
        
        # ﻟ؟۰ﻝ؟ﮒﻛﺕﻝ?        participation_rate = order_size / (average_volume * execution_time)
        
        # ﻟ؟۰ﻝ؟ﻛﺕﺑﮔﭘﮒﺎﮒﭨ
        temporary_impact = self.temporary_impact_coef * participation_rate * volatility
        
        # ﻟ؟۰ﻝ؟ﮔﺍﺕﻛﺗﮒﺎﮒﭨ
        permanent_impact = self.permanent_impact_coef * participation_rate * volatility
        
        # ﻟ؟۰ﻝ؟ﮔﭨﮒﺎﮒ?        total_impact = temporary_impact + permanent_impact
        
        # ﻟ؟۰ﻝ؟ﮒﺎﮒﭨﮔﮔ؛
        impact_cost = total_impact * order_size
        
        return MarketImpactResult(
            temporary_impact=temporary_impact,
            permanent_impact=permanent_impact,
            total_impact=total_impact,
            impact_cost=impact_cost,
            participation_rate=participation_rate,
            confidence=self._calculate_confidence(participation_rate, volatility)
        )
    
    def _calculate_confidence(self, participation_rate: float, volatility: float) -> float:
        """ﻟ؟۰ﻝ؟ﻝﺛ؟ﻛﺟ۰ﮒﭦ?        
        ﻝﺛ؟ﻛﺟ۰ﮒﭦ۵ﮒﭦﻛﭦ?
        1. ﮒﻛﺕﻝﮔﺁﮒ۵ﮒ۷ﮒﻝﻟﮒﺑﮒ?        2. ﮔﺏ۱ﮒ۷ﻝﮔﺁﮒ۵ﮒ۷ﮒﮒﺎﻟﮒﺑﮒ?        """
        confidence = 1.0
        
        # ﮒﻛﺕﻝﻟﺟﻠ،?ﻝﺛ؟ﻛﺟ۰ﮒﭦ۵ﻠﻛﺛ?        if participation_rate > 0.1:
            confidence *= 0.7
        
        # ﮔﺏ۱ﮒ۷ﻝﻟﺟﻠ،?ﻝﺛ؟ﻛﺟ۰ﮒﭦ۵ﻠﻛﺛ?        if volatility > 0.05:
            confidence *= 0.8
        
        return confidence
```

#### 4.1.2 ﮔ۷۰ﮒﮔ ۰ﮒﮔﺗﮔﺏ

```python
class MarketImpactCalibrator:
    """ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮔ ۰ﮒﮒ?    
    ﻝﺑ۱ﮒﺙ: CALIBRATOR.MARKET_IMPACT.001
    ﻟﻟﺑ۲: ﻛﺛﺟﻝ۷ﮒﮒﺎﮔﺍﮔ؟ﮔ ۰ﮒﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮒﮔﺍ
    """
    
    def __init__(self, model: MarketImpactModel):
        self.model = model
        self.logger = logging.getLogger(__name__)
        
    def calibrate(self, 
                 historical_data: pd.DataFrame,
                 calibration_config: CalibrationConfig) -> CalibrationResult:
        """ﮔ ۰ﮒﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒ
        
        ﮔ ۰ﮒﮔﭖﻝ۷:
        1. ﮔﺍﮔ؟ﻠ۱ﮒ۳ﻝ?        2. ﻝﺗﮒﺝﮒﺓ۴ﻝ۷
        3. ﮒﮔﺍﻛﺙﺍﻟ؟۰
        4. ﮔ۷۰ﮒﻠ۹ﻟﺁ
        5. ﻝﮔﮔ ۰ﮒﮔ۴ﮒ
        """
        self.logger.info("Starting market impact model calibration...")
        
        # 1. ﮔﺍﮔ؟ﻠ۱ﮒ۳ﻝ?        cleaned_data = self._preprocess_data(historical_data)
        
        # 2. ﻝﺗﮒﺝﮒﺓ۴ﻝ۷
        features = self._engineer_features(cleaned_data)
        
        # 3. ﮒﮔﺍﻛﺙﺍﻟ؟۰
        estimated_params = self._estimate_parameters(features, calibration_config)
        
        # 4. ﮔ۷۰ﮒﻠ۹ﻟﺁ
        validation_result = self._validate_model(estimated_params, cleaned_data)
        
        # 5. ﮔﺑﮔﺍﮔ۷۰ﮒﮒﮔﺍ
        self._update_model_parameters(estimated_params)
        
        # 6. ﻝﮔﮔ ۰ﮒﮔ۴ﮒ
        calibration_report = self._generate_calibration_report(
            estimated_params, validation_result
        )
        
        self.logger.info("Market impact model calibration completed.")
        
        return CalibrationResult(
            success=True,
            parameters=estimated_params,
            validation=validation_result,
            report=calibration_report,
            timestamp=datetime.now()
        )
    
    def _preprocess_data(self, historical_data: pd.DataFrame) -> pd.DataFrame:
        """ﮔﺍﮔ؟ﻠ۱ﮒ۳ﻝ?        
        ﮒ۳ﻝﮔ­۴ﻠ۹۳:
        1. ﮒﭨﻠ۳ﮒﺙﮒﺕﺕﮒ?        2. ﮒ۰،ﮒﻝﺙﭦﮒ۳ﺎﮒ?        3. ﮔ ﮒﮒ?        """
        cleaned_data = historical_data.copy()
        
        # ﮒﭨﻠ۳ﮒﺙﮒﺕﺕﮒ?3ﺵﮒﮒ)
        for col in ['price_impact', 'volume', 'volatility']:
            mean = cleaned_data[col].mean()
            std = cleaned_data[col].std()
            cleaned_data = cleaned_data[
                (cleaned_data[col] >= mean - 3*std) &
                (cleaned_data[col] <= mean + 3*std)
            ]
        
        # ﮒ۰،ﮒﻝﺙﭦﮒ۳ﺎﮒ?        cleaned_data = cleaned_data.fillna(method='ffill')
        
        return cleaned_data
    
    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """ﻝﺗﮒﺝﮒﺓ۴ﻝ۷
        
        ﻝﺗﮒﺝ:
        1. ﮒﻛﺕﻝ?= ﻟ؟۱ﮒﻠ?/ ﮒﺗﺏﮒﮔﻛﭦ۳ﻠ?        2. ﻝﺕﮒﺁﺗﮔﺏ۱ﮒ۷ﻝ?= ﮔﺏ۱ﮒ۷ﻝ?/ ﮒﺗﺏﮒﮔﺏ۱ﮒ۷ﻝ?        3. ﮔﭖﮒ۷ﮔ۶ﮔﮔ ?= ﮔﻛﭦ۳ﻠ?/ ﮒﺕﮒ?        """
        features = data.copy()
        
        features['participation_rate'] = features['order_size'] / features['average_volume']
        features['relative_volatility'] = features['volatility'] / features['volatility'].rolling(20).mean()
        features['liquidity_indicator'] = features['volume'] / features['market_cap']
        
        return features
    
    def _estimate_parameters(self, 
                           features: pd.DataFrame,
                           config: CalibrationConfig) -> Dict[str, float]:
        """ﮒﮔﺍﻛﺙﺍﻟ؟۰
        
        ﻛﺛﺟﻝ۷ﮔﺗﮔﺏ:
        1. ﻝﭦﺟﮔ۶ﮒﮒﺛ?ﮒﭦﻝ۰ﮔﺗﮔﺏ)
        2. ﻠﻝﭦﺟﮔ۶ﻛﺙﮒ?ﻠ،ﻝﭦ۶ﮔﺗﮔﺏ)
        """
        from scipy.optimize import minimize
        
        # ﮒﮒ۳ﮔﺍﮔ؟
        X = features[['participation_rate', 'relative_volatility']].values
        y = features['price_impact'].values
        
        # ﮒ؟ﻛﺗﮔﮒ۳ﺎﮒﺛﮔﺍ
        def loss_function(params):
            temp_coef, perm_coef = params
            
            # ﻠ۱ﮔﭖﮒﺎﮒﭨ
            predicted_impact = temp_coef * X[:, 0] * X[:, 1] + perm_coef * X[:, 0]
            
            # ﻟ؟۰ﻝ؟MSE
            mse = np.mean((predicted_impact - y) ** 2)
            
            # ﮔﺓﭨﮒ ﮔ­۲ﮒﮒ?            regularization = config.regularization_coef * (temp_coef**2 + perm_coef**2)
            
            return mse + regularization
        
        # ﻛﺙﮒﮒﮔﺍ
        initial_params = [0.1, 0.05]  # ﮒﮒ۶ﻝﮔﭖ
        result = minimize(
            loss_function,
            initial_params,
            method='L-BFGS-B',
            bounds=[(0, 1), (0, 1)]  # ﮒﮔﺍﻟﮒﺑ[0, 1]
        )
        
        estimated_params = {
            'temporary_impact_coef': result.x[0],
            'permanent_impact_coef': result.x[1],
            'optimization_success': result.success,
            'final_loss': result.fun
        }
        
        return estimated_params
    
    def _validate_model(self, 
                       params: Dict[str, float],
                       data: pd.DataFrame) -> ValidationResult:
        """ﻠ۹ﻟﺁﮔ۷۰ﮒ
        
        ﻠ۹ﻟﺁﮔﺗﮔﺏ:
        1. ﮔ ﺓﮔ؛ﮒﻠ۹ﻟﺁ?Rﺡﺎ)
        2. ﮔ ﺓﮔ؛ﮒ۳ﻠ۹ﻟﺁ?ﻛﭦ۳ﮒﻠ۹ﻟﺁ)
        3. ﮔ؟ﮒﺓ؟ﮒﮔ
        """
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import r2_score, mean_absolute_error
        
        # ﮒﮒﺎﮔﺍﮔ؟
        train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
        
        # ﻟ؟­ﻝﭨﻠﻠ۹ﻟﺁ?        train_pred = self._predict_impact(train_data, params)
        train_r2 = r2_score(train_data['price_impact'], train_pred)
        train_mae = mean_absolute_error(train_data['price_impact'], train_pred)
        
        # ﮔﭖﻟﺁﻠﻠ۹ﻟﺁ?        test_pred = self._predict_impact(test_data, params)
        test_r2 = r2_score(test_data['price_impact'], test_pred)
        test_mae = mean_absolute_error(test_data['price_impact'], test_pred)
        
        return ValidationResult(
            train_r2=train_r2,
            test_r2=test_r2,
            train_mae=train_mae,
            test_mae=test_mae,
            is_valid=test_r2 > 0.5 and test_mae < 0.02
        )
    
    def _predict_impact(self, data: pd.DataFrame, params: Dict[str, float]) -> np.ndarray:
        """ﻠ۱ﮔﭖﮒﺕﮒﭦﮒﺎﮒﭨ"""
        participation_rate = data['order_size'] / data['average_volume']
        relative_volatility = data['volatility'] / data['volatility'].rolling(20).mean()
        
        predicted_impact = (
            params['temporary_impact_coef'] * participation_rate * relative_volatility +
            params['permanent_impact_coef'] * participation_rate
        )
        
        return predicted_impact.values
    
    def _update_model_parameters(self, params: Dict[str, float]):
        """ﮔﺑﮔﺍﮔ۷۰ﮒﮒﮔﺍ"""
        self.model.temporary_impact_coef = params['temporary_impact_coef']
        self.model.permanent_impact_coef = params['permanent_impact_coef']
        self.model.is_calibrated = True
        self.model.calibration_date = datetime.now()
        self.model.calibration_metrics = params
    
    def _generate_calibration_report(self,
                                    params: Dict[str, float],
                                    validation: ValidationResult) -> str:
        """ﻝﮔﮔ ۰ﮒﮔ۴ﮒ"""
        report = f"""
# ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮔ ۰ﮒﮔ۴ﮒ

## ﮔ ۰ﮒﮔ۵ﻟ۶
- **ﮔ ۰ﮒﮔ۴ﮔ**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **ﻛﺙﮒﮔﮒ**: {params['optimization_success']}
- **ﮔﻝﭨﮔﮒ۳?*: {params['final_loss']:.6f}

## ﮔ ۰ﮒﮒﮔﺍ
- **ﻛﺕﺑﮔﭘﮒﺎﮒﭨﻝﺏﭨﮔﺍ**: {params['temporary_impact_coef']:.6f}
- **ﮔﺍﺕﻛﺗﮒﺎﮒﭨﻝﺏﭨﮔﺍ**: {params['permanent_impact_coef']:.6f}

## ﻠ۹ﻟﺁﻝﭨﮔ
- **ﻟ؟­ﻝﭨﻠRﺡﺎ**: {validation.train_r2:.4f}
- **ﮔﭖﻟﺁﻠRﺡﺎ**: {validation.test_r2:.4f}
- **ﻟ؟­ﻝﭨﻠMAE**: {validation.train_mae:.6f}
- **ﮔﭖﻟﺁﻠMAE**: {validation.test_mae:.6f}
- **ﮔ۷۰ﮒﮔﮔ**: {'ﻗ?ﮔ? if validation.is_valid else 'ﻗ?ﮒ?}

## ﮒﭨﭦﻟ؟؟
"""
        
        if validation.is_valid:
            report += "- ﮔ۷۰ﮒﻠ۹ﻟﺁﻠﻟﺟ,ﮒﺁﻛﭨ۴ﻛﺛﺟﻝ۷\n"
            report += "- ﮒﭨﭦﻟ؟؟ﮒ؟ﮔﻠﮔﺍﮔ ۰ﮒ(ﮔﺁﮔﻛﺕﮔ؛?\n"
        else:
            report += "- ﻗ ﺅﺕ ﮔ۷۰ﮒﻠ۹ﻟﺁﮔ۹ﻠﻟﺟ,ﻠﻟ۵ﻟﺍﮔﺑﮒﮔﺍﮔﮒ۱ﮒ ﮔﺍﮔ؟\n"
            report += "- ﮒﭨﭦﻟ؟؟ﮔ۲ﮔ۴ﮔﺍﮔ؟ﻟﺑ۷ﻠﮒﻝﺗﮒﺝﮒﺓ۴ﻝ۷\n"
        
        return report
```

### 4.2 ﮔ ۰ﮒﮔﺍﮔ؟ﻟ۵ﮔﺎ

```yaml
market_impact_calibration:
  data_requirements:
    min_samples: 1000  # ﮔﮒﺍﮔ ﺓﮔ؛ﮔﺍ
    date_range:  # ﮔﺍﮔ؟ﮔﭘﻠﺑﻟﮒﺑ
      start_date: "2023-01-01"
      end_date: "2024-12-31"
    
    required_fields:  # ﮒﺟﻠﮒ­ﮔ؟ﭖ
      - timestamp
      - symbol
      - order_size
      - average_volume
      - volatility
      - price_impact
      - market_cap
    
    data_sources:
      - name: "ﮒﮒﺎﻛﭦ۳ﮔﮔﺍﮔ؟"
        priority: 1
        fields: ["order_size", "average_volume", "volatility"]
      - name: "Level-2ﻟ۰ﮔﮔﺍﮔ؟"
        priority: 2
        fields: ["price_impact", "market_cap"]
  
  calibration_config:
    method: "nonlinear_optimization"  # ﻝﭦﺟﮔ۶ﮒﮒﺛﮔﻠﻝﭦﺟﮔ۶ﻛﺙﮒ?    regularization_coef: 0.01  # ﮔ­۲ﮒﮒﻝﺏﭨﮔ?    validation_split: 0.2  # ﻠ۹ﻟﺁﻠﮔﺁﻛﺝ?    cross_validation: true  # ﮔﺁﮒ۵ﻛﭦ۳ﮒﻠ۹ﻟﺁ
    
  quality_thresholds:
    min_r2: 0.5  # ﮔﮒﺍRﺡﺎ
    max_mae: 0.02  # ﮔﮒ۳۶MAE
    max_parameter_value: 1.0  # ﮒﮔﺍﮔﮒ۳۶ﮒ?    
  recalibration:
    enabled: true
    frequency: "monthly"  # ﮔﺁﮔﻠﮔﺍﮔ ۰ﮒ
    trigger_conditions:  # ﻟ۶۵ﮒﮔ۰ﻛﭨﭘ
      - performance_degradation: 0.2  # ﮔ۶ﻟﺛﻛﺕﻠ20%
      - data_drift: true  # ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨ
```

### 4.3 ﮔ ۰ﮒﻠ۹ﻟﺁﮔ ﮒ

| ﻠ۹ﻟﺁﻝﭨﺑﮒﭦ۵ | ﻠ۹ﻟﺁﮔ ﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|---------|---------|---------|
| **ﮒﮔﺍﮒﻝﮔ?* | ﮒﮔﺍﮒ۷[0, 1]ﻟﮒﺑﮒ?| ﮒﮔﺍﻟﺝﺗﻝﮔ۲ﮔ?|
| **ﮔﮒﻛﺙﮒﭦ۵** | Rﺡﺎ ﻗ?0.5 | ﮔ ﺓﮔ؛ﮒ۳ﻠ۹ﻟﺁ?|
| **ﻠ۱ﮔﭖﮒﻝ۰؟ﮔ?* | MAE < 0.02 | ﮔ؟ﮒﺓ؟ﮒﮔ |
| **ﻝ۷ﺏﮒ؟ﮔ?* | ﮒﮔﺍﮔﺏ۱ﮒ۷ < 10% | ﮔﭨﮒ۷ﻝ۹ﮒ۲ﻠ۹ﻟﺁ |
| **ﻛﺕﮒ۰ﮒﻝﮔ?* | ﻛﺕﺑﮔﭘﮒﺎﮒﭨ > ﮔﺍﺕﻛﺗﮒﺎﮒﭨ | ﻝﻟ؟ﭦﻠ۹ﻟﺁ |

---

## ﻭ ﻛﭦﻙﻠﮔﮒﺍﻛﺕﭨﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵

### 5.1 ﮔﺑﮔﺍﻟﺁﺑﮔ

ﮔ؛ﻟ۰۴ﮒﮔﮔ۰۲ﮒﺓﺎﻟ۰۴ﮒﻛﭦﻛﺕﻛﺕ۹ﮒﺟﻠ۰ﭨﮔﺗﻟﺟﻠ۰ﺗﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟?

1. **IMP-001**: ﮒ؟ﮔﺑﻝﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒﭘﻟ؟ﺝﻟ؟۰
   - ﮒﺙﮒﺕﺕﮒﺎﮔ؛۰ﻝﭨﮔ
   - ﻝﭨﻛﺕﮒﺙﮒﺕﺕﮒ۳ﻝﮒ?   - ﻠﻟﺁﻝ­ﻝ۴ﮒﮔ۶ﻟ۰ﮒ۷
   - ﮒﺓﻛﺛﮒﭦﻝ۷ﮒﭦﮔﺁ

2. **IMP-002**: ﮒ؟ﮒﻝRLﮔ۷۰ﮒﻟ؟­ﻝﭨﻝﮔ۶ﮔﮔ ﻟ؟ﺝﻟ؟۰
   - ﮔ ﺕﮒﺟﻝﮔ۶ﮔﮔ ﻛﺛﻝﺏﭨ
   - ﻟ؟­ﻝﭨﻝﮔ۶ﮒ?   - ﻟ؟­ﻝﭨﻟﺟﻝ۷ﮒﺁﻟ۶ﮒ?   - ﮒﺙﮒﺕﺕﮔ۲ﮔﭖﮒﮒﻟ­۵

3. **IMP-003**: ﻟﺁ۵ﻝﭨﻝﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮔ ۰ﮒﮔﺗﮔ۰?   - ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮒﭦﻝ۰
   - ﮔ۷۰ﮒﮔ ۰ﮒﮔﺗﮔﺏ
   - ﮔ ۰ﮒﮔﺍﮔ؟ﻟ۵ﮔﺎ
   - ﮔ ۰ﮒﻠ۹ﻟﺁﮔ ﮒ

### 5.2 ﻛﺕﻛﺕﮔ­۴ﻟ۰ﮒ?
1. **ﻝ،ﮒﺏﮔ۶ﻟ۰**: ﮒﺍﮔ؛ﻟ۰۴ﮒﮔﮔ۰۲ﻝﮒﮒ؟ﺗﻠﮔﮒﺍﻛﺕﭨﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵
2. **ﻛﭨ۲ﻝ ﮒ؟ﻝﺍ**: ﮔﻝ۶ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﮒ؟ﻝﺍﻛﺕﻛﺕ۹ﮔﺗﻟﺟﻠ۰?3. **ﮒﮒﮔﭖﻟﺁ**: ﻛﺕﭦﻛﺕﻛﺕ۹ﮔﺗﻟﺟﻠ۰ﺗﻝﺙﮒﮒﮒﮔﭖﻟﺁ
4. **ﻠﮔﮔﭖﻟﺁ**: ﻠ۹ﻟﺁﻛﺕﻛﺕ۹ﮔﺗﻟﺟﻠ۰ﺗﻛﺕﻝﺍﮔﻝﺏﭨﻝﭨﻝﻠﮔ?
---

**ﻝﮔ؛**: v1.0 | **ﮔﺑﮔﺍ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ?