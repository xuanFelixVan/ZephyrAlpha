---
task_id: TASK-OPS-0021
module_id: MOD-INF-005
title: "第四层盲点 B60-B91 系统性缓解 — §27 32盲点×§28 10行动项A1-A10"
status: TODO
priority: P1
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - blind-spots
  - fourth-layer
  - ai-session
  - 1person-maintenance
description: |
  将第四层盲点 B60-B91（§27）和对应的 10 行动项 A1-A10（§28）拆解为可跟踪的缓解任务。
  
  §27.1 AI会话上下文管理 (B60-B62): 上下文污染 / 中断续接 / 规则版本过期
  §27.2 AI反馈回路安全 (B63-B65): Finding反馈中毒 / 自修复振荡 / 跨脚本接口断裂
  §27.3 1人+AI维护专属 (B66-B69): 维护者缺席 / 模型迁移 / 巴士系数 / AI行为隐式依赖
  §27.4 性能规模递增 (B70-B72): Pre-commit延迟 / 重复解析 / 增量扫描
  §27.5 脚本质量测试 (B73-B75): Golden Test Case / 跨维度集成 / 变异测试
  §27.6 运维韧性 (B76-B78): 分级降级 / 断点续传 / Finding模式异常
  §27.7 AI安全专属 (B79-B80): 混淆后门 / Prompt Injection
  §27.8 生态适配 (B81-B82): 跨IDE / AI消费仪表盘
  §27.9 演进废弃 (B83-B84): 版本兼容 / 退役影响分析
  §27.10 文档追溯 (B85-B86): 规则追索 / 根因聚类
  §27.11 Vibe Coding (B87-B89): 环境漂移 / 演化漂移 / Session特化
  §27.12 度量反馈 (B90-B91): 脚本ROI / 检测修复速度比

acceptance_criteria:
  - "§28 的 A1-A10 每项在本蓝图中有对应任务卡或验证脚本"
  - "§28 P0 项 A1(Golden Test)→TASK-OPS-0018 / A2(depends_on)→TASK-OPS-0006 / A3(pre-commit SLA)→TASK-OPS-0006"
  - "B60 上下文窗口污染→AGENTS.md 增加注入策略指令"
  - "B64 自修复振荡→detect_fix_oscillation.py 脚本新建"
  - "B66 维护者缺席→Kill Switch 扩展 maintainer_absent_until 字段"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\detect_fix_oscillation.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\score_script_effectiveness.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\detect_script_divergence.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\detect_config_deviation.py"

rollback_instructions: "git checkout -- scripts/governance/meta/detect_fix_oscillation.py scripts/governance/meta/score_script_effectiveness.py"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§27.1-§27.12", "§28.1", "§28.2", "§28.3"]

phase: phase_3_systematize
effort_estimate: XL
risk_level: MEDIUM
depends_on_task: ["TASK-OPS-0020"]
blocks_task: ["TASK-OPS-0022"]
related_blind_spots: ["B60", "B61", "B62", "B63", "B64", "B65", "B66", "B67", "B68", "B69", "B70", "B71", "B72", "B73", "B74", "B75", "B76", "B77", "B78", "B79", "B80", "B81", "B82", "B83", "B84", "B85", "B86", "B87", "B88", "B89", "B90", "B91"]
related_risks: []
related_contracts: []
card_type: planning
upstream_blueprint_version: "5.2.1"
autonomy_level: human_required
---

# TASK-OPS-0021: 第四层盲点 B60-B91 + A1-A10 缓解任务规划

## 1. 任务概述

第四层 32 盲点（B60-B91）聚焦"AI+1人维护"语境。§28 将 32 盲点精炼为 10 行动项（P0/P1/P2）。需要逐项确认 10 行动项在当前 task card 体系中是否有对应施工任务。

## 2. A1-A10 对应验证

### P0 项：
| 行动 | 本蓝图已关联 | 备注 |
|------|:---:|------|
| A1 Golden Test Case 库 | TASK-OPS-0018 | B73→D1/D3/D5/D6 各3用例 |
| A2 depends_on_scripts 字段 | TASK-OPS-0006 | B65/B72/B84→manifest schema扩展 |
| A3 Pre-commit SLA ≤60s | TASK-OPS-0006 | B70→超时+分层策略 |

### P1 项：
| 行动 | 待施工 |
|------|--------|
| A4 上下文治理 | TASK-OPS-0019 (B60,B62) |
| A5 维护者缺席 | 新建 `maintainer_absent_mode.py` |
| A6 脚本效果分 | 新建 `score_script_effectiveness.py` |
| A7 Fix振荡检测 | 新建 `detect_fix_oscillation.py` |

### P2 项：
| 行动 | 待施工 |
|------|--------|
| A8 跨维度集成+变异 | TASK-OPS-0018 (变异) + cross_dimension_pipeline test |
| A9 脚本-规则矩阵 | manifest enforces 字段 |
| A10 跨IDE环境快照 | env_check 扩展 |

## 3. 验收标准
- [ ] A1-A3 P0 项全部对应已完成或在建 task card
- [ ] A4-A7 P1 项有对应 task card 或不实施的原因记录
- [ ] A8-A10 P2 项在 Backlog 登记
