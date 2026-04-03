"""
StrategyLifecycleReporter - 策略生命周期报告器模块

模块ID: STRATEGY_LIFECYCLE_REPORTER_001
技术层次: Layer 7 - AI报告层 | 业务架构: 三级时间框架融合架构
版本: v1.0.0
创建日期: 2026-04-02

核心功能:
1. 策略生命周期追踪（萌芽期→成长期→成熟期→衰退期→退役）
2. 策略性能监控
3. 策略退役预警
4. 生命周期报告生成

参考模型: Bridgewater Strategy Lifecycle Management, Renaissance Strategy Retirement
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import logging


class StrategyPhase(Enum):
    """策略生命周期阶段"""
    EMERGING = "emging"      # 萌芽期
    GROWING = "growing"      # 成长期
    MATURE = "mature"        # 成熟期
    DECLINING = "declining"  # 衰退期
    RETIRED = "retired"      # 退役期


class StrategyStatus(Enum):
    """策略状态"""
    ACTIVE = "active"
    WARNING = "warning"
    CRITICAL = "critical"
    RETIRED = "retired"


@dataclass
class StrategyMetrics:
    """策略指标"""
    strategy_id: str
    strategy_name: str
    
    sharpe_ratio: float
    annual_return: float
    max_drawdown: float
    win_rate: float
    
    ic: float
    ic_ir: float
    
    trading_days: int
    total_trades: int
    
    current_phase: StrategyPhase
    status: StrategyStatus
    
    created_date: datetime
    last_updated: datetime
    
    def to_dict(self) -> Dict:
        return {
            'strategy_id': self.strategy_id,
            'strategy_name': self.strategy_name,
            'sharpe_ratio': self.sharpe_ratio,
            'annual_return': self.annual_return,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'ic': self.ic,
            'ic_ir': self.ic_ir,
            'trading_days': self.trading_days,
            'total_trades': self.total_trades,
            'current_phase': self.current_phase.value,
            'status': self.status.value,
            'created_date': self.created_date.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }


@dataclass
class LifecycleReport:
    """生命周期报告"""
    report_id: str
    timestamp: datetime
    
    active_strategies: List[StrategyMetrics]
    warning_strategies: List[StrategyMetrics]
    critical_strategies: List[StrategyMetrics]
    retired_strategies: List[StrategyMetrics]
    
    phase_distribution: Dict[str, int]
    performance_summary: Dict[str, float]
    
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'report_id': self.report_id,
            'timestamp': self.timestamp.isoformat(),
            'active_strategies': [s.to_dict() for s in self.active_strategies],
            'warning_strategies': [s.to_dict() for s in self.warning_strategies],
            'critical_strategies': [s.to_dict() for s in self.critical_strategies],
            'retired_strategies': [s.to_dict() for s in self.retired_strategies],
            'phase_distribution': self.phase_distribution,
            'performance_summary': self.performance_summary,
            'recommendations': self.recommendations
        }


class StrategyLifecycleManager:
    """策略生命周期管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.strategies: Dict[str, StrategyMetrics] = {}
    
    def determine_phase(self, metrics: StrategyMetrics) -> StrategyPhase:
        """确定策略生命周期阶段"""
        if metrics.trading_days < 30:
            return StrategyPhase.EMERGING
        elif metrics.trading_days < 180 and metrics.sharpe_ratio > 1.0:
            return StrategyPhase.GROWING
        elif metrics.sharpe_ratio > 1.5 and metrics.ic_ir > 1.0:
            return StrategyPhase.MATURE
        elif metrics.sharpe_ratio < 0.5 or metrics.ic < 0.02:
            return StrategyPhase.DECLINING
        else:
            return StrategyPhase.MATURE
    
    def determine_status(self, metrics: StrategyMetrics) -> StrategyStatus:
        """确定策略状态"""
        if metrics.sharpe_ratio < 0 or metrics.ic < 0:
            return StrategyStatus.CRITICAL
        elif metrics.sharpe_ratio < 0.5 or metrics.ic_ir < 0.5:
            return StrategyStatus.WARNING
        else:
            return StrategyStatus.ACTIVE
    
    def add_strategy(self, metrics: StrategyMetrics):
        """添加策略"""
        metrics.current_phase = self.determine_phase(metrics)
        metrics.status = self.determine_status(metrics)
        self.strategies[metrics.strategy_id] = metrics
    
    def update_strategy(self, strategy_id: str, updates: Dict):
        """更新策略"""
        if strategy_id in self.strategies:
            strategy = self.strategies[strategy_id]
            for key, value in updates.items():
                if hasattr(strategy, key):
                    setattr(strategy, key, value)
            
            strategy.current_phase = self.determine_phase(strategy)
            strategy.status = self.determine_status(strategy)
            strategy.last_updated = datetime.now()


class StrategyLifecycleReporter:
    """策略生命周期报告器主类"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.lifecycle_manager = StrategyLifecycleManager()
        self.report_counter = 0
    
    def generate_lifecycle_report(self) -> LifecycleReport:
        """生成生命周期报告"""
        self.report_counter += 1
        report_id = f"LIFECYCLE_RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.report_counter:06d}"
        
        strategies = list(self.lifecycle_manager.strategies.values())
        
        active = [s for s in strategies if s.status == StrategyStatus.ACTIVE]
        warning = [s for s in strategies if s.status == StrategyStatus.WARNING]
        critical = [s for s in strategies if s.status == StrategyStatus.CRITICAL]
        retired = [s for s in strategies if s.status == StrategyStatus.RETIRED]
        
        phase_dist = {}
        for phase in StrategyPhase:
            phase_dist[phase.value] = len([s for s in strategies if s.current_phase == phase])
        
        perf_summary = {
            'avg_sharpe': np.mean([s.sharpe_ratio for s in strategies]) if strategies else 0,
            'avg_return': np.mean([s.annual_return for s in strategies]) if strategies else 0,
            'avg_ic': np.mean([s.ic for s in strategies]) if strategies else 0,
            'total_strategies': len(strategies)
        }
        
        recommendations = self._generate_recommendations(active, warning, critical)
        
        return LifecycleReport(
            report_id=report_id,
            timestamp=datetime.now(),
            active_strategies=active,
            warning_strategies=warning,
            critical_strategies=critical,
            retired_strategies=retired,
            phase_distribution=phase_dist,
            performance_summary=perf_summary,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        active: List[StrategyMetrics],
        warning: List[StrategyMetrics],
        critical: List[StrategyMetrics]
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if critical:
            recommendations.append(f"🚨 {len(critical)}个策略处于临界状态，建议立即评估是否退役")
        
        if warning:
            recommendations.append(f"⚠️ {len(warning)}个策略处于警告状态，需要优化参数或降低权重")
        
        if len(active) < 5:
            recommendations.append("💡 活跃策略数量较少，建议开发新策略以分散风险")
        
        return recommendations
    
    def generate_report_markdown(self, report: LifecycleReport) -> str:
        """生成Markdown报告"""
        md = []
        md.append(f"# 策略生命周期报告")
        md.append(f"\n**报告ID**: {report.report_id}")
        md.append(f"\n**生成时间**: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        md.append(f"\n## 策略状态汇总")
        md.append(f"\n- ✅ 活跃策略: {len(report.active_strategies)}")
        md.append(f"\n- ⚠️ 警告策略: {len(report.warning_strategies)}")
        md.append(f"\n- 🚨 临界策略: {len(report.critical_strategies)}")
        md.append(f"\n- ⚰️ 退役策略: {len(report.retired_strategies)}")
        
        md.append(f"\n## 生命周期阶段分布")
        for phase, count in report.phase_distribution.items():
            md.append(f"\n- {phase}: {count}")
        
        md.append(f"\n## 性能摘要")
        md.append(f"\n- 平均夏普比率: {report.performance_summary['avg_sharpe']:.2f}")
        md.append(f"\n- 平均年化收益: {report.performance_summary['avg_return']:.2%}")
        md.append(f"\n- 平均IC: {report.performance_summary['avg_ic']:.4f}")
        
        if report.recommendations:
            md.append(f"\n## 建议")
            for rec in report.recommendations:
                md.append(f"\n- {rec}")
        
        return "\n".join(md)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    reporter = StrategyLifecycleReporter()
    
    strategy1 = StrategyMetrics(
        strategy_id="STRAT_001",
        strategy_name="价值策略",
        sharpe_ratio=1.8,
        annual_return=0.25,
        max_drawdown=0.15,
        win_rate=0.55,
        ic=0.05,
        ic_ir=1.5,
        trading_days=250,
        total_trades=120,
        current_phase=StrategyPhase.MATURE,
        status=StrategyStatus.ACTIVE,
        created_date=datetime.now() - timedelta(days=250),
        last_updated=datetime.now()
    )
    
    strategy2 = StrategyMetrics(
        strategy_id="STRAT_002",
        strategy_name="动量策略",
        sharpe_ratio=0.3,
        annual_return=0.08,
        max_drawdown=0.25,
        win_rate=0.48,
        ic=0.01,
        ic_ir=0.3,
        trading_days=180,
        total_trades=90,
        current_phase=StrategyPhase.DECLINING,
        status=StrategyStatus.WARNING,
        created_date=datetime.now() - timedelta(days=180),
        last_updated=datetime.now()
    )
    
    reporter.lifecycle_manager.add_strategy(strategy1)
    reporter.lifecycle_manager.add_strategy(strategy2)
    
    report = reporter.generate_lifecycle_report()
    
    markdown_report = reporter.generate_report_markdown(report)
    print(markdown_report)
