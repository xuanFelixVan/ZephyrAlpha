---
module_id: KE-module_blu-2__scheduling_profiles-003
title: 2. Scheduling Profiles（三配置）
category: module_blueprint
---

# 2. Scheduling Profiles（三配置）

2. Scheduling Profiles（三配置）

| Profile | 适用条件 | 管线配置 |
|---------|---------|---------|
| **audit_strict** | task_type=AUDIT + priority=P0/P1 | M3+M7双盲 + full_g0_g7 |
| **doc_fast** | task_type∈{DOC_WRITE,REFACTOR} | M1→M3(跳过M7) + pre_commit_only |
| **batch_low** | priority=P3 | 攒P3 batch→30min或10个→batch dispatch + post_exec_only |

```python
class SchedulingProfile(BaseModel):
    name: str                     # "audit_strict"|"doc_fast"|"batch_low"
    timeout_s: float
    gate_profile: str
    skip_modules: list[str]       # doc_fast跳过 M7/M8/M9
    batch_window_s: int|None      # batch_low 30min batch window
    
PROFILES = {
    "audit_strict": SchedulingProfile("audit_strict", 600, "full_g0_g7", [], None),
    "doc_fast":     SchedulingProfile("doc_fast", 120, "pre_commit_only", ["M7","M8","M9"], None),
    "batch_low":    SchedulingProfile("batch_low", 1800, "post_exec_only", [], 1800),
}

def select_profile(task_card: TaskCard) -> SchedulingProfile:
    if task_card.task_type == "AUDIT" and task_card.priority in ("P0","P1"):
        return PROFILES["audit_strict"]
    elif task_card.task_type in ("DOC_WRITE","REFACTOR"):
        return PROFILES["doc_fast"]
    elif task_card.priority == "P3":
        return PROFILES["batch_low"]
    return PROFILES["audit_strict"]  # 默认
```
