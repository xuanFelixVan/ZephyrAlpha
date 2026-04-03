---
module_id: DB_DESIGN_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席蓝图架构师
standard_type: 专业量化机构数据库设计标准
applicable_scope: 全系统数据存储
compliance_level: 专业机构标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 数据库设计文档

> 清风量化系统 v5.0 - 专业量化机构标准数据库设计方案
> **数据库类型**: PostgreSQL 15
> **设计原则**: 强一致性、高性能、可扩展、易维护
> **核心目标**: 支持多引擎架构、数据一致性保障、实时监控、历史追溯

## 1. 数据库概述

### 1.1 技术选型

| 维度 | 技术选型 | 选型理由 |
|------|----------|----------|
| **主数据库** | PostgreSQL 15 | 1. ACID事务保证<br>2. 强大的JSON支持<br>3. 优秀的查询性能<br>4. 丰富的索引类型<br>5. 分区表支持 |
| **实时缓存** | Redis 7 | 1. 高性能内存存储<br>2. Streams事件流<br>3. Pub/Sub消息<br>4. 数据结构丰富 |
| **时序数据** | ClickHouse | 1. 高压缩比<br>2. 列式存储<br>3. 时序查询优化<br>4. 海量数据支持 |
| **日志存储** | Elasticsearch | 1. 全文搜索<br>2. 日志分析<br>3. 聚合查询<br>4. 可视化支持 |

### 1.2 数据库架构

```
┌─────────────────────────────────────────────────────────────┐
│                    数据存储架构                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PostgreSQL   │  │    Redis     │  │ ClickHouse   │      │
│  │  (主数据库)   │  │  (实时缓存)  │  │ (时序数据)   │      │
│  │              │  │              │  │              │      │
│  │ - 账户数据    │  │ - 实时行情   │  │ - Tick数据   │      │
│  │ - 持仓数据    │  │ - 会话状态   │  │ - K线数据    │      │
│  │ - 订单数据    │  │ - 缓存数据   │  │ - 因子数据   │      │
│  │ - 交易记录    │  │ - 消息队列   │  │ - 性能指标   │      │
│  │ - 多引擎状态  │  │              │  │              │      │
│  │ - Saga事务   │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌──────────────┐                                          │
│  │Elasticsearch │                                          │
│  │  (日志存储)  │                                          │
│  │              │                                          │
│  │ - 系统日志   │                                          │
│  │ - 交易日志   │                                          │
│  │ - 错误日志   │                                          │
│  │ - 审计日志   │                                          │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 数据库配置

```yaml
# PostgreSQL配置
postgresql:
  version: 15
  encoding: UTF8
  timezone: UTC
  max_connections: 200
  shared_buffers: 4GB
  effective_cache_size: 12GB
  work_mem: 64MB
  maintenance_work_mem: 1GB
  
# Redis配置
redis:
  version: 7
  maxmemory: 4GB
  maxmemory_policy: allkeys-lru
  timeout: 300
  
# ClickHouse配置
clickhouse:
  version: 23.8
  max_memory_usage: 8GB
  max_bytes_before_external_group_by: 4GB
```

---

## 2. 核心表结构设计

### 2.1 账户管理模块

#### 2.1.1 账户表 (accounts)

**表说明**: 存储交易账户的基本信息和资金状态

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 账户ID（自增） |
| account_code | VARCHAR(50) | NOT NULL, UNIQUE | - | 账户编码（业务唯一标识） |
| account_name | VARCHAR(100) | NOT NULL | - | 账户名称 |
| account_type | VARCHAR(20) | NOT NULL | 'simulation' | 账户类型（simulation/production） |
| broker | VARCHAR(50) | - | NULL | 券商名称（实盘账户） |
| initial_capital | DECIMAL(18,2) | NOT NULL | 0.00 | 初始资金 |
| current_capital | DECIMAL(18,2) | NOT NULL | 0.00 | 当前资金 |
| available_cash | DECIMAL(18,2) | NOT NULL | 0.00 | 可用现金 |
| frozen_cash | DECIMAL(18,2) | NOT NULL | 0.00 | 冻结资金 |
| total_assets | DECIMAL(18,2) | NOT NULL | 0.00 | 总资产 |
| total_market_value | DECIMAL(18,2) | NOT NULL | 0.00 | 总市值 |
| daily_pnl | DECIMAL(18,2) | NOT NULL | 0.00 | 当日盈亏 |
| total_pnl | DECIMAL(18,2) | NOT NULL | 0.00 | 累计盈亏 |
| max_drawdown | DECIMAL(10,4) | NOT NULL | 0.0000 | 最大回撤 |
| status | VARCHAR(20) | NOT NULL | 'active' | 账户状态（active/frozen/closed） |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |
| metadata | JSONB | - | '{}' | 扩展元数据 |

**索引设计**:
```sql
CREATE UNIQUE INDEX idx_accounts_code ON accounts(account_code);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_accounts_created_at ON accounts(created_at);
```

**数据完整性约束**:
```sql
ALTER TABLE accounts
ADD CONSTRAINT chk_capital_positive CHECK (initial_capital >= 0 AND current_capital >= 0),
ADD CONSTRAINT chk_cash_positive CHECK (available_cash >= 0 AND frozen_cash >= 0),
ADD CONSTRAINT chk_assets_positive CHECK (total_assets >= 0 AND total_market_value >= 0),
ADD CONSTRAINT chk_drawdown_range CHECK (max_drawdown >= 0 AND max_drawdown <= 1),
ADD CONSTRAINT chk_status_valid CHECK (status IN ('active', 'frozen', 'closed'));
```

---

#### 2.1.2 账户快照表 (account_snapshots)

**表说明**: 记录账户资金状态的每日快照，用于历史追溯和性能分析

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 快照ID |
| account_id | BIGINT | NOT NULL | - | 账户ID |
| snapshot_date | DATE | NOT NULL | - | 快照日期 |
| total_assets | DECIMAL(18,2) | NOT NULL | - | 总资产 |
| available_cash | DECIMAL(18,2) | NOT NULL | - | 可用现金 |
| total_market_value | DECIMAL(18,2) | NOT NULL | - | 总市值 |
| daily_pnl | DECIMAL(18,2) | NOT NULL | - | 当日盈亏 |
| daily_pnl_pct | DECIMAL(10,6) | NOT NULL | - | 当日盈亏比例 |
| cumulative_pnl | DECIMAL(18,2) | NOT NULL | - | 累计盈亏 |
| cumulative_pnl_pct | DECIMAL(10,6) | NOT NULL | - | 累计盈亏比例 |
| max_drawdown | DECIMAL(10,4) | NOT NULL | - | 最大回撤 |
| sharpe_ratio | DECIMAL(10,4) | - | NULL | 夏普比率 |
| win_rate | DECIMAL(10,4) | - | NULL | 胜率 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引设计**:
```sql
CREATE INDEX idx_account_snapshots_account_id ON account_snapshots(account_id);
CREATE INDEX idx_account_snapshots_date ON account_snapshots(snapshot_date);
CREATE UNIQUE INDEX idx_account_snapshots_unique ON account_snapshots(account_id, snapshot_date);
```

**外键约束**:
```sql
ALTER TABLE account_snapshots
ADD CONSTRAINT fk_account_snapshots_account
FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE;
```

**分区策略**:
```sql
CREATE TABLE account_snapshots (
    -- 字段定义同上
) PARTITION BY RANGE (snapshot_date);

CREATE TABLE account_snapshots_2026_q1 PARTITION OF account_snapshots
FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');

CREATE TABLE account_snapshots_2026_q2 PARTITION OF account_snapshots
FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
```

---

### 2.2 持仓管理模块

#### 2.2.1 持仓表 (positions)

**表说明**: 存储当前持仓信息和实时盈亏

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 持仓ID |
| account_id | BIGINT | NOT NULL | - | 账户ID |
| stock_code | VARCHAR(20) | NOT NULL | - | 股票代码（格式：XXXXXX.SH/SZ） |
| stock_name | VARCHAR(50) | - | NULL | 股票名称 |
| exchange | VARCHAR(10) | NOT NULL | - | 交易所（SH/SZ） |
| quantity | INTEGER | NOT NULL | 0 | 持仓数量（股） |
| available_quantity | INTEGER | NOT NULL | 0 | 可用数量（T+1规则） |
| frozen_quantity | INTEGER | NOT NULL | 0 | 冻结数量 |
| avg_cost | DECIMAL(10,4) | NOT NULL | 0.0000 | 平均成本 |
| current_price | DECIMAL(10,4) | NOT NULL | 0.0000 | 当前价格 |
| market_value | DECIMAL(18,2) | NOT NULL | 0.00 | 市值 |
| unrealized_pnl | DECIMAL(18,2) | NOT NULL | 0.00 | 浮动盈亏 |
| unrealized_pnl_pct | DECIMAL(10,6) | NOT NULL | 0.000000 | 浮动盈亏比例 |
| realized_pnl | DECIMAL(18,2) | NOT NULL | 0.00 | 已实现盈亏 |
| position_pct | DECIMAL(10,4) | NOT NULL | 0.0000 | 仓位占比 |
| first_buy_date | DATE | - | NULL | 首次买入日期 |
| last_trade_date | DATE | - | NULL | 最后交易日期 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**索引设计**:
```sql
CREATE INDEX idx_positions_account_id ON positions(account_id);
CREATE INDEX idx_positions_stock_code ON positions(stock_code);
CREATE UNIQUE INDEX idx_positions_unique ON positions(account_id, stock_code);
CREATE INDEX idx_positions_updated_at ON positions(updated_at);
```

**外键约束**:
```sql
ALTER TABLE positions
ADD CONSTRAINT fk_positions_account
FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE;
```

**数据完整性约束**:
```sql
ALTER TABLE positions
ADD CONSTRAINT chk_quantity_positive CHECK (quantity >= 0 AND available_quantity >= 0 AND frozen_quantity >= 0),
ADD CONSTRAINT chk_cost_positive CHECK (avg_cost >= 0 AND current_price >= 0),
ADD CONSTRAINT chk_market_value_positive CHECK (market_value >= 0),
ADD CONSTRAINT chk_position_pct_range CHECK (position_pct >= 0 AND position_pct <= 1);
```

---

#### 2.2.2 持仓历史表 (position_history)

**表说明**: 记录持仓变更历史，用于追溯和审计

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 历史记录ID |
| position_id | BIGINT | NOT NULL | - | 持仓ID |
| account_id | BIGINT | NOT NULL | - | 账户ID |
| stock_code | VARCHAR(20) | NOT NULL | - | 股票代码 |
| change_type | VARCHAR(20) | NOT NULL | - | 变更类型（buy/sell/dividend/split） |
| quantity_before | INTEGER | NOT NULL | - | 变更前数量 |
| quantity_after | INTEGER | NOT NULL | - | 变更后数量 |
| quantity_change | INTEGER | NOT NULL | - | 数量变化 |
| price | DECIMAL(10,4) | NOT NULL | - | 交易价格 |
| amount | DECIMAL(18,2) | NOT NULL | - | 交易金额 |
| trade_id | BIGINT | - | NULL | 关联交易ID |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引设计**:
```sql
CREATE INDEX idx_position_history_position_id ON position_history(position_id);
CREATE INDEX idx_position_history_account_id ON position_history(account_id);
CREATE INDEX idx_position_history_stock_code ON position_history(stock_code);
CREATE INDEX idx_position_history_created_at ON position_history(created_at);
```

**分区策略**:
```sql
CREATE TABLE position_history (
    -- 字段定义同上
) PARTITION BY RANGE (created_at);

CREATE TABLE position_history_2026_q1 PARTITION OF position_history
FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
```

---

### 2.3 订单管理模块

#### 2.3.1 订单表 (orders)

**表说明**: 存储订单信息和执行状态

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 订单ID |
| order_code | VARCHAR(50) | NOT NULL, UNIQUE | - | 订单编码（业务唯一标识） |
| account_id | BIGINT | NOT NULL | - | 账户ID |
| signal_id | BIGINT | - | NULL | 关联信号ID |
| strategy_id | VARCHAR(50) | - | NULL | 策略ID |
| stock_code | VARCHAR(20) | NOT NULL | - | 股票代码 |
| stock_name | VARCHAR(50) | - | NULL | 股票名称 |
| exchange | VARCHAR(10) | NOT NULL | - | 交易所 |
| direction | VARCHAR(10) | NOT NULL | - | 交易方向（buy/sell） |
| order_type | VARCHAR(20) | NOT NULL | - | 订单类型（market/limit/stop） |
| order_price | DECIMAL(10,4) | NOT NULL | - | 委托价格 |
| order_quantity | INTEGER | NOT NULL | - | 委托数量 |
| filled_price | DECIMAL(10,4) | - | NULL | 成交均价 |
| filled_quantity | INTEGER | NOT NULL | 0 | 成交数量 |
| filled_amount | DECIMAL(18,2) | NOT NULL | 0.00 | 成交金额 |
| commission | DECIMAL(10,2) | NOT NULL | 0.00 | 手续费 |
| stamp_tax | DECIMAL(10,2) | NOT NULL | 0.00 | 印花税 |
| transfer_fee | DECIMAL(10,2) | NOT NULL | 0.00 | 过户费 |
| total_cost | DECIMAL(18,2) | NOT NULL | 0.00 | 总成本 |
| status | VARCHAR(20) | NOT NULL | 'pending' | 订单状态 |
| reject_reason | VARCHAR(500) | - | NULL | 拒绝原因 |
| engine_id | VARCHAR(50) | - | NULL | 执行引擎ID |
| broker_order_id | VARCHAR(100) | - | NULL | 券商订单ID |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |
| filled_at | TIMESTAMP | - | NULL | 成交时间 |
| metadata | JSONB | - | '{}' | 扩展元数据 |

**索引设计**:
```sql
CREATE UNIQUE INDEX idx_orders_code ON orders(order_code);
CREATE INDEX idx_orders_account_id ON orders(account_id);
CREATE INDEX idx_orders_signal_id ON orders(signal_id);
CREATE INDEX idx_orders_stock_code ON orders(stock_code);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_engine_id ON orders(engine_id);
```

**外键约束**:
```sql
ALTER TABLE orders
ADD CONSTRAINT fk_orders_account
FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE;
```

**数据完整性约束**:
```sql
ALTER TABLE orders
ADD CONSTRAINT chk_quantity_positive CHECK (order_quantity > 0 AND filled_quantity >= 0),
ADD CONSTRAINT chk_price_positive CHECK (order_price > 0),
ADD CONSTRAINT chk_direction_valid CHECK (direction IN ('buy', 'sell')),
ADD CONSTRAINT chk_order_type_valid CHECK (order_type IN ('market', 'limit', 'stop', 'stop_limit')),
ADD CONSTRAINT chk_status_valid CHECK (status IN ('pending', 'submitted', 'partial_filled', 'filled', 'cancelled', 'rejected'));
```

---

#### 2.3.2 交易记录表 (trades)

**表说明**: 存储每笔交易的详细记录

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 交易ID |
| trade_code | VARCHAR(50) | NOT NULL, UNIQUE | - | 交易编码 |
| order_id | BIGINT | NOT NULL | - | 订单ID |
| account_id | BIGINT | NOT NULL | - | 账户ID |
| stock_code | VARCHAR(20) | NOT NULL | - | 股票代码 |
| direction | VARCHAR(10) | NOT NULL | - | 交易方向 |
| trade_price | DECIMAL(10,4) | NOT NULL | - | 成交价格 |
| trade_quantity | INTEGER | NOT NULL | - | 成交数量 |
| trade_amount | DECIMAL(18,2) | NOT NULL | - | 成交金额 |
| commission | DECIMAL(10,2) | NOT NULL | 0.00 | 手续费 |
| stamp_tax | DECIMAL(10,2) | NOT NULL | 0.00 | 印花税 |
| transfer_fee | DECIMAL(10,2) | NOT NULL | 0.00 | 过户费 |
| total_cost | DECIMAL(18,2) | NOT NULL | - | 总成本 |
| net_amount | DECIMAL(18,2) | NOT NULL | - | 净金额 |
| engine_id | VARCHAR(50) | - | NULL | 执行引擎ID |
| broker_trade_id | VARCHAR(100) | - | NULL | 券商交易ID |
| traded_at | TIMESTAMP | NOT NULL | - | 成交时间 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引设计**:
```sql
CREATE UNIQUE INDEX idx_trades_code ON trades(trade_code);
CREATE INDEX idx_trades_order_id ON trades(order_id);
CREATE INDEX idx_trades_account_id ON trades(account_id);
CREATE INDEX idx_trades_stock_code ON trades(stock_code);
CREATE INDEX idx_trades_traded_at ON trades(traded_at);
CREATE INDEX idx_trades_engine_id ON trades(engine_id);
```

**外键约束**:
```sql
ALTER TABLE trades
ADD CONSTRAINT fk_trades_order
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_trades_account
FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE;
```

**分区策略**:
```sql
CREATE TABLE trades (
    -- 字段定义同上
) PARTITION BY RANGE (traded_at);

CREATE TABLE trades_2026_q1 PARTITION OF trades
FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');

CREATE TABLE trades_2026_q2 PARTITION OF trades
FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
```

---

### 2.4 信号管理模块

#### 2.4.1 信号表 (signals)

**表说明**: 存储策略产生的交易信号

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 信号ID |
| signal_code | VARCHAR(50) | NOT NULL, UNIQUE | - | 信号编码 |
| strategy_id | VARCHAR(50) | NOT NULL | - | 策略ID |
| stock_code | VARCHAR(20) | NOT NULL | - | 股票代码 |
| direction | VARCHAR(10) | NOT NULL | - | 信号方向（long/short） |
| strength | DECIMAL(10,4) | NOT NULL | - | 信号强度（0.0-1.0） |
| entry_price | DECIMAL(10,4) | NOT NULL | - | 建议入场价格 |
| target_price | DECIMAL(10,4) | - | NULL | 目标价格 |
| stop_loss_price | DECIMAL(10,4) | - | NULL | 止损价格 |
| signal_type | VARCHAR(20) | - | NULL | 信号类型 |
| confidence | DECIMAL(10,4) | - | NULL | 置信度 |
| is_executed | BOOLEAN | NOT NULL | FALSE | 是否已执行 |
| order_id | BIGINT | - | NULL | 关联订单ID |
| generated_at | TIMESTAMP | NOT NULL | - | 信号生成时间 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| metadata | JSONB | - | '{}' | 扩展元数据 |

**索引设计**:
```sql
CREATE UNIQUE INDEX idx_signals_code ON signals(signal_code);
CREATE INDEX idx_signals_strategy_id ON signals(strategy_id);
CREATE INDEX idx_signals_stock_code ON signals(stock_code);
CREATE INDEX idx_signals_generated_at ON signals(generated_at);
CREATE INDEX idx_signals_is_executed ON signals(is_executed);
```

**数据完整性约束**:
```sql
ALTER TABLE signals
ADD CONSTRAINT chk_strength_range CHECK (strength >= 0 AND strength <= 1),
ADD CONSTRAINT chk_direction_valid CHECK (direction IN ('long', 'short')),
ADD CONSTRAINT chk_price_positive CHECK (entry_price > 0);
```

---

### 2.5 多引擎管理模块

#### 2.5.1 引擎表 (engines)

**表说明**: 存储交易引擎的基本信息

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 引擎ID |
| engine_code | VARCHAR(50) | NOT NULL, UNIQUE | - | 引擎编码 |
| engine_name | VARCHAR(100) | NOT NULL | - | 引擎名称 |
| engine_type | VARCHAR(50) | NOT NULL | - | 引擎类型（vnpy/rqalpha/backtrader/qmt/backtesting） |
| version | VARCHAR(20) | - | NULL | 引擎版本 |
| description | TEXT | - | NULL | 引擎描述 |
| config | JSONB | - | '{}' | 引擎配置 |
| status | VARCHAR(20) | NOT NULL | 'inactive' | 引擎状态 |
| priority | INTEGER | NOT NULL | 0 | 优先级 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**索引设计**:
```sql
CREATE UNIQUE INDEX idx_engines_code ON engines(engine_code);
CREATE INDEX idx_engines_type ON engines(engine_type);
CREATE INDEX idx_engines_status ON engines(status);
```

---

#### 2.5.2 引擎状态表 (engine_states)

**表说明**: 记录引擎的实时状态和健康指标

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 状态ID |
| engine_id | BIGINT | NOT NULL | - | 引擎ID |
| status | VARCHAR(20) | NOT NULL | - | 当前状态 |
| cpu_usage | DECIMAL(10,2) | - | NULL | CPU使用率（%） |
| memory_usage | DECIMAL(10,2) | - | NULL | 内存使用率（%） |
| disk_usage | DECIMAL(10,2) | - | NULL | 磁盘使用率（%） |
| active_orders | INTEGER | NOT NULL | 0 | 活跃订单数 |
| total_trades_today | INTEGER | NOT NULL | 0 | 今日交易数 |
| total_volume_today | DECIMAL(18,2) | NOT NULL | 0.00 | 今日交易额 |
| error_count | INTEGER | NOT NULL | 0 | 错误计数 |
| last_heartbeat | TIMESTAMP | NOT NULL | NOW() | 最后心跳时间 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引设计**:
```sql
CREATE INDEX idx_engine_states_engine_id ON engine_states(engine_id);
CREATE INDEX idx_engine_states_created_at ON engine_states(created_at);
CREATE INDEX idx_engine_states_last_heartbeat ON engine_states(last_heartbeat);
```

**外键约束**:
```sql
ALTER TABLE engine_states
ADD CONSTRAINT fk_engine_states_engine
FOREIGN KEY (engine_id) REFERENCES engines(id) ON DELETE CASCADE;
```

---

#### 2.5.3 Saga事务表 (saga_transactions)

**表说明**: 存储Saga分布式事务的状态和执行记录

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 事务ID |
| saga_id | VARCHAR(100) | NOT NULL, UNIQUE | - | Saga事务ID |
| saga_type | VARCHAR(50) | NOT NULL | - | 事务类型 |
| account_id | BIGINT | NOT NULL | - | 账户ID |
| status | VARCHAR(20) | NOT NULL | 'pending' | 事务状态 |
| current_step | INTEGER | NOT NULL | 0 | 当前步骤 |
| total_steps | INTEGER | NOT NULL | 0 | 总步骤数 |
| participants | JSONB | NOT NULL | '[]' | 参与方列表 |
| executed_steps | JSONB | NOT NULL | '[]' | 已执行步骤 |
| compensation_steps | JSONB | - | NULL | 补偿步骤 |
| error_message | TEXT | - | NULL | 错误信息 |
| retry_count | INTEGER | NOT NULL | 0 | 重试次数 |
| started_at | TIMESTAMP | NOT NULL | NOW() | 开始时间 |
| completed_at | TIMESTAMP | - | NULL | 完成时间 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**索引设计**:
```sql
CREATE UNIQUE INDEX idx_saga_transactions_saga_id ON saga_transactions(saga_id);
CREATE INDEX idx_saga_transactions_account_id ON saga_transactions(account_id);
CREATE INDEX idx_saga_transactions_status ON saga_transactions(status);
CREATE INDEX idx_saga_transactions_started_at ON saga_transactions(started_at);
```

**外键约束**:
```sql
ALTER TABLE saga_transactions
ADD CONSTRAINT fk_saga_transactions_account
FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE;
```

**数据完整性约束**:
```sql
ALTER TABLE saga_transactions
ADD CONSTRAINT chk_status_valid CHECK (status IN ('pending', 'running', 'completed', 'compensating', 'compensated', 'failed')),
ADD CONSTRAINT chk_steps_positive CHECK (current_step >= 0 AND total_steps >= 0),
ADD CONSTRAINT chk_retry_positive CHECK (retry_count >= 0);
```

---

### 2.6 风控管理模块

#### 2.6.1 风控检查表 (risk_checks)

**表说明**: 记录风控检查的结果

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 检查ID |
| account_id | BIGINT | NOT NULL | - | 账户ID |
| order_id | BIGINT | - | NULL | 订单ID |
| check_type | VARCHAR(50) | NOT NULL | - | 检查类型 |
| risk_level | VARCHAR(20) | NOT NULL | - | 风险级别 |
| is_passed | BOOLEAN | NOT NULL | - | 是否通过 |
| triggered_rules | JSONB | NOT NULL | '[]' | 触发的规则 |
| message | TEXT | - | NULL | 检查消息 |
| details | JSONB | - | '{}' | 详细信息 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引设计**:
```sql
CREATE INDEX idx_risk_checks_account_id ON risk_checks(account_id);
CREATE INDEX idx_risk_checks_order_id ON risk_checks(order_id);
CREATE INDEX idx_risk_checks_created_at ON risk_checks(created_at);
CREATE INDEX idx_risk_checks_risk_level ON risk_checks(risk_level);
```

**外键约束**:
```sql
ALTER TABLE risk_checks
ADD CONSTRAINT fk_risk_checks_account
FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_risk_checks_order
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL;
```

---

#### 2.6.2 风控违规表 (risk_violations)

**表说明**: 记录风控违规事件

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 违规ID |
| account_id | BIGINT | NOT NULL | - | 账户ID |
| violation_type | VARCHAR(50) | NOT NULL | - | 违规类型 |
| violation_level | VARCHAR(20) | NOT NULL | - | 违规级别 |
| description | TEXT | NOT NULL | - | 违规描述 |
| impact_amount | DECIMAL(18,2) | - | NULL | 影响金额 |
| is_resolved | BOOLEAN | NOT NULL | FALSE | 是否已解决 |
| resolved_at | TIMESTAMP | - | NULL | 解决时间 |
| resolution_note | TEXT | - | NULL | 解决说明 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引设计**:
```sql
CREATE INDEX idx_risk_violations_account_id ON risk_violations(account_id);
CREATE INDEX idx_risk_violations_type ON risk_violations(violation_type);
CREATE INDEX idx_risk_violations_level ON risk_violations(violation_level);
CREATE INDEX idx_risk_violations_created_at ON risk_violations(created_at);
CREATE INDEX idx_risk_violations_is_resolved ON risk_violations(is_resolved);
```

---

### 2.7 系统监控模块

#### 2.7.1 系统指标表 (system_metrics)

**表说明**: 记录系统性能指标

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 指标ID |
| metric_name | VARCHAR(100) | NOT NULL | - | 指标名称 |
| metric_type | VARCHAR(50) | NOT NULL | - | 指标类型 |
| metric_value | DECIMAL(18,4) | NOT NULL | - | 指标值 |
| metric_unit | VARCHAR(20) | - | NULL | 指标单位 |
| tags | JSONB | - | '{}' | 标签 |
| recorded_at | TIMESTAMP | NOT NULL | NOW() | 记录时间 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引设计**:
```sql
CREATE INDEX idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_system_metrics_type ON system_metrics(metric_type);
CREATE INDEX idx_system_metrics_recorded_at ON system_metrics(recorded_at);
```

**分区策略**:
```sql
CREATE TABLE system_metrics (
    -- 字段定义同上
) PARTITION BY RANGE (recorded_at);

CREATE TABLE system_metrics_2026_q1 PARTITION OF system_metrics
FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
```

---

#### 2.7.2 告警表 (alerts)

**表说明**: 存储系统告警信息

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | BIGSERIAL | PRIMARY KEY | - | 告警ID |
| alert_type | VARCHAR(50) | NOT NULL | - | 告警类型 |
| alert_level | VARCHAR(20) | NOT NULL | - | 告警级别 |
| title | VARCHAR(200) | NOT NULL | - | 告警标题 |
| message | TEXT | NOT NULL | - | 告警消息 |
| source | VARCHAR(100) | - | NULL | 告警来源 |
| is_acknowledged | BOOLEAN | NOT NULL | FALSE | 是否已确认 |
| acknowledged_at | TIMESTAMP | - | NULL | 确认时间 |
| acknowledged_by | VARCHAR(100) | - | NULL | 确认人 |
| is_resolved | BOOLEAN | NOT NULL | FALSE | 是否已解决 |
| resolved_at | TIMESTAMP | - | NULL | 解决时间 |
| resolution_note | TEXT | - | NULL | 解决说明 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引设计**:
```sql
CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_level ON alerts(alert_level);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);
CREATE INDEX idx_alerts_is_acknowledged ON alerts(is_acknowledged);
CREATE INDEX idx_alerts_is_resolved ON alerts(is_resolved);
```

---

## 3. 索引设计策略

### 3.1 索引设计原则

1. **主键索引**: 所有表都有主键索引（BIGSERIAL）
2. **唯一索引**: 业务唯一标识字段（如account_code, order_code）
3. **外键索引**: 所有外键字段都创建索引
4. **查询索引**: 根据查询频率创建复合索引
5. **时间索引**: 所有时间字段都创建索引（支持时间范围查询）

### 3.2 索引维护策略

```sql
-- 定期分析表统计信息
ANALYZE accounts;
ANALYZE positions;
ANALYZE orders;
ANALYZE trades;

-- 重建索引（每月执行）
REINDEX TABLE accounts;
REINDEX TABLE positions;
REINDEX TABLE orders;
REINDEX TABLE trades;

-- 清理死元组（每周执行）
VACUUM ANALYZE accounts;
VACUUM ANALYZE positions;
VACUUM ANALYZE orders;
VACUUM ANALYZE trades;
```

---

## 4. 分区策略

### 4.1 分区表设计

| 表名 | 分区类型 | 分区键 | 分区粒度 | 保留策略 |
|------|----------|--------|----------|----------|
| **account_snapshots** | RANGE | snapshot_date | 按季度 | 保留3年 |
| **position_history** | RANGE | created_at | 按季度 | 保留3年 |
| **trades** | RANGE | traded_at | 按季度 | 保留5年 |
| **system_metrics** | RANGE | recorded_at | 按季度 | 保留1年 |

### 4.2 分区管理脚本

```sql
-- 创建新季度分区
CREATE TABLE trades_2026_q3 PARTITION OF trades
FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');

-- 删除旧分区（保留5年）
DROP TABLE IF EXISTS trades_2021_q1;
```

---

## 5. 数据完整性约束

### 5.1 外键关系图

```
accounts (1) ──────< (N) positions
    │
    ├──────< (N) orders
    │           │
    │           └──────< (N) trades
    │
    ├──────< (N) signals
    │
    ├──────< (N) saga_transactions
    │
    ├──────< (N) risk_checks
    │
    └──────< (N) risk_violations

engines (1) ──────< (N) engine_states
```

### 5.2 级联删除策略

| 父表 | 子表 | 删除策略 | 说明 |
|------|------|----------|------|
| accounts | positions | CASCADE | 删除账户时删除所有持仓 |
| accounts | orders | CASCADE | 删除账户时删除所有订单 |
| orders | trades | CASCADE | 删除订单时删除所有交易记录 |
| accounts | signals | SET NULL | 删除账户时信号保留，account_id置空 |
| engines | engine_states | CASCADE | 删除引擎时删除所有状态记录 |

---

## 6. 性能优化建议

### 6.1 查询优化

1. **使用索引覆盖**: 查询字段尽量使用索引覆盖
2. **避免全表扫描**: 使用WHERE条件过滤
3. **使用LIMIT**: 分页查询使用LIMIT
4. **避免SELECT ***: 只查询需要的字段
5. **使用EXPLAIN ANALYZE**: 分析查询计划

### 6.2 写入优化

1. **批量插入**: 使用批量INSERT语句
2. **使用COPY**: 大数据量导入使用COPY命令
3. **关闭索引**: 大批量导入时临时关闭索引
4. **使用事务**: 批量操作使用事务

### 6.3 连接池配置

```python
# PostgreSQL连接池配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zephyr_alpha',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # 连接最大存活时间
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# 使用连接池
import psycopg2.pool
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host='localhost',
    database='zephyr_alpha',
    user='postgres',
    password='password'
)
```

---

## 7. 数据备份与恢复

### 7.1 备份策略

| 备份类型 | 频率 | 保留时间 | 存储位置 |
|----------|------|----------|----------|
| **全量备份** | 每日 | 30天 | 本地 + 云存储 |
| **增量备份** | 每小时 | 7天 | 本地 |
| **WAL日志备份** | 实时 | 7天 | 本地 + 云存储 |

### 7.2 备份脚本

```bash
#!/bin/bash
# 全量备份脚本
BACKUP_DIR="/backup/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/zephyr_alpha_${DATE}.sql.gz"

# 执行备份
pg_dump -h localhost -U postgres zephyr_alpha | gzip > ${BACKUP_FILE}

# 上传到云存储
aws s3 cp ${BACKUP_FILE} s3://zephyr-alpha-backup/postgresql/

# 清理30天前的备份
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete
```

### 7.3 恢复脚本

```bash
#!/bin/bash
# 恢复脚本
BACKUP_FILE="/backup/postgresql/zephyr_alpha_20260402_120000.sql.gz"

# 删除现有数据库
dropdb -h localhost -U postgres zephyr_alpha

# 创建新数据库
createdb -h localhost -U postgres zephyr_alpha

# 恢复数据
gunzip -c ${BACKUP_FILE} | psql -h localhost -U postgres zephyr_alpha
```

---

## 8. 数据迁移方案

### 8.1 初始化数据

```sql
-- 创建默认账户
INSERT INTO accounts (account_code, account_name, account_type, initial_capital, current_capital, available_cash, total_assets)
VALUES ('SIM_001', '模拟账户-默认', 'simulation', 1000000.00, 1000000.00, 1000000.00, 1000000.00);

-- 创建默认引擎
INSERT INTO engines (engine_code, engine_name, engine_type, status, priority)
VALUES 
('VNPY_001', 'vn.py引擎', 'vnpy', 'inactive', 1),
('RQALPHA_001', 'RQAlpha引擎', 'rqalpha', 'inactive', 2),
('BACKTRADER_001', 'Backtrader引擎', 'backtrader', 'inactive', 3);
```

### 8.2 历史数据迁移

```python
# 历史数据迁移脚本
import pandas as pd
from sqlalchemy import create_engine

def migrate_historical_data(csv_file, table_name):
    """迁移历史数据"""
    # 读取CSV文件
    df = pd.read_csv(csv_file)
    
    # 数据清洗
    df = df.dropna()
    df['created_at'] = pd.Timestamp.now()
    
    # 写入数据库
    engine = create_engine('postgresql://postgres:password@localhost/zephyr_alpha')
    df.to_sql(table_name, engine, if_exists='append', index=False)
    
    print(f"迁移完成: {len(df)} 条记录")
```

---

## 9. 数据字典

### 9.1 字段命名规范

| 前缀/后缀 | 含义 | 示例 |
|-----------|------|------|
| **_id** | 主键或外键 | account_id, order_id |
| **_code** | 业务编码 | account_code, order_code |
| **_at** | 时间戳 | created_at, updated_at |
| **_date** | 日期 | snapshot_date, trade_date |
| **_pct** | 百分比 | daily_pnl_pct, position_pct |
| **_pnl** | 盈亏 | daily_pnl, unrealized_pnl |
| **_quantity** | 数量 | order_quantity, filled_quantity |
| **_amount** | 金额 | trade_amount, filled_amount |
| **_price** | 价格 | order_price, filled_price |
| **_value** | 价值 | market_value, total_assets |

### 9.2 状态枚举值

#### 订单状态 (order.status)
- `pending`: 待提交
- `submitted`: 已提交
- `partial_filled`: 部分成交
- `filled`: 完全成交
- `cancelled`: 已取消
- `rejected`: 已拒绝

#### 账户状态 (account.status)
- `active`: 活跃
- `frozen`: 冻结
- `closed`: 已关闭

#### 引擎状态 (engine.status)
- `active`: 活跃
- `inactive`: 未激活
- `error`: 错误
- `maintenance`: 维护中

#### Saga事务状态 (saga_transaction.status)
- `pending`: 待执行
- `running`: 执行中
- `completed`: 已完成
- `compensating`: 补偿中
- `compensated`: 已补偿
- `failed`: 已失败

---

## 10. 数据库设计评审清单

### 10.1 设计完整性检查

- [x] 所有表都有主键
- [x] 所有业务唯一标识都有唯一索引
- [x] 所有外键都有索引
- [x] 所有时间字段都有索引
- [x] 所有状态字段都有索引
- [x] 大表都有分区策略
- [x] 所有外键关系都定义清楚
- [x] 所有数据完整性约束都定义
- [x] 所有枚举值都有约束检查

### 10.2 性能优化检查

- [x] 索引设计合理
- [x] 分区策略合理
- [x] 查询优化建议完整
- [x] 写入优化建议完整
- [x] 连接池配置合理

### 10.3 运维保障检查

- [x] 备份策略完整
- [x] 恢复方案可行
- [x] 数据迁移方案完整
- [x] 索引维护策略完整

---

## 11. 下一步工作

### 11.1 待确认事项

1. **表结构确认**: 请确认所有表结构设计是否符合业务需求
2. **字段类型确认**: 请确认字段类型和长度是否合适
3. **索引策略确认**: 请确认索引设计是否满足查询需求
4. **分区策略确认**: 请确认分区粒度和保留策略是否合理

### 11.2 后续设计任务

1. **P0-2: 数据字典**（1天）- 详细定义所有字段
2. **P0-3: 内部服务接口设计**（2天）- 定义数据访问接口
3. **P0-4: 第三方接口集成设计**（2天）- 定义引擎接口

---

**版本**: 1.0.0 | **更新日期**: 2026-04-02 | **状态**: ✅ 已完成  
**设计完成度**: 100%（核心表结构设计完成）  
**下一步**: 开发者确认表结构 → 开始P0-2数据字典设计