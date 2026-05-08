---
module_id: KE-module_blu-2_2_b_______m6-m11-002
title: 2.2 B区：审计管线（M6-M11）
category: module_blueprint
---

# 2.2 B区：审计管线（M6-M11）

2.2 B区：审计管线（M6-M11）

| 节点 | 职责 | 模型 | Sandbox | Gate |
|:---:|------|------|:---:|:---:|
| **M6** | 差异检测——产出 vs 期望（AP2边界标记） | DeepSeek V4 Pro | standard | pre_commit_only |
| **M7** | 深度审查——逐个文件逻辑/合规 | GLM-5.1 | audit | full_g0_g7 |
| **M8** | 标准合规——PS/GOV/ADR | DeepSeek V4 Pro | standard | post_exec_only |
| **M9** | 风险评估——OWASP LLM Top 10 | DeepSeek V4 Pro | standard | post_exec_only |
| **M10** | 审计报告→Finding 格式 | DeepSeek V4 Pro | standard | post_exec_only |
| **M11** | 门禁裁决——G5/G6 | DeepSeek V4 Pro | restricted | none |
