---
module_id: KE-module_blu-5_feedback_loop___context_engi-000
title: 遗漏 #5：Feedback Loop → Context Engine 反馈通道 schema
category: module_blueprint
---

# 遗漏 #5：Feedback Loop → Context Engine 反馈通道 schema

遗漏 #5：Feedback Loop → Context Engine 反馈通道 schema
class FeedbackSignal(BaseModel):
    task_id: str
    anomaly_type: Literal[
        "hallucination_spike",        # 幻觉率飙升
        "test_failure_pattern",       # 测试失败模式
        "irrelevant_context_cited",   # 引用了不相关上下文
        "context_insufficient",       # 上下文不足反复追问
        "token_overflow",             # 实际调用时 token 超限
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    suggested_action: Literal[
        "downweight_slot",            # 降权某 slot
        "upweight_slot",              # 升权某 slot
        "invalidate_cache",           # 失效缓存
        "switch_compression_strategy", # 切换压缩策略
    ]
    target_slot: Optional[str] = None
    adjustment_magnitude: float = Field(default=0.1, description="权重调整幅度，0.1 = ±10%")
    observed_at: datetime

class AdjustResult(BaseModel):
    applied: bool
    new_slot_budgets: dict[str, float]
    effective_from: datetime
    ttl_minutes: int = Field(default=60, description="调整生效时长，到期回默认")
```

---
