---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑦考工C·findings台账
---

# findings 台账（追加式，禁删改他人行）

格式：`## <MM-DD HH:MM> · <一批摘要>` + 要点若干 + 自检结论（两轮）。
本席四件套建册时点＝2026-10-15 班次 01（st-qoder-p07c-1015-01），本班之前无班次记录。

## 10-15 19:25 · 班次 01（st-qoder-p07c-1015-01）建席首班·全族机动：0 张出分（保底双口径未达，如实呈报）＋对静态席"零可考"的独立第三复量＋类 A 错面升格为落地实测

**本班实际耗时**：起 18:50:19 冷启动 → 19:25 交账 ≈ 35 分（`date` 实测三锚点 18:50:19／19:05:39／19:24:23，非体感）。
**出分 0 张＜8，未跑满 4 小时 ⇒ 保底双口径均未达**，本班不产分数行、不翻卡状态、不改判据门柱（理由见⑤⑥节，非"没干活"）。

### 一、冷启动与值守环境（三态实测，含水位三读）

- 步骤一 python=3.12.8；`setup_dev_env.py --check` usercustomize exists=True／installed（指 D:\\ZephyrAlpha）。
- 步骤二 `lock_files.py cleanup`＝**CLEAN 无死锁需要清理**（与 ⑨席 14 班"释放报 NOT FOUND 而 released=4"不同形态，本班进场即无过期 claim 面）。
- 步骤三 `process_reaper --status` source=live／last_run=18:50:38／scanned=50／whitelist_hits=32／killed=1／reported=2 ⇒ 允许写。
- **水位三读**（本班全程未起 GPU、未装全市场面板，只做单列 CH 聚合与只读尺）：
  18:51 `commit_pct 95.95／degraded=True／breached=[ALERT-SYS-001, ALERT-SYS-003]`→19:2x `90.85／True／[ALERT-SYS-003]`→19:24 `85.74／**degraded=False**`。
  起批闸前读数即 95.95 处我未起任何重计算，与 ⑥席 1015-11 班／⑧B 06 班"degraded 即不试重装载"同纪律。
- reaper dry-run 点名 `would kill PID=2380 reason=runtime_dir_orphan:age=60min cmd=...\.runtime\tmp\st-doc`＝**他会话件，本席不代杀不认领**；
  `worktree_changes=5859 > 50` 并行漂移告警在报（非本席造成，本席未建车道）。

### 二、防重入＝四件套缺失，按指令卡允许路径补建（禁裸建）

- 指令卡要求先读 `docs/_working/automation_campaign/p07c_examiner_c/checkpoint.md`——**该目录盘/HEAD 两面查无**。
- 负空间三扫尽净：①`git ls-files | grep -i p07c` 零行；②`git grep -l -iE "p07c_examiner_c|examiner_c" HEAD` 零行；
  ③全仓 `grep -rliE "p07c_examiner_c|考工c席|examiner_c" docs/ scripts/ src/ tests/` 零文件；
  ④`.aidrafts/*/docs/_working/automation_campaign/` 逐车道快照只见 p01..p10（含 p07_examiner_a／p08_examiner_b），无 c 席；
  ⑤`docs/_archive/**` 无 p07c／examiner_c。**⇒ 本席确为建席首班，无上一班游标可撞**（"两址同读游标"在册教训此处不适用：只有一个址，且它当时不存在）。
- 正对照（防"0 命中是尺坏"）：同批目录同型 grep 对 A/B 席图案命中 **17** 行 ⇒ 尺通、C 席缺席是真缺席。
- SOP 侧核对：§3-A 白纸黑字"只扩吞吐席：考工（⑦⑧→C/D/E…按 preregistered 积压>50 张时每 50 张加一席）"——本班实测积压 171–175 张＞50，
  扩 C 属政策预授权；但 **§3⑦⑧ 席位节与 §3-D 排班表至今未列 C 席**，且 `docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml`
  是龙虎榜交易席位册（SEAT-INST/YOUZI…）与本生产线无关，非席位登记面。
  ⇒ **SOP 席位节补记 C 席归 ⑩ 线长，本席不代改政策/他席指令面**（指令卡"禁代⑩线长改其它席指令面"）。
- 补建走令在册通道（先例＝`6ba6295646` 十席 40 件"token 同袋登记 autopipeline×40"）：
  `batch_creation_tokens.py --capability p07c-examiner-c`（**ASCII slug**，避在册坑①）
  先 `--dry-run` 预览 4 件 → 实跑回显 `OK: 已登记 4 条` → 册面自证
  `grep -cE "p07c_examiner_c/(scope|instruction|checkpoint|ledger)\.md" capability_canonical_file_registry.yaml` ＝ **4**。
  令牌热册本身未随袋投（在册教训：整档快照入袋＝归属篡改）。
- **在册坑第③条本班实地命中一次**：首次 `--dry-run` 报"无待登记文件（全部已登记或前缀为空）"，
  真因＝当时前缀目录尚不存在（非"已被他人登记"）。工具扫描面＝`git ls-files` ∪ `--others --exclude-standard`，
  空目录自然零候选。⇒ 顺序须"先落件、后登令牌"，CREATE-GUARD 在提交时才看账本，非"登记了才能落笔"。

### 三、分母实测（本班值守内面值被上游推进，两时点都记，不拿旧数当现值）

| 尺 | 18:53 | 19:05:39／46／54（三测同值） | 19:12:59 | 19:2x |
|---|---|---|---|---|
| grep `status: preregistered`（磁盘） | 175 | 175 | **171** | 171 |
| yaml 解析同谓词 | — | 175 | — | **171** |
| `find -name *.yaml` 文件总数 | 552 | 552 | — | 552 |
| HEAD 面 grep | 191 | — | — | — |

- 全树五态加总自证（18:56）：empty 186／preregistered 175／examined 73／blocked_on_data 71／blocked_on_impl 47＝**552**＝文件总数。
- 族分片（18:53）：entry_flow 103／exit_flow 26／portfolio_flow 21／position_flow 25＝175（目录实名 `portfolio_flow`，非 portfolio）。
- **面值移动归因**：19:05→19:12 磁盘 preregistered 175→171，减少的 4 张全在 entry_flow（103→99，见④节 family×class 加总）。
  本班未翻任何卡，故系他席（A/B）在途推进——与 `face-value-moves-under-you-during-shift` 同型；配额面须写实名领卡少写条件式。
- HEAD 191 ＞ 磁盘 171 ⇒ 他席翻卡字节尚未落地（落地链不健康侧证），本席按指令"采磁盘面"不自行合面。
- 分数册（18:56）：双文档结构，doc1 `rows:` 长度 **96**（⑩席 ledger 记 06:12 时 examined 恒 55，现磁盘 73／册 96 行 ⇒ 今日确有产出，非全线停摆）。
- raw 形制尺：全库含 `prereg` 的 `status:` 行**恰 175 处、全为 indent=0 且无引号**⇒ grep 与解析两尺此处同构，无别名/引号漏网。

### 四、独立普查（机动席本职：不复抄 A/B 结论，自带三尺）

`card_binding.classify_card` 逐卡直调（docstring 自陈"零 CH"），n=171 与 preregistered 面**加总自证相等**：

- 类别：**C 120／U 27／B 15／A? 7／A 2／D 0**（加总 171）。可绑面 `_BINDABLE_CLASSES=("A","D")` ⇒ **全班可绑面＝2 张**（均 entry_flow L2）。
- family×class：entry_flow A2+A?7+B14+C50+U26＝**99**；exit_flow B1+C24+U1＝**26**；portfolio_flow C21＝**21**；position_flow C25＝**25**；加总 171。
  ⇒ 与 ⑦A 席游标"entry 族 A2・A?7・…加总 103"在两格上逐字复现（A2／A?7），其 103 与本班 99 的差＝③节那 4 张在途推进。
- 拒因头名分账（加总 171）：`target_face_not_index_next_day` **117**／`panel_deferred` 15／`multi_table_needs_composite_recipe` 13／
  `no_data_binding_section` 13／`table_not_in_recipe_book` 4／`normalization_recipe_undecided` 3／`needs_replay_engine` 2／
  `signal_column_not_a_single_identifier` 1／`executor_horizon_mismatch` 1／none（＝2 张 A）2。
- 类 C 目标面分型（执行器硬绑"指数次日收益"撞空的形状，加总 **117** 与拒因头名精确相等＝两尺互锁）：
  `engine_replay` 64／`other` 27／`panel_stock` 20／`sector_series` 3／`probability_hit` 3。
- 绑定块形状普查：175 张中 **160 张** data_binding 齐 `signal_table+signal_column+signal_derivation+target_source`（CH 表式）、
  **13 张**整块无 data_binding（含积压最久的 10-09 20:25 十二张里多数）、**0 张**申报本地 `derived_series/target_series`。

### 五、类 A 两卡"可绑＝假绿"——本班把它从读码结论升格为落地实测

尺（读码）：`SQL_FACE_DAILY = "SELECT toDate({date_col}) AS d, anyLast({col}) AS v FROM {tbl} WHERE {where} GROUP BY d ORDER BY d"`
——`anyLast` 跨 `sector_code` 塌成每日一值；`c1_market.kline_sector_880` 日频面 per（卡面自证 industry_l1 61 codes＋industry_ths 128 codes），
故该式取的是**任意一个板块**的 amount/close，既非合计也非卡面声明的截面份额。且 `WHERE` 只有 `period='1d'`、**无日期谓词**。

实测（`build_signal(card, cls)` 直调，只读 CH、不写册、不改卡面）：

- `TDM-E-L2-01-2/calibration/02_板块成交额占比活跃度`：返回 Series len=**1595**，index 起 **2020-03-17**（卡 IS 窗起 **2021-08-02**，越界即证无日期闸），
  值 527702.0／781991.0／559322.19…末 2306761.25／1721043.38／2064194.13，nunique 1584——**原始 amount 量级**，
  而卡面 `signal_derivation` 逐字冻结的是"占比=sector amount / Σ(同 code_family 全体 sector amount)（分母口径=industry_l1∪industry_ths，
  由 c1_market.sector_code_name_map.code_family 在册映射界定，禁自拟名单）；环比=占比/占比.shift(5)−1；series 面取占比前 10% 板块等权组合的次日超额与全样本差"。
  份额值域应∈[0,1]，实测值域 5×10^5..2×10^6 ⇒ **不同物**。
- `TDM-E-L2-01-3/calibration/02_多周期动量主导度`：返回 close 首 6594.24／6710.3／6816.43、末 596.77／578.12／556.23
  ——逐日在不同板块指数间跳（首末差 10 倍）＝`anyLast` 任取一码的直接可见性；卡面声明的是"各周期截面 rank-pct 归一→主导度=argmax_i(rank_i)；
  连续面=0.2·rank_q3+0.3·rank_q5+0.5·rank_q20"。
- 两次的 `ev` 凭据面均如实记 `op: amount|anyLast_per_day`／`close|anyLast_per_day`＋完整 SQL 前缀 ⇒ 机器自证喂的是错面，非本席推测。

结论：**这两张若开考＝往永久分数册写两条"信号无/弱信息"的假陈述**（考的是随机板块的原始量价，不是卡面冻结的截面份额／主导度）。
与 ⑧B 席 top_n=20 撞 `ic_exam.py` 30 列地板致 `ic_stats([])` 交回 **0.0 而非 nan** 是同族病灶（仪器没测到却报数），不同层：那里是地板，这里是**绑定面**。

正解在册、非本席职权：模块内已有截面形算子 `op_sector_top_n_amount_share`（用 `SQL_SECTOR_TOP_N`＝`sumIf(amt, rk<=n)/nullIf(sum(amt),0)`）
与 `load_sector_family_panel`（`SQL_SECTOR_FAMILY_PANEL`，GROUP BY d,code＋anyLast 收版本行），
其 `:929` 注释自陈"族名单／映射表／周期／列名四要素**整表取自册 args**——本函数不写"。
而这两张卡面**无 `composite_join_rules` 块**，`_card_composite_pairs` 对该情形直接 `raise ValueError("composite_card_face_rules_absent（卡面无 composite_join_rules 块＝不许走复合口）")`。
⇒ 缺的是**卡面绑定申报位**（⑥制卡席）与**册格**（⑤/⑥），不是考工可以自造的东西——"考工自制册格＝自批"在 ⑧B 05 班已定性违甲案③，本席照此不越。

### 六、正对照：管道未失明，"0" 是面结论

- 全库申报本地序列的卡恰 **8 张**，状态 **8/8 全为 examined**、preregistered 面 **0 张**；`SERIES_DIR=docs/04_research_records/mining/ledgers/nightmine_20261010/series`
  exists=True、37 件在盘，申报名 `avg_abs_ret／avg_abs_ret_z20／lu_count／lu_count_z20／lu_ratio／lu_ratio_z20／mkt_fwd5／mkt_fwd10` 可解。
- 磁盘 examined 73（⑩ 06:12 记 55）＋分数册 rows 96 ⇒ 本班工具面能判出可绑类（D 路径在 examined 那 8 张上仍判得通）。
- ⇒ 本席"0 出分"不是"考工永远跑不了"（04 班两张真分即自物化跑的，⑧B 亦如此纠偏），而是**当前 preregistered 面的构成里没有一张能被现有执行器喂对口径**。

### 七、断供册避让纪律：面积≠阻断，两条在册缺口经实测判定"不挡本席候选"

- `rate_decision_calendar_jin10_retired`（status=**no_source**）：停更窗 2025-11-01..2026-09-18，
  而本席最久积压卡（10-09 20:25 十二张）OOS 窗逐字＝`2024-01-01..2025-09-09`（⑨席 13 班同值），**整窗在停更窗之前**；
  且该条 `primary_alternative` 自记"11 央行历史决议 2,386 行在库无损（1991/1970 起）"⇒ **不因该条拒考**。
- `kline_sector_880_resample_false_success`（status=**open**，表名正是两张 A 卡的 signal_table）：
  `impact` 逐字＝"15min/30min/60min 重采样行在 09-22 与 09-23 缺失；**日K腿无恙**"，两张卡走 `period='1d'` 且 IS/OOS 均早于 2026-09 ⇒ **不挡**。
- ⇒ 本席把这两条写清是防下一班拿"表名命中断供册"当拒考理由（⑧B 06 班"按表名级避让会白挡 8 张"同型，本族数字另立）。
- 断供册盘面：84 条，status 分布 completed 7／accepted 19／resolved 13／monitoring 5／**open 28**／mitigated 4／**no_source 7**／retired_quarantine 1。

### 八、堵点分账与路由（本席不自清、不代签、不改判据）

给 **⑤ 实现席**（117 张，占积压 68.4%）：执行器目标面硬绑 `_INDEX_TARGET_RE`（指数次日收益），
类 C 中 `engine_replay` 64 张需双臂/NAV 回放口、`panel_stock` 20 张需面板撮合口、`probability_hit` 3／`sector_series` 3／`other` 27。
⇒ 这是**执行器能力面缺口**，不是卡缺陷；不补齐则 preregistered 积压永远出不了分。
给 **⑥ 制卡席**：①两张类 A（L2-01-2/02、L2-01-3/02）缺 `composite_join_rules` 申报位 ⇒ 补了才走得通在册截面算子；
②13 张整块无 data_binding（含 10-09 20:25 十二张最久积压者多数）；
③A? 7 张逐卡：`normalization_recipe_undecided` 3 张（L2-01/comparison/02、L2-01/comparison/03、L2-04-1/calibration/02）＝归一配方未定，
`table_not_in_recipe_book` 4 张（L2-09/calibration/03→`c3_fundamental.research_report`；L9-A10/calibration/02→`c1_market.macro_data`；
L9-A15/calibration/02・/03→`c1_market.hl_funding_history`）＝表未入配方册，且三张表各自在册均有 open 缺口
（`research_report_hot_value_rating_change_empty`／`macro_data_eastmoney_ssl_eof_chronic`／`hl_liquidation_raw_empty`）⇒ 须与 ①席复测联判，勿先入册后补数。
给 **① 数据源席**：上列 4 张 A? 卡的表名与其 open 缺口一一对应，见⑦节判据（勿把"表名命中"当"必挡"）。
给 **⑩ 线长**：本班＝⑩ 席 ledger 第 58 行预告的"第三班"（"⑦⑧ 两班未开闸（examined 恒 55），若第三班仍零消费，
须把'考工席位无人发车'升级成呈批面而非再派同文配额"）。**第三席独立复量结论＝现器可考面 2 张、且 2 张口径错配不可考**。
与 10-12 在册档 `exam-card-pipeline-blockage-map` 的"现器可考=0 三证＋三条闸（面板形 39／目标面 118／供题）"同向；
本班 10-15 现值＝目标面闸 **117**（当日 118）、面板/持仓面闸 15+20＝35（当日 39）——**三天未变，属结构性而非当日抖动**。
另：SOP §3⑦⑧/§3-D 席位节补记 C 席归 ⑩，本席未代改。

### 九、本班自纠（四处，另起留旧案不改上文）

1. **首个普查脚本自报 preregistered=191 未复现**：19:05 三尺三测（grep／find／yaml 解析）同值 175，19:12 起 171。
   该 191 读数无法在任何尺上重现，**下一班勿引用**；本班不据此判事故（在册教训：勿把行数骤变当事故、0 命中/满命中都要对照）。
2. **第一版 route 尺取 `route:` 键，103 张全归空值**＝族盲尺（卡面真字段是 `family:`＋`signal_kind:`）；改键后加总恰＝175 才自证。
   与 ⑧B 06 班"拿单一 `_CALIBRATION_JUDGED_KEYS` 量 72 张属族盲"同型，本席首版比它更糟（直接全空）。
3. **data_binding 覆盖首版只扁平探一层**，误报 `derived_series/target_series` 在 examined 面也全 0，
   与"examined 有 8 张真分走双注入"当场矛盾；改按执行器真读路径 `card["data_binding"][...]` 重测，得 8/8 examined、0/175 preregistered。
4. **`GitCommitGateway.list_active` 不存在**（AttributeError：type object has no attribute）——本班未拿它当活性尺，
   改按会话册与四件套实面直查；在册教训"liveness 尺须与执行工具守卫同源"此处表现为**我记错了单口名**，勿照抄。

### 十、自检两轮

- 第一轮（only-add 未动旧行）：ledger 与 checkpoint 均以 Edit 追加/原地游标行改写，本席四件系本班新建（建册首班），
  不存在他人旧行；分数册 `exam_scores_v1.yaml` 本班 **plus=0／minus=0**（未写任何行）；卡面文件本班 plus=0／minus=0（未翻状态）。
  卡锁：本班未 claim 任何 exam_card（未开考即不占卡），仅 claim 自家四件（TTL 30 分，交账后即 release）。
- 第二轮（与门柱一致）：本班未跑任何判据、未读门柱出分⇒无"分数与门柱不一致"可能；
  判据/门柱/冻结值零改动、零新建卡、零翻态、零入册行、零改他席面；`断供` 与 `可达性` 结论全部带实测读数与文件行号，无凭记忆路径。
- 加总自证三处：五态 552＝文件总数；family×class 99+26+21+25=171＝类别普查加总＝preregistered 面；
  类 C 目标面分型 64+27+20+3+3=117＝拒因 `target_face_not_index_next_day` 计数。

### 十一、降级直改主区理由（RULE-WORKTREE 显式申请制留痕）

本班两件写入件系本岗 `_working` 活文档（新建席位台账／游标）＋席位 scope/instruction 两件，
**非施工件、不改判据面、不碰分数册、不翻卡状态**；与 ⑧B 06／05 班同型先例。
未建车道的原因＝产出全部为只读尺与自岗账，且落地链当日不健康（死信 315、⑩ 停发生产配额），建车道再合批只会增加三方冲突面。

## 10-15 20:06 · 班次 01 补记（同一班，另起留旧案、上文不改）＝本班两处结论被 ⑦A 席 06 班当场纠正＋袋态实报

**触发**：20:0x 读到 ⑦A 席班次 06（起手 18:10:12、写册 19:3x、实测 87 分）主产出＝**推翻前任"现器可考面=0"并已 8 张入册（0 pass／8 fail）**。
本补记优先于上文④⑤⑧节的相应结论；上文原样留着不涂（Owner 两轮追认过的更正法＝另起留旧案）。

### 一、被纠正的两处（逐字引 A 席在册原文，非本席转述）

1. 上文⑧节我把 117 张 `target_face_not_index_next_day` 判为"**执行器能力面缺口，不补齐则积压永远出不了分**"——**判重了**。
   真身＝**绑定层**只认指数次日面（`card_binding.py:330-338`），而 `signal_kind=panel` 的卡由考工自己灌面对象即可考；
   A 席原文＝"panel 且目标=个股次日 的卡 **24 张**，其中 **21 张被归 C、3 张归 B**；按卡面绑定逐张人读后**可考面 ≥8（本班烧尽 8 张）**"。
2. 上文⑤节我把两枚类 A 卡判为"缺卡面绑定申报位与 22 册格⇒考工不可自造"——**停在了错误的一步**。
   A 席正尺原文（ledger:242）＝"正确尺＝逐表面三件实测（①重复行数 ②有效码数≥30 ③目标面是否 1 日），
   **'卡面没写'绝不等于'跑不了'，也绝不等于'可以瞎跑'**"；且他们确实自己按卡面 `universe_rule` 原文直译造了宇宙掩码
   （前缀留 5,365 票／剔 279；窗内留 7,152,422 格）。⇒ 两枚 sector 卡的**正确动作＝本席按卡面逐字冻结式自物化截面份额／rank-pct 主导度后 run_card 注入**，
   而非把它们退回 ⑥。本班把"绑定层不给路"误读成"执行器没能力"，是把**自家工序**记在了别人账上（同 `lane-enqueue` 与 ⑧B"别把 class A/D=0 当考工永远跑不了"两次在册纠偏同型，我第三次踩）。

**仍然成立的部分（不被本次纠正覆盖）**：`build_signal` 类 A 路实跑出 `anyLast(amount|close) GROUP BY d`＝跨 729 板块码任取一码，
该结论只否定**自动绑定路**，不否定**考工自物化注入路**。卡1 len=1595／值 5.3e5..2.3e6／index 起 2020-03-17 越 IS 窗，与卡2 close 首 6594→末 556 逐日跳码，
仍是"下一班**勿走 --mode run 自动绑**、须走注入"的直接凭据。

### 二、本班剩余时间内为何仍未补跑这 2 张（不是省力，是两条硬约束）

- 时间：20:06 起距班期上限 20:20 仅≈14 分，而 A 席为同类 sector/panel 面付出 87 分（超 60 分班期，超支记因见其 §七）；
  本席若此刻起做截面份额物化＋五分位分桶＋regime 同号＋OOS 同号五柱，**必然落在"瞎跑"一侧**，正撞 A 席那句"绝不等于可以瞎跑"。
- 写册面：分数册当日是热件且**落地面未跟上盘面**——A 席原文"分数册照旧不随袋（index 仍是他班 **97 行**快照）"＋"分数册从未落 HEAD⇒开班必自带备份"。
  本席在 18:56 量到 rows=96，A 席 19:3x 已写到 97 行且其袋亦 landing 失败（"8 张卡面 status 仍 examined ⇒ 本次 landing 失败未洗掉本席交付"）
  ⇒ 在 14 分内追加分数行＝给他席在途快照再叠一个必撞"双侧皆改"的热件写面。**记堵点即停**，交下一班带备份做。

### 三、袋态实报（本班交付未落地，不自封已交付）

- 袋①`q-20261015-st-qoder-p07c-1015-01-0001`＝**dead**，dead_reason 逐字已读＝
  `ghost_session: 属主会话 … 已死（heartbeat=exited / 注册表无在册），自动重投被存活闸拒绝（裁定#459；CLI 手动 requeue 不受闸限，人工可强制）`
  ⇒ **本席未取人工强制杠杆**（不越闸）。
- 根因实测钉死（非猜）：`register(pid=0)` 的条目**活不过一次外来 `list_active` 收割**——
  19:36 注册→19:45 `mark_logical` 时 `get_session` 已 None；再注册（19:50）→19:55 守护首拍即
  `{"status":"exited","reason":"session not in registry"}` 且条目又查无＝
  在册坑 `examcard-wrong-dir-and-pid0-claim-reaped` 与 `save()=merge-upsert 永不删（删除只能走 unregister/**list_active 收割**）`两档互证。
  **正解实测＝守护进程用自己的活 PID 自注册后再进循环**（单进程内 `register(pid=os.getpid())`→`run_daemon`），
  三态核实通过：注册表 present=True 且 **pid=29748（活 PID 非 0）**／heartbeat 末三行 `status=alive` 30s 一拍／keepalive grant 在册（ttl 3600）。
  该形态下 `ENQUEUE-RENEW: claim 续租 **4/4** 件`（pid=0 那次是 **0/4**）＝pid 形态真被下游消费的旁证。
- 袋②`q-…-0002` 于 20:04 实测仍 **pending**（head 他袋 `q-20261015-st-qoder-p07-1015-06-0002` 在压），
  `git log -- 本席目录`＝**0**、`git show HEAD:…ledger.md`＝**0 行**⇒**未落地**；`landed_commits=0` 是唯一判据，入队回显不作数。
- 袋③＝本补记（严格超集：同四件仅 ledger 追加本节＋游标追加本段，纯 plus/minus=0），本班末投。
- 另记一处非本席事件：`git add` 当轮报 `fatal: Unable to create '.git/index.lock': File exists`＝并发他席 git 进程；
  按在册"主区 index.lock 不挡入袋只挡直连落地"复量 `staged=4` 后照投，未代拆锁未清他人锁。

### 四、给下一班 C 的改判（游标同步改，勿再按上文⑤⑧节的"退回⑥"领面）

- **本席真实可考面不是 2**：照 A 席 06 班口径，entry_flow 里 `panel＋个股次日` 那一层 24 张中 21 张归 C 只是**绑定层**拒，
  不是不能考；下一班第一动作＝**自带分数册备份**（A 席在册教训"分数册从未落 HEAD"）→
  按卡面 `universe_rule`／`signal_derivation` 逐字自物化面 → `run_card` 注入 → only-add 追加行。
- 两枚 sector 卡（L2-01-2/02・L2-01-3/02，10-10 08:20，积压 5 日）**改判为"可考、须注入"**，
  禁走 `--mode run` 自动绑（本班实测凭据在⑤节）；分母口径先跑 A 席三件实测（重复行数／有效码数≥30／目标面是否 1 日）。
- 上文⑧节给 ⑤ 的"117 张目标面口缺口"工单**降级为线索非结论**；给 ⑥ 的"补 composite_join_rules"仍有效但对这 2 张**不是前置条件**。
- 会话保活配方照③节实测形态抄：**守护自注册活 PID＋单进程进环**，勿再 `pid=0` 裸注册后指望条目活着。

### 五、补记之补记（20:09）：③节那条"活 PID 守护"处方**只成立约 9 分钟**，勿当已验证配方继承

实测追证（`tasklist //FI "PID eq 29748"`＝无匹配；heartbeat 末条 `{"ts":"...12:05:06...","pid":29748,"status":"alive"}` 后即断，
下一条是 pid 58484 的 `exited / reason="session not in registry"`；20:08:56 复量 `get_session` present=**False**）：

- 三态曾在 19:57 全绿（在册 True＋活 PID＋heartbeat alive），**但守护进程本身于≈20:05 静默消失**（无 traceback、nohup 壳不留痕），
  条目随之被外来 `list_active` 收割 ⇒ 第三袋预检再次 **SESSION-REQUIRED**（20:07／20:08 两次同因，均"1 项违规一次给全"、锁外白烧已避免）。
- ⇒ ③节末句应读作"**必要条件**而非充分条件"：主区无车道形态下，会话活性靠一个本机长驻进程撑着，而本机长批进程会静默消失
  （同在册 `long-batch-collector-must-flush-per-block`）。**充分解不在本席职权**＝要么走 `session_worktree_start` 车道（daemon 由 worktree 锚定），
  要么由 ⑩/统筹改存活闸判据（⑨席 14 班原文同结论："恒定班要保袋须跨班 keeper 或 ⑩/统筹改存活闸判据，非本席职权"）。
- 本班据此**不再无限重试**：最后一次尝试＝同一命令串内"注册→立即 enqueue"（不给收割留窗口）；投得进与否都就此收班，
  四件字节在盘＋暂存面双存证（`git diff --cached` 4 件），不丢。下一班续投前先读 dead_reason 再定（不盲重推死袋）。
- 纪律复核：本席**未**取 CLI 手动 requeue 人工强制杠杆、**未**代拆他人 index.lock、**未**自清他会话 claim、
  未动判据/门柱/冻结值、未翻任何卡状态、未写分数册一行；袋在飞故本班 claim **未释放**（在册"袋在飞禁放锁"）。
