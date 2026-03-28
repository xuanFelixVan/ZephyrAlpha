# ERROR_HANDLING.md - 错误处理规范

> **版本**：v4.0
> **更新日期**：2026-03-28
> **状态**：已制定

---

## 1. 异常分类体系

### 1.1 异常层次结构

```python
# 基础异常类
class QuantSystemException(Exception):
    """量化系统基础异常"""
    def __init__(self, message: str, code: int = None, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

# 数据层异常
class DataException(QuantSystemException):
    """数据相关异常"""
    pass

# 因子层异常
class FactorException(QuantSystemException):
    """因子相关异常"""
    pass

# 策略层异常
class StrategyException(QuantSystemException):
    """策略相关异常"""
    pass

# 风险层异常
class RiskException(QuantSystemException):
    """风险相关异常"""
    pass

# 执行层异常
class ExecutionException(QuantSystemException):
    """执行相关异常"""
    pass
```

### 1.2 异常错误码定义

| 错误码 | 异常类型 | 说明 |
|--------|----------|------|
| 1000-1999 | DataException | 数据相关错误 |
| 2000-2999 | FactorException | 因子相关错误 |
| 3000-3999 | StrategyException | 策略相关错误 |
| 4000-4999 | RiskException | 风险相关错误 |
| 5000-5999 | ExecutionException | 执行相关错误 |

---

## 2. 异常处理模式

### 2.1 标准异常处理流程

```python
def process_data(data):
    """标准异常处理流程"""
    try:
        # 1. 验证输入
        validate_input(data)

        # 2. 执行处理
        result = do_processing(data)

        # 3. 验证输出
        validate_output(result)

        return Result(success=True, data=result)

    except ValidationError as e:
        # 输入验证失败 - 记录日志，返回失败
        logger.warning(f"Validation failed: {e}")
        return Result(success=False, error=str(e), code=1001)

    except ProcessingError as e:
        # 处理错误 - 记录日志，尝试恢复
        logger.error(f"Processing error: {e}")
        return retry_processing(data)

    except CriticalError as e:
        # 严重错误 - 记录日志，告警
        logger.critical(f"Critical error: {e}")
        send_alert("CRITICAL", str(e))
        raise

    except Exception as e:
        # 未知错误 - 记录日志，返回通用错误
        logger.exception(f"Unknown error: {e}")
        return Result(success=False, error="Unknown error", code=9999)
```

### 2.2 重试机制

```python
def retry(max_attempts: int = 3, backoff: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except RecoverableError as e:
                    if attempt < max_attempts - 1:
                        wait_time = backoff * (2 ** attempt)
                        logger.warning(f"Retry {attempt + 1}/{max_attempts} after {wait_time}s")
                        time.sleep(wait_time)
                    else:
                        raise MaxRetriesExceeded(f"Max retries exceeded: {e}")
            return None
        return wrapper
    return decorator
```

### 2.3 熔断机制

```python
class CircuitBreaker:
    """熔断器"""
    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError("Circuit is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.threshold:
            self.state = "OPEN"
```

---

## 3. 日志规范

### 3.1 日志级别使用规范

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| DEBUG | 开发调试 | `logger.debug(f"Processing {len(data)} records")` |
| INFO | 正常流程 | `logger.info("Data update completed")` |
| WARNING | 异常但可处理 | `logger.warning("Using fallback data source")` |
| ERROR | 处理失败 | `logger.error(f"Failed to fetch data: {e}")` |
| CRITICAL | 严重错误需告警 | `logger.critical("Risk limit exceeded!")` |

### 3.2 日志格式规范

```python
# ✅ 标准日志格式
logger.info(f"[{timestamp}] [{module}] [{level}] {message} | context={context}")

# 示例
logger.info("[2026-03-28 15:30:00] [DataCollector] [INFO] Daily data update completed | records=3500, duration=2.3s")
```

### 3.3 日志记录位置

```python
# 每个模块应记录以下日志：

class DataCollector:
    def __init__(self):
        self.logger = Logger("DataCollector")

    def collect(self, data_type, symbols):
        # 入口日志
        self.logger.info(f"Starting collection | type={data_type}, symbols={len(symbols)}")

        try:
            result = self._fetch_data(data_type, symbols)

            # 成功日志
            self.logger.info(f"Collection completed | records={len(result)}, duration={elapsed}")

            return Result(success=True, data=result)

        except Exception as e:
            # 错误日志
            self.logger.error(f"Collection failed | error={str(e)}", exc_info=True)
            return Result(success=False, error=str(e))
```

---

## 4. 错误响应格式

### 4.1 统一错误响应

```python
class ErrorResponse:
    def __init__(self, code: int, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp
            }
        }
```

### 4.2 错误码定义

```python
ERROR_CODES = {
    # 数据层 (1000-1999)
    1001: "DATA_FETCH_FAILED",
    1002: "DATA_VALIDATION_FAILED",
    1003: "DATA_STORAGE_FAILED",

    # 因子层 (2000-2999)
    2001: "FACTOR_NOT_FOUND",
    2002: "FACTOR_CALCULATION_FAILED",
    2003: "FACTOR_VALIDATION_FAILED",

    # 策略层 (3000-3999)
    3001: "STRATEGY_NOT_FOUND",
    3002: "STRATEGY_SIGNAL_FAILED",
    3003: "STRATEGY_PARAM_INVALID",

    # 风险层 (4000-4999)
    4001: "RISK_LIMIT_EXCEEDED",
    4002: "RISK_VALIDATION_FAILED",
    4003: "POSITION_SIZE_ERROR",

    # 执行层 (5000-5999)
    5001: "ORDER_SUBMIT_FAILED",
    5002: "ORDER_CANCEL_FAILED",
    5003: "EXECUTION_TIMEOUT"
}
```

---

## 5. 告警机制

### 5.1 告警级别

| 级别 | 触发条件 | 通知方式 |
|------|----------|----------|
| INFO | 正常事件 | 仅记录 |
| WARNING | 异常但可处理 | 日志+控制台 |
| ERROR | 处理失败 | 日志+邮件 |
| CRITICAL | 严重错误 | 日志+邮件+短信 |

### 5.2 告警触发规则

```python
ALERT_RULES = {
    "risk_limit_exceeded": {
        "level": "CRITICAL",
        "channels": ["log", "email", "sms"],
        "throttle": 300  # 5分钟内不重复告警
    },
    "data_update_failed": {
        "level": "ERROR",
        "channels": ["log", "email"],
        "throttle": 600
    },
    "strategy_signal_error": {
        "level": "WARNING",
        "channels": ["log"],
        "throttle": 0
    }
}
```

---

## 6. 相关文档

| 文档 | 说明 |
|------|------|
| [CODE_QUALITY.md](./CODE_QUALITY.md) | 代码质量标准 |
| [SECURITY.md](./SECURITY.md) | 安全规范 |

---

*最后更新：2026-03-28*
