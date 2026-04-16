---
module_id: 05_IMPLEMENTATION_02_DEVELOPMENT_LOGGING_STANDARD
layer: layer_05
version: 1.0.0
status: Active
responsibility:
  - Logging Standard相关业务
created_date: 2026-04-01
last_updated: 2026-04-07
owner: 首席文档架构?
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---

## 1. 日志级别定义



### 1.1 级别规范



| 级别 | 数据| 使用场景 | 示例 |

|------|------|----------|------|

| `CRITICAL` | 50 | 系统级严重问?| 资金风险、认证失败、数据丢?|

| `ERROR` | 40 | 错误需要处?| API调用失败、数据解析异?|

| `WARNING` | 30 | 异常但可处理 | 数据缺失、配置使用默认?|

| `INFO` | 20 | 正常业务流程 | 策略启动、信号生成、订单执?|

| `DEBUG` | 10 | 开发调试信?| 函数入参、中间变量、循环次?|



### 1.2 级别使用原则



```python

# ?正确示例



logger.critical(f"账户 {account_id} 亏损超过阈?{threshold}")

logger.error(f"THS API 调用失败: {error_code} - {message}")

logger.warning(f"数据?{source} 返回空数据，使用缓存")

logger.info(f"策略 {strategy_id} ?{stock_code} 生成买入信号")

logger.debug(f"因子计算参数: window={window}, threshold={threshold}")



# ?错误示例



logger.info(f"用户 {user_id} 登录成功")  # 过于琐碎

logger.error(f"出错?)  # 信息不足

logger.debug(f"循环?{i} ?)  # 生产环境不应输出

```



```
```---
```



## 2. 日志格式规范



### 2.1 标准格式



```python

# 日志格式定义

LOG_FORMAT = "[{timestamp}] [{level}] [{module}] [{function}:{line}] [{context}] {message}"

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"



# 输出示例

[2026-03-28 10:15:30] [INFO] [backtest_engine] [run_strategy:156] [strategy=S001] 策略执行开?

[2026-03-28 10:15:31] [ERROR] [data_fetcher] [fetch_ohlcv:89] [stock=000001] 数据获取失败: 超时

[2026-03-28 10:15:32] [WARNING] [risk_manager] [check_position:203] [position=0.95] 仓位超过阈?

```



### 2.2 上下文字?



```python

# 日志上下文字段规?

CONTEXT_FIELDS = {

    "strategy_id": "策略唯一标识",

    "stock_code": "股票代码",

    "signal_type": "信号类型 (buy/sell/hold)",

    "order_id": "订单ID",

    "account_id": "账户ID",

    "error_code": "错误代码",

    "duration_ms": "执行耗时(毫秒)",

}



# 上下文使用示?

logger.info(

    f"生成交易信号",

    extra={"strategy_id": "S001", "stock_code": "600519", "signal_type": "buy"}

)

```



```
```---
```



## 3. 日志输出规范



### 3.1 输出目标配置



```yaml

# config/logging.yaml



logging:

  version: 1

  disable_existing_loggers: false



  formatters:

    standard:

      format: "[{timestamp}] [{level}] [{module}] [{function}:{line}] {message}"

      datefmt: "%Y-%m-%d %H:%M:%S"



    json:

      class: pythonjsonlogger.jsonlogger.JsonFormatter

      format: "%(timestamp)s %(level)s %(name)s %(message)s"



  handlers:

    console:

      class: logging.StreamHandler

      level: INFO

      formatter: standard

      stream: ext://sys.stdout



    file:

      class: logging.handlers.RotatingFileHandler

      level: DEBUG

      formatter: standard

      filename: logs/app.log

      maxBytes: 10485760  # 10MB

      backupCount: 5



    error_file:

      class: logging.handlers.RotatingFileHandler

      level: ERROR

      formatter: standard

      filename: logs/error.log

      maxBytes: 10485760

      backupCount: 10



    audit_file:

      class: logging.handlers.RotatingFileHandler

      level: INFO

      formatter: standard

      filename: logs/audit/audit.log

      maxBytes: 10485760

      backupCount: 20



  loggers:

    root:

      level: INFO

      handlers: [console, file, error_file]



    audit:

      level: INFO

      handlers: [audit_file]

      propagate: false



    backtest:

      level: DEBUG

      handlers: [file]

      propagate: false

```



### 3.2 日志文件分类



```markdown

## 日志文件分类



| 文件 | 内容 | 级别 | 保留策略 |

|------|------|------|----------|

| `logs/app.log` | 应用主日?| INFO+ | 5个备?|

| `logs/error.log` | 错误日志 | ERROR+ | 10个备?|

| `logs/audit/audit.log` | 审计日志 | INFO+ | 20个备?|

| `logs/backtest/backtest_{date}.log` | 回测日志 | DEBUG | 30?|

| `logs/trade/trade_{date}.log` | 交易日志 | INFO+ | 90?|

| `logs/data/data_{date}.log` | 数据获取日志 | WARNING+ | 14?|

```



```
```---
```



## 4. 日志命名规范



### 4.1 模块命名



```python

# 日志命名规范

logger = logging.getLogger("quant_system.backtest.engine")

logger = logging.getLogger("quant_system.risk.manager")

logger = logging.getLogger("quant_system.data.fetcher")

logger = logging.getLogger("quant_system.trade.executor")



# 层级结构

# quant_system.{layer}.{module}.{submodule}

# - layer: backtest / risk / data / trade / system

# - module: engine / manager / fetcher / executor

# - submodule: (可? 具体功能

```



### 4.2 日志文件?



```bash

# 日志文件名规?

app_{YYYYMMDD}.log              # 应用日志

error_{YYYYMMDD}.log            # 错误日志

audit_{YYYYMMDD}.log            # 审计日志

backtest_{strategy_id}_{YYYYMMDD}_{HHMMSS}.log   # 回测日志

trade_{account_id}_{YYYYMMDD}.log                  # 交易日志

data_{source}_{YYYYMMDD}.log    # 数据获取日志

```



```
```---
```



## 5. 敏感信息保护



### 5.1 日志脱敏规则



```python

# src/core/logging/sanitizer.py



import re

from typing import Any, Dict



class LogSanitizer:

    """日志脱敏处理?""



    SENSITIVE_PATTERNS = {

        "api_key": (r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_/-]+)',

                   r'api_key=[REDACTED]'),

        "password": (r'password["\']?\s*[:=]\s*["\']?([^\s"\']+)',

                     r'password=[REDACTED]'),

        "token": (r'token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_/-]+)',

                  r'token=[REDACTED]'),

        "account": (r'account["\']?\s*[:=]\s*["\']?([^\s"\']+)',

                   r'account=[REDACTED]'),

        "stock_code": (r'stock_code=([0-9]{{6}})',

                      r'stock_code=[MASKED]'),

    }



    @classmethod

    def sanitize(cls, message: str) -> str:

        result = message

        for name, (pattern, replacement) in cls.SENSITIVE_PATTERNS.items():

            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result



    @classmethod

    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:

        result = {}

        sensitive_keys = {"api_key", "password", "token", "secret", "account"}

        for key, value in data.items():

            if key.lower() in sensitive_keys:

                result[key] = "[REDACTED]"

            elif isinstance(value, dict):

                result[key] = cls.sanitize_dict(value)

            else:

                result[key] = value

        return result

```



### 5.2 禁止记录的敏感信?



```markdown

## 禁止记录的敏感信?



?API密钥和Token

?交易密码和资金密?

?身份证号、手机号

?银行卡号

?策略参数中的核心算法

?真实资金账户信息



?可以记录

?操作类型和结?

?股票代码和交易方?

?时间戳和耗时

?脱敏后的统计信息

```



```
```---
```



## 6. 日志记录规范



### 6.1 函数日志规范



```python

# 函数入口/出口日志



def fetch_stock_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:

    logger.info(

        f"开始获取股票数?,

        extra={

            "stock_code": stock_code,

            "start_date": start_date,

            "end_date": end_date,

            "function": "fetch_stock_data"

        }

    )



    try:

        result = _do_fetch(stock_code, start_date, end_date)

        logger.info(

            f"数据获取成功",

            extra={

                "stock_code": stock_code,

                "record_count": len(result),

                "duration_ms": elapsed_ms()

            }

        )

        return result



    except DataSourceError as e:

        logger.error(

            f"数据源错?,

            extra={

                "stock_code": stock_code,

                "error_code": e.code,

                "error_message": e.message

            }

        )

        raise



    except Exception as e:

        logger.critical(

            f"未知错误",

            extra={

                "stock_code": stock_code,

                "exception_type": type(e).__name__

            }

        )

        raise

```



### 6.2 交易日志规范



```python

# 交易操作日志格式



TRADE_LOG_FORMAT = "[{timestamp}] [{level}] [{order_id}] [{account_id}] [{stock_code}] [{direction}] [{volume}] @{price}] [{status}] [{message}]"



# 示例

[2026-03-28 09:30:00] [INFO] [ORD001] [ACC001] [600519] [BUY] [100] @1800.00 [FILLED] [订单成交]

[2026-03-28 09:31:00] [WARNING] [ORD002] [ACC001] [000001] [SELL] [50] @15.50 [PARTIAL] [部分成交]

[2026-03-28 09:35:00] [ERROR] [ORD003] [ACC001] [601318] [BUY] [1000] @50.00 [REJECTED] [余额不足]

```



```
```---
```



## 7. 日志监控告警



### 7.1 告警规则



```yaml

# config/alerts.yaml



alert_rules:

  - name: "连续错误告警"

    condition: "error_count > 10 in 5 minutes"

    severity: HIGH

    channels: [email, sms]



  - name: "策略执行失败"

    condition: "ERROR in backtest.log and 'strategy_failed'"

    severity: HIGH

    channels: [email]



  - name: "数据源超?

    condition: "WARNING in data.log and 'timeout'"

    severity: MEDIUM

    channels: [slack]



  - name: "系统资源告警"

    condition: "disk_usage > 90% or memory_usage > 85%"

    severity: CRITICAL

    channels: [email, sms]

```



```
```---
```



## 8. 日志分析规范



### 8.1 日志查询示例



```bash

# 查询特定策略的错误日?

grep "S001" logs/error.log | grep ERROR



# 查询某时间范围的日志

grep "2026-03-28 10:" logs/app.log



# 统计错误类型分布

grep ERROR logs/error.log | awk '{print $5}' | sort | uniq -c



# 查询交易流水

grep "TRADE" logs/trade_20260328.log | grep FILLED

```



```
```---
```



## 附录: 相关文档



| 文档 | 说明 |

|------|------|

| `ERROR_HANDLING.md` | 错误处理规范 |

| `SECURITY.md` | 安全规范 |

| `CODE_QUALITY.md` | 代码质量标准 |



```
```---
```



**版本**: v1.0

**最后更?*: 2026-03-28
