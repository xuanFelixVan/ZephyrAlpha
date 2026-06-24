---
module_id: KE-4075-------dx-000
title: 3c. 模块集成 DX：统一接入点 🆕
category: module_blueprint
---

# 3c. 模块集成 DX：统一接入点 🆕

3c. 模块集成 DX：统一接入点 🆕

> **B29 修复**——v0.6.0 新增。九个子系统各自定义了 `report()`、`emit()`、`get_logger()` 等不同 API。AI 每给一个新模块加遥测都要查阅九份文档。统一门面类的设计原则：**一行 `Telemetry(module_id)` 获得全部能力，AI 不需要记忆子系统 API。**
