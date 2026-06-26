---
module_id: KE-2954
status: active
title: Telemetry 内部实现约束
category: module_blueprint
ttl: permanent
---

# Telemetry 内部实现约束

Telemetry 内部实现约束

```
Telemetry(module_id) 初始化时:
  1. 自动从环境变量 / config 读取 environment
  2. 自动注册到 LifecycleManager（如果已启动）
  3. 为 metrics 子系统设置默认标签 {module: module_id, environment: env}
  4. 为 traces 子系统注入 shared.logging.TraceContext
  5. 不启动新线程——所有子系统复用 Telemetry 主进程
```
