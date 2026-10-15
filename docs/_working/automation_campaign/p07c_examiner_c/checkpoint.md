---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑦考工C·游标
---

# 游标

cursor: 班次 01（st-qoder-p07c-1015-01，18:50:19 开班→19:25 交账≈35 分）**本班 0 张入册**（保底双口径未达：0＜8 且未跑满 4 小时，如实呈报）。
交付＝对 A/B 两静态席"零可考"的**独立第三复量**＋把"类 A 可绑"从读码结论升格为落地实测（证其为错面）。

分母（值守内两时点，**面值被上游推进**）：preregistered 磁盘面 175@18:53/19:05 → **171@19:12**（减少的 4 张全在 entry_flow 103→99，
系 A/B 在途翻卡，本班零翻卡）；HEAD 面 191@18:53＞磁盘 ⇒ 他席翻卡未落地；五态加总 empty186/prereg175/examined73/blocked_data71/blocked_impl47＝552＝文件总数。
分数册 doc1 `rows:`＝**96**（⑩ 06:12 记 examined 恒 55，现磁盘 73 ⇒ 今日确有产出，非全线停摆）。本班采**磁盘面**，不合面。

本班可考面尺直出：`classify_card` 逐卡 n=171 加总自证 ⇒ **C120／U27／B15／A?7／A2／D0**；`_BINDABLE_CLASSES=("A","D")` ⇒ **全班可绑面＝2**。
两把尺互锁：类 C 目标面分型 64+27+20+3+3＝**117** ＝ 拒因 `target_face_not_index_next_day` 计数（执行器硬绑指数次日收益）。
**两把尺互不解释的另一面（勿混）**：160/175 声明 CH 表式绑定、0/175 声明本地 `derived_series`；全库申报本地序列者恰 8 张**且 8/8 已 examined** ⇒
下一班若再遇"preregistered 面零本地序列"，那是**供题形状**问题不是管道失明（D 路径 10-09 20:25 批之前的 8 张跑得通，正对照在盘 SERIES_DIR 37 件）。

下一班领面序（按 ROI，**本班一张未跑、未占卡，故无遗留卡锁**）：
①**先验 ⑤ 是否补了目标面口**＝本席判定"开考与否的唯一闸门"：117 张卡在 `_INDEX_TARGET_RE`（`card_binding.py:330`）外，
  分型 engine_replay 64／other 27／panel_stock 20／sector_series 3／probability_hit 3。⑤未补则本班这类**零收益**，别再逐卡烧 15 分钟窗。
②**等 ⑥ 补 `composite_join_rules` 申报位**＝仅有的两枚类 A：`entry_flow/L2/TDM-E-L2-01-2__calibration__02_板块成交额占比活跃度.yaml`・
  `.../TDM-E-L2-01-3__calibration__02_多周期动量主导度.yaml`（均 10-10 08:20，积压 5 日）。**⚠ 补前绝不可考**：
  `build_signal` 实跑出的是 `SQL_FACE_DAILY = anyLast(col) GROUP BY d`＝跨 729 板块码任取一码的原始 amount/close
  （实测 卡1 len=1595 值 5.3e5..2.3e6、index 起 2020-03-17 越卡 IS 窗 2021-08-02＝SQL 无日期谓词；卡2 close 首 6594→末 556 逐日跳码），
  而卡面冻结的是截面份额／rank-pct 主导度⇒**跑＝往永久分数册写假陈述**。在册正解算子 `op_sector_top_n_amount_share`・`load_sector_family_panel`
  要求四要素整表取自 22 册 args，卡面无 `composite_join_rules` 时 `_card_composite_pairs` 直接 raise ⇒ **考工自制册格＝自批，勿越**（⑧B 05 班定性违甲案③同）。
③**A? 7 张逐卡**（离可绑只差一步，但要 ⑤/⑥/① 三席各自点头）：`normalization_recipe_undecided` 3 张＝
  L2-01/comparison/02・L2-01/comparison/03・L2-04-1/calibration/02（归一配方未定）；`table_not_in_recipe_book` 4 张＝
  L2-09/calibration/03→`c3_fundamental.research_report`・L9-A10/calibration/02→`c1_market.macro_data`・
  L9-A15/calibration/02・/03→`c1_market.hl_funding_history`，**三表各挂一条 open 缺口**
  （`research_report_hot_value_rating_change_empty`／`macro_data_eastmoney_ssl_eof_chronic`／`hl_liquidation_raw_empty`）⇒ 与 ① 席联判，勿先入册后补数。
④**断供避让只按"窗与列"判，禁按表名命中判**（本席两条实测）：`rate_decision_calendar_jin10_retired` 虽 status=no_source，
  但停更窗 2025-11-01..2026-09-18 **不覆盖**事件卡 OOS `2024-01-01..2025-09-09`，且册内 `primary_alternative` 自记 2,386 行历史无损⇒不挡；
  `kline_sector_880_resample_false_success` 虽表名正是两枚类 A 卡的 signal_table，但 `impact` 逐字"15/30/60min 缺失、**日K腿无恙**"⇒`period='1d'` 不挡。
⑤**别将事件族 OOS 柱当"缺数"或"信号弱"**（⑨席 13 班尺已在册，勿重烧）：floor=max(200,卡面值) 与被确认窗同套（`calibration_exam.py:843/872-881`），
  410 日窗需密度≥48.8% 而实测 19.3–40.2%＝0/23 可达，**P-9 待裁**、floor 属门柱本席无权动；读 `oos` 须按**嵌套 dict** 取键（按标量判即得"23/23 无面"假红）。

水位与纪律（本班读数，勿沿用）：`commit_pct 95.95→90.85→85.74`、`degraded True→True→**False**`（19:24）、ALERT-SYS-001 于 19:2x 自解。
本班全程未起 GPU、未装全市场面板（degraded 期不试重装载，循 ⑥ 1015-11／⑧B 06 班先例）；reaper dry-run 点名的 PID=2380 系他会话件，本席未代杀。

下一班防重入锚：本席四件套系 10-15 建席首班经 `batch_creation_tokens.py --capability p07c-examiner-c` 登记（`OK: 已登记 4 条`，
册面 grep 自家四件＝4 自证），**只此一址**（`.aidrafts/*/…/automation_campaign/` 逐车道快照与 `docs/_archive/**` 均无 c 席，"两址同读"此处不适用）。
**SOP §3⑦⑧ 席位节与 §3-D 排班表至今未列 C 席**（扩席依据仅＝§3-A "积压>50 每 50 张加一席"预授权；`_registry/catalogs/seat_registry.yaml` 是龙虎榜交易席位册，非本生产线席位面）
⇒ 补记归 ⑩ 线长，考工席不代改政策/他席指令面。
