---
module_id: KE-1362
title: 10.3 降级条件速查表
category: module_blueprint
ttl: permanent
---

# 10.3 降级条件速查表

10.3 降级条件速查表

| 触发条件 | 降级动作 | 上游感知 |
|---------|---------|---------|
| VMS degraded=True | fs 兜底，bundle.degraded=True | **DEGRADE-001** |
| Qwen2.5-3B 加载失败 | 规则压缩 | **DEGRADE-002** |
| 压缩仍超 budget | 简单截断 | **DEGRADE-002b** |
| IDE 能力未知 | 静态矩阵 | 透明，无需上游处理 |
| MCP `resources`/`tools` 通道失败 | 降级到 prompts | **DEGRADE-003** |
| prompts 超 budget | 丢低优先级 slot | **DEGRADE-003b** |
| entity-graph 加载失败 | 跳过依赖图槽，仍能跑 | 日志告警，不阻塞 |

所有降级必须写入 `logs/ce_degrade.log`（结构化 JSON：触发原因 / 时间戳 / task_id / 降级码）。

---
