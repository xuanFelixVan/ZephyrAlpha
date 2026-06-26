---
module_id: KE-1805
status: active
title: 2.227 Action Atomicity Manager - action_atomicity_manager.py (🆕 v0.21.0 - 盲点276
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.227 Action Atomicity Manager - action_atomicity_manager.py (🆕 v0.21.0 - 盲点276

2.227 Action Atomicity Manager - action_atomicity_manager.py (🆕 v0.21.0 - 盲点276 — 多步骤修复的事务性保证)

**致命问题**：REPAIR_CONFIG通常涉及多个步骤——更新config file→reload进程→验证→若失败→回滚。但现有FLE执行这些步骤时没有事务性保证：如果第2步(reload)成功但第3步(验证)失败→FLE没有机制确保回滚第1步的config file变更。在金融系统中，配置撕裂(config-split)可能导致order router一半用旧规则一半用新规则→灾难。
**对标**：PostgreSQL Savepoint + Redis MULTI/EXEC + Kubernetes Controller Reconciliation Pattern + Saga Pattern for Distributed Transactions

```python
@dataclass
class AtomicStep:
    step_index: int
    action: str          # "UPDATE_CONFIG"|"RELOAD_SERVICE"|"VERIFY_METRICS"
    rollback_action: str # "REVERT_CONFIG"|"RESTART_SERVICE"|None
    executed: bool
    rolled_back: bool

class ActionAtomicityManager:
    MAX_RETRY_PER_STEP: int = 2

    async def execute_with_atomicity(self,
                                       plan: list[AtomicStep]) -> AtomicityResult:
        executed_steps = []
        try:
            for step in plan:
                for attempt in range(self.MAX_RETRY_PER_STEP + 1):
                    try:
                        await self._execute_step(step)
                        step.executed = True
                        executed_steps.append(step)
                        break
                    except Exception as e:
                        if attempt == self.MAX_RETRY_PER_STEP:
                            raise AtomicityFailure(
                                f"Step {step.step_index} failed after {self.MAX_RETRY_PER_STEP+1} attempts: {e}",
                                executed_steps=executed_steps)
                        await asyncio.sleep(1 << attempt)  # exponential backoff
            # All steps succeeded → final verification
            verification = await self._verify_all_steps(plan)
            if not verification.passed:
                raise AtomicityFailure("Post-execution verification failed",
                    executed_steps=executed_steps)
            return AtomicityResult(success=True)
        except AtomicityFailure as af:
            # ROLLBACK: 反向遍历已执行的steps，执行各自的rollback_action
            rolled_back = []
            for step in reversed(executed_steps):
                if step.rollback_action:
                    try:
                        await self._execute_rollback(step)
                        step.rolled_back = True
                        rolled_back.append(step)
                    except Exception as e:
                        self.FLE.notify_owner("ATOMICITY_ROLLBACK_PARTIAL",
                            f"Rollback of step {step.step_index} FAILED: {e}. "
                            f"System may be in INCONSISTENT state. "
                            f"Rolled back: {len(rolled_back)}/{len(executed_steps)} steps. "
                            f"Owner MUST perform manual state verification.")
            return AtomicityResult(success=False,
                rolled_back_count=len(rolled_back),
                total_steps=len(plan))
```
