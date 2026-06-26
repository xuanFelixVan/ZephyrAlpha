---
module_id: KE-102
status: active
title: 10. AI 自治权限标注
category: documentation
ttl: permanent
---

# 10. AI 自治权限标注

10. AI 自治权限标注

<!-- 填写：AI 对本 playbook 的操作权限。合法值见 PS-STD-001 §10.3：
  - immutable_core：不可变核心，AI 禁止修改
  - human_gated：AI 需 Owner 批准才能修改
  - ai_editable：AI 可自主修改
-->

| 规则区域 | AI 自治权限 | 说明 |
|---------|:---:|------|
| P0 事故响应步骤 | human_gated | 核心事故响应，变更需 Owner 确认 |
| P1/P2 响应步骤 | ai_editable | AI 可自主优化操作细节 |
| 通知与上报链 | human_gated | 涉及人员联系方式，变更需确认 |
| 通用回滚方案 | human_gated | 回滚操作不可逆，需谨慎 |
