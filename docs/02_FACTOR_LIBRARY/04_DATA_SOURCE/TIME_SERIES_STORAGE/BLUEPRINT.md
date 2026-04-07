﻿---
module_id: TIME_SERIES_STORAGE_BP_001
version: 1.0.0
status: Blueprint
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
responsibility: 时序数据存储架构设计与TimescaleDB集成
standard_type: 模块蓝图
applicable_scope: 高性能时序存储系统
compliance_level: 专业标准
parent_document: ../INDEX.md
dependencies:
- QuestDB
- InfluxDB
- TimescaleDB
---


# 高性能时序存储系统蓝图

> **核心职责**: 高性能时序存储系统蓝图的定义和实现
> **职责边界**: 
> - ✅ 本文档负责：蓝图设计和架构规划相关内容
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: 高性能时序存储系统设计蓝图
- 定义时序数据库架构和选型
- 说明Tick数据存储和查询方案
- 提供高性能写入和检索策略

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 数据源索引 | [../INDEX.md](../INDEX.md) | 上级索引 | 数据源模块总索引 |
| 数据管道 | [../07_DATA_PIPELINE/](../07_DATA_PIPELINE/) | 数据流 | 数据管道设计 |

**职责边界**:
- 本文档负责: 时序数据存储架构设计
- 本文档不负责: 具体数据采集实现（由各数据源适配器负责）

> 清风量化系统 v5.4 - 高性能时序存储模块
> **优先级**: P1级（重要）
> **实施周期**: 1周
> **开源方案**: QuestDB (主) + DuckDB (分析)

---

## 1. 概述

### 1.1 定位与目标

**核心定位**: 为量化交易提供高性能时序数据存储引擎

**业务价值**:
- 支持每秒500万行Tick数据写入
- 毫秒级历史数据查询
- ASOF JOIN优化交易匹配
- 降低存储成本70%

### 1.2 版本信息

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-04-06 | 初始蓝图设计 |

---

## 2. 架构设计

### 2.1 Layer定位

```
Layer 0: 数据源层
├── 数据采集 (iFind/Baostock/AKShare)
├── 时序存储 (QuestDB) ← 本模块
├── 数据处理 (dbt/Great Expectations)
└── 数据服务 (FastAPI/Redis)
```

### 2.2 技术选型对比

| 数据库 | 写入性能 | 查询性能 | SQL支持 | 个人适用性 |
|--------|----------|----------|---------|-----------|
| **QuestDB** | 500万行/秒 | 极快 | 扩展SQL | ⭐⭐⭐⭐⭐ |
| InfluxDB | 100万行/秒 | 快 | Flux | ⭐⭐⭐⭐ |
| TimescaleDB | 50万行/秒 | 快 | 标准SQL | ⭐⭐⭐⭐ |
| ClickHouse | 100万行/秒 | 极快 | 标准SQL | ⭐⭐⭐ |

**推荐方案**: QuestDB (主存储) + DuckDB (分析)

### 2.3 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                   时序存储架构                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ 数据源       │    │ 写入层       │    │ 存储层       │ │
│  │ iFind        │    │ ILP协议      │    │ QuestDB      │ │
│  │ Baostock     │───▶│ 批量写入     │───▶│ 列式存储     │ │
│  │ AKShare      │    │ 去重索引     │    │ 分区表       │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                   │                    │          │
│         └───────────────────┴────────────────────┘          │
│                            │                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 查询层                                                │  │
│  │ • SQL查询 • ASOF JOIN • 时间窗口函数 • 降采样        │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 导出层                                                │  │
│  │ • Parquet导出 • CSV导出 • API查询 • DuckDB集成       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 技术实现

### 3.1 核心组件

#### QuestDB配置

```python
from questdb.ingress import Sender, TimestampNanos

class QuestDBManager:
    def __init__(self, host: str = "localhost", port: int = 9009):
        self.host = host
        self.port = port
        self.sender = Sender(host, port)
        
    async def write_tick_data(
        self,
        table: str,
        symbol: str,
        timestamp: int,
        price: float,
        volume: float,
        bid_price: float = None,
        ask_price: float = None
    ):
        self.sender.table(table)\
            .symbol('symbol', symbol)\
            .column('price', price)\
            .column('volume', volume)
        
        if bid_price:
            self.sender.column('bid_price', bid_price)
        if ask_price:
            self.sender.column('ask_price', ask_price)
            
        self.sender.at(TimestampNanos(timestamp))
        self.sender.flush()
    
    async def batch_write_ticks(
        self,
        table: str,
        ticks: list
    ):
        for tick in ticks:
            await self.write_tick_data(
                table=table,
                symbol=tick['symbol'],
                timestamp=tick['timestamp'],
                price=tick['price'],
                volume=tick['volume']
            )
```

#### ASOF JOIN查询

```sql
SELECT 
    t.timestamp,
    t.symbol,
    t.price AS trade_price,
    t.volume,
    ob.bid_price,
    ob.ask_price,
    ob.bid_volume,
    ob.ask_volume
FROM trades t
ASOF JOIN orderbook ob
ON t.symbol = ob.symbol
AND t.timestamp >= ob.timestamp
WHERE t.timestamp IN '2024-03-03'
AND t.symbol = '000001.SZ';
```

### 3.2 数据模型

#### Tick数据表

```sql
CREATE TABLE IF NOT EXISTS ticks (
    timestamp TIMESTAMP,
    symbol SYMBOL,
    trade_date DATE,
    price DOUBLE,
    volume DOUBLE,
    turnover DOUBLE,
    bid_price1 DOUBLE,
    ask_price1 DOUBLE,
    bid_volume1 DOUBLE,
    ask_volume1 DOUBLE,
    trade_type SYMBOL
) TIMESTAMP(timestamp)
PARTITION BY DAY;
```

#### K线数据表

```sql
CREATE TABLE IF NOT EXISTS candles (
    timestamp TIMESTAMP,
    symbol SYMBOL,
    trade_date DATE,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume DOUBLE,
    turnover DOUBLE,
    vwap DOUBLE
) TIMESTAMP(timestamp)
PARTITION BY MONTH;
```

### 3.3 性能优化

#### 写入优化

```python
class TickDataWriter:
    def __init__(self, questdb_host: str, batch_size: int = 10000):
        self.sender = Sender(questdb_host, 9009)
        self.batch_size = batch_size
        self.buffer = []
        
    async def write_with_buffer(self, tick: dict):
        self.buffer.append(tick)
        if len(self.buffer) >= self.batch_size:
            await self._flush_buffer()
            
    async def _flush_buffer(self):
        for tick in self.buffer:
            self.sender.table('ticks')\
                .symbol('symbol', tick['symbol'])\
                .column('price', tick['price'])\
                .column('volume', tick['volume'])\
                .at(TimestampNanos(tick['timestamp']))
        self.sender.flush()
        self.buffer = []
```

#### 查询优化

```sql
SELECT 
    timestamp,
    symbol,
    first(price) AS open,
    max(price) AS high,
    min(price) AS low,
    last(price) AS close,
    sum(volume) AS volume
FROM ticks
WHERE timestamp IN '2024-03-03'
AND symbol = '000001.SZ'
SAMPLE BY 1m;
```

---

## 4. 数据流设计

### 4.1 数据写入流程

```
数据源 → ILP协议 → QuestDB → 分区存储
    │         │         │          │
    └─────────┴─────────┴──────────┘
              实时写入
              去重索引
              自动分区
```

### 4.2 数据查询流程

```
应用层 → SQL查询 → QuestDB → 结果返回
    │        │         │          │
    └────────┴─────────┴──────────┘
           ASOF JOIN
           时间窗口
           降采样
```

---

## 5. 实施路径

### Phase 1: 基础部署 (3天)

| 任务 | 开源方案 | 工作量 |
|------|----------|--------|
| QuestDB安装配置 | Docker | 0.5天 |
| Tick数据表创建 | SQL | 0.5天 |
| 写入接口开发 | Python SDK | 1天 |
| 基础查询测试 | SQL | 1天 |

### Phase 2: 性能优化 (2天)

| 任务 | 开源方案 | 工作量 |
|------|----------|--------|
| 批量写入优化 | ILP协议 | 0.5天 |
| ASOF JOIN测试 | SQL | 0.5天 |
| Parquet导出 | QuestDB | 0.5天 |
| DuckDB集成 | DuckDB | 0.5天 |

### Phase 3: 生产部署 (2天)

| 任务 | 开源方案 | 工作量 |
|------|----------|--------|
| 监控告警 | Prometheus | 0.5天 |
| 备份策略 | 快照 | 0.5天 |
| API封装 | FastAPI | 0.5天 |
| 文档完善 | Markdown | 0.5天 |

---

## 6. 开源方案详情

### 6.1 QuestDB

| 属性 | 值 |
|------|-----|
| GitHub | https://github.com/questdb/questdb |
| Stars | 14k+ |
| 许可证 | Apache 2.0 |
| 语言 | Java/C++ |
| 特点 | 高性能时序数据库 |

**核心特性**:
- 每秒500万行写入
- SQL兼容
- ASOF JOIN优化
- 原生Parquet支持
- 零依赖部署

### 6.2 DuckDB集成

```python
import duckdb

con = duckdb.connect()

con.execute("""
    CREATE VIEW ticks AS
    SELECT * FROM read_parquet('ticks/*.parquet')
""")

result = con.execute("""
    SELECT 
        symbol,
        avg(close) as avg_close,
        sum(volume) as total_volume
    FROM ticks
    WHERE trade_date = '2024-03-03'
    GROUP BY symbol
""").fetchdf()
```

---

## 7. 维护成本评估

| 维护项 | 频率 | 工作量 |
|--------|------|--------|
| 数据库监控 | 每日 | 5分钟 |
| 存储空间管理 | 每周 | 30分钟 |
| 性能调优 | 每月 | 1小时 |
| 版本升级 | 每季度 | 2小时 |

**总维护成本**: 约 **1小时/月**

---

## 8. 风险评估

| 风险 | 级别 | 缓解措施 |
|------|------|----------|
| 存储空间不足 | P2 | 分区清理+冷数据归档 |
| 写入延迟 | P2 | 批量写入+异步处理 |
| 查询超时 | P2 | 索引优化+查询限制 |
| 数据丢失 | P1 | 定期快照+增量备份 |

---

## 9. 质量指标

| 指标 | 目标值 | 监控方式 |
|------|--------|----------|
| 写入延迟 | <10ms | Prometheus |
| 查询延迟 | <100ms | Prometheus |
| 数据完整性 | 99.99% | 校验脚本 |
| 存储效率 | >70% | 监控面板 |

---

**版本**: 1.0 | **状态**: Blueprint

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
---

## 10. 文档治理

### 10.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Time Series Storage Bp
- **模块ID**: TIME_SERIES_STORAGE_BP_001
- **蓝图文档**: [BLUEPRINT.md](02_FACTOR_LIBRARY\04_DATA_SOURCE\TIME_SERIES_STORAGE\BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: 高性能时序存储系统
- **状态**: Blueprint
```

### 10.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Time Series Storage Bp** | 高性能时序存储系统 | **核心模块** |

### 10.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Blueprint
