---
module_id: TIMESCALEDB_INTEGRATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
responsibility:
  - TimescaleDB集成
  - 时序数据库
  - 时间序列
  - 高效存储

layer: Layer 5.1 (数据处理)
---


> **职责边界**: 

## 核心定位


TimescaleDB集成模块，实现与TimescaleDB时序数据库的集成，支持大规模时序数据的高效存储和查询。
### 主要目标

1. **功能完整性**: 确保TIMESCALEDB INTEGRATION功能完整，满足业务需求
2. **性能优化**: 提升系统性能，降低资源消耗
3. **可维护性**: 提高代码质量，便于后续维护
4. **可扩展性**: 支持功能扩展，适应业务变化

### 质量目标

- 代码覆盖率: ≥80%
- 性能指标: 满足设计要求
- 文档完整性: 100%


## 核心功能

### 功能清单

1. **数据管理**: 提供数据存储、查询、更新功能
2. **业务逻辑**: 实现核心业务逻辑处理
3. **接口服务**: 提供标准化的API接口
4. **监控告警**: 实时监控系统状态

### 功能特性

- 高可用性设计
- 自动故障恢复
- 灵活配置管理


## 实现方案

### 技术架构

采用TIMESCALEDB INTEGRATION化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控


### 职责边界

|------|--------|
分发 |
洗处理 |



## 1. 技术选型

### 1.1 为什么选择TimescaleDB

|------|-------------|----------|---------|
| SQL
¨

### 1.2 核心优势

1. **PostgreSQL
4. **单机友好**: 个人开发场景最佳选择



## 2. 架构设计

### 2.1 整体架构

```
```

### 2.2 数据模型设计

```sql
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

级表
SELECT create_hypertable('stock_ticks', 'time',
    partitioning_column => 'symbol',
    number_partitions => 4
);

级表
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



## 3. 核心功能实现


```sql
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

SELECT add_compression_policy('stock_ticks', INTERVAL '7 days');

ALTER TABLE stock_klines SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,interval',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('stock_klines', INTERVAL '7 days');
```

### 3.3 数据保留策略

```sql
SELECT add_retention_policy('stock_ticks', INTERVAL '30 days');

SELECT add_retention_policy('stock_klines', INTERVAL '1 year');

SELECT add_retention_policy('factor_values', INTERVAL '1 year');
```



## 4. Python接口设计


```python
from typing import List, Dict, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

class TimescaleDBWriter:
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cursor = self.conn.cursor()
    
    def write_ticks(self, ticks: List[Dict]) -> int:
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
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime
    ) -> pd.DataFrame:
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


```python
import asyncio
from asyncpg import create_pool

class AsyncTimescaleDBWriter:
    
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
¥"""
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




### 6.1 性能监控

```sql
SELECT * FROM timescaledb_information.hypertables;

SELECT * FROM timescaledb_information.compression_settings;

SELECT * FROM timescaledb_information.continuous_aggregates;

SELECT * FROM timescaledb_information.jobs;

-- 查看数据大小
SELECT 
    hypertable_name,
    pg_size_pretty(total_bytes) as total_size,
    pg_size_pretty(compressed_bytes) as compressed_size,
    compression_ratio
FROM timescaledb_information.compressed_hypertable_stats;
```


```python
class TimescaleDBHealthCheck:
    
    def __init__(self, conn):
        self.conn = conn
    
    def check_connection(self) -> bool:
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def check_hypertables(self) -> List[Dict]:
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


```sql
-- init.sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

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
        
```

### 8.2 与Redis集成

```python
class TimescaleDBRedisCache:
    
    def get_latest_price_with_cache(self, symbol: str) -> float:
        # 1. 
        # 2. 缓存未命中则查TimescaleDB
```



## 📋 变更历史

|------|------|---------|------|



**文档结束**

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 实施团队 |



