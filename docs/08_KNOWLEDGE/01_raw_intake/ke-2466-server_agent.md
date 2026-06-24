---
module_id: KE-2371---server------agent-000
status: active
title: 6.2 跨 Server 编排流程（Agent 串联）
category: module_blueprint
---

# 6.2 跨 Server 编排流程（Agent 串联）

6.2 跨 Server 编排流程（Agent 串联）

```
AI Agent
  │
  ├─ tools/call: task_manager.decompose_blueprint("MOD-INF-013")
  │     → 返回子任务列表 [T1, T2, T3]
  │
  ├─ tools/call: knowledge_base.search("MCP authentication patterns")
  │     → 返回相关 KE 列表
  │
  ├─ tools/call: gate_engine.run_g4_contract({...})
  │     → 返回 PASS/FAIL + 裁决理由
  │
  └─ tools/call: session_handoff.validate_doc_version({...})
        → 返回版本校验结果
```

---
