---
module_id: OVERVIEW_DOC_001
version: 5.3.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?standard_type: 专业量化机构文档
applicable_scope: 全系�?compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行�?---

# DATA_FLOW.md - 数据流与模块依赖

> **版本**：v5.3
> **更新日期**�?026-03-31
> **状�?*：已完成

---

## 1. 完整数据流图

```
┌─────────────────────────────────────────────────────────────────────────────�?�?                        完整数据流（从数据到交易�?                             �?├─────────────────────────────────────────────────────────────────────────────�?�?                                                                            �?�? ┌──────────────�?    ┌──────────────�?    ┌──────────────�?              �?�? �?  AkShare    │────▶│    Baostock  │────▶│   Tushare    �?              �?�? �? (实时行情)  �?    �? (历史数据)  �?    �?  (财务)     �?              �?�? └──────────────�?    └──────────────�?    └──────────────�?              �?�?          �?                  �?                  �?                       �?�?          �?                  �?                  �?                       �?�? ┌─────────────────────────────────────────────────────────────────�?     �?�? �?                     Layer 0: 数据�?                              �?     �?�? �? ┌────────────�? ┌────────────�? ┌────────────�? ┌────────────�?  �?     �?�? �? �?  data_    �? �?  data_    �? �?  data_    �? �?  factor_  �?  �?     �?�? �? �?collector  │──▶│  cleaner   │──▶│  storage   │──▶│ registry   �?  �?     �?�? �? └────────────�? └────────────�? └────────────�? └────────────�?  �?     �?�? └─────────────────────────────────────────────────────────────────�?     �?�?                                   �?                                         �?�?                                   �?                                         �?�? ┌─────────────────────────────────────────────────────────────────�?     �?�? �?                     Layer 2: Alpha�?                            �?     �?�? �? ┌────────────�? ┌────────────�? ┌────────────�?                 �?     �?�? �? �?  factor_  �? �? strategy_ �? �?  signal_ �?                 �?     �?�? �? �?calculator  │──▶│   engine   │──▶│ generator �?                 �?     �?�? �? └────────────�? └────────────�? └────────────�?                 �?     �?�? └─────────────────────────────────────────────────────────────────�?     �?�?                                   �?                                         �?�?                                   �?                                         �?�? ┌─────────────────────────────────────────────────────────────────�?     �?�? �?                     Layer 3: 风险�?                              �?     �?�? �? ┌────────────�? ┌────────────�? ┌────────────�?                 �?     �?�? �? �?   risk_   �? �?  position �? �?  stop_    �?                 �?     �?�? �? �? manager   │──▶│  calculator│──▶│   loss     �?                 �?     �?�? �? └────────────�? └────────────�? └────────────�?                 �?     �?�? └─────────────────────────────────────────────────────────────────�?     �?�?                                   �?                                         �?�?                                   �?                                         �?�? ┌─────────────────────────────────────────────────────────────────�?     �?�? �?                     Layer 5: 执行�?                             �?     �?�? �? ┌────────────�? ┌────────────�? ┌────────────�? ┌────────────┐│      �?�? �? �?  order_   �? �?   trade_  �? �?  broker_  �? �?  order_   ││      �?�? �? �? generator │──▶│  executor  │──▶│   adapter  │──▶│   router   ││      �?�? �? └────────────�? └────────────�? └────────────�? └────────────┘│      �?�? └─────────────────────────────────────────────────────────────────�?     �?�?                                                                            �?└─────────────────────────────────────────────────────────────────────────────�?```

---

## 2. Layer间接口定�?
### 2.1 Layer 0 �?Layer 2 接口

```python
# 数据输出格式（Layer 0 输出�?DataOutput = {
    "date": "2026-03-28",
    "code": "000001",
    "open": 10.5,
    "high": 11.0,
    "low": 10.3,
    "close": 10.8,
    "volume": 1000000,
    "amount": 10800000,
    "change": 0.028,
    "turnover": 0.015,
    "pe": 12.5,
    "pb": 1.2
}
```

### 2.2 Layer 2 �?Layer 3 接口

```python
# 因子输出格式（Layer 2 输出�?FactorOutput = {
    "date": "2026-03-28",
    "code": "000001",
    "factor_id": "ALPHA_001",
    "factor_value": 0.75,
    "factor_rank": 15,
    "confidence": 0.85
}

# 策略信号格式
SignalOutput = {
    "signal_id": "SIG_001",
    "strategy_id": "S001",
    "date": "2026-03-28",
    "code": "000001",
    "direction": "long",  # long / short
    "strength": 0.85,     # 0.0 - 1.0
    "entry_price": 10.8,
    "stop_loss": 9.72,
    "take_profit": 11.88
}
```

### 2.3 Layer 3 �?Layer 5 接口

```python
# 风险校验后信�?ValidatedSignal = {
    "signal_id": "SIG_001",
    "approved": True,
    "position_size": 0.15,
    "risk_level": "LOW",
    "adjustments": []
}

# 订单格式
Order = {
    "order_id": "ORD_001",
    "signal_id": "SIG_001",
    "code": "000001",
    "direction": "buy",   # buy / sell
    "order_type": "limit", # market / limit
    "price": 10.8,
    "quantity": 1000,
    "status": "pending"
}
```

---

## 3. 模块依赖关系

```
模块依赖图：

data_collector ──┬──�?data_cleaner ──┬──�?data_storage
                 �?                   �?                 �?                   └──�?factor_registry
                 �?                 └────────────────────────�?factor_calculator

factor_registry ──┬──�?factor_calculator ──┬──�?strategy_engine
                  �?                       �?                  �?                       └──�?signal_generator

strategy_engine ──┬──�?risk_manager ──┬──�?position_calculator
                  �?                  �?                  �?                  └──�?stop_loss_handler

risk_manager ─────┼──�?backtest_framework
                  �?                  └──�?trade_executor

trade_executor ───┬──�?monitoring_system
                  �?                  └──�?performance_monitor

config_manager ───┼──�?task_scheduler
                  �?                  └──�?logger

logger ───────────┼──�?exception_handler
                  �?                  └──�?performance_monitor
```

---

## 4. 数据存储规格

| 存储�?| 格式 | 位置 | 说明 |
|--------|------|------|------|
| 原始数据 | Parquet | `data/raw/{type}/{year}/` | 原始采集数据 |
| 处理后数�?| Parquet + SQLite | `data/processed/` | 清洗后数�?|
| 因子数据 | Parquet | `data/factors/{factor_id}/` | 按因子存�?|
| 信号数据 | SQLite | `data/signals/` | 策略信号 |
| 订单数据 | SQLite | `data/orders/` | 交易订单 |
| 回测结果 | Parquet | `data/backtest_results/` | 回测绩效 |

---

## 5. 配置文件关联

```
配置文件 �?模块映射�?
config/
├── system.yaml ──────────────�?main.py / config_manager
├── data_sources.yaml ────────�?data_collector
├── factors/
�?  ├── alpha_factors.yaml ──�?factor_calculator
�?  └── selected_factors.yaml ─�?strategy_engine
├── strategies/
�?  └── active_strategies.yaml ─�?strategy_engine
└── risk/
    ├── rules.yaml ──────────�?risk_manager
    └── limits.yaml ─────────�?position_calculator
```

---

## 6. 错误处理机制

```python
# 错误传播�?
Layer 0 (数据�?
    �?    ├── DataException ──────�?记录日志，跳过该数据，继续处�?    �?    �?Layer 2 (Alpha�?
    �?    ├── FactorException ────�?跳过该因子，使用备选因�?    �?    �?Layer 3 (风险�?
    �?    ├── RiskException ──────�?拒绝信号，记录风控日�?    �?    �?Layer 5 (执行�?
    �?    └── ExecutionException ─�?重试3次，失败则告�?```

---

## 7. 版本兼容性规�?
| 规则 | 说明 |
|------|------|
| 数据格式版本 | 主版本不兼容，次版本向后兼容 |
| 接口版本 | 通过版本号协�?|
| 配置版本 | 通过配置中的version字段标识 |

---

*最后更新：2026-03-28*
