---
module_id: KE-2152
status: active
title: 3.8 #62: BlueprintAccessFilter
category: module_blueprint
---

# 3.8 #62: BlueprintAccessFilter

3.8 #62: BlueprintAccessFilter

文件：`D:\ZephyrAlpha\src\zephyr\shared\context_assembler.py` + `D:\ZephyrAlpha\config\capacity\ai_context_policy.yaml`

- 三级访问：tier_public(AI可读) / tier_internal(仅Owner+Meta-SLO) / tier_forensic(仅取证审计)
- `filter_for_ai_context(blueprint_text)`: 正则移除敏感阈值
  - Kill Switch 90% → "[阈值信息已移除]"
  - 72h离线 → "[阈值信息已移除]"
- 设计中不应让AI知道所有阈值
