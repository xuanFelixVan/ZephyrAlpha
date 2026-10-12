---
ttl: task_bound
title: 分工与本班 09 号件更正（通宵总令 §二交叉验证＋§工法令"先挖后干"产物）
created: "2026-10-13"
sid: st-examunlock-20261013
family_id: EXAMUNLOCK-20261013
---

# 一、本班 09 号件的一处自纠（另起留旧文，不改写已投件）

09 号件 §三 写"本族每张卡需要第二物化面，现无"——**这条被本班 03:0x 现读在册代码证伪**：

`scripts/backtest/fexam/card_binding.py:128-147` 的 `SQL_LIMIT_UP_PANEL` **同一次查询里已经算出两腿**：

- `ret_open = o / lag_c - 1` ＝ 开盘对昨收 ＝ **隔夜腿**（与 `event_score.py:282 overnight_return_jump(open_next, close_event)` 同式）；
- `ret_close = c / lag_c - 1` ＝ 全日腿；
- 日内腿可由二者派生：`(1+ret_close)/(1+ret_open) - 1`，**零新 SQL**；
- 聚合位也已存在：`prem_open = avgIf(ret_open, lu_prev = 1)`、`prem_close = avgIf(ret_close, lu_prev = 1)`
  （即"昨日涨停集合当日"的截面均值，两腿各一份），`_PANEL_COLS` 第六列就是 `prem_open`。

真缺口不是数据、也不是 SQL，而是**曝露位**：`op_limit_up_premium_close_mean`（`:665-687`）
只把 `prem_close` 当信号返回，`prem_open` 仅写进附注（`open_form_days`／`open_form_median`），
其 docstring 自书原因="开盘口径按卡面 two_form_spread 另档建档：只把统计量写进附注，
不占 run_card 单信号入口（卡面自记该柱'不作一票否决门柱'，且'显著低于全样本'无冻结检验量）"。
⇒ 矿脉的真实前置＝**卡面先把"隔夜/日内两档各自的检验量"冻出来**（属供题侧立法，非工程侧），
   工程侧只欠一个 `value_col` 参数位或一次面板结果的顺手物化。

本班为何不自己动手补这两条（写清楚，免得明晨被当成偷懒）：
1. 加 `value_col`＝改 `card_binding.py`，该件在矿考二班在途袋 0014 的件面里——三方真冲突簇已杀 239 袋，
   按总令"遇他班在编同件＝登记后置或改道，禁硬闯"。
2. 顺手物化两腿需要跑一次 hfq×stk_limit 全面板（2018-09-01..2025-09-09）：
   这是**矿考二班今夜正在跑的同一重量级装载**（路径 1 落地后 07b 四跑），
   而 CH 侧上限 7.14 GiB 是被"面板×8 年日线"并发撞穿过（在案 code=241）。
   本班再叠一发同重量查询＝把他班考批推下墙。本班选择零抢墙。

# 二、给矿考二班的分工请求（一条，成本≈0）

你们 `load_limit_up_panel` 的结果里已经带 `prem_open`。若在同一次进程内（用你们已备的
"同进程复用装置缓存"）把两腿各写一枚 CSV 进 `docs/_working/nightmine_campaign/series/`：
`lu_ew_prem_open_v1.csv`（隔夜）与 `lu_ew_prem_intraday_v1.csv`（由 ret_close/ret_open 派生），
表头沿用在册契约 `trade_date,value`，并各带一枚 `.meta.yaml`（本班 02 号规格 §三 的 provenance 形状）
——**零额外 CH 查询**，就把本矿脉的底座钉住。本班可出接线侧配套（绑定册格＋逐张判定）。

# 三、给挖矿二班的分工（配方册/物化，按总令"先 claim 先做"）

本班 04:04 的物化件只覆盖 `technical_indicator` 一族列（列集从你们 20 张卡的卡面派生），
你们聚合 8 卡（`TDM-E-L1-S2/calibration/40..47`）不在其内。本班用在册尺对这 8 张实测：

- **8/8 → `cls=C, reason=target_face_not_index_next_day`**（本班 03:0x 现跑，非读你们台账）；
  卡面 primary=`mkt_fwd10_panel_ew_return（面板等权 10 日前向收益均值，_proxy 披露非指数）`。
  ⇒ 你们这族的**决定面是多日等权目标腿**，不是配方册；物化与登记都做尽也仍考不了（与你们自书缺口②同条）。
- **配方册这条本班劝你们别走**：`c1_market.kline_daily_hfq` 是"逐票×日"表面
  （`SQL_LIMIT_UP_PANEL` 的 `k` 段按 symbol×trade_date 取行、再 `GROUP BY d` 才成日度标量），
  而 A 路模板 `SQL_FACE_DAILY` 是 `anyLast(col) GROUP BY toDate(date_col)`——
  把 5000 只票的某列压成"当日任取一票的值"，与你们 lu_count/lu_ratio/avg_abs_ret 的命题不同型。
  这与本班 05 号判定册对 11 张 A? 卡的结论是同一判据（横截面/聚合口径不同型⇒拒登），
  **你们该走的是"日度聚合序列物化＋base_csv 底座"**（本班 20 张卡就走这条），不是 `_REGISTERED_TABLES`。
- 你们的聚合基序列若在 `minedig_pipeline.py:826 _screen_aggregate` 处顺手落盘
  （现"随函数返回销毁，盘面零存"＝你们自书缺口①），落成本班同款表头契约，
  则本班绑定册的 `base_csv` 形状可直接复用，不必再造第二套读法。

# 四、交叉验证（总令 §二：遇他班已完成任务用自家尺复测）

| 他班已完成 | 本班自取尺 | 结果 |
|---|---|---|
| 考试班宇宙 177／A=0 | 本班 00:1x 与 03:0x **两次独立跑**（中间跨 25 袋、9 张新卡落地） | 两次 tally 全等（A0/A?11/B17/C121/D0/U28，宇宙集合差 0 张）⇒ 本班已落地的 04/05/06 三册至今仍是现值，无需回写 |
| 考试班 §25.9"目标面通道解 119/178＝67%" | 本班按卡面 primary 归一重量 | **同数 118**（差 1 张＝07 卡已被矿考二班考出）；但"一条通道解 119"不成立：94 种读法、91 种单例、前 10 种覆盖 34 张（04 号件） |
| 矿考二班 07 卡双臂首考 | 本班读分数册末两行 | 存在 off/mid 两行、kind=exam、verdict=fail、`maxdd_improvement_pp=1.636`、`sharpe_delta=0.089`、turnover −1.609x；两行 run_id 分别带 `-dualarm_off-`／`-dualarm_mid-` 钉档 ⇒ 与本班"每试次入账"口径相容 |
| 全班共用尺 | 本班跑 07b/双臂之外的事务前正对照 | classify 喂在册已知 hint⇒出 D、喂已登记表⇒出 A、喂未登记表⇒复现 `table_not_in_recipe_book` 原文；三条破坏性输入（缺 base_csv／改 prose_quote／乱 op 名）全部按预期红 ⇒ "开考面 0"是真读数不是坏尺 |
| 统计合法性班（幽灵袋形态） | 本班 02:3x 队列读数 | 该 sid 此前有 dead 袋（ghost_session），本班未动其件；仅登记形态供晨包 |
