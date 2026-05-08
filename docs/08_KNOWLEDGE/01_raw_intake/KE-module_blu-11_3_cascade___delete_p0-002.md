---
module_id: KE-module_blu-11_3_cascade___delete_p0-002
title: 11.3 Cascade & Delete P0
category: module_blueprint
---

# 11.3 Cascade & Delete P0

11.3 Cascade & Delete P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-C1 | cascade=supersede 默认 | ADR v1 已入库 | `update_document(..., cascade=SUPERSEDE)` | 旧 chunks 保留，metadata.superseded_by 指向新；默认 search 权重降至 0.1 |
| P0-C2 | cascade=delete 物理删除 | doc 已入库 | `update_document(..., cascade=DELETE)` | 所有 chunks 物理删除，search 无命中 |
| P0-C3 | cascade=merge 合并语义 | 两 doc content_hash 相同 | `update_document(old_id, ..., cascade=MERGE)` | old_id 标记 merged_into=new_id，gc 后物理删除 |
| P0-C4 | cascade=reorder 元数据更新 | 任务卡 doc | `update_document(..., cascade=REORDER, new_metadata={"task_deps":...})` | chunks 不动，仅 metadata 更新 |
| P0-C5 | soft delete 默认不返回 | doc 已入库 | `delete_document(id, mode="soft")` → search | search 不返回；`gc()` 后硬删除 |
