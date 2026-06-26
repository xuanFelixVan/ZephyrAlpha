---
module_id: KE-431---14-001
status: active
title: 5A.2 与 14 层量化架构的关系
category: documentation
ttl: permanent
---

# 5A.2 与 14 层量化架构的关系

5A.2 与 14 层量化架构的关系

```
L12 跨层支撑层
  └─ src/zephyr/
       ├─ llm-security/      ← LSG
       ├─ vector-memory/     ← VMS
       ├─ context-engine/    ← CE
       ├─ orchestrator/      ← Orc
       └─ feedback-loop/     ← FLE

6 大核心服务属于 L12，为 L00-L11 + L13 业务层提供 AI 基础设施能力。
```
