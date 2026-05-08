---
module_id: KE-documentat-4a_5-001
title: 4A.5 架构归属说明
category: documentation
---

# 4A.5 架构归属说明

4A.5 架构归属说明

```
src/zephyr/
├── l00_data_source/          ← 业务层（L00）
├── l01_.../                  ← 业务层
├── ...
├── l11_.../                  ← 业务层（L11）
├── l13_.../                  ← 业务层（L13）
│
├── llm_security/             ← L12 跨层支撑（LSG）
├── vector_memory/            ← L12 跨层支撑（VMS）
├── context_engine/           ← L12 跨层支撑（CE）
├── orchestrator/             ← L12 跨层支撑（Orc）
├── feedback_loop/            ← L12 跨层支撑（FLE）
│
└── shared/                   ← 跨层公共契约（原有）
```

**命名约定决策**：6 大核心服务**不**使用 `l12_` 前缀，理由：

- `l12_` 前缀语义是 "编号层"；6 大核心服务是 "职能模块"，两者概念不同
- 避免与未来可能的 `l12_cross_cutting/` 命名冲突
- 与业务层 `l<NN>_` 命名视觉区分，便于快速识别 "基础设施 vs 业务"
