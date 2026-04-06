---
module_id: EXEC_MONITORING_README_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
responsibility:
  - 数据质量
  - 因子计算
  - 交易执行
standard_type: 专业量化机构交易执行标准
applicable_scope: 交易执行与监�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?---


# 实时监控系统

> 策略状态、实时PnL、异常检�?

**版本**: v1.0
**更新**: 2026-03-29
**Layer**: Layer 5 (监控�?
**索引**: 04_EXECUTION/03_MONITORING

---

## 1. 监控概述

实时监控是AI自动报告的核心：

| 角色 | 职责 |
|------|------|
| **AI** | 自动监控、异常检测、报告生�?|
| **�?* | 监督、异常确�?|

---

## 2. 核心监控指标

### 2.1 策略状态监�?

```python
class StrategyMonitor:
    """策略运行状态监�?""

    def __init__(self):
        self.strategies = {}

    def update_status(self, strategy_id: str, status: dict) -> None:
        """更新策略状�?""
        self.strategies[strategy_id] = {
            'status': status.get('running', 'unknown'),
            'last_signal': status.get('last_signal_time'),
            'signal_count': status.get('signal_count', 0),
            'error_count': status.get('error_count', 0)
        }

    def get_health_score(self, strategy_id: str) -> float:
        """计算健康评分"""
        s = self.strategies.get(strategy_id, {})
        score = 1.0
        if s.get('error_count', 0) > 10:
            score *= 0.5
        if s.get('signal_count', 0) == 0:
            score *= 0.8
        return score
```

### 2.2 实时PnL追踪

```python
class RealTimePnLTracker:
    """实时盈亏追踪"""

    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.positions = {}
        self.realized_pnl = 0
        self.unrealized_pnl = 0

    def update_position(self, symbol: str, quantity: int,
                      avg_cost: float, current_price: float) -> None:
        """更新持仓"""
        self.positions[symbol] = {
            'quantity': quantity,
            'avg_cost': avg_cost,
            'current_price': current_price
        }
        self._calculate_pnl()

    def _calculate_pnl(self) -> None:
        """计算盈亏"""
        self.unrealized_pnl = sum(
            (p['current_price'] - p['avg_cost']) * p['quantity']
            for p in self.positions.values()
        )

    def get_total_pnl(self) -> dict:
        """获取总盈�?""
        total_pnl = self.realized_pnl + self.unrealized_pnl
        return {
            'realized': self.realized_pnl,
            'unrealized': self.unrealized_pnl,
            'total': total_pnl,
            'return_pct': total_pnl / self.initial_capital
        }
```

### 2.3 持仓汇�?

```python
class PositionSummary:
    """持仓汇�?""

    def generate_summary(self, positions: dict) -> dict:
        """生成持仓汇�?""
        total_value = sum(p['current_price'] * p['quantity']
                         for p in positions.values())
        total_cost = sum(p['avg_cost'] * p['quantity']
                        for p in positions.values())

        return {
            'total_positions': len(positions),
            'total_value': total_value,
            'total_cost': total_cost,
            'total_pnl': total_value - total_cost,
            'positions': [
                {
                    'symbol': symbol,
                    'quantity': p['quantity'],
                    'value': p['current_price'] * p['quantity'],
                    'pnl': (p['current_price'] - p['avg_cost']) * p['quantity'],
                    'pnl_pct': (p['current_price'] - p['avg_cost']) / p['avg_cost']
                }
                for symbol, p in positions.items()
            ]
        }
```

---

## 3. 异常检�?

### 3.1 价格异常

```python
class PriceAnomalyDetector:
    """价格异常检�?""

    def __init__(self, z_threshold: float = 3.0):
        self.z_threshold = z_threshold
        self.price_history = {}

    def detect(self, symbol: str, price: float) -> dict:
        """检测价格异�?""
        if symbol not in self.price_history:
            self.price_history[symbol] = []

        history = self.price_history[symbol]
        history.append(price)

        if len(history) < 20:
            return {'anomaly': False}

        mean = np.mean(history[:-1])
        std = np.std(history[:-1])
        z_score = (price - mean) / std if std > 0 else 0

        return {
            'anomaly': abs(z_score) > self.z_threshold,
            'z_score': z_score,
            'deviation_pct': (price - mean) / mean if mean > 0 else 0
        }
```

### 3.2 成交量异�?

```python
class VolumeAnomalyDetector:
    """成交量异常检�?""

    def __init__(self, volume_threshold: float = 5.0):
        self.volume_threshold = volume_threshold  # 超过平均5�?

    def detect(self, symbol: str, volume: int, avg_volume: float) -> dict:
        """检测成交量异常"""
        ratio = volume / avg_volume if avg_volume > 0 else 0

        return {
            'anomaly': ratio > self.volume_threshold,
            'volume_ratio': ratio,
            'volume': volume,
            'avg_volume': avg_volume
        }
```

### 3.3 信号异常

```python
class SignalAnomalyDetector:
    """信号异常检�?""

    def __init__(self):
        self.signal_history = {}

    def detect(self, strategy_id: str, signal: dict) -> dict:
        """检测信号异�?""
        if strategy_id not in self.signal_history:
            self.signal_history[strategy_id] = []

        history = self.signal_history[strategy_id]
        history.append(signal)

        # 检测信号频率异�?
        recent_signals = [s for s in history if
                         (datetime.now() - s['timestamp']).seconds < 300]
        frequency_anomaly = len(recent_signals) > 10

        # 检测信号方向突�?
        direction_anomaly = False
        if len(history) >= 2:
            last_direction = history[-2].get('direction')
            curr_direction = signal.get('direction')
            if last_direction != curr_direction:
                direction_anomaly = True

        return {
            'frequency_anomaly': frequency_anomaly,
            'direction_anomaly': direction_anomaly,
            'needs_review': frequency_anomaly or direction_anomaly
        }
```

---

## 4. 告警系统

```python
class AlertSystem:
    """告警系统"""

    ALERT_LEVELS = {
        'INFO': 1,
        'WARNING': 2,
        'CRITICAL': 3
    }

    def __init__(self, notification_service):
        self.notification_service = notification_service
        self.alert_rules = []

    def add_rule(self, condition: callable, level: str, message: str):
        """添加告警规则"""
        self.alert_rules.append({
            'condition': condition,
            'level': self.ALERT_LEVELS[level],
            'message': message
        })

    def check_and_alert(self, metrics: dict) -> List[Alert]:
        """检查并告警"""
        alerts = []
        for rule in self.alert_rules:
            if rule:
                alerts.append(Alert(
                    level=rule['level'],
                    message=rule['message'],
                    timestamp=datetime.now()
                ))
                self.notification_service.send(alerts[-1])
        return alerts
```

---

## 5. 层级关系

```
Layer 5 (监控�?
    �?上游
Layer 4 (执行�? �?订单执行
Layer 3 (策略�? �?策略信号
    �?下游
AI报告系统 �?自动报告生成
```

---

## 索引

- 父目�? [04_EXECUTION/README.md](../README.md)
- 相关: [PERFORMANCE_ATTRIBUTION.md](./PERFORMANCE_ATTRIBUTION.md)
