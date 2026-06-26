---
module_id: KE-2878
status: active
title: Saga Coordinator（触发式）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# Saga Coordinator（触发式）

Saga Coordinator（触发式）

```python
class SagaCoordinator:
    """RI-13 扩展——跨模块补偿事务（Phase 4 触发，仅当需要多步骤回滚时激活）"""
    _active_sagas: dict[str, "SagaInstance"] = {}

    async def start(self, saga_id: str,
                    steps: list["SagaStep"]) -> SagaResult: ...

    async def compensate(self, saga_id: str,
                         failed_step: int) -> CompensateResult:
        """从 failed_step 逆序执行补偿——恢复每个步骤之前的状态"""
```
