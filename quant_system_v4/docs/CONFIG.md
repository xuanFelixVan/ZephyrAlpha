# CONFIG.md - 配置规格

> **版本**：v4.0
> **日期**：2026-03-28
> **状态**：设计阶段

---

## 1. 配置原则

1. **一切通过配置控制** - 代码只是配置的执行器
2. **YAML驱动** - 所有配置文件使用YAML格式
3. **环境变量** - 敏感信息使用环境变量
4. **版本控制** - 配置文件纳入Git版本控制

---

## 2. 配置文件结构

```
config/
├── system.yaml                 # 系统全局配置
├── data_sources.yaml           # 数据源配置
├── database.yaml               # 数据库配置
│
├── factors/                   # 因子配置
│   ├── alpha_factors.yaml     # Alpha因子定义
│   ├── risk_factors.yaml      # 风险因子定义
│   └── selected_factors.yaml  # 当前选中因子
│
├── strategies/                 # 策略配置
│   ├── strategy_001.yaml     # 策略1配置
│   ├── strategy_002.yaml     # 策略2配置
│   └── active_strategies.yaml # 活跃策略列表
│
├── risk/                      # 风险配置
│   ├── rules.yaml            # 风险规则
│   ├── limits.yaml           # 风险限制
│   └── stop_loss.yaml        # 止损配置
│
└── workflows/                 # 工作流配置
    ├── daily_pipeline.yaml   # 每日流水线
    └── weekly_pipeline.yaml  # 每周流水线
```

---

## 3. 配置文件示例

### 3.1 system.yaml - 系统全局配置

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
    initial_capital: 1000000  # 初始资金100万
    commission_rate: 0.0003  # 万三佣金
    stamp_tax: 0.001        # 千一印花税

  logging:
    level: "INFO"
    format: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
    rotation: "00:00"       # 每天零点轮转
    retention: "30 days"
```

### 3.2 data_sources.yaml - 数据源配置

```yaml
data_sources:
  akshare:
    enabled: true
    rate_limit: 10
    retry: 3

  tushare:
    enabled: true
    token: "${TUSHARE_TOKEN}"
    retry: 3

  baostock:
    enabled: true
    retry: 3

  efinance:
    enabled: true

  # 数据更新计划
  update_schedule:
    daily_price: "18:00"    # 每天18:00更新日线
    minute_data: "16:00"     # 收盘后更新分钟
    financial: "20:00"       # 20:00更新财务
```

### 3.3 factors/selected_factors.yaml - 选中因子

```yaml
selected_factors:
  version: "v1.0"
  last_updated: "2026-03-28"

  alpha_factors:
    - factor_id: "ALPHA_001"
      name: "RPS5日"
      weight: 0.15
      status: "active"

    - factor_id: "ALPHA_002"
      name: "资金流"
      weight: 0.20
      status: "active"

    - factor_id: "ALPHA_003"
      name: "PE倒数"
      weight: 0.10
      status: "active"

  risk_factors:
    - factor_id: "RISK_001"
      name: "市值因子"
      style: "SIZE"

    - factor_id: "RISK_002"
      name: "价值因子"
      style: "VALUE"
```

### 3.4 strategies/active_strategies.yaml - 活跃策略

```yaml
active_strategies:
  version: "v1.0"
  last_updated: "2026-03-28"

  strategies:
    - strategy_id: "S001"
      name: "趋势跟踪策略"
      enabled: true
      mode: "simulation"  # simulation | paper | live
      max_position: 0.20
      priority: 1

    - strategy_id: "S002"
      name: "均值回归策略"
      enabled: true
      mode: "simulation"
      max_position: 0.15
      priority: 2

    - strategy_id: "S003"
      name: "龙头策略"
      enabled: true
      mode: "simulation"
      max_position: 0.25
      priority: 1
```

### 3.5 risk/rules.yaml - 风险规则

```yaml
risk_rules:
  position_limits:
    max_single_position: 0.20      # 单股最大20%
    max_same_sector: 0.40          # 同板块最大40%
    max_total_position: 0.90       # 总仓位最大90%
    min_cash_ratio: 0.10          # 最小现金比例10%

  stop_loss:
    enabled: true
    hard_stop_loss: -0.08         # 硬止损8%
    time_stop_days: 5             # 时间止损5天
    trailing_stop:
      enabled: true
      activation_profit: 0.05      # 盈利5%后激活
      trail_distance: 0.03         # 追踪距离3%

  take_profit:
    enabled: true
    targets:
      - level: 1
        profit: 0.05              # 第一止盈5%
        exit_ratio: 0.50          # 卖出50%
      - level: 2
        profit: 0.10              # 第二止盈10%
        exit_ratio: 1.00          # 全部卖出

  var_limits:
    enabled: true
    confidence: 0.95
    max_var: 0.15                # VaR最大15%

  drawdown_limits:
    enabled: true
    max_drawdown: 0.20           # 最大回撤20%
    warning_threshold: 0.15      # 预警阈值15%
```

### 3.6 workflows/daily_pipeline.yaml - 每日流水线

```yaml
workflow:
  name: "daily_pipeline"
  description: "每日量化流水线"
  schedule: "0 19 * * 1-5"  # 每天19:00

  steps:
    - name: "step1_data_update"
      module: "data_collector"
      action: "collect_all"
      params:
        date: "${yesterday}"
      on_error: "retry"
      max_retries: 3

    - name: "step2_factor_calculation"
      module: "factor_calculator"
      action: "calculate_selected"
      params:
        top_n: 50
      depends_on: ["step1_data_update"]

    - name: "step3_strategy_signals"
      module: "strategy_engine"
      action: "run_all"
      depends_on: ["step2_factor_calculation"]

    - name: "step4_risk_validation"
      module: "risk_manager"
      action: "validate_signals"
      depends_on: ["step3_strategy_signals"]

    - name: "step5_generate_report"
      module: "report_generator"
      action: "generate_daily_report"
      depends_on: ["step4_risk_validation"]
```

---

## 4. 环境变量

```bash
# .env 文件
TUSHARE_TOKEN=your_token_here
DATABASE_PASSWORD=your_password
ALPHA_VANTAGE_KEY=your_key
```

---

## 5. 配置验证

```python
# config/schema.py - 配置验证模式
from pydantic import BaseModel
from typing import List, Optional

class SystemConfig(BaseModel):
    name: str
    version: str
    mode: str

class RiskConfig(BaseModel):
    max_single_position: float
    max_total_position: float
    hard_stop_loss: float

class StrategyConfig(BaseModel):
    strategy_id: str
    name: str
    enabled: bool
    max_position: float
```

---

## 6. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 初始版本，配置规格设计 |
