---
ttl: task_bound
title: 量化方法论总册（Owner 直批六主题）+ 三定向调查附录
owner: ZephyrAlpha-Owner
language: zh
created: "2026-09-24"
status: active
session: quant-methodology-mining
approval: Owner 直批立项（六主题清单见总指挥批文）
execute_discipline: 挖矿 SOP v1.4.0（docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md）
next_action: 落地时由总指挥统一 CREATE-GUARD 登记 + git_commit.py 入队（本班禁 commit）
---

# 量化方法论总册——总目录与挖矿日志

> **一句话读法**：这是"方法的立法理由书"，不是操作手册——每个主题回答"为什么这么定口径"，并给出现行项目资产（文件路径）与机构做法（书/论文出处）的对照。落地施工另走 construction 闭环。

## 一、分册清单

| 分册 | 主题 | Owner 批准议题 |
|------|------|---------------|
| [01_caliber_law.md](01_caliber_law.md) | 口径立法 | 条件格子层用期望值+Wilson 置信下界，策略层用夏普/卡玛——两层分工与理由；胜率单独用的坑 |
| [02_overfitting_defense.md](02_overfitting_defense.md) | 过拟合防线总册 | 多重比较问题；DSR 与 PBO；CPCV；预注册+闭卷考+成本门三件套与新工具的组合防线 |
| [03_conditional_stats_spec.md](03_conditional_stats_spec.md) | 条件概率表统计规范 | Wilson 置信下界；分层贝叶斯收缩；MIN_OBS 现行值；小样本"明示不作数"纪律 |
| [04_switch_friction.md](04_switch_friction.md) | 切换摩擦治理 | 滞回带（置信不够不移交）；最短任职期；换仓成本预算 |
| [05_drift_reestimation.md](05_drift_reestimation.md) | 漂移监控与重估循环 | 定期重估节奏；漂移降权规则；衔接现有监控自动化/对账文化 |
| [06_institutional_benchmark.md](06_institutional_benchmark.md) | 机构对照与先进做法分级 | 骨架层对照；可直接引入/关注不必急/项目已具备 三档分级 |

## 二、三个定向调查附录（Owner 点名追凶）

| 附录 | 问题 | 结论一句话 |
|------|------|-----------|
| [appendix_A_retired_strategies.md](appendix_A_retired_strategies.md) | 退役策略档案在哪（~800/退役600+/现役161 口径追凶） | 单一"退役档案"不存在；退役=漏斗出局+并入宿主+deprecated 三种机制，可机读账本三处，strategy_archive/ 已建成但空 |
| [appendix_B_tick_vs_minute.md](appendix_B_tick_vs_minute.md) | tick vs 分钟有没有已成文结论 | 无独立成文裁决；隐含口径=分钟做信号（5 年历史）、tick 做执行增强（3s L1、无逐笔）；METHOD_MINING_t0.md 目前只在 worktree 未落主区 |
| [appendix_C_six_state_truth_chain.md](appendix_C_six_state_truth_chain.md) | 六段温度真源链与 601 vs 1,051 日分叉 | 法定真源=SIX_STATES+REGIME_STATE_TO_ACTIVATION_PHASE；分叉=auto_mount.R2SIX（法定侧）vs daily_decision_orchestrator.REGIME_TO_SEGMENT（产线占位）；修复清单 6 条只列不施工 |

## 三、挖矿日志（SOP §7 强制——无日志=没挖过）

矿脉=主题；每轮=内部反查+外部搜索双动作；判定 signal/noise/受阻/查无。

| 轮 | 矿脉 | 内部反查（路径证据） | 外部搜索 | 判定 |
|----|------|--------------------|----------|------|
| R1 | 治理框架 | mining_sop/index.md + mining_sop_policy.md v1.4.0（六向/四闸/日志纪律） | 无需 | signal |
| R2 | 口径立法 | pattern_win_rate_provider.py（Wilson LB 加权口径=M1 裁定）；search_space_prereg.yaml（cost_adjusted_sharpe 主目标）；exam_scale_cost_gate.yaml（换手 8x 推导） | DSR 出处（Bailey 官网/SSRN/JPM 2014） | signal |
| R3 | 过拟合防线 | 62_business_registry_construction.md §4.13 G2（PBO>0.2/CPCV std-mean>0.5/White RC 落地记录）；n_trial_ledger.py；deflated_sharpe_calculator.py（全仓 DSR 唯一真源） | PBO（JCF 2017 20(4) 39-69）；CPCV（AFML Wiley 2018）；trial 相关性修复（Soloviov 2026-07，62 号转引） | signal |
| R4 | 条件概率统计 | condition_package.py（_CELL_FLOOR_DAYS=30 30 日地板+禁凑 n）；market_pattern_win_rate `__baseline__` 行（收缩先验天然挂点）；MIN_OBS 全家实测枚举 | empirical Bayes beta-binomial（Robinson 2016 varianceexplained；Bayes Rules! ch3） | signal |
| R5 | 切换摩擦 | daily_decision_orchestrator.py:95-96（过渡带 0.60×0.5 折减）；msprt_champion_challenger.py（MOD-PF-008 序贯晋升）；turnover_gate cap 8x | LuxAlgo 2026-08/ArrowAlgo 2026-05/DeepTradeX 2026-07（memo55 已存 URL，转引） | signal |
| R6 | 漂移监控 | gov_drift/model_drift_monitor.py；factor/governance/lifecycle_state_machine.py（retired 终态）；feedback_loop/detectors/drift/*；alert_threshold_registry（REG-ATH-001）；decision_gate 偏离 >30%/50% | 无新增（内部富矿，SOP §8"内部轮占比~40%"印证） | signal（纯内部） |
| R7 | 机构对照 | regime_detector.py REGIME_STATES 7 态；framework_composer 合成面板+sleeves；STR-VREV-024 盘口失衡；kill_switch | meta-labeling（AFML §3.8/Hudson&Thames）；LinUCB（Chu et al. 2011）；Cartea et al. 2023 SSRN；Ni et al. 2023 | signal |
| R8 | 调查A：退役档案 | strategy_registry.yaml 实测 161；strategy_archive/（空，仅 README）；29_factor_strategy_extraction.md（docs/_archive/，非 design_memos 现行位）；sop_c（聚宽 600 漏斗）；c4_deferrals.csv（322 行） | 无需（内部追凶） | signal+查无（"单一退役账本"查无=有效结论） |
| R9 | 调查B：tick vs 分钟 | 主区 docs/_working/t0_matrix/ 无 METHOD_MINING_t0.md；worktree st-t0-matrix-20260924 内同名件全文读；t0_ceiling_verdict 转引 | 无需 | signal |
| R10 | 调查C：六段真源链 | environment_switch.py:41；framework_composer.py:153；auto_mount.py:129；daily_decision_orchestrator.py:110；t0_matrix/LEDGER.md D-14（601 vs 1,051 实测） | 无需 | signal |

**受阻/查无登记**：①"退役策略统一账本"查无——不是漏挖，是结构性不存在（见附录A §3）；②"分钟级 vs tick 级"独立成文裁决查无——结论散在 34 法卡评级与判读总纲里（见附录B §2）。两者均按 SOP 记档为有效结论，防后人重挖。

**防噪音四闸自检**：外部论断全部带 URL+发布方+年份（含转引注明"转引"）；A股适配闸=62bp 成本口径/T+1/程序化报撤单约束贯穿各册；可回测闸=每个新工具都给了"用现有哪台考试机器考它"的挂点；交叉验证闸=关键结论（六段分叉/退役口径）均有 ≥2 独立仓内证据。

## 四、全资产净零声明（宪法 §4）

本总册=纯文档产出，零新增 gate/脚本/配置；每册引用的现行资产全部已存在。册内"新立建议"（如最短任职期）均标【新立提案】并给 net_zero 对价说明，未经裁定不施工。
