---
ttl: task_bound
title: 矿考循环班第一轮滚动终报（st-mineloop-20261010，2026-10-10 夜）
created: "2026-10-10"
sid: st-mineloop-20261010
family_id: MINELOOP-CAMPAIGN
---

# 第一轮滚动终报（班时 20:50 起，本报告 23:1x 落）

## 一、四条验收指标实测（令卡 §四）

| 指标 | 实测值 | 凭据 |
|---|---|---|
| 新卡数 | **31 张**（preregistered 14／blocked_on_data 9／blocked_on_impl 8） | `04_newcard_validation.yaml`（总包尺机生）＋5 份车道台账 |
| 出分数 | **7 张**（分数册 18→25 行，only-add 零改旧行） | `exam_scores_v1.yaml`＋`03/05/06/07_exam_run_r*.yaml` |
| FAIL 率 | **7/7＝100%**（全负结果如实入册，无一例改判） | 同上；ic/mono/oos 读数逐行在册 |
| 复挖命中率 | **8/8 前役"封矿"节点全部推翻**（另 L2-09-1 理由推翻、结论维持） | L11/L12/L13 台账逐节点六向行 |
| 数据面阻塞 | 见 §四清单（emotion close_final=0／pre_open=27 行／TI 周月陈旧至 09-15／… ） | `grain_probe3.yaml` 实测 |

**未达令卡"每轮 ≥15 张出分"**，且这不是执行问题而是结构问题——§三给了实测分母和解锁价码。

## 二、本轮真正交付的东西：绑定层与它量出的结构性缺口

`scripts/backtest/fexam/card_binding.py`（MOD-BT-248）补齐 `calibration_exam.run_card` 明示的缺位面——
卡面 `data_binding` 段此前**全仓零代码消费**（`grep -rln data_binding --include=*.py` 零命中，
capability_lookup 四关键词 0/4 命中留审计）。三层防误绑设计：

1. **算子册每条逐字引用卡面原文**，运行器机械校验引句必须存在于该卡 `data_binding`，找不到即拒绑；
2. **反挪门柱自闸**：出分前后对判据四键（window/buckets/pillars/pillars_numeric/target/hypothesis）
   做内容级断言，被改动即 `BindingIntegrityError` 整卡中止、分数册不动；
3. **CH 让路钟闸**：21:00–22:30 与 01:00–04:00 默认拒绝取数，须 `--override-ch-window-with-reason` 显式留痕。

绑定普查实测分母（193 张 prereg，含本班新卡）：

| 类 | 张数 | 含义 |
|---|---|---|
| C 需重放引擎/非次日指数目标 | **121** | engine_replay 63／other 27／panel_stock 22／sector_series 3／probability_hit 3／未标 3 |
| U 无 data_binding 或多表未定复合配方 | 31 | 接线未冻结，禁考 |
| B panel 宽表（去重/撮合口径须逐表面核） | 17 | 后置 |
| A? 表未在配方册 | 15 | 其中 9 张同一板块族底座可批量解锁 |
| A／D 现成可绑 | **0** | — |

⇒ **"待考积压 174 张"里真正"差一根线就能考"的是一张都没有**；差的是 63 张要重放引擎、
22 张要个股面板机器、17 张要板块族底座。我本轮把板块族底座（`load_sector_family_panel`）立起来了，
同族还有 8 张卡可复用同一取数面。

## 三、下一轮目标重定（给 Owner 的一句话）

≥15 张/轮若指"如实出分"，需要的是**一条 op 车道专做板块族 9 张**＋**重放引擎工单（63 张的门）**；
按本轮实测，每张 bespoke 算子含粒度实测+引句校验约 20–30 分钟，纯 CPU 面不可能既快又真。

7 张出分的诚实读数（两条对"要不要挪门柱"很关键）：

- 过 `ic_mean≥0.02` 地板但未过 `mono_spearman≥0.6`：**地量档位开关**（ic=0.0465／mono=0.467／oos=+0.112）、
  **宏观剪刀差**（ic=0.0139 近线／mono=0.624 已过／oos=+0.106）——属"响应曲线不单调"，不是"无信号"；
- 其余 5 张 ic 与 mono 双未过（两融 5 日环比 ic=-0.035、下行半偏差 ic=-0.002、虹吸集中度、
  调整周期进度、快讯情感日均值）。
- 挪门柱=作废（G4-5），要重考须另立新卡并计新试次。

## 四、数据面阻塞清单（本班实测，非引用账面）

| 面 | 实测 | 影响的卡 |
|---|---|---|
| `c1_market.emotion_index` stage | close_final 8,617 行但**止于 2026-09-30**；pre_open **仅 27 行**（09-01..10-09）；auction 17 行 | T4M 情绪先锋四态卡面：L15 卡 03（pre_open）已由我改判 blocked_on_data（判据四键零动，仅 status+取证）；卡 04（close_final）解锁判据已写死 |
| `c3_fundamental.news_sentiment_score` | 7,947,739 行/6,021 日/caliber_version 单值；2024=733,384 行 vs 2025=17,011 行＝**密度断崖但逐日覆盖未断**（OOS 601 交易日有数） | A09 快讯情感卡可考，已在绑定册声明抽样噪声残余 |
| `technical_indicator` weekly/monthly | max=2026-09-15（比 daily 陈旧 2 周） | TI 族卡维持 blocked_on_data |
| `kline_sector_880` period='1d' | 785,204 行/729 codes/2020-03-17..2026-10-08；族映射 industry_l1=61∪industry_ths=128 | 板块族 9 张卡的底座（已实装 2 张） |
| QMT 终端 | 未复元（本班无可证伪信号，情绪 close_final 仍 0） | T4 触发清单见 L15 台账回报 |

## 五、两处令卡前提被实测更正（不是抱怨，是账）

1. **令卡"GPU 明早 08:00 v2 首窗"已过时**：examchief 19:30 Owner 加速令把首窗提前，
   实测任务 `ZephyrAlpha_F06Grid` NextRunTime=当晚 21:00；21:00 点火、**21:29:02 收卷三判全过=PASS**
   （dev `c69a4a6948`/`cdec731bf9`），任务现 Disabled。我据其"CH 让路通知（点名矿考班 21:00–22:30）"
   先守窗、后以双证（任务 Disabled＋CH 探针 0.06s 空载）留痕放行，未静默绕闸。
2. **令卡"卡册 454"账面落后实测**：HEAD 现值 456（骨架 186／名卡 270），
   已考 18 行、待考 prereg 174 张与账面一致。

## 六、呈批与移交清单（不自拍）

| # | 事项 | 为何要 Owner/总控 |
|---|---|---|
| P1 | 3 张新卡门柱键在 `_COMPARISON_KNOWN_KEYS` 词表外（`classification_confusion_min` 等 4 键／`downside_5d_min`／`arm_monotone_ok`），执行器无机判面 | 扩词表＝改判据面口径，须立法；我已按在册词表判、未代改车道件 |
| P2 | `apply_depgraph.py --add-design-node ... --dry-run` **实际写入了 PG**（node_id=16575808 先于实跑存在） | "dry-run 零写"契约被破，属工具病根，归治理面 |
| P3 | MOD-BT-248 的 blueprint 面：`--add-design-node` 报 `docs/03_modules/MOD-BT-248/blueprint.md` 不存在并标 missing | 蓝图挂接＝depgraph 权威面，须总控口径 |
| P4 | 试次账本内可见 `batch_id: examcard:TDM-E-TEST/*` 形态行（测试卡 id） | 若确证由单元跑写入生产册＝测试隔离缺口；**我未钉死写入者**，须复核后再定性 |
| P5 | 主区被工具写的面（`module_translation_registry.yaml` +8/−0、`trial_ledger_registry.yaml` 我的 7 批次） | 落地面归属须按 sid 复核，我带的是纯增件 |
| P6 | 业务资产判死类零项（本轮未产生需 Owner 门位的动作） | — |

## 七、车道与队列账

- 车道：L11／L12／L13（复挖）＋L14／L15（深挖）全部交车，合计 5 道 31 卡；
  每道独占台账文件、零跨道写、零 git、让路窗内零 CH（自报已核：文件 mtime 与卡面 `preregistered_by` 对账）。
- 队列 4 袋：`q-...-0001` token 先行袋**已落 dev**（+200/−0 纯增，HEAD 投影在册 40 条）；
  绑定层本体袋／出分袋／新卡袋在队（按域拆三袋，队列不吃跨域旗）。
- 并发避让：主区 616 脏件、14 条在飞工棚，本班全程只写自己工棚＋工具侧纯增册面。
