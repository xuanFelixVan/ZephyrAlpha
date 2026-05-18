---

task_id: TASK-INF-0212
task_title: "§10-§11第五六轮审计-Compliance/KYA/Sandbox+Cross-Model/Ontology/Prompt/Attention等 + D-019-14~22"
parent_ticket: TASK-INF-0211
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§10 第五轮审计-Compliance+KYA+Sandbox+Antifragility", "§11 第六轮审计-Cross-Model+Ontology+Prompt+Attention等"]
status: backlog
priority: P1
type: blind_spot_closure
estimated_effort: "12h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-07
dependencies:
  - TASK-INF-0211
decisions:
  - D-019-14
  - D-019-15
  - D-019-16
  - D-019-17
  - D-019-18
  - D-019-19
  - D-019-20
  - D-019-21
  - D-019-22
tags:
  - compliance
  - kya
  - sandbox
  - cross-model
  - ontology
severity: high
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_compliance.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_kya.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_sandbox.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_cross_model.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_ontology.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_prompt_opt.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_attention.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_idempotency.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_resilience.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_observability.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_shadow.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_contract.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_learning.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_feature_flags.py"
acceptance_criteria:
  - "§10: EU AI Act/MiFID II/SEC 613合规架构→Annex III §5高风险+5s Kill Switch+50μs审计时间戳+7年留存 (D-019-14)"
  - "§10: KYA协议→JWT凭证+四类Attestation(Identity/Authority/Principal/Auditability)+per-tool-call验证 (D-019-15)"
  - "§10: Sandbox→Docker隔离+副作用预览+Diff Preview+人类审批 (D-019-16)"
  - "§10: FIPA-ACL→REQUEST/INFORM/DELEGATE/CONFIRM四种Performative+SKILL_COMM审计事件"
  - "§11: Cross-Model→DeepSeek/GLM/Qwen/Claude/GPT-4矩阵+model_hint升级为约束 (D-019-17)"
  - "§11: Semantic Ontology→三层分类+五类关系边+规则推理引擎 (D-019-18)"
  - "§11: Prompt Engineering→Token效率+对抗鲁棒性+四维质量门禁 (D-019-19)"
  - "§11: Attention Economics→注意力权重+优先级抢占+3 Skill活跃上限 (D-019-20)"
  - "§11: Idempotency→Idempotency Key+L0-L3幂等分级+Checkpoint/Restore (D-019-21)"
  - "§11: Auto-Rollback→多信号加权评分+自动回滚<5s+per-Skill回滚 (D-019-22)"
  - "§11: Shadow Deployment+Circuit Breaker+Bulkhead+Feature Flags+Skill Deactivation 全实现"
rollback_instructions: "批量回退上述14个Python文件"
context_assembly_manifest:
  blueprint_content: "§10 第五轮审计(Compliance/KYA/Sandbox/FIPA-ACL/Antifragility/Backtesting/FormalVerification/Observability) + §11 第六轮审计(Cross-Model/Ontology/Prompt/Attention/Idempotency/Hallucination/Rollback/Shadow/Contract/Learning/CircuitBreaker/FeatureFlags/Deactivation)"
  template_version: "task-card-template.md v1.0.0"
blueprint_id: DOM-GOV-001
---


# TASK-INF-0212: 第五六轮审计盲点关闭

## 1. 任务描述

关闭 §10 第五轮审计（Compliance/KYA/Sandbox等9小节）和 §11 第六轮审计（Cross-Model到Deactivation等13小节）的盲点，实现 D-019-14~22 九项设计决策。

## 2. 关键实现

### Compliance Architecture (D-019-14)
- EU AI Act Annex III §5 高风险分类自动判定
- MiFID II RTS 6: Kill Switch 5s强制响应
- SEC Rule 613 CAT: 50μs审计时间戳精度
- 7年数据留存 + tamper-evident storage

### KYA Protocol (D-019-15)
```python
class KYAAttestation:
    IDENTITY: "Agent ID + model + version"
    AUTHORITY: "Allowed tools + permissions"
    PRINCIPAL: "Human owner + delegation chain"
    AUDITABILITY: "Session log + checkpoint hash"
```

### Cross-Model Portability (D-019-17)
- 矩阵测试: 5 models × N Skills → pass_rate对比
- model_hint 从建议升级为约束: 不支持的模型拒绝执行
- pass_rate < 70% 的组合标记为 incompatible

### Attention Economics (D-019-20)
- 3 Skill 活跃上限（SkillsBench 实证最优）
- 优先级抢占: P0 > P1 > P2
- 上下文压缩: 第4个Skill加载时压缩最早的

## 3. 验收标准

- [ ] §10 全部9小节 + §11 全部13小节盲点关闭
- [ ] D-019-14~22 全部实现

## 4. 回滚说明

`git revert`