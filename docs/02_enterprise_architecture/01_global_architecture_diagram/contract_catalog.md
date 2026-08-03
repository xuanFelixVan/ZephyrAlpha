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

> **文档作用 / Purpose**: 以表格形式展示66个跨层数据契约,用于AI接入新模块时查询"消费了谁的契约、产出什么契约"。

> 本文档由 generate_contract_catalog.py 从 depgraph (PostgreSQL) 自动生成
> 真源: architecture_model/contracts/cross_layer_contracts.yaml
> 最后更新以 git log 为准

## 1. 统计概览

| 指标 | 数量 |
|------|------|
| 契约总数 | 66 |
| P0(核心数据/错误/背压契约) | 0 |
| P1(蓝图签名契约) | 0 |
| 其他 | 66 |
| 已冻结(planned) | 8 |
| 设计中(design) | 1 |

## 2. 契约流向矩阵(Provider → Consumer)

> 行:提供方域 | 列:消费方域 | 单元格:契约ID

| Provider \ Consumer | D_ASHARE_SIGNAL | D_BACKTEST | D_DATA_SEC | D_EX_CORE | D_FACTOR | D_FRONTEND | D_GOV_ENFORCEMENT | D_GOV_SCRIPTS | D_INFRA_OPS | D_INTELLIGENCE | D_MKT_DATA | D_ML_TRAIN | D_OPS | D_PF_CORE | D_RISK | D_SHARED | D_SIGLEGACY | D_SIGQC | D_SIMULATION | D_TRADING | capability.py（fnmatch.fnmatch —— 不支持 brace expansion） | scripts/governance/meta/validate_emergency_bypass_log.py | scripts/governance/meta/validate_script_system_health.py | scripts/governance/run_all.py --depth | scripts/governance/run_all.py --tags | src/zephyr/context-engine/context_budget_tracker.py (get_thresholds_from_yaml) | src/zephyr/context-engine/doc_compressor.py（运行时读取并校验 Immutable Core 字段） | src/zephyr/gov_enforcement/rule_bridge/worktree_lifecycle.py (WorktreeLifecycle v1.0) | src/zephyr/infra_ops/script_system/finding.py | src/zephyr/kb/embedding_migrate.py (load_model_registry) | src/zephyr/orchestrator/execution/trigger_router.py (4 real handlers with fallback) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **D_ASHARE_SIGNAL** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_BACKTEST** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_DATA_SEC** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | CT-004 | — | — | — | — | CT-001 | CT-006 | CT-003 | — | CT-002 | — |
| **D_EX_CORE** | — | — | — | — | — | — | — | — | — | — | — | CTR-006 | — | — | CTR-006 | — | — | — | — | CTR-005, CTR-006 | — | — | — | — | — | — | — | — | — | — | — |
| **D_FACTOR** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_FRONTEND** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_GOV_ENFORCEMENT** | — | — | — | CTR-P1-012 | — | — | CTR-P1-012 | — | — | — | — | — | — | — | CTR-P1-012 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_GOV_SCRIPTS** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | CT-008 | CT-007 | CT-010 | CT-009 | — | — | — | CT-011 | — | — |
| **D_INFRA_OPS** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_INTELLIGENCE** | — | — | — | — | — | — | — | — | — | — | — | CTR-P1-014 | — | — | — | — | — | — | CTR-P1-014 | — | — | — | — | — | — | — | — | — | — | — | CT-005 |
| **D_MKT_DATA** | — | CTR-001 | — | CTR-TRACE-001 | CTR-001, CTR-TRACE-001 | — | — | — | — | — | — | CTR-TRACE-001 | — | CTR-TRACE-001 | CTR-TRACE-001 | — | CTR-001, CTR-TRACE-001 | — | CTR-001 | CTR-TRACE-001 | — | — | — | — | — | — | — | — | — | — | — |
| **D_ML_TRAIN** | — | — | — | — | — | — | — | — | — | — | — | — | — | CTR-P1-004, CTR-P1-005 | — | — | CTR-P1-004, CTR-P1-005 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_OPS** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_PF_CORE** | — | — | — | CTR-004 | — | — | CTR-P1-006 | — | — | — | — | — | — | — | — | — | — | — | — | CTR-P1-006 | — | — | — | — | — | — | — | — | — | — | — |
| **D_RISK** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_SHARED** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_SIGLEGACY** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_SIGQC** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_SIMULATION** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **D_TRADING** | — | — | — | — | — | CTR-P1-009 | CTR-P1-009 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **capability.py（fnmatch.fnmatch —— 不支持 brace expansion）** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **scripts/governance/meta/validate_emergency_bypass_log.py** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **scripts/governance/meta/validate_script_system_health.py** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **scripts/governance/run_all.py --depth** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **scripts/governance/run_all.py --tags** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **src/zephyr/context-engine/context_budget_tracker.py (get_thresholds_from_yaml)** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **src/zephyr/context-engine/doc_compressor.py（运行时读取并校验 Immutable Core 字段）** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **src/zephyr/gov_enforcement/rule_bridge/worktree_lifecycle.py (WorktreeLifecycle v1.0)** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **src/zephyr/infra_ops/script_system/finding.py** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **src/zephyr/kb/embedding_migrate.py (load_model_registry)** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **src/zephyr/orchestrator/execution/trigger_router.py (4 real handlers with fallback)** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |

## 3. 契约详情

### CT-TEL-001 — TelemetryMetrics / 遥测指标采集

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_OPS
- **消费方**: —
- **状态**: unresolved
- **描述**: Telemetry System Telemetry → Config Capacity Assurance / Execution Resource Optimization

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_OPS
- **消费方**: —
- **状态**: unresolved
- **描述**: Telemetry System Telemetry → Config Capacity Assurance / Execution Resource Optimization

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_OPS
- **消费方**: —
- **状态**: unresolved
- **描述**: Telemetry System Telemetry → Config Capacity Assurance / Execution Resource Optimization

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_OPS
- **消费方**: —
- **状态**: unresolved
- **描述**: Telemetry System Telemetry → Config Capacity Assurance / Execution Resource Optimization

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| module_id | str | ✅ | 探针所属模块ID |
| probe_type | str | ✅ | liveness | readiness | healthz |
| status | str | ✅ | healthy | unhealthy | degraded |
| heartbeat_interval_s | int | ✅ | 心跳间隔（秒），默认30 |
| last_heartbeat | datetime | ✅ | 最近心跳时间 |
| details | Dict[str, Any] | — | 探针详情 |
| schema_version | str | — | 契约版本 |

### CTR-001 — NormalizedMarketData / 标准化行情数据

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_MKT_DATA
- **消费方**: D_FACTOR, D_SIGLEGACY, D_SIMULATION, D_BACKTEST
- **状态**: generated
- **描述**: Data Source → Alpha Factor

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: —
- **状态**: unresolved
- **描述**: Alpha Factor → Signal/Risk/Portfolio

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_RISK
- **消费方**: —
- **状态**: unresolved
- **描述**: Risk Management → Portfolio Construction

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_PF_CORE
- **消费方**: D_EX_CORE
- **状态**: design
- **描述**: Portfolio Construction → Trade Execution

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_EX_CORE
- **消费方**: D_TRADING
- **状态**: planned
- **描述**: Trade Execution → Post-Trade Analytics

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_EX_CORE
- **消费方**: D_RISK, D_TRADING, D_ML_TRAIN
- **状态**: planned
- **描述**: OMS / Analytics → Risk Monitor / Strategic Decision

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

### CTR-007 — TargetPortfolio / 目标组合

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_PF_CORE
- **消费方**: —
- **状态**: unresolved
- **描述**: Portfolio Construction → Execution/Position/Reporting

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| portfolio_id | str | ✅ | 组合 ID |
| strategy_id | str | ✅ | 来源策略 ID |
| target_weights | Dict[str, float] | ✅ | 目标权重 {symbol: weight} |
| current_weights | Dict[str, float] | ✅ | 当前权重 {symbol: weight} |
| drift_pct | float | ✅ | 加权权重漂移百分比 |
| risk_limits | RiskLimits | ✅ | 本次优化遵循的风险限额（CTR-003 引用） |
| rebalance_reason | str | ✅ | 再平衡触发原因：drift_threshold/calendar/event/risk_breach |
| created_at | datetime | ✅ | 目标组合创建时间（UTC） |
| idempotency_key | str | ✅ | 幂等键（UUID），防止重复处理 |
| trace_context | Optional[TraceContext] | — | 全链路追踪上下文（CTR-TRACE-001） |
| schema_version | str | — | 契约版本 |

- **物理路径**: `src/zephyr/shared/contracts/target_portfolio.py`

### CTR-BP-001 — BackpressurePause / 背压暂停信号

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: —
- **状态**: unresolved
- **描述**: Factor/Signal 下游 → Data Source 上游（背压逆向）

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: —
- **状态**: unresolved
- **描述**: Factor/Signal 下游 → Data Source 上游（背压逆向）

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: —
- **状态**: unresolved
- **描述**: Factor/Signal 下游 → Data Source 上游（背压逆向）

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_MKT_DATA
- **消费方**: —
- **状态**: unresolved
- **描述**: Data Source → Alpha Factor（错误路径）

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: —
- **状态**: unresolved
- **描述**: Alpha Factor → Signal Generation（错误路径）

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_SIGQC
- **消费方**: —
- **状态**: unresolved
- **描述**: Signal Quality → Risk/Portfolio（降级通知）

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_RISK
- **消费方**: —
- **状态**: unresolved
- **描述**: Risk Management → Portfolio/Execution（拒绝交易）

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_EX_CORE
- **消费方**: —
- **状态**: unresolved
- **描述**: Trade Execution → Portfolio/Analytics（执行失败反馈）

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_SHARED
- **消费方**: —
- **状态**: unresolved
- **描述**: shared/contracts/ → ALL LAYERS（运行时强制校验失败）

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

### CTR-P1-001 — FactorMonitorReport / 因子有效性监控报告

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: —
- **状态**: unresolved
- **描述**: Alpha Factor → Post-trade Analytics

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_FACTOR
- **消费方**: —
- **状态**: unresolved
- **描述**: Factor（宏观因子计算）→ Signal/Portfolio

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_ASHARE_SIGNAL
- **消费方**: —
- **状态**: unresolved
- **描述**: Signal Generation → Portfolio Construction

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_ML_TRAIN
- **消费方**: D_SIGLEGACY, D_PF_CORE
- **状态**: planned
- **描述**: ML Platform → Signal/Portfolio

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| model_id | str | ✅ | 已注册模型 ID |
| model_version | str | ✅ | 模型版本 |
| input_features | Dict[str, float] | ✅ | 特征名 → 特征值 |
| request_id | str | ✅ | UUID，用于异步匹配 |
| idempotency_key | str | ✅ | 幂等键（UUID） |

- **物理路径**: `src/zephyr/shared/contracts/model_serving_request.py`

### CTR-P1-005 — ModelServingResponse / 模型推理响应

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_ML_TRAIN
- **消费方**: D_SIGLEGACY, D_PF_CORE
- **状态**: planned
- **描述**: ML Platform → Signal/Portfolio

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_PF_CORE
- **消费方**: D_TRADING, D_GOV_ENFORCEMENT
- **状态**: planned
- **描述**: Portfolio Construction → Analytics/Compliance

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_EX_CORE
- **消费方**: —
- **状态**: unresolved
- **描述**: Trade Execution → Post-trade Analytics

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_RISK
- **消费方**: —
- **状态**: unresolved
- **描述**: Risk Management → Human-AI Interface

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_TRADING
- **消费方**: D_FRONTEND, D_GOV_ENFORCEMENT
- **状态**: planned
- **描述**: Post-trade Analytics → Frontend/Compliance

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_INFRA_OPS
- **消费方**: —
- **状态**: unresolved
- **描述**: Configuration Management → 全系统

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_RISK
- **消费方**: —
- **状态**: unresolved
- **描述**: Risk Metrics → Portfolio/Analytics/Frontend/Compliance

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_GOV_ENFORCEMENT
- **消费方**: D_RISK, D_EX_CORE, D_GOV_ENFORCEMENT
- **状态**: planned
- **描述**: Compliance Rule Definitions → Risk/Execution/Compliance

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_OPS
- **消费方**: —
- **状态**: unresolved
- **描述**: Telemetry Metrics → 全系统

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_INTELLIGENCE
- **消费方**: D_SIMULATION, D_ML_TRAIN
- **状态**: planned
- **描述**: Experimentation → Research / ML Platform

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_ASHARE_SIGNAL
- **消费方**: —
- **状态**: unresolved
- **描述**: Signal Generation → Risk Management / Portfolio Construction

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

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_BACKTEST
- **消费方**: —
- **状态**: unresolved
- **描述**: L_BACKTEST → Portfolio Portfolio / Risk Risk / Telemetry Ops / Frontend

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

- **类型**: cross_layer
- **版本**: 1.0.0
- **提供方**: D_BACKTEST
- **消费方**: —
- **状态**: unresolved
- **描述**: L_BACKTEST → Frontend Visualization

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

### CTR-TRACE-001 — TraceContext / 全链路追踪上下文

- **类型**: cross_layer
- **版本**: 1.0
- **提供方**: D_MKT_DATA
- **消费方**: D_FACTOR, D_SIGLEGACY, D_RISK, D_PF_CORE, D_EX_CORE, D_TRADING, D_ML_TRAIN
- **状态**: generated
- **描述**: Data Source → Factor → Signal → Portfolio → Execution → Analytics（贯穿全链路）

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

### OCP-002 — StrategyBase + StrategyRegistry / 策略扩展点

- **类型**: cross_layer
- **版本**: —
- **提供方**: D_SHARED
- **消费方**: —
- **状态**: unresolved
- **描述**: —

- **物理路径**: `src/zephyr/pf_core/strategy_base.py`

### OCP-003 — BrokerInterface / 券商扩展点

- **类型**: cross_layer
- **版本**: —
- **提供方**: D_SHARED
- **消费方**: —
- **状态**: unresolved
- **描述**: —

- **物理路径**: `src/zephyr/trading/trading_contracts/broker_interface.py`

### CT-001 — config/context-rules.yaml

- **类型**: declarative
- **版本**: —
- **提供方**: D_DATA_SEC
- **消费方**: src/zephyr/context-engine/context_budget_tracker.py (get_thresholds_from_yaml)
- **状态**: resolved
- **描述**: 15 条上下文管理规则应作为 AI agent session 的运行约束

### CT-002 — config/embedding_model_registry.yaml

- **类型**: declarative
- **版本**: —
- **提供方**: D_DATA_SEC
- **消费方**: src/zephyr/kb/embedding_migrate.py (load_model_registry)
- **状态**: resolved
- **描述**: 从 YAML 加载嵌入模型配置，替代硬编码 KNOWN_MODELS 字典

### CT-003 — config/worktree_state_machine.yaml

- **类型**: declarative
- **版本**: —
- **提供方**: D_DATA_SEC
- **消费方**: src/zephyr/gov_enforcement/rule_bridge/worktree_lifecycle.py (WorktreeLifecycle v1.0)
- **状态**: resolved
- **描述**: WorktreeLifecycle 将消费此状态机定义来管理 worktree 生命周期

### CT-004 — config/capabilities.yaml

- **类型**: declarative
- **版本**: —
- **提供方**: D_DATA_SEC
- **消费方**: capability.py（fnmatch.fnmatch —— 不支持 brace expansion）
- **状态**: resolved_as_not_supported
- **描述**: {a,b} brace expansion glob 语法

### CT-005 — src/zephyr/orchestrator/execution/trigger_router.py + config/trigger_router.yaml

- **类型**: declarative
- **版本**: —
- **提供方**: D_INTELLIGENCE
- **消费方**: src/zephyr/orchestrator/execution/trigger_router.py (4 real handlers with fallback)
- **状态**: resolved
- **描述**: 5 个触发器全部接真实 handler（当前 4 stubs + 1 已兑现）

### CT-006 — config/compression_policy.yaml

- **类型**: declarative
- **版本**: —
- **提供方**: D_DATA_SEC
- **消费方**: src/zephyr/context-engine/doc_compressor.py（运行时读取并校验 Immutable Core 字段）
- **状态**: resolved
- **描述**: 压缩策略 YAML 作为文档压缩的运行时约束（min_chars/max_chars/preserve_* 由 CompressionInvariantError 强制执行）

### CT-007 — MOD-INF-005 §13.1 (script_system/blueprint.md V3.0.0)

- **类型**: declarative
- **版本**: —
- **提供方**: D_GOV_SCRIPTS
- **消费方**: scripts/governance/meta/validate_script_system_health.py
- **状态**: resolved
- **描述**: 脚本系统自我监控——Meta 维度脚本检查系统自身健康状态（6 项自检：run_all.py 可执行性、全脚本可运行性、manifest 一致性、输出格式合规、依赖完整性、磁盘空间）

### CT-008 — MOD-INF-005 §13.2 (script_system/blueprint.md V3.0.0)

- **类型**: declarative
- **版本**: —
- **提供方**: D_GOV_SCRIPTS
- **消费方**: scripts/governance/meta/validate_emergency_bypass_log.py
- **状态**: resolved
- **描述**: 应急回退绕过审计——紧急情况下可绕过脚本系统提交代码，但每次绕过需 Session Log 记录 + 事后审计

### CT-009 — MOD-INF-005 §3.6 + §5.2 (script_system/blueprint.md V3.0.0)

- **类型**: declarative
- **版本**: —
- **提供方**: D_GOV_SCRIPTS
- **消费方**: scripts/governance/run_all.py --tags
- **状态**: resolved
- **描述**: --tags 标签选择参数——允许按标签（Security/Quick/Disruptive/Critical/AI-Generated/Periodic）选择脚本执行

### CT-010 — MOD-INF-005 §5.2 (script_system/blueprint.md V3.0.0)

- **类型**: declarative
- **版本**: —
- **提供方**: D_GOV_SCRIPTS
- **消费方**: scripts/governance/run_all.py --depth
- **状态**: resolved
- **描述**: --depth 验证深度参数——quick（快速扫描<5s）/ full（标准）/ deep（深度含知识分析）三级渐进验证

### CT-011 — MOD-INF-005 §6.5 (script_system/blueprint.md V3.0.0)

- **类型**: declarative
- **版本**: —
- **提供方**: D_GOV_SCRIPTS
- **消费方**: src/zephyr/infra_ops/script_system/finding.py
- **状态**: resolved
- **描述**: Finding Schema 新增 recommendation 字段——MEDIUM+ Finding 包含修复建议（recommendation + recommendation_type + recommended_action）

### AS-CT-DATA-001 — 市场数据→因子引擎（OHLCV/orderbook/tick）

- **类型**: domain_contract
- **版本**: —
- **提供方**: D_FACTOR
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### AS-CT-FACTOR-002 — Code-Dedup-Engine→去重后的因子值（唯一source_key）

- **类型**: domain_contract
- **版本**: —
- **提供方**: D_FACTOR
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### AS-CT-SIGNAL-001 — 信号数据帧→风控引擎

- **类型**: domain_contract
- **版本**: —
- **提供方**: D_ASHARE_SIGNAL
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### AS-CT-VMS-001 — 因子嵌入向量存储（8 collections: signal-embeddings）

- **类型**: domain_contract
- **版本**: —
- **提供方**: D_ASHARE_SIGNAL
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### ME-CT-AB-001 — AB实验全流程：config→traffic_split→gate[eval]→analyst→deploy/rollback

- **类型**: domain_contract
- **版本**: —
- **提供方**: D_ML_TRAIN
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### ME-CT-BACKTEST-001 — 回测实验：ckpt→historical→PnL→Attribution→Report

- **类型**: domain_contract
- **版本**: —
- **提供方**: D_ML_TRAIN
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### ME-CT-CHECKPOINT-001 — 检查点导入（MODEL_CHECKPOINTS→AB/Backtest Experiment）

- **类型**: domain_contract
- **版本**: —
- **提供方**: D_ML_TRAIN
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### ME-CT-FEATURE-001 — 特征向量读取（ChromaDB collections: factor-signals, model-features）

- **类型**: domain_contract
- **版本**: —
- **提供方**: D_ML_TRAIN
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### ME-CT-SHADOW-001 — Shadow Mode：旁路预测→threshold→divergence alert→正式切流

- **类型**: domain_contract
- **版本**: —
- **提供方**: D_ML_TRAIN
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### ME-CT-TRAIN-001 — 训练Pipeline Gate：数据→训练→验证→Sanity→发布

- **类型**: domain_contract
- **版本**: —
- **提供方**: D_ML_TRAIN
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### CTR-009 — ExperimentConfig → D_ML_TRAIN ML Platform

- **类型**: layer_contract
- **版本**: —
- **提供方**: D_SIMULATION
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### CTR-010 — ExperimentMetric → D_RESEARCH Research

- **类型**: layer_contract
- **版本**: —
- **提供方**: D_SIMULATION
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### CTR-011 — ModelCheckpoint ← D_ML_TRAIN ML Platform

- **类型**: layer_contract
- **版本**: —
- **提供方**: D_SIMULATION
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### CTR-012 — ExperimentArtifact → INF-012 Database

- **类型**: layer_contract
- **版本**: —
- **提供方**: D_SIMULATION
- **消费方**: —
- **状态**: unresolved
- **描述**: —

### EXT-DASHBOARD-FLE-001 — 消费 FLE fitness Facade

- **类型**: layer_contract
- **版本**: —
- **提供方**: D_FRONTEND
- **消费方**: —
- **状态**: unresolved
- **描述**: —
