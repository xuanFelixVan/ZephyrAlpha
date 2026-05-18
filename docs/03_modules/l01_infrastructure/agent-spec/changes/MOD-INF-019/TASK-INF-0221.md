---

task_id: TASK-INF-0221
task_title: "盲点全量关闭追踪——B1-B156共156盲点关闭状态矩阵 + 风险矩阵R1-R90追踪 + Anti-Pattern AP1-AP43防护追踪"
parent_ticket: TASK-INF-0219
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§8-§21 全部16轮审计盲点表", "§6 风险矩阵 R1-R90", "Anti-Pattern AP1-AP43"]
status: backlog
priority: P0
type: meta_tracking
estimated_effort: "6h"
assignee: governor-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-08
dependencies:
  - TASK-INF-0208
  - TASK-INF-0210
  - TASK-INF-0211
  - TASK-INF-0212
  - TASK-INF-0213
  - TASK-INF-0214
  - TASK-INF-0215
  - TASK-INF-0216
  - TASK-INF-0217
  - TASK-INF-0218
  - TASK-INF-0219
tags:
  - blind-spot-tracking
  - B1-B156
  - risk-tracking
  - R1-R90
  - anti-pattern
  - AP1-AP43
severity: critical
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blind_spot_tracker.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\risk_tracker.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\antipattern_tracker.yaml"
acceptance_criteria:
  - "156个盲点全部注册到 blind_spot_tracker.yaml，含 audit_round / section / decision / status / implementation_file / verification"
  - "90项风险(R1-R90)全部注册到 risk_tracker.yaml，含 probability / impact / mitigation / detected / status"
  - "43条Anti-Pattern(AP1-AP43)全部注册到 antipattern_tracker.yaml，含 pattern / detector / action / status"
  - "Must-Have(~25) / Should-Have(~50) / Nice-to-Have(~78) 三级分类标注"
  - "自动化验证脚本: python -m zephyr.agent_spec verify-blindspots"
rollback_instructions: "删除 blind_spot_tracker.yaml, risk_tracker.yaml, antipattern_tracker.yaml"
context_assembly_manifest:
  blueprint_content: "16轮审计共156盲点(B1-B156) + 风险矩阵90项(R1-R90) + 反模式43条(AP1-AP43)——结构化追踪矩阵"
  template_version: "task-card-template.md v1.0.0"
blueprint_id: DOM-GOV-001
---


# TASK-INF-0221: 全量盲点/风险/反模式追踪矩阵

## 1. 任务描述

创建盲点(156)、风险(90)、反模式(43)的三合一全量追踪矩阵。每项条目追踪其关闭/缓解/防护状态，按 Must-Have/Should-Have/Nice-to-Have 分级。

## 2. 盲点按审计轮次分组

| 轮次 | 版本 | 盲点范围 | 数量 | 关键TaskCard |
|------|------|---------|:---:|-------------|
| Original | 0.1.0 | B1-B47 | 47 | Prior rounds |
| Round 3 | 0.6.0 | B48-B63 | 16 | TASK-INF-0210 |
| Round 4 | 0.7.0 | B64-B76 | 13 | TASK-INF-0211 |
| Round 5 | 0.7.0 | B77-B92 | 16 | TASK-INF-0212 |
| Round 6 | 0.8.0 | B93-B103 | 11 | TASK-INF-0213 |
| Round 9 | 0.10.0 | B106-B115 | 10 | TASK-INF-0214 |
| Round 10 | 0.11.0 | B116-B123 | 8 | TASK-INF-0215 |
| Round 11 | 0.12.0 | B124-B130 | 7 | TASK-INF-0215 |
| Round 12 | 0.13.0 | B131-B134 | 4 | TASK-INF-0216 |
| Round 13 | 0.14.0 | B135-B142 | 8 | TASK-INF-0216 |
| Round 14 | 0.15.0 | B143-B149 | 7 | TASK-INF-0217 |
| Round 15 | 0.16.0 | B150-B153 | 4 | TASK-INF-0218 |
| Round 16 | 0.17.0 | B154-B156 | 3 | TASK-INF-0219 |

**Total: 154+ = 156 盲点 (含B92/103/105等个别编号跳跃)**

## 3. 风险按严重性分级

| 严重性 | 风险项 | 数量 |
|--------|-------|:---:|
| (P=高/I=高) | R1,R16,R19,R32,R33,R34,R35,R36,R37,R38,R40,R45,R47 etc. | ~25 |
| (P=高/I=中) | R2,R7,R12,R26,R28 etc. | ~25 |
| (P=中/I=高) | R6,R10,R11,R18,R23,R25,R42 etc. | ~20 |
| (P=中/I=中) | R3,R4,R8,R13 etc. | ~20 |
| (P=低) | R5,R9,R20,R21,R22,R24 etc. | ~10 |

**Total: ~90 风险项**

## 4. 反模式防护

```yaml
antipattern_categories:
  comprehensive_vs_focused: "AP1: Encyclopedia Skill pattern → split to 2-3 modules"
  hero_pattern: "AP2: Skill claims ALL capabilities → scope reduction"
  vacuum_pattern: "AP3: Skill too sparse → auto-generate missing sections"
  contradiction: "AP4: Internal conflicting instructions → LLM contradiction check"
  circular_ref: "AP5: Self-reference/DAG cycle → topology check"
  staleness: "AP6: Outdated references → cross-reference scan"
  # ... AP7-AP43
```

## 5. 验收标准

- [ ] 156 盲点全注册 + 分级
- [ ] 90 风险全注册 + 严重性标注
- [ ] 43 反模式全注册 + 检测器

## 6. 回滚说明

删除三个 tracker YAML 文件。