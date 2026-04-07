---
module_id: UNIFIED_DATA_INFRASTRUCTURE__001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: ä¸ªäººå¼åè?
standard_type: 专业量化机构文档
responsibility:
  - 数据采集框架
  - 数据存储架构
  - 数据处理引擎
  - 基础设施管理
layer: Layer 5 (策略执行层)
---


## 核心定位

负责统一数据基础设施的设计与实现，构建统一的数据平台架构，提供数据存储、计算和服务功能，支持数据管理。

# UNIFIED DATA INFRASTRUCTURE BLUEPRINT

> **核心职责**: 统一数据基础设施，构建数据采集、存储和处理框架
> **职责边界**: 
> - â?æ¬ææ¡£è´è´£ï¼æ°æ®ééãæ°æ®å­å¨ã...


## 设计目标

### 主要目标

1. **功能完整性**: 确保UNIFIED DATA INFRASTRUCTURE功能完整，满足业务需求
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

采用UNIFIED DATA INFRASTRUCTURE化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控


## 核心定位

**单一职责**: 统一数据基础设施，构建统一的数据采集、存储和处理基础设施

### 职责边界

**â?æ ¸å¿èè´£**:

- 数据采集框架
- 数据存储架构
- 数据处理引擎
- 基础设施管理

**â?éèè´£èå?*:
- 业务数据处理
- 数据质量监控
- 数据治理

## ð¯ æ¨¡åå®ä½ä¸èè´?

### 层级定位

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?          æ¸
é£éåç³»ç» - ä¸çº§æ¶é´æ¡æ¶æ¶æ                â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â? ç¬¬ä¸çº§ï¼å®è§é
ç½®å±ï¼å­£åº¦/å¹´åº¦ï¼?                        â?
â? ç¬¬äºçº§ï¼ä¸­è§ç­ç¥å±ï¼å¨åº¦/æ¥åº¦ï¼?                        â?
â? ç¬¬ä¸çº§ï¼å¾®è§æ§è¡å±ï¼æ¥å
/åé/ç§çº§ï¼?                   â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?          ç»ä¸æ°æ®åºç¡è®¾æ½ï¼æ¬æ¨¡åï¼?                    â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â? æ°æ®æºéé
å±? â? æ°æ®æ¹å­å¨å±  â? æ°æ®APIå±?    â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### 核心职责

| èè´£ç±»å« | å
·ä½èè´£ | è¾åºäº§ç© |
|---------|---------|---------|
| **æ°æ®éé** | å¤æºæ°æ®ééãå®æ¶æ°æ®è®¢é?| åå§æ°æ®æµ?|
| **æ°æ®å­å¨** | æ¶åºæ°æ®å­å¨ãåå²æ°æ®å½æ¡?| æ°æ®æ¹ãæ°æ®ä»åº?|
| **æ°æ®è®¿é®** | ç»ä¸æ°æ®APIãæ°æ®æ¥è¯¢æå?| æ°æ®è®¿é®æ¥å£ |
| **æ°æ®ç®¡ç** | æ°æ®çå½å¨æç®¡çãæ°æ®æ²»ç?| æ°æ®ç®å½ãè¡ç¼å
³ç³?|
| **æ°æ®è´¨é** | æ°æ®è´¨éçæ§ãå¼å¸¸æ£æµ?| è´¨éæ¥åãåè­?|

### éèè´£è¾¹ç?

- â?**å å­è®¡ç®**: ç±å å­è®¡ç®å¨æ¨¡åè´è´£
- â?**ç­ç¥é»è¾**: ç±ç­ç¥å¼ææ¨¡åè´è´?
- â?**äº¤ææ§è¡**: ç±äº¤ææ§è¡å¼æè´è´?
- â?**é£é©è®¡ç®**: ç±é£é©ç®¡çç³»ç»è´è´?

---

## ðï¸?æ¶æè®¾è®¡

### 整体架构

```mermaid
graph TB
    subgraph "数据源层"
        A1[宏观经济数据源]
        A2[æ¥é¢è¡æ
数据源]
        A3[æ¥å
è¡æ
数据源]
        A4[å®æ¶è¡æ
数据源]
        A5[另类数据源]
    end
    
    subgraph "æ°æ®ééå±?
        B1[批量采集器]
        B2[流式采集器]
        B3[å®æ¶è®¢é
器]
        B4[æ°æ®éé
å¨]
    end
    
    subgraph "æ°æ®å­å¨å±?
        C1[æ¶åºæ°æ®åº?br/>InfluxDB/QuestDB]
        C2[æ°æ®æ¹?br/>Delta Lake]
        C3[ç¼å­å±?br/>Redis]
        C4[归档存储<br/>对象存储]
    end
    
    subgraph "æ°æ®å¤çå±?
        D1[æ°æ®æ¸
洗]
        D2[数据标准化]
        D3[数据聚合]
        D4[数据质量检查]
    end
    
    subgraph "æ°æ®æå¡å±?
        E1[统一数据API]
        E2[数据查询服务]
        E3[æ°æ®è®¢é
服务]
        E4[数据目录服务]
    end
    
    subgraph "åºç¨å±?
        F1[å®è§é
ç½®å±]
        F2[中观策略层]
        F3[微观执行层]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B2
    A4 --> B3
    A5 --> B1
    
    B1 --> B4
    B2 --> B4
    B3 --> B4
    
    B4 --> C1
    B4 --> C2
    B4 --> C3
    
    C1 --> D1
    C2 --> D1
    C3 --> D1
    
    D1 --> D2
    D2 --> D3
    D3 --> D4
    
    D4 --> E1
    D4 --> E2
    D4 --> E3
    D4 --> E4
    
    E1 --> F1
    E1 --> F2
    E1 --> F3
    E2 --> F1
    E2 --> F2
    E3 --> F3
    E4 --> F1
    E4 --> F2
```

### æ°æ®æµè®¾è®?

#### å®è§æ°æ®æµï¼å­£åº¦/å¹´åº¦ï¼?

```
å®è§ç»æµæ°æ®æº?â?æ¹éééå?â?æ°æ®éé
å?â?æ°æ®æ¹?â?æ°æ®æ¸
æ´ â?æ°æ®æ åå?â?ç»ä¸API â?å®è§é
ç½®å±?
```

**特点**:
- ä½é¢æ´æ°ï¼æåº?å­£åº¦ï¼?
- 数据量小但重要性高
- éè¦åå²æ°æ®å®æ?

#### æ¥é¢æ°æ®æµï¼å¨åº¦/æ¥åº¦ï¼?

```
æ¥é¢è¡æ
æ°æ®æº?â?æ¹éééå?â?æ°æ®éé
å?â?æ°æ®æ¹?â?æ°æ®æ¸
æ´ â?æ°æ®æ åå?â?ç»ä¸API â?ä¸­è§ç­ç¥å±?
```

**特点**:
- 每日更新
- æ°æ®éä¸­ç­?
- éè¦å¿«éæ¥è¯?

#### æ¥å
数据流（分钟级）

```
æ¥å
è¡æ
æ°æ®æº?â?æµå¼ééå?â?æ°æ®éé
å?â?æ¶åºæ°æ®åº?â?æ°æ®æ¸
æ´ â?æ°æ®èå â?ç»ä¸API â?ä¸­è§ç­ç¥å±?
```

**特点**:
- åéçº§æ´æ?
- 数据量大
- éè¦é«æå­å?

#### å®æ¶æ°æ®æµï¼ç§çº§ï¼?

```
å®æ¶è¡æ
æ°æ®æº?â?å®æ¶è®¢é
å?â?æ°æ®éé
å?â?ç¼å­å±?â?æ°æ®è´¨éæ£æ?â?æ°æ®è®¢é
æå¡ â?å¾®è§æ§è¡å±?
```

**特点**:
- 秒级更新
- è¶
低延迟要求
- éè¦é«å¯ç¨æ?

---

## ð§ å
³é®ç»ä»¶è®¾è®¡

### 1. æ°æ®æºéé
å?(Data Source Adapter)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

class DataSourceAdapter(ABC):
    """æ°æ®æºéé
å¨åºç±?""
    
    @abstractmethod
    def connect(self) -> bool:
        """建立连接"""
        pass
    
    @abstractmethod
    def fetch(self, params: Dict[str, Any]) -> pd.DataFrame:
        """获取数据"""
        pass
    
    @abstractmethod
    def subscribe(self, callback: callable) -> None:
        """è®¢é
实时数据"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass


class MacroDataSourceAdapter(DataSourceAdapter):
    """å®è§ç»æµæ°æ®æºéé
å?""
    
    def __init__(self, source_config: Dict[str, Any]):
        self.source_config = source_config
        self.connection = None
        
    def connect(self) -> bool:
        """è¿æ¥å®è§ç»æµæ°æ®æº?""
        # 实现连接逻辑
        # 支持的数据源：Wind、同花顺iFinD、东方财富Choice
        pass
    
    def fetch(self, params: Dict[str, Any]) -> pd.DataFrame:
        """获取宏观经济数据"""
        # params示例:
        # {
        #     'indicators': ['GDP', 'CPI', 'PMI'],
        #     'start_date': '2020-01-01',
        #     'end_date': '2024-12-31',
        #     'frequency': 'monthly'
        # }
        pass
    
    def subscribe(self, callback: callable) -> None:
        """å®è§ç»æµæ°æ®éå¸¸ä¸éè¦å®æ¶è®¢é?""
        pass
    
    def disconnect(self) -> None:
        """断开连接"""
        pass


class DailyMarketDataSourceAdapter(DataSourceAdapter):
    """æ¥é¢è¡æ
æ°æ®æºéé
å?""
    
    def __init__(self, source_config: Dict[str, Any]):
        self.source_config = source_config
        self.connection = None
        
    def connect(self) -> bool:
        """è¿æ¥æ¥é¢è¡æ
æ°æ®æº?""
        # æ¯æçæ°æ®æºï¼TushareãAKShareãèå®½ãç±³ç­?
        pass
    
    def fetch(self, params: Dict[str, Any]) -> pd.DataFrame:
        """è·åæ¥é¢è¡æ
数据"""
        # params示例:
        # {
        #     'symbols': ['000001.SZ', '000002.SZ'],
        #     'start_date': '2024-01-01',
        #     'end_date': '2024-12-31',
        #     'fields': ['open', 'high', 'low', 'close', 'volume']
        # }
        pass
    
    def subscribe(self, callback: callable) -> None:
        """æ¥é¢æ°æ®éå¸¸ä¸éè¦å®æ¶è®¢é?""
        pass
    
    def disconnect(self) -> None:
        """断开连接"""
        pass


class IntradayMarketDataSourceAdapter(DataSourceAdapter):
    """æ¥å
è¡æ
æ°æ®æºéé
å?""
    
    def __init__(self, source_config: Dict[str, Any]):
        self.source_config = source_config
        self.connection = None
        
    def connect(self) -> bool:
        """è¿æ¥æ¥å
è¡æ
æ°æ®æº?""
        # æ¯æçæ°æ®æºï¼QMTãèå®½ãç±³ç­?
        pass
    
    def fetch(self, params: Dict[str, Any]) -> pd.DataFrame:
        """è·åæ¥å
è¡æ
数据"""
        # params示例:
        # {
        #     'symbol': '000001.SZ',
        #     'date': '2024-12-01',
        #     'frequency': '1min',
        #     'fields': ['open', 'high', 'low', 'close', 'volume']
        # }
        pass
    
    def subscribe(self, callback: callable) -> None:
        """è®¢é
æ¥å
实时数据"""
        # å®ç°å®æ¶è®¢é
逻辑
        pass
    
    def disconnect(self) -> None:
        """断开连接"""
        pass


class RealtimeMarketDataSourceAdapter(DataSourceAdapter):
    """å®æ¶è¡æ
æ°æ®æºéé
å?""
    
    def __init__(self, source_config: Dict[str, Any]):
        self.source_config = source_config
        self.connection = None
        self.websocket = None
        
    def connect(self) -> bool:
        """è¿æ¥å®æ¶è¡æ
æ°æ®æº?""
        # æ¯æçæ°æ®æºï¼QMTãä¸æ¹è´¢å¯ãéè¾¾ä¿?
        pass
    
    def fetch(self, params: Dict[str, Any]) -> pd.DataFrame:
        """实时数据通常不使用fetch，而是使用subscribe"""
        pass
    
    def subscribe(self, callback: callable) -> None:
        """è®¢é
å®æ¶è¡æ
数据"""
        # å®ç°WebSocketè®¢é
逻辑
        pass
    
    def disconnect(self) -> None:
        """断开连接"""
        pass
```

### 2. 数据湖存储层 (Data Lake Storage)

```python
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
import delta
import pyspark.sql.functions as F

class DataLakeStorage:
    """数据湖存储层 - Delta Lake实现"""
    
    def __init__(self, spark_session, base_path: str):
        self.spark = spark_session
        self.base_path = base_path
        
    def store_macro_data(self, data: pd.DataFrame, table_name: str) -> None:
        """存储宏观经济数据"""
        # 转换为Spark DataFrame
        spark_df = self.spark.createDataFrame(data)
        
        # åå
¥Deltaè¡?
        spark_df.write.format("delta") \
            .mode("overwrite") \
            .partitionBy("indicator_code") \
            .save(f"{self.base_path}/macro/{table_name}")
    
    def store_daily_data(self, data: pd.DataFrame, table_name: str) -> None:
        """å­å¨æ¥é¢è¡æ
数据"""
        spark_df = self.spark.createDataFrame(data)
        
        # åå
¥Deltaè¡¨ï¼ææ¥æåå?
        spark_df.write.format("delta") \
            .mode("append") \
            .partitionBy("trade_date") \
            .save(f"{self.base_path}/daily/{table_name}")
    
    def store_intraday_data(self, data: pd.DataFrame, table_name: str) -> None:
        """å­å¨æ¥å
è¡æ
数据"""
        spark_df = self.spark.createDataFrame(data)
        
        # åå
¥Deltaè¡¨ï¼ææ¥æåè¡ç¥¨ä»£ç ååº
        spark_df.write.format("delta") \
            .mode("append") \
            .partitionBy("trade_date", "symbol") \
            .save(f"{self.base_path}/intraday/{table_name}")
    
    def query_macro_data(self, 
                        indicators: List[str],
                        start_date: str,
                        end_date: str) -> pd.DataFrame:
        """查询宏观经济数据"""
        query = f"""
        SELECT * FROM delta.`{self.base_path}/macro/macro_indicators`
        WHERE indicator_code IN ({','.join([f"'{i}'" for i in indicators])})
        AND date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY date
        """
        return self.spark.sql(query).toPandas()
    
    def query_daily_data(self,
                        symbols: List[str],
                        start_date: str,
                        end_date: str,
                        fields: List[str]) -> pd.DataFrame:
        """æ¥è¯¢æ¥é¢è¡æ
数据"""
        query = f"""
        SELECT {','.join(fields)} FROM delta.`{self.base_path}/daily/market_data`
        WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
        AND trade_date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY symbol, trade_date
        """
        return self.spark.sql(query).toPandas()
    
    def query_intraday_data(self,
                           symbol: str,
                           date: str,
                           frequency: str = '1min') -> pd.DataFrame:
        """æ¥è¯¢æ¥å
è¡æ
数据"""
        query = f"""
        SELECT * FROM delta.`{self.base_path}/intraday/{frequency}_data`
        WHERE symbol = '{symbol}'
        AND trade_date = '{date}'
        ORDER BY timestamp
        """
        return self.spark.sql(query).toPandas()
    
    def compact_data(self, table_path: str) -> None:
        """压缩Delta表，优化查询性能"""
        self.spark.sql(f"OPTIMIZE delta.`{table_path}`")
    
    def vacuum_data(self, table_path: str, retention_hours: int = 168) -> None:
        """æ¸
理旧版本数据，释放存储空间"""
        self.spark.sql(f"VACUUM delta.`{table_path}` RETAIN {retention_hours} HOURS")
```

### 3. æ¶åºæ°æ®åºå­å?(Time Series Database)

```python
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

class TimeSeriesDBStorage:
    """æ¶åºæ°æ®åºå­å?- InfluxDBå®ç°"""
    
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.bucket = bucket
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        
    def write_realtime_data(self, 
                           measurement: str,
                           tags: Dict[str, str],
                           fields: Dict[str, Any],
                           timestamp: datetime) -> None:
        """åå
¥å®æ¶æ°æ®"""
        point = Point(measurement) \
            .time(timestamp, WritePrecision.NS)
        
        for tag_key, tag_value in tags.items():
            point.tag(tag_key, tag_value)
        
        for field_key, field_value in fields.items():
            point.field(field_key, field_value)
        
        self.write_api.write(bucket=self.bucket, record=point)
    
    def write_batch_realtime_data(self, 
                                  measurement: str,
                                  data: pd.DataFrame,
                                  tag_columns: List[str]) -> None:
        """æ¹éåå
¥å®æ¶æ°æ®"""
        points = []
        for _, row in data.iterrows():
            point = Point(measurement) \
                .time(row['timestamp'], WritePrecision.NS)
            
            for tag_col in tag_columns:
                point.tag(tag_col, str(row[tag_col]))
            
            for col in data.columns:
                if col not in tag_columns and col != 'timestamp':
                    point.field(col, row[col])
            
            points.append(point)
        
        self.write_api.write(bucket=self.bucket, record=points)
    
    def query_realtime_data(self,
                           measurement: str,
                           symbol: str,
                           start_time: datetime,
                           end_time: datetime,
                           fields: List[str]) -> pd.DataFrame:
        """查询实时数据"""
        query = f'''
        from(bucket: "{self.bucket}")
        |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
        |> filter(fn: (r) => r._measurement == "{measurement}")
        |> filter(fn: (r) => r.symbol == "{symbol}")
        |> filter(fn: (r) => contains(value: r._field, set: {fields}))
        '''
        
        result = self.query_api.query_data_frame(query)
        return result
    
    def query_latest_data(self, measurement: str, symbol: str) -> pd.DataFrame:
        """æ¥è¯¢ææ°æ°æ?""
        query = f'''
        from(bucket: "{self.bucket}")
        |> range(start: -5m)
        |> filter(fn: (r) => r._measurement == "{measurement}")
        |> filter(fn: (r) => r.symbol == "{symbol}")
        |> last()
        '''
        
        result = self.query_api.query_data_frame(query)
        return result
```

### 4. 统一数据API (Unified Data API)

```python
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="统一数据API")


class MacroDataRequest(BaseModel):
    """宏观经济数据请求"""
    indicators: List[str]
    start_date: str
    end_date: str
    frequency: str = 'monthly'


class DailyDataRequest(BaseModel):
    """日频数据请求"""
    symbols: List[str]
    start_date: str
    end_date: str
    fields: List[str]


class IntradayDataRequest(BaseModel):
    """æ¥å
数据请求"""
    symbol: str
    date: str
    frequency: str = '1min'
    fields: Optional[List[str]] = None


class UnifiedDataAPI:
    """统一数据API"""
    
    def __init__(self, 
                 data_lake: DataLakeStorage,
                 time_series_db: TimeSeriesDBStorage,
                 cache_client):
        self.data_lake = data_lake
        self.time_series_db = time_series_db
        self.cache = cache_client
        
    @app.post("/api/v1/macro/data")
    async def get_macro_data(self, request: MacroDataRequest) -> Dict[str, Any]:
        """获取宏观经济数据"""
        # 1. æ£æ¥ç¼å­?
        cache_key = f"macro:{':'.join(request.indicators)}:{request.start_date}:{request.end_date}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return {
                'status': 'success',
                'data': cached_data,
                'source': 'cache'
            }
        
        # 2. 从数据湖查询
        try:
            data = self.data_lake.query_macro_data(
                indicators=request.indicators,
                start_date=request.start_date,
                end_date=request.end_date
            )
            
            # 3. åå
¥ç¼å­
            self.cache.set(cache_key, data.to_dict(), expire=3600)  # 1小时过期
            
            return {
                'status': 'success',
                'data': data.to_dict(),
                'source': 'data_lake'
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/daily/data")
    async def get_daily_data(self, request: DailyDataRequest) -> Dict[str, Any]:
        """è·åæ¥é¢è¡æ
数据"""
        # 1. æ£æ¥ç¼å­?
        cache_key = f"daily:{':'.join(request.symbols)}:{request.start_date}:{request.end_date}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return {
                'status': 'success',
                'data': cached_data,
                'source': 'cache'
            }
        
        # 2. 从数据湖查询
        try:
            data = self.data_lake.query_daily_data(
                symbols=request.symbols,
                start_date=request.start_date,
                end_date=request.end_date,
                fields=request.fields
            )
            
            # 3. åå
¥ç¼å­
            self.cache.set(cache_key, data.to_dict(), expire=1800)  # 30分钟过期
            
            return {
                'status': 'success',
                'data': data.to_dict(),
                'source': 'data_lake'
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/intraday/data")
    async def get_intraday_data(self, request: IntradayDataRequest) -> Dict[str, Any]:
        """è·åæ¥å
è¡æ
数据"""
        # 1. æ£æ¥ç¼å­?
        cache_key = f"intraday:{request.symbol}:{request.date}:{request.frequency}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return {
                'status': 'success',
                'data': cached_data,
                'source': 'cache'
            }
        
        # 2. 从数据湖查询
        try:
            data = self.data_lake.query_intraday_data(
                symbol=request.symbol,
                date=request.date,
                frequency=request.frequency
            )
            
            # 3. åå
¥ç¼å­
            self.cache.set(cache_key, data.to_dict(), expire=300)  # 5分钟过期
            
            return {
                'status': 'success',
                'data': data.to_dict(),
                'source': 'data_lake'
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/realtime/data/{symbol}")
    async def get_realtime_data(self, symbol: str) -> Dict[str, Any]:
        """è·åå®æ¶è¡æ
数据"""
        try:
            # ä»æ¶åºæ°æ®åºæ¥è¯¢ææ°æ°æ?
            data = self.time_series_db.query_latest_data(
                measurement='realtime_quotes',
                symbol=symbol
            )
            
            return {
                'status': 'success',
                'data': data.to_dict(),
                'source': 'time_series_db'
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/data/catalog")
    async def get_data_catalog(self) -> Dict[str, Any]:
        """获取数据目录"""
        # 返回可用的数据集列表
        catalog = {
            'macro': {
                'indicators': ['GDP', 'CPI', 'PMI', 'M2', 'Industrial_Output'],
                'frequency': ['monthly', 'quarterly', 'yearly'],
                'date_range': ['2000-01-01', '2024-12-31']
            },
            'daily': {
                'symbols': ['000001.SZ', '000002.SZ', '...'],
                'fields': ['open', 'high', 'low', 'close', 'volume', 'amount'],
                'date_range': ['2010-01-01', '2024-12-31']
            },
            'intraday': {
                'symbols': ['000001.SZ', '000002.SZ', '...'],
                'frequency': ['1min', '5min', '15min', '30min', '60min'],
                'date_range': ['2020-01-01', '2024-12-31']
            },
            'realtime': {
                'symbols': ['000001.SZ', '000002.SZ', '...'],
                'fields': ['price', 'volume', 'bid', 'ask', 'last']
            }
        }
        
        return {
            'status': 'success',
            'catalog': catalog
        }
```

### 5. æ°æ®è®¢é
服务 (Data Subscription Service)

```python
from typing import Dict, Any, Callable, List
import asyncio
import websockets
import json
from datetime import datetime

class DataSubscriptionService:
    """æ°æ®è®¢é
服务"""
    
    def __init__(self, realtime_adapter: RealtimeMarketDataSourceAdapter):
        self.realtime_adapter = realtime_adapter
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.websocket_clients: List[websockets.WebSocketServerProtocol] = []
        
    async def subscribe_realtime_quotes(self, 
                                        symbols: List[str],
                                        callback: Callable) -> str:
        """è®¢é
å®æ¶è¡æ
"""
        subscription_id = f"sub_{datetime.now().timestamp()}"
        
        # 注册回调函数
        for symbol in symbols:
            if symbol not in self.subscriptions:
                self.subscriptions[symbol] = []
            self.subscriptions[symbol].append(callback)
        
        # è¿æ¥æ°æ®æºå¹¶è®¢é

        await self.realtime_adapter.connect()
        await self.realtime_adapter.subscribe(
            callback=self._handle_realtime_data
        )
        
        return subscription_id
    
    async def _handle_realtime_data(self, data: Dict[str, Any]) -> None:
        """处理实时数据"""
        symbol = data.get('symbol')
        
        # è°ç¨ææè®¢é
äºè¯¥symbolçåè°å½æ?
        if symbol in self.subscriptions:
            for callback in self.subscriptions[symbol]:
                try:
                    await callback(data)
                except Exception as e:
                    print(f"Callback error: {e}")
        
        # æ¨éç»WebSocketå®¢æ·ç«?
        await self._broadcast_to_websocket(data)
    
    async def _broadcast_to_websocket(self, data: Dict[str, Any]) -> None:
        """å¹¿æ­æ°æ®ç»WebSocketå®¢æ·ç«?""
        if self.websocket_clients:
            message = json.dumps(data)
            await asyncio.gather(
                *[client.send(message) for client in self.websocket_clients]
            )
    
    async def handle_websocket_client(self, 
                                      websocket: websockets.WebSocketServerProtocol,
                                      path: str) -> None:
        """å¤çWebSocketå®¢æ·ç«¯è¿æ?""
        self.websocket_clients.append(websocket)
        
        try:
            async for message in websocket:
                # å¤çå®¢æ·ç«¯æ¶æ?
                request = json.loads(message)
                # å¯ä»¥å®ç°è®¢é
/åæ¶è®¢é
逻辑
        finally:
            self.websocket_clients.remove(websocket)
    
    async def unsubscribe(self, subscription_id: str) -> None:
        """åæ¶è®¢é
"""
        # å®ç°åæ¶è®¢é
逻辑
        pass
```

---

## 📊 数据模型设计

### 宏观经济数据模型

```sql
CREATE TABLE macro_indicators (
    indicator_code VARCHAR(50) NOT NULL COMMENT '指标代码',
    indicator_name VARCHAR(100) NOT NULL COMMENT '指标名称',
    date DATE NOT NULL COMMENT '日期',
    value DECIMAL(20, 6) COMMENT 'ææ å?,
    unit VARCHAR(20) COMMENT '单位',
    frequency VARCHAR(20) COMMENT 'é¢çï¼monthly/quarterly/yearlyï¼?,
    source VARCHAR(50) COMMENT 'æ°æ®æº?,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (indicator_code, date)
) COMMENT 'å®è§ç»æµææ è¡?;
```

### æ¥é¢è¡æ
数据模型

```sql
CREATE TABLE daily_market_data (
    symbol VARCHAR(20) NOT NULL COMMENT '股票代码',
    trade_date DATE NOT NULL COMMENT '交易日期',
    open DECIMAL(10, 3) COMMENT '开盘价',
    high DECIMAL(10, 3) COMMENT '最高价',
    low DECIMAL(10, 3) COMMENT '最低价',
    close DECIMAL(10, 3) COMMENT 'æ¶çä»?,
    volume BIGINT COMMENT 'æäº¤é?,
    amount DECIMAL(20, 2) COMMENT 'æäº¤é¢?,
    turnover_rate DECIMAL(10, 4) COMMENT 'æ¢æç?,
    pe_ttm DECIMAL(10, 2) COMMENT '市盈率TTM',
    pb DECIMAL(10, 2) COMMENT 'å¸åç?,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (symbol, trade_date)
) COMMENT 'æ¥é¢è¡æ
æ°æ®è¡?;
```

### æ¥å
è¡æ
数据模型

```sql
CREATE TABLE intraday_market_data (
    symbol VARCHAR(20) NOT NULL COMMENT '股票代码',
    trade_date DATE NOT NULL COMMENT '交易日期',
    timestamp TIMESTAMP NOT NULL COMMENT 'æ¶é´æ?,
    frequency VARCHAR(10) NOT NULL COMMENT 'é¢çï¼?min/5min/15min/30min/60minï¼?,
    open DECIMAL(10, 3) COMMENT '开盘价',
    high DECIMAL(10, 3) COMMENT '最高价',
    low DECIMAL(10, 3) COMMENT '最低价',
    close DECIMAL(10, 3) COMMENT 'æ¶çä»?,
    volume BIGINT COMMENT 'æäº¤é?,
    amount DECIMAL(20, 2) COMMENT 'æäº¤é¢?,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (symbol, trade_date, timestamp, frequency)
) COMMENT 'æ¥å
è¡æ
æ°æ®è¡?;
```

---

## 🔌 接口规范

### RESTful API接口

#### 1. 获取宏观经济数据

```
POST /api/v1/macro/data
Content-Type: application/json

Request:
{
    "indicators": ["GDP", "CPI", "PMI"],
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "frequency": "monthly"
}

Response:
{
    "status": "success",
    "data": {
        "GDP": [...],
        "CPI": [...],
        "PMI": [...]
    },
    "source": "data_lake",
    "timestamp": "2024-12-01T10:00:00Z"
}
```

#### 2. è·åæ¥é¢è¡æ
数据

```
POST /api/v1/daily/data
Content-Type: application/json

Request:
{
    "symbols": ["000001.SZ", "000002.SZ"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "fields": ["open", "high", "low", "close", "volume"]
}

Response:
{
    "status": "success",
    "data": {
        "000001.SZ": [...],
        "000002.SZ": [...]
    },
    "source": "data_lake",
    "timestamp": "2024-12-01T10:00:00Z"
}
```

#### 3. è·åæ¥å
è¡æ
数据

```
POST /api/v1/intraday/data
Content-Type: application/json

Request:
{
    "symbol": "000001.SZ",
    "date": "2024-12-01",
    "frequency": "1min",
    "fields": ["open", "high", "low", "close", "volume"]
}

Response:
{
    "status": "success",
    "data": [...],
    "source": "data_lake",
    "timestamp": "2024-12-01T10:00:00Z"
}
```

#### 4. è·åå®æ¶è¡æ
数据

```
GET /api/v1/realtime/data/{symbol}

Response:
{
    "status": "success",
    "data": {
        "symbol": "000001.SZ",
        "price": 10.50,
        "volume": 1000000,
        "bid": 10.49,
        "ask": 10.51,
        "last": 10.50,
        "timestamp": "2024-12-01T10:00:00Z"
    },
    "source": "time_series_db"
}
```

### WebSocket接口

#### è®¢é
å®æ¶è¡æ


```
WebSocket: ws://localhost:8000/ws/realtime

Subscribe:
{
    "action": "subscribe",
    "symbols": ["000001.SZ", "000002.SZ"]
}

Message:
{
    "symbol": "000001.SZ",
    "price": 10.50,
    "volume": 1000000,
    "timestamp": "2024-12-01T10:00:00Z"
}

Unsubscribe:
{
    "action": "unsubscribe",
    "symbols": ["000001.SZ"]
}
```

---

## 🚀 实施要点

### 阶段1：基础设施搭建（第1周）

**任务**:
1. â?é¨ç½²Apache Sparkéç¾¤
2. â?é
ç½®Delta Lakeå­å¨
3. â?é¨ç½²InfluxDBæ¶åºæ°æ®åº?
4. â?é
ç½®Redisç¼å­
5. â?æ­å»ºFastAPIæå¡æ¡æ¶

**验收标准**:
- Spark集群正常运行
- Delta Lake可以读写数据
- InfluxDB可以存储时序数据
- Redis缓存可用
- FastAPIæå¡å¯è®¿é?

---

### é¶æ®µ2ï¼æ°æ®æºéé
å¨å¼åï¼ç¬?å¨ï¼

**任务**:
1. â?å®ç°å®è§ç»æµæ°æ®æºéé
å?
2. â?å®ç°æ¥é¢è¡æ
æ°æ®æºéé
å?
3. â?å®ç°æ¥å
è¡æ
æ°æ®æºéé
å?
4. â?å®ç°å®æ¶è¡æ
æ°æ®æºéé
å?
5. â?ç¼åæ°æ®æºéé
å¨åå
æµè¯?

**验收标准**:
- æææ°æ®æºéé
å¨å¯ä»¥æ­£å¸¸è¿æ?
- 可以从数据源获取数据
- åå
æµè¯è¦ççâ¥80%

---

### é¶æ®µ3ï¼æ°æ®å­å¨å±å¼åï¼ç¬?-3å¨ï¼

**任务**:
1. â?å®ç°æ°æ®æ¹å­å¨å±
2. â?å®ç°æ¶åºæ°æ®åºå­å¨å±
3. â?å®ç°æ°æ®æ¸
洗和标准化
4. â?å®ç°æ°æ®èååè½
5. â?ç¼åå­å¨å±åå
æµè¯?

**验收标准**:
- æ°æ®å¯ä»¥æ­£å¸¸åå
¥Delta Lake
- æ¶åºæ°æ®å¯ä»¥æ­£å¸¸åå
¥InfluxDB
- æ°æ®æ¸
洗和标准化正确
- åå
æµè¯è¦ççâ¥80%

---

### é¶æ®µ4ï¼æ°æ®æå¡å±å¼åï¼ç¬?å¨ï¼

**任务**:
1. â?å®ç°ç»ä¸æ°æ®API
2. â?å®ç°æ°æ®è®¢é
服务
3. â?å®ç°æ°æ®ç®å½æå¡
4. â?å®ç°ç¼å­ç­ç¥
5. â?ç¼åæå¡å±åå
æµè¯?

**验收标准**:
- RESTful API可以正常访问
- WebSocketè®¢é
功能正常
- 缓存策略有效
- åå
æµè¯è¦ççâ¥80%

---

### 阶段5：集成测试与优化（第3周）

**任务**:
1. â?ç¼åéææµè¯ç¨ä¾
2. â?æ§è¡æ§è½æµè¯
3. â?ä¼åæ¥è¯¢æ§è½
4. â?ä¼åå­å¨æ§è½
5. â?ç¼åé¨ç½²ææ¡£

**验收标准**:
- éææµè¯å
¨é¨éè¿
- 查询响应时间<100ms（日频数据）
- 查询响应时间<10ms（实时数据）
- 部署文档完整

---

## 🧪 测试策略

### åå
æµè¯

```python
import pytest
import pandas as pd
from datetime import datetime

def test_macro_data_adapter_fetch():
    """æµè¯å®è§ç»æµæ°æ®æºéé
å?""
    adapter = MacroDataSourceAdapter(config)
    
    # è¿æ¥æ°æ®æº?
    assert adapter.connect() == True
    
    # 获取数据
    params = {
        'indicators': ['GDP', 'CPI'],
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'frequency': 'monthly'
    }
    data = adapter.fetch(params)
    
    # 验证数据
    assert isinstance(data, pd.DataFrame)
    assert len(data) > 0
    assert 'GDP' in data.columns
    assert 'CPI' in data.columns
    
    # 断开连接
    adapter.disconnect()


def test_data_lake_store_and_query():
    """测试数据湖存储和查询"""
    storage = DataLakeStorage(spark, base_path)
    
    # 存储数据
    test_data = pd.DataFrame({
        'symbol': ['000001.SZ', '000002.SZ'],
        'trade_date': ['2024-12-01', '2024-12-01'],
        'close': [10.0, 20.0]
    })
    
    storage.store_daily_data(test_data, 'test_table')
    
    # 查询数据
    result = storage.query_daily_data(
        symbols=['000001.SZ'],
        start_date='2024-12-01',
        end_date='2024-12-01',
        fields=['close']
    )
    
    assert len(result) == 1
    assert result['close'].iloc[0] == 10.0


def test_unified_data_api():
    """测试统一数据API"""
    client = TestClient(app)
    
    # 测试获取日频数据
    response = client.post("/api/v1/daily/data", json={
        "symbols": ["000001.SZ"],
        "start_date": "2024-12-01",
        "end_date": "2024-12-01",
        "fields": ["close"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert 'data' in data
```

### 集成测试

```python
def test_end_to_end_data_flow():
    """测试端到端数据流"""
    # 1. 从数据源获取数据
    adapter = DailyMarketDataSourceAdapter(config)
    adapter.connect()
    raw_data = adapter.fetch(params)
    
    # 2. 存储到数据湖
    storage = DataLakeStorage(spark, base_path)
    storage.store_daily_data(raw_data, 'market_data')
    
    # 3. 通过API查询数据
    client = TestClient(app)
    response = client.post("/api/v1/daily/data", json={
        "symbols": ["000001.SZ"],
        "start_date": "2024-12-01",
        "end_date": "2024-12-01",
        "fields": ["close"]
    })
    
    # 4. éªè¯æ°æ®ä¸è´æ?
    assert response.status_code == 200
    api_data = response.json()['data']
    assert api_data == raw_data.to_dict()
```

### 性能测试

```python
def test_query_performance():
    """测试查询性能"""
    import time
    
    client = TestClient(app)
    
    # 测试日频数据查询性能
    start_time = time.time()
    response = client.post("/api/v1/daily/data", json={
        "symbols": ["000001.SZ"] * 100,  # 100åªè¡ç¥?
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",  # 1å¹´æ°æ?
        "fields": ["open", "high", "low", "close", "volume"]
    })
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 0.1  # 100mså
å®æ?
    
    # 测试实时数据查询性能
    start_time = time.time()
    response = client.get("/api/v1/realtime/data/000001.SZ")
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 0.01  # 10mså
å®æ?
```

---

## 📈 性能指标

### 响应时间要求

| 数据类型 | 查询类型 | 响应时间要求 | 缓存策略 |
|---------|---------|------------|---------|
| **宏观经济数据** | 历史查询 | <1000ms | 1小时缓存 |
| **æ¥é¢è¡æ
数据** | 历史查询 | <100ms | 30分钟缓存 |
| **æ¥å
è¡æ
数据** | 历史查询 | <50ms | 5分钟缓存 |
| **å®æ¶è¡æ
æ°æ®** | å®æ¶æ¥è¯¢ | <10ms | æ ç¼å­?|

### ååéè¦æ±?

| æ°æ®ç±»å | åå
¥ååé?| æ¥è¯¢ååé?|
|---------|-----------|-----------|
| **å®è§ç»æµæ°æ®** | 100æ?ç§?| 1000æ¬?ç§?|
| **æ¥é¢è¡æ
æ°æ®** | 10000æ?ç§?| 10000æ¬?ç§?|
| **æ¥å
è¡æ
æ°æ®** | 100000æ?ç§?| 50000æ¬?ç§?|
| **å®æ¶è¡æ
æ°æ®** | 1000000æ?ç§?| 100000æ¬?ç§?|

### 存储容量规划

| æ°æ®ç±»å | æ¥å¢é?| å¹´å¢é?| å­å¨å¨æ |
|---------|--------|--------|---------|
| **å®è§ç»æµæ°æ®** | 1MB | 365MB | æ°¸ä¹
 |
| **æ¥é¢è¡æ
æ°æ®** | 100MB | 36GB | 10å¹?|
| **æ¥å
è¡æ
æ°æ®** | 10GB | 3.6TB | 3å¹?|
| **å®æ¶è¡æ
数据** | 100GB | 36TB | 1个月 |

---

## ð ç¸å
³ææ¡£

- ä¸ä¸å¤æ¶é´æ¡æ¶ç­ç¥æ¶æ?
- [数据质量监控系统蓝图](./DATA_QUALITY_MONITORING_BLUEPRINT.md)
- [数据治理平台蓝图](./DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md)
- æ¨¡åæ³¨åè¡?

---

## 📝 变更历史

| çæ¬ | æ¥æ | åæ´å
å®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**èå¾ç¶æ?*: â?è®¾è®¡å®æ
**ä¸ä¸æ­?*: å¼å§å®æ½é¶æ®? - åºç¡è®¾æ½æ­å»º

## 变更历史

| çæ¬ | æ¥æ | åæ´å
å®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.1 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active
---


---

## ð ç¸å
³ææ¡£

### 下游依赖

| 文档名称 | module_id | 依赖类型 | 说明 |
|---------|-----------|---------|------|
| [DATA SOURCE MANAGEMENT BLUEPRINT](./DATA_SOURCE_MANAGEMENT_BLUEPRINT.md) | DATA_SOURCE_MANAGEMENT_001 | å¼ºä¾èµ?| æä¾åºç¡è®¾æ½æ¯æ |
| [HIGH PERFORMANCE DATA PIPELINE BLUEPRINT](./HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md) | HIGH_PERFORMANCE_DATA_PIPELINE_001 | å¼ºä¾èµ?| æä¾æ°æ®å¤çå¼æ |
| [REALTIME DATA LAKE BLUEPRINT](./REALTIME_DATA_LAKE_BLUEPRINT.md) | REALTIME_DATA_LAKE_001 | å¼ºä¾èµ?| æä¾å­å¨æ¶æ |

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **Apache Spark** | 3.5+ | 数据处理 | [官方文档](https://spark.apache.org/) |
| **Apache Kafka** | 3.5+ | 消息队列 | [官方文档](https://kafka.apache.org/) |
| **PostgreSQL** | 15+ | å
³ç³»æ°æ®åº?| [å®æ¹ææ¡£](https://www.postgresql.org/) |
| **Redis** | 7.0+ | 缓存 | [官方文档](https://redis.io/) |

### å¼ç¨å
³ç³»å?

```mermaid
graph LR
    B["UNIFIED DATA IN"]
    B --> D0["DATA SOURCE MAN"]
    B --> D1["HIGH PERFORMANC"]
    B --> D2["REALTIME DATA L"]
    
    style B fill:#ff6b6b
    style D0 fill:#45b7d1
```

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 6: ç»åä¼åå±?
##### 6.001. Unified Data Infrastructure
- **模块ID**: UNIFIED_DATA_INFRASTRUCTURE_001
- **蓝图文档**: UNIFIED_DATA_INFRASTRUCTURE_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾
åå»?
- **èè´£**: å
¨ç³»ç»æ°æ®åºç¡è®¾æ½
- **ç¶æ?*: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Unified Data Infrastructure** | å
¨ç³»ç»æ°æ®åºç¡è®¾æ½ | **æ ¸å¿æ¨¡å** |

### 1.3 版本管理

| çæ¬ | æ¥æ | åæ´å
å®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active
