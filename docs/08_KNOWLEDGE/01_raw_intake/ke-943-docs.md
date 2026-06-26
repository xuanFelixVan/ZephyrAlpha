---
module_id: KE-865
title: 3.3 docs 目录编号保留规则
category: governance
ttl: permanent
---

# 3.3 docs 目录编号保留规则

3.3 docs 目录编号保留规则

docs 目录编号（00-19, 99）**仅在以下场景中合法使用**：

| 合法场景 | 示例 |
|---------|------|
| 文件系统路径引用 | `docs/09_data_platform/data-sources/` |
| 信息架构视图内部讨论 | "09 号抽屉存放数据平台文档" |
| `_index.yaml` 或 index.md 中的目录导航 | 目录索引条目 |

**禁止场景**：

| 禁止场景 | 错误示例 | 正确替代 |
|---------|---------|---------|
| Mermaid 架构图节点 | `node_09[Data Platform]` | `node_L00[L00 Data Source]` |
| ADR 中引用架构层 | "影响 09 数据平台" | "影响 L00 Data Source 层" |
| 蓝图 frontmatter 的 layer 字段 | `layer: 09_data_platform` | `layer: l00_data_source` |
| 施工图命名 | `construction-plan-09-data.md` | `construction-plan-l00-data-source.md` |
| 模块 ID 前缀 | `09-DP-001` | `L00-DS-001` |
| 跨文档引用架构层 | "参见 09 号抽屉的设计" | "参见 L00 Data Source 层蓝图" |
