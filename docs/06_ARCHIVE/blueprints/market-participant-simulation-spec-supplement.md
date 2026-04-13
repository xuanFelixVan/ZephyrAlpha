---
module_id: MARKET_PARTICIPANT_SIMULATION_SPEC_SUPPLEMENT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - MARKET_PARTICIPANT_SIMULATION_SUPPLEMENT技术规范
layer: layer_06
standard_type: ﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵ﻟ۰۴ﮒﮔﮔ۰۲
applicable_scope: "ﮒﺕﮒﭦﮒﻛﺕﻟﻟ۰ﻛﺕﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨ?compliance_level: ﻛﺕﻛﺕﮔﮒ"
parent_document: ./MARKET_PARTICIPANT_SIMULATION_SPEC.md
implementation_status: ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ
---
```
```---
```











# ﮒﺕﮒﭦﮒﻛﺕﻟﻟ۰ﻛﺕﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨ?- ﮒﺟﻠ۰ﭨﮔﺗﻟﺟﻠ۰ﺗﻟ۰۴ﮒﻟ؟ﺝﻟ؟?



> **核心职责**: 文档内容说明



> **职责边界**: 



> - ✅ 本文档负责：文档内容说明相关内容



> - ❌ 本文档不负责：其他模块内容







> **ﻝﮔ؛**: v1.0



> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02



> **ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟**: Spec-Approver (ﮒ؟۰ﮔﺗﮔﭦﻟﺛﻛﺛ?



> **ﻝ؟ﻝ**: ﻟ۰۴ﮒﻛﺕﻛﺕ۹ﮒﺟﻠ۰ﭨﮔﺗﻟﺟﻠ۰ﺗﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰,ﻝ۰؟ﻛﺟﻟﮒﺝﮒ؟ﮔﺑﮔ?> **ﻛﺙﮒﻝﭦ?*: P0 (24ﮒﺍﮔﭘﮒﮒ؟ﮔ?







```
```---
```







## ﻭ ﻛﺕﻙﮔﺗﻟﺟﻠ۰ﺗﮔ۵ﻟﺟﺍ







ﮔﺗﮔ؟ﮔﮔﺁﻟﺁﮒ؟۰ﮔ۴ﮒ?ﻠﻟ۵ﻟ۰۴ﮒﻛﭨ۴ﻛﺕﻛﺕﻛﺕ۹ﮒﺟﻠ۰ﭨﮔﺗﻟﺟﻠ۰ﺗ:







| ﮔﺗﻟﺟﻠ۰ﺗID | ﮔﺗﻟﺟﮒﮒ؟ﺗ | ﻛﺙﮒﻝﭦ?| ﮒ؟ﮔﮔﮒ |



|---------|---------|--------|---------|



| **IMP-001** | ﻟ۰۴ﮒﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒ?| P0 | ﮔﮔﮔ۴ﮒ۲ﻠﺛﮔﮒﺙﮒﺕﺕﮒ۳ﻝ?ﻠﻟﺁﮔﭦﮒﭘﮒ؟ﮒ |



| **IMP-002** | ﮒ؟ﮒRLﮔ۷۰ﮒﻟ؟ﻝﭨﻝﮔ۶ﮔﮔ | P1 | ﻟ؟ﻝﭨﻟﺟﻝ۷ﮒﺁﻟ۶ﮒ?ﮔ۶ﻟﺛﮔﮔﮒ؟ﮔﭘﻝﮔ۶ |



| **IMP-003** | ﻟ۰۴ﮒﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮔ۰ﮒﮔﺗﮔ۰ | P1 | ﮔ۰ﮒﮔﭖﻝ۷ﮔﺕﮔﺍ,ﻠ۹ﻟﺁﮔﮒﮔﻝ۰؟ |







```
```---
```







## ﻭ۶ ﻛﭦﻙIMP-001: ﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒﭘﻟ؟ﺝﻟ؟?



### 2.1 ﮒﺙﮒﺕﺕﮒ۳ﻝﮔﭘﮔ







#### 2.1.1 ﮒﺙﮒﺕﺕﮒﺎﮔ؛۰ﻝﭨﮔ







```python



class MarketSimulationException(Exception):



    """ﮒﺕﮒﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨﮒﭦﻝ۰ﮒﺙﮒﺕﺕ



    



    ﻝﺑ۱ﮒﺙ: EXCEPTION.BASE.001



    """



    def __init__(self, message: str, error_code: str = None, context: Dict = None):



        self.message = message



        self.error_code = error_code or "UNKNOWN_ERROR"



        self.context = context or {}



        self.timestamp = datetime.now()



        super().__init__(self.message)











class DataAcquisitionException(MarketSimulationException):



    """ﮔﺍﮔ؟ﻠﻠﮒﺙﮒﺕﺕ



    



    ﻝﺑ۱ﮒﺙ: EXCEPTION.DATA.001



ﮒﭦﮔﺁ: ﮔﺍﮔ؟ﮔﭦﻛﺕﮒﺁﻝ۷ﻙﮔﺍﮔ؟ﮔﺙﮒﺙﻠﻟﺁﺁﻙﮔﺍﮔ؟ﻝﺙﭦﮒ۳?    """



    def __init__(self, source: str, message: str, **kwargs):



        self.source = source



        error_code = f"DATA_ACQUISITION_{source.upper()}"



        super().__init__(message, error_code, **kwargs)











class AgentDecisionException(MarketSimulationException):



"""ﮔﭦﻟﺛﻛﺛﮒﺏﻝﮒﺙﮒﺕ?



    ﻝﺑ۱ﮒﺙ: EXCEPTION.AGENT.001



ﮒﭦﮔﺁ: ﮔﭦﻟﺛﻛﺛﮒﺏﻝﮒ۳ﺎﻟﺑ۴ﻙﻝﭘﮔﮒﺙﮒﺕﺕﻙﮒﮔﺍﻠﻟﺁ?    """



    def __init__(self, agent_type: str, message: str, **kwargs):



        self.agent_type = agent_type



        error_code = f"AGENT_DECISION_{agent_type.upper()}"



        super().__init__(message, error_code, **kwargs)











class RLTrainingException(MarketSimulationException):



"""RLﻟ؟ﻝﭨﮒﺙﮒﺕﺕ



    



    ﻝﺑ۱ﮒﺙ: EXCEPTION.RL.001



ﮒﭦﮔﺁ: ﮔ۷۰ﮒﻟ؟ﻝﭨﮒ۳ﺎﻟﺑ۴ﻙﮔ۱ﺁﮒﭦ۵ﻝﻝﺕﻙﮔﭘﮔﮒ۳ﺎﻟﺑ?    """



    def __init__(self, model_name: str, message: str, **kwargs):



        self.model_name = model_name



        error_code = f"RL_TRAINING_{model_name.upper()}"



        super().__init__(message, error_code, **kwargs)











class MarketImpactException(MarketSimulationException):



    """ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮒﺙﮒﺕﺕ



    



    ﻝﺑ۱ﮒﺙ: EXCEPTION.MARKET_IMPACT.001



ﮒﭦﮔﺁ: ﮒﺕﮒﭦﮒﺎﮒﭨﻟ؟۰ﻝ؟ﮒ۳ﺎﻟﺑ۴ﻙﮒﮔﺍﮔ۰ﮒﻠﻟﺁ?    """



    def __init__(self, message: str, **kwargs):



        error_code = "MARKET_IMPACT_ERROR"



        super().__init__(message, error_code, **kwargs)



```







#### 2.1.2 ﮒﺙﮒﺕﺕﮒ۳ﻝﮒ۷ﻟ؟ﺝﻟ؟?



```python



class ExceptionHandler:



    """ﻝﭨﻛﺕﮒﺙﮒﺕﺕﮒ۳ﻝﮒ?    



    ﻝﺑ۱ﮒﺙ: HANDLER.EXCEPTION.001



ﻟﻟﺑ۲: ﻝﭨﻛﺕﮒ۳ﻝﻝﺏﭨﻝﭨﮒﺙﮒﺕﺕ,ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟ,ﮒﻠﮒﻟ?    """



    



    def __init__(self, config: ExceptionHandlerConfig):



        self.config = config



        self.logger = logging.getLogger(__name__)



        self.alert_manager = AlertManager()



        self.error_recorder = ErrorRecorder()



        



    def handle_exception(self, 



                        exception: MarketSimulationException,



                        context: Dict = None) -> ExceptionHandlingResult:



        """ﮒ۳ﻝﮒﺙﮒﺕﺕ



        



        ﮒ۳ﻝﮔﭖﻝ۷:



        1. ﻟ؟ﺍﮒﺛﮒﺙﮒﺕﺕﮔ۴ﮒﺟ



2. ﮒ۳ﮔﮒﺙﮒﺕﺕﻝﭦ۶ﮒ،



3. ﮒﻠﮒﻟ?ﮒ۵ﻠﻟ۵?



        4. ﻟ؟ﺍﮒﺛﮒﺍﻠﻟﺁﺁﮔﺍﮔ؟ﮒﭦ



        5. ﻟﺟﮒﮒ۳ﻝﻝﭨﮔ



        """



        # 1. ﻟ؟ﺍﮒﺛﮒﺙﮒﺕﺕﮔ۴ﮒﺟ



        self._log_exception(exception, context)



        



# 2. ﮒ۳ﮔﮒﺙﮒﺕﺕﻝﭦ۶ﮒ،



        severity = self._determine_severity(exception)



        



# 3. ﮒﻠﮒﻟ?        if severity in ['HIGH', 'CRITICAL']:



            self._send_alert(exception, severity)



        



        # 4. ﻟ؟ﺍﮒﺛﮒﺍﻠﻟﺁﺁﮔﺍﮔ؟ﮒﭦ



        self._record_error(exception, severity)



        



        # 5. ﻟﺟﮒﮒ۳ﻝﻝﭨﮔ



        return ExceptionHandlingResult(



            exception_id=self._generate_exception_id(),



            severity=severity,



            handled=True,



            timestamp=datetime.now()



        )



    



    def _log_exception(self, exception: MarketSimulationException, context: Dict):



        """ﻟ؟ﺍﮒﺛﮒﺙﮒﺕﺕﮔ۴ﮒﺟ"""



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



"""ﮒ۳ﮔﮒﺙﮒﺕﺕﻛﺕ۴ﻠﻝﭦ۶ﮒ،



        



        ﻝﭦ۶ﮒ،ﮒ؟ﻛﺗ:



- CRITICAL: ﻝﺏﭨﻝﭨﮒﺑ۸ﮔﭦﻙﮔﺍﮔ؟ﻛﺕ۱ﮒ۳?        - HIGH: ﮔﺕﮒﺟﮒﻟﺛﮒ۳ﺎﮔ



        - MEDIUM: ﻠ۷ﮒﮒﻟﺛﻠﻝﭦ۶



        - LOW: ﮒﺁﮒﺟﺛﻝ۴ﻝﮒﺙﮒﺕﺕ



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



"""ﮒﻠﮒﻟ?""



        alert = Alert(



            level=severity,



            title=f"ﮒﺕﮒﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨﮒﺙﮒﺕﺕ: {exception.error_code}",



            message=exception.message,



            context=exception.context,



            timestamp=datetime.now()



        )



        



        self.alert_manager.send_alert(alert)



    



    def _record_error(self, exception: MarketSimulationException, severity: str):



        """ﻟ؟ﺍﮒﺛﻠﻟﺁﺁﮒﺍﮔﺍﮔ؟ﮒﭦ"""



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



        """ﻝﮔﮒﺙﮒﺕﺕID"""



        import uuid



        return f"EXC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"



```







### 2.2 ﻠﻟﺁﮔﭦﮒﭘﻟ؟ﺝﻟ؟۰







#### 2.2.1 ﻠﻟﺁﻝﻝ۴







```python



from enum import Enum



from typing import Callable, Any



import time



from functools import wraps







class RetryStrategy(Enum):



"""ﻠﻟﺁﻝﻝ۴ﮔﻛﺕﺝ"""



    FIXED_INTERVAL = "fixed_interval"  # ﮒﭦﮒ؟ﻠﺑﻠ



    EXPONENTIAL_BACKOFF = "exponential_backoff"  # ﮔﮔﺍﻠﻠ?    LINEAR_BACKOFF = "linear_backoff"  # ﻝﭦﺟﮔ۶ﻠﻠ?







class RetryConfig:



    """ﻠﻟﺁﻠﻝﺛ؟



    



    ﻝﺑ۱ﮒﺙ: CONFIG.RETRY.001



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



    """ﻠﻟﺁﮔ۶ﻟ۰ﮒ?    



    ﻝﺑ۱ﮒﺙ: EXECUTOR.RETRY.001



    ﻟﻟﺑ۲: ﮔ۶ﻟ۰ﮒﺕ۵ﻠﻟﺁﮔﭦﮒﭘﻝﮔﻛﺛ



    """



    



    def __init__(self, config: RetryConfig):



        self.config = config



        self.logger = logging.getLogger(__name__)



        



    def execute_with_retry(self, 



                          operation: Callable[[], Any],



                          operation_name: str = "operation") -> Any:



        """ﮔ۶ﻟ۰ﮒﺕ۵ﻠﻟﺁﮔﭦﮒﭘﻝﮔﻛﺛ



        



        ﮔ۶ﻟ۰ﮔﭖﻝ۷:



        1. ﮔ۶ﻟ۰ﮔﻛﺛ



2. ﮒ۵ﮔﮒ۳ﺎﻟﺑ۴,ﮔﺗﮔ؟ﻠﻟﺁﻝﻝ۴ﻝﮒﺝ



        3. ﻠﻟﺁﮔﻛﺛ



        4. ﻟﺝﺝﮒﺍﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔﺍﮒﮔﮒﭦﮒﺙﮒﺕﺕ



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



                



                # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻛﺕﭦﮒﺁﻠﻟﺁﮒﺙﮒﺕ?                if not self._is_retryable_exception(e):



                    self.logger.error(



                        f"Operation '{operation_name}' failed with non-retryable exception: {e}"



                    )



                    raise



                



                # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟﺝﺝﮒﺍﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ?                if attempt >= self.config.max_retries:



                    self.logger.error(



                        f"Operation '{operation_name}' failed after {self.config.max_retries} retries"



                    )



                    raise



                



# ﻟ؟۰ﻝ؟ﻝﮒﺝﮔﭘﻠﺑ



                delay = self._calculate_delay(attempt)



                



                self.logger.warning(



                    f"Operation '{operation_name}' failed on attempt {attempt + 1}, "



                    f"retrying in {delay:.2f}s. Error: {e}"



                )



                



                time.sleep(delay)



        



        raise last_exception



    



    def _is_retryable_exception(self, exception: Exception) -> bool:



        """ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻛﺕﭦﮒﺁﻠﻟﺁﮒﺙﮒﺕ?""



        return any(



            isinstance(exception, retryable_exc) 



            for retryable_exc in self.config.retryable_exceptions



        )



    



    def _calculate_delay(self, attempt: int) -> float:



        """ﻟ؟۰ﻝ؟ﻠﻟﺁﮒﭨﭘﻟﺟﮔﭘﻠﺑ"""



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



    """ﻠﻟﺁﻟ۲ﻠ۴ﺍﮒ?    



    ﻝﺑ۱ﮒﺙ: DECORATOR.RETRY.001



    ﻝ۷ﮔﺏ: @retry_on_failure(RetryConfig(max_retries=3))



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







#### 2.2.2 ﮒﺓﻛﺛﮒﭦﻝ۷ﮒﭦﮔﺁ







```python



class DataCollectorWithRetry:



    """ﮒﺕ۵ﻠﻟﺁﮔﭦﮒﭘﻝﮔﺍﮔ؟ﻠﻠﮒ?    



    ﻝﺑ۱ﮒﺙ: COLLECTOR.DATA.RETRY.001



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



        """ﻠﻠﻠﺝﻟﮔ۵ﮔﺍﮔ?ﮒﺕ۵ﻠﻟﺁ?"""



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



        """ﻠﻠLevel-2ﮔﺍﮔ؟(ﮒﺕ۵ﻠﻟﺁ?"""



        try:



            # ﮔ۷۰ﮔLevel-2ﮔﺍﮔ؟ﻠﻠ



            data = self._fetch_level2_from_source(symbol, date)



            return data



        except Exception as e:



            raise DataAcquisitionException(



                source="level2",



                message=f"Failed to collect Level-2 data for {symbol} on {date}: {e}",



                context={'symbol': symbol, 'date': date}



            )











class AgentDecisionWithRetry:



"""ﮒﺕ۵ﻠﻟﺁﮔﭦﮒﭘﻝﮔﭦﻟﺛﻛﺛﮒﺏﻝ?



    ﻝﺑ۱ﮒﺙ: AGENT.DECISION.RETRY.001



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



"""ﻝﮔﮒﺏﻝ(ﮒﺕ۵ﻠﻟﺁ?"""



        operation = lambda: self.agent.generate_trading_decision(market_state)



        



        try:



            return self.executor.execute_with_retry(



                operation, 



                f"{self.agent.__class__.__name__}.generate_trading_decision"



            )



        except Exception as e:



# ﮒ۵ﮔﻠﻟﺁﮒ۳ﺎﻟﺑ۴,ﻟﺟﮒﻠﭨﻟ؟۳ﮒﺏﻝ



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







```
```---
```







## ﻭ ﻛﺕﻙIMP-002: RLﮔ۷۰ﮒﻟ؟ﻝﭨﻝﮔ۶ﮔﮔﻟ؟ﺝﻟ؟۰







### 3.1 ﻝﮔ۶ﮔﮔﻛﺛﻝﺏﭨ







#### 3.1.1 ﮔﺕﮒﺟﻝﮔ۶ﮔﮔ







```python



@dataclass



class RLTrainingMetrics:



"""RLﻟ؟ﻝﭨﻝﮔ۶ﮔﮔ



    



    ﻝﺑ۱ﮒﺙ: METRICS.RL.001



    """



# ﮒﭦﻝ۰ﮔﮔ



    episode: int  # ﮒﺛﮒﮒﮒ



step: int  # ﮒﺛﮒﮔ۴ﮔﺍ



    timestamp: datetime  # ﮔﭘﻠﺑﮔ?    



# ﮒ۴ﮒﺎﮔﮔ



    episode_reward: float  # ﮒﮒﮔﭨﮒ۴ﮒ?    average_reward: float  # ﮒﺗﺏﮒﮒ۴ﮒﺎ



reward_std: float  # ﮒ۴ﮒﺎﮔﮒﮒﺓ?



# ﮔﮒ۳ﺎﮔﮔ



    actor_loss: float  # Actorﮔﮒ۳ﺎ



    critic_loss: float  # Criticﮔﮒ۳ﺎ



    entropy: float  # ﻝ?ﮔ۱ﻝﺑ۱ﻝ۷ﮒﭦ۵)



    



# ﮔ۶ﻟﺛﮔﮔ



    sharpe_ratio: float  # ﮒ۳ﮔ؟ﮔﺁﻝ



    max_drawdown: float  # ﮔﮒ۳۶ﮒﮔ?    win_rate: float  # ﻟﻝ



    profit_factor: float  # ﻝﻛﭦﮔﺁ?    



# ﻟ؟ﻝﭨﻝ۷ﺏﮒ؟ﮔ۶ﮔﮔ?    gradient_norm: float  # ﮔ۱ﺁﮒﭦ۵ﻟﮔﺍ



learning_rate: float  # ﮒ۵ﻛﺗﻝ?    exploration_rate: float  # ﮔ۱ﻝﺑ۱ﻝ?



# ﻟﭖﮔﭦﮔﮔ



gpu_memory_used: float  # GPUﮒﮒﻛﺛﺟﻝ۷



training_time: float  # ﻟ؟ﻝﭨﮔﭘﻠﺑ











class RLTrainingMonitor:



"""RLﻟ؟ﻝﭨﻝﮔ۶ﮒ?



    ﻝﺑ۱ﮒﺙ: MONITOR.RL.001



ﻟﻟﺑ۲: ﮒ؟ﮔﭘﻝﮔ۶RLﻟ؟ﻝﭨﻟﺟﻝ۷,ﻟ؟ﺍﮒﺛﮔﮔ,ﻝﮔﮔ۴ﮒ



    """



    



    def __init__(self, config: RLTrainingMonitorConfig):



        self.config = config



        self.logger = logging.getLogger(__name__)



        self.metrics_history: List[RLTrainingMetrics] = []



        self.tensorboard_writer = SummaryWriter(config.log_dir)



        self.alert_manager = AlertManager()



        



    def record_metrics(self, metrics: RLTrainingMetrics):



"""ﻟ؟ﺍﮒﺛﻟ؟ﻝﭨﮔﮔ



        



        ﻟ؟ﺍﮒﺛﮔﭖﻝ۷:



1. ﮔﺓﭨﮒﮒﺍﮒﮒﺎﻟ؟ﺍﮒﺛ?        2. ﮒﮒ۴TensorBoard



3. ﮔ۲ﮔ۴ﮒﺙﮒﺕﺕﮔﮔ?        4. ﮒﻠﮒﻟ?ﮒ۵ﻠﻟ۵?



        """



# 1. ﮔﺓﭨﮒﮒﺍﮒﮒﺎﻟ؟ﺍﮒﺛ?        self.metrics_history.append(metrics)



        



        # 2. ﮒﮒ۴TensorBoard



        self._write_to_tensorboard(metrics)



        



# 3. ﮔ۲ﮔ۴ﮒﺙﮒﺕﺕﮔﮔ?        anomalies = self._check_anomalies(metrics)



        



# 4. ﮒﻠﮒﻟ?        if anomalies:



            self._send_training_alert(metrics, anomalies)



    



    def _write_to_tensorboard(self, metrics: RLTrainingMetrics):



        """ﮒﮒ۴TensorBoard"""



# ﮒ۴ﮒﺎﮔﮔ



        self.tensorboard_writer.add_scalar(



            'Reward/Episode_Reward', metrics.episode_reward, metrics.episode



        )



        self.tensorboard_writer.add_scalar(



            'Reward/Average_Reward', metrics.average_reward, metrics.episode



        )



        



# ﮔﮒ۳ﺎﮔﮔ



        self.tensorboard_writer.add_scalar(



            'Loss/Actor_Loss', metrics.actor_loss, metrics.episode



        )



        self.tensorboard_writer.add_scalar(



            'Loss/Critic_Loss', metrics.critic_loss, metrics.episode



        )



        



# ﮔ۶ﻟﺛﮔﮔ



        self.tensorboard_writer.add_scalar(



            'Performance/Sharpe_Ratio', metrics.sharpe_ratio, metrics.episode



        )



        self.tensorboard_writer.add_scalar(



            'Performance/Max_Drawdown', metrics.max_drawdown, metrics.episode



        )



        



# ﻟ؟ﻝﭨﻝ۷ﺏﮒ؟ﮔ۶ﮔﮔ?        self.tensorboard_writer.add_scalar(



            'Training/Gradient_Norm', metrics.gradient_norm, metrics.episode



        )



        self.tensorboard_writer.add_scalar(



            'Training/Entropy', metrics.entropy, metrics.episode



        )



    



    def _check_anomalies(self, metrics: RLTrainingMetrics) -> List[str]:



"""ﮔ۲ﮔ۴ﮒﺙﮒﺕﺕﮔﮔ?""



        anomalies = []



        



        # ﮔ۲ﮔ۴ﮒ۴ﮒﺎﮒﺙﮒﺕ?        if metrics.episode_reward < self.config.reward_lower_bound:



            anomalies.append(f"Episode reward too low: {metrics.episode_reward}")



        



        # ﮔ۲ﮔ۴ﮔﮒ۳ﺎﮒﺙﮒﺕ?        if abs(metrics.actor_loss) > self.config.loss_upper_bound:



            anomalies.append(f"Actor loss too high: {metrics.actor_loss}")



        



        if abs(metrics.critic_loss) > self.config.loss_upper_bound:



            anomalies.append(f"Critic loss too high: {metrics.critic_loss}")



        



        # ﮔ۲ﮔ۴ﮔ۱ﺁﮒﭦ۵ﻝﻝ?        if metrics.gradient_norm > self.config.gradient_norm_threshold:



            anomalies.append(f"Gradient explosion detected: {metrics.gradient_norm}")



        



        # ﮔ۲ﮔ۴ﮔ۶ﻟﺛﻛﺕﻠ



        if len(self.metrics_history) >= 10:



            recent_sharpe = [m.sharpe_ratio for m in self.metrics_history[-10:]]



            if metrics.sharpe_ratio < np.mean(recent_sharpe) * 0.5:



                anomalies.append(f"Performance degradation: Sharpe ratio dropped to {metrics.sharpe_ratio}")



        



        return anomalies



    



    def _send_training_alert(self, metrics: RLTrainingMetrics, anomalies: List[str]):



"""ﮒﻠﻟ؟ﻝﭨﮒﻟ?""



        alert = Alert(



            level='HIGH',



title=f"RLﻟ؟ﻝﭨﮒﺙﮒﺕﺕ: Episode {metrics.episode}",



            message=f"ﮔ۲ﮔﭖﮒﺍﻛﭨ۴ﻛﺕﮒﺙﮒﺕﺕ:\n" + "\n".join(anomalies),



            context={



                'episode': metrics.episode,



                'metrics': asdict(metrics),



                'anomalies': anomalies



            },



            timestamp=datetime.now()



        )



        



        self.alert_manager.send_alert(alert)



    



    def generate_training_report(self) -> str:



"""ﻝﮔﻟ؟ﻝﭨﮔ۴ﮒ"""



        if not self.metrics_history:



            return "No training data available"



        



        latest_metrics = self.metrics_history[-1]



        



        report = f"""



# RLﻟ؟ﻝﭨﮔ۴ﮒ







## ﻟ؟ﻝﭨﮔ۵ﻟ۶



- **ﮒﺛﮒﮒﮒ**: {latest_metrics.episode}



- **ﻟ؟ﻝﭨﮔﭘﻠﺑ**: {latest_metrics.training_time:.2f}ﻝ۶?- **GPUﮒﮒﻛﺛﺟﻝ۷**: {latest_metrics.gpu_memory_used:.2f}GB







## ﮒ۴ﮒﺎﮔﮔ



- **ﮒﮒﮔﭨﮒ۴ﮒ?*: {latest_metrics.episode_reward:.4f}



- **ﮒﺗﺏﮒﮒ۴ﮒﺎ**: {latest_metrics.average_reward:.4f}



- **ﮒ۴ﮒﺎﮔﮒﮒﺓ?*: {latest_metrics.reward_std:.4f}







## ﮔ۶ﻟﺛﮔﮔ



- **ﮒ۳ﮔ؟ﮔﺁﻝ**: {latest_metrics.sharpe_ratio:.4f}



- **ﮔﮒ۳۶ﮒﮔ?*: {latest_metrics.max_drawdown:.4f}



- **ﻟﻝ**: {latest_metrics.win_rate:.2%}



- **ﻝﻛﭦﮔﺁ?*: {latest_metrics.profit_factor:.4f}







## ﻟ؟ﻝﭨﻝ۷ﺏﮒ؟ﮔ?- **ﮔ۱ﺁﮒﭦ۵ﻟﮔﺍ**: {latest_metrics.gradient_norm:.4f}



- **ﮒ۵ﻛﺗﻝ?*: {latest_metrics.learning_rate:.6f}



- **ﮔ۱ﻝﺑ۱ﻝ?*: {latest_metrics.exploration_rate:.4f}







## ﮔﮒ۳ﺎﮔﮔ



- **Actorﮔﮒ۳ﺎ**: {latest_metrics.actor_loss:.4f}



- **Criticﮔﮒ۳ﺎ**: {latest_metrics.critic_loss:.4f}



- **ﻝ?*: {latest_metrics.entropy:.4f}



"""



        



        return report



```







#### 3.1.2 ﻟ؟ﻝﭨﻟﺟﻝ۷ﮒﺁﻟ۶ﮒ?



```python



class RLTrainingVisualizer:



"""RLﻟ؟ﻝﭨﮒﺁﻟ۶ﮒﮒ۷



    



    ﻝﺑ۱ﮒﺙ: VISUALIZER.RL.001



ﻟﻟﺑ۲: ﻝﮔﻟ؟ﻝﭨﻟﺟﻝ۷ﮒﺁﻟ۶ﮒﮒﺝﻟ۰?    """



    



    def __init__(self, monitor: RLTrainingMonitor):



        self.monitor = monitor



        



    def plot_training_curves(self, save_path: str = None):



"""ﻝﭨﮒﭘﻟ؟ﻝﭨﮔﺎﻝﭦﺟ"""



        import matplotlib.pyplot as plt



        



        metrics = self.monitor.metrics_history



        



        fig, axes = plt.subplots(2, 3, figsize=(15, 10))



        



        # ﮒ۴ﮒﺎﮔﺎﻝﭦﺟ



        episodes = [m.episode for m in metrics]



        rewards = [m.episode_reward for m in metrics]



        axes[0, 0].plot(episodes, rewards)



        axes[0, 0].set_title('Episode Reward')



        axes[0, 0].set_xlabel('Episode')



        axes[0, 0].set_ylabel('Reward')



        



        # ﮔﮒ۳ﺎﮔﺎﻝﭦﺟ



        actor_losses = [m.actor_loss for m in metrics]



        critic_losses = [m.critic_loss for m in metrics]



        axes[0, 1].plot(episodes, actor_losses, label='Actor Loss')



        axes[0, 1].plot(episodes, critic_losses, label='Critic Loss')



        axes[0, 1].set_title('Training Losses')



        axes[0, 1].set_xlabel('Episode')



        axes[0, 1].set_ylabel('Loss')



        axes[0, 1].legend()



        



        # ﮒ۳ﮔ؟ﮔﺁﻝﮔﺎﻝﭦﺟ



        sharpe_ratios = [m.sharpe_ratio for m in metrics]



        axes[0, 2].plot(episodes, sharpe_ratios)



        axes[0, 2].set_title('Sharpe Ratio')



        axes[0, 2].set_xlabel('Episode')



        axes[0, 2].set_ylabel('Sharpe Ratio')



        



        # ﮔﮒ۳۶ﮒﮔ۳ﮔﺎﻝﭦ?        max_drawdowns = [m.max_drawdown for m in metrics]



        axes[1, 0].plot(episodes, max_drawdowns)



        axes[1, 0].set_title('Max Drawdown')



        axes[1, 0].set_xlabel('Episode')



        axes[1, 0].set_ylabel('Drawdown')



        



        # ﮔ۱ﺁﮒﭦ۵ﻟﮔﺍﮔﺎﻝﭦﺟ



        gradient_norms = [m.gradient_norm for m in metrics]



        axes[1, 1].plot(episodes, gradient_norms)



        axes[1, 1].set_title('Gradient Norm')



        axes[1, 1].set_xlabel('Episode')



        axes[1, 1].set_ylabel('Norm')



        



        # ﮔ۱ﻝﺑ۱ﻝﮔﺎﻝﭦ?        exploration_rates = [m.exploration_rate for m in metrics]



        axes[1, 2].plot(episodes, exploration_rates)



        axes[1, 2].set_title('Exploration Rate')



        axes[1, 2].set_xlabel('Episode')



        axes[1, 2].set_ylabel('Rate')



        



        plt.tight_layout()



        



        if save_path:



            plt.savefig(save_path)



        



        return fig



```







### 3.2 ﻟ؟ﻝﭨﻝﮔ۶ﻠﻝﺛ؟







```yaml



rl_training_monitor:



  log_dir: "logs/rl_training/"



  



monitoring_interval: 100  # ﮔﺁ?00ﮔ۴ﻟ؟ﺍﮒﺛﻛﺕﮔ؛?



  anomaly_detection:



    reward_lower_bound: -1000.0



    loss_upper_bound: 10000.0



    gradient_norm_threshold: 100.0



    



  alert_thresholds:



consecutive_low_reward: 10  # ﻟﺟﻝﭨ10ﮒﮒﻛﺛﮒ۴ﮒ?    performance_degradation: 0.5  # ﮔ۶ﻟﺛﻛﺕﻠ50%



    



  visualization:



    enabled: true



update_interval: 1000  # ﮔﺁ?000ﮔ۴ﮔﺑﮔﺍﮒﺝﻟ۰?    save_dir: "reports/rl_training/"



    



  early_stopping:



    enabled: true



patience: 50  # 50ﮒﮒﮔﮔﺗﮒﮒﮒﮔ۱



    min_delta: 0.01  # ﮔﮒﺍﮔﺗﮒﻠﮒ?```







```---







## ﻭﺁ ﮒﻙIMP-003: ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮔ۰ﮒﮔﺗﮔ۰







### 4.1 ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﻟ؟ﺝﻟ؟۰







#### 4.1.1 ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮒﭦﻝ۰







```python



class MarketImpactModel:



    """ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒ



    



    ﻝﺑ۱ﮒﺙ: MODEL.MARKET_IMPACT.001



ﻝﻟ؟ﭦﮒﭦﻝ۰: Almgren-Chrissﮔ۷۰ﮒ + ﮒ؟ﻠﮒﺕﮒﭦﮔﺍﮔ؟ﮔ۰ﮒ



    """



    



    def __init__(self, config: MarketImpactConfig):



        self.config = config



        self.logger = logging.getLogger(__name__)



        



        # ﮔ۷۰ﮒﮒﮔﺍ



        self.temporary_impact_coef = None  # ﻛﺕﺑﮔﭘﮒﺎﮒﭨﻝﺏﭨﮔﺍ



        self.permanent_impact_coef = None  # ﮔﺍﺕﻛﺗﮒﺎﮒﭨﻝﺏﭨﮔﺍ



        self.volatility_coef = None  # ﮔﺏ۱ﮒ۷ﻝﻝﺏﭨﮔ?        self.liquidity_coef = None  # ﮔﭖﮒ۷ﮔ۶ﻝﺏﭨﮔ?        



# ﮔ۰ﮒﻝﭘﮔ?        self.is_calibrated = False



        self.calibration_date = None



        self.calibration_metrics = {}



        



    def calculate_market_impact(self,



                               order_size: float,



                               average_volume: float,



                               volatility: float,



                               execution_time: float) -> MarketImpactResult:



        """ﻟ؟۰ﻝ؟ﮒﺕﮒﭦﮒﺎﮒﭨ



        



        ﮒﮔﺍ:



            order_size: ﻟ؟۱ﮒﮒ۳۶ﮒﺍ(ﻟ۰ﮔﺍ)



            average_volume: ﮒﺗﺏﮒﮔﻛﭦ۳ﻠ?            volatility: ﮔﺏ۱ﮒ۷ﻝ?            execution_time: ﮔ۶ﻟ۰ﮔﭘﻠﺑ(ﮒ۳?



            



        ﻟﺟﮒ:



            MarketImpactResult: ﮒﺕﮒﭦﮒﺎﮒﭨﻝﭨﮔ



        """



        if not self.is_calibrated:



            raise MarketImpactException("Model not calibrated. Please calibrate first.")



        



        # ﻟ؟۰ﻝ؟ﮒﻛﺕﻝ?        participation_rate = order_size / (average_volume * execution_time)



        



        # ﻟ؟۰ﻝ؟ﻛﺕﺑﮔﭘﮒﺎﮒﭨ



        temporary_impact = self.temporary_impact_coef * participation_rate * volatility



        



        # ﻟ؟۰ﻝ؟ﮔﺍﺕﻛﺗﮒﺎﮒﭨ



        permanent_impact = self.permanent_impact_coef * participation_rate * volatility



        



        # ﻟ؟۰ﻝ؟ﮔﭨﮒﺎﮒ?        total_impact = temporary_impact + permanent_impact



        



        # ﻟ؟۰ﻝ؟ﮒﺎﮒﭨﮔﮔ؛



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



        """ﻟ؟۰ﻝ؟ﻝﺛ؟ﻛﺟ۰ﮒﭦ?        



        ﻝﺛ؟ﻛﺟ۰ﮒﭦ۵ﮒﭦﻛﭦ?



        1. ﮒﻛﺕﻝﮔﺁﮒ۵ﮒ۷ﮒﻝﻟﮒﺑﮒ?        2. ﮔﺏ۱ﮒ۷ﻝﮔﺁﮒ۵ﮒ۷ﮒﮒﺎﻟﮒﺑﮒ?        """



        confidence = 1.0



        



        # ﮒﻛﺕﻝﻟﺟﻠ،?ﻝﺛ؟ﻛﺟ۰ﮒﭦ۵ﻠﻛﺛ?        if participation_rate > 0.1:



            confidence *= 0.7



        



        # ﮔﺏ۱ﮒ۷ﻝﻟﺟﻠ،?ﻝﺛ؟ﻛﺟ۰ﮒﭦ۵ﻠﻛﺛ?        if volatility > 0.05:



            confidence *= 0.8



        



        return confidence



```







#### 4.1.2 ﮔ۷۰ﮒﮔ۰ﮒﮔﺗﮔﺏ







```python



class MarketImpactCalibrator:



"""ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮔ۰ﮒﮒ?



    ﻝﺑ۱ﮒﺙ: CALIBRATOR.MARKET_IMPACT.001



ﻟﻟﺑ۲: ﻛﺛﺟﻝ۷ﮒﮒﺎﮔﺍﮔ؟ﮔ۰ﮒﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮒﮔﺍ



    """



    



    def __init__(self, model: MarketImpactModel):



        self.model = model



        self.logger = logging.getLogger(__name__)



        



    def calibrate(self, 



                 historical_data: pd.DataFrame,



                 calibration_config: CalibrationConfig) -> CalibrationResult:



"""ﮔ۰ﮒﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒ



        



ﮔ۰ﮒﮔﭖﻝ۷:



        1. ﮔﺍﮔ؟ﻠ۱ﮒ۳ﻝ?        2. ﻝﺗﮒﺝﮒﺓ۴ﻝ۷



        3. ﮒﮔﺍﻛﺙﺍﻟ؟۰



        4. ﮔ۷۰ﮒﻠ۹ﻟﺁ



5. ﻝﮔﮔ۰ﮒﮔ۴ﮒ



        """



        self.logger.info("Starting market impact model calibration...")



        



        # 1. ﮔﺍﮔ؟ﻠ۱ﮒ۳ﻝ?        cleaned_data = self._preprocess_data(historical_data)



        



        # 2. ﻝﺗﮒﺝﮒﺓ۴ﻝ۷



        features = self._engineer_features(cleaned_data)



        



        # 3. ﮒﮔﺍﻛﺙﺍﻟ؟۰



        estimated_params = self._estimate_parameters(features, calibration_config)



        



        # 4. ﮔ۷۰ﮒﻠ۹ﻟﺁ



        validation_result = self._validate_model(estimated_params, cleaned_data)



        



        # 5. ﮔﺑﮔﺍﮔ۷۰ﮒﮒﮔﺍ



        self._update_model_parameters(estimated_params)



        



# 6. ﻝﮔﮔ۰ﮒﮔ۴ﮒ



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



        """ﮔﺍﮔ؟ﻠ۱ﮒ۳ﻝ?        



ﮒ۳ﻝﮔ۴ﻠ۹۳:



1. ﮒﭨﻠ۳ﮒﺙﮒﺕﺕﮒ?        2. ﮒ۰،ﮒﻝﺙﭦﮒ۳ﺎﮒ?        3. ﮔﮒﮒ?        """



        cleaned_data = historical_data.copy()



        



        # ﮒﭨﻠ۳ﮒﺙﮒﺕﺕﮒ?3ﺵﮒﮒ)



        for col in ['price_impact', 'volume', 'volatility']:



            mean = cleaned_data[col].mean()



            std = cleaned_data[col].std()



            cleaned_data = cleaned_data[



                (cleaned_data[col] >= mean - 3*std) &



                (cleaned_data[col] <= mean + 3*std)



            ]



        



        # ﮒ۰،ﮒﻝﺙﭦﮒ۳ﺎﮒ?        cleaned_data = cleaned_data.fillna(method='ffill')



        



        return cleaned_data



    



    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:



        """ﻝﺗﮒﺝﮒﺓ۴ﻝ۷



        



        ﻝﺗﮒﺝ:



1. ﮒﻛﺕﻝ?= ﻟ؟۱ﮒﻠ?/ ﮒﺗﺏﮒﮔﻛﭦ۳ﻠ?        2. ﻝﺕﮒﺁﺗﮔﺏ۱ﮒ۷ﻝ?= ﮔﺏ۱ﮒ۷ﻝ?/ ﮒﺗﺏﮒﮔﺏ۱ﮒ۷ﻝ?        3. ﮔﭖﮒ۷ﮔ۶ﮔﮔ?= ﮔﻛﭦ۳ﻠ?/ ﮒﺕﮒ?        """



        features = data.copy()



        



        features['participation_rate'] = features['order_size'] / features['average_volume']



        features['relative_volatility'] = features['volatility'] / features['volatility'].rolling(20).mean()



        features['liquidity_indicator'] = features['volume'] / features['market_cap']



        



        return features



    



    def _estimate_parameters(self, 



                           features: pd.DataFrame,



                           config: CalibrationConfig) -> Dict[str, float]:



        """ﮒﮔﺍﻛﺙﺍﻟ؟۰



        



        ﻛﺛﺟﻝ۷ﮔﺗﮔﺏ:



        1. ﻝﭦﺟﮔ۶ﮒﮒﺛ?ﮒﭦﻝ۰ﮔﺗﮔﺏ)



        2. ﻠﻝﭦﺟﮔ۶ﻛﺙﮒ?ﻠ،ﻝﭦ۶ﮔﺗﮔﺏ)



        """



        from scipy.optimize import minimize



        



        # ﮒﮒ۳ﮔﺍﮔ؟



        X = features[['participation_rate', 'relative_volatility']].values



        y = features['price_impact'].values



        



        # ﮒ؟ﻛﺗﮔﮒ۳ﺎﮒﺛﮔﺍ



        def loss_function(params):



            temp_coef, perm_coef = params



            



            # ﻠ۱ﮔﭖﮒﺎﮒﭨ



            predicted_impact = temp_coef * X[:, 0] * X[:, 1] + perm_coef * X[:, 0]



            



            # ﻟ؟۰ﻝ؟MSE



            mse = np.mean((predicted_impact - y) ** 2)



            



# ﮔﺓﭨﮒﮔ۲ﮒﮒ?            regularization = config.regularization_coef * (temp_coef**2 + perm_coef**2)



            



            return mse + regularization



        



        # ﻛﺙﮒﮒﮔﺍ



        initial_params = [0.1, 0.05]  # ﮒﮒ۶ﻝﮔﭖ



        result = minimize(



            loss_function,



            initial_params,



            method='L-BFGS-B',



            bounds=[(0, 1), (0, 1)]  # ﮒﮔﺍﻟﮒﺑ[0, 1]



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



        """ﻠ۹ﻟﺁﮔ۷۰ﮒ



        



        ﻠ۹ﻟﺁﮔﺗﮔﺏ:



1. ﮔﺓﮔ؛ﮒﻠ۹ﻟﺁ?Rﺡﺎ)



2. ﮔﺓﮔ؛ﮒ۳ﻠ۹ﻟﺁ?ﻛﭦ۳ﮒﻠ۹ﻟﺁ)



        3. ﮔ؟ﮒﺓ؟ﮒﮔ



        """



        from sklearn.model_selection import train_test_split



        from sklearn.metrics import r2_score, mean_absolute_error



        



        # ﮒﮒﺎﮔﺍﮔ؟



        train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)



        



# ﻟ؟ﻝﭨﻠﻠ۹ﻟﺁ?        train_pred = self._predict_impact(train_data, params)



        train_r2 = r2_score(train_data['price_impact'], train_pred)



        train_mae = mean_absolute_error(train_data['price_impact'], train_pred)



        



        # ﮔﭖﻟﺁﻠﻠ۹ﻟﺁ?        test_pred = self._predict_impact(test_data, params)



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



        """ﻠ۱ﮔﭖﮒﺕﮒﭦﮒﺎﮒﭨ"""



        participation_rate = data['order_size'] / data['average_volume']



        relative_volatility = data['volatility'] / data['volatility'].rolling(20).mean()



        



        predicted_impact = (



            params['temporary_impact_coef'] * participation_rate * relative_volatility +



            params['permanent_impact_coef'] * participation_rate



        )



        



        return predicted_impact.values



    



    def _update_model_parameters(self, params: Dict[str, float]):



        """ﮔﺑﮔﺍﮔ۷۰ﮒﮒﮔﺍ"""



        self.model.temporary_impact_coef = params['temporary_impact_coef']



        self.model.permanent_impact_coef = params['permanent_impact_coef']



        self.model.is_calibrated = True



        self.model.calibration_date = datetime.now()



        self.model.calibration_metrics = params



    



    def _generate_calibration_report(self,



                                    params: Dict[str, float],



                                    validation: ValidationResult) -> str:



"""ﻝﮔﮔ۰ﮒﮔ۴ﮒ"""



        report = f"""



# ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮔ۰ﮒﮔ۴ﮒ







## ﮔ۰ﮒﮔ۵ﻟ۶



- **ﮔ۰ﮒﮔ۴ﮔ**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}



- **ﻛﺙﮒﮔﮒ**: {params['optimization_success']}



- **ﮔﻝﭨﮔﮒ۳?*: {params['final_loss']:.6f}







## ﮔ۰ﮒﮒﮔﺍ



- **ﻛﺕﺑﮔﭘﮒﺎﮒﭨﻝﺏﭨﮔﺍ**: {params['temporary_impact_coef']:.6f}



- **ﮔﺍﺕﻛﺗﮒﺎﮒﭨﻝﺏﭨﮔﺍ**: {params['permanent_impact_coef']:.6f}







## ﻠ۹ﻟﺁﻝﭨﮔ



- **ﻟ؟ﻝﭨﻠRﺡﺎ**: {validation.train_r2:.4f}



- **ﮔﭖﻟﺁﻠRﺡﺎ**: {validation.test_r2:.4f}



- **ﻟ؟ﻝﭨﻠMAE**: {validation.train_mae:.6f}



- **ﮔﭖﻟﺁﻠMAE**: {validation.test_mae:.6f}



- **ﮔ۷۰ﮒﮔﮔ**: {'ﻗ?ﮔ? if validation.is_valid else 'ﻗ?ﮒ?}







## ﮒﭨﭦﻟ؟؟



"""



        



        if validation.is_valid:



            report += "- ﮔ۷۰ﮒﻠ۹ﻟﺁﻠﻟﺟ,ﮒﺁﻛﭨ۴ﻛﺛﺟﻝ۷\n"



report += "- ﮒﭨﭦﻟ؟؟ﮒ؟ﮔﻠﮔﺍﮔ۰ﮒ(ﮔﺁﮔﻛﺕﮔ؛?\n"



        else:



report += "- ﻗﺅﺕ ﮔ۷۰ﮒﻠ۹ﻟﺁﮔ۹ﻠﻟﺟ,ﻠﻟ۵ﻟﺍﮔﺑﮒﮔﺍﮔﮒ۱ﮒﮔﺍﮔ؟\n"



            report += "- ﮒﭨﭦﻟ؟؟ﮔ۲ﮔ۴ﮔﺍﮔ؟ﻟﺑ۷ﻠﮒﻝﺗﮒﺝﮒﺓ۴ﻝ۷\n"



        



        return report



```







### 4.2 ﮔ۰ﮒﮔﺍﮔ؟ﻟ۵ﮔﺎ







```yaml



market_impact_calibration:



  data_requirements:



min_samples: 1000  # ﮔﮒﺍﮔﺓﮔ؛ﮔﺍ



    date_range:  # ﮔﺍﮔ؟ﮔﭘﻠﺑﻟﮒﺑ



      start_date: "2023-01-01"



      end_date: "2024-12-31"



    



required_fields:  # ﮒﺟﻠﮒﮔ؟ﭖ



      - timestamp



      - symbol



      - order_size



      - average_volume



      - volatility



      - price_impact



      - market_cap



    



    data_sources:



      - name: "ﮒﮒﺎﻛﭦ۳ﮔﮔﺍﮔ؟"



        priority: 1



        fields: ["order_size", "average_volume", "volatility"]



      - name: "Level-2ﻟ۰ﮔﮔﺍﮔ؟"



        priority: 2



        fields: ["price_impact", "market_cap"]



  



  calibration_config:



method: "nonlinear_optimization"  # ﻝﭦﺟﮔ۶ﮒﮒﺛﮔﻠﻝﭦﺟﮔ۶ﻛﺙﮒ?    regularization_coef: 0.01  # ﮔ۲ﮒﮒﻝﺏﭨﮔ?    validation_split: 0.2  # ﻠ۹ﻟﺁﻠﮔﺁﻛﺝ?    cross_validation: true  # ﮔﺁﮒ۵ﻛﭦ۳ﮒﻠ۹ﻟﺁ



    



  quality_thresholds:



    min_r2: 0.5  # ﮔﮒﺍRﺡﺎ



    max_mae: 0.02  # ﮔﮒ۳۶MAE



    max_parameter_value: 1.0  # ﮒﮔﺍﮔﮒ۳۶ﮒ?    



  recalibration:



    enabled: true



frequency: "monthly"  # ﮔﺁﮔﻠﮔﺍﮔ۰ﮒ



    trigger_conditions:  # ﻟ۶۵ﮒﮔ۰ﻛﭨﭘ



      - performance_degradation: 0.2  # ﮔ۶ﻟﺛﻛﺕﻠ20%



      - data_drift: true  # ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨ



```







### 4.3 ﮔ۰ﮒﻠ۹ﻟﺁﮔﮒ







| ﻠ۹ﻟﺁﻝﭨﺑﮒﭦ۵ | ﻠ۹ﻟﺁﮔﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |



|---------|---------|---------|



| **ﮒﮔﺍﮒﻝﮔ?* | ﮒﮔﺍﮒ۷[0, 1]ﻟﮒﺑﮒ?| ﮒﮔﺍﻟﺝﺗﻝﮔ۲ﮔ?|



| **ﮔﮒﻛﺙﮒﭦ۵** | Rﺡﺎ ﻗ?0.5 | ﮔﺓﮔ؛ﮒ۳ﻠ۹ﻟﺁ?|



| **ﻠ۱ﮔﭖﮒﻝ۰؟ﮔ?* | MAE < 0.02 | ﮔ؟ﮒﺓ؟ﮒﮔ |



| **ﻝ۷ﺏﮒ؟ﮔ?* | ﮒﮔﺍﮔﺏ۱ﮒ۷ < 10% | ﮔﭨﮒ۷ﻝ۹ﮒ۲ﻠ۹ﻟﺁ |



| **ﻛﺕﮒ۰ﮒﻝﮔ?* | ﻛﺕﺑﮔﭘﮒﺎﮒﭨ > ﮔﺍﺕﻛﺗﮒﺎﮒﭨ | ﻝﻟ؟ﭦﻠ۹ﻟﺁ |







```---







## ﻭ ﻛﭦﻙﻠﮔﮒﺍﻛﺕﭨﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵







### 5.1 ﮔﺑﮔﺍﻟﺁﺑﮔ







ﮔ؛ﻟ۰۴ﮒﮔﮔ۰۲ﮒﺓﺎﻟ۰۴ﮒﻛﭦﻛﺕﻛﺕ۹ﮒﺟﻠ۰ﭨﮔﺗﻟﺟﻠ۰ﺗﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟?







1. **IMP-001**: ﮒ؟ﮔﺑﻝﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒﭘﻟ؟ﺝﻟ؟۰



   - ﮒﺙﮒﺕﺕﮒﺎﮔ؛۰ﻝﭨﮔ



- ﻝﭨﻛﺕﮒﺙﮒﺕﺕﮒ۳ﻝﮒ?   - ﻠﻟﺁﻝﻝ۴ﮒﮔ۶ﻟ۰ﮒ۷



   - ﮒﺓﻛﺛﮒﭦﻝ۷ﮒﭦﮔﺁ







2. **IMP-002**: ﮒ؟ﮒﻝRLﮔ۷۰ﮒﻟ؟ﻝﭨﻝﮔ۶ﮔﮔﻟ؟ﺝﻟ؟۰



- ﮔﺕﮒﺟﻝﮔ۶ﮔﮔﻛﺛﻝﺏﭨ



- ﻟ؟ﻝﭨﻝﮔ۶ﮒ?   - ﻟ؟ﻝﭨﻟﺟﻝ۷ﮒﺁﻟ۶ﮒ?   - ﮒﺙﮒﺕﺕﮔ۲ﮔﭖﮒﮒﻟ۵







3. **IMP-003**: ﻟﺁ۵ﻝﭨﻝﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮔ۰ﮒﮔﺗﮔ۰?   - ﮒﺕﮒﭦﮒﺎﮒﭨﮔ۷۰ﮒﮒﭦﻝ۰



- ﮔ۷۰ﮒﮔ۰ﮒﮔﺗﮔﺏ



- ﮔ۰ﮒﮔﺍﮔ؟ﻟ۵ﮔﺎ



- ﮔ۰ﮒﻠ۹ﻟﺁﮔﮒ







### 5.2 ﻛﺕﻛﺕﮔ۴ﻟ۰ﮒ?



1. **ﻝ،ﮒﺏﮔ۶ﻟ۰**: ﮒﺍﮔ؛ﻟ۰۴ﮒﮔﮔ۰۲ﻝﮒﮒ؟ﺗﻠﮔﮒﺍﻛﺕﭨﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵



2. **ﻛﭨ۲ﻝﮒ؟ﻝﺍ**: ﮔﻝ۶ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﮒ؟ﻝﺍﻛﺕﻛﺕ۹ﮔﺗﻟﺟﻠ۰?3. **ﮒﮒﮔﭖﻟﺁ**: ﻛﺕﭦﻛﺕﻛﺕ۹ﮔﺗﻟﺟﻠ۰ﺗﻝﺙﮒﮒﮒﮔﭖﻟﺁ



4. **ﻠﮔﮔﭖﻟﺁ**: ﻠ۹ﻟﺁﻛﺕﻛﺕ۹ﮔﺗﻟﺟﻠ۰ﺗﻛﺕﻝﺍﮔﻝﺏﭨﻝﭨﻝﻠﮔ?



```---







**ﻝﮔ؛**: v1.0 | **ﮔﺑﮔﺍ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ?