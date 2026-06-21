---
module_id: KE-472
status: active
title: 7. AI 自治权限标注
category: documentation
---

# 7. AI 自治权限标注

7. AI 自治权限标注

<!-- 填写：AI 对本 runbook 的操作权限。合法值见 PS-STD-001 §10.3：
  - immutable_core：不可变核心，AI 禁止修改
  - human_gated：AI 需 Owner 批准才能修改
  - ai_editable：AI 可自主修改
-->

| 规则区域 | AI 自治权限 | 说明 |
|---------|:---:|------|
| 操作步骤 | human_gated | 操作步骤变更需 Owner 确认 |
| 前置条件检查 | ai_editable | AI 可自主补充检查项 |
| 回滚方案 | human_gated | 回滚操作不可逆，需谨慎 |
