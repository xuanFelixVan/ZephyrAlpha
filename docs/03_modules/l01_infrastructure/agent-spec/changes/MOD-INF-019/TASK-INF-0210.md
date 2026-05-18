---

task_id: TASK-INF-0210
task_title: "§8第三轮审计-Security+Evaluation+Multi-Agent+Deployment盲点关闭(B48-B63)"
parent_ticket: TASK-INF-0206
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§8 第三轮深度审计-Security+Evaluation+Multi-Agent+Deployment"]
status: backlog
priority: P1
type: blind_spot_closure
estimated_effort: "10h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-07
dependencies:
  - TASK-INF-0206
tags:
  - third-round-audit
  - security
  - multi-agent
  - deployment
  - B48-B63
severity: high
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\02_architecture\\security\\threat-model.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_security.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_evaluator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_canary.py"
acceptance_criteria:
  - "B48-B63 共 16 个盲点全部关闭——每个盲点对应完整的检测/防护/审计机制"
  - "L1 静态验证(L1-SV-01~04): YAML合法性+工具在册+语义模糊+freshness过期"
  - "L2 轨迹测试(L2-TT-01~03): 单Skill in-vitro + 多Skill交互 + Cross-Model兼容性"
  - "L3 产出物质检(L3-EVAL-01~03): LLM-as-a-Judge 7维评估 + 人类抽样 + A/B对照"
  - "Security Threat Model: Parse/Validate/Simulate/Audit四层Defense in Depth"
  - "Multi-Agent systematic risk (herding/model homogeneity/emergent manipulation)已防护"
  - "Canary部署系统: 20%→50%→100%三步gray+Welch t-test+自动回滚"
rollback_instructions: "回退 skill_security.py, skill_evaluator.py, skill_canary.py"
context_assembly_manifest:
  blueprint_content: "§8 第三轮深度审计——Security+Evaluation+Multi-Agent+Deployment四维盲点补充，新增B48-B63共16盲点"
  decisions:
    - "D-019-06: Skill Testing & Evaluation Framework——三层评估体系"
    - "D-019-07: Skill Security Threat Model——Defense in Depth"
    - "D-019-08: Multi-Skill Chaining Protocol——循环检测+碎片化管理"
    - "D-019-09: Skill Canary Deployment——灰度三部+A/B Testing"
  template_version: "task-card-template.md v1.0.0"
blueprint_id: DOM-GOV-001
---


# TASK-INF-0210: 第三轮审计盲点关闭

## 1. 任务描述

关闭 §8 第三轮深度审计中发现的 B48-B63 共 16 个盲点，覆盖 Security Threat Model、Skill Testing Framework、Multi-Agent Chaining、Canary Deployment 四大维度。

## 2. 实施方案

### 2.1 三层评估体系 (D-019-06)

```yaml
evaluation_framework:
  L1_static:
    - SV-01: YAML合法性——frontmatter可解析
    - SV-02: 工具注册——allowed-tools均存在于 tool-registry
    - SV-03: 语义模糊——≥3条模糊指令→标记
    - SV-04: freshness过期——score<30→拒绝加载
  L2_trajectory:
    - TT-01: 单Skill in-vitro——10个标准task→pass≥8
    - TT-02: 多Skill交互——5个组合→无冲突
    - TT-03: Cross-Model——3+模型→pass rate≥70%
  L3_output:
    - EVAL-01: LLM-as-a-Judge——7维25子维130项
    - EVAL-02: 人类采样——10%的judge结果人工复核
    - EVAL-03: A/B对照——新旧Skill对比

  calibration_threshold: "Spearman ρ ≥ 0.80"
```

### 2.2 四层 Defense in Depth (D-019-07)

```
Layer 1 — PARSE: YAML frontmatter syntax check + schema validation
Layer 2 — VALIDATE: tool-call allowlist check + RBAC enforcement
Layer 3 — SIMULATE: Sandbox dry-run + side-effect preview
Layer 4 — AUDIT: full execution trace + Merkle audit trail
```

### 2.3 Multi-Skill Chaining (D-019-08)

```python
class SkillChainManager:
    MAX_DEPTH = 3

    def can_chain(self, skill_a: str, skill_b: str) -> bool:
        if self._chain_depth >= self.MAX_DEPTH:
            return False
        return not self._detects_cycle(skill_a, skill_b)

    def manage_fragmentation(self, active_skills: list):
        if len(active_skills) > 3:
            old_skill = active_skills[0]
            self._compact_and_unload(old_skill)
```

### 2.4 Canary Deployment (D-019-09)

```
Phase 1 — 20%: deploy to 20% sessions, 50 operations minimum
Phase 2 — 50%: if Welch's t-test p<0.05 + no regression, ramp
Phase 3 — 100%: full rollout after 200 operations + gate pass
Auto-rollback: error_rate > baseline × 1.5 → instant revert
```

## 3. 验收标准

- [ ] B48-B63 全 16 盲点关闭
- [ ] 三层评估体系可执行
- [ ] Defense in Depth 四层全实现
- [ ] Canary 灰度可用

## 4. 回滚说明

回退对应 Python 文件。