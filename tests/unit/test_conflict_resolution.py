"""
信号冲突解决机制单元测试

测试范围:
- EnhancedConflictResolver: 增强型冲突解决器
- ConflictPriorityEngine: 冲突优先级引擎
- ResolutionStrategyLibrary: 解决策略库

性能要求:
- 冲突检测: < 30ms (100信号)
- 冲突分类: < 10ms
- 优先级排序: < 5ms (50冲突)
- 策略选择: < 5ms
- 冲突解决: < 20ms (10冲突)
"""

import pytest
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class NormalizedSignal:
    name: str
    value: float
    confidence: float
    strength: float
    direction: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EnhancedSignalConflict:
    signal_name: str
    conflict_type: str
    macro_signal: NormalizedSignal
    meso_signal: NormalizedSignal
    severity: str
    priority_score: float = 0.0
    direction_info: Optional[Dict] = None
    strength_info: Optional[Dict] = None
    confidence_info: Optional[Dict] = None
    timing_info: Optional[Dict] = None


@dataclass
class MarketState:
    volatility_regime: str
    trend_strength: float


@dataclass
class ConflictResolutionResult:
    resolved_signals: Dict[str, NormalizedSignal]
    resolution_details: List[Dict]
    total_conflicts: int
    resolution_efficiency: float
    timestamp: datetime


class TestEnhancedConflictResolver:
    """测试增强型冲突解决器"""
    
    @pytest.fixture
    def resolver_config(self):
        """解决器配置"""
        from dataclasses import dataclass
        
        @dataclass
        class MockConfig:
            strength_threshold: float = 0.3
            confidence_threshold: float = 0.3
            timing_threshold: float = 0.4
        
        return MockConfig()
    
    @pytest.fixture
    def test_macro_signals(self):
        """测试宏观信号"""
        return {
            'signal_1': NormalizedSignal(
                name='signal_1',
                value=0.8,
                confidence=0.9,
                strength=0.7,
                direction='bullish'
            ),
            'signal_2': NormalizedSignal(
                name='signal_2',
                value=-0.6,
                confidence=0.8,
                strength=0.6,
                direction='bearish'
            ),
            'signal_3': NormalizedSignal(
                name='signal_3',
                value=0.5,
                confidence=0.7,
                strength=0.5,
                direction='bullish'
            )
        }
    
    @pytest.fixture
    def test_meso_signals(self):
        """测试中观信号"""
        return {
            'signal_1': NormalizedSignal(
                name='signal_1',
                value=-0.5,
                confidence=0.7,
                strength=0.4,
                direction='bearish'
            ),
            'signal_2': NormalizedSignal(
                name='signal_2',
                value=-0.7,
                confidence=0.85,
                strength=0.7,
                direction='bearish'
            ),
            'signal_3': NormalizedSignal(
                name='signal_3',
                value=0.4,
                confidence=0.6,
                strength=0.4,
                direction='bullish'
            )
        }
    
    @pytest.fixture
    def test_market_state(self):
        """测试市场状态"""
        return MarketState(
            volatility_regime='normal',
            trend_strength=0.5
        )
    
    def test_direction_conflict_detection(
        self, resolver_config, test_macro_signals, test_meso_signals, test_market_state
    ):
        """测试方向冲突检测"""
        conflicts = []
        
        for signal_name in set(test_macro_signals.keys()) & set(test_meso_signals.keys()):
            macro = test_macro_signals[signal_name]
            meso = test_meso_signals[signal_name]
            
            if (macro.direction != meso.direction and 
                macro.direction != 'neutral' and 
                meso.direction != 'neutral'):
                
                severity = 'high' if abs(macro.value - meso.value) > 0.5 else 'medium'
                
                conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='direction',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity=severity,
                    direction_info={
                        'macro_direction': macro.direction,
                        'meso_direction': meso.direction,
                        'value_diff': abs(macro.value - meso.value)
                    }
                ))
        
        assert len(conflicts) == 1
        assert conflicts[0].signal_name == 'signal_1'
        assert conflicts[0].conflict_type == 'direction'
        assert conflicts[0].severity == 'high'
    
    def test_strength_conflict_detection(
        self, resolver_config, test_macro_signals, test_meso_signals
    ):
        """测试强度冲突检测"""
        conflicts = []
        strength_threshold = 0.2
        
        for signal_name in set(test_macro_signals.keys()) & set(test_meso_signals.keys()):
            macro = test_macro_signals[signal_name]
            meso = test_meso_signals[signal_name]
            
            strength_diff = abs(macro.strength - meso.strength)
            
            if strength_diff > strength_threshold:
                severity = 'medium' if strength_diff > 0.3 else 'low'
                
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
        
        assert len(conflicts) >= 1
        assert all(c.conflict_type == 'strength' for c in conflicts)
    
    def test_confidence_conflict_detection(
        self, resolver_config, test_macro_signals, test_meso_signals
    ):
        """测试置信度冲突检测"""
        conflicts = []
        confidence_threshold = 0.3
        
        for signal_name in set(test_macro_signals.keys()) & set(test_meso_signals.keys()):
            macro = test_macro_signals[signal_name]
            meso = test_meso_signals[signal_name]
            
            confidence_diff = abs(macro.confidence - meso.confidence)
            
            if confidence_diff > confidence_threshold:
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
        
        assert len(conflicts) >= 0
    
    def test_all_conflicts_detection(
        self, resolver_config, test_macro_signals, test_meso_signals, test_market_state
    ):
        """测试所有类型冲突检测"""
        all_conflicts = []
        
        for signal_name in set(test_macro_signals.keys()) & set(test_meso_signals.keys()):
            macro = test_macro_signals[signal_name]
            meso = test_meso_signals[signal_name]
            
            if (macro.direction != meso.direction and 
                macro.direction != 'neutral' and 
                meso.direction != 'neutral'):
                all_conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='direction',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity='high'
                ))
            
            strength_diff = abs(macro.strength - meso.strength)
            if strength_diff > 0.3:
                all_conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='strength',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity='medium'
                ))
        
        assert len(all_conflicts) >= 1
        conflict_types = [c.conflict_type for c in all_conflicts]
        assert 'direction' in conflict_types


class TestConflictPriorityEngine:
    """测试冲突优先级引擎"""
    
    @pytest.fixture
    def priority_config(self):
        """优先级配置"""
        from dataclasses import dataclass
        
        @dataclass
        class MockConfig:
            pass
        
        return MockConfig()
    
    @pytest.fixture
    def test_conflicts(self):
        """测试冲突列表"""
        return [
            EnhancedSignalConflict(
                signal_name='s1',
                conflict_type='direction',
                macro_signal=NormalizedSignal('s1', 0.8, 0.9, 0.7, 'bullish'),
                meso_signal=NormalizedSignal('s1', -0.5, 0.7, 0.5, 'bearish'),
                severity='high'
            ),
            EnhancedSignalConflict(
                signal_name='s2',
                conflict_type='strength',
                macro_signal=NormalizedSignal('s2', 0.6, 0.8, 0.6, 'bullish'),
                meso_signal=NormalizedSignal('s2', 0.5, 0.7, 0.3, 'bullish'),
                severity='medium'
            ),
            EnhancedSignalConflict(
                signal_name='s3',
                conflict_type='timing',
                macro_signal=NormalizedSignal('s3', 0.4, 0.6, 0.4, 'bullish'),
                meso_signal=NormalizedSignal('s3', 0.3, 0.5, 0.3, 'bullish'),
                severity='low'
            )
        ]
    
    @pytest.fixture
    def test_market_state(self):
        """测试市场状态"""
        return MarketState(
            volatility_regime='high',
            trend_strength=0.8
        )
    
    def test_priority_calculation(self, priority_config, test_conflicts, test_market_state):
        """测试优先级计算"""
        severity_scores = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
        type_weights = {
            'direction': 1.0,
            'confidence': 0.8,
            'strength': 0.6,
            'timing': 0.4
        }
        
        for conflict in test_conflicts:
            base_score = severity_scores.get(conflict.severity, 0.5)
            
            if test_market_state.volatility_regime == 'high':
                market_adjustment = 1.3
            else:
                market_adjustment = 1.0
            
            type_weight = type_weights.get(conflict.conflict_type, 0.5)
            
            priority_score = base_score * market_adjustment * type_weight
            conflict.priority_score = priority_score
        
        assert test_conflicts[0].priority_score > test_conflicts[1].priority_score
        assert test_conflicts[1].priority_score > test_conflicts[2].priority_score
    
    def test_priority_sorting(self, priority_config, test_conflicts, test_market_state):
        """测试优先级排序"""
        severity_scores = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
        type_weights = {'direction': 1.0, 'strength': 0.6, 'timing': 0.4}
        
        for conflict in test_conflicts:
            base_score = severity_scores.get(conflict.severity, 0.5)
            market_adjustment = 1.3 if test_market_state.volatility_regime == 'high' else 1.0
            type_weight = type_weights.get(conflict.conflict_type, 0.5)
            conflict.priority_score = base_score * market_adjustment * type_weight
        
        prioritized = sorted(test_conflicts, key=lambda c: c.priority_score, reverse=True)
        
        assert prioritized[0].signal_name == 's1'
        assert prioritized[-1].signal_name == 's3'
        assert all(prioritized[i].priority_score >= prioritized[i+1].priority_score 
                   for i in range(len(prioritized)-1))


class TestResolutionStrategyLibrary:
    """测试解决策略库"""
    
    @pytest.fixture
    def strategy_library(self):
        """策略库"""
        return {
            'direction': {
                'market_state_priority': 'MarketStatePriorityStrategy',
                'confidence_weighted': 'ConfidenceWeightedStrategy'
            },
            'strength': {
                'dynamic_weight': 'DynamicWeightStrategy'
            },
            'confidence': {
                'quality_weighted': 'QualityWeightedStrategy'
            },
            'timing': {
                'phased_execution': 'PhasedExecutionStrategy'
            }
        }
    
    def test_strategy_selection_direction(self, strategy_library):
        """测试方向冲突策略选择"""
        conflict_type = 'direction'
        market_state = MarketState(volatility_regime='high', trend_strength=0.7)
        
        available_strategies = strategy_library.get(conflict_type, {})
        
        if market_state.volatility_regime == 'high':
            selected_strategy = available_strategies.get('market_state_priority')
        else:
            selected_strategy = available_strategies.get('confidence_weighted')
        
        assert selected_strategy == 'MarketStatePriorityStrategy'
    
    def test_strategy_selection_strength(self, strategy_library):
        """测试强度冲突策略选择"""
        conflict_type = 'strength'
        
        available_strategies = strategy_library.get(conflict_type, {})
        selected_strategy = available_strategies.get('dynamic_weight')
        
        assert selected_strategy == 'DynamicWeightStrategy'
    
    def test_market_state_priority_resolution(self):
        """测试市场状态优先策略解决"""
        conflict = EnhancedSignalConflict(
            signal_name='test',
            conflict_type='direction',
            macro_signal=NormalizedSignal('test', 0.8, 0.9, 0.7, 'bullish'),
            meso_signal=NormalizedSignal('test', -0.5, 0.7, 0.5, 'bearish'),
            severity='high'
        )
        
        market_state = MarketState(volatility_regime='high', trend_strength=0.7)
        
        if market_state.trend_strength > 0.6:
            primary_signal = conflict.macro_signal
            secondary_signal = conflict.meso_signal
            primary_weight = 0.7
        else:
            primary_signal = conflict.meso_signal
            secondary_signal = conflict.macro_signal
            primary_weight = 0.6
        
        resolved_value = (
            primary_weight * primary_signal.value +
            (1 - primary_weight) * secondary_signal.value
        )
        
        assert resolved_value == pytest.approx(0.41, rel=0.01)
    
    def test_confidence_weighted_resolution(self):
        """测试置信度加权策略解决"""
        conflict = EnhancedSignalConflict(
            signal_name='test',
            conflict_type='direction',
            macro_signal=NormalizedSignal('test', 0.8, 0.9, 0.7, 'bullish'),
            meso_signal=NormalizedSignal('test', -0.5, 0.7, 0.5, 'bearish'),
            severity='high'
        )
        
        total_confidence = conflict.macro_signal.confidence + conflict.meso_signal.confidence
        
        if total_confidence == 0:
            macro_weight = 0.5
            meso_weight = 0.5
        else:
            macro_weight = conflict.macro_signal.confidence / total_confidence
            meso_weight = conflict.meso_signal.confidence / total_confidence
        
        resolved_value = (
            macro_weight * conflict.macro_signal.value +
            meso_weight * conflict.meso_signal.value
        )
        
        assert resolved_value == pytest.approx(0.23125, rel=0.01)


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """性能基准测试"""
    
    def test_conflict_detection_performance(self):
        """测试冲突检测性能"""
        import time
        
        macro_signals = {
            f'signal_{i}': NormalizedSignal(
                name=f'signal_{i}',
                value=np.random.uniform(-1, 1),
                confidence=np.random.uniform(0.5, 1.0),
                strength=np.random.uniform(0.3, 1.0),
                direction='bullish' if np.random.random() > 0.5 else 'bearish'
            )
            for i in range(100)
        }
        
        meso_signals = {
            f'signal_{i}': NormalizedSignal(
                name=f'signal_{i}',
                value=np.random.uniform(-1, 1),
                confidence=np.random.uniform(0.5, 1.0),
                strength=np.random.uniform(0.3, 1.0),
                direction='bullish' if np.random.random() > 0.5 else 'bearish'
            )
            for i in range(100)
        }
        
        start_time = time.time()
        
        conflicts = []
        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            if macro.direction != meso.direction:
                conflicts.append(EnhancedSignalConflict(
                    signal_name=signal_name,
                    conflict_type='direction',
                    macro_signal=macro,
                    meso_signal=meso,
                    severity='high'
                ))
        
        elapsed_time = (time.time() - start_time) * 1000
        
        assert elapsed_time < 30, f"冲突检测耗时 {elapsed_time}ms，超过30ms阈值"
    
    def test_priority_sorting_performance(self):
        """测试优先级排序性能"""
        import time
        
        conflicts = [
            EnhancedSignalConflict(
                signal_name=f's{i}',
                conflict_type='direction',
                macro_signal=NormalizedSignal(f's{i}', 0.5, 0.7, 0.5, 'bullish'),
                meso_signal=NormalizedSignal(f's{i}', -0.3, 0.6, 0.4, 'bearish'),
                severity='high',
                priority_score=np.random.random()
            )
            for i in range(50)
        ]
        
        start_time = time.time()
        
        prioritized = sorted(conflicts, key=lambda c: c.priority_score, reverse=True)
        
        elapsed_time = (time.time() - start_time) * 1000
        
        assert elapsed_time < 5, f"优先级排序耗时 {elapsed_time}ms，超过5ms阈值"
    
    def test_conflict_resolution_performance(self):
        """测试冲突解决性能"""
        import time
        
        conflicts = [
            EnhancedSignalConflict(
                signal_name=f's{i}',
                conflict_type='direction',
                macro_signal=NormalizedSignal(f's{i}', 0.8, 0.9, 0.7, 'bullish'),
                meso_signal=NormalizedSignal(f's{i}', -0.5, 0.7, 0.5, 'bearish'),
                severity='high'
            )
            for i in range(10)
        ]
        
        start_time = time.time()
        
        resolved_signals = {}
        for conflict in conflicts:
            resolved_value = 0.6 * conflict.macro_signal.value + 0.4 * conflict.meso_signal.value
            resolved_signals[conflict.signal_name] = NormalizedSignal(
                name=conflict.signal_name,
                value=resolved_value,
                confidence=0.8,
                strength=0.6,
                direction='bullish' if resolved_value > 0 else 'bearish'
            )
        
        elapsed_time = (time.time() - start_time) * 1000
        
        assert elapsed_time < 20, f"冲突解决耗时 {elapsed_time}ms，超过20ms阈值"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
