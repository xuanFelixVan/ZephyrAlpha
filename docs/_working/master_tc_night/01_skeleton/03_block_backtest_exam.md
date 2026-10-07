---
created: "2026-10-07"
ttl: task_bound
title: "总包夜战 W1·业务块子册：回测考试（18 环节×子模块×上下游×本夜卡）"
session: st-mastertc-mine
---

# 0x_block：回测考试（B 段考试半段(F23-F28，边界=F22|F23 即 strategy_production_map 的 E3→E4 咽喉)+G 段(F64-F71)+H 段模拟转正(F72-F75)）

> 环节行/职责/上下游/模块锚点全部复用 `docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`（F01-F122）与 `docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md`（F123-F132 定版新增）；状态轴复用 `docs/_working/night_sweep_20260929/00_skeleton_nightsweep.md`。本册只做块视图组装+本夜卡挂接，不重挖、不改真源。

## 一、环节清单（18 环节）

| 环节 | 名称 | 段 | 状态轴 | 基态 | 上游（谁供料）| 下游（谁消费）| 核心模块锚点 | 本夜卡 |
|---|---|---|---|---|---|---|---|---|
| F023 | E4 考试咽喉 | B | 已通 | built | F22 | F24 | MOD-BT-039；c1_backtest.strategy_screen | C33(L7)、C34(L7)、C216(L7)、C236(L7)、C239(L7)、C288(L7) |
| F024 | E5 协同去重 | B | 已通 | built | F23 | F25 | MOD-BT-086 | — |
| F025 | E6 入库监控 | B | 开口 | built | F24 | F26/F14 反馈 | MOD-BT-078；data/backtest_artifacts/runs/ | — |
| F026 | E7 模拟盘前哨 | B | 开口 | missing | F25 | F27/F72 | strategy_production_map FAC-E7：module_ref=null | — |
| F027 | E8 组装与资金分配 | B | 开口 | partial | F26 | F74/F48 | MOD-PA-002..024（MOD-PA-003/007/022/013/004/014/015） | — |
| F028 | E9 实盘归因 | B | 开口 | partial | 实盘账本 | F50/F21 | MOD-PF-007 | — |
| F064 | 回测三件套 | G | 已通 | built | REG 三册 | F65/F66 | docs/01.../catalogs/universe、benchmark、cost_model_registry.yaml | C199(L7) |
| F065 | 回测引擎族 | G | 已通 | built | F06/F64 | F66 | src/zephyr/backtest/core/matching_engine.py、ch_tick_replay.py | — |
| F066 | 回测预注册与七步循环 | G | 已通 | built | F64 | F25/F67 | scripts/backtest/generate_backtest_backlog.py；sop_a/sop_b（backtest_system_sop） | C237(L7) |
| F067 | 实验登记与档案 | G | 已通 | built | F66 | F50 | docs/01.../catalogs/experiment_registry.yaml | — |
| F068 | GPU 矩阵/工厂格子 | G | 已通 | built | F13 | F66 | src/zephyr/trading/gpu_consensus_scheduler.py；scripts/backtest/factory_grid_exec | C238(L7)、C70(L7) |
| F069 | T0/成本门/IBT | G | 已通 | built | F64 | F66 | src/zephyr/backtest/regime_validation/exam_cost_gate.py | — |
| F070 | 模拟撮合与偏差检测 | G | 已通 | built | F65 | F72 | src/zephyr/simulation/（look_ahead_bias_detector.py、overfitting_protection_gate.p | — |
| F071 | AutoRuntime Core | G | 已通 | built | 全链 | 全链 | `python -m zephyr.trading`→src/zephyr/trading/auto_runtime_core.py | C21(L10) |
| F072 | 模拟盘日跑四件 | H | 开口 | partial | F25/F70 | F73/F74 | src/zephyr/ex_core/live_strategy_adapter.py；sch_paper_session、sch_sim_bridge_exe | — |
| F073 | A/B 联赛与分仓 | H | 开口 | design | F72 | F74 | automation 骨架 §7；sop/backtest_system_sop/exam_policy.md | — |
| F074 | 转正建议书汇总器 | H | 开口 | missing | F72/F73 | Owner 门位→实盘 | automation 骨架 §4 P0 工单；strategy_pipeline/promotion_advisory.py | — |
| F075 | 策略生命周期状态机 | H | 开口 | partial | F23-F27 | REG-STR-001 | src/zephyr/strategy_pipeline/lifecycle_fsm.py、intake.py、registry_writer.py、scree | C84(L8) |

## 二、块内数据流与上下游（谁喂谁、谁消费谁——真源 DAG 摘录）

### B 段·策略供给链＝策略工厂（F023-F028）

- **F023 E4 考试咽喉**：全厂唯一判定权：IS 冻结窗→DSR→OOS 双窗及格线。上游=F22；下游=F24。本夜卡：C33、C34、C216、C236、C239、C288
- **F024 E5 协同去重**：对称正交化后增量 IC 显著才准入（禁朴素等权）。上游=F23；下游=F25。本夜无卡
- **F025 E6 入库监控**：台账只增+判死行追加；oos_years_decay≥0.5 判存疑。上游=F24；下游=F26/F14 反馈。本夜无卡（开口，见总表 §五建议）
- **F026 E7 模拟盘前哨**：registry 幸存者 live 数据跑模拟盘 N 周逐日对账。上游=F25；下游=F27/F72。本夜无卡（开口，见总表 §五建议）
- **F027 E8 组装与资金分配**：多策略 sleeve 装配+regime 元分配+风险平价+渐进爬坡。上游=F26；下游=F74/F48。本夜无卡（开口，见总表 §五建议）
- **F028 E9 实盘归因**：影子组合对照+IS 分解+Brinson-Fachler+因子归因，回灌 E2。上游=实盘账本；下游=F50/F21。本夜无卡（开口，见总表 §五建议）

### G 段·回测模拟链（F064-F071）

- **F064 回测三件套**：universe 7/benchmark 9/cost_model 6 每测 MUST 指定。上游=REG 三册；下游=F65/F66。本夜卡：C199
- **F065 回测引擎族**：事件驱动引擎+CH tick replay+撮合+组合核算。上游=F06/F64；下游=F66。本夜无卡
- **F066 回测预注册与七步循环**：backtest_backlog 137 对象跑前写死阈值；无注册不归档。上游=F64；下游=F25/F67。本夜卡：C237
- **F067 实验登记与档案**：experiment_registry 11 条 FallbackBackend+Panel 实验 Tab。上游=F66；下游=F50。本夜无卡
- **F068 GPU 矩阵/工厂格子**：35.33s/格×4640 格重排+gpu_consensus/gpu_monitor。上游=F13；下游=F66。本夜卡：C238、C70
- **F069 T0/成本门/IBT**：T0 成本模型+考试成本双口径门+复权降级。上游=F64；下游=F66。本夜无卡
- **F070 模拟撮合与偏差检测**：涨板队列/前视偏差检测/过拟合保护门/DSR。上游=F65；下游=F72。本夜无卡
- **F071 AutoRuntime Core**：三层运行时运营中心（系统大脑）：三层路由/节律调度/work DAG。上游=全链；下游=全链。本夜卡：C21

### H 段·模拟盘→转正链（F072-F075）

- **F072 模拟盘日跑四件**：PaperSession 日跑/平台四件/对账验证（行业实证回测夸大实盘 30-60%，此门不可跳）。上游=F25/F70；下游=F73/F74。本夜无卡（开口，见总表 §五建议）
- **F073 A/B 联赛与分仓**：champion-challenger 守擂/踢馆+等风险预算分仓+ρ>0.7 相关性闸。上游=F72；下游=F74。本夜无卡（开口，见总表 §五建议）
- **F074 转正建议书汇总器**：四件产出→一页报告+组合门打分=**全链唯一人工门**。上游=F72/F73；下游=Owner 门位→实盘。本夜无卡（开口，见总表 §五建议）
- **F075 策略生命周期状态机**：lifecycle FSM/上架入库/晋升建议/事件流。上游=F23-F27；下游=REG-STR-001。本夜卡：C84

## 三、本夜涉及卡（12 张，去重按主挂接）

| 卡号 | 车道 | 自审闸预判 | 卡面摘要（canonical）| night_sweep 机判交叉 |
|---|---|---|---|---|
| C33 | L7 | **GREEN** | 139 新题（PQ-0284~0422）首考——status=registered 0 条开考，exam_loop 复考机器已落地 | — |
| C34 | L7 | **GREEN** | 旧 283 题全量复考（册面守恒 pass152/fail45/insufficient86；09-25 04:20 后复考活动为零；基建 fail 口径 12-16 有出入以 PG 册面为准） | — |
| C216 | L7 | **GREEN** | 16 例测试红（reexam 族 9/closed-book 族 6/t0_family 收集错） | — |
| C236 | L7 | **GREEN** | 波10 G-C.4 lead-lag统计验证器（P2观察轨） | — |
| C239 | L7 | **GREEN** | 波10 G-D.3多重检验与滚动重考（StepM/SPA+分半窗） | — |
| C288 | L7 | **GREEN** | C2晋级率缺陷（2027-03前修完即可） | — |
| C199 | L7 | **GREEN** | 文件群7 材料线+预检报告 5 件（scripts/backtest 等） | — |
| C237 | L7 | **GREEN** | 波10 G-D.1新预注册族 chart_resonance_prereg.yaml | — |
| C238 | L7 | **GREEN** | 波10 G-D.2逐格统计引擎（样本/夏普/c*/DSR 四件套） | — |
| C70 | L7 | **GREEN** | T2 发车 900 格终审——机件就绪（t1_t2_handover 已重构），卡裁1/⚑-2 口径一个字母；Owner 追认后即可发车 | — |
| C21 | L10 | **GREEN** | AutoRuntime 常驻化窗口（维持手动=默认，启用须 Owner） | — |
| C84 | L8 | **GREEN** | FSM 词表最后一公里——to_registry_lifecycle_state 全仓零消费、promotion_advisory:596 仍裸写 production、strategy_regist | — |

## 四、处方指针（复用既有工单，不新开处方）

- 挖矿处方卷=docs/_working/fullconnect_campaign/ 各域 per-F 卷（总表夜战骨架处方指针列）；施工序列=docs/_working/fullconnect_campaign/00_workorders.md（S1-S5+§四下一战役）；分诊六态=docs/_working/final_delivery_campaign/workorders_{governance,commit_clean,data_exam_factory,docs_misc}.md。
- 本块开口环节中已有工单无卡者（如 F115'R1-R3 最薄一刀'）按总表 §五建议补卡挂接，工单不重写。
- Owner 门位卡（等Owner 状态轴/§五 保留）本夜只登记不施工；清单见总表 §四 WAIT 行。

## 五、复核命令

```bash
# 本块环节数与总表 §三 行一致；卡数与总表 §四 该块行数一致（主挂接口径）
grep -c '^| F' docs/_working/master_tc_night/01_skeleton/03_block_backtest_exam.md
```
