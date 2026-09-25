---
doc_type: audit_report
campaign: decision_map_campaign
title: 整装回测全环节审计（"宇宙不完整"同款举一反三）
date: 2026-09-24
author: 整装回测审计班（只读挖掘，唯一可写=本文件）
status: delivered
evidence_rule: 每论断带文件路径；历史已修案底标注"已修+commit"防重复立案；无证据处写"仓内未见"
note: 本文件为新建件，CREATE-GUARD creation_token 登记由落地车道随批补办（同 10_evaporation_forensics.md 先例）
ttl: task_bound
---

# 11_integrated_backtest_audit.md — 整装回测全环节审计报告

> 背景：Owner 09-25 深夜问"板块为什么只有 469 个"（答案=通达信 881xxx 行业族从未采补；
> 真源：`docs/_working/2026-08-30-b7-batch-bc-doc-supplement-checklist.md:87`（sector_list 0 行/881xxx 候选源）+
> `docs/_working/sector_line/sector_internal_inventory.md:30`（kline_sector_880=469 码））。本审计对整装回测
> 全链举一反三：每环节都问一遍"它的 469 vs 800+ 在哪"。
> 审计窗口：2026-09-24 深夜（GPU T1 跑批中，grid_20260924-213246，见 `docs/_working/decision_map_campaign/README.md` 状态仪表盘）。
> 链路真源五册：`docs/_working/integrated_backtest/`（PROTOCOL-V1/DATA-MATRIX/RUN-REPORT/REDBLUE-REPORT/FINAL-DELIVERY）+
> `max_remediation_plan.md`（批 A-H）+ `IBT-HANDOFF-TO-MAX.md`（14 项问题清单）+ `docs/_working/e2e_integration/LEDGER.md`（GPU 总包台账）。

## §0 八环节一页总览

| 环节 | 一行判定 | 最重的"469 vs 800+"同款 |
|---|---|---|
| ①数据供给与宇宙构建 | 表级窗口全绿但宇宙坐标系统 Multiple 且无裁定：板块五口径、指数成分断供、因子落表面断裂 | 板块 469/596/90/499/727 五口径并存+881xxx 零采补（IBT-A01）；index_constituent 000010.SH 零行（IBT-A02） |
| ②信号与因子层 | 15 员池是"污染时代成绩单+修后重考收缩"的混血：修后合格名单 17→3 且未落主区 | E4 存活 17 条 vs 修后成本合格 3 条（IBT-B04）；FACT 族 IS 前段 26 个月零贡献（IBT-B02） |
| ③组合构建 | 等权 1/15 占位件在跑，装配层本体未建 | 7 态×15 员权重矩阵=0（应 105 格全空，IBT-C01） |
| ④执行模拟与成本模型 | 引擎防线红证扎实，但考尺引擎与整装引擎成本口径分裂 | 同一策略两套成本真相（平面 5bp vs ADV 分层标定，IBT-D01） |
| ⑤考尺与考试门 | 哑门三修已落（已修+commit），判定语义 fail-closed 在岗；考试循环本体从未自动运行 | meta_question_exam_result=0 行、283 题全 registered（IBT-E07） |
| ⑥HOLDOUT 闭卷考 | 单次烧毁纪律执行了，但批 D 新鲜窗重考未完成——GPU 搜索的池基悬空 | 批 D 产物仓内未见；artifacts_v2 仅 1 个 pkl（IBT-F01） |
| ⑦报告与面板 | 首跑五册报告在 HEAD，但成绩单与面板断桥、审计链尾件卡暂存区+蒸发风险 | 22 件 nav/trades/run_summary 尾件主区盘面已不见（IBT-B03） |
| ⑧回测与实盘一致性 | 滑点标定真源已治本（已修），但校准闭环零样本、落地通道两处 P1 缺陷 | sim_trade_log 切点前 0 行——回测↔实盘滑点偏差校准分母为零（IBT-H02） |

---

## §1 环节①：数据供给与宇宙构建

### 1.1 链路现状（组件+路径）
- 表级探针：`docs/_working/integrated_backtest/IBT-DATA-MATRIX.md` §1 + 机读 `ibt_data_matrix.yaml`（wall 279s 实测）——kline_daily_hfq（W_IS 484.7 万行/4996 标的→W_HOLDOUT 5216 标的）、stock_indicator、stk_limit、regime_snapshot_history、index_constituent 000300.SH（482 版本行）、kline_index 四指数，四窗全绿，判定"无阻断缺口"。
- 策略级冒烟：17 条×4 窗 build(start,end) 实测（同上 §2）。
- 引擎侧宇宙防线：PIT 标的池过滤（退市/ST/次新 120 日）默认开=`scripts/backtest/ibt/ibt_runner.py:322`（enable_pit_universe_filter=True）；成份宇宙=c4 引擎 SCD-2 窗口并集=`scripts/backtest/translated/_c4_engine.py:252`（load_index_constituents）。
- 数据地基凭证：`docs/_working/data_fix_campaign/final_delivery_report_20260921.md`（九项目标七绿两挂账，tick/五档 09-17 找回 2832 万行）。

### 1.2 已知缺陷/历史伤疤
- 600016 复权事件缺+老股深史 0.2-0.4% 偏差=登记级尾款（`IBT-PROTOCOL-V1.md` §4，甲线尾款在案）。
- regime_snapshot_history 多 run 重叠（W_IS 2312 行=2 run），消费靠 runner 手工锁定 run=VAL-P0-20260916-230726（`IBT-DATA-MATRIX.md` §1）——无机械闸。
- FACT 族 IS 特征行空（宇宙回看窗 425 天 vs kline_daily_hfq 2019-01 起）——同根见 1.4。
- 板块分钟 K 断供与假 SUCCESS：kline_sector_intraday 5m/15m/30m/60m 四档全部停在 09-10（`docs/_working/e2e_integration/LEDGER.md` ④·进度）；盘面 kline_resampler.py 仍指 kline_sector_880 旧表；板块分钟 K 真值源未定、现 synth 合成行顶着（`docs/_working/decision_map_campaign/02_rulings_and_calibers.md` §七）。
- 蒸发连环案伤疤：09-24 凌晨 03:47-07:46 主区四起 untracked 全灭（`docs/_working/decision_map_campaign/10_evaporation_forensics.md`）——回测产物类 untracked 件是高危人群。

### 1.3 "全不全"审计（对标 469 vs 800+）
- **板块宇宙五口径并存无裁定**：kline_sector_880=469 码 vs kline_sector=596 码 vs sector_meta=90 行业 vs 申万=499 名 vs kline_sector_intraday=727 码（近三日 580 板）——`docs/_working/sector_line/sector_gap_list_and_construction_proposal.md` G5（"施工前先出一页板块坐标系裁定"）；881xxx 行业族从未采补（`docs/_working/2026-08-30-b7-batch-bc-doc-supplement-checklist.md:87`）——**与本审计母题同款，且 L2 板块轴 sector_state 仅 17 日×469 板（`docs/_working/e2e_integration/w3_w5_precheck_20260923.md` §2.4）**。
- **股票指数成分断供**：index_constituent 000010.SH（上证 180）SCD-2 零行，PIT 引擎 fail-closed 炸响=正确（`docs/_working/integrated_backtest/batch_b_pit_repair_comparison.yaml` B-F2）——凡以非 300/500/852/16 指数为靶的策略，其宇宙根本建不出来。
- **因子矩阵（alt-data 族）切点前零样本**：money_flow 2026-06 起、sector_fund_flow 2026-09 起、alt_stock_comment 2026-09-11 起、weather_data 2026-08 起……96 条 insufficient 逐条实证（`docs/_working/e2e_integration/panorama_health_snapshot_20260924.md` §四）——"全 A+全史"只对价量类表成立，另类因子在回测窗内是空矩阵。
- **生产因子落表面断裂**：factor_signal/factor_feature_value 两 CH 表不存在（`docs/_working/e2e_integration/LEDGER.md` ④·进度二遗留缺口）。
- kline_etf_daily 仅 2026-07 起（`IBT-DATA-MATRIX.md` §3）——ETF 执行腿无深史。

### 1.4 "对不对"审计
- FACT 族宇宙回看窗导致 IS 生效起点后移 2021-04-01，前段零贡献已按协议 §1 预注册披露（`IBT-DATA-MATRIX.md` §2 根因段）——处置正确但依赖披露纪律，无机械断言"该成员在窗内是否被静默置零"。
- 复权对齐链抽检违例率≠0：PQ-0012/PQ-0131（月度 50 只×56 个月抽样 53,134 点，U4 口径违例 45.4%）——`panorama_health_snapshot_20260924.md` §三——回测价的复权正确性在抽检口径下未闭合。
- 探针 SQL 列名不符误报（financial_derived trade_date 不存在）已在 `IBT-DATA-MATRIX.md` §1 澄清为探测问题非数据缺失——诚实披露在案。

### 1.5 自动吗
- 半自动：02:30 tilib 夜跑带自动推进 hfq 表（跨批微漂根因，`IBT-CAMPAIGN-LEDGER.md` §3 03:02 批）；数据线七分包修复已落代码+哨兵 58 腿（`final_delivery_report_20260921.md` §1 分包3）。
- 手工：完备性矩阵探针、板块分钟 K 回补、宇宙坐标裁定——均人工触发；仓内未见"宇宙完整性"常驻探针/gate。

### 1.6 施工项
| 编号 | 项 | 优先级 |
|---|---|---|
| IBT-A01 | 板块坐标系裁定页+881xxx 采补立项（五口径辨析，sector_gap_list G5 落地） | P1（L2 层+T1 板块分层键前置） |
| IBT-A02 | index_constituent 000010.SH SCD-2 回补或改靶裁定（B-F2） | P1 |
| IBT-A03 | 板块分钟 K 5m/15m/30m/60m 09-10 缺口回补+resampler 换表修复件回补+真值源裁定 | P1 |
| IBT-A04 | regime 消费 run 锁定机械化（禁口头锁 run） | P2 |
| IBT-A05 | kline_etf_daily 深史回补（指数腿实盘化前置） | P2 |
| IBT-A06 | factor_signal/factor_feature_value 落表面重建 | P2 |
| IBT-A07 | 复权对齐抽检违例（PQ-0012/0131）定性回查 | P2 |

## §2 环节②：信号与因子层

### 2.1 链路现状
- 池真源=E4 存活 17 条（剔除 2 死刑=15 员），`IBT-PROTOCOL-V1.md` §1；名单真源=`docs/_working/archive/2026-09/sharpe2_prep/`（reexam_results.csv）。
- 面板生产=c4 翻译件 build(start,end)（`scripts/backtest/translated/c4_*.py` 85 件族+`_c4_engine.py`）；首跑工具正门化后=`scripts/backtest/ibt/`四件（fc16e63162 落 HEAD，W_OOS 复跑 410/410 逐位一致 R-022 PASS）。

### 2.2 已知缺陷/历史伤疤
- #326 池污染（成分回灌 15 件+同 bar 7 件）：裁定#326（`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:4036`）。**批 B 已修**：修复 commits=edd503efb5e+c0f8763511，修前/修后/复核对照表冻结件=`docs/_working/integrated_backtest/batch_b_pit_repair_comparison.yaml`（复核轮 C4-SCD2-VERIFY-20260923 与修后逐位一致）——防重复立案。
- 污染时代旧行仍在账（B-F4，同上文件）：C4-translated-20260912/0915 批未逐行标 suspect；C6 bothwin 及格集底座刷新未做。
- HOLDOUT 盲窗 4/15 微正互证池失效（`IBT-RUN-REPORT.md` §3）。

### 2.3 "全不全"审计
- **17 存活 vs 修后成本合格 3 条**：`D:\ZephyrAlpha\.worktrees\st-e2e-20260924\docs\_working\e2e_integration\cost_qualified_list_reexam_20260923.yaml` 实测 pool 17→cost_qualified_n=3（8d00/e3da/29eb），4440 照妖镜拦截（81.57x 换手）——**该名单主区盘面与 HEAD 均未见**（e2e LEDGER 收官待办："cost_qualified_list_reexam_20260923.yaml 缓收"）。GPU 搜索要接的池基在主区不可见=本环节最大的"469 vs 800+"。
- 池外因子轴：factor_registry 175 条、strategy_registry 161 条（19 active+139 candidate+3 deprecated）+"退役 600+"有下落（`02_rulings_and_calibers.md` §四）——重考三纪律已立未执行。

### 2.4 "对不对"审计
- 符号后缀缺陷（FACT 面板 .SZ 后缀 vs 引擎裸码→六员不可成交，首版 IS/POSTD 作废重跑）：`IBT-RUN-REPORT.md` §5 缺陷#1——runner 已补 split('.')[0]，`exam_cost_reexam.py` `_norm_frame` 同款纪律已固化——已修。
- 六段温度两实现未对齐真源：auto_mount.py:129 R2SIX（法定）vs daily_decision_orchestrator.py:110 REGIME_TO_SEGMENT（产线占位，r4/r2/r1 三键冲突）——`02_rulings_and_calibers.md` §三，修复六步在 quant_methodology/appendix_C——**未施工**。

### 2.5 自动吗
- 手工 CLI 为主：翻译件 build、批 B/C/D 重考脚本均人工触发；F06Grid 有 Task Scheduler 周六 14:00 档（`scripts/register_f06_grid_task.ps1:12`）；退役重考循环仓内未见自动实现（PQ-0097 实证"三件对应的调度代码全仓零实现"）。

### 2.6 施工项
| 编号 | 项 | 优先级 |
|---|---|---|
| IBT-B01 | 批 B 残留收尾：污染时代旧行标 suspect+C6 及格集底座刷新（B-F4） | P1 |
| IBT-B02 | FACT 族 IS 前段 26 个月零贡献：深史回补评估或断言固化 | P2 |
| IBT-B03 | 【09-26 结案勘误】22 件全数找回（.runtime/commit_queue/blobs/ 内容寻址袋 22/22，34 项对账全绿——见 16 号文）。根因修正：非"两规则冲突待裁"，而是 **N-16 的 skip_dirs_docs 真源提交面从不消费**（只有审计面剪枝）→产物长期滞留 untracked 面等蒸发；修复=check_naming_convention.py 补 _in_n16_skip_dir() 双向执法（274 项回归绿），袋 q-20260925-st-ibt22-recovery-0001 已入队 | **CLOSED** |
| IBT-B04 | cost_qualified_list（17→3）落主区+作为整装 v2 池基登记 | **P0** |
| IBT-B05 | 六段温度两实现对齐（appendix_C 六步） | P1 |

## §3 环节③：组合构建（pf_alloc/权重）

### 3.1 链路现状
- 合成算子 compose_weight_panels（等权 α=1/15，行级 Σ>0 归一）=`src/zephyr/pf_core/strategy_engine/framework_composer.py:1002`（动态版 :1244）；IBT-A/B 两方案=`IBT-PROTOCOL-V1.md` §7。
- 生产侧 pf_alloc：allocation_orchestrator/batched_position_builder=`src/zephyr/pf_alloc/`；日循环 16:45 圈已跑通（`e2e_integration/LEDGER.md` ④·进度二：run_daily_loop 8 段全 ok）。

### 3.2 已知缺陷/历史伤疤
- pf_alloc 三连 poison（load_anchored_cap 对 tuple 行调 .get()）——**已修**（2d6ae249f3，`e2e_integration/LEDGER.md` 收官状态"pf_alloc 治本"）——防重复立案。
- 单票硬上限口径：代码实测 5% 较题面 10% 更严、'15% 上限'约束在代码中未定位（PQ-0049/PQ-0094，`panorama_health_snapshot_20260924.md` §四）。

### 3.3 "全不全"审计
- **权重矩阵零格**：7 态×15 员 regime 权重矩阵 v1 预注册不做（`IBT-PROTOCOL-V1.md` §7），E8 装配层（QuantCombine 三算法+矩阵）未建（`max_remediation_plan.md` 批 G）——组合维度当前只有 2 个配置（A/B）。
- PP-001 sleeve 独立子账户 vs 单账户线性合成结构性丢失（协议 §10.5）——五项交互未建模。

### 3.4 "对不对"审计
- 满仓摊派语义（任意成员有信号即满仓，半仓意图被放大）——协议 §10.1 如实披露，Σ<1 直通未建（`max_remediation_plan.md` 批 G，R-022 要求独立批+数值回归对照）。
- regime 节流先验映射（r4→0.5/r10→0.2）带"事后知识风险"自披露（协议 §10.4），实测四窗三负（`IBT-RUN-REPORT.md` §2 归因2）——判定脱钩正确。

### 3.5 自动吗
- 生产侧自动（日循环 16:45+事件）；回测侧合成全手工（runner 脚本）；fw_backtest 事件触发链存在（`src/zephyr/strategy_pipeline/fw_backtest.py` 挂图→emit_fw_backtest_due，断桥③桥件）但与 IBT 协议链未打通。

### 3.6 施工项
| 编号 | 项 | 优先级 |
|---|---|---|
| IBT-C01 | E8 装配层+7 态×成员权重矩阵+PP-001 生产配比（批 G） | P2 |
| IBT-C02 | 引擎 Σ<1 目标权重直通（批 G，R-022 数值回归对照） | P2 |
| IBT-C03 | G4 棘轮/做T 配对核算（批 G，落地前折扣标注持续） | P2 |
| IBT-C04 | 单票上限/15% 约束口径三查（PQ-0049） | P2 |

## §4 环节④：执行模拟与成本模型（c4 引擎/五档）

### 4.1 链路现状
- 整装引擎=DefaultBacktestEngine（向量化日频，T+1 硬断言/开盘优先成交/PIT 池/参与率 10%/护栏）=`src/zephyr/backtest/implementations/vectorized_engine.py`+撮合真源 `src/zephyr/backtest/core/matching_logic.py`（佣金万 0.854 双向+5 元地板+印花 0.0005 卖出+过户费）；滑点腿单一真源=`src/zephyr/backtest/core/cost_model_calibration.py`（ADV 分位分层+Almgren-Chriss 冲击）。
- 考尺引擎=冻结土规 `_c4_engine.py`（run_backtest/daily_net_returns，gate_limits 涨跌停闸+slippage_bp 档覆盖，:399/:439）。
- 五档成本门扫描=exam_cost_gate.run_cost_tier_scan 接入 factory_grid_executor（`scripts/backtest/factory_grid_executor.py:796-803`）。

### 4.2 已知缺陷/历史伤疤
- **哑门事故**：exam_cost_gate 位置传参致滑点从未进入计算（五档 Sharpe 全等 10.6211）+bp=0 顺手关涨跌停闸+缺册静默默认档+换手缺键零放行——**四件全部已修**（`docs/_working/e2e_integration/w3_w5_precheck_20260923.md` §2.1；修后 40bp=3.8307；commit 80880932d4；契约钉 `tests/backtest/test_cost_gate_tier_wiring.py` 未修字节 3 红）——防重复立案。
- 旧伤疤：matching_logic.SLIPPAGE_BPS=1 无出处、AC 冲击恒 ±1bp 零方差、地板佣金吞噬 51.7%——**已修**（cost_model_calibration.py 头注，车道 M/台账 #23 H2-A·H2-C）——防重复立案。

### 4.3 "全不全"审计
- **双引擎成本口径分裂（本环节最大的"469 vs 800+"）**：考尺引擎 `_c4_engine.py:46-48` COMMISSION_BP=2.5/STAMP_BP=10/SLIPPAGE_BP=5（平面常数）vs 整装引擎 matching_logic 万 0.854+ADV 分层标定+AC 冲击——同一策略在考尺与整装两侧的成本真相不同构，GPU 3700 格成绩单全部产自考尺引擎口径，与首跑五册（整装引擎口径）数字不可直译；仓内未见两口径换算/对照表。
- 五档真实成本影响已量化（五档扫描/单跑=4.0-4.5x，占单格点 83%）——`w3_w5_precheck_20260923.md` §二·五+`e2e_integration/LEDGER.md` 心跳 10:15 profiling。
- 场景覆盖：红蓝四向（前视/T+1/PIT/成本）在两窗×四轮零击穿（`IBT-REDBLUE-REPORT.md` §4）；但极端行情场景专用压测（跌停连板/流动性枯竭）除 gate_limits 闸外仓内未见系统矩阵。

### 4.4 "对不对"审计
- 净收益丢日期索引（net_returns.parquet values-only RangeIndex，产物不自描述）——**已修**（q-0010，factory nets_archive 带日期索引，`e2e_integration/LEDGER.md` 心跳 10:35/10:55）——防重复立案。
- 零成本对照 BacktestConfig 不透传 min_commission（首跑缺陷#4）——引擎级整体替换处置——已修。
- 02:30 夜跑带推进 hfq 表→跨批 sharpe 漂移（首跑缺陷#2）——同批产出纪律处置，无机械闸（见 IBT-H06）。

### 4.5 自动吗
- 引擎本身 in-process 自动；T0 标定/T1 跑批=Owner 点火+后台守护（reaper keep 在册：`data/runtime/process_reaper_keep.txt:18,34`）；探测性 profiling 手工。

### 4.6 施工项
| 编号 | 项 | 优先级 |
|---|---|---|
| IBT-D01 | 考尺引擎↔整装引擎成本口径对照表（或统一声明：成绩单数字仅考尺口径可判读） | **P0** |
| IBT-D02 | TradeRecord algo_id/order_type 归因字段（批 G 立项成立未施工；`docs/_working/fullflow_campaign/lanes/datagap_trade_record_requirement.md`+`docs/_working/recovered_task_cards/tc06_ruling_cards/tc06_r3_traderecord_card.md`） | P1 |
| IBT-D03 | 指数腿实盘化（ETF 替代+跟踪差建模，批 G） | P2 |
| IBT-D04 | 极端行情执行场景压测矩阵（跌停连板/枯 liquidity）立项评估 | P2 |

## §5 环节⑤：考尺与考试门（f06/exam_cost_gate/成本门）

### 5.1 链路现状
- 考尺=E4 正考 `scripts/backtest/f06_e4_wfa_exam.py`（IS→WFA→OOS 三线裁决全委托 strategy_validation_pipeline+DecisionGate+OverfittingDetector，:8 头注 INVARIANTS）；成本门=`src/zephyr/backtest/regime_validation/exam_cost_gate.py`（三道门：五档单调+全成本档存活+E7 换手≤8x）；预注册参数=`config/exam_scale_cost_gate.yaml`（Owner 通宵令冻结档）。
- 搜索目标函数切换=cost_adjusted_sharpe 为主（同 yaml search_objective 节）。
- 重考 runner=`scripts/backtest/exam_cost_reexam.py`（批 C 照妖镜/批 D 新鲜窗同一机械）。

### 5.2 已知缺陷/历史伤疤
- 哑门三修+换手键必取+缺册拒考——**已修**（80880932d4，见 §4.2）。
- N_eff 手填病（DSR 分母盲信 f06_survivors.csv 手填列，`f06_e4_wfa_exam.py:253` 病史自述）——**已修**（verify_n_trials_provenance RB-STATS-01 治本，:455-459 复算值为主口径，登记列降对照披露）——防重复立案。
- 多次考试假阳性案底："实测纯噪声 N=1 时 DSR=0.9986 曾判通过，一列改字即放水"（同文件 :8）+裁定#306（N=4562 下 DSR>0 数学不可过=尺子自护，`ruling_registry.yaml:3795`）——防线已加严在岗。
- E0 问闸 F06/grid 路 0 接（`w3_w5_precheck_20260923.md` §2.3）——**已接**（cfe9b86f 落 dev，终验 10/10 PASS，`e2e_integration/LEDGER.md` 收官状态）——防重复立案。

### 5.3 "全不全"审计
- **考试循环本体从未运行**：meta_question 283 题全 registered/answered=0/exam_result=0 行（PQ-0051/0052/0054-0058，`panorama_health_snapshot_20260924.md` §四）——"考试"目前只有策略级 E4 一台机器，治理级考试循环是空壳。
- 参数空间覆盖：T0 标定实测 per_point=35.33s（预算估 5.2 倍），59h 有效容量≈4809 格 vs 全矩阵 1.71M 格（0.28%）；两档粗筛方案①被 `cost_gate_in_every_tier: true`（Owner 冻结条款，`config/search_space_prereg.yaml:62`）禁用——现按 3700 格全档门跑批（`decision_map_campaign/README.md` 仪表盘）——覆盖率天花板已如实入册。
- N_trial 记账：n_trial_ledger 已接 factory_grid_executor（`factory_grid_executor.py:836-841`）；E1C/LLM 轨接线仓内未见实证。

### 5.4 "对不对"审计
- prereg SSOT 冲突（search_space_prereg 零消费方 vs position_recipe_grid_schema 机器真源、I_cost_tier 含可搜成本轴矛盾）——**已解**（裁定#413 冻结 v2，frozen_at=2026-09-24T22:00+owner_signoff 回填+per_point_seconds_measured=35.33 实测回填，`config/search_space_prereg.yaml:12-14,57`）。
- 判定语义 fail-closed（档位<3/天数<60 判不通过非跳过；证据缺失=不通过）——`exam_cost_gate.py` 头注 INVARIANTS——在岗。

### 5.5 自动吗
- 半自动：F06Grid 周六 14:00 Task Scheduler 档+GPU 手工点火；治理级考试循环=零自动化（5.3）；n_trial 记账已随跑批自动。

### 5.6 施工项
| 编号 | 项 | 优先级 |
|---|---|---|
| IBT-E01 | 治理级考试循环落地（exam_result 写入/reexam 到期/三取二裁定——PQ-0054~0058 全零样本） | P2 |
| IBT-E02 | E1C/LLM 搜索轨 n_trial 记账接线实证 | P2 |

## §6 环节⑥：HOLDOUT 闭卷考

### 6.1 链路现状
- 窗口制=W_IS（可多次）/W_OOS（准样本外）/W_HOLDOUT（2025-09-09..2026-09-08，冻结后单次烧毁）/W_POSTD（`IBT-PROTOCOL-V1.md` §3，继承 TDMAP-001 §12 D=2026-09-09）。
- 首跑执行：W_HOLDOUT 03:10-03:20 单次烧毁，IBT-A -12.24%/Sharpe -1.389→C 门不过（`IBT-CAMPAIGN-LEDGER.md` §3）。

### 6.2 已知缺陷/历史伤疤
- 无。首跑对 HOLDOUT 纪律执行无违规记录；W_OOS 与池选择窗重叠的"自证窗"风险已如实披露（`IBT-RUN-REPORT.md` §3 注）。

### 6.3 "全不全"审计
- **批 D 新鲜窗重考未完成**：`max_remediation_plan.md` §2-批 D（前置 B+C 全绿，以 2025-09..2026-09 为新鲜 OOS 重考产新名单）；实测证据=artifacts_v2/W_OOS 仅 composed_panel.pkl（09-23 05:37）、`--tag fresh` 名单产物**仓内未见**、IBT-v2 协议 v1.1 冻结件仓内未见——GPU 第一轮搜索的"池基=修后新名单"悬空，现网搜的是旧 15 员族谱系。
- 盲窗余额语义：批 D 用掉原 HOLDOUT 段后"最终盲窗=2026-09 之后前向段"（`max_remediation_plan.md` §2-D 诚实条款）——语义正确但窗口状态（哪段已烧/哪段在烧/哪段未开）无机械账本，全靠文档纪律。

### 6.4 "对不对"审计
- OOS 跨批 sharpe 漂移（02:30 夜跑带）首跑已按同批重算纪律处置（`IBT-CAMPAIGN-LEDGER.md` §3 03:02 批）——处置正确。
- E1C-09 灾难折 63 天小样本+N_eff=13 同根疑件——裁定#404 R2 并入批 D 同窗重考（`max_remediation_plan.md` 批 D 增补）；重考结果仓内未见。

### 6.5 自动吗
- 全手工：烧毁/重考均为人工 CLI+协议纪律；窗口状态机仓内未见。

### 6.6 施工项
| 编号 | 项 | 优先级 |
|---|---|---|
| IBT-F01 | 批 D 新鲜窗重考收口：fresh 名单产出+IBT-v2 协议 v1.1 冻结+E1C-09 同窗重考 | **P0**（GPU 成绩单池基） |
| IBT-F02 | 窗口状态账本件（IS/OOS/HOLDOUT/POSTD 烧毁状态机械化，禁文档口传） | P1 |
| IBT-F03 | regime 检测器 r4/r10 方向失真治本（丁线域；脱钩口径已定 IBT-A 为准） | P2 |

## §7 环节⑦：报告与面板

### 7.1 链路现状
- 报告五册+机读 yaml 全在 HEAD（`docs/_working/integrated_backtest/`；commit 3050d67/739655a，`IBT-HANDOFF-TO-MAX.md` §5）。
- 面板组件=backtest_results/backtest_performance（`src/zephyr/frontend/dashboard/components/backtest_results.py`，数据源=BacktestResult CTR-P1-016 11 必填字段）。
- 生产观察档：sim_daily_report 当日 49 行（`e2e_integration/LEDGER.md` ④·进度）。

### 7.2 已知缺陷/历史伤疤
- 收官提交 13 轮死因谱系（DCR-json/gitignore/N-16 后缀等）——`IBT-HANDOFF-TO-MAX.md` §5③——批 A 已收编主体（fc16e63162）。

### 7.3 "全不全"审计
- **成绩单↔面板断桥**：backtest_results 消费 BacktestResult 对象，IBT/考尺产物为 docs/_working yaml+data/backtest_artifacts json——两套无消费桥，"周末 GPU 成绩单"没有上板通道；仓内未见 IBT 产物的面板适配器。
- **审计链尾件蒸发风险成真**：22 件尾件（run_summary×4+sensitivity×2+nav/trades csv×16）09-22 时"盘上完好"（`IBT-HANDOFF-TO-MAX.md` §5），本审计实测主区盘面已无这些文件、HEAD 亦无（`git status`：artifacts 下仅 redblu yaml 在库，artifacts_v2/ 为 untracked）——与 09-24 凌晨蒸发连环案时间线相容（`10_evaporation_forensics.md`）；核心数字尚有五册+ibt_attribution.yaml 兜底，逐笔审计链（csv）面临永久灭失。
- 全景图健康度：TDM 182 节点仅 7 节点有题覆盖且全红、175 节点零题覆盖、254 边零引用（`panorama_health_snapshot_20260924.md` §1.3/§二）——回测相关 TDM 节点的"健康"当前不可验证。

### 7.4 "对不对"审计
- Sharpe 双口径（引擎 rf=2.5% vs 离线复算 rf=0）差异已披露"以 artifacts 为准"（`IBT-RUN-REPORT.md` §1 注）——披露在案但 artifacts 本体恰是 7.3 的蒸发风险件。
- ORPHAN 门 pathspec 误伤——**已修**（GT-ORPHAN-PATHSPEC-001，`e2e_integration/LEDGER.md` 收官状态）——防重复立案。

### 7.5 自动吗
- 报告=人工撰写五册；index.md=生成器自动（`generate_missing_index_md.py`）；面板=自动渲染但无 IBT 数据源；健康快照=临时探针（`.runtime/tmp/gpu_final_20260924/panorama_health_probe.py`）非常驻。

### 7.6 施工项
| 编号 | 项 | 优先级 |
|---|---|---|
| IBT-G01 | GPU/IBT 成绩单上板桥（BacktestResult 适配器或专用成绩单页） | P1 |
| IBT-G02 | 22 件尾件对账+抢救性落库（与 IBT-B03 合并执行） | **P0**（并入） |
| IBT-G03 | 健康快照探针常驻化+回测族 TDM 节点出题覆盖 | P2 |
| IBT-G04 | c1_market.account_nav_daily 0 行（模拟盘 NAV 账断裂）修复 | P2 |

## §8 环节⑧：回测与实盘一致性（滑点假设 vs 实盘）

### 8.1 链路现状
- 回测侧：成本单一真源链=matching_logic（费率字面量唯一位点）+cost_model_calibration（滑点/冲击标定，PROVENANCE=2026-07-24..09-16/5519 标的/1319 万五档快照）。
- 实盘/模拟侧：QMT 桥三通道（tick/下单/取价）+五档落库 tick_depth_5（`docs/_working/2026-09-08-qmt-bridge-migration-ledger.md:30,188,217`）；模拟账户 8886156677 全程 env='sim'（`e2e_integration/LEDGER.md` 置顶四禁）。
- 对照机制=sim_deviation_report（月度"模拟盘实跑 vs 同期回测"四项对照，AGREE_MIN=0.90/MISS_MAX=0.10/GAP_MAX=0.30，`scripts/backtest/sim_deviation_report.py`）。

### 8.2 已知缺陷/历史伤疤
- LEGACY 平面滑点 1bp 被实盘 52× 年化换手实测否证（低 3.8 倍）——**已修**（cost_model_calibration.py 治本）——防重复立案。
- 回测 tick 回放源切 CH（xtquant 9/18 断供）+1 档回放降级（五档深度待 tick_depth_5 积累）——已裁定已执行（同 ledger :213,274，ch_tick_replay.py）。

### 8.3 "全不全"审计
- **滑点偏差校准分母为零**：sim_trade_log 总量 66 行、切点（2025-09-09）前=0 行（PQ-0053）；execution_report 切点前零行（PQ-0139）——回测滑点假设 vs 实盘成交的校准闭环（REG-VALM-001 exec_quality 分桶 20/40bp）当前无一份合规样本。
- 五档深史边界：更早深史五档任何渠道不存在，回测五档精细撮合自切换日起才有数据（同 ledger :217）——诚实登记。
- algo_id 缺失→sim↔live divergence 无法按算法分解（`datagap_trade_record_requirement.md` §4 消费方4）——与 IBT-D02 同根。

### 8.4 "对不对"审计
- 落地器"快照外文件吸收"缺陷（k4 池化终批 q-0011/0f08f7a06c 以陈旧快照落地吞并 10+ 文件面，message 称 10 文件实 stat 28 文件）+队列丢件 bug（q-0003/0006/0007/0008 四袋无痕消失）——`e2e_integration/LEDGER.md` P0 落地事故+收官待办6——**未治本，P1 呈批中**；GPU 成绩单产物落库走同一通道，直接暴露。
- 02:30 夜跑带推进 hfq 表跨批微漂——纪律在无机械闸（IBT-H06）。
- 桥两缺口（客户端为 QMT 加密件 ZEPHYR_EXEC_V16 不可直改，Z 侧 #DONE vs 柜台零收录侦探对账）——等批（`e2e_integration/LEDGER.md` ③）。

### 8.5 自动吗
- 回测↔实盘对照=手工月度 CLI（sim_deviation_report），运行产物仓内未见（月报零命中）；桥对账=手工+拟议侦探件；五档/分钟 K 自拼=任务排程自动。

### 8.6 施工项
| 编号 | 项 | 优先级 |
|---|---|---|
| IBT-H01 | 滑点偏差校准管道（sim_trade_log/execution_report 积累+月度对照首跑） | P1 |
| IBT-H02 | 落地器快照对账 fail-closed（超集即回退）+队列丢件治本 | **P0**（GPU 产物落库通道） |
| IBT-H03 | Z 侧桥对账侦探件（#DONE vs 柜台收录矛盾→报警） | P2 |
| IBT-H04 | 02:30 夜跑带与长批互斥闸（跨批漂移机械化防范） | P2 |

---

## §9 历史案底台账（已修/已解——防重复立案）

| 案底 | 状态 | 凭证 |
|---|---|---|
| #326 C4 翻译件前视/幸存者污染（15+7 件） | 已修（批 B，edd503efb5e+c0f8763511） | batch_b_pit_repair_comparison.yaml |
| 成本门哑门（位置传参滑点不生效+bp0 关闸+缺册静默+换手缺键放行） | 已修（80880932d4+契约钉） | w3_w5_precheck_20260923.md §2.1 |
| N_eff 手填病（f06 DSR 分母盲信手填列） | 已修（verify_n_trials_provenance） | f06_e4_wfa_exam.py:245-459 |
| 平面滑点 1bp/AC 冲击零方差/地板佣金吞噬 | 已修（cost_model_calibration.py，车道 M） | 该文件头注 PROVENANCE |
| 净收益丢日期索引（net_returns.parquet） | 已修（q-0010） | e2e_integration/LEDGER.md 心跳 10:35 |
| ORPHAN 门 pathspec 误伤 | 已修（GT-ORPHAN-PATHSPEC-001） | e2e_integration/LEDGER.md 收官状态 |
| pf_alloc 三连 poison（tuple .get()） | 已修（2d6ae249f3） | 同上 |
| prereg 零消费方/SSOT 冲突 | 已解（裁定#413 冻结 v2+signoff 回填） | config/search_space_prereg.yaml:12-14 |
| E0 问闸 F06/grid 零接线 | 已接（cfe9b86f，终验 10/10） | 同上 |
| FACT 符号后缀不可成交（首版 IS/POSTD 作废） | 已修（runner 符号归一） | IBT-RUN-REPORT.md §5#1 |
| OOS 敏感性跨批漂移（首版） | 已修（同批六档重算纪律） | IBT-CAMPAIGN-LEDGER.md §3 03:02 |
| 回测 tick 回放 xtquant 断供 | 已修（ch_tick_replay.py 切 CH） | qmt-bridge-migration-ledger.md:274 |
| 多次考试假阳性（DSR N=1 判通过案底） | 防线已加严（RB-STATS-01+裁定#306） | ruling_registry.yaml:3795 + f06 头注 |
| 压测伤疤矩阵"C1-C10" | **仓内未见**以该名落盘的独立台账；最接近实体=regime_validation c1-c4 考尺族（src/zephyr/backtest/regime_validation/）+CONSTRUCTION_DISCIPLINE §6"压测 worker 50 曾三度压死宿主"+IBT-RUN-REPORT §5 缺陷记录 | 全仓 grep 伤疤仅命中 docs/_working/archive/2026-09/design_memos/10_regime_detector_spec.md:2420（expanding 窗危机伤疤） |

## §10 施工项汇总表（31 项开放+已修案底 14 条在 §9）

| 编号 | 环节 | 项 | 状态 | 优先级（GPU 成绩单可信度视角） |
|---|---|---|---|---|
| IBT-D01 | ④ | 考尺↔整装双引擎成本口径对照/统一 | OPEN | **P0-1** |
| IBT-F01 | ⑥ | 批 D 新鲜窗重考收口（fresh 名单+IBT-v2 v1.1+E1C-09） | OPEN | **P0-2** |
| IBT-B03/G02 | ②⑦ | 22 件尾件对账+抢救落库（N-16 裁定+蒸发对账） | OPEN | **P0-3** |
| IBT-H02 | ⑧ | 落地器快照对账 fail-closed+队列丢件治本 | OPEN | **P0-4** |
| IBT-B04 | ② | cost_qualified_list（17→3）落主区+池基登记 | OPEN | **P0-5** |
| IBT-A01 | ① | 板块坐标系裁定+881xxx 采补（五口径 469/596/90/499/727） | OPEN | P1 |
| IBT-B05 | ② | 六段温度两实现对齐（appendix_C 六步） | OPEN | P1 |
| IBT-B01 | ② | 批 B 残留：旧行标 suspect+C6 底座刷新（B-F4） | OPEN | P1 |
| IBT-A02 | ① | index_constituent 000010.SH 回补/改靶（B-F2） | OPEN | P1 |
| IBT-A03 | ① | 板块分钟 K 缺口回补+resampler 换表+真值源裁定 | OPEN | P1 |
| IBT-D02 | ④ | TradeRecord algo_id/order_type 归因字段（批 G） | OPEN | P1 |
| IBT-F02 | ⑥ | 窗口烧毁状态账本件 | OPEN | P1 |
| IBT-H01 | ⑧ | 滑点偏差校准管道+月度对照首跑 | OPEN | P1 |
| IBT-G01 | ⑦ | 成绩单上板桥 | OPEN | P1 |
| IBT-A04 | ① | regime run 锁定机械化 | OPEN | P2 |
| IBT-A05 | ① | kline_etf_daily 深史回补 | OPEN | P2 |
| IBT-A06 | ① | 因子落表面重建（factor_signal/feature_value） | OPEN | P2 |
| IBT-A07 | ① | 复权对齐抽检违例回查（PQ-0012/0131） | OPEN | P2 |
| IBT-B02 | ② | FACT IS 前段零贡献断言固化/深史评估 | OPEN | P2 |
| IBT-C01 | ③ | E8 装配层+权重矩阵+PP-001 配比 | OPEN | P2 |
| IBT-C02 | ③ | Σ<1 目标权重直通 | OPEN | P2 |
| IBT-C03 | ③ | G4 棘轮/做T 配对 | OPEN | P2 |
| IBT-C04 | ③ | 单票上限口径三查（PQ-0049） | OPEN | P2 |
| IBT-D03 | ④ | 指数腿实盘化 | OPEN | P2 |
| IBT-D04 | ④ | 极端行情执行压测矩阵 | OPEN | P2 |
| IBT-E01 | ⑤ | 治理级考试循环落地 | OPEN | P2 |
| IBT-E02 | ⑤ | E1C/LLM 轨 n_trial 接线实证 | OPEN | P2 |
| IBT-F03 | ⑥ | regime r4/r10 方向失真治本（丁线） | OPEN | P2 |
| IBT-G03 | ⑦ | 健康探针常驻化+回测节点出题 | OPEN | P2 |
| IBT-G04 | ⑦ | account_nav_daily 0 行修复 | OPEN | P2 |
| IBT-H03 | ⑧ | Z 侧桥对账侦探件 | OPEN | P2 |
| IBT-H04 | ⑧ | 夜跑带互斥闸 | OPEN | P2 |

### 优先级排序说明（按"影响周末 GPU 成绩单可信度"）
1. **IBT-D01**：成绩单每格数字产自考尺引擎平面成本（5bp），与首跑五册的标定滑点口径不同构——不解释清楚，成绩单与历史数字不可比。
2. **IBT-F01**：GPU 搜索接的池基=污染修复后的新名单——该名单（批 D）仓内未见，现网跑的是旧族谱系，成绩单结论的"池"不成立。
3. **IBT-B03/G02**：首跑逐笔审计链（nav/trades csv）主区已不见+HEAD 无——蒸发案频发环境下，成绩单的对照基线审计链面临归零。
4. **IBT-H02**：GPU 产物落库走同一落地器/队列通道，吞并+丢件两缺陷未治本——成绩单可能落不进 HEAD 或落错。
5. **IBT-B04**：成本合格名单（17→3，照妖镜实测）只在 worktree——不落主区，成绩单的"合格池"口径无真源可查。

—— 整装回测审计班 2026-09-24（只读取证，未做任何 git 写操作）
