---
module_id: STRATEGYENGINECOREBLUEPRINT_001_8121
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: '2026-04-07'
owner: 交易策略团队
responsibility:
- 交易策略框架设计与实施指导与实施指导
layer: layer_03
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---
```
module_id: TACTICS_BLUEPRINT_CORE_001_8121
```
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-03
parent_document: ../INDEX.md
implementation_status: 设计阶段
```
```---
```


> **核心职责**: Strategy Engine Core蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Strategy Engine Core蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容

>



## 一、设计目标与约束

### 1.1 核心设计目标

|------|--------|----------|
| **统一策略接口** | P0 | 遵循API_Contract.md的IStrategyEngine接口 |
| **

### 1.2 技术约束与原则

2. **
3. **
| 已有模块 | 集成方式 | 接口定义 |
|----------|----------|----------|
| **alert_manager.py** | 告警通知服务 | 事件总线集成 |
?| STRATEGY_ENGINE_TACTICS_ENTRY.md 3.2?|


```

### 2.2 组件职责划分

|------|------|----------|------------|

```
```


```python
class StrategyScanner:
    索引: STRAT.ENG.CORE.001-M01
    """
    
    def __init__(self, config_dir: str = "config/strategies"):
        self.config_dir = Path(config_dir)
self.cache = {}  # ID ?(mtime, config_path)
        
    def scan(self, force_refresh: bool = False) -> Dict[str, str]:
        参数:
            force_refresh: 是否强制刷新缓存
            
        返回:
        """
        if not force_refresh and self._is_cache_valid():
            return self._get_cached_configs()
            
        configs = {}
        for yaml_file in self.config_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    strategy_id = config.get('strategy_id')
                    if strategy_id:
                        configs[strategy_id] = str(yaml_file)
            except Exception as e:
                logger.warning(f"Failed to parse {yaml_file}: {e}")
                
        self.cache = configs
        self._save_cache()
        return configs
        
    def watch_changes(self) -> None:
        """监控策略目录变化，支持热重载"""
        # 使用watchdog监控文件变化
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
```


```python
class StrategyLoader:
    索引: STRAT.ENG.CORE.001-M02
    职责: 动态加载策略模块，验证策略接口
    """
    
    def __init__(self, module_search_paths: List[str] = None):
        self.module_search_paths = module_search_paths or []
        
    def load_strategy_class(self, config: Dict) -> Type[BaseStrategy]:
        参数:
config:
            
        返回:
        步骤:
            1. 解析模块路径 (module_path)
        # 1. 解析模块信息
        module_path = config.get('module_path')
        class_name = config.get('class_name')
        
        if not module_path or not class_name:
            raise StrategyLoadError("Missing module_path or class_name in config")
            
?        try:
            if module_path not in self._loaded_modules:
                module = importlib.import_module(module_path)
                self._loaded_modules[module_path] = module
            else:
                module = self._loaded_modules[module_path]
                
            
?            self._validate_strategy_interface(strategy_class)
            
            return strategy_class
            
        except ImportError as e:
            raise StrategyLoadError(f"Failed to import module {module_path}: {e}")
        except AttributeError as e:
            raise StrategyLoadError(f"Class {class_name} not found in module {module_path}: {e}")
            
    def _validate_strategy_interface(self, strategy_class: Type) -> None:
?""
        required_methods = [
            'initialize',
            'handle_data', 
            'generate_signal',
            'get_parameters',
            'set_parameters'
        ]
        
        for method in required_methods:
            if not hasattr(strategy_class, method):
                raise StrategyInterfaceError(f"Strategy class missing required method: {method}")
                
            raise StrategyInterfaceError(f"Strategy class must inherit from BaseStrategy")
```

```python
class StrategyRegistry:
    索引: STRAT.ENG.CORE.001-M03
    
    def __init__(self):
self._strategies = {}  # ID ?StrategyMetadata
    def register(self, strategy_id: str, metadata: StrategyMetadata) -> None:
?
        参数:
            strategy_id: 策略ID
metadata:
        if strategy_id in self._strategies:
            raise StrategyAlreadyRegisteredError(f"Strategy {strategy_id} already registered")
            
        self._strategies[strategy_id] = metadata
        self._by_category[metadata.category].append(strategy_id)
        self._statuses[strategy_id] = StrategyStatus.REGISTERED
        
        logger.info(f"Registered strategy: {strategy_id} ({metadata.name})")
        
    def get_metadata(self, strategy_id: str) -> StrategyMetadata:
?""
        if strategy_id not in self._strategies:
            raise StrategyNotFoundError(f"Strategy {strategy_id} not found")
        return self._strategies[strategy_id]
        
    def get_by_category(self, category: str) -> List[StrategyMetadata]:
        strategy_ids = self._by_category.get(category, [])
        return [self._strategies[strategy_id] for strategy_id in strategy_ids]
        
    def update_status(self, strategy_id: str, status: StrategyStatus) -> None:
        if strategy_id not in self._strategies:
            raise StrategyNotFoundError(f"Strategy {strategy_id} not found")
        self._statuses[strategy_id] = status
        
    def list_all(self) -> List[StrategyMetadata]:
        return list(self._strategies.values())


@dataclass
class StrategyMetadata:
"""
?""
    strategy_id: str
    name: str
    description: str
    category: str  # trend, mean_reversion, youzi, etc.
    version: str
    author: str
    created_date: str
    last_modified: str
    config_path: str
    module_path: str
    class_name: str
    parameters: Dict[str, ParameterInfo]
    dependencies: List[str]
    tags: List[str]
    performance_metrics: Optional[Dict] = None
    

@dataclass  
class ParameterInfo:
    """参数信息"""
    name: str
    type: str  # int, float, str, bool, list
    default: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""
    options: Optional[List[Any]] = None  # 枚举选项
```

### 3.4 StrategyFactory（策略工厂）


```python
class StrategyFactory:
    """策略工厂
    
    索引: STRAT.ENG.CORE.001-M04
    输出: 策略实例对象
    """
    
    def __init__(self, registry: StrategyRegistry, loader: StrategyLoader):
        self.registry = registry
        self.loader = loader
        
    def create_strategy(self, strategy_id: str, 
                       parameter_overrides: Dict[str, Any] = None,
                       use_cache: bool = True) -> BaseStrategy:
        """创建策略实例
        
        参数:
            strategy_id: 策略ID
            
        返回:
            BaseStrategy: 策略实例
        """
            instance = self._instances[strategy_id]
            # 应用参数覆盖
            if parameter_overrides:
                instance.set_parameters(parameter_overrides)
            return instance
            
?        metadata = self.registry.get_metadata(strategy_id)
        
            'module_path': metadata.module_path,
            'class_name': metadata.class_name
        }
        strategy_class = self.loader.load_strategy_class(config)
        
        # 4. 构建策略参数
        parameters = self._build_parameters(metadata, parameter_overrides)
        
        # 5. 创建策略实例
        try:
            instance = strategy_class(parameters)
            
            # 6. 缓存实例
            if use_cache:
                self._instances[strategy_id] = instance
                
            
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create strategy {strategy_id}: {e}")
            self.registry.update_status(strategy_id, StrategyStatus.ERROR)
            raise
            
    def _build_parameters(self, metadata: StrategyMetadata, 
                         overrides: Dict[str, Any] = None) -> Dict[str, Any]:
"""
        parameters = {}
        
        for param_name, param_info in metadata.parameters.items():
#
                value = overrides[param_name]
            else:
                value = param_info.default
                
                validated_value = self._validate_parameter(value, param_info)
                parameters[param_name] = validated_value
            except ValueError as e:
                logger.warning(f"Parameter validation failed for {param_name}: {e}")
        return parameters
```

### 3.5 StrategyEngine（策略引擎）

```python
class StrategyEngine:
    """策略引擎
    
    索引: STRAT.ENG.CORE.001-M05
    输出: 交易信号 + 策略事件
    接口: 遵循API_Contract.md中的IStrategyEngine接口
    """
    
    def __init__(self, event_bus: EventBus, registry: StrategyRegistry):
        self.event_bus = event_bus
        self.registry = registry
        self.factory = StrategyFactory(registry, StrategyLoader())
        
    def generate_signals(self, strategy_id: str, 
                        symbols: List[str], 
                        date: str) -> List[Signal]:
        """生成交易信号 - 实现IStrategyEngine接口
        
        参数:
            strategy_id: 策略ID
            symbols: 股票代码列表
date: ?
        返回:
            List[Signal]: 交易信号列表
            
        流程:
            1. 获取策略实例
            2. 获取市场数据
            3. 执行策略逻辑
            4. 生成交易信号
            5. 发布策略事件
        """
        # 1. 获取策略实例
        strategy = self.factory.create_strategy(strategy_id)
        
        # 2. 获取市场数据
        market_data = self._fetch_market_data(symbols, date)
        
        # 3. 执行策略逻辑
        try:
            self.registry.update_status(strategy_id, StrategyStatus.RUNNING)
            
            # 异步执行策略
            future = self._executor.submit(
                self._execute_strategy_logic,
                strategy, market_data
            )
            
时
            signals = future.result(timeout=5.0)
            
            # 4. 发布策略执行事件
            self.event_bus.publish(
                StrategyExecutedEvent(
                    strategy_id=strategy_id,
                    execution_time=datetime.utcnow(),
                    symbols=symbols,
                    signals_count=len(signals),
                    success=True
                )
            )
            
            self.registry.update_status(strategy_id, StrategyStatus.IDLE)
            return signals
            
        except TimeoutError:
            logger.error(f"Strategy {strategy_id} execution timeout")
            self.registry.update_status(strategy_id, StrategyStatus.TIMEOUT)
            self.event_bus.publish(
                StrategyTimeoutEvent(strategy_id=strategy_id)
            )
            return []
        except Exception as e:
            logger.error(f"Strategy {strategy_id} execution failed: {e}")
            self.registry.update_status(strategy_id, StrategyStatus.ERROR)
            self.event_bus.publish(
                StrategyErrorEvent(strategy_id=strategy_id, error=str(e))
            )
            return []
            
    def start_strategy(self, strategy_id: str, 
                      schedule: Optional[str] = None) -> None:
        """启动策略（定时执行）"""
            strategy_id=strategy_id,
            status=StrategyStatus.SCHEDULED,
            last_run=None,
            next_run=self._calculate_next_run(schedule),
            schedule=schedule
        )
        
        self._running_strategies[strategy_id] = ctx
        self.event_bus.publish(StrategyStartedEvent(strategy_id=strategy_id))
        
    def stop_strategy(self, strategy_id: str) -> None:
        """停止策略"""
        if strategy_id in self._running_strategies:
            del self._running_strategies[strategy_id]
            self.registry.update_status(strategy_id, StrategyStatus.STOPPED)
            self.event_bus.publish(StrategyStoppedEvent(strategy_id=strategy_id))
```

### 3.6 Layer 11

含AI理解逻辑

含AI理解
- ?**

**

|------|------|------|--------|
| **configure** |
| **backtest** | 回测策略 | strategy_id, start_date, end_date | 回测结果 |
| **optimize** | 优化策略参数 | strategy_id, param_ranges | 优化结果 |

```python

?strategy_tool = StrategyTool()

#
    "action": "configure",
    "params": {
        "strategy_type": "momentum",
        "holding_period": 5,
        "stop_loss": 0.1,
        "take_profit": 0.2
    }
})

# 返回结果
# {
#     "success": True,
#     "message": "
",
#     "data": {
#         "strategy_id": "STRAT_20260402_001",
#         "status": "configured"
#     }
# }
```

```python
class EventBus:
    """事件总线
    
    索引: STRAT.ENG.CORE.001-M06
?    """
    
    def __init__(self):
        self._worker_thread = None
        self._running = False
        
    def subscribe(self, event_type: Type[Event], callback: Callable) -> None:
"""
事件"""
        self._subscribers[event_type].append(callback)
        
    def publish(self, event: Event) -> None:
        """发布事件"""
        self._queue.put(event)
        
    def start(self) -> None:
        """启动事件总线"""
        self._running = True
        self._worker_thread = Thread(target=self._process_events, daemon=True)
        self._worker_thread.start()
        
    def stop(self) -> None:
        """停止事件总线"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
            
    def _process_events(self) -> None:
        """处理事件队列"""
        while self._running:
            try:
                event = self._queue.get(timeout=1.0)
                event_type = type(event)
                
?                for callback in self._subscribers[event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"Event callback failed: {e}")
                        
                self._queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")


# 策略事件定义
@dataclass
class StrategyEvent(Event):
    """策略基础事件"""
    strategy_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    

@dataclass
class StrategyStartedEvent(StrategyEvent):
    """策略启动事件"""


@dataclass
class StrategyStoppedEvent(StrategyEvent):
    """策略停止事件"""


@dataclass
class StrategyExecutedEvent(StrategyEvent):
    """策略执行完成事件"""
    execution_time: datetime
    symbols: List[str]
    signals_count: int
    success: bool
    

@dataclass
class StrategyErrorEvent(StrategyEvent):
    """策略错误事件"""
    error: str
    

@dataclass
class StrategyTimeoutEvent(StrategyEvent):
时事件"""
```


### 4.1 策略发现流程

```
1.
?3.

### 4.2

```yaml
# config/strategies/trend/ma_cross.yaml
strategy_id: "T001_ma_cross"
name: "移动均线交叉策略"
category: "trend"
version: "1.0.0"
置"
created_date: "2026-03-01"
last_modified: "2026-03-30"

#
置
module_path: "src.strategies.trend.ma_cross"
class_name: "MovingAverageCrossStrategy"

#
置
parameters:
  fast_period:
    type: "int"
    default: 20
    min_value: 5
    max_value: 100
  slow_period:
    type: "int"  
    default: 50
    min_value: 10
    max_value: 200
description: "
  position_size:
    type: "float"
    default: 0.1
    min_value: 0.01
    max_value: 0.5
    description: "仓位大小比例"

#
置
dependencies:
  - "pandas>=1.5.0"
  - "numpy>=1.24.0"

# 标签系统
tags:
  - "趋势跟踪"
- "A?
```

```python
class HotDeploymentManager:
    """热部署管理器"""
    
    def __init__(self, scanner: StrategyScanner, registry: StrategyRegistry):
        self.scanner = scanner
        self.registry = registry
        self.file_watcher = None
        
    def enable_hot_reload(self) -> None:
        # 监控策略目录变化
        self.file_watcher = FileSystemWatcher(
            path="config/strategies/",
            callback=self._on_config_changed
        )
        self.file_watcher.start()
        
    def _on_config_changed(self, event: FileSystemEvent) -> None:
"""
        if event.event_type in ('created', 'modified'):
            
            for strategy_id, config_path in configs.items():
                try:
                    self._reload_strategy(strategy_id, config_path)
                except Exception as e:
                    logger.error(f"Hot reload failed for {strategy_id}: {e}")
                    
    def _reload_strategy(self, strategy_id: str, config_path: str) -> None:
        """重新加载策略"""
?        with open(config_path, 'r') as f:
            new_config = yaml.safe_load(f)
            
        
        strategy_class = loader.load_strategy_class(new_config)
        
        metadata = self._create_metadata(new_config, config_path)
        self.registry.update_metadata(strategy_id, metadata)
        
            # 重启策略
            self._restart_strategy(strategy_id)
```


### 5.1 与Backtrader集成

```python
class BacktraderStrategyAdapter:
?""
    
    def __init__(self, strategy_engine: StrategyEngine):
        self.strategy_engine = strategy_engine
        
    def create_backtrader_strategy(self, strategy_id: str) -> bt.Strategy:
?""
        
        class BacktraderStrategyWrapper(bt.Strategy):
"""Backtrader
?""
            
            params = (
                ('strategy_id', strategy_id),
            )
            
            def __init__(self):
                # 通过StrategyEngine获取策略实例
                self.original_strategy = strategy_engine.factory.create_strategy(strategy_id)
                self.signals = []
                
            def next(self):
                # 将Backtrader数据转换为DataFrame
                data_df = self._convert_backtrader_data()
                
                # 调用原始策略逻辑
                signals = self.original_strategy.generate_signal(data_df)
                
                # 转换为Backtrader订单
                for signal in signals:
                    self._execute_backtrader_order(signal)
                    
        return BacktraderStrategyWrapper
```

```python
class SystemIntegrator:
    
    def __init__(self):
        self.loader = StrategyLoader()
        self.registry = StrategyRegistry()
        self.factory = StrategyFactory(self.registry, self.loader)
        self.event_bus = EventBus()
        self.engine = StrategyEngine(self.event_bus, self.registry)
        
        # 集成现有模块
        self.factor_calculator = FactorCalculator()
        self.risk_manager = RiskManager()
        self.alert_manager = AlertManager()
        
    def setup_event_handlers(self) -> None:
        
        self.event_bus.subscribe(StrategyExecutedEvent, self._on_strategy_executed)
        
        self.event_bus.subscribe(StrategyErrorEvent, self._on_strategy_error)
        
        
    def _on_strategy_executed(self, event: StrategyExecutedEvent) -> None:
        """策略执行完成事件处理"""
        # 触发因子重新计算
        self.factor_calculator.recalculate_factors(event.symbols)
        
    def _on_strategy_error(self, event: StrategyErrorEvent) -> None:
        """策略错误事件处理"""
        # 发送告警通知
        self.alert_manager.send_alert(
            f"策略 {event.strategy_id} 执行错误: {event.error}",
            level="ERROR"
        )
        
    def _on_signal_generated(self, event: SignalGeneratedEvent) -> None:
        """信号生成事件处理"""
        
        if risk_result.approved:
            # 发送到交易执行
            self._send_to_execution(event.signal)
        else:
```


##

### 6.1

```
?
级)
2. 策略实例参数
3.
级)
```

### 6.2 参数版本控制

```python
class ParameterVersionManager:
    
    def __init__(self, storage_backend: ParameterStorage):
        self.storage = storage_backend
        
    def save_parameter_snapshot(self, strategy_id: str, 
                               parameters: Dict[str, Any],
                               version_note: str = "") -> str:
"""
        version_id = f"v{len(self._versions.get(strategy_id, [])) + 1}"
        
        snapshot = ParameterSnapshot(
            strategy_id=strategy_id,
            version_id=version_id,
            parameters=parameters,
            created_at=datetime.utcnow(),
            note=version_note
        )
        
        self.storage.save_snapshot(snapshot)
        
#
存版本列表
        if strategy_id not in self._versions:
            self._versions[strategy_id] = []
        self._versions[strategy_id].append(snapshot)
        
        return version_id
        
    def rollback_parameters(self, strategy_id: str, 
                           version_id: str) -> Dict[str, Any]:
        snapshot = self.storage.load_snapshot(strategy_id, version_id)
        
        if not snapshot:
            raise ParameterVersionError(f"Snapshot not found: {strategy_id}/{version_id}")
            
        # 应用回滚
        self._apply_parameters(strategy_id, snapshot.parameters)
        
        return snapshot.parameters
```

### 6.3

```python
CONFIG_VALIDATION_RULES = {
    'strategy_id': {
        'type': 'string',
        'pattern': r'^[A-Z][A-Z0-9]{2,5}_[a-z0-9_]+$',
        'required': True
    },
    'name': {
        'type': 'string',
        'min_length': 3,
        'max_length': 100,
        'required': True
    },
    'category': {
        'type': 'string',
        'enum': ['trend', 'mean_reversion', 'youzi', 'market_neutral', 'event_driven'],
        'required': True
    },
    'parameters': {
        'type': 'dict',
        'required': True,
        'schema': {
            '*': {
                'type': 'dict',
                'schema': {
                    'type': {'type': 'string', 'required': True},
                    'default': {'required': True},
                    'description': {'type': 'string', 'required': False}
                }
            }
        }
    }
}
```


### 7.1 性能指标收集

```python
class PerformanceMonitor:
    
    METRICS = [
        'strategy_load_time_ms',
        'strategy_execution_time_ms',
        'signal_generation_count',
        'error_rate',
        'cache_hit_rate',
        'memory_usage_mb'
    ]
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = time.time()
        
    def record_metric(self, metric_name: str, value: float) -> None:
        """记录性能指标"""
        self.metrics[metric_name].append({
            'timestamp': time.time(),
            'value': value
        })
        
    def get_strategy_performance(self, strategy_id: str) -> Dict[str, Any]:
        """获取策略性能报告"""
        return {
            'strategy_id': strategy_id,
            'avg_execution_time': self._calculate_avg(f'{strategy_id}_execution_time'),
            'total_executions': len(self.metrics.get(f'{strategy_id}_execution_time', [])),
            'success_rate': self._calculate_success_rate(strategy_id),
            'last_execution': self._get_last_execution_time(strategy_id)
        }
```

### 7.2 缓存优化策略

```python
CACHE_CONFIG = {
    'strategy_instances': {
        'max_size': 50,
        'ttl_seconds': 3600,  # 1小时
    'market_data': {
        'max_size': 1000,
        'ttl_seconds': 300,  # 5分钟
        'eviction_policy': 'LRU'
    },
    'parameter_snapshots': {
        'max_size': 100,
        'ttl_seconds': 86400,  # 24小时
'eviction_policy': 'FIFO'  #
    }
}
```

### 7.3 资源隔离机制

```python
class ResourceIsolator:
    
    def __init__(self):
        
    def run_strategy_in_isolation(self, strategy_id: str, 
                                 func: Callable, *args, **kwargs) -> Any:
        """在隔离环境中运行策略"""
            future = executor.submit(func, *args, **kwargs)
            
            try:
                result = future.result(timeout=10.0)
                return result
            except TimeoutError:
                # 终止进程
                future.cancel()
                raise StrategyTimeoutError(f"Strategy {strategy_id} timeout")
            except Exception as e:
                raise StrategyExecutionError(f"Strategy {strategy_id} failed: {e}")
```


##

| 错误类型 | 严重等级 | 处理策略 | 恢复动作 |
|----------|----------|----------|----------|
| **
| **加载错误** | ERROR | 立即失败 | 标记策略不可用，通知用户 |
** | WARNING |
时控制 | 终止执行，返回空信号 |
| **
存溢出** | CRITICAL | 资源隔离 | 重启策略进程 |
| **数据错误** | WARNING | 数据验证 | 使用默认值或跳过 |

```python
class CircuitBreaker:
    
    def __init__(self, failure_threshold: int = 5,
                 recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == 'OPEN':
            if self._should_try_recovery():
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
                
        try:
            result = func(*args, **kwargs)
            
                self.state = 'CLOSED'
            self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                
            raise
            
    def _should_try_recovery(self) -> bool:
        if not self.last_failure_time:
            return True
            
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout
```


## 九、部署与运维指南

### 9.1 部署架构

```
生产环境部署:

```python
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {
            'strategy_engine': engine.get_status(),
            'event_bus': event_bus.get_status(),
            'registry': registry.get_status(),
            'cache': cache.get_stats()
        },
        'metrics': {
            'strategies_loaded': len(registry.list_all()),
            'strategies_running': len(engine.get_running_strategies()),
            'avg_execution_time_ms': monitor.get_avg_execution_time()
        }
    }
```

### 9.3 监控指标

```yaml
prometheus_metrics:
  - name: strategy_engine_strategies_total
    type: gauge
    help: "Total number of strategies"
    
  - name: strategy_engine_executions_total
    type: counter
    help: "Total strategy executions"
    
  - name: strategy_engine_execution_duration_seconds
    type: histogram
    help: "Strategy execution duration"
    
  - name: strategy_engine_errors_total
    type: counter
    help: "Total strategy errors"
    
  - name: strategy_engine_cache_hits_total
    type: counter
    help: "Cache hit count"
```


##
?|
|------|------|--------|
| [ARCHITECTURE.md](../../01_FRAMEWORK/ARCHITECTURE.md) | 系统架构设计 | ⭐⭐⭐⭐ |
| BACKTEST_BLUEPRINT.md | 回测系统设计 | ⭐⭐⭐⭐ |

### 10.2 代码实现位置

|------|----------|------|
| StrategyScanner | `src/modules/strategy_scanner.py` |
?|
| StrategyLoader | `src/modules/strategy_loader.py` |
?|
| StrategyRegistry | `src/modules/strategy_registry.py` |
?|
| StrategyFactory | `src/modules/strategy_factory.py` |
?|
| StrategyEngine | `src/modules/strategy_engine.py` |
?|
| EventBus | `src/core/event_bus.py` |
?|

### 10.3

|
|----------|----------|------|
|
置 |
|
置 |
|
置 |


## 十一、开发里程碑


- [ ] 实现StrategyEngine生命周期管理
- [ ] 实现EventBus事件系统
- [ ] 完成基础集成测试

- [ ] 实现性能监控系统
### 11.4 第四阶段：生产就
```---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Tactics Blueprint Core
- **模块ID**: TACTICS_BLUEPRINT_CORE_001
- **蓝图文档**: STRATEGY_ENGINE_CORE_BLUEPRINT.md
- **技术规格书**: 待创建
- **职责**: ?compliance_level: 
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Tactics Blueprint Core** | ?compliance_level:  | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-01 | 初始版本创建 | 首席蓝图架构师 |

```---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-01 | **状态**: Active
```
