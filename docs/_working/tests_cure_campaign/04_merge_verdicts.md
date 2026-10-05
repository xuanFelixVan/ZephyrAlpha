---
ttl: task_bound
completes_when: tests 治理战役收官随批归档
---
# 归并裁定表（04）——tests/ 129 目录 → 8 域

- 生成: 2026-10-04T20:52:08+08:00 | 生成器: .runtime/tmp/st-tests-chief-20261004/gen_merge_verdicts.py（机生禁手改）
- 真源: 01_structure_census.md 域分配 + 总包 21 条 need_review 裁定（import 面证据在案）
- 施工语义: tests/<dir> → tests/<域>/<dir>（git mv 整体下沉，目录名不变，rename 历史保留）
- 顶层散文件: conftest.py 原位保留（pytest 语义）；test_batch_creation_tokens_anchor.py 与 test_generate_governance_map.py → tests/gov/ 平铺

## 未映射/多余核对

- 实存未映射: ∅
- 映射无实存: ∅

## 域汇总

| 域 | 目录数 | 递归py |
|---|---:|---:|
| gov | 32 | 1507 |
| data | 13 | 143 |
| trade | 11 | 363 |
| research | 19 | 639 |
| infra | 10 | 249 |
| ai | 16 | 552 |
| meta | 27 | 442 |
| legacy_zephyr | 1 | 150 |
| **合计** | **129** | **4045** |

## 明细（搬迁清单=每域一节）

### tests/gov/（32 目录）

| 源目录 | 递归py | 裁定依据 |
|---|---:|---|
| tests/architecture | 6 | 架构治理测试 |
| tests/audit | 105 | 矿工规则命中 |
| tests/autonomy_core | 3 | autonomy 核（同族已在 gov） |
| tests/boundary | 6 | 矿工规则命中 |
| tests/budget | 13 | 矿工规则命中 |
| tests/capability | 7 | 矿工规则命中 |
| tests/capacity | 9 | 被测=orchestrator.governance.capacity_budget+feedback_loop 容量 |
| tests/clone_guard | 16 | 矿工规则命中 |
| tests/compliance | 24 | 矿工规则命中 |
| tests/decision | 7 | 矿工规则命中 |
| tests/dependency | 7 | 依赖治理 |
| tests/escalation | 21 | 矿工规则命中 |
| tests/f_lifecycle | 20 | 被测=ops_governance.auto_runner(35)+finalizer+event_bus |
| tests/feedback | 111 | 被测=zephyr.feedback_loop.*（反馈回路引擎，111py 大户） |
| tests/feedback_loop | 3 | 与 feedback 同族同批收编 |
| tests/gate | 32 | 矿工规则命中 |
| tests/git | 21 | 矿工规则命中 |
| tests/gov_audit | 1 | 矿工规则命中 |
| tests/gov_code_dedup | 7 | 矿工规则命中 |
| tests/gov_drift | 1 | 矿工规则命中 |
| tests/gov_enforcement | 8 | 矿工规则命中 |
| tests/gov_rule | 1 | 矿工规则命中 |
| tests/governance | 832 | 矿工规则命中 |
| tests/guard | 8 | 矿工规则命中 |
| tests/risk | 83 | 矿工规则命中 |
| tests/rollback | 34 | 矿工规则命中 |
| tests/rule | 7 | 矿工规则命中 |
| tests/safety | 31 | 矿工规则命中 |
| tests/security | 14 | 矿工规则命中 |
| tests/semantic_auditor | 9 | 矿工规则命中 |
| tests/session | 12 | 会话治理 |
| tests/trae_rules | 48 | 矿工规则命中 |

### tests/data/（13 目录）

| 源目录 | 递归py | 裁定依据 |
|---|---:|---|
| tests/alt_data | 20 | 矿工规则命中 |
| tests/backup | 2 | 矿工规则命中 |
| tests/cold | 5 | 矿工规则命中 |
| tests/data | 37 | 矿工规则命中 |
| tests/data_eng | 1 | 矿工规则命中 |
| tests/data_governance | 14 | 矿工规则命中 |
| tests/data_security | 6 | 矿工规则命中 |
| tests/db | 17 | 矿工规则命中 |
| tests/dr | 8 | 矿工规则命中 |
| tests/file | 5 | 矿工规则命中 |
| tests/io | 10 | 矿工规则命中 |
| tests/market_data | 13 | 矿工规则命中 |
| tests/path | 5 | 矿工规则命中 |

### tests/trade/（11 目录）

| 源目录 | 递归py | 裁定依据 |
|---|---:|---|
| tests/action | 9 | 矿工规则命中 |
| tests/bridges | 7 | 矿工规则命中 |
| tests/e | 36 | 矿工规则命中 |
| tests/ex_core | 70 | 矿工规则命中 |
| tests/ex_sor | 18 | 矿工规则命中 |
| tests/execution_simulation | 1 | 矿工规则命中 |
| tests/plan_engine | 34 | 被测=zephyr.plan_engine 核心（交易计划→执行链） |
| tests/position | 31 | 矿工规则命中 |
| tests/sell_decision | 22 | 矿工规则命中 |
| tests/simulation | 14 | 矿工规则命中 |
| tests/trading | 121 | 矿工规则命中 |

### tests/research/（19 目录）

| 源目录 | 递归py | 裁定依据 |
|---|---:|---|
| tests/alpha_signal | 3 | 矿工规则命中 |
| tests/ba | 10 | 矿工规则命中 |
| tests/backtest | 143 | 矿工规则命中 |
| tests/digital_twin | 1 | 被测=digital_twin.market_twin_simulator |
| tests/experiment_tracking | 5 | 矿工规则命中 |
| tests/factor | 61 | 矿工规则命中 |
| tests/federated_learning | 81 | 矿工规则命中 |
| tests/ml_experiment | 4 | 矿工规则命中 |
| tests/ml_train | 27 | 矿工规则命中 |
| tests/pf_alloc | 22 | 组合分配（L9 知识供给闸域） |
| tests/pf_core | 33 | 被测=pf_core.strategy_engine.framework_composer |
| tests/regime | 48 | 矿工规则命中 |
| tests/research | 9 | 矿工规则命中 |
| tests/signal | 1 | 矿工规则命中 |
| tests/signal_ashare | 149 | 矿工规则命中 |
| tests/signal_fundamental | 13 | 矿工规则命中 |
| tests/signal_quality | 5 | 矿工规则命中 |
| tests/strategy_factory | 8 | 策略工厂（图9 研究生产链） |
| tests/strategy_pipeline | 16 | 策略管线 |

### tests/infra/（10 目录）

| 源目录 | 递归py | 裁定依据 |
|---|---:|---|
| tests/ce | 7 | 被测=cache_invalidation/capacity_assurance.kill_switch（容量保障杂烩） |
| tests/external | 5 | 外部接口 |
| tests/frontend | 28 | 矿工规则命中 |
| tests/infra_ops | 5 | 矿工规则命中 |
| tests/infra_runtime | 8 | 矿工规则命中 |
| tests/infrastructure | 137 | 矿工规则命中 |
| tests/observability | 16 | 矿工规则命中 |
| tests/ops | 2 | 运维 |
| tests/reporting | 29 | 矿工规则命中 |
| tests/resource | 12 | 资源 |

### tests/ai/（16 目录）

| 源目录 | 递归py | 裁定依据 |
|---|---:|---|
| tests/a2a | 49 | 矿工规则命中 |
| tests/agent | 13 | 矿工规则命中 |
| tests/agent_rbac | 43 | 矿工规则命中 |
| tests/ai | 8 | 矿工规则命中 |
| tests/ai_layer | 78 | 矿工规则命中 |
| tests/autonomy | 94 | 矿工规则命中 |
| tests/intelligence | 46 | 矿工规则命中 |
| tests/intent | 5 | 意图识别 |
| tests/knowledge | 14 | 矿工规则命中 |
| tests/library | 17 | 矿工规则命中 |
| tests/llm_security | 64 | 矿工规则命中 |
| tests/memory | 12 | 矿工规则命中 |
| tests/model | 28 | 矿工规则命中 |
| tests/nlp | 7 | 矿工规则命中 |
| tests/prompt | 9 | 矿工规则命中 |
| tests/skill | 65 | 矿工规则命中 |

### tests/meta/（27 目录）

| 源目录 | 递归py | 裁定依据 |
|---|---:|---|
| tests/asset_inventory | 20 | 矿工规则命中 |
| tests/automation | 22 | 矿工规则命中 |
| tests/blueprint | 16 | 矿工规则命中 |
| tests/canary | 5 | 矿工规则命中 |
| tests/chaos | 7 | 矿工规则命中 |
| tests/config | 10 | 矿工规则命中 |
| tests/context | 47 | 矿工规则命中 |
| tests/contracts | 33 | 被测=orchestrator.contracts（编排器契约，与 orchestrator 同域） |
| tests/cross | 20 | 矿工规则命中 |
| tests/drift | 17 | 矿工规则命中 |
| tests/event | 9 | 矿工规则命中 |
| tests/fix | 13 | 矿工规则命中 |
| tests/fixtures | 8 | 矿工规则命中 |
| tests/fle | 15 | 矿工规则命中 |
| tests/industry_graph | 4 | 矿工规则命中 |
| tests/integration | 6 | 矿工规则命中 |
| tests/metamorphic | 3 | 矿工规则命中 |
| tests/multi | 7 | 矿工规则命中 |
| tests/orchestrator | 20 | 矿工规则命中 |
| tests/phase | 6 | 矿工规则命中 |
| tests/pipeline | 14 | 管线测试 |
| tests/scripts | 50 | 矿工规则命中 |
| tests/self_check | 22 | 矿工规则命中 |
| tests/shared | 18 | 矿工规则命中 |
| tests/task | 8 | 矿工规则命中 |
| tests/temporal | 5 | 矿工规则命中 |
| tests/utils | 37 | 矿工规则命中 |

### tests/legacy_zephyr/（1 目录）

| 源目录 | 递归py | 裁定依据 |
|---|---:|---|
| tests/zephyr | 150 | 矿工规则命中 |
