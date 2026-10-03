---
ttl: task_bound
title: "孤岛入账增量批次1草案"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine
---

> 本批次已入账：commit e405020493，generate_wiring_registry --check rc=0

# W2 孤岛入账增量批次1草案（top20，交总筹落册）

- 证据源：`data/runtime/consumption_census_ledger.json`（schema=consumption_census/2，updated_at=2026-09-29，全账 473 岛）
- 机器视图：`docs/_working/fullflow_mine_20261001/wiring/wiring_view_20261001.yaml`（generator=MOD-INF-005，--top 20，rc=0）
- 现势：`docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml` 无 `consumption_islands` 段 → 本批 20 条全为净新增；`--check`（top5/top20）均 DRIFT rc=1（账面全缺）
- 生成器不变量：新岛默认 `wiring_status=unwired`、已在册者继承原值；判定建议仅为本批咨询意见，改状态须治愈实证（island_transitions 只认 census 复跑 state=active）

## 一、总筹入账增量片段（wiring_registry.yaml `consumption_islands` 追加）

```yaml
consumption_islands:
- entity_id: MAC-CN-001
  family: macro
  wiring_status: unwired
  value_score: 2.3
  suggested_wiring_target: regime/regime_cycle_analyzer.py 或 plan_engine 隔夜链（CNS-04 宏观族总裁决）
  booked_at: '2026-09-29'
- entity_id: MAC-CN-002
  family: macro
  wiring_status: unwired
  value_score: 2.3
  suggested_wiring_target: regime/regime_cycle_analyzer.py 或 plan_engine 隔夜链（CNS-04 宏观族总裁决）
  booked_at: '2026-09-29'
- entity_id: MAC-CN-003
  family: macro
  wiring_status: unwired
  value_score: 2.3
  suggested_wiring_target: regime/regime_cycle_analyzer.py 或 plan_engine 隔夜链（CNS-04 宏观族总裁决）
  booked_at: '2026-09-29'
- entity_id: MAC-CN-010
  family: macro
  wiring_status: unwired
  value_score: 2.3
  suggested_wiring_target: regime/regime_cycle_analyzer.py 或 plan_engine 隔夜链（CNS-04 宏观族总裁决）
  booked_at: '2026-09-29'
- entity_id: STR-VREV-018
  family: strategy
  wiring_status: unwired
  value_score: 2.3
  suggested_wiring_target: TDM nodes[].strategy_mounts（族⑦→执行路径）
  booked_at: '2026-09-29'
- entity_id: STR-VREV-019
  family: strategy
  wiring_status: unwired
  value_score: 2.3
  suggested_wiring_target: TDM nodes[].strategy_mounts（族⑦→执行路径）
  booked_at: '2026-09-29'
- entity_id: FCT-EXP-001
  family: factor
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/pf_core/strategies/ 挂载 + TDM factor_refs（CNS-09）
  booked_at: '2026-09-29'
- entity_id: FCT-EXP-003
  family: factor
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/pf_core/strategies/ 挂载 + TDM factor_refs（CNS-09）
  booked_at: '2026-09-29'
- entity_id: FCT-EXP-004
  family: factor
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/pf_core/strategies/ 挂载 + TDM factor_refs（CNS-09）
  booked_at: '2026-09-29'
- entity_id: FCT-EXP-005
  family: factor
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/pf_core/strategies/ 挂载 + TDM factor_refs（CNS-09）
  booked_at: '2026-09-29'
- entity_id: FCT-FQ-005
  family: factor
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/pf_core/strategies/ 挂载 + TDM factor_refs（CNS-09）
  booked_at: '2026-09-29'
- entity_id: FCT-FQ-006
  family: factor
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/pf_core/strategies/ 挂载 + TDM factor_refs（CNS-09）
  booked_at: '2026-09-29'
- entity_id: FCT-GR-001
  family: factor
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/pf_core/strategies/ 挂载 + TDM factor_refs（CNS-09）
  booked_at: '2026-09-29'
- entity_id: FCT-GR-002
  family: factor
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/pf_core/strategies/ 挂载 + TDM factor_refs（CNS-09）
  booked_at: '2026-09-29'
- entity_id: FCT-QUAL-002
  family: factor
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/pf_core/strategies/ 挂载 + TDM factor_refs（CNS-09）
  booked_at: '2026-09-29'
- entity_id: IND-CHIPS-001
  family: indicator
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/factor/indicator_reader.py PIT 白名单 → factor/analysis/multifactor_synthesis.py（CNS-01）
  booked_at: '2026-09-29'
- entity_id: IND-CHIPS-002
  family: indicator
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/factor/indicator_reader.py PIT 白名单 → factor/analysis/multifactor_synthesis.py（CNS-01）
  booked_at: '2026-09-29'
- entity_id: IND-CHIPS-003
  family: indicator
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/factor/indicator_reader.py PIT 白名单 → factor/analysis/multifactor_synthesis.py（CNS-01）
  booked_at: '2026-09-29'
- entity_id: IND-CHIPS-004
  family: indicator
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/factor/indicator_reader.py PIT 白名单 → factor/analysis/multifactor_synthesis.py（CNS-01）
  booked_at: '2026-09-29'
- entity_id: IND-CHIPS-005
  family: indicator
  wiring_status: unwired
  value_score: 2.0
  suggested_wiring_target: src/zephyr/factor/indicator_reader.py PIT 白名单 → factor/analysis/multifactor_synthesis.py（CNS-01）
  booked_at: '2026-09-29'
```

## 二、top20 逐条接线判定建议（咨询意见，非落册值）

| # | entity_id | family | score | 判定建议 | 依据 / defer_reason |
|---|-----------|--------|-------|---------|---------------------|
| 1 | MAC-CN-001 | macro | 2.3 | unwired 挂账 | state=zero、build_maturity=doc_ref_only（仅 6 处文档声明需求、零代码消费者）；接线目标 regime_cycle_analyzer.py 现无 macro 引用（grep=0），接线=新建消费，须先过 CNS-04 宏观族总裁决 |
| 2 | MAC-CN-002 | macro | 2.3 | unwired 挂账 | 同 MAC-CN-001（同族同因，声明需求 6 处、doc_ref_only、CNS-04 未裁） |
| 3 | MAC-CN-003 | macro | 2.3 | unwired 挂账 | 同 MAC-CN-001 |
| 4 | MAC-CN-010 | macro | 2.3 | unwired 挂账 | 同 MAC-CN-001 |
| 5 | STR-VREV-018 | strategy | 2.3 | **wired 建议** | census 实证零 entity_id 消费，但 advisory_alias_files 6 处含实现本体 src/zephyr/pf_core/vwap_reversion_strategy.py、config/trading_decision_map.yaml、src/zephyr/trading/decision_map.py、frontend/dashboard/api_server.py、scripts/tests/smoke_test_ede_e2e.py、config/framework_plans.yaml，declared_demand_refs=1；消费方案=TDM nodes[].strategy_mounts 显式挂载（字段已在册，config/trading_decision_map.yaml:60 起，多数节点为空可挂） |
| 6 | STR-VREV-019 | strategy | 2.3 | **wired 建议** | 同 STR-VREV-018（同族 VWAP 反转变体，6 alias + 1 声明需求；TDM strategy_mounts 显式挂载即治愈，改 wired 须 census 复跑 state=active 实证后经 island_transitions） |
| 7 | FCT-EXP-001 | factor | 2.0 | unwired 挂账 | state=zero、零声明需求；doc 提及全在 _working 归档/作业簿（非消费）；挂载目标 pf_core/strategies/ 存在（3 sleeve 策略），接线待 CNS-09 因子挂载裁决 |
| 8 | FCT-EXP-003 | factor | 2.0 | unwired 挂账 | 同 FCT-EXP-001（提及均 archive/kimi_audit lane 报告） |
| 9 | FCT-EXP-004 | factor | 2.0 | unwired 挂账 | 同 FCT-EXP-001 |
| 10 | FCT-EXP-005 | factor | 2.0 | unwired 挂账 | state=zero；8 处 advisory alias 系名称子串疑似命中（expectations.py 等），无一直指本实体，需因子域会话人工甄别后再判，暂挂账 defer |
| 11 | FCT-FQ-005 | factor | 2.0 | unwired 挂账 | state=zero、零提及零别名零声明——三零孤岛，defer_reason=无任何消费线索，待 CNS-09 统一挂载或退役裁决 |
| 12 | FCT-FQ-006 | factor | 2.0 | unwired 挂账 | state=zero，仅工段作业簿 doc 提及（非消费）；同上待 CNS-09 |
| 13 | FCT-GR-001 | factor | 2.0 | unwired 挂账 | state=zero，仅工段作业簿 doc 提及；待 CNS-09 |
| 14 | FCT-GR-002 | factor | 2.0 | unwired 挂账 | state=zero、三零孤岛；待 CNS-09 |
| 15 | FCT-QUAL-002 | factor | 2.0 | unwired 挂账 | state=zero；2 alias（factor/__init__.py、value_factor.py）系疑似命中未实证；仅 B3.md 归档提及；待因子域甄别 |
| 16 | IND-CHIPS-001 | indicator | 2.0 | unwired 挂账 | census recommendation=retire_candidate(零消费，指标域会话核实后处置)；PIT 白名单接线目标存在（indicator_reader.py / multifactor_synthesis.py），先核处置方向（接线 vs 退役）再动 |
| 17 | IND-CHIPS-002 | indicator | 2.0 | unwired 挂账 | 同 IND-CHIPS-001（retire_candidate） |
| 18 | IND-CHIPS-003 | indicator | 2.0 | unwired 挂账 | 同 IND-CHIPS-001（retire_candidate，零提及） |
| 19 | IND-CHIPS-004 | indicator | 2.0 | unwired 挂账 | 同上 + advisory_alias=factor/technical_indicators/chips.py（疑似实现本体，须指标域会话甄别是否即消费点） |
| 20 | IND-CHIPS-005 | indicator | 2.0 | unwired 挂账 | 同 IND-CHIPS-004（retire_candidate + chips.py 疑似别名） |

## 三、判定计数与说明

- **wired 建议：2 条**（STR-VREV-018/019，证据=6 advisory alias + 1 声明需求 + TDM strategy_mounts 在册可挂）
- **unwired 挂账：18 条**（MAC-CN×4 缺代码路径待 CNS-04；FCT×9 待 CNS-09/人工甄别；IND-CHIPS×5 census 自标 retire_candidate 待指标域核实）
- **exempt：0 条**（exempt 词表对应 pure_library 模块类，top20 全为数据实体——宏观概念/策略/因子/指标，无一适用）
- 治愈路径：任何 unwired→wired 变更须经 census 复跑 state=active 实证，走 `island_transitions`（healed_by_consumer），禁手工直改（MOD-INF-005 不变量）

## 四、总筹操作指引

1. 将 §一 YAML 追加进 `docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml`（热文件，走 `safe_write_text` CAS，GitCommitGateway 提交）。
2. 落册后复跑 `python scripts/governance/d3_metadata/generate_wiring_registry.py --repo-root . --check` 应 rc=0（top5 视角）。
3. STR-VREV 挂载（TDM strategy_mounts）属施工，走 construction_workflow 15 步 + apply_depgraph 登记，不在本工单范围。
