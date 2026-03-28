# 交易监控模块

> 量化监控系统架构
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 容灾备份：[architecture/disaster-recovery.md](./architecture/disaster-recovery.md)

***

## 1. 监控指标体系

| 类型 | 指标 | 告警阈值 |
|------|------|----------|
| 系统监控 | CPU使用率 | >80% |
| 系统监控 | 内存使用率 | >85% |
| 系统监控 | 网络延迟 | >100ms |
| 交易监控 | 订单失败率 | >5% |
| 交易监控 | 成交延迟P99 | >100ms |
| 风控监控 | 仓位超限 | 即时告警 |
| 风控监控 | 亏损超限 | 即时告警 |

***

## 2. 监控Python实现

```python
class TradingMonitor:
    """交易监控系统"""

    def __init__(self):
        self.metrics = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'order_latency': [],
            'order_success_rate': 1.0,
            'positions': {},
            'daily_pnl': 0
        }
        self.alerts = []
        self.alert_thresholds = {
            'cpu_usage': 80,
            'memory_usage': 85,
            'order_failure_rate': 0.05,
            'max_position_loss': 0.02
        }

    def collect_metrics(self):
        """采集系统指标"""
        import psutil

        self.metrics['cpu_usage'] = psutil.cpu_percent(interval=0.1)
        self.metrics['memory_usage'] = psutil.virtual_memory().percent

        return self.metrics

    def check_alerts(self) -> list:
        """检查告警"""
        alerts = []

        if self.metrics['cpu_usage'] > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'level': 'WARNING',
                'type': 'CPU_HIGH',
                'message': f"CPU使用率{self.metrics['cpu_usage']:.1f}%超限"
            })

        if self.metrics['memory_usage'] > self.alert_thresholds['memory_usage']:
            alerts.append({
                'level': 'WARNING',
                'type': 'MEMORY_HIGH',
                'message': f"内存使用率{self.metrics['memory_usage']:.1f}%超限"
            })

        return alerts

    def record_order_result(self, order_id: str, success: bool, latency_ms: float):
        """记录订单结果"""
        self.metrics['order_latency'].append(latency_ms)

        if not success:
            self.metrics['order_success_rate'] *= 0.99
        else:
            self.metrics['order_success_rate'] = min(1.0, self.metrics['order_success_rate'] * 1.001)

        if self.metrics['order_success_rate'] < self.alert_thresholds['order_failure_rate']:
            self.alerts.append({
                'level': 'CRITICAL',
                'type': 'ORDER_FAILURE_HIGH',
                'message': f"订单失败率{1-self.metrics['order_success_rate']:.2%}超限"
            })

    def get_status_summary(self) -> dict:
        """获取状态摘要"""
        latency_p99 = sorted(self.metrics['order_latency'])[int(len(self.metrics['order_latency'])*0.99)] if self.metrics['order_latency'] else 0

        return {
            'system': {
                'cpu': self.metrics['cpu_usage'],
                'memory': self.metrics['memory_usage']
            },
            'trading': {
                'order_success_rate': self.metrics['order_success_rate'],
                'latency_p99_ms': latency_p99
            },
            'alerts': len(self.alerts),
            'daily_pnl': self.metrics['daily_pnl']
        }
```

***

## 3. 监控告警级别

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| INFO | 正常信息 | 记录 |
| WARNING | 警告 | 关注 |
| ERROR | 错误 | 处理 |
| CRITICAL | 严重 | 立即处理 |

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-27 | 新增交易监控文档 |
