"""
RealTimeRiskReporter - 实时风险监控报告器模块

模块ID: REALTIME_RISK_REPORTER_001
技术层次: Layer 7 - AI报告层 | 业务架构: 三级时间框架融合架构
版本: v1.0.0
创建日期: 2026-04-02

核心功能:
1. 实时风险指标监控（秒级更新）
2. VaR/CVaR实时计算
3. 希腊字母实时监控
4. 流动性风险实时监控
5. 风险预警与告警

参考模型: Bridgewater Real-Time Risk Monitoring, Renaissance Risk Dashboard
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import logging
import threading
import time
from queue import Queue
from scipy import stats


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """告警类型枚举"""
    VAR_BREACH = "var_breach"
    DRAWDOWN_WARNING = "drawdown_warning"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    CONCENTRATION_RISK = "concentration_risk"
    VOLATILITY_SPIKE = "volatility_spike"


@dataclass
class RiskMetric:
    """风险指标"""
    name: str
    value: float
    threshold: float
    risk_level: RiskLevel
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'value': self.value,
            'threshold': self.threshold,
            'risk_level': self.risk_level.value,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class RiskAlert:
    """风险告警"""
    alert_id: str
    alert_type: AlertType
    severity: RiskLevel
    message: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'alert_id': self.alert_id,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'message': self.message,
            'current_value': self.current_value,
            'threshold': self.threshold,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged
        }


@dataclass
class RealTimeRiskReport:
    """实时风险报告"""
    report_id: str
    timestamp: datetime
    
    portfolio_value: float
    daily_pnl: float
    daily_pnl_pct: float
    
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    
    max_drawdown: float
    current_drawdown: float
    
    volatility: float
    beta: float
    
    liquidity_score: float
    concentration_score: float
    
    risk_metrics: List[RiskMetric]
    active_alerts: List[RiskAlert]
    
    overall_risk_level: RiskLevel
    
    def to_dict(self) -> Dict:
        return {
            'report_id': self.report_id,
            'timestamp': self.timestamp.isoformat(),
            'portfolio_value': self.portfolio_value,
            'daily_pnl': self.daily_pnl,
            'daily_pnl_pct': self.daily_pnl_pct,
            'var_95': self.var_95,
            'var_99': self.var_99,
            'cvar_95': self.cvar_95,
            'cvar_99': self.cvar_99,
            'max_drawdown': self.max_drawdown,
            'current_drawdown': self.current_drawdown,
            'volatility': self.volatility,
            'beta': self.beta,
            'liquidity_score': self.liquidity_score,
            'concentration_score': self.concentration_score,
            'risk_metrics': [m.to_dict() for m in self.risk_metrics],
            'active_alerts': [a.to_dict() for a in self.active_alerts],
            'overall_risk_level': self.overall_risk_level.value
        }


class VaRCalculator:
    """VaR计算器"""
    
    def __init__(self, confidence_levels: List[float] = None):
        self.confidence_levels = confidence_levels or [0.95, 0.99]
        self.logger = logging.getLogger(__name__)
    
    def calculate_var(
        self,
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """计算VaR（历史模拟法）"""
        if len(returns) == 0:
            return 0.0
        
        var = np.percentile(returns, (1 - confidence_level) * 100)
        return abs(var)
    
    def calculate_cvar(
        self,
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """计算CVaR（条件风险价值）"""
        if len(returns) == 0:
            return 0.0
        
        var = self.calculate_var(returns, confidence_level)
        cvar = returns[returns <= -var].mean()
        return abs(cvar)
    
    def calculate_parametric_var(
        self,
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """计算参数化VaR（假设正态分布）"""
        if len(returns) == 0:
            return 0.0
        
        mean = returns.mean()
        std = returns.std()
        z_score = stats.norm.ppf(1 - confidence_level)
        
        var = -(mean + z_score * std)
        return abs(var)


class GreeksCalculator:
    """希腊字母计算器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_portfolio_greeks(
        self,
        portfolio: pd.DataFrame
    ) -> Dict[str, float]:
        """计算组合希腊字母"""
        greeks = {
            'delta': 0.0,
            'gamma': 0.0,
            'vega': 0.0,
            'theta': 0.0,
            'rho': 0.0
        }
        
        for idx, row in portfolio.iterrows():
            if 'delta' in row:
                greeks['delta'] += row['delta'] * row['value']
            if 'gamma' in row:
                greeks['gamma'] += row['gamma'] * row['value']
            if 'vega' in row:
                greeks['vega'] += row['vega'] * row['value']
            if 'theta' in row:
                greeks['theta'] += row['theta'] * row['value']
            if 'rho' in row:
                greeks['rho'] += row['rho'] * row['value']
        
        return greeks


class LiquidityMonitor:
    """流动性监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_liquidity_score(
        self,
        portfolio: pd.DataFrame
    ) -> float:
        """计算流动性评分（0-100）"""
        if portfolio.empty:
            return 100.0
        
        total_value = portfolio['value'].sum()
        if total_value == 0:
            return 100.0
        
        liquidity_scores = []
        for idx, row in portfolio.iterrows():
            asset_value = row['value']
            asset_type = row.get('asset_type', 'equity')
            
            if asset_type == 'currency':
                liquidity = 100
            elif asset_type == 'bond':
                liquidity = 80
            elif asset_type == 'equity':
                liquidity = 70
            elif asset_type == 'commodity':
                liquidity = 60
            else:
                liquidity = 50
            
            liquidity_scores.append(liquidity * (asset_value / total_value))
        
        return sum(liquidity_scores)
    
    def estimate_liquidation_cost(
        self,
        portfolio: pd.DataFrame,
        liquidation_days: int = 5
    ) -> float:
        """估算清算成本"""
        total_value = portfolio['value'].sum()
        liquidity_score = self.calculate_liquidity_score(portfolio)
        
        cost_rate = (100 - liquidity_score) / 100 * 0.05
        
        return total_value * cost_rate


class ConcentrationMonitor:
    """集中度监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_concentration_score(
        self,
        portfolio: pd.DataFrame
    ) -> float:
        """计算集中度评分（0-100，越高越分散）"""
        if portfolio.empty:
            return 100.0
        
        total_value = portfolio['value'].sum()
        if total_value == 0:
            return 100.0
        
        weights = portfolio['value'] / total_value
        herfindahl_index = (weights ** 2).sum()
        
        concentration_score = (1 - herfindahl_index) * 100
        
        return max(0, min(100, concentration_score))
    
    def get_top_holdings(
        self,
        portfolio: pd.DataFrame,
        top_n: int = 10
    ) -> pd.DataFrame:
        """获取前N大持仓"""
        return portfolio.nlargest(top_n, 'value')


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alerts: List[RiskAlert] = []
        self.alert_counter = 0
    
    def check_thresholds(
        self,
        metrics: Dict[str, RiskMetric]
    ) -> List[RiskAlert]:
        """检查阈值并生成告警"""
        new_alerts = []
        
        for metric_name, metric in metrics.items():
            if metric.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                alert = self._create_alert(metric)
                new_alerts.append(alert)
                self.alerts.append(alert)
        
        return new_alerts
    
    def _create_alert(self, metric: RiskMetric) -> RiskAlert:
        """创建告警"""
        self.alert_counter += 1
        
        alert_type_map = {
            'var_95': AlertType.VAR_BREACH,
            'var_99': AlertType.VAR_BREACH,
            'drawdown': AlertType.DRAWDOWN_WARNING,
            'liquidity': AlertType.LIQUIDITY_CRISIS,
            'concentration': AlertType.CONCENTRATION_RISK,
            'volatility': AlertType.VOLATILITY_SPIKE
        }
        
        return RiskAlert(
            alert_id=f"ALERT_{self.alert_counter:06d}",
            alert_type=alert_type_map.get(metric.name, AlertType.VAR_BREACH),
            severity=metric.risk_level,
            message=f"{metric.name} exceeded threshold: {metric.value:.2f} > {metric.threshold:.2f}",
            metric_name=metric.name,
            current_value=metric.value,
            threshold=metric.threshold
        )
    
    def get_active_alerts(self) -> List[RiskAlert]:
        """获取活跃告警"""
        return [alert for alert in self.alerts if not alert.acknowledged]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False


class RealTimeRiskReporter:
    """实时风险监控报告器主类"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化实时风险监控报告器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        self.var_calculator = VaRCalculator()
        self.greeks_calculator = GreeksCalculator()
        self.liquidity_monitor = LiquidityMonitor()
        self.concentration_monitor = ConcentrationMonitor()
        self.alert_manager = AlertManager()
        
        self.risk_thresholds = {
            'var_95': 0.05,
            'var_99': 0.08,
            'drawdown': 0.15,
            'liquidity': 50,
            'concentration': 40,
            'volatility': 0.30
        }
        
        self.report_counter = 0
    
    def generate_realtime_report(
        self,
        portfolio: pd.DataFrame,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None
    ) -> RealTimeRiskReport:
        """生成实时风险报告
        
        Args:
            portfolio: 投资组合数据
            returns: 收益率序列
            benchmark_returns: 基准收益率序列
            
        Returns:
            实时风险报告
        """
        self.report_counter += 1
        report_id = f"RISK_RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.report_counter:06d}"
        
        portfolio_value = portfolio['value'].sum()
        daily_pnl = returns.iloc[-1] * portfolio_value if len(returns) > 0 else 0
        daily_pnl_pct = returns.iloc[-1] if len(returns) > 0 else 0
        
        var_95 = self.var_calculator.calculate_var(returns, 0.95) * portfolio_value
        var_99 = self.var_calculator.calculate_var(returns, 0.99) * portfolio_value
        cvar_95 = self.var_calculator.calculate_cvar(returns, 0.95) * portfolio_value
        cvar_99 = self.var_calculator.calculate_cvar(returns, 0.99) * portfolio_value
        
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        current_drawdown = drawdown.iloc[-1] if len(drawdown) > 0 else 0
        
        volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0
        
        beta = self._calculate_beta(returns, benchmark_returns) if benchmark_returns is not None else 1.0
        
        liquidity_score = self.liquidity_monitor.calculate_liquidity_score(portfolio)
        concentration_score = self.concentration_monitor.calculate_concentration_score(portfolio)
        
        risk_metrics = self._calculate_risk_metrics(
            var_95=var_95 / portfolio_value,
            var_99=var_99 / portfolio_value,
            drawdown=abs(current_drawdown),
            volatility=volatility,
            liquidity=liquidity_score,
            concentration=concentration_score
        )
        
        new_alerts = self.alert_manager.check_thresholds(risk_metrics)
        active_alerts = self.alert_manager.get_active_alerts()
        
        overall_risk_level = self._determine_overall_risk_level(risk_metrics)
        
        return RealTimeRiskReport(
            report_id=report_id,
            timestamp=datetime.now(),
            portfolio_value=portfolio_value,
            daily_pnl=daily_pnl,
            daily_pnl_pct=daily_pnl_pct,
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            cvar_99=cvar_99,
            max_drawdown=max_drawdown,
            current_drawdown=current_drawdown,
            volatility=volatility,
            beta=beta,
            liquidity_score=liquidity_score,
            concentration_score=concentration_score,
            risk_metrics=list(risk_metrics.values()),
            active_alerts=active_alerts,
            overall_risk_level=overall_risk_level
        )
    
    def _calculate_beta(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> float:
        """计算Beta"""
        if len(returns) == 0 or len(benchmark_returns) == 0:
            return 1.0
        
        covariance = returns.cov(benchmark_returns)
        benchmark_variance = benchmark_returns.var()
        
        if benchmark_variance == 0:
            return 1.0
        
        return covariance / benchmark_variance
    
    def _calculate_risk_metrics(
        self,
        var_95: float,
        var_99: float,
        drawdown: float,
        volatility: float,
        liquidity: float,
        concentration: float
    ) -> Dict[str, RiskMetric]:
        """计算风险指标"""
        metrics = {}
        
        metrics['var_95'] = RiskMetric(
            name='var_95',
            value=var_95,
            threshold=self.risk_thresholds['var_95'],
            risk_level=self._get_risk_level(var_95, self.risk_thresholds['var_95'])
        )
        
        metrics['var_99'] = RiskMetric(
            name='var_99',
            value=var_99,
            threshold=self.risk_thresholds['var_99'],
            risk_level=self._get_risk_level(var_99, self.risk_thresholds['var_99'])
        )
        
        metrics['drawdown'] = RiskMetric(
            name='drawdown',
            value=drawdown,
            threshold=self.risk_thresholds['drawdown'],
            risk_level=self._get_risk_level(drawdown, self.risk_thresholds['drawdown'])
        )
        
        metrics['volatility'] = RiskMetric(
            name='volatility',
            value=volatility,
            threshold=self.risk_thresholds['volatility'],
            risk_level=self._get_risk_level(volatility, self.risk_thresholds['volatility'])
        )
        
        metrics['liquidity'] = RiskMetric(
            name='liquidity',
            value=liquidity,
            threshold=self.risk_thresholds['liquidity'],
            risk_level=self._get_risk_level(100 - liquidity, 100 - self.risk_thresholds['liquidity'])
        )
        
        metrics['concentration'] = RiskMetric(
            name='concentration',
            value=concentration,
            threshold=self.risk_thresholds['concentration'],
            risk_level=self._get_risk_level(100 - concentration, 100 - self.risk_thresholds['concentration'])
        )
        
        return metrics
    
    def _get_risk_level(self, value: float, threshold: float) -> RiskLevel:
        """获取风险等级"""
        if value < threshold * 0.5:
            return RiskLevel.LOW
        elif value < threshold:
            return RiskLevel.MEDIUM
        elif value < threshold * 1.5:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _determine_overall_risk_level(self, metrics: Dict[str, RiskMetric]) -> RiskLevel:
        """确定整体风险等级"""
        risk_levels = [metric.risk_level for metric in metrics.values()]
        
        if RiskLevel.CRITICAL in risk_levels:
            return RiskLevel.CRITICAL
        elif RiskLevel.HIGH in risk_levels:
            return RiskLevel.HIGH
        elif RiskLevel.MEDIUM in risk_levels:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def generate_realtime_report_markdown(
        self,
        report: RealTimeRiskReport
    ) -> str:
        """生成Markdown格式实时报告"""
        md = []
        md.append(f"# 实时风险监控报告")
        md.append(f"\n**报告ID**: {report.report_id}")
        md.append(f"\n**生成时间**: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        md.append(f"\n**整体风险等级**: {report.overall_risk_level.value.upper()}")
        
        md.append(f"\n## 组合概况")
        md.append(f"\n- 组合价值: ¥{report.portfolio_value:,.2f}")
        md.append(f"\n- 日度盈亏: ¥{report.daily_pnl:,.2f} ({report.daily_pnl_pct:.2%})")
        
        md.append(f"\n## 风险指标")
        md.append(f"\n| 指标 | 数值 | 阈值 | 风险等级 |")
        md.append(f"\n|-----|------|------|---------|")
        for metric in report.risk_metrics:
            md.append(f"\n| {metric.name} | {metric.value:.4f} | {metric.threshold:.4f} | {metric.risk_level.value} |")
        
        if report.active_alerts:
            md.append(f"\n## 活跃告警 ({len(report.active_alerts)})")
            for alert in report.active_alerts:
                md.append(f"\n- [{alert.severity.value.upper()}] {alert.message}")
        
        return "\n".join(md)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    reporter = RealTimeRiskReporter()
    
    portfolio_data = [
        {'asset_id': '600519.SH', 'asset_name': '贵州茅台', 'asset_type': 'equity', 'value': 800000, 'beta': 1.2},
        {'asset_id': '000858.SZ', 'asset_name': '五粮液', 'asset_type': 'equity', 'value': 600000, 'beta': 1.1},
        {'asset_id': '601318.SH', 'asset_name': '中国平安', 'asset_type': 'equity', 'value': 500000, 'beta': 1.3},
        {'asset_id': 'BOND_001', 'asset_name': '国债ETF', 'asset_type': 'bond', 'value': 400000, 'beta': 0.2},
    ]
    portfolio = pd.DataFrame(portfolio_data)
    
    np.random.seed(42)
    returns = pd.Series(np.random.randn(100) * 0.02)
    
    print(f"投资组合总价值: ¥{portfolio['value'].sum():,.2f}")
    
    report = reporter.generate_realtime_report(portfolio, returns)
    
    markdown_report = reporter.generate_realtime_report_markdown(report)
    print("\n" + markdown_report)
