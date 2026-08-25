---
blueprint_id: MOD-PLAN-019
module_name: scenario_playbook
domain: D_PLAN
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_PLAN
path: src/zephyr/plan_engine/scenario_playbook.py
granularity: file
---

# MOD-PLAN-019 scenario_playbook 蓝图（C-005 多情景对策）

> **module_id**: MOD-PLAN-019 | **域**: D_PLAN | **优先级**: P1
> **来源**: B1-00190（AUD-DRAFT-001-DIGEST P1 波 W-P1-19，CAND-PLAN-013，跨域元文档 §功能域模块·D-PORTFOLIO）
> 代码：`src/zephyr/plan_engine/scenario_playbook.py`

## 0. 定位

C-005 多情景对策：TSV 现状注记"情景规划器在，情景预案模板库与盘中自动匹配
触发未成体系"。施工形态=预案模板库（情景→操作边界/持仓动作/风控升级）+
盘中实时匹配（状态/事件触发）+执行确认流，预案命中率复盘入
scenario_probability_model 更新。

查重分工（W-P1-19 铁律②探查，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| scenario_planner | MOD-PLAN-005 | 9:00 三情景生成 + 9:25 竞价二次匹配 | 管盘前情景**生成**，不管盘中对策模板与触发 |
| scenario_plan_recorder | MOD-PLAN-008 | 预案落库 prediction_log + outcome 回写 | 管预测记录，不管对策确认流 |
| scenario_probability_model | MOD-PLAN-017 | 9 格概率三层融合 | 本模块复盘命中率**回写目标**（回调注入，不直连） |
| scenario_attribution_stats | MOD-PLAN-009 | 三维归因统计 | 不管模板库与实时匹配 |

不做什么：不重生成盘前情景（MOD-PLAN-005 产出注入）、不直接写库（复盘回调
委托装配批）、不下单（只出对策建议与确认状态）。

## 1. 规则（确定性，纯函数）

- **模板库**：PlaybookTemplate（scenario∈SCENARIO_LIST 9 情景语义对齐
  MOD-PLAN-002 → operation_boundary（加仓上限/禁加仓价位/减仓触发）+
  holding_action（持仓动作枚举）+ risk_escalation（风控升级档位 0~2）+
  trigger_states/trigger_events）。默认库 9 情景全覆盖，可注入覆盖。
- **盘中实时匹配**：match(market_state, active_scenario, events) → 模板命中
  （trigger_states 含 market_state 且 trigger_events ∩ events 非空，或
  无触发条件=常配模板）；多命中取 risk_escalation 最高者（保守优先）。
- **执行确认流**：PROPOSED →（人工 confirm）→ CONFIRMED → EXECUTED；
  PROPOSED → REJECTED / EXPIRED（TTL _bar 数封顶）；状态机非法迁移
  Fail-Closed。confirm 必须携 confirmed_by（人工确认留痕，对齐
  40号决策⑧ 人工在环）。
- **复盘回写**：settle(template_id, hit) → 命中率统计（Beta 平滑）+
  review payload 经 review_sink 回调供 scenario_probability_model 更新
  （sink 异常不阻断如实记录）。

## 2. 接口

```python
@dataclass(frozen=True)
class PlaybookTemplate: template_id / scenario / operation_boundary / holding_action / risk_escalation / trigger_states / trigger_events / ttl_bars
@dataclass(frozen=True)
class PlaybookMatch: template / matched_trigger / proposed_at_bar
class PlaybookConfirmation: confirm / reject / expire / mark_executed（状态机）
class PlaybookLibrary: default_library() / match(...) / settle(...)
class PlaybookError(ValueError)  # error_code 待登记
```

## 3. 依赖前置

- MOD-PLAN-002 premarket_constraint_loader（SCENARIO_LIST 9 情景语义唯一真源，
  node 10619476）。
- MOD-PLAN-005 scenario_planner（盘前情景产出哲学对齐，node 10619480）。
- MOD-PLAN-017 scenario_probability_model（复盘命中率回写目标，node 10619481）。

## 4. 验收标准

- 单测全绿（默认库 9 情景全覆盖/触发匹配与保守优先/确认流状态机非法迁移
  拒绝/确认留痕/复盘 Beta 平滑与 sink 回调/畸形输入 Fail-Closed）；
  tests/plan_engine 零回归。
