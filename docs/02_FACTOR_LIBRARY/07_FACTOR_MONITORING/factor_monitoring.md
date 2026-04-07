---
module_id: FACTOR_MONITORING_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
responsibility:
  - 因子计算、因子库管理
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
---
---



# 因子监控
> **核心职责**: 因子监控系统和预警机制，涉及因子监控
> **职责边界**: 
> - ✅ 本文档负责：因子监控系统和预警机制相关内容
> - ❌ 本文档不负责：具体实现细节、其他模块内容


> 因子IC监控、衰减预警、生命周期管�?
>
> **版本**: v1.0
> **更新**: 2026-03-28
> **优先�?*: P1 - 核心模块
> **Layer**: Layer 2 (因子�?
> **索引**: F.05.MON.001

---

## 1. 概述

因子监控是确保因子长期有效性的关键系统，包括：
- IC实时监控
- 衰减预警
- 生命周期管理
- 告警通知

---

## 2. IC监控面板

### 2.1 IC监控系统

```python
import pandas as pd
import numpy as np
from datetime import datetime

class FactorICMonitor:
    """因子IC监控系统"""

    def __init__(self, thresholds: dict = None):
        """
        thresholds: IC告警阈值配�?
        """
        self.thresholds = thresholds or {
            'ic_ir_excellent': 1.0,
            'ic_ir_good': 0.5,
            'ic_ir_warning': 0.3,
            'ic_ir_critical': 0.0,
            'ic_win_rate_warning': 0.50,
            'ic_win_rate_critical': 0.45
        }

    def calculate_metrics(
        self,
        ic_series: pd.Series,
        window: int = 20
    ) -> dict:
        """
        计算IC指标

        Parameters:
        -----------
        ic_series : pd.Series
            IC时间序列
        window : int
            滚动窗口大小

        Returns:
        --------
        dict: IC指标
        """
        # 滚动IC统计
        rolling_ic = ic_series.rolling(window)

        metrics = {
            'current_ic': ic_series.iloc[-1],
            'ic_mean': ic_series.mean(),
            'ic_std': ic_series.std(),
            'ic_ir': ic_series.mean() / ic_series.std() if ic_series.std() > 0 else 0,
            'ic_win_rate': (ic_series > 0).mean(),
            'rolling_ic_mean': rolling_ic.mean().iloc[-1],
            'rolling_ic_std': rolling_ic.std().iloc[-1],
            'rolling_ic_ir': rolling_ic.mean().iloc[-1] / rolling_ic.std().iloc[-1] if rolling_ic.std().iloc[-1] > 0 else 0,
            'recent_ic_mean': ic_series.tail(window).mean(),
            'recent_ic_ir': ic_series.tail(window).mean() / ic_series.tail(window).std() if ic_series.tail(window).std() > 0 else 0
        }

        return metrics

    def evaluate_status(self, metrics: dict) -> dict:
        """
        评估因子状�?

        Returns:
        --------
        dict: {status: str, alerts: list}
        """
        status = 'NORMAL'
        alerts = []

        # IC_IR评估
        if metrics['ic_ir'] >= self.thresholds['ic_ir_excellent']:
            status = 'EXCELLENT'
        elif metrics['ic_ir'] >= self.thresholds['ic_ir_good']:
            status = 'GOOD'
        elif metrics['ic_ir'] >= self.thresholds['ic_ir_warning']:
            if status != 'EXCELLENT':
                status = 'WARNING'
            alerts.append({
                'level': 'WARNING',
                'message': f"IC_IR={metrics['ic_ir']:.3f}低于良好阈值{self.thresholds['ic_ir_good']}"
            })
        elif metrics['ic_ir'] >= self.thresholds['ic_ir_critical']:
            status = 'CRITICAL'
            alerts.append({
                'level': 'CRITICAL',
                'message': f"IC_IR={metrics['ic_ir']:.3f}处于临界水平"
            })
        else:
            status = 'FAILED'
            alerts.append({
                'level': 'CRITICAL',
                'message': f"IC_IR={metrics['ic_ir']:.3f}已失�?
            })

        # 胜率评估
        if metrics['ic_win_rate'] < self.thresholds['ic_win_rate_critical']:
            alerts.append({
                'level': 'CRITICAL',
                'message': f"胜率={metrics['ic_win_rate']:.1%}低于临界�?
            })
        elif metrics['ic_win_rate'] < self.thresholds['ic_win_rate_warning']:
            alerts.append({
                'level': 'WARNING',
                'message': f"胜率={metrics['ic_win_rate']:.1%}偏低"
            })

        # 近期衰减检�?
        if metrics['recent_ic_ir'] < metrics['ic_ir'] * 0.7:
            alerts.append({
                'level': 'WARNING',
                'message': "因子近期IC_IR明显下降，可能存在衰�?
            })

        return {
            'status': status,
            'alerts': alerts,
            'metrics': metrics
        }
```

---

## 3. 衰减预警

### 3.1 衰减检测器

```python
class FactorDecayDetector:
    """因子衰减检测器"""

    def __init__(self):
        self.decay_thresholds = {
            'ic_decay_warning': 0.3,    # IC衰减30%告警
            'ic_decay_critical': 0.5,   # IC衰减50%严重告警
            'rolling_window': 60,       # 滚动窗口
            'baseline_window': 252       # 基线窗口（一年）
        }

    def detect_decay(
        self,
        ic_series: pd.Series,
        factor_id: str
    ) -> dict:
        """
        检测因子衰�?

        Parameters:
        -----------
        ic_series : pd.Series
            IC时间序列
        factor_id : str
            因子ID

        Returns:
        --------
        dict: 衰减检测结�?
        """
        baseline_ic = ic_series.tail(self.decay_thresholds['baseline_window']).mean()
        recent_ic = ic_series.tail(self.decay_thresholds['rolling_window']).mean()

        # 计算衰减�?
        decay_rate = (baseline_ic - recent_ic) / baseline_ic if baseline_ic > 0 else 0

        # IC随时间衰减分�?
        ic_by_month = ic_series.groupby(ic_series.index.to_period('M')).mean()
        monthly_decay = ic_by_month.pct_change().dropna()

        return {
            'factor_id': factor_id,
            'baseline_ic': baseline_ic,
            'recent_ic': recent_ic,
            'decay_rate': decay_rate,
            'is_decaying': decay_rate > self.decay_thresholds['ic_decay_warning'],
            'severity': self._get_severity(decay_rate),
            'monthly_avg_decay': monthly_decay.mean(),
            'recommendation': self._get_recommendation(decay_rate)
        }

    def _get_severity(self, decay_rate: float) -> str:
        if decay_rate < self.decay_thresholds['ic_decay_warning']:
            return 'NORMAL'
        elif decay_rate < self.decay_thresholds['ic_decay_critical']:
            return 'WARNING'
        else:
            return 'CRITICAL'

    def _get_recommendation(self, decay_rate: float) -> str:
        if decay_rate < 0.2:
            return "因子表现稳定，继续使�?
        elif decay_rate < 0.3:
            return "因子有轻微衰减，密切监控"
        elif decay_rate < 0.5:
            return "因子衰减明显，建议降低权�?
        else:
            return "因子严重衰减，建议暂停使用或优化"
```

---

## 4. 因子生命周期管理

### 4.1 状态机

```python
class FactorLifecycleManager:
    """因子生命周期管理�?""

    STATES = {
        'TESTING': '测试�?,
        'ACTIVE': '运行�?,
        'WARNING': '预警�?,
        'DEGRADED': '降级使用',
        'DEPRECATED': '已废�?,
        'ARCHIVED': '归档'
    }

    def __init__(self):
        self.state_transitions = {
            'TESTING': ['ACTIVE', 'DEPRECATED'],
            'ACTIVE': ['WARNING', 'DEPRECATED'],
            'WARNING': ['ACTIVE', 'DEGRADED', 'DEPRECATED'],
            'DEGRADED': ['ACTIVE', 'DEPRECATED'],
            'DEPRECATED': ['ARCHIVED'],
            'ARCHIVED': []
        }

    def transition(
        self,
        current_state: str,
        event: str,
        reason: str = None
    ) -> dict:
        """
        状态转�?

        Parameters:
        -----------
        current_state : str
            当前状�?
        event : str
            触发事件
        reason : str
            转换原因

        Returns:
        --------
        dict: {success: bool, new_state: str, message: str}
        """
        allowed_states = self.state_transitions.get(current_state, [])

        # 根据事件确定目标状�?
        target_state = self._event_to_state(event)

        if target_state not in allowed_states:
            return {
                'success': False,
                'current_state': current_state,
                'message': f"不允许从{current_state}转换到{target_state}"
            }

        return {
            'success': True,
            'previous_state': current_state,
            'new_state': target_state,
            'reason': reason,
            'timestamp': datetime.now()
        }

    def _event_to_state(self, event: str) -> str:
        """事件到状态的映射"""
        event_map = {
            'pass_validation': 'ACTIVE',
            'ic_warning': 'WARNING',
            'ic_recover': 'ACTIVE',
            'ic_critical': 'DEGRADED',
            'manual_deprecate': 'DEPRECATED',
            'archive': 'ARCHIVED'
        }
        return event_map.get(event, 'TESTING')
```

---

## 5. 监控面板

### 5.1 面板数据生成

```python
class MonitoringDashboard:
    """监控面板数据生成�?""

    def generate_factor_status(
        self,
        factor_metrics: dict,
        decay_result: dict,
        lifecycle_state: str
    ) -> dict:
        """
        生成监控面板数据

        Returns:
        --------
        dict: 面板数据
        """
        return {
            'factor_id': factor_metrics.get('factor_id'),
            'status': lifecycle_state,
            'health_score': self._calculate_health_score(factor_metrics, decay_result),
            'ic_metrics': {
                'current': factor_metrics.get('ic_ir'),
                'trend': 'up' if factor_metrics.get('rolling_ic_ir', 0) > factor_metrics.get('ic_ir', 0) else 'down',
                'win_rate': factor_metrics.get('ic_win_rate')
            },
            'decay_indicators': {
                'decay_rate': decay_result.get('decay_rate'),
                'severity': decay_result.get('severity'),
                'recommendation': decay_result.get('recommendation')
            },
            'last_updated': datetime.now().isoformat()
        }

    def _calculate_health_score(
        self,
        metrics: dict,
        decay: dict
    ) -> float:
        """计算因子健康评分(0-100)"""
        score = 100

        # IC_IR扣分
        ic_ir = metrics.get('ic_ir', 0)
        if ic_ir < 1.0:
            score -= (1.0 - ic_ir) * 30

        # 衰减扣分
        decay_rate = decay.get('decay_rate', 0)
        score -= decay_rate * 50

        # 胜率扣分
        win_rate = metrics.get('ic_win_rate', 0.5)
        if win_rate < 0.55:
            score -= (0.55 - win_rate) * 100

        return max(0, min(100, score))
```

---

## 6. 告警系统

### 6.1 告警规则

```python
class AlertManager:
    """告警管理�?""

    def __init__(self):
        self.rules = [
            {
                'name': 'ic_ir_critical',
                'condition': lambda m: m.get('ic_ir', 0) < 0.3,
                'level': 'CRITICAL',
                'message': '因子IC_IR低于临界�?.3'
            },
            {
                'name': 'ic_decay_warning',
                'condition': lambda m: m.get('decay_rate', 0) > 0.3,
                'level': 'WARNING',
                'message': '因子衰减超过30%'
            },
            {
                'name': 'win_rate_low',
                'condition': lambda m: m.get('ic_win_rate', 1) < 0.50,
                'level': 'WARNING',
                'message': '因子胜率低于50%'
            },
            {
                'name': 'health_score_low',
                'condition': lambda m: m.get('health_score', 100) < 50,
                'level': 'CRITICAL',
                'message': '因子健康评分低于50'
            }
        ]

    def check_alerts(self, metrics: dict) -> list:
        """检查告�?""
        alerts = []

        for rule in self.rules:
            if rule:
                alerts.append({
                    'name': rule['name'],
                    'level': rule['level'],
                    'message': rule['message'],
                    'timestamp': datetime.now()
                })

        return alerts
```

---

## 7. 配置模板

```yaml
# config/factor_monitoring.yaml
factor_monitoring:
  # IC告警阈�?
  ic_thresholds:
    ir_excellent: 1.0
    ir_good: 0.5
    ir_warning: 0.3
    ir_critical: 0.0
    win_rate_warning: 0.50
    win_rate_critical: 0.45

  # 衰减阈�?
  decay_thresholds:
    warning: 0.3    # 30%
    critical: 0.5   # 50%

  # 监控窗口
  windows:
    rolling_ic: 20      # 滚动IC窗口
    baseline_ic: 252    # 基线窗口(一�?
    decay_check: 60     # 衰减检测窗�?

  # 告警配置
  alerts:
    enabled: true
    channels:
      - type: "log"
        level: "WARNING"
      - type: "email"
        level: "CRITICAL"
        recipients: ["researcher@example.com"]
```

---

## 8. 目录位置

```
02_FACTOR_LIBRARY/
├── 01_STANDARDS/
�?  ├── IC_ANALYSIS.md
�?  ├── FACTOR_RETURN_ANALYSIS.md
�?  └── FACTOR_NEUTRALIZATION.md
├── 05_BACKTEST/
�?  └── ic_reports/
├── 06_REGISTRY/
�?  └── FACTOR_CATALOG.md
└── 07_FACTOR_MONITORING/           # �?新目�?
    ├── README.md
    └── FACTOR_MONITORING.md        # 本文�?
```

---

## 9. 接口定义

| 接口 | 说明 |
|------|------|
| **上游接口** | 因子计算引擎、IC分析系统 |
| **下游接口** | 因子筛选、组合优化、告警通知 |
| **输入格式** | IC时间序列、因子元数据 |
| **输出格式** | 监控指标、告警列表、状态转�?|

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
