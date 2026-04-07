---
module_id: SECURITY
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: IMPL_DEV_SECURITY_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 系统实施与部署管理与优化维护
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
---


# 安全规范 (SECURITY.md)
> **核心职责**: 标准规范制定
> **职责边界**: 
> - ✅ 本文档负责：标准规范制定相关内容
> - ❌ 本文档不负责：其他模块内容


> 本文档定义了清风量化交易系统4.0的安全规范，包括敏感信息管理、权限控制、API密钥保护等安全相关的标准和最佳实践?

---

## 1. 敏感信息管理

### 1.1 敏感信息定义

以下信息被视为敏感信息，必须严格保护?

| 类别 | 示例 | 风险等级 |
|------|------|----------|
| 认证凭证 | API密钥、Token、密?| 🔴 极高 |
| 金融数据 | 交易账户、持仓信息、资?| 🔴 极高 |
| 个人隐私 | 身份证号、手机号、地址 | 🟠 ?|
| 配置凭证 | 数据库连接串、Redis密码 | 🔴 极高 |
| 策略敏感 | 策略参数、因子权?| 🟡 ?|

### 1.2 敏感信息保护原则

```
原则1: 最小暴?
  - 只在必要时提供敏感信?
  - 敏感信息不应出现在代码仓库中
  - 敏感信息不应出现在日志中

原则2: 分级存储
  - 生产环境: 专用密钥管理系统 (AWS KMS / HashiCorp Vault)
  - 开发环? 本地 .env 文件 (不提交到版本控制)
  - 测试环境: 脱敏后的测试数据

原则3: 审计追溯
  - 所有敏感信息访问必须有日志记录
  - 日志中不记录敏感信息的实际?
  - 支持审计查询
```

---

## 2. API密钥管理规范

### 2.1 密钥分类

| 密钥类型 | 用?| 安全要求 |
|----------|------|----------|
| `DATA_API_KEY` | 行情数据API | 每日使用量限?|
| `TRADE_API_KEY` | 交易API (模拟/实盘) | 最高安全等?|
| `DATABASE_KEY` | 数据库连?| 定期轮换 |
| `ENCRYPTION_KEY` | 数据加密密钥 | 独立存储 |

### 2.2 密钥配置规范

```yaml
# config/secrets.yaml.example - 密钥配置示例 (不提交到版本控制)

data_sources:
  ths:
    api_key: "${THS_API_KEY}"
    api_secret: "${THS_API_SECRET}"
  tushare:
    token: "${TUSHARE_TOKEN}"

trading:
  broker:
    broker_id: "${BROKER_ID}"
    account: "${BROKER_ACCOUNT}"
    password: "${BROKER_PASSWORD}"
    auth_code: "${BROKER_AUTH_CODE}"
```

### 2.3 环境变量加载

```python
# src/core/config/secret_manager.py

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class SecretConfig:
    data_api_key: Optional[str] = None
    trade_api_key: Optional[str] = None
    database_key: Optional[str] = None

class SecretManager:
    """敏感信息管理?""

    REQUIRED_ENV_VARS = [
        "THS_API_KEY",
        "TUSHARE_TOKEN",
    ]

    def __init__(self):
        self._secrets: dict = {}
        self._load_env_secrets()

    def _load_env_secrets(self):
        for var_name in self.REQUIRED_ENV_VARS:
            value = os.environ.get(var_name)
            if value:
                self._secrets[var_name] = value

    def get_secret(self, key: str) -> Optional[str]:
        return self._secrets.get(key)

    def validate(self) -> bool:
        missing = [v for v in self.REQUIRED_ENV_VARS if v not in self._secrets]
        if missing:
            raise SecurityError(f"缺少必需的環境變? {', '.join(missing)}")
        return True

class SecurityError(Exception):
    """安全相关异常"""
    pass
```

### 2.4 禁止的行?

```markdown
?禁止在代码中硬编码密?
   BAD:  api_key = "ak_live_xxxxx123456"

?禁止在注释中记录密钥
   BAD:  # API Key: ak_live_xxxxx123456

?禁止在日志中输出密钥
   BAD:  logger.info(f"Using API key: {api_key}")

?禁止将密钥提交到版本控制
   BAD:  .git commit -m "Add API key" config/secrets.yaml

?禁止在错误信息中暴露密钥
   BAD:  raise ValueError(f"Invalid API key: {api_key}")
```

---

## 3. 权限管理规范

### 3.1 用户角色定义

| 角色 | 权限范围 | 典型用户 |
|------|----------|----------|
| `ADMIN` | 系统配置、用户管理、回测执?| 系统管理?|
| `TRADER` | 策略执行、持仓查询、资金查?| 交易?|
| `RESEARCHER` | 因子研究、回测分析、策略开?| 研究?|
| `VIEWER` | 只读数据访问 | 观察?|

### 3.2 数据访问控制

```python
# src/core/security/permission.py

from enum import Enum
from functools import wraps
from typing import Callable, List

class Permission(Enum):
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    STRATEGY_EXECUTE = "strategy:execute"
    STRATEGY_EDIT = "strategy:edit"
    BACKTEST_RUN = "backtest:run"
    CONFIG_EDIT = "config:edit"
    SYSTEM_ADMIN = "system:admin"

ROLE_PERMISSIONS = {
    "ADMIN": [
        Permission.DATA_READ, Permission.DATA_WRITE,
        Permission.STRATEGY_EXECUTE, Permission.STRATEGY_EDIT,
        Permission.BACKTEST_RUN, Permission.CONFIG_EDIT,
        Permission.SYSTEM_ADMIN
    ],
    "TRADER": [
        Permission.DATA_READ,
        Permission.STRATEGY_EXECUTE,
        Permission.BACKTEST_RUN,
    ],
    "RESEARCHER": [
        Permission.DATA_READ,
        Permission.STRATEGY_EDIT,
        Permission.BACKTEST_RUN,
    ],
    "VIEWER": [
        Permission.DATA_READ,
    ],
}

def require_permissions(*permissions: Permission):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(user_role: str, *args, **kwargs):
            if user_role not in ROLE_PERMISSIONS:
                raise PermissionError(f"未知角色: {user_role}")

            user_permissions = ROLE_PERMISSIONS[user_role]
            for perm in permissions:
                if perm not in user_permissions:
                    raise PermissionError(
                        f"角色 {user_role} 缺少权限: {perm.value}"
                    )
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## 4. 日志安全规范

### 4.1 日志脱敏规则

```python
# src/core/security/log_sanitizer.py

import re
from typing import Any, Dict

class LogSanitizer:
    """日志脱敏处理?""

    SENSITIVE_PATTERNS = {
        "api_key": re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_/-]+)',
                             re.IGNORECASE),
        "password": re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^\s"\']+)',
                              re.IGNORECASE),
        "token": re.compile(r'(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_/-]+)',
                           re.IGNORECASE),
        "account": re.compile(r'(account["\']?\s*[:=]\s*["\']?)([^\s"\']+)',
                              re.IGNORECASE),
    }

    @classmethod
    def sanitize(cls, message: str) -> str:
        """对日志消息进行脱敏处?""
        result = message
        for name, pattern in cls.SENSITIVE_PATTERNS.items():
            result = pattern.sub(r'\1[REDACTED]', result)
        return result

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """对字典数据进行脱敏处?""
        result = {}
        for key, value in data.items():
            if cls._is_sensitive_key(key):
                result[key] = "[REDACTED]"
            elif isinstance(value, dict):
                result[key] = cls.sanitize_dict(value)
            else:
                result[key] = value
        return result

    @classmethod
    def _is_sensitive_key(cls, key: str) -> bool:
        sensitive_keywords = ["key", "password", "secret", "token", "auth"]
        return any(kw in key.lower() for kw in sensitive_keywords)
```

### 4.2 日志级别规范

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| `DEBUG` | 开发调试信?| 函数入参、中间变?|
| `INFO` | 正常业务流程 | 策略信号、执行结?|
| `WARNING` | 异常但可处理 | 数据缺失、配置警?|
| `ERROR` | 错误需要处?| API失败、计算异?|
| `CRITICAL` | 系统级严重问?| 资金风险、认证失?|

---

## 5. 文件系统安全

### 5.1 目录权限控制

```markdown
## 目录权限矩阵

| 目录 | 所有?| 所属组 | 权限 | 说明 |
|------|--------|--------|------|------|
| src/ | user | quant | 755 | 代码目录 |
| config/ | user | quant | 750 | 配置目录 |
| data/ | user | quant | 750 | 数据目录 |
| logs/ | user | quant | 750 | 日志目录 |
| temp/ | user | quant | 777 | 临时目录 |
```

### 5.2 禁止的可执行文件扩展?

```
禁止上传或执行以下类型的文件:

.exe  .bat  .cmd  .sh  .ps1  .vbs  .js  .jar  .dll  .so

例外: 已在版本控制中明确管理的可执行脚?
```

---

## 6. 网络安全规范

### 6.1 API调用安全

```python
# src/core/security/api_security.py

import time
import hashlib
from typing import Optional
from dataclasses import dataclass

@dataclass
class APIRateLimit:
    """API调用频率限制"""
    max_calls: int
    time_window: int  # ?

    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self._calls: list = []

    def is_allowed(self) -> bool:
        now = time.time()
        self._calls = [t for t in self._calls if now - t < self.time_window]
        return len(self._calls) < self.max_calls

    def record_call(self):
        self._calls.append(time.time())

class APISecurity:
    """API安全处理?""

    RATE_LIMITS = {
        "ths": APIRateLimit(max_calls=100, time_window=60),
        "tushare": APIRateLimit(max_calls=200, time_window=60),
    }

    @classmethod
    def check_rate_limit(cls, source: str) -> bool:
        if source not in cls.RATE_LIMITS:
            return True
        return cls.RATE_LIMITS[source].is_allowed()

    @classmethod
    def sign_request(cls, params: dict, secret: str) -> str:
        """生成请求签名"""
        sorted_params = sorted(params.items())
        sign_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        sign_str += secret
        return hashlib.md5(sign_str.encode()).hexdigest()
```

---

## 7. 安全审计

### 7.1 审计日志格式

```yaml
# 审计日志格式 (logs/audit/audit_YYYYMMDD.log)

audit_log:
  format: "[{timestamp}] [{level}] [{user_id}] [{action}] [{resource}] [{result}] [{ip}]"
  example: "[2026-03-28T10:15:30] [INFO] [user_001] [LOGIN] [system] [SUCCESS] [192.168.1.100]"
  example: "[2026-03-28T10:16:45] [WARN] [user_002] [TRADE_EXECUTE] [AAPL] [FAILED] [192.168.1.101]"

敏感操作审计:
  - 用户登录/登出
  - 策略执行/修改
  - 配置变更
  - 数据导出
  - 权限变更
```

### 7.2 安全检查清?

```markdown
## 上线前安全检?

?所有API密钥已移至环境变量或密钥管理系统
?敏感信息未出现在代码仓库?
?日志脱敏规则已启?
?权限控制已正确配?
?审计日志已启?
?频率限制已配?
?错误信息不暴露敏感信?
?目录权限已正确设?
?无禁止的可执行文?
?依赖项无已知安全漏洞
```

---

## 8. 依赖安全

### 8.1 依赖审计

```bash
# 定期执行依赖安全检?

# Python 依赖审计
pip audit

# 或使?safety
safety check

# 检查过期依?
pip list --outdated
```

### 8.2 requirements.txt 格式

```text
# requirements.txt - 依赖清单
# 安装命令: pip install -r requirements.txt

# 核心依赖 (锁定版本)
pandas>=1.5.0
numpy>=1.23.0
scipy>=1.9.0
scikit-learn>=1.2.0

# 数据?(锁定版本)
efinance>=0.5.0
akshare>=1.12.0
tushare>=1.3.0

# 安全相关
cryptography>=41.0.0
python-dotenv>=1.0.0
```

---

## 附录: 相关文档

| 文档 | 说明 |
|------|------|
| `ERROR_HANDLING.md` | 错误处理规范 |
| `LOGGING_STANDARD.md` | 日志记录规范 |
| `CONFIG_STANDARD.md` | 配置文件标准 |
| `CODE_QUALITY.md` | 代码质量标准 |

---

**版本**: v1.0
**最后更?*: 2026-03-28
**维护?*: Security Team
