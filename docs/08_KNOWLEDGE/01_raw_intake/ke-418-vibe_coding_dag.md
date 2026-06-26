---
module_id: KE-381-------dag-003
status: active
title: 4A.2 服务间依赖 DAG
category: documentation
ttl: permanent
---

# 4A.2 服务间依赖 DAG

4A.2 服务间依赖 DAG

```
LSG ──────── （零依赖，最底层）
VMS ──────── （仅依赖 ChromaDB + BGE-M3 本地资源）
CE  ──────── 依赖 VMS（检索）+ LSG（注入前校验）
Orc ──────── 依赖 CE（上下文）+ VMS（记忆写入）+ LSG（工具调用校验）
FLE ──────── 指标入向：所有服务上报；动作出向：Protocol 适配器调 CE/Orc/VMS/LSG
```

**强约束**：FLE 到其他服务通过 **Protocol 适配器**（单向），其他服务**不知道 FLE 存在**。防止循环依赖。
