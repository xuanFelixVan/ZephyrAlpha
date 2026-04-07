---
module_id: TIMESCALEDB_INTEGRATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®å±?
compliance_level: ä¸ä¸æ å
responsibility:
  - TimescaleDBéæ
  - æ¶åºæ°æ®å­å¨
  - é«é¢æ°æ®ç®¡ç
  - æ¶é´çªå£èå
layer: Layer 5.1 (数据处理)
---

# TimescaleDBæ¶åºæ°æ®åºéæèå?

> **æ ¸å¿èè´£**: æ¶åºæ°æ®çå­å¨ãæ¥è¯¢åç®¡çï¼ä¸æ³¨äºé«é¢éèæ°æ®çæ¶é´åºåç¹æ?
> **èè´£è¾¹ç**: 
> - â?æ¬æ¨¡åè´è´£ï¼æ¶åºæ°æ®å­å¨ãæ¶é´çªå£æ¥è¯¢ãè¿ç»­èåãæ°æ®åç¼?
> - â?æ¬æ¨¡åä¸è´è´£ï¼åå¼åæå­å¨ï¼ClickHouseï¼ãç¼å­ï¼Redisï¼?

## æ ¸å¿å®ä½

**åä¸èè´£**: æ¶åºæ°æ®çå­å¨ãæ¥è¯¢åç®¡çï¼ä¸æ³¨äºé«é¢éèæ°æ®çæ¶é´åºåç¹æ?

## 设计目标

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


### èè´£è¾¹ç

| è´è´£ | ä¸è´è´?|
|------|--------|
| â?é«é¢è¡ææ°æ®å­å¨ | â?å¤§è§æ¨¡åå²æ°æ®åæ?|
| â?æ¶é´çªå£èåæ¥è¯¢ | â?åå¼èååæ |
| â?è¿ç»­èåé¢è®¡ç®?| â?å®æ¶æ°æ®ç¼å­ |
| â?æ°æ®åç¼©ä¸ä¿çç­ç?| â?æ°æ®è®¢éåå |
| â?æ¶åºæ°æ®ééæ ?| â?æ°æ®æ¸æ´å¤ç |

---

## 1. ææ¯éå

### 1.1 ä¸ºä»ä¹éæ©TimescaleDB

| ç¹æ?| TimescaleDB | InfluxDB | QuestDB |
|------|-------------|----------|---------|
| SQLå¼å®¹ | â?å®å¨å¼å®¹ | â?Fluxè¯­è¨ | â?é¨åå¼å®¹ |
| å­¦ä¹ æ²çº¿ | â­â­â­â­â­?| â­â­â­?| â­â­â­?|
| Pythonæ¯æ | â?psycopg2 | â?influxdb | â?questdb |
| åæºé¨ç½² | â?ç®å?| â?ç®å?| â?ç®å?|
| åç¼©è½å | â?ä¼ç§ | â?ä¼ç§ | â?ä¼ç§ |
| è¿ç»­èå | â?æ¯æ | â?æ¯æ | â?æ¯æ |
| ç¤¾åºæ´»è·åº?| â­â­â­â­â­?| â­â­â­â­ | â­â­â­?|
| **æ¨èææ°** | **â­â­â­â­â­?* | â­â­â­â­ | â­â­â­?|

### 1.2 æ ¸å¿ä¼å¿

1. **PostgreSQLå¼å®¹**: æ éå­¦ä¹ æ°è¯­è¨ï¼SQLç´æ¥ä½¿ç¨
2. **æ¶åºä¼å**: èªå¨ååºãåç¼©ãè¿ç»­èå?
3. **çæå®å?*: psycopg2ãSQLAlchemyãpandaså®ç¾æ¯æ
4. **åæºåå¥½**: ä¸ªäººå¼ååºæ¯æä½³éæ©

---

## 2. æ¶æè®¾è®¡

### 2.1 æ´ä½æ¶æ

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   TimescaleDBéææ¶æ                           â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                                                                â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â? â?æ°æ®åå¥å±?  â?   â?æ°æ®å­å¨å±?  â?   â?æ°æ®æ¥è¯¢å±?  â?    â?
â? â?             â?   â?             â?   â?             â?    â?
â? â?â?æ¹éåå¥   â?   â?â?è¶çº§è¡?    â?   â?â?æ¶é´çªå£   â?    â?
â? â?â?æµå¼åå¥   â?   â?â?èªå¨ååº   â?   â?â?è¿ç»­èå   â?    â?
â? â?â?å¼æ­¥åå¥   â?   â?â?åç¼©ç­ç¥   â?   â?â?ééæ ·æ¥è¯?â?    â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â?        â?                  â?                   â?             â?
â?        âââââââââââââââââââââ´âââââââââââââââââââââ?             â?
â?                           â?                                   â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?                   æ°æ®ä¿çç­ç¥                          â?  â?
â? â? â?ç­æ°æ? 7å¤?(æªåç¼?                                  â?  â?
â? â? â?æ¸©æ°æ? 30å¤?(åç¼©)                                   â?  â?
â? â? â?å·æ°æ? å½æ¡£å°ClickHouse                              â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                                                                â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### 2.2 æ°æ®æ¨¡åè®¾è®¡

```sql
-- è¡ææ°æ®è¶çº§è¡?
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

-- è½¬æ¢ä¸ºè¶çº§è¡¨
SELECT create_hypertable('stock_ticks', 'time',
    partitioning_column => 'symbol',
    number_partitions => 4
);

-- Kçº¿æ°æ®è¶çº§è¡¨
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

-- å å­æ°æ®è¶çº§è¡?
CREATE TABLE factor_values (
    time        TIMESTAMPTZ NOT NULL,
    symbol      VARCHAR(20) NOT NULL,
    factor_id   VARCHAR(50) NOT NULL,
    value       DECIMAL(18,6),
    quality     INTEGER  -- æ°æ®è´¨éè¯å
);

SELECT create_hypertable('factor_values', 'time',
    partitioning_column => 'symbol',
    number_partitions => 4
);
```

---

## 3. æ ¸å¿åè½å®ç°

### 3.1 è¿ç»­èåï¼Continuous Aggregatesï¼?

```sql
-- 1åéKçº¿èå?
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

-- å·æ°ç­ç¥
SELECT add_continuous_aggregate_policy('kline_1m',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute'
);

-- 5åéKçº¿èå?
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

-- æ¥Kçº¿èå?
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

### 3.2 æ°æ®åç¼©ç­ç¥

```sql
-- å¯ç¨åç¼©
ALTER TABLE stock_ticks SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol',
    timescaledb.compress_orderby = 'time DESC'
);

-- æ·»å åç¼©ç­ç¥ï¼?å¤©ååç¼©ï¼?
SELECT add_compression_policy('stock_ticks', INTERVAL '7 days');

-- Kçº¿æ°æ®åç¼?
ALTER TABLE stock_klines SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,interval',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('stock_klines', INTERVAL '7 days');
```

### 3.3 æ°æ®ä¿çç­ç¥

```sql
-- Tickæ°æ®ä¿ç30å¤?
SELECT add_retention_policy('stock_ticks', INTERVAL '30 days');

-- Kçº¿æ°æ®ä¿ç?å¹?
SELECT add_retention_policy('stock_klines', INTERVAL '1 year');

-- å å­æ°æ®ä¿ç1å¹?
SELECT add_retention_policy('factor_values', INTERVAL '1 year');
```

---

## 4. Pythonæ¥å£è®¾è®¡

### 4.1 æ°æ®åå¥æ¥å£

```python
from typing import List, Dict, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

class TimescaleDBWriter:
    """TimescaleDBæ°æ®åå¥å?""
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cursor = self.conn.cursor()
    
    def write_ticks(self, ticks: List[Dict]) -> int:
        """æ¹éåå¥Tickæ°æ®"""
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
        """æ¹éåå¥Kçº¿æ°æ?""
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
        """æ¹éåå¥å å­æ°æ®"""
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

### 4.2 æ°æ®æ¥è¯¢æ¥å£

```python
class TimescaleDBReader:
    """TimescaleDBæ°æ®æ¥è¯¢å?""
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime
    ) -> pd.DataFrame:
        """è·åKçº¿æ°æ?""
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
        """è·åTickæ°æ®"""
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
        """è·åå å­æ°æ®"""
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
        """è·åææ°ä»·æ ?""
        sql = """
        SELECT DISTINCT ON (symbol) symbol, price, time
        FROM stock_ticks
        WHERE symbol = ANY(%s)
        ORDER BY symbol, time DESC
        """
        
        df = pd.read_sql(sql, self.conn, params=[symbols])
        return dict(zip(df['symbol'], df['price']))
```

### 4.3 æ¶é´çªå£æ¥è¯¢

```python
class TimeWindowQueries:
    """æ¶é´çªå£æ¥è¯¢"""
    
    def __init__(self, reader: TimescaleDBReader):
        self.reader = reader
    
    def get_rolling_stats(
        self,
        symbol: str,
        window: str,  # '1h', '1d', '1w'
        metric: str = 'close'
    ) -> pd.DataFrame:
        """è·åæ»å¨ç»è®¡"""
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
        """æ¶é´æ¡¶èåæ¥è¯?""
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

## 5. æ§è½ä¼å

### 5.1 ç´¢å¼ç­ç¥

```sql
-- ç¬¦å·ç´¢å¼
CREATE INDEX idx_ticks_symbol ON stock_ticks (symbol, time DESC);
CREATE INDEX idx_klines_symbol_interval ON stock_klines (symbol, interval, time DESC);
CREATE INDEX idx_factors_symbol_factor ON factor_values (symbol, factor_id, time DESC);

-- æ¶é´èå´ç´¢å¼
CREATE INDEX idx_ticks_time ON stock_ticks (time DESC);
CREATE INDEX idx_klines_time ON stock_klines (time DESC);
```

### 5.2 æ¥è¯¢ä¼å

```sql
-- ä½¿ç¨æ¶é´æ¡¶å½æ°ä¼å?
EXPLAIN ANALYZE
SELECT time_bucket('5 minutes', time) AS bucket,
       symbol,
       AVG(price) as avg_price
FROM stock_ticks
WHERE time > NOW() - INTERVAL '1 day'
GROUP BY bucket, symbol;

-- ä½¿ç¨è¿ç»­èåä¼å
EXPLAIN ANALYZE
SELECT * FROM kline_5m
WHERE symbol = '000001.SZ'
AND bucket > NOW() - INTERVAL '7 days';
```

### 5.3 æ¹éåå¥ä¼å

```python
import asyncio
from asyncpg import create_pool

class AsyncTimescaleDBWriter:
    """å¼æ­¥æ¹éåå¥å?""
    
    def __init__(self, connection_string: str, pool_size: int = 5):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.pool = None
    
    async def init_pool(self):
        """åå§åè¿æ¥æ± """
        self.pool = await create_pool(
            self.connection_string,
            min_size=1,
            max_size=self.pool_size
        )
    
    async def write_ticks_batch(self, ticks: List[Dict]) -> int:
        """å¼æ­¥æ¹éåå¥"""
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

## 6. çæ§ä¸è¿ç»?

### 6.1 æ§è½çæ§

```sql
-- æ¥çè¶çº§è¡¨ä¿¡æ?
SELECT * FROM timescaledb_information.hypertables;

-- æ¥çåç¼©ç¶æ?
SELECT * FROM timescaledb_information.compression_settings;

-- æ¥çè¿ç»­èåç¶æ?
SELECT * FROM timescaledb_information.continuous_aggregates;

-- æ¥çä½ä¸ç¶æ?
SELECT * FROM timescaledb_information.jobs;

-- æ¥çæ°æ®å¤§å°
SELECT 
    hypertable_name,
    pg_size_pretty(total_bytes) as total_size,
    pg_size_pretty(compressed_bytes) as compressed_size,
    compression_ratio
FROM timescaledb_information.compressed_hypertable_stats;
```

### 6.2 å¥åº·æ£æ?

```python
class TimescaleDBHealthCheck:
    """å¥åº·æ£æ?""
    
    def __init__(self, conn):
        self.conn = conn
    
    def check_connection(self) -> bool:
        """æ£æ¥è¿æ?""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"è¿æ¥å¤±è´¥: {e}")
            return False
    
    def check_hypertables(self) -> List[Dict]:
        """æ£æ¥è¶çº§è¡¨ç¶æ?""
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
        """æ£æ¥ä½ä¸ç¶æ?""
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

## 7. é¨ç½²éç½®

### 7.1 Dockeré¨ç½²

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

### 7.2 åå§åèæ?

```sql
-- init.sql
-- å¯ç¨TimescaleDBæ©å±
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- åå»ºè¶çº§è¡?
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

-- è®¾ç½®åç¼©ç­ç¥
ALTER TABLE stock_ticks SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol'
);

SELECT add_compression_policy('stock_ticks', INTERVAL '7 days');
SELECT add_retention_policy('stock_ticks', INTERVAL '30 days');
```

---

## 8. ä¸å¶ä»æ¨¡åéæ?

### 8.1 ä¸ClickHouseéæ

```python
class TimescaleDBToClickHouse:
    """æ°æ®å½æ¡£å°ClickHouse"""
    
    def archive_old_data(self, days: int = 30):
        """å½æ¡£æ§æ°æ®å°ClickHouse"""
        # 1. ä»TimescaleDBå¯¼åºæ°æ®
        sql = f"""
        COPY (
            SELECT * FROM stock_ticks
            WHERE time < NOW() - INTERVAL '{days} days'
        ) TO STDOUT WITH CSV HEADER
        """
        
        # 2. å¯¼å¥å°ClickHouse
        # 3. å é¤TimescaleDBä¸­çæ§æ°æ?
```

### 8.2 ä¸Rediséæ

```python
class TimescaleDBRedisCache:
    """Redisç¼å­å±?""
    
    def get_latest_price_with_cache(self, symbol: str) -> float:
        """å¸¦ç¼å­çææ°ä»·æ ¼æ¥è¯?""
        # 1. åæ¥Redisç¼å­
        # 2. ç¼å­æªå½ä¸­åæ¥TimescaleDB
        # 3. åå¥Redisç¼å­
```

---

## ð åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**ææ¡£ç»æ**
