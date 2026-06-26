---
module_id: KE-4222---ct-----mock-000
title: 8.3 每个CT-*契约的mock策略
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 8.3 每个CT-*契约的mock策略

8.3 每个CT-*契约的mock策略

当AI agent只实现契约的一方时，需要用mock模拟对方。以下mock策略均在契约的`mock_strategy`字段内约定：

| CT-* | mock策略 |
|------|---------|
| CT-ORC-SCRIPT-001 | `python -c "import sys; sys.exit(0)"` 模拟脚本exit 0 |
| CT-ORC-CE-001 | 返回 `{"context": "MOCK_CONTEXT", "source_files": []}` |
| CT-ORC-VMS-001 | SQLite内存模式 `:memory:` 模拟向量存储 |
| CT-ORC-GATE-001 | 返回 `{"response": "PASS", "detail": {"gate_id": "G0", "violations": []}}` |
| CT-CE-VMS-001 | FAISS内存索引 `faiss.IndexFlatL2(768)` 模拟 |
| CT-CE-LSG-001 | 返回 `{"allowed": true, "audit_id": "mock-audit-001"}` |
| CT-KB-VMS-001 | `numpy.random.rand(3072)` 模拟embedding |
| CT-FLE-ORC-001 | 返回 `{"action": "NONE", "reason": "no anomaly detected"}` |
| CT-FLE-DB-001 | SQLite `:memory:` 模拟时序存储 |
| CT-PIPE-ORC-001 | 返回 `{"node": "M1", "status": "ready"}` |
| CT-TELE-FLE-001 | 空dict `{}` 模拟指标推送 |

---
