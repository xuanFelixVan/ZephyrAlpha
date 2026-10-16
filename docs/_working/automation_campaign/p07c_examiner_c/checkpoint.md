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

---

## 游标更正（10-15 20:06 同班补记，旧上文保留不涂）：**本班"可考面=2"判错，改判为"须注入面，非不能考"**

读 ⑦A 席班次 06（起手 18:10:12／写册 19:3x／实测 87 分）后当班自纠，**下一班照本节领面、勿照上文①②节**：

- 上文①节"117 张＝执行器目标面硬绑，⑤不补则积压永远出不了分"**作废为线索**：`card_binding.py:330-338` 的
  `target_face_not_index_next_day` 只是**绑定层**只认指数次日面；A 席原文＝"panel 且目标=个股次日 的卡 **24 张**，
  其中 **21 张被归 C、3 张归 B**；按卡面绑定逐张人读后**可考面 ≥8（本班烧尽 8 张）**"，并已 8 张入册（0 pass／8 fail）。
- 上文②节"两枚 sector 类等 ⑥ 补 `composite_join_rules`"**降级**：A 席正尺原文（ledger:242）＝
  "正确尺＝逐表面三件实测（①重复行数 ②有效码数≥30 ③目标面是否 1 日），**'卡面没写'绝不等于'跑不了'，也绝不等于'可以瞎跑'**"，
  且他们自己按卡面 `universe_rule` 原文直译造了宇宙掩码（前缀留 5,365 票／剔 279，窗内 7,152,422 格）。
  ⇒ 两枚 sector 卡（`TDM-E-L2-01-2__calibration__02`・`TDM-E-L2-01-3__calibration__02`，10-10 08:20，积压 5 日）**改判＝可考、须自物化注入**。
- **本班实测仍然拦住一条路**（不是"不能考"，是"不能那么考"）：`--mode run`/`build_signal` 类 A 自动绑实跑出
  `anyLast(amount|close) GROUP BY d`＝跨 729 板块码任取一码（卡1 len1595／值 5.3e5..2.3e6 应∈[0,1]、index 起 2020-03-17 越 IS 窗 2021-08-02；
  卡2 close 首 6594→末 556 逐日跳码）⇒ **下一班禁走自动绑，须按卡面逐字冻结式自物化截面份额／rank-pct 主导度后 `run_card` 注入**。
- 本班为何没补跑＝两硬约束非省力：20:06 距班限仅 14 分（A 席同类面花 87 分），且分数册当日**落地面≠盘面**
  （A 席原文"index 仍是他班 **97 行**快照"＋"分数册从未落 HEAD⇒**开班必自带备份**"，其袋亦 landing 失败而 8 张卡面 status 仍 examined）。
  ⇒ **下一班第一动作＝先自带分数册备份再写行**。
- 会话保活正解（本班三次实测钉死，别照抄 pid=0）：`register(pid=0)` 条目**活不过一次外来 `list_active` 收割**
  （19:36 注→19:45 已 None；19:50 再注→19:55 守护首拍 `exited: session not in registry`）；
  **正解＝守护进程单进程内 `register(pid=os.getpid())` 后再进 `run_daemon`**，三态核实 present=True＋pid 为活 PID＋heartbeat 末行 `alive`；
  该形态下 `ENQUEUE-RENEW claim 续租 4/4`（pid=0 那次 0/4）。
- 交付终态（不自封）：袋① dead（ghost_session，未取人工强制 requeue＝不越闸）；袋② 20:04 实测 pending、
  `git log -- 本席目录`=0 且 `git show HEAD:ledger.md`=0 行 ⇒ **本班四件尚未落地**；袋③＝本补记（严格超集）本班末投。

<!-- P10-1016-01-FORCE-CLOSEOUT -->
> **⑩线长席强制收班提醒（2026-10-16 01:5x 实测追加，指令面-only，未改任何判据）**
> 本席 `ledger.md` 里 `[BLOCKER]` 行数实测 **0**（同尺负对照＝⑤席 8 行／⑨席 13 行命中；本席 ledger 正文 26157 字节内连 `BLOCKER` 子串都零命中⇒不是谓词伪空，是真未收班）；10-16 00:53 班同读数＝**连续两班 0 行** ⇒ 依 SOP §3⑩ 工序 9 追记本提醒。
> 下班收班三件（缺一＝本班不算收班）＝①ledger.md 追加至少一行 `[BLOCKER] <YYYY-MM-DD>|<席+班号>|<工具缺陷|判据缺失|数据问题|流程问题|需Owner>|<一句话>|<file:line 或路径>|<要谁做什么>|<高|中|低>`（零问题必写 `[BLOCKER] <date>|<席+班号>|无`）；②提交只走 `python scripts/commit_queue.py` 上游的 `git_commit.py --session <sid> --files <自家清单> --enqueue`（禁裸 git commit／禁从主区 index 直连）；③release 自家 claim＋注销心跳＋台账记实耗分钟。


---

## 游标（⑦c 1016-01 班末，追加节・上文 10-15 首班游标逐字不涂）

- **本班终值＝出分 2 张（均 fail）・prereg 167（C116/U27/B15/A?7/A2/D0）・自动可绑面 2・本班零翻卡外零改判据**。分数册 104→106 行 only-add（写后读回三 sha 全序自证）。
- **下一班领面序改正**：10-15 首班游标①②两节（"117 张等 ⑤ 补目标面口"／"两枚 sector 等 ⑥"）在本席 20:06 更正节基础上再落一刀＝
  ⑦A 席 1015-06 班的"净 15 张形状 OK"里，**已用同一路跑通的是筹码维与均线维（L3-12-3/02・L3-03-2/02）**，其余 13 张逐张还要过"卡面是否给出 t 日可算式"这一关（本班 L3-03-2/03 与两张 sector 卡即卡在此关，非供数堵）。
- **正解装载口（勿重造）**：目标面 t1o_to_t2c 与 20 日动量面已在 ⑦A 席缓存内可复得（shift06_close/open/mask.parquet＋load_column），
  均线族四缓存本班直接命中＝零拉数；chips_winner／conc_90 现拉各≈20 秒/年块。宇宙谓词按卡面逐字，两卡未申报 ST/年龄 ⇒ 勿套 V1 掩码。
- **风险与在册坑复证**：占卡锁 TTL 30 分 < 班限 90 分＝拉数窗内静默过期（本班三锁全过期且零告警）；心跳按 10-15 在册配方（守护自注册活 PID 后同进程进环）本班全程存活 96 分未被收割＝该配方**可用但非充分**，仍须收班按 PID 双证认下班。
- **本班未做（如实）**：未走 GPU（未 acquire 故免还牌）・未 requeue 任何死袋・未 release 他会话 claim・未动门柱/冻结值/判据・未建 worktree・未 spawn 子代理。
