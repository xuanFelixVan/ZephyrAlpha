---

task_id: TASK-INF-0207
task_title: "施工Phase规划与14层扩展路线执行——§5全量Phase编排"
parent_ticket: TASK-INF-0201
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§5 施工Phase规划", "§5.1 14层扩展路线"]
status: backlog
priority: P0
type: planning
estimated_effort: "4h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-07
dependencies:
  - TASK-INF-0206
tags:
  - phase-planning
  - expansion-roadmap
  - 14-layers
severity: high
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\phase_planner.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\phase_tracker.yaml"
acceptance_criteria:
  - "27个Phase全部在 phase_planner.py 中注册，含状态机（Backlog→InProgress→Done→Verified）"
  - "14层扩展路线映射到对应Phase并关联 Domain Skill 创建触发器"
  - "scaffold-0/1/2 优先级最高，test-infra/security/integrate 其次"
  - "Skill扩展预测：Phase 1=8 Skills → Phase 2=~20 → Phase 3=~50 → Final=~100"
rollback_instructions: "删除 phase_planner.py 和 phase_tracker.yaml"
context_assembly_manifest:
  blueprint_content: "§5 施工Phase规划——27个Phase从scaffold到discovery，§5.1 14层扩展路线——L00 foundation到L06 execution同步创建 Domain Skills，最终~100 Skills"
  template_version: "task-card-template.md v1.0.0"
blueprint_id: DOM-GOV-001
---


# TASK-INF-0207: 施工Phase规划系统

## 1. 任务描述

实现 §5 定义的 27 个施工 Phase 编排系统和 §5.1 的 14 层扩展路线管理。每个 Phase 有明确状态、前驱依赖、产出物和检验门禁。

## 2. 实施方案

### 2.1 Phase 状态机

```python
from enum import Enum

class PhaseStatus(str, Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    VERIFIED = "verified"
    BLOCKED = "blocked"

class Phase:
    def __init__(self, name: str, description: str, depends_on: list[str], status: PhaseStatus):
        self.name = name
        self.description = description
        self.depends_on = depends_on
        self.status = status
```

### 2.2 Phase 全量清单

| Phase | 序 | 前驱 |
|-------|---|------|
| scaffold-0 | 1 | - |
| scaffold-1 | 2 | scaffold-0 |
| scaffold-2 | 3 | scaffold-1 |
| test-infra | 4 | scaffold-2 |
| security | 5 | test-infra |
| integrate | 6 | security |
| deploy | 7 | integrate |
| lifecycle | 8 | deploy |
| autonomy | 9 | lifecycle |
| incident | 10 | autonomy |
| cold-start | 11 | incident |
| expand | 12 | cold-start |
| optimize | 13 | expand |
| compliance | 14 | optimize |
| sandbox | 15 | compliance |
| verify | 16 | sandbox |
| cross-model | 17 | verify |
| ontology | 18 | cross-model |
| prompt-eng | 19 | ontology |
| resilience | 20 | prompt-eng |
| model-evolution | 21 | resilience |
| silent-failure | 22 | model-evolution |
| xai | 23 | silent-failure |
| calibration | 24 | xai |
| context-isolation | 25 | calibration |
| consensus | 26 | context-isolation |
| cognitive | 27 | consensus |
| temperature | 28 | cognitive |
| workflow | 29 | temperature |
| cache | 30 | workflow |
| knowledge-base | 31 | cache |
| di | 32 | knowledge-base |
| guardrails | 33 | di |
| team-optimization | 34 | guardrails |
| discovery | 35 | team-optimization |

### 2.3 14层扩展

```yaml
layer_expansion:
  L00_foundation: [configuration, logging, health-check]
  L01_infrastructure: [当前全部蓝图]
  L02_factor: [factor-definition, factor-computation, factor-registry, factor-evaluation]
  L04_risk: [position-limits, stress-testing, stop-loss]
  L06_execution: [order-router, algorithmic-execution, slippage-control]
  skill_projection: "Phase1=8 → Phase2≈20 → Phase3≈50 → Final≈100"
```

## 3. 验收标准

- [ ] 35 个 Phase 全在 phase_tracker.yaml 中
- [ ] 状态机转换正确
- [ ] 14层扩展映射完整

## 4. 回滚说明

删除 `phase_planner.py` 和 `phase_tracker.yaml`。