---
module_id: MODULE_MONITOR
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 系统监控体系文档
---

﻿---
module_id: EXEC_MODULE_MONITOR_001
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
implementation_status: 进行?---


# 系统监控体系
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 基础设施? 模块监控、资源监控、性能指标、告警管?

---

## 1. 设计概述

系统监控体系负责收集和展示所有模块的运行状态和性能指标?

```
监控架构
├── 指标收集?(Metrics Collection)
?  ├── 系统指标
?  ├── 业务指标
?  └── 自定义指?
├── 指标存储?(Metrics Storage)
?  ├── 实时内存存储
?  ├── 时序数据库存?
?  └── 历史数据存储
├── 可视化层 (Visualization)
?  ├── 仪表?
?  ├── 趋势?
?  └── 告警面板
└── 告警管理?(Alerting)
    ├── 阈值告?
    ├── 趋势告警
    └── 复合告警
```

---

## 2. 核心实现

### 2.1 指标定义

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import time


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"       # 计数?
    GAUGE = "gauge"         # 仪表
    HISTOGRAM = "histogram" # 直方?
    TIMER = "timer"         # 计时?


@dataclass
class Metric:
    """指标"""
    name: str
    value: float
    metric_type: MetricType
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ModuleStatus:
    """模块状?""
    module_id: str
    module_name: str
    status: str  # 'healthy', 'degraded', 'down'
    uptime: float
    last_heartbeat: datetime
    metrics: Dict[str, Metric] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class MetricsCollector:
    """指标收集?""

    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = {}
        self.module_status: Dict[str, ModuleStatus] = {}
        self.start_time = time.time()

    def record(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        unit: str = "",
        tags: Dict[str, str] = None
    ):
        """记录指标"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            unit=unit,
            tags=tags or {},
            timestamp=datetime.now()
        )

        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append(metric)

        if len(self.metrics[name]) > 10000:
            self.metrics[name] = self.metrics[name][-5000:]

    def increment(self, name: str, value: float = 1, tags: Dict[str, str] = None):
        """增加计数?""
        self.record(name, value, MetricType.COUNTER, tags=tags)

    def gauge(self, name: str, value: float, unit: str = "", tags: Dict[str, str] = None):
        """设置仪表?""
        self.record(name, value, MetricType.GAUGE, unit, tags)

    def histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录直方图?""
        self.record(name, value, MetricType.HISTOGRAM, tags=tags)

    def timer(self, name: str, func, tags: Dict[str, str] = None):
        """计时器装饰器"""
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start

            self.record(name, duration, MetricType.TIMER, "seconds", tags)

            return result

        return wrapper

    def update_module_status(
        self,
        module_id: str,
        module_name: str,
        status: str,
        metrics: Dict[str, float] = None,
        errors: List[str] = None
    ):
        """更新模块状?""
        now = datetime.now()

        if module_id in self.module_status:
            uptime = self.module_status[module_id].uptime
        else:
            uptime = time.time() - self.start_time

        module_metrics = {}
        if metrics:
            for name, value in metrics.items():
                module_metrics[name] = Metric(
                    name=name,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    timestamp=now
                )

        self.module_status[module_id] = ModuleStatus(
            module_id=module_id,
            module_name=module_name,
            status=status,
            uptime=uptime,
            last_heartbeat=now,
            metrics=module_metrics,
            errors=errors or []
        )

    def get_metric_series(
        self,
        name: str,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[Metric]:
        """获取指标时间序列"""
        if name not in self.metrics:
            return []

        metrics = self.metrics[name]

        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]

        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]

        return metrics

    def get_latest_value(self, name: str) -> Optional[float]:
        """获取最新?""
        if name not in self.metrics or not self.metrics[name]:
            return None

        return self.metrics[name][-1].value

    def get_aggregated_value(
        self,
        name: str,
        aggregation: str = "mean",
        window_seconds: int = 60
    ) -> Optional[float]:
        """获取聚合?""
        metrics = self.get_metric_series(name)

        if not metrics:
            return None

        cutoff = datetime.now().timestamp() - window_seconds
        recent = [m for m in metrics if m.timestamp.timestamp() >= cutoff]

        if not recent:
            return None

        values = [m.value for m in recent]

        if aggregation == "mean":
            return sum(values) / len(values)
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "max":
            return max(values)
        else:
            return values[-1]
```

---

## 3. 预定义监控指?

### 3.1 系统级指?

```python
class SystemMetrics:
    """系统级指?""

    @staticmethod
    def get_cpu_metrics() -> Dict[str, float]:
        """CPU指标"""
        import psutil

        return {
            "system.cpu.usage_percent": psutil.cpu_percent(interval=1),
            "system.cpu.count": psutil.cpu_count(),
            "system.cpu.load_avg": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
        }

    @staticmethod
    def get_memory_metrics() -> Dict[str, float]:
        """内存指标"""
        import psutil

        mem = psutil.virtual_memory()

        return {
            "system.memory.total": mem.total,
            "system.memory.available": mem.available,
            "system.memory.used": mem.used,
            "system.memory.percent": mem.percent
        }

    @staticmethod
    def get_disk_metrics() -> Dict[str, float]:
        """磁盘指标"""
        import psutil

        disk = psutil.disk_usage('/')

        return {
            "system.disk.total": disk.total,
            "system.disk.free": disk.free,
            "system.disk.percent": disk.percent
        }
```

### 3.2 业务级指?

```python
class BusinessMetrics:
    """业务级指?""

    DATA_HUB = "datahub"
    FACTOR_CALC = "factor_calculator"
    STRATEGY_ENG = "strategy_engine"
    RISK_MGMT = "risk_manager"
    TRADE_EXEC = "trade_executor"
    BACKTEST = "backtest_engine"

    @staticmethod
    def get_datahub_metrics() -> Dict[str, str]:
        """DataHub业务指标"""
        return {
            "datahub.data_requests": "gauge",
            "datahub.cache_hit_rate": "gauge",
            "datahub.query_latency_ms": "histogram",
            "datahub.error_count": "counter"
        }

    @staticmethod
    def get_factor_metrics() -> Dict[str, str]:
        """因子计算业务指标"""
        return {
            "factor.calc_requests": "counter",
            "factor.calc_latency_ms": "histogram",
            "factor.calc_errors": "counter",
            "factor.quality_score": "gauge"
        }
```

---

## 4. 监控面板

### 4.1 监控面板生成

```python
class MonitoringDashboard:
    """监控仪表?""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def generate_system_overview(self) -> str:
        """生成系统概览"""
        lines = [
            "=" * 80,
            "系统监控概览",
            "=" * 80,
            ""
        ]

        uptime_seconds = time.time() - self.collector.start_time
        uptime_hours = uptime_seconds / 3600

        lines.append(f"系统运行时间: {uptime_hours:.1f} 小时")
        lines.append("")

        lines.append("模块状?")
        lines.append("-" * 80)

        for module_id, status in self.collector.module_status.items():
            status_icon = "? if status.status == "healthy" else "⚠️" if status.status == "degraded" else "?

            lines.append(f"{status_icon} {status.module_name}: {status.status}")
            lines.append(f"   运行时间: {status.uptime / 3600:.1f}小时")
            lines.append(f"   最后心? {status.last_heartbeat.strftime('%H:%M:%S')}")

            if status.errors:
                lines.append(f"   错误: {', '.join(status.errors[-3:])}")

            lines.append("")

        return "\n".join(lines)

    def generate_performance_report(self) -> str:
        """生成性能报告"""
        lines = [
            "=" * 80,
            "性能监控报告",
            "=" * 80,
            ""
        ]

        key_metrics = [
            ("datahub.query_latency_ms", "查询延迟"),
            ("factor.calc_latency_ms", "因子计算延迟"),
            ("backtest.duration_ms", "回测耗时"),
            ("trade.exec_latency_ms", "交易执行延迟")
        ]

        for metric_name, metric_label in key_metrics:
            value = self.collector.get_aggregated_value(metric_name, "mean", 300)

            if value is not None:
                lines.append(f"{metric_label}: {value:.2f} ms")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def check_health(self) -> Dict:
        """健康检?""
        issues = []

        for module_id, status in self.collector.module_status.items():
            if status.status == "down":
                issues.append(f"Module {module_id} is down")

            time_since_heartbeat = (datetime.now() - status.last_heartbeat).total_seconds()
            if time_since_heartbeat > 300:
                issues.append(f"Module {module_id} heartbeat timeout")

        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "timestamp": datetime.now()
        }
```

---

## 5. 使用示例

```python
def example_monitoring():
    """监控使用示例"""

    collector = MetricsCollector()

    collector.update_module_status(
        module_id="M01",
        module_name="DataHub",
        status="healthy",
        metrics={
            "requests": 1000,
            "latency_ms": 45.2
        }
    )

    for i in range(100):
        collector.increment("datahub.data_requests")
        collector.histogram(
            "datahub.query_latency_ms",
            30 + (i % 20)
        )

    dashboard = MonitoringDashboard(collector)

    print(dashboard.generate_system_overview())
    print(dashboard.generate_performance_report())

    health = dashboard.check_health()
    print(f"System healthy: {health['healthy']}")
```

---

**版本**: 1.0
**更新**: 2026-03-28
**Layer**: 基础设施?(横切关注?
**索引**: BLUEPRINTS.md ?基础设施蓝图
**上游接口**: 所有模?(M01-M15)
**下游接口**: AlertManager (M14)
