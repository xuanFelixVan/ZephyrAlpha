---
module_id: KE-3280
title: 10. Revision history / 修订记录
category: documentation
---

# 10. Revision history / 修订记录

10. Revision history / 修订记录

| Date | Description |
|------|-------------|
| 2026-05-01 | **v2.2.0**：结构清理 — 融入 `by-domain/src-domain/` 三个详解文件（OCP 扩展点 + ACL 三段架构 + Vendor Registry 设计原则、容错策略矩阵 + 降级优先级、幂等设计与 Idempotency Guard 实现），合并到 §4.4 和 §8。删除 by-domain/ 目录。移除已冗余的 §4.5。 |
| 2026-04-24 | **v2.1.0**：B-d-2 — 追加 §4A Vibe Coding 2.0 Infrastructure / 6 大核心服务（L12 跨层支撑）。含服务清单+依赖 DAG+与 14 层集成模式+5 个 Protocol 扩展点+命名约定说明。架构真源：本视图 §4A。 |
| 2026-04-21 | **v2.0.0**：Architecture-as-Code 重组织——模块属性详情迁移至 `architecture-model/` 联邦 YAML 模型，视图正文从 1076 行压缩至 ≤600 行，保留设计理由+层间关系叙事+核心决策。 |
| 2026-04-19 | v1.10.0：新增 §4.0 Runtime Plane Attribution Index（R69/KBG-0011）。 |
| 2026-04-19 | v1.8.0-v1.9.1：批次 D 深加工（C4-L3 三图 + Vendor Registry + 容错矩阵 + 幂等设计）+ J0-sync（L10 ai_security + L11 scout）。 |

> 完整修订历史：`git log --oneline -- application_architecture.md`

---
