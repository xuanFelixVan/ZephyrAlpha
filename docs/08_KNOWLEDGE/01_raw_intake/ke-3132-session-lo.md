---
module_id: KE-3030
status: active
title: 5.2 读取流程
category: session_log
---

# 5.2 读取流程

5.2 读取流程

```python
async def load_session_carryover(self) -> SessionCarryover | None:
    target = Path(".runtime/sessions/session_carryover.json")
    if not target.exists():
        return None

    try:
        raw = target.read_text(encoding="utf-8")
        carryover = SessionCarryover.model_validate_json(raw)
    except ValidationError as e:
        # schema 不匹配 → 触发迁移或拒绝
        return self._handle_schema_mismatch(raw, e)

    # 检查 schema_version
    if carryover.schema_version != "1.0.0":
        carryover = await self._migrate_schema(carryover)

    # 暴露给 Orchestrator：恢复 open_tasks
    await self.orchestrator.restore_open_tasks(carryover.open_tasks)

    # 暴露给用户：展示 blockers + user_intentions
    self._display_session_recap(carryover)

    return carryover
```
