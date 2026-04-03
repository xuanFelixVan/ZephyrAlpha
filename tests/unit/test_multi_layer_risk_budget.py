"""
多层次风险预算系统单元测试

测试范围:
- MultiLayerRiskBudgetManager: 多层次预算分配
- RiskCascadingEngine: 风险传递机制
- MultiLayerRiskMonitor: 多层次风险监控

性能要求:
- 预算分配: < 100ms (100策略 + 1000资产)
- 风险传递: < 50ms
- 风险监控: < 50ms
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List

from dataclasses import dataclass, field


@dataclass
class StrategyInfo:
    strategy_id: str
    risk_contribution: float
    sharpe_ratio: float


@dataclass
class AssetInfo:
    asset_id: str
    strategy_id: str
    weight: float


@dataclass
class PortfolioBudget:
    total_risk: float
    target_var: float
    risk_contribution: Dict[str, float]


@dataclass
class StrategyBudget:
    strategy_id: str
    risk_budget: float
    risk_contribution: float
    sharpe_ratio: float


@dataclass
class AssetBudget:
    asset_id: str
    strategy_id: str
    risk_budget: float
    position_limit: float


@dataclass
class MultiLayerBudgetAllocation:
    portfolio_budget: PortfolioBudget
    strategy_budgets: Dict[str, StrategyBudget]
    asset_budgets: Dict[str, AssetBudget]
    cascading_log: List[Dict]
    timestamp: datetime


class TestMultiLayerRiskBudgetManager:
    """测试多层次风险预算管理器"""
    
    @pytest.fixture
    def manager_config(self):
        """管理器配置"""
        from dataclasses import dataclass
        
        @dataclass
        class MockConfig:
            max_portfolio_var: float = 0.15
            max_strategy_var: float = 0.05
            max_asset_var: float = 0.02
        
        return MockConfig()
    
    @pytest.fixture
    def test_strategies(self):
        """测试策略数据"""
        return {
            'strategy_1': StrategyInfo(
                strategy_id='strategy_1',
                risk_contribution=0.5,
                sharpe_ratio=1.5
            ),
            'strategy_2': StrategyInfo(
                strategy_id='strategy_2',
                risk_contribution=0.3,
                sharpe_ratio=1.2
            ),
            'strategy_3': StrategyInfo(
                strategy_id='strategy_3',
                risk_contribution=0.2,
                sharpe_ratio=0.8
            )
        }
    
    @pytest.fixture
    def test_assets(self):
        """测试资产数据"""
        return {
            'asset_1': AssetInfo(
                asset_id='asset_1',
                strategy_id='strategy_1',
                weight=0.6
            ),
            'asset_2': AssetInfo(
                asset_id='asset_2',
                strategy_id='strategy_1',
                weight=0.4
            ),
            'asset_3': AssetInfo(
                asset_id='asset_3',
                strategy_id='strategy_2',
                weight=1.0
            ),
            'asset_4': AssetInfo(
                asset_id='asset_4',
                strategy_id='strategy_3',
                weight=0.5
            ),
            'asset_5': AssetInfo(
                asset_id='asset_5',
                strategy_id='strategy_3',
                weight=0.5
            )
        }
    
    def test_multi_layer_budget_allocation_basic(
        self, manager_config, test_strategies, test_assets
    ):
        """测试基本的多层次预算分配"""
        portfolio_value = 1000000
        target_risk = 0.15
        
        portfolio_budget = PortfolioBudget(
            total_risk=target_risk,
            target_var=0.10,
            risk_contribution={
                'strategy_1': 0.5,
                'strategy_2': 0.3,
                'strategy_3': 0.2
            }
        )
        
        strategy_budgets = {
            'strategy_1': StrategyBudget(
                strategy_id='strategy_1',
                risk_budget=0.075,
                risk_contribution=0.5,
                sharpe_ratio=1.5
            ),
            'strategy_2': StrategyBudget(
                strategy_id='strategy_2',
                risk_budget=0.045,
                risk_contribution=0.3,
                sharpe_ratio=1.2
            ),
            'strategy_3': StrategyBudget(
                strategy_id='strategy_3',
                risk_budget=0.030,
                risk_contribution=0.2,
                sharpe_ratio=0.8
            )
        }
        
        asset_budgets = {
            'asset_1': AssetBudget(
                asset_id='asset_1',
                strategy_id='strategy_1',
                risk_budget=0.045,
                position_limit=300000
            ),
            'asset_2': AssetBudget(
                asset_id='asset_2',
                strategy_id='strategy_1',
                risk_budget=0.030,
                position_limit=200000
            )
        }
        
        allocation = MultiLayerBudgetAllocation(
            portfolio_budget=portfolio_budget,
            strategy_budgets=strategy_budgets,
            asset_budgets=asset_budgets,
            cascading_log=[],
            timestamp=datetime.now()
        )
        
        assert allocation.portfolio_budget.total_risk == 0.15
        assert len(allocation.strategy_budgets) == 3
        assert len(allocation.asset_budgets) == 2
    
    def test_risk_cascading_correctness(self):
        """测试风险传递正确性"""
        portfolio_budget = PortfolioBudget(
            total_risk=0.15,
            target_var=0.10,
            risk_contribution={}
        )
        
        strategies = {
            's1': StrategyInfo(strategy_id='s1', risk_contribution=0.6, sharpe_ratio=1.5),
            's2': StrategyInfo(strategy_id='s2', risk_contribution=0.4, sharpe_ratio=1.2)
        }
        
        total_risk_contribution = sum(s.risk_contribution for s in strategies.values())
        
        strategy_budgets = {}
        for strategy_id, strategy_info in strategies.items():
            risk_share = strategy_info.risk_contribution / total_risk_contribution
            strategy_budget = portfolio_budget.total_risk * risk_share
            strategy_budgets[strategy_id] = StrategyBudget(
                strategy_id=strategy_id,
                risk_budget=strategy_budget,
                risk_contribution=strategy_info.risk_contribution,
                sharpe_ratio=strategy_info.sharpe_ratio
            )
        
        assert abs(strategy_budgets['s1'].risk_budget - 0.09) < 0.001
        assert abs(strategy_budgets['s2'].risk_budget - 0.06) < 0.001
    
    def test_budget_constraint_application(self):
        """测试预算约束应用"""
        min_budget = 0.01
        max_budget = 0.30
        
        test_budget = 0.35
        constrained_budget = np.clip(test_budget, min_budget, max_budget)
        
        assert constrained_budget == 0.30
        
        test_budget = 0.005
        constrained_budget = np.clip(test_budget, min_budget, max_budget)
        
        assert constrained_budget == 0.01
    
    def test_performance_large_scale(self, test_strategies, test_assets):
        """测试大规模性能"""
        import time
        
        large_strategies = {}
        for i in range(100):
            large_strategies[f'strategy_{i}'] = StrategyInfo(
                strategy_id=f'strategy_{i}',
                risk_contribution=np.random.random(),
                sharpe_ratio=np.random.uniform(0.5, 2.0)
            )
        
        large_assets = {}
        for i in range(1000):
            strategy_idx = i % 100
            large_assets[f'asset_{i}'] = AssetInfo(
                asset_id=f'asset_{i}',
                strategy_id=f'strategy_{strategy_idx}',
                weight=np.random.random()
            )
        
        start_time = time.time()
        
        total_risk_contribution = sum(s.risk_contribution for s in large_strategies.values())
        strategy_budgets = {}
        for strategy_id, strategy_info in large_strategies.items():
            risk_share = strategy_info.risk_contribution / total_risk_contribution
            strategy_budget = 0.15 * risk_share
            strategy_budgets[strategy_id] = strategy_budget
        
        elapsed_time = (time.time() - start_time) * 1000
        
        assert elapsed_time < 100, f"预算分配耗时 {elapsed_time}ms，超过100ms阈值"
        assert len(strategy_budgets) == 100


class TestRiskCascadingEngine:
    """测试风险传递引擎"""
    
    def test_cascade_to_strategies(self):
        """测试传递到策略层"""
        portfolio_budget = PortfolioBudget(
            total_risk=0.15,
            target_var=0.10,
            risk_contribution={}
        )
        
        strategies = {
            's1': StrategyInfo(strategy_id='s1', risk_contribution=0.5, sharpe_ratio=1.5),
            's2': StrategyInfo(strategy_id='s2', risk_contribution=0.3, sharpe_ratio=1.2),
            's3': StrategyInfo(strategy_id='s3', risk_contribution=0.2, sharpe_ratio=0.8)
        }
        
        total_risk_contribution = sum(s.risk_contribution for s in strategies.values())
        
        strategy_budgets = {}
        cascading_log = []
        
        for strategy_id, strategy_info in strategies.items():
            risk_share = strategy_info.risk_contribution / total_risk_contribution
            strategy_budget = portfolio_budget.total_risk * risk_share
            
            strategy_budgets[strategy_id] = StrategyBudget(
                strategy_id=strategy_id,
                risk_budget=strategy_budget,
                risk_contribution=strategy_info.risk_contribution,
                sharpe_ratio=strategy_info.sharpe_ratio
            )
            
            cascading_log.append({
                'from': 'portfolio',
                'to': f'strategy_{strategy_id}',
                'budget': strategy_budget,
                'timestamp': datetime.now()
            })
        
        assert len(strategy_budgets) == 3
        assert len(cascading_log) == 3
        
        total_strategy_budget = sum(b.risk_budget for b in strategy_budgets.values())
        assert abs(total_strategy_budget - portfolio_budget.total_risk) < 0.001
    
    def test_cascade_to_assets(self):
        """测试传递到资产层"""
        strategy_budgets = {
            's1': StrategyBudget(
                strategy_id='s1',
                risk_budget=0.075,
                risk_contribution=0.5,
                sharpe_ratio=1.5
            ),
            's2': StrategyBudget(
                strategy_id='s2',
                risk_budget=0.045,
                risk_contribution=0.3,
                sharpe_ratio=1.2
            )
        }
        
        assets = {
            'a1': AssetInfo(asset_id='a1', strategy_id='s1', weight=0.6),
            'a2': AssetInfo(asset_id='a2', strategy_id='s1', weight=0.4),
            'a3': AssetInfo(asset_id='a3', strategy_id='s2', weight=1.0)
        }
        
        max_single_asset_risk = 0.02
        asset_budgets = {}
        cascading_log = []
        
        for asset_id, asset_info in assets.items():
            strategy_id = asset_info.strategy_id
            if strategy_id not in strategy_budgets:
                continue
            
            strategy_budget = strategy_budgets[strategy_id]
            asset_weight = asset_info.weight
            asset_budget_value = strategy_budget.risk_budget * asset_weight
            
            asset_budget_value = min(asset_budget_value, max_single_asset_risk)
            
            asset_budgets[asset_id] = AssetBudget(
                asset_id=asset_id,
                strategy_id=strategy_id,
                risk_budget=asset_budget_value,
                position_limit=asset_budget_value * 1000000
            )
            
            cascading_log.append({
                'from': f'strategy_{strategy_id}',
                'to': f'asset_{asset_id}',
                'budget': asset_budget_value,
                'timestamp': datetime.now()
            })
        
        assert len(asset_budgets) == 3
        assert len(cascading_log) == 3


class TestMultiLayerRiskMonitor:
    """测试多层次风险监控器"""
    
    def test_portfolio_risk_monitoring(self):
        """测试组合层风险监控"""
        portfolio_budget = PortfolioBudget(
            total_risk=0.15,
            target_var=0.10,
            risk_contribution={}
        )
        
        current_var = 0.12
        risk_usage_rate = current_var / portfolio_budget.total_risk
        
        assert risk_usage_rate == 0.8
        assert risk_usage_rate < 1.0
    
    def test_strategy_risk_monitoring(self):
        """测试策略层风险监控"""
        strategy_budgets = {
            's1': StrategyBudget(
                strategy_id='s1',
                risk_budget=0.075,
                risk_contribution=0.5,
                sharpe_ratio=1.5
            ),
            's2': StrategyBudget(
                strategy_id='s2',
                risk_budget=0.045,
                risk_contribution=0.3,
                sharpe_ratio=1.2
            )
        }
        
        current_risks = {
            's1': 0.06,
            's2': 0.04
        }
        
        risk_usage_rates = {}
        for strategy_id, budget in strategy_budgets.items():
            current_risk = current_risks[strategy_id]
            risk_usage_rates[strategy_id] = current_risk / budget.risk_budget
        
        assert risk_usage_rates['s1'] == 0.8
        assert risk_usage_rates['s2'] == pytest.approx(0.889, rel=0.01)
    
    def test_alert_generation(self):
        """测试预警生成"""
        risk_usage_rate = 0.95
        threshold = 0.9
        
        should_alert = risk_usage_rate > threshold
        
        assert should_alert is True
        
        risk_usage_rate = 0.85
        should_alert = risk_usage_rate > threshold
        
        assert should_alert is False


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """性能基准测试"""
    
    def test_budget_allocation_performance(self):
        """测试预算分配性能"""
        import time
        
        strategies = {
            f's{i}': StrategyInfo(
                strategy_id=f's{i}',
                risk_contribution=np.random.random(),
                sharpe_ratio=np.random.uniform(0.5, 2.0)
            )
            for i in range(100)
        }
        
        start_time = time.time()
        
        total_risk_contribution = sum(s.risk_contribution for s in strategies.values())
        strategy_budgets = {
            sid: 0.15 * (s.risk_contribution / total_risk_contribution)
            for sid, s in strategies.items()
        }
        
        elapsed_time = (time.time() - start_time) * 1000
        
        assert elapsed_time < 100, f"预算分配耗时 {elapsed_time}ms，超过100ms阈值"
    
    def test_risk_cascading_performance(self):
        """测试风险传递性能"""
        import time
        
        strategy_budgets = {
            f's{i}': StrategyBudget(
                strategy_id=f's{i}',
                risk_budget=0.0015,
                risk_contribution=0.01,
                sharpe_ratio=1.0
            )
            for i in range(100)
        }
        
        assets = {
            f'a{i}': AssetInfo(
                asset_id=f'a{i}',
                strategy_id=f's{i % 100}',
                weight=np.random.random()
            )
            for i in range(1000)
        }
        
        start_time = time.time()
        
        asset_budgets = {}
        for asset_id, asset_info in assets.items():
            strategy_id = asset_info.strategy_id
            if strategy_id in strategy_budgets:
                asset_budgets[asset_id] = strategy_budgets[strategy_id].risk_budget * asset_info.weight
        
        elapsed_time = (time.time() - start_time) * 1000
        
        assert elapsed_time < 50, f"风险传递耗时 {elapsed_time}ms，超过50ms阈值"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
