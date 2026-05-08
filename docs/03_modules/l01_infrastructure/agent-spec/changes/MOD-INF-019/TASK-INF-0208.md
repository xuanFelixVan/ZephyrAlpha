---
task_id: TASK-INF-0208
task_title: "§6风险矩阵全量缓解实现——R1-R65+风险项对应缓解措施落地"
parent_ticket: TASK-INF-0205
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§6 风险与缓解"]
status: backlog
priority: P0
type: risk_mitigation
estimated_effort: "6h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-07
dependencies:
  - TASK-INF-0205
tags:
  - risk-mitigation
  - risk-matrix
  - R1-R65
severity: critical
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_risk_mitigator.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\risk_tracker.yaml"
acceptance_criteria:
  - "R1(R1蓝图Skill漂移): freshness_score机制 + CI门禁自动降分 + 降分超阈值触发重审 —— 已实现"
  - "R2(Skill指令模糊): 强制Checklist格式 + 反馈环对接记录模糊失败 —— 已实现"
  - "R3(Domain Skill爆炸): Factory Agent自举 + freshness优先级排序 —— 已实现"
  - "R4(多Skill组合冲突): Domain > Role优先级规则 + 冲突检测脚本 —— 已实现"
  - "R5(AGENTS.md膨胀): 触发表≤30条 + 溢出拆分 trigger_table.yaml —— 已实现"
  - "R6(Token预算超限): Progressive Disclosure + 组合≤800 tokens + 超降自动降级 —— 已实现"
  - "R7(跨session丢失进度): Session Resume协议 + 卸载时写入结构化摘要 —— 已实现"
  - "R8(Factory质量不一): 模板驱动 + 人工审查 + gate格式校验 —— 已实现"
  - "R9(多模型理解不同): model_hint推荐模型 + 结构化表格>散文 —— 已实现"
  - "R10(Skill注入攻击): Defense in Depth四层防护 + LLM Security + Skill哈希校验 —— 已实现"
  - "R11(Skill链死锁): Chain depth limit=3 + 循环检测O(1) —— 已实现"
  - "R12(上下文碎片化): Skill Compact合并 + Attention Weighting权重标注 —— 已实现"
  - "R13(Canary评估失效): ramp 50% + Welch's t-test p<0.05 —— 已实现"
  - "R14(Cross-IDE翻译失真): SSOT AGENTS.md + schema valid + diff test —— 已实现"
  - "R15(评估不可靠): Spearman ρ≥0.80 + 不达标人工审查 —— 已实现"
  - "R16(成本无边): Skill Economics + Budget Enforcer + 模型路由优化 —— 已实现"
  - "R17(废弃Skill腐烂): Deprecation四阶段 + 自动过期触发 —— 已实现"
  - "R18(AI自主修改致门禁下降): Autonomy Spectrum L0-L4 + CI门禁阻断 + auto-revert —— 已实现"
  - "R19(事故无法追溯Skill): Incident Postmortem Engine闭环 —— 已实现"
  - "R20(目录损坏被删): GitOps DR + 每日备份验证 + SHA256 corrosion detection —— 已实现"
  - "R21(冷启动过长): Onboarding Skill前三session + Session Warm-up —— 已实现"
  - "R22(双语Skill不一致): 双语对照字段 + 跨模型 pass_rate 差异≤5% —— 已实现"
  - "所有65项风险都有对应的自动化检测/缓解/告警机制"
rollback_instructions: "回退 skill_risk_mitigator.py 和 risk_tracker.yaml"
context_assembly_manifest:
  blueprint_content: "§6 风险与缓解——R1-R65 风险矩阵，含概率/影响/缓解措施"
  template_version: "task-card-template.md v1.0.0"
---

# TASK-INF-0208: 风险矩阵全量缓解

## 1. 任务描述

为 §6 风险矩阵中的全部 65 个风险项（R1-R65）创建自动化缓解措施和追踪系统。每个风险项必须有对应的检测逻辑、缓解动作和告警机制。

## 2. 实施方案

### 2.1 风险自动缓解引擎

```python
class RiskMitigator:
    def __init__(self):
        self.risks = self._load_risk_registry()

    def evaluate_all(self) -> list[RiskEvaluation]:
        results = []
        for risk_id, risk_def in self.risks.items():
            probability = self._assess_probability(risk_id, risk_def)
            impact = risk_def["impact"]
            score = probability * impact
            if score > self.THRESHOLD:
                self._trigger_mitigation(risk_id, risk_def, score)
            results.append(RiskEvaluation(risk_id, probability, impact, score))
        return results
```

### 2.2 顶级风险关键缓解

| Risk | Prob | Impact | Key Mitigation |
|------|:---:|:---:|---------------|
| R1 | 高 | 高 | freshness_score自动降分+CI门禁 |
| R6 | 中 | 高 | Progressive Disclosure+超降降级 |
| R7 | 高 | 中 | Session Resume协议 |
| R10 | 低 | 高 | Defense in Depth四层+哈希校验 |
| R11 | 中 | 高 | Chain depth=3+循环检测 |
| R12 | 高 | 中 | Attention Weighting+Skill Compact |
| R16 | 高 | 高 | Economics+Budget强制约束 |
| R18 | 中 | 高 | Autonomy Spectrum+CI阻断+auto-revert |
| R19 | 高 | 高 | Postmortem Engine闭环 |
| R20 | 低 | 高 | GitOps DR+SHA256 |

## 3. 验收标准

- [ ] 65 个风险项全部注册到 risk_tracker.yaml
- [ ] 自动评估/缓解/告警机制可用
- [ ] 高风险项(P=高/I=高)有实时监控

## 4. 回滚说明

删除 `skill_risk_mitigator.py` 和 `risk_tracker.yaml`。
