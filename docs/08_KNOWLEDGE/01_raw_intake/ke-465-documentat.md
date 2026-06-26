---
module_id: KE-417
status: active
title: 5.3 逃逸检测
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 5.3 逃逸检测

5.3 逃逸检测

**P0 检测项**：

1. Agent 尝试访问白名单外路径 → 立即 kill + 记录 Session Log
2. Agent 尝试执行白名单外命令 → 拒绝 + 触发 FLE 异常事件
3. Agent 进程内存 / CPU 超配额（默认 2GB / 2 cores）→ 强制回收

**已知局限**：Windows ACL 不如 Linux namespace 隔离严格，beta 接入真实资金前**必须**升级为 Docker 沙箱。

---
