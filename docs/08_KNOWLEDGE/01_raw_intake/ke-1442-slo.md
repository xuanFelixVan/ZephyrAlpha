---
module_id: KE-1352-----slo-000
status: active
title: 10.2 冷启动 SLO（首次启动 / 重启后首次调用，补充）
category: module_blueprint
---

# 10.2 冷启动 SLO（首次启动 / 重启后首次调用，补充）

10.2 冷启动 SLO（首次启动 / 重启后首次调用，补充）

> **为什么必须量化**：个人量化系统高频场景——每天开电脑第一次启动。不快就是用户体验灾难。

| 指标 | 目标 | 说明 |
|------|------|------|
| 进程冷启动（不含 BGE-M3 加载） | ≤ 3 s | import + 配置解析 |
| BGE-M3 模型首次加载 | ≤ 5 s | ONNX Runtime 加载 + warmup 1 条 embedding |
| 首次 `search()` 延迟（冷缓存） | ≤ 2 s | 含 ChromaDB 打开持久化文件 |
| 首次 `multi_search()` 延迟（冷缓存） | ≤ 3 s | 4 个 Collection 首次打开 |
| **总冷启动到首次可用** | **≤ 10 s** | 进程启动 + 模型加载 + ChromaDB 打开 + warmup 查询 |
| `bulk_bootstrap(200 docs)` 端到端 | ≤ 60 s | 首次部署场景 |

**冷启动优化要求**：
- BGE-M3 懒加载（首次调用时才加载，而非 import 时）
- ChromaDB collection 懒打开（首次检索对应 collection 时才 open）
- 启动完成后记录 `logs/vms_startup.log`，供运维比对

---
