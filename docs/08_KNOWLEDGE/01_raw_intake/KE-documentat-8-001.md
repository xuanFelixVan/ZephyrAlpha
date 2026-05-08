---
module_id: KE-documentat-8-001
title: 8. 双轨/下沉结构（已退役）
category: documentation
---

# 8. 双轨/下沉结构（已退役）

8. 双轨/下沉结构（已退役）

> **2026-05-01 更新**：原 `by-domain/` 双轨结构已于 README v2.0.0 统一移除。所有原计划下沉到 `by-domain/frontend-domain/` 的内容已吸纳入本视图及 `architecture-model/` YAML 联邦模型。以下触发清单保留为历史参考，实际落地不再依赖独立 by-domain 目录。

**下沉触发条件（历史记录）**：

| 触发 | 动作 |
|------|------|
| 03-AA §frontend 章节 > 800 行 | 下沉到 `frontend-domain/architecture.md` |
| 实际开始建 `frontend/` 仓 | 新建 `module-topology.mmd` + `apps-portfolio.md` + `interfaces.md` |
| App ≥ 5 时 | 新建 `apps-portfolio.md` |
| packages ≥ 3 时 | 新建 `packages-inventory.md` |
| API 路由 ≥ 10 类时 | 新建 `interfaces.md`（OpenAPI/WebSocket Topic/Auth）|
| AI Operator 启用 | 新建 `ai-ops-frontend.md` |
