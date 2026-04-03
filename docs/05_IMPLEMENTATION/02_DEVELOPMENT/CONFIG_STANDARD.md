---
module_id: IMPL_GUIDE_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部署
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# CONFIG_STANDARD.md - 配置文件标准

> **版本**：v4.0
> **更新日期**：2026-03-28
> **状态**：已制定

---

## 1. 配置文件目录结构

```
ZephyrAlpha/
├── config/                    # 配置文件根目录
│   ├── system.yaml         # 系统配置
│   ├── data_sources.yaml   # 数据源配置
│   ├── strategies/          # 策略配置
│   │   ├── active.yaml    # 活跃策略列表
│   │   └── templates/      # 策略模板
│   ├── factors/            # 因子配置
│   │   ├── alpha.yaml     # Alpha因子
│   │   ├── risk.yaml      # 风险因子
│   │   └── selected.yaml  # 选中的因子
│   ├── risk/              # 风险配置
│   │   ├── limits.yaml    # 风险限制
│   │   └── rules.yaml     # 风险规则
│   └── workflows/          # 工作流配置
│       └── daily.yaml      # 每日流水线
```

---

## 2. 配置文件格式规范

### 2.1 YAML格式要求

```yaml
# ✅ 正确格式
config_version: "v1.0"
last_updated: "2026-03-28"

system:
  name: "清风量化系统"
  mode: "backtest"

# ❌ 错误格式
config-version: v1.0  # 使用横杠而非下划线
lastUpdated: "2026-03-28"  # 使用驼峰而非蛇形
```

### 2.2 配置项命名规范

```yaml
# ✅ 正确：蛇形命名
data_source:
  api_key: "xxx"
  timeout_seconds: 30

# ❌ 错误：驼峰命名
dataSource:
  apiKey: "xxx"
  timeoutSeconds: 30
```

---

## 3. 配置项分类

### 3.1 系统配置 (system.yaml)

```yaml
system:
  name: "清风量化交易系统v4.0"
  version: "4.0.0"
  mode: "backtest"  # backtest | simulation | paper | live

paths:
  data_dir: "./data"
  log_dir: "./logs"
  output_dir: "./output"
  config_dir: "./config"

defaults:
  initial_capital: 1000000
  commission_rate: 0.0003
  stamp_tax: 0.001

logging:
  level: "INFO"
  rotation: "00:00"
  retention_days: 30
```

### 3.2 数据源配置 (data_sources.yaml)

```yaml
data_sources:
  akshare:
    enabled: true
    rate_limit: 10
    retry: 3

  tushare:
    enabled: false
    token: "${TUSHARE_TOKEN}"  # 使用环境变量

  baostock:
    enabled: true
    retry: 3

update_schedule:
  daily_price: "18:00"
  minute_data: "16:00"
  financial: "20:00"
```

### 3.3 因子配置 (factors/selected.yaml)

```yaml
selected_factors:
  version: "v1.0"
  last_updated: "2026-03-28"

  alpha_factors:
    - factor_id: "ALPHA_001"
      name: "RPS5日"
      weight: 0.15
      status: "active"

  risk_factors:
    - factor_id: "RISK_001"
      name: "市值因子"
      style: "SIZE"
```

---

## 4. 环境变量配置

### 4.1 环境变量命名规范

```bash
# ✅ 正确：大写下划线
TUSHARE_TOKEN=xxx
DATABASE_URL=xxx
LOG_LEVEL=INFO

# ❌ 错误：驼峰或点号
tushareToken=xxx
database.url=xxx
```

### 4.2 .env文件结构

```bash
# 数据源Token
TUSHARE_TOKEN=xxx

# 数据库
DATABASE_URL=sqlite:///./data/quant.db

# 系统
LOG_LEVEL=INFO
TRADING_MODE=backtest

# API（可选）
API_HOST=127.0.0.1
API_PORT=8000
```

---

## 5. 配置加载规范

### 5.1 配置加载优先级

```
命令行参数 > 环境变量 > 用户配置 > 默认配置
```

### 5.2 配置验证

```python
# ✅ 配置加载后必须验证
class ConfigValidator:
    def validate(self, config: dict) -> bool:
        required_fields = ["system.name", "system.version"]
        for field in required_fields:
            if not self._get_nested(config, field):
                raise ConfigException(f"Missing required field: {field}")
        return True
```

---

## 6. 配置热重载规范

```python
# 配置变更监听
class ConfigWatcher:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.last_modified = None

    def check_for_changes(self):
        """检查配置文件是否变更"""
        current_mtime = os.path.getmtime(self.config_path)
        if current_mtime != self.last_modified:
            self.last_modified = current_mtime
            return True
        return False
```

---

## 7. 禁止的硬编码

| 类型 | 示例 | 正确做法 |
|------|------|----------|
| API地址 | `"http://api.example.com"` | `config.get("api.base_url")` |
| 超时时间 | `timeout=30` | `config.get("api.timeout")` |
| 重试次数 | `retry=3` | `config.get("api.retry")` |
| 阈值 | `if x > 100:` | `if x > config.get("threshold.value"):` |

---

## 8. 相关文档

| 文档 | 说明 |
|------|------|
| [CODE_QUALITY.md](./CODE_QUALITY.md) | 代码质量标准 |
| [ERROR_HANDLING.md](./ERROR_HANDLING.md) | 错误处理规范 |

---

*最后更新：2026-03-28*
