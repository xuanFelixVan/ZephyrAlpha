---
ttl: task_bound
completes_when: 总筹对审消费且 TDM 挂载裁决落地后本件转归档参考
title: "任务B·TDM 覆盖账本 v1（机生）"
owner: st-tdm-mount-flash-20261003
generation: machine_generated
generator: scripts/generate_map_coverage_ledger.py
anchor: ""
---

# TDM 覆盖账本 v1（双向对账，机生）

> 人口侧=23 交易相关域蓝图 module_id 全集；挂载侧=config/trading_decision_map.yaml module_id 集 + module_ref 折算模块集。净零申报：替代 docs/_working/map_census/00_panorama_map_census_v1.md 手工普查段（原册保留历史快照）。

## 计数（字段，勿散文引用）

- population_with_id: 302
- population_unique_module_ids: 300
- population_duplicate_ids: 2
- mounted: 67
- unmounted_orphan: 233
- cross_domain_mount: 9
- mounted_unresolved: 0
- tdm_module_id_unique: 97
- tdm_module_ref_unique: 113
- ref_folded_to_module: 110
- ref_folded_unique_modules: 96
- ref_unresolved: 3
- trading_domains: 22

## 已挂(mounted)｜已挂（人口∩挂载面）（67 行）

| # | module_id |
|---|---|
| 1 | MOD-BT-001 |
| 2 | MOD-EX-001 |
| 3 | MOD-INF-018 |
| 4 | MOD-L03-001 |
| 5 | MOD-L05-001 |
| 6 | MOD-L06-001 |
| 7 | MOD-PA-003 |
| 8 | MOD-PA-007 |
| 9 | MOD-PF-007 |
| 10 | MOD-PLAN-001 |
| 11 | MOD-PLAN-003 |
| 12 | MOD-PLAN-022 |
| 13 | MOD-PLAN-024 |
| 14 | MOD-PLAN-025 |
| 15 | MOD-POS-001 |
| 16 | MOD-POS-002 |
| 17 | MOD-POS-003 |
| 18 | MOD-POS-004 |
| 19 | MOD-POS-010 |
| 20 | MOD-POS-021 |
| 21 | MOD-POS-022 |
| 22 | MOD-POS-024 |
| 23 | MOD-POS-026 |
| 24 | MOD-POS-027 |
| 25 | MOD-POS-028 |
| 26 | MOD-POS-030 |
| 27 | MOD-REGIME-001 |
| 28 | MOD-REGIME-002 |
| 29 | MOD-REGIME-005 |
| 30 | MOD-REGIME-012 |
| 31 | MOD-REGIME-016 |
| 32 | MOD-RK-049 |
| 33 | MOD-RK-050 |
| 34 | MOD-RK-09 |
| 35 | MOD-SELL-000 |
| 36 | MOD-SELL-001 |
| 37 | MOD-SELL-003 |
| 38 | MOD-SELL-004 |
| 39 | MOD-SELL-005 |
| 40 | MOD-SELL-007 |
| 41 | MOD-SELL-019 |
| 42 | MOD-SIG-056 |
| 43 | MOD-SIG-057 |
| 44 | MOD-SIG-060 |
| 45 | MOD-SIG-062 |
| 46 | MOD-SIG-086 |
| 47 | MOD-SIG-089 |
| 48 | MOD-SIG-090 |
| 49 | MOD-SIG-093 |
| 50 | MOD-SIG-098 |
| 51 | MOD-SIG-118 |
| 52 | MOD-SIG-135 |
| 53 | MOD-SIG-136 |
| 54 | MOD-SIG-137 |
| 55 | MOD-SIG-138 |
| 56 | MOD-SIG-139 |
| 57 | MOD-SIG-140 |
| 58 | MOD-SIG-141 |
| 59 | MOD-SIG-142 |
| 60 | MOD-SIG-143 |
| 61 | MOD-SIG-151 |
| 62 | MOD-SIGQC-004 |
| 63 | MOD-TDMVAL-001 |
| 64 | MOD-TRADING-008 |
| 65 | MOD-TRADING-013 |
| 66 | MOD-XS-016 |
| 67 | MOD-XS-018 |

## 未挂孤儿(unmounted_orphan)｜未挂孤儿（人口−挂载面，红区=任务C 输入全集）（233 行）

| # | module_id |
|---|---|
| 1 | MOD-AU-001 |
| 2 | MOD-AU-002 |
| 3 | MOD-AU-005 |
| 4 | MOD-AU-006 |
| 5 | MOD-AU-007 |
| 6 | MOD-AU-008 |
| 7 | MOD-AU-009 |
| 8 | MOD-AU-010 |
| 9 | MOD-AU-011 |
| 10 | MOD-AU-012 |
| 11 | MOD-AU-013 |
| 12 | MOD-AUDITTEST-001 |
| 13 | MOD-BT-018 |
| 14 | MOD-BT-019 |
| 15 | MOD-BT-020 |
| 16 | MOD-BT-021 |
| 17 | MOD-BT-022 |
| 18 | MOD-BT-023 |
| 19 | MOD-BT-024 |
| 20 | MOD-BT-026 |
| 21 | MOD-BT-027 |
| 22 | MOD-BT-028 |
| 23 | MOD-DT-001 |
| 24 | MOD-EX-002 |
| 25 | MOD-EX-003 |
| 26 | MOD-EX-049 |
| 27 | MOD-EX-050 |
| 28 | MOD-EX-055 |
| 29 | MOD-EX-056 |
| 30 | MOD-EX-057 |
| 31 | MOD-EX-063 |
| 32 | MOD-EX-064 |
| 33 | MOD-EXE-AGENTS |
| 34 | MOD-EXSIM-001 |
| 35 | MOD-FAC-001 |
| 36 | MOD-FAC-002 |
| 37 | MOD-FAC-003 |
| 38 | MOD-FAC-004 |
| 39 | MOD-FAC-005 |
| 40 | MOD-FAC-006 |
| 41 | MOD-FAC-007 |
| 42 | MOD-FACTORY-001 |
| 43 | MOD-FACTORY-002 |
| 44 | MOD-INF-019 |
| 45 | MOD-INF-021 |
| 46 | MOD-L02-001 |
| 47 | MOD-L02-027 |
| 48 | MOD-L02-LIFECYCLE |
| 49 | MOD-L04-001 |
| 50 | MOD-L11-001 |
| 51 | MOD-L13-001 |
| 52 | MOD-MKT-001 |
| 53 | MOD-MKT-002 |
| 54 | MOD-MKT-003 |
| 55 | MOD-MKT-004 |
| 56 | MOD-MKT-005 |
| 57 | MOD-MKT-006 |
| 58 | MOD-MKT-007 |
| 59 | MOD-ML-010 |
| 60 | MOD-ML-011 |
| 61 | MOD-ML-012 |
| 62 | MOD-ML-013 |
| 63 | MOD-ML-014 |
| 64 | MOD-ML-015 |
| 65 | MOD-ML-016 |
| 66 | MOD-ML-017 |
| 67 | MOD-ML-018 |
| 68 | MOD-ML-019 |
| 69 | MOD-ML-020 |
| 70 | MOD-ML-021 |
| 71 | MOD-ML-022 |
| 72 | MOD-PA-002 |
| 73 | MOD-PA-004 |
| 74 | MOD-PA-006 |
| 75 | MOD-PA-013 |
| 76 | MOD-PA-014 |
| 77 | MOD-PA-015 |
| 78 | MOD-PF-001 |
| 79 | MOD-PF-002 |
| 80 | MOD-PF-003 |
| 81 | MOD-PF-006 |
| 82 | MOD-PF-008 |
| 83 | MOD-PF-009 |
| 84 | MOD-PF-010 |
| 85 | MOD-PF-011 |
| 86 | MOD-PF-012 |
| 87 | MOD-PF-013 |
| 88 | MOD-PF-014 |
| 89 | MOD-PLAN-002 |
| 90 | MOD-PLAN-004 |
| 91 | MOD-PLAN-005 |
| 92 | MOD-PLAN-006 |
| 93 | MOD-PLAN-007 |
| 94 | MOD-PLAN-019 |
| 95 | MOD-PLAN-020 |
| 96 | MOD-PLAN-021 |
| 97 | MOD-PLAN-023 |
| 98 | MOD-POS-006 |
| 99 | MOD-POS-007 |
| 100 | MOD-POS-008 |
| 101 | MOD-POS-009 |
| 102 | MOD-POS-016 |
| 103 | MOD-POS-017 |
| 104 | MOD-POS-020 |
| 105 | MOD-POS-025 |
| 106 | MOD-POS-029 |
| 107 | MOD-REGIME-006 |
| 108 | MOD-REGIME-007 |
| 109 | MOD-REGIME-011 |
| 110 | MOD-REGIME-013 |
| 111 | MOD-REGIME-014 |
| 112 | MOD-RK-011 |
| 113 | MOD-RK-042 |
| 114 | MOD-RK-043 |
| 115 | MOD-RK-044 |
| 116 | MOD-RK-045 |
| 117 | MOD-RK-046 |
| 118 | MOD-RK-048 |
| 119 | MOD-RK-05 |
| 120 | MOD-RK-06 |
| 121 | MOD-RK-07 |
| 122 | MOD-RK-08 |
| 123 | MOD-RK-10 |
| 124 | MOD-RK-12 |
| 125 | MOD-RK-13 |
| 126 | MOD-RK-14 |
| 127 | MOD-RK-15 |
| 128 | MOD-RK-16 |
| 129 | MOD-RK-18 |
| 130 | MOD-RK-19 |
| 131 | MOD-RK-20 |
| 132 | MOD-RK-21 |
| 133 | MOD-RK-23 |
| 134 | MOD-RK-26 |
| 135 | MOD-RK-28 |
| 136 | MOD-RK-29 |
| 137 | MOD-RK-30 |
| 138 | MOD-RK-31 |
| 139 | MOD-RK-32 |
| 140 | MOD-RK-33 |
| 141 | MOD-RK-34 |
| 142 | MOD-RK-35 |
| 143 | MOD-RK-36 |
| 144 | MOD-RK-37 |
| 145 | MOD-RK-38 |
| 146 | MOD-RK-39 |
| 147 | MOD-RK-40 |
| 148 | MOD-RK-41 |
| 149 | MOD-SELL-006 |
| 150 | MOD-SELL-008 |
| 151 | MOD-SELL-009 |
| 152 | MOD-SELL-015 |
| 153 | MOD-SELL-016 |
| 154 | MOD-SIG-058 |
| 155 | MOD-SIG-059 |
| 156 | MOD-SIG-061 |
| 157 | MOD-SIG-063 |
| 158 | MOD-SIG-087 |
| 159 | MOD-SIG-088 |
| 160 | MOD-SIG-091 |
| 161 | MOD-SIG-092 |
| 162 | MOD-SIG-094 |
| 163 | MOD-SIG-095 |
| 164 | MOD-SIG-096 |
| 165 | MOD-SIG-097 |
| 166 | MOD-SIG-099 |
| 167 | MOD-SIG-100 |
| 168 | MOD-SIG-101 |
| 169 | MOD-SIG-102 |
| 170 | MOD-SIG-103 |
| 171 | MOD-SIG-104 |
| 172 | MOD-SIG-105 |
| 173 | MOD-SIG-106 |
| 174 | MOD-SIG-107 |
| 175 | MOD-SIG-108 |
| 176 | MOD-SIG-109 |
| 177 | MOD-SIG-110 |
| 178 | MOD-SIG-111 |
| 179 | MOD-SIG-112 |
| 180 | MOD-SIG-113 |
| 181 | MOD-SIG-114 |
| 182 | MOD-SIG-115 |
| 183 | MOD-SIG-116 |
| 184 | MOD-SIG-117 |
| 185 | MOD-SIG-119 |
| 186 | MOD-SIG-120 |
| 187 | MOD-SIG-121 |
| 188 | MOD-SIG-122 |
| 189 | MOD-SIG-123 |
| 190 | MOD-SIG-124 |
| 191 | MOD-SIG-125 |
| 192 | MOD-SIG-126 |
| 193 | MOD-SIG-127 |
| 194 | MOD-SIG-128 |
| 195 | MOD-SIG-129 |
| 196 | MOD-SIG-130 |
| 197 | MOD-SIG-131 |
| 198 | MOD-SIG-132 |
| 199 | MOD-SIG-133 |
| 200 | MOD-SIG-144 |
| 201 | MOD-SIG-145 |
| 202 | MOD-SIG-146 |
| 203 | MOD-SIG-147 |
| 204 | MOD-SIG-148 |
| 205 | MOD-SIG-149 |
| 206 | MOD-SIG-150 |
| 207 | MOD-SIGQC-003 |
| 208 | MOD-SIGQC-005 |
| 209 | MOD-SIGQC-006 |
| 210 | MOD-SIM-002 |
| 211 | MOD-SIM-003 |
| 212 | MOD-SIM-005 |
| 213 | MOD-SIM-012 |
| 214 | MOD-SIM-021 |
| 215 | MOD-SIM-022 |
| 216 | MOD-SIM-023 |
| 217 | MOD-SIM-024 |
| 218 | MOD-SIM-028 |
| 219 | MOD-TRADING-002 |
| 220 | MOD-TRADING-003 |
| 221 | MOD-TRADING-004 |
| 222 | MOD-TRADING-009 |
| 223 | MOD-TRADING-010 |
| 224 | MOD-TRADING-011 |
| 225 | MOD-TRADING-012 |
| 226 | MOD-TRADING-014 |
| 227 | MOD-TRADING-015 |
| 228 | MOD-TRIG-001 |
| 229 | MOD-VOTE_REVIEW_SHELL |
| 230 | MOD-XS-008 |
| 231 | MOD-XS-015 |
| 232 | MOD-XS-017 |
| 233 | MOD-XS-019 |

## 跨域挂载(cross_domain_mount)｜跨域挂载（挂载面外域 id=伸手进交易流程）（9 行）

| # | module_id | depgraph 域 |
|---|---|
| 1 | MOD-ALT-010 | D_ALT_DATA |
| 2 | MOD-DATA-069 | D_DATA |
| 3 | MOD-DATA-L9AGG | D_DATA |
| 4 | MOD-ENTITY-GRAPH | D_DATA |
| 5 | MOD-GOV-CHAINRECON | D_GOVERNANCE |
| 6 | MOD-INT-AISA | D_INTELLIGENCE |
| 7 | MOD-INT-CHAIN-IMPACT | D_INTELLIGENCE |
| 8 | MOD-INT-NEWS-CHAIN | D_INTELLIGENCE |
| 9 | MOD-L00-004 | D_ALT_DATA |

## mounted_unresolved｜挂载面无主 id（depgraph 无域记录，不判域不编造）（0 行）

| # | module_id |
|---|---|

## module_ref 未折算清单（3 条，depgraph 无精确路径且包名无节点）

- scripts/backtest/mcts_expression_search.py
- scripts/entity_graph/equity_penetration.py
- scripts/governance/reconcile_chain_refs.py

## 人口缺 ID 蓝图（4 个，=任务A 未匹配清单同源）

- docs/03_modules/_domain_ml_serve/codegen_model_adapter/blueprint.md（blueprint_id=MOD-MLS-003，域=D_ML_SERVE）
- docs/03_modules/_domain_ml_serve/deep_review_model_adapter/blueprint.md（blueprint_id=MOD-MLS-004，域=D_ML_SERVE）
- docs/03_modules/_domain_ml_serve/model_compression_accelerator/blueprint.md（blueprint_id=MOD-MLS-002，域=D_ML_SERVE）
- docs/03_modules/_domain_ml_serve/model_drift_monitor/blueprint.md（blueprint_id=MOD-MLS-001，域=D_ML_SERVE）
