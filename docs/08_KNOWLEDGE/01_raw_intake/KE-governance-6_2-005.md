---
module_id: KE-governance-6_2-005
title: 6.2 分类规则
category: governance_rule
---

# 6.2 分类规则

6.2 分类规则

1. 每条规则必须且只能有一个 stability
2. stability 决定了变更的审批门槛：
   - `frozen`：Owner 批准 + ADR
   - `stable`：领域负责人批准
   - `evolving`：正常变更流程
3. stability 与 `ai_autonomy` 的关系（正交维度，非硬绑定）：
   - `frozen` → `ai_autonomy: immutable_core`（冻结文件 AI 不可修改）
   - `stable` → `ai_autonomy: human_gated` 或 `immutable_core`（均合法，取决于内容敏感度）
   - `evolving` → `ai_autonomy: ai_modifiable` 或 `human_gated`（均合法）
