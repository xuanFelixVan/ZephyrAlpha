---
module_id: STRATEGYENGINECOREBLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 交易策略团队
responsibility:
  - 交易策略、战术执行
layer: Layer 3 (策略层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---
---


﻿---
module_id: TACTICS_BLUEPRINT_CORE_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-03
owner: é¦å¸­ææ¡£æ¶æå¸?standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: ç­ç¥å¼ææ ¸å¿æ¨¡åææ¯è®¾è®?compliance_level: ä¸ä¸æ å
parent_document: ../INDEX.md
implementation_status: è®¾è®¡é¶æ®µ
---


# ç­ç¥å¼ææ ¸å¿æ¨¡åææ¯èå?
> **核心职责**: Strategy Engine Core蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Strategy Engine Core蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容

> æ¸é£éåäº¤æç³»ç» v5.3 - ç­ç¥å¼ææ ¸å¿æ¨¡åè¯¦ç»ææ¯è®¾è®?> **ç´¢å¼**: `STRAT.ENG.CORE.001`
> **å¼åå¨æ?*: 400å°æ¶ï¼è¶åä»£ç å¼åï¼
> **æ ¸å¿å®ä½**: ç­ç¥å¼ææ ¸å¿ç»ä»¶è¯¦ç»è®¾è®¡ï¼æ¯æ?20+ç­ç¥å¨æå è½½ãäºä»¶é©±å¨æ§è¡ãç­é¨ç½²çä¸ä¸æ¶æ?> **è¡¥åææ¡£**: æ¬èå¾æ¯[STRATEGY_ENGINE_BLUEPRINT.md](./STRATEGY_ENGINE_BLUEPRINT.md)çææ¯è¡¥åï¼ä¸æ³¨äºæ ¸å¿æ¨¡åå®ç°ç»è?

## ä¸ãè®¾è®¡ç®æ ä¸çº¦æ

### 1.1 æ ¸å¿è®¾è®¡ç®æ 

| ç®æ  | ä¼åçº?| ææ¯å®ç?|
|------|--------|----------|
| **120+ç­ç¥å¨æå è½?* | P0 | æä»¶å¼æ¶æ?+ éç½®é©±å¨åç° |
| **ç»ä¸ç­ç¥æ¥å£** | P0 | éµå¾ªAPI_Contract.mdçIStrategyEngineæ¥å£ |
| **ç­é¨ç½²æ¯æ?* | P0 | ç­ç¥éç¦» + å¨æç±»å è½½ |
| **äºä»¶é©±å¨æ§è¡** | P1 | å¼æ­¥äºä»¶æ»çº¿ + ç­ç¥äºä»¶çå¬å?|
| **éç½®é©±å¨ç®¡ç** | P1 | YAMLéç½®æä»¶ + åæ°çæ¬æ§å¶ |
| **ç¶æå¯è§æµ** | P1 | ç­ç¥ç¶æçæ?+ æ§è½ææ æ¶é |
| **æ¨¡ååæ©å±?* | P2 | æä»¶ç³»ç» + ä¾èµæ³¨å¥å®¹å¨ |

### 1.2 ææ¯çº¦æä¸åå

1. **æå°åèªç ä»£ç åå**ï¼?0%ä½¿ç¨æçå¼æºï¼20%èªç è¶åä»£ç 
2. **æ¥å£åè¡åå**ï¼æææ¨¡åå¿é¡»åå®ä¹æ¥å£ï¼åå®ç°
3. **éç½®é©±å¨åå**ï¼ç­ç¥åç°ãå è½½ãåæ°å¨é¨éè¿éç½®æä»¶ç®¡ç
4. **äºä»¶é©±å¨åå**ï¼æ¨¡åé´éè¿äºä»¶éä¿¡ï¼éä½è¦ååº?5. **ç¶æå¯è§æµåå**ï¼ææç­ç¥è¿è¡ç¶æå®æ¶çæ§ï¼å¯è¿½æº?
### 1.3 ä¸ç°æç³»ç»éæ?
| å·²ææ¨¡å | éææ¹å¼ | æ¥å£å®ä¹ |
|----------|----------|----------|
| **factor_calculator.py** | å å­è®¡ç®æå¡ | API_Contract.md 2.2è?|
| **risk_manager.py** | é£æ§æ£æ¥æå?| API_Contract.md 2.3è?|
| **alert_manager.py** | åè­¦éç¥æå¡ | äºä»¶æ»çº¿éæ |
| **Backtraderå¼æ** | åæµééå?| STRATEGY_ENGINE_BLUEPRINT.md 3.2è?|


## äºãæ ¸å¿æ¶æè®¾è®?
### 2.1 æ´ä½æ¶æå?
```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?â?                  ç­ç¥å¼ææ ¸å¿æ¶æ                                â?âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?â?                                                                â?â? âââââââââââââââ?    åç°       âââââââââââââââ?                â?â? â? ç­ç¥ç®å½   â?âââââââââââââââ?âç­ç¥æ«æå¨   â?                â?â? â?(config/    â?               â?Strategy    â?                â?â? â? strategies/)â?               â?Scanner)    â?                â?â? âââââââââââââââ?               ââââââââ¬âââââââ?                â?â?                                        â?è§£æ                   â?â?                                        â?                       â?â? âââââââââââââââ?    æ³¨å       âââââââââââââââ?                â?â? âç­ç¥æ³¨åè¡¨   â?ââââââââââââââ âç­ç¥å è½½å¨   â?                â?â? â?Strategy    â?               â?Strategy    â?                â?â? â?Registry)   â?               â?Loader)     â?                â?â? ââââââââ¬âââââââ?               âââââââââââââââ?                â?â?        â?è·ååæ°æ?                                            â?â?        â?                                                       â?â? âââââââââââââââ?    åå»ºå®ä¾    âââââââââââââââ?                â?â? âç­ç¥å·¥å?    â?âââââââââââââââ?âç­ç¥å¼æ?    â?                â?â? â?Strategy    â?               â?Strategy     â?                â?â? â?Factory)    â?               â?Engine)      â?                â?â? ââââââââ¬âââââââ?               ââââââââ¬âââââââ?                â?â?        â?                              â?æ§è¡                   â?â?        â?                              â?                       â?â? ââââââââ¼âââââââ?               âââââââââââââââ?                â?â? âåæ°ç®¡çå¨   â?               âäºä»¶æ»çº¿     â?                â?â? â?Parameter   â?               â?Event Bus)  â?                â?â? â?Manager)    â?               ââââââââ¬âââââââ?                â?â? âââââââââââââââ?                      â?åå¸äºä»¶                â?â?                                        â?                       â?â?                                 âââââââââââââââ?                â?â?                                 âä¸æ¸¸æ¨¡å?    â?                â?â?                                 â?é£æ§/æ§è¡/  â?                â?â?                                 â?çæ§)       â?                â?â?                                 âââââââââââââââ?                â?âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?```

### 2.2 ç»ä»¶èè´£åå

| ç»ä»¶ | èè´£ | æ ¸å¿åè½ | å®ç°å¤æåº?|
|------|------|----------|------------|
| **StrategyScanner** | ç­ç¥åç° | æ«æç­ç¥ç®å½ï¼è§£æéç½®æä»?| ä½?|
| **StrategyLoader** | ç­ç¥å è½½ | å¨æå¯¼å¥ç­ç¥æ¨¡åï¼éªè¯æ¥å£ | ä¸?|
| **StrategyRegistry** | ç­ç¥æ³¨å | ç®¡çç­ç¥åæ°æ®ï¼æä¾æ¥è¯¢æ¥å£ | ä¸?|
| **StrategyFactory** | ç­ç¥åå»º | å®ä¾åç­ç¥å¯¹è±¡ï¼æ³¨å¥ä¾èµ | ä¸?|
| **StrategyEngine** | ç­ç¥æ§è¡ | è¿è¡ç­ç¥é»è¾ï¼ç®¡çç­ç¥çå½å¨æ?| é«?|
| **ParameterManager** | åæ°ç®¡ç | ç®¡çç­ç¥åæ°ï¼æ¯æçæ¬æ§å?| ä¸?|
| **EventBus** | äºä»¶åå | å¼æ­¥äºä»¶åå¸/è®¢éï¼æ¨¡åè§£è?| ä¸?|
| **StateMonitor** | ç¶æçæ?| æ¶éç­ç¥è¿è¡ææ ï¼å¥åº·æ£æ?| ä½?|

### 2.3 æ°æ®æµè®¾è®?
```
ç­ç¥å¼å?â?éç½®æä»¶ â?æ«æåç° â?å è½½éªè¯ â?æ³¨ååæ°æ?    â?åæ°éç½® â?å·¥ååå»º â?å¼ææ§è¡ â?äºä»¶åå¸ â?ä¸æ¸¸å¤ç
    â?ç¶æçæ?â?ææ æ¶é â?è¿è¡æ¥å¿ â?å¼å¸¸å¤ç â?ç»æåé¦
```


## ä¸ãæ ¸å¿ç»ä»¶è¯¦ç»è®¾è®?
### 3.1 StrategyScannerï¼ç­ç¥æ«æå¨ï¼?
**è®¾è®¡ç®æ **ï¼èªå¨åç°ç­ç¥éç½®æä»¶ï¼æ¯æå¢éæ«æåç¼å­æºå?
```python
class StrategyScanner:
    """ç­ç¥æ«æå?    
    ç´¢å¼: STRAT.ENG.CORE.001-M01
    èè´£: æ«æç­ç¥éç½®ç®å½ï¼åç°ç­ç¥éç½®æä»?    è¾å¥: ç­ç¥ç®å½è·¯å¾(config/strategies/)
    è¾åº: ç­ç¥éç½®æä»¶åè¡¨(ç­ç¥ID â?éç½®æä»¶è·¯å¾)
    """
    
    def __init__(self, config_dir: str = "config/strategies"):
        self.config_dir = Path(config_dir)
        self.cache = {}  # ç­ç¥ID â?(mtime, config_path)
        
    def scan(self, force_refresh: bool = False) -> Dict[str, str]:
        """æ«æç­ç¥ç®å½ï¼è¿åç­ç¥éç½®æä»¶æ å°?        
        åæ°:
            force_refresh: æ¯å¦å¼ºå¶å·æ°ç¼å­
            
        è¿å:
            Dict[str, str]: ç­ç¥ID â?éç½®æä»¶è·¯å¾
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
        """çæ§ç­ç¥ç®å½ååï¼æ¯æç­éè½½"""
        # ä½¿ç¨watchdogçæ§æä»¶åå
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
```

### 3.2 StrategyLoaderï¼ç­ç¥å è½½å¨ï¼?
**è®¾è®¡ç®æ **ï¼å¨æå è½½ç­ç¥æ¨¡åï¼éªè¯æ¥å£å¼å®¹æ§ï¼éç¦»ç­ç¥æ§è¡ç¯å¢

```python
class StrategyLoader:
    """ç­ç¥å è½½å?    
    ç´¢å¼: STRAT.ENG.CORE.001-M02
    èè´£: å¨æå è½½ç­ç¥æ¨¡åï¼éªè¯ç­ç¥æ¥å£
    è¾å¥: ç­ç¥éç½®æä»¶è·¯å¾
    è¾åº: ç­ç¥ç±»å¯¹è±?å·²éªè¯?
    """
    
    def __init__(self, module_search_paths: List[str] = None):
        self.module_search_paths = module_search_paths or []
        self._loaded_modules = {}  # æ¨¡åè·¯å¾ â?æ¨¡åå¯¹è±¡
        
    def load_strategy_class(self, config: Dict) -> Type[BaseStrategy]:
        """æ ¹æ®éç½®å è½½ç­ç¥ç±?        
        åæ°:
            config: ç­ç¥éç½®å­å¸
            
        è¿å:
            Type[BaseStrategy]: ç­ç¥ç±?            
        æ­¥éª¤:
            1. è§£ææ¨¡åè·¯å¾ (module_path)
            2. å¨æå¯¼å¥æ¨¡å?            3. è·åç­ç¥ç±?(class_name)
            4. éªè¯æ¥å£å¼å®¹æ?            5. è¿åç­ç¥ç±?        """
        # 1. è§£ææ¨¡åä¿¡æ¯
        module_path = config.get('module_path')
        class_name = config.get('class_name')
        
        if not module_path or not class_name:
            raise StrategyLoadError("Missing module_path or class_name in config")
            
        # 2. å¨æå¯¼å¥æ¨¡å?        try:
            if module_path not in self._loaded_modules:
                module = importlib.import_module(module_path)
                self._loaded_modules[module_path] = module
            else:
                module = self._loaded_modules[module_path]
                
            # 3. è·åç­ç¥ç±?            strategy_class = getattr(module, class_name)
            
            # 4. éªè¯æ¥å£å¼å®¹æ?            self._validate_strategy_interface(strategy_class)
            
            return strategy_class
            
        except ImportError as e:
            raise StrategyLoadError(f"Failed to import module {module_path}: {e}")
        except AttributeError as e:
            raise StrategyLoadError(f"Class {class_name} not found in module {module_path}: {e}")
            
    def _validate_strategy_interface(self, strategy_class: Type) -> None:
        """éªè¯ç­ç¥ç±»æ¥å£å¼å®¹æ?""
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
                
        # éªè¯æ¯å¦æ¯BaseStrategyçå­ç±?        if not issubclass(strategy_class, BaseStrategy):
            raise StrategyInterfaceError(f"Strategy class must inherit from BaseStrategy")
```

### 3.3 StrategyRegistryï¼ç­ç¥æ³¨åè¡¨ï¼?
**è®¾è®¡ç®æ **ï¼éä¸­ç®¡çç­ç¥åæ°æ®ï¼æä¾å¿«éæ¥è¯¢åç¶æç®¡ç?
```python
class StrategyRegistry:
    """ç­ç¥æ³¨åè¡?    
    ç´¢å¼: STRAT.ENG.CORE.001-M03
    èè´£: ç®¡çç­ç¥åæ°æ®ï¼æä¾æ¥è¯¢åç¶æç®¡ç?    è¾å¥: ç­ç¥éç½®ä¿¡æ¯
    è¾åº: ç­ç¥åæ°æ®å¯¹è±?    """
    
    def __init__(self):
        self._strategies = {}  # ç­ç¥ID â?StrategyMetadata
        self._by_category = defaultdict(list)  # ç­ç¥ç±»å« â?ç­ç¥IDåè¡¨
        self._statuses = {}  # ç­ç¥ID â?ç­ç¥ç¶æ?        
    def register(self, strategy_id: str, metadata: StrategyMetadata) -> None:
        """æ³¨åç­ç¥åæ°æ?        
        åæ°:
            strategy_id: ç­ç¥ID
            metadata: ç­ç¥åæ°æ®å¯¹è±?        """
        if strategy_id in self._strategies:
            raise StrategyAlreadyRegisteredError(f"Strategy {strategy_id} already registered")
            
        self._strategies[strategy_id] = metadata
        self._by_category[metadata.category].append(strategy_id)
        self._statuses[strategy_id] = StrategyStatus.REGISTERED
        
        logger.info(f"Registered strategy: {strategy_id} ({metadata.name})")
        
    def get_metadata(self, strategy_id: str) -> StrategyMetadata:
        """è·åç­ç¥åæ°æ?""
        if strategy_id not in self._strategies:
            raise StrategyNotFoundError(f"Strategy {strategy_id} not found")
        return self._strategies[strategy_id]
        
    def get_by_category(self, category: str) -> List[StrategyMetadata]:
        """æç±»å«è·åç­ç¥åè¡?""
        strategy_ids = self._by_category.get(category, [])
        return [self._strategies[strategy_id] for strategy_id in strategy_ids]
        
    def update_status(self, strategy_id: str, status: StrategyStatus) -> None:
        """æ´æ°ç­ç¥ç¶æ?""
        if strategy_id not in self._strategies:
            raise StrategyNotFoundError(f"Strategy {strategy_id} not found")
        self._statuses[strategy_id] = status
        
    def list_all(self) -> List[StrategyMetadata]:
        """ååºææç­ç?""
        return list(self._strategies.values())


@dataclass
class StrategyMetadata:
    """ç­ç¥åæ°æ?""
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
    """åæ°ä¿¡æ¯"""
    name: str
    type: str  # int, float, str, bool, list
    default: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""
    options: Optional[List[Any]] = None  # æä¸¾éé¡¹
```

### 3.4 StrategyFactoryï¼ç­ç¥å·¥åï¼

**è®¾è®¡ç®æ **ï¼æéåå»ºç­ç¥å®ä¾ï¼æ¯æä¾èµæ³¨å¥ååæ°æ³¨å¥

```python
class StrategyFactory:
    """ç­ç¥å·¥å
    
    ç´¢å¼: STRAT.ENG.CORE.001-M04
    èè´£: åå»ºç­ç¥å®ä¾ï¼æ³¨å¥ä¾èµååæ°
    è¾å¥: ç­ç¥ID + åæ°è¦ç
    è¾åº: ç­ç¥å®ä¾å¯¹è±¡
    """
    
    def __init__(self, registry: StrategyRegistry, loader: StrategyLoader):
        self.registry = registry
        self.loader = loader
        self._instances = {}  # ç­ç¥ID â?ç­ç¥å®ä¾ç¼å­
        
    def create_strategy(self, strategy_id: str, 
                       parameter_overrides: Dict[str, Any] = None,
                       use_cache: bool = True) -> BaseStrategy:
        """åå»ºç­ç¥å®ä¾
        
        åæ°:
            strategy_id: ç­ç¥ID
            parameter_overrides: åæ°è¦çå?            use_cache: æ¯å¦ä½¿ç¨å®ä¾ç¼å­
            
        è¿å:
            BaseStrategy: ç­ç¥å®ä¾
        """
        # 1. æ£æ¥ç¼å­?        if use_cache and strategy_id in self._instances:
            instance = self._instances[strategy_id]
            # åºç¨åæ°è¦ç
            if parameter_overrides:
                instance.set_parameters(parameter_overrides)
            return instance
            
        # 2. è·åç­ç¥åæ°æ?        metadata = self.registry.get_metadata(strategy_id)
        
        # 3. å è½½ç­ç¥ç±?        config = {
            'module_path': metadata.module_path,
            'class_name': metadata.class_name
        }
        strategy_class = self.loader.load_strategy_class(config)
        
        # 4. æå»ºç­ç¥åæ°
        parameters = self._build_parameters(metadata, parameter_overrides)
        
        # 5. åå»ºç­ç¥å®ä¾
        try:
            instance = strategy_class(parameters)
            
            # 6. ç¼å­å®ä¾
            if use_cache:
                self._instances[strategy_id] = instance
                
            # 7. æ´æ°æ³¨åè¡¨ç¶æ?            self.registry.update_status(strategy_id, StrategyStatus.INITIALIZED)
            
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create strategy {strategy_id}: {e}")
            self.registry.update_status(strategy_id, StrategyStatus.ERROR)
            raise
            
    def _build_parameters(self, metadata: StrategyMetadata, 
                         overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """æå»ºç­ç¥åæ°å­å¸"""
        parameters = {}
        
        for param_name, param_info in metadata.parameters.items():
            # ä¼åä½¿ç¨è¦çå?            if overrides and param_name in overrides:
                value = overrides[param_name]
            else:
                value = param_info.default
                
            # ç±»åè½¬æ¢åéªè¯?            try:
                validated_value = self._validate_parameter(value, param_info)
                parameters[param_name] = validated_value
            except ValueError as e:
                logger.warning(f"Parameter validation failed for {param_name}: {e}")
                parameters[param_name] = value  # ä½¿ç¨åå§å?                
        return parameters
```

### 3.5 StrategyEngineï¼ç­ç¥å¼æï¼

**è®¾è®¡ç®æ **ï¼ç­ç¥æ§è¡æ ¸å¿ï¼ç®¡çç­ç¥çå½å¨æï¼éæäºä»¶é©±å¨æ¶æ?
```python
class StrategyEngine:
    """ç­ç¥å¼æ
    
    ç´¢å¼: STRAT.ENG.CORE.001-M05
    èè´£: ç­ç¥æ§è¡æ ¸å¿ï¼ç®¡çç­ç¥çå½å¨æ?    è¾å¥: å¸åºæ°æ® + ç­ç¥å®ä¾
    è¾åº: äº¤æä¿¡å· + ç­ç¥äºä»¶
    æ¥å£: éµå¾ªAPI_Contract.mdä¸­çIStrategyEngineæ¥å£
    """
    
    def __init__(self, event_bus: EventBus, registry: StrategyRegistry):
        self.event_bus = event_bus
        self.registry = registry
        self.factory = StrategyFactory(registry, StrategyLoader())
        self._running_strategies = {}  # ç­ç¥ID â?è¿è¡ä¸ä¸æ?        self._executor = ThreadPoolExecutor(max_workers=10)
        
    def generate_signals(self, strategy_id: str, 
                        symbols: List[str], 
                        date: str) -> List[Signal]:
        """çæäº¤æä¿¡å· - å®ç°IStrategyEngineæ¥å£
        
        åæ°:
            strategy_id: ç­ç¥ID
            symbols: è¡ç¥¨ä»£ç åè¡¨
            date: äº¤ææ?            
        è¿å:
            List[Signal]: äº¤æä¿¡å·åè¡¨
            
        æµç¨:
            1. è·åç­ç¥å®ä¾
            2. è·åå¸åºæ°æ®
            3. æ§è¡ç­ç¥é»è¾
            4. çæäº¤æä¿¡å·
            5. åå¸ç­ç¥äºä»¶
        """
        # 1. è·åç­ç¥å®ä¾
        strategy = self.factory.create_strategy(strategy_id)
        
        # 2. è·åå¸åºæ°æ®
        market_data = self._fetch_market_data(symbols, date)
        
        # 3. æ§è¡ç­ç¥é»è¾
        try:
            self.registry.update_status(strategy_id, StrategyStatus.RUNNING)
            
            # å¼æ­¥æ§è¡ç­ç¥
            future = self._executor.submit(
                self._execute_strategy_logic,
                strategy, market_data
            )
            
            # è®¾ç½®è¶æ¶
            signals = future.result(timeout=5.0)
            
            # 4. åå¸ç­ç¥æ§è¡äºä»¶
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
        """å¯å¨ç­ç¥ï¼å®æ¶æ§è¡ï¼"""
        # åå»ºè¿è¡ä¸ä¸æ?        ctx = StrategyContext(
            strategy_id=strategy_id,
            status=StrategyStatus.SCHEDULED,
            last_run=None,
            next_run=self._calculate_next_run(schedule),
            schedule=schedule
        )
        
        self._running_strategies[strategy_id] = ctx
        self.event_bus.publish(StrategyStartedEvent(strategy_id=strategy_id))
        
    def stop_strategy(self, strategy_id: str) -> None:
        """åæ­¢ç­ç¥"""
        if strategy_id in self._running_strategies:
            del self._running_strategies[strategy_id]
            self.registry.update_status(strategy_id, StrategyStatus.STOPPED)
            self.event_bus.publish(StrategyStoppedEvent(strategy_id=strategy_id))
```

### 3.6 Layer 11å·¥å·æ¥å£éæ

**è®¾è®¡ç®æ **ï¼ç­ç¥å¼æä½ä¸ºçº¯æ§è¡å±ï¼éè¿Layer 11å·¥å·æ¥å£æ¥åè°ç¨ï¼ä¸åå«AIçè§£é»è¾

**æ¶æåå**ï¼?- â?**çº¯æ§è¡å±**ï¼ç­ç¥å¼æåªæä¾APIæ¥å£ï¼ä¸åå«AIçè§£
- â?**åä¸AIå±?*ï¼æææå¾è¯å«ååæ°æåç±Layer 11ç»ä¸å¤ç
- â?**å·¥å·åå°è£?*ï¼ç­ç¥å¼æå°è£ä¸ºå·¥å·ï¼éè¿LangChainè°ç¨

**å·¥å·æ¥å£è§è**ï¼?
è¯¦ç»æ¥å£å®ä¹åè§ï¼[Layer 11å·¥å·æ¥å£è§è](module_designs\layer_11\LAYER_11_TOOL_INTERFACE_SPECIFICATION.md)

**æ¯æçæä½?*ï¼?
| æä½ | è¯´æ | åæ° | è¿åå?|
|------|------|------|--------|
| **configure** | éç½®æ°ç­ç?| strategy_type, holding_period, stop_loss, take_profit | strategy_id |
| **start** | å¯å¨ç­ç¥ | strategy_id | å¯å¨ç¶æ?|
| **stop** | åæ­¢ç­ç¥ | strategy_id | åæ­¢ç¶æ?|
| **status** | æ¥è¯¢ç­ç¥ç¶æ?| strategy_id | ç­ç¥ç¶æè¯¦æ?|
| **list** | ååºææç­ç?| æ?| ç­ç¥åè¡¨ |
| **backtest** | åæµç­ç¥ | strategy_id, start_date, end_date | åæµç»æ |
| **optimize** | ä¼åç­ç¥åæ° | strategy_id, param_ranges | ä¼åç»æ |

**è°ç¨ç¤ºä¾**ï¼?
```python
# Layer 11è°ç¨ç­ç¥å¼æï¼çº¯æ§è¡ï¼æ AIï¼?from src.layer_11.tools.strategy_tool import StrategyTool

# åå§åç­ç¥å·¥å?strategy_tool = StrategyTool()

# éç½®ç­ç¥ï¼åæ°å·²ç±Layer 11 AIæåï¼?result = strategy_tool.execute({
    "action": "configure",
    "params": {
        "strategy_type": "momentum",
        "holding_period": 5,
        "stop_loss": 0.1,
        "take_profit": 0.2
    }
})

# è¿åç»æ
# {
#     "success": True,
#     "message": "ç­ç¥éç½®æå",
#     "data": {
#         "strategy_id": "STRAT_20260402_001",
#         "strategy_name": "å¨éç­ç¥_5æ¥æä»?,
#         "status": "configured"
#     }
# }
```

**éè¦è¯´æ**ï¼?- â?**å·²ç§»é?*ï¼èªç¶è¯­è¨ç­ç¥æ¥å£(NLSI)ãç­ç¥æè¿°è¯­è¨(DSL)ãAIç­ç¥è½¬æ¢å·¥ä½æµ?- â?**åå **ï¼è¿äºåè½å±äºAIçè§£å±ï¼åºç±Layer 11ç»ä¸å¤ç
- â?**ä¼å¿**ï¼é¿åéå¤AIè°ç¨ï¼æåæ§è½ï¼éä½ç»´æ¤ææ?
### 3.7 EventBusï¼äºä»¶æ»çº¿ï¼?
**è®¾è®¡ç®æ **ï¼å¼æ­¥äºä»¶åå¸?è®¢éç³»ç»ï¼å®ç°æ¨¡åè§£è?
```python
class EventBus:
    """äºä»¶æ»çº¿
    
    ç´¢å¼: STRAT.ENG.CORE.001-M06
    èè´£: å¼æ­¥äºä»¶åå¸/è®¢éï¼æ¨¡åè§£è?    è®¾è®¡æ¨¡å¼: åå¸-è®¢éæ¨¡å¼ + è§å¯èæ¨¡å¼?    """
    
    def __init__(self):
        self._subscribers = defaultdict(list)  # äºä»¶ç±»å â?è®¢éèåè¡?        self._queue = Queue()  # äºä»¶éå
        self._worker_thread = None
        self._running = False
        
    def subscribe(self, event_type: Type[Event], callback: Callable) -> None:
        """è®¢éäºä»¶"""
        self._subscribers[event_type].append(callback)
        
    def publish(self, event: Event) -> None:
        """åå¸äºä»¶"""
        self._queue.put(event)
        
    def start(self) -> None:
        """å¯å¨äºä»¶æ»çº¿"""
        self._running = True
        self._worker_thread = Thread(target=self._process_events, daemon=True)
        self._worker_thread.start()
        
    def stop(self) -> None:
        """åæ­¢äºä»¶æ»çº¿"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
            
    def _process_events(self) -> None:
        """å¤çäºä»¶éå"""
        while self._running:
            try:
                event = self._queue.get(timeout=1.0)
                event_type = type(event)
                
                # éç¥ææè®¢éè?                for callback in self._subscribers[event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"Event callback failed: {e}")
                        
                self._queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")


# ç­ç¥äºä»¶å®ä¹
@dataclass
class StrategyEvent(Event):
    """ç­ç¥åºç¡äºä»¶"""
    strategy_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    

@dataclass
class StrategyStartedEvent(StrategyEvent):
    """ç­ç¥å¯å¨äºä»¶"""


@dataclass
class StrategyStoppedEvent(StrategyEvent):
    """ç­ç¥åæ­¢äºä»¶"""


@dataclass
class StrategyExecutedEvent(StrategyEvent):
    """ç­ç¥æ§è¡å®æäºä»¶"""
    execution_time: datetime
    symbols: List[str]
    signals_count: int
    success: bool
    

@dataclass
class StrategyErrorEvent(StrategyEvent):
    """ç­ç¥éè¯¯äºä»¶"""
    error: str
    

@dataclass
class StrategyTimeoutEvent(StrategyEvent):
    """ç­ç¥è¶æ¶äºä»¶"""
```


## åãå¨æå è½½æºå?
### 4.1 ç­ç¥åç°æµç¨

```
1. éç½®æä»¶æ«æ
   â?2. YAMLè§£æéªè¯
   â?3. åæ°æ®æå?   â?4. æ¥å£å¼å®¹æ§æ£æ?   â?5. æ³¨åè¡¨æ³¨å?```

### 4.2 éç½®æä»¶æ ¼å¼è§è

```yaml
# config/strategies/trend/ma_cross.yaml
strategy_id: "T001_ma_cross"
name: "ç§»å¨åçº¿äº¤åç­ç¥"
description: "åºäºå¿«éåçº¿åæ¢éåçº¿äº¤åçäº¤æç­ç¥"
category: "trend"
version: "1.0.0"
author: "ç³»ç»åç½®"
created_date: "2026-03-01"
last_modified: "2026-03-30"

# æ¨¡åéç½®
module_path: "src.strategies.trend.ma_cross"
class_name: "MovingAverageCrossStrategy"

# åæ°éç½®
parameters:
  fast_period:
    type: "int"
    default: 20
    min_value: 5
    max_value: 100
    description: "å¿«éåçº¿å¨æ?
  slow_period:
    type: "int"  
    default: 50
    min_value: 10
    max_value: 200
    description: "æ¢éåçº¿å¨æ?
  position_size:
    type: "float"
    default: 0.1
    min_value: 0.01
    max_value: 0.5
    description: "ä»ä½å¤§å°æ¯ä¾"

# ä¾èµéç½®
dependencies:
  - "pandas>=1.5.0"
  - "numpy>=1.24.0"

# æ ç­¾ç³»ç»
tags:
  - "è¶å¿è·è¸ª"
  - "ææ¯ææ ?
  - "Aè¡ä¼å?
```

### 4.3 ç­é¨ç½²å®ç°æ¹æ¡?
```python
class HotDeploymentManager:
    """ç­é¨ç½²ç®¡çå¨"""
    
    def __init__(self, scanner: StrategyScanner, registry: StrategyRegistry):
        self.scanner = scanner
        self.registry = registry
        self.file_watcher = None
        
    def enable_hot_reload(self) -> None:
        """å¯ç¨ç­éè½?""
        # çæ§ç­ç¥ç®å½åå
        self.file_watcher = FileSystemWatcher(
            path="config/strategies/",
            callback=self._on_config_changed
        )
        self.file_watcher.start()
        
    def _on_config_changed(self, event: FileSystemEvent) -> None:
        """éç½®æä»¶åååè°"""
        if event.event_type in ('created', 'modified'):
            # éæ°æ«æå¹¶å è½½ç­ç?            configs = self.scanner.scan(force_refresh=True)
            
            for strategy_id, config_path in configs.items():
                try:
                    self._reload_strategy(strategy_id, config_path)
                except Exception as e:
                    logger.error(f"Hot reload failed for {strategy_id}: {e}")
                    
    def _reload_strategy(self, strategy_id: str, config_path: str) -> None:
        """éæ°å è½½ç­ç¥"""
        # 1. è§£ææ°éç½?        with open(config_path, 'r') as f:
            new_config = yaml.safe_load(f)
            
        # 2. è·åç°æç­ç¥ç¶æ?        old_status = self.registry.get_status(strategy_id)
        
        # 3. éæ°å è½½ç­ç¥ç±?        loader = StrategyLoader()
        strategy_class = loader.load_strategy_class(new_config)
        
        # 4. æ´æ°æ³¨åè¡¨åæ°æ®
        metadata = self._create_metadata(new_config, config_path)
        self.registry.update_metadata(strategy_id, metadata)
        
        # 5. æ¢å¤ç­ç¥ç¶æ?        if old_status == StrategyStatus.RUNNING:
            # éå¯ç­ç¥
            self._restart_strategy(strategy_id)
```


## äºãéææ¹æ¡è®¾è®?
### 5.1 ä¸Backtraderéæ

```python
class BacktraderStrategyAdapter:
    """Backtraderç­ç¥ééå?""
    
    def __init__(self, strategy_engine: StrategyEngine):
        self.strategy_engine = strategy_engine
        
    def create_backtrader_strategy(self, strategy_id: str) -> bt.Strategy:
        """åå»ºBacktraderç­ç¥åè£å?""
        
        class BacktraderStrategyWrapper(bt.Strategy):
            """Backtraderç­ç¥åè£å?""
            
            params = (
                ('strategy_id', strategy_id),
            )
            
            def __init__(self):
                # éè¿StrategyEngineè·åç­ç¥å®ä¾
                self.original_strategy = strategy_engine.factory.create_strategy(strategy_id)
                self.signals = []
                
            def next(self):
                # å°Backtraderæ°æ®è½¬æ¢ä¸ºDataFrame
                data_df = self._convert_backtrader_data()
                
                # è°ç¨åå§ç­ç¥é»è¾
                signals = self.original_strategy.generate_signal(data_df)
                
                # è½¬æ¢ä¸ºBacktraderè®¢å
                for signal in signals:
                    self._execute_backtrader_order(signal)
                    
        return BacktraderStrategyWrapper
```

### 5.2 ä¸ç°ææ¨¡åéæ?
```python
class SystemIntegrator:
    """ç³»ç»éæå?""
    
    def __init__(self):
        # åå§åæææ ¸å¿ç»ä»?        self.scanner = StrategyScanner()
        self.loader = StrategyLoader()
        self.registry = StrategyRegistry()
        self.factory = StrategyFactory(self.registry, self.loader)
        self.event_bus = EventBus()
        self.engine = StrategyEngine(self.event_bus, self.registry)
        
        # éæç°ææ¨¡å
        self.factor_calculator = FactorCalculator()
        self.risk_manager = RiskManager()
        self.alert_manager = AlertManager()
        
    def setup_event_handlers(self) -> None:
        """è®¾ç½®äºä»¶å¤çå?""
        
        # ç­ç¥äºä»¶ â?å å­è®¡ç®
        self.event_bus.subscribe(StrategyExecutedEvent, self._on_strategy_executed)
        
        # ç­ç¥éè¯¯ â?åè­¦éç¥
        self.event_bus.subscribe(StrategyErrorEvent, self._on_strategy_error)
        
        # ç­ç¥ä¿¡å· â?é£æ§æ£æ?        self.event_bus.subscribe(SignalGeneratedEvent, self._on_signal_generated)
        
    def _on_strategy_executed(self, event: StrategyExecutedEvent) -> None:
        """ç­ç¥æ§è¡å®æäºä»¶å¤ç"""
        # è§¦åå å­éæ°è®¡ç®
        self.factor_calculator.recalculate_factors(event.symbols)
        
    def _on_strategy_error(self, event: StrategyErrorEvent) -> None:
        """ç­ç¥éè¯¯äºä»¶å¤ç"""
        # åéåè­¦éç¥
        self.alert_manager.send_alert(
            f"ç­ç¥ {event.strategy_id} æ§è¡éè¯¯: {event.error}",
            level="ERROR"
        )
        
    def _on_signal_generated(self, event: SignalGeneratedEvent) -> None:
        """ä¿¡å·çæäºä»¶å¤ç"""
        # é£æ§æ£æ?        risk_result = self.risk_manager.check_signal(event.signal)
        
        if risk_result.approved:
            # åéå°äº¤ææ§è¡
            self._send_to_execution(event.signal)
        else:
            logger.warning(f"ä¿¡å·è¢«é£æ§æç»? {risk_result.reason}")
```


## å­ãéç½®ç®¡çä¸åæ°ç³»ç»

### 6.1 å¤å±éç½®ç³»ç»

```
éç½®å±çº§ï¼ä»é«å°ä½ä¼åçº§ï¼?
1. è¿è¡æ¶åæ°è¦ç?(æé«ä¼åçº§)
2. ç­ç¥å®ä¾åæ°
3. ç­ç¥éç½®æä»¶åæ°  
4. ç³»ç»é»è®¤åæ° (æä½ä¼åçº§)
```

### 6.2 åæ°çæ¬æ§å¶

```python
class ParameterVersionManager:
    """åæ°çæ¬ç®¡çå?""
    
    def __init__(self, storage_backend: ParameterStorage):
        self.storage = storage_backend
        self._versions = {}  # ç­ç¥ID â?åæ°çæ¬åè¡¨
        
    def save_parameter_snapshot(self, strategy_id: str, 
                               parameters: Dict[str, Any],
                               version_note: str = "") -> str:
        """ä¿å­åæ°å¿«ç§"""
        version_id = f"v{len(self._versions.get(strategy_id, [])) + 1}"
        
        snapshot = ParameterSnapshot(
            strategy_id=strategy_id,
            version_id=version_id,
            parameters=parameters,
            created_at=datetime.utcnow(),
            note=version_note
        )
        
        self.storage.save_snapshot(snapshot)
        
        # æ´æ°åå­çæ¬åè¡¨
        if strategy_id not in self._versions:
            self._versions[strategy_id] = []
        self._versions[strategy_id].append(snapshot)
        
        return version_id
        
    def rollback_parameters(self, strategy_id: str, 
                           version_id: str) -> Dict[str, Any]:
        """åæ»å°æå®çæ¬åæ?""
        snapshot = self.storage.load_snapshot(strategy_id, version_id)
        
        if not snapshot:
            raise ParameterVersionError(f"Snapshot not found: {strategy_id}/{version_id}")
            
        # åºç¨åæ»
        self._apply_parameters(strategy_id, snapshot.parameters)
        
        return snapshot.parameters
```

### 6.3 éç½®éªè¯è§å

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


## ä¸ãæ§è½ä¼åä¸çæ?
### 7.1 æ§è½ææ æ¶é

```python
class PerformanceMonitor:
    """æ§è½çæ§å?""
    
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
        """è®°å½æ§è½ææ """
        self.metrics[metric_name].append({
            'timestamp': time.time(),
            'value': value
        })
        
    def get_strategy_performance(self, strategy_id: str) -> Dict[str, Any]:
        """è·åç­ç¥æ§è½æ¥å"""
        return {
            'strategy_id': strategy_id,
            'avg_execution_time': self._calculate_avg(f'{strategy_id}_execution_time'),
            'total_executions': len(self.metrics.get(f'{strategy_id}_execution_time', [])),
            'success_rate': self._calculate_success_rate(strategy_id),
            'last_execution': self._get_last_execution_time(strategy_id)
        }
```

### 7.2 ç¼å­ä¼åç­ç¥

```python
CACHE_CONFIG = {
    'strategy_instances': {
        'max_size': 50,
        'ttl_seconds': 3600,  # 1å°æ¶
        'eviction_policy': 'LRU'  # æè¿æå°ä½¿ç?    },
    'market_data': {
        'max_size': 1000,
        'ttl_seconds': 300,  # 5åé
        'eviction_policy': 'LRU'
    },
    'parameter_snapshots': {
        'max_size': 100,
        'ttl_seconds': 86400,  # 24å°æ¶
        'eviction_policy': 'FIFO'  # åè¿ååº
    }
}
```

### 7.3 èµæºéç¦»æºå¶

```python
class ResourceIsolator:
    """èµæºéç¦»å?""
    
    def __init__(self):
        self.strategy_processes = {}  # ç­ç¥ID â?è¿ç¨å¥æ
        
    def run_strategy_in_isolation(self, strategy_id: str, 
                                 func: Callable, *args, **kwargs) -> Any:
        """å¨éç¦»ç¯å¢ä¸­è¿è¡ç­ç¥"""
        # ä½¿ç¨è¿ç¨æ± éç¦»ç­ç¥æ§è¡?        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            
            try:
                result = future.result(timeout=10.0)
                return result
            except TimeoutError:
                # ç»æ­¢è¿ç¨
                future.cancel()
                raise StrategyTimeoutError(f"Strategy {strategy_id} timeout")
            except Exception as e:
                raise StrategyExecutionError(f"Strategy {strategy_id} failed: {e}")
```


## å«ãéè¯¯å¤çä¸å®¹éæºå¶

### 8.1 éè¯¯åç±»ä¸å¤çç­ç?
| éè¯¯ç±»å | ä¸¥éç­çº§ | å¤çç­ç¥ | æ¢å¤å¨ä½ |
|----------|----------|----------|----------|
| **éç½®éè¯¯** | ERROR | ç«å³å¤±è´¥ | è·³è¿è¯¥ç­ç¥ï¼è®°å½æ¥å¿ |
| **å è½½éè¯¯** | ERROR | ç«å³å¤±è´¥ | æ è®°ç­ç¥ä¸å¯ç¨ï¼éç¥ç¨æ· |
| **æ§è¡è¶æ¶** | WARNING | è¶æ¶æ§å¶ | ç»æ­¢æ§è¡ï¼è¿åç©ºä¿¡å· |
| **åå­æº¢åº** | CRITICAL | èµæºéç¦» | éå¯ç­ç¥è¿ç¨ |
| **æ°æ®éè¯¯** | WARNING | æ°æ®éªè¯ | ä½¿ç¨é»è®¤å¼æè·³è¿ |

### 8.2 æ­è·¯å¨æ¨¡å¼å®ç?
```python
class CircuitBreaker:
    """æ­è·¯å¨æ¨¡å¼?""
    
    def __init__(self, failure_threshold: int = 5,
                 recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """éè¿æ­è·¯å¨æ§è¡å½æ?""
        if self.state == 'OPEN':
            if self._should_try_recovery():
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
                
        try:
            result = func(*args, **kwargs)
            
            # æåæ§è¡ï¼éç½®ç¶æ?            if self.state == 'HALF_OPEN':
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
        """æ£æ¥æ¯å¦åºè¯¥å°è¯æ¢å¤?""
        if not self.last_failure_time:
            return True
            
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout
```


## ä¹ãé¨ç½²ä¸è¿ç»´æå

### 9.1 é¨ç½²æ¶æ

```
çäº§ç¯å¢é¨ç½²:
âââââââââââââââââââ?   âââââââââââââââââââ?â? ç­ç¥éç½®ä¸­å¿    â?   â? ç­ç¥æ§è¡éç¾¤    â?â? (Config DB)    âââââºâ  (Engine Nodes) â?âââââââââââââââââââ?   âââââââââââââââââââ?         â?                     â?         â?                     â?âââââââââââââââââââ?   âââââââââââââââââââ?â? çæ§åè­¦ç³»ç»    â?   â? æ¥å¿åæå¹³å°    â?â? (Prometheus)   â?   â? (ELK Stack)    â?âââââââââââââââââââ?   âââââââââââââââââââ?```

### 9.2 å¥åº·æ£æ¥æ¥å?
```python
@app.route('/health')
def health_check():
    """å¥åº·æ£æ¥æ¥å?""
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

### 9.3 çæ§ææ 

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


## åãç¸å³ææ¡£ç´¢å¼?
### 10.1 æ ¸å¿åèææ¡?
| ææ¡£ | è¯´æ | ç¸å³æ?|
|------|------|--------|
| [STRATEGY_ENGINE_BLUEPRINT.md](./STRATEGY_ENGINE_BLUEPRINT.md) | ä¸ªäººå¼åèå?| â­â­â­â­â­?|
| [API_Contract.md](../API_Contract.md) | ç³»ç»æ¥å£å¥çº¦ | â­â­â­â­â­?|
| [ARCHITECTURE.md](../../01_FRAMEWORK/ARCHITECTURE.md) | ç³»ç»æ¶æè®¾è®¡ | â­â­â­â­ |
| [BACKTEST_BLUEPRINT.md](./BACKTEST_BLUEPRINT.md) | åæµç³»ç»è®¾è®¡ | â­â­â­â­ |
| [STRATEGY_TEMPLATES.md](./STRATEGY_TEMPLATES.md) | ç­ç¥æ¨¡æ¿åº?| â­â­â­?|

### 10.2 ä»£ç å®ç°ä½ç½®

| ç»ä»¶ | æä»¶è·¯å¾ | ç¶æ?|
|------|----------|------|
| StrategyScanner | `src/modules/strategy_scanner.py` | å¾å®ç?|
| StrategyLoader | `src/modules/strategy_loader.py` | å¾å®ç?|
| StrategyRegistry | `src/modules/strategy_registry.py` | å¾å®ç?|
| StrategyFactory | `src/modules/strategy_factory.py` | å¾å®ç?|
| StrategyEngine | `src/modules/strategy_engine.py` | å¾å®ç?|
| EventBus | `src/core/event_bus.py` | å¾å®ç?|

### 10.3 éç½®ç¤ºä¾ä½ç½®

| éç½®ç±»å | æä»¶è·¯å¾ | ç¨é?|
|----------|----------|------|
| ç­ç¥éç½® | `config/strategies/trend/ma_cross.yaml` | ç§»å¨åçº¿äº¤åç­ç¥ |
| ç³»ç»éç½® | `config/system.yaml` | ç­ç¥å¼æå¨å±éç½® |
| ç¼å­éç½® | `config/cache.yaml` | ç¼å­ç­ç¥éç½® |
| çæ§éç½® | `config/monitoring.yaml` | æ§è½çæ§éç½® |


## åä¸ãå¼åéç¨ç¢

### 11.1 ç¬¬ä¸é¶æ®µï¼æ ¸å¿éª¨æ¶ï¼Week 1-2ï¼?- [ ] å®ç°StrategyScanneråºç¡æ«æåè½
- [ ] å®ç°StrategyLoaderå¨æå è½½æºå?- [ ] å®ç°StrategyRegistryåæ°æ®ç®¡ç?- [ ] å®æéç½®æä»¶è§£æéªè¯

### 11.2 ç¬¬äºé¶æ®µï¼å¼ææ ¸å¿ï¼Week 3-4ï¼?- [ ] å®ç°StrategyFactoryä¾èµæ³¨å¥
- [ ] å®ç°StrategyEngineçå½å¨æç®¡ç
- [ ] å®ç°EventBusäºä»¶ç³»ç»
- [ ] å®æåºç¡éææµè¯

### 11.3 ç¬¬ä¸é¶æ®µï¼é«çº§åè½ï¼Week 5-6ï¼?- [ ] å®ç°ç­é¨ç½²æºå?- [ ] å®ç°åæ°çæ¬æ§å¶
- [ ] å®ç°æ§è½çæ§ç³»ç»
- [ ] å®ææ­è·¯å¨å®¹éæºå?
### 11.4 ç¬¬åé¶æ®µï¼çäº§å°±
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Tactics Blueprint Core
- **模块ID**: TACTICS_BLUEPRINT_CORE_001
- **蓝图文档**: [STRATEGY_ENGINE_CORE_BLUEPRINT.md](03_TRADING_TACTICS\01_STRATEGY_FRAMEWORK\STRATEGY_ENGINE_CORE_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: ç­ç¥å¼ææ ¸å¿æ¨¡åææ¯è®¾è®?compliance_level: ä¸ä¸æ å
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Tactics Blueprint Core** | ç­ç¥å¼ææ ¸å¿æ¨¡åææ¯è®¾è®?compliance_level: ä¸ä¸æ å | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-01 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-01 | **状态**: Active
