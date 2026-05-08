---
module_id: KE-module_blu-11_5_____p0__10_2_slo-000
title: 11.5 冷启动 P0（§10.2 SLO 对应）
category: module_blueprint
---

# 11.5 冷启动 P0（§10.2 SLO 对应）

11.5 冷启动 P0（§10.2 SLO 对应）

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-B1 | 冷启动端到端 ≤ 10s | 清空进程，ChromaDB 已持久化 50k chunks | 启动进程 + 首次 search | 端到端 ≤ 10s |
| P0-B2 | bulk_bootstrap 200 docs ≤ 60s | 空库 | `bulk_bootstrap(200 docs)` | ≤ 60s |
| P0-B3 | BGE-M3 懒加载 | 启动进程 | 仅 import 不调用 | 不触发模型加载（内存 < 200MB） |
