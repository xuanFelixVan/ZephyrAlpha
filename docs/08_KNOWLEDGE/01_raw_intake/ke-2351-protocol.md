---
module_id: KE-2256----------protocol--------5-003
status: active
title: 5. 反馈动作与下游 Protocol 引用（遗漏 #5 重点章节）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 5. 反馈动作与下游 Protocol 引用（遗漏 #5 重点章节）

5. 反馈动作与下游 Protocol 引用（遗漏 #5 重点章节）

> **核心设计约束**：FLE 调 Context Engine / Orchestrator 的 `adjust_*` 接口时，**严禁直接 import** 其实现类。必须定义本地 Protocol，调用方在 wiring 层注入。
>
> **原因**：
> 1. 避免循环依赖（CE 未来可能订阅 FLE 的 `runtime_state` 作为 slot 输入）
> 2. 测试时能用 Mock Protocol 脱钩真实服务
> 3. beta+ 服务化后只需换注入实现（HTTP Client / Remote Proxy），FLE 本体零改动
