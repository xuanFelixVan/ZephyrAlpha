---
ttl: task_bound
completes_when: tests 治理战役收官随批归档
---
# tests/ 战役 01 — 结构普查报告

- 生成时间: 2026-10-04 20:34 +0800
- 统计脚本: `.runtime/tmp/st-tests-chief-20261004/tests_structure_census.py`（只读扫描, 禁改 tests/ 本体）
- 总计数: 一级子目录 **130**（含 __pycache__ 垃圾 1 个, 实际 129）| 顶层散文件 3 | 二级目录 127 | .py 总数 **4048**（递归, 排除 __pycache__）
- 口径: 平铺=目录直接子 .py（排除 __init__.py/隐藏文件, 门禁口径）; 递归=全部子树 .py（排除 __pycache__）
- 口径注: 战役简报称 148 个一级目录/4046 py, 实测 **130 目录 / 4048 py**，以本实测为准。

## 1a. 一级子目录全景（130 行: 平铺/递归/子目录数）

| 一级目录 | 平铺py | 递归py | 子目录数 |
|---|---:|---:|---:|
| a2a | 49 | 49 | 0 |
| action | 9 | 9 | 0 |
| agent | 13 | 13 | 0 |
| agent_rbac | 42 | 43 | 0 |
| ai | 8 | 8 | 0 |
| ai_layer | 3 | 78 | 9 |
| alpha_signal | 2 | 3 | 0 |
| alt_data | 20 | 20 | 0 |
| architecture | 5 | 6 | 0 |
| asset_inventory | 19 | 20 | 0 |
| audit | 27 | 105 | 5 |
| automation | 22 | 22 | 0 |
| autonomy | 93 | 94 | 0 |
| autonomy_core | 3 | 3 | 0 |
| ba | 10 | 10 | 0 |
| backtest | 143 | 143 | 0 |
| backup | 2 | 2 | 0 |
| blueprint | 16 | 16 | 0 |
| boundary | 5 | 6 | 0 |
| bridges | 7 | 7 | 0 |
| budget | 13 | 13 | 0 |
| canary | 5 | 5 | 0 |
| capability | 7 | 7 | 0 |
| capacity | 9 | 9 | 0 |
| ce | 7 | 7 | 0 |
| chaos | 6 | 7 | 0 |
| clone_guard | 11 | 16 | 1 |
| cold | 5 | 5 | 0 |
| compliance | 24 | 24 | 0 |
| config | 10 | 10 | 0 |
| context | 47 | 47 | 0 |
| contracts | 28 | 33 | 1 |
| cross | 20 | 20 | 0 |
| data | 30 | 37 | 1 |
| data_eng | 1 | 1 | 0 |
| data_governance | 14 | 14 | 0 |
| data_security | 6 | 6 | 0 |
| db | 17 | 17 | 0 |
| decision | 7 | 7 | 0 |
| dependency | 7 | 7 | 0 |
| digital_twin | 1 | 1 | 0 |
| dr | 7 | 8 | 0 |
| drift | 17 | 17 | 0 |
| e | 36 | 36 | 0 |
| escalation | 21 | 21 | 0 |
| event | 9 | 9 | 0 |
| ex_core | 64 | 70 | 2 |
| ex_sor | 18 | 18 | 0 |
| execution_simulation | 1 | 1 | 0 |
| experiment_tracking | 4 | 5 | 0 |
| external | 5 | 5 | 0 |
| f_lifecycle | 20 | 20 | 0 |
| factor | 60 | 61 | 0 |
| federated_learning | 80 | 81 | 0 |
| feedback | 23 | 111 | 7 |
| feedback_loop | 3 | 3 | 0 |
| file | 5 | 5 | 0 |
| fix | 13 | 13 | 0 |
| fixtures | 7 | 8 | 0 |
| fle | 15 | 15 | 0 |
| frontend | 28 | 28 | 0 |
| gate | 32 | 32 | 0 |
| git | 21 | 21 | 0 |
| gov_audit | 1 | 1 | 0 |
| gov_code_dedup | 6 | 7 | 0 |
| gov_drift | 1 | 1 | 0 |
| gov_enforcement | 7 | 8 | 1 |
| gov_rule | 1 | 1 | 0 |
| governance | 164 | 832 | 45 |
| guard | 8 | 8 | 0 |
| industry_graph | 4 | 4 | 0 |
| infra_ops | 5 | 5 | 0 |
| infra_runtime | 8 | 8 | 0 |
| infrastructure | 62 | 137 | 7 |
| integration | 6 | 6 | 0 |
| intelligence | 35 | 46 | 4 |
| intent | 5 | 5 | 0 |
| io | 10 | 10 | 0 |
| knowledge | 14 | 14 | 0 |
| library | 17 | 17 | 0 |
| llm_security | 63 | 64 | 1 |
| market_data | 5 | 13 | 3 |
| memory | 12 | 12 | 0 |
| metamorphic | 3 | 3 | 0 |
| ml_experiment | 3 | 4 | 0 |
| ml_train | 25 | 27 | 1 |
| model | 28 | 28 | 0 |
| multi | 7 | 7 | 0 |
| nlp | 6 | 7 | 0 |
| observability | 16 | 16 | 0 |
| ops | 2 | 2 | 0 |
| orchestrator | 20 | 20 | 0 |
| path | 5 | 5 | 0 |
| pf_alloc | 21 | 22 | 0 |
| pf_core | 33 | 33 | 0 |
| phase | 6 | 6 | 0 |
| pipeline | 14 | 14 | 0 |
| plan_engine | 34 | 34 | 0 |
| position | 31 | 31 | 0 |
| prompt | 9 | 9 | 0 |
| regime | 25 | 48 | 3 |
| reporting | 29 | 29 | 0 |
| research | 9 | 9 | 0 |
| resource | 12 | 12 | 0 |
| risk | 57 | 83 | 1 |
| rollback | 34 | 34 | 0 |
| rule | 7 | 7 | 0 |
| safety | 31 | 31 | 0 |
| scripts | 38 | 50 | 4 |
| security | 8 | 14 | 3 |
| self_check | 22 | 22 | 0 |
| sell_decision | 22 | 22 | 0 |
| semantic_auditor | 8 | 9 | 0 |
| session | 12 | 12 | 0 |
| shared | 9 | 18 | 4 |
| signal | 1 | 1 | 0 |
| signal_ashare | 62 | 149 | 7 |
| signal_fundamental | 5 | 13 | 2 |
| signal_quality | 5 | 5 | 0 |
| simulation | 13 | 14 | 0 |
| skill | 64 | 65 | 0 |
| strategy_factory | 8 | 8 | 0 |
| strategy_pipeline | 16 | 16 | 0 |
| task | 8 | 8 | 0 |
| temporal | 5 | 5 | 0 |
| trading | 81 | 121 | 6 |
| trae_rules | 48 | 48 | 0 |
| utils | 37 | 37 | 0 |
| zephyr | 0 | 150 | 9 |
| _junk:__pycache__ | 0 | 0 | 0 | （缓存垃圾, 删除候选, 不参与归并） |

## 1b. 二级目录平铺 py 清单（超限标记: >120 将被新门禁拦; >100 贴顶预警）

二级目录共 127 个, 按平铺数降序。

| 二级目录 | 平铺py | 标记 |
|---|---:|---|
| governance/commit_gates | 120 | >100 贴顶 |
| zephyr/data | 115 | >100 贴顶 |
| governance/audit | 95 |  |
| governance/rule_bridge | 36 |  |
| audit/audit_core | 31 |  |
| governance/security | 26 |  |
| risk/core | 25 |  |
| governance/resilience | 23 |  |
| governance/shared | 21 |  |
| signal_ashare/sector | 21 |  |
| infrastructure/process_lifecycle | 20 |  |
| trading/unit | 20 |  |
| governance/chaos_drill | 19 |  |
| signal_ashare/ml_forecast | 19 |  |
| audit/drift_integrity | 18 |  |
| governance/budget | 18 |  |
| governance/lifecycle | 18 |  |
| feedback/feedback_loop | 17 |  |
| governance/code_quality | 17 |  |
| governance/scripts_governance | 17 |  |
| infrastructure/observability | 17 |  |
| governance/integration | 16 |  |
| signal_ashare/strategy_signal | 16 |  |
| feedback/anomaly_diagnosis | 15 |  |
| infrastructure/mcp | 15 |  |
| feedback/learning_evolution | 14 |  |
| feedback/resilience_dr | 14 |  |
| governance/delegation | 13 |  |
| ai_layer/redline | 12 |  |
| governance/d3_metadata | 12 |  |
| governance/governance_e2e | 12 |  |
| governance/observability | 12 |  |
| audit/quality_static | 11 |  |
| governance/adversarial | 11 |  |
| governance/generators | 11 |  |
| governance/ops | 11 |  |
| governance/trading | 11 |  |
| ai_layer/heritage | 10 |  |
| ai_layer/scheduling | 10 |  |
| audit/intelligence_audit | 10 |  |
| feedback/governance_audit | 10 |  |
| feedback/observability_notify | 10 |  |
| governance/meta_question | 10 |  |
| governance/rule_enforcement | 10 |  |
| ai_layer/comparator | 9 |  |
| governance/compliance | 9 |  |
| governance/red_blue_pkg14 | 9 |  |
| regime/validation | 9 |  |
| ai_layer/perceive | 8 |  |
| audit/ops_resilience | 8 |  |
| feedback/scheduling | 8 |  |
| governance/access_control | 8 |  |
| governance/d5_architecture | 8 |  |
| governance/data_layer | 8 |  |
| governance/redblue_wave73 | 8 |  |
| regime/features | 8 |  |
| signal_ashare/intraday_t0 | 8 |  |
| signal_ashare/limit_up | 8 |  |
| ai_layer/intake | 7 |  |
| ai_layer/switch_engine | 7 |  |
| data/implementations | 7 |  |
| governance/drift | 7 |  |
| governance/orchestrator | 7 |  |
| signal_ashare/screening | 7 |  |
| signal_ashare/sentiment | 7 |  |
| ai_layer/cleaning | 6 |  |
| ai_layer/tools | 6 |  |
| intelligence/switch_engine | 6 |  |
| trading/pipeline | 6 |  |
| governance/code_dedup | 5 |  |
| governance/depgraph | 5 |  |
| governance/governance_misc | 5 |  |
| infrastructure/adversarial | 5 |  |
| regime/phase2 | 5 |  |
| shared/alerts | 5 |  |
| ex_core/adapters | 4 |  |
| governance/persistence | 4 |  |
| governance/registry_projection | 4 |  |
| infrastructure/escalation | 4 |  |
| infrastructure/system_telemetry | 4 |  |
| trading/integration | 4 |  |
| trading/root | 4 |  |
| contracts/_meta | 3 |  |
| governance/d1_structure | 3 |  |
| governance/data_supply | 3 |  |
| infrastructure/drift | 3 |  |
| scripts/backup | 3 |  |
| security/ops | 3 |  |
| signal_fundamental/audit | 3 |  |
| trading/runtime | 3 |  |
| governance/d8_doc_sync | 2 |  |
| governance/escalation | 2 |  |
| governance/fixtures | 2 |  |
| intelligence/model_intel | 2 |  |
| intelligence/model_routing | 2 |  |
| market_data/connectors | 2 |  |
| ml_train/implementations | 2 |  |
| scripts/ch | 2 |  |
| shared/io | 2 |  |
| signal_fundamental/router | 2 |  |
| trading/extreme | 2 |  |
| zephyr/trading | 2 |  |
| ex_core/rules | 1 |  |
| gov_enforcement/read_side | 1 |  |
| governance/context_governance | 1 |  |
| governance/d7_code | 1 |  |
| governance/docs | 1 |  |
| governance/fullflow | 1 |  |
| governance/standards_governance | 1 |  |
| intelligence/model_profiling | 1 |  |
| market_data/failover | 1 |  |
| market_data/raw_data_cache | 1 |  |
| scripts/ops | 1 |  |
| security/access_control | 1 |  |
| security/llm_defense | 1 |  |
| shared/capacity_governance | 1 |  |
| shared/lifecycle | 1 |  |
| zephyr/alt_data | 1 |  |
| zephyr/backtest | 1 |  |
| zephyr/factor | 1 |  |
| zephyr/infrastructure | 1 |  |
| zephyr/regime | 1 |  |
| zephyr/runtime | 1 |  |
| clone_guard/fixtures | 0 |  |
| llm_security/golden | 0 |  |
| scripts/governance | 0 |  |
| zephyr/shared | 0 |  |

### 任意深度超限目录（>120 / >100, 含三级及以下, 兜底核对）

| 目录(任意深度) | 平铺py | 判定 |
|---|---:|---|
| governance | 164 | >120 超限(新门禁将拦) |
| backtest | 143 | >120 超限(新门禁将拦) |
| governance/commit_gates | 120 | >100 贴顶预警 |
| zephyr/data | 115 | >100 贴顶预警 |

## 1c. 碎簇清单（一级目录递归 py ≤5）

| 一级目录 | 平铺py | 递归py | 平铺+递归字面和≤5 |
|---|---:|---:|---|
| data_eng | 1 | 1 | 是 |
| digital_twin | 1 | 1 | 是 |
| execution_simulation | 1 | 1 | 是 |
| gov_audit | 1 | 1 | 是 |
| gov_drift | 1 | 1 | 是 |
| gov_rule | 1 | 1 | 是 |
| signal | 1 | 1 | 是 |
| backup | 2 | 2 | 是 |
| ops | 2 | 2 | 是 |
| alpha_signal | 2 | 3 | 是 |
| autonomy_core | 3 | 3 | 否 |
| feedback_loop | 3 | 3 | 否 |
| metamorphic | 3 | 3 | 否 |
| industry_graph | 4 | 4 | 否 |
| ml_experiment | 3 | 4 | 否 |
| canary | 5 | 5 | 否 |
| cold | 5 | 5 | 否 |
| experiment_tracking | 4 | 5 | 否 |
| external | 5 | 5 | 否 |
| file | 5 | 5 | 否 |
| infra_ops | 5 | 5 | 否 |
| intent | 5 | 5 | 否 |
| path | 5 | 5 | 否 |
| signal_quality | 5 | 5 | 否 |
| temporal | 5 | 5 | 否 |

共 25 个碎簇（口径: 递归 py ≤5; 字面口径=平铺+递归≤5 亦并列展示）。

## 1d. 同名异父目录对（共 56 对）

| 同名 | 路径A | A平铺 | 路径B | B平铺 |
|---|---|---:|---|---:|
| access_control | governance/access_control | 8 | security/access_control | 1 |
| adversarial | governance/adversarial | 11 | infrastructure/adversarial | 5 |
| alt_data | alt_data | 20 | zephyr/alt_data | 1 |
| audit | audit | 27 | governance/audit | 95 |
| audit | audit | 27 | signal_fundamental/audit | 3 |
| audit | governance/audit | 95 | signal_fundamental/audit | 3 |
| backtest | backtest | 143 | zephyr/backtest | 1 |
| backup | backup | 2 | scripts/backup | 3 |
| budget | budget | 13 | governance/budget | 18 |
| compliance | compliance | 24 | governance/compliance | 9 |
| d8_doc_sync | governance/d8_doc_sync | 2 | scripts/governance/d8_doc_sync | 5 |
| data | data | 30 | zephyr/data | 115 |
| drift | drift | 17 | governance/drift | 7 |
| drift | drift | 17 | infrastructure/drift | 3 |
| drift | governance/drift | 7 | infrastructure/drift | 3 |
| escalation | escalation | 21 | governance/escalation | 2 |
| escalation | escalation | 21 | infrastructure/escalation | 4 |
| escalation | governance/escalation | 2 | infrastructure/escalation | 4 |
| factor | factor | 60 | zephyr/factor | 1 |
| feedback_loop | feedback/feedback_loop | 17 | feedback_loop | 3 |
| fixtures | clone_guard/fixtures | 0 | fixtures | 7 |
| fixtures | clone_guard/fixtures | 0 | governance/fixtures | 2 |
| fixtures | fixtures | 7 | governance/fixtures | 2 |
| governance | governance | 164 | scripts/governance | 0 |
| implementations | data/implementations | 7 | ml_train/implementations | 2 |
| infrastructure | infrastructure | 62 | zephyr/infrastructure | 1 |
| integration | governance/integration | 16 | integration | 6 |
| integration | governance/integration | 16 | trading/integration | 4 |
| integration | integration | 6 | trading/integration | 4 |
| io | io | 10 | shared/io | 2 |
| lifecycle | governance/lifecycle | 18 | shared/lifecycle | 1 |
| observability | governance/observability | 12 | infrastructure/observability | 17 |
| observability | governance/observability | 12 | observability | 16 |
| observability | governance/observability | 12 | zephyr/shared/observability | 3 |
| observability | infrastructure/observability | 17 | observability | 16 |
| observability | infrastructure/observability | 17 | zephyr/shared/observability | 3 |
| observability | observability | 16 | zephyr/shared/observability | 3 |
| ops | governance/ops | 11 | ops | 2 |
| ops | governance/ops | 11 | scripts/ops | 1 |
| ops | governance/ops | 11 | security/ops | 3 |
| ops | ops | 2 | scripts/ops | 1 |
| ops | ops | 2 | security/ops | 3 |
| ops | scripts/ops | 1 | security/ops | 3 |
| orchestrator | governance/orchestrator | 7 | orchestrator | 20 |
| pipeline | pipeline | 14 | trading/pipeline | 6 |
| regime | regime | 25 | zephyr/regime | 1 |
| runtime | trading/runtime | 3 | zephyr/runtime | 1 |
| scheduling | ai_layer/scheduling | 10 | feedback/scheduling | 8 |
| security | governance/security | 26 | security | 8 |
| shared | governance/shared | 21 | shared | 9 |
| shared | governance/shared | 21 | zephyr/shared | 0 |
| shared | shared | 9 | zephyr/shared | 0 |
| switch_engine | ai_layer/switch_engine | 7 | intelligence/switch_engine | 6 |
| trading | governance/trading | 11 | trading | 81 |
| trading | governance/trading | 11 | zephyr/trading | 2 |
| trading | trading | 81 | zephyr/trading | 2 |

## 2. 归并建议表（129 个一级目录 → 8 域）

| 域 | 目录数 | 递归py合计 |
|---|---:|---:|
| gov | 24 | 1336 |
| data | 13 | 143 |
| trade | 10 | 329 |
| research | 14 | 559 |
| infra | 6 | 223 |
| ai | 15 | 547 |
| meta | 25 | 395 |
| legacy_zephyr | 1 | 150 |
| need_review | 21 | 363 |

### → gov（24 个）

| 目录名 | 递归py | 平铺py | 置信度 | 依据 |
|---|---:|---:|---|---|
| audit | 105 | 27 | high | 规则命中(gov) |
| boundary | 6 | 5 | high | 规则命中(gov) |
| budget | 13 | 13 | high | 规则命中(gov) |
| capability | 7 | 7 | high | 规则命中(gov) |
| clone_guard | 16 | 11 | high | 规则命中(gov) |
| compliance | 24 | 24 | high | 规则命中(gov) |
| decision | 7 | 7 | high | 规则命中(gov) |
| escalation | 21 | 21 | high | 规则命中(gov) |
| gate | 32 | 32 | high | 规则命中(gov) |
| git | 21 | 21 | medium | GitCommitGateway 提交治理(commit_block/dead_session_salvage) |
| gov_audit | 1 | 1 | high | 规则命中(gov) 子串:gov_audit |
| gov_code_dedup | 7 | 6 | high | 规则命中(gov) 子串:gov_code_dedup |
| gov_drift | 1 | 1 | high | 规则命中(gov) 子串:gov_drift |
| gov_enforcement | 8 | 7 | high | 规则命中(gov) 子串:gov_enforcement |
| gov_rule | 1 | 1 | high | 规则命中(gov) 子串:gov_rule |
| governance | 832 | 164 | high | 规则命中(gov) |
| guard | 8 | 8 | high | 规则命中(gov) |
| risk | 83 | 57 | high | 规则命中(gov) |
| rollback | 34 | 34 | high | 规则命中(gov) |
| rule | 7 | 7 | high | 规则命中(gov) |
| safety | 31 | 31 | high | 规则命中(gov) |
| security | 14 | 8 | medium | kill_switch/出站清洗/密钥绑定=安全治理 |
| semantic_auditor | 9 | 8 | high | 规则命中(gov) 子串:semantic_auditor |
| trae_rules | 48 | 48 | high | 规则命中(gov) 子串:trae_rules |

### → data（13 个）

| 目录名 | 递归py | 平铺py | 置信度 | 依据 |
|---|---:|---:|---|---|
| alt_data | 20 | 20 | high | 规则命中(data) |
| backup | 2 | 2 | high | 规则命中(data) |
| cold | 5 | 5 | high | 规则命中(data) |
| data | 37 | 30 | high | 规则命中(data) |
| data_eng | 1 | 1 | high | 规则命中(data*) |
| data_governance | 14 | 14 | medium | 规则撞车 data*|governance; 内容=血缘/资产发现, 归数据链 |
| data_security | 6 | 6 | medium | 规则撞车 data*|security; 内容=数据脱敏管道, 归数据链(备选gov) |
| db | 17 | 17 | high | 规则命中(data) |
| dr | 8 | 7 | medium | 内容=backup 冷备/CH/VM 检查 |
| file | 5 | 5 | high | 规则命中(data) |
| io | 10 | 10 | high | 规则命中(data) |
| market_data | 13 | 5 | high | 规则命中(data) |
| path | 5 | 5 | high | 规则命中(data) |

### → trade（10 个）

| 目录名 | 递归py | 平铺py | 置信度 | 依据 |
|---|---:|---:|---|---|
| action | 9 | 9 | high | 规则命中(trade) |
| bridges | 7 | 7 | high | 规则命中(trade) |
| e | 36 | 36 | high | 规则命中(trade) |
| ex_core | 70 | 64 | high | 规则命中(trade) |
| ex_sor | 18 | 18 | high | 规则命中(trade) |
| execution_simulation | 1 | 1 | high | 规则命中(execution*) |
| position | 31 | 31 | high | 规则命中(trade) |
| sell_decision | 22 | 22 | high | 规则命中(trade) |
| simulation | 14 | 13 | high | 规则命中(trade) |
| trading | 121 | 81 | high | 规则命中(trade) |

### → research（14 个）

| 目录名 | 递归py | 平铺py | 置信度 | 依据 |
|---|---:|---:|---|---|
| alpha_signal | 3 | 2 | high | 规则命中(research 前缀) |
| ba | 10 | 10 | high | 规则命中(research) |
| backtest | 143 | 143 | high | 规则命中(research) |
| experiment_tracking | 5 | 4 | high | 规则命中(research) |
| factor | 61 | 60 | high | 规则命中(research) |
| federated_learning | 81 | 80 | high | 规则命中(research) |
| ml_experiment | 4 | 3 | high | 规则命中(research 前缀) |
| ml_train | 27 | 25 | high | 规则命中(research 前缀) |
| regime | 48 | 25 | high | 规则命中(research) |
| research | 9 | 9 | high | 规则命中(research) |
| signal | 1 | 1 | high | 规则命中(research 前缀) |
| signal_ashare | 149 | 62 | high | 规则命中(research 前缀) |
| signal_fundamental | 13 | 5 | high | 规则命中(research 前缀) |
| signal_quality | 5 | 5 | high | 规则命中(research 前缀) |

### → infra（6 个）

| 目录名 | 递归py | 平铺py | 置信度 | 依据 |
|---|---:|---:|---|---|
| frontend | 28 | 28 | high | 规则命中(infra) |
| infra_ops | 5 | 5 | high | 规则命中(infra_*) |
| infra_runtime | 8 | 8 | high | 规则命中(infra_*) |
| infrastructure | 137 | 62 | high | 规则命中(infra) |
| observability | 16 | 16 | high | 规则命中(infra) |
| reporting | 29 | 29 | high | 规则命中(infra) |

### → ai（15 个）

| 目录名 | 递归py | 平铺py | 置信度 | 依据 |
|---|---:|---:|---|---|
| a2a | 49 | 49 | high | 规则命中(ai) |
| agent | 13 | 13 | high | 规则命中(agent*) |
| agent_rbac | 43 | 42 | high | 规则命中(agent*) |
| ai | 8 | 8 | high | 规则命中(ai) |
| ai_layer | 78 | 3 | high | 规则命中(ai) |
| autonomy | 94 | 93 | medium | 内容=agent_spec/agent_ticket/ai_ops 卡片 |
| intelligence | 46 | 35 | high | 规则命中(ai) |
| knowledge | 14 | 14 | high | 规则命中(ai) |
| library | 17 | 17 | high | 规则命中(ai) |
| llm_security | 64 | 63 | high | 规则命中(ai) |
| memory | 12 | 12 | high | 规则命中(ai) |
| model | 28 | 28 | medium | 内容=deepseek_v4_chat 等 LLM 网关 |
| nlp | 7 | 6 | high | 规则命中(ai) |
| prompt | 9 | 9 | high | 规则命中(ai) |
| skill | 65 | 64 | high | 规则命中(ai) |

### → meta（25 个）

| 目录名 | 递归py | 平铺py | 置信度 | 依据 |
|---|---:|---:|---|---|
| asset_inventory | 20 | 19 | high | 规则命中(meta) |
| automation | 22 | 22 | high | 规则命中(meta) |
| blueprint | 16 | 16 | high | 规则命中(meta) |
| canary | 5 | 5 | high | 规则命中(meta) |
| chaos | 7 | 6 | high | 规则命中(meta) |
| config | 10 | 10 | high | 规则命中(meta) |
| context | 47 | 47 | high | 规则命中(meta) |
| cross | 20 | 20 | high | 规则命中(meta) |
| drift | 17 | 17 | high | 规则命中(meta) |
| event | 9 | 9 | high | 规则命中(meta) |
| fix | 13 | 13 | high | 规则命中(meta) |
| fixtures | 8 | 7 | high | 规则命中(meta) |
| fle | 15 | 15 | high | 规则命中(meta) |
| industry_graph | 4 | 4 | high | 规则命中(meta) |
| integration | 6 | 6 | high | 规则命中(meta) |
| metamorphic | 3 | 3 | high | 规则命中(meta) |
| multi | 7 | 7 | high | 规则命中(meta) |
| orchestrator | 20 | 20 | high | 规则命中(meta) |
| phase | 6 | 6 | high | 规则命中(meta) |
| scripts | 50 | 38 | high | 规则命中(meta) |
| self_check | 22 | 22 | high | 规则命中(meta) |
| shared | 18 | 9 | high | 规则命中(meta) |
| task | 8 | 8 | high | 规则命中(meta) |
| temporal | 5 | 5 | high | 规则命中(meta) |
| utils | 37 | 37 | high | 规则命中(meta) |

### → legacy_zephyr（1 个）

| 目录名 | 递归py | 平铺py | 置信度 | 依据 |
|---|---:|---:|---|---|
| zephyr | 150 | 0 | high | 残局收容 |

### → need_review（21 个）

| 目录名 | 递归py | 平铺py | 置信度 | 依据 |
|---|---:|---:|---|---|
| architecture | 6 | 5 | need_review | 规则未命中; 建议方向 gov? |
| autonomy_core | 3 | 3 | need_review | 规则未命中; 建议方向 ai/gov? |
| capacity | 9 | 9 | need_review | 规则未命中; 建议方向 meta/infra? |
| ce | 7 | 7 | need_review | 规则未命中; 建议方向 ? |
| contracts | 33 | 28 | need_review | 规则未命中; 建议方向 gov? |
| dependency | 7 | 7 | need_review | 规则未命中; 建议方向 gov/infra? |
| digital_twin | 1 | 1 | need_review | 规则未命中; 建议方向 research/trade? |
| external | 5 | 5 | need_review | 规则未命中; 建议方向 infra? |
| f_lifecycle | 20 | 20 | need_review | 规则未命中; 建议方向 meta? |
| feedback | 111 | 23 | need_review | 规则未命中; 建议方向 ai/meta? |
| feedback_loop | 3 | 3 | need_review | 规则未命中; 建议方向 meta? |
| intent | 5 | 5 | need_review | 规则未命中; 建议方向 ai? |
| ops | 2 | 2 | need_review | 规则未命中; 建议方向 infra? |
| pf_alloc | 22 | 21 | need_review | 规则未命中; 建议方向 trade/research? |
| pf_core | 33 | 33 | need_review | 规则未命中; 建议方向 trade/research? |
| pipeline | 14 | 14 | need_review | 规则未命中; 建议方向 data/research? |
| plan_engine | 34 | 34 | need_review | 规则未命中; 建议方向 trade/research? |
| resource | 12 | 12 | need_review | 规则未命中; 建议方向 infra? |
| session | 12 | 12 | need_review | 规则未命中; 建议方向 meta/gov? |
| strategy_factory | 8 | 8 | need_review | 规则未命中; 建议方向 research/trade? |
| strategy_pipeline | 16 | 16 | need_review | 规则未命中; 建议方向 research? |

## 3. tests/zephyr 残局（legacy_zephyr 收容候选）

tests/zephyr 递归 py 总数 = **150**, 顶层平铺 py = 0, 二级子目录 9 个:

| zephyr 二级 | 平铺py | 递归py | 子目录数 |
|---|---:|---:|---:|
| zephyr/data | 115 | 122 | 4 |
| zephyr/factor | 1 | 12 | 2 |
| zephyr/infrastructure | 1 | 4 | 1 |
| zephyr/shared | 0 | 4 | 2 |
| zephyr/regime | 1 | 2 | 0 |
| zephyr/runtime | 1 | 2 | 0 |
| zephyr/trading | 2 | 2 | 0 |
| zephyr/alt_data | 1 | 1 | 0 |
| zephyr/backtest | 1 | 1 | 0 |

### basename 对撞清单（tests/zephyr/** vs tests/其他/**, 有效对撞共 3 对; 其中同相对子路径 0 对; 另有 __init__.py 天然同名噪音 228 对已剔除）

| zephyr 侧文件 | 其他侧同名文件 | 同相对子路径 |
|---|---|---|
| tests/zephyr/data/calendar/test_market_calendar.py | tests/feedback/scheduling/test_market_calendar.py |  |
| tests/zephyr/data/test_metrics.py | tests/backtest/test_metrics.py |  |
| tests/zephyr/data/test_reference_data_manager.py | tests/trading/test_reference_data_manager.py |  |

## 4. 顶层散文件归属建议

| 文件 | 建议 | 依据 |
|---|---|---|
| tests/conftest.py | 原位保留 | pytest 根 conftest(全局 fixture), 移动会破坏收集语义 |
| tests/test_batch_creation_tokens_anchor.py | gov | 文件头 [DOMAIN]=D_GOV_SCRIPTS, creation_tokens 治理锚点 |
| tests/test_generate_governance_map.py | gov | 文件头 [DOMAIN]=D_GOV_SCRIPTS, 治理地图生成器 |

