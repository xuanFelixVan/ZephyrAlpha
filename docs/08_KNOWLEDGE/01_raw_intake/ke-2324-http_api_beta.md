---
module_id: KE-2229
status: active
title: 4.2 HTTP API（beta 按需启用，预留骨架）
category: module_blueprint
ttl: permanent
---

# 4.2 HTTP API（beta 按需启用，预留骨架）

4.2 HTTP API（beta 按需启用，预留骨架）

**现在不实现**，但固化 URL 与 schema，`RemoteVectorMemory` 将严格对齐：

| Method + Path | 对应库方法 |
|---------------|-----------|
| `POST /v1/ingest` | `ingest()` |
| `POST /v1/ingest/bootstrap` | `bulk_bootstrap()` |
| `POST /v1/sync` | `sync_document()` |
| `PATCH /v1/documents/{doc_id}` | `update_document()` |
| `DELETE /v1/documents/{doc_id}?mode=&cascade=` | `delete_document()` |
| `POST /v1/search` | `search()` |
| `POST /v1/search/multi` | `multi_search()` |
| `GET /v1/documents/{doc_id}` | `get_by_id()` |
| `GET /v1/stats` | `stats()` |
| `POST /v1/reindex` | `reindex()` |
| `POST /v1/gc` | `gc()` |

HTTP 请求 / 响应 schema = 库方法入参 / 出参的 Pydantic JSON 序列化形式。

---
