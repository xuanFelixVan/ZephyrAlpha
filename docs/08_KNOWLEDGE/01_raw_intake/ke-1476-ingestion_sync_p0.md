---
module_id: KE-1386---sync-p0-000
title: 11.1 Ingestion & Sync P0
category: module_blueprint
ttl: permanent
---

# 11.1 Ingestion & Sync P0

11.1 Ingestion & Sync P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-I1 | 单文档首次入库 | 空 Collection | `await vm.ingest(doc)` | 返回 `ingested`，search 能命中 |
| P0-I2 | content_hash 未变幂等 | 已 ingest | 再次 ingest 同 doc | 返回 `unchanged`，chunks_created=0 |
| P0-I3 | 内容变更 version 递增 | 已 ingest v1 | 修改 content 再 ingest | version=2，旧 chunks 被替换 |
| P0-I4 | bulk_bootstrap 断点续传 | 导 200 docs 中途 kill | 重启再调用 | checkpoint 续跑，不重入库，总耗时 < 1.5× 无中断 |
| P0-I5 | sync_document add 事件 | 新文件 | `sync_document(path, "add")` | 等价 ingest，Collection 按 §7.3 自动路由 |
| P0-I6 | sync_document delete 事件 | 已入库 | `sync_document(path, "delete")` | 等价 `delete_document(mode="hard")` |
