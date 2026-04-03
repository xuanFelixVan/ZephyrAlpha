---
module_id: TIMEFRAME_SPEC_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SIMPLIFIED_TIMEFRAME_COORDINATION_BLUEPRINT.md
last_updated: 2026-04-03
created_date: 2026-04-03
layer: Layer 6 (组合优化层)
index: TIMEFRAME_SPEC_001
estimated_hours: 80h
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-03
owner: 组合优化层负责人
standard_type: 专业量化机构技术规格书
applicable_scope: 全系统
compliance_level: 专业标准
---

# 简化时间框架协同技术规格书 v1.0

> 清风量化系统 v5.3 - 时间框架协同详细技术设计
> **索引**: `TIMEFRAME_SPEC_001`
> **开发时间**: 80h
> **核心定位**: 三级时间框架协同、信号融合

---

## 1. 概述

时间框架协同模块负责宏观/中观/微观三级时间框架的信号融合。

## 2. 接口定义

```python
class TimeframeCoordinator:
    """时间框架协调器"""
    
    def fuse_signals(self,
                    macro_signal: pd.Series,
                    medium_signal: pd.Series,
                    micro_signal: pd.Series) -> pd.Series:
        """融合信号"""
        pass
    
    def resolve_conflicts(self,
                         signals: Dict[str, pd.Series]) -> pd.Series:
        """解决信号冲突"""
        pass
```

---

**技术规格书版本**: v1.0 | **创建日期**: 2026-04-03 | **状态**: Final

---

## 3. 信号冲突解决增强模块

### 3.1 EnhancedConflictResolver

`python
class EnhancedConflictResolver:
    """
    增强型冲突解决器
    
    职责: 多维度冲突检测与智能解决
    输入: 宏观信号、中观信号、市场状态
    输出: 冲突检测结果、解决后信号
    """
    
    def __init__(self, config: EnhancedConflictConfig):
        """
        初始化解决器
        
        Args:
            config: 增强型冲突配置
        """
        self.config = config
        self.conflict_classifier = ConflictClassifier(config.classifier_config)
        self.priority_engine = ConflictPriorityEngine(config.priority_config)
        self.resolution_strategy_library = ResolutionStrategyLibrary()
        self.resolution_log = []
    
    def detect_all_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal],
        market_state: MarketState
    ) -> List[EnhancedSignalConflict]:
        """
        检测所有类型的冲突
        
        Args:
            macro_signals: 宏观信号字典
            meso_signals: 中观信号字典
            market_state: 市场状态
            
        Returns:
            List[EnhancedSignalConflict]: 增强型冲突列表
            
        Performance:
            - 计算时间: < 30ms (100信号)
            - 冲突检测维度: 4维（方向/强度/置信度/时机）
        """
        all_conflicts = []
        
        # 检测方向冲突
        direction_conflicts = self._detect_direction_conflicts(
            macro_signals, meso_signals
        )
        all_conflicts.extend(direction_conflicts)
        
        # 检测强度冲突
        strength_conflicts = self._detect_strength_conflicts(
            macro_signals, meso_signals
        )
        all_conflicts.extend(strength_conflicts)
        
        # 检测置信度冲突
        confidence_conflicts = self._detect_confidence_conflicts(
            macro_signals, meso_signals
        )
        all_conflicts.extend(confidence_conflicts)
        
        # 检测时机冲突
        timing_conflicts = self._detect_timing_conflicts(
            macro_signals, meso_signals, market_state
        )
        all_conflicts.extend(timing_conflicts)
        
        # 分类和优先级排序
        classified_conflicts = self.conflict_classifier.classify(all_conflicts)
        prioritized_conflicts = self.priority_engine.prioritize(
            classified_conflicts, market_state
        )
        
        return prioritized_conflicts
    
    def resolve_with_strategy(
        self,
        conflicts: List[EnhancedSignalConflict],
        fused_signals: Dict[str, Signal],
        market_state: MarketState,
        historical_performance: Optional[Dict] = None
    ) -> ConflictResolutionResult:
        """
        使用策略库解决冲突
        
        Args:
            conflicts: 冲突列表
            fused_signals: 融合信号
            market_state: 市场状态
            historical_performance: 历史表现数据
            
        Returns:
            ConflictResolutionResult: 冲突解决结果
            
        Performance:
            - 解决时间: < 20ms (10冲突)
            - 策略选择: 自适应
        """
        resolved_signals = fused_signals.copy()
        resolution_details = []
        
        for conflict in conflicts:
            # 选择解决策略
            strategy = self.resolution_strategy_library.select_strategy(
                conflict, market_state, historical_performance
            )
            
            # 应用策略解决冲突
            resolved_signal = strategy.resolve(
                conflict, market_state, historical_performance
            )
            
            resolved_signals[conflict.signal_name] = resolved_signal
            
            # 记录解决详情
            resolution_details.append({
                'signal_name': conflict.signal_name,
                'conflict_type': conflict.conflict_type,
                'severity': conflict.severity,
                'strategy_used': strategy.name,
                'resolution_value': resolved_signal.value,
                'timestamp': datetime.now()
            })
            
            self.resolution_log.append(resolution_details[-1])
        
        return ConflictResolutionResult(
            resolved_signals=resolved_signals,
            resolution_details=resolution_details,
            total_conflicts=len(conflicts),
            resolution_efficiency=self._calculate_resolution_efficiency(
                conflicts, resolution_details
            ),
            timestamp=datetime.now()
        )
`

### 3.2 ConflictPriorityEngine

`python
class ConflictPriorityEngine:
    """
    冲突优先级引擎
    
    职责: 基于多维度因素确定冲突解决优先级
    算法: 多因素加权评分
    """
    
    def __init__(self, config: PriorityConfig):
        """
        初始化引擎
        
        Args:
            config: 优先级配置
        """
        self.config = config
    
    def prioritize(
        self,
        conflicts: List[EnhancedSignalConflict],
        market_state: MarketState
    ) -> List[EnhancedSignalConflict]:
        """
        确定冲突优先级
        
        Args:
            conflicts: 冲突列表
            market_state: 市场状态
            
        Returns:
            List[EnhancedSignalConflict]: 按优先级排序的冲突列表
            
        Algorithm:
            优先级分数 = 严重程度分数  市场状态调整  冲突类型权重
            
        Performance:
            - 计算时间: O(n log n), n为冲突数量
        """
        # 计算每个冲突的优先级分数
        for conflict in conflicts:
            priority_score = self._calculate_priority_score(
                conflict, market_state
            )
            conflict.priority_score = priority_score
        
        # 按优先级排序
        return sorted(
            conflicts, 
            key=lambda c: c.priority_score, 
            reverse=True
        )
    
    def _calculate_priority_score(
        self,
        conflict: EnhancedSignalConflict,
        market_state: MarketState
    ) -> float:
        """
        计算优先级分数
        
        Args:
            conflict: 冲突对象
            market_state: 市场状态
            
        Returns:
            float: 优先级分数 (0-1)
        """
        # 基础分数（基于严重程度）
        severity_scores = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
        base_score = severity_scores.get(conflict.severity, 0.5)
        
        # 市场状态调整
        market_adjustment = self._get_market_adjustment(market_state)
        
        # 冲突类型权重
        type_weights = {
            'direction': 1.0,
            'confidence': 0.8,
            'strength': 0.6,
            'timing': 0.4
        }
        type_weight = type_weights.get(conflict.conflict_type, 0.5)
        
        # 综合优先级分数
        priority_score = base_score * market_adjustment * type_weight
        
        return priority_score
`

### 3.3 ResolutionStrategyLibrary

`python
class ResolutionStrategyLibrary:
    """
    冲突解决策略库
    
    职责: 提供多种冲突解决策略
    策略数量: 8种（方向2 + 强度2 + 置信度2 + 时机2）
    """
    
    def __init__(self):
        """初始化策略库"""
        self.strategies = {
            'direction': {
                'market_state_priority': MarketStatePriorityStrategy(),
                'confidence_weighted': ConfidenceWeightedStrategy(),
                'historical_performance': HistoricalPerformanceStrategy()
            },
            'strength': {
                'dynamic_weight': DynamicWeightStrategy(),
                'average_fusion': AverageFusionStrategy()
            },
            'confidence': {
                'quality_weighted': QualityWeightedStrategy(),
                'risk_adjusted': RiskAdjustedStrategy()
            },
            'timing': {
                'phased_execution': PhasedExecutionStrategy(),
                'monitor_and_act': MonitorAndActStrategy()
            }
        }
    
    def select_strategy(
        self,
        conflict: EnhancedSignalConflict,
        market_state: MarketState,
        historical_performance: Optional[Dict] = None
    ) -> ResolutionStrategy:
        """
        选择最佳解决策略
        
        Args:
            conflict: 冲突对象
            market_state: 市场状态
            historical_performance: 历史表现
            
        Returns:
            ResolutionStrategy: 解决策略
            
        Algorithm:
            1. 根据冲突类型筛选可用策略
            2. 基于市场状态选择最优策略
            3. 参考历史表现调整选择
        """
        conflict_type = conflict.conflict_type
        available_strategies = self.strategies.get(conflict_type, {})
        
        # 基于市场状态选择策略
        if conflict_type == 'direction':
            if market_state.volatility_regime == 'high':
                return available_strategies['market_state_priority']
            elif historical_performance and historical_performance.get('accuracy', 0) > 0.7:
                return available_strategies['historical_performance']
            else:
                return available_strategies['confidence_weighted']
        
        elif conflict_type == 'strength':
            return available_strategies['dynamic_weight']
        
        elif conflict_type == 'confidence':
            return available_strategies['quality_weighted']
        
        elif conflict_type == 'timing':
            return available_strategies['phased_execution']
        
        # 默认策略
        return DefaultResolutionStrategy()


class MarketStatePriorityStrategy(ResolutionStrategy):
    """市场状态优先策略"""
    
    name = 'market_state_priority'
    
    def resolve(
        self,
        conflict: EnhancedSignalConflict,
        market_state: MarketState,
        historical_performance: Optional[Dict] = None
    ) -> Signal:
        """
        基于市场状态优先级解决方向冲突
        
        Algorithm:
            - 趋势市场: 优先宏观信号（权重0.7）
            - 震荡市场: 优先中观信号（权重0.6）
        """
        # 在趋势市场中优先宏观信号
        if market_state.trend_strength > 0.6:
            primary_signal = conflict.macro_signal
            secondary_signal = conflict.meso_signal
            primary_weight = 0.7
        # 在震荡市场中优先中观信号
        else:
            primary_signal = conflict.meso_signal
            secondary_signal = conflict.macro_signal
            primary_weight = 0.6
        
        resolved_value = (
            primary_weight * primary_signal.value +
            (1 - primary_weight) * secondary_signal.value
        )
        
        resolved_confidence = min(
            primary_signal.confidence,
            secondary_signal.confidence
        ) * 0.85
        
        return Signal(
            name=conflict.signal_name,
            value=resolved_value,
            confidence=resolved_confidence,
            source='market_state_priority_resolution'
        )
`

---

## 4. 数据模型

### 4.1 配置模型

`python
@dataclass
class EnhancedConflictConfig:
    """增强型冲突解决配置"""
    classifier_config: ConflictClassifierConfig
    priority_config: PriorityConfig
    
    # 冲突检测阈值
    strength_threshold: float = 0.3  # 强度差异阈值
    confidence_threshold: float = 0.3  # 置信度差异阈值
    timing_threshold: float = 0.4  # 时机差异阈值
    
    # 解决策略配置
    default_strategy: str = 'confidence_weighted'
    enable_adaptive_strategy: bool = True  # 自适应策略选择
    
    # 历史表现权重
    historical_weight: float = 0.3  # 历史表现在策略选择中的权重

@dataclass
class ConflictClassifierConfig:
    """冲突分类器配置"""
    enable_multi_level: bool = True  # 启用多层次分类
    severity_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'high': 0.7,
        'medium': 0.4,
        'low': 0.2
    })
`

### 4.2 数据模型

`python
@dataclass
class EnhancedSignalConflict:
    """增强型信号冲突"""
    signal_name: str
    conflict_type: str  # direction/strength/confidence/timing
    macro_signal: NormalizedSignal
    meso_signal: NormalizedSignal
    severity: str  # high/medium/low
    priority_score: float = 0.0
    
    # 冲突详细信息
    direction_info: Optional[Dict] = None
    strength_info: Optional[Dict] = None
    confidence_info: Optional[Dict] = None
    timing_info: Optional[Dict] = None

@dataclass
class ConflictResolutionResult:
    """冲突解决结果"""
    resolved_signals: Dict[str, Signal]
    resolution_details: List[Dict]
    total_conflicts: int
    resolution_efficiency: float  # 解决效率评分 (0-1)
    timestamp: datetime

@dataclass
class NormalizedSignal:
    """标准化信号"""
    name: str
    value: float  # 信号值 (-1 to 1)
    confidence: float  # 置信度 (0-1)
    strength: float  # 信号强度 (0-1)
    direction: str  # bullish/bearish/neutral
    timestamp: datetime
`

---

## 5. 性能要求

| 操作 | 性能指标 | 要求 |
|------|---------|------|
| **冲突检测** | 计算时间 | < 30ms (100信号) |
| **冲突分类** | 计算时间 | < 10ms |
| **优先级排序** | 计算时间 | < 5ms (50冲突) |
| **策略选择** | 响应时间 | < 5ms |
| **冲突解决** | 计算时间 | < 20ms (10冲突) |
| **内存占用** | 最大内存 | < 20MB |

---

## 6. 测试要求

### 6.1 单元测试

`python
def test_conflict_detection():
    """测试冲突检测"""
    resolver = EnhancedConflictResolver(EnhancedConflictConfig())
    
    macro_signals = {
        'signal_1': NormalizedSignal(name='signal_1', value=0.8, confidence=0.9, strength=0.7, direction='bullish'),
        'signal_2': NormalizedSignal(name='signal_2', value=-0.6, confidence=0.8, strength=0.6, direction='bearish')
    }
    
    meso_signals = {
        'signal_1': NormalizedSignal(name='signal_1', value=-0.5, confidence=0.7, strength=0.5, direction='bearish'),
        'signal_2': NormalizedSignal(name='signal_2', value=-0.7, confidence=0.85, strength=0.7, direction='bearish')
    }
    
    market_state = MarketState(volatility_regime='normal', trend_strength=0.5)
    
    conflicts = resolver.detect_all_conflicts(macro_signals, meso_signals, market_state)
    
    # 验证冲突检测
    assert len(conflicts) > 0
    assert any(c.conflict_type == 'direction' for c in conflicts)
    assert all(c.priority_score >= 0 for c in conflicts)

def test_conflict_priority():
    """测试冲突优先级"""
    engine = ConflictPriorityEngine(PriorityConfig())
    
    conflicts = [
        EnhancedSignalConflict(signal_name='s1', conflict_type='direction', severity='high'),
        EnhancedSignalConflict(signal_name='s2', conflict_type='strength', severity='medium'),
        EnhancedSignalConflict(signal_name='s3', conflict_type='timing', severity='low')
    ]
    
    market_state = MarketState(volatility_regime='high', trend_strength=0.8)
    
    prioritized = engine.prioritize(conflicts, market_state)
    
    # 验证优先级排序
    assert prioritized[0].signal_name == 's1'  # 高严重程度优先
    assert all(prioritized[i].priority_score >= prioritized[i+1].priority_score 
               for i in range(len(prioritized)-1))

def test_strategy_selection():
    """测试策略选择"""
    library = ResolutionStrategyLibrary()
    
    conflict = EnhancedSignalConflict(
        signal_name='test',
        conflict_type='direction',
        severity='high'
    )
    
    market_state = MarketState(volatility_regime='high', trend_strength=0.7)
    
    strategy = library.select_strategy(conflict, market_state)
    
    # 验证策略选择
    assert strategy.name == 'market_state_priority'
`

### 6.2 集成测试

`python
def test_end_to_end_conflict_resolution():
    """端到端冲突解决测试"""
    # 1. 初始化系统
    resolver = EnhancedConflictResolver(EnhancedConflictConfig())
    
    # 2. 创建测试信号
    macro_signals = create_macro_signals()
    meso_signals = create_meso_signals()
    market_state = create_market_state()
    
    # 3. 检测冲突
    conflicts = resolver.detect_all_conflicts(
        macro_signals, meso_signals, market_state
    )
    
    # 4. 解决冲突
    fused_signals = create_fused_signals(macro_signals, meso_signals)
    result = resolver.resolve_with_strategy(
        conflicts, fused_signals, market_state
    )
    
    # 5. 验证结果
    assert len(result.resolved_signals) > 0
    assert result.resolution_efficiency >= 0.8
    assert len(result.resolution_details) == len(conflicts)
`

---

## 7. 部署要求

### 7.1 环境要求

- Python 3.8+
- NumPy 1.20+
- Pandas 1.3+

### 7.2 依赖模块

- Layer 5: 信号生成（宏观/中观信号）
- Layer 3: 市场数据（市场状态）
- Layer 2: 历史数据（历史表现）

### 7.3 监控要求

- 冲突检测频率: 实时
- 解决策略日志: 保留90天
- 性能监控: 每小时统计

---

**技术规格书版本**: v1.0 | **创建日期**: 2026-04-03 | **状态**: Final | **增强模块**: 已包含
