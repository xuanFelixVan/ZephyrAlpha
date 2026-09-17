---
ttl: task_bound
rule_form: data
verifiability: manual
title: S3 待裁项全仓穷举清单（去重归并后 96 条 + 违规发现 8 条）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-17
---

# S3 待裁项全仓穷举清单 v1.0（2026-09-17 主力会话预扫）

> **用途**：本案由主力会话（非 Kimi 配额）完成穷举，**Kimi 的 S3 战场不必再自己扫文档**，直接从这张表开工：逐条预消化 → 每页一条 Owner 签名即生效的裁定书草案。
> **扫描法**：五分区并行穷举（策略回测 / 治理门禁 / 数据层 / 模块蓝图与减法 / 配置与管线），标记词全量 grep（`待裁` 135 文件·`需 Owner` 170 文件·`挂单` 139 文件·`HELD` 95 文件·另 12 词），命中的每条**逐行 Read 核实**后才入表；同一决策跨多文档只留一行、锚点全列。
> **核验口径**：凡条目引用了 `裁定#NNN`，已逐一比对 `ruling_registry.yaml`（在册 121 条、最大号 **#303**）。因此"**引用了编号但登记表查无此条**"是稀缺信号，单列 §9。
> **总数**：待裁 **96 条**（含 12 个批量合并项，折算实际决策点 ≈190）+ 违规与矛盾 **8 条** + 低置信待确认 14 条（§10）。
> **本清单自身的可信度声明**：锚点全部实测命中，但"是否已被后续文档推翻"仅按新鲜度推断，Kimi 逐条裁前须复核当前 HEAD（宪法 §7.5：文档矛盾=事故）。

## 1. 分类与优先级（Kimi 按此序消化）

| 类 | 名称 | 条数 | 为什么这个序 |
|---|---|---|---|
| **A** | 资金动作·仓位·花钱闸 | 16 | 直接关系真钱与实盘敞口，不裁=降级运行或悬空 |
| **B** | 尺子·阈值·统计口径 | 19 | 与 S1/S5 同源，一次裁定可批量解锁下游 |
| **C** | 战役存亡·删资产·破坏性清理 | 18 | 不裁=继续烧算力与存储 |
| **D** | 注册表·flag·错误码门位 | 14 | 门位口径不统一导致反复踩同一道闸 |
| **E** | 晋升·冻结区解锁 | 9 | 多为一次性批文 |
| **F** | 数据可得性与外推授权 | 12 | 与 S8/S14 同源 |
| **G** | 方法论选型（该不该做） | 5 | 纯判断，最需要强模型 |
| **H** | 治理机制与常设门位澄清 | 3 | 需先定"什么算门位" |

**首批必做 12 条**（卡带宽最狠、且一次裁定连带解锁最多）：A-01 A-02 A-03 A-08、B-01 B-02 B-03 B-06、C-01 C-02 C-05、G-01。

## 2. A 类：资金动作·仓位·花钱闸（16 条）

| 编号 | 要拍的板 | 锚点 | 来源 |
|---|---|---|---|
| A-01 | 编排器 §八 八项打包裁：①"今日不交易"判据阈值+no_trade 枚举终稿 ②首版接入包集合与 state_matrix 3 个 `pending-owner-adoption` 格采纳节奏 ③60% 硬顶+六段预算带+过渡带降仓系数 0.5-0.7 proposed→confirmed ④日历降级容忍度（`data_proven` 可否作开市判定+连续 N 日告警的 N，草案 3） ⑤`decision_daily` 落 c1_backtest 确认+是否双写 prediction_log ⑥首版分发范围（仅留痕/驱动执行单）与执行面接入时点 ⑦T3 `intraday_revoke` 归 AI 自动 or Owner 人工+自动修订白名单 ⑧排班 v2 落地前 `read_today_schedule()` 返 stub（全可用）是否接受 | `docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md:185-192,32-34,59,120,199` ; `config/trading_decision_map.yaml:4415,4417,4418,3668,3671`（该文件自述"AI 禁自填"）; `docs/_working/full-auto-chain/S11_assembled_backtest/nodes/tdm_sleeve_allocation_mining.md:162-166` | STR-20/21/22/23/24/25/26/27 |
| A-02 | 卖出族 17 处启用与否：固定/分批/时间加权/密度感知止盈、密度止损、退出比例四式、阶段 6/7/8 | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/42_sell_flow.md:206,296-299,367-370,678-680` ; `docs/03_modules/_domain_sell_decision/take_profit_strategy/blueprint.md:87` | MOD-03 |
| A-03 | S-OWNER-002 默认行为翻转（全时全包→切换器管）放行 | `docs/_working/factory/strategy_cards/2026-09-16-s-owner-002-regime-switcher.md:3,30` ; `docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md:138` | STR-29 |
| A-04 | iFind 是否续费（不续=`edb_data` 永久 disabled） | `…design_memos/64_data_source_download_spec.md:1163` | DAT-04 |
| A-05 | L2 行情权限是否开通（含大 QMT 沙箱权限/券商确认） | `64…:1164` ; `docs/_working/2026-09-08-qmt-bridge-migration-ledger.md:264` ; `src/zephyr/data/config/tasks.yaml:1703,1714` | DAT-05 |
| A-06 | 加密行情网络闸解锁：Cloudflare 反代 / 币安换源 / 代理 三选一 | `docs/_working/2026-09-11-crypto-shadow-mvp.md:86,119,123` | DAT-06 |
| A-07 | 链上付费 API（Glassnode / CryptoQuant）是否订阅 | `…design_memos/95_crypto_system_blueprint.md:275,276,332` ; `crypto-shadow-mvp.md:117` | DAT-07 |
| A-08 | 做T v2 战役：全矩阵穷举开跑 / 改设计 / 砍（S2 的落地批文） | `docs/_working/factory/t_v2/2026-09-17-t-v2-campaign-design.md:21,27` ; `docs/_working/kimi_audit/kimi_deep_adjudication.md:58-65` | STR-01 |
| A-09 | CST-T0-001 做T成本模型 candidate→production 启用（宪章 B-007） | `docs/01_policies_and_standards/_registry/catalogs/cost_model_registry.yaml:233` ; `docs/_working/sharpe2_prep/d_ledger/2026-09-17-node-verdict-triage.md:118-120` | STR-03 |
| A-10 | GPU-04 RL 真训练 + GPU-02 Kronos 消费门的 B-007 生产门位审批 | `docs/_working/automation/20260917_automation_linkage_plan_v1.md:90` ; `…/20260917_autolnk_session_log.md:39,41` | GOV-04 |
| A-11 | 模拟盘计划任务 `ZephyrAlpha_PaperSession` 开闸 | `docs/_working/full-auto-chain/S14_live_qmt_bridge/README.md:153,176` | STR-42 |
| A-12 | 影视票房付费层（艺恩/灯塔）是否值得评估（默认不买付费另类） | `src/zephyr/data/config/known_data_gaps.yaml:614` | DAT-03 |
| A-13 | 另类 3/4 批门槛：政采网/猫眼爬虫合规试点 + VPN 常态在线 | `docs/_working/2026-09-12-alt-data-construction-plan.md:144,145,147` | DAT-22 |
| A-14 | 商品现货数据采购 + 云盘存货接收是否批 | `docs/_working/industry_chain_alpha/industry_chain_alpha_plan.md:180` ; `…/industry_chain_global_expansion_plan.md:32` | DAT 低置信转正 |
| A-15 | C1 lane_b/lane_c 生成器无人值守授权（Owner 承担 LLM token 成本才成立） | `docs/_working/pipeline-research/pending-owner-rulings.md:19` | PIPE-5 |
| A-16 | SLE-1 `--rebalance`→落图 `weight_adjust_assert` 门位开闸 | `…S11_assembled_backtest/nodes/tdm_sleeve_allocation_mining.md:167` | STR-32 |

## 3. B 类：尺子·阈值·统计口径（19 条）

| 编号 | 要拍的板 | 锚点 | 来源 |
|---|---|---|---|
| B-01 | 严尺放行档=0 的归因裁定：`STD-SIM-ACCESS-001` 四阈值过严，还是池子质量与标称不符（**两向都要给结论**） | `config/standards.yaml:16-21` ; `docs/_working/sharpe2_prep/2026-09-17-sharpe2-prep-final-report.md:47` | STR-06 |
| B-02 | `STD-LIVE-REDLINE-001` 实盘红线 draft→frozen（须附分布校准记录） | `config/standards.yaml:22-34` | STR-07 |
| B-03 | N_eff 估计器 `effective_rank` 冻结版本追认 + **补登裁定号**（registry 全文 grep `N_eff`/`effective_rank` 零命中） | `docs/_working/2026-09-15-neff-estimator-preregistration.md:13-19` ; `sharpe2-prep-final-report.md:90,98` | STR-11 |
| B-04 | DSR 0.70 硬线：补外部出处，或显式标注"工程约定" | `sharpe2-prep-final-report.md:90,98` | STR-12 |
| B-05 | batch_records 两大批（10,080 / 5,990 次）补登 N 账本 → **动摇全部历史 DSR 读数** | `sharpe2-prep-final-report.md:90,98` ; 承 #291 | STR-13 |
| B-06 | EXP 复评 IS 窗三选一：缩窗 2019-2021 / 授权补 2022-2026 提取批 / 换 analyst_forecast 前向窗 | `docs/_working/reports/2026-09-16-consensus-repaired-build.md:84-92,153,511` ; `docs/_working/2026-09-12-data-layer-gap-analysis.md:133` | STR-33=DAT-15 |
| B-07 | 共识聚合是否放宽 high-only（mid 入聚合） | `consensus-repaired-build.md:96-99,497` | STR-34 |
| B-08 | T1A-5 `regime_overrides` r1/r2/r11 回退基准是否合理（#270 明列"另行裁定"） | `…S11_assembled_backtest/nodes/decision_kernel_mining.md:146` ; `…/rsc2_shrinkage_backtest_ruling.md:94-95` | STR-30 |
| B-09 | 考尺 P1 缺陷修后（OOS/IS 比率分子分母不可比）历史及格结论是否重判 | `sharpe2-prep-final-report.md:33,89` ; `scripts/…/f06_e4_wfa_exam.py:355-367` | STR 低置信→转正 |
| B-10 | R-A X-S2 执行族 5 节点方法分配（exit_counterfactual→exec_quality） | `d_ledger/2026-09-17-node-verdict-triage.md:108-112,150,165` | STR-15 |
| B-11 | R-C TDM-X-R1-03 加仓动作的消融剥离语义 | `node-verdict-triage.md:98,167` | STR-17 |
| B-12 | R-E L0 计划族 5 节点方法学归属（新增"计划质量"判据 or 挂 agg_discrimination） | `…sharpe2_prep/…/2026-09-17-backtest-backlog-executability.md:190` | STR-19 |
| B-13 | B0 决赛前 15 条 backlog 批准开跑 + L4 批阈值清单补一次冻结 | `sharpe2-prep-final-report.md:95` ; `backtest-backlog-executability.md:46,219,233` | STR-08 |
| B-14 | 流动性危机 13 项是否接受"经验阈值先行"（盘口深度、自身订单>5%ADV、SaR/Residual Supply、AUM 门槛） | `…design_memos/37_liquidity_crisis_protocol.md:729-743` ; `docs/03_modules/_domain_risk/liquidity_crisis_manager/blueprint.md:131` | MOD-04 |
| B-15 | 组队方案 A（4 条 ρ̄0.167 / 合并 Sharpe 1.541）进 E7 评审 + 采"观察档"降级表述 | `sharpe2-prep-final-report.md:72,94` | STR-05 |
| B-16 | 竞价成交量归属口径（建议归当日首 bar）+ 十年日线 open 代理口径认可 + 2021-09 起末态标定回补批（~600 万行）是否立项 | `docs/_working/auction_bridge_switch_mining_2026_09_17.md:90,96` ; `known_data_gaps.yaml:817` ; `2026-09-08-qmt-bridge-migration-ledger.md:243` | DAT-09/10 |
| B-17 | 6 日永久 tick 缺口可否用 1min 合成近似续回放 | `known_data_gaps.yaml:397` | DAT-01 |
| B-18 | `daily_valuation` 09-09~14 数值全 0：此窗可用性判定 + 是否再投 10h 级重刷 | `known_data_gaps.yaml:631` | DAT-02 |
| B-19 | crypto_top50_usdt 静态宇宙去留 + 是否改动态 Top-50 | `2026-09-11-crypto-shadow-mvp.md:121` ; `sharpe2-prep-final-report.md:88` ; `data/crypto/universe_manifest.csv` | DAT-08 |

## 4. C 类：战役存亡·删资产·破坏性清理（18 条）

| 编号 | 要拍的板 | 锚点 | 来源 |
|---|---|---|---|
| C-01 | 清洁零风险三件批文：10 张空壳表 DROP / 110 个 CAS tmp / 重复 bak 二选一 | `sharpe2-prep-final-report.md:87,96` ; `docs/_working/sharpe2_prep/c_audit/2026-09-17-cleanliness-audit.md:24,97` | STR-09=DAT-12 前半 |
| C-02 | 决赛后破坏性批：9 垃圾件归档 / 85MB forensic bak 冷存 / integrator bak / 20260526 bak（合计≈6860 万行） | `sharpe2-prep-final-report.md:87` ; `cleanliness-audit.md:22,23,26,59` ; `docs/_working/2026-09-14-market-data-gap-report.md:20` | STR-10=DAT-12 后半 |
| C-03 | `auction_book_limit_bak_20260908`（该名**唯一副本**）去留 | `cleanliness-audit.md:59` ; `sharpe2-prep-final-report.md:88` | STR-10b=DAT-13 |
| C-04 | BT-P2-055 底仓+日内回转执行模板是否立项（做T臂底座） | `backtest-backlog-executability.md:211` ; `…catalogs/backtest_backlog.yaml:1896` | STR-04 |
| C-05 | 方法论五选型建/废：P-1 Wasserstein 栈、P-2 Conformal 变体、P-3 Robust HMM、P-4 RL 执行、P-5 过拟合协议 | `…design_memos/90_methodology_open_questions.md:779-783,24,29,424`（08-28 复核明写"仍全部待用户裁定"） | MOD-01 |
| C-06 | MOD-XS-008 RL 训练环境骨架已按未裁的 P-4 施工并标 `build_status: production`——追认 or 撤件 | `docs/03_modules/_domain_ex_sor/rl_execution_training_env/blueprint.md:9,26,106` | MOD-02 |
| C-07 | BM-INV-007 孤儿模块 **439 件**怎么判 + 扫描是否加 `node_type` 过滤收敛到 17 件（**口径即尺子**） | `docs/02_enterprise_architecture/03_governance_reports/battle_map_alignment_report.md:24,89` ; `panorama_alignment_overview.md:49,64` ; `orphan_module_checklist.md:26,211,242` | MOD-08 |
| C-08 | 31 件候选模块 `status: deferred` 建 or 废（含 CAND-EX-001 富途/IB 适配、CAND-RSK-014 黑天鹅库、CAND-WFO-001） | `…catalogs/candidate_module_registry.yaml:291,510,914,993,1315,1395,1473,1552,1632,1711,1808,1891,2896,2955,3014,3073,3132,4108,4353,4474` 等 31 处 | MOD-10 |
| C-09 | 弃用流程第②步 9 件：MOD-PF-004/005（最小方差/风险平价）deferred→rejected 升格、MOD-RSK-011 否决理由空 | `orphan_module_checklist.md:165-184` | MOD-09 |
| C-10 | B13 `nan_processor`：退役 vs 保留但删 bfill/linear/mean 三策略 | `docs/_working/2026-09-05-steward-b-class-owner-book.md:138`（挂 12 天） | GOV-15 |
| C-11 | B7 `semantic_audit/orchestrator`：接线 vs 退役 + BM-SEL-11 锚改挂 | `…steward-b-class-owner-book.md:139` | GOV-16 |
| C-12 | B9 `ashare_stop_loss_engine`：保留待接线 or 定退役+接线里程碑 | `…steward-b-class-owner-book.md:137` | GOV-17 |
| C-13 | B14 `gpu_consensus_scheduler` 双实现去留与合并方向（569 行 vs 598 行，零消费） | `…steward-b-class-owner-book.md:143` | GOV-18 |
| C-14 | B10/B11 `market_data` 集群批量 salvage（涉 RecoveryManager 进程内轮询=结构性违规）是否升为机制裁定 | `…steward-b-class-owner-book.md:153` | GOV-20 |
| C-15 | CircuitBreaker×9/KillSwitch×5 收敛残余：`capacity_assurance` + `context_pipeline_auto` 是否向 SSoT 收（同批 A3/A4 已走 #254，此项无号） | `docs/_working/2026-09-15-governance-module-mining-sop-map.md:137,169` | GOV-36=MOD-11 |
| C-16 | 5 个一次性/遗留计划任务删除或转正：4 个测试遗留任务（C4Exam/LaneC 各 2，**每日白烧整条工厂线**）+ 4 个一次性实验任务 + NightlySentiment 退役残余 + `ZephyrAlpha_AltFxECB`（告警板连日 orphan warning） | `docs/_working/automation/20260917_automation_linkage_plan_v1.md:63,70,84` ; `…/20260917_autolnk_session_log.md:29,35` ; `docs/_working/resource_schedule/resource_schedule_v2_acceptance_evidence.md:48` ; `docs/_working/automation/campaign/CAMPAIGN_LEDGER.md:104` | GOV-01/07=DAT-25 |
| C-17 | B5 silent-except 路线批准：抽样定点+新增门禁，**否决 122 处批量治理** | `…steward-b-class-owner-book.md:87` | GOV-27 |
| C-18 | 蓝图建设缺口"内容工程族 ~190 项"是否立 Owner 排期专项 | `…steward-b-class-owner-book.md:119` | GOV-29 |

## 5. D 类：注册表·flag·错误码门位（14 条）

| 编号 | 要拍的板 | 锚点 | 来源 |
|---|---|---|---|
| D-01 | **门位口径统一**（建议一条规则批掉 D-02~D-06）：凡"注册表净删/扩行"是否一律 Owner，还是按 tier 分级 | `…steward-b-class-owner-book.md` 全篇 + 下列四条反复触发 | GOV 分区总评 |
| D-02 | 错误码命名空间：FAC / MLS / AUDITTEST 三前缀入 `domain_prefixes` | `…steward-b-class-owner-book.md:52,54` | GOV-21 |
| D-03 | 预留码关闭 vs 落码：ZA-PA-0008~0010 / ZA-POS-0041~0043；ZA-PA-0013 批准即转正 | `…steward-b-class-owner-book.md:64,66` | GOV-22 |
| D-04 | `tool_contracts` 34 契约码收编路线：(a) 落 raise 点 vs (b) 注册表新增 `contract_declared` 形态 | `…steward-b-class-owner-book.md:44` | GOV-23 |
| D-05 | 存量孤件 `model_capability_exam__init__.yaml` 删除（注册表净删=门位，#ARCH-326 status=open） | `…_registry/catalogs/architecture_issue_registry.yaml:21918` ; `docs/_working/reports/p21_algo_flow_link_findings.md:264,365` | GOV-33 |
| D-06 | C4 对质表 STR evidence 字段回填算不算"注册表净变更"（+`failed_obsolete` 落库） | `docs/_working/2026-09-13-c5-cluster-differentiation-report.md:107` | GOV-34 |
| D-07 | ROOR schema 增 `counting_rule` 字段（10 表 entry_count 语义口径）批准 | `…steward-b-class-owner-book.md:113` | GOV-25 |
| D-08 | unified-asset-index 唯一真源写者 + 扫描口径（宽 31847/B vs 窄 24415/C） | `…steward-b-class-owner-book.md:164` | GOV-26 |
| D-09 | `SYS-MASTER-001` §0.2 dispatch 表两行 REMINDER 是否扩行（机生清单扩行=门位） | `docs/_working/resource_schedule/resource_schedule_delivery_report_v1.md:75` | GOV-09 |
| D-10 | 三张 miniQMT 占位表/任务（从未产出）删登记 vs 留待替代源 | `src/zephyr/data/config/tasks.yaml:1832,1846,1860` ; `2026-09-08-qmt-bridge-migration-ledger.md:126` | DAT-11 |
| D-11 | `functional_domain_registry` D_AUTONOMY_PERM 两行 `ssot_path` 指向**不存在的目录**——改注册表 / 补目录 / 退役域 | `…catalogs/functional_domain_registry.yaml:431,454` ; `docs/03_modules/_domain_autonomy_perm/{budget_enforcer,escalation_protocol}/blueprint.md:3` | MOD-07 |
| D-12 | L6-#2 墓碑 TTL 清理判据 + 注册表净删门确认 | `docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md:259-260` ; `ai_layer_vision/README.md:202` | STR-36 |
| D-13 | L4-#2 独立性 gate 立案准许（判据文件保护 gate + `criteria_ref` 机检） | `…/L4_compare/DESIGN.md:189` ; `README.md:187` | STR-37 |
| D-14 | DS-275 修复表 `switch_gate=Owner`：生产读路径是否切换（DS-229 消费方改指 `consensus_daily_repaired`） | `consensus-repaired-build.md:131,137,158,207` | STR-35=DAT-16 |

## 6. E 类：晋升·冻结区解锁（9 条）

| 编号 | 要拍的板 | 锚点 | 来源 |
|---|---|---|---|
| E-01 | H-01：7 份战役蓝图（含 promotion_combo_gate / standards_lib）晋升 `docs/03_modules` | `docs/_working/automation/campaign/CAMPAIGN_LEDGER.md:13,99` ; `…/campaign/blueprints/promotion_combo_gate_blueprint.md:3,8` | STR-40=GOV-10=DAT-23 |
| E-02 | H-02：TableRegistry / `business_data_categories` 表名入册 | `CAMPAIGN_LEDGER.md:100` | GOV-10=DAT-23 |
| E-03 | H-03/H-04：GPU-01/02 回测施工进 `scripts/backtest` 红线区 + 预测表 DDL + RL B-007 门 | `CAMPAIGN_LEDGER.md:101,102` | STR-41=DAT-24 |
| E-04 | 禁写区蓝图×2（`measure_calibration` / `resource_morning_report`）晋升 | `docs/_working/resource_schedule/resource_schedule_v2_acceptance_evidence.md:49` ; `…/resource_schedule_delivery_report_v1.md:75` | GOV-08 |
| E-05 | `.trae/documents/` 181 份非 git 裁定/方案是否承认为真源并迁册（CloneGuard 引擎核实裁定唯一落点在此；蓝图仍称 6 引擎、架构图仍画已废弃 mcrit 为 L2 底座） | `docs/03_modules/_cross_layer/clone_guard/blueprint.md:29,154,158,212,228,230,266` | MOD-12 |
| E-06 | 数据库 4 项"用户裁定"暂缓是否到期解锁（DuckDB Warm / Cold / Feature Store / Event Store）——**称"用户裁定"但无裁定号** | `docs/03_modules/_cross_layer/database/blueprint.md:109,112,116,117` | MOD-13 |
| E-07 | 三条 akshare 采集链（指数成分调整 / 新股申购 / 两融标的）是否开数据窗（现 `enabled: false`、schema 已建；其引用真源已归档） | `…catalogs/business_data_categories.yaml:874,890,906` ; `docs/_archive/17_special_trading_days_data_assets.md:21` | MOD-14 |
| E-08 | `REG-EXP-001` 实验/回测登记表整表 `status: draft` 是否晋升真源（master_index 记 entry_count=0，表内实有条目） | `…catalogs/registry_master_index.yaml:177` ; `…catalogs/experiment_registry.yaml:38` | MOD-15 |
| E-09 | 裁定#1（因子 YAML DSL，>500 因子触发）自 2026-06-15 挂 `status: draft` 未生效——执行 or 废止 | `…catalogs/ruling_registry.yaml:60,64`（在册但长期 draft） | MOD-16 |

## 7. F 类：数据可得性与外推授权（12 条）

| 编号 | 要拍的板 | 锚点 | 来源 |
|---|---|---|---|
| F-01 | 16 条 error 策略补考排期（前置=`market_commodity_futures_main` 品类注册缺陷） | `sharpe2-prep-final-report.md:18,89,99` | STR-14 |
| F-02 | R-B 消融对照回放实弹运行 §12 放行（X-S1/X-R1 13 节点） | `d_ledger/2026-09-17-node-verdict-triage.md:60,94,151,166` | STR-16 |
| F-03 | R-D 3 条 L1-AGG 历史 pending 行是否加 superseded 标记机制 | `node-verdict-triage.md:127-129,168` | STR-18 |
| F-04 | L3 对账期初持仓快照源 A/B/C 勾选（勾选框全空；A 案依赖 miniQMT 疑需重拟） | `docs/_working/2026-08-30-l3-snapshot-datasource-adjudication.md:26,87` | DAT-17 |
| F-05 | bdpan 云盘同步器 7/3 停更是否重启（影响 tick/分钟/财务/复权/新闻；疑被"不可恢复 accepted"部分吸收） | `docs/_working/2026-09-12-fundamental-consumption-design.md:103` ; `known_data_gaps.yaml:390` | DAT-18 |
| F-06 | TradingWatchdog / RestartMiniQmt 启停（资源表已标 retired，两处口径互斥） | `docs/_working/2026-09-14-market-data-gap-report.md:19,108` ; `…S01_data_pipeline/README.md:54,66` ; `scripts/governance/generators/generate_resource_profile_registry.py:662` | DAT-19 |
| F-07 | TICK_SOURCE 切 xtdata 后桥模式是否降级为纯后备 | `S01_data_pipeline/README.md:53,73` ; `market-data-gap-report.md:18` | DAT-20 |
| F-08 | QUOTE_V17 并入 TICKDUMP3 v20 加速路径（一致则退役 v17） | `2026-09-08-qmt-bridge-migration-ledger.md:222` | DAT-21 |
| F-09 | L1 必需传感器集定义（哪些日更必需 / 哪些可选） | `docs/_working/trading_vision/2026-09-16-skeleton-coverage-audit.md:241,276` | STR-28 |
| F-10 | L4-#3 派考边 `intake_exam_due` 跨稿契约对齐 | `…ai_layer_vision/L4_compare/DESIGN.md:140,190` ; `README.md:200` | STR-38 |
| F-11 | L7 A/B 联赛 + AI 判净站：6 个月模拟数据判定窗是否现在立项 | `CAMPAIGN_LEDGER.md:94-95` | STR-39 |
| F-12 | 模拟盘 A 阶段 2026-12-14 首评是否维持"明令勿提前施工" | `docs/_working/pipeline-research/pending-owner-rulings.md:18` | PIPE-4 |

## 8. G/H 类：方法论选型与机制澄清（8 条）

| 编号 | 要拍的板 | 锚点 | 来源 |
|---|---|---|---|
| G-01 | `_system_master` 蓝图 〇-B **12 项**"设计决策待定"（多进程/并发调度/100-AI 会话/SQLite 多写…）：承认 S 级单机现实判"挂"，还是立容量架构项 | `docs/03_modules/_system_master/blueprint.md:142,154,166,178,190,202,214,225,236,248,260,272` | MOD-17 |
| G-02 | G07 判 COMBINATION_INVALID（ρ_max=0.768）后的三件：TDM-E-L2-05 维持红节点 pending_gate、G13 加情绪暴露硬上限、定位器增"回放/打标"语义 | `docs/_working/2026-09-11-g07-sentiment-validation.md:32,78` ; `docs/03_modules/_domain_signal/sentiment_cycle/blueprint.md:32` | MOD-18 |
| G-03 | belt daemon 治本路线 A（静默窗/Owner 门位重启一次）vs B（每项起短命子进程，动 lease 单写者语义）#ARCH-324 open | `…catalogs/architecture_issue_registry.yaml:21845` ; `docs/_working/reports/p21_algo_flow_link_findings.md:219` | GOV-32 |
| G-04 | AI 资产盘点 7 项开放问题（域归属 / D_KNOWLEDGE 保留合并 / 施工优先级 / 计数入口 / 口径真源 / 补护照 / 域 ssot 缺失）+ Q10 场外依赖图快照（CSV 2434 行、抽样 67% 路径失效）重生成 or 随草稿区清理 | `docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/02_design_asset_inventory.md:399,402,414,457-466,479`（Q5/Q7 已自行消解） | MOD-05/06 |
| G-05 | 数据工厂升级议题 #ARCH-314（dataflowgraph 阶段分层）是否排期立项 | `…architecture_issue_registry.yaml:21686`（status=proposed） | GOV-44 |
| H-01 | 审计链取证完成期间"冻结一切轮转"的处置（26,909 条 HMAC 失配 + 链断裂；#266/#267 已覆密钥线） | `docs/_working/greatwall_integration/2026-09-16-eight-greatwall-e2e-integration.md:61` ; `docs/_working/audit_integrity/audit_chain_incident_forensics_gwa.md:148` | GOV-11 |
| H-02 | 裁定撞号 #264(WYF-3) vs #266 的最终合法性认定（两条均 active） | `audit_chain_incident_forensics_gwa.md:154` | GOV-14 |
| H-03 | 常设门位 vs 待裁项的边界澄清：AUTOGEN 蓝图变更矩阵里 ~60 处"需 Owner 审批"（如 `known_good_hashes` 需 Owner PGP 签名）与 `ai_autonomy_authority_registry.yaml:272,276,282,354,381,512,516,531` 八条——**这些是常设约束不是待裁项**，但"PGP 签名是否真要人执行"需 Owner 表态 | `docs/03_modules/_cross_layer/gate_engine/blueprint.md:1528,1535` ; `…catalogs/ai_autonomy_authority_registry.yaml` 八处 | GOV 低置信→转正 |

## 9. 违规与矛盾发现（8 条，**本案最高价值区**）

| 编号 | 发现 | 证据 | 严重级 |
|---|---|---|---|
| V-01 | **被引用的裁定号 304 在登记表查无此条**（registry 最大号 #303；全表唯一 "304" 命中是进程号 30424）——做T v2 战役设计书把"304 教训"当作裁定背书（原文写作"裁定"连写井号数字的形式；本文档刻意不照抄该连写形式，否则 RULING-REFERENCE 门禁会把它当**新增**引用硬拦，实测已拦过本清单自身，见证据列） | `docs/_working/factory/t_v2/2026-09-17-t-v2-campaign-design.md:28` vs `…catalogs/ruling_registry.yaml`（实测 296-310 全缺） | P1（RULE-RULING 违规，且污染战役依据） |
| V-01b | **同族机理实证（转 S4）**：RULING-REFERENCE 门禁对**新增**引用会硬拦（本案 09-17 落库时被拦两次即证据），但 09-17 那条真悬空引用所在设计书却顺利入库——须查该 gate 的 own-diff 作用域/阶段启用时点/是否仅对手改文件生效，即"门还在、牙没了"同型 | 本清单落库死信 `q-20260917-kimi-audit-0001/0002`（`.runtime/commit_queue/dead/`）vs `t_v2…campaign-design.md:28` 入库提交 | P1（机制面，与 GOV #ARCH-322 同族） |
| V-02 | **`#293` 引用不符**：在册内容是"回测合理性收益带单一真源化收紧（+1000%→+300%）"，却被用来背书"S-OWNER-001 考试 FAIL"这一证伪结论 | `…ruling_registry.yaml:3435-3441` vs `t_v2…campaign-design.md:8` ; `docs/_working/factory/strategy_cards/2026-09-16-s-owner-001-300etf-band-t.md:3,26` | P1（做T战役的立项依据无真源） |
| V-03 | **待裁项与已生效裁定冲突**：管线班请 Owner"提供飞书 webhook 或 SMTP 凭据即激活告警"，而 09-15 已裁"飞书/SMTP 通道彻底删除，通知=前端 promotion 页" | `docs/_working/pipeline-research/pending-owner-rulings.md:13` vs 裁定#255 线（通道删除，在册 active） | P2（该条应作废并回写，否则可能诱导重建已删通道） |
| V-04 | **63 号备忘自相矛盾**：`:1386` 记 Q1/Q3/Q8 已 Owner 拍板（08-21），`:32` 与 `:1446` 又记"未拍板/仍待拍板"（宪法 §4：文档矛盾=事故） | `…design_memos/64_data_source_download_spec.md:32,1386,1446` | P2 |
| V-05 | **已决未回写 ×2**：①全历史时区重写已"Owner 批准+11:14 全完成"，但交接文档仍写"需 Owner 点头"；②`consensus_daily` 处置已裁 A 并晋升至政策文件，旧设计文档仍挂待裁 | `docs/_working/2026-09-14-market-data-gap-report.md:133` vs `…/2026-09-14-handoff-market-data-repair.md:68,151` ; `docs/_working/2026-09-12-expectation-consumption-design.md:207` vs `docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md:191` | P3（虚增待裁面） |
| V-06 | **大量实质裁定只写"用户裁定/待定"不编号**（E-05/E-06/C-05 等），使 RULE-RULING gate 完全失能——本清单里"未见裁定号"占绝大多数 | 本表 96 条中仅 6 条带编号引用 | P1（机制面，与 S4 同族：门还在、牙没了） |
| V-07 | **蓝图 frontmatter 与正文自相矛盾**：`rl_execution_training_env` 标 `build_status: production` 而正文自述"design（骨架）"，且其依据 P-4 方法论未裁 | `docs/03_modules/_domain_ex_sor/rl_execution_training_env/blueprint.md:3,31,76` | P2（与 C-06 联动） |

### 9.1 处置回填（kimi-audit 班次 2026-09-17）

| 编号 | 处置 | 落点 |
|---|---|---|
| V-01 | **实证成立+已入真源**：#304 悬空坐实（registry 全表最大 #303）；缺陷模式 #15 已入 `defect_pattern_checklist.md` v1.1.0；战役背书失效并入 S2 裁定书 | `adjudications/S2_做T_v2_战役裁定书.md` §1.1 |
| V-01b | 转 S4 战场（RULING-REFERENCE 门禁 own-diff 作用域审查，为何放过原始违规件） | S4 战场文档 |
| V-02 | **实证成立+已入真源**：#293 内容不符坐实（在册=收益带收紧）；001 考试全仓零产物（strategy_screen 零行、artifacts 零档、策略卡自述"冻结前禁跑"）——立项依据无证，进 S2 裁定书主论据 | 同上 |

## 10. 低置信待人工确认（14 条，Kimi 裁前自判是否升格）

1. `sharpe2-prep-final-report.md:82` — `stash_notice.json` 三次扫描未留 notice，待排查（疑运维派工）。
2. `node-verdict-triage.md:178` — 面板 API 8890 旧实例 wedge，标"Owner 窗口事项"。
3. `ai_layer_vision/README.md:142-145` — L1 施工项 7"外扫=日历节拍"需 Owner 追认+裁定登记双前置（放松宪法 §9.3，属 AI 层）。
4. `…S11_assembled_backtest/nodes/decision_kernel_mining.md:134` — 组合层是否允许现金权重（**疑似已决于 #270**，文档未同步）。
5. `sharpe2-prep-final-report.md:97` — alpha 增量车道立项排序。
6. `20260917_autolnk_session_log.md:36` — F06Grid 与 C4Exam 周六 14:00 同刻双活，错窗方向（移位 vs 入串行组）。
7. `…/20260917_autolnk_session_log.md:37` — CH-OptimizeMerge 立 `register_*.ps1` + 任务名下划线规范化（涉改活任务）。
8. `…/20260917_fullauto_skeleton_v1.md:53` — WeeklyRest 周日休息窗（涉关机）点头。
9. `…/20260917_autolnk_session_log.md:42` — 外网论文/策略搜索 agent 启用=外呼边界放行。
10. `known_data_gaps.yaml:833` + `docs/_working/datavein/2026-09-17-etf60min-depth-workorder.md` — kline_etf_60min 回补工单是否需批（现挂 monitoring）。
11. `known_data_gaps.yaml:784` — sector_constituent 8803/8804 接受 82% 覆盖 vs 立项挖矿。
12. `…design_memos/15_data_feature_layer_spec.md:162` — Embargo BDay 是否换真交易日历。
13. `docs/_working/2026-09-10-legacy-clear-night-report.md:90,94,95,96,97` 五件（pytest_cache 根治 + `.openclaw/` ACL takeown / R21 决策地图死批归一 / `[allow-mass-deletion]` 中文阈值放宽 / CloneGuard acknowledged 不覆盖 ast_grep / SCHEMA-FILE-EXISTS 悬空）——均为"门禁松紧"级，可整族并入 D-01 门位口径一次批掉。
14. `docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md:364,956,957` — §9.1/§10 标"待对齐·人工核对"且 §4.2 DDL 缺 `ingest_ts`（蓝图内部矛盾），疑已随 CH 战役闭环。

## 11. 统计与口径自证

- 原始命中：策略区 43 + 治理区 45 + 数据区 25 + 模块区 18 行（折算 114） + 管线区 6 = **137 行 / ≈190 决策点**。
- 去重后**净 96 条**：合并了跨区重复 8 组（H-01~H-06 三处重复、EXP 复评两处、破坏性清理批两处、CircuitBreaker 残余两处、一次性任务三处、DS-229 切换两处、成本模型启用两处、竞价口径两处），剔除已决/纯施工 ≈30 条（明细在各分区报告，Kimi 若需回溯按 §2-§8"来源"列的原始编号查）。
- 分区交叉复核：策略/治理/数据/模块四区的 `裁定#NNN` 引用共 **120+ 个编号逐一比对 registry**，除 V-01（#304）与 V-02（#293 内容不符）外**未发现悬空引用**；注意 registry 里 `ruling_id` 有带引号/不带引号两种写法，机器核验须兼容（本次实测会产生 6 条假阴性）。
- 待裁项分布本身就是一个裁定素材：**A+C+G 类共 39 条属"该不该做/花不花钱"，B+D+E 类共 42 条属"尺子与门位"，F 类 12 条属"数据能不能推"**——Owner 拍板带宽若按条消耗需 96 次，按族消耗只需 ≈14 次批文（见首批 12 条的打包设计）。
- **锚点抽检（本表自身被复核过一遍）**：全表 file:line 先经脚本核"文件存在 + 行号在范围内"（唯一路径失准已修：S-OWNER-002 在 `factory/strategy_cards/` 而非 `trading_vision/`），再抽 21 个承重锚点比对行内关键词——命中 17 条，其余 4 条经 grep 定位后修准 3 处行号漂移（C-06 蓝图 `build_status` 实为 :9/:26/:106；C-07 的"439 孤儿"实为 :24/:89；A-01 六段预算带补 :3671 过渡带系数行），另 1 处（`known_data_gaps.yaml:614` 影视票房）为关键词在相邻行、锚点本身准确。**残余风险**：表中以 `…` 缩写的长路径未逐个复检，Kimi 引用前请展开核实。

## 12. Kimi 使用本表的纪律

1. **不许直接替 Owner 拍**（三问第 3 条）：本表 A/C/E 类与全部 V 类，产出**一页式裁定书草案**，落 `docs/_working/kimi_audit/adjudications/`，一份一条，格式见主案 §2 S3。
2. **B 类与尺子同源**：B-01~B-05、B-09、B-13、B-15 与 S5 定尺子是同一件事的两侧，**S5 结论出来后回头批量重写这些条目的建议**，别裁两遍。
3. **D-01 优先**：门位口径统一是杠杆最大的一条——一条规则可消掉 D-02~D-06、H-03、低置信 13 共 12 个决策点。
4. **V 类必须先处理**：V-01/V-02/V-06 说明"裁定引用不核真源"是全仓习惯，这条要写进 `defect_pattern_checklist.md`（结论入真源规则）。
5. 每条裁完在本表追加一列 `处置=草案已出/已直改/作废/仍挂`，供收官报告统计（本表即 S3 的进度真源）。

## 13. 处置回填（kimi-audit 班次 2026-09-17，裁定书索引）

> 本表即 S3 进度真源。V 类回填在 §9.1；本节登记其余各类。B 类按 §12.2 纪律等 S5 定尺后批量重写。

| 编号 | 处置 | 落点 |
|---|---|---|
| A-01 | 草案已出（八项逐项建议：首版接入包=空集联动 S2；预算带 confirmed 标未校准；不双写；T3 自动仅限 kill_switch 联动） | `adjudications/A-01_编排器八项打包裁.md` |
| A-02 | 草案已出（12 件整族挂起+依赖达成自动回队） | `adjudications/A-02_卖出族整族挂起.md` |
| A-03 | 草案已出（不予放行；三重未就绪） | `adjudications/A-03_切换器默认翻转.md` |
| A-08 | 草案已出（=S2 裁定书：砍现形态） | `adjudications/S2_做T_v2_战役裁定书.md` |
| C-01 | 草案已出（批准走可逆通道：隔离 7 天再 DROP/冷存不删除） | `adjudications/C-01_C-02_破坏性清理两批.md` |
| C-02 | 草案已出（同上；C-03 唯一副本明示豁免） | 同上 |
| C-05 | 草案已出（P-1/P-3/P-4 不上，P-2 三层，P-5 采纳修订方向） | `adjudications/C-05_方法论五选型.md` |
| G-01 | 草案已出（11 项封挂+SQLite/锁按现实规模单独立项） | `adjudications/G-01_system_master_12项封挂.md` |
| D-01 | 草案已出（三档统一规则：净删=Owner 常设/tier0 新增改=提案+登记/派生行全自动/号段分配自动预留码 tier0） | `adjudications/D-01_注册表门位口径统一.md` |
| B-01~B-03/B-06 | 仍挂（等 S5 定尺后回头重写，§12.2 纪律） | — |
| 其余 84 条 | 仍挂（配额纪律：首批完成后按 A→C→D→E→F→G→H 序续推） | — |
