---
ttl: task_bound
title: 本班对矿考二班/统筹的接口对齐单（判官扩键·第 4 张事件卡·面板通道消费侧）
created: "2026-10-13"
sid: st-examunlock-20261013
family_id: EXAMUNLOCK-20261013
---

# 一、判官扩键（令卡 P1d）＝矿考二班在飞袋已含，本班不重画

实测（非读台账转述）：队列在途袋 `q-20261013-st-mineloop2-20261012-0014`（00:13:56 入队，
base=91644e826f=当时 HEAD）files 面含 `scripts/backtest/fexam/calibration_exam.py`＋
`card_binding.py`＋三支测试，袋文自书"裁定③：三柱机器面落判官件＋臂上下文注入位＋11 支判别力钉"。
⇒ 该项**已在他们域内执行**，本班动作＝零施工＋把本班核到的工作量分母交回：

| 判据键（卡面散文名） | 现机器面 | 本班实测位 |
|---|---|---|
| `ic_floor__ic_ir` | 数值键 `ic_ir_min` 在册且有面（面板路 `st.get("icir")` 已修，钉在 `tests/backtest/test_calibration_exam.py`）；**series 路仍置 None** | 考试班 cd934a5e01 那针；series 路缺口＝`calibration_exam` 内 `ic_ir: None` 一处 |
| `lag_profile` | 查无（零计算面：全仓无 半衰期/half_life/t+1..t+5 |IC| 峰值实现） | 需新建，非"补一行" |
| `head_to_head` | 部分面：双臂 `_comparison_metrics` 已产 `ic_delta_is/ic_delta_oos` 且有判据腿，但**卡面要求的"去掉母卡信号后的净 IC／共线性／联立回归"查无** | 需 `signal_b` 接线＋正交回归面 |

配对 IC 样本面＝同一 `signal_b` 通道的副产品，不另立件。
07 卡重考走 only-append：分数册现 46 行 32 卡全 fail（本班 00:1x 实测再取），追加行不动旧行。

# 二、第 4 张 A 类事件卡开考（令卡 P1e）＝前提被证伪，本班不硬跑

令卡说"矿考二班现成通道，协调跑掉"。实测该卡的卡面自述否决了"现成"二字：
`entry_flow/L2/TDM-E-L2-09__calibration__06_催化剂密度过热事件开关.yaml:60`
`blocked_reason: 缺基序列算子：催化剂密度（行业×日研报发布量）在 card_binding 算子册内无实现
（本班未建，属 T3 实现面/WO 接线）；…禁以近似密度序列冒代`。

- 现成通道（`op_event_flag_rolling_pctile` 的 `base_op`/`base_csv` 二选一）**装不下它**：
  底座"行业×日研报发布量密度"需要按 industry 分组的两级聚合，在册 `SQL_DAILY_AGG` 无 industry 维，
  且该模板**无 anyLast 逐日去重**（`research_report` 按 (symbol,publish_date,report_id) 一日多行，
  直方聚合＝把多版本当唯一行，触在册 30 倍放大铁律）。
- 本班不新建算子：`card_binding.py` 正被矿考二班在途袋改（撞件＝昨晚三方真冲突形态），
  且算子册属他们声明的 T3 实现面。
- 交回统筹的可执行选择（本班不自决）：
  甲＝他们按 `blocked_reason` 落 `industry_report_density` 算子＋配对测试，本班出判定与分母；
  乙＝该卡底座改由**已入库 CSV**承担（若有人先物化"行业级日研报密度"序列，本班可零算子开考）；
  丙＝判该卡继续 blocked_on_impl（与 挖矿二班聚合 8 卡同态），不计入本班考面。

# 三、面板/横截面通道的消费侧准备（本班已备齐的输入，不代建通道）

令卡明确"面板形 17 张的前置在矿考二班域，本班只做消费侧准备"。本班准备物＝两份机生册：

1. `04_target_face_channel_census.yaml`：preregistered 177 张里 118 张堵在
   `target_face_not_index_next_day`，**按卡面 primary 原文归一后需 94 条不同目标腿，其中 91 条只 1 张卡**，
   前 10 条腿覆盖 34 张；16 张属双臂形。
   ⇒ 对考试班 §25.9"打通目标面通道一项＝解开 119/178＝67%"的**口径更正**：
   119 是"被这张尺判为堵"的计数，不是"建一条通道即解 119"。真实形状＝至少 4 类通道
   （个股开盘可成交 T+1→T+2 族 14 张／成本调整 Sharpe 族 11 张／NAV-双臂族 16 张／多日 horizon 族）
   ＋ 91 条单例腿的长尾。立项分母请用本件，别按 119 估工作量。
2. `05_recipe_book_grain_verdicts.yaml`：11 张 A? 卡逐张机判"能不能如实进配方册"，
   结果 **11/11 不同型**（横截面形／聚合口径与 anyLast 不同型／序列未冻结到一列）。
   ⇒ 令卡"9 张单表入配方册"不可如实落地；本班已按在册纪律**零登记**，并逐表写清正确通道
   （三件 sector 形算子先例已在册，走绑定册 args 携表名，本就不依赖 `_REGISTERED_TABLES`）。

# 四、horizon 阶梯 v3+（令卡 P2c）＝挖矿二班已冻结同族，本班不另立

实测在册件：挖矿二班收班把"聚合 8 卡（`TDM-E-L1-S2/calibration/40..47`，
lu_count/lu_ratio/avg_abs_ret × level/z20 × fwd5/fwd10）"整族立为 `blocked_on_impl`，
判据理由与本令卡 P2c 同一条：执行器 `_series_metrics` 只有 `shift(-1)` 次日面。
⇒ 本班**不再产第二套 horizon 卡**（同域重复簇＝违根宪法 §4.2）。本班交回的分母＝
`04` 号件 `horizon_ladder` 段：preregistered 面里带 horizon 词的 31 张
（next5d 17／next_5d 6／next_3d 3／next_10d 3／next_20d 2），
其中已因多日目标被拦的具体样例 reason=`executor_horizon_mismatch` 在册命中 1 张。
另：令卡"按族计试次"在册**查无立法**（`trial_ledger_registry.yaml` 无族级字段，
只有 `…meta-method-research.md:199` 的提案句）⇒ 本班不自造族计数口径，列为呈批件。

# 五、本班与在途袋的撞件自查（三方真冲突规避，按 10-12 夜教训执行）

- 本班**不改** `card_binding.py`／`calibration_exam.py`／`mineloop_campaign/02_binding_book.yaml`
  ／任何他班属主册；本班自有绑定册另起 `03_binding_book_event20.yaml`。
- 本班袋内**不带** `capability_canonical_file_registry.yaml` 与 `module_translation_registry.yaml`
  的 render 字节（在册禁令：整册 render 随袋＝他人登记混进我的 commit＝归属篡改）；
  token 与大白话登记一律走意图 API 单口，PG 侧在册即为准。
- 同会话同件不跨袋重复：20 卡状态翻转、序列 CSV、分数册追加只在"落地批"出现一次。
