---
module_id: CLICKHOUSE_INTEGRATION_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 大规模历史数据存储
  - 列式数据查询
  - 数据聚合分析
layer: "Layer 1 (数据预处理层)"
---

# ClickHouse列式存储集成蓝图

> **核心职责**: 大规模历史数据的存储、查询和分析，专注于OLAP场景
> **职责边界**: 
> - ✅ 本模块负责：大规模历史数据存储、列式聚合查询、物化视图、数据压缩
> - ❌ 本模块不负责：实时数据存储（TimescaleDB）、缓存（Redis）

## 核心定位

**单一职责**: 大规模历史数据的存储、查询和分析，专注于OLAP场景

### 职责边界

| 负责 | 不负责 |
|------|--------|
| ✅ 历史行情数据存储（10年+） | ❌ 实时数据存储 |
| ✅ 列式聚合分析 | ❌ 事务处理 |
| ✅ 物化视图预计算 | ❌ 高频写入 |
| ✅ 数据压缩存储 | ❌ 实时查询 |
| ✅ 复杂分析查询 | ❌ 数据订阅 |

---

## 1. 技术选型

### 1.1 为什么选择ClickHouse

| 特性 | ClickHouse | Apache Doris | Apache Druid |
|------|------------|--------------|--------------|
| 查询性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 压缩能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 部署复杂度 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 学习曲线 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Python支持 | ✅ clickhouse-driver | ✅ pydoris | ✅ pydruid |
| 单机适用 | ✅ 支持 | ✅ 支持 | ❌ 需集群 |
| 社区活跃度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **推荐指数** | **⭐⭐⭐⭐⭐** | ⭐⭐⭐⭐ | ⭐⭐⭐ |

### 1.2 核心优势

1. **极致性能**: 单机每秒处理数亿行数据
2. **高压缩比**: 列式存储压缩比可达10:1
3. **SQL兼容**: 支持标准SQL语法
4. **单机友好**: 个人开发场景最佳选择

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    ClickHouse集成架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ 数据导入层   │    │ 数据存储层   │    │ 数据查询层   │     │
│  │              │    │              │    │              │     │
│  │ • 批量导入   │    │ • MergeTree  │    │ • 聚合查询   │     │
│  │ • 增量导入   │    │ • 分区策略   │    │ • 物化视图   │     │
│  │ • 数据归档   │    │ • TTL策略    │    │ • 分析函数   │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                   │                    │              │
│         └───────────────────┴────────────────────┘              │
│                            │                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    数据分层策略                          │   │
│  │  • 热数据: TimescaleDB (30天内)                          │   │
│  │  • 温数据: ClickHouse (1年内)                            │   │
│  │  • 冷数据: 对象存储 (归档)                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 数据模型设计

```sql
-- 历史行情数据表
CREATE TABLE historical_klines (
    date Date,
    symbol LowCardinality(String),
    interval LowCardinality(String),
    open_time DateTime,
    open Decimal(18,4),
    high Decimal(18,4),
    low Decimal(18,4),
    close Decimal(18,4),
    volume UInt64,
    amount Decimal(18,4),
    trades UInt32
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (symbol, interval, open_time)
TTL date + INTERVAL 5 YEAR;

-- 因子历史数据表
CREATE TABLE factor_history (
    date Date,
    symbol LowCardinality(String),
    factor_id LowCardinality(String),
    value Decimal(18,6),
    quality UInt8
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (factor_id, symbol, date)
TTL date + INTERVAL 3 YEAR;

-- 财务数据表
CREATE TABLE financial_statements (
    report_date Date,
    symbol LowCardinality(String),
    report_type LowCardinality(String),
    revenue Decimal(18,2),
    net_income Decimal(18,2),
    total_assets Decimal(18,2),
    total_liabilities Decimal(18,2),
    eps Decimal(18,4),
    pe_ratio Decimal(18,4),
    pb_ratio Decimal(18,4)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(report_date)
ORDER BY (symbol, report_date, report_type);
```

---

## 3. 核心功能实现

### 3.1 物化视图

```sql
-- 日收益统计物化视图
CREATE MATERIALIZED VIEW daily_stats_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (symbol, date)
AS SELECT
    date,
    symbol,
    count() as trade_days,
    sum(volume) as total_volume,
    avg(close) as avg_close,
    max(high) as max_high,
    min(low) as min_low
FROM historical_klines
WHERE interval = '1d'
GROUP BY date, symbol;

-- 因子统计物化视图
CREATE MATERIALIZED VIEW factor_stats_mv
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (factor_id, date)
AS SELECT
    date,
    factor_id,
    avgState(value) as avg_value,
    quantileState(0.5)(value) as median_value,
    quantileState(0.25)(value) as q1_value,
    quantileState(0.75)(value) as q3_value
FROM factor_history
GROUP BY date, factor_id;
```

### 3.2 高效查询

```sql
-- 时间范围查询
SELECT 
    symbol,
    open_time,
    close,
    volume
FROM historical_klines
WHERE symbol = '000001.SZ'
AND interval = '1d'
AND date BETWEEN '2020-01-01' AND '2025-12-31'
ORDER BY open_time;

-- 聚合分析查询
SELECT 
    symbol,
    avg(close) as avg_close,
    stddev(close) as std_close,
    max(high) as max_high,
    min(low) as min_low,
    sum(volume) as total_volume
FROM historical_klines
WHERE interval = '1d'
AND date >= today() - INTERVAL 1 YEAR
GROUP BY symbol
ORDER BY total_volume DESC
LIMIT 100;

-- 窗口函数查询
SELECT 
    symbol,
    open_time,
    close,
    avg(close) OVER (
        PARTITION BY symbol 
        ORDER BY open_time 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) as ma20,
    avg(close) OVER (
        PARTITION BY symbol 
        ORDER BY open_time 
        ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
    ) as ma50
FROM historical_klines
WHERE symbol = '000001.SZ'
AND interval = '1d'
ORDER BY open_time DESC
LIMIT 100;
```

---

## 4. Python接口设计

### 4.1 数据写入接口

```python
from typing import List, Dict, Optional
from datetime import datetime
from clickhouse_driver import Client
import pandas as pd

class ClickHouseWriter:
    """ClickHouse数据写入器"""
    
    def __init__(self, host: str, port: int = 9000, database: str = 'zephyr'):
        self.client = Client(host=host, port=port, database=database)
    
    def write_klines(self, klines: pd.DataFrame) -> int:
        """批量写入K线数据"""
        data = [
            (
                row['date'], row['symbol'], row['interval'],
                row['open_time'], row['open'], row['high'],
                row['low'], row['close'], row['volume'],
                row.get('amount', 0), row.get('trades', 0)
            )
            for _, row in klines.iterrows()
        ]
        
        self.client.execute(
            """
            INSERT INTO historical_klines VALUES
            """,
            data
        )
        
        return len(data)
    
    def write_factors(self, factors: pd.DataFrame) -> int:
        """批量写入因子数据"""
        data = [
            (
                row['date'], row['symbol'], row['factor_id'],
                row['value'], row.get('quality', 100)
            )
            for _, row in factors.iterrows()
        ]
        
        self.client.execute(
            """
            INSERT INTO factor_history VALUES
            """,
            data
        )
        
        return len(data)
```

### 4.2 数据查询接口

```python
class ClickHouseReader:
    """ClickHouse数据查询器"""
    
    def __init__(self, host: str, port: int = 9000, database: str = 'zephyr'):
        self.client = Client(host=host, port=port, database=database)
    
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """获取K线数据"""
        sql = """
        SELECT 
            open_time, symbol, open, high, low, close, volume, amount
        FROM historical_klines
        WHERE symbol = %(symbol)s
        AND interval = %(interval)s
        AND date BETWEEN %(start_date)s AND %(end_date)s
        ORDER BY open_time
        """
        
        result = self.client.execute(sql, {
            'symbol': symbol,
            'interval': interval,
            'start_date': start_date,
            'end_date': end_date
        })
        
        return pd.DataFrame(result, columns=[
            'open_time', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'amount'
        ])
    
    def get_factor_panel(
        self,
        factor_id: str,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """获取因子截面数据"""
        sql = """
        SELECT 
            date, symbol, value
        FROM factor_history
        WHERE factor_id = %(factor_id)s
        AND symbol IN %(symbols)s
        AND date BETWEEN %(start_date)s AND %(end_date)s
        ORDER BY date, symbol
        """
        
        result = self.client.execute(sql, {
            'factor_id': factor_id,
            'symbols': symbols,
            'start_date': start_date,
            'end_date': end_date
        })
        
        df = pd.DataFrame(result, columns=['date', 'symbol', 'value'])
        return df.pivot(index='date', columns='symbol', values='value')
```

---

## 5. 部署配置

### 5.1 Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    container_name: zephyr_clickhouse
    environment:
      CLICKHOUSE_DB: zephyr
      CLICKHOUSE_USER: zephyr
      CLICKHOUSE_PASSWORD: ${CLICKHOUSE_PASSWORD}
      CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT: 1
    ports:
      - "8123:8123"  # HTTP接口
      - "9000:9000"  # Native接口
    volumes:
      - clickhouse_data:/var/lib/clickhouse
      - clickhouse_logs:/var/log/clickhouse-server
      - ./config.xml:/etc/clickhouse-server/config.d/custom.xml
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "localhost:8123/ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  clickhouse_data:
  clickhouse_logs:
```

### 5.2 配置优化

```xml
<!-- config.xml -->
<clickhouse>
    <max_connections>4096</max_connections>
    <keep_alive_timeout>3</keep_alive_timeout>
    <max_concurrent_queries>100</max_concurrent_queries>
    
    <mark_cache_size>5368709120</mark_cache_size>
    
    <logger>
        <level>information</level>
        <log>/var/log/clickhouse-server/clickhouse-server.log</log>
        <errorlog>/var/log/clickhouse-server/clickhouse-server.err.log</errorlog>
    </logger>
</clickhouse>
```

---

## 📋 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 首席架构师 |

---

**文档结束**
