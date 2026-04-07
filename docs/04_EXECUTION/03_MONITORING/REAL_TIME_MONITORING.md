---
module_id: REAL_TIME_MONITORING
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 实时监控系统文档
---

﻿---
module_id: EXEC_REAL_TIME_MONITORING_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 交易执行系统设计与优化与实施指导
standard_type: 专业量化机构交易执行标准
applicable_scope: 交易执行与监?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
---


# 实时监控系统
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 策略运行状态、性能追踪、异常检?

---

## 1. 实时监控架构

```
实时监控系统
├── 策略状态监?
?  ├── 运行状?
?  ├── 信号生成
?  ├── 订单执行
?  └── 持仓变化
├── 性能追踪
?  ├── 实时PnL
?  ├── 持仓市?
?  ├── 风险指标
?  └── 换手?
├── 异常检?
?  ├── 价格异动
?  ├── 流动性枯?
?  ├── 信号异常
?  └── 风控触发
└── 告警推?
    ├── 即时通知
    ├── 定期报告
    └── 异常汇?
```

---

## 2. 策略状态监?

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class StrategyState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class StrategyStatus:
    """策略状?""
    strategy_id: str
    strategy_name: str
    state: StrategyState
    start_time: datetime
    last_signal_time: datetime
    last_order_time: datetime
    position_count: int
    daily_pnl: float
    total_pnl: float
    metrics: Dict = field(default_factory=dict)

class StrategyMonitor:
    """策略状态监控器"""

    def __init__(self):
        self.strategies: Dict[str, StrategyStatus] = {}
        self.state_history: Dict[str, List] = {}

    def register_strategy(
        self,
        strategy_id: str,
        strategy_name: str
    ):
        """注册策略"""
        status = StrategyStatus(
            strategy_id=strategy_id,
            strategy_name=strategy_name,
            state=StrategyState.INITIALIZING,
            start_time=datetime.now(),
            last_signal_time=None,
            last_order_time=None,
            position_count=0,
            daily_pnl=0.0,
            total_pnl=0.0
        )
        self.strategies[strategy_id] = status
        self.state_history[strategy_id] = []

    def update_status(
        self,
        strategy_id: str,
        state: StrategyState = None,
        last_signal_time: datetime = None,
        last_order_time: datetime = None,
        position_count: int = None,
        daily_pnl: float = None,
        metrics: Dict = None
    ):
        """更新策略状?""
        if strategy_id not in self.strategies:
            return

        status = self.strategies[strategy_id]

        if state is not None and state != status.state:
            status.state = state
            self._record_state_change(strategy_id, state)

        if last_signal_time is not None:
            status.last_signal_time = last_signal_time
        if last_order_time is not None:
            status.last_order_time = last_order_time
        if position_count is not None:
            status.position_count = position_count
        if daily_pnl is not None:
            status.daily_pnl = daily_pnl
        if metrics is not None:
            status.metrics.update(metrics)

    def _record_state_change(self, strategy_id: str, new_state: StrategyState):
        """记录状态变?""
        self.state_history[strategy_id].append({
            'state': new_state,
            'timestamp': datetime.now()
        })

    def get_strategy_status(self, strategy_id: str) -> Optional[StrategyStatus]:
        """获取策略状?""
        return self.strategies.get(strategy_id)

    def get_all_strategies_status(self) -> List[StrategyStatus]:
        """获取所有策略状?""
        return list(self.strategies.values())

    def check_stale_strategies(self, threshold_minutes: int = 30) -> List[Dict]:
        """检查停滞策?""
        now = datetime.now()
        stale = []

        for strategy_id, status in self.strategies.items():
            if status.state != StrategyState.RUNNING:
                continue

            if status.last_signal_time:
                minutes_since_signal = (now - status.last_signal_time).total_seconds() / 60
                if minutes_since_signal > threshold_minutes:
                    stale.append({
                        'strategy_id': strategy_id,
                        'strategy_name': status.strategy_name,
                        'last_signal': status.last_signal_time,
                        'minutes_since': minutes_since_signal
                    })

        return stale
```

---

## 3. 性能实时追踪

```python
class PerformanceTracker:
    """性能实时追踪"""

    def __init__(self):
        self.daily_metrics: Dict[str, List] = {}
        self.realtimePnL: float = 0.0
        self.positions: Dict[str, Dict] = {}

    def update_positions(self, positions: Dict[str, Dict]):
        """更新持仓"""
        self.positions = positions

    def update_pnl(self, pnl_data: Dict):
        """更新PnL"""
        self.realtimePnL = pnl_data.get('daily_pnl', 0.0)
        self.daily_pnl_history.append({
            'timestamp': datetime.now(),
            'pnl': self.realtimePnL
        })

    def calculate_realtime_metrics(self) -> Dict:
        """计算实时指标"""
        total_value = sum(
            pos['quantity'] * pos['current_price']
            for pos in self.positions.values()
        )
        total_cost = sum(
            pos['quantity'] * pos['avg_cost']
            for pos in self.positions.values()
        )

        unrealized_pnl = total_value - total_cost
        pnl_rate = unrealized_pnl / total_cost if total_cost > 0 else 0

        # 换手率（今日交易?总市值）
        today_turnover = sum(
            pos.get('today_traded_value', 0)
            for pos in self.positions.values()
        )
        turnover_rate = today_turnover / total_value if total_value > 0 else 0

        return {
            'total_market_value': total_value,
            'total_cost': total_cost,
            'unrealized_pnl': unrealized_pnl,
            'pnl_rate': pnl_rate,
            'position_count': len(self.positions),
            'today_turnover': today_turnover,
            'turnover_rate': turnover_rate,
            'cash': self.cash,
            'total_assets': total_value + self.cash
        }

    def get_position_summary(self) -> pd.DataFrame:
        """获取持仓汇?""
        if not self.positions:
            return pd.DataFrame()

        data = []
        for symbol, pos in self.positions.items():
            data.append({
                'symbol': symbol,
                'quantity': pos['quantity'],
                'avg_cost': pos['avg_cost'],
                'current_price': pos['current_price'],
                'market_value': pos['quantity'] * pos['current_price'],
                'unrealized_pnl': (pos['current_price'] - pos['avg_cost']) * pos['quantity'],
                'pnl_rate': (pos['current_price'] - pos['avg_cost']) / pos['avg_cost']
            })

        return pd.DataFrame(data)
```

---

## 4. 异常检?

```python
class AnomalyDetector:
    """异常检测器"""

    def __init__(self):
        self.baseline_stats: Dict = {}
        self.alert_callbacks: List = []

    def register_baseline(
        self,
        symbol: str,
        mean_price: float,
        std_price: float,
        avg_volume: float,
        std_volume: float
    ):
        """注册基准统计"""
        self.baseline_stats[symbol] = {
            'price_mean': mean_price,
            'price_std': std_price,
            'volume_mean': avg_volume,
            'volume_std': std_volume
        }

    def detect_price_anomaly(
        self,
        symbol: str,
        current_price: float,
        window: int = 20
    ) -> Optional[Dict]:
        """检测价格异?""
        if symbol not in self.baseline_stats:
            return None

        baseline = self.baseline_stats[symbol]
        z_score = (current_price - baseline['price_mean']) / baseline['price_std']

        if abs(z_score) > 3:  # 3个标准差
            return {
                'type': 'price_anomaly',
                'symbol': symbol,
                'current_price': current_price,
                'z_score': z_score,
                'severity': 'critical' if abs(z_score) > 4 else 'warning',
                'message': f"{symbol} 价格异常波动 (Z={z_score:.2f})"
            }

        return None

    def detect_volume_anomaly(
        self,
        symbol: str,
        current_volume: float
    ) -> Optional[Dict]:
        """检测成交量异常"""
        if symbol not in self.baseline_stats:
            return None

        baseline = self.baseline_stats[symbol]
        volume_ratio = current_volume / baseline['volume_mean']

        if volume_ratio > 5:  # 成交量放??
            return {
                'type': 'volume_anomaly',
                'symbol': symbol,
                'current_volume': current_volume,
                'volume_ratio': volume_ratio,
                'severity': 'critical' if volume_ratio > 10 else 'warning',
                'message': f"{symbol} 成交量异常放?({volume_ratio:.1f}x)"
            }

        return None

    def detect_signal_anomaly(
        self,
        signals: List[Dict],
        threshold: int = 20
    ) -> Optional[Dict]:
        """检测信号异常（信号过于集中?""
        if len(signals) > threshold:
            return {
                'type': 'signal_flood',
                'signal_count': len(signals),
                'severity': 'warning',
                'message': f"信号过于集中 ({len(signals)} 个信?"
            }
        return None

    def detect_drawdown_anomaly(
        self,
        current_drawdown: float,
        max_acceptable_drawdown: float = 0.15
    ) -> Optional[Dict]:
        """检测回撤异?""
        if current_drawdown < -max_acceptable_drawdown:
            return {
                'type': 'drawdown_alert',
                'current_drawdown': current_drawdown,
                'threshold': -max_acceptable_drawdown,
                'severity': 'critical',
                'message': f"回撤超限 ({current_drawdown:.2%})"
            }
        return None
```

---

## 5. 监控面板

```python
class MonitoringDashboard:
    """监控面板数据生成"""

    def __init__(self, strategy_monitor: StrategyMonitor,
                 performance_tracker: PerformanceTracker,
                 anomaly_detector: AnomalyDetector):
        self.strategy_monitor = strategy_monitor
        self.performance_tracker = performance_tracker
        self.anomaly_detector = anomaly_detector

    def generate_dashboard_data(self) -> Dict:
        """生成监控面板数据"""
        # 策略状?
        strategies = self.strategy_monitor.get_all_strategies_status()
        strategy_summary = {
            'total': len(strategies),
            'running': sum(1 for s in strategies if s.state == StrategyState.RUNNING),
            'paused': sum(1 for s in strategies if s.state == StrategyState.PAUSED),
            'error': sum(1 for s in strategies if s.state == StrategyState.ERROR)
        }

        # 性能指标
        perf_metrics = self.performance_tracker.calculate_realtime_metrics()

        # 持仓汇?
        positions_df = self.performance_tracker.get_position_summary()

        # 活跃告警
        active_alerts = self._get_active_alerts()

        return {
            'timestamp': datetime.now().isoformat(),
            'strategies': strategy_summary,
            'performance': perf_metrics,
            'positions': positions_df.to_dict('records') if not positions_df.empty else [],
            'alerts': active_alerts,
            'system_health': self._get_system_health()
        }

    def _get_system_health(self) -> Dict:
        """获取系统健康?""
        import psutil

        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'status': 'healthy' if psutil.cpu_percent() < 80 else 'degraded'
        }

    def _get_active_alerts(self) -> List[Dict]:
        """获取活跃告警"""
        # 从告警管理器获取
        return []
```

---

## 6. 监控配置

```yaml
# config/realtime_monitoring.yaml
monitoring:
  realtime:
    enabled: true
    update_interval_seconds: 5

  strategies:
    stale_threshold_minutes: 30
    max_simultaneous_signals: 20

  risk:
    max_drawdown: 0.15
    max_position_loss: 0.08

  anomaly_detection:
    price_z_score_threshold: 3
    volume_ratio_threshold: 5
    signal_count_threshold: 20

  alerts:
    realtime:
      - channel: "dingtalk"
        events: ["strategy_error", "drawdown_alert", "system_critical"]
      - channel: "log"
        events: ["all"]

    periodic:
      - schedule: "17:00"
        report: "daily_summary"
        channel: "email"
```

---

## 7. 监控指标速查

| 类别 | 指标 | 正常范围 | 告警条件 |
|------|------|---------|---------|
| 策略 | 运行状?| RUNNING | ERROR, STOPPED |
| 策略 | 信号频率 | 0-10/分钟 | > 20/分钟 |
| 策略 | 无信号时?| < 30分钟 | > 60分钟 |
| 持仓 | 单股持仓 | < 20% | > 25% |
| 持仓 | 总仓?| 0-90% | > 95% |
| PnL | 日盈?| 10% | < -15% |
| PnL | 回撤 | > -10% | < -15% |
| 系统 | CPU | < 70% | > 85% |
| 系统 | 内存 | < 80% | > 90% |

---

**版本**: 1.0 | **更新**: 2026-03-28
