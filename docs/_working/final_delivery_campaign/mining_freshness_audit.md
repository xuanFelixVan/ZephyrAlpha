---
ttl: task_bound
title: "M6 保鲜抽验矿道——全流通 132 案卷新鲜度审计报告"
session: st-finaldel-m6-20260929
---

# M6 案卷保鲜抽验审计（2026-09-29）

> 审计对象：`docs/_working/fullconnect_campaign/` 12 内容段（+00_skeleton 骨架段，合计 13 目录）F01-F132 共 132 卷。
> 挖干基线：2026-09-27/28 落库；审计切片：`git log --since=2026-09-28T00:00`（审计时 HEAD=31c38c5205，分支 dev）。
> 纪律：全程只读，本文件为唯一新写文件；未改任何既有案卷/代码；未 commit（总筹统一收口）。
> 附注：本 .md 的 CREATE-GUARD creation_token 未登记（登记面属既有册，依"只写 1 文件"纪律留给总筹随批补登）。

## 0. 审计口径

- **清点**：逐卷 grep `自审闸三态` 节提取三态裁定原文；F 号由文件名 `_fNN_` 机械解析，全集=132/132，无缺号无重号。
- **新鲜度矩阵**：每段抽首卷+末卷共 24 卷，正则提取卷内（六向台账为主）引用的 src/scripts/config/docs/data/tests 系真源路径，逐路径跑 `git log --since=2026-09-28T00:00 --oneline -- <path>`；非空=STALE。路径缺目录前缀的按 basename 经 `git ls-files` 解析。
- **增量对照**：`git log --since=2026-09-28T00:00 --name-only -- src/ scripts/ config/` 共 82 commit / 155 件，按路径主题粗映射到 12 段（规则见 §3 表注）。
- **二期核验**：读 `91_progress.md` §终局四清单③的 7 项，逐项以 commit 主题+99 台账现状行判定。

## 1. 全量清点（132/132）

派生态：施=含"可施工"；门=含 Owner 门/待裁/挂起/提请；裁=涉裁定表述（无新裁=明示无新裁定需要）。三态裁定原文过长时截断（…）。

### a_data_foundation — 数据底座（采集/清洗/落库/备份/TDM 轴）（16 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 1 | 01_f01_multi_source_ingest.md | F001 | 挖干可施工（引用 M1 册+今日四态复核+勘误两条）；G3/G4 待 Owner 门/逐腿判定；无新裁定需要。 | 可施工 | Y | 无新裁 |
| 2 | 02_f02_source_onboarding_lifecycle.md | F002 | 挖干可施工（07 册+本卷复核；O1-O5 可施工报总筹排期；O6 挂起）。非新裁定。 | 可施工 | Y | 涉裁 |
| 3 | 03_f03_provider_routing.md | F003 | 挖干可施工（十子包实扫双源：ls+yaml 解析；P2/P4 可直开；P1 挂起；P2 壳包=Owner 门）。 | 可施工 | Y | - |
| 4 | 04_f04_cleaning_validation.md | F004 | 取证挖干（08 册+90 册）；C1/C3/C6=挂起+Owner 门（解锁条件在案）；C2/C4/C5 可施工。沿用总册判定处已注明。 | 可施工 | Y | - |
| 5 | 05_f05_dedup_audit.md | F005 | 挖干可施工（判据件本日实核 sed :18-23+调用链 integrity_checker.py:54-66 双源）；D1/D2 可施工；D3/D4… | 可施工 | Y | - |
| 6 | 06_f06_ch_hot_warehouse.md | F006 | 挖干可施工（本日实测 253 表+空壳 6 张未登记复证）；W1 补登记/W3 流水线/W4 生成器可施工；净删与 DDL=Owner 门。勘误两条（… | 可施工 | Y | - |
| 7 | 07_f07_pg_arch_db.md | F007 | 挖干可施工（生成器/DDL/消费链 file:line 实核；节点数引用锚点已注明非独立复测）；D2=挂起 Owner 门（裁-5）；余可施工。首次单… | 可施工 | Y | - |
| 8 | 08_f08_cold_archive.md | F008 | 挖干可施工（04/09 册双册+本卷无翻案复核）；S1/S4/S5 可施工；S2 挂起日历；S3 提请。总册判定沿用处已注明（built 确认传递）。 | 可施工 | Y | - |
| 9 | 09_f09_backup_chain.md | F009 | 挖干可施工（本日五任务实测+脚本族实列双源）；B1/B5 可施工；B2/B4 挂起日历；B3 Owner 门。首次单独立卷；04 册沿用处已注明。 | 可施工 | Y | - |
| 10 | 10_f10_quote_subscribe.md | F010 | 挖干可施工（常驻态 schtasks 实测+五件落盘链实列）；T1/T2/T3 可施工；T4 挂起。首次单独立卷，01 册沿用处已注明。 | 可施工 | Y | - |
| 11 | 11_f11_tdm_crossaxis.md | F011 | 挖干可施工（05/10 册+本日三数实测复核）；X2/X3/X5 可施工；X1=总筹宪法通道；X4 挂起裁-5。总册判定沿用处已注明。 | 可施工 | Y | - |
| 12 | 12_f12_industry_chain_graph.md | F012 | 挖干可施工（数据面 873 实数+生成/消费/审计三面 file 列实扫）；Y1 挂起待专项；Y2/Y4 可施工；Y3 挂起跨带。首次独立成卷，05 … | 可施工 | Y | - |
| 123 | 13_f123_db_schema_migration_channel.md | F123 | **未干。** 理由（不含修辞）：①本环节名义语义（schema 迁移通道）的穷尽枚举要求"33 件 DDL 逐件读侧/写侧/幂等面核完"，本卷只完成… | 取证 | - | - |
| 125 | 14_f125_data_governance_lineage.md | F125 | **未干（但主结论已定）。** 已定且可复算的：生产零 import、注入无供方、在册态三层计数、21 件三级枚举、五骨架目录零实现——这五项足以支撑… | 取证 | - | - |
| 126 | 15_f126_field_dictionary.md | F126 | **未干。** 穷尽度自评：六向台账与接线四态已实核到 file:line 级并主动剔除了两类"提到即算"假绿，这部分可信。未干的原因有三，均不可在本… | 取证 | - | - |
| 127 | 16_f127_data_eng_engineering.md | F127 | **未干。** 已实核且可复算：PROD=0 的 import 面、10 件测试面、三处头注假声明的逐条否证、`ArchivePlan` 同名假阳性拆… | 取证 | - | - |

### b_factory_inbound — 策略工厂入口（E0-E3·五车道）（11 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 13 | 01_f13_e0_compute_gate.md | F013 | - **三态：built（闸门本体）／partial（按图 9 store_refs 承诺口径）**。沿用基册结论+复核无新缺口（审计落盘仍缺、接线面… | 取证 | - | - |
| 14 | 02_f14_e1_intake_orchestration.md | F014 | - **三态：partial**。沿用基册+复核无新缺口；增量=09-26 手工班证明通路仍健康（非代码退化）；勘误两条（§三①②）已录。 | 取证 | - | - |
| 15 | 03_f15_lane_a_community.md | F015 | - **三态：built（人工版口径）**。沿用基册+复核无新缺口（597/597 复测一致）；自动化口径差什么=爬虫+增量模式+收货事件接 F14。 | 取证 | - | - |
| 16 | 04_f16_lane_b_ai_gen.md | F016 | - **三态：partial**。沿用基册+复核有增量：P0 蒸发维持；新增断点=3 条 pass 占坑死锁（§三）；Ollama 断供为停滞直接根因… | 取证 | - | - |
| 17 | 05_f17_lane_c_formula_mining.md | F017 | - **三态：partial**。沿用基册+复核有增量：defer 滞留 2→7 条（新证据）；新增 store_refs 登记欠账；其余四条病灶维持。 | 取证 | - | - |
| 18 | 06_f18_lane_d_three_high.md | F018 | - **三态：partial**。沿用基册+复核有重大增量：车道已复跑（勘误①）；堆积病灶量化更新（60/29）；其余维持。 | 取证 | - | - |
| 19 | 07_f19_lane_e_model_baseline.md | F019 | - **三态：partial**。沿用基册+复核无新缺口（资产缺失 09-27 复测维持；四件代码/tests 全在盘无退化）。 | 取证 | - | - |
| 20 | 08_f20_lane_g_stomach_intake.md | F020 | - **三态：partial**。沿用基册+复核无新缺口（三数全同=零变化实证）；新增注册面欠账一条（§四.3）。 | 取证 | - | - |
| 21 | 09_f21_e2_hypothesis_precheck.md | F021 | - **三态：partial**。沿用基册+复核有增量：P0 滞留 19→24 条且获正向对照证据；运行时间线更新至 09-26；其余三伤维持。 | 取证 | - | - |
| 22 | 10_f22_e3_construct_translate.md | F022 | - **三态：partial**。沿用基册+复核有增量：滞留口径勘误 7→9（按考卷件）；新增 llm_error 占坑缺陷（09-26 实证）；两轨… | 取证 | - | - |
| 129 | 11_f129_ml_train_line.md | F129 | **未干。** 已可复算：PROD=5/TC=1/TEST=28 的 AST 三态分类、在产 4 件名单、entry 假在产拆解、占位测试不计能力的判… | 取证 | - | - |

### c_exam_pipeline — 考试链（E4-E9·编排/台账）（8 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 23 | 01_f23_e4_exam.md | F023 | **挖干可施工（复核维持）**。六向全实跑复核；built 成立；增量=台账+10/FACT 6/滞留恶化 2 天/考卷件计数勘误。E4a/E4b 与… | 可施工 | Y | - |
| 24 | 02_f24_e5_synergy_dedup.md | F024 | **挖干（复核维持，含 2 待裁）**。引擎测试本日复跑绿；两待裁（簇首准则/正交化法注）随册呈总筹；本环节零代码缺陷新发现。 | 挖干 | Y | - |
| 25 | 03_f25_e6_intake_monitor.md | F025 | **挖干可施工（复核维持+三增量）**。引擎全 built；增量=sim 池 1→2（E7 前置 1 部分缓解）、泄漏 6→8（BP-5 恶化）、si… | 可施工 | - | - |
| 26 | 04_f26_e7_paper_outpost.md | F026 | **挖干（缺位定性升级为在途施工定性）**。missing→工作树 built 有完整证据链（diff 3 行+18 测试+码面结构）；四缺清单即落地… | 挖干 | Y | - |
| 27 | 05_f27_e8_assembly_allocation.md | F027 | **挖干可施工（复核维持+两勘误）**。治本注释在码实证；八日 marker 链实证；毒丸遗体定性修正；休市缺口=推断进待裁注（万无一失纪律：不判"断… | 可施工 | Y | - |
| 28 | 06_f28_e9_live_attribution.md | F028 | **挖干（复核维持）**。FIELD-GAP 实锤复读；sim 级日账连续性本日再证（09-26 marker）；三缺件定性不变；实盘级红线维持零触。 | 挖干 | - | - |
| 29 | 07_f29_factory_ledger_birth_cert.md | F029 | **挖干可施工（复核维持+断链收敛实证）**。台账族 13+csv 全活双源核对；出生证缺行 5→2 有逐行证据；车道 D 进货 +20 为全链少有的… | 可施工 | Y | - |
| 131 | 08_f131_nlp_text_intelligence.md | F131 | **未干。** 已可复算：PROD 8 条精确到 文件:行号、TC 装饰腿单列、三跳传递链逐跳给锚（schedule.yaml:205 → run_n… | 取证 | - | - |

### d_l9_knowledge — L9 知识层（源线/图谱/一问一考）（7 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 30 | 01_f30_源线行情基本面.md | F030 | **挖干可施工**：16 节点逐一线到 file 级实证（26 provider+8 采集/加工件今日全数 ls 命中），CH 四表行数/时戳今日复测… | 可施工 | - | - |
| 31 | 02_f31_源线另类.md | F031 | **挖干（实件化闸=待裁/Owner）**：谱系三档判定、渠道核实记录、底座指派表全部落到 file 级今日实证；但每线接入=资金门位/合规门位（宪法… | 挖干 | Y | - |
| 32 | 03_f32_图谱谱系.md | F032 | **挖干可施工**：五谱逐节点 file 级+PG 行数双源今日实证；两个可施工件（G4 增量 1 人日、module_ref 四节点回填 0.5 人… | 可施工 | - | - |
| 33 | 04_f33_状态变量快照.md | F033 | **挖干可施工**：三节点逐一到 file 级+CH 行数今日双源实证；V2 挂起合规非缺件判读成立。不确定项：无（全部数字今日机读）。 | 可施工 | Y | - |
| 34 | 05_f34_知识汇聚.md | F034 | **挖干可施工**：态变证据链完整（module_ref 回填注记原文+五件套逐一 ls/grep+表不存在异常原文+调度行号）；剩余三步（建表/首跑… | 可施工 | - | - |
| 35 | 06_f35_一问一考.md | F035 | **挖干可施工**：四节点 file 级+PG 三表今日双源实证；核心贡献=确认 mining 册 D2/E2 改判成立**并修正其 D2 件名错误*… | 可施工 | Y | - |
| 36 | 07_f36_治理横切.md | F036 | **挖干可施工**：Z1/Z2 双节点 file 级+事件流/读数双源今日实证；Z1 改判"有码可挂（在跑）"证据链完整。待裁两案进 §四#4/#5（… | 可施工 | Y | - |

### e_decision_chain — 决策链（L0-L4·P1-P3·S1）（9 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 37 | 01_f37_l0_premarket_plan.md | F037 | **挖干可施工**（节点锚 5/5 今日实锚在盘；六向有实证；缺口有修法；两处保留意见已列 P1/P2，不阻施工）。 ### 待裁 - 双拍板体谁是"… | 可施工 | Y | 涉裁 |
| 38 | 02_f38_l1_market_gate.md | F038 | **挖干可施工**（状态机血肉七套全数落码；两件 P0 欠账路径清晰均零新施工；L02 升格缺口已登记待裁）。 ### 待裁 - L02 升格挂账形式… | 可施工 | Y | - |
| 39 | 03_f39_l2_sector_selection.md | F039 | **挖干可施工**（供料端全绿实证+实件零缺；四处判据-码面/接线差异已列修法；传导线缺口按 L04 SKEL 账本引用不重立）。 ### 待裁 - … | 可施工 | Y | 涉裁 |
| 40 | 04_f40_l3_stock_selection.md | F040 | **挖干可施工**（实件零缺；两处判据-码面差异+两处登记欠账已列修法；两个 P0 均有现成工单真源引用不重立）。 ### 待裁 - L3-05/L3… | 可施工 | Y | 涉裁 |
| 41 | 05_f41_l4_execution.md | F041 | **挖干可施工**（验证状态全组最佳：13 件中 12 valid；三件结构性欠账今日复核成立且均小施工；EX 组交界引用 L07/M7 册不重复立工… | 可施工 | Y | 涉裁 |
| 42 | 06_f42_p1_position_checkup.md | F042 | **待挖（窄口）**（状态机血肉与验证欠账挖干；唯触发链向欠"谁调、何时调、跑没跑"最后一向实证——考古后补证即可翻挖干可施工；体检五件零编排今日独立… | 可施工 | Y | - |
| 43 | 07_f43_p2_t_trade_rebalance.md | F043 | **挖干可施工**（六向有实证：yaml 逐节点血肉+模块行数+消费方 grep 双源复核+BT-P0-003 实考结果；堵点有根因+修法）。施工序列… | 可施工 | Y | - |
| 44 | 08_f44_p3_pyramiding.md | F044 | **挖干可施工**（血肉逐节点+模块实测+测试锚+欠账清单齐；零编排双源复核成立）。 ### 待裁 - 持仓流编排工单（P2+P3 同批）排期与载体（… | 可施工 | Y | 涉裁 |
| 45 | 09_f45_s1_sell_signal.md | F045 | **挖干可施工**（血肉/模块/三源零消费实证/验证欠账全链登记；P0 双缺口有现成修法与共享设计约束）。 ### 待裁 - S1-06 黑天鹅/主力… | 可施工 | Y | - |

### f_exec_risk — 执行与风控（S2/R1/C1-C3/SOR/QMT/对账）（12 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 46 | 01_f46_s2_exit_execution.md | F046 | **挖干可施工**（六节点判据/边/验证状态齐；缺口 1 有修法有量级；P0 编排与 F45 同工单两段，不重复立项）。 | 可施工 | - | - |
| 47 | 02_f47_r1_emergency_lifeline.md | F047 | **挖干可施工**（判定语义/边/豁免/验证欠账齐；缺口 1/2 有归属；R1-03 休眠为正确态勿提前激活）。 | 可施工 | - | - |
| 48 | 03_f48_c1_capital_budget_split.md | F048 | **挖干可施工**（B 半唯一有夜批运行证据的环节；L1-AGG 翻转后 anchored 链已终批落地；带表代码化是唯一结构缺口）。 | 可施工 | - | - |
| 49 | 04_f49_c2_portfolio_aggregation.md | F049 | **挖干可施工**（四模块消费面本日三源复证全 wired；缺口均在"执行侧/事件化/验证"三层，无码面缺口）。 | 可施工 | - | - |
| 50 | 05_f50_c3_attribution_feedback.md | F050 | **挖干可施工**（红节点三处均有真源+修法；消费面较 16 册口径再增强一处证据 reporting/attribution_calculator；… | 可施工 | - | - |
| 51 | 06_f51_crypto_decision_skeleton.md | F051 | **待裁**（空壳去留=Owner 门位；本卷贡献=把 18 册"仅一件真身"口径修正为"crypto 数据面 6 件+调度登记 2 件，交易面仍零"… | 取证 | Y | - |
| 52 | 07_f52_validation_methodology_dal.md | F052 | **挖干可施工**（机制三件全建成+台账实弹；真结论产出受 holdout 纪律约束属"正确等待"非欠账；欠账七条各有归属）。 | 可施工 | - | - |
| 53 | 08_f53_order_lifecycle_precheck.md | F053 | **挖干可施工**（订单全流转 file:line 实证；54 测试件 tests/ex_core/ 在册；两 P0 均有明确处置序与归属；本车道可修… | 可施工 | - | - |
| 54 | 09_f54_daban_execution_family.md | F054 | **挖干可施工**（八件全勘+回测/执行两半边界清晰；缺口 1 挂 G22 有归属有量级；文档↔代码映射经 algo_flow 机生天然成册，净零纪律… | 可施工 | - | - |
| 55 | 10_f55_sor_algo_routing.md | F055 | **挖干可施工（结论修正型）**——"设计态无实装"预判不成立：代码完备+测试在册+生产装配缺位+头注漂移；缺口 3/4 本车道可修，缺口 1 挂 O… | 可施工 | - | 涉裁 |
| 56 | 11_f56_qmt_broker_bridge.md | F056 | **挖干可施工**（桥面 11 件全实证；缺口 1 是 M7-01 已立案未修的最高优先施工项，本日复核确认仍未修；缺口 2 为本卷新增观测，处置有判据）。 | 可施工 | - | - |
| 57 | 12_f57_settlement_reconciliation.md | F057 | **挖干可施工**（三层对账件全 file:line 实证+排班 yaml 原文锚；缺口 1/2 有明确取证路径与处置选项；eod 零导入为本卷独立新证）。 | 可施工 | - | - |

### g_backtest_gpu — 回测 GPU（成本/回撤/合规闸/引擎族）（12 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 58 | 01_f58_execution_cost_feedback.md | F058 | **挖干可施工**（三零件 file:line+边实测+断链双源同判；缺口 1 处置明确=selector 评分输入）。 | 可施工 | - | - |
| 59 | 02_f59_risk_limit_stoploss.md | F059 | **挖干可施工**（登记/执行/止损三面 file:line 实证；缺口 1=本卷新增判定，总册 built 态的细化修正非推翻）。 | 可施工 | - | - |
| 60 | 03_f60_drawdown_state_machine.md | F060 | **挖干可施工**（9 件回撤族全实扫+4 消费者复测+编排缺口处置明确；缺口 3/4 归 Owner 门位挂 99 台账）。 | 可施工 | Y | - |
| 61 | 04_f61_killswitch_instances.md | F061 | **挖干可施工**（6 件同名族+state file+持久化双轨全实证；缺口 1①/3/4 可直接施工，1②/2 Owner 门位）。 | 可施工 | Y | - |
| 62 | 05_f62_compliance_report_gate.md | F062 | **挖干可施工（红→绿路径清晰但含 Owner 人工动作，非纯工程可闭）**——本卷纯引用+复测加深，不重挖 M7-06；勘误 1 条（Feature… | 可施工 | - | - |
| 63 | 06_f63_position_reconciliation.md | F063 | **挖干可施工**（29 件 core 实扫+对账三件+NAV 门禁复核；总册 built 态维持，勘误 1 条锚点路径）。 | 可施工 | - | - |
| 64 | 07_f64_backtest_triad_registries.md | F064 | **挖干可施工**（三册计数实测+MUST/生存偏差字段行级实锚；缺口 2 Owner 挂 R-M2-2 不代裁）。 | 可施工 | - | - |
| 65 | 08_f65_backtest_engine_family.md | F065 | **挖干可施工**（九子包逐包实扫计数与任务书口径相符；勘误 1 条锚点路径；M2 车道 6 册引用不重挖，本卷补九子包枚举与消费域实测）。 | 可施工 | - | - |
| 66 | 09_f66_backtest_prereg_loop.md | F066 | **挖干可施工**（SOP 七步+生成器 INVARIANTS+142 对象实测三源交叉；勘误 1 条计数）。 | 可施工 | - | - |
| 67 | 10_f67_experiment_registry.md | F067 | **挖干可施工**（三锚全实证+四级档案地图补全；P2 支线按内收判据暂无退役项——登记/存储/面板三件均有消费）。 | 可施工 | - | - |
| 68 | 11_f68_gpu_matrix_grid.md | F068 | **挖干可施工（在飞禁令解除：T1 dedup 已完赛，跑中禁动约束翻页为完赛处置窗口）**；缺口 1 口径复核先行防误判，3 Owner 门位；"G… | 可施工 | Y | - |
| 69 | 12_f69_t0_cost_gate_ibt.md | F069 | **挖干可施工**（门/模型/口径/降级/IBT 五面 file:line 实证；缺口 1/2 Owner 待裁在 R-M2-2/R-M2-3 不代裁… | 可施工 | Y | - |

### h_sched_recovery — 排班与恢复（运行核/晋级/生命周期/守护）（12 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 70 | 01_f70_sim_matching_bias.md | F070 | **复核维持（部分挖干）**：包面实扫+消费方 grep 双源；缺口=测试面未逐支验（登记）、消费方仅到文件级未到 file:line（引用 PR-A… | 取证 | - | - |
| 71 | 02_f71_auto_runtime_core.md | F071 | **复核维持（结构挖干+运行态当日补证）**：M2 册六向结构证+本卷当日进程表/文件实体/子目录计数三向补证。三态=**维持 built（代码），运… | 取证 | - | - |
| 72 | 03_f72_paper_four_pieces.md | F072 | **挖干（复核维持+嫌疑解除实证）**：PR-A 基册六向全证引用+本卷四项当日活探（双任务码/双日志/NextRun/PostSettlement）… | 挖干 | - | - |
| 73 | 04_f73_ab_league.md | F073 | **挖干（复核维持）**：PR-A 六向全证引用+本卷四项当日活探（双目录不存在/members 空/review_scheduled false/s… | 挖干 | - | - |
| 74 | 05_f74_promotion_gate.md | F074 | **部分挖干（复核维持）**：PR-B 六向+五堵点全证引用；本卷补当日事件计数/advisories 目录双活探。未挖面（fw 停更根因/S4 消费… | 挖干 | - | - |
| 75 | 06_f75_lifecycle_fsm.md | F075 | **部分挖干（复核维持）**：PR-B file:line 全证+三套词表逐值对照；本卷维持（F75 本体文件在盘未变，无当日新探针必要——decid… | 挖干 | - | - |
| 76 | 07_f76_windows_schedtasks.md | F076 | **挖干（全列复核）**：50 席全列当日四态（State/LastRun/LastResult/NextRun）活探+五族归位+M5 名册逐项对照；… | 挖干 | Y | - |
| 77 | 08_f77_data_scheduler.md | F077 | **挖干（调度面复核）**：宿主/心跳/日志/槽位白名单/任务分母五证当日活探；管线腿病状归属逐腿 grep 实测（非转抄）。开口=腿级修复本身归 M… | 挖干 | - | - |
| 78 | 09_f78_belt_daemon.md | F078 | **挖干（复核维持）**：02 册四向全证+本卷任务级当日活探（Ready/0/NextRun PT1M）。三态=**维持 built**。 | 挖干 | - | - |
| 79 | 10_f79_reaper_watermark.md | F079 | **挖干（复核维持+红点当日复探）**：02 册+04 补挖册三层闸全证+本卷 --status/任务码/白名单行数当日三探。开口=exit 1 成因… | 挖干 | - | - |
| 80 | 11_f80_resource_profile.md | F080 | **部分挖干（复核维持）**：04 补挖册六向全证+本卷五任务/册头字段当日五探；缺口=冲突闸消费面与 99 实体逐条收录未验（登记）。三态=**维持… | 挖干 | - | - |
| 81 | 12_f81_monitor_alert.md | F081 | **部分挖干（复核维持）**：04 补挖册阈值链双向闭环证（红队 36 用例在册）+02 册 deadman 四向证+本卷三层当日活探（心跳/任务码/… | 挖干 | - | - |

### i_ai_ops_gov — AI 运维治理（crews/LSG/编排/PG 册）（13 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 82 | 01_f82_order_settlement_resident.md | F082 | **挖干可施工（结算腿与接线判定）**：每态带任务表/进程表/git 锚点 ✅；**待裁**：order_daemon 启动门位与宿主选择（Owner… | 可施工 | Y | - |
| 83 | 02_f83_automation_crew.md | F083 | **未干（并明确否证原 stub 的"挖干"自审）。** 理由逐条：①原 stub §五 写"挖干（册面两册实存+分工条款实证）✅"，但**未测三腿中… | 取证 | - | - |
| 84 | 03_f84_feedback_loop_fbl.md | F084 | **挖干（包面穷举+宿主注入点 file:line+进程探针）✅；待裁（缺口#2 口径）；待挖（深挖四段流水线内部逐件接线，归 M5 补挖项，本卷只判… | 挖干 | Y | - |
| 85 | 04_f85_env_startup_chain.md | F085 | **挖干（脚本/任务/头注/进程四向锚点）✅；待裁（缺口#2 服务化去留）；windows_service 内部逐函数深挖未做（manual 态低价值… | 挖干 | Y | - |
| 86 | 05_f86_ai_six_families_pipeline.md | F086 | **挖干可施工（九包 62 件穷举+git/PG/api_server 三面独立复核）✅；待裁（缺②部署与缺③触发的 Owner 门位时序，收口册02… | 可施工 | Y | - |
| 87 | 06_f87_ai_redline.md | F087 | **挖干（10 件穷举+三 gate 册页实锚+装饰判定引今日普查）✅；待裁（缺口#1 处置方向）；待挖（缺口#3 三件消费面——本卷不越判）。** | 挖干 | Y | - |
| 88 | 07_f88_lsg_gateway.md | F088 | **挖干（三探针本日复跑+15 死路径引收口册01 逐条 file:line）✅；待裁（无——修法①为配置级，施工须走流程，本车道只读未动）；零 LL… | 挖干 | Y | - |
| 89 | 08_f89_local_models_embedding.md | F089 | **挖干（四卡实读+服务态双源 M5/本日）✅；待裁（缺口#1 全归 Owner，本卷禁动）；待挖（嵌入路由/reranker 的调用方明细——登记 … | 挖干 | Y | - |
| 90 | 09_f90_agent_orchestration_a2a.md | F090 | **挖干（三包目录级穷举+计数双核）✅；无待裁；待挖（技能逐件深挖与 A2A 协议面——P2 支线，本卷有意不展开，登记即可）。** | 挖干 | Y | - |
| 91 | 10_f91_capability_lookup.md | F091 | **挖干（summary 本日实跑+双册双源+互链新边）✅；无待裁；无待挖（P2 支线建成态，深挖无增量）。** | 挖干 | Y | - |
| 92 | 11_f92_meta_question_ledger.md | F092 | **挖干（PG/快照/ROOR 三方独立取证+月检实跑+文件名 git 考古）✅；待裁（缺口#1 治本路线归 ROOR 对账族、缺口#2 数值裁定归 … | 挖干 | Y | 涉裁 |
| 93 | 12_f93_pg_library.md | F093 | **挖干（六件穷举+双表行数+消费方 grep 反查+SOP 实存）✅；待裁（缺口#1 元凶定位与重放时序归采集车道/Owner）；待挖（collec… | 挖干 | Y | - |
| 132 | 13_f132_infra_ops_engineering.md | F132 | **未干。** 已可复算且是实测硬料：计划任务的机器态（名称/State/Action/LastRunTime/NextRunTime/LastTas… | 取证 | - | - |

### j_ai_design_gates — AI 设计闸（七段设计/闸引擎/审计/并发）（13 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 94 | 01_f94_ai_seven_segment_design.md | F094 | **设计面=挖干可施工**（七段真源全 design_done、六向有锚）；**施工面=待裁**（落 HEAD/DDL/点火三关均 Owner 门位或… | 可施工 | Y | - |
| 95 | 02_f95_obj_four_objects_design.md | F095 | **设计面=挖干可施工**（四稿六向台账齐、施工项带验收标准）；**处置分晓=待裁**（真待 Owner 5 项+P1 12 项均 Owner 门位）… | 可施工 | Y | - |
| 96 | 03_f96_stomach_intake.md | F096 | **代码/链路面=挖干可施工**（三段件+invariants+tests 全实证）；**任务存活与断流根因=待裁**（计划任务运行态本车道只读，不代… | 可施工 | Y | - |
| 97 | 04_f97_commit_gate_chain_reference.md | F097 | **未干。** 已做到且可复算：四件在 HEAD 的存在性、战役 46 件落地面、23/115 两口径的机械复算（含 `stages` 为 dict … | 取证 | - | - |
| 98 | 05_f98_gate_engine_runtime.md | F098 | **引擎与名册结构=挖干可施工**（五子包逐文件 wc 实证+91 canonical 复算一致）；**43 门处置与三账收敛=待裁**（Owner … | 可施工 | Y | - |
| 99 | 06_f99_drift_detection.md | F099 | **检测器登记与三件套=挖干可施工**（30 复算+全件 ls 实证）；**"双 watchdog"归属=待裁**；**告警下游闭环=挂起**（待 M… | 可施工 | Y | - |
| 100 | 07_f100_red_blue_adversarial.md | F100 | **册与引擎=挖干可施工**（53/44 复算一致+25 件逐层实证）；**计数字段修正=本车道禁改（既有文件），登记待施工**；**演练频度=挂起**。 | 可施工 | Y | - |
| 101 | 08_f101_rules_and_rulings.md | F101 | **册面=挖干可施工**（86/231 双复算）；**执法闭环=待裁**（RULING-REFERENCE 红证+映射册）；**灰度通道=挂起**（活… | 可施工 | Y | - |
| 102 | 09_f102_audit_system.md | F102 | **结构面=挖干可施工**（总册五点名件逐一 ls 命中+64 条目族谱收敛）；**小时链宿主=待裁**；**测试树分层口径=挂起**。 | 可施工 | Y | - |
| 103 | 10_f103_code_quality_clone_guard.md | F103 | **双包结构与执法编排=挖干可施工**（ls/wc 实证+宪法铁律对应件全命中）；**测试密度缺口=待施工**；**acknowledged 复核节拍… | 可施工 | Y | - |
| 104 | 11_f104_session_concurrency_gov.md | F104 | **结构面=挖干可施工**（902/1659/1332 行三件+四证锚行号全实证）；**判据红证=待施工**（G1/G2）；**env 信任绑定=待裁… | 可施工 | Y | - |
| 105 | 12_f105_secrets_governance.md | F105 | **通道与 gate=挖干可施工**（542 行+priority+豁免+Q&A 全实证）；**运行时钩子=待施工**（G1 有平移范例）；**env… | 可施工 | Y | - |
| 130 | 13_f130_ml_serve_adapters.md | F130 | **未干。** 已可复算：PROD=0、TC=0、反射装配零命中、在册四层含晋升两处 file:line、双同名件事实与行数对照、与 F129 的"同… | 取证 | - | - |

### k_frontend_docs — 前端与文档（i18n/契约/面板/通知）（12 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 106 | 01_f106_terminology_i18n.md | F106 | **挖干（三册 yaml 复数+loader/gate 锚+消费方 grep+own-scope/fail-closed 状态实证）✅；待裁（无——本… | 挖干 | Y | - |
| 107 | 02_f107_rollback_recovery.md | F107 | **挖干（54 文件穷举+蓝图/四级/双轨字面锚+24 生产引用普查）✅；待裁（缺口#1 heartbeat 兜底=Owner 门在案；外延件域归属=… | 挖干 | Y | - |
| 108 | 03_f108_human_gate_risk_tier.md | F108 | **挖干（18 条 yaml 复数+四门样例+5 消费方 grep）✅；待裁（无）；待挖（四门触发留痕抽样=P2）。** | 挖干 | Y | - |
| 109 | 04_f109_registry_governance_roor.md | F109 | **挖干（双计数现场复现+master_index 锚+欠账面引用）✅；待裁（裁-1 漂移归因=Owner/总筹，本卷不代裁）；待挖（77 册逐册 m… | 挖干 | Y | - |
| 110 | 05_f110_contracts_error_codes.md | F110 | **挖干（38/788 双实测+六错误件 ls+双 gate 在册锚+悬空判引用）✅；待裁（无——接线归 C5 批既有排期）；待挖（788 码逐族透视… | 挖干 | Y | - |
| 111 | 06_f111_panel_dashboard.md | F111 | **挖干（九子包实数+54/54+40 方法+35 启动项实测+弃用头注实读+红线点逐项复跑）✅；待裁（缺口#1 口径改写=Owner 宪法文件门位；… | 挖干 | Y | - |
| 112 | 07_f112_api_server_routes.md | F112 | **挖干（47 路径全列+49/47 双口径实测+写端点授权链+三 daemon 防线+前端消费侧复跑）✅；待裁（连接池化跨域取舍；retire 日语… | 挖干 | Y | - |
| 113 | 08_f113_visual_renderers.md | F113 | **挖干（五件 INVARIANTS 逐一实读+全仓消费普查双口径+域册 ls）✅；待裁（缺口#2 职责界线=归总筹内收审计窗）；待挖（五件确定性输出… | 挖干 | Y | - |
| 114 | 09_f114_notification_router.md | F114 | **挖干（头注实读+implementations 5 件 ls+全仓普查+替代链锚）✅；待裁（缺口#1/2 装配 vs 退役=涉撤通道裁定口径对齐，… | 挖干 | Y | 涉裁 |
| 115 | 10_f115_report_generation.md | F115 | **挖干（两前册收口+本日三方锚点抽验：_archive 行号/零路由/模板在盘全过）✅；待裁（R1 宿主选择、R4 分发语义、壳包净删=Owner … | 挖干 | Y | - |
| 124 | 11_f124_state_vocab_lifecycle.md | F124 | **未干。** 已穷尽的部分：三件套实现件全锚（含 ROOR/门注册/豁免注册三处在册态行号）、装载腿与装饰腿的 AST 级区分、供给方缺失的证伪、f… | 取证 | - | - |
| 128 | 12_f128_data_security_masking.md | F128 | **未干。** 已可复算：PROD=0、`SourceType` 同名假阳性拆解、晋升留痕两处 file:line、六层骨架零实现、触发面三重排查（脚… | 取证 | - | - |

### l_methodology_routing — 方法论路由（SOP 九族/双引擎/四轴）（7 卷）

| # | 文件 | F号 | 自审闸三态（摘录） | 施 | 门 | 裁 |
|---|---|---|---|---|---|---|
| 116 | 01_f116_sop_methodology_families.md | F116 | **挖干（本环节方法论面）**：48 md 清单逐文件枚举 ✅ README 锚点实证 ✅；**待裁**：无（本环节无 Owner 门位事项；勘误 1… | 挖干 | Y | - |
| 117 | 02_f117_document_asset_system.md | F117 | **挖干（三件物结构与口径差）**：三册字段级实测 ✅ 漂移点逐条带数 ✅；**待裁**：无 Owner 门位事项；缺口 1 属注册表修复施工（归 M… | 挖干 | Y | - |
| 118 | 03_f118_four_drive_storage_map.md | F118 | **挖干（四盘真源面）**：MOD-INF-043/INFRA-STORE-003 双锚 ✅ 四盘落点逐盘带路径 ✅；**待裁**：备份链重跑授权（R… | 挖干 | Y | - |
| 119 | 04_f119_dual_engine_automation_master_plan.md | F119 | **挖干（册结构与生命周期态）**：L0-L6/引擎席/结构节全枚举 ✅ frontmatter 生命周期字段实证 ✅；**待裁**：归档后继任真源（… | 挖干 | Y | - |
| 120 | 05_f120_business_fouraxis_skeleton.md | F120 | **挖干（design 态裁前证据面）**：工单逐条落地物 git/盘面双复现 ✅ 零消费/零排班/零裁定三零点复现 ✅；**待裁**：骨架本体收编路… | 挖干 | Y | 涉裁 |
| 121 | 06_f121_research_three_domains.md | F121 | **挖干（四包实态+待裁原文）**：包/文件/登记三级枚举本日全复现 ✅ M0 待裁 22/23 原文转录零改字 ✅；**待裁**：F121 终裁路径… | 挖干 | Y | - |
| 122 | 07_f122_pipeline_routing_boundary.md | F122 | **挖干（两物正交+登记面+认领态）**：30 路由/域册双域/消费方/零挂轴全部本日复现 ✅ M0 待裁 24 原文转录零改字 ✅；**待裁**：R… | 挖干 | Y | - |

段卷数合计：a=16｜b=11｜c=8｜d=7｜e=9｜f=12｜g=12｜h=12｜i=13｜j=13｜k=12｜l=7｜总 132。

## 2. 新鲜度矩阵（24 抽验卷：每段首卷+末卷）

判定：卷内引用真源存在 9/28 后 commit 即 STALE；仅命中翻译册等登记面纯增的记 STALE(弱)。

| 段 | 抽验卷 | 命中面 | 判定 | 改动点（摘） |
|---|---|---|---|---|
| a | 01_f01_multi_source_ingest.md | 3 | **STALE** | SW5 夜战卡3/4/5 三卡台账落地（2060958ad4，09-29）；E8/E9 袋 F27 sleeve 装配+再平衡调度+TDM 对接（a349ddc1fe，09-28）；etf_benchmark 假绿治本：_fetch_etf_benchmark 重写 index_csindex_all（3c01517bb2，09-29） |
| a | 16_f127_data_eng_engineering.md | 2 | **STALE** | SW15 墓碑覆盖治本（81d85b9a77）+T14 对账三件套（76fd3f1788），09-29；16 commits 翻译/登记纯增（GPU P1 cf16fa43fd 等，09-28/29）——登记面噪音级 |
| b | 01_f13_e0_compute_gate.md | 2 | **STALE** | T2 闸代码袋 batch_window_preflight 四件+测试（f6e288fc54，09-28）；reconciler 批量 auto-commit（a2881d059e，09-29） |
| b | 11_f129_ml_train_line.md | 1 | STALE(弱·仅登记册) | 16 commits 翻译/登记纯增（GPU P1 cf16fa43fd 等，09-28/29）——登记面噪音级 |
| c | 01_f23_e4_exam.md | 1 | **STALE** | P1-4 cost-tier scale-aware（裁-4 item5，d72852ccf9，09-29） |
| c | 08_f131_nlp_text_intelligence.md | 4 | **STALE** | 16 commits 翻译/登记纯增（GPU P1 cf16fa43fd 等，09-28/29）——登记面噪音级；SW5 夜战卡3/4/5 三卡台账落地（2060958ad4，09-29）；E8/E9 袋 F27 sleeve 装配+再平衡调度+TDM 对接（a349ddc1fe，09-28）；E8/E9 袋调度接线（a349ddc1fe，09-28） |
| d | 01_f30_源线行情基本面.md | 1 | **STALE** | 4 commits：F34 L9 消费接线（e21ebc03ec）/F62 模拟执法（fa9ae36533）/ig_equity_edge 退役（8b098e31eb）/F40+F41 T袋（1dd6c70c74） |
| d | 07_f36_治理横切.md | 1 | **STALE** | 4 commits：F34 L9 消费接线（e21ebc03ec）/F62 模拟执法（fa9ae36533）/ig_equity_edge 退役（8b098e31eb）/F40+F41 T袋（1dd6c70c74） |
| e | 01_f37_l0_premarket_plan.md | 2 | **STALE** | 4 commits：F34 L9 消费接线（e21ebc03ec）/F62 模拟执法（fa9ae36533）/ig_equity_edge 退役（8b098e31eb）/F40+F41 T袋（1dd6c70c74）；E8/E9 袋 F27 sleeve 装配+再平衡调度+TDM 对接（a349ddc1fe，09-28） |
| e | 09_f45_s1_sell_signal.md | 1 | **STALE** | 4 commits：F34 L9 消费接线（e21ebc03ec）/F62 模拟执法（fa9ae36533）/ig_equity_edge 退役（8b098e31eb）/F40+F41 T袋（1dd6c70c74） |
| f | 01_f46_s2_exit_execution.md | 2 | **STALE** | 4 commits：F34 L9 消费接线（e21ebc03ec）/F62 模拟执法（fa9ae36533）/ig_equity_edge 退役（8b098e31eb）/F40+F41 T袋（1dd6c70c74）；B7 超集袋 phantom_grace_s/cancel_hold_s 修复（78982c4c81，09-28） |
| f | 12_f57_settlement_reconciliation.md | 1 | **STALE** | E8/E9 袋 F27 sleeve 装配+再平衡调度+TDM 对接（a349ddc1fe，09-28） |
| g | 01_f58_execution_cost_feedback.md | 4 | **STALE** | 4 commits：F34 L9 消费接线（e21ebc03ec）/F62 模拟执法（fa9ae36533）/ig_equity_edge 退役（8b098e31eb）/F40+F41 T袋（1dd6c70c74）；F41 执行反馈环最后一米（1dd6c70c74，09-28）；F41 执行反馈环最后一米（1dd6c70c74，09-28）；T 线残留袋配套测试（8e446b7d08，09-28） |
| g | 12_f69_t0_cost_gate_ibt.md | 4 | **STALE** | P1-4 cost-tier scale-aware（裁-4 item5，d72852ccf9，09-29）；R5 改名账实修正（d094852ffa，09-29）；P1-4 cost-tier scale-aware（d72852ccf9，09-29）；P1-4 配套测试（d72852ccf9，09-29） |
| h | 01_f70_sim_matching_bias.md | 1 | **STALE** | 涨跌停 provider 正结果缓存治本（cf1018351b，09-29） |
| h | 12_f81_monitor_alert.md | 0 | FRESH（0 命中） | — |
| i | 01_f82_order_settlement_resident.md | 2 | **STALE** | SW5 夜战卡2 F62 二次接线（35ca1d69cd，09-29）；SW5 夜战卡2 配套测试（35ca1d69cd，09-29） |
| i | 13_f132_infra_ops_engineering.md | 2 | **STALE** | 16 commits 翻译/登记纯增（GPU P1 cf16fa43fd 等，09-28/29）——登记面噪音级；E8/E9 袋调度接线（a349ddc1fe，09-28） |
| j | 01_f94_ai_seven_segment_design.md | 0 | FRESH（0 命中） | — |
| j | 13_f130_ml_serve_adapters.md | 2 | **STALE** | SW15 墓碑覆盖治本（81d85b9a77）+T14 对账三件套（76fd3f1788），09-29；16 commits 翻译/登记纯增（GPU P1 cf16fa43fd 等，09-28/29）——登记面噪音级 |
| k | 01_f106_terminology_i18n.md | 2 | **STALE** | SW15 墓碑覆盖治本（81d85b9a77）+T14 对账三件套（76fd3f1788），09-29；16 commits 翻译/登记纯增（GPU P1 cf16fa43fd 等，09-28/29）——登记面噪音级 |
| k | 12_f128_data_security_masking.md | 3 | **STALE** | SW15 墓碑覆盖治本（81d85b9a77）+T14 对账三件套（76fd3f1788），09-29；16 commits 翻译/登记纯增（GPU P1 cf16fa43fd 等，09-28/29）——登记面噪音级；E8/E9 袋 F27 sleeve 装配+再平衡调度+TDM 对接（a349ddc1fe，09-28） |
| l | 01_f116_sop_methodology_families.md | 1 | **STALE** | reconciler 批+micro 5 件（3 commits，09-28/29） |
| l | 07_f122_pipeline_routing_boundary.md | 2 | **STALE** | E8/E9 袋 TDM 对接（a349ddc1fe，09-28）；4 commits：F34 L9 消费接线（e21ebc03ec）/F62 模拟执法（fa9ae36533）/ig_equity_edge 退役（8b098e31eb）/F40+F41 T袋（1dd6c70c74） |

小结：24 抽验卷中 **22 卷 STALE**（21 强 + 1 纯登记面弱过时 F129；另 F106/F132 两卷命中面以登记册为主但含实体命中），2 卷 FRESH（h 段 F81 monitor_alert、j 段 F94 ai_seven_segment_design）。抽验 STALE 率 91.7%（22/24）。

## 3. 增量对照：9/28 后改动面 → 段映射（82 commit / 155 件）

映射为路径主题粗映射（前缀规则：data*→a、hypothesis/lane_b/intake→b、exam·t0·pf_alloc→c、TDM-L9→d、plan_engine·signal_ashare→e、ex_core·ex_sor·contracts→f、backtest·compliance·post_settlement→g、reaper·boot_hooks·lifecycle_fsm·paper_session→h、ai_layer·llm_defense·consumption→i、gov_enforcement·governance 脚本→j、frontend·state_vocab·shared api→k、library_hygiene→l；一份文件可映射多段）。另有 6 件未映射（register_ai_l1_scan_task.ps1、script-manifest.yaml、reconciliation_registry.py、indicator_usage_audit.py、intelligence/switch_engine/__init__.py、shared/foundation/errors.py），归 i/j 邻面。

| 段 | 改动件数 | 主要触面（F 号域） | 需补挖/刷新判定 |
|---|---|---|---|
| a 数据底座 | 16 | tasks/schedule/known_data_gaps 三配置+scheduler（F01/F10）；cleaning_rules+washer 托管（F04）；apply_market_tables_ddl（F06）；备份三小件 backup.ps1/backup_config/restore_drill（F08/F09）；alt_source_bootstrap（F02）；data_eng 封矿（F127） | **重度刷新**（含 #19 etf_benchmark 重写、E8/E9 调度面、备份链） |
| b 策略工厂入口 | 6 | factory_grid_executor（F14）；intake_ledger_recon+lane_b_idea_generator（F16）；hypothesis_precheck/translator（F21/F22）；search_space_prereg（F17）——S4 工厂包 f28ce0d0f0 已施工 | **刷新**（F16/F21/F22 卷内缺口已被 S4 袋落地） |
| c 考试链 | 12 | exam_scale_cost_gate+exam_cost_gate P1-4（F23/F24）；t0_*exam/t0_gpu/t0_six_phase 六件（F23/F26）；pf_alloc 三件+shadow_portfolio+strategy_production_map（F27/F28·E8/E9 袋 21 件已施工） | **重度刷新**（F27/F28 卷记 missing 编排面，现已被 E8/E9 袋落地=翻面级过时） |
| d L9 知识层 | 1 | trading_decision_map TDM-E-L9-AGG/TDM-E-FLOW 注记（F34/F35；l9_readiness_aggregator 落 a 段路径但语义属 F34） | **轻刷新**（F34 消费接线已落） |
| e 决策链 | 5 | premarket_workflow（F37）；signal_ashare 四件 candidate_pool/tradability/candlestick/trendline（F38/F40）——T 袋 F40 候选池持久化+盘前通电/F41 反馈环已施工（1dd6c70c74） | **重度刷新**（F40/F41 卷内"最后一米缺口"已闭合=翻面级过时） |
| f 执行与风控 | 14 | qmt_file_bridge_broker/integration（F56·B7 超集 78982c4c81+墓碑收口 edf0788dfb）；execution_report 契约三件 decision_timestamp（F53 邻面）；algo_execution_selector+quality_scorer（F55·F41 边）；ex_core 另四件（F51-F57） | **重度刷新**（F56 卷内三选一已有终局判定） |
| g 回测 GPU | 15 | matching_engine/ch_tick_replay/vectorized_engine（F65/F69）；_c4_engine 翻译件+GPU P1 接线（F68）；compute_window_gate/batch_window_preflight（F66 邻）；checklist_evidence+post_settlement_pipeline（F62 三门注入+清单闸写侧+时区锚）；exam_cost_gate（F23 邻）——另有 K 袋 F60 减仓进料/F61 KillSwitch 失忆窗（461a86be17） | **重度刷新（全仓最重）**（F62 已三袋施工、F68 GPU P1 已接线、F60/F61 K袋已落） |
| h 排班与恢复 | 9 | boot_hooks（F71）；start_paper_session 四 commit（F72）；lifecycle_fsm+pipeline_events（F75·总包接线版 909de5192c+demote 修复 8033a3de49）；heartbeat_daemon（F78）；process_reaper（F79）；schedule_overview/run_post_settlement_daily（F77）；morning_digest 通知通道（F74·d988f1e6d0） | **重度刷新**（F71/F72/F74/F75 卷内缺口已有落地） |
| i AI 运维治理 | 21 | ai_layer 十件 washer/redline/switch_engine/dispatcher（F83/F86/F87/F90）；runtime_interceptor（F88）；model_routing/scoring_policy（F89）；consumption_census 四件（F91）；reconciliation_loop（F82）；migrate_sqlite_to_pg（F93） | **重度刷新**（F92 ROOR 回填已做 3cb98bb6f6，卷内 76 基线过期实锤） |
| j AI 设计闸 | 41 | commit_gates 八件+generate_gate_registry/reconcile_gate_rosters（F97/F98·墓碑治本 81d85b9a77+T14 对账 76fd3f1788）；governance 脚本 24 件（F98/F102 面）；session_concurrency+lane_leases（F104）；noqa_exempt（F103）；secret_registry（F105）；ml_serve 封矿（F130） | **重度刷新**（gate 治理面 9/28-29 大改：墓碑覆盖、死指针尺、对账生成器） |
| k 前端与文档 | 8 | dashboard 五件 bridge/schedulegate/api_server/api.js（F111-F113）；registry_state_vocab（F124）；shared_quickref（F110）；data_security 封矿（F128） | **中度刷新**（F111 三方口径冲突卷面需按 bridge 改动复验；F124/F128 有落地） |
| l 方法论路由 | 1 | library_hygiene 判龄轴 created 治本（14dc95cb05，F117 邻面） | **轻刷新**（方法论段无代码直改面，登记面波及） |

结论：**12/12 段均有 9/28 后触面，无一免检**。重灾段（按触面深度排序）：g_backtest_gpu、j_ai_design_gates、i_ai_ops_gov、c_exam_pipeline、f_exec_risk、e_decision_chain、a_data_foundation、h_sched_recovery。

## 4. 二期序列核验（91_progress §③已排序待施工 7 项 × HEAD 现状）

| # | 二期项 | HEAD 现状证据 | 判定 |
|---|---|---|---|
| 1 | 合规门十闸余量接线（W-140） | fa9ae36533 G07+G09 接入 OrderManager C-002 链+W140 接线表 12 行（09-28）；5acdd1ef85 C-004 清单闸写侧三腿+装配（09-29）；ced0f780bf 清单证据时区锚统一北京日（09-29，修三腿误判陈旧生产缺陷） | **大部分已做**；余量=实盘面 TRD-A10 沙箱换版（Owner 门 #29 未动） |
| 2 | F56 kernel 三选一（99 #36） | edf0788dfb（09-29）按 Owner 批文选 c=墓碑收口（CCR merge_evaluation 补墓碑，kernel 字节封存死袋 blobs）；另 dd3b17f9fd sim_daily_runner 补 bridge-execute 执行腿（断腿重建） | **已做（选项 c）**；遗留：99 #36 行未回填墓碑终局（台账滞后一处） |
| 3 | M1 封矿治理（F125/F127/F128/F130 装饰环） | 794f16569b（09-29）[SW5 夜战卡1·M1封矿第一批] 四环逐环三选一落地；随批 data_eng/data_security/ml_serve/orchestrator 四 __init__ 面 | **已做（第一批）**；裁-6 分母活边余量待复核 |
| 4 | trae_034 三死指针（99 #35） | 1cf01067f5（09-29，ARCH-APPROVAL 通道）规则册 3 处死库指针→governance.db（6 测全绿）；7f9de37b2a（09-29）余两件 construction_workflow_policy:388+blueprint.md:2410 改指活库 | **已做**；遗留：99 #30（zalpha_metadata.db 真删=净删 Owner 门）与 99 #35 行回填未动 |
| 5 | CH 复活后实弹批（#19/#20/rebuild/DDL 执行） | 代码面：#19 etf_benchmark 重写源码件 3c01517bb2+测试件 f79a88a11e 已落（09-29，接口实测 2370 只）；DDL 决策卡 2060958ad4（SW5 卡3/4/5）。实弹面：#20 realtime 换源零 commit；intake_ledger_recon rebuild 与 apply_market_tables_ddl --apply 无执行证据（99 #19/#20 行仍"登记跳过（禁实弹）"） | **部分做**（代码/决策面约 2/4，实弹批整体未执行，仍受 CH 复活前置） |
| 6 | 二期序列 F53/F04/F74/F73/F75/F92/F30/F05-F06 | 已做：F92 序1 3cb98bb6f6（ROOR REG-METAQ-001 回填 422）；F75 缺口2 8033a3de49（demote 真实边+initial_state）；F74 堵点3 d988f1e6d0（morning_digest 晨报承接）。部分：F04 面 28d596cf96 清洗门控托管+233adc3cca washer 消费键真源修复（"四引擎"本体未见）；F05-F06 邻面（known_data_gaps 台账+DDL 决策卡）。未动：F53 Saga（仅邻面契约件 7c3da698df0 decision_timestamp，非 Saga 本体）、F73（零 commit）、F30（零 commit） | **3/8 做、2/8 部分、3/8 未动**（未动=F53/F73/F30） |
| 7 | 波9 回流 W-152..W-162 | 仅 W-156 3dc18f13d6（run_post_settlement_daily.ps1 假声明改锚，09-28）；W-152..155/W-157..162 共 10 项零 commit | **基本未动（1/11）** |

总评：7 项中 **3 项已做**（#2/#3/#4）、**2 项部分**（#1 大部/#5 半）、**2 项在途**（#6 半数子项、#7 几乎未启动）。91 台账 §③ 本身未回填终局，其"已排序待施工"7 项按写作时点已部分失效——**二期施工排期需按本表重排**。

## 5. 刷新建议（供总筹排波）

### 5.1 抽验实测 STALE 卷清单（22 卷）

| 卷 | 过时原因 | 建议刷新动作 |
|---|---|---|
| a·01_f01_multi_source_ingest.md | 三配置 tasks/schedule/known_data_gaps 9/28-29 三改（#19 重写/E8E9 槽面/三卡台账） | 复核 271/30/63 三数+census 分布，勘误补记 |
| a·16_f127_data_eng_engineering.md | M1 封矿第一批 794f16569b 已对 F127 环三选一落地 | 卷内缺口表按封矿结果闭合（登记面+实体面双更） |
| b·01_f13_e0_compute_gate.md | compute_window_gate.py 并入 T2 闸四件（f6e288fc54） | E0 闸现状复测+缺口表勾销 |
| b·11_f129_ml_train_line.md | 仅翻译册纯增（登记面弱过时） | 随批勘误即可，无需重挖 |
| c·01_f23_e4_exam.md | exam_scale_cost_gate P1-4 scale-aware 落地（d72852ccf9） | 成本门三态复测，卷内 C 面缺口勾销 |
| c·08_f131_nlp_text_intelligence.md | 数据面三配置+scheduler 变更波及（登记面为主） | 轻刷新：引用计数勘误 |
| d·01_f30_源线行情基本面.md | TDM-E-FLOW/E-L9-AGG 注记 4 commits（F34 接线） | F30 卷引用 TDM 行复验 |
| d·07_f36_治理横切.md | TDM 治理横切行 4 commits | 同上轻刷新 |
| e·01_f37_l0_premarket_plan.md | TDM+schedule+premarket_workflow 面（T袋/E8E9 波及） | L0 卷接线四态复测 |
| e·09_f45_s1_sell_signal.md | TDM 4 commits（F40/F41/F62 波及） | S1 卷下游引用面复验 |
| f·01_f46_s2_exit_execution.md | qmt_file_bridge_integration B7 修复（78982c4c81） | S2 卷 QMT 桥引用行勘误 |
| f·12_f57_settlement_reconciliation.md | schedule.yaml E8E9（排班面）+post_settlement SW5 卡2 | 对账排班+post_settlement 现状补记 |
| g·01_f58_execution_cost_feedback.md | algo_execution_selector/quality_scorer 进 F41 反馈环（1dd6c70c74） | F58 卷"断链缺口"已被消费边闭合=翻面 |
| g·12_f69_t0_cost_gate_ibt.md | exam_cost_gate P1-4+handover_verdict R5 改名 | T0 成本门卷勘误 |
| h·01_f70_sim_matching_bias.md | matching_engine 涨跌停缓存治本（cf1018351b） | 撮合偏差卷现状补记 |
| i·01_f82_order_settlement_resident.md | post_settlement_pipeline SW5 卡2 二次接线（35ca1d69cd） | F82 卷常驻链复测 |
| i·13_f132_infra_ops_engineering.md | scheduler+翻译册 16 commits（登记面为主） | 轻刷新 |
| j·13_f130_ml_serve_adapters.md | M1 封矿 794f16569b 已落 F130 环+gate_registry 墓碑治本 | 卷内缺口表按封矿闭合 |
| k·01_f106_terminology_i18n.md | gate_registry/翻译册治理面（登记面为主） | 轻刷新 |
| k·12_f128_data_security_masking.md | M1 封矿 F128 环落地+schedule 波及 | 卷内缺口表闭合 |
| l·01_f116_sop_methodology_families.md | rule_catalog_registry 3 commits（micro 5 件+reconciler） | SOP 族引用面勘误 |
| l·07_f122_pipeline_routing_boundary.md | TDM+strategy_production_map 变更波及 | 路由边界卷轻刷新 |

### 5.2 抽验外推与波次规模

- STALE 率 22/24≈91.7%；每段首末两卷同 STALE 的段（a/b/c/d/e/f/g/i/k/l 共 10 段）提示段内中段卷大概率同病（段共享注册表/配置被波及）。保守估计全量受影响卷 **90-115 卷**；其中登记面弱过时约 15-20 卷，翻面级（卷内核心缺口已被施工闭合）约 19 卷：F16/F21/F22、F27/F28、F40/F41、F56、F58、F60/F61/F62、F68、F71/F72/F74/F75、F92、F125/F127/F128/F130。
- **波 1·重度刷新（约 26 卷/8 段）**：a 段 F01/F04/F05/F06/F09/F127；c 段 F23/F26/F27/F28；e 段 F37/F40/F41；f 段 F53/F55/F56/F57；g 段 F58/F60/F61/F62/F65/F68；h 段 F71/F72/F74/F75/F79。翻面卷（F27/F28/F40/F41/F56/F58/F62/F68/F74/F75 等）须改写"缺口清单+自审闸"而非小勘误。
- **波 2·轻刷新/登记面勘误（约 12 卷/6 段）**：d 段 F34/F36；b 段 F14/F17/F129；i 段 F83/F87/F88/F92；j 段 F97/F98/F103/F104；k 段 F110/F111/F124；l 段 F117。
- **零改动段不存在**；l 段（1 件触面）与 d 段（1 件触面）最轻，随波 2 顺带。

## 6. 审计留痕

- 工具链：Python 3.12.8 + git log/ls-files；中间数据存 `.runtime/tmp/m6_*.json`（临时区随 TTL 消亡，不作为永久证据锚）。
- 抽验覆盖：清点 132/132 全量；新鲜度 24/132 抽样（每段首末）；映射 155/155 全量改动件；二期 7/7 逐项。
- 已知局限：抽验仅每段 2 卷，段中卷状态系外推；六向台账路径正则可能漏采裸文件名引用（已按 basename 解析兜底）；"STALE"指卷内实证快照过期，不判卷内处方失效。

