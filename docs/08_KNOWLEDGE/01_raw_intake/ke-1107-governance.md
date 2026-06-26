---
module_id: KE-1022
status: active
title: 8. 破坏性变更处理
category: governance
ttl: permanent
---

# 8. 破坏性变更处理

8. 破坏性变更处理

当接口发生破坏性变更时，必须执行以下流程：

1. **创建 KB 决策记录**：记录变更原因、影响范围、迁移方案
2. **双版本并行**：新旧接口同时运行，旧接口标记 `deprecated`
3. **通知消费方**：向所有 `consumers` 发出迁移通知
4. **迁移期**：至少 30 天，消费方完成迁移
5. **旧接口下线**：迁移期结束后，旧接口标记 `deprecated`，`superseded_by` 指向新版本
6. **清理**：90 天后物理删除旧接口定义
