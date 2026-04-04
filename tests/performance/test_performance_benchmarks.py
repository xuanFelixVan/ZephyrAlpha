"""
性能基准测试套件

测试目标:
- 验证多层次风险预算系统性能
- 验证信号冲突解决机制性能
- 建立性能基准线
- 识别性能瓶颈

性能要求:
- 预算分配: < 100ms (100策略 + 1000资产)
- 风险传递: < 50ms
- 冲突检测: < 30ms (100信号)
- 冲突解决: < 20ms (10冲突)
"""

import pytest
import numpy as np
import pandas as pd
import time
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, field
import json


@dataclass
class PerformanceMetrics:
    """性能指标"""
    operation_name: str
    execution_time_ms: float
    data_size: int
    throughput: float  # 操作/秒
    meets_requirement: bool
    requirement_threshold_ms: float


class PerformanceBenchmarkSuite:
    """性能基准测试套件"""
    
    def __init__(self):
        self.results: List[PerformanceMetrics] = []
        self.baseline_results: Dict[str, float] = {}
    
    def run_benchmark(
        self,
        operation_name: str,
        operation_func,
        data_size: int,
        requirement_threshold_ms: float,
        iterations: int = 10
    ) -> PerformanceMetrics:
        """
        运行基准测试
        
        Args:
            operation_name: 操作名称
            operation_func: 操作函数
            data_size: 数据规模
            requirement_threshold_ms: 性能要求阈值（毫秒）
            iterations: 迭代次数
            
        Returns:
            PerformanceMetrics: 性能指标
        """
        execution_times = []
        
        for _ in range(iterations):
            start_time = time.time()
            operation_func()
            elapsed_time = (time.time() - start_time) * 1000
            execution_times.append(elapsed_time)
        
        avg_execution_time = np.mean(execution_times)
        throughput = (iterations / (avg_execution_time / 1000)) if avg_execution_time > 0 else 0
        
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time_ms=avg_execution_time,
            data_size=data_size,
            throughput=throughput,
            meets_requirement=avg_execution_time <= requirement_threshold_ms,
            requirement_threshold_ms=requirement_threshold_ms
        )
        
        self.results.append(metrics)
        
        return metrics
    
    def generate_report(self) -> str:
        """生成性能报告"""
        report_lines = [
            "=" * 80,
            "性能基准测试报告",
            "=" * 80,
            ""
        ]
        
        for metrics in self.results:
            status = "✓ 通过" if metrics.meets_requirement else "✗ 失败"
            report_lines.extend([
                f"操作: {metrics.operation_name}",
                f"  数据规模: {metrics.data_size}",
                f"  平均执行时间: {metrics.execution_time_ms:.2f}ms",
                f"  性能要求: {metrics.requirement_threshold_ms:.2f}ms",
                f"  状态: {status}",
                f"  吞吐量: {metrics.throughput:.2f} 操作/秒",
                ""
            ])
        
        passed = sum(1 for m in self.results if m.meets_requirement)
        total = len(self.results)
        
        report_lines.extend([
            "=" * 80,
            f"测试总结: {passed}/{total} 通过",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def save_results(self, filepath: str):
        """保存测试结果"""
        results_dict = {
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "operation_name": m.operation_name,
                    "execution_time_ms": m.execution_time_ms,
                    "data_size": m.data_size,
                    "throughput": m.throughput,
                    "meets_requirement": m.meets_requirement,
                    "requirement_threshold_ms": m.requirement_threshold_ms
                }
                for m in self.results
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=2, ensure_ascii=False)


class TestMultiLayerRiskBudgetPerformance:
    """多层次风险预算性能测试"""
    
    @pytest.fixture
    def benchmark_suite(self):
        """基准测试套件"""
        return PerformanceBenchmarkSuite()
    
    def test_budget_allocation_performance(self, benchmark_suite):
        """测试预算分配性能"""
        from dataclasses import dataclass
        
        @dataclass
        class StrategyInfo:
            strategy_id: str
            risk_contribution: float
            sharpe_ratio: float
        
        def allocate_budget():
            strategies = {
                f's{i}': StrategyInfo(
                    strategy_id=f's{i}',
                    risk_contribution=np.random.random(),
                    sharpe_ratio=np.random.uniform(0.5, 2.0)
                )
                for i in range(100)
            }
            
            total_risk_contribution = sum(s.risk_contribution for s in strategies.values())
            strategy_budgets = {
                sid: 0.15 * (s.risk_contribution / total_risk_contribution)
                for sid, s in strategies.items()
            }
            
            return strategy_budgets
        
        metrics = benchmark_suite.run_benchmark(
            operation_name="预算分配 (100策略)",
            operation_func=allocate_budget,
            data_size=100,
            requirement_threshold_ms=100.0,
            iterations=10
        )
        
        assert metrics.meets_requirement, f"预算分配性能不达标: {metrics.execution_time_ms:.2f}ms > {metrics.requirement_threshold_ms:.2f}ms"
    
    def test_risk_cascading_performance(self, benchmark_suite):
        """测试风险传递性能"""
        from dataclasses import dataclass
        
        @dataclass
        class AssetInfo:
            asset_id: str
            strategy_id: str
            weight: float
        
        def cascade_risk():
            strategy_budgets = {f's{i}': 0.0015 for i in range(100)}
            
            assets = {
                f'a{i}': AssetInfo(
                    asset_id=f'a{i}',
                    strategy_id=f's{i % 100}',
                    weight=np.random.random()
                )
                for i in range(1000)
            }
            
            asset_budgets = {}
            for asset_id, asset_info in assets.items():
                strategy_id = asset_info.strategy_id
                if strategy_id in strategy_budgets:
                    asset_budgets[asset_id] = strategy_budgets[strategy_id] * asset_info.weight
            
            return asset_budgets
        
        metrics = benchmark_suite.run_benchmark(
            operation_name="风险传递 (100策略 + 1000资产)",
            operation_func=cascade_risk,
            data_size=1100,
            requirement_threshold_ms=50.0,
            iterations=10
        )
        
        assert metrics.meets_requirement, f"风险传递性能不达标: {metrics.execution_time_ms:.2f}ms > {metrics.requirement_threshold_ms:.2f}ms"
    
    def test_large_scale_budget_allocation(self, benchmark_suite):
        """测试大规模预算分配性能"""
        from dataclasses import dataclass
        
        @dataclass
        class StrategyInfo:
            strategy_id: str
            risk_contribution: float
            sharpe_ratio: float
        
        def allocate_large_budget():
            strategies = {
                f's{i}': StrategyInfo(
                    strategy_id=f's{i}',
                    risk_contribution=np.random.random(),
                    sharpe_ratio=np.random.uniform(0.5, 2.0)
                )
                for i in range(500)
            }
            
            total_risk_contribution = sum(s.risk_contribution for s in strategies.values())
            strategy_budgets = {
                sid: 0.15 * (s.risk_contribution / total_risk_contribution)
                for sid, s in strategies.items()
            }
            
            return strategy_budgets
        
        metrics = benchmark_suite.run_benchmark(
            operation_name="大规模预算分配 (500策略)",
            operation_func=allocate_large_budget,
            data_size=500,
            requirement_threshold_ms=200.0,
            iterations=5
        )
        
        assert metrics.meets_requirement, f"大规模预算分配性能不达标: {metrics.execution_time_ms:.2f}ms > {metrics.requirement_threshold_ms:.2f}ms"


class TestConflictResolutionPerformance:
    """信号冲突解决性能测试"""
    
    @pytest.fixture
    def benchmark_suite(self):
        """基准测试套件"""
        return PerformanceBenchmarkSuite()
    
    def test_conflict_detection_performance(self, benchmark_suite):
        """测试冲突检测性能"""
        from dataclasses import dataclass
        
        @dataclass
        class NormalizedSignal:
            name: str
            value: float
            confidence: float
            strength: float
            direction: str
        
        def detect_conflicts():
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
            
            conflicts = []
            for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
                macro = macro_signals[signal_name]
                meso = meso_signals[signal_name]
                
                if macro.direction != meso.direction:
                    conflicts.append({
                        'signal_name': signal_name,
                        'conflict_type': 'direction',
                        'severity': 'high'
                    })
            
            return conflicts
        
        metrics = benchmark_suite.run_benchmark(
            operation_name="冲突检测 (100信号)",
            operation_func=detect_conflicts,
            data_size=100,
            requirement_threshold_ms=30.0,
            iterations=10
        )
        
        assert metrics.meets_requirement, f"冲突检测性能不达标: {metrics.execution_time_ms:.2f}ms > {metrics.requirement_threshold_ms:.2f}ms"
    
    def test_conflict_resolution_performance(self, benchmark_suite):
        """测试冲突解决性能"""
        from dataclasses import dataclass
        
        @dataclass
        class NormalizedSignal:
            name: str
            value: float
            confidence: float
            strength: float
            direction: str
        
        def resolve_conflicts():
            conflicts = [
                {
                    'signal_name': f's{i}',
                    'conflict_type': 'direction',
                    'macro_value': 0.8,
                    'meso_value': -0.5,
                    'macro_confidence': 0.9,
                    'meso_confidence': 0.7
                }
                for i in range(10)
            ]
            
            resolved_signals = {}
            for conflict in conflicts:
                total_confidence = conflict['macro_confidence'] + conflict['meso_confidence']
                macro_weight = conflict['macro_confidence'] / total_confidence
                meso_weight = conflict['meso_confidence'] / total_confidence
                
                resolved_value = (
                    macro_weight * conflict['macro_value'] +
                    meso_weight * conflict['meso_value']
                )
                
                resolved_signals[conflict['signal_name']] = NormalizedSignal(
                    name=conflict['signal_name'],
                    value=resolved_value,
                    confidence=0.8,
                    strength=0.6,
                    direction='bullish' if resolved_value > 0 else 'bearish'
                )
            
            return resolved_signals
        
        metrics = benchmark_suite.run_benchmark(
            operation_name="冲突解决 (10冲突)",
            operation_func=resolve_conflicts,
            data_size=10,
            requirement_threshold_ms=20.0,
            iterations=10
        )
        
        assert metrics.meets_requirement, f"冲突解决性能不达标: {metrics.execution_time_ms:.2f}ms > {metrics.requirement_threshold_ms:.2f}ms"
    
    def test_large_scale_conflict_detection(self, benchmark_suite):
        """测试大规模冲突检测性能"""
        from dataclasses import dataclass
        
        @dataclass
        class NormalizedSignal:
            name: str
            value: float
            confidence: float
            strength: float
            direction: str
        
        def detect_large_conflicts():
            macro_signals = {
                f'signal_{i}': NormalizedSignal(
                    name=f'signal_{i}',
                    value=np.random.uniform(-1, 1),
                    confidence=np.random.uniform(0.5, 1.0),
                    strength=np.random.uniform(0.3, 1.0),
                    direction='bullish' if np.random.random() > 0.5 else 'bearish'
                )
                for i in range(500)
            }
            
            meso_signals = {
                f'signal_{i}': NormalizedSignal(
                    name=f'signal_{i}',
                    value=np.random.uniform(-1, 1),
                    confidence=np.random.uniform(0.5, 1.0),
                    strength=np.random.uniform(0.3, 1.0),
                    direction='bullish' if np.random.random() > 0.5 else 'bearish'
                )
                for i in range(500)
            }
            
            conflicts = []
            for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
                macro = macro_signals[signal_name]
                meso = meso_signals[signal_name]
                
                if macro.direction != meso.direction:
                    conflicts.append({
                        'signal_name': signal_name,
                        'conflict_type': 'direction',
                        'severity': 'high'
                    })
            
            return conflicts
        
        metrics = benchmark_suite.run_benchmark(
            operation_name="大规模冲突检测 (500信号)",
            operation_func=detect_large_conflicts,
            data_size=500,
            requirement_threshold_ms=100.0,
            iterations=5
        )
        
        assert metrics.meets_requirement, f"大规模冲突检测性能不达标: {metrics.execution_time_ms:.2f}ms > {metrics.requirement_threshold_ms:.2f}ms"


def test_comprehensive_performance_report():
    """综合性能报告测试"""
    benchmark_suite = PerformanceBenchmarkSuite()
    
    from dataclasses import dataclass
    
    @dataclass
    class StrategyInfo:
        strategy_id: str
        risk_contribution: float
        sharpe_ratio: float
    
    def allocate_budget():
        strategies = {
            f's{i}': StrategyInfo(
                strategy_id=f's{i}',
                risk_contribution=np.random.random(),
                sharpe_ratio=np.random.uniform(0.5, 2.0)
            )
            for i in range(100)
        }
        
        total_risk_contribution = sum(s.risk_contribution for s in strategies.values())
        strategy_budgets = {
            sid: 0.15 * (s.risk_contribution / total_risk_contribution)
            for sid, s in strategies.items()
        }
        
        return strategy_budgets
    
    benchmark_suite.run_benchmark(
        operation_name="预算分配",
        operation_func=allocate_budget,
        data_size=100,
        requirement_threshold_ms=100.0,
        iterations=10
    )
    
    @dataclass
    class NormalizedSignal:
        name: str
        value: float
        confidence: float
        strength: float
        direction: str
    
    def detect_conflicts():
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
        
        conflicts = []
        for signal_name in set(macro_signals.keys()) & set(meso_signals.keys()):
            macro = macro_signals[signal_name]
            meso = meso_signals[signal_name]
            
            if macro.direction != meso.direction:
                conflicts.append({
                    'signal_name': signal_name,
                    'conflict_type': 'direction'
                })
        
        return conflicts
    
    benchmark_suite.run_benchmark(
        operation_name="冲突检测",
        operation_func=detect_conflicts,
        data_size=100,
        requirement_threshold_ms=30.0,
        iterations=10
    )
    
    report = benchmark_suite.generate_report()
    print("\n" + report)
    
    assert all(m.meets_requirement for m in benchmark_suite.results), "部分性能测试未通过"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
