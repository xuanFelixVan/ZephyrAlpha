---
doc_type: architecture_view
title: 契约目录全景图
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 契约目录全景图 / Contract Catalog

> **文档作用 / Purpose**: 以表格形式展示39个跨层数据契约,用于AI接入新模块时查询"消费了谁的契约、产出什么契约"。

> 本文档由 generate_contract_catalog.py 从 depgraph (PostgreSQL) 自动生成
> 真源: architecture_model/contracts/cross_layer_contracts.yaml
> 最后更新以 git log 为准

## 1. 统计概览

| 指标 | 数量 |
|------|------|
| 契约总数 | 39 |
| P0(核心数据/错误/背压契约) | 16 |
| P1(蓝图签名契约) | 21 |
| 其他 | 2 |
| 已冻结(planned) | 32 |
| 设计中(design) | 7 |

## 2. 契约流向矩阵(Provider → Consumer)

> 行:提供方域 | 列:消费方域 | 单元格:契约ID

| Provider \ Consumer | * | D_BACKTEST | D_EX_CORE | D_FACTOR | D_FRONTEND | D_GOV_ENFORCEMENT | D_INFRA_OPS | D_INTELLIGENCE | D_MKT_DATA | D_ML_TRAIN | D_OPS | D_PF_CORE | D_RISK | D_SHARED | D_SIGLEGACY | D_SIGQC | D_SIMULATION | D_TRADING |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ***** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_BACKTEST** | — | — | — | — | CTR-P1-016, CTR-P1-017 | — | — | — | — | — | CTR-P1-016 | CTR-P1-016 | CTR-P1-016 | — | — | — | — | — |
| **D_EX_CORE** | — | — | — | — | — | — | — | — | — | CTR-006 | — | CTR-ERR-005 | CTR-006 | — | — | — | — | CTR-005, CTR-006, CTR-ERR-005, CTR-P1-007 |
| **D_FACTOR** | — | CTR-002 | — | — | — | — | — | — | CTR-BP-001, CTR-BP-002, CTR-BP-003 | — | — | CTR-002, CTR-P1-002 | CTR-002 | — | CTR-002, CTR-ERR-002, CTR-P1-002 | — | — | CTR-P1-001 |
| **D_FRONTEND** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_GOV_ENFORCEMENT** | — | — | CTR-P1-012 | — | — | CTR-P1-012 | — | — | — | — | — | — | CTR-P1-012 | — | — | — | — | — |
| **D_INFRA_OPS** | — | — | CTR-P1-010 | CTR-P1-010 | CTR-P1-010 | CTR-P1-010 | — | — | — | CTR-P1-010 | CTR-P1-010 | CTR-P1-010 | CTR-P1-010 | — | CTR-P1-010 | — | CTR-P1-010 | CTR-P1-010 |
| **D_INTELLIGENCE** | — | — | — | — | — | — | — | — | — | CTR-P1-014 | — | — | — | — | — | — | CTR-P1-014 | — |
| **D_MKT_DATA** | — | CTR-001 | CTR-TRACE-001 | CTR-001, CTR-ERR-001, CTR-TRACE-001 | — | — | — | — | — | CTR-TRACE-001 | — | CTR-TRACE-001 | CTR-TRACE-001 | — | CTR-001, CTR-TRACE-001 | — | CTR-001 | CTR-TRACE-001 |
| **D_ML_TRAIN** | — | — | — | — | — | — | — | — | — | — | — | CTR-P1-004, CTR-P1-005 | — | — | CTR-P1-004, CTR-P1-005 | — | — | — |
| **D_OPS** | — | — | CT-TEL-001, CT-TEL-002, CT-TEL-003, CT-TEL-004, CTR-P1-013 | — | — | CTR-P1-013 | CT-TEL-001, CT-TEL-002, CT-TEL-003, CT-TEL-004, CTR-P1-013 | — | — | — | CTR-P1-013 | — | CTR-P1-013 | — | — | — | — | CTR-P1-013 |
| **D_PF_CORE** | — | — | CTR-004 | — | — | CTR-P1-006 | — | — | — | — | — | — | — | — | — | — | — | CTR-P1-006 |
| **D_RISK** | — | — | CTR-ERR-004 | — | CTR-P1-008, CTR-P1-011 | CTR-P1-011 | — | — | — | — | — | CTR-003, CTR-ERR-004, CTR-P1-011 | — | — | — | — | — | CTR-P1-011 |
| **D_SHARED** | CTR-ERR-006 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_SIGLEGACY** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_SIGQC** | — | — | — | — | — | — | — | — | — | — | — | CTR-ERR-003 | CTR-ERR-003 | — | — | — | — | — |
| **D_SIMULATION** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_TRADING** | — | — | — | — | CTR-P1-009 | CTR-P1-009 | — | — | — | — | — | — | — | — | — | — | — | — |

## 3. 契约详情

### CTR-001 — NormalizedMarketData / 标准化行情数据

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_MKT_DATA
- **消费方**: D_FACTOR, D_SIGLEGACY, D_SIMULATION, D_BACKTEST
- **状态**: planned
- **描述**: Data Source → Factor 核心数据契约。质量门禁通过后的标准化行情数据。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| symbol | str | ✅ | 标准化证券代码（如 600519.SH） |
| data_source | str | ✅ | 数据源标识（如 akshare, wind） |
| timestamp | datetime | ✅ | 数据时间戳（UTC） |
| open | Decimal | ✅ | 开盘价 |
| high | Decimal | ✅ | 最高价 |
| low | Decimal | ✅ | 最低价 |
| close | Decimal | ✅ | 收盘价 |
| volume | Decimal | ✅ | 成交量 |
| amount | Optional[Decimal] | — | 成交额（A 股必填） |
| adj_factor | Optional[Decimal] | — | 复权因子 |
| quality_score | float | — | 质量门禁结果 0.0-1.0 |
| is_suspended | bool | — | 停牌标记 |
| ingested_at | Optional[datetime] | — | 入库时间 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文（CTR-TRACE-001） |
| timeout_ms | int | — | 操作超时时间（毫秒） |
| retry_policy | str | — | 重试策略：none | linear | exponential_backoff |
| config_load_timeout_ms | int | — | 配置加载超时时间（毫秒） |
| config_load_retry_policy | str | — | 重试策略：none | linear | exponential_backoff |
| max_retries | int | — | 最大重试次数 |
| exceptions | List[str] | — | 预期异常类型列表 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/market_data.py`

### CTR-002 — FactorSignal / 因子信号

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: D_SIGLEGACY, D_RISK, D_PF_CORE, D_BACKTEST
- **状态**: planned
- **描述**: Factor → Signal/Risk/Portfolio 核心数据契约。单个因子在单个时间截面对单个标的的信号值。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| factor_id | str | ✅ | 因子唯一 ID（对应 FactorRegistry 的 key） |
| symbol | str | ✅ | 标的代码 |
| as_of_date | datetime | ✅ | 信号计算截面日期 |
| raw_value | float | ✅ | 原始因子值 |
| normalized_value | Optional[float] | — | 截面标准化后的值（z-score） |
| rank_pct | Optional[float] | — | 分位数排名 0-1 |
| confidence | float | — | 信号置信度 0.0-1.0 |
| is_valid | bool | — | 信号有效性 |
| factor_version | str | — | 因子版本 |
| extra | Dict[str, Any] | — | 扩展字段 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文（CTR-TRACE-001） |
| timeout_ms | int | — | 因子计算超时时间（毫秒） |
| retry_policy | str | — | 重试策略：none | linear | exponential_backoff |
| max_retries | int | — | 最大重试次数 |
| exceptions | List[str] | — | 预期异常类型列表 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/factor_signal.py`

### CTR-003 — RiskLimits / 风险限额

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_RISK
- **消费方**: D_PF_CORE
- **状态**: planned
- **描述**: Risk → Portfolio 核心数据契约。风险限额约束集合，由 Portfolio 组合优化器强制执行。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| as_of_date | datetime | ✅ | 限额生效日期 |
| max_single_position | float | — | 单标的最大权重（如 0.10 = 10%） |
| min_single_position | float | — | 单标的最小权重 |
| max_gross_leverage | float | — | 总杠杆上限 |
| max_sector_concentration | float | — | 单行业集中度上限 |
| max_portfolio_var_1d | Optional[float] | — | 日度 VaR 上限（绝对值） |
| max_drawdown_limit | Optional[float] | — | 最大回撤触发线 |
| symbol_overrides | Dict[str, float] | — | 个股特殊限制 {symbol: max_weight} |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文（CTR-TRACE-001） |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/risk_limits.py`

### CTR-004 — Order / 委托指令

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_PF_CORE
- **消费方**: D_EX_CORE
- **状态**: design
- **描述**: Portfolio → Execution 核心数据契约。单笔委托指令（可变对象，随生命周期更新状态）。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| order_id | str | ✅ | 全局唯一 ID（UUID） |
| symbol | str | ✅ | 标的代码 |
| strategy_id | str | ✅ | 来源策略 ID |
| side | OrderSide | ✅ | 方向：BUY / SELL |
| order_type | OrderType | ✅ | 类型：MARKET / LIMIT / STOP |
| quantity | Decimal | ✅ | 目标数量（股数） |
| limit_price | Optional[Decimal] | — | LIMIT 单必填 |
| status | OrderStatus | — | 状态机：PENDING/SUBMITTED/PARTIAL/FILLED/CANCELLED/REJECTED |
| filled_quantity | Decimal | — | 已成交数量 |
| avg_fill_price | Optional[Decimal] | — | 加权平均成交价 |
| created_at | Optional[datetime] | — | 创建时间 |
| updated_at | Optional[datetime] | — | 更新时间 |
| broker_order_id | Optional[str] | — | 券商侧委托号（回填） |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文（CTR-TRACE-001） |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/order.py`

### CTR-005 — Fill / 成交回报

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_EX_CORE
- **消费方**: D_TRADING
- **状态**: planned
- **描述**: Execution → Analytics 核心数据契约。单次成交回报（不可变）。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| fill_id | str | ✅ | 全局唯一成交 ID |
| order_id | str | ✅ | 关联委托 ID |
| symbol | str | ✅ | 标的代码 |
| strategy_id | str | ✅ | 来源策略 ID |
| filled_quantity | Decimal | ✅ | 成交数量 |
| fill_price | Decimal | ✅ | 成交价格 |
| fill_timestamp | datetime | ✅ | 成交时间 |
| commission | Decimal | — | 佣金 |
| slippage | Optional[Decimal] | — | 滑点（实际 vs 预期） |
| broker_fill_id | Optional[str] | — | 券商侧成交 ID |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文（CTR-TRACE-001） |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/fill.py`

### CTR-006 — PositionSnapshot / 持仓快照

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_EX_CORE
- **消费方**: D_RISK, D_TRADING, D_ML_TRAIN
- **状态**: planned
- **描述**: 持仓快照。不可变，代表某一时刻的完整持仓状态。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| as_of_timestamp | datetime | ✅ | 快照时间 |
| portfolio_id | str | ✅ | 组合 ID |
| holdings | Dict[str, Decimal] | — | {symbol: quantity} |
| market_values | Dict[str, Decimal] | — | {symbol: market_value} |
| total_market_value | Decimal | — | 总市值 |
| cash | Decimal | — | 现金 |
| gross_leverage | float | — | 总杠杆 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文（CTR-TRACE-001） |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/position.py`

### CTR-BP-001 — BackpressurePause / 背压暂停信号

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: D_MKT_DATA
- **状态**: planned
- **描述**: 下游（Factor/Signal）处理能力不足时，向上游（Data Source）发出暂停信号。Data Source 暂停该标的的数据下发。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| signal_id | str | ✅ | 信号唯一 ID |
| symbol | str | ✅ | 暂停的标的 |
| action | str | — | 固定值 PAUSE |
| duration_ms | int | ✅ | 暂停时长（毫秒），到期自动恢复 |
| reason | str | ✅ | 暂停原因：buffer_full | processing_overload | gc_pause | downstream_unavailable |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/backpressure/pause.py`

### CTR-BP-002 — BackpressureThrottle / 背压降速信号

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: D_MKT_DATA
- **状态**: planned
- **描述**: 下游处理压力较大但不至于暂停时，向上游发出降速信号。上游将下发速率降至指定值。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| signal_id | str | ✅ | 信号唯一 ID |
| symbol | str | ✅ | 降速的标的 |
| action | str | — | 固定值 THROTTLE |
| max_rate_per_sec | int | ✅ | 降速后的最大速率（条/秒） |
| reason | str | ✅ | 降速原因 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/backpressure/throttle.py`

### CTR-BP-003 — BackpressureResume / 背压恢复信号

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: D_MKT_DATA
- **状态**: planned
- **描述**: 下游处理能力恢复后，向上游发出恢复信号。上游恢复正常下发速率。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| signal_id | str | ✅ | 信号唯一 ID |
| symbol | str | ✅ | 恢复的标的 |
| action | str | — | 固定值 RESUME |
| reason | str | ✅ | 恢复原因：buffer_cleared | capacity_restored | gc_complete | upstream_recovered |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/backpressure/resume.py`

### CTR-ERR-001 — DataQualityError / 行情质量门禁不通过错误

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_MKT_DATA
- **消费方**: D_FACTOR
- **状态**: planned
- **描述**: Data Source 行情质量门禁不通过时抛出的错误。包含具体的质量缺陷分类和恢复建议。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| error_id | str | ✅ | 错误唯一 ID（UUID） |
| symbol | str | ✅ | 出问题的标的代码 |
| failure_reason | str | ✅ | missing_tick | stale_data | outlier_price | timestamp_future | suspension_detected | volume_zero |
| quality_score | float | ✅ | 实际质量分（< 0.7） |
| recovery_hint | str | ✅ | RETRY | SKIP_SYMBOL | SWITCH_SOURCE | HALT |
| failed_field | Optional[str] | — | 触发的具体字段名 |
| failed_value | Optional[str] | — | 触发时的实际值（字符串表示） |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/errors/data_quality_error.py`

### CTR-ERR-002 — FactorComputationError / 因子计算失败错误

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: D_SIGLEGACY
- **状态**: planned
- **描述**: Factor 因子计算过程中遇到无法处理的异常时抛出的错误。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| error_id | str | ✅ | 错误唯一 ID |
| factor_id | str | ✅ | 出问题的因子 ID |
| symbol | str | ✅ | 标的代码 |
| failure_reason | str | ✅ | input_missing | division_by_zero | window_insufficient | memory_exceeded | invalid_parameter | timeout |
| recovery_hint | str | ✅ | RETRY | SKIP_FACTOR | DEGRADE_TO_DEFAULT | ESCALATE |
| detail | Optional[str] | — | 详细错误堆栈摘要 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/errors/factor_computation_error.py`

### CTR-ERR-003 — SignalDegradationWarning / 信号质量下降警告

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_SIGQC
- **消费方**: D_RISK, D_PF_CORE
- **状态**: planned
- **描述**: Signal 检测到信号质量显著下降时发出的警告。非致命，但 Risk/Portfolio 应据此调低仓位或暂停交易。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| warning_id | str | ✅ | 警告唯一 ID |
| reason | str | ✅ | confidence_below_threshold | regime_change_detected | factor_decay_triggered | signal_conflict | throughput_drop |
| affected_factor_ids | List[str] | — | 受影响的因子 ID 列表 |
| degradation_level | str | ✅ | MILD | MODERATE | SEVERE |
| suggested_action | str | ✅ | REDUCE_POSITION | PAUSE_SIGNAL | CONTINUE_WITH_FLAG |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/trading/trading_contracts/market/signal_degradation_warning.py`

### CTR-ERR-004 — RiskLimitViolationError / 风险限额突破错误

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_RISK
- **消费方**: D_PF_CORE, D_EX_CORE
- **状态**: planned
- **描述**: Risk 检测到当前或计划操作将突破风险限额时抛出的硬错误。Portfolio/Execution MUST 据此阻止订单生成和执行。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| error_id | str | ✅ | 错误唯一 ID |
| portfolio_id | str | ✅ | 组合 ID |
| violated_constraint | str | ✅ | position_limit | leverage_limit | var_breach | drawdown_trigger | sector_concentration | concentration_limit |
| violation_detail | str | ✅ | 人类可读的违规描述（如 'BTC 仓位 12.3% 超过 10% 限额'） |
| limit_value | float | ✅ | 限额值 |
| actual_value | float | ✅ | 实际值 |
| recovery_hint | str | ✅ | REDUCE_AND_RETRY | HALT_AND_ESCALATE | MANUAL_OVERRIDE_REQUIRED |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/errors/risk_limit_violation_error.py`

### CTR-ERR-005 — ExecutionRejectionError / 执行拒绝错误

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_EX_CORE
- **消费方**: D_PF_CORE, D_TRADING
- **状态**: planned
- **描述**: Execution 订单执行过程中被券商或市场拒绝时抛出的错误。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| error_id | str | ✅ | 错误唯一 ID |
| order_id | str | ✅ | 被拒绝的 Order ID |
| symbol | str | ✅ | 标的代码 |
| rejection_source | str | ✅ | BROKER | EXCHANGE | CIRCUIT_BREAKER | INTERNAL |
| rejection_reason | str | ✅ | insufficient_balance | quantity_exceeds_limit | price_out_of_range | market_closed | timeout | broker_error |
| broker_message | Optional[str] | — | 券商原始错误信息（保留原文） |
| recovery_hint | str | ✅ | RETRY | RETRY_WITH_REDUCED_QTY | CANCEL_AND_REPORT | WAIT_NEXT_CYCLE |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/errors/execution_rejection_error.py`

### CTR-ERR-006 — ContractViolationError / 契约违反错误

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_SHARED
- **消费方**: *
- **状态**: planned
- **描述**: 运行时跨层数据契约校验失败时抛出的通用错误。任何层的数据入站/出站校验均可抛出。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| error_id | str | ✅ | 错误唯一 ID |
| contract_id | str | ✅ | 被违反的契约 ID（如 CTR-001） |
| violation_type | str | ✅ | schema_mismatch | field_type_error | missing_required | version_incompatible | value_out_of_range | extra_field_forbidden |
| field_name | Optional[str] | — | 触发的具体字段名 |
| expected_type | Optional[str] | — | 契约期望的类型 |
| actual_type | Optional[str] | — | 实际收到的类型 |
| detail | str | ✅ | 详细校验失败描述 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/errors/contract_violation_error.py`

### CTR-TRACE-001 — TraceContext / 全链路追踪上下文

- **类型**: P0
- **版本**: 1.0
- **提供方**: D_MKT_DATA
- **消费方**: D_FACTOR, D_SIGLEGACY, D_RISK, D_PF_CORE, D_EX_CORE, D_TRADING, D_ML_TRAIN
- **状态**: planned
- **描述**: 跨所有数据层的全链路追踪上下文。Data Source 在首次产生数据时生成，后续每层追加 span。支持反向追溯：'这笔订单是因为哪个因子的哪个信号在哪个时刻产生的'。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| trace_id | str | ✅ | 全局唯一追踪 ID（UUID），Data Source 生成，永不改变 |
| span_id | str | ✅ | 本层 span ID（UUID），每层重新生成 |
| service_name | str | ✅ | 本层标识：data / factor / signal / ... |
| created_at | datetime | ✅ | 本 span 创建时间（UTC 纳秒精度） |
| parent_span_id | Optional[str] | — | 上游 span_id，NULL 表示这是链头 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/trace_context.py`

### CT-TEL-001 — TelemetryMetrics / 遥测指标采集

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_OPS
- **消费方**: D_INFRA_OPS, D_EX_CORE
- **状态**: design
- **描述**: Telemetry → Config/Execution 遥测指标采集契约。Telemetry facade 提供指标采集接口，消费方通过 gauge/counter/histogram/summary 记录指标。SLA: 指标采集延迟<1s。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| module_id | str | ✅ | 来源模块ID |
| metric_name | str | ✅ | FQMN指标名（module_id::metric_name） |
| metric_type | str | ✅ | counter | gauge | histogram | summary |
| metric_value | float | ✅ | 指标值 |
| labels | Dict[str, str] | — | 标签键值对 |
| timestamp | datetime | ✅ | 采集时间戳（UTC） |
| collection_latency_ms | int | ✅ | 采集延迟（毫秒），SLA<1000 |
| schema_version | str | — | 契约版本 |

### CT-TEL-002 — TelemetryLogs / 遥测日志持久化

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_OPS
- **消费方**: D_INFRA_OPS, D_EX_CORE
- **状态**: design
- **描述**: Telemetry → Config/Execution 遥测日志持久化契约。结构化日志通过 JSONL 持久化，支持 trace_id 关联。SLA: 持久化延迟<5s。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| module_id | str | ✅ | 来源模块ID |
| level | str | ✅ | DEBUG | INFO | WARNING | ERROR | FATAL |
| message | str | ✅ | 日志消息 |
| trace_id | str | — | 关联Trace ID |
| span_id | str | — | 关联Span ID |
| labels | Dict[str, str] | — | 标签键值对 |
| timestamp | datetime | ✅ | 日志时间戳（UTC） |
| persistence_latency_ms | int | ✅ | 持久化延迟（毫秒），SLA<5000 |
| schema_version | str | — | 契约版本 |

### CT-TEL-003 — TelemetryTraces / 遥测链路追踪

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_OPS
- **消费方**: D_INFRA_OPS, D_EX_CORE
- **状态**: design
- **描述**: Telemetry → Config/Execution 遥测链路追踪契约。W3C TraceContext 传播，采样率可配置。提供 span 创建/属性设置/上下文管理接口。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| trace_id | str | ✅ | W3C Trace ID |
| span_id | str | ✅ | W3C Span ID |
| parent_span_id | str | — | 父Span ID |
| operation_name | str | ✅ | 操作名称 |
| attributes | Dict[str, Any] | — | Span属性 |
| sample_rate | float | ✅ | 采样率 0.0-1.0 |
| start_time | datetime | ✅ | Span开始时间 |
| elapsed_seconds | float | ✅ | Span耗时（秒） |
| schema_version | str | — | 契约版本 |

### CT-TEL-004 — TelemetryHealth / 遥测健康检查

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_OPS
- **消费方**: D_INFRA_OPS, D_EX_CORE
- **状态**: design
- **描述**: Telemetry → Config/Execution 遥测健康检查契约。Liveness/Readiness/Healthz 三级探针，心跳间隔30s。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| module_id | str | ✅ | 探针所属模块ID |
| probe_type | str | ✅ | liveness | readiness | healthz |
| status | str | ✅ | healthy | unhealthy | degraded |
| heartbeat_interval_s | int | ✅ | 心跳间隔（秒），默认30 |
| last_heartbeat | datetime | ✅ | 最近心跳时间 |
| details | Dict[str, Any] | — | 探针详情 |
| schema_version | str | — | 契约版本 |

### CTR-P1-001 — FactorMonitorReport / 因子有效性监控报告

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: D_TRADING
- **状态**: planned
- **描述**: Factor → Analytics 因子有效性监控报告。定期评估已注册因子的预测有效性。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| factor_id | str | ✅ | 因子 ID |
| evaluation_date | str | ✅ | 评估日期 YYYY-MM-DD |
| ic_mean | float | ✅ | 信息系数均值（近 N 期） |
| ic_std | float | ✅ | IC 标准差 |
| ic_ir | float | ✅ | ICIR = IC_mean / IC_std |
| rank_ic | float | ✅ | Rank IC（Spearman 相关） |
| half_life_days | Optional[int] | — | 因子半衰期（天） |
| is_effective | bool | ✅ | True = IC 显著 + ICIR > 0.5 |
| decay_alert | bool | ✅ | True = 因子衰减告警 |
| evaluation_window | int | — | 评估窗口（交易日数） |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/factor_monitor_report.py`

### CTR-P1-002 — MacroFactorSignal / 宏观因子信号

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: D_SIGLEGACY, D_PF_CORE
- **状态**: planned
- **描述**: Factor 宏观因子信号契约。扩展 FactorSignal 以支持宏观经济维度。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| factor_id | str | ✅ | 宏观因子 ID（如 macro.pmi.cn.v1） |
| as_of_date | str | ✅ | 信号日期 |
| macro_regime | str | ✅ | expansion | contraction | neutral |
| signal_value | float | ✅ | 标准化信号值（-3 到 3） |
| data_source | str | ✅ | 宏观数据来源（如 wind_macro, nbs） |
| release_lag_days | int | ✅ | 数据发布滞后天数 |
| confidence | float | — | 置信度 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/macro_factor_signal.py`

### CTR-P1-003 — CapitalAllocationResult / 资本配置结果

- **类型**: P1
- **版本**: 1.0
- **提供方**: —
- **消费方**: D_PF_CORE
- **状态**: planned
- **描述**: Signal → Portfolio 资本配置结果契约。多策略资本分配的中间产物。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| allocation_date | str | ✅ | 配置日期 |
| strategy_allocations | Dict[str, float] | ✅ | {strategy_id: capital_weight} |
| total_allocated_weight | float | ✅ | 总权重（通常 = 1.0） |
| allocation_method | str | ✅ | equal_weight | sharpe_weight | risk_parity |
| rebalance_threshold | float | — | 触发再平衡的权重漂移阈值 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/capital_allocation_result.py`

### CTR-P1-004 — ModelServingRequest / 模型推理请求

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_ML_TRAIN
- **消费方**: D_SIGLEGACY, D_PF_CORE
- **状态**: planned
- **描述**: 跨层模型推理请求契约。ML Platform 提供推理服务，Signal/Portfolio 消费。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| model_id | str | ✅ | 已注册模型 ID |
| model_version | str | ✅ | 模型版本 |
| input_features | Dict[str, float] | ✅ | 特征名 → 特征值 |
| request_id | str | ✅ | UUID，用于异步匹配 |
| idempotency_key | str | ✅ | 幂等键（UUID） |

- **物理路径**: `src/zephyr/shared/contracts/model_serving_request.py`

### CTR-P1-005 — ModelServingResponse / 模型推理响应

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_ML_TRAIN
- **消费方**: D_SIGLEGACY, D_PF_CORE
- **状态**: planned
- **描述**: 跨层模型推理响应契约。ML Platform 返回推理结果给 Signal/Portfolio。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| request_id | str | ✅ | 请求 ID |
| model_id | str | ✅ | 模型 ID |
| prediction | float | ✅ | 预测值 |
| prediction_type | str | ✅ | factor_value | return | probability |
| confidence | float | ✅ | 预测置信度 0.0-1.0 |
| inference_ms | int | ✅ | 推理耗时（毫秒） |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/model_serving_response.py`

### CTR-P1-006 — StrategyLifecycleEvent / 策略生命周期事件

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_PF_CORE
- **消费方**: D_TRADING, D_GOV_ENFORCEMENT
- **状态**: planned
- **描述**: Portfolio → Analytics/Compliance 策略生命周期事件契约。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| strategy_id | str | ✅ | 策略 ID |
| event_type | str | ✅ | created | activated | paused | deprecated | retired |
| event_timestamp | str | ✅ | ISO 8601 UTC |
| triggered_by | str | ✅ | human | agent | system |
| reason | str | ✅ | 事件触发原因 |
| previous_status | str | ✅ | 变更前状态 |
| new_status | str | ✅ | 变更后状态 |
| performance_snapshot | Optional[Dict[str, float]] | — | 事件时的关键绩效指标 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/strategy_lifecycle_event.py`

### CTR-P1-007 — ExecutionReport / 执行分析报告

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_EX_CORE
- **消费方**: D_TRADING
- **状态**: planned
- **描述**: Execution → Analytics 执行分析报告契约（TCA 输入）。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| order_id | str | ✅ | 委托 ID |
| symbol | str | ✅ | 标的代码 |
| direction | str | ✅ | BUY | SELL |
| intended_quantity | int | ✅ | 意图成交数量 |
| actual_quantity | int | ✅ | 实际成交数量 |
| intended_price | Decimal | ✅ | 意图价格（决策价） |
| vwap_price | Decimal | ✅ | 实际成交 VWAP |
| slippage_bps | float | ✅ | 滑点（基点） |
| commission | Decimal | ✅ | 佣金 |
| execution_start | str | ✅ | 执行开始时间 ISO 8601 UTC |
| execution_end | str | ✅ | 执行结束时间 ISO 8601 UTC |
| broker_id | str | ✅ | 执行券商 |
| algo_type | str | — | 算法类型 TWAP | VWAP | NONE |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/execution_report.py`

### CTR-P1-008 — RiskDashboardSnapshot / 风险仪表板快照

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_RISK
- **消费方**: D_FRONTEND
- **状态**: planned
- **描述**: Risk → Frontend 风险仪表板实时快照契约。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| snapshot_time | str | ✅ | 快照时间 ISO 8601 UTC |
| portfolio_id | str | ✅ | 组合 ID |
| portfolio_var_1d | float | ✅ | 日度 VaR |
| max_drawdown_current | float | ✅ | 当前最大回撤 |
| gross_leverage | float | ✅ | 总杠杆 |
| top_position_concentration | float | ✅ | 最大单仓集中度 |
| sector_concentrations | Dict[str, float] | ✅ | {sector: weight} |
| active_alerts | List[str] | ✅ | 当前激活的风险告警 rule_id 列表 |
| overall_risk_score | float | ✅ | 综合风险分 0-10 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/risk_dashboard_snapshot.py`

### CTR-P1-009 — PerformanceAttributionReport / 绩效归因报告

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_TRADING
- **消费方**: D_FRONTEND, D_GOV_ENFORCEMENT
- **状态**: planned
- **描述**: Analytics → Frontend/Compliance 绩效归因报告契约。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| portfolio_id | str | ✅ | 组合 ID |
| period_start | str | ✅ | YYYY-MM-DD |
| period_end | str | ✅ | YYYY-MM-DD |
| total_return | float | ✅ | 总收益率 |
| allocation_effect | float | ✅ | 配置效应（Brinson 归因） |
| selection_effect | float | ✅ | 选股效应 |
| interaction_effect | float | ✅ | 交互效应 |
| factor_contributions | Dict[str, float] | ✅ | {factor_id: contribution} |
| transaction_cost_drag | float | ✅ | 交易成本拖累（bps） |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/performance_attribution_report.py`

### CTR-P1-010 — SystemConfiguration / 系统配置

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_INFRA_OPS
- **消费方**: D_FACTOR, D_SIGLEGACY, D_RISK, D_PF_CORE, D_EX_CORE, D_TRADING, D_FRONTEND, D_SIMULATION, D_GOV_ENFORCEMENT, D_ML_TRAIN, D_OPS
- **状态**: planned
- **描述**: Config → 全系统配置契约。基于dataclass的配置加载API，支持环境变量覆盖和热重载。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| config_id | str | ✅ | 配置唯一ID |
| config_type | str | ✅ | 配置类型：risk | trading | data | system |
| version | str | ✅ | 配置版本 |
| environment | str | ✅ | 环境：dev | test | prod |
| config_data | Dict[str, Any] | ✅ | 配置数据 |
| created_at | datetime | ✅ | 创建时间 |
| updated_at | datetime | ✅ | 更新时间 |
| is_active | bool | ✅ | 是否激活 |
| timeout_ms | int | — | 配置加载超时时间（毫秒） |
| retry_policy | str | — | 重试策略：none | linear | exponential_backoff |
| max_retries | int | — | 最大重试次数 |
| exceptions | List[str] | — | 预期异常类型列表 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/system_configuration.py`

### CTR-P1-011 — RiskMetricsReport / 风险指标报告

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_RISK
- **消费方**: D_PF_CORE, D_TRADING, D_FRONTEND, D_GOV_ENFORCEMENT
- **状态**: planned
- **描述**: Risk → 下游风险指标报告契约。包含VaR、CVaR、回撤等风险指标的计算结果。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| portfolio_id | str | ✅ | 组合ID |
| as_of_date | datetime | ✅ | 计算日期 |
| var_1d_95 | float | ✅ | 日度95% VaR |
| var_1d_99 | float | ✅ | 日度99% VaR |
| cvar_1d_95 | float | ✅ | 日度95% CVaR |
| cvar_1d_99 | float | ✅ | 日度99% CVaR |
| max_drawdown | float | ✅ | 最大回撤 |
| current_drawdown | float | ✅ | 当前回撤 |
| beta | float | ✅ | Beta系数 |
| sharpe_ratio | float | ✅ | 夏普比率 |
| sortino_ratio | float | ✅ | 索提诺比率 |
| volatility_1d | float | ✅ | 日度波动率 |
| volatility_1m | float | ✅ | 月度波动率 |
| calculation_method | str | ✅ | 计算方法：historical | parametric | monte_carlo |
| confidence_level | float | ✅ | 置信水平 |
| lookback_period | int | ✅ | 回看期（交易日） |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/risk_metrics.py`

### CTR-P1-012 — ComplianceRule / 合规规则

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_GOV_ENFORCEMENT
- **消费方**: D_RISK, D_EX_CORE, D_GOV_ENFORCEMENT
- **状态**: planned
- **描述**: Compliance → 合规规则定义契约。包含规则注册、评估接口和规则元数据。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| rule_id | str | ✅ | 规则唯一ID |
| rule_name | str | ✅ | 规则名称 |
| rule_type | str | ✅ | 规则类型：regulatory | internal_policy | jurisdiction |
| jurisdiction | str | ✅ | 适用辖区：cn_a_share | us_share | eu_mifid2 | crypto_global |
| description | str | ✅ | 规则描述 |
| severity | str | ✅ | 严重程度：critical | high | medium | low |
| enforcement_action | str | ✅ | 执行动作：block | warn | log |
| rule_logic | str | ✅ | 规则逻辑（Python表达式或规则语言） |
| version | str | ✅ | 规则版本 |
| is_active | bool | ✅ | 是否激活 |
| created_at | datetime | ✅ | 创建时间 |
| updated_at | datetime | ✅ | 更新时间 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/compliance_rule.py`

### CTR-P1-013 — TelemetryEmitter / 遥测发射器

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_OPS
- **消费方**: D_INFRA_OPS, D_RISK, D_EX_CORE, D_TRADING, D_GOV_ENFORCEMENT, D_OPS
- **状态**: planned
- **描述**: Telemetry → 全系统遥测发射器契约。提供结构化指标、日志、追踪的发射接口。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| emitter_id | str | ✅ | 发射器唯一ID |
| emitter_type | str | ✅ | 发射器类型：metrics | logs | traces |
| metric_name | str | ✅ | 指标名称 |
| metric_value | float | ✅ | 指标值 |
| metric_type | str | ✅ | 指标类型：counter | gauge | histogram | summary |
| labels | Dict[str, str] | ✅ | 标签键值对 |
| timestamp | datetime | ✅ | 时间戳 |
| source_module | str | ✅ | 来源模块 |
| correlation_id | str | ✅ | 关联ID |
| severity | str | — | 严重程度：debug | info | warning | error | critical |
| message | str | — | 消息内容 |
| span_id | str | — | 追踪Span ID |
| trace_id | str | — | 追踪Trace ID |
| parent_span_id | str | — | 父Span ID |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/telemetry_emitter.py`

### CTR-P1-014 — ExperimentResult / 实验结论

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_INTELLIGENCE
- **消费方**: D_SIMULATION, D_ML_TRAIN
- **状态**: planned
- **描述**: Experimentation → Research/ML Platform 实验结论契约。Scout Agent 完成对照实验后产出的结构化结论。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| experiment_id | str | ✅ | 全局唯一实验 ID（UUID） |
| experiment_name | str | ✅ | 人类可读实验名称 |
| experiment_type | str | ✅ | ab_test | factor_ablation | strategy_variant | parameter_sweep | custom |
| hypothesis | str | ✅ | 实验假设 |
| variant_a_description | str | ✅ | A 组描述（对照组） |
| variant_b_description | str | ✅ | B 组描述（实验组） |
| start_timestamp | datetime | ✅ | 实验开始时间（UTC） |
| end_timestamp | datetime | ✅ | 实验结束时间（UTC） |
| sample_size | int | ✅ | 样本数量 |
| metrics | Dict[str, float] | ✅ | 关键指标 {metric_name: value} |
| variant_b_improvement | float | ✅ | B 组相对 A 组的改善（%） |
| p_value | float | ✅ | 统计显著性 p-value |
| confidence | float | ✅ | 结论置信度 0.0-1.0 |
| conclusion | str | ✅ | supported | rejected | inconclusive |
| actionable_suggestions | List[str] | ✅ | 下游可操作建议列表 |
| affected_factor_ids | List[str] | — | 受影响的因子 ID |
| affected_strategy_ids | List[str] | — | 受影响的策略 ID |
| archived_to_kms | bool | — | 已归档到 KMS |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/experiment_result.py`

### CTR-P1-015 — SynthesizedSignal / 合成交易信号

- **类型**: P1
- **版本**: 1.0
- **提供方**: —
- **消费方**: D_RISK, D_PF_CORE
- **状态**: planned
- **描述**: Signal → Risk/Portfolio 合成交易信号契约。Signal 信号合成引擎聚合多个 FactorSignal 后产出的综合交易信号。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| signal_id | str | ✅ | 全局唯一信号 ID（UUID） |
| symbol | str | ✅ | 标的代码 |
| as_of_timestamp | datetime | ✅ | 信号截面时间（UTC） |
| signal_value | float | ✅ | 标准化合成信号值（-3 到 3） |
| signal_direction | str | ✅ | LONG | SHORT | NEUTRAL |
| confidence | float | ✅ | 合成置信度 0.0-1.0 |
| contributing_factors | Dict[str, float] | ✅ | {factor_id: weight} |
| regime | str | — | 市场状态：trending | mean_reverting | high_volatility | low_volatility |
| suggested_position_pct | float | — | 建议仓位百分比 |
| generation_latency_ms | int | ✅ | 信号合成耗时（毫秒） |
| is_degraded | bool | — | 是否降级信号 |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/synthesized_signal.py`

### CTR-P1-016 — BacktestResult / 回测结果

- **类型**: P1
- **版本**: 1.0
- **提供方**: D_BACKTEST
- **消费方**: D_PF_CORE, D_RISK, D_OPS, D_FRONTEND
- **状态**: planned
- **描述**: D_BACKTEST域产出的标准化回测结果契约。包含绩效指标、交易统计、净值曲线引用。下游Portfolio组合构建层用于策略遴选,Risk风控层用于风险预算校准,Telemetry运维层用于回测任务监控。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| strategy_id | str | ✅ | 策略唯一标识 |
| start_date | datetime | ✅ | 回测起始日期 |
| end_date | datetime | ✅ | 回测结束日期 |
| total_return | float | ✅ | 总收益率(小数,0.15=15%) |
| annual_return | float | ✅ | 年化收益率(小数) |
| sharpe_ratio | float | ✅ | 夏普比率 |
| max_drawdown | float | ✅ | 最大回撤(正数小数,0.2=20%) |
| win_rate | float | ✅ | 胜率(0.0-1.0) |
| trades_count | int | ✅ | 总交易笔数 |
| timestamp | datetime | ✅ | 回测完成时间戳(UTC) |
| overfitting_flag | bool | — | 过拟合标记(true=检测到过拟合) |
| benchmark_symbol | Optional[str] | — | 基准标的代码 |
| idempotency_key | str | ✅ | 幂等键(UUID),防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文 |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/backtest/core/engine_base.py`

### CTR-P1-017 — BacktestRunArtifact / 回测运行产物

- **类型**: P1
- **版本**: 1.0.0
- **提供方**: D_BACKTEST
- **消费方**: D_FRONTEND
- **状态**: planned
- **描述**: 回测运行产物契约，包含回测结果时序数据（equity curve/trade log/tick replay data），用于前端可视化消费。与 CTR-P1-016 BacktestResult（汇总指标）互补——BacktestResult 是标量汇总，BacktestRunArtifact 是时序明细。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| strategy_id | str | ✅ | 策略唯一标识 |
| run_id | str | ✅ | 回测运行 ID,与 BacktestResult.idempotency_key 关联 |
| equity_curve | array[{timestamp: ISO8601, equity: float}] | ✅ | 权益曲线时序数据 |
| trade_log | array[{timestamp: ISO8601, symbol: string, side: string, price: float, quantity: int, commission: float}] | ✅ | 交易记录 |
| tick_replay_data | array[{timestamp: ISO8601, price: float, volume: int}] | — | tick 回放数据(可选,启用 tick 级回放时填充) |
| benchmark_curve | array[{timestamp: ISO8601, value: float}] | — | 基准曲线(可选) |
| drawdown_curve | array[{timestamp: ISO8601, drawdown: float}] | — | 回撤曲线(可选) |
| schema_version | str | ✅ | 契约版本,默认 1.0.0 |

- **物理路径**: `src/zephyr/backtest/io/result_repository.py`

### OCP-002 — StrategyBase + StrategyRegistry / 策略扩展点

- **类型**: unknown
- **版本**: —
- **提供方**: —
- **消费方**: —
- **状态**: design
- **描述**: Portfolio 策略基类契约。所有策略必须继承 StrategyBase，实现 generate_target_weights()，向 StrategyRegistry 注册。 (INV-007: implementors must ensure cross-layer calls carry idempotency_key)

- **物理路径**: `src/zephyr/pf_core/strategy_base.py`

### OCP-003 — BrokerInterface / 券商扩展点

- **类型**: unknown
- **版本**: —
- **提供方**: —
- **消费方**: —
- **状态**: design
- **描述**: Execution 券商接口契约。所有券商适配器必须实现此接口。支持同时接入多家券商，通过 SOR 路由。 (INV-007: implementors must ensure cross-layer calls carry idempotency_key)

- **物理路径**: `src/zephyr/trading/trading_contracts/broker_interface.py`
