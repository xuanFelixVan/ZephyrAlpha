---
module_id: KE-1660
status: active
title: 2.1 全链路架构视图
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.1 全链路架构视图

2.1 全链路架构视图

```
┌─────────────────────────────────────────────────────────────────┐
│                     ZephyrAlpha 任务系统全链路                      │
│                                                                   │
│  ① 你提想法 → ② 草稿（多轮 AI 优化 → 最终版）                      │
│              草稿治理系统（TBD——后续独立讨论）                      │
│                          │                                        │
│                          ↓                                        │
│              ③ 蓝图真源（本蓝图格式：11 节）                         │
│                 MTH-012 涌现式设计保证血肉丰满                       │
│                          │                                        │
│                          ↓                                        │
│    ④ §11 施工指引 → 拆卡算法 → TaskCard对象 → task_repo.create()   │
│        写入 SQLite（真源） + 同步生成 changes/{feature-id}/*.md     │
│                          │                                        │
│           ┌──────────────┼──────────────┐                         │
│           ↓              ↓              ↓                         │
│     ⑤ A区生产线      ⑥ B区生产线    ⑦ C区脚本系统                  │
│     (代码生产)       (深度审计)      (横切校验)                     │
│     DeepSeek主力     GLM审查主力      MOD-INF-005                   │
│           │              │              │                         │
│           └──────────────┼──────────────┘                         │
│                          ↓                                        │
│               ⑧ 下一个循环开始                                      │
└─────────────────────────────────────────────────────────────────┘
```

> ⛔ **强制规则（RULE-ZERO-TASK）**：上图第④步是生成任务卡的**唯一合法路径**。
> 任何 AI / 工具 / 脚本 **禁止** 绕过 BlueprintDecomposer 直接生成 `.md` 任务卡文件。
> `Blueprint → Decomposer → SQLite（真源）→ .md（伴读）` ——没有其他入口。
> **历史例外**：MOD-INF-001 的 20 张卡（AI-GLM-5.1 直接产出），通过 `scripts/governance/import_task_cards.py`
> 做过一次性回填。此后全部强制走 Decomposer。
