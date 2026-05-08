---
module_id: KE-module_blu-phase_2_8_collection-003
title: Phase 2：8 Collection 落地
category: module_blueprint
---

# Phase 2：8 Collection 落地

Phase 2：8 Collection 落地

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §2 八大 Collection + §5.2 迁移映射 |
| 产出位置 | `in_process_vector_memory.py`（InProcessVectorMemory 统一入口） |
| 验收标准 | 8 个 Collection 可创建/写入/检索/删除；迁移 4 旧 Collection 数据无损 |
| G7 检查项 | Collection Schema 与蓝图 §2 一致？嵌入维度正确？WriteTrace 每条都有？ |

**迁移顺序**：
1. 先建 `rules` / `blueprints` / `knowledge` / `lessons` —— 从现有 Collection 迁移数据
2. 再建 `decisions` / `code_context` / `session_snapshots` / `execution_traces` —— 全新创建
3. BridgeLayer 双读期间（Phase 2-3 过渡）保持兼容
4. 迁移完成后冻结 `kb/chromadb_init.py`（标记 deprecated，不再新增写入）
