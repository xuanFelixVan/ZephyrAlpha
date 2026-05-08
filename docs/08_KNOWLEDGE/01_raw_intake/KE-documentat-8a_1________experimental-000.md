---
module_id: KE-documentat-8a_1________experimental-000
title: 8A.1 服务生命周期（experimental 单机单进程）
category: documentation
---

# 8A.1 服务生命周期（experimental 单机单进程）

8A.1 服务生命周期（experimental 单机单进程）

```
系统启动 (python -m zephyr.orchestrator.bootstrap)  # 未来实现点，LPC 双轨下由 Orchestrator 启动 DAG
   │
   ▼
1. 加载 vibe_config.yaml
   │
   ▼
2. 按依赖顺序启动（DAG 序）：
      LSG  →  VMS  →  CE  →  Orc  →  FLE
      （每个服务 health check 通过才启动下一个）
   │
   ▼
3. FLE 订阅全部服务的 metrics channel
   │
   ▼
4. 服务 Ready → Agent 可消费

系统停止 (Ctrl+C / SIGTERM)
   │
   ▼
反向停止顺序：FLE → Orc → CE → VMS → LSG
   （每个服务完成 in-flight 任务后退出）
```
