---
module_id: KE-286
title: 3.3 Network boundary / 网络边界
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3.3 Network boundary / 网络边界

3.3 Network boundary / 网络边界

| 边界 | 方向 | 协议 | 安全考量 |
|------|------|------|---------|
| Host → Market Data Provider | 出站 | HTTPS REST / WSS | API Key（本地 `.env`，不入 Git） |
| Host → Broker API | 出站 | HTTPS REST / TCP FIX | API Key + IP 白名单 |
| Host → LLM Providers | 出站 | HTTPS REST | API Key（本地 `.env`） |
| Host → Feishu Webhook | 出站 | HTTPS REST | Webhook Secret |
| Inbound（无） | — | — | 当前无入站监听 |

---
