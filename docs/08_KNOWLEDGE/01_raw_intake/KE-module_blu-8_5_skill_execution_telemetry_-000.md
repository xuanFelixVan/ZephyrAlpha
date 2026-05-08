---
module_id: KE-module_blu-8_5_skill_execution_telemetry_-000
title: 8.5 Skill Execution Telemetry Standard
category: module_blueprint
---

# 8.5 Skill Execution Telemetry Standard

8.5 Skill Execution Telemetry Standard

```yaml
skill_telemetry:
  description: "每个 Skill 执行必须产生的标准化遥测数据——对接 Skill Freshness + 反馈环 + 审计"

  required_fields:
    session_id: "AI 会话的唯一标识"
    skill_id: "Skill 唯一 ID（SKILL-DOM-DB-001）"
    skill_version: "Skill 的 semver 版本"
    load_timestamp: "Skill 加载时间（ISO 8601 UTC）"
    unload_timestamp: "Skill 卸载时间"
    domain_skill_id: "加载的 Domain Skill ID（可为 null）"
    role_skill_id: "加载的 Role Skill ID"
    token_consumed: "此 Skill 加载消耗的 token 数（L1+L2+L3 总计）"
    checklist_completed: "完成的 Checklist 步骤数 / 总步骤数"
    tools_invoked: "执行期间调用的工具列表 + 每个工具的调用次数"
    gate_results: "G0-G7 门禁各门 PASS/FAIL"
    human_interventions: "触发 Escalation 的次数 + 类型"
    model_used: "实际执行 Skill 的模型名称"
    model_hint_match: "是否与 Skill 指定的 model_hint 一致"
    execution_duration_ms: "Skill 从加载到卸载的总耗时"
    errors_encountered: "执行期间遇到的错误类型 + 次数"
    outcome_summary: "摘要（≤ 200 tokens）"
```
