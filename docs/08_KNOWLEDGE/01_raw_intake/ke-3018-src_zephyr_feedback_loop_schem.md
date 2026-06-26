---
module_id: KE-2918
status: active
title: src/zephyr/feedback-loop/schemas.py (experimental 产出)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# src/zephyr/feedback-loop/schemas.py (experimental 产出)

src/zephyr/feedback-loop/schemas.py (experimental 产出)

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class Metric(BaseModel):
    metric_name: str = Field(..., description="命名空间化，如 'orc.task.duration_ms' / 'vms.search.hit_rate'")
    value: float
    unit: Optional[str] = None
    tags: dict[str, str] = Field(default_factory=dict,
        description="如 {'task_kind':'feature','agent_id':'A-01'}")
    source: Literal["orchestrator", "vms", "context-engine", "lsg", "external"] = "external"
    observed_at: datetime
    correlation_id: Optional[str] = Field(None, description="关联 task_id / request_id，用于根因追溯")

class Baseline(BaseModel):
    metric_name: str
    window: str = Field(description="'7d' / '24h' / '1h'")
    mean: float
    stddev: float
    ema: float = Field(description="指数移动平均")
    ema_alpha: float = Field(default=0.2)
    sample_count: int
    computed_at: datetime

class Anomaly(BaseModel):
    anomaly_id: str
    metric_name: str
    observed_value: float
    baseline_mean: float
    baseline_stddev: float
    deviation_sigma: float = Field(description="|(value-mean)/stddev|")
    severity: Literal["info", "warn", "error", "critical"]
    anomaly_kind: Literal[
        "spike",            # 单点飙升
        "drop",             # 单点跌落
        "trend_up",         # 持续上升
        "trend_down",       # 持续下降
        "flatline",         # 数据停滞（上游挂了？）
        "oscillation",      # 震荡
    ]
    window: str
    first_observed_at: datetime
    last_observed_at: datetime
    correlation_ids: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list,
        description="根据 anomaly_kind 映射建议动作 ID")

class PendingAction(BaseModel):
    action_id: str
    anomaly_id: str
    action_kind: Literal[
        "adjust_context_slot_weight",   # → Context Engine
        "invalidate_context_cache",     # → Context Engine
        "pause_task_kind",              # → Orchestrator
        "quarantine_agent",             # → Orchestrator
        "quarantine_vms_collection",    # → VMS (降权检索)
        "bump_lsg_strictness",          # → LSG
        "alert_ops",                    # → Dashboard / log only
    ]
    target_service: Literal["context-engine", "orchestrator", "vms", "lsg", "ops"]
    payload: dict
    dispatched_at: Optional[datetime] = None
    expires_at: datetime = Field(description="超时未执行自动丢弃")

class ActionOutcome(BaseModel):
    action_id: str
    executed: bool
    effective_observed: bool = Field(description="是否观察到指标改善")
    rollback_required: bool = Field(default=False)
    outcome_measured_at: datetime
    notes: Optional[str] = None
```
