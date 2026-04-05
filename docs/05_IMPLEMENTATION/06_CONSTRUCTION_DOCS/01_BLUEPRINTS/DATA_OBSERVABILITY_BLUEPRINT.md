---
module_id: DATA_OBSERVABILITY_001
version: 1.0.0
status: Active
created_date: 2026-04-05
last_updated: 2026-04-05
owner: 首席蓝图架构师
standard_type: 专业量化机构蓝图
applicable_scope: Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
---

# 数据可观测性平台蓝图

> 清风量化系统 v5.3 - 数据可观测性平台详细设计
> **模块ID**: `DATA_OBSERVABILITY_001`
> **实施周期**: Week 7-8（2周）
> **优先级**: P0（核心）
> **预期收益**: 数据问题发现时间从小时级缩短到分钟级，数据信任度提升50%

## 一、设计背景与目标

### 1.1 业务需求

**当前痛点**:
- 数据问题发现被动，依赖用户报告或告警
- 缺少数据新鲜度监控，无法及时发现数据延迟
- 数据量异常变化难以察觉，影响下游分析
- Schema变更无感知，导致管道失败

**业务目标**:
- 主动发现数据问题，而非被动响应告警
- 监控数据新鲜度，及时发现数据延迟
- 检测数据量异常变化，预警潜在问题
- 自动检测Schema变更，提前预警

### 1.2 技术目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **异常检测准确率** | ≥95% | 95%以上的异常被正确识别 |
| **问题发现时间** | <5分钟 | 从问题发生到发现的时间 |
| **误报率** | <5% | 误报比例低于5% |
| **覆盖率** | 100% | 所有关键数据表被监控 |

---

## 二、系统架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                数据可观测性平台架构                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           监控采集层 (Monitoring Collection)         │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │新鲜度监控   │ │数据量监控   │ │Schema监控   │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │质量监控     │ │分布监控     │ │血缘监控     │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           异常检测层 (Anomaly Detection)             │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │统计检测     │ │ML检测       │ │规则检测     │   │   │
│  │  │(Z-Score)    │ │(Isolation   │ │(Threshold)  │   │   │
│  │  │             │ │Forest)      │ │             │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           告警与通知层 (Alert & Notification)        │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │告警聚合     │ │告警抑制     │ │多渠道通知   │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           可视化层 (Visualization)                   │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │监控仪表板   │ │异常报告     │ │趋势分析     │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 组件 | 技术方案 | 版本要求 | 选型理由 |
|------|---------|---------|---------|
| **可观测性平台** | Elementary | 0.12.0+ | dbt原生数据可观测性 |
| **异常检测** | PyOD | 1.1.0+ | 50+异常检测算法 |
| **时序预测** | Prophet | 1.1.0+ | Facebook时序预测 |
| **监控存储** | PostgreSQL | 15.0+ | 存储监控指标 |
| **可视化** | Grafana | 10.0+ | 监控仪表板 |

### 2.3 Layer定位

- **Layer归属**: Layer 1 - 数据预处理层
- **职责范围**: 数据新鲜度监控、数据量监控、Schema变更检测、异常检测
- **上下层接口**:
  - 上层依赖: Layer 2-8（提供数据健康状态查询）
  - 下层依赖: Layer 0-1数据源层（采集监控指标）

---

## 三、核心模块设计

### 3.1 数据新鲜度监控器 (FreshnessMonitor)

**职责**: 监控数据更新频率，检测数据延迟

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

class FreshnessStatus(Enum):
    """新鲜度状态"""
    FRESH = "fresh"           # 数据新鲜
    STALE = "stale"           # 数据过期
    CRITICAL = "critical"     # 严重过期
    UNKNOWN = "unknown"       # 未知状态

@dataclass
class FreshnessConfig:
    """新鲜度配置"""
    table_id: str
    expected_frequency: timedelta
    warning_threshold: timedelta
    critical_threshold: timedelta
    timezone: str = "Asia/Shanghai"

@dataclass
class FreshnessMetric:
    """新鲜度指标"""
    table_id: str
    last_update_time: datetime
    expected_update_time: datetime
    actual_delay: timedelta
    status: FreshnessStatus
    timestamp: datetime = field(default_factory=datetime.now)

class FreshnessMonitor:
    """数据新鲜度监控器"""
    
    def __init__(self):
        self.configs: Dict[str, FreshnessConfig] = {}
        self.metrics: Dict[str, List[FreshnessMetric]] = {}
    
    def register_table(self, config: FreshnessConfig):
        """注册表监控"""
        self.configs[config.table_id] = config
    
    def check_freshness(self, table_id: str, last_update_time: datetime) -> FreshnessMetric:
        """检查数据新鲜度"""
        config = self.configs.get(table_id)
        if not config:
            raise ValueError(f"表 {table_id} 未注册监控")
        
        now = datetime.now()
        actual_delay = now - last_update_time
        
        if actual_delay > config.critical_threshold:
            status = FreshnessStatus.CRITICAL
        elif actual_delay > config.warning_threshold:
            status = FreshnessStatus.STALE
        else:
            status = FreshnessStatus.FRESH
        
        metric = FreshnessMetric(
            table_id=table_id,
            last_update_time=last_update_time,
            expected_update_time=now - config.expected_frequency,
            actual_delay=actual_delay,
            status=status
        )
        
        if table_id not in self.metrics:
            self.metrics[table_id] = []
        self.metrics[table_id].append(metric)
        
        return metric
    
    def get_stale_tables(self) -> List[FreshnessMetric]:
        """获取过期表列表"""
        stale_tables = []
        for table_id, metrics in self.metrics.items():
            if metrics:
                latest = metrics[-1]
                if latest.status in [FreshnessStatus.STALE, FreshnessStatus.CRITICAL]:
                    stale_tables.append(latest)
        return stale_tables
    
    def get_freshness_summary(self) -> Dict[str, int]:
        """获取新鲜度摘要"""
        summary = {status.value: 0 for status in FreshnessStatus}
        for metrics in self.metrics.values():
            if metrics:
                summary[metrics[-1].status.value] += 1
        return summary
```

### 3.2 数据量监控器 (VolumeMonitor)

**职责**: 监控数据量变化，检测异常波动

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass
class VolumeMetric:
    """数据量指标"""
    table_id: str
    row_count: int
    size_bytes: int
    timestamp: datetime
    change_rate: float = 0.0
    is_anomaly: bool = False

class VolumeMonitor:
    """数据量监控器"""
    
    def __init__(self, anomaly_detector: 'VolumeAnomalyDetector'):
        self.anomaly_detector = anomaly_detector
        self.history: Dict[str, List[VolumeMetric]] = {}
    
    def record_volume(self, table_id: str, row_count: int, size_bytes: int) -> VolumeMetric:
        """记录数据量"""
        now = datetime.now()
        
        change_rate = 0.0
        if table_id in self.history and self.history[table_id]:
            prev = self.history[table_id][-1]
            if prev.row_count > 0:
                change_rate = (row_count - prev.row_count) / prev.row_count
        
        metric = VolumeMetric(
            table_id=table_id,
            row_count=row_count,
            size_bytes=size_bytes,
            timestamp=now,
            change_rate=change_rate
        )
        
        is_anomaly = self.anomaly_detector.detect(metric, self.history.get(table_id, []))
        metric.is_anomaly = is_anomaly
        
        if table_id not in self.history:
            self.history[table_id] = []
        self.history[table_id].append(metric)
        
        return metric
    
    def get_volume_trend(self, table_id: str, days: int = 7) -> Dict[str, Any]:
        """获取数据量趋势"""
        if table_id not in self.history:
            return {}
        
        metrics = self.history[table_id]
        cutoff = datetime.now() - timedelta(days=days)
        recent = [m for m in metrics if m.timestamp >= cutoff]
        
        if not recent:
            return {}
        
        return {
            "table_id": table_id,
            "current_row_count": recent[-1].row_count,
            "avg_row_count": np.mean([m.row_count for m in recent]),
            "min_row_count": min(m.row_count for m in recent),
            "max_row_count": max(m.row_count for m in recent),
            "avg_change_rate": np.mean([m.change_rate for m in recent]),
            "anomaly_count": sum(1 for m in recent if m.is_anomaly)
        }

class VolumeAnomalyDetector:
    """数据量异常检测器"""
    
    def __init__(self, z_threshold: float = 3.0, min_history: int = 7):
        self.z_threshold = z_threshold
        self.min_history = min_history
    
    def detect(self, metric: VolumeMetric, history: List[VolumeMetric]) -> bool:
        """检测数据量异常"""
        if len(history) < self.min_history:
            return False
        
        historical_counts = [m