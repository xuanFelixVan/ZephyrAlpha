---
module_id: TIME_SERIES_STORAGE_BP_001
version: 1.0.0
status: Blueprint
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
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
    low DOUBLE