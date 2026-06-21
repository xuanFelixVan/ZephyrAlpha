---
module_id: KE-2314
status: active
title: 5.4 依赖方向图
category: module_blueprint
---

# 5.4 依赖方向图

5.4 依赖方向图

```
  Orchestrator --[push metrics via FeedbackSinkProtocol]--> FLE
  Context Engine --[push metrics]--> FLE
  VMS --[push metrics]--> FLE
  LSG --[push metrics]--> FLE

  FLE --[via ContextAdjustActionProtocol adapter]--> Context Engine.adjust_strategy()
  FLE --[via OrchestratorControlActionProtocol adapter]--> Orchestrator.pause_task_kind() 等
  FLE --[via VMSControlActionProtocol adapter]--> VMS.quarantine_collection()
  FLE --[via LSGControlActionProtocol adapter]--> LSG.bump_strictness()
```

**没有循环依赖**：FLE 永远是中心，上游推、下游拉。所有跨服务调用通过 Protocol 解耦。

---
