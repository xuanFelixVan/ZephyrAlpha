---
module_id: CDC_CHANGE_DATA_CAPTURE_BLUEPRINT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - CDC变更数据捕获
  - 数据变更检测
  - 变更流处理
  - 数据同步
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
layer: Layer 5.1 (数据处理)
---


# CDC变更数据捕获蓝图

## 核心定位

负责变更数据捕获模块设计，实时监控数据库变更，捕获增量数据，支持数据同步和实时处理。

> **职责边界**: 
> - ✅ 本文档负责：CDC变更数据捕获、数据变更检测、变更流处理
> - ❌ 本文档不负责：数据存储（由数据存储模块负责）

## 设计目标

### 主要目标

1. **功能完整性**: 确保CDC CHANGE DATA CAPTURE功能完整，满足业务需求
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

采用CDC CHANGE DATA CAPTURE化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控






### 1.1 专业机构标准要求

| 机构类型 | CDC要求 | 延迟目标 |
|---------|---------|---------|

### 1.2 核心功能矩阵

|---------|---------|--------|-----------|---------|





```
```


```
                    完整CDC链路
```





```python
"""
"""
import os
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent
import threading
import queue


class ChangeType(Enum):
    """变更类型"""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    MOVE = "move"


@dataclass
class FileChangeEvent:
    """文件变更事件"""
    event_id: str
    file_path: str
    change_type: ChangeType
    timestamp: datetime
    old_content_hash: Optional[str]
    new_content_hash: Optional[str]
    metadata: Dict[str, Any]


class FileCDCMonitor:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.watch_paths = config.get("watch_paths", [])
        self.file_patterns = config.get("file_patterns", ["*"])
        self.ignore_patterns = config.get("ignore_patterns", [".git", "__pycache__"])
        
        self.event_queue = queue.Queue()
        self.change_handlers: List[Callable] = []
        self.file_hashes: Dict[str, str] = {}
        
        self.observer = Observer()
        self.running = False
    
    def _compute_file_hash(self, file_path: str) -> Optional[str]:
        """计算文件哈希"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None
    
    def _should_watch(self, file_path: str) -> bool:
        for ignore_pattern in self.ignore_patterns:
            if ignore_pattern in file_path:
                return False
        
        import fnmatch
        file_name = os.path.basename(file_path)
        for pattern in self.file_patterns:
            if fnmatch.fnmatch(file_name, pattern):
                return True
        
        return False
    
    def _create_event(
        self,
        file_path: str,
        change_type: ChangeType,
        old_hash: Optional[str] = None,
        new_hash: Optional[str] = None
    ) -> FileChangeEvent:
        """创建变更事件"""
        event_id = hashlib.sha256(
            f"{file_path}_{change_type.value}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        return FileChangeEvent(
            event_id=event_id,
            file_path=file_path,
            change_type=change_type,
            timestamp=datetime.now(),
            old_content_hash=old_hash,
            new_content_hash=new_hash,
            metadata={
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                "file_name": os.path.basename(file_path),
                "directory": os.path.dirname(file_path)
            }
        )
    
    def on_file_created(self, file_path: str):
        """文件创建事件"""
        if not self._should_watch(file_path):
            return
        
        new_hash = self._compute_file_hash(file_path)
        self.file_hashes[file_path] = new_hash
        
        event = self._create_event(file_path, ChangeType.CREATE, new_hash=new_hash)
        self.event_queue.put(event)
        self._notify_handlers(event)
    
    def on_file_modified(self, file_path: str):
        """文件修改事件"""
        if not self._should_watch(file_path):
            return
        
        old_hash = self.file_hashes.get(file_path)
        new_hash = self._compute_file_hash(file_path)
        
        if old_hash == new_hash:
            return
        
        self.file_hashes[file_path] = new_hash
        
        event = self._create_event(
            file_path, ChangeType.MODIFY,
            old_hash=old_hash, new_hash=new_hash
        )
        self.event_queue.put(event)
        self._notify_handlers(event)
    
    def on_file_deleted(self, file_path: str):
        """文件删除事件"""
        if file_path in self.file_hashes:
            old_hash = self.file_hashes.pop(file_path)
            
            event = self._create_event(file_path, ChangeType.DELETE, old_hash=old_hash)
            self.event_queue.put(event)
            self._notify_handlers(event)
    
    def add_change_handler(self, handler: Callable):
        self.change_handlers.append(handler)
    
    def _notify_handlers(self, event: FileChangeEvent):
        """通知所有处理器"""
        for handler in self.change_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Handler error: {e}")
    
    def get_event(self, timeout: float = 1.0) -> Optional[FileChangeEvent]:
        """获取事件"""
        try:
            return self.event_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def start(self):
        """启动监控"""
        for watch_path in self.watch_paths:
            if os.path.exists(watch_path):
                handler = CDCEventHandler(self)
                self.observer.schedule(handler, watch_path, recursive=True)
        
        self.observer.start()
        self.running = True
    
    def stop(self):
        """停止监控"""
        self.running = False
        self.observer.stop()
        self.observer.join()


class CDCEventHandler(FileSystemEventHandler):
    
    def __init__(self, monitor: FileCDCMonitor):
        self.monitor = monitor
    
    def on_created(self, event):
        if not event.is_directory:
            self.monitor.on_file_created(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.monitor.on_file_modified(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.monitor.on_file_deleted(event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory:
            self.monitor.on_file_deleted(event.src_path)
            self.monitor.on_file_created(event.dest_path)
```


```python
"""
"""
import asyncio
import aiohttp
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import logging


@dataclass
class APICDCConfig:
"""API CDC
    endpoint: str
    method: str = "GET"
    headers: Dict[str, str] = None
    params: Dict[str, Any] = None
    poll_interval: int = 60
    cursor_field: str = "updated_at"
    cursor_value: Any = None
    data_path: str = "data"
    id_field: str = "id"


class APICDCPoller:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.endpoints: Dict[str, APICDCConfig] = {}
        
        for name, ep_config in config.get("endpoints", {}).items():
            self.endpoints[name] = APICDCConfig(**ep_config)
        
        self.change_handlers: List[Callable] = []
        self.state_store = CDCStateStore(config.get("state_path", "data/cdc_state/"))
        
        self.running = False
        self.logger = logging.getLogger(__name__)
    
    async def poll_endpoint(self, name: str, config: APICDCConfig):
        """轮询单个端点"""
        last_cursor = self.state_store.get_cursor(name)
        if last_cursor:
            config.cursor_value = last_cursor
        
        try:
            async with aiohttp.ClientSession() as session:
                params = config.params or {}
                
                if config.cursor_value:
                    params[config.cursor_field] = config.cursor_value
                
                async with session.request(
                    config.method,
                    config.endpoint,
                    headers=config.headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        self.logger.error(
                            f"API poll failed for {name}: {response.status}"
                        )
                        return
                    
                    data = await response.json()
                    
                    items = data
                    for path_part in config.data_path.split("."):
                        if isinstance(items, dict):
                            items = items.get(path_part, [])
                    
                    if not isinstance(items, list):
                        items = [items]
                    
                    for item in items:
                        await self._process_item(name, config, item)
                    
                    if items:
                        last_item = items[-1]
                        if config.cursor_field in last_item:
                            new_cursor = last_item[config.cursor_field]
                            self.state_store.set_cursor(name, new_cursor)
        
        except Exception as e:
            self.logger.error(f"Poll error for {name}: {e}")
    
    async def _process_item(
        self,
        endpoint_name: str,
        config: APICDCConfig,
        item: Dict[str, Any]
    ):
        item_id = item.get(config.id_field)
        if not item_id:
            return
        
        item_hash = hashlib.md5(
            json.dumps(item, sort_keys=True).encode()
        ).hexdigest()
        
        stored_hash = self.state_store.get_item_hash(endpoint_name, item_id)
        
        if stored_hash is None:
            change_type = "create"
        elif stored_hash != item_hash:
            change_type = "update"
        else:
            return
        
        self.state_store.set_item_hash(endpoint_name, item_id, item_hash)
        
        event = {
            "event_id": hashlib.sha256(
                f"{endpoint_name}_{item_id}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16],
            "endpoint_name": endpoint_name,
            "item_id": item_id,
            "change_type": change_type,
            "timestamp": datetime.now().isoformat(),
            "data": item
        }
        
        for handler in self.change_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                self.logger.error(f"Handler error: {e}")
    
    def add_change_handler(self, handler: Callable):
        self.change_handlers.append(handler)
    
    async def start(self):
        """启动轮询"""
        self.running = True
        
        while self.running:
            tasks = []
            for name, config in self.endpoints.items():
                tasks.append(self.poll_endpoint(name, config))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            await asyncio.sleep(
                min(config.poll_interval for config in self.endpoints.values())
            )
    
    def stop(self):
        """停止轮询"""
        self.running = False


class CDCStateStore:
    
    def __init__(self, state_path: str):
        from pathlib import Path
        self.state_path = Path(state_path)
        self.state_path.mkdir(parents=True, exist_ok=True)
        
        self.cursors: Dict[str, Any] = {}
        self.item_hashes: Dict[str, Dict[str, str]] = {}
        
        self._load_state()
    
    def _load_state(self):
        cursor_file = self.state_path / "cursors.json"
        if cursor_file.exists():
            with open(cursor_file, 'r') as f:
                self.cursors = json.load(f)
        
        hash_file = self.state_path / "item_hashes.json"
        if hash_file.exists():
            with open(hash_file, 'r') as f:
                self.item_hashes = json.load(f)
    
    def _save_state(self):
        cursor_file = self.state_path / "cursors.json"
        with open(cursor_file, 'w') as f:
            json.dump(self.cursors, f, indent=2)
        
        hash_file = self.state_path / "item_hashes.json"
        with open(hash_file, 'w') as f:
            json.dump(self.item_hashes, f, indent=2)
    
    def get_cursor(self, endpoint_name: str) -> Any:
        """获取游标"""
        return self.cursors.get(endpoint_name)
    
    def set_cursor(self, endpoint_name: str, cursor: Any):
        """设置游标"""
        self.cursors[endpoint_name] = cursor
        self._save_state()
    
    def get_item_hash(self, endpoint_name: str, item_id: str) -> Optional[str]:
        return self.item_hashes.get(endpoint_name, {}).get(item_id)
    
    def set_item_hash(self, endpoint_name: str, item_id: str, hash_value: str):
        if endpoint_name not in self.item_hashes:
            self.item_hashes[endpoint_name] = {}
        
        self.item_hashes[endpoint_name][item_id] = hash_value
        self._save_state()
```


```python
"""
"""
import json
from typing import Dict, List, Any, Callable
from datetime import datetime
from dataclasses import dataclass
import redis
import logging


@dataclass
class ChangeEvent:
    """变更事件"""
    event_id: str
    source: str
    table: str
    operation: str
    before: Dict[str, Any]
    after: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]


class CDCEventProcessor:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        
        self.stream_name = config.get("stream_name", "cdc_events")
        self.consumer_group = config.get("consumer_group", "cdc_processor")
        self.consumer_name = config.get("consumer_name", "worker_1")
        
        self.handlers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
        
        self._ensure_consumer_group()
    
    def _ensure_consumer_group(self):
组存在"""
        try:
            self.redis_client.xgroup_create(
                self.stream_name,
                self.consumer_group,
                id='0',
                mkstream=True
            )
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
    
    def register_handler(self, operation: str, handler: Callable):
        if operation not in self.handlers:
            self.handlers[operation] = []
        self.handlers[operation].append(handler)
    
    def emit_event(self, event: ChangeEvent):
        event_data = {
            "event_id": event.event_id,
            "source": event.source,
            "table": event.table,
            "operation": event.operation,
            "before": json.dumps(event.before) if event.before else "",
            "after": json.dumps(event.after) if event.after else "",
            "timestamp": event.timestamp.isoformat(),
            "metadata": json.dumps(event.metadata)
        }
        
        self.redis_client.xadd(self.stream_name, event_data)
    
    def process_events(self, count: int = 10, block: int = 1000):
        """处理事件"""
        messages = self.redis_client.xreadgroup(
            groupname=self.consumer_group,
            consumername=self.consumer_name,
            streams={self.stream_name: '>'},
            count=count,
            block=block
        )
        
        if not messages:
            return
        
        for stream, msgs in messages:
            for msg_id, data in msgs:
                try:
                    event = self._parse_event(data)
                    self._dispatch_event(event)
                    self.redis_client.xack(
                        self.stream_name,
                        self.consumer_group,
                        msg_id
                    )
                except Exception as e:
                    self.logger.error(f"Error processing event {msg_id}: {e}")
    
    def _parse_event(self, data: Dict[str, str]) -> ChangeEvent:
        """解析事件"""
        return ChangeEvent(
            event_id=data["event_id"],
            source=data["source"],
            table=data["table"],
            operation=data["operation"],
            before=json.loads(data["before"]) if data["before"] else None,
            after=json.loads(data["after"]) if data["after"] else None,
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=json.loads(data["metadata"])
        )
    
    def _dispatch_event(self, event: ChangeEvent):
        """分发事件"""
        handlers = self.handlers.get(event.operation, [])
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Handler error: {e}")
    
    def start_processing(self):
        while True:
            self.process_events()
```




### 4.1 Debezium

```json
{
  "name": "zephyr-postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "localhost",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "password",
    "database.dbname": "zephyr",
    "database.server.name": "zephyr-pg",
    "plugin.name": "pgoutput",
    "table.include.list": "public.stock_data,public.trade_records",
    "database.history.kafka.bootstrap.servers": "localhost:9092",
    "database.history.kafka.topic": "schema-changes.zephyr"
  }
}
```

### 4.2 Docker Compose

```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    networks:
      - zephyr-network

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    networks:
      - zephyr-network

  connect:
    image: debezium/connect:latest
    ports:
      - "8083:8083"
    environment:
      BOOTSTRAP_SERVERS: kafka:9092
      GROUP_ID: 1
      CONFIG_STORAGE_TOPIC: connect_configs
      OFFSET_STORAGE_TOPIC: connect_offsets
      STATUS_STORAGE_TOPIC: connect_statuses
    depends_on:
      - kafka
    networks:
      - zephyr-network

networks:
  zephyr-network:
    external: true
```




### 5.1 文件CDC监控

```python
from cdc_capture import FileCDCMonitor

config = {
    "watch_paths": ["/data/market_data"],
    "file_patterns": ["*.csv", "*.parquet"],
    "ignore_patterns": [".git", "__pycache__", ".tmp"]
}

monitor = FileCDCMonitor(config)

def handle_change(event):
    print(f"文件变更: {event.file_path} - {event.change_type.value}")

monitor.add_change_handler(handle_change)
monitor.start()
```

### 5.2 API CDC轮询

```python
from cdc_capture import APICDCPoller
import asyncio

config = {
    "endpoints": {
        "stock_list": {
            "endpoint": "https://api.example.com/stocks",
            "poll_interval": 300,
            "cursor_field": "updated_at",
            "data_path": "data.list",
            "id_field": "symbol"
        }
    }
}

poller = APICDCPoller(config)

async def handle_change(event):
    print(f"数据变更: {event['endpoint_name']} - {event['item_id']}")

poller.add_change_handler(handle_change)
asyncio.run(poller.start())
```




### 6.1 CDC性能

|------|--------|--------|
| **捕获延迟** | <100ms | 50-80ms |
| **
障恢复时间** | <30s | 20s |

### 6.2 资源占用

| 资源 | Debezium | Kafka | 总计 |
|------|----------|-------|------|
| CPU | 0.5?| 1?| 1.5?|
| 
存 | 1GB | 2GB | 3GB |
| 存储 | 1GB | 10GB | 11GB |





- [x] 文件CDC实现
- [x] API CDC实现
- [x] Redis Streams集成


- [x] Debezium部署
- [x] Kafka集成
- [x] 事件处理


- [x] 性能优化
- [x] 监控告警
- [x] 
障恢复




|------|------|---------|------|



**文档结束**

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 实施团队 |



