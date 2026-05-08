---
task_id: TASK-INF-0205
task_title: "跨模块八项集成实现——AuditTrail/Rollback/FeedbackLoop/RBAC/Budget/Script/Escalation/KB"
parent_ticket: TASK-INF-0201
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§3.1-3.8 跨模块集成设计"]
status: backlog
priority: P0
type: integration
estimated_effort: "12h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-07
dependencies:
  - TASK-INF-0201
  - MOD-INF-020 (audit-trail)
  - MOD-INF-021 (rollback)
  - MOD-INF-010 (feedback-loop)
  - MOD-INF-018 (rbac)
  - MOD-INF-024 (budget-enforcer)
  - MOD-INF-005 (script-system)
  - MOD-INF-022 (escalation)
  - MOD-KB-001 (knowledge-base)
tags:
  - integration
  - cross-module
  - audit-trail
  - rollback
  - feedback-loop
severity: critical
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\feedback-loop\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\escalation\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_executor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_freshness.py"
acceptance_criteria:
  - "Audit Trail: skill_loaded/skill_applied/skill_drift_detected/skill_unloaded 四种事件写入 MOD-INF-020"
  - "Rollback: Skill 加载前自动创建 Checkpoint，门禁 FAIL 自动rollback，格式 skill_{skill_id}_{timestamp}"
  - "Feedback Loop: predict→detect→diagnose→act→verify 五阶段闭环对接 MOD-INF-010"
  - "RBAC: 每 Skill allowed-tools 注入 AGENTS.md 上下文，read_only/code_modify/admin 三级权限"
  - "Budget: L1(~50tokens always loaded), L2(≤800tokens combined), L3(≤8000tokens per file), 超预算自动降级"
  - "Script System: Skill 脚本输出(exit code+stdout)被全局采集为 Finding，统一 exit code: 0=pass/1=fail/2=warning/3=error"
  - "Escalation: 轻量/中度/重大三级升级路径对接 MOD-INF-022"
  - "KB: Skill→KB 自动生成KE草稿，KB→Skill(≥5次引用+可执行)升级为指令，双向freshness同步"
rollback_instructions: "回退 skill_executor.py 和 skill_freshness.py 到集成前版本"
context_assembly_manifest:
  blueprint_content: "§3 跨模块集成——Agent Spec 不是孤立模块，与已有八个模块深度集成"
  template_version: "task-card-template.md v1.0.0"
---

# TASK-INF-0205: 跨模块八项集成

## 1. 任务描述

实现 §3.1-3.8 定义的八项跨模块集成：Audit Trail、Rollback、Feedback Loop、RBAC、Budget Enforcer、Script System、Escalation Protocol、Knowledge Base。

## 2. 实施方案

### 2.1 Audit Trail 集成

| Skill 事件 | Audit Entry Type | 内容 |
|-----------|-----------------|------|
| skill_loaded | AI_ACTION(type_id=1) | skill_id + domain + role + trigger_reason + timestamp |
| skill_applied | TASK_COMPLETE(type_id=3) | skill_id + execution_steps + artifact_hash + gate_result |
| skill_drift_detected | ANOMALY(type_id=6) | skill_id + drift_type + drift_diff + freshness_score |
| skill_unloaded | AI_ACTION(type_id=1) | skill_id + execution_summary + next_step → Session Resume |

### 2.2 Rollback 集成

```yaml
skill_checkpoint:
  rule: "Skill 加载前自动创建 Checkpoint, Skill 卸载时门禁 FAIL 自动 rollback"
  checkpoint_name_format: "skill_{skill_id}_{timestamp}"
  rollback_trigger:
    - "Skill 执行后门禁 FAIL (G0-G7 任一)"
    - "Skill 产出代码导致下游测试 FAIL"
    - "Skill 执行中 AI 主动请求回滚"
  post_rollback_action: "降级 Skill freshness_score → 触发人工审查"
```

### 2.3 Feedback Loop 集成

```python
class SkillFeedbackLoop:
    def predict(skill_id: str) -> float: ...
    def detect(skill_id: str) -> GateResult: ...
    def diagnose(skill_id: str) -> RootCauseAnalysis: ...
    def act(skill_id: str) -> AutoFixSuggestion: ...
    def verify(skill_id: str, fix: AutoFixSuggestion) -> bool: ...
```

### 2.4 RBAC 集成

```yaml
permission_levels:
  read_only: {tools: [Read, Grep, Glob, Bash(readonly), mcp__context_retrieval], example: "drift-detector"}
  code_modify: {tools: [Read, Grep, Glob, Edit, Write, Bash], example: "database-specialist"}
  admin: {tools: [Read, Grep, Glob, Edit, Write, Bash, Execute], example: "governor, implementer"}
enforcement: "SkillLoader 加载时检查 allowed-tools → 注入 AGENTS.md 上下文"
```

### 2.5 Budget Enforcer 集成

```yaml
skill_budget:
  per_skill:
    L1_metadata: "~50 tokens (always loaded, 不计入 Skill 预算)"
    L2_body: "~300-500 tokens (Domain) / ~200-300 tokens (Role)"
    L3_references: "~2000-8000 tokens per file (按需, 计入会话预算)"
  combined_budget: "Domain L2 + Role L2 ≤ 800 tokens"
  over_budget_action: "自动降级——只加载 L1 metadata + L2 CRITICAL 规则, L3 全跳过"
```

## 3. 验收标准

- [ ] 八项集成全部实现且通过端到端测试
- [ ] 回滚触发条件全部覆盖且执行 < 5s
- [ ] Token 预算强制生效

## 4. 回滚说明

`git revert <integration_commit>`
