---
module_id: KE-638-----------------canoni-005
status: active
title: Stage 9：从"脚本位置未决"到"记忆系统 canonical 落位确定"
category: documentation
ttl: permanent
---

# Stage 9：从"脚本位置未决"到"记忆系统 canonical 落位确定"

Stage 9：从"脚本位置未决"到"记忆系统 canonical 落位确定"

本轮讨论追溯了 OQ-010（异步流水线脚本位置）的依赖链，发现其最底层依赖是 OQ-001（记忆系统 canonical 物理落位）。

因此优先确定了记忆系统的物理落位方案：

1. **核心原则**：分散存储 + 集中索引，避免双真源
2. **索引层**：`08_ai_engineering_and_agent_ops/memory-and-context/` 内部按语义分类
   - `decision-memory/` —— 决策记忆索引（ADR、关键决策、依赖追踪）
   - `operational-memory/` —— 操作记忆索引（session logs、执行轨迹）
   - `knowledge-memory/` —— 知识记忆索引（链接到 15_knowledge_base/）
   - `context-services/` —— 上下文服务能力（装配、交接、检索接口）
   - `memory-governance/` —— 记忆治理（schema、质量闸门、留存策略）
3. **全文层**：各业务域（02/15/18 等）存实际文档，记忆系统只存索引和元数据
4. **状态管理**：candidate/raw/active/superseded 用索引层状态字段，不按目录分

这一落位方案符合机构标准（"按域分放，不用单一记忆层堆全文"），为后续确定脚本位置、Session Log 路径、数据流设计提供了基础。
