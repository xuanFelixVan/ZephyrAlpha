---
module_id: KE-2721
status: active
title: Emergency Trading Kill Switch（紧急交易停止）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# Emergency Trading Kill Switch（紧急交易停止）

Emergency Trading Kill Switch（紧急交易停止）

```python
class TradingKillSwitch:
    """B5-K01——一条命令紧急停止所有交易活动。
    对标：CME Kill Switch / Two Sigma "Big Red Button"。
    在量化交易系统中，这是最重要的安全组件——比 CircuitBreaker 高一个优先级。
    """
    _mode: str = "NORMAL"  # NORMAL | PAPER_ONLY | READ_ONLY | KILLED

    async def activate(self, reason: str,
                        confirmed_by: str = "AUTO") -> KillSwitchResult:
        """立即执行五步停止序列"""
        results = []

        # 1. 标记模式→KILLED（所有RM模块立即感知）
        self._mode = "KILLED"

        # 2. 所有未完成订单→取消
        results.append(await self._cancel_all_pending_orders())

        # 3. EventBus 中所有交易事件→清空
        results.append(await EventBus.purge_events(
            event_types=["TradeEvent", "OrderEvent"]))

        # 4. 所有L05（交易执行）模块→只读
        results.append(await ModuleLifecycle.set_mode("L05", "READ_ONLY"))

        # 5. 审计记录→永久留存
        audit.record_severe(f"KILL_SWITCH: reason={reason} by={confirmed_by}")

        return KillSwitchResult(mode=self._mode, actions=results)

    async def deactivate(self, confirmed_by: str) -> KillSwitchResult:
        """恢复交易——需要Owner显式确认"""
        if confirmed_by != "Owner":
            raise PermissionError("Kill Switch 只能由 Owner 手动解除")
        self._mode = "NORMAL"
        # 恢复L05模块为可写
        await ModuleLifecycle.set_mode("L05", "NORMAL")
        return KillSwitchResult(mode=self._mode)
```
