---
ttl: task_bound
completes_when: P14 终局报告落盘
session: st-maxexec-20260920
issue: MAXEXEC-P5
title: W4-7 后半——UP-2/3/4/5 四条接线挂 TDM + 两雏形 algo_refs（接线记录）
created: 2026-09-20
---

# W4-7 后半接线记录（P5 分包，st-maxexec-20260920，裁定#371）

- 依据：`docs/_working/final3_campaign/w4_7_tdm_absorption_gap.md`（差距表 §3/§4/§5）+ `docs/_working/2026-09-13-tdm-upgrade-blueprint.md`（蓝图"消费端接线"）+ 裁定#371（全程自裁）。
- 能力反查（RULE-CAPABILITY-LOOKUP）：`CapabilityLookup.find('decision_map')` 命中 `tdm_consumption_policy` SOP（S1 差异说明义务已履行：4 目标节点均有主，UP 件=建议位叠加非重复实现）；`find('validation_method_registry')`/`find('decision_algo_registry')` 零命中（无专门卡，注册表自身头注即真源）。

## 1. 形态自裁（差距表建议位 vs TDM 现状冲突处置）

差距表 §4 字段草案写 `module_ref=src/zephyr/pf_alloc/core/*.py`，但 4 目标节点**均有现任主决策模块**（module_ref 非空且为该节点决策所有者）。按 INV-1 真源边界（零件不单独占 module_ref，差距表 §5 明文）+ UP-1 挂载先例（cf84f2861e：algo_note_zh 增补不动 module_ref）+ D108"不加树深"，自裁为：

**DAL-* 算法条目登记（第三批 5 条）+ 节点 algo_refs 挂接 + algo_note_zh 增补（含阈值冻结声明）+ note_confirmed 同 commit 刷新**。module_ref 零改动、节点数 138 不变、边 194 不变。

## 2. 四条接线（UP → TDM 节点）

| # | 模块 | 挂载节点 | DAL 条目 | 阈值冻结（禁挪门柱） | 建议位语义（差距表 §4） |
|---|---|---|---|---|---|
| UP-2 | forward_stop_loss（MOD-PA-020） | TDM-X-S1-02 止损族判定 | DAL-FWD-STOP | P(跌)≥0.65；左尾厚比≥0.60 | 评审建议非强制（正常→评审→执行三态），修订权仍在 X 流五路止损；composite_stop_score 作程度灰度 |
| UP-3 | risk_budget_allocator（MOD-PA-022） | TDM-F-C1 预算切分 | DAL-RISK-BUDGET | 预测 VaR(5%)/CVaR 口径 | C1 预算带仍为上限，带内再分配三模式（inverse_var/risk_parity/sharpe_weight），与 C3-01 历史 Component VaR 双口径并存 |
| UP-4 | sector_distribution_comparator（MOD-PA-023） | TDM-E-L2-01 板块强度综合 | DAL-SECTOR-DIST | PIT（特征≤T-1 预测 T+1）；q05/q50/q95 | 六指数独立分布预测按收益-风险比排序，作强度分排序叠加通道，不改树枝结构 |
| UP-5 | tail_hedge_signal（MOD-PA-024） | TDM-X-R1 应急保命 | DAL-TAIL-HEDGE | CVaR(5%) 破阈=默认 -3% 日损 | 信号仅供决策参考非执行指令，喂 R1-03 白名单通道（D107 弹药回测验证前维持休眠 fallback）；期权执行另案 |

## 3. 两雏形 algo_refs（差距表 §5）

| 零件 | DAL 条目 | 挂载节点 | 备注 |
|---|---|---|---|
| next_day_8state_forecast（MOD-SIG-037） | DAL-8STATE-FCST（新登记） | TDM-E-L0-03（盘后先验生产侧）+ TDM-E-L0-04（盘中消费侧） | L0-04 algo_note 既有挂名，本轮补正式 refs |
| scenario_probability_model（MOD-PLAN-017） | DAL-SCEN-PROB（**存量已有**，差距表"未登记"判断过时——本轮复核注册表已存在，仅补引用） | TDM-E-L0-01（计划生成） | algo_note 补注九格情景概率输入 + algo_refs 挂接 |

## 4. 验证方法登记（蓝图"每条引用需 validation_method_registry 登记"的落地口径）

validation_method_registry（REG-VALM-001）自身 INVARIANTS：节点不加 YAML 字段、方法由 layer+flow+形态推导。4 节点按 derivation_rules 自动落位：X-S1-02/X-R1→exit_counterfactual；F-C1→portfolio_attribution；E-L2-01→agg_discrimination。方法映射已写入 DAL 第三批批次注释留痕；阈值冻结落在 DAL mechanism_zh（先例=DAL-CIRCUIT-5 阈值入机制文本）+ 模块代码常量（0.65/-0.03 等模块默认参数）。

## 5. node_verdict 台账裁定

蓝图"落图批=TDM YAML+node_verdict 台账同 commit"，但台账 DDL 真源（schemas/categories/backtest/backtest_node_verdict.py）明文：行由验证 runner 写入、verdict_reason **禁 AI 手填**。接线批无回测成绩可记，**不伪造台账行**；UP-2..5 的 A/B 回测验证欠账由后续回测批经 runner 自然落账（与 UP-1"仅剩 A/B 回测对比验证待跑"同状态）。

## 6. 验收实测（2026-09-20）

- `check_decision_map.run_checks()`：**fails=0 / warns=115 / nodes=138**；warns 与基线（HEAD 版本）完全一致（R1×23 红节点占位/R39×50/R16×1/R23×1/R24×2/R25×8/R22×16/R11×14），零新增。
- 成环检测：sequence 边=**0 环**（R8 正典口径）；父子边=**0 环**（R16）；feed 前向回边 6 条=存量设计性跨日反馈闭环（F-C3 归因→L0 计划/P3-04→E-L4/L4 盘中回环/F-C2 聚合回环），本批零加边、环比基线不变。
- 改动面：`config/trading_decision_map.yaml`（7 节点：4 UP 挂接+2 雏形 refs+L0-01 补注）、`docs/01_policies_and_standards/_registry/catalogs/decision_algo_registry.yaml`（27→32 条）。

## 7. 未完成与后续

- UP-1（vol_target_allocator）按差距表 §4 无需挂载（TDM-E-L1 algo_note 已声明），A/B 回测对比仍待跑（与本批 UP-2..5 同欠账）。
- 蓝图 `2026-09-13-tdm-upgrade-blueprint.md` 结案报告头部"接线待施工"表述待清理批复核刷新（本记录+commit 为真源）。
- R11 数据新鲜度 14 条 warn（CH 四态）为运行时状态，非本批范围。
