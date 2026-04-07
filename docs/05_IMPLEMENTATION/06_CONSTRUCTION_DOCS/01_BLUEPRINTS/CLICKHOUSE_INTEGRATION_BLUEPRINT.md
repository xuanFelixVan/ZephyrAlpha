---
module_id: CLICKHOUSE_INTEGRATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®å±?
compliance_level: ä¸ä¸æ å
responsibility:
  - ClickHouseéæ
  - åå¼æ°æ®å­å¨
  - åå¼æ°æ®æ¥è¯¢
  - æ°æ®èååæ
layer: Layer 5.1 (数据处理)
---

# ClickHouseåå¼å­å¨éæèå¾

## 核心定位

负责ClickHouse集成的设计与实现，基于列式存储技术，提供高性能数据分析能力，支持实时查询。


## æ ¸å¿å®ä½

**åä¸èè´£**: å¤§è§æ¨¡åå²æ°æ®çå­å¨ãæ¥è¯¢ååæï¼ä¸æ³¨äºOLAPåºæ¯

### èè´£è¾¹ç

| è´è´£ | ä¸è´è´?|
|------|--------|
| â?åå²è¡ææ°æ®å­å¨ï¼?0å¹?ï¼?| â?å®æ¶æ°æ®å­å¨ |
| â?åå¼èååæ | â?äºå¡å¤ç |
| â?ç©åè§å¾é¢è®¡ç®?| â?é«é¢åå¥ |
| â?æ°æ®åç¼©å­å¨ | â?å®æ¶æ¥è¯¢ |
| â?å¤æåææ¥è¯¢ | â?æ°æ®è®¢é |

---

## 1. ææ¯éå

### 1.1 ä¸ºä»ä¹éæ©ClickHouse

| ç¹æ?| ClickHouse | Apache Doris | Apache Druid |
|------|------------|--------------|--------------|
| æ¥è¯¢æ§è½ | â­â­â­â­â­?| â­â­â­â­ | â­â­â­â­â­?|
| åç¼©è½å | â­â­â­â­â­?| â­â­â­â­ | â­â­â­â­ |
| é¨ç½²å¤æåº?| â­â­â­â­ | â­â­â­?| â­â­ |
| å­¦ä¹ æ²çº¿ | â­â­â­â­ | â­â­â­?| â­â­ |
| Pythonæ¯æ | â?clickhouse-driver | â?pydoris | â?pydruid |
| åæºéç¨ | â?æ¯æ | â?æ¯æ | â?ééç¾¤ |
| ç¤¾åºæ´»è·åº?| â­â­â­â­â­?| â­â­â­â­ | â­â­â­â­ |
| **æ¨èææ°** | **â­â­â­â­â­?* | â­â­â­â­ | â­â­â­?|

### 1.2 æ ¸å¿ä¼å¿

1. **æè´æ§è½**: åæºæ¯ç§å¤çæ°äº¿è¡æ°æ?
2. **é«åç¼©æ¯**: åå¼å­å¨åç¼©æ¯å¯è¾?0:1
3. **SQLå¼å®¹**: æ¯ææ åSQLè¯­æ³
4. **åæºåå¥½**: ä¸ªäººå¼ååºæ¯æä½³éæ©

---

## 2. æ¶æè®¾è®¡

### 2.1 æ´ä½æ¶æ

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   ClickHouseéææ¶æ                            â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                                                                â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â? â?æ°æ®å¯¼å¥å±?  â?   â?æ°æ®å­å¨å±?  â?   â?æ°æ®æ¥è¯¢å±?  â?    â?
â? â?             â?   â?             â?   â?             â?    â?
â? â?â?æ¹éå¯¼å¥   â?   â?â?MergeTree  â?   â?â?èåæ¥è¯¢   â?    â?
â? â?â?å¢éå¯¼å¥   â?   â?â?ååºç­ç¥   â?   â?â?ç©åè§å¾   â?    â?
â? â?â?æ°æ®å½æ¡£   â?   â?â?TTLç­ç¥    â?   â?â?åæå½æ°   â?    â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â?        â?                  â?                   â?             â?
â?        âââââââââââââââââââââ´âââââââââââââââââââââ?             â?
â?                           â?                                   â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?                   æ°æ®åå±ç­ç¥                          â?  â?
â? â? â?ç­æ°æ? TimescaleDB (30å¤©å)                          â?  â?
â? â? â?æ¸©æ°æ? ClickHouse (1å¹´å)                            â?  â?
â? â? â?å·æ°æ? å¯¹è±¡å­å¨ (å½æ¡£)                               â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                                                                â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### 2.2 æ°æ®æ¨¡åè®¾è®¡

```sql
-- åå²è¡ææ°æ®è¡?
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

-- å å­åå²æ°æ®è¡?
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

-- è´¢å¡æ°æ®è¡?
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

## 3. æ ¸å¿åè½å®ç°

### 3.1 ç©åè§å¾

```sql
-- æ¥æ¶çç»è®¡ç©åè§å?
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

-- å å­ç»è®¡ç©åè§å¾
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

### 3.2 é«ææ¥è¯¢

```sql
-- æ¶é´èå´æ¥è¯¢
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

-- èååææ¥è¯¢
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

-- çªå£å½æ°æ¥è¯¢
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

## 4. Pythonæ¥å£è®¾è®¡

### 4.1 æ°æ®åå¥æ¥å£

```python
from typing import List, Dict, Optional
from datetime import datetime
from clickhouse_driver import Client
import pandas as pd

class ClickHouseWriter:
    """ClickHouseæ°æ®åå¥å?""
    
    def __init__(self, host: str, port: int = 9000, database: str = 'zephyr'):
        self.client = Client(host=host, port=port, database=database)
    
    def write_klines(self, klines: pd.DataFrame) -> int:
        """æ¹éåå¥Kçº¿æ°æ?""
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
        """æ¹éåå¥å å­æ°æ®"""
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

### 4.2 æ°æ®æ¥è¯¢æ¥å£

```python
class ClickHouseReader:
    """ClickHouseæ°æ®æ¥è¯¢å?""
    
    def __init__(self, host: str, port: int = 9000, database: str = 'zephyr'):
        self.client = Client(host=host, port=port, database=database)
    
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """è·åKçº¿æ°æ?""
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
        """è·åå å­æªé¢æ°æ®"""
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

## 5. é¨ç½²éç½®

### 5.1 Dockeré¨ç½²

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
      - "8123:8123"  # HTTPæ¥å£
      - "9000:9000"  # Nativeæ¥å£
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

### 5.2 éç½®ä¼å

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

## ð åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**ææ¡£ç»æ**
