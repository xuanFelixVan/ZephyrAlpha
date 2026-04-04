﻿﻿﻿---
module_id: SIMPLIFIED_TIMEFRAME_COORDINATION_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-03
created_date: 2026-04-03
layer: Layer 6 (组合优化? | 业务架构: 三级时间框架融合架构
index: TIMEFRAME_COORD_001
estimated_hours: 80h
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-03
owner: 组合优化层负责人
standard_type: 专业量化机构蓝图文档（简化版?applicable_scope: 全系?compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
personal_development: true
ai_maintenance: true
simplified_version: true
---

# 简化版多时间框架协同优化蓝?v1.0

> 清风量化系统 v5.3 - 简化版多时间框架协同优化架构设?> **索引**: `TIMEFRAME_COORD_001`
> **开发时?*: 80h（约2周）
> **核心定位**: 双时间框架协同（宏观季度 + 中观日度），实现信号融合与冲突解?> **个人开发可行?*: ⭐⭐?部分可行（简化版?> **AI维护难度**: ?
---

## 1. 模块概述

### 1.1 简化说?
**原版设计**（Two Sigma实现）：
- 三级时间框架协同（宏观季?+ 中观日度 + 微观分钟?- 复杂的信号融合机?- 时间框架间的风险传递控?- 开发时间：120h

**简化版设计**（个人开发）?- ?**保留**: 双时间框架协同（宏观季度 + 中观日度?- ?**保留**: 信号融合机制
- ?**保留**: 冲突检测与解决
- ?**放弃**: 微观分钟级时间框?- ?**放弃**: 复杂的风险传递机?
**简化理?*?- 个人开发资源有限，优先实现核心功能
- 双时间框架已能满足基本协同需?- 降低系统复杂度，提升可维护?
### 1.2 业务背景与价值主?
**业务需?*?- 当前系统各时间框架独立优化，信号冲突频发
- 缺乏跨时间框架的协同机制
- 无法有效融合不同时间框架的信?
**价值主?*?- 实现双时间框架信号融?- 信号冲突率降?0%
- 提升组合优化效率20%
- 为Two Sigma模式提供核心能力支撑

### 1.3 技术定位与架构层归?
**Layer定位**: Layer 6 - 组合优化层（协同优化层）

**模块类别**: 核心模块（简化版?
**架构角色**: 
- 作为多时间框架的协同中心，融合不同时间框架的信号
- 作为信号冲突解决器，协调不同时间框架的决?- 作为组合优化的输入，提供协同后的信号

### 1.4 核心功能清单

1. **信号融合**: 融合宏观和中观时间框架的信号
2. **冲突检?*: 检测不同时间框架的信号冲突
3. **冲突解决**: 解决信号冲突，生成最终决?4. **权重调整**: 动态调整时间框架权?
---

## 2. 架构设计

### 2.1 系统架构?
```
┌─────────────────────────────────────────────────────────────────??             简化版多时间框架协同优化系统架?                     ?├─────────────────────────────────────────────────────────────────??                                                                ?? ┌──────────────────────────────────────────────────────────? ?? ?             输入?                                       ? ?? ? ┌──────────────────────? ┌──────────────────────?    ? ?? ? ?宏观信号（季度）      ? ?中观信号（日度）      ?    ? ?? ? ?- 经济范式判断        ? ?- 策略信号           ?    ? ?? ? ?- 战略资产配置        ? ?- 因子信号           ?    ? ?? ? ?- 风险预算分配        ? ?- 交易信号           ?    ? ?? ? └──────────────────────? └──────────────────────?    ? ?? └──────────────────────────────────────────────────────────? ??                         ?                                     ?? ┌──────────────────────────────────────────────────────────? ?? ?             信号融合?                                   ? ?? ? ┌────────────────────────────────────────────────────? ? ?? ? ? Signal Fusion Engine                              ? ? ?? ? ? - 信号标准?                                      ? ? ?? ? ? - 信号加权                                         ? ? ?? ? ? - 信号组合                                         ? ? ?? ? └────────────────────────────────────────────────────? ? ?? └──────────────────────────────────────────────────────────? ??                         ?                                     ?? ┌──────────────────────────────────────────────────────────? ?? ?             冲突检测与解决?                             ? ?? ? ┌──────────? ┌──────────? ┌──────────?              ? ?? ? ?冲突检?? ?冲突分类 ? ?冲突解决 ?              ? ?? ? ?         ? ?         ? ?         ?              ? ?? ? └──────────? └──────────? └──────────?              ? ?? └──────────────────────────────────────────────────────────? ??                         ?                                     ?? ┌──────────────────────────────────────────────────────────? ?? ?             权重调整?                                   ? ?? ? ┌────────────────────────────────────────────────────? ? ?? ? ? Dynamic Timeframe Weight Adjustment               ? ? ?? ? ? 基于市场状态动态调整时间框架权?                  ? ? ?? ? └────────────────────────────────────────────────────? ? ?? └──────────────────────────────────────────────────────────? ??                         ?                                     ?? ┌──────────────────────────────────────────────────────────? ?? ?             输出?                                       ? ?? ? ┌──────────? ┌──────────? ┌──────────?              ? ?? ? ?协同信号 ? ?冲突报告 ? ?权重方案 ?              ? ?? ? ?         ? ?         ? ?         ?              ? ?? ? └──────────? └──────────? └──────────?              ? ?? └──────────────────────────────────────────────────────────? ?└─────────────────────────────────────────────────────────────────?```

### 2.2 核心数据?
```
宏观信号（季度） + 中观信号（日度）
    ?信号标准化与对齐
    ?信号融合（加权组合）
    ?冲突检?    ?冲突解决（如有冲突）
    ?动态权重调?    ?输出协同信号
```

---

## 3. 核心模块设计

### 3.1 简化版时间框架协同器（SimplifiedTimeframeCoordinator?
```python
class SimplifiedTimeframeCoordinator:
    """
    简化版多时间框架协同器
    
    索引: TIMEFRAME_COORD_001-M01
    职责: 协调宏观和中观时间框架的信号
    输入: 宏观信号、中观信?    输出: 协同后的信号、冲突报?    """
    
    def __init__(self, config: TimeframeConfig):
        self.config = config
        self.signal_fusion_engine = SignalFusionEngine(config.fusion_config)
        self.conflict_resolver = ConflictResolver(config.conflict_config)
        self.weight_adjuster = TimeframeWeightAdjuster(config.weight_config)
        
    def coordinate_signals(
        self,
        macro_signals: Dict[str, Signal],
        meso_signals: Dict[str, Signal],
        market_state: MarketState
    ) -> CoordinatedDecision:
        """
        协同多时间框架信?        
        Args:
            macro_signals: 宏观层信号（季度?            meso_signals: 中观层信号（日度?            market_state: 市场状?            
        Returns:
            CoordinatedDecision: 协同后的决策
        """
        # 1. 信号标准?        normalized_macro = self._normalize_signals(macro_signals)
        normalized_meso = self._normalize_signals(meso_signals)
        
        # 2. 动态权重调?        timeframe_weights = self.weight_adjuster.adjust_weights(market_state)
        
        # 3. 信号融合
        fused_signals = self.signal_fusion_engine.fuse(
            normalized_macro, normalized_meso, timeframe_weights
        )
        
        # 4. 冲突检?        conflicts = self.conflict_resolver.detect_conflicts(
            normalized_macro, normalized_meso, fused_signals
        )
        
        # 5. 冲突解决
        if conflicts:
            resolved_signals = self.conflict_resolver.resolve(conflicts, fused_signals)
        else:
            resolved_signals = fused_signals
        
        return CoordinatedDecision(
            signals=resolved_signals,
            timeframe_weights=timeframe_weights,
            conflicts=conflicts,
            conflict_resolution=self.conflict_resolver.get_resolution_log(),
            timestamp=datetime.now()
        )
    
    def fuse_signals(
        self,
        macro_signals: Dict[str, Signal],
        meso_signals: Dict[str, Signal],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Signal]:
        """
        融合信号
        
        Args:
            macro_signals: 宏观信号
            meso_signals: 中观信号
            weights: 时间框架权重（可选）
            
        Returns:
            Dict[str, Signal]: 融合后的信号
        """
        if weights is None:
            weights = {'macro': 0.3, 'meso': 0.7}  # 默认权重
        
        return self.signal_fusion_engine.fuse(
            macro_signals, meso_signals, weights
        )
    
    def detect_conflicts(
        self,
        macro_signals: Dict[str, Signal],
        meso_signals: Dict[str, Signal]
    ) -> List[SignalConflict]:
        """
        检测信号冲?        
        Args:
            macro_signals: 宏观信号
            meso_signals: 中观信号
            
        Returns:
            List[SignalConflict]: 冲突列表
        """
        return self.conflict_resolver.detect_conflicts(
            macro_signals, meso_signals
        )
    
    def _normalize_signals(
        self,
        signals: Dict[str, Signal]
    ) -> Dict[str, NormalizedSignal]:
        """信号标准?""
        normalized = {}
        for signal_name, signal in signals.items():
            normalized[signal_name] = NormalizedSignal(
                name=signal_name,
                value=signal.value,
                confidence=signal.confidence,
                direction=self._get_signal_direction(signal.value),
                strength=abs(signal.value)
            )
        return normalized
    
    def _get_signal_direction(self, value: float) -> str:
        """获取信号方向"""
        if value > 0.1:
            return 'bullish'
        elif value < -0.1:
            return 'bearish'
        else:
            return 'neutral'
```

### 3.2 信号融合引擎（SignalFusionEngine?
```python
class SignalFusionEngine:
    """
    信号融合引擎
    
    索引: TIMEFRAME_COORD_001-M02
    职责: 融合不同时间框架的信?    """
    
    def __init__(self, config: FusionConfig):
        self.config = config
        
    def fuse(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal],
        weights: Dict[str, float]
    ) -> Dict[str, Signal]:
        """
        融合信号
        
        Args:
            macro_signals: 宏观信号
            meso_signals: 中观信号
            weights: 时间框架权重
            
        Returns:
            Dict[str, Signal]: 融合后的信号
        """
        fused_signals = {}
        
        # 获取所有信号名?        all_signal_names = set(macro_signals.keys()) | set(meso_signals.keys())
        
        for signal_name in all_signal_names:
            macro_signal = macro_signals.get(signal_name)
            meso_signal = meso_signals.get(signal_name)
            
            # 加权融合
            if macro_signal and meso_signal:
                fused_value = (
                    weights['macro'] * macro_signal.value +
                    weights['meso'] * meso_signal.value
                )
                fused_confidence = (
                    weights['macro'] * macro_signal.confidence +
                    weights['meso'] * meso_signal.confidence
                )
            elif macro_signal:
                fused_value = macro_signal.value
                fused_confidence = macro_signal.confidence
            elif meso_signal:
                fused_value = meso_signal.value
                fused_confidence = meso_signal.confidence
            else:
                continue
            
            fused_signals[signal_name] = Signal(
                name=signal_name,
                value=fused_value,
                confidence=fused_confidence,
                source='fusion'
            )
        
        return fused_signals
```

### 3.3 冲突解决器（ConflictResolver?
```python
class ConflictResolver:
    """
    冲突解决?    
    索引: TIMEFRAME_COORD_001-M03
    职责: 检测和解决信号冲突
    """
    
    def __init__(self, config: ConflictConfig):
        self.config = config
        self.resolution_log = []
        
    def detect_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal],
        fused_signals: Optional[Dict[str, Signal]] = None
    ) -> List[SignalConflict]:
        """
        检测信号冲?        
        Args:
            macro_signals: 宏观信号
            meso_signals: 中观信号
            fused_signals: 融合后的信号（可选）
            
        Returns:
            List[SignalConflict]: 冲突列表
        """
        conflicts = []
        
        # 检查方向冲?        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            # 方向相反
            if macro.direction != meso.direction and macro.direction != 'neutral' and meso.direction != 'neutral':
                conflicts.append(SignalConflict(
                    signal_name=signal_name,
                    conflict_type='direction',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity='high' if abs(macro.value - meso.value) > 0.5 else 'medium'
                ))
            
            # 强度差异过大
            elif abs(macro.strength - meso.strength) > self.config.strength_threshold:
                conflicts.append(SignalConflict(
                    signal_name=signal_name,
                    conflict_type='strength',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity='low'
                ))
        
        return conflicts
    
    def resolve(
        self,
        conflicts: List[SignalConflict],
        fused_signals: Dict[str, Signal]
    ) -> Dict[str, Signal]:
        """
        解决冲突
        
        Args:
            conflicts: 冲突列表
            fused_signals: 融合后的信号
            
        Returns:
            Dict[str, Signal]: 解决冲突后的信号
        """
        resolved_signals = fused_signals.copy()
        
        for conflict in conflicts:
            if conflict.conflict_type == 'direction':
                # 方向冲突：优先使用宏观信号（长期趋势?                resolved_signals[conflict.signal_name] = Signal(
                    name=conflict.signal_name,
                    value=conflict.macro_signal.value * 0.6 + conflict.meso_signal.value * 0.4,
                    confidence=min(conflict.macro_signal.confidence, conflict.meso_signal.confidence) * 0.8,
                    source='resolution'
                )
                
                self.resolution_log.append({
                    'signal': conflict.signal_name,
                    'type': 'direction',
                    'resolution': 'weighted_average_with_macro_priority',
                    'timestamp': datetime.now()
                })
            
            elif conflict.conflict_type == 'strength':
                # 强度冲突：使用平均?                resolved_signals[conflict.signal_name] = Signal(
                    name=conflict.signal_name,
                    value=(conflict.macro_signal.value + conflict.meso_signal.value) / 2,
                    confidence=(conflict.macro_signal.confidence + conflict.meso_signal.confidence) / 2,
                    source='resolution'
                )
        
        return resolved_signals
    
    def get_resolution_log(self) -> List[Dict]:
        """获取冲突解决日志"""
        return self.resolution_log
```

### 3.4 时间框架权重调整器（TimeframeWeightAdjuster?
```python
class TimeframeWeightAdjuster:
    """
    时间框架权重调整?    
    索引: TIMEFRAME_COORD_001-M04
    职责: 基于市场状态动态调整时间框架权?    """
    
    def __init__(self, config: WeightConfig):
        self.config = config
        
    def adjust_weights(
        self,
        market_state: MarketState
    ) -> Dict[str, float]:
        """
        调整时间框架权重
        
        Args:
            market_state: 市场状?            
        Returns:
            Dict[str, float]: 时间框架权重
        """
        # 基础权重
        base_weights = {'macro': 0.3, 'meso': 0.7}
        
        # 根据市场状态调?        if market_state.volatility == 'high':
            # 高波动市场：增加宏观权重（长期趋势更可靠?            weights = {'macro': 0.5, 'meso': 0.5}
        elif market_state.trend == 'strong':
            # 强趋势市场：增加中观权重（短期趋势更明显?            weights = {'macro': 0.2, 'meso': 0.8}
        elif market_state.regime == 'crisis':
            # 危机市场：增加宏观权重（长期配置更重要）
            weights = {'macro': 0.6, 'meso': 0.4}
        else:
            # 正常市场：使用基础权重
            weights = base_weights
        
        return weights
```

### 3.5 配置类定?
```python
@dataclass
class TimeframeConfig:
    """时间框架协同配置"""
    fusion_config: FusionConfig
    conflict_config: ConflictConfig
    weight_config: WeightConfig
    
@dataclass
class FusionConfig:
    """信号融合配置"""
    default_macro_weight: float = 0.3
    default_meso_weight: float = 0.7
    confidence_threshold: float = 0.5
    
@dataclass
class ConflictConfig:
    """冲突检测配?""
    strength_threshold: float = 0.3  # 强度差异阈?    direction_threshold: float = 0.1  # 方向差异阈?    
@dataclass
class WeightConfig:
    """权重调整配置"""
    adjustment_frequency: str = 'daily'  # 调整频率
    min_weight: float = 0.1  # 最小权?    max_weight: float = 0.9  # 最大权?```

---

## 4. 数据模型定义

### 4.1 输入数据模型

```python
@dataclass
class Signal:
    """信号"""
    name: str
    value: float  # 信号值（-1??    confidence: float  # 置信度（0??    source: str  # 信号来源
    
@dataclass
class NormalizedSignal:
    """标准化信?""
    name: str
    value: float
    confidence: float
    direction: str  # bullish/bearish/neutral
    strength: float  # 信号强度
    
@dataclass
class MarketState:
    """市场状?""
    volatility: str  # low/medium/high
    trend: str  # weak/strong
    regime: str  # normal/stress/crisis
```

### 4.2 输出数据模型

```python
@dataclass
class CoordinatedDecision:
    """协同决策"""
    signals: Dict[str, Signal]
    timeframe_weights: Dict[str, float]
    conflicts: List[SignalConflict]
    conflict_resolution: List[Dict]
    timestamp: datetime
    
@dataclass
class SignalConflict:
    """信号冲突"""
    signal_name: str
    conflict_type: str  # direction/strength
    macro_signal: NormalizedSignal
    meso_signal: NormalizedSignal
    severity: str  # low/medium/high
```

---

## 5. 集成方案

### 5.1 与组合优化器集成

```python
class PortfolioOptimizer:
    """组合优化器（集成时间框架协同?""
    
    def __init__(self, coordinator: SimplifiedTimeframeCoordinator):
        self.coordinator = coordinator
        
    def optimize_with_coordination(
        self,
        macro_signals: Dict[str, Signal],
        meso_signals: Dict[str, Signal],
        market_state: MarketState
    ) -> OptimizationResult:
        """协同优化的组合优?""
        # 1. 协同信号
        coordinated = self.coordinator.coordinate_signals(
            macro_signals, meso_signals, market_state
        )
        
        # 2. 使用协同信号进行优化
        optimized_weights = self._optimize_using_signals(coordinated.signals)
        
        return OptimizationResult(
            weights=optimized_weights,
            coordinated_signals=coordinated.signals,
            conflicts=coordinated.conflicts
        )
```

---

## 6. 实施路线?
### 6.1 开发阶段（2周）

**Week 1: 核心功能开?*
- Day 1-2: 信号融合引擎
- Day 3-4: 冲突检测与解决?- Day 5: 权重调整?
**Week 2: 集成与测?*
- Day 1-2: 系统集成
- Day 3: 单元测试
- Day 4: 集成测试
- Day 5: 文档编写

### 6.2 里程?
| 里程?| 时间 | 交付?| 验收标准 |
|--------|------|--------|----------|
| **M1: 融合引擎完成** | Day 2 | 信号融合引擎 | 融合正常 |
| **M2: 冲突解决完成** | Day 4 | 冲突解决?| 解决有效 |
| **M3: 权重调整完成** | Day 5 | 权重调整?| 调整合理 |
| **M4: 集成完成** | Day 7 | 完整系统 | 所有接口正?|
| **M5: 测试通过** | Day 8 | 测试报告 | 所有测试通过 |

---

## 7. 预期收益评估

### 7.1 定量收益

| 指标 | 当前水平 | 目标水平 | 提升幅度 |
|------|---------|---------|---------|
| **信号冲突?* | ?| ?| -60% |
| **组合优化效率** | ?| ?| +20% |
| **协同决策质量** | ?| ?| 提升2?|

### 7.2 定性收?
- ?实现Two Sigma核心能力（简化版）：多时间框架协?- ?降低信号冲突?- ?提升组合优化效率
- ?建立协同决策机制

---

## 8. 与原版对?
| 特?| 原版（Two Sigma?| 简化版 | 说明 |
|------|-----------------|--------|------|
| **时间框架数量** | 三级 | 双级 | 简化架?|
| **信号融合方法** | 复杂 | 加权平均 | 简化算?|
| **冲突解决机制** | 多层?| 单层?| 简化逻辑 |
| **开发时?* | 120h | 80h | 减少33% |
| **维护复杂?* | ?| ?| 降低难度 |

---

## 附录

### A. 参考文?
1. **多时间框架分?*:
   - Murphy, J. (1999). "Technical Analysis of the Financial Markets"

2. **信号融合理论**:
   - Hall, D.L. and Llinas, J. (1997). "An Introduction to Multisensor Data Fusion"


---

## 9. 信号冲突解决机制增强设计

### 9.1 冲突分类体系

`

                 信号冲突分类体系                                

                                                                 
     
    Level 1: 方向冲突（Direction Conflict）                   
    - 多头 vs 空头                                            
    - 严重程度：高                                            
    - 解决策略：市场状态优先 + 置信度加权                     
     
                                                                 
     
    Level 2: 强度冲突（Strength Conflict）                    
    - 强信号 vs 弱信号                                        
    - 严重程度：中                                            
    - 解决策略：动态权重调整 + 历史表现参考                   
     
                                                                 
     
    Level 3: 置信度冲突（Confidence Conflict）                
    - 高置信 vs 低置信                                        
    - 严重程度：中                                            
    - 解决策略：置信度加权 + 信号质量评估                     
     
                                                                 
     
    Level 4: 时机冲突（Timing Conflict）                      
    - 立即行动 vs 等待观察                                    
    - 严重程度：低                                            
    - 解决策略：分阶段执行 + 动态监控                         
     
                                                                 

`

### 9.2 增强型冲突解决器

`python
class EnhancedConflictResolver:
    """
    增强型冲突解决器
    
    索引: TIMEFRAME_COORD_001-M05（增强）
    职责: 多维度冲突检测与智能解决
    """
    
    def __init__(self, config: EnhancedConflictConfig):
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
            macro_signals: 宏观信号
            meso_signals: 中观信号
            market_state: 市场状态
            
        Returns:
            List[EnhancedSignalConflict]: 增强型冲突列表
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
    
    def _detect_direction_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal]
    ) -> List[EnhancedSignalConflict]:
        """检测方向冲突"""
        conflicts = []
        
        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            # 判断方向
            macro_direction = self._get_signal_direction(macro.value)
            meso_direction = self._get_signal_direction(meso.value)
            
            # 方向相反且都不为中性
            if (macro_direction != meso_direction and 
                macro_direction != 'neutral' and 
                meso_direction != 'neutral'):
                
                severity = self._calculate_direction_severity(
                    macro.value, meso.value
                )
                
                conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='direction',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity=severity,
                    direction_info={
                        'macro_direction': macro_direction,
                        'meso_direction': meso_direction,
                        'value_diff': abs(macro.value - meso.value)
                    }
                ))
        
        return conflicts
    
    def _detect_strength_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal]
    ) -> List[EnhancedSignalConflict]:
        """检测强度冲突"""
        conflicts = []
        
        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            strength_diff = abs(macro.strength - meso.strength)
            
            if strength_diff > self.config.strength_threshold:
                severity = 'medium' if strength_diff > 0.5 else 'low'
                
                conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='strength',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity=severity,
                    strength_info={
                        'macro_strength': macro.strength,
                        'meso_strength': meso.strength,
                        'strength_diff': strength_diff
                    }
                ))
        
        return conflicts
    
    def _detect_confidence_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal]
    ) -> List[EnhancedSignalConflict]:
        """检测置信度冲突"""
        conflicts = []
        
        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            confidence_diff = abs(macro.confidence - meso.confidence)
            
            if confidence_diff > self.config.confidence_threshold:
                severity = 'medium' if confidence_diff > 0.4 else 'low'
                
                conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='confidence',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity=severity,
                    confidence_info={
                        'macro_confidence': macro.confidence,
                        'meso_confidence': meso.confidence,
                        'confidence_diff': confidence_diff
                    }
                ))
        
        return conflicts
    
    def _detect_timing_conflicts(
        self,
        macro_signals: Dict[str, NormalizedSignal],
        meso_signals: Dict[str, NormalizedSignal],
        market_state: MarketState
    ) -> List[EnhancedSignalConflict]:
        """检测时机冲突"""
        conflicts = []
        
        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            # 判断时机差异（基于信号变化率）
            macro_urgency = self._calculate_signal_urgency(macro, market_state)
            meso_urgency = self._calculate_signal_urgency(meso, market_state)
            
            urgency_diff = abs(macro_urgency - meso_urgency)
            
            if urgency_diff > self.config.timing_threshold:
                conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='timing',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity='low',
                    timing_info={
                        'macro_urgency': macro_urgency,
                        'meso_urgency': meso_urgency,
                        'urgency_diff': urgency_diff
                    }
                ))
        
        return conflicts
`

### 9.3 冲突优先级引擎

`python
class ConflictPriorityEngine:
    """
    冲突优先级引擎
    
    索引: TIMEFRAME_COORD_001-M06（增强）
    职责: 基于多维度因素确定冲突解决优先级
    """
    
    def __init__(self, config: PriorityConfig):
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
        """计算优先级分数"""
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
    
    def _get_market_adjustment(self, market_state: MarketState) -> float:
        """获取市场状态调整系数"""
        # 高波动市场提高优先级
        if market_state.volatility_regime == 'high':
            return 1.3
        # 趋势市场中等优先级
        elif market_state.trend_strength > 0.7:
            return 1.1
        # 震荡市场降低优先级
        else:
            return 0.9
`

### 9.4 解决策略库

`python
class ResolutionStrategyLibrary:
    """
    冲突解决策略库
    
    索引: TIMEFRAME_COORD_001-M07（增强）
    职责: 提供多种冲突解决策略
    """
    
    def __init__(self):
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
        """基于市场状态优先级解决方向冲突"""
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


class ConfidenceWeightedStrategy(ResolutionStrategy):
    """置信度加权策略"""
    
    name = 'confidence_weighted'
    
    def resolve(
        self,
        conflict: EnhancedSignalConflict,
        market_state: MarketState,
        historical_performance: Optional[Dict] = None
    ) -> Signal:
        """基于置信度加权解决冲突"""
        total_confidence = (
            conflict.macro_signal.confidence + 
            conflict.meso_signal.confidence
        )
        
        if total_confidence == 0:
            # 如果置信度都为0，平均分配
            macro_weight = 0.5
            meso_weight = 0.5
        else:
            macro_weight = conflict.macro_signal.confidence / total_confidence
            meso_weight = conflict.meso_signal.confidence / total_confidence
        
        resolved_value = (
            macro_weight * conflict.macro_signal.value +
            meso_weight * conflict.meso_signal.value
        )
        
        resolved_confidence = (
            macro_weight * conflict.macro_signal.confidence +
            meso_weight * conflict.meso_signal.confidence
        )
        
        return Signal(
            name=conflict.signal_name,
            value=resolved_value,
            confidence=resolved_confidence,
            source='confidence_weighted_resolution'
        )
`

### 9.5 增强配置类

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

### 9.6 增强数据模型

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
    resolution_efficiency: float  # 解决效率评分
    timestamp: datetime
`

### 9.7 预期收益（增强版）

| 指标 | 简化版 | 增强版 | 提升幅度 |
|------|--------|--------|---------|
| **冲突检测维度** | 2个 | 4个 | +100% |
| **冲突解决策略** | 2个 | 8个 | +300% |
| **冲突解决准确率** | 75% | 90% | +15% |
| **信号冲突率** | 30% | 15% | -50% |
| **协同决策质量** | 良好 | 优秀 | 提升1个等级 |
---

**蓝图版本**: v1.0 | **创建日期**: 2026-04-03 | **状?*: Final | **简化版**: ?| **下一?*: 技术规格书编写

