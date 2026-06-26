---
module_id: KE-3892--------3-------owasp-ll-005
title: 13.7 F. 安全与治理（3个）——对标 OWASP LLM + AWS Secrets Manager
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 13.7 F. 安全与治理（3个）——对标 OWASP LLM + AWS Secrets Manager

13.7 F. 安全与治理（3个）——对标 OWASP LLM + AWS Secrets Manager

> **现状**：蓝图有 CBAC 校验 + input_sanitizer + AI 自治级别绑定。但向量层面的数据泄漏和审计追溯不完整。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 20 | **V-VMS-420** | **无向量嵌入中的 PII/敏感信息检测**——ChromaDB 存储原文 + 向量，embedding 可以部分还原原文信息。需要写入前 scan：API keys/Token/私钥/个人身份信息 | 4 | 2 | 4 | 32 🔴 | 日志/代码写入向量DB |
| 21 | **V-VMS-421** | **无检索操作的完整审计链**——谁(哪个session/AI)、何时、检索了什么查询、得到了哪些结果、最终用了哪条。没有这个审计链，Owner 无法追溯"AI为什么做了那个决策" | 3 | 3 | 3 | 27 🟠 | 事后复盘 |
| 22 | **V-VMS-422** | **无 Collection/文档级 RBAC**——`rules` 应仅 Governance 写入，`decisions` 应仅 Orc 写入。当前蓝图有 AI 自治级别（§2最后一列）但无运行时强制执行。需要 CBAC 与 Collection 操作绑定的硬校验 | 2 | 3 | 3 | 18 🟡 | 新AI session接入 |
