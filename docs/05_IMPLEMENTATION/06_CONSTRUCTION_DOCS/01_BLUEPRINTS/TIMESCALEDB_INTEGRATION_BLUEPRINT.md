---
module_id: TIMESCALEDB_INTEGRATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 1 数据层
compliance_level: 专业标准
responsibility:
  - TimescaleDB集成
  - 时序数据存储
  - 高频数据管理
  - 时间窗口聚合
layer: "Layer 1 (数据层)"
---

# TimescaleDB时序数据库集成蓝图

> **核心职责**: 时序数据的存储、查询和管理，专注于高频金融数据的时间序列特性
> **职责边界**: 
> - ✅ 本模块负责：时序数据存储、时间窗口查询、连续聚合、数据压缩
> - ❌ 本模块不负责：列式分析存储（ClickHouse）、缓存（Redis）

## 核心定位

**单一职责**: 时序数据的存储、查询和管理，专注于高频金融数据的时间序列特性

### 职责边界

| 负责 | 不负责 |
|------|--------|
| ✅ 高频行情数据存储 | ❌ 大规模历史数据分析 |
| ✅ 时间窗口聚合查询 | ❌ 列式聚合分析 |
| ✅ 连续聚合预计算 | ❌ 实时数据缓存 |
| ✅ 数据压缩与保留策略 | ❌ 数据订阅分发 |
| ✅ 时序数据降采样 | ❌ 数据清洗处理 |

---

## 1. 技术选型

### 1.1 为什么选择TimescaleDB

| 特性 | TimescaleDB | InfluxDB | QuestDB |
|------|-------------|----------|---------|
| SQL兼容 | ✅ 完全兼容 | ❌ Flux语言 | ✅ 部分兼容 |
| 学习曲线 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Python支持 | ✅ psycopg2 | ✅ influxdb | ✅ questdb |
| 单机部署 | ✅ 简单 | ✅ 简单 | ✅ 简单 |
| 压缩能力 | ✅ 优秀 | ✅ 优秀 | ✅ 优秀 |
| 连续聚合 | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| 社区活跃度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **推荐指数** | **⭐⭐⭐⭐⭐** | ⭐⭐⭐⭐ | ⭐⭐⭐ |

### 1.2 核心优势

1. **PostgreSQL兼容**: 无需学习新语言，SQL直接使用
2. **时序优化**: 自动分区、压缩、连续聚合
3. **生态完善**: psycopg2、SQLAlchemy、pandas完美支持
4. **单机友好**: 个人开发场景最佳选择

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    TimescaleDB集成架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ 数据写入层   │    │ 数据存储层   │    │ 数据查询层   │     │
│  │              │    │              │    │              │     │
│  │ • 批量写入   │    │ • 超级表     │    │ • 时间窗口   │     │
│  │ • 流式写入   │    │ • 自动分区   │    │ • 连续聚合   │     │
│  │ • 异步写入   │    │ • 压缩策略   │    │ • 降采样查询 │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                   │                    │              │
│         └───────────────────┴────────────────────┘              │
│                            │                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    数据保留策略                          │   │
│  │  • 热数据: 7天 (未压缩)                                  │   │
│  │  • 温数据: 30天 (压缩)                                   │   │
│  │  • 冷数据: 归档到ClickHouse                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 数据模型设计

```sql
-- 行情数据超级表
CREATE TABLE stock_ticks (
    time        TIMESTAMPTZ NOT NULL,
    symbol      VARCHAR(20) NOT NULL,
    price       DECIMAL(18,4),
    volume      BIGINT,
    bid_price   DECIMAL(18,4),
    ask_price   DECIMAL(18,4),
    bid_volume  BIGINT,
    ask_volume  BIGINT
);

-- 转换为超级表
SELECT create_hypertable('stock_ticks', 'time',
    partitioning_column => 'symbol',
    number_partitions => 4
);

-- K线数据超级表
CREATE TABLE stock_klines (
    time        TIMESTAMPTZ NOT NULL,
    symbol      VARCHAR(20) NOT NULL,
    interval    VARCHAR(10) NOT NULL,  -- 1m, 5m, 15m, 1h, 1d
    open        DECIMAL(18,4),
    high        DECIMAL(18,4),
    low         DECIMAL(18,4),
    close       DECIMAL(18,4),
    volume      BIGINT,
    amount      DECIMAL(18,4)
);

SELECT create_hypertable('stock_klines', 'time',
    partitioning_column => 'symbol',
    number_partitions => 4
);

-- 因子数据超级表
CREATE TABLE factor_values (
    time        TIMESTAMPTZ NOT NULL,
    symbol      VARCHAR(20) NOT NULL,
    factor_id   VARCHAR(50) NOT NULL,
    value       DECIMAL(18,6),
    quality     INTEGER  -- 数据质量评分
);

SELECT create_hypertable('factor_values', 'time',
    partitioning_column => 'symbol',
    number_partitions => 4
);
```

---

## 3. 核心功能实现

### 3.1 连续聚合（Continuous Aggregates）

```sql
-- 1分钟K线聚合
CREATE MATERIALIZED VIEW kline_1m
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 minute', time) AS bucket,
    symbol,
    FIRST(price, time) AS open,
    MAX(price) AS high,
    MIN(price) AS low,
    LAST(price, time) AS close,
    SUM(volume) AS volume
FROM stock_ticks
GROUP BY bucket, symbol;

-- 刷新策略
SELECT add_continuous_aggregate_policy('kline_1m',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute'
);

-- 5分钟K线聚合
CREATE MATERIALIZED VIEW kline_5m
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('5 minutes', time) AS bucket,
    symbol,
    FIRST(price, time) AS open,
    MAX(price) AS high,
    MIN(price) AS low,
    LAST(price, time) AS close,
    SUM(volume) AS volume
FROM stock_ticks
GROUP BY bucket, symbol;

-- 日K线聚合
CREATE MATERIALIZED VIEW kline_1d
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS bucket,
    symbol,
    FIRST(price, time) AS open,
    MAX(price) AS high,
    MIN(price) AS low,
    LAST(price, time) AS close,
    SUM(volume) AS volume
FROM stock_ticks
GROUP BY bucket, symbol;
```

### 3.2 数据压缩策略

```sql
-- 启用压缩
ALTER TABLE stock_ticks SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol',
    timescaledb.compress_orderby = 'time DESC'
);

-- 添加压缩策略（7天后压缩）
SELECT add_compression_policy('stock_ticks', INTERVAL '7 days');

-- K线数据压缩
ALTER TABLE stock_klines SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,interval',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('stock_klines', INTERVAL '7 days');
```

### 3.3 数据保留策略

```sql
-- Tick数据保留30天
SELECT add_retention_policy('stock_ticks', INTERVAL '30 days');

-- K线数据保留1年
SELECT add_retention_policy('stock_klines', INTERVAL '1 year');

-- 因子数据保留1年
SELECT add_retention_policy('factor_values', INTERVAL '1 year');
```

---

## 4. Python接口设计

### 4.1 数据写入接口

```python
from typing import List, Dict, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

class TimescaleDBWriter:
    """TimescaleDB数据写入器"""
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cursor = self.conn.cursor()
    
    def write_ticks(self, ticks: List[Dict]) -> int:
        """批量写入Tick数据"""
        sql = """
        INSERT INTO stock_ticks 
        (time, symbol, price, volume, bid_price, ask_price, bid_volume, ask_volume)
        VALUES %s
        """
        
        values = [(
            tick['time'], tick['symbol'], tick['price'], tick['volume'],
            tick.get('bid_price'), tick.get('ask_price'),
            tick.get('bid_volume'), tick.get('ask_volume')
        ) for tick in ticks]
        
        execute_values(self.cursor, sql, values)
        self.conn.commit()
        return len(values)
    
    def write_klines(self, klines: pd.DataFrame) -> int:
        """批量写入K线数据"""
        sql = """
        INSERT INTO stock_klines 
        (time, symbol, interval, open, high, low, close, volume, amount)
        VALUES %s
        """
        
        values = [(
            row['time'], row['symbol'], row['interval'],
            row['open'], row['high'], row['low'], row['close'],
            row['volume'], row.get('amount')
        ) for _, row in klines.iterrows()]
        
        execute_values(self.cursor, sql, values)
        self.conn.commit()
        return len(values)
    
    def write_factors(self, factors: pd.DataFrame) -> int:
        """批量写入因子数据"""
        sql = """
        INSERT INTO factor_values 
        (time, symbol, factor_id, value, quality)
        VALUES %s
        """
        
        values = [(
            row['time'], row['symbol'], row['factor_id'],
            row['value'], row.get('quality', 100)
        ) for _, row in factors.iterrows()]
        
        execute_values(self.cursor, sql, values)
        self.conn.commit()
        return len(values)
```

### 4.2 数据查询接口

```python
class TimescaleDBReader:
    """TimescaleDB数据查询器"""
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime
    ) -> pd.DataFrame:
        """获取K线数据"""
        sql = """
        SELECT time, symbol, open, high, low, close, volume, amount
        FROM stock_klines
        WHERE symbol = %s AND interval = %s
        AND time >= %s AND time < %s
        ORDER BY time
        """
        
        return pd.read_sql(sql, self.conn, params=[
            symbol, interval, start_time, end_time
        ])
    
    def get_ticks(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime
    ) -> pd.DataFrame:
        """获取Tick数据"""
        sql = """
        SELECT time, symbol, price, volume, bid_price, ask_price
        FROM stock_ticks
        WHERE symbol = %s
        AND time >= %s AND time < %s
        ORDER BY time
        """
        
        return pd.read_sql(sql, self.conn, params=[
            symbol, start_time, end_time
        ])
    
    def get_factor_values(
        self,
        factor_id: str,
        symbols: List[str],
        start_time: datetime,
        end_time: datetime
    ) -> pd.DataFrame:
        """获取因子数据"""
        sql = """
        SELECT time, symbol, value, quality
        FROM factor_values
        WHERE factor_id = %s
        AND symbol = ANY(%s)
        AND time >= %s AND time < %s
        ORDER BY time, symbol
        """
        
        return pd.read_sql(sql, self.conn, params=[
            factor_id, symbols, start_time, end_time
        ])
    
    def get_latest_prices(self, symbols: List[str]) -> Dict[str, float]:
        """获取最新价格"""
        sql = """
        SELECT DISTINCT ON (symbol) symbol, price, time
        FROM stock_ticks
        WHERE symbol = ANY(%s)
        ORDER BY symbol, time DESC
        """
        
        df = pd.read_sql(sql, self.conn, params=[symbols])
        return dict(zip(df['symbol'], df['price']))
```

### 4.3 时间窗口查询

```python
class TimeWindowQueries:
    """时间窗口查询"""
    
    def __init__(self, reader: TimescaleDBReader):
        self.reader = reader
    
    def get_rolling_stats(
        self,
        symbol: str,
        window: str,  # '1h', '1d', '1w'
        metric: str = 'close'
    ) -> pd.DataFrame:
        """获取滚动统计"""
        sql = f"""
        SELECT 
            time,
            {metric},
            AVG({metric}) OVER (ORDER BY time RANGE BETWEEN INTERVAL '{window}' PRECEDING AND CURRENT ROW) as avg,
            STDDEV({metric}) OVER (ORDER BY time RANGE BETWEEN INTERVAL '{window}' PRECEDING AND CURRENT ROW) as std,
            MAX({metric}) OVER (ORDER BY time RANGE BETWEEN INTERVAL '{window}' PRECEDING AND CURRENT ROW) as max,
            MIN({metric}) OVER (ORDER BY time RANGE BETWEEN INTERVAL '{window}' PRECEDING AND CURRENT ROW) as min
        FROM stock_klines
        WHERE symbol = %s AND interval = '1m'
        ORDER BY time DESC
        LIMIT 1000
        """
        
        return pd.read_sql(sql, self.reader.conn, params=[symbol])
    
    def get_time_bucket_agg(
        self,
        symbol: str,
        bucket_size: str,  # '1 hour', '1 day'
        start_time: datetime,
        end_time: datetime
    ) -> pd.DataFrame:
        """时间桶聚合查询"""
        sql = f"""
        SELECT 
            time_bucket('{bucket_size}', time) AS bucket,
            symbol,
            FIRST(close, time) AS open,
            MAX(high) AS high,
            MIN(low) AS low,
            LAST(close, time) AS close,
            SUM(volume) AS volume
        FROM stock_klines
        WHERE symbol = %s AND interval = '1m'
        AND time >= %s AND time < %s
        GROUP BY bucket, symbol
        ORDER BY bucket
        """
        
        return pd.read_sql(sql, self.reader.conn, params=[
            symbol, start_time, end_time
        ])
```

---

## 5. 性能优化

### 5.1 索引策略

```sql
-- 符号索引
CREATE INDEX idx_ticks_symbol ON stock_ticks (symbol, time DESC);
CREATE INDEX idx_klines_symbol_interval ON stock_klines (symbol, interval, time DESC);
CREATE INDEX idx_factors_symbol_factor ON factor_values (symbol, factor_id, time DESC);

-- 时间范围索引
CREATE INDEX idx_ticks_time ON stock_ticks (time DESC);
CREATE INDEX idx_klines_time ON stock_klines (time DESC);
```

### 5.2 查询优化

```sql
-- 使用时间桶函数优化
EXPLAIN ANALYZE
SELECT time_bucket('5 minutes', time) AS bucket,
       symbol,
       AVG(price) as avg_price
FROM stock_ticks
WHERE time > NOW() - INTERVAL '1 day'
GROUP BY bucket, symbol;

-- 使用连续聚合优化
EXPLAIN ANALYZE
SELECT * FROM kline_5m
WHERE symbol = '000001.SZ'
AND bucket > NOW() - INTERVAL '7 days';
```

### 5.3 批量写入优化

```python
import asyncio
from asyncpg import create_pool

class AsyncTimescaleDBWriter:
    """异步批量写入器"""
    
    def __init__(self, connection_string: str, pool_size: int = 5):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.pool = None
    
    async def init_pool(self):
        """初始化连接池"""
        self.pool = await create_pool(
            self.connection_string,
            min_size=1,
            max_size=self.pool_size
        )
    
    async def write_ticks_batch(self, ticks: List[Dict]) -> int:
        """异步批量写入"""
        async with self.pool.acquire() as conn:
            values = [
                (t['time'], t['symbol'], t['price'], t['volume'])
                for t in ticks
            ]
            
            await conn.executemany(
                """
                INSERT INTO stock_ticks (time, symbol, price, volume)
                VALUES ($1, $2, $3, $4)
                """,
                values
            )
            
            return len(values)
```

---

## 6. 监控与运维

### 6.1 性能监控

```sql
-- 查看超级表信息
SELECT * FROM timescaledb_information.hypertables;

-- 查看压缩状态
SELECT * FROM timescaledb_information.compression_settings;

-- 查看连续聚合状态
SELECT * FROM timescaledb_information.continuous_aggregates;

-- 查看作业状态
SELECT * FROM timescaledb_information.jobs;

-- 查看数据大小
SELECT 
    hypertable_name,
    pg_size_pretty(total_bytes) as total_size,
    pg_size_pretty(compressed_bytes) as compressed_size,
    compression_ratio
FROM timescaledb_information.compressed_hypertable_stats;
```

### 6.2 健康检查

```python
class TimescaleDBHealthCheck:
    """健康检查"""
    
    def __init__(self, conn):
        self.conn = conn
    
    def check_connection(self) -> bool:
        """检查连接"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def check_hypertables(self) -> List[Dict]:
        """检查超级表状态"""
        sql = """
        SELECT 
            hypertable_name,
            num_chunks,
            is_compressed
        FROM timescaledb_information.hypertables
        """
        
        with self.conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    
    def check_jobs(self) -> List[Dict]:
        """检查作业状态"""
        sql = """
        SELECT 
            job_id,
            application_name,
            schedule_interval,
            last_run_status
        FROM timescaledb_information.jobs
        """
        
        with self.conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
```

---

## 7. 部署配置

### 7.1 Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg15
    container_name: zephyr_timescaledb
    environment:
      POSTGRES_USER: zephyr
      POSTGRES_PASSWORD: ${TIMESCALEDB_PASSWORD}
      POSTGRES_DB: zephyr_quant
    ports:
      - "5432:5432"
    volumes:
      - timescaledb_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U zephyr -d zephyr_quant"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  timescaledb_data:
```

### 7.2 初始化脚本

```sql
-- init.sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建超级表
CREATE TABLE stock_ticks (
    time        TIMESTAMPTZ NOT NULL,
    symbol      VARCHAR(20) NOT NULL,
    price       DECIMAL(18,4),
    volume      BIGINT
);

SELECT create_hypertable('stock_ticks', 'time',
    partitioning_column => 'symbol',
    number_partitions => 4
);

-- 设置压缩策略
ALTER TABLE stock_ticks SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol'
);

SELECT add_compression_policy('stock_ticks', INTERVAL '7 days');
SELECT add_retention_policy('stock_ticks', INTERVAL '30 days');
```

---

## 8. 与其他模块集成

### 8.1 与ClickHouse集成

```python
class TimescaleDBToClickHouse:
    """数据归档到ClickHouse"""
    
    def archive_old_data(self, days: int = 30):
        """归档旧数据到ClickHouse"""
        # 1. 从TimescaleDB导出数据
        sql = f"""
        COPY (
            SELECT * FROM stock_ticks
            WHERE time < NOW() - INTERVAL '{days} days'
        ) TO STDOUT WITH CSV HEADER
        """
        
        # 2. 导入到ClickHouse
        # 3. 删除TimescaleDB中的旧数据
```

### 8.2 与Redis集成

```python
class TimescaleDBRedisCache:
    """Redis缓存层"""
    
    def get_latest_price_with_cache(self, symbol: str) -> float:
        """带缓存的最新价格查询"""
        # 1. 先查Redis缓存
        # 2. 缓存未命中则查TimescaleDB
        # 3. 写入Redis缓存
```

---

## 📋 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 首席架构师 |

---

**文档结束**
