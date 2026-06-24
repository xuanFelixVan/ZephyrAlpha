---
module_id: KE-4213
title: 8. 渐进路线
category: module_blueprint
---

# 8. 渐进路线

8. 渐进路线

| Phase | 范围 | 验收标准 |
|:-:|------|---------|
| **scaffold**（当前） | 接口规范定稿（本文档） | KBG-0016 Active + 接口规范 Active |
| **experimental** | `InProcessVectorMemory` 实现 + `bulk_bootstrap` 200+ 文档首次导入 | ① §11 P0 用例全通过<br>② 导入 `docs/**/*.md` 全量成功<br>③ Context Engine `multi_search` p50 < 200ms |
| **beta** | git post-commit hook 接 `sync_document` + MCP Server 重构 | ① commit 后 5s 内增量入库<br>② MCP `knowledge_base_server.py` 调用转发到 `get_vm()` |
| **beta** | `RemoteVectorMemory` 独立服务（按需触发才启动） | 触发条件满足时启动；业务层切 factory 即可，零重写 |
| **stable** | gRPC 升级（按需） | RPS > 500 时 |

---
