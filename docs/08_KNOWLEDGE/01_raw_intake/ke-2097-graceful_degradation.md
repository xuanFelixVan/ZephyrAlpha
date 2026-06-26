---
module_id: KE-2006
status: active
title: 3. Graceful Degradation 对齐
category: module_blueprint
ttl: permanent
---

# 3. Graceful Degradation 对齐

3. Graceful Degradation 对齐

当Kill Switch ON或Budget耗尽：
- Pipeline 状态 → DEGRADED
- 拒绝新dispatch
- 现有活跃dispatch → 标记需要尽快完成
- 通知Owner
