---
ttl: task_bound
completes_when: 总筹消化本车道报告并把 medium/low 复核清单与病历挂载面转入 F2+ 施工单后，本件转归档
title: 图9 策略工厂 挂图升级 车道F1 清点报告
owner: ZephyrAlpha-Owner
session: st-map9-f1-20261003
---

# 图9 策略工厂 车道F1 清点报告

> 会话 `st-map9-f1-20261003`｜2026-10-03｜判据真源=`vertical_map_mounting_policy.md` §1 四判据。
> 产出三件套：`fac9_01_mount_candidates.yaml`（449 行机生候选表）+ `fac9_02_tag_candidates.md`（12 条目的标签候选）+ 本报告。
> 性质：**纯只读盘点**——未改 `docs/03_modules/**`、未改任何既有注册册、未改图9 本体。

## 一、计数（与 yaml counts 字段一致，此处不重复明细）

- 总行数 449；可挂载（verdict 1/2/3/4）333；反面 116。
- verdict 分布：判据1=181｜判据2=61｜判据3=88｜判据4=3｜反面=116。
- 置信分布：high=154｜medium=129｜low=166。
- 现挂面：已在图9（是=24，打包=4）；新候选（否）=421。
- 覆盖面来源：`docs/03_modules` 在域面 blueprint 237 册 + MOD-BT 编号面 166 号（全量枚举，与任务单预扫数 166 实证吻合）+ 判据4 config 图引用面 + 病历/代码面补充。

## 二、现挂面核验（28 件）——3 处名实问题挂账（不属本车道修，移交总筹）

1. **FAC-E4 挂点 `module_ref: MOD-BT-039` 名实错位**：翻译册 039=C4 翻译共享引擎（`scripts/backtest/translated/_c4_engine.py`），与「考试咽喉」语义不符；E4 真身机械面（WFO/purged CV/CPCV/DSR/闭卷闸/N试次账本）在清点表 `af:*` 与 SIM-021/022/023/024、MOD-BT-200/201 等行。建议 F2 批核图头挂点。
2. **FAC-E1A 挂点 `MOD-BT-035`**：翻译册名=「C2 粗筛成绩灌表」，与「车道A-社区货源」名义对不上（灌表是 A 车道下游工序，爬取器本体无独立编号）。
3. **MOD-BT-201 双源冲突**：path_ownership_map 唯一路径=`tests/backtest/test_forward_post.py`（E7 前哨对账器），而 `battle_map_alignment_report.md` 表行=Closed Book Gate（`src/zephyr/backtest/core/closed_book_gate.py`）。两真源打架，挂载前需考古定谳。

## 三、判据4 一岗多图实证（合法多处引用，非抄写）

- **图9 × 图7（trading_decision_map）共享 5 件**：`MOD-PA-003 / MOD-PA-007 / MOD-PA-022 / MOD-PF-007 / MOD-REGIME-001`——编制归属：PA 族与 PF-007 归本图（为工厂而生的判定/归因件被 TDM 消费），REGIME-001 归图7（为交易决策而生、E8 元分配消费）。清点表已按此给 home_map。
- **图9 × config/ai_search_veins.yaml**：E1 进货件族 13 个引用号被搜索矿脉配置整面消费（E1G 供需要源），属配置消费面非第二张图，不构成双编制。
- 其余四图（图11 交付/图12 数据供给链/交易日循环/施工流）与本图 module_ref 零交集，判据4 无争议面。

## 四、预扫提示逐条验证结论（含 2 条降级，证实「提示须验证不是结论」）

| 预扫提示 | 验证结论 |
|---|---|
| 主干=_domain_backtest 全量 | ✅ 成立：域 11 册+编号面 166 号全量入表，判据1 主力（E3 78 行+E4 78 行大头） |
| _domain_pf_alloc/_domain_portfolio_alloc/_domain_portfolio_core 装配线 | ✅ 成立：E8 组 34 行（PA-002..024 族+PF-001/002/006/008+code 面 5 件） |
| E1 车道件 | ✅ 成立：A/B/C/D/E/F/G 七车道全量（含 F 车道 adapter/executor/ANOVA/WFA 正考 4 件） |
| _domain_data algo_flow/sector_line | ✅ 成立：sector_state_pipeline（板块状态管道）判据2 入表（home=图12）；algo_flow 目录=ALGO_FLOW 外部真源册族（131 yaml），其中回测引擎机械面 18 件以 af: 行入表 |
| _domain_feedback_loop 衰减回灌 | ❌ **降级为反面（同名陷阱）**：该域三册=AI 自我改进闭环（meta_harness/module_matcher/skill_library），与策略衰减回灌（E6→E1）无关；真回灌件=`scripts/backtest/feedback_prior.py`（回灌边消费端读数件）+`strategy_iteration_upgrader`（因子域）。挂载时勿被域名误导 |
| 伸手件=_cross_layer 四件 | ⚠️ 部分降级：resource 族四件（gate/profile/sampler/alerts）+resource_optimization_engine+auto_runtime_core ✅ 判据3 挂 E0；**gate_engine 降级反面**——G0-G7 任务门禁是提交期治理门，工厂运行时零消费；shared_core/model_profiler 保持判据3 low（横切设施，无单环节归属） |
| 基础设施数据库存储（E4 速度） | ✅ 成立：database_layer/SH-DB-001/CH 机械面/redis/WAL checkpoint/缓存/压缩归档等判据3（速度）入表 |
| LSG 安全网关（E1B/E2 LLM 必经） | ✅ 成立：MOD-LLM_SECURITY 判据3 high（车道B/预审/翻译/车道G 全部 LLM 调用必经）；补 ml_serve 双 adapter（codegen/deep_review）与 intelligence 双 LLM 池为判据2 供力手 |

## 五、medium/low 清单及原因（106 medium 可挂 + 89 low 可挂；反面 low/mid 不列，全量在 yaml）

**medium 可挂 106 件**，按原因分五组：
1. **证据在但本人不判 high（编号面 mid 26 件）**：MOD-BT-006/023/024/036/037/038/077/081/094/191/197/201/202/203/204/211/212/213/214/215/222/223/226/231/232/233——多为「翻译册名与前缀匹配有噪声」「双源名实冲突（201）」「挂起/试点态（036-038）」，方向判据1/3 无疑，挂载时按 stage 直接取用。
2. **跨域伸手件（cross_layer/infra 16 件）**：SH-DB-001、MOD-RESOURCE_OPTIMIZATION_ENGINE、MOD-RESCHED-GATE/PROFILE、database_layer、MOD-INF-001/015/045/063/066/069、strategy_canary_release、wal_checkpoint_monitor 等——判据3 成立但影响量级未实测（E4 速度因子缺定量），挂载前无需复核，facts 批（F3）补 trigger_facts 即可。
3. **判据2 供数/供力手（data/mkt/ml/intel/alt 22 件）**：MOD-DATA-069/072、MOD-L00-021、source_sla_tracker、MOD-MKT-005、ml_model_factory、kan/patchtst 密度家族、local/api_llm_pool、MOD-INT-AISA、sentiment_engine 等——「伸进本流程的手」成立，home_map 已按编制图标注（图12/图7/无纵向图）。
4. **E8/E7 组合线（12 件）**：MOD-PA-006、MOD-PF-006/008、strategy_capacity_estimator、strategy_factory、REGIME-002/005/011/016、MOD-SIM-002、overfitting_protection_gate、weight_ssot 等。
5. **代码面/af 面（30 件）**：af:* 引擎机械面 18 件（ALGO_FLOW 册实证，判据1 E4）+ league/replay/grid/前向止损等 12 件。

**low 可挂 89 件**，按原因分四组（F2 前建议抽查前两组）：
1. **工具/病历性质待归类（E4/E7 周边约 20 件）**：MOD-BT-032/033/034/083/092/218/228、reexam_harness、exam_cost_reexam、dsr_recalc_backfill、replay_drill、crisis_drill、condition_attribution、almgren_chriss、sim_promotion_memo、strategy_lifecycle_advisor 等——一次性工具与常设机制的边界未定谳（SOP 反面=纯个案；本表暂按「可重复使用的质量设施」给判据3 low，若总筹按个案处置则转反面）。
2. **判据2 弱手（alt_data/intel/data/ml 约 35 件）**：alt_data 八件（web_scraper/social_sentiment/research_report/filing_nlp/policy 双件/concept_mapper/健康管理与目录）、intelligence 六件（news_linker/nightly_window/llm_fundamental/llm_research/event_chain/market_interpreter）、data 六件（auto_backfiller/breadth/sector 双件/mtf/refdata/financial_parser）、ml 四件——「伸进来」方向成立但消费点在车道侧无直接 import 证据（车道件多为经 LSG/经台账间接消费），confidence 如实给 low。
3. **regime/trading 编制外手（约 12 件）**：MOD-REGIME-006、style_regime/cross_sectional/market_forecast、MOD-TRADING-002/004/012、refdata 双件、SIG-141、trace_context_store、signal_quality 三件——编制图7/图12，本图只取单只手，强度低。
4. **组合/数据边角（约 22 件）**：rebalance_cost_analyzer、funnel_adjudicator、exposure_manager、factor_vote_mining、signature_feature_extractor、qnn_two_stage、ts_augmentation、decision_annotation、reproducibility、research_data 双件、research_asset_versioning、data_eng 四件、冷归档、league 双件、pf_alloc 双件（sector_distribution/tail_hedge）等。

**反面 116 件摘要**（全量在 yaml，按 verdict=反面 筛）：全系统旁观基建（灾备/盘点/遥测/拓扑/日志）、执行与高频域（hot_plane/latency/shared_memory——图9 boundary 明排高频/做市）、币圈件（MOD-BT-031+data 域 crypto 族——markets=[cn_a]）、TDM 编制件（decision_map/validation/trigger/结算/异常退出）、AI 运营域（cross_layer 治理九件+orchestrator 四件+intelligence 记忆四件+feedback_loop 三件同名陷阱）、退归/placeholder（MOD-BT-026 退归实证、079/097-101/133/140/210/219/234 无实体）、产品非机制（087/093/095 联赛参赛策略——不挂产品挂机器）。

## 六、策略域病历册清单（§3 病历挂载面——每本须被 ≥1 环节挂载，未挂=覆盖账本判红）

| # | 册 | 身份/路径 | 性质 | 建议挂载环节 |
|---|----|----------|------|-------------|
| 1 | 因子研究案例库 | MOD-L02-027，`data/databases/factor_casebook.db`（册蓝图 `docs/03_modules/_domain_factor/casebook/blueprint.md`） | 成功/失败→修复案例（防 AI 重复试错） | E4（+E1C 挖掘前查库） |
| 2 | N 试次账本 | MOD-BT-200，`src/zephyr/backtest/core/n_trial_ledger.py` | FDR 预算证据位（三铁律②执法台账） | E4 |
| 3 | 预审判定台账 | MOD-BT-152/153，表 `c1_backtest.hypothesis_precheck` + `scripts/ch/apply_hypothesis_precheck_ddl.py` | E2 判定记录 | E2 |
| 4 | 考试成绩+判定书台账 | 表 `c1_backtest.strategy_screen`（图9 FAC-E4 store_refs）+ 查询器 MOD-BT-078 | E4 成绩册 | E4 |
| 5 | 衰减死因册 | E6 判死行追加（`oos_years_decay≥0.5` 判存疑 + `decay_cause` 枚举 crowding/regime/overfitting/tech/depletion，台账只增）+ MOD-BT-018 衰减监控 + `dir:_domain_signal_quality/signal_degradation_monitor` + `dir:_domain_fbl_detectors/distribution_drift_monitor`（分布漂移信号源） | 衰减/死因档案 | E6 |
| 6 | 过拟合裁定档案 | `src/zephyr/backtest/core/overfitting_adjudicator.py` + `dir:_domain_simulation/overfitting_protection_gate` | 裁定记录 | E4 |
| 7 | 回测 run 档案图书馆 | `src/zephyr/backtest/run_archive.py` + `data/backtest_artifacts/runs/`（校验器 `scripts/backtest/verify_run_archive.py`） | 成绩原件归档 | E4 |
| 8 | 试验台账红证 | MOD-BT-228（P0-6 批末记账红证）+ MOD-BT-032/033/034（P0 印教材/对照器/成本验证件） | 成本红线证据 | E4 |
| 9 | 进货台账（含对账） | `data/strategy_intake/`（候选清单+出生证）+ MOD-BT-231 `scripts/backtest/intake_ledger_recon.py`（对账核验器） | 进货出生证册 | E1 |
| 10 | 翻译件台账 | translated_manifest（E3 construct 产物，`scripts/backtest/translated/` 35+ 验收集+backlog） | 翻译验收册 | E3 |
| 11 | 模拟盘病历族 | MOD-BT-223 判定台账表结构（`schemas/categories/sim_daily_report.py`）+ `sim_platform_journal.py` 平台日刊 + `sim_deviation_report.py` 月度偏离报告 + `sim_governance.py` 治理建议 | E7 前哨病历 | E7 |
| 12 | 联赛档案 | `league_registry.py`（赛马计分板）+ `league_archive.py`（档案打包）+ `league_monthly_snapshot.py`（月度快照）+ `league_restore.py`（复原） | E7/E8 赛马档案 | E7 |
| 13 | 模型版本注册表 | `dir:_domain_machine_learning_train/model_version_registry` | 模型版本台账（Kronos 等基线） | E1E |
| 14 | 全域事实台账 | `dir:_domain_intelligence/universal_fact_ledger` | 进货证据位 | E1G |
| 15 | 复现演练档案 | `scripts/backtest/replay_drill.py` + `crisis_drill_monthly.py` | 复现/危机演练记录 | E4/E7 |

## 七、其他发现（移交总筹）

1. **`docs/03_modules/_domain_strategy_pipeline/` 目录零 blueprint**（仅存在于域列表）：策略管线域册缺位，而其代码面（src/zephyr/strategy_pipeline 13 py）恰是 E3-E7 主干（BT-187~199/212~214/225/232 全挂此目录）——域册与代码面脱节，建议补册或并入 D_BACKTEST 编制说明。
2. **`scripts/backtest/t0_*` 三件**（t0_material_line/t0_rule_engine/t0_state_match_matrix）与 `f06_e4_wfa_exam.py.tmp.*` 两个 tmp 残留在 scripts/backtest/——t0 族判 TDM 做T 域未入表；tmp 残留建议随存量清算清走。
3. **翻译册个别 name_zh 有函数级噪声**（如 MOD-PA-003 取到「资金分配输入非法」等 docstring 首行），本表已用蓝图标题/编号面考古名纠偏；翻译册本体回填不在本车道。
4. **图9 地图 16 节点 vs 本表 333 可挂机制行**：单节点挂载面最重的是 E3（78）/E4（78）/E8（34）——与 SOP「同标签多钉=重复簇显影位」预告一致，内收对审（§5 步7）重点核查 E3 验收集与 E4 考尺的重复簇。

## 八、降级直改主区原因登记（RULE-WORKTREE §10）

本车道三件产出（fac9_01_mount_candidates.yaml / fac9_02_tag_candidates.md / fac9_01_report.md）为**新建小面文件**（非热册、非他人 claim 面），任务单明示降级直改主区：目标文件面小且当前零活跃 claim（`lock_files.py list` 实测 docs/_working/map_census/ 无他 claim；vmap12_f1a 为邻车道件未相交）。改前已 acquire 三件（持单 st-map9-f1-20261003），全程未触碰 `docs/03_modules/**` 与既有注册册。

## 九、未决项（供 Owner 转总筹）

1. 三处现挂名实问题（§二）待 F2 批核图头：E4→039、E1A→035、BT-201 双源。
2. medium/low 复核清单（§五 195 件）由 F2 按需抽查，优先级=§五 low 组1（工具/病历边界 20 件）。
3. 病历册 15 本（§六）待 §3 完备性校验：逐本落到 casebooks 字段，未挂本=覆盖账本三红之二。
4. `_domain_strategy_pipeline` 域册缺位（§七-1）与 scripts/backtest tmp 残留（§七-2）建议开小施工单。
5. 目的标签 12 条（fac9_02）待 Owner 一轮终审冻结。

## 十、堵点实录：CREATE-GUARD token 登记未成（登记两连拒，按纪律停手；三件产出已 staged 待 requeue）

**时间线**（2026-10-03 22:36-22:4x，capability_canonical_file_registry.yaml）：
1. 首次登记：整册 YAML 解析崩（`di_seam_exemptions: []di_seam_exemptions: []` 尾行重复拼接）——他会话 `st-vm12f1-20261003`（图12 F1 车道，registry 当时的 claim 持有者）在途写损坏。
2. 数分钟后该会话自愈重写，册恢复可解析（12744 tokens），但其快照领先/异于 HEAD：batch_creation_tokens 以 HEAD 为只增不减基线 → 拒写。
3. 逐对分诊实证（file+token 二元组，非丢单）：HEAD 有 `('src/zephyr/governance/reuse_scan.py', 'surgery-c-reuse-scan-20261003')` 而盘面无；盘面多出同名 token 挂新路径 `('src/zephyr/governance/audit/reuse_scan.py', …)` + vmap12_flesh 五条新登记。**旧路径文件已不存在、新路径文件在盘未进 HEAD**＝手术批改名后注册册盘面领先 HEAD，工具 HEAD 基线判「缺 1 条」属改名滞后误报，非蒸发。盘面另有 vm12 五条新 token 为真增量。
4. 两次登记均未落盘（第一次解析崩、第二次写前自检 fail-safe 拦截），**按任务单「登记两次失败→停手报告」停止**；registry 为 st-vm12f1 claimed 在途热册，本车道不代修不覆盖（B23 禁整片回退铁律）。

**三件产出现状**：已写盘+已 `git add` staged（`docs/_working/map_census/fac9_01_mount_candidates.yaml / fac9_02_tag_candidates.md / fac9_01_report.md`），未 enqueue（无 token 入队必死=白造死信，故不投）。

**复投处方**（registry 归属理清后任一会话三步，~1 分钟）：
```bash
# ①若裁定「补回旧路径对」：按 batch 工具处方增量补 HEAD 基线差（禁整片 checkout）
#   ——更优解：等手术批「audit/reuse_scan.py 改名+注册册同步」commit 落 HEAD 后基线自然对齐
python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix docs/_working/map_census \
  --created-by st-map9-f1-20261003 --capability map9_f1_census \
  --merge-evaluation "跨域不同对象不并：图9 F1 清点三件套（候选表/标签候选/车道报告），map_census 家族新图实例，非既有 census 第二实现"
# ②先重新 acquire（原 claim 已 release/过期）再入队
python scripts/lock_files.py acquire docs/_working/map_census/fac9_01_mount_candidates.yaml st-map9-f1-20261003   # 三件同理
python scripts/git_commit.py --session st-map9-f1-20261003 --files docs/_working/map_census/fac9_01_mount_candidates.yaml docs/_working/map_census/fac9_02_tag_candidates.md docs/_working/map_census/fac9_01_report.md --enqueue
```
