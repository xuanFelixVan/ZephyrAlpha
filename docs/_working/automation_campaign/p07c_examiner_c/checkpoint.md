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

---

## 游标（⑦c 1016-02 班末，追加节・上文 1016-01 游标逐字不涂）

- **本班终值＝出分 2 张（均 fail）・分数册 106→108 行 only-add・prereg 起手实测 163・本班翻卡 2（由执行器自翻）・零改判据/门柱/冻结值**。
  两张＝`entry_flow/L3/TDM-E-L3-12-3__calibration__03_股东户数集中度`（rows[106]）・`.../L3-04__calibration__02_解禁否决`（rows[107]）。
- **本班开考未遂 1 张并转单**＝`entry_flow/L9/TDM-E-L9-A06__calibration__02_主力净流入截面`：供数两面已拉齐并缓存
  （`.runtime/tmp/p07c_1016_02/mf_mnp.parquet` 32,007,191B・`mf_pc.parquet` 2,743,763B，五块 49 秒），
  死在执行器 regime 分段解析器吃卡面 `bull_note` 散文条目（DateParseError 22:15:48）。**卡面未被我改一字，未写分数行，卡仍 preregistered。**
- **新机判谓词与分母（下班与 ⑥/⑤ 可直接复量）**：`window.regimes` 值须匹配 `^\d{4}-\d{2}-\d{2}\.\.\d{4}-\d{2}-\d{2}`；
  全池 553 中有 regimes 者 **369**，含非 span 条目者 **39**＝prereg **14**／blocked_on_data 17／blocked_on_impl 8。
  14 枚 prereg 具名在本席 ledger §四。**其中仅 MF 一枚本班已把两面供数拉齐并缓存＝卡面一修即零拉数开考；
  其余 13 枚本席未验供数与目标面，下班勿当零成本面领。**
- **本班可考面尺直出（勿沿用上班"自动可绑面=2"）**：磁盘面 prereg 163 中，`signal_kind=panel` 且卡面 `data_binding.signal_derivation` 非空
  且 signal_table 挂在本席已服务化源（technical_indicator／kline_daily_hfq／stk_limit）者＝entry_flow **8** 枚
  ＝L2-06 族 4 枚（⑦A 在册 CRASH 面＝calibration_exam.py:261 TypeError，卡面申报 sector＋hfq 双腿）・
  L3-03/ablation/02・L3-07-2/ablation/02 两枚（需新拉 `stk_limit.limit_up` 与 `technical_indicator.atr_14`）・
  L4-03/comparison/02（signal_column＝ask/bid 五档 tick 面）・L2-07/comparison/03（kline_sector_880 板块面）。
  另本班消费的 3 枚（SHC・UNL・MF）系 c3_fundamental／money_flow 单表源，不在此尺的三源谓词内＝**该尺本身族盲，下班勿拿 8 当全集**。
  ⇒ 注入路"卡面可算式＋供数已在册＋执行器可吃"三条件同时成立者，本班复量净剩余 **0**（MF 供数齐但卡面崩，属卡面/执行器缺陷非可考）。
- **下班首查四件**：① 本班袋是否落地（只认 `git log -1 --name-only` 与 blob 内容级）；② ⑥/⑤ 是否已修 regimes 非 span 面
  （修后即考 MF，零拉数）；③ panel 路 mono_spearman 是否已由 ⑤ 补齐（本班两行 unjudged 仍自述"panel 路恒 None"，旧案卷勿涂）；
  ④ 两枚消融卡（L3-03/ablation/02・L3-07-2/ablation/02）若要做＝先拉 `stk_limit.limit_up` 与 `technical_indicator.atr_14`，
  开考口＝`scripts/backtest/fexam/comparison_exam.py:177 run_card_comparison(signal=,target=,dry=)`（R1 注入通道，实测存在）。
- **纪律与自纠（另起留旧案卷，上文不涂）**：
  ① 本班实证一条在册坑＝**"占卡三步翻 examining"与执行器状态闸互斥**（calibration_exam.py:979-980 只认 preregistered；
  :1113-1114 执行器自翻 examined＋lineage）。本席正解＝靠 `.ailocks` 卡锁互斥＋卡面保持 preregistered＋由执行器自翻，
  **未使用 --force**（force 的在册语义＝重考已出分卡）。
  ② 本班一条**归因自纠**：ledger §三 BLOCKER-2 原文把"三把卡锁 6 分钟内消失"归因于"心跳被收割后遭外来清理释放"，
  现测反证＝`.ailocks/salvage_audit.jsonl` 对本席三条记录全为 `salvage-skip`（dead_confirmed false，evidence1 registry:alive）
  且 **claims:none** 出现在 22:00:15／22:10:18／22:15:31 三点；而首班 keeper（pid 37316，21:52 起）确于 22:05 实测已死且
  `.runtime/locks` 无自家 heartbeat 文件（该两件事各自为真）。锁消失机制本席**不下结论**，候选两条如实标注未验＝
  （a）卡文件被改写后锁记录失效（SHC 系本席 CAS 翻面后、UNL 系执行器改写后消失；MF 无写入却同样消失＝该条不自洽）；
  （b）外来 `lock_files.py cleanup` 按 acquiring 进程 PID 判死（本席 acquire 用短命 CLI 进程，PID 即退）。转 ⑤/运行班定论。
  ③ 本班新立自设前置闸 **G5＝signal_spread_day_frac≥0.5**（逐日截面 std>0 的天占比）拦住一次退化读数
  （UNL 装载方向写反→6,743,477 格全同值→G1-G4 四绿且 dry 行照出 ic_mean 4.58e-17）；**门柱与 pillars_numeric 零改动**，
  G5 只算席侧临时面，是否收编在册归 ⑤ 判（本席 ledger §三 BLOCKER-3）。
- **水位与资源（本班读数，勿沿用）**：reaper 起手实测 source=live・commit_pct **74.98**・ram_used 67.6%・cpu 71.1%・degraded False；
  本班全程未起 GPU（未 acquire 看门人⇒收班⑥免执行）；D 盘余量本班未复量。
- **本班未做（如实）**：未 requeue 任何死袋・未 release 他会话 claim・未动其它席指令面・未动门柱/冻结值/判据・未建 worktree・未 spawn 子代理。

---

## 游标补充（⑦c 1016-02 班尾 22:32 现测追加，上文本班游标节逐字不涂）

- **本班袋① `q-20261016-st-qoder-p07c-1016-02-0001` 22:32 仍 pending**（5 件＝台账・游标・分数册・两枚已翻卡；
  队列 head 为他班 300 件件袋，`daemon.online=false`）。**本席 keeper 留岗未销＝pid 22976**
  （在册序＝全袋落地→release→最后 unregister，先注销会被 SESSION-REQUIRED 挡尾袋；
  本席 10-15 首班 ghost_session 袋死实证＋keep 名册第 43 行"袋落地期间 keeper 必须在岗"）。
  ⇒ **下班第一动作＝先查本班袋终态**：`python scripts/commit_queue.py status --session st-qoder-p07c-1016-02`；
  已 done→按 PID 22976 核活终止＋复证 pid 不存在＋心跳末行 exited；仍 pending→续留 keeper，勿代杀、勿 requeue、勿自 drain。
- **袋死预案（禁盲重投）**：袋①快照含"双划 force 旗"字面原文三处（message 已固化不可改），
  而 `gate-detect-git-dangerous` 对本类引用型字面串有在册袋死先例（⑩席 1016-01 班自家两枚，同签名）＝本班已把盘上面改为指称
  （盘现测＝本席台账内该字面串命中 0，谓词与缘由见本班台账 §九；严式 BLOCKER 行数＝5）。若袋①判死，读 `dead_reason` 后以指称版重投即可，无需回滚。
- **worktree 面如实更正（勿自删）**：本席未调用任何工棚/工作树入口（`.worktrees/` 内 p07c 命中 0＝本班零自建），
  但实测会话一注册即由工具自动生成 `.aidrafts/st-qoder-p07c-1016-02` 整树影子壳（同壳另有 1016-01 一枚），
  与"禁建 worktree"令面属既存在册冲突面 ⇒ 本席不自删，交 ⑩/清理专班定性（在册先例＝`auto-spawned-aidrafts-worktree-shell`）。
- **本班剩余面复量结论（下班勿再逐卡烧窗）**：注入路"卡面可算式＋供数已在册＋执行器可吃"三条件净剩余 **0**；
  下一步收益不在考工席而在 ⑥/⑤ 各补一条面＝⑥ 修 14 枚 prereg 卡的 regimes 散文条目（本席已供两面缓存，修后即考零拉数）・
  ⑤ 判 G5 收编与 panel 路 mono_spearman 补面（三班连续未动）。

---

## 游标补充二（⑦c 1016-02 班尾 22:42・袋② 归属风险一行，上文补充节逐字不涂）

- **下班勿盲目 requeue**：实测袋② 分数册 blob＝盘现值 109 行（含 ⑦A 席未落地 rows[108]，HEAD 面 0 命中），
  袋① 册 blob＝108 行（仅本席两行）⇒ 详版与本席自犯定性在 ledger §十一；
  处置权在 ⑩/运行班（本席不删他席字节、不自行摘队列件）。下班领面先 `git show HEAD:分数册` 复量行数与
  `commit_queue.py status --session st-qoder-p07c-1016-02` 三袋终态，再决定是否需按盘现字节另投（＝在册正解"读 dead_reason 修因后重投"）。
- 本班尾巴面（§十・§十一 与本节）系袋② 快照之后所写，由袋③（只含本席两件 _working 件，不含分数册）承接落地。
## 游标（⑦c 1017-01 班末 01:1x 追加，上文 1016-02 各节逐字不涂）

- **本班终值＝出分 0 张・零翻卡・零改判据/门柱/冻结值・分数册字节零动作**（CH 禁跑窗 01:00–04:00 与 90 分班限整段重叠，两条零 CH 出分路实测均无面＝缓存目标面板 0 枚＋162 枚 prereg 零本地序列申报）。本班产出＝**执行器面案卷**，非考试读数。
- **分母（本班两时点同尺，值守内未动）**：prereg 磁盘面 **162**（00:52 与 01:01/01:03 三次 survey 同值）＝entry 91／exit 25／portfolio 21／position 25；四族文件总数 589；六态加总 438＋51＋37＋63＝589 ✓。分数册 disk 110＝HEAD 110・index 106（在册「落地一次 index 停在落地前一版」形态复现，本席不复位）。上班 1016-02 袋① done（landed e9089e6cfc）・袋②③ dead（同一条 ledger.md 双侧皆改）⇒ **上班尾巴面 §十—§十四 与游标补充二至今未落地**，本席不 requeue（同字节必同死）、不自 drain。
- **下班领面全集＝162 减 41 枚点名＝121 枚**（不必重跑预演；预演尺全程 13.5 秒/8 枚、满批 <3 分，零 CH、三面隔离已实测自证）。分层：entry panel 25／series 55・exit panel 3／series 6・portfolio panel 4／series 17・position panel 10／series 1。route 面 series 126／dual_arm 36／**event 0**（积压面里根本没有事件路卡，上班游标担心的事件路 OOS 地板柱不在本面积）。
- **41 枚避让（＝两张转单面，具名在本席台账 §五）**：(a) 28 枚 route=dual_arm 且 kind=panel ⇒ 崩在 `calibration_exam.py:561 _comparison_metrics`→`:217 _series_metrics`→`:97 pd.Series(2D)`，**对照族驱动器 comparison_exam 同根**（dry=False 实测同帧崩），换入口救不了；(b) 13 枚 regimes 散文条目（`_span_pairs` 退回整串→`_in_spans` pd.Timestamp 抛），其中 **2 枚系 ⑥ 10-16 22:15 新出**（L3-11-1/03・L3-11-2/03 现势窗）＝1016-02 班转单后该形制仍在新增。
- **下班首查四件**：① 先查本席本班袋终态（`commit_queue.py status --session st-qoder-p07c-1017-01`）与本行是否落地，只认 `git log -1 --name-only` 与 blob 内容级；② ⑤ 是否修 (a) 那条腿（修后 28 枚即并入领面，其中 12 枚 position/exit 族 10-15 19:00 起积压最久）；③ ⑥ 是否把 13 枚 regimes 改回 span 形制（修后即考，MF 一枚供数两面仍缓存于 `.runtime/tmp/p07c_1016_02/`＝零拉数）；④ 孤儿 examining 卡 `entry_flow/L3/TDM-E-L3-03-2__calibration__03_温和放量`（盘=examining／HEAD=preregistered／run_id null／18:38:44 翻面未开考，⑦A 1016-03 面）——**复位归 ⑦A/⑩，本席与下班皆不代翻**（状态闸只认 preregistered，卡对全席不可考）。
- **给 ⑩/⑨/⑤ 的一条现象（本席不裁）**：白噪声两面（真 IC≈0）在 121 枚 ran 里出 **2 枚 pass 且 fails 空**——其一 `TDM-P-P1-04/calibration/04` 实读 ic_mean +0.00321 对卡面冻的 `ic_mean_min: -0.015` 负地板（方向柱缺位）；其二 `TDM-E-L2-01/comparison/02` 双臂路 ic_mean=None／n=None 而 unjudged 三面全空。＝**「冻负地板」与「数值面无」两形态下判官不会判 fail**（calibration_exam.py:267-269 在册注释自述「NaN 跳过加败＝只可能放行不可能记败」的同族第二、三例）。
- **纪律与自纠（另起留旧案卷）**：本班一处**本席脚本自犯**＝keep 名册追加件首版把结果面写成 `res.ok`（SafeWriteResult 真字段＝written/before_sha256/after_sha256）⇒ AttributeError 于写后的打印行，**实质追加已成功且不重复**（复量＝422 行、本席三行在位、前缀 intact），本班已就地改为幂等版（已在位则零动作）并按该形态给复核命令；本班未起 GPU（IC_DEVICE=cpu 全程）⇒ 收班⑥免执行；本班未建 worktree、未 spawn 子代理、未 release 他会话 claim、未 requeue 死袋。
- **水位与资源（本班读数，勿沿用）**：reaper 00:50:46 source=live・commit_pct 81.46・ram_used 73.3%・cpu 87.2%・degraded False・stash_count 27・worktree_changes 1456・dead_archive ok=False rc=1（serializer 租约 pid=47508 存活）；D 盘余量本班未量。
- **心跳交接**：本席 keeper pid **39796**（01:01:33 registered present=True entry_pid=39796）。本班收班按 PID 精确终止并在末次网关动作之后复量（在册更正＝调网关即被代起守护，杀须排最后＋等 ≥70 秒双谓词读）；keep 名册本席两行（421–422 行）与注释行 420 留岗（属白名单面，非本班临时件）。
