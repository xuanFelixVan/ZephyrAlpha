---
module_id: KE-module_blu-3_1-000
title: 3.1 从"事后检测"到"全生命周期去重+健康监控"
category: module_blueprint
---

# 3.1 从"事后检测"到"全生命周期去重+健康监控"

3.1 从"事后检测"到"全生命周期去重+健康监控"

```
                        ┌─────────────────────────────────────────────────┐
                        │              代码去重全生命周期                     │
                        │                                                  │
                        │  ① 生成时预防  ──→  ② 提交时拦截  ──→  ③ 定期扫描    │
                        │   (Prevent)        (Block)          (Audit)       │
                        │       │                │                │         │
                        │       │    ┌───────────┴───────────┐    │         │
                        │       │    │  ④ 自动修复 (Fix)     │    │         │
                        │       │    │  ⑤ SSoT注册 (Register)│    │         │
                        │       │    │  ⑥ 进化沉淀 (Evolve)  │    │         │
                        │       │    └───────────────────────┘    │         │
                        │       │                                  │         │
                        │       └──────────  ⑦ 健康监控  ─────────┘         │
                        │                  (Health Monitor)                 │
                        └─────────────────────────────────────────────────┘
```

| 阶段 | 触发时机 | 做什么 | 成本 | 防重效果 |
|:---:|---------|------|:---:|:---:|
| **① Prevent** | 每次 AI session 开始 | Context Engine 注入"共享API影子清单" + 渐进式三层记忆注入 | 0 token（已在内） | ★★★★★ |
| **② Block** | Pre-commit | 增量扫描变更文件 → 命中已知重复模式 → BLOCKED（Wave 1 即落地阻断！） | ~2s | ★★★★★ |
| **③ Audit** | 每周 / 每 N 个 commit | 全量 MinHash + AST 深度扫描 | ~30s | ★★★ |
| **④ Fix** | Audit 后 or 手动 `--fix` | 高置信度重复自动提取→替换→验证（含ROI评估排序 + **Doom Loop检测**——3次失败→停止+告警） | ~60s | ★★★★ |
| **⑤ Register** | Fix 后自动 | 提取的函数注册到 shared + 更新 AGENTS.md | ~1s | ★★★★★ |
| **⑥ Evolve** | 定期批处理 | 重复模式→FLE→evolve()→EvolutionProposal | ~5s | ★★★ |
| **⑦ Monitor** | 每次扫描后自动 | 更新代码健康仪表盘（Dedup Health Score + 趋势 + 健忘热点）→ 写入 Session Log（Wave 1 即落地交接！） | ~1s | — |
| **⑧ Self-Protect** | 每次全量扫描后自动 + 每周 | 引擎扫描自身源码去重 + **Codegen覆盖检测**（BLIND-CODGEN-INIT-OVERWRITE）——吃自己的狗粮 | ~3s | — |
| **⑨ Lifecycle Manage** | 每月 / shared 函数 > 50 时 | 共享函数生命周期巡检（Deprecation→Grace Period→Sunset→Retirement）+ Import表面积负债评分 | ~5s | ★★ |
| **⑩ Anti-Degrade** | 每次扫描后自动 | Doom Loop日志分析 + 设计模式白名单更新 + 幂等性自校验 + 冷启动性能基准 | ~2s | — |
