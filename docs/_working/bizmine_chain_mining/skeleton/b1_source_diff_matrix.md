---
ttl: task_bound
completes_when: 五独立真源两两差集全部落表且未归入环节对象清单已逐条归口或点名留档
title: 环节枚举差集矩阵（≥5 独立真源两两差集，仪器=fullflow §4.1 遗漏自检法）
owner: ZephyrAlpha-Owner
language: zh
status: B3 批待外部方法学源回填
created: 2026-09-19
session: st-bizmine2-20260919
---

# 0. 仪器与判据

- 方法来源：`docs/_working/fullflow_campaign/FLOWTHROUGH_ACCEPTANCE_SPEC.md` §4.1（L115-129）——≥5 个独立真源各导环节清单 → 两两求差集 → 判据「任一真源出现但未归入任何环节的对象数=0」。
- **先例教训（必读，本战役据此定诚实口径）**：fullflow 的 R-024C（`COORDINATION_LEDGER.md` 约 L490-525）实测推翻了自己骨架的「未归属=0」——7 真源里 B=2（D_ORDER/D_PORTFOLIO）、F=10 未归口，那个 0 是**人工兜底后的 0**，结论原话「"无遗漏"不得作交付声明」；且 17 推导环节 vs 16 段 = COVERAGE-DIFF 判黄。本战役据此：**只声明机械可复核的收敛，不声明绝对无遗漏**，残余差集必须点名留档。
- 骨架查重前置（skeleton_mining_policy §1「查重先查骨架，防重复建源」）：本仓已存在一条 alpha 链的官方阶段轴 = `config/strategy_production_map.yaml` 的 **E0-E9**（策略工厂十段），本骨架以它为锚做超集扩展，不另造一套命名。

# 1. 五独立真源清单（各源导出的环节枚举，原词保留）

| 源 | 路径 | 导出的阶段（原词） |
|---|---|---|
| S1 SOP/方法论层 | `sop/mining_sop/`(3 件)、`construction_sop/construction_workflow_policy.md`、`backtest_system_sop/sop_a|b|c`、`sop/trading_decision_map_sop/`、`data_ops_sop/data_source_onboarding_sop.md`、`docs/_working/bizmine_night/factor_sop_screen/factor_mining_sop_v0_1.md`+`strategy_sop_gap_report.md` | 挖矿：触发→六向→轮次/枯竭→时间盒→四闸→自审闸三态→日志；施工：Step 0-12(+1.5/1.8/1.9/3.5，标称"15 步"实列 17 节点)；回测 A0-A5；七步 ①算法调研②数据需求③缺口取数④宽回测⑤噪音剪枝⑥窄回测⑦归档三出口；入库 C1-C6；TDM S1-S9；数据接入 §1-§10；因子链 S0-S7；缺口 G1-G10 |
| S2 注册表/架构层 | `battle_map_domain_policy.yaml`(flow_stage 11 段+FF-13~16)、`functional_domain_registry.yaml`、`config/strategy_production_map.yaml`(E0-E9)、`registry_of_registries.yaml`(REG-FCT/STR/EXP/BTB/CAND/PFM/ML/VALM/UNI/BMK/CST/RISK-TIER/DAL/DAL)、`docs/02_enterprise_architecture/06_decision_architecture/index.md`(L0-L6 层/四轨)、`config/trading_decision_map.yaml`(flow+layer+state_matrix) | flow_stage：research_incubation/model_training/backtest_validation/simulation_validation/stock_selection/…；工厂：E0 算力闸·E1 进货·E2 假说预审·E3 构造·E4 考试咽喉·E5 协同去重·E6 入库监控·E7 模拟盘前哨·E8 组装分配·E9 实盘归因；生命周期态：因子 candidate→experimental→active→deprecated→retired / 策略 candidate→backtest→sim→paper→live→monitoring→decayed→retired / 五态 certified-probation-failed-retired-resurrected；products 五类含 negative_archive |
| S3 代码/自动化实装层 | `scripts/backtest/{compute_window_gate,lane_b_idea_generator,lane_c_formula_miner,lane_c2_agentic_miner,mcts_expression_search,lane_g_stomach_intake,three_high_screen,factory_intake_pipeline,hypothesis_precheck,hypothesis_translator,factory_grid_executor,factory_grid_anova,f06_e4_wfa_exam,c4_batch_screen,strategy_screen_c2,promotion_combo_gate,forward_post,sim_*}.py`、`src/zephyr/{research,factor/analysis,factor/governance,strategy_pipeline,pf_alloc,pf_core,regime,signal_ashare/strategy_signal,backtest/core}/` | 与 E0-E9 同轴实装齐（E7 登记滞后 map=pending）；**查无**：窄考执行器、预注册卡机器可读件与校验器、端到端自动挖矿编排器、E8 装配落库/E9 决策时间戳闭环；**空壳**：`src/zephyr/red_blue_validator/`（43 行 `__init__.py`，却被多处当先例引用）；**孤儿实装（有代码+测试、零生产消费端）**：`research/factor_mining_pipeline.py:run_factor_mining`、`factor_vote_mining.py`、`gp_strategy_discovery.py`、`llm_evolutionary_search.py`、`auto_feature_discoverer.py`、`factor_model_co_evaluator.py`、`strategy_iteration_upgrader.py`、`backtest/services/decay_monitor.py`（`scripts/governance/register_deferred_modules.py:210` 登记"暂缓"）；`data/capability_cards/` 中因子挖掘/考试/组合/上产 **零张卡** |
| S4 历史战役/在办工作层 | `docs/_working/fullflow_campaign/`（FF-01..16+R-024C 差集）、`docs/_working/bizmine_night/`（21 车道目录）、`residual_construction/00_master_ledger.md`、`kimi_audit/`（S12-S15、B 族尺子未签、#304）、`tdchain_mine/` | 车道按**数据面**切（图形/指标/另类/板块/tick/币圈/灰度），未按链路面切 ⇒ 链路面从未度量；已点名空档 5 条（见 §3 未覆盖） |
| S5 外部方法学层 | 由外部矿脉车道回填（机构 alpha 研究流水线阶段划分 + 开源先例 + 学术过拟合防御框架），带 URL+发布方+年份 | 待回填（本件 §5 占位；未回填前本骨架不得宣布三扫收敛） |

# 2. 两两差集（关键差异，S5 未回填故其行待补）

| 差集 | 结果 |
|---|---|
| S1 vs S2 | S1 无「算力/作业闸」段（E0 只在 S2/S3）；S1 无「协同去重」（E5）与「实盘归因」（E9）独立段——只在归因反馈里被提；S2 无「预注册卡的机器可读件」概念（REG-BTB-001 只到 threshold_status 冻结）；两套生命周期命名（S2 三套并存）在 S1 只有 factor_mining_sop 一列 |
| S1 vs S3 | S1 `factor_mining_sop_v0_1` 的 S3 预注册卡、S6 组队备料在 S3 代码**无执行件**（卡是 .md，窄考协议是 .md）；S3 的 E0 算力闸/E5 去重/E7 前哨在 S1 八段**无对应步骤**；S1 无「自动化编排」段，S3 实测该段查无实装 |
| S2 vs S3 | E7 在 S2/E-map 标 pending 而 S3 有 `sim_*.py`+测试（登记滞后=状态盲区，骨架 SOP §2 第四宗罪的现行样本）；S3 八个孤儿实装在 S2 无任何注册表归口（有矿无人采） |
| S3 vs S4 | S4 的 21 车道全部落在 S3 的 E1-E4 与 AM-02 段（初筛/考试/数据），**E5 之后几乎无车道**（去重、预注册机器化、窄考执行器、编排层=零产出）；`red_blue_validator` 空壳被 S4 红蓝报告当"先例"引用（虚假锚点） |
| S4 vs S1 | S1 的 G1（假设生成）、G2（因子→策略组装）、G8（负结果台账）、G10（数据面复核）与 S4 点名的 5 空档一一对应 ⇒ 两个独立层同向指认同一批缺段=可信度高（非单源断言） |

# 3. 未归口对象清单（诚实面：逐条点名，不兜底为 0）

S3 有实装而 E0-E9/flow_stage 未归口：8 件孤儿（`factor_mining_pipeline` 等，上表已列）→ 本骨架归口于 AM-04/AM-05/AM-06/AM-13（见 b0 归口列），归口判据=生产者相同。
S1 有步骤而 S2 无注册表承载：`sop_b ③缺口取数`、`data_source_onboarding §7 调度/§10 运维退役`、`tdm_consumption S8 复盘`、`S9 转级` → 归口 AM-02/AM-12/AM-14。
SOP 层与战役层共同指认、代码与注册表**双查无**（真遗漏，5 条）：
1. 预注册卡机器可读+校验器（卡目前是人写 .md，无闸拦"未 frozen 先取数"）；
2. 窄考执行器（协议只在 docs，无件）；
3. 端到端自动挖矿编排器（E1-E4 只有手工 CLI + `pipeline_events` 事件队列）；
4. 归因→假设再生的闭环件（FF-12→FF-02，E9 输出未回灌 E1/E2）；
5. 数据债→自动重考触发（`known_data_gaps.yaml` 有条目、无触发器）。
另：fullflow 遗留未归口 `D_ORDER`/`D_PORTFOLIO`（B 源 2 条）在本链外（属下单/组合运行域），点名留档不硬收编。

# 4. 批次志（骨架增量曲线，封矿判据②的实测面）

| 批次 | 日期 | 视角 | 新增环节 | 累计 |
|---|---|---|---|---|
| B0 | 09-19 | 查既有骨架（E0-E9 锚） | 10（E0-E9 直取） | 10 |
| B1 | 09-19 | 四路内部真源差集（S1-S4） | +6（算力闸外的自动化编排/预注册机器化/窄考执行/正交去重独立化/归因再生闭环/监控退役独立化） | 16 |
| B2 | 09-19 | 逐环节深挖（16 车道实查改标） | 待回填 | 待回填 |
| B3 | 09-19 | 外部方法学（S5：机构流水线+开源+学术防御框架） | 待回填 | 待回填 |
| B4 | 09-19 | 三重扫描收口批（按生产者/按形态资产类/按消费者文献） | 待回填 | 待回填 |

收敛判据：B2 与 B3 各自新增=0 且 B4 三扫无新枝 ⇒ 拉平，方可写封顶声明（a4）。

# 5. S5 外部方法学源（占位，待外部矿脉车道回填 URL+发布方+年份）

待答三问：①机构 alpha 研究流水线的阶段划分与我们的 E0-E9 有何差集（尤其 capacity/decay 管理、research ops 版本化）；②开源先例（qlib / RD-Agent / alphalens / gplearn / Nautilus / Optuna）各自的环节边界；③过拟合防御学术框架（CSCV/PBO、Deflated Sharpe、t>3 门槛、regime-conditional timing）应落在我们哪一环节、现有件是否够。**未回填前本骨架不得宣布三扫收敛。**
