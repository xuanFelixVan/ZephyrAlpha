---
module_id: KE-1396
title: 11.3 施工约束
category: module_blueprint
ttl: permanent
---

# 11.3 施工约束

11.3 施工约束

| 约束 | 来源 |
|------|------|
| **LLM 预算不可超 $2.00/任务卡** | GOV-AI-002 + tool-contracts.yaml |
| **模型路由策略不可被 AI 改写** | GOV-AI-002 + Gate Engine |
| **safety_level L 的 tool 无限制；M 需确认；H 需 Owner 审批** | MOD-INF-018 + tool-contracts.yaml |
| **新增 tool 前必须先改 tool-contracts.yaml** | 本蓝图 §3.2 |
