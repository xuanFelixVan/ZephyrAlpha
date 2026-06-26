---
module_id: KE-973
title: 6.1 自动检测项
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 6.1 自动检测项

6.1 自动检测项

以下违规可通过 CI/pre-commit 自动检测：

| 检测项 ID | 违规描述 | 检测方法 | 严重级别 |
|----------|---------|---------|---------|
| NUM-V01 | Mermaid 图中使用 docs 目录编号作为节点 ID | 正则匹配 `\b(0[0-9]\|1[0-9]\|99)_[a-z]` 在 `.mmd` 文件中 | ERROR |
| NUM-V02 | 蓝图 frontmatter `layer` 字段使用 docs 目录编号 | 检查 `layer:` 值是否匹配 `l{xx}_*` 或合法特殊分区 | ERROR |
| NUM-V03 | 施工图文件名不以 `construction-plan-l{xx}-` 或 `construction-plan-fe-` 或 `construction-plan-shared-` 开头 | 文件名正则 | WARNING |
| NUM-V04 | `src/zephyr/` 下目录名不匹配 `l{xx}_{snake_case}` 或 `shared` | 目录名正则 | ERROR |
| NUM-V05 | 模块 ID 不匹配 `L{XX}-{ABBR}-{NNN}` 格式 | frontmatter `module_id` 正则 | WARNING |
| NUM-V06 | 架构文档正文中使用 "09 数据平台" 等旧编号指代架构层 | 正则匹配已废弃的 docs 编号+业务域名称组合 | WARNING |
