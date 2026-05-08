---
module_id: KE-module_blu-fle___record_metric____try_exc-003
title: 调 FLE 的 record_metric 必须 try/except，不抛到业务层
category: module_blueprint
---

# 调 FLE 的 record_metric 必须 try/except，不抛到业务层

调 FLE 的 record_metric 必须 try/except，不抛到业务层
try:
    await fle_sink.record_metric(metric)
except Exception as e:
    # 不阻塞业务，本地缓冲待恢复
    local_buffer.append(metric)
    log_structured("fle_push_degrade", reason=str(e))
```

**FLE 恢复后**：暴露 `replay_buffer(metrics)` 接口给上游回放。

**DEGRADE-002：下游 Action Protocol 未注入或调用失败时缓冲**

触发场景：
- Wiring 阶段某下游 Protocol 未注入（例如 experimental 暂不接 LSG）
- 下游服务挂
- 下游超时

降级动作：

```python
try:
    await self._context_action.adjust_strategy(task_id, signal)
except Exception as e:
    # 写 pending_actions.ndjson
    await self._buffer_pending_action(action, reason=str(e))
    log_structured("fle_dispatch_degrade", code="DEGRADE-002", action_id=aid, reason=str(e))
```

**恢复策略**：暴露 `replay_pending_actions()` 接口，下游恢复后主动调。action 超 `expires_at` 自动丢弃避免陈旧动作生效。

**对 ACTION 产出的硬约束**：每个 Action 的生效**必须记录 `effective_from` + `ttl`**，超 ttl 自动回滚默认，**FLE 挂了也不会留下永久错误配置**。
