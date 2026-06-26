---
module_id: KE-3624
title: 7.3 可脚本化的部分
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 7.3 可脚本化的部分

7.3 可脚本化的部分

| 检查项 | 脚本实现难度 | 建议实现位置 |
|--------|:---:|------|
| doc_type 是否在词表中 | ⭐ 容易 | GATE-11 pre-commit（已实现） |
| doc_type 是否匹配目录 | ⭐ 容易 | GATE-11 pre-commit（已实现） |
| 文件名后缀是否匹配 doc_type | ⭐ 容易 | GATE-11 N-08 新规则 |
| index.md 文件清单 vs 磁盘实际文件 | ⭐⭐ 中等 | `scripts/governance/check_index_integrity.py` |
| 内容关键词 vs doc_type（如 content 含"Step" 但 doc_type=policy） | ⭐⭐⭐ 较难 | `scripts/governance/scan_deep_content.py`（启发式，需人工复核） |
| 全文内容 vs doc_type 匹配 | ⭐⭐⭐⭐ 困难 | 人工审查 + AI 辅助（V5） |

> **大白话**：前三个检查项是机器干的活——脚本一秒扫完。最后两个才是你刚刚让我做的事情——打开文件看内容，判断它到底是不是它声称的那个类型。这个过程没有办法完全自动化，因为"内容像不像规则"需要理解上下文。但前三个检查项做好了，人工审查的工作量就从 70+ 个文件缩减到 3~5 个可疑文件。

---
