---
module_id: DATA_REALTIME_STREAMING_BP_001
version: 1.0.0
status: Blueprint
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席架构师
responsibility: 实时数据流处理架构与Kafka集成
standard_type: 模块蓝图
applicable_scope: 实时数据流平台
compliance_level: 专业标准
parent_document: ../INDEX.md
dependencies:
- Redpanda
- Apache Kafka (可选)
- confluent-kafka-python
---
---


# 实时数据流平台蓝图

> **核心职责**: 实时数据流平台蓝图的定义和实现
> **职责边界**: 
> - ✅ 本文档负责：蓝图设计和架构规划相关内容
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: 实时数据流平台设计蓝图
- 定义实时数据流架构
- 说明事件驱动数据处理方案
- 提供市场数据实时摄入方案

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 数据源索引 | [../INDEX.md](../INDEX.md) | 上级索引 | 数据源模块总索引 |
| 数据同步复制 | [../DATA_SYNC_REPLICATION/](../DATA_SYNC_REPLICATION/) | 协同模块 | CDC数据同步 |
| 数据管道 | [../07_DATA_PIPELINE/](../07_DATA_PIPELINE/) | 下游模块 | 数据处理管道 |

**职责边界**:
- ✅ 本文档负责: 实时数据流平台架构设计
- ❌ 本文档不负责: 具体数据源实现（由各CONNECTOR文档负责）

> 清风量化系统 v5.4 - 实时数据流模块
> **优先级**: 🟡 P1级（重要）
> **实施周期**: 1周
> **开源方案**: Redpanda (推荐) / Apache Kafka

---

## 1. 概述

### 1.1 定位与目标

**Layer定位**: Layer 0 - 数据源层

**核心定位**:
- 实时市场数据流处理
- 事件驱动架构支持
- 高吞吐量数据摄入

**业务价值**:
- 支持实时交易信号处理
- 降低数据延迟至毫秒级
- 支持多数据源实时汇聚

### 1.2 技术选型对比

| 特性 | Redpanda | Apache Kafka |
|------|----------|--------------|
| 部署复杂度 | ✅ 单二进制 | ⚠️ 需要ZooKeeper |
| 内存效率 | ✅ C++实现 | ⚠️ JVM依赖 |
| Kafka兼容 | ✅ 100%兼容 | ✅ 原生 |
| 运维成本 | ✅ 低 | ⚠️ 中等 |
| 个人开发适用 | ✅ 高 | 🟡 中等 |
| GitHub Stars | 9k+ | 28k+ |

**推荐方案**: **Redpanda** - 更适合个人开发者

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    实时数据流平台架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  市场数据源   │    │  新闻数据源   │    │  交易数据源   │      │
│  │  (iFind/QMT) │    │  (舆情API)   │    │  (券商接口)   │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Producer Layer (数据生产者)                  │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │   │
│  │  │Tick Prod│  │Bar Prod │  │News Prod│  │TradeProd│    │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘    │   │
│  └───────┼────────────┼────────────┼────────────┼─────────┘   │
│          │            │            │            │              │
│          ▼            ▼            ▼            ▼              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Redpanda Cluster (消息队列)                  │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  Topics:                                          │   │   │
│  │  │  • market.ticks (Tick数据)                       │   │   │
│  │  │  • market.bars (K线数据)                         │   │   │
│  │  │  • news.sentiment (舆情数据)                     │   │   │
│  │  │  • trade.signals (交易信号)                      │   │   │
│  │  │  • system.events (系统事件)                      │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                  │
│         ┌───────────────────┼───────────────────┐              │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Consumer 1   │    │ Consumer 2   │    │ Consumer 3   │      │
│  │ (实时存储)    │    │ (因子计算)    │    │ (风控监控)    │      │
│  │ QuestDB      │    │ Factor Engine│    │ Risk Monitor │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

#### 2.2.1 Producer（数据生产者）

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json
from confluent_kafka import Producer

@dataclass
class TickData:
    symbol: str
    timestamp: datetime
    price: float
    volume: float
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_volume: Optional[float] = None
    ask_volume: Optional[float] = None

class MarketDataProducer:
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'zephyr-market-producer',
            'compression.type': 'zstd',
            'batch.size': 32768,
            'linger.ms': 5,
        })
        
    async def publish_tick(self, tick: TickData):
        topic = f"market.ticks.{tick.symbol[:2].lower()}"
        
        message = {
            'symbol': tick.symbol,
            'timestamp': tick.timestamp.isoformat(),
            'price': tick.price,
            'volume': tick.volume,
            'bid_price': tick.bid_price,
            'ask_price': tick.ask_price,
            'bid_volume': tick.bid_volume,
            'ask_volume': tick.ask_volume,
        }
        
        self.producer.produce(
            topic=topic,
            key=tick.symbol.encode(),
            value=json.dumps(message).encode(),
            callback=self._delivery_callback
        )
        
    def _delivery_callback(self, err, msg):
        if err:
            print(f"Delivery failed: {err}")
        else:
            print(f"Delivered to {msg.topic()} [{msg.partition()}]")
            
    def flush(self):
        self.producer.flush()
```

#### 2.2.2 Consumer（数据消费者）

```python
from confluent_kafka import Consumer, KafkaError
import asyncio
from typing import Callable, List

class MarketDataConsumer:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "zephyr-consumer"
    ):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'latest',
            'enable.auto.commit': False,
        })
        
    def subscribe(self, topics: List[str]):
        self.consumer.subscribe(topics)
        
    async def consume(
        self,
        handler: Callable[[dict], None],
        max_messages: int = 1000
    ):
        messages_processed = 0
        
        while messages_processed < max_messages:
            msg = self.consumer.poll(1.0)
            
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error: {msg.error()}")
                    break
                    
            try:
                data = json.loads(msg.value().decode('utf-8'))
                await handler(data)
                self.consumer.commit(msg)
                messages_processed += 1
            except Exception as e:
                print(f"Error processing message: {e}")
                
    def close(self):
        self.consumer.close()
```

#### 2.2.3 Stream Processor（流处理器）

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

@dataclass
class OHLCVBar:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class TickToBarAggregator:
    def __init__(self, bar_interval: timedelta = timedelta(minutes=1)):
        self.bar_interval = bar_interval
        self.current_bars = defaultdict(dict)
        
    async def process_tick(self, tick: dict):
        symbol = tick['symbol']
        timestamp = datetime.fromisoformat(tick['timestamp'])
        price = tick['price']
        volume = tick['volume']
        
        bar_start = timestamp.replace(
            second=0, microsecond=0
        )
        
        if symbol not in self.current_bars:
            self.current_bars[symbol] = {
                'timestamp': bar_start,
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': volume,
            }
        else:
            bar = self.current_bars[symbol]
            
            if bar_start > bar['timestamp']:
                completed_bar = OHLCVBar(
                    symbol=symbol,
                    timestamp=bar['timestamp'],
                    open=bar['open'],
                    high=bar['high'],
                    low=bar['low'],
                    close=bar['close'],
                    volume=bar['volume'],
                )
                
                self.current_bars[symbol] = {
                    'timestamp': bar_start,
                    'open': price,
                    'high': price,
                    'low': price,
                    'close': price,
                    'volume': volume,
                }
                
                return completed_bar
            else:
                bar['high'] = max(bar['high'], price)
                bar['low'] = min(bar['low'], price)
                bar['close'] = price
                bar['volume'] += volume
                
        return None
```

---

## 3. 数据模型

### 3.1 Topic设计

| Topic名称 | 分区数 | 保留时间 | 说明 |
|-----------|--------|----------|------|
| `market.ticks.sh` | 6 | 1天 | 上海市场Tick |
| `market.ticks.sz` | 6 | 1天 | 深圳市场Tick |
| `market.bars.1m` | 3 | 7天 | 1分钟K线 |
| `market.bars.5m` | 3 | 30天 | 5分钟K线 |
| `news.sentiment` | 3 | 7天 | 舆情数据 |
| `trade.signals` | 3 | 30天 | 交易信号 |
| `system.events` | 1 | 7天 | 系统事件 |

### 3.2 消息格式

```json
{
  "header": {
    "version": "1.0",
    "source": "ifind",
    "timestamp": "2026-04-07T09:30:00.123456",
    "sequence": 12345
  },
  "payload": {
    "symbol": "600000.SH",
    "data": {
      "price": 10.25,
      "volume": 1000,
      "bid_price": 10.24,
      "ask_price": 10.26
    }
  }
}
```

---

## 4. 部署方案

### 4.1 单节点部署（个人开发推荐）

```yaml
version: '3.8'
services:
  redpanda:
    image: docker.redpanda.com/redpandadata/redpanda:latest
    container_name: redpanda
    ports:
      - "9092:9092"
      - "9644:9644"
    volumes:
      - redpanda_data:/var/lib/redpanda/data
    command:
      - redpanda
      - start
      - --mode
      - dev-container
      - --smp
      - "2"
      - --memory
      - 2G
      - --overprovisioned
      - --node-id
      - "0"
      - --kafka-addr
      - PLAINTEXT://0.0.0.0:9092
      - --advertise-kafka-addr
      - PLAINTEXT://localhost:9092

volumes:
  redpanda_data:
```

### 4.2 配置优化

```yaml
redpanda:
  config:
    storage:
      data_directory: /var/lib/redpanda/data
      log_segment_size: 134217728
      
    kafka_api:
      - name: external
        address: 0.0.0.0
        port: 9092
        
    admin:
      - name: admin
        address: 0.0.0.0
        port: 9644
        
    log_segment_size: 134217728
    retention_bytes: 1073741824
    segment_size: 134217728
```

---

## 5. 性能指标

### 5.1 吞吐量目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| Tick写入吞吐 | 100k/s | 每秒10万Tick |
| 消息延迟 | <10ms | P99延迟 |
| 消费延迟 | <100ms | 端到端延迟 |
| 数据保留 | 1-30天 | 按Topic配置 |

### 5.2 资源需求

| 资源 | 最小配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核 |
| 内存 | 4GB | 8GB |
| 存储 | 50GB SSD | 200GB SSD |
| 网络 | 100Mbps | 1Gbps |

---

## 6. 监控与运维

### 6.1 关键监控指标

```python
from prometheus_client import Counter, Histogram, Gauge

MESSAGES_PRODUCED = Counter(
    'kafka_messages_produced_total',
    'Total messages produced',
    ['topic']
)

MESSAGES_CONSUMED = Counter(
    'kafka_messages_consumed_total',
    'Total messages consumed',
    ['topic', 'consumer_group']
)

CONSUMER_LAG = Gauge(
    'kafka_consumer_lag',
    'Consumer lag in messages',
    ['topic', 'consumer_group']
)

LATENCY = Histogram(
    'kafka_message_latency_seconds',
    'Message latency',
    ['topic']
)
```

### 6.2 健康检查

```python
import requests
from datetime import datetime

class RedpandaHealthCheck:
    def __init__(self, admin_url: str = "http://localhost:9644"):
        self.admin_url = admin_url
        
    def check_cluster_health(self) -> dict:
        try:
            response = requests.get(
                f"{self.admin_url}/v1/cluster/health"
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def check_topic_status(self, topic: str) -> dict:
        try:
            response = requests.get(
                f"{self.admin_url}/v1/topics/{topic}"
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def get_consumer_groups(self) -> list:
        try:
            response = requests.get(
                f"{self.admin_url}/v1/consumer_groups"
            )
            return response.json()
        except Exception as e:
            return []
```

---

## 7. 实施路径

### Phase 1: 基础部署（3天）

**目标**: 搭建基础消息队列服务

**任务清单**:
- [ ] 安装Redpanda单节点
- [ ] 创建基础Topic
- [ ] 实现Producer/Consumer基础类
- [ ] 验证消息收发

**验收标准**:
- Redpanda服务正常运行
- 能够发送和接收消息
- 延迟<50ms

### Phase 2: 数据接入（2天）

**目标**: 接入实时市场数据

**任务清单**:
- [ ] 实现iFind数据Producer
- [ ] 实现Tick聚合为K线
- [ ] 对接QuestDB存储
- [ ] 配置数据保留策略

**验收标准**:
- 实时Tick数据正常流入
- K线聚合正确
- 数据持久化到QuestDB

### Phase 3: 生产优化（2天）

**目标**: 优化性能和稳定性

**任务清单**:
- [ ] 配置监控告警
- [ ] 实现消费者组管理
- [ ] 添加错误处理和重试
- [ ] 性能压测和优化

**验收标准**:
- 吞吐量达到100k/s
- P99延迟<10ms
- 监控指标正常

---

## 8. 维护成本评估

| 维护项目 | 频率 | 时间 | 说明 |
|----------|------|------|------|
| 服务监控 | 每日 | 5分钟 | 检查服务状态 |
| 日志检查 | 每周 | 15分钟 | 检查错误日志 |
| 存储清理 | 每月 | 30分钟 | 清理过期数据 |
| 版本升级 | 每季度 | 1小时 | 安全更新 |

**总维护成本**: 约 **2小时/月**

---

## 9. 风险评估

| 风险 | 等级 | 影响 | 缓解措施 |
|------|------|------|----------|
| 消息丢失 | P1 | 数据不完整 | 启用acks=all |
| 消费延迟 | P2 | 数据时效性 | 监控告警 |
| 存储满 | P2 | 服务中断 | 配置保留策略 |
| 网络故障 | P2 | 连接中断 | 重连机制 |

---

## 10. 与现有模块集成

```
┌─────────────────────────────────────────────────────────────┐
│                    模块集成关系                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │ 数据源接口       │         │ 实时数据流平台   │           │
│  │ (IFIND/QMT)     │────────▶│ (Redpanda)      │           │
│  └─────────────────┘         └────────┬────────┘           │
│                                       │                     │
│                    ┌──────────────────┼──────────────────┐  │
│                    │                  │                  │  │
│                    ▼                  ▼                  ▼  │
│           ┌─────────────┐    ┌─────────────┐    ┌────────┐ │
│           │ 时序存储     │    │ 因子引擎     │    │ 风控   │ │
│           │ (QuestDB)   │    │ (Layer 2)   │    │ 监控   │ │
│           └─────────────┘    └─────────────┘    └────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

**版本**: 1.0 | **状态**: Blueprint

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
---

## 11. 文档治理

### 11.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Data Realtime Streaming Bp
- **模块ID**: DATA_REALTIME_STREAMING_BP_001
- **蓝图文档**: [BLUEPRINT.md](02_FACTOR_LIBRARY\04_DATA_SOURCE\REALTIME_DATA_STREAMING\BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: 实时数据流平台
- **状态**: Blueprint
```

### 11.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Data Realtime Streaming Bp** | 实时数据流平台 | **核心模块** |

### 11.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-07 | **状态**: Blueprint
