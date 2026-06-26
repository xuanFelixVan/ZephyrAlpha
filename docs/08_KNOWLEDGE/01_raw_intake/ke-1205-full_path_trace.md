---
module_id: KE-1119--------full-path-trace-003
status: active
title: DOC-004：完整路径引用（Full Path Traceability）
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# DOC-004：完整路径引用（Full Path Traceability）

DOC-004：完整路径引用（Full Path Traceability）

所有文件间的引用必须使用完整绝对路径，禁止使用相对路径或仅使用 module_id 引用。

- **规则**：引用格式为 `../../../01_policies_and_standards/{子路径}\{文件名}.md`（GOV-XXX-NNN）。同时提供路径和 module_id。
- **违反后果**：AI 无法定位引用目标，引用链断裂
- **验证方式**：`check_dead_links.py`；人工审查引用格式
- **专业参考**：ISO 27001 → Document Control / NIST 800-53 → AU-6 Audit Trail
