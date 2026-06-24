---
module_id: KE-4112
title: 4.3 HTTP API（beta 预留骨架）
category: module_blueprint
---

# 4.3 HTTP API（beta 预留骨架）

4.3 HTTP API（beta 预留骨架）

| Method + Path | 对应库方法 |
|---------------|-----------|
| `POST /v1/validate/input` | `validate_input()` |
| `POST /v1/validate/output` | `validate_output()` |
| `POST /v1/scan/secrets` | `scan_secrets()` |
| `POST /v1/inspect/patterns` | `inspect_patterns()` |
| `POST /v1/schemas/{schema_id}` | `register_schema()` |
| `POST /v1/strictness/bump` | `bump_strictness()` |
| `GET /v1/strictness` | `get_strictness()` |
| `GET /v1/stats` | `stats()` |

---
