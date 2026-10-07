---
created: "2026-10-07"
ttl: task_bound
title: "总包夜战 W1·业务块子册：信号策略（16 环节×子模块×上下游×本夜卡）"
session: st-mastertc-mine
---

# 0x_block：信号策略（B 段进货构造半段(F13-F22,F29)+F96 胃+F129/F130 模型线+F120/F121 设计面）

> 环节行/职责/上下游/模块锚点全部复用 `docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`（F01-F122）与 `docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md`（F123-F132 定版新增）；状态轴复用 `docs/_working/night_sweep_20260929/00_skeleton_nightsweep.md`。本册只做块视图组装+本夜卡挂接，不重挖、不改真源。

## 一、环节清单（16 环节）

| 环节 | 名称 | 段 | 状态轴 | 基态 | 上游（谁供料）| 下游（谁消费）| 核心模块锚点 | 本夜卡 |
|---|---|---|---|---|---|---|---|---|
| F013 | E0 算力调度心跳 | B | 开口 | partial | 日历/数据到达 | 全工厂重任务 | MOD-BT-151（拉式闸门）；strategy_production_map FAC-E0 | — |
| F014 | E1 想法进货编排 | B | 开口 | partial | F15-F20 | F21 | MOD-BT-154（factory_intake_pipeline）；FAC-E1 | — |
| F015 | 车道A·社区货源 | B | 已通 | built | 社区源 | F14 | MOD-BT-035；data/strategy_intake/normalized/ | — |
| F016 | 车道B·AI 生成 | B | 开口 | partial | 本地/LLM | F14 | MOD-BT-150；lane_b_candidates.csv | — |
| F017 | 车道C·公式挖掘机 | B | 开口 | partial | F21 过审假说反哺种子 | F14 | MOD-BT-155+158；config/factor_mining_whitelist.yaml | C232(L6)、C234(L6)、C235(L6)、C252(L6)、C233(L7) |
| F018 | 车道D·产业链三高 | B | 开口 | partial | F12 图谱 | F14 | MOD-BT-090；three_high_candidates.csv | — |
| F019 | 车道E·模型基线 | B | 开口 | partial | 行情库 | F14/F22 | MOD-BT-084+194+195（kronos_adapter 登记跳过） | — |
| F020 | 车道G·全网搜索进货 | B | 开口 | partial | F96 胃 | F14 | MOD-AUTO-E1G-001；lane_g_stomach_intake.py；lane_g_candidates.csv | — |
| F021 | E2 假说预审逻辑门 | B | 开口 | partial | F14（及 F28/F50 回灌） | F22 | MOD-BT-091；c1_backtest.hypothesis_precheck | — |
| F022 | E3 构造与翻译 | B | 开口 | partial | F21 | F23 | MOD-BT-041..075+159+190；scripts/backtest/translated/ | C253(L6) |
| F029 | 工厂进货台账与出生证 | B | 开口 | partial | F14-F22 | 全工厂 | data/strategy_intake/*；scripts/backtest/factory_intake_pipeline.py | — |
| F096 | 胃·全网搜索消化设备 | J | 开口 | partial | F31 | F20/F02 | docs/_working/automation/inbox/；automation 骨架 §4 P1"搜索设备 v0" | — |
| F120 | 业务层四轴+底板骨架 | M | 开口 | design | — | F72-F75/F73 | docs/_working/automation/20260917_fullauto_skeleton_v1.md+20260917_decision_skel | C106(L6) |
| F121 | 研究性三域+研究域 | M | 等Owner | design | — | 待裁 | src/zephyr/{digital_twin,cross_asset,execution_simulation,research}/ | — |
| F129 | ml_train 训练线(43 py) | 新环 | 开口 | new(定版新增) | — | — | 处方卷=11_f129_ml_train_line.md | — |
| F130 | ml_serve 数值推理线(11 py) | 新环 | 开口 | new(定版新增) | — | — | 处方卷=13_f130_ml_serve_adapters.md | — |

## 二、块内数据流与上下游（谁喂谁、谁消费谁——真源 DAG 摘录）

### B 段·策略供给链＝策略工厂（F013-F029）

- **F013 E0 算力调度心跳**：重算力任务问闸（交易日历+收盘缓冲，四枚理由码）。上游=日历/数据到达；下游=全工厂重任务。本夜无卡（开口，见总表 §五建议）
- **F014 E1 想法进货编排**：六车道并发进货薄编排→统一卸 strategy_intake 台账带出生证。上游=F15-F20；下游=F21。本夜无卡（开口，见总表 §五建议）
- **F015 车道A·社区货源**：聚宽/掘金社区策略爬取入库（C1 已收 597 条）。上游=社区源；下游=F14。本夜无卡
- **F016 车道B·AI 生成**：自然语言→策略假说量产（生成件必须走 E3 验收集）。上游=本地/LLM；下游=F14。本夜无卡（开口，见总表 §五建议）
- **F017 车道C·公式挖掘机**：gplearn 轨 MVP+智能体轨 MVP（DSL→增量 IC 三道验收）。上游=F21 过审假说反哺种子；下游=F14。本夜卡：C232、C234、C235、C252、C233
- **F018 车道D·产业链三高**：BOM 拆解三高筛选（四支柱 z 分合成）带出生证。上游=F12 图谱；下游=F14。本夜无卡（开口，见总表 §五建议）
- **F019 车道E·模型基线**：分位数回归/Kronos 分布预测只当基线对台。上游=行情库；下游=F14/F22。本夜无卡（开口，见总表 §五建议）
- **F020 车道G·全网搜索进货**：消化胃收件箱→本地 LLM 抽 0-2 条可检验假说/篇。上游=F96 胃；下游=F14。本夜无卡（开口，见总表 §五建议）
- **F021 E2 假说预审逻辑门**：经济学讲不通的想法在此死，不花回测算力。上游=F14（及 F28/F50 回灌）；下游=F22。本夜无卡（开口，见总表 §五建议）
- **F022 E3 构造与翻译**：外来策略→标准件（C3 翻译/公式轨桥/假说轨翻译 MVP）。上游=F21；下游=F23。本夜卡：C253
- **F029 工厂进货台账与出生证**：候选想法/翻译件/考卷件的 manifest 台账族。上游=F14-F22；下游=全工厂。本夜无卡（开口，见总表 §五建议）

### J 段·AI 层链（F096）

- **F096 胃·全网搜索消化设备**：搜索→清洗→情报 inbox（intel-*.md）→供 F20 点菜。上游=F31；下游=F20/F02。本夜无卡（开口，见总表 §五建议）

### M 段·全局横切段（F120-F121）

- **F120 业务层四轴+底板骨架**：决策权/时间节拍/产线工段 8+1/生命周期四轴+标准库红线库底板（骨架封顶声明在案）。上游=—；下游=F72-F75/F73。本夜卡：C106
- **F121 研究性三域+研究域**：数字孪生/跨资产/执行仿真（设计态）+research 事件研究。上游=—；下游=待裁。本夜无卡

## 三、本夜涉及卡（7 张，去重按主挂接）

| 卡号 | 车道 | 自审闸预判 | 卡面摘要（canonical）| night_sweep 机判交叉 |
|---|---|---|---|---|
| C232 | L6 | **GREEN** | 波10 G-B.3A股特有事件轴显式化（封板/炸板/busted/缠论） | — |
| C234 | L6 | **GREEN** | 波10 G-C.2摆动结构序列（LH/HL双峰检测） | — |
| C235 | L6 | **GREEN** | 波10 G-C.3共振条件对定义器（15M上沿×1M双峰） | 17 |
| C252 | L6 | **GREEN** | dossier_github建议采纳汇总（trendln/pytrendline/merge_asof/vectorbt/不引pandas-ta） | 1、13、16、21 |
| C233 | L7 | **GREEN** | 波10 G-C.1跨周期数据层（merge_asof backward PIT） | — |
| C253 | L6 | **GREEN** | dossier_institution建议采纳汇总（接线优先/TradingView枢轴口径/镜像测试三纪律） | 1、14、21 |
| C106 | L6 | **GREEN** | 全流通缺口定档 122→132（红队打假后诚实读数：122 中 44 无簿） | — |

## 四、处方指针（复用既有工单，不新开处方）

- 挖矿处方卷=docs/_working/fullconnect_campaign/ 各域 per-F 卷（总表夜战骨架处方指针列）；施工序列=docs/_working/fullconnect_campaign/00_workorders.md（S1-S5+§四下一战役）；分诊六态=docs/_working/final_delivery_campaign/workorders_{governance,commit_clean,data_exam_factory,docs_misc}.md。
- 本块开口环节中已有工单无卡者（如 F115'R1-R3 最薄一刀'）按总表 §五建议补卡挂接，工单不重写。
- Owner 门位卡（等Owner 状态轴/§五 保留）本夜只登记不施工；清单见总表 §四 WAIT 行。

## 五、复核命令

```bash
# 本块环节数与总表 §三 行一致；卡数与总表 §四 该块行数一致（主挂接口径）
grep -c '^| F' docs/_working/master_tc_night/01_skeleton/02_block_signal_strategy.md
```
