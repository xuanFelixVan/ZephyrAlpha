---
module_id: ENVIRONMENT_CONFIG_GUIDE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 运维团队
standard_type: 专业量化机构指南
applicable_scope: ZephyrAlpha环境配置
responsibility:
  - ENVIRONMENT_CONFIG操作指南
---

# ZephyrAlpha环境配置指南

## 📋 文档概要

**文档职责**: 提供ZephyrAlpha系统的环境配置方法和最佳实践
**适用范围**: 开发环境、测试环境、生产环境
**前置条件**: 已完成系统架构设计

---

## 🎯 配置目标

### 配置原则

1. **环境隔离**: 不同环境配置相互隔离
2. **安全可控**: 敏感信息加密存储
3. **版本可控**: 配置文件纳入版本管理
4. **易于维护**: 配置结构清晰、易于理解

---

### 环境类型

| 环境类型 | 用途 | 配置特点 |
|---------|------|---------|
| **开发环境** | 本地开发和调试 | 宽松配置、详细日志 |
| **测试环境** | 集成测试和性能测试 | 接近生产配置 |
| **预生产环境** | 最终验证 | 与生产环境一致 |
| **生产环境** | 正式运行 | 严格配置、精简日志 |

---

## 📁 配置文件结构

### 1. 目录结构

```
config/
├── settings.yaml              # 主配置文件
├── environments/              # 环境配置
│   ├── development.yaml       # 开发环境
│   ├── testing.yaml           # 测试环境
│   ├── staging.yaml           # 预生产环境
│   └── production.yaml        # 生产环境
├── secrets/                   # 敏感配置（不纳入版本控制）
│   ├── database.yaml          # 数据库密码
│   ├── redis.yaml             # Redis密码
│   └── api_keys.yaml          # API密钥
└── logging/                   # 日志配置
    ├── development.yaml       # 开发日志
    └── production.yaml        # 生产日志
```

---

## 🔧 主配置文件

### settings.yaml

```yaml
# 应用配置
app:
  name: ZephyrAlpha
  version: 1.0.0
  environment: ${ZEPHYR_ENV:development}
  debug: false
  
# 服务器配置
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  timeout: 30
  
# 数据库配置
database:
  host: ${DB_HOST:localhost}
  port: ${DB_PORT:5432}
  name: ${DB_NAME:zephyr_alpha}
  user: ${DB_USER:zephyr_user}
  password: ${DB_PASSWORD}
  pool_size: 20
  max_overflow: 10
  
# Redis配置
redis:
  host: ${REDIS_HOST:localhost}
  port: ${REDIS_PORT:6379}
  db: ${REDIS_DB:0}
  password: ${REDIS_PASSWORD}
  
# 日志配置
logging:
  level: ${LOG_LEVEL:INFO}
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/app.log
  max_bytes: 10485760  # 10MB
  backup_count: 5
  
# 监控配置
monitoring:
  enabled: true
  metrics_port: 9090
  health_check_interval: 30
  
# 安全配置
security:
  secret_key: ${SECRET_KEY}
  token_expiry: 3600
  cors_origins:
    - https://zephyr-alpha.com
    - https://app.zephyr-alpha.com
```

---

## 🌍 环境配置

### 1. 开发环境 (development.yaml)

```yaml
# 开发环境配置
app:
  debug: true
  
database:
  host: localhost
  port: 5432
  name: zephyr_alpha_dev
  pool_size: 5
  
redis:
  host: localhost
  port: 6379
  db: 0
  
logging:
  level: DEBUG
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d"
  
monitoring:
  enabled: false
  
security:
  secret_key: dev-secret-key-change-in-production
  token_expiry: 86400  # 24小时
  cors_origins:
    - http://localhost:3000
    - http://localhost:8080
```

---

### 2. 测试环境 (testing.yaml)

```yaml
# 测试环境配置
app:
  debug: false
  
database:
  host: test-db.zephyr-alpha.com
  port: 5432
  name: zephyr_alpha_test
  pool_size: 10
  
redis:
  host: test-redis.zephyr-alpha.com
  port: 6379
  db: 1
  
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
monitoring:
  enabled: true
  metrics_port: 9090
  
security:
  secret_key: ${SECRET_KEY}
  token_expiry: 3600
  cors_origins:
    - https://test.zephyr-alpha.com
```

---

### 3. 生产环境 (production.yaml)

```yaml
# 生产环境配置
app:
  debug: false
  
database:
  host: ${DB_HOST}
  port: 5432
  name: zephyr_alpha
  pool_size: 20
  max_overflow: 10
  ssl_mode: require
  
redis:
  host: ${REDIS_HOST}
  port: 6379
  db: 0
  ssl: true
  
logging:
  level: WARNING
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: /var/log/zephyr/app.log
  max_bytes: 104857600  # 100MB
  backup_count: 10
  
monitoring:
  enabled: true
  metrics_port: 9090
  health_check_interval: 10
  
security:
  secret_key: ${SECRET_KEY}
  token_expiry: 3600
  cors_origins:
    - https://zephyr-alpha.com
    - https://app.zephyr-alpha.com
  rate_limit:
    enabled: true
    requests_per_minute: 100
```

---

## 🔐 敏感配置管理

### 1. 环境变量方式

```bash
# .env文件（不纳入版本控制）
ZEPHYR_ENV=production
DB_HOST=prod-db.zephyr-alpha.com
DB_PORT=5432
DB_NAME=zephyr_alpha
DB_USER=zephyr_user
DB_PASSWORD=secure_password_here
REDIS_HOST=prod-redis.zephyr-alpha.com
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_here
SECRET_KEY=very_secure_secret_key_here
```

---

### 2. 密钥管理服务

```yaml
# 使用HashiCorp Vault
vault:
  enabled: true
  url: https://vault.zephyr-alpha.com
  path: secret/zephyr
  
# 使用AWS Secrets Manager
aws_secrets:
  enabled: true
  region: us-east-1
  secret_name: zephyr/production
```

---

## 📊 日志配置

### 1. 开发日志 (logging/development.yaml)

```yaml
version: 1
disable_existing_loggers: false

formatters:
  detailed:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d"
    datefmt: "%Y-%m-%d %H:%M:%S"

handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: detailed
    stream: ext://sys.stdout
    
  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/app.log
    maxBytes: 10485760
    backupCount: 5

loggers:
  zephyr:
    level: DEBUG
    handlers: [console, file]
    propagate: false
    
  sqlalchemy:
    level: INFO
    handlers: [console]
    propagate: false
```

---

### 2. 生产日志 (logging/production.yaml)

```yaml
version: 1
disable_existing_loggers: false

formatters:
  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter
    format: "%(asctime)s %(name)s %(levelname)s %(message)s"

handlers:
  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: json
    filename: /var/log/zephyr/app.log
    maxBytes: 104857600
    backupCount: 10
    
  syslog:
    class: logging.handlers.SysLogHandler
    level: WARNING
    formatter: json
    address: /dev/log

loggers:
  zephyr:
    level: INFO
    handlers: [file, syslog]
    propagate: false
    
  sqlalchemy:
    level: WARNING
    handlers: [file]
    propagate: false
```

---

## 🚀 配置加载

### 1. 配置加载代码

```python
# config/loader.py
import os
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.environment = os.getenv("ZEPHYR_ENV", "development")
        
    def load_config(self) -> Dict[str, Any]:
        # 加载主配置
        with open(self.config_dir / "settings.yaml") as f:
            config = yaml.safe_load(f)
        
        # 加载环境配置
        env_config_path = self.config_dir / "environments" / f"{self.environment}.yaml"
        if env_config_path.exists():
            with open(env_config_path) as f:
                env_config = yaml.safe_load(f)
                config = self._deep_merge(config, env_config)
        
        # 替换环境变量
        config = self._replace_env_vars(config)
        
        return config
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _replace_env_vars(self, config: Dict) -> Dict:
        # 递归替换环境变量
        # 实现略
        return config
```

---

### 2. 使用配置

```python
# app/main.py
from config.loader import ConfigLoader

# 加载配置
config_loader = ConfigLoader()
config = config_loader.load_config()

# 使用配置
app_name = config["app"]["name"]
db_host = config["database"]["host"]
log_level = config["logging"]["level"]
```

---

## ✅ 配置验证

### 1. 配置验证脚本

```python
# scripts/validate_config.py
import yaml
from pathlib import Path

def validate_config():
    config_dir = Path("config")
    
    # 检查必需文件
    required_files = [
        "settings.yaml",
        "environments/development.yaml",
        "environments/production.yaml"
    ]
    
    for file in required_files:
        if not (config_dir / file).exists():
            print(f"❌ 缺少配置文件: {file}")
            return False
    
    # 验证配置格式
    try:
        with open(config_dir / "settings.yaml") as f:
            config = yaml.safe_load(f)
        
        # 检查必需配置项
        required_keys = ["app", "database", "redis", "logging"]
        for key in required_keys:
            if key not in config:
                print(f"❌ 缺少配置项: {key}")
                return False
        
        print("✅ 配置验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

if __name__ == "__main__":
    validate_config()
```

---

## 📊 配置检查清单

### 配置前检查

- [ ] 配置文件结构完整
- [ ] 环境变量设置正确
- [ ] 敏感信息已加密
- [ ] 配置文件权限正确

### 配置后检查

- [ ] 配置加载成功
- [ ] 配置验证通过
- [ ] 应用启动正常
- [ ] 功能测试通过

---

## 🔗 相关文档

- [系统部署指南](DEPLOYMENT_GUIDE.md)
- [数据迁移指南](DATA_MIGRATION_GUIDE.md)
- [故障诊断指南](../07_OPERATIONS/TROUBLESHOOTING_GUIDE.md)
- [性能监控指南](../07_OPERATIONS/PERFORMANCE_MONITORING_GUIDE.md)

---

**文档版本**: v1.0.0 | **创建日期**: 2026-04-07 | **状态**: Active
