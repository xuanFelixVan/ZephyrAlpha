---
module_id: KE-1940
title: 2.7 shared-lifecycle（模块生命周期）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.7 shared-lifecycle（模块生命周期）

2.7 shared-lifecycle（模块生命周期）

> **盲点 B8 修复**——统一模块初始化/启动/关闭/健康检查契约。

| 文件 | 职责 |
|------|------|
| `lifecycle/hooks.py` | **LifecycleAware Protocol** + **LifecycleManager 编排器**——on_init/on_startup/on_shutdown/health_check |
