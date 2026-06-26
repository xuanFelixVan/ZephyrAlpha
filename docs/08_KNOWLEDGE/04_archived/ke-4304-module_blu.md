---
module_id: KE-4145
title: 5.4 超时策略
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 5.4 超时策略

5.4 超时策略

| 维度类型 | 超时（单维度） | 超时（全量） |
|---------|:---:|:---:|
| 文件扫描类（D1,D2,D3,D4） | 30s | 120s |
| 内容分析类（D5,D6,D7,D8） | 60s | 240s |
| 知识/AI类（D9,D10,D11,D12） | 120s | 300s |
| **全局硬超时** | — | **600s（10分钟）** |

超时后的脚本标记为 exit code 3（脚本崩溃）——强制阻断。
