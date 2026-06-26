---
module_id: KE-1444----p0-000
title: 12.6 Strictness 管理 P0
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 12.6 Strictness 管理 P0

12.6 Strictness 管理 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-ST-1 | bump_strictness(0.2, ttl=60min) 生效 | current=1.2 |
| P0-ST-2 | TTL 到期回默认 | current=1.0 |
| P0-ST-3 | 多次 bump 叠加 | 累积；每条 delta 独立 TTL |
